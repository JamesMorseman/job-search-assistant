"""Firm repository — draft file I/O.

Approved firm profiles live in config/firms.yaml.
Draft profiles live in data/firm_drafts/<firm_id>.yaml.

Drafts are never loaded by ingestion, scoring, or approved-firm paths.
Only write_draft / read_draft / list_drafts touch the draft directory.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from job_search.models import DraftFirmProfile

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
