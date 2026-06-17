# <a name="x262ab23db453f67320c07883dda851d57405872"></a>ATLAS Command Center Workspace Specification v1.0
Status: Canonical Workspace Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Command Center is the primary workspace of ATLAS.

It is the default landing experience.

It is the operational center of the platform.

The Command Center exists to answer three questions:

What changed?

What matters?

What should I do next?

-----
# <a name="core-philosophy"></a>Core Philosophy
The Command Center is not:

- a dashboard
- a report
- an analytics page
- a data summary

The Command Center is:

An operational awareness workspace.

Users should arrive, orient themselves, identify priorities, and determine next actions.

-----
# <a name="ownership"></a>Ownership
## <a name="the-command-center-owns"></a>The Command Center Owns
Awareness

Attention

Prioritization

Immediate Actions

Operational Status

Atlas Recommendations

-----
## <a name="the-command-center-does-not-own"></a>The Command Center Does Not Own
Opportunity Discovery

Application Management

Document Editing

Deep Analytics

Conversation

Those belong to:

- Radar
- Pipeline
- Documents
- Intelligence
- Ask Atlas
-----
# <a name="primary-questions"></a>Primary Questions
The workspace must answer:

What requires attention?

What changed since my last visit?

What opportunities deserve review?

What actions should happen next?

What risks exist?

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The hierarchy is fixed.

\```text id=“8b8n4w” Action Required

Atlas Recommendations

Interviews

Follow-Ups

Recent Signals

Pipeline Snapshot

System Health

\
\
This order is mandatory.\
\
\---\
\
\# Hierarchy Rationale\
\
Actions come first.\
\
Recommendations come second.\
\
Awareness comes third.\
\
Analytics come last.\
\
The Command Center is action-oriented.\
\
Not analysis-oriented.\
\
\---\
\
\# Layout Architecture\
\
The workspace is divided into three operational zones.\
\
\---\
\
\# Top Zone\
\
Purpose:\
\
Immediate attention.\
\
\---\
\
Contains:\
\
Action Queue\
\
Atlas Recommendations\
\
Critical Notifications\
\
Upcoming Interviews\
\
\---\
\
Question Answered:\
\
What requires action now?\
\
\---\
\
Priority:\
\
Highest\
\
\---\
\
Visual Weight:\
\
Highest\
\
\---\
\
\# Middle Zone\
\
Purpose:\
\
Situational awareness.\
\
\---\
\
Contains:\
\
Recent Signals\
\
Follow-Ups\
\
Tracked Opportunity Updates\
\
Recent Pipeline Changes\
\
\---\
\
Question Answered:\
\
What changed?\
\
\---\
\
Priority:\
\
Medium\
\
\---\
\
Visual Weight:\
\
Medium\
\
\---\
\
\# Lower Zone\
\
Purpose:\
\
Operational context.\
\
\---\
\
Contains:\
\
Pipeline Snapshot\
\
Source Health\
\
System Health\
\
Activity Trends\
\
\---\
\
Question Answered:\
\
How is the system performing?\
\
\---\
\
Priority:\
\
Lowest\
\
\---\
\
Visual Weight:\
\
Lowest\
\
\---\
\
\# Context Panel Relationship\
\
The Context Panel serves as the investigation layer.\
\
It never replaces the Command Center.\
\
\---\
\
\# Trigger Sources\
\
Recommendations\
\
Interviews\
\
Signals\
\
Follow-Ups\
\
Pipeline Events\
\
\---\
\
\# Context Panel Contents\
\
Expanded Details\
\
Referenced Objects\
\
Related Recommendations\
\
Ask Atlas Entry Point\
\
Timeline\
\
\---\
\
\# Behavior\
\
The Command Center remains visible.\
\
The Context Panel provides depth.\
\
\---\
\
\# Required Components\
\
\---\
\
\# Action Queue\
\
Placement\
\
Top Zone\
\
\---\
\
Purpose\
\
Highest-priority actions.\
\
\---\
\
Component\
\
Action Queue Card\
\
\---\
\
Maximum Visible\
\
5\
\
\---\
\
\# Atlas Recommendations\
\
Placement\
\
Top Zone\
\
\---\
\
Purpose\
\
Surface intelligence.\
\
\---\
\
Component\
\
Recommendation Card\
\
\---\
\
Maximum Visible\
\
3–5\
\
\---\
\
Governance Rule\
\
Only high-confidence recommendations appear.\
\
\---\
\
\# Interviews\
\
Placement\
\
Top Zone\
\
\---\
\
Purpose\
\
Upcoming commitments.\
\
\---\
\
Component\
\
Interview Card\
\
\---\
\
Sorting\
\
Nearest interview first.\
\
\---\
\
\# Follow-Ups\
\
Placement\
\
Middle Zone\
\
\---\
\
Purpose\
\
Pipeline momentum.\
\
\---\
\
Component\
\
Follow-Up Card\
\
\---\
\
Sorting\
\
Oldest due first.\
\
\---\
\
\# Recent Signals\
\
Placement\
\
Middle Zone\
\
\---\
\
Purpose\
\
Opportunity awareness.\
\
\---\
\
Component\
\
Opportunity Signal Card\
\
\---\
\
Governance Rule\
\
Only exceptional and strong signals appear.\
\
\---\
\
\# Pipeline Snapshot\
\
Placement\
\
Lower Zone\
\
\---\
\
Purpose\
\
Status overview.\
\
\---\
\
Component\
\
Pipeline Snapshot Card\
\
\---\
\
Contents\
\
Applications\
\
Interviews\
\
Offers\
\
Awaiting Response\
\
\---\
\
\# System Health\
\
Placement\
\
Lower Zone\
\
\---\
\
Purpose\
\
Platform operational awareness.\
\
\---\
\
Component\
\
System Health Card\
\
\---\
\
Contents\
\
Source Status\
\
Generation Status\
\
Monitoring Status\
\
\---\
\
\# Attention Model\
\
The Command Center uses a strict attention hierarchy.\
\
\---\
\
\## Level 1\
\
Action Required\
\
Interviews\
\
Deadlines\
\
Critical Follow-Ups\
\
\---\
\
\## Level 2\
\
Atlas Recommendations\
\
\---\
\
\## Level 3\
\
Recent Signals\
\
Tracked Opportunity Changes\
\
\---\
\
\## Level 4\
\
Pipeline Summary\
\
\---\
\
\## Level 5\
\
System Health\
\
Analytics\
\
\---\
\
Governance Rule\
\
No Level 5 element may visually compete with Level 1 elements.\
\
\---\
\
\# Daily Workflow\
\
Typical Daily Flow\
\
\```text id="4o8c9u"\
Open Command Center\
\
↓\
\
Review Action Queue\
\
↓\
\
Review Recommendations\
\
↓\
\
Review Interviews\
\
↓\
\
Review Follow-Ups\
\
↓\
\
Review New Signals\
\
↓\
\
Open Radar / Pipeline\
\
↓\
\
Execute Work

-----
# <a name="daily-goal"></a>Daily Goal
Determine:

What should I do today?

-----
# <a name="weekly-workflow"></a>Weekly Workflow
Typical Weekly Flow

\```text id=“p0rx1u” Open Command Center

↓

Review Pipeline Snapshot

↓

Review Recommendations

↓

Review Recent Signals

↓

Review Intelligence Workspace

↓

Review Career Direction

↓

Plan Following Week ```

