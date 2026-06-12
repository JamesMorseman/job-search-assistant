"""Future-facing planning objects.

This package is intentionally inert. Runtime pipeline modules should not import
from it until the relevant architecture is accepted for Phase 2/3.
"""

from .future_scoring_contracts import (
    APPROVED_REVIEW_STATUSES,
    BENEFIT_KEYS,
    TRAJECTORY_KEYS,
    ClaimStatus,
    DashboardScoreSummaryDraft,
    EvidenceClaimDraft,
    FirmAtsDraft,
    FirmProfileDraft,
    JobScoreEnvelopeDraft,
    JobScoreInputsDraft,
    Rating,
    ReviewStatus,
    ScoreDomain,
    SignalHitDraft,
    SignalRuleDraft,
    SignalScoreDraft,
    SignalSource,
)

__all__ = [
    "APPROVED_REVIEW_STATUSES",
    "BENEFIT_KEYS",
    "TRAJECTORY_KEYS",
    "ClaimStatus",
    "DashboardScoreSummaryDraft",
    "EvidenceClaimDraft",
    "FirmAtsDraft",
    "FirmProfileDraft",
    "JobScoreEnvelopeDraft",
    "JobScoreInputsDraft",
    "Rating",
    "ReviewStatus",
    "ScoreDomain",
    "SignalHitDraft",
    "SignalRuleDraft",
    "SignalScoreDraft",
    "SignalSource",
]
