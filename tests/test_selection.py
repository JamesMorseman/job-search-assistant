"""Tests for SelectionProcessor sync logic (no live Sheet calls)."""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from job_search.db.connection import init_db
from job_search.models import CanonicalJob
from job_search.reporting.documents import get_latest_generated_doc, get_latest_generated_docs
from job_search.reporting.selection import SelectionProcessor
from job_search.reporting.sheets import SheetsLogger
from job_search.tracking import advance_state


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    monkeypatch.setattr("job_search.config.settings.TRACKER_SHEET_ID", "test-sheet-id")
    init_db(db_path)
    yield db_path


def _insert_job(db_path: str, job_id: str = "job1", state: str = "presented"):
    """Insert a minimal job row at the given state."""
    from job_search.ingestion.dedup import Deduplicator
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    dedup = Deduplicator(conn)
    dedup.upsert(CanonicalJob(
        canonical_job_id=job_id,
        source="test",
        source_job_id=job_id,
        company="Acme Engineering",
        title="Civil Engineer",
        description_normalized="structural design",
    ))
    if state != "discovered":
        # Walk it forward to the target state
        if state in ("presented", "selected", "applied", "rejected"):
            advance_state(conn, job_id, "presented", note="test setup")
        if state in ("selected", "applied"):
            advance_state(conn, job_id, "selected", note="test setup")
        if state == "applied":
            advance_state(conn, job_id, "applied", note="test setup")
        if state == "rejected":
            # rejected from presented; nothing else needed
            pass
    conn.commit()
    conn.close()


def _check_state(db_path: str, job_id: str) -> str:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT app_state FROM jobs WHERE canonical_job_id = ?", (job_id,)).fetchone()
    conn.close()
    return row["app_state"] if row else ""


def test_apply_status_moves_job_to_selected(db, monkeypatch):
    _insert_job(db, "job1", "presented")

    # Mock the sheet read to return one row with status="apply"
    mock_sheets = MagicMock(spec=SheetsLogger)
    mock_sheets.read_status_column.return_value = [("job1", "apply")]

    proc = SelectionProcessor()
    proc.sheets = mock_sheets
    stats = proc.sync_from_sheet()

    assert stats["selected"] == 1
    assert _check_state(db, "job1") == "selected"


def test_applied_status_advances_through_selected(db, monkeypatch):
    _insert_job(db, "job1", "selected")

    mock_sheets = MagicMock(spec=SheetsLogger)
    mock_sheets.read_status_column.return_value = [("job1", "applied")]

    proc = SelectionProcessor()
    proc.sheets = mock_sheets
    stats = proc.sync_from_sheet()

    assert stats["applied"] == 1
    assert _check_state(db, "job1") == "applied"


def test_skip_status_moves_to_rejected(db):
    _insert_job(db, "job1", "presented")

    mock_sheets = MagicMock(spec=SheetsLogger)
    mock_sheets.read_status_column.return_value = [("job1", "skip")]

    proc = SelectionProcessor()
    proc.sheets = mock_sheets
    stats = proc.sync_from_sheet()

    assert stats["rejected"] == 1
    assert _check_state(db, "job1") == "rejected"


def test_unrecognized_status_is_ignored(db):
    _insert_job(db, "job1", "presented")

    mock_sheets = MagicMock(spec=SheetsLogger)
    mock_sheets.read_status_column.return_value = [("job1", "thinking about it")]

    proc = SelectionProcessor()
    proc.sheets = mock_sheets
    stats = proc.sync_from_sheet()

    assert stats["synced"] == 0
    assert _check_state(db, "job1") == "presented"


def test_already_in_target_state_no_advance(db):
    _insert_job(db, "job1", "selected")

    mock_sheets = MagicMock(spec=SheetsLogger)
    mock_sheets.read_status_column.return_value = [("job1", "apply")]   # already selected

    proc = SelectionProcessor()
    proc.sheets = mock_sheets
    stats = proc.sync_from_sheet()

    assert stats["selected"] == 0    # no change


# ── _col_letter helper ───────────────────────────────────────────────────────

