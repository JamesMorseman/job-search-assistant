"""Safe ATLAS Desktop runtime/config status read model.

This service exposes presence/status only. It never returns secret values,
absolute private paths, profile contents, token contents, or environment
values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from job_search.config import settings
from job_search.diagnostics import check_database_connectivity, check_openai_api_key


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class RuntimeCheck(BaseModel):
    name: str
    status: str
    detail: str
    severity: str


class RuntimeCommand(BaseModel):
    label: str
    command: str
    purpose: str


class RuntimeConfigStatus(BaseModel):
    generated_at: str
    checks: list[RuntimeCheck]
    launch_commands: list[RuntimeCommand]
    data_protection_path: str
    desktop_update_path: list[str]
    tauri_wrapper_status: str


class RuntimeStatusService:
    """Build the read-only Settings/About status payload for ATLAS Desktop."""

    def get_config_status(self) -> RuntimeConfigStatus:
        return RuntimeConfigStatus(
            generated_at=_now_iso(),
            checks=[
                self._diagnostic_check(check_database_connectivity(), severity="required"),
                self._diagnostic_check(check_openai_api_key(), severity="required"),
                self._candidate_profile_check(),
                self._frontend_build_check(),
                self._launcher_script_check(),
                self._backup_command_check(),
            ],
            launch_commands=[
                RuntimeCommand(
                    label="ATLAS Desktop",
                    command=r"powershell -ExecutionPolicy Bypass -File .\scripts\start-atlas.ps1",
                    purpose="Runs diagnostics, starts the local FastAPI server, and serves /atlas.",
                ),
                RuntimeCommand(
                    label="Frontend build",
                    command="cd frontend; npm run build",
                    purpose="Refreshes the static ATLAS Desktop bundle served by FastAPI.",
                ),
                RuntimeCommand(
                    label="Local backup",
                    command="jsa backup",
                    purpose="Creates a timestamped local backup before risky local work.",
                ),
            ],
            data_protection_path="output/backups/<timestamp>/",
            desktop_update_path=[
                "Switch to the approved local branch or pull the approved update.",
                "Run npm run build from frontend/ when frontend files changed.",
                "Run jsa check before launching ATLAS Desktop.",
                r"Launch with scripts\start-atlas.ps1 and open http://127.0.0.1:8000/atlas.",
            ],
            tauri_wrapper_status=(
                "Architecture documented in docs/Architecture/desktop_launch_tauri_spec.md; "
                "native packaging/updater remain separately gated."
            ),
        )

    @staticmethod
    def _diagnostic_check(result, *, severity: str) -> RuntimeCheck:
        if result.name == "DB_PATH":
            detail = (
                "database is reachable"
                if result.status == "pass"
                else "database is not reachable; run jsa check locally for path-specific detail"
            )
        else:
            detail = result.detail
        return RuntimeCheck(
            name=result.name,
            status=result.status,
            detail=detail,
            severity=severity,
        )

    @staticmethod
    def _candidate_profile_check() -> RuntimeCheck:
        present = Path(settings.PROFILE_PATH).is_file()
        return RuntimeCheck(
            name="candidate profile",
            status="pass" if present else "fail",
            detail=(
                "configured candidate profile is present"
                if present
                else "missing - copy the profile template locally before generating drafts"
            ),
            severity="required",
        )

    @staticmethod
    def _frontend_build_check() -> RuntimeCheck:
        present = Path("frontend/dist/index.html").is_file()
        return RuntimeCheck(
            name="ATLAS Desktop bundle",
            status="pass" if present else "warn",
            detail=(
                "frontend/dist/index.html is present"
                if present
                else "frontend build output is missing - run npm run build from frontend/"
            ),
            severity="recommended",
        )

    @staticmethod
    def _launcher_script_check() -> RuntimeCheck:
        present = Path("scripts/start-atlas.ps1").is_file()
        return RuntimeCheck(
            name="local launcher",
            status="pass" if present else "fail",
            detail=(
                "scripts/start-atlas.ps1 is present"
                if present
                else "scripts/start-atlas.ps1 is missing"
            ),
            severity="required",
        )

    @staticmethod
    def _backup_command_check() -> RuntimeCheck:
        return RuntimeCheck(
            name="backup/export path",
            status="pass",
            detail="jsa backup writes local copies under output/backups/<timestamp>/",
            severity="recommended",
        )
