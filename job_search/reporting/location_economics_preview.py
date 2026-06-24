"""Pure location/salary economics rationale module.

Explains the economics behind a posting's already-computed `LocationScore`
and (optionally) the underlying `MetroArea` reference data, in
advisory/explanatory language. This module performs NO database reads, NO
file IO, NO network calls, and NO LLM calls — it only formats data handed to
it by the caller, mirroring the pattern in
`job_search.reporting.score_preview`.

Language is deliberately advisory ("may indicate...", "is often associated
with...") rather than deterministic ("this means...", "you should..."),
since cost-of-living and relocation tradeoffs are personal and the
underlying city_guide.pdf framework is itself a heuristic scoring model, not
a guarantee about any individual's actual outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from job_search.location.models import LocationScore, MetroArea

# Human-readable labels for the five city_guide.pdf dimensions.
_DIMENSION_LABELS: dict[str, str] = {
    "ce": "Career/job-market strength",
    "col": "Cost-of-living-adjusted salary",
    "home": "Home affordability",
    "mj": "Cannabis legal status",
    "dating": "Dating market size",
}


@dataclass(frozen=True)
class LocationEconomicsPreview:
    """Advisory, human-readable explanation of a posting's location economics."""

    metro_name: str | None
    composite: float | None
    ranked: bool
    match_kind: str
    headline: str = ""
    dimension_notes: list[str] = field(default_factory=list)
    economics_notes: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines: list[str] = []
        if self.headline:
            lines.append(self.headline)
        lines.extend(self.dimension_notes)
        lines.extend(self.economics_notes)
        for caveat in self.caveats:
            lines.append(f"Note: {caveat}")
        return "\n".join(lines)


def _format_money_k(value_k: int | None) -> str | None:
    if value_k is None:
        return None
    return f"${value_k:,}k" if value_k >= 1000 else f"${value_k}k"


def _headline_for(location_score: LocationScore) -> str:
    if not location_score.ranked:
        if location_score.match_kind == "remote":
            return "This posting is remote or has no fixed location, so location economics do not directly apply."
        return "This posting's location is not in Atlas's ranked metro framework; an unranked fallback estimate is shown."
    name = location_score.metro_name or "this metro"
    return f"{name} scores {location_score.composite:.1f}/100 on Atlas's location framework — this may indicate the overall relocation/lifestyle fit, not a guarantee of outcome."


def _dimension_notes_for(location_score: LocationScore) -> list[str]:
    if not location_score.ranked:
        return []
    notes: list[str] = []
    dims = location_score.dimensions
    for key, label in _DIMENSION_LABELS.items():
        value = getattr(dims, key, None)
        if value is None:
            continue
        notes.append(f"{label}: {value:.1f}/5 — may indicate relative {label.lower()} versus other ranked metros.")
    return notes


def _economics_notes_for(metro: MetroArea | None) -> list[str]:
    if metro is None:
        return []
    notes: list[str] = []

    salary = _format_money_k(metro.salary_k)
    real_net = _format_money_k(metro.real_net_k)
    if salary and real_net:
        notes.append(
            f"Reference salary for this metro is around {salary}, which is approximately {real_net} "
            "after regional price-parity adjustment — this may indicate relative purchasing power, not "
            "an offer prediction for this specific posting."
        )
    elif salary:
        notes.append(f"Reference salary for this metro is around {salary} (city_guide.pdf reference data).")

    if metro.rent_1br is not None:
        notes.append(
            f"Typical 1BR rent reference for this metro is around ${metro.rent_1br:,}/month, which may "
            "indicate relative housing cost versus other ranked metros."
        )

    if metro.years_20pct_solo is not None:
        notes.append(
            f"At reference income, saving a 20% down payment solo may take roughly "
            f"{metro.years_20pct_solo:.1f} years in this metro — a rough affordability signal, not "
            "financial advice."
        )

    if metro.entry_jobs is not None and metro.total_jobs:
        notes.append(
            f"This metro's reference data lists about {metro.entry_jobs:,} entry-level postings out of "
            f"{metro.total_jobs:,} tracked — this may indicate relative entry-level market depth."
        )

    return notes


def build_location_economics_preview(
    location_score: LocationScore | None,
    metro: MetroArea | None = None,
) -> LocationEconomicsPreview:
    """Assemble a LocationEconomicsPreview from an already-computed LocationScore.

    `metro` is optional supplementary reference data (e.g. from
    `LocationScorer.get_metro(location_score.metro_id)`) used only to add raw
    economics figures (reference salary, rent, affordability years) — the
    preview still produces useful dimension-level rationale without it.
    """
    if location_score is None:
        return LocationEconomicsPreview(
            metro_name=None,
            composite=None,
            ranked=False,
            match_kind="unknown",
            headline="No location data is available for this posting yet.",
        )

    caveats = [
        "These figures are reference estimates from Atlas's metro framework "
        "(city_guide.pdf), not real-time market data or a personalized financial projection.",
    ]
    if not location_score.ranked:
        caveats.append(
            "This metro is not individually ranked in Atlas's framework, so a fallback "
            "estimate is used instead of metro-specific figures."
        )

    return LocationEconomicsPreview(
        metro_name=location_score.metro_name,
        composite=location_score.composite if location_score.ranked else None,
        ranked=location_score.ranked,
        match_kind=location_score.match_kind,
        headline=_headline_for(location_score),
        dimension_notes=_dimension_notes_for(location_score),
        economics_notes=_economics_notes_for(metro),
        caveats=caveats,
    )
