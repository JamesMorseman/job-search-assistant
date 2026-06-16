# Daily Review Workflow Specification

Owner lane: Product & Operations
Status: Planning specification for Ash review and Anna handoff
Runtime impact: None
Scope: Morning operating experience after application tracking, reminders, benefit scoring, and approved firm intelligence exist

## 1. Morning Workflow Walkthrough

Core morning question:

> When James opens Job Search Assistant each morning, what should he see and what actions should he take?

The ideal daily review should feel like a short operating checklist, not a dashboard audit. It should answer: what needs action today, what new opportunities deserve attention, and what warnings could change the plan.

Recommended morning flow:

1. Read the daily summary.
2. Clear urgent actions first: interviews, offers, expiring deadlines, failed pipeline steps.
3. Resolve follow-ups due today or overdue.
4. Check selected jobs waiting on materials or submission.
5. Review new jobs and choose apply, skip, or hold.
6. Confirm any firm/source warnings that affect today's decisions.
7. End with a small next-action list.

A good morning review should usually take 10 to 20 minutes. If it routinely takes longer, too much dashboard-level information has leaked into the daily report.

## 2. Recommended Daily Report Structure

Daily reports must remain compact, actionable, and explainable.

Recommended report sections, in order:

1. **Today Summary**
2. **Critical Actions**
3. **Follow-Ups Due**
4. **Selected Jobs To Finish**
5. **New Jobs For Review**
6. **Firm And Source Warnings**
7. **Done / Next Actions**

### Section 1: Today Summary

Purpose: orient James in under 30 seconds.

Show:

- count of critical actions
- count of due follow-ups
- count of selected jobs needing completion
- count of new jobs for review
- count of warnings

Example:

```text
Today: 2 critical actions, 3 follow-ups due, 1 selected job waiting on submission, 8 new jobs for review, 1 warning.
```

Do not show:

- full funnel analytics
- source-by-source tables
- full state counts
- every discovered job

### Section 2: Critical Actions

Purpose: protect time-sensitive opportunities.

Include:

- interviews today or tomorrow
- screens today or tomorrow
- offer deadlines
- follow-up deadlines tied to active interviews/offers
- failed document generation for a selected job
- broken apply links for selected or high-priority jobs

Each item should include:

- company and title
- current state
- deadline or event date
- next action
- link when available
- one-line context

Example:

```text
[Critical] KPFF - Structural Designer - interview tomorrow.
Action: review job packet and send prep notes.
Context: High trajectory; firm target; latest resume ready.
```

### Section 3: Follow-Ups Due

Purpose: keep applications from silently aging out.

Include:

- applied jobs with due follow-up today or overdue
- ghosted-review items
- acknowledged jobs with no next step after the expected window
- screens/interviews with no next step after the expected window

Each item should include:

- company and title
- current state
- days since applied or last response
- recommended action
- apply URL or contact link when available
- compact rationale

Example:

```text
[Follow up] AECOM - Entry Level Structural Engineer - applied 15 days ago.
Action: check ATS portal or send short follow-up.
Why: no acknowledgment or screen recorded.
```

Do not include full transition history. That belongs in job detail or dashboard views.

### Section 4: Selected Jobs To Finish

Purpose: turn intent into completed applications.

Include:

- selected jobs missing resume or cover letter
- selected jobs with generated materials ready but not marked applied
- selected jobs where regeneration failed
- selected jobs whose apply URL may be stale

Each item should include:

- company and title
- material status: missing, ready, failed, stale
- latest resume and cover-letter links when ready
- next action
- age since selected

Example:

```text
[Submit] WSP - Junior Structural Engineer - materials ready.
Action: open apply link, submit externally, then mark applied.
Docs: resume ready; cover letter ready.
```

### Section 5: New Jobs For Review

Purpose: help James choose which jobs deserve document-generation effort.

Include only jobs worth reviewing today, capped to a manageable number. The current report cap of 30 is a technical limit; product preference is a smaller top set plus overflow count when many jobs qualify.

Each job should include:

