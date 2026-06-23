"""Tests for the Phase 4 dashboard service layer (Packages 1, 2b, and 3b).

Read services must: read SQLite directly, agree with existing CLI/reporting
behavior, and never mutate application state on their own.
`TrackerService.transition_job()` / `resolve_followup()` (Package 3b) and
`DocumentsService.regenerate_documents()` (Package 2b) are the only
state-mutating service functions, and must not be more permissive than (or
duplicate the logic of) the existing infrastructure they wrap.
"""

from __future__ import annotations

import sqlite3

import pytest

from job_search.db.connection import get_db, init_db
from job_search.firms.repository import _upsert_firm
from job_search.ingestion.dedup import Deduplicator
from job_search.models import (
    CanonicalJob,
    FirmApproval,
    FirmBenefit,
    FirmBenefitStatus,
    FirmPriority,
    FirmProfile,
    FirmProfileMeta,
)
from job_search.reporting.documents import list_generated_docs
from job_search.reporting.funnel import FunnelReporter
from job_search.reporting.selection import SelectionProcessor
from job_search.services.documents import (
    DocumentRegenerationError,
    DocumentsService,
)
from job_search.services.firms import FirmsService
from job_search.services.jobs import JobsService
from job_search.services.metrics import MetricsService
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


# ── JobsService ───────────────────────────────────────────────────────────


def test_list_jobs_returns_all_by_default(db):
    _insert_job(db, "j1")
    _insert_job(db, "j2", source="usajobs", match_score=0.5)

    items = JobsService().list_jobs()
    assert {i.canonical_job_id for i in items} == {"j1", "j2"}


def test_list_jobs_filters_by_state_and_source(db):
    _insert_job(db, "j1")
    _insert_job(db, "j2", source="usajobs")
    _advance(db, "j1", "presented")

    presented = JobsService().list_jobs(app_state="presented")
    assert [i.canonical_job_id for i in presented] == ["j1"]

    usajobs_only = JobsService().list_jobs(source="usajobs")
    assert [i.canonical_job_id for i in usajobs_only] == ["j2"]


def test_list_jobs_respects_limit_and_offset(db):
    _insert_job(db, "j1", match_score=0.9)
    _insert_job(db, "j2", match_score=0.7)
    _insert_job(db, "j3", match_score=0.5)

    page1 = JobsService().list_jobs(limit=2, offset=0)
    page2 = JobsService().list_jobs(limit=2, offset=2)
    assert [i.canonical_job_id for i in page1] == ["j1", "j2"]
    assert [i.canonical_job_id for i in page2] == ["j3"]


def test_get_job_detail_returns_none_for_missing_job(db):
    assert JobsService().get_job_detail("nope") is None


def test_get_job_detail_parses_json_fields(db):
    _insert_job(db, "j1")
    with get_db() as conn:
        conn.execute(
            "UPDATE jobs SET benefit_reasons = ?, trajectory_reasons = ?, discipline_tags = ? "
            "WHERE canonical_job_id = ?",
            ('[{"key": "tuition_reimbursement", "label": "Tuition Reimbursement"}]', "[]", '["structural"]', "j1"),
        )

    detail = JobsService().get_job_detail("j1")
    assert detail is not None
    assert detail.benefit_reasons[0]["key"] == "tuition_reimbursement"
    assert detail.discipline_tags == ["structural"]


# ── DocumentsService ──────────────────────────────────────────────────────


def test_documents_service_current_and_history(db):
    _insert_job(db, "j1")
    with get_db() as conn:
        conn.execute(
            "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at) "
            "VALUES ('j1', 'resume', 'https://drive/old', '2026-01-01T00:00:00')"
        )
        conn.execute(
            "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at) "
            "VALUES ('j1', 'resume', 'https://drive/new', '2026-02-01T00:00:00')"
        )

    svc = DocumentsService()
    history = svc.list_documents("j1", doc_type="resume")
    assert [d.drive_url for d in history] == ["https://drive/new", "https://drive/old"]

    current = svc.get_current_documents("j1")
    assert current["resume"].drive_url == "https://drive/new"
    assert current["cover_letter"] is None


def test_documents_service_returns_empty_history_for_unknown_job(db):
    assert DocumentsService().list_documents("nope") == []


# ── DocumentsService.regenerate_documents (Package 2b) ───────────────────


