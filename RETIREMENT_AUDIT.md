# Old-Laptop Retirement Safety Audit

Audit only. No commits, pushes, or deletes performed.

Baseline for comparison: `origin/feature/llm-abstraction` (14f35ad) and `origin/main` (dcb83c4, in sync with local `main`).

---

## 1. Local-only branch audit: `planning/phase-2-3-scoring-contracts`

- **Commit:** `379af0034a24fbaf762399a4d02cde8df2cd9d61`
- **Summary:** "Add draft Phase 2/3 scoring contract planning artifacts"
- **Diff vs `origin/feature/llm-abstraction`:** identical file set, 701 insertions, 0 deletions:
  - `docs/Architecture/future_scoring_firm_contracts.md` (187 lines)
  - `job_search/planning/__init__.py` (45 lines)
  - `job_search/planning/future_scoring_contracts.py` (294 lines)
  - `tests/test_future_scoring_contracts.py` (175 lines)

**Content analysis:**
- The module is explicitly self-described as "preparatory only," "not imported by the runtime pipeline," and "must not be treated as accepted Phase 2/3 implementation."
- It defines draft dataclasses (`SignalRuleDraft`, `SignalHitDraft`, `SignalScoreDraft`, `EvidenceClaimDraft`, `FirmAtsDraft`, `FirmProfileDraft`, `JobScoreInputsDraft`, `JobScoreEnvelopeDraft`, `DashboardScoreSummaryDraft`) plus enums (`ScoreDomain`, `SignalSource`, `ClaimStatus`, `Rating`, `ReviewStatus`).
- Compared against `origin/feature/llm-abstraction:job_search/models.py`: the **real, accepted, runtime-wired** equivalents already exist there — `FirmProfile`, `DraftFirmProfile`, `FirmBenefit`, `FirmBenefitStatus`, `FirmProfileMeta`, and `CanonicalJob.benefit_score` / `career_trajectory_score` fields are all implemented and in production use (`job_search/ingestion/scoring.py`, `job_search/firms/repository.py`).
- The draft module is **not a duplicate of the implementation** — it proposes a *next-iteration* object model (controlled benefit/trajectory keys, evidence claims with provenance, dashboard read models) that is more granular than what's currently shipped, and is intended for **future** Phase 2/3 work once Ash reviews it. It contains genuine unique design thinking not captured in any committed doc on origin.

**Classification: `KEEP_AND_PUSH`**

