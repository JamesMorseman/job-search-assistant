# Application Tracker UX Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** Evaluating Application Tracker's unique value proposition relative to Review Queue, Job Detail, and Documents; the role follow-ups should play in the screen design; and the risks of building Tracker as a simple filtered list rather than a distinct screen.

**Grounding:** Derived from the current `TrackerService` and `FollowUpItem` read models (see `job_search/services/tracker.py`). `TrackerService.TRACKED_STATES` = (selected, applied, acknowledged, screen, interview, offer, rejected, ghosted). `list_due_followups()` returns items where `due_date ≤ today` and `resolved = 0` by default — it does not return future-dated items without an explicit `as_of` override.

---

## 1. Executive Summary

Application Tracker's differentiated value is not what states it shows — it is **time**. Review Queue has no time dimension; a job scores well or it doesn't, and the user decides immediately. Application Tracker is fundamentally about when things happened, when they need to happen next, and how long silence has been accumulating. Without the time dimension surfaced explicitly, Tracker becomes a filtered version of Review Queue for a different set of states, and there is no compelling reason to navigate to it rather than staying in Job Detail.

The follow-up queue is the mechanism that makes that time dimension concrete. A list of due and overdue follow-ups is not just a feature of the Tracker — it is the reason the user opens it. A user checking "what needs my attention today in my active applications" is asking a time-sorted urgency question, not a job-identity question. If follow-ups are treated as secondary (a sub-list beneath the main job table, or worse, a column in it), the Tracker fails at its primary job while still technically being correct.

The three specific risks this study identifies:

- **Follow-ups subordinated to the job list.** If the Tracker opens on a chronological or alphabetical job table and follow-up items are a sortable column or a filter, a user with three overdue items and fourteen tracked jobs has to actively seek out what needs attention rather than being shown it immediately.
- **State history on the wrong screen.** Application Tracker has access to `TrackerService.get_state_history()`, and it is technically straightforward to surface full transition history per row. Doing so would duplicate Job Detail's primary unique content — the full, sequential picture of one job's journey — and would bloat the list without serving Tracker's cross-job purpose.
- **"Applied, no response" invisibility.** The auto-ghost logic in `FollowUpEngine.run()` is intentionally bypassed by `list_due_followups()` to avoid implicit state mutation from a read path. This means a job can sit at "applied" for weeks with no signal to the user. The Tracker is the correct screen to surface "applied N days ago, no activity" as a visible signal — not as an automatic state change, but as an attention flag that a human can act on.

---

## 2. Tracker Differentiation Analysis

### 2.1 Review Queue vs Application Tracker

These two screens are the closest structural analogs in the dashboard: both are multi-job list screens where the user takes action. The difference is in what kind of thinking each screen supports.

**Review Queue supports triage thinking.** The user is in an evaluation mode — each job is a new candidate that hasn't yet been committed to. The decision is fast and binary (investigate further or discard). There is no prior history to recall. Time is not a primary dimension — a job presented today and a job presented last week are evaluated the same way.

**Application Tracker supports management thinking.** The user is in a stewardship mode — each job in the Tracker represents a commitment already made. The questions are not "is this worth my time?" but "what do I owe this one?", "how long have I been waiting?", and "what needs attention today?" History is essential, not incidental. Time is the primary organizing dimension.

This distinction has a concrete structural implication: **Review Queue's organizing principle is match score** (best fit first). Tracker's organizing principle should be urgency (what needs attention soonest), not match score. A job with a 0.85 match score that had an interview six weeks ago and no follow-up since is less urgent than a job with a 0.60 match score with an interview scheduled for tomorrow. Sorting Tracker by match_score carries the wrong mental model from Review Queue into a screen where it does not belong.

| Dimension | Review Queue | Application Tracker |
|---|---|---|
| Job scope | Presented only | Post-triage (8 states) |
| Primary thinking mode | Triage / evaluate | Manage / steward |
| Organizing principle | Match score (best fit first) | Urgency (what needs attention) |
| Time dimension | None | Central |
| Actions available | select, reject | state transitions, resolve follow-up |
| Follow-ups | None | Core feature |
| Row count expectation | Can be large (many presented jobs) | Should shrink over time as jobs reach terminal states |
| When user visits | After a pipeline run adds new jobs | When something needs attention (follow-up due, response received) |

