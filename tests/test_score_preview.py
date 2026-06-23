"""Tests for the pure score-preview/explanation module.

job_search.reporting.score_preview is import-pure: no DB, no file IO, no
network, no LLM. All inputs here are hand-built fixtures — no fixtures or
helpers from daily_report, no get_db, no real config/data files.
"""

from __future__ import annotations

from job_search.evidence.types import EvidenceItem, EvidenceScore
from job_search.ingestion.scoring import SignalHit, SignalScore
from job_search.location.models import DimensionScores, LocationScore
from job_search.reporting.score_preview import (
    ScoreComponentPreview,
    ScorePreview,
    build_score_preview,
    explain_evidence_scores,
    explain_location_score,
    explain_signal_score,
)


# ── Fixture builders ───────────────────────────────────────────────────────

def make_signal_hit(label: str, weight: float = 0.18, key: str | None = None) -> SignalHit:
    return SignalHit(
        key=key or label.lower().replace(" ", "_"),
        label=label,
        source="job_description",
        weight=weight,
        confidence=1.0,
        matched_text=label.lower(),
        reason=f"Job post mentions {label.lower()}.",
    )


def make_signal_score(
    score: float = 0.32,
    hits: list[SignalHit] | None = None,
    missing_priority_keys: list[str] | None = None,
) -> SignalScore:
    return SignalScore(
        score=score,
        hits=hits if hits is not None else [],
        missing_priority_keys=missing_priority_keys if missing_priority_keys is not None else [],
    )


def make_evidence_item(text: str = "Designed steel moment frames.", **kwargs) -> EvidenceItem:
    defaults = {
        "id": "ev-1",
        "section": "experience",
        "text": text,
        "evidence_type": "resume_bullet",
    }
    defaults.update(kwargs)
    return EvidenceItem(**defaults)


def make_evidence_score(
    score: float = 0.8,
    text: str = "Designed steel moment frames.",
    reasons: list[str] | None = None,
) -> EvidenceScore:
    return EvidenceScore(
        item=make_evidence_item(text=text),
        score=score,
        reasons=reasons if reasons is not None else [],
    )


def make_location_score(
    metro_name: str | None = "Seattle",
    composite: float = 72.0,
    ranked: bool = True,
    match_kind: str = "exact",
    confidence: float = 1.0,
) -> LocationScore:
    return LocationScore(
        metro_id="seattle-wa" if metro_name else None,
        metro_name=metro_name,
        composite=composite,
        dimensions=DimensionScores(),
        scheme="balanced",
        ranked=ranked,
        match_kind=match_kind,
        confidence=confidence,
    )


# ── explain_signal_score ────────────────────────────────────────────────────

def test_explain_signal_score_with_hits_returns_top_reasons():
    signal = make_signal_score(
        score=0.32,
        hits=[
            make_signal_hit("Tuition reimbursement", 0.18),
            make_signal_hit("PE exam reimbursement", 0.14),
        ],
    )
    preview = explain_signal_score("benefit", "Benefit signals", signal)
    assert isinstance(preview, ScoreComponentPreview)
    assert preview.name == "benefit"
    assert preview.label == "Benefit signals"
    assert preview.score == 0.32
    assert preview.top_reasons == ["Tuition reimbursement", "PE exam reimbursement"]


def test_explain_signal_score_caps_top_n():
    signal = make_signal_score(
        score=0.5,
        hits=[
            make_signal_hit("A", 0.1),
            make_signal_hit("B", 0.1),
            make_signal_hit("C", 0.1),
            make_signal_hit("D", 0.1),
        ],
    )
    preview = explain_signal_score("benefit", "Benefit signals", signal, top_n=2)
    assert preview.top_reasons == ["A", "B"]


def test_explain_signal_score_zero_hits_has_no_signals_summary():
    signal = make_signal_score(score=0.0, hits=[])
    preview = explain_signal_score("benefit", "Benefit signals", signal)
    assert preview.top_reasons == []
    assert "no explicit signals detected" in preview.summary


def test_explain_signal_score_missing_priority_keys_in_summary():
    signal = make_signal_score(score=0.0, hits=[], missing_priority_keys=["pe_license"])
    preview = explain_signal_score("benefit", "Benefit signals", signal)
    assert "missing: pe_license" in preview.summary


def test_explain_signal_score_none_input_returns_zero_score():
    preview = explain_signal_score("benefit", "Benefit signals", None)
    assert preview.score == 0.0
    assert preview.summary == "no data supplied"
    assert preview.top_reasons == []


def test_explain_signal_score_computes_contribution_when_weight_and_overall_supplied():
    signal = make_signal_score(score=0.5, hits=[make_signal_hit("Tuition reimbursement")])
    preview = explain_signal_score(
        "benefit",
        "Benefit signals",
        signal,
        weight=0.10,
        overall_score=0.80,
    )
    assert preview.contribution == (0.5 * 0.10) / 0.80


def test_explain_signal_score_no_contribution_without_weight():
    signal = make_signal_score(score=0.5, hits=[])
    preview = explain_signal_score("benefit", "Benefit signals", signal, overall_score=0.8)
    assert preview.contribution is None


# ── explain_evidence_scores ─────────────────────────────────────────────────

def test_explain_evidence_scores_empty_list_returns_zero_score():
    preview = explain_evidence_scores("evidence", "Evidence match", [])
    assert preview.score == 0.0
    assert preview.summary == "no evidence items supplied"


