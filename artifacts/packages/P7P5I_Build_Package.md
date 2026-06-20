# Phase 7 Package 5I — Radar Reference Audit and Machine Build Specification

Type: No-code reference/spec reset
Author: Ash-Master (repo-side project master)
Date: 2026-06-19
Branch: recovery/full-private-state-20260618 @ d98c8ec
Status: DRAFT — pending Main Ash governance acceptance.

> P7P5I is a reference/spec package, not visual acceptance. It does not authorize
> P7P5J until Main Ash accepts the package. It does not authorize push, Rin sync,
> P7P6, or public/recruiter release. Sara owns visual acceptance.

---

## 1. Package summary

P7P5H was technically clean (read-only auditor PASS) but failed visual acceptance
(Sara: HARD VISUAL FAIL + REFERENCE / SPEC RESET REQUIRED, 2.5/10). Root cause is an
instruction/spec gap, not a code defect: repo agents lacked a measurable,
reference-decomposed Radar build target. P7P5I closes that gap by producing
machine-oriented specs and a reference annotation ledger, so that P7P5J can implement
against measurable targets rather than generic visual prose. No code was changed.

## 2. Live repo state

```text
branch: recovery/full-private-state-20260618 (verified)
HEAD:   d98c8ec fix(p7p5h): canonicalize radar geometry and motion behavior
ahead/behind origin: ahead 6, behind 0
```

Pre-existing dirty/untracked files (settings, agent-memory, jobs.db, dist artifacts,
reference images, P7P5E artifacts, agent backups) are UNRELATED to P7P5I and were not
staged.

## 3. Source audit inputs

```text
- REF-RADAR-A: artifacts/png/workspaces/Radar Workspace Reference v1.png (corrected reference, primary)
- REF-RADAR-B: Reference Images/Radar Reference.png (corrected reference, secondary)
- REF-CARD-A:  artifacts/png/objects/Opportunity Signal Card v1.png (hero card anatomy)
- Sara P7P5H severe audit (external context): ATLAS_P7P5H_Severe_Visual_Audit_REFERENCE_SPEC_RESET_REQUIRED.md
- Current implementation CSS: radar.css, signalCard.css, radarSweepMark.css @ d98c8ec
```

## 4. Files created / updated

```text
docs/Brand/Radar_Reference_Annotation_Ledger.md      (new)
docs/Brand/Radar_Workspace_Machine_Build_Spec.md     (new)
docs/Brand/SignalCard_Machine_Build_Spec.md          (new)
docs/Brand/RadarSweep_Motion_Spec.md                 (new)
artifacts/packages/P7P5I_Build_Package.md            (this file, new)
```

No frontend/backend/schema/data/public/export files were touched.

## 5. Reference asset ledger summary

The prior "Radar reference is a duplicate of Pipeline" defect is RESOLVED: Radar and
Pipeline reference images now hash distinctly. A genuine corrected Radar reference
exists (REF-RADAR-A/B). Per default policy, reference images remain LOCAL/UNCOMMITTED
unless Main Ash authorizes committing them. Full inventory with SHA256 hashes is in
`docs/Brand/Radar_Reference_Annotation_Ledger.md` Section 1.

## 6. Current-vs-reference measurement summary

Reference reads as a discovery cockpit: ~330-360px right rail, 3x2 grid of ~410-440px
wide / ~290-320px tall cards, 96-112px dominant card dials, 56-72px instrument status
strip. Current P7P5H: 3 columns at minmax(330px,1fr), NO card min-height (cards render
shallow), 124px compact dial subordinated by shallow cards, status strip with padding
but no pinned height, periodic 20s/92%-hold sweep motion. Full tables in the ledger
(Sections 2-3, 5) and the two build specs.

## 7. P0 / P1 / P2 blocker mapping