### 2.2 Job Detail vs Application Tracker

Job Detail provides depth on one job. Application Tracker provides breadth across all tracked jobs. These are not competing screens — they are complementary levels of scope, and each depends on the other.

**The depth ↔ breadth handoff:** A user who wants to understand the full picture of a specific opportunity navigates from Tracker to Job Detail. A user who has finished reviewing a specific job's detail navigates back to Tracker to resume managing the overall landscape.

**What belongs on Tracker but not Job Detail:**
- Cross-job urgency signals: which job has the oldest follow-up, which has been silent the longest
- Aggregate state visibility: how many jobs are at each stage simultaneously
- Relative recency: "applied 3 days ago" is meaningful only in comparison to "applied 42 days ago" when both are visible on the same screen

**What belongs on Job Detail but not Tracker:**
- Full state transition history (the complete chronological log from `get_state_history()`) — this belongs on Job Detail because it is a per-job narrative; surfacing it per-row in Tracker would bloat each row and duplicate Job Detail's content
- Full job description and scoring rationale — these are why a user opens Job Detail; Tracker doesn't need them and shouldn't try to inline them
- Document links and keyword coverage — per the information architecture study, these belong to the Job Detail → Documents axis, not to the Tracker

**The single point of overlap that needs a stated rule:** `app_state` appears in both `TrackerRow` and `JobDetail`. On Tracker it is the organizing field. On Job Detail it is one field in a larger picture. This is fine — read-only context fields can coexist on multiple screens. The constraint is that state transition *actions* stay on Tracker only, not on Job Detail, per the ratified decision that Job Detail is read-only.

### 2.3 Documents vs Application Tracker

These two screens have no meaningful overlap and need no boundary statement. `DocumentRecord` carries nothing about application state. `TrackerRow` carries nothing about documents. The only shared ancestor is Job Detail, which contextually links to both. A user who wants documents for a specific tracked job follows the path Tracker → Job Detail → Documents; the screens do not need to reference each other directly.

### 2.4 What Makes Tracker Unique — Summary

Tracker's unique value rests on three things that no other screen provides:

1. **Cross-job urgency signal.** Only Tracker can show "you have two overdue follow-ups and one interview tomorrow" across the whole active pipeline simultaneously. Review Queue can't (it covers a different phase). Job Detail can't (it covers one job). Metrics can't (it shows aggregate counts, not actionable items).

2. **Pending-action agenda.** The follow-up queue — sorted by due date, surfaced above or alongside the job list — is an active to-do list that the user can work through during a single session. No other screen provides this.

3. **Silence detection.** A job that has been at "applied" for an extended period with no follow-up scheduled and no state change is invisible in the current pipeline — the auto-ghost logic is intentionally bypassed from read paths. Tracker is the only screen positioned to surface this as a visible signal (e.g., "applied 38 days ago, no activity") that prompts a human decision without triggering an automatic state change.

---

## 3. Follow-Up Workflow Analysis

### 3.1 The Three Urgency Tiers

Follow-up items in the `followup_queue` table carry a `due_date` field. For display and UX purposes, these fall into three meaningfully different tiers:

| Tier | Condition | User question | Appropriate UX treatment |
|---|---|---|---|
| Overdue | due_date < today, resolved = 0 | "Why haven't I done this yet?" | Highest visual prominence — these require immediate attention or a conscious decision to dismiss |
| Due today | due_date = today, resolved = 0 | "What do I need to do before end of day?" | Clearly surfaced alongside overdue items; distinct from upcoming |
| Upcoming | due_date > today, resolved = 0 | "What's coming up this week?" | Secondary section or filtered view; not urgent but useful for planning |

**Service gap worth noting:** `list_due_followups()` as currently written accepts an `as_of` parameter that defaults to today. It returns items where `due_date ≤ as_of`. This means:
- Overdue items: returned when as_of = today (due_date < today satisfies ≤ today)
- Due today: returned when as_of = today
- Upcoming: **not returned** unless as_of is set to a future date