class _FakeGenerator:
    """Stands in for DocumentGenerator — no LLM calls, no audit machinery.

    Deliberately omits `prepare_resume_for_rendering` and `_profile` so
    SelectionProcessor._upload_docs()/_audit_rendered_docs() take their
    skip branches, exactly as tests/test_selection.py does.
    """

    def save_docx(self, resume_json, output_path):
        from pathlib import Path
        Path(output_path).write_bytes(b"resume")

    def save_cover_docx(self, cover_json, output_path, job=None, today=None):
        from pathlib import Path
        Path(output_path).write_bytes(b"cover")

    def generate(self, job):
        return {
            "resume_json": {"professional_summary": "Summary."},
            "cover_letter_json": {
                "salutation": "Dear Hiring Manager,",
                "body_paragraphs": ["Paragraph one.", "Paragraph two."],
                "closing": "Sincerely,\nJames Morseman",
            },
            "keyword_coverage": 0.75,
            "keywords_hit": ["structural design"],
            "keywords_missed": ["seismic"],
        }


class _FailingGenerator(_FakeGenerator):
    def generate(self, job):
        raise RuntimeError("simulated generation failure")


class _FakeSheets:
    def __init__(self):
        self.uploaded = []
        self.doc_links = []

    def upload_document(self, local_path, filename, folder_id=None):
        self.uploaded.append((local_path, filename, folder_id))
        return f"https://example.invalid/{filename}"

    def update_doc_links(self, job_id, resume_url, cover_url):
        self.doc_links.append((job_id, resume_url, cover_url))


def _processor_with_fake_generator(generator_cls=_FakeGenerator) -> SelectionProcessor:
    proc = SelectionProcessor()
    proc.sheets = _FakeSheets()
    proc._generator = generator_cls()
    return proc


def test_regenerate_documents_success_path(db):
    _insert_job(db, "j1", source="test")
    _advance(db, "j1", "presented", "selected")

    svc = DocumentsService(processor=_processor_with_fake_generator())
    result = svc.regenerate_documents("j1")

    assert result.canonical_job_id == "j1"
    assert result.resume_url.endswith("_resume.docx")
    assert result.cover_url.endswith("_cover.docx")


def test_regenerate_documents_preserves_existing_history(db):
    _insert_job(db, "j1", source="test")
    _advance(db, "j1", "presented", "selected")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at) "
            "VALUES ('j1', 'resume', 'https://drive/old', '2026-01-01T00:00:00')"
        )

    svc = DocumentsService(processor=_processor_with_fake_generator())
    svc.regenerate_documents("j1")

    with get_db() as conn:
        history = list_generated_docs(conn, "j1", doc_type="resume")

    # Old row preserved, new row appended — never overwritten or deleted.
    assert len(history) == 2
    assert {row["drive_url"] for row in history} >= {"https://drive/old"}


def test_regenerate_documents_current_resolution_reflects_new_doc(db):
    _insert_job(db, "j1", source="test")
    _advance(db, "j1", "presented", "selected")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO generated_docs (canonical_job_id, doc_type, drive_url, generated_at) "
            "VALUES ('j1', 'resume', 'https://drive/old', '2026-01-01T00:00:00')"
        )

    svc = DocumentsService(processor=_processor_with_fake_generator())
    result = svc.regenerate_documents("j1")

    current = svc.get_current_documents("j1")
    assert current["resume"].drive_url == result.resume_url
    assert current["resume"].drive_url != "https://drive/old"


def test_regenerate_documents_works_for_already_selected_job(db):
    """Regeneration must not be blocked by the known jsa-apply idempotency
    gap: it does not call advance_state() at all, so a job already past
    'selected' (e.g. 'applied') regenerates without any transition attempt."""
    _insert_job(db, "j1", source="test")
    _advance(db, "j1", "presented", "selected", "applied")

    svc = DocumentsService(processor=_processor_with_fake_generator())
    result = svc.regenerate_documents("j1")

    assert result.canonical_job_id == "j1"
    assert JobsService().get_job_detail("j1").app_state == "applied"  # unchanged


def test_regenerate_documents_raises_for_unknown_job(db):
    svc = DocumentsService(processor=_processor_with_fake_generator())
    with pytest.raises(DocumentRegenerationError):
        svc.regenerate_documents("does-not-exist")


def test_regenerate_documents_raises_on_generation_failure(db):
    _insert_job(db, "j1", source="test")
    _advance(db, "j1", "presented", "selected")

    svc = DocumentsService(processor=_processor_with_fake_generator(_FailingGenerator))
    with pytest.raises(DocumentRegenerationError):
        svc.regenerate_documents("j1")


# ── TrackerService ────────────────────────────────────────────────────────


