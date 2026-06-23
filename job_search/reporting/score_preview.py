"""Pure score-preview / explanation module.

Explains how a posting's match score breaks down, given already-computed
score components supplied by the caller (objects / dicts from fixtures or
the live scoring engine's output). This module performs NO database reads,
NO file IO, NO network calls, and NO LLM calls — it only formats data that
is handed to it.

Contrast with `job_search.reporting.daily_report`, which is DB/IO-coupled
(`get_db`, `tempfile`, `Path`, `SheetsLogger`) and is out of scope for this
module. Nothing here imports or calls into `daily_report`.

Callers are expected to pass already-computed result objects from the
scoring engine (e.g. `job_search.ingestion.scoring.SignalScore`,
`job_search.evidence.types.EvidenceScore`,
`job_search.location.models.LocationScore`) — this module only reads their
public attributes; it does not construct or mutate them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from job_search.evidence.types import EvidenceScore
from job_search.ingestion.scoring import SignalHit, SignalScore, format_top_reasons
from job_search.location.models import LocationScore

# Number of top signal reasons to surface per signal category by default.
DEFAULT_TOP_N_REASONS = 3


@dataclass(frozen=True)
class ScoreComponentPreview:
    """Human-readable explanation of a single named score component."""

    name: str
    label: str
    score: float
    weight: float | None = None
    contribution: float | None = None
    top_reasons: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass(frozen=True)
class ScorePreview:
    """Structured, human-readable explanation of a posting's overall score."""

    overall_score: float | None
    components: list[ScoreComponentPreview] = field(default_factory=list)
    headline: str = ""
    notes: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        """Render the preview as a multi-line human-readable report."""
        lines: list[str] = []
        if self.headline:
            lines.append(self.headline)
        for component in self.components:
            lines.append(_format_component_line(component))
        for note in self.notes:
            lines.append(f"Note: {note}")
        return "\n".join(lines)


def _format_component_line(component: ScoreComponentPreview) -> str:
    pct = f"{component.score * 100:.1f}%"
    parts = [f"{component.label}: {pct}"]
    if component.contribution is not None:
        parts.append(f"(contributes {component.contribution * 100:.1f}% to overall)")
    if component.top_reasons:
        parts.append("— " + ", ".join(component.top_reasons))
    elif component.summary:
        parts.append(f"— {component.summary}")
    return " ".join(parts)


def explain_signal_score(
    name: str,
    label: str,
    signal_score: SignalScore | None,
    *,
    weight: float | None = None,
    overall_score: float | None = None,
    top_n: int = DEFAULT_TOP_N_REASONS,
) -> ScoreComponentPreview:
    """Build a preview for a benefit/trajectory-style SignalScore component.

    `signal_score` is the already-computed result object (e.g. produced by
    the ingestion scoring engine and supplied by the caller). This function
    does not compute scores — it only formats an existing SignalScore.
    """
    if signal_score is None:
        return ScoreComponentPreview(
            name=name,
            label=label,
            score=0.0,
            weight=weight,
            contribution=None,
            top_reasons=[],
            summary="no data supplied",
        )

    contribution = None
    if weight is not None and overall_score:
        contribution = (signal_score.score * weight) / overall_score if overall_score else None

    top_reasons_str = format_top_reasons(signal_score.hits, n=top_n)
    top_reasons = [r.strip() for r in top_reasons_str.split(",") if r.strip()]

    summary = ""
    if not top_reasons:
        summary = "no explicit signals detected"
        if signal_score.missing_priority_keys:
            summary += f" (missing: {', '.join(signal_score.missing_priority_keys)})"

    return ScoreComponentPreview(
        name=name,
        label=label,
        score=signal_score.score,
        weight=weight,
        contribution=contribution,
        top_reasons=top_reasons,
        summary=summary,
    )


def explain_evidence_scores(
    name: str,
    label: str,
    evidence_scores: list[EvidenceScore] | None,
    *,
    weight: float | None = None,
    top_n: int = DEFAULT_TOP_N_REASONS,
) -> ScoreComponentPreview:
    """Build a preview for a list of already-computed EvidenceScore items.

    The aggregate "score" shown is the average of the supplied item scores
    (0.0 when the list is empty), matching the intent of an evidence-match
    quality summary rather than re-deriving any engine logic.
    """
    if not evidence_scores:
        return ScoreComponentPreview(
            name=name,
            label=label,
            score=0.0,
            weight=weight,
            top_reasons=[],
            summary="no evidence items supplied",
        )

    avg_score = sum(e.score for e in evidence_scores) / len(evidence_scores)
    ranked = sorted(evidence_scores, key=lambda e: e.score, reverse=True)[:top_n]
    top_reasons: list[str] = []
    for e in ranked:
        if e.reasons:
            top_reasons.append(e.reasons[0])
        else:
            top_reasons.append(e.item.text[:60])

    return ScoreComponentPreview(
        name=name,
        label=label,
        score=avg_score,
        weight=weight,
        top_reasons=top_reasons,
    )


def explain_location_score(
    location_score: LocationScore | None,
    *,
    weight: float | None = None,
) -> ScoreComponentPreview:
    """Build a preview for an already-computed LocationScore."""
    if location_score is None:
        return ScoreComponentPreview(
            name="location",
            label="Location fit",
            score=0.0,
            weight=weight,
            summary="no location data supplied",
        )

    summary_parts = []
    if location_score.metro_name:
        summary_parts.append(location_score.metro_name)
    summary_parts.append(f"match: {location_score.match_kind}")
    if not location_score.ranked:
        summary_parts.append("unranked/fallback")

    return ScoreComponentPreview(
        name="location",
        label="Location fit",
        score=location_score.normalized,
        weight=weight,
        summary=", ".join(summary_parts),
    )


def build_score_preview(
    *,
    overall_score: float | None = None,
    stretch_category: str | None = None,
    benefit: SignalScore | None = None,
    benefit_weight: float | None = None,
    trajectory: SignalScore | None = None,
    trajectory_weight: float | None = None,
    location: LocationScore | None = None,
    location_weight: float | None = None,
    evidence: list[EvidenceScore] | None = None,
    evidence_weight: float | None = None,
    extra_notes: list[str] | None = None,
) -> ScorePreview:
    """Assemble a full ScorePreview from supplied, already-computed components.

    All arguments are pre-computed results / fixtures handed in by the
    caller (e.g. unit-test fixtures, or live SignalScore/LocationScore/
    EvidenceScore objects produced elsewhere). This function performs no
    scoring computation of its own — it only explains data it receives.
    """
    components: list[ScoreComponentPreview] = []

    if benefit is not None:
        components.append(
            explain_signal_score(
                "benefit",
                "Benefit signals",
                benefit,
                weight=benefit_weight,
                overall_score=overall_score,
            )
        )
    if trajectory is not None:
        components.append(
            explain_signal_score(
                "trajectory",
                "Career trajectory signals",
                trajectory,
                weight=trajectory_weight,
                overall_score=overall_score,
            )
        )
    if location is not None:
        components.append(explain_location_score(location, weight=location_weight))
    if evidence is not None:
        components.append(
            explain_evidence_scores(
                "evidence",
                "Resume/cover evidence match",
                evidence,
                weight=evidence_weight,
            )
        )

    headline = ""
    if overall_score is not None:
        headline = f"Overall match score: {overall_score * 100:.1f}%"
        if stretch_category:
            headline += f" ({stretch_category})"

    return ScorePreview(
        overall_score=overall_score,
        components=components,
        headline=headline,
        notes=list(extra_notes or []),
    )
