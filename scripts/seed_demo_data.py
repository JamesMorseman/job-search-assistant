"""Seed a local current-schema SQLite database with fictional ATLAS demo data.

This script is intentionally local-only. It writes fictional records marked
with source='demo' and makes a timestamped backup before modifying an existing
database file.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from job_search.config import settings
from job_search.services.pipeline import PipelineService


DEMO_JOB_PREFIX = "demo-p7p5"


@dataclass(frozen=True)
class DemoOpportunity:
    job_id: str
    source_job_id: str
    company: str
    title: str
    city: str
    state: str
    remote_flag: str
    posted_date: str
    last_seen: str
    match_score: float
    stretch_category: str
    benefit_score: float
    trajectory_score: float
    app_state: str
    llm_grade: str
    llm_fit_score: float
    benefit_reasons: list[str]
    trajectory_reasons: list[str]
    description: str
    salary_min: int
    salary_max: int
    ko_min_years: float | None
    ko_eit_required: bool | None
    ko_degree_required: str


DEMO_OPPORTUNITIES: tuple[DemoOpportunity, ...] = (
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-atlas-infrastructure-001",
        source_job_id="atlas-infrastructure-001",
        company="Atlas Demo Infrastructure Group",
        title="Demo Civil Design Associate",
        city="Sample Metro",
        state="ST",
        remote_flag="hybrid",
        posted_date="2026-06-12",
        last_seen="2026-06-18 09:10:00",
        match_score=0.91,
        stretch_category="qualified",
        benefit_score=0.84,
        trajectory_score=0.88,
        app_state="presented",
        llm_grade="Strong",
        llm_fit_score=4.6,
        benefit_reasons=["Demo mentorship signal", "Sample training support"],
        trajectory_reasons=["Fictional design ownership", "Demo EIT-to-PE path"],
        description=(
            "Fictional demo record for ATLAS screenshot review only. "
            "This sample role emphasizes civil design coordination, safe review cues, "
            "and demo-only infrastructure context."
        ),
        salary_min=72000,
        salary_max=88000,
        ko_min_years=1.0,
        ko_eit_required=True,
        ko_degree_required="BS Civil Engineering or equivalent demo requirement",
    ),
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-northstar-civil-002",
        source_job_id="northstar-civil-002",
        company="Northstar Demo Civil",
        title="Sample Transportation Engineer",
        city="Fictional Junction",
        state="ST",
        remote_flag="no",
        posted_date="2026-06-11",
        last_seen="2026-06-18 09:08:00",
        match_score=0.86,
        stretch_category="qualified",
        benefit_score=0.76,
        trajectory_score=0.82,
        app_state="presented",
        llm_grade="Strong",
        llm_fit_score=4.3,
        benefit_reasons=["Sample continuing education support"],
        trajectory_reasons=["Demo transportation project exposure"],
        description=(
            "Fictional sample posting for local ATLAS review. The role is demo-only "
            "and includes safe transportation design language without real employer data."
        ),
        salary_min=69000,
        salary_max=83000,
        ko_min_years=0.0,
        ko_eit_required=False,
        ko_degree_required="Civil engineering degree preferred in demo context",
    ),
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-bluebridge-003",
        source_job_id="bluebridge-003",
        company="Bluebridge Sample Engineering",
        title="Fictional Structural Project Coordinator",
        city="Example Harbor",
        state="ST",
        remote_flag="hybrid",
        posted_date="2026-06-10",
        last_seen="2026-06-18 09:05:00",
        match_score=0.79,
        stretch_category="competitive_stretch",
        benefit_score=0.68,
        trajectory_score=0.8,
        app_state="selected",
        llm_grade="Good",
        llm_fit_score=4.0,
        benefit_reasons=["Demo professional development budget"],
        trajectory_reasons=["Fictional structural practice depth"],
        description=(
            "Fictional structural coordination opportunity for demo review only. "
            "Use this record to inspect populated Opportunity Detail content."
        ),
        salary_min=74000,
        salary_max=91000,
        ko_min_years=2.0,
        ko_eit_required=True,
        ko_degree_required="BS Civil or Structural Engineering in demo context",
    ),
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-harborline-transit-004",
        source_job_id="harborline-transit-004",
        company="Harborline Fictional Transit",
        title="Demo Transit Infrastructure Analyst",
        city="Sample Port",
        state="ST",
        remote_flag="yes",
        posted_date="2026-06-09",
        last_seen="2026-06-18 09:02:00",
        match_score=0.72,
        stretch_category="competitive_stretch",
        benefit_score=0.62,
        trajectory_score=0.74,
        app_state="presented",
        llm_grade="Good",
        llm_fit_score=3.8,
        benefit_reasons=["Sample flexible work signal"],
        trajectory_reasons=["Demo public infrastructure exposure"],
        description=(
            "Demo-only transit infrastructure record with fictional scope, safe labels, "
            "and no copied posting text."
        ),
        salary_min=68000,
        salary_max=82000,
        ko_min_years=1.0,
        ko_eit_required=None,
        ko_degree_required="Engineering or planning degree in fictional context",
    ),
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-clearwater-works-005",
        source_job_id="clearwater-works-005",
        company="Clearwater Demo Works",
        title="Sample Water Resources Associate",
        city="Demo Springs",
        state="ST",
        remote_flag="hybrid",
        posted_date="2026-06-08",
        last_seen="2026-06-18 08:58:00",
        match_score=0.66,
        stretch_category="qualified",
        benefit_score=0.7,
        trajectory_score=0.69,
        app_state="discovered",
        llm_grade="Good",
        llm_fit_score=3.6,
        benefit_reasons=["Demo tuition support signal"],
        trajectory_reasons=["Sample water resources project rotation"],
        description=(
            "Fictional water resources opportunity for ATLAS demo data. "
            "Visible text is intentionally sample-only."
        ),
        salary_min=65000,
        salary_max=79000,
        ko_min_years=0.0,
        ko_eit_required=False,
        ko_degree_required="Civil or environmental engineering demo requirement",
    ),
    DemoOpportunity(
        job_id=f"{DEMO_JOB_PREFIX}-summit-structures-006",
        source_job_id="summit-structures-006",
        company="Summit Demo Structures",
        title="Fictional Bridge Inspection Engineer",
        city="Example Ridge",
        state="ST",
        remote_flag="no",
        posted_date="2026-06-07",
        last_seen="2026-06-18 08:54:00",
        match_score=0.58,
        stretch_category="long_shot",
        benefit_score=0.52,
        trajectory_score=0.64,
        app_state="discovered",
        llm_grade="Marginal",
        llm_fit_score=3.1,
        benefit_reasons=["Sample field training signal"],
        trajectory_reasons=["Fictional inspection experience path"],
        description=(
            "Fictional bridge inspection sample for demo review. This record is not a "
            "real posting and contains no real application details."
        ),
        salary_min=70000,
        salary_max=86000,
        ko_min_years=3.0,
        ko_eit_required=True,
        ko_degree_required="Civil engineering degree in fictional demo context",
    ),
)


def _now_stamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")


def _backup_database(db_path: Path) -> Path | None:
    if not db_path.exists():
        return None
    backup_dir = db_path.parent / "recovery_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{db_path.stem}.before-p7p5-demo.{_now_stamp()}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _require_current_schema(conn: sqlite3.Connection) -> None:
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    required = {"jobs", "pipeline_runs"}
    missing = sorted(required - tables)
    if missing:
        raise RuntimeError(
            "Database is missing required current-schema table(s): "
            + ", ".join(missing)
            + ". Run 'jsa init-db' first."
        )


def _reason_json(labels: list[str]) -> str:
    return json.dumps([{"label": label, "source": "demo"} for label in labels])


def _delete_existing_demo_rows(conn: sqlite3.Connection) -> int:
    demo_ids = [
        row["canonical_job_id"]
        for row in conn.execute(
            """
            SELECT canonical_job_id
            FROM jobs
            WHERE source = 'demo' OR canonical_job_id LIKE ?
            """,
            (f"{DEMO_JOB_PREFIX}-%",),
        )
    ]
    if demo_ids:
        placeholders = ",".join("?" for _ in demo_ids)
        for table in ("generated_docs", "job_keywords", "followup_queue", "app_transitions"):
            conn.execute(f"DELETE FROM {table} WHERE canonical_job_id IN ({placeholders})", demo_ids)
        conn.execute(f"DELETE FROM jobs WHERE canonical_job_id IN ({placeholders})", demo_ids)

    run_count = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM pipeline_runs
        WHERE source = 'demo' OR trigger = 'demo' OR run_type = 'demo'
        """
    ).fetchone()["count"]
    conn.execute(
        """
        DELETE FROM pipeline_runs
        WHERE source = 'demo' OR trigger = 'demo' OR run_type = 'demo'
        """
    )
    return len(demo_ids) + int(run_count)


