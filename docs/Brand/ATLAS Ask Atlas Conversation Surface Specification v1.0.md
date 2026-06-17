# <a name="xb6414367c5bc43b23a4391b00503a95cf95b8f9"></a>ATLAS Ask Atlas Conversation Surface Specification v1.0
Status: Canonical Component Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Ask Atlas Conversation Surface is the primary communication workspace of the ATLAS ecosystem.

It exists to transform:

Awareness

↓

Intelligence

↓

Understanding

Unlike Radar, Pipeline, or Intelligence, Ask Atlas does not own workflows.

It owns explanation.

-----
# <a name="core-narrative"></a>Core Narrative
ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

The Conversation Surface is the final stage of this sequence.

Its purpose is to help users understand:

- why opportunities matter
- why recommendations exist
- what actions are available
- what tradeoffs exist
- what should happen next
-----
# <a name="design-principle"></a>Design Principle
Ask Atlas is not a chatbot.

Ask Atlas is a conversational intelligence layer.

The experience should feel like:

Consulting an advisor.

Not:

Using a messenger application.

-----
# <a name="when-users-enter-ask-atlas"></a>When Users Enter Ask Atlas
Users should enter Ask Atlas when they need:

Explanation

Comparison

Interpretation

Planning

Decision Support

-----
Examples

Why is this recommended?

Which opportunity should I prioritize?

What am I missing?

How should I prepare?

What should happen next?

-----
# <a name="x00b64ccac541747f759f19e4202034310d9ecec"></a>When Users Should Remain In Workflow Screens
Users should remain in:

Radar

Pipeline

Command Center

Intelligence

when performing operational work.

Examples:

Applying

Tracking

Updating Status

Managing Documents

Reviewing Opportunities

-----
Governance Rule

Ask Atlas explains workflows.

It does not replace workflows.

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The Conversation Surface follows a fixed hierarchy.

\```text id=“3djf9x” Conversation

Context

Referenced Objects

Suggested Actions

Suggested Prompts

History ```

-----
# <a name="visual-hierarchy"></a>Visual Hierarchy
## <a name="primary-element"></a>Primary Element
Conversation

The active discussion.

Largest visual area.

-----
## <a name="secondary-element"></a>Secondary Element
Context

The information Atlas is currently considering.

-----
## <a name="supporting-elements"></a>Supporting Elements
Referenced Opportunities

Referenced Recommendations

Referenced Applications

Referenced Companies

-----
## <a name="tertiary-elements"></a>Tertiary Elements
Suggested Prompts

Conversation History

-----
# <a name="surface-anatomy"></a>Surface Anatomy
## <a name="conversation-region"></a>Conversation Region
Purpose

Primary communication workspace.

-----
Contents

User Messages

Atlas Responses

Referenced Objects

Inline Recommendations

-----
Layout Priority

Highest.

Occupies majority of available space.

-----
# <a name="input-region"></a>Input Region
Purpose

Question submission.

-----
Contents

Input Field

Send Action

Context Attachments

-----
Position

Bottom anchored.

Persistent.

-----
# <a name="context-region"></a>Context Region
Purpose

Display active context.

-----
Examples

Opportunity

Application

Recommendation

Company

Document

-----
Behavior

Always visible when context exists.

Collapsible.

-----
# <a name="reference-object-region"></a>Reference Object Region
Purpose

Display objects currently referenced in the conversation.

-----
Examples

Opportunity Cards

Recommendation Cards

Application Cards

Company Cards

-----
Behavior

Interactive.

Open original object on selection.

-----
# <a name="suggested-prompt-region"></a>Suggested Prompt Region
Purpose

Reduce blank-page friction.

-----
Position

Below conversation header.

Above conversation body.

-----
# <a name="context-model"></a>Context Model
Ask Atlas is context-aware.

Every conversation should know what initiated it.

-----
# <a name="opportunity-context"></a>Opportunity Context
Example

User opens Ask Atlas from Radar.

-----
Context Attached

Opportunity

Company

Signal Strength

Notes

-----
# <a name="recommendation-context"></a>Recommendation Context
Example

User opens Ask Atlas from Recommendation Card.

-----
Context Attached

Recommendation

Reasoning

Confidence

Suggested Action

-----
# <a name="application-context"></a>Application Context
Example

User opens Ask Atlas from Pipeline.

-----
Context Attached

Status

Timeline

Interview Data

Notes

-----
# <a name="company-context"></a>Company Context
Example

User launches from Company Intelligence.

-----
Context Attached

Company

History

Hiring Activity

Tracked Signals

-----
# <a name="governance-rule"></a>Governance Rule
Ask Atlas should never ask users to manually re-explain information already available in ATLAS.

