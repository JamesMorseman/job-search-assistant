# ATLAS Pipeline Workspace Architecture Study v2

**Owner:** Sara — Visual Design
**Authority:** Project Master (Ash)
**Status:** Architecture Evaluation

---

# Problem Statement

Pipeline v1 correctly identified a major risk:

ATLAS cannot become:

* a Kanban board
* a CRM
* an ATS clone
* a spreadsheet

The proposed Hybrid Mission Flow solved that problem.

However, a second problem emerged:

The workspace may over-prioritize visual progression while under-prioritizing operational decision-making.

In reality, a user managing:

```text
50–200 active opportunities
```

rarely asks:

```text
Where is this opportunity in the flow?
```

They more often ask:

```text
What requires action?

What interview is next?

What needs follow-up?

What is stalled?

What offer requires a decision?
```

The Pipeline workspace must therefore balance:

```text
Progression
+
Operations
```

rather than progression alone.

---

# Option A — Progression-First Workspace

## Core Model

Pipeline visualizes movement.

Primary object:

```text
Opportunity progression
```

Examples:

```text
Detected
↓
Selected
↓
Applied
↓
Interview
↓
Offer
```

---

## Strengths

Creates strong visual identity.

Feels distinct from ATS products.

Reinforces the narrative:

```text
Pipeline executes.
```

Easy to understand conceptually.

---

## Weaknesses

Weak operational awareness.

Important actions become secondary.

Users managing large pipelines must hunt for:

* follow-ups
* interviews
* deadlines
* offers

Progression becomes more visible than decisions.

---

## Scalability

Moderate.

Works well:

```text
10–30 opportunities
```

Struggles:

```text
100+ opportunities
```

because movement visualization becomes dense.

---

## Mission Control Alignment

Good.

But leans toward:

```text
Visualization
```

rather than:

```text
Operations
```

---

## Assessment

Strong concept.

Insufficient primary workspace.

---

# Option B — Operational-First Workspace

## Core Model

Pipeline behaves like a mission queue.

Primary object:

```text
Required actions
```

Examples:

```text
Interview Tomorrow

Follow-Up Due

Offer Requires Decision

Application Stalled
```

Progression becomes secondary metadata.

---

## Strengths

Extremely useful.

Scales well.

Supports large opportunity volumes.

Immediate operational value.

Users instantly know:

```text
What requires attention?
```

---

## Weaknesses

Can drift toward task manager.

Can feel disconnected from progression.

May resemble productivity software.

Weakens the unique Pipeline identity.

---

## Scalability

Excellent.

Works well at:

```text
200+
```

opportunities.

---

## Mission Control Alignment

Strong.

Mission Control naturally prioritizes:

```text
attention
```

over:

```text
history
```

---

## Assessment

Operationally superior.

Visually weaker.

---

# Option C — Hybrid Operational Flow

## Core Model

Pipeline becomes:

```text
Progression-aware Operations
```

not

```text
Progression Visualization
```

and not

```text
Task Management
```

The primary workspace answers:

```text
What requires attention?
```

while maintaining constant awareness of:

```text
Where opportunities are progressing.
```

---

# Workspace Structure

## Zone 1

Pipeline Attention Queue

Highest prominence.

Examples:

```text
Interview Tomorrow

Follow-Up Due Today

Offer Awaiting Decision

Application Stalled
```

This becomes the operational heart of Pipeline.

---

## Zone 2

Progression Overview

Not a Kanban.

Not a board.

Not a flowchart.

Instead:

```text
Detected: 18

Selected: 9

Applied: 22

Interview: 4

Offer: 1
```

Displayed as a monitored progression system.

Users understand flow without living inside flow.

---

## Zone 3

Active Opportunity Stream

Opportunities currently moving through the system.

Examples:

```text
Interview Scheduled

Moved to Screen

Application Acknowledged

Offer Received
```

Pipeline becomes a living progression feed.

---

## Zone 4

Context Panel

Selected opportunity reveals:

* progression history
* next milestone
* follow-up history
* Atlas recommendations
* Ask Atlas

No workspace transitions.

---

# Strengths

Balances:

```text
Operations
+
Progression
```

Scales effectively.

Supports large pipelines.

Retains Mission Control identity.

Creates a distinct workspace role.

---

# Weaknesses

More difficult to design.

Requires strong hierarchy discipline.

Risk of becoming:

```text
Command Center 2.0
```

if differentiation is weak.

---

# Scalability

Excellent.

Supports:

```text
20 opportunities
```

and

```text
200 opportunities
```

without fundamental redesign.

---

# Mission Control Alignment

Strongest alignment.

Mission Control is fundamentally:

```text
monitoring
+
decision support
+
progress awareness
```

This model supports all three.

---

# Comparative Summary

| Model                   | Operations | Progression | Scalability | Mission Control |
| ----------------------- | ---------- | ----------- | ----------- | --------------- |
| Progression First       | Low        | Excellent   | Moderate    | Good            |
| Operational First       | Excellent  | Weak        | Excellent   | Strong          |
| Hybrid Operational Flow | Excellent  | Strong      | Excellent   | Excellent       |

---

# Recommendation

## Adopt: Hybrid Operational Flow

The key insight is:

Pipeline is not primarily a progression visualization tool.

Pipeline is not primarily a task manager.

Pipeline is:

```text
Operational oversight of opportunity progression.
```

Users do not wake up wondering:

```text
How beautiful is my pipeline flow?
```

They wake up wondering:

```text
What needs attention?

What is progressing?

What is stalled?

What decision is next?
```

The workspace should therefore prioritize:

```text
Attention
↓
Progress
↓
History
```

rather than:

```text
Progress
↓
Attention
↓
History
```

---

# Final Direction

Command Center answers:

```text
What changed?
```

Radar answers:

```text
What was discovered?
```

Pipeline answers:

```text
What is progressing and what requires action?
```

This distinction gives Pipeline a unique role within the ATLAS ecosystem while remaining fully aligned with:

```text
ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

Pipeline executes.
```
