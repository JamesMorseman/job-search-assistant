"""Read-only ATLAS Desktop data service.

This module owns the local-first DTO boundary for Desktop Package 2. It reads
existing SQLite job state and exposes conservative opportunity models for the
React client without adding workspace behavior or mutation paths.
"""

from __future__ import annotations

from sqlite3 import Row

from pydantic import BaseModel

from job_search.db import get_db
from job_search.services.jobs import _parse_json_list


class AtlasOpportunitySummary(BaseModel):
    job_id: str
    company: str
    title: str
    source: str
    stage: str
    status: str
    location_city: str | None
    location_state: str | None
    remote_flag: str
    posted_date: str | None
    last_seen: str | None
    match_score: float | None
    stretch_category: str | None
    llm_grade: str | None


class AtlasOpportunityDetail(AtlasOpportunitySummary):
    firm_id: str | None
    location_country: str | None
    apply_url: str | None
    salary_min: int | None
    salary_max: int | None
    discipline_tags: list
    description: str | None
    benefit_score: float
    career_trajectory_score: float
    benefit_reasons: list
    trajectory_reasons: list
    llm_fit_score: float | None
    llm_rationale: str | None
    llm_graded_at: str | None
    ko_work_auth: str | None
    ko_min_years: float | None
    ko_eit_required: bool | None
    ko_pe_required: bool | None
    ko_clearance: str | None
    ko_relocation: str | None
    ko_degree_required: str | None


class AtlasStageCount(BaseModel):
    stage: str
    count: int


class AtlasSummary(BaseModel):
    total_opportunities: int
    stages: list[AtlasStageCount]


class AtlasOpportunityList(BaseModel):
    opportunities: list[AtlasOpportunitySummary]
    limit: int


def _row_to_summary(row: Row) -> AtlasOpportunitySummary:
    stage = row["app_state"] or "discovered"
    return AtlasOpportunitySummary(
        job_id=row["canonical_job_id"],
        company=row["company"],
        title=row["title"],
        source=row["source"],
        stage=stage,
        status=stage,
        location_city=row["location_city"],
        location_state=row["location_state"],
        remote_flag=row["remote_flag"] or "unknown",
        posted_date=row["posted_date"],
        last_seen=row["last_seen"],
        match_score=row["match_score"],
        stretch_category=row["stretch_category"],
        llm_grade=row["llm_grade"],
    )


def _row_to_detail(row: Row) -> AtlasOpportunityDetail:
    summary = _row_to_summary(row)
    description = row["description_normalized"] or row["description_raw"]
    return AtlasOpportunityDetail(
        **summary.model_dump(),
        firm_id=row["firm_id"],
        location_country=row["location_country"],
        apply_url=row["apply_url"],
        salary_min=row["salary_min"],
        salary_max=row["salary_max"],
        discipline_tags=_parse_json_list(row["discipline_tags"]),
        description=description,
        benefit_score=row["benefit_score"] or 0.0,
        career_trajectory_score=row["career_trajectory_score"] or 0.0,
        benefit_reasons=_parse_json_list(row["benefit_reasons"]),
        trajectory_reasons=_parse_json_list(row["trajectory_reasons"]),
        llm_fit_score=row["llm_fit_score"],
        llm_rationale=row["llm_rationale"],
        llm_graded_at=row["llm_graded_at"],
        ko_work_auth=row["ko_work_auth"],
        ko_min_years=row["ko_min_years"],
        ko_eit_required=bool(row["ko_eit_required"]) if row["ko_eit_required"] is not None else None,
        ko_pe_required=bool(row["ko_pe_required"]) if row["ko_pe_required"] is not None else None,
        ko_clearance=row["ko_clearance"],
        ko_relocation=row["ko_relocation"],
        ko_degree_required=row["ko_degree_required"],
    )


class AtlasDataService:
    """Read-only opportunity data for ATLAS Desktop API routes."""

    DEFAULT_LIMIT = 50
    MAX_LIMIT = 200

    _ORDER_BY = """
        ORDER BY
            datetime(COALESCE(last_seen, first_seen, created_at)) DESC,
            company COLLATE NOCASE ASC,
            title COLLATE NOCASE ASC,
            canonical_job_id ASC
    """

    def list_opportunities(self, limit: int | None = None) -> AtlasOpportunityList:
        resolved_limit = self._normalize_limit(limit)
        with get_db() as db:
            rows = db.execute(
                f"""
                SELECT canonical_job_id, company, title, source, app_state,
                       location_city, location_state, remote_flag, posted_date,
                       last_seen, match_score, stretch_category, llm_grade,
                       first_seen, created_at
                FROM jobs
                {self._ORDER_BY}
                LIMIT ?
                """,
                (resolved_limit,),
            ).fetchall()
        return AtlasOpportunityList(
            opportunities=[_row_to_summary(row) for row in rows],
            limit=resolved_limit,
        )

    def get_opportunity(self, job_id: str) -> AtlasOpportunityDetail | None:
        with get_db() as db:
            row = db.execute(
                """
                SELECT *
                FROM jobs
                WHERE canonical_job_id = ?
                """,
                (job_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_detail(row)

    def get_summary(self) -> AtlasSummary:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) AS count FROM jobs").fetchone()["count"]
            rows = db.execute(
                """
                SELECT COALESCE(app_state, 'discovered') AS stage, COUNT(*) AS count
                FROM jobs
                GROUP BY COALESCE(app_state, 'discovered')
                ORDER BY stage COLLATE NOCASE ASC
                """
            ).fetchall()
        return AtlasSummary(
            total_opportunities=total,
            stages=[AtlasStageCount(stage=row["stage"], count=row["count"]) for row in rows],
        )

    def _normalize_limit(self, limit: int | None) -> int:
        if limit is None:
            return self.DEFAULT_LIMIT
        return max(1, min(limit, self.MAX_LIMIT))
