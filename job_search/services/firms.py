"""Firm intelligence read service for dashboard consumption.

Reads the SQLite `firms` table directly — the same table Phase 3's
`job_search.firms.repository.sync_approved_firms()` / `_upsert_firm()`
already populate from `config/firms.yaml`. This module does not
re-implement firm intelligence parsing or sync logic; it only reads the
columns Phase 3 already wrote and reshapes them into dashboard-facing
Pydantic models.

Scope note: only approved firms exist in the `firms` table today. Draft
profiles (`data/firm_drafts/*.yaml`) are filesystem-only — Phase 3 never
synced them to SQLite (see Governance Findings in the Package 6 deliverable
for why a Firm Review Queue backed by this service cannot yet show drafts).
This package is read-only: no firm lookup here can mutate `firms`,
`config/firms.yaml`, or any draft file.
"""

from __future__ import annotations

import json
from sqlite3 import Row

from pydantic import BaseModel

from job_search.db import get_db


def _parse_json_dict(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return value if isinstance(value, dict) else {}


def _parse_json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return value if isinstance(value, list) else []


class FirmSummary(BaseModel):
    """Row sufficient to render a firm list / firm review queue index."""

    firm_id: str
    name: str
    ats_tier: str
    manual_priority: str
    employee_count: str | None
    enr_rank: int | None
    disciplines: list[str]
    known_benefit_count: int
    open_job_count: int


class FirmStatus(BaseModel):
    """ATS reliability / operational health for one firm."""

    firm_id: str
    ats_tier: str
    circuit_state: str
    quarantine_until: str | None
    consecutive_failures: int
    last_successful_fetch: str | None
    last_fingerprinted: str | None
    last_verified: str | None


class FirmMetadata(BaseModel):
    """Profile-level descriptive metadata, independent of status/priority."""

    firm_id: str
    enr_rank: int | None
    employee_count: str | None
    disciplines: list[str]
    aliases: list[str]
    known_benefits: list[str]


class FirmDetail(BaseModel):
    """Full firm detail: identity, ATS config, intelligence, status."""

    firm_id: str
    name: str
    website: str | None
    careers_url: str | None
    aliases: list[str]
    ats_type: str | None
    ats_tier: str
    enr_rank: int | None
    employee_count: str | None
    disciplines: list[str]
    benefits: dict
    trajectory: dict
    manual_priority: str
    reputation_notes: str | None
    last_verified: str | None
    status: FirmStatus


_SUMMARY_COLUMNS = """
    f.firm_id, f.name, f.ats_tier, f.manual_priority, f.employee_count,
    f.enr_rank, f.specialties, f.known_benefits,
    (SELECT COUNT(*) FROM jobs j WHERE j.firm_id = f.firm_id) AS open_job_count
"""

_DETAIL_COLUMNS = """
    firm_id, name, website, careers_url, aliases, ats_type, ats_tier,
    enr_rank, employee_count, specialties, benefits_json, trajectory_json,
    manual_priority, reputation_notes, last_verified, circuit_state,
    quarantine_until, consecutive_failures, last_successful_fetch,
    last_fingerprinted
"""


def _row_to_summary(row: Row) -> FirmSummary:
    return FirmSummary(
        firm_id=row["firm_id"],
        name=row["name"],
        ats_tier=row["ats_tier"] or "unknown",
        manual_priority=row["manual_priority"] or "neutral",
        employee_count=row["employee_count"],
        enr_rank=row["enr_rank"],
        disciplines=_parse_json_list(row["specialties"]),
        known_benefit_count=len(_parse_json_list(row["known_benefits"])),
        open_job_count=row["open_job_count"],
    )


def _row_to_status(row: Row) -> FirmStatus:
    return FirmStatus(
        firm_id=row["firm_id"],
        ats_tier=row["ats_tier"] or "unknown",
        circuit_state=row["circuit_state"] or "closed",
        quarantine_until=row["quarantine_until"],
        consecutive_failures=row["consecutive_failures"] or 0,
        last_successful_fetch=row["last_successful_fetch"],
        last_fingerprinted=row["last_fingerprinted"],
        last_verified=row["last_verified"],
    )


def _row_to_detail(row: Row) -> FirmDetail:
    return FirmDetail(
        firm_id=row["firm_id"],
        name=row["name"],
        website=row["website"],
        careers_url=row["careers_url"],
        aliases=_parse_json_list(row["aliases"]),
        ats_type=row["ats_type"],
        ats_tier=row["ats_tier"] or "unknown",
        enr_rank=row["enr_rank"],
        employee_count=row["employee_count"],
        disciplines=_parse_json_list(row["specialties"]),
        benefits=_parse_json_dict(row["benefits_json"]),
        trajectory=_parse_json_dict(row["trajectory_json"]),
        manual_priority=row["manual_priority"] or "neutral",
        reputation_notes=row["reputation_notes"],
        last_verified=row["last_verified"],
        status=_row_to_status(row),
    )


class FirmsService:
    """Read-only firm intelligence queries backed by SQLite (`firms` table).

    Covers only approved firms — the set Phase 3's `sync_approved_firms()`
    writes to SQLite. No method here reads `data/firm_drafts/`, writes to
    `firms`, or touches `config/firms.yaml`.
    """

    def list_firms(self, manual_priority: str | None = None) -> list[FirmSummary]:
        where = []
        params: list[object] = []
        if manual_priority is not None:
            where.append("f.manual_priority = ?")
            params.append(manual_priority)

        sql = f"SELECT {_SUMMARY_COLUMNS} FROM firms f"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY f.name ASC"

        with get_db() as db:
            rows = db.execute(sql, params).fetchall()
        return [_row_to_summary(row) for row in rows]

    def get_firm_summary(self, firm_id: str) -> FirmSummary | None:
        with get_db() as db:
            row = db.execute(
                f"SELECT {_SUMMARY_COLUMNS} FROM firms f WHERE f.firm_id = ?",
                (firm_id,),
            ).fetchone()
        return _row_to_summary(row) if row is not None else None

    def get_firm(self, firm_id: str) -> FirmDetail | None:
        with get_db() as db:
            row = db.execute(
                f"SELECT {_DETAIL_COLUMNS} FROM firms WHERE firm_id = ?",
                (firm_id,),
            ).fetchone()
        return _row_to_detail(row) if row is not None else None

    def get_firm_status(self, firm_id: str) -> FirmStatus | None:
        with get_db() as db:
            row = db.execute(
                """
                SELECT firm_id, ats_tier, circuit_state, quarantine_until,
                       consecutive_failures, last_successful_fetch,
                       last_fingerprinted, last_verified
                FROM firms WHERE firm_id = ?
                """,
                (firm_id,),
            ).fetchone()
        return _row_to_status(row) if row is not None else None

    def get_firm_priority(self, firm_id: str) -> str | None:
        with get_db() as db:
            row = db.execute(
                "SELECT manual_priority FROM firms WHERE firm_id = ?",
                (firm_id,),
            ).fetchone()
        if row is None:
            return None
        return row["manual_priority"] or "neutral"

    def get_firm_metadata(self, firm_id: str) -> FirmMetadata | None:
        with get_db() as db:
            row = db.execute(
                """
                SELECT firm_id, enr_rank, employee_count, specialties,
                       aliases, known_benefits
                FROM firms WHERE firm_id = ?
                """,
                (firm_id,),
            ).fetchone()
        if row is None:
            return None
        return FirmMetadata(
            firm_id=row["firm_id"],
            enr_rank=row["enr_rank"],
            employee_count=row["employee_count"],
            disciplines=_parse_json_list(row["specialties"]),
            aliases=_parse_json_list(row["aliases"]),
            known_benefits=_parse_json_list(row["known_benefits"]),
        )