-----
# <a name="suggested-prompt-system"></a>Suggested Prompt System
## <a name="purpose-1"></a>Purpose
Provide useful entry points.

-----
# <a name="display-conditions"></a>Display Conditions
Appears:

New Conversations

Context Changes

Empty Conversations

-----
Hidden:

Established conversations

-----
# <a name="quantity"></a>Quantity
Maximum:

4 prompts

Recommended:

3 prompts

-----
# <a name="example-prompts"></a>Example Prompts
Opportunity Context

Why is this a strong signal?

How does this compare to similar roles?

What concerns should I investigate?

-----
Recommendation Context

Why is Atlas recommending this?

What happens if I ignore this?

What should I do next?

-----
Pipeline Context

What is my best next action?

Am I at risk of losing momentum?

What should I prioritize?

-----
# <a name="visual-treatment"></a>Visual Treatment
Low emphasis.

Secondary element.

Never dominant.

-----
# <a name="recommendation-integration"></a>Recommendation Integration
Recommendations appear as referenced objects.

Not conversation replacements.

-----
# <a name="recommendation-reference"></a>Recommendation Reference
Displays:

Recommendation

Reasoning

Confidence

Action

-----
Behavior

Clickable.

Expandable.

-----
Governance Rule

Recommendations remain Recommendation Cards.

Do not transform them into messages.

-----
# <a name="workflow-integration"></a>Workflow Integration
## <a name="command-center"></a>Command Center
Entry Point

Recommendation Cards

Action Queue

-----
Purpose

Decision support.

-----
## <a name="radar"></a>Radar
Entry Point

Opportunity Signal Cards

-----
Purpose

Opportunity investigation.

-----
## <a name="pipeline"></a>Pipeline
Entry Point

Applications

Interviews

Offers

-----
Purpose

Workflow guidance.

-----
## <a name="intelligence"></a>Intelligence
Entry Point

Recommendations

Insights

Trend Analysis

-----
Purpose

Interpretation.

-----
# <a name="exit-behavior"></a>Exit Behavior
User always returns to originating workflow.

Context preserved.

No loss of state.

-----
# <a name="waveform-identity"></a>Waveform Identity
Ask Atlas uses waveform language.

ATLAS uses radar language.

Atlas uses signal-intelligence language.

-----
# <a name="waveform-purpose"></a>Waveform Purpose
Communicate:

Conversation

Signal exchange

Interpretation

-----
# <a name="approved-waveform-usage"></a>Approved Waveform Usage
Conversation Header

Loading States

Input Activation

Conversation Transitions

-----
# <a name="prohibited-usage"></a>Prohibited Usage
Large backgrounds

Continuous motion

Decorative animation

-----
# <a name="signal-cyan-governance"></a>Signal Cyan Governance
## <a name="purpose-2"></a>Purpose
Signal Cyan represents intelligence.

-----
# <a name="approved-usage"></a>Approved Usage
Waveform Elements

Conversation Focus States

Recommendation References

Context Highlights

Atlas Responses

-----
# <a name="maximum-visual-weight"></a>Maximum Visual Weight
10–15%

-----
# <a name="prohibited-usage-1"></a>Prohibited Usage
Entire conversation backgrounds

Large text blocks

Input surfaces

Primary layout containers

-----
Reason

Cyan remains an accent.

Not an environment color.

-----
# <a name="conversation-states"></a>Conversation States
## <a name="empty"></a>Empty
No conversation yet.

-----
Message

Ask Atlas about opportunities, recommendations, applications, or career strategy.

-----
Prompts visible.

-----
## <a name="active"></a>Active
Normal conversation.

-----
## <a name="loading"></a>Loading
Atlas generating response.

-----
Uses approved waveform loading behavior.

-----
## <a name="error"></a>Error
Response unavailable.

-----
Recovery path required.

-----
## <a name="context-lost"></a>Context Lost
Referenced object unavailable.

-----
Conversation preserved.

Context flagged.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Understood

Informed

Guided

Prepared

Confident

-----
Users should not feel:

Judged

Managed

Overwhelmed

Lectured

Sold to

-----
# <a name="success-criteria"></a>Success Criteria
The Ask Atlas Conversation Surface succeeds when users can quickly answer:

What are we discussing?

What information is Atlas considering?

Why is Atlas saying this?

What should I do next?

If those answers are clear, the conversation surface has succeeded.

If users feel they have entered a separate chatbot disconnected from the rest of ATLAS, the conversation surface has failed.

The Ask Atlas Conversation Surface is the canonical communication workspace of the ATLAS ecosystem and serves as the primary interface between users and Atlas intelligence.
