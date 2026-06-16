# Dashboard Information Architecture Review

Owner lane: Product & Operations
Status: Planning review for Ash and Anna
Runtime impact: None
Scope: Information ownership across daily reports, weekly review, dashboard, detail views, analytics, and operational warnings

## 1. Information Ownership Map

This information architecture defines where information should live in the future Job Search Assistant experience. It is not a UI design and does not prescribe visual layout.

Accepted principles applied:

- Daily reports must remain compact, actionable, and explainable.
- Daily review target time is 10 to 20 minutes.
- Applying remains a human action outside the tool.
- SQLite is the operational source of truth.
- Google Sheets remains a secondary interaction surface.
- Dashboard should become the primary local interaction surface.

| Information type | Daily report | Weekly review | Dashboard overview | Job detail | Firm detail | Analytics |
| --- | --- | --- | --- | --- | --- | --- |
| New jobs | Top actionable subset only | Volume and quality trends | Filterable queue | Full record | Related open jobs | Source/funnel trends |
| Application tracking | Due/urgent actions only | Stage movement summary | Active pipeline | Full transition history | Firm-level history | Conversion rates |
| Follow-ups | Due/overdue only | Aging and completion trends | Reminder queue | Reminder history | Firm response pattern | Response timing |
| Interviews/screens | Today/tomorrow/soon only | Upcoming and completed summary | Active commitments | Prep/history details | Prior firm interactions | Stage conversion |
| Offers | Deadlines and critical actions | Outcome summary | Active offer tracker | Offer notes/history | Firm outcome history | Offer rate |
| Benefit scoring | Band plus top reasons | Score/outcome trend | Filter/sort facets | Full reasons/evidence | Firm benefit priors | Correlation analysis |
| Trajectory scoring | Band plus top reasons | Score/outcome trend | Filter/sort facets | Full reasons/evidence | Firm trajectory priors | Correlation analysis |
| Firm intelligence | Decision-relevant summary/warning | Target/watch/avoid trends | Firm priority badges | Applied firm context | Full approved profile | Firm outcomes |
| Generated documents | Ready/missing/failed only | Generation throughput | Document task queue | Full doc history | N/A except firm outcomes | Coverage trends |
| Source health | Action-affecting warnings only | Source reliability summary | Source health status | Job source context | ATS/source config | Failure trends |
| Operational metrics | Counts only | Summary narrative | Current state widgets | N/A | N/A | Full metric views |

Core rule: daily report answers "what should James do today?" Dashboard/detail/analytics answer "what is true, why is it true, and what patterns are emerging?"

## 2. Section-By-Section Recommendations

### Daily Report

Purpose: morning action checklist.

Belongs here:

- Today summary counts.
- Critical actions: interviews, screens, offers, deadline risks, blocking failures.
- Due or overdue follow-ups.
- Selected jobs needing submission, materials, or regeneration.
- Top new jobs for review.
- Decision-relevant benefit and trajectory bands with compact reason labels.
- Decision-relevant firm priority and stale-data warnings.
- Source/apply-link warnings that affect today's work.
- A short next-action list.

Does not belong here:

- Full job descriptions.
- Full LLM rationale.
- Full benefit/trajectory reason JSON.
- Full firm profiles or draft firm evidence.
- Full generated document history.
- Full source health logs.
- Full funnel analytics.
- Long transition histories.
- Calibration recommendations.
- Low-priority backlog unless it blocks today's work.

Daily report information should be summarized. It should link or point to detail views for full evidence.

### Weekly Review

Purpose: strategy and calibration review, separate from the daily action flow.

Belongs here:

- Funnel movement summary.
- Applications submitted this week.
- Responses received this week.
- Screens/interviews/offers/rejections/ghosting events.
- Source quality summary.
- Firm outcomes and repeated-employer patterns.
- Benefit/trajectory score bands vs selected/applied/responded outcomes.
- Generated document throughput and failure summary.
- Follow-up completion rate.
- Suggested operational adjustments for human review.

Does not belong here:

- Every raw job record.
- Every source log line.
- Every document version.
- Every benefit/trajectory evidence hit.
- Automatic scoring-weight changes.

Weekly review may be longer than the daily report, but it should still summarize first and link to analytics/detail views for investigation.

### Dashboard Overview

Purpose: primary local workspace for active job-search operations.

Belongs here:

- Review queue.
- Active application tracker.
- Follow-up queue.
- Selected jobs needing documents or submission.
- Upcoming screens/interviews/offers.
- Source health status.
- Firm review queue summary.
- Pipeline run status when implemented.
- Filters for score bands, firm priority, state, source, and warning type.

Does not belong here:

- Full evidence blobs by default.
- Full job descriptions inline by default.
- Full firm YAML inline by default.
- Raw logs by default.
- Automatic application submission.

Dashboard overview should show enough information for triage and routing. Full context belongs in detail views.

