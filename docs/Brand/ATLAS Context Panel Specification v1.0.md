# <a name="atlas-context-panel-specification-v1.0"></a>ATLAS Context Panel Specification v1.0
Status: Canonical Workspace Surface Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Context Panel is the investigation layer of ATLAS.

It exists to provide depth without disrupting workflow.

The Context Panel allows users to explore an object while remaining anchored to their current workspace.

-----
# <a name="core-philosophy"></a>Core Philosophy
Primary Workspaces answer:

What is happening?

The Context Panel answers:

What should I know about this specific thing?

-----
# <a name="narrative-role"></a>Narrative Role
ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

The Context Panel is where those layers converge around a single object.

It is the location where:

- opportunity context
- pipeline context
- recommendations
- supporting intelligence
- conversational entry points

are unified.

-----
# <a name="design-principle"></a>Design Principle
The Context Panel should feel:

Focused

Contextual

Immediate

Supportive

It should never feel:

Like a second application

Like a replacement workspace

Like a dashboard

Like a modal

-----
# <a name="ownership"></a>Ownership
## <a name="the-context-panel-owns"></a>The Context Panel Owns
Object Summary

Related Information

Atlas Recommendations

Timeline Context

Related Objects

Ask Atlas Launch Points

Supporting Metadata

-----
## <a name="the-context-panel-does-not-own"></a>The Context Panel Does Not Own
Primary Workflows

Navigation

Large Forms

Application Management

Discovery

Recommendation Management

Conversation

Analytics

Those belong to primary workspaces.

-----
# <a name="core-questions"></a>Core Questions
The Context Panel must answer:

What is this?

Why does it matter?

What else should I know?

What should I do next?

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The hierarchy is fixed.

Object Summary\
\
Related Objects\
\
Atlas Recommendations\
\
Timeline\
\
Ask Atlas\
\
Supporting Metadata

-----
# <a name="hierarchy-rationale"></a>Hierarchy Rationale
Users first need orientation.

Then relationships.

Then intelligence.

Then history.

Then explanation.

-----
# <a name="surface-anatomy"></a>Surface Anatomy
The Context Panel consists of five sections.

-----
# <a name="summary-region"></a>Summary Region
Purpose:

Immediate understanding.

-----
Visual Priority:

Highest

-----
Contains:

Title

Status

Owner

Summary

Key Metadata

-----
Examples:

Opportunity

Application

Recommendation

Company

Interview

Offer

-----
Question Answered:

What is this?

-----
# <a name="related-objects-region"></a>Related Objects Region
Purpose:

Show connected information.

-----
Visual Priority:

High

-----
Contains:

Related Opportunities

Related Applications

Related Companies

Related Recommendations

Documents

-----
Question Answered:

What is connected to this?

-----
# <a name="atlas-recommendation-region"></a>Atlas Recommendation Region
Purpose:

Provide intelligence.

-----
Visual Priority:

Medium

-----
Contains:

Recommendation Cards

Insight Summaries

Relevant Signals

-----
Question Answered:

What does Atlas think?

-----
Governance Rule

Maximum:

3 active recommendations visible.

-----
# <a name="timeline-region"></a>Timeline Region
Purpose:

Historical context.

-----
Visual Priority:

Medium

-----
Contains:

Events

Status Changes

Detection History

Application History

Interview Activity

Recommendation Activity

-----
Question Answered:

How did we get here?

-----
# <a name="ask-atlas-region"></a>Ask Atlas Region
Purpose:

Provide explanation.

-----
Visual Priority:

Supporting

-----
Contains:

Launch Actions

Suggested Questions

Conversation Entry Points

-----
Question Answered:

What do I want explained?

-----
# <a name="context-panel-width"></a>Context Panel Width
Default

360px

-----
Expanded

480px

-----
Collapsed

Hidden

-----
Reference:

ATLAS Desktop Design System v1.1

-----
# <a name="context-types"></a>Context Types
The Context Panel adapts to the selected object.

-----
# <a name="opportunity-context"></a>Opportunity Context
Contains:

Opportunity Summary

Signal Strength

Company

Related Opportunities

Atlas Context

Ask Atlas

-----
# <a name="application-context"></a>Application Context
Contains:

Application Status

Timeline

Follow-Ups

Recommendations

Ask Atlas

-----
# <a name="interview-context"></a>Interview Context
Contains:

Interview Details

Preparation Guidance

Timeline

Recommendations

Ask Atlas

-----
# <a name="offer-context"></a>Offer Context
Contains:

Offer Details

Decision Context

Recommendations

Ask Atlas

-----
# <a name="recommendation-context"></a>Recommendation Context
Contains:

