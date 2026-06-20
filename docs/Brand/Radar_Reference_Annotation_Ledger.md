# ATLAS Radar Reference Annotation Ledger

Package: Phase 7 Package 5I — Radar Reference Audit and Machine Build Specification
Type: No-code reference/spec reset
Author: Ash-Master (repo-side project master)
Date: 2026-06-19
Branch: recovery/full-private-state-20260618
HEAD at authoring: d98c8ec
Status: DRAFT — pending Main Ash governance acceptance. Not visual acceptance (Sara owns that).

---

## 0. Authority and scope

This ledger is the reference-decomposition source of truth for the Radar workspace
rebuild (P7P5J). It decomposes the corrected Radar reference image into numbered
regions, records measurement method, and maps current P7P5H behavior against the
reference.

This document does NOT:
- accept P7P5H visually (Sara owns visual acceptance);
- authorize P7P5J implementation (Main Ash owns governance acceptance);
- authorize push, Rin sync, P7P6, or public/recruiter release.

Measurement method note: exact pixel extraction tooling was not run in this package.
Measurements below are RATIO-and-region estimates derived from direct visual
inspection of the rendered reference PNGs at the dimensions recorded in Section 1,
cross-checked against the current implementation CSS (which carries explicit px
values). Where a value is a visual estimate it is marked (est). Where it is read
directly from current implementation CSS it is marked (code). P7P5J must re-measure
against the live build before editing (see acceptance gate in Section 7).

---

## 1. Reference asset inventory

All assets are local. Per P7P5I default policy, images remain LOCAL/UNCOMMITTED
unless Main Ash explicitly authorizes committing reference images to the repo.
This ledger references stable local paths and SHA256 hashes so P7P5J can verify it
is using the same assets.

| ID | Path | Purpose | Bytes | SHA256 | Repo status | Safe to ref in docs | Keep uncommitted |
|---|---|---|---:|---|---|---|---|
| REF-RADAR-A | artifacts/png/workspaces/Radar Workspace Reference v1.png | Corrected Radar workspace reference (primary, highest fidelity) | 2248937 | 0035EC3F0A7221FA375AD34CEB1B5F398704F790070EAF55CE50B02B089F120A | untracked | yes | yes (default) |
| REF-RADAR-B | Reference Images/Radar Reference.png | Corrected Radar workspace reference (secondary, near-identical composition) | 1606719 | C9A1A3B38DC2F7A108521E992AF3C3A9FD0F1ED29A1DBD66B8C6CD6B0777E9A3 | untracked | yes | yes (default) |
| REF-CARD-A | artifacts/png/objects/Opportunity Signal Card v1.png | Hero SignalCard reference (full card anatomy) | 1964680 | 279D9280581D96FEF14A28F3FE72A2867BF0CE698002002379E0378FA8949327 | untracked | yes | yes (default) |
| REF-CARD-B | Reference Images/Opportunity Singal Card Refernce.png | Hero SignalCard reference (visual duplicate of REF-CARD-A) | 1385381 | 4206753AA6626F97CB644969665C659BA1FF81FDA72F74115092CCE571F2710B | untracked | yes | yes (default) |
| REF-PIPE | Reference Images/Pipeline Reference.png | Pipeline reference (used only for defect cross-check) | 1593442 | 0B4811C38CBDB34202D1E2176B3749B79D9E4D57829293F645A0B78031A5C70C | untracked | n/a | yes |
| REF-SUITE | Reference Images/Reference Image suite.png | Full ecosystem suite contact sheet | 1815500 | C2F927F312AE3A9D737C72DCE6BD5C5E0D25587D1BE8FCCF53E1D78324A0522B | untracked | yes | yes |

Supplementary context (NOT live repo truth, external):
- C:\Users\james\Downloads\ATLAS_P7P5H_Severe_Visual_Audit_REFERENCE_SPEC_RESET_REQUIRED.md — controlling Sara verdict, used as governing context.

### 1.1 Prior reference-defect resolution

A previously recorded defect held that `Reference Images/Radar Reference.png` was a
byte-identical duplicate of the Pipeline reference, meaning no true Radar reference
existed. That defect is RESOLVED in the current asset set:

```text
Radar Reference.png    SHA256 C9A1A3B3...0777E9A3
Pipeline Reference.png SHA256 0B4811C3...031A5C70C
Result: DISTINCT. A genuine corrected Radar reference now exists (REF-RADAR-A/B).
```

