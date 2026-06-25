"""SelectionProcessor — turns James's Sheet edits into doc generation.

Flow:
  1. sync_from_sheet():  Read Sheet status column → advance DB app_state
       "apply"  → presented → selected   (queue for generation)
       "applied"→ selected/presented → applied (start follow-up)
       "skip"   → presented → rejected
  2. generate_for_selected(): For every job in 'selected' without docs,
       call configured LLM provider once for resume + once for cover letter, upload to Drive,
       write doc links back to the Sheet.

Only step (2) consumes LLM tokens. Step (1) is pure DB/Sheet I/O.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from docx import Document as DocxDocument

from job_search.config import settings
from job_search.db import get_db
from job_search.generation import DocumentGenerator
from job_search.generation.audit import (
    AuditSeverity,
    DocumentAuditCheck,
    DocumentAuditFailure,
    DocumentAuditResult,
    audit_generated_documents,
    cover_docx_formatting_metadata,
)
from job_search.llm import resolve_service_config
from job_search.models import AppState, ATSType, CanonicalJob

from .sheets import SheetsLogger

logger = logging.getLogger(__name__)

GENERATED_APPLICATION_MATERIALS_DIR = Path("output/application_materials")


# Sheet status values James writes → (target DB state, note)
SHEET_TRIGGERS: dict[str, tuple[str, str]] = {
    "apply":    (AppState.SELECTED.value,  "James flagged for application"),
    "selected": (AppState.SELECTED.value,  "James flagged for application"),
    "applied":  (AppState.APPLIED.value,   "James marked submitted"),
    "skip":     (AppState.REJECTED.value,  "James passed"),
    "rejected": (AppState.REJECTED.value,  "James passed"),
}


class SelectionProcessor:
    def __init__(self):
        self.sheets = SheetsLogger()
        self._generator: DocumentGenerator | None = None

    # ── Step 1: pull James's Sheet edits into the DB ─────────────────────────

    def sync_from_sheet(self) -> dict:
        """Reconcile Sheet status column → DB app_state."""
        stats = {"synced": 0, "selected": 0, "applied": 0, "rejected": 0, "errors": 0}

        if not settings.TRACKER_SHEET_ID:
            logger.info("TRACKER_SHEET_ID not set — skipping sync")
            return stats

        try:
            rows = self.sheets.read_status_column()
        except Exception as exc:
            logger.error("Failed to read sheet: %s", exc)
            stats["errors"] += 1
            return stats

        with get_db() as db:
            for job_id, sheet_status in rows:
                if not job_id or not sheet_status:
                    continue
                sheet_status_lower = sheet_status.strip().lower()
                if sheet_status_lower not in SHEET_TRIGGERS:
                    continue

                target_state, note = SHEET_TRIGGERS[sheet_status_lower]
                current = db.execute(
                    "SELECT app_state FROM jobs WHERE canonical_job_id = ?", (job_id,)
                ).fetchone()
                if not current:
                    continue

                if current["app_state"] == target_state:
                    continue  # already in sync

                # Advance state if valid
                from job_search.tracking import advance_state
                ok = advance_state(db, job_id, target_state, note=note)
                if ok:
                    stats["synced"] += 1
                    if target_state == AppState.SELECTED.value:
                        stats["selected"] += 1
                    elif target_state == AppState.APPLIED.value:
                        stats["applied"] += 1
                    elif target_state == AppState.REJECTED.value:
                        stats["rejected"] += 1

        logger.info("Sheet sync: %s", stats)
        return stats

    # ── Step 2: generate docs for jobs James selected ────────────────────────

    def generate_for_selected(
        self,
        job_ids: list[str] | None = None,
        force: bool = False,
    ) -> dict:
        """
        Generate resume + cover letter for jobs in 'selected' state without docs.

        Args:
            job_ids: limit to these IDs (default: all selected jobs)
            force: regenerate even if docs already exist
        """
        stats = {"generated": 0, "skipped": 0, "errors": 0, "docs": []}

        with get_db() as db:
            jobs = self._fetch_jobs_needing_docs(db, job_ids, force)
            eligible_jobs = []
            for row in jobs:
                reason = self._generation_block_reason(row)
                if reason:
                    logger.warning("Skipping doc generation for %s: %s", row["canonical_job_id"], reason)
                    stats["skipped"] += 1
                    continue
                eligible_jobs.append(row)
            jobs = eligible_jobs
            logger.info("Generating docs for %d selected jobs", len(jobs))

            if not jobs:
                return stats

            self._lazy_init_generator()
            generation_model = resolve_service_config("generation").model

            for job_row in jobs:
                job_id = job_row["canonical_job_id"]
                try:
                    job_obj = self._hydrate_canonical_job(job_row)
                    result = self._generator.generate(job_obj)

                    resume_url, cover_url, resume_path, cover_path = self._upload_docs(
                        job_row, result, today=date.today().isoformat()
                    )

                    # Log the generated docs to the DB
                    db.execute(
                        """
                        INSERT INTO generated_docs
                          (canonical_job_id, doc_type, drive_url, local_path, keyword_coverage,
                           keywords_hit, keywords_missed, model_used)
                        VALUES (?, 'resume', ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            job_id, resume_url, resume_path, result["keyword_coverage"],
                            str(result["keywords_hit"]), str(result["keywords_missed"]),
                            generation_model,
                        ),
                    )
                    if cover_url or cover_path:
                        db.execute(
                            "INSERT INTO generated_docs "
                            "(canonical_job_id, doc_type, drive_url, local_path, model_used) "
                            "VALUES (?, 'cover_letter', ?, ?, ?)",
                            (job_id, cover_url, cover_path, generation_model),
                        )

                    # Write doc links back to Sheet
                    try:
                        self.sheets.update_doc_links(job_id, resume_url, cover_url)
                    except Exception as exc:
                        logger.warning("Sheet doc-link update failed for %s: %s", job_id, exc)

                    stats["generated"] += 1
                    stats["docs"].append({
                        "canonical_job_id": job_id,
                        "company": job_row["company"],
                        "title": job_row["title"],
                        "resume_url": resume_url,
                        "cover_url": cover_url,
                        "resume_path": resume_path,
                        "cover_path": cover_path,
                    })

                except Exception as exc:
                    logger.error("Doc generation failed for %s: %s", job_id, exc)
                    stats["errors"] += 1

        logger.info("Doc generation done: %s", {k: v for k, v in stats.items() if k != "docs"})
        return stats

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _enforce_document_audit(result: dict) -> None:
        audit = result.get("document_audit")
        if not audit or audit.get("status") != "FAIL":
            return
        checks = tuple(
            DocumentAuditCheck(
                code=failure.get("code", "DOCUMENT_AUDIT_FAILURE"),
                severity=AuditSeverity(failure.get("severity", "critical")),
                requirement=failure.get("requirement", "Generated documents must pass Phase 1 audit."),
                explanation=failure.get("explanation", "Generated document audit failed."),
                recommended_fix=failure.get("recommended_fix", "Review document_audit failures."),
                passed=False,
            )
            for failure in audit.get("failures", [])
        )
        raise DocumentAuditFailure(DocumentAuditResult(document_type="document_set", checks=checks))

    def _fetch_jobs_needing_docs(self, db, job_ids: list[str] | None, force: bool):
        if job_ids:
            placeholders = ",".join("?" * len(job_ids))
            base = f"SELECT * FROM jobs WHERE canonical_job_id IN ({placeholders})"
            params = list(job_ids)
        else:
            base = "SELECT * FROM jobs WHERE app_state = 'selected'"
            params = []

        rows = db.execute(base, params).fetchall()
        if force:
            return rows

        # Filter out jobs that already have a resume
        filtered = []
        for row in rows:
            has_resume = db.execute(
                "SELECT 1 FROM generated_docs "
                "WHERE canonical_job_id = ? AND doc_type = 'resume' LIMIT 1",
                (row["canonical_job_id"],),
            ).fetchone()
            if not has_resume:
                filtered.append(row)
        return filtered

    @staticmethod
    def _generation_block_reason(row) -> str | None:
        clearance = (row["ko_clearance"] or "").strip() if "ko_clearance" in row.keys() else ""
        clearance_required = bool(
            clearance
            and clearance.lower()
            not in {"", "none", "n/a", "na", "not required", "no clearance", "no clearance required"}
        )
        if row["stretch_category"] == "long_shot":
            return "long_shot fit status"
        if row["ko_pe_required"]:
            return "PE license is required"
        if clearance_required:
            return f"security clearance is required ({clearance})"
        if row["ko_min_years"] is not None and row["ko_min_years"] > 2:
            return f"minimum years requirement exceeds current fit threshold ({row['ko_min_years']})"
        return None

    def _hydrate_canonical_job(self, row) -> CanonicalJob:
        return CanonicalJob(
            source=row["source"],
            source_job_id=row["source_job_id"],
            firm_id=row["firm_id"],
            company=row["company"],
            title=row["title"],
            location_city=row["location_city"],
            location_state=row["location_state"],
            description_normalized=row["description_normalized"],
            description_raw=row["description_raw"],
            apply_url=row["apply_url"],
            ats_type=ATSType(row["ats_type"] or "unknown"),
        )

    def _upload_docs(self, job_row, result, today: str) -> tuple[str | None, str | None, str, str]:
        safe_company = "".join(c for c in job_row["company"] if c.isalnum() or c in " -_")[:30]
        safe_title = "".join(c for c in job_row["title"] if c.isalnum() or c in " -_")[:30]
        prefix = f"{today}_{safe_company}_{safe_title}".replace(" ", "_")

        output_dir = GENERATED_APPLICATION_MATERIALS_DIR / str(job_row["canonical_job_id"])
        output_dir.mkdir(parents=True, exist_ok=True)
        resume_path = (output_dir / f"{prefix}_resume.docx").resolve()
        cover_path = (output_dir / f"{prefix}_cover.docx").resolve()

        if hasattr(self._generator, "prepare_resume_for_rendering"):
            rendered_resume_json, _ = self._generator.prepare_resume_for_rendering(result["resume_json"])
        else:
            rendered_resume_json = result["resume_json"]
        self._generator.save_docx(rendered_resume_json, str(resume_path))
        self._generator.save_cover_docx(
            result["cover_letter_json"],
            str(cover_path),
            job=self._hydrate_canonical_job(job_row),
            today=today,
        )
        self._audit_rendered_docs(
            job_row,
            result,
            str(resume_path),
            str(cover_path),
            rendered_resume_json=rendered_resume_json,
        )

        folder_id = self._get_or_create_drive_folder(prefix)
        resume_url = self.sheets.upload_document(
            str(resume_path), f"{prefix}_resume.docx", folder_id
        )
        cover_url = self.sheets.upload_document(
            str(cover_path), f"{prefix}_cover.docx", folder_id
        )
        return resume_url, cover_url, str(resume_path), str(cover_path)

    def _audit_rendered_docs(self, job_row, result: dict, resume_path: str, cover_path: str, rendered_resume_json: dict | None = None) -> None:
        if not hasattr(self._generator, "_profile"):
            return
        job = self._hydrate_canonical_job(job_row)
        audit = audit_generated_documents(
            resume_json=rendered_resume_json or result["resume_json"],
            cover_letter_json=result["cover_letter_json"],
            profile=getattr(self._generator, "_profile", {}) or {},
            job=job,
            resume_text=self._docx_text(resume_path),
            cover_letter_text=self._docx_text(cover_path),
            cover_formatting_metadata=cover_docx_formatting_metadata(cover_path),
        )
        result["document_audit"] = audit
        self._enforce_document_audit(result)

    @staticmethod
    def _docx_text(path: str) -> str:
        return "\n".join(paragraph.text for paragraph in DocxDocument(path).paragraphs if paragraph.text)

    def _get_or_create_drive_folder(self, name: str) -> str | None:
        if not settings.DRIVE_ROOT_FOLDER_ID:
            return None
        try:
            drive = self.sheets._drive_service()
            meta = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [settings.DRIVE_ROOT_FOLDER_ID],
            }
            folder = drive.files().create(body=meta, fields="id").execute()
            return folder.get("id")
        except Exception as exc:
            logger.warning("Drive folder creation failed: %s", exc)
            return settings.DRIVE_ROOT_FOLDER_ID

    def _lazy_init_generator(self) -> None:
        if self._generator is None:
            self._generator = DocumentGenerator()
            self._generator.load_profile()
