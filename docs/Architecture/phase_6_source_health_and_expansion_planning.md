# Phase 6 Source Health — Operator Experience Design
# And Preliminary Planning: Firm Review Queue, Pipeline Runs, Future Expansion

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) and Anna (Software Dev) review. Not an implementation specification. Not a governance change. No code modifications.
**Date:** 2026-06-16
**Authorization context:** Project Master has authorized Source Health as the first Phase 6 package. Firm Review Queue, Pipeline Runs, and Future Expansion sections are preliminary planning — not authorized for implementation.

**Grounding:** `FirmsService` (Phase 4 Package 6) already provides `FirmStatus` (circuit_state, quarantine_until, consecutive_failures, last_successful_fetch). `source_health` table records per-source run outcomes with a five-class error taxonomy. `CircuitBreaker` constants: PERSISTENT_FAILURE_THRESHOLD=5, QUARANTINE_DAYS=7, SILENT_DRIFT_ZERO_THRESHOLD=3. Anti-bot errors immediately open the circuit; all others escalate through five consecutive failures. The nine configured source adapters are: adzuna, ashby, greenhouse, lever, recruitee, smartrecruiters, usajobs, workable, workday (plus email_alerts).

---

# Part One — Source Health: Operator Experience Design

## 1. Operational Questions This Screen Must Answer

Source Health exists to answer one category of question: **is my pipeline collecting jobs from its configured sources, and if not, why not?**

Every other dashboard screen is job-centric (Review Queue, Job Detail, Documents, Application Tracker) or aggregate-outcome-centric (Metrics). Source Health is the only screen that looks at the collection layer itself — the nine adapters that feed the entire pipeline. Its audience is the operator wearing a maintenance hat, not a job-search hat.

**The specific questions, in priority order:**

1. **"Is anything broken right now?"** — The first question on every visit. Should be answerable in under five seconds without reading a table.
2. **"Which sources ran since my last check?"** — Confirms the pipeline is executing on schedule.
3. **"Which sources returned jobs, and how many?"** — Distinguishes a healthy low-volume day from a silent failure.
4. **"Which firms or sources are quarantined, and until when?"** — Quarantined firms do not contribute to Review Queue. Missing this means wondering why a firm has gone quiet.
5. **"What kind of failure occurred, and what does it mean?"** — `error_class` encodes a meaningful taxonomy (transient, silent_drift, endpoint_moved, anti_bot, persistent), each with different implications.
6. **"Has this source been failing repeatedly or is this a one-time anomaly?"** — A single transient failure is noise. Three consecutive failures from the same source is a signal.
7. **"When did this source last successfully produce records?"** — `last_successful_fetch` answers whether a source has been silently degraded for days or weeks.
8. **"Why is Review Queue empty or thinner than expected?"** — The entry point for diagnosing upstream problems.

**Questions this screen deliberately does not answer:**
- "Which jobs came from this source?" — that is Review Queue and Application Tracker's role
- "How is my application pipeline converting?" — that is Metrics
- "Did my grading batch finish?" — that is Pipeline Runs

---

## 2. Information That Belongs on Source Health

### 2.1 Per-Source Summary (landing view)

For each source adapter, at a glance:
- Source identifier (the adapter name: adzuna, greenhouse, lever, etc.)
- Severity indicator (see Section 6)
- Last run timestamp and its status (ok / empty / error / quarantined)
- Records fetched on last run
- Consecutive failures count (aggregated from `firms.consecutive_failures` for firm-scoped sources; from `source_health` run log for aggregate sources like adzuna)
- Circuit state for the primary firm (if applicable): open or closed
- Quarantine-until date (if quarantined)

### 2.2 Per-Source History (drill-down)

For a single source, over recent runs:
- Chronological run log: run_at, status, records_fetched, error_class, error_detail
- Healing actions taken: heal_action column from `source_health`
- Configuration snapshots before/after any healing: old_config / new_config (useful context for understanding what changed)
- Per-firm status breakdown for multi-firm sources: which firms under this source adapter are healthy vs. quarantined

### 2.3 Alert-Priority Surface

