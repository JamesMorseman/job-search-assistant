"""Tests for Phase 3 Step 3: missing-firm discovery (discovery.py and jsa firms discover)."""

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from job_search.db.connection import init_db
from job_search.firms.discovery import (
    FirmCandidate,
    _load_approved_firm_ids,
    _make_firm_id_slug,
    discover_missing_firms,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def test_db(tmp_path) -> str:
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


@pytest.fixture
def empty_firms_yaml(tmp_path) -> str:
    p = tmp_path / "firms.yaml"
    p.write_text("firms: []\n", encoding="utf-8")
    return str(p)


def insert_job(
    db_path: str,
    company: str,
    source: str = "test_source",
    apply_url: str | None = None,
    title: str = "Civil Engineer",
) -> None:
    """Insert one job row into a test DB. Uses uuid for guaranteed unique source_job_id."""
    source_job_id = str(uuid.uuid4())
    import hashlib
    cjid = hashlib.sha256(f"{source}:{source_job_id}".encode()).hexdigest()[:32]
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR IGNORE INTO jobs "
        "(canonical_job_id, source, source_job_id, company, title, apply_url) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (cjid, source, source_job_id, company, title, apply_url),
    )
    conn.commit()
    conn.close()


def make_firms_yaml(tmp_path: Path, firm_ids: list[str]) -> str:
    """Write a firms.yaml with the given firm_ids as minimal approved records."""
    firms = [{"firm_id": fid, "name": fid.title()} for fid in firm_ids]
    p = tmp_path / "firms.yaml"
    p.write_text(yaml.dump({"firms": firms}), encoding="utf-8")
    return str(p)


# ── Group A: _make_firm_id_slug ───────────────────────────────────────────────

def test_slug_lowercases():
    assert _make_firm_id_slug("AECOM") == "aecom"


def test_slug_replaces_spaces_with_underscore():
    assert _make_firm_id_slug("Golder Associates") == "golder_associates"


def test_slug_collapses_consecutive_non_alnum():
    assert _make_firm_id_slug("HDR, Inc.") == "hdr_inc"


def test_slug_strips_leading_trailing_underscores():
    assert _make_firm_id_slug(" RS&H ") == "rs_h"


def test_slug_truncates_at_40_chars():
    long_name = "A" * 60
    result = _make_firm_id_slug(long_name)
    assert len(result) == 40


def test_slug_empty_string_returns_unknown():
    assert _make_firm_id_slug("") == "unknown"


def test_slug_special_chars_only_returns_unknown():
    assert _make_firm_id_slug("!!!") == "unknown"


def test_slug_preserves_existing_underscores_and_digits():
    assert _make_firm_id_slug("WSP2 Group") == "wsp2_group"


# ── Group B: _load_approved_firm_ids ─────────────────────────────────────────

def test_load_approved_ids_empty_yaml(tmp_path):
    p = tmp_path / "firms.yaml"
    p.write_text("firms: []\n")
    result = _load_approved_firm_ids(p)
    assert result == frozenset()


def test_load_approved_ids_populated_yaml(tmp_path):
    p = tmp_path / "firms.yaml"
    p.write_text(yaml.dump({"firms": [
        {"firm_id": "aecom", "name": "AECOM"},
        {"firm_id": "jacobs", "name": "Jacobs"},
    ]}))
    result = _load_approved_firm_ids(p)
    assert result == frozenset({"aecom", "jacobs"})


def test_load_approved_ids_missing_file_returns_empty():
    result = _load_approved_firm_ids("/nonexistent/path/firms.yaml")
    assert result == frozenset()


def test_load_approved_ids_skips_entries_without_firm_id(tmp_path):
    p = tmp_path / "firms.yaml"
    p.write_text(yaml.dump({"firms": [
        {"firm_id": "aecom", "name": "AECOM"},
        {"name": "No ID Firm"},
    ]}))
    result = _load_approved_firm_ids(p)
    assert result == frozenset({"aecom"})


