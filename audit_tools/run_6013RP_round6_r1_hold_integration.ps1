param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$R1RunDir = "",
    [string]$OutputDir = "",
    [string]$AnalysisPython = "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe",
    [string]$CompositionPython = "D:\bioinfor\python.exe",
    [string]$Rscript = "C:\Program Files\R\R-4.6.0\bin\Rscript.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if ([string]::IsNullOrWhiteSpace($R1RunDir)) {
    $R1RunDir = Join-Path $ProjectRoot "phase17_v7\round6_q1_robustness\20260825_full_pipeline_identity_resampling"
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\round6_q1_robustness\20260827_r1_hold_integration"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$RawH5ad = Join-Path $ProjectRoot "phase17_v7\gateC2B1\20260810_171000_full_library_doublets\04_full_raw_counts.h5ad"
$ReferenceH5ad = Join-Path $ProjectRoot "phase17_v7\gateC2B2\20260812_full_representation\06_primary_all_cells_representation.h5ad"
$GateC3 = Join-Path $ProjectRoot "phase17_v7\gateC3\20260815_metadata_design"
$GateC3A = Join-Path $ProjectRoot "phase17_v7\gateC3A\20260815_frozen_abundance"
$GateC4A = Join-Path $ProjectRoot "phase17_v7\gateC4A\20260815_raw_pseudobulk_freeze"
$GateC4B = Join-Path $ProjectRoot "phase17_v7\gateC4B\20260815_edger_transcription"
$AuditScript = Join-Path $PSScriptRoot "phase17_round6_04_audit_r1_hold_and_prepare_propagation.py"
$CompositionScript = Join-Path $PSScriptRoot "phase17_round6_05_fit_identity_uncertainty_composition.py"
$RModelScript = Join-Path $PSScriptRoot "phase17_round6_05_fit_identity_uncertainty_ifn.R"

foreach ($Required in @($AnalysisPython, $CompositionPython, $Rscript, $R1RunDir, $RawH5ad, $ReferenceH5ad, $GateC3, $GateC3A, $GateC4A, $GateC4B, $AuditScript, $CompositionScript, $RModelScript)) {
    if (-not (Test-Path -LiteralPath $Required)) {
        throw "Required input was not found: $Required"
    }
}

Write-Host "[1/3] Independently auditing R1 and preparing frozen-design propagation..."
& $AnalysisPython -u $AuditScript `
    --r1-run-dir $R1RunDir `
    --raw-h5ad $RawH5ad `
    --reference-h5ad $ReferenceH5ad `
    --gate-c3-dir $GateC3 `
    --gate-c3a-dir $GateC3A `
    --gate-c4b-dir $GateC4B `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "R1 independent audit/preparation failed with exit code $LASTEXITCODE"
}

Write-Host "[2/3] Refitting frozen B_ASC composition under each boundary exchange..."
& $CompositionPython -u $CompositionScript `
    --r1-run-dir $R1RunDir `
    --gate-c3-dir $GateC3 `
    --gate-c3a-dir $GateC3A `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    throw "R1 composition uncertainty propagation failed with exit code $LASTEXITCODE"
}

Write-Host "[3/3] Refitting frozen IFN/ISG effects under each boundary exchange..."
& $Rscript $RModelScript $OutputDir $GateC4B $GateC4A
if ($LASTEXITCODE -ne 0) {
    throw "R1 IFN uncertainty propagation failed with exit code $LASTEXITCODE"
}

Write-Host "Round 6 R1 HOLD integration completed:"
Write-Host $OutputDir
