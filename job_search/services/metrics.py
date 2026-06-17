"""Dashboard metrics — thin wrapper over the existing funnel reporter.

`jsa stats` calls `FunnelReporter().compute()` directly (see
`job_search/cli.py`). This service calls the same method so dashboard
metrics are guaranteed to agree with the CLI — no duplicate metric logic.
"""

from __future__ import annotations

from job_search.reporting.funnel import FunnelReporter, FunnelStats


class MetricsService:
    """Read-only dashboard metrics, identical to `jsa stats`."""

    def __init__(self, reporter: FunnelReporter | None = None):
        self._reporter = reporter or FunnelReporter()

    def get_funnel_stats(self) -> FunnelStats:
        return self._reporter.compute()