# ── Group C: discover_missing_firms — core logic ──────────────────────────────

def test_discover_empty_database_returns_empty(test_db, empty_firms_yaml):
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    assert result == []


def test_discover_returns_candidate_for_unknown_company(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    assert len(result) == 1
    assert result[0].company == "Stantec"


def test_discover_suggests_correct_slug(test_db, empty_firms_yaml):
    insert_job(test_db, "HDR, Inc.")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    assert any(c.suggested_firm_id == "hdr_inc" for c in result)


def test_discover_excludes_company_matching_approved_firm_id(test_db, tmp_path):
    insert_job(test_db, "AECOM")
    config = make_firms_yaml(tmp_path, ["aecom"])
    result = discover_missing_firms(config_path=config, db_path=test_db)
    assert not any(c.company == "AECOM" for c in result)


def test_discover_includes_company_not_matching_any_approved_id(test_db, tmp_path):
    insert_job(test_db, "Stantec")
    insert_job(test_db, "AECOM")
    config = make_firms_yaml(tmp_path, ["aecom"])
    result = discover_missing_firms(config_path=config, db_path=test_db)
    companies = [c.company for c in result]
    assert "Stantec" in companies
    assert "AECOM" not in companies


def test_discover_aggregates_job_count(test_db, empty_firms_yaml):
    for _ in range(4):
        insert_job(test_db, "Jacobs")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    jacobs = next(c for c in result if c.company == "Jacobs")
    assert jacobs.job_count == 4


def test_discover_aggregates_sources(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec", source="adzuna")
    insert_job(test_db, "Stantec", source="usajobs")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    stantec = next(c for c in result if c.company == "Stantec")
    assert sorted(stantec.sources) == ["adzuna", "usajobs"]


def test_discover_deduplicates_same_source(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec", source="adzuna")
    insert_job(test_db, "Stantec", source="adzuna")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    stantec = next(c for c in result if c.company == "Stantec")
    assert stantec.sources == ["adzuna"]


def test_discover_includes_sample_urls(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec", apply_url="https://stantec.com/job/1")
    insert_job(test_db, "Stantec", apply_url="https://stantec.com/job/2")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    stantec = next(c for c in result if c.company == "Stantec")
    assert len(stantec.sample_urls) == 2
    assert "https://stantec.com/job/1" in stantec.sample_urls


def test_discover_caps_sample_urls_at_three(test_db, empty_firms_yaml):
    for i in range(5):
        insert_job(test_db, "Stantec", apply_url=f"https://stantec.com/job/{i}")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    stantec = next(c for c in result if c.company == "Stantec")
    assert len(stantec.sample_urls) == 3


def test_discover_handles_null_apply_url(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec", apply_url=None)
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    stantec = next(c for c in result if c.company == "Stantec")
    assert stantec.sample_urls == []


def test_discover_min_jobs_filter(test_db, empty_firms_yaml):
    insert_job(test_db, "Small Firm")
    for _ in range(3):
        insert_job(test_db, "Big Firm")
    result = discover_missing_firms(min_jobs=2, config_path=empty_firms_yaml, db_path=test_db)
    companies = [c.company for c in result]
    assert "Big Firm" in companies
    assert "Small Firm" not in companies


def test_discover_source_filter(test_db, empty_firms_yaml):
    insert_job(test_db, "Firm A", source="adzuna")
    insert_job(test_db, "Firm B", source="usajobs")
    result = discover_missing_firms(source_filter="adzuna", config_path=empty_firms_yaml, db_path=test_db)
    companies = [c.company for c in result]
    assert "Firm A" in companies
    assert "Firm B" not in companies


def test_discover_sorted_by_descending_job_count(test_db, empty_firms_yaml):
    for _ in range(5):
        insert_job(test_db, "High Count Firm")
    insert_job(test_db, "Low Count Firm")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    assert result[0].company == "High Count Firm"
    assert result[1].company == "Low Count Firm"


def test_discover_sorted_alpha_for_equal_count(test_db, empty_firms_yaml):
    for name in ("Zeta Corp", "Alpha Corp", "Beta Corp"):
        insert_job(test_db, name)
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    names = [c.company for c in result]
    assert names == sorted(names, key=str.lower)


def test_discover_returns_firm_candidate_instances(test_db, empty_firms_yaml):
    insert_job(test_db, "Stantec")
    result = discover_missing_firms(config_path=empty_firms_yaml, db_path=test_db)
    assert all(isinstance(c, FirmCandidate) for c in result)


def test_discover_missing_config_file_treats_all_as_unknown(test_db):
    """Missing firms.yaml → no approved ids → all companies are candidates."""
    insert_job(test_db, "Stantec")
    result = discover_missing_firms(
        config_path="/nonexistent/firms.yaml",
        db_path=test_db,
    )
    assert any(c.company == "Stantec" for c in result)


def test_discover_alias_limitation_documented(test_db, tmp_path):
    """A company approved under a different slug still surfaces as a candidate (known MVP gap)."""
    # firm_id in registry is "aecom"; company in DB is "AECOM Technical Services"
    # slug("AECOM Technical Services") = "aecom_technical_services" ≠ "aecom"
    insert_job(test_db, "AECOM Technical Services")
    config = make_firms_yaml(tmp_path, ["aecom"])
    result = discover_missing_firms(config_path=config, db_path=test_db)
    # Expected MVP behavior: candidate appears because slugs don't match
    assert any(c.company == "AECOM Technical Services" for c in result)


# ── Group D: CLI — jsa firms discover ────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_firms_discover_empty_db(test_db, empty_firms_yaml, monkeypatch, runner):
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "discover", "--config", empty_firms_yaml])
    assert result.exit_code == 0
    assert "No missing firms" in result.output


def test_cli_firms_discover_shows_candidate(test_db, empty_firms_yaml, monkeypatch, runner):
    insert_job(test_db, "Stantec", apply_url="https://stantec.com/jobs/1")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "discover", "--config", empty_firms_yaml])
    assert result.exit_code == 0
    assert "Stantec" in result.output
    assert "stantec" in result.output  # suggested firm_id


def test_cli_firms_discover_min_jobs_flag(test_db, empty_firms_yaml, monkeypatch, runner):
    insert_job(test_db, "Rare Firm")
    for _ in range(3):
        insert_job(test_db, "Common Firm")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "discover", "--min-jobs", "2", "--config", empty_firms_yaml])
    assert result.exit_code == 0
    assert "Common Firm" in result.output
    assert "Rare Firm" not in result.output


