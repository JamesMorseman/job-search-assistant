"""Tests for Phase 3 Step 1: firm repository Pydantic models and vocab validation."""

import yaml
import pytest
from pydantic import ValidationError

from job_search.models import (
    FIRM_BENEFIT_KEYS,
    FIRM_TRAJECTORY_KEYS,
    ATSType,
    ATSTier,
    DraftEvidenceSummary,
    DraftFirmProfile,
    DraftReview,
    DraftStatus,
    FirmApproval,
    FirmATS,
    FirmBenefit,
    FirmBenefitStatus,
    FirmConfig,
    FirmNotes,
    FirmPriority,
    FirmProfile,
    FirmProfileMeta,
    FirmSourceType,
    FirmTrajectoryPrior,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_approval(**kwargs) -> FirmApproval:
    defaults = dict(approved_at="2026-06-13", approved_by="james", last_verified="2026-06-13")
    defaults.update(kwargs)
    return FirmApproval(**defaults)


def make_firm_profile(**kwargs) -> FirmProfile:
    defaults = dict(
        firm_id="aecom",
        name="AECOM",
        approval=make_approval(),
    )
    defaults.update(kwargs)
    return FirmProfile(**defaults)


def make_draft_profile(**kwargs) -> DraftFirmProfile:
    defaults = dict(firm_id="aecom", name="AECOM")
    defaults.update(kwargs)
    return DraftFirmProfile(**defaults)


# ── Group A: Controlled vocabulary constants ──────────────────────────────────

def test_firm_benefit_keys_contains_expected_keys():
    assert "tuition_reimbursement" in FIRM_BENEFIT_KEYS
    assert "pe_exam_reimbursement" in FIRM_BENEFIT_KEYS
    assert "internal_mobility" not in FIRM_BENEFIT_KEYS  # trajectory, not benefit


def test_firm_trajectory_keys_contains_internal_mobility():
    assert "internal_mobility" in FIRM_TRAJECTORY_KEYS


def test_firm_trajectory_keys_does_not_contain_rotation_or_growth():
    assert "rotation_or_growth" not in FIRM_TRAJECTORY_KEYS


def test_firm_benefit_keys_count():
    assert len(FIRM_BENEFIT_KEYS) == 11


def test_firm_trajectory_keys_count():
    assert len(FIRM_TRAJECTORY_KEYS) == 10


# ── Group B: FirmBenefit validation ──────────────────────────────────────────

def test_firm_benefit_default_status_unknown():
    b = FirmBenefit()
    assert b.status == FirmBenefitStatus.UNKNOWN


def test_firm_benefit_status_confirmed():
    b = FirmBenefit(status="confirmed", confidence=0.9)
    assert b.status == FirmBenefitStatus.CONFIRMED
    assert b.confidence == 0.9


def test_firm_benefit_status_not_offered():
    b = FirmBenefit(status="not_offered", confidence=1.0)
    assert b.status == FirmBenefitStatus.NOT_OFFERED


def test_firm_benefit_invalid_status_raises():
    with pytest.raises(ValidationError):
        FirmBenefit(status="maybe")


def test_firm_benefit_confidence_clamped_above_one():
    b = FirmBenefit(confidence=1.5)
    assert b.confidence == 1.0


def test_firm_benefit_confidence_clamped_below_zero():
    b = FirmBenefit(confidence=-0.3)
    assert b.confidence == 0.0


def test_firm_benefit_optional_fields_default_none():
    b = FirmBenefit()
    assert b.source_url is None
    assert b.last_verified is None
    assert b.extraction_note is None


def test_firm_benefit_source_type_careers_page():
    b = FirmBenefit(source_type="careers_page")
    assert b.source_type == FirmSourceType.CAREERS_PAGE


def test_firm_benefit_invalid_source_type_raises():
    with pytest.raises(ValidationError):
        FirmBenefit(source_type="reddit")


# ── Group C: FirmTrajectoryPrior validation ───────────────────────────────────

def test_firm_trajectory_prior_default_unknown():
    t = FirmTrajectoryPrior()
    assert t.status == FirmBenefitStatus.UNKNOWN
    assert t.confidence == 0.0
    assert t.rating is None


def test_firm_trajectory_prior_rating_field():
    t = FirmTrajectoryPrior(status="confirmed", confidence=0.8, rating="high")
    assert t.rating == "high"


def test_firm_trajectory_prior_confidence_clamped():
    t = FirmTrajectoryPrior(confidence=2.5)
    assert t.confidence == 1.0


# ── Group D: FirmProfile validation ──────────────────────────────────────────

def test_firm_profile_minimal_valid():
    p = make_firm_profile()
    assert p.firm_id == "aecom"
    assert p.name == "AECOM"
    assert p.manual_priority == FirmPriority.NEUTRAL
    assert isinstance(p.approval, FirmApproval)


def test_firm_profile_requires_approval():
    with pytest.raises((ValidationError, TypeError)):
        FirmProfile(firm_id="acme", name="Acme")


def test_firm_profile_defaults_empty_dicts():
    p = make_firm_profile()
    assert p.benefits == {}
    assert p.trajectory == {}
    assert p.aliases == []


def test_firm_profile_valid_benefit_keys():
    p = make_firm_profile(
        benefits={
            "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=0.9),
            "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.6),
        }
    )
    assert "tuition_reimbursement" in p.benefits
    assert "pe_exam_reimbursement" in p.benefits


def test_firm_profile_invalid_benefit_key_raises():
    with pytest.raises(ValidationError, match="Unknown benefit key"):
        make_firm_profile(
            benefits={"free_snacks": FirmBenefit(status="confirmed", confidence=1.0)}
        )


def test_firm_profile_valid_trajectory_internal_mobility():
    p = make_firm_profile(
        trajectory={"internal_mobility": FirmTrajectoryPrior(status="likely", confidence=0.7)}
    )
    assert "internal_mobility" in p.trajectory


def test_firm_profile_invalid_trajectory_key_raises():
    with pytest.raises(ValidationError, match="Unknown trajectory key"):
        make_firm_profile(
            trajectory={"rotation_or_growth": FirmTrajectoryPrior(status="likely", confidence=0.5)}
        )


def test_firm_profile_invalid_old_rotation_key_rejected():
    """Explicitly confirm the old Phase 2.1 key is not valid in firm profiles."""
    with pytest.raises(ValidationError):
        make_firm_profile(
            trajectory={"rotation_or_growth": FirmTrajectoryPrior()}
        )


def test_firm_profile_all_trajectory_keys_valid():
    traj = {key: FirmTrajectoryPrior() for key in FIRM_TRAJECTORY_KEYS}
    p = make_firm_profile(trajectory=traj)
    assert len(p.trajectory) == len(FIRM_TRAJECTORY_KEYS)


def test_firm_profile_all_benefit_keys_valid():
    benefits = {key: FirmBenefit() for key in FIRM_BENEFIT_KEYS}
    p = make_firm_profile(benefits=benefits)
    assert len(p.benefits) == len(FIRM_BENEFIT_KEYS)


def test_firm_profile_ats_defaults():
    p = make_firm_profile()
    assert p.ats.type == ATSType.UNKNOWN
    assert p.ats.tier == ATSTier.UNKNOWN


def test_firm_profile_ats_workday():
    p = make_firm_profile(
        ats=FirmATS(type=ATSType.WORKDAY, tier=ATSTier.YELLOW, tenant="aecom", site="AECOM_Jobs")
    )
    assert p.ats.type == ATSType.WORKDAY
    assert p.ats.tenant == "aecom"


def test_firm_profile_manual_priority_target():
    p = make_firm_profile(manual_priority="target")
    assert p.manual_priority == FirmPriority.TARGET


def test_firm_profile_invalid_priority_raises():
    with pytest.raises(ValidationError):
        make_firm_profile(manual_priority="maybe")


# ── Group E: DraftFirmProfile validation ─────────────────────────────────────

def test_draft_profile_default_status_pending_review():
    d = make_draft_profile()
    assert d.draft_status == DraftStatus.PENDING_REVIEW


def test_draft_profile_is_not_firm_profile():
    d = make_draft_profile()
    assert not isinstance(d, FirmProfile)


def test_draft_profile_does_not_require_approval():
    d = DraftFirmProfile(firm_id="test", name="Test Corp")
    assert d.review.approved is False
    assert d.review.approved_at is None


def test_draft_profile_invalid_benefit_key_raises():
    with pytest.raises(ValidationError, match="Unknown benefit key"):
        make_draft_profile(
            benefits={"lottery_tickets": FirmBenefit(status="confirmed", confidence=1.0)}
        )


def test_draft_profile_invalid_trajectory_key_raises():
    with pytest.raises(ValidationError, match="Unknown trajectory key"):
        make_draft_profile(
            trajectory={"rotation_or_growth": FirmTrajectoryPrior(status="likely", confidence=0.5)}
        )


def test_draft_profile_valid_trajectory_internal_mobility():
    d = make_draft_profile(
        trajectory={"internal_mobility": FirmTrajectoryPrior(status="likely", confidence=0.7)}
    )
    assert "internal_mobility" in d.trajectory


def test_draft_profile_evidence_summary_defaults():
    d = make_draft_profile()
    assert d.evidence_summary.source_urls == []
    assert d.evidence_summary.extraction_notes == []


def test_draft_profile_review_notes_accumulate():
    d = make_draft_profile(
        review=DraftReview(reviewer_notes=["Verified PE support on careers page."])
    )
    assert len(d.review.reviewer_notes) == 1


def test_draft_profile_rejected_status():
    d = make_draft_profile(draft_status="rejected")
    assert d.draft_status == DraftStatus.REJECTED


# ── Group F: YAML round-trip ──────────────────────────────────────────────────

def test_firm_profile_yaml_round_trip():
    p = FirmProfile(
        firm_id="stantec",
        name="Stantec",
        aliases=["Stantec Consulting"],
        website="https://stantec.com",
        ats=FirmATS(type=ATSType.WORKDAY, tier=ATSTier.YELLOW, tenant="stantec"),
        profile=FirmProfileMeta(enr_rank=12, disciplines=["structural", "transportation"]),
        benefits={
            "tuition_reimbursement": FirmBenefit(
                status="confirmed", confidence=0.9,
                source_url="https://stantec.com/careers",
                source_type="careers_page",
                last_verified="2026-06-13",
            )
        },
        trajectory={
            "eit_pe_path": FirmTrajectoryPrior(status="likely", confidence=0.7),
            "internal_mobility": FirmTrajectoryPrior(status="unknown", confidence=0.0),
        },
        manual_priority="watch",
        approval=FirmApproval(approved_at="2026-06-13", approved_by="james", last_verified="2026-06-13"),
    )
    serialized = yaml.dump(p.model_dump(mode="json"), default_flow_style=False)
    raw = yaml.safe_load(serialized)
    p2 = FirmProfile(**raw)
    assert p2.firm_id == "stantec"
    assert p2.benefits["tuition_reimbursement"].status == FirmBenefitStatus.CONFIRMED
    assert p2.trajectory["internal_mobility"].status == FirmBenefitStatus.UNKNOWN
    assert p2.approval.approved_by == "james"


def test_draft_profile_yaml_round_trip():
    d = DraftFirmProfile(
        firm_id="jacobs",
        name="Jacobs Engineering",
        generated_at="2026-06-13T10:00:00",
        generator_version="firm-drafter-v1",
        evidence_summary=DraftEvidenceSummary(
            source_urls=["https://jacobs.com/careers"],
            extraction_notes=["PE support mentioned in entry-level postings."],
        ),
        benefits={
            "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.6)
        },
    )
    serialized = yaml.dump(d.model_dump(mode="json"), default_flow_style=False)
    raw = yaml.safe_load(serialized)
    d2 = DraftFirmProfile(**raw)
    assert d2.draft_status == DraftStatus.PENDING_REVIEW
    assert d2.benefits["pe_exam_reimbursement"].status == FirmBenefitStatus.LIKELY


# ── Group G: Empty firms.yaml compatibility ───────────────────────────────────

def test_empty_firms_yaml_loads_as_empty_list():
    raw = yaml.safe_load("firms: []") or {}
    firms = raw.get("firms", [])
    assert firms == []


def test_ingestor_load_firms_empty_yaml(tmp_path):
    """Ingestor.load_firms() must not crash on firms: []."""
    yaml_file = tmp_path / "firms.yaml"
    yaml_file.write_text("firms: []\n")
    from job_search.ingestion.ingestor import Ingestor
    ingestor = Ingestor(dry_run=True)
    ingestor.load_firms(str(yaml_file))
    assert ingestor._firms == []


# ── Group H: FirmConfig backward compatibility ────────────────────────────────

def test_firm_config_still_loads():
    """FirmConfig (legacy ATS model) must remain functional."""
    fc = FirmConfig(
        firm_id="aecom",
        name="AECOM",
        ats_type=ATSType.WORKDAY,
        ats_tier=ATSTier.YELLOW,
        ats_tenant="aecom",
        ats_site="AECOM_Jobs",
    )
    assert fc.firm_id == "aecom"
    assert fc.tuition_reimbursement is False


def test_firm_config_does_not_have_approval():
    """FirmConfig must not require approval — it is the legacy ATS config model."""
    fc = FirmConfig(firm_id="test", name="Test")
    assert not hasattr(fc, "approval")
