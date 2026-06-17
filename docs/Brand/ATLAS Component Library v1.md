# <a name="atlas-component-library-v1.0"></a>ATLAS Component Library v1.0
Status: Canonical UI Component Specification\
Owner: Sara — Brand & Product Design\
Authority: Project Master (Ash)

-----
# <a name="purpose"></a>Purpose
This document defines the official reusable UI components of ATLAS.

The objective is to ensure:

- implementation consistency
- design consistency
- component reuse
- predictable workflows

Future implementation teams should construct ATLAS using these components rather than inventing new interface objects.

-----
# <a name="component-classification"></a>Component Classification
## <a name="tier-1"></a>Tier 1
Core System Components

Used throughout the application.

-----
## <a name="tier-2"></a>Tier 2
Workspace Components

Specific to major workspaces.

-----
## <a name="tier-3"></a>Tier 3
Supporting Components

Contextual and utility objects.

-----
# <a name="global-components"></a>GLOBAL COMPONENTS
-----
# <a name="sidebar"></a>Sidebar
## <a name="purpose-1"></a>Purpose
Primary application navigation.

-----
## <a name="required-fields"></a>Required Fields
Navigation Items

Current Active Item

Application Logo

-----
## <a name="optional-fields"></a>Optional Fields
Notification Badges

Collapse Toggle

Workspace Shortcuts

-----
## <a name="actions"></a>Actions
Navigate

Collapse

Expand

-----
## <a name="states"></a>States
Default

Collapsed

Expanded

Hover

Selected

-----
## <a name="priority"></a>Priority
Tier 1

-----
# <a name="top-navigation-bar"></a>Top Navigation Bar
## <a name="purpose-2"></a>Purpose
Global awareness and utility actions.

-----
## <a name="required-fields-1"></a>Required Fields
Current Workspace

Global Search Access

Notification Access

-----
## <a name="optional-fields-1"></a>Optional Fields
User Profile

Quick Actions

Connection Status

-----
## <a name="actions-1"></a>Actions
Search

Open Notifications

Launch Ask Atlas

-----
## <a name="priority-1"></a>Priority
Tier 1

-----
# <a name="search-surface"></a>Search Surface
## <a name="purpose-3"></a>Purpose
Universal discovery mechanism.

-----
## <a name="required-fields-2"></a>Required Fields
Search Input

Results Container

-----
## <a name="optional-fields-2"></a>Optional Fields
Filters

Recent Searches

Suggested Searches

-----
## <a name="actions-2"></a>Actions
Search

Filter

Open Result

-----
## <a name="priority-2"></a>Priority
Tier 1

-----
# <a name="context-panel"></a>Context Panel
## <a name="purpose-4"></a>Purpose
Contextual detail surface.

-----
## <a name="required-fields-3"></a>Required Fields
Selected Object

Content Region

-----
## <a name="optional-fields-3"></a>Optional Fields
Recommendations

Timeline

Documents

-----
## <a name="actions-3"></a>Actions
Expand

Collapse

Open Related Content

Launch Ask Atlas

-----
## <a name="priority-3"></a>Priority
Tier 1

-----
# <a name="notification-center"></a>Notification Center
## <a name="purpose-5"></a>Purpose
Aggregated event awareness.

-----
## <a name="required-fields-4"></a>Required Fields
Notification List

Severity Indicator

Timestamp

-----
## <a name="optional-fields-4"></a>Optional Fields
Actions

Related Objects

-----
## <a name="actions-4"></a>Actions
Dismiss

Open

Filter

Mark Read

-----
## <a name="priority-4"></a>Priority
Tier 1

-----
# <a name="status-indicator"></a>Status Indicator
## <a name="purpose-6"></a>Purpose
Communicate state.

-----
## <a name="required-fields-5"></a>Required Fields
State Label

Icon

-----
## <a name="optional-fields-5"></a>Optional Fields
Timestamp

Severity

-----
## <a name="states-1"></a>States
Success

Warning

Error

Pending

Neutral

-----
## <a name="priority-5"></a>Priority
Tier 1

