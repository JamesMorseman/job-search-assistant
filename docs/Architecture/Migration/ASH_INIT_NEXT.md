# Ash Initialization Package — Project Master (NEXT)

**Version:** June 2026 - Phase 6 complete (all 5 packages); Phase 7 Packages 1-4 complete; Phase 7 Package 5 definition accepted; Desktop Packages 1-11 complete

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
- **Governance files:** Current governance commit records Phase 7 Packages 1-4
  acceptance and Phase 7 Package 5 definition accepted
- **Implementation files:** Phase 6 complete through `a69b36d`; Phase 7
  Package 1 complete at `1d02117`; Phase 7 Package 2 complete at `65cf0a7`; Phase 7 Package 3 complete at `38314f2`; Phase 7 Package 4 complete at `2227265`;
  Desktop Packages 1-11 committed in
  `d6bdde7`, `42fff28`, `5b19d5e`, `2195cd8`, `c7562de`, `d9eec59`, `913cd4a`,
  `da6aed3`, `e985918`, `bf1655d`, `230bfe4`
- **Test suite:** 1011 passing, 1 skipped, 6 warnings (as of Phase 7 Package 2; no code changes in Package 2)

**Confirm at session start:**

```powershell
git status --short --untracked-files=all
git log --oneline -8
```

**Expected untracked files (intentional — must not be committed without
explicit PM authorization):**

| File | Disposition |
|---|---|
| `.claude/settings.local.json` | Local settings; do not commit without explicit PM authorization |
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
| 7 — Future Enhancements | **Active** — Package 1 complete `1d02117`; Package 2 complete `65cf0a7`; Package 3 complete `38314f2`; Package 4 complete `2227265`; Package 5 definition accepted; implementation authorized |

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
| 1 - Desktop Shell | `frontend/` Vite React TypeScript scaffold, ATLAS shell layout, sidebar navigation, workspace routing placeholders, Context Panel stub, ATLAS design-token CSS variables, FastAPI `/atlas` SPA serving | **Accepted / Complete** - commit `d6bdde7`; 808 passed, 1 skipped, 6 warnings |
| 2 - Core Data Layer | Read-only `/atlas/api` endpoints, opportunity summary/detail DTOs, summary counts, API-local JSON 404 fallback, Pydantic response models, `AtlasDataService`, frontend API client/types/state boundary, API contract/route-isolation tests | **Accepted / Complete** - commit `42fff28`; 817 passed, 1 skipped, 6 warnings |
| 3 - Opportunity Detail Surface MVP | Read-only `/atlas/opportunities/:jobId` route; consumes Package 2 `getOpportunity()` boundary; opportunity-first hierarchy; loading/error/not-found states; route behavior tests | **Accepted / Complete** — commit `5b19d5e`; 828 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 4 - Radar Workspace MVP | Opportunity Signal Card grid via Package 2 API; client-side search and source filter; selected card state; `ContextPanelContext` shell-level context; Context Panel opportunity preview; "Open Opportunity Detail" navigation; loading/error/empty states; tests | **Accepted / Complete** — commit `2195cd8`; 847 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 5 - Pipeline Workspace MVP | `GET /atlas/api/pipeline/runs` read endpoint (consuming Phase 6 Package 3 `PipelineService.list_recent_runs()`); recent pipeline runs list; status indicators; counters and timestamps; frontend API client extension; loading/error/empty states; tests | **Accepted / Complete** — commit `c7562de`; 870 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 6 - Command Center MVP | Opportunity Signal summary panel (Package 2 `getSummary()`); Pipeline Snapshot panel (Package 5 `getPipelineRuns()`); Recommendations deferred-state section; navigation shortcuts to Radar and Pipeline; loading/error/empty states per panel; tests | **Accepted / Complete** - commit `d9eec59`; 892 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT |
| 7 - Recommendations MVP | `RecommendationService` using existing LLM provider abstraction; `GET /atlas/api/recommendations`; `getRecommendations()` frontend client; Command Center Recommendations section populated; loading/error/empty states; tests; stateless at MVP | **Accepted / Complete** - commit `913cd4a`; 903 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT |
| 8 - Ask Atlas Investigation Surface MVP | Investigation-oriented `/atlas/ask-atlas` workspace; attached context; structured observation/explanation/suggested-action/follow-up response via existing LLM provider abstraction; loading/error/empty/context-missing states; tests; stateless at MVP | **Accepted / Complete** - commit `da6aed3`; 921 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT |
| 9 - Atlas Focus MVP | Focus read model/DTO; local-first Focus service deriving active prioritized awareness objects from accepted read sources; optional read-only `/atlas/api/focuses`; frontend client/types; Command Center Focus list; loading/error/empty states; tests; read-only at MVP | **Definition accepted - implementation authorized** |
| 10+ | Later product surfaces and enhancements | Not yet authorized; require separate definition entries |

