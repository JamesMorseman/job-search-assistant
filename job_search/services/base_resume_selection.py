"""Build 1 Package 2 — base resume selection/recommendation service.

Owns the only write path for `base_resume_selections` rows. Selection here
is advisory and user-overridable (BUILD1-REQ-BASE-RESUME-LIBRARY); recording
a selection here NEVER calls document generation, NEVER advances
`app_state`, and NEVER mutates the profile. The deterministic recommender
reuses the existing role-family classifier
(`job_search.evidence.discipline.classify_job`) rather than introducing a
new classification path or calling an LLM — Build 1 prefers a deterministic
recommendation over an LLM call for this purpose.

Manual selection (`selected_by_user=True`, `selection_mode="manual"`) is
required when a posting is unreachable (no job description text to
classify); `recommend()` returns the `general_strongest_overall` fallback
with low confidence in that case rather than failing, but the caller (API
route / UI) is responsible for treating that path as "selection required",
not as an automatic choice.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlite3 import Connection, Row

from pydantic import BaseModel

from job_search.db import get_db
from job_search.evidence.base_resume_library import (
    APPROVED_BASE_RESUME_CATEGORIES,
    BaseResumeCategory,
    category_for_role_family,
    get_category,
    is_deferred_category,
)
from job_search.evidence.discipline import classify_job
from job_search.models import CanonicalJob

VALID_SELECTION_MODES = {"recommended", "manual"}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class BaseResumeSelectionError(Exception):
    """Raised for an unknown job id, unknown/deferred category, or invalid
    selection request. Never raised as a side effect of generation — this
    service never calls generation."""


class BaseResumeRecommendation(BaseModel):
    """A read-only, advisory recommendation. Recording it as a selection is
    a separate, explicit step (`record_selection`)."""

    category_id: str
    label: str
    confidence: float
    reason: str
    posting_reachable: bool


class BaseResumeSelectionRecord(BaseModel):
    """A persisted selection/recommendation row."""

    id: int
    canonical_job_id: str
    category_id: str
    document_ref: str | None
    selection_mode: str
    confidence: float | None
    reason: str | None
    selected_by_user: bool
    selected_at: str


def _row_to_record(row: Row) -> BaseResumeSelectionRecord:
    return BaseResumeSelectionRecord(
        id=row["id"],
        canonical_job_id=row["canonical_job_id"],
        category_id=row["category"],
        document_ref=row["document_ref"],
        selection_mode=row["selection_mode"],
        confidence=row["confidence"],
        reason=row["reason"],
        selected_by_user=bool(row["selected_by_user"]),
        selected_at=row["selected_at"],
    )


class BaseResumeSelectionService:
    """Recommendation (read-only/advisory) + selection recording (the one
    write path) for base resume categories. No generation calls anywhere in
    this class."""

    def list_categories(self) -> tuple[BaseResumeCategory, ...]:
        return APPROVED_BASE_RESUME_CATEGORIES

    def recommend(
        self,
        job: CanonicalJob | None,
        jd: str | None,
        posting_reachable: bool,
    ) -> BaseResumeRecommendation:
        """Advisory-only recommendation. Never persists anything, never
        calls generation. Manual selection is required when
        `posting_reachable` is False — this method still returns a
        best-effort fallback recommendation in that case so the UI has
        something to show, but the caller must require an explicit user
        choice (manual override) rather than auto-applying it.
        """
        if not posting_reachable or job is None or not jd:
            fallback = get_category("general_strongest_overall")
            assert fallback is not None
            return BaseResumeRecommendation(
                category_id=fallback.category_id,
                label=fallback.label,
                confidence=0.0,
                reason="Posting is unreachable or has no description text; manual selection is required.",
                posting_reachable=False,
            )

        classification = classify_job(job, jd)
        category = category_for_role_family(classification.role_family)
        if classification.role_family == "general_civil":
            reason = (
                "Role-family classification confidence was low for this posting; "
                "recommending the broad-purpose general category."
            )
        else:
            reason = (
                f"Posting classified as '{classification.role_family}' "
                f"(confidence {classification.confidence:.2f}); recommending the matching category."
            )
        return BaseResumeRecommendation(
            category_id=category.category_id,
            label=category.label,
            confidence=classification.confidence,
            reason=reason,
            posting_reachable=True,
        )

    def record_selection(
        self,
        canonical_job_id: str,
        category_id: str,
        selection_mode: str,
        selected_by_user: bool,
        confidence: float | None = None,
        reason: str | None = None,
    ) -> BaseResumeSelectionRecord:
        """Record a selection. Append-only — never updates or deletes a
        prior selection row, mirroring the `generated_docs` history pattern.
        Recording a selection is the entire effect of this method: it never
        triggers generation and never changes `app_state` or
        `material_generation_status`.
        """
        if selection_mode not in VALID_SELECTION_MODES:
            raise BaseResumeSelectionError(f"Invalid selection_mode: {selection_mode!r}")
        if is_deferred_category(category_id):
            raise BaseResumeSelectionError(
                f"Category {category_id!r} is deferred and not available in Build 1."
            )
        category = get_category(category_id)
        if category is None:
            raise BaseResumeSelectionError(f"Unknown base resume category: {category_id!r}")

        with get_db() as db:
            self._require_job(db, canonical_job_id)
            cursor = db.execute(
                """
                INSERT INTO base_resume_selections
                    (canonical_job_id, category, document_ref, selection_mode,
                     confidence, reason, selected_by_user, selected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    canonical_job_id,
                    category.category_id,
                    category.document_ref,
                    selection_mode,
                    confidence,
                    reason,
                    1 if selected_by_user else 0,
                    _now_iso(),
                ),
            )
            row = db.execute(
                "SELECT * FROM base_resume_selections WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return _row_to_record(row)

    def get_latest_selection(self, canonical_job_id: str) -> BaseResumeSelectionRecord | None:
        with get_db() as db:
            row = db.execute(
                """
                SELECT * FROM base_resume_selections
                WHERE canonical_job_id = ?
                ORDER BY datetime(selected_at) DESC, id DESC
                LIMIT 1
                """,
                (canonical_job_id,),
            ).fetchone()
        return _row_to_record(row) if row is not None else None

    def list_selection_history(self, canonical_job_id: str) -> list[BaseResumeSelectionRecord]:
        with get_db() as db:
            rows = db.execute(
                """
                SELECT * FROM base_resume_selections
                WHERE canonical_job_id = ?
                ORDER BY datetime(selected_at) DESC, id DESC
                """,
                (canonical_job_id,),
            ).fetchall()
        return [_row_to_record(row) for row in rows]

    @staticmethod
    def _require_job(db: Connection, canonical_job_id: str) -> None:
        exists = db.execute(
            "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        if not exists:
            raise BaseResumeSelectionError(f"Unknown job: {canonical_job_id}")