-----
# <a name="empty-state"></a>Empty State
## <a name="purpose-7"></a>Purpose
Communicate operational absence.

-----
## <a name="required-fields-6"></a>Required Fields
Title

Description

-----
## <a name="optional-fields-6"></a>Optional Fields
Suggested Action

Atlas Guidance

-----
## <a name="priority-6"></a>Priority
Tier 1

-----
# <a name="modal"></a>Modal
## <a name="purpose-8"></a>Purpose
Focused workflow interruption.

-----
## <a name="required-fields-7"></a>Required Fields
Title

Content

Primary Action

-----
## <a name="optional-fields-7"></a>Optional Fields
Secondary Action

Context

-----
## <a name="priority-7"></a>Priority
Tier 1

-----
# <a name="confirmation-dialog"></a>Confirmation Dialog
## <a name="purpose-9"></a>Purpose
Confirm significant action.

-----
## <a name="required-fields-8"></a>Required Fields
Action Description

Confirm Action

Cancel Action

-----
## <a name="priority-8"></a>Priority
Tier 1

-----
# <a name="command-center-components"></a>COMMAND CENTER COMPONENTS
-----
# <a name="action-queue-card"></a>Action Queue Card
## <a name="purpose-10"></a>Purpose
Surface actionable work.

-----
## <a name="information-hierarchy"></a>Information Hierarchy
Action

Due Date

Context

Status

-----
## <a name="required-fields-9"></a>Required Fields
Title

Action Type

Due Date

-----
## <a name="optional-fields-8"></a>Optional Fields
Related Opportunity

Related Company

-----
## <a name="actions-5"></a>Actions
Open

Complete

Dismiss

-----
# <a name="recommendation-card"></a>Recommendation Card
## <a name="purpose-11"></a>Purpose
Atlas-generated action recommendation.

-----
## <a name="information-hierarchy-1"></a>Information Hierarchy
Recommendation

Reason

Suggested Action

Confidence

-----
## <a name="required-fields-10"></a>Required Fields
Recommendation

Reasoning Summary

Suggested Action

Confidence Score

-----
## <a name="actions-6"></a>Actions
Accept

Review

Dismiss

-----
# <a name="follow-up-card"></a>Follow-Up Card
## <a name="purpose-12"></a>Purpose
Track required outreach.

-----
## <a name="required-fields-11"></a>Required Fields
Company

Position

Follow-Up Date

-----
## <a name="actions-7"></a>Actions
Complete

Reschedule

Open Opportunity

-----
# <a name="interview-card"></a>Interview Card
## <a name="purpose-13"></a>Purpose
Track upcoming interviews.

-----
## <a name="required-fields-12"></a>Required Fields
Company

Position

Interview Date

-----
## <a name="optional-fields-9"></a>Optional Fields
Interview Type

Preparation Notes

-----
## <a name="actions-8"></a>Actions
Prepare

Reschedule

Open Details

-----
# <a name="opportunity-alert-card"></a>Opportunity Alert Card
## <a name="purpose-14"></a>Purpose
Surface newly detected opportunities.

-----
## <a name="required-fields-13"></a>Required Fields
Position

Company

Signal Score

-----
## <a name="optional-fields-10"></a>Optional Fields
Reason Detected

-----
## <a name="actions-9"></a>Actions
Review

Save

Ignore

-----
# <a name="pipeline-snapshot-card"></a>Pipeline Snapshot Card
## <a name="purpose-15"></a>Purpose
Summarize application pipeline.

-----
## <a name="required-fields-14"></a>Required Fields
Application Counts

Status Breakdown

-----
## <a name="optional-fields-11"></a>Optional Fields
Trend Indicators

-----
# <a name="system-health-card"></a>System Health Card
## <a name="purpose-16"></a>Purpose
Platform operational awareness.

-----
## <a name="required-fields-15"></a>Required Fields
System Status

Source Status

-----
## <a name="optional-fields-12"></a>Optional Fields
Warnings

-----
# <a name="radar-components"></a>RADAR COMPONENTS
-----
# <a name="opportunity-signal-card"></a>Opportunity Signal Card
## <a name="purpose-17"></a>Purpose
Represent discovered opportunity.

