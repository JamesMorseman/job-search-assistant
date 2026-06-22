# ATLAS Visual Object Registry Schema

Status: draft registry foundation
Owner: Main Ash / user
Maintained by: visual-governance documentation

## Purpose

This schema defines the first machine-readable ATLAS visual object registry.
It is data and validation only. It does not authorize UI changes, render
changes, screenshot collection, visual acceptance, or implementation acceptance.

The registry is intended to sit between governance language and implementation
mapping. It names the objects, their variants, the screen instances that use
them, and the criteria that must be satisfied before a later implementation
package can wire them into live code.

## Schema hierarchy

The registry is organized in this order:

1. `design_tokens`
2. `visual_primitives`
3. `reusable_visual_objects`
4. `variant_axes`
5. `named_variants`
6. `screen_instances`
7. `state_overrides`
8. `acceptance_criteria`
9. `implementation_mapping`

## Required top-level sections

```text
schema_version
registry_status
objects
variants
screen_instances
```

## Required object fields

Each object entry must include:

```text
object_id
schema_version
status
semantic_role
variant_axes
token_bindings
acceptance_criteria
implementation_mapping
```

## Object status values

```text
candidate
draft
accepted
deprecated
```

This first registry uses `candidate` for every initial object.

## Variant axes

Allowed axis values are symbolic only. Registry entries must reference these
named values instead of introducing ad hoc labels.

```text
size: compact | standard | workspace
density: compact | comfortable | expanded
tier: relevant | emerging | neutral | warning
motion: static | periodic_hold | continuous_sweep
state: default | hover | selected | loading | empty | disabled
surface: dark_panel | shell_panel | modal_panel
emphasis: low | medium | high
```

## Named variant format

Each named variant must include:

```text
variant_ref
object_id
axis_values
token_bindings
state_overrides
acceptance_criteria_refs
implementation_mapping
```

Variant refs are dotted identifiers such as:

```text
radar_workspace.workspace.relevant.default
signal_card.compact.relevant.default
radar_sweep_mark.workspace.relevant.continuous
```

## Screen instance format

Each screen instance must include:

```text
instance_id
object_id
variant_ref
surface
route
state
acceptance_criteria_refs
implementation_mapping
```

## Token binding rules

Token bindings must point to design-token names or token references only. They
must not contain raw colors, raw pixel values, or raw durations.

Examples of allowed symbolic bindings:

```text
token.color.accent
token.motion.continuous_sweep.duration
token.size.card.compact.min_height
```

Examples of disallowed raw bindings:

```text
<raw-hex-color>
<raw-px-value>
<raw-duration-value>
```

## Acceptance criteria rules

Acceptance criteria must be plain-text statements with stable IDs. Later
variants and instances may reference those IDs, but unresolved references are
not allowed.

## Implementation mapping rules

Implementation mapping must describe where an object is expected to appear or be
consumed, but it must not import the registry into live render code in this
first E3.

Example mapping fields:

```text
target
kind
notes
```

## First E3 object set

The initial candidate object set is limited to:

```text
radar_workspace
radar_sweep_mark
signal_card
```

These objects define the first registry foundation for the Radar surface and
its two primary visual object families.

## Panel/badge/control expansion object set

A later, separate data-only package (W4-VISUAL-REGISTRY-EXPANSION-01) extends
the registry foundation above with panel, badge, and control object families.
These objects remain `candidate` status and stay data-only, with no render,
CSS, layout, or motion runtime changes:

```text
panel_surface
tier_badge
status_badge
action_button
icon_button
```

These objects reuse the existing variant axis vocabulary and token namespace
established by the first E3 object set. No new axis values, raw literals, or
schema structure changes were introduced for this expansion.
