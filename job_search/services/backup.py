"""Local backup/export for job-search data (Build 1, Lane C).

Produces a timestamped, read-only export of the local SQLite database plus a
small set of generated career-material artifacts, so a user does not lose
their entire job-search history if `data/jobs.db` is lost or corrupted.

This module never mutates the source database or any source artifact files —
it only reads from them and writes new files under the destination directory.
The SQLite copy uses the standard library's online backup API
(`sqlite3.Connection.backup`), which is safe to use against a live database
(including one open elsewhere in WAL mode) without locking out other readers.
"""

from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from job_search.config import settings

#: Default root directory for backup exports. Matches the existing
#: gitignored `output/` convention used for other generated artifacts.
DEFAULT_BACKUP_ROOT = Path("output") / "backups"

#: Artifact directories copied alongside the database, if present. These are
#: generated career documents — useful to retain alongside the DB rows that
#: reference them, but never required for the backup to succeed.
_DEFAULT_ARTIFACT_DIRS: tuple[str, ...] = ("generated",)


@dataclass
class BackupResult:
    """Outcome of a single backup/export run."""

    backup_dir: Path
    db_backup_path: Path | None
    artifact_dirs_copied: list[str] = field(default_factory=list)
    source_db_path: Path | None = None
    timestamp: str = ""

    @property
    def ok(self) -> bool:
        """True if at least the database (or an artifact dir) was captured."""
        return self.db_backup_path is not None or bool(self.artifact_dirs_copied)


def _timestamp_dirname(now: datetime | None = None) -> str:
    moment = now or datetime.now(tz=timezone.utc)
    return moment.strftime("%Y%m%dT%H%M%SZ")


def _backup_database(source_db: Path, dest_dir: Path) -> Path | None:
    """Copy `source_db` into `dest_dir` using SQLite's online backup API.

    Returns the destination path, or None if the source database does not
    exist (e.g. a fresh install with no data yet — not an error condition).
    """
    if not source_db.exists():
        return None

    dest_path = dest_dir / source_db.name
    dest_dir.mkdir(parents=True, exist_ok=True)

    # `sqlite3.Connection.backup()` performs a consistent, lock-safe copy even
    # while the source DB is open elsewhere (e.g. WAL mode) — this is the
    # SQLite-recommended approach over a raw file copy, which can capture a
    # database mid-write or miss WAL-journaled pages.
    src_conn = sqlite3.connect(str(source_db))
    try:
        dest_conn = sqlite3.connect(str(dest_path))
        try:
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        src_conn.close()

    return dest_path


def _copy_artifact_dirs(
    artifact_dirs: tuple[str, ...], artifact_base: Path, dest_dir: Path
) -> list[str]:
    """Copy any existing artifact directories into the backup. Read-only on source."""
    copied: list[str] = []
    for name in artifact_dirs:
        source = artifact_base / name
        if not source.exists() or not source.is_dir():
            continue
        target = dest_dir / "artifacts" / name
        shutil.copytree(source, target, dirs_exist_ok=True)
        copied.append(name)
    return copied


def create_backup(
    *,
    db_path: str | Path | None = None,
    backup_root: str | Path | None = None,
    artifact_dirs: tuple[str, ...] = _DEFAULT_ARTIFACT_DIRS,
    artifact_base: str | Path | None = None,
    now: datetime | None = None,
) -> BackupResult:
    """Create a timestamped local backup of the job-search database and artifacts.

    Read-only with respect to all source data: the source database and
    artifact directories are never modified, deleted, or locked out — only
    read from. Safe to call against the live database.

    Args:
        db_path: path to the SQLite database to back up. Defaults to
            `settings.DB_PATH`.
        backup_root: root directory under which a new timestamped
            subdirectory is created for this backup. Defaults to
            `output/backups/`.
        artifact_dirs: relative directory names to copy alongside the DB
            backup, if they exist. Defaults to `("generated",)`.
        artifact_base: base directory that `artifact_dirs` are resolved
            against. Defaults to the current working directory (matching
            this repo's convention of running `jsa` commands from the repo
            root, where `generated/` lives).
        now: override for the current time (used by tests for determinism).

    Returns:
        A `BackupResult` describing what was captured and where.
    """
    source_db = Path(db_path) if db_path is not None else Path(settings.DB_PATH)
    root = Path(backup_root) if backup_root is not None else DEFAULT_BACKUP_ROOT
    base = Path(artifact_base) if artifact_base is not None else Path.cwd()

    timestamp = _timestamp_dirname(now)
    backup_dir = root / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    db_backup_path = _backup_database(source_db, backup_dir)
    copied_artifacts = _copy_artifact_dirs(artifact_dirs, base, backup_dir)

    return BackupResult(
        backup_dir=backup_dir,
        db_backup_path=db_backup_path,
        artifact_dirs_copied=copied_artifacts,
        source_db_path=source_db if source_db.exists() else None,
        timestamp=timestamp,
    )