Items that require immediate operator awareness, surfaced above the per-source table:
- Open circuits (circuit_state=open): which firms, quarantine expiry
- Anti-bot detections: which source, when
- Persistent failures (5+ consecutive): which source/firm
- Silent drift alerts (3+ zero-result runs in 7 days): which firm

### 2.4 Firm-Level Health Details (in per-source drill-down)

From `FirmStatus` (already available via `FirmsService.get_firm_status()`):
- firm_id and name
- ats_tier (reliability classification)
- circuit_state and quarantine_until
- consecutive_failures count
- last_successful_fetch timestamp
- last_fingerprinted timestamp (NULL = re-fingerprint scheduled)

---

## 3. Information That Does NOT Belong on Source Health

**Individual job listings.** The moment Source Health shows a table of jobs from a given source, it becomes a second Review Queue. The contextual link from Source Health to a filtered Review Queue view is the correct pattern — the jobs stay on Review Queue, not on Source Health.

**Application-state data.** How many jobs from this source are at "interview" stage is a Metrics question (by_source counts), not a Source Health question. Source Health is about collection, not outcomes.

**Funnel conversion rates or response rates.** These belong to Metrics. Showing "greenhouse response rate: 12%" on Source Health conflates adapter operational health with employer behavior patterns — two very different signals.

**Document generation history.** Not relevant to adapter health.

**Follow-up items.** Not relevant to adapter health.

**Pipeline run history beyond ingest.** Grading batches, report runs, and document generation runs belong to Pipeline Runs (when it ships). Source Health covers the ingest layer only.

**Firm intelligence details** (ENR rank, PE support, benefit signals). These are Firm Review Queue and Job Detail content. Source Health needs only the firm's operational status (circuit state, failures), not its intelligence profile.

**Configuration editing UI.** Source adapter configuration (ATS board tokens, tenant IDs, site URLs) lives in `config/firms.yaml` and `firms` table columns populated by the fingerprinting pipeline. Source Health is a read-only diagnostic screen, not a configuration editor.

---

## 4. Recommended Screen Layout

Source Health has two views: the **Summary View** (landing) and the **Source Detail View** (drill-down). These are described as layout intent, not as implementation specification.

### 4.1 Summary View (Landing)

```
Source Health
─────────────────────────────────────────────────────
[Alert bar — visible only when one or more critical issues exist]
┌──────────────────────────────────────────────────────────────────┐
│  ⚠ 1 source quarantined  ·  1 source with persistent failures   │
└──────────────────────────────────────────────────────────────────┘

Last pipeline ingest: [timestamp] — [N] sources ran

Source Status
┌────────────────┬──────────┬─────────────┬─────────┬──────────┬────────────────────┐
│ Source         │ Status   │ Last Run    │ Records │ Failures │ Details            │
├────────────────┼──────────┼─────────────┼─────────┼──────────┼────────────────────┤
│ greenhouse     │ ● OK     │ 2h ago      │ 14      │ 0        │ → View history     │
│ lever          │ ● OK     │ 2h ago      │ 7       │ 0        │ → View history     │
│ adzuna         │ ◐ Empty  │ 2h ago      │ 0       │ 0        │ → View history     │
│ workday        │ ✕ Error  │ 2h ago      │ 0       │ 5        │ → View history     │
│ ashby          │ ✕ Qrntnd │ 3d ago      │ 0       │ 7        │ → View history     │
│ smartrecruiters│ ● OK     │ 2h ago      │ 3       │ 0        │ → View history     │
│ usajobs        │ ● OK     │ 2h ago      │ 22      │ 0        │ → View history     │
│ recruitee      │ ◐ Warn   │ 2h ago      │ 0       │ 2        │ → View history     │
│ workable       │ ● OK     │ 2h ago      │ 6       │ 0        │ → View history     │
└────────────────┴──────────┴─────────────┴─────────┴──────────┴────────────────────┘

Quarantined Firms                            [only if any exist]
┌──────────────────┬────────────┬─────────────────┬───────────────┐
│ Firm             │ Source     │ Quarantine Until │ Reason        │
├──────────────────┼────────────┼─────────────────┼───────────────┤
│ Thornton Tomasetti│ ashby     │ Jun 23, 2026     │ anti_bot      │
└──────────────────┴────────────┴─────────────────┴───────────────┘
```

