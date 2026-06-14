"""Tests for Phase 2 Step 3: benefit/trajectory reason display in daily report."""

import json

import pytest

from job_search.reporting.daily_report import DailyReporter


def make_reporter() -> DailyReporter:
    r = DailyReporter.__new__(DailyReporter)
    r.sheets = None  # not needed for formatting tests
    return r


def make_job_dict(**kwargs) -> dict:
    defaults = {
        "canonical_job_id": "abc123",
        "title": "Structural Engineer",
        "company": "Acme Engineering",
        "match_score": 0.82,
        "stretch_category": "qualified",
        "llm_grade": "Good",
        "benefit_score": 0.0,
        "career_trajectory_score": 0.0,
        "benefit_reasons": "[]",
        "trajectory_reasons": "[]",
        "location_city": "Seattle",
        "location_state": "WA",
        "apply_url": "https://example.com/apply",
    }
    defaults.update(kwargs)
    return defaults


def reasons_json(*labels_weights) -> str:
    """Build a reasons JSON string from (label, weight) pairs."""
    return json.dumps([
        {
            "key": label.lower().replace(" ", "_"),
            "label": label,
            "source": "job_description",
            "weight": weight,
            "confidence": 1.0,
            "matched_text": label.lower(),
            "reason": f"Job post mentions {label.lower()}.",
        }
        for label, weight in labels_weights
    ], sort_keys=True)


# ── _format_reasons unit tests ────────────────────────────────────────────────

def test_format_reasons_returns_top_3_labels():
    reporter = make_reporter()
    rj = reasons_json(
        ("Tuition reimbursement", 0.18),
        ("PE exam reimbursement", 0.14),
        ("Signing bonus", 0.02),
    )
    result = reporter._format_reasons(rj)
    assert result == "Tuition reimbursement, PE exam reimbursement, Signing bonus"


def test_format_reasons_caps_at_n():
    reporter = make_reporter()
    rj = reasons_json(
        ("Tuition reimbursement", 0.18),
        ("PE exam reimbursement", 0.14),
        ("FE exam reimbursement", 0.10),
        ("Signing bonus", 0.02),
    )
    result = reporter._format_reasons(rj, n=2)
    assert result == "Tuition reimbursement, PE exam reimbursement"


def test_format_reasons_empty_array_returns_empty_string():
    reporter = make_reporter()
    assert reporter._format_reasons("[]") == ""


def test_format_reasons_null_returns_empty_string():
    reporter = make_reporter()
    assert reporter._format_reasons(None) == ""


def test_format_reasons_malformed_json_returns_empty_string():
    reporter = make_reporter()
    assert reporter._format_reasons("{not valid json}") == ""


def test_format_reasons_non_list_json_returns_empty_string():
    reporter = make_reporter()
    assert reporter._format_reasons('{"key": "value"}') == ""


def test_format_reasons_single_hit():
    reporter = make_reporter()
    rj = reasons_json(("Tuition reimbursement", 0.18))
    result = reporter._format_reasons(rj)
    assert result == "Tuition reimbursement"


# ── _format_report_line integration tests ────────────────────────────────────

def test_report_line_shows_benefit_reasons_when_present():
    reporter = make_reporter()
    job = make_job_dict(
        benefit_score=0.32,
        benefit_reasons=reasons_json(
            ("Tuition reimbursement", 0.18),
            ("PE exam reimbursement", 0.14),
        ),
    )
    line = reporter._format_report_line(job)
    assert "Tuition reimbursement" in line
    assert "PE exam reimbursement" in line


def test_report_line_shows_trajectory_reasons_when_present():
    reporter = make_reporter()
    job = make_job_dict(
        career_trajectory_score=0.36,
        trajectory_reasons=reasons_json(
            ("EIT/PE path", 0.20),
            ("Mentorship program", 0.16),
        ),
    )
    line = reporter._format_report_line(job)
    assert "EIT/PE path" in line
    assert "Mentorship program" in line


def test_report_line_zero_benefit_shows_no_signals_message():
    reporter = make_reporter()
    job = make_job_dict(benefit_score=0.0, benefit_reasons="[]")
    line = reporter._format_report_line(job)
    assert "no explicit benefit signals" in line


def test_report_line_zero_trajectory_shows_no_signals_message():
    reporter = make_reporter()
    job = make_job_dict(career_trajectory_score=0.0, trajectory_reasons="[]")
    line = reporter._format_report_line(job)
    assert "no explicit trajectory signals" in line


def test_report_line_null_reasons_does_not_crash():
    reporter = make_reporter()
    job = make_job_dict(
        benefit_score=0.18,
        career_trajectory_score=0.20,
        benefit_reasons=None,
        trajectory_reasons=None,
    )
    line = reporter._format_report_line(job)
    assert "Benefit:" in line
    assert "Trajectory:" in line


def test_report_line_missing_reasons_key_does_not_crash():
    reporter = make_reporter()
    job = make_job_dict()
    del job["benefit_reasons"]
    del job["trajectory_reasons"]
    line = reporter._format_report_line(job)
    assert "Benefit:" in line
    assert "Trajectory:" in line


def test_report_line_preserves_existing_fields():
    reporter = make_reporter()
    job = make_job_dict()
    line = reporter._format_report_line(job)
    assert "Structural Engineer" in line
    assert "Acme Engineering" in line
    assert "Good" in line
    assert "82.0%" in line
    assert "Seattle" in line
    assert "abc123" in line


def test_report_line_benefit_score_shown_as_percentage():
    reporter = make_reporter()
    job = make_job_dict(
        benefit_score=0.32,
        benefit_reasons=reasons_json(("Tuition reimbursement", 0.18)),
    )
    line = reporter._format_report_line(job)
    assert "32.0%" in line


def test_report_line_trajectory_score_shown_as_percentage():
    reporter = make_reporter()
    job = make_job_dict(
        career_trajectory_score=0.20,
        trajectory_reasons=reasons_json(("EIT/PE path", 0.20)),
    )
    line = reporter._format_report_line(job)
    assert "20.0%" in line
