"""Tests for the location-scoring framework.

Reference values pulled from docs/city_guide.pdf (the analytical model).
Composite tolerances allow ±0.5 to account for rounding differences.
"""

import pytest

from job_search.location import LocationScorer


@pytest.fixture(scope="module")
def scorer():
    return LocationScorer(scheme="balanced")


# ── Composite calculation matches PDF reference values ───────────────────────

@pytest.mark.parametrize(
    "metro_id,scheme,expected",
    [
        ("cleveland_oh",   "balanced",     76.5),
        ("cleveland_oh",   "fit_first",    82.1),
        ("cleveland_oh",   "career_first", 67.9),
        ("cleveland_oh",   "career_only",  57.0),
        ("dc_nova",        "balanced",     71.3),
        ("dc_nova",        "career_first", 70.4),
        ("dc_nova",        "career_only",  75.8),
        ("houston_tx",     "balanced",     68.3),
        ("houston_tx",     "career_relax", 72.7),
        ("nyc_ny",         "balanced",     63.5),
        ("nyc_ny",         "fit_first",    78.8),
        ("sf_bay_ca",      "career_only",  38.7),
    ],
)
def test_composite_matches_pdf(scorer, metro_id, scheme, expected):
    actual = scorer.composite_for(metro_id, scheme=scheme)
    assert abs(actual - expected) < 0.6, (
        f"{metro_id}/{scheme}: expected {expected}, got {actual}"
    )


# ── City matching ────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "city,state,expected_metro_id,expected_kind",
    [
        ("Cleveland",       "OH", "cleveland_oh",     "exact"),
        ("San Bernardino",  "CA", "ie_riverside_ca",  "exact"),
        ("Arlington",       "VA", "dc_nova",          "exact"),
        ("Tysons",          "VA", "dc_nova",          "exact"),
        ("Fort Worth",      "TX", "dallas_fw_tx",     "exact"),
        ("Brooklyn",        "NY", "nyc_ny",           "exact"),
        ("Tempe",           "AZ", "phoenix_tempe_az", "exact"),
        ("Cambridge",       "MA", "boston_ma",        "exact"),
        ("St. Paul",        "MN", "minneapolis_mn",   "exact"),
        ("Jersey City",     "NJ", "nyc_ny",           "exact"),
        ("Inland Empire",   "CA", "ie_riverside_ca",  "alias"),
    ],
)
def test_city_alias_matching(scorer, city, state, expected_metro_id, expected_kind):
    s = scorer.score(city, state)
    assert s.metro_id == expected_metro_id
    assert s.match_kind == expected_kind
    assert s.ranked is True


def test_fuzzy_match_on_typo(scorer):
    s = scorer.score("Cinncinati", "OH")    # misspelled
    assert s.metro_id == "cincinnati_oh"
    assert s.match_kind == "fuzzy"
    assert 0.8 <= s.confidence < 1.0


# ── Cross-state name-collision guard ──────────────────────────────────────────
#
# Several metros carry a bare-city alias (e.g. "troy, mi" -> key "troy" for
# Detroit, "columbus" for Columbus, OH) that also happens to be the name of a
# real, unrelated city elsewhere in the country (Troy, NY; Columbus, GA — not
# in this dataset). The matcher must not let its global fuzzy fallback
# resurrect that same alias key at high confidence once the explicit state
# disagreement has already ruled it out for this query.

def test_state_mismatch_does_not_resurrect_via_global_fuzzy(scorer):
    """Troy, NY is real but unranked; must not silently resolve to Detroit, MI
    just because "troy, mi" is an alias of Detroit."""
    s = scorer.score("Troy", "NY")
    assert s.metro_id is None
    assert s.ranked is False
    assert s.match_kind == "fallback"


def test_columbus_ga_does_not_resolve_to_columbus_oh(scorer):
    """Columbus, GA is unranked and distinct from Columbus, OH."""
    s = scorer.score("Columbus", "GA")
    assert s.metro_id is None
    assert s.ranked is False
    assert s.match_kind == "fallback"


