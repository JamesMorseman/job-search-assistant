"""Build 1 Package 3 — generation intent-gate integration.

Wires the explicit apply-intent gate required before resume/cover-letter
generation (BUILD1-REQ-APPLICATION-PATHWAY hard rule 5: "Resume/cover
generation requires explicit user confirmation after posting review").

This module does NOT reimplement generation, rendering, evidence selection,
or Drive upload — it wraps the existing, already-tested generation boundary
(`job_search.services.documents.DocumentsService.regenerate_documents`,
itself a thin wrapper around `SelectionProcessor.generate_for_selected`).
Its entire job is to:

1. Require an explicit `confirm_generation()` call before that boundary is
   ever invoked — nothing in this module calls generation as a side effect
   of navigation, base-resume selection, or any read path.
2. Track `jobs.material_generation_status` through an observable lifecycle
   (not_started -> base_selected -> confirmation_required -> generating ->
   generated_draft_review_required | failed_error) so the UI can show
   accurate status without guessing.
3. Never advance `app_state` and never mark a job applied — those remain
   entirely separate concerns owned by `job_search.tracking.state_machine`
   and `job_search.services.pathway.ApplicationPathwayService` respectively.

Hard safety invariants enforced here (see tests/test_generation_intent_gate.py):
- `request_confirmation()` only ever sets `material_generation_status`; it
  never calls `DocumentsService.regenerate_documents()`.
- `confirm_generation()` is the only method in this module that calls
  `DocumentsService.regenerate_documents()`, and it always requires the
  caller to have explicitly invoked it — there is no automatic/implicit
  path that reaches generation.
- A failed generation call sets `failed_error` and re-raises; it never
  silently swallows the error and never corrupts `generated_docs` history
  (regeneration is append-only at the `DocumentsService`/`SelectionProcessor`
  layer, unchanged here).
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel

from job_search.db import get_db
from job_search.services.documents import (
    DocumentRegenerationError,
    DocumentsService,
    RegenerationResult,
)

# Status lifecycle. "stale_missing" is set externally by a freshness check
# (e.g. posting/profile changed since the last draft) — not produced by any
# method in this module, which only ever moves status forward through an
# explicit user action.
VALID_MATERIAL_GENERATION_STATUSES = {
    "not_started",
    "base_selected",
    "confirmation_required",
    "generating",
    "generated_draft_review_required",
    "failed_error",
    "stale_missing",
}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class GenerationIntentError(Exception):
    """Raised for an unknown job id or an invalid gate transition. Also
    raised (re-raised, wrapping the original) when the underlying generation
    call fails — the caller always sees a clear, actionable error rather
    than a silently-corrupted state."""


class GenerationIntentState(BaseModel):
    canonical_job_id: str
    material_generation_status: str
    pathway_updated_at: str | None


class GenerationConfirmationResult(BaseModel):
    """Result of a successful, explicitly-confirmed generation call."""

    canonical_job_id: str
    material_generation_status: str
    resume_url: str | None
    cover_url: str | None


class GenerationIntentService:
    """The apply-intent gate. Every method here is explicit and
    user-triggered — none of them are wired to navigation, selection, or any
    read path elsewhere in the app."""

    def __init__(self, documents_service: DocumentsService | None = None):
        self._documents_service = documents_service or DocumentsService()

    def request_confirmation(self, canonical_job_id: str) -> GenerationIntentState:
        """Move the gate to 'confirmation_required'. This is shown to the
        user as "ready to generate, pending your confirmation" — it never
        calls generation itself. Safe to call repeatedly (idempotent)."""
        return self._set_status(canonical_job_id, "confirmation_required")

    def mark_base_selected(self, canonical_job_id: str) -> GenerationIntentState:
        """Optional UI bookkeeping step: record that a base resume has been
        selected for this job, without requesting generation yet. Selection
        itself is recorded by `BaseResumeSelectionService`; this only updates
        the generation-status lifecycle field on `jobs` so the UI has a
        single status to read. Never calls generation."""
        with get_db() as db:
            self._require_job(db, canonical_job_id)
            current = self._read_status(db, canonical_job_id)
            if current in {"confirmation_required", "generating", "generated_draft_review_required"}:
                # Don't regress a more-advanced status back to base_selected.
                return self._read_state(db, canonical_job_id)
            return self._write_status(db, canonical_job_id, "base_selected")

    def confirm_generation(
        self,
        canonical_job_id: str,
        generate_resume: bool = True,
        generate_cover_letter: bool = True,
    ) -> GenerationConfirmationResult:
        """The one path in this module that calls real generation.

        Requires an explicit call from the user-facing route — there is no
        automatic trigger anywhere else in this codebase that reaches this
        method. `generate_resume`/`generate_cover_letter` are accepted for
        forward compatibility with a more granular UI, but the underlying
        `SelectionProcessor.generate_for_selected()` boundary always
        produces both in one call today; this method does not change that
        boundary's behavior, only gates entry to it.
        """
        if not generate_resume and not generate_cover_letter:
            raise GenerationIntentError("At least one of resume or cover letter must be requested.")

        with get_db() as db:
            self._require_job(db, canonical_job_id)
            self._write_status(db, canonical_job_id, "generating")

        try:
            result: RegenerationResult = self._documents_service.regenerate_documents(canonical_job_id)
        except DocumentRegenerationError as exc:
            with get_db() as db:
                self._write_status(db, canonical_job_id, "failed_error")
            raise GenerationIntentError(str(exc)) from exc

        with get_db() as db:
            state = self._write_status(db, canonical_job_id, "generated_draft_review_required")

        return GenerationConfirmationResult(
            canonical_job_id=canonical_job_id,
            material_generation_status=state.material_generation_status,
            resume_url=result.resume_url,
            cover_url=result.cover_url,
        )

    def get_status(self, canonical_job_id: str) -> GenerationIntentState:
        with get_db() as db:
            self._require_job(db, canonical_job_id)
            return self._read_state(db, canonical_job_id)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _set_status(self, canonical_job_id: str, status: str) -> GenerationIntentState:
        with get_db() as db:
            self._require_job(db, canonical_job_id)
            return self._write_status(db, canonical_job_id, status)

    @staticmethod
    def _require_job(db, canonical_job_id: str) -> None:
        exists = db.execute(
            "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        if not exists:
            raise GenerationIntentError(f"Unknown job: {canonical_job_id}")

    @staticmethod
    def _read_status(db, canonical_job_id: str) -> str:
        row = db.execute(
            "SELECT material_generation_status FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        return (row["material_generation_status"] if row else None) or "not_started"

    @classmethod
    def _write_status(cls, db, canonical_job_id: str, status: str) -> GenerationIntentState:
        if status not in VALID_MATERIAL_GENERATION_STATUSES:
            raise GenerationIntentError(f"Invalid material_generation_status: {status!r}")
        now = _now_iso()
        db.execute(
            """
            UPDATE jobs
            SET material_generation_status = ?, pathway_updated_at = ?
            WHERE canonical_job_id = ?
            """,
            (status, now, canonical_job_id),
        )
        return cls._read_state(db, canonical_job_id)

    @staticmethod
    def _read_state(db, canonical_job_id: str) -> GenerationIntentState:
        row = db.execute(
            "SELECT canonical_job_id, material_generation_status, pathway_updated_at FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        return GenerationIntentState(
            canonical_job_id=row["canonical_job_id"],
            material_generation_status=row["material_generation_status"] or "not_started",
            pathway_updated_at=row["pathway_updated_at"],
        )