def test_explain_evidence_scores_none_returns_zero_score():
    preview = explain_evidence_scores("evidence", "Evidence match", None)
    assert preview.score == 0.0


def test_explain_evidence_scores_averages_scores():
    scores = [
        make_evidence_score(score=0.9, text="Designed steel frames."),
        make_evidence_score(score=0.5, text="Led structural team."),
    ]
    preview = explain_evidence_scores("evidence", "Evidence match", scores)
    assert preview.score == 0.7


def test_explain_evidence_scores_ranks_top_reasons_by_score():
    scores = [
        make_evidence_score(score=0.3, text="Low score item.", reasons=["weak match"]),
        make_evidence_score(score=0.9, text="High score item.", reasons=["strong match"]),
    ]
    preview = explain_evidence_scores("evidence", "Evidence match", scores, top_n=1)
    assert preview.top_reasons == ["strong match"]


def test_explain_evidence_scores_falls_back_to_item_text_when_no_reasons():
    scores = [make_evidence_score(score=0.9, text="Designed steel moment frames.", reasons=[])]
    preview = explain_evidence_scores("evidence", "Evidence match", scores)
    assert preview.top_reasons == ["Designed steel moment frames."]


# ── explain_location_score ──────────────────────────────────────────────────

def test_explain_location_score_uses_normalized_composite():
    loc = make_location_score(composite=80.0)
    preview = explain_location_score(loc)
    assert preview.score == 0.8


def test_explain_location_score_includes_metro_name_in_summary():
    loc = make_location_score(metro_name="Seattle")
    preview = explain_location_score(loc)
    assert "Seattle" in preview.summary
    assert "match: exact" in preview.summary


def test_explain_location_score_flags_unranked_fallback():
    loc = make_location_score(metro_name=None, ranked=False, match_kind="fallback")
    preview = explain_location_score(loc)
    assert "unranked/fallback" in preview.summary


def test_explain_location_score_none_input_returns_zero_score():
    preview = explain_location_score(None)
    assert preview.score == 0.0
    assert preview.summary == "no location data supplied"


# ── build_score_preview (integration of the above) ─────────────────────────

def test_build_score_preview_assembles_all_components():
    preview = build_score_preview(
        overall_score=0.82,
        stretch_category="qualified",
        benefit=make_signal_score(score=0.3, hits=[make_signal_hit("Tuition reimbursement")]),
        benefit_weight=0.10,
        trajectory=make_signal_score(score=0.2, hits=[make_signal_hit("Mentorship program")]),
        trajectory_weight=0.10,
        location=make_location_score(),
        location_weight=0.30,
        evidence=[make_evidence_score(score=0.9)],
        evidence_weight=0.25,
    )
    assert isinstance(preview, ScorePreview)
    assert preview.overall_score == 0.82
    names = [c.name for c in preview.components]
    assert names == ["benefit", "trajectory", "location", "evidence"]
    assert "82.0%" in preview.headline
    assert "qualified" in preview.headline


def test_build_score_preview_omits_components_not_supplied():
    preview = build_score_preview(overall_score=0.5, benefit=make_signal_score())
    names = [c.name for c in preview.components]
    assert names == ["benefit"]


def test_build_score_preview_no_overall_score_has_empty_headline():
    preview = build_score_preview(benefit=make_signal_score())
    assert preview.headline == ""


def test_build_score_preview_includes_extra_notes():
    preview = build_score_preview(overall_score=0.5, extra_notes=["fixture data, not live scoring"])
    assert preview.notes == ["fixture data, not live scoring"]


# ── ScorePreview.to_text ─────────────────────────────────────────────────────

def test_to_text_renders_headline_and_components():
    preview = build_score_preview(
        overall_score=0.75,
        stretch_category="strong_fit",
        benefit=make_signal_score(score=0.4, hits=[make_signal_hit("Tuition reimbursement")]),
        benefit_weight=0.10,
    )
    text = preview.to_text()
    assert "Overall match score: 75.0%" in text
    assert "strong_fit" in text
    assert "Benefit signals: 40.0%" in text
    assert "Tuition reimbursement" in text


def test_to_text_includes_notes():
    preview = build_score_preview(overall_score=0.5, extra_notes=["sample note"])
    text = preview.to_text()
    assert "Note: sample note" in text


def test_to_text_empty_preview_is_empty_string():
    preview = ScorePreview(overall_score=None, components=[], headline="", notes=[])
    assert preview.to_text() == ""


# ── Purity checks ────────────────────────────────────────────────────────────

def test_module_has_no_db_or_io_imports():
    """Guard against accidental coupling: this module must stay pure.

    Checks code only (strips the module docstring via ast, since the
    docstring legitimately mentions get_db/tempfile/Path/SheetsLogger as
    prose contrasting this module with the IO-coupled daily_report module).
    """
    import ast
    import inspect

    import job_search.reporting.score_preview as mod

    tree = ast.parse(inspect.getsource(mod))
    tree.body = tree.body[1:]  # drop module docstring (first statement)
    code = ast.unparse(tree)
    forbidden = ["get_db", "tempfile", "SheetsLogger", "open(", "Path(", "import requests"]
    for token in forbidden:
        assert token not in code, f"score_preview.py code must not contain {token!r}"