**Design intent:**
- Alert bar appears only when critical issues exist. No alert bar = no critical issues. The absence of the bar is itself meaningful.
- The source table is the primary content. Ordered by severity descending (critical first), then alphabetical.
- Each source row is one line — scannable in a single pass.
- The Quarantined Firms section below the table appears only when firms are quarantined, drawing attention without permanently occupying space.
- "Last pipeline ingest" timestamp at the top answers the "did it run?" question before the user reads the table.

### 4.2 Source Detail View (Drill-Down)

```
← Source Health

Source: greenhouse
Status: ● OK  ·  Last successful fetch: 2 hours ago

Recent Runs (last 14 days)
┌─────────────────────┬────────────┬─────────┬─────────────┬──────────────────────────────┐
│ Run At              │ Status     │ Records │ Error Class │ Detail                       │
├─────────────────────┼────────────┼─────────┼─────────────┼──────────────────────────────┤
│ Jun 16, 09:04       │ ● OK       │ 14      │ —           │ —                            │
│ Jun 15, 09:02       │ ● OK       │ 11      │ —           │ —                            │
│ Jun 14, 09:07       │ ◐ Empty    │ 0       │ —           │ —                            │
│ Jun 13, 09:05       │ ✕ Error    │ 0       │ transient   │ Connection timeout (retry ok)│
│ Jun 12, 08:59       │ ● OK       │ 19      │ —           │ —                            │
└─────────────────────┴────────────┴─────────┴─────────────┴──────────────────────────────┘

Firms Under This Source
┌───────────────────┬──────────┬──────────────┬───────────────┬──────────────────────┐
│ Firm              │ ATS Tier │ Circuit      │ Failures      │ Last Successful Fetch│
├───────────────────┼──────────┼──────────────┼───────────────┼──────────────────────┤
│ AECOM             │ green    │ Closed       │ 0             │ Jun 16              │
│ Jacobs            │ green    │ Closed       │ 0             │ Jun 16              │
│ HDR               │ yellow   │ Closed       │ 1             │ Jun 15              │
└───────────────────┴──────────┴──────────────┴───────────────┴──────────────────────┘

→ View jobs from greenhouse in Review Queue
→ View applied jobs from greenhouse in Application Tracker
```

**Design intent:**
- "← Source Health" returns to the summary view. Consistent with the "actions return to originating screen" convention.
- Recent Runs shows the last 14 days (or a configurable recent window) — enough to identify patterns without overwhelming.
- Error Class column uses the exact vocabulary from `source_health.error_class` so the operator can look it up against documentation.
- Firms Under This Source uses `FirmStatus` data — no additional service work beyond what Phase 4 Package 6 already built.
- Contextual links at the bottom navigate to other screens with this source as a filter parameter. Source Health does not show those jobs inline.

---

## 5. Recommended Workflow

### 5.1 Daily Morning Check (Primary Workflow)

The operator opens Source Health as part of a morning pipeline health check before triaging Review Queue.

1. **Scan the alert bar.** If no bar is visible: no critical issues — proceed to Review Queue. If a bar is visible: read it to understand what is broken before interpreting Review Queue.
2. **Check the "Last pipeline ingest" timestamp.** Confirms the pipeline ran since last visit. If stale by more than a day: investigate Pipeline Runs (when it ships) before anything else.
3. **Scan the status column.** Red (✕) and amber (◐) rows require investigation. Green (●) rows need no attention.
4. **Drill into any non-green source.** Read the recent runs table to determine whether the last failure was a one-time event or part of a pattern.
5. **Check the Quarantined Firms section.** If any firm is quarantined: note the expiry date and understand that its jobs are not being fetched until the quarantine lifts.
6. **Navigate to Review Queue** with accurate expectations about which sources are contributing.

### 5.2 Diagnostic Workflow (When Review Queue Is Unexpectedly Empty or Thin)

1. Open Source Health.
2. Check whether all sources ran recently (ingest timestamp).
3. Identify any sources showing zero records or errors.
4. Drill into the affected source(s) to determine error_class.
5. Interpret the error class against the known taxonomy (see Section 6).
6. Determine whether action is required (most transient errors self-resolve; endpoint_moved needs re-fingerprinting; anti_bot and persistent need operator awareness).

