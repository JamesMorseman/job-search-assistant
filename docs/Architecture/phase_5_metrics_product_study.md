# Metrics Dashboard Product Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** What the Metrics screen should contain, how it differs from Application Tracker, which information categories are essential vs. nice-to-have vs. out-of-scope, and what product risks arise from common Metrics design mistakes.

**Grounding:** `MetricsService.get_funnel_stats()` is a thin wrapper over `FunnelReporter.compute()`, which populates these fields on `FunnelStats`: `total_jobs`, `by_state`, `by_source`, `by_stretch`, `avg_match_by_state`, `response_rate_by_source`, `median_days`. Two additional fields declared on `FunnelStats` — `by_discipline_state` and `by_location_metro` — are never assigned by `compute()` and remain empty dicts at runtime. `FUNNEL_STAGES = ["discovered", "presented", "selected", "applied", "screen", "interview", "offer"]`. `TERMINAL_STATES = ("rejected", "ghosted", "offer")`. `response_rate_by_source` skips any source with zero applied jobs.

---

## 1. Executive Summary

Every other dashboard screen answers a doing question: what should I select, what do I know about this job, what documents exist, what needs attention today. Metrics is the only screen that answers a learning question: **is this job search working?** That distinction is the governing principle for every design decision the screen requires.

The doing/learning divide has concrete consequences. Application Tracker and Metrics both derive data from the same underlying jobs table, but a user opening Tracker is in management mode — "what do I owe this employer?" — while a user opening Metrics is in analysis mode — "what is my strategy producing?" Tracker shows individual job rows the user can act on. Metrics shows aggregate patterns the user can reason about. Inlining individual jobs on Metrics, or making Tracker display aggregate rates, would blur the most important boundary in the dashboard.

The study finds six information categories currently computable from `FunnelStats` that belong on the Metrics screen, one that is nice-to-have, and two prompt categories that are out-of-scope because the service does not compute them. The most consequential finding is not about any individual category — it is about the screen's structural dead-end problem. Metrics currently has no path from an observation to the underlying data. A user who notices that one source has a 2% response rate cannot follow that observation to the actual jobs or navigate to Source Health for that source's operational status. Every aggregate Metrics surfaces is, without a contextual link, an interesting fact the user cannot act on. Addressing the dead-end at Package 6 scoping time costs far less than shipping a screen that diagnoses problems the user cannot investigate.

---

## 2. Metrics Screen Purpose

### 2.1 The Question the Screen Must Answer

The core question Metrics should answer is: **is my job search strategy working, and where specifically is it not?**

This question has several sub-questions, all of which are answerable from currently computed `FunnelStats` fields:

- Is my pipeline flowing, or are jobs stalling at a specific stage?
- Which sources are producing conversations, and which are producing silence?
- Is my scoring algorithm actually predicting which jobs respond?
- How long should I wait before following up or marking a job ghosted?
- Are my stretch applications justified by outcomes, or am I spending effort on reach roles that don't respond?

None of these questions can be answered from any other dashboard screen. Review Queue shows whether any new jobs exist. Job Detail shows one job in full. Application Tracker shows what individual active applications need. Metrics alone shows the pattern across the whole pipeline.

### 2.2 The User Mental Mode

The user opening Metrics is not managing a task. They are stepping back from individual job decisions and asking whether the overall approach is sound. This "analyst reviewing results" mode is distinct from every other screen in the dashboard, and it should influence the design:

- Information is presented as summary statistics and rates, not as rows to act on.
- The organizing principle is insight, not urgency.
- There are no action buttons on Metrics itself — actions happen on other screens after the user has identified what to investigate.
- The natural follow-through from a Metrics insight is navigation to another screen, not an in-place action.

### 2.3 How Metrics Differs from Application Tracker

| Dimension | Application Tracker | Metrics |
|---|---|---|
| Unit of information | Individual job | Aggregate across all jobs |
| User question | What do I owe this employer? | Is my strategy working? |
| Mental mode | Management / stewardship | Analysis / learning |
| Organizing principle | Urgency (follow-ups, recency) | Insight (rates, trends, correlations) |
| Action available | State transitions, resolve follow-up | None — navigation only |
| Data granularity | Row-level (one row per job) | Summary (counts, rates, medians) |
| Freshness requirement | Should reflect current state (user acts on it) | Summary can be computed on page load without live updates |
| When user visits | When something needs attention | When evaluating strategy or checking overall health |