**Recommendation:** Push this branch to `origin` as-is (no cherry-pick needed — it's a clean, self-contained, inert addition with zero runtime risk). Do not merge into `main` or `feature/llm-abstraction` without Ash's review, per the doc's own "Review Needed Before Acceptance" section — just get it off local-only storage.

---

## 2. Worktree WIP audit

### 2a. `C:/Users/James/.codex/worktrees/6f47/job-search-assistant`

- **Branch/commit:** detached HEAD at `0138c1c` ("feat: improve resume rendering and cover letter generation pipeline") — this commit is already an ancestor of `main`.
- **`git status --short`:**
  ```
   M docs/Architecture/resume_generation_architecture.md
   M job_search/db/schema.sql
   M job_search/generation/generator.py
   M job_search/reporting/__init__.py
   M tests/test_generation_evidence.py
   M tests/test_selection.py
  ?? job_search/reporting/documents.py
  ```
- **`git diff --stat`:** 6 files changed, 225 insertions(+), 22 deletions(-)
- **Untracked:** `job_search/reporting/documents.py` (83 lines — `get_latest_generated_doc`, `get_latest_generated_docs`, `get_latest_generated_docs_for_jobs` helpers over the `generated_docs` table)
- **Purpose of WIP:** adding a query layer for generated-document history (resume/cover-letter lookups by job) plus a supporting DB index, with matching test/doc updates.
- **Comparison against `origin/feature/llm-abstraction`:**
  - `job_search/reporting/documents.py` **already exists verbatim in concept on origin** (origin's version has 66 lines with `list_generated_docs` instead of `get_latest_generated_docs_for_jobs`, but covers the same query surface, already integrated and tested).
  - `job_search/db/schema.sql`: the single index the WIP adds (`idx_generated_docs_job_type_generated`) **already exists on origin**, which additionally has a second index (`idx_generated_docs_job_generated`) the WIP lacks.
  - `job_search/generation/generator.py`: diffing the WIP against origin shows origin contains a **superset** — an `audit_generated_documents` integration (`document_audit` field, `RESUME_ONE_PAGE_*` constants, template-marker validation regex) that this WIP's base commit predates entirely. The WIP is not ahead of origin here — it's behind.
  - `tests/test_generation_evidence.py`: diff against origin shows origin has **549 more lines** than this WIP's version — confirming the WIP's base snapshot is stale relative to origin, not additive to it.
- **Determination: obsolete.** This WIP was built on top of an old commit before the document-audit feature set landed upstream. Every concept in it (doc-history queries, the index) is already present and exceeded on origin.

**Classification: `SUPERSEDED_BY_REMOTE`**

### 2b. `C:/Users/James/.codex/worktrees/f8b7/job-search-assistant`

- **Branch/commit:** detached HEAD at `379af00` (the same commit as `planning/phase-2-3-scoring-contracts`, see §1).
- **`git status --short`:**
  ```
   M docs/Architecture/dashboard_architecture.md
   M docs/Architecture/resume_generation_architecture.md
   M job_search/db/connection.py
   M job_search/db/schema.sql
   M job_search/generation/generator.py
   M job_search/reporting/__init__.py
   M tests/test_generation_evidence.py
   M tests/test_resume_renderer.py
   M tests/test_selection.py
  ?? job_search/reporting/documents.py
  ?? tests/test_generated_documents.py
  ```
- **`git diff --stat` (vs its own HEAD):** 9 files changed, 346 insertions(+), 41 deletions(-)
- **Untracked:** `job_search/reporting/documents.py`, `tests/test_generated_documents.py`
- **Purpose of WIP:** same document-history feature as 6f47, plus a DB migration helper (`_apply_migrations` extended with `_ADDED_INDEXES`) and dashboard-doc cross-references.
- **Comparison against `origin/feature/llm-abstraction`:**
  - `git diff origin/feature/llm-abstraction --stat` from this worktree shows **56 files differing, net −9,383 lines** relative to origin — this worktree's base commit (`379af00`) predates the entire Phase 3 firm-repository build-out (`job_search/firms/*`, `job_search/generation/audit.py`, rewritten `job_search/cli.py`, rewritten `job_search/ingestion/scoring.py`, six firm-related test files, `profile/james_profile.yaml`, etc. all missing from this snapshot).
  - Checked exact byte-for-byte: `job_search/db/connection.py` WIP diff adds `_ADDED_INDEXES` with the exact two index statements `idx_generated_docs_job_type_generated` and `idx_generated_docs_job_generated` — **this exact code, including the comment text, already exists verbatim on `origin/feature/llm-abstraction:job_search/db/connection.py`**, which additionally has `_FIRMS_ADDED_COLUMNS` migrations this WIP doesn't know about.
  - `job_search/db/schema.sql` WIP diff: identical two-index addition, already present on origin.
- **Determination: obsolete and superseded**, same root cause as 6f47 — this worktree's checkout predates a large amount of now-merged upstream work, and the specific WIP edits on top of it duplicate functionality origin already shipped (in some cases with identical code).

**Classification: `SUPERSEDED_BY_REMOTE`**

---

## 3. `docs/Planning/` audit

No `docs/Planning/` directory exists on `origin/feature/llm-abstraction`, `origin/main`, or local `main`. All four files below are **untracked, unique, and not represented anywhere else in the repo.**

| Worktree | File | Lines | Topic |
|---|---|---|---|
| `-donut-application-lifecycle` | `application_lifecycle_design_review.md` | 533 | Application state machine (Discovered → Presented → Selected → Applied → Acknowledged → Screen → Ghosted → Rejected, etc.), tracked data, reporting/reminder hooks, future automation |
| `-donut-benefit-firm-prb` | `phase_2_3_product_requirements_brief.md` | 365 | Product requirements brief for Phase 2 (Benefit/Trajectory Scoring) and Phase 3 (Firm Repository): goals, explainability requirements, approval-boundary rules |
| `-donut-daily-review-workflow` | `daily_review_workflow_specification.md` | 608 | Morning operating workflow spec: daily summary triage order, follow-ups, firm/source warnings, 10–20 min target session |
| `-donut-dashboard-ia` | `dashboard_information_architecture_review.md` | 417 | Information ownership map across daily report / weekly review / dashboard / job detail / firm detail / analytics surfaces |

**Comparison against committed `docs/Architecture/`:**
- `dashboard_architecture.md` (committed) covers technical dashboard structure; `dashboard_information_architecture_review.md` (untracked) covers a *product/IA ownership map* layered on top — complementary, not duplicate, no content overlap found in either file's headers/sections.
- No committed doc addresses application lifecycle states, the daily-review morning workflow, or a Phase 2/3 product requirements brief — these four documents are net-new product thinking with zero counterpart on origin or main.
- All four explicitly state `Runtime impact: None` and are framed as "Planning review/brief for Ash and Anna" — i.e., real authored governance/planning input awaiting review, not generated scratch output.

**Classification (all four): `KEEP_AND_PUSH`** (or archive, see §4 — these are documentation-only, zero conflict risk)

---

## 4. Preservation plan (not yet executed)

| Item | Recommended method | Why |
|---|---|---|
| `planning/phase-2-3-scoring-contracts` branch | `git push origin planning/phase-2-3-scoring-contracts` | Already a clean, self-contained commit; pushing preserves full history and lets Ash review it as a normal branch. |
| `docs/Planning/application_lifecycle_design_review.md` | Copy into a new commit on a fresh branch (e.g. `docs/Planning` added directly, or staged into `docs/Archive/LocalWork/`) and push | Untracked-only — must be committed somewhere before it can leave this machine. A dedicated docs branch avoids touching `main` or `feature/llm-abstraction` directly. |
| `docs/Planning/phase_2_3_product_requirements_brief.md` | Same as above | Same reasoning. |
| `docs/Planning/daily_review_workflow_specification.md` | Same as above | Same reasoning. |
| `docs/Planning/dashboard_information_architecture_review.md` | Same as above | Same reasoning. |
| Worktree `6f47` WIP | Discard | Confirmed superseded by origin; no unique value found in any of its 6 modified files or 1 untracked file. |
| Worktree `f8b7` WIP | Discard | Confirmed superseded by origin, including byte-identical code already merged upstream. |

Suggested concrete sequence (when approved):
1. `git push origin planning/phase-2-3-scoring-contracts`
2. Create one new branch (e.g. `docs/local-planning-archive`) off `main`, copy the four `docs/Planning/*.md` files in from their worktree paths, commit, push.
3. Leave the two `.codex` worktrees and their WIP as-is or remove the worktrees (no preservation needed) — confirm with user before any worktree removal, since that step wasn't requested as part of this audit.

---

## 5. Final old-laptop retirement verdict

**YES, after preserving listed items.**

Specifically:
- The 4 product/planning docs (`docs/Planning/*.md`, ~1,923 lines combined) and the `planning/phase-2-3-scoring-contracts` branch (701 lines) are genuinely unique, not present on GitHub in any form, and would be permanently lost if this machine is retired without action.
- The two `.codex` worktree WIPs (`6f47`, `f8b7`) carry **no unique value** — both are confirmed superseded, in places byte-for-byte identical to code already merged on `origin/feature/llm-abstraction`. They are safe to discard without any preservation step.
- `main` itself is already fully in sync with `origin/main` — no action needed there.

No commits, pushes, or deletions were made during this audit.