REF-RADAR-A (artifacts/png) is the higher-resolution canonical source and is the
primary target for P7P5J. REF-RADAR-B corroborates the same composition.

---

## 2. Reference measurement table (ratio-based)

Reference viewport: the reference renders a full desktop ATLAS shell (left nav +
main canvas + right rail). Reading composition by horizontal bands and column split.

Measurement method: proportional decomposition of REF-RADAR-A by visual inspection.
Absolute px values are scaled to a nominal 1920px-wide viewport for P7P5J targeting.

| Region | Reference value (est, @~1920w) | Method |
|---|---|---|
| Sidebar width | ~210–230px fixed | est, matches existing shell |
| Right rail width | ~330–360px | est — rail is a substantial intelligence panel, not a mini-rail |
| Main content width | remaining (~1320–1360px) | derived |
| Page header region (title + subtitle + atmosphere) | ~120–140px tall | est |
| Filter row | ~46–52px tall | est |
| Status strip | ~60–70px tall | est — reads as an instrument band, not a caption |
| Grid area | 3 columns x 2 rows | est (6 cards visible) |
| Card width | ~410–440px | est |
| Card height | ~290–320px | est — cards read as tall tiles |
| Card gap | ~16–20px | est |
| Radar object diameter (in-card) | ~96–112px | est — a dominant object, upper area of card |
| Radar visual zone | ~28–32% of card area | est |
| Right rail module count | 4–5 stacked modules | est (context header, stage/status, related, recommendation, action) |
| Status strip metric count | 5 metric cells + left summary | est (New Today, Trending, Strong Signals, Watchlist, Signal Map) |
| Typography hierarchy | page title dominant; card title strong; metadata compact-but-legible | est |

---

## 3. Current P7P5H measurement table

Source: current implementation CSS at HEAD d98c8ec. Values marked (code) are read
directly from the stylesheets; no live screenshot pixel extraction was performed in
this package, so where the rendered result differs from the declared value it is
noted as a known gap for P7P5J to re-measure.

| Region | Current P7P5H value | Source file | Marker |
|---|---|---|---|
| Card grid | `repeat(3, minmax(330px, 1fr))`, gap 18px | frontend/src/workspaces/radar.css:147-154 | code |
| Grid breakpoint | 2 cols < 1280px, 1 col < 980px | radar.css:156-168 | code |
| Compact card dial | 124px (96px noted in comment, 124px in rule) | frontend/src/workspaces/signalCard.css:41-44 | code |
| Large/featured card dial | 196px | signalCard.css:72-76 | code |
| Card padding | 24px compact / 32px large | signalCard.css:28-39 | code |
| Card border radius | 18px | signalCard.css:6 | code |
| Card min-height | NONE declared | signalCard.css | code (GAP) |
| Card title size | 17px compact / 22px base / 28px large | signalCard.css:131-152 | code |
| Status strip padding | 20px 24px (no fixed height) | radar.css:48-59 | code |
| Status strip total label | 17px | radar.css:61-67 | code |
| Status chip value | 22px | radar.css:105-110 | code |
| Radar mark motion | 20s ease-in-out, 92% static hold + ~1.6s sweep | frontend/src/shell/radarSweepMark.css:34-52 | code |
| Radar mark rest angle | rotate(35deg) | radarSweepMark.css:29-32 | code |
| Reduced motion | animation:none on periodic rotor | radarSweepMark.css:54-58 | code |
| Footer actions | Save + Review Opportunity (Track removed P7P5H) | signalCard.css:250-259 | code |
| Right rail width | governed by shell ContextPanel (not set in radar.css) | — | GAP — must verify |

Known current-vs-declared gaps to re-measure in P7P5J:
- No `min-height` on cards → rendered cards are shallow (Sara P0-2). Declared dial
  sizes do not guarantee the 25–32% area ratio because card height is unconstrained.
- Grid holds 3 columns down to 330px card width, below the 390px anatomy floor
  (Sara: never preserve 3 columns by collapsing anatomy).
- Motion is periodic (20s, 92% hold) — the rejected model (Sara P0-3).

---

## 4. Numbered region ledger (R1–R15)

For each region: visual role / reference behavior / current P7P5H mismatch /
measurable build constraint / P7P5J implication / severity.

