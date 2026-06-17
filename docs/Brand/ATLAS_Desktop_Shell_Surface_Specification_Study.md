# ATLAS Desktop Shell Surface Specification Study

**Authority:**

* Desktop Shell Architecture Study
* Desktop v1 Surface Inventory Study
* Desktop MVP Experience Cutline Study

**Status:** Surface Specification Study

---

# Executive Observation

The Desktop Shell is not a workspace.

It is not a navigation container.

It is not a dashboard frame.

The shell exists to provide:

```text
Context
Continuity
Orientation
```

across the entire ATLAS experience.

A user should never feel like they are moving between disconnected screens.

Instead they should feel:

```text
I am observing the same system
from different perspectives.
```

This becomes the defining responsibility of the Desktop Shell.

---

# Desktop v1 Shell Philosophy

ATLAS Desktop should feel closer to:

```text
Mission Control

Professional Intelligence Software

Operational Workstation
```

than:

```text
Business Dashboard

Project Management Tool

ATS Software
```

The shell should fade into the background.

Objects should become the focus.

---

# Shell Layout

Desktop v1 should standardize around a four-region model.

```text
┌──────────────────────────────────────────────┐
│ Global Header                               │
├───────┬───────────────────────┬──────────────┤
│       │                       │              │
│       │                       │              │
│Sidebar│   Workspace Region    │ Context Panel│
│       │                       │              │
│       │                       │              │
├───────┴───────────────────────┴──────────────┤
│ Global Notifications Layer                  │
└──────────────────────────────────────────────┘
```

---

# Region 1

## Sidebar

Persistent.

Always visible.

Never scrolls with content.

Provides orientation.

---

# Sidebar Structure

## Primary Navigation

Required:

```text
Command Center

Radar

Pipeline

Ask Atlas
```

These are the only primary destinations in Desktop v1.

---

## Utility Navigation

Lower section:

```text
Documents

Resume Library

Company Repository
```

These are support surfaces.

Not primary workflows.

---

## System Navigation

Bottom region:

```text
Settings

Source Configuration
```

Always separated from workspace navigation.

---

# What Never Appears

The sidebar should never contain:

```text
Opportunity

Recommendation

Focus

Perspective

Case
```

These are objects.

Not workspaces.

Object inflation must be avoided.

---

# Sidebar Behavior

Active workspace remains highlighted.

Workspace switching never resets context automatically.

Context survives navigation whenever possible.

---

# Region 2

## Global Header

Recommended.

Required for Desktop v1.

---

# Purpose

Provides:

```text
Search

Notifications

Atlas Presence

Current Context
```

without expanding sidebar complexity.

---

# Header Layout

```text
ATLAS Logo

Current Workspace

Global Search

Notifications

Atlas Status
```

---

# Atlas Status

Subtle.

Never chat-like.

Examples:

```text
Monitoring Active

2 New Signals

Recommendation Available
```

Atlas should feel present.

Not demanding.

---

# What Does Not Belong

Avoid:

```text
Large metrics

Charts

Activity feeds

Workspace controls
```

The header is navigation and awareness.

Not content.

---

# Region 3

## Workspace Region

Primary content area.

Largest region of the application.

---

# Responsibilities

Workspace region owns:

```text
Command Center

Radar

Pipeline

Ask Atlas
```

content.

---

# Rule

Workspaces answer:

```text
What perspective am I using?
```

Objects should remain secondary until selected.

---

# Region 4

## Context Panel

Persistent secondary intelligence region.

One of the defining elements of ATLAS.

---

# Purpose

Answer:

```text
What else should I know?
```

without forcing navigation.

---

# Default Width

```text
360px
```

Accepted standard.

---

# Empty State

When nothing is selected:

Show:

```text
Atlas Status

Active Focuses

Recent Recommendations

Suggested Investigations
```

The panel remains useful.

Never blank.

---

# Opportunity Selected

Display:

```text
Opportunity Summary

Current State

Atlas Recommendation

Related Objects

Ask Atlas Entry
```

This becomes the primary Context Panel mode.

---

# Pipeline Item Selected

Display:

```text
Current State

Next Step

Upcoming Events

Related Opportunity

Ask Atlas Entry
```

Pipeline should prioritize:

```text
What happens next?
```

over historical progression.

---

# Recommendation Selected

Display:

```text
Recommendation

Reasoning

Related Opportunity

Ask Atlas Why
```

---

