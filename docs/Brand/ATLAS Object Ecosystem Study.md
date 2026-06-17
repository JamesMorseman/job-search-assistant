# ATLAS Object Ecosystem Study

**Owner:** Sara — Visual Design
**Authority:** Radar Workspace v3, Pipeline Workspace v5, Intelligence Workspace Direction, Ask Atlas Workspace Direction
**Status:** Ecosystem Architecture Study

---

# Executive Observation

The individual workspace studies have been successful.

However, a more important pattern has emerged.

ATLAS is no longer organizing itself around:

```text
Pages
```

It is organizing itself around:

```text
Objects
```

This is significant.

Many products have workspaces.

Very few products possess a coherent object ecosystem.

The long-term strength of ATLAS may ultimately come from its objects rather than its screens.

---

# Current Candidate Objects

Radar

```text
Opportunity Signal
```

Pipeline

```text
Opportunity Progression
```

Intelligence

```text
Atlas Perspective
```

Ask Atlas

```text
Atlas Case
```

At first glance these appear unrelated.

On closer inspection they form a surprisingly coherent chain.

---

# The Fundamental Lifecycle

A career opportunity moves through four stages of understanding:

---

## Stage 1

### Discovery

Question:

```text
What exists?
```

Object:

```text
Opportunity Signal
```

Owner:

```text
ATLAS
```

Meaning:

```text
Something has been detected.
```

---

## Stage 2

### Progression

Question:

```text
What is happening?
```

Object:

```text
Opportunity Progression
```

Owner:

```text
Pipeline
```

Meaning:

```text
Something is moving.
```

---

## Stage 3

### Interpretation

Question:

```text
What does it mean?
```

Object:

```text
Atlas Perspective
```

Owner:

```text
Atlas
```

Meaning:

```text
Atlas understands something.
```

---

## Stage 4

### Investigation

Question:

```text
What should I understand?
```

Object:

```text
Atlas Case
```

Owner:

```text
Ask Atlas
```

Meaning:

```text
Understanding is being explored.
```

---

# Canonical Object Hierarchy

Current model:

```text
Signal
↓
Progression
↓
Perspective
↓
Investigation
```

This is close.

But not quite correct.

The issue:

Investigation is not downstream of Perspective.

Investigation can originate anywhere.

Example:

```text
Signal
↓
Case
```

or

```text
Progression
↓
Case
```

or

```text
Perspective
↓
Case
```

Therefore the hierarchy is not linear.

It is relational.

---

# Recommended Canonical Model

```text
Opportunity Signal
        ↓
Opportunity Progression

        ↓

Atlas Perspective

        ↘
          Atlas Case
        ↗
```

Meaning:

Signals become Progressions.

Signals and Progressions generate Perspectives.

Cases can investigate any of them.

This is much more accurate.

---

# Workspace Ownership

## Radar

Owns:

```text
Opportunity Signals
```

Does not own:

```text
Progressions
Perspectives
Cases
```

---

## Pipeline

Owns:

```text
Opportunity Progressions
```

References:

```text
Signals
```

May display:

```text
Perspectives
```

---

## Intelligence

Owns:

```text
Atlas Perspectives
```

References:

```text
Signals
Progressions
```

May launch:

```text
Cases
```

---

## Ask Atlas

Owns:

```text
Atlas Cases
```

References:

```text
Signals
Progressions
Perspectives
```

This creates a natural apex position for Ask Atlas.

---

# Object Relationship Analysis

## Opportunity Signal

Purpose:

```text
Detection
```

Emotional state:

```text
Curiosity
```

Question:

```text
What was found?
```

---

## Opportunity Progression

Purpose:

```text
Execution
```

Emotional state:

```text
Momentum
```

Question:

```text
What is happening?
```

---

## Atlas Perspective

Purpose:

```text
Interpretation
```

Emotional state:

```text
Understanding
```

Question:

```text
What does Atlas see?
```

---

## Atlas Case

Purpose:

```text
Investigation
```

Emotional state:

```text
Resolution
```

Question:

```text
Help me understand.
```

The emotional progression is remarkably clean.

---

# Naming Conflict Analysis

## Opportunity Signal

Strong.

Unique.

Distinctive.

No changes recommended.

---

## Opportunity Progression

Functional.

But slightly weaker than Signal.

Potential future risk:

```text
Progression
```

describes state.

Not object identity.

Monitor.

Do not change yet.

---

## Atlas Perspective

Strong.

Differentiated.

Consistent with interpretation.

No conflicts discovered.

---

## Atlas Case

Strong.

Distinct from chat.

Distinct from thread.

Distinct from conversation.

No conflicts discovered.

---

# Missing Objects

Most ecosystems eventually require supporting objects.

Potential future secondary objects:

---

## Perspective Brief

Presentation format.

Derived from:

```text
Atlas Perspective
```

Not primary.

---

## Investigation Brief

Output artifact.

Derived from:

```text
Atlas Case
```

Not primary.

---

## Decision

Potential future object.

Example:

```text
Decision Recorded

Pursue Transportation Focus
```

Could become important if Atlas evolves into long-term career planning.

Not required currently.

---

# Visual Language Consistency

A surprising pattern has emerged.

Radar owns:

```text
Detection
```

Visual language:

```text
Sweep
Return
Signal
```

---

Pipeline owns:

```text
Movement
```

Visual language:

```text
Flow
State
Transition
```

---

Intelligence owns:

```text
Interpretation
```

Visual language:

```text
Lens
Perspective
Focus
```

---

Ask Atlas owns:

```text
Investigation
```

Visual language:

```text
Case
Evidence
Inquiry
Resolution
```

These are complementary rather than overlapping.

This is a strong sign.

---

# Navigation Implications

The current workspace hierarchy:

```text
Command Center

Radar

Pipeline

Intelligence

Ask Atlas
```

maps almost perfectly onto object ownership.

Meaning:

```text
Command Center
```

is not an object workspace.

It is a synthesis workspace.

Everything else is object-centric.

This is a healthy architecture.

---

# Long-Term Scalability

The strongest test:

Can this model support future ATLAS capabilities?

Future features:

```text
Career Coaching

Employability Analysis

Market Intelligence

Compensation Intelligence

Network Analysis

Professional Development
```

All fit naturally.

Because the ecosystem is based on:

```text
Discovery

Progression

Interpretation

Investigation
```

rather than:

```text
Jobs

Applications

Resumes

Chat
```

This is significantly more durable.

---

# Final Recommendation

The object ecosystem should be formally understood as:

```text
Opportunity Signal
        ↓
Opportunity Progression

        ↓

Atlas Perspective

        ↘
          Atlas Case
        ↗
```

Workspace ownership:

```text
Radar
→ Opportunity Signals

Pipeline
→ Opportunity Progressions

Intelligence
→ Atlas Perspectives

Ask Atlas
→ Atlas Cases
```

Supporting artifacts:

```text
Perspective Brief

Investigation Brief
```

This is the first ATLAS-wide object model that:

* aligns with the accepted narrative
* aligns with workspace ownership
* scales beyond job search
* avoids dashboard thinking
* avoids chatbot thinking
* creates a coherent product language

Most importantly, it transforms ATLAS from a collection of features into a system of understanding.

```text
ATLAS scans.
↓
Opportunity Signal

Pipeline executes.
↓
Opportunity Progression

Atlas interprets.
↓
Atlas Perspective

Ask Atlas investigates.
↓
Atlas Case
```

At this point, the object ecosystem is becoming strong enough to serve as the conceptual foundation of the entire product.
