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

import json
from datetime import datetime, timezone
from pathlib import Path
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
LOCAL_BASE_RESUME_ARTIFACT_MAP_PATH = Path("output/local/base_resume_artifacts.json")
DEFAULT_BASE_RESUME_ARTIFACT_PATH = Path("templates/Resume 2026.docx")


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


class BaseResumeSelectionSummary(BaseModel):
    """Selection history row for the top-level Base Resume Library screen."""

    id: int
    canonical_job_id: str
    company: str | None
    title: str | None
    category_id: str
    document_ref: str | None
    selection_mode: str
    confidence: float | None
    reason: str | None
    selected_by_user: bool
    selected_at: str


class BaseResumeArtifact(BaseModel):
    """Runtime pointer to a usable local base-resume artifact.

    This is deliberately separate from the committed category registry:
    category metadata remains safe to commit, while the resolved local path
    can point at James's private workstation artifact or the tracked default
    resume template.
    """

    category_id: str
    document_ref: str | None
    artifact_status: str
    local_path: str | None
    note: str


class BaseResumeUseResult(BaseModel):
    canonical_job_id: str
    material_generation_status: str
    pathway_updated_at: str
    artifact: BaseResumeArtifact


class BaseResumeArtifactRegistration(BaseModel):
    category_id: str
    local_path: str


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


def _row_to_summary(row: Row) -> BaseResumeSelectionSummary:
    return BaseResumeSelectionSummary(
        id=row["id"],
        canonical_job_id=row["canonical_job_id"],
        company=row["company"],
        title=row["title"],
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

    def resolve_category_artifact(self, category_id: str) -> BaseResumeArtifact:
        category = get_category(category_id)
        if category is None:
            return BaseResumeArtifact(
                category_id=category_id,
                document_ref=None,
                artifact_status="unavailable",
                local_path=None,
                note="Unknown base resume category.",
            )

        configured_path = self._configured_artifact_path(category_id)
        if configured_path is not None:
            path = configured_path
            source_note = "Local-only artifact registered in output/local/base_resume_artifacts.json."
            available_status = "local-only"
        else:
            path = DEFAULT_BASE_RESUME_ARTIFACT_PATH
            source_note = (
                "Using tracked default resume template; register a category-specific local file "
                "from Base Resume Library when ready."
            )
            available_status = "configured"

        resolved = path if path.is_absolute() else Path.cwd() / path
        if resolved.is_file():
            return BaseResumeArtifact(
                category_id=category.category_id,
                document_ref=category.document_ref,
                artifact_status=available_status,
                local_path=str(resolved.resolve()),
                note=source_note,
            )
        return BaseResumeArtifact(
            category_id=category.category_id,
            document_ref=category.document_ref,
            artifact_status="missing",
            local_path=None,
            note=(
                "Base resume file not configured. Register a local .docx/.pdf path for this "
                f"category in Base Resume Library; expected file was not found at {resolved}."
            ),
        )

    def register_category_artifact(
        self,
        category_id: str,
        local_path: str,
    ) -> BaseResumeArtifact:
        category = get_category(category_id)
        if category is None or is_deferred_category(category_id):
            raise BaseResumeSelectionError(f"Unknown base resume category: {category_id!r}")
        cleaned = (local_path or "").strip().strip('"')
        if not cleaned:
            raise BaseResumeSelectionError("Base resume local path is required.")
        path = Path(cleaned).expanduser()
        resolved = path if path.is_absolute() else Path.cwd() / path
        if not resolved.is_file():
            raise BaseResumeSelectionError(
                "Base resume file not configured. Register an existing local .docx or .pdf file."
            )
        if resolved.suffix.lower() not in {".docx", ".pdf"}:
            raise BaseResumeSelectionError("Base resume artifact must be a .docx or .pdf file.")

        payload = self._read_artifact_map()
        payload[category.category_id] = {"path": str(resolved.resolve())}
        LOCAL_BASE_RESUME_ARTIFACT_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_BASE_RESUME_ARTIFACT_MAP_PATH.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return self.resolve_category_artifact(category.category_id)

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

    def get_latest_artifact(self, canonical_job_id: str) -> BaseResumeArtifact | None:
        selection = self.get_latest_selection(canonical_job_id)
        if selection is None:
            return None
        return self.resolve_category_artifact(selection.category_id)

    def use_selected_base_resume(self, canonical_job_id: str) -> BaseResumeUseResult:
        selection = self.get_latest_selection(canonical_job_id)
        if selection is None:
            raise BaseResumeSelectionError(
                "Select a base resume category before using a base resume without tailoring."
            )
        artifact = self.resolve_category_artifact(selection.category_id)
        if artifact.artifact_status not in {"configured", "generated", "local-only"} or not artifact.local_path:
            raise BaseResumeSelectionError(artifact.note)

        now = _now_iso()
        with get_db() as db:
            self._require_job(db, canonical_job_id)
            db.execute(
                """
                UPDATE jobs
                SET material_generation_status = 'using_base_resume',
                    pathway_updated_at = ?
                WHERE canonical_job_id = ?
                """,
                (now, canonical_job_id),
            )
        return BaseResumeUseResult(
            canonical_job_id=canonical_job_id,
            material_generation_status="using_base_resume",
            pathway_updated_at=now,
            artifact=artifact,
        )

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

    def list_recent_selections(self, limit: int = 20) -> list[BaseResumeSelectionSummary]:
        with get_db() as db:
            rows = db.execute(
                """
                SELECT
                    brs.id, brs.canonical_job_id, brs.category, brs.document_ref,
                    brs.selection_mode, brs.confidence, brs.reason,
                    brs.selected_by_user, brs.selected_at,
                    j.company, j.title
                FROM base_resume_selections brs
                LEFT JOIN jobs j ON j.canonical_job_id = brs.canonical_job_id
                ORDER BY datetime(brs.selected_at) DESC, brs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [_row_to_summary(row) for row in rows]

    @staticmethod
    def _require_job(db: Connection, canonical_job_id: str) -> None:
        exists = db.execute(
            "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        if not exists:
            raise BaseResumeSelectionError(f"Unknown job: {canonical_job_id}")

    @staticmethod
    def _configured_artifact_path(category_id: str) -> Path | None:
        raw = BaseResumeSelectionService._read_artifact_map()
        entry = raw.get(category_id) or raw.get("default") or raw.get("*")
        if isinstance(entry, dict):
            entry = entry.get("path") or entry.get("local_path")
        if not isinstance(entry, str) or not entry.strip():
            return None
        return Path(entry).expanduser()

    @staticmethod
    def _read_artifact_map() -> dict:
        path = LOCAL_BASE_RESUME_ARTIFACT_MAP_PATH
        if not path.is_file():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}
        return raw if isinstance(raw, dict) else {}
