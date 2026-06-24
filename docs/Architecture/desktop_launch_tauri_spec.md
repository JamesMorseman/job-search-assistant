# Desktop Launch Experience — Tauri Wrapper Spec

## Metadata

- Document ID: `B1_DESKTOP_LAUNCH_TAURI_SPEC_DOC_01`
- Package: `B1-DESKTOP-LAUNCH-TAURI-SCOPE-OR-PROTOTYPE-01`
- Status: bounded implementation spec only — **no Tauri build was attempted or
  performed**. This document does not claim installer, packaging, distribution,
  or release readiness of any kind.
- Owner: Main Ash / user (James)
- Authored by: Anna Repo Agent, away-run implementation pass
- This document does **not** authorize a build, install, package, screenshot,
  release, or acceptance claim. See "Non-Authorization Notice" at the end.

---

## 1. Why This Is a Spec, Not an Implementation

This machine's PATH has no `cargo` and no `rustc` (verified live: `which cargo`
and `which rustc` both report "command not found"; `cargo --version` and
`rustc --version` both fail with "command not found"). Tauri's build pipeline
requires a working Rust toolchain (`cargo`, `rustc`, plus the Tauri CLI and,
on Windows, the MSVC Build Tools / WebView2 runtime) to compile the native
shell. None of that is installed here.

Per this package's authorization, since Tauri is confirmed not feasible on
this machine, the correct deliverable is a concrete, bounded implementation
spec — exact steps, dependencies, file layout, and what a future package
would do — rather than a partial or simulated build attempt.

---

## 2. Current State (Verified Live)

- ATLAS Desktop is a React/Vite SPA at `frontend/` that builds to
  `frontend/dist/` (`npm run build` — confirmed present at
  `frontend/package.json` scripts: `dev`, `build`, `preview`).
- The backend is a FastAPI app (`job_search.dashboard.app:create_app`) served
  by uvicorn. It mounts the built frontend's static assets and serves the SPA
  shell at `/atlas` (see `job_search/dashboard/app.py`, `atlas_spa` route).
- A PowerShell launcher already exists: `scripts/start-atlas.ps1`. It runs
  `jsa check` (diagnostics gate), warns if `frontend/dist/index.html` is
  missing, then starts uvicorn in the foreground on `127.0.0.1:8000` and
  prints the ATLAS URL (`docs/Runbooks/LOCAL_LAUNCH.md` documents this fully).
- **The gap this package addresses:** today, "launching ATLAS" means opening
  a terminal, running a PowerShell script (or the raw uvicorn command), and
  then manually opening a browser tab to `http://127.0.0.1:8000/atlas`. There
  is no double-clickable desktop entrypoint and no native app window — the
  experience is a locally-hosted web page, not a desktop app, despite the
  product being framed as "ATLAS Desktop."

---

## 3. Target End State

A double-clickable local entrypoint (ideally a single `.exe` produced by
Tauri) that:

1. Starts the existing FastAPI/uvicorn backend as a child process (reusing
   `job_search.dashboard.app:create_app`, unchanged).
2. Opens a native window pointed at `http://127.0.0.1:<port>/atlas` instead
   of a browser tab — this is Tauri's core value proposition: it wraps an
   existing web frontend in a native OS window using the system WebView,
   without requiring a rewrite of the frontend.
3. Runs the existing `jsa check` diagnostics gate before showing the window,
   surfacing failures in a native dialog instead of a terminal message.
4. Shuts down the backend child process cleanly when the window is closed.

This explicitly reuses 100% of the existing backend and frontend code. Tauri
does not require porting the React app or the FastAPI service to Rust — Rust
is only the thin native shell/process-supervisor layer.

---

## 4. Why Tauri (Not Electron) — Carried Forward From Build 1 Definitions

- Tauri ships a much smaller binary (uses the OS's built-in WebView2 on
  Windows, not a bundled Chromium), which matters for "polished, finished
  app" framing.
- The existing frontend is already a vanilla Vite/React SPA with no
  Electron-specific or Tauri-specific code — it is wrapper-agnostic today,
  so adopting Tauri is additive, not a rewrite.
- This spec does not evaluate Electron in depth because the package
  instruction explicitly named Tauri as preferred; Electron would be a
  reasonable fallback if a future package later finds Tauri's Rust toolchain
  requirement to be a persistent blocker across all reasonably available
  dev/build machines.

---

## 5. Exact Dependencies a Future Implementation Package Would Need

Before any future package attempts a real Tauri build, the executing machine
must have:

1. **Rust toolchain**: `rustup` installing a stable `rustc` + `cargo`
   (`rustup-init.exe` from `https://rustup.rs`, or via `winget install
   Rustlang.Rustup`). Verify with `cargo --version` and `rustc --version`
   both succeeding.
