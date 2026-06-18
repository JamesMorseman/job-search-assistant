"""Stateless Ask Atlas investigation response service."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from job_search.llm import get_llm_provider, resolve_service_config
from job_search.llm.types import JSONSchemaSpec, LLMMessage, LLMRequest
from job_search.services.atlas import AtlasOpportunityList, AtlasSummary
from job_search.services.pipeline import PipelineRun


class AskAtlasInvestigation(BaseModel):
    observation: str
    explanation: str
    suggested_action: str
    suggested_followups: list[str]


class AskAtlasService:
    """Generate one read-only investigation response from existing ATLAS context."""

    MAX_FOLLOWUPS = 3

    def __init__(self, llm_provider=None):
        self._config = resolve_service_config("generation")
        self._llm = llm_provider or get_llm_provider("generation")

    def investigate(
        self,
        *,
        prompt: str,
        summary: AtlasSummary,
        opportunities: AtlasOpportunityList,
        most_recent_run: PipelineRun | None,
    ) -> AskAtlasInvestigation:
        request = self._build_request(
            prompt=prompt,
            summary=summary,
            opportunities=opportunities,
            most_recent_run=most_recent_run,
        )
        response = self._llm.generate_json(request)
        parsed = self._parse_response(response.content)
        if parsed is not None:
            return parsed
        return AskAtlasInvestigation(
            observation="Atlas could not produce a structured observation from the current context.",
            explanation="The investigation response was unavailable or malformed. Existing ATLAS data remains unchanged.",
            suggested_action="Review Radar, Pipeline, or Command Center for the current source data.",
            suggested_followups=[],
        )

    def _build_request(
        self,
        *,
        prompt: str,
        summary: AtlasSummary,
        opportunities: AtlasOpportunityList,
        most_recent_run: PipelineRun | None,
    ) -> LLMRequest:
        context = {
            "investigation_prompt": prompt,
            "opportunity_summary": summary.model_dump(),
            "recent_opportunities": [item.model_dump() for item in opportunities.opportunities],
            "most_recent_pipeline_run": most_recent_run.model_dump() if most_recent_run else None,
        }
        return LLMRequest(
            service="generation",
            model=self._config.model,
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are Ask Atlas, an investigation surface for a local job-search workspace. "
                        "Respond with structured investigation notes only. Do not behave like a generic assistant. "
                        "Do not suggest or perform mutations such as applying, selecting, rejecting, transitioning, "
                        "resolving, regenerating, or changing stored data."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=(
                        "Investigate the user's question using only the supplied ATLAS context. "
                        "Return observation, explanation, suggested_action, and up to 3 suggested_followups. "
                        "Keep the response grounded in the visible local data.\n\n"
                        f"Context JSON:\n{json.dumps(context, sort_keys=True)}"
                    ),
                ),
            ],
            max_tokens=900,
            json_schema=JSONSchemaSpec(
                name="ask_atlas_investigation",
                schema={
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "observation": {"type": "string"},
                        "explanation": {"type": "string"},
                        "suggested_action": {"type": "string"},
                        "suggested_followups": {
                            "type": "array",
                            "maxItems": self.MAX_FOLLOWUPS,
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "observation",
                        "explanation",
                        "suggested_action",
                        "suggested_followups",
                    ],
                },
            ),
            metadata={"feature": "ask_atlas_investigation"},
        )

    def _parse_response(self, content: str) -> AskAtlasInvestigation | None:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None

        followups = payload.get("suggested_followups", [])
        if isinstance(followups, list):
            payload = {**payload, "suggested_followups": followups[: self.MAX_FOLLOWUPS]}

        try:
            return AskAtlasInvestigation.model_validate(payload)
        except ValueError:
            return None