-----
# <a name="weekly-goal"></a>Weekly Goal
Determine:

Am I moving forward?

-----
# <a name="atlas-placement"></a>Atlas Placement
Atlas appears in the Command Center primarily through Recommendation Cards.

Atlas does not dominate the workspace.

Atlas supports decision making.

The Command Center remains an ATLAS workspace.

Not an Atlas workspace.

-----
# <a name="ask-atlas-placement"></a>Ask Atlas Placement
Ask Atlas appears through:

Recommendation Cards

Context Panel

Interview Cards

Follow-Up Cards

Pipeline Events

-----
Governance Rule

Ask Atlas is always available.

It is never the primary focus of the Command Center.

-----
# <a name="empty-state-behavior"></a>Empty State Behavior
## <a name="no-actions"></a>No Actions
Message:

No actions currently require attention.

All systems nominal.

-----
## <a name="no-recommendations"></a>No Recommendations
Message:

Atlas has no high-confidence recommendations at this time.

Monitoring continues.

-----
## <a name="no-signals"></a>No Signals
Message:

No new opportunity signals detected.

Monitoring continues.

-----
Rule

Empty states should communicate awareness.

Not absence.

-----
# <a name="success-criteria"></a>Success Criteria
A user should be able to spend five minutes in the Command Center and leave with a clear understanding of:

What changed.

What matters.

What requires action.

What opportunities deserve attention.

What should happen next.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Aware

Organized

Prepared

In Control

Confident

-----
Users should not feel:

Overwhelmed

Behind

Judged

Managed

Distracted

-----
# <a name="workspace-definition"></a>Workspace Definition
The Command Center is the operational awareness layer of ATLAS.

It is the primary workspace of the platform and serves as the user’s daily point of orientation.

Its responsibility is not to manage opportunities, applications, or intelligence directly.

Its responsibility is to establish situational awareness and direct attention toward the most important next actions.

The Command Center succeeds when users can confidently answer:

What changed?

What matters?

What should I do next?
