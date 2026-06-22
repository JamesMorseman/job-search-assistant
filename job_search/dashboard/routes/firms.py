"""Firm Repository screens (W2-FIRM-REPO-UI).

Read-only views over `FirmsService`, the Phase 3 read service that surfaces
the SQLite `firms` table populated by `job_search.firms.repository.
sync_approved_firms()`. This module renders only — it does not write to
`firms`, does not call into `job_search.firms`, and does not import
`job_search.db` directly; the service is the sole data-access boundary
(see `job_search/dashboard/deps.py`).

Scope note: only approved firms exist in the `firms` table today. The
draft Firm Review Queue (unapproved firm profiles) is a separate, not-yet
-built feature — this package only renders a static note that it is not
yet available, with no supporting logic.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from job_search.dashboard.deps import get_firms_service
from job_search.dashboard.render import templates
from job_search.services.firms import FirmsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/firms", response_class=HTMLResponse)
def firms_list(
    request: Request,
    svc: FirmsService = Depends(get_firms_service),
) -> HTMLResponse:
    try:
        firms = svc.list_firms()
    except Exception:
        logger.exception("firms_list: FirmsService.list_firms() failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Firm Repository is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "firms.html",
        {"firms": firms},
    )


@router.get("/firms/{firm_id}", response_class=HTMLResponse)
def firm_detail(
    request: Request,
    firm_id: str,
    svc: FirmsService = Depends(get_firms_service),
) -> HTMLResponse:
    try:
        firm = svc.get_firm(firm_id)
    except Exception:
        logger.exception("firm_detail: FirmsService.get_firm() failed for %r", firm_id)
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Firm Detail is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    if firm is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": f"No firm found with id {firm_id!r}."},
            status_code=404,
        )

    return templates.TemplateResponse(
        request,
        "firm_detail.html",
        {"firm": firm},
    )
