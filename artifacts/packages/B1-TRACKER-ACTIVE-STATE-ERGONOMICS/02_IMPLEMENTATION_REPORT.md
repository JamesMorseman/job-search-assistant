# B1 Tracker Active-State Ergonomics Implementation Report

## Scope

Implemented a bounded Application Tracker default-view refinement from shared WIP baseline `0dab0a2e049fcd31361adfd46e06c3190170b12e`.

## Changes

- Default `/dashboard/tracker` now passes the active-state tuple `selected`, `applied`, `acknowledged`, `screen`, `interview`, and `offer` to the existing `TrackerService.list_tracker_rows()` filter seam.
- Explicit `?state=rejected` and `?state=ghosted` filters remain available and continue to use the existing stage-filter route behavior.
- Tracker filter copy now labels the default link as `All active`.
- Tests cover default exclusion of terminal states, explicit terminal-state filters, and the injected service call arguments.

## Boundaries Preserved

- No state-machine changes.
- No database schema changes.
- No CSS, rendering framework, component, layout, route, or navigation redesign.
- No screenshots.
- No implementation acceptance, release readiness, public/recruiter release, Rin sync, or P7P6 claim.
