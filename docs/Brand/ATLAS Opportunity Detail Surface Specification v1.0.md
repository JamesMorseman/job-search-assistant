# <a name="x11291394e58e73f44868bdc5f6cf112417ec37a"></a>ATLAS Opportunity Detail Surface Specification v1.0
Status: Canonical Workspace Surface Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Opportunity Detail Surface is the primary evaluation workspace for individual opportunities.

It is reached when a user selects:

Review Opportunity

from an Opportunity Signal Card.

-----
# <a name="core-narrative"></a>Core Narrative
ATLAS scans.

↓

Opportunity discovered.

↓

User investigates.

↓

Atlas assists interpretation.

↓

User decides.

The Opportunity Detail Surface exists between discovery and action.

It is intentionally positioned before:

- application submission
- recommendation acceptance
- pipeline management

Its purpose is evaluation.

-----
# <a name="ownership"></a>Ownership
## <a name="the-opportunity-detail-surface-owns"></a>The Opportunity Detail Surface Owns
Opportunity Evaluation

Opportunity Investigation

Position Review

Company Review Entry

Opportunity Comparison Entry

Opportunity Context

Application Initiation

-----
## <a name="x590df817c279cc778f77c43cae5a95830ba3658"></a>The Opportunity Detail Surface Does Not Own
Discovery

Application Tracking

Recommendation Management

Conversation

Career Strategy

Those belong to:

- Radar
- Pipeline
- Intelligence
- Ask Atlas
-----
# <a name="core-questions"></a>Core Questions
The Opportunity Detail Surface must answer:

What is this opportunity?

Who is offering it?

Why might it matter?

What are the requirements?

What are the risks?

Should I pursue it?

What should I do next?

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The hierarchy is fixed.

