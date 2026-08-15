#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC2B1RunDir = "",
    [string]$GateC3RunDir = "",
    [string]$GateC3ARunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell",
    [int]$ChunkCells = 5000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

function Resolve-GateRunDir {
    param([string]$RunDir, [string]$PointerPath, [string]$GateName)
    if ([string]::IsNullOrWhiteSpace($RunDir)) {
        if (-not (Test-Path -LiteralPath $PointerPath)) {
            throw "$GateName pointer not found: $PointerPath"
        }
        $PointerLine = Get-Content -LiteralPath $PointerPath | Select-Object -First 1
        if ($PointerLine -notmatch '^run_dir=(.+)$') {
            throw "Invalid $GateName pointer: $PointerLine"
        }
        $RunDir = $Matches[1]
    }
    if (-not [System.IO.Path]::IsPathRooted($RunDir)) {
        $RunDir = Join-Path $ProjectRoot $RunDir
    }
    return [System.IO.Path]::GetFullPath($RunDir)
}

$GateC2B1RunDir = Resolve-GateRunDir `
    -RunDir $GateC2B1RunDir `
    -PointerPath (Join-Path $ProjectRoot "phase17_v7\gateC2B1\_LATEST_GATE_C2B1.txt") `
    -GateName "Gate C2B1"
$GateC3RunDir = Resolve-GateRunDir `
    -RunDir $GateC3RunDir `
    -PointerPath (Join-Path $ProjectRoot "phase17_v7\gateC3\_LATEST_GATE_C3.txt") `
    -GateName "Gate C3"
$GateC3ARunDir = Resolve-GateRunDir `
    -RunDir $GateC3ARunDir `
    -PointerPath (Join-Path $ProjectRoot "phase17_v7\gateC3A\_LATEST_GATE_C3A.txt") `
    -GateName "Gate C3A"

$RawH5ad = Join-Path $GateC2B1RunDir "04_full_raw_counts.h5ad"
if (-not (Test-Path -LiteralPath $RawH5ad)) {
    throw "Gate C2B1 raw-count H5AD not found: $RawH5ad"
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC4A\$(Get-Date -Format 'yyyyMMdd_HHmmss')_raw_pseudobulk_freeze"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot $OutputDir
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$CondaCandidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "C:\ProgramData\miniforge3\Scripts\conda.exe"
)
$PathConda = Get-Command conda -ErrorAction SilentlyContinue
if ($null -ne $PathConda) { $CondaCandidates += $PathConda.Source }
$CondaExe = $CondaCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    throw "No conda executable found. Install Miniforge or expose conda on PATH."
}

Write-Host "[1/2] Extracting dual-branch raw-count pseudobulks and freezing designs..." -ForegroundColor Cyan
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $ProjectRoot "audit_tools\phase17_c4a_01_extract_raw_pseudobulk.py") `
    --raw-h5ad $RawH5ad `
    --gate-c2b1-dir $GateC2B1RunDir `
    --gate-c3-dir $GateC3RunDir `
    --gate-c3a-dir $GateC3ARunDir `
    --output-dir $OutputDir `
    --chunk-cells $ChunkCells
if ($LASTEXITCODE -ne 0) {
    throw "Gate C4A raw-count extraction failed with exit code $LASTEXITCODE"
}

Write-Host "[2/2] Reviewing support and freezing Gate C4A authorization..." -ForegroundColor Cyan
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $ProjectRoot "audit_tools\phase17_c4a_02_review_freeze.py") `
    --run-dir $OutputDir `
    --raw-h5ad $RawH5ad `
    --gate-c3-dir $GateC3RunDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C4A review failed with exit code $LASTEXITCODE"
}

$PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC4A"
New-Item -ItemType Directory -Force -Path $PointerDir | Out-Null
$PortableRunDir = "phase17_v7\gateC4A\" + (Split-Path -Leaf $OutputDir)
Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C4A.txt") `
    -Value "run_dir=$PortableRunDir" -Encoding UTF8

Write-Host "Gate C4A workflow completed:" -ForegroundColor Green
Write-Host (Join-Path $OutputDir "14_GATE_C4A_ADVISOR_DECISION.md")
