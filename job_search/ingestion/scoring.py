"""Match scoring engine.

Produces a 0.0–1.0 match_score and a stretch_category for each job.
Also computes benefit_score, career_trajectory_score, and attaches a
LocationScore from the city-guide framework.

Weights are configurable in config/scoring.yaml.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from job_search.location import LocationScore, LocationScorer
from job_search.location.models import SchemeName
from job_search.models import CanonicalJob, FirmBenefitStatus, FirmProfile, KnockoutFields, StretchCategory
from job_search.services.scoring_settings import (
    DEFAULT_PENALTIES as DEFAULT_SCORING_PENALTIES,
    ScoringSettingsService,
)

logger = logging.getLogger(__name__)


# ── Signal engine dataclasses ─────────────────────────────────────────────────

@dataclass(frozen=True)
class SignalRule:
    key: str
    label: str
    weight: float
    patterns: tuple[str, ...]
    negative_patterns: tuple[str, ...] = ()
    category: str = "job_description"


@dataclass(frozen=True)
class SignalHit:
    key: str
    label: str
    source: str
    weight: float
    confidence: float
    matched_text: str | None
    reason: str


@dataclass(frozen=True)
class SignalScore:
    score: float
    hits: list[SignalHit]
    missing_priority_keys: list[str]


# ── Benefit signal rules ──────────────────────────────────────────────────────

BENEFIT_RULES: list[SignalRule] = [
    SignalRule(
        key="tuition_reimbursement",
        label="Tuition reimbursement",
        weight=0.18,
        patterns=(
            r"\btuition reimbursement\b",
            r"\btuition assistance\b",
            r"\beducation assistance program\b",
            r"\beducational reimbursement\b",
        ),
    ),
    SignalRule(
        key="graduate_degree_assistance",
        label="Graduate degree assistance",
        weight=0.16,
        patterns=(
            r"\bgraduate degree assistance\b",
            r"\bmaster'?s degree assistance\b",
            r"\bgraduate school reimbursement\b",
            r"\bpaid graduate study\b",
        ),
        negative_patterns=(
            r"\bnew graduate\b",
            r"\brecent graduate\b",
            r"\bgraduate engineer\b",
        ),
    ),
    SignalRule(
        key="pe_exam_reimbursement",
        label="PE exam reimbursement",
        weight=0.14,
        patterns=(
            r"\bpe exam reimbursement\b",
            r"\bpe exam fee\b",
            r"\bprofessional engineer exam reimbursement\b",
            r"\bpe licensure reimbursement\b",
            r"\bpe exam costs?\b",
        ),
    ),
    SignalRule(
        key="pe_prep_reimbursement",
        label="PE prep support",
        weight=0.12,
        patterns=(
            r"\bpe prep\b",
            r"\bpe exam prep\b",
            r"\bpe study materials?\b",
            r"\bpe review course\b",
        ),
    ),
    SignalRule(
        key="fe_exam_reimbursement",
        label="FE exam reimbursement",
        weight=0.10,
        patterns=(
            r"\bfe exam reimbursement\b",
            r"\bfe exam fee\b",
            r"\bfundamentals of engineering exam\b",
            r"\bfe licensure\b",
        ),
    ),
    SignalRule(
        key="licensing_reimbursement",
        label="Licensing reimbursement",
        weight=0.10,
        patterns=(
            r"\blicensing reimbursement\b",
            r"\blicense reimbursement\b",
            r"\bprofessional licensure support\b",
            r"\blicensure fees? reimbursed\b",
        ),
    ),
    SignalRule(
        key="continuing_education",
        label="Continuing education",
        weight=0.08,
        patterns=(
            r"\bcontinuing education\b",
            r"\bprofessional development reimbursement\b",
            r"\bprofessional development allowance\b",
            r"\bconference reimbursement\b",
        ),
    ),
    SignalRule(
        key="student_loan_assistance",
        label="Student loan assistance",
        weight=0.05,
        patterns=(
            r"\bstudent loan assistance\b",
            r"\bstudent loan repayment\b",
            r"\bstudent debt assistance\b",
        ),
    ),
    SignalRule(
        key="relocation_assistance",
        label="Relocation assistance",
        weight=0.04,
        patterns=(
            r"\brelocation assistance\b",
            r"\brelocation package\b",
            r"\brelocation reimbursement\b",
            r"\bmoving expense\b",
        ),
    ),
    SignalRule(
        key="signing_bonus",
        label="Signing bonus",
        weight=0.02,
        patterns=(
            r"\bsigning bonus\b",
            r"\bsign.?on bonus\b",
        ),
    ),
    SignalRule(
        key="housing_assistance",
        label="Housing assistance",
        weight=0.01,
        patterns=(
            r"\bhousing assistance\b",
            r"\bhousing allowance\b",
            r"\bhousing stipend\b",
        ),
    ),
]

# ── Trajectory signal rules ───────────────────────────────────────────────────

TRAJECTORY_RULES: list[SignalRule] = [
    SignalRule(
        key="eit_pe_path",
        label="EIT/PE path",
        weight=0.20,
        patterns=(
            r"\bengineers? in training\b",
            r"\beit\b",
            r"\bpe track\b",
            r"\bprofessional engineer path\b",
            r"\bwork under (a )?licensed professional engineer\b",
            r"\bpe licensure support\b",
        ),
    ),
    SignalRule(
        key="mentorship",
        label="Mentorship program",
        weight=0.16,
        patterns=(
            r"\bmentorship program\b",
            r"\bformal mentorship\b",
            r"\bmentoring program\b",
            r"\bpaired with (a )?senior engineer\b",
            r"\bmentor.mentee\b",
        ),
    ),
    SignalRule(
        key="technical_training",
        label="Technical training",
        weight=0.13,
        patterns=(
            r"\btechnical training\b",
            r"\btraining program\b",
            r"\binternal training\b",
            r"\bonboarding training\b",
            r"\bskills development program\b",
        ),
    ),
    SignalRule(
        key="new_grad_program",
        label="New grad program",
        weight=0.12,
        patterns=(
            r"\bnew graduate program\b",
            r"\brecent graduate program\b",
            r"\bentry.?level development program\b",
            r"\bearly career program\b",
            r"\bcampus hire program\b",
        ),
    ),
    SignalRule(
        key="design_responsibility",
        label="Design responsibility",
        weight=0.12,
        patterns=(
            r"\bdesign responsibility\b",
            r"\bindependent design\b",
            r"\blead design\b",
            r"\bown.{0,20}design\b",
            r"\bfull design\b",
        ),
    ),
    SignalRule(
        key="project_scale",
        label="Large project exposure",
        weight=0.08,
        patterns=(
            r"\blarge.?scale project\b",
            r"\bmajor infrastructure\b",
            r"\bmulti.?million.?dollar project\b",
            r"\bhigh.?profile project\b",
            r"\bsignificant project\b",
        ),
    ),
    SignalRule(
        key="internal_mobility",
        label="Internal mobility / rotation",
        weight=0.07,
        patterns=(
            r"\brotational program\b",
            r"\brotation program\b",
            r"\bjob rotation\b",
            r"\bcareer ladder\b",
            r"\bcareer development program\b",
            r"\bstructured (?:career|advancement|growth) (?:path|program|framework|track)\b",
        ),
    ),
    SignalRule(
        key="graduate_school_support",
        label="Graduate school support",
        weight=0.06,
        patterns=(
            r"\bgraduate school support\b",
            r"\bgraduate study support\b",
            r"\bmaster'?s program support\b",
            r"\bpaid graduate study\b",
        ),
    ),
    SignalRule(
        key="leadership_development",
        label="Leadership development",
        weight=0.04,
        patterns=(
            r"\bleadership development\b",
            r"\bleadership training\b",
            r"\bleadership program\b",
            r"\bfuture leader\b",
        ),
    ),
    SignalRule(
        key="structural_practice_depth",
        label="Structural practice depth",
        weight=0.02,
        patterns=(
            r"\bstructural engineering practice\b",
            r"\bstructural depth\b",
            r"\badvanced structural\b",
            r"\bcomplex structural\b",
        ),
    ),
]

# ── Firm-prior blend constants (from benefit_scoring_design.md) ───────────────

# Status → confidence multiplier.  unknown/not_offered produce zero contribution.
_FIRM_STATUS_MULTIPLIER: dict[str, float] = {
    FirmBenefitStatus.CONFIRMED.value:    1.00,
    FirmBenefitStatus.LIKELY.value:       0.65,
    FirmBenefitStatus.UNKNOWN.value:      0.00,
    FirmBenefitStatus.NOT_OFFERED.value:  0.00,
}

# Blend weights: JD score weight + firm-prior weight = 1.0
_JD_BENEFIT_WEIGHT:   float = 0.70
_FIRM_BENEFIT_WEIGHT: float = 0.30
_JD_TRAJ_WEIGHT:      float = 0.65
_FIRM_TRAJ_WEIGHT:    float = 0.35

# Pre-compute total weights for normalization (same denominator as JD scoring).
_BENEFIT_TOTAL_WEIGHT:    float = sum(r.weight for r in BENEFIT_RULES)      # populated below
_TRAJECTORY_TOTAL_WEIGHT: float = sum(r.weight for r in TRAJECTORY_RULES)  # populated below

# Rule lookup by key — used when generating firm-prior SignalHit objects.
_BENEFIT_RULE_BY_KEY:    dict[str, SignalRule] = {r.key: r for r in BENEFIT_RULES}
_TRAJECTORY_RULE_BY_KEY: dict[str, SignalRule] = {r.key: r for r in TRAJECTORY_RULES}

# Pre-compile all patterns at module load time for performance.
_BENEFIT_COMPILED: list[tuple[SignalRule, list[re.Pattern[str]], list[re.Pattern[str]]]] = [
    (
        rule,
        [re.compile(p, re.IGNORECASE) for p in rule.patterns],
        [re.compile(p, re.IGNORECASE) for p in rule.negative_patterns],
    )
    for rule in BENEFIT_RULES
]

_TRAJECTORY_COMPILED: list[tuple[SignalRule, list[re.Pattern[str]], list[re.Pattern[str]]]] = [
    (
        rule,
        [re.compile(p, re.IGNORECASE) for p in rule.patterns],
        [re.compile(p, re.IGNORECASE) for p in rule.negative_patterns],
    )
    for rule in TRAJECTORY_RULES
]


def _firm_priors_to_signal_score(
    firm_data: dict,  # dict[str, FirmBenefit | FirmTrajectoryPrior]
    rule_by_key: dict[str, SignalRule],
    total_weight: float,
) -> SignalScore:
    """Convert approved firm benefit/trajectory data into a SignalScore.

    Only confirmed (×1.0) and likely (×0.65) statuses produce non-zero hits.
    Confidence = status_multiplier × prior.confidence.
    source is always "firm_profile".
    """
    hits: list[SignalHit] = []
    for key, prior in firm_data.items():
        rule = rule_by_key.get(key)
        if rule is None:
            continue
        multiplier = _FIRM_STATUS_MULTIPLIER.get(prior.status.value, 0.0)
        if multiplier == 0.0:
            continue
        confidence = round(multiplier * prior.confidence, 6)
        if confidence == 0.0:
            continue
        verified = f" (verified {prior.last_verified})" if prior.last_verified else ""
        hits.append(SignalHit(
            key=rule.key,
            label=rule.label,
            source="firm_profile",
            weight=rule.weight,
            confidence=confidence,
            matched_text=None,
            reason=(
                f"Approved firm profile: {rule.label.lower()} is "
                f"{prior.status.value}{verified}."
            ),
        ))
    hits.sort(key=lambda h: h.weight * h.confidence, reverse=True)
    raw = sum(h.weight * h.confidence for h in hits)
    score = round(min(max(raw / total_weight if total_weight else 0.0, 0.0), 1.0), 6)
    return SignalScore(score=score, hits=hits, missing_priority_keys=[])


def _load_approved_profiles(config_path: str) -> dict[str, FirmProfile]:
    """Load approved FirmProfile records keyed by firm_id. Returns {} on any error."""
    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        return {}
    profiles: dict[str, FirmProfile] = {}
    for entry in raw.get("firms", []):
        if not isinstance(entry, dict):
            continue
        try:
            p = FirmProfile(**entry)
            profiles[p.firm_id] = p
        except Exception:
            pass  # skip invalid/legacy entries silently
    return profiles


def _match_signal_rules(
    text: str,
    compiled_rules: list[tuple[SignalRule, list[re.Pattern[str]], list[re.Pattern[str]]]],
) -> SignalScore:
    """Match compiled signal rules against normalized text. One hit per key."""
    hits: list[SignalHit] = []
    total_weight = sum(rule.weight for rule, _, _ in compiled_rules)

    for rule, pos_patterns, neg_patterns in compiled_rules:
        matched_text: str | None = None
        for pat in pos_patterns:
            m = pat.search(text)
            if m:
                matched_text = m.group(0)[:60]
                break
        if matched_text is None:
            continue
        if any(neg.search(text) for neg in neg_patterns):
            continue
        hits.append(SignalHit(
            key=rule.key,
            label=rule.label,
            source="job_description",
            weight=rule.weight,
            confidence=1.0,
            matched_text=matched_text,
            reason=f"Job post mentions {rule.label.lower()}.",
        ))

    hits.sort(key=lambda h: h.weight, reverse=True)
    raw = sum(h.weight * h.confidence for h in hits)
    score = round(min(max(raw / total_weight if total_weight else 0.0, 0.0), 1.0), 6)
    return SignalScore(score=score, hits=hits, missing_priority_keys=[])


def _serialize_hits(hits: list[SignalHit]) -> str:
    """Serialize SignalHits to a compact, stable JSON string for persistence."""
    return json.dumps(
        [
            {
                "key": h.key,
                "label": h.label,
                "source": h.source,
                "weight": h.weight,
                "confidence": h.confidence,
                "matched_text": h.matched_text,
                "reason": h.reason,
            }
            for h in hits
        ],
        sort_keys=True,
    )


def format_top_reasons(hits: list[SignalHit], n: int = 3) -> str:
    """Return a compact comma-separated label string for the top n hits."""
    return ", ".join(h.label for h in hits[:n])


# ── Discipline detection (used by Scorer) ─────────────────────────────────────
# Defaults; can be overridden by config/scoring.yaml -> discipline_weights
DEFAULT_DISCIPLINE_WEIGHTS: dict[str, float] = {
    "structural": 1.0,
    "construction_engineering": 0.8,
    "construction_management": 0.8,
    "land_development": 0.7,
    "site_civil": 0.7,
    "transportation": 0.6,
    "municipal": 0.6,
    "water_resources": 0.5,
    "environmental": 0.5,
    "geotechnical": 0.5,
    "federal": 0.5,
}

DEFAULT_MATCH_FORMULA = {
    "base": 0.25,
    "discipline_weight": 0.25,
    "location_weight": 0.30,
    "benefit_weight": 0.10,
    "trajectory_weight": 0.10,
}

# ── Degree requirement patterns ───────────────────────────────────────────────
DEGREE_EXACT = re.compile(r"\bbs\s+civil\s+engineering\b", re.IGNORECASE)
DEGREE_RELATED = re.compile(
    r"\b(civil engineering technology|construction engineering|bachelor.*engineer)\b",
    re.IGNORECASE,
)

# Clearance values that mean "no clearance required" — treated as no knockout issue
# even though the field is non-empty. Normalized via .strip().lower() before matching.
_NO_CLEARANCE_VALUES: frozenset[str] = frozenset({
    "none", "", "n/a", "na", "not required", "no clearance", "no clearance required",
})

_NUMBER_WORDS: dict[str, float] = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
}

_CLEARANCE_NEGATIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bno\s+(?:active\s+)?(?:security\s+)?clearance\s+(?:is\s+)?required\b", re.IGNORECASE),
    re.compile(r"\b(?:security\s+)?clearance\s+(?:is\s+)?not\s+required\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+(?:a\s+)?(?:security\s+)?clearance\s+requirement\b", re.IGNORECASE),
)

_CLEARANCE_REQUIRED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:active|current|existing)\s+(?P<level>(?:top\s+secret|secret|ts/sci|sci|dod|security))\s+clearance\b", re.IGNORECASE),
    re.compile(r"\b(?P<level>top\s+secret|secret|ts/sci|sci|dod|security)\s+clearance\s+(?:required|needed|mandatory|preferred)\b", re.IGNORECASE),
    re.compile(r"\b(?:requires?|must\s+(?:have|possess|hold)|ability\s+to\s+obtain)\s+(?:an?\s+)?(?P<level>top\s+secret|secret|ts/sci|sci|dod|security)\s+clearance\b", re.IGNORECASE),
    re.compile(r"\bwith\s+(?:an?\s+)?(?P<level>top\s+secret|secret|ts/sci|sci|dod|security)\s+clearance\b", re.IGNORECASE),
    re.compile(r"\bsecurity\s+clearance\s+(?:required|needed|mandatory)\b", re.IGNORECASE),
)

_PE_REQUIRED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:p\.?\s*e\.?|pe|professional engineer)\s+(?:license|licensure|registration|certification)\s+(?:is\s+)?(?:required|needed|mandatory)\b", re.IGNORECASE),
    re.compile(r"\b(?:requires?|required|must\s+(?:have|possess|hold)|need(?:s)?(?:\s+to\s+have)?)\s+(?:an?\s+)?(?:active\s+)?(?:p\.?\s*e\.?|pe|professional engineer)(?:\s+(?:license|licensure|registration))?\b", re.IGNORECASE),
    re.compile(r"\b(?:registered|licensed)\s+professional\s+engineer\b", re.IGNORECASE),
)

_EIT_REQUIRED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:eit|engineer\s+in\s+training)\s+(?:certification|license|registration)?\s*(?:is\s+)?(?:required|needed|mandatory)\b", re.IGNORECASE),
    re.compile(r"\b(?:requires?|must\s+(?:have|possess|hold))\s+(?:an?\s+)?(?:eit|engineer\s+in\s+training)\b", re.IGNORECASE),
)

_MIN_YEARS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:minimum|at\s+least|requires?|required|must\s+have|need(?:s)?|with)\D{0,36}(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE),
    re.compile(r"\b(?P<years>\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:relevant\s+)?(?:professional\s+)?(?:experience|engineering|structural|construction|design)\b", re.IGNORECASE),
    re.compile(r"\b(?P<years>\d+(?:\.\d+)?)\s*[-–]\s*\d+(?:\.\d+)?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|engineering|structural|construction|design)\b", re.IGNORECASE),
)

_MIN_YEARS_WORD_PATTERN = re.compile(
    r"\b(?P<years>one|two|three|four|five|six|seven|eight|nine|ten)\+?\s+"
    r"(?:years?|yrs?)\s+(?:of\s+)?(?:relevant\s+)?(?:professional\s+)?"
    r"(?:experience|engineering|structural|construction|design)\b",
    re.IGNORECASE,
)

_SENIORITY_INFERENCES: tuple[tuple[re.Pattern[str], float, str], ...] = (
    (re.compile(r"\b(?:senior|sr\.?)\b", re.IGNORECASE), 5.0, "senior role title"),
    (re.compile(r"\b(?:lead|principal|staff)\s+(?:(?:civil|structural|construction|project)\s+)?engineer\b", re.IGNORECASE), 6.0, "lead/principal engineering role"),
    (re.compile(r"\bproject\s+manager\b", re.IGNORECASE), 5.0, "project manager role"),
    (re.compile(r"\bconstruction\s+manager\b", re.IGNORECASE), 5.0, "construction manager role"),
)

# Years thresholds used to tier a min_years signal into a major vs. minor gap.
# >= MAJOR: heavily weighted (contributes to LONG_SHOT). Between MINOR and
# MAJOR: a soft signal that only nudges a role to COMPETITIVE_STRETCH —
# per governance correction, a minor years gap must not auto-exclude an
# otherwise strong match.
_MAJOR_YEARS_THRESHOLD: float = 5.0
_MINOR_YEARS_THRESHOLD: float = 2.0


@dataclass
class ScoringContext:
    text: str = ""
    discipline: str = "unknown"
    discipline_weight: float = 0.5
    location: LocationScore | None = None
    major_gaps: list[str] = field(default_factory=list)
    minor_gaps: list[str] = field(default_factory=list)
    knockout_issues: list[str] = field(default_factory=list)
    benefit_score: float = 0.0
    trajectory_score: float = 0.0
    benefit_hits: list[SignalHit] = field(default_factory=list)
    trajectory_hits: list[SignalHit] = field(default_factory=list)
    stretch_category: StretchCategory = StretchCategory.QUALIFIED


class Scorer:
    def __init__(
        self,
        config_path: str = "config/scoring.yaml",
        firms_config_path: str = "config/firms.yaml",
    ):
        cfg = self._load_config(config_path)
        desktop_settings = ScoringSettingsService().active_settings()
        desktop_weights = desktop_settings.discipline_weights if desktop_settings.active else {}
        self.discipline_weights = {
            **DEFAULT_DISCIPLINE_WEIGHTS,
            **(cfg.get("discipline_weights") or {}),
            **desktop_weights,
        }
        self.formula = {**DEFAULT_MATCH_FORMULA, **(cfg.get("match_formula") or {})}
        self.penalty_multipliers = {
            **DEFAULT_SCORING_PENALTIES,
            **(desktop_settings.penalties if desktop_settings.active else {}),
        }
        loc_cfg = cfg.get("location") or {}
        scheme: SchemeName = (
            desktop_settings.location_scheme if desktop_settings.active else loc_cfg.get("scheme", "balanced")
        )
        try:
            self.location_scorer: LocationScorer | None = LocationScorer(scheme=scheme)
        except FileNotFoundError:
            logger.warning("cities.yaml not found — location scoring disabled")
            self.location_scorer = None
        # Approved firm profiles indexed by firm_id; empty when config is absent.
        self._firm_profiles: dict[str, FirmProfile] = _load_approved_profiles(firms_config_path)
        if self._firm_profiles:
            logger.info("Scorer: loaded %d approved firm profiles", len(self._firm_profiles))

    def score(self, job: CanonicalJob, firm: FirmProfile | None = None) -> CanonicalJob:
        """Score a job, optionally blending in approved firm intelligence.

        firm is resolved in this order:
          1. Explicit firm argument (highest priority, used in tests and direct calls).
          2. Auto-lookup by job.firm_id in self._firm_profiles (loaded at init).
          3. None — pure JD scoring, backward-compatible with all existing callers.

        DraftFirmProfile is never accepted here; only FirmProfile (approved) data
        affects scoring.
        """
        if firm is None and job.firm_id:
            firm = self._firm_profiles.get(job.firm_id)
        ctx = self._build_context(job, firm=firm)
        job.match_score = self._compute_match_score(ctx)
        job.benefit_score = ctx.benefit_score
        job.career_trajectory_score = ctx.trajectory_score
        job.stretch_category = ctx.stretch_category
        job.benefit_reasons = _serialize_hits(ctx.benefit_hits)
        job.trajectory_reasons = _serialize_hits(ctx.trajectory_hits)
        return job

    def score_location(self, job: CanonicalJob) -> LocationScore | None:
        """Public: get the LocationScore for a job (used by reporting)."""
        if not self.location_scorer:
            return None
        return self.location_scorer.score(job.location_city, job.location_state)

    def _build_context(self, job: CanonicalJob, firm: FirmProfile | None = None) -> ScoringContext:
        ctx = ScoringContext()
        ctx.text = (
            (job.title or "") + " " +
            (job.description_normalized or "") + " " +
            (job.location_city or "") + " " +
            (job.location_state or "")
        ).lower()

        self._infer_missing_knockouts(job, ctx.text)
        ctx.discipline, ctx.discipline_weight = self._detect_discipline(ctx.text)
        if self.location_scorer:
            ctx.location = self.location_scorer.score(job.location_city, job.location_state)
        ctx.major_gaps, ctx.minor_gaps, ctx.knockout_issues = self._assess_gaps(job)

        jd_benefit = _match_signal_rules(ctx.text, _BENEFIT_COMPILED)
        jd_traj    = _match_signal_rules(ctx.text, _TRAJECTORY_COMPILED)

        if firm is not None:
            # Blend JD signals with approved firm-profile priors.
            fp_benefit = _firm_priors_to_signal_score(
                firm.benefits, _BENEFIT_RULE_BY_KEY, _BENEFIT_TOTAL_WEIGHT
            )
            fp_traj = _firm_priors_to_signal_score(
                firm.trajectory, _TRAJECTORY_RULE_BY_KEY, _TRAJECTORY_TOTAL_WEIGHT
            )
            ctx.benefit_score = round(
                _JD_BENEFIT_WEIGHT * jd_benefit.score
                + _FIRM_BENEFIT_WEIGHT * fp_benefit.score,
                6,
            )
            ctx.trajectory_score = round(
                _JD_TRAJ_WEIGHT * jd_traj.score
                + _FIRM_TRAJ_WEIGHT * fp_traj.score,
                6,
            )
            # Merge hit lists: JD hits first, then firm hits for keys not already in JD.
            # Sorted by weight * confidence descending so top reasons reflect contribution.
            combined_benefit = jd_benefit.hits + fp_benefit.hits
            combined_traj    = jd_traj.hits + fp_traj.hits
            ctx.benefit_hits    = sorted(combined_benefit, key=lambda h: h.weight * h.confidence, reverse=True)
            ctx.trajectory_hits = sorted(combined_traj,    key=lambda h: h.weight * h.confidence, reverse=True)
        else:
            ctx.benefit_score    = jd_benefit.score
            ctx.trajectory_score = jd_traj.score
            ctx.benefit_hits     = jd_benefit.hits
            ctx.trajectory_hits  = jd_traj.hits

        ctx.stretch_category = self._classify_stretch(ctx)
        return ctx

    def _detect_discipline(self, text: str) -> tuple[str, float]:
        scores: dict[str, float] = {}
        w = self.discipline_weights
        if "structural" in text or "ram structural" in text or "seismic" in text:
            scores["structural"] = w["structural"]
        if "construction management" in text or "construction manager" in text:
            scores["construction_management"] = w["construction_management"]
        if "construction engineer" in text or "field engineer" in text:
            scores["construction_engineering"] = w["construction_engineering"]
        if "land development" in text or "site civil" in text or "site design" in text:
            scores["land_development"] = w["land_development"]
        if "transportation" in text or "highway" in text or "roadway" in text:
            scores["transportation"] = w["transportation"]
        if "water resource" in text or "hydraulic" in text or "hydrology" in text or "hec-ras" in text:
            scores["water_resources"] = w["water_resources"]
        if "environmental" in text:
            scores["environmental"] = w["environmental"]
        if "geotechnical" in text or "geotech" in text or " soil" in text:
            scores["geotechnical"] = w["geotechnical"]
        if "municipal" in text or "public works" in text:
            scores["municipal"] = w["municipal"]

        if not scores:
            return "civil", 0.5
        best = max(scores, key=lambda k: scores[k])
        return best, scores[best]

    @classmethod
    def _infer_missing_knockouts(cls, job: CanonicalJob, text: str) -> None:
        ko = job.knockout or KnockoutFields()
        job.knockout = ko

        if ko.clearance is None:
            ko.clearance = cls._detect_clearance_requirement(text)
        if ko.pe_required is None:
            ko.pe_required = cls._detect_pe_requirement(text)
        if ko.eit_required is None:
            ko.eit_required = cls._detect_eit_requirement(text)

        detected_years = cls._detect_min_years(text)
        inferred_years = cls._infer_seniority_years(text)
        candidates = [
            value
            for value in (ko.min_years, detected_years, inferred_years)
            if value is not None
        ]
        if candidates:
            ko.min_years = max(candidates)

    @staticmethod
    def _detect_clearance_requirement(text: str) -> str | None:
        if any(pattern.search(text) for pattern in _CLEARANCE_NEGATIVE_PATTERNS):
            return None
        for pattern in _CLEARANCE_REQUIRED_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            level = match.groupdict().get("level")
            if level:
                normalized = " ".join(level.split()).title().replace("Ts/Sci", "TS/SCI")
                return "Security clearance" if normalized == "Security" else normalized
            return "Security clearance"
        return None

    @staticmethod
    def _detect_pe_requirement(text: str) -> bool | None:
        if re.search(r"\b(?:pe|p\.?\s*e\.?|professional engineer)\s+(?:preferred|a plus|desired)\b", text, re.IGNORECASE):
            return None
        if re.search(r"\b(?:under|supervised by|mentored by)\s+(?:a\s+)?(?:licensed|registered)\s+professional\s+engineer\b", text, re.IGNORECASE):
            return None
        return True if any(pattern.search(text) for pattern in _PE_REQUIRED_PATTERNS) else None

    @staticmethod
    def _detect_eit_requirement(text: str) -> bool | None:
        if re.search(r"\b(?:eit|engineer\s+in\s+training)\s+(?:preferred|a plus|desired|path|support)\b", text, re.IGNORECASE):
            return None
        return True if any(pattern.search(text) for pattern in _EIT_REQUIRED_PATTERNS) else None

    @staticmethod
    def _detect_min_years(text: str) -> float | None:
        years: list[float] = []
        for pattern in _MIN_YEARS_PATTERNS:
            for match in pattern.finditer(text):
                years.append(float(match.group("years")))
        for match in _MIN_YEARS_WORD_PATTERN.finditer(text):
            value = _NUMBER_WORDS.get(match.group("years").lower())
            if value is not None:
                years.append(value)
        return max(years) if years else None

    @staticmethod
    def _infer_seniority_years(text: str) -> float | None:
        years: list[float] = []
        for pattern, inferred_years, _reason in _SENIORITY_INFERENCES:
            if pattern.search(text):
                years.append(inferred_years)
        return max(years) if years else None

    def _assess_gaps(self, job: CanonicalJob) -> tuple[list[str], list[str], list[str]]:
        """Classify detected knockout signals into major vs. minor risk gaps.

        Clearance, PE licensure, and a strong years/seniority signal (>=
        _MAJOR_YEARS_THRESHOLD) are "major" gaps: they demote a role to
        LONG_SHOT and apply a heavy match-score penalty, but the job is
        still scored, categorized, and surfaced — never silently dropped.
        A years requirement above the new-grad baseline but below the major
        threshold is a "minor" gap: it only nudges a role to
        COMPETITIVE_STRETCH so an otherwise-strong match stays visible.
        """
        ko = job.knockout
        major: list[str] = []
        minor: list[str] = []
        issues: list[str] = []

        if ko.pe_required:
            major.append("pe_required")
            issues.append("PE license required")
        clearance = (ko.clearance or "").strip()
        if clearance and clearance.lower() not in _NO_CLEARANCE_VALUES:
            major.append("clearance")
            issues.append(f"Security clearance required: {clearance}")
        if ko.min_years:
            if ko.min_years >= _MAJOR_YEARS_THRESHOLD:
                major.append("min_years")
                issues.append(f"Min {ko.min_years:.0f} years required")
            elif ko.min_years > _MINOR_YEARS_THRESHOLD:
                minor.append("min_years")
                issues.append(f"Min {ko.min_years:.0f} years required (minor gap)")
        if ko.eit_required:
            minor.append("eit_required")
            issues.append("EIT certification required")
        relocation = (ko.relocation or "").strip()
        if relocation and relocation.lower() not in {"none", "n/a", "na", "not required", "no relocation"}:
            minor.append("relocation")
            issues.append(f"Relocation requirement: {relocation}")
        return major, minor, issues

    def _classify_stretch(self, ctx: "ScoringContext") -> StretchCategory:
        if ctx.major_gaps:
            return StretchCategory.LONG_SHOT
        if ctx.minor_gaps:
            return StretchCategory.COMPETITIVE_STRETCH
        if DEGREE_RELATED.search(ctx.text):
            return StretchCategory.QUALIFIED
        if DEGREE_EXACT.search(ctx.text):
            return StretchCategory.COMPETITIVE_STRETCH
        return StretchCategory.QUALIFIED

    def _compute_match_score(self, ctx: ScoringContext) -> float:
        f = self.formula
        major_count = len(ctx.major_gaps)
        base = f["base"] * (0.5 if major_count else 1.0)

        discipline_contribution = ctx.discipline_weight * f["discipline_weight"]
        location_contribution = (
            ctx.location.normalized * f["location_weight"]
            if ctx.location else 0.4 * f["location_weight"]   # fallback if no scorer
        )
        benefit_contribution = ctx.benefit_score * f["benefit_weight"]
        trajectory_contribution = ctx.trajectory_score * f["trajectory_weight"]

        raw = (
            base
            + discipline_contribution
            + location_contribution
            + benefit_contribution
            + trajectory_contribution
        )

        # Weighted penalty by gap severity — never an automatic exclusion.
        # A single major gap (clearance, PE licensure, or strong seniority)
        # demotes the role; stacking two or more major gaps demotes it
        # heavily so it won't surface as a top "qualified" recommendation.
        # A minor years-only gap is penalized lightly so an otherwise strong
        # match can still stand as a competitive stretch.
        if ctx.major_gaps:
            multiplier = self._combined_gap_multiplier(ctx.major_gaps, major=True)
            if major_count >= 2:
                multiplier = min(multiplier, 0.40)
            raw *= multiplier
        elif ctx.minor_gaps:
            raw *= self._combined_gap_multiplier(ctx.minor_gaps, major=False)

        return round(min(max(raw, 0.0), 1.0), 4)

    def _combined_gap_multiplier(self, gaps: list[str], *, major: bool) -> float:
        multiplier = 1.0
        for gap in gaps:
            key = self._penalty_key_for_gap(gap, major=major)
            multiplier *= self.penalty_multipliers.get(key, 0.70 if major else 0.90)
        return max(0.0, min(multiplier, 1.0))

    @staticmethod
    def _penalty_key_for_gap(gap: str, *, major: bool) -> str:
        if gap == "clearance":
            return "active_security_clearance_required"
        if gap == "pe_required":
            return "PE_required"
        if gap == "eit_required":
            return "EIT_required"
        if gap == "relocation":
            return "relocation_mismatch"
        if gap == "min_years":
            return "years_gap_major" if major else "years_gap_minor"
        return "years_gap_major" if major else "years_gap_minor"

    def _load_config(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        with open(p) as f:
            return yaml.safe_load(f) or {}
