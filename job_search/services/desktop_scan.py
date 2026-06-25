"""ATLAS Desktop scan status and explicit sweep trigger service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from job_search.config import settings
from job_search.diagnostics import check_database_connectivity, check_openai_api_key
from job_search.pipeline import PipelineRunner, PipelineRunResult
from job_search.pipeline.runner import RUN_TYPES
from job_search.services.pipeline import PipelineRun, PipelineService


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class ScanRequestError(Exception):
    """Raised when a desktop scan request is invalid or blocked by setup."""


class ScanCheck(BaseModel):
    name: str
    status: str
    detail: str
    severity: str


class ScanStep(BaseModel):
    name: str
    status: str
    stats: dict[str, Any]
    error: str | None = None
    error_count: int = 0


class RunSweepRequest(BaseModel):
    run_type: str = "full"
    dry_run: bool = True


class RunSweepResponse(BaseModel):
    status: str
    message: str
    run_type: str
    dry_run: bool
    run_id: int | None
    steps: list[ScanStep]
    checks: list[ScanCheck]
    latest_run: PipelineRun | None


class ScanStatus(BaseModel):
    generated_at: str
    latest_run: PipelineRun | None
    checks: list[ScanCheck]
    allowed_run_types: list[str]


class AtlasScanService:
    """Wrap PipelineRunner for the ATLAS Desktop Run Sweep control."""

    def __init__(self, pipeline_service: PipelineService | None = None):
        self._pipeline_service = pipeline_service or PipelineService()

    def get_status(self) -> ScanStatus:
        return ScanStatus(
            generated_at=_now_iso(),
            latest_run=self._latest_run(),
            checks=self._checks(run_type="full", dry_run=True),
            allowed_run_types=sorted(RUN_TYPES),
        )

    def run_sweep(self, run_type: str = "full", dry_run: bool = True) -> RunSweepResponse:
        if run_type not in RUN_TYPES:
            raise ScanRequestError(
                f"Unsupported run_type {run_type!r}; expected one of {sorted(RUN_TYPES)}"
            )

        checks = self._checks(run_type=run_type, dry_run=dry_run)
        blockers = [check for check in checks if check.status == "fail" and check.severity == "required"]
        if blockers:
            return RunSweepResponse(
                status="blocked",
                message="Run Sweep is blocked by required local setup checks.",
                run_type=run_type,
                dry_run=dry_run,
                run_id=None,
                steps=[],
                checks=checks,
                latest_run=self._latest_run(),
            )

        try:
            result = PipelineRunner(pipeline_service=self._pipeline_service).run(
                run_type=run_type,
                dry_run=dry_run,
                trigger="atlas_desktop",
            )
        except Exception as exc:
            return RunSweepResponse(
                status="failed",
                message=f"Run Sweep failed before completion: {exc}",
                run_type=run_type,
                dry_run=dry_run,
                run_id=None,
                steps=[],
                checks=checks,
                latest_run=self._latest_run(),
            )

        return RunSweepResponse(
            status=result.status,
            message=self._message_for_result(result),
            run_type=result.run_type,
            dry_run=result.dry_run,
            run_id=result.run_id,
            steps=[
                ScanStep(
                    name=step.name,
                    status=step.status,
                    stats=step.stats,
                    error=step.error,
                    error_count=step.error_count,
                )
                for step in result.steps
            ],
            checks=checks,
            latest_run=self._latest_run(),
        )

    def _latest_run(self) -> PipelineRun | None:
        return next(iter(self._pipeline_service.list_recent_runs(limit=1)), None)

    def _checks(self, *, run_type: str, dry_run: bool) -> list[ScanCheck]:
        checks = [
            self._diagnostic_check(check_database_connectivity(), severity="required"),
            self._diagnostic_check(check_openai_api_key(), severity=self._openai_severity(run_type, dry_run)),
            self._candidate_profile_check(severity=self._profile_severity(run_type, dry_run)),
        ]
        if dry_run:
            checks.append(
                ScanCheck(
                    name="dry run",
                    status="pass",
                    detail="writes are avoided where the underlying step supports dry-run; unsupported write steps are skipped",
                    severity="info",
                )
            )
        return checks

    @staticmethod
    def _diagnostic_check(result, *, severity: str) -> ScanCheck:
        if result.name == "DB_PATH":
            detail = (
                "database is reachable"
                if result.status == "pass"
                else "database is not reachable; run jsa check locally for path-specific detail"
            )
        else:
            detail = result.detail
        return ScanCheck(name=result.name, status=result.status, detail=detail, severity=severity)

    @staticmethod
    def _candidate_profile_check(*, severity: str) -> ScanCheck:
        present = Path(settings.PROFILE_PATH).is_file()
        return ScanCheck(
            name="candidate profile",
            status="pass" if present else "fail",
            detail=(
                "configured candidate profile is present"
                if present
                else "missing - copy the profile template locally before generating drafts"
            ),
            severity=severity,
        )

    @staticmethod
    def _openai_severity(run_type: str, dry_run: bool) -> str:
        if dry_run:
            return "recommended"
        return "required" if run_type in {"full", "grade", "generate"} else "recommended"

    @staticmethod
    def _profile_severity(run_type: str, dry_run: bool) -> str:
        if dry_run:
            return "recommended"
        return "required" if run_type in {"full", "generate"} else "recommended"

    @staticmethod
    def _message_for_result(result: PipelineRunResult) -> str:
        if result.status == "dry_run":
            return "Run Sweep dry-run completed; skipped steps did not write local records."
        if result.status == "complete":
            return "Run Sweep completed successfully."
        if result.status == "failed":
            return "Run Sweep completed with step errors; review the step list before retrying."
        return f"Run Sweep finished with status {result.status}."