def test_tracker_rows_reflect_latest_transition(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    rows = TrackerService().list_tracker_rows()
    assert len(rows) == 1
    assert rows[0].canonical_job_id == "j1"
    assert rows[0].app_state == "applied"
    assert rows[0].last_transitioned_at is not None


def test_tracker_rows_excludes_untracked_states_by_default(db):
    _insert_job(db, "j1")  # stays at 'discovered'
    rows = TrackerService().list_tracker_rows()
    assert rows == []


def test_state_history_orders_oldest_first(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected")

    history = TrackerService().get_state_history("j1")
    assert [h.to_state for h in history] == ["presented", "selected"]


def test_list_due_followups_does_not_mutate_state(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    before = JobsService().get_job_detail("j1").app_state
    TrackerService().list_due_followups(as_of="2099-01-01")
    after = JobsService().get_job_detail("j1").app_state

    assert before == after == "applied"


def test_list_due_followups_returns_scheduled_item(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    due = TrackerService().list_due_followups(as_of="2099-01-01")
    assert len(due) == 1
    assert due[0].canonical_job_id == "j1"
    assert due[0].resolved is False


# ── TrackerService actions (Package 3b) ──────────────────────────────────


def test_list_upcoming_followups_returns_next_seven_days_only(db):
    _insert_job(db, "j1")
    _insert_job(db, "j2")
    _insert_job(db, "j3")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
            ("j1", "check_status", "2026-06-24"),
        )
        conn.execute(
            "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
            ("j2", "check_status", "2026-06-23"),
        )
        conn.execute(
            "INSERT INTO followup_queue (canonical_job_id, action_type, due_date) VALUES (?, ?, ?)",
            ("j3", "check_status", "2026-07-01"),
        )

    upcoming = TrackerService().list_upcoming_followups(as_of="2026-06-23")

    assert [item.canonical_job_id for item in upcoming] == ["j1"]


def test_list_upcoming_followups_excludes_resolved_items(db):
    _insert_job(db, "j1")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO followup_queue (canonical_job_id, action_type, due_date, resolved) "
            "VALUES (?, ?, ?, 1)",
            ("j1", "check_status", "2026-06-24"),
        )

    assert TrackerService().list_upcoming_followups(as_of="2026-06-23") == []


def test_list_upcoming_followups_does_not_mutate_state(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    before = JobsService().get_job_detail("j1").app_state
    TrackerService().list_upcoming_followups(as_of="2026-06-23")
    after = JobsService().get_job_detail("j1").app_state

    assert before == after == "applied"


def test_transition_job_valid_transition_succeeds(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented")

    ok = TrackerService().transition_job("j1", "selected", note="James flagged for application")
    assert ok is True

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "selected"


def test_transition_job_invalid_transition_rejected(db):
    _insert_job(db, "j1")
    # 'discovered' -> 'interview' is not a valid transition.
    ok = TrackerService().transition_job("j1", "interview")
    assert ok is False

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "discovered"


def test_transition_job_unknown_job_returns_false(db):
    ok = TrackerService().transition_job("does-not-exist", "presented")
    assert ok is False


def test_transition_job_preserves_transition_history(db):
    _insert_job(db, "j1")

    svc = TrackerService()
    svc.transition_job("j1", "presented", note="auto-presented")
    svc.transition_job("j1", "selected", note="James flagged for application")

    history = svc.get_state_history("j1")
    assert [h.to_state for h in history] == ["presented", "selected"]
    assert history[0].note == "auto-presented"
    assert history[1].from_state == "presented"
    assert history[1].note == "James flagged for application"


def test_transition_job_state_machine_enforcement_matches_advance_state(db):
    """The service must not be more permissive than advance_state() itself —
    same invalid transition rejected by both, with no transition recorded."""
    _insert_job(db, "j1")

    direct_db = sqlite3.connect(db)
    direct_db.row_factory = sqlite3.Row
    direct_ok = advance_state(direct_db, "j1", "offer")  # discovered -> offer: invalid
    direct_db.commit()
    direct_db.close()

    _insert_job(db, "j2")
    service_ok = TrackerService().transition_job("j2", "offer")

    assert direct_ok is False
    assert service_ok is False
    assert TrackerService().get_state_history("j1") == []
    assert TrackerService().get_state_history("j2") == []


def test_resolve_followup_marks_item_resolved(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")

    due_before = TrackerService().list_due_followups(as_of="2099-01-01")
    assert len(due_before) == 1
    followup_id = due_before[0].id

    TrackerService().resolve_followup(followup_id)

    due_after = TrackerService().list_due_followups(as_of="2099-01-01")
    assert due_after == []

    all_items = TrackerService().list_due_followups(as_of="2099-01-01", include_resolved=True)
    assert len(all_items) == 1
    assert all_items[0].resolved is True


def test_resolve_followup_does_not_alter_job_state(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    followup_id = TrackerService().list_due_followups(as_of="2099-01-01")[0].id

    TrackerService().resolve_followup(followup_id)

    detail = JobsService().get_job_detail("j1")
    assert detail.app_state == "applied"


# ── FirmsService (Package 6) ─────────────────────────────────────────────


def _insert_firm(db_path: str, firm_id: str, **overrides) -> FirmProfile:
    defaults = dict(
        firm_id=firm_id,
        name="Acme Engineering",
        profile=FirmProfileMeta(enr_rank=42, employee_count="201-1000", disciplines=["structural"]),
        benefits={
            "tuition_reimbursement": FirmBenefit(status=FirmBenefitStatus.CONFIRMED, confidence=0.9),
        },
        manual_priority=FirmPriority.TARGET,
        approval=FirmApproval(approved_at="2026-06-01", approved_by="james", last_verified="2026-06-01"),
    )
    defaults.update(overrides)
    profile = FirmProfile(**defaults)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _upsert_firm(conn, profile)
    conn.commit()
    conn.close()
    return profile


def test_get_firm_returns_detail_for_known_firm(db):
    _insert_firm(db, "acme")

    detail = FirmsService().get_firm("acme")
    assert detail is not None
    assert detail.name == "Acme Engineering"
    assert detail.enr_rank == 42
    assert detail.disciplines == ["structural"]
    assert detail.benefits["tuition_reimbursement"]["status"] == "confirmed"
    assert detail.manual_priority == "target"


def test_get_firm_returns_none_for_missing_firm(db):
    assert FirmsService().get_firm("does-not-exist") is None


def test_get_firm_status_reflects_ats_health_columns(db):
    _insert_firm(db, "acme")
    with get_db() as conn:
        conn.execute(
            "UPDATE firms SET circuit_state = 'open', consecutive_failures = 3, "
            "quarantine_until = '2026-07-01T00:00:00' WHERE firm_id = 'acme'"
        )

    status = FirmsService().get_firm_status("acme")
    assert status is not None
    assert status.circuit_state == "open"
    assert status.consecutive_failures == 3
    assert status.quarantine_until == "2026-07-01T00:00:00"


def test_get_firm_status_returns_none_for_missing_firm(db):
    assert FirmsService().get_firm_status("does-not-exist") is None


def test_get_firm_priority_returns_manual_priority_value(db):
    _insert_firm(db, "acme", manual_priority=FirmPriority.WATCH)
    assert FirmsService().get_firm_priority("acme") == "watch"


def test_get_firm_priority_returns_none_for_missing_firm(db):
    assert FirmsService().get_firm_priority("does-not-exist") is None


def test_get_firm_metadata_returns_profile_fields(db):
    _insert_firm(db, "acme")

    meta = FirmsService().get_firm_metadata("acme")
    assert meta is not None
    assert meta.enr_rank == 42
    assert meta.employee_count == "201-1000"
    assert meta.disciplines == ["structural"]
    assert meta.known_benefits == ["tuition_reimbursement"]


def test_get_firm_metadata_returns_none_for_missing_firm(db):
    assert FirmsService().get_firm_metadata("does-not-exist") is None


def test_list_firms_returns_dashboard_summaries(db):
    _insert_firm(db, "acme", name="Acme Engineering")
    _insert_firm(db, "globex", name="Globex Structural", manual_priority=FirmPriority.WATCH)
    _insert_job(db, "j1", firm_id="acme", company="Acme Engineering")

    summaries = FirmsService().list_firms()
    by_id = {s.firm_id: s for s in summaries}
    assert set(by_id) == {"acme", "globex"}
    assert by_id["acme"].open_job_count == 1
    assert by_id["globex"].open_job_count == 0
    assert by_id["acme"].known_benefit_count == 1


def test_list_firms_filters_by_manual_priority(db):
    _insert_firm(db, "acme", manual_priority=FirmPriority.TARGET)
    _insert_firm(db, "globex", manual_priority=FirmPriority.WATCH)

    target_only = FirmsService().list_firms(manual_priority="target")
    assert [s.firm_id for s in target_only] == ["acme"]


def test_get_firm_summary_matches_list_firms_entry(db):
    _insert_firm(db, "acme")

    summary = FirmsService().get_firm_summary("acme")
    assert summary is not None
    assert summary.firm_id == "acme"
    assert summary.name == "Acme Engineering"


def test_firm_models_serialize_to_json_compatible_dict(db):
    _insert_firm(db, "acme")

    detail = FirmsService().get_firm("acme")
    dumped = detail.model_dump(mode="json")
    assert dumped["firm_id"] == "acme"
    assert dumped["status"]["firm_id"] == "acme"
    assert isinstance(dumped["benefits"], dict)


# ── MetricsService ────────────────────────────────────────────────────────


def test_metrics_service_agrees_with_funnel_reporter(db):
    _insert_job(db, "j1")
    _advance(db, "j1", "presented", "selected", "applied")
    _insert_job(db, "j2", source="usajobs")
    _advance(db, "j2", "presented")

    via_service = MetricsService().get_funnel_stats()
    via_direct = FunnelReporter().compute()

    assert via_service.total_jobs == via_direct.total_jobs == 2
    assert via_service.by_state == via_direct.by_state
    assert via_service.by_source == via_direct.by_source
