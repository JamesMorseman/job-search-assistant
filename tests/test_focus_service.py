"""ATLAS Desktop Package 9 Focus service tests."""

from __future__ import annotations

import inspect

from job_search.services.atlas import (
    AtlasOpportunityList,
    AtlasOpportunitySummary,
    AtlasStageCount,
    AtlasSummary,
)
from job_search.services.focus import FocusService
import job_search.services.focus as focus_module
from job_search.services.pipeline import PipelineRun


def _summary(*, total: int = 3, selected: int = 1) -> AtlasSummary:
    return AtlasSummary(
        total_opportunities=total,
        stages=[
            AtlasStageCount(stage="discovered", count=max(total - selected, 0)),
            AtlasStageCount(stage="selected", count=selected),
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


def _run(*, errors: int = 0, created: int = 0) -> PipelineRun:
    return PipelineRun(
        id=7,
        run_type="ingest",
        status="complete",
        started_at="2026-06-18T12:00:00",
        completed_at="2026-06-18T12:05:00",
        source="greenhouse",
        trigger="manual",
        jobs_seen=20,
        jobs_created=created,
        jobs_updated=2,
        jobs_presented=1,
        errors_count=errors,
        metadata_json=None,
        notes=None,
    )


def test_focus_service_derives_pipeline_and_stage_focuses():
    service = FocusService()

    focuses = service.list_active_focuses(
        summary=_summary(total=5, selected=2),
        opportunities=_opportunities(),
        most_recent_run=_run(errors=1, created=3),
    )

    assert len(focuses) == 3
    assert focuses[0].focus_statement == "Pipeline run completed with errors"
    assert focuses[0].source_object == "pipeline-run:7"
    assert focuses[0].attention_horizon == "now"
    assert focuses[0].resolution_state == "active"
    assert focuses[1].focus_statement == "New opportunities entered Radar"
    assert focuses[2].focus_statement == "Selected opportunities deserve review"


def test_focus_service_returns_monitoring_focus_for_existing_opportunities_without_stronger_signal():
    service = FocusService()

    focuses = service.list_active_focuses(
        summary=_summary(total=1, selected=0),
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    assert len(focuses) == 1
    assert focuses[0].focus_statement == "Review current opportunity mix"
    assert focuses[0].source_object == "opportunity:job-1"
    assert focuses[0].resolution_state == "monitoring"


def test_focus_service_returns_empty_when_no_context_needs_attention():
    service = FocusService()

    focuses = service.list_active_focuses(
        summary=AtlasSummary(total_opportunities=0, stages=[]),
        opportunities=AtlasOpportunityList(opportunities=[], limit=3),
        most_recent_run=None,
    )

    assert focuses == []


def test_focus_service_is_read_only_and_provider_free():
    source = inspect.getsource(focus_module)

    assert "get_llm_provider" not in source
    assert "LLMRequest" not in source
    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
    for term in [
        "complete_focus",
        "defer_focus",
        "dismiss_focus",
        "archive_focus",
        "notification",
        "calendar",
    ]:
        assert term not in source
def test_stage_counts_returns_zero_for_missing_stage_and_real_count_for_present_stage():
    summary = _summary(total=5, selected=2)

    counts = FocusService._stage_counts(summary, ["selected", "interview", "offer"])

    assert counts == {"selected": 2, "interview": 0, "offer": 0}


def test_stage_count_delegates_to_stage_counts_for_a_single_stage():
    summary = _summary(total=5, selected=2)

    assert FocusService._stage_count(summary, "selected") == 2
    assert FocusService._stage_count(summary, "discovered") == 3
    assert FocusService._stage_count(summary, "offer") == 0


def test_offer_stage_focus_outranks_interview_and_selected_when_all_present():
    service = FocusService()
    summary = AtlasSummary(
        total_opportunities=10,
        stages=[
            AtlasStageCount(stage="selected", count=1),
            AtlasStageCount(stage="interview", count=2),
            AtlasStageCount(stage="offer", count=1),
        ],
    )

    focuses = service.list_active_focuses(
        summary=summary,
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    # Deterministic priority order regardless of the order stages were
    # listed in summary.stages: offer > interview > selected.
    assert [f.focus_statement for f in focuses] == [
        "Outstanding offers need a decision",
        "Interview stage opportunities need preparation",
        "Selected opportunities deserve review",
    ]
    assert all(f.resolution_state == "active" for f in focuses)
    assert focuses[0].source_object == "opportunity-stage:offer"
    assert focuses[1].source_object == "opportunity-stage:interview"
    assert focuses[2].source_object == "opportunity-stage:selected"


def test_offer_stage_focus_is_truncated_by_max_focuses_when_pipeline_signals_present():
    service = FocusService()
    summary = AtlasSummary(
        total_opportunities=10,
        stages=[
            AtlasStageCount(stage="selected", count=1),
            AtlasStageCount(stage="interview", count=2),
            AtlasStageCount(stage="offer", count=1),
        ],
    )

    focuses = service.list_active_focuses(
        summary=summary,
        opportunities=_opportunities(),
        most_recent_run=_run(errors=1, created=3),
    )

    # Pipeline-error and new-opportunity focuses are highest priority and
    # always come first; MAX_FOCUSES=3 caps the list before the offer-stage
    # focus (next in priority order) ever gets appended.
    assert len(focuses) == 3
    assert [f.focus_statement for f in focuses] == [
        "Pipeline run completed with errors",
        "New opportunities entered Radar",
        "Outstanding offers need a decision",
    ]


def test_interview_stage_alone_yields_single_active_focus():
    service = FocusService()
    summary = AtlasSummary(
        total_opportunities=2,
        stages=[AtlasStageCount(stage="interview", count=2)],
    )

    focuses = service.list_active_focuses(
        summary=summary,
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    assert len(focuses) == 1
    assert focuses[0].focus_statement == "Interview stage opportunities need preparation"
    assert focuses[0].reason == "2 opportunities are currently in the interview stage."
    assert focuses[0].source_object == "opportunity-stage:interview"
    assert focuses[0].resolution_state == "active"


def test_fallback_monitoring_focus_still_uses_most_recent_opportunity_as_source():
    """Locks the existing fallback behavior: when no pipeline-run or stage
    signal fires, the monitoring focus's source_object must point at the
    specific most-recent opportunity, not a generic placeholder.
    """
    service = FocusService()

    focuses = service.list_active_focuses(
        summary=_summary(total=1, selected=0),
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    assert len(focuses) == 1
    assert focuses[0].source_object == "opportunity:job-1"
    assert focuses[0].resolution_state == "monitoring"


def test_attention_stages_ordering_is_offer_then_interview_then_selected():
    """Locks the declared priority/tie-break order itself, independent of
    list_active_focuses, so a reordering of _ATTENTION_STAGES is caught
    directly rather than only inferred from end-to-end behavior.
    """
    assert [rule.stage for rule in focus_module._ATTENTION_STAGES] == [
        "offer",
        "interview",
        "selected",
    ]


def test_no_stage_focus_emitted_when_all_attention_stage_counts_are_zero():
    service = FocusService()
    summary = AtlasSummary(
        total_opportunities=3,
        stages=[
            AtlasStageCount(stage="discovered", count=2),
            AtlasStageCount(stage="applied", count=1),
        ],
    )

    focuses = service.list_active_focuses(
        summary=summary,
        opportunities=_opportunities(),
        most_recent_run=None,
    )

    # None of discovered/applied are in _ATTENTION_STAGES, so this falls
    # through to the monitoring fallback rather than an active stage focus.
    assert len(focuses) == 1
    assert focuses[0].resolution_state == "monitoring"
