"""Pipeline Runs screen — read-only (Phase 6 Package 5).

GET /dashboard/pipeline-runs only. No POST routes, no mutations.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from job_search.dashboard.deps import get_pipeline_service
from job_search.dashboard.render import templates
from job_search.services.pipeline import PipelineService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/pipeline-runs", response_class=HTMLResponse)
def pipeline_runs(
    request: Request,
    svc: PipelineService = Depends(get_pipeline_service),
) -> HTMLResponse:
    try:
        runs = svc.list_recent_runs()
    except Exception:
        logger.exception("pipeline_runs: PipelineService.list_recent_runs() failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Pipeline Runs is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "pipeline_runs.html",
        {"runs": runs},
    )