\```text id=“v2l6tr” Position

Company

Opportunity Summary

Requirements

Compensation & Logistics

Atlas Context

Related Opportunities

Actions

\
\---\
\
\# Hierarchy Rationale\
\
The opportunity itself remains primary.\
\
Atlas exists to support evaluation.\
\
Atlas must never dominate the opportunity.\
\
\---\
\
\# Layout Architecture\
\
The Opportunity Detail Surface consists of three regions.\
\
\---\
\
\# Main Content Region\
\
Purpose:\
\
Opportunity evaluation.\
\
\---\
\
Visual Priority:\
\
Highest.\
\
\---\
\
Contains:\
\
Position Overview\
\
Opportunity Summary\
\
Responsibilities\
\
Requirements\
\
Qualifications\
\
Compensation\
\
Benefits\
\
Location\
\
Work Arrangement\
\
Source Information\
\
\---\
\
Question Answered:\
\
What is this opportunity?\
\
\---\
\
\# Context Panel\
\
Purpose:\
\
Supporting context.\
\
\---\
\
Visual Priority:\
\
Secondary.\
\
\---\
\
Contains:\
\
Company Intelligence\
\
Related Opportunities\
\
Atlas Context\
\
Activity History\
\
Notes\
\
Watchlist Status\
\
\---\
\
Question Answered:\
\
What should I know beyond the job posting?\
\
\---\
\
\# Action Region\
\
Purpose:\
\
Decision making.\
\
\---\
\
Visual Priority:\
\
Persistent.\
\
\---\
\
Contains:\
\
Save\
\
Track\
\
Compare\
\
Apply\
\
Investigate Company\
\
Ask Atlas\
\
\---\
\
Question Answered:\
\
What can I do next?\
\
\---\
\
\# Main Content Structure\
\
\## Position Header\
\
Contains:\
\
Position Title\
\
Company\
\
Location\
\
Work Arrangement\
\
Detection Timestamp\
\
Signal Strength\
\
\---\
\
Purpose:\
\
Immediate orientation.\
\
\---\
\
\# Opportunity Summary\
\
Contains:\
\
Role Summary\
\
Opportunity Overview\
\
Key Highlights\
\
\---\
\
Purpose:\
\
Quick understanding.\
\
\---\
\
\# Responsibilities Section\
\
Contains:\
\
Primary Duties\
\
Core Expectations\
\
Role Scope\
\
\---\
\
Purpose:\
\
Role evaluation.\
\
\---\
\
\# Requirements Section\
\
Contains:\
\
Required Skills\
\
Preferred Skills\
\
Experience Requirements\
\
Education Requirements\
\
Certifications\
\
\---\
\
Purpose:\
\
Qualification assessment.\
\
\---\
\
\# Compensation & Logistics\
\
Contains:\
\
Salary\
\
Benefits\
\
Location\
\
Remote Status\
\
Travel Requirements\
\
Schedule\
\
\---\
\
Purpose:\
\
Practical evaluation.\
\
\---\
\
\# Company Intelligence Placement\
\
Company information belongs in the Context Panel.\
\
Not the primary content region.\
\
\---\
\
Contains:\
\
Company Summary\
\
Industry\
\
Organization Size\
\
Hiring Activity\
\
Watchlist Status\
\
Related Opportunities\
\
\---\
\
Purpose:\
\
Support evaluation without overwhelming the role.\
\
\---\
\
\# Atlas Integration\
\
\## Principle\
\
Atlas assists evaluation.\
\
Atlas does not dominate evaluation.\
\
\---\
\
\# Atlas Context Region\
\
Placement:\
\
Below Opportunity Summary.\
\
Above Actions.\
\
\---\
\
Visual Weight:\
\
Moderate.\
\
\---\
\
Contains:\
\
Opportunity Alignment\
\
Potential Strengths\
\
Potential Concerns\
\
Relevant Recommendations\
\
\---\
\
Question Answered:\
\
Why might this opportunity matter?\
\
\---\
\
\# Governance Rule\
\
Atlas context must never become larger than the opportunity description itself.\
\
\---\
\
\# Atlas Recommendation Placement\
\
Recommendations appear as embedded Recommendation Cards.\
\
\---\
\
Placement:\
\
Atlas Context Region\
\
Context Panel\
\
\---\
\
Examples:\
\
Apply Recommendation\
\
Investigate Company\
\
Resume Improvement\
\
Compare Similar Opportunities\
\
\---\
\
Rule:\
\
Recommendations remain secondary.\
\
\---\
\
\# Ask Atlas Placement\
\
Ask Atlas is the investigation layer.\
\
\---\
\
Primary Entry Points\
\
Opportunity Header\
\
Atlas Context Region\
\
Recommendation Cards\
\
Action Region\
\
Context Panel\
\
\---\
\
Example Questions\
\
Why is this a strong signal?\
\
What concerns should I investigate?\
\
How does this compare to similar roles?\
\
Am I qualified for this position?\
\
Should I prioritize this opportunity?\
\
\---\
\
\# Ask Atlas Behavior\
\
Launches with opportunity context attached.\
\
\---\
\
Attached Context\
\
Position\
\
Company\
\
Signal Strength\
\
Requirements\
\
Atlas Context\
\
Recommendations\
\
\---\
\
Governance Rule\
\
Users should never need to re-explain the opportunity.\
\
\---\
\
\# Action Hierarchy\
\
Actions follow a strict hierarchy.\
\
\---\
\
\## Primary Action\
\
Apply\
\
\---\
\
Purpose:\
\
Commit to pursuit.\
\
\---\
\
Visual Weight:\
\
Highest.\
\
\---\
\
\## Secondary Actions\
\
Save\
\
Track\
\
Compare\
\
Investigate Company\
\
\---\
\
Purpose:\
\
Support evaluation.\
\
\---\
\
Visual Weight:\
\
Medium.\
\
\---\
\
\## Advisory Action\
\
Ask Atlas\
\
\---\
\
Purpose:\
\
Decision support.\
\
\---\
\
Visual Weight:\
\
Secondary.\
\
\---\
\
Governance Rule\
\
Ask Atlas should support decisions.\
\
Not compete with Apply.\
\
\---\
\
\# Opportunity State Integration\
\
The surface reflects opportunity state.\
\
\---\
\
\# Newly Detected\
\
Focus:\
\
Evaluation.\
\
\---\
\
\# Tracked\
\
Focus:\
\
Monitoring.\
\
\---\
\
\# Saved\
\
Focus:\
\
Future review.\
\
\---\
\
\# Investigating\
\
Focus:\
\
Deep analysis.\
\
\---\
\
\# Ignored\
\
Focus:\
\
Read-only.\
\
\---\
\
\# Expired\
\
Focus:\
\
Historical reference.\
\
\---\
\
Actions disabled.\
\
\---\
\
\# Radar Relationship\
\
Radar is the source.\
\
\---\
\
Flow\
\
\```text id="sjr6m2"\
Radar\
\
↓\
\
Opportunity Signal Card\
\
↓\
\
Opportunity Detail Surface

-----
Purpose:

Discovery to evaluation.

-----
# <a name="command-center-relationship"></a>Command Center Relationship
Command Center surfaces exceptional opportunities.

-----
Flow

\```text id=“tfm0q1” Command Center

↓

Opportunity Alert

↓

Opportunity Detail Surface

\
\---\
\
Purpose:\
\
Awareness to evaluation.\
\
\---\
\
\# Pipeline Relationship\
\
Application begins here.\
\
\---\
\
Flow\
\
\```text id="wq8l4n"\
Opportunity Detail Surface\
\
↓\
\
Apply\
\
↓\
\
Pipeline

-----
Purpose:

Evaluation to execution.

-----
# <a name="empty-state-behavior"></a>Empty State Behavior
Not applicable.

The surface only exists when an opportunity exists.

-----
# <a name="error-state"></a>Error State
Opportunity unavailable.

-----
Examples

Posting removed

Source unavailable

Expired listing

-----
Message

This opportunity is no longer available.

Historical information remains accessible.

-----
# <a name="attention-model"></a>Attention Model
The Opportunity Detail Surface uses three levels.

-----
## <a name="level-1"></a>Level 1
Position

Company

Opportunity Summary

-----
## <a name="level-2"></a>Level 2
Requirements

Compensation

Actions

-----
## <a name="level-3"></a>Level 3
Atlas Context

Company Intelligence

Related Opportunities

-----
Governance Rule

Atlas supports evaluation.

Atlas does not become the evaluation.

-----
# <a name="success-criteria"></a>Success Criteria
A user should be able to spend five minutes in the Opportunity Detail Surface and understand:

What the opportunity is.

Who is offering it.

Whether they are qualified.

What concerns exist.

Why it may matter.

What actions are available.

Whether they should pursue it.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Informed

Curious

Prepared

Confident

In Control

-----
Users should not feel:

Pressured

Manipulated

Overwhelmed

Scored

Judged

-----
# <a name="surface-definition"></a>Surface Definition
The Opportunity Detail Surface is the primary opportunity evaluation environment of ATLAS.

It serves as the bridge between discovery and action.

Its responsibility is to help users understand opportunities deeply enough to make informed decisions.

It succeeds when users can confidently answer:

What is this opportunity?

Why might it matter?

Should I pursue it?

and can move naturally toward tracking, comparison, application, or further investigation through Atlas and Ask Atlas.
