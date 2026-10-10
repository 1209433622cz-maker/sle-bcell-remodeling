param(
    [string]$Python = "D:\bioinfor\python.exe",
    [Parameter(Mandatory = $true)][string]$OutputRoot,
    [Parameter(Mandatory = $true)][string]$CanonicalOutput,
    [string]$ExternalZip = "C:\Users\Administrator\Downloads\SLE_RPv4_StageE_Preflight_20261011.zip",
    [string]$ExternalRoot = ""
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$stageC = Join-Path $repo "phase17_v7\rp_v4_redesign\20261010_stageC_single_g2c_external_input_protocol_freeze"
$registry = Join-Path $stageC "05_G2C_FINAL_DGP_REGISTRY.csv"
$calibration = Join-Path $repo "phase17_v7\rp_v3_redesign\20261010_g2_implementation_freeze\02_G2_CALIBRATION_MODEL.json"

if ([string]::IsNullOrWhiteSpace($ExternalRoot)) {
    $ExternalRoot = Join-Path $repo "phase17_v7\rp_v4_redesign\20261011_stageE_external_candidate\SLE_RPv4_StageE_Preflight_20261011"
}
foreach ($path in @($Python, $registry, $calibration, $ExternalZip, $ExternalRoot)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required Stage E2 input not found: $path"
    }
}
if (Test-Path -LiteralPath $OutputRoot) {
    throw "Stage E2 work root exists; use a new path: $OutputRoot"
}
if (Test-Path -LiteralPath $CanonicalOutput) {
    throw "Canonical Stage E2 output exists; refusing overwrite: $CanonicalOutput"
}

New-Item -ItemType Directory -Path $OutputRoot | Out-Null
$prepared = Join-Path $OutputRoot "prepared"
$outerResume = Join-Path $OutputRoot "outer_resume"
$outerFresh = Join-Path $OutputRoot "outer_fresh"
$truthOutput = Join-Path $OutputRoot "truth_qualification"
$preflightReceipt = Join-Path $OutputRoot "windows_preflight.json"
$env:PYTHONPATH = $repo

& $Python -m unittest -v audit_tools.test_rp_v4_stageE2
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 unit tests failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_freeze.py") prepare `
    --output $prepared
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 preparation failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_runner.py") `
    --registry $registry `
    --calibration-model $calibration `
    --output $outerResume `
    --mode qualification `
    --qualification-attempts 8 `
    --scenarios C0_X1 C1_X2 C2_X3
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 outer qualification failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_runner.py") `
    --registry $registry `
    --calibration-model $calibration `
    --output $outerResume `
    --mode qualification `
    --qualification-attempts 8 `
    --scenarios C0_X1 C1_X2 C2_X3 `
    --resume
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 outer resume qualification failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_runner.py") `
    --registry $registry `
    --calibration-model $calibration `
    --output $outerFresh `
    --mode qualification `
    --qualification-attempts 8 `
    --scenarios C0_X1 C1_X2 C2_X3
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 independent outer replay failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_truth.py") `
    --registry $registry `
    --calibration-model $calibration `
    --output $truthOutput `
    --mode qualification `
    --scenarios C0_X1 C1_X2 C2_X3
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 truth qualification failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_preflight.py") `
    --registry $registry `
    --calibration-model $calibration `
    --author-signoff (Join-Path $prepared "02_AUTHOR_CONTRACT_SIGNOFF.json") `
    --go-template (Join-Path $prepared "08_FULL_G2C_GO_TEMPLATE.json") `
    --binding-manifest (Join-Path $prepared "04_STAGE_E2_SOURCE_BINDING.csv") `
    --outer-receipt (Join-Path $outerResume "02_RUN_RECEIPT.json") `
    --truth-receipt (Join-Path $truthOutput "02_TRUTH_RECEIPT.json") `
    --output $preflightReceipt
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 Windows preflight failed"
}

& $Python (Join-Path $PSScriptRoot "rp_v4_stageE2_freeze.py") finalize `
    --prepared $prepared `
    --external-zip $ExternalZip `
    --external-root $ExternalRoot `
    --outer-resume $outerResume `
    --outer-fresh $outerFresh `
    --truth-output $truthOutput `
    --preflight-receipt $preflightReceipt `
    --output $CanonicalOutput
if ($LASTEXITCODE -ne 0) {
    throw "Stage E2 canonical freeze failed"
}

Write-Output "PASS_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING"
Write-Output "HOLD_EXACT_CODE_GO: stage141/stage142 were not started."
