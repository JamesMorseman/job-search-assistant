# Screenshot Rules

This file defines placeholder screenshot guidance only. Phase 7 Package 2 does
not add screenshots, image files, or screenshot filenames.

Any future screenshot package requires final screenshot approval after privacy
redaction review.

## Recommended Screenshot List

- Command Center: demonstrate operational overview, priority signals, recent
  pipeline context, recommendations, and Focus state.
- Radar: demonstrate opportunity discovery, signal scanning, filtering, and
  opportunity awareness.
- Pipeline: demonstrate opportunity progression and local pipeline visibility.
- Opportunity Detail: demonstrate full opportunity context, scoring/evaluation
  fields, and operator review context.
- Ask Atlas: demonstrate investigation-oriented questions and structured
  response format.
- Dashboard Metrics: demonstrate funnel and analytics visibility without
  exposing private counts tied to real application history.
- Pipeline Runs screen: demonstrate run history, counters, status, and error
  visibility using redacted or seeded data.

## Redaction Requirements

Screenshots must not expose:

- Real candidate personal information.
- Real employer or application details.
- Gmail/email content.
- Google Drive links.
- Generated resumes or cover letters.
- Local file paths containing private identity.
- Database filenames or runtime artifacts that reveal private state.
- API credentials, tokens, or environment values.

Use seeded demo data or approved redacted local data. If redaction would make a
screen misleading, do not publish that screenshot.

## Labeling Rules

Future images must be clearly labeled as one of:

- Visual reference: a committed design/reference artifact, not a live runtime
  screenshot.
- Runtime screenshot: a captured application state from the implemented system,
  using redacted or seeded data.

Do not mix visual references and runtime screenshots without labeling them.

## Approval Gate

Before any screenshot is committed or published:

- Confirm the screenshot supports an implemented feature.
- Confirm the source data is demo or redacted.
- Confirm no prohibited private categories are visible.
- Confirm the file path and filename do not reveal private context.
- Obtain final screenshot approval from Project Master after Leah review.
