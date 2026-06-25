"""Build 1 desktop-surface completion recovery coverage."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.pipeline.runner import PipelineRunResult, StepOutcome

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


@pytest.fixture
def client(db):
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_runtime_config_status_endpoint_is_safe(client, tmp_path, monkeypatch):
    profile = tmp_path / "profile.yaml"
    profile.write_text("name: Demo\n", encoding="utf-8")
    monkeypatch.setattr("job_search.config.settings.PROFILE_PATH", str(profile))
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "secret-test-key")

    resp = client.get("/atlas/api/runtime/config-status")

    assert resp.status_code == 200
    body = resp.json()
    check_names = {check["name"] for check in body["checks"]}
    assert {"DB_PATH", "OPENAI_API_KEY", "candidate profile", "local launcher"} <= check_names
    rendered = str(body)
    assert "secret-test-key" not in rendered
    assert str(profile) not in rendered
    assert "output/backups/<timestamp>/" in rendered


def test_pipeline_run_sweep_dry_run_uses_runner_and_does_not_create_run(client, db, monkeypatch):
    class FakeRunner:
        def __init__(self, pipeline_service=None):
            self.pipeline_service = pipeline_service

        def run(self, run_type="full", *, dry_run=False, trigger="cli", source=None):
            assert run_type == "full"
            assert dry_run is True
            assert trigger == "atlas_desktop"
            return PipelineRunResult(
                run_id=None,
                run_type="full",
                status="dry_run",
                dry_run=True,
                steps=[
                    StepOutcome(name="ingest", status="ok", stats={"seen": 2}),
                    StepOutcome(
                        name="generate",
                        status="skipped",
                        stats={"reason": "no native dry-run support"},
                    ),
                ],
            )

    monkeypatch.setattr("job_search.services.desktop_scan.PipelineRunner", FakeRunner)

    resp = client.post("/atlas/api/pipeline/run-sweep", json={"run_type": "full", "dry_run": True})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "dry_run"
    assert body["steps"][0]["name"] == "ingest"

    conn = sqlite3.connect(db)
    run_count = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
    conn.close()
    assert run_count == 0


def test_pipeline_run_sweep_blocks_real_generation_when_profile_is_missing(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "present")
    monkeypatch.setattr("job_search.config.settings.PROFILE_PATH", str(tmp_path / "missing.yaml"))

    resp = client.post(
        "/atlas/api/pipeline/run-sweep",
        json={"run_type": "generate", "dry_run": False},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "blocked"
    assert any(check["name"] == "candidate profile" for check in body["checks"])
    assert body["steps"] == []


def test_new_desktop_surfaces_are_routed_and_visible_in_source():
    app_source = (ROOT / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    sidebar_source = (ROOT / "frontend" / "src" / "shell" / "Sidebar.tsx").read_text(
        encoding="utf-8"
    )
    pipeline_source = (ROOT / "frontend" / "src" / "workspaces" / "Pipeline.tsx").read_text(
        encoding="utf-8"
    )
    context_source = (ROOT / "frontend" / "src" / "shell" / "ContextPanel.tsx").read_text(
        encoding="utf-8"
    )
    firms_source = (ROOT / "frontend" / "src" / "workspaces" / "FirmRepository.tsx").read_text(
        encoding="utf-8"
    )
    base_resume_source = (
        ROOT / "frontend" / "src" / "workspaces" / "BaseResumeLibrary.tsx"
    ).read_text(encoding="utf-8")
    settings_source = (ROOT / "frontend" / "src" / "workspaces" / "SettingsAbout.tsx").read_text(
        encoding="utf-8"
    )

    assert 'path="base-resumes"' in app_source
    assert 'path="settings"' in app_source
    assert "Base Resume Library" in sidebar_source
    assert "Settings / About" in sidebar_source
    assert "Run Sweep" in pipeline_source
    assert "runSweep" in pipeline_source
    assert "Score Rationale" in context_source
    assert "Pathway State" in context_source
    assert "Benefits / Risks" in context_source
    assert "ATS Tier Legend" in firms_source
    assert "Selection History" in base_resume_source
    assert "getRuntimeConfigStatus" in settings_source
