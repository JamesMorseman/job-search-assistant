"""Tests for Phase 3 Step 2: draft firm profile storage (repository.py)."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from job_search.firms.repository import (
    DRAFTS_DIR,
    draft_path,
    list_drafts,
    read_draft,
    write_draft,
)
from job_search.models import (
    DraftFirmProfile,
    DraftStatus,
    FirmBenefit,
    FirmBenefitStatus,
    FirmProfile,
    FirmTrajectoryPrior,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_draft(**kwargs) -> DraftFirmProfile:
    defaults = dict(firm_id="aecom", name="AECOM")
    defaults.update(kwargs)
    return DraftFirmProfile(**defaults)


def make_full_draft() -> DraftFirmProfile:
    return DraftFirmProfile(
        firm_id="stantec",
        name="Stantec",
        generated_at="2026-06-13T10:00:00",
        generator_version="firm-drafter-v1",
        benefits={
            "tuition_reimbursement": FirmBenefit(
                status="confirmed",
                confidence=0.9,
                source_url="https://stantec.com/careers",
                source_type="careers_page",
                last_verified="2026-06-13",
                extraction_note="Careers page confirms tuition support.",
            ),
            "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.6),
        },
        trajectory={
            "eit_pe_path": FirmTrajectoryPrior(status="likely", confidence=0.7),
            "internal_mobility": FirmTrajectoryPrior(status="unknown", confidence=0.0),
        },
    )


# ── Group A: draft_path and firm_id validation ────────────────────────────────

def test_draft_path_produces_expected_filename(tmp_path):
    p = draft_path("aecom", drafts_dir=tmp_path)
    assert p == tmp_path / "aecom.yaml"


def test_draft_path_default_dir_is_data_firm_drafts():
    p = draft_path("jacobs")
    assert str(p).endswith("firm_drafts/jacobs.yaml") or str(p).endswith(r"firm_drafts\jacobs.yaml")


def test_draft_path_rejects_path_traversal_dotdot():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("../config/firms")


def test_draft_path_rejects_absolute_path():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("/etc/passwd")


def test_draft_path_rejects_forward_slash():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("foo/bar")


def test_draft_path_rejects_backslash():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("foo\\bar")


def test_draft_path_rejects_empty_string():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("")


def test_draft_path_rejects_uppercase():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("AECOM")


def test_draft_path_accepts_underscores_and_hyphens(tmp_path):
    p = draft_path("golder_associates", tmp_path)
    assert p.name == "golder_associates.yaml"
    p2 = draft_path("ws-atkins", tmp_path)
    assert p2.name == "ws-atkins.yaml"


def test_draft_path_rejects_too_long():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("a" * 41)


def test_draft_path_rejects_space():
    with pytest.raises(ValueError, match="Invalid firm_id"):
        draft_path("aecom inc")


# ── Group B: write_draft ──────────────────────────────────────────────────────

def test_write_draft_creates_file(tmp_path):
    profile = make_draft()
    path = write_draft(profile, drafts_dir=tmp_path)
    assert path.exists()
    assert path.name == "aecom.yaml"


def test_write_draft_creates_directory_if_missing(tmp_path):
    subdir = tmp_path / "nested" / "drafts"
    profile = make_draft()
    path = write_draft(profile, drafts_dir=subdir)
    assert path.exists()


def test_write_draft_returns_path(tmp_path):
    profile = make_draft()
    returned = write_draft(profile, drafts_dir=tmp_path)
    assert returned == tmp_path / "aecom.yaml"


def test_write_draft_yaml_is_safe_loadable(tmp_path):
    """Written YAML must be parseable by yaml.safe_load (no Python-specific tags)."""
    profile = make_full_draft()
    path = write_draft(profile, drafts_dir=tmp_path)
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    assert isinstance(raw, dict)
    assert raw["firm_id"] == "stantec"


def test_write_draft_enum_values_are_strings(tmp_path):
    """Enum fields must serialize as plain strings, not Python objects."""
    profile = make_full_draft()
    path = write_draft(profile, drafts_dir=tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "!!python" not in content
    assert "pending_review" in content
    assert "confirmed" in content


def test_write_draft_contains_draft_status(tmp_path):
    profile = make_draft()
    path = write_draft(profile, drafts_dir=tmp_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw["draft_status"] == "pending_review"


def test_write_draft_overwrites_existing(tmp_path):
    profile_v1 = make_draft(generator_version="v1")
    write_draft(profile_v1, drafts_dir=tmp_path)
    profile_v2 = make_draft(generator_version="v2")
    write_draft(profile_v2, drafts_dir=tmp_path)
    raw = yaml.safe_load((tmp_path / "aecom.yaml").read_text(encoding="utf-8"))
    assert raw["generator_version"] == "v2"


# ── Group C: read_draft ───────────────────────────────────────────────────────

def test_read_draft_returns_draft_firm_profile(tmp_path):
    profile = make_draft()
    write_draft(profile, drafts_dir=tmp_path)
    result = read_draft("aecom", drafts_dir=tmp_path)
    assert isinstance(result, DraftFirmProfile)


def test_read_draft_missing_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="No draft found"):
        read_draft("nobody", drafts_dir=tmp_path)


def test_read_draft_rejects_invalid_firm_id(tmp_path):
    with pytest.raises(ValueError, match="Invalid firm_id"):
        read_draft("../evil", drafts_dir=tmp_path)


# ── Group D: YAML round-trip ──────────────────────────────────────────────────

def test_write_read_round_trip_minimal(tmp_path):
    profile = make_draft(name="AECOM", aliases=["AECOM Technical Services"])
    write_draft(profile, drafts_dir=tmp_path)
    result = read_draft("aecom", drafts_dir=tmp_path)
    assert result.firm_id == "aecom"
    assert result.name == "AECOM"
    assert result.aliases == ["AECOM Technical Services"]
    assert result.draft_status == DraftStatus.PENDING_REVIEW


def test_write_read_round_trip_full(tmp_path):
    profile = make_full_draft()
    write_draft(profile, drafts_dir=tmp_path)
    result = read_draft("stantec", drafts_dir=tmp_path)
    assert result.firm_id == "stantec"
    assert result.generator_version == "firm-drafter-v1"
    # Benefit fields survive round-trip
    benefit = result.benefits["tuition_reimbursement"]
    assert benefit.status == FirmBenefitStatus.CONFIRMED
    assert benefit.confidence == 0.9
    assert benefit.source_url == "https://stantec.com/careers"
    assert benefit.last_verified == "2026-06-13"
    assert benefit.extraction_note == "Careers page confirms tuition support."
    # Trajectory fields survive round-trip
    traj = result.trajectory["internal_mobility"]
    assert traj.status == FirmBenefitStatus.UNKNOWN
    assert traj.confidence == 0.0


def test_write_read_round_trip_review_metadata(tmp_path):
    from job_search.models import DraftEvidenceSummary, DraftReview
    profile = DraftFirmProfile(
        firm_id="jacobs",
        name="Jacobs",
        generated_at="2026-06-13T09:00:00",
        review=DraftReview(reviewer_notes=["Check PE support claim."]),
        evidence_summary=DraftEvidenceSummary(
            source_urls=["https://jacobs.com/careers"],
            extraction_notes=["Seen in 3 entry-level postings."],
        ),
    )
    write_draft(profile, drafts_dir=tmp_path)
    result = read_draft("jacobs", drafts_dir=tmp_path)
    assert result.review.reviewer_notes == ["Check PE support claim."]
    assert result.evidence_summary.source_urls == ["https://jacobs.com/careers"]
    assert result.generated_at == "2026-06-13T09:00:00"


# ── Group E: list_drafts ──────────────────────────────────────────────────────

def test_list_drafts_empty_dir(tmp_path):
    assert list_drafts(drafts_dir=tmp_path) == []


def test_list_drafts_missing_dir(tmp_path):
    missing = tmp_path / "nonexistent"
    assert list_drafts(drafts_dir=missing) == []


def test_list_drafts_returns_sorted_firm_ids(tmp_path):
    for firm_id in ("stantec", "aecom", "jacobs"):
        write_draft(make_draft(firm_id=firm_id, name=firm_id.title()), drafts_dir=tmp_path)
    result = list_drafts(drafts_dir=tmp_path)
    assert result == ["aecom", "jacobs", "stantec"]


def test_list_drafts_ignores_non_yaml_files(tmp_path):
    write_draft(make_draft(), drafts_dir=tmp_path)
    (tmp_path / "notes.txt").write_text("not a draft")
    (tmp_path / ".gitkeep").write_text("")
    result = list_drafts(drafts_dir=tmp_path)
    assert result == ["aecom"]


# ── Group F: Draft isolation from approved firm loading ───────────────────────

def test_draft_yaml_cannot_load_as_firm_profile(tmp_path):
    """A draft YAML must fail FirmProfile validation (missing approval field)."""
    profile = make_full_draft()
    path = write_draft(profile, drafts_dir=tmp_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    with pytest.raises((ValidationError, TypeError)):
        FirmProfile(**raw)


def test_ingestor_does_not_load_drafts(tmp_path):
    """Ingestor.load_firms() reads config/firms.yaml only — drafts must not appear."""
    # Write a draft to a temp drafts directory
    write_draft(make_full_draft(), drafts_dir=tmp_path / "firm_drafts")
    # Write an empty approved firms yaml
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text("firms: []\n")
    from job_search.ingestion.ingestor import Ingestor
    ingestor = Ingestor(dry_run=True)
    ingestor.load_firms(str(firms_yaml))
    assert ingestor._firms == []


def test_approved_firms_yaml_unaffected_by_draft_writes(tmp_path):
    """Writing a draft must not modify config/firms.yaml."""
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text("firms: []\n")
    original_content = firms_yaml.read_text()
    write_draft(make_full_draft(), drafts_dir=tmp_path / "drafts")
    assert firms_yaml.read_text() == original_content


def test_draft_status_field_absent_from_firm_profile():
    """FirmProfile has no draft_status attribute — the types are structurally distinct."""
    from job_search.models import FirmApproval
    p = FirmProfile(
        firm_id="test",
        name="Test",
        approval=FirmApproval(approved_at="2026-06-13", approved_by="james", last_verified="2026-06-13"),
    )
    assert not hasattr(p, "draft_status")


def test_draft_firm_profile_has_no_approval_field():
    """DraftFirmProfile has no approval attribute — it cannot masquerade as approved."""
    d = make_draft()
    assert not hasattr(d, "approval")


# ── Group G: DRAFTS_DIR constant ──────────────────────────────────────────────

def test_drafts_dir_constant_is_path():
    assert isinstance(DRAFTS_DIR, Path)


def test_drafts_dir_constant_points_to_data_firm_drafts():
    assert DRAFTS_DIR == Path("data/firm_drafts")