Surfacing upcoming follow-ups would require either a separate service call with a future `as_of` date or a schema change to the query. This study does not propose an implementation, but the gap is a product design constraint: Tracker cannot show a planning horizon ("what's coming up this week") without this being addressed at the service level.

### 3.2 The Follow-Up as Primary, Not Secondary

The most consequential UX decision for Tracker is whether follow-ups are primary or secondary content.

**Follow-ups as secondary (the easy path, the wrong path):** Tracker opens on the job list. Follow-up items appear as a column ("Follow-up due: Nov 3"), a badge on the row, or a separate table below the main list. A user who has overdue items must visually scan the job list to find which jobs have them.

**Follow-ups as primary (the right path):** Tracker opens on the urgency agenda. Overdue and due-today items appear first, clearly labeled, with the relevant job context (company, title, apply_url for quick action). The job list follows as secondary content — the broader landscape once the urgent items are handled.

The argument for primacy: the reason a daily user opens Application Tracker is not to look at their full list of tracked jobs. They know which jobs they're tracking. The reason they open Tracker is to answer "what needs attention today?" Surfacing that answer immediately, before they have to scan a list, is what makes the screen useful rather than merely correct.

### 3.3 Per-Follow-Up Context

Each `FollowUpItem` already carries the fields needed for action without requiring a separate Job Detail navigation: `company`, `title`, `app_state`, `apply_url`, `action_type`, `due_date`, `note`. This means a user can:
- Read the company and role (confirm which job this is)
- Check the action type (what kind of follow-up: check on status, send a note, etc.)
- Open the apply URL directly to take the action
- Resolve the follow-up in place

What `FollowUpItem` does not carry: the full job description, scoring, knockout criteria, documents. For a user who wants to review the job before acting, a link to Job Detail from the follow-up item is the right answer, not inlining Job Detail content.

### 3.4 State Visibility

`TrackerRow` carries `app_state`, `last_transitioned_at`, and `last_transition_note`. These three fields together answer "where is this job and when did it last move?" without the full state history, which belongs on Job Detail.

For the Tracker list, grouping or filtering by `app_state` is more useful than sorting by it alphabetically. A user with two interviews, five applications, and three selections pending is better served by seeing "Interviews (2): [jobs]" than by an alphabetically sorted list that scatters the same state across the table.

**States that warrant visual distinction:**
- `interview` and `offer` — positive-momentum states; the user wants these visible
- `ghosted` — terminal state reached by inaction; the user may want to hide these or review them separately
- `rejected` — terminal state reached by employer action; same as ghosted for review purposes
- `selected` (but not yet applied) — the user has committed to apply but hasn't yet; this is an action item almost as much as a follow-up item

`selected` jobs — jobs the user has chosen but not yet applied to — occupy an ambiguous space. They are in the Tracker's `TRACKED_STATES` list, but they represent a user commitment, not an employer process. A `selected` job with a `due_date` follow-up for "submit application" is a user-facing task, not an employer-response task. Whether `selected` jobs should appear in the same list as `interview` and `offer` jobs is a layout question the information architecture alone cannot resolve, but it is worth naming as a distinction.

### 3.5 State History on the Wrong Screen

`TrackerService.get_state_history()` retrieves the full `app_transitions` log for a given job. This method exists in `TrackerService` for clean encapsulation — all tracker-related queries in one service — but its presentation home is Job Detail, not the Tracker list.

The reason: state history is a per-job narrative ("this job was presented on Oct 1, selected Oct 3, applied Oct 5, acknowledged Oct 9"). It tells the story of one opportunity. A Tracker list is a cross-job view of current status and urgency. Inlining full history per row on Tracker would make each row as long as a Job Detail page, and would duplicate Job Detail's primary differentiating content.

The correct pattern — consistent with every other detail field — is: Tracker row links to Job Detail → Job Detail shows full state history. The tracker row's `last_transitioned_at` and `last_transition_note` provide enough recency context for the list view without pulling the full log.

### 3.6 Tracker-to-Job Detail Navigation

Every Tracker row should link to the corresponding Job Detail page, following the same pattern already established between Review Queue rows and Job Detail. This is the primary cross-screen link for Tracker.

