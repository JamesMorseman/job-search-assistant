# Dashboard Information Architecture Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** Information ownership across the eight accepted, planned, and deferred dashboard screens. Grounded in the current service layer read models (`JobListItem`, `JobDetail`, `DocumentRecord`, `TrackerRow`, `StateTransition`, `FollowUpItem`, `FunnelStats`) and the current template implementations.

---

## 1. Executive Summary

The three accepted screens — Review Queue, Job Detail, Documents — already exhibit a clean scope hierarchy that can be named explicitly: **many-jobs list → one-job full picture → one-job one-domain**. Review Queue scans across all presented jobs. Job Detail renders everything knowable about a single job. Documents narrows further to a single domain (generated documents) within that one job. Each scope is narrower than the one above it, with no scope inversion.

The two planned screens don't extend that hierarchy — they introduce a parallel structure. Application Tracker is a second many-jobs list (post-triage jobs instead of presented ones), and Metrics is the only screen that aggregates beyond jobs into pipeline-level statistics. These two belong in a different category than the accepted screens, and designing them as if they extend the RQ → Job Detail → Documents chain would be a mistake.

Three information boundaries require explicit decisions to prevent drift:

- **Job Detail and Documents share current document links.** Both should show resume and cover letter links for the same job. This is legitimate minimal duplication if Document links in Job Detail are read-only references (quick glance) and Documents is the authoritative screen for version history, keyword coverage, and regeneration. The boundary is clear only if it is stated.
- **Job Detail and Application Tracker both carry `app_state`.** That field is a read-only display datum on Job Detail and the primary organizing key on Application Tracker. State transition *actions* belong exclusively on Application Tracker (and Review Queue for select/reject) — not on Job Detail. The state history (`app_transitions` full log) belongs on Job Detail, not on the Tracker list; the Tracker needs only the last transition for its own display purposes.
- **Metrics and Source Health both surface per-source data.** Metrics shows source *outcomes* (conversion rates, response rates). Source Health shows source *operational status* (run success/failure, quarantine). These are complementary, not duplicative, but they share a subject (the source) and a contextual link between them would be natural.

