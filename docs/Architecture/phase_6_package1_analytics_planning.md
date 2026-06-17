# Phase 6 Package 1 — Analytics Expansion Planning Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. No implementation authorization implied. No governance modification. No roadmap change.
**Date:** 2026-06-17
**Authority basis:** Phase 6 package structure, current Metrics screen, existing MetricsService and FunnelReporter architecture.

---

## Executive Summary

The current Metrics screen is seven things: a count, a state distribution table, a source breakdown table, a stretch category table, a source effectiveness table, a match-score average table, and three median-transition-day numbers. That is a useful foundation but it is a snapshot of inputs — it does not answer the questions an operator actually asks when standing back from the daily pipeline to evaluate strategy.

The most consequential missing capability is **funnel conversion rates**. The screen currently shows how many jobs are in each state but not what fraction moved from the prior state. An operator who sees "12 applied, 3 screen" has no reference point for whether 25% is good, bad, or typical for their sources. Without conversion rates, the screen is a status board rather than a diagnostic tool.

The second most consequential missing capability is **score calibration insight**. The screen shows average match_score by state, but a single average conceals the distribution. Is the grader accurately ordering jobs, or is the scoring algorithm misfiring? Are jobs that advance to interview actually higher-scoring than jobs that are rejected? This is a strategy-validation question that the current metrics cannot answer.

The third missing capability is **stretch strategy feedback**. `by_stretch` data is already computed and rendered, but it shows only counts — not conversion rates per stretch category. Whether long_shots are worth the application cost is currently unanswerable from the dashboard.

Beyond these three analytical gaps, there are two structural gaps:

1. `by_discipline_state` and `by_location_metro` are declared as `FunnelStats` fields and computed as placeholder empty dicts by `FunnelReporter.compute()`. They were designed for but never implemented. Discipline and location breakdowns would be the most directly actionable missing segmentations.

2. The schema contains rich data across `generated_docs`, `job_keywords`, `app_transitions`, `source_health`, and `firms` that is never surfaced in analytics. The keyword coverage data, document quality metrics, and time-in-state data are all computable from existing tables. They are simply not queried.

The information architecture challenge is that analytics data has three distinct time horizons — strategic (where am I?), operational (what happened today?), and historical (how is this evolving?) — and these three layers should not share a single screen. The current Metrics screen is predominantly strategic; the current Source Health screen is operational. A third surface (trends or pipeline history) is needed for the historical layer, and the boundary between them must be explicit to prevent Metrics from bloating into an unsorted data dump.

---

# Part 1 — Analytics Gap Assessment

## 1.1 What Currently Exists

**FunnelReporter.compute() populates and returns:**

| Field | Description | Current render |
|---|---|---|
| `total_jobs` | Total job count across all states | "Total ever discovered: N" — headline |
| `by_state` | Count per `app_state` | State Distribution table |
| `avg_match_by_state` | Mean `match_score` per state (null-safe) | Column in State Distribution table |
| `by_source` | Count per source per state | Source Breakdown table (source × state flat table) |
| `by_stretch` | Count per `stretch_category` per state | Stretch Category Analysis table (conditional render) |
| `response_rate_by_source` | Per source: applied, responded, response_rate, screened, screen_rate, interviewed, interview_rate | Source Effectiveness table |
| `median_days` | Median days: applied→response, applied→screen, applied→terminal | Time to Response list |

**What the route passes to the template:**
`metrics.py:40-51` — passes all seven fields above. `by_discipline_state` and `by_location_metro` are intentionally excluded per the route docstring ("FunnelReporter does not populate; they are not passed to the template").

**What FunnelStats declares but FunnelReporter never assigns:**

- `by_discipline_state: dict[str, dict[str, int]]` — designed to show discipline_tags breakdown by state; currently always `{}` at runtime
- `by_location_metro: dict[str, dict[str, int]]` — designed to show metro area breakdown; currently always `{}` at runtime

These two fields have been placeholder-empty since the metrics module shipped. The Metrics product study confirmed this via grep (they appear only as field declarations, never as assignment targets in `compute()`).

---

## 1.2 What Is Missing — Schema-Grounded Analysis

The following analytical capabilities are not currently computed. Each is grounded in data that already exists in the schema.

### From the `jobs` table

**Funnel conversion rates** — the most critical missing calculation. `by_state` gives counts; dividing adjacent funnel stages gives the fraction that advanced at each step. The `FUNNEL_STAGES` constant in `funnel.py` already defines the ordering: `discovered → presented → selected → applied → screen → interview → offer`. Conversion rate = count(stage N+1) / count(stage N). This is arithmetic on existing data, not new queries.

