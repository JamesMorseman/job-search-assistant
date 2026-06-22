# ATLAS Release Readiness Ladder

Status: CODIFICATION ONLY — no gate passed by this document
Owner: Main Ash / user
Maintained by: Anna Repo Agent (under explicit E3 authorization)
Initiative: ATLAS Governance Gate E3 — Package DOCS-RELEASE-READINESS-LADDER-01
Date authored: 2026-06-22 (this document reflects the corrected ladder as of this
authoring date; if the ladder is revised later, update this date rather than
silently editing the record)

---

## Purpose

ATLAS/JSA has three distinct release builds with different audiences, different
must-have requirements, and different stop conditions. Prior framing conflated
two of them: it described Build 1 as "private-only" and implied that
public/recruiter-facing readiness belonged to a later, more expansive build.
That framing was incorrect and is corrected here.

This document codifies the corrected three-build release-readiness ladder so
that future ATLAS/JSA gates — implementation, audit, visual, docs, and
governance acceptance — have one shared reference for which build is being
targeted, what each build requires, and how the builds depend on one another.

This document does not itself evaluate, pass, or authorize any build. It is a
reference ladder, written once, to be pointed at by later gate work.

---

## Non-Authorization Notice

This document does NOT authorize, and must never be cited as authorizing, any
of the following:

```
release of any build (Build 1, Build 2, or Build 3)
Rin sync
P7P6
screenshots
visual pass
implementation acceptance
public launch
recruiter release approval
monetization launch
```

This document is a reference ladder only. Authoring this ladder is a docs/
governance codification action, not a gate pass. Every gate named in this
document (release, Rin sync, P7P6, visual pass, implementation acceptance,
public launch, recruiter release approval, monetization launch) remains
unauthorized and unpassed until a separate, explicit acceptance object clears
it, per `ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`.

---

## Corrected Build Ladder Summary

```
Build 1: Jim Public/Recruiter-Facing Career-Services Build
  -> single user (Jim), externally presentable to recruiters/portfolio viewers
  -> NOT private-only; NOT a generalized multi-user product

Build 2: Friends-and-Family Trusted Tester Build
  -> small set of known, trusted testers beyond Jim
  -> adds tester onboarding, tester data boundaries, rollback/reset, feedback capture

Build 3: Full Public Expanded-User-Base / Potential Monetization Build
  -> broad/unknown user base, potential monetization
  -> adds multi-user productization, scalable ops, legal/privacy/billing readiness
```

| Build | Audience | Core addition over previous build | Monetization in scope? |
|---|---|---|---|
| Build 1 | Jim (public/recruiter-facing) | Public/recruiter-facing polish, claims discipline, privacy hygiene for a single user's career-services build | No |
| Build 2 | Friends & family trusted testers | Tester onboarding, tester data boundaries, rollback/reset, feedback capture | No |
| Build 3 | Full public / expanded user base | Multi-user productization, scalable onboarding/support, legal/privacy/billing readiness | If pursued |

Cross-cutting correction: public/recruiter-facing readiness is a Build 1
property. It is not deferred to Build 3. Build 3 is distinguished from Build 1
by user-base scale and productization/monetization, not by whether the build is
externally presentable — Build 1 is already externally presentable, to Jim's
recruiter/portfolio audience.

---

## Build 1: Jim Public/Recruiter-Facing Career-Services Build

checklist_id: `ENDSTATE-01_JIM_PUBLIC_RECRUITER_FACING_CAREER_SERVICES_BUILD`

### Goal

A polished public/recruiter-facing build that Jim can use directly for his own
career-services workflow, portfolio presentation, and job-search credibility.
This build is externally presentable for Jim — recruiters, hiring contacts, and
portfolio viewers may see it — but it is not a generalized multi-user product
and not a monetized SaaS release.

### Entry criteria

- A working end-to-end career-services workflow exists for Jim's own use.
- No outstanding known privacy/secrets exposure in the surfaces intended for
  presentation.
