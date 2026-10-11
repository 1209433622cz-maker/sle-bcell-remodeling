param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$StageLRoot = ".\phase17_v7\rp_v4_redesign\20261011_stageL_external_cohort_gate",
    [string]$RunInfo = ".\phase17_v7\rp_v4_redesign\20261010_stageC_single_g2c_external_input_protocol_freeze\source_metadata\PRJNA1093470_RunInfo.csv",
    [string]$Output = ".\phase17_v7\rp_v4_redesign\20261011_stageM_raw_pipeline_freeze"
)

$ErrorActionPreference = "Stop"
if (Test-Path -LiteralPath $Output) {
    throw "Stage M output already exists: $Output"
}

& $Python ".\audit_tools\rp_v4_stageM_01_raw_pipeline_freeze.py" `
    --stage-l-root $StageLRoot `
    --runinfo $RunInfo `
    --output $Output

if ($LASTEXITCODE -ne 0) {
    throw "Stage M generator failed with exit code $LASTEXITCODE"
}

Write-Host "Stage M disease-blind pipeline freeze completed: $Output"
