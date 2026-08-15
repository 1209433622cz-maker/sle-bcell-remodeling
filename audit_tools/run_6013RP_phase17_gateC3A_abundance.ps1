#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC3RunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if ([string]::IsNullOrWhiteSpace($GateC3RunDir)) {
    $PointerPath = Join-Path $ProjectRoot "phase17_v7\gateC3\_LATEST_GATE_C3.txt"
    if (-not (Test-Path -LiteralPath $PointerPath)) {
        throw "Gate C3 pointer not found: $PointerPath"
    }
    $PointerLine = Get-Content -LiteralPath $PointerPath | Select-Object -First 1
    if ($PointerLine -notmatch '^run_dir=(.+)$') {
        throw "Invalid Gate C3 pointer: $PointerLine"
    }
    $GateC3RunDir = $Matches[1]
}
if (-not [System.IO.Path]::IsPathRooted($GateC3RunDir)) {
    $GateC3RunDir = Join-Path $ProjectRoot $GateC3RunDir
}
$GateC3RunDir = [System.IO.Path]::GetFullPath($GateC3RunDir)

$GateStatusPath = Join-Path $GateC3RunDir "00_GATE_C3_RUN_STATUS.json"
if (-not (Test-Path -LiteralPath $GateStatusPath)) {
    throw "Gate C3 status not found: $GateStatusPath"
}
$GateStatus = Get-Content -LiteralPath $GateStatusPath -Raw | ConvertFrom-Json
if ($GateStatus.status -ne "PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE") {
    throw "Gate C3 has not authorized abundance modeling: $($GateStatus.status)"
}
if (-not [bool]$GateStatus.effect_estimation_authorized) {
    throw "Gate C3 effect-estimation authorization is false."
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC3A\$(Get-Date -Format 'yyyyMMdd_HHmmss')_frozen_abundance"
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

Write-Host "Fitting Gate C3A frozen abundance models and mandatory sensitivities..." -ForegroundColor Cyan
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $ProjectRoot "audit_tools\phase17_c3_02_fit_frozen_abundance.py") `
    --gate-c3-dir $GateC3RunDir `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C3A abundance workflow failed with exit code $LASTEXITCODE"
}

$PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC3A"
New-Item -ItemType Directory -Force -Path $PointerDir | Out-Null
$PortableRunDir = "phase17_v7\gateC3A\" + (Split-Path -Leaf $OutputDir)
Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C3A.txt") `
    -Value "run_dir=$PortableRunDir" -Encoding UTF8

Write-Host "Gate C3A abundance workflow completed:" -ForegroundColor Green
Write-Host (Join-Path $OutputDir "09_GATE_C3A_ADVISOR_DECISION.md")
