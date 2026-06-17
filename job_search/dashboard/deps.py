"""Service integration boundary for the dashboard.

Every dashboard route depends on the Phase 4 service layer exclusively
through the functions in this module. No route or template may import
`job_search.db` or construct a service class directly — that boundary is
what keeps SQLite access mediated by the service layer (see
`dashboard_architecture.md`: "Add dashboard-facing services instead of
putting SQL and orchestration directly inside route handlers.").

Tests override these dependencies via FastAPI's `app.dependency_overrides`
to exercise empty-state and service-failure behavior without a real
database.
"""

from __future__ import annotations

from job_search.services.documents import DocumentsService
from job_search.services.firms import FirmsService
from job_search.services.jobs import JobsService
from job_search.services.metrics import MetricsService
from job_search.services.source_health import SourceHealthService
from job_search.services.tracker import TrackerService


def get_jobs_service() -> JobsService:
    return JobsService()


def get_documents_service() -> DocumentsService:
    return DocumentsService()


def get_tracker_service() -> TrackerService:
    return TrackerService()


def get_metrics_service() -> MetricsService:
    return MetricsService()


def get_firms_service() -> FirmsService:
    return FirmsService()


def get_source_health_service() -> SourceHealthService:
    return SourceHealthService()