def _insert_demo_jobs(conn: sqlite3.Connection) -> None:
    for item in DEMO_OPPORTUNITIES:
        conn.execute(
            """
            INSERT INTO jobs (
                canonical_job_id, source, source_job_id, company, title,
                discipline_tags, location_city, location_state, location_country,
                remote_flag, description_raw, description_normalized, jd_content_hash,
                apply_url, posted_date, first_seen, last_seen, salary_min, salary_max,
                ko_work_auth, ko_min_years, ko_eit_required, ko_pe_required,
                ko_clearance, ko_relocation, ko_degree_required, match_score,
                stretch_category, benefit_score, career_trajectory_score,
                benefit_reasons, trajectory_reasons, llm_grade, llm_fit_score,
                llm_rationale, llm_graded_at, llm_model, app_state, ats_type
            )
            VALUES (
                ?, 'demo', ?, ?, ?, ?, ?, ?, 'US', ?, ?, ?, ?, NULL, ?, ?, ?,
                ?, ?, 'Demo-only work authorization context', ?, ?, 0, NULL,
                'No relocation in demo context', ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, 'demo-local', ?, 'other'
            )
            """,
            (
                item.job_id,
                item.source_job_id,
                item.company,
                item.title,
                json.dumps(["civil", "demo", "sample"]),
                item.city,
                item.state,
                item.remote_flag,
                item.description,
                item.description,
                f"demo-hash-{item.source_job_id}",
                item.posted_date,
                item.last_seen,
                item.last_seen,
                item.salary_min,
                item.salary_max,
                item.ko_min_years,
                int(item.ko_eit_required) if item.ko_eit_required is not None else None,
                item.ko_degree_required,
                item.match_score,
                item.stretch_category,
                item.benefit_score,
                item.trajectory_score,
                _reason_json(item.benefit_reasons),
                _reason_json(item.trajectory_reasons),
                item.llm_grade,
                item.llm_fit_score,
                (
                    f"Fictional ATLAS demo rationale for {item.company}: "
                    "review the visible score, stage, and safe next cue only."
                ),
                "2026-06-18 09:15:00",
                item.app_state,
            ),
        )


