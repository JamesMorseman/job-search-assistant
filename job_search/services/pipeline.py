"""Pipeline run service — sole authorized write path for pipeline_runs records.

No dashboard route, template, FunnelReporter, FunnelStats, MetricsService,
or analytics code may mutate pipeline_runs. All runtime writes must go through
PipelineService (Phase 6 Package 3).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from pydantic import BaseModel

from job_search.db import get_db


class PipelineRun(BaseModel):
    """Read model for a single pipeline run record."""

    id: int
    run_type: str
    status: str
    started_at: str
    completed_at: str | None
    source: str | None
    trigger: str
    jobs_seen: int
    jobs_created: int
    jobs_updated: int
    jobs_presented: int
    errors_count: int
    metadata_json: str | None
    notes: str | None


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def _row_to_run(row) -> PipelineRun:
    return PipelineRun(
        id=row["id"],
        run_type=row["run_type"],
        status=row["status"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        source=row["source"],
        trigger=row["trigger"],
        jobs_seen=row["jobs_seen"] or 0,
        jobs_created=row["jobs_created"] or 0,
        jobs_updated=row["jobs_updated"] or 0,
        jobs_presented=row["jobs_presented"] or 0,
        errors_count=row["errors_count"] or 0,
        metadata_json=row["metadata_json"],
        notes=row["notes"],
    )


class PipelineService:
    """Read/write service for pipeline_runs.

    All mutations go through this class. Read methods return shapes suitable
    for a future Pipeline Runs dashboard screen (Phase 6 Package 5).
    """

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path

    # ── Write methods ─────────────────────────────────────────────────────────

    def start_run(
        self,
        run_type: str,
        *,
        source: str | None = None,
        trigger: str = "manual",
    ) -> int:
        """Create a new run record in 'running' status. Returns the new run id."""
        with get_db(self._db_path) as db:
            cur = db.execute(
                """
                INSERT INTO pipeline_runs (run_type, status, started_at, source, trigger)
                VALUES (?, 'running', ?, ?, ?)
                """,
                (run_type, _now_iso(), source, trigger),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def update_counters(
        self,
        run_id: int,
        *,
        jobs_seen: int | None = None,
        jobs_created: int | None = None,
        jobs_updated: int | None = None,
        jobs_presented: int | None = None,
        errors_count: int | None = None,
    ) -> None:
        """Set counter fields on a run. Only supplied (non-None) fields are updated."""
        fields: list[str] = []
        values: list[object] = []
        for col, val in (
            ("jobs_seen", jobs_seen),
            ("jobs_created", jobs_created),
            ("jobs_updated", jobs_updated),
            ("jobs_presented", jobs_presented),
            ("errors_count", errors_count),
        ):
            if val is not None:
                fields.append(f"{col} = ?")
                values.append(val)
        if not fields:
            return
        values.append(run_id)
        with get_db(self._db_path) as db:
            db.execute(
                f"UPDATE pipeline_runs SET {', '.join(fields)} WHERE id = ?",
                values,
            )

    def update_status(self, run_id: int, status: str) -> None:
        """Update the status field of an existing run."""
        with get_db(self._db_path) as db:
            db.execute(
                "UPDATE pipeline_runs SET status = ? WHERE id = ?",
                (status, run_id),
            )

    def complete_run(
        self,
        run_id: int,
        *,
        metadata: dict | None = None,
        notes: str | None = None,
    ) -> None:
        """Mark a run as complete, persisting optional metadata and notes."""
        with get_db(self._db_path) as db:
            db.execute(
                """
                UPDATE pipeline_runs
                SET status = 'complete',
                    completed_at = ?,
                    metadata_json = COALESCE(?, metadata_json),
                    notes = COALESCE(?, notes)
                WHERE id = ?
                """,
                (
                    _now_iso(),
                    json.dumps(metadata) if metadata is not None else None,
                    notes,
                    run_id,
                ),
            )

    def fail_run(
        self,
        run_id: int,
        *,
        error_detail: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Mark a run as failed, persisting optional error detail in notes."""
        with get_db(self._db_path) as db:
            db.execute(
                """
                UPDATE pipeline_runs
                SET status = 'failed',
                    completed_at = ?,
                    notes = COALESCE(?, notes),
                    metadata_json = COALESCE(?, metadata_json)
                WHERE id = ?
                """,
                (
                    _now_iso(),
                    error_detail,
                    json.dumps(metadata) if metadata is not None else None,
                    run_id,
                ),
            )

    # ── Read methods ──────────────────────────────────────────────────────────

    def list_recent_runs(self, limit: int = 20) -> list[PipelineRun]:
        """Return the most recent pipeline runs, newest first."""
        with get_db(self._db_path) as db:
            rows = db.execute(
                "SELECT * FROM pipeline_runs ORDER BY started_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_run(r) for r in rows]

    def get_run(self, run_id: int) -> PipelineRun | None:
        """Return a single run by id, or None if not found."""
        with get_db(self._db_path) as db:
            row = db.execute(
                "SELECT * FROM pipeline_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        return _row_to_run(row) if row else None