def test_columbus_oh_still_matches_with_correct_state(scorer):
    """Sanity check: the fix must not break the legitimate same-state match."""
    s = scorer.score("Columbus", "OH")
    assert s.metro_id == "columbus_oh"
    assert s.ranked is True


def test_cross_state_fuzzy_match_gets_confidence_penalty(scorer):
    """A genuine fuzzy (typo) match that lands in a state different from the
    one supplied should be flagged with reduced confidence, not full trust."""
    same_state = scorer.score("Cinncinati", "OH")
    cross_state = scorer.score("Cinncinati", "KY")
    assert same_state.metro_id == "cincinnati_oh"
    assert cross_state.metro_id == "cincinnati_oh"
    assert cross_state.confidence < same_state.confidence


# ── Degenerate / short input guard ────────────────────────────────────────────

def test_single_character_city_does_not_falsely_match(scorer):
    """A single garbage character must not substring-match into an unrelated
    metro/alias key (e.g. "a" is a substring of "cleveland")."""
    s = scorer.score("a", "OH")
    assert s.metro_id is None
    assert s.ranked is False
    assert s.match_kind == "fallback"


def test_short_but_real_alias_still_matches(scorer):
    """The short-input guard must not break legitimate short aliases."""
    s = scorer.score("LA", "CA")
    assert s.metro_id == "los_angeles_ca"
    s2 = scorer.score("SF", "CA")
    assert s2.metro_id == "sf_bay_ca"


def test_unranked_metro_returns_fallback(scorer):
    s = scorer.score("Boise", "ID")
    assert s.metro_id is None
    assert s.ranked is False
    assert s.match_kind == "fallback"
    assert s.composite == 40.0


def test_remote_classified_as_remote(scorer):
    s = scorer.score("Remote", None)
    assert s.metro_id is None
    assert s.match_kind == "remote"


def test_empty_city_classified_as_remote(scorer):
    s = scorer.score(None, "CA")
    assert s.match_kind == "remote"


# ── Scheme switching changes the composite ───────────────────────────────────

def test_scheme_changes_composite():
    """Houston favors career; Cleveland favors lifestyle. Different schemes should reverse the order."""
    sc_balanced = LocationScorer(scheme="balanced")
    sc_career   = LocationScorer(scheme="career_only")

    cleveland_bal = sc_balanced.composite_for("cleveland_oh")
    houston_bal   = sc_balanced.composite_for("houston_tx")
    cleveland_car = sc_career.composite_for("cleveland_oh")
    houston_car   = sc_career.composite_for("houston_tx")

    assert cleveland_bal > houston_bal, "Cleveland should lead under balanced"
    assert houston_car > cleveland_car, "Houston should lead under career_only"


def test_invalid_scheme_rejected():
    with pytest.raises(ValueError, match="not defined"):
        LocationScorer(scheme="bogus_scheme")  # type: ignore[arg-type]


# ── Normalization helper ─────────────────────────────────────────────────────

def test_location_score_normalized_property(scorer):
    s = scorer.score("Cleveland", "OH")
    assert 0.0 <= s.normalized <= 1.0
    assert abs(s.normalized - s.composite / 100.0) < 1e-9


# ── get_metro lookup (Build 1 location-economics rationale wiring) ───────────

def test_get_metro_returns_full_metro_area(scorer):
    metro = scorer.get_metro("cleveland_oh")
    assert metro is not None
    assert metro.id == "cleveland_oh"
    assert metro.name


def test_get_metro_returns_none_for_unknown_id(scorer):
    assert scorer.get_metro("not_a_real_metro") is None


def test_get_metro_returns_none_for_none_input(scorer):
    assert scorer.get_metro(None) is None


def test_get_metro_does_not_mutate_internal_state(scorer):
    before = list(scorer._metros)
    scorer.get_metro("cleveland_oh")
    after = list(scorer._metros)
    assert before == after
