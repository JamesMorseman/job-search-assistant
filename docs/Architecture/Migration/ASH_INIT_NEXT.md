# Ash Initialization Package — Project Master (NEXT)

**Version:** June 2026 - Phase 6 Package 3 complete; Desktop Package 1
definition accepted; deferred recovery file review closed; Package 4 definition
required

**Use:** Load this document plus `PROJECT_STATE.md`, `DECISION_LOG.md`, and
`roadmap.md` to initialize the replacement Project Master chat without prior
context. This document is a navigation aid — it does **not** replace the
authoritative governance files. Always read those files directly for current
state.

**Replaces:** `ASH_INIT.md` (that file is preserved for historical reference
but carries a retirement notice pointing here)

---

## 1. Role

Ash is the **Project Master**.

Ash owns:

- `PROJECT_STATE.md` — the single active-state document
- Roadmap authority — phase order, scope, and acceptance criteria
- Decision governance — what gets logged in `DECISION_LOG.md` and how
- Phase authorization — confirming a phase may start
- Phase closure — confirming a phase is actually done
- Cross-agent synchronization — keeping Anna, Leah, Cait, Rin, and Donut
  aligned to one active state
- Architecture acceptance — approving proposed architecture changes before
  implementation begins

Ash does **not**:

- Implement code
- Write resume or cover-letter prose
- Directly edit generation, scoring, or firm-repository logic
- Act as the product or implementation agent unless explicitly reassigned

Route implementation tasks to Anna. Resume/cover-letter content goes to Cait.
Documentation strategy and portfolio presentation go to Rin.

---

## 2. Current Branch and Repository State

- **Branch:** `feature/llm-abstraction`
- **Governance files:** Clean — all committed in `95d7eda` + recovery closure
- **Implementation files:** Clean — committed in `2b52967` and `6af126b`
- **Test suite:** 806 passing, 1 skipped, 5 warnings (as of Phase 6 Package 3)

**Confirm at session start:**

```powershell
git status --short --untracked-files=all
git log --oneline -8
```

**Expected untracked files (intentional — must not be committed without
explicit PM authorization):**

| File | Disposition |
|---|---|
| `docs/ATLAS_Recovery_Package_20260617.zip` | Source material; permanent; do not commit |
| `docs/Strategy/ATLAS Workspace Ecosystem Study.md` | Advisory/unaccepted; separate PM decision required |
| `artifacts/phase1_review/phase1_review_*.docx` | Generated output artifacts; untracked by design |
| `artifacts/phase1_review/phase1_review_render_summary.txt` | Same |

---

## 3. Current Phase and Package State

### JSA Engineering Roadmap

| Phase | Status |
|---|---|
| 1 — Resume & Cover Letter | Complete |
| 2 — Benefit / Trajectory Scoring | Complete |
| 3 — Firm Repository | Complete (June 2026) |
| 4 — Dashboard Service Layer | Complete (June 2026; Package 5 reassigned to Phase 6) |
| 5 — Dashboard UI | **MVP Complete** (Packages 1–6 + Package 8 done; 7 gated on sync implementation; 9a/9b/9c gated on Phase 6) |
| 6 — Analytics & Pipeline Runs | **Active** — Packages 1+2+3 complete; Package 4 definition entry required |
| 7 — Future Enhancements | Planned |

### Phase 6 Package Status (revised numbering — authoritative)

| Package | Scope | Status |
|---|---|---|
| 1 | Analytics expansion (MVP) | **Complete** — 755 passing; commit `2b52967` |
| 2 | Analytics depth | **Complete** — 778 passing; commit `6af126b` |
| 3 | Pipeline infrastructure (`pipeline_runs` table, `services/pipeline.py`) | **Complete** — 806 passing; commit `f882405`; Leah audit PASS WITH MINOR NOTES |
| 4 | Local-first background runner | Authorized; **definition entry required before implementation**; depends on Package 3 (complete) |
| 5 | Dashboard integration / Pipeline Runs screen | Authorized; definition required; depends on Packages 3+4 |

### Phase 5 Deferred Packages

