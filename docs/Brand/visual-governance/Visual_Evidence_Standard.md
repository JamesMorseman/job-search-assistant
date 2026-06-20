# Visual Evidence Standard

## Purpose

Define what evidence is required and sufficient before a Sara visual audit can be
performed, so audits evaluate against a known standard rather than whatever was
captured. See `VISUAL_GOVERNANCE_V1.md` for governing direction. This standard does not
authorize taking or committing any screenshots, images, or videos - it only defines what
"sufficient evidence" means when capture happens under a separate, explicitly authorized
package.

## Required Evidence Types

| Evidence Type | Use |
|---|---|
| Full surface screenshot | Overall silhouette and layout hierarchy |
| Object crop | Anatomy and local hierarchy at readable scale |
| State variant screenshots | Empty / loading / running / success / error / selected states |
| Motion clip | Animation behavior and prohibited-motion detection |
| Reduced-motion / static capture | Accessibility behavior and screenshot stability |
| Regression screenshots | Shared shell or shared component side effects |
| Measurement notes | Confirms ratios and dimensions when relevant |

## Sufficient Evidence

Evidence is sufficient when it shows:

```text
full surface context (not just a cropped hero area)
the object at readable scale
all required states for the relevant acceptance object
any motion at normal speed
reduced-motion/static behavior when motion exists
shared-shell regression surfaces, if shared CSS/components changed
route, viewport, build/commit, and capture method
```

## Insufficient Evidence

Evidence is insufficient when it:

```text
only shows a cropped hero area
hides the right rail, footer, shell, or status regions
omits motion for an animated object
omits reduced-motion/static mode for an animated object
shows only a best-case selected state
uses different viewport sizes without labeling them
relies on a text description without visual proof
```

## Required Metadata Per Evidence Package

```text
Route captured
Viewport size
Build label / commit hash
Capture method (manual screen recording, browser devtools region capture, etc.)
Motion mode (normal / reduced-motion / static)
```

## Relationship to Existing Practice

This standard formalizes, and does not replace, the evidence-capture instructions
already used for P7P5J (full workspace screenshot, reduced/static-mode screenshot,
per-tier card-mark crops, right-rail crop, status-strip crop, logo/shell crop, motion
clips, and named regression screenshots for Ask Atlas / Opportunity Detail / Command
Center). Future packages should cite this standard instead of re-deriving an evidence
list per package.

## Non-Authorization

```text
This document does not authorize capturing or committing screenshots, images, or videos.
This document does not authorize a Sara visual audit on its own.
Evidence capture remains a separate, explicitly authorized step per package.
```
