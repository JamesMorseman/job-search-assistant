# <a name="xd3fc8942e032a571859f3d7061fbc8157acaacd"></a>ATLAS Motion & Interaction Specification v1.0
Status: Implementation-Grade Design Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>1. Purpose
This document defines the official motion and interaction language for ATLAS.

Motion is not decorative.

Motion communicates:

- awareness
- state
- intelligence
- attention
- transition

Every motion behavior must reinforce:

ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

-----
# <a name="motion-philosophy"></a>2. Motion Philosophy
## <a name="core-principles"></a>Core Principles
ATLAS should feel:

Calm

Deliberate

Precise

Operational

Professional

-----
## <a name="emotional-goal"></a>Emotional Goal
The user should feel:

“In control.”

Not:

“Stimulated.”

-----
## <a name="motion-personality"></a>Motion Personality
Reference Concepts:

- Mission Control
- Air Traffic Control
- Professional Monitoring Systems
- Modern Intelligence Platforms

Not:

- Gaming UI
- Social Media UI
- Cyberpunk UI
- Consumer Entertainment UI
-----
# <a name="motion-rules"></a>Motion Rules
Motion must:

- communicate purpose
- reinforce awareness
- reveal state changes
- guide attention

Motion must never:

- distract
- celebrate excessively
- create urgency without cause
-----
# <a name="timing-standards"></a>Timing Standards
Fast

100ms–150ms

Micro-interactions

-----
Standard

200ms–300ms

Primary transitions

-----
Slow

400ms–600ms

Major state transitions

-----
Maximum

800ms

No animation may exceed 800ms.

-----
# <a name="radar-motion-system"></a>3. Radar Motion System
Radar motion is the primary motion language of ATLAS.

-----
## <a name="startup-sweep"></a>Startup Sweep
Purpose:

System activation

-----
Behavior

Radar sweep begins from center.

Single sweep rotates.

Signal points gradually appear.

Sweep slows and settles.

Application opens.

-----
Duration

1200ms total

Single execution

-----
Emotional Goal

Situational awareness being established.

-----
## <a name="active-monitoring-sweep"></a>Active Monitoring Sweep
Purpose:

Background awareness

-----
Behavior

Very subtle sweep.

Low opacity.

Slow movement.

No continuous looping visible to the user.

Periodic refresh only.

-----
Frequency

Every 15–30 seconds

Context dependent

-----
Rule

Monitoring should feel alive.

Not animated.

-----
## <a name="signal-acquisition"></a>Signal Acquisition
Purpose:

New opportunity discovered.

-----
Behavior

Signal point appears.

Small expansion ring.

Ring dissipates.

Signal remains.

-----
Duration

400ms

-----
Meaning

Something new was detected.

-----
## <a name="opportunity-detection"></a>Opportunity Detection
Purpose:

Important opportunity discovered.

-----
Behavior

Signal acquisition

↓

Brief pulse

↓

Highlight state

-----
Duration

500ms

-----
Visual Weight

Moderate

Never flashing.

-----
## <a name="recommendation-appearance"></a>Recommendation Appearance
Purpose:

Atlas recommendation generated.

-----
Behavior

Signal detected

↓

Card materializes

↓

Subtle cyan accent activates

-----
Duration

300ms

-----
Meaning

Information became intelligence.

-----
# <a name="notification-motion-system"></a>4. Notification Motion System
Notifications represent detected events.

Not messages.

-----
# <a name="informational"></a>Informational
Examples

Source Updated

Application Viewed

Data Refreshed

-----
Motion

Fade + slight rise

-----
Duration

200ms

-----
Visual Weight

Low

-----
# <a name="recommendation"></a>Recommendation
Examples

Review Position

Apply to Opportunity

Resume Update Suggested

-----
Motion

Signal pulse

↓

Card reveal

-----
Duration

300ms

-----
Visual Weight

Medium

-----
# <a name="action-required"></a>Action Required
Examples

Follow-Up Due

Interview Approaching

Deadline Near

-----
Motion

Signal pulse

↓

Amber accent

↓

Panel reveal

-----
Duration

350ms

-----
Visual Weight

High

-----
# <a name="critical"></a>Critical
Examples

Submission Failure

Interview Conflict

Opportunity Closing

-----
Motion

Immediate appearance

↓

Single emphasis pulse

↓

Static state

-----
Duration

250ms

-----
Visual Weight

Highest

-----
Governance Rule

Critical notifications do not animate repeatedly.

Attention should come from severity.

Not motion.

-----
# <a name="atlas-atlas-ask-atlas-transition-system"></a>5. ATLAS → Atlas → Ask Atlas Transition System
This is the most important transition family.

-----
# <a name="concept"></a>Concept
ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

Motion should visually communicate this progression.

-----
# <a name="stage-1"></a>Stage 1
ATLAS

