"""Draft contracts for future Benefit/Trajectory and Firm Repository work.

These structures are preparatory only. They are not imported by the runtime
pipeline and must not be treated as accepted Phase 2/3 implementation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


BENEFIT_KEYS: tuple[str, ...] = (
    "tuition_reimbursement",
    "graduate_degree_assistance",
    "fe_exam_reimbursement",
    "pe_exam_reimbursement",
    "pe_prep_reimbursement",
    "licensing_reimbursement",
    "continuing_education",
    "student_loan_assistance",
    "relocation_assistance",
    "signing_bonus",
    "housing_assistance",
)

TRAJECTORY_KEYS: tuple[str, ...] = (
    "eit_pe_path",
    "mentorship",
    "technical_training",
    "new_grad_program",
    "design_responsibility",
    "project_scale",
    "rotation_or_growth",
    "graduate_school_support",
    "leadership_development",
    "structural_practice_depth",
)


class ScoreDomain(str, Enum):
    BENEFIT = "benefit"
    TRAJECTORY = "trajectory"


class SignalSource(str, Enum):
    JOB_DESCRIPTION = "job_description"
    FIRM_PROFILE = "firm_profile"
    MANUAL_REVIEW = "manual_review"


class ClaimStatus(str, Enum):
    CONFIRMED = "confirmed"
    LIKELY = "likely"
    UNKNOWN = "unknown"
    NOT_OFFERED = "not_offered"


class Rating(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


APPROVED_REVIEW_STATUSES: tuple[ReviewStatus, ...] = (ReviewStatus.APPROVED,)


@dataclass(frozen=True)
class SignalRuleDraft:
    """Future deterministic rule for one benefit or trajectory signal."""

    key: str
    label: str
    domain: ScoreDomain
    weight: float
    patterns: tuple[str, ...]
    negative_patterns: tuple[str, ...] = ()
    source: SignalSource = SignalSource.JOB_DESCRIPTION

    def __post_init__(self) -> None:
        _validate_controlled_key(self.domain, self.key)
        _validate_probability("weight", self.weight)
        if not self.patterns:
            raise ValueError("SignalRuleDraft.patterns must not be empty.")


@dataclass(frozen=True)
class SignalHitDraft:
    """Evidence for a matched signal, suitable for future JSON persistence."""

    key: str
    label: str
    domain: ScoreDomain
    source: SignalSource
    weight: float
    confidence: float
    matched_text: str | None = None
    reason: str = ""
    source_url: str | None = None

    def __post_init__(self) -> None:
        _validate_controlled_key(self.domain, self.key)
        _validate_probability("weight", self.weight)
        _validate_probability("confidence", self.confidence)

    def to_json_dict(self) -> dict[str, Any]:
        return _enum_to_value(asdict(self))


@dataclass(frozen=True)
class SignalScoreDraft:
    """Draft in-memory output for one score category before DB integration."""

    domain: ScoreDomain
    score: float
    hits: tuple[SignalHitDraft, ...] = ()
    missing_priority_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_probability("score", self.score)
        for hit in self.hits:
            if hit.domain != self.domain:
                raise ValueError("SignalScoreDraft.hits must share the score domain.")

    def to_reason_json(self) -> list[dict[str, Any]]:
        return [hit.to_json_dict() for hit in self.hits]


@dataclass(frozen=True)
class EvidenceClaimDraft:
    """Future firm-level benefit or trajectory prior with provenance."""

    key: str
    domain: ScoreDomain
    status: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = 0.0
    source_url: str | None = None
    source_type: str | None = None
    last_verified: str | None = None
    extraction_note: str | None = None
    rating: Rating | None = None

    def __post_init__(self) -> None:
        _validate_controlled_key(self.domain, self.key)
        _validate_probability("confidence", self.confidence)

    def to_json_dict(self) -> dict[str, Any]:
        return _enum_to_value(asdict(self))


@dataclass(frozen=True)
class FirmAtsDraft:
    """Draft ATS plumbing to keep source health separate from firm quality."""

    ats_type: str = "unknown"
    ats_tier: str = "unknown"
    board_token: str | None = None
    tenant: str | None = None
    site: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FirmProfileDraft:
    """Future YAML/SQLite shape for approved or pending firm intelligence."""

    firm_id: str
    name: str
    review_status: ReviewStatus
    aliases: tuple[str, ...] = ()
    website: str | None = None
    careers_url: str | None = None
    ats: FirmAtsDraft = field(default_factory=FirmAtsDraft)
    disciplines: tuple[str, ...] = ()
    markets: tuple[str, ...] = ()
    office_regions: tuple[str, ...] = ()
    benefits: tuple[EvidenceClaimDraft, ...] = ()
    trajectory: tuple[EvidenceClaimDraft, ...] = ()
    manual_priority: str = "neutral"
    approved_at: str | None = None
    approved_by: str | None = None
    last_verified: str | None = None
    reviewer_notes: tuple[str, ...] = ()

    @property
    def is_approved_for_scoring(self) -> bool:
        return self.review_status in APPROVED_REVIEW_STATUSES

    def approved_claims(self, domain: ScoreDomain) -> tuple[EvidenceClaimDraft, ...]:
        if not self.is_approved_for_scoring:
            return ()
        claims = self.benefits if domain == ScoreDomain.BENEFIT else self.trajectory
        return tuple(claim for claim in claims if claim.status != ClaimStatus.UNKNOWN)

    def to_json_dict(self) -> dict[str, Any]:
        return _enum_to_value(asdict(self))


@dataclass(frozen=True)
class JobScoreInputsDraft:
    """Draft scoring input envelope combining job and optional firm context."""

    canonical_job_id: str
    title: str
    company: str
    normalized_job_text: str
    firm_id: str | None = None
    firm_profile: FirmProfileDraft | None = None

    @property
    def has_approved_firm_profile(self) -> bool:
        return bool(self.firm_profile and self.firm_profile.is_approved_for_scoring)


@dataclass(frozen=True)
class JobScoreEnvelopeDraft:
    """Future job-level score result that preserves existing numeric fields."""

    canonical_job_id: str
    benefit: SignalScoreDraft
    trajectory: SignalScoreDraft
    blended_with_firm_profile: bool = False

    def to_job_column_updates(self) -> dict[str, Any]:
        return {
            "benefit_score": self.benefit.score,
            "career_trajectory_score": self.trajectory.score,
            "benefit_reasons": self.benefit.to_reason_json(),
            "trajectory_reasons": self.trajectory.to_reason_json(),
        }


@dataclass(frozen=True)
class DashboardScoreSummaryDraft:
    """Future read model for dashboard job detail and firm drilldowns."""

    canonical_job_id: str
    benefit_score: float
    trajectory_score: float
    benefit_labels: tuple[str, ...] = ()
    trajectory_labels: tuple[str, ...] = ()
    firm_name: str | None = None
    firm_review_status: ReviewStatus | None = None

    def __post_init__(self) -> None:
        _validate_probability("benefit_score", self.benefit_score)
        _validate_probability("trajectory_score", self.trajectory_score)

    @classmethod
    def from_envelope(
        cls,
        envelope: JobScoreEnvelopeDraft,
        firm: FirmProfileDraft | None = None,
    ) -> DashboardScoreSummaryDraft:
        return cls(
            canonical_job_id=envelope.canonical_job_id,
            benefit_score=envelope.benefit.score,
            trajectory_score=envelope.trajectory.score,
            benefit_labels=tuple(hit.label for hit in envelope.benefit.hits),
            trajectory_labels=tuple(hit.label for hit in envelope.trajectory.hits),
            firm_name=firm.name if firm else None,
            firm_review_status=firm.review_status if firm else None,
        )


def _validate_controlled_key(domain: ScoreDomain, key: str) -> None:
    allowed = BENEFIT_KEYS if domain == ScoreDomain.BENEFIT else TRAJECTORY_KEYS
    if key not in allowed:
        raise ValueError(f"Unknown {domain.value} key: {key}")


def _validate_probability(field_name: str, value: float) -> None:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")


def _enum_to_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_to_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_enum_to_value(item) for item in value]
    return value
