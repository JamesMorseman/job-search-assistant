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
from job_search.models import CanonicalJob, StretchCategory

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
        key="rotation_or_growth",
        label="Rotation or growth path",
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


@dataclass
class ScoringContext:
    text: str = ""
    discipline: str = "unknown"
    discipline_weight: float = 0.5
    location: LocationScore | None = None
    knockout_ok: bool = True
    knockout_issues: list[str] = field(default_factory=list)
    benefit_score: float = 0.0
    trajectory_score: float = 0.0
    benefit_hits: list[SignalHit] = field(default_factory=list)
    trajectory_hits: list[SignalHit] = field(default_factory=list)
    stretch_category: StretchCategory = StretchCategory.QUALIFIED


class Scorer:
    def __init__(self, config_path: str = "config/scoring.yaml"):
        cfg = self._load_config(config_path)
        self.discipline_weights = {
            **DEFAULT_DISCIPLINE_WEIGHTS,
            **(cfg.get("discipline_weights") or {}),
        }
        self.formula = {**DEFAULT_MATCH_FORMULA, **(cfg.get("match_formula") or {})}
        loc_cfg = cfg.get("location") or {}
        scheme: SchemeName = loc_cfg.get("scheme", "balanced")
        try:
            self.location_scorer: LocationScorer | None = LocationScorer(scheme=scheme)
        except FileNotFoundError:
            logger.warning("cities.yaml not found — location scoring disabled")
            self.location_scorer = None

    def score(self, job: CanonicalJob) -> CanonicalJob:
        ctx = self._build_context(job)
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

    def _build_context(self, job: CanonicalJob) -> ScoringContext:
        ctx = ScoringContext()
        ctx.text = (
            (job.title or "") + " " +
            (job.description_normalized or "") + " " +
            (job.location_city or "") + " " +
            (job.location_state or "")
        ).lower()

        ctx.discipline, ctx.discipline_weight = self._detect_discipline(ctx.text)
        if self.location_scorer:
            ctx.location = self.location_scorer.score(job.location_city, job.location_state)
        ctx.knockout_ok, ctx.knockout_issues = self._check_knockouts(job)
        benefit_signal = _match_signal_rules(ctx.text, _BENEFIT_COMPILED)
        trajectory_signal = _match_signal_rules(ctx.text, _TRAJECTORY_COMPILED)
        ctx.benefit_score = benefit_signal.score
        ctx.benefit_hits = benefit_signal.hits
        ctx.trajectory_score = trajectory_signal.score
        ctx.trajectory_hits = trajectory_signal.hits
        ctx.stretch_category = self._classify_stretch(job, ctx.text)
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

    def _check_knockouts(self, job: CanonicalJob) -> tuple[bool, list[str]]:
        ko = job.knockout
        issues: list[str] = []
        if ko.pe_required:
            issues.append("PE license required — not yet eligible")
        if ko.min_years and ko.min_years > 2:
            issues.append(f"Min {ko.min_years:.0f} years required — new grad")
        if ko.clearance and ko.clearance.lower() not in ("none", ""):
            issues.append(f"Security clearance required: {ko.clearance}")
        return len(issues) == 0, issues

    def _classify_stretch(self, job: CanonicalJob, text: str) -> StretchCategory:
        if DEGREE_RELATED.search(text):
            return StretchCategory.QUALIFIED
        if DEGREE_EXACT.search(text):
            return StretchCategory.COMPETITIVE_STRETCH
        if job.knockout.pe_required:
            return StretchCategory.LONG_SHOT
        if job.knockout.min_years and job.knockout.min_years >= 5:
            return StretchCategory.LONG_SHOT
        return StretchCategory.QUALIFIED

    def _compute_match_score(self, ctx: ScoringContext) -> float:
        f = self.formula
        base = f["base"] * (0.5 if not ctx.knockout_ok else 1.0)

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

        # Stretch penalty
        if ctx.stretch_category == StretchCategory.COMPETITIVE_STRETCH:
            raw *= 0.92
        elif ctx.stretch_category == StretchCategory.LONG_SHOT:
            raw *= 0.75

        return round(min(max(raw, 0.0), 1.0), 4)

    def _load_config(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        with open(p) as f:
            return yaml.safe_load(f) or {}
