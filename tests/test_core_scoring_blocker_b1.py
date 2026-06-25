"""B1-CORE-SCORING-BLOCKER-01 regression tests."""

from __future__ import annotations

import sqlite3

import pytest

from job_search.db.connection import init_db
from job_search.ingestion.scoring import Scorer
from job_search.models import CanonicalJob, StretchCategory
from job_search.reporting.daily_report import DailyReporter


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    monkeypatch.setattr("job_search.config.settings.DRIVE_ROOT_FOLDER_ID", "")
    init_db(db_path)
    yield db_path


def _job(title: str, description: str, company: str = "Example Firm") -> CanonicalJob:
    return CanonicalJob(
        source="test",
        source_job_id=title.lower().replace(" ", "-"),
        company=company,
        title=title,
        description_normalized=description,
        location_city="Seattle",
        location_state="WA",
    )


@pytest.mark.parametrize(
    "company,title,description,expected",
    [
        (
            "Markon",
            "Structural Engineer with Security Clearance",
            "Structural design role supporting secure facilities.",
            "clearance",
        ),
        (
            "Wyetech",
            "Senior Structural Engineer with Security Clearance",
            "Senior structural engineer role with active Secret clearance required.",
            "clearance",
        ),
        (
            "Lumen",
            "Senior Construction Engineer",
            "Construction engineering role for senior field coordination.",
            "seniority",
        ),
        (
            "Lumen",
            "Senior Construction Engineer",
            "Candidate must have 6+ years of construction engineering experience.",
            "years",
        ),
    ],
)
def test_b1_core_blocker_rows_are_structured_and_demoted(company, title, description, expected):
    scored = Scorer().score(_job(title=title, description=description, company=company))

    if expected == "clearance":
        assert scored.knockout.clearance
    if expected in {"seniority", "years"}:
        assert scored.knockout.min_years is not None
        assert scored.knockout.min_years >= 5
    assert scored.stretch_category == StretchCategory.LONG_SHOT
    assert scored.match_score is not None
    assert scored.match_score < 0.55


class _FakeSheets:
    def __init__(self):
        self.rows: list[dict] = []

    def ensure_headers(self):
        return None

    def upsert_row(self, job_dict):
        self.rows.append(dict(job_dict))


def _insert_candidate(
    conn: sqlite3.Connection,
    job_id: str,
    *,
    match_score: float,
    stretch_category: str = "qualified",
    ko_clearance: str | None = None,
    ko_min_years: float | None = None,
    ko_pe_required: int | None = None,
):
    conn.execute(
        """
        INSERT INTO jobs (
            canonical_job_id, source, source_job_id, company, title,
            description_normalized, app_state, match_score, stretch_category,
            ko_clearance, ko_min_years, ko_pe_required
        )
        VALUES (?, 'test', ?, 'Example Firm', ?, 'structural design', 'discovered', ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            job_id,
            job_id,
            match_score,
            stretch_category,
            ko_clearance,
            ko_min_years,
            ko_pe_required,
        ),
    )


def test_daily_report_excludes_hard_blockers_even_when_scores_are_high(db):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    _insert_candidate(conn, "good-clean-role", match_score=0.72)
    _insert_candidate(
        conn,
        "clearance-role",
        match_score=0.96,
        ko_clearance="Secret",
    )
    _insert_candidate(
        conn,
        "senior-role",
        match_score=0.94,
        ko_min_years=5,
    )
    _insert_candidate(
        conn,
        "pe-role",
        match_score=0.93,
        ko_pe_required=1,
    )
    conn.commit()
    conn.close()

    fake_sheets = _FakeSheets()
    reporter = DailyReporter()
    reporter.sheets = fake_sheets

    stats = reporter.run()

    assert stats["presented"] == 1
    assert [row["canonical_job_id"] for row in fake_sheets.rows] == ["good-clean-role"]

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = {
        row["canonical_job_id"]: row["app_state"]
        for row in conn.execute("SELECT canonical_job_id, app_state FROM jobs")
    }
    conn.close()
    assert rows["good-clean-role"] == "presented"
    assert rows["clearance-role"] == "discovered"
    assert rows["senior-role"] == "discovered"
    assert rows["pe-role"] == "discovered"
