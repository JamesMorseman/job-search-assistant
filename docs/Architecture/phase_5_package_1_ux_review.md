# Phase 5 Package 1 UX Review

**Author/Role:** Donut — Product & Operations
**Status:** Proposed — operational/UX input for Project Master (Ash) review. Not an authoritative roadmap, architecture, or governance artifact.
**Date:** 2026-06-16
**Scope:** Usability and workflow alignment of Phase 5 Package 1 — the dashboard navigation shell, startup redirect, and Review Queue screen, as a user journey. Does not evaluate code quality or architecture (see Leah's audits for that ground).

## What Package 1 actually ships, for grounding

- `/` redirects to `/dashboard/review-queue`. `/dashboard` renders the
  navigation shell on its own with no screen content.
- The navigation shell lists 8 screens; only Review Queue is a working
  link. The other 7 are inert text labeled "(not yet implemented)."
- Review Queue lists jobs where the application state is `presented`:
  company, title, location, source, match score, grade. It is read-only by
  design — there is no select, reject, or any other action anywhere on the
  screen.
- An empty-state message and a degraded-service message both exist and are
  user-facing plain language, not raw errors.

This review evaluates that experience against the daily workflow it's
meant to serve, not against how it's built.

---

## Workflow Analysis

### Does the screen support the intended daily workflow?

Only partially. The Review Queue's purpose, as scoped in prior planning
(`phase_4_operational_plan.md`, `phase_5_mvp_acceptance_criteria.md`), is
to decide — select or reject — on each presented job without leaving the
dashboard. This package supports the *looking* half of that workflow and
not the *deciding* half. A user can see what's presented, but cannot act
on any of it from this screen. Every decision still has to happen
somewhere else (CLI or Sheet), which means the daily workflow hasn't
actually moved into the dashboard yet — it has only gained an additional
place to read the same information.

### Is critical information missing?

Yes, relative to what the workflow needs to support a decision:

- **No apply link.** Even "I want to apply right now" cannot be acted on
  from this screen.
- **No stretch category or remote flag** in the rendered table, even
  though both already inform the daily review (and are typically part of
  the at-a-glance triage). These weren't expected to require new data
  collection — they just don't appear on screen yet.
- **No score rationale.** The existing daily report (CLI) already shows
  top benefit/trajectory reason labels alongside scores. The dashboard's
  first screen is, on this one dimension, less informative than the
  surface it's meant to eventually replace.
- **No way to reach a job's full detail.** Not a defect of this specific
  package (Job Detail doesn't exist yet either), but it means a user who
  wants more than six columns of information has nowhere to go from here.

### Is information density appropriate?

The current density is low, not high — six plain columns with no visual
hierarchy. That is the safer place to start (Package 1 does not suffer
from the overload risk flagged for the eventual full MVP screen), but it
under-serves the decision the workflow needs: nothing on the page
distinguishes a strong match from a marginal one beyond reading the raw
number in the Match Score column. For a workflow whose value is fast
volume triage, the absence of any visual emphasis on the column that
matters most is a real gap, not just a stylistic one.

### Does the workflow encourage efficient job review?

Partially, and for one good reason: rows already arrive ordered by match
score, so the strongest candidates surface first without any extra effort
from the user. That's a genuine credit — the highest-value sort decision
is already correct by default.

But "efficient review" here can only mean efficient *reading*, not
efficient *deciding*, because there is no action. Until that changes, the
dashboard adds a step to the daily routine (one more place to check)
without removing any (CLI/Sheet are still required for the actual
decision), which is the opposite of the workflow improvement this screen
is meant to deliver.

---

## MVP Alignment

### What MVP requirements are already satisfied

(Against the Review Queue minimum-functionality bar in
`phase_5_mvp_acceptance_criteria.md`.)

- Sources strictly from the operational database, not the Sheet.
- Filters correctly to jobs awaiting review — nothing presented is hidden,
  nothing already moved past `presented` lingers.
- Shows enough to recognize a job at a glance: company, title, location,
  source, score, grade.
- Defaults to a decision-useful order (best matches first) with no extra
  user effort.
- The navigation shell is honest: unfinished screens are clearly labeled
  rather than appearing as broken or missing links.
- The startup redirect correctly treats Review Queue as the front door of
  daily use, matching its status as the highest-frequency workflow.

### What remains missing

- **Select/reject actions** — the single most important gap relative to
  the workflow's actual purpose. Without this, the screen cannot yet
  replace any part of the CLI/Sheet workflow for decision-making, only for
  reading.
- **Apply link** — absent from this screen entirely.
- **Stretch category and remote flag** — not currently shown, even though
  they're part of the expected at-a-glance triage set.
- **Score rationale / top reasons** — not required for this screen by the
  original MVP bar (that responsibility was assigned to Job Detail), but
  worth naming since it creates a capability gap versus the existing daily
  report.
- **A path to Job Detail** — a forward dependency on a screen that hasn't
  been built yet, not a flaw in this one, but it currently caps how far a
  user can go from here.

### What should be prioritized next

In order of workflow value:

1. **Make the screen actionable.** Closing the select/reject gap is the
   highest-leverage next step, because it is what turns this from a
   read-only mirror of the database into something that actually changes
   the daily workflow. The capability this depends on already exists
   elsewhere in the system, so this is a completeness gap for the screen
   to close, not a new capability to design from scratch.
2. **Surface the apply link and the two missing at-a-glance fields**
   (stretch category, remote flag) — smaller, immediate value, no new
   workflow concept introduced.
3. **Job Detail**, once scheduled, so Review Queue rows have somewhere to
   send a user who wants more than the table provides.

---

## Operational Risks

### Workflow bottlenecks

- The screen can be read but not acted on, so the daily routine still
  requires a second tool for the decision itself. Until select/reject
  ships, opening the dashboard is an additional step, not a replacement
  one.
- The missing apply link means even the simplest possible action — "go
  apply" — still requires leaving the dashboard to find the link
  somewhere else.

### Adoption risks

- First impressions carry extra weight for a single-user product with no
  peer pressure to push through a rough start. If the first thing the
  dashboard demonstrates is "you can look here, but you still have to act
  somewhere else," it risks getting filed as a secondary surface rather
  than becoming the daily habit.
- Seven of eight navigation items reading "not yet implemented" is honest,
  but on a first visit it can also read as "not ready" rather than "being
  built incrementally" — a framing/expectation risk rather than a defect
  in what's shipped.

### Usability concerns

- No visual emphasis distinguishes strong matches from marginal ones
  beyond the raw number in one column — the screen leaves all of the
  triage judgment to the reader instead of doing any of it visually.
- No indication of "how many jobs are waiting today" beyond the table's
  own length, which matters for someone deciding whether to review now or
  batch it later.
- Two genuine positives worth preserving as the screen grows: the
  empty-state message clearly distinguishes "nothing to review" from
  "something's broken," and a service failure degrades to a plain-language
  message instead of a raw error — both reduce the risk that an early bad
  day permanently damages trust in the dashboard.

### Information overload risk

None observed at this stage — if anything, the opposite. This package
errs toward minimalism, which is the right place to start from, but it
means the overload risk flagged for the eventual full MVP screen set
(`phase_5_mvp_acceptance_criteria.md`) has not yet had a chance to
materialize and should be watched for as fields are added, not assumed
solved.

---

## Synchronization Note for Project Master

- **Change:** UX/workflow assessment of Phase 5 Package 1 (navigation
  shell + Review Queue), no governance or architecture content.
- **Affected chats:** Software Development (Anna — for whichever package
  picks up select/reject next), Project Master (sequencing confirmation).
- **Required context update:** None to `PROJECT_STATE.md` — this is a UX
  assessment of already-shipped scope, not a status or roadmap claim.
- **Required action:** None required; this is advisory input for whatever
  package is sequenced next after Package 1.
- **Decision status:** Proposed — awaiting Project Master review.
- **Source document:** This document (`phase_5_package_1_ux_review.md`).
