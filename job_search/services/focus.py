"""Read-only Atlas Focus derivation service."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from job_search.services.atlas import AtlasOpportunityList, AtlasSummary
from job_search.services.pipeline import PipelineRun

FocusResolutionState = Literal["active", "monitoring"]


class AtlasFocus(BaseModel):
    focus_statement: str
    reason: str
    source_object: str
    attention_horizon: str
    next_action: str
    resolution_state: FocusResolutionState


class FocusService:
    """Derive prioritized awareness objects from existing read-only ATLAS data."""

    MAX_FOCUSES = 3

    def list_active_focuses(
        self,
        *,
        summary: AtlasSummary,
        opportunities: AtlasOpportunityList,
        most_recent_run: PipelineRun | None,
    ) -> list[AtlasFocus]:
        focuses: list[AtlasFocus] = []

        if most_recent_run and most_recent_run.errors_count > 0:
            focuses.append(
                AtlasFocus(
                    focus_statement="Pipeline run completed with errors",
                    reason=(
                        f"Run #{most_recent_run.id} recorded "
                        f"{most_recent_run.errors_count} errors during the latest pipeline pass."
                    ),
                    source_object=f"pipeline-run:{most_recent_run.id}",
                    attention_horizon="now",
                    next_action="Inspect the Pipeline workspace before relying on the latest intake.",
                    resolution_state="active",
                )
            )

        if most_recent_run and most_recent_run.jobs_created > 0:
            focuses.append(
                AtlasFocus(
                    focus_statement="New opportunities entered Radar",
                    reason=(
                        f"The latest pipeline run created {most_recent_run.jobs_created} new "
                        "opportunities that may change today's review priority."
                    ),
                    source_object=f"pipeline-run:{most_recent_run.id}",
                    attention_horizon="today",
                    next_action="Open Radar and compare the newest opportunity signals.",
                    resolution_state="active",
                )
            )

        selected_count = self._stage_count(summary, "selected")
        if selected_count > 0:
            focuses.append(
                AtlasFocus(
                    focus_statement="Selected opportunities deserve review",
                    reason=f"{selected_count} opportunities are currently in the selected stage.",
                    source_object="opportunity-stage:selected",
                    attention_horizon="near-term",
                    next_action="Inspect Pipeline status and supporting opportunity details.",
                    resolution_state="active",
                )
            )

        if not focuses and summary.total_opportunities > 0:
            recent = opportunities.opportunities[0] if opportunities.opportunities else None
            source = f"opportunity:{recent.job_id}" if recent else "opportunity-summary"
            title = f"{recent.company} - {recent.title}" if recent else "tracked opportunity mix"
            focuses.append(
                AtlasFocus(
                    focus_statement="Review current opportunity mix",
                    reason=f"ATLAS is tracking {summary.total_opportunities} opportunities; the latest visible item is {title}.",
                    source_object=source,
                    attention_horizon="today",
                    next_action="Use Command Center and Radar to decide what deserves inspection.",
                    resolution_state="monitoring",
                )
            )

        return focuses[: self.MAX_FOCUSES]

    @staticmethod
    def _stage_count(summary: AtlasSummary, stage_name: str) -> int:
        for stage in summary.stages:
            if stage.stage == stage_name:
                return stage.count
        return 0