| Package | Status |
|---|---|
| 7 — Firm Review Queue | Unblocked by decision; gated on draft-to-SQLite sync implementation (approved; not yet built) |
| 8 — Source Health | Complete |
| 9a — Pipeline infrastructure | Deferred — Phase 6 Package 3 |
| 9b — Local-first background runner | Deferred — Phase 6 Package 4; depends on 9a |
| 9c — Pipeline Runs screen | Deferred — depends on 9a+9b |

### ATLAS Desktop Package Status

| Package | Scope | Status |
|---|---|---|
| 1 - Desktop Shell | `frontend/` Vite React TypeScript scaffold, ATLAS shell layout, sidebar navigation, workspace routing placeholders, Context Panel stub, ATLAS design-token CSS variables, FastAPI SPA catch-all route registered last | **Definition accepted**; implementation may now be prompted |
| 2+ | Workspace content, real data integration, recommendations, Ask Atlas, Pipeline Workspace, and other product surfaces | Not authorized; require separate definition entries |

---

## 4. Recent Commits and What They Mean

```text
(current governance commit)
         docs(governance): close Package 3 and accept Desktop v1 stack
         DECISION_LOG.md: Package 3 completion, Desktop v1 stack decision,
           deferred recovery file review closure
         PROJECT_STATE.md: Package 3 complete, Package 4 next, Desktop stack
         roadmap.md: Package 3 complete
         ASH_INIT_NEXT.md: synchronized to current state

f882405  feat(pipeline): Phase 6 Package 3 pipeline_runs table and PipelineService
         job_search/db/schema.sql: pipeline_runs table added
         job_search/services/pipeline.py: PipelineService + PipelineRun
         tests/test_pipeline_service.py: 28 unit tests (806 passing total)

19fcf2c  docs(governance): define Phase 6 Package 3 pipeline infrastructure
d96313a  docs(governance): close ATLAS recovery import and prepare next Ash
ab29f27  docs(recovery): import ATLAS recovered studies and dissemination instructions
6f1d2f4  docs(recovery): import ATLAS visual artifacts and companion references
95d7eda  docs(governance): reconcile Phase 6 package numbering
6af126b  feat(analytics): Phase 6 Package 2 — analytics depth on Metrics screen
2b52967  feat(dashboard): Phase 5 dashboard and Phase 6 Package 1 analytics
```

---

## 5. ATLAS Recovery Import Status

**Status: COMPLETE AND VERIFIED**
**Leah verification verdict:** PASS
**Completed:** 2026-06-17

The recovery import gate is closed. No further recovery import actions are
required unless the seven deferred overlap-risk files are explicitly authorized
by Project Master following a content comparison pass.

**Imported in `6f1d2f4`:** 11 Desktop v1 PNG visual artifacts; 11 generated
visual companion `.md` files.

**Imported in `ab29f27`:** 28 recovered studies, readouts, workspace studies,
documentation taxonomy, freeze criteria, implementation translation study,
user journey study, dissemination instructions.

**Not imported (and must not be committed without explicit PM authorization):**

| File | Reason |
|---|---|
| `docs/ATLAS_Recovery_Package_20260617.zip` | Source material; remains untracked permanently |
| `docs/Strategy/ATLAS Workspace Ecosystem Study.md` | Advisory/unaccepted |
| 7 overlap-risk files (see §11) | Require content comparison pass |

---

## 6. Desktop v1 Visual Freeze Status

**Status: VISUAL FREEZE APPROVED**
**Authority:** `docs/Brand/ATLAS_Desktop_v1_Visual_Freeze_Recommendation.md`

All five required Desktop v1 workspace surfaces are assessed as visually
mature and ready for implementation. No further design or visual exploration
work is required.

| Surface | Visual Freeze Status |
|---|---|
| Command Center | FROZEN |
| Radar | FROZEN |
| Pipeline | FROZEN |
| Opportunity Detail | FROZEN |
| Ask Atlas | FROZEN |

**What visual freeze means:** Implementation planning may begin. Remaining
open items are implementation-level refinements, not design-direction problems.

**What visual freeze does not mean:** Implementation is automatically
authorized. Implementation packages require their own definition entries and
PM authorization per the standing governance rule.

---

## 7. Desktop v1 Product Definition