def _insert_demo_pipeline_runs(db_path: Path) -> list[int]:
    pipeline = PipelineService(db_path=str(db_path))

    older_id = pipeline.start_run("grade", source="demo", trigger="demo")
    pipeline.update_counters(
        older_id,
        jobs_seen=4,
        jobs_created=2,
        jobs_updated=1,
        jobs_presented=2,
        errors_count=0,
    )
    pipeline.complete_run(
        older_id,
        metadata={"demo": True, "purpose": "fictional ATLAS pipeline history"},
        notes="Fictional demo grading pass for screenshot-readiness review.",
    )

    latest_id = pipeline.start_run("full", source="demo", trigger="demo")
    pipeline.update_counters(
        latest_id,
        jobs_seen=len(DEMO_OPPORTUNITIES),
        jobs_created=len(DEMO_OPPORTUNITIES),
        jobs_updated=0,
        jobs_presented=3,
        errors_count=0,
    )
    pipeline.complete_run(
        latest_id,
        metadata={"demo": True, "purpose": "fictional ATLAS runtime hardening"},
        notes="Fictional completed demo run: 6 seen, 6 created, 0 updated, 3 presented, 0 errors.",
    )
    return [older_id, latest_id]


def seed_demo_database(db_path: str | Path | None = None) -> dict[str, object]:
    """Back up, reset existing demo rows, and seed fictional demo records."""
    resolved_path = Path(db_path or settings.DB_PATH)
    backup_path = _backup_database(resolved_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Database not found at {resolved_path}. Run 'jsa init-db' first.")

    with _connect(resolved_path) as conn:
        _require_current_schema(conn)
        removed = _delete_existing_demo_rows(conn)
        _insert_demo_jobs(conn)
        conn.commit()

    run_ids = _insert_demo_pipeline_runs(resolved_path)
    return {
        "db_path": str(resolved_path),
        "backup_path": str(backup_path) if backup_path else None,
        "removed_demo_rows": removed,
        "jobs_seeded": len(DEMO_OPPORTUNITIES),
        "pipeline_runs_seeded": len(run_ids),
        "latest_run_id": run_ids[-1],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed fictional ATLAS demo data into a local SQLite DB.")
    parser.add_argument(
        "--db-path",
        default=None,
        help="SQLite database path. Defaults to job_search.config.settings.DB_PATH.",
    )
    args = parser.parse_args()

    result = seed_demo_database(args.db_path)
    print("Seeded fictional ATLAS demo data.")
    print(f"Database: {result['db_path']}")
    print(f"Backup: {result['backup_path']}")
    print(f"Removed demo rows: {result['removed_demo_rows']}")
    print(f"Jobs seeded: {result['jobs_seeded']}")
    print(f"Pipeline runs seeded: {result['pipeline_runs_seeded']}")
    print(f"Latest run id: {result['latest_run_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
