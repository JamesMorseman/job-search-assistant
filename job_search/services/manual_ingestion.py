"""Manual URL/text ingestion for the ATLAS Desktop workflow."""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field

from job_search.db import get_db
from job_search.ingestion.dedup import Deduplicator
from job_search.ingestion.scoring import Scorer
from job_search.models import CanonicalJob


class ManualPostingRequest(BaseModel):
    apply_url: str
    title: str
    company: str
    description: str = Field(min_length=1)
    location_city: str | None = None
    location_state: str | None = None


class ManualPostingResult(BaseModel):
    canonical_job_id: str
    source: str
    source_job_id: str
    created: bool
    repost: bool
    company: str
    title: str
    apply_url: str
    match_score: float | None
    stretch_category: str | None


class ManualIngestionError(Exception):
    """Raised when a manual posting request is not actionable."""


class ManualIngestionService:
    """Create or refresh one manually supplied posting.

    The request stores the exact URL and text supplied by the user, then
    runs the normal deterministic scorer so manual postings behave like
    adapter-sourced postings everywhere else in ATLAS.
    """

    SOURCE = "manual_url"

    def ingest(self, request: ManualPostingRequest) -> ManualPostingResult:
        apply_url = request.apply_url.strip()
        title = request.title.strip()
        company = request.company.strip()
        description = request.description.strip()
        if not apply_url:
            raise ManualIngestionError("Manual posting URL is required.")
        if not title:
            raise ManualIngestionError("Manual posting title is required.")
        if not company:
            raise ManualIngestionError("Manual posting company is required.")
        if not description:
            raise ManualIngestionError("Manual posting description text is required.")

        source_job_id = hashlib.sha256(apply_url.encode("utf-8")).hexdigest()[:32]
        job = CanonicalJob(
            source=self.SOURCE,
            source_job_id=source_job_id,
            company=company,
            title=title,
            location_city=request.location_city,
            location_state=request.location_state,
            description_raw=description,
            description_normalized=description,
            apply_url=apply_url,
        )
        job = Scorer().score(job)

        with get_db() as db:
            is_new, is_repost = Deduplicator(db).upsert(job)
            if not is_new:
                self._refresh_existing_manual_job(db, job)

        return ManualPostingResult(
            canonical_job_id=job.canonical_job_id,
            source=job.source,
            source_job_id=job.source_job_id,
            created=is_new,
            repost=is_repost,
            company=job.company,
            title=job.title,
            apply_url=job.apply_url or apply_url,
            match_score=job.match_score,
            stretch_category=job.stretch_category.value if job.stretch_category else None,
        )

    @staticmethod
    def _refresh_existing_manual_job(db, job: CanonicalJob) -> None:
        d = job.to_db_dict()
        update_fields = [
            "company",
            "title",
            "discipline_tags",
            "location_city",
            "location_state",
            "location_country",
            "remote_flag",
            "description_raw",
            "description_normalized",
            "jd_content_hash",
            "apply_url",
            "ko_work_auth",
            "ko_min_years",
            "ko_eit_required",
            "ko_pe_required",
            "ko_clearance",
            "ko_relocation",
            "ko_degree_required",
            "match_score",
            "stretch_category",
            "benefit_score",
            "career_trajectory_score",
            "benefit_reasons",
            "trajectory_reasons",
        ]
        values = [d[field] for field in update_fields]
        values.append(job.canonical_job_id)
        db.execute(
            f"""
            UPDATE jobs
            SET {", ".join(f"{field} = ?" for field in update_fields)},
                last_seen = datetime('now'),
                updated_at = datetime('now')
            WHERE canonical_job_id = ?
            """,
            values,
        )


def manual_posting_to_metadata(result: ManualPostingResult) -> str:
    return json.dumps(result.model_dump(), sort_keys=True)
