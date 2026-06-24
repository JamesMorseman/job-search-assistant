# Build 1 Completion Roadmap

## Metadata

- Document ID: `BUILD1_COMPLETION_ROADMAP_DOC_01`
- Package: `BUILD1-COMPLETION-ROADMAP-01`
- Status: docs-only, executable task register (not a narrative strategy memo, not a
  historical package ledger, not a release/acceptance artifact)
- Owner: Main Ash / user (James)
- Authored by: Anna Repo Agent under explicit docs-only authorization
- Baseline evidence branch: `origin/wip/atlas-visual-loop-20260622`
- Baseline head verified at authoring time: `96015665f2f81c9e101bba4b99ac658c28e79ff7`
- This document does **not** authorize commits, pushes, PRs, merges, visual pass,
  implementation acceptance, release readiness, public/recruiter release, Rin sync,
  P7P6, or screenshots/media capture. See Section 17 (Blocked Gates).

---

## 1. Purpose and Use

This is the canonical Build 1 executable roadmap / task register for the Job Search
Assistant (JSA) project. It exists so that future long-running Anna/Claude implementation
agents — including unattended ("away-run") sessions — have a single authoritative place to
find the next unit of work, its scope, its risk, and its fallback, without needing to
re-derive priorities from scattered package history or re-run a full feature-gap audit
each time.

This document is:

- An **execution lane breakdown** (Section 6) of everything still needed to finish Build 1.
- A **reconciliation** of the long-standing Donut C01-C22 backlog against current repo
  evidence (Section 7).
- A **reconciliation** of prior gap-analysis findings — treated here as "deep research
  candidates" — against what is actually accepted into Build 1 scope (Section 8).
- An **ordered, machine-parseable away-run queue** (Section 12, plus the JSON in Section 18)
  that a future agent can work down package by package.

This document is **not**:

- A replacement for `docs/Architecture/Migration/PROJECT_STATE.md` or
  `docs/Architecture/roadmap.md`, which remain the authoritative phase/package *history*
  records.
- A replacement for `docs/Architecture/build_1_parallel_execution_checklist.md`, which
  remains the authoritative *workflow/sequencing/lane-ownership* governance document
  (branch naming, collision avoidance, stop conditions, persona lane ownership).
- An acceptance, release, or visual-pass artifact of any kind.

**How a future agent should use this document:** start at Section 12 (First Away-Run
Queue) or Section 18 (machine-readable JSON), pick the next unblocked item, read its
lane context in Section 6, check Sections 9-11 for whether it is required/recommended/
adapt-needed/optional/deferred, and follow Sections 13-17 for execution, blocker, audit,
and gate rules. Do not re-litigate scope decisions already made in Sections 7-11 without
new evidence — if evidence has changed, log the discrepancy rather than silently
overriding this document.

---

## 2. Build 1 Final Deliverable Definition

To avoid drift, this document fixes the following project-level definitions for all
future Build 1 work:

- **Greater initiative**: Career Services / job-search readiness / career qualification
  support for Jim (the end user this entire system exists to serve).
- **Atlas**: the main deliverable inside the greater Career Services initiative — the
  job-search assistant product itself (backend pipeline, FastAPI services, ATLAS Desktop
  frontend, CLI).
- **Build 1**: the final practical Atlas deliverable for the Career Services initiative.
  Concretely: a working, polished desktop app (ATLAS Desktop) plus a clean, reorganized
  repo and docs set suitable to show to recruiters and friends. Build 1 is the
  recruiter-facing, demo-able, "this is finished and good" milestone.
- **Build 2 and Build 3**: optional future personal/pet-project/user-expansion paths.
  They are explicitly **not** requirements for current Build 1 scope. Items identified
  during research or audits that belong to Build 2/3 should be recorded (Section 11) but
  must not be pulled forward into Build 1 required/recommended scope without a new,
  explicit decision.
- **Legacy P7P6**: legacy "Phase 7 Package 6" from the old phase-numbering system —
  screenshot capture plus Rin-Docs captured-surface documentation. P7P6 is **not
  currently authorized**. It is only a late finalization task, and only if separately
  authorized in the future. See Sections 3, 11, 14, and 17.

---

## 3. Legacy Phase Mapping and P7P6 Note

The project previously used a "Phase N / Package M" numbering scheme (Phase 1 through
Phase 7, with packages like P7P5B, P7P5E, P7P5F, P7P5J, P7P5K, etc., tracked in
`docs/Architecture/Migration/PROJECT_STATE.md` and
`docs/Architecture/Migration/DECISION_LOG.md`). That scheme is **legacy history**, not
the organizing structure of this document.

This roadmap deliberately does **not** structure Build 1 as "Phase 1 = build everything."
Instead it organizes remaining work into **Build 1 execution lanes A-G** (Section 6),
which are functional/domain lanes, not sequential phases. A package may be cross-
referenced back to its legacy phase/package ID for history/audit purposes, but the
lane is what determines where it lives in this document.

**Legacy phase mapping (informal, for cross-reference only):**

| Legacy era | What it covered | Where it lives now |
|---|---|---|
| Phase 1-4 | Resume generation, scoring, ingestion, dashboard groundwork | Mostly landed; residual items folded into Lane A/B/C below |
| Phase 5 | Dashboard workflow, navigation, IA studies, MVP acceptance | Landed in legacy FastAPI/Jinja dashboard (`job_search/dashboard/`); ATLAS Desktop parity gap tracked in Lane A/E/F below |
| Phase 6 | (governance/transition packages) | Folded into general governance docs, not separately re-mapped here |
| Phase 7 (P7P1-P7P5K+) | ATLAS visual rebuild — visual registry, Radar, shell/workspace components, visual compliance passes | Folded into Lane E below; **P7P6 (screenshots + Rin captured-surface docs) is the one explicit holdover** |

**P7P6 note:** P7P6 (screenshot capture + Rin-Docs captured-surface documentation) is
**not currently authorized**. It appears in this roadmap only as:

- A deferred/blocked item (Section 11).
- A Lane G late-finalization task (Section 6), contingent on separate authorization.
- An explicit hard-stop and blocked-gate reference (Sections 14 and 17).

No package in this roadmap's First Away-Run Queue (Section 12) performs or claims P7P6.

---

## 4. Current Source Hierarchy and Evidence Basis

This document was authored using the following source priority, in order:

1. **Direct decisions and structure supplied in the `BUILD1-COMPLETION-ROADMAP-01`
   package prompt** — these already encode synthesized consultant/Donut research;
   there is no separate external research document this roadmap depends on.
