"""Tests for job_search.services.backup — local backup/export (Build 1, Lane C).

All tests operate against tmp_path fixtures only. None of these tests touch
the real data/jobs.db or any real generated artifacts.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from job_search.services.backup import create_backup


def _make_db(path: Path, rows: int = 0) -> None:
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, title TEXT)")
        for i in range(rows):
            conn.execute("INSERT INTO jobs (title) VALUES (?)", (f"job-{i}",))
        conn.commit()
    finally:
        conn.close()


def test_create_backup_copies_database(tmp_path):
    source_db = tmp_path / "source" / "jobs.db"
    source_db.parent.mkdir(parents=True)
    _make_db(source_db, rows=3)

    backup_root = tmp_path / "backups"
    result = create_backup(db_path=source_db, backup_root=backup_root)

    assert result.ok
    assert result.db_backup_path is not None
    assert result.db_backup_path.exists()
    assert result.db_backup_path.parent == result.backup_dir
    assert result.backup_dir.parent == backup_root


def test_backup_database_contents_match_source(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db, rows=5)

    backup_root = tmp_path / "backups"
    result = create_backup(db_path=source_db, backup_root=backup_root)

    conn = sqlite3.connect(str(result.db_backup_path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    finally:
        conn.close()
    assert count == 5


def test_backup_does_not_mutate_source_database(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db, rows=2)
    original_bytes = source_db.read_bytes()

    create_backup(db_path=source_db, backup_root=tmp_path / "backups")

    assert source_db.read_bytes() == original_bytes


def test_backup_is_independent_copy_not_same_file(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db, rows=1)

    result = create_backup(db_path=source_db, backup_root=tmp_path / "backups")

    # Mutate the backup copy and verify the source is unaffected — proves
    # this is a real independent copy, not a hardlink/same-inode reference.
    conn = sqlite3.connect(str(result.db_backup_path))
    try:
        conn.execute("INSERT INTO jobs (title) VALUES ('mutated-in-backup')")
        conn.commit()
    finally:
        conn.close()

    conn = sqlite3.connect(str(source_db))
    try:
        count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    finally:
        conn.close()
    assert count == 1


def test_backup_missing_database_is_not_an_error(tmp_path):
    missing_db = tmp_path / "does_not_exist.db"

    result = create_backup(db_path=missing_db, backup_root=tmp_path / "backups")

    assert result.db_backup_path is None
    assert result.source_db_path is None
    # Backup directory is still created even with nothing to capture, so the
    # caller has a deterministic location to inspect.
    assert result.backup_dir.exists()


def test_backup_copies_artifact_directories(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db)

    generated_dir = tmp_path / "generated"
    generated_dir.mkdir()
    (generated_dir / "resume.docx").write_text("fake resume content")

    result = create_backup(
        db_path=source_db,
        backup_root=tmp_path / "backups",
        artifact_dirs=("generated",),
        artifact_base=tmp_path,
    )

    assert "generated" in result.artifact_dirs_copied
    copied_file = result.backup_dir / "artifacts" / "generated" / "resume.docx"
    assert copied_file.exists()
    assert copied_file.read_text() == "fake resume content"


def test_backup_skips_missing_artifact_directories(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db)

    result = create_backup(
        db_path=source_db,
        backup_root=tmp_path / "backups",
        artifact_dirs=("nonexistent_dir",),
        artifact_base=tmp_path,
    )

    assert result.artifact_dirs_copied == []


def test_backup_uses_timestamped_directory_name(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db)

    fixed_time = datetime(2026, 6, 24, 12, 30, 45, tzinfo=timezone.utc)
    result = create_backup(
        db_path=source_db,
        backup_root=tmp_path / "backups",
        now=fixed_time,
    )

    assert result.timestamp == "20260624T123045Z"
    assert result.backup_dir.name == "20260624T123045Z"


def test_backup_result_ok_false_when_nothing_captured(tmp_path):
    result = create_backup(
        db_path=tmp_path / "missing.db",
        backup_root=tmp_path / "backups",
        artifact_dirs=(),
        artifact_base=tmp_path,
    )

    assert result.ok is False


def test_create_backup_uses_settings_db_path_by_default(tmp_path, monkeypatch):
    source_db = tmp_path / "default_jobs.db"
    _make_db(source_db, rows=1)
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(source_db))

    result = create_backup(backup_root=tmp_path / "backups")

    assert result.db_backup_path is not None
    assert result.db_backup_path.exists()


def test_multiple_backups_do_not_collide(tmp_path):
    source_db = tmp_path / "jobs.db"
    _make_db(source_db, rows=1)

    t1 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 1, 0, 0, 1, tzinfo=timezone.utc)

    result1 = create_backup(db_path=source_db, backup_root=tmp_path / "backups", now=t1)
    result2 = create_backup(db_path=source_db, backup_root=tmp_path / "backups", now=t2)

    assert result1.backup_dir != result2.backup_dir
    assert result1.db_backup_path.exists()
    assert result2.db_backup_path.exists()
