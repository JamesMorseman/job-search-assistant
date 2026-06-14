# Firm Repository Governance Specification

**Status:** Planning Document
**Phase:** Phase 3 — Firm Repository
**Audience:** Repository reviewers, approvers, and maintainers

---

## Purpose

This document defines the governance model for the Firm Repository: the rules, standards, and procedures that determine how firm profiles are created, reviewed, approved, maintained, and retired.

The Firm Repository stores intelligence about prospective employers — including benefit offerings, career trajectory patterns, and ATS behavior — that directly influences job search decisions. Errors, stale data, or unsupported claims in this repository have real consequences: misallocated effort, inaccurate expectations, and poor applications to poorly-understood firms.

Governance exists to ensure that every approved profile reflects only what is genuinely known, at a stated confidence level, from credible evidence.

---

## Repository Ownership

**Repository Owner:** James Morseman

Responsibilities of the owner:
- Maintain this governance specification
- Grant and revoke reviewer access
- Resolve escalated disputes about evidence or approval
- Authorize exceptions to governance rules
- Conduct periodic audits of the governance process itself

There is one owner. Ownership is not delegated or shared.

---

## Reviewer Responsibilities

A reviewer is any person authorized to evaluate a draft firm profile and recommend it for approval or return it for revision.

Reviewers are responsible for:

- Reading the full draft profile before rendering any judgment
- Verifying that every claim in the profile is accompanied by a source citation
- Assessing whether cited sources meet the evidence standards defined in this document
- Identifying claims that are stated with more confidence than the evidence supports
- Identifying missing fields that are required for an acceptable profile
- Documenting their findings in writing before returning or approving a draft
- Disclosing any personal knowledge of a firm that might introduce bias (in either direction)

Reviewers are **not** responsible for:
- Independently researching claims not already present in the draft
- Filling in missing information on behalf of the drafter
- Approving profiles they have substantive reservations about in order to accelerate throughput

A reviewer who lacks sufficient time to conduct a thorough review should decline rather than conduct a superficial one.

---

## Approval Authority

Only the Repository Owner may approve a draft profile and transition it to approved status.

A reviewer may recommend approval, but that recommendation does not constitute approval.

The Repository Owner may not approve a profile that the Owner personally drafted without a second reviewer having reviewed it first.

---

## Evidence Standards

Evidence standards apply to every claim in a firm profile. A claim is any statement presented as factual: that a firm offers a benefit, that a firm uses a particular ATS, that a firm's promotion timeline is a given number of years.

### Benefit Intelligence

**Acceptable evidence:**
- Official firm benefits page on the firm's own website (with URL and access date)
- Employee handbook or benefits summary document obtained through the firm
- Offer letter or benefits documentation received directly from the firm
- Recruiter statement made in writing (email or message), with the recruiter's name and firm affiliation recorded
- Job posting that explicitly describes benefits, at the posting URL and access date

**Unacceptable evidence:**
- Anonymous employee review on Glassdoor, Blind, or comparable platforms without corroboration
- Word-of-mouth from a single personal contact without a written record
- Benefits information that appears on a third-party aggregator without an original source link
- Information more than 24 months old without re-verification

**Confidence expectations:**
- Evidence from the firm's own website or documents: High confidence permitted
- Evidence from recruiter communications: Medium confidence; note that recruiters may state benefits incorrectly and claims should be flagged as recruiter-sourced
- Evidence from job postings: Medium confidence for explicitly stated benefits; Low confidence for implied or inferred benefits
- Evidence from corroborated employee accounts: Low-to-medium confidence; must be noted as indirect

### Career Trajectory Intelligence

**Acceptable evidence:**
- Firm's published career ladder, leveling guide, or progression documentation
- LinkedIn profile analysis of multiple (minimum 3) confirmed employees who joined and were promoted at the firm, with promotion dates visible
- Recruiter statement made in writing about typical timelines
- Job posting language that specifies level expectations or progression language

**Unacceptable evidence:**
- Single anecdote from one employee or one contact
- Anonymous forum post without corroboration
- Assumptions drawn from the firm's size, industry, or reputation alone
- Information about a firm's former parent company applied to a post-acquisition entity