- Implementation work intended for this build has gone through normal repo
  implementation and is ready for audit (not yet accepted).

### Must-have features

- Public/recruiter-facing polish across any surface Jim intends to show.
- Implementation acceptance obtained before this build is claimed done.
- A visual pass obtained before this build's visual readiness is claimed.
- Cait-approved public/recruiter claims and career-material language.
- Rin-reviewed public/private documentation boundaries.
- Privacy/secrets/data hygiene appropriate to a single-user, externally-visible
  build.
- Public-safe screenshots only if separately authorized.
- Clear limitations and human-review language wherever the build makes claims
  about its own output quality or accuracy.
- Public-safe demo/sample evidence where evidence is needed for review.

### Must-not-include / must-not-imply

- No private profile, job, firm, resume, credential, env, database, generated-
  sensitive artifact, screenshot, or private agent memory exposed anywhere in
  the build or its supporting docs.
- Must not imply multi-user product readiness.
- Must not imply friends-and-family beta readiness.
- Must not imply full public product launch.
- Must not imply monetization readiness.
- Must not imply general customer support readiness.
- Must not imply SaaS/business compliance readiness.

### Privacy and data requirements

- Single-user (Jim) data model; no other user's data is in scope.
- No private profile, job, firm, resume, credential, env, database, or backup
  content exposed in any public/recruiter-facing surface.
- Data hygiene reviewed before any public-facing claim is made about the build.

### Docs requirements

- Public-facing documentation is reviewed for a clean public/private boundary
  (Rin-reviewed) before being treated as presentable.
- Internal/governance docs remain separate from anything shown to recruiters.

### Visual requirements

- A visual pass (per the visual governance standard in effect at the time) is
  required before visual readiness is claimed for this build.
- No visual pass is claimed or implied by this document.

### Testing requirements

- Implementation acceptance evidence (technical pass, repo readout pass) is
  required before this build is claimed done, per
  `ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`.

### Security/secrets requirements

- No secrets, credentials, or env values present in any surface intended for
  public/recruiter presentation.
- Secrets/data hygiene checked as part of implementation acceptance, not
  assumed.

### Claims and messaging requirements

- All public/recruiter-facing claims and career-material language require
  Cait approval before use.
