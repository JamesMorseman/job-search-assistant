"""Tests for ATLAS Desktop Package 10 — FocusResolutionService and focus_resolutions schema.

FocusResolutionService is the sole authorized write path for focus_resolutions.
All tests run against an isolated tmp_path SQLite database.
"""

from __future__ import annotations

import pytest

from job_search.db.connection import init_db
from job_search.services.focus_resolution import FocusResolutionService


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


# ── Schema / table existence ──────────────────────────────────────────────────


def test_focus_resolutions_table_exists(db):
    import sqlite3

    conn = sqlite3.connect(db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert "focus_resolutions" in tables


def test_focus_resolutions_has_required_columns(db):
    import sqlite3

    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(focus_resolutions)")}
    conn.close()
    required = {"id", "source_object", "focus_statement", "resolution", "note", "resolved_at"}
    assert required <= cols


# ── record_resolution ────────────────────────────────────────────────────────


def test_record_resolution_returns_archived_record(db):
    svc = FocusResolutionService(db)

    record = svc.record_resolution(
        source_object="pipeline-run:1",
        focus_statement="Pipeline run completed with errors",
        resolution="completed",
        note="Investigated and cleared.",
    )

    assert record.id >= 1
    assert record.source_object == "pipeline-run:1"
    assert record.resolution == "completed"
    assert record.note == "Investigated and cleared."
    assert record.resolved_at


def test_record_resolution_defaults_note_to_none(db):
    svc = FocusResolutionService(db)

    record = svc.record_resolution(
        source_object="opportunity-stage:selected",
        focus_statement="Selected opportunities deserve review",
        resolution="deferred",
    )

    assert record.note is None


@pytest.mark.parametrize(
    "resolution", ["completed", "deferred", "dismissed", "superseded", "expired"]
)
def test_record_resolution_accepts_all_lifecycle_actions(db, resolution):
    svc = FocusResolutionService(db)

    record = svc.record_resolution(
        source_object="pipeline-run:1",
        focus_statement="Pipeline run completed with errors",
        resolution=resolution,
    )

    assert record.resolution == resolution


# ── list_recent_resolutions ──────────────────────────────────────────────────


def test_list_recent_resolutions_returns_newest_first(db):
    svc = FocusResolutionService(db)
    svc.record_resolution(
        source_object="opportunity:job-1",
        focus_statement="Review current opportunity mix",
        resolution="expired",
    )
    svc.record_resolution(
        source_object="pipeline-run:1",
        focus_statement="Pipeline run completed with errors",
        resolution="completed",
    )

    records = svc.list_recent_resolutions()

    assert [r.source_object for r in records] == ["pipeline-run:1", "opportunity:job-1"]


def test_list_recent_resolutions_respects_limit(db):
    svc = FocusResolutionService(db)
    for i in range(5):
        svc.record_resolution(
            source_object=f"opportunity:job-{i}",
            focus_statement="Review current opportunity mix",
            resolution="dismissed",
        )

    records = svc.list_recent_resolutions(limit=2)

    assert len(records) == 2


def test_list_recent_resolutions_empty_when_no_records(db):
    svc = FocusResolutionService(db)

    assert svc.list_recent_resolutions() == []


# ── resolved_source_objects ──────────────────────────────────────────────────


def test_resolved_source_objects_returns_distinct_set(db):
    svc = FocusResolutionService(db)
    svc.record_resolution(
        source_object="pipeline-run:1",
        focus_statement="Pipeline run completed with errors",
        resolution="completed",
    )
    svc.record_resolution(
        source_object="pipeline-run:1",
        focus_statement="Pipeline run completed with errors",
        resolution="superseded",
    )
    svc.record_resolution(
        source_object="opportunity:job-1",
        focus_statement="Review current opportunity mix",
        resolution="dismissed",
    )

    assert svc.resolved_source_objects() == {"pipeline-run:1", "opportunity:job-1"}


def test_resolved_source_objects_empty_when_no_records(db):
    svc = FocusResolutionService(db)

    assert svc.resolved_source_objects() == set()