**Confidence expectations:**
- Documented career ladder: High confidence for the stated structure; note that lived experience may diverge from documentation
- LinkedIn analysis of 3+ employees: Medium confidence; note that visible promotions are a non-random sample
- Recruiter statements: Low-to-medium confidence; recruiters present their firm favorably
- Single data point from any source: Insufficient for any confidence level; must not appear as a standalone claim

### ATS Intelligence

**Acceptable evidence:**
- Direct observation of the firm's application portal (recorded with URL and access date)
- Explicit statement in a recruiter communication identifying the ATS by name
- Job posting that names the ATS platform in the application instructions
- Confirmed report from a contact who applied through the firm's system within the past 12 months, with the contact's name recorded

**Unacceptable evidence:**
- Inference from the firm's industry, size, or tech stack
- Outdated reports (more than 18 months old) without confirmation that the ATS has not changed
- Aggregator databases of ATS usage without a verifiable original source

**Confidence expectations:**
- Direct portal observation: High confidence for the ATS name; note that firms may use multiple ATS systems across regions or roles
- Named recruiter confirmation: Medium confidence
- Contact report: Medium confidence if within 12 months; Low confidence if 12–18 months old
- All other sources: Low confidence; must be explicitly flagged as unverified

---

## Source Hierarchy

Sources are ranked by trustworthiness. When sources conflict, higher-ranked sources take precedence unless the reviewer documents a specific reason to weigh the lower-ranked source more heavily.

1. **Primary firm documents** — Official firm websites, employee handbooks, offer letters, and published career ladders. The firm itself is the authoritative source on its own policies, with the limitation that published materials may lag internal reality.

2. **Direct firm communications** — Written communications from recruiters or HR representatives at the firm, with the communicant's name and role recorded. Ranked below primary documents because recruiters may be mistaken or incentivized to present the firm favorably.

3. **Verified personal contacts** — Written statements from named individuals known to the reviewer who have direct, recent experience with the firm. Ranked below firm communications because contact knowledge may be role-specific, team-specific, or outdated.

4. **Structured observations** — LinkedIn analysis, portal observations, or other structured first-party data collection. Ranked here because observations are accurate but may be incomplete (LinkedIn shows only what is public; portals show only what one path through the process reveals).

5. **Job postings** — Useful for ATS and role-level claims; less reliable for benefits or culture claims because postings are recruiting materials and may be aspirational.

6. **Employer review platforms** (Glassdoor, Blind, Levels.fyi, etc.) — May provide signal but carry significant noise. Anonymous, self-selected, potentially unrepresentative. Acceptable only as corroborating evidence for claims already supported by higher-ranked sources, or as Low-confidence flagged claims.

7. **Forum discussions, social media, and other informal sources** — Lowest trustworthiness. May be used only to generate hypotheses for investigation via higher-ranked sources. Must never appear as standalone evidence for an approved claim.

---

## Approval Requirements

A draft profile may not be approved unless all of the following conditions are satisfied:

1. **Completeness:** The profile meets the definition of an acceptable profile (see Data Quality Standards).

2. **Evidence coverage:** Every claim in the profile is accompanied by at least one source citation meeting the evidence standards for that claim type.

3. **Confidence calibration:** Every claim is accompanied by an explicit confidence level (High, Medium, or Low). No claim carries a confidence level higher than its evidence warrants.

4. **Source dating:** Every source citation includes an access or observation date. No claim relies exclusively on undated sources.

5. **Reviewer sign-off:** At least one reviewer has evaluated the draft and documented their findings. If the reviewer recommended revision, those revisions have been completed and reviewed.

6. **Owner review:** The Repository Owner has reviewed the profile after any reviewer sign-off.

7. **No unresolved conflicts:** Any conflicts between sources have been resolved using the Conflicting Evidence Workflow, with the resolution documented in the profile.

A profile that satisfies conditions 1–5 but has not completed conditions 6–7 is in a "reviewer-approved" intermediate state, not an approved state.

---

## Re-Verification Rules

Approved profiles are not permanent. Firms change their benefits, ATS systems, and career structures. An approved profile that is not periodically verified becomes unreliable over time without any visible indication.

### Standard Re-Verification Schedule

| Intelligence Type | Re-Verification Interval |
|---|---|
| Benefit intelligence | 12 months |
| ATS intelligence | 18 months |
| Career trajectory intelligence | 24 months |

