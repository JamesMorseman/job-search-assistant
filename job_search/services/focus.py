"""Read-only Atlas Focus derivation service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

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


@dataclass(frozen=True)
class _StageFocusRule:
    """A single pure, declarative rule mapping a pipeline stage to a Focus.

    Rules are evaluated in the fixed order they appear in ``_ATTENTION_STAGES``
    below, which is the deterministic priority / tie-break order: when more
    than one actionable stage has a nonzero count, the stage listed earliest
    in this tuple always wins the higher-priority focus slot, independent of
    whatever order ``summary.stages`` happens to be returned in.
    """

    stage: str
    focus_statement: str
    reason_template: str
    attention_horizon: str
    next_action: str
    resolution_state: FocusResolutionState


# Ordered most urgent -> least urgent. This ordering is the single source of
# truth for both stage priority (which stage's Focus appears first when
# several stages are simultaneously actionable) and resolution-state
# classification (which stages are "active" attention items vs merely
# "monitoring"). Adding a new actionable stage means adding one entry here.
_ATTENTION_STAGES: tuple[_StageFocusRule, ...] = (
    _StageFocusRule(
        stage="offer",
        focus_statement="Outstanding offers need a decision",
        reason_template="{count} opportunities are currently in the offer stage.",
        attention_horizon="now",
        next_action="Review offer details and respond before the window closes.",
        resolution_state="active",
    ),
    _StageFocusRule(
        stage="interview",
        focus_statement="Interview stage opportunities need preparation",
        reason_template="{count} opportunities are currently in the interview stage.",
        attention_horizon="near-term",
        next_action="Confirm interview logistics and prepare supporting materials.",
        resolution_state="active",
    ),
    _StageFocusRule(
        stage="selected",
        focus_statement="Selected opportunities deserve review",
        reason_template="{count} opportunities are currently in the selected stage.",
        attention_horizon="near-term",
        next_action="Inspect Pipeline status and supporting opportunity details.",
        resolution_state="active",
    ),
)


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

        stage_counts = self._stage_counts(summary, (rule.stage for rule in _ATTENTION_STAGES))
        for rule in _ATTENTION_STAGES:
            count = stage_counts[rule.stage]
            if count > 0:
                focuses.append(
                    AtlasFocus(
                        focus_statement=rule.focus_statement,
                        reason=rule.reason_template.format(count=count),
                        source_object=f"opportunity-stage:{rule.stage}",
                        attention_horizon=rule.attention_horizon,
                        next_action=rule.next_action,
                        resolution_state=rule.resolution_state,
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
    def _stage_counts(summary: AtlasSummary, stage_names: Iterable[str]) -> dict[str, int]:
        """Pure helper: resolve counts for several stages in a single pass.

        Returns a dict keyed by every name in ``stage_names`` (defaulting to
        ``0`` for any stage absent from ``summary.stages``), so callers never
        need to guard against missing keys. A single pass over
        ``summary.stages`` keeps this O(stages) regardless of how many stage
        names are requested.
        """
        wanted = list(stage_names)
        counts = {name: 0 for name in wanted}
        wanted_set = set(wanted)
        for stage in summary.stages:
            if stage.stage in wanted_set:
                counts[stage.stage] = stage.count
        return counts

    @classmethod
    def _stage_count(cls, summary: AtlasSummary, stage_name: str) -> int:
        return cls._stage_counts(summary, (stage_name,))[stage_name]
