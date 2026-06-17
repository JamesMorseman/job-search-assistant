# ATLAS Desktop v1 Implementation Translation Study

**Owner:** Sara — Visual Design
**Authority:** Desktop MVP Cutline, Desktop Shell Architecture, Object Ecosystem, Personal Edition Strategy
**Status:** Product Translation Study

---

# Executive Summary

Desktop v1 should not attempt to build the full Career Intelligence Platform.

Desktop v1 should prove the daily loop:

```text
ATLAS scans.
Atlas recommends.
User decides.
Pipeline progresses.
Ask Atlas explains.
```

The minimum complete product is not every future workspace.

It is a coherent personal desktop application that allows one user to:

```text
Discover opportunities
Evaluate opportunities
Track progress
Resolve daily focuses
Ask contextual questions
```

without leaving ATLAS.

---

# 1. Complete Desktop v1 Workflow

## Primary Daily Flow

```text
Startup
↓
Command Center
↓
Review Focuses
↓
Review Recommendations
↓
Review New Signals
↓
Open Opportunity Detail
↓
Track / Save / Review
↓
Pipeline
↓
Resolve follow-ups / interviews / offers
↓
Ask Atlas when explanation is needed
```

This is the core v1 experience.

---

# Most Common Flows

## Flow A — Morning Awareness

```text
Open ATLAS
↓
Command Center
↓
Review Atlas Focuses
↓
Resolve urgent items
```

Purpose:

```text
What needs attention today?
```

---

## Flow B — Discovery

```text
Command Center
↓
Radar
↓
Opportunity Signal
↓
Opportunity Detail
↓
Save / Track / Ignore
```

Purpose:

```text
What did ATLAS find?
```

---

## Flow C — Application Progression

```text
Command Center
↓
Pipeline
↓
Opportunity Progression
↓
Update State
↓
Schedule Follow-Up
```

Purpose:

```text
What is moving and what is stuck?
```

---

## Flow D — Explanation

```text
Recommendation / Opportunity / Progression
↓
Ask Atlas
↓
Contextual answer
↓
Return to workflow
```

Purpose:

```text
Why does this matter?
```

---

# Minimum Complete Flow

Desktop v1 is complete when this works:

```text
ATLAS finds an opportunity.
↓
User reviews it.
↓
Atlas recommends an action.
↓
User tracks or dismisses it.
↓
Pipeline manages its progress.
↓
Ask Atlas explains when needed.
```

If this loop works, ATLAS Desktop v1 feels complete.

---

# 2. Workspace Readiness

# Command Center

## Must Have

* Atlas Focus list
* Compact Recommendation Cards
* New Opportunity Signals
* Upcoming Interviews
* Follow-Ups Due
* Pipeline Snapshot
* Low-emphasis System Health
* Context Panel support

Command Center must answer:

```text
What changed?
What matters?
What should I do next?
```

---

## Optional

* Trend previews
* Weekly summary
* Source performance
* Mini activity timeline

---

## Can Wait

* Full Intelligence summaries
* Long-term strategy
* Career trajectory
* Professional Graph views

---

# Radar

## Must Have

* Opportunity Signal Cards
* Search
* Filters
* Signal strength
* Watchlist / tracked visibility
* Selected card state
* Opportunity Context Panel
* Open Opportunity Detail action

Radar must answer:

```text
What was discovered?
```

---

## Optional

* Aggregate Signal Map
* Company watchlist groupings
* Saved views
* Advanced source filters

---

## Can Wait

* Full company intelligence workspace
* Market trend overlays
* Professional Graph relationship visualization

---

# Pipeline

## Must Have

* Attention Queue
* Progression Overview
* Active Opportunity Stream
* Opportunity Progression object
* State-based progression language
* Follow-up tracking
* Interview tracking
* Offer tracking
* Context Panel

Pipeline must answer:

```text
What is progressing?
What requires action?
What is stalled?
```

---

## Optional

* Historical outcome summaries
* Batch status updates
* Advanced filtering
* Weekly progression recap