The risk of blurring this boundary runs in both directions. Metrics that lists individual job rows becomes a second Application Tracker with no reason to exist. A Tracker that computes and displays aggregate response rates duplicates Metrics. The prior information architecture study named this risk explicitly — it bears repeating here as the foundational constraint for Package 6 scoping.

---

## 3. Information Ownership Analysis

### 3.1 What Metrics Owns Exclusively

No other screen surfaces any of the following:

- **Pipeline conversion rates** — what fraction of applications at each stage advance to the next
- **Source response rates** — which job boards actually produce employer responses
- **Time-to-response medians** — how long applications typically take to progress or terminate
- **Score calibration signal** — whether higher match scores correlate with better outcomes
- **Stretch category outcomes** — whether reach applications justify the effort

These are all aggregate findings. They require data from multiple jobs to be meaningful. No per-job screen (Job Detail, Documents) and no per-job-list screen (Review Queue, Application Tracker) can compute them.

### 3.2 What Does NOT Belong on Metrics

- **Individual job rows.** The moment Metrics shows job-level data in a table, it becomes a filtered version of Application Tracker with redundant columns. If a user needs to see the specific greenhouse jobs that produced a 2% response rate, the right path is a contextual link from Metrics to a filtered Tracker view — not inlining those rows on the Metrics page.
- **Follow-up items.** Per-job follow-ups are Application Tracker's primary differentiating content. Surfacing them on Metrics would dilute both screens.
- **Document generation history.** This is a per-job domain concern; there is no aggregate "document health" view that belongs on Metrics.
- **State transition actions.** Metrics has no mutation surface.

### 3.3 The Dead-End Problem and Its Resolution

The workflow study, the information architecture study, and the navigation architecture study all flagged the same structural gap: Metrics currently ends every user session. A user who notices "greenhouse: 2% response rate" has no path from that observation to the greenhouse jobs in Application Tracker. A user who sees "median 38 days to terminal state" has no path to the jobs that are approaching that threshold. Every insight is a fact the user cannot follow.

The resolution is navigational, not architectural. Metrics does not need to show individual jobs. It needs contextual links from each aggregate row to the screen that contains the underlying detail:

- A source row in `response_rate_by_source` → links to Application Tracker filtered by that source (or Source Health for operational context)
- A state-count row in `by_state` → links to Application Tracker filtered to that state
- An entry in `by_stretch` → links to Application Tracker filtered by stretch category

These links are navigation decisions to be settled at Package 6 scoping time, not data decisions. The underlying data for the linked views already exists in Application Tracker's service layer.

---

## 4. Metrics Categories

### 4.1 Funnel Metrics — Essential

**What it is:** The pipeline shape — how many jobs are at each stage of the funnel (`FUNNEL_STAGES`: discovered → presented → selected → applied → screen → interview → offer).

**Why essential:** This is the most immediate health indicator for the job search as a whole. A healthy funnel narrows gradually at each stage. A stalled funnel has a large pool of jobs at one stage and almost nothing progressing past it. This is not visible from any other screen.

**Currently available:** `by_state` provides counts per `app_state` across all states (including terminal). Mapping these counts to the `FUNNEL_STAGES` order gives the funnel shape. Note: `by_state` includes terminal states (`rejected`, `ghosted`) which are not funnel stages — the display should distinguish active-funnel states from terminal states.

**Display consideration:** A funnel shape (large bar for early stages, narrowing bars for later) communicates this more immediately than a table of counts. The widths of the bars at each stage tell the story at a glance.

---

### 4.2 State Distribution — Essential

**What it is:** Current-state snapshot of where all jobs sit right now, including terminal states.

**Why essential:** The funnel view (§4.1) emphasizes the active stages. The state distribution view shows the complete picture including how many jobs have reached terminal states — rejected and ghosted. These are important for understanding how the search is closing: a high ghosted count relative to rejected count suggests employers are disengaging rather than responding either way.

**Currently available:** `by_state` covers all states including terminal ones. `total_jobs` provides the denominator.

**Relationship to funnel metrics:** These two categories are closely related and could share a single display section. The distinction is frame: funnel metrics emphasizes flow and conversion; state distribution emphasizes the current snapshot including closed outcomes.

