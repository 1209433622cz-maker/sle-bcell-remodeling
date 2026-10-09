param(
    [string]$Workspace = "H:\cuhk-2025fALL\6013RP-wyf",
    [string]$OutputDir = "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\rp_v3_redesign\20261009_stage0b"
)

$ErrorActionPreference = "Stop"

$Python = "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    throw "The sle-bcell Python executable was not found: $Python"
}

$Workspace = (Resolve-Path -LiteralPath $Workspace).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$OutputDir = (Resolve-Path -LiteralPath $OutputDir).Path
$ExternalDir = Join-Path $OutputDir "external_source_rebuild"
$A2Dir = Join-Path $OutputDir "a2_rebuild"

Write-Host "[1/4] Freezing RP v3 Stage 0B contracts and materializing A2 input..."
& $Python (Join-Path $Workspace "audit_tools\rp_v3_stage0b_01_freeze_protocol.py") `
    --workspace $Workspace `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) { throw "Stage 0B protocol freeze failed." }

Write-Host "[2/4] Fitting the full-cell disease-blind A2 representation..."
$PreparedA2 = Join-Path $A2Dir "03_a2_prepared.h5ad"
$FittedA2 = Join-Path $A2Dir "08_isg_excluded_representation.h5ad"
if ((Test-Path -LiteralPath $FittedA2) -and ((Get-Item -LiteralPath $PreparedA2).LastWriteTimeUtc -gt (Get-Item -LiteralPath $FittedA2).LastWriteTimeUtc)) {
    Remove-Item -LiteralPath $FittedA2 -Force
    Remove-Item -LiteralPath (Join-Path $A2Dir "16_GATE_C2B2_PARTIAL.json") -Force -ErrorAction SilentlyContinue
    Write-Host "Removed stale A2 fit because the prepared source changed."
}
& $Python (Join-Path $Workspace "audit_tools\phase17_c2b_08_fit_representation.py") `
    --prepared-h5ad $PreparedA2 `
    --output-dir $A2Dir `
    --branches "isg_excluded" `
    --resolutions "0.4" `
    --n-neighbors 15 `
    --n-pcs 30 `
    --harmony-max-iter 20
if ($LASTEXITCODE -ne 0) { throw "A2 representation fit failed." }

$ExternalCounts = Join-Path $ExternalDir "07_EXTERNAL_PSEUDOBULK_COUNTS.npz"
$ExternalGenes = Join-Path $ExternalDir "09_EXTERNAL_GENE_UNIVERSE.csv.gz"
if ((Test-Path -LiteralPath $ExternalCounts) -and (Test-Path -LiteralPath $ExternalGenes)) {
    Write-Host "[3/4] Reusing validated Stage 0B external source rebuild..."
} else {
    Write-Host "[3/4] Rebuilding external source-label pseudobulk from raw matrices..."
    New-Item -ItemType Directory -Force -Path $ExternalDir | Out-Null
    & $Python (Join-Path $Workspace "audit_tools\phase17_c5a_01_source_mapping_freeze.py") `
        --source-dir (Join-Path $Workspace "Data\processed\GSE135779_nehar_validation\source") `
        --gate-c4a-dir (Join-Path $Workspace "phase17_v7\gateC4A\20260815_raw_pseudobulk_freeze") `
        --output-dir $ExternalDir
    if ($LASTEXITCODE -ne 0) {
        if ((Test-Path -LiteralPath $ExternalCounts) -and (Test-Path -LiteralPath $ExternalGenes)) {
            Write-Warning "The legacy C5A script exited after writing the required count objects; Stage 0B will validate and use those objects with the frozen canonical design."
        } else {
            throw "External source pseudobulk rebuild failed before required count objects were written."
        }
    }
}

Write-Host "[4/4] Running result-blind identifiability, scoring and simulation trials..."
& $Python (Join-Path $Workspace "audit_tools\rp_v3_stage0b_02_minimal_trial.py") `
    --workspace $Workspace `
    --output-dir $OutputDir `
    --external-rebuild-dir $ExternalDir
if ($LASTEXITCODE -ne 0) { throw "Stage 0B minimal trial returned HOLD or failed." }

Write-Host "RP v3 Stage 0B completed:"
Write-Host (Join-Path $OutputDir "14_STAGE0B_ADVISOR_REVIEW.md")
