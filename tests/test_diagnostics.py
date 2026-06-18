"""Tests for Phase 7 Package 1 — credential & configuration diagnostics.

Covers job_search.diagnostics unit checks, the `jsa check` CLI command,
and the `jsa run` pre-flight guard (which must prevent a `pipeline_runs`
record from being written when required credentials are missing).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from click.testing import CliRunner

from job_search.db.connection import init_db
from job_search.diagnostics import (
    check_database_connectivity,
    check_openai_api_key,
    run_all_checks,
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_db(tmp_path) -> str:
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


# ── Unit checks ──────────────────────────────────────────────────────────────


def test_check_openai_api_key_passes_when_present(monkeypatch):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "sk-test-key")
    result = check_openai_api_key()
    assert result.status == "pass"
    assert "sk-test-key" not in result.detail


def test_check_openai_api_key_fails_when_missing(monkeypatch):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "")
    result = check_openai_api_key()
    assert result.status == "fail"
    assert "missing" in result.detail


def test_check_database_connectivity_passes_for_valid_db(monkeypatch, test_db):
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    result = check_database_connectivity()
    assert result.status == "pass"


def test_check_database_connectivity_does_not_create_missing_db_file(monkeypatch, tmp_path):
    missing_db = tmp_path / "missing.db"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(missing_db))

    result = check_database_connectivity()

    assert result.status == "fail"
    assert "not found" in result.detail
    assert not missing_db.exists()


def test_check_database_connectivity_fails_for_unreachable_path_without_creating_parent(monkeypatch, tmp_path):
    bad_path = tmp_path / "no_such_dir" / "jobs.db"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(bad_path))

    result = check_database_connectivity()

    assert result.status == "fail"
    assert not bad_path.exists()
    assert not bad_path.parent.exists()


def test_check_database_connectivity_does_not_create_wal_or_shm_files(monkeypatch, tmp_path):
    db_path = tmp_path / "existing.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE marker (id INTEGER PRIMARY KEY)")
    conn.close()
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(db_path))
    wal_path = Path(f"{db_path}-wal")
    shm_path = Path(f"{db_path}-shm")

    result = check_database_connectivity()

    assert result.status == "pass"
    assert not wal_path.exists()
    assert not shm_path.exists()


def test_run_all_checks_returns_both_checks(monkeypatch, test_db):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    results = run_all_checks()
    names = {r.name for r in results}
    assert names == {"OPENAI_API_KEY", "DB_PATH"}
    assert all(r.status == "pass" for r in results)


# ── `jsa check` CLI command ──────────────────────────────────────────────────


def test_jsa_check_exits_zero_when_all_required_present(monkeypatch, test_db, runner):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["check"])
    assert result.exit_code == 0
    assert "PASS" in result.output
    assert "sk-test-key" not in result.output


def test_jsa_check_exits_nonzero_when_openai_key_missing(monkeypatch, test_db, runner):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["check"])
    assert result.exit_code != 0
    assert "FAIL" in result.output
    assert "OPENAI_API_KEY" in result.output


def test_jsa_check_never_prints_secret_value(monkeypatch, test_db, runner):
    secret = "sk-super-secret-value-12345"
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", secret)
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["check"])
    assert secret not in result.output


# ── `jsa run` pre-flight guard ───────────────────────────────────────────────


def test_run_without_openai_key_writes_no_pipeline_runs_record(monkeypatch, test_db, runner):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["run", "--run-type", "full"])

    assert result.exit_code != 0
    conn = sqlite3.connect(test_db)
    assert conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0] == 0
    conn.close()


def test_run_dry_run_unaffected_by_guard_when_openai_key_missing(monkeypatch, test_db, runner, _patch_all_steps):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["run", "--dry-run", "--run-type", "full"])

    assert result.exit_code == 0
    conn = sqlite3.connect(test_db)
    assert conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0] == 0
    conn.close()


def test_run_proceeds_when_openai_key_present(monkeypatch, test_db, runner, _patch_all_steps):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli

    result = runner.invoke(cli, ["run", "--run-type", "full"])

    assert result.exit_code == 0
    conn = sqlite3.connect(test_db)
    assert conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0] == 1
    conn.close()


# ── Fake step implementations (no network/LLM/DB I/O) ───────────────────────


class _FakeIngestor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def load_firms(self, config_path="config/firms.yaml"):
        pass

    def run(self):
        return {"new": 1, "updated": 0, "reposts": 0, "errors": 0, "would_insert": 0, "dry_run": self.dry_run}


class _FakeFitGrader:
    def __init__(self):
        pass

    def run(self, dry_run: bool = False):
        return {"drained": 0, "selected": 0, "graded": 0, "batch_errors": []}


class _FakeDailyReporter:
    def __init__(self):
        pass

    def run(self):
        return {"date": "2026-06-18", "presented": 0, "errors": 0}


class _FakeSelectionProcessor:
    def __init__(self):
        pass

    def generate_for_selected(self):
        return {"generated": 0, "skipped": 0, "errors": 0, "docs": []}


class _FakeFollowUpEngine:
    def __init__(self):
        pass

    def run(self):
        return []


@pytest.fixture
def _patch_all_steps(monkeypatch):
    monkeypatch.setattr("job_search.pipeline.runner.Ingestor", _FakeIngestor)
    monkeypatch.setattr("job_search.pipeline.runner.FitGrader", _FakeFitGrader)
    monkeypatch.setattr("job_search.pipeline.runner.DailyReporter", _FakeDailyReporter)
    monkeypatch.setattr("job_search.pipeline.runner.SelectionProcessor", _FakeSelectionProcessor)
    monkeypatch.setattr("job_search.pipeline.runner.FollowUpEngine", _FakeFollowUpEngine)
