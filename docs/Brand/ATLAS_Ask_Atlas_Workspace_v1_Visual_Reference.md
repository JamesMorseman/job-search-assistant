# ATLAS Ask Atlas Workspace v1 Visual Reference

**Authority:**

* Ask Atlas Surface Specification Study
* Desktop v1 Visual Implementation Readiness Study
* Desktop Shell Surface Specification
* Opportunity Detail Surface Architecture Study

**Status:** Visual Reference Generation

---

# Design Intent

This visual reference exists to answer one question:

```text
Can Ask Atlas feel like Investigation
instead of Chat?
```

The answer should not come from labels.

The answer should come from structure.

The user should immediately perceive:

```text
Question
↓
Investigation
↓
Understanding
↓
Action
```

rather than:

```text
Message
↓
Message
↓
Message
```

The surface should feel closer to:

```text
Mission Analysis
```

than:

```text
Messaging Application
```

---

# Desktop Layout

```text
┌──────────────────────────────────────────────────────────────┬─────────────────────┐
│                                                              │                     │
│ Investigation Header                                         │                     │
│                                                              │                     │
│ Structural Engineer I Evaluation                             │                     │
│                                                              │                     │
│ Opportunity • Recommendation • Interview Stage              │                     │
│                                                              │                     │
├──────────────────────────────────────────────────────────────┤                     │
│                                                              │                     │
│ Attached Context                                             │                     │
│                                                              │                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │                     │
│ │ Opportunity │ │ Recommend.  │ │ Progression │              │                     │
│ │ Structural  │ │ Review This │ │ Interview   │              │                     │
│ └─────────────┘ └─────────────┘ └─────────────┘              │                     │
│                                                              │ Context Panel       │
├──────────────────────────────────────────────────────────────┤                     │
│                                                              │                     │
│ Investigation Surface                                        │                     │
│                                                              │                     │
│ Observation                                                  │                     │
│                                                              │                     │
│ Transportation-focused structural roles                      │                     │
│ are generating stronger interview conversion                │                     │
│ than general civil opportunities.                           │                     │
│                                                              │                     │
│ ----------------------------------------------------------   │                     │
│                                                              │                     │
│ Explanation                                                  │                     │
│                                                              │                     │
│ This opportunity aligns with previously                      │                     │
│ successful applications and exceeds                           │                     │
│ average compensation for comparable roles.                   │                     │
│                                                              │                     │
│ Interview conversion among similar                           │                     │
│ opportunities is currently above baseline.                   │                     │
│                                                              │                     │
│ ----------------------------------------------------------   │                     │
│                                                              │                     │
│ Suggested Action                                             │                     │
│                                                              │                     │
│ Prioritize review before Friday.                             │                     │
│ Consider scheduling interview preparation                    │                     │
│ if application is submitted.                                 │                     │
│                                                              │                     │
│ [ Open Opportunity ]                                         │                     │
│ [ Compare Opportunities ]                                    │                     │
│                                                              │                     │
├──────────────────────────────────────────────────────────────┤                     │
│                                                              │                     │
│ Suggested Follow-Ups                                         │                     │
│                                                              │                     │
│ ○ Why was this recommended?                                  │                     │
│ ○ Compare to transportation roles                            │                     │
│ ○ What qualifications matter most?                           │                     │
│ ○ How should I prepare?                                      │                     │
│                                                              │                     │
├──────────────────────────────────────────────────────────────┤                     │
│                                                              │                     │
│ Ask Atlas                                                    │                     │
│                                                              │                     │
│ Investigate this opportunity, compare alternatives,          │                     │
│ evaluate qualifications, or prepare next steps...            │                     │
│                                                              │                     │
└──────────────────────────────────────────────────────────────┴─────────────────────┘
```

---

# Investigation Header

The header establishes:

```text
What am I investigating?
```

before:

```text
What am I asking?
```

This is the most important distinction from traditional chat interfaces.

