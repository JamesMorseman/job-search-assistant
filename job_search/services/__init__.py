"""Dashboard service layer.

Stable, UI-framework-independent boundaries between SQLite (the operational
source of truth) and future dashboard consumers. Services in this package
read existing tables and reuse existing reporting/tracking logic rather
than re-implementing queries or business rules.

`jobs.py` and `metrics.py` remain fully read-only. `tracker.py` exposes two
state-mutating actions (Phase 4 Package 3b) — `TrackerService.transition_job()`
and `TrackerService.resolve_followup()`. `documents.py` exposes one
state-mutating action (Phase 4 Package 2b) — `DocumentsService.regenerate_documents()`.
All three actions are thin wrappers around existing tracking/generation
infrastructure, not new workflow rules. No route, UI, pipeline-orchestration,
or background-runner code lives here.
"""

from .documents import (
    DocumentRecord,
    DocumentRegenerationError,
    DocumentsService,
    RegenerationResult,
)
from .firms import FirmDetail, FirmMetadata, FirmStatus, FirmSummary, FirmsService
from .jobs import JobDetail, JobListItem, JobsService
from .metrics import MetricsService
from .tracker import FollowUpItem, TrackerRow, TrackerService

__all__ = [
    "JobListItem",
    "JobDetail",
    "JobsService",
    "DocumentRecord",
    "RegenerationResult",
    "DocumentRegenerationError",
    "DocumentsService",
    "TrackerRow",
    "FollowUpItem",
    "TrackerService",
    "MetricsService",
    "FirmSummary",
    "FirmDetail",
    "FirmStatus",
    "FirmMetadata",
    "FirmsService",
]
