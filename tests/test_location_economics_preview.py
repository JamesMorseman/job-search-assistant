"""Tests for the pure location/salary economics rationale module.

job_search.reporting.location_economics_preview is import-pure: no DB, no
file IO, no network, no LLM. All inputs are hand-built fixtures.
"""

from __future__ import annotations

from job_search.location.models import DimensionScores, LocationScore, MetroArea
from job_search.reporting.location_economics_preview import (
    LocationEconomicsPreview,
    build_location_economics_preview,
)


def make_location_score(
    *,
    metro_id: str | None = "cleveland_oh",
    metro_name: str | None = "Cleveland, OH",
    composite: float = 76.5,
    ranked: bool = True,
    match_kind: str = "exact",
    confidence: float = 1.0,
    dimensions: DimensionScores | None = None,
) -> LocationScore:
    return LocationScore(
        metro_id=metro_id,
        metro_name=metro_name,
        composite=composite,
        dimensions=dimensions or DimensionScores(ce=3.5, col=4.2, home=4.8, mj=2.0, dating=3.0),
        scheme="balanced",
        ranked=ranked,
        match_kind=match_kind,
        confidence=confidence,
    )


def make_metro(**overrides) -> MetroArea:
    defaults = dict(
        id="cleveland_oh",
        name="Cleveland, OH",
        state="OH",
        balanced_rank=1,
        salary_k=68,
        real_net_k=58,
        rpp=92.0,
        rent_1br=950,
        years_20pct_solo=4.2,
        entry_jobs=1200,
        total_jobs=15000,
    )
    defaults.update(overrides)
    return MetroArea(**defaults)


# ── Headline / ranked vs unranked behavior ───────────────────────────────────

def test_ranked_metro_produces_headline_with_composite():
    score = make_location_score()
    preview = build_location_economics_preview(score)

    assert preview.ranked is True
    assert preview.metro_name == "Cleveland, OH"
    assert "76.5" in preview.headline
    assert "may indicate" in preview.headline


def test_remote_posting_produces_remote_headline():
    score = make_location_score(metro_id=None, metro_name=None, ranked=False, match_kind="remote", composite=40.0)
    preview = build_location_economics_preview(score)

    assert preview.ranked is False
    assert "remote" in preview.headline.lower()


def test_unranked_fallback_produces_fallback_headline():
    score = make_location_score(metro_id=None, metro_name=None, ranked=False, match_kind="fallback", composite=40.0)
    preview = build_location_economics_preview(score)

    assert preview.ranked is False
    assert "not in atlas" in preview.headline.lower() or "fallback" in preview.headline.lower()


def test_none_location_score_returns_no_data_preview():
    preview = build_location_economics_preview(None)

    assert preview.metro_name is None
    assert preview.composite is None
    assert "no location data" in preview.headline.lower()


# ── Dimension notes ───────────────────────────────────────────────────────────

def test_ranked_metro_includes_dimension_notes():
    score = make_location_score()
    preview = build_location_economics_preview(score)

    assert len(preview.dimension_notes) == 5
    joined = " ".join(preview.dimension_notes)
    assert "Career/job-market strength" in joined
    assert "Cost-of-living-adjusted salary" in joined


def test_unranked_metro_has_no_dimension_notes():
    score = make_location_score(metro_id=None, metro_name=None, ranked=False, match_kind="remote")
    preview = build_location_economics_preview(score)

    assert preview.dimension_notes == []


# ── Economics notes (requires MetroArea reference data) ──────────────────────

def test_economics_notes_empty_without_metro():
    score = make_location_score()
    preview = build_location_economics_preview(score, metro=None)

    assert preview.economics_notes == []


def test_economics_notes_include_salary_and_rent_when_metro_supplied():
    score = make_location_score()
    metro = make_metro()
    preview = build_location_economics_preview(score, metro=metro)

    joined = " ".join(preview.economics_notes)
    assert "$68k" in joined
    assert "$58k" in joined
    assert "$950" in joined
    assert "may indicate" in joined


def test_economics_notes_use_advisory_not_deterministic_language():
    score = make_location_score()
    metro = make_metro()
    preview = build_location_economics_preview(score, metro=metro)

    full_text = preview.to_text()
    assert "this means" not in full_text.lower()
    assert "you should" not in full_text.lower()


def test_economics_notes_handle_missing_optional_fields_gracefully():
    score = make_location_score()
    metro = make_metro(salary_k=None, real_net_k=None, rent_1br=None, years_20pct_solo=None, entry_jobs=None, total_jobs=None)
    preview = build_location_economics_preview(score, metro=metro)

    # No exception, and no notes fabricated from missing data.
    assert preview.economics_notes == []


def test_economics_notes_salary_only_no_real_net():
    score = make_location_score()
    metro = make_metro(real_net_k=None)
    preview = build_location_economics_preview(score, metro=metro)

    joined = " ".join(preview.economics_notes)
    assert "$68k" in joined


# ── Caveats ────────────────────────────────────────────────────────────────

def test_ranked_metro_has_general_caveat_only():
    score = make_location_score()
    preview = build_location_economics_preview(score)

    assert len(preview.caveats) == 1
    assert "reference estimates" in preview.caveats[0]


def test_unranked_metro_has_additional_caveat():
    score = make_location_score(metro_id=None, metro_name=None, ranked=False, match_kind="fallback")
    preview = build_location_economics_preview(score)

    assert len(preview.caveats) == 2


# ── to_text rendering ─────────────────────────────────────────────────────────

def test_to_text_includes_headline_and_caveats():
    score = make_location_score()
    preview = build_location_economics_preview(score)

    text = preview.to_text()
    assert preview.headline in text
    assert "Note:" in text


def test_to_text_empty_preview_still_returns_string():
    preview = LocationEconomicsPreview(metro_name=None, composite=None, ranked=False, match_kind="unknown")
    assert preview.to_text() == ""


# ── Purity guard ───────────────────────────────────────────────────────────

def test_module_has_no_db_or_io_imports():
    """Guard against accidental coupling: this module must stay pure."""
    import ast
    import inspect

    import job_search.reporting.location_economics_preview as mod

    tree = ast.parse(inspect.getsource(mod))
    tree.body = tree.body[1:]  # drop module docstring (first statement)
    code = ast.unparse(tree)
    forbidden = ["get_db", "tempfile", "SheetsLogger", "open(", "import requests"]
    for token in forbidden:
        assert token not in code, f"location_economics_preview must stay pure; found {token!r}"