The re-verification interval is measured from the date of the most recent source used to support each claim — not from the profile approval date. A claim supported by a source dated 10 months ago has 2 months remaining on a 12-month benefit clock regardless of when the profile was approved.

### Staleness Handling

When a claim's source exceeds its re-verification interval:

1. The claim is marked stale. It is not deleted and not immediately downgraded.

2. The profile's overall status is downgraded from Approved to Needs Re-Verification. It remains visible and usable, but any consumer of the profile is informed that it contains stale claims.

3. The Repository Owner is notified. Re-verification becomes a tracked obligation.

4. If re-verification is not completed within 90 days of the staleness date, the stale claims are downgraded to Low confidence and flagged explicitly.

5. If re-verification is not completed within 180 days of the staleness date, the profile is moved to Draft status and must go through the full approval process again.

### Re-Verification Scope

Re-verification is not a full re-research of the firm. It is a targeted check: does the previously cited source still say what it said, or has it changed? If the source has changed, the claim must be updated to reflect current information before re-verification is considered complete.

---

## Conflicting Evidence Workflow

Conflicts arise when two credible sources make incompatible claims about the same fact. The correct response is not to pick the more favorable claim or the more recent claim automatically.

### Step 1: Document the conflict

Record both claims, both sources, and the nature of the disagreement in the profile. A conflict must be visible, not resolved silently.

### Step 2: Rank the sources

Apply the Source Hierarchy. If one source outranks the other and the higher-ranked source is sufficiently recent, prefer it and document why.

### Step 3: Consider specificity

A specific claim from a lower-ranked source may be more credible than a general claim from a higher-ranked source. A named employee's account of their specific team's ATS experience may be more accurate than a firm's general website description that hasn't been updated. Document this reasoning explicitly if it overrides the source hierarchy.

### Step 4: Consider recency

Where sources are otherwise comparable, prefer more recent sources. Document the dates of both sources.

### Step 5: Escalate if unresolvable

If the conflict cannot be resolved under steps 2–4, escalate to the Repository Owner. The Owner may:
- Declare one source authoritative for documented reasons
- Record both positions as competing claims at their respective confidence levels
- Commission additional research to resolve the conflict before approval

### Step 6: Never suppress conflicts

A conflict that is resolved by choosing one source over another must still be documented. The losing claim, its source, and the resolution rationale must be preserved in the profile's audit record.

---

## Auditability Requirements

The following information must always be preserved, regardless of subsequent changes to the profile:

1. **Every source ever cited** — Source URL or description, access date, and the claim(s) it supported at the time of citation. Sources are never deleted from the record, even if the claim they supported has been updated or removed.

2. **Every version of every claim** — When a claim is updated, the prior claim text, its effective date range, and the reason for the update are preserved.

3. **Every reviewer action** — Who reviewed, when, what their findings were, and what action they took (approved, returned for revision, escalated).

4. **Every approval and de-approval event** — Who approved, when, and what version they approved. If a profile is moved from Approved back to Draft or Needs Re-Verification, the reason is recorded.

5. **Every conflict and its resolution** — Per the Conflicting Evidence Workflow.

6. **Governance exceptions** — If the Repository Owner authorizes an exception to any rule in this specification, the exception is documented with a rationale.

Audit records are never edited. If an audit record contains an error (a typo, a misattributed source), a correction is appended rather than the original altered.

---

## Data Quality Standards

### Incomplete Profile

A profile is incomplete if any of the following are true:
- The firm name and legal entity are not recorded
- No benefit intelligence is present
- No ATS intelligence is present
- No career trajectory intelligence is present
- Any present claim lacks a source citation
- Any present claim lacks a confidence level
- The profile has not been reviewed by any reviewer

An incomplete profile may not advance to approved status under any circumstances.

### Acceptable Profile

A profile is acceptable if all of the following are true:
- All required fields are populated (firm name, legal entity, primary location, industry, headcount range)
- At least one benefit claim is present with a Medium or High confidence source
- At least one ATS claim is present with a Medium or High confidence source
- At least one career trajectory claim is present with any confidence level and a source citation
- All claims have source citations
- All claims have confidence levels
- No source exceeds its re-verification interval
- At least one reviewer has signed off

An acceptable profile may be approved.

### High-Quality Profile