---

### 4.3 Application Counts — Essential, With Framing Requirement

**What it is:** How many applications exist in each meaningful group.

**Why essential:** The user needs to know how many active applications they are managing, not merely how many total jobs the pipeline has ever discovered.

**Critical framing requirement:** `total_jobs` from `FunnelStats` counts every job ever ingested — discovered, presented, selected, applied, rejected, ghosted. A job search running for two months with 9 active adapters could have `total_jobs = 900` while having only 8 outstanding applications. Displaying `total_jobs` without context produces the most common Metrics screen mistake: **vanity counts that make the pipeline feel productive regardless of outcome**.

The meaningful application counts are:

| Grouping | States included | What it means |
|---|---|---|
| Outstanding applications | applied + acknowledged | Applications submitted, awaiting response |
| Active pipeline | screen + interview | Applications in active employer process |
| Terminal outcomes | offer + rejected + ghosted | Applications fully resolved |
| Pending commitment | selected | User has decided to apply, hasn't yet |

`total_jobs` is best positioned as context ("out of N total jobs ever ingested") rather than a headline number.

---

### 4.4 Source Effectiveness — Essential

**What it is:** Which job boards and ATS adapters are producing real outcomes (responses, screens, interviews), and which are producing noise (applied but no progress).

**Why essential:** This is the most directly strategy-informing category on the screen. If adzuna jobs never advance past "applied" while greenhouse jobs reach "screen" at a 20% rate, the search should lean into greenhouse. No other screen surfaces this comparison. It directly informs which of the nine configured adapters deserve attention and which should be deprioritized or investigated via Source Health.

**Currently available:** `by_source` provides state counts per source. `response_rate_by_source` provides the derived rates (applied, responded, response_rate, screened, screen_rate, interviewed, interview_rate) for each source with at least one applied job.

**Important data caveat:** `response_rate_by_source` skips sources with zero applied jobs. Early in a job search, this section may be empty or show only one or two sources. The display should handle the empty-source case gracefully.

**Contextual link opportunity:** Each source row is a natural link to Source Health for that source's operational status. "This source has a 0% response rate — is that because civil engineering firms don't respond via this board, or because the adapter has been failing for three weeks?" That question requires Source Health, not Metrics, to answer. The contextual link closes the gap without Metrics needing to duplicate operational data.

---

### 4.5 Conversion Rates — Essential

**What it is:** The rate at which applications advance from one stage to the next. Distinct from raw counts: not "8 applied" but "of 8 applied, 3 responded (37.5%)."

**Why essential:** Raw counts without rates are difficult to evaluate. Knowing "2 of 5 screen-stage applications led to interviews" is more useful than knowing "2 interviews scheduled" without context. Conversion rates let the user evaluate whether each stage of the funnel is healthy or leaking.

**Currently available:** `response_rate_by_source` already computes per-source response, screen, and interview rates. Cross-source aggregate conversion rates (what fraction of all applied jobs reach screen, regardless of source) are derivable from `by_state` counts but require arithmetic not pre-computed by `FunnelReporter`. They are displayable but need to be computed from the available data.

**Relationship to Source Effectiveness:** Conversion rates and source effectiveness are closely related — the source effectiveness section naturally contains per-source rates. A separate "conversion rates" section could show aggregate cross-source rates as a complementary view.

---

### 4.6 Time-to-Response — Essential, With Data Caveats

**What it is:** How long, in median days, applications take to produce a response, reach screen stage, or reach a terminal state.

**Why essential:** This is the calibration tool for follow-up timing and patience thresholds. "Median 18 days from applied to first response" tells the user not to follow up after 3 days and not to give up after 10. "Median 42 days to terminal state" calibrates when to start treating a job as ghosted. No other screen can provide this — it requires aggregate data across all transitions.

**Currently available:** `median_days` has three computed fields: `applied_to_response`, `applied_to_screen`, `applied_to_terminal`. All three can return `None` if insufficient transition data exists (no completed transitions of that type in the DB).

**Empty-state caveat:** Early in a job search, all three values will be `None`. The screen must handle this case explicitly — displaying "Insufficient data" or a descriptive empty state rather than blank values or zeros. Zeros would be actively misleading (implying same-day responses).

---

### 4.7 Score Calibration — Nice-to-Have

