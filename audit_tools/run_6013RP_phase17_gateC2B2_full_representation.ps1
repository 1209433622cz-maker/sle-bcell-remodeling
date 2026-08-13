#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$PythonExe = "",
    [string]$ResumeRunDir = "",
    [int]$MaxCells = 0,
    [int]$NHvg = 3000,
    [int]$HarmonyMaxIter = 20,
    [double]$PrimaryResolution = 0.4,
    [switch]$PreparationOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $PythonCandidates = @(
        "C:\ProgramData\miniforge3\envs\sle-bcell-v7\python.exe",
        "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe"
    )
    $PathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $PathPython) { $PythonCandidates += $PathPython.Source }
    $PythonExe = $PythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if ([string]::IsNullOrWhiteSpace($PythonExe) -or -not (Test-Path -LiteralPath $PythonExe)) {
    throw "No usable Python environment found. Pass -PythonExe explicitly."
}

$GateC2B1Pointer = Join-Path $ProjectRoot "phase17_v7\gateC2B1\_LATEST_GATE_C2B1.txt"
if (-not (Test-Path -LiteralPath $GateC2B1Pointer)) {
    throw "Gate C2B1 pointer not found: $GateC2B1Pointer"
}
$PointerLine = Get-Content -LiteralPath $GateC2B1Pointer | Select-Object -First 1
if ($PointerLine -notmatch '^run_dir=(.+)$') {
    throw "Invalid Gate C2B1 pointer: $PointerLine"
}
$GateC2B1Dir = $Matches[1]
if (-not [System.IO.Path]::IsPathRooted($GateC2B1Dir)) {
    $GateC2B1Dir = Join-Path $ProjectRoot $GateC2B1Dir
}
if (-not (Test-Path -LiteralPath $GateC2B1Dir)) {
    $GateC2B1Dir = Join-Path $ProjectRoot ("phase17_v7\gateC2B1\" + (Split-Path -Leaf $GateC2B1Dir))
}

$InputH5ad = Join-Path $GateC2B1Dir "04_full_raw_counts.h5ad"
$DoubletScores = Join-Path $GateC2B1Dir "06_full_cell_doublet_scores.csv.gz"
$GateC2B1Decision = Join-Path $GateC2B1Dir "17_GATE_C2B1_DECISION.json"
foreach ($RequiredFile in @($InputH5ad, $DoubletScores, $GateC2B1Decision)) {
    if (-not (Test-Path -LiteralPath $RequiredFile)) { throw "Required Gate C2B1 file not found: $RequiredFile" }
}
$Decision = Get-Content -LiteralPath $GateC2B1Decision -Raw | ConvertFrom-Json
if ($Decision.decision -ne "PASS_TO_C2B2_WITH_DUAL_BRANCH") {
    throw "Gate C2B1 has not authorized C2B2: $($Decision.decision)"
}

if ([string]::IsNullOrWhiteSpace($ResumeRunDir)) {
    if ($MaxCells -gt 0) {
        $RunDir = Join-Path $ProjectRoot "phase17_v7\gateC2B2\_software_test_${MaxCells}"
    } else {
        $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $RunDir = Join-Path $ProjectRoot "phase17_v7\gateC2B2\${Stamp}_full_representation"
    }
} else {
    $RunDir = [System.IO.Path]::GetFullPath($ResumeRunDir)
}
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$PreparedH5ad = Join-Path $RunDir "03_prepared_log_union_hvg.h5ad"
$PreparationSummary = Join-Path $RunDir "04_GATE_C2B2_PREPARATION.json"
$ExpectedWorkingCells = if ($MaxCells -gt 0) {
    [Math]::Min($MaxCells, [int]$Decision.cells)
} else {
    [int]$Decision.cells
}
$PreparationIsReusable = $false
if ((Test-Path -LiteralPath $PreparedH5ad) -and (Test-Path -LiteralPath $PreparationSummary)) {
    try {
        $Prep = Get-Content -LiteralPath $PreparationSummary -Raw | ConvertFrom-Json
        $BranchNames = @($Prep.branches | ForEach-Object { $_.branch } | Sort-Object)
        $HvgCountsMatch = @($Prep.branches | Where-Object { [int]$_.n_hvg -ne $NHvg }).Count -eq 0
        $PreparationIsReusable = (
            [int]$Prep.schema_version -eq 2 -and
            $Prep.status -eq "PASS_TO_REPRESENTATION_FIT" -and
            [int]$Prep.working_cells -eq $ExpectedWorkingCells -and
            [bool]$Prep.test_mode -eq ($MaxCells -gt 0) -and
            $HvgCountsMatch -and
            ($BranchNames -join ',') -eq "isg_excluded,primary_ig_excluded" -and
            $Prep.ig_dominance_sensitivity.status -eq "NOT_EVALUABLE_SOURCE_FEATURE_SPACE"
        )
    } catch {
        $PreparationIsReusable = $false
    }
}

if (-not $PreparationIsReusable) {
    Write-Host "[1/3] Preparing disease-blind recurrent-HVG branches..." -ForegroundColor Cyan
    & $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_07_prepare_representation.py") `
        --input-h5ad $InputH5ad `
        --doublet-scores $DoubletScores `
        --output-dir $RunDir `
        --n-hvg $NHvg `
        --max-cells $MaxCells
    if ($LASTEXITCODE -ne 0) { throw "Gate C2B2 preparation failed with exit code $LASTEXITCODE" }
} else {
    Write-Host "[1/3] Reusing schema-validated HVG checkpoint: $PreparedH5ad" -ForegroundColor Yellow
}

if ($PreparationOnly) {
    Write-Host "Preparation checkpoint completed; representation fit intentionally not started." -ForegroundColor Green
    Write-Host $PreparedH5ad
    exit 0
}

Write-Host "[2/3] Fitting primary and prespecified sensitivity representations..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_08_fit_representation.py") `
    --prepared-h5ad $PreparedH5ad `
    --output-dir $RunDir `
    --harmony-max-iter $HarmonyMaxIter
if ($LASTEXITCODE -ne 0) { throw "Gate C2B2 representation fit failed with exit code $LASTEXITCODE" }

Write-Host "[3/3] Reviewing mixing, bridge consistency, markers and branch stability..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_09_review_representation.py") `
    --run-dir $RunDir `
    --primary-resolution $PrimaryResolution
if ($LASTEXITCODE -ne 0) { throw "Gate C2B2 review failed with exit code $LASTEXITCODE" }

if ($MaxCells -eq 0) {
    $PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC2B2"
    $PortableRunDir = "phase17_v7\gateC2B2\" + (Split-Path -Leaf $RunDir)
    Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C2B2.txt") `
        -Value "run_dir=$PortableRunDir" -Encoding UTF8
}

Write-Host "Gate C2B2 representation fit completed; review remains required:" -ForegroundColor Green
Write-Host (Join-Path $RunDir "21_GATE_C2B2_REVIEW.md")
