param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputDir = "",
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\rp_v3_redesign\20261010_wp2_effect_free_prefit_v1"
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)

if (Test-Path -LiteralPath $OutputDir) {
    throw "Output directory already exists. Use a new path or explicitly archive the prior run: $OutputDir"
}

$PrefitScript = Join-Path $PSScriptRoot "rp_v3_wp2_01_effect_free_prefit.py"
$ReviewScript = Join-Path $PSScriptRoot "rp_v3_wp2_02_review_prefit.py"

Write-Host "[1/3] Running effect-free WP2 structural preflight..."
& $PythonExe $PrefitScript --project-root $ProjectRoot --output $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "WP2 structural preflight failed with exit code $LASTEXITCODE"
}

Write-Host "[2/3] Freezing target, scenario and acceptance registries..."
& $PythonExe $ReviewScript --project-root $ProjectRoot --prefit-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "WP2 prefit review failed with exit code $LASTEXITCODE"
}

Write-Host "[3/3] Running focused WP2 prefit tests..."
& $PythonExe -m unittest "$PSScriptRoot\test_rp_v3_wp2_prefit.py" -v
if ($LASTEXITCODE -ne 0) {
    throw "WP2 prefit tests failed with exit code $LASTEXITCODE"
}

Write-Host "WP2 effect-free preflight completed:"
Write-Host (Join-Path $OutputDir "11_WP2_PREFIT_ADVISOR_REVIEW.md")