**What it is:** Whether higher match scores correlate with better outcomes — specifically, whether jobs that advance to screen and interview stages have meaningfully higher average match scores than jobs that stall at applied or reach terminal states.

**Why nice-to-have rather than essential:** This category does not help the user manage their current applications or take any immediate action. Its value is meta-level: validating (or questioning) whether the scoring algorithm is predictive. If `avg_match_by_state` shows that interview-stage jobs have an average match score of 0.72 while applied-but-ghosted jobs average 0.54, the algorithm is discriminating correctly. If the averages are similar, the algorithm isn't predicting outcomes and scoring weights may need recalibration. This is a periodic strategic check, not a daily operational need.

**Currently available:** `avg_match_by_state` is computed for all states where `match_score IS NOT NULL`. It requires jobs to have been scored — early in the pipeline, ungraded jobs return no data for some states.

**Display recommendation:** A simple table of state → average match score, with enough context to compare "good" states (screen, interview) against "terminal" states (rejected, ghosted). This does not require a chart; numbers in a compact table are sufficient.

---

### 4.8 Stretch Category Analysis — Nice-to-Have

**What it is:** Whether applications in different stretch categories (core, reach, etc.) have different conversion rates. Are reach applications worth the effort?

**Why nice-to-have rather than essential:** Useful for targeting calibration — if reach applications never advance past "applied" while core-fit applications reach screen at a 30% rate, the search should deprioritize stretch roles. But this analysis requires enough applications in each stretch category to be statistically meaningful, which makes it more useful after months of searching than at the start.

**Currently available:** `by_stretch` provides state counts per `stretch_category`. Per-stretch conversion rates are not pre-computed but are derivable from these counts. Jobs with `stretch_category IS NULL` are excluded from `by_stretch`, so unscored jobs create gaps.

**Display consideration:** A table of stretch_category → (applied count, screen rate, interview rate) is the useful form. A raw count table without rates is less actionable for targeting decisions.

---

### 4.9 Follow-Up Effectiveness — Out-of-Scope for Current Service

**What it is:** Whether sending follow-up actions correlates with better outcomes — e.g., whether jobs with a resolved "follow up" action in `followup_queue` advance to the next stage more often than jobs without.

**Why out-of-scope:** `FunnelStats` contains no follow-up data. `FunnelReporter.compute()` does not query `followup_queue` at all. Computing this metric would require joining `followup_queue` resolved items with subsequent `app_transitions` entries — a non-trivial correlation query that does not exist in the current service layer. This study does not propose implementing it; it names the gap for awareness.

**Future relevance:** As the pipeline matures and more follow-up data accumulates, this becomes a genuinely valuable metric (did my Thursday follow-up lead to a Friday acknowledgment more often than not?). It is an appropriate candidate for a future enhancement to `FunnelReporter`, not for Package 6.

---

### 4.10 Discipline Analysis — Out-of-Scope (Not Computed)

**What it is:** Conversion rates broken down by civil engineering discipline (structural, transportation, water resources, geotechnical, environmental, etc.).

**Why out-of-scope:** `FunnelStats.by_discipline_state` is declared as a field but is never populated by `FunnelReporter.compute()`. It returns an empty dict at runtime. Displaying it would show nothing; computing it requires new service work outside this study's scope.

---

### 4.11 Location / Metro Analysis — Out-of-Scope (Not Computed)

**What it is:** Conversion rates broken down by metro area or geographic region.

**Why out-of-scope:** `FunnelStats.by_location_metro` has the same status as `by_discipline_state` — declared but never assigned by `compute()`. Displays as empty dict at runtime. Same reasoning applies.

---

### Summary Table

| Category | Status | Primary FunnelStats field |
|---|---|---|
| Funnel metrics | Essential | `by_state` (mapped to FUNNEL_STAGES) |
| State distribution | Essential | `by_state` (all states including terminal) |
| Application counts | Essential (with framing) | `total_jobs`, `by_state` grouped by lifecycle phase |
| Source effectiveness | Essential | `by_source`, `response_rate_by_source` |
| Conversion rates | Essential | `response_rate_by_source`, derived from `by_state` |
| Time-to-response | Essential (data-conditional) | `median_days` |
| Score calibration | Nice-to-have | `avg_match_by_state` |
| Stretch category analysis | Nice-to-have | `by_stretch` |
| Follow-up effectiveness | Out-of-scope | Not computed — no `followup_queue` join |
| Discipline analysis | Out-of-scope | `by_discipline_state` is empty at runtime |
| Location / metro analysis | Out-of-scope | `by_location_metro` is empty at runtime |

