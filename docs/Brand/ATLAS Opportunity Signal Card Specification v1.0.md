# <a name="x32976c0ec4c7171d897d0bbb6a0bd7469b08afa"></a>ATLAS Opportunity Signal Card Specification v1.0
Status: Canonical Component Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
The Opportunity Signal Card is the primary manifestation of ATLAS.

The Recommendation Card represents Atlas intelligence.

The Opportunity Signal Card represents ATLAS awareness.

This is the moment where:

ATLAS scans.

↓

Opportunity detected.

↓

User investigates.

The card exists to surface potentially valuable opportunities discovered by the platform.

It is intentionally positioned before:

- recommendations
- applications
- interviews
- analytics

Its responsibility is discovery.

-----
# <a name="design-principle"></a>Design Principle
The Opportunity Signal Card should feel:

Interesting

Promising

Discoverable

Relevant

Professional

The card should never feel:

Urgent

Prescriptive

Analytical

Overwhelming

Gamified

-----
# <a name="user-interpretation"></a>User Interpretation
Users should immediately understand:

“ATLAS found something worth looking at.”

Not:

“Atlas believes I should do this.”

That distinction is critical.

Recommendations belong to Atlas.

Detection belongs to ATLAS.

-----
# <a name="when-opportunity-signal-cards-appear"></a>When Opportunity Signal Cards Appear
The card appears when:

- new opportunities are discovered
- existing opportunities change meaningfully
- tracked companies create relevant openings
- monitored sources detect matching roles
-----
# <a name="xda6387e8f2e597c80d9ae430d00e7b541941b54"></a>When Opportunity Signal Cards Should Not Appear
Do not use this card for:

Recommendations

Follow-Ups

Interview Preparation

Pipeline Actions

Career Insights

System Notifications

Those belong to other component families.

-----
# <a name="information-hierarchy"></a>Information Hierarchy
The card follows a fixed hierarchy.

\```text id=“j8ut7s” Position

Company

Opportunity Summary

Signal Strength

Location

Compensation

Tags

Status ```

-----
# <a name="visual-hierarchy"></a>Visual Hierarchy
## <a name="primary-element"></a>Primary Element
Position Title

Largest element.

Most important piece of information.

Answers:

What opportunity was found?

-----
## <a name="secondary-element"></a>Secondary Element
Company

Answers:

Who is offering the opportunity?

-----
## <a name="supporting-element"></a>Supporting Element
Opportunity Summary

Answers:

Why might this be relevant?

-----
## <a name="tertiary-elements"></a>Tertiary Elements
Signal Strength

Location

Compensation

Tags

Status

-----
# <a name="card-anatomy"></a>Card Anatomy
## <a name="header"></a>Header
Contains:

Position Title

Company

Detection Timestamp

-----
Example:

Structural Engineer I

H2M Architects + Engineers

Detected 3 hours ago

-----
# <a name="signal-region"></a>Signal Region
Purpose:

Represent detection quality.

Contains:

Signal Indicator

Signal Label

-----
Position:

Upper-right region.

Visually important but not dominant.

-----
# <a name="opportunity-summary"></a>Opportunity Summary
Purpose:

Provide quick context.

-----
Required:

Single concise summary.

Maximum:

2 lines.

-----
Example:

Entry-level structural engineering role aligned with current experience and location preferences.

-----
# <a name="metadata-region"></a>Metadata Region
Contains:

Location

Work Mode

Compensation

Source

Tags

-----
Metadata supports evaluation.

It never dominates the card.

-----
# <a name="action-region"></a>Action Region
Contains primary interaction options.

Actions vary by placement context.

-----
# <a name="signal-strength-presentation"></a>Signal Strength Presentation
## <a name="principle"></a>Principle
Signal strength communicates relevance.

Not certainty.

Not recommendation quality.

Not predictive success.

-----
# <a name="prohibited"></a>Prohibited
Percentages

Scores

Rankings

Numerical grades

Opaque algorithms

-----
# <a name="approved-levels"></a>Approved Levels
Exceptional Match

Strong Signal

Relevant Signal

Emerging Signal

-----
# <a name="visual-treatment"></a>Visual Treatment
Small signal indicator

Text label

-----
Example

● Strong Signal

-----
# <a name="governance-rule"></a>Governance Rule
Signal strength is supporting information.

The opportunity itself remains primary.

-----
# <a name="opportunity-states"></a>Opportunity States
## <a name="newly-detected"></a>Newly Detected
Purpose:

Recently discovered.

-----
Behavior:

Appears in Radar.

Eligible for Command Center surfacing.

