"""Application pathway mutation service (Build 1 Package 1).

Owns the only write paths for the navigation-only pathway metadata added to
`jobs` in this package: `workspace_url`/`workspace_provider`/`workspace_label`,
`application_status`, and `pathway_updated_at`. Kept separate from
`job_search.services.atlas.AtlasDataService` (read-only, enforced by
`tests/test_desktop_data_api.py::test_atlas_service_has_no_write_sql`) and
separate from document generation — nothing in this module ever calls the
generator, the LLM, or Drive, and nothing here advances `app_state` through
the state machine.

Hard boundaries enforced here, not just documented:
- `set_workspace_link` only ever writes `workspace_url`/`workspace_provider`/
  `workspace_label`/`pathway_updated_at`. It never creates a real Drive
  folder and never triggers generation.
- `mark_applied` only ever writes `application_status`/`pathway_updated_at`.
  It is an honest user-logged record of an external submission that already
  happened — it does not call `job_search.tracking.advance_state` and does
  not require the job to be in any particular `app_state`. Automatic/
  one-click submission is out of scope and not implemented here.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import BaseModel

from job_search.db import get_db

VALID_APPLICATION_STATUSES = {"not_applied", "applied"}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class ApplicationPathwayError(Exception):
    """Raised for an unknown job id or an invalid pathway mutation request."""


class ApplicationPathwayState(BaseModel):
    """The current pathway metadata for one job, after a mutation."""

    canonical_job_id: str
    workspace_url: str | None
    workspace_provider: str | None
    workspace_label: str | None
    application_status: str
    application_deadline: str | None
    pathway_updated_at: str | None


class ApplicationPathwayService:
    """Write boundary for application-pathway metadata. No generation calls."""

    def set_workspace_link(
        self,
        canonical_job_id: str,
        workspace_url: str,
        workspace_provider: str | None = None,
        workspace_label: str | None = None,
    ) -> ApplicationPathwayState:
        """Record a user-provided workspace/folder reference.

        Navigation-only metadata: this does not create a Drive folder, does
        not upload anything, and does not change `material_generation_status`
        or `app_state`. A blank/pre-created workspace may exist before any
        documents do — recording its link here is exactly that case.
        """
        cleaned_url = workspace_url.strip() if workspace_url else ""
        if not cleaned_url:
            raise ApplicationPathwayError("workspace_url is required and cannot be blank.")

        with get_db() as db:
            self._require_job(db, canonical_job_id)
            now = _now_iso()
            db.execute(
                """
                UPDATE jobs
                SET workspace_url = ?, workspace_provider = ?, workspace_label = ?,
                    pathway_updated_at = ?
                WHERE canonical_job_id = ?
                """,
                (cleaned_url, workspace_provider, workspace_label, now, canonical_job_id),
            )
            return self._read_state(db, canonical_job_id)

    def mark_applied(self, canonical_job_id: str) -> ApplicationPathwayState:
        """Let the user log that they already submitted an application externally.

        This is a user-logged record, not a submission action — ATLAS never
        submits anything itself (one-click apply / automatic submission is
        explicitly out of Build 1 scope). Setting this status does not touch
        `app_state` or the state machine; tracker/pipeline state transitions
        remain a separate, existing concern.
        """
        with get_db() as db:
            self._require_job(db, canonical_job_id)
            now = _now_iso()
            db.execute(
                """
                UPDATE jobs
                SET application_status = 'applied', pathway_updated_at = ?
                WHERE canonical_job_id = ?
                """,
                (now, canonical_job_id),
            )
            return self._read_state(db, canonical_job_id)

    def set_application_deadline(
        self,
        canonical_job_id: str,
        application_deadline: str | None,
    ) -> ApplicationPathwayState:
        cleaned = (application_deadline or "").strip()
        if cleaned:
            try:
                date.fromisoformat(cleaned)
            except ValueError as exc:
                raise ApplicationPathwayError(
                    "application_deadline must use YYYY-MM-DD format."
                ) from exc
        else:
            cleaned = None

        with get_db() as db:
            self._require_job(db, canonical_job_id)
            now = _now_iso()
            db.execute(
                """
                UPDATE jobs
                SET application_deadline = ?, pathway_updated_at = ?
                WHERE canonical_job_id = ?
                """,
                (cleaned, now, canonical_job_id),
            )
            return self._read_state(db, canonical_job_id)

    @staticmethod
    def _require_job(db, canonical_job_id: str) -> None:
        exists = db.execute(
            "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
            (canonical_job_id,),
        ).fetchone()
        if not exists:
            raise ApplicationPathwayError(f"Unknown job: {canonical_job_id}")

    @staticmethod
    def _read_state(db, canonical_job_id: str) -> ApplicationPathwayState:
        row = db.execute(
            """
            SELECT canonical_job_id, workspace_url, workspace_provider, workspace_label,
                   application_status, application_deadline, pathway_updated_at
            FROM jobs
            WHERE canonical_job_id = ?
            """,
            (canonical_job_id,),
        ).fetchone()
        return ApplicationPathwayState(
            canonical_job_id=row["canonical_job_id"],
            workspace_url=row["workspace_url"],
            workspace_provider=row["workspace_provider"],
            workspace_label=row["workspace_label"],
            application_status=row["application_status"] or "not_applied",
            application_deadline=row["application_deadline"],
            pathway_updated_at=row["pathway_updated_at"],
        )
