# Phase 6 Product & Operations Assessment

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** Evaluating Phase 6 work from a product, workflow, and operator perspective. Covers current workflow friction, Phase 6 user goals, pipeline visibility, Source Health, deferred package sequencing, and a Phase 7 UX backlog.

**Key grounding finding:** Phase 6 is not starting from scratch on pipeline data. The `source_health` table already exists in `schema.sql` with a rich schema (status, error_class, error_detail, heal_action, old_config/new_config snapshots). The `grading_batches` table tracks LLM batch state. The `daily_reports` table records when reports ran and which jobs were presented. `firms.circuit_state` and `firms.quarantine_until` implement circuit breaking at the data layer. A `healing/circuit_breaker.py` module exists. What Phase 6 is building is primarily **dashboard surfaces over data that already largely exists**, plus the `pipeline_runs` orchestration layer and background runner that do not yet exist.

---

## 1. Current Workflow Analysis

### 1.1 Ingest

**Operation:** `jsa ingest` → `Ingestor.run()` → writes to `jobs`, updates `source_health`

**What happens silently:** Every ingest run writes per-source outcomes to `source_health` — status (`ok|empty|error|quarantined`), records_fetched count, error_class, and error_detail. The circuit breaker (`healing/circuit_breaker.py`) tracks consecutive failures and can quarantine a firm, setting `firms.circuit_state = 'open'` and populating `firms.quarantine_until`. Quarantined firms are silently skipped on subsequent runs.

**Operator experience:** None of this is visible from the dashboard. The CLI outputs stats to the terminal, but those stats evaporate after the session. A cron-run ingest has completely invisible outcomes — the operator has no way to know whether any source succeeded, failed, or is quarantined without running a direct DB query or reading log files. A source that has been failing silently for two weeks still allows the operator to use Review Queue normally (jobs from other sources still appear), so the failure is easy to miss indefinitely.

**Friction:** The complete absence of a dashboard surface for data that is already being collected on every run. No additional instrumentation is needed — the data exists, the surface does not.

### 1.2 Grading

**Operation:** `jsa grade` → `FitGrader.run()` → uses `grading_batches` table

**What happens:** The `grading_batches` table tracks batch submissions to the LLM provider (batch_id, status, job_count, submitted_at, completed_at). `GRADING_POLL_TIMEOUT_S = 900` — a run can wait up to 15 minutes for batch completion. If grading times out before the batch completes, the batch is left in `submitted` state and "drained on next run" per the schema comment — the system avoids paying twice for the same batch.

**Operator experience:** No dashboard visibility into grading batch status. The operator cannot tell from the dashboard whether grading ran today, how many jobs were graded, whether any batches are in `submitted`-but-incomplete state, or whether a specific job's lack of an LLM grade is because grading hasn't run yet or because it was filtered out.

**Friction:** `grading_batches` already contains the data to answer "did grading run, and did it finish?" No new instrumentation needed for basic visibility.

### 1.3 Presentation / Report

**Operation:** `jsa report` → `DailyReporter.run()` → writes to `daily_reports`, transitions qualifying jobs to `presented`

**What happens:** The `daily_reports` table records when each report ran, which job IDs were presented, and a Drive file ID for the report document. The presentation threshold (`GRADING_FLOOR = 0.55`) filters jobs silently — jobs below the threshold are in the DB but never appear in Review Queue.

**Operator experience:** No dashboard surface for report history. An operator cannot see when the last report ran, how many jobs were presented vs. filtered, or whether a specific job is missing from Review Queue because it scored below the threshold or because ingest hasn't run yet. `daily_reports` already records this history; it is simply not surfaced.

**Friction:** A user who sees an empty Review Queue has no way to diagnose why — whether ingest hasn't run, whether grading is still pending, whether all jobs scored below threshold, or whether the right adapters are enabled. Each of these has a different remedy, and currently the operator must investigate all of them manually.

### 1.4 Document Generation

**Operation:** `jsa generate` or dashboard Documents screen → `SelectionProcessor.generate_for_selected()` → writes to `generated_docs`

