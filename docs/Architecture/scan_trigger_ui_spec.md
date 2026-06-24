# Scan Trigger UI — Scope Note / Implementation Spec

## Metadata

- Document ID: `B1_SCAN_TRIGGER_UI_SPEC_DOC_01`
- Package: `B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01`
- Status: soft-blocked for a real write-trigger implementation in this pass;
  bounded spec only. **No scan-trigger code was written.** This document
  does not authorize implementation, only scopes it for a future package.
- Owner: Main Ash / user (James)
- Authored by: Anna Repo Agent, away-run implementation pass

---

## 1. Why This Is Scoped, Not Implemented

The package instruction explicitly allows scoping instead of implementing
"if the service boundary is unclear or implementing a real trigger is too
risky for this scope." That condition is met here for reasons verified live
in this pass, not assumed from the roadmap:

1. **`PipelineService` is the correct, already-existing write boundary** for
   `pipeline_runs` (confirmed: `job_search/services/pipeline.py`'s own
   docstring states it is "the sole authorized write path for pipeline_runs
   records," and `PipelineRunner` in `job_search/pipeline/runner.py` already
   respects that boundary — it never writes to `pipeline_runs` directly).
   So the boundary itself is *not* the blocker.
2. **The real blocker is what's behind that boundary.** `PipelineRunner.run()`
   executes `Ingestor.run()` (live USAJOBS/Adzuna/ATS network calls),
   `FitGrader.run()` (live OpenAI LLM calls — real cost per call),
   `DailyReporter.run()` (Google Sheets write), `SelectionProcessor
   .generate_for_selected()` (document generation, possibly more LLM calls),
   and `FollowUpEngine.run()`. A "Scan Now" button wired directly to this
   would mean an HTTP request from the ATLAS Desktop UI triggers real,
   possibly-costly external API calls and a Google Sheets write — not a
   contained local DB read.
3. **No background-job infrastructure exists anywhere in this backend**
   (verified via repo-wide grep: no `BackgroundTasks` usage, no Celery, no
   `asyncio.create_task`/`ThreadPoolExecutor` pattern for long-running work).
   `FastAPI.BackgroundTasks` is available as a dependency (`fastapi` is
   already a direct dependency) but is not currently used anywhere in this
   codebase, so adopting it for the first time here would be a real
   architectural addition, not a wiring task.
4. **No existing auth/rate-limiting on the dashboard.** Any locally-running
   ATLAS Desktop instance currently has unauthenticated access to all
   `/dashboard` and `/atlas/api` routes. A trigger that costs real money per
   click (LLM calls) with no confirmation/rate-limit step is a real product
   and cost-safety risk, not just an engineering nuance.
5. **The existing CLI path (`jsa run`) already has a `--dry-run` flag** and
   is the only currently-supported way to execute a full or partial pipeline
   pass. This spec's recommended approach treats the CLI path as the
   continuing source of truth for triggering, not something to bypass.

None of this means a trigger UI is permanently out of scope for Build 1 — it
means this specific away-run pass is the wrong place to introduce new
async-execution and cost-control infrastructure as a side effect of a
"surface an existing read-only path" package.

---

## 2. What Already Exists (Confirmed Live, This Pass)

- **Read-only "Scan Status" already exists and is fully landed**: ATLAS
  Desktop's Pipeline workspace (`frontend/src/workspaces/Pipeline.tsx`)
  renders recent `pipeline_runs` history via `GET /atlas/api/pipeline/runs`
  (`job_search/dashboard/routes/atlas_api.py`,
  `PipelineService.list_recent_runs()`). This already satisfies the
  "Scan Status" half of the C03 backlog item
  (`docs/Architecture/build_1_completion_roadmap.md` Section 7, row C03/C04).
- **No trigger affordance of any kind exists in `Pipeline.tsx`** — confirmed
  via direct read: no buttons, no form, no client call to any
  write-capable endpoint. The workspace is purely a historical/status view.
- **CLI trigger already exists**: `jsa run [--dry-run] [run_type]` via
  `job_search/cli.py` → `PipelineRunner.run()`. This remains the only
  supported way to actually start a pipeline pass today.

---

## 3. Recommended Implementation Path For A Future Package

In priority order, lowest-risk first:

### 3.1 Minimum viable: "Run a dry-run preview" button (lower risk, but not zero)

