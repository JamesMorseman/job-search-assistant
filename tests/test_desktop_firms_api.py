"""Tests for the Build 1 ATLAS Desktop Firm Repository read-only surface.

GET /atlas/api/firms and GET /atlas/api/firms/{firm_id} reuse the existing
FirmsService — the same read-only boundary the legacy dashboard's
/dashboard/firms screen already uses. No new firm-intelligence logic.
"""

from __future__ import annotations

import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db


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


def _insert_firm(db_path: str, firm_id: str, name: str = "Test Firm", **kwargs):
    defaults = dict(
        ats_tier="unknown",
        manual_priority="neutral",
        employee_count=None,
        enr_rank=None,
        specialties="[]",
        known_benefits="[]",
        website=None,
        careers_url=None,
        aliases="[]",
        ats_type=None,
        benefits_json="{}",
        trajectory_json="{}",
        reputation_notes=None,
        last_verified=None,
        circuit_state="closed",
        quarantine_until=None,
        consecutive_failures=0,
        last_successful_fetch=None,
        last_fingerprinted=None,
    )
    defaults.update(kwargs)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT OR REPLACE INTO firms
           (firm_id, name, ats_tier, manual_priority, employee_count, enr_rank,
            specialties, known_benefits, website, careers_url, aliases, ats_type,
            benefits_json, trajectory_json, reputation_notes, last_verified,
            circuit_state, quarantine_until, consecutive_failures,
            last_successful_fetch, last_fingerprinted)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            firm_id, name,
            defaults["ats_tier"], defaults["manual_priority"], defaults["employee_count"],
            defaults["enr_rank"], defaults["specialties"], defaults["known_benefits"],
            defaults["website"], defaults["careers_url"], defaults["aliases"],
            defaults["ats_type"], defaults["benefits_json"], defaults["trajectory_json"],
            defaults["reputation_notes"], defaults["last_verified"],
            defaults["circuit_state"], defaults["quarantine_until"],
            defaults["consecutive_failures"], defaults["last_successful_fetch"],
            defaults["last_fingerprinted"],
        ),
    )
    conn.commit()
    conn.close()


def test_list_firms_returns_empty_list_when_no_firms(client, db):
    resp = client.get("/atlas/api/firms")

    assert resp.status_code == 200
    assert resp.json() == {"firms": []}


def test_list_firms_returns_firm_summaries(client, db):
    _insert_firm(
        db,
        "f1",
        "Acme Engineering",
        specialties='["structural"]',
        known_benefits='["tuition_support", "mentorship"]',
    )
    _insert_firm(db, "f2", "Beta Engineering")

    resp = client.get("/atlas/api/firms")

    assert resp.status_code == 200
    body = resp.json()
    names = [f["name"] for f in body["firms"]]
    assert names == ["Acme Engineering", "Beta Engineering"]
    assert body["firms"][0]["disciplines"] == ["structural"]
    assert body["firms"][0]["known_benefits"] == ["tuition_support", "mentorship"]
    assert body["firms"][0]["known_benefit_count"] == 2


def test_list_firms_filters_by_manual_priority(client, db):
    _insert_firm(db, "f1", "Acme Engineering", manual_priority="high")
    _insert_firm(db, "f2", "Beta Engineering", manual_priority="neutral")

    resp = client.get("/atlas/api/firms?manual_priority=high")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["firms"]) == 1
    assert body["firms"][0]["name"] == "Acme Engineering"


def test_get_firm_returns_full_detail(client, db):
    _insert_firm(
        db,
        "f1",
        "Acme Engineering",
        website="https://acme.example",
        benefits_json='{"tuition": true}',
    )

    resp = client.get("/atlas/api/firms/f1")

    assert resp.status_code == 200
    body = resp.json()
    assert body["firm_id"] == "f1"
    assert body["name"] == "Acme Engineering"
    assert body["website"] == "https://acme.example"
    assert body["benefits"] == {"tuition": True}
    assert body["status"]["circuit_state"] == "closed"


def test_get_firm_404_for_missing_firm(client, db):
    resp = client.get("/atlas/api/firms/does-not-exist")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Firm not found"}


def test_firms_endpoints_are_read_only_no_db_mutation(client, db):
    _insert_firm(db, "f1", "Acme Engineering")

    before = sqlite3.connect(db).execute("SELECT * FROM firms WHERE firm_id = ?", ("f1",)).fetchone()
    client.get("/atlas/api/firms")
    client.get("/atlas/api/firms/f1")
    after = sqlite3.connect(db).execute("SELECT * FROM firms WHERE firm_id = ?", ("f1",)).fetchone()

    assert before == after


def test_dashboard_firms_route_remains_unaffected(client, db):
    _insert_firm(db, "f1", "Acme Engineering")

    resp = client.get("/dashboard/firms")

    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
