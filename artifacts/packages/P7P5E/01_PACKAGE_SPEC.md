# P7P5E — ATLAS Visual Foundation REBUILD / Completion Pass

Status: DEFINED (implementation dispatched to Anna-Implimentor)
Base commit: 158d9ae ("chore(dev): add ATLAS visual review reload harness")
Stacked on: 22e9889 ("feat(p7p5d): establish ATLAS visual style foundation and reusable objects")
Branch: recovery/full-private-state-20260618 (2 ahead / 0 behind origin, not pushed)
Defined by: Ash-Master
Supersedes review framing of: Sara "ATLAS P7P5D Strict Visual Governance Audit — Implementation-AI Handoff Edition" (verdict: HARD VISUAL FAIL)

## Why this package exists
Sara's revised, stricter audit SUPERSEDES the earlier softer P7P5D audit. New verdict:
HARD VISUAL FAIL. The finding is perceptual, not technical: P7P5D added components and
objects, but the screenshots still look substantially like the prior failed build. The
user's reaction — "I can't tell a difference" — is decisive. Adding component names,
labels, chips, or text panels is explicitly NOT sufficient. The visual SILHOUETTE of the
app must change. Standard: "Can a viewer immediately tell this is the accepted ATLAS
visual system without reading labels?" Current answer: No. P7P5E must change the answer.

## Objective
Produce a visually OBVIOUS shift from dark runtime scaffold to ATLAS reference-style
mission-control system, and establish reusable visual foundations so future ATLAS objects
inherit the accepted system without further churn. This is a rebuild/completion pass, more
assertive than incremental polish — NOT product expansion, NOT release prep, NOT docs, NOT
P7P6 capture.

## THE GUARDRAIL (the failure mode to avoid)
The P7P5D failure was adding labels/components without changing the app's visual
silhouette. Do NOT solve this by adding more chips/text/sections to the same layout
skeletons. The goal is a perceptually obvious shift in SIZE, BRIGHTNESS, DENSITY,
HIERARCHY, GLOW, and the LAYOUT SKELETON ITSELF — not vocabulary.

## Command Center scope decision (Ash, binding for this pass)
Command Center is EXCLUDED from this pass's screenshot candidates. Given the full
Shell/Brand rebuild + Radar + RecommendationCard + Opportunity Detail recompose + Ask
Atlas + ContextPanel module library already in P0 scope, a full CC reference-skeleton
rebuild would be the largest single item and a partial rebuild is the exact half-measure
that caused the HARD FAIL. Radar / Opportunity Detail / Ask Atlas are the closest,
highest-leverage surfaces and must carry the perceptual shift. CC gets ONLY the shared
shell/brand/token inheritance (it will improve automatically from the shell rebuild) plus,
at most, minor cleanup — NO new text cards added to its existing sparse layout. The report
must state CC was excluded and why.

## Authorized file areas (frontend source / source tests only)
- frontend/src/**/*.tsx and frontend/src/**/*.css
- frontend source tests if useful (no test framework currently present; do not add one)
- this spec under artifacts/packages/P7P5E/ (convention already established)

## P0 priorities — implement in this order (Anna treats as the spec, not paraphrase)

### 1. Shell / Brand (P0 — fix FIRST; every surface inherits it)
- Rebuild AtlasMark / AtlasLogo: larger, brighter sweep wedge, clearer concentric radar
  rings, visible crosshair/axis geometry, stronger cyan glow; legible at 24/32/48px AND
  sidebar-header size. Reference silhouette = radar circle + sweep wedge + signal/compass
  identity — NOT a dot / low-contrast ring / generic target icon / abstract teal circle.
- Strengthen sidebar brand lockup (mark + wordmark + subline) so it visually DOMINATES the
  sidebar top more than now.
- Fix or hide the weak tiny text-only footer: either build a real mission-strip with icon
  rhythm (e.g. "ATLAS scans. Atlas interprets. Ask Atlas communicates. Pipeline executes.")
  or suppress it from screenshot surfaces.
- Establish a shared WorkspaceHeader top-shell pattern (eyebrow / title / subtitle /
  optional controls) so content does not start abruptly after the sidebar.
- Strengthen shared card depth / glow / typography-scale tokens (design-tokens.css,
  shell.css).
- Acceptance bar: a viewer should recognize ATLAS from shell identity ALONE, before
  reading page content.

### 2. Radar / OpportunitySignalCard (P0 — closest surface, push over the line)
- Define OpportunitySignalCard.Full: large dominant radar visual on a strong left anchor,
  brighter sweep, visible signal dots/returns, signal-detected label, tier badge,
  title/company, metadata row with icons, signal summary block, detected/strength/source
  row, Save / Review Opportunity / Track action row, strong border/glow/depth.
- Define OpportunitySignalCard.Compact: mini radar object that is still VISIBLY a radar
  (not squeezed text), signal-detected label, tier badge, title/company, compact metadata,
  1-line summary, mini metric row, compact primary action.
- Tier visual differentiation must be REAL (brighter sweep / stronger glow / more dots /
  stronger CTA for Exceptional vs medium for Strong vs lower-intensity for Relevant) — not
  pill-text-only.
- Strengthen the selected-signal right rail (signal summary, strength, why-selected,
  stage/status, Review CTA — not plain metadata).
- Remove the weak duplicate "Open Opportunity Detail" link that undercuts the primary CTA.
- Object rule: must read as SIGNAL before text.

### 3. RecommendationCard (P0)
- Define .Full / .Compact / .Rail variants.
- Full: Atlas Recommendation identity row, confidence as a real visual OBJECT (not a small
  pill), large headline, rationale body, reason checklist, optional subtle radar/network
  background, action row (Review / Ask Atlas Why / Dismiss).
