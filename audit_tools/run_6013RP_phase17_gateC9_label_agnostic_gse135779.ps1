#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$SourceDir = "",
    [string]$ReferenceRaw = "",
    [string]$ReferenceRepresentation = "",
    [string]$ProgramDictionary = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell",
    [switch]$TestMode,
    [int]$MaxSamples = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

$Defaults = @{
    SourceDir = "Data\processed\GSE135779_nehar_validation\source"
    ReferenceRaw = "phase17_v7\gateC2B1\20260810_171000_full_library_doublets\04_full_raw_counts.h5ad"
    ReferenceRepresentation = "phase17_v7\gateC2B2\20260812_full_representation\06_primary_all_cells_representation.h5ad"
    ProgramDictionary = "phase17_v7\gateC5A\20260815_gse135779_source_mapping_freeze\10_FROZEN_PROGRAM_DICTIONARY.csv"
    OutputDir = "phase17_v7\gateC9\20260828_gse135779_label_agnostic_validation"
}

foreach ($Name in $Defaults.Keys) {
    $Value = Get-Variable -Name $Name -ValueOnly
    if ([string]::IsNullOrWhiteSpace($Value)) {
        $Value = Join-Path $ProjectRoot $Defaults[$Name]
    } elseif (-not [System.IO.Path]::IsPathRooted($Value)) {
        $Value = Join-Path $ProjectRoot $Value
    }
    Set-Variable -Name $Name -Value ([System.IO.Path]::GetFullPath($Value))
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$CondaCandidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "$env:USERPROFILE\miniforge3\condabin\conda.bat"
)
$PathConda = Get-Command conda -ErrorAction SilentlyContinue
if ($null -ne $PathConda) { $CondaCandidates += $PathConda.Source }
$CondaExe = $CondaCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    throw "Conda was not found. Prepare the existing sle-bcell environment first."
}

$PrefreezeArguments = @(
    "run", "--no-capture-output", "-n", $CondaEnvironment, "python",
    (Join-Path $PSScriptRoot "phase17_c9_01_prefreeze_label_agnostic_mapping.py"),
    "--project-root", $ProjectRoot,
    "--source-dir", $SourceDir,
    "--reference-raw", $ReferenceRaw,
    "--reference-representation", $ReferenceRepresentation,
    "--program-dictionary", $ProgramDictionary,
    "--output-dir", $OutputDir
)
if ($TestMode) { $PrefreezeArguments += "--test-mode" }
if ($MaxSamples -gt 0) { $PrefreezeArguments += @("--max-samples", "$MaxSamples") }

Write-Host "[1/2] Freezing label-agnostic selection, mapping and program scores..."
& $CondaExe @PrefreezeArguments
if ($LASTEXITCODE -ne 0) {
    throw "Gate C9A prefreeze failed or did not authorize outcome access."
}

if ($TestMode) {
    Write-Host "Gate C9A test mode completed; protected outcomes were not opened:"
    Write-Host (Join-Path $OutputDir "16_GATE_C9A_PREFREEZE_REVIEW.md")
    exit 0
}

Write-Host "[2/2] Verifying the freeze, unlocking protected metadata and reviewing outcomes..."
& $CondaExe run --no-capture-output -n $CondaEnvironment python `
    (Join-Path $PSScriptRoot "phase17_c9_02_unlock_outcomes_and_review.py") `
    --project-root $ProjectRoot `
    --prefreeze-dir $OutputDir `
    --metadata (Join-Path $SourceDir "Meta_caSLE_processed_08092021_small.csv") `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Gate C9B outcome review failed to complete."
}

Write-Host "Gate C9 workflow completed:"
Write-Host (Join-Path $OutputDir "28_GATE_C9_ADVISOR_REVIEW.md")
