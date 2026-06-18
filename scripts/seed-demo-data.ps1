$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$SeedScript = Join-Path $RepoRoot "scripts\seed_demo_data.py"

if (-not (Test-Path $Python)) {
    throw "Missing local Python executable at $Python. Create .venv and install the project first."
}

& $Python $SeedScript @args
