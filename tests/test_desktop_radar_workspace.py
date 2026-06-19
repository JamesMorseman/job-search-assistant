"""ATLAS Desktop Package 4 — Radar Workspace MVP tests.

This repository has no JavaScript test runner (see frontend/package.json);
Package 3 established the convention of verifying frontend boundaries through
source-inspection checks against the TypeScript sources, mirroring the
backend's architecture-enforcement tests (see test_atlas_service_has_no_write_sql
in test_desktop_data_api.py). This file extends that convention to Package 4.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
# Phase 7 Package 5C introduced the reusable Opportunity Signal Card
# component; Radar now renders opportunity-detail routing through that
# shared component rather than inline in Radar.tsx, so route/link
# assertions below check the combined rendered source.
SIGNAL_CARD_TSX = (FRONTEND_SRC / "workspaces" / "SignalCard.tsx").read_text(encoding="utf-8")
RADAR_RENDERED_TSX = RADAR_TSX + SIGNAL_CARD_TSX
CONTEXT_PANEL_TSX = (FRONTEND_SRC / "shell" / "ContextPanel.tsx").read_text(encoding="utf-8")
CONTEXT_PANEL_CONTEXT_TSX = (
    FRONTEND_SRC / "shell" / "ContextPanelContext.tsx"
).read_text(encoding="utf-8")
APP_SHELL_TSX = (FRONTEND_SRC / "shell" / "AppShell.tsx").read_text(encoding="utf-8")


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


def test_radar_route_exists_in_frontend_routing():
    assert 'path="radar"' in APP_TSX
    assert "Radar" in APP_TSX


def test_radar_consumes_package2_api_client_boundary():
    assert 'from "../api/client"' in RADAR_TSX
    assert "getOpportunities" in RADAR_TSX
    assert "fetch(" not in RADAR_TSX


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


def test_radar_has_search_by_title_or_company():
    assert "atlas-radar-search" in RADAR_TSX
    assert "title.toLowerCase().includes" in RADAR_TSX
    assert "company.toLowerCase().includes" in RADAR_TSX


def test_radar_has_source_filter():
    assert "atlas-radar-filter" in RADAR_TSX
    assert "sourceFilter" in RADAR_TSX


def test_radar_has_selected_opportunity_state():
    assert "selectedJobId" in RADAR_TSX
    assert "handleSelect" in RADAR_TSX


def test_radar_selection_sets_context_panel_preview_with_core_fields():
    assert "useContextPanel" in RADAR_TSX
    assert "setPreview" in RADAR_TSX
    for field in ["jobId", "title", "company", "source", "location", "signalLabel", "stage", "status"]:
        assert field in RADAR_TSX


def test_context_panel_renders_preview_fields():
    assert "preview" in CONTEXT_PANEL_TSX
    assert "Source" in CONTEXT_PANEL_TSX
    assert "Location" in CONTEXT_PANEL_TSX


def test_radar_links_to_opportunity_detail_route():
    assert '/opportunities/${encodeURIComponent(' in RADAR_RENDERED_TSX
    assert "Open Opportunity Detail" in RADAR_RENDERED_TSX


def test_radar_renders_loading_state():
    assert '"loading"' in RADAR_TSX
    assert "Loading opportunities" in RADAR_TSX


def test_radar_renders_error_state():
    assert "AtlasApiError" in RADAR_TSX
    assert "Unable to load opportunities" in RADAR_TSX


def test_radar_renders_empty_state():
    assert "No signals detected" in RADAR_TSX
    assert "No opportunities match your search or filter" in RADAR_TSX


def test_radar_does_not_implement_prohibited_behavior():
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
    ]
    for term in prohibited_terms:
        assert term not in RADAR_TSX


def test_context_panel_context_does_not_implement_prohibited_behavior():
    prohibited_terms = [
        "Recommended for you",
        "Atlas recommends",
        "Ask Atlas",
        "mark_applied",
    ]
    for term in prohibited_terms:
        assert term not in CONTEXT_PANEL_CONTEXT_TSX
        assert term not in CONTEXT_PANEL_TSX


def test_app_shell_provides_context_panel_provider():
    assert "ContextPanelProvider" in APP_SHELL_TSX


def test_dashboard_routes_remain_unaffected_by_package_4(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_api_unknown_route_remains_json_404(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")


def test_atlas_radar_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/radar")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
