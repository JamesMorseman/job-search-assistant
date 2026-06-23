"""ATLAS Desktop Package 3 — Opportunity Detail Surface MVP tests.

This repository has no JavaScript test runner (see frontend/package.json);
Packages 1-2 verified frontend boundaries only through backend API tests and
the build step. These tests extend that convention with source-inspection
checks against the frontend TypeScript sources, mirroring the existing
pattern used for backend route/service boundary enforcement (see
test_atlas_service_has_no_write_sql in test_desktop_data_api.py).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
SURFACE_TSX = (FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx").read_text(encoding="utf-8")
PLACEHOLDER_TSX = (FRONTEND_SRC / "workspaces" / "OpportunityDetail.tsx").read_text(encoding="utf-8")


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


def test_opportunity_detail_route_exists_in_frontend_routing():
    assert 'path="opportunities/:jobId"' in APP_TSX
    assert "OpportunityDetailSurface" in APP_TSX


def test_surface_consumes_package2_api_client_boundary():
    assert 'from "../api/client"' in SURFACE_TSX
    assert "getOpportunity" in SURFACE_TSX
    assert "fetch(" not in SURFACE_TSX


def test_surface_renders_loading_state():
    assert '"loading"' in SURFACE_TSX
    assert "Loading opportunity" in SURFACE_TSX


def test_surface_renders_not_found_state():
    assert '"not-found"' in SURFACE_TSX
    assert "Opportunity not found" in SURFACE_TSX


def test_surface_renders_error_state():
    assert "AtlasApiError" in SURFACE_TSX
    assert "Unable to load this opportunity" in SURFACE_TSX


def test_surface_uses_advisory_match_and_stored_score_language():
    assert "High Advisory Match" in SURFACE_TSX
    assert "Stored Match Score" in SURFACE_TSX
    assert "Exceptional Match" not in SURFACE_TSX
    assert "Atlas Confidence" not in SURFACE_TSX


def test_no_workspace_placeholder_calls_fetch_directly():
    workspace_dir = FRONTEND_SRC / "workspaces"
    for path in workspace_dir.glob("*.tsx"):
        if path.name == "OpportunityDetailSurface.tsx":
            continue
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


def test_opportunity_detail_placeholder_shows_neutral_instruction():
    assert "Select an opportunity to view details." in PLACEHOLDER_TSX


def test_surface_does_not_implement_prohibited_behavior():
    prohibited_terms = [
        "Atlas recommends",
        "Next best action",
        "You should apply",
        "select_job",
        "reject_job",
        "mark_applied",
        "regenerate",
    ]
    for term in prohibited_terms:
        assert term not in SURFACE_TSX


def test_atlas_opportunity_detail_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/opportunities/job-1")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")


def test_dashboard_routes_remain_unaffected_by_package_3(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text