**Current state:** This is the most complete workflow in the system. The Documents screen (Phase 5 Package 4a/4b) surfaces generation history, keyword coverage, and the regenerate action. Document generation has a dashboard surface.

**Remaining friction:** Generation is synchronous — a regeneration request blocks the request/response cycle during execution. For a single job this is acceptable; for a batch of selected jobs, it can be slow. This becomes a Phase 6 concern when the dashboard needs to trigger generation as a pipeline action across multiple jobs without blocking.

### 1.5 Application Tracking

**Operation:** Dashboard Application Tracker + Review Queue select/reject; CLI `jsa update-state`, `jsa apply`

**Current state:** The most complete workflow in the dashboard. State transitions are available from both surfaces, the state machine is enforced uniformly through `TrackerService.transition_job()`, and full state history is available on Job Detail.

**Remaining friction:**
- `jsa sync-sheet` still needed to pull Google Sheets state changes back to the DB. This step has no dashboard equivalent — Sheets changes are invisible until a CLI sync runs.
- The auto-ghost behavior in `FollowUpEngine.run()` (marking stale `applied` jobs as `ghosted`) only happens via the CLI `jsa followup` command, not via the dashboard's read path. This creates a subtle divergence: the dashboard shows a job as `applied` while a CLI run would have ghosted it.

### 1.6 Follow-Up Management

**Operation:** CLI `jsa followup` → `FollowUpEngine.run()` (includes auto-ghost mutation); Dashboard Application Tracker (read + resolve)

**Current state:** The dashboard surfaces due follow-up items and allows resolution. The CLI run includes an auto-ghost side effect.

**Friction:**
- The CLI and dashboard follow-up surfaces are subtly different in behavior. `jsa followup` auto-ghosts stale `applied` jobs; the dashboard read path intentionally does not. Running the CLI command after the dashboard may produce state changes the dashboard didn't show.
- No upcoming follow-up surface in the dashboard — `list_due_followups()` only returns items where `due_date ≤ today`; planning-horizon items (due next week) are invisible.
- No summary of total outstanding follow-ups visible without opening Application Tracker.

### 1.7 Reporting / Stats

**Operation:** `jsa stats` = `FunnelReporter.compute()` = same as Metrics screen

**Current state:** Metrics screen (Phase 5 Package 6) surfaces the same data as `jsa stats`. The CLI and dashboard are equivalent on this point.

**Friction:**
- No historical trend view. Metrics is always a current snapshot. `daily_reports` records report history but there is no dashboard surface for it.
- No way to compare "last week" to "this week" — the funnel could be stalling or accelerating, and Metrics has no way to show that.

### 1.8 Operator Workload Summary

| Operation | Dashboard surface | CLI required | Data already in DB |
|---|---|---|---|
| Ingest | None | Yes | Yes (source_health) |
| Grading | None | Yes | Yes (grading_batches) |
| Presentation | None | Yes | Yes (daily_reports) |
| Document generation | Full (Phase 5) | Optional | Yes (generated_docs) |
| State transitions | Full (Phase 5) | Optional | Yes (app_transitions) |
| Follow-up management | Partial (read + resolve) | Required for auto-ghost | Yes (followup_queue) |
| Sheets sync | None | Required | — |
| Stats / Metrics | Full (Phase 5) | Optional | — |

The operator must maintain a parallel CLI workflow for every row where "CLI required" is Yes. For a cron-based deployment, this means the first four rows run on schedule with no dashboard feedback. The operator has no active way to know whether the pipeline ran successfully without checking the terminal, the DB, or log files.

---

## 2. Phase 6 User Goals

These are the questions an operator should be able to answer from the dashboard in Phase 6 — without needing CLI access, DB queries, or log files.

### 2.1 "What ran since I last checked?"

The operator opens the dashboard after a night of cron-driven pipeline activity. They should be able to see: which operations ran, when they ran, and whether they succeeded or produced warnings. This is the most basic operational question and is currently completely unanswerable from the dashboard.

### 2.2 "What failed, and why?"

