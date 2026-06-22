"""Source Health screen — read-only (Phase 6 Package 8).

GET /dashboard/source-health only. No POST routes, no mutations.

ANNA-P2-DASHBOARD-DIAGNOSTICS adds an optional `status` query-param filter
for diagnostic visibility — passed straight through to
`SourceHealthService.get_report()`, which filters the per-source rows while
leaving the global summary computed over all data. No new write path.
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
    status: str | None = None,
    svc: SourceHealthService = Depends(get_source_health_service),
) -> HTMLResponse:
    try:
        report = svc.get_report(status=status or None)
        statuses = svc.list_distinct_statuses()
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
            "statuses": statuses,
            "selected_status": status or "",
        },
    )