- Prohibited public claims (as defined by Cait's claims policy) are not used.

### Release or non-release gate

No release, visual pass, or implementation acceptance for Build 1 is currently
passed or authorized. This document does not change that status; it only
defines what Build 1 requires once those gates are separately cleared.

### Agent owners

- Donut Lead: release ladder sequencing and package readiness for Build 1.
- Leah Lead: implementation safety, security/secrets hygiene, implementation
  acceptance evidence.
- Rin Lead: public/private docs boundary review for Build 1 documentation.
- Cait Lead: career evidence, claims policy, recruiter-facing language review.
- Sara Lead: visual governance and visual pass for Build 1 surfaces.
- Anna Repo Agent: repo implementation only after explicit E3-style
  authorization for each Build 1 work package.

### Acceptance evidence needed

- Implementation acceptance object (per `ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`).
- Visual pass acceptance object.
- Cait claims-policy review record.
- Rin public/private docs boundary review record.
- Privacy/secrets hygiene confirmation.

### Stop conditions

- Do not claim Build 1 is done without a recorded implementation acceptance
  object.
- Do not claim Build 1 visual readiness without a recorded visual pass.
- Do not present public/recruiter-facing claims without Cait approval.
- Do not expose private profile, job, firm, resume, credential, env, database,
  generated-sensitive artifact, screenshot, or private agent memory content.

---

## Build 2: Friends-and-Family Trusted Tester Build

checklist_id: `ENDSTATE-02_FRIENDS_AND_FAMILY_RELEASE`

### Goal

A controlled small release for a known set of trusted friends-and-family
testers, extending the Build 1 public/recruiter-facing readiness discipline
with the additional safeguards a small external testing population requires.

### Entry criteria

- Build 1 public/recruiter-facing readiness discipline (claims policy, docs
  boundary, privacy/secrets hygiene, visual pass discipline) is established and
  in use.
- Explicit trusted-tester authorization has been obtained from Main Ash / user.

### Must-have features

- Explicit trusted-tester authorization recorded before any tester access is
  granted.
- Tester onboarding flow appropriate to a small, known group.
- Documented known limitations communicated to testers.
- Feedback capture mechanism for trusted testers.
- Rollback/reset/delete-or-disable plan in case the trusted test needs to be
  paused or undone.
- Tester data boundaries kept separate from Jim's private data.
- Safe sample/demo data guidance for testers where real data should not be
  used.
- Privacy and logging safeguards appropriate to external (non-Jim) testers
  using the build.

### Must-not-include / must-not-imply

- Must not imply full public product release.
- Must not imply monetization.
- Must not imply unlimited user onboarding.
- Must not imply enterprise/security compliance.
- Must not imply public marketing launch.

### Privacy and data requirements

- Tester data is isolated from Jim's private profile, job, and firm data.
- Logging captures only what is necessary to support the trusted test and
  respects tester privacy.

### Docs requirements

- Tester-facing onboarding and known-limitations docs exist and are reviewed
  for an appropriate public/private boundary.

### Visual requirements

- Build 2 inherits the visual pass discipline established for Build 1; no
  separate, lower visual bar is introduced for testers.

### Testing requirements

- Implementation acceptance for any new tester-specific features (onboarding,
  rollback/reset, feedback capture) is required before those features are
  considered done.

### Security/secrets requirements

- No secrets, credentials, or env values exposed to trusted testers.
- Tester accounts/sessions (if any) are isolated from Jim's private session
  and data.

### Claims and messaging requirements

- Tester-facing communication sets expectations as a trusted/limited test, not
  a finished product, and is reviewed under the same claims discipline as
  Build 1.

### Release or non-release gate

No release for Build 2 is currently passed or authorized. Build 2 cannot be
entered until Build 1's public/recruiter-facing readiness discipline is
established and explicit trusted-tester authorization is separately granted.

### Agent owners

- Donut Lead: release ladder sequencing, trusted-tester package readiness,
  dependency tracking against Build 1.
- Leah Lead: file scope, mutation risk, implementation safety for tester-facing
  features.
- Rin Lead: tester onboarding docs, known-limitations docs, public/private
  boundary review.
- Cait Lead: tester-facing claims and expectation-setting language.
- Sara Lead: visual governance continuity from Build 1 into tester-facing
  surfaces.
- Anna Repo Agent: repo implementation only after explicit authorization for
  each Build 2 work package.

### Acceptance evidence needed

- Explicit trusted-tester authorization record from Main Ash / user.
- Implementation acceptance objects for onboarding, rollback/reset, and
  feedback-capture features.
- Tester data boundary confirmation.
- Rin review of tester-facing docs.

### Stop conditions

- Do not grant tester access without explicit trusted-tester authorization.
- Do not allow tester data to mix with Jim's private data.
- Do not claim Build 2 is a public release.
- Do not skip rollback/reset planning before granting tester access.

---

## Build 3: Full Public Expanded-User-Base / Potential Monetization Build

checklist_id: `ENDSTATE-03_FULL_PUBLIC_EXPANDED_USER_BASE_OR_MONETIZATION_RELEASE`

### Goal

A future productization path if Jim chooses to expand beyond his own
career-services use case (Build 1) and beyond a small trusted-tester group
(Build 2) to a broader, potentially unknown user base, and potentially
monetize the product. Build 3 is distinguished from Build 1 by user-base scale
and productization/monetization scope, not by being the first build that is
externally presentable — Build 1 is already externally presentable to
recruiters/portfolio viewers.

### Entry criteria

- Build 2 friends-and-family trusted testing has occurred and produced
  sufficient feedback/evidence to inform expanded-user-base readiness.
- Main Ash / user has decided to pursue expansion beyond trusted testing.

### Must-have features

- Multi-user data isolation across an expanded, potentially unknown user base.
- Scalable onboarding appropriate to a broader audience than friends-and-family
  testers.
- A support and operations model appropriate to public users.
- Terms/privacy/legal review appropriate to public productization.
- Billing/monetization readiness, only if monetization is actually pursued.
- Broader public documentation appropriate to an expanded user base.
- Security and dependency review appropriate to expanded, less-trusted users.
- A data deletion/export/reset story for users.
- Public product messaging and limitations appropriate to a broad audience.
- A support/feedback/incident handling route appropriate to public scale.

### Must-not-include / must-not-imply

- Must not imply that Build 1 (Jim's public/recruiter-facing build) already
  satisfies full productization requirements.
- Must not imply that recruiter-facing portfolio readiness equals monetization
  readiness.
- Must not imply that friends-and-family testing (Build 2) equals full public
  launch.

### Privacy and data requirements

- Multi-user data isolation, with each user's data segregated.
- Data deletion/export/reset capability available to users.
- Privacy terms appropriate to a public, expanded user base.

### Docs requirements

- Public-facing product documentation appropriate to an expanded, unknown
  audience, beyond the tester-facing docs used in Build 2.
- Legal/terms/privacy documentation appropriate to public productization.

### Visual requirements

- Build 3 inherits and extends the visual pass discipline established in
  Build 1 and carried through Build 2; no separate, lower visual bar is
  introduced for expanded users.

### Testing requirements

- Implementation acceptance and security/dependency review appropriate to
  multi-user, expanded-scale operation, beyond what was required for Build 1
  or Build 2.

### Security/secrets requirements

- Security and dependency review appropriate to a broader, less-trusted user
  base than friends-and-family testers.
- Secrets/credentials hygiene at a standard appropriate to public exposure and
  potential billing integration.

### Claims and messaging requirements

- Public product messaging and limitations reviewed under the same claims
  discipline established in Build 1, extended to a public audience and, if
  monetization is pursued, to billing-related claims.

### Release or non-release gate

No release for Build 3 is currently passed or authorized. Build 3 cannot be
entered until Build 2 friends-and-family testing has occurred and Main Ash /
user has explicitly decided to pursue expanded-user-base productization.

### Agent owners

- Donut Lead: release ladder sequencing, operational readiness, dependency
  tracking against Build 2.
- Leah Lead: file scope, mutation risk, implementation safety, security/
  secrets hygiene at expanded scale.
- Rin Lead: public docs architecture, release notes, public/private docs
  boundary for an expanded audience.
- Cait Lead: public product claims, prohibited public claims, monetization
  messaging review if monetization is pursued.
- Sara Lead: visual governance and visual pass continuity at public scale.
- Anna Repo Agent: repo implementation only after explicit authorization for
  each Build 3 work package.

### Acceptance evidence needed

- Main Ash / user decision record to pursue expanded-user-base productization.
- Implementation acceptance objects for multi-user isolation, onboarding,
  support/ops model, and (if pursued) billing.
- Legal/privacy/terms review record.
- Security and dependency review record appropriate to expanded scale.

### Stop conditions

- Do not enter Build 3 without a Main Ash / user decision to pursue expanded-
  user-base productization.
- Do not claim monetization readiness without explicit billing/legal review.
- Do not treat Build 1 or Build 2 evidence as sufficient for Build 3 multi-user
  productization claims.

---

## Dependency Map

```
Build 1 -> Build 2:
  Build 2 extends beyond Jim's public/recruiter-facing build by adding
  trusted-tester onboarding, tester data boundaries, rollback/reset, support
  expectations, and feedback capture.

Build 2 -> Build 3:
  Build 3 extends beyond trusted testing by adding expanded-user-base
  readiness, scalable operations, product/legal/privacy terms,
  monetization/billing readiness if pursued, and stronger security/
  compliance.

Cross-cutting note:
  Public/recruiter-facing polish belongs to Build 1.
  Multi-user productization and monetization belong to Build 3.
```

---

## Agent Owner Map

- Donut Lead: release ladder sequencing; package readiness; dependency map;
  operational readiness.
- Leah Lead: file scope; mutation risk; implementation safety; security/
  secrets/generated-artifact hygiene; implementation acceptance evidence.
- Rin Lead: public/private docs boundary; release notes; docs architecture;
  Rin sync readiness only when separately authorized.
- Cait Lead: career evidence; claims policy; recruiter-facing language;
  prohibited public claims; career-material readiness boundaries.
- Sara Lead: visual governance; visual pass; screenshot/readiness standards;
  reference compliance.
- Anna Repo Agent: repo implementation only after explicit E3 authorization;
  never self-authorizes release, push, implementation acceptance, visual pass,
  or public launch.

---

## Blocked Gates

As of this document's authoring (2026-06-22), none of the following are passed
or authorized for any build:

```
release (Build 1)
release (Build 2)
release (Build 3)
Rin sync
P7P6
visual pass
implementation acceptance (for this ladder document itself)
public launch
recruiter release approval
monetization launch
```

This document does not change any of the above. Each remains blocked until a
separate, explicit acceptance object clears it.

---

## Stop Conditions

The following are standing rules for any future revision of this document:

- Do not describe Build 1 as private-only.
- Do not move public/recruiter-facing readiness out of Build 1.
- Do not describe Build 3 as merely public/recruiter-facing portfolio
  readiness.
- Do not claim any gate has passed in this document.
- Do not authorize release, Rin sync, P7P6, screenshots, visual pass,
  implementation acceptance, public launch, recruiter release approval, or
  monetization launch via this document.
- Do not include Firm Repository nav wiring as immediate work.
- Do not include profile/`james_profile.yaml` PII remediation unless
  separately authorized.
- Do not expose secrets, env values, private profile data, private job/firm
  data, database contents, generated backups, screenshots, or private agent
  memory anywhere in this document's content.

---

## Machine-Readable Summary

```json
{
  "doc_id": "ATLAS_RELEASE_READINESS_LADDER",
  "status": "codification_only",
  "authored_date": "2026-06-22",
  "checklist_ids": [
    "ENDSTATE-01_JIM_PUBLIC_RECRUITER_FACING_CAREER_SERVICES_BUILD",
    "ENDSTATE-02_FRIENDS_AND_FAMILY_RELEASE",
    "ENDSTATE-03_FULL_PUBLIC_EXPANDED_USER_BASE_OR_MONETIZATION_RELEASE"
  ],
  "dependency_map": {
    "build_1_to_build_2": "Build 2 extends beyond Jim's public/recruiter-facing build by adding trusted-tester onboarding, tester data boundaries, rollback/reset, support expectations, and feedback capture.",
    "build_2_to_build_3": "Build 3 extends beyond trusted testing by adding expanded-user-base readiness, scalable operations, product/legal/privacy terms, monetization/billing readiness if pursued, and stronger security/compliance.",
    "cross_cutting_note": "Public/recruiter-facing polish belongs to Build 1. Multi-user productization and monetization belong to Build 3."
  },
  "agent_owner_map": {
    "Donut Lead": ["release ladder sequencing", "package readiness", "dependency map", "operational readiness"],
    "Leah Lead": ["file scope", "mutation risk", "implementation safety", "security/secrets/generated-artifact hygiene", "implementation acceptance evidence"],
    "Rin Lead": ["public/private docs boundary", "release notes", "docs architecture", "Rin sync readiness only when separately authorized"],
    "Cait Lead": ["career evidence", "claims policy", "recruiter-facing language", "prohibited public claims", "career-material readiness boundaries"],
    "Sara Lead": ["visual governance", "visual pass", "screenshot/readiness standards", "reference compliance"],
    "Anna Repo Agent": ["repo implementation only after explicit E3 authorization", "never self-authorizes release, push, implementation acceptance, visual pass, or public launch"]
  },
  "gates_passed": [],
  "non_authorization_notice": true
}
```
