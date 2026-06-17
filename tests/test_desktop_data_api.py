"""ATLAS Desktop Package 2 data API tests."""

from __future__ import annotations

import inspect
import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services import atlas as atlas_service


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


@pytest.fixture
def client(db):
    app = create_app()
    with TestClient(app) as c:
        yield c


def _insert_job(db_path: str, job_id: str, **overrides):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    dedup = Deduplicator(conn)
    job_kwargs = dict(
        canonical_job_id=job_id,
        source="greenhouse",
        source_job_id=job_id,
        company="Acme Engineering",
        title="Civil Engineer",
        description_raw="Raw civil engineering description",
        description_normalized="Normalized civil engineering description",
        match_score=0.8,
        stretch_category="qualified",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def test_atlas_opportunities_returns_deterministic_json(client, db):
    _insert_job(
        db,
        "job-b",
        company="Beta Engineering",
        title="Civil Engineer II",
        last_seen="2026-06-01 10:00:00",
    )
    _insert_job(
        db,
        "job-a",
        company="Acme Engineering",
        title="Civil Engineer I",
        last_seen="2026-06-01 10:00:00",
    )
    conn = sqlite3.connect(db)
    conn.execute(
        "UPDATE jobs SET last_seen = ? WHERE canonical_job_id IN (?, ?)",
        ("2026-06-01 10:00:00", "job-a", "job-b"),
    )
    conn.commit()
    conn.close()

    resp = client.get("/atlas/api/opportunities")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body["limit"] == 50
    assert [item["job_id"] for item in body["opportunities"]] == ["job-a", "job-b"]
    assert body["opportunities"][0] == {
        "job_id": "job-a",
        "company": "Acme Engineering",
        "title": "Civil Engineer I",
        "source": "greenhouse",
        "stage": "discovered",
        "status": "discovered",
        "location_city": None,
        "location_state": None,
        "remote_flag": "unknown",
        "posted_date": None,
        "last_seen": "2026-06-01 10:00:00",
        "match_score": 0.8,
        "stretch_category": "qualified",
        "llm_grade": None,
    }


def test_atlas_opportunities_applies_safe_limit(client, db):
    _insert_job(db, "job-1")
    _insert_job(db, "job-2", company="Beta Engineering")

    resp = client.get("/atlas/api/opportunities?limit=1")

    assert resp.status_code == 200
    body = resp.json()
    assert body["limit"] == 1
    assert len(body["opportunities"]) == 1


def test_atlas_opportunity_detail_returns_local_dto(client, db):
    _insert_job(
        db,
        "job-1",
        company="Acme Engineering",
        title="Structural Engineer",
        discipline_tags=["structural", "civil"],
        location_city="Denver",
        location_state="CO",
        remote_flag="hybrid",
        apply_url="https://example.invalid/jobs/1",
        salary_min=70000,
        salary_max=90000,
        benefit_reasons='[{"label": "Tuition Reimbursement"}]',
        trajectory_reasons='[{"label": "EIT/PE Path"}]',
        llm_grade="Strong",
        llm_fit_score=4.5,
        llm_rationale="Good local fit.",
    )
    conn = sqlite3.connect(db)
    conn.execute("UPDATE jobs SET ko_eit_required = 1 WHERE canonical_job_id = ?", ("job-1",))
    conn.commit()
    conn.close()

    resp = client.get("/atlas/api/opportunities/job-1")

    assert resp.status_code == 200
    body = resp.json()
    assert body["job_id"] == "job-1"
    assert body["company"] == "Acme Engineering"
    assert body["title"] == "Structural Engineer"
    assert body["discipline_tags"] == ["structural", "civil"]
    assert body["description"] == "Normalized civil engineering description"
    assert body["apply_url"] == "https://example.invalid/jobs/1"
    assert body["ko_eit_required"] is True
    assert body["benefit_reasons"] == [{"label": "Tuition Reimbursement"}]
    assert body["trajectory_reasons"] == [{"label": "EIT/PE Path"}]


def test_atlas_opportunity_detail_returns_404_for_missing_job(client):
    resp = client.get("/atlas/api/opportunities/does-not-exist")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Opportunity not found"}


def test_atlas_summary_returns_basic_counts(client, db):
    _insert_job(db, "job-1", app_state="selected")
    _insert_job(db, "job-2", app_state="applied", company="Beta Engineering")

    resp = client.get("/atlas/api/summary")

    assert resp.status_code == 200
    assert resp.json() == {
        "total_opportunities": 2,
        "stages": [
            {"stage": "applied", "count": 1},
            {"stage": "selected", "count": 1},
        ],
    }


def test_atlas_api_routes_are_not_captured_by_spa_fallback(client):
    resp = client.get("/atlas/api/summary")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    assert "ATLAS frontend has not been built" not in resp.text


def test_unknown_atlas_api_route_is_json_404_not_spa_fallback(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {"detail": "ATLAS API route not found"}


def test_dashboard_routes_remain_unaffected(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_service_has_no_write_sql():
    source = inspect.getsource(atlas_service)

    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
    assert "advance_state" not in source
    assert "FollowUpEngine" not in source
