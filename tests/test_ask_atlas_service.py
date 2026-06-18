"""ATLAS Desktop Package 8 Ask Atlas service tests."""

from __future__ import annotations

import inspect
import json

from job_search.llm.types import LLMResponse
from job_search.services.ask_atlas import AskAtlasService
import job_search.services.ask_atlas as ask_atlas_module
from job_search.services.atlas import (
    AtlasOpportunityList,
    AtlasOpportunitySummary,
    AtlasStageCount,
    AtlasSummary,
)
from job_search.services.pipeline import PipelineRun


class FakeLLMProvider:
    provider_name = "fake"

    def __init__(self, content: str):
        self.content = content
        self.requests = []

    def generate_json(self, request):
        self.requests.append(request)
        return LLMResponse(content=self.content, model=request.model)


def _summary() -> AtlasSummary:
    return AtlasSummary(
        total_opportunities=2,
        stages=[
            AtlasStageCount(stage="discovered", count=1),
            AtlasStageCount(stage="selected", count=1),
        ],
    )


def _opportunities() -> AtlasOpportunityList:
    return AtlasOpportunityList(
        opportunities=[
            AtlasOpportunitySummary(
                job_id="job-1",
                company="Acme Engineering",
                title="Civil Engineer",
                source="greenhouse",
                stage="discovered",
                status="discovered",
                location_city=None,
                location_state=None,
                remote_flag="hybrid",
                posted_date=None,
                last_seen="2026-06-18T12:00:00",
                match_score=0.82,
                stretch_category="qualified",
                llm_grade="A",
            )
        ],
        limit=3,
    )


def _run() -> PipelineRun:
    return PipelineRun(
        id=3,
        run_type="ingest",
        status="complete",
        started_at="2026-06-18T12:00:00",
        completed_at="2026-06-18T12:05:00",
        source="greenhouse",
        trigger="manual",
        jobs_seen=12,
        jobs_created=2,
        jobs_updated=1,
        jobs_presented=0,
        errors_count=0,
        metadata_json=None,
        notes=None,
    )


def test_ask_atlas_service_builds_provider_neutral_structured_request():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "observation": "Radar has two active opportunities.",
                "explanation": "The latest pipeline run created two jobs with no errors.",
                "suggested_action": "Inspect Radar and compare the newest qualified roles.",
                "suggested_followups": ["Which stage needs attention?"],
            }
        )
    )
    service = AskAtlasService(llm_provider=fake)

    result = service.investigate(
        prompt="What changed?",
        summary=_summary(),
        opportunities=_opportunities(),
        most_recent_run=_run(),
    )

    assert result.observation == "Radar has two active opportunities."
    request = fake.requests[0]
    assert request.service == "generation"
    assert request.json_schema is not None
    assert request.json_schema.name == "ask_atlas_investigation"
    assert request.metadata == {"feature": "ask_atlas_investigation"}
    prompt = request.messages[1].content
    assert '"investigation_prompt": "What changed?"' in prompt
    assert '"company": "Acme Engineering"' in prompt
    assert '"jobs_seen": 12' in prompt


def test_ask_atlas_service_limits_suggested_followups():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "observation": "A",
                "explanation": "B",
                "suggested_action": "C",
                "suggested_followups": ["one", "two", "three", "four"],
            }
        )
    )
    service = AskAtlasService(llm_provider=fake)

    result = service.investigate(
        prompt="Inspect context",
        summary=_summary(),
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    assert result.suggested_followups == ["one", "two", "three"]


def test_ask_atlas_service_returns_fallback_for_malformed_response():
    fake = FakeLLMProvider("not-json")
    service = AskAtlasService(llm_provider=fake)

    result = service.investigate(
        prompt="Inspect context",
        summary=_summary(),
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    assert "structured observation" in result.observation
    assert result.suggested_followups == []


def test_ask_atlas_service_uses_provider_abstraction_without_sql_or_hardcoded_client():
    source = inspect.getsource(ask_atlas_module)

    assert "get_llm_provider" in source
    assert "LLMRequest" in source
    assert "OpenAIProvider" not in source
    assert "from openai" not in source
    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