### R1 — Shell / sidebar / AtlasMark zone
- Role: persistent left nav + ATLAS identity mark.
- Reference: fixed slim sidebar, static AtlasMark, nav list, account footer.
- Current mismatch: largely correct; not the failure surface.
- Constraint: sidebar fixed width preserved; AtlasMark STATIC (never animates).
- P7P5J: do not alter shell unless rail width change requires it.
- Severity: P2.

### R2 — Page header / title / subtitle / atmospheric header
- Role: "Radar" title + "Discovering new opportunities. Continuously." subtitle + header scope instrument.
- Reference: ~120–140px atmospheric band; strong title; small radar accent at right.
- Current mismatch: acceptable but not strong enough to carry weak cards.
- Constraint: header region 115–140px; page title 28–34px / weight 700–800.
- P7P5J: keep header; ensure it does not shrink below 115px.
- Severity: P1.

### R3 — Filter row / segmented controls / search
- Role: role/type, location, signal strength, sources, search.
- Reference: single horizontal filter band, ~46–52px.
- Current mismatch: present (P7P5G added it); height not pinned.
- Constraint: filter row 44–52px; full control set retained.
- P7P5J: pin height; keep all five controls.
- Severity: P1.

### R4 — Status strip / operational signal summary
- Role: left "N Opportunities Detected" summary + 5 metric cells.
- Reference: instrument band, ~60–70px, reads at a distance.
- Current mismatch: present and improved (P7P5H) but height not pinned; reads thin.
- Constraint: 56–72px tall; left summary + 5 cells (New Today, Trending, Strong Signals, Watchlist, Signal Map); each cell = count + label + dot.
- P7P5J: pin height; ensure 5 cells; dot color tied to tier grammar.
- Severity: P1.

### R5 — SignalCard grid container
- Role: 3x2 opportunity grid.
- Reference: 3 columns x 2 rows of tall tiles; gap 16–20px.
- Current mismatch: 3 cols but cards shallow; 330px min allows anatomy collapse.
- Constraint: 3 cols only if card width >= 390px else 2 cols; gap 16–20px; cards stretch vertically before bottom dead space appears.
- P7P5J: change `minmax(330px,...)` to enforce 390px anatomy floor; add card min-height.
- Severity: P0.

### R6 — Individual SignalCard anatomy
- Role: self-contained opportunity signal object.
- Reference: tall tile — radar zone, identity, summary, meta, footer each distinct.
- Current mismatch: too horizontal/shallow; no min-height; CTA-dominant.
- Constraint: min-height 250px abs / 280px preferred; min-width 360px abs / 390px preferred; named zones (radar/identity/summary/meta/action); padding 20–24px; radius 12–18px.
- P7P5J: add explicit min-height + named grid zones (see SignalCard spec).
- Severity: P0.

### R7 — Radar sweep object inside SignalCard
- Role: primary card-defining object.
- Reference: dominant radar dial (~96–112px) upper area of card; luminous sweep.
- Current mismatch: compact dial 124px declared but subordinated by shallow card; reads as icon.
- Constraint: card radar diameter 82–112px; visual zone >= 25% card area; sweep origin exact center; sweep length 88–96% radius; tail 28–42deg, opacity 0.45–0.65 fading to 0.
- P7P5J: keep canonical RadarSweepMark primitive; enforce zone ratio via card min-height.
- Severity: P0.

### R8 — Signal tier chip / status grammar
- Role: tier label (Strong Signal, etc.) top-right of card.
- Reference: pill chip, tier-colored.
- Current mismatch: present; tier colors drift (relevant=violet, emerging=violet-deep) vs Sara's cyan/blue-led map.
- Constraint: tier map — Exceptional cyan+blue strongest; Strong blue+cyan medium; Relevant muted cyan/governed-secondary low; Low/Monitor slate+low-cyan minimal. No ad hoc per-card colors.
- P7P5J: reconcile current violet tiers against tier map — see Section 6 ambiguity.
- Severity: P1.

### R9 — Card metadata / summary / action footer
- Role: location/type meta row, signal summary band, footer actions.
- Reference: meta row (3 facts), summary band, footer with actions.
- Current mismatch: infogrid hidden on compact; footer = Save + Review Opportunity.
- Constraint: metadata zone 10–14% card height; summary zone 18–24%; action zone 40–48px high; primary CTA "Review Opportunity".
- P7P5J: preserve zones at target card height.
- Severity: P1 (P0 where it forces card shallowness).