**Score distribution (min / max / quartiles)** — `avg_match_by_state` is computed but score distribution is not. A job pool with mean 0.71 could be concentrated at 0.71 (narrow band, consistent grader) or bimodal at 0.90 and 0.52 (algorithm is sorting well into two tiers). Quartiles (25th/75th percentile) per state would distinguish these cases and validate whether the scoring algorithm is ordering jobs meaningfully.

**LLM grade distribution** — `llm_grade` (Strong / Good / Marginal / Pass) and `llm_fit_score` (1–5) are populated for graded jobs but not surfaced in any metric. The distribution of LLM grades among presented jobs answers: is the grader selecting mostly Marginal jobs (threshold too low) or mostly Strong jobs (threshold well-calibrated)?

**LLM-outcome correlation** — do jobs that advance to interview have higher `llm_fit_score` than jobs that are rejected? This is the most direct empirical test of whether LLM grading is adding signal. Requires grouping `llm_fit_score` by outcome state — currently not computed.

**Stretch category conversion rates** — `by_stretch` shows counts per stretch_category × state, which is rendered on the Metrics screen. What is NOT shown: the conversion rate within each stretch category. For a long_shot job, what fraction reach `selected`? `applied`? `screen`? This answers the strategic question "is it worth applying to long_shots?"

**Remote / hybrid breakdown** — `remote_flag` (yes / no / hybrid / unknown) exists on every job. No metric aggregates this. An operator whose scoring strongly favors remote roles should be able to see whether the presented/applied mix reflects that preference.

**Discipline breakdown** — `discipline_tags` is a JSON array per job. `by_discipline_state` was designed for this breakdown but is never populated. Knowing which discipline tags appear most often among presented vs. selected jobs would validate whether the discipline weighting in scoring.yaml is working as intended.

