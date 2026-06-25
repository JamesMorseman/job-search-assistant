"""Job list and job detail read models for dashboard consumption.

Reads SQLite directly (the operational source of truth) and returns
dataclass-free, framework-independent Pydantic models. No write paths,
no CLI shelling, no UI/FastAPI dependency.
"""

from __future__ import annotations

import json
from sqlite3 import Row

from pydantic import BaseModel

from job_search.db import get_db


def _parse_json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return value if isinstance(value, list) else []


class JobListItem(BaseModel):
    """Row sufficient to render a dashboard job list / review queue."""

    canonical_job_id: str
    source: str
    firm_id: str | None
    company: str
    title: str
    location_city: str | None
    location_state: str | None
    remote_flag: str
    posted_date: str | None
    apply_url: str | None
    match_score: float | None
    stretch_category: str | None
    benefit_score: float
    career_trajectory_score: float
    llm_grade: str | None
    app_state: str


class JobDetail(BaseModel):
    """Full job detail: JD, scores, grade, knockouts, and reason summaries."""

    canonical_job_id: str
    source: str
    firm_id: str | None
    company: str
    title: str
    discipline_tags: list
    location_city: str | None
    location_state: str | None
    location_country: str | None
    remote_flag: str
    description_raw: str | None
    apply_url: str | None
    posted_date: str | None
    salary_min: int | None
    salary_max: int | None
    ko_work_auth: str | None
    ko_min_years: float | None
    ko_eit_required: bool | None
    ko_pe_required: bool | None
    ko_clearance: str | None
    ko_relocation: str | None
    ko_degree_required: str | None
    match_score: float | None
    stretch_category: str | None
    benefit_score: float
    career_trajectory_score: float
    benefit_reasons: list
    trajectory_reasons: list
    llm_grade: str | None
    llm_fit_score: float | None
    llm_rationale: str | None
    llm_graded_at: str | None
    app_state: str


def _row_to_list_item(row: Row) -> JobListItem:
    return JobListItem(
        canonical_job_id=row["canonical_job_id"],
        source=row["source"],
        firm_id=row["firm_id"],
        company=row["company"],
        title=row["title"],
        location_city=row["location_city"],
        location_state=row["location_state"],
        remote_flag=row["remote_flag"],
        posted_date=row["posted_date"],
        apply_url=row["apply_url"],
        match_score=row["match_score"],
        stretch_category=row["stretch_category"],
        benefit_score=row["benefit_score"] or 0.0,
        career_trajectory_score=row["career_trajectory_score"] or 0.0,
        llm_grade=row["llm_grade"],
        app_state=row["app_state"],
    )


def _row_to_detail(row: Row) -> JobDetail:
    return JobDetail(
        canonical_job_id=row["canonical_job_id"],
        source=row["source"],
        firm_id=row["firm_id"],
        company=row["company"],
        title=row["title"],
        discipline_tags=_parse_json_list(row["discipline_tags"]),
        location_city=row["location_city"],
        location_state=row["location_state"],
        location_country=row["location_country"],
        remote_flag=row["remote_flag"],
        description_raw=row["description_raw"],
        apply_url=row["apply_url"],
        posted_date=row["posted_date"],
        salary_min=row["salary_min"],
        salary_max=row["salary_max"],
        ko_work_auth=row["ko_work_auth"],
        ko_min_years=row["ko_min_years"],
        ko_eit_required=bool(row["ko_eit_required"]) if row["ko_eit_required"] is not None else None,
        ko_pe_required=bool(row["ko_pe_required"]) if row["ko_pe_required"] is not None else None,
        ko_clearance=row["ko_clearance"],
        ko_relocation=row["ko_relocation"],
        ko_degree_required=row["ko_degree_required"],
        match_score=row["match_score"],
        stretch_category=row["stretch_category"],
        benefit_score=row["benefit_score"] or 0.0,
        career_trajectory_score=row["career_trajectory_score"] or 0.0,
        benefit_reasons=_parse_json_list(row["benefit_reasons"]),
        trajectory_reasons=_parse_json_list(row["trajectory_reasons"]),
        llm_grade=row["llm_grade"],
        llm_fit_score=row["llm_fit_score"],
        llm_rationale=row["llm_rationale"],
        llm_graded_at=row["llm_graded_at"],
        app_state=row["app_state"],
    )


class JobsService:
    """Read-only job list / job detail queries backed by SQLite."""

    def list_jobs(
        self,
        app_state: str | None = None,
        source: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        q: str | None = None,
    ) -> list[JobListItem]:
        """List jobs, optionally filtered by state/source and a free-text
        search term `q`. `q` matches case-insensitively against company or
        title (diagnostic search/filter for the Review Queue dashboard
        screen) — it does not introduce a new query surface beyond simple
        substring matching on existing columns.
        """
        where = []
        params: list[object] = []
        if app_state is not None:
            where.append("app_state = ?")
            params.append(app_state)
        if source is not None:
            where.append("source = ?")
            params.append(source)
        if q:
            where.append("(company LIKE ? OR title LIKE ?)")
            like_term = f"%{q}%"
            params.extend([like_term, like_term])

        sql = """
            SELECT canonical_job_id, source, firm_id, company, title,
                   location_city, location_state, remote_flag, posted_date,
                   apply_url, match_score, stretch_category, benefit_score,
                   career_trajectory_score, llm_grade, app_state
            FROM jobs
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += """
            ORDER BY
              CASE
                WHEN COALESCE(stretch_category, '') = 'long_shot' THEN 1
                WHEN COALESCE(ko_pe_required, 0) = 1 THEN 1
                WHEN ko_min_years IS NOT NULL AND ko_min_years > 2 THEN 1
                WHEN (
                  ko_clearance IS NOT NULL
                  AND lower(trim(ko_clearance)) NOT IN (
                    '', 'none', 'n/a', 'na', 'not required',
                    'no clearance', 'no clearance required'
                  )
                ) THEN 1
                ELSE 0
              END ASC,
              match_score DESC,
              posted_date DESC
        """
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with get_db() as db:
            rows = db.execute(sql, params).fetchall()
        return [_row_to_list_item(row) for row in rows]

    def get_job_detail(self, canonical_job_id: str) -> JobDetail | None:
        with get_db() as db:
            row = db.execute(
                "SELECT * FROM jobs WHERE canonical_job_id = ?",
                (canonical_job_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_detail(row)
