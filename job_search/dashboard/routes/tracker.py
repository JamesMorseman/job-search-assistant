"""Application Tracker screen — read and actions (Phase 5 Packages 5a/5b).

Read paths call `TrackerService.list_tracker_rows()` and
`TrackerService.list_due_followups()` only. Mutation paths call
`TrackerService.transition_job()` and `TrackerService.resolve_followup()`
exclusively — no alternate transition or resolution path exists in this
module.

`VALID_TRANSITIONS` is imported from the state machine for rendering
per-row dropdown options only, not for enforcing transition rules.
Enforcement remains inside `advance_state()` via `TrackerService`.
"""

from __future__ import annotations

import logging
import urllib.parse

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from job_search.dashboard.deps import get_tracker_service
from job_search.dashboard.render import templates
from job_search.services.tracker import TrackerService
from job_search.tracking.state_machine import VALID_TRANSITIONS

logger = logging.getLogger(__name__)

router = APIRouter()

_TRACKER_URL = "/dashboard/tracker"


def _redirect_to_tracker(error: str | None = None) -> RedirectResponse:
    url = _TRACKER_URL
    if error:
        url = f"{url}?error={urllib.parse.quote(error)}"
    return RedirectResponse(url=url, status_code=303)


@router.get("/tracker", response_class=HTMLResponse)
def application_tracker(
    request: Request,
    error: str | None = None,
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> HTMLResponse:
    try:
        rows = tracker_service.list_tracker_rows()
        followups = tracker_service.list_due_followups()
    except Exception:
        logger.exception("application_tracker: TrackerService failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Application Tracker is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "tracker.html",
        {
            "rows": rows,
            "followups": followups,
            "valid_transitions": VALID_TRANSITIONS,
            "error": error,
        },
    )


@router.post("/tracker/{canonical_job_id}/transition")
def transition_job_action(
    canonical_job_id: str,
    to_state: str = Form(...),
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> RedirectResponse:
    try:
        ok = tracker_service.transition_job(
            canonical_job_id,
            to_state,
            note=f"Transitioned to {to_state} from Application Tracker",
        )
    except Exception:
        logger.exception(
            "transition_job_action: TrackerService.transition_job() failed for %r → %r",
            canonical_job_id,
            to_state,
        )
        return _redirect_to_tracker("State transition failed. Please try again shortly.")

    if not ok:
        return _redirect_to_tracker(
            f"Could not transition job {canonical_job_id!r} to {to_state!r}. "
            "The transition may not be valid from its current state."
        )

    return _redirect_to_tracker()


@router.post("/tracker/followups/{followup_id}/resolve")
def resolve_followup_action(
    followup_id: int,
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> RedirectResponse:
    try:
        tracker_service.resolve_followup(followup_id)
    except Exception:
        logger.exception(
            "resolve_followup_action: TrackerService.resolve_followup() failed for followup_id=%r",
            followup_id,
        )
        return _redirect_to_tracker("Follow-up resolution failed. Please try again shortly.")

    return _redirect_to_tracker()
