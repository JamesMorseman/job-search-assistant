"""ATLAS Desktop Package 6 — Command Center MVP tests.

This repository has no JavaScript test runner (see frontend/package.json);
Packages 3-5 established the convention of verifying frontend boundaries
through source-inspection checks against the TypeScript sources, mirroring
the backend's architecture-enforcement tests (see
test_atlas_service_has_no_write_sql in test_desktop_data_api.py). This file
extends that convention to Package 6.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
COMMAND_CENTER_TSX = (
    FRONTEND_SRC / "workspaces" / "CommandCenter.tsx"
).read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (
    Path(__file__).resolve().parents[1] / "job_search" / "dashboard" / "routes" / "atlas_api.py"
).read_text(encoding="utf-8")
CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
TYPES_TS = (FRONTEND_SRC / "api" / "types.ts").read_text(encoding="utf-8")


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


# ── Routing / placeholder replacement ────────────────────────────────────


def test_command_center_route_exists_in_frontend_routing():
    assert 'path="command-center"' in APP_TSX
    assert "CommandCenter" in APP_TSX


def test_command_center_placeholder_is_replaced():
    assert "WorkspacePlaceholder" not in COMMAND_CENTER_TSX
    assert "Workspace placeholder" not in COMMAND_CENTER_TSX


# ── Data consumption ──────────────────────────────────────────────────────


def test_command_center_uses_get_summary():
    assert 'from "../api/client"' in COMMAND_CENTER_TSX
    assert "getSummary" in COMMAND_CENTER_TSX


def test_command_center_uses_get_pipeline_runs():
    assert "getPipelineRuns" in COMMAND_CENTER_TSX


def test_command_center_uses_get_recommendations():
    assert "getRecommendations" in COMMAND_CENTER_TSX


def test_command_center_uses_get_focuses():
    assert "getFocuses" in COMMAND_CENTER_TSX


def test_command_center_does_not_call_fetch_directly():
    assert "fetch(" not in COMMAND_CENTER_TSX


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


def test_command_center_no_backend_endpoint_added():
    assert "command-center" not in ATLAS_API_PY


def test_frontend_client_exposes_get_recommendations():
    assert "export function getRecommendations" in CLIENT_TS
    assert '"/recommendations"' in CLIENT_TS


def test_frontend_types_define_recommendation_shape():
    assert "AtlasRecommendation" in TYPES_TS
    assert "AtlasRecommendationsResponse" in TYPES_TS
    assert "action_surface" in TYPES_TS


def test_frontend_client_and_types_define_focus_shape():
    assert "export function getFocuses" in CLIENT_TS
    assert "AtlasFocus" in TYPES_TS
    assert "AtlasFocusListResponse" in TYPES_TS


# ── Panel content ──────────────────────────────────────────────────────────


def test_opportunity_signal_panel_renders_total_and_stage_distribution():
    assert "total_opportunities" in COMMAND_CENTER_TSX
    assert "stages" in COMMAND_CENTER_TSX
    assert "Recent Signals" in COMMAND_CENTER_TSX


def test_pipeline_snapshot_panel_renders_status_counters_timestamp():
    assert "Pipeline Snapshot" in COMMAND_CENTER_TSX
    assert "mostRecentRun" in COMMAND_CENTER_TSX
    assert "jobs_seen" in COMMAND_CENTER_TSX
    assert "started_at" in COMMAND_CENTER_TSX


def test_recommendations_section_renders_from_api_data():
    assert "Recommendations engine not yet active" not in COMMAND_CENTER_TSX
    assert "recommendationState" in COMMAND_CENTER_TSX
    assert "recommendation.text" in COMMAND_CENTER_TSX
    assert "recommendation.priority" in COMMAND_CENTER_TSX
    assert "recommendation.action_surface" in COMMAND_CENTER_TSX


def test_focus_section_renders_from_api_data():
    assert "Atlas Focus" in COMMAND_CENTER_TSX
    assert "focus.focus_statement" in COMMAND_CENTER_TSX
    assert "focus.reason" in COMMAND_CENTER_TSX
    assert "focus.source_object" in COMMAND_CENTER_TSX
    assert "focus.attention_horizon" in COMMAND_CENTER_TSX
    assert "focus.next_action" in COMMAND_CENTER_TSX
    assert "focus.resolution_state" in COMMAND_CENTER_TSX


def test_navigation_shortcuts_present():
    assert 'to="/radar"' in COMMAND_CENTER_TSX
    assert 'to="/pipeline"' in COMMAND_CENTER_TSX


# ── States ────────────────────────────────────────────────────────────────


def test_loading_states_exist():
    assert "Loading opportunity signals" in COMMAND_CENTER_TSX
    assert "Loading pipeline snapshot" in COMMAND_CENTER_TSX
    assert "Loading recommendations" in COMMAND_CENTER_TSX
    assert "Loading Atlas Focus" in COMMAND_CENTER_TSX


def test_error_states_exist():
    assert "AtlasApiError" in COMMAND_CENTER_TSX
    assert "Unable to load opportunity signals" in COMMAND_CENTER_TSX
    assert "Unable to load pipeline snapshot" in COMMAND_CENTER_TSX
    assert "Unable to load recommendations" in COMMAND_CENTER_TSX
    assert "Unable to load Atlas Focus" in COMMAND_CENTER_TSX


def test_empty_states_exist():
    assert "No opportunities tracked yet" in COMMAND_CENTER_TSX
    assert "No pipeline runs recorded yet" in COMMAND_CENTER_TSX
    assert "No recommendations available yet" in COMMAND_CENTER_TSX
    assert "No active Focus objects right now" in COMMAND_CENTER_TSX


# ── Boundary / scope enforcement ─────────────────────────────────────────


def test_command_center_does_not_touch_context_panel_context():
    assert "ContextPanelContext" not in COMMAND_CENTER_TSX
    assert "useContextPanel" not in COMMAND_CENTER_TSX
    assert "setPreview" not in COMMAND_CENTER_TSX


def test_command_center_does_not_implement_prohibited_behavior():
    prohibited_terms = [
        "Recommended for you",
        "Best opportunities",
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
        "<button",
        "<form",
    ]
    for term in prohibited_terms:
        assert term not in COMMAND_CENTER_TSX, f"prohibited term found: {term}"


def test_radar_and_pipeline_and_opportunity_detail_untouched_by_command_center_work():
    assert "CommandCenter" not in RADAR_TSX
    assert "CommandCenter" not in PIPELINE_TSX
    assert "CommandCenter" not in OPPORTUNITY_DETAIL_SURFACE_TSX


def test_package2_and_package5_api_boundaries_unmodified_in_source():
    assert '@router.get("/opportunities"' in ATLAS_API_PY
    assert '@router.get("/opportunities/{job_id}"' in ATLAS_API_PY
    assert '@router.get("/summary"' in ATLAS_API_PY
    assert '@router.get("/pipeline/runs"' in ATLAS_API_PY


# ── Route isolation ───────────────────────────────────────────────────────


def test_dashboard_routes_remain_unaffected_by_package_6(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_api_unknown_route_remains_json_404(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")


def test_atlas_command_center_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/command-center")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
