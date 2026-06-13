"""Generate final Phase 1 review artifacts for visual inspection."""

import os
from pathlib import Path

import pytest

from scripts.generate_phase1_review_artifacts import OUT_DIR, REAL_JOB_OUT_DIR, main


def test_generate_phase1_review_artifacts():
    main()

    resume_path = OUT_DIR / "phase1_review_resume.docx"
    cover_path = OUT_DIR / "phase1_review_cover_letter.docx"
    summary_path = OUT_DIR / "phase1_review_render_summary.txt"

    assert resume_path.exists()
    assert cover_path.exists()
    summary = summary_path.read_text(encoding="utf-8")
    assert "https://github.com/JamesMorseman" in summary
    assert "Acme [Infrastructure Group]" in summary
    assert "closing. [" not in summary
    assert Path(summary_path).exists()


def test_generate_phase1_real_job_artifacts_when_requested():
    job_id = os.environ.get("PHASE1_REAL_JOB_ID")
    if not job_id:
        pytest.skip("Set PHASE1_REAL_JOB_ID to generate real-job review artifacts.")

    main(["--job-id", job_id])

    summaries = sorted(REAL_JOB_OUT_DIR.glob("*_render_summary.txt"))
    audits = sorted(REAL_JOB_OUT_DIR.glob("*_audit.json"))
    resumes = sorted(REAL_JOB_OUT_DIR.glob("*_resume.docx"))
    cover_letters = sorted(REAL_JOB_OUT_DIR.glob("*_cover_letter.docx"))

    assert summaries
    assert audits
    assert resumes
    assert cover_letters
    assert job_id in summaries[-1].read_text(encoding="utf-8")