Visual Language

Radar

Grid

Detection

-----
# <a name="stage-2"></a>Stage 2
Atlas

Visual Language

Signal interpretation

Connections

Intelligence overlays

-----
# <a name="stage-3"></a>Stage 3
Ask Atlas

Visual Language

Waveforms

Conversation

Signal exchange

-----
# <a name="transition-pattern"></a>Transition Pattern
Radar sweep

↓

Signal acquisition

↓

Waveform emergence

↓

Conversation surface

-----
Duration

400–500ms

-----
Emotional Goal

The user should feel:

“I am moving from information to understanding.”

Not:

“I opened a chat window.”

-----
# <a name="ask-atlas-launch"></a>Ask Atlas Launch
Launch Sources

Recommendation

Opportunity

Application

Intelligence Panel

Global Shortcut

-----
Behavior

Context panel expands.

Waveform appears.

Conversation loads.

Context is preserved.

-----
# <a name="ask-atlas-exit"></a>Ask Atlas Exit
Behavior

Waveform recedes.

Context retained.

User returns to prior workflow.

-----
Rule

Ask Atlas should feel integrated.

Not separate.

-----
# <a name="context-panel-motion"></a>6. Context Panel Motion
## <a name="open"></a>Open
Slide from right.

Fade simultaneously.

-----
Duration

250ms

-----
## <a name="close"></a>Close
Fade

↓

Slide away

-----
Duration

200ms

-----
## <a name="expand"></a>Expand
Width grows.

Content remains stable.

-----
Duration

250ms

-----
## <a name="collapse"></a>Collapse
Width reduces.

No content reflow outside panel.

-----
Duration

250ms

-----
## <a name="context-updates"></a>Context Updates
Content crossfades.

Never reload abruptly.

-----
Duration

150ms

-----
Rule

Context changes should feel continuous.

Not disruptive.

-----
# <a name="loading-state-system"></a>7. Loading State System
Generic spinners are prohibited.

-----
# <a name="scan-animation"></a>Scan Animation
Purpose

Searching

Monitoring

Discovery

-----
Behavior

Radar sweep

↓

No signal

↓

Repeat

-----
Meaning

System is scanning.

-----
# <a name="acquisition-animation"></a>Acquisition Animation
Purpose

Fetching results

-----
Behavior

Radar sweep

↓

Signal appears

↓

Result loads

-----
Meaning

System found information.

-----
# <a name="generation-animation"></a>Generation Animation
Purpose

Resume generation

Analysis

Document creation

-----
Behavior

Signal fragments converge

↓

Single signal forms

↓

Output appears

-----
Meaning

Information becoming output.

-----
# <a name="recommendation-loading"></a>Recommendation Loading
Purpose

Atlas thinking

-----
Behavior

Signal network forms

↓

Connections activate

↓

Recommendation appears

-----
Meaning

Information becoming intelligence.

-----
# <a name="hover-focus-states"></a>8. Hover & Focus States
## <a name="hover"></a>Hover
Duration

100ms

-----
Behavior

Elevation increase

Minor brightness shift

-----
Rule

No dramatic scaling.

-----
## <a name="focus"></a>Focus
Atlas Blue outline

-----
Duration

100ms

-----
Rule

Focus always visible.

-----
# <a name="motion-accessibility"></a>9. Motion Accessibility
## <a name="reduced-motion-mode"></a>Reduced Motion Mode
Required.

-----
Behavior Changes

No radar sweeps

No waveform animations

No sliding panels

No acquisition effects

-----
Replacement

Fade only

100–150ms

-----
## <a name="motion-reduction-compliance"></a>Motion Reduction Compliance
All major motion systems must respect OS-level motion preferences.

-----
## <a name="flashing"></a>Flashing
Prohibited.

-----
## <a name="continuous-motion"></a>Continuous Motion
Minimized.

-----
## <a name="animation-frequency"></a>Animation Frequency
No recurring motion more frequent than once every 10 seconds.

-----
# <a name="motion-ownership-matrix"></a>10. Motion Ownership Matrix

|Motion Type|Owner|
| :- | :- |
|Radar Sweep|ATLAS|
|Signal Acquisition|ATLAS|
|Recommendation Reveal|Atlas|
|Intelligence Overlay|Atlas|
|Waveform Activity|Ask Atlas|
|Conversation Transition|Ask Atlas|
|Notification Motion|Shared|
|Context Panel Motion|Platform|

-----
# <a name="success-criteria"></a>11. Success Criteria
The motion system succeeds when users perceive:

ATLAS is aware.

Atlas is thinking.

Ask Atlas is communicating.

Motion should make the platform feel alive without ever making it feel animated.

The user should experience a calm, continuously aware professional intelligence environment rather than a traditional dashboard or consumer application.
