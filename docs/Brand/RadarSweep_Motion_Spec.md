# ATLAS RadarSweep — Motion Specification

Package: Phase 7 Package 5I
Type: No-code reference/spec reset
Author: Ash-Master
Date: 2026-06-19
Branch: recovery/full-private-state-20260618 @ d98c8ec
Status: DRAFT — pending Main Ash governance acceptance. Not visual acceptance.

---

## 1. Purpose and authority

Defines the motion model for the canonical RadarSweepMark primitive
(`frontend/src/shell/RadarSweepMark.tsx` + `radarSweepMark.css`) as used inside Radar
workspace SignalCards. Governing input: Sara P7P5H audit section 7 (chosen Option C)
and the user's correction that the current periodic sweep "feels asleep."

This spec REPLACES the current periodic motion model for Radar card dials. It does not
grant visual or governance acceptance.

## 2. Governance exception for Radar card signal objects

```text
Continuous sweep animation is allowed ONLY inside Radar workspace signal objects.
Logo / AtlasMark remains static.
Rings / tracks / center / blips remain static.
Only the sweep ray and its attached tail rotate continuously.
Each card uses a deterministic per-card phase offset.
prefers-reduced-motion disables animation.
Screenshot / static mode freezes each sweep at its deterministic phase offset.
No other workspace receives continuous decorative looping from this exception.
```

This is a scoped exception to the ATLAS Motion & Interaction Specification, which
otherwise forbids continuous decorative looping. It must be recorded in governance by
Rin AFTER P7P5J implementation and audit — not in this package.

## 3. Static-element rules

```text
AtlasMark / brand logo:  STATIC always (Logo System prohibited modifications).
rings / tracks:          STATIC.
center point / hub:      STATIC.
blips:                   STATIC (tier-dependent count; pulsing not authorized here).
ONLY .atlas-sweepmark-rotor (ray + tail) rotates.
```

Current code already isolates rotation to `.atlas-sweepmark-rotor` with
`transform-origin: 50px 50px` (radarSweepMark.css:29-32) — KEEP this isolation. Only
the keyframe/timing changes.

## 4. Motion model decision

```text
CHOSEN: Option C — continuous sweep with deterministic card-specific phase offsets.
REJECTED: Option A (fully static) — reduced-motion/screenshot fallback only.
REJECTED: Option B (periodic 20s hold) — this is the current FAILED model.
REJECTED: Option D (hover/selected only) — secondary interaction only.
```

## 5. Continuous card sweep

```text
animation: continuous full revolution, no static hold.
animation-name:            rotate rotor 0 -> 360deg
animation-duration:        7.5s
animation-timing-function: linear
animation-iteration-count: infinite
```

## 6. Phase offsets for six cards

Deterministic by `cardIndex % 6`. Do NOT randomize per render.

```text
card 1: 0deg
card 2: 57deg
card 3: 114deg
card 4: 171deg
card 5: 228deg
card 6: 285deg
```

Equivalent negative animation-delays (at 7.5s / 360deg = 0.020833s per deg):

```text
card 1:  0s
card 2: -1.1875s
card 3: -2.375s
card 4: -3.5625s
card 5: -4.75s
card 6: -5.9375s
```

## 7. Animation duration and timing

```text
duration: 7.5s per revolution
timing:   linear (constant angular velocity — no ease, this is what made periodic
          motion feel like a refresh indicator)
iteration: infinite
header scope accent: MAY remain static or animate more subtly; card dials are the
          priority. If animated, use the same primitive but it is not required.
```

## 8. Reduced-motion behavior

```text
@media (prefers-reduced-motion: reduce) {
  rotor animation: none;
  rotor rests at its deterministic phase offset (NOT a single shared angle), so the
  field still reads as differentiated when frozen.
}
```

## 9. Screenshot / static mode behavior

```text
In screenshot/static capture mode, freeze each card's rotor at its assigned phase
offset (0/57/114/171/228/285deg). This yields a still frame that already looks like a
live, asynchronously-scanned field rather than six identical dials.
Implementation: a static-mode flag (or the reduced-motion path) sets
transform: rotate(var(--atlas-sweep-phase)) and disables the animation.
```

## 10. Implementation CSS / SVG constraints

```text
- One canonical primitive (RadarSweepMark.tsx) — do not fork geometry per surface.
- transform-origin: 50% 50% (50px 50px in the 100x100 viewBox) — sweep never detaches
  from center (Sara 3.5).
- beam length: 88-96% of outer ring radius.
- tail angular width: 28-42deg.
- tail opacity: 0.45-0.65 at ray edge, fading to 0 behind. Implement as conic/radial
  gradient sector or SVG path ATTACHED to the ray, not a floating pseudo-element.
- per-card phase via CSS custom property (e.g. --atlas-sweep-phase / --atlas-sweep-delay).
- tier color via existing .atlas-sweepmark-<tier> classes (color only, never geometry).
```

Replace current `radarSweepMark.css:34-52` periodic keyframe block. The current rest
angle `rotate(35deg)` and the 20s/92%-hold keyframe are the rejected model.

## 11. Forbidden motion defects

```text
[X] periodic sweep with long static hold (current 20s/92%) — REJECTED
[X] ease-in-out timing on the revolution — must be linear
[X] all six cards synchronized to the same phase
[X] sweep detaching from the dial center
[X] tail as a floating decorative triangle separate from the ray
[X] rotating rings, center, blips, or the AtlasMark
[X] randomized per-render phase
[X] continuous looping leaking into any non-Radar workspace
```

## 12. Motion storyboard (6 frames, one revolution)

Each frame ~1.25s apart over the 7.5s revolution; columns show each card's ray angle
at that instant (base angle + per-card offset, mod 360).

```text
Frame  t       card1  card2  card3  card4  card5  card6
F0     0.00s     0     57    114    171    228    285
F1     1.25s    60    117    174    231    288    345
F2     2.50s   120    177    234    291    348     45
F3     3.75s   180    237    294    351     48    105
F4     5.00s   240    297    354     51    108    165
F5     6.25s   300    357     54    111    168    225
(F6 = F0, loop)
```

Reading: at any instant the six rays sit at six different angles, so the grid always
reads as a live, asynchronously scanned signal field. This table also defines the
deterministic freeze positions for screenshot/static mode (use the F0 column).

## 13. Motion evidence checklist (for P7P5J / Sara)

```text
[ ] All six card dials rotate continuously (no static hold).
[ ] Revolution period measures ~7.5s, linear.
[ ] Six dials show six different ray angles at any frozen instant.
[ ] prefers-reduced-motion disables animation; dials rest at distinct phases.
[ ] Screenshot/static mode freezes dials at deterministic phase offsets.
[ ] Rings, center, blips, AtlasMark all static.
[ ] Tail stays attached to ray, fades 0.45-0.65 -> 0, 28-42deg wide.
[ ] No continuous looping appears in any non-Radar workspace.
```
