"""Funnel statistics — tells James which sources convert and which don't.

This is the loop that improves targeting (per spec §15). Tracks the candidate
journey through state transitions and surfaces conversion rates by source,
discipline, location, and stretch_category.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from sqlite3 import Connection

from job_search.db import get_db

# Funnel stages in order. Each is a milestone in the application journey.
FUNNEL_STAGES = ["discovered", "presented", "selected", "applied", "screen", "interview", "offer"]
TERMINAL_STATES = ("rejected", "ghosted", "offer")

_APPLIED_AND_BEYOND = frozenset({
    "applied", "acknowledged", "screen", "interview", "offer", "rejected", "ghosted"
})
_SCREEN_AND_BEYOND = frozenset({"screen", "interview", "offer"})
_RESPONDED = frozenset({"acknowledged", "screen", "interview", "offer"})
_INTERVIEWED_OR_OFFER = frozenset({"interview", "offer"})


def _percentile(sorted_scores: list[float], p: float) -> float | None:
    n = len(sorted_scores)
    if n == 0:
        return None
    idx = p * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return round(sorted_scores[lo], 3)
    return round(sorted_scores[lo] + (idx - lo) * (sorted_scores[hi] - sorted_scores[lo]), 3)


@dataclass
class FunnelStats:
    total_jobs: int = 0
    by_state: dict[str, int] = field(default_factory=dict)
    by_source: dict[str, dict[str, int]] = field(default_factory=dict)
    by_discipline_state: dict[str, dict[str, int]] = field(default_factory=dict)
    by_location_metro: dict[str, dict[str, int]] = field(default_factory=dict)
    by_stretch: dict[str, dict[str, int]] = field(default_factory=dict)
    avg_match_by_state: dict[str, float] = field(default_factory=dict)
    response_rate_by_source: dict[str, dict] = field(default_factory=dict)
    median_days: dict[str, float | None] = field(default_factory=dict)
    funnel_conversion_rates: dict[str, float | None] = field(default_factory=dict)
    llm_grade_distribution: dict[str, dict] = field(default_factory=dict)
    stretch_conversion_rates: dict[str, dict] = field(default_factory=dict)
    # Package 2
    score_distribution_by_state: dict[str, dict] = field(default_factory=dict)
    stretch_response_rates: dict[str, dict] = field(default_factory=dict)
    unified_source_data: dict[str, dict] = field(default_factory=dict)
    pipeline_velocity: dict[str, dict] = field(default_factory=dict)
    llm_grade_outcome_correlation: dict[str, dict] = field(default_factory=dict)


class FunnelReporter:
    def compute(self) -> FunnelStats:
        stats = FunnelStats()
        with get_db() as db:
            stats.total_jobs = self._total(db)
            stats.by_state = self._by_state(db)
            stats.by_source = self._by_source(db)
            stats.by_stretch = self._by_stretch(db)
            stats.avg_match_by_state = self._avg_match_by_state(db)
            stats.response_rate_by_source = self._response_rate_by_source(db)
            stats.median_days = self._median_days_between_states(db)
            stats.llm_grade_distribution = self._llm_grade_distribution(db)
            stats.score_distribution_by_state = self._score_distribution_by_state(db)
            stats.unified_source_data = self._unified_source_data(db)
            stats.pipeline_velocity = self._pipeline_velocity(db)
            stats.llm_grade_outcome_correlation = self._llm_grade_outcome_correlation(db)
        stats.funnel_conversion_rates = self._funnel_conversion_rates(stats.by_state)
        stats.stretch_conversion_rates = self._stretch_conversion_rates(stats.by_stretch)
        stats.stretch_response_rates = self._stretch_response_rates(stats.by_stretch)
        return stats

    # ── Aggregations ──────────────────────────────────────────────────────────

    def _total(self, db: Connection) -> int:
        row = db.execute("SELECT COUNT(*) as n FROM jobs").fetchone()
        return row["n"] if row else 0

    def _by_state(self, db: Connection) -> dict[str, int]:
        rows = db.execute(
            "SELECT app_state, COUNT(*) as n FROM jobs GROUP BY app_state"
        ).fetchall()
        return {r["app_state"]: r["n"] for r in rows}

    def _by_source(self, db: Connection) -> dict[str, dict[str, int]]:
        rows = db.execute("""
            SELECT source, app_state, COUNT(*) as n
            FROM jobs
            GROUP BY source, app_state
            ORDER BY source
        """).fetchall()
        out: dict[str, dict[str, int]] = {}
        for r in rows:
            out.setdefault(r["source"], {})[r["app_state"]] = r["n"]
        return out

    def _by_stretch(self, db: Connection) -> dict[str, dict[str, int]]:
        rows = db.execute("""
            SELECT stretch_category, app_state, COUNT(*) as n
            FROM jobs
            WHERE stretch_category IS NOT NULL
            GROUP BY stretch_category, app_state
        """).fetchall()
        out: dict[str, dict[str, int]] = {}
        for r in rows:
            out.setdefault(r["stretch_category"] or "unknown", {})[r["app_state"]] = r["n"]
        return out

    def _avg_match_by_state(self, db: Connection) -> dict[str, float]:
        rows = db.execute("""
            SELECT app_state, AVG(match_score) as avg_score
            FROM jobs
            WHERE match_score IS NOT NULL
            GROUP BY app_state
        """).fetchall()
        return {r["app_state"]: round(r["avg_score"] or 0, 3) for r in rows}

    def _response_rate_by_source(self, db: Connection) -> dict[str, dict]:
        """For each source: applied count, response count (any progress past applied), response rate."""
        rows = db.execute("""
            SELECT
                source,
                SUM(CASE WHEN app_state IN ('applied','acknowledged','screen','interview','offer','rejected','ghosted') THEN 1 ELSE 0 END) as applied_total,
                SUM(CASE WHEN app_state IN ('acknowledged','screen','interview','offer') THEN 1 ELSE 0 END) as responded,
                SUM(CASE WHEN app_state IN ('screen','interview','offer') THEN 1 ELSE 0 END) as screened,
                SUM(CASE WHEN app_state IN ('interview','offer') THEN 1 ELSE 0 END) as interviewed
            FROM jobs
            GROUP BY source
        """).fetchall()
        out: dict[str, dict] = {}
        for r in rows:
            applied = r["applied_total"] or 0
            if applied == 0:
                continue
            out[r["source"]] = {
                "applied": applied,
                "responded": r["responded"] or 0,
                "response_rate": round((r["responded"] or 0) / applied, 3),
                "screened": r["screened"] or 0,
                "screen_rate": round((r["screened"] or 0) / applied, 3),
                "interviewed": r["interviewed"] or 0,
                "interview_rate": round((r["interviewed"] or 0) / applied, 3),
            }
        return out

    def _median_days_between_states(self, db: Connection) -> dict[str, float | None]:
        """Median days for transitions: applied→acknowledged, applied→screen, applied→rejected/ghosted."""
        return {
            "applied_to_response": self._median_transition_days(
                db, from_state="applied",
                to_states=("acknowledged", "screen", "interview", "offer"),
            ),
            "applied_to_screen": self._median_transition_days(
                db, from_state="applied",
                to_states=("screen",),
            ),
            "applied_to_terminal": self._median_transition_days(
                db, from_state="applied",
                to_states=("rejected", "ghosted"),
            ),
        }

    def _funnel_conversion_rates(self, by_state: dict[str, int]) -> dict[str, float | None]:
        """Conversion rate from each funnel stage to the next. None when prior stage count is 0."""
        if not by_state:
            return {}
        result: dict[str, float | None] = {}
        for i, stage in enumerate(FUNNEL_STAGES):
            if i == 0:
                result[stage] = None
            else:
                prior_count = by_state.get(FUNNEL_STAGES[i - 1], 0)
                if prior_count == 0:
                    result[stage] = None
                else:
                    result[stage] = round(by_state.get(stage, 0) / prior_count, 3)
        return result

    def _llm_grade_distribution(self, db: Connection) -> dict[str, dict]:
        rows = db.execute("""
            SELECT llm_grade, COUNT(*) as n FROM jobs
            WHERE llm_grade IS NOT NULL
            GROUP BY llm_grade
        """).fetchall()
        if not rows:
            return {}
        total = sum(r["n"] for r in rows)
        return {
            r["llm_grade"]: {"count": r["n"], "pct": round(r["n"] / total, 3)}
            for r in rows
        }

    def _stretch_conversion_rates(self, by_stretch: dict[str, dict[str, int]]) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for category, states in by_stretch.items():
            total = sum(states.values())
            if total == 0:
                continue
            applied_count = sum(states.get(s, 0) for s in _APPLIED_AND_BEYOND)
            screen_count = sum(states.get(s, 0) for s in _SCREEN_AND_BEYOND)
            result[category] = {
                "total": total,
                "applied_rate": round(applied_count / total, 3),
                "screen_rate": round(screen_count / total, 3),
            }
        return result

    def _score_distribution_by_state(self, db: Connection) -> dict[str, dict]:
        rows = db.execute("""
            SELECT app_state, match_score
            FROM jobs
            WHERE match_score IS NOT NULL
            ORDER BY app_state, match_score
        """).fetchall()
        if not rows:
            return {}
        by_state: dict[str, list[float]] = {}
        for r in rows:
            by_state.setdefault(r["app_state"], []).append(r["match_score"])
        return {
            state: {
                "q1": _percentile(scores, 0.25),
                "median": _percentile(scores, 0.50),
                "q3": _percentile(scores, 0.75),
                "n": len(scores),
            }
            for state, scores in by_state.items()
        }

    def _stretch_response_rates(self, by_stretch: dict[str, dict[str, int]]) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for category, states in by_stretch.items():
            applied = sum(states.get(s, 0) for s in _APPLIED_AND_BEYOND)
            if applied == 0:
                continue
            responded = sum(states.get(s, 0) for s in _RESPONDED)
            interviewed = sum(states.get(s, 0) for s in _INTERVIEWED_OR_OFFER)
            result[category] = {
                "applied": applied,
                "response_rate": round(responded / applied, 3),
                "interview_rate": round(interviewed / applied, 3),
            }
        return result

    def _unified_source_data(self, db: Connection) -> dict[str, dict]:
        rows = db.execute("""
            SELECT
                source,
                COUNT(*) as jobs_seen,
                SUM(CASE WHEN app_state != 'discovered' THEN 1 ELSE 0 END) as jobs_presented,
                SUM(CASE WHEN app_state IN (
                    'applied','acknowledged','screen','interview','offer','rejected','ghosted'
                ) THEN 1 ELSE 0 END) as applied_total,
                SUM(CASE WHEN app_state IN (
                    'acknowledged','screen','interview','offer'
                ) THEN 1 ELSE 0 END) as responded,
                SUM(CASE WHEN app_state IN ('interview','offer') THEN 1 ELSE 0 END) as interviewed_total,
                SUM(CASE WHEN app_state = 'offer' THEN 1 ELSE 0 END) as offers_total
            FROM jobs
            GROUP BY source
        """).fetchall()
        result: dict[str, dict] = {}
        for r in rows:
            seen = r["jobs_seen"] or 0
            presented = r["jobs_presented"] or 0
            applied = r["applied_total"] or 0
            responded = r["responded"] or 0
            interviewed = r["interviewed_total"] or 0
            offers = r["offers_total"] or 0
            result[r["source"]] = {
                "jobs_seen": seen,
                "jobs_presented": presented,
                "presentation_rate": round(presented / seen, 3) if seen > 0 else None,
                "applied": applied,
                "responded": responded,
                "response_rate": round(responded / applied, 3) if applied > 0 else None,
                "interviewed": interviewed,
                "interview_rate": round(interviewed / applied, 3) if applied > 0 else None,
                "offers": offers,
            }
        return result

    def _pipeline_velocity(self, db: Connection) -> dict[str, dict]:
        pairs = [
            ("presented_to_selected", "Presented → Selected", "presented", "selected"),
            ("selected_to_applied", "Selected → Applied", "selected", "applied"),
        ]
        result: dict[str, dict] = {}
        for key, label, from_state, to_state in pairs:
            rows = db.execute("""
                SELECT
                  (julianday(t2.transitioned_at) - julianday(t1.transitioned_at)) as days
                FROM app_transitions t1
                JOIN app_transitions t2
                  ON t1.canonical_job_id = t2.canonical_job_id
                 AND t1.to_state = ?
                 AND t2.to_state = ?
                 AND t2.transitioned_at > t1.transitioned_at
            """, (from_state, to_state)).fetchall()
            values = sorted([r["days"] for r in rows if r["days"] is not None])
            n = len(values)
            if n == 0:
                median = None
            else:
                mid = n // 2
                median = round(
                    (values[mid] if n % 2 else (values[mid - 1] + values[mid]) / 2),
                    2,
                )
            result[key] = {"label": label, "median_days": median, "n": n}
        return result

    def _llm_grade_outcome_correlation(self, db: Connection) -> dict[str, dict]:
        rows = db.execute("""
            SELECT
                llm_grade,
                COUNT(*) as total,
                SUM(CASE WHEN app_state IN ('rejected','ghosted','offer') THEN 1 ELSE 0 END) as terminal_count,
                SUM(CASE WHEN app_state IN ('screen','interview','offer') THEN 1 ELSE 0 END) as advanced_count
            FROM jobs
            WHERE llm_grade IS NOT NULL
            GROUP BY llm_grade
        """).fetchall()
        if not rows:
            return {}
        result: dict[str, dict] = {}
        for r in rows:
            total = r["total"] or 0
            terminal = r["terminal_count"] or 0
            advanced = r["advanced_count"] or 0
            result[r["llm_grade"]] = {
                "total": total,
                "terminal": terminal,
                "advanced": advanced,
                "advance_rate": round(advanced / total, 3) if total > 0 else None,
                "qualifies": terminal >= 5,
            }
        return result

    def _median_transition_days(
        self,
        db: Connection,
        from_state: str,
        to_states: tuple[str, ...],
    ) -> float | None:
        placeholders = ",".join("?" * len(to_states))
        rows = db.execute(f"""
            SELECT
              (julianday(t2.transitioned_at) - julianday(t1.transitioned_at)) as days
            FROM app_transitions t1
            JOIN app_transitions t2
              ON t1.canonical_job_id = t2.canonical_job_id
             AND t1.to_state = ?
             AND t2.to_state IN ({placeholders})
             AND t2.transitioned_at > t1.transitioned_at
        """, (from_state, *to_states)).fetchall()
        values = sorted([r["days"] for r in rows if r["days"] is not None])
        if not values:
            return None
        n = len(values)
        mid = n // 2
        return round((values[mid] if n % 2 else (values[mid - 1] + values[mid]) / 2), 2)
