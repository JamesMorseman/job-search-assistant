"""Source Health read service — Package 8.

Queries the `source_health` table joined to `firms` for circuit state. All
methods are read-only. No method writes to any table.

Three concerns:
  1. Per-source run summary — last run per (source, firm_id).
  2. Firm circuit-state join — adds circuit_state / quarantine_until /
     consecutive_failures / last_successful_fetch / ats_tier from `firms`
     for firm-backed sources.
  3. Global health summary — aggregate counts across all sources.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel

from job_search.db import get_db


class SourceRunSummary(BaseModel):
    source: str
    firm_id: str | None
    firm_name: str | None
    run_at: str | None
    status: str | None
    records_fetched: int | None
    error_class: str | None
    error_detail: str | None
    # From firms join (None for global sources)
    circuit_state: str | None
    quarantine_until: str | None
    consecutive_failures: int | None
    last_successful_fetch: str | None
    ats_tier: str | None
    # Derived
    is_quarantined: bool
    quarantine_active: bool
    severity: str


class GlobalHealthSummary(BaseModel):
    total_sources: int
    open_circuit_count: int
    recent_error_count: int
    last_successful_run: str | None
    all_healthy: bool


class SourceHealthReport(BaseModel):
    sources: list[SourceRunSummary]
    global_summary: GlobalHealthSummary


def _is_quarantine_active(quarantine_until: str | None, circuit_state: str | None) -> bool:
    if circuit_state != "open":
        return False
    if quarantine_until is None:
        return True
    try:
        until = datetime.fromisoformat(quarantine_until)
        if until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
        return until > datetime.now(tz=timezone.utc)
    except ValueError:
        return True


def _source_severity(
    status: str | None,
    *,
    quarantine_active: bool,
    consecutive_failures: int | None,
) -> str:
    if quarantine_active or status in {"error", "quarantined"}:
        return "critical"
    if status == "empty" or (consecutive_failures or 0) > 0:
        return "warning"
    if status == "ok":
        return "healthy"
    return "unknown"


class SourceHealthService:
    """Read-only source health queries backed by SQLite."""

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path

    def _db(self):
        return get_db(self._db_path)

    def get_report(self, status: str | None = None) -> SourceHealthReport:
        """Build the source health report.

        `status` is an optional equality filter on each source's latest run
        status (diagnostic filtering for the Source Health dashboard
        screen). The global summary is always computed over the full,
        unfiltered data — filtering only narrows the per-source table, it
        must not change the health totals shown in the global bar.
        """
        sources = self._get_source_run_summaries()
        global_summary = self._get_global_summary()
        if status is not None:
            sources = [s for s in sources if s.status == status]
        return SourceHealthReport(sources=sources, global_summary=global_summary)

    def list_distinct_statuses(self) -> list[str]:
        """Return distinct latest-run status values, sorted, for filter UI."""
        with self._db() as db:
            rows = db.execute(
                "SELECT DISTINCT status FROM source_health WHERE status IS NOT NULL ORDER BY status ASC"
            ).fetchall()
        return [r["status"] for r in rows]

    def _get_source_run_summaries(self) -> list[SourceRunSummary]:
        sql = """
        SELECT
            sh.source,
            sh.firm_id,
            f.name        AS firm_name,
            sh.run_at,
            sh.status,
            sh.records_fetched,
            sh.error_class,
            sh.error_detail,
            f.circuit_state,
            f.quarantine_until,
            f.consecutive_failures,
            f.last_successful_fetch,
            f.ats_tier
        FROM (
            SELECT
                source,
                firm_id,
                MAX(run_at) AS latest_run_at
            FROM source_health
            GROUP BY source, firm_id
        ) latest
        JOIN source_health sh
            ON sh.source = latest.source
            AND (sh.firm_id = latest.firm_id OR (sh.firm_id IS NULL AND latest.firm_id IS NULL))
            AND sh.run_at = latest.latest_run_at
        LEFT JOIN firms f ON f.firm_id = sh.firm_id
        ORDER BY sh.source ASC, f.name ASC
        """
        with self._db() as db:
            rows = db.execute(sql).fetchall()

        result = []
        for row in rows:
            circuit_state = row["circuit_state"]
            quarantine_until = row["quarantine_until"]
            is_quarantined = circuit_state == "open"
            quarantine_active = _is_quarantine_active(quarantine_until, circuit_state)
            result.append(
                SourceRunSummary(
                    source=row["source"],
                    firm_id=row["firm_id"],
                    firm_name=row["firm_name"],
                    run_at=row["run_at"],
                    status=row["status"],
                    records_fetched=row["records_fetched"],
                    error_class=row["error_class"],
                    error_detail=row["error_detail"],
                    circuit_state=circuit_state,
                    quarantine_until=quarantine_until,
                    consecutive_failures=row["consecutive_failures"],
                    last_successful_fetch=row["last_successful_fetch"],
                    ats_tier=row["ats_tier"],
                    is_quarantined=is_quarantined,
                    quarantine_active=quarantine_active,
                    severity=_source_severity(
                        row["status"],
                        quarantine_active=quarantine_active,
                        consecutive_failures=row["consecutive_failures"],
                    ),
                )
            )
        return result

    def _get_global_summary(self) -> GlobalHealthSummary:
        with self._db() as db:
            total_row = db.execute(
                "SELECT COUNT(DISTINCT source || '|' || COALESCE(firm_id, '')) FROM source_health"
            ).fetchone()
            total_sources = total_row[0] if total_row else 0

            open_row = db.execute(
                "SELECT COUNT(*) FROM firms WHERE circuit_state = 'open'"
            ).fetchone()
            open_circuit_count = open_row[0] if open_row else 0

            error_row = db.execute(
                """
                SELECT COUNT(*) FROM source_health
                WHERE status IN ('error', 'quarantined')
                AND run_at >= datetime('now', '-7 days')
                """
            ).fetchone()
            recent_error_count = error_row[0] if error_row else 0

            last_ok_row = db.execute(
                "SELECT MAX(run_at) FROM source_health WHERE status = 'ok'"
            ).fetchone()
            last_successful_run = last_ok_row[0] if last_ok_row else None

        return GlobalHealthSummary(
            total_sources=total_sources,
            open_circuit_count=open_circuit_count,
            recent_error_count=recent_error_count,
            last_successful_run=last_successful_run,
            all_healthy=(open_circuit_count == 0 and recent_error_count == 0),
        )
