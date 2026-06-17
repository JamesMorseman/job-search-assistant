# ATLAS Pipeline Workspace v5 Reference

**Workspace:** Pipeline  
**Owner:** Sara — Visual Design  
**Authority:** Project Master (Ash)  
**Status:** Reference Candidate / Near Freeze  
**Version:** v5

---

# Purpose

Pipeline is the operational workspace of ATLAS.

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
What is progressing?

What requires action?

What decision comes next?
```

Pipeline is not a Kanban board.

Pipeline is not an ATS.

Pipeline is not a CRM.

Pipeline is not a task manager.

Pipeline exists to provide operational oversight of opportunity progression.

---

# Accepted Design Direction

Pipeline v5 adopts the Hybrid Operational Flow model.

Primary hierarchy:

```text
Attention
↓
Progress
↓
History
```

The workspace prioritizes:

1. immediate actions
2. active opportunity movement
3. progression awareness

without becoming workflow software.

---

# Workspace Structure

## Zone 1 — Attention Queue

Purpose:

```text
What requires action now?
```

Examples:

* Interview Tomorrow
* Follow-Up Due Today
* Offer Requires Decision
* Acknowledgement Pending
* No Response

Design principles:

* highest visual priority
* operationally focused
* action-oriented language
* urgency visible at a glance

The queue is intended to function as the operational heart of Pipeline.

---

## Zone 2 — Pipeline Overview

Purpose:

```text
Where is the pipeline currently distributed?
```

Displays:

* Detected
* Saved
* Reviewing
* Selected
* Applied
* Acknowledged
* Screen
* Offer
* Closed

This is not a Kanban board.

This is not a workflow editor.

It is a monitored progression system.

Users should understand pipeline shape within seconds.

---

## Zone 3 — Active Opportunity Stream

Purpose:

```text
What is actively moving?
```

Examples:

* Interview Scheduled
* Application Acknowledged
* Moved to Screen
* Offer Received

The stream functions as a real-time operational feed.

Movement is emphasized over storage.

The workspace should feel alive.

---

## Zone 4 — Opportunity Context Panel

Purpose:

```text
What does this opportunity require?
```

Provides:

* opportunity context
* next step
* progression status
* Atlas recommendation
* Ask Atlas entry point

Users should not need to leave Pipeline to understand opportunity state.

---

# Visual Language

Radar uses:

```text
Scanning
Detection
Signal Discovery
```

Pipeline uses:

```text
Movement
Advancement
Progression
Attention
```

Visual emphasis shifts from:

```text
Signal
```

to:

```text
Trajectory
```

and:

```text
Operational Readiness
```

---

# Progression Representation Rule

Pipeline does not use completion bars.

Pipeline does not imply linear completion percentages.

Avoid:

```text
Stage 7 of 10
```

because opportunity workflows are not guaranteed to reach later states.

Preferred:

```text
Current State: Interview
Current State: Applied
Current State: Offer
```

The goal is state awareness rather than completion tracking.

---

# Attention Queue Priority System

Approved priority levels:

### Critical

Examples:

* Interview Tomorrow

Visual treatment:

* strongest urgency
* highest attention weight

---

### Follow-Up Due

Examples:

* Follow-Up Due Today

Visual treatment:

* action-oriented
* operational reminder

---

### Decision Required

Examples:

* Offer Requires Decision

Visual treatment:

* decision emphasis
* user action required

---

### Time Sensitive

Examples:

* Acknowledgement Pending

Visual treatment:

* moderate urgency

---

### At Risk

Examples:

* No Response

Visual treatment:

* stalled opportunity indicator

---

# Mission Control Alignment

Pipeline should feel like:

```text
Mission Control
```

not:

```text
Spreadsheet
```

not:

```text
CRM
```

not:

```text
Kanban
```

not:

```text
Applicant Tracking System
```

Users should feel:

```text
These opportunities are progressing.

Some require attention.

Some are stalled.

Some are accelerating.

I understand the operational state of my search.
```

---

# Remaining Observations

Pipeline v5 resolves the largest architectural concern identified in v4:

Removed:

```text
Stage X of Y
```

Added:

```text
Current State
```

This improves semantic accuracy and avoids implying deterministic progression.

One minor refinement remains under consideration:

* selected interview states may still carry slightly more red emphasis than necessary

This is not currently considered blocking.

---

# Freeze Assessment

Status:

```text
Reference Candidate
```

Confidence:

```text
High
```

Recommended next action:

```text
Archive as Pipeline v5 Reference Candidate

Move Sara to Intelligence Workspace exploration
```

---

# Narrative Alignment

ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

Pipeline executes.
