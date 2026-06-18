"""Phase 6 Package 4 -- local-first background pipeline runner.

Wraps the existing pipeline steps (ingest, grade, daily report, generate,
follow-up scan) in a durable execution layer. Every real run produces a
`pipeline_runs` record through `PipelineService` -- the sole authorized
write path for that table.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from job_search.grading import FitGrader
from job_search.ingestion import Ingestor
from job_search.reporting import DailyReporter, SelectionProcessor
from job_search.services.pipeline import PipelineService
from job_search.tracking import FollowUpEngine

STEP_ORDER = ["ingest", "grade", "report", "generate", "followup"]
RUN_TYPES = {"full", *STEP_ORDER}

# Steps with no native dry-run support: skipped during a dry run rather than
# executed, since they would otherwise write to the database unconditionally.
DRY_RUN_CAPABLE_STEPS = {"ingest", "grade"}


@dataclass
class StepOutcome:
    name: str
    status: str  # "ok" | "error" | "skipped"
    stats: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    error_count: int = 0


@dataclass
class PipelineRunResult:
    run_id: int | None
    run_type: str
    status: str  # "complete" | "failed" | "dry_run"
    dry_run: bool
    steps: list[StepOutcome] = field(default_factory=list)

    @property
    def errors(self) -> list[StepOutcome]:
        return [s for s in self.steps if s.status == "error"]


class PipelineRunner:
    """Orchestrates the existing local pipeline steps in sequence.

    `PipelineService` remains the sole authorized write path for
    `pipeline_runs`; this class never writes to that table directly.
    """

    def __init__(self, pipeline_service: PipelineService | None = None):
        self._pipeline_service = pipeline_service or PipelineService()

    def run(
        self,
        run_type: str = "full",
        *,
        dry_run: bool = False,
        trigger: str = "cli",
        source: str | None = None,
    ) -> PipelineRunResult:
        if run_type not in RUN_TYPES:
            raise ValueError(
                f"Unsupported run_type {run_type!r}; expected one of {sorted(RUN_TYPES)}"
            )
        steps_to_run = STEP_ORDER if run_type == "full" else [run_type]

        if dry_run:
            return self._run_dry(run_type, steps_to_run)

        run_id = self._pipeline_service.start_run(run_type, source=source, trigger=trigger)
        steps = [self._execute_step(name) for name in steps_to_run]
        counters = self._aggregate_counters(steps)
        self._pipeline_service.update_counters(run_id, **counters)

        if any(s.status == "error" for s in steps):
            self._pipeline_service.fail_run(
                run_id,
                error_detail=json.dumps(
                    [{"step": s.name, "error": s.error} for s in steps if s.status == "error"]
                ),
                metadata={"steps": {s.name: s.stats for s in steps}},
            )
            status = "failed"
        else:
            self._pipeline_service.complete_run(
                run_id, metadata={"steps": {s.name: s.stats for s in steps}}
            )
            status = "complete"

        return PipelineRunResult(
            run_id=run_id, run_type=run_type, status=status, dry_run=False, steps=steps
        )

    def _run_dry(self, run_type: str, steps_to_run: list[str]) -> PipelineRunResult:
        outcomes = []
        for name in steps_to_run:
            if name in DRY_RUN_CAPABLE_STEPS:
                outcomes.append(self._execute_step(name, dry_run=True))
            else:
                outcomes.append(
                    StepOutcome(
                        name=name,
                        status="skipped",
                        stats={
                            "reason": "no native dry-run support; skipped to avoid database writes"
                        },
                    )
                )
        return PipelineRunResult(
            run_id=None, run_type=run_type, status="dry_run", dry_run=True, steps=outcomes
        )

    def _execute_step(self, name: str, *, dry_run: bool = False) -> StepOutcome:
        try:
            if name == "ingest":
                ingestor = Ingestor(dry_run=dry_run)
                ingestor.load_firms()
                stats = ingestor.run()
            elif name == "grade":
                stats = FitGrader().run(dry_run=dry_run)
            elif name == "report":
                stats = DailyReporter().run()
            elif name == "generate":
                stats = SelectionProcessor().generate_for_selected()
            elif name == "followup":
                actions = FollowUpEngine().run()
                stats = {"due_actions": len(actions)}
            else:
                raise ValueError(f"Unknown pipeline step {name!r}")
        except Exception as exc:
            return StepOutcome(name=name, status="error", error=str(exc), error_count=1)

        error_count = self._step_error_count(name, stats)
        if error_count > 0:
            return StepOutcome(
                name=name,
                status="error",
                stats=stats,
                error=f"{error_count} recoverable error(s) reported by the '{name}' step",
                error_count=error_count,
            )
        return StepOutcome(name=name, status="ok", stats=stats)

    @staticmethod
    def _step_error_count(name: str, stats: dict[str, Any]) -> int:
        if name == "grade":
            return len(stats.get("batch_errors") or [])
        return int(stats.get("errors", 0) or 0)

    @staticmethod
    def _aggregate_counters(steps: list[StepOutcome]) -> dict[str, int]:
        jobs_seen = jobs_created = jobs_updated = jobs_presented = errors_count = 0
        for step in steps:
            stats = step.stats
            if step.name == "ingest":
                jobs_created += stats.get("new", 0) or 0
                jobs_updated += stats.get("updated", 0) or 0
                jobs_seen += (
                    (stats.get("new", 0) or 0)
                    + (stats.get("updated", 0) or 0)
                    + (stats.get("reposts", 0) or 0)
                )
            elif step.name == "report":
                jobs_presented += stats.get("presented", 0) or 0
            errors_count += step.error_count
        return {
            "jobs_seen": jobs_seen,
            "jobs_created": jobs_created,
            "jobs_updated": jobs_updated,
            "jobs_presented": jobs_presented,
            "errors_count": errors_count,
        }
