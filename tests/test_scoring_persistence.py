"""Tests for Phase 2 Step 2: benefit/trajectory reason persistence."""

import json
import sqlite3

import pytest

from job_search.db.connection import _apply_migrations, init_db
from job_search.ingestion.scoring import (
    SignalHit,
    Scorer,
    _serialize_hits,
)
from job_search.models import CanonicalJob


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_job(**kwargs) -> CanonicalJob:
    defaults = dict(
        source="test",
        source_job_id="p001",
        company="Acme",
        title="Structural Engineer",
        description_normalized=(
            "structural design engineer in training EIT tuition reimbursement "
            "mentorship program pe exam reimbursement"
        ),
        location_city="Seattle",
        location_state="WA",
    )
    defaults.update(kwargs)
    return CanonicalJob(**defaults)


def make_hit(key="tuition_reimbursement", label="Tuition reimbursement", weight=0.18) -> SignalHit:
    return SignalHit(
        key=key,
        label=label,
        source="job_description",
        weight=weight,
        confidence=1.0,
        matched_text="tuition reimbursement",
        reason=f"Job post mentions {label.lower()}.",
    )


# ── Group 1: Schema migration ─────────────────────────────────────────────────

def test_init_db_creates_reason_columns(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    conn.close()
    assert "benefit_reasons" in columns
    assert "trajectory_reasons" in columns


def _create_legacy_schema(conn: sqlite3.Connection) -> None:
    """Create the pre-reason-column schema that a real legacy database would have."""
    conn.execute("""
        CREATE TABLE jobs (
            canonical_job_id TEXT PRIMARY KEY,
            source TEXT,
            source_job_id TEXT,
            company TEXT,
            title TEXT,
            benefit_score REAL DEFAULT 0.0,
            career_trajectory_score REAL DEFAULT 0.0,
            app_state TEXT DEFAULT 'discovered',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # generated_docs always existed alongside jobs — migration depends on it.
    conn.execute("""
        CREATE TABLE generated_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
            doc_type TEXT NOT NULL,
            generated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def test_migration_adds_reason_columns_to_existing_db(tmp_path):
    """Simulates a pre-existing database that lacks the reason columns."""
    db_path = str(tmp_path / "legacy.db")
    conn = sqlite3.connect(db_path)
    _create_legacy_schema(conn)
    conn.commit()
    # Confirm columns absent before migration.
    before = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    assert "benefit_reasons" not in before
    assert "trajectory_reasons" not in before
    # Apply migration.
    _apply_migrations(conn)
    conn.commit()
    after = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    conn.close()
    assert "benefit_reasons" in after
    assert "trajectory_reasons" in after


def test_migration_is_idempotent(tmp_path):
    """Applying migrations twice must not raise."""
    db_path = str(tmp_path / "idem.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    _apply_migrations(conn)  # second application
    conn.close()


# ── Group 2: Reason serialization ────────────────────────────────────────────

def test_serialize_hits_produces_valid_json():
    hit = make_hit()
    result = _serialize_hits([hit])
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 1


def test_serialize_hits_empty_produces_empty_array():
    result = _serialize_hits([])
    assert result == "[]"


def test_serialize_hits_fields_present():
    hit = make_hit()
    parsed = json.loads(_serialize_hits([hit]))
    record = parsed[0]
    assert record["key"] == "tuition_reimbursement"
    assert record["label"] == "Tuition reimbursement"
    assert record["source"] == "job_description"
    assert record["weight"] == 0.18
    assert record["confidence"] == 1.0
    assert record["matched_text"] == "tuition reimbursement"
    assert "reason" in record


def test_serialize_hits_is_deterministic():
    hits = [make_hit("tuition_reimbursement", "Tuition reimbursement", 0.18),
            make_hit("signing_bonus", "Signing bonus", 0.02)]
    assert _serialize_hits(hits) == _serialize_hits(hits)


def test_serialize_hits_uses_sort_keys():
    """JSON keys must be alphabetically sorted for stable output."""
    hit = make_hit()
    raw = _serialize_hits([hit])
    parsed = json.loads(raw)
    keys = list(parsed[0].keys())
    assert keys == sorted(keys)


def test_serialize_hits_multiple_preserves_order():
    """Hit order in the array reflects the input list order (sorted by weight from engine)."""
    high = make_hit("tuition_reimbursement", "Tuition reimbursement", 0.18)
    low = make_hit("signing_bonus", "Signing bonus", 0.02)
    parsed = json.loads(_serialize_hits([high, low]))
    assert parsed[0]["key"] == "tuition_reimbursement"
    assert parsed[1]["key"] == "signing_bonus"


# ── Group 3: Reason persistence end-to-end ───────────────────────────────────

def test_scorer_populates_benefit_reasons():
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)
    parsed = json.loads(job.benefit_reasons)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    keys = [r["key"] for r in parsed]
    assert "tuition_reimbursement" in keys


def test_scorer_populates_trajectory_reasons():
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)
    parsed = json.loads(job.trajectory_reasons)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    keys = [r["key"] for r in parsed]
    assert "eit_pe_path" in keys


def test_reasons_written_to_db(tmp_path):
    db_path = str(tmp_path / "reasons.db")
    init_db(db_path)
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)

    conn = sqlite3.connect(db_path)
    d = job.to_db_dict()
    cols = ", ".join(d.keys())
    placeholders = ", ".join(["?"] * len(d))
    conn.execute(f"INSERT INTO jobs ({cols}) VALUES ({placeholders})", list(d.values()))
    conn.commit()

    row = conn.execute(
        "SELECT benefit_reasons, trajectory_reasons FROM jobs WHERE canonical_job_id = ?",
        (job.canonical_job_id,),
    ).fetchone()
    conn.close()

    assert row is not None
    benefit_parsed = json.loads(row[0])
    trajectory_parsed = json.loads(row[1])
    assert isinstance(benefit_parsed, list)
    assert isinstance(trajectory_parsed, list)
    assert len(benefit_parsed) > 0
    assert len(trajectory_parsed) > 0


