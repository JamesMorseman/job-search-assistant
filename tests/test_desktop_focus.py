"""ATLAS Desktop Package 9 + 10 Focus API and Command Center tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_focus_resolution_service, get_focus_service
from job_search.db.connection import init_db
from job_search.ingestion.dedup import Deduplicator
from job_search.models import CanonicalJob
from job_search.services.focus import AtlasFocus
from job_search.services.focus_resolution import FocusResolutionService
from job_search.services.pipeline import PipelineService

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
COMMAND_CENTER_TSX = (
    FRONTEND_SRC / "workspaces" / "CommandCenter.tsx"
).read_text(encoding="utf-8")
COMMAND_CENTER_CSS = (
    FRONTEND_SRC / "workspaces" / "commandCenter.css"
).read_text(encoding="utf-8")
CLIENT_TS = (FRONTEND_SRC / "api" / "client.ts").read_text(encoding="utf-8")
TYPES_TS = (FRONTEND_SRC / "api" / "types.ts").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
PIPELINE_TSX = (FRONTEND_SRC / "workspaces" / "Pipeline.tsx").read_text(encoding="utf-8")
ASK_ATLAS_TSX = (FRONTEND_SRC / "workspaces" / "AskAtlas.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_SURFACE_TSX = (
    FRONTEND_SRC / "workspaces" / "OpportunityDetailSurface.tsx"
).read_text(encoding="utf-8")
ATLAS_API_PY = (ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py").read_text(
    encoding="utf-8"
)
DEPS_PY = (ROOT / "job_search" / "dashboard" / "deps.py").read_text(encoding="utf-8")
SCHEMA_SQL = (ROOT / "job_search" / "db" / "schema.sql").read_text(encoding="utf-8")


class FakeFocusService:
    def __init__(self):
        self.calls = []

    def list_active_focuses(self, *, summary, opportunities, most_recent_run, due_followups=None):
        self.calls.append((summary, opportunities, most_recent_run, due_followups))
        return [
            AtlasFocus(
                focus_statement="Review new Radar intake",
                reason="Two new opportunities appeared in the latest run.",
                source_object="pipeline-run:9",
                attention_horizon="today",
                next_action="Open Radar and compare the newest opportunity signals.",
                resolution_state="active",
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


def test_focuses_endpoint_returns_read_only_focus_shape(client, app, db):
    fake = FakeFocusService()
    app.dependency_overrides[get_focus_service] = lambda: fake
    _insert_job(db, "job-1", app_state="discovered")
    pipeline = PipelineService(db_path=db)
    run_id = pipeline.start_run("ingest", trigger="manual")
    pipeline.update_counters(run_id, jobs_created=2)
    pipeline.complete_run(run_id)

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["focuses", "generated_at"]
    assert body["focuses"] == [
        {
            "focus_statement": "Review new Radar intake",
            "reason": "Two new opportunities appeared in the latest run.",
            "source_object": "pipeline-run:9",
            "attention_horizon": "today",
            "next_action": "Open Radar and compare the newest opportunity signals.",
            "resolution_state": "active",
        }
    ]
    assert "T" in body["generated_at"]
    summary, opportunities, most_recent_run, due_followups = fake.calls[0]
    assert summary.total_opportunities == 1
    assert opportunities.limit == 3
    assert most_recent_run.id == run_id
    assert due_followups == []


def test_focuses_endpoint_allows_empty_focuses(client, app):
    class EmptyFocusService:
        def list_active_focuses(self, *, summary, opportunities, most_recent_run, due_followups=None):
            return []

    app.dependency_overrides[get_focus_service] = lambda: EmptyFocusService()

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    assert resp.json()["focuses"] == []


def test_resolve_focus_persists_and_returns_archived_record(client, app, db):
    payload = {
        "source_object": "pipeline-run:9",
        "focus_statement": "Review new Radar intake",
        "resolution": "completed",
        "note": "Reviewed the new intake during morning standup.",
    }

    resp = client.post("/atlas/api/focuses/resolutions", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["source_object"] == "pipeline-run:9"
    assert body["resolution"] == "completed"
    assert body["note"] == payload["note"]
    assert isinstance(body["id"], int)
    assert "T" in body["resolved_at"]


def test_resolved_focus_is_excluded_from_active_focus_list(client, app, db):
    fake = FakeFocusService()
    app.dependency_overrides[get_focus_service] = lambda: fake

    client.post(
        "/atlas/api/focuses/resolutions",
        json={
            "source_object": "pipeline-run:9",
            "focus_statement": "Review new Radar intake",
            "resolution": "dismissed",
        },
    )

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    assert resp.json()["focuses"] == []


def test_focuses_endpoint_surfaces_real_due_followup_end_to_end(client, db):
    """Build 1: a real followup_queue row (no fake FocusService override)
    must surface through the live /atlas/api/focuses endpoint as a Focus.
    """
    import sqlite3

    _insert_job(db, "job-1", company="Acme Engineering", title="Civil Engineer I")
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
        ("job-1", "check_status", "2026-01-01"),
    )
    conn.commit()
    conn.close()

    resp = client.get("/atlas/api/focuses")

    assert resp.status_code == 200
    body = resp.json()
    followup_focuses = [f for f in body["focuses"] if f["source_object"].startswith("followup:")]
    assert len(followup_focuses) == 1
    assert "Acme Engineering" in followup_focuses[0]["focus_statement"]
    assert followup_focuses[0]["resolution_state"] == "active"


def test_focuses_endpoint_does_not_surface_resolved_or_future_followups(client, db):
    import sqlite3

    _insert_job(db, "job-1")
    _insert_job(db, "job-2")
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO followup_queue (canonical_job_id, action_type, due_date, resolved) "
        "VALUES (?, ?, ?, 1)",
        ("job-1", "check_status", "2026-01-01"),
    )
    conn.execute(
        "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
        ("job-2", "check_status", "2099-01-01"),
    )
    conn.commit()
    conn.close()

    resp = client.get("/atlas/api/focuses")

    body = resp.json()
    followup_focuses = [f for f in body["focuses"] if f["source_object"].startswith("followup:")]
    assert followup_focuses == []


def test_focus_archive_endpoint_lists_resolutions_newest_first(client, app, db):
    service = FocusResolutionService(db_path=db)
    service.record_resolution(
        source_object="opportunity:job-1",
        focus_statement="Review current opportunity mix",
        resolution="expired",
    )
    service.record_resolution(
        source_object="pipeline-run:9",
        focus_statement="Review new Radar intake",
        resolution="completed",
    )

    resp = client.get("/atlas/api/focuses/archive")

    assert resp.status_code == 200
    body = resp.json()
    assert list(body) == ["resolutions", "limit"]
    assert [r["source_object"] for r in body["resolutions"]] == [
        "pipeline-run:9",
        "opportunity:job-1",
    ]


def test_focus_resolution_service_is_sole_write_path_for_focus_resolutions():
    import inspect

    import job_search.services.focus_resolution as focus_resolution_module

    source = inspect.getsource(focus_resolution_module)
    assert "INSERT INTO focus_resolutions" in source
    for forbidden in ["DELETE FROM focus_resolutions", "DROP TABLE"]:
        assert forbidden not in source


def test_focuses_endpoint_is_get_only_and_uses_existing_read_boundaries():
    assert '@router.get("/focuses"' in ATLAS_API_PY
    assert "atlas_service.get_summary()" in ATLAS_API_PY
    assert "atlas_service.list_opportunities(limit=3)" in ATLAS_API_PY
    assert "pipeline_service.list_recent_runs(limit=1)" in ATLAS_API_PY
    assert "focus_service.list_active_focuses" in ATLAS_API_PY
    assert "get_focus_service" in DEPS_PY
    assert "FocusService()" in DEPS_PY
    for verb in ['@router.put(', '@router.patch(', '@router.delete(']:
        assert verb not in ATLAS_API_PY


def test_focus_resolution_endpoint_is_the_only_authorized_mutation_route():
    """Package 10's definition entry authorizes read/write `/atlas/api`
    endpoints for the bounded Focus lifecycle only. `/focuses/resolutions`
    must be the sole POST route in the ATLAS API; every other surface
    (opportunities, summary, pipeline, recommendations, ask-atlas) remains
    GET-only.
    """
    post_routes = [
        line.strip()
        for line in ATLAS_API_PY.splitlines()
        if line.strip().startswith('@router.post(')
    ]
    assert post_routes == ['@router.post("/focuses/resolutions", response_model=FocusResolutionRecord)']
    assert '@router.get("/focuses/archive"' in ATLAS_API_PY
    assert "get_focus_resolution_service" in DEPS_PY
    assert "FocusResolutionService()" in DEPS_PY


def test_frontend_client_and_types_define_focus_boundary():
    assert "export function getFocuses" in CLIENT_TS
    assert '"/focuses"' in CLIENT_TS
    assert "AtlasFocus" in TYPES_TS
    assert "AtlasFocusListResponse" in TYPES_TS
    for field in [
        "focus_statement",
        "reason",
        "source_object",
        "attention_horizon",
        "next_action",
        "resolution_state",
    ]:
        assert field in TYPES_TS


def test_frontend_client_and_types_define_focus_resolution_boundary():
    assert "export function resolveFocus" in CLIENT_TS
    assert "export function getFocusArchive" in CLIENT_TS
    assert '"/focuses/resolutions"' in CLIENT_TS
    assert "/focuses/archive" in CLIENT_TS
    for symbol in [
        "FocusResolutionAction",
        "FocusResolutionRequest",
        "FocusResolutionRecord",
        "AtlasFocusArchiveResponse",
    ]:
        assert symbol in TYPES_TS
    for value in ["completed", "deferred", "dismissed", "superseded", "expired"]:
        assert f'"{value}"' in TYPES_TS


def test_command_center_renders_focus_list_and_states():
    assert "getFocuses" in COMMAND_CENTER_TSX
    assert "focusState" in COMMAND_CENTER_TSX
    assert "Atlas Focus" in COMMAND_CENTER_TSX
    for field in [
        "focus.focus_statement",
        "focus.reason",
        "focus.source_object",
        "focus.attention_horizon",
        "focus.next_action",
        "focus.resolution_state",
    ]:
        assert field in COMMAND_CENTER_TSX
    assert "Loading Atlas Focus" in COMMAND_CENTER_TSX
    assert "Unable to load Atlas Focus" in COMMAND_CENTER_TSX
    assert "No active Focus objects right now" in COMMAND_CENTER_TSX
    assert ".atlas-cc-focus-card" in COMMAND_CENTER_CSS


def test_command_center_renders_focus_history_and_states():
    assert "getFocusArchive" in COMMAND_CENTER_TSX
    assert "focusArchiveState" in COMMAND_CENTER_TSX
    assert "Focus History" in COMMAND_CENTER_TSX
    for field in [
        "record.focus_statement",
        "record.source_object",
        "record.resolved_at",
        "record.note",
        "resolutionLabel(record.resolution)",
    ]:
        assert field in COMMAND_CENTER_TSX
    assert "Loading Focus history" in COMMAND_CENTER_TSX
    assert "Unable to load Focus history" in COMMAND_CENTER_TSX
    assert "No Focus objects have been resolved yet" in COMMAND_CENTER_TSX
    assert ".atlas-cc-focus-archive-card" in COMMAND_CENTER_CSS


def test_command_center_has_no_focus_mutation_controls_or_task_management():
    prohibited_terms = [
        "Complete Focus",
        "Defer Focus",
        "Dismiss Focus",
        "Archive Focus",
        "delete",
        "notification",
        "reminder",
        "calendar",
        "task",
        "onClick",
        "<button",
        "<form",
        "select_job",
        "reject_job",
        "mark_applied",
    ]
    combined = COMMAND_CENTER_TSX + COMMAND_CENTER_CSS
    for term in prohibited_terms:
        assert term not in combined, f"prohibited Focus behavior found: {term}"


def test_focus_resolution_persistence_is_isolated_to_archive_service():
    """Package 9 prohibited Focus schema/persistence; Package 10's definition
    entry (`DECISION_LOG.md`, "ATLAS Desktop Package 10 - Atlas Focus
    Resolution & Archive MVP Definition Accepted") explicitly authorizes the
    minimal local persistence needed to preserve Focus history. The read-only
    derivation module (`job_search/services/focus.py`) must remain free of
    SQL and mutation verbs; only `FocusResolutionService` may write
    `focus_resolutions`.
    """
    import inspect

    import job_search.services.focus as focus_module

    focus_source = inspect.getsource(focus_module)
    assert "SELECT " not in focus_source
    assert "INSERT " not in focus_source
    assert "UPDATE " not in focus_source
    assert "DELETE " not in focus_source

    assert "focus_resolutions" in SCHEMA_SQL.lower()


def test_no_workspace_file_calls_fetch_directly():
    offenders = []
    for path in (FRONTEND_SRC / "workspaces").glob("*.tsx"):
        source = path.read_text(encoding="utf-8")
        if "fetch(" in source:
            offenders.append(path.name)
    assert offenders == []


def test_unrelated_closed_surfaces_untouched_by_focus_work():
    for source in [RADAR_TSX, PIPELINE_TSX, ASK_ATLAS_TSX, OPPORTUNITY_DETAIL_SURFACE_TSX]:
        assert "getFocuses" not in source
        assert "AtlasFocus" not in source
        assert "FocusService" not in source


def test_dashboard_routes_remain_unaffected_by_package_9(client):
    resp = client.get("/dashboard/review-queue")

    assert resp.status_code == 200
    assert "Review Queue" in resp.text


def test_atlas_api_unknown_route_remains_json_404(client):
    resp = client.get("/atlas/api/not-a-route")

    assert resp.status_code == 404
    assert resp.headers["content-type"].startswith("application/json")


def test_atlas_command_center_path_is_served_by_spa_not_api(client):
    resp = client.get("/atlas/command-center")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
