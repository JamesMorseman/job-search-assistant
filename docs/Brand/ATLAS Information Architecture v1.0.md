# <a name="atlas-information-architecture-v1.0"></a>ATLAS Information Architecture v1.0
Status: Architecture Candidate\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>1. Purpose
This document defines the long-term information architecture of ATLAS.

The objective is to organize ATLAS around:

Career Intelligence

rather than

Feature Inventory

The architecture must reinforce:

ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

Every screen should support one stage of that process.

-----
# <a name="architectural-principles"></a>2. Architectural Principles
## <a name="principle-1"></a>Principle 1
Awareness Before Analysis

Users should immediately understand:

- what changed
- what matters
- what requires attention

before seeing metrics.

-----
## <a name="principle-2"></a>Principle 2
Workflow Before Features

Navigation should represent how users think.

Not how software was implemented.

-----
## <a name="principle-3"></a>Principle 3
Intelligence Is Cross-Cutting

Atlas should not be isolated inside one screen.

Recommendations should appear throughout ATLAS.

-----
## <a name="principle-4"></a>Principle 4
Conversation Is Optional

Ask Atlas should be available everywhere.

But it should never become mandatory.

-----
## <a name="principle-5"></a>Principle 5
Mission Control First

ATLAS is not a reporting tool.

ATLAS is an operational environment.

-----
# <a name="top-level-navigation"></a>3. Top-Level Navigation
## <a name="primary-navigation"></a>Primary Navigation
### <a name="command-center"></a>Command Center
### <a name="radar"></a>Radar
### <a name="pipeline"></a>Pipeline
### <a name="intelligence"></a>Intelligence
### <a name="ask-atlas"></a>Ask Atlas
-----
## <a name="secondary-navigation"></a>Secondary Navigation
### <a name="documents"></a>Documents
### <a name="companies"></a>Companies
### <a name="saved-views"></a>Saved Views
Future

-----
## <a name="utility-navigation"></a>Utility Navigation
### <a name="settings"></a>Settings
### <a name="integrations"></a>Integrations
### <a name="help"></a>Help
### <a name="feedback"></a>Feedback
-----
# <a name="navigation-map"></a>Navigation Map
ATLAS\
│\
├── Command Center\
├── Radar\
├── Pipeline\
├── Intelligence\
├── Ask Atlas\
│\
├── Documents\
├── Companies\
│\
└── Utilities\
`    `├── Settings\
`    `├── Integrations\
`    `├── Help\
`    `└── Feedback

-----
# <a name="primary-screen-definitions"></a>4. Primary Screen Definitions
-----
# <a name="command-center-1"></a>Command Center
## <a name="purpose-1"></a>Purpose
Operational awareness.

The Command Center answers:

What requires attention?

-----
## <a name="questions-answered"></a>Questions Answered
What changed today?

What requires action?

What is most important?

What should happen next?

-----
## <a name="major-components"></a>Major Components
Action Queue

Follow-Ups Due

Upcoming Interviews

Application Deadlines

Atlas Recommendations

Recent Signals

Pipeline Snapshot

-----
## <a name="supported-actions"></a>Supported Actions
Review

Follow Up

Apply

Dismiss

Open Recommendation

Launch Ask Atlas

-----
## <a name="information-boundary"></a>Information Boundary
Command Center does not manage records.

Command Center manages attention.

-----
# <a name="radar-1"></a>Radar
## <a name="purpose-2"></a>Purpose
Discovery and monitoring.

Radar answers:

What opportunities exist?

-----
## <a name="questions-answered-1"></a>Questions Answered
What is new?

What changed?

What opportunities match?

What companies are emerging?

-----
## <a name="major-components-1"></a>Major Components
Opportunity Feed

Watchlists

Company Tracking

Source Monitoring

Signal Detection

Search

Filters

-----
## <a name="supported-actions-1"></a>Supported Actions
Save

Ignore

Track

Review

Investigate

-----
## <a name="information-boundary-1"></a>Information Boundary
Radar discovers opportunities.

Radar does not manage applications.

-----
# <a name="pipeline-1"></a>Pipeline
## <a name="purpose-3"></a>Purpose
Application operations.

Pipeline answers:

What is happening with active opportunities?

-----
## <a name="questions-answered-2"></a>Questions Answered
Where is each application?

What requires follow-up?

Which interviews exist?

Which opportunities are progressing?

-----
## <a name="major-components-2"></a>Major Components
Application Tracker

Interview Tracker

Offer Tracker

Timeline View

Status Management

Pipeline Analytics

-----
## <a name="supported-actions-2"></a>Supported Actions
Update Status

Schedule Follow-Up

Record Outcome

Attach Documents

Launch Ask Atlas

-----
## <a name="information-boundary-2"></a>Information Boundary
Pipeline manages active opportunities.

Pipeline does not discover opportunities.

-----
# <a name="intelligence-1"></a>Intelligence
## <a name="purpose-4"></a>Purpose
Interpretation and recommendation.

Intelligence answers:

What should I do next?

-----
## <a name="questions-answered-3"></a>Questions Answered
Which opportunities matter most?

What patterns exist?

What skills should improve?

What recommendations exist?

What trends are emerging?

-----
## <a name="major-components-3"></a>Major Components
Recommendation Center

Career Insights

Trajectory Analysis

Skill Analysis

Market Intelligence

Outcome Analytics

Decision History

