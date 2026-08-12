#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$PythonExe = "",
    [string]$ResumeRunDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

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

$ToolDir = Join-Path $ProjectRoot "audit_tools"
$LatestGateC1 = Join-Path $ProjectRoot "phase17_v7\gateC1\_LATEST_GATE_C1.txt"
if (-not (Test-Path -LiteralPath $LatestGateC1)) {
    throw "Gate C1 pointer not found: $LatestGateC1"
}
$GateC1Line = Get-Content -LiteralPath $LatestGateC1 | Select-Object -First 1
if ($GateC1Line -notmatch '^run_dir=(.+)$') {
    throw "Invalid Gate C1 pointer: $GateC1Line"
}
$GateC1Dir = $Matches[1]
if (-not (Test-Path -LiteralPath $GateC1Dir)) {
    $PortableGateC1Dir = Join-Path $ProjectRoot ("phase17_v7\gateC1\" + (Split-Path -Leaf $GateC1Dir))
    if (Test-Path -LiteralPath $PortableGateC1Dir) { $GateC1Dir = $PortableGateC1Dir }
}

if ([string]::IsNullOrWhiteSpace($ResumeRunDir)) {
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $RunDir = Join-Path $ProjectRoot "phase17_v7\gateC2B1\${Stamp}_full_library_doublets"
} else {
    $RunDir = [System.IO.Path]::GetFullPath($ResumeRunDir)
}
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$FullRaw = Join-Path $RunDir "04_full_raw_counts.h5ad"
if (-not (Test-Path -LiteralPath $FullRaw)) {
    Write-Host "[1/4] Extracting all hard-QC-passing raw counts..." -ForegroundColor Cyan
    & $PythonExe (Join-Path $ToolDir "phase17_c2b_01_prepare_full.py") `
        --project-root $ProjectRoot `
        --gatec1-dir $GateC1Dir `
        --output-dir $RunDir
    if ($LASTEXITCODE -ne 0) {
        throw "Gate C2B-01 failed with exit code $LASTEXITCODE"
    }
} else {
    Write-Host "[1/4] Reusing existing full raw object: $FullRaw" -ForegroundColor Yellow
}

Write-Host "[2/4] Running resumable residual Scrublet diagnostics on complete libraries..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ToolDir "phase17_c2b_02_full_library_doublets.py") `
    --input-h5ad $FullRaw `
    --output-dir $RunDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C2B-02 failed with exit code $LASTEXITCODE"
}

Write-Host "[3/4] Building multimetric residual doublet review..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ToolDir "phase17_c2b_03_review_residual_doublets.py") `
    --input-h5ad $FullRaw `
    --output-dir $RunDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C2B-03 review failed with exit code $LASTEXITCODE"
}

Write-Host "[4/4] Applying the programmatic Gate C2B1 decision contract..." -ForegroundColor Cyan
& $PythonExe (Join-Path $ToolDir "phase17_c2b_05_finalize_gatec2b1.py") `
    --run-dir $RunDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C2B1 finalization failed with exit code $LASTEXITCODE"
}

$PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC2B1"
New-Item -ItemType Directory -Force -Path $PointerDir | Out-Null
$PortableRunDir = "phase17_v7\gateC2B1\" + (Split-Path -Leaf $RunDir)
Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C2B1.txt") `
    -Value "run_dir=$PortableRunDir" -Encoding UTF8

Write-Host "Gate C2B1 completed with a programmatic cell-policy decision:" -ForegroundColor Green
Write-Host (Join-Path $RunDir "16_GATE_C2B1_DECISION.md")
