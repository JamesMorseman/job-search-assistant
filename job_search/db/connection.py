import sqlite3
from contextlib import contextmanager
from pathlib import Path

from job_search.config import settings

# Columns/indexes added after the original schema shipped. `CREATE TABLE IF NOT
# EXISTS` handles new tables, but existing databases still need idempotent
# ALTER/CREATE INDEX statements on init.
_JOBS_ADDED_COLUMNS: dict[str, str] = {
    "llm_grade": "TEXT",
    "llm_fit_score": "REAL",
    "llm_rationale": "TEXT",
    "llm_graded_at": "TEXT",
    "llm_model": "TEXT",
    "benefit_reasons": "TEXT",
    "trajectory_reasons": "TEXT",
}

_FIRMS_ADDED_COLUMNS: dict[str, str] = {
    "aliases": "TEXT DEFAULT '[]'",
    "benefits_json": "TEXT DEFAULT '{}'",
    "trajectory_json": "TEXT DEFAULT '{}'",
    "manual_priority": "TEXT DEFAULT 'neutral'",
    "last_verified": "TEXT",
}

_ADDED_INDEXES: tuple[str, ...] = (
    """
    CREATE INDEX IF NOT EXISTS idx_generated_docs_job_type_generated
        ON generated_docs(canonical_job_id, doc_type, generated_at DESC, id DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_generated_docs_job_generated
        ON generated_docs(canonical_job_id, generated_at DESC, id DESC)
    """,
)


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Idempotently apply lightweight schema migrations. Safe every init."""
    existing_jobs = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    for col, decl in _JOBS_ADDED_COLUMNS.items():
        if col not in existing_jobs:
            conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} {decl}")

    existing_firms = {row[1] for row in conn.execute("PRAGMA table_info(firms)")}
    if existing_firms:  # table exists — safe to ALTER
        for col, decl in _FIRMS_ADDED_COLUMNS.items():
            if col not in existing_firms:
                conn.execute(f"ALTER TABLE firms ADD COLUMN {col} {decl}")

    for sql in _ADDED_INDEXES:
        conn.execute(sql)


def init_db(db_path: str | None = None) -> None:
    path = Path(db_path or settings.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = Path(__file__).parent / "schema.sql"
    with sqlite3.connect(path) as conn:
        conn.executescript(schema.read_text())
        _apply_migrations(conn)


@contextmanager
def get_db(db_path: str | None = None):
    path = db_path or settings.DB_PATH
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
