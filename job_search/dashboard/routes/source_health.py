"""Source Health screen — read-only (Phase 6 Package 8).

GET /dashboard/source-health only. No POST routes, no mutations.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from job_search.dashboard.deps import get_source_health_service
from job_search.dashboard.render import templates
from job_search.services.source_health import SourceHealthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/source-health", response_class=HTMLResponse)
def source_health(
    request: Request,
    svc: SourceHealthService = Depends(get_source_health_service),
) -> HTMLResponse:
    try:
        report = svc.get_report()
    except Exception:
        logger.exception("source_health: SourceHealthService.get_report() failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Source Health is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "source_health.html",
        {
            "sources": report.sources,
            "global_summary": report.global_summary,
        },
    )
