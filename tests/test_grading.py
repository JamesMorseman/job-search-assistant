"""Tests for the LLM fit-grading tier (no network; OpenAI client is mocked)."""

import json
import re
import sqlite3
from types import SimpleNamespace

import pytest

from job_search.db.connection import init_db
from job_search.grading import FitGrader, GradeResult

VALID_ID = "a" * 64  # 64 hex chars, like a real canonical_job_id (SHA256)


# ── fake OpenAI batch client ─────────────────────────────────────────────────
def _result_line(custom_id, payload, model="gpt-4.1"):
    return json.dumps({
        "custom_id": custom_id,
        "response": {
            "status_code": 200,
            "body": {
                "model": model,
                "choices": [
                    {"message": {"content": json.dumps(payload)}}
                ],
            },
        },
    })


def _errored_line(custom_id):
    return json.dumps({
        "custom_id": custom_id,
        "error": {"message": "failed"},
    })


class FakeFiles:
    def __init__(self, output_text=""):
        self.output_text = output_text
        self.created: list = []

    def create(self, file, purpose):
        self.created.append({"file": file, "purpose": purpose})
        return SimpleNamespace(id="file_input")

    def content(self, file_id):
        return SimpleNamespace(read=lambda: self.output_text.encode("utf-8"))


class FakeBatches:
    def __init__(self, *, status="completed", batch_id="batch_test"):
        self._status = status
        self._batch_id = batch_id
        self.created: list = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id=self._batch_id)

    def retrieve(self, batch_id):
        return SimpleNamespace(status=self._status, output_file_id="file_output")


class FakeOpenAIClient:
    def __init__(self, batches=None, files=None):
        self.batches = batches or FakeBatches()
        self.files = files or FakeFiles()


def _client(batches=None, output_text=""):
    return FakeOpenAIClient(batches=batches, files=FakeFiles(output_text))


def _grader(client=None, profile=None):
    g = FitGrader(client=client or _client())
    g._profile = profile or {"identity": {"first_name": "James", "last_name": "Morseman"}}
    return g


# ── DB helpers ───────────────────────────────────────────────────────────────
@pytest.fixture
def db_path(tmp_path, monkeypatch):
    p = str(tmp_path / "test.db")
    monkeypatch.setattr("job_search.config.settings.DB_PATH", p)
    init_db(p)
    return p


def _conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _insert(conn, job_id, match_score=0.7, state="discovered",
            stretch="qualified", graded_at=None):
    conn.execute(
        "INSERT INTO jobs (canonical_job_id, source, source_job_id, company, title, "
        "description_normalized, match_score, stretch_category, app_state, llm_graded_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (job_id, "test", job_id, "Acme Eng", "Civil Engineer",
         "structural design of bridges", match_score, stretch, state, graded_at),
    )
    conn.commit()


# ── selection ────────────────────────────────────────────────────────────────
def test_select_viable_filters_and_orders(db_path):
    conn = _conn(db_path)
    _insert(conn, "hi", match_score=0.90)
    _insert(conn, "lo", match_score=0.40)
    _insert(conn, "mid", match_score=0.70)
    _insert(conn, "shot", match_score=0.95, stretch="long_shot")
    _insert(conn, "seen", match_score=0.95, graded_at="2026-01-01")
    _insert(conn, "pres", match_score=0.95, state="presented")

    rows = _grader().select_viable(conn, max_jobs=10)
    ids = [r["canonical_job_id"] for r in rows]
    assert ids == ["hi", "mid"]


def test_select_viable_respects_cap(db_path):
    conn = _conn(db_path)
    for i in range(5):
        _insert(conn, f"j{i}", match_score=0.6 + i / 100)
    rows = _grader().select_viable(conn, max_jobs=3)
    assert len(rows) == 3


# ── request construction ─────────────────────────────────────────────────────
def test_custom_id_is_canonical_job_id():
    job = {"canonical_job_id": VALID_ID, "title": "CE", "company": "Acme",
           "description_normalized": "bridges"}
    req = _grader()._build_request(job)
    assert req["custom_id"] == VALID_ID
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,64}", req["custom_id"])


def test_request_carries_schema_and_cached_profile():
    job = {"canonical_job_id": VALID_ID, "title": "CE", "company": "Acme",
           "description_normalized": "bridges"}
    req = _grader()._build_request(job)
    body = req["body"]

    schema = body["response_format"]["json_schema"]["schema"]
    assert schema["properties"]["grade"]["enum"] == ["Strong", "Good", "Marginal", "Pass"]
    assert schema["properties"]["fit_score"]["maximum"] == 5

    assert req["method"] == "POST"
    assert req["url"] == "/v1/chat/completions"
    assert "James" in body["messages"][0]["content"]
    assert body["model"] == "gpt-4.1"


