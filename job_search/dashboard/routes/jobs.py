"""Review Queue and Job Detail screens.

Review Queue display reads go through `JobsService.list_jobs()`. Job Detail
is read-only — calls `JobsService.get_job_detail()` only, no write path.
The two action routes (`select_job`, `reject_job`) call
`TrackerService.transition_job()`, the sole authorized path for
`jobs.app_state` changes from any dashboard route. No route in this module
writes to `jobs.app_state` or `app_transitions` directly.

ANNA-P2-DASHBOARD-DIAGNOSTICS adds an optional `q` query-param search over
company/title for the Review Queue, passed through to
`JobsService.list_jobs(q=...)` as a keyword argument so existing callers
(and test stubs) that omit it are unaffected.
"""

from __future__ import annotations

import logging
from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from job_search.dashboard.deps import get_jobs_service, get_tracker_service
from job_search.dashboard.render import templates
from job_search.services.jobs import JobsService
from job_search.services.tracker import TrackerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/review-queue", response_class=HTMLResponse)
def review_queue(
    request: Request,
    error: str | None = None,
    q: str | None = None,
    jobs_service: JobsService = Depends(get_jobs_service),
) -> HTMLResponse:
    try:
        jobs = jobs_service.list_jobs(app_state="presented", q=q or None)
    except Exception:
        logger.exception("review_queue: JobsService.list_jobs() failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Review Queue is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "review_queue.html",
        {"jobs": jobs, "error": error, "q": q or ""},
    )


@router.get("/jobs/{canonical_job_id}", response_class=HTMLResponse)
def job_detail(
    request: Request,
    canonical_job_id: str,
    jobs_service: JobsService = Depends(get_jobs_service),
) -> HTMLResponse:
    try:
        detail = jobs_service.get_job_detail(canonical_job_id)
    except Exception:
        logger.exception("job_detail: JobsService.get_job_detail() failed for %r", canonical_job_id)
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Job Detail is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    if detail is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": f"No job found with id {canonical_job_id!r}."},
            status_code=404,
        )

    return templates.TemplateResponse(
        request,
        "job_detail.html",
        {"job": detail},
    )


def _redirect_to_review_queue(error: str | None = None) -> RedirectResponse:
    url = "/dashboard/review-queue"
    if error:
        url += f"?error={quote(error)}"
    return RedirectResponse(url=url, status_code=303)


@router.post("/review-queue/{canonical_job_id}/select")
def select_job(
    canonical_job_id: str,
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> RedirectResponse:
    try:
        ok = tracker_service.transition_job(canonical_job_id, "selected", note="Selected from dashboard Review Queue")
    except Exception:
        logger.exception("select_job: TrackerService.transition_job() failed for %r", canonical_job_id)
        return _redirect_to_review_queue(error="Select action is temporarily unavailable. Please try again shortly.")

    if not ok:
        return _redirect_to_review_queue(error="That job could not be selected (invalid state transition).")
    return _redirect_to_review_queue()


@router.post("/review-queue/{canonical_job_id}/reject")
def reject_job(
    canonical_job_id: str,
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> RedirectResponse:
    try:
        ok = tracker_service.transition_job(canonical_job_id, "rejected", note="Rejected from dashboard Review Queue")
    except Exception:
        logger.exception("reject_job: TrackerService.transition_job() failed for %r", canonical_job_id)
        return _redirect_to_review_queue(error="Reject action is temporarily unavailable. Please try again shortly.")

    if not ok:
        return _redirect_to_review_queue(error="That job could not be rejected (invalid state transition).")
    return _redirect_to_review_queue()
