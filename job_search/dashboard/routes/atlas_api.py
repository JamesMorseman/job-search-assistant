"""Read-only ATLAS Desktop API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from job_search.dashboard.deps import get_atlas_data_service
from job_search.services.atlas import (
    AtlasDataService,
    AtlasOpportunityDetail,
    AtlasOpportunityList,
    AtlasSummary,
)

router = APIRouter()


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


@router.get("/{path:path}", include_in_schema=False)
def atlas_api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="ATLAS API route not found")
