"""Tests for Phase 3 Step 4: YAML-to-SQLite approved firm sync."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
import yaml

from job_search.db.connection import (
    _FIRMS_ADDED_COLUMNS,
    _apply_migrations,
    get_db,
    init_db,
)
from job_search.firms.repository import sync_approved_firms, write_draft
from job_search.models import (
    DraftFirmProfile,
    FirmApproval,
    FirmATS,
    FirmBenefit,
    FirmProfile,
    FirmProfileMeta,
    FirmTrajectoryPrior,
    ATSType,
    ATSTier,
)


# ── Fixtures and helpers ──────────────────────────────────────────────────────

@pytest.fixture
def test_db(tmp_path) -> str:
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


def make_approval(**kwargs) -> FirmApproval:
    defaults = dict(approved_at="2026-06-14", approved_by="james", last_verified="2026-06-14")
    defaults.update(kwargs)
    return FirmApproval(**defaults)


def make_profile(**kwargs) -> FirmProfile:
    defaults = dict(
        firm_id="stantec",
        name="Stantec",
        approval=make_approval(),
    )
    defaults.update(kwargs)
    return FirmProfile(**defaults)


def write_firms_yaml(path: Path, profiles: list[FirmProfile]) -> None:
    data = {"firms": [p.model_dump(mode="json") for p in profiles]}
    path.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")


def fetch_firm(db_path: str, firm_id: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM firms WHERE firm_id = ?", (firm_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def count_firms(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    n = conn.execute("SELECT COUNT(*) FROM firms").fetchone()[0]
    conn.close()
    return n


# ── Group A: Schema migration ─────────────────────────────────────────────────

def test_new_firms_columns_present_after_init_db(test_db):
    conn = sqlite3.connect(test_db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(firms)")}
    conn.close()
    for col in _FIRMS_ADDED_COLUMNS:
        assert col in cols, f"Expected column '{col}' in firms table"


def test_firms_added_columns_dict_has_expected_keys():
    expected = {"aliases", "benefits_json", "trajectory_json", "manual_priority", "last_verified"}
    assert set(_FIRMS_ADDED_COLUMNS.keys()) == expected


def test_migration_is_idempotent(test_db):
    """Running _apply_migrations twice on the same DB must not raise."""
    conn = sqlite3.connect(test_db)
    _apply_migrations(conn)
    _apply_migrations(conn)
    conn.close()


def test_migration_adds_columns_to_existing_db_without_them(tmp_path):
    """Simulate an older DB that lacks the new firms columns."""
    db_path = str(tmp_path / "legacy.db")
    # Create schema without the new columns (manually)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE firms (firm_id TEXT PRIMARY KEY, name TEXT NOT NULL, "
        "created_at TEXT DEFAULT (datetime('now')))"
    )
    conn.execute(
        "CREATE TABLE jobs (canonical_job_id TEXT PRIMARY KEY, source TEXT NOT NULL, "
        "source_job_id TEXT NOT NULL, company TEXT NOT NULL, title TEXT NOT NULL, "
        "UNIQUE(source, source_job_id))"
    )
    conn.execute(
        "CREATE TABLE generated_docs (id INTEGER PRIMARY KEY, "
        "canonical_job_id TEXT NOT NULL, doc_type TEXT NOT NULL, "
        "generated_at TEXT DEFAULT (datetime('now')))"
    )
    conn.commit()
    conn.close()

    _apply_migrations(sqlite3.connect(db_path))

    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(firms)")}
    conn.close()
    for col in _FIRMS_ADDED_COLUMNS:
        assert col in cols


# ── Group B: sync_approved_firms — core behavior ──────────────────────────────

def test_sync_empty_yaml_returns_zero(test_db, tmp_path):
    config = tmp_path / "firms.yaml"
    config.write_text("firms: []\n")
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 0
    assert count_firms(test_db) == 0


def test_sync_missing_yaml_returns_zero(test_db):
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path="/nonexistent/firms.yaml")
    assert n == 0


def test_sync_inserts_approved_firm(test_db, tmp_path):
    profile = make_profile()
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 1
    row = fetch_firm(test_db, "stantec")
    assert row is not None
    assert row["name"] == "Stantec"


def test_sync_updates_existing_firm_on_second_call(test_db, tmp_path):
    profile_v1 = make_profile(name="Stantec Original")
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile_v1])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)

    profile_v2 = make_profile(name="Stantec Updated")
    write_firms_yaml(config, [profile_v2])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)

    row = fetch_firm(test_db, "stantec")
    assert row["name"] == "Stantec Updated"
    assert count_firms(test_db) == 1  # still one row, not two


def test_sync_is_idempotent(test_db, tmp_path):
    profile = make_profile()
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    assert count_firms(test_db) == 1


def test_sync_multiple_firms(test_db, tmp_path):
    profiles = [
        make_profile(firm_id="aecom", name="AECOM"),
        make_profile(firm_id="jacobs", name="Jacobs"),
        make_profile(firm_id="stantec", name="Stantec"),
    ]
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, profiles)
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 3
    assert count_firms(test_db) == 3


def test_sync_skips_invalid_entry_without_approval(test_db, tmp_path):
    """FirmConfig-shaped entries (no approval field) must be skipped gracefully."""
    data = {"firms": [{"firm_id": "badfirm", "name": "Bad Firm"}]}  # missing approval
    config = tmp_path / "firms.yaml"
    config.write_text(yaml.dump(data))
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 0
    assert fetch_firm(test_db, "badfirm") is None


def test_sync_skips_invalid_entry_continues_with_valid(test_db, tmp_path):
    """One bad entry must not prevent valid entries from syncing."""
    bad = {"firm_id": "badfirm", "name": "Bad Firm"}  # no approval
    good = make_profile().model_dump(mode="json")
    config = tmp_path / "firms.yaml"
    config.write_text(yaml.dump({"firms": [bad, good]}))
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 1
    assert fetch_firm(test_db, "stantec") is not None
    assert fetch_firm(test_db, "badfirm") is None


# ── Group C: Field persistence ────────────────────────────────────────────────

def test_sync_stores_aliases_as_json_array(test_db, tmp_path):
    profile = make_profile(aliases=["Stantec Consulting", "Stantec Inc"])
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    parsed = json.loads(row["aliases"])
    assert parsed == ["Stantec Consulting", "Stantec Inc"]


def test_sync_stores_benefits_json(test_db, tmp_path):
    profile = make_profile(
        benefits={
            "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=0.9),
            "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.6),
        }
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    benefits = json.loads(row["benefits_json"])
    assert "tuition_reimbursement" in benefits
    assert benefits["tuition_reimbursement"]["status"] == "confirmed"
    assert benefits["pe_exam_reimbursement"]["confidence"] == 0.6


def test_sync_stores_trajectory_json(test_db, tmp_path):
    profile = make_profile(
        trajectory={
            "eit_pe_path": FirmTrajectoryPrior(status="likely", confidence=0.7),
            "internal_mobility": FirmTrajectoryPrior(status="unknown", confidence=0.0),
        }
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    traj = json.loads(row["trajectory_json"])
    assert "eit_pe_path" in traj
    assert traj["eit_pe_path"]["status"] == "likely"
    assert "internal_mobility" in traj


def test_sync_stores_last_verified(test_db, tmp_path):
    profile = make_profile(approval=make_approval(last_verified="2026-06-14"))
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["last_verified"] == "2026-06-14"


def test_sync_stores_manual_priority(test_db, tmp_path):
    profile = make_profile(manual_priority="target")
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["manual_priority"] == "target"


def test_sync_stores_ats_fields(test_db, tmp_path):
    profile = make_profile(
        ats=FirmATS(type=ATSType.WORKDAY, tier=ATSTier.YELLOW, tenant="stantec", site="Careers")
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["ats_type"] == "workday"
    assert row["ats_tier"] == "yellow"
    assert row["ats_tenant"] == "stantec"


def test_sync_stores_profile_meta(test_db, tmp_path):
    profile = make_profile(
        profile=FirmProfileMeta(enr_rank=12, employee_count="10000+", disciplines=["structural"])
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["enr_rank"] == 12
    assert row["employee_count"] == "10000+"
    assert json.loads(row["specialties"]) == ["structural"]


def test_sync_sets_tuition_reimbursement_flag_when_confirmed(test_db, tmp_path):
    profile = make_profile(
        benefits={"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["tuition_reimbursement"] == 1


def test_sync_sets_tuition_reimbursement_flag_when_likely(test_db, tmp_path):
    profile = make_profile(
        benefits={"tuition_reimbursement": FirmBenefit(status="likely", confidence=0.6)}
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["tuition_reimbursement"] == 1


def test_sync_does_not_set_tuition_flag_when_unknown(test_db, tmp_path):
    profile = make_profile(
        benefits={"tuition_reimbursement": FirmBenefit(status="unknown", confidence=0.0)}
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["tuition_reimbursement"] == 0


def test_sync_sets_pe_support_flag_from_pe_exam_reimbursement(test_db, tmp_path):
    profile = make_profile(
        benefits={"pe_exam_reimbursement": FirmBenefit(status="confirmed", confidence=0.9)}
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["pe_support"] == 1


def test_sync_sets_pe_support_flag_from_pe_prep_reimbursement(test_db, tmp_path):
    profile = make_profile(
        benefits={"pe_prep_reimbursement": FirmBenefit(status="likely", confidence=0.7)}
    )
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)
    row = fetch_firm(test_db, "stantec")
    assert row["pe_support"] == 1


def test_sync_does_not_reset_circuit_state_on_update(test_db, tmp_path):
    """Updating intelligence fields must not overwrite circuit breaker state."""
    # First insert a firm via raw SQL with circuit_state = 'open'
    conn = sqlite3.connect(test_db)
    conn.execute(
        "INSERT INTO firms (firm_id, name, circuit_state) VALUES (?, ?, ?)",
        ("stantec", "Stantec Old", "open"),
    )
    conn.commit()
    conn.close()

    # Now sync the approved profile
    profile = make_profile(name="Stantec New")
    config = tmp_path / "firms.yaml"
    write_firms_yaml(config, [profile])
    with get_db(test_db) as db:
        sync_approved_firms(db, config_path=config)

    row = fetch_firm(test_db, "stantec")
    assert row["name"] == "Stantec New"        # intelligence updated
    assert row["circuit_state"] == "open"       # operational state preserved


# ── Group D: Draft isolation ──────────────────────────────────────────────────

def test_draft_files_not_synced_when_config_is_empty(test_db, tmp_path):
    """Draft profiles in data/firm_drafts/ must never reach the sync path."""
    drafts_dir = tmp_path / "firm_drafts"
    drafts_dir.mkdir()
    draft = DraftFirmProfile(firm_id="draft_firm", name="Draft Corp")
    write_draft(draft, drafts_dir=drafts_dir)

    config = tmp_path / "firms.yaml"
    config.write_text("firms: []\n")
    with get_db(test_db) as db:
        n = sync_approved_firms(db, config_path=config)
    assert n == 0
    assert fetch_firm(test_db, "draft_firm") is None


def test_draft_firm_profile_cannot_be_synced_directly(test_db):
    """DraftFirmProfile lacks approval — it cannot be passed to _upsert_firm."""
    from job_search.firms.repository import _upsert_firm
    draft = DraftFirmProfile(firm_id="draft", name="Draft")
    with pytest.raises((AttributeError, TypeError)):
        with get_db(test_db) as db:
            _upsert_firm(db, draft)  # type: ignore[arg-type]


# ── Group E: Backward compatibility ──────────────────────────────────────────

def test_firm_config_still_loads_via_ingestor(tmp_path):
    """Ingestor.load_firms() must continue to read FirmConfig records unchanged."""
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text(yaml.dump({"firms": [
        {
            "firm_id": "acme_engineering",
            "name": "ACME Engineering",
            "ats_type": "greenhouse",
            "ats_tier": "green",
            "ats_board_token": "acmeengineering",
        }
    ]}))
    from job_search.ingestion.ingestor import Ingestor
    ingestor = Ingestor(dry_run=True)
    ingestor.load_firms(str(firms_yaml))
    assert len(ingestor._firms) == 1
    assert ingestor._firms[0].firm_id == "acme_engineering"


def test_empty_firms_yaml_ingestor_still_runs(tmp_path):
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text("firms: []\n")
    from job_search.ingestion.ingestor import Ingestor
    ingestor = Ingestor(dry_run=True)
    ingestor.load_firms(str(firms_yaml))
    assert ingestor._firms == []


def test_existing_jobs_table_migrations_still_apply(test_db):
    """Existing jobs column migrations must still run alongside firms migrations."""
    conn = sqlite3.connect(test_db)
    job_cols = {row[1] for row in conn.execute("PRAGMA table_info(jobs)")}
    conn.close()
    for col in ("benefit_reasons", "trajectory_reasons", "llm_grade"):
        assert col in job_cols, f"Expected jobs column '{col}' still present"