The deferred screens fall cleanly into three distinct categories — firm-centric, analytical-operational, and operational-only — none of which maps onto the job-centric scope hierarchy of the accepted screens. Treating them as global-nav peers (consistent with the navigation study's Model C recommendation) is the right fit for all three.

---

## 2. Screen Ownership Matrix

| Screen | Scope | Category | Primary Data Owner | Action Surface |
|---|---|---|---|---|
| Review Queue | Many jobs (presented) | Job list | `JobsService.list_jobs(app_state="presented")` | select, reject |
| Job Detail | One job (any state) | Job full-picture | `JobsService.get_job_detail()` + `TrackerService.get_state_history()` | none (read-only by ratified decision) |
| Documents | One job, document domain | Per-job domain | `DocumentsService.list_documents()` / `get_current_documents()` | regenerate |
| Application Tracker | Many jobs (post-triage) | Lifecycle list | `TrackerService.list_tracker_rows()` + `list_due_followups()` | state transitions, resolve follow-up |
| Metrics | Whole pipeline | Aggregate | `MetricsService.get_funnel_stats()` | none |
| Firm Review Queue | All firm drafts | Firm-centric | `FirmsService` (draft profiles) | approve, reject firm draft |
| Source Health | All sources | Operational | `source_health` table | (tbd — operational decisions) |
| Pipeline Runs | All pipeline executions | Operational | `pipeline_runs` table | (tbd — Phase 6) |

---

## 3. Information Placement Analysis

### 3.1 Review Queue

**Primary purpose:** Fast, low-friction triage of newly presented jobs. The user is scanning, not reading — making a quick binary decision (investigate further vs. reject outright) based on signals visible without opening each job.

**Required information:**
- Company, title, location, remote flag — the minimum to know what the job is
- Source — where it came from, relevant for evaluating reliability
- Match score, LLM grade — the triage quality signals; the user's scoring system is the whole point of the pipeline, and these are the summary outputs
- Apply URL — a fast path to verify the posting before deciding
- Select and reject actions — the two decisions available at this stage

**Optional information:**
- Stretch category — useful for quickly identifying which jobs are reach vs. core
- Posted date — freshness is a legitimate triage criterion; the service already retrieves it
- Benefit score, career trajectory score — these are available in `JobListItem` but are sub-signals of the match score; surfacing them in the list may overwhelm triage without adding decision value beyond what the grade already summarizes

**Information that does NOT belong:**
- Full job description — belongs to Job Detail; rendering it in a list creates both a visual and performance problem
- Score reason breakdowns (benefit reasons, trajectory reasons) — these are decision *rationale*; they belong where a user has already committed to investigating a job (Job Detail)
- Knockout criteria details — same as above; these belong in Job Detail
- Document history — no documents exist yet for presented jobs
- State transition history — presented jobs have minimal history; this belongs in Application Tracker and Job Detail
- Aggregate metrics — belongs to Metrics screen

**Relationships:**
| Related screen | Relationship |
|---|---|
| Job Detail | Primary drill-down link from every row (job title → job detail); already implemented |
| Documents | None — documents don't exist at the presented stage |
| Application Tracker | Indirect — select action transitions a job into the tracker's scope, but no direct link is needed |
| Metrics | None |

---

### 3.2 Job Detail

**Primary purpose:** The single authoritative page for everything knowable about one specific job. The user arrives here to build enough understanding to support a decision — whether that's deciding to select/reject, reviewing a past decision, checking scoring rationale, or verifying application status before a follow-up.

Job Detail is the only screen that crosses all domains for a single job (identity, scoring, knockouts, lifecycle, documents) in one place. All other per-job screens are domain-specific subsets; Job Detail is the cross-domain summary.

**Required information:**
- Full job identity: company, title, location (city, state, country), salary, remote flag, source, firm_id, apply_url, posted_date
- Full job description (`description_raw`) — this is the justification for Job Detail's existence; a user comes here to read what they couldn't read in the queue
- All score components with reasons: match_score, benefit_score, career_trajectory_score, stretch_category, benefit_reasons (list), trajectory_reasons (list)
- LLM grade and full rationale text (`llm_grade`, `llm_rationale`)
- All knockout criteria: ko_work_auth, ko_min_years, ko_eit_required, ko_pe_required, ko_clearance, ko_relocation, ko_degree_required
- Current application state (`app_state`)
- Full state transition history (from `app_transitions` — the complete sequence, not just the last entry)
- Current document links (resume URL, cover letter URL) — a lightweight reference only; the user should be able to see whether documents exist and follow a link to them without needing to navigate to Documents and back

**Optional information:**
- Due follow-up items for this job (`FollowUpItem` — action_type, due_date) — relevant when a user opens Job Detail for a job they've applied to, to see pending actions
- Discipline tags — already available in `JobDetail`; useful context but not essential for the core purpose
- Firm context (if FirmsService eventually provides it) — the `firm_id` is already surfaced; a link or summary block for the associated firm profile would be natural here once firm data is accessible

**Information that does NOT belong:**
- Document version history and keyword coverage details — these belong to Documents; Job Detail should show only current document links as references, not the full history
- Regenerate documents action — belongs to Documents; triggering regeneration from Job Detail would create two action surfaces for the same operation
- State transition actions (select/reject, or post-application advances) — select/reject is on Review Queue by ratified decision; post-application transitions belong on Application Tracker; Job Detail remains read-only
- Aggregate metrics — belongs to Metrics

**Relationships:**
| Related screen | Relationship |
|---|---|
| Review Queue | "Back to Review Queue" link (already implemented); primary entry path for presented jobs |
| Documents | "View Documents" link (already implemented in `job_detail.html` line 9); contextual link for this job's document history |
| Application Tracker | A contextual link to this job's tracker entry would close the same round-trip gap that the "Back to Review Queue" link closed for select/reject — worth settling before Application Tracker ships |
| Metrics | None |

---

### 3.3 Documents

**Primary purpose:** Complete document lifecycle for one specific job — version history of all generated resumes and cover letters, keyword coverage analysis, and the regeneration action. Documents is the only screen where document generation is triggered and its outputs reviewed in detail.

Documents is strictly per-job. It is always scoped to a `canonical_job_id`. It is not an aggregate "all documents" screen and should not be reachable as a top-level destination without a job context. The global nav entry for Documents should resolve to a message or redirect, not a document list, unless a job context is present.

**Required information:**
- Job identity header: company, title, app_state — just enough context to confirm which job this is (not the full detail; that's Job Detail)
- Current resume and cover letter: drive_url, generated_at, model_used
- Keyword coverage: keyword_coverage (%), keywords_hit list, keywords_missed list
- Regenerate action

**Optional information:**
- Full version history of all prior generations (list of `DocumentRecord` rows in reverse chronological order) — gives the user the ability to compare current against past without separate navigation
- Individual document metadata per version (model_used, generated_at) — useful for understanding which model produced which output

**Information that does NOT belong:**
- Full job description, scoring details, knockout criteria — all belong to Job Detail; Documents is a domain screen, not a full-picture screen
- Application state transition history — belongs to Job Detail and Application Tracker
- Documents for other jobs — this screen is strictly scoped to one job; a list of all generated documents across all jobs would belong to a future aggregate screen if ever needed, not to this one
- Aggregate pipeline metrics — belongs to Metrics

**Relationships:**
| Related screen | Relationship |
|---|---|
| Job Detail | Primary entry point (via "View Documents" link already in `job_detail.html`); Documents needs a "Back to Job Detail" link as the primary return path |
| Review Queue | None — documents are always accessed through a job, not directly from the queue |
| Application Tracker | None — no data overlap; regeneration is independent of application state by design (confirmed in `documents.py` docstring) |
| Metrics | None |

---

### 3.4 Application Tracker

**Primary purpose:** Ongoing lifecycle management of all active applications. This is the multi-job list for the post-triage world — the equivalent of Review Queue for jobs that have moved past `presented`. The user comes here to advance application states, check overdue follow-ups, and maintain awareness of active applications as a whole.

Application Tracker is fundamentally different in character from Documents: it is a cross-job view (like Review Queue), not a per-job domain screen. Designing it as a per-job screen would miss its primary value — showing all active applications at once, which no other screen does.

**Required information:**
- Job list: company, title, source, app_state, match_score, last_transitioned_at, last_transition_note — the `TrackerRow` model as specified
- Valid state transition actions per row (advance to next valid state via `TrackerService.transition_job()`)
- Due and overdue follow-up items (`FollowUpItem` — due_date, action_type, note) — surfaced either inline with each job row or as a dedicated follow-up section
- Resolve follow-up action

**Optional information:**
- Apply URL per row — useful when taking a follow-up action (e.g., checking status on an applied job)
- Filter/group by app_state — for a user with many active applications, being able to view all "interview" jobs at once is more useful than a flat chronological list
- Last transition note — already in `TrackerRow`; helps recall what happened without opening Job Detail

**Information that does NOT belong:**
- Full job description — belongs to Job Detail; Tracker rows should link there for detail, not inline it
- Score reason breakdowns — belong to Job Detail
- Document history — belongs to Documents; the tracker has no knowledge of generated_docs and should not acquire it
- Knockout details — belong to Job Detail
- Aggregate metrics — belong to Metrics; the Tracker is about individual jobs, not pipeline health
- Full state transition history per job — Tracker shows last_transitioned_at/last_transition_note only; the full history belongs to Job Detail (which already calls `TrackerService.get_state_history()` for this purpose)

**Relationships:**
| Related screen | Relationship |
|---|---|
| Job Detail | Each row should link to that job's detail page, consistent with the Review Queue pattern; this gives the user a path to full context without duplicating it in the list row |
| Review Queue | No direct link; Tracker covers a disjoint set of jobs (post-triage vs. presented) |
| Documents | No direct link needed; a user wanting documents for a specific job goes Job Detail → Documents |
| Metrics | Tracker data feeds into `FunnelStats` (by_state, by_source, response rates) but no dashboard link is needed from Tracker to Metrics |

---

### 3.5 Metrics

**Primary purpose:** Aggregate view of pipeline health across the entire job search — not per-job, not per-document. The user comes here to understand whether the pipeline is working: which sources convert, how fast applications progress, how scoring correlates with outcomes.

Metrics is the only screen with no per-job entry point. `FunnelStats` aggregates across all jobs and all states simultaneously. Every other screen has at least one related job; Metrics has none.

**Required information (all from `FunnelStats`):**
- State distribution: `by_state` counts across the full pipeline
- Source conversion: `by_source` (state counts per source) and `response_rate_by_source` (applied/responded/screened/interviewed counts and rates)
- Pipeline velocity: `median_days` (applied→response, applied→screen, applied→terminal)
- Score correlation: `avg_match_by_state` (are higher-scoring jobs actually progressing further?)

**Optional information:**
- Stretch category breakdown: `by_stretch` — useful for understanding whether reach jobs are worth pursuing
- Location metro breakdown: `by_location_metro` — available in `FunnelStats` though not yet populated by the current `FunnelReporter` (noted as a roadmap item in `dashboard_architecture.md`)
- Discipline breakdown: `by_discipline_state` — in `FunnelStats` structure but similarly future-state

**Information that does NOT belong:**
- Individual job rows — this is the most important boundary; Metrics should never inline job-level data, only aggregate counts and rates
- Document generation history — this is a per-job domain concern; no aggregate view of documents belongs here
- Follow-up items — these are per-job; if follow-up health were ever surfaced as a metric (e.g., "N follow-ups overdue"), it should be an aggregate count only, not the items themselves
- Application state actions — this screen has no mutation surface

**Relationships:**
| Related screen | Relationship |
|---|---|
| Review Queue | None |
| Job Detail | None directly; however, a `by_state` count on Metrics could contextually link to a filtered view of those jobs — a dead-end observation becoming actionable (this is the "Metrics to action" gap flagged in the workflow study) |
| Documents | None |
| Application Tracker | `by_state` data flows from Tracker's underlying job states into Metrics; a contextual link from a state-count row in Metrics to Application Tracker filtered by that state would close the dead-end gap without requiring Metrics to duplicate Tracker content |
| Source Health | Both surface per-source data; Source Health covers operational status (failures, quarantine) while Metrics covers outcome rates; a contextual link from a source row in Metrics to that source's health entry would be the natural cross-reference |

---

## 4. Duplication Risks

### 4.1 Job Detail ↔ Documents: Current Document Links

**The overlap:** Both screens will show resume and cover letter URLs for the same job.

**Why it exists:** Job Detail shows documents as *contextual reference* — "does a document exist for this job?" A user shouldn't need to navigate away from Job Detail just to confirm that a cover letter was generated. Documents shows documents as *the primary subject* — the full history, keyword coverage, and regeneration action.

**Where the line should be:** Job Detail shows only the current document links (`drive_url`) and their generation timestamp — read-only, no action. Documents owns everything else: version history, `keyword_coverage`, `keywords_hit`, `keywords_missed`, `model_used`, and the regeneration action.

**Risk if undefined:** If Job Detail ever adds keyword coverage details or a regeneration button, it duplicates Documents' entire purpose. If Documents ever omits job identity context, the user has no way to confirm which job they're looking at. Both risks are manageable if the boundary is stated explicitly.

### 4.2 Job Detail ↔ Application Tracker: `app_state` and Transition History

**The overlap:** `app_state` appears in `JobDetail`, `TrackerRow`, and `FollowUpItem`. State transition history (`get_state_history()`) is a `TrackerService` method but logically belongs on Job Detail.

**Why it exists:** `app_state` is unavoidable context on any screen that discusses a specific job — the user naturally wants to know what state the job is in. Application Tracker's primary key *is* `app_state` (filtering by it, acting on it). Job Detail's `app_state` is a read-only field in a larger picture.

**Where the line should be:** `app_state` as *display* lives everywhere a job is discussed. State transition *actions* live only on Review Queue (select/reject, ratified) and Application Tracker (post-application advances). Full state history (`app_transitions` log) belongs on Job Detail — it is part of understanding one specific job's lifecycle, and the Tracker's list view needs only `last_transitioned_at` and `last_transition_note`.

**Risk if undefined:** If Application Tracker surfaces full state history per row inline, it duplicates Job Detail's primary value-add. If Job Detail ever adds state transition action buttons, it creates two mutation surfaces for the same state machine — the governance concern already named in `phase_5_mvp_acceptance_criteria.md`.

### 4.3 Metrics ↔ Application Tracker: Per-Source and Per-State Counts

**The overlap:** Both ultimately derive counts from the same `jobs.app_state` column. `FunnelStats.by_source` and `FunnelStats.by_state` are aggregate views of the same underlying data that Tracker lists at the row level.

**Why it exists:** Aggregate counts and individual rows are different views of the same data. Neither duplicates the other — a count of 12 "applied" jobs is not the same as a list of those 12 jobs.

**Where the line should be:** Metrics owns the aggregate counts only. Application Tracker owns the individual rows. The link from a Metrics count to the corresponding filtered Tracker view is a navigation pattern, not a duplication — the recommended way to make Metrics actionable.

**Risk if undefined:** If Metrics ever starts listing individual jobs (even as a table beneath the count), it becomes a second Tracker. If Application Tracker ever starts computing and displaying pipeline-wide aggregate rates, it duplicates Metrics.

### 4.4 Metrics ↔ Source Health: Per-Source Data

**The overlap:** `FunnelStats.response_rate_by_source` and `FunnelStats.by_source` in Metrics; `source_health` operational data in Source Health. Both are about "how is this source doing?"

**Why it coexists cleanly:** The question being answered is different. Metrics answers "which sources produce applications that progress?" (outcome). Source Health answers "which sources are reliably running?" (operational). A source can have a perfect run record but terrible conversion rate, or an excellent conversion rate but frequent fetch failures.

**Risk if undefined:** If Source Health adds outcome rate columns, it overlaps Metrics. If Metrics adds failure-count columns, it overlaps Source Health. Maintaining distinct subjects (outcomes vs. operations) is the safe boundary.

---

## 5. Future Screen Categorization

### 5.1 Firm Review Queue

**Category: Firm-centric**

Firm Review Queue manages `DraftFirmProfile` records awaiting human review before they can influence scoring or ingestion. Its subject is the firm, not the job. The user is reviewing and approving or rejecting organizational-level data.

**Job-centric?** Indirectly — jobs belong to firms, and `firm_id` is already present in both `JobListItem` and `JobDetail`. A contextual link from Job Detail to its firm's review queue entry is natural. But Firm Review Queue's own list is scoped to firms, not jobs.

**Firm-centric?** Yes — this is the primary firm-centric screen.

**Operational?** Partially — it is an administrative queue, not a pipeline operations screen.

**Analytical?** No.

**Navigation implication:** Global nav entry (the full queue); contextual link from Job Detail to its associated firm entry (since `firm_id` is already on the `JobDetail` model). The link direction is Job Detail → Firm Review Queue, not the reverse.

**Relationship to other screens:** Firm data is upstream of job ingestion (FirmConfig affects which ATS jobs are ingested and at what tier). Its approval state influences what appears in Review Queue eventually, but there is no direct display relationship between the two screens.

**Blocked by:** Draft-to-SQLite sync gap (Decision 1, `phase_3_governance_addendum.md`).

---

### 5.2 Source Health

**Category: Operational / Analytical (primarily operational)**

Source Health monitors the `source_health` table — latest run timestamps, error messages, consecutive failure counts, quarantine status — for each of the nine configured source adapters. The user comes here to diagnose why a source isn't contributing to Review Queue, not to understand their application outcomes.

**Job-centric?** No — the unit is the source adapter (adzuna, greenhouse, lever, etc.), not any individual job.

**Firm-centric?** Loosely — `ats_type` is a FirmConfig field that maps to an ATS adapter, and quarantined firms are a Source Health concern (`phase_3_governance_addendum.md` Decision 2). But the primary subject is the source, not the firm.

**Operational?** Yes — this is the diagnostic screen for when the pipeline is misbehaving.

**Analytical?** Marginally — consecutive failure counts and quarantine state have an analytical quality, but they don't measure outcomes; they measure process health.

**Navigation implication:** Global nav entry. A contextual link from Metrics' per-source conversion table to that source's health record would be the most natural cross-reference: "this source has a 3% response rate; is that because the jobs are poor quality or because the adapter has been failing?"

**Relationship to other screens:** Closest relationship is with Metrics (both surface per-source data, from complementary angles). No relationship with job-centric screens unless a quarantined firm's jobs are surfaced.

**Blocked by:** ATS quarantine mapping (Decision 2, `phase_3_governance_addendum.md`).

---

### 5.3 Pipeline Runs

**Category: Operational**

Pipeline Runs records the execution history of background pipeline operations (ingest, grade, report, sync-sheet, generate, followup). The user comes here to confirm an operation succeeded, investigate a failure, or check what ran and when.

**Job-centric?** No — a run record covers an entire pipeline operation across many jobs, not one job specifically.

**Firm-centric?** No.

**Operational?** Yes — this is the most purely operational screen of the three deferred screens.

**Analytical?** Minimally — run history has an implicit trend (frequency of runs, run durations), but no user story has been written around analyzing run history as such.

**Navigation implication:** Global nav entry. The most natural contextual link would run from a Documents regeneration action to the resulting pipeline run record — a user who just triggered a regeneration might want to see its run status rather than refreshing Documents and hoping the new record appears. This is the only case where the link direction would be Documents → Pipeline Runs.

**Relationship to other screens:** Closest relationship is with Documents (regeneration actions create pipeline runs) and Review Queue (ingest + grade + report runs are what populates Review Queue). No direct relationship with Metrics or Application Tracker at the screen level.

**Blocked by:** Background-job-runner decision; reassigned to Phase 6 by DECISION_LOG.md.

---

## 6. Product Risks

**6.1 — Documents loses its reason to exist if Job Detail absorbs too much.**
The clearest version of this risk: a future package adds keyword coverage or a regeneration button to Job Detail because it's "more convenient" to have it there. At that point, Documents becomes redundant — a screen that only adds version history, which most users will rarely want. Documents' value depends on Job Detail remaining a reference screen (links only) rather than a functional one for document operations.

**6.2 — Application Tracker becomes a second Review Queue.**
If the Tracker is designed as a list of jobs with inline actions, filter controls, and sortable columns, it is structurally identical to Review Queue for a different set of states. This isn't inherently wrong, but it risks making the two screens feel interchangeable, with the boundary being only which `app_state` values they cover. The Tracker's distinguishing characteristic is that it also shows follow-up items — without that, it is just a filtered job list.

**6.3 — Metrics dead-end, compounding over time.**
As more jobs accumulate in terminal states (rejected, ghosted, offer), Metrics will become increasingly useful for diagnosing which sources or categories work. But if Metrics has no path back to the underlying jobs, the observation stays abstract. A user who notices that greenhouse jobs never progress past "applied" has no path from that observation to actually looking at those jobs. This risk grows as the pipeline matures.

**6.4 — State history split between Job Detail and Application Tracker.**
`TrackerService.get_state_history()` is a tracker service method that is conceptually more useful on Job Detail than on the Tracker list. If a future package surfaces full state history on the Application Tracker (because it's a "tracker feature"), the information appears on the wrong screen and the right screen (Job Detail) becomes less complete. The method's home in `TrackerService` makes this easy to do — but the presentation should be on Job Detail.

**6.5 — Global nav growing without grouping.**
With all eight screens eventually as global nav entries, the nav list will carry screens of very different categories — job-centric (RQ, Job Detail), domain-per-job (Documents), lifecycle list (Application Tracker), aggregate (Metrics), firm-centric (Firm Review Queue), and operational (Source Health, Pipeline Runs). A flat eight-item list without any grouping will feel arbitrary. The navigation study's suggestion of a light grouping (e.g., "Jobs" vs. "Operations") is worth considering before the nav becomes unwieldy.

**6.6 — No global follow-up surface.**
Follow-up items live in Application Tracker's scope (since follow-ups are tied to tracked jobs). But a user with multiple overdue follow-ups — checking on three interviews and two applications simultaneously — needs to see all of them together. Application Tracker can serve this purpose if it surfaces a "follow-ups due" section above the job list, but only if that is explicitly designed rather than assumed.

---

## 7. Recommendations for Project Master

1. **Name the three accepted screens' scope hierarchy explicitly** — many-jobs list (Review Queue), one-job full picture (Job Detail), one-job one-domain (Documents) — so that future packages can test whether a new information element belongs to a screen by checking its scope, not by guessing where it feels most convenient. This is a one-sentence design principle, not a formal governance change.

2. **State the Job Detail / Documents boundary before Documents ships (Packages 4a/4b).** Specifically: Job Detail shows current document links and timestamps as read-only references only; keyword coverage, version history, and the regeneration action belong exclusively to Documents. If this boundary is not written into the Package 4a acceptance criteria, the path of least resistance will be to add convenient document actions to Job Detail and then wonder why Documents feels redundant.

3. **State the Application Tracker / Job Detail boundary before Tracker ships (Packages 5a/5b).** Specifically: full state transition history (`get_state_history()`) belongs on Job Detail; Tracker displays only `last_transitioned_at` and `last_transition_note` per row. State transition actions belong on Tracker only (following the same "actions live on the list screen, not the detail screen" principle already established by select/reject on Review Queue vs. Job Detail). A contextual link from each Tracker row to that job's Job Detail page closes the detail-access gap without duplicating detail on the list.

4. **Resolve the Job Detail → Application Tracker contextual link question at the same time as Tracker scoping.** A user looking at Job Detail for an applied job has no specified path to that job's tracker entry today — the same round-trip gap that the "Back to Review Queue" link resolved for presented jobs. Settling this before Tracker ships is less costly than discovering it after.

5. **Design Application Tracker around follow-ups, not just job rows.** The Tracker's distinguishing value over a filtered job list is the follow-up surface. If `list_due_followups()` isn't surfaced prominently — ideally as a dedicated section or summary above the job list — the screen becomes a filtered version of Review Queue with different state labels, losing most of its purpose.

6. **Make Metrics actionable before it accumulates too much history behind a dead end.** The minimum viable fix — linking a by_state count or a by_source row to a filtered view of those jobs in Application Tracker — doesn't require Metrics to know about individual jobs or duplicate Tracker content. It is a navigation decision, not a data decision, and it is easiest to add at the time Metrics is first implemented (Package 6) than after the screen has shipped without it.

7. **Categorize the three deferred screens explicitly in their eventual scoping conversations.** Firm Review Queue is firm-centric; Source Health is operational/analytical; Pipeline Runs is operational. None of the three is job-centric in the way the accepted screens are. Designing them with job-centric patterns (per-job drill-down, contextual links from Job Detail as primary entry) would be a category error.

8. This document is advisory only. It proposes no roadmap change, no architecture change, and no governance modification. All boundary decisions named above require Project Master authorization before they carry any binding weight.