---

## 4. Recent Commits and What They Mean

```text
(current governance commit)
         docs(governance): accept Phase 7 Package 4 and define Phase 7 Package 5
         DECISION_LOG.md: Phase 7 Package 4 accepted/complete (impl `2227265`;
           Leah ACCEPT WITH MINOR NOTES); Phase 7 Package 5 (Demo Artifact
           Capture and Screenshot Review) definition accepted
         PROJECT_STATE.md: Phase 7 Packages 1-4 complete; Package 5 definition
           accepted; implementation authorized
         roadmap.md: Phase 7 table updated (Package 4 complete, Package 5 row
           added); build order items 7-8 updated
         ASH_INIT_NEXT.md: synchronized to current state

38314f2  tools(launch): add Phase 7 Package 3 local ATLAS launcher
         scripts/start-atlas.ps1 (new): PowerShell launcher; $PSScriptRoot root
         detection; .venv executables guard; jsa check pre-flight; exits if
         diagnostics fail; warns for missing frontend; uvicorn factory start on
         127.0.0.1:8000; prints ATLAS URL and Ctrl+C instruction
         docs/Runbooks/LOCAL_LAUNCH.md (new): operator runbook
         README.md: 1 line added (runbook link)
         (3 files; 224 insertions; 1011 passed, 1 skipped, 6 warnings)

6261569  docs(governance): accept Phase 7 Package 2 and define Phase 7 Package 3

65cf0a7  feat(docs): Phase 7 Package 2 Portfolio Documentation Skeleton
         README.md reframed to ATLAS Career Intelligence / Career Mission Control
         docs/Public/ created: ATLAS_OVERVIEW, TECHNICAL_ARCHITECTURE,
         RECRUITER_BRIEF, PRIVACY_AND_REDACTION, FEATURE_SUMMARY, SCREENSHOTS
         (docs-only; 7 files; 584 insertions, 77 deletions; 1011 passed)

523187b  docs(governance): accept Phase 7 Package 1 and define Phase 7 Package 2

1d02117  feat(cli): implement Phase 7 Package 1 credential diagnostics
         job_search/diagnostics.py (new); jsa check command; jsa run pre-flight
         guard; read-only DB connectivity check; exits 0 if pass, 1 if fail
         (1011 passed, 1 skipped, 6 warnings)

b84f13f  docs(governance): accept Phase 6 Package 5 and define Phase 7 Package 1

a69b36d  feat(dashboard): implement Phase 6 Package 5 Pipeline Runs screen

(prior governance: Desktop Packages 1-11 and Phase 6)
da6aed3  feat(atlas): implement Desktop Package 8 Ask Atlas Investigation MVP
         askAtlas.css (new), ask_atlas.py (new), test_ask_atlas_service.py
         (new), test_desktop_ask_atlas_workspace.py (new); AskAtlas.tsx,
         client.ts, types.ts, deps.py, atlas_api.py modified; GET-only
         /atlas/api/ask-atlas/investigation endpoint; AskAtlasService via
         existing LLM provider abstraction; one active investigation at a time
         (921 passed, 1 skipped, 6 warnings)

44afd74  docs(governance): accept Desktop Package 7 and define Package 8

913cd4a  feat(atlas): implement Desktop Package 7 Recommendations MVP
         recommendations.py (new), test_recommendation_service.py (new),
         test_desktop_recommendations_api.py (new); deps.py, atlas_api.py,
         client.ts, types.ts, CommandCenter.tsx, commandCenter.css, and
         test_desktop_command_center_workspace.py modified; read-only
         /atlas/api/recommendations endpoint; RecommendationService via existing
         LLM provider abstraction; Command Center recommendations populated
         (903 passed, 1 skipped, 6 warnings)

96dc71f  docs(governance): accept Desktop Package 6 and define Package 7

d9eec59  feat(atlas): implement Desktop Package 6 Command Center MVP
         commandCenter.css (new), test_desktop_command_center_workspace.py
         (new); CommandCenter.tsx modified; /atlas/command-center route;
         Opportunity Signal summary via getSummary(); Pipeline Snapshot via
         getPipelineRuns(); Recommendations deferred-state section;
         navigation shortcuts; independent loading/error/empty states
         (892 passed, 1 skipped, 6 warnings)

1442b0f  docs(governance): accept Desktop Package 5 and define Package 6

c7562de  feat(atlas): implement Desktop Package 5 Pipeline Workspace MVP
         pipeline.css (new), test_desktop_pipeline_workspace.py (new);
         Pipeline.tsx, client.ts, types.ts, atlas_api.py, deps.py modified;
         /atlas/pipeline route; GET /atlas/api/pipeline/runs endpoint via
         PipelineService.list_recent_runs(); getPipelineRuns() client method;
         run list with status, counters, timestamps; loading/error/empty states
         (870 passed, 1 skipped)

9757fe5  docs(governance): accept Desktop Package 4 and define Package 5

2195cd8  feat(atlas): implement Desktop Package 4 Radar Workspace MVP
         ContextPanelContext.tsx (new), radar.css (new),
         test_desktop_radar_workspace.py (new); Radar.tsx, AppShell.tsx,
         ContextPanel.tsx, shell.css modified; /atlas/radar route; Signal Cards
         from getOpportunities(); client-side search and source filter; selected
         card state; Context Panel preview; "Open Opportunity Detail" nav
         (847 passed, 1 skipped)

2282184  docs(governance): accept Desktop Package 3 and define Package 4

5b19d5e  feat(atlas): implement Desktop Package 3 Opportunity Detail Surface MVP
         OpportunityDetailSurface.tsx, opportunityDetailSurface.css,
         test_desktop_opportunity_detail.py; /atlas/opportunities/:jobId route;
         consumes Package 2 getOpportunity() boundary
         (828 passed, 1 skipped)

50cf8b7  docs(governance): accept Desktop Package 2 and define Package 3

42fff28  feat(atlas): implement Desktop Package 2 data API boundary
         read-only /atlas/api endpoints, AtlasDataService, Pydantic response
         DTOs, frontend/src/api client/types/state boundary, API route tests
         (817 passed, 1 skipped, 6 warnings)

66f5165  docs(governance): accept Desktop Package 1 and define Package 2
d6bdde7  feat(atlas): implement Desktop Package 1 shell
3edd347  docs(governance): define ATLAS Desktop Package 1 shell

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

### Step 3 - Prompt ATLAS Desktop Package 10 implementation (Desktop track)

**Desktop Packages 1 through 9 are complete and accepted.** Desktop Package 10 -
Atlas Focus Resolution & Archive MVP definition is accepted; implementation is
now authorized. See `DECISION_LOG.md` "ATLAS Desktop Package 10 - Atlas Focus
Resolution & Archive MVP Definition Accepted."

Package 10 implementation may now be prompted. Authorized scope: add bounded
Focus resolution mutations, archive/history support, local persistence needed
to preserve resolved Focus history, frontend client/types through the existing
`client.ts` boundary, and Command Center resolution/archive presentation.

Package 10 must remain Focus-domain only. It must not implement generic task
management, reminders, notification center, alert system, calendar
integration, Ask Atlas changes, recommendation generation changes,
Radar/Pipeline/Opportunity Detail behavior changes, scoring or ingestion
changes, background runner/scheduler behavior, pipeline execution,
hard-coded LLM provider, cloud sync, or Tauri packaging.

Package 10 must preserve the distinction between Recommendation and Focus: a
recommendation says what Atlas suggests; a Focus says what deserves attention.
Resolution-state display is allowed, but state-changing controls are not
authorized.

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
- **Treat Desktop Package 10 as authorizing generic task management or focus
  mutations**
  - Package 10 is Atlas Focus Resolution & Archive MVP focus-lifecycle only.
    No generic task management, reminders, notification center, alert system,
    calendar integration, Ask Atlas behavior changes, recommendation generation
    changes, closed workspace behavior changes, background runner, scheduler,
    pipeline execution, cloud sync, or Tauri packaging.
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
