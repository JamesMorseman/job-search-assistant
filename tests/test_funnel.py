"""Tests for FunnelReporter — shapes + correctness on synthetic data."""

import sqlite3

import pytest

from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.reporting.funnel import FunnelReporter
from job_search.tracking import advance_state


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


def _seed(db_path, source: str, job_id: str, final_state: str, match_score: float = 0.7):
    """Insert a job and walk it forward through valid transitions."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    dedup = Deduplicator(conn)
    dedup.upsert(CanonicalJob(
        canonical_job_id=job_id,
        source=source,
        source_job_id=job_id,
        company=f"Firm {job_id}",
        title="Civil Engineer",
        match_score=match_score,
        stretch_category="qualified",
    ))

    # Walk forward
    path = {
        "discovered": [],
        "presented": ["presented"],
        "selected":  ["presented", "selected"],
        "applied":   ["presented", "selected", "applied"],
        "screen":    ["presented", "selected", "applied", "screen"],
        "interview": ["presented", "selected", "applied", "screen", "interview"],
        "offer":     ["presented", "selected", "applied", "screen", "interview", "offer"],
        "rejected":  ["presented", "selected", "applied", "rejected"],
        "ghosted":   ["presented", "selected", "applied", "ghosted"],
    }[final_state]
    for state in path:
        advance_state(conn, job_id, state, note="test seed")
    conn.commit()
    conn.close()


def test_funnel_basic_counts(db):
    _seed(db, "greenhouse", "j1", "presented")
    _seed(db, "greenhouse", "j2", "applied")
    _seed(db, "usajobs",    "j3", "presented")
    _seed(db, "usajobs",    "j4", "interview")
    _seed(db, "usajobs",    "j5", "rejected")

    stats = FunnelReporter().compute()
    assert stats.total_jobs == 5
    assert stats.by_state["presented"] == 2
    assert stats.by_state["applied"] == 1
    assert stats.by_state["interview"] == 1
    assert stats.by_state["rejected"] == 1


def test_funnel_by_source(db):
    _seed(db, "greenhouse", "j1", "applied")
    _seed(db, "greenhouse", "j2", "rejected")
    _seed(db, "lever",      "j3", "interview")
    _seed(db, "usajobs",    "j4", "presented")

    stats = FunnelReporter().compute()
    assert "greenhouse" in stats.by_source
    assert stats.by_source["greenhouse"]["applied"] == 1
    assert stats.by_source["greenhouse"]["rejected"] == 1
    assert stats.by_source["lever"]["interview"] == 1
    assert stats.by_source["usajobs"]["presented"] == 1


def test_response_rate_by_source(db):
    # USAJOBS: 3 applied, 2 got a response (1 screen + 1 rejected)
    # Actually rejected is NOT a response in our model
    _seed(db, "usajobs", "j1", "interview")    # responded
    _seed(db, "usajobs", "j2", "rejected")     # applied but rejected (no response)
    _seed(db, "usajobs", "j3", "ghosted")      # applied, no response
    _seed(db, "usajobs", "j4", "screen")       # responded

    stats = FunnelReporter().compute()
    usa = stats.response_rate_by_source["usajobs"]
    assert usa["applied"] == 4
    assert usa["responded"] == 2     # interview + screen count as responses
    assert abs(usa["response_rate"] - 0.5) < 0.001


def test_avg_match_by_state(db):
    _seed(db, "greenhouse", "j1", "applied",   match_score=0.85)
    _seed(db, "greenhouse", "j2", "applied",   match_score=0.65)
    _seed(db, "greenhouse", "j3", "rejected",  match_score=0.55)

    stats = FunnelReporter().compute()
    assert abs(stats.avg_match_by_state["applied"] - 0.75) < 0.001
    assert abs(stats.avg_match_by_state["rejected"] - 0.55) < 0.001


def test_empty_db_returns_zeros(db):
    stats = FunnelReporter().compute()
    assert stats.total_jobs == 0
    assert stats.by_state == {}
    assert stats.by_source == {}
    assert stats.response_rate_by_source == {}


# ── Phase 6 Package 1 — Analytics Expansion ──────────────────────────────


def test_funnel_conversion_rates_empty_on_empty_db(db):
    stats = FunnelReporter().compute()
    assert stats.funnel_conversion_rates == {}


def test_funnel_conversion_rates_first_stage_is_none(db):
    _seed(db, "greenhouse", "j1", "discovered")
    stats = FunnelReporter().compute()
    assert stats.funnel_conversion_rates["discovered"] is None


def test_funnel_conversion_rates_computes_correctly(db):
    _seed(db, "greenhouse", "j1", "presented")
    _seed(db, "greenhouse", "j2", "presented")
    _seed(db, "greenhouse", "j3", "selected")
    stats = FunnelReporter().compute()
    # by_state = {"presented": 2, "selected": 1}
    # presented prior is "discovered" which has 0 current jobs → None
    assert stats.funnel_conversion_rates["presented"] is None
    # selected prior is "presented" = 2, selected = 1 → 0.5
    assert abs(stats.funnel_conversion_rates["selected"] - 0.5) < 0.001
    # applied prior is "selected" = 1, applied = 0 → 0.0 (not None)
    assert stats.funnel_conversion_rates["applied"] == 0.0


def test_funnel_conversion_rates_none_when_prior_stage_is_zero(db):
    _seed(db, "greenhouse", "j1", "applied")
    # by_state has "applied" but not "selected" (all jobs walked through but none stuck there)
    stats = FunnelReporter().compute()
    # selected count is 0 → applied conversion is None
    assert stats.funnel_conversion_rates["applied"] is None


def test_llm_grade_distribution_empty_when_no_grades(db):
    _seed(db, "greenhouse", "j1", "applied")
    stats = FunnelReporter().compute()
    assert stats.llm_grade_distribution == {}


def test_llm_grade_distribution_counts_and_percentages(db):
    import sqlite3 as _sqlite3
    _seed(db, "greenhouse", "j1", "applied")
    _seed(db, "greenhouse", "j2", "applied")
    _seed(db, "greenhouse", "j3", "applied")
    conn = _sqlite3.connect(db)
    conn.execute("UPDATE jobs SET llm_grade = 'A' WHERE canonical_job_id IN ('j1', 'j2')")
    conn.execute("UPDATE jobs SET llm_grade = 'B' WHERE canonical_job_id = 'j3'")
    conn.commit()
    conn.close()
    stats = FunnelReporter().compute()
    assert "A" in stats.llm_grade_distribution
    assert "B" in stats.llm_grade_distribution
    assert stats.llm_grade_distribution["A"]["count"] == 2
    assert stats.llm_grade_distribution["B"]["count"] == 1
    assert abs(stats.llm_grade_distribution["A"]["pct"] - 0.667) < 0.001
    assert abs(stats.llm_grade_distribution["B"]["pct"] - 0.333) < 0.001


def test_llm_grade_distribution_excludes_null_grades(db):
    import sqlite3 as _sqlite3
    _seed(db, "greenhouse", "j1", "applied")
    _seed(db, "greenhouse", "j2", "applied")
    conn = _sqlite3.connect(db)
    conn.execute("UPDATE jobs SET llm_grade = 'A' WHERE canonical_job_id = 'j1'")
    conn.commit()
    conn.close()
    stats = FunnelReporter().compute()
    assert len(stats.llm_grade_distribution) == 1
    assert stats.llm_grade_distribution["A"]["count"] == 1
    assert abs(stats.llm_grade_distribution["A"]["pct"] - 1.0) < 0.001


def test_stretch_conversion_rates_empty_on_empty_db(db):
    stats = FunnelReporter().compute()
    assert stats.stretch_conversion_rates == {}


def test_stretch_conversion_rates_computes_correctly(db):
    # _seed always uses stretch_category="qualified"
    _seed(db, "greenhouse", "j1", "applied")   # in _APPLIED_AND_BEYOND
    _seed(db, "greenhouse", "j2", "presented")  # not yet applied
    stats = FunnelReporter().compute()
    assert "qualified" in stats.stretch_conversion_rates
    data = stats.stretch_conversion_rates["qualified"]
    assert data["total"] == 2
    assert abs(data["applied_rate"] - 0.5) < 0.001
    assert data["screen_rate"] == 0.0


def test_stretch_conversion_rates_screen_rate(db):
    _seed(db, "greenhouse", "j1", "screen")    # in _SCREEN_AND_BEYOND
    _seed(db, "greenhouse", "j2", "applied")   # in _APPLIED_AND_BEYOND but not screen
    _seed(db, "greenhouse", "j3", "presented") # not yet applied
    stats = FunnelReporter().compute()
    data = stats.stretch_conversion_rates["qualified"]
    assert data["total"] == 3
    assert abs(data["screen_rate"] - round(1 / 3, 3)) < 0.001
    assert abs(data["applied_rate"] - round(2 / 3, 3)) < 0.001


# ── Phase 6 Package 2 — Analytics Depth ──────────────────────────────────


def test_score_distribution_empty_on_empty_db(db):
    stats = FunnelReporter().compute()
    assert stats.score_distribution_by_state == {}


def test_score_distribution_computes_quartiles(db):
    # Four jobs in "applied" with known scores; sorted: 0.2, 0.4, 0.6, 0.8
    for i, score in enumerate([0.2, 0.4, 0.6, 0.8]):
        _seed(db, "greenhouse", f"j{i}", "applied", match_score=score)
    stats = FunnelReporter().compute()
    dist = stats.score_distribution_by_state["applied"]
    assert dist["n"] == 4
    # Q1 = lerp(0.2, 0.4, 0.75) = 0.35 (linear interpolation at 25th pct of 4 values)
    assert dist["q1"] is not None
    assert dist["median"] is not None
    assert dist["q3"] is not None
    # Median of [0.2, 0.4, 0.6, 0.8] = lerp(0.4, 0.6, 0.5) = 0.5
    assert abs(dist["median"] - 0.5) < 0.01


def test_score_distribution_single_value(db):
    _seed(db, "greenhouse", "j1", "applied", match_score=0.75)
    stats = FunnelReporter().compute()
    dist = stats.score_distribution_by_state["applied"]
    assert dist["n"] == 1
    assert dist["q1"] == 0.75
    assert dist["median"] == 0.75
    assert dist["q3"] == 0.75


def test_stretch_response_rates_empty_on_no_applications(db):
    _seed(db, "greenhouse", "j1", "presented")  # not yet applied
    stats = FunnelReporter().compute()
    assert stats.stretch_response_rates == {}


def test_stretch_response_rates_computes_correctly(db):
    _seed(db, "greenhouse", "j1", "screen")    # responded + interviewed-adjacent
    _seed(db, "greenhouse", "j2", "applied")   # applied, no response
    _seed(db, "greenhouse", "j3", "rejected")  # applied, no response
    stats = FunnelReporter().compute()
    rr = stats.stretch_response_rates["qualified"]
    # applied (in _APPLIED_AND_BEYOND): all 3 — screen + applied + rejected
    assert rr["applied"] == 3
    # responded (acknowledged/screen/interview/offer): 1 (screen)
    assert abs(rr["response_rate"] - round(1 / 3, 3)) < 0.001
    # interviewed (interview/offer): 0
    assert rr["interview_rate"] == 0.0


def test_unified_source_data_empty_on_empty_db(db):
    stats = FunnelReporter().compute()
    assert stats.unified_source_data == {}


def test_unified_source_data_discovery_columns(db):
    _seed(db, "greenhouse", "j1", "discovered")
    _seed(db, "greenhouse", "j2", "presented")
    _seed(db, "greenhouse", "j3", "selected")
    stats = FunnelReporter().compute()
    gh = stats.unified_source_data["greenhouse"]
    assert gh["jobs_seen"] == 3
    assert gh["jobs_presented"] == 2  # presented + selected (not discovered)
    assert abs(gh["presentation_rate"] - round(2 / 3, 3)) < 0.001


def test_unified_source_data_outcome_columns(db):
    _seed(db, "usajobs", "j1", "applied")
    _seed(db, "usajobs", "j2", "screen")
    _seed(db, "usajobs", "j3", "offer")
    stats = FunnelReporter().compute()
    usa = stats.unified_source_data["usajobs"]
    assert usa["applied"] == 3    # all in _APPLIED_AND_BEYOND
    assert usa["interviewed"] == 1  # offer only
    assert usa["offers"] == 1
    assert abs(usa["response_rate"] - round(2 / 3, 3)) < 0.001   # screen + offer responded


def test_pipeline_velocity_empty_on_empty_db(db):
    stats = FunnelReporter().compute()
    # Dict still has keys but n=0 for each pair
    assert "presented_to_selected" in stats.pipeline_velocity
    assert stats.pipeline_velocity["presented_to_selected"]["n"] == 0
    assert stats.pipeline_velocity["presented_to_selected"]["median_days"] is None


def test_pipeline_velocity_computes_median(db):
    import sqlite3 as _sqlite3
    import datetime
    _seed(db, "greenhouse", "j1", "selected")
    # Insert explicit transitions with known timestamps
    conn = _sqlite3.connect(db)
    conn.row_factory = _sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    base = datetime.datetime(2026, 6, 1, 12, 0, 0)
    conn.execute(
        "INSERT INTO app_transitions (canonical_job_id, to_state, transitioned_at) VALUES (?, ?, ?)",
        ("j1", "presented", (base).isoformat()),
    )
    conn.execute(
        "INSERT INTO app_transitions (canonical_job_id, to_state, transitioned_at) VALUES (?, ?, ?)",
        ("j1", "selected", (base + datetime.timedelta(days=3)).isoformat()),
    )
    conn.commit()
    conn.close()
    stats = FunnelReporter().compute()
    vel = stats.pipeline_velocity["presented_to_selected"]
    assert vel["n"] >= 1
    assert vel["median_days"] is not None
    assert vel["median_days"] >= 3.0


def test_llm_grade_outcome_correlation_empty_when_no_grades(db):
    _seed(db, "greenhouse", "j1", "applied")
    stats = FunnelReporter().compute()
    assert stats.llm_grade_outcome_correlation == {}


def test_llm_grade_outcome_correlation_qualifies_with_5_terminals(db):
    import sqlite3 as _sqlite3
    for i in range(6):
        _seed(db, "greenhouse", f"j{i}", "rejected")
    conn = _sqlite3.connect(db)
    conn.execute("UPDATE jobs SET llm_grade = 'A'")
    conn.commit()
    conn.close()
    stats = FunnelReporter().compute()
    assert "A" in stats.llm_grade_outcome_correlation
    assert stats.llm_grade_outcome_correlation["A"]["qualifies"] is True
    assert stats.llm_grade_outcome_correlation["A"]["terminal"] == 6


def test_llm_grade_outcome_correlation_does_not_qualify_below_threshold(db):
    import sqlite3 as _sqlite3
    for i in range(3):
        _seed(db, "greenhouse", f"j{i}", "rejected")
    conn = _sqlite3.connect(db)
    conn.execute("UPDATE jobs SET llm_grade = 'B'")
    conn.commit()
    conn.close()
    stats = FunnelReporter().compute()
    assert stats.llm_grade_outcome_correlation["B"]["qualifies"] is False
    assert stats.llm_grade_outcome_correlation["B"]["terminal"] == 3
