"""Missing-firm discovery — identifies companies in ingested jobs without approved firm profiles.

Alias limitation (MVP):
    Comparison is against approved firm_id slugs only. A company whose suggested
    slug does not match any existing firm_id will appear as a candidate even if
    the firm is already approved under a different name or alias.
    Alias-aware filtering is deferred until alias support is added to the
    approved firm repository (Phase 3 Step 4+).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from job_search.db import get_db

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _make_firm_id_slug(name: str) -> str:
    """Convert a company name to a safe firm_id slug (lowercase, underscores, max 40 chars)."""
    slug = _NON_ALNUM.sub("_", name.lower()).strip("_")
    return slug[:40] if slug else "unknown"


def _load_approved_firm_ids(config_path: str | Path = "config/firms.yaml") -> frozenset[str]:
    """Return approved firm_id values from firms.yaml. Returns empty frozenset if file is missing."""
    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return frozenset(
            f["firm_id"]
            for f in raw.get("firms", [])
            if isinstance(f, dict) and "firm_id" in f
        )
    except FileNotFoundError:
        return frozenset()


@dataclass
class FirmCandidate:
    company: str
    suggested_firm_id: str
    job_count: int
    sources: list[str] = field(default_factory=list)
    sample_urls: list[str] = field(default_factory=list)


def discover_missing_firms(
    *,
    min_jobs: int = 1,
    source_filter: str | None = None,
    config_path: str | Path = "config/firms.yaml",
    db_path: str | None = None,
) -> list[FirmCandidate]:
    """Return FirmCandidate records for companies in ingested jobs that lack an approved firm profile.

    Results are sorted by descending job count, then alphabetically by company name.

    Alias limitation (MVP): approved firm exclusion uses firm_id slug matching only.
    Firms approved under a different name or alias may still appear as candidates.
    """
    approved_ids = _load_approved_firm_ids(config_path)

    query = "SELECT company, source, apply_url FROM jobs"
    params: tuple = ()
    if source_filter:
        query += " WHERE source = ?"
        params = (source_filter,)

    with get_db(db_path) as db:
        rows = db.execute(query, params).fetchall()

    agg: dict[str, dict] = {}
    for row in rows:
        company = (row["company"] or "").strip()
        if not company:
            continue
        entry = agg.setdefault(company, {"count": 0, "sources": set(), "urls": []})
        entry["count"] += 1
        if row["source"]:
            entry["sources"].add(row["source"])
        if row["apply_url"] and len(entry["urls"]) < 3:
            entry["urls"].append(row["apply_url"])

    candidates: list[FirmCandidate] = []
    for company, data in agg.items():
        if data["count"] < min_jobs:
            continue
        slug = _make_firm_id_slug(company)
        if slug in approved_ids:
            continue
        candidates.append(FirmCandidate(
            company=company,
            suggested_firm_id=slug,
            job_count=data["count"],
            sources=sorted(data["sources"]),
            sample_urls=data["urls"],
        ))

    return sorted(candidates, key=lambda c: (-c.job_count, c.company.lower()))
