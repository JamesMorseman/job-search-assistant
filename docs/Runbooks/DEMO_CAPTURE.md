# Demo Capture Runbook

This runbook defines the future operator workflow for capturing ATLAS demo
screenshots safely.

Phase 7 Package 4 does not authorize committing screenshot files. It also does
not authorize public release, demo seed code, fixture files, frontend demo
mode, database changes, or runtime behavior changes.

## Purpose

The goal is to capture ATLAS surfaces using fictional demo state while keeping
private job-search records, credentials, local paths, generated documents,
email content, Drive links, and candidate details out of screenshots.

## Prerequisites

- The Package 3 launcher works locally:

```powershell
.\scripts\start-atlas.ps1
```

- The frontend is built for ATLAS Desktop:

```powershell
cd frontend
npm run build
cd ..
```

- Demo data is loaded according to `docs/Runbooks/DEMO_DATA.md`.
- No real records are visible in any surface being captured.
- LLM-backed surfaces have a valid local `.env` value configured before
  capture.
- The browser window is clean: no private tabs, bookmark bar, account avatar,
  download shelf, or private extension UI.

## Pre-Capture Checklist

- Confirm `docs/Public/SCREENSHOTS.md` has the target surface listed.
- Confirm the visible data is fictional/demo/sample only.
- Confirm no real employer, recruiter, application, or candidate information is
  visible.
- Confirm terminal prompts and local paths are cropped or masked.
- Confirm no browser profile/account indicators are visible.
- Confirm dates and counts are fictionalized.
- Confirm no generated resumes, cover letters, Gmail/email content, or Google
  Drive links are visible.
- Store captures locally outside the repo until approval.

## Capture Sequence

Capture in this priority order:

1. Command Center.
2. Radar.
3. Ask Atlas.
4. Opportunity Detail Surface.
5. Pipeline Workspace.
6. CLI launcher terminal output.
7. Dashboard Metrics.
8. Dashboard Pipeline Runs.

Stop if any surface shows private data. Fix the demo state before continuing.

## Surface Notes

### Command Center

Show the full workspace with fictional opportunity signal, pipeline summary,
Recommendations, and Focus objects. Recommendations and Focus objects should
be included here unless a future package authorizes standalone captures.

### Radar

Show fictional opportunity cards and safe filter/search state. Do not show real
apply URLs, scraped descriptions, source IDs, or employer names.

### Ask Atlas

Use the fictional investigation prompt from `docs/Runbooks/DEMO_DATA.md`.
Capture only if the answer references fictional demo records and contains no
private context.

### Opportunity Detail Surface

Use a fictional opportunity with complete but safe fields. Avoid any visible
real external link, generated document link, or copied job description.

### Pipeline Workspace

Use fictional opportunity progression and fictional run context. Avoid real
application states, response dates, or operator notes.

### CLI Launcher Terminal Output

Show the local launcher command, diagnostics result, ATLAS URL, and Ctrl+C stop
instruction if available. Crop or mask the prompt and any path. Use examples
like:

```text
C:\Users\<user>\Documents\job-search-assistant
```

Do not show a real Windows username.

### Dashboard Metrics

Use fictional aggregate counts only. If any metric includes real application
history, skip the surface.

### Dashboard Pipeline Runs

Use fictional run records or redacted records cleared for review. Do not show
real error notes, private paths, credential diagnostics, or source metadata.

## Redaction Checklist

Before review, confirm the screenshot does not show:

- Real employer or recruiter names.
- Real job titles, job IDs, descriptions, or apply URLs.
- Real application states or follow-up records.
- Real LLM rationale.
- Candidate PII.
- Credential values.
- `.env` contents.
- Private profile contents.
- OAuth credential contents.
- Gmail/email content.
- Google Drive links.
- Generated resumes or cover letters.
- Capstone source files.
- Real Windows username or local private paths.
- Browser account/profile details.

## Terminal Path Masking

Mask or crop terminal prompts. Acceptable documentation-style path example:

```text
C:\Users\<user>\Documents\job-search-assistant
```

Do not expose machine names, shell history, environment output, or private
local paths.

## File Naming Conventions

Use clear hypothetical names while files remain local and uncommitted:

```text
atlas_command_center_runtime_v1.png
atlas_radar_runtime_v1.png
atlas_ask_atlas_runtime_v1.png
atlas_opportunity_detail_runtime_v1.png
atlas_pipeline_runtime_v1.png
atlas_cli_launcher_runtime_v1.png
atlas_dashboard_metrics_runtime_v1.png
atlas_dashboard_pipeline_runs_runtime_v1.png
```

These files are not committed in Package 4.

## Storage Before Approval

Keep screenshot files in local offline storage outside the repository until
Leah redaction review and Project Master approval are complete.

If screenshots are later authorized, runtime captures are expected to belong
under `docs/Artifacts/Images/` or another governance-approved artifact path.
Do not create that directory in Package 4.

## Approval Gate

Before any screenshot commit:

- Complete the pre-capture checklist.
- Complete the redaction checklist.
- Confirm every visible record is fictional/demo/sample or approved redacted
  local data.
- Obtain Leah redaction review.
- Obtain Project Master approval.

## Package 4 Does Not Authorize

- Screenshot files.
- Image files.
- Contact sheets.
- `docs/Artifacts/`.
- Fixture JSON.
- Demo seed scripts.
- Demo mode flags.
- Database files.
- Runtime behavior changes.
- Public release.
