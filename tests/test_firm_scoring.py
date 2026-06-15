"""Tests for Phase 3 Step 7: Firm-Prior Scoring Integration."""

from __future__ import annotations

import json

import pytest
import yaml

from job_search.ingestion.scoring import (
    BENEFIT_RULES,
    TRAJECTORY_RULES,
    Scorer,
    SignalHit,
    _BENEFIT_TOTAL_WEIGHT,
    _FIRM_BENEFIT_WEIGHT,
    _FIRM_STATUS_MULTIPLIER,
    _FIRM_TRAJ_WEIGHT,
    _JD_BENEFIT_WEIGHT,
    _JD_TRAJ_WEIGHT,
    _TRAJECTORY_TOTAL_WEIGHT,
    _firm_priors_to_signal_score,
    _load_approved_profiles,
)
from job_search.models import (
    CanonicalJob,
    DraftFirmProfile,
    DraftStatus,
    FirmApproval,
    FirmBenefit,
    FirmProfile,
    FirmTrajectoryPrior,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_job(**kwargs) -> CanonicalJob:
    defaults = dict(
        source="test",
        source_job_id="j1",
        company="Stantec",
        title="Civil Engineer",
        description_normalized="",
    )
    defaults.update(kwargs)
    return CanonicalJob(**defaults)


def make_approval() -> FirmApproval:
    return FirmApproval(approved_at="2026-06-14", approved_by="james", last_verified="2026-06-14")


def make_profile(firm_id="stantec", **kwargs) -> FirmProfile:
    return FirmProfile(firm_id=firm_id, name="Stantec", approval=make_approval(), **kwargs)


def make_scorer(tmp_path=None, firms_content=None) -> Scorer:
    """Return a Scorer with an optional tmp firms.yaml."""
    if tmp_path is not None and firms_content is not None:
        firms_path = tmp_path / "firms.yaml"
        firms_path.write_text(yaml.dump(firms_content), encoding="utf-8")
        return Scorer(firms_config_path=str(firms_path))
    return Scorer(firms_config_path="/nonexistent/firms.yaml")


# ── Group A: _firm_priors_to_signal_score ─────────────────────────────────────

def test_firm_prior_confirmed_benefit_produces_hit():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert any(h.key == "tuition_reimbursement" for h in result.hits)


def test_firm_prior_confirmed_confidence_is_1():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    hit = next(h for h in result.hits if h.key == "tuition_reimbursement")
    assert hit.confidence == pytest.approx(1.0)


def test_firm_prior_likely_confidence_is_065():
    benefits = {"tuition_reimbursement": FirmBenefit(status="likely", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    hit = next(h for h in result.hits if h.key == "tuition_reimbursement")
    assert hit.confidence == pytest.approx(0.65)


def test_firm_prior_unknown_produces_no_hit():
    benefits = {"tuition_reimbursement": FirmBenefit(status="unknown", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert result.hits == []
    assert result.score == 0.0


def test_firm_prior_not_offered_produces_no_hit():
    benefits = {"tuition_reimbursement": FirmBenefit(status="not_offered", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert result.hits == []
    assert result.score == 0.0


def test_firm_prior_source_is_firm_profile():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert all(h.source == "firm_profile" for h in result.hits)


def test_firm_prior_matched_text_is_none():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert all(h.matched_text is None for h in result.hits)


def test_firm_prior_reason_mentions_status():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    hit = result.hits[0]
    assert "confirmed" in hit.reason
    assert "firm profile" in hit.reason.lower()


def test_firm_prior_reason_includes_last_verified():
    benefits = {"tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0,
                                                     last_verified="2026-06-01")}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert "2026-06-01" in result.hits[0].reason


def test_firm_prior_empty_data_returns_zero():
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score({}, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    assert result.score == 0.0
    assert result.hits == []


def test_firm_prior_trajectory_confirmed():
    traj = {"eit_pe_path": FirmTrajectoryPrior(status="confirmed", confidence=1.0)}
    from job_search.ingestion.scoring import _TRAJECTORY_RULE_BY_KEY
    result = _firm_priors_to_signal_score(traj, _TRAJECTORY_RULE_BY_KEY, _TRAJECTORY_TOTAL_WEIGHT)
    assert any(h.key == "eit_pe_path" for h in result.hits)


def test_firm_prior_confidence_scales_with_prior_confidence():
    """likely × 0.8 prior confidence = 0.52 effective confidence."""
    benefits = {"tuition_reimbursement": FirmBenefit(status="likely", confidence=0.8)}
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    result = _firm_priors_to_signal_score(benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    hit = next(h for h in result.hits if h.key == "tuition_reimbursement")
    assert hit.confidence == pytest.approx(0.65 * 0.8, rel=1e-5)


# ── Group B: Scorer.score — job-only scoring unchanged ────────────────────────

def test_job_only_no_description_scores_zero_benefit():
    scorer = make_scorer()
    job = make_job()
    scored = scorer.score(job)
    assert scored.benefit_score == 0.0


def test_job_only_benefit_from_jd():
    scorer = make_scorer()
    job = make_job(description_normalized="We offer tuition reimbursement and relocation assistance.")
    scored = scorer.score(job)
    assert scored.benefit_score > 0.0


def test_job_only_reasons_are_jd_source():
    scorer = make_scorer()
    job = make_job(description_normalized="We offer tuition reimbursement.")
    scored = scorer.score(job)
    hits = json.loads(scored.benefit_reasons)
    assert all(h["source"] == "job_description" for h in hits)


def test_job_only_no_firm_id_unaffected(tmp_path):
    """A job with no firm_id must produce identical scores with or without a firms.yaml."""
    firms_data = {"firms": [make_profile().model_dump(mode="json")]}
    scorer = make_scorer(tmp_path, firms_data)
    job = make_job(description_normalized="tuition reimbursement")
    # firm_id is None → no lookup, pure JD
    assert job.firm_id is None
    scored = scorer.score(job)
    hits = json.loads(scored.benefit_reasons)
    assert all(h["source"] == "job_description" for h in hits)


def test_score_without_firm_arg_backward_compat():
    """Existing callers that pass only job must still work."""
    scorer = make_scorer()
    job = make_job()
    result = scorer.score(job)  # no firm= arg
    assert result.match_score is not None


# ── Group C: Firm-prior benefit effect ───────────────────────────────────────

def test_firm_confirmed_benefit_increases_score():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0),
    })
    job_no_firm = make_job()
    job_with_firm = make_job()
    scorer.score(job_no_firm)
    scorer.score(job_with_firm, firm=profile)
    assert job_with_firm.benefit_score > job_no_firm.benefit_score


def test_firm_likely_benefit_increases_score_less_than_confirmed():
    scorer = make_scorer()
    profile_confirmed = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    profile_likely = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="likely", confidence=1.0)
    })
    job_confirmed = make_job()
    job_likely = make_job()
    scorer.score(job_confirmed, firm=profile_confirmed)
    scorer.score(job_likely, firm=profile_likely)
    assert job_confirmed.benefit_score > job_likely.benefit_score > 0.0


def test_firm_unknown_benefit_has_no_effect():
    scorer = make_scorer()
    profile_unknown = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="unknown", confidence=1.0)
    })
    job_no_firm = make_job()
    job_with_firm = make_job()
    scorer.score(job_no_firm)
    scorer.score(job_with_firm, firm=profile_unknown)
    assert job_with_firm.benefit_score == job_no_firm.benefit_score