### P0 (composition / structure — block convergence)
```text
P0-1 Radar silhouette not reference-convergent (compressed dashboard).
     -> apply workspace layout ratios (Workspace spec S4-S9).
P0-2 SignalCards wrong as objects (no min-height, too horizontal, CTA-dominant).
     -> add min-height clamp(250px,28vh,320px) + named zones (SignalCard spec S3-S5).
P0-3 Motion model wrong (periodic 20s hold feels asleep).
     -> continuous 7.5s linear sweep + per-card phase offsets (Motion spec S5-S6).
P0-4 Radar object lacks reference-grade scale/motion anatomy.
     -> dial >=25% card area + canonical sweep geometry (SignalCard S6, Motion S10).
P0-5 Right rail too narrow/underpowered.
     -> clamp(300px,18vw,360px) + 4-5 rich modules (Workspace spec S9).
P0-6 No machine-oriented spec existed.
     -> RESOLVED by this package.
```

### P1 (richness / hierarchy)
```text
P1-1 Tier differentiation weak / violet drift -> apply tier map (SignalCard S10).
P1-2 Selected state weak -> +30-40% border, +30% glow (SignalCard S9).
P1-3 Status strip thin -> pin 56-72px, 5 cells (Workspace S6.3).
P1-4 Typography too small -> min sizes (SignalCard S7).
P1-5 CTA glow competes with radar -> reduce 25-40% (SignalCard S11).
P1-6 Rail module hierarchy weak -> enforce module anatomy (Workspace S9).
```

### P2 (polish, after structure passes)
```text
copy refinements, chip labels, hover states, micro spacing.
```

## 8. Exact P7P5J implementation handoff

See Section 12 (P7P5J definition). In short: implement the four specs against
`frontend/src/workspaces/Radar.tsx`, `radar.css`, `SignalCard.tsx`, `signalCard.css`,
`frontend/src/shell/RadarSweepMark.tsx`, `radarSweepMark.css`, and (only if rail
requires) `ContextPanel.tsx` / `ContextPanelContext.tsx`. Re-measure the live build
before editing and output the seven pre-edit artifacts (Section 13).

## 9. Stop conditions for P7P5J

```text
- Stop if the agent cannot output the 7 pre-edit artifacts (Section 13).
- Stop if implementing would require backend/API/schema/data/public/export changes.
- Track and tier-color (ledger S6) are RULED, not open: Track stays removed;
  tiers follow Sara's cyan/blue-led map. Do not relitigate either in P7P5J.
- Stop if a change would require committing reference images without Main Ash approval.
```

## 10. Acceptance criteria for P7P5I

```text
1. Reference regions R1-R15 numbered and described.            DONE
2. Current screenshot/CSS compared to reference by region.     DONE (CSS-based; live
   re-measure deferred to P7P5J).
3. All P0 visual failures mapped to measurable corrections.    DONE
4. Motion model decided: continuous card sweeps + phase offsets, reduced-motion,
   screenshot mode.                                            DONE
5. Specs avoid placeholders and generic language.              DONE
6. A repo builder could implement from the docs without Sara reinterpreting "make it
   more like the reference."                                   YES. Main Ash has
   ruled both ledger S6 decisions (Track removed; cyan/blue tier map); no
   outstanding product ambiguities block implementation.
```

## 11. Whether P7P5I is ready for Main Ash review

YES, and Main Ash has reviewed and ruled both Section 6 decisions (2026-06-19):
Track stays removed (the reference image's Track does not override Sara's
semantic blocker, absent a Donut-defined distinct tracking workflow); tiers
follow Sara's cyan/blue-led map (violet is not retained as default for
relevant/emerging tiers absent a specific stage/status semantic). Recommended:
Sara review P7P5I specs before P7P5J implementation begins.

---

## 12. Phase 7 Package 5J — Radar Reference-Convergent Workspace Rebuild (DEFINITION ONLY — DO NOT IMPLEMENT)