### 5.3 Weekly Maintenance Glance

Once per week, check:
- Any firms with elevated consecutive_failures (2-4, below circuit threshold)
- Any firms where `last_fingerprinted` is NULL (re-fingerprint scheduled but not yet run)
- `last_successful_fetch` for all quarantined firms — confirm quarantines are lifting on schedule

---

## 6. Recommended Severity Indicators

Severity is determined by the combination of circuit state, error class, and failure count. Four levels, with concrete criteria grounded in `CircuitBreaker` constants.

### Level 1 — Critical (Red ✕)

Shown when any of these conditions are true:
- `circuit_state = 'open'` (circuit breaker tripped)
- `quarantine_until` is in the future (firm actively quarantined)
- `error_class = 'anti_bot'` on most recent run (adapter is being blocked)
- `error_class = 'persistent'` on most recent run
- `consecutive_failures >= PERSISTENT_FAILURE_THRESHOLD` (5 or more)

**Meaning:** This source is not contributing jobs. Its silence is confirmed by the system, not assumed.

### Level 2 — Degraded (Amber ◐)

Shown when any of these conditions are true (and no Critical condition applies):
- `error_class = 'silent_drift'` on any run in the last 7 days (3+ consecutive zero-result runs flagged)
- `error_class = 'endpoint_moved'` on most recent run (re-fingerprint scheduled)
- `consecutive_failures` between 2 and 4 (approaching circuit threshold without triggering it)
- `last_fingerprinted IS NULL` (re-fingerprint pending)

**Meaning:** This source may be degrading. The system has taken automatic action but the operator should be aware.

### Level 3 — Warning (Yellow ◐)

Shown when:
- `status = 'empty'` on most recent run (zero records, no error logged — could be a genuinely quiet day or early silent drift)
- `error_class = 'transient'` on most recent run (retried and recovered, or expected to recover on next run)
- `consecutive_failures = 1` (single failure, not yet a pattern)

**Meaning:** Something noteworthy happened but the system handled it or may self-correct. Monitor but no immediate action needed.

### Level 4 — Healthy (Green ●)

Shown when:
- `status = 'ok'` on most recent run
- `records_fetched > 0`
- `consecutive_failures = 0`
- `circuit_state = 'closed'`

**Meaning:** This source ran, produced results, and has no known issues.

### Level 4b — No Data (Grey ○)

Shown when:
- No `source_health` rows exist for this source (adapter configured but has never run, or all rows are older than the display window)

**Meaning:** Cannot assess health. Usually indicates ingest has never run for this source.

---

## 7. Recommended Alert Hierarchy

The alert bar (Section 4.1) surfaces a prioritized summary of critical conditions. If multiple issues exist, the bar shows the highest-priority one with a count of additional issues.

**Alert priority, highest to lowest:**

| Priority | Condition | Alert text example |
|---|---|---|
| 1 | Anti-bot block detected | "Anti-bot block: ashby adapter is being blocked. Jobs from quarantined firms will not appear." |
| 2 | Circuit open (not anti-bot) | "1 source circuit-open: workday — 5 consecutive failures. Quarantine until Jun 23." |
| 3 | Persistent failure (circuit not yet open) | "workday: 4 consecutive failures — approaching circuit threshold." |
| 4 | Silent drift detected | "HDR (greenhouse): zero records for 3 consecutive runs. Re-fingerprint scheduled." |
| 5 | Endpoint moved | "jacobs (lever): ATS endpoint may have moved. Re-fingerprint scheduled." |
| 6 | Ingest stale by >24h | "Last ingest: 38 hours ago. Pipeline may not be running on schedule." |

**Alert text principles:**
- Name the specific source or firm. "Something is wrong" is not an alert.
- State the implication for the operator's job search ("Jobs from quarantined firms will not appear").
- State what automatic action was taken ("Re-fingerprint scheduled").
- Do not alarm for conditions that are self-healing (transient errors).
- Alert bar is absent — not empty, not grayed out, but completely absent — when no conditions at Level 1–2 exist.

---

## 8. Actions Operators Should Have

**Navigate to Source Detail.** From any source row in the summary table, the operator can drill into the per-source history view. This is the only navigation action from the summary.