---

## Can Wait

* Deep analytics
* Conversion-rate reporting
* Full decision history
* Multi-year outcome analysis

---

# Ask Atlas

## Must Have

* Contextual question entry
* Opportunity-aware answers
* Recommendation explanation
* Pipeline guidance
* Suggested prompts
* Return-to-workflow behavior

Ask Atlas must answer:

```text
Why?
What should I understand?
What should I consider?
```

---

## Optional

* Persistent investigation history
* Named Atlas Cases
* Saved answers
* Multi-turn research sessions

---

## Can Wait

* Full Atlas Case object system
* Investigation Briefs
* Career coaching workflows
* Long-term memory views

---

# 3. Opportunity Detail Surface Requirements

The Opportunity Detail Surface is the primary object surface for Desktop v1.

It is not a top-level workspace.

It opens from:

```text
Radar
Command Center
Pipeline
Ask Atlas
```

---

# Required Information

## Must Have

* Position title
* Company
* Location
* Work mode
* Compensation if available
* Opportunity summary
* Requirements
* Source
* Detection status
* Signal strength
* Current state if tracked
* Related recommendation if available

---

# Required Actions

## Primary

```text
Review / Track / Apply Preparation
```

The surface should not immediately behave like an external application launcher.

The user should evaluate first.

---

## Secondary

```text
Save
Track
Compare
Ignore
Open in Pipeline
Ask Atlas
```

---

# Relationship To Radar

Radar discovers the opportunity.

Opportunity Detail evaluates it.

---

# Relationship To Pipeline

Pipeline owns progress after the user tracks or applies.

---

# Relationship To Ask Atlas

Ask Atlas explains opportunity context.

The user should not need to re-explain what opportunity they mean.

---

# 4. Atlas Focus Requirements

Atlas Focus is required for Desktop v1.

Without Focus, Command Center becomes a dashboard.

---

# Definition

An Atlas Focus is:

```text
A prioritized area of attention identified by ATLAS.
```

---

# How Focuses Are Created

## From Signals

Example:

```text
Strong new opportunity detected.
```

---

## From Progressions

Example:

```text
Follow-up due today.
```

---

## From Recommendations

Example:

```text
Atlas recommends reviewing this role.
```

---

## From Calendar / Pipeline Events

Example:

```text
Interview tomorrow.
```

---

# How Focuses Are Displayed

Focuses appear primarily in:

```text
Command Center
```

and secondarily in:

```text
Pipeline
Context Panel
```

Each Focus must include:

* focus statement
* reason
* source object
* attention horizon
* next action
* resolution state

---

# How Focuses Are Resolved

A Focus can be:

```text
Completed
Deferred
Dismissed
Superseded
Expired
```

Resolved Focuses should archive, not disappear permanently.

---

# Relationship To Signals

Not every Signal becomes a Focus.

Only Signals requiring attention become Focuses.

---

# Relationship To Progressions

Progressions commonly create Focuses.

Examples:

```text
Interview scheduled
Follow-up overdue
Offer decision required
```

---

# Relationship To Recommendations

Recommendations suggest action.

Focuses prioritize attention.

A Focus may contain a Recommendation, but they are not the same object.

---

# 5. Recommendation System Requirements

Recommendations are required for Desktop v1.

They are the visible proof that Atlas interprets.

---

# Where Recommendations Appear

## Must Appear

* Command Center
* Opportunity Detail Surface
* Pipeline Context Panel
* Ask Atlas responses

---

## Optional

* Radar Context Panel
* Documents utility area
* Startup summary

---

# Recommendation Relationship To Focuses

Recommendation:

```text
What Atlas suggests.
```

Focus:

```text
What deserves attention.
```

Example:

```text
Focus:
Interview tomorrow.

Recommendation:
Review bridge project examples before the interview.
```

---

# Recommendation Relationship To Opportunities

Recommendations should attach directly to opportunities when relevant.

Example:

```text
Apply to Structural Engineer I
```

