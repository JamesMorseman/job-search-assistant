"""Read-only wiring between an opportunity's location and the pure
`job_search.reporting.location_economics_preview` rationale module.

This module performs no scoring computation of its own. It:

1. Reads `location_city`/`location_state` off an already-fetched
   `AtlasOpportunityDetail` (itself fetched read-only via
   `AtlasDataService.get_opportunity`, which already mediates all SQLite
   access per the dashboard service boundary).
2. Re-derives a `LocationScore` via the existing, side-effect-free
   `LocationScorer` (a pure city/state lookup against `config/cities.yaml`,
   not a DB write) since location score is not persisted on the `jobs` row.
3. Looks up the full `MetroArea` reference data (raw salary/rent/affordability
   figures) via `LocationScorer.get_metro`, also a pure in-memory lookup.
4. Hands both to `build_location_economics_preview`, which does the actual
   advisory-language formatting.

No new database writes, no re-scoring.
"""

from __future__ import annotations

from functools import lru_cache

from job_search.location.scorer import LocationScorer
from job_search.reporting.location_economics_preview import (
    LocationEconomicsPreview,
    build_location_economics_preview,
)
from job_search.services.atlas import AtlasOpportunityDetail


@lru_cache(maxsize=1)
def _location_scorer() -> LocationScorer | None:
    """Lazily construct a LocationScorer once per process.

    Pure read against config/cities.yaml — no DB access, no mutation.
    Mirrors the same lazy-cache pattern used in
    job_search.services.score_preview_service.
    """
    try:
        return LocationScorer()
    except FileNotFoundError:
        return None


def build_location_economics_preview_for_opportunity(
    opportunity: AtlasOpportunityDetail,
) -> LocationEconomicsPreview:
    """Build a read-only location-economics rationale for an already-fetched opportunity.

    Performs no database writes and does not mutate `opportunity`.
    """
    scorer = _location_scorer()
    if scorer is None:
        return build_location_economics_preview(None)

    location_score = scorer.score(opportunity.location_city, opportunity.location_state)
    metro = scorer.get_metro(location_score.metro_id)
    return build_location_economics_preview(location_score, metro=metro)
