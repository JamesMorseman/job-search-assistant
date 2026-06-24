"""Build 1 Package 2 — base resume library / selector.

Covers: the metadata-only category registry (cap of 10, required
general_strongest_overall category, coursework-optional flag), the
deterministic recommender (grounded in the existing role-family classifier,
never an LLM call), manual-selection-required-when-unreachable behavior, the
append-only selection history table/service, the new API routes, and the
hard safety rule for this package: selection/recommendation never triggers
document generation and never mutates the profile or app_state.
"""

from __future__ import annotations

import inspect
import sqlite3

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db
from job_search.evidence import base_resume_library
from job_search.evidence.base_resume_library import (
    APPROVED_BASE_RESUME_CATEGORIES,
    DEFERRED_BASE_RESUME_CATEGORIES,
    category_for_role_family,
    get_category,
    is_deferred_category,
    list_categories,
)
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.base_resume_selection import (
    BaseResumeSelectionError,
    BaseResumeSelectionService,
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
        title="Structural Engineer",
        description_raw="Structural design role.",
        description_normalized="structural design steel concrete bridge",
        apply_url="https://example.invalid/jobs/1",
    )
    job_kwargs.update(overrides)
    dedup.upsert(CanonicalJob(**job_kwargs))
    conn.commit()
    conn.close()


# ── Category registry ────────────────────────────────────────────────────────


def test_category_count_is_at_most_ten():
    assert len(APPROVED_BASE_RESUME_CATEGORIES) <= 10


def test_general_strongest_overall_is_present_and_required():
    category = get_category("general_strongest_overall")
    assert category is not None
    assert category.coursework_optional is True


def test_only_general_strongest_overall_has_coursework_optional():
    optional = [c.category_id for c in APPROVED_BASE_RESUME_CATEGORIES if c.coursework_optional]
    assert optional == ["general_strongest_overall"]


def test_every_category_has_required_metadata_fields():
    for category in APPROVED_BASE_RESUME_CATEGORIES:
        assert category.category_id
        assert category.label
        assert len(category.role_families) >= 1
        assert len(category.selection_cues) >= 1
        assert len(category.excluded_cues) >= 1
        assert category.rationale
        assert category.document_ref


def test_no_category_id_overlaps_deferred_categories():
    approved_ids = {c.category_id for c in APPROVED_BASE_RESUME_CATEGORIES}
    assert approved_ids.isdisjoint(DEFERRED_BASE_RESUME_CATEGORIES)


def test_deferred_categories_are_marked_deferred_not_approved():
    for deferred_id in DEFERRED_BASE_RESUME_CATEGORIES:
        assert is_deferred_category(deferred_id)
        assert get_category(deferred_id) is None


def test_category_for_role_family_maps_known_families():
    assert category_for_role_family("structural").category_id == "structural_engineering"
    assert category_for_role_family("water_resources").category_id == "water_resources_stormwater"
    assert category_for_role_family("construction_management").category_id == "construction_project_engineering"
    assert category_for_role_family("field_engineering").category_id == "construction_project_engineering"
    assert category_for_role_family("public_sector").category_id == "public_sector_civil"


def test_category_for_role_family_falls_back_to_general_for_unknown_or_deferred_families():
    assert category_for_role_family("general_civil").category_id == "general_strongest_overall"
    assert category_for_role_family("transportation").category_id == "general_strongest_overall"
    assert category_for_role_family("totally_unknown_family").category_id == "general_strongest_overall"


def test_list_categories_returns_all_approved_categories():
    assert {c.category_id for c in list_categories()} == {
        c.category_id for c in APPROVED_BASE_RESUME_CATEGORIES
    }


def test_no_real_resume_content_in_category_registry():
    """Privacy boundary: document_ref values must be safe placeholder
    references, never a real Drive URL or filesystem path to private content."""
    source = inspect.getsource(base_resume_library)
    assert "drive.google.com" not in source
    assert "docs.google.com" not in source
    assert "profile/james_profile" not in source
    for category in APPROVED_BASE_RESUME_CATEGORIES:
        assert category.document_ref.startswith("base_resume_library/")
        assert category.document_ref.endswith(".reference")


