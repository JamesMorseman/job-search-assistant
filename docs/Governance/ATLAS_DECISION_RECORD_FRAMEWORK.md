# ATLAS Decision Record Framework

Status: DRAFT (standards foundation)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Governance Evolution — Package G1
Date: 2026-06-19

---

## Purpose

Stop rediscovering accepted decisions. This framework defines a lightweight,
category-tagged decision record format so that once a decision is accepted, it
lives in a durable record instead of being re-litigated from narrative or memory.

This framework defines the categories and the template only. It does NOT create
any decision records. Records are authored later, after team memory audits, so
that each record reflects accepted state rather than assumed state.

This framework is plain markdown. There is no engine.

---

## Decision Record Categories

```
VDR — Visual Decision Record
ADR — Architecture Decision Record
GDR — Governance Decision Record
PDR — Product Decision Record
CDR — Career/Evidence Decision Record
DDR — Documentation Decision Record
```

Category guidance:

- VDR — visual/reference/rendering decisions (e.g. Radar sweep behavior, tier
  color map, card composition).
- ADR — architecture/technical structure decisions (e.g. module boundaries, data
  flow, abstraction layers).
- GDR — governance/process decisions (e.g. what "pass" means, gate ordering,
  acceptance authority).
- PDR — product/feature decisions (e.g. what a surface is for, what it must show).
- CDR — career/evidence decisions specific to the job-search assistant domain
  (e.g. how evidence is captured or presented).
- DDR — documentation decisions (e.g. which gates a doc type requires before it
  may be published or exported).

Each record gets a category-prefixed, zero-padded sequential ID within its
category (e.g. GDR-001, VDR-001, VDR-002).

---

## Decision Record Template

Copy this block to author a record (later, not in G1).

```
# [CATEGORY-ID] Decision Title

Status:
Date:
Owner:
Decision:
Rationale:
Applies to:
Does not apply to:
Evidence:
Consequences:
Revisit condition:
Related records:
```

Field notes:

- Status — e.g. ACCEPTED, PROPOSED, SUPERSEDED (superseded records name their
  successor).
- Date — absolute date of acceptance.
- Owner — accepting authority (governance acceptance is Main Ash / user).
- Decision — the decision itself, stated plainly.
- Rationale — why this was decided.
- Applies to — the scope where the decision holds.
- Does not apply to — explicit non-scope, to prevent over-application.
- Evidence — what supports the decision (commits, references, audits, rulings).
- Consequences — what follows from the decision.
- Revisit condition — what would reopen the decision.
- Related records — cross-links to other records (by CATEGORY-ID).

---

## Candidate First Records (NOT YET CREATED)

The following are candidate records to author later, after team memory audits.
They are listed here only as a backlog. Do NOT create them in G1.

```
GDR-001 Technical Pass Is Not Visual Pass
VDR-001 Radar Card Continuous Sweep Exception
VDR-002 Track Removed From SignalCard
VDR-003 Radar Cyan/Blue Tier Map
DDR-001 Screenshot Docs Require Sara/P7P6/Leah/Cait/Main Ash Gates
```

Authoring rule: each candidate is created only after audit evidence confirms it
reflects accepted state. Until then it remains a backlog entry, not a record.

---

## Where Records Live

When records are created (in a later package), they will live under
`docs/Governance/` in a records location to be specified at authoring time (for
example, a `Records/` subfolder). G1 does not create that location or any record.
