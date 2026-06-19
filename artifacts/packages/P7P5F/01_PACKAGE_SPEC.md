# P7P5F — Visual Reference Compliance Stabilization (Package Spec)

Author: Ash-Master. Status: ACCEPTED for implementation (scope-bounded). NOT a new
foundation package. NOT P7P6. NOT a Command Center or Pipeline rebuild.

## Controlling input
Sara's audit "ATLAS P7P5E Visual Audit — New Convergence Governance Ruleset" — verdict
VISUAL FAIL under a hard-gated pass policy (any P0 fail blocks; 3+ P1 issues block
regardless of P0). This package fixes ONLY the specific P0/P1 blockers Sara identified on
candidate surfaces. Command Center (P0 skeleton fail) and Pipeline (P0 Run-Visibility fail)
are EXCLUDED by explicit governance decision — not rebuilt, not lightly polished and
claimed fixed.

## Starting state
- Branch recovery/full-private-state-20260618, start HEAD 43ea232 (P7P5E), 0 behind origin,
  not pushed. Reference images present on disk under `Reference Images/` (untracked, must
  NOT be committed).

## In-scope surfaces (candidate surfaces only)
1. Radar / OpportunitySignalCard (P0/P1 — top priority)
2. Ask Atlas — context-contradiction fix (P0/P1)
3. Opportunity Detail — right rail / advisory / identity (P1)
4. ContextPanelModule system — standardize candidate-surface rails
5. Shell/Brand — LOW-RISK polish only
6. Command Center — EXCLUDED (incidental-only)
7. Pipeline — EXCLUDED/internal (incidental-only)

## Confirmed concrete root causes (grounded in current code, not vibes)
- **SignalCard compact clipping**: `.atlas-signal-card-compact .atlas-signal-card-select`
  is `grid-template-columns: 96px 1fr` but the compact body still renders the FULL content
  set (toprow + h3@22px + company + 3-item metarow + summary block + 3-col infogrid) with
  no compact-specific reduction/clamp. The full content packed into the narrow `1fr` column
  overflows. Fix = compact-specific content hierarchy + line-clamp, not a vibe pass.
  (frontend/src/workspaces/SignalCard.tsx, signalCard.css)
- **Ask Atlas rail contradiction**: main investigation (`DEFAULT_DEMO_INVESTIGATION` in
  AskAtlas.tsx) names "Atlas Demo Infrastructure Group" as a specific demo opportunity, but
  the rail "Related Opportunity" module ALWAYS renders `ContextModuleEmpty title="No
  opportunity attached"` — hardcoded independent of investigation context. Fix = derive the
  rail's attached-opportunity display from the same demo-investigation context so rail and
  main content agree. Prefer acknowledging the attached opportunity over stripping detail.

## Allowed file areas
`frontend/src/**` (.tsx/.css), frontend-only tests if useful/non-invasive, this spec under
`artifacts/packages/P7P5F/`. DENIED: job_search/**, data/**, profile/**, docs/** (except
this spec), scripts/**, non-frontend tests, README/public/release/export, any DB/sqlite, any
image file, credentials/local-settings. NO dependency changes (STOP+report if one seems
needed).

## Binding architectural constraints (carried from P7P5E — must respect)
- The shared/global `ContextPanel.tsx` is covered by
  `test_context_panel_context_does_not_implement_prohibited_behavior` which BANS the literal
  "Ask Atlas" in that file. Ask-Atlas rail work stays local to AskAtlas.tsx (using the
  shared ContextModule library) — do NOT move it into ContextPanel.tsx.
- `AskAtlasInvestigation` stores a single `explanation` string. Do NOT invent investigation
  content, scoring, or LLM calls. Derived cards may only use already-fetched data.
- Opportunity Detail may use segmented sections OR tabs (either acceptable).
- Honest "stored"/"existing-rationale" language on advisory objects — never imply fresh
  live generation.

## Acceptance criteria (this package)
- Build passes (tsc -b && vite build), no new dependencies.
- No forbidden files staged; no images/screenshots committed; no backend/API/schema/data/
  docs/public/export changes.
- Compact SignalCard no longer clips/overflows; preserves radar identity + Save/Review/Track
  row from P7P5E.
- Ask Atlas rail no longer contradicts the main investigation.
- Opportunity Detail + Ask Atlas + Radar rails use consistent module anatomy with designed
  empty states; generic "Local Context" copy removed from these three candidate surfaces.
- Command Center / Pipeline not rebuilt; any incidental shared-component touch reported.
- Visual ACCEPTANCE is NOT granted here — that is Sara's call after screenshots.

## Workflow
Ash defines scope (this doc) -> Anna implements + validates + answers Implementation Friction
Diagnostic + reports -> Ash independently spot-checks the actual diff (Radar compact-card fix
and Ask Atlas rail-contradiction fix read directly) -> Ash synthesizes. Sara/Rin/Leah NOT
invoked unless a sentinel fires. Commit locally only if clean. Do NOT push. Do NOT start P7P6.
