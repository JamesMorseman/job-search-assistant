"""Tests for ingestion orchestration hardening."""

import sqlite3

from job_search.ingestion.ingestor import Ingestor
from job_search.db.connection import init_db
from job_search.models import CanonicalJob


class FakeDB:
    def execute(self, *args, **kwargs):
        return None


class LockedHealthDB:
    def execute(self, *args, **kwargs):
        raise sqlite3.OperationalError("database is locked")


class FailingAdapter:
    source_name = "greenhouse"
    firm = None

    def fetch(self):
        raise RuntimeError("404 not found")


class OneJobAdapter:
    source_name = "test_source"
    firm = None

    def __init__(self, *args, **kwargs):
        pass

    def fetch(self):
        yield CanonicalJob(
            source=self.source_name,
            source_job_id="job1",
            company="Acme",
            title="Civil Engineer",
            description_normalized="civil structural design",
        )


class EmptyAdapter:
    source_name = "empty_source"
    firm = None

    def __init__(self, *args, **kwargs):
        pass

    def fetch(self):
        return iter(())


def test_load_firms_skips_placeholder_entries(tmp_path):
    firms_yaml = tmp_path / "firms.yaml"
    firms_yaml.write_text(
        """
firms:
  - firm_id: example_green_firm
    name: Example Green Firm
    website: https://example.com
    careers_url: https://boards.greenhouse.io/examplefirm
    ats_type: greenhouse
    ats_tier: green
    ats_board_token: examplefirm
  - firm_id: real_green_firm
    name: Real Green Firm
    website: https://real.example
    careers_url: https://boards.greenhouse.io/realfirm
    ats_type: greenhouse
    ats_tier: green
    ats_board_token: realfirm
""",
        encoding="utf-8",
    )
    ingestor = Ingestor()

    ingestor.load_firms(str(firms_yaml))

    assert [firm.firm_id for firm in ingestor._firms] == ["real_green_firm"]


def test_adapter_failure_and_locked_health_logging_do_not_crash():
    ingestor = Ingestor()

    jobs = list(ingestor._run_adapter(FailingAdapter(), LockedHealthDB()))

    assert jobs == []


def test_public_sources_still_run_with_empty_firm_registry(monkeypatch):
    import job_search.adapters as adapters

    monkeypatch.setattr(adapters, "USAJobsAdapter", OneJobAdapter)
    monkeypatch.setattr(adapters, "AdzunaAdapter", OneJobAdapter)
    monkeypatch.setattr(adapters, "EmailAlertsAdapter", EmptyAdapter)

    ingestor = Ingestor()
    ingestor._firms = []

    jobs = list(ingestor._iter_all_sources(FakeDB()))

    assert [job.source for job in jobs] == ["test_source", "test_source"]


def test_dry_run_counts_would_insert_without_new_or_db_writes(tmp_path, monkeypatch):
    db_path = str(tmp_path / "jobs.db")
    init_db(db_path)
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)

    ingestor = Ingestor(dry_run=True)
    monkeypatch.setattr(ingestor, "_iter_all_sources", lambda db: iter([
        CanonicalJob(
            source="test",
            source_job_id="dry1",
            company="Acme",
            title="Civil Engineer",
            description_normalized="civil structural design",
        )
    ]))

    stats = ingestor.run()

    assert stats["dry_run"] is True
    assert stats["would_insert"] == 1
    assert stats["new"] == 0
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0
    finally:
        conn.close()


def test_real_ingest_counts_new_and_writes_to_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "jobs.db")
    init_db(db_path)
    monkeypatch.setattr("job_search.config.settings.DB_PATH", db_path)

    ingestor = Ingestor(dry_run=False)
    monkeypatch.setattr(ingestor, "_iter_all_sources", lambda db: iter([
        CanonicalJob(
            source="test",
            source_job_id="real1",
            company="Acme",
            title="Civil Engineer",
            description_normalized="civil structural design",
        )
    ]))

    stats = ingestor.run()

    assert stats["dry_run"] is False
    assert stats["would_insert"] == 0
    assert stats["new"] == 1
    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
    finally:
        conn.close()