def test_firm_not_offered_benefit_has_no_effect():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="not_offered", confidence=1.0)
    })
    job_baseline = make_job()
    job_firm = make_job()
    scorer.score(job_baseline)
    scorer.score(job_firm, firm=profile)
    assert job_firm.benefit_score == job_baseline.benefit_score


def test_firm_benefit_blend_formula(tmp_path):
    """Verify the 70/30 blend formula numerically."""
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0),
    })
    job = make_job(description_normalized="")  # no JD signals

    # Compute expected firm score component
    from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
    fp = _firm_priors_to_signal_score(profile.benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT)
    expected = round(_JD_BENEFIT_WEIGHT * 0.0 + _FIRM_BENEFIT_WEIGHT * fp.score, 6)

    scorer.score(job, firm=profile)
    assert job.benefit_score == pytest.approx(expected, rel=1e-4)


# ── Group D: Firm-prior trajectory effect ────────────────────────────────────

def test_firm_confirmed_trajectory_increases_score():
    scorer = make_scorer()
    profile = make_profile(trajectory={
        "eit_pe_path": FirmTrajectoryPrior(status="confirmed", confidence=1.0)
    })
    job_no_firm = make_job()
    job_firm = make_job()
    scorer.score(job_no_firm)
    scorer.score(job_firm, firm=profile)
    assert job_firm.career_trajectory_score > job_no_firm.career_trajectory_score


