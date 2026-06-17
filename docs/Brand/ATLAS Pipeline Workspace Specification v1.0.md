# <a name="xe2ee58ce5c1ca94ea7b84be4e9c069fc635dbd5"></a>ATLAS Pipeline Workspace Specification v1.0
Status: Canonical Workspace Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Pipeline Workspace is the operational execution layer of ATLAS.

If Radar answers:

“What opportunities exist?”

and Intelligence answers:

“What should I do next?”

then Pipeline answers:

“What is happening right now?”

Pipeline is where opportunities become outcomes.

-----
# <a name="core-narrative"></a>Core Narrative
ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

Pipeline executes.

While not part of the public narrative hierarchy, Pipeline is where users convert awareness and intelligence into career progress.

-----
# <a name="ownership"></a>Ownership
## <a name="pipeline-owns"></a>Pipeline Owns
Applications

Status Tracking

Interviews

Offers

Follow-Ups

Pipeline Progression

Application History

Workflow Execution

-----
## <a name="pipeline-does-not-own"></a>Pipeline Does Not Own
Opportunity Discovery

Recommendation Generation

Career Intelligence

Document Authoring

Deep Analytics

Conversation

Those belong to:

- Radar
- Intelligence
- Documents
- Ask Atlas
-----
# <a name="core-questions"></a>Core Questions
The Pipeline Workspace must answer:

Where are my applications?

What requires follow-up?

Which opportunities are progressing?

What interviews are upcoming?

What offers are active?

What is at risk?

What should happen next?

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The hierarchy is fixed.

Follow-Ups Due\
\
Interviews\
\
Offers\
\
Awaiting Response\
\
Active Applications\
\
Pipeline Timeline\
\
Historical Outcomes

-----
# <a name="hierarchy-rationale"></a>Hierarchy Rationale
Pipeline is action-oriented.

Not reporting-oriented.

Not analytics-oriented.

The first thing users should see is:

What requires intervention?

not

How many applications exist?

-----
# <a name="layout-architecture"></a>Layout Architecture
The Pipeline Workspace consists of four regions.

-----
# <a name="primary-workspace"></a>Primary Workspace
Purpose:

Operational management.

-----
Contents:

Application Cards

Pipeline Table

Status Views

Offer Views

Interview Views

-----
Question Answered:

What is happening?

-----
Priority:

Highest

-----
# <a name="timeline-region"></a>Timeline Region
Purpose:

Chronological understanding.

-----
Contents:

Application Events

Interview Events

Follow-Up Events

Offer Events

Status Changes

-----
Question Answered:

How did we get here?

-----
Priority:

Medium

-----
# <a name="status-region"></a>Status Region
Purpose:

Pipeline health.

-----
Contents:

Status Counts

Risk Indicators

Upcoming Events

Response Activity

-----
Question Answered:

Where are bottlenecks?

-----
Priority:

Medium

-----
# <a name="context-panel"></a>Context Panel
Purpose:

Investigation and decision support.

-----
Contents:

Application Details

Interview Details

Offer Details

Atlas Recommendations

Ask Atlas Context

Documents

Timeline History

-----
Question Answered:

What should I know about this specific item?

-----
Priority:

Supporting

-----
# <a name="pipeline-state-model"></a>Pipeline State Model
All applications must exist in one and only one primary state.

-----
# <a name="applied"></a>Applied
Definition:

Application submitted.

No response received.

-----
Question:

Was the application successfully sent?

-----
# <a name="awaiting-response"></a>Awaiting Response
Definition:

Waiting for employer action.

-----
Question:

How long has this opportunity been idle?

-----
# <a name="interview"></a>Interview
Definition:

Interview process active.

-----
Question:

What preparation is required?

-----
# <a name="offer"></a>Offer
Definition:

Offer received and decision pending.

-----
Question:

What decision should be made?

-----
# <a name="closed"></a>Closed
Definition:

Pipeline completed successfully.

-----
Examples:

Accepted Offer

Position Filled

Process Completed

-----
# <a name="rejected"></a>Rejected
Definition:

Employer declined application.

-----
Question:

Should any lessons be captured?

-----
# <a name="withdrawn"></a>Withdrawn
Definition:

User exited process voluntarily.

-----
Question:

Why was the opportunity abandoned?

-----
# <a name="pipeline-object-model"></a>Pipeline Object Model
-----
# <a name="application-card"></a>Application Card
Purpose:

Primary operational object.

-----
Represents:

Single application.

-----
Contains:

Position

Company

Current Status

Applied Date

Latest Event

Next Action

-----
Primary Action:

Open Application

-----
# <a name="interview-card"></a>Interview Card
Purpose:

Interview management.

-----
Contains:

Company

Position

Interview Date

Interview Type

Preparation Status

-----
Primary Action:

Prepare Interview

-----
Relationship:

Attached to Application.

-----
# <a name="follow-up-card"></a>Follow-Up Card
Purpose:

Maintain momentum.

