"""Tests for Phase 6 Package 3 — PipelineService and pipeline_runs schema.

PipelineService is the sole authorized write path for pipeline_runs.
All tests run against an isolated tmp_path SQLite database.
"""

from __future__ import annotations

import json

import pytest

from job_search.db.connection import init_db
from job_search.services.pipeline import PipelineService


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


# ── Schema / table existence ──────────────────────────────────────────────────


def test_pipeline_runs_table_exists(db):
    import sqlite3

    conn = sqlite3.connect(db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert "pipeline_runs" in tables


def test_pipeline_runs_has_required_columns(db):
    import sqlite3

    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(pipeline_runs)")}
    conn.close()
    required = {
        "id", "run_type", "status", "started_at", "completed_at",
        "source", "trigger", "jobs_seen", "jobs_created", "jobs_updated",
        "jobs_presented", "errors_count", "metadata_json", "notes",
    }
    assert required <= cols


# ── start_run ─────────────────────────────────────────────────────────────────


def test_start_run_returns_integer_id(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    assert isinstance(run_id, int)
    assert run_id >= 1


def test_start_run_creates_running_record(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", source="greenhouse", trigger="cli")
    run = svc.get_run(run_id)
    assert run is not None
    assert run.status == "running"
    assert run.run_type == "ingest"
    assert run.source == "greenhouse"
    assert run.trigger == "cli"
    assert run.started_at is not None
    assert run.completed_at is None


def test_start_run_defaults(db):
    svc = PipelineService(db)
    run_id = svc.start_run("grade")
    run = svc.get_run(run_id)
    assert run.source is None
    assert run.trigger == "manual"
    assert run.jobs_seen == 0
    assert run.errors_count == 0


def test_multiple_runs_get_distinct_ids(db):
    svc = PipelineService(db)
    ids = [svc.start_run("ingest") for _ in range(3)]
    assert len(set(ids)) == 3


# ── update_counters ───────────────────────────────────────────────────────────


def test_update_counters_sets_supplied_fields(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.update_counters(run_id, jobs_seen=50, jobs_created=10, jobs_updated=5)
    run = svc.get_run(run_id)
    assert run.jobs_seen == 50
    assert run.jobs_created == 10
    assert run.jobs_updated == 5
    assert run.jobs_presented == 0   # untouched
    assert run.errors_count == 0     # untouched


def test_update_counters_ignores_none_fields(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.update_counters(run_id, jobs_seen=10)
    svc.update_counters(run_id, jobs_created=3)  # jobs_seen not overwritten
    run = svc.get_run(run_id)
    assert run.jobs_seen == 10
    assert run.jobs_created == 3


def test_update_counters_noop_when_all_none(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.update_counters(run_id)  # all None — should not error
    run = svc.get_run(run_id)
    assert run.jobs_seen == 0


def test_update_counters_errors_count(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.update_counters(run_id, errors_count=2)
    run = svc.get_run(run_id)
    assert run.errors_count == 2


# ── update_status ─────────────────────────────────────────────────────────────


def test_update_status_changes_status(db):
    svc = PipelineService(db)
    run_id = svc.start_run("report")
    svc.update_status(run_id, "complete")
    run = svc.get_run(run_id)
    assert run.status == "complete"


# ── complete_run ──────────────────────────────────────────────────────────────


def test_complete_run_sets_status_and_timestamp(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.complete_run(run_id)
    run = svc.get_run(run_id)
    assert run.status == "complete"
    assert run.completed_at is not None


def test_complete_run_persists_metadata(db):
    svc = PipelineService(db)
    run_id = svc.start_run("grade")
    meta = {"model": "claude-sonnet-4-6", "batch_id": "batch_abc123"}
    svc.complete_run(run_id, metadata=meta)
    run = svc.get_run(run_id)
    assert run.metadata_json is not None
    decoded = json.loads(run.metadata_json)
    assert decoded["model"] == "claude-sonnet-4-6"
    assert decoded["batch_id"] == "batch_abc123"


def test_complete_run_persists_notes(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    svc.complete_run(run_id, notes="Processed greenhouse feed only.")
    run = svc.get_run(run_id)
    assert run.notes == "Processed greenhouse feed only."


def test_complete_run_without_metadata_leaves_existing_notes(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest")
    # Pre-set notes via update_counters (no direct notes path here —
    # complete_run uses COALESCE so pre-existing NULL stays NULL)
    svc.complete_run(run_id)
    run = svc.get_run(run_id)
    assert run.status == "complete"
    assert run.notes is None


# ── fail_run ──────────────────────────────────────────────────────────────────


def test_fail_run_sets_status_and_timestamp(db):
    svc = PipelineService(db)
    run_id = svc.start_run("generate")
    svc.fail_run(run_id)
    run = svc.get_run(run_id)
    assert run.status == "failed"
    assert run.completed_at is not None


def test_fail_run_persists_error_detail(db):
    svc = PipelineService(db)
    run_id = svc.start_run("generate")
    svc.fail_run(run_id, error_detail="OpenAI rate limit exceeded")
    run = svc.get_run(run_id)
    assert run.notes == "OpenAI rate limit exceeded"


def test_fail_run_persists_metadata(db):
    svc = PipelineService(db)
    run_id = svc.start_run("grade")
    meta = {"provider": "openai", "http_status": 429}
    svc.fail_run(run_id, metadata=meta)
    run = svc.get_run(run_id)
    assert run.metadata_json is not None
    decoded = json.loads(run.metadata_json)
    assert decoded["http_status"] == 429


# ── list_recent_runs ──────────────────────────────────────────────────────────


def test_list_recent_runs_empty_on_empty_db(db):
    svc = PipelineService(db)
    assert svc.list_recent_runs() == []


def test_list_recent_runs_returns_all_when_under_limit(db):
    svc = PipelineService(db)
    svc.start_run("ingest")
    svc.start_run("grade")
    svc.start_run("report")
    runs = svc.list_recent_runs()
    assert len(runs) == 3


def test_list_recent_runs_ordered_newest_first(db):
    svc = PipelineService(db)
    id1 = svc.start_run("ingest")
    id2 = svc.start_run("grade")
    id3 = svc.start_run("report")
    runs = svc.list_recent_runs()
    assert [r.id for r in runs] == [id3, id2, id1]


def test_list_recent_runs_respects_limit(db):
    svc = PipelineService(db)
    for _ in range(5):
        svc.start_run("ingest")
    runs = svc.list_recent_runs(limit=3)
    assert len(runs) == 3


def test_list_recent_runs_returns_pipelinerun_models(db):
    svc = PipelineService(db)
    svc.start_run("ingest", source="usajobs")
    runs = svc.list_recent_runs()
    assert len(runs) == 1
    run = runs[0]
    assert run.run_type == "ingest"
    assert run.source == "usajobs"
    assert run.status == "running"


# ── get_run ───────────────────────────────────────────────────────────────────


def test_get_summary_empty_on_empty_db(db):
    summary = PipelineService(db).get_summary()
    assert summary.total_runs == 0
    assert summary.running_count == 0
    assert summary.failed_count == 0
    assert summary.last_run_at is None
    assert summary.last_successful_run_at is None


def test_get_summary_counts_global_statuses(db):
    svc = PipelineService(db)
    complete_id = svc.start_run("ingest")
    svc.complete_run(complete_id)
    failed_id = svc.start_run("grade")
    svc.fail_run(failed_id)
    svc.start_run("report")

    summary = svc.get_summary()
    assert summary.total_runs == 3
    assert summary.running_count == 1
    assert summary.failed_count == 1
    assert summary.last_run_at is not None
    assert summary.last_successful_run_at is not None


def test_get_summary_last_successful_run_uses_completed_at_for_complete_runs(db):
    import sqlite3

    conn = sqlite3.connect(db)
    conn.execute(
        """
        INSERT INTO pipeline_runs (run_type, status, started_at, completed_at, trigger)
        VALUES
            ('ingest', 'complete', '2026-01-01T10:00:00', '2026-01-01T10:05:00', 'cli'),
            ('grade', 'failed', '2026-01-02T10:00:00', '2026-01-02T10:05:00', 'cli'),
            ('report', 'complete', '2026-01-03T10:00:00', '2026-01-03T10:08:00', 'manual')
        """
    )
    conn.commit()
    conn.close()

    summary = PipelineService(db).get_summary()
    assert summary.last_run_at == "2026-01-03T10:00:00"
    assert summary.last_successful_run_at == "2026-01-03T10:08:00"


def test_get_run_returns_none_for_missing_id(db):
    svc = PipelineService(db)
    assert svc.get_run(99999) is None


def test_get_run_returns_correct_record(db):
    svc = PipelineService(db)
    run_id = svc.start_run("full", source=None, trigger="scheduled")
    run = svc.get_run(run_id)
    assert run is not None
    assert run.id == run_id
    assert run.run_type == "full"
    assert run.trigger == "scheduled"


# ── Full lifecycle integration ────────────────────────────────────────────────


def test_full_success_lifecycle(db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", source="greenhouse", trigger="cli")
    svc.update_counters(run_id, jobs_seen=120, jobs_created=8, jobs_updated=3)
    svc.complete_run(run_id, metadata={"adapter": "greenhouse"}, notes="OK")
    run = svc.get_run(run_id)
    assert run.status == "complete"
    assert run.jobs_seen == 120
    assert run.jobs_created == 8
    assert run.jobs_updated == 3
    assert run.completed_at is not None
    assert json.loads(run.metadata_json)["adapter"] == "greenhouse"
    assert run.notes == "OK"


def test_full_failure_lifecycle(db):
    svc = PipelineService(db)
    run_id = svc.start_run("grade")
    svc.update_counters(run_id, jobs_seen=10, errors_count=10)
    svc.fail_run(run_id, error_detail="Batch API unavailable", metadata={"retries": 3})
    run = svc.get_run(run_id)
    assert run.status == "failed"
    assert run.errors_count == 10
    assert run.notes == "Batch API unavailable"
    assert json.loads(run.metadata_json)["retries"] == 3


def test_mixed_statuses_in_recent_runs(db):
    svc = PipelineService(db)
    id1 = svc.start_run("ingest")
    id2 = svc.start_run("grade")
    id3 = svc.start_run("report")
    svc.complete_run(id1)
    svc.fail_run(id2, error_detail="timeout")
    # id3 remains 'running'
    runs = svc.list_recent_runs()
    by_id = {r.id: r for r in runs}
    assert by_id[id1].status == "complete"
    assert by_id[id2].status == "failed"
    assert by_id[id3].status == "running"
