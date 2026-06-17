"""Dashboard UI foundation (Phase 5 Package 1).

This package is the application shell only: app factory, navigation shell,
and the Review Queue screen as a read-only display shell. It consumes the
Phase 4 service layer (`job_search.services`) exclusively through
`job_search.dashboard.deps` — no route or template in this package queries
SQLite directly.

Non-scope for this package (see `docs/Architecture/phase_4_operational_plan.md`
and the Phase 5 Package 1 task): Application Tracker actions, document
regeneration, Firm Review Queue, Source Health, Pipeline Runs, background
runner, authentication, user management, and any dashboard write operation.
"""

from .app import create_app

__all__ = ["create_app"]
