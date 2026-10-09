param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")),
    [string]$ResearchProposal = "",
    [string]$R4Package = "",
    [string]$RetrospectiveProposal = "",
    [string]$DiagnosticPackage = "",
    [string]$OutputDir = (Join-Path $ProjectRoot "phase17_v7\rp_v3_redesign\20261009_stage0")
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$ReadOnlyInputs = Join-Path $ProjectRoot "phase17_v7\rp_v3_redesign\20261009_stage0\inputs_readonly"

if ([string]::IsNullOrWhiteSpace($ResearchProposal)) {
    $RpCandidates = @(Get-ChildItem -LiteralPath $ReadOnlyInputs `
        -Filter "SLE_Bcell_RP_v3_*_20261009.docx" -File -ErrorAction SilentlyContinue)
    if ($RpCandidates.Count -eq 0) {
        $RpCandidates = @(Get-ChildItem -LiteralPath (Join-Path $env:USERPROFILE "Downloads") `
            -Filter "SLE_Bcell_RP_v3_*_20261009.docx" -File)
    }
    if ($RpCandidates.Count -ne 1) {
        throw "Expected one RP v3 DOCX in Downloads; found $($RpCandidates.Count)."
    }
    $ResearchProposal = $RpCandidates[0].FullName
}

if ([string]::IsNullOrWhiteSpace($R4Package)) {
    $R4Package = Join-Path $ReadOnlyInputs "SLE_Bcell_Submission_Package_QiTeng_R4_2026-09-29.zip"
}

if ([string]::IsNullOrWhiteSpace($RetrospectiveProposal)) {
    $RetrospectiveProposal = Join-Path $ReadOnlyInputs "SLE_Bcell_Retrospective_Doctoral_Research_Proposal.docx"
}

if ([string]::IsNullOrWhiteSpace($DiagnosticPackage)) {
    $DiagnosticCandidates = @(Get-ChildItem -LiteralPath $ReadOnlyInputs `
        -Filter "SLE_Bcell_*20261009.zip" -File | Where-Object { $_.Length -eq 2460790 })
    if ($DiagnosticCandidates.Count -eq 0) {
        $DiagnosticCandidates = @(Get-ChildItem -LiteralPath $ProjectRoot `
            -Filter "SLE_Bcell_*20261009.zip" -File | Where-Object { $_.Length -eq 2460790 })
    }
    if ($DiagnosticCandidates.Count -ne 1) {
        throw "Expected one 2,460,790-byte diagnostic ZIP in the project root; found $($DiagnosticCandidates.Count)."
    }
    $DiagnosticPackage = $DiagnosticCandidates[0].FullName
}

$Python = "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    throw "sle-bcell Python was not found at $Python"
}

& $Python (Join-Path $PSScriptRoot "rp_v3_stage0_01_freeze.py") `
    --project-root $ProjectRoot `
    --rp $ResearchProposal `
    --r4-package $R4Package `
    --retrospective-rp $RetrospectiveProposal `
    --diagnostic-package $DiagnosticPackage `
    --outdir $OutputDir

if ($LASTEXITCODE -ne 0) {
    throw "RP v3 Stage 0 freeze failed with exit code $LASTEXITCODE"
}

Write-Host "RP v3 Stage 0 outputs: $OutputDir"
