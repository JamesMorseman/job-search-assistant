"""Read-only ATLAS Desktop API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from datetime import datetime, timezone

from job_search.dashboard.deps import (
    get_atlas_data_service,
    get_ask_atlas_service,
    get_focus_resolution_service,
    get_focus_service,
    get_pipeline_service,
    get_recommendation_service,
    get_tracker_service,
)
from job_search.services.ask_atlas import AskAtlasInvestigation, AskAtlasService
from job_search.services.atlas import (
    AtlasDataService,
    AtlasOpportunityDetail,
    AtlasOpportunityList,
    AtlasSummary,
)
from job_search.services.focus import AtlasFocus, FocusService
from job_search.services.focus_resolution import (
    FocusResolutionAction,
    FocusResolutionRecord,
    FocusResolutionService,
)
from job_search.services.location_economics_service import (
    build_location_economics_preview_for_opportunity,
)
from job_search.services.pipeline import PipelineRun, PipelineService
from job_search.services.recommendations import Recommendation, RecommendationService
from job_search.services.score_preview_service import build_score_preview_for_opportunity
from job_search.services.tracker import TrackerService
from job_search.reporting.location_economics_preview import LocationEconomicsPreview
from job_search.reporting.score_preview import ScorePreview

router = APIRouter()


class PipelineRunList(BaseModel):
    runs: list[PipelineRun]
    limit: int


class RecommendationList(BaseModel):
    recommendations: list[Recommendation]
    generated_at: str


class AskAtlasInvestigationResponse(BaseModel):
    investigation: AskAtlasInvestigation
    generated_at: str


class FocusList(BaseModel):
    focuses: list[AtlasFocus]
    generated_at: str


class FocusResolutionRequest(BaseModel):
    source_object: str
    focus_statement: str
    resolution: FocusResolutionAction
    note: str | None = None


class FocusArchiveList(BaseModel):
    resolutions: list[FocusResolutionRecord]
    limit: int


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


@router.get("/opportunities", response_model=AtlasOpportunityList)
def list_opportunities(
    limit: int | None = None,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> AtlasOpportunityList:
    return service.list_opportunities(limit=limit)


@router.get("/opportunities/{job_id}", response_model=AtlasOpportunityDetail)
def get_opportunity(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> AtlasOpportunityDetail:
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.get("/opportunities/{job_id}/score-preview", response_model=ScorePreview)
def get_opportunity_score_preview(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> ScorePreview:
    """Read-only explanation of how this opportunity's match score breaks down.

    Built entirely from already-persisted score data (no re-scoring, no DB
    writes) — see job_search.services.score_preview_service for details.
    """
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return build_score_preview_for_opportunity(opportunity)


@router.get(
    "/opportunities/{job_id}/location-economics",
    response_model=LocationEconomicsPreview,
)
def get_opportunity_location_economics(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> LocationEconomicsPreview:
    """Read-only, advisory explanation of this opportunity's location economics.

    Built from a side-effect-free re-lookup against the existing location
    framework (no re-scoring of the persisted match score, no DB writes) —
    see job_search.services.location_economics_service for details.
    """
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return build_location_economics_preview_for_opportunity(opportunity)


@router.get("/summary", response_model=AtlasSummary)
def get_summary(service: AtlasDataService = Depends(get_atlas_data_service)) -> AtlasSummary:
    return service.get_summary()


@router.get("/pipeline/runs", response_model=PipelineRunList)
def list_pipeline_runs(
    limit: int = 20,
    service: PipelineService = Depends(get_pipeline_service),
) -> PipelineRunList:
    return PipelineRunList(runs=service.list_recent_runs(limit=limit), limit=limit)


@router.get("/recommendations", response_model=RecommendationList)
def get_recommendations(
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationList:
    summary = atlas_service.get_summary()
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    return RecommendationList(
        recommendations=recommendation_service.generate(
            summary=summary,
            most_recent_run=most_recent_run,
        ),
        generated_at=_now_iso(),
    )


@router.get("/focuses", response_model=FocusList)
def list_focuses(
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    focus_service: FocusService = Depends(get_focus_service),
    focus_resolution_service: FocusResolutionService = Depends(get_focus_resolution_service),
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> FocusList:
    summary = atlas_service.get_summary()
    opportunities = atlas_service.list_opportunities(limit=3)
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    due_followups = tracker_service.list_due_followups()
    focuses = focus_service.list_active_focuses(
        summary=summary,
        opportunities=opportunities,
        most_recent_run=most_recent_run,
        due_followups=due_followups,
    )
    resolved = focus_resolution_service.resolved_source_objects()
    return FocusList(
        focuses=[f for f in focuses if f.source_object not in resolved],
        generated_at=_now_iso(),
    )


@router.post("/focuses/resolutions", response_model=FocusResolutionRecord)
def resolve_focus(
    payload: FocusResolutionRequest,
    service: FocusResolutionService = Depends(get_focus_resolution_service),
) -> FocusResolutionRecord:
    return service.record_resolution(
        source_object=payload.source_object,
        focus_statement=payload.focus_statement,
        resolution=payload.resolution,
        note=payload.note,
    )


@router.get("/focuses/archive", response_model=FocusArchiveList)
def list_focus_archive(
    limit: int = 20,
    service: FocusResolutionService = Depends(get_focus_resolution_service),
) -> FocusArchiveList:
    return FocusArchiveList(resolutions=service.list_recent_resolutions(limit=limit), limit=limit)


@router.get("/ask-atlas/investigation", response_model=AskAtlasInvestigationResponse)
def investigate_with_ask_atlas(
    prompt: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    ask_atlas_service: AskAtlasService = Depends(get_ask_atlas_service),
) -> AskAtlasInvestigationResponse:
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        raise HTTPException(status_code=400, detail="Investigation prompt is required")
    summary = atlas_service.get_summary()
    opportunities = atlas_service.list_opportunities(limit=3)
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    return AskAtlasInvestigationResponse(
        investigation=ask_atlas_service.investigate(
            prompt=cleaned_prompt,
            summary=summary,
            opportunities=opportunities,
            most_recent_run=most_recent_run,
        ),
        generated_at=_now_iso(),
    )


@router.get("/{path:path}", include_in_schema=False)
def atlas_api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="ATLAS API route not found")