When something goes wrong — an adapter returns zero results, a batch grading call times out, a document generation fails — the operator needs a specific, actionable diagnosis. "Something looks wrong with Review Queue" is not a useful starting point for debugging. "Greenhouse adapter: 0 records fetched, error_class=anti_bot, 3 consecutive failures" is.

### 2.3 "Are my sources still producing jobs?"

Source-level per-run contribution counts — how many jobs each adapter fetched in each run — answer whether adapters are active and healthy. A source that was producing 15 jobs per week and is now producing 0 is either broken or has run dry. The operator cannot currently tell the difference without a per-source history view.

### 2.4 "Which firms or sources are quarantined?"

`firms.circuit_state = 'open'` and `firms.quarantine_until` are already populated by the circuit breaker. An operator who doesn't know a major firm is quarantined will wonder why that firm's jobs aren't appearing in Review Queue without realizing the adapter is intentionally skipping it.

### 2.5 "What's the current grading batch status?"

`grading_batches` records whether a batch has been submitted, completed, or errored. An operator who ran `jsa grade` and is waiting for results should be able to see the batch status from the dashboard rather than polling the terminal.

### 2.6 "Why is Review Queue empty?"

This is the canonical diagnostic question. The answer requires cross-referencing: Did ingest run? Did any source produce results? Did grading run? Did the report run? Did any jobs score above the threshold? Each step can independently produce an empty Review Queue with a different cause and remedy. Phase 6 should make this question answerable from the dashboard.

### 2.7 "Can I trigger a pipeline run without using the terminal?"

The dashboard currently cannot initiate any pipeline operation. An operator away from their development machine who wants to trigger an ingest from a phone or remote browser has no way to do so. This requires the background-job-runner decision to be resolved — it is the primary architectural gate on Phase 6.

### 2.8 "What's in my firm review queue?"

Firm drafts awaiting human review/approval — the precursor to a firm contributing jobs from its ATS adapter. This question is currently unanswerable from the dashboard; it is blocked on the draft-to-SQLite sync decision (Decision 1).

---

## 3. Pipeline Visibility Assessment

### 3.1 Data Already Available vs. Data to Build

Phase 6 has a significant head start: multiple tables already accumulate pipeline state on every run.

| Existing table | What it records | Visibility gap |
|---|---|---|
| `source_health` | Per-source run outcomes, error_class, error_detail, records_fetched, heal_action, config snapshots | No dashboard surface exists |
| `grading_batches` | LLM batch submissions, status, job_count, submitted_at, completed_at | No dashboard surface exists |
| `daily_reports` | When reports ran, which jobs were presented | No dashboard surface exists |
| `firms.circuit_state` + `firms.quarantine_until` | Per-firm circuit breaker state | No dashboard surface exists |

**What does not yet exist:**
- `pipeline_runs` table — a top-level orchestration log that records ingest/grade/report/generate/followup as unified run records with overall status, stats, and log excerpts. This table was designed in `dashboard_architecture.md` but was never created.
- A background job runner — no mechanism currently exists to run a pipeline operation from the dashboard without blocking the request/response cycle.

The implication for scoping: Phase 6 has two distinct categories of work with very different complexity profiles:
- **Expose existing data** (Source Health screen, grading batch status, report history) — relatively bounded; the data exists, the work is dashboard surface
- **Build new infrastructure** (pipeline_runs table, background job runner, triggered pipeline actions) — involves architectural decisions that are currently open and have more implementation risk

### 3.2 Historical Runs

`source_health` records append-only (each run adds a new row), giving a full history of every adapter's outcomes over time. `grading_batches` records each batch submission. `daily_reports` records each presentation. These together provide a retroactive audit trail that the operator can't currently see.

**Operator value of historical runs:** A single failed run is noise. Three failed runs from the same source with `error_class = anti_bot` is a signal — that source's adapter may need a configuration change. The historical view makes patterns visible that single-run data cannot.

### 3.3 Failures and Diagnostics