-----
## <a name="required-fields-16"></a>Required Fields
Title

Company

Location

Signal Score

-----
## <a name="optional-fields-13"></a>Optional Fields
Salary

Remote Status

Tags

-----
## <a name="actions-10"></a>Actions
Track

Review

Compare

-----
# <a name="opportunity-detail-surface"></a>Opportunity Detail Surface
## <a name="purpose-18"></a>Purpose
Full opportunity review.

-----
## <a name="required-fields-17"></a>Required Fields
Description

Requirements

Company

Location

-----
## <a name="optional-fields-14"></a>Optional Fields
Benefits

Notes

Recommendations

-----
# <a name="company-intelligence-card"></a>Company Intelligence Card
## <a name="purpose-19"></a>Purpose
Company awareness.

-----
## <a name="required-fields-18"></a>Required Fields
Company Name

Status

Summary

-----
## <a name="optional-fields-15"></a>Optional Fields
Hiring Activity

Watchlist Status

-----
# <a name="watchlist-component"></a>Watchlist Component
## <a name="purpose-20"></a>Purpose
Monitor tracked entities.

-----
## <a name="required-fields-19"></a>Required Fields
Tracked Items

Status

-----
## <a name="actions-11"></a>Actions
Remove

Review

Prioritize

-----
# <a name="source-health-component"></a>Source Health Component
## <a name="purpose-21"></a>Purpose
Monitor ingestion sources.

-----
## <a name="required-fields-20"></a>Required Fields
Source Name

Status

Last Update

-----
# <a name="opportunity-comparison-surface"></a>Opportunity Comparison Surface
## <a name="purpose-22"></a>Purpose
Compare opportunities side-by-side.

-----
## <a name="required-fields-21"></a>Required Fields
Two or More Opportunities

Comparison Metrics

-----
## <a name="actions-12"></a>Actions
Rank

Save

Review

-----
# <a name="pipeline-components"></a>PIPELINE COMPONENTS
-----
# <a name="application-card"></a>Application Card
## <a name="purpose-23"></a>Purpose
Track single application.

-----
## <a name="required-fields-22"></a>Required Fields
Company

Position

Current Status

-----
## <a name="optional-fields-16"></a>Optional Fields
Notes

Timeline

-----
# <a name="pipeline-table"></a>Pipeline Table
## <a name="purpose-24"></a>Purpose
Operational management view.

-----
## <a name="required-fields-23"></a>Required Fields
Applications

Statuses

Dates

-----
## <a name="actions-13"></a>Actions
Sort

Filter

Open

-----
# <a name="timeline-component"></a>Timeline Component
## <a name="purpose-25"></a>Purpose
Display chronological progression.

-----
## <a name="required-fields-24"></a>Required Fields
Events

Dates

-----
## <a name="optional-fields-17"></a>Optional Fields
Notes

Documents

-----
# <a name="interview-milestone"></a>Interview Milestone
## <a name="purpose-26"></a>Purpose
Represent interview stage.

-----
## <a name="required-fields-25"></a>Required Fields
Interview Date

Status

-----
# <a name="offer-milestone"></a>Offer Milestone
## <a name="purpose-27"></a>Purpose
Represent offer stage.

-----
## <a name="required-fields-26"></a>Required Fields
Offer Status

Decision Date

-----
# <a name="status-change-component"></a>Status Change Component
## <a name="purpose-28"></a>Purpose
Record status transitions.

-----
## <a name="required-fields-27"></a>Required Fields
Previous Status

Current Status

Timestamp

-----
# <a name="intelligence-components"></a>INTELLIGENCE COMPONENTS
-----
# <a name="insight-card"></a>Insight Card
## <a name="purpose-29"></a>Purpose
Present analytical observation.

-----
## <a name="required-fields-28"></a>Required Fields
Insight

Supporting Evidence

-----
## <a name="optional-fields-18"></a>Optional Fields
Trend Data

-----
# <a name="skill-gap-card"></a>Skill Gap Card
## <a name="purpose-30"></a>Purpose
Identify improvement opportunities.

