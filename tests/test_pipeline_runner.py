"""Tests for Phase 6 Package 4 — PipelineRunner (local-first background runner).

PipelineService remains the sole authorized write path for `pipeline_runs`;
PipelineRunner only orchestrates existing pipeline steps and calls
PipelineService to record results.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from job_search.db.connection import init_db
from job_search.pipeline import PipelineRunner
from job_search.pipeline.runner import STEP_ORDER
from job_search.services.pipeline import PipelineService

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


# ── Fake step implementations (no network/LLM/DB I/O) ───────────────────────


class FakeIngestor:
    instances: list["FakeIngestor"] = []

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        FakeIngestor.instances.append(self)

    def load_firms(self, config_path="config/firms.yaml"):
        pass

    def run(self):
        return {
            "new": 5,
            "updated": 2,
            "reposts": 1,
            "errors": 0,
            "would_insert": 0,
            "dry_run": self.dry_run,
        }


class FakeFitGrader:
    instances: list["FakeFitGrader"] = []

    def __init__(self):
        FakeFitGrader.instances.append(self)
        self.run_kwargs = None

    def run(self, dry_run: bool = False):
        self.run_kwargs = {"dry_run": dry_run}
        return {"drained": 3, "selected": 3, "graded": 3, "batch_errors": []}


class FakeDailyReporter:
    instances: list["FakeDailyReporter"] = []

    def __init__(self):
        FakeDailyReporter.instances.append(self)

    def run(self):
        return {"date": "2026-06-18", "presented": 4, "errors": 0}


class FakeSelectionProcessor:
    instances: list["FakeSelectionProcessor"] = []

    def __init__(self):
        FakeSelectionProcessor.instances.append(self)

    def generate_for_selected(self):
        return {"generated": 2, "skipped": 0, "errors": 0, "docs": []}


class FakeFollowUpEngine:
    instances: list["FakeFollowUpEngine"] = []

    def __init__(self):
        FakeFollowUpEngine.instances.append(self)

    def run(self):
        return [{"action_type": "thank_you", "company": "Acme"}]


class FailingFitGrader:
    def __init__(self):
        pass

    def run(self, dry_run: bool = False):
        return {"drained": 1, "selected": 1, "graded": 0, "batch_errors": ["boom"]}


class RaisingIngestor:
    def __init__(self, dry_run: bool = False):
        pass

    def load_firms(self, config_path="config/firms.yaml"):
        pass

    def run(self):
        raise RuntimeError("adapter unreachable")


@pytest.fixture(autouse=True)
def _reset_fake_instances():
    FakeIngestor.instances.clear()
    FakeFitGrader.instances.clear()
    FakeDailyReporter.instances.clear()
    FakeSelectionProcessor.instances.clear()
    FakeFollowUpEngine.instances.clear()
    yield


@pytest.fixture
def patch_all_steps(monkeypatch):
    monkeypatch.setattr("job_search.pipeline.runner.Ingestor", FakeIngestor)
    monkeypatch.setattr("job_search.pipeline.runner.FitGrader", FakeFitGrader)
    monkeypatch.setattr("job_search.pipeline.runner.DailyReporter", FakeDailyReporter)
    monkeypatch.setattr("job_search.pipeline.runner.SelectionProcessor", FakeSelectionProcessor)
    monkeypatch.setattr("job_search.pipeline.runner.FollowUpEngine", FakeFollowUpEngine)


class RecordingPipelineService:
    def __init__(self):
        self.calls: list[tuple] = []

    def start_run(self, run_type, *, source=None, trigger="manual"):
        self.calls.append(("start_run", run_type, source, trigger))
        return 1

    def update_counters(self, run_id, **kwargs):
        self.calls.append(("update_counters", run_id, kwargs))

    def update_status(self, run_id, status):
        self.calls.append(("update_status", run_id, status))

    def complete_run(self, run_id, **kwargs):
        self.calls.append(("complete_run", run_id, kwargs))

    def fail_run(self, run_id, **kwargs):
        self.calls.append(("fail_run", run_id, kwargs))


# ── Full run, real PipelineService against a tmp_path DB ────────────────────


def test_full_run_creates_completed_record_with_aggregated_counters(db, patch_all_steps):
    runner = PipelineRunner(pipeline_service=PipelineService(db))
    result = runner.run(run_type="full", trigger="cli")

    assert result.status == "complete"
    assert result.run_id is not None
    assert [s.name for s in result.steps] == STEP_ORDER
    assert all(s.status == "ok" for s in result.steps)

    run = PipelineService(db).get_run(result.run_id)
    assert run.status == "complete"
    assert run.run_type == "full"
    assert run.trigger == "cli"
    assert run.jobs_created == 5
    assert run.jobs_updated == 2
    assert run.jobs_seen == 5 + 2 + 1
    assert run.jobs_presented == 4
    assert run.errors_count == 0
    assert run.completed_at is not None


def test_single_step_run_type_only_executes_that_step(db, patch_all_steps):
    runner = PipelineRunner(pipeline_service=PipelineService(db))
    result = runner.run(run_type="grade", trigger="cli")

    assert [s.name for s in result.steps] == ["grade"]
    assert len(FakeFitGrader.instances) == 1
    assert len(FakeIngestor.instances) == 0
    assert len(FakeDailyReporter.instances) == 0
    assert len(FakeSelectionProcessor.instances) == 0
    assert len(FakeFollowUpEngine.instances) == 0


def test_invalid_run_type_raises_value_error(db):
    runner = PipelineRunner(pipeline_service=PipelineService(db))
    with pytest.raises(ValueError):
        runner.run(run_type="sync")


# ── Failure paths ─────────────────────────────────────────────────────────


def test_run_fails_when_step_raises_exception(db, monkeypatch, patch_all_steps):
    monkeypatch.setattr("job_search.pipeline.runner.Ingestor", RaisingIngestor)
    runner = PipelineRunner(pipeline_service=PipelineService(db))
    result = runner.run(run_type="full", trigger="cli")

    assert result.status == "failed"
    ingest_outcome = next(s for s in result.steps if s.name == "ingest")
    assert ingest_outcome.status == "error"
    assert "adapter unreachable" in ingest_outcome.error

    run = PipelineService(db).get_run(result.run_id)
    assert run.status == "failed"
    assert run.errors_count >= 1
    assert run.notes is not None
    assert "adapter unreachable" in run.notes


def test_run_fails_when_step_reports_recoverable_errors(db, monkeypatch, patch_all_steps):
    monkeypatch.setattr("job_search.pipeline.runner.FitGrader", FailingFitGrader)
    runner = PipelineRunner(pipeline_service=PipelineService(db))
    result = runner.run(run_type="full", trigger="cli")

    assert result.status == "failed"
    grade_outcome = next(s for s in result.steps if s.name == "grade")
    assert grade_outcome.status == "error"
    assert grade_outcome.error_count == 1

    run = PipelineService(db).get_run(result.run_id)
    assert run.status == "failed"
    assert run.errors_count >= 1


# ── Dry-run behavior ──────────────────────────────────────────────────────


def test_dry_run_does_not_call_start_run(patch_all_steps):
    recorder = RecordingPipelineService()
    runner = PipelineRunner(pipeline_service=recorder)
    result = runner.run(run_type="full", dry_run=True)

    assert result.status == "dry_run"
    assert result.run_id is None
    assert recorder.calls == []


def test_dry_run_executes_only_dry_run_capable_steps(patch_all_steps):
    recorder = RecordingPipelineService()
    runner = PipelineRunner(pipeline_service=recorder)
    result = runner.run(run_type="full", dry_run=True)

    by_name = {s.name: s for s in result.steps}
    assert by_name["ingest"].status == "ok"
    assert by_name["grade"].status == "ok"
    assert by_name["report"].status == "skipped"
    assert by_name["generate"].status == "skipped"
    assert by_name["followup"].status == "skipped"

    assert len(FakeIngestor.instances) == 1
    assert FakeIngestor.instances[0].dry_run is True
    assert len(FakeFitGrader.instances) == 1
    assert FakeFitGrader.instances[0].run_kwargs == {"dry_run": True}
    assert len(FakeDailyReporter.instances) == 0
    assert len(FakeSelectionProcessor.instances) == 0
    assert len(FakeFollowUpEngine.instances) == 0


def test_dry_run_writes_no_database_records(db, patch_all_steps):
    import sqlite3

    runner = PipelineRunner(pipeline_service=PipelineService(db))
    runner.run(run_type="full", dry_run=True)

    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0] == 0
    conn.close()


# ── PipelineService write-boundary enforcement ───────────────────────────


def test_pipeline_service_is_sole_writer_of_pipeline_runs():
    pattern = re.compile(r"\b(INSERT INTO|UPDATE)\s+pipeline_runs\b", re.IGNORECASE)
    offenders = []
    for path in (ROOT / "job_search").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if pattern.search(text) and path.name != "pipeline.py":
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_runner_module_contains_no_direct_pipeline_runs_writes():
    runner_src = (ROOT / "job_search" / "pipeline" / "runner.py").read_text(encoding="utf-8")
    assert "INSERT INTO pipeline_runs" not in runner_src
    assert "UPDATE pipeline_runs" not in runner_src
