#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC2B3RunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if ([string]::IsNullOrWhiteSpace($GateC2B3RunDir)) {
    $Pointer = Join-Path $ProjectRoot "phase17_v7\gateC2B3\_LATEST_GATE_C2B3.txt"
    if (-not (Test-Path -LiteralPath $Pointer)) {
        throw "Gate C2B3 pointer not found: $Pointer"
    }
    $PointerLine = Get-Content -LiteralPath $Pointer | Select-Object -First 1
    if ($PointerLine -notmatch '^run_dir=(.+)$') {
        throw "Invalid Gate C2B3 pointer: $PointerLine"
    }
    $GateC2B3RunDir = $Matches[1]
}
if (-not [System.IO.Path]::IsPathRooted($GateC2B3RunDir)) {
    $GateC2B3RunDir = Join-Path $ProjectRoot $GateC2B3RunDir
}
$GateC2B3RunDir = [System.IO.Path]::GetFullPath($GateC2B3RunDir)

$C2B3StatusPath = Join-Path $GateC2B3RunDir "06_RESAMPLING_STATUS.json"
$C2B3ReviewPath = Join-Path $GateC2B3RunDir "16_GATE_C2B3_ADVISOR_REVIEW.json"
foreach ($RequiredPath in @($C2B3StatusPath, $C2B3ReviewPath)) {
    if (-not (Test-Path -LiteralPath $RequiredPath)) {
        throw "Required Gate C2B3 input is missing: $RequiredPath"
    }
}
$C2B3Status = Get-Content -LiteralPath $C2B3StatusPath -Raw | ConvertFrom-Json
$C2B3Review = Get-Content -LiteralPath $C2B3ReviewPath -Raw | ConvertFrom-Json
if ([int]$C2B3Status.schema_version -lt 2 -or -not [bool]$C2B3Status.representation_dimension_match) {
    throw "Gate C2B3 is not a valid schema-v2 source-matched run."
}
if ($C2B3Review.decision -ne "HOLD_GATE_C2B3_REVIEW_REQUIRED") {
    throw "Gate C2B4 repair requires the preserved C2B3 HOLD decision."
}
if ([bool]$C2B3Review.outcome_unlock_authorized) {
    throw "Gate C2B3 unexpectedly authorized outcome unlock; C2B4 repair is not applicable."
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC2B4\$(Get-Date -Format 'yyyyMMdd_HHmmss')_two_level_state_repair"
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

Write-Host "Adjudicating the disease-blind two-level state model..." -ForegroundColor Cyan
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $ProjectRoot "audit_tools\phase17_c2b_15_adjudicate_two_level_model.py") `
    --c2b3-run-dir $GateC2B3RunDir `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C2B4 adjudication failed with exit code $LASTEXITCODE"
}

$PortableRunDir = "phase17_v7\gateC2B4\" + (Split-Path -Leaf $OutputDir)
$PointerDir = Join-Path $ProjectRoot "phase17_v7\gateC2B4"
New-Item -ItemType Directory -Force -Path $PointerDir | Out-Null
Set-Content -LiteralPath (Join-Path $PointerDir "_LATEST_GATE_C2B4.txt") `
    -Value "run_dir=$PortableRunDir" -Encoding UTF8

Write-Host "Gate C2B4 workflow completed:" -ForegroundColor Green
Write-Host (Join-Path $OutputDir "06_GATE_C2B4_ADVISOR_DECISION.md")