2. **Tauri CLI**: `npm install --save-dev @tauri-apps/cli` inside `frontend/`
   (or a new top-level `desktop/` package — see Section 6), plus the Tauri
   Rust crate `tauri` added to a new `Cargo.toml`.
3. **Windows native build prerequisites**: Microsoft C++ Build Tools (MSVC,
   not MinGW — Tauri on Windows requires the MSVC toolchain) and the WebView2
   Runtime (pre-installed on most modern Windows 10/11 systems, but should be
   verified, not assumed).
4. **No new Python dependencies** — the backend is unchanged.

A future package's first concrete validation step should simply be
re-running `cargo --version` / `rustc --version` on the actual execution
machine — do not assume this spec's "not feasible here" finding still holds
on a different machine or after a future `rustup` install.

---

## 6. Proposed File Layout

```
job-search-assistant/
  frontend/                      # unchanged — existing React/Vite SPA
  desktop/                       # NEW — Tauri shell project
    src-tauri/
      Cargo.toml                 # Rust package manifest, tauri dependency
      tauri.conf.json            # window config, app identifier, build hooks
      src/
        main.rs                  # entrypoint: spawn backend, open window
        backend.rs               # child-process supervisor for uvicorn
      icons/                     # app icon set (Tauri's icon generator)
    package.json                 # thin wrapper for `npm run tauri dev/build`
```

A separate top-level `desktop/` directory (rather than nesting under
`frontend/`) is recommended so the Tauri/Rust toolchain requirement is
clearly opt-in and does not become an implicit dependency of the existing
`frontend/` Node toolchain or CI path.

---

## 7. Backend Process Supervision — The One Real Design Decision

The Rust shell needs to start and stop the existing Python backend. Two
viable approaches, in order of preference:

1. **Spawn `python -m uvicorn job_search.dashboard.app:create_app --factory
   --host 127.0.0.1 --port <port>` as a child process from Rust**
   (`std::process::Command` in `main.rs`), using the same `.venv` the rest of
   the repo already relies on. Tauri's `on_window_event` /
   `RunEvent::ExitRequested` hooks should kill the child process on window
   close. This is the lowest-risk option: it reuses the exact existing
   launch command from `scripts/start-atlas.ps1`/`docs/Runbooks/LOCAL_LAUNCH.md`
   verbatim, with no new Python entrypoint to maintain.
2. **Run `jsa check` first, synchronously, before spawning uvicorn** —
   mirrors `start-atlas.ps1`'s existing diagnostics gate. A failure should
   surface as a native dialog (Tauri's `tauri::api::dialog`) rather than
   silently failing to open a usable window.

**Explicitly out of scope / not recommended for a first pass:** rewriting the
backend as a Rust-native service, embedding Python via PyOxidizer or similar,
or bundling a Python interpreter into the Tauri binary. All of these are
real options for a later, more polished distributable build, but add
significant complexity disproportionate to "make double-click launch work
locally for the existing developer machine."

---

## 8. Validation a Future Package Should Run

1. `cargo --version` / `rustc --version` succeed on the target machine.
2. `npm run tauri dev` (from `desktop/`) opens a native window showing the
   existing ATLAS Desktop UI at `/atlas`, with the backend started
   automatically.
3. Closing the native window terminates the backend child process (verify no
   orphaned `python.exe`/`uvicorn` process remains — e.g. via Task Manager or
   `Get-Process python`).
4. `jsa check` failure (e.g. temporarily renaming `.env`) surfaces as a
   native dialog, not a silent failure or crash.
5. The existing `scripts/start-atlas.ps1` / terminal-based launch path
   continues to work unmodified — the Tauri wrapper is an additive launch
   option, not a replacement, until separately decided.

---

## 9. Explicitly Not Claimed By This Document

- No build was run. No `desktop/` directory, `Cargo.toml`, or Rust code has
  been created by this package — this document is the spec only.
- No installer, code signing, auto-update mechanism, or distribution channel
  is in scope for the first implementation pass described here.
- No claim of release readiness, packaging readiness, or "Build 1 desktop
  launch is done" — this remains an open, recommended-required item per
  `docs/Architecture/build_1_completion_roadmap.md` Section 9, item 3, until
  a future package actually implements and validates Sections 6-8 above on a
  machine with a working Rust toolchain.

## Non-Authorization Notice

This document does not authorize a build, package, install, screenshot,
release, or implementation-acceptance claim. It is scoping/planning output
only, intended to let a future package start implementation immediately
once a Rust toolchain is available, without re-deriving the dependency list,
file layout, or process-supervision design from scratch.
