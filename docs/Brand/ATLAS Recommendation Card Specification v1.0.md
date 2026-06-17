# <a name="xc4f4c7261991f6a243225fff2c697b22bee2984"></a>ATLAS Recommendation Card Specification v1.0
Status: Canonical Component Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Recommendation Card is the primary manifestation of Atlas intelligence.

It represents the moment where:

ATLAS scans.

↓

Atlas interprets.

↓

The user decides.

The Recommendation Card exists to convert information into action.

It is not an alert.

It is not a notification.

It is not analytics.

It is a decision-support object.

-----
# <a name="design-principle"></a>Design Principle
The Recommendation Card should feel:

Important

Actionable

Thoughtful

Strategic

Calm

The card should never feel:

Urgent

Demanding

Alarmist

Sales-like

Gamified

-----
# <a name="appearance-criteria"></a>Appearance Criteria
The user should interpret a Recommendation Card as:

“Atlas believes this deserves my attention.”

Not:

“You must do this immediately.”

-----
# <a name="when-recommendations-appear"></a>When Recommendations Appear
Recommendations appear when Atlas identifies a high-confidence action or insight.

Examples:

- Apply to a position
- Follow up on an application
- Prepare for an interview
- Improve a resume
- Address a skill gap
- Review a newly discovered opportunity
-----
# <a name="when-recommendations-should-not-appear"></a>When Recommendations Should Not Appear
Recommendations should not appear for:

Routine status updates

Pure informational events

Historical reporting

Low-confidence observations

System health events

Generic reminders

Those belong elsewhere.

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The Recommendation Card follows a fixed hierarchy.

Recommendation\
\
Reasoning\
\
Suggested Action\
\
Impact\
\
Confidence\
\
Supporting Metadata

This order is mandatory.

-----
# <a name="visual-hierarchy"></a>Visual Hierarchy
## <a name="primary-element"></a>Primary Element
Recommendation Statement

Largest visual element.

Answers:

What should I do?

-----
## <a name="secondary-element"></a>Secondary Element
Reasoning Summary

Answers:

Why is Atlas recommending this?

-----
## <a name="supporting-element"></a>Supporting Element
Suggested Action

Answers:

What happens next?

-----
## <a name="tertiary-elements"></a>Tertiary Elements
Impact

Confidence

Metadata

-----
# <a name="card-anatomy"></a>Card Anatomy
## <a name="header"></a>Header
Contains:

Recommendation Type

Recommendation Title

Timestamp

-----
Example:

Apply to Structural Engineer I

Detected 2 hours ago

-----
# <a name="body"></a>Body
Contains:

Recommendation Statement

Single concise sentence.

-----
Example:

This position aligns strongly with your structural engineering goals and current experience profile.

-----
# <a name="reasoning-section"></a>Reasoning Section
Purpose:

Provide evidence.

-----
Required:

1–3 supporting factors.

-----
Example:

- Strong structural focus
- Matches geographic preferences
- Salary above current target range
-----
Rule:

Reasoning must be concise.

Never exceed three bullets.

-----
# <a name="suggested-action-section"></a>Suggested Action Section
Purpose:

Convert intelligence into action.

-----
Required:

Action Label

-----
Examples:

Apply Now

Review Position

Prepare Interview

Update Resume

Investigate Company

-----
# <a name="metadata-section"></a>Metadata Section
Optional.

Contains:

Company

Location

Salary

Deadline

Source

-----
Metadata is supporting information only.

Never primary.

-----
# <a name="confidence-presentation"></a>Confidence Presentation
## <a name="principle"></a>Principle
Avoid fake precision.

No percentages.

No confidence scores.

No statistical language.

-----
## <a name="approved-confidence-levels"></a>Approved Confidence Levels
High Confidence

Strong Signal

Emerging Signal

Review Recommended

-----
# <a name="visual-treatment"></a>Visual Treatment
Confidence appears as:

Small signal indicator

Label

-----
Examples:

● High Confidence

● Strong Signal

-----
Confidence is supporting context.

Never dominant.

-----
# <a name="recommendation-types"></a>Recommendation Types
Recommendation types share the same structure.

Only accent behavior changes.

-----
# <a name="apply"></a>Apply
Purpose:

Opportunity identified.

-----
Primary Action:

Apply Now

-----
Reasoning Focus:

Fit

Alignment

Potential

-----
# <a name="follow-up"></a>Follow Up
Purpose:

Application requires attention.

-----
Primary Action:

Follow Up

-----
Reasoning Focus:

Timing

Pipeline progression

Response likelihood

-----
# <a name="interview-preparation"></a>Interview Preparation
Purpose:

Upcoming interview.

-----
Primary Action:

Prepare Interview

-----
Reasoning Focus:

Readiness

Company research

Role preparation

-----
# <a name="resume-improvement"></a>Resume Improvement
Purpose:

Application competitiveness.

-----
Primary Action:

Review Resume

-----
Reasoning Focus:

Missing evidence

Formatting

Keyword alignment

-----
# <a name="skill-gap"></a>Skill Gap
Purpose:

Career improvement.

-----
Primary Action:

Review Skill Gap

-----
Reasoning Focus:

Market demand

Career trajectory

Opportunity access

-----
# <a name="opportunity-alert"></a>Opportunity Alert
Purpose:

Exceptional opportunity detected.

-----
Primary Action:

Review Opportunity

-----
Reasoning Focus:

Alignment

Quality

Potential impact

-----
# <a name="action-hierarchy"></a>Action Hierarchy
Every Recommendation Card supports:

-----
## <a name="primary-action"></a>Primary Action
Recommended next step.

Required.

Single action only.

-----
Examples:

Apply

Prepare

Review

Follow Up

-----
## <a name="secondary-action"></a>Secondary Action
Open detailed context.

Optional.

-----
Examples:

View Position

Open Company

See Analysis

-----
## <a name="dismiss"></a>Dismiss
Always available.

Low visual emphasis.

-----
# <a name="governance-rule"></a>Governance Rule
Only one primary action may exist.

Multiple competing primary actions are prohibited.

-----
# <a name="signal-cyan-usage"></a>Signal Cyan Usage
## <a name="governance-requirement"></a>Governance Requirement
Signal Cyan represents Atlas intelligence.

The Recommendation Card is one of the few places where cyan is explicitly permitted.

-----
# <a name="approved-cyan-usage"></a>Approved Cyan Usage
Recommendation Type Marker

Confidence Indicator

Atlas Identifier

Recommendation Accent Bar

-----
# <a name="maximum-visual-weight"></a>Maximum Visual Weight
10–15% of card surface.

-----
# <a name="prohibited-usage"></a>Prohibited Usage
Full cyan backgrounds

Large cyan blocks

Cyan body text

Cyan buttons unrelated to Atlas

-----
# <a name="empty-state"></a>Empty State
Purpose:

No recommendations available.

-----
Message:

Atlas has no high-confidence recommendations at this time.

Monitoring continues.

-----
Visual Treatment:

Minimal radar sweep.

No warning indicators.

-----
# <a name="dismissed-state"></a>Dismissed State
Purpose:

User rejected recommendation.

-----
Behavior:

Removed from primary surfaces.

Stored in recommendation history.

-----
Visual Treatment:

No persistent warning.

No reappearance unless conditions materially change.

-----
# <a name="expired-state"></a>Expired State
Purpose:

Recommendation no longer relevant.

-----
Examples:

Opportunity closed.

Deadline passed.

Interview completed.

-----
Behavior:

Moves to history.

Clearly marked expired.

No action available.

-----
# <a name="placement-rules"></a>Placement Rules
## <a name="command-center"></a>Command Center
Highest visibility.

Maximum:

3–5 active recommendations.

-----
Purpose:

Immediate attention.

-----
# <a name="radar"></a>Radar
Contextual recommendations.

-----
Examples:

Apply

Track

Investigate

-----
Purpose:

Opportunity evaluation.

-----
# <a name="pipeline"></a>Pipeline
Workflow recommendations.

-----
Examples:

Follow Up

Prepare Interview

Respond to Offer

-----
Purpose:

Pipeline advancement.

-----
# <a name="intelligence"></a>Intelligence
Primary recommendation workspace.

-----
Contains:

All active recommendations

History

Decision tracking

Recommendation analytics

-----
Purpose:

Recommendation management.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Informed

Guided

Confident

Prepared

In control

-----
Users should not feel:

Pressured

Judged

Overwhelmed

Managed

-----
# <a name="success-criteria"></a>Success Criteria
The Recommendation Card succeeds when a user can answer three questions within five seconds:

What is Atlas recommending?

Why is Atlas recommending it?

What should I do next?

If any of those answers are unclear, the card has failed.

The Recommendation Card is the canonical expression of Atlas intelligence and should be treated as the highest-value non-alert component in the ATLAS platform.