### Job Detail Views

Purpose: complete operational record for one job.

Belongs here:

- Full job description.
- Normalized job metadata.
- Full scores and score reasons.
- Benefit and trajectory hits, including source: job description or firm profile.
- LLM grade, fit score, rationale, and model metadata.
- Knockouts and location details.
- Firm context summary with link to firm detail.
- Generated document history.
- Latest/current document links.
- Keyword coverage and missed keywords.
- Application state and transition history.
- Follow-up history and unresolved reminders.
- Apply URL and source metadata.
- Notes.

Does not belong here:

- Full firm profile if a link to firm detail is available.
- Cross-source analytics beyond this job.
- Global scoring calibration charts.

Job detail is the right place for depth. It should explain why the job was scored, selected, applied, followed up, or closed.

### Firm Detail Views

Purpose: approved employer intelligence and outcome history.

Belongs here:

- Approved firm identity, aliases, parent/subsidiary notes.
- Manual priority: target, watch, neutral, ignore, avoid.
- ATS/source configuration summary.
- Firm data verification status and stale-data flag after 365 days.
- Approved benefit priors with status, confidence, source, and verification date.
- Approved trajectory priors with status, confidence, source, and verification date.
- Dashboard-only firm attributes such as internal mobility.
- Managerial path as firm-profile attribute only, not a scoring signal.
- Open jobs for the firm.
- Past applications and outcomes.
- Source health for firm-specific adapters.
- Draft review status, if surfaced in a separate review queue.

Does not belong here:

- Unapproved draft data blended with approved data.
- Scoring output for unrelated firms.
- Automatic approval actions without James review.

Firm detail should distinguish approved facts, likely claims, unknowns, stale claims, and draft material with great care.

### Analytics Views

Purpose: trends, calibration, and strategic decisions.

Belongs here:

- Response rates by source.
- Response rates by firm.
- Conversion by application state.
- Median days between stages.
- Outcomes by stretch category.
- Outcomes by benefit band: None, Low, Medium, High.
- Outcomes by trajectory band: None, Low, Medium, High.
- Generated document counts and keyword coverage trends.
- Source health trends.
- Firm outcome scoring after enough data exists.
- Advisory calibration recommendations after sufficient sample size.

Does not belong here:

- Daily action checklist items as primary content.
- One-off job decisions without aggregation.
- Automatic weight changes.
- Unreviewed firm draft claims.

Analytics should guide strategy, not interrupt daily execution.

## 3. Daily Vs Dashboard Vs Detail View Boundaries

### Daily Report Boundary

Daily report should include information only if it helps James take an action today.

Daily report should answer:

- What is urgent?
- What follow-up is due?
- What selected application needs completion?
- Which new jobs are worth reviewing now?
- What warning could change today's action?

Daily report should not answer:

- Why did every historical transition happen?
- What is the full evidence trail behind every score?
- Which source has the best 90-day trend?
- What are all firm aliases and benefit evidence URLs?
- How should scoring weights change?

### Dashboard Boundary

Dashboard should include operational breadth: queues, filters, current status, and navigation into details.

Dashboard should answer:

- What queues exist?
- What needs attention soon?
- What state is each active job in?
- Which jobs can I filter by firm, score band, state, or warning?
- Where can I inspect deeper evidence?

Dashboard should not become the raw database viewer. It should organize, not dump.

### Detail View Boundary

Detail views should include full explainability for one object.

Job detail should answer:

- What is this job?
- Why was it scored this way?
- What materials exist?
- What happened in the application lifecycle?
- What is the next action?

Firm detail should answer:

- What do we know about this firm?
- How trustworthy and fresh is that knowledge?
- How has this firm performed in James's search?
- Which open jobs and applications connect to it?

## 4. Analytics Boundaries

Analytics views should be separated from daily review to protect the 10 to 20 minute morning target.

Analytics belongs in:

- weekly review
- dashboard metrics view
- future calibration screens
- strategy/advisory reports

Analytics should not appear in daily reports except as a tiny count or warning.

Allowed daily analytics snippets:

- "3 follow-ups overdue"
- "1 source warning affecting today's results"
- "8 new jobs above threshold"
- "1 selected job has documents ready"

Not allowed in daily report:

- source conversion tables
- firm outcome ranking tables
- score correlation charts
- historical trend charts
- detailed pipeline run histories
- scoring calibration recommendations

Analytics should be advisory and human-reviewed, especially if it proposes changing search strategy, scoring weights, firm priorities, or source selection.

## 5. What Should Never Appear In Daily Reports

Never include these in daily reports unless explicitly requested for debugging:

