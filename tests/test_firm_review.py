"""Tests for Phase 3 Step 5: Review and Approval Workflow."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from job_search.db.connection import get_db, init_db
from job_search.firms.repository import (
    DraftNotFoundError,
    DraftStatusError,
    approve_draft,
    load_firms_yaml,
    read_draft,
    reject_draft,
    save_firms_yaml,
    write_draft,
)
from job_search.models import (
    DraftFirmProfile,
    DraftStatus,
    FirmBenefit,
    FirmProfile,
    FirmTrajectoryPrior,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def test_db(tmp_path) -> str:
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


@pytest.fixture
def runner():
    return CliRunner()


def make_pending_draft(**kwargs) -> DraftFirmProfile:
    defaults = dict(firm_id="stantec", name="Stantec", draft_status=DraftStatus.PENDING_REVIEW)
    defaults.update(kwargs)
    return DraftFirmProfile(**defaults)


def make_draft_with_benefits(**kwargs) -> DraftFirmProfile:
    return DraftFirmProfile(
        firm_id="aecom",
        name="AECOM",
        draft_status=DraftStatus.PENDING_REVIEW,
        benefits={
            "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=0.9),
            "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.7),
        },
        trajectory={
            "eit_pe_path": FirmTrajectoryPrior(status="likely", confidence=0.8),
            "internal_mobility": FirmTrajectoryPrior(status="unknown", confidence=0.0),
        },
        **kwargs,
    )


def count_firms_in_yaml(config_path) -> int:
    return len(load_firms_yaml(config_path))


def fetch_firm_from_db(db_path: str, firm_id: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM firms WHERE firm_id = ?", (firm_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Group A: load_firms_yaml / save_firms_yaml ────────────────────────────────

def test_load_firms_yaml_missing_file_returns_empty(tmp_path):
    result = load_firms_yaml(tmp_path / "nonexistent.yaml")
    assert result == []


def test_load_firms_yaml_empty_firms_list(tmp_path):
    p = tmp_path / "firms.yaml"
    p.write_text("firms: []\n")
    assert load_firms_yaml(p) == []


def test_load_firms_yaml_returns_list_of_dicts(tmp_path):
    p = tmp_path / "firms.yaml"
    p.write_text(yaml.dump({"firms": [{"firm_id": "aecom", "name": "AECOM"}]}))
    result = load_firms_yaml(p)
    assert len(result) == 1
    assert result[0]["firm_id"] == "aecom"


def test_save_firms_yaml_creates_file(tmp_path):
    p = tmp_path / "firms.yaml"
    save_firms_yaml([{"firm_id": "aecom", "name": "AECOM"}], p)
    assert p.exists()


def test_save_firms_yaml_round_trips(tmp_path):
    p = tmp_path / "firms.yaml"
    data = [{"firm_id": "aecom", "name": "AECOM"}, {"firm_id": "jacobs", "name": "Jacobs"}]
    save_firms_yaml(data, p)
    loaded = load_firms_yaml(p)
    assert len(loaded) == 2
    assert {f["firm_id"] for f in loaded} == {"aecom", "jacobs"}


def test_save_firms_yaml_creates_parent_dir(tmp_path):
    p = tmp_path / "subdir" / "firms.yaml"
    save_firms_yaml([], p)
    assert p.exists()


# ── Group B: approve_draft — core behavior ────────────────────────────────────

def test_approve_draft_returns_firm_profile(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    profile = approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    assert isinstance(profile, FirmProfile)


def test_approve_draft_sets_approval_fields(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    profile = approve_draft("stantec", approved_by="james", last_verified="2026-06-14",
                            config_path=config, drafts_dir=tmp_path)
    assert profile.approval.approved_by == "james"
    assert profile.approval.last_verified == "2026-06-14"
    assert profile.approval.approved_at != ""


def test_approve_draft_defaults_last_verified_to_today(tmp_path):
    from datetime import date
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    profile = approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    assert profile.approval.last_verified == date.today().isoformat()


def test_approve_draft_preserves_intelligence_fields(tmp_path):
    draft = make_draft_with_benefits()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    profile = approve_draft("aecom", approved_by="james", config_path=config, drafts_dir=tmp_path)
    assert "tuition_reimbursement" in profile.benefits
    assert profile.benefits["tuition_reimbursement"].status.value == "confirmed"
    assert "eit_pe_path" in profile.trajectory


def test_approve_draft_writes_to_firms_yaml(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    firms = load_firms_yaml(config)
    assert any(f["firm_id"] == "stantec" for f in firms)


def test_approve_draft_merges_with_existing_yaml(tmp_path):
    # Pre-populate YAML with a different firm
    config = tmp_path / "firms.yaml"
    save_firms_yaml([{"firm_id": "jacobs", "name": "Jacobs",
                      "approval": {"approved_at": "2026-01-01", "approved_by": "james",
                                   "last_verified": "2026-01-01"}}], config)
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    firms = load_firms_yaml(config)
    ids = {f["firm_id"] for f in firms}
    assert ids == {"jacobs", "stantec"}


def test_approve_draft_replaces_existing_entry_for_same_firm(tmp_path):
    config = tmp_path / "firms.yaml"
    # Pre-existing entry for stantec
    save_firms_yaml([{"firm_id": "stantec", "name": "Old Stantec",
                      "approval": {"approved_at": "2025-01-01", "approved_by": "old",
                                   "last_verified": "2025-01-01"}}], config)
    draft = make_pending_draft(name="Stantec Updated")
    write_draft(draft, drafts_dir=tmp_path)
    approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    firms = load_firms_yaml(config)
    stantec = next(f for f in firms if f["firm_id"] == "stantec")
    assert stantec["name"] == "Stantec Updated"
    assert len([f for f in firms if f["firm_id"] == "stantec"]) == 1


def test_approve_draft_marks_draft_as_approved(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    updated = read_draft("stantec", drafts_dir=tmp_path)
    assert updated.draft_status == DraftStatus.APPROVED
    assert updated.review.approved is True
    assert updated.review.approved_by == "james"


def test_approve_draft_syncs_to_sqlite(tmp_path, test_db):
    draft = make_draft_with_benefits()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    with get_db(test_db) as db:
        approve_draft("aecom", approved_by="james", config_path=config,
                      drafts_dir=tmp_path, db=db)
    row = fetch_firm_from_db(test_db, "aecom")
    assert row is not None
    assert row["name"] == "AECOM"


def test_approve_draft_sqlite_has_benefit_flags(tmp_path, test_db):
    import json
    draft = make_draft_with_benefits()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    with get_db(test_db) as db:
        approve_draft("aecom", approved_by="james", config_path=config,
                      drafts_dir=tmp_path, db=db)
    row = fetch_firm_from_db(test_db, "aecom")
    assert row["tuition_reimbursement"] == 1
    assert row["pe_support"] == 1
    benefits = json.loads(row["benefits_json"])
    assert "tuition_reimbursement" in benefits


# ── Group C: approve_draft — error cases ─────────────────────────────────────

def test_approve_draft_raises_if_draft_not_found(tmp_path):
    config = tmp_path / "firms.yaml"
    with pytest.raises(DraftNotFoundError):
        approve_draft("nonexistent", approved_by="james",
                      config_path=config, drafts_dir=tmp_path)


def test_approve_draft_raises_for_already_approved_draft(tmp_path):
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.APPROVED
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    with pytest.raises(DraftStatusError, match="approved"):
        approve_draft("stantec", approved_by="james",
                      config_path=config, drafts_dir=tmp_path)


def test_approve_draft_raises_for_rejected_draft(tmp_path):
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.REJECTED
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    with pytest.raises(DraftStatusError, match="rejected"):
        approve_draft("stantec", approved_by="james",
                      config_path=config, drafts_dir=tmp_path)


def test_approve_draft_raises_for_invalid_firm_id(tmp_path):
    config = tmp_path / "firms.yaml"
    with pytest.raises(ValueError):
        approve_draft("../etc/passwd", approved_by="james",
                      config_path=config, drafts_dir=tmp_path)


def test_approved_profile_validates_vocab_keys(tmp_path):
    """A draft with bad benefit keys must not be approvable."""
    # Bypass the model validator by writing raw YAML
    bad_yaml = {
        "firm_id": "badfirm",
        "name": "Bad Firm",
        "draft_status": "pending_review",
        "benefits": {"not_a_real_key": {"status": "confirmed", "confidence": 0.9}},
    }
    path = tmp_path / "badfirm.yaml"
    path.write_text(yaml.dump(bad_yaml))
    config = tmp_path / "firms.yaml"
    with pytest.raises(Exception):
        approve_draft("badfirm", approved_by="james",
                      config_path=config, drafts_dir=tmp_path)


# ── Group D: reject_draft ─────────────────────────────────────────────────────

def test_reject_draft_returns_draft_with_rejected_status(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    result = reject_draft("stantec", drafts_dir=tmp_path)
    assert result.draft_status == DraftStatus.REJECTED


def test_reject_draft_preserves_draft_file(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    reject_draft("stantec", drafts_dir=tmp_path)
    assert (tmp_path / "stantec.yaml").exists()


def test_reject_draft_records_reviewer_notes(tmp_path):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    reject_draft("stantec", reviewer_notes="Too small to target.", drafts_dir=tmp_path)
    updated = read_draft("stantec", drafts_dir=tmp_path)
    assert "Too small to target." in updated.review.reviewer_notes


def test_reject_draft_preserves_evidence(tmp_path):
    draft = make_draft_with_benefits()
    write_draft(draft, drafts_dir=tmp_path)
    reject_draft("aecom", drafts_dir=tmp_path)
    updated = read_draft("aecom", drafts_dir=tmp_path)
    assert "tuition_reimbursement" in updated.benefits


def test_reject_draft_raises_if_not_found(tmp_path):
    with pytest.raises(DraftNotFoundError):
        reject_draft("nonexistent", drafts_dir=tmp_path)


def test_reject_draft_raises_for_invalid_firm_id():
    with pytest.raises(ValueError):
        reject_draft("../../evil")


def test_reject_approved_draft_raises(tmp_path):
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.APPROVED
    write_draft(draft, drafts_dir=tmp_path)
    with pytest.raises(DraftStatusError, match="approved"):
        reject_draft("stantec", drafts_dir=tmp_path)


def test_reject_already_rejected_draft_is_idempotent(tmp_path):
    """Rejecting a rejected draft again is allowed (re-adds notes)."""
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.REJECTED
    write_draft(draft, drafts_dir=tmp_path)
    result = reject_draft("stantec", reviewer_notes="Still no.", drafts_dir=tmp_path)
    assert result.draft_status == DraftStatus.REJECTED


def test_approved_draft_not_in_pending_review_list(tmp_path):
    """After approval the draft shows as 'approved', not in pending list."""
    from job_search.firms.repository import list_drafts
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    approve_draft("stantec", approved_by="james", config_path=config, drafts_dir=tmp_path)
    # Draft file is still listed (preserved for audit)
    assert "stantec" in list_drafts(drafts_dir=tmp_path)
    updated = read_draft("stantec", drafts_dir=tmp_path)
    assert updated.draft_status == DraftStatus.APPROVED


# ── Group E: CLI — jsa firms review ───────────────────────────────────────────

def test_cli_review_no_drafts(tmp_path, monkeypatch, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No draft" in result.output


def test_cli_review_lists_pending_draft(tmp_path, monkeypatch, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "stantec" in result.output
    assert "Stantec" in result.output


def test_cli_review_hides_approved_by_default(tmp_path, runner):
    approved = make_pending_draft()
    approved.draft_status = DraftStatus.APPROVED
    write_draft(approved, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "stantec" not in result.output


def test_cli_review_all_statuses_shows_approved(tmp_path, runner):
    approved = make_pending_draft()
    approved.draft_status = DraftStatus.APPROVED
    write_draft(approved, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "--all-statuses", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "stantec" in result.output


def test_cli_review_detail_shows_firm_info(tmp_path, runner):
    draft = make_draft_with_benefits()
    write_draft(draft, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "aecom", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "aecom" in result.output
    assert "AECOM" in result.output
    assert "tuition_reimbursement" in result.output
    assert "eit_pe_path" in result.output


def test_cli_review_detail_missing_firm(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "review", "nonexistent", "--drafts-dir", str(tmp_path)])
    assert result.exit_code != 0


# ── Group F: CLI — jsa firms approve ─────────────────────────────────────────

def test_cli_approve_succeeds(tmp_path, test_db, monkeypatch, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "approve", "stantec",
        "--approved-by", "james",
        "--drafts-dir", str(tmp_path),
        "--config", str(config),
    ])
    assert result.exit_code == 0
    assert "approved" in result.output.lower()


def test_cli_approve_writes_to_yaml(tmp_path, test_db, monkeypatch, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    runner.invoke(cli, [
        "firms", "approve", "stantec",
        "--approved-by", "james",
        "--drafts-dir", str(tmp_path),
        "--config", str(config),
    ])
    assert any(f["firm_id"] == "stantec" for f in load_firms_yaml(config))


def test_cli_approve_syncs_to_db(tmp_path, test_db, monkeypatch, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    runner.invoke(cli, [
        "firms", "approve", "stantec",
        "--approved-by", "james",
        "--drafts-dir", str(tmp_path),
        "--config", str(config),
    ])
    assert fetch_firm_from_db(test_db, "stantec") is not None


def test_cli_approve_missing_draft_exits_nonzero(tmp_path, test_db, monkeypatch, runner):
    config = tmp_path / "firms.yaml"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "approve", "nonexistent",
        "--approved-by", "james",
        "--drafts-dir", str(tmp_path),
        "--config", str(config),
    ])
    assert result.exit_code != 0


def test_cli_approve_rejected_draft_exits_nonzero(tmp_path, test_db, monkeypatch, runner):
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.REJECTED
    write_draft(draft, drafts_dir=tmp_path)
    config = tmp_path / "firms.yaml"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "approve", "stantec",
        "--approved-by", "james",
        "--drafts-dir", str(tmp_path),
        "--config", str(config),
    ])
    assert result.exit_code != 0
    assert "rejected" in result.output.lower()


# ── Group G: CLI — jsa firms reject ──────────────────────────────────────────

def test_cli_reject_succeeds(tmp_path, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "reject", "stantec",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code == 0
    assert "rejected" in result.output.lower()


def test_cli_reject_records_notes(tmp_path, runner):
    draft = make_pending_draft()
    write_draft(draft, drafts_dir=tmp_path)
    from job_search.cli import cli
    runner.invoke(cli, [
        "firms", "reject", "stantec",
        "--notes", "Not a target market.",
        "--drafts-dir", str(tmp_path),
    ])
    updated = read_draft("stantec", drafts_dir=tmp_path)
    assert "Not a target market." in updated.review.reviewer_notes


def test_cli_reject_missing_draft_exits_nonzero(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "reject", "nonexistent",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code != 0


def test_cli_reject_approved_draft_exits_nonzero(tmp_path, runner):
    draft = make_pending_draft()
    draft.draft_status = DraftStatus.APPROVED
    write_draft(draft, drafts_dir=tmp_path)
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "reject", "stantec",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code != 0


def test_cli_firms_group_now_has_review_approve_reject(runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "--help"])
    assert result.exit_code == 0
    assert "review" in result.output
    assert "approve" in result.output
    assert "reject" in result.output