**Salary range distribution** — `salary_min` and `salary_max` exist but are sparsely populated (many postings don't include salary). A conditional display when salary coverage reaches a useful threshold (e.g., N ≥ 20 jobs with salary data) would surface whether the presented job pool is in the expected compensation range.

**Knockout frequency analysis** — `ko_*` fields flag work authorization requirements, experience floors, clearance requirements, EIT/PE requirements, and degree requirements. Knowing what fraction of discovered jobs have each knockout requirement would surface whether the discovery pipeline is pulling jobs that would be knocked out in bulk — an ingest-configuration signal, not an application-management signal.

**Time-in-current-state** — `app_transitions` tracks when each job reached its current state. How long has a job been sitting in `selected`? In `applied`? In `acknowledged`? The median_days fields track historical transitions that completed; time-in-current-state tracks the current pipeline's age distribution. A job that has been in `applied` for 30 days is behaviorally different from one that has been there for 3 days, even though both count equally in `by_state`.

### From the `generated_docs` table

**Document keyword coverage summary** — `keyword_coverage` (% of JD top-tier keywords hit), `keywords_hit`, and `keywords_missed` are stored per generated document. No metric aggregates these across documents. An operator who sees average keyword coverage dropping over time knows the document generator is drifting; one who sees specific keywords consistently missed knows which gaps to address in the profile.

**Generation volume and recency** — `generated_at` per document records when generation occurred. How many documents were generated in the last 7 days? What is the typical lag between a job reaching `selected` and its documents being generated? This is an operational signal that belongs in the analytics layer, not the Source Health layer.

### From the `app_transitions` table (extended)

The current `median_days` computation uses `app_transitions` but only for three specific transition pairs. Extended transition analytics could surface:

**Full transition velocity** — not just applied→response but presented→selected, selected→applied, acknowledged→screen, screen→interview. Each leg has a different decision-maker: presented→selected is the operator's decision speed; selected→applied and beyond is the employer's.

**Historical funnel snapshot** — if `transitioned_at` timestamps are grouped by week or month, week-over-week funnel state can be reconstructed. "How many jobs entered `presented` state this week vs. last week?" is the trend question Metrics cannot currently answer at all.

**Stale-pipeline detection** — jobs where the most recent `app_transitions` row is older than N days in a non-terminal state. Currently the TrackerService `list_due_followups()` surfaces some of this, but a metric-level count ("12 jobs with no state change in 14+ days") would give the operator a pipeline-stagnation signal without navigating to the Tracker.

### From the `source_health` table (analytics angle)

Source Health (Phase 6 Package 1 authorization) surfaces per-run health. There is an analytics dimension to source health data that belongs on Metrics, not Source Health: **source yield over time**. The average `records_fetched` per source per week, and whether that trend is increasing or decreasing, is a strategic question about source quality. The specific error that caused today's failure is an operational question that belongs on Source Health.

The distinction: **Source Health is diagnostic** (why did this run fail?), **Metrics is strategic** (is this source worth maintaining?).

### From the `firms` table

**Target firm pipeline penetration** — `manual_priority = 'target'` marks firms the operator has explicitly prioritized. What fraction of target firms have yielded any jobs in the pipeline? What fraction have resulted in applications? This closes the gap between firm strategy (set by the operator in firms.yaml) and pipeline outcomes (recorded in jobs). Currently there is no surface that connects these two tables analytically.

---

## 1.3 Insights Operators Cannot Currently See

Organized by the question an operator would actually ask:

**"Is my scoring algorithm working?"**
Not answerable. The screen shows avg_match_by_state but not the distribution, not whether selected jobs are meaningfully higher-scoring than non-selected ones, and not whether LLM grades correlate with outcomes.

**"Should I apply to long_shots?"**
Not answerable. The stretch category table shows counts but not conversion rates. An operator cannot determine from the Metrics screen whether long_shot applications produce any interviews.

**"Which source is actually worth my time?"**
Partially answerable. Source Effectiveness shows response rates by source, but only for the applied-and-beyond funnel. The screen cannot show: which source produces the highest-quality presented jobs (by match_score or LLM grade), which source has the best discovery-to-interview conversion rate, or whether a source's yield is trending up or down.

**"Is my pipeline healthy right now?"**
Not answerable. The screen shows a point-in-time count per state but not pipeline age, stale-job count, or how the pipeline size has changed over the past week.

**"Are my documents competitive?"**
Not answerable. Keyword coverage is computed and stored per document in `generated_docs` but is never surfaced in any metric. An operator has no view of average keyword coverage or which keywords are systematically missed.

**"Am I targeting the right companies?"**
Not answerable from Metrics. No surface connects `manual_priority = 'target'` firm designations to pipeline outcomes.

**"Is my search getting better or worse over time?"**
Not answerable. All Metrics data is point-in-time. Week-over-week or month-over-month funnel changes are invisible.

**"Are my discipline preferences correctly reflected in the pipeline?"**
Not answerable. `by_discipline_state` is always empty. Discipline-level breakdowns are unimplemented.

---

# Part 2 — Analytics UX Design

## 2.1 Design Principles

Before designing individual workflows, three principles should guide all analytics UX decisions:

**Principle 1 — Questions first, data second.** Every analytics surface should be organized around the question an operator asks, not the table structure that holds the data. "Is my scoring working?" is the question; `avg_match_by_state` is one piece of data that partially answers it. Design the surface to answer the question completely, then select the data needed.

**Principle 2 — Point-in-time and trend are different surfaces.** Point-in-time analytics (what is my pipeline state right now?) and trend analytics (how is my pipeline changing over time?) serve different decision-making contexts and have different data requirements. They should not be merged into a single scrolling page. The Metrics screen is the right home for point-in-time; trends need a dedicated surface or a clearly delimited section.

**Principle 3 — Every metric should lead to a decision or an action.** If a metric cannot change operator behavior, it is vanity data. The design should verify, for each proposed metric: what does the operator do differently if this number is high vs. low? Metrics that don't have an answer to that question should be deprioritized.

---

## 2.2 Workflow: Trend Analysis

**The question being answered:** Is my job search trajectory improving, stagnating, or deteriorating?

**Decision context:** An operator checks trend data weekly or after a significant event (completed a batch of applications, changed a scoring parameter, added a new firm). The decision triggered is strategic recalibration — "should I change my approach?"

**Information the trend workflow needs:**

- Weekly new job discoveries (count of jobs where `first_seen` falls in each week)
- Weekly funnel state changes (transitions per week)
- Weekly application volume (jobs reaching `applied` state per week)
- Source yield per week (average `records_fetched` per source per week from `source_health`)
- Pipeline size over time (count per state at weekly intervals — reconstructed from `app_transitions`)

**Operator experience design:**

The trend workflow is not a daily-check workflow. An operator arriving at this surface has a specific question: "what's my trajectory over the past 30 days?" The design should answer this without requiring interpretation of raw time-series data.

*Landing state:* "Your pipeline added N jobs in the past 7 days (vs. M the prior 7 days). Application rate: N this week vs. M last week."

*Primary display:* A three-row summary comparison — discovery rate, application rate, interview/response rate — comparing this week to the prior period. Numbers only; no charts. Charts require a visualization library that does not exist in the current Jinja2/plain-HTML stack. Three rows of "this week / last week / change" comparisons are readable as plain HTML tables and fully informative.

*Drill-down:* Source yield trend — which source is contributing more or fewer discoveries this week than last? This surfaces the strategic version of what Source Health surfaces operationally (was today's run healthy?).

*What this workflow should NOT include:* Day-level granularity (too noisy for a weekly check workflow), predictive analytics ("at this rate, you'll have an interview in N weeks" — spurious at small n), or visualization of states that don't yet have enough data for a meaningful trend (any state with fewer than 10 jobs in the time window should show "not enough data").

---

## 2.3 Workflow: Source Comparison

**The question being answered:** Which source is the most valuable, and is that consistent with my configuration?

**Decision context:** An operator is deciding whether to invest time seeding more firms for a specific ATS type, or whether to deprioritize a source that isn't converting. The decision is configuration-level — adjusting firms.yaml, adding API keys, or filing a Source Health investigation.

**Information the source comparison workflow needs:**

- Per source: jobs discovered, jobs presented (passed grading threshold), jobs selected, jobs applied
- Per source: discovery → presented conversion rate, presented → applied conversion rate
- Per source: average match_score among presented jobs (quality signal, not just volume)
- Per source: average LLM grade distribution among presented jobs
- Per source: response rate and interview rate (from existing `response_rate_by_source`)
- Per source: yield trend over last 30 days (from `source_health.records_fetched`)

**Operator experience design:**

Source comparison is currently split across two Metrics sections (Source Breakdown and Source Effectiveness) that tell different parts of the story. Merging them into a single source-comparison row gives a complete picture.

*Landing state:* A single table, one row per source, with columns: Discovered | Presented | Present Rate | Applied | Response Rate | Avg Match Score | Trend.

*The "Trend" column* is the key addition to what currently exists. It would show a simple signal (↑ more this week than last / ↓ fewer / ≈ stable) derived from `source_health.records_fetched`. This is not a chart — it's a directional indicator that tells the operator whether a source is gaining or losing yield without requiring a separate trend surface visit.

*Contextual action: "View in Source Health"* — a link on each source row to the Source Health drill-down for that source. Source comparison asks "is this source worth keeping?"; Source Health answers "why is this source behaving this way?" These are complementary questions; the link between them closes the diagnostic loop.

*What this workflow should NOT include:* Firm-level breakdown within a source (that is Firm Intelligence territory), or per-adapter health status (that belongs on Source Health, not Metrics).

---

## 2.4 Workflow: Funnel Diagnostics

**The question being answered:** At which stage am I losing jobs, and is that the expected loss point?

**Decision context:** An operator is assessing pipeline efficiency. Are too many discovered jobs never getting presented (scoring threshold too high, or grading floor too strict)? Are too many presented jobs never getting selected (presentation framing is off, or the operator is passing on competitive opportunities)? Are too many selected jobs never getting applied (documents aren't being generated fast enough)?

**Information the funnel diagnostics workflow needs:**

- Stage-by-stage counts: discovered → presented → selected → applied → screen → interview → offer
- Stage-by-stage conversion rates (the % that moved forward at each stage)
- Qualitative context for each conversion loss point (what typically happens at this stage?)
- Per-stage score distribution (do the jobs that advance have higher scores than those that don't?)
- Time-in-current-state for active jobs (how long has each stage been holding its current jobs?)
- Comparison: stretch category conversion rates (long_shot vs. qualified vs. competitive_stretch)

**Operator experience design:**

The funnel diagnostic view is a vertical pipeline view — each stage displayed in order, with count, conversion rate from prior stage, and average match_score of jobs currently at that stage.

*Landing state:* "Your funnel: N discovered → M presented (X%) → P selected (Y%) → Q applied (Z%) → ..."

*Each stage row includes:*
- Stage name
- Current count
- Conversion rate from prior stage (% of prior stage that advanced here)
- Average match_score at this stage
- A qualitative interpretation: "Low presented→selected rate may indicate the presentation threshold is high, or opportunities are not being prioritized" — template-static interpretations based on threshold comparisons to reasonable ranges

*Stretch category conversion panel:* Below the main funnel, a secondary table showing the conversion rate from `discovered` to `applied` for each stretch category. The key question: are `long_shot` applications producing any interviews? This makes the stretch strategy empirically evaluable for the first time.

*Time-in-stage indicator:* For active (non-terminal) stages, the median age of jobs currently at that stage (days since last transition). A flag appears if median age exceeds a threshold (e.g., "Applications in 'applied' state have been waiting an average of 21 days — consider following up"). This is derived from `app_transitions` and does not require any new schema.

*What funnel diagnostics should NOT include:* Per-job drill-down (that is the Tracker's job), any mutation actions (Metrics is read-only by design), or source-specific funnel breakdowns (that belongs in Source Comparison).

---

## 2.5 Workflow: Response Rate Analysis

**The question being answered:** Which applications are producing employer responses, and what do successful applications have in common?

**Decision context:** The operator has been applying for several weeks and wants to understand which approach is working. This is a retrospective analysis workflow, not a daily check.

**Information the response rate analysis workflow needs:**

- Overall response rate (% of applied jobs that received any employer-initiated contact)
- Response rate by source (current `response_rate_by_source` — already computed)
- Response rate by stretch category (new — are long_shots actually responding?)
- Time to response distribution: median days applied→acknowledged, applied→screen, applied→terminal (current `median_days`)
- Extended time metrics: applied→interview, screen→interview, interview→offer (new — additional transition pairs)
- Response rate by LLM grade (new — are "Strong" LLM-graded applications responding at higher rates?)
- Ghost rate: % of applied jobs reaching `ghosted` state (a "no response by timeout" terminal state)

**Operator experience design:**

Response rate analysis is an evaluative retrospective — the operator is looking back over completed applications, not managing active ones. The design should make pattern recognition easy.

*Landing state:* A summary header — "You have applied to N jobs. Response rate: X%. Average time to first response: N days."

*Source breakdown:* The existing Source Effectiveness table, improved with response-rate-by-stretch and confidence signals (n= counts displayed, entries with n < 5 shown as "insufficient data").

*LLM grade correlation panel:* A table showing, for each LLM grade category (Strong / Good / Marginal / Pass), the number applied, number responded, and response rate. This is the empirical validation surface for LLM grading — if Strong jobs don't respond at meaningfully higher rates than Marginal ones, the LLM grader is not adding signal and its threshold should be reconsidered.

*Time distribution display:* The three existing `median_days` values plus three new transition pairs (applied→interview, screen→interview, interview→offer). Displayed as a timeline: "Typical path: applied → responded in N days → screened in M more days → interview in P more days." This is more interpretable than a flat list of transition pairs.

*What response rate analysis should NOT include:* Individual job performance (Tracker handles that), predictive response probability for active applications (spurious at small n), or email/phone log integration (out of scope for current architecture).

---

## 2.6 Workflow: Score Calibration Review

**The question being answered:** Is the scoring algorithm ordering jobs correctly, and is the grading threshold set at the right level?

**Decision context:** This is an occasional (monthly or after a threshold adjustment) review workflow, not a daily check. The operator is validating that the algorithm is doing what it was designed to do — pushing the best-fit jobs toward the top of the presented queue.

**Information the score calibration workflow needs:**

- Score distribution per state: min / 25th percentile / median / 75th percentile / max for each `app_state` (not just averages)
- Outcome-by-score brackets: for jobs at 0.60–0.69, 0.70–0.79, 0.80–0.89, 0.90+, what fraction reached each outcome?
- LLM fit score vs. match_score correlation: do high `match_score` jobs also tend to have high `llm_fit_score`? Divergence signals that one scoring mechanism is misfiring.
- Stretch category score overlap: what is the score range of `long_shot` vs. `qualified` jobs? Do they overlap (suggesting stretch category assignment may not be calibrated)?
- Threshold sensitivity: how many currently-presented jobs would be added or removed if GRADING_FLOOR moved to 0.50 / 0.60 / 0.65 / 0.70? (Derived from current job scores — no new data collection.)

**Operator experience design:**

Score calibration is a diagnostic review, not a management view. The operator is asking: "should I change my settings?"

*Landing state:* "Current grading threshold: 0.55. Jobs presented: N. If raised to 0.65: N-M jobs presented."

*Score distribution table:* One row per state, columns: min / Q1 / median / Q3 / max / avg / n. This gives the operator a statistical picture of how scores distribute across the funnel. A well-functioning algorithm shows increasing score distributions as you move down the funnel (selected > presented > discovered).

*Score bracket outcome table:* Rows are score ranges (0.55–0.64 / 0.65–0.74 / 0.75–0.84 / 0.85+), columns are terminal and advanced states (selected / applied / screened / interviewed / rejected / ghosted). Each cell shows the count for that bracket-state combination. This is the empirical validation that high-scoring jobs are actually advancing further.

*LLM calibration panel:* A table of LLM grades (Strong / Good / Marginal) compared to the distribution of match_scores within each grade category. If "Strong" LLM grades have similar match_scores to "Marginal" ones, the two scoring mechanisms are not aligned.

*Threshold sensitivity table:* A single table showing how many jobs would be presented at each threshold value. Simple count queries against current job data.

*What score calibration should NOT include:* Per-job score editing (scores are algorithm outputs, not configurable), LLM prompt inspection (architecture territory), or scoring.yaml editing (configuration territory, not analytics territory).

---

# Part 3 — Candidate Analytics Features

## 3.1 High Value / Low Effort — Do First

These can be implemented primarily through new SQL aggregations or arithmetic on existing data structures. No new tables, no new schema, no new infrastructure.

| Feature | Value | Why low effort | Data source |
|---|---|---|---|
| Funnel conversion rates (presented→selected→applied→...) | Highest — the most-asked question the screen cannot answer | Arithmetic on existing `by_state` dict; no new query | `by_state` (already computed) |
| Score distribution (Q1/median/Q3 per state) | High — makes avg_match_by_state actually diagnostic | Add percentile columns to existing `_avg_match_by_state()` query | `jobs.match_score` |
| Stretch category conversion rates | High — validates long_shot strategy empirically | Arithmetic on existing `by_stretch` dict | `by_stretch` (already computed) |
| LLM grade distribution across presented jobs | High — validates grader calibration | One new GROUP BY query on `jobs.llm_grade` | `jobs.llm_grade` |
| Confidence signals (n= counts on source effectiveness) | Medium — prevents misreading small-n rates as significant | Add n to response rate display; data already present | `response_rate_by_source` (already computed) |
| Remote / hybrid breakdown | Medium — validates remote preference is reflected in pipeline | One new GROUP BY on `jobs.remote_flag` | `jobs.remote_flag` |
| Contextual links from Metrics to Tracker / Source Health | High for usability — resolves the dead-end problem | Template navigation links; no data changes | N/A — template change |
| `total_jobs` framing refinement | Low-medium — prevents vanity read | Text label change in template | N/A — template change |
| Extended time metrics (applied→interview, screen→interview) | Medium — completes the transition timeline | Add two transition pairs to `_median_transition_days()` | `app_transitions` (already queried) |
| Threshold sensitivity table | Medium — makes calibration review actionable | COUNT queries filtered by score thresholds | `jobs.match_score` |
| Time-in-current-state summary | High — pipeline stagnation is currently invisible | JOIN `jobs` to most-recent `app_transitions` row per job | `jobs` + `app_transitions` |

---

## 3.2 High Value / High Effort — Plan Carefully

These require new queries against multiple tables, new data structures in FunnelStats, or new analytical screens with distinct UX.

| Feature | Value | Why high effort | Notes |
|---|---|---|---|
| Discipline breakdown (populate `by_discipline_state`) | High — validates discipline weighting in scoring.yaml | SQLite JSON array parsing across thousands of jobs; complex aggregation | The field exists on FunnelStats; the query does not |
| Week-over-week discovery and application trend | High — makes trajectory visible | Requires time-series aggregation by week from `first_seen` / `app_transitions`; new display surface | No chart library in current stack; plain-HTML table comparison is viable |
| LLM grade vs. outcome correlation | High — empirical grader validation | Requires joining `llm_grade` to terminal state outcomes across historical jobs; moderate SQL complexity | Answers the most important grader question |
| Score bracket outcome table | High — empirical scoring validation | Requires bucketing match_score into ranges and joining to outcome states; moderate complexity | Key part of score calibration review |
| Source yield trend over time | High — makes "is this source degrading?" answerable | Requires aggregating `source_health.records_fetched` by week per source | Low-to-medium SQL complexity, medium display complexity |
| Target firm pipeline penetration | Medium-high — connects firm strategy to outcomes | Requires joining `jobs` to `firms.manual_priority`; new concept not currently in FunnelStats | `FirmsService` already exists; adds an analytics bridge |
| Document keyword coverage summary | Medium — validates document quality | Requires aggregating `generated_docs.keyword_coverage` and `keywords_missed` | Surfacing a quality metric that was always hidden |
| Historical funnel snapshot (weekly) | High for trend workflow | Requires reconstructing pipeline state at historical dates from `app_transitions`; complex window queries | Needed for week-over-week trend comparisons |
| Full transition velocity (all state pairs) | Medium — completes time-to-response picture | Multiple additional transition pairs in `_median_transition_days()` | The function is generic; the pairs need to be defined |
| Response rate by stretch category | High — makes stretch strategy evaluable | Requires joining `by_stretch` logic to `response_rate_by_source` equivalent per stretch; new aggregation | Currently two separate computation paths |

---

## 3.3 Low Value / Low Effort — Fill-in Work

| Feature | Value | Why low effort | Notes |
|---|---|---|---|
| `by_location_metro` — populate from `jobs.location_city` | Low-medium — location breakdown is coarse signal | One GROUP BY on existing column | The field exists on FunnelStats; query is trivial |
| Salary range distribution | Low — sparsely populated field | GROUP BY salary bands; trivial | Limited actionability; most postings omit salary |
| LLM model distribution (which model graded which jobs) | Low — only one model in use | GROUP BY `jobs.llm_model` | Becomes relevant when second model is added |
| Grading batch success rate | Low — operational signal better suited to Pipeline Runs | GROUP BY `grading_batches.status` | Wrong screen; belongs in Pipeline Runs overview |
| Knockout field frequency (% of jobs with each KO requirement) | Low-medium | COUNT CASE expressions on KO columns | Interesting at setup time; limited ongoing value |

---

## 3.4 Low Value / High Effort — Deprioritize

| Feature | Why low value | Why high effort |
|---|---|---|
| Predictive pipeline analytics ("you'll have an interview in N weeks") | Spurious accuracy at small n; can set false expectations; not actionable | Requires modeling; no external calibration possible |
| Real-time funnel chart with live updates | A periodic snapshot is sufficient for strategy review | Requires JavaScript charting library + data refresh infrastructure |
| Keyword gap analysis across all JDs (aggregate job_keywords to profile) | Per-job keyword coverage in Documents is more actionable | Large computation across all `job_keywords` rows; limited strategic utility |
| External market benchmarking | Requires external data source with comparable role types | External API integration; no data source is available; CE-specific comparison would be needed |
| Resume performance A/B comparison | No A/B mechanism exists (one document generation path per job) | Would require architecture changes to generate multiple variants |
| Interactive score simulator | Marginal gain over threshold sensitivity table | Complex frontend state management; real-time score recomputation |

---

# Part 4 — Dashboard Information Architecture

## 4.1 The Three-Layer Model

Analytics data has three distinct time horizons, each serving a different decision-making context. The information architecture recommendation follows from making this explicit:

| Layer | Time horizon | Decision context | Current screen | Proposed screen |
|---|---|---|---|---|
| **Strategic** | Point in time | "Is my approach working?" | Metrics | Metrics (expanded) |
| **Operational** | Last run / today | "What happened today?" | Source Health | Source Health |
| **Historical** | Week / month trend | "Is this improving?" | None | Pipeline Trends (new) |

Conflating these three layers onto a single screen produces a screen that is too long, has no clear purpose, and requires the operator to mentally filter data across three different decision contexts. The current Metrics screen conflates strategic data (state distribution, source effectiveness) with operational data (some median_days are really about current wait times) without acknowledging the distinction.

---

## 4.2 What Belongs on Metrics

Metrics is the **strategic analytics** surface. Everything on this screen answers the question: "Is my job search strategy working?" The operator visits Metrics to review, recalibrate, and evaluate — not to diagnose what went wrong today or to manage specific jobs.

**Belongs on Metrics:**
- Funnel overview with conversion rates (discovered → presented → selected → applied → screen → interview → offer)
- Score distribution per state (min / median / max, not just average)
- LLM grade distribution across presented jobs
- Score bracket outcome table (are high-scoring jobs advancing further?)
- Source effectiveness (response rate, screen rate, interview rate per source — with confidence signals)
- Stretch category conversion rates (what fraction of long_shots advance to each stage?)
- Time to response (median transition days — historical, not current-pipeline age)
- Remote / hybrid breakdown of presented jobs
- Extended time metrics (applied→interview, screen→interview)
- Discipline breakdown (when `by_discipline_state` is implemented)

**Does NOT belong on Metrics:**
- Per-job navigation (Tracker)
- Run health status (Source Health)
- Source error details (Source Health)
- Grading batch status (Pipeline Runs)
- Historical trend charts (Pipeline Trends)
- Individual document quality (Documents)
- Firm configuration (Source Management)

**Boundary clarification — median_days:** The current `median_days` values (applied→response, applied→screen, applied→terminal) are historical — they describe past completed transitions. They belong on Metrics as a response-rate-analysis input. The time-in-current-state metric (how long have active jobs been sitting in their current states?) is also strategic but forward-looking — it also belongs on Metrics, clearly labeled as distinct from historical median times.

---

## 4.3 What Belongs on Source Health

Source Health is the **operational analytics** surface. It answers: "What happened during the last run, and is a source in a recoverable state?"

**Belongs on Source Health:**
- Per-source last-run status (ok / empty / error / quarantined)
- Error class and error detail for the most recent failure
- Records fetched in the last run vs. previous run (immediate comparison)
- Circuit state (closed / open) and quarantine timeline
- Heal action taken (if any)
- Active firm count per source adapter
- Contextual link to source in Source Comparison (on Metrics)

**Does NOT belong on Source Health:**
- Long-term source yield trend (Metrics / Pipeline Trends)
- Per-source application outcomes (Metrics)
- Aggregate response rates by source (Metrics)
- Grading batch outcomes (Pipeline Runs)
- Job-level content for sources (Review Queue)

**Boundary clarification — records_fetched trends:** A single comparison (last run vs. prior run) is operational and belongs on Source Health. A weekly trend of records_fetched over 4 weeks is strategic and belongs on Metrics (Source Comparison panel) or Pipeline Trends. The distinction: operational data is "is this working right now?" and strategic data is "is this source worth investing in?"

---

## 4.4 What Belongs on a Future Analytics Screen

A future **Pipeline Trends** or **Analytics History** screen would host the historical layer — trend data that requires aggregation over multiple time periods.

**Would belong on Pipeline Trends:**
- Week-over-week discovery volume (jobs with `first_seen` in each week)
- Week-over-week application volume (jobs transitioning to `applied` per week)
- Weekly source yield trends (average `records_fetched` per source per week from `source_health`)
- Historical funnel snapshots (pipeline state counts at weekly intervals, reconstructed from `app_transitions`)
- Application outcome timeline (when did responses arrive relative to application dates?)

**What Pipeline Trends is NOT:**
- A replacement for Metrics (Metrics handles point-in-time strategic analytics)
- A replacement for Source Health (Source Health handles per-run operational diagnostics)
- A per-job log (that is Application Tracker + Job Detail)

**Timing consideration:** Pipeline Trends requires historical data accumulation to be meaningful. A search that has been running for 2 weeks has insufficient data for meaningful weekly trends. The screen should detect low-data conditions and surface an appropriate message: "Trend data becomes meaningful after 4+ weeks of pipeline runs. Check back later." This prevents the operator from drawing premature conclusions from insufficient data.

---

## 4.5 Boundary Cases and Open Questions

**Where does discipline breakdown go?** Discipline-level analytics (by_discipline_state) answers the strategic question "are my discipline preferences reflected in what's getting presented?" — this is a Metrics question. If it also shows which disciplines are producing employer responses, it remains strategic. If it shows "Discipline X had a failure on today's run," that is Source Health. Discipline analytics belong on Metrics.

**Where does keyword coverage go?** Per-job keyword coverage belongs on the Documents screen (already present in the Documents service design). Aggregate keyword coverage across all generated documents (average %, most-missed keywords across the set) is a strategic quality metric that belongs on Metrics. The distinction is per-job (Documents) vs. aggregate pattern (Metrics).

**Where does target firm penetration go?** Firm strategy connects two domains: the firms configuration (Source Management / Firm Registry) and the pipeline outcomes (Metrics). Target firm penetration — "of my 12 target firms, 7 have yielded pipeline jobs, 2 have produced applications" — is strategic and belongs on Metrics. The firm's operational status (circuit state, last successful fetch) belongs on Source Health.

**Where does time-in-current-state go?** This is a borderline case. Time-in-current-state for active jobs tells the operator: "your 4 'acknowledged' jobs have been sitting there for an average of 18 days — consider following up." This is closer to the Tracker's follow-up functionality than to strategic Metrics. However, at the aggregate level (not per-job), it is a pipeline-health signal that belongs on Metrics. At the per-job level, it belongs on Tracker. The Metrics surface should show the summary (median age per state); Tracker should surface the individual jobs.

---

# Deliverable Summary

| Deliverable | Location in this document |
|---|---|
| Executive summary | Pages 1–2 |
| Analytics gap assessment | Part 1 (§1.1–1.3) |
| Analytics UX vision | Part 2 (§2.1–2.6) |
| Candidate feature ranking | Part 3 (§3.1–3.4) |
| Information architecture recommendations | Part 4 (§4.1–4.5) |

---

*This document is advisory only. It proposes no roadmap change, no governance change, no phase assignment, and no implementation authorization. Everything in this document remains preliminary planning until explicitly authorized by Project Master.*
