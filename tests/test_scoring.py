"""Tests for match scoring engine."""

import pytest

from job_search.ingestion.scoring import (
    BENEFIT_RULES,
    TRAJECTORY_RULES,
    SignalHit,
    SignalRule,
    SignalScore,
    Scorer,
    _BENEFIT_COMPILED,
    _TRAJECTORY_COMPILED,
    _match_signal_rules,
    format_top_reasons,
)
from job_search.models import CanonicalJob, StretchCategory


def make_job(**kwargs) -> CanonicalJob:
    defaults = dict(
        source="test",
        source_job_id="s001",
        company="Acme",
        title="Structural Engineer",
        description_normalized="structural design RAM Structural System steel design reinforced concrete engineer in training EIT tuition reimbursement mentorship program",
        location_city="Seattle",
        location_state="WA",
    )
    defaults.update(kwargs)
    return CanonicalJob(**defaults)


# ── Existing tests (must remain passing) ─────────────────────────────────────

def test_structural_seattle_high_score():
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)
    assert job.match_score is not None
    assert job.match_score >= 0.70, f"Expected high score, got {job.match_score}"


def test_benefit_score_captured():
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)
    assert job.benefit_score > 0.0


def test_trajectory_score_captured():
    scorer = Scorer()
    job = make_job()
    job = scorer.score(job)
    assert job.career_trajectory_score > 0.0


def test_pe_required_penalty():
    scorer = Scorer()
    from job_search.models import KnockoutFields
    job = make_job(
        title="Senior Structural Engineer",
        description_normalized="PE required professional engineer license 10 years experience",
    )
    job.knockout = KnockoutFields(pe_required=True, min_years=10)
    job = scorer.score(job)
    assert job.match_score < 0.50


def test_stretch_category_bs_ce():
    scorer = Scorer()
    job = make_job(
        description_normalized="BS Civil Engineering required structural design"
    )
    job = scorer.score(job)
    assert job.stretch_category == StretchCategory.COMPETITIVE_STRETCH


def test_qualified_with_cet():
    scorer = Scorer()
    job = make_job(
        description_normalized="civil engineering technology bachelor degree structural"
    )
    job = scorer.score(job)
    assert job.stretch_category == StretchCategory.QUALIFIED


# ── Group A: Benefit phrase matching ─────────────────────────────────────────

