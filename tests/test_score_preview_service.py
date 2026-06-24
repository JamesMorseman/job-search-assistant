"""Tests for job_search.services.score_preview_service (Build 1, Lane B).

Covers the pure reconstruction logic (no DB) and the read-only
/atlas/api/opportunities/{job_id}/score-preview endpoint end to end.
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
from job_search.services.score_preview_service import (
    build_score_preview_for_opportunity,
    _hits_from_reasons,
    _signal_score_from_reasons,
)


def test_hits_from_reasons_reconstructs_signal_hits():
    reasons = [
        {
            "key": "tuition_reimbursement",
            "label": "Tuition reimbursement",
            "source": "jd",
            "weight": 0.18,
            "confidence": 1.0,
            "matched_text": "tuition reimbursement",
            "reason": "JD mentions tuition reimbursement",
        }
    ]
    hits = _hits_from_reasons(reasons)
    assert len(hits) == 1
    assert hits[0].key == "tuition_reimbursement"
    assert hits[0].label == "Tuition reimbursement"
    assert hits[0].weight == 0.18


def test_hits_from_reasons_skips_malformed_entries():
    reasons = [
        "not-a-dict",
        {"key": "valid", "label": "Valid", "weight": "not-a-number"},
        {"key": "ok", "label": "OK", "weight": 0.1},
    ]
    hits = _hits_from_reasons(reasons)
    assert len(hits) == 1
    assert hits[0].key == "ok"


def test_hits_from_reasons_handles_empty_list():
    assert _hits_from_reasons([]) == []


def test_signal_score_from_reasons_defaults_missing_score_to_zero():
    score = _signal_score_from_reasons(None, [])
    assert score.score == 0.0
    assert score.hits == []


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
        benefit_score=0.5,
        career_trajectory_score=0.4,
        benefit_reasons='[{"key": "tuition_reimbursement", "label": "Tuition reimbursement", "weight": 0.18, "confidence": 1.0, "reason": "JD mentions tuition"}]',
        trajectory_reasons='[{"key": "eit_pe_path", "label": "EIT/PE Path", "weight": 0.1, "confidence": 1.0, "reason": "JD mentions PE path"}]',
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def test_build_score_preview_for_opportunity_uses_persisted_data(db):
    _insert_job(db, "job-1", location_city="Denver", location_state="CO")
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")

    preview = build_score_preview_for_opportunity(opportunity)

    assert preview.overall_score == 0.72
    component_names = {c.name for c in preview.components}
    assert {"benefit", "trajectory", "location"}.issubset(component_names)
    benefit_component = next(c for c in preview.components if c.name == "benefit")
    assert "Tuition reimbursement" in benefit_component.top_reasons


def test_build_score_preview_for_opportunity_does_not_mutate_opportunity(db):
    _insert_job(db, "job-1")
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")
    original = opportunity.model_copy(deep=True)

    build_score_preview_for_opportunity(opportunity)

    assert opportunity == original


def test_build_score_preview_handles_no_reasons_gracefully(db):
    _insert_job(
        db,
        "job-1",
        benefit_score=0.0,
        career_trajectory_score=0.0,
        benefit_reasons="[]",
        trajectory_reasons="[]",
    )
    service = AtlasDataService()
    opportunity = service.get_opportunity("job-1")

    preview = build_score_preview_for_opportunity(opportunity)

    assert preview.overall_score is not None
    # No exception, and components are still produced (with "no signals" summaries).
    assert len(preview.components) >= 2


@pytest.fixture
def client(db):
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_score_preview_endpoint_returns_explanation(client, db):
    _insert_job(db, "job-1", location_city="Denver", location_state="CO")

    resp = client.get("/atlas/api/opportunities/job-1/score-preview")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    body = resp.json()
    assert body["overall_score"] == 0.72
    assert "headline" in body
    assert any(c["name"] == "benefit" for c in body["components"])


def test_score_preview_endpoint_404_for_missing_job(client):
    resp = client.get("/atlas/api/opportunities/does-not-exist/score-preview")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Opportunity not found"}


def test_score_preview_endpoint_is_read_only_no_db_mutation(client, db):
    _insert_job(db, "job-1")

    before = sqlite3.connect(db).execute("SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    client.get("/atlas/api/opportunities/job-1/score-preview")
    after = sqlite3.connect(db).execute("SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()

    assert before == after
