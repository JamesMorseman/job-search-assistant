# ATLAS Recommendation Card v1.0 — Production Candidate

## Visual Description

The Recommendation Card appears as a calm intelligence object within the Command Center or Intelligence workspace.

It immediately communicates:

1. What Atlas recommends
2. Why Atlas recommends it
3. What the user can do next

The card should feel:

* deliberate
* intelligent
* trustworthy
* high-value

It should not feel:

* urgent
* promotional
* warning-oriented
* gamified

Visually, the card sits on a Deep Navy surface with a slightly elevated panel.

Atlas Blue establishes structure.

Signal Cyan appears only as a small intelligence marker.

The card should visually read:

```text
Atlas has an idea worth considering.
```

not

```text
You need to do this now.
```

---

## Layout Anatomy

```text
┌──────────────────────────────────────────────┐
│ ◉ APPLY                           High       │
│                                    Confidence│
│                                              │
│ Apply to Structural Engineer I               │
│                                              │
│ Atlas identified this position as a strong   │
│ match based on your profile and preferences. │
│                                              │
│ Why Atlas recommends this:                   │
│                                              │
│ • Strong structural focus                    │
│ • Matches geographic preferences             │
│ • Salary above target range                  │
│                                              │
│ ┌──────────────┐                             │
│ │Review Position│                            │
│ └──────────────┘                             │
│                                              │
│ Ask Atlas why                 Dismiss        │
└──────────────────────────────────────────────┘
```

---

## Information Hierarchy

### Level 1

Recommendation Title

```text
Apply to Structural Engineer I
```

Largest element.

Primary focal point.

---

### Level 2

Reasoning

```text
Strong structural focus
Matches geographic preferences
Salary above target range
```

Provides justification.

---

### Level 3

Primary Action

```text
Review Position
```

Clearly visible.

---

### Level 4

Confidence

```text
High Confidence
```

Supporting signal.

Never dominant.

---

### Level 5

Secondary Actions

```text
Ask Atlas why
Dismiss
```

Available but visually restrained.

---

## Spacing System

Based on Design System v1.1

### Card Padding

24px

---

### Header → Title

16px

---

### Title → Summary

16px

---

### Summary → Reasoning

20px

---

### Reasoning → Actions

24px

---

### Internal List Spacing

8px

---

### Card Width

Preferred:

420–520px

---

### Card Height

Content-driven.

Minimum:

280px

---

## Color Usage

### Background

Deep Navy

Primary card surface.

---

### Border

Subtle Atlas Blue

1px

Low contrast.

---

### Recommendation Marker

Signal Cyan

Small circular signal indicator.

Example:

```text
◉ APPLY
```

Only the marker uses cyan.

---

### Title

White

High contrast.

---

### Reasoning

Light neutral text.

---

### Confidence Label

Atlas Blue text

Small signal accent.

---

### Primary Button

Atlas Blue

Filled.

---

### Secondary Actions

Text only.

---

### Cyan Usage Limit

Maximum:

10% visual weight

Used only for:

* recommendation marker
* confidence indicator
* Atlas intelligence references

No cyan backgrounds.

No cyan buttons.

No cyan panels.

---

## Confidence Presentation

### Visual Form

```text
◉ High Confidence
```

Small signal marker.

Compact label.

---

### Placement

Upper right.

Header region.

---

### Behavior

Confidence supports.

Confidence never sells.

No:

* percentages
* scores
* rankings
* numeric certainty

---

## Interaction States

### Default

Subtle elevation.

No motion.

---

### Hover

Elevation +1 level.

Border slightly brighter.

100ms.

---

### Focus

Visible Atlas Blue outline.

Accessibility compliant.

---

### Selected

Persistent blue outline.

Context Panel opens.

---

### Loading

Recommendation skeleton.

Signal acquisition animation.

---

### Dismissed

Removed from primary surfaces.

Stored in recommendation history.

---

### Expired

Gray metadata state.

Actions removed.

Reason shown.

---

## Actions

### Primary

Review Position

Atlas Blue button.

Most prominent interactive element.

---

### Secondary

Ask Atlas why

Text action.

Signal Cyan text accent permitted.

Launches Ask Atlas with recommendation context attached.

---

### Dismiss

Lowest visual weight.

Text only.

No icon.

No emphasis.

---

## Command Center Placement

Recommended location:

Top Zone

Immediately below Action Queue.

Maximum visible:

3–5 Recommendation Cards.

---

### Ordering

1. High Confidence
2. Strong Signal
3. Review Recommended
4. Emerging Signal

---

## Emotional Outcome

A user should see this card and think:

```text
Atlas found something worth my attention.
I understand why.
I know what to do next.
```

They should not feel:

```text
I'm behind.

I'm missing something.

The system is pressuring me.
```

The Recommendation Card succeeds when intelligence feels useful, explainable, and actionable without becoming urgent or intrusive.
