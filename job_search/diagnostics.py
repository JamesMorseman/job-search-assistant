"""Phase 7 Package 1 — credential & configuration diagnostics.

Read-only checks for runtime credentials and configuration whose absence
would otherwise cause a pipeline run to fail. No database writes, no
secret values are ever surfaced — only presence/absence and connectivity
status.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from job_search.config import settings

CheckStatus = Literal["pass", "warn", "fail"]


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    detail: str


def check_openai_api_key() -> CheckResult:
    present = bool(settings.OPENAI_API_KEY)
    return CheckResult(
        name="OPENAI_API_KEY",
        status="pass" if present else "fail",
        detail="present" if present else "missing — required for grading and document generation",
    )


def check_database_connectivity() -> CheckResult:
    db_path = Path(settings.DB_PATH)
    if not db_path.is_file():
        return CheckResult(
            name="DB_PATH",
            status="fail",
            detail=f"database file not found at {db_path}; run 'jsa init-db' before checking",
        )

    db_uri = f"file:{quote(db_path.as_posix(), safe='/:')}?mode=ro&immutable=1"
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_uri, uri=True, isolation_level=None)
        conn.execute("SELECT 1").fetchone()
    except Exception as exc:
        return CheckResult(name="DB_PATH", status="fail", detail=f"connection failed: {exc}")
    finally:
        if conn is not None:
            conn.close()
    return CheckResult(name="DB_PATH", status="pass", detail=f"connected ({settings.DB_PATH})")


def run_all_checks() -> list[CheckResult]:
    """Run every required diagnostic check. Read-only; writes no records."""
    return [check_openai_api_key(), check_database_connectivity()]


def required_checks_passed(results: list[CheckResult] | None = None) -> bool:
    results = results if results is not None else run_all_checks()
    return all(r.status != "fail" for r in results)
