"""LLM fit-grading — a cheap pre-triage tier over NEW viable postings.

Runs once per daily pass through the configured LLM batch provider: every new posting that
clears the deterministic floor is graded for fit against James's master profile
and gets a categorical grade + one-sentence rationale. The grade augments the
deterministic `match_score`; it never gates which postings are presented.

This is the only LLM call that runs before James flags "apply". The expensive
per-job resume/cover-letter generation stays gated on selection.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from job_search.config import settings
from job_search.db import get_db
from job_search.llm import get_llm_provider, resolve_service_config
from job_search.llm.types import JSONSchemaSpec, LLMBatchStatus, LLMMessage, LLMRequest

logger = logging.getLogger(__name__)

GRADE_RANK = {"Strong": 3, "Good": 2, "Marginal": 1, "Pass": 0}
BATCH_TERMINAL_STATUSES = {"completed", "failed", "expired", "cancelled"}

GRADE_SYSTEM = """You are grading the FIT between a civil-engineering candidate and a SINGLE job posting.
You are NOT writing a resume or cover letter. Output only a categorical grade + one-sentence rationale.

RUBRIC (pick the best category the evidence supports):
- Strong  : Clearly meets core requirements; discipline and seniority align well.
- Good    : Meets most requirements; minor gaps the candidate can credibly cover.
- Marginal: Plausible but with real gaps (discipline mismatch or seniority/experience gap).
- Pass    : Poor fit; a hard requirement the candidate cannot meet (e.g. PE license, years of experience).

