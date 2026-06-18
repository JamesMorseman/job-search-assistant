"""Focus resolution and archive service.

Sole authorized write path for `focus_resolutions` records (ATLAS Desktop
Package 10). Persists bounded Atlas Focus lifecycle outcomes — completed,
deferred, dismissed, superseded, expired — per
`docs/Brand/ATLAS_Focus_Object_v1_Visual_Reference.md` ("How Focuses Are
Resolved"). No dashboard route, template, or other service may write to
`focus_resolutions` directly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

from job_search.db import get_db

FocusResolutionAction = Literal["completed", "deferred", "dismissed", "superseded", "expired"]


class FocusResolutionRecord(BaseModel):
    """Read model for a single Focus resolution/archive entry."""

    id: int
    source_object: str
    focus_statement: str
    resolution: FocusResolutionAction
    note: str | None
    resolved_at: str


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def _row_to_record(row) -> FocusResolutionRecord:
    return FocusResolutionRecord(
        id=row["id"],
        source_object=row["source_object"],
        focus_statement=row["focus_statement"],
        resolution=row["resolution"],
        note=row["note"],
        resolved_at=row["resolved_at"],
    )


class FocusResolutionService:
    """Read/write service for `focus_resolutions` — the Atlas Focus archive."""

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path

    # ── Write methods ─────────────────────────────────────────────────────────

    def record_resolution(
        self,
        *,
        source_object: str,
        focus_statement: str,
        resolution: FocusResolutionAction,
        note: str | None = None,
    ) -> FocusResolutionRecord:
        """Persist a Focus lifecycle outcome and return the archived record."""
        with get_db(self._db_path) as db:
            cur = db.execute(
                """
                INSERT INTO focus_resolutions
                    (source_object, focus_statement, resolution, note, resolved_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source_object, focus_statement, resolution, note, _now_iso()),
            )
            row = db.execute(
                "SELECT * FROM focus_resolutions WHERE id = ?",
                (cur.lastrowid,),
            ).fetchone()
        return _row_to_record(row)

    # ── Read methods ──────────────────────────────────────────────────────────

    def list_recent_resolutions(self, limit: int = 20) -> list[FocusResolutionRecord]:
        """Return the most recent Focus resolutions, newest first."""
        with get_db(self._db_path) as db:
            rows = db.execute(
                "SELECT * FROM focus_resolutions ORDER BY resolved_at DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_record(r) for r in rows]

    def resolved_source_objects(self) -> set[str]:
        """Return the set of `source_object` values that have any resolution record."""
        with get_db(self._db_path) as db:
            rows = db.execute("SELECT DISTINCT source_object FROM focus_resolutions").fetchall()
        return {row["source_object"] for row in rows}
