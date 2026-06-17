# ATLAS Workspace Navigation Architecture Study

**Owner:** Sara — Visual Design
**Authority:** Command Center Accepted, Radar v3, Pipeline v5, Intelligence Direction, Ask Atlas Direction
**Status:** Experience Architecture Study

---

# Core Observation

Most software products organize around:

```text
Features
```

Examples:

```text
Jobs

Applications

Documents

Analytics

Settings
```

ATLAS is increasingly organizing around:

```text
Modes of understanding
```

Examples:

```text
Discovery

Progression

Interpretation

Investigation
```

This distinction fundamentally changes navigation architecture.

The goal is not:

```text
Where is the feature?
```

The goal is:

```text
What am I trying to understand?
```

---

# Navigation Principle

Each workspace should answer a different question.

---

## Command Center

Question:

```text
What changed?
```

Purpose:

Operational awareness.

---

## Radar

Question:

```text
What was discovered?
```

Purpose:

Discovery.

---

## Pipeline

Question:

```text
What is progressing?
```

Purpose:

Execution.

---

## Intelligence

Question:

```text
What does Atlas understand?
```

Purpose:

Interpretation.

---

## Ask Atlas

Question:

```text
Help me understand.
```

Purpose:

Investigation.

---

# Critical Decision

Navigation should not be understood as:

```text
Page Switching
```

It should be understood as:

```text
Perspective Shifting
```

When users move from Radar to Intelligence they are not changing tools.

They are changing viewpoints.

This is a very important distinction.

---

# Primary Navigation Model

## Recommended Model

```text
Command Center

Radar

Pipeline

Intelligence

Ask Atlas
```

This hierarchy remains correct.

---

# Why Command Center Remains First

Command Center is unique.

It does not own an object.

It owns:

```text
Awareness
```

It synthesizes:

* Signals
* Progressions
* Perspectives
* Recommendations

into one operational view.

Command Center is therefore:

```text
Home
```

not:

```text
Workspace 1
```

---

# Workspace Relationships

## Radar → Pipeline

Natural transition:

```text
Signal
↓
Track
↓
Pipeline
```

User journey:

```text
Discovery
↓
Commitment
```

Most common transition.

---

## Pipeline → Intelligence

Natural transition:

```text
Progression
↓
Interpretation
```

Example:

```text
Why are transportation firms
performing better?
```

---

## Intelligence → Ask Atlas

Natural transition:

```text
Perspective
↓
Investigation
```

Example:

```text
Atlas Perspective
↓
Why?
```

---

## Radar → Ask Atlas

Natural transition:

```text
Opportunity Signal
↓
Case
```

Example:

```text
Why is this opportunity interesting?
```

---

## Pipeline → Ask Atlas

Natural transition:

```text
Opportunity Progression
↓
Case
```

Example:

```text
How should I prepare?
```

---

# Navigation Architecture

## Primary Navigation

Permanent.

Persistent.

Workspace-level.

```text
Command Center

Radar

Pipeline

Intelligence

Ask Atlas
```

These should never move.

These represent the ATLAS operating model.

---

## Secondary Navigation

Workspace-specific.

Examples:

Radar:

```text
All Signals

Watchlist

Companies

Saved
```

Pipeline:

```text
Active

Interviews

Offers

Closed
```

Intelligence:

```text
Perspectives

Lenses

History
```

These remain local.

---

## Utility Navigation

Separate.

Never mixed with primary workspaces.

Examples:

```text
Documents

Settings

Profile
```

These are support functions.

Not part of the operating model.

---

# Context Preservation

This is where ATLAS can become significantly stronger than traditional software.

---

## Rule

Objects persist across workspaces.

Users should never feel like they are starting over.

---

# Example

User selects:

```text
Structural Engineer I
```

inside Radar.

Moves to Pipeline.

The same opportunity remains selected.

Moves to Intelligence.

The same opportunity remains contextual.

Moves to Ask Atlas.

The same opportunity remains attached.

This creates:

```text
Persistent Context
```

instead of:

```text
Page Reset
```

---

# Recommended Context Model

Everything revolves around:

```text
Current Object
```

Examples:

```text
Opportunity Signal

Opportunity Progression

Atlas Perspective

Atlas Case
```

Navigation should preserve the active object whenever possible.

---

# Deep Link Behavior

Deep links should open:

```text
Workspace
+
Object
```

not merely:

```text
Workspace
```

---

## Example

Bad:

```text
Radar
```

Good:

```text
Radar
→ Structural Engineer I
```

---

## Example

Bad:

```text
Intelligence
```

Good:

```text
Intelligence
→ Transportation Hiring Perspective
```

---

## Example

Bad:

```text
Ask Atlas
```

Good:

```text
Ask Atlas
→ Transportation Evaluation Case
```

This dramatically improves continuity.

---

# Multi-Workspace Workflow Model

The most important question:

How do real users move through ATLAS?

---

# Daily Workflow

Typical flow:

```text
Command Center
↓
Radar
↓
Pipeline
```

Questions:

```text
What changed?

What was discovered?

What requires action?
```

This will likely represent 80% of usage.

---

# Weekly Strategic Workflow

Typical flow:

```text
Command Center
↓
Intelligence
↓
Ask Atlas
```

Questions:

```text
What patterns exist?

What does Atlas understand?

Why?
```

This is the strategic review loop.

---

# Opportunity Evaluation Workflow

Typical flow:

```text
Radar
↓
Opportunity Detail
↓
Ask Atlas
↓
Pipeline
```

Questions:

```text
What is it?

Is it worth pursuing?

Why?

Track it.
```

---

# Career Strategy Workflow

Typical flow:

```text
Intelligence
↓
Perspective
↓
Ask Atlas
↓
Case
```

Questions:

```text
What does Atlas see?

Why?

What should I do?
```

---

# Recommended Navigation Philosophy

Most software treats navigation as:

```text
Move between screens.
```

ATLAS should treat navigation as:

```text
Move between layers of understanding.
```

This aligns perfectly with the accepted narrative:

```text
ATLAS scans.
↓
Radar

Pipeline executes.
↓
Pipeline

Atlas interprets.
↓
Intelligence

Ask Atlas communicates.
↓
Investigation
```

---

# Final Recommendation

## Primary Navigation

```text
Command Center

Radar

Pipeline

Intelligence

Ask Atlas
```

Frozen.

---

## Context Model

```text
Persistent Object Context
```

should become a foundational ATLAS behavior.

---

## Deep Link Model

```text
Workspace
+
Object
```

not merely workspace.

---

## Experience Model

Users should feel like they are moving through:

```text
Awareness
↓
Discovery
↓
Execution
↓
Interpretation
↓
Investigation
```

rather than moving through unrelated application pages.

This creates the first navigation architecture that fully supports the emerging ATLAS object ecosystem and scales naturally as the product evolves beyond job search into a broader Career Intelligence System.