-----
Visual Treatment:

Subtle detection indicator.

-----
## <a name="tracked"></a>Tracked
Purpose:

User actively monitoring.

-----
Behavior:

Added to watchlist.

-----
Visual Treatment:

Tracked marker.

-----
## <a name="saved"></a>Saved
Purpose:

User interested.

-----
Behavior:

Stored for later review.

-----
Visual Treatment:

Saved indicator.

-----
## <a name="investigating"></a>Investigating
Purpose:

Under active review.

-----
Behavior:

Appears in context workflows.

-----
Visual Treatment:

Investigation marker.

-----
## <a name="ignored"></a>Ignored
Purpose:

User intentionally dismissed.

-----
Behavior:

Removed from primary surfaces.

-----
Visual Treatment:

Hidden by default.

-----
## <a name="expired"></a>Expired
Purpose:

Opportunity no longer available.

-----
Behavior:

Moved to history.

Actions disabled.

-----
Visual Treatment:

Reduced emphasis.

-----
# <a name="action-hierarchy"></a>Action Hierarchy
Every Opportunity Signal Card supports:

-----
## <a name="primary-action"></a>Primary Action
Review Opportunity

-----
Purpose:

Open detail surface.

-----
Reason:

Discovery should precede commitment.

-----
## <a name="secondary-actions"></a>Secondary Actions
Track

Save

Compare

-----
Purpose:

Organize evaluation workflow.

-----
## <a name="dismissive-action"></a>Dismissive Action
Ignore

-----
Purpose:

Remove irrelevant opportunities.

-----
Visual Weight:

Lowest.

-----
# <a name="governance-rule-1"></a>Governance Rule
Apply actions do not belong on the Opportunity Signal Card.

Application actions belong inside the Opportunity Detail Surface or Atlas recommendations.

-----
# <a name="signal-cyan-governance"></a>Signal Cyan Governance
## <a name="principle-1"></a>Principle
The Opportunity Signal Card belongs to ATLAS.

Not Atlas.

-----
# <a name="approved-cyan-usage"></a>Approved Cyan Usage
Signal Indicator

Detection Marker

Radar Context

-----
# <a name="maximum-visual-weight"></a>Maximum Visual Weight
5–10%

-----
# <a name="primary-color-usage"></a>Primary Color Usage
Deep Navy

Atlas Blue

-----
# <a name="prohibited-cyan-usage"></a>Prohibited Cyan Usage
Large surfaces

Primary headers

Position titles

Card backgrounds

-----
Reason

Cyan is reserved primarily for Atlas intelligence.

-----
# <a name="placement-rules"></a>Placement Rules
## <a name="radar"></a>Radar
Primary surface.

-----
Purpose:

Discovery.

-----
Maximum Density:

High.

Radar may contain many Opportunity Signal Cards.

-----
# <a name="command-center"></a>Command Center
Selective surface.

-----
Purpose:

Awareness.

-----
Only:

Exceptional Match

Strong Signal

opportunities appear.

-----
Maximum:

3–5 cards.

-----
# <a name="context-panel"></a>Context Panel
Expanded representation.

-----
Purpose:

Investigation.

-----
Contains:

Full summary

Metadata

Related recommendations

Company intelligence

-----
# <a name="search-results"></a>Search Results
Compact representation.

-----
Purpose:

Efficient discovery.

-----
Reduced metadata.

-----
Same information hierarchy.

-----
# <a name="relationship-to-recommendation-cards"></a>Relationship To Recommendation Cards
Opportunity Signal Cards answer:

What was found?

-----
Recommendation Cards answer:

What should I do?

-----
These components must remain distinct.

-----
# <a name="empty-state"></a>Empty State
Purpose:

No opportunities detected.

-----
Message:

No new signals detected.

Monitoring continues.

-----
Visual Treatment:

Single radar sweep.

No warning state.

No negative messaging.

-----
# <a name="emotional-outcome"></a>Emotional Outcome
Users should feel:

Curious

Optimistic

Informed

Aware

Prepared

-----
Users should not feel:

Pressured

Evaluated

Managed

Directed

-----
# <a name="success-criteria"></a>Success Criteria
The Opportunity Signal Card succeeds when a user can answer three questions within five seconds:

What opportunity was found?

Why might it be relevant?

Should I investigate further?

If those answers are clear, the card has succeeded.

If the user instead asks:

“What is Atlas trying to get me to do?”

then the card has failed.

The Opportunity Signal Card represents awareness, not recommendation.

Its purpose is to embody the scanning function of ATLAS and serve as the canonical detection object throughout the platform.