def test_benefit_tuition_reimbursement_phrase():
    result = _match_signal_rules("we offer tuition reimbursement for all employees", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "tuition_reimbursement" in keys
    assert result.score > 0.0


def test_benefit_tuition_bare_word_no_score():
    result = _match_signal_rules("candidates studying tuition fees are common", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "tuition_reimbursement" not in keys


def test_benefit_pe_exam_reimbursement_phrase():
    result = _match_signal_rules("we cover pe exam reimbursement costs", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "pe_exam_reimbursement" in keys


def test_benefit_graduate_degree_assistance_phrase():
    result = _match_signal_rules("we offer graduate degree assistance for staff", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "graduate_degree_assistance" in keys


def test_benefit_graduate_bare_word_blocked_by_negative():
    result = _match_signal_rules("seeking new graduate engineer for entry level role", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "graduate_degree_assistance" not in keys


def test_benefit_relocation_assistance_phrase():
    result = _match_signal_rules("relocation assistance available for qualified candidates", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "relocation_assistance" in keys


def test_benefit_housing_bare_word_no_score():
    result = _match_signal_rules("housing project design in a coastal environment", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "housing_assistance" not in keys


def test_benefit_housing_assistance_phrase():
    result = _match_signal_rules("we provide housing assistance for relocated staff", _BENEFIT_COMPILED)
    keys = [h.key for h in result.hits]
    assert "housing_assistance" in keys


# ── Group B: Trajectory phrase matching ──────────────────────────────────────

def test_trajectory_eit_pe_path_phrase():
    result = _match_signal_rules("this role supports engineers in training toward pe licensure", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "eit_pe_path" in keys


def test_trajectory_eit_acronym():
    result = _match_signal_rules("we support EIT candidates through licensure", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "eit_pe_path" in keys


def test_trajectory_mentorship_program_phrase():
    result = _match_signal_rules("we run a formal mentorship program for junior engineers", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "mentorship" in keys


def test_trajectory_mentor_bare_word_no_score():
    result = _match_signal_rules("your manager will mentor and guide you", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "mentorship" not in keys


def test_trajectory_promotion_bare_word_no_score():
    result = _match_signal_rules("promotion of sustainable design practices", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" not in keys


def test_trajectory_rotation_program_phrase():
    result = _match_signal_rules("our rotational program places engineers across disciplines", _TRAJECTORY_COMPILED)
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


# ── Group C: Double-count prevention ─────────────────────────────────────────

def test_no_double_count_repeated_phrase():
    single = _match_signal_rules("tuition reimbursement available", _BENEFIT_COMPILED)
    repeated = _match_signal_rules(
        "tuition reimbursement tuition reimbursement tuition reimbursement tuition reimbursement",
        _BENEFIT_COMPILED,
    )
    assert single.score == repeated.score


def test_no_double_count_multiple_patterns_same_key():
    # Both "tuition reimbursement" and "tuition assistance" match tuition_reimbursement key.
    result = _match_signal_rules("tuition reimbursement and tuition assistance offered", _BENEFIT_COMPILED)
    tuition_hits = [h for h in result.hits if h.key == "tuition_reimbursement"]
    assert len(tuition_hits) == 1


# ── Group D: No-hit zero ──────────────────────────────────────────────────────

def test_benefit_no_signals_zero_score():
    result = _match_signal_rules("civil engineering structural design position", _BENEFIT_COMPILED)
    assert result.score == 0.0
    assert result.hits == []


def test_trajectory_no_signals_zero_score():
    result = _match_signal_rules("competitive salary and benefits package", _TRAJECTORY_COMPILED)
    assert result.score == 0.0
    assert result.hits == []


# ── Group E: Score normalization ──────────────────────────────────────────────

def test_benefit_score_bounded():
    # Maximum-signal text.
    text = (
        "tuition reimbursement graduate degree assistance pe exam reimbursement "
        "pe prep fe exam reimbursement licensing reimbursement continuing education "
        "student loan assistance relocation assistance signing bonus housing assistance"
    )
    result = _match_signal_rules(text, _BENEFIT_COMPILED)
    assert 0.0 <= result.score <= 1.0


def test_trajectory_score_bounded():
    text = (
        "engineer in training mentorship program technical training new graduate program "
        "design responsibility large-scale project rotational program graduate school support "
        "leadership development structural engineering practice"
    )
    result = _match_signal_rules(text, _TRAJECTORY_COMPILED)
    assert 0.0 <= result.score <= 1.0


# ── Group F: Determinism ──────────────────────────────────────────────────────

def test_scoring_is_deterministic():
    scorer = Scorer()
    job = make_job()
    result_a = scorer.score(make_job())
    result_b = scorer.score(make_job())
    assert result_a.match_score == result_b.match_score
    assert result_a.benefit_score == result_b.benefit_score
    assert result_a.career_trajectory_score == result_b.career_trajectory_score


# ── Group G: Reason hits ──────────────────────────────────────────────────────

def test_benefit_hits_returned():
    result = _match_signal_rules("we offer tuition reimbursement and pe exam reimbursement", _BENEFIT_COMPILED)
    assert len(result.hits) >= 2
    keys = [h.key for h in result.hits]
    assert "tuition_reimbursement" in keys
    assert "pe_exam_reimbursement" in keys


def test_trajectory_hits_returned():
    result = _match_signal_rules("engineer in training mentorship program", _TRAJECTORY_COMPILED)
    assert len(result.hits) >= 2


def test_hits_sorted_by_weight_descending():
    result = _match_signal_rules(
        "tuition reimbursement signing bonus relocation assistance", _BENEFIT_COMPILED
    )
    weights = [h.weight for h in result.hits]
    assert weights == sorted(weights, reverse=True)


def test_format_top_reasons_output():
    hits = [
        SignalHit(key="tuition_reimbursement", label="Tuition reimbursement", source="job_description",
                  weight=0.18, confidence=1.0, matched_text="tuition reimbursement",
                  reason="Job post mentions tuition reimbursement."),
        SignalHit(key="pe_exam_reimbursement", label="PE exam reimbursement", source="job_description",
                  weight=0.14, confidence=1.0, matched_text="pe exam reimbursement",
                  reason="Job post mentions pe exam reimbursement."),
        SignalHit(key="signing_bonus", label="Signing bonus", source="job_description",
                  weight=0.02, confidence=1.0, matched_text="signing bonus",
                  reason="Job post mentions signing bonus."),
    ]
    out = format_top_reasons(hits, n=3)
    assert out == "Tuition reimbursement, PE exam reimbursement, Signing bonus"


def test_format_top_reasons_fewer_than_n():
    hits = [
        SignalHit(key="signing_bonus", label="Signing bonus", source="job_description",
                  weight=0.02, confidence=1.0, matched_text="signing bonus",
                  reason="Job post mentions signing bonus."),
    ]
    out = format_top_reasons(hits, n=3)
    assert out == "Signing bonus"


def test_format_top_reasons_empty():
    assert format_top_reasons([], n=3) == ""


# ── Group H: Backwards compatibility ─────────────────────────────────────────

def test_scorer_public_interface_unchanged():
    scorer = Scorer()
    job = make_job()
    result = scorer.score(job)
    assert isinstance(result, CanonicalJob)
    assert isinstance(result.benefit_score, float)
    assert isinstance(result.career_trajectory_score, float)
    assert isinstance(result.match_score, float)


def test_signal_dataclasses_present():
    rule = BENEFIT_RULES[0]
    assert isinstance(rule, SignalRule)
    assert isinstance(rule.key, str)
    assert isinstance(rule.patterns, tuple)


def test_no_legacy_dicts():
    import job_search.ingestion.scoring as mod
    assert not hasattr(mod, "BENEFIT_SIGNALS")
    assert not hasattr(mod, "TRAJECTORY_SIGNALS")


def test_no_legacy_compute_methods():
    scorer = Scorer()
    assert not hasattr(scorer, "_compute_benefit_score")
    assert not hasattr(scorer, "_compute_trajectory_score")


# ── Group I: rotation_or_growth calibration (Phase 2.1) ──────────────────────

# Boilerplate phrases that must NOT score.

def test_rotation_career_path_bare_no_score():
    result = _match_signal_rules(
        "we offer competitive salary and a clear career path for growth", _TRAJECTORY_COMPILED
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" not in keys


def test_rotation_growth_path_bare_no_score():
    result = _match_signal_rules(
        "excellent growth path opportunities available for motivated engineers", _TRAJECTORY_COMPILED
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" not in keys


def test_rotation_advancement_opportunity_bare_no_score():
    result = _match_signal_rules(
        "we provide advancement opportunities for high performers", _TRAJECTORY_COMPILED
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" not in keys


def test_rotation_generic_boilerplate_block_no_score():
    # Sentence combining all three removed patterns — must produce zero rotation_or_growth hit.
    result = _match_signal_rules(
        "competitive salary career path growth path advancement opportunity benefits package",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" not in keys


# Existing tight patterns must still score.

def test_rotation_rotational_program_still_scores():
    result = _match_signal_rules(
        "our rotational program places junior engineers across three practice areas",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_rotation_program_still_scores():
    result = _match_signal_rules(
        "engineers are eligible for our rotation program after six months",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_job_rotation_still_scores():
    result = _match_signal_rules(
        "we offer job rotation across structural, transportation, and water resources",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


# New tighter replacement patterns must score.

def test_rotation_career_ladder_scores():
    result = _match_signal_rules(
        "we have a defined career ladder from engineer i to principal engineer",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_career_development_program_scores():
    result = _match_signal_rules(
        "all engineers participate in our career development program in their first year",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_structured_career_path_scores():
    result = _match_signal_rules(
        "we provide a structured career path with clear promotion milestones",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_structured_advancement_program_scores():
    result = _match_signal_rules(
        "our structured advancement program is reviewed annually with your manager",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


def test_rotation_structured_growth_track_scores():
    result = _match_signal_rules(
        "the firm offers a structured growth track for early-career engineers",
        _TRAJECTORY_COMPILED,
    )
    keys = [h.key for h in result.hits]
    assert "rotation_or_growth" in keys


# Score isolation: boilerplate-only JD scores lower than structured-program JD.

def test_rotation_boilerplate_jd_scores_lower_than_structured_program_jd():
    boilerplate = _match_signal_rules(
        "competitive pay career path growth path advancement opportunity great culture",
        _TRAJECTORY_COMPILED,
    )
    structured = _match_signal_rules(
        "we run a rotational program and maintain a defined career ladder for all engineers",
        _TRAJECTORY_COMPILED,
    )
    assert boilerplate.score < structured.score