---

## Visual Treatment

Large title.

Single-line object identity.

Attached object count.

Subtle Atlas intelligence glyph.

No avatar.

No chat identity.

No assistant profile image.

---

# Attached Context Region

This is the defining visual object of Ask Atlas.

More important than the input.

More important than message history.

---

## Purpose

Makes Atlas reasoning visible.

Users should immediately understand:

```text
Atlas is looking at:
```

* Opportunity
* Recommendation
* Progression
* Focus

---

## Visual Treatment

Compact context capsules.

Object-specific icons.

Atlas Blue containment.

Minimal border weight.

No card clutter.

---

# Investigation Surface

Primary workspace region.

Largest area.

Highest information density.

---

# Structure

Every investigation follows:

```text
Observation
↓
Explanation
↓
Suggested Action
```

No exceptions.

---

# Observation

Atlas states:

```text
What it sees.
```

---

# Explanation

Atlas explains:

```text
Why it matters.
```

---

# Suggested Action

Atlas provides:

```text
What should be considered next.
```

Not commands.

Not tasks.

Strategic guidance.

---

# Visual Treatment

Not chat bubbles.

Not alternating messages.

Not speaker identities.

Not timestamps.

The content should read like:

```text
Investigation Brief
```

generated live.

---

# Suggested Follow-Ups

Placed below understanding.

Not beside the input.

---

## Purpose

Guide deeper investigation.

---

## Visual Treatment

Small investigation prompts.

Waveform accent.

Low-friction interaction.

---

## Example Prompts

```text
Why was this recommended?

Compare alternatives.

Evaluate risk.

Prepare for interview.
```

---

# Investigation Input

Bottom anchored.

Persistent.

Always available.

---

## Design Goal

The input should feel like:

```text
Launch Investigation
```

not:

```text
Send Message
```

---

## Placeholder

```text
Investigate this opportunity...
```

preferred over:

```text
Message Atlas...
```

---

# Context Panel

Fixed width:

```text
360px
```

Matches other ATLAS workspaces.

---

# Section 1

## Investigation Context

Displays currently attached objects.

---

# Section 2

## Related Opportunities

Compact Opportunity Signals.

Discovery continuity.

---

# Section 3

## Atlas Context

Related recommendations.

Supporting intelligence.

---

# Section 4

## Active Focuses

Operational awareness.

Examples:

```text
Review Before Friday

Interview Next Week

Follow-Up Due Tomorrow
```

---

# Ask Atlas Identity

Ask Atlas requires a unique visual language.

---

## ATLAS

Uses:

```text
Radar
Signals
Detection
```

---

## Atlas

Uses:

```text
Node Networks
Interpretation
Intelligence
```

---

## Ask Atlas

Uses:

```text
Waveforms
Investigation Paths
Conversation Threads
```

but never:

```text
Chat Bubbles
```

---

# Color System

## Deep Navy

Workspace foundation.

---

## Atlas Blue

Structural surfaces.

---

## Signal Cyan

Restricted to:

* Waveform accents
* Investigation highlights
* Context attachment indicators

---

## Purple

Strategic interpretation.

Recommendations.

Comparisons.

---

## Red

Only for urgent operational context.

Never part of the investigation experience.

---

# Visual Hierarchy

## Level 1

Investigation Context

---

## Level 2

Observation

Explanation

Suggested Action

---

## Level 3

Follow-Up Investigations

---

## Level 4

Input Surface

---

# Success Criteria

A user opening the workspace should immediately feel:

```text
I am investigating something.
```

Not:

```text
I am chatting with an AI.
```

The ideal emotional sequence is:

```text
Question
↓
Understanding
↓
Confidence
↓
Action
```

If the surface successfully communicates investigation before conversation, then Ask Atlas has achieved its Desktop v1 design objective and established a visual identity distinct from ChatGPT, Slack, Discord, and traditional assistant interfaces.