def test_cli_firms_discover_out_writes_tsv(test_db, empty_firms_yaml, tmp_path, monkeypatch, runner):
    insert_job(test_db, "Stantec")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    out_path = str(tmp_path / "candidates.tsv")
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "discover", "--config", empty_firms_yaml, "--out", out_path])
    assert result.exit_code == 0
    content = Path(out_path).read_text(encoding="utf-8")
    assert "company" in content  # header
    assert "Stantec" in content


def test_cli_firms_discover_excludes_approved(test_db, tmp_path, monkeypatch, runner):
    insert_job(test_db, "AECOM")
    config = make_firms_yaml(tmp_path, ["aecom"])
    monkeypatch.setattr("job_search.config.settings.DB_PATH", test_db)
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "discover", "--config", str(config)])
    assert result.exit_code == 0
    # AECOM is approved → should not appear
    assert "No missing firms" in result.output


def test_cli_firms_group_exists(runner):
    """The 'firms' subgroup must be registered under 'jsa'."""
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "--help"])
    assert result.exit_code == 0
    assert "discover" in result.output


def test_cli_discover_firm_flat_command_still_works(runner):
    """Existing 'jsa discover-firm' flat command must remain registered (backward compat)."""
    from job_search.cli import cli
    result = runner.invoke(cli, ["discover-firm", "--help"])
    assert result.exit_code == 0