```text
Objective:
  Implement the Radar workspace to converge on REF-RADAR-A using the accepted P7P5I
  machine specs.

Files likely in scope:
  frontend/src/workspaces/Radar.tsx
  frontend/src/workspaces/radar.css
  frontend/src/workspaces/SignalCard.tsx
  frontend/src/workspaces/signalCard.css
  frontend/src/shell/RadarSweepMark.tsx
  frontend/src/shell/radarSweepMark.css
  frontend/src/shell/AtlasMark.tsx          (only to preserve static logo)
  frontend/src/shell/Sidebar.tsx            (only to preserve shell layout)
  frontend/src/shell/ContextPanel.tsx       (only if rail width/modules require it)
  frontend/src/shell/ContextPanelContext.tsx (only if rail data mapping requires it)
  tests/test_desktop_radar_visual_geometry.py
  tests/test_desktop_radar_workspace.py
  tests/test_desktop_demo_readiness.py

Files out of scope:
  backend / API / schema / data / profile
  Pipeline, Command Center, Ask Atlas, Opportunity Detail rebuilds
  public / export docs
  Rin sync, P7P6, push, public/recruiter release

Reference assets required:
  REF-RADAR-A, REF-CARD-A (local, verify SHA256 from ledger S1)

Machine specs required (must be accepted first):
  Radar_Workspace_Machine_Build_Spec.md
  SignalCard_Machine_Build_Spec.md
  RadarSweep_Motion_Spec.md
  Radar_Reference_Annotation_Ledger.md

Implementation sequence:
  1. Output the 7 pre-edit artifacts (Section 13).
  2. Card min-height + named zones (P0-2).
  3. Grid floor 390px + 2-col fallback (P0-1).
  4. Right rail width + modules (P0-5).
  5. Continuous sweep motion + phase offsets (P0-3).
  6. Status strip height + 5 cells (P1-3).
  7. Tier map + glow hierarchy (P1-1, P1-5).
  8. Selected state strengthening (P1-2).

Acceptance criteria:
  Workspace + SignalCard + Motion screenshot/motion checklists all pass (see specs).

Screenshot evidence required:
  full Radar 1920x1080, card crop, sweep crop, rail crop, status strip crop.

Motion evidence required:
  6-phase frozen capture proving distinct ray angles + continuous 7.5s linear sweep.

Read-only auditor requirements:
  Leah read-only audit for scope compliance, no backend/data drift, tests pass.

Sara re-audit requirements:
  Sara visual re-audit against REF-RADAR-A. P7P5J is NOT accepted without it.

Stop conditions:
  As Section 9.
```

## 13. AI-builder pre-edit requirements for P7P5J

Before editing any code, the P7P5J agent MUST output:

```text
1. Current screenshot measurement table (live build, measured).
2. Reference measurement table.
3. Proposed layout grid map.
4. Proposed SignalCard anatomy map.
5. Proposed RadarSweep geometry and motion plan.
6. File scope list.
7. Explicit risks and unresolved reference ambiguities.
If the agent cannot produce these, implementation MUST stop.
```

P7P5J must NOT:
```text
- do more small polish without matching the machine spec
- do a local component tweak without a full Radar screenshot comparison
- preserve 3 columns if it collapses card anatomy
- use periodic sweep as primary Radar card motion
- treat a technical/test pass as visual convergence
- implement generic "premium"/"more polished" changes without measurable targets
```

## 14. Recreate-the-reference success test

```text
Given only the P7P5I reference assets and machine specs, could an AI builder reproduce
a Radar screen whose silhouette, card proportions, sweep motion, right rail, and status
strip are recognizably the corrected Radar reference?
```

Answer: YES — enough to attempt P7P5J. The composition is decomposed into measurable
regions, every P0 maps to a px/ratio/timing correction, and the motion model is fully
specified with a storyboard. The two product-decision points (Track action; tier
color family) have been ruled by Main Ash (ledger S6, 2026-06-19) and no longer
carry residual ambiguity.
