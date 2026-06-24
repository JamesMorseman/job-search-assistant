"""Read-only wiring between persisted job score data and the pure
`job_search.reporting.score_preview` explanation module.

This module performs no scoring computation of its own. It:

1. Reads already-persisted score fields off an `AtlasOpportunityDetail`
   (itself fetched read-only via `AtlasDataService.get_opportunity`, which
   already mediates all SQLite access per the dashboard service boundary).
2. Reconstructs the lightweight `SignalHit`/`SignalScore` objects that
   `score_preview.py` expects, from the JSON-serialized reasons already
   stored in the `jobs` table (see `job_search.ingestion.scoring._serialize_hits`
   for the persisted shape).
3. Optionally re-derives a `LocationScore` via the existing, side-effect-free
   `LocationScorer` (a pure city/state lookup against `config/cities.yaml`,
   not a DB write) since location score is not persisted on the `jobs` row.
4. Hands all of the above to `build_score_preview`, which does the actual
   formatting.

No new database writes, no re-scoring of benefit/trajectory/match
score — those values are read exactly as already computed and stored.

Note: contribution percentages use `DEFAULT_MATCH_FORMULA`'s weights, not
any custom overrides from `config/scoring.yaml`. This is a deliberate
simplification for a read-only explanation surface — the underlying
benefit/trajectory/match scores themselves are always the real persisted
values regardless of which weights were used to compute the percentage
breakdown shown here. If a future package finds this drifts from the
config in practice, swap in `Scorer._load_config`'s merged formula dict.
"""

from __future__ import annotations

from functools import lru_cache

from job_search.ingestion.scoring import DEFAULT_MATCH_FORMULA, SignalHit, SignalScore
from job_search.location.scorer import LocationScorer
from job_search.reporting.score_preview import ScorePreview, build_score_preview
from job_search.services.atlas import AtlasOpportunityDetail


def _hits_from_reasons(reasons: list) -> list[SignalHit]:
    """Reconstruct SignalHit objects from persisted reason dicts.

    Tolerant of partial/missing keys (older rows, manual edits) — any
    malformed entry is skipped rather than raising, since this is a
    best-effort explanation surface, not a validation path.
    """
    hits: list[SignalHit] = []
    for item in reasons:
        if not isinstance(item, dict):
            continue
        try:
            hits.append(
                SignalHit(
                    key=item.get("key", ""),
                    label=item.get("label", item.get("key", "signal")),
                    source=item.get("source", "jd"),
                    weight=float(item.get("weight", 0.0)),
                    confidence=float(item.get("confidence", 1.0)),
                    matched_text=item.get("matched_text"),
                    reason=item.get("reason", ""),
                )
            )
        except (TypeError, ValueError):
            continue
    return hits


def _signal_score_from_reasons(score: float, reasons: list) -> SignalScore:
    hits = _hits_from_reasons(reasons)
    return SignalScore(score=score or 0.0, hits=hits, missing_priority_keys=[])


@lru_cache(maxsize=1)
def _location_scorer() -> LocationScorer | None:
    """Lazily construct a LocationScorer once per process.

    Pure read against config/cities.yaml — no DB access, no mutation. Cached
    because the underlying scorer parses the YAML file once; failures (e.g.
    cities.yaml missing) degrade to no location component rather than
    raising, matching `Scorer.__init__`'s own fallback behavior.
    """
    try:
        return LocationScorer()
    except FileNotFoundError:
        return None


def build_score_preview_for_opportunity(
    opportunity: AtlasOpportunityDetail,
) -> ScorePreview:
    """Build a read-only ScorePreview explanation for an already-fetched opportunity.

    Uses only data already persisted on the opportunity (benefit/trajectory
    score + reasons, overall match score, stretch category) plus a
    side-effect-free location re-lookup. Performs no database writes and
    does not mutate `opportunity`.
    """
    benefit = _signal_score_from_reasons(opportunity.benefit_score, opportunity.benefit_reasons)
    trajectory = _signal_score_from_reasons(
        opportunity.career_trajectory_score, opportunity.trajectory_reasons
    )

    location = None
    scorer = _location_scorer()
    if scorer is not None:
        location = scorer.score(opportunity.location_city, opportunity.location_state)

    return build_score_preview(
        overall_score=opportunity.match_score,
        stretch_category=opportunity.stretch_category,
        benefit=benefit,
        benefit_weight=DEFAULT_MATCH_FORMULA.get("benefit_weight"),
        trajectory=trajectory,
        trajectory_weight=DEFAULT_MATCH_FORMULA.get("trajectory_weight"),
        location=location,
        location_weight=DEFAULT_MATCH_FORMULA.get("location_weight"),
    )
