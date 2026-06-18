"""Stateless ATLAS recommendation generation service."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel

from job_search.llm import get_llm_provider, resolve_service_config
from job_search.llm.types import JSONSchemaSpec, LLMMessage, LLMRequest
from job_search.services.atlas import AtlasSummary
from job_search.services.pipeline import PipelineRun

RecommendationPriority = Literal["high", "medium", "low"]
RecommendationSurface = Literal["radar", "pipeline", "opportunity-detail", "command-center"]


class Recommendation(BaseModel):
    text: str
    priority: RecommendationPriority
    action_surface: RecommendationSurface


class RecommendationService:
    """Generate recommendation DTOs from existing ATLAS context.

    The service is intentionally stateless: callers provide all context and no
    recommendations are persisted or cached.
    """

    MAX_RECOMMENDATIONS = 3

    def __init__(self, llm_provider=None):
        self._config = resolve_service_config("generation")
        self._llm = llm_provider or get_llm_provider("generation")

    def generate(
        self,
        *,
        summary: AtlasSummary,
        most_recent_run: PipelineRun | None,
    ) -> list[Recommendation]:
        request = self._build_request(summary=summary, most_recent_run=most_recent_run)
        response = self._llm.generate_json(request)
        return self._parse_response(response.content)

    def _build_request(
        self,
        *,
        summary: AtlasSummary,
        most_recent_run: PipelineRun | None,
    ) -> LLMRequest:
        context = {
            "opportunity_summary": summary.model_dump(),
            "most_recent_pipeline_run": most_recent_run.model_dump() if most_recent_run else None,
        }
        return LLMRequest(
            service="generation",
            model=self._config.model,
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You generate concise ATLAS job-search recommendations. "
                        "Return only grounded, read-only recommendations based on the provided context. "
                        "Do not suggest applying, dismissing, accepting, rejecting, selecting, or mutating records."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=(
                        "Create at most 3 recommendations for the Command Center. "
                        "Each recommendation must include text, priority, and action_surface. "
                        "Valid priorities: high, medium, low. "
                        "Valid action surfaces: radar, pipeline, opportunity-detail, command-center.\n\n"
                        f"Context JSON:\n{json.dumps(context, sort_keys=True)}"
                    ),
                ),
            ],
            max_tokens=700,
            json_schema=JSONSchemaSpec(
                name="atlas_recommendations",
                schema={
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "recommendations": {
                            "type": "array",
                            "maxItems": self.MAX_RECOMMENDATIONS,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "text": {"type": "string"},
                                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "action_surface": {
                                        "type": "string",
                                        "enum": [
                                            "radar",
                                            "pipeline",
                                            "opportunity-detail",
                                            "command-center",
                                        ],
                                    },
                                },
                                "required": ["text", "priority", "action_surface"],
                            },
                        }
                    },
                    "required": ["recommendations"],
                },
            ),
            metadata={"feature": "atlas_recommendations"},
        )

    def _parse_response(self, content: str) -> list[Recommendation]:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return []

        items = payload.get("recommendations", [])
        if not isinstance(items, list):
            return []

        recommendations: list[Recommendation] = []
        for item in items[: self.MAX_RECOMMENDATIONS]:
            parsed = self._parse_item(item)
            if parsed is not None:
                recommendations.append(parsed)
        return recommendations

    @staticmethod
    def _parse_item(item: Any) -> Recommendation | None:
        if not isinstance(item, dict):
            return None
        try:
            return Recommendation.model_validate(item)
        except ValueError:
            return None
