import pytest

from job_search.planning.future_scoring_contracts import (
    ClaimStatus,
    DashboardScoreSummaryDraft,
    EvidenceClaimDraft,
    FirmProfileDraft,
    JobScoreEnvelopeDraft,
    Rating,
    ReviewStatus,
    ScoreDomain,
    SignalHitDraft,
    SignalScoreDraft,
    SignalSource,
)


def test_signal_hit_serializes_to_future_reason_json_shape():
    hit = SignalHitDraft(
        key="tuition_reimbursement",
        label="Tuition reimbursement",
        domain=ScoreDomain.BENEFIT,
        source=SignalSource.JOB_DESCRIPTION,
        weight=0.18,
        confidence=1.0,
        matched_text="tuition reimbursement",
        reason="Job post mentions tuition reimbursement.",
    )

    assert hit.to_json_dict() == {
        "key": "tuition_reimbursement",
        "label": "Tuition reimbursement",
        "domain": "benefit",
        "source": "job_description",
        "weight": 0.18,
        "confidence": 1.0,
        "matched_text": "tuition reimbursement",
        "reason": "Job post mentions tuition reimbursement.",
        "source_url": None,
    }


def test_signal_score_rejects_cross_domain_hits():
    hit = SignalHitDraft(
        key="eit_pe_path",
        label="EIT/PE path",
        domain=ScoreDomain.TRAJECTORY,
        source=SignalSource.JOB_DESCRIPTION,
        weight=0.2,
        confidence=1.0,
    )

    with pytest.raises(ValueError, match="share the score domain"):
        SignalScoreDraft(domain=ScoreDomain.BENEFIT, score=0.2, hits=(hit,))


def test_unknown_controlled_key_is_rejected():
    with pytest.raises(ValueError, match="Unknown benefit key"):
        EvidenceClaimDraft(
            key="free_snacks",
            domain=ScoreDomain.BENEFIT,
            status=ClaimStatus.LIKELY,
            confidence=0.5,
        )


def test_only_approved_firm_profile_exposes_scoring_claims():
    claim = EvidenceClaimDraft(
        key="pe_exam_reimbursement",
        domain=ScoreDomain.BENEFIT,
        status=ClaimStatus.CONFIRMED,
        confidence=0.9,
        source_url="https://example.invalid/benefits",
        source_type="benefits_page",
        last_verified="2026-06-12",
    )
    draft = FirmProfileDraft(
        firm_id="example_engineering",
        name="Example Engineering",
        review_status=ReviewStatus.PENDING_REVIEW,
        benefits=(claim,),
    )
    approved = FirmProfileDraft(
        firm_id="example_engineering",
        name="Example Engineering",
        review_status=ReviewStatus.APPROVED,
        benefits=(claim,),
    )

    assert draft.approved_claims(ScoreDomain.BENEFIT) == ()
    assert approved.approved_claims(ScoreDomain.BENEFIT) == (claim,)


def test_job_score_envelope_preserves_future_column_names():
    benefit_hit = SignalHitDraft(
        key="relocation_assistance",
        label="Relocation assistance",
        domain=ScoreDomain.BENEFIT,
        source=SignalSource.JOB_DESCRIPTION,
        weight=0.04,
        confidence=1.0,
    )
    trajectory_hit = SignalHitDraft(
        key="structural_practice_depth",
        label="Structural practice depth",
        domain=ScoreDomain.TRAJECTORY,
        source=SignalSource.FIRM_PROFILE,
        weight=0.02,
        confidence=0.65,
        source_url="https://example.invalid/careers",
    )
    envelope = JobScoreEnvelopeDraft(
        canonical_job_id="job123",
        benefit=SignalScoreDraft(
            domain=ScoreDomain.BENEFIT,
            score=0.25,
            hits=(benefit_hit,),
        ),
        trajectory=SignalScoreDraft(
            domain=ScoreDomain.TRAJECTORY,
            score=0.35,
            hits=(trajectory_hit,),
        ),
        blended_with_firm_profile=True,
    )

    updates = envelope.to_job_column_updates()

    assert updates["benefit_score"] == 0.25
    assert updates["career_trajectory_score"] == 0.35
    assert updates["benefit_reasons"][0]["key"] == "relocation_assistance"
    assert updates["trajectory_reasons"][0]["source"] == "firm_profile"


def test_dashboard_summary_uses_labels_and_firm_review_status():
    benefit = SignalScoreDraft(
        domain=ScoreDomain.BENEFIT,
        score=0.4,
        hits=(
            SignalHitDraft(
                key="graduate_degree_assistance",
                label="Graduate degree assistance",
                domain=ScoreDomain.BENEFIT,
                source=SignalSource.JOB_DESCRIPTION,
                weight=0.16,
                confidence=1.0,
            ),
        ),
    )
    trajectory = SignalScoreDraft(domain=ScoreDomain.TRAJECTORY, score=0.0)
    envelope = JobScoreEnvelopeDraft(
        canonical_job_id="job123",
        benefit=benefit,
        trajectory=trajectory,
    )
    firm = FirmProfileDraft(
        firm_id="example_engineering",
        name="Example Engineering",
        review_status=ReviewStatus.APPROVED,
        trajectory=(
            EvidenceClaimDraft(
                key="structural_practice_depth",
                domain=ScoreDomain.TRAJECTORY,
                status=ClaimStatus.LIKELY,
                confidence=0.6,
                rating=Rating.MEDIUM,
            ),
        ),
    )

    summary = DashboardScoreSummaryDraft.from_envelope(envelope, firm=firm)

    assert summary.benefit_labels == ("Graduate degree assistance",)
    assert summary.firm_name == "Example Engineering"
    assert summary.firm_review_status == ReviewStatus.APPROVED
