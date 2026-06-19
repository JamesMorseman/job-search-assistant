---
name: project-jsa-p7p5b-visual-corrective-pass
description: Phase 7 Package 5B (ATLAS Visual Alignment Corrective Pass) implementation context and what remains for P7P6 capture gating
metadata:
  type: project
---

P7P5B was implemented on 2026-06-18 on branch `recovery/full-private-state-20260618` at
parent HEAD `0aba075` (docs(governance): record P7P5 visual fail and define P7P5B visual
alignment correction). Governance source: `docs/Architecture/Migration/DECISION_LOG.md`,
"Phase 7 Package 5 — Visual Governance Reconciliation" entry (~lines 4046-4245).

Files changed (frontend only, no commit/push made by Anna — orchestrator must authorize
that separately): `frontend/src/shell/Sidebar.tsx`, `frontend/src/shell/ContextPanel.tsx`,
`frontend/src/shell/shell.css`, `frontend/src/workspaces/OpportunityDetailSurface.tsx`,
`frontend/src/workspaces/opportunityDetailSurface.css`, `frontend/src/workspaces/Radar.tsx`,
`frontend/src/workspaces/radar.css`, `frontend/src/workspaces/AskAtlas.tsx`,
`frontend/src/workspaces/askAtlas.css`.

Key findings before implementing:
- No dedicated ATLAS logo image asset exists anywhere in the repo (checked `git ls-files`
  for image extensions — only `artifacts/png/**` *reference/governance* PNGs exist, no
  brand/logo file). The accepted brand mark per `artifacts/png/workspaces/Desktop Shell
  Reference v1.png` is a text wordmark "ATLAS" + small radial/compass dot icon + small-caps
  kicker "Career Mission Control" — not a separate image file. So the P0 brand fix was
  implemented as a CSS/text wordmark approximation (circular ring + accent dot replacing the
  square "A" tile), not a new image. This is the safe approach per governance hard constraints
  and should be reused if P7P6/Sara re-audit asks for further brand polish.
- The repo has **no frontend test runner** (`frontend/package.json` has no test script).
  All frontend behavior is verified via Python source-inspection tests in `tests/test_desktop_*.py`
  that `read_text()` the `.tsx`/`.css` files and assert on literal strings/class names. This means
  any visual/copy change must be cross-checked against ALL `tests/test_desktop_*.py` files for
  literal string coupling before editing — e.g. `ContextPanel.tsx` default state must keep the
  exact strings "Local Context" and "Workspace context appears here" (test_desktop_demo_readiness.py),
  and several workspaces are explicitly forbidden from importing `ContextPanelContext`/`useContextPanel`
  (CommandCenter, Pipeline) per existing boundary tests — don't wire those into the shared context panel.
- `frontend/dist/` is tracked in git and gets modified by `npm run build`. Running the build for
  validation purposes will show up as a dirty diff (deleted old hashed asset files + modified
  index.html) even though no source-unrelated change was made. Flag this in any future P7P5B/P7P6
  follow-up report rather than assuming it's accidental.

Remaining limitation explicitly reported to the user: no separate ATLAS logo/brand image asset
exists in the repo; only a CSS/text wordmark approximation was implemented per the hard constraint
against inventing new image assets. If Sara's visual re-audit wants a literal logo graphic, that
requires a new explicitly-authorized asset-creation task — not implied by P7P5B.

P7P6 (screenshot capture) remains blocked pending Leah technical re-audit + Sara visual re-audit
of this P7P5B work. Anna did not and must not self-accept this work.

See also [[user_governance_workflow_anna]] for how this user runs the Anna persona.
