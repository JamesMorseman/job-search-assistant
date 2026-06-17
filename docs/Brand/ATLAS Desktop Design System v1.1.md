# <a name="atlas-desktop-design-system-v1.1"></a>ATLAS Desktop Design System v1.1
### <a name="minor-revision-package"></a>Minor Revision Package
### <a name="status-freeze-candidate"></a>Status: Freeze Candidate
Authority:

- ATLAS Brand Specification v1.0
- Package 1 Review (Ash)

This package supplements Package 1 only.

No existing standards are superseded unless explicitly stated.

-----
# <a name="sidebar-specification"></a>1. Sidebar Specification
## <a name="purpose"></a>Purpose
The sidebar is the primary navigation system for ATLAS.

Its purpose is:

- orientation
- navigation
- awareness

Not content consumption.

Not workflow execution.

-----
# <a name="sidebar-hierarchy"></a>Sidebar Hierarchy
Primary Navigation

Represents major platform functions.

Examples:

- Command Center
- Radar
- Pipeline
- Intelligence
- Ask Atlas
-----
Secondary Navigation

Contextual tools.

Examples:

- Documents
- Saved Searches
- Reports
-----
Utility Navigation

Persistent application utilities.

Examples:

- Settings
- Help
- Feedback

Always anchored to bottom.

-----
# <a name="sidebar-width"></a>Sidebar Width
Expanded

280px

Default desktop state.

-----
Collapsed

72px

Icon-only mode.

-----
Transition

200ms

Fade + slide.

No bounce.

No overshoot.

-----
# <a name="active-state"></a>Active State
Uses Atlas Blue.

Never Signal Cyan.

Reason:

Navigation belongs to ATLAS.

Not Atlas.

-----
# <a name="notification-badges"></a>Notification Badges
Color:

Atlas Blue

Default

-----
Amber

Action Required

-----
Red

Critical

-----
Signal Cyan prohibited.

Cyan remains reserved for intelligence.

-----
# <a name="context-panel-specification"></a>2. Context Panel Specification
## <a name="purpose-1"></a>Purpose
The Context Panel provides situational detail.

It should never become a second workspace.

-----
Examples

Selected Opportunity

Selected Company

Selected Recommendation

Selected Application

Ask Atlas Context

-----
# <a name="default-width"></a>Default Width
360px

-----
Expanded Width

480px

Maximum

-----
Collapsed

Hidden

Retains state.

-----
# <a name="behavior"></a>Behavior
Optional.

Not required on every screen.

-----
Priority Order

Workspace

↓

Context Panel

↓

Analytics

The Context Panel supports decisions.

It does not drive navigation.

-----
# <a name="laptop-behavior"></a>Laptop Behavior
Below 1440px:

Auto-collapse

Open on demand.

-----
# <a name="allowed-content"></a>Allowed Content
Opportunity Details

Company Details

Atlas Recommendations

Conversation Context

Related Documents

Timeline History

-----
# <a name="prohibited-content"></a>Prohibited Content
Primary navigation

Full dashboards

Complex forms

Major workflows

-----
# <a name="recommendation-card-specification"></a>3. Recommendation Card Specification
## <a name="new-card-type"></a>New Card Type
Recommendation Card

Priority:

Highest non-alert component.

-----
# <a name="purpose-2"></a>Purpose
Translate intelligence into action.

This card represents:

Atlas recommendations.

Not observations.

Not metrics.

-----
# <a name="examples"></a>Examples
Apply to Position

Follow Up

Review Resume

Investigate Employer

Prepare Interview

Skill Gap Identified

-----
# <a name="anatomy"></a>Anatomy
Recommendation Type

↓

Recommendation Statement

↓

Reasoning Summary

↓

Suggested Action

↓

Confidence Indicator

-----
# <a name="visual-treatment"></a>Visual Treatment
Base:

Standard card

Accent:

Signal Cyan

Maximum 10% card area.

-----
# <a name="required-actions"></a>Required Actions
Accept

Dismiss

Review

At least one action required.

-----
# <a name="governance-rule"></a>Governance Rule
Recommendations must always produce a possible action.

Never surface intelligence without a path forward.

-----
# <a name="empty-state-specification"></a>4. Empty State Specification
## <a name="principle"></a>Principle
Empty states are awareness states.

Not failure states.

-----
# <a name="tone"></a>Tone
Calm

Professional

Positive

-----
# <a name="follow-ups"></a>Follow-Ups
No Follow-Ups Due

All tracked opportunities are current.

-----
# <a name="interviews"></a>Interviews
No Interviews Scheduled

ATLAS continues monitoring for opportunities.

-----
# <a name="offers"></a>Offers
No Active Offers

Your opportunity pipeline remains active.

-----
# <a name="recommendations"></a>Recommendations
No Recommendations Available

Atlas has no high-confidence actions at this time.

-----
# <a name="radar"></a>Radar
No New Signals Detected

Monitoring continues.

-----
# <a name="visual-pattern"></a>Visual Pattern
Minimal radar

Single sweep

No warning indicators

No illustrations

No mascots

-----
# <a name="empty-state-goal"></a>Empty State Goal
The system should feel:

Operational

not

Inactive

-----
# <a name="notification-severity-hierarchy"></a>5. Notification Severity Hierarchy
## <a name="level-1"></a>Level 1
Informational

Purpose:

Awareness

Examples:

Source Updated

Application Viewed

New Data Available

-----
Visual Weight:

Low

Color:

Atlas Blue

-----
## <a name="level-2"></a>Level 2
Recommendation

Purpose:

Suggested Action

Examples:

Apply to Position

Review Opportunity

Resume Update Suggested

-----
Visual Weight:

Medium

Color:

Signal Cyan

-----
## <a name="level-3"></a>Level 3
Action Required

Purpose:

User intervention needed

Examples:

Follow-Up Due

Application Deadline

Interview Preparation Needed

-----
Visual Weight:

High

Color:

Amber

-----
## <a name="level-4"></a>Level 4
Critical

Purpose:

Immediate attention

Examples:

Opportunity Closing Soon

Interview Conflict

Submission Failure

-----
Visual Weight:

Highest

Color:

Red

-----
# <a name="notification-ordering"></a>Notification Ordering
Critical

↓

Action Required

↓

Recommendation

↓

Informational

-----
# <a name="governance-rule-1"></a>Governance Rule
Severity reflects urgency.

Not importance.

Atlas recommendations may be strategically important while remaining lower severity than an approaching deadline.

-----
# <a name="freeze-recommendation"></a>Freeze Recommendation
The following elements are now considered sufficiently specified for implementation:

- Grid System
- Spacing System
- Typography System
- Color Architecture
- Cyan Governance
- Sidebar
- Context Panel
- Card System
- Recommendation Cards
- Empty States
- Notification Hierarchy
- Status System
- Responsive Rules

Package 1 may now be considered implementation-ready and eligible for design-system freeze pending governance approval.