- If Dismiss has no real handler: hide it from screenshot-candidate surfaces or render it
  clearly secondary/disabled — do NOT ship a clickable-looking stub.

### 4. Opportunity Detail (P0/P1 — recompose, not just add sections)
Target structure: Top (Back to Pipeline + optional breadcrumb) -> Hero (identity tile/logo,
title/company, status chips, metadata row, confidence ring integrated into hero/advisory
area rather than isolated) -> State (stronger CurrentStateStrip + stronger NextStep block)
-> Advisory (Stored Atlas Context / Existing Rationale styled as a real advisory object,
reason chips/bullets, score if stored) -> Details (tabs or segmented sections:
Overview/Requirements/Fit Context/Signal Context/Job Details) -> Right rail (Related
Opportunities as compact SignalCards or a genuinely designed empty state, Atlas Context,
Active Focuses, Ask Atlas entry).
- Do not invent unsupported facts. Designed empty states are fine; fake private/real data
  is not. Empty-state standard: icon + title + short body + 1-2 CTAs (avoid plain
  sentence with no icon/CTA).

### 5. Ask Atlas (P0/P1 — investigation workspace, not a flat report)
- Investigation-context card row (Opportunity / Recommendation-or-Stored-Fit-Context /
  Focus-priority / Progression-stage).
- User question bubble/prompt state; an Atlas Observation card; Atlas Explanation split
  into multiple richer cards (Signal/Fit, Timing/Stage, Comparison/Next Review) instead of
  plain text blocks.
- Stronger Suggested Review Path object (icon/title/concise action/CTA); upgraded follow-up
  prompt objects; stronger input bar; Ask-Atlas-specific right rail (Atlas Context, Related
  Opportunity, Active Focuses, Quick Actions) replacing the generic Local Context rail.
- Reduce empty lower-screen space.
- Acceptance bar: should look like Atlas communicating in context, not a static diagnostic
  report.

### 6. Command Center — EXCLUDED this pass (see scope decision above)
Shell/brand/token inheritance only; minor cleanup permitted; NO new text cards on the
existing sparse layout. Report must state exclusion + reason.

### 7. Right Context Panel module system (supports #4 / #5)
Build/strengthen reusable modules: ContextPanel, ContextModule, SelectedOpportunityModule,
RelatedOpportunitiesModule, AtlasContextModule, ActiveFocusesModule, AskAtlasEntryModule,
QuickActionsModule, ProgressionModule, RecommendationModule. Each module: icon, label,
concise content, optional state/chip, optional CTA, designed empty state if no data. Avoid
generic repeated "Local Context" copy as the default screenshot rail.

### 8. Pipeline — EXCLUDED / internal. No rebuild. Do not present "Run Visibility" as the
accepted product Pipeline. Minor language/styling cleanup to keep it clearly
internal/diagnostic is fine.

## PRESERVE from P7P5D (useful direction; NOT sufficient as-is — must be strengthened)
ATLAS wordmark + sidebar structure; AtlasMark concept (rebuild/polish strongly); nav icons;
SignalCard concept; Radar hero + signal hierarchy; Save/Review/Track action set;
RecommendationCard concept; Opportunity Detail confidence ring; Back to Pipeline;
Current State / Next Step concepts; Stored/Existing rationale language; Ask Atlas
completed/default response state; fictional/demo safety language; the visual review reload
harness (do not touch it; use it to validate).

## Denied scope (HARD)
No Run Sweep / Scan Now; no UI-triggered pipeline execution; no new backend endpoints or
POST/PUT/PATCH/DELETE routes; no DB/schema changes; no pipeline-runner/scoring/generation
behavior changes; no resume/profile/career-material logic changes; no public/export docs;
no Rin invocation; no P7P6 capture; no new dependencies (STOP + report instead); no
data/jobs.db modification; no committing screenshots/credentials/local-settings/DOCX/private
artifacts; no push; no backend/Python application code, database/schema, or scoring logic.

## Do-not-stage list (already dirty in tree — leave untouched)
data/jobs.db, .claude/settings.local.json, .claude/agents/*.md, artifacts/phase1_review/*,
"Reference Images/*", "Pipeline Reference.png", frontend/dist/* stale build drift,
8 untracked reference PNGs.

## Leah sentinel conditions (STOP and report; do not implement past)
backend/API/service/DB change; real/private data risk; governance/docs/release files
touched; forbidden files staged; data/jobs.db or creds staged; new dependency; Pipeline
rebuilt rather than excluded; unexplained build/validation failure; scope creep beyond
visual-foundation work; need to touch backend/Python.

## Required validation
- .\scripts\review-atlas-visual.ps1 -BuildLabel p7p5e-local -SearchTerms (minification-safe
  tokens: route paths / user-facing label text / stable CSS class names — NOT React
  component identifiers, which the production build strips)
- cd frontend; npm run build (must pass; if a dependency is missing, STOP + report — do not
  npm install)
- git diff --stat; git diff --check; git status --short --untracked-files=all (confirm no
  forbidden files staged)
- pytest ONLY if any Python changed (it must not; flag loudly as a stop-condition if Anna
  finds she needs to touch backend/Python)

## Commit rule
Commit locally ONLY if clean, scoped to this visual-foundation package, and validation
passes. Suggested message: feat(p7p5e): rebuild ATLAS visual foundation (adjust to match
actual diff). DO NOT push.

## Acceptance note
This package is NOT accepted on implementation report alone. Visual acceptance is Sara's /
the user's call after screenshots — never Ash's or Anna's. Implementation ends at honest
build + validation + synthesis.