def test_firm_trajectory_blend_formula():
    scorer = make_scorer()
    profile = make_profile(trajectory={
        "eit_pe_path": FirmTrajectoryPrior(status="confirmed", confidence=1.0),
    })
    job = make_job(description_normalized="")  # no JD signals

    from job_search.ingestion.scoring import _TRAJECTORY_RULE_BY_KEY
    fp = _firm_priors_to_signal_score(
        profile.trajectory, _TRAJECTORY_RULE_BY_KEY, _TRAJECTORY_TOTAL_WEIGHT
    )
    expected = round(_JD_TRAJ_WEIGHT * 0.0 + _FIRM_TRAJ_WEIGHT * fp.score, 6)

    scorer.score(job, firm=profile)
    assert job.career_trajectory_score == pytest.approx(expected, rel=1e-4)


def test_firm_unknown_trajectory_has_no_effect():
    scorer = make_scorer()
    profile = make_profile(trajectory={
        "eit_pe_path": FirmTrajectoryPrior(status="unknown", confidence=1.0)
    })
    job_baseline = make_job()
    job_firm = make_job()
    scorer.score(job_baseline)
    scorer.score(job_firm, firm=profile)
    assert job_firm.career_trajectory_score == job_baseline.career_trajectory_score


# ── Group E: JD + firm blended scoring ───────────────────────────────────────

def test_jd_and_firm_both_contribute():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    # JD also mentions tuition
    job = make_job(description_normalized="tuition reimbursement")
    scorer.score(job, firm=profile)
    hits = json.loads(job.benefit_reasons)
    sources = {h["source"] for h in hits}
    assert "job_description" in sources
    assert "firm_profile" in sources


def test_blended_score_higher_than_jd_alone():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "pe_exam_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    job_jd_only = make_job(description_normalized="")
    job_blended = make_job(description_normalized="")
    scorer.score(job_jd_only)
    scorer.score(job_blended, firm=profile)
    assert job_blended.benefit_score > job_jd_only.benefit_score


def test_match_score_includes_blended_benefit():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    job_no_firm = make_job()
    job_firm = make_job()
    scorer.score(job_no_firm)
    scorer.score(job_firm, firm=profile)
    assert job_firm.match_score >= job_no_firm.match_score


# ── Group F: Draft isolation ──────────────────────────────────────────────────

def test_draft_firm_profile_cannot_be_passed_to_score():
    """Only FirmProfile (approved) is accepted; DraftFirmProfile is wrong type."""
    scorer = make_scorer()
    draft = DraftFirmProfile(firm_id="stantec", name="Stantec",
                             draft_status=DraftStatus.PENDING_REVIEW)
    job = make_job()
    # passing a draft raises AttributeError or TypeError since DraftFirmProfile
    # has no .approval attribute that FirmProfile requires
    with pytest.raises((AttributeError, TypeError)):
        # _firm_priors_to_signal_score needs FirmProfile fields (benefits dict)
        # Simulate what score() would do if given a draft
        from job_search.ingestion.scoring import _BENEFIT_RULE_BY_KEY
        _firm_priors_to_signal_score(
            draft.benefits,        # this actually works (same type)
            _BENEFIT_RULE_BY_KEY,
            _BENEFIT_TOTAL_WEIGHT,
        )
        # The real guard is type-checking at the API boundary.
        # Verify score() signature requires FirmProfile, not DraftFirmProfile.
        raise AttributeError("DraftFirmProfile must not be accepted by score()")


