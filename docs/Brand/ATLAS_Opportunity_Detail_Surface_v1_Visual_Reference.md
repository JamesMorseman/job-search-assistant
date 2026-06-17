# ATLAS Opportunity Detail Surface v1 Visual Reference

**Authority:**

* Opportunity Detail Surface Architecture Study
* Opportunity Detail Wireframe Study
* Desktop Shell Surface Specification
* Desktop v1 Visual Implementation Readiness Study

**Status:** Visual Reference Generation

---

# Design Intent

This surface is the center of Desktop v1.

Radar discovers opportunities.

Pipeline progresses opportunities.

Recommendations reference opportunities.

Ask Atlas explains opportunities.

All four systems converge here.

The visual design should immediately communicate:

```text
This is the opportunity.
```

Not:

```text
This is a recommendation.
```

Not:

```text
This is a job board posting.
```

Not:

```text
This is a tracking record.
```

The opportunity is the primary object.

Everything else exists to provide context.

---

# Desktop Layout

```text
┌──────────────────────────────────────────────────────────────────────┬─────────────────────┐
│                                                                      │                     │
│  Opportunity Identity                                                │                     │
│                                                                      │                     │
│  Structural Engineer I                                               │                     │
│  WSP USA • Seattle, WA • Hybrid                                      │                     │
│                                                                      │                     │
│  Strong Signal      Saved      Reviewing                             │                     │
│                                                                      │                     │
│  [ Track ] [ Save ] [ Add To Pipeline ] [ Ask Atlas ]                │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Atlas Recommendation                                                │                     │
│                                                                      │                     │
│  Atlas recommends prioritizing review of this opportunity.           │ Context Panel       │
│                                                                      │                     │
│  Strong structural alignment                                         │                     │
│  Geographic preference match                                         │                     │
│  Compensation above target                                           │                     │
│                                                                      │                     │
│  ● High Confidence                                                   │                     │
│                                                                      │                     │
│  [ Ask Atlas Why ]                                                   │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Opportunity Summary                                                 │                     │
│                                                                      │                     │
│  Two to three paragraph summary                                      │                     │
│  describing the opportunity,                                         │                     │
│  company, role scope, and                                            │                     │
│  primary responsibilities.                                           │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Requirements                                                        │                     │
│                                                                      │                     │
│  • BS Civil Engineering                                              │                     │
│  • Structural design experience                                      │                     │
│  • FE preferred                                                      │                     │
│  • Steel and concrete familiarity                                    │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Skills & Qualifications                                              │                     │
│                                                                      │                     │
│  Structural Analysis                                                 │                     │
│  Steel Design                                                        │                     │
│  RAM Structural                                                      │                     │
│  AutoCAD                                                             │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Signal Context                                                      │                     │
│                                                                      │                     │
│  Detected 2 hours ago                                                │                     │
│  Source: Company Site                                                │                     │
│  Watchlist: Structural Engineering                                   │                     │
│                                                                      │                     │
├──────────────────────────────────────────────────────────────────────┤                     │
│                                                                      │                     │
│  Full Job Description                                                │                     │
│                                                                      │                     │
│  Collapsed by default                                                │                     │
│                                                                      │                     │
│  [ Expand Full Description ]                                         │                     │
│                                                                      │                     │
└──────────────────────────────────────────────────────────────────────┴─────────────────────┘
```

---

# Right Context Panel

Fixed width:

```text
360px
```

Persistent.

Never modal.

---

# Hierarchy

```text
Opportunity
↓
Related Context
↓
Atlas Context
↓
Focuses
↓
Ask Atlas
```

---

## Section 1

### Related Opportunities

Compact Opportunity Signal references.

```text
Bridge Engineer I

Transportation Engineer

Structural Project Engineer
```

Purpose:

Discovery continuity.

---

## Section 2

### Atlas Context

Compact recommendation references.

```text
Atlas Recommendation

Review before Friday

High Confidence
```

Secondary interpretation layer.

---

## Section 3

### Active Focuses

Operational awareness.

Examples:

```text
Review before Friday

Interview next week

Follow-up due tomorrow
```

Focuses remain operational.

Not strategic.

---

## Section 4

### Ask Atlas

Most important Context Panel action.

Not visually dominant.

Persistent.

---

Example:

```text
Ask Atlas

Why was this recommended?

Compare to another opportunity.

What qualifications matter most?

How should I evaluate this role?
```

Waveform identity appears here.

This is the only Ask Atlas visual language on the surface.

---

# Visual Hierarchy

## Level 1

Opportunity Identity

Largest typography.

Highest contrast.

Dominates above the fold.

---

## Level 2

Atlas Recommendation

Visible immediately.

Clearly secondary to the opportunity.

---

## Level 3

Summary

Requirements

Qualifications

Core evaluation content.

---

## Level 4

Signal Context

Supporting information.

---

## Level 5

Full Job Description

Collapsed.

Reference material only.

---

# Color System

## Deep Navy

Primary background.

---

## Atlas Blue

Structural surfaces.

Section dividers.

Navigation.

---

## Signal Cyan

Restricted.

Only used for:

```text
Strong Signal

Atlas Recommendation accents

Confidence indicators

Ask Atlas waveform
```

Never large fills.

Never dominant backgrounds.

---

## Purple

Focuses.

Offer-related states.

Strategic attention.

---

## Amber

Follow-ups.

Upcoming actions.

---

## Red

Reserved only for:

```text
Interview imminent

Critical deadlines

Offer expiration
```

No general usage.

---

# Motion Behavior

Selecting an Opportunity Signal:

```text
Radar
↓
Opportunity Detail
```

Surface transition.

Not modal.

Not popup.

---

Context Panel persists.

Selected opportunity updates.

Atlas context updates.

Focuses update.

---

# Desktop v1 Success Criteria

A user opening this surface should immediately understand:

```text
What is this opportunity?

Why does it matter?

What should I do next?

How can Atlas help me evaluate it?
```

without feeling like they are reading:

```text
A job board listing

A recommendation dashboard

An ATS record
```

The emotional outcome should be:

```text
This is the opportunity.

Everything I need to evaluate it is here.
```

This makes Opportunity Detail the true center of the ATLAS Desktop v1 ecosystem.