# ── results + persistence ────────────────────────────────────────────────────
def test_fetch_results_keeps_only_successful_lines():
    text = "\n".join([
        _result_line("good", {"grade": "Strong", "fit_score": 5, "rationale": "fits"}),
        _errored_line("bad"),
    ])
    results = _grader(_client(output_text=text)).fetch_results("b")
    assert len(results) == 1
    assert results[0].canonical_job_id == "good"
    assert results[0].grade == "Strong"


def test_persist_sets_columns_and_grade_once(db_path):
    conn = _conn(db_path)
    _insert(conn, "j1", match_score=0.8)
    grader = _grader()

    n = grader.persist(conn, [GradeResult("j1", "Good", 4, "solid match", "gpt-4.1")])
    conn.commit()
    assert n == 1

    row = conn.execute(
        "SELECT llm_grade, llm_fit_score, llm_rationale, llm_graded_at FROM jobs WHERE canonical_job_id='j1'"
    ).fetchone()
    assert row["llm_grade"] == "Good"
    assert row["llm_fit_score"] == 4
    assert row["llm_graded_at"] is not None

    assert _grader().select_viable(conn) == []


def test_persist_rejects_invalid_grade(db_path):
    conn = _conn(db_path)
    _insert(conn, "j1", match_score=0.8)
    n = _grader().persist(conn, [GradeResult("j1", "Excellent", 9, "x", "m")])
    conn.commit()
    assert n == 0
    row = conn.execute("SELECT llm_grade FROM jobs WHERE canonical_job_id='j1'").fetchone()
    assert row["llm_grade"] is None


# ── drain prior batch ────────────────────────────────────────────────────────
def test_drain_prior_finishes_open_batch(db_path):
    conn = _conn(db_path)
    _insert(conn, "j1", match_score=0.8)
    conn.execute(
        "INSERT INTO grading_batches (batch_id, status, job_count) VALUES ('bprev', 'submitted', 1)"
    )
    conn.commit()

    text = _result_line("j1", {"grade": "Marginal", "fit_score": 2, "rationale": "gap"})
    drained = _grader(_client(output_text=text)).drain_prior(conn)
    conn.commit()

    assert drained == 1
    assert conn.execute("SELECT llm_grade FROM jobs WHERE canonical_job_id='j1'").fetchone()[0] == "Marginal"
    assert conn.execute("SELECT status FROM grading_batches WHERE batch_id='bprev'").fetchone()[0] == "drained"


def test_drain_prior_leaves_unfinished_batch(db_path):
    conn = _conn(db_path)
    conn.execute(
        "INSERT INTO grading_batches (batch_id, status, job_count) VALUES ('bprev', 'submitted', 1)"
    )
    conn.commit()
    drained = _grader(_client(batches=FakeBatches(status="in_progress"))).drain_prior(conn)
    assert drained == 0
    assert conn.execute("SELECT status FROM grading_batches WHERE batch_id='bprev'").fetchone()[0] == "submitted"


# ── run() orchestration ──────────────────────────────────────────────────────
def test_run_disabled_is_noop(db_path, monkeypatch):
    monkeypatch.setattr("job_search.config.settings.GRADING_ENABLED", False)
    client = _client()
    stats = _grader(client).run()
    assert stats["enabled"] is False
    assert client.batches.created == []


def test_run_timeout_fallback(db_path, monkeypatch):
    monkeypatch.setattr("job_search.config.settings.GRADING_ENABLED", True)
    conn = _conn(db_path)
    _insert(conn, "j1", match_score=0.8)
    conn.close()

    client = _client(batches=FakeBatches(status="in_progress", batch_id="bnew"))
    stats = _grader(client).run(timeout_s=0)

    assert stats["timed_out"] is True
    assert stats["graded"] == 0
    assert len(client.batches.created) == 1

    conn = _conn(db_path)
    assert conn.execute("SELECT llm_graded_at FROM jobs WHERE canonical_job_id='j1'").fetchone()[0] is None
    assert conn.execute("SELECT status FROM grading_batches WHERE batch_id='bnew'").fetchone()[0] == "submitted"


def test_run_full_cycle_persists(db_path, monkeypatch):
    monkeypatch.setattr("job_search.config.settings.GRADING_ENABLED", True)
    conn = _conn(db_path)
    _insert(conn, "j1", match_score=0.8)
    conn.close()

    text = _result_line("j1", {"grade": "Strong", "fit_score": 5, "rationale": "strong fit"})
    client = _client(batches=FakeBatches(status="completed", batch_id="bnew"), output_text=text)
    stats = _grader(client).run(timeout_s=5)

    assert stats["graded"] == 1
    assert stats["timed_out"] is False
    conn = _conn(db_path)
    assert conn.execute("SELECT llm_grade FROM jobs WHERE canonical_job_id='j1'").fetchone()[0] == "Strong"
    assert conn.execute("SELECT status FROM grading_batches WHERE batch_id='bnew'").fetchone()[0] == "drained"