`source_health.error_class` already encodes a taxonomy: `transient|silent_drift|endpoint_moved|anti_bot|persistent`. Each class implies a different remediation path:
- `transient` — wait and retry; likely recoverable without intervention
- `silent_drift` — jobs are being fetched but content has changed (e.g., JD format shifted); may require extraction tuning
- `endpoint_moved` — ATS configuration needs updating (firm moved to a new ATS board)
- `anti_bot` — the adapter is being blocked; may need rate limiting, delay, or different fetch strategy
- `persistent` — repeated failure over many runs; requires investigation

Surfacing this taxonomy on the dashboard turns "something is wrong with the pipeline" into a specific, classified problem. This diagnostic value is built into the existing data — Phase 6 needs to surface it, not create it.

### 3.4 Operator Confidence

The core product goal of Phase 6 pipeline visibility is **operator confidence**: the ability to know, at a glance, that the pipeline is running correctly and producing trustworthy Review Queue content.

Without pipeline visibility, the operator is working on faith — trusting that last night's cron ran, that sources produced results, that grading completed, and that the threshold is working as intended. This faith is appropriate when the system is new and actively monitored; it becomes a gap as the deployment matures and the operator relies on it without daily manual checking.

Pipeline visibility does not require the operator to actively manage the pipeline. It requires that when something goes wrong — silently, in a background cron — the operator can discover it from the dashboard the next time they open it, rather than noticing symptomatically (empty Review Queue, missing jobs, stale follow-ups) weeks later.

---

## 4. Source Health Assessment

### 4.1 Current Data Richness

The `source_health` table is already one of the most data-rich tables in the schema. Every ingest run writes a row per source with: run timestamp, status (ok/empty/error/quarantined), records_fetched count, error_class, error_detail, heal_action taken, and JSON snapshots of firm configuration before and after any healing. The firms table adds circuit_state and quarantine_until per firm.

A Source Health dashboard screen is, more than any other Phase 6 screen, primarily a data surface problem rather than a data creation problem. Most of what the screen needs to display already exists.

### 4.2 Operator Usefulness

**High-value operator questions already answerable from `source_health` data:**
- Which sources ran in the last 24 hours? (run_at + source)
- Which sources returned zero records? (records_fetched = 0)
- Which sources produced errors, and what kind? (status + error_class)
- Which firms are currently circuit-broken or quarantined? (firms.circuit_state, firms.quarantine_until)
- Has this source been failing repeatedly? (consecutive_failures on firms, multiple error rows in source_health)

**Operator usefulness is high because silent failures directly degrade Review Queue quality.** A quarantined Greenhouse firm doesn't produce jobs that week. An anti-bot block on Adzuna reduces the total job pool. Neither failure is visible from any current dashboard screen — the operator sees only the symptom (fewer jobs in Review Queue) without a path to the cause.

### 4.3 Relationship to the ATS Quarantine Decision

The prior audit trail noted that Source Health is "blocked on ATS quarantine mapping (Decision 2)." This framing deserves refinement.

Decision 2 concerns the mapping of ATS tier values to the `quarantined` status — specifically, which tier values should automatically trigger quarantine. This decision gates the **quarantine status display specifically** on Source Health.

It does not gate the broader Source Health display: run history, records_fetched counts, error_class taxonomy, and consecutive_failures data can all be displayed without the quarantine mapping being resolved. A Phase 6 scoping decision to scope Source Health as "run history and error diagnostics, with quarantine display pending Decision 2" would be workable — it surfaces most of the operator value without requiring the open decision to be resolved first.

### 4.4 Likely Workflow Impact

Once Source Health is available:
- Morning workflow: operator opens dashboard, checks Source Health before Review Queue. If all sources are green, proceed normally. If a source is red, the operator knows Review Queue may be incomplete before spending time triaging it.
- Diagnostic workflow: when Review Queue is unexpectedly empty, Source Health is the first screen to check rather than the last resort (terminal/DB query).
- Maintenance workflow: recurring `endpoint_moved` errors flag firms whose ATS configuration needs updating — currently invisible until manually noticed.

---

## 5. Deferred Package Assessment

### 5.1 Source Health