RULES (non-negotiable):
1. Cite ONLY facts present in the job description and the candidate profile below. No fabrication.
2. The rationale is ONE sentence naming the deciding factor(s).
3. fit_score is an integer 1-5 (5 = strongest), consistent with the grade bucket.
4. Return ONLY the structured object."""

GRADE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["grade", "fit_score", "rationale"],
    "properties": {
        "grade": {"type": "string", "enum": ["Strong", "Good", "Marginal", "Pass"]},
        "fit_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "rationale": {"type": "string", "maxLength": 280},
    },
}

GRADE_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "fit_grade",
        "strict": True,
        "schema": GRADE_SCHEMA,
    },
}


@dataclass
class GradeResult:
    canonical_job_id: str
    grade: str
    fit_score: int | None
    rationale: str
    model_used: str


class FitGrader:
    def __init__(self, llm_provider=None):
        self.config = resolve_service_config("grading")
        self.llm = llm_provider or get_llm_provider("grading")
        self.model = self.config.model
        self._profile: dict | None = None
        self._system_cache: str | None = None
        self._batch_files: dict[str, str] = {}

    # ── profile (mirrors DocumentGenerator.load_profile) ─────────────────────
    def load_profile(self, path: str | None = None) -> None:
        profile_path = path or settings.PROFILE_PATH
        if not Path(profile_path).exists():
            raise FileNotFoundError(
                f"Profile not found at {profile_path}. "
                f"Copy the template:  cp {settings.PROFILE_TEMPLATE_PATH} {profile_path}  "
                f"and fill in James's real data before running."
            )
        with open(profile_path) as f:
            self._profile = yaml.safe_load(f)
        self._system_cache = None
        logger.info("Profile loaded from %s", profile_path)

    # ── selection ────────────────────────────────────────────────────────────
    def select_viable(self, db, max_jobs: int | None = None) -> list:
        """NEW postings above the floor, not yet graded, skipping deterministically
        dead ones (`long_shot` = hard PE / high-years requirement)."""
        limit = max_jobs or settings.GRADING_MAX_JOBS
        return db.execute(
            """
            SELECT * FROM jobs
            WHERE app_state = 'discovered'
              AND match_score >= ?
              AND llm_graded_at IS NULL
              AND COALESCE(stretch_category, '') != 'long_shot'
              AND COALESCE(ko_pe_required, 0) != 1
              AND (ko_min_years IS NULL OR ko_min_years <= 2)
              AND (
                ko_clearance IS NULL
                OR lower(trim(ko_clearance)) IN (
                  '', 'none', 'n/a', 'na', 'not required',
                  'no clearance', 'no clearance required'
                )
              )
            ORDER BY match_score DESC
            LIMIT ?
            """,
            (settings.GRADING_FLOOR, limit),
        ).fetchall()

    # ── request construction ─────────────────────────────────────────────────
    def _system_prompt(self) -> str:
        if self._system_cache is None:
            if not self._profile:
                self.load_profile()
            self._system_cache = (
                GRADE_SYSTEM
                + "\n\nCANDIDATE PROFILE:\n"
                + json.dumps(self._profile, indent=2)
            )
        return self._system_cache

    def _user_message(self, job: dict) -> str:
        jd = job.get("description_normalized") or job.get("description_raw") or ""
        ko: list[str] = []
        if job.get("ko_pe_required"):
            ko.append("PE required")
        if job.get("ko_eit_required"):
            ko.append("EIT required")
        if job.get("ko_min_years"):
            ko.append(f"min {job['ko_min_years']:.0f}yr exp")
        if job.get("ko_clearance"):
            ko.append(f"clearance: {job['ko_clearance']}")
        if job.get("ko_degree_required"):
            ko.append(f"degree: {job['ko_degree_required']}")
        return (
            f"ROLE: {job.get('title', '')} @ {job.get('company', '')}\n"
            f"LOCATION: {job.get('location_city', '')}, {job.get('location_state', '')}   "
            f"REMOTE: {job.get('remote_flag', '')}\n"
            f"DETERMINISTIC SIGNALS: match_score={job.get('match_score') or 0:.2f}, "
            f"stretch={job.get('stretch_category', '')}, knockouts={'; '.join(ko) or 'none'}\n\n"
            f"JOB DESCRIPTION:\n{jd[:8000]}\n\n"
            f"Grade the fit."
        )

    def _build_request(self, job: dict) -> LLMRequest:
        # custom_id == canonical_job_id so result.custom_id IS the job id.
        return LLMRequest(
            service="grading",
            model=self.model,
            max_tokens=512,
            custom_id=job["canonical_job_id"],
            json_schema=JSONSchemaSpec(name="fit_grade", schema=GRADE_SCHEMA),
            messages=[
                LLMMessage(role="system", content=self._system_prompt()),
                LLMMessage(role="user", content=self._user_message(job)),
            ],
        )

    # ── batch lifecycle ──────────────────────────────────────────────────────
    def submit_batch(self, requests: list[LLMRequest]) -> str:
        return self.llm.submit_json_batch(requests)

    def poll_until_done(self, batch_id: str, timeout_s: int, interval_s: int | None = None) -> LLMBatchStatus:
        interval = interval_s or settings.GRADING_POLL_INTERVAL_S
        deadline = time.monotonic() + timeout_s
        while True:
            batch_status = self.llm.retrieve_batch_status(batch_id)
            status = batch_status.status
            logger.info(
                "grading batch %s status=%s output_file_id=%s error_file_id=%s request_counts=%s",
                batch_id,
                status or "unknown",
                batch_status.output_file_id,
                batch_status.error_file_id,
                batch_status.request_counts,
            )
            if status in BATCH_TERMINAL_STATUSES:
                return batch_status
            if time.monotonic() >= deadline:
                return batch_status
            time.sleep(interval)

    def fetch_results(self, batch_id: str) -> list[GradeResult]:
        out: list[GradeResult] = []
        for response in self.llm.fetch_json_batch_results(batch_id):
            try:
                payload = json.loads(response.content)
                out.append(
                    GradeResult(
                        canonical_job_id=response.custom_id or "",
                        grade=payload["grade"],
                        fit_score=payload.get("fit_score"),
                        rationale=payload.get("rationale", ""),
                        model_used=response.model or self.model,
                    )
                )
            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                logger.warning("grade parse failed: %s", exc)
        return out

    def persist(self, db, results: list[GradeResult]) -> int:
        n = 0
        for g in results:
            if g.grade not in GRADE_RANK:
                logger.warning("invalid grade %r for %s; skipping", g.grade, g.canonical_job_id)
                continue
            db.execute(
                "UPDATE jobs SET llm_grade=?, llm_fit_score=?, llm_rationale=?, "
                "llm_graded_at=datetime('now'), llm_model=? WHERE canonical_job_id=?",
                (g.grade, g.fit_score, g.rationale, g.model_used, g.canonical_job_id),
            )
            n += 1
        return n

    # ── batch tracking table ─────────────────────────────────────────────────
    def _record_batch(self, db, batch_id: str, job_count: int) -> None:
        db.execute(
            "INSERT OR REPLACE INTO grading_batches (batch_id, status, job_count) "
            "VALUES (?, 'submitted', ?)",
            (batch_id, job_count),
        )

    def _mark_batch(self, db, batch_id: str, status: str) -> None:
        db.execute(
            "UPDATE grading_batches SET status=?, completed_at=datetime('now') WHERE batch_id=?",
            (status, batch_id),
        )

    def _log_failed_batch(self, batch_status: LLMBatchStatus) -> None:
        logger.warning(
            "grading batch %s ended with status=%s",
            batch_status.batch_id,
            batch_status.status or "unknown",
        )
        fetch_errors = getattr(self.llm, "fetch_batch_error_text", None)
        if callable(fetch_errors):
            fetch_errors(batch_status.batch_id)
        elif batch_status.error_file_id or batch_status.failure_details:
            logger.warning(
                "grading batch %s error_file_id=%s failure_details=%s",
                batch_status.batch_id,
                batch_status.error_file_id,
                batch_status.failure_details,
            )

    def _collect_batch_errors(self, batch_id: str) -> list[dict]:
        fetch_errors = getattr(self.llm, "fetch_batch_errors", None)
        if not callable(fetch_errors):
            return []
        try:
            return fetch_errors(batch_id, limit=5)
        except Exception as exc:  # noqa: BLE001 - diagnostics should not crash grading
            logger.warning("grading batch %s error parsing failed: %s", batch_id, exc)
            return []

    def drain_prior(self, db) -> int:
        """Finish any prior batch that timed out before its grades were retrieved.
        Persists their grades and marks them drained, so a slow batch is never
        re-graded."""
        pending = db.execute(
            "SELECT batch_id FROM grading_batches WHERE status = 'submitted'"
        ).fetchall()
        total = 0
        for r in pending:
            bid = r["batch_id"]
            try:
                batch = self.llm.retrieve_batch_status(bid)
            except Exception as exc:  # noqa: BLE001 — best-effort drain
                logger.warning("drain_prior: retrieve %s failed: %s", bid, exc)
                continue
            if batch.status != "completed":
                logger.info("drain_prior: batch %s status=%s", bid, batch.status or "unknown")
                if batch.status in {"failed", "expired", "cancelled"}:
                    self._log_failed_batch(batch)
                    self._mark_batch(db, bid, batch.status)
                continue
            results = self.fetch_results(bid)
            total += self.persist(db, results)
            self._mark_batch(db, bid, "drained")
        return total

    # ── orchestration ────────────────────────────────────────────────────────
    def run(
        self,
        timeout_s: int | None = None,
        max_jobs: int | None = None,
        dry_run: bool = False,
    ) -> dict:
        stats = {
            "enabled": settings.GRADING_ENABLED,
            "drained": 0,
            "selected": 0,
            "graded": 0,
            "timed_out": False,
            "batch_id": None,
            "batch_status": None,
            "batch_request_counts": None,
            "batch_errors": [],
        }
        if not settings.GRADING_ENABLED:
            return stats

        timeout_s = timeout_s if timeout_s is not None else settings.GRADING_POLL_TIMEOUT_S
        limit = max_jobs or settings.GRADING_MAX_JOBS

        # Phase A — drain any prior batch, then select what's new and viable.
        with get_db() as db:
            stats["drained"] = self.drain_prior(db)
            rows = [dict(r) for r in self.select_viable(db, limit)]
        stats["selected"] = len(rows)
        if not rows:
            return stats

        requests = [self._build_request(r) for r in rows]
        if dry_run:
            stats["dry_run"] = True
            return stats

        # Phase B — submit and poll (no DB held open during the wait).
        batch_id = self.submit_batch(requests)
        stats["batch_id"] = batch_id
        with get_db() as db:
            self._record_batch(db, batch_id, len(rows))

        batch_status = self.poll_until_done(batch_id, timeout_s)
        stats["batch_status"] = batch_status.status
        stats["batch_request_counts"] = batch_status.request_counts

        if batch_status.status != "completed":
            if batch_status.status in BATCH_TERMINAL_STATUSES:
                self._log_failed_batch(batch_status)
                stats["batch_errors"] = self._collect_batch_errors(batch_status.batch_id)
                with get_db() as db:
                    self._mark_batch(db, batch_id, batch_status.status or "failed")
                return stats

            stats["timed_out"] = True  # leave 'submitted' -> drained next run
            logger.warning(
                "grading batch %s status=%s after %ss; report falls back to deterministic score",
                batch_id,
                batch_status.status or "unknown",
                timeout_s,
            )
            return stats

        # Phase C — retrieve, persist, mark drained.
        if batch_status.error_file_id:
            stats["batch_errors"] = self._collect_batch_errors(batch_id)
        results = self.fetch_results(batch_id)
        with get_db() as db:
            stats["graded"] = self.persist(db, results)
            self._mark_batch(db, batch_id, "drained")
        return stats
