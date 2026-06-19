# P7P5D — ATLAS Visual Style Foundation Alignment Pass

Status: DEFINED (implementation dispatched to Anna)
Base commit: b75a782 ("feat(p7p5c): align ATLAS surfaces to corrected visual references")
Branch: recovery/full-private-state-20260618
Defined by: Ash-Master
Supersedes review framing of: Sara "Strict Visual Governance Audit — VISUAL FAIL"

## Naming correction
Sara's attached document calls the next pass "P7P5C". That is stale: P7P5C already
shipped at b75a782. This package is **P7P5D**. All output uses P7P5D.

## Reference-image duplicate check (CONFIRMED)
"Reference Images/Radar Reference.png" is BYTE-IDENTICAL to both
"Reference Images/Pipeline Reference.png" and root "Pipeline Reference.png"
(SHA256 prefix 0B4811C3..., size 1,593,442 each). The supplied Radar reference is a
duplicate of the Pipeline reference. Radar must NOT be overfit to it.
Genuine Radar/signal targets:
- "Reference Images/Opportunity Singal Card Refernce.png" (filename misspelled on disk)
- "Reference Images/Reference Image suite.png"

## Objective
Make runtime demo surfaces materially closer to the accepted ATLAS visual system AND
establish reusable visual objects/tokens so later generated surfaces inherit correct
grammar. Style-foundation work, not per-screen patching. Not product exploration, not
release prep, not docs, not P7P6 capture.

## Authorized scope (frontend/test only)
- P1 Style foundation: AtlasMark fidelity/scale/brightness; sidebar/nav icon system +
  active states; shell/topbar pattern; footer "Runtime Demo Ready" de-emphasis/hide for
  review surfaces; shared tokens (depth, glow, borders, type scale, icon rhythm, spacing)
  in design-tokens.css / shell.css.
- P2 Reusable objects: AtlasMark, SignalCard (OpportunitySignalCard), RecommendationCard,
  ContextPanel modules, ConfidenceScore module, CurrentStateStrip/progression, AskAtlas
  observation/explanation cards, CommandCenter action card (only if CC touched).
- P3 Surfaces in order: (1) OpportunityDetail (2) Radar (3) Ask Atlas
  (4) Command Center only if materially improvable without product expansion; else narrow
  improvement + document gaps.

## Pipeline: EXCLUDED. Keep safe/honest only if shared shell touches it. No rebuild.

## Denied scope (hard)
No real/private data; no data/jobs.db; no credentials/.env/path-leak/resume/cover-letter/
Gmail-Drive/private artifacts; no reference-image commits; no governance updates; no Rin;
no P7P6; no public release; no new dependencies (STOP+report instead); no backend/domain
rebuild (narrow read-only DTO fix only, flagged loudly); no unrelated final-phase features.

## Do-not-stage list (already dirty in tree)
data/jobs.db, .claude/settings.local.json, .claude/agents/*.md,
artifacts/phase1_review/*, "Reference Images/*", "Pipeline Reference.png".

## Leah sentinel conditions
backend/API/service/DB change; real/private data risk; governance/docs/release files
touched; forbidden files staged; data/jobs.db or creds staged; new dependency; Pipeline
rebuilt; unexplained test/build failure; scope creep; unexplained file change.

## Required validation
git diff --stat; git status --short --untracked-files=all; frontend build
(cd frontend; npm run build); frontend/component tests if any; pytest only if a route/DTO
assumption was touched. Demo DB only. Never touch real DB backup.
