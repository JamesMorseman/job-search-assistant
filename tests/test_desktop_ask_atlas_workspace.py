"""ATLAS Desktop Package 8 Ask Atlas investigation surface tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_ask_atlas_service
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.ask_atlas import AskAtlasInvestigation
from job_search.services.pipeline import PipelineService

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
APP_TSX = (FRONTEND_SRC / "App.tsx").read_text(encoding="utf-8")
ASK_ATLAS_TSX = (FRONTEND_SRC / "workspaces" / "AskAtlas.tsx").read_text(encoding="utf-8")
ASK_ATLAS_CSS = (FRONTEND_SRC / "workspaces" / "askAtlas.css").read_text(encoding="utf-8")
CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
TYPES_TS = (FRONTEND_SRC / "api" / "types.ts").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
COMMAND_CENTER_TSX = (
    FRONTEND_SRC / "workspaces" / "CommandCenter.tsx"
).read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py").read_text(
    encoding="utf-8"
)
DEPS_PY = (ROOT / "job_search" / "dashboard" / "deps.py").read_text(encoding="utf-8")
SCHEMA_SQL = (ROOT / "job_search" / "db" / "schema.sql").read_text(encoding="utf-8")


class FakeAskAtlasService:
    def __init__(self):
        self.calls = []

    def investigate(self, *, prompt, summary, opportunities, most_recent_run):
        self.calls.append((prompt, summary, opportunities, most_recent_run))
        return AskAtlasInvestigation(
            observation="Two opportunity stages are active.",
            explanation="The latest run completed without errors.",
            suggested_action="Inspect Radar for the newest qualified role.",
            suggested_followups=["Which source changed most?"],
        )


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


def test_ask_atlas_endpoint_returns_structured_investigation(client, app, db):
    fake = FakeAskAtlasService()
    app.dependency_overrides[get_ask_atlas_service] = lambda: fake
    _insert_job(db, "job-1", app_state="discovered")
    pipeline = PipelineService(db_path=db)
    run_id = pipeline.start_run("ingest", trigger="manual")
    pipeline.complete_run(run_id)

    resp = client.get("/atlas/api/ask-atlas/investigation?prompt=What%20changed%3F")

    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["investigation", "generated_at"]
    assert body["investigation"] == {
        "observation": "Two opportunity stages are active.",
        "explanation": "The latest run completed without errors.",
        "suggested_action": "Inspect Radar for the newest qualified role.",
        "suggested_followups": ["Which source changed most?"],
    }
    assert "T" in body["generated_at"]
    prompt, summary, opportunities, most_recent_run = fake.calls[0]
    assert prompt == "What changed?"
    assert summary.total_opportunities == 1
    assert opportunities.limit == 3
    assert most_recent_run.id == run_id


def test_ask_atlas_endpoint_requires_prompt(client, app):
    app.dependency_overrides[get_ask_atlas_service] = lambda: FakeAskAtlasService()

    resp = client.get("/atlas/api/ask-atlas/investigation?prompt=%20")

    assert resp.status_code == 400
    assert resp.json() == {"detail": "Investigation prompt is required"}


def test_ask_atlas_endpoint_is_get_only_and_uses_existing_context_boundaries():
    assert '@router.get("/ask-atlas/investigation"' in ATLAS_API_PY
    assert "atlas_service.get_summary()" in ATLAS_API_PY
    assert "atlas_service.list_opportunities(limit=3)" in ATLAS_API_PY
    assert "pipeline_service.list_recent_runs(limit=1)" in ATLAS_API_PY
    assert "ask_atlas_service.investigate" in ATLAS_API_PY
    assert "get_ask_atlas_service" in DEPS_PY
    assert "AskAtlasService()" in DEPS_PY
    for verb in ['@router.put(', '@router.patch(', '@router.delete(']:
        assert verb not in ATLAS_API_PY
    # Package 10 authorizes exactly one POST mutation route (Focus
    # resolution); Ask Atlas itself must not gain one.
    assert '@router.post("/ask-atlas' not in ATLAS_API_PY


def test_ask_atlas_route_exists_and_placeholder_is_replaced():
    assert 'path="ask-atlas"' in APP_TSX
    assert "WorkspacePlaceholder" not in ASK_ATLAS_TSX
    assert "Workspace placeholder" not in ASK_ATLAS_TSX
    assert "Investigation Surface" in ASK_ATLAS_TSX


def test_ask_atlas_workspace_uses_client_boundary_and_existing_context_clients():
    assert 'from "../api/client"' in ASK_ATLAS_TSX
    assert "getAskAtlasInvestigation" in ASK_ATLAS_TSX
    assert "getSummary" in ASK_ATLAS_TSX
    assert "getPipelineRuns" in ASK_ATLAS_TSX
    assert "fetch(" not in ASK_ATLAS_TSX
    assert "export function getAskAtlasInvestigation" in CLIENT_TS
    assert "/ask-atlas/investigation" in CLIENT_TS


def test_ask_atlas_types_define_structured_response():
    assert "AskAtlasInvestigation" in TYPES_TS
    assert "AskAtlasInvestigationResponse" in TYPES_TS
    for field in ["observation", "explanation", "suggested_action", "suggested_followups"]:
        assert field in TYPES_TS


def test_ask_atlas_renders_investigation_layout_and_states():
    for text in [
        "Attached Context",
        "Current Investigation",
        "Suggested Follow-Ups",
        "Investigation input",
        "Loading opportunity context",
        "Loading pipeline context",
        "Generating investigation",
        "Unable to load opportunity context",
        "Unable to load pipeline context",
        "Unable to generate investigation",
        "No opportunity or pipeline context is available yet",
        "Ask Atlas is ready to inspect attached ATLAS context",
    ]:
        assert text in ASK_ATLAS_TSX
    assert ".atlas-ask-layout" in ASK_ATLAS_CSS


def test_ask_atlas_is_not_chat_surface_and_has_no_prohibited_mutation_behavior():
    prohibited_terms = [
        "chat-bubble",
        "avatar",
        "message thread",
        "conversation history",
        "memory store",
        "Focus Object",
        "Apply now",
        "Move to Applied",
        "select_job",
        "reject_job",
        "mark_applied",
        "transition_job",
        "resolve_followup",
        "regenerate",
    ]
    combined = ASK_ATLAS_TSX + ASK_ATLAS_CSS
    for term in prohibited_terms:
        assert term not in combined, f"prohibited Ask Atlas behavior found: {term}"


def test_no_workspace_file_calls_fetch_directly():
    offenders = []
    for path in (FRONTEND_SRC / "workspaces").glob("*.tsx"):
        source = path.read_text(encoding="utf-8")
        if "fetch(" in source:
            offenders.append(path.name)
    assert offenders == []


def test_unrelated_closed_surfaces_untouched_by_ask_atlas_work():
    assert "getAskAtlasInvestigation" not in RADAR_TSX
    assert "getAskAtlasInvestigation" not in PIPELINE_TSX
    assert "getAskAtlasInvestigation" not in COMMAND_CENTER_TSX
    assert "getAskAtlasInvestigation" not in OPPORTUNITY_DETAIL_SURFACE_TSX


def test_ask_atlas_does_not_add_schema_or_persistence():
    assert "ask_atlas" not in SCHEMA_SQL.lower()
    assert "investigation" not in SCHEMA_SQL.lower()


def test_dashboard_routes_remain_unaffected_by_package_8(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_api_unknown_route_remains_json_404(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")


def test_atlas_ask_atlas_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/ask-atlas")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
