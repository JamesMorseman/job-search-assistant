"""Application tracker service — state history, follow-up visibility, and
(as of Phase 4 Package 3b) state-mutating tracker actions.

Read paths reuse the existing state machine (`job_search.tracking.advance_state`)
and `app_transitions`/`followup_queue` tables without re-deriving query logic.
This service does not call `FollowUpEngine.run()` for read purposes because
that method performs a write (auto-flagging stale "applied" jobs as
"ghosted") as a side effect of what is otherwise a read — using it from a
read path would mutate state outside of an explicit action. Instead,
`list_due_followups()` runs the same due-item query directly, without the
auto-flag step. See Governance Findings in the Phase 4 Package 1 report for
why this divergence from "reuse existing logic" is necessary.

Package 3b adds the first approved state-mutating service functions:
`transition_job()` and `resolve_followup()`. Both are thin wrappers — all
state-machine rules, validation, and history persistence remain owned by
`job_search.tracking.advance_state()` and `FollowUpEngine.mark_resolved()`
respectively. No new workflow rules are introduced here.
"""

from __future__ import annotations

from datetime import date, timedelta
from sqlite3 import Row

from pydantic import BaseModel

from job_search.db import get_db
from job_search.tracking import FollowUpEngine, advance_state


class TrackerRow(BaseModel):
    """A job's current application-tracking state for dashboard display."""

    canonical_job_id: str
    company: str
    title: str
    source: str
    app_state: str
    match_score: float | None
    last_transitioned_at: str | None
    last_transition_note: str | None


class StateTransition(BaseModel):
    from_state: str | None
    to_state: str
    transitioned_at: str
    note: str | None


class FollowUpItem(BaseModel):
    id: int
    canonical_job_id: str
    company: str
    title: str
    app_state: str
    apply_url: str | None
    action_type: str
    due_date: str
    resolved: bool
    note: str | None


def _row_to_tracker_row(row: Row) -> TrackerRow:
    return TrackerRow(
        canonical_job_id=row["canonical_job_id"],
        company=row["company"],
        title=row["title"],
        source=row["source"],
        app_state=row["app_state"],
        match_score=row["match_score"],
        last_transitioned_at=row["last_transitioned_at"],
        last_transition_note=row["last_transition_note"],
    )


def _row_to_followup_item(row: Row) -> FollowUpItem:
    return FollowUpItem(
        id=row["id"],
        canonical_job_id=row["canonical_job_id"],
        company=row["company"],
        title=row["title"],
        app_state=row["app_state"],
        apply_url=row["apply_url"],
        action_type=row["action_type"],
        due_date=row["due_date"],
        resolved=bool(row["resolved"]),
        note=row["note"],
    )


