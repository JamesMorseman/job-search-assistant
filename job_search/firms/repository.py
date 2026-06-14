"""Firm repository — draft file I/O and approved firm SQLite sync.

Approved firm profiles live in config/firms.yaml.
Draft profiles live in data/firm_drafts/<firm_id>.yaml.

Drafts are never loaded by ingestion, scoring, or approved-firm sync.
Only write_draft / read_draft / list_drafts touch the draft directory.
sync_approved_firms() reads only from config/firms.yaml.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from pathlib import Path

import yaml

from job_search.models import DraftFirmProfile, FirmProfile

logger = logging.getLogger(__name__)

# Default draft staging area (relative to project working directory, mirrors DB_PATH convention).
DRAFTS_DIR = Path("data/firm_drafts")

# firm_id must be a safe slug: lowercase alphanumeric, underscores, hyphens; no path separators.
_SAFE_FIRM_ID: re.Pattern[str] = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")


def _resolve_dir(drafts_dir: Path | str | None) -> Path:
    return Path(drafts_dir) if drafts_dir is not None else DRAFTS_DIR


def _validate_firm_id(firm_id: str) -> None:
    """Raise ValueError for firm_ids that could cause path traversal or shell injection."""
    if not isinstance(firm_id, str) or not _SAFE_FIRM_ID.match(firm_id):
        raise ValueError(
            f"Invalid firm_id {firm_id!r}. "
            "Must be lowercase alphanumeric with optional underscores/hyphens, 1–40 chars."
        )


def draft_path(firm_id: str, drafts_dir: Path | str | None = None) -> Path:
    """Return the canonical path for a draft file. Validates firm_id before constructing."""
    _validate_firm_id(firm_id)
    return _resolve_dir(drafts_dir) / f"{firm_id}.yaml"


def write_draft(
    profile: DraftFirmProfile,
    drafts_dir: Path | str | None = None,
) -> Path:
    """Write a DraftFirmProfile to YAML. Creates the directory if absent. Returns the path written."""
    path = draft_path(profile.firm_id, drafts_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            profile.model_dump(mode="json"),
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    return path


def read_draft(
    firm_id: str,
    drafts_dir: Path | str | None = None,
) -> DraftFirmProfile:
    """Load a DraftFirmProfile from YAML. Raises FileNotFoundError if missing."""
    path = draft_path(firm_id, drafts_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"No draft found for firm_id={firm_id!r}. Expected: {path}"
        )
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return DraftFirmProfile(**raw)


def list_drafts(drafts_dir: Path | str | None = None) -> list[str]:
    """Return sorted firm_ids of all YAML draft files in the drafts directory."""
    d = _resolve_dir(drafts_dir)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.yaml"))


# ── Approved firm SQLite sync ──────────────────────────────────────────────────

def sync_approved_firms(
    db: sqlite3.Connection,
    config_path: str | Path = "config/firms.yaml",
) -> int:
    """Upsert approved FirmProfile records from YAML into the SQLite firms table.

    Returns the number of firms successfully synced.
    Entries that do not validate as FirmProfile (e.g. legacy FirmConfig shape
    without an approval block) are skipped with a warning.
    Draft profiles are never synced — they live in data/firm_drafts/, not in
    config/firms.yaml.
    """
    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        logger.debug("sync_approved_firms: config file not found at %s — nothing to sync", config_path)
        return 0

    firms_raw = raw.get("firms", [])
    if not firms_raw:
        return 0

    count = 0
    for entry in firms_raw:
        if not isinstance(entry, dict):
            continue
        try:
            profile = FirmProfile(**entry)
        except Exception as exc:
            firm_id = entry.get("firm_id", "<unknown>")
            logger.warning("sync_approved_firms: skipping %r — not a valid FirmProfile: %s", firm_id, exc)
            continue
        _upsert_firm(db, profile)
        count += 1

    return count


def _upsert_firm(db: sqlite3.Connection, profile: FirmProfile) -> None:
    """Write one approved FirmProfile to the SQLite firms table via upsert.

    Preserves operational columns (circuit_state, quarantine_until,
    consecutive_failures, last_successful_fetch, last_fingerprinted, created_at)
    on update — only intelligence and ATS fields are refreshed.
    """
    benefits_dict = {k: v.model_dump(mode="json") for k, v in profile.benefits.items()}
    trajectory_dict = {k: v.model_dump(mode="json") for k, v in profile.trajectory.items()}

    known_benefit_keys = [
        k for k, v in profile.benefits.items()
        if v.status in ("confirmed", "likely")
    ]
    tuition_reimb = int(
        "tuition_reimbursement" in profile.benefits
        and profile.benefits["tuition_reimbursement"].status in ("confirmed", "likely")
    )
    pe_support = int(
        any(
            k in profile.benefits and profile.benefits[k].status in ("confirmed", "likely")
            for k in ("pe_exam_reimbursement", "pe_prep_reimbursement")
        )
    )

    db.execute(
        """
        INSERT INTO firms (
            firm_id, name, website, careers_url,
            ats_type, ats_tier, ats_board_token, ats_tenant, ats_site,
            enr_rank, employee_count, specialties, known_benefits,
            tuition_reimbursement, pe_support, reputation_notes,
            aliases, benefits_json, trajectory_json, manual_priority, last_verified
        ) VALUES (
            :firm_id, :name, :website, :careers_url,
            :ats_type, :ats_tier, :ats_board_token, :ats_tenant, :ats_site,
            :enr_rank, :employee_count, :specialties, :known_benefits,
            :tuition_reimbursement, :pe_support, :reputation_notes,
            :aliases, :benefits_json, :trajectory_json, :manual_priority, :last_verified
        )
        ON CONFLICT(firm_id) DO UPDATE SET
            name                 = excluded.name,
            website              = excluded.website,
            careers_url          = excluded.careers_url,
            ats_type             = excluded.ats_type,
            ats_tier             = excluded.ats_tier,
            ats_board_token      = excluded.ats_board_token,
            ats_tenant           = excluded.ats_tenant,
            ats_site             = excluded.ats_site,
            enr_rank             = excluded.enr_rank,
            employee_count       = excluded.employee_count,
            specialties          = excluded.specialties,
            known_benefits       = excluded.known_benefits,
            tuition_reimbursement = excluded.tuition_reimbursement,
            pe_support           = excluded.pe_support,
            reputation_notes     = excluded.reputation_notes,
            aliases              = excluded.aliases,
            benefits_json        = excluded.benefits_json,
            trajectory_json      = excluded.trajectory_json,
            manual_priority      = excluded.manual_priority,
            last_verified        = excluded.last_verified,
            updated_at           = datetime('now')
        """,
        {
            "firm_id":              profile.firm_id,
            "name":                 profile.name,
            "website":              profile.website,
            "careers_url":          profile.careers_url,
            "ats_type":             profile.ats.type.value,
            "ats_tier":             profile.ats.tier.value,
            "ats_board_token":      profile.ats.board_token,
            "ats_tenant":           profile.ats.tenant,
            "ats_site":             profile.ats.site,
            "enr_rank":             profile.profile.enr_rank,
            "employee_count":       profile.profile.employee_count,
            "specialties":          json.dumps(profile.profile.disciplines),
            "known_benefits":       json.dumps(known_benefit_keys),
            "tuition_reimbursement": tuition_reimb,
            "pe_support":           pe_support,
            "reputation_notes":     profile.notes.reputation or None,
            "aliases":              json.dumps(profile.aliases),
            "benefits_json":        json.dumps(benefits_dict),
            "trajectory_json":      json.dumps(trajectory_dict),
            "manual_priority":      profile.manual_priority.value,
            "last_verified":        profile.approval.last_verified,
        },
    )