def test_col_letter_basic():
    assert SheetsLogger._col_letter(0) == "A"
    assert SheetsLogger._col_letter(20) == "U"
    assert SheetsLogger._col_letter(25) == "Z"
    assert SheetsLogger._col_letter(26) == "AA"
    assert SheetsLogger._col_letter(27) == "AB"


def test_upload_docs_renders_cover_letter_as_docx(monkeypatch):
    class FakeGenerator:
        def __init__(self):
            self.saved_resume = None
            self.saved_cover = None

        def save_docx(self, resume_json, output_path):
            self.saved_resume = output_path
            Path(output_path).write_bytes(b"resume")

        def save_cover_docx(self, cover_json, output_path, job=None, today=None):
            self.saved_cover = {
                "path": output_path,
                "cover_json": cover_json,
                "job": job,
                "today": today,
            }
            Path(output_path).write_bytes(b"cover")

    uploaded = []

    class FakeSheets:
        def upload_document(self, local_path, filename, folder_id=None):
            uploaded.append((local_path, filename, folder_id))
            return f"https://example.invalid/{filename}"

    monkeypatch.setattr("job_search.config.settings.DRIVE_ROOT_FOLDER_ID", "")
    proc = SelectionProcessor()
    proc.sheets = FakeSheets()
    proc._generator = FakeGenerator()
    job_row = {
        "canonical_job_id": "job1",
        "source": "test",
        "source_job_id": "job1",
        "firm_id": None,
        "company": "Acme Engineering",
        "title": "Civil Engineer",
        "location_city": "New York",
        "location_state": "NY",
        "description_normalized": "Structural design.",
        "description_raw": "",
        "apply_url": "",
        "ats_type": "unknown",
    }
    result = {
        "resume_json": {"professional_summary": "Summary."},
        "cover_letter_json": {
            "salutation": "Dear Hiring Manager,",
            "body_paragraphs": ["Paragraph one.", "Paragraph two."],
            "closing": "Sincerely,\nJames Morseman",
        },
    }

    resume_url, cover_url = proc._upload_docs(job_row, result, today="2026-06-12")

    assert resume_url.endswith("_resume.docx")
    assert cover_url.endswith("_cover.docx")
    assert uploaded[0][1].endswith("_resume.docx")
    assert uploaded[1][1].endswith("_cover.docx")
    assert proc._generator.saved_cover["today"] == "2026-06-12"
    assert proc._generator.saved_cover["job"].company == "Acme Engineering"


def test_fetch_jobs_skips_existing_docs_unless_force(db):
    _insert_job(db, "job1", "selected")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url) VALUES (?, 'resume', ?)",
        ("job1", "https://example.invalid/old_resume.docx"),
    )
    conn.commit()

    proc = SelectionProcessor()

    assert proc._fetch_jobs_needing_docs(conn, ["job1"], force=False) == []
    forced = proc._fetch_jobs_needing_docs(conn, ["job1"], force=True)
    assert [row["canonical_job_id"] for row in forced] == ["job1"]
    assert _check_state(db, "job1") == "selected"
    conn.close()


def test_latest_generated_docs_are_identifiable(db):
    _insert_job(db, "job1", "selected")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.executemany(
        """
        INSERT INTO generated_docs
          (canonical_job_id, doc_type, drive_url, generated_at)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("job1", "resume", "https://example.invalid/resume-old.docx", "2026-06-10 09:00:00"),
            ("job1", "cover_letter", "https://example.invalid/cover-old.docx", "2026-06-10 09:00:00"),
            ("job1", "resume", "https://example.invalid/resume-new.docx", "2026-06-11 09:00:00"),
            ("job1", "cover_letter", "https://example.invalid/cover-new.docx", "2026-06-11 09:00:00"),
        ],
    )
    conn.commit()

    latest_resume = get_latest_generated_doc(conn, "job1", "resume")
    latest_docs = get_latest_generated_docs(conn, "job1")

    assert latest_resume["drive_url"].endswith("resume-new.docx")
    assert latest_docs["resume"]["drive_url"].endswith("resume-new.docx")
    assert latest_docs["cover_letter"]["drive_url"].endswith("cover-new.docx")
    conn.close()
