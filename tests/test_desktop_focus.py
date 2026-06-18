"""ATLAS Desktop Package 9 Focus API and Command Center tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_focus_service
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.focus import AtlasFocus
from job_search.services.pipeline import PipelineService

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
COMMAND_CENTER_TSX = (
    FRONTEND_SRC / "workspaces" / "CommandCenter.tsx"
).read_text(encoding="utf-8")
COMMAND_CENTER_CSS = (
    FRONTEND_SRC / "workspaces" / "commandCenter.css"
).read_text(encoding="utf-8")
CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
TYPES_TS = (FRONTEND_SRC / "api" / "types.ts").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
ASK_ATLAS_TSX = (FRONTEND_SRC / "workspaces" / "AskAtlas.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py").read_text(
    encoding="utf-8"
)
DEPS_PY = (ROOT / "job_search" / "dashboard" / "deps.py").read_text(encoding="utf-8")
SCHEMA_SQL = (ROOT / "job_search" / "db" / "schema.sql").read_text(encoding="utf-8")


class FakeFocusService:
    def __init__(self):
        self.calls = []

    def list_active_focuses(self, *, summary, opportunities, most_recent_run):
        self.calls.append((summary, opportunities, most_recent_run))
        return [
            AtlasFocus(
                focus_statement="Review new Radar intake",
                reason="Two new opportunities appeared in the latest run.",
                source_object="pipeline-run:9",
                attention_horizon="today",
                next_action="Open Radar and compare the newest opportunity signals.",
                resolution_state="active",
            )
        ]


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


@pytest.fixture
def app(db):
    app = create_app()
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


def _insert_job(db_path: str, job_id: str, **overrides):
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    dedup = Deduplicator(conn)
    job_kwargs = dict(
        canonical_job_id=job_id,
        source="greenhouse",
        source_job_id=job_id,
        company="Acme Engineering",
        title="Civil Engineer",
        description_raw="Raw civil engineering description",
        description_normalized="Normalized civil engineering description",
        match_score=0.8,
        stretch_category="qualified",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def test_focuses_endpoint_returns_read_only_focus_shape(client, app, db):
    fake = FakeFocusService()
    app.dependency_overrides[get_focus_service] = lambda: fake
    _insert_job(db, "job-1", app_state="discovered")
    pipeline = PipelineService(db_path=db)
    run_id = pipeline.start_run("ingest", trigger="manual")
    pipeline.update_counters(run_id, jobs_created=2)
    pipeline.complete_run(run_id)

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["focuses", "generated_at"]
    assert body["focuses"] == [
        {
            "focus_statement": "Review new Radar intake",
            "reason": "Two new opportunities appeared in the latest run.",
            "source_object": "pipeline-run:9",
            "attention_horizon": "today",
            "next_action": "Open Radar and compare the newest opportunity signals.",
            "resolution_state": "active",
        }
    ]
    assert "T" in body["generated_at"]
    summary, opportunities, most_recent_run = fake.calls[0]
    assert summary.total_opportunities == 1
    assert opportunities.limit == 3
    assert most_recent_run.id == run_id


def test_focuses_endpoint_allows_empty_focuses(client, app):
    class EmptyFocusService:
        def list_active_focuses(self, *, summary, opportunities, most_recent_run):
            return []

    app.dependency_overrides[get_focus_service] = lambda: EmptyFocusService()

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    assert resp.json()["focuses"] == []


def test_focuses_endpoint_is_get_only_and_uses_existing_read_boundaries():
    assert '@router.get("/focuses"' in ATLAS_API_PY
    assert "atlas_service.get_summary()" in ATLAS_API_PY
    assert "atlas_service.list_opportunities(limit=3)" in ATLAS_API_PY
    assert "pipeline_service.list_recent_runs(limit=1)" in ATLAS_API_PY
    assert "focus_service.list_active_focuses" in ATLAS_API_PY
    assert "get_focus_service" in DEPS_PY
    assert "FocusService()" in DEPS_PY
    for verb in ['@router.post(', '@router.put(', '@router.patch(', '@router.delete(']:
        assert verb not in ATLAS_API_PY


def test_frontend_client_and_types_define_focus_boundary():
    assert "export function getFocuses" in CLIENT_TS
    assert '"/focuses"' in CLIENT_TS
    assert "AtlasFocus" in TYPES_TS
    assert "AtlasFocusListResponse" in TYPES_TS
    for field in [
        "focus_statement",
        "reason",
        "source_object",
        "attention_horizon",
        "next_action",
        "resolution_state",
    ]:
        assert field in TYPES_TS


def test_command_center_renders_focus_list_and_states():
    assert "getFocuses" in COMMAND_CENTER_TSX
    assert "focusState" in COMMAND_CENTER_TSX
    assert "Atlas Focus" in COMMAND_CENTER_TSX
    for field in [
        "focus.focus_statement",
        "focus.reason",
        "focus.source_object",
        "focus.attention_horizon",
        "focus.next_action",
        "focus.resolution_state",
    ]:
        assert field in COMMAND_CENTER_TSX
    assert "Loading Atlas Focus" in COMMAND_CENTER_TSX
    assert "Unable to load Atlas Focus" in COMMAND_CENTER_TSX
    assert "No active Focus objects right now" in COMMAND_CENTER_TSX
    assert ".atlas-cc-focus-card" in COMMAND_CENTER_CSS


def test_command_center_has_no_focus_mutation_controls_or_task_management():
    prohibited_terms = [
        "Complete Focus",
        "Defer Focus",
        "Dismiss Focus",
        "Archive Focus",
        "delete",
        "notification",
        "reminder",
        "calendar",
        "task",
        "onClick",
        "<button",
        "<form",
        "select_job",
        "reject_job",
        "mark_applied",
    ]
    combined = COMMAND_CENTER_TSX + COMMAND_CENTER_CSS
    for term in prohibited_terms:
        assert term not in combined, f"prohibited Focus behavior found: {term}"


def test_focus_package_does_not_add_schema_or_persistence():
    assert "focus" not in SCHEMA_SQL.lower()


def test_no_workspace_file_calls_fetch_directly():
    offenders = []
    for path in (FRONTEND_SRC / "workspaces").glob("*.tsx"):
        source = path.read_text(encoding="utf-8")
        if "fetch(" in source:
            offenders.append(path.name)
    assert offenders == []


def test_unrelated_closed_surfaces_untouched_by_focus_work():
    for source in [RADAR_TSX, PIPELINE_TSX, ASK_ATLAS_TSX, OPPORTUNITY_DETAIL_SURFACE_TSX]:
        assert "getFocuses" not in source
        assert "AtlasFocus" not in source
        assert "FocusService" not in source


def test_dashboard_routes_remain_unaffected_by_package_9(client):
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
