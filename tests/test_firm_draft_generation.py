"""Tests for Phase 3 Step 6: Skeleton Draft Generation."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from job_search.firms.repository import (
    DraftExistsError,
    _company_to_firm_id,
    create_draft,
    draft_path,
    list_drafts,
    read_draft,
    write_draft,
)
from job_search.models import DraftFirmProfile, DraftStatus


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


# ── Group A: _company_to_firm_id slug generation ──────────────────────────────

def test_slug_from_simple_name():
    assert _company_to_firm_id("Stantec") == "stantec"


def test_slug_lowercases_all():
    assert _company_to_firm_id("AECOM") == "aecom"


def test_slug_replaces_spaces():
    assert _company_to_firm_id("HDR Engineering") == "hdr_engineering"


def test_slug_collapses_punctuation():
    assert _company_to_firm_id("WSP, Inc.") == "wsp_inc"


def test_slug_strips_leading_trailing_underscores():
    assert _company_to_firm_id(" RS&H ") == "rs_h"


def test_slug_truncates_at_40():
    assert len(_company_to_firm_id("A" * 60)) == 40


def test_slug_empty_string_returns_unknown():
    assert _company_to_firm_id("") == "unknown"


def test_slug_punctuation_only_returns_unknown():
    assert _company_to_firm_id("!!!---") == "unknown"


def test_slug_preserves_digits():
    assert _company_to_firm_id("3XN Architects") == "3xn_architects"


def test_slug_consecutive_separators_collapse():
    assert _company_to_firm_id("Foo & Bar, LLC") == "foo_bar_llc"


# ── Group B: create_draft — core behavior ─────────────────────────────────────

def test_create_draft_returns_draft_and_path(tmp_path):
    draft, path = create_draft("Stantec", drafts_dir=tmp_path)
    assert isinstance(draft, DraftFirmProfile)
    assert isinstance(path, Path)


def test_create_draft_derives_firm_id_from_name(tmp_path):
    draft, _ = create_draft("HDR Engineering", drafts_dir=tmp_path)
    assert draft.firm_id == "hdr_engineering"


def test_create_draft_uses_explicit_firm_id(tmp_path):
    draft, _ = create_draft("HDR Engineering", firm_id="hdr", drafts_dir=tmp_path)
    assert draft.firm_id == "hdr"


def test_create_draft_preserves_company_name(tmp_path):
    draft, _ = create_draft("Stantec Consulting Ltd.", drafts_dir=tmp_path)
    assert draft.name == "Stantec Consulting Ltd."


def test_create_draft_status_is_pending_review(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.draft_status == DraftStatus.PENDING_REVIEW


def test_create_draft_generated_at_is_today(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.generated_at == date.today().isoformat()


def test_create_draft_generator_version_is_skeleton(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.generator_version == "skeleton-v1"


def test_create_draft_benefits_empty_by_default(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.benefits == {}


def test_create_draft_trajectory_empty_by_default(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.trajectory == {}


def test_create_draft_sets_website(tmp_path):
    draft, _ = create_draft("Stantec", website="https://stantec.com", drafts_dir=tmp_path)
    assert draft.website == "https://stantec.com"


def test_create_draft_sets_careers_url(tmp_path):
    draft, _ = create_draft("Stantec", careers_url="https://stantec.com/careers",
                             drafts_dir=tmp_path)
    assert draft.careers_url == "https://stantec.com/careers"


def test_create_draft_website_defaults_to_none(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.website is None


def test_create_draft_review_not_approved(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.review.approved is False
    assert draft.review.approved_by is None


def test_create_draft_evidence_summary_empty(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    assert draft.evidence_summary.source_urls == []
    assert draft.evidence_summary.extraction_notes == []


# ── Group C: YAML output ──────────────────────────────────────────────────────

def test_create_draft_writes_yaml_file(tmp_path):
    _, path = create_draft("Stantec", drafts_dir=tmp_path)
    assert path.exists()


def test_create_draft_yaml_path_uses_firm_id(tmp_path):
    _, path = create_draft("HDR Engineering", drafts_dir=tmp_path)
    assert path.name == "hdr_engineering.yaml"


def test_create_draft_yaml_is_safe_loadable(tmp_path):
    _, path = create_draft("Stantec", drafts_dir=tmp_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    assert raw["firm_id"] == "stantec"


def test_create_draft_yaml_no_python_tags(tmp_path):
    _, path = create_draft("Stantec", drafts_dir=tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "!!python" not in content
    assert "tag:yaml.org" not in content


def test_create_draft_roundtrips_via_read_draft(tmp_path):
    draft, _ = create_draft("Stantec", drafts_dir=tmp_path)
    loaded = read_draft("stantec", drafts_dir=tmp_path)
    assert loaded.firm_id == draft.firm_id
    assert loaded.name == draft.name
    assert loaded.draft_status == draft.draft_status
    assert loaded.generated_at == draft.generated_at


def test_create_draft_appears_in_list_drafts(tmp_path):
    create_draft("Stantec", drafts_dir=tmp_path)
    assert "stantec" in list_drafts(drafts_dir=tmp_path)


# ── Group D: overwrite protection ────────────────────────────────────────────

def test_create_draft_raises_if_draft_exists(tmp_path):
    create_draft("Stantec", drafts_dir=tmp_path)
    with pytest.raises(DraftExistsError):
        create_draft("Stantec", drafts_dir=tmp_path)


def test_create_draft_force_overwrites(tmp_path):
    create_draft("Stantec", drafts_dir=tmp_path)
    draft, _ = create_draft("Stantec Revised", firm_id="stantec",
                             drafts_dir=tmp_path, force=True)
    assert draft.name == "Stantec Revised"
    loaded = read_draft("stantec", drafts_dir=tmp_path)
    assert loaded.name == "Stantec Revised"


def test_create_draft_no_force_preserves_original(tmp_path):
    create_draft("Stantec", drafts_dir=tmp_path)
    with pytest.raises(DraftExistsError):
        create_draft("Stantec Revised", firm_id="stantec", drafts_dir=tmp_path)
    # Original unchanged
    loaded = read_draft("stantec", drafts_dir=tmp_path)
    assert loaded.name == "Stantec"


def test_create_draft_force_false_is_default(tmp_path):
    """Default behavior without force= kwarg must also raise on conflict."""
    create_draft("Stantec", drafts_dir=tmp_path)
    with pytest.raises(DraftExistsError):
        create_draft("Stantec", drafts_dir=tmp_path)


# ── Group E: error cases ──────────────────────────────────────────────────────

def test_create_draft_invalid_explicit_firm_id(tmp_path):
    with pytest.raises(ValueError):
        create_draft("Bad Firm", firm_id="../evil", drafts_dir=tmp_path)


def test_create_draft_invalid_firm_id_uppercase(tmp_path):
    with pytest.raises(ValueError):
        create_draft("Bad Firm", firm_id="BadFirm", drafts_dir=tmp_path)


def test_create_draft_firm_id_with_spaces_invalid(tmp_path):
    with pytest.raises(ValueError):
        create_draft("Bad Firm", firm_id="bad firm", drafts_dir=tmp_path)


def test_create_draft_empty_company_name_slug_is_unknown(tmp_path):
    # "!!!" maps to slug "unknown" — valid firm_id
    draft, _ = create_draft("!!!", drafts_dir=tmp_path)
    assert draft.firm_id == "unknown"


# ── Group F: CLI — jsa firms draft ───────────────────────────────────────────

def test_cli_draft_succeeds(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "draft", "Stantec",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code == 0
    assert "stantec" in result.output


def test_cli_draft_creates_file(tmp_path, runner):
    from job_search.cli import cli
    runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    assert (tmp_path / "stantec.yaml").exists()


def test_cli_draft_explicit_firm_id(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "draft", "Stantec Consulting",
        "--firm-id", "stantec_consulting",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code == 0
    assert (tmp_path / "stantec_consulting.yaml").exists()


def test_cli_draft_with_website_and_careers_url(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "draft", "Stantec",
        "--website", "https://stantec.com",
        "--careers-url", "https://stantec.com/careers",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code == 0
    draft = read_draft("stantec", drafts_dir=tmp_path)
    assert draft.website == "https://stantec.com"
    assert draft.careers_url == "https://stantec.com/careers"


def test_cli_draft_fails_if_draft_exists(tmp_path, runner):
    from job_search.cli import cli
    runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    result = runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_draft_force_overwrites(tmp_path, runner):
    from job_search.cli import cli
    runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    result = runner.invoke(cli, [
        "firms", "draft", "Stantec Revised",
        "--firm-id", "stantec",
        "--force",
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code == 0
    loaded = read_draft("stantec", drafts_dir=tmp_path)
    assert loaded.name == "Stantec Revised"


def test_cli_draft_invalid_firm_id_fails(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, [
        "firms", "draft", "Bad Firm",
        "--firm-id", "Bad Firm",  # uppercase + spaces
        "--drafts-dir", str(tmp_path),
    ])
    assert result.exit_code != 0


def test_cli_draft_output_shows_firm_id_and_path(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "draft", "HDR Engineering",
                                 "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "hdr_engineering" in result.output


def test_cli_draft_output_shows_next_steps(tmp_path, runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "review" in result.output.lower()


def test_cli_draft_appears_in_firms_help(runner):
    from job_search.cli import cli
    result = runner.invoke(cli, ["firms", "--help"])
    assert "draft" in result.output


# ── Group G: integration with review command ──────────────────────────────────

def test_draft_then_review_shows_pending(tmp_path, runner):
    from job_search.cli import cli
    runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    result = runner.invoke(cli, ["firms", "review", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "stantec" in result.output
    assert "pending_review" in result.output


def test_draft_then_review_detail_shows_name(tmp_path, runner):
    from job_search.cli import cli
    runner.invoke(cli, ["firms", "draft", "Stantec", "--drafts-dir", str(tmp_path)])
    result = runner.invoke(cli, ["firms", "review", "stantec", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Stantec" in result.output
    assert "stantec" in result.output


def test_multiple_drafts_all_appear_in_review(tmp_path, runner):
    from job_search.cli import cli
    for name in ("Stantec", "AECOM", "Jacobs"):
        runner.invoke(cli, ["firms", "draft", name, "--drafts-dir", str(tmp_path)])
    result = runner.invoke(cli, ["firms", "review", "--drafts-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "stantec" in result.output
    assert "aecom" in result.output
    assert "jacobs" in result.output