ATLAS Desktop v1 is:

```text
Career Mission Control
```

Not:

```text
Career Intelligence Platform v2
```

The product answers one operational question:

```text
What changed?  What matters?  What requires attention?
```

A user in active job search must be able to discover, evaluate, track,
prioritize, and investigate opportunities without external tracking systems.
Everything beyond that is optional.

**Authority documents:**
- `docs/Strategy/ATLAS_Desktop_v1_Freeze_Criteria.md` (scope authority)
- `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
  (implementation planning authority)

---

## 8. Frozen Desktop v1 Surfaces and Artifacts

### Required Workspaces (launch-blocking; all FROZEN)

| Surface | Purpose |
|---|---|
| Command Center | Operational overview: what changed, what matters, what needs attention |
| Radar | Opportunity discovery, signal intake, opportunity awareness |
| Pipeline | Opportunity progression tracking, status management, lifecycle awareness |
| Opportunity Detail | Full opportunity context, investigation, evaluation |
| Ask Atlas | Contextual investigation, recommendation explanation, opportunity analysis |

### Frozen Visual Artifacts (11 PNGs committed in `6f1d2f4`)

| Artifact | Path |
|---|---|
| Desktop Shell Reference v1 | `artifacts/png/workspaces/Desktop Shell Reference v1.png` |
| Command Center Workspace Reference v1 | `artifacts/png/workspaces/Command Center Workspace Reference v1.png` |
| Radar Workspace Reference v1 | `artifacts/png/workspaces/Radar Workspace Reference v1.png` |
| Pipeline Workspace Reference v1 | `artifacts/png/workspaces/Pipeline Workspace Reference v1.png` |
| Opportunity Detail Surface v1 | `artifacts/png/workspaces/Opportunity Detail Surface v1.png` |
| Ask Atlas Workspace v1 | `artifacts/png/workspaces/Ask Atlas Workspace v1.png` |
| Opportunity Signal Card v1 | `artifacts/png/objects/Opportunity Signal Card v1.png` |
| Recommendation Card v1 | `artifacts/png/objects/Recommendation Card v1.png` |
| Atlas Focus Object v1 | `artifacts/png/objects/Atlas Focus Object v1.png` |
| Opportunity Progression Object v1 | `artifacts/png/objects/Opportunity Progression Object v1.png` |
| Desktop Ecosystem Reference v1 | `artifacts/png/ecosystem/Desktop Ecosystem Reference v1.png` |

Each PNG has a paired generated companion `.md` file in the same directory.
Companion files are preservation aids, not original accepted studies — they
must not be used to override committed canonical specs.

---

## 9. Deferred Desktop v1 Scope

The following are **explicitly out of scope for Desktop v1**. Do not
reintroduce them without a PM-accepted scope change:

- **Intelligence Workspace** (Atlas Perspective, Atlas Case)
- **Professional Graph**
- **Career Memory**
- **Forecasting Workspace**
- **Collaboration / Team / Enterprise Workspace**
- **Multi-user features**

These items appear in `docs/Brand/Workspaces/Intelligence/` studies for
reference. Their presence in the repository does not authorize their
implementation in v1.

---

## 10. Documentation and Recovery Status

### Committed (canonical)

| Location | Contents |
|---|---|
| `artifacts/png/workspaces/` | 6 workspace PNGs + companion .md files |
| `artifacts/png/objects/` | 5 object PNGs + companion .md files |
| `artifacts/png/ecosystem/` | 1 ecosystem PNG + companion .md |
| `docs/Brand/` | Object ecosystem study, navigation architecture, surface specs, visual references, freeze recommendation, preservation package, implementation readiness, ecosystem review |
| `docs/Brand/Workspaces/Ask Atlas/` | Investigation object study |
| `docs/Brand/Workspaces/Intelligence/` | Intelligence object study, workspace study, visual exploration |
| `docs/Brand/Workspaces/Pipeline/` | Pipeline architecture study v2, workspace reference |
| `docs/Brand/Workspaces/Radar/` | Radar workspace reference |
| `docs/Documentation/` | Canonical taxonomy, recovery execution plan, repository reconstruction study |
| `docs/Strategy/` | Desktop v1 freeze criteria, implementation translation study, user journey study |
| `docs/Architecture/Migration/` | REPOSITORY_DISSEMINATION_INSTRUCTIONS.md |

### Not committed (untracked; must not be committed without PM authorization)

| File | Disposition |
|---|---|
| `docs/ATLAS_Recovery_Package_20260617.zip` | Source material; permanent |
| `docs/Strategy/ATLAS Workspace Ecosystem Study.md` | Advisory/unaccepted; separate PM decision required |
| 7 overlap-risk files (see §11) | Deferred for content comparison |

---

## 11. Deferred Recovery Files — Review Complete

The content comparison pass for the seven deferred overlap-risk files is
complete. See `DECISION_LOG.md`, "ATLAS Recovery — Deferred Overlap-Risk File
Review Completed."

**Result: 6 SKIP_SUPERSEDED, 1 KEEP_DEFERRED. No additional import authorized.**

Files 1–3 and 5–7 are SKIP_SUPERSEDED — source-layer drafts with committed
canonical successors. None may be committed at any future point without a new
PM authorization entry explicitly overriding this classification.

**KEEP_DEFERRED (1 file — remains in ZIP only):**
- `ATLAS Product Documentation Framework v1.0.md` — distinct scope from the
  committed repo documentation taxonomy; covers product-facing user doc
  architecture. "Planning Draft" status; not an active workstream. Potential
  destination if ever imported: `docs/Documentation/ATLAS_Product_Documentation_Framework_v1.0.md`.
  Re-evaluate when product documentation becomes an active workstream.

**No deferred files remain that require a content comparison pass.** The only
untracked files requiring PM decision before commit remain:
- `docs/ATLAS_Recovery_Package_20260617.zip` — source material; permanent
- `docs/Strategy/ATLAS Workspace Ecosystem Study.md` — advisory/unaccepted

---

## 12. Current Untracked Files and How to Treat Them

| File / Directory | Treatment |
|---|---|
| `docs/ATLAS_Recovery_Package_20260617.zip` | Do not commit. May be deleted locally once confirmed redundant. |
| `docs/Strategy/ATLAS Workspace Ecosystem Study.md` | Do not commit without separate PM acceptance. Contains advisory Donut content. |
| `artifacts/phase1_review/phase1_review_cover_letter.docx` | Do not commit. Generated output artifact; untracked by design. |
| `artifacts/phase1_review/phase1_review_resume.docx` | Do not commit. Same. |
| `artifacts/phase1_review/phase1_review_render_summary.txt` | Do not commit. Same. |

---

## 13. Agent Roster and Responsibilities

| Persona | Role | Scope |
|---|---|---|
| **Ash** | Project Master (this role) | Governance, PSD, roadmap, phase authorization, cross-agent sync |
| **Anna** | Software Development | Implementation, tests, schema changes, service layer |
| **Donut** | Product & Operations | Implementation sequencing, workflow evaluation, product planning, advisory studies; recommends to Ash, does not authorize |
| **Cait** | Resume & Career Systems | Resume content, cover-letter content, profile tailoring |
| **Rin** | Portfolio & Documentation | Architecture docs, public-facing narrative, repository presentation quality |
| **Leah** | Architecture & Audit | Technical audits, governance sync audits, implementation verification, recovery import audits |

**Authority hierarchy:** Ash owns final governance decisions. Donut plans and
recommends; Ash accepts or defers. Specialized chats propose; Ash confirms.

**Formalized in:** `PROJECT_MASTER.md` (bridge between persona names and
`OPERATING_MODEL.md` generic role labels). `OPERATING_MODEL.md` uses generic
role labels; `PROJECT_MASTER.md` maps them to persona names.

---

## 14. Required Prompt Format

Every task prompt issued to any agent must open with:

```text
[Target: <Agent — Role>]
[Recommended Intelligence: High/Medium/Low/Instant]
```

### Intelligence Level Guidance

| Level | When to use |
|---|---|
| **High** | Governance decisions, technical audits, complex refactors, failing-test diagnosis, architecture analysis, scope conflicts, multi-file consistency checks |
| **Medium** | Normal scoped implementation, standard documentation work, routine scoped verification |
| **Low / Instant** | Mechanical commands, simple file moves, single-fact lookups, regex find/replace, status checks |

### Example

```text
[Target: Anna — Software Development]
[Recommended Intelligence: Medium]