---

## 5. Risks

**5.1 — Vanity count as headline number.**
`total_jobs` is the easiest number to put at the top of the screen and the most misleading one to feature prominently. A job search that has ingested 900 jobs from nine adapters over three months will show `total_jobs = 900` regardless of how few are in active stages. A user who sees "900 jobs tracked" on the Metrics headline is reassured by a number that does not reflect whether the search is producing conversations. The meaningful count is active-pipeline jobs (`screen + interview`), not total ingested. If `total_jobs` appears at all, it should be labeled clearly as "total ever discovered" and positioned as denominator context rather than headline.

**5.2 — Empty states across multiple sections simultaneously.**
On the day Package 6 ships, the pipeline will have some accumulated data — but likely not enough to populate every section meaningfully. `response_rate_by_source` shows nothing for sources with zero applied jobs. `median_days` returns `None` for transitions that haven't occurred enough times to compute a median. `avg_match_by_state` is absent for states with no scored jobs. `by_stretch` omits categories where all jobs lack a stretch_category. A Metrics screen that shows five empty sections and one populated one on first use will feel broken rather than accurate. Handling `None` and empty-dict cases with descriptive "not yet enough data" states — not blank cells, not zeros — is essential for the screen to be useful from day one.

**5.3 — Dead-end observation with no investigation path.**
This is the highest-severity structural risk for Metrics. An observation like "adzuna: 0% response rate" or "median 62 days to terminal state" is useful only if the user can investigate it. Without a contextual link from that observation to the relevant jobs in Application Tracker, or to Source Health for the source's operational status, Metrics produces actionable-seeming data that the user cannot act on. The risk compounds over time: the more useful Metrics becomes (the more data accumulates), the more frustrating the dead-end becomes, because the user has more to investigate and no way to do it.

**5.4 — Score calibration misread when sample sizes are small.**
`avg_match_by_state` is a useful signal, but it is trivially distorted by small samples. If one interview-stage job happens to have a 0.40 match score and five ghosted jobs happen to average 0.70, the table will suggest the scoring algorithm works against the user — when the real explanation is noise in a small dataset. Without some indication of sample size (n= for each state), this table actively misleads. Displaying averages without sample sizes is worse than displaying nothing.

**5.5 — `by_discipline_state` and `by_location_metro` displayed as empty sections.**
Both fields exist in `FunnelStats` and it would be technically straightforward to render them as sections on the Metrics page. Because `compute()` never assigns them, both render as empty tables. An empty "By Discipline" or "By Metro" section that appears broken rather than clearly labeled as not-yet-available degrades the screen's credibility. These sections should either be hidden entirely until the underlying data is computed, or labeled explicitly as "planned — not yet available."

**5.6 — Metrics updated only on page load, aging between visits.**
`MetricsService.get_funnel_stats()` calls `FunnelReporter.compute()` on demand. If the dashboard is not refreshed after a state transition in Application Tracker, the Metrics view will lag behind the current state. For a single-user local tool with a small dataset, this is low risk — the computation is fast and a page reload is cheap. But if the Metrics screen does not visibly communicate when data was last computed (even as a simple "as of page load" note), users who notice a discrepancy between Tracker state and Metrics counts may distrust the screen rather than understanding the cause.

---

## 6. Opportunities

**6.1 — Score calibration as algorithm feedback loop.**
The `avg_match_by_state` table, if displayed with sample sizes and formatted to invite comparison (are "interview" job scores higher than "applied" scores?), gives the user direct feedback on whether the scoring algorithm is predicting outcomes. For a single-user civil engineering search, this is the closest thing to a ground-truth validation loop the system has. If the scores aren't predicting outcomes, the user has evidence to revisit `config/scoring.yaml` discipline weights. No external tool provides this — it is a unique value the system creates by combining its own scoring with its own outcome tracking.

**6.2 — Source pruning as direct ROI calculation.**
`response_rate_by_source` makes it straightforward to compare nine configured adapters by what they actually produce. If three sources account for all screen and interview outcomes while six produce applications that all reach terminal state without any response, the user has evidence to deprioritize those six in `firms.yaml` configuration or to investigate their Source Health records. This is a high-value strategic insight that is currently not surfaced anywhere and requires no new data collection — only a well-designed display of `response_rate_by_source`.

