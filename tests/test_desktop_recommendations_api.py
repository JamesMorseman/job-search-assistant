"""ATLAS Desktop Package 7 recommendations API tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_recommendation_service
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.pipeline import PipelineService
from job_search.services.recommendations import Recommendation

ROOT = Path(__file__).resolve().parents[1]
ATLAS_API_PY = (ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py").read_text(
    encoding="utf-8"
)
DEPS_PY = (ROOT / "job_search" / "dashboard" / "deps.py").read_text(encoding="utf-8")
SCHEMA_SQL = (ROOT / "job_search" / "db" / "schema.sql").read_text(encoding="utf-8")


class FakeRecommendationService:
    def __init__(self):
        self.calls = []

    def generate(self, *, summary, most_recent_run):
        self.calls.append((summary, most_recent_run))
        return [
            Recommendation(
                text="Review the latest Radar intake before prioritizing.",
                priority="high",
                action_surface="radar",
            )
        ]


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


@pytest.fixture
def app(db):
    app = create_app()
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


def _insert_job(db_path: str, job_id: str, **overrides):
    import sqlite3

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


def test_recommendations_endpoint_returns_shape_and_generated_at(client, app, db):
    fake = FakeRecommendationService()
    app.dependency_overrides[get_recommendation_service] = lambda: fake
    _insert_job(db, "job-1", app_state="discovered")
    pipeline = PipelineService(db_path=db)
    run_id = pipeline.start_run("ingest", trigger="manual")
    pipeline.update_counters(run_id, jobs_seen=8)
    pipeline.complete_run(run_id)

    resp = client.get("/atlas/api/recommendations")

    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["recommendations", "generated_at"]
    assert body["recommendations"] == [
        {
            "text": "Review the latest Radar intake before prioritizing.",
            "priority": "high",
            "action_surface": "radar",
        }
    ]
    assert "T" in body["generated_at"]
    summary, most_recent_run = fake.calls[0]
    assert summary.total_opportunities == 1
    assert most_recent_run.id == run_id


def test_recommendations_endpoint_allows_empty_recommendations(client, app):
    class EmptyRecommendationService:
        def generate(self, *, summary, most_recent_run):
            return []

    app.dependency_overrides[get_recommendation_service] = lambda: EmptyRecommendationService()

    resp = client.get("/atlas/api/recommendations")

    assert resp.status_code == 200
    assert resp.json()["recommendations"] == []


def test_recommendations_endpoint_is_get_only_and_uses_existing_context_services():
    assert '@router.get("/recommendations"' in ATLAS_API_PY
    assert "atlas_service.get_summary()" in ATLAS_API_PY
    assert "pipeline_service.list_recent_runs(limit=1)" in ATLAS_API_PY
    assert "recommendation_service.generate" in ATLAS_API_PY
    assert "get_recommendation_service" in DEPS_PY
    assert "RecommendationService()" in DEPS_PY
    for verb in ['@router.put(', '@router.patch(', '@router.delete(']:
        assert verb not in ATLAS_API_PY
    # Package 10 authorizes exactly one POST mutation route (Focus
    # resolution); Recommendations itself must not gain one.
    assert '@router.post("/recommendations' not in ATLAS_API_PY


def test_recommendations_package_does_not_add_schema_or_persistence():
    assert "recommendations" not in SCHEMA_SQL.lower()
    assert "recommendation" not in SCHEMA_SQL.lower()
