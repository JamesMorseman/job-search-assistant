"""Documents screen — read and regeneration actions.

Renders generated-document history and current/latest resolution for one
job. Read paths use `DocumentsService.list_documents()` and
`DocumentsService.get_current_documents()`. The regeneration action uses
`DocumentsService.regenerate_documents()` exclusively — no alternate
generation path is introduced. `JobsService.get_job_detail()` is used
solely to confirm the job exists and to render the company/title header.
"""

from __future__ import annotations

import logging
import urllib.parse

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from job_search.dashboard.deps import get_documents_service, get_jobs_service
from job_search.dashboard.render import templates
from job_search.services.documents import DocumentsService
from job_search.services.jobs import JobsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/jobs/{canonical_job_id}/documents", response_class=HTMLResponse)
def job_documents(
    request: Request,
    canonical_job_id: str,
    error: str | None = None,
    jobs_service: JobsService = Depends(get_jobs_service),
    documents_service: DocumentsService = Depends(get_documents_service),
) -> HTMLResponse:
    try:
        job = jobs_service.get_job_detail(canonical_job_id)
    except Exception:
        logger.exception("job_documents: JobsService.get_job_detail() failed for %r", canonical_job_id)
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Documents is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    if job is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": f"No job found with id {canonical_job_id!r}."},
            status_code=404,
        )

    try:
        current = documents_service.get_current_documents(canonical_job_id)
        history = documents_service.list_documents(canonical_job_id)
    except Exception:
        logger.exception("job_documents: DocumentsService failed for %r", canonical_job_id)
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Documents is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "documents.html",
        {"job": job, "current": current, "history": history, "error": error},
    )


@router.post("/jobs/{canonical_job_id}/documents/regenerate")
def regenerate_documents_action(
    canonical_job_id: str,
    documents_service: DocumentsService = Depends(get_documents_service),
) -> RedirectResponse:
    try:
        documents_service.regenerate_documents(canonical_job_id)
    except Exception:
        logger.exception(
            "regenerate_documents_action: DocumentsService.regenerate_documents() failed for %r",
            canonical_job_id,
        )
        error = urllib.parse.quote("Document regeneration failed. Please try again shortly.")
        return RedirectResponse(
            url=f"/dashboard/jobs/{canonical_job_id}/documents?error={error}",
            status_code=303,
        )
    return RedirectResponse(
        url=f"/dashboard/jobs/{canonical_job_id}/documents",
        status_code=303,
    )
