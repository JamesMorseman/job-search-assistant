# Build 1 Package 0 — Application Pathway and Base Resume Library Spec

## Metadata

- Document ID: `B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_DOC_01`
- Package: `B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_UPDATE`
- Prompt ID: `B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_UPDATE`
- Track: B
- Gate classification: `E3_DOCS_SPEC_ONLY_PACKAGE_0`
- Status: docs/spec-only requirement record (not implementation, not acceptance,
  not release readiness)
- Owner: Main Ash / user (James)
- Authored by: Repo Ash Master under explicit docs/spec-only authorization
- Baseline branch verified at authoring time: `wip/build1/away-run-implementation-01`
- Baseline head verified at authoring time: `c9168e0`
- This document does **not** authorize commits, staging, pushes, PRs, merges,
  source/frontend/backend/test/data mutation, profile mutation, dependency
  changes, resume/cover-letter generation, visual pass, implementation
  acceptance, release readiness, public/recruiter release, Rin sync, P7P6, or
  screenshots/media capture. See Section 9 (Blocked Gates).

---

## 1. Purpose

This is the docs/spec-only Package 0 that records two newly accepted Build 1
critical requirements into repo truth **before** any code implementation:

- `BUILD1-REQ-APPLICATION-PATHWAY` — the dashboard must provide a real
  application pathway (at minimum an external apply/posting URL, plus
  workspace/material links when available).
- `BUILD1-REQ-BASE-RESUME-LIBRARY` — Build 1 must include an evidence-governed
  base resume library used as tailoring input.

Per Leah's audit decision, this Package 0 spec must precede code implementation
and the implementation must be split into Package 1, Package 2, and Package 3
(Section 6). This document encodes the accepted product, claim/quality, and
architecture constraints; preserves open questions with conservative defaults
rather than blocking; and hands nothing to implementation beyond a recorded
specification.

This document is a **requirement specification and decision record**. It is not
a replacement for `docs/Architecture/build_1_completion_roadmap.md` (the
executable task register, which now carries summary sections for both
requirements and the Package 0–3 sequence) or for
`docs/Architecture/Migration/DECISION_LOG.md` (the authoritative governance
decision log, which now carries the accepted-decision entries).

---

## 2. Requirement: BUILD1-REQ-APPLICATION-PATHWAY

**Summary:** The dashboard must provide a real application pathway through an
external apply/posting URL at minimum, plus workspace/material links when
available.

**Accepted product decisions (Donut):**

- An external apply/posting URL is **required** for Build 1.
- Direct one-click apply inside ATLAS is **rejected/deferred** for Build 1.
- An explicit apply-intent gate is **required** before any material generation.

**Hard rules:**

1. Direct one-click apply inside ATLAS is rejected/deferred for Build 1.
2. Opening an apply/posting URL is **navigation-only** (no submission, no
   generation side effect).
3. Opening a workspace is **navigation-only**.
4. Selecting a job or a base resume is **not** generation authorization.
5. Resume/cover generation requires **explicit user confirmation after posting
   review**.
6. Generated materials are **drafts requiring human review** — not
   submission-ready and not recruiter-ready artifacts.

**Behavioral model (decoupled, per Leah):**

- Navigation (open apply URL, open workspace) and generation (produce a
  tailored draft) are separate user actions with separate authorization.
- The apply-intent gate sits between posting review and generation; no
  selection event (job or base resume) may auto-advance through it.

---

## 3. Requirement: BUILD1-REQ-BASE-RESUME-LIBRARY

**Summary:** Build 1 must include an evidence-governed base resume library used
as tailoring input.

**Approved base resume categories:**

- `structural_engineering`
- `site_civil_land_development`
- `water_resources_stormwater`
- `environmental_engineering`
- `construction_project_engineering`
- `general_civil_technical_analyst_fallback`

**Deferred base resume categories (not Build 1 scope):**

- `transportation_traffic`
- `geotechnical`
- `operations_project_controls`

**Hard rules:**

1. Base resume selection/recommendation is **advisory and user-overridable**.
2. Manual base resume selection is **required for unreachable postings** (no
   reachable apply/posting URL).
3. Base resume selection alone **must not generate documents**.
4. No real private resume contents, Drive URLs, generated materials,
   credentials, or profile PII may be committed.

---

## 4. Claim and Resume-Quality Policy (Cait)

