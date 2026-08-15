#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC2B2RunDir = "",
    [string]$GateC2B4RunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell",
    [int]$MinimumCells = 50
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

function Resolve-GateRunDir {
    param(
        [string]$RunDir,
        [string]$PointerPath,
        [string]$GateName
    )
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

$GateC2B2RunDir = Resolve-GateRunDir `
    -RunDir $GateC2B2RunDir `
    -PointerPath (Join-Path $ProjectRoot "phase17_v7\gateC2B2\_LATEST_GATE_C2B2.txt") `
    -GateName "Gate C2B2"
$GateC2B4RunDir = Resolve-GateRunDir `
    -RunDir $GateC2B4RunDir `
    -PointerPath (Join-Path $ProjectRoot "phase17_v7\gateC2B4\_LATEST_GATE_C2B4.txt") `
    -GateName "Gate C2B4"

$C2B4DecisionPath = Join-Path $GateC2B4RunDir "06_GATE_C2B4_ADVISOR_DECISION.json"
if (-not (Test-Path -LiteralPath $C2B4DecisionPath)) {
    throw "Gate C2B4 decision not found: $C2B4DecisionPath"
}
$C2B4Decision = Get-Content -LiteralPath $C2B4DecisionPath -Raw | ConvertFrom-Json
if ($C2B4Decision.decision -ne "PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED") {
    throw "Gate C2B4 has not authorized Gate C3: $($C2B4Decision.decision)"
}
if (-not [bool]$C2B4Decision.outcome_unlock_authorized) {
    throw "Gate C2B4 outcome unlock is false."
}

$PrimaryH5ad = Join-Path $GateC2B2RunDir "06_primary_all_cells_representation.h5ad"
$SourceH5ad = Join-Path $ProjectRoot "Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad"
foreach ($RequiredPath in @($PrimaryH5ad, $SourceH5ad)) {
    if (-not (Test-Path -LiteralPath $RequiredPath)) {
        throw "Required Gate C3 input not found: $RequiredPath"
    }
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC3\$(Get-Date -Format 'yyyyMMdd_HHmmss')_metadata_design"
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

Write-Host "Joining protected metadata by exact cell ID and freezing Gate C3 designs..." -ForegroundColor Cyan
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $ProjectRoot "audit_tools\phase17_c3_01_unlock_metadata_and_freeze_design.py") `
    --primary-h5ad $PrimaryH5ad `
    --source-h5ad $SourceH5ad `
    --gate-c2b4-dir $GateC2B4RunDir `
    --output-dir $OutputDir `
    --minimum-cells $MinimumCells
if ($LASTEXITCODE -ne 0) {
    throw "Gate C3 metadata/design audit failed with exit code $LASTEXITCODE"
}

$PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC3"
New-Item -ItemType Directory -Force -Path $PointerDir | Out-Null
$PortableRunDir = "phase17_v7\gateC3\" + (Split-Path -Leaf $OutputDir)
Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C3.txt") `
    -Value "run_dir=$PortableRunDir" -Encoding UTF8

Write-Host "Gate C3 metadata/design workflow completed:" -ForegroundColor Green
Write-Host (Join-Path $OutputDir "15_GATE_C3_METADATA_AUDIT.md")
