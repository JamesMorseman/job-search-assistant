# ATLAS Opportunity SignalCard — Machine Build Specification

Package: Phase 7 Package 5I
Type: No-code reference/spec reset
Author: Ash-Master
Date: 2026-06-19
Branch: recovery/full-private-state-20260618 @ d98c8ec
Status: DRAFT — pending Main Ash governance acceptance. Not visual acceptance.

---

## 1. Purpose and authority

Machine-readable build target for the Opportunity SignalCard as rendered in the Radar
grid. Governing inputs: hero SignalCard reference REF-CARD-A
(`artifacts/png/objects/Opportunity Signal Card v1.png`,
SHA256 279D9280...8949327) and the Sara P7P5H severe audit (sections 3.2-3.5, P0-2).
Does not grant visual or governance acceptance.

## 2. SignalCard visual role

Each card is a self-contained opportunity SIGNAL OBJECT, not a content row with a
radar icon (Sara P0-2). The radar object and opportunity identity dominate; the CTA
is subordinate. In the Radar grid the card is rendered in the COMPACT variant; the
hero/full variant (REF-CARD-A) is the canonical anatomy source.

## 3. Required named zones

Implement the card body as a CSS grid with named regions. Compact (grid) layout:

```text
+-------------------------------------------+
|  [radar]   detected-label      tier-chip  |  <- toprow
|  [radar]   TITLE (job)                     |  <- identity
|  [radar]   company                         |
|            meta row (location / type)      |  <- meta
|  summary band (signal summary)             |  <- summary
|  footer: Save        Review Opportunity    |  <- action
+-------------------------------------------+
```

Hero/full variant adds: 3-metric info row (Detected / Signal Strength / Source) and a
larger left-anchored radar dial, matching REF-CARD-A.

## 4. Card dimensions

```text
min-width:  360px absolute, 390px preferred
min-height: 250px absolute, 280px preferred   <-- MISSING in current code; ADD THIS
target height: 270-320px desktop
padding:    20-24px desktop (current: 24px compact / 32px large — OK)
gap (internal): 16-20px between zones
border-radius: 12-18px (current: 18px — OK)
```

Critical correction (Sara P0-2): current `signalCard.css` declares NO min-height, so
cards render shallow. P7P5J MUST add `min-height: clamp(250px, 28vh, 320px)` (or
equivalent) to `.atlas-signal-card`.

## 5. Zone ratios

```text
radar visual zone:    25-32% of card AREA minimum (Sara 9.3)
title/identity zone:  18-24% of card height
metadata zone:        10-14% of card height
summary zone:         18-24% of card height
action/footer zone:   40-48px high (fixed)
```

The radar zone ratio is satisfied by combining the dial size (Section 7) with the
enforced card min-height. Do not shrink the dial to hit the ratio; raise card height.

## 6. Radar visual zone

```text
compact card dial: 82-112px (current declares 124px — slightly high, re-measure;
                   acceptable if card height supports >=25% area ratio)
hero/full dial:    ~196px (current — OK for hero variant)
zone placement:    left-anchored (compact) / large left block (hero)
zone must read as the card's primary object, not a 32-48px icon.
```

## 7. Identity, metadata, summary zones

```text
identity:
  job title: 17-20px compact / 22-28px hero, weight 700-800, max 2 lines (clamp ok)
  company:   12-14px, accent-strong color, single line ellipsis ok
metadata:
  location / type / size facts, 11-12px (never below 10px)
summary:
  "SIGNAL SUMMARY" micro-label (10.5-11.5px uppercase) + body 12-13px
  body max 3 lines clamp on compact (current — OK)
```

## 8. Footer / action zone

```text
height: 40-48px
primary CTA: "Review Opportunity" (gradient, white-on-accent)
secondary: Save / Saved toggle
CTA glow: LOWER priority than radar object glow (Sara 3.13) — reduce CTA glow
          25-40% if it competes with the dial.
```

### Track action (UNRESOLVED — see ledger Section 6)
```text
The hero reference REF-CARD-A shows THREE actions: Save / Review Opportunity / Track.
The Sara audit + governing rule say "Track is forbidden unless distinct from Save."
P7P5H code removed Track.
DEFAULT FOR P7P5J: keep Track REMOVED unless Main Ash/Sara rule that the reference's
Track is a distinct progression action. Do not silently re-add it.
```

## 9. Selected state rules (R10)

```text
border opacity:  +30-40% over base
outer glow:      +30% radius over base, NO bloom spill into adjacent cards
sweep brightness: +15%
add a selected chip / active marker
right rail selected title MUST equal this card's title exactly
```

## 10. Tier variant matrix (R8)

| Tier | Border | Sweep | Blips | Glow | Chip |
|---|---|---|---|---|---|
| Exceptional | Cyan + Atlas Blue | cyan/blue, high brightness | 3-4 bright | strong controlled outer glow | cyan/blue chip |
| Strong | Atlas Blue dominant | blue/cyan, medium | 2-3 | medium glow | blue chip |
| Relevant | muted cyan / governed secondary | lower brightness | 1-2 | low glow | muted chip |
| Low/Monitor | slate + low cyan | low brightness | 0-1 | minimal | slate chip |

```text
RULE: no ad hoc per-card colors.
NOTE: current code uses a violet family for relevant/emerging tiers. P7P5J must
reconcile against this map (default: follow this map unless a violet tier token is
governance-approved). See ledger Section 6.2.
```

## 11. CTA hierarchy

```text
1. radar/selected object glow (highest)
2. radar sweep + blips
3. CTA button
4. panel borders
5. background atmosphere (lowest)
primary CTA: Review Opportunity (one primary action per card)
do not let the footer bar carry the card's visual weight.
```

## 12. Save / Saved / Track action rules

```text
Save:  toggle, becomes "Saved" when active (is-active state)
Track: FORBIDDEN unless distinct from Save (see Section 8 unresolved item)
no second weak duplicate link (e.g. prior "Open Opportunity Detail" — already removed)
```

## 13. Fail conditions (P7P5J reject if any true)

```text
[X] card has no min-height (renders shallow)
[X] radar object reads as an icon (<25% card area)
[X] 3 columns preserved with card width < 390px
[X] CTA glow visually dominates the radar object
[X] tier colors drift ad hoc per card
[X] footer/CTA occupies the card's primary visual weight
[X] selected state indistinguishable from base
```

## 14. Current-vs-reference summary

| Item | Reference | Current P7P5H | Severity |
|---|---|---|---|
| min-height | 280-320px | none | P0 |
| anatomy | tall tile, named zones | horizontal, shallow | P0 |
| radar zone ratio | >=25% area | subordinated by shallow card | P0 |
| tier colors | cyan/blue-led | violet-led drift | P1 |
| CTA glow | subordinate | competes (exceptional CTA 26px glow) | P1 |
| Track | shown in ref / removed in code | removed | unresolved |