class TrackerService:
    """Application-tracker queries and actions.

    Read methods (`list_tracker_rows`, `get_state_history`,
    `list_due_followups`) never mutate state. The two action methods below
    (`transition_job`, `resolve_followup`) are the only state-mutating
    surface in this service, and both delegate entirely to existing
    tracking infrastructure rather than implementing new rules.
    """

    TRACKED_STATES = (
        "selected",
        "applied",
        "acknowledged",
        "screen",
        "interview",
        "offer",
        "rejected",
        "ghosted",
    )

    def list_tracker_rows(self, states: tuple[str, ...] | None = None) -> list[TrackerRow]:
        states = states or self.TRACKED_STATES
        placeholders = ",".join("?" * len(states))
        sql = f"""
            SELECT
                j.canonical_job_id, j.company, j.title, j.source, j.app_state,
                j.match_score,
                t.transitioned_at AS last_transitioned_at,
                t.note AS last_transition_note
            FROM jobs j
            LEFT JOIN (
                SELECT canonical_job_id, to_state, transitioned_at, note,
                       ROW_NUMBER() OVER (
                           PARTITION BY canonical_job_id
                           ORDER BY datetime(transitioned_at) DESC, id DESC
                       ) AS rn
                FROM app_transitions
            ) t ON t.canonical_job_id = j.canonical_job_id AND t.rn = 1
            WHERE j.app_state IN ({placeholders})
            ORDER BY datetime(t.transitioned_at) DESC
        """
        with get_db() as db:
            rows = db.execute(sql, states).fetchall()
        return [_row_to_tracker_row(row) for row in rows]

    def get_state_history(self, canonical_job_id: str) -> list[StateTransition]:
        with get_db() as db:
            rows = db.execute(
                """
                SELECT from_state, to_state, transitioned_at, note
                FROM app_transitions
                WHERE canonical_job_id = ?
                ORDER BY datetime(transitioned_at) ASC, id ASC
                """,
                (canonical_job_id,),
            ).fetchall()
        return [
            StateTransition(
                from_state=row["from_state"],
                to_state=row["to_state"],
                transitioned_at=row["transitioned_at"],
                note=row["note"],
            )
            for row in rows
        ]

    def list_due_followups(self, as_of: str | None = None, include_resolved: bool = False) -> list[FollowUpItem]:
        """Follow-up queue items, read-only. Mirrors FollowUpEngine.run()'s
        SELECT but intentionally skips its auto-ghost mutation step."""
        as_of = as_of or date.today().isoformat()
        where = ["fq.due_date <= ?"]
        params: list[object] = [as_of]
        if not include_resolved:
            where.append("fq.resolved = 0")

        sql = f"""
            SELECT fq.id, fq.canonical_job_id, fq.action_type, fq.due_date,
                   fq.resolved, fq.note,
                   j.company, j.title, j.app_state, j.apply_url
            FROM followup_queue fq
            JOIN jobs j ON j.canonical_job_id = fq.canonical_job_id
            WHERE {' AND '.join(where)}
            ORDER BY fq.due_date ASC
        """
        with get_db() as db:
            rows = db.execute(sql, params).fetchall()
        return [_row_to_followup_item(row) for row in rows]

    def list_upcoming_followups(self, as_of: str | None = None, days: int = 7) -> list[FollowUpItem]:
        """Unresolved follow-ups due after `as_of` and within `days`.

        This is intentionally separate from `list_due_followups()` so the
        dashboard can show a planning horizon without changing due-item
        behavior or invoking FollowUpEngine's auto-ghost write path.
        """
        as_of = as_of or date.today().isoformat()
        horizon = (date.fromisoformat(as_of) + timedelta(days=days)).isoformat()

        sql = """
            SELECT fq.id, fq.canonical_job_id, fq.action_type, fq.due_date,
                   fq.resolved, fq.note,
                   j.company, j.title, j.app_state, j.apply_url
            FROM followup_queue fq
            JOIN jobs j ON j.canonical_job_id = fq.canonical_job_id
            WHERE fq.due_date > ?
              AND fq.due_date <= ?
              AND fq.resolved = 0
            ORDER BY fq.due_date ASC
        """
        with get_db() as db:
            rows = db.execute(sql, (as_of, horizon)).fetchall()
        return [_row_to_followup_item(row) for row in rows]

    # ── Actions (Package 3b — state-mutating) ────────────────────────────

    def transition_job(
        self,
        canonical_job_id: str,
        to_state: str,
        note: str | None = None,
    ) -> bool:
        """Transition a job's application state.

        Thin wrapper around `job_search.tracking.advance_state()` — does not
        duplicate or relax the state-machine's valid-transition rules.
        `advance_state()` already writes the `app_transitions` row, so
        history and auditability are preserved automatically.

        Returns True on a successful transition, False if the job is
        unknown or the transition is not valid from its current state.
        """
        with get_db() as db:
            return advance_state(db, canonical_job_id, to_state, note=note)

    def resolve_followup(self, followup_id: int) -> None:
        """Mark a follow-up queue item resolved.

        Thin wrapper around `FollowUpEngine.mark_resolved()` — does not
        reimplement follow-up resolution logic.
        """
        FollowUpEngine().mark_resolved(followup_id)
