"""Tests for the Firm Repository dashboard UI (W2-FIRM-REPO-UI).

Mirrors the dependency-override pattern used in `tests/test_dashboard.py`:
routes are exercised against a stub `FirmsService`-shaped object via
`app.dependency_overrides`, never a real database. This proves the routes
depend on the injected service (per `job_search/dashboard/deps.py`) rather
than constructing `FirmsService()` directly or touching `job_search.db`.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_firms_service
from job_search.services.firms import FirmDetail, FirmStatus, FirmSummary


def _make_summary(**overrides) -> FirmSummary:
    fields = dict(
        firm_id="acme-eng",
        name="Acme Engineering",
        ats_tier="tier_1",
        manual_priority="favored",
        employee_count="1000-5000",
        enr_rank=42,
        disciplines=["structural", "civil"],
        known_benefits=["tuition_reimbursement", "pe_support", "mentorship"],
        known_benefit_count=3,
        open_job_count=5,
    )
    fields.update(overrides)
    return FirmSummary(**fields)


def _make_detail(**overrides) -> FirmDetail:
    status = FirmStatus(
        firm_id="acme-eng",
        ats_tier="tier_1",
        circuit_state="closed",
        quarantine_until=None,
        consecutive_failures=0,
        last_successful_fetch="2026-06-20T00:00:00Z",
        last_fingerprinted="2026-06-20T00:00:00Z",
        last_verified="2026-06-01T00:00:00Z",
    )
    fields = dict(
        firm_id="acme-eng",
        name="Acme Engineering",
        website="https://acme-eng.example",
        careers_url="https://acme-eng.example/careers",
        aliases=["Acme Eng", "Acme"],
        ats_type="greenhouse",
        ats_tier="tier_1",
        enr_rank=42,
        employee_count="1000-5000",
        disciplines=["structural", "civil"],
        benefits={"401k_match": "6%"},
        trajectory={"growth": "expanding"},
        manual_priority="favored",
        reputation_notes="Well regarded for structural work.",
        last_verified="2026-06-01T00:00:00Z",
        status=status,
    )
    fields.update(overrides)
    return FirmDetail(**fields)


class _StubFirmsService:
    def __init__(self, firms: list[FirmSummary] | None = None, detail: FirmDetail | None = None):
        self._firms = firms if firms is not None else [_make_summary()]
        self._detail = detail if detail is not None else _make_detail()

    def list_firms(self, manual_priority: str | None = None) -> list[FirmSummary]:
        return self._firms

    def get_firm(self, firm_id: str):
        if firm_id == self._detail.firm_id:
            return self._detail
        return None


class _FailingFirmsService:
    def list_firms(self, manual_priority: str | None = None):
        raise RuntimeError("boom")

    def get_firm(self, firm_id: str):
        raise RuntimeError("boom")


@pytest.fixture
def app():
    return create_app()


def test_firms_list_renders_rows_from_stub(app):
    app.dependency_overrides[get_firms_service] = lambda: _StubFirmsService(
        firms=[
            _make_summary(firm_id="acme-eng", name="Acme Engineering"),
            _make_summary(firm_id="globex-structural", name="Globex Structural", ats_tier="tier_2"),
        ]
    )
    with TestClient(app) as client:
        resp = client.get("/dashboard/firms")

    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
    assert "Globex Structural" in resp.text
    assert "/dashboard/firms/acme-eng" in resp.text
    assert "/dashboard/firms/globex-structural" in resp.text


def test_firms_list_renders_empty_state_without_error(app):
    app.dependency_overrides[get_firms_service] = lambda: _StubFirmsService(firms=[])
    with TestClient(app) as client:
        resp = client.get("/dashboard/firms")

    assert resp.status_code == 200
    assert "No firms recorded" in resp.text


def test_firms_list_includes_review_queue_not_available_note(app):
    app.dependency_overrides[get_firms_service] = lambda: _StubFirmsService(firms=[])
    with TestClient(app) as client:
        resp = client.get("/dashboard/firms")

    assert resp.status_code == 200
    assert "not yet available" in resp.text


def test_firm_detail_renders_known_firm(app):
    app.dependency_overrides[get_firms_service] = lambda: _StubFirmsService(
        detail=_make_detail(firm_id="acme-eng", name="Acme Engineering")
    )
    with TestClient(app) as client:
        resp = client.get("/dashboard/firms/acme-eng")

    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
    assert "greenhouse" in resp.text
    assert "tier_1" in resp.text
    assert "closed" in resp.text


def test_firm_detail_unknown_firm_returns_404(app):
    app.dependency_overrides[get_firms_service] = lambda: _StubFirmsService(
        detail=_make_detail(firm_id="acme-eng")
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/firms/does-not-exist")

    assert resp.status_code == 404
    assert "does-not-exist" in resp.text


def test_firms_list_service_failure_returns_503(app):
    app.dependency_overrides[get_firms_service] = lambda: _FailingFirmsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/firms")

    assert resp.status_code == 503


def test_firm_detail_service_failure_returns_503(app):
    app.dependency_overrides[get_firms_service] = lambda: _FailingFirmsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/firms/acme-eng")

    assert resp.status_code == 503


def test_dependency_function_returns_firms_service_instance():
    from job_search.services.firms import FirmsService

    assert isinstance(get_firms_service(), FirmsService)
