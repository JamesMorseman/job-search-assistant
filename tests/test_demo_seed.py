"""Phase 7 Package 5 demo seed tests."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.db.connection import init_db

ROOT = Path(__file__).resolve().parents[1]
SEED_SCRIPT = ROOT / "scripts" / "seed_demo_data.py"

spec = importlib.util.spec_from_file_location("seed_demo_data", SEED_SCRIPT)
seed_demo_data = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["seed_demo_data"] = seed_demo_data
spec.loader.exec_module(seed_demo_data)


def test_seed_demo_database_creates_backup_and_current_schema_demo_rows(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_db(str(db_path))

    result = seed_demo_data.seed_demo_database(db_path)

    backup_path = Path(result["backup_path"])
    assert backup_path.exists()
    assert backup_path.parent == tmp_path / "recovery_backups"
    assert result["jobs_seeded"] == 6
    assert result["pipeline_runs_seeded"] == 2

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    jobs = conn.execute(
        "SELECT canonical_job_id, source, company, title, app_state FROM jobs ORDER BY canonical_job_id"
    ).fetchall()
    runs = conn.execute(
        "SELECT run_type, status, source, trigger, jobs_seen, jobs_created, jobs_updated, jobs_presented, errors_count "
        "FROM pipeline_runs ORDER BY id DESC"
    ).fetchall()
    conn.close()

    assert len(jobs) == 6
    assert {row["source"] for row in jobs} == {"demo"}
    assert all("Demo" in row["company"] or "Sample" in row["company"] or "Fictional" in row["company"] for row in jobs)
    assert {row["app_state"] for row in jobs} == {"discovered", "presented", "selected"}

    latest = runs[0]
    assert latest["run_type"] == "full"
    assert latest["status"] == "complete"
    assert latest["source"] == "demo"
    assert latest["trigger"] == "demo"
    assert latest["jobs_seen"] == 6
    assert latest["jobs_created"] == 6
    assert latest["jobs_updated"] == 0
    assert latest["jobs_presented"] == 3
    assert latest["errors_count"] == 0


def test_seed_demo_database_is_repeatable_and_replaces_demo_rows_only(tmp_path):
    db_path = tmp_path / "jobs.db"
    init_db(str(db_path))
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO jobs (canonical_job_id, source, source_job_id, company, title) VALUES (?, ?, ?, ?, ?)",
        ("real-local-job", "greenhouse", "real-local-job", "Local Private Company", "Private Role"),
    )
    conn.commit()
    conn.close()

    first = seed_demo_data.seed_demo_database(db_path)
    second = seed_demo_data.seed_demo_database(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    demo_jobs = conn.execute("SELECT COUNT(*) AS count FROM jobs WHERE source = 'demo'").fetchone()["count"]
    real_jobs = conn.execute("SELECT COUNT(*) AS count FROM jobs WHERE canonical_job_id = 'real-local-job'").fetchone()[
        "count"
    ]
    demo_runs = conn.execute(
        "SELECT COUNT(*) AS count FROM pipeline_runs WHERE source = 'demo' OR trigger = 'demo'"
    ).fetchone()["count"]
    conn.close()

    assert first["jobs_seeded"] == 6
    assert second["removed_demo_rows"] >= 8
    assert demo_jobs == 6
    assert demo_runs == 2
    assert real_jobs == 1


def test_seeded_demo_data_populates_atlas_api_surfaces(tmp_path, monkeypatch):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(db_path))
    init_db(str(db_path))
    seed_demo_data.seed_demo_database(db_path)

    app = create_app()
    with TestClient(app) as client:
        summary = client.get("/atlas/api/summary").json()
        opportunities = client.get("/atlas/api/opportunities").json()
        pipeline = client.get("/atlas/api/pipeline/runs").json()
        first_job_id = opportunities["opportunities"][0]["job_id"]
        detail = client.get(f"/atlas/api/opportunities/{first_job_id}").json()

    assert summary["total_opportunities"] == 6
    assert {"stage": "presented", "count": 3} in summary["stages"]
    assert len(opportunities["opportunities"]) == 6
    assert opportunities["opportunities"][0]["source"] == "demo"
    assert pipeline["runs"][0]["jobs_seen"] == 6
    assert pipeline["runs"][0]["jobs_created"] == 6
    assert pipeline["runs"][0]["jobs_presented"] == 3
    assert detail["source"] == "demo"
    assert detail["description"].startswith("Fictional")
    assert detail["llm_rationale"].startswith("Fictional ATLAS demo rationale")
    assert detail["benefit_reasons"]
    assert detail["trajectory_reasons"]