- title and company
- fit grade
- match score
- stretch category
- location
- benefit band and top reason labels
- trajectory band and top reason labels
- firm priority and verification warning when relevant
- knockout warnings
- apply URL
- job ID
- recommended action options: apply, skip, hold

Recommended compact format:

```text
[Review] Structural Designer @ Degenkolb
Fit: Strong | Score: 82% | Stretch: qualified | Location: Seattle, WA
Benefit: Medium - PE exam support, continuing education
Trajectory: High - mentorship, design responsibility, EIT/PE path
Firm: target; verified 2026-04-10
Warnings: none detected
Action: apply / skip / hold
```

If no explicit reasons exist:

```text
Benefit: None - no explicit benefit signals
Trajectory: Low - design responsibility only
Firm: no approved profile
```

Do not include:

- raw matched phrases
- full LLM rationale
- full firm profile
- all benefit/trajectory hits
- long job descriptions

### Section 6: Firm And Source Warnings

Purpose: surface only warnings that affect today's actions.

Include:

- approved firm data older than 365 days when used in scoring/reporting
- firm profile conflict or alias uncertainty affecting a presented job
- source health failure affecting today's results
- ATS config warning for a selected or high-priority job
- draft firm profile awaiting James review only if it blocks or improves today's job decisions

Example:

```text
[Warning] Firm data for Jacobs is stale: last verified 395 days ago.
Impact: firm-derived benefit/trajectory reasons should be treated as lower confidence.
Action: review firm profile when time allows; do not block today's application if job text is strong.
```

### Section 7: Done / Next Actions

Purpose: end the morning review with a small action list.

Show:

- applications to submit today
- follow-ups to send/check today
- profile/firm/source review actions that are not urgent
- any blocked items

Example:

```text
Next actions: submit 1 application, send/check 2 follow-ups, review 1 stale firm profile later.
```

## 3. Priority Ranking Methodology

The daily report should rank work by operational urgency first, then opportunity value.

Priority order:

1. Time-sensitive commitments: interviews, screens, offer deadlines.
2. Blocking failures: document generation failed, apply link broken for selected job.
3. Due or overdue follow-ups.
4. Selected jobs ready to submit.
5. Selected jobs needing materials.
6. New high-fit jobs with strong benefit/trajectory reasons.
7. New good-fit jobs with no warnings.
8. Firm/source warnings that affect today's decisions.
9. Informational backlog items.

New job review ranking should combine:

- LLM grade
- match score
- stretch category
- knockout severity
- benefit band
- trajectory band
- firm priority: target, watch, neutral, ignore, avoid
- firm data freshness
- source reliability
- location fit

Recommended score bands for daily display:

- `None`: no explicit signals
- `Low`: weak or one limited signal
- `Medium`: meaningful but incomplete signal set
- `High`: strong, explicit signal set

Product rule: bands and reason labels should make scores understandable; they should not require James to inspect formula details during morning review.

## 4. Required Information By Section

### Today Summary

Required:

- report date
- count of critical actions
- count of due follow-ups
- count of selected jobs needing completion
- count of new jobs for review
- count of warnings

### Critical Actions

Required:

- company
- title
- current state
- event/deadline date
- next action
- relevant link
- reason for criticality

### Follow-Ups Due

Required:

- company
- title
- current state
- applied date or last transition date
- due date
- action type
- recommended action label
- note
- apply URL or contact link when available

### Selected Jobs To Finish

Required:

- company
- title
- selected date or age
- generated document status
- latest resume link
- latest cover-letter link
- apply URL
- blocker or next action

### New Jobs For Review

Required:

- company
- title
- location
- fit grade
- match score
- stretch category
- benefit band and compact reasons
- trajectory band and compact reasons
- firm priority when approved firm profile exists
- firm freshness warning when relevant
- knockout warnings
- apply URL
- job ID

### Firm And Source Warnings

Required:

- warning type
- affected firm/source/job
- impact
- recommended action
- urgency

### Done / Next Actions

Required:

- short count of remaining actions
- itemized action labels only when needed
- blocked items, if any

