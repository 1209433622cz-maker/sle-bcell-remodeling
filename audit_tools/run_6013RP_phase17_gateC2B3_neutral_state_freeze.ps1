#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$PythonExe = "",
    [string]$GateC2B2RunDir = "",
    [string]$ResumeRunDir = "",
    [int]$Replicates = 20,
    [double]$ResampleFraction = 0.8,
    [int]$MaxCells = 0
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

if ([string]::IsNullOrWhiteSpace($GateC2B2RunDir)) {
    $Pointer = Join-Path $ProjectRoot "phase17_v7\gateC2B2\_LATEST_GATE_C2B2.txt"
    if (-not (Test-Path -LiteralPath $Pointer)) { throw "Gate C2B2 pointer not found: $Pointer" }
    $PointerLine = Get-Content -LiteralPath $Pointer | Select-Object -First 1
    if ($PointerLine -notmatch '^run_dir=(.+)$') { throw "Invalid Gate C2B2 pointer: $PointerLine" }
    $GateC2B2RunDir = $Matches[1]
}
if (-not [System.IO.Path]::IsPathRooted($GateC2B2RunDir)) {
    $GateC2B2RunDir = Join-Path $ProjectRoot $GateC2B2RunDir
}
$GateC2B2RunDir = [System.IO.Path]::GetFullPath($GateC2B2RunDir)
$C2B2DecisionPath = Join-Path $GateC2B2RunDir "26_GATE_C2B2_ADVISOR_DECISION.json"
if (-not (Test-Path -LiteralPath $C2B2DecisionPath)) {
    throw "Gate C2B2 advisor decision is missing: $C2B2DecisionPath"
}
$C2B2Decision = Get-Content -LiteralPath $C2B2DecisionPath -Raw | ConvertFrom-Json
if ($C2B2Decision.decision -ne "PASS_TO_C2B3_WITH_R04_IDENTITY_BACKBONE") {
    throw "Gate C2B2 has not authorized C2B3: $($C2B2Decision.decision)"
}

$GateC2B1Pointer = Join-Path $ProjectRoot "phase17_v7\gateC2B1\_LATEST_GATE_C2B1.txt"
$GateC2B1Line = Get-Content -LiteralPath $GateC2B1Pointer | Select-Object -First 1
if ($GateC2B1Line -notmatch '^run_dir=(.+)$') { throw "Invalid Gate C2B1 pointer: $GateC2B1Line" }
$GateC2B1RunDir = $Matches[1]
if (-not [System.IO.Path]::IsPathRooted($GateC2B1RunDir)) {
    $GateC2B1RunDir = Join-Path $ProjectRoot $GateC2B1RunDir
}

if ([string]::IsNullOrWhiteSpace($ResumeRunDir)) {
    if ($MaxCells -gt 0) {
        $RunDir = Join-Path $ProjectRoot "phase17_v7\gateC2B3\_software_test_${MaxCells}"
    } else {
        $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $RunDir = Join-Path $ProjectRoot "phase17_v7\gateC2B3\${Stamp}_neutral_state_freeze"
    }
} else {
    $RunDir = [System.IO.Path]::GetFullPath($ResumeRunDir)
}
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$PrimaryH5ad = Join-Path $GateC2B2RunDir "06_primary_all_cells_representation.h5ad"
$RawH5ad = Join-Path $GateC2B1RunDir "04_full_raw_counts.h5ad"
$SourceH5ad = Join-Path $ProjectRoot "Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad"
$CandidateProfiles = Join-Path $ProjectRoot "phase17_v7\gateC2B2_prechecks\blineage_extraction_completeness\07_blineage_candidate_gene_profiles.csv.gz"
foreach ($RequiredFile in @($PrimaryH5ad, $RawH5ad, $SourceH5ad, $CandidateProfiles)) {
    if (-not (Test-Path -LiteralPath $RequiredFile)) { throw "Required input not found: $RequiredFile" }
}