- Raw JSON reason blobs.
- Full firm YAML.
- Unapproved firm draft content.
- Full source health logs.
- Full pipeline run logs.
- Full historical generated document list.
- Full application transition history.
- Full job descriptions.
- Long LLM rationale paragraphs.
- Calibration recommendations.
- Scoring formulas or implementation details.
- Every low-scoring discovered job.
- Every stale firm profile unrelated to today's jobs.
- Every unresolved non-urgent warning.

Daily reports can link or refer to these details elsewhere.

## 6. Summarized Versus Fully Displayed

### Summarize In Daily Report, Display Fully In Detail

- Benefit/trajectory reasons: summarize as band plus top labels; full hits in job detail.
- Firm intelligence: summarize priority/freshness/caveat; full profile in firm detail.
- Follow-up history: summarize due action; full history in job detail.
- Generated documents: summarize ready/missing/failed; full history in job detail or documents view.
- Source health: summarize action-affecting warning; full trend/log in source health view.
- LLM grading: summarize grade/score; full rationale in job detail.
- Knockouts: summarize warnings; full parsed fields in job detail.

### Display Fully In Dashboard/Detail, Not Daily

- Job description.
- Transition history.
- Generated document versions.
- Keyword coverage details.
- Full score evidence.
- Firm source URLs and extraction notes.
- Pipeline run stats and errors.

### Summarize Weekly, Analyze Fully In Analytics

- Source conversion.
- Firm outcomes.
- Response timing.
- Benefit/trajectory score effectiveness.
- Document generation throughput.
- Follow-up completion rate.

## 7. Anti-Bloat Recommendations

Daily report anti-bloat rules:

- Use fixed sections and suppress empty sections unless the absence is useful.
- Cap new jobs for review and show overflow count.
- Show at most three benefit reason labels and three trajectory reason labels.
- Use score bands instead of formula details.
- Use one primary action per item.
- Move raw evidence to detail views.
- Move trends to weekly review or analytics.
- Move firm evidence to firm detail.
- Move document history to job detail/documents view.
- Move source logs to source health view.
- Avoid repeating the same warning on every item; group when possible.

Dashboard anti-bloat rules:

- Overview pages should route to detail, not inline everything.
- Filters should support focus by state, priority, score band, source, firm, and warning type.
- Use detail views for deep evidence.
- Use analytics views for trends.
- Keep action queues separate from metrics dashboards.

Weekly review anti-bloat rules:

- Start with decisions and trends.
- Keep raw data out unless it explains a recommendation.
- Treat scoring calibration as advisory.
- Avoid daily operational tasks unless they rolled over repeatedly.

## 8. Open Questions For Ash

1. Should weekly review become a formal report artifact separate from daily reports?
2. Should dashboard IA include a dedicated Documents view, or should document history live primarily inside job detail?
3. Should firm review queue be a first-class dashboard area in Phase 5, or deferred until firm repository workflow matures?
4. Should `hold` jobs live in dashboard review queue filters, daily report sections, or both?
5. Should source health warnings appear in daily reports only when they affect presented/selected jobs?
6. Should analytics include advisory recommendations only after a minimum number of applications, such as 30 applied jobs?
7. Should generated document keyword coverage appear in daily reports only when materials are ready to submit?
8. Should offer/interview prep content be a future detail view, a generated packet, or outside scope for now?
9. Should unapproved firm drafts ever appear in daily reports as "review available," or only in dashboard/weekly review?
10. Should compact reason labels in Google Sheets mirror the daily report wording exactly?

## 9. Implementation Handoff Notes For Anna

[Target: Anna / Codex]

This is an information-architecture planning document only. Do not implement dashboard UI, schema changes, or runtime behavior from this document without Ash approval.

Implementation implications once approved:

- Design service/read-model outputs around information ownership boundaries.
- Keep daily report formatting compact and action-oriented.
- Put full job evidence in job detail read models, not daily report read models.
- Put firm evidence and approval metadata in firm detail/read models.
- Put trends and conversion rates in metrics/analytics read models.
- Keep generated document history available through job detail or document-specific read models.
- Ensure dashboard actions never submit applications.
- Preserve follow-up resolution and application state transitions through approved tracking services.
- Avoid raw SQLite row leakage into UI-facing or report-facing code.

Suggested implementation sequence after Ash approval:

1. Define separate read models for daily report items, dashboard queue items, job detail, firm detail, documents, source health, and analytics.
2. Update daily report only after the read model can enforce compact fields.
3. Add job detail and firm detail service functions before building UI screens.
4. Add analytics read models separately from daily report logic.
5. Add tests that prevent raw reason JSON, full firm data, full job descriptions, and full transition history from appearing in daily report output.
6. Keep Google Sheets as a compact secondary surface aligned with daily report summaries.

[Target: Ash / ChatGPT]

Review the open IA questions and decide which surfaces are accepted for weekly review, document history, firm review queue, hold jobs, source health warnings, and analytics thresholds. If accepted, issue synchronization notes to Software Development and Portfolio & Documentation.