## 5. Action Categories

Daily report actions should use a small controlled set of labels.

Recommended action categories:

- `Apply`: James should select the job and generate/review materials.
- `Skip`: James should reject or pass on the job.
- `Hold`: keep visible but do not generate materials today.
- `Submit`: materials are ready; James should apply externally.
- `Regenerate`: materials need refresh before applying.
- `Follow up`: check portal, email recruiter, or otherwise seek status.
- `Mark applied`: James submitted externally and should update tracking.
- `Mark response`: James received acknowledgment, screen, interview, rejection, or offer.
- `Resolve reminder`: action is complete or no longer relevant.
- `Review warning`: source, firm, or data quality issue needs attention.
- `Investigate`: something is inconsistent or blocked.

Product rule: each item should have one primary action. Secondary actions can be listed only when useful.

## 6. Escalation And Exception Handling

### Critical Exceptions

Escalate to the top of the report:

- interview or screen today/tomorrow
- offer deadline within three days
- generated materials missing for a selected job James intends to apply to today
- document generation failure
- apply URL missing or broken for selected job
- selected job at an `avoid` firm
- firm intelligence conflict that changes apply/skip decision

### Standard Warnings

Show below action sections:

- firm data stale beyond 365 days
- source health degradation
- no approved firm profile for a high-interest company
- benefit/trajectory score has no reasons despite high numeric score
- repeated posting for an already applied job
- duplicate jobs with conflicting data

### Suppressed Or Deferred Information

Keep out of the daily report unless it affects today's action:

- raw firm evidence
- all source-health logs
- low-scoring jobs
- historical generated document versions
- full application transition histories
- weekly analytics
- calibration recommendations

### Escalation Targets

- Ash: governance, new statuses, priority policy, accepted product changes.
- Anna: implementation tasks after Ash approval.
- Rin: documentation/public-facing wording if workflow claims affect portfolio docs.
- Donut: workflow friction, report usefulness, follow-up process quality.

## 7. Application Follow-Up Workflow

Morning follow-up loop:

1. Review overdue follow-ups first.
2. For each item, check the ATS portal, email thread, or recruiter contact.
3. If no response, decide whether to send/check follow-up or mark reminder resolved.
4. If response exists, update state: acknowledged, screen, interview, offer, rejected, or ghosted.
5. Resolve or reschedule the reminder.
6. Add a short note only when it changes future action.

Recommended follow-up timing:

- applied with no response: due after 10 business days
- no response after 30 calendar days: ghosted review
- screen with no next step: check after 7 days
- interview with no next step: check after 7 days
- offer deadline: show three days before and on deadline day

Product rule: reminders should lead to one concrete action, not a pile of context.

## 8. Job Review Workflow

Morning new-job loop:

1. Scan top jobs sorted by grade, match, priority, and warnings.
2. For each job, inspect compact fit line, benefit/trajectory reasons, firm priority, and knockouts.
3. Choose one: apply, skip, or hold.
4. Apply means select for materials; it does not submit the application.
5. Skip means close from daily review unless a later repost changes the situation.
6. Hold means keep for later without spending generation effort.

Apply decision should usually require:

- no hard knockout, or an intentional stretch decision
- clear role relevance
- acceptable location/remote fit
- benefit or trajectory value, or unusually strong overall fit
- source/apply URL usable

Skip decision should be encouraged when:

- hard knockout exists
- firm priority is `avoid`
- role is off-discipline
- benefit/trajectory reasons are weak and fit is not strong
- posting appears stale, duplicated, or low quality

## 9. Offer And Interview Visibility

Offers and interviews should override normal job-review order.

Visible daily fields:

- company and title
- stage: screen, interview, offer
- date/time or deadline
- contact/interviewer when available
- next action
- prep or decision note
- relevant document/job links

Daily report should avoid full prep content. It should point to the item and action:

```text
[Interview] Thornton Tomasetti - Graduate Engineer - Friday 10:00 AM.
Action: prepare project examples and send thank-you reminder after interview.
```