opens Opportunity Detail, not an external application immediately.

---

# Recommendation Relationship To Ask Atlas

Every Recommendation should support:

```text
Ask Atlas Why
```

Ask Atlas receives:

* recommendation
* reason
* source opportunity
* related progression
* available context

---

# 6. Desktop v1 vs Phase 2 vs Future Vision

# Desktop v1 — Must Have

## Workspaces

```text
Command Center
Radar
Pipeline
Ask Atlas
```

## Objects

```text
Opportunity Signal
Opportunity Progression
Recommendation
Atlas Focus
Opportunity Detail Surface
```

## Capabilities

```text
Daily awareness
Opportunity discovery
Opportunity review
Application tracking
Follow-up tracking
Interview tracking
Basic recommendations
Contextual Ask Atlas
```

---

# Phase 2 — Should Have

## Workspaces

```text
Intelligence
```

## Objects

```text
Atlas Perspective
Saved Ask Atlas history
Recommendation history
Decision history
```

## Capabilities

```text
Strategic weekly review
Career trajectory signals
Skill gap interpretation
Source effectiveness interpretation
Compensation observations
```

---

# Future Vision — Could Have

## Objects

```text
Atlas Case
Professional Graph
Perspective Brief
Investigation Brief
Career Strategy
```

## Capabilities

```text
Professional Graph visualization
Long-term career planning
Multi-year coaching
Advanced market intelligence
Career memory
Scenario planning
Commercial edition features
```

---

# 7. Recommended Implementation Sequence

## Step 1 — Desktop Shell

Build the container first.

Required:

* sidebar navigation
* persistent context model
* context panel
* shared visual system
* utility routing

Reason:

Every workspace depends on shell behavior.

---

## Step 2 — Opportunity Detail Surface

Build the primary object surface early.

Reason:

Radar, Pipeline, Recommendations, and Ask Atlas all converge here.

Without Opportunity Detail, the experience remains fragmented.

---

## Step 3 — Radar

Build discovery next.

Required:

* Opportunity Signal Cards
* filters
* search
* context panel
* open Opportunity Detail

Reason:

Radar proves ATLAS scans.

This is the product’s core differentiator.

---

## Step 4 — Pipeline

Build execution after discovery.

Required:

* Opportunity Progressions
* state tracking
* attention queue
* follow-ups
* interviews
* offers

Reason:

Discovery without progression is incomplete.

---

## Step 5 — Command Center

Build Command Center after Radar and Pipeline produce real objects.

Required:

* Focuses
* recommendations
* signals
* interviews
* follow-ups
* pipeline snapshot

Reason:

Command Center synthesizes objects. It should not be built before objects exist.

---

## Step 6 — Recommendations

Integrate recommendations across:

* Command Center
* Opportunity Detail
* Pipeline
* Ask Atlas

Reason:

Recommendations prove Atlas interprets.

---

## Step 7 — Ask Atlas

Build contextual Ask Atlas last in v1.

Reason:

Ask Atlas is most valuable when it has real objects to explain.

Minimum v1 Ask Atlas should be contextual, not general-purpose.

---

# Final Desktop v1 Product Definition

ATLAS Desktop Personal Edition v1 should deliver:

```text
Awareness
Discovery
Execution
Explanation
```

It should not yet attempt full:

```text
Interpretation
Investigation
Career Strategy
Professional Memory
```

Those belong to Phase 2 and beyond.

---

# Final Recommendation

The v1 build sequence should be:

```text
1. Desktop Shell
2. Opportunity Detail Surface
3. Radar
4. Pipeline
5. Command Center
6. Recommendations
7. Ask Atlas
```

This sequence protects the product from becoming a static dashboard.

It builds ATLAS from the object outward:

```text
Opportunity
↓
Signal
↓
Progression
↓
Focus
↓
Recommendation
↓
Explanation
```

That is the strongest path to a Desktop v1 that feels complete for personal daily use without drifting into the full future Career Intelligence Platform.
