"""ATLAS Desktop Package 7 recommendation service tests."""

from __future__ import annotations

import inspect
import json

from job_search.llm.types import LLMResponse
from job_search.services.atlas import AtlasStageCount, AtlasSummary
from job_search.services.pipeline import PipelineRun
import job_search.services.recommendations as recommendations_module
from job_search.services.recommendations import RecommendationService


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
        total_opportunities=4,
        stages=[
            AtlasStageCount(stage="discovered", count=2),
            AtlasStageCount(stage="selected", count=2),
        ],
    )


def _run() -> PipelineRun:
    return PipelineRun(
        id=7,
        run_type="ingest",
        status="complete",
        started_at="2026-06-18T12:00:00",
        completed_at="2026-06-18T12:05:00",
        source="greenhouse",
        trigger="manual",
        jobs_seen=20,
        jobs_created=4,
        jobs_updated=3,
        jobs_presented=2,
        errors_count=0,
        metadata_json=None,
        notes=None,
    )


def test_recommendation_service_builds_provider_neutral_structured_request():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "recommendations": [
                    {
                        "text": "Review the newly discovered opportunities in Radar.",
                        "priority": "high",
                        "action_surface": "radar",
                    }
                ]
            }
        )
    )
    service = RecommendationService(llm_provider=fake)

    recommendations = service.generate(summary=_summary(), most_recent_run=_run())

    assert len(recommendations) == 1
    request = fake.requests[0]
    assert request.service == "generation"
    assert request.json_schema is not None
    assert request.json_schema.name == "atlas_recommendations"
    assert request.metadata == {"feature": "atlas_recommendations"}
    prompt = request.messages[1].content
    assert '"total_opportunities": 4' in prompt
    assert '"jobs_seen": 20' in prompt


def test_recommendation_service_parses_at_most_three_structured_recommendations():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "recommendations": [
                    {"text": "A", "priority": "high", "action_surface": "radar"},
                    {"text": "B", "priority": "medium", "action_surface": "pipeline"},
                    {"text": "C", "priority": "low", "action_surface": "opportunity-detail"},
                    {"text": "D", "priority": "low", "action_surface": "command-center"},
                ]
            }
        )
    )
    service = RecommendationService(llm_provider=fake)

    recommendations = service.generate(summary=_summary(), most_recent_run=None)

    assert [item.text for item in recommendations] == ["A", "B", "C"]
    assert recommendations[0].priority == "high"
    assert recommendations[2].action_surface == "opportunity-detail"


def test_recommendation_service_skips_invalid_llm_items():
    fake = FakeLLMProvider(
        json.dumps(
            {
                "recommendations": [
                    {"text": "Valid", "priority": "medium", "action_surface": "pipeline"},
                    {"text": "Invalid", "priority": "urgent", "action_surface": "pipeline"},
                    {"text": "Invalid surface", "priority": "low", "action_surface": "apply"},
                ]
            }
        )
    )
    service = RecommendationService(llm_provider=fake)

    recommendations = service.generate(summary=_summary(), most_recent_run=None)

    assert len(recommendations) == 1
    assert recommendations[0].text == "Valid"


def test_recommendation_service_uses_llm_provider_abstraction_without_sql_or_hardcoded_client():
    source = inspect.getsource(recommendations_module)

    assert "get_llm_provider" in source
    assert "LLMRequest" in source
    assert "OpenAIProvider" not in source
    assert "from openai" not in source
    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
