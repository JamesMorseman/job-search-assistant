"""ATLAS Desktop Package 5 — Pipeline Workspace MVP tests.

This repository has no JavaScript test runner (see frontend/package.json);
Packages 3 and 4 established the convention of verifying frontend boundaries
through source-inspection checks against the TypeScript sources, mirroring
the backend's architecture-enforcement tests (see
test_atlas_service_has_no_write_sql in test_desktop_data_api.py). This file
extends that convention to Package 5, plus live HTTP tests for the new
read-only `/atlas/api/pipeline/runs` endpoint.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.services.pipeline import PipelineService

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
TYPES_TS = (FRONTEND_SRC / "api" / "types.ts").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (
    Path(__file__).resolve().parents[1] / "job_search" / "dashboard" / "routes" / "atlas_api.py"
).read_text(encoding="utf-8")


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


# ── Backend endpoint ──────────────────────────────────────────────────────


def test_pipeline_runs_route_exists_and_returns_json(client, db):
    resp = client.get("/atlas/api/pipeline/runs")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert "runs" in body
    assert "limit" in body
    assert body["runs"] == []


def test_pipeline_runs_route_uses_pipeline_service_list_recent_runs(client, db):
    service = PipelineService(db_path=db)
    run_id = service.start_run("ingest", source="greenhouse", trigger="manual")
    service.update_counters(run_id, jobs_seen=10, jobs_created=3, jobs_updated=2, errors_count=0)
    service.complete_run(run_id)

    resp = client.get("/atlas/api/pipeline/runs")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["runs"]) == 1
    run = body["runs"][0]
    assert run["id"] == run_id
    assert run["status"] == "complete"
    assert run["jobs_seen"] == 10
    assert run["jobs_created"] == 3
    assert run["jobs_updated"] == 2
    assert "started_at" in run
    assert "completed_at" in run


def test_pipeline_runs_route_reflects_running_and_failed_status(client, db):
    service = PipelineService(db_path=db)
    running_id = service.start_run("ingest", trigger="manual")
    failed_id = service.start_run("grade", trigger="manual")
    service.fail_run(failed_id, error_detail="boom")

    resp = client.get("/atlas/api/pipeline/runs")
    statuses = {run["id"]: run["status"] for run in resp.json()["runs"]}

    assert statuses[running_id] == "running"
    assert statuses[failed_id] == "failed"


def test_pipeline_runs_route_is_read_only_no_mutating_verbs_in_route_module():
    forbidden = ['@router.put(', '@router.patch(', '@router.delete(']
    for verb in forbidden:
        assert verb not in ATLAS_API_PY, f"{verb} should not appear in atlas_api.py"
    # Build 1 recovery authorizes the explicit local Run Sweep POST route.
    assert '@router.post("/pipeline/run-sweep"' in ATLAS_API_PY


def test_pipeline_route_consumes_list_recent_runs_in_source():
    assert "list_recent_runs" in ATLAS_API_PY
    assert "PipelineService" in ATLAS_API_PY


def test_package2_opportunity_endpoints_unmodified_in_source():
    assert '@router.get("/opportunities"' in ATLAS_API_PY
    assert '@router.get("/opportunities/{job_id}"' in ATLAS_API_PY
    assert '@router.get("/summary"' in ATLAS_API_PY


# ── Frontend boundary ─────────────────────────────────────────────────────


def test_client_exposes_get_pipeline_runs():
    assert "export function getPipelineRuns" in CLIENT_TS
    assert "/pipeline/runs" in CLIENT_TS


def test_types_define_pipeline_run_shape():
    assert "AtlasPipelineRun" in TYPES_TS
    assert "AtlasPipelineRunsResponse" in TYPES_TS


def test_pipeline_route_exists_in_frontend_routing():
    assert 'path="pipeline"' in APP_TSX
    assert "Pipeline" in APP_TSX


def test_pipeline_workspace_consumes_api_client_boundary():
    assert 'from "../api/client"' in PIPELINE_TSX
    assert "getPipelineRuns" in PIPELINE_TSX
    assert "fetch(" not in PIPELINE_TSX


def test_no_workspace_file_calls_fetch_directly():
    workspace_dir = FRONTEND_SRC / "workspaces"
    for path in workspace_dir.glob("*.tsx"):
        source = path.read_text(encoding="utf-8")
        assert "fetch(" not in source, f"{path.name} should not call fetch() directly"


def test_frontend_api_client_remains_centralized():
    offenders = []
    for path in FRONTEND_SRC.rglob("*.ts*"):
        if path.name == "client.ts":
            continue
        source = path.read_text(encoding="utf-8")
        if "fetch(" in source:
            offenders.append(path.name)
    assert offenders == [], f"fetch() used outside api/client.ts: {offenders}"


def test_pipeline_renders_loading_state():
    assert '"loading"' in PIPELINE_TSX
    assert "Loading pipeline runs" in PIPELINE_TSX


def test_pipeline_renders_error_state():
    assert "AtlasApiError" in PIPELINE_TSX
    assert "Unable to load pipeline runs" in PIPELINE_TSX


def test_pipeline_renders_empty_state():
    assert "No pipeline runs recorded yet" in PIPELINE_TSX


def test_pipeline_empty_state_includes_actionable_guidance():
    """Build 1 onboarding polish: tell a first-time observer how to start
    their first pipeline run, not just that none exist yet."""
    assert "jsa run" in PIPELINE_TSX


def test_pipeline_renders_run_status_counters_and_timestamps():
    assert "statusLabel" in PIPELINE_TSX
    for field in ["jobs_seen", "jobs_created", "jobs_updated", "jobs_presented", "errors_count"]:
        assert field in PIPELINE_TSX
    assert "started_at" in PIPELINE_TSX
    assert "completed_at" in PIPELINE_TSX
    assert "run.id" in PIPELINE_TSX


def test_pipeline_distinguishes_running_completed_failed():
    assert '"Running"' in PIPELINE_TSX
    assert '"Completed"' in PIPELINE_TSX
    assert '"Failed"' in PIPELINE_TSX


def test_pipeline_does_not_implement_prohibited_behavior():
    prohibited_terms = [
        "Recommended for you",
        "Atlas recommends",
        "Next action",
        "Apply now",
        "Move to Applied",
        "Start scan",
        "Refresh market",
        "Run pipeline",
        "Ask Atlas",
        "select_job",
        "reject_job",
        "mark_applied",
        "regenerate",
    ]
    for term in prohibited_terms:
        assert term not in PIPELINE_TSX, f"prohibited term/control found: {term}"


def test_pipeline_does_not_touch_context_panel_context():
    assert "ContextPanelContext" not in PIPELINE_TSX
    assert "useContextPanel" not in PIPELINE_TSX
    assert "setPreview" not in PIPELINE_TSX


def test_radar_and_opportunity_detail_surfaces_untouched_by_pipeline_work():
    for forbidden in ["getPipelineRuns", "AtlasPipelineRun", "PipelineService"]:
        assert forbidden not in RADAR_TSX
        assert forbidden not in OPPORTUNITY_DETAIL_SURFACE_TSX


# ── Route isolation ───────────────────────────────────────────────────────


def test_dashboard_routes_remain_unaffected_by_package_5(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_api_unknown_route_remains_json_404(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")


def test_atlas_pipeline_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/pipeline")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