### R10 — Selected card state
- Role: active card emphasis synced to rail.
- Reference: stronger border/glow on selected card; rail mirrors it.
- Current mismatch: border+glow present; not strong enough.
- Constraint: selected border opacity +30–40%; outer glow +30% (no bloom into neighbors); sweep brightness +15%; rail title matches selected card.
- P7P5J: strengthen selected state per constraint.
- Severity: P1.

### R11 — Right rail / Opportunity Context
- Role: live selected-opportunity intelligence panel.
- Reference: substantial rail (~330–360px) with stacked modules.
- Current mismatch: too narrow/utility-like; underpowered for silhouette.
- Constraint: width clamp(300px, 18vw, 360px); modules 1) selected opportunity 2) stage/status 3) related objects (>=3 rows) 4) atlas recommendation 5) optional governed action; module padding 16–20px.
- P7P5J: widen rail; ensure module richness (may touch ContextPanel).
- Severity: P0 (width) / P1 (content richness).

### R12 — Related Objects module
- Role: related companies/roles/objects list inside rail.
- Reference: >=3 object rows.
- Current mismatch: present but shallow.
- Constraint: minimum 3 rows if data exists; each row distinct title/icon/body.
- P7P5J: ensure 3+ rows.
- Severity: P1.

### R13 — Atlas Recommendation module
- Role: advisory module in rail.
- Reference: one clear advisory sentence + one action.
- Current mismatch: present; weak hierarchy.
- Constraint: one advisory sentence + one action button.
- P7P5J: enforce single clear advisory + action.
- Severity: P1.

### R14 — Motion model / sweep behavior
- Role: continuous live scanning across card dials.
- Reference: live radar field; cards feel asynchronously scanned.
- Current mismatch: periodic 20s, 92% static hold — feels asleep (Sara P0-3, rejected Option B).
- Constraint: continuous sweep 7.5s linear infinite; per-card deterministic phase offsets (0/57/114/171/228/285deg); rings/center/blips static; AtlasMark static; reduced-motion disables; screenshot/static mode freezes at deterministic phase.
- P7P5J: replace periodic keyframe with continuous rotation + per-card delay (see Motion spec).
- Severity: P0.

### R15 — Color / glow hierarchy
- Role: glow reinforces signal strength, not CTA.
- Reference: radar/selected object glow first; CTA subordinate.
- Current mismatch: CTA glow competes with radar (exceptional CTA has 0 0 26px blue glow).
- Constraint: glow priority — selected card/radar glow > sweep/blips > CTA > panel borders > background. Reduce CTA glow 25–40% if it competes; raise radar glow 15–25% on strong/exceptional.
- P7P5J: rebalance glow tokens.
- Severity: P1.

---

## 5. Current-vs-reference mismatch matrix

| Region | Reference behavior | Current P7P5H behavior | Severity | Measurable correction | P7P5J instruction | Evidence required after P7P5J |
|---|---|---|---|---|---|---|
| Overall silhouette | Discovery cockpit; cards+rail dominate | Compressed dashboard; weak center of gravity | P0 | Tall cards + wide rail + instrument strip | Apply layout ratios in Workspace spec | Full Radar screenshot vs REF-RADAR-A |
| Sidebar/shell | Slim fixed nav | Correct | P2 | none | Leave shell | n/a |
| Header height/atmosphere | 120–140px atmospheric | Acceptable, not strong | P1 | 115–140px region | Pin header min height | Header crop |
| Filter row | 46–52px band | Present, height unpinned | P1 | 44–52px | Pin filter row height | Filter crop |
| Status strip | 60–70px instrument | Present, thin | P1 | 56–72px + 5 cells | Pin height; 5 cells | Status strip crop |
| Grid container | 3x2 tall tiles | 3 cols, shallow | P0 | 390px col floor; 16–20px gap | Raise minmax floor; add min-height | Grid screenshot |
| Card width | ~410–440px | minmax(330px,1fr) | P0 | >=390px or drop to 2 cols | Enforce 390px anatomy floor | Card width measure |
| Card height | ~290–320px | no min-height | P0 | min-height 250 abs/280 pref | Add card min-height | Card height measure |
| Card anatomy | distinct named zones | horizontal, CTA-dominant | P0 | named grid zones w/ ratios | Implement zone grid | Card crop |
| Radar object size | 96–112px dominant | 124px but subordinated | P0 | >=25% card area | Hold dial size + raise card height | Sweep crop |
| Radar object motion | continuous async sweep | periodic 20s hold | P0 | 7.5s linear + phase offsets | Replace motion model | Motion capture (6 phases) |
| Tier differentiation | systematic cyan/blue-led | violet-led, drifts | P1 | tier map | Apply tier map | Tier examples crop |
| Selected state | strong border/glow | present, weak | P1 | +30–40% border, +30% glow | Strengthen selected | Selected card crop |
| CTA hierarchy | subordinate to radar | competes via glow | P1 | reduce CTA glow 25–40% | Rebalance glow | Card crop |
| Right rail width | 330–360px | narrow | P0 | clamp(300,18vw,360) | Widen rail | Rail crop |
| Right rail richness | 4–5 rich modules | shallow | P1 | 5 modules, 3+ related rows | Enrich rail | Rail crop |
| Typography hierarchy | strong titles | titles ok, micro text tiny | P1 | min sizes per Motion/typo spec | Raise min sizes | Card crop |
| Color/glow hierarchy | radar-first | CTA-first | P1 | glow priority order | Reorder glow | Full screenshot |
| Bottom dead space | only after target height | likely dead space below shallow cards | P0 | cards stretch first | Add min-height/stretch | Full screenshot |
| Screenshot readiness | yes | no | P0 | all above | All above | Full set |

