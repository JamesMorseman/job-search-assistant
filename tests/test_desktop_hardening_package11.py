"""ATLAS Desktop Package 11 — Desktop v1 Hardening Pass tests.

Covers the package's authorized scope only: accessibility remediation
(list semantics, accessible link labeling, validation ARIA wiring),
request-cancellation hardening for Ask Atlas, and edge-case coverage
(empty collections, null/missing optional fields, no-pipeline-run
context) for existing read-only API boundaries and stateless services.

No new routes, endpoints, tables, or service modules are introduced or
exercised by this file — see `test_package11_introduces_no_new_surface`.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.llm.types import LLMResponse
from job_search.services.ask_atlas import AskAtlasService
from job_search.services.atlas import (
    AtlasOpportunityList,
    AtlasStageCount,
    AtlasSummary,
)
from job_search.services.recommendations import RecommendationService

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
COMMAND_CENTER_TSX = (FRONTEND_SRC / "workspaces" / "CommandCenter.tsx").read_text(
    encoding="utf-8"
)
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
ASK_ATLAS_TSX = (FRONTEND_SRC / "workspaces" / "AskAtlas.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (
    ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py"
).read_text(encoding="utf-8")


class FakeLLMProvider:
    provider_name = "fake"

    def __init__(self, content: str):
        self.content = content
        self.requests = []

    def generate_json(self, request):
        self.requests.append(request)
        return LLMResponse(content=self.content, model=request.model)


def _empty_summary() -> AtlasSummary:
    return AtlasSummary(total_opportunities=0, stages=[])


def _empty_opportunities() -> AtlasOpportunityList:
    return AtlasOpportunityList(opportunities=[], limit=3)


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


def _insert_minimal_job(db_path: str, job_id: str):
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO jobs (
            canonical_job_id, source, source_job_id, company, title,
            description_raw, description_normalized
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (job_id, "greenhouse", job_id, "Acme Engineering", "Civil Engineer", "raw", "normalized"),
    )
    conn.commit()
    conn.close()


# ── Backend: empty collections ───────────────────────────────────────────


def test_atlas_opportunities_returns_empty_list_when_no_jobs(client):
    resp = client.get("/atlas/api/opportunities")

    assert resp.status_code == 200
    assert resp.json() == {"opportunities": [], "limit": 50}


def test_atlas_summary_returns_zero_counts_when_no_jobs(client):
    resp = client.get("/atlas/api/summary")

    assert resp.status_code == 200
    assert resp.json() == {"total_opportunities": 0, "stages": []}


def test_focus_archive_endpoint_returns_empty_list_when_no_resolutions(client):
    resp = client.get("/atlas/api/focuses/archive")

    assert resp.status_code == 200
    assert resp.json() == {"resolutions": [], "limit": 20}


# ── Backend: null/missing optional fields ───────────────────────────────


def test_atlas_opportunity_detail_handles_null_optional_fields(client, db):
    _insert_minimal_job(db, "job-minimal")

    resp = client.get("/atlas/api/opportunities/job-minimal")

    assert resp.status_code == 200
    body = resp.json()
    assert body["location_city"] is None
    assert body["location_state"] is None
    assert body["apply_url"] is None
    assert body["salary_min"] is None
    assert body["salary_max"] is None
    assert body["llm_grade"] is None
    assert body["llm_fit_score"] is None
    assert body["llm_rationale"] is None
    assert body["ko_work_auth"] is None
    assert body["ko_eit_required"] is None
    assert body["ko_pe_required"] is None
    assert body["discipline_tags"] == []
    assert body["benefit_reasons"] == []
    assert body["trajectory_reasons"] == []
    assert body["benefit_score"] == 0.0
    assert body["career_trajectory_score"] == 0.0


def test_resolve_focus_endpoint_allows_omitted_note(client, db):
    resp = client.post(
        "/atlas/api/focuses/resolutions",
        json={
            "source_object": "pipeline-run:1",
            "focus_statement": "Pipeline run completed with errors",
            "resolution": "completed",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["note"] is None


# ── Backend: stateless services with no-pipeline-run / empty context ────


def test_recommendation_service_handles_no_pipeline_run_and_empty_summary():
    fake = FakeLLMProvider(json.dumps({"recommendations": []}))
    service = RecommendationService(llm_provider=fake)

    recommendations = service.generate(summary=_empty_summary(), most_recent_run=None)

    assert recommendations == []
    prompt = fake.requests[0].messages[1].content
    assert '"most_recent_pipeline_run": null' in prompt
    assert '"total_opportunities": 0' in prompt


def test_ask_atlas_service_handles_no_pipeline_run_and_empty_opportunities():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "observation": "No tracked opportunities yet.",
                "explanation": "ATLAS has no opportunity or pipeline data to inspect.",
                "suggested_action": "Run an ingest pass to populate Radar.",
                "suggested_followups": [],
            }
        )
    )
    service = AskAtlasService(llm_provider=fake)

    result = service.investigate(
        prompt="What changed?",
        summary=_empty_summary(),
        opportunities=_empty_opportunities(),
        most_recent_run=None,
    )

    assert result.observation == "No tracked opportunities yet."
    prompt = fake.requests[0].messages[1].content
    assert '"most_recent_pipeline_run": null' in prompt
    assert '"recent_opportunities": []' in prompt


# ── Frontend: list semantics (Safari/VoiceOver list-style:none gap) ─────


def test_command_center_lists_use_explicit_list_semantics():
    for ul_class, li_class in [
        ("atlas-cc-focus-list", "atlas-cc-focus-card"),
        ("atlas-cc-focus-archive-list", "atlas-cc-focus-archive-card"),
        ("atlas-cc-recommendations", "atlas-cc-recommendation-card"),
    ]:
        assert f'className="{ul_class}" role="list"' in COMMAND_CENTER_TSX
    assert COMMAND_CENTER_TSX.count('role="listitem"') >= 3


def test_pipeline_workspace_list_uses_explicit_list_semantics():
    assert 'className="atlas-pipeline-list" role="list"' in PIPELINE_TSX
    assert 'role="listitem"' in PIPELINE_TSX


def test_ask_atlas_followups_list_uses_explicit_list_semantics():
    assert '<ul role="list">' in ASK_ATLAS_TSX
    assert 'role="listitem"' in ASK_ATLAS_TSX


# ── Frontend: Ask Atlas stale-response / request-cancellation hardening ──


def test_ask_atlas_guards_against_stale_investigation_responses():
    assert "useRef" in ASK_ATLAS_TSX
    assert "RequestIdRef" in ASK_ATLAS_TSX
    assert "investigationRequestIdRef.current !== requestId" in ASK_ATLAS_TSX


# ── Frontend: accessibility wiring ───────────────────────────────────────


def test_ask_atlas_prompt_input_has_validation_aria_wiring():
    assert "aria-invalid={investigationState.status" in ASK_ATLAS_TSX
    assert "aria-describedby={" in ASK_ATLAS_TSX
    assert 'id="ask-atlas-prompt-error"' in ASK_ATLAS_TSX


def test_opportunity_detail_apply_link_has_accessible_label():
    assert "aria-label=\"View original posting (opens in a new tab)\"" in (
        OPPORTUNITY_DETAIL_SURFACE_TSX
    )


# ── Scope confirmation: no new surface introduced ────────────────────────


def test_package11_introduces_no_new_surface():
    post_routes = [
        line.strip()
        for line in ATLAS_API_PY.splitlines()
        if line.strip().startswith("@router.post(")
    ]
    assert post_routes == [
        '@router.post("/focuses/resolutions", response_model=FocusResolutionRecord)'
    ]
    for verb in ["@router.put(", "@router.patch(", "@router.delete("]:
        assert verb not in ATLAS_API_PY

    service_modules = {
        path.name
        for path in (ROOT / "job_search" / "services").glob("*.py")
        if path.name != "__init__.py"
    }
    assert service_modules == {
        "ask_atlas.py",
        "atlas.py",
        "documents.py",
        "firms.py",
        "focus.py",
        "focus_resolution.py",
        "jobs.py",
        "metrics.py",
        "pipeline.py",
        "recommendations.py",
        "source_health.py",
        "tracker.py",
    }