Future dashboard/job detail can hold deeper prep notes, full timeline, and interview packets.

## 10. Firm Intelligence Visibility

Firm intelligence should appear only when it helps today's decision.

Daily report should show:

- firm priority: target, watch, neutral, ignore, avoid
- approved profile presence
- stale warning when last verified is older than 365 days
- compact firm-derived benefit/trajectory reasons when used
- caveat if firm alias is uncertain or parent/subsidiary mapping is risky

Daily report should not show:

- full firm YAML/profile
- draft firm profile data
- full evidence source list
- all aliases
- firm analytics tables

Examples:

```text
Firm: target; approved; verified 2026-05-12
Firm: no approved profile
Firm: watch; stale profile, 390 days old
Firm: avoid - review before applying
```

## 11. Benefit And Trajectory Presentation

Daily presentation should use bands plus compact reason labels.

Recommended format:

```text
Benefit: Medium - tuition assistance, PE exam support
Trajectory: High - mentorship, EIT/PE path, design responsibility
```

When absent:

```text
Benefit: None - no explicit benefit signals
Trajectory: None - no explicit trajectory signals
```

When firm-derived:

```text
Benefit: Medium - tuition assistance, PE exam support (firm)
Trajectory: High - EIT/PE path (job), mentorship (firm)
```

Rules:

- Show at most three reason labels per category.
- Prefer job-description reasons before firm-derived reasons when both exist.
- Mark firm-derived reasons when that distinction affects trust.
- Do not show raw matched text in the daily report.
- Do not let high benefit/trajectory scores hide knockouts.

## 12. Open Questions For Ash

1. Should `hold` become an accepted daily-review action, and if so is it a state, a note, or a dashboard/report filter?
2. Should daily reports cap new jobs at 10, 15, or keep the current technical maximum of 30 with a smaller recommended top section?
3. Should `avoid` firms be hidden by default or shown as warnings when a job otherwise ranks highly?
4. Should selected jobs with materials ready appear above due follow-ups or below them?
5. Should firm stale warnings appear only when firm-derived reasons influence scoring, or anytime an approved firm profile is older than 365 days?
6. Should benefit/trajectory bands have fixed numeric thresholds, or be presentation-only labels derived from signal quality?
7. Should weekly analytics be a separate report so the daily report remains compact?
8. Should ghosted items appear in daily reports until resolved, or only on the day they become ghosted?
9. Should interviews/offers be supported by a separate prep packet later, outside the daily report?
10. Should `hold` jobs expire from daily review after a fixed number of days?

## 13. Implementation Handoff Notes For Anna

[Target: Anna / Codex]

This is a planning specification only. Do not implement without Ash approval. Preserve the principle that daily reports are compact, actionable, and explainable.

Near-term implementation candidates after approval:

- Add report sections for summary, follow-ups due, selected jobs to finish, new jobs, and warnings.
- Add compact benefit and trajectory reason labels once Phase 2 reason persistence exists.
- Add compact firm priority/freshness display once Phase 3 approved firm intelligence exists.
- Surface selected jobs with generated materials ready but not marked applied.
- Surface selected jobs with missing or failed document generation.
- Include due follow-ups and ghosted-review items in the report body.
- Keep raw detail in SQLite/dashboard read models, not in the daily report.

Implementation guardrails:

- Do not submit applications.
- Do not introduce dashboard UI as part of daily report work.
- Do not add schema or state changes solely for presentation if existing data can support the first version.
- Do not mirror long reason JSON or full firm evidence into the report.
- Keep each report item oriented around one primary action.
- Add tests for section ordering, compact reason fallback, warning placement, and empty-section behavior.

Suggested implementation sequence:

1. Define report read model fields without changing runtime behavior.
2. Add formatting tests for compact report sections.
3. Add follow-up and selected-job sections using existing data.
4. Add benefit/trajectory reason labels after Phase 2 persistence lands.
5. Add firm intelligence labels after Phase 3 approved firm sync lands.
6. Reconcile daily report output with future dashboard service read models during Phase 4.