-----
Contains:

Application

Company

Follow-Up Date

Reason

-----
Primary Action:

Complete Follow-Up

-----
Relationship:

Attached to Application.

-----
# <a name="offer-card"></a>Offer Card
Purpose:

Decision management.

-----
Contains:

Company

Position

Offer Status

Decision Deadline

-----
Primary Action:

Review Offer

-----
Relationship:

Attached to Application.

-----
# <a name="pipeline-relationships"></a>Pipeline Relationships
Opportunity\
\
↓\
\
Application\
\
↓\
\
Interview\
\
↓\
\
Offer\
\
↓\
\
Outcome

Pipeline manages everything after Application.

-----
# <a name="atlas-integration"></a>Atlas Integration
Atlas appears as a supporting intelligence layer.

Atlas does not dominate Pipeline.

-----
# <a name="recommendation-types"></a>Recommendation Types
Follow-Up Recommended

Interview Preparation Recommended

Response Risk Detected

Offer Evaluation Recommended

Pipeline Momentum Risk

-----
# <a name="placement"></a>Placement
Application Detail Surface

Context Panel

Recommendation Region

Ask Atlas Launch Points

-----
# <a name="governance-rule"></a>Governance Rule
Pipeline recommendations must be operational.

Not strategic.

Strategic recommendations belong in Intelligence.

-----
# <a name="ask-atlas-integration"></a>Ask Atlas Integration
Ask Atlas exists as contextual guidance.

-----
# <a name="entry-points"></a>Entry Points
Application Card

Interview Card

Offer Card

Timeline Events

Recommendation Cards

Context Panel

-----
# <a name="example-questions"></a>Example Questions
Why has this application stalled?

What should I prepare for this interview?

How does this offer compare to my alternatives?

Should I follow up now?

-----
# <a name="exit-behavior"></a>Exit Behavior
Return to originating pipeline object.

Preserve context.

No state loss.

-----
# <a name="pipeline-attention-model"></a>Pipeline Attention Model
Pipeline uses four attention levels.

-----
## <a name="level-1"></a>Level 1
Follow-Ups Due

Upcoming Interviews

Offer Deadlines

-----
## <a name="level-2"></a>Level 2
Applications Requiring Review

Atlas Operational Recommendations

-----
## <a name="level-3"></a>Level 3
Awaiting Response

Pipeline Progress

-----
## <a name="level-4"></a>Level 4
Historical Outcomes

Archive Data

-----
Governance Rule

Historical information must never compete with active opportunities.

-----
# <a name="daily-workflow"></a>Daily Workflow
Typical Daily Flow

Command Center\
\
↓\
\
Pipeline\
\
↓\
\
Review Follow-Ups\
\
↓\
\
Review Interviews\
\
↓\
\
Review Offers\
\
↓\
\
Update Statuses\
\
↓\
\
Complete Actions\
\
↓\
\
Return to Command Center

-----
# <a name="daily-goal"></a>Daily Goal
Maintain momentum.

Prevent opportunity decay.

Advance active opportunities.

-----
# <a name="weekly-workflow"></a>Weekly Workflow
Typical Weekly Flow

Pipeline\
\
↓\
\
Review Active Applications\
\
↓\
\
Review Response Rates\
\
↓\
\
Review Rejections\
\
↓\
\
Review Offers\
\
↓\
\
Review Atlas Guidance\
\
↓\
\
Adjust Strategy

-----
# <a name="weekly-goal"></a>Weekly Goal
Evaluate progression.

Identify bottlenecks.

Improve outcomes.

-----
# <a name="empty-state-behavior"></a>Empty State Behavior
## <a name="no-applications"></a>No Applications
Message:

No active applications in the pipeline.

Explore opportunities in Radar.

-----
## <a name="no-interviews"></a>No Interviews
Message:

No interviews currently scheduled.

Pipeline monitoring continues.

-----
## <a name="no-offers"></a>No Offers
Message:

No active offers.

Pipeline remains active.

-----
Rule:

Pipeline empty states should redirect attention toward opportunity creation.

-----
# <a name="success-criteria"></a>Success Criteria
A user should be able to spend five minutes in Pipeline and understand:

What applications are active.

What requires follow-up.

What interviews are upcoming.

What offers require decisions.

What opportunities are at risk.

What actions should happen next.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Organized

In Control

Prepared

Proactive

Confident

-----
Users should not feel:

Overwhelmed

Behind

Lost

Punished

Judged

-----
# <a name="workspace-definition"></a>Workspace Definition
The Pipeline Workspace is the operational execution environment of ATLAS.

It owns the lifecycle of active opportunities after application submission and serves as the system of record for interviews, offers, follow-ups, and outcomes.

Its purpose is not discovery, intelligence, or conversation.

Its purpose is progression.

The Pipeline Workspace succeeds when users can confidently answer:

What is happening?

What is at risk?

What should I do next?

and can move active opportunities toward meaningful outcomes with minimal friction.
