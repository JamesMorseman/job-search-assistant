# W4-VISUAL-REGISTRY-02 Package Spec

## Package Identity

- Package ID: `W4-VISUAL-REGISTRY-02`
- Track: Track A - Visual Governance Pipeline
- Baseline: `origin/wip/atlas-visual-loop-20260622 @ 2c37046f6fb820be8dab0eb64f531b8408497f5e`
- Branch: `wip/build1/tracka-vr-evidence-backfill-01`

## Purpose

Backfill stale visual-registry evidence/prose so the repository truthfully states
the current Build 1 machine-readable visual registry closed object set and does
not imply visual pass, implementation acceptance, or stale eight-object
coverage.

## Current Truth To Preserve

The current Build 1 machine-readable closed object set is exactly:

- `context_rail`
- `status_metric`
- `atlas_mark`

Evidence strength by group:

- Current grounded objects: the three objects above are the active Build 1
  closed set and are grounded by the registry foundation plus the W4
  implementation report.
- Stale VR01 / prose-only claims: earlier eight-object coverage language is
  historical context only. It is preserved as conflict history when useful, but
  it does not describe the current closed set.
- Deferred VR03 shell objects: `recommendation_card.shell_only`,
  `pipeline_status_item.shell_only`, `progress_indicator`, `metric_tile`,
  `empty_state_panel`, `section_header`, `filter_chip`, and
  `search_input_shell` are deferred shell vocabulary, not current Build 1
  coverage.

## Required Documentation Changes

- Correct or annotate stale W4 package-spec prose that implied eight-object
  visual registry coverage.
- State the current Build 1 machine-readable closed object set exactly.
- Add evidence-strength language for the grounded three-object set, the stale
  VR01/prose-only claims, and the deferred VR03 shell objects.
- Preserve the W4 implementation-report truth that the registry foundation was
  replaced with exactly the three-object current set.
- Clarify that registry validation is not visual pass, render acceptance, or
  implementation acceptance.
- Preserve the conflict history instead of silently normalizing it away.

## Non-Goals

- No new visual objects.
- No registry JSON or schema JSON edits.
- No React, CSS, layout, render, or runtime changes.
- No screenshots, media capture, or image generation.
- No claim of visual pass, implementation acceptance, release readiness, Rin
  sync, P7P6, or public/recruiter release.

## Validation Expectations

- Confirm the changed files are limited to allowed documentation paths.
- Run `git diff --check`.
- Run a diff summary against `origin/wip/atlas-visual-loop-20260622`.
- Search changed files for misleading phrases such as `visual pass`,
  `implementation acceptance`, `release ready`, `public release`, `eight
  objects`, and `8 objects`.

## Output

This package produces documentation-only evidence backfill. It is not a visual
pass, implementation acceptance, or release gate.
