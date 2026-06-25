"""Build 1 Package 3 — generation intent-gate integration.

Covers the explicit confirmation gate in front of the existing
`DocumentsService.regenerate_documents()` boundary (itself a thin wrapper
around `SelectionProcessor.generate_for_selected()`), the
`material_generation_status` lifecycle, and the hard safety rules: no
navigation/selection path reaches generation, regeneration never marks a
job applied or moves it backward, and a failed generation call surfaces an
error without corrupting status.

All tests here use a fake `DocumentsService` — no real LLM or Drive call is
ever made by this test file.
"""

from __future__ import annotations

import inspect
import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.documents import DocumentRegenerationError, RegenerationResult
from job_search.services.generation_intent import (
    GenerationIntentError,
    GenerationIntentService,
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
        title="Structural Engineer",
        description_raw="Structural design role.",
        description_normalized="structural design",
        apply_url="https://example.invalid/jobs/1",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


class FakeDocumentsService:
    """Stands in for DocumentsService — never touches the real generator,
    LLM, or Drive."""

    def __init__(self, result: RegenerationResult | None = None, error: Exception | None = None):
        self.result = result
        self.error = error
        self.calls: list[str] = []

    def regenerate_documents(self, canonical_job_id: str, force: bool = True) -> RegenerationResult:
        self.calls.append(canonical_job_id)
        if self.error is not None:
            raise self.error
        return self.result


# ── Status lifecycle (no generation call) ────────────────────────────────────


def test_new_job_starts_not_started(db):
    _insert_job(db, "job-1")
    svc = GenerationIntentService(documents_service=FakeDocumentsService())

    state = svc.get_status("job-1")

    assert state.material_generation_status == "not_started"


def test_mark_base_selected_updates_status_without_calling_generation(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService()
    svc = GenerationIntentService(documents_service=fake_docs)

    state = svc.mark_base_selected("job-1")

    assert state.material_generation_status == "base_selected"
    assert fake_docs.calls == []


def test_mark_base_selected_does_not_regress_a_more_advanced_status(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService()
    svc = GenerationIntentService(documents_service=fake_docs)
    svc.request_confirmation("job-1")

    state = svc.mark_base_selected("job-1")

    assert state.material_generation_status == "confirmation_required"


def test_request_confirmation_updates_status_without_calling_generation(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService()
    svc = GenerationIntentService(documents_service=fake_docs)

    state = svc.request_confirmation("job-1")

    assert state.material_generation_status == "confirmation_required"
    assert fake_docs.calls == []


def test_request_confirmation_is_idempotent(db):
    _insert_job(db, "job-1")
    svc = GenerationIntentService(documents_service=FakeDocumentsService())

    svc.request_confirmation("job-1")
    state = svc.request_confirmation("job-1")

    assert state.material_generation_status == "confirmation_required"


def test_unknown_job_raises_for_all_methods(db):
    svc = GenerationIntentService(documents_service=FakeDocumentsService())
    with pytest.raises(GenerationIntentError):
        svc.request_confirmation("does-not-exist")
    with pytest.raises(GenerationIntentError):
        svc.mark_base_selected("does-not-exist")
    with pytest.raises(GenerationIntentError):
        svc.get_status("does-not-exist")
    with pytest.raises(GenerationIntentError):
        svc.confirm_generation("does-not-exist")


# ── confirm_generation() — the only method that calls generation ───────────


def test_confirm_generation_calls_documents_service_exactly_once(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService(
        result=RegenerationResult(
            canonical_job_id="job-1",
            resume_url="https://example.invalid/resume.docx",
            cover_url="https://example.invalid/cover.docx",
        )
    )
    svc = GenerationIntentService(documents_service=fake_docs)

    result = svc.confirm_generation("job-1")

    assert fake_docs.calls == ["job-1"]
    assert result.resume_url == "https://example.invalid/resume.docx"
    assert result.cover_url == "https://example.invalid/cover.docx"
    assert result.material_generation_status == "generated_draft_review_required"


def test_confirm_generation_sets_status_to_generated_draft_review_required(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService(
        result=RegenerationResult(canonical_job_id="job-1", resume_url="x", cover_url="y")
    )
    svc = GenerationIntentService(documents_service=fake_docs)

    svc.confirm_generation("job-1")
    state = svc.get_status("job-1")

    assert state.material_generation_status == "generated_draft_review_required"


def test_confirm_generation_failure_sets_failed_error_and_raises(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService(error=DocumentRegenerationError("boom"))
    svc = GenerationIntentService(documents_service=fake_docs)

    with pytest.raises(GenerationIntentError):
        svc.confirm_generation("job-1")

    state = svc.get_status("job-1")
    assert state.material_generation_status == "failed_error"


def test_confirm_generation_unexpected_failure_sets_failed_error_and_raises(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService(error=RuntimeError("profile setup exploded"))
    svc = GenerationIntentService(documents_service=fake_docs)

    with pytest.raises(GenerationIntentError) as excinfo:
        svc.confirm_generation("job-1")

    assert "Generation failed before drafts were created" in str(excinfo.value)
    state = svc.get_status("job-1")
    assert state.material_generation_status == "failed_error"


def test_confirm_generation_failure_does_not_corrupt_generated_docs_history(db):
    _insert_job(db, "job-1")
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url) VALUES ('job-1', 'resume', 'https://example.invalid/old.docx')"
    )
    conn.commit()
    conn.close()

    fake_docs = FakeDocumentsService(error=DocumentRegenerationError("boom"))
    svc = GenerationIntentService(documents_service=fake_docs)
    with pytest.raises(GenerationIntentError):
        svc.confirm_generation("job-1")

    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT COUNT(*) FROM generated_docs WHERE canonical_job_id = 'job-1'").fetchone()[0]
    conn.close()
    assert rows == 1  # untouched, not deleted or duplicated by the failure path


def test_confirm_generation_requires_at_least_one_doc_type(db):
    _insert_job(db, "job-1")
    svc = GenerationIntentService(documents_service=FakeDocumentsService())

    with pytest.raises(GenerationIntentError):
        svc.confirm_generation("job-1", generate_resume=False, generate_cover_letter=False)


def test_confirm_generation_never_marks_applied(db):
    _insert_job(db, "job-1")
    fake_docs = FakeDocumentsService(
        result=RegenerationResult(canonical_job_id="job-1", resume_url="x", cover_url="y")
    )
    svc = GenerationIntentService(documents_service=fake_docs)

    svc.confirm_generation("job-1")

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT app_state, application_status FROM jobs WHERE canonical_job_id = ?", ("job-1",)
    ).fetchone()
    conn.close()
    assert row["app_state"] == "discovered"
    assert row["application_status"] == "not_applied"


def test_confirm_generation_never_moves_app_state_backward_for_selected_job(db):
    _insert_job(db, "job-1")
    from job_search.tracking import advance_state

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    advance_state(conn, "job-1", "presented", note="test")
    advance_state(conn, "job-1", "selected", note="test")
    conn.commit()
    conn.close()

    fake_docs = FakeDocumentsService(
        result=RegenerationResult(canonical_job_id="job-1", resume_url="x", cover_url="y")
    )
    svc = GenerationIntentService(documents_service=fake_docs)
    svc.confirm_generation("job-1")

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT app_state FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    conn.close()
    assert row["app_state"] == "selected"  # unchanged — generation never transitions state


# ── Static safety checks ─────────────────────────────────────────────────────


def test_only_confirm_generation_calls_the_documents_service():
    """Static check: request_confirmation and mark_base_selected never
    reference `regenerate_documents` or `_documents_service` in their own
    source — only confirm_generation does."""
    from job_search.services.generation_intent import GenerationIntentService as Svc

    assert "regenerate_documents" not in inspect.getsource(Svc.request_confirmation)
    assert "regenerate_documents" not in inspect.getsource(Svc.mark_base_selected)
    assert "regenerate_documents" in inspect.getsource(Svc.confirm_generation)


def test_generation_intent_service_never_advances_state_machine():
    code_sources = "\n".join(
        inspect.getsource(method)
        for name, method in vars(GenerationIntentService).items()
        if callable(method) and not name.startswith("__")
    )
    assert "advance_state" not in code_sources


# ── API routes ────────────────────────────────────────────────────────────────


@pytest.fixture
def app_and_fake_docs(db, monkeypatch):
    fake_docs = FakeDocumentsService(
        result=RegenerationResult(
            canonical_job_id="job-1",
            resume_url="https://example.invalid/resume.docx",
            cover_url="https://example.invalid/cover.docx",
        )
    )

    from job_search.dashboard import deps as deps_module
    from job_search.services.generation_intent import GenerationIntentService as RealService

    app = create_app()
    app.dependency_overrides[deps_module.get_generation_intent_service] = (
        lambda: RealService(documents_service=fake_docs)
    )
    return app, fake_docs


def test_request_confirmation_route_never_calls_generation(app_and_fake_docs, db):
    app, fake_docs = app_and_fake_docs
    _insert_job(db, "job-1")
    with TestClient(app) as client:
        resp = client.post("/atlas/api/opportunities/job-1/generation/request-confirmation")

    assert resp.status_code == 200
    assert resp.json()["material_generation_status"] == "confirmation_required"
    assert fake_docs.calls == []


def test_confirm_generation_route_calls_generation_exactly_once(app_and_fake_docs, db):
    app, fake_docs = app_and_fake_docs
    _insert_job(db, "job-1")
    with TestClient(app) as client:
        resp = client.post("/atlas/api/opportunities/job-1/generation/confirm", json={})

    assert resp.status_code == 200
    body = resp.json()
    assert body["resume_url"] == "https://example.invalid/resume.docx"
    assert body["material_generation_status"] == "generated_draft_review_required"
    assert fake_docs.calls == ["job-1"]


def test_confirm_generation_route_404_for_unknown_job(app_and_fake_docs):
    app, _fake_docs = app_and_fake_docs
    with TestClient(app) as client:
        resp = client.post("/atlas/api/opportunities/does-not-exist/generation/confirm", json={})
    assert resp.status_code == 404


def test_confirm_generation_route_reports_missing_profile_and_sets_failed_error(db, monkeypatch):
    monkeypatch.setattr("job_search.config.settings.OPENAI_API_KEY", "present")
    monkeypatch.setattr("job_search.config.settings.PROFILE_PATH", "profile/missing-test-profile.yaml")
    _insert_job(db, "job-1")
    app = create_app()

    with TestClient(app) as client:
        resp = client.post("/atlas/api/opportunities/job-1/generation/confirm", json={})
        status_resp = client.get("/atlas/api/opportunities/job-1/generation/status")

    assert resp.status_code == 502
    assert "candidate profile is missing" in resp.json()["detail"]
    assert status_resp.json()["material_generation_status"] == "failed_error"


def test_get_generation_status_route(app_and_fake_docs, db):
    app, _fake_docs = app_and_fake_docs
    _insert_job(db, "job-1")
    with TestClient(app) as client:
        resp = client.get("/atlas/api/opportunities/job-1/generation/status")

    assert resp.status_code == 200
    assert resp.json()["material_generation_status"] == "not_started"


def test_opening_apply_url_or_workspace_link_never_calls_generation(app_and_fake_docs, db):
    """Hard safety assertion: GET/navigation-shaped endpoints never touch
    the generation boundary. We can't literally "click" a link in a test,
    but we can assert that the read-only opportunity-detail route and the
    pathway mutation routes never invoke FakeDocumentsService."""
    app, fake_docs = app_and_fake_docs
    _insert_job(db, "job-1")
    with TestClient(app) as client:
        client.get("/atlas/api/opportunities/job-1")
        client.post(
            "/atlas/api/opportunities/job-1/pathway/workspace-link",
            json={"workspace_url": "https://drive.google.com/folder/1"},
        )
        client.post(
            "/atlas/api/opportunities/job-1/base-resume-selection",
            json={"category_id": "structural_engineering", "selection_mode": "manual"},
        )

    assert fake_docs.calls == []