`PipelineRunner().run(run_type="full", dry_run=True, trigger="atlas-ui")`
skips the **database upsert** step for ingest (confirmed:
`Ingestor.run()` still calls `self._iter_all_sources(db)` — which fetches
live from USAJOBS/Adzuna/ATS adapters regardless of `dry_run` — and only
the final `dedup.upsert(job)` call is skipped when `dry_run=True`). **This
is a real correction to an earlier draft of this document, which incorrectly
stated dry-run makes no external network calls — it does.** Dry-run is
genuinely a no-database-write preview, not a no-network-call preview.
`grade` is the only other `DRY_RUN_CAPABLE_STEPS` member. Verified directly
in this pass: `FitGrader.run(dry_run=True)` (`job_search/grading/grader.py`)
never calls `submit_batch()` (the new-LLM-call path) when `dry_run=True` —
it returns early at the point requests are built, before submission. *But*
it still unconditionally calls `self.drain_prior(db)` first, and
`drain_prior()` calls `self.llm.retrieve_batch_status(bid)` for any
still-`submitted` prior batch — **a real LLM provider API call** (checking
an existing batch's status, not creating a new one) — and can write via
`self._mark_batch(db, bid, ...)` if that batch turned out failed/expired/
cancelled. So `grade`'s dry-run mode is "no new grading cost" but is not
fully side-effect-free either, if a prior batch is still pending.
`report`/`generate`/`followup` are NOT in `DRY_RUN_CAPABLE_STEPS` and are
skipped entirely under dry_run (no execution at all, per
`PipelineRunner._run_dry`).

So a "dry-run preview" button would still: (a) make live USAJOBS/Adzuna/ATS
network calls every time (free APIs, but real outbound requests against
rate-limited/ToS-bound third-party services), and (b) potentially make a
real LLM API call and a DB write *only if* a prior grading batch is still
in `submitted` status when the button is clicked — an edge case, not the
common path, but a real one. This is meaningfully lower-risk than a full
real run (no new-grading cost, no Sheets write, no ingest-table mutation)
but is not fully risk-free or fully side-effect-free. A future package
should treat "dry-run" as "safer," not "guaranteed free/no-op."

### 3.2 Real trigger, explicitly gated (medium-to-high risk, needs governance)

A real (non-dry-run) trigger needs, at minimum, before implementation:

1. **Async execution** — `FastAPI.BackgroundTasks` (already available, zero
   new dependencies) wrapping `PipelineRunner().run(...)`, so the HTTP
   request returns immediately with a `run_id` and the UI polls
   `GET /atlas/api/pipeline/runs/{run_id}` (a new single-run read endpoint;
   `PipelineService.get_run()` already exists for this) for status, rather
   than blocking the request for the full pipeline duration.
2. **An explicit confirmation step in the UI** before any non-dry-run
   trigger, given the real LLM cost per grading call.
3. **A cooldown/rate-limit** (e.g. "one real run per N minutes") to prevent
   accidental repeated-click cost — this does not exist anywhere today and
   would need new state, likely in `pipeline_runs` itself (last `started_at`
   check) rather than a new table.
4. **A governance decision** on whether unauthenticated local UI access is
   an acceptable trigger surface for a real-money action, or whether some
   confirmation/lock step is required first. This is a product/safety
   decision, not a pure engineering one — flagged for Donut/Leah review
   before a future package implements 3.2.

### 3.3 Explicitly out of scope for any near-term package

- A scheduler/cron-like "run automatically every N hours" feature — this
  compounds the cost/safety concerns above and is not part of the current
  Build 1 backlog item (C03 is about manual on-demand triggering, not
  scheduling).
- Multi-run concurrency handling (what happens if a user clicks "Scan Now"
  while a run is already in progress) — needs its own design once 3.2 is
  real; not addressed here.

---

## 4. Explicitly Not Claimed By This Document

- No endpoint, button, or background-task code was added by this package.
- No claim that the C03 backlog item ("Run Sweep / Scan Now / Scan Status")
  is closed — "Scan Status" (read-only history) is landed; "Scan Now"
  (an actual trigger) remains an open, scoped-not-implemented gap.
- No governance/cost/safety decision is made here — Section 3.2's open
  questions are flagged for a future, explicitly authorized package and/or
  Donut/Leah review, not resolved by this document.
