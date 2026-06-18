"""Read-only ATLAS Desktop API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from datetime import datetime, timezone

from job_search.dashboard.deps import (
    get_atlas_data_service,
    get_pipeline_service,
    get_recommendation_service,
)
from job_search.services.atlas import (
    AtlasDataService,
    AtlasOpportunityDetail,
    AtlasOpportunityList,
    AtlasSummary,
)
from job_search.services.pipeline import PipelineRun, PipelineService
from job_search.services.recommendations import Recommendation, RecommendationService

router = APIRouter()


class PipelineRunList(BaseModel):
    runs: list[PipelineRun]
    limit: int


class RecommendationList(BaseModel):
    recommendations: list[Recommendation]
    generated_at: str


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


@router.get("/{path:path}", include_in_schema=False)
def atlas_api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="ATLAS API route not found")