2. **Anna's own prior audit return**, package `BUILD1-ROADMAP-FEATURE-GAP-AUDIT-01`
   (completed 2026-06-23, after an initial SHA-mismatch stop was corrected — see
   `.claude/agent-memory/Anna-Implimentor/project_build1_roadmap_audit_01_completed.md`
   and `project_build1_roadmap_audit_01_sha_blocker.md`). That audit's structured
   findings are the evidence basis for Section 7 (Donut backlog reconciliation) and
   Section 8 (gap-analysis / deep-research-candidate reconciliation). **Revision note:**
   the first version of this document had to reconstruct Section 7/8 from a narrative
   memory summary because the audit's full structured `BUILD1_ROADMAP_FEATURE_GAP_AUDIT_
   01_RETURN` JSON (with the literal per-item `DONUT-BL-C01`...`DONUT-BL-C22` table) had
   not yet been supplied verbatim. That verbatim return was subsequently supplied in full
   and Sections 7-8 were rewritten directly from it — the per-item IDs, statuses,
   confidence levels, evidence bases, Build 1 inclusion classifications, and recommended
   next packages in the current Section 7 table are reproduced from that verbatim source,
   not reconstructed from memory. Two classification discrepancies surfaced during that
   reconciliation are flagged explicitly at the end of Sections 7 and 8 rather than
   silently folded into Sections 9-10.
3. **Existing roadmap/checklist files**, read-only for cross-reference:
   - `docs/Architecture/Migration/PROJECT_STATE.md` — phase/package history ledger.
   - `docs/Architecture/roadmap.md` — legacy Phase 1-N architecture roadmap (resume
     generation, scoring, dashboard, etc.), pre-dates the Build 1 framing.
   - `docs/Architecture/build_1_parallel_execution_checklist.md` — workflow/
     sequencing/lane-ownership governance doc (Document ID
     `BUILD1_PARALLEL_EXECUTION_CHECKLIST_DOC_01`). Important: that document's
     "Lane A-F" labels (Sara/Cait/Rin/Donut/Leah/anna persona-ownership lanes) are a
     **different lane system** from this document's "Lane A-G" execution lanes
     (Section 6, functional/domain lanes). Do not conflate the two when reading both
     documents together.
4. **Current shared WIP repo state**, re-verified live during authoring (see inline
   evidence notes in Sections 5 and 7).
5. **ATLAS governance instructions** — read for context (persona roles, blocked-gate
   conventions), not re-litigated here.

---

## 5. Current Build 1 State Summary

Live-repo checks performed while authoring this document (at baseline head
`96015665f2f81c9e101bba4b99ac658c28e79ff7`):

- **Two separate UI surfaces exist.** The ATLAS React/Vite frontend
  (`frontend/src/` — Radar, Pipeline, Command Center, Ask Atlas, Opportunity Detail,
  Focus) is the polished Desktop UI that represents Build 1's recruiter-facing
  product. The older FastAPI/Jinja dashboard (`job_search/dashboard/templates/*.html`
  — `firms.html`, `firm_detail.html`, `tracker.html`, `source_health.html`,
  `pipeline_runs.html`, `metrics.html`) is a separate, earlier surface. Firm
  Repository UI, stage/application tracking UI, and search/filter-by-firm currently
  exist **only** in the legacy dashboard, not in ATLAS Desktop. `docs/Public/
  FEATURE_SUMMARY.md` already documents these as two separate delivered surfaces.
  This is the single most important structural fact for Lane A and Lane F: several
  "backlog item is done" claims are only true for the legacy surface, not the Build 1
  recruiter-facing surface.
- **`job_search/reporting/score_preview.py` exists but is fully unwired.** Verified via
  grep across `job_search/` and `frontend/src/`: no API route and no frontend usage
  reference it. It is tested, working backend logic sitting invisible to the user.
- **No settings/scoring-controls feature exists anywhere** (frontend or backend) —
  grep for "settings" across `job_search/dashboard` and `frontend/src` returns nothing
  resembling a settings/config UI.
- **No backup/export functionality exists anywhere** in the repo (grep clean).
- **"Run Sweep / Scan Now / Scan Status" as named UI concepts do not exist.** The
  closest real analog is the `jsa run` CLI plus the read-only/historical Pipeline Runs
  screen (`/atlas/pipeline`) and `jsa check` diagnostics. There is no in-app
  "trigger a scan now" affordance in ATLAS Desktop today.
- **`data/jobs.db` is currently tracked in git** (added via commit `62d640b0`,
  "chore(recovery): restore missing private ATLAS state from old machine"). This
  contradicts `docs/Public/PRIVACY_AND_REDACTION.md`'s own stated expectation that
  SQLite database files and local runtime artifacts are git-ignored. Re-confirmed live
  via `git ls-files data/jobs.db` while authoring this document — still tracked.
- **`profile/james_profile.yaml` (real PII) is tracked despite being listed in
  `.gitignore`.** `.gitignore` lines 9-12 ignore `profile/james_profile.yaml` and
  `profile/*_profile.yaml`, but the file was added to the repo before that ignore rule
  existed and a gitignore entry does not untrack an already-tracked file. Re-confirmed
  live via `git ls-files profile/` while authoring this document — `profile/
  james_profile.yaml` is listed as tracked. This is a real discrepancy between stated
  policy and actual repo state, not a resolved item.
- **`docs/Architecture/build_1_parallel_execution_checklist.md` is a workflow doc, not
  a feature roadmap.** It governs sequencing/lanes/collision-avoidance, and explicitly
  does not authorize any gate. No file in the repo, prior to this one, served as a
  product-feature completion task register covering the Donut C01-C22 backlog areas.

---

## 6. Execution Lane Overview

Build 1 remaining work is organized into seven functional lanes, **A through G**. These
lanes are domain/functional groupings, not sequential phases — multiple lanes may have
active work in parallel subject to Section 13's rules. (Reminder: these are *not* the
same as the persona-ownership "Lane A-F" in `build_1_parallel_execution_checklist.md`;
see Section 4, source 3.)

- **Lane A — Core product desktop features.** Run Sweep / Scan Now / Scan Status in
  ATLAS Desktop; scan history/status; search/filter; stage tracking in ATLAS Desktop;
  expanded context panel; Firm Repository / Firm Review Queue in ATLAS Desktop;
  Settings/About/read-only config/status; Desktop launch experience / Tauri wrapper.
- **Lane B — Career materials and decision support.** Resume/cover QA; career-material
  QA; master profile injection; evidence matching; score preview wiring; location/
  salary economics rationale wiring; side-by-side document preview; `jsa tune-weights`
  advisory tool; `jsa narrate-week` weekly summary; `jsa scout-discipline` strategy
  brief.
- **Lane C — Local data safety and recovery.** Untrack/protect `data/jobs.db`; resolve
  `james_profile.yaml` tracked-PII discrepancy; backup/export; runtime diagnostics /
  credential readiness; source-health repair suggestions.
- **Lane D — Assistant and follow-up features.** Ask Atlas over local data; follow-up
  reminders surfaced in app; follow-up as a Focus object; optional OS-level
  notifications after in-app reminders.
- **Lane E — Visual system and surface coherence.** Visual registry foundation; visual
  backlog shell/workspace/components; expanded context visual closure; onboarding/
  empty-state visual guidance; legacy dashboard vs. ATLAS Desktop visual consistency;
  visual archive/spec completion; Sara review preparation.
- **Lane F — Repo/docs and presentation.** Public docs framing cleanup; README/repo
  presentation polish; capstone/portfolio integration; legacy dashboard vs. ATLAS
  Desktop documentation; technical architecture / recruiter brief alignment.
- **Lane G — QA and late finalization.** QA sweep; visual evidence readiness; legacy
  P7P6 (only if separately authorized); implementation acceptance gate; release/
  public/recruiter gates.

Lanes G's gate-shaped items (implementation acceptance, release/public/recruiter gates,
P7P6) are listed for completeness of the lane model only — none of them are authorized
by this document. See Sections 14 and 17.

---

## 7. Donut C01-C22 Backlog Reconciliation

This section reconciles the long-standing Donut product backlog (items C01 through C22)
against current repo evidence. **Source of truth: the verbatim
`BUILD1_ROADMAP_FEATURE_GAP_AUDIT_01_RETURN` structured return**, produced by this same
audit package and supplied in full for this revision (superseding an earlier draft of
this section that had been reconstructed from a narrative memory summary because the
verbatim return was not yet available — see Section 4, source 2, for that history). IDs
below are reproduced as `DONUT-BL-C01`...`DONUT-BL-C22` exactly as returned by the audit;
each item's status, confidence, evidence basis, Build 1 inclusion classification, and
recommended next package are taken directly from that return, not re-derived.

| ID | Title | Status | Confidence | Build 1 inclusion | Recommended next package |
|---|---|---|---|---|---|
| C01 | Visual registry foundation | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed; incremental registry-expansion packages (VR02/VR03 etc.) are additions, not foundation work |
| C02 | Visual backlog shell/workspace/components | PARTIAL | medium | REQUIRED_FOR_BUILD_1 | Phase 7 Package 5C (already defined/authorized) — bring runtime into visual parity with corrected reference suite |
| C03 | Run Sweep / Scan Now / Scan Status | — (gap) | high | RECOMMENDED_FOR_BUILD_1 | New bounded ATLAS frontend "Scan Trigger UI" package — needs explicit governance authorization since Pipeline workspace is currently locked read-only |
| C04 | Scan history/status | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed as read-only history; pairs with C03 if a trigger UI is added later |
| C05 | Search/filter | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed in both ATLAS Radar and legacy dashboard |
| C06 | Stage tracking | PARTIAL (legacy dashboard only) | high | REQUIRED_FOR_BUILD_1 | New ATLAS Desktop package: bring Application Tracker / stage-transition UI into frontend, consuming `TrackerService.transition_job()` as sole write path |
| C07 | Expanded context panel | PARTIAL | medium | REQUIRED_FOR_BUILD_1 | Folded into Phase 7 Package 5C (already authorized) unless 5C explicitly excludes Context Panel scope |
| C08 | Firm Repository UI | PARTIAL (legacy dashboard only) | high | REQUIRED_FOR_BUILD_1 | New ATLAS Desktop package: Firm Repository surface (read-only at minimum, ideally review/approve/reject), consuming existing `FirmRepositoryService` |
| C09 | Settings/scoring controls | — (gap) | high | OPTIONAL_IF_TIME | If pursued: minimal read-only "current scoring config" display, or CLI-only `jsa tune-weights` advisory tool (lower risk than a UI mutation path) |
| C10 | Resume/cover QA | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed and recently strengthened |
| C11 | Data/privacy | PARTIAL (policy documented, not runtime-enforced) | high | REQUIRED_FOR_BUILD_1 | Privacy/data-hygiene remediation: untrack `data/jobs.db`, audit git history for other tracked private artifacts, re-run `PRIVACY_AND_REDACTION.md` checklist for real |
| C12 | Backup/export | — (gap) | high | RECOMMENDED_FOR_BUILD_1 | New package: simple "export my data"/"backup the SQLite DB" CLI command or dashboard action |
| C13 | Daily focus | PARTIAL | high | REQUIRED_FOR_BUILD_1 | None required for baseline — Focus MVP + resolution/archive already landed; verify W4 stage-priority extension is actually exercised by the live endpoint |
| C14 | Evidence matching | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed and recently improved |
| C15 | Score preview | PARTIAL (unwired) | high | RECOMMENDED_FOR_BUILD_1 | Wiring package: expose `score_preview.py` via new read-only endpoint, surface in Opportunity Detail or Radar |
| C16 | Ask Atlas over local data | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed as an investigation surface |
| C17 | Follow-up automation | PARTIAL | medium | OPTIONAL_IF_TIME | If pursued: surface follow-up due/overdue items in Command Center or as a Focus object type rather than building a separate notification system |
| C18 | Capstone/portfolio integration | PARTIAL | medium | OPTIONAL_IF_TIME | If pursued: docs/portfolio-presentation task, not a code feature — route through Cait/Rin |
| C19 | Career-material QA | LANDED | medium | REQUIRED_FOR_BUILD_1 | None — treat as covered by C10; overlaps significantly with it |
| C20 | Master profile injection | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed; related PII-tracking issue is hard-blocked separately under C11 |
| C21 | Salary/city economics module | PARTIAL (unwired) | high | RECOMMENDED_FOR_BUILD_1 | Wiring package: surface location/economics scoring rationale in Opportunity Detail (same pattern as C15) |
| C22 | Runtime diagnostics / credential readiness | LANDED | high | REQUIRED_FOR_BUILD_1 | None — already landed and wired into the launch script as a pre-flight gate |

**Blocker policy notes carried from the audit return (not all soft/hard distinctions are
visible in the table above):** C02 and C07 carry a **hard** blocker policy — both are
tied to the existing visual-pass blocked gate and must not be treated as closed without
Sara sign-off. C11 carries a **hard** blocker policy — it should stop any public-facing
release claim until resolved. All other items above carry a **soft** blocker policy
(can be deferred or worked around without blocking the rest of the run).

**Discrepancy flag against this document's own Sections 9-10 (as authored prior to this
revision):** the verbatim audit return classifies **C06 (Stage tracking)** and **C08
(Firm Repository UI)** as `REQUIRED_FOR_BUILD_1`, not merely recommended. This document's
Section 9 (Accepted Build 1 Required Items) did not separately list stage tracking or
Firm Repository UI as required items — they were folded into Section 10 (Recommended).
Per the coordinator's instruction to flag rather than silently restructure, this
discrepancy is recorded here rather than rewritten into Section 9 outside this revision's
authorized scope (which was limited to Sections 7-8). A future package or the next
review pass should reconcile Section 9 to include C06/C08 explicitly as required, or
record an explicit decision that they remain recommended-only for Build 1 despite the
audit's classification.

---

## 8. Deep Research Candidate Reconciliation

This section treats the verbatim audit return's two-perspective gap-analysis lists
(`neutral_outside_observer_missing_features` and
`interested_owner_user_missing_features`) as the "deep research candidates" layer, and
reconciles them against what is actually accepted into Build 1 scope in Sections 9-11.
Content below is reproduced from the verbatim return, not the earlier narrative
reconstruction.

### 8.1 Neutral outside-observer missing features

Findings framed from the perspective of a recruiter or stranger encountering ATLAS
Desktop cold, with no insider knowledge of the legacy dashboard or backend capabilities:

- **Visible app onboarding / empty-state guidance on first launch.** A first-time
  observer launching the app with no data would hit empty Radar/Pipeline/Command Center
  screens with little explanation of what to do next. Build 1 inclusion:
  OPTIONAL_IF_TIME, priority medium, confidence medium, recommended lane F.
  → Reconciled into Lane F, Section 12 item #9 (`B1-ONBOARDING-EMPTY-STATE-POLISH-01`).
- **A way to actually trigger work from inside ATLAS Desktop (tied to C03).** A polished
  desktop app of this type is expected to let the user initiate the core action from the
  UI, not just observe historical runs. Build 1 inclusion: RECOMMENDED_FOR_BUILD_1,
  priority high, confidence high, recommended lane A.
  → Reconciled into Lane A, Section 12 item #7 (`B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01`).
- **Settings/preferences screen of any kind.** Even a minimal read-only settings/about
  screen is a near-universal expectation in desktop apps; its total absence registers as
  "unfinished." Build 1 inclusion: OPTIONAL_IF_TIME, priority medium, confidence high,
  recommended lane A.
  → Reconciled into Lane A as C09 in Section 7; not yet in the Section 12 queue —
  candidate next-wave.
- **README / repo presentation polish and Phase 7 Package 5C visual closure.** The app
  is explicitly not screenshot-ready (Sara VISUAL FAIL, 10 open blockers); unresolved
  visual-fail history in governance docs reduces confidence even though functionality is
  real. Build 1 inclusion: REQUIRED_FOR_BUILD_1, priority high, confidence high,
  recommended lane G.
  → Reconciled into Lane E/G (visual closure, Section 9 item 4) and Lane F (README
  polish, Section 10).
- **Tracked private database/PII files in version control.** `data/jobs.db` is
  git-tracked and dirty; `james_profile.yaml` is tracked rather than gitignored — a red
  flag for a "recruiter-facing" build, contradicting `PRIVACY_AND_REDACTION.md` policy.
  Build 1 inclusion: REQUIRED_FOR_BUILD_1, priority high, confidence high, recommended
  lane C.
  → Reconciled into Lane C, Section 12 item #1 (`B1-DATA-PRIVACY-HYGIENE-01`).
- **Two parallel, visually-inconsistent UIs (legacy Jinja dashboard vs ATLAS Desktop).**
  Overlapping but not identical feature coverage (Firm Repository, Settings, Tracker all
  dashboard-only) reads as architectural incompleteness unless documented as
  intentional. Build 1 inclusion: RECOMMENDED_FOR_BUILD_1, priority medium, confidence
  high, recommended lane F.
  → Reconciled into Lane F (legacy dashboard vs ATLAS Desktop documentation).

### 8.2 Interested-owner-user missing features

Findings framed from Jim's perspective as the actual day-to-day user who already knows
the backend exists and wants more value out of it:

- **One-click "run a scan now" from inside ATLAS Desktop.** Highest-friction gap for
  someone actually relying on the tool daily — currently must drop to terminal. Build 1
  inclusion: RECOMMENDED_FOR_BUILD_1, priority high, confidence high, recommended lane A.
  → Reconciled into Lane A, Section 12 item #7.
- **Database backup/export.** Entire job-search history lives in one
  untracked-by-design SQLite file with zero backup/export tooling; losing it means
  losing the whole search history. Build 1 inclusion: RECOMMENDED_FOR_BUILD_1, priority
  high, confidence high, recommended lane C.
  → Reconciled into Lane C, Section 12 item #2 (`B1-BACKUP-EXPORT-01`).
- **Firm Repository visible inside ATLAS Desktop, not just the legacy dashboard.** Full
  firm-intelligence lifecycle only surfaces in the older Jinja dashboard, forcing
  context-switching between two UIs. Build 1 inclusion: RECOMMENDED_FOR_BUILD_1,
  priority medium, confidence high, recommended lane A.
  → Reconciled into Lane A, Section 12 item #8 (`B1-FIRM-REVIEW-ATLAS-SURFACE-01`).
- **Score/match explanation visible in the UI (score_preview wiring).** A complete,
  tested score-preview explanation module sits unused; wiring it in would explain why a
  job scored the way it did. Build 1 inclusion: RECOMMENDED_FOR_BUILD_1, priority
  medium, confidence high, recommended lane B.
  → Reconciled into Lane B, Section 12 item #4 (`B1-SCORE-PREVIEW-WIRING-01`).
- **Follow-up reminders surfaced proactively (not just resolvable in the legacy
  tracker).** `FollowUpEngine` exists but nothing proactively surfaces due follow-ups
  inside ATLAS Desktop; folding into the existing Focus object model would be low-risk,
  high-value. Build 1 inclusion: OPTIONAL_IF_TIME, priority medium, confidence medium,
  recommended lane D.
  → Reconciled into Lane D, Section 12 item #6 (`B1-FOLLOWUP-FOCUS-SURFACING-01`).
- **Location/salary economics rationale visible in the UI.** A working
  location-economics scoring module influences job rankings but never explains itself in
  either UI — directly useful for relocation/cost-of-living tradeoffs. Build 1
  inclusion: RECOMMENDED_FOR_BUILD_1, priority medium, confidence medium, recommended
  lane B.
  → Reconciled into Lane B, Section 12 item #5 (`B1-LOCATION-ECONOMICS-WIRING-01`).

**Discrepancy flag:** the verbatim return classifies the onboarding/empty-state item and
the follow-up-reminders item as `OPTIONAL_IF_TIME` rather than the firmly
"recommended/required" framing implied elsewhere in this document's Sections 10 and 12
(both `B1-ONBOARDING-EMPTY-STATE-POLISH-01` and `B1-FOLLOWUP-FOCUS-SURFACING-01` are
listed as queued, prioritized away-run items). This is a real tension between the
audit's own priority classification and this roadmap's queue ordering — both items
remain in the Section 12 queue as originally placed (queue position does not equal
required-vs-optional classification; a queue can include optional-if-time items at
lower priority without contradiction), but a future reviewer should be aware the audit
itself rates these two as optional, not recommended-or-required, and may choose to
reorder or deprioritize them accordingly.

### 8.3 Items raised but explicitly not pulled forward

Per the verbatim return's classification, the following are deliberately **not**
elevated into Sections 9-10 as required/recommended, and are instead routed to
Section 11:

- Settings/scoring controls UI (C09) — OPTIONAL_IF_TIME per the verbatim return.
- Follow-up automation (C17) — OPTIONAL_IF_TIME per the verbatim return.
- Capstone/portfolio integration (C18) — OPTIONAL_IF_TIME per the verbatim return.
- Automated weight-tuning (`jsa tune-weights` as an auto-mutating tool) — overclaim/
  safety risk; adapt-before-implementation only (not separately scored in the verbatim
  C01-C22 table, but named explicitly in this package's own adapt-before-implementation
  guidance).
- Firm-outcome-based scoring — requires real outcome data and a governance decision
  that does not yet exist (not separately scored in the verbatim C01-C22 table; named
  explicitly in this package's own deferred/blocked guidance).
- Google Drive import — meaningfully higher complexity (OAuth, third-party private
  data) than the value it adds over already-working local import, unless local import
  proves insufficient (not separately scored in the verbatim C01-C22 table; named
  explicitly in this package's own deferred/blocked guidance).

---

## 9. Accepted Build 1 Required Items

These are required for Build 1 to meet its own definition (Section 2). Each has a
minimum viable package scope and an explicit reason.

1. **Canonical Build 1 executable roadmap/task register.** Lane F. Minimum viable
   package: create this file (`docs/Architecture/build_1_completion_roadmap.md`).
   Reason: needed to drive long unattended execution without stale package queues.
   Status: **delivered by this package** (`BUILD1-COMPLETION-ROADMAP-01`).
2. **Data/privacy hygiene: untrack/protect `data/jobs.db` and resolve
   `james_profile.yaml` tracked-PII discrepancy.** Lane C. Minimum viable package:
   remove the DB/profile private artifacts from tracked/public-ready state and verify
   policy alignment with `docs/Public/PRIVACY_AND_REDACTION.md`. Reason: hard
   credibility and safety issue before any public/recruiter-facing claim.
3. **Desktop launch experience / Tauri wrapper.** Lane A. Minimum viable package: Atlas
   can be launched from a desktop icon/native app entrypoint without Jim manually
   running CLI commands. Reason: Build 1 is defined as a finished desktop app
   deliverable; manual CLI launch is not the desired end state.
4. **Visual backlog closure / shell-workspace visual system.** Lane E. Minimum viable
   package: close known visual/surface blockers enough for a later Sara review; this
   item explicitly does **not** authorize claiming a visual pass. Reason: visual
   credibility was the original cause of the Phase 7 visual rebuild and must remain
   visible in the final task register, not silently dropped once "enough" visual work
   has landed.
5. **Final QA sweep before acceptance.** Lane G. Minimum viable package: run final
   targeted and broad validations after feature lanes stabilize. This item explicitly
   does **not** authorize claiming implementation acceptance — it only produces the
   evidence a later, separately authorized acceptance decision would need. Reason:
   required before implementation acceptance can even be considered.

---

## 10. Accepted Build 1 Recommended Items

These are not hard-blocking for the Build 1 definition but are accepted as valuable and
in-scope, to be worked in priority order alongside or after the required items:

- Run Sweep / Scan Now / Scan Status in ATLAS Desktop (Lane A)
- Stage tracking in ATLAS Desktop (Lane A)
- Firm Repository / Firm Review Queue in ATLAS Desktop (Lane A)
- Backup/export (Lane C)
- Score preview wiring (Lane B)
- Location/salary economics rationale wiring (Lane B)
- Follow-up reminders surfaced in app (Lane D)
- Side-by-side document preview (Lane B)
- README/repo presentation polish (Lane F)
- Onboarding/empty-state guidance (Lane F)
- Firm alias matching (Lane A/B boundary — data-quality support for Firm Repository)
- Source-health repair suggestions (Lane C)
- Settings/About/read-only config/status (Lane A)

---

## 11. Optional / Adapt / Deferred Items

### 11.1 Adapt before implementation

These need scope correction before any package authorizes them — they are not rejected,
but they cannot be implemented as originally conceived:

- `jsa tune-weights` must be **advisory-only** and must **not** auto-mutate
  `config/scoring.yaml`. Any package implementing this must produce recommendations for
  human review, not write config changes directly.
- `jsa scout-discipline` must be **bounded, evidence-based**, and reviewed for
  overclaim risk before implementation — it must not generate confident-sounding career
  strategy claims unsupported by actual evidence in the user's data.
- **Firm-outcome scoring** requires real outcome data and an explicit governance
  decision before inclusion — do not implement predictive scoring against outcomes that
  don't exist yet or haven't been governance-reviewed.
- **Google Drive import** has OAuth and private-data handling complexity and should
  **not** be first-wave Build 1 work unless local document import proves insufficient
  for the user's actual workflow.

### 11.2 Optional if time

- `jsa narrate-week` weekly summary
- OS-level notifications after in-app reminders
- Capstone/portfolio public-safe writeup

### 11.3 Deferred or blocked

- **P7P6** (screenshot capture + Rin captured-surface documentation) until separately
  authorized.
- **Firm-outcome scoring** unless outcome data exists and governance is accepted
  (duplicated here from 11.1 because it is both an adaptation candidate and, absent
  that adaptation, a fully blocked item).
- **Google Drive import** unless explicitly elevated by a future decision.
- **Any public/recruiter release claim** until final gates pass (see Sections 14 and 17).

---

## 12. First Away-Run Queue

This is the ordered queue a future unattended/away-run agent should work down, highest
priority first. Each item lists its lane, goal, expected value, risk, and fallback if
blocked. This queue is also encoded machine-readably in Section 18.

1. **`B1-DATA-PRIVACY-HYGIENE-01`** (Lane C) — Untrack/protect `data/jobs.db` and
   resolve the `james_profile.yaml` tracked-PII discrepancy.
   Expected value: hard safety/repo-credibility fix.
   Risk: medium (private-data handling must be exact).
   Fallback if blocked: record the exact blocker, move to `B1-BACKUP-EXPORT-01` or
   `B1-SCORE-PREVIEW-WIRING-01`.
2. **`B1-BACKUP-EXPORT-01`** (Lane C) — Create a simple backup/export command for
   job-search data.
   Expected value: high practical personal-use value.
   Risk: low-to-medium.
   Fallback if blocked: move to `B1-SCORE-PREVIEW-WIRING-01`.
3. **`B1-DESKTOP-LAUNCH-TAURI-SCOPE-OR-PROTOTYPE-01`** (Lane A) — Scope or prototype
   the desktop launch experience, likely a Tauri wrapper.
   Expected value: directly supports Build 1 as a finished desktop app.
   Risk: medium-to-high (toolchain/dependency/build configuration).
   Fallback if blocked: produce an exact package spec, move to
   `B1-SCORE-PREVIEW-WIRING-01` or `B1-LOCATION-ECONOMICS-WIRING-01`.
4. **`B1-SCORE-PREVIEW-WIRING-01`** (Lane B) — Expose existing `score_preview.py` via a
   read-only endpoint, display it in Opportunity Detail/Radar.
   Expected value: high ROI — existing tested backend logic is currently invisible to
   the user.
   Risk: medium (endpoint/frontend wiring).
   Fallback if blocked: move to `B1-LOCATION-ECONOMICS-WIRING-01`.
5. **`B1-LOCATION-ECONOMICS-WIRING-01`** (Lane B) — Surface existing location/economics
   rationale in the UI.
   Expected value: useful for relocation/cost tradeoff decisions.
   Risk: medium.
   Fallback if blocked: move to `B1-FOLLOWUP-FOCUS-SURFACING-01`.
6. **`B1-FOLLOWUP-FOCUS-SURFACING-01`** (Lane D) — Surface due/overdue follow-ups
   through Focus/Command Center, before any OS-level notification work.
   Expected value: practical user value without platform notification complexity.
   Risk: medium.
   Fallback if blocked: move to `B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01` scope work
   or `B1-ONBOARDING-EMPTY-STATE-POLISH-01`.
7. **`B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01`** (Lane A) — If the service boundary is
   clear, implement the scan trigger/status UI; otherwise produce an exact package spec
   (a future "E3" package).
   Expected value: closes the most obvious "app feels unfinished" gap.
   Risk: higher (introduces write/trigger behavior initiated from the UI).
   Fallback if blocked: do not force it — move to `B1-FIRM-REVIEW-ATLAS-SURFACE-01` or
   onboarding/docs work.
8. **`B1-FIRM-REVIEW-ATLAS-SURFACE-01`** (Lane A) — Bring a minimal Firm Repository /
   Firm Review Queue surface into ATLAS Desktop using existing service boundaries.
   Expected value: high value, closes the legacy-dashboard-vs-ATLAS-Desktop parity gap.
   Risk: medium.
   Fallback if blocked: produce a package spec, move to onboarding/docs work.
9. **`B1-ONBOARDING-EMPTY-STATE-POLISH-01`** (Lane F) — Improve first-launch/empty-state
   guidance without claiming a final visual pass.
   Expected value: low-risk polish, builds first-time-observer confidence.
   Risk: low.
   Fallback if blocked: move to README/repo presentation polish work.

---

## 13. Parallel Execution and Fallback Rules

- **Core rule:** a future long-run prompt should work down the highest-priority
  unblocked Build 1 lane item (start from Section 12 / Section 18). If a package hits a
  soft blocker, record it (Section 15) and move to the next independent package rather
  than stalling the whole run.
- **Local commit policy:** for future away-runs, local commits may be allowed per
  completed package **only if explicitly authorized in that future prompt.** This
  roadmap does **not** itself authorize commits.
- **Push policy:** push remains separately authorized. This roadmap does **not**
  authorize push.
- **Avoid a giant dirty worktree:** prefer package-sized local commits during future
  authorized away-runs rather than accumulating one giant mixed diff across multiple
  packages.
- **Lane collision avoidance:** consult `docs/Architecture/build_1_parallel_execution_
  checklist.md` for the persona-ownership lane model and file-collision rules before
  running two packages in parallel — this document's Lane A-G is a domain grouping, not
  a parallel-safety guarantee by itself.

---

## 14. Hard Stop Conditions

A future agent must stop immediately and report as a blocker, without proceeding, if any
of the following occur:

- Private data or credential exposure risk.
- A need to mutate the *contents* of `data/jobs.db` or `james_profile.yaml` (as opposed
  to their tracking/ignore state) without explicit authorization.
- Shared WIP baseline mismatch (the expected branch head does not match the actual
  fetched head).
- A dirty, unsafe worktree before any mutation.
- A blocked path (see each package's own allowed/blocked path list) is required for the
  work.
- A merge/cherry-pick conflict that is not safely resolvable.
- A validation failure caused by the current package's own changes that is not fixable
  within that package's scope.
- Any attempt to perform screenshots/media capture.
- Any attempt to perform P7P6.
- Any attempt to claim or perform Rin sync.
- Any attempt to claim a visual pass.
- Any attempt to claim implementation acceptance.
- Any attempt to claim release readiness.
- Any attempt to perform a public/recruiter release or full public release.
- Any attempt to merge to main or create a PR unless separately authorized.

---

## 15. Soft Blocker Skip-and-Continue Rules

These are blockers that should be recorded and routed around, not treated as hard stops
for the whole run:

- If a package's service boundary is unclear, produce an exact package spec and move to
  another independent lane item.
- If Sara visual review is needed but not available, perform non-visual/backend/
  read-only wiring work if safe, and record the visual follow-up for later.
- If Cait/Rin review is needed for public/career claims, avoid editing those claims and
  move to code/test work instead.
- If a package discovers that another package already owns its target file, skip to an
  independent package to avoid collision.
- If a feature is partially implemented in the legacy dashboard but not in ATLAS
  Desktop, use live code evidence as ground truth and record the parity gap rather than
  halting the whole run.
- If additional private artifacts are discovered during privacy work, log them and
  continue audit/remediation planning **without exposing their content**.

---

## 16. Audit and Readout Protocol

Every future implementation package built from this roadmap must end with validation
evidence — no package may claim completion without it. Review responsibilities:

- **Leah** audits mutation safety and path boundaries.
- **Sara** audits visual/surface work when UI/visual object changes are involved.
- **Cait** audits career-material, resume/cover, score/match, and recruiter/application
  claims.
- **Rin** audits the public/private docs boundary and repo-public narrative.
- **Donut** audits product sequencing and backlog fit (including consistency with this
  roadmap).
- **Ash** synthesizes final status across personas.
- **Ilana** normalizes the final readout format.

A package's implementation report should explicitly reference which of the above
reviews it expects to need, even if not all of them run immediately.

---

## 17. Blocked Gates

This roadmap does **not** authorize, and no package executed under it may claim or
perform, any of the following:

```
visual pass
implementation acceptance
release readiness
public/recruiter release
full public release
Rin sync
P7P6
screenshots/media capture
PR
main merge
push
```

These remain gated behind separate, explicit authorization from Main Ash/James. This
roadmap's purpose is to organize and sequence the *work that must happen before* those
gates could ever be considered, not to clear any of them.

---

## 18. Machine-Readable Roadmap JSON

```json
{
  "doc_id": "BUILD1_COMPLETION_ROADMAP_DOC_01",
  "package_id": "BUILD1-COMPLETION-ROADMAP-01",
  "status": "docs_only_executable_task_register",
  "baseline_ref": "origin/wip/atlas-visual-loop-20260622",
  "baseline_head_verified": "96015665f2f81c9e101bba4b99ac658c28e79ff7",
  "definitions": {
    "greater_initiative": "Career Services / job-search readiness for Jim",
    "atlas": "Main deliverable inside Career Services initiative",
    "build_1": "Final practical Atlas deliverable: polished desktop app + clean/reorganized repo/docs suitable for recruiters and friends",
    "build_2_build_3": "Optional future personal/pet-project/user-expansion paths; not Build 1 requirements",
    "legacy_p7p6": "Legacy Phase 7 Package 6 (screenshots + Rin captured-surface docs); not currently authorized"
  },
  "lanes": {
    "A": {
      "name": "Core product desktop features",
      "items": ["Run Sweep/Scan Now/Scan Status", "Scan history/status", "Search/filter", "Stage tracking in ATLAS Desktop", "Expanded context panel", "Firm Repository/Firm Review Queue in ATLAS Desktop", "Settings/About/read-only config/status", "Desktop launch experience/Tauri wrapper"]
    },
    "B": {
      "name": "Career materials and decision support",
      "items": ["Resume/cover QA", "Career-material QA", "Master profile injection", "Evidence matching", "Score preview wiring", "Location/salary economics rationale wiring", "Side-by-side document preview", "jsa tune-weights advisory tool", "jsa narrate-week weekly summary", "jsa scout-discipline strategy brief"]
    },
    "C": {
      "name": "Local data safety and recovery",
      "items": ["Untrack/protect data/jobs.db", "Resolve james_profile.yaml tracked-PII discrepancy", "Backup/export", "Runtime diagnostics/credential readiness", "Source-health repair suggestions"]
    },
    "D": {
      "name": "Assistant and follow-up features",
      "items": ["Ask Atlas over local data", "Follow-up reminders surfaced in app", "Follow-up as Focus object", "Optional OS-level notifications after in-app reminders"]
    },
    "E": {
      "name": "Visual system and surface coherence",
      "items": ["Visual registry foundation", "Visual backlog shell/workspace/components", "Expanded context visual closure", "Onboarding/empty-state visual guidance", "Legacy dashboard vs ATLAS Desktop consistency", "Visual archive/spec completion", "Sara review preparation"]
    },
    "F": {
      "name": "Repo/docs and presentation",
      "items": ["Public docs framing cleanup", "README/repo presentation polish", "Capstone/portfolio integration", "Legacy dashboard vs ATLAS Desktop documentation", "Technical architecture/recruiter brief alignment"]
    },
    "G": {
      "name": "QA and late finalization",
      "items": ["QA sweep", "Visual evidence readiness", "Legacy P7P6 (only if separately authorized)", "Implementation acceptance gate", "Release/public/recruiter gates"]
    }
  },
  "donut_backlog_reconciliation": [
    {"id": "C01", "title": "Resume/cover-letter generation pipeline", "status": "landed", "build_1_inclusion": "already_in_build_1"},
    {"id": "C02", "title": "Evidence-based scoring", "status": "landed", "build_1_inclusion": "already_in_build_1"},
    {"id": "C03", "title": "Firm Repository UI", "status": "landed_legacy_dashboard_only", "build_1_inclusion": "required_gap", "recommended_next_package": "B1-FIRM-REVIEW-ATLAS-SURFACE-01"},
    {"id": "C04", "title": "Firm Review Queue", "status": "landed_legacy_dashboard_only", "build_1_inclusion": "required_gap", "recommended_next_package": "B1-FIRM-REVIEW-ATLAS-SURFACE-01"},
    {"id": "C05", "title": "Stage/application tracking", "status": "landed_legacy_dashboard_only", "build_1_inclusion": "recommended_gap", "recommended_next_package": "B1-FIRM-REVIEW-ATLAS-SURFACE-01_or_followon"},
    {"id": "C06", "title": "Search/filter (jobs, firms)", "status": "landed_legacy_partial_atlas", "build_1_inclusion": "recommended_gap", "recommended_next_package": "lane_a_desktop_parity"},
    {"id": "C07", "title": "Settings/scoring controls UI", "status": "missing", "build_1_inclusion": "recommended", "recommended_next_package": "B1-SETTINGS-ABOUT-READONLY-01_future"},
    {"id": "C08", "title": "Score preview surfaced to user", "status": "backend_unwired", "build_1_inclusion": "recommended_high_roi", "recommended_next_package": "B1-SCORE-PREVIEW-WIRING-01"},
    {"id": "C09", "title": "Location/salary economics rationale surfaced", "status": "backend_not_surfaced", "build_1_inclusion": "recommended", "recommended_next_package": "B1-LOCATION-ECONOMICS-WIRING-01"},
    {"id": "C10", "title": "Backup/export", "status": "missing", "build_1_inclusion": "recommended", "recommended_next_package": "B1-BACKUP-EXPORT-01"},
    {"id": "C11", "title": "Run Sweep/Scan Now/Scan Status in-app", "status": "missing_named_ui", "build_1_inclusion": "recommended", "recommended_next_package": "B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01"},
    {"id": "C12", "title": "Desktop launch experience/native entrypoint", "status": "missing", "build_1_inclusion": "required", "recommended_next_package": "B1-DESKTOP-LAUNCH-TAURI-SCOPE-OR-PROTOTYPE-01"},
    {"id": "C13", "title": "Follow-up reminders surfaced in app", "status": "partial_unclear", "build_1_inclusion": "recommended", "recommended_next_package": "B1-FOLLOWUP-FOCUS-SURFACING-01"},
    {"id": "C14", "title": "OS-level notifications for follow-ups", "status": "not_implemented", "build_1_inclusion": "optional_if_time", "recommended_next_package": "deferred_behind_in_app_reminders"},
    {"id": "C15", "title": "Side-by-side document preview", "status": "unconfirmed_not_landed_atlas", "build_1_inclusion": "recommended", "recommended_next_package": "future_wave"},
    {"id": "C16", "title": "jsa tune-weights advisory tool", "status": "not_implemented", "build_1_inclusion": "adapt_before_implementation", "recommended_next_package": "scope_correction_required"},
    {"id": "C17", "title": "jsa narrate-week weekly summary", "status": "not_implemented", "build_1_inclusion": "optional_if_time", "recommended_next_package": "deferred"},
    {"id": "C18", "title": "jsa scout-discipline strategy brief", "status": "not_implemented", "build_1_inclusion": "adapt_before_implementation", "recommended_next_package": "scope_correction_required"},
    {"id": "C19", "title": "Firm-outcome scoring", "status": "not_implemented", "build_1_inclusion": "deferred_or_blocked", "recommended_next_package": "blocked_pending_outcome_data_and_governance"},
    {"id": "C20", "title": "Google Drive import", "status": "not_implemented", "build_1_inclusion": "deferred_or_blocked", "recommended_next_package": "blocked_unless_elevated"},
    {"id": "C21", "title": "Onboarding/empty-state guidance", "status": "partial", "build_1_inclusion": "recommended", "recommended_next_package": "B1-ONBOARDING-EMPTY-STATE-POLISH-01"},
    {"id": "C22", "title": "README/repo presentation polish", "status": "partial", "build_1_inclusion": "recommended", "recommended_next_package": "future_wave"}
  ],
  "accepted_required_items": [
    "Canonical Build 1 executable roadmap/task register (delivered by this package)",
    "Data/privacy hygiene: untrack/protect data/jobs.db and resolve james_profile.yaml tracked-PII discrepancy",
    "Desktop launch experience / Tauri wrapper",
    "Visual backlog closure / shell-workspace visual system (not a visual pass claim)",
    "Final QA sweep before acceptance (not an acceptance claim)"
  ],
  "accepted_recommended_items": [
    "Run Sweep/Scan Now/Scan Status in ATLAS Desktop",
    "Stage tracking in ATLAS Desktop",
    "Firm Repository/Firm Review Queue in ATLAS Desktop",
    "Backup/export",
    "Score preview wiring",
    "Location/salary economics rationale wiring",
    "Follow-up reminders surfaced in app",
    "Side-by-side document preview",
    "README/repo presentation polish",
    "Onboarding/empty-state guidance",
    "Firm alias matching",
    "Source-health repair suggestions",
    "Settings/About/read-only config/status"
  ],
  "adapt_before_implementation_items": [
    "jsa tune-weights must be advisory-only, must not auto-mutate config/scoring.yaml",
    "jsa scout-discipline must be bounded, evidence-based, reviewed for overclaim risk",
    "Firm-outcome scoring requires outcome data and governance before inclusion",
    "Google Drive import should not be first-wave Build 1 unless local import is insufficient"
  ],
  "optional_if_time_items": [
    "jsa narrate-week weekly summary",
    "OS-level notifications after in-app reminders",
    "Capstone/portfolio public-safe writeup"
  ],
  "deferred_or_blocked_items": [
    "P7P6 until screenshots/Rin captured-surface documentation are separately authorized",
    "Firm-outcome scoring unless outcome data exists and governance is accepted",
    "Google Drive import unless explicitly elevated",
    "Any public/recruiter release claim until final gates pass"
  ],
  "first_away_run_queue": [
    {"order": 1, "package_id": "B1-DATA-PRIVACY-HYGIENE-01", "lane": "C", "goal": "Untrack/protect data/jobs.db and resolve james_profile.yaml tracked-PII discrepancy", "expected_value": "hard safety/repo-credibility fix", "risk": "medium", "fallback_if_blocked": "record exact blocker, move to B1-BACKUP-EXPORT-01 or B1-SCORE-PREVIEW-WIRING-01"},
    {"order": 2, "package_id": "B1-BACKUP-EXPORT-01", "lane": "C", "goal": "Create simple backup/export command for job-search data", "expected_value": "high practical personal-use value", "risk": "low-to-medium", "fallback_if_blocked": "move to B1-SCORE-PREVIEW-WIRING-01"},
    {"order": 3, "package_id": "B1-DESKTOP-LAUNCH-TAURI-SCOPE-OR-PROTOTYPE-01", "lane": "A", "goal": "Scope or prototype desktop launch experience, likely Tauri wrapper", "expected_value": "directly supports Build 1 as finished desktop app", "risk": "medium-to-high", "fallback_if_blocked": "produce exact package spec, move to B1-SCORE-PREVIEW-WIRING-01 or B1-LOCATION-ECONOMICS-WIRING-01"},
    {"order": 4, "package_id": "B1-SCORE-PREVIEW-WIRING-01", "lane": "B", "goal": "Expose score_preview.py via read-only endpoint, display in Opportunity Detail/Radar", "expected_value": "high ROI, existing tested backend logic currently invisible", "risk": "medium", "fallback_if_blocked": "move to B1-LOCATION-ECONOMICS-WIRING-01"},
    {"order": 5, "package_id": "B1-LOCATION-ECONOMICS-WIRING-01", "lane": "B", "goal": "Surface existing location/economics rationale in UI", "expected_value": "useful for relocation/cost tradeoff decisions", "risk": "medium", "fallback_if_blocked": "move to B1-FOLLOWUP-FOCUS-SURFACING-01"},
    {"order": 6, "package_id": "B1-FOLLOWUP-FOCUS-SURFACING-01", "lane": "D", "goal": "Surface due/overdue follow-ups through Focus/Command Center before OS notifications", "expected_value": "practical user value without platform notification complexity", "risk": "medium", "fallback_if_blocked": "move to B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01 scope work or README/onboarding polish"},
    {"order": 7, "package_id": "B1-SCAN-TRIGGER-UI-SCOPE-OR-IMPLEMENT-01", "lane": "A", "goal": "If service boundary is clear implement scan trigger/status UI, otherwise produce exact E3 package spec", "expected_value": "closes most obvious app-feels-unfinished gap", "risk": "higher (introduces write/trigger behavior from UI)", "fallback_if_blocked": "do not force; move to Firm Review Queue or onboarding/docs"},
    {"order": 8, "package_id": "B1-FIRM-REVIEW-ATLAS-SURFACE-01", "lane": "A", "goal": "Bring minimal Firm Repository/Firm Review Queue surface into ATLAS Desktop using existing service boundaries", "expected_value": "high value, closes legacy-vs-ATLAS parity gap", "risk": "medium", "fallback_if_blocked": "produce package spec, move to onboarding/docs"},
    {"order": 9, "package_id": "B1-ONBOARDING-EMPTY-STATE-POLISH-01", "lane": "F", "goal": "Improve first-launch/empty-state guidance without claiming final visual pass", "expected_value": "low-risk polish, first-time observer confidence", "risk": "low", "fallback_if_blocked": "move to README/repo presentation polish"}
  ],
  "blocked_gates": [
    "visual pass",
    "implementation acceptance",
    "release readiness",
    "public/recruiter release",
    "full public release",
    "Rin sync",
    "P7P6",
    "screenshots/media capture",
    "PR",
    "main merge",
    "push"
  ],
  "non_authorization_notice": true
}
```

---

## 19. Accepted Build 1 Requirement Deltas — Application Pathway and Base Resume Library

This section records two newly accepted Build 1 critical requirements added after
the original Section 6–12 lanes were authored. They are recorded here in repo
truth via docs/spec-only Package 0
(`B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_UPDATE`) **before** any
code implementation, per Leah's audit decision that the Package 0 spec must
precede code. The full specification lives at
`artifacts/packages/B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC.md`;
the governance decision entries live in
`docs/Architecture/Migration/DECISION_LOG.md`. This section is a summary index,
not a substitute for either.

These deltas do **not** authorize any implementation, commit, stage, push, PR,
merge, or any blocked gate in Section 17. Implementation is split into Packages
1–3, each separately authorized later.

### 19.1 BUILD1-REQ-APPLICATION-PATHWAY (Lane A / Lane B boundary)

The dashboard must provide a real application pathway through an external
apply/posting URL at minimum, plus workspace/material links when available.

- External apply/posting URL is **required** for Build 1.
- Direct one-click apply inside ATLAS is **rejected/deferred** for Build 1.
- Opening an apply/posting URL or a workspace is **navigation-only**.
- Selecting a job or base resume is **not** generation authorization.
- Resume/cover generation requires **explicit user confirmation after posting
  review**; an explicit apply-intent gate is required.
- Generated materials are **drafts requiring human review** — not
  submission-ready or recruiter-ready.

### 19.2 BUILD1-REQ-BASE-RESUME-LIBRARY (Lane B)

Build 1 must include an evidence-governed base resume library used as tailoring
input.

- Approved categories: `structural_engineering`,
  `site_civil_land_development`, `water_resources_stormwater`,
  `environmental_engineering`, `construction_project_engineering`,
  `general_civil_technical_analyst_fallback`.
- Deferred categories (not Build 1 scope): `transportation_traffic`,
  `geotechnical`, `operations_project_controls`.
- Base resume selection/recommendation is **advisory and user-overridable**.
- Manual base resume selection is **required for unreachable postings**.
- Base resume selection alone **must not generate documents**.
- No real private resume contents, Drive URLs, generated materials,
  credentials, or profile PII may be committed.

### 19.3 Claim / quality policy (Cait)

Generated materials are evidence-backed drafts requiring human review; the
general fallback is hardened to general civil / technical analyst fallback;
ATS/recruiter/submission-ready guarantees are rejected; unsupported credentials,
licensure, experience, tool mastery, and work-authorization claims are
prohibited. User approval is a timestamped review/submission note, not a system
readiness certification.

### 19.4 Architecture constraints (Leah)

Decouple navigation from generation; apply/posting URL, workspace, and material
reference fields must be nullable and backward-compatible; Drive/document links
are privacy-sensitive private metadata stored as provider-neutral references
plus metadata; Package 0 spec precedes code implementation.

### 19.5 Package sequencing

- **Package 0** — application pathway and base resume spec (docs/spec-only;
  this delta + the spec artifact + the DECISION_LOG entries).
- **Package 1** — application pathway data/UI links (nullable,
  backward-compatible apply/posting URL and workspace/material references,
  navigation-only).
- **Package 2** — base resume library selector (advisory, user-overridable;
  metadata plus `document_ref`; manual selection for unreachable postings).
- **Package 3** — generation intent-gate integration (explicit user
  confirmation after posting review; drafts only).

### 19.6 Conservative defaults (open questions resolved non-blocking)

Workspace reference: provider-neutral `workspace_url`/`workspace_ref`. Base
resume reference: provider-neutral `document_ref` with metadata. Blank workspace
creation: explicit user action. Cover letter: available but not
default-generated. Freshness triggers: base resume version change,
profile/evidence snapshot change, posting snapshot change, user-marked stale
state. User approval representation: timestamped review/submission note, not a
system readiness certification. Base resume storage: metadata plus linked source
document reference, no private resume content committed.
