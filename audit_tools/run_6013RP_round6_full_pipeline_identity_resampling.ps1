param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputDir = "",
    [int]$Replicates = 20,
    [double]$ResampleFraction = 0.8,
    [int]$MaxCells = 0,
    [int]$HarmonyMaxIter = 50,
    [string]$PythonPath = "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\round6_q1_robustness\20260825_full_pipeline_identity_resampling"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if (-not (Test-Path -LiteralPath $PythonPath)) {
    throw "Scanpy Python was not found: $PythonPath"
}

$InputH5ad = Join-Path $ProjectRoot "phase17_v7\gateC2B1\20260810_171000_full_library_doublets\04_full_raw_counts.h5ad"
$ReferenceH5ad = Join-Path $ProjectRoot "phase17_v7\gateC2B2\20260812_full_representation\06_primary_all_cells_representation.h5ad"
$Script = Join-Path $PSScriptRoot "phase17_round6_03_full_pipeline_identity_resampling.py"
foreach ($Required in @($InputH5ad, $ReferenceH5ad, $Script)) {
    if (-not (Test-Path -LiteralPath $Required)) {
        throw "Required input was not found: $Required"
    }
}

Write-Host "Running resumable full-pipeline disease-blind identity resampling..."
Write-Host "  Replicates: $Replicates"
Write-Host "  Fraction: $ResampleFraction"
Write-Host "  MaxCells: $MaxCells (0 means full scientific run)"
Write-Host "  HarmonyMaxIter: $HarmonyMaxIter"
Write-Host "  Output: $OutputDir"

& $PythonPath $Script `
    --input-h5ad $InputH5ad `
    --reference-h5ad $ReferenceH5ad `
    --output-dir $OutputDir `
    --replicates $Replicates `
    --fraction $ResampleFraction `
    --max-cells $MaxCells `
    --harmony-max-iter $HarmonyMaxIter
if ($LASTEXITCODE -ne 0) {
    throw "Full-pipeline identity resampling failed with exit code $LASTEXITCODE"
}

Write-Host "Round 6 full-pipeline resampling outputs:"
Write-Host $OutputDir