def test_reasons_in_db_match_scorer_output(tmp_path):
    db_path = str(tmp_path / "match.db")
    init_db(db_path)
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)

    conn = sqlite3.connect(db_path)
    d = job.to_db_dict()
    cols = ", ".join(d.keys())
    placeholders = ", ".join(["?"] * len(d))
    conn.execute(f"INSERT INTO jobs ({cols}) VALUES ({placeholders})", list(d.values()))
    conn.commit()

    row = conn.execute(
        "SELECT benefit_reasons, trajectory_reasons FROM jobs WHERE canonical_job_id = ?",
        (job.canonical_job_id,),
    ).fetchone()
    conn.close()

    assert row[0] == job.benefit_reasons
    assert row[1] == job.trajectory_reasons


# ── Group 4: Backward compatibility ──────────────────────────────────────────

def test_canonical_job_default_reasons_are_empty_arrays():
    job = CanonicalJob(source="test", source_job_id="bc001", company="Old Corp", title="Engineer")
    assert job.benefit_reasons == "[]"
    assert job.trajectory_reasons == "[]"


def test_existing_row_without_reason_columns_readable(tmp_path):
    """A job row written before reason columns existed can still be read."""
    db_path = str(tmp_path / "compat.db")
    conn = sqlite3.connect(db_path)
    _create_legacy_schema(conn)
    conn.execute(
        "INSERT INTO jobs (canonical_job_id, source, source_job_id, company, title) VALUES (?,?,?,?,?)",
        ("abc123", "test", "old001", "OldCorp", "Civil Engineer"),
    )
    conn.commit()
    # Apply migration to add reason columns.
    _apply_migrations(conn)
    conn.commit()
    # Existing row should have NULL for the new columns (SQLite ALTER ADD COLUMN default).
    row = conn.execute(
        "SELECT benefit_reasons, trajectory_reasons FROM jobs WHERE canonical_job_id = 'abc123'"
    ).fetchone()
    conn.close()
    # NULL is acceptable for pre-migration rows; empty array is only set on new writes.
    assert row is not None
    # Either NULL or a valid JSON value is acceptable — must not raise.
    for val in row:
        if val is not None:
            json.loads(val)  # must be valid JSON if present


def test_no_signal_job_persists_empty_arrays(tmp_path):
    db_path = str(tmp_path / "empty.db")
    init_db(db_path)
    scorer = Scorer()
    job = make_job(
        source_job_id="nosig001",
        description_normalized="civil engineering design position salary benefits",
    )
    job = scorer.score(job)

    assert job.benefit_reasons == "[]"
    assert job.trajectory_reasons == "[]"

    conn = sqlite3.connect(db_path)
    d = job.to_db_dict()
    cols = ", ".join(d.keys())
    placeholders = ", ".join(["?"] * len(d))
    conn.execute(f"INSERT INTO jobs ({cols}) VALUES ({placeholders})", list(d.values()))
    conn.commit()

    row = conn.execute(
        "SELECT benefit_reasons, trajectory_reasons FROM jobs WHERE canonical_job_id = ?",
        (job.canonical_job_id,),
    ).fetchone()
    conn.close()

    assert json.loads(row[0]) == []
    assert json.loads(row[1]) == []


def test_to_db_dict_includes_reason_fields():
    job = CanonicalJob(source="test", source_job_id="dict001", company="X", title="Y")
    d = job.to_db_dict()
    assert "benefit_reasons" in d
    assert "trajectory_reasons" in d
    assert d["benefit_reasons"] == "[]"
    assert d["trajectory_reasons"] == "[]"
