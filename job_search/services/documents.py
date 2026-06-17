"""Document history / current-document read models, and (as of Phase 4
Package 2b) the document regeneration action, for dashboard consumption.

Read paths wrap the existing query helpers in `job_search.reporting.documents`
rather than re-implementing generated-doc lookups. Current/latest document
resolution remains query-derived (ordered by generated_at, id) — this
package does not introduce `generated_docs.is_current`; that remains an
unresolved future decision per roadmap/dashboard_readiness_review.

`DocumentsService.regenerate_documents()` is a thin wrapper around
`SelectionProcessor.generate_for_selected()` — it does not reimplement
generation logic. It targets a single job by `canonical_job_id` via
`generate_for_selected(job_ids=[...])`, which does not filter by
`app_state` when explicit job IDs are given. This means regeneration works
regardless of the job's current state (selected, applied, etc.) and never
performs a state transition itself — so it sidesteps the known `jsa apply`
idempotency gap (`advance_state()` rejecting a 'selected' -> 'selected'
transition) without touching that code path, rather than fixing it
upstream. See Governance Findings in the Phase 4 Package 2b report for why
a broader fix was judged unnecessary for this package.
"""

from __future__ import annotations

import json
from sqlite3 import Row

from pydantic import BaseModel

from job_search.db import get_db
from job_search.reporting.documents import (
    get_latest_generated_doc,
    get_latest_generated_docs,
    list_generated_docs,
)
from job_search.reporting.selection import SelectionProcessor


def _parse_json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return value if isinstance(value, list) else []


class DocumentRecord(BaseModel):
    """A single generated document (resume or cover letter) snapshot."""

    id: int
    canonical_job_id: str
    doc_type: str
    drive_file_id: str | None
    drive_url: str | None
    keyword_coverage: float | None
    keywords_hit: list
    keywords_missed: list
    model_used: str | None
    generated_at: str


def _row_to_record(row: Row) -> DocumentRecord:
    return DocumentRecord(
        id=row["id"],
        canonical_job_id=row["canonical_job_id"],
        doc_type=row["doc_type"],
        drive_file_id=row["drive_file_id"],
        drive_url=row["drive_url"],
        keyword_coverage=row["keyword_coverage"],
        keywords_hit=_parse_json_list(row["keywords_hit"]),
        keywords_missed=_parse_json_list(row["keywords_missed"]),
        model_used=row["model_used"],
        generated_at=row["generated_at"],
    )


class DocumentRegenerationError(Exception):
    """Raised when document regeneration cannot complete for a job.

    Covers both an unknown/invalid `canonical_job_id` and a generation
    failure reported by `SelectionProcessor.generate_for_selected()`. The
    underlying processor logs failure detail; this exception surfaces a
    caller-facing message without re-deriving or duplicating that detail.
    """


class RegenerationResult(BaseModel):
    """Result of a successful document regeneration."""

    canonical_job_id: str
    resume_url: str | None
    cover_url: str | None


class DocumentsService:
    """Generated-document history/current-document queries, plus the
    regenerate action.

    `list_documents`, `get_latest_document`, and `get_current_documents`
    never mutate state. `regenerate_documents` is the only state-mutating
    method in this service (Package 2b) and delegates entirely to
    `SelectionProcessor.generate_for_selected()`.
    """

    def __init__(self, processor: SelectionProcessor | None = None):
        self._processor = processor or SelectionProcessor()

    def list_documents(
        self,
        canonical_job_id: str,
        doc_type: str | None = None,
        limit: int | None = None,
    ) -> list[DocumentRecord]:
        with get_db() as db:
            rows = list_generated_docs(db, canonical_job_id, doc_type=doc_type, limit=limit)
        return [_row_to_record(row) for row in rows]

    def get_latest_document(self, canonical_job_id: str, doc_type: str) -> DocumentRecord | None:
        with get_db() as db:
            row = get_latest_generated_doc(db, canonical_job_id, doc_type)
        return _row_to_record(row) if row is not None else None

    def get_current_documents(self, canonical_job_id: str) -> dict[str, DocumentRecord | None]:
        """Current resume + cover letter, resolved by latest generated_at/id (query-derived)."""
        with get_db() as db:
            rows = get_latest_generated_docs(db, canonical_job_id)
        return {
            doc_type: (_row_to_record(row) if row is not None else None)
            for doc_type, row in rows.items()
        }

    # ── Actions (Package 2b — state-mutating) ────────────────────────────

    def regenerate_documents(self, canonical_job_id: str, force: bool = True) -> RegenerationResult:
        """Regenerate resume + cover letter for one job.

        Thin wrapper around `SelectionProcessor.generate_for_selected()` —
        does not reimplement generation, rendering, or upload logic. Does
        not transition `app_state`; regeneration is independent of
        selection status. New `generated_docs` rows are appended (existing
        history is never deleted or overwritten), so current/latest
        resolution after this call remains query-derived exactly as before.

        Raises DocumentRegenerationError if `canonical_job_id` does not
        exist, or if generation did not succeed.
        """
        with get_db() as db:
            exists = db.execute(
                "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
                (canonical_job_id,),
            ).fetchone()
        if not exists:
            raise DocumentRegenerationError(f"Unknown job: {canonical_job_id}")

        stats = self._processor.generate_for_selected(job_ids=[canonical_job_id], force=force)

        if stats["generated"] == 0:
            raise DocumentRegenerationError(
                f"Document regeneration failed for {canonical_job_id} "
                f"({stats['errors']} error(s) — see application logs for detail)."
            )

        doc = stats["docs"][0]
        return RegenerationResult(
            canonical_job_id=canonical_job_id,
            resume_url=doc["resume_url"],
            cover_url=doc["cover_url"],
        )