$ExpectedAnalysisCells = if ($MaxCells -gt 0) { $MaxCells } else { 150402 }
$ExpectedTestMode = $MaxCells -gt 0
$ResamplingReusable = $false
$ResamplingStatusPath = Join-Path $RunDir "06_RESAMPLING_STATUS.json"
if (Test-Path -LiteralPath $ResamplingStatusPath) {
    try {
        $Status = Get-Content -LiteralPath $ResamplingStatusPath -Raw | ConvertFrom-Json
        $ResamplingReusable = (
            [bool]$Status.test_mode -eq $ExpectedTestMode -and
            [int]$Status.analysis_cells -eq $ExpectedAnalysisCells -and
            [int]$Status.replicates -eq $Replicates -and
            [Math]::Abs([double]$Status.fraction - $ResampleFraction) -lt 0.000001
        )
    } catch { $ResamplingReusable = $false }
}
if ($ResamplingReusable) {
    Write-Host "[1/4] Reusing validated graph-resampling checkpoint." -ForegroundColor Yellow
} else {
    Write-Host "[1/4] Repeated disease-blind graph resampling..." -ForegroundColor Cyan
    & $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_11_resampling_stability.py") `
        --primary-h5ad $PrimaryH5ad `
        --output-dir $RunDir `
        --replicates $Replicates `
        --fraction $ResampleFraction `
        --max-cells $MaxCells
    if ($LASTEXITCODE -ne 0) { throw "C2B3 resampling failed with exit code $LASTEXITCODE" }
}

$ReferenceCap = if ($MaxCells -gt 0) { $MaxCells } else { 0 }
$MappingReusable = $false
$MappingStatusPath = Join-Path $RunDir "10_CANDIDATE_MAPPING_DECISION.json"
if (Test-Path -LiteralPath $MappingStatusPath) {
    try {
        $Status = Get-Content -LiteralPath $MappingStatusPath -Raw | ConvertFrom-Json
        $MappingReusable = (
            $Status.decision -eq "MAPPING_COMPLETE_NO_AUTOMATIC_APPEND" -and
            [bool]$Status.test_mode -eq $ExpectedTestMode -and
            [int]$Status.reference_cells -eq $ExpectedAnalysisCells -and
            [int]$Status.candidates -eq 768
        )
    } catch { $MappingReusable = $false }
}
if ($MappingReusable) {
    Write-Host "[2/4] Reusing validated outside-label candidate mapping." -ForegroundColor Yellow
} else {
    Write-Host "[2/4] Mapping outside-label B-lineage candidates..." -ForegroundColor Cyan
    & $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_12_map_blineage_candidates.py") `
        --source-h5ad $SourceH5ad `
        --primary-h5ad $PrimaryH5ad `
        --candidate-profiles $CandidateProfiles `
        --output-dir $RunDir `
        --max-reference-cells $ReferenceCap
    if ($LASTEXITCODE -ne 0) { throw "C2B3 candidate mapping failed with exit code $LASTEXITCODE" }
}

$MarkerReusable = $false
$MarkerStatusPath = Join-Path $RunDir "14_MARKER_RANKING_STATUS.json"
if (Test-Path -LiteralPath $MarkerStatusPath) {
    try {
        $Status = Get-Content -LiteralPath $MarkerStatusPath -Raw | ConvertFrom-Json
        $MarkerReusable = (
            [bool]$Status.test_mode -eq $ExpectedTestMode -and
            [int]$Status.analysis_cells -eq $ExpectedAnalysisCells -and
            [int]$Status.genes -eq 30172
        )
    } catch { $MarkerReusable = $false }
}
if ($MarkerReusable) {
    Write-Host "[3/4] Reusing validated full-gene marker ranking." -ForegroundColor Yellow
} else {
    Write-Host "[3/4] Ranking full-gene neutral markers..." -ForegroundColor Cyan
    & $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_13_rank_neutral_markers.py") `
        --raw-h5ad $RawH5ad `
        --primary-h5ad $PrimaryH5ad `
        --output-dir $RunDir `
        --max-cells $MaxCells
    if ($LASTEXITCODE -ne 0) { throw "C2B3 marker ranking failed with exit code $LASTEXITCODE" }
}

Write-Host "[4/4] Reviewing the neutral-state freeze contract..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_14_review_gatec2b3.py") `
    --run-dir $RunDir
if ($LASTEXITCODE -ne 0) { throw "C2B3 review failed with exit code $LASTEXITCODE" }

if ($MaxCells -eq 0) {
    $PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC2B3"
    $PortableRunDir = "phase17_v7\gateC2B3\" + (Split-Path -Leaf $RunDir)
    Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C2B3.txt") `
        -Value "run_dir=$PortableRunDir" -Encoding UTF8
}

Write-Host "Gate C2B3 workflow completed:" -ForegroundColor Green
Write-Host (Join-Path $RunDir "16_GATE_C2B3_ADVISOR_REVIEW.md")