**Why it matters for follow-ups specifically:** A user with an overdue follow-up may want to review Job Detail before taking action — checking the company, role details, or LLM rationale before composing a follow-up email. The apply_url in `FollowUpItem` gets them to the external posting; the link to Job Detail gets them to the internal full picture. Both should be reachable from the follow-up item without navigating elsewhere first.

**Round-trip implication:** When a user navigates from Tracker to Job Detail, the return path should be "Back to Application Tracker," not "Back to Review Queue." The current Job Detail template has a hardcoded "Back to Review Queue" link. Once Application Tracker ships, Job Detail will need a return path that reflects where the user came from — or a consistent decision that "Back to Review Queue" is the always-present link and Tracker users use the global nav to return. The latter is functional but suboptimal; the former requires contextual return-path logic that the current template does not have.

---

## 4. Risks

**4.1 — Tracker designed as a filtered list, not an urgency screen.**
If Packages 5a/5b scope Application Tracker as "a table of jobs in tracked states, sortable by column," the follow-up surface will be a column or badge afterthought, and the screen will fail to provide the urgency-first UX that distinguishes it from Review Queue. The risk is not that Tracker will be wrong — it will correctly show tracked jobs — but that it will be insufficiently useful to justify regular visits.

**4.2 — Overdue items indistinguishable from due-today items.**
`list_due_followups()` returns both overdue and due-today items in a single list sorted by `due_date ASC`. Without explicit visual distinction between "this was due three days ago" and "this is due today," the urgency signal is lost. A due_date column alone doesn't convey urgency; the user has to compute "how overdue is this?" themselves.

**4.3 — No upcoming follow-up surface.**
As currently implemented, the service cannot return future-dated follow-up items without an `as_of` override. A user who just resolved three overdue items and wants to know when the next one is due has no way to see that from the Tracker screen without this being addressed. This gap compounds as the user's pipeline matures and follow-up patterns become more important for planning.

**4.4 — `selected` jobs lost in the list.**
Jobs in `selected` state have been committed to by the user but not yet applied to. They represent pending user action (submit the application), not pending employer response. Mixing them into the same sorted list as `interview` and `applied` jobs without distinction risks burying a self-imposed action item under jobs awaiting external responses.

**4.5 — Terminal-state accumulation cluttering the active view.**
`rejected` and `ghosted` are in `TRACKED_STATES`. As the pipeline matures, most tracked jobs will eventually reach a terminal state. Without filtering or archiving, the Tracker list will grow monotonically and the active jobs — the ones that still need attention — will be harder to find.

**4.6 — Return-path ambiguity from Job Detail.**
Job Detail currently hard-codes "Back to Review Queue." A user who navigated to Job Detail from Tracker returns to Review Queue rather than Tracker — a wrong-context return that breaks the management session. This is a small but concrete friction point that will be noticed the first time a user opens Job Detail from Tracker.

**4.7 — Auto-ghost gap invisible without Tracker surfacing it.**
`list_due_followups()` intentionally bypasses `FollowUpEngine.run()`'s auto-ghost step. This is correct for read-path purity, but it means a job that has been at "applied" for 60 days with no follow-up scheduled has no signal anywhere in the dashboard. The Tracker is the right screen to surface "applied N days ago, no activity" — but only if it is explicitly designed to do so, rather than relying on a `last_transitioned_at` column that a user must inspect manually.

---

## 5. Opportunities

**5.1 — An urgency-first layout creates daily habit.**
If Tracker opens with overdue and due-today follow-ups as the top section — a short, action-oriented list the user can work through quickly — it becomes the natural morning starting point for active job-search sessions. A screen that answers "what do I need to do right now?" before anything else earns repeat visits in a way that a job table does not.

**5.2 — State grouping creates immediate pipeline visibility.**
Grouping tracked jobs by `app_state` (rather than a flat sorted table) gives the user an instant picture of where their pipeline stands: "2 interviews, 3 applied, 5 selected." This is a different kind of value from Metrics' aggregate counts — Tracker's grouped list is *actionable* (each group contains jobs the user can act on), while Metrics' counts are *diagnostic* (useful for understanding patterns over time).