**Urgency: High**
**Operator value: High**
**Data available: Yes — mostly**
**Blocker: Partial (quarantine display only)**

Source Health has the strongest case for priority treatment in Phase 6. Most of its data already exists, it directly addresses the most painful operator gap (silent pipeline failures), and the blocking decision (Decision 2) gates only the quarantine display feature, not the screen as a whole. A Source Health screen scoped to run history and error diagnostics — with a clear placeholder for quarantine display pending Decision 2 — delivers most of the operator value without waiting for the governance decision.

### 5.2 Pipeline Runs

**Urgency: High (for triggering actions); Medium (for history)**
**Operator value: High**
**Data available: Partial (grading_batches, daily_reports exist; pipeline_runs does not)**
**Blocker: Strong — background-job-runner architectural decision**

Pipeline Runs splits into two distinct sub-problems:

**Pipeline history display** — showing when operations ran and what they produced — is achievable from existing tables (`grading_batches`, `daily_reports`, `source_health`) with modest new infrastructure. The `pipeline_runs` table was designed to unify these but is not strictly required for read-only history display; the operator value of "what ran and what failed" can be partially served from existing data.

**Pipeline action triggers** — ingest, grade, report, generate, followup scan — cannot be added to the dashboard without resolving the background-job-runner decision. These operations are synchronous and long-running; triggering them from an HTTP request handler would block the server. This is the architectural gate that `dashboard_architecture.md` named as Phase 3 work (now Phase 6) and that the open decisions table in `ASH_INIT.md` tracks.

**Recommendation:** Separate the two sub-problems at scoping time. Pipeline history display can proceed without the background-job-runner decision. Pipeline action triggers require it. Scoping them as separate sub-packages allows history visibility to ship while the architectural decision is made.

### 5.3 Firm Review Queue

**Urgency: Low (for current operator workflow)**
**Operator value: Medium (grows as firm registry grows)**
**Data available: Blocked — draft-to-SQLite sync not implemented**
**Blocker: Strong — Decision 1 (draft-to-SQLite sync) must be resolved first**

Firm Review Queue manages `DraftFirmProfile` records awaiting human review. `config/firms.yaml` currently ships as an empty list — the firm registry is not yet seeded with any entries. Until the draft-to-SQLite sync gap is resolved (Decision 1), no DraftFirmProfile records exist in SQLite to display, and the screen would show an empty queue regardless of what firms.yaml contains.

The urgency is low because the current workflow is not blocked by the absence of this screen — firm discovery and management are CLI-only operations (`jsa firms discover/review/approve/reject/draft`) and the empty firms.yaml means there is little firm management activity happening. As the firm registry grows, the value of a dashboard review UI increases proportionally.

### 5.4 Recommended Sequencing

| Package | Sequence | Rationale |
|---|---|---|
| Source Health (run history + diagnostics, no quarantine display) | First | High urgency, data exists, no architectural blocker for the scoped version |
| Pipeline Runs — history display only | Second | Partial data exists, no background-job-runner needed for read-only; high diagnostic value |
| Pipeline Runs — action triggers | Third | Requires background-job-runner decision; can be scoped as a follow-on to history display |
| Firm Review Queue | Last | Hard data dependency on Decision 1; low current urgency given empty firms.yaml |

---

## 6. Phase 7 UX Backlog

These are quality-of-life gaps identified across the Donut study series. None require new architectural work — they are presentation and navigation decisions. Prioritized by operator impact.

### 6.1 High Priority

**Job Detail return path is context-unaware.**
`job_detail.html` hard-codes "Back to Review Queue" regardless of where the user came from. When navigating to Job Detail from Application Tracker or a future Firm Review Queue, the return link is wrong — the user returns to Review Queue instead of the screen they were working from. This will be noticed the first time a user opens Job Detail from Application Tracker and has to re-navigate back manually. Should be resolved before Application Tracker's first use is widespread.

**Terminal-state accumulation in Application Tracker.**
`rejected` and `ghosted` are in `TRACKED_STATES` and appear in the default Tracker view. As the pipeline matures, these will accumulate and dominate the list — the operator will eventually have more closed jobs than active ones. The default view should filter to active states (selected, applied, acknowledged, screen, interview, offer), with terminal states opt-in rather than default. Without this, Application Tracker becomes progressively harder to use over time.

