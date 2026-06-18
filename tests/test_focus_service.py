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