A profile is high-quality if all of the following are true:
- All acceptable profile criteria are met
- Benefit intelligence covers at minimum: health insurance, PTO policy, remote work policy, and retirement benefits
- ATS intelligence includes the platform name and at least one observation about how the system behaves (screening questions, timeline, communication patterns)
- Career trajectory intelligence includes: typical time-to-promotion at the entry/mid level, and whether internal mobility is common or rare
- At least two independent sources are cited for each major claim category
- No claim relies exclusively on employer review platforms or informal sources
- All Medium and High confidence claims are supported by sources ranked 1–4 in the Source Hierarchy
- The profile has been reviewed by at least one reviewer and approved by the Repository Owner
- No claims are stale

A high-quality profile is the target state. Profiles should not be considered final at the acceptable threshold unless research capacity is genuinely exhausted.

---

## Governance Risks

The following operational mistakes are likely without explicit attention.

**Claim drift under time pressure.** When a profile needs to be finished quickly, Low-confidence claims get labeled Medium. Confidence calibration erodes and the labels become meaningless. Risk is highest during bulk profile creation.

**Source citation as ritual.** Reviewers may verify that a source is cited without verifying that the source actually supports the claim. A URL that returns a 404, a job posting that doesn't mention the claimed benefit, or a review that contradicts the claim may pass review if no one reads the source.

**Staleness invisibility.** Once a profile is approved, the pressure to re-verify it is low because nothing visibly changes. Profiles will drift out of date silently unless the re-verification schedule is actively enforced.

**Single-contact dependency.** Career trajectory intelligence in particular tends to be built from one or two contacts with direct experience. When a claim rests on a single named contact, and that contact is later found to be mistaken or to have had an atypical experience, the entire intelligence category may need to be rebuilt.

**Conflict suppression.** When two sources disagree and one is clearly more convenient, reviewers may be tempted to apply the hierarchy mechanically to justify the preferred source rather than genuinely engaging with the conflict. The result is a formally resolved but substantively unresolved conflict.

**Reviewer workload concentration.** If one reviewer handles the majority of profile reviews, their biases, blind spots, and time pressures become the bottleneck. Review quality degrades without anyone noticing because there is no comparison baseline.

**Exception proliferation.** The Repository Owner will be asked to authorize exceptions when research stalls or a profile needs to advance quickly. If exceptions are granted without documentation, they become informal precedent and the governance standards gradually shift downward.

---

## Recommended Governance Rules

The following rules are recommended as the operational governance baseline.

**Rule 1 — No claim without a source.** Every claim in an approved profile must be accompanied by a source citation. This rule has no exceptions.

**Rule 2 — No confidence without calibration.** Every claim in an approved profile must carry a confidence level. Confidence levels must reflect the quality and rank of the supporting source, not the desirability of the claim.

**Rule 3 — Sources age.** Every source citation must include an access or observation date. Sources must be re-verified on the schedule defined in this document. Stale sources reduce the profile's overall confidence, visibly and automatically.

**Rule 4 — Conflicts must be visible.** When sources disagree, the conflict and its resolution are recorded in the profile. Conflicts resolved silently — by simply choosing one source — violate this rule.

**Rule 5 — One reviewer minimum.** No profile may be approved without at least one reviewer having evaluated it and documented their findings. The Repository Owner may not waive this rule for their own drafts.

**Rule 6 — Audit records are permanent.** Source citations, claim histories, reviewer actions, and conflict records are never deleted or edited in place. Corrections are appended. This rule has no exceptions.

**Rule 7 — Exceptions require documentation.** When the Repository Owner authorizes an exception to any rule, the exception is recorded with the rule number, the rationale, and the date. Undocumented exceptions do not exist.

**Rule 8 — Acceptable is not the target.** A profile meeting the acceptable threshold may be approved, but the review process should identify what is missing for high-quality status and record it as a known gap. Profiles should not be considered finished at the acceptable threshold without a documented reason.

**Rule 9 — Re-verification is mandatory.** A profile in Needs Re-Verification status is not an approved profile. It must be treated as provisional until re-verification is complete. Consumers of the repository must be aware of this status.

**Rule 10 — Governance itself is reviewed.** This specification is reviewed annually or when a significant operational failure makes it clear that a rule is missing, ambiguous, or counterproductive. Review is conducted by the Repository Owner and documented as a governance event.
