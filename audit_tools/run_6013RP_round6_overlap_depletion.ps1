param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputDir = "",
    [string]$RscriptPath = "C:\Program Files\R\R-4.6.0\bin\Rscript.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\round6_q1_robustness\20260825_overlap_depletion"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if (-not (Test-Path -LiteralPath $RscriptPath)) {
    throw "Rscript was not found: $RscriptPath"
}

$Script = Join-Path $PSScriptRoot "phase17_round6_01_overlap_depletion_sensitivity.R"
if (-not (Test-Path -LiteralPath $Script)) {
    throw "Analysis script was not found: $Script"
}

Write-Host "Running frozen STAT1/STAT2 overlap-depletion sensitivity..."
& $RscriptPath $Script $ProjectRoot $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Overlap-depletion sensitivity failed with exit code $LASTEXITCODE"
}

Write-Host "Round 6 overlap-depletion outputs:"
Write-Host $OutputDir