# ── BaseResumeSelectionService.recommend() ───────────────────────────────────


def test_recommend_uses_deterministic_classifier_not_llm():
    """Static safety check: recommend() never imports/calls an LLM provider."""
    source = inspect.getsource(BaseResumeSelectionService.recommend)
    assert "llm" not in source.lower()
    assert "openai" not in source.lower()
    assert "DocumentGenerator" not in source


def test_recommend_for_unreachable_posting_requires_manual_fallback():
    svc = BaseResumeSelectionService()
    recommendation = svc.recommend(job=None, jd=None, posting_reachable=False)

    assert recommendation.posting_reachable is False
    assert recommendation.category_id == "general_strongest_overall"
    assert recommendation.confidence == 0.0


def test_recommend_for_structural_posting():
    svc = BaseResumeSelectionService()
    job = CanonicalJob(source="test", source_job_id="1", company="Acme", title="Structural Engineer")
    recommendation = svc.recommend(
        job=job,
        jd="structural design steel concrete bridge framing",
        posting_reachable=True,
    )

    assert recommendation.category_id == "structural_engineering"
    assert recommendation.posting_reachable is True
    assert recommendation.confidence > 0


def test_recommend_for_ambiguous_posting_falls_back_to_general():
    svc = BaseResumeSelectionService()
    job = CanonicalJob(source="test", source_job_id="1", company="Acme", title="Engineer")
    recommendation = svc.recommend(job=job, jd="general engineering tasks", posting_reachable=True)

    assert recommendation.category_id == "general_strongest_overall"


# ── BaseResumeSelectionService.record_selection() (the one write path) ──────