**6.3 — Time-to-response as follow-up calibration tool.**
`median_days.applied_to_response` gives the user a data-driven basis for follow-up timing: "the median time to first response is 22 days; I sent this application 10 days ago — it is still within normal range." Currently, follow-up timing in `followup_queue` is set manually without benchmark data. Over time, the median_days values become the benchmark. A Metrics screen that shows median time-to-response alongside Application Tracker's overdue follow-up list closes a planning loop no other screen provides.

**6.4 — Contextual links as the solution to the dead-end.**
The most impactful design opportunity for Package 6 is resolving the dead-end at implementation time rather than after ship. Every essential Metrics category has a natural forward link:

- `by_state` count row → Application Tracker filtered to that state
- `response_rate_by_source` row → Application Tracker filtered to that source, or Source Health for that source
- `by_stretch` row → Application Tracker filtered to that stretch category

These links are navigation decisions that cost nothing architecturally — Application Tracker already has the data, and `JobsService.list_jobs()` already supports `source` filtering. The design work is settling which links to include and where they appear on the Metrics page.

**6.5 — Metrics as the "is it worth continuing?" check-in.**
A job search that has been running for months accumulates enough data to answer a genuinely hard question: "am I targeting the right roles at the right firms in the right geography?" Source response rates, stretch category outcomes, and score calibration together provide the inputs for that judgment. No other screen in the dashboard, and no external tool, provides this synthesis for this specific user's civil engineering search history. Metrics that surfaces these three signals clearly — not buried in tables, but as the screen's headline insights — would be among the most differentiated features in the dashboard.

---

## 7. Recommendations for Project Master

1. **Establish Metrics' governing question at Package 6 scoping: "is my strategy working?"** All display decisions for the screen should be evaluated against whether they help the user answer that question. Individual job rows, follow-up items, and document history all fail this test and should be rejected at scoping time regardless of convenience.

2. **Require explicit handling for every `None` and empty-dict state before Package 6 ships.** `median_days` returns `None` for transitions with no data. `response_rate_by_source` returns nothing for sources with zero applied jobs. `avg_match_by_state` omits unscored states. These are not edge cases — they are the guaranteed initial state of a freshly deployed or recently reset pipeline. Each section should have a named "not enough data yet" empty state, not blank cells or zeros.

3. **Remove `total_jobs` as a headline or primary metric.** If it appears at all, it should be labeled "total ever discovered" and positioned as context for the funnel, not as a measure of pipeline health. The meaningful headline count is active-pipeline jobs (screen + interview), which the display should compute from `by_state` rather than showing `total_jobs`.

4. **Include sample sizes wherever averages are displayed.** `avg_match_by_state` is potentially misleading without knowing how many jobs are in each state. A table showing "interview: avg 0.71 (n=2)" is safer than showing "interview: 0.71" when the interpretation depends entirely on sample size.

5. **Settle the contextual link pattern at Package 6 scoping, not after.** The three natural links — state count → Tracker filtered by state, source row → Tracker filtered by source or Source Health, stretch row → Tracker filtered by stretch — should be in the Package 6 acceptance criteria. Adding them after ship is possible but less likely to happen; leaving Metrics as a dead-end compounds the problem with every new data point the user accumulates.

6. **Hide `by_discipline_state` and `by_location_metro` entirely.** Both are empty at runtime. They should not appear as sections on the Metrics page until `FunnelReporter.compute()` is updated to populate them. An empty section that looks broken is worse than no section. This is not a future deprecation — these fields have simply not been implemented yet, and the display should reflect that.

7. **Treat score calibration (`avg_match_by_state`) as a periodic review tool, not a daily operational metric.** It should appear on the Metrics screen — it is uniquely valuable for validating the scoring algorithm — but positioned lower on the page than source effectiveness and conversion rates, which are more actionable for daily strategy decisions. The user who opens Metrics to check "is greenhouse worth applying through?" should not have to scroll past a scoring calibration table to get there.

8. This document is advisory only. It proposes no roadmap change, no architecture change, and no governance modification. All display and scoping decisions named above require Project Master authorization before they carry any binding weight.
