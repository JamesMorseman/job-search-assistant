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

from datetime import date

from job_search.models import DraftFirmProfile, DraftStatus, FirmApproval, FirmProfile

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


# ── Approved firms YAML I/O ────────────────────────────────────────────────────

_DEFAULT_CONFIG = Path("config/firms.yaml")


def load_firms_yaml(config_path: str | Path = _DEFAULT_CONFIG) -> list[dict]:
    """Return the raw list of firm dicts from config/firms.yaml, or [] if missing."""
    try:
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return raw.get("firms", [])
    except FileNotFoundError:
        return []


def save_firms_yaml(firms: list[dict], config_path: str | Path = _DEFAULT_CONFIG) -> None:
    """Overwrite config/firms.yaml with the given list of firm dicts.

    Uses yaml.dump with model-serialised dicts so no Python-specific tags appear.
    Preserves YAML key order (sort_keys=False).
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            {"firms": firms},
            fh,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


# ── Review and approval workflow ───────────────────────────────────────────────

class DraftNotFoundError(FileNotFoundError):
    """Raised when a draft file does not exist for the given firm_id."""


class DraftStatusError(ValueError):
    """Raised when a draft is not in the expected status for the requested operation."""


def approve_draft(
    firm_id: str,
    approved_by: str,
    last_verified: str | None = None,
    *,
    drafts_dir: Path | str | None = None,
    config_path: str | Path = _DEFAULT_CONFIG,
    db: sqlite3.Connection | None = None,
) -> FirmProfile:
    """Promote a pending draft to an approved FirmProfile.

    Workflow:
    1. Read the draft; raise DraftNotFoundError if absent.
    2. Raise DraftStatusError if not PENDING_REVIEW.
    3. Build a FirmProfile with a new FirmApproval block.
    4. Upsert the profile into config/firms.yaml (by firm_id).
    5. Mark the draft file as APPROVED (preserves evidence trail).
    6. If a db connection is provided, call sync_approved_firms() to keep
       SQLite current.

    Returns the approved FirmProfile.
    """
    _validate_firm_id(firm_id)

    # 1. Load draft
    path = draft_path(firm_id, drafts_dir)
    if not path.exists():
        raise DraftNotFoundError(f"No draft found for firm_id={firm_id!r}. Expected: {path}")
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    draft = DraftFirmProfile(**raw)

    # 2. Status guard
    if draft.draft_status != DraftStatus.PENDING_REVIEW:
        raise DraftStatusError(
            f"Draft {firm_id!r} has status {draft.draft_status.value!r}; "
            "only pending_review drafts can be approved."
        )

    # 3. Build FirmProfile
    today = date.today().isoformat()
    approval = FirmApproval(
        approved_at=today,
        approved_by=approved_by,
        last_verified=last_verified or today,
    )
    profile_data = draft.model_dump(mode="json", exclude={"draft_status", "generated_at",
                                                           "generator_version", "review",
                                                           "evidence_summary"})
    profile_data["approval"] = approval.model_dump(mode="json")
    profile = FirmProfile(**profile_data)  # validates vocab keys + approval

    # 4. Upsert into config/firms.yaml
    existing = load_firms_yaml(config_path)
    profile_dict = profile.model_dump(mode="json")
    updated = [f for f in existing if f.get("firm_id") != firm_id]
    updated.append(profile_dict)
    save_firms_yaml(updated, config_path)

    # 5. Mark draft as APPROVED (preserve evidence trail)
    draft.draft_status = DraftStatus.APPROVED
    draft.review.approved = True
    draft.review.approved_at = today
    draft.review.approved_by = approved_by
    write_draft(draft, drafts_dir)

    # 6. Sync SQLite if connection provided
    if db is not None:
        _upsert_firm(db, profile)

    logger.info("approve_draft: %r approved by %s; synced to config/firms.yaml", firm_id, approved_by)
    return profile


def reject_draft(
    firm_id: str,
    reviewer_notes: str = "",
    *,
    drafts_dir: Path | str | None = None,
) -> DraftFirmProfile:
    """Mark a draft as REJECTED.

    The draft YAML file is preserved with its evidence intact.
    The status is changed to 'rejected' and the reviewer_notes appended.
    Returns the updated DraftFirmProfile.
    """
    _validate_firm_id(firm_id)

    path = draft_path(firm_id, drafts_dir)
    if not path.exists():
        raise DraftNotFoundError(f"No draft found for firm_id={firm_id!r}. Expected: {path}")
    with path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    draft = DraftFirmProfile(**raw)

    if draft.draft_status == DraftStatus.APPROVED:
        raise DraftStatusError(
            f"Draft {firm_id!r} is already approved; rejection is not permitted."
        )

    draft.draft_status = DraftStatus.REJECTED
    if reviewer_notes:
        draft.review.reviewer_notes.append(reviewer_notes)
    write_draft(draft, drafts_dir)

    logger.info("reject_draft: %r marked rejected", firm_id)
    return draft


# ── Skeleton draft generation ──────────────────────────────────────────────────

# Non-alphanumeric run → underscore (same logic as discovery._make_firm_id_slug,
# kept local to avoid cross-module coupling inside the firms package).
_SLUG_NON_ALNUM: re.Pattern[str] = re.compile(r"[^a-z0-9]+")


def _company_to_firm_id(name: str) -> str:
    """Derive a safe firm_id slug from a company name."""
    slug = _SLUG_NON_ALNUM.sub("_", name.lower()).strip("_")[:40]
    return slug or "unknown"


class DraftExistsError(FileExistsError):
    """Raised when a draft file already exists and force=False."""


def create_draft(
    company_name: str,
    *,
    firm_id: str | None = None,
    website: str | None = None,
    careers_url: str | None = None,
    drafts_dir: Path | str | None = None,
    force: bool = False,
) -> tuple[DraftFirmProfile, Path]:
    """Generate a skeleton DraftFirmProfile and write it to the drafts directory.

    firm_id is derived from company_name if not provided.
    Benefits and trajectory are left empty; the human reviewer fills them in
    (or a future LLM extraction step populates them before review).

    Raises DraftExistsError if a draft already exists and force is False.
    Returns (draft, path_written).
    """
    if firm_id is None:
        firm_id = _company_to_firm_id(company_name)
    _validate_firm_id(firm_id)

    path = draft_path(firm_id, drafts_dir)
    if path.exists() and not force:
        raise DraftExistsError(
            f"Draft already exists for {firm_id!r} at {path}. "
            "Pass force=True / --force to overwrite."
        )

    draft = DraftFirmProfile(
        firm_id=firm_id,
        name=company_name,
        draft_status=DraftStatus.PENDING_REVIEW,
        generated_at=date.today().isoformat(),
        generator_version="skeleton-v1",
        website=website,
        careers_url=careers_url,
    )
    written = write_draft(draft, drafts_dir)
    logger.info("create_draft: skeleton draft written for %r at %s", firm_id, written)
    return draft, written
