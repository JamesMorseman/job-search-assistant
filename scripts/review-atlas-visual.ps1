<#
.SYNOPSIS
    ATLAS frontend visual review reload harness (developer tooling).

.DESCRIPTION
    Rebuilds the ATLAS frontend from a clean dist/, frees the dev ports it normally
    occupies, and prints cache-busted review URLs plus a bundle freshness sanity check.

    This script does NOT start the (blocking) ATLAS server and does NOT capture
    screenshots. No screenshot/Playwright/Puppeteer automation exists in this repo and
    none is installed by this script. After running this script, start ATLAS manually
    in a separate terminal with .\scripts\start-atlas.ps1, then open the printed URLs
    and hard-refresh (Ctrl+Shift+R) to bust any browser cache.

    The bundle freshness check (-SearchTerms) is a sanity check only - it confirms a
    string appears in the built JS bundle, NOT that the UI renders or looks correct.
    It is NOT visual acceptance and NOT a substitute for a P7P6 final screenshot pass.

.PARAMETER BuildLabel
    A short label identifying this build/review pass (e.g. a package id + short SHA).
    Appended to all printed review URLs as a cache-busting query parameter.

.PARAMETER SearchTerms
    Optional list of literal strings (e.g. component names) to search for inside the
    built frontend/dist/assets/*.js bundle(s) as a bundle-freshness sanity check.

.EXAMPLE
    .\scripts\review-atlas-visual.ps1 -BuildLabel p7p5d-22e9889 -SearchTerms "command-center","radar","pipeline"

    Use minification-surviving tokens (route paths, user-facing text, CSS class names) as
    search terms. React component identifiers like "AtlasMark" are stripped by the production
    build and will always read NOT FOUND - they are not a useful freshness signal.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$BuildLabel,

    [Parameter(Mandatory = $false)]
    [string[]]$SearchTerms
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $Root "frontend"
$DistDir = Join-Path $FrontendDir "dist"
$AssetsDir = Join-Path $DistDir "assets"

Write-Host "===================================================================="
Write-Host " ATLAS visual review reload harness"
Write-Host "===================================================================="

# ---------------------------------------------------------------------------
# 1. Git status: current branch, HEAD, and ahead/behind vs origin (if tracked)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Git status --"
Push-Location $Root
try {
    $branch = (& git rev-parse --abbrev-ref HEAD).Trim()
    $headFull = (& git rev-parse HEAD).Trim()
    $headShort = (& git rev-parse --short HEAD).Trim()
    Write-Host "Branch: $branch"
    Write-Host "HEAD:   $headShort ($headFull)"

    $upstream = $null
    try {
        $upstream = (& git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null)
        if ($LASTEXITCODE -ne 0) { $upstream = $null }
    }
    catch {
        $upstream = $null
    }

    if ($upstream) {
        $upstream = $upstream.Trim()
        $counts = (& git rev-list --left-right --count "HEAD...$upstream" 2>$null)
        if ($LASTEXITCODE -eq 0 -and $counts) {
            $parts = $counts -split '\s+'
            Write-Host "Tracking: $upstream (ahead $($parts[0]), behind $($parts[1]))"
        }
        else {
            Write-Host "Tracking: $upstream (ahead/behind count unavailable)"
        }
    }
    else {
        Write-Host "Tracking: no upstream/origin tracking branch configured - skipping ahead/behind."
    }
}
finally {
    Pop-Location
}

# ---------------------------------------------------------------------------
# 2. Free local dev ports (8000 = uvicorn, 5173 = vite dev server)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Freeing local dev ports (8000, 5173) --"
foreach ($port in 8000, 5173) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop
        foreach ($conn in $conns) {
            $pid_ = $conn.OwningProcess
            try {
                $proc = Get-Process -Id $pid_ -ErrorAction Stop
                Write-Host "Port $port is held by PID $pid_ ($($proc.ProcessName)) - stopping it."
                Stop-Process -Id $pid_ -Force -ErrorAction Stop
            }
            catch {
                Write-Host "Port $port is held by PID $pid_ - could not resolve/stop process: $($_.Exception.Message)"
            }
        }
    }
    catch {
        Write-Host "Port $port has no local listener (nothing to free)."
    }
}

# ---------------------------------------------------------------------------
# 3. Clean frontend/dist
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Cleaning frontend/dist --"
if (Test-Path -LiteralPath $DistDir) {
    Remove-Item -LiteralPath $DistDir -Recurse -Force
    Write-Host "Removed: $DistDir"
}
else {
    Write-Host "Nothing to remove: $DistDir does not exist."
}

# ---------------------------------------------------------------------------
# 4. Build the frontend (no installs)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Building frontend (npm run build) --"
Push-Location $FrontendDir
try {
    & npm run build
    $buildExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($buildExitCode -ne 0) {
    Write-Host ""
    Write-Host "ERROR: 'npm run build' failed with exit code $buildExitCode."
    Write-Host "If the failure indicates a missing dependency, STOP - do not run npm install from this script."
    Write-Host "Report the failure and resolve dependency/scope questions before retrying."
    exit $buildExitCode
}

if (-not (Test-Path -LiteralPath $DistDir)) {
    Write-Host ""
    Write-Host "ERROR: frontend/dist was not produced by the build. Aborting."
    exit 1
}

Write-Host "Build succeeded. frontend/dist verified present."

# ---------------------------------------------------------------------------
# 5. Print newest built assets
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Newest built assets --"
if (Test-Path -LiteralPath $AssetsDir) {
    $newestJs = Get-ChildItem -LiteralPath $AssetsDir -Filter "*.js" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $newestCss = Get-ChildItem -LiteralPath $AssetsDir -Filter "*.css" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1

    if ($newestJs) {
        Write-Host "Newest JS:  $($newestJs.Name) (LastWriteTime: $($newestJs.LastWriteTime))"
    }
    else {
        Write-Host "Newest JS:  none found in $AssetsDir"
    }

    if ($newestCss) {
        Write-Host "Newest CSS: $($newestCss.Name) (LastWriteTime: $($newestCss.LastWriteTime))"
    }
    else {
        Write-Host "Newest CSS: none found in $AssetsDir"
    }
}
else {
    Write-Host "WARNING: $AssetsDir does not exist - no assets to list."
}

# ---------------------------------------------------------------------------
# 6. Print cache-busted review URLs (real routes only, from App.tsx)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Cache-busted review URLs --"
Write-Host "(Append ?build=$BuildLabel and hard-refresh with Ctrl+Shift+R to bust browser cache.)"
Write-Host ""
$baseUrl = "http://127.0.0.1:8000/atlas"
Write-Host "$baseUrl`?build=$BuildLabel"
Write-Host "$baseUrl/command-center?build=$BuildLabel"
Write-Host "$baseUrl/radar?build=$BuildLabel"
Write-Host "$baseUrl/pipeline?build=$BuildLabel"
Write-Host "$baseUrl/opportunity-detail?build=$BuildLabel"
Write-Host "$baseUrl/ask-atlas?build=$BuildLabel"
Write-Host "$baseUrl/opportunities/:jobId?build=$BuildLabel   (note: requires a real jobId in place of :jobId)"

# ---------------------------------------------------------------------------
# 7. Manual start instructions (this script never starts the blocking server)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Manual start instructions --"
Write-Host "This script does not start ATLAS (the canonical start command blocks)."
Write-Host "In a SEPARATE terminal, run:"
Write-Host "    .\scripts\start-atlas.ps1"
Write-Host "Then open the URLs above in your browser and hard-refresh (Ctrl+Shift+R) on each."

# ---------------------------------------------------------------------------
# 8. Bundle freshness sanity check (NOT visual acceptance)
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Bundle freshness sanity check --"
Write-Host "NOTE: this only confirms a string literal exists in the built JS bundle."
Write-Host "It is a sanity check, NOT visual acceptance, and NOT a substitute for manual review."
if ($SearchTerms -and $SearchTerms.Count -gt 0) {
    if (-not (Test-Path -LiteralPath $AssetsDir)) {
        Write-Host "Cannot run freshness check: $AssetsDir does not exist."
    }
    else {
        $jsFiles = Get-ChildItem -LiteralPath $AssetsDir -Filter "*.js" -ErrorAction SilentlyContinue
        if (-not $jsFiles) {
            Write-Host "Cannot run freshness check: no .js files found in $AssetsDir."
        }
        else {
            foreach ($term in $SearchTerms) {
                $match = $jsFiles | Select-String -SimpleMatch -Pattern $term -ErrorAction SilentlyContinue
                if ($match) {
                    Write-Host "FOUND:     '$term'"
                }
                else {
                    Write-Host "NOT FOUND: '$term'"
                }
            }
            Write-Host ""
            Write-Host "NOTE: production builds are minified - React component identifiers"
            Write-Host "(e.g. 'AtlasMark', 'RecommendationCard') are renamed/stripped and will read"
            Write-Host "NOT FOUND even when present. For a meaningful freshness signal, search for"
            Write-Host "tokens that survive minification: route paths (e.g. 'command-center', 'radar'),"
            Write-Host "user-facing label text, or stable CSS class names - not source symbol names."
        }
    }
}
else {
    Write-Host "No -SearchTerms supplied - skipping freshness check."
}

# ---------------------------------------------------------------------------
# 9. Screenshot capture note
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "-- Screenshot capture --"
Write-Host "Intentionally skipped. No Playwright/Puppeteer/screenshot automation exists in this"
Write-Host "repo and none was installed by this script. Use the printed URLs with a manual"
Write-Host "hard-refresh instead. Screenshots captured this way are review aids only - they are"
Write-Host "NOT P7P6 final acceptance screenshots."

Write-Host ""
Write-Host "===================================================================="
Write-Host " Done."
Write-Host "===================================================================="