-----
## <a name="required-fields-29"></a>Required Fields
Skill

Gap Severity

Recommendation

-----
# <a name="career-trend-card"></a>Career Trend Card
## <a name="purpose-31"></a>Purpose
Surface longitudinal patterns.

-----
## <a name="required-fields-30"></a>Required Fields
Trend

Interpretation

-----
# <a name="decision-history-component"></a>Decision History Component
## <a name="purpose-32"></a>Purpose
Track recommendation outcomes.

-----
## <a name="required-fields-31"></a>Required Fields
Recommendation

Outcome

Timestamp

-----
# <a name="confidence-indicator"></a>Confidence Indicator
## <a name="purpose-33"></a>Purpose
Communicate certainty.

-----
## <a name="required-fields-32"></a>Required Fields
Confidence Level

-----
## <a name="formats"></a>Formats
Low

Medium

High

Very High

-----
# <a name="ask-atlas-components"></a>ASK ATLAS COMPONENTS
-----
# <a name="conversation-surface"></a>Conversation Surface
## <a name="purpose-34"></a>Purpose
Primary conversational interface.

-----
## <a name="required-fields-33"></a>Required Fields
Messages

Input Surface

-----
## <a name="optional-fields-19"></a>Optional Fields
Context References

Recommendations

-----
# <a name="suggested-prompt-component"></a>Suggested Prompt Component
## <a name="purpose-35"></a>Purpose
Accelerate interaction.

-----
## <a name="required-fields-34"></a>Required Fields
Prompt Text

-----
## <a name="actions-14"></a>Actions
Insert

Execute

-----
# <a name="referenced-opportunity-component"></a>Referenced Opportunity Component
## <a name="purpose-36"></a>Purpose
Attach opportunity context.

-----
## <a name="required-fields-35"></a>Required Fields
Opportunity Reference

-----
## <a name="actions-15"></a>Actions
Open

Compare

-----
# <a name="referenced-recommendation-component"></a>Referenced Recommendation Component
## <a name="purpose-37"></a>Purpose
Attach Atlas recommendation.

-----
## <a name="required-fields-36"></a>Required Fields
Recommendation Reference

-----
# <a name="context-attachment-component"></a>Context Attachment Component
## <a name="purpose-38"></a>Purpose
Provide conversation grounding.

-----
## <a name="supported-context"></a>Supported Context
Opportunity

Application

Company

Recommendation

Document

-----
# <a name="conversation-history-component"></a>Conversation History Component
## <a name="purpose-39"></a>Purpose
Preserve prior interactions.

-----
## <a name="required-fields-37"></a>Required Fields
Conversation List

Timestamp

-----
# <a name="shared-components"></a>SHARED COMPONENTS
These components are reusable across all workspaces.

-----
Recommendation Card

Status Indicator

Timeline Component

Confidence Indicator

Context Panel

Notification Center

Company Intelligence Card

Opportunity Signal Card

Referenced Opportunity Component

Referenced Recommendation Component

-----
# <a name="standard-component-states"></a>STANDARD COMPONENT STATES
All applicable components support:

Default

Hover

Focus

Selected

Expanded

Loading

Empty

Error

Disabled

-----
# <a name="state-behavior-rules"></a>State Behavior Rules
Hover

Visual emphasis only.

-----
Focus

Accessibility-first.

Visible at all times.

-----
Selected

Persistent state.

-----
Expanded

Reveals additional information.

-----
Loading

Uses approved ATLAS motion primitives.

-----
Empty

Operational awareness messaging.

-----
Error

Clear explanation.

Recovery path required.

-----
Disabled

Visible but inactive.

Reason must be understandable.

-----
# <a name="canonical-construction-rule"></a>Canonical Construction Rule
Future screens must be composed from this library before new components are created.

New components require justification that existing components cannot satisfy the use case.

The preferred ATLAS workflow is:

Reuse

↓

Extend

↓

Create New

This component library serves as the canonical source of truth for ATLAS interface construction across Command Center, Radar, Pipeline, Intelligence, and Ask Atlas.
