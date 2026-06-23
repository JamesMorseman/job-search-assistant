"""Tests for the Phase 5 dashboard application shell, Review Queue, Job
Detail, and Documents screens.

Covers: application startup, the service-integration boundary
(`job_search.dashboard.deps`), Review Queue rendering, empty-state
behavior, select/reject actions (Package 2), Job Detail rendering and
navigation (Package 3), Documents rendering and navigation (Package 4a),
and service-failure handling. No test in this file queries SQLite from "UI
code" — the dashboard routes consume `JobsService`/`TrackerService`/
`DocumentsService` exactly as a real deployment would.
"""

from __future__ import annotations

from datetime import date, timedelta
import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import (
    get_documents_service,
    get_firms_service,
    get_jobs_service,
    get_metrics_service,
    get_pipeline_service,
    get_source_health_service,
    get_tracker_service,
)
from job_search.db.connection import get_db, init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.documents import DocumentsService
from job_search.services.firms import FirmsService
from job_search.services.jobs import JobsService
from job_search.services.metrics import MetricsService
from job_search.services.pipeline import PipelineService
from job_search.services.tracker import TrackerService
from job_search.tracking import advance_state


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
        description_normalized="structural design",
        match_score=0.8,
        stretch_category="qualified",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def _advance(db_path: str, job_id: str, *states: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    for state in states:
        advance_state(conn, job_id, state, note="test")
    conn.commit()
    conn.close()


@pytest.fixture
def client(db):
    app = create_app()
    with TestClient(app) as c:
        yield c


# ── Application startup ──────────────────────────────────────────────────


def test_app_starts_and_healthz_responds(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_redirects_to_review_queue(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/dashboard/review-queue"


def test_dashboard_root_renders_navigation_shell(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "Review Queue" in resp.text
    assert "Application Tracker" in resp.text  # listed, not implemented


# ── Service integration boundary ─────────────────────────────────────────


def test_atlas_spa_route_does_not_capture_dashboard_routes(client):
    resp = client.get("/dashboard/review-queue")
    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_spa_route_resolves_or_reports_missing_build(client):
    resp = client.get("/atlas")
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "<!doctype html>" in resp.text.lower()
    else:
        assert "ATLAS frontend has not been built" in resp.text


def test_dependency_functions_return_service_instances():
    assert isinstance(get_jobs_service(), JobsService)
    assert isinstance(get_documents_service(), DocumentsService)
    assert isinstance(get_tracker_service(), TrackerService)
    assert isinstance(get_metrics_service(), MetricsService)
    assert isinstance(get_firms_service(), FirmsService)


def test_review_queue_route_uses_dependency_override_not_direct_construction(db):
    """Proves the route depends on the injected service, not a hardcoded
    JobsService() call — overriding the dependency changes the response
    without touching the database."""
    app = create_app()

    class _StubJobsService:
        def list_jobs(self, app_state=None, source=None, limit=None, offset=0, q=None):
            assert app_state == "presented"
            return []

    app.dependency_overrides[get_jobs_service] = lambda: _StubJobsService()
    with TestClient(app) as client:
        resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "No jobs are currently presented for review." in resp.text


# ── Review Queue rendering ───────────────────────────────────────────────


def test_review_queue_renders_presented_jobs(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_job(db, "j2", company="Globex Structural", title="Civil Engineer II", source="usajobs")
    _advance(db, "j1", "presented")
    _advance(db, "j2", "presented")

    resp = client.get("/dashboard/review-queue")
    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
    assert "Structural Engineer I" in resp.text
    assert "Globex Structural" in resp.text


def test_review_queue_excludes_jobs_not_in_presented_state(client, db):
    _insert_job(db, "j1", company="Acme Engineering")  # stays at 'discovered'
    _insert_job(db, "j2", company="Globex Structural")
    _advance(db, "j2", "presented", "selected")  # moved past presented

    resp = client.get("/dashboard/review-queue")
    assert resp.status_code == 200
    assert "Acme Engineering" not in resp.text
    assert "Globex Structural" not in resp.text


def test_review_queue_displays_remote_flag_and_stretch_category(client, db):
    _insert_job(db, "j1", remote_flag="hybrid", stretch_category="competitive_stretch")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue")
    assert "hybrid" in resp.text
    assert "competitive_stretch" in resp.text


def test_review_queue_renders_apply_link_when_apply_url_present(client, db):
    _insert_job(db, "j1", apply_url="https://example.invalid/jobs/123")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue")
    assert 'href="https://example.invalid/jobs/123"' in resp.text
    assert 'data-testid="apply-link"' in resp.text


def test_review_queue_omits_apply_link_when_apply_url_missing(client, db):
    _insert_job(db, "j1", apply_url=None)
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue")
    assert 'data-testid="apply-link"' not in resp.text


def test_review_queue_renders_select_and_reject_actions(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue")
    assert f'/dashboard/review-queue/j1/select' in resp.text
    assert f'/dashboard/review-queue/j1/reject' in resp.text
    # 2 action forms (select/reject) + 1 search form (ANNA-P2-DASHBOARD-DIAGNOSTICS)
    assert resp.text.count("<form") == 3


# ── Empty-state behavior ─────────────────────────────────────────────────


def test_review_queue_shows_empty_state_with_no_presented_jobs(client, db):
    resp = client.get("/dashboard/review-queue")
    assert resp.status_code == 200
    assert "No jobs are currently presented for review." in resp.text
    assert "<table>" not in resp.text


# ── Select action ─────────────────────────────────────────────────────────


def test_select_action_transitions_job_to_selected(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    resp = client.post("/dashboard/review-queue/j1/select", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/review-queue"

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "selected"


def test_select_action_records_app_transition_with_note(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    client.post("/dashboard/review-queue/j1/select", follow_redirects=False)

    history = TrackerService().get_state_history("j1")
    assert [h.to_state for h in history] == ["presented", "selected"]
    assert history[-1].note == "Selected from dashboard Review Queue"


def test_select_action_invalid_transition_redirects_with_error(client, db):
    _insert_job(db, "j1")  # stays at 'discovered' — 'discovered' -> 'selected' is invalid

    resp = client.post("/dashboard/review-queue/j1/select", follow_redirects=False)
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "discovered"  # unchanged


def test_select_action_unknown_job_redirects_with_error(client, db):
    resp = client.post("/dashboard/review-queue/does-not-exist/select", follow_redirects=False)
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


# ── Reject action ────────────────────────────────────────────────────────


def test_reject_action_transitions_job_to_rejected(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    resp = client.post("/dashboard/review-queue/j1/reject", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/review-queue"

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "rejected"


def test_reject_action_removes_job_from_review_queue(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented")

    client.post("/dashboard/review-queue/j1/reject", follow_redirects=False)

    resp = client.get("/dashboard/review-queue")
    assert "Acme Engineering" not in resp.text


def test_reject_action_invalid_transition_redirects_with_error(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied", "rejected")  # already terminal

    resp = client.post("/dashboard/review-queue/j1/reject", follow_redirects=False)
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


# ── Mutation-path behavior ───────────────────────────────────────────────


def test_select_action_uses_tracker_service_not_direct_db_write(db):
    """Proves select_job() routes through the injected TrackerService —
    overriding it intercepts the mutation instead of touching the database."""
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    app = create_app()
    calls = []

    class _StubTrackerService:
        def transition_job(self, canonical_job_id, to_state, note=None):
            calls.append((canonical_job_id, to_state, note))
            return True

    app.dependency_overrides[get_tracker_service] = lambda: _StubTrackerService()
    with TestClient(app) as client:
        client.post("/dashboard/review-queue/j1/select", follow_redirects=False)

    assert calls == [("j1", "selected", "Selected from dashboard Review Queue")]
    # Real state untouched — proves the route called the override, not advance_state() directly.
    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "presented"


def test_reject_action_does_not_write_app_transitions_directly(db):
    """If reject_job() bypassed TrackerService and wrote SQL directly, this
    would still pass — so it also asserts the transition note matches what
    only TrackerService.transition_job() would have written."""
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    app = create_app()
    with TestClient(app) as client:
        client.post("/dashboard/review-queue/j1/reject", follow_redirects=False)

    with get_db() as conn:
        row = conn.execute(
            "SELECT from_state, to_state, note FROM app_transitions WHERE canonical_job_id = 'j1' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    assert row["from_state"] == "presented"
    assert row["to_state"] == "rejected"
    assert row["note"] == "Rejected from dashboard Review Queue"


# ── Job Detail rendering ─────────────────────────────────────────────────


def test_job_detail_renders_core_fields(client, db):
    _insert_job(
        db,
        "j1",
        company="Acme Engineering",
        title="Structural Engineer I",
        location_city="Denver",
        location_state="CO",
        remote_flag="hybrid",
        apply_url="https://example.invalid/jobs/123",
        salary_min=70000,
        salary_max=90000,
        match_score=0.82,
    )

    resp = client.get("/dashboard/jobs/j1")
    assert resp.status_code == 200
    assert "Structural Engineer I" in resp.text
    assert "Acme Engineering" in resp.text
    assert "Denver" in resp.text
    assert "CO" in resp.text
    assert "hybrid" in resp.text
    assert "70000" in resp.text
    assert "90000" in resp.text
    assert 'href="https://example.invalid/jobs/123"' in resp.text


def test_job_detail_renders_grade_rationale_and_reasons(client, db):
    _insert_job(db, "j1")
    with get_db() as conn:
        conn.execute(
            "UPDATE jobs SET llm_grade = ?, llm_rationale = ?, "
            "benefit_reasons = ?, trajectory_reasons = ?, "
            "ko_work_auth = ?, ko_pe_required = 1 WHERE canonical_job_id = ?",
            (
                "strong_fit",
                "Strong alignment with structural design experience.",
                '[{"key": "tuition_reimbursement", "label": "Tuition Reimbursement"}]',
                '[{"key": "eit_pe_path", "label": "EIT/PE Path"}]',
                "US Citizen or Permanent Resident",
                "j1",
            ),
        )

    resp = client.get("/dashboard/jobs/j1")
    assert resp.status_code == 200
    assert "strong_fit" in resp.text
    assert "Strong alignment with structural design experience." in resp.text
    assert "Tuition Reimbursement" in resp.text
    assert "EIT/PE Path" in resp.text
    assert "US Citizen or Permanent Resident" in resp.text


def test_job_detail_renders_knockouts_with_not_stated_fallback(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1")
    assert resp.status_code == 200
    assert "Not stated" in resp.text


# ── Missing-job behavior ─────────────────────────────────────────────────


def test_job_detail_returns_404_for_missing_job(client, db):
    resp = client.get("/dashboard/jobs/does-not-exist")
    assert resp.status_code == 404
    assert "No job found" in resp.text


# ── Navigation from Review Queue ─────────────────────────────────────────


def test_review_queue_links_to_job_detail(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue")
    assert 'href="/dashboard/jobs/j1"' in resp.text
    assert 'data-testid="job-detail-link"' in resp.text


def test_navigating_from_review_queue_link_reaches_job_detail(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented")

    queue_resp = client.get("/dashboard/review-queue")
    assert 'href="/dashboard/jobs/j1"' in queue_resp.text

    detail_resp = client.get("/dashboard/jobs/j1")
    assert detail_resp.status_code == 200
    assert "Structural Engineer I" in detail_resp.text


def test_job_detail_links_back_to_review_queue(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1")
    assert 'href="/dashboard/review-queue"' in resp.text


# ── Service-boundary enforcement (Job Detail) ────────────────────────────


def test_job_detail_uses_dependency_override_not_direct_construction(db):
    """Proves job_detail() depends on the injected JobsService rather than
    constructing one inline — overriding the dependency changes the
    response without touching the database."""
    app = create_app()
    calls = []

    class _StubJobsService:
        def get_job_detail(self, canonical_job_id):
            calls.append(canonical_job_id)
            return None

    app.dependency_overrides[get_jobs_service] = lambda: _StubJobsService()
    with TestClient(app) as client:
        resp = client.get("/dashboard/jobs/some-id")

    assert calls == ["some-id"]
    assert resp.status_code == 404


def test_job_detail_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import jobs as jobs_routes

    source = inspect.getsource(jobs_routes.job_detail)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


# ── Documents rendering ───────────────────────────────────────────────────


def _insert_generated_doc(db_path: str, job_id: str, doc_type: str, drive_url: str, generated_at: str, **overrides):
    fields = dict(
        canonical_job_id=job_id,
        doc_type=doc_type,
        drive_url=drive_url,
        generated_at=generated_at,
    )
    fields.update(overrides)
    columns = ", ".join(fields)
    placeholders = ", ".join("?" for _ in fields)
    conn = sqlite3.connect(db_path)
    conn.execute(f"INSERT INTO generated_docs ({columns}) VALUES ({placeholders})", list(fields.values()))
    conn.commit()
    conn.close()


def test_documents_renders_current_resume_and_cover_letter(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-old", "2026-01-01T00:00:00")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-new", "2026-02-01T00:00:00")
    _insert_generated_doc(db, "j1", "cover_letter", "https://drive.invalid/cover-new", "2026-02-01T00:00:00")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    assert "Structural Engineer I" in resp.text
    assert "Acme Engineering" in resp.text
    assert 'href="https://drive.invalid/resume-new"' in resp.text
    assert 'href="https://drive.invalid/cover-new"' in resp.text


def test_documents_history_includes_all_versions(client, db):
    _insert_job(db, "j1")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-old", "2026-01-01T00:00:00")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-new", "2026-02-01T00:00:00")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    assert "https://drive.invalid/resume-old" in resp.text
    assert "https://drive.invalid/resume-new" in resp.text


def test_documents_displays_generation_timestamps_and_doc_type(client, db):
    _insert_job(db, "j1")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume", "2026-03-01T12:00:00")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert "2026-03-01T12:00:00" in resp.text
    assert "resume" in resp.text


# ── Current/latest resolution ────────────────────────────────────────────


def test_documents_marks_only_latest_version_as_current(client, db):
    import re

    _insert_job(db, "j1")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-old", "2026-01-01T00:00:00")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-new", "2026-02-01T00:00:00")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    # The "current" marker should appear exactly once (only the newest resume row).
    markers = re.findall(r'data-testid="is-current">\s*current\s*<', resp.text)
    assert len(markers) == 1


def test_documents_current_resolution_matches_service_directly(client, db):
    _insert_job(db, "j1")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-old", "2026-01-01T00:00:00")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-new", "2026-02-01T00:00:00")

    expected = DocumentsService().get_current_documents("j1")
    resp = client.get("/dashboard/jobs/j1/documents")

    assert expected["resume"].drive_url in resp.text


# ── Empty-state behavior ─────────────────────────────────────────────────


def test_documents_shows_empty_state_with_no_generated_documents(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    assert "No documents have been generated for this job yet." in resp.text


# ── Navigation ────────────────────────────────────────────────────────────


def test_job_detail_links_to_documents(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1")
    assert resp.status_code == 200
    assert 'href="/dashboard/jobs/j1/documents"' in resp.text
    assert 'data-testid="documents-link"' in resp.text


def test_documents_links_back_to_job_detail(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert 'href="/dashboard/jobs/j1"' in resp.text


def test_navigating_from_job_detail_link_reaches_documents(client, db):
    _insert_job(db, "j1", title="Structural Engineer I")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume", "2026-01-01T00:00:00")

    detail_resp = client.get("/dashboard/jobs/j1")
    assert 'href="/dashboard/jobs/j1/documents"' in detail_resp.text

    docs_resp = client.get("/dashboard/jobs/j1/documents")
    assert docs_resp.status_code == 200
    assert "Structural Engineer I" in docs_resp.text


# ── Missing-job behavior (Documents) ─────────────────────────────────────


def test_documents_returns_404_for_missing_job(client, db):
    resp = client.get("/dashboard/jobs/does-not-exist/documents")
    assert resp.status_code == 404
    assert "No job found" in resp.text


# ── Service-boundary enforcement (Documents) ─────────────────────────────


def test_documents_uses_dependency_overrides_not_direct_construction(db):
    """Proves job_documents() depends on the injected JobsService and
    DocumentsService rather than constructing either inline."""
    _insert_job(db, "j1")
    app = create_app()
    calls = []

    class _StubDocumentsService:
        def get_current_documents(self, canonical_job_id):
            calls.append(("current", canonical_job_id))
            return {"resume": None, "cover_letter": None}

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            calls.append(("history", canonical_job_id))
            return []

    app.dependency_overrides[get_documents_service] = lambda: _StubDocumentsService()
    with TestClient(app) as client:
        resp = client.get("/dashboard/jobs/j1/documents")

    assert resp.status_code == 200
    assert ("current", "j1") in calls
    assert ("history", "j1") in calls


def test_documents_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import documents as documents_routes

    source = inspect.getsource(documents_routes.job_documents)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_documents_route_never_calls_regenerate_documents():
    """Confirms Package 4a introduces no write path — `regenerate_documents`
    (Package 4b) must not be invoked from this module. Checks for the call
    syntax specifically, not the docstring's explanatory mention of the
    method name."""
    import inspect

    from job_search.dashboard.routes import documents as documents_routes

    source = inspect.getsource(documents_routes.job_documents)
    assert ".regenerate_documents(" not in source


# ── Service failure handling (Documents) ─────────────────────────────────


def test_documents_handles_jobs_service_failure_without_500(db):
    app = create_app()

    class _FailingJobsService:
        def get_job_detail(self, canonical_job_id):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_jobs_service] = lambda: _FailingJobsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/jobs/j1/documents")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


def test_documents_handles_documents_service_failure_without_500(db):
    _insert_job(db, "j1")
    app = create_app()

    class _FailingDocumentsService:
        def get_current_documents(self, canonical_job_id):
            raise RuntimeError("simulated database outage")

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            return []

    app.dependency_overrides[get_documents_service] = lambda: _FailingDocumentsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/jobs/j1/documents")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Service failure handling ─────────────────────────────────────────────


def test_job_detail_handles_service_failure_without_500_traceback(db):
    app = create_app()

    class _FailingJobsService:
        def get_job_detail(self, canonical_job_id):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_jobs_service] = lambda: _FailingJobsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/jobs/j1")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


def test_review_queue_handles_service_failure_without_500_traceback(db):
    app = create_app()

    class _FailingJobsService:
        def list_jobs(self, app_state=None, source=None, limit=None, offset=0, q=None):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_jobs_service] = lambda: _FailingJobsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Package 4b — Regeneration action ────────────────────────────────────


def test_regenerate_action_redirects_to_documents_on_success(db):
    _insert_job(db, "j1")

    app = create_app()
    calls = []

    class _StubDocumentsService:
        def regenerate_documents(self, canonical_job_id, force=True):
            calls.append(canonical_job_id)
            from job_search.services.documents import RegenerationResult
            return RegenerationResult(canonical_job_id=canonical_job_id, resume_url=None, cover_url=None)

        def get_current_documents(self, canonical_job_id):
            return {"resume": None, "cover_letter": None}

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            return []

    app.dependency_overrides[get_documents_service] = lambda: _StubDocumentsService()
    with TestClient(app) as client:
        resp = client.post("/dashboard/jobs/j1/documents/regenerate", follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/jobs/j1/documents"
    assert calls == ["j1"]


def test_regenerate_action_redirects_with_error_on_failure(db):
    _insert_job(db, "j1")

    app = create_app()

    class _FailingDocumentsService:
        def regenerate_documents(self, canonical_job_id, force=True):
            from job_search.services.documents import DocumentRegenerationError
            raise DocumentRegenerationError("generation failed")

        def get_current_documents(self, canonical_job_id):
            return {"resume": None, "cover_letter": None}

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            return []

    app.dependency_overrides[get_documents_service] = lambda: _FailingDocumentsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.post("/dashboard/jobs/j1/documents/regenerate", follow_redirects=False)

    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]
    assert "/dashboard/jobs/j1/documents" in resp.headers["location"]


def test_regenerate_action_uses_documents_service_not_direct_generation(db):
    """Proves regeneration routes through the injected DocumentsService —
    overriding the dependency intercepts the call."""
    _insert_job(db, "j1")

    app = create_app()
    calls = []

    class _StubDocumentsService:
        def regenerate_documents(self, canonical_job_id, force=True):
            calls.append(canonical_job_id)
            from job_search.services.documents import RegenerationResult
            return RegenerationResult(canonical_job_id=canonical_job_id, resume_url=None, cover_url=None)

        def get_current_documents(self, canonical_job_id):
            return {"resume": None, "cover_letter": None}

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            return []

    app.dependency_overrides[get_documents_service] = lambda: _StubDocumentsService()
    with TestClient(app) as client:
        client.post("/dashboard/jobs/j1/documents/regenerate", follow_redirects=False)

    assert "j1" in calls


def test_documents_page_displays_error_from_query_param(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1/documents?error=Document+regeneration+failed.")
    assert resp.status_code == 200
    assert "Document regeneration failed." in resp.text
    assert 'data-testid="regeneration-error"' in resp.text


def test_documents_page_shows_no_error_without_query_param(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    assert 'data-testid="regeneration-error"' not in resp.text


def test_regenerate_history_preserved_and_new_doc_becomes_current(db):
    """After regeneration, old document rows remain in history and the new
    document becomes current (query-derived resolution unchanged)."""
    import re

    _insert_job(db, "j1", title="Structural Engineer I")
    _insert_generated_doc(db, "j1", "resume", "https://drive.invalid/resume-old", "2026-01-01T00:00:00")

    class _StubProcessor:
        def generate_for_selected(self, job_ids, force=True):
            conn = sqlite3.connect(db)
            conn.execute(
                "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at) "
                "VALUES (?, ?, ?, ?)",
                ("j1", "resume", "https://drive.invalid/resume-new", "2026-06-01T00:00:00"),
            )
            conn.commit()
            conn.close()
            return {
                "generated": 1,
                "errors": 0,
                "docs": [{"resume_url": "https://drive.invalid/resume-new", "cover_url": None}],
            }

    from job_search.services.documents import DocumentsService as _DS
    app = create_app()
    app.dependency_overrides[get_documents_service] = lambda: _DS(processor=_StubProcessor())
    with TestClient(app) as c:
        resp = c.post("/dashboard/jobs/j1/documents/regenerate", follow_redirects=True)

    assert resp.status_code == 200
    # Old doc still visible in history
    assert "https://drive.invalid/resume-old" in resp.text
    # New doc present
    assert "https://drive.invalid/resume-new" in resp.text
    # Only the new doc is marked current
    markers = re.findall(r'data-testid="is-current">\s*current\s*<', resp.text)
    assert len(markers) == 1


def test_regenerate_stays_in_documents_workflow_after_success(db):
    """After successful regeneration the user is redirected to the Documents
    screen, not back to Review Queue or Job Detail."""
    _insert_job(db, "j1")

    app = create_app()

    class _StubDocumentsService:
        def regenerate_documents(self, canonical_job_id, force=True):
            from job_search.services.documents import RegenerationResult
            return RegenerationResult(canonical_job_id=canonical_job_id, resume_url=None, cover_url=None)

        def get_current_documents(self, canonical_job_id):
            return {"resume": None, "cover_letter": None}

        def list_documents(self, canonical_job_id, doc_type=None, limit=None):
            return []

    app.dependency_overrides[get_documents_service] = lambda: _StubDocumentsService()
    with TestClient(app) as client:
        resp = client.post("/dashboard/jobs/j1/documents/regenerate", follow_redirects=True)

    assert resp.status_code == 200
    assert 'data-testid="regenerate-button"' in resp.text


def test_regenerate_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import documents as documents_routes

    source = inspect.getsource(documents_routes.regenerate_documents_action)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_documents_page_shows_regenerate_button(client, db):
    _insert_job(db, "j1")

    resp = client.get("/dashboard/jobs/j1/documents")
    assert resp.status_code == 200
    assert 'data-testid="regenerate-button"' in resp.text
    assert f'/dashboard/jobs/j1/documents/regenerate' in resp.text


# ── Service failure handling ─────────────────────────────────────────────


def test_select_action_handles_service_failure_without_500(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    app = create_app()

    class _FailingTrackerService:
        def transition_job(self, canonical_job_id, to_state, note=None):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_tracker_service] = lambda: _FailingTrackerService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.post("/dashboard/review-queue/j1/select", follow_redirects=False)

    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Package 5b — Transition action ──────────────────────────────────────


def test_transition_action_advances_job_state(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    resp = client.post(
        "/dashboard/tracker/j1/transition",
        data={"to_state": "acknowledged"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/tracker"

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "acknowledged"


def test_transition_action_records_note_in_history(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    client.post(
        "/dashboard/tracker/j1/transition",
        data={"to_state": "acknowledged"},
        follow_redirects=False,
    )

    history = TrackerService().get_state_history("j1")
    last = history[-1]
    assert last.to_state == "acknowledged"
    assert last.note is not None
    assert "acknowledged" in last.note


def test_transition_action_invalid_transition_redirects_with_error(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied", "rejected")  # terminal

    resp = client.post(
        "/dashboard/tracker/j1/transition",
        data={"to_state": "screen"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "rejected"  # unchanged


def test_transition_action_unknown_job_redirects_with_error(client, db):
    resp = client.post(
        "/dashboard/tracker/does-not-exist/transition",
        data={"to_state": "applied"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


def test_transition_action_uses_tracker_service_not_direct_db_write(db):
    """Proves the route calls the injected TrackerService, not advance_state() directly."""
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    app = create_app()
    calls = []

    class _StubTrackerService:
        def list_tracker_rows(self, states=None):
            return []

        def list_due_followups(self, as_of=None, include_resolved=False):
            return []

        def transition_job(self, canonical_job_id, to_state, note=None):
            calls.append((canonical_job_id, to_state))
            return True

    app.dependency_overrides[get_tracker_service] = lambda: _StubTrackerService()
    with TestClient(app) as c:
        c.post(
            "/dashboard/tracker/j1/transition",
            data={"to_state": "acknowledged"},
            follow_redirects=False,
        )

    assert calls == [("j1", "acknowledged")]
    # Real state untouched — proves the override intercepted the call.
    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "applied"


def test_transition_action_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import tracker as tracker_routes

    source = inspect.getsource(tracker_routes.transition_job_action)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_transition_action_service_failure_redirects_with_error(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    app = create_app()

    class _FailingTrackerService:
        def transition_job(self, canonical_job_id, to_state, note=None):
            raise RuntimeError("simulated outage")

    app.dependency_overrides[get_tracker_service] = lambda: _FailingTrackerService()
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.post(
            "/dashboard/tracker/j1/transition",
            data={"to_state": "acknowledged"},
            follow_redirects=False,
        )

    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


def test_tracker_remains_navigable_after_transition(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected", "applied")

    resp = client.post(
        "/dashboard/tracker/j1/transition",
        data={"to_state": "acknowledged"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert "Application Tracker" in resp.text
    assert "acknowledged" in resp.text


# ── Package 5b — Resolve followup action ────────────────────────────────


def _insert_followup_with_id(db_path: str, job_id: str, due_date: str, action_type: str = "check_status") -> int:
    """Insert a followup_queue row and return its id."""
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
        (job_id, action_type, due_date),
    )
    followup_id = cur.lastrowid
    conn.commit()
    conn.close()
    return followup_id


def test_resolve_followup_marks_item_resolved(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    fid = _insert_followup_with_id(db, "j1", "2026-01-01")

    resp = client.post(f"/dashboard/tracker/followups/{fid}/resolve", follow_redirects=False)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/dashboard/tracker"

    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(db)
    row = conn.execute("SELECT resolved FROM followup_queue WHERE id = ?", (fid,)).fetchone()
    conn.close()
    assert row[0] == 1


def test_resolve_followup_removes_item_from_due_list(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected", "applied")
    fid = _insert_followup_with_id(db, "j1", "2026-01-01")

    client.post(f"/dashboard/tracker/followups/{fid}/resolve", follow_redirects=False)

    # After resolving, the item should no longer appear in the default due list.
    resp = client.get("/dashboard/tracker")
    assert f'data-testid="resolve-submit-{fid}"' not in resp.text


def test_resolve_followup_uses_tracker_service_not_direct_db_write(db):
    """Proves the route calls the injected TrackerService.resolve_followup()."""
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    fid = _insert_followup_with_id(db, "j1", "2026-01-01")

    app = create_app()
    calls = []

    class _StubTrackerService:
        def list_tracker_rows(self, states=None):
            return []

        def list_due_followups(self, as_of=None, include_resolved=False):
            return []

        def resolve_followup(self, followup_id):
            calls.append(followup_id)

    app.dependency_overrides[get_tracker_service] = lambda: _StubTrackerService()
    with TestClient(app) as c:
        c.post(f"/dashboard/tracker/followups/{fid}/resolve", follow_redirects=False)

    assert calls == [fid]


def test_resolve_followup_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import tracker as tracker_routes

    source = inspect.getsource(tracker_routes.resolve_followup_action)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_resolve_followup_service_failure_redirects_with_error(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    fid = _insert_followup_with_id(db, "j1", "2026-01-01")

    app = create_app()

    class _FailingTrackerService:
        def resolve_followup(self, followup_id):
            raise RuntimeError("simulated outage")

    app.dependency_overrides[get_tracker_service] = lambda: _FailingTrackerService()
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.post(f"/dashboard/tracker/followups/{fid}/resolve", follow_redirects=False)

    assert resp.status_code == 303
    assert "error=" in resp.headers["location"]


def test_tracker_renders_transition_forms_for_non_terminal_states(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="transition-form"' in resp.text
    # applied → acknowledged, screen, rejected, ghosted are all valid
    assert "acknowledged" in resp.text


def test_tracker_renders_no_transition_form_for_terminal_state(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied", "rejected")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="no-transitions"' in resp.text


def test_tracker_renders_resolve_button_for_due_followups(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    fid = _insert_followup_with_id(db, "j1", "2026-01-01")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert f'data-testid="resolve-submit-{fid}"' in resp.text
    assert 'data-testid="resolve-form"' in resp.text


def test_tracker_displays_error_from_query_param(client, db):
    resp = client.get("/dashboard/tracker?error=Transition+failed.")
    assert resp.status_code == 200
    assert "Transition failed." in resp.text
    assert 'data-testid="tracker-error"' in resp.text


def test_tracker_shows_no_error_without_query_param(client, db):
    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="tracker-error"' not in resp.text


# ── Package 5a — Application Tracker read ────────────────────────────────


def _insert_followup(db_path: str, job_id: str, action_type: str, due_date: str, **overrides):
    fields = dict(canonical_job_id=job_id, action_type=action_type, due_date=due_date)
    fields.update(overrides)
    columns = ", ".join(fields)
    placeholders = ", ".join("?" for _ in fields)
    conn = sqlite3.connect(db_path)
    conn.execute(f"INSERT INTO followup_queue ({columns}) VALUES ({placeholders})", list(fields.values()))
    conn.commit()
    conn.close()


def test_tracker_renders_active_applications(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_job(db, "j2", company="Globex Structural", title="Civil Engineer II")
    _advance(db, "j1", "presented", "selected")
    _advance(db, "j2", "presented", "selected", "applied")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
    assert "Structural Engineer I" in resp.text
    assert "Globex Structural" in resp.text
    assert "Civil Engineer II" in resp.text


def test_tracker_shows_current_state_and_last_note(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert "selected" in resp.text
    assert 'data-testid="tracker-state"' in resp.text


def test_tracker_excludes_jobs_not_in_tracked_states(client, db):
    _insert_job(db, "j1", company="Acme Engineering")  # stays at 'discovered'
    _insert_job(db, "j2", company="Globex Structural")
    _advance(db, "j2", "presented")  # 'presented' is not a tracked state

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert "Acme Engineering" not in resp.text
    assert "Globex Structural" not in resp.text


def test_tracker_empty_state_when_no_tracked_applications(client, db):
    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="tracker-empty-state"' in resp.text
    assert "No applications are currently being tracked." in resp.text
    assert "<table>" not in resp.text or 'data-testid="tracker-row"' not in resp.text


def test_tracker_renders_due_followups(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected", "applied")
    _insert_followup(db, "j1", "check_status", "2026-01-01", note="Check in with recruiter")

    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="followup-row"' in resp.text
    assert "check_status" in resp.text
    assert "2026-01-01" in resp.text
    assert "Check in with recruiter" in resp.text


def test_tracker_followups_empty_state_when_none_due(client, db):
    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="followups-empty-state"' in resp.text
    assert "No follow-ups are currently due." in resp.text


def test_tracker_renders_upcoming_followups(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected", "applied")
    upcoming = (date.today() + timedelta(days=3)).isoformat()
    _insert_followup(db, "j1", "check_status", upcoming, note="Plan next check-in")

    resp = client.get("/dashboard/tracker")

    assert resp.status_code == 200
    assert 'data-testid="upcoming-followups-section"' in resp.text
    assert 'data-testid="upcoming-followup-row"' in resp.text
    assert "Plan next check-in" in resp.text
    assert upcoming in resp.text


def test_tracker_upcoming_followups_empty_state_when_none_upcoming(client, db):
    resp = client.get("/dashboard/tracker")

    assert resp.status_code == 200
    assert 'data-testid="upcoming-followups-empty-state"' in resp.text
    assert "No follow-ups are due in the next 7 days." in resp.text


def test_tracker_upcoming_followups_excludes_due_and_later_items(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _insert_job(db, "j2", company="Globex Structural")
    _insert_job(db, "j3", company="Initech Civil")
    _advance(db, "j1", "presented", "selected", "applied")
    _advance(db, "j2", "presented", "selected", "applied")
    _advance(db, "j3", "presented", "selected", "applied")

    due_today = date.today().isoformat()
    in_window = (date.today() + timedelta(days=2)).isoformat()
    outside_window = (date.today() + timedelta(days=9)).isoformat()
    _insert_followup(db, "j1", "check_status", due_today)
    _insert_followup(db, "j2", "check_status", in_window)
    _insert_followup(db, "j3", "check_status", outside_window)

    resp = client.get("/dashboard/tracker")

    assert resp.status_code == 200
    assert 'data-testid="followup-row"' in resp.text
    assert 'data-testid="upcoming-followup-row"' in resp.text
    assert resp.text.count('data-testid="upcoming-followup-row"') == 1
    assert "Acme Engineering" in resp.text
    assert "Globex Structural" in resp.text
    assert outside_window not in resp.text


def test_tracker_upcoming_followups_excludes_resolved_items(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected", "applied")
    upcoming = (date.today() + timedelta(days=3)).isoformat()
    _insert_followup(db, "j1", "check_status", upcoming, resolved=1)

    resp = client.get("/dashboard/tracker")

    assert resp.status_code == 200
    assert 'data-testid="upcoming-followup-row"' not in resp.text


def test_tracker_links_to_job_detail(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected")

    resp = client.get("/dashboard/tracker")
    assert 'href="/dashboard/jobs/j1"' in resp.text
    assert 'data-testid="tracker-job-detail-link"' in resp.text


def test_tracker_followup_links_to_job_detail(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected", "applied")
    _insert_followup(db, "j1", "check_status", "2026-01-01")

    resp = client.get("/dashboard/tracker")
    assert 'data-testid="followup-job-detail-link"' in resp.text
    assert 'href="/dashboard/jobs/j1"' in resp.text


def test_navigating_from_tracker_link_reaches_job_detail(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _advance(db, "j1", "presented", "selected")

    tracker_resp = client.get("/dashboard/tracker")
    assert 'href="/dashboard/jobs/j1"' in tracker_resp.text

    detail_resp = client.get("/dashboard/jobs/j1")
    assert detail_resp.status_code == 200
    assert "Structural Engineer I" in detail_resp.text


def test_tracker_nav_link_visible_in_all_pages(client, db):
    resp = client.get("/dashboard/review-queue")
    assert 'href="/dashboard/tracker"' in resp.text
    assert "Application Tracker" in resp.text


def test_tracker_uses_dependency_override_not_direct_construction(db):
    """Proves application_tracker() depends on the injected TrackerService."""
    app = create_app()
    calls = []

    class _StubTrackerService:
        def list_tracker_rows(self, states=None):
            calls.append("list_tracker_rows")
            return []

        def list_due_followups(self, as_of=None, include_resolved=False):
            calls.append("list_due_followups")
            return []

        def list_upcoming_followups(self, as_of=None, days=7):
            calls.append("list_upcoming_followups")
            return []

    app.dependency_overrides[get_tracker_service] = lambda: _StubTrackerService()
    with TestClient(app) as client:
        resp = client.get("/dashboard/tracker")

    assert resp.status_code == 200
    assert "list_tracker_rows" in calls
    assert "list_due_followups" in calls
    assert "list_upcoming_followups" in calls


def test_tracker_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import tracker as tracker_routes

    source = inspect.getsource(tracker_routes.application_tracker)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_tracker_route_never_calls_mutation_methods():
    import inspect

    from job_search.dashboard.routes import tracker as tracker_routes

    source = inspect.getsource(tracker_routes.application_tracker)
    assert ".transition_job(" not in source
    assert ".resolve_followup(" not in source


def test_tracker_handles_service_failure_without_500(db):
    app = create_app()

    class _FailingTrackerService:
        def list_tracker_rows(self, states=None):
            raise RuntimeError("simulated database outage")

        def list_due_followups(self, as_of=None, include_resolved=False):
            return []

    app.dependency_overrides[get_tracker_service] = lambda: _FailingTrackerService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/tracker")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Package 6 — Metrics ───────────────────────────────────────────────────


from job_search.reporting.funnel import FunnelStats  # noqa: E402


def _stub_metrics_service(stats: FunnelStats):
    """Return a dependency-override factory yielding a MetricsService backed
    by a stub reporter that returns the given FunnelStats."""
    from job_search.services.metrics import MetricsService as _MS

    class _StubReporter:
        def compute(self) -> FunnelStats:
            return stats

    return lambda: _MS(reporter=_StubReporter())


def test_metrics_route_renders_ok(client, db):
    resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert "Metrics" in resp.text


def test_metrics_labels_total_as_total_ever_discovered(client, db):
    resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert "Total ever discovered" in resp.text
    assert 'data-testid="total-jobs-label"' in resp.text


def test_metrics_shows_state_distribution_when_data_present(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        by_state={"discovered": 1, "presented": 2},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert 'data-testid="state-distribution-table"' in resp.text
    assert "discovered" in resp.text
    assert "presented" in resp.text
    assert 'data-testid="state-count"' in resp.text


def test_metrics_shows_empty_state_when_no_jobs(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, by_state={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert 'data-testid="state-distribution-empty"' in resp.text
    assert "No jobs have been ingested yet." in resp.text




def test_metrics_shows_not_enough_data_for_none_median_days(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=2,
        median_days={
            "applied_to_response": None,
            "applied_to_screen": None,
            "applied_to_terminal": None,
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert "Not enough data yet." in resp.text
    assert 'data-testid="median-applied-to-response"' in resp.text


def test_metrics_renders_median_days_when_present(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        median_days={
            "applied_to_response": 7.5,
            "applied_to_screen": None,
            "applied_to_terminal": 14.0,
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert "7.5 days" in resp.text
    assert "14.0 days" in resp.text


def test_metrics_omits_by_discipline_and_by_location(db):
    """by_discipline_state and by_location_metro are not populated by
    FunnelReporter and must not appear as empty sections."""
    app = create_app()
    stats = FunnelStats(
        by_discipline_state={"civil": {"selected": 1}},
        by_location_metro={"Denver": {"presented": 2}},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert "by_discipline_state" not in resp.text
    assert "by_location_metro" not in resp.text
    assert "Denver" not in resp.text


def test_metrics_nav_link_visible_on_all_pages(client, db):
    resp = client.get("/dashboard/review-queue")
    assert 'href="/dashboard/metrics"' in resp.text
    assert "Metrics" in resp.text


def test_metrics_uses_dependency_override_not_direct_construction(db):
    app = create_app()
    calls = []

    class _StubMetricsService:
        def get_funnel_stats(self):
            calls.append("get_funnel_stats")
            return FunnelStats()

    app.dependency_overrides[get_metrics_service] = lambda: _StubMetricsService()
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 200
    assert "get_funnel_stats" in calls


def test_metrics_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import metrics as metrics_routes

    source = inspect.getsource(metrics_routes.metrics)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_metrics_route_renders_no_raw_jinja(db):
    """Jinja2 template is fully rendered — no unprocessed tags in the HTTP response."""
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        by_state={"applied": 5},
        score_distribution_by_state={"applied": {"q1": 0.5, "median": 0.6, "q3": 0.7, "n": 5}},
        unified_source_data={
            "greenhouse": {
                "jobs_seen": 5, "jobs_presented": 4, "presentation_rate": 0.8,
                "applied": 5, "responded": 2, "response_rate": 0.4,
                "interviewed": 1, "interview_rate": 0.2, "offers": 0,
            }
        },
        pipeline_velocity={
            "presented_to_selected": {"label": "Presented → Selected", "median_days": 2.0, "n": 4},
            "selected_to_applied": {"label": "Selected → Applied", "median_days": 1.0, "n": 4},
        },
        llm_grade_distribution={"A": {"count": 3, "pct": 0.6}},
        llm_grade_outcome_correlation={
            "A": {"total": 5, "terminal": 2, "advanced": 1, "advance_rate": 0.2, "qualifies": False},
        },
        stretch_conversion_rates={"qualified": {"total": 3, "applied_rate": 0.667, "screen_rate": 0.0}},
        stretch_response_rates={"qualified": {"applied": 2, "response_rate": 0.0, "interview_rate": 0.0}},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert "{%" not in resp.text
    assert "%}" not in resp.text
    assert "{{" not in resp.text
    assert "}}" not in resp.text


def test_metrics_route_has_no_mutation_paths():
    import inspect

    from job_search.dashboard.routes import metrics as metrics_routes

    source = inspect.getsource(metrics_routes.metrics)
    assert ".transition_job(" not in source
    assert ".resolve_followup(" not in source
    assert ".regenerate_documents(" not in source


def test_metrics_handles_service_failure_without_500(db):
    app = create_app()

    class _FailingMetricsService:
        def get_funnel_stats(self):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_metrics_service] = lambda: _FailingMetricsService()
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/dashboard/metrics")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Package 8 — Source Health ─────────────────────────────────────────────


from job_search.services.source_health import (  # noqa: E402
    GlobalHealthSummary,
    SourceHealthService,
    SourceHealthReport,
    SourceRunSummary,
)


def _insert_firm(db_path: str, firm_id: str, name: str = "Test Firm", **kwargs):
    defaults = dict(
        ats_tier="unknown",
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
           (firm_id, name, ats_tier, circuit_state, quarantine_until,
            consecutive_failures, last_successful_fetch, last_fingerprinted)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            firm_id, name,
            defaults["ats_tier"], defaults["circuit_state"],
            defaults["quarantine_until"], defaults["consecutive_failures"],
            defaults["last_successful_fetch"], defaults["last_fingerprinted"],
        ),
    )
    conn.commit()
    conn.close()


def _insert_source_run(db_path: str, source: str, firm_id=None, **kwargs):
    defaults = dict(
        run_at="2026-06-17T10:00:00",
        status="ok",
        records_fetched=None,
        error_class=None,
        error_detail=None,
    )
    defaults.update(kwargs)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO source_health
           (source, firm_id, run_at, status, records_fetched, error_class, error_detail)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            source, firm_id,
            defaults["run_at"], defaults["status"],
            defaults["records_fetched"], defaults["error_class"],
            defaults["error_detail"],
        ),
    )
    conn.commit()
    conn.close()


# Case 1: renders 200 with empty source_health table
def test_source_health_renders_200_with_empty_table(client, db):
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "Source Health" in resp.text


# Case 2: renders 200 with one healthy source
def test_source_health_renders_200_with_healthy_source(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok", records_fetched=10)
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "greenhouse" in resp.text
    assert "Acme Corp" in resp.text


# Case 3: renders 200 with one error source
def test_source_health_renders_200_with_error_source(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="error", error_class="transient")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "error" in resp.text
    assert "transient" in resp.text


# Case 4: renders 200 with mix of healthy/error sources
def test_source_health_renders_200_with_mixed_sources(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_firm(db, "f2", "Globex")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    _insert_source_run(db, "lever", firm_id="f2", status="error", error_class="persistent")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "greenhouse" in resp.text
    assert "lever" in resp.text
    assert "ok" in resp.text
    assert "error" in resp.text


# Case 5: open circuit_state on firm renders as quarantined (circuit_state drives it)
def test_source_health_open_circuit_renders_as_quarantined(client, db):
    _insert_firm(db, "f1", "Acme Corp", circuit_state="open",
                 quarantine_until="2099-01-01T00:00:00")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="quarantined-active"' in resp.text


# Case 6: expired quarantine renders as closed
def test_source_health_expired_quarantine_renders_as_closed(client, db):
    _insert_firm(db, "f1", "Acme Corp", circuit_state="open",
                 quarantine_until="2000-01-01T00:00:00")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="quarantine-expired"' in resp.text
    assert 'data-testid="quarantined-active"' not in resp.text


# Case 7: active quarantine renders with quarantine_until displayed
def test_source_health_active_quarantine_shows_quarantine_until(client, db):
    _insert_firm(db, "f1", "Acme Corp", circuit_state="open",
                 quarantine_until="2099-12-31T00:00:00")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "2099-12-31" in resp.text


# Case 8: global source (firm_id=NULL) renders without error, shows "Global"
def test_source_health_global_source_renders_as_global(client, db):
    _insert_source_run(db, "adzuna", firm_id=None, status="ok")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "Global" in resp.text


# Case 9: records_fetched=NULL renders as "—"
def test_source_health_null_records_fetched_renders_as_dash(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok", records_fetched=None)
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "—" in resp.text


# Case 10: empty source_health table shows "No runs recorded"
def test_source_health_empty_table_shows_no_runs_recorded(client, db):
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="no-runs-recorded"' in resp.text


# Case 11: route uses dependency override, not direct service construction
def test_source_health_uses_dependency_override_not_direct_construction(db):
    app = create_app()
    calls = []

    class _StubSourceHealthService:
        def get_report(self, status=None):
            calls.append("get_report")
            return SourceHealthReport(
                sources=[],
                global_summary=GlobalHealthSummary(
                    total_sources=0,
                    open_circuit_count=0,
                    recent_error_count=0,
                    last_successful_run=None,
                    all_healthy=True,
                ),
            )

        def list_distinct_statuses(self):
            return []

    app.dependency_overrides[get_source_health_service] = lambda: _StubSourceHealthService()
    with TestClient(app) as c:
        resp = c.get("/dashboard/source-health")

    assert resp.status_code == 200
    assert "get_report" in calls


# Case 12: SourceHealthService methods testable with real tmp_path SQLite
def test_source_health_service_testable_with_real_sqlite(db):
    _insert_firm(db, "f1", "Test Firm")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok", records_fetched=5)
    svc = SourceHealthService(db_path=db)
    report = svc.get_report()
    assert len(report.sources) == 1
    assert report.sources[0].source == "greenhouse"
    assert report.sources[0].records_fetched == 5


# Case 13: Source Health nav link is active (not "(not yet implemented)")
def test_source_health_nav_link_is_active(client, db):
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'href="/dashboard/source-health"' in resp.text
    assert "Source Health (not yet implemented)" not in resp.text


# Case 14: screen has no form / POST targets
def test_source_health_screen_has_no_forms(client, db):
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert "<form" not in resp.text


# Case 15: global health bar shows correct open-circuit count
def test_source_health_global_bar_open_circuit_count(db):
    _insert_firm(db, "f1", "Acme", circuit_state="open", quarantine_until="2099-01-01T00:00:00")
    _insert_firm(db, "f2", "Globex", circuit_state="closed")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    _insert_source_run(db, "lever", firm_id="f2", status="ok")
    svc = SourceHealthService(db_path=db)
    report = svc.get_report()
    assert report.global_summary.open_circuit_count == 1


# Case 16: global health bar shows correct 7-day error count
def test_source_health_global_bar_recent_error_count(db):
    _insert_firm(db, "f1", "Acme")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="error",
                       run_at="2026-06-16T10:00:00")
    _insert_source_run(db, "lever", firm_id=None, status="error",
                       run_at="2025-01-01T00:00:00")  # older than 7 days
    svc = SourceHealthService(db_path=db)
    report = svc.get_report()
    assert report.global_summary.recent_error_count == 1


# Case 17: "All sources healthy" when zero open circuits and zero recent errors
def test_source_health_global_bar_all_healthy_message(client, db):
    _insert_firm(db, "f1", "Acme", circuit_state="closed")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="all-sources-healthy"' in resp.text
    assert "All sources healthy" in resp.text


def test_source_health_route_does_not_query_sqlite_directly():
    import inspect
    from job_search.dashboard.routes import source_health as source_health_routes
    source = inspect.getsource(source_health_routes.source_health)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_source_health_handles_service_failure_without_500(db):
    app = create_app()

    class _FailingSourceHealthService:
        def get_report(self):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_source_health_service] = lambda: _FailingSourceHealthService()
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.get("/dashboard/source-health")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


# ── Phase 6 Package 1 — Analytics Expansion ──────────────────────────────


def test_metrics_shows_funnel_conversion_rates_when_data_present(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=10,
        by_state={"discovered": 10, "presented": 8, "selected": 4, "applied": 2},
        funnel_conversion_rates={
            "discovered": None,
            "presented": 0.8,
            "selected": 0.5,
            "applied": 0.5,
            "screen": None,
            "interview": None,
            "offer": None,
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="funnel-conversion"' in resp.text
    assert 'data-testid="funnel-conversion-table"' in resp.text
    assert 'data-testid="conversion-rate"' in resp.text
    assert "80.0%" in resp.text


def test_metrics_hides_funnel_conversion_section_when_empty(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, funnel_conversion_rates={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="funnel-conversion"' not in resp.text


def test_metrics_funnel_conversion_shows_dash_for_none_rate(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        by_state={"discovered": 3},
        funnel_conversion_rates={"discovered": None, "presented": None},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="funnel-conversion"' in resp.text
    assert "—" in resp.text


def test_metrics_funnel_conversion_shows_stage_and_count(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        by_state={"presented": 5, "selected": 3},
        funnel_conversion_rates={"discovered": None, "presented": None, "selected": 0.6},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="conversion-stage"' in resp.text
    assert 'data-testid="conversion-count"' in resp.text
    assert "selected" in resp.text
    assert "60.0%" in resp.text


def test_metrics_shows_llm_grade_distribution_when_grades_exist(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=4,
        llm_grade_distribution={
            "A": {"count": 2, "pct": 0.5},
            "B": {"count": 2, "pct": 0.5},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-grade-section"' in resp.text
    assert 'data-testid="llm-grade-table"' in resp.text
    assert 'data-testid="llm-grade-row"' in resp.text
    assert "50.0%" in resp.text


def test_metrics_hides_llm_grade_section_when_no_grades(db):
    app = create_app()
    stats = FunnelStats(total_jobs=5, llm_grade_distribution={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-grade-section"' not in resp.text


def test_metrics_llm_grade_shows_name_count_and_pct(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        llm_grade_distribution={"C": {"count": 3, "pct": 1.0}},
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-grade-name"' in resp.text
    assert 'data-testid="llm-grade-count"' in resp.text
    assert 'data-testid="llm-grade-pct"' in resp.text
    assert "100.0%" in resp.text


def test_metrics_shows_stretch_conversion_rates_when_data_present(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        stretch_conversion_rates={
            "qualified": {"total": 4, "applied_rate": 0.75, "screen_rate": 0.25},
            "stretch": {"total": 1, "applied_rate": 0.0, "screen_rate": 0.0},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="stretch-conversion"' in resp.text
    assert 'data-testid="stretch-conversion-table"' in resp.text
    assert 'data-testid="stretch-conversion-row"' in resp.text
    assert "qualified" in resp.text
    assert "75.0%" in resp.text


def test_metrics_hides_stretch_conversion_when_empty(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, stretch_conversion_rates={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="stretch-conversion"' not in resp.text


def test_metrics_stretch_conversion_shows_applied_and_screen_rates(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        stretch_conversion_rates={
            "long_shot": {"total": 3, "applied_rate": 0.333, "screen_rate": 0.0},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="stretch-applied-rate"' in resp.text
    assert 'data-testid="stretch-screen-rate"' in resp.text
    assert "long_shot" in resp.text


def test_metrics_shows_source_health_link_in_outcome_section(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        unified_source_data={
            "greenhouse": {
                "jobs_seen": 3, "jobs_presented": 2, "presentation_rate": 0.667,
                "applied": 1, "responded": 0, "response_rate": 0.0,
                "interviewed": 0, "interview_rate": 0.0, "offers": 0,
            }
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="nav-source-health-link"' in resp.text
    assert 'href="/dashboard/source-health"' in resp.text


def test_metrics_shows_tracker_and_review_queue_contextual_links(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        by_state={"applied": 5},
        funnel_conversion_rates={
            "discovered": None, "presented": None, "selected": None,
            "applied": None, "screen": None, "interview": None, "offer": None,
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="nav-tracker-link"' in resp.text
    assert 'href="/dashboard/tracker"' in resp.text
    assert 'data-testid="nav-review-queue-link"' in resp.text


# ── Phase 6 Package 2 — Analytics Depth ──────────────────────────────────

_UNIFIED_SOURCE = {
    "greenhouse": {
        "jobs_seen": 10, "jobs_presented": 8, "presentation_rate": 0.8,
        "applied": 5, "responded": 2, "response_rate": 0.4,
        "interviewed": 1, "interview_rate": 0.2, "offers": 0,
    }
}


def test_metrics_shows_score_distribution_when_data_present(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=4,
        score_distribution_by_state={
            "applied": {"q1": 0.35, "median": 0.5, "q3": 0.65, "n": 4},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="score-distribution"' in resp.text
    assert 'data-testid="score-distribution-table"' in resp.text
    assert 'data-testid="score-dist-row"' in resp.text
    assert "0.35" in resp.text
    assert "0.5" in resp.text


def test_metrics_hides_score_distribution_when_empty(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, score_distribution_by_state={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="score-distribution"' not in resp.text


def test_metrics_score_distribution_shows_q1_median_q3_n(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        score_distribution_by_state={
            "screen": {"q1": 0.6, "median": 0.75, "q3": 0.85, "n": 12},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="score-dist-q1"' in resp.text
    assert 'data-testid="score-dist-median"' in resp.text
    assert 'data-testid="score-dist-q3"' in resp.text
    assert 'data-testid="score-dist-n"' in resp.text
    assert "0.75" in resp.text


def test_metrics_shows_source_discovery_table_when_data_present(db):
    app = create_app()
    stats = FunnelStats(total_jobs=10, unified_source_data=_UNIFIED_SOURCE)
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="source-discovery"' in resp.text
    assert 'data-testid="source-discovery-table"' in resp.text
    assert 'data-testid="discovery-row"' in resp.text
    assert 'data-testid="discovery-source"' in resp.text
    assert "greenhouse" in resp.text
    assert "80.0%" in resp.text  # presentation_rate


def test_metrics_shows_source_outcome_table_when_data_present(db):
    app = create_app()
    stats = FunnelStats(total_jobs=10, unified_source_data=_UNIFIED_SOURCE)
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="source-outcome"' in resp.text
    assert 'data-testid="source-outcome-table"' in resp.text
    assert 'data-testid="outcome-row"' in resp.text
    assert 'data-testid="outcome-applied"' in resp.text
    assert 'data-testid="outcome-offers"' in resp.text
    assert "40.0%" in resp.text  # response_rate (n=5 >= 5)


def test_metrics_source_outcome_suppresses_rates_for_small_n(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=3,
        unified_source_data={
            "lever": {
                "jobs_seen": 3, "jobs_presented": 3, "presentation_rate": 1.0,
                "applied": 3, "responded": 1, "response_rate": 0.333,
                "interviewed": 0, "interview_rate": 0.0, "offers": 0,
            }
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="outcome-insufficient"' in resp.text
    assert "(n=3)" in resp.text
    assert 'data-testid="outcome-response-rate"' not in resp.text


def test_metrics_source_outcome_shows_rates_for_adequate_n(db):
    app = create_app()
    stats = FunnelStats(total_jobs=10, unified_source_data=_UNIFIED_SOURCE)
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="outcome-response-rate"' in resp.text
    assert 'data-testid="outcome-insufficient"' not in resp.text


def test_metrics_hides_source_tables_when_no_source_data(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, unified_source_data={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="source-discovery"' not in resp.text
    assert 'data-testid="source-outcome"' not in resp.text


def test_metrics_shows_pipeline_velocity_section(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        pipeline_velocity={
            "presented_to_selected": {"label": "Presented → Selected", "median_days": 2.0, "n": 4},
            "selected_to_applied": {"label": "Selected → Applied", "median_days": 1.5, "n": 6},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="pipeline-velocity"' in resp.text
    assert 'data-testid="velocity-list"' in resp.text
    assert 'data-testid="velocity-pair"' in resp.text
    assert "Presented → Selected" in resp.text
    assert "2.0 days" in resp.text


def test_metrics_pipeline_velocity_suppresses_for_small_n(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=2,
        pipeline_velocity={
            "presented_to_selected": {"label": "Presented → Selected", "median_days": None, "n": 1},
            "selected_to_applied": {"label": "Selected → Applied", "median_days": 2.0, "n": 4},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert "— (n=1)" in resp.text
    assert "2.0 days" in resp.text


def test_metrics_hides_pipeline_velocity_when_empty(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, pipeline_velocity={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="pipeline-velocity"' not in resp.text


def test_metrics_llm_correlation_shows_table_when_all_qualify(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=15,
        llm_grade_outcome_correlation={
            "A": {"total": 10, "terminal": 6, "advanced": 4, "advance_rate": 0.4, "qualifies": True},
            "B": {"total": 8, "terminal": 5, "advanced": 2, "advance_rate": 0.25, "qualifies": True},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-correlation"' in resp.text
    assert 'data-testid="llm-correlation-table"' in resp.text
    assert 'data-testid="llm-correlation-row"' in resp.text
    assert "40.0%" in resp.text
    assert 'data-testid="llm-correlation-scarcity"' not in resp.text


def test_metrics_llm_correlation_shows_scarcity_notice_when_not_qualified(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=5,
        llm_grade_outcome_correlation={
            "A": {"total": 5, "terminal": 2, "advanced": 1, "advance_rate": 0.2, "qualifies": False},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-correlation"' in resp.text
    assert 'data-testid="llm-correlation-scarcity"' in resp.text
    assert 'data-testid="llm-correlation-table"' not in resp.text
    assert "Insufficient outcome data" in resp.text


def test_metrics_llm_correlation_hides_when_no_data(db):
    app = create_app()
    stats = FunnelStats(total_jobs=0, llm_grade_outcome_correlation={})
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="llm-correlation"' not in resp.text


def test_metrics_stretch_shows_response_rate_columns(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=8,
        stretch_conversion_rates={
            "qualified": {"total": 8, "applied_rate": 0.625, "screen_rate": 0.125},
        },
        stretch_response_rates={
            "qualified": {"applied": 6, "response_rate": 0.333, "interview_rate": 0.167},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert 'data-testid="stretch-response-rate"' in resp.text
    assert 'data-testid="stretch-interview-rate"' in resp.text
    assert "33.3%" in resp.text
    assert "(n=6)" in resp.text


def test_metrics_stretch_response_suppresses_rates_for_small_n(db):
    app = create_app()
    stats = FunnelStats(
        total_jobs=4,
        stretch_conversion_rates={
            "long_shot": {"total": 4, "applied_rate": 0.5, "screen_rate": 0.0},
        },
        stretch_response_rates={
            "long_shot": {"applied": 2, "response_rate": 0.5, "interview_rate": 0.0},
        },
    )
    app.dependency_overrides[get_metrics_service] = _stub_metrics_service(stats)
    with TestClient(app) as client:
        resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    assert "— (n=2)" in resp.text


# ── Phase 6 Package 5 — Pipeline Runs Dashboard Screen ──────────────────


def test_pipeline_runs_renders_200_with_empty_table(client, db):
    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert "Pipeline Runs" in resp.text


def test_pipeline_runs_empty_table_shows_no_runs_recorded(client, db):
    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'data-testid="no-runs-recorded"' in resp.text


def test_pipeline_runs_renders_completed_run(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", source="greenhouse", trigger="cli")
    svc.update_counters(run_id, jobs_seen=120, jobs_created=8, jobs_updated=3, jobs_presented=4)
    svc.complete_run(run_id, metadata={"adapter": "greenhouse"}, notes="OK")

    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'data-testid="pipeline-run-row"' in resp.text
    assert "ingest" in resp.text
    assert "cli" in resp.text
    assert "greenhouse" in resp.text
    assert "complete" in resp.text
    assert "120" in resp.text
    assert "OK" in resp.text


def test_pipeline_runs_renders_failed_run_with_error_detail(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("grade", trigger="cli")
    svc.update_counters(run_id, jobs_seen=10, errors_count=10)
    svc.fail_run(run_id, error_detail="Batch API unavailable", metadata={"retries": 3})

    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert "failed" in resp.text
    assert "Batch API unavailable" in resp.text
    assert 'data-testid="run-errors-count"' in resp.text


def test_pipeline_runs_renders_running_run_with_dash_for_completed_at(client, db):
    svc = PipelineService(db)
    svc.start_run("full", trigger="manual")

    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert "running" in resp.text


def test_pipeline_runs_shows_metadata_summary_when_present(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("report", trigger="cli")
    svc.complete_run(run_id, metadata={"steps": {"report": {"presented": 4}}})

    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'data-testid="run-metadata"' in resp.text


def test_pipeline_runs_nav_link_is_active(client, db):
    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'href="/dashboard/pipeline-runs"' in resp.text
    assert "Pipeline Runs (not yet implemented)" not in resp.text


def test_pipeline_runs_screen_has_no_forms(client, db):
    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert "<form" not in resp.text


def test_pipeline_runs_uses_dependency_override_not_direct_construction(db):
    app = create_app()
    calls = []

    class _StubPipelineService:
        def list_recent_runs(self, status=None, run_type=None):
            calls.append("list_recent_runs")
            return []

        def list_distinct_statuses(self):
            return []

        def list_distinct_run_types(self):
            return []

    app.dependency_overrides[get_pipeline_service] = lambda: _StubPipelineService()
    with TestClient(app) as c:
        resp = c.get("/dashboard/pipeline-runs")

    assert resp.status_code == 200
    assert "list_recent_runs" in calls


def test_pipeline_runs_handles_service_failure_without_500(db):
    app = create_app()

    class _FailingPipelineService:
        def list_recent_runs(self):
            raise RuntimeError("simulated database outage")

    app.dependency_overrides[get_pipeline_service] = lambda: _FailingPipelineService()
    with TestClient(app, raise_server_exceptions=False) as c:
        resp = c.get("/dashboard/pipeline-runs")

    assert resp.status_code == 503
    assert "temporarily unavailable" in resp.text
    assert "Traceback" not in resp.text
    assert "RuntimeError" not in resp.text


def test_pipeline_runs_route_does_not_query_sqlite_directly():
    import inspect

    from job_search.dashboard.routes import pipeline_runs as pipeline_runs_routes
    source = inspect.getsource(pipeline_runs_routes.pipeline_runs)
    assert "get_db" not in source
    assert "sqlite3" not in source
    assert "SELECT" not in source


def test_pipeline_runs_route_has_exactly_one_dependency():
    import inspect

    from job_search.dashboard.routes import pipeline_runs as pipeline_runs_routes
    source = inspect.getsource(pipeline_runs_routes.pipeline_runs)
    assert source.count("Depends(") == 1


def test_pipeline_runs_route_has_no_mutation_routes():
    import inspect

    from job_search.dashboard.routes import pipeline_runs as pipeline_runs_routes
    source = inspect.getsource(pipeline_runs_routes)
    for verb in ("@router.post(", "@router.put(", "@router.patch(", "@router.delete("):
        assert verb not in source


# ── ANNA-P2-DASHBOARD-DIAGNOSTICS — Pipeline Runs status/run_type filters ──


def test_pipeline_runs_filters_by_status(client, db):
    svc = PipelineService(db)
    run_id_1 = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id_1)
    run_id_2 = svc.start_run("grade", trigger="cli")
    svc.fail_run(run_id_2, error_detail="boom")

    resp = client.get("/dashboard/pipeline-runs?status=failed")
    assert resp.status_code == 200
    assert 'data-testid="run-type">grade<' in resp.text
    assert 'data-testid="run-type">ingest<' not in resp.text


def test_pipeline_runs_filters_by_run_type(client, db):
    svc = PipelineService(db)
    svc.start_run("ingest", trigger="cli")
    svc.start_run("grade", trigger="cli")

    resp = client.get("/dashboard/pipeline-runs?run_type=grade")
    assert resp.status_code == 200
    assert 'data-testid="run-type">grade<' in resp.text
    assert 'data-testid="run-type">ingest<' not in resp.text


def test_pipeline_runs_filters_combine_status_and_run_type(client, db):
    svc = PipelineService(db)
    run_id_1 = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id_1)
    run_id_2 = svc.start_run("ingest", trigger="cli")
    svc.fail_run(run_id_2)
    run_id_3 = svc.start_run("grade", trigger="cli")
    svc.fail_run(run_id_3)

    resp = client.get("/dashboard/pipeline-runs?status=failed&run_type=ingest")
    assert resp.status_code == 200
    rows = resp.text.count('data-testid="pipeline-run-row"')
    assert rows == 1


def test_pipeline_runs_filter_nav_renders_distinct_values(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id)

    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'data-testid="pipeline-runs-filters"' in resp.text
    assert 'data-testid="status-filter-complete"' in resp.text
    assert 'data-testid="run-type-filter-ingest"' in resp.text


def test_pipeline_runs_no_filter_nav_when_no_runs(client, db):
    resp = client.get("/dashboard/pipeline-runs")
    assert resp.status_code == 200
    assert 'data-testid="pipeline-runs-filters"' not in resp.text


def test_pipeline_runs_empty_filtered_result_shows_filtered_message(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id)

    resp = client.get("/dashboard/pipeline-runs?status=failed")
    assert resp.status_code == 200
    assert 'data-testid="no-runs-recorded"' in resp.text
    assert "No pipeline runs match the selected filters" in resp.text


def test_pipeline_runs_clear_filters_link_present_when_filtered(client, db):
    svc = PipelineService(db)
    run_id = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id)

    resp = client.get("/dashboard/pipeline-runs?status=complete")
    assert resp.status_code == 200
    assert 'data-testid="clear-filters"' in resp.text
    assert 'href="/dashboard/pipeline-runs"' in resp.text


def test_pipeline_runs_service_filters_by_status_directly(db):
    svc = PipelineService(db)
    run_id_1 = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id_1)
    run_id_2 = svc.start_run("grade", trigger="cli")
    svc.fail_run(run_id_2)

    failed = svc.list_recent_runs(status="failed")
    assert [r.id for r in failed] == [run_id_2]


def test_pipeline_runs_service_list_distinct_statuses_and_run_types(db):
    svc = PipelineService(db)
    run_id_1 = svc.start_run("ingest", trigger="cli")
    svc.complete_run(run_id_1)
    run_id_2 = svc.start_run("grade", trigger="cli")
    svc.fail_run(run_id_2)

    assert svc.list_distinct_statuses() == ["complete", "failed"]
    assert svc.list_distinct_run_types() == ["grade", "ingest"]


# ── ANNA-P2-DASHBOARD-DIAGNOSTICS — Source Health status filter ───────────


def test_source_health_filters_by_status(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_firm(db, "f2", "Globex")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    _insert_source_run(db, "lever", firm_id="f2", status="error", error_class="transient")

    resp = client.get("/dashboard/source-health?status=error")
    assert resp.status_code == 200
    assert "lever" in resp.text
    assert "greenhouse" not in resp.text


def test_source_health_filter_does_not_change_global_summary(client, db):
    _insert_firm(db, "f1", "Acme Corp", circuit_state="open", quarantine_until="2099-01-01T00:00:00")
    _insert_firm(db, "f2", "Globex", circuit_state="closed")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="error")
    _insert_source_run(db, "lever", firm_id="f2", status="ok")

    resp = client.get("/dashboard/source-health?status=ok")
    assert resp.status_code == 200
    # Global summary still reflects the full, unfiltered dataset.
    assert '<span data-testid="total-sources">2</span>' in resp.text
    assert 'data-testid="open-circuit-count">Open circuits: 1' in resp.text


def test_source_health_filter_nav_renders_distinct_statuses(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")

    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="source-health-filters"' in resp.text
    assert 'data-testid="status-filter-ok"' in resp.text


def test_source_health_no_filter_nav_when_no_runs(client, db):
    resp = client.get("/dashboard/source-health")
    assert resp.status_code == 200
    assert 'data-testid="source-health-filters"' not in resp.text


def test_source_health_empty_filtered_result_shows_filtered_message(client, db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")

    resp = client.get("/dashboard/source-health?status=error")
    assert resp.status_code == 200
    assert 'data-testid="no-runs-recorded"' in resp.text
    assert "No sources match the selected status filter" in resp.text


def test_source_health_service_get_report_filters_by_status_directly(db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_firm(db, "f2", "Globex")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    _insert_source_run(db, "lever", firm_id="f2", status="error")

    svc = SourceHealthService(db_path=db)
    report = svc.get_report(status="error")
    assert [s.source for s in report.sources] == ["lever"]
    # Global summary unaffected by the filter.
    assert report.global_summary.total_sources == 2


def test_source_health_service_list_distinct_statuses(db):
    _insert_firm(db, "f1", "Acme Corp")
    _insert_source_run(db, "greenhouse", firm_id="f1", status="ok")
    _insert_source_run(db, "lever", firm_id="f1", status="error")

    svc = SourceHealthService(db_path=db)
    assert svc.list_distinct_statuses() == ["error", "ok"]


# ── ANNA-P2-DASHBOARD-DIAGNOSTICS — Review Queue search ────────────────────


def test_review_queue_search_filters_by_company(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_job(db, "j2", company="Globex Structural", title="Civil Engineer II", source="usajobs")
    _advance(db, "j1", "presented")
    _advance(db, "j2", "presented")

    resp = client.get("/dashboard/review-queue?q=Acme")
    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text
    assert "Globex Structural" not in resp.text


def test_review_queue_search_filters_by_title(client, db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_job(db, "j2", company="Globex Structural", title="Civil Engineer II")
    _advance(db, "j1", "presented")
    _advance(db, "j2", "presented")

    resp = client.get("/dashboard/review-queue?q=Civil")
    assert resp.status_code == 200
    assert "Civil Engineer II" in resp.text
    assert "Structural Engineer I" not in resp.text


def test_review_queue_search_is_case_insensitive(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue?q=acme")
    assert resp.status_code == 200
    assert "Acme Engineering" in resp.text


def test_review_queue_search_no_match_shows_empty_state(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented")

    resp = client.get("/dashboard/review-queue?q=NoSuchCompany")
    assert resp.status_code == 200
    assert "No jobs are currently presented for review." in resp.text


def test_review_queue_search_box_preserves_query_value(client, db):
    resp = client.get("/dashboard/review-queue?q=Acme")
    assert resp.status_code == 200
    assert 'value="Acme"' in resp.text
    assert 'data-testid="review-queue-active-search"' in resp.text


def test_review_queue_search_box_present_without_query(client, db):
    resp = client.get("/dashboard/review-queue")
    assert resp.status_code == 200
    assert 'data-testid="review-queue-search-form"' in resp.text
    assert 'data-testid="review-queue-active-search"' not in resp.text


def test_review_queue_clear_search_link_present_when_searching(client, db):
    resp = client.get("/dashboard/review-queue?q=Acme")
    assert resp.status_code == 200
    assert 'data-testid="review-queue-clear-search"' in resp.text


def test_jobs_service_list_jobs_search_matches_company_or_title(db):
    _insert_job(db, "j1", company="Acme Engineering", title="Structural Engineer I")
    _insert_job(db, "j2", company="Globex Structural", title="Civil Engineer II")

    svc = JobsService()
    results = svc.list_jobs(q="Acme")
    assert [j.canonical_job_id for j in results] == ["j1"]


def test_jobs_service_list_jobs_no_search_term_returns_all(db):
    _insert_job(db, "j1", company="Acme Engineering")
    _insert_job(db, "j2", company="Globex Structural")

    svc = JobsService()
    results = svc.list_jobs()
    assert {j.canonical_job_id for j in results} == {"j1", "j2"}


# ── ANNA-P2-DASHBOARD-DIAGNOSTICS — Tracker stage filter ───────────────────


def test_tracker_filters_by_stage(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _insert_job(db, "j2", company="Globex Structural")
    _advance(db, "j1", "presented", "selected")
    _advance(db, "j2", "presented", "selected", "applied")

    resp = client.get("/dashboard/tracker?state=applied")
    assert resp.status_code == 200
    assert "Globex Structural" in resp.text
    assert "Acme Engineering" not in resp.text


def test_tracker_stage_filter_ignores_invalid_state(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected")

    resp = client.get("/dashboard/tracker?state=not-a-real-state")
    assert resp.status_code == 200
    # Falls back to showing all tracked states rather than erroring.
    assert "Acme Engineering" in resp.text


def test_tracker_stage_filter_nav_renders_all_tracked_states(client, db):
    resp = client.get("/dashboard/tracker")
    assert resp.status_code == 200
    assert 'data-testid="tracker-state-filters"' in resp.text
    assert 'data-testid="tracker-state-filter-applied"' in resp.text
    assert 'data-testid="tracker-state-filter-all"' in resp.text


def test_tracker_stage_filter_empty_state_names_the_stage(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected")

    resp = client.get("/dashboard/tracker?state=offer")
    assert resp.status_code == 200
    assert 'data-testid="tracker-empty-state"' in resp.text
    assert 'No applications are currently in the "offer" stage.' in resp.text


def test_tracker_stage_filter_clear_link_present_when_filtered(client, db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected")

    resp = client.get("/dashboard/tracker?state=selected")
    assert resp.status_code == 200
    assert 'data-testid="tracker-clear-state-filter"' in resp.text


def test_tracker_stage_filter_does_not_affect_followups(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected", "applied")
    _insert_followup(db, "j1", "check_status", "2026-01-01")

    resp = client.get("/dashboard/tracker?state=offer")
    assert resp.status_code == 200
    # Job is filtered out of the tracker table (it's in 'applied', not 'offer'),
    # but its due follow-up still appears — filter only narrows the table.
    assert 'data-testid="followup-row"' in resp.text


def test_tracker_stage_filter_does_not_affect_upcoming_followups(client, db):
    _insert_job(db, "j1", company="Acme Engineering")
    _advance(db, "j1", "presented", "selected", "applied")
    upcoming = (date.today() + timedelta(days=3)).isoformat()
    _insert_followup(db, "j1", "check_status", upcoming)

    resp = client.get("/dashboard/tracker?state=offer")

    assert resp.status_code == 200
    assert 'data-testid="upcoming-followup-row"' in resp.text


def test_tracker_service_list_tracker_rows_with_single_state(db):
    _insert_job(db, "j1", company="Acme Engineering")
    _insert_job(db, "j2", company="Globex Structural")
    _advance(db, "j1", "presented", "selected")
    _advance(db, "j2", "presented", "selected", "applied")

    svc = TrackerService()
    rows = svc.list_tracker_rows(states=("applied",))
    assert [r.company for r in rows] == ["Globex Structural"]