- Generated materials are **evidence-backed drafts requiring human review**.
- The general fallback category is hardened to
  **general civil / technical analyst fallback**.
- ATS / recruiter / submission-ready guarantees are **rejected**.
- Unsupported claims are **prohibited**, including unverified credentials,
  licensure, experience, tool mastery, and work authorization.
- User approval is represented as a **timestamped review/submission note, not a
  system readiness certification** (see Section 7).

---

## 5. Architecture Constraints (Leah)

- **Decouple navigation from generation** — opening an apply URL or workspace
  must never trigger material generation.
- **Nullable / backward-compatible fields** — apply/posting URL, workspace
  reference, and material reference fields must be nullable and must not break
  existing records that lack them.
- **Privacy-safe references** — Drive/document links are privacy-sensitive
  private metadata; store provider-neutral references plus metadata, never real
  private URLs or resume contents in repo truth.
- Roadmap/spec Package 0 must precede code implementation (this document
  satisfies that precondition).

---

## 6. Package Sequencing

Implementation is split into the following packages. Package 0 (this document)
is docs/spec-only and authorizes none of the code work below.

- **Package 0 — Application pathway and base resume spec (this document).**
  Docs/spec-only requirement record. No code, no acceptance.
- **Package 1 — Application pathway data/UI links.** Add nullable,
  backward-compatible apply/posting URL and workspace/material reference fields
  end-to-end (data model, API, types/client, detail surface), navigation-only.
  No generation, no one-click apply.
- **Package 2 — Base resume library selector.** Introduce the evidence-governed
  base resume library (approved categories only) and an advisory,
  user-overridable selector that surfaces metadata plus a linked source
  document reference. Manual selection required for unreachable postings.
  Selection alone must not generate documents.
- **Package 3 — Generation intent-gate integration.** Wire the explicit
  apply-intent gate so resume/cover generation requires explicit user
  confirmation after posting review, producing drafts only (evidence-backed,
  human-review-required, no readiness guarantees).

Each of Packages 1–3 requires its own future authorization, allowed/blocked
path list, validation evidence, and audit before any acceptance claim.

---

## 7. Conservative Defaults (Open Questions Resolved Non-Blocking)

These defaults resolve open design questions conservatively so Package 0 is not
blocked. Implementation packages may refine them with explicit authorization.

- **Workspace reference:** provider-neutral `workspace_url` / `workspace_ref`.
- **Base resume reference:** provider-neutral `document_ref` with metadata.
- **Blank workspace creation:** explicit user action only.
- **Cover letter:** available but **not** default-generated.
- **Freshness triggers** (mark a generated draft stale): base resume version
  change; profile/evidence snapshot change; posting snapshot change;
  user-marked stale state.
- **User approval representation:** timestamped review/submission note, **not**
  a system readiness certification.
- **Base resume storage:** metadata plus a linked source document reference; no
  private resume content committed.

---

## 8. Remaining Open Questions (Non-Blocking)

These are recorded for future implementation packages; none block Package 0:

- Exact field placement of `apply_url` / `workspace_ref` / `document_ref` in the
  data model versus a related side table (Package 1 design choice).
- Whether the base resume library is stored as repo-tracked metadata files,
  config, or DB rows — constrained only by "no private resume content
  committed" (Package 2 design choice).
- Exact UI affordance for the apply-intent gate (modal confirm vs. explicit
  action button) — constrained by "explicit user confirmation after posting
  review" (Package 3 design choice).
- How deferred categories (`transportation_traffic`, `geotechnical`,
  `operations_project_controls`) are represented as not-yet-available without
  implying they exist.

---

## 9. Blocked Gates

This Package 0 spec does **not** authorize, and no work performed under it may
claim or perform, any of the following:

```
stage
commit
push
PR
merge
source_code_mutation
frontend_mutation
backend_mutation
test_mutation
data_db_mutation
profile_mutation
dependency_changes
run_full_unfiltered_pytest
generate_resumes_or_cover_letters
create_real_application_materials
screenshots/media capture
Rin sync
P7P6
visual pass
implementation acceptance
release readiness
public/recruiter release
full public release
```

These remain gated behind separate, explicit authorization from Main Ash /
James.

---

## 10. Machine-Readable Spec JSON

