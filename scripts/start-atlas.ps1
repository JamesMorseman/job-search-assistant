Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$JsaExe = Join-Path $Root ".venv\Scripts\jsa.exe"
$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"
$FrontendIndex = Join-Path $Root "frontend\dist\index.html"
$AtlasUrl = "http://127.0.0.1:8000/atlas"

if (-not (Test-Path -LiteralPath $JsaExe)) {
    Write-Host "ERROR: Missing local launcher dependency: .venv\Scripts\jsa.exe. Create the local virtual environment and install the package before launching ATLAS."
    exit 1
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    Write-Host "ERROR: Missing local Python executable: .venv\Scripts\python.exe. Create the local virtual environment before launching ATLAS."
    exit 1
}

Write-Host "Running ATLAS diagnostics..."
Push-Location $Root
try {
    & $JsaExe check
    $CheckExitCode = $LASTEXITCODE
    if ($CheckExitCode -ne 0) {
        Write-Host "ERROR: ATLAS diagnostics failed. Fix the reported items, then run scripts\start-atlas.ps1 again."
        exit $CheckExitCode
    }

    if (-not (Test-Path -LiteralPath $FrontendIndex)) {
        Write-Warning "frontend\dist\index.html is missing. ATLAS Desktop may return 404 until the frontend is built."
    }

    Write-Host "Starting ATLAS..."
    Write-Host "Open: $AtlasUrl"
    Write-Host "Press Ctrl+C to stop."

    & $PythonExe -m uvicorn job_search.dashboard.app:create_app --factory --host 127.0.0.1 --port 8000
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