**5.3 — Silence detection as a first-class signal.**
Surfacing "applied N days ago, no activity" as an attention flag — without auto-ghosting, without triggering a state change — gives the user the information to make a human judgment: is this worth one more follow-up, or is it time to mark it ghosted manually? The `last_transitioned_at` field is already on `TrackerRow`; computing "days since last transition" is a display decision, not a data gap.

**5.4 — Follow-up resolution as a satisfying micro-action.**
A follow-up item with a "Resolve" button that disappears when clicked — without navigating away from the Tracker — is a small but meaningful piece of UX. It makes the screen feel like a to-do list the user can complete, not just a table to review. The `resolve_followup()` action already exists in `TrackerService`; the UX design determines whether it feels like a checkbox or a buried form.

**5.5 — `selected` as a distinct "ready to apply" section.**
If `selected` jobs are surfaced as their own section ("Ready to Apply") above the rest of the tracked states, the Tracker gains a natural multi-section structure: Ready to Apply → Active Applications → Awaiting Response → Terminal. Each section has a different character and different user intent. This grouping also makes it easier to filter out terminal states from the active view without a separate filtering mechanism.

**5.6 — Upcoming follow-ups as a planning horizon.**
Even a simple "Next 7 days" section below the overdue/due-today items — if the service can be extended to return future-dated items — would give the user a planning view without requiring a calendar integration. The value is low-effort planning: "I have follow-ups due Tuesday and Thursday this week" is enough to structure a session without detailed calendar management.

---

## 6. Recommendations for Project Master

1. **Define Tracker's organizing principle as urgency, not match score or alphabetical order, before Packages 5a/5b are scoped.** Match score is the correct default for Review Queue (evaluating new candidates). For Tracker, last_transitioned_at recency and follow-up due_date urgency are the correct defaults. Setting this in the package acceptance criteria is the cleanest time to do it — before the template is written with a column-sorted table as the assumed shape.

2. **Make follow-ups the primary content, not a secondary column.** The package spec for Tracker should explicitly describe where follow-up items appear relative to the job list — not leave it implicit. The recommendation is: overdue and due-today follow-up items as a named section at the top of the screen, above the job list. The job list follows. This decision should be in the acceptance criteria, not discovered during implementation.

3. **Distinguish overdue from due-today items visually.** Both come from the same `list_due_followups()` call, but they represent different urgency levels. The display — whether through color, label ("Overdue: 3 days"), or section separation — should make the distinction immediately readable without requiring the user to check the date column.

4. **Decide the `selected`-state placement explicitly.** `selected` jobs are user-created commitments, not employer-process milestones. Whether they belong in the same job list as `interview` and `applied` jobs, or in a separate "Ready to Apply" section, should be settled in Package 5a scoping — not left to default list behavior. Both are defensible choices; the risk is having no choice at all.

5. **Decide terminal-state visibility before Tracker ships.** Whether `rejected` and `ghosted` jobs appear in the default Tracker view, or require an explicit filter to show, determines how useful the screen is as active applications accumulate. A default-visible terminal state list will eventually dominate the screen. The recommendation is to default to hiding terminal states, with an option to show them — but any conscious decision is better than no decision.

6. **Settle the Job Detail return path at the same time as Tracker scoping.** The hardcoded "Back to Review Queue" link in `job_detail.html` will produce a wrong-context return for Tracker users. Decide the return-path convention before Tracker ships — either contextual (back to wherever the user came from) or consistent (always back to Review Queue, with global nav for Tracker). The navigation study's "actions return to originating screen" principle suggests contextual is preferred, but the implementation approach is Anna's to determine.

7. **Flag the upcoming-follow-up service gap to Anna at scoping time.** `list_due_followups()` cannot return future-dated items without an `as_of` override. If Package 5a or 5b intends to surface an upcoming-follow-up section (the planning horizon opportunity in §5.6), this constraint needs to be surfaced to Anna as a service-layer consideration before the template design assumes the data is available.

8. This document is advisory only. It proposes no roadmap change, no architecture change, and no governance modification. All design decisions named above require Project Master authorization before they carry any binding weight.