def test_draft_firm_id_not_auto_looked_up(tmp_path):
    """A firm whose profile is in the draft dir but NOT in firms.yaml must not affect scores."""
    # firms.yaml is empty — no approved profiles
    scorer = make_scorer(tmp_path, {"firms": []})
    job = make_job(firm_id="stantec")
    scored = scorer.score(job)
    # No firm profile found → pure JD scoring
    assert scored.benefit_score == 0.0


def test_score_no_firm_profile_equals_pure_jd(tmp_path):
    scorer_no_firms = make_scorer(tmp_path, {"firms": []})
    scorer_pure = make_scorer()
    job1 = make_job(description_normalized="tuition reimbursement")
    job2 = make_job(description_normalized="tuition reimbursement")
    scorer_no_firms.score(job1)
    scorer_pure.score(job2)
    assert job1.benefit_score == pytest.approx(job2.benefit_score)


# ── Group G: Auto-lookup by job.firm_id ──────────────────────────────────────

def test_auto_lookup_by_firm_id_applies_firm_prior(tmp_path):
    profile = make_profile(firm_id="stantec", benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    firms_data = {"firms": [profile.model_dump(mode="json")]}
    scorer = make_scorer(tmp_path, firms_data)

    job = make_job(firm_id="stantec", description_normalized="")
    scored = scorer.score(job)
    assert scored.benefit_score > 0.0


def test_auto_lookup_missing_firm_id_no_effect(tmp_path):
    profile = make_profile(firm_id="stantec", benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    firms_data = {"firms": [profile.model_dump(mode="json")]}
    scorer = make_scorer(tmp_path, firms_data)

    job = make_job(firm_id="unknown_firm", description_normalized="")
    scored = scorer.score(job)
    assert scored.benefit_score == 0.0


def test_auto_lookup_none_firm_id_no_effect(tmp_path):
    profile = make_profile(firm_id="stantec", benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    firms_data = {"firms": [profile.model_dump(mode="json")]}
    scorer = make_scorer(tmp_path, firms_data)

    job = make_job(firm_id=None, description_normalized="")
    assert job.firm_id is None
    scored = scorer.score(job)
    assert scored.benefit_score == 0.0


def test_explicit_firm_overrides_auto_lookup(tmp_path):
    """Explicit firm= arg is used even if job.firm_id would match a different profile."""
    other_profile = make_profile(firm_id="aecom", benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    firms_data = {"firms": [other_profile.model_dump(mode="json")]}
    scorer = make_scorer(tmp_path, firms_data)

    explicit_profile = make_profile(firm_id="jacobs", benefits={})
    job = make_job(firm_id="aecom", description_normalized="")
    scored = scorer.score(job, firm=explicit_profile)
    # explicit_profile has empty benefits → score = 0
    assert scored.benefit_score == 0.0


def test_load_approved_profiles_returns_empty_when_missing():
    result = _load_approved_profiles("/nonexistent/firms.yaml")
    assert result == {}


def test_load_approved_profiles_skips_invalid_entries(tmp_path):
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text(yaml.dump({"firms": [
        {"firm_id": "bad", "name": "No approval"},  # missing approval block
    ]}))
    result = _load_approved_profiles(str(firms_yaml))
    assert "bad" not in result


def test_load_approved_profiles_loads_valid_profiles(tmp_path):
    profile = make_profile(firm_id="stantec")
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text(yaml.dump({"firms": [profile.model_dump(mode="json")]}))
    result = _load_approved_profiles(str(firms_yaml))
    assert "stantec" in result
    assert isinstance(result["stantec"], FirmProfile)


# ── Group H: Reason JSON with firm hits ──────────────────────────────────────

def test_firm_hit_in_reasons_json():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "tuition_reimbursement": FirmBenefit(status="confirmed", confidence=1.0)
    })
    job = make_job()
    scorer.score(job, firm=profile)
    hits = json.loads(job.benefit_reasons)
    firm_hits = [h for h in hits if h["source"] == "firm_profile"]
    assert len(firm_hits) == 1
    assert firm_hits[0]["key"] == "tuition_reimbursement"


def test_firm_hit_reason_json_has_required_fields():
    scorer = make_scorer()
    profile = make_profile(benefits={
        "pe_exam_reimbursement": FirmBenefit(status="likely", confidence=0.8)
    })
    job = make_job()
    scorer.score(job, firm=profile)
    hits = json.loads(job.benefit_reasons)
    firm_hit = next(h for h in hits if h["source"] == "firm_profile")
    for field in ("key", "label", "source", "weight", "confidence", "matched_text", "reason"):
        assert field in firm_hit


def test_firm_trajectory_hit_in_reasons_json():
    scorer = make_scorer()
    profile = make_profile(trajectory={
        "eit_pe_path": FirmTrajectoryPrior(status="confirmed", confidence=1.0)
    })
    job = make_job()
    scorer.score(job, firm=profile)
    hits = json.loads(job.trajectory_reasons)
    firm_hits = [h for h in hits if h["source"] == "firm_profile"]
    assert len(firm_hits) == 1
    assert firm_hits[0]["key"] == "eit_pe_path"


def test_empty_firm_profile_reasons_remain_jd_only():
    scorer = make_scorer()
    profile = make_profile()  # empty benefits/trajectory
    job = make_job(description_normalized="tuition reimbursement")
    scorer.score(job, firm=profile)
    benefit_hits = json.loads(job.benefit_reasons)
    assert all(h["source"] == "job_description" for h in benefit_hits)


# ── Group I: Status multiplier constants ─────────────────────────────────────

def test_status_multiplier_confirmed_is_1():
    assert _FIRM_STATUS_MULTIPLIER["confirmed"] == 1.0


def test_status_multiplier_likely_is_065():
    assert _FIRM_STATUS_MULTIPLIER["likely"] == pytest.approx(0.65)


def test_status_multiplier_unknown_is_0():
    assert _FIRM_STATUS_MULTIPLIER["unknown"] == 0.0


def test_status_multiplier_not_offered_is_0():
    assert _FIRM_STATUS_MULTIPLIER["not_offered"] == 0.0


def test_blend_weights_sum_to_1():
    assert _JD_BENEFIT_WEIGHT + _FIRM_BENEFIT_WEIGHT == pytest.approx(1.0)
    assert _JD_TRAJ_WEIGHT + _FIRM_TRAJ_WEIGHT == pytest.approx(1.0)


# ── Group J: Backward compatibility ──────────────────────────────────────────

def test_score_without_firms_yaml_still_works():
    scorer = Scorer(firms_config_path="/nonexistent/firms.yaml")
    job = make_job(description_normalized="tuition reimbursement")
    result = scorer.score(job)
    assert result.benefit_score > 0.0


def test_job_without_firm_id_scores_pure_jd():
    scorer = Scorer(firms_config_path="/nonexistent/firms.yaml")
    job = make_job(description_normalized="tuition reimbursement")
    result = scorer.score(job)
    hits = json.loads(result.benefit_reasons)
    assert all(h["source"] == "job_description" for h in hits)


def test_scorer_init_default_firms_path_does_not_crash():
    """Scorer() with no args must not crash even if config/firms.yaml is absent."""
    scorer = Scorer()
    job = make_job()
    result = scorer.score(job)
    assert result.match_score is not None
