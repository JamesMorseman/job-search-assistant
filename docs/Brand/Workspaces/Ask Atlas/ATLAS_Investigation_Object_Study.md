# ATLAS Investigation Object Study

**Owner:** Sara — Visual Design
**Authority:** Ask Atlas Workspace Study v1
**Status:** Object Definition Study

---

# Core Observation

The Ask Atlas architecture is now substantially resolved.

Ask Atlas is not:

```text
Chat
```

Ask Atlas is not:

```text
Assistant
```

Ask Atlas is not:

```text
Conversation
```

Ask Atlas is:

```text
Investigation
```

The remaining question is:

```text
What is the object of Investigation?
```

Radar found:

```text
Opportunity Signal
```

Pipeline found:

```text
Opportunity Flow
```

Intelligence found:

```text
Atlas Perspective
```

Ask Atlas now requires an equivalent object.

---

# Evaluation A

## Investigation Thread

### Concept

The conversation itself becomes the object.

Example:

```text
Investigation Thread

Why does Atlas prefer transportation firms?

Question
↓
Evidence
↓
Reasoning
↓
Conclusion
```

---

## Strengths

Natural.

Easy to understand.

Compatible with existing chat models.

Supports long-running investigations.

---

## Weaknesses

Feels conversational.

Feels close to:

```text
Chat history
```

or

```text
Message thread
```

which immediately weakens differentiation.

Users begin thinking:

```text
Conversation
```

rather than:

```text
Investigation
```

---

## Scalability

Technically excellent.

Experientially weak.

---

## Assessment

Useful internal structure.

Not strong enough to become the primary object.

---

# Evaluation B

## Investigation Case

### Concept

Every inquiry becomes a Case.

Examples:

```text
WSP Transportation Evaluation

Bridge Career Path Assessment

Seattle Relocation Analysis

Interview Preparation Strategy
```

---

## Strengths

Immediately communicates:

```text
Active investigation
```

Feels professional.

Feels mission-control aligned.

Feels distinct from generic chat.

Supports persistence.

Supports history.

Supports evidence gathering.

Supports future AI capabilities.

---

## Weaknesses

Can feel overly formal.

Risk of becoming:

```text
Case Management Software
```

if pushed too far.

Requires careful language design.

---

## Scalability

Excellent.

Works equally well for:

* opportunities
* recommendations
* interviews
* career planning
* strategic decisions

---

## Assessment

Strong candidate.

---

# Evaluation C

## Investigation Brief

### Concept

Atlas produces Briefs as outputs.

Example:

```text
Investigation Brief

Question

Should I pursue WSP?

Findings

Strong transportation alignment.

High interview likelihood.

Conclusion

Pursue.
```

---

## Strengths

Creates durable artifacts.

Easy to save.

Easy to reference later.

Supports decision making.

---

## Weaknesses

Same issue identified in Intelligence:

A Brief is a format.

Not an object.

It describes output.

Not the thing itself.

---

## Scalability

Excellent.

But secondary.

---

## Assessment

Should exist.

Should not become the primary Investigation object.

---

# Alternative Exploration

The key realization:

People do not enter Ask Atlas seeking conversation.

They enter Ask Atlas seeking resolution.

The emotional flow is:

```text
Uncertainty
↓
Investigation
↓
Understanding
↓
Decision
```

The object should embody that journey.

---

# Proposed Object

## Atlas Case

Definition:

```text
A structured investigation into a question,
decision, opportunity, or recommendation.
```

---

# Why Case Works

Signals answer:

```text
What exists?
```

Perspectives answer:

```text
What does it mean?
```

Cases answer:

```text
What should I understand?
```

This creates a clean conceptual progression.

---

# Example

```text
Atlas Case

Transportation Firm Evaluation

Question

Should I prioritize transportation-focused firms?

Perspective Referenced

Transportation specialization is outperforming
general civil hiring.

Evidence

62% of interviews originated from
transportation-focused employers.

Findings

Current market conditions favor specialization.

Conclusion

Transportation firms should be prioritized.
```

---

# Why Case Is Stronger Than Thread

Thread describes:

```text
Communication
```

Case describes:

```text
Investigation
```

Ask Atlas owns investigation.

Therefore:

```text
Case
```

is the more natural object.

---

# Why Case Is Stronger Than Brief

Brief is:

```text
Output
```

Case is:

```text
Process
```

Ask Atlas fundamentally owns process.

The object should therefore be process-oriented.

---

# Object Anatomy

## Atlas Case

### Question

The initiating uncertainty.

Example:

```text
Should I pursue this role?
```

---

### Context

Relevant opportunities.

Relevant recommendations.

Relevant perspectives.

Relevant applications.

---

### Evidence

Observed facts.

Referenced opportunities.

Referenced intelligence.

---

### Findings

What Atlas discovered.

Not yet a recommendation.

---

### Conclusion

Atlas understanding.

---

### Recommended Next Step

Optional.

Not always present.

---

### Investigation History

Persistent record of reasoning.

---

# Relationship To Perspectives

Perspective:

```text
Atlas understanding.
```

Case:

```text
Investigation of that understanding.
```

Flow:

```text
Lens
↓
Perspective
↓
Case
```

---

# Relationship To Opportunities

Signals often initiate Cases.

Example:

```text
Opportunity Signal
↓
Why is this interesting?
↓
Atlas Case
```

Cases become the mechanism through which opportunities are investigated.

---

# Relationship To Atlas Briefs

This resolves the Brief problem.

Case becomes:

```text
The object.
```

Brief becomes:

```text
The presentation format.
```

Equivalent to:

```text
Perspective
↓
Perspective Brief

Case
↓
Investigation Brief
```

---

# Relationship To Conversations

Conversation becomes a mechanism.

Not the object.

Important distinction:

Wrong model:

```text
Conversation
↓
Understanding
```

Recommended model:

```text
Case
↓
Conversation
↓
Understanding
```

Conversation serves the Case.

The Case does not serve the conversation.

This is what prevents Ask Atlas from becoming a chatbot.

---

# Final Recommendation

## Primary Investigation Object

### Atlas Case

The Ask Atlas workspace should be organized around Cases.

Not Threads.

Not Chats.

Not Conversations.

---

## Supporting Object

### Investigation Brief

The durable artifact produced by a completed Case.

---

## Final Architecture

```text
ATLAS scans.
↓
Opportunity Signal

Pipeline executes.
↓
Opportunity Flow

Atlas interprets.
↓
Atlas Perspective

Ask Atlas investigates.
↓
Atlas Case

Ask Atlas communicates.
↓
Investigation Brief
```

This is the first model that gives Ask Atlas a native object that is as distinct and defensible as:

```text
Opportunity Signal
Opportunity Flow
Atlas Perspective
```

while avoiding the trap of becoming merely another AI chat interface.
