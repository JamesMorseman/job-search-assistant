"""Build 0.5 application-workflow unlock regression coverage."""

from __future__ import annotations

import sqlite3
from types import SimpleNamespace
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.generation.generator import DocumentGenerator
from job_search.ingestion.dedup import Deduplicator
from job_search.ingestion.ingestor import Ingestor
from job_search.models import CanonicalJob
from job_search.reporting.selection import SelectionProcessor
from job_search.services.scoring_settings import ScoringSettingsService


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


def _insert_job(db_path: str, job_id: str = "job-1", **overrides):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    dedup = Deduplicator(conn)
    job_kwargs = dict(
        canonical_job_id=job_id,
        source="manual_url",
        source_job_id=job_id,
        company="Acme Engineering",
        title="Structural Engineer",
        description_raw="Structural design role.",
        description_normalized="structural design steel concrete bridge",
        apply_url="https://example.invalid/jobs/1",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


def test_use_base_resume_without_api_marks_status_and_creates_no_generated_docs(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    base_doc = tmp_path / "base-resume.docx"
    base_doc.write_text("placeholder", encoding="utf-8")
    monkeypatch.setattr(
        "job_search.services.base_resume_selection.DEFAULT_BASE_RESUME_ARTIFACT_PATH",
        base_doc,
    )
    _insert_job(db)

    select_resp = client.post(
        "/atlas/api/opportunities/job-1/base-resume-selection",
        json={"category_id": "structural_engineering", "selection_mode": "manual"},
    )
    assert select_resp.status_code == 200

    use_resp = client.post("/atlas/api/opportunities/job-1/generation/use-base-resume")

    assert use_resp.status_code == 200
    body = use_resp.json()
    assert body["material_generation_status"] == "using_base_resume"
    assert body["artifact"]["local_path"] == str(base_doc.resolve())

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT material_generation_status FROM jobs WHERE canonical_job_id = 'job-1'"
    ).fetchone()
    docs_count = conn.execute("SELECT COUNT(*) FROM generated_docs").fetchone()[0]
    conn.close()
    assert row["material_generation_status"] == "using_base_resume"
    assert docs_count == 0


def test_base_resume_artifact_can_be_registered_and_downloaded(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    artifact_map = tmp_path / "base_resume_artifacts.json"
    base_doc = tmp_path / "structural-base.docx"
    base_doc.write_text("fake resume artifact", encoding="utf-8")
    monkeypatch.setattr(
        "job_search.services.base_resume_selection.LOCAL_BASE_RESUME_ARTIFACT_MAP_PATH",
        artifact_map,
    )

    register_resp = client.post(
        "/atlas/api/base-resume-categories/structural_engineering/artifact",
        json={"local_path": str(base_doc)},
    )

    assert register_resp.status_code == 200
    body = register_resp.json()
    assert body["artifact_status"] == "local-only"
    assert body["artifact_path"] == str(base_doc.resolve())
    assert artifact_map.is_file()

    download_resp = client.get("/atlas/api/base-resume-categories/structural_engineering/artifact-file")
    assert download_resp.status_code == 200
    assert download_resp.content == b"fake resume artifact"


def test_use_base_resume_missing_artifact_returns_configuration_guidance(
    client,
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "job_search.services.base_resume_selection.DEFAULT_BASE_RESUME_ARTIFACT_PATH",
        tmp_path / "missing.docx",
    )
    _insert_job(db)

    client.post(
        "/atlas/api/opportunities/job-1/base-resume-selection",
        json={"category_id": "structural_engineering", "selection_mode": "manual"},
    )
    use_resp = client.post("/atlas/api/opportunities/job-1/generation/use-base-resume")

    assert use_resp.status_code == 400
    assert "Base resume file not configured" in use_resp.json()["detail"]


def test_manual_posting_route_stores_exact_url_and_scored_job(client, db):
    resp = client.post(
        "/atlas/api/manual-postings",
        json={
            "apply_url": "https://example.invalid/manual/structural",
            "company": "Manual Firm",
            "title": "Structural Engineer",
            "location_city": "Seattle",
            "location_state": "WA",
            "description": "Structural design role with steel and concrete.",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "manual_url"
    assert body["apply_url"] == "https://example.invalid/manual/structural"
    assert body["match_score"] is not None

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT source, apply_url, description_raw, match_score FROM jobs WHERE canonical_job_id = ?",
        (body["canonical_job_id"],),
    ).fetchone()
    conn.close()
    assert row["source"] == "manual_url"
    assert row["apply_url"] == "https://example.invalid/manual/structural"
    assert row["description_raw"] == "Structural design role with steel and concrete."
    assert row["match_score"] is not None


def test_recommendations_route_returns_safe_fallback_when_generator_fails(db, caplog):
    class BrokenRecommendationService:
        def generate(self, **_kwargs):
            raise RuntimeError("model unavailable for sk-testSECRET123")

    from job_search.dashboard import deps as deps_module

    app = create_app()
    app.dependency_overrides[deps_module.get_recommendation_service] = lambda: BrokenRecommendationService()
    with TestClient(app) as test_client:
        resp = test_client.get("/atlas/api/recommendations")

    assert resp.status_code == 200
    assert resp.json()["recommendations"] == []
    assert "sk-testSECRET123" not in caplog.text
    assert "sk-REDACTED" in caplog.text


def test_scoring_settings_save_and_reset_routes(db, tmp_path):
    from job_search.dashboard import deps as deps_module

    override_path = tmp_path / "atlas_scoring_override.json"
    app = create_app()
    app.dependency_overrides[deps_module.get_scoring_settings_service] = (
        lambda: ScoringSettingsService(override_path=override_path)
    )
    with TestClient(app) as test_client:
        save_resp = test_client.post(
            "/atlas/api/settings/scoring",
            json={
                "preset": "fit_first",
                "location_scheme": "fit_first",
                "discipline_weights": {"structural": 1.05},
                "penalties": {"active_security_clearance_required": 0.5},
                "profile_context_notes": "Prefer early-career structural roles.",
            },
        )
        assert save_resp.status_code == 200
        assert save_resp.json()["settings"]["active"] is True
        assert override_path.is_file()

        reset_resp = test_client.post("/atlas/api/settings/scoring/reset")
        assert reset_resp.status_code == 200
        assert reset_resp.json()["settings"]["active"] is False
        assert not override_path.exists()


def test_application_deadline_can_be_saved_read_and_cleared(client, db):
    _insert_job(db)

    save_resp = client.post(
        "/atlas/api/opportunities/job-1/pathway/deadline",
        json={"application_deadline": "2026-07-15"},
    )

    assert save_resp.status_code == 200
    assert save_resp.json()["application_deadline"] == "2026-07-15"
    detail_resp = client.get("/atlas/api/opportunities/job-1")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["application_deadline"] == "2026-07-15"

    clear_resp = client.post(
        "/atlas/api/opportunities/job-1/pathway/deadline",
        json={"application_deadline": None},
    )
    assert clear_resp.status_code == 200
    assert clear_resp.json()["application_deadline"] is None


def test_settings_context_notes_are_added_to_generation_profile_context(monkeypatch):
    class FakeSettingsService:
        def active_settings(self):
            return SimpleNamespace(
                active=True,
                profile_context_notes="Project Atlas is relevant for technical analyst roles.",
            )

    class SparseEvidenceSelector:
        def select(self, *_args, **_kwargs):
            return SimpleNamespace(has_rich_evidence=lambda: False)

    monkeypatch.setattr("job_search.generation.generator.ScoringSettingsService", FakeSettingsService)
    generator = DocumentGenerator(llm_provider=object())
    generator._profile = {"identity": {"first_name": "James"}}
    generator.evidence_selector = SparseEvidenceSelector()
    job = CanonicalJob(source="manual_url", source_job_id="1", company="Acme", title="Data Analyst")

    context, _packet, used_fallback = generator._build_profile_context(job, "SQL automation role", [])

    assert used_fallback is True
    assert context["local_profile_context_notes"]["content"].startswith("Project Atlas")
    assert context["full_profile_fallback"]["identity"]["first_name"] == "James"


def test_ingestion_stats_include_role_lane_breakdown():
    stats = {"query_lanes": {}}
    job = CanonicalJob(
        source="adzuna",
        source_job_id="1",
        company="Acme",
        title="Project Controls Analyst",
        description_normalized="Scheduling, cost control, SQL dashboards, and project controls.",
    )

    Ingestor._record_query_lane(stats, job)

    assert stats["query_lanes"]["project_controls"] == 1
    assert stats["query_lanes"]["technical_analyst_data_systems"] == 1


def test_document_upload_writes_durable_local_paths(tmp_path, monkeypatch):
    class FakeGenerator:
        def generate(self, _job):
            raise AssertionError("not used")

        def save_docx(self, _payload, path):
            Path(path).write_text("resume", encoding="utf-8")

        def save_cover_docx(self, _payload, path, *, job, today):
            Path(path).write_text(f"cover {job.title} {today}", encoding="utf-8")

    class FakeSheets:
        def upload_document(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(
        "job_search.reporting.selection.GENERATED_APPLICATION_MATERIALS_DIR",
        tmp_path / "materials",
    )
    processor = SelectionProcessor()
    processor._generator = FakeGenerator()
    processor.sheets = FakeSheets()
    job_row = {
        "canonical_job_id": "job-1",
        "source": "manual_url",
        "source_job_id": "job-1",
        "firm_id": None,
        "company": "Acme Engineering",
        "title": "Structural Engineer",
        "location_city": "Seattle",
        "location_state": "WA",
        "description_normalized": "structural design",
        "description_raw": "structural design",
        "apply_url": "https://example.invalid/jobs/1",
        "ats_type": "unknown",
    }

    resume_url, cover_url, resume_path, cover_path = processor._upload_docs(
        job_row,
        {
            "resume_json": {},
            "cover_letter_json": {},
            "keyword_coverage": 0.5,
            "keywords_hit": [],
            "keywords_missed": [],
        },
        today="2026-06-25",
    )

    assert resume_url is None
    assert cover_url is None
    assert Path(resume_path).is_file()
    assert Path(cover_path).is_file()
    assert str(tmp_path / "materials") in resume_path
