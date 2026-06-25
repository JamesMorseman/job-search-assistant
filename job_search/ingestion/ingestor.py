"""Main daily ingestion orchestrator — Subsystem A."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

import yaml

from job_search.config import settings
from job_search.db import get_db
from job_search.models import FirmConfig

from .dedup import Deduplicator
from .scoring import Scorer

logger = logging.getLogger(__name__)

QUERY_LANES = {
    "structural_engineering": ("structural", "bridge", "steel", "concrete"),
    "site_civil_land_development": ("land development", "site civil", "site design"),
    "water_resources_stormwater": ("water resource", "stormwater", "hydrology", "hydraulic"),
    "environmental": ("environmental", "remediation", "permitting"),
    "construction_project_field": ("construction", "project engineer", "field engineer", "schedule"),
    "public_sector_municipal": ("municipal", "public works", "city engineer", "county"),
    "technical_analyst_data_systems": ("data", "analyst", "systems", "automation", "python", "sql"),
    "project_controls": ("project controls", "cost control", "scheduling", "primavera", "p6"),
    "general_civil": ("civil engineer", "civil engineering"),
}


class Ingestor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.scorer = Scorer()
        self._firms: list[FirmConfig] = []

    def load_firms(self, config_path: str = "config/firms.yaml") -> None:
        try:
            with open(config_path) as f:
                raw = yaml.safe_load(f) or {}
            firms = [FirmConfig(**firm) for firm in raw.get("firms", [])]
            self._firms = [firm for firm in firms if not self._is_placeholder_firm(firm)]
            skipped = len(firms) - len(self._firms)
            logger.info(
                "Loaded %d firms from registry%s",
                len(self._firms),
                f" ({skipped} placeholder skipped)" if skipped else "",
            )
        except FileNotFoundError:
            logger.warning("firms.yaml not found — registry empty; only public-sector sources will run")

    def run(self) -> dict:
        stats = {
            "started_at": datetime.utcnow().isoformat(),
            "new": 0,
            "updated": 0,
            "reposts": 0,
            "errors": 0,
            "would_insert": 0,
            "would_update": 0,
            "would_repost": 0,
            "dry_run": self.dry_run,
            "sources": {},
            "query_lanes": {lane: 0 for lane in QUERY_LANES},
        }
        logger.info("Ingest starting: dry_run=%s db_path=%s", self.dry_run, Path(settings.DB_PATH).resolve())

        with get_db() as db:
            dedup = Deduplicator(db)

            for job in self._iter_all_sources(db):
                try:
                    job = self.scorer.score(job)
                    self._record_query_lane(stats, job)
                    if self.dry_run:
                        logger.info("DRY RUN — would upsert: %s @ %s", job.title, job.company)
                        src = stats["sources"].setdefault(
                            job.source,
                            {
                                "new": 0,
                                "updated": 0,
                                "reposts": 0,
                                "would_create": 0,
                                "would_update": 0,
                                "would_repost": 0,
                            },
                        )
                        exists = db.execute(
                            "SELECT 1 FROM jobs WHERE canonical_job_id = ?",
                            (job.canonical_job_id,),
                        ).fetchone()
                        if exists:
                            stats["would_update"] += 1
                            src["would_update"] += 1
                        else:
                            stats["would_insert"] += 1
                            src["would_create"] += 1
                            if dedup._detect_repost(job):
                                stats["would_repost"] += 1
                                src["would_repost"] += 1
                        continue
                    is_new, is_repost = dedup.upsert(job)
                    src = stats["sources"].setdefault(
                        job.source,
                        {
                            "new": 0,
                            "updated": 0,
                            "reposts": 0,
                            "would_create": 0,
                            "would_update": 0,
                            "would_repost": 0,
                        },
                    )
                    if is_new:
                        stats["new"] += 1
                        src["new"] += 1
                        self._safe_log_health(db, job.source, job.firm_id, "ok")
                    else:
                        stats["updated"] += 1
                        src["updated"] += 1
                    if is_repost:
                        stats["reposts"] += 1
                        src["reposts"] += 1
                except Exception as exc:
                    logger.error("Failed to process job %s: %s", getattr(job, "source_job_id", "?"), exc)
                    stats["errors"] += 1

        stats["finished_at"] = datetime.utcnow().isoformat()
        logger.info(
            "Ingestion complete: %d new, %d updated, %d reposts, %d errors",
            stats["new"], stats["updated"], stats["reposts"], stats["errors"],
        )
        return stats

    @staticmethod
    def _record_query_lane(stats: dict, job) -> None:
        lanes = stats.setdefault("query_lanes", {lane: 0 for lane in QUERY_LANES})
        text = " ".join(
            str(value or "").lower()
            for value in (
                job.title,
                job.company,
                job.description_normalized,
                job.description_raw,
                " ".join(job.discipline_tags or []),
            )
        )
        matched = False
        for lane, terms in QUERY_LANES.items():
            if any(term in text for term in terms):
                lanes[lane] = int(lanes.get(lane, 0) or 0) + 1
                matched = True
        if not matched:
            lanes["general_civil"] = int(lanes.get("general_civil", 0) or 0) + 1

    def _iter_all_sources(self, db):
        """Yield CanonicalJob from all configured sources in priority order."""
        from job_search.adapters import (
            ATS_ADAPTER_MAP,
            AdzunaAdapter,
            EmailAlertsAdapter,
            USAJobsAdapter,
        )
        from job_search.models import ATSTier

        # 1. Public sector (USAJOBS)
        yield from self._run_adapter(USAJobsAdapter(), db)

        # 2. Aggregator (Adzuna)
        yield from self._run_adapter(AdzunaAdapter(), db)

        # 3. Green-tier firm adapters
        for firm in self._firms:
            if firm.ats_tier == ATSTier.GREEN:
                adapter_cls = ATS_ADAPTER_MAP.get(firm.ats_type)
                if adapter_cls:
                    yield from self._run_adapter(adapter_cls(firm), db)

        # 4. Yellow-tier (Workday) — throttled
        for firm in self._firms:
            if firm.ats_tier == ATSTier.YELLOW:
                adapter_cls = ATS_ADAPTER_MAP.get(firm.ats_type)
                if adapter_cls:
                    yield from self._run_adapter(adapter_cls(firm), db)

        # 5. Email alerts — backstop for LinkedIn/Indeed (ruled out for direct scraping)
        yield from self._run_adapter(EmailAlertsAdapter(), db)

    def _run_adapter(self, adapter, db):
        source_name = adapter.source_name
        firm_id = getattr(adapter.firm, "firm_id", None) if adapter.firm else None
        try:
            count = 0
            for job in adapter.fetch():
                count += 1
                yield job
            logger.info("Adapter %s/%s: %d jobs yielded", source_name, firm_id or "global", count)
        except Exception as exc:
            logger.error("Adapter %s/%s failed: %s", source_name, firm_id or "global", exc)
            self._safe_log_health(db, source_name, firm_id, "error", str(exc))

    def _log_health(
        self,
        db,
        source: str,
        firm_id: str | None,
        status: str,
        error_detail: str | None = None,
    ) -> None:
        db.execute(
            """
            INSERT INTO source_health (source, firm_id, status, error_detail)
            VALUES (?, ?, ?, ?)
            """,
            (source, firm_id, status, error_detail),
        )

    def _safe_log_health(
        self,
        db,
        source: str,
        firm_id: str | None,
        status: str,
        error_detail: str | None = None,
    ) -> None:
        try:
            self._log_health(db, source, firm_id, status, error_detail)
        except sqlite3.Error as exc:
            logger.warning("Source health logging failed for %s/%s: %s", source, firm_id or "global", exc)

    @staticmethod
    def _is_placeholder_firm(firm: FirmConfig) -> bool:
        identity_text = " ".join(str(value or "").lower() for value in (
            firm.firm_id,
            firm.name,
            firm.ats_board_token,
            firm.ats_tenant,
            firm.ats_site,
        ))
        urls = " ".join(str(value or "").lower() for value in (firm.website, firm.careers_url))
        return (
            any(marker in identity_text for marker in ("example", "placeholder", "replace with real", "testfirm"))
            or "example.com" in urls
            or "examplefirm" in urls
        )
