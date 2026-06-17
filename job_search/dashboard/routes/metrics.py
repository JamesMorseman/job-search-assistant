"""Metrics screen — read-only (Phase 5 Package 6).

Calls `MetricsService.get_funnel_stats()` exclusively. No mutations.
`by_discipline_state` and `by_location_metro` are FunnelStats fields that
FunnelReporter does not populate; they are not passed to the template.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from job_search.dashboard.deps import get_metrics_service
from job_search.dashboard.render import templates
from job_search.services.metrics import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics", response_class=HTMLResponse)
def metrics(
    request: Request,
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> HTMLResponse:
    try:
        stats = metrics_service.get_funnel_stats()
    except Exception:
        logger.exception("metrics: MetricsService.get_funnel_stats() failed")
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "Metrics is temporarily unavailable. Please try again shortly."},
            status_code=503,
        )

    return templates.TemplateResponse(
        request,
        "metrics.html",
        {
            "total_jobs": stats.total_jobs,
            "by_state": stats.by_state,
            "avg_match_by_state": stats.avg_match_by_state,
            "median_days": stats.median_days,
            "by_stretch": stats.by_stretch,
            "funnel_conversion_rates": stats.funnel_conversion_rates,
            "llm_grade_distribution": stats.llm_grade_distribution,
            "stretch_conversion_rates": stats.stretch_conversion_rates,
            "stretch_response_rates": stats.stretch_response_rates,
            "score_distribution_by_state": stats.score_distribution_by_state,
            "unified_source_data": stats.unified_source_data,
            "pipeline_velocity": stats.pipeline_velocity,
            "llm_grade_outcome_correlation": stats.llm_grade_outcome_correlation,
        },
    )