Recommendation

Reasoning

Confidence

Related Objects

Ask Atlas

-----
# <a name="company-context"></a>Company Context
Contains:

Company Summary

Hiring Activity

Tracked Opportunities

Recommendations

Ask Atlas

-----
# <a name="workspace-relationships"></a>Workspace Relationships
The Context Panel behaves consistently across ATLAS.

Its content changes.

Its structure does not.

-----
# <a name="command-center"></a>Command Center
Purpose:

Investigation.

-----
Triggered By:

Action Queue

Recommendations

Signals

Interviews

Follow-Ups

-----
Question Answered:

Why does this require attention?

-----
# <a name="radar"></a>Radar
Purpose:

Opportunity evaluation.

-----
Triggered By:

Opportunity Signal Cards

Companies

Watchlists

-----
Question Answered:

Should I investigate further?

-----
# <a name="pipeline"></a>Pipeline
Purpose:

Operational understanding.

-----
Triggered By:

Applications

Interviews

Offers

Follow-Ups

-----
Question Answered:

What should happen next?

-----
# <a name="intelligence"></a>Intelligence
Purpose:

Decision support.

-----
Triggered By:

Recommendations

Insights

Trends

Decision History

-----
Question Answered:

Why is Atlas recommending this?

-----
# <a name="atlas-integration"></a>Atlas Integration
Atlas primarily appears inside the Context Panel through:

Recommendation Cards

Insight Summaries

Confidence Indicators

Relationship Signals

-----
Governance Rule

Atlas supports context.

Atlas does not dominate context.

The selected object remains primary.

-----
# <a name="recommendation-placement"></a>Recommendation Placement
Recommendations appear after:

Summary

Related Objects

before:

Timeline

Ask Atlas

-----
Reason:

Interpretation should occur before history.

-----
# <a name="ask-atlas-integration"></a>Ask Atlas Integration
Ask Atlas is the explanation layer.

-----
# <a name="placement"></a>Placement
Bottom persistent region.

Always available.

-----
# <a name="entry-methods"></a>Entry Methods
Ask Atlas Button

Suggested Questions

Recommendation Cards

Related Objects

-----
# <a name="context-transfer"></a>Context Transfer
When launched, Ask Atlas receives:

Selected Object

Related Objects

Atlas Recommendations

Timeline Context

Relevant Metadata

-----
Governance Rule

Users should never need to manually recreate context.

-----
# <a name="motion-behavior"></a>Motion Behavior
Reference:

ATLAS Motion & Interaction Specification v1.0

-----
# <a name="open"></a>Open
Slide from right.

Fade in.

250ms.

-----
# <a name="close"></a>Close
Fade out.

Slide away.

200ms.

-----
# <a name="expand"></a>Expand
Grow width.

Maintain content stability.

250ms.

-----
# <a name="collapse"></a>Collapse
Reduce width.

No content reflow outside panel.

250ms.

-----
# <a name="context-change"></a>Context Change
Crossfade content.

150ms.

-----
Rule

The panel should feel continuous.

Not disruptive.

-----
# <a name="empty-state-behavior"></a>Empty State Behavior
## <a name="no-context-selected"></a>No Context Selected
Message:

Select an opportunity, application, recommendation, or company to view additional context.

-----
Visual Treatment:

Minimal.

No illustrations.

-----
Purpose:

Orientation.

-----
# <a name="error-state"></a>Error State
Message:

Context is temporarily unavailable.

Retry or return to the workspace.

-----
Recovery path required.

-----
# <a name="attention-model"></a>Attention Model
The Context Panel uses three levels.

-----
## <a name="level-1"></a>Level 1
Summary

Related Objects

-----
## <a name="level-2"></a>Level 2
Atlas Recommendations

-----
## <a name="level-3"></a>Level 3
Timeline

Ask Atlas

-----
Governance Rule

The selected object must always remain more important than Atlas recommendations.

-----
# <a name="success-criteria"></a>Success Criteria
A user should be able to open the Context Panel and understand:

What this object is.

Why it matters.

What is connected to it.

What Atlas recommends.

What happened previously.

What should happen next.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Informed

Grounded

Prepared

Confident

Aware

-----
Users should not feel:

Lost

Distracted

Overwhelmed

Pulled away from their workflow

-----
# <a name="surface-definition"></a>Surface Definition
The Context Panel is the universal investigation layer of ATLAS.

It provides depth without requiring navigation.

Its responsibility is to enrich understanding of the currently selected object through context, relationships, recommendations, history, and explanation.

It succeeds when users can answer:

What is this?

Why does it matter?

What should I do next?

without leaving their current workspace.
