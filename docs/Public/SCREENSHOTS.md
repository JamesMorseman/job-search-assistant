# Screenshot Rules

This file defines future screenshot guidance for ATLAS portfolio preparation.
Phase 7 Package 4 does not authorize committing screenshot files.

Screenshots require later Leah redaction review and Project Master approval
before any commit. This package does not authorize public release.

Use `docs/Runbooks/DEMO_DATA.md` to prepare fictional demo state and
`docs/Runbooks/DEMO_CAPTURE.md` for the capture workflow.

## Capture Priorities

Priority levels:

- P1: primary portfolio surfaces.
- P2: supporting surfaces and local launch evidence.
- P3: dashboard analytics/supporting operational views.

Recommendations and Focus objects should be captured as part of Command Center
unless a future package authorizes separate standalone captures.

## P1 Surfaces

### Command Center - P1

- Purpose: show ATLAS as Career Mission Control: current opportunity signal,
  recent pipeline context, recommendations, and Focus objects in one operating
  view.
- Safe demo state required: fictional/demo opportunities, fictional pipeline
  run summaries, sample recommendations, and sample Focus objects only.
- Redaction requirements: no real opportunity titles, employer names, counts
  tied to real history, application state, generated document links, or
  candidate details.
- Capture notes: show the full workspace with enough context to demonstrate
  overview, prioritization, Recommendations, and Focus. Avoid browser account
  indicators and private tabs.
- Type: runtime screenshot.
- Priority: P1.

### Radar - P1

- Purpose: demonstrate opportunity discovery, signal scanning, filtering, and
  opportunity awareness.
- Safe demo state required: several fictional opportunities with source set to
  demo/sample context and safe location/score fields.
- Redaction requirements: no real company names, apply URLs, source-specific
  identifiers, job descriptions, or private fit rationale.
- Capture notes: include search/filter state only if it uses fictional terms.
  Ensure selected-card preview does not reveal real details.
- Type: runtime screenshot.
- Priority: P1.

### Ask Atlas - P1

- Purpose: demonstrate investigation-oriented questions and structured response
  format rather than generic chat.
- Safe demo state required: fictional prompt, fictional attached context, and
  generated response based only on fictional records.
- Redaction requirements: no real LLM rationale, real employer context, private
  career facts, email content, or generated application-document text.
- Capture notes: configure a valid local `.env` value before capturing
  LLM-backed surfaces. Use a question from `docs/Runbooks/DEMO_DATA.md`.
- Type: runtime screenshot.
- Priority: P1.

## P2 Surfaces

### Opportunity Detail Surface - P2

- Purpose: show full opportunity context, scoring/evaluation fields, status,
  and operator review context.
- Safe demo state required: one fictional opportunity with safe scores,
  fictional company, fictional role title, fictional location, and no real
  apply link.
- Redaction requirements: no real job ID, employer name, apply URL, job
  description, generated document link, or LLM rationale from real data.
- Capture notes: prefer a record with complete but compact fictional fields so
  the surface reads as populated without showing sensitive content.
- Type: runtime screenshot.
- Priority: P2.

### Pipeline Workspace - P2

- Purpose: show opportunity progression and local pipeline visibility.
- Safe demo state required: fictional opportunity states and fictional
  pipeline run summaries only.
- Redaction requirements: no real application state history, employer names,
  response dates, or private counts.
- Capture notes: include enough rows to demonstrate status grouping without
  requiring real application data.
- Type: runtime screenshot.
- Priority: P2.

### CLI Launcher Terminal Output - P2

- Purpose: show the local Package 3 launch path, diagnostic gate, ATLAS URL,
  and Ctrl+C stop instruction.
- Safe demo state required: local launcher output only; diagnostics should not
  print credential values.
- Redaction requirements: crop or mask terminal prompts, Windows username,
  machine name, shell history, private paths, environment values, and any
  visible local account context.
- Capture notes: path examples in documentation should use
  `C:\Users\<user>\Documents\job-search-assistant`. Do not show a real Windows
  username.
- Type: runtime screenshot.
- Priority: P2.

## P3 Surfaces

### Dashboard Metrics - P3

- Purpose: show funnel and analytics visibility from the classic FastAPI
  dashboard.
- Safe demo state required: fictional aggregate data only, with counts that do
  not correspond to real application history.
- Redaction requirements: no real employer/application counts, real source
  performance, real response rates, or private timeline information.
- Capture notes: use fictionalized dates and counts. If a metric cannot be
  safely fictionalized, skip that view until a future approved demo dataset
  exists.
- Type: runtime screenshot.
- Priority: P3.

### Dashboard Pipeline Runs - P3

- Purpose: show run history, counters, status, and error visibility from the
  classic dashboard.
- Safe demo state required: fictional/demo run records or fully redacted local
  records approved for review.
- Redaction requirements: no real error notes, private file paths, source
  details, credential diagnostics, or run metadata from real application
  activity.
- Capture notes: prefer fictional completed and failed examples with safe
  metadata. Do not expose real local runtime artifacts.
- Type: runtime screenshot.
- Priority: P3.

## Visual Reference vs Runtime Screenshot

Future images must be clearly labeled as one of:

- Visual reference: a committed design/reference artifact, not a live runtime
  screenshot.
- Runtime screenshot: a captured application state from the implemented system,
  using fictional demo data or approved redacted local data.

Do not mix visual references and runtime screenshots without labeling them.
Hypothetical filenames should include surface, capture type, and version, such
as `atlas_command_center_runtime_v1.png`. Do not add actual files in this
package.

## Approval Gate

Before any screenshot is committed:

- Confirm the screenshot supports an implemented feature.
- Confirm the source data is fictional demo data or approved redacted local
  data.
- Confirm no prohibited private categories are visible.
- Confirm terminal prompts, browser account indicators, and file paths are
  masked or cropped.
- Confirm the file path and filename do not reveal private context.
- Obtain Leah redaction review.
- Obtain Project Master approval.
