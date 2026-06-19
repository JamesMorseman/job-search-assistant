# ATLAS Radar Workspace — Machine Build Specification

Package: Phase 7 Package 5I
Type: No-code reference/spec reset
Author: Ash-Master
Date: 2026-06-19
Branch: recovery/full-private-state-20260618 @ d98c8ec
Status: DRAFT — pending Main Ash governance acceptance. Not visual acceptance.

---

## 1. Purpose and authority

Machine-readable build target for the Radar workspace, precise enough that a repo AI
builder (Anna, in P7P5J) can reconstruct the corrected Radar reference without
interpreting generic visual language. Governing inputs: corrected Radar reference
REF-RADAR-A (`artifacts/png/workspaces/Radar Workspace Reference v1.png`,
SHA256 0035EC3F...089F120A) and the Sara P7P5H severe audit. This spec does not grant
visual or governance acceptance and does not authorize push/Rin/P7P6/public release.

## 2. Source reference assets

| ID | Path | SHA256 |
|---|---|---|
| REF-RADAR-A | artifacts/png/workspaces/Radar Workspace Reference v1.png | 0035EC3F0A7221FA375AD34CEB1B5F398704F790070EAF55CE50B02B089F120A |
| REF-RADAR-B | Reference Images/Radar Reference.png | C9A1A3B38DC2F7A108521E992AF3C3A9FD0F1ED29A1DBD66B8C6CD6B0777E9A3 |

Assets are local/uncommitted unless Main Ash authorizes committing them.

## 3. Desktop viewport target

```text
Primary target viewport: ~1920 x 1080 (desktop).
Validation viewport for screenshots: 1920 x 1080.
Secondary check: 1440-wide (cards may drop to 2 columns).
```

## 4. Workspace layout ratios

```text
sidebar:        existing fixed shell width (~210-230px), unchanged
right rail:     clamp(300px, 18vw, 360px)
main content:   remaining width after sidebar + right rail
page header:    115-140px tall (title + subtitle + header scope accent)
filter row:     44-52px tall
status strip:   56-72px tall
card grid gap:  16-20px
card rows:      2 rows, each card min 250px / target 270-320px
bottom dead space: allowed ONLY after card rows reach target height
```

## 5. Sidebar / main / right rail proportions

```text
At ~1920w:
  sidebar      ~220px fixed
  right rail   ~330-360px (clamped)
  main content ~1340px remaining
The cards and right rail must visibly dominate the surface (Sara 3.1).
Do not let the main content read as a compressed horizontal table.
```

## 6. Header / filter / status strip regions

### 6.1 Header (R2)
```text
height: 115-140px
title "Radar": 28-34px, weight 700-800
subtitle "Discovering new opportunities. Continuously.": ~13-15px muted
header scope accent (RadarSweepMark, header tier): ~120-150px, right-aligned
```

### 6.2 Filter row (R3)
```text
height: 44-52px
controls: role/type, location, signal strength, sources, search (all five retained)
search flexes; filters fixed pill controls
```

### 6.3 Status strip (R4)
```text
height: 56-72px (PIN a min-height; current code only sets padding)
left: "<N> Opportunities Detected" primary summary, ~17px weight 800
right: 5 metric cells — New Today, Trending, Strong Signals, Watchlist, Signal Map
metric cell: value (~22px) + label (uppercase ~11px) + status dot
dot color follows tier grammar (cyan = strong signal, blue = brand/default)
panel: low-glow background, clear separators
```

## 7. Grid behavior (R5)

```text
grid-template-columns target:
  if available card width >= 390px: repeat(3, minmax(390px, 1fr))
  if available card width <  390px: repeat(2, minmax(360px, 1fr))
gap: 16-20px
RULE: never preserve 3 columns by collapsing card anatomy below the 390px floor.
RULE: cards stretch vertically (min-height) BEFORE bottom dead space appears.
```

Current P7P5H uses `repeat(3, minmax(330px, 1fr))` (radar.css:149) — the 330px floor
is below the 390px anatomy floor and MUST be raised in P7P5J.

## 8. Card row / column rules

```text
2 rows x 3 columns at >=1920w (6 cards visible).
Cards in a row share equal height (align-items: stretch).
Each card honors min-height (see SignalCard spec) so the row fills before dead space.
At 2-column fallback, 3 rows x 2 columns is acceptable.
```

## 9. Right rail width and module rules (R11-R13)

```text
width: clamp(300px, 18vw, 360px)
module padding: 16-20px
required modules, top to bottom:
  1. Selected Opportunity (header: title + company + tier)
  2. Stage & Status
  3. Related Objects (>= 3 rows if data exists)
  4. Atlas Recommendation (one advisory sentence + one action)
  5. Optional governed investigation/action entry (only if governance permits)
Do not use a compressed mini-card stack.
Rail selected title MUST match the selected card exactly.
```

## 10. Current-vs-reference mismatch table (workspace level)

| Item | Reference | Current P7P5H | Severity | Correction |
|---|---|---|---|---|
| Silhouette | discovery cockpit | compressed dashboard | P0 | tall cards + wide rail + tall strip |
| Right rail width | 330-360px | narrow (shell default) | P0 | clamp(300,18vw,360) |
| Card height | 290-320px | no min-height | P0 | add min-height (SignalCard spec) |
| Grid col floor | ~410-440px cards | minmax(330px) | P0 | raise to minmax(390px) |
| Status strip | 56-72px, 5 cells | padding only, thin | P1 | pin height, 5 cells |
| Header | 120-140px atmospheric | acceptable | P1 | pin min height |
| Filter row | 46-52px | unpinned | P1 | pin height |
| Bottom dead space | only after target h | likely present | P0 | min-height + stretch |

## 11. P7P5J implementation constraints

```text
In scope (workspace level):
  frontend/src/workspaces/Radar.tsx
  frontend/src/workspaces/radar.css
  frontend/src/shell/ContextPanel.tsx        (only if rail width/modules require it)
  frontend/src/shell/ContextPanelContext.tsx (only if rail data mapping requires it)
Out of scope:
  backend / API / schema / data / profile
  Pipeline, Command Center, Ask Atlas, Opportunity Detail
  public / export docs, Rin sync, P7P6, push, public/recruiter release
Constraints:
  - Do not collapse card anatomy to preserve 3 columns.
  - Do not introduce ad hoc per-card colors.
  - AtlasMark and shell rings stay static.
  - Status strip and header heights are pinned, not padding-only.
```

## 12. Screenshot acceptance checklist (for P7P5J / Sara)

```text
[ ] Full Radar at 1920x1080 reads as a discovery cockpit, cards + rail dominate.
[ ] Right rail width measures 300-360px.
[ ] Each card measures min-height >= 250px (target 270-320px).
[ ] Card width >= 390px in 3-column mode, else 2 columns.
[ ] Status strip measures 56-72px tall with left summary + 5 metric cells.
[ ] Header region measures 115-140px.
[ ] Filter row measures 44-52px and shows all five controls.
[ ] No large black dead space below row 2 while cards remain shallow.
[ ] Card radar object reads as a dominant object (>=25% card area), not an icon.
[ ] Glow priority: radar/selected first, CTA subordinate.
```

This checklist is the convergence gate. P7P5J is not visually accepted until Sara
confirms it against REF-RADAR-A.
