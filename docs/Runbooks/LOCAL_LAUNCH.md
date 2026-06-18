# Local ATLAS Launch Runbook

This runbook covers the local Windows launcher for ATLAS:

```powershell
.\scripts\start-atlas.ps1
```

The launcher is a local operator convenience. It starts the existing FastAPI
application in the foreground so the operator does not need to remember the
full uvicorn command.

It is not an installer, packaging flow, daemon, service, scheduler, or public
release package.

## What The Launcher Does

`scripts/start-atlas.ps1`:

- Derives the repository root from the script location.
- Confirms `.venv\Scripts\jsa.exe` exists.
- Confirms `.venv\Scripts\python.exe` exists.
- Runs `.\.venv\Scripts\jsa.exe check`.
- Stops before uvicorn if diagnostics fail.
- Warns if `frontend\dist\index.html` is missing.
- Starts FastAPI with the ATLAS app factory on `127.0.0.1:8000`.
- Prints the ATLAS URL and Ctrl+C stop instruction.

## Prerequisites

- A local virtual environment exists at `.venv`.
- The package is installed in editable mode if the local `jsa.exe` entry point
  is not already present.
- `.env` is configured with valid local credentials.
- The database is initialized if needed.
- The frontend is built if using ATLAS Desktop.

Common setup commands:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\jsa.exe init-db
```

For ATLAS Desktop, build the frontend first:

```powershell
cd frontend
npm run build
cd ..
```

## PowerShell Execution Policy

For a one-time process-only bypass:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-atlas.ps1
```

For the current Windows user, allow locally authored scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## How To Run

From the repository root:

```powershell
.\scripts\start-atlas.ps1
```

If local execution policy blocks the script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-atlas.ps1
```

## Diagnostics

The launcher runs:

```powershell
.\.venv\Scripts\jsa.exe check
```

`jsa check` validates required local runtime configuration without writing
database records. It checks for required credentials and database connectivity.

If diagnostics fail, the launcher prints a clear failure message and exits
without starting uvicorn. Fix the reported items and run the launcher again.

If the OpenAI key is missing, configure a valid local `.env` value. For
dashboard-only review before a future dashboard-only launch mode exists, use
the manual uvicorn command directly and understand that LLM-dependent workflows
will still require valid credentials.

## Missing Frontend Build

If `frontend\dist\index.html` is missing, the launcher warns but continues.
The classic FastAPI dashboard can still be useful, but ATLAS Desktop at
`/atlas` may return a 404 until the frontend is built.

Build the frontend from `frontend/`:

```powershell
npm run build
```

## URLs

Open ATLAS Desktop:

```text
http://127.0.0.1:8000/atlas
```

Classic dashboard fallback:

```text
http://127.0.0.1:8000/dashboard/review-queue
```

## Stop The Server

The server runs in the foreground. Press Ctrl+C in the same terminal to stop.

## Troubleshooting

### Missing `.venv`

Create the local virtual environment and install the package before launching.

### Missing `jsa.exe`

Install the package in editable mode from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

### Missing OpenAI Key

Configure a valid local `.env` value, then rerun:

```powershell
.\.venv\Scripts\jsa.exe check
```

### Missing Database

Initialize the local database:

```powershell
.\.venv\Scripts\jsa.exe init-db
```

Then rerun the launcher.

### Frontend Not Built

Build the frontend:

```powershell
cd frontend
npm run build
cd ..
```

Then rerun the launcher.

### Port 8000 Already In Use

Stop the conflicting local process that is using port 8000, then rerun the
launcher.

This package intentionally does not add custom port selection or port conflict
detection.