---

## 6. Reference ambiguities — RULED by Main Ash (2026-06-19)

1. TRACK ACTION — RULED: keep Track removed for P7P5J. The hero SignalCard
   reference (REF-CARD-A/B) shows THREE footer actions (`Save`, `Review
   Opportunity`, `Track`), conflicting with the Sara P7P5H audit's removal of
   Track. Main Ash ruling: the reference image showing Track is not sufficient
   to override Sara's semantic blocker. Track stays removed unless Donut/Main
   Ash later defines a distinct tracking workflow that justifies reintroducing
   it as a separate action from Save. Not an open ambiguity for P7P5J.

2. TIER COLOR FAMILY — RULED: follow Sara's cyan/blue-led tier map for P7P5J.
   Current code's violet family for "relevant"/"emerging" tiers (P7P5G "Radar
   color grammar") is superseded. Violet must not remain the default for
   relevant/emerging tiers unless a specific stage/status semantic (not yet
   identified) requires a distinct token. Not an open ambiguity for P7P5J.

3. CARD DIAL SIZE. Reference reads ~96–112px; current compact dial is declared
   124px. Within tolerance but P7P5J should re-measure against the live render; the
   real failure is card height/area ratio, not the raw dial px.

---

## 7. Required crops list (local handoff, not committed)

If crops are generated, place in `artifacts/local_visual_handoff/P7P5I/` and DO NOT
commit unless Main Ash authorizes. Required crops for P7P5J:

```text
radar_reference_full.png            (= REF-RADAR-A, already exists local)
radar_reference_annotated_regions.png   (regions R1–R15 overlaid) — MISSING
radar_reference_header_filters_status_crop.png — MISSING
radar_reference_signal_card_crop.png    (= REF-CARD-A, already exists local)
radar_reference_selected_card_crop.png  — MISSING (selected variant not isolatable from current refs)
radar_reference_radar_sweep_crop.png    — MISSING
radar_reference_right_rail_crop.png     — MISSING
radar_reference_status_strip_crop.png   — MISSING
radar_reference_logo_static_crop.png    — MISSING
radar_reference_tier_examples.png       — MISSING
radar_motion_storyboard.md              — provided in RadarSweep_Motion_Spec.md
```

## 8. Missing asset list

- Annotated region overlay image (R1–R15 numbered on the reference).
- Isolated crops (header/status/sweep/rail/tier/logo).
- A dedicated SELECTED-card reference (current refs show default state only).
- An exact-pixel current P7P5H Radar screenshot (only CSS values were available).

None of these block authoring the machine specs (ratios are derivable), but P7P5J
must re-measure the live build before editing.

## 9. Can P7P5J begin?

Conditional YES, pending Main Ash governance acceptance of P7P5I. The corrected
Radar reference exists, is unambiguous in composition, and is decomposed into
measurable regions. The Track and tier-color decisions (Section 6) have been
ruled by Main Ash and are no longer open ambiguities. The missing crops are
helpful but not blocking because the specs encode ratios and px ranges directly.