def test_record_selection_persists_append_only_row(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    record = svc.record_selection(
        canonical_job_id="job-1",
        category_id="structural_engineering",
        selection_mode="recommended",
        selected_by_user=True,
        confidence=0.8,
        reason="Matched structural role family.",
    )

    assert record.category_id == "structural_engineering"
    assert record.selection_mode == "recommended"
    assert record.selected_by_user is True

    latest = svc.get_latest_selection("job-1")
    assert latest is not None
    assert latest.id == record.id


def test_record_selection_rejects_deferred_category(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    with pytest.raises(BaseResumeSelectionError):
        svc.record_selection(
            canonical_job_id="job-1",
            category_id="transportation_traffic",
            selection_mode="manual",
            selected_by_user=True,
        )


def test_record_selection_rejects_unknown_category(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    with pytest.raises(BaseResumeSelectionError):
        svc.record_selection(
            canonical_job_id="job-1",
            category_id="not_a_real_category",
            selection_mode="manual",
            selected_by_user=True,
        )


def test_record_selection_rejects_unknown_job(db):
    svc = BaseResumeSelectionService()
    with pytest.raises(BaseResumeSelectionError):
        svc.record_selection(
            canonical_job_id="does-not-exist",
            category_id="general_strongest_overall",
            selection_mode="manual",
            selected_by_user=True,
        )


def test_record_selection_history_is_append_only_and_latest_is_deterministic(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    svc.record_selection(
        canonical_job_id="job-1",
        category_id="structural_engineering",
        selection_mode="recommended",
        selected_by_user=True,
    )
    second = svc.record_selection(
        canonical_job_id="job-1",
        category_id="general_strongest_overall",
        selection_mode="manual",
        selected_by_user=True,
    )

    history = svc.list_selection_history("job-1")
    assert len(history) == 2
    latest = svc.get_latest_selection("job-1")
    assert latest is not None
    assert latest.id == second.id
    assert latest.category_id == "general_strongest_overall"


def test_selection_service_never_calls_generation_or_state_machine():
    code_sources = "\n".join(
        inspect.getsource(method)
        for name, method in vars(BaseResumeSelectionService).items()
        if callable(method) and not name.startswith("__")
    )
    assert "DocumentGenerator" not in code_sources
    assert "generate_for_selected" not in code_sources
    assert "advance_state" not in code_sources
    assert "SelectionProcessor" not in code_sources


def test_selecting_a_base_resume_never_creates_generated_docs_rows(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    svc.record_selection(
        canonical_job_id="job-1",
        category_id="structural_engineering",
        selection_mode="manual",
        selected_by_user=True,
    )

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM generated_docs").fetchone()[0]
    conn.close()
    assert count == 0


def test_selecting_a_base_resume_never_changes_app_state(db):
    _insert_job(db, "job-1")
    svc = BaseResumeSelectionService()

    svc.record_selection(
        canonical_job_id="job-1",
        category_id="structural_engineering",
        selection_mode="manual",
        selected_by_user=True,
    )

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT app_state, material_generation_status FROM jobs WHERE canonical_job_id = ?", ("job-1",)).fetchone()
    conn.close()
    assert row["app_state"] == "discovered"
    assert row["material_generation_status"] == "not_started"


# ── API routes ────────────────────────────────────────────────────────────────


def test_list_base_resume_categories_route(client):
    resp = client.get("/atlas/api/base-resume-categories")

    assert resp.status_code == 200
    body = resp.json()
    category_ids = {c["category_id"] for c in body["categories"]}
    assert "general_strongest_overall" in category_ids
    assert len(body["categories"]) <= 10


def test_get_recommendation_route_for_reachable_posting(client, db):
    _insert_job(db, "job-1")

    resp = client.get("/atlas/api/opportunities/job-1/base-resume-recommendation")

    assert resp.status_code == 200
    body = resp.json()
    assert body["posting_reachable"] is True
    assert body["category_id"] == "structural_engineering"


def test_get_recommendation_route_for_unreachable_posting(client, db):
    _insert_job(db, "job-1", apply_url=None, description_normalized=None, description_raw=None)

    resp = client.get("/atlas/api/opportunities/job-1/base-resume-recommendation")

    assert resp.status_code == 200
    body = resp.json()
    assert body["posting_reachable"] is False
    assert body["category_id"] == "general_strongest_overall"


def test_get_recommendation_route_404_for_unknown_job(client):
    resp = client.get("/atlas/api/opportunities/does-not-exist/base-resume-recommendation")
    assert resp.status_code == 404


def test_record_selection_route_persists_and_is_readable(client, db):
    _insert_job(db, "job-1")

    resp = client.post(
        "/atlas/api/opportunities/job-1/base-resume-selection",
        json={"category_id": "structural_engineering", "selection_mode": "manual"},
    )
    assert resp.status_code == 200
    assert resp.json()["category_id"] == "structural_engineering"

    get_resp = client.get("/atlas/api/opportunities/job-1/base-resume-selection")
    assert get_resp.status_code == 200
    assert get_resp.json()["category_id"] == "structural_engineering"


def test_get_selection_route_404_when_none_recorded(client, db):
    _insert_job(db, "job-1")

    resp = client.get("/atlas/api/opportunities/job-1/base-resume-selection")
    assert resp.status_code == 404


def test_record_selection_route_rejects_deferred_category(client, db):
    _insert_job(db, "job-1")

    resp = client.post(
        "/atlas/api/opportunities/job-1/base-resume-selection",
        json={"category_id": "geotechnical", "selection_mode": "manual"},
    )
    assert resp.status_code == 400


def test_record_selection_route_404_for_unknown_job(client):
    resp = client.post(
        "/atlas/api/opportunities/does-not-exist/base-resume-selection",
        json={"category_id": "general_strongest_overall", "selection_mode": "manual"},
    )
    assert resp.status_code == 404


def test_selection_routes_never_create_generated_docs_rows(client, db):
    _insert_job(db, "job-1")

    client.post(
        "/atlas/api/opportunities/job-1/base-resume-selection",
        json={"category_id": "structural_engineering", "selection_mode": "manual"},
    )

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM generated_docs").fetchone()[0]
    conn.close()
    assert count == 0