-----
## <a name="supported-actions-3"></a>Supported Actions
Accept Recommendation

Dismiss Recommendation

Explore Insight

Generate Plan

Launch Ask Atlas

-----
## <a name="information-boundary-3"></a>Information Boundary
Intelligence generates conclusions.

It does not execute workflows.

-----
# <a name="ask-atlas-1"></a>Ask Atlas
## <a name="purpose-5"></a>Purpose
Conversation and explanation.

Ask Atlas answers:

Why?

-----
## <a name="questions-answered-4"></a>Questions Answered
Why is this recommended?

What should I prioritize?

How do these opportunities compare?

What am I missing?

What should happen next?

-----
## <a name="major-components-4"></a>Major Components
Conversation Thread

Context Viewer

Suggested Prompts

Referenced Opportunities

Referenced Recommendations

Atlas Memory

-----
## <a name="supported-actions-4"></a>Supported Actions
Ask

Compare

Explain

Analyze

Plan

Summarize

-----
## <a name="information-boundary-4"></a>Information Boundary
Ask Atlas communicates intelligence.

It does not replace primary workflows.

-----
# <a name="secondary-screens"></a>5. Secondary Screens
-----
# <a name="documents-1"></a>Documents
Purpose:

Manage generated assets.

Contents:

- Resumes
- Cover Letters
- Templates
- Generated Content
-----
# <a name="companies-1"></a>Companies
Purpose:

Maintain company intelligence.

Contents:

- Firm Profiles
- Watchlists
- Historical Activity
- Relationships
-----
# <a name="atlas-placement-model"></a>6. Atlas Placement Model
## <a name="principle"></a>Principle
Atlas is everywhere.

Atlas is not a destination.

-----
# <a name="embedded-placement"></a>Embedded Placement
Command Center

Recommendations

-----
Radar

Opportunity Scoring

-----
Pipeline

Follow-Up Guidance

-----
Intelligence

Primary Surface

-----
Ask Atlas

Conversation Layer

-----
# <a name="governance-rule"></a>Governance Rule
Atlas recommendations should appear throughout the application.

The Intelligence screen serves as the master recommendation center.

-----
# <a name="ask-atlas-placement-model"></a>7. Ask Atlas Placement Model
## <a name="persistent-entry-point"></a>Persistent Entry Point
Always available.

All major screens.

-----
## <a name="entry-methods"></a>Entry Methods
Sidebar

Context Panel

Keyboard Shortcut

Recommendation Actions

Opportunity Detail Views

Pipeline Views

-----
## <a name="philosophy"></a>Philosophy
Ask Atlas should feel omnipresent.

Not isolated.

-----
# <a name="daily-workflow-model"></a>8. Daily Workflow Model
## <a name="active-job-search"></a>Active Job Search
Command Center

↓

Radar

↓

Review Opportunities

↓

Pipeline

↓

Track Progress

↓

Atlas Recommendations

↓

Ask Atlas

↓

Next Actions

-----
# <a name="daily-goal"></a>Daily Goal
Determine:

What requires action today?

-----
# <a name="weekly-workflow-model"></a>9. Weekly Workflow Model
## <a name="weekly-review"></a>Weekly Review
Command Center

↓

Pipeline Review

↓

Intelligence Review

↓

Career Insights

↓

Recommendation Acceptance

↓

Planning

-----
# <a name="weekly-goal"></a>Weekly Goal
Determine:

Am I progressing?

-----
# <a name="passive-monitoring-workflow"></a>10. Passive Monitoring Workflow
## <a name="employed-user"></a>Employed User
Command Center

↓

Radar

↓

Intelligence

↓

Ask Atlas

-----
Pipeline usage becomes minimal.

Radar and Intelligence become dominant.

-----
# <a name="goal"></a>Goal
Maintain situational awareness.

-----
# <a name="future-desktop-structure"></a>11. Future Desktop Structure
## <a name="phase-1"></a>Phase 1
Application Intelligence

Radar

Pipeline

Documents

-----
## <a name="phase-2"></a>Phase 2
Career Intelligence

Command Center

Radar

Pipeline

Intelligence

Ask Atlas

-----
## <a name="phase-3"></a>Phase 3
Professional Intelligence

Expanded Intelligence

Career Forecasting

Market Intelligence

Decision Modeling

-----
## <a name="phase-4"></a>Phase 4
Career Mission Control

Full ATLAS ecosystem

Atlas as persistent intelligence layer

Ask Atlas as conversational operating layer

-----
# <a name="information-ownership-matrix"></a>12. Information Ownership Matrix

|Screen|Owns Discovery|Owns Tracking|Owns Intelligence|Owns Conversation|
| :- | :- | :- | :- | :- |
|Command Center|No|No|Surface Only|Launch Only|
|Radar|Yes|No|Limited|Launch Only|
|Pipeline|No|Yes|Limited|Launch Only|
|Intelligence|No|No|Yes|Launch Only|
|Ask Atlas|No|No|Explain Only|Yes|

-----
# <a name="final-architecture-statement"></a>Final Architecture Statement
ATLAS is organized around awareness, action, intelligence, and communication.

Command Center answers:

What requires attention?

Radar answers:

What opportunities exist?

Pipeline answers:

What is happening?

Intelligence answers:

What should I do next?

Ask Atlas answers:

Why?

Together these screens implement the ATLAS narrative:

ATLAS scans.

Atlas interprets.

Ask Atlas communicates.