**Follow-up items as secondary content rather than primary.**
The Tracker UX study established that follow-up items should be the screen's primary section — answering "what do I need to do today?" before displaying the full job list. Without this, the screen becomes a filtered Review Queue for later states rather than a dedicated urgency management tool.

**Tracker urgency ordering.**
The correct default sort for Application Tracker is urgency (follow-up due_date, then last_transitioned_at recency), not match_score or alphabetical order. Match score is the right default for Review Queue; it is the wrong default for Tracker, which is about time-sensitive obligations rather than candidate evaluation.

### 6.2 Medium Priority

**Upcoming follow-ups not surfaced.**
`list_due_followups()` returns only items where `due_date ≤ today`. An operator cannot see follow-ups due next week from the dashboard, which prevents planning. A "Next 7 days" section below the overdue/due-today items would close the planning gap. This requires a service call with a future `as_of` date — a known constraint flagged in the Tracker UX study.

**Metrics contextual links missing.**
Every aggregate row on Metrics (by_state, by_source, by_stretch) is a dead end — the user can observe a pattern but cannot navigate to the underlying jobs to investigate. Contextual links from each aggregate row to a filtered Application Tracker view resolve the most useful dead ends without requiring Metrics to duplicate Tracker content. This should be settled at Package 6 scoping.

**`selected` state placement in Application Tracker.**
`selected` jobs (committed to, not yet applied) are self-imposed pending actions, not employer-process milestones. Mixing them into the same sorted list as `interview` and `applied` jobs without visual distinction creates the wrong urgency signal. A dedicated "Ready to Apply" section above the active-pipeline list resolves this.

**Documents global nav without job context.**
The current global nav includes "Documents (open a job, then view its documents)" — a note that the screen is only accessible through a job. If the global nav entry for Documents navigates to a URL that then requires a job_id parameter, the entry needs either a graceful "please select a job first" message or to be removed from the global nav and replaced with a per-job contextual link only.

### 6.3 Lower Priority

**Global nav grouping.**
With all eight screens eventually present as nav entries, the flat list will carry screens of very different character without visual hierarchy. A light grouping (e.g., "Jobs" grouping Review Queue, Job Detail, Documents; "Operations" grouping Pipeline Runs, Source Health; "Insights" grouping Metrics) would preserve discoverability as the screen count grows. Low priority because the grouping only becomes necessary at full eight-screen implementation.

**Score calibration sample sizes on Metrics.**
`avg_match_by_state` is displayed without sample sizes. A "interview: avg 0.71" based on two jobs is easily misread as a meaningful statistic. Adding "(n=2)" or similar to each average prevents the misread. Minor display change, meaningful accuracy improvement.

**`total_jobs` vanity metric framing on Metrics.**
The total job count (all discovered, including terminal states) should be labeled as "total ever discovered" and positioned as denominator context, not as a headline number. A search that has ingested 900 jobs over three months with 6 active applications should not feature "900" prominently.

**Metrics empty-state design.**
Multiple Metrics sections return `None` or empty dicts before sufficient pipeline history exists — `median_days` returns `None` for transitions that haven't occurred, `response_rate_by_source` returns nothing for sources with no applied jobs. Each section needs a named "not enough data yet" empty state rather than blank cells or zeros. Zeros specifically are misleading (implying same-day responses or zero response rates).

**Auto-ghost CLI/dashboard divergence.**
`jsa followup` auto-ghosts stale `applied` jobs as a side effect of follow-up scanning. The dashboard read path intentionally bypasses this. A job that `jsa followup` would ghost appears as `applied` in the dashboard until a CLI run occurs. This divergence is not a bug — it is a deliberate read-path decision — but it is worth surfacing to the operator somewhere (perhaps via a "last follow-up scan: X days ago" indicator in Application Tracker) so the user understands that a CLI run may update states the dashboard is currently showing.
