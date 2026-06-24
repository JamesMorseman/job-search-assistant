"""Tests for job_search.services.location_economics_service (Build 1, Lane B).

Covers the read-only wiring (no DB) and the
/atlas/api/opportunities/{job_id}/location-economics endpoint end to end.
"""

from __future__ import annotations

import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.atlas import AtlasDataService
from job_search.services.location_economics_service import (
    build_location_economics_preview_for_opportunity,
)


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)
    init_db(db_path)
    yield db_path


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
        description_raw="Raw description",
        description_normalized="Normalized description",
        match_score=0.72,
        stretch_category="qualified",
        location_city="Cleveland",
        location_state="OH",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def test_build_preview_for_ranked_metro_includes_economics_notes(db):
    _insert_job(db, "job-1", location_city="Cleveland", location_state="OH")
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")

    preview = build_location_economics_preview_for_opportunity(opportunity)

    assert preview.ranked is True
    assert preview.metro_name is not None
    assert len(preview.dimension_notes) == 5


def test_build_preview_for_remote_posting(db):
    _insert_job(db, "job-1", location_city="Remote", location_state=None)
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")

    preview = build_location_economics_preview_for_opportunity(opportunity)

    assert preview.ranked is False
    assert preview.match_kind == "remote"


def test_build_preview_does_not_mutate_opportunity(db):
    _insert_job(db, "job-1")
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")
    original = opportunity.model_copy(deep=True)

    build_location_economics_preview_for_opportunity(opportunity)

    assert opportunity == original


@pytest.fixture
def client(db):
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_location_economics_endpoint_returns_explanation(client, db):
    _insert_job(db, "job-1", location_city="Cleveland", location_state="OH")

    resp = client.get("/atlas/api/opportunities/job-1/location-economics")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body["ranked"] is True
    assert "may indicate" in body["headline"].lower()


def test_location_economics_endpoint_404_for_missing_job(client):
    resp = client.get("/atlas/api/opportunities/does-not-exist/location-economics")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Opportunity not found"}


def test_location_economics_endpoint_is_read_only_no_db_mutation(client, db):
    _insert_job(db, "job-1")

    before = sqlite3.connect(db).execute(
        "SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)
    ).fetchone()
    client.get("/atlas/api/opportunities/job-1/location-economics")
    after = sqlite3.connect(db).execute(
        "SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)
    ).fetchone()

    assert before == after


def test_location_economics_endpoint_uses_advisory_language(client, db):
    _insert_job(db, "job-1", location_city="Cleveland", location_state="OH")

    resp = client.get("/atlas/api/opportunities/job-1/location-economics")
    body = resp.json()
    full_text = " ".join(
        [body["headline"], *body["dimension_notes"], *body["economics_notes"], *body["caveats"]]
    ).lower()

    assert "this means" not in full_text
    assert "you should" not in full_text