# Focus Selected

Display:

```text
Focus

Source Object

Recommended Action

Resolution Options
```

---

# Opportunity Detail Behavior

This is the most important shell decision.

---

# Modal

Rejected.

Modals break context.

---

# Context Panel Only

Rejected.

Opportunity Detail is too important.

---

# Workspace Replacement

Rejected.

Loses orientation.

---

# Recommended Model

## Object Surface

Opportunity Detail launches as a dedicated object surface.

Similar to:

```text
Workspace
↓
Object Surface
```

rather than:

```text
Workspace
↓
Modal
```

---

# Behavior

Example:

```text
Radar
↓
Opportunity Signal
↓
Opportunity Detail
```

The sidebar remains visible.

The shell remains visible.

Context remains visible.

The user never feels lost.

---

# Navigation Result

Users understand:

```text
I am still in ATLAS.
```

not:

```text
I opened another application.
```

---

# Global Search

Search becomes a first-class shell capability.

---

# Placement

Header.

Always available.

---

# Scope

Searches:

```text
Signals

Progressions

Focuses

Recommendations

Companies

Documents
```

---

# Behavior

Results grouped by object type.

Example:

```text
Opportunities

Companies

Recommendations

Documents
```

not one mixed list.

---

# Search Outcome

Selecting a result opens:

```text
Object Surface
```

or

```text
Relevant Workspace
```

depending on result type.

---

# Notifications

Notifications are not Focuses.

This distinction is important.

---

# Notifications

Answer:

```text
What happened?
```

---

# Focuses

Answer:

```text
What matters?
```

---

# Relationship

Example:

Notification:

```text
Interview scheduled.
```

↓

Atlas generates:

```text
Focus

Prepare for interview.
```

Notifications create awareness.

Focuses create prioritization.

---

# Placement

Notification icon:

Header.

Notification history:

slide-over panel.

Not a dedicated workspace.

---

# Atlas Presence Model

Atlas must appear throughout the application.

But never dominate it.

---

# Command Center

Atlas appears through:

```text
Recommendations

Focuses
```

---

# Radar

Atlas appears through:

```text
Contextual Recommendations
```

only.

Radar remains ATLAS territory.

Discovery first.

---

# Pipeline

Atlas appears through:

```text
Next Step Guidance

Recommendation Context
```

Execution remains primary.

---

# Ask Atlas

Atlas becomes explicit.

This is the only workspace where Atlas is the primary actor.

---

# Design Principle

Atlas should feel like:

```text
A strategic intelligence layer.
```

Not:

```text
A chatbot following the user around.
```

---

# Workspace Transition Behavior

Transitions should preserve:

```text
Context

Object Selection

Orientation
```

whenever possible.

---

# Example

User views:

```text
Structural Engineer I
```

in Radar.

Moves to:

```text
Pipeline
```

The Context Panel can continue referencing:

```text
Structural Engineer I
```

until another object is selected.

---

# Context Persistence Rule

Selected object persists.

Workspace changes.

Perspective changes.

Object remains.

This is a major differentiator from dashboard software.

---

# Desktop v1 Context Model

The shell should maintain:

```text
Current Workspace
+
Current Object
```

at all times.

Example:

```text
Workspace:
Radar

Object:
Structural Engineer I
```

or

```text
Workspace:
Pipeline

Object:
WSP Interview
```

This becomes the core state model.

---

# Final Desktop Shell Specification

## Persistent Elements

```text
Sidebar

Header

Context Panel
```

Always present.

---

## Variable Elements

```text
Workspace Region

Object Surface
```

Change based on interaction.

---

## Core Navigation

```text
Command Center
Radar
Pipeline
Ask Atlas
```

Only.

---

## Core Context

```text
Current Workspace

Current Object
```

Always known.

---

## Opportunity Detail

Dedicated object surface.

Not modal.

Not workspace.

Not panel.

---

# Final Recommendation

Desktop v1 should be implemented around a simple but powerful principle:

```text
Workspaces provide perspective.

Objects provide meaning.
```

The shell's responsibility is to ensure users can move between:

```text
Command Center
Radar
Pipeline
Ask Atlas
```

while continuously maintaining awareness of:

```text
What am I looking at?

Why does it matter?

What should I do next?
```

If the shell successfully preserves those three answers, the Desktop v1 experience will feel cohesive, professional, and significantly more like a Career Mission Control system than a collection of disconnected productivity screens.