# Phase 6 Package 3 — Pipeline Infrastructure Implementation

Authority:
- DECISION_LOG.md "Phase 6 Package 3 — Pipeline Infrastructure Definition Accepted"
- Current PROJECT_STATE.md
- Current roadmap.md

Objective:
Implement Package 3 per the accepted definition entry.

Scope:
- Add `pipeline_runs` table to `job_search/db/schema.sql`
- Add `services/pipeline.py` read/write service
- Add tests

Do not modify:
- Dashboard routes
- FunnelReporter
- FunnelStats
- Any Package 2 implementation
```

---

## 15. Token and Session Efficiency Rules

- Do not re-summarize project history already in governance docs — reference
  the doc by name and section instead
- Do not inspect files outside the task scope
- Do not re-audit completed work — use governance doc entries as source of
  truth; call out explicitly if you need to verify
- Do not perform broad repo exploration when the target file is known
- Do not include advisory studies, recovery packages, or generated handoff
  docs in implementation or governance commits
- Stop when the task scope is satisfied — do not pre-emptively start next
  tasks
- Read the minimum necessary files; prefer `git show <commit>:<path>` for
  historical lookups over full file reads when only one section is needed

---

## 16. Parallel Implementation Rules

Multiple Anna agents may run in parallel **only when file ownership is fully
separated** — no shared writes:

- Two Annas writing to the same file is never safe
- Two Annas writing to disjoint file sets (e.g., two different new service
  modules with no shared imports in the same file) is safe
- Before issuing parallel tasks, identify every file each agent will modify
  and confirm there is no overlap
- Parallel agents must not depend on each other's outputs within the same wave

**Commit discipline for parallel agents:**
- Each agent commits its own scope in a separate commit
- Do not merge parallel-agent outputs in a single commit unless Ash has
  verified the combined diff is coherent

---

## 17. Immediate Next Workflow

### Step 1 — Initialize (you are doing this now)

Load this document, `PROJECT_STATE.md`, `DECISION_LOG.md`, and `roadmap.md`.
Run `git status --short --untracked-files=all` and `git log --oneline -8`.
Confirm repo state matches §2 and §4. Identify any contradictions or
ambiguities before proceeding.

### Step 2 — Write Phase 6 Package 4 definition entry (JSA track)

**Package 3 is complete (commit `f882405`, 806 passing, Leah audit PASS WITH
MINOR NOTES). Package 4 (local-first background runner) is the next JSA
engineering package.**

Package 4 is authorized but requires its own definition entry before any
implementation begins. Per the standing governance rule, write and accept a
DECISION_LOG entry covering: scope (wrap ingest/grade/generate/follow-up
pipeline steps in a durable local execution layer; persist run stats and errors
to `pipeline_runs`), authorized mutation paths (via PipelineService only),
prohibited paths, acceptance criteria, and any Leah or Donut planning study
references.

After that entry is accepted, issue an Anna implementation task referencing it.

### Step 3 - Prompt ATLAS Desktop Package 1 implementation (Desktop track)

**Desktop v1 tech stack is accepted** (React 18 + TypeScript + Vite + Tailwind
+ FastAPI catch-all; see DECISION_LOG.md "ATLAS Desktop v1 — Frontend Technology
Stack Decision"). Desktop Package 1 - Desktop Shell definition is now accepted;
see DECISION_LOG.md "ATLAS Desktop Package 1 - Desktop Shell Definition
Accepted."

Package 1 implementation may now be prompted. Authorized scope is limited to:
`frontend/` Vite React TypeScript scaffold; ATLAS shell layout; sidebar
navigation; workspace routing placeholders; Context Panel stub; ATLAS
design-token CSS variables; and FastAPI SPA catch-all route registered last.

Package 1 must not implement workspace content, real data integration,
recommendations, Ask Atlas behavior, Pipeline Package 4 work, background runner
work, database/schema changes, or Desktop Package 2+ scope.

This track is parallel to the JSA Phase 6 work. Desktop packages 1-3 are
intended to be file-disjoint from Phase 6 Python work, but the Package 1
implementation will touch `job_search/dashboard/app.py` for the SPA catch-all
and must preserve all existing dashboard/API routes.

**Sequencing constraint:** Do not split Desktop v1 implementation into
parallel agents before file ownership across surfaces is clearly separated.
Surface packages must be defined with non-overlapping file sets.

### Step 4 — Deferred content comparison (CLOSED)

The 7-file deferred recovery comparison is complete. No action required.
See DECISION_LOG.md "ATLAS Recovery — Deferred Overlap-Risk File Review
Completed." Only one file remains KEEP_DEFERRED; six are SKIP_SUPERSEDED.

---

## 18. What Not To Do

A new Ash must not:

- **Restart completed Phase 1–3 debates** — deterministic rendering,
  SQLite-as-source-of-truth, FirmConfig/FirmProfile split are settled
- **Authorize Phase 6 Package 4 implementation before writing its definition
  entry** — the standing governance rule is non-negotiable
- **Treat the ATLAS Workspace Ecosystem Study as accepted** — it is advisory
  and untracked
- **Commit the recovery ZIP** — it must remain untracked permanently
- **Commit the 7 deferred overlap-risk files** without explicit PM authorization
  following a content comparison
- **Add trend/historical data to the Metrics screen** — analytics information
  architecture separates Metrics (strategic/point-in-time) from Pipeline
  Trends (Package 5)
- **Allow `DraftFirmProfile` records to affect scoring, matching, or ingestion**
  — draft isolation is a hard constraint
- **Touch `job_search/`, `tests/`, or `templates/` directly** — route to Anna
- **Let portfolio/README claims describe unimplemented features as done**
- **Trust `MIGRATION_SOURCE_MATERIAL.md` or `PROJECT_HISTORY.md` as current
  state** — those are historical reference only
- **Expand Desktop v1 scope** to include Intelligence Workspace, Professional
  Graph, Career Memory, Forecasting, or enterprise features
- **Treat Desktop Package 1 as workspace implementation** - it is shell-only:
  no workspace content, data integration, recommendations, Ask Atlas behavior,
  Pipeline Package 4 work, background runner work, database/schema changes, or
  Desktop Package 2+ scope
- **Issue parallel implementation tasks** without first confirming disjoint
  file ownership across agents

---

## 19. Source-of-Truth Hierarchy

**Primary (load every session):**
- `PROJECT_STATE.md`
- `roadmap.md`
- `DECISION_LOG.md`

**Secondary (load when the question touches that area):**
- `PROJECT_HISTORY.md` — for "why was X rejected/superseded" questions only
- `docs/Brand/ATLAS_Desktop_v1_Visual_Freeze_Recommendation.md` — visual
  freeze authority
- `docs/Strategy/ATLAS_Desktop_v1_Freeze_Criteria.md` — Desktop v1 scope
  authority
- `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md` —
  Desktop v1 implementation planning authority
- `dashboard_architecture.md`, `dashboard_readiness_review.md`,
  `system_architecture.md`
- Phase-specific architecture docs (`benefit_scoring_design.md`,
  `firm_repository_architecture.md`, `resume_generation_architecture.md`)
- `OPERATING_MODEL.md`, `PROJECT_MASTER.md`, `CHAT_ECOSYSTEM.md`

**Reference-only (do not load as active context):**
- `MIGRATION_SOURCE_MATERIAL.md` — **explicitly superseded; never use**
- Old planning artifacts with resolved decisions
- `docs/ATLAS_Recovery_Package_20260617.zip`

---

## 20. New Ash Initialization Procedure

1. Load `ASH_INIT_NEXT.md` (this document), `PROJECT_STATE.md`,
   `DECISION_LOG.md`, and `roadmap.md`
2. Run `git status --short --untracked-files=all` and `git log --oneline -8`
   to confirm repo state matches §2 and §4 above
3. Identify any contradictions or ambiguities before doing any governance work
4. Only after that check-in, proceed with the authorized task
5. Load additional secondary documents on demand only — do not load the entire
   doc tree upfront