**Navigate to filtered job views.** From the Source Detail view, contextual links to:
- Review Queue filtered by `source=X` — "View presented jobs from this source"
- Application Tracker filtered by `source=X` — "View active applications from this source"

These links give the operator a path from "this source is behaving strangely" to "what jobs has it actually been producing" — closing the diagnostic loop without duplicating job content on Source Health.

**Return to Source Health summary.** Consistent "← Source Health" link from every detail view, following the navigation study's "actions return to originating screen" convention.

---

## 9. Actions Operators Should NOT Have

**Manually open or close circuit breakers.** The circuit breaker is safety infrastructure, not a configuration knob. The anti-bot constraint in `circuit_breaker.py` is explicit: "NEVER escalate evasion." A manual "unquarantine" button directly contradicts this principle — an operator who forces a quarantined anti-bot firm to resume fetching could trigger escalating blocks. The circuit auto-closes when `quarantine_until` expires; this is the correct and only path.

**Manually unquarantine firms.** Same reasoning as above. The 7-day quarantine period is a technical safety constraint, not an arbitrary preference.

**Trigger ingestion from Source Health.** Triggering ingest is Pipeline Runs' responsibility. Source Health is read-only diagnostic. Mixing operation triggers into a diagnostic screen blurs the screen's purpose and creates an unexpected second surface for pipeline control.

**Acknowledge or dismiss errors.** Source Health should not have a "mark as seen" or "dismiss alert" mechanism. The alert bar disappears naturally when the condition resolves — either the source recovers on the next run, or the quarantine expires. A dismissal mechanism would allow the operator to hide a persistent problem without fixing it, making Source Health unreliable as a health signal.

**Edit source configuration.** ATS board tokens, tenant IDs, and site configurations live in `config/firms.yaml` and the `firms` table populated by the fingerprinting pipeline. These are not dashboard-editable parameters. Source Health shows the current configuration (in old_config/new_config snapshots from source_health rows) for diagnostic context, but does not expose edit fields.

**Set manual priority for firms from Source Health.** `firms.manual_priority` is a targeting signal (target/watch/neutral/ignore). It is not a health signal. Source Health is about operational reliability, not targeting preference. Firm targeting management belongs to Firm Review Queue, not here.

---

## 10. Integration with Future Pipeline Runs

When Pipeline Runs ships, Source Health and Pipeline Runs will share a time axis — every ingest run in Pipeline Runs produces `source_health` records. The two screens should be designed as complementary views of the same ingest event, not as separate silos.

