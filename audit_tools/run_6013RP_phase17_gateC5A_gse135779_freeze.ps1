#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$SourceDir = "",
    [string]$GateC4ARunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($SourceDir)) {
    $SourceDir = Join-Path $ProjectRoot "Data\processed\GSE135779_nehar_validation\source"
} elseif (-not [System.IO.Path]::IsPathRooted($SourceDir)) {
    $SourceDir = Join-Path $ProjectRoot $SourceDir
}
if ([string]::IsNullOrWhiteSpace($GateC4ARunDir)) {
    $GateC4ARunDir = Join-Path $ProjectRoot "phase17_v7\gateC4A\20260815_raw_pseudobulk_freeze"
} elseif (-not [System.IO.Path]::IsPathRooted($GateC4ARunDir)) {
    $GateC4ARunDir = Join-Path $ProjectRoot $GateC4ARunDir
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC5A\$(Get-Date -Format 'yyyyMMdd_HHmmss')_gse135779_source_mapping_freeze"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot $OutputDir
}
$SourceDir = [System.IO.Path]::GetFullPath($SourceDir)
$GateC4ARunDir = [System.IO.Path]::GetFullPath($GateC4ARunDir)
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$Candidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "$env:USERPROFILE\miniforge3\condabin\conda.bat"
)
$PathConda = Get-Command conda -ErrorAction SilentlyContinue
if ($null -ne $PathConda) { $Candidates += $PathConda.Source }
$CondaExe = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    throw "Conda was not found. Prepare the sle-bcell environment first."
}

Write-Host "[1/2] Auditing source matrices and freezing disease-blind mappings..."
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $PSScriptRoot "phase17_c5a_01_source_mapping_freeze.py") `
    --source-dir $SourceDir `
    --gate-c4a-dir $GateC4ARunDir `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) { throw "Gate C5A source/mapping freeze failed." }

Write-Host "[2/2] Independently reviewing the pre-effect freeze..."
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $PSScriptRoot "phase17_c5a_02_review_freeze.py") `
    --run-dir $OutputDir `
    --source-dir $SourceDir `
    --gate-c4a-dir $GateC4ARunDir
if ($LASTEXITCODE -ne 0) { throw "Gate C5A review failed; external effects remain locked." }

Write-Host "Gate C5A workflow completed:"
Write-Host (Join-Path $OutputDir "17_GATE_C5A_ADVISOR_DECISION.md")