```json
{
  "doc_id": "B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_DOC_01",
  "prompt_id": "B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC_UPDATE",
  "track": "B",
  "gate_classification": "E3_DOCS_SPEC_ONLY_PACKAGE_0",
  "status": "docs_spec_only_requirement_record",
  "baseline_branch_verified": "wip/build1/away-run-implementation-01",
  "baseline_head_verified": "c9168e0",
  "requirements": [
    {
      "id": "BUILD1-REQ-APPLICATION-PATHWAY",
      "summary": "Dashboard must provide a real application pathway through external apply/posting URL at minimum, plus workspace/material links when available.",
      "product_decisions": [
        "external apply URL required",
        "one-click apply rejected/deferred for Build 1",
        "explicit apply-intent gate required before material generation"
      ],
      "hard_rules": [
        "Direct one-click apply inside ATLAS is rejected/deferred for Build 1.",
        "Opening apply/posting URLs is navigation-only.",
        "Opening a workspace is navigation-only.",
        "Selecting a job/base resume is not generation authorization.",
        "Resume/cover generation requires explicit user confirmation after posting review.",
        "Generated materials are drafts requiring human review, not submission-ready or recruiter-ready artifacts."
      ]
    },
    {
      "id": "BUILD1-REQ-BASE-RESUME-LIBRARY",
      "summary": "Build 1 must include an evidence-governed base resume library used as tailoring input.",
      "approved_categories": [
        "structural_engineering",
        "site_civil_land_development",
        "water_resources_stormwater",
        "environmental_engineering",
        "construction_project_engineering",
        "general_civil_technical_analyst_fallback"
      ],
      "deferred_categories": [
        "transportation_traffic",
        "geotechnical",
        "operations_project_controls"
      ],
      "hard_rules": [
        "Base resume selection/recommendation is advisory and user-overridable.",
        "Manual base resume selection is required for unreachable postings.",
        "Base resume selection alone must not generate documents.",
        "No real private resume contents, Drive URLs, generated materials, credentials, or profile PII may be committed."
      ]
    }
  ],
  "claim_policy": {
    "owner": "cait",
    "rules": [
      "Generated materials are evidence-backed drafts requiring human review.",
      "General fallback hardened to general civil / technical analyst fallback.",
      "ATS/recruiter/submission-ready guarantees rejected.",
      "Unsupported credentials, licensure, experience, tool mastery, and work authorization claims prohibited."
    ]
  },
  "architecture_constraints": {
    "owner": "leah",
    "rules": [
      "Decouple navigation from generation.",
      "URL/workspace/material fields must be nullable/backward-compatible.",
      "Drive/document links are privacy-sensitive private metadata.",
      "Package 0 spec precedes code implementation."
    ]
  },
  "package_sequence": [
    {"package": "Package 0", "scope": "Application pathway and base resume spec (this document), docs/spec-only"},
    {"package": "Package 1", "scope": "Application pathway data/UI links (nullable, navigation-only)"},
    {"package": "Package 2", "scope": "Base resume library selector (advisory, metadata + document_ref)"},
    {"package": "Package 3", "scope": "Generation intent-gate integration (explicit confirmation, drafts only)"}
  ],
  "conservative_defaults": {
    "workspace_reference": "provider-neutral workspace_url/workspace_ref",
    "base_resume_reference": "provider-neutral document_ref with metadata",
    "blank_workspace_creation": "explicit user action",
    "cover_letter_default": "available but not default-generated",
    "freshness_triggers": [
      "base resume version change",
      "profile/evidence snapshot change",
      "posting snapshot change",
      "user-marked stale state"
    ],
    "user_approval_representation": "timestamped review/submission note, not system readiness certification",
    "base_resume_storage": "metadata plus linked source document reference; no private resume content committed"
  },
  "blocked_gates": [
    "stage", "commit", "push", "PR", "merge",
    "source_code_mutation", "frontend_mutation", "backend_mutation",
    "test_mutation", "data_db_mutation", "profile_mutation",
    "dependency_changes", "run_full_unfiltered_pytest",
    "generate_resumes_or_cover_letters", "create_real_application_materials",
    "screenshots_or_media_capture", "Rin_sync", "P7P6", "visual_pass",
    "implementation_acceptance", "release_readiness",
    "public_recruiter_release", "full_public_release"
  ],
  "non_authorization_notice": true
}
```
