"""Tests for generated document history retrieval."""

import sqlite3

import pytest

from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.reporting.documents import (
    get_latest_generated_doc,
    get_latest_generated_docs,
    list_generated_docs,
)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", path)
    init_db(path)
    return path


@pytest.fixture
def db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    Deduplicator(conn).upsert(CanonicalJob(
        canonical_job_id="job1",
        source="test",
        source_job_id="job1",
        company="Acme Engineering",
        title="Civil Engineer",
    ))
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


def _insert_doc(db, doc_type: str, drive_url: str, generated_at: str = "2026-06-12 09:00:00") -> int:
    cursor = db.execute(
        """
        INSERT INTO generated_docs
          (canonical_job_id, doc_type, drive_url, generated_at)
        VALUES ('job1', ?, ?, ?)
        """,
        (doc_type, drive_url, generated_at),
    )
    db.commit()
    return int(cursor.lastrowid)


def test_latest_generated_doc_uses_id_tiebreaker_for_same_timestamp(db):
    _insert_doc(db, "resume", "https://example.invalid/resume-v1.docx")
    newer_id = _insert_doc(db, "resume", "https://example.invalid/resume-v2.docx")

    latest = get_latest_generated_doc(db, "job1", "resume")

    assert latest["id"] == newer_id
    assert latest["drive_url"].endswith("resume-v2.docx")


def test_latest_generated_docs_returns_none_for_missing_types(db):
    _insert_doc(db, "resume", "https://example.invalid/resume.docx")

    latest = get_latest_generated_docs(db, "job1")

    assert latest["resume"]["drive_url"].endswith("resume.docx")
    assert latest["cover_letter"] is None


def test_list_generated_docs_returns_history_newest_first(db):
    _insert_doc(db, "resume", "https://example.invalid/resume-old.docx", "2026-06-10 09:00:00")
    _insert_doc(db, "cover_letter", "https://example.invalid/cover.docx", "2026-06-11 09:00:00")
    _insert_doc(db, "resume", "https://example.invalid/resume-new.docx", "2026-06-12 09:00:00")

    all_docs = list_generated_docs(db, "job1")
    resume_docs = list_generated_docs(db, "job1", doc_type="resume", limit=1)

    assert [row["drive_url"] for row in all_docs] == [
        "https://example.invalid/resume-new.docx",
        "https://example.invalid/cover.docx",
        "https://example.invalid/resume-old.docx",
    ]
    assert [row["drive_url"] for row in resume_docs] == [
        "https://example.invalid/resume-new.docx",
    ]


def test_generated_doc_helpers_validate_inputs(db):
    with pytest.raises(ValueError, match="Unsupported generated doc type"):
        get_latest_generated_doc(db, "job1", "portfolio")

    with pytest.raises(ValueError, match="Unsupported generated doc type"):
        list_generated_docs(db, "job1", doc_type="portfolio")

    with pytest.raises(ValueError, match="limit must be positive"):
        list_generated_docs(db, "job1", limit=0)


def test_init_db_creates_generated_doc_lookup_indexes(db):
    indexes = {row["name"] for row in db.execute("PRAGMA index_list(generated_docs)").fetchall()}

    assert "idx_generated_docs_job_type_generated" in indexes
    assert "idx_generated_docs_job_generated" in indexes
