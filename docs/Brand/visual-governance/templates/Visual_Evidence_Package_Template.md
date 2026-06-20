# Visual Evidence Package Template

## Status

```text
TEMPLATE ONLY. This file is not an evidence package for any specific package or surface.
Filling this in does not itself authorize capturing or committing screenshots, images,
or videos - that remains a separate, explicitly authorized step per package.
```

## Purpose

Defines the required structure for an actual evidence package once a package has been
explicitly authorized to capture evidence. See `../Visual_Evidence_Standard.md` for the
underlying sufficiency rules this template operationalizes, and
`../templates/Surface_Acceptance_Object_Template.md` for the acceptance object this
evidence is evaluated against.

## Authority Level

```text
Implementation readout / audit evidence. Not accepted governance on its own.
An evidence package does not become a Sara "visual pass" until Sara reviews it, and
a Sara "visual pass" does not become governance acceptance until Main Ash accepts it.
```

## How To Use This Template

```text
1. Copy this file per package/surface once evidence capture has been explicitly
   authorized (this template's existence is not that authorization).
2. Fill in every required metadata field for every piece of evidence listed.
3. Mark any evidence type as "MISSING - <reason>" rather than omitting it silently.
4. Do not claim "sufficient evidence" status yourself - that determination belongs to
   the Sara audit step, per ../Visual_Audit_Classification_Standard.md.
```

## Required Fields

```text
Package:
Surface or Object:
Acceptance Object referenced:
Build label / commit hash:
Capture date:
```

### Required Metadata Per Item (repeat per evidence item)

```text
Evidence type:           (full surface screenshot | object crop | state variant |
                           motion clip | reduced-motion/static capture | regression
                           screenshot | measurement notes - per ../Visual_Evidence_Standard.md)
Route captured:
Viewport size:
Motion mode:              (normal | reduced-motion | static)
Capture method:           (manual screen recording, browser devtools region capture, etc.)
File reference:           (local-only path - do not commit the asset itself here)
Notes:
```

### Evidence Checklist (mark each present / missing, do not delete unused rows)

```text
[ ] Full surface screenshot
[ ] Object crop(s)
[ ] Required state variants (per the relevant object spec / acceptance object)
[ ] Motion clip (if the object/surface has motion)
[ ] Reduced-motion / static capture (if the object/surface has motion)
[ ] Regression screenshots (if shared shell/components changed)
[ ] Measurement notes (if ratio/dimension claims are made)
```

### Sufficiency Self-Check (informational only - not a substitute for Sara audit)

```text
Does the package show full surface context, not just a cropped hero area?
Does it show the object at readable scale?
Does it show all required states for the relevant acceptance object?
Does it show motion at normal speed, if motion exists?
Does it show reduced-motion/static behavior, if motion exists?
Does it include shared-shell regression surfaces, if shared CSS/components changed?
Does every item carry route, viewport, build/commit, and capture method?
```

## Non-Authorization

```text
This template does not authorize capturing or committing screenshots, images, or videos.
This template does not authorize a Sara visual audit on its own.
This template does not authorize push, Rin sync, P7P6, or public/recruiter release.
```