**Source Health → Pipeline Runs link:**
Each run in the Source Detail history (a `source_health` row's `run_at` timestamp) should eventually link to the parent Pipeline Run record that triggered it. A future `source_health.pipeline_run_id` foreign key would enable this. Until that column exists, a time-range link ("view pipeline runs near this time") is an adequate approximation.

**Pipeline Runs → Source Health link:**
An ingest pipeline run record should link to "see per-source health for this run" — navigating to Source Health filtered by the run's timestamp. This makes the relationship bidirectional: the operator can start from the orchestration-level view (Pipeline Runs) and drill into the source-level detail (Source Health), or start from Source Health and navigate up to the parent run.

**Alert propagation:**
A failed ingest run in Pipeline Runs should surface the same severity level as the corresponding Source Health entries. If Source Health shows Critical for two sources, the parent ingest run in Pipeline Runs should also show a Critical indicator, not just "Completed with errors" — ensuring the operator sees the full severity picture from whichever screen they check first.

**Triggering and observing:**
When the operator triggers an ingest from Pipeline Runs, the Source Health view should reflect the new run's outcomes immediately after it completes. The two screens' data is the same underlying DB rows — Pipeline Runs writes the run record, Source Health reads the resulting `source_health` entries. No synchronization is needed; freshness is automatic as long as both screens read directly from SQLite.

---

# Part Two — Preliminary Planning: Firm Review Queue

*This section is preliminary planning only. Not authorized for implementation. Blocked on Decision 1 (draft-to-SQLite sync).*

## 11. Screen Purpose and Character

Firm Review Queue manages draft firm profiles awaiting human review before they influence ingestion and scoring. Its governing question is: **"should this firm be added to my registry, and with what configuration?"**

This is an administrative workflow, not a job-search workflow. The operator is reviewing organizational data (ATS type, tier, disciplines, known benefits, ENR rank), not individual job postings. The mental mode is evaluation of sources, not evaluation of opportunities.

**Character distinction from other screens:**
- Review Queue: evaluate presented job opportunities → select/reject
- Firm Review Queue: evaluate proposed firm configurations → approve/reject/defer

The parallel structure is intentional and the screen name is appropriately analogous — but the content and stakes are different. Approving a firm configuration makes that firm's ATS adapter active for future ingests; rejecting it suppresses it. The decision has pipeline consequences, not just job-search consequences.

## 12. Data Dependency and Blocker

`FirmsService` currently reads only the `firms` table, which contains only approved firms (those synced by `sync_approved_firms()` from `config/firms.yaml`). Draft profiles live in `data/firm_drafts/*.yaml` as filesystem-only artifacts — they have never been synced to SQLite.

Until Decision 1 (draft-to-SQLite sync) is resolved, no draft firm data exists in the database for a dashboard screen to display. A Firm Review Queue screen built against the current data model would always show an empty queue, regardless of how many drafts exist in `data/firm_drafts/`.

This is not a service layer gap — `FirmsService` could readily be extended to read a `firm_drafts` table once that table exists. It is a data architecture decision that must precede any implementation.

## 13. Proposed Information Model

When drafts are eventually in SQLite, Firm Review Queue would display:

**List view (left panel or full-width table):**
- Firm name
- ATS type detected (greenhouse, lever, workday, etc.)
- ATS tier assigned (green / yellow / red / unknown)
- ENR rank (if detected)
- Discipline specialties (detected)
- Date added to draft queue
- Reviewer action buttons: Approve / Reject / Defer

**Detail view (right panel or sequential full-width):**
- Full draft profile: all detected fields
- ATS configuration (board token, tenant, site)
- Known benefits detected
- Reputation notes
- Fingerprinting metadata (how was this firm discovered, when, from what source)

**Information that does NOT belong:**
- Jobs currently in the DB from this firm (these are jobs already ingested from approved configurations; they belong in Job Detail / Review Queue)
- Application outcomes for this firm (Tracker / Metrics)
- Source health runs for this firm (Source Health)

## 14. Proposed Actions

**Approve:** Accepts the draft configuration, marks it as approved, triggers sync to the `firms` table and eventual activation for ingestion. The approval path should confirm the ATS configuration is valid before activating.

**Reject:** Removes the draft from the queue without syncing to SQLite. Optionally sets `manual_priority = 'ignore'` to prevent re-discovery.

**Defer:** Leaves the draft in the queue for future review. No state change. Useful when the operator needs more time to evaluate a firm.

**Actions operators should NOT have from this screen:**
- Edit ATS board tokens or tenant IDs directly (configuration errors could produce bad ingestion behavior; editing should remain a CLI/file operation)
- Trigger immediate ingestion for a newly approved firm (that should be a scheduled or Pipeline Runs-triggered operation)
- Manually set circuit breaker state for a draft firm (that is Source Health / circuit breaker territory)

## 15. Navigation Relationships

- **From Job Detail:** `firm_id` is already in `JobDetail`. A contextual link from Job Detail to the firm's Review Queue entry (if it is in draft state) or the firm's Source Health status (if it is approved) would be the natural cross-reference.
- **From Source Health:** If a firm appears in Source Health (via per-firm status in the drill-down), a contextual link to its Firm Review Queue entry (if it has a pending draft) would close the discovery→review loop.
- **From Firm Review Queue:** After approving a firm, the operator would naturally want to go to Source Health to confirm the firm's adapter becomes active on the next ingest. A contextual "view in Source Health" link post-approval supports this.

---

# Part Three — Preliminary Planning: Pipeline Runs

*This section is preliminary planning only. Not authorized for implementation. Background-job-runner architectural decision is open.*

## 16. Screen Purpose and Character

Pipeline Runs answers the question: **"what happened in the pipeline, and can I make something happen?"**

This is the operational control center of the dashboard — the only screen that both reports on pipeline history and (eventually) triggers pipeline operations. It is the correct home for actions that Source Health, Metrics, and Application Tracker must not have.

**Two distinct sub-problems** (confirmed in the Phase 6 product assessment):

- **Pipeline history display** — read-only, achievable without background runner, can ship before action triggers
- **Pipeline action triggers** — requires background-job-runner architectural decision; cannot be added without it

These should be treated as separate implementation sub-packages, not as one combined screen that waits for both.

## 17. Pipeline History Display

**Data already available:**
- `grading_batches` — LLM batch submissions, status, job_count, completed_at
- `daily_reports` — when reports ran, which job IDs were presented
- `source_health` — per-source ingest outcomes (covered by Source Health screen)

**Data that needs the `pipeline_runs` table:**
- A unified orchestration-level log that records ingest/grade/report/generate/followup as single run records with aggregate stats and overall status

**Proposed layout — Pipeline History View:**

```
Pipeline Runs
──────────────────────────────────────────────────
[Last run: Jun 16, 09:04 — All operations OK]

Recent Runs
┌─────────────────────┬──────────────┬────────────┬──────────────┬──────────────────────┐
│ Started             │ Operation    │ Status     │ Duration     │ Summary              │
├─────────────────────┼──────────────┼────────────┼──────────────┼──────────────────────┤
│ Jun 16, 09:04       │ Ingest       │ ● OK       │ 4m 12s       │ 52 jobs · 9 sources  │
│ Jun 16, 09:08       │ Grade        │ ● OK       │ 14m 03s      │ 48 graded            │
│ Jun 16, 09:23       │ Report       │ ● OK       │ 0m 18s       │ 12 presented         │
│ Jun 15, 09:05       │ Ingest       │ ◐ Partial  │ 4m 44s       │ 38 jobs · 7 sources  │
│ Jun 15, 09:09       │ Grade        │ ● OK       │ 11m 52s      │ 33 graded            │
└─────────────────────┴──────────────┴────────────┴──────────────┴──────────────────────┘

[Load more]
```

**Per-run detail (drill-down):**
For an ingest run: links to Source Health showing source breakdown for that run's timestamp.
For a grade run: links to grading batch status.
For a report run: which jobs were presented (count + link to Review Queue filtered by that report date).

**Severity indicators:** Same four-level system as Source Health (Red/Amber/Yellow/Green), applied to run-level outcomes.

## 18. Pipeline Action Triggers

When the background-job-runner decision is resolved, a second layout section appears above the run history:

```
Run Operations
──────────────────────────────────────────────────────────────────────────
[Ingest]        Last: Jun 16, 09:04 — OK (52 jobs)
[Grade]         Last: Jun 16, 09:08 — OK (48 graded)
[Report]        Last: Jun 16, 09:23 — OK (12 presented)
[Generate]      Last: Jun 14, 18:30 — OK (3 document sets)
[Follow-up Scan] Last: Jun 15, 07:00 — OK
[Sync Sheet]    Last: Jun 13, 08:55 — OK
```

**Design intent:**
- Each operation button shows its last run outcome inline, so the operator can confirm the pipeline's current state before deciding what to trigger.
- Operations run in the background; the button becomes a "running..." indicator after submission, not a spinner that blocks the page.
- Triggering an operation that is already running (e.g., clicking Ingest while an ingest is in progress) should be prevented, not duplicated.

**Actions operators should NOT have:**
- Cancel a running operation mid-execution (too risky without knowing what state the DB is in)
- Schedule recurring runs from the dashboard (cron configuration belongs in the system, not the dashboard)
- Run operations in a non-default configuration (e.g., ingest-only-one-source) — that is a CLI parameter, not a dashboard action

## 19. Navigation Relationships

- **Pipeline Runs → Source Health:** Ingest runs link to Source Health filtered by that run's time range.
- **Pipeline Runs → Review Queue:** Report runs link to Review Queue with a "presented on date X" filter (showing which jobs came from that run).
- **Pipeline Runs → Application Tracker:** Generate runs link to Application Tracker showing jobs whose documents were generated in that run.
- **Source Health → Pipeline Runs:** Source Health drill-down's run timestamps link to the parent Pipeline Run record.
- **Review Queue → Pipeline Runs:** If Review Queue is empty, a contextual message "Check Pipeline Runs to confirm the last ingest" provides a diagnostic path.

---

# Part Four — Future Dashboard Expansion: High-Level Planning

*This section is high-level planning only. Not authorized, not sequenced, not a roadmap change.*

## 20. Historical Trend Views

The current Metrics screen is a current-state snapshot. As the pipeline accumulates months of data, the most valuable diagnostic questions become longitudinal: "is my response rate improving or declining?" "which source was strongest last month?" "how has my interview-to-offer rate changed?"

These questions require time-series data — weekly or monthly snapshots of the funnel — rather than a single computed snapshot. `daily_reports` already records presentation dates; `app_transitions` records all state changes with timestamps. A historical trend view would aggregate these over time windows rather than computing a single point-in-time summary.

This is a Metrics evolution, not a new screen. The same screen could toggle between "current snapshot" and "trend over N weeks" without requiring a separate navigation destination.

## 21. Firm Intelligence Drill-Down

`FirmDetail` (from `FirmsService.get_firm()`) already exposes ENR rank, known benefits, trajectory priors, reputation notes, disciplines, and ATS configuration. Currently there is no screen that displays this information to the operator.

A future Firm Detail screen would be reachable from:
- Job Detail (via `firm_id` contextual link)
- Source Health (from the per-firm status in drill-down)
- Firm Review Queue (from any approved firm in the queue)

It would display the full `FirmDetail` — intelligence profile, ATS configuration, source health status — as a read-only reference. It would not duplicate Firm Review Queue's approval workflow or Source Health's run history.

## 22. Scoring Calibration Visualization

The Metrics study identified `avg_match_by_state` as a strategy validation signal — whether higher match scores correlate with better outcomes. A scoring calibration view would make this more actionable by showing the full distribution:
- Score distributions per state (how spread out are the scores in each stage?)
- Which discipline weights are contributing most to high-scoring-but-not-progressing jobs
- Which benefit signals are present in jobs that reach "screen" vs. jobs that stay at "applied"

This is a future enhancement to Metrics, not a separate screen. It requires no new data — all the inputs exist in the `jobs` table. The value grows proportionally with the number of applications that have reached late-stage outcomes.

## 23. Dashboard Configuration Surface

Currently all configuration (scoring weights, source adapter credentials, firm seeding) requires editing YAML files. As the dashboard matures toward eventual OSS use, a configuration surface would allow:
- Source adapter enable/disable toggles
- Scoring threshold adjustments (GRADING_FLOOR)
- Follow-up cadence preferences
- LLM provider and model selection

This is Large effort (per the OSS productization assessment) and is appropriate for a future phase, not Phase 6 or 7. It is named here as a planning horizon item — the kinds of parameters that would eventually move from `.env` and YAML files into the dashboard configuration surface.

## 24. Alert and Notification Surface

Currently, critical pipeline events (quarantine, circuit open, silent drift) are surfaced only when the operator actively visits Source Health. A future notification or alert surface would surface these events proactively — either as a dashboard badge, a local notification, or an email/webhook.

The alert hierarchy defined in Section 7 is designed to be compatible with a future notification system. The severity levels and alert text could drive notifications without architectural changes to the underlying data.

This is appropriate as a long-term enhancement after Source Health and Pipeline Runs have established the alert taxonomy in practice.

## 25. Navigation Architecture as Screens Accumulate

With Firm Review Queue, Source Health, and Pipeline Runs added to the existing five screens, the global nav will carry eight entries. The navigation study (Model C) recommended light grouping before the flat list becomes unwieldy.

A proposed future grouping, consistent with the screen categorization study:

```
Jobs
  Review Queue
  Job Detail
  Documents
  Application Tracker

Operations
  Pipeline Runs
  Source Health
  Firm Review Queue

Insights
  Metrics
```

This grouping imposes no navigation model change — Model C (global nav + contextual links) remains correct. It only adds visual structure to a flat list that will otherwise become an undifferentiated eight-item index. The grouping should be settled when the eighth screen ships, not before — adding groups prematurely creates visual hierarchy where none is yet needed.

---

*This document is advisory only. Part One (Source Health operator experience design) is authorized for Phase 6 implementation by Project Master. Parts Two, Three, and Four are preliminary planning without implementation authorization. No code modifications, no governance changes, no roadmap changes are proposed or implied by this document.*
