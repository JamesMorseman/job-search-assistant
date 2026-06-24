"""Build 1 Package 1 — application pathway data/UI links.

Covers the navigation-only pathway metadata added to `jobs`
(workspace_url/provider/label, application_status, pathway_updated_at,
material_generation_status), the ApplicationPathwayService write boundary,
and the new ATLAS API routes. Asserts the hard safety rule for this package:
none of these mutations call document generation, and AtlasDataService
remains read-only.
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
from job_search.services import atlas as atlas_service
from job_search.services.pathway import (
    ApplicationPathwayError,
    ApplicationPathwayService,
)


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
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


# ── Schema / model defaults ──────────────────────────────────────────────────


def test_new_jobs_default_to_safe_pathway_state(db):
    _insert_job(db, "job-1")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    conn.close()

    assert row["workspace_url"] is None
    assert row["workspace_provider"] is None
    assert row["workspace_label"] is None
    assert row["application_status"] == "not_applied"
    assert row["pathway_updated_at"] is None
    assert row["material_generation_status"] == "not_started"


def test_canonical_job_model_round_trips_pathway_fields():
    job = CanonicalJob(
        source="test",
        source_job_id="job-1",
        company="Acme",
        title="Engineer",
        workspace_url="https://drive.google.com/folder/abc",
        workspace_provider="google_drive",
        workspace_label="My Folder",
        application_status="applied",
        pathway_updated_at="2026-06-24T10:00:00",
        material_generation_status="generated_draft_review_required",
    )
    d = job.to_db_dict()
    assert d["workspace_url"] == "https://drive.google.com/folder/abc"
    assert d["workspace_provider"] == "google_drive"
    assert d["application_status"] == "applied"
    assert d["material_generation_status"] == "generated_draft_review_required"


# ── ApplicationPathwayService ────────────────────────────────────────────────


def test_set_workspace_link_writes_only_pathway_fields(db):
    _insert_job(db, "job-1")
    svc = ApplicationPathwayService()
    monkeypatch_path = db

    state = svc.set_workspace_link(
        "job-1",
        workspace_url="https://drive.google.com/folder/xyz",
        workspace_provider="google_drive",
        workspace_label="Acme Application",
    )

    assert state.workspace_url == "https://drive.google.com/folder/xyz"
    assert state.workspace_provider == "google_drive"
    assert state.workspace_label == "Acme Application"
    assert state.application_status == "not_applied"
    assert state.pathway_updated_at is not None

    conn = sqlite3.connect(monkeypatch_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    conn.close()
    # app_state and material_generation_status must be untouched by this action.
    assert row["app_state"] == "discovered"
    assert row["material_generation_status"] == "not_started"


def test_set_workspace_link_rejects_blank_url(db):
    _insert_job(db, "job-1")
    svc = ApplicationPathwayService()

    with pytest.raises(ApplicationPathwayError):
        svc.set_workspace_link("job-1", workspace_url="   ")


def test_set_workspace_link_rejects_unknown_job(db):
    svc = ApplicationPathwayService()

    with pytest.raises(ApplicationPathwayError):
        svc.set_workspace_link("does-not-exist", workspace_url="https://example.invalid")


def test_mark_applied_only_changes_application_status(db):
    _insert_job(db, "job-1")
    svc = ApplicationPathwayService()

    state = svc.mark_applied("job-1")

    assert state.application_status == "applied"
    assert state.pathway_updated_at is not None

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    conn.close()
    # app_state (the tracker state machine) is untouched by this action.
    assert row["app_state"] == "discovered"


def test_mark_applied_rejects_unknown_job(db):
    svc = ApplicationPathwayService()
    with pytest.raises(ApplicationPathwayError):
        svc.mark_applied("does-not-exist")


def test_pathway_service_never_calls_generation_or_state_machine():
    """Static safety check: ApplicationPathwayService never imports or calls
    anything from the generation or state-machine boundaries. Checked against
    actual code (function bodies), not the module docstring, since the
    docstring explains the boundary using those same terms in prose."""
    from job_search.services.pathway import ApplicationPathwayService

    code_sources = "\n".join(
        inspect.getsource(method)
        for name, method in vars(ApplicationPathwayService).items()
        if callable(method) and not name.startswith("__")
    )
    assert "DocumentGenerator" not in code_sources
    assert "generate_for_selected" not in code_sources
    assert "advance_state" not in code_sources
    assert "SelectionProcessor" not in code_sources
    assert "import" not in code_sources or "from job_search.tracking" not in code_sources


# ── AtlasDataService stays read-only ─────────────────────────────────────────


def test_atlas_service_still_has_no_write_sql():
    """Re-assert the pre-existing read-only boundary after Package 1 changes
    (AtlasDataService gained generated_materials via a read-only helper
    import; it must still never write)."""
    source = inspect.getsource(atlas_service)
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source


def test_get_opportunity_surfaces_pathway_fields_and_generated_materials(db):
    _insert_job(db, "job-1")
    conn = sqlite3.connect(db)
    conn.execute(
        """
        UPDATE jobs
        SET workspace_url = ?, workspace_provider = ?, workspace_label = ?,
            application_status = 'applied', pathway_updated_at = ?,
            material_generation_status = 'generated_draft_review_required'
        WHERE canonical_job_id = ?
        """,
        ("https://drive.google.com/x", "google_drive", "Folder", "2026-06-24T09:00:00", "job-1"),
    )
    conn.execute(
        """
        INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at)
        VALUES ('job-1', 'resume', 'https://drive.google.com/resume.docx', '2026-06-24 09:05:00')
        """
    )
    conn.commit()
    conn.close()

    svc = atlas_service.AtlasDataService()
    detail = svc.get_opportunity("job-1")

    assert detail.workspace_url == "https://drive.google.com/x"
    assert detail.application_status == "applied"
    assert detail.material_generation_status == "generated_draft_review_required"
    assert len(detail.generated_materials) == 1
    assert detail.generated_materials[0].doc_type == "resume"
    assert detail.generated_materials[0].drive_url == "https://drive.google.com/resume.docx"


def test_get_opportunity_defaults_pathway_fields_when_absent(db):
    _insert_job(db, "job-1")

    svc = atlas_service.AtlasDataService()
    detail = svc.get_opportunity("job-1")

    assert detail.workspace_url is None
    assert detail.application_status == "not_applied"
    assert detail.material_generation_status == "not_started"
    assert detail.generated_materials == []


# ── API routes ────────────────────────────────────────────────────────────────


def test_set_workspace_link_route_persists_and_returns_state(client, db):
    _insert_job(db, "job-1")

    resp = client.post(
        "/atlas/api/opportunities/job-1/pathway/workspace-link",
        json={"workspace_url": "https://drive.google.com/folder/1", "workspace_label": "Folder"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["workspace_url"] == "https://drive.google.com/folder/1"
    assert body["workspace_label"] == "Folder"
    assert body["application_status"] == "not_applied"

    detail_resp = client.get("/atlas/api/opportunities/job-1")
    assert detail_resp.json()["workspace_url"] == "https://drive.google.com/folder/1"


def test_set_workspace_link_route_404_for_unknown_job(client):
    resp = client.post(
        "/atlas/api/opportunities/does-not-exist/pathway/workspace-link",
        json={"workspace_url": "https://drive.google.com/folder/1"},
    )
    assert resp.status_code == 404


def test_set_workspace_link_route_rejects_blank_url(client, db):
    _insert_job(db, "job-1")

    resp = client.post(
        "/atlas/api/opportunities/job-1/pathway/workspace-link",
        json={"workspace_url": "   "},
    )
    assert resp.status_code == 400


def test_mark_applied_route_persists_and_returns_state(client, db):
    _insert_job(db, "job-1")

    resp = client.post("/atlas/api/opportunities/job-1/pathway/mark-applied")

    assert resp.status_code == 200
    body = resp.json()
    assert body["application_status"] == "applied"
    assert body["pathway_updated_at"] is not None

    detail_resp = client.get("/atlas/api/opportunities/job-1")
    assert detail_resp.json()["application_status"] == "applied"


def test_mark_applied_route_404_for_unknown_job(client):
    resp = client.post("/atlas/api/opportunities/does-not-exist/pathway/mark-applied")
    assert resp.status_code == 404


def test_pathway_routes_never_create_generated_docs_rows(client, db):
    """Hard safety assertion: navigation-only pathway actions never insert
    into generated_docs (no generation side effect from these endpoints)."""
    _insert_job(db, "job-1")

    client.post(
        "/atlas/api/opportunities/job-1/pathway/workspace-link",
        json={"workspace_url": "https://drive.google.com/folder/1"},
    )
    client.post("/atlas/api/opportunities/job-1/pathway/mark-applied")

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM generated_docs").fetchone()[0]
    conn.close()
    assert count == 0
