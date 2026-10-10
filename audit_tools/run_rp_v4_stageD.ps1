param(
    [string]$Python = "D:\bioinfor\python.exe",
    [Parameter(Mandatory = $true)][string]$OutputRoot,
    [switch]$Resume
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$stageC = Join-Path $repo "phase17_v7\rp_v4_redesign\20261010_stageC_single_g2c_external_input_protocol_freeze"
$calibration = Join-Path $repo "phase17_v7\rp_v3_redesign\20261010_g2_implementation_freeze\02_G2_CALIBRATION_MODEL.json"
$registry = Join-Path $stageC "05_G2C_FINAL_DGP_REGISTRY.csv"
$sourceMetadata = Join-Path $stageC "source_metadata"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}
if (-not (Test-Path -LiteralPath $registry -PathType Leaf)) {
    throw "Stage C registry not found: $registry"
}
if (-not (Test-Path -LiteralPath $calibration -PathType Leaf)) {
    throw "Calibration model not found: $calibration"
}
if ((Test-Path -LiteralPath $OutputRoot) -and -not $Resume) {
    throw "Output root exists; use a new path or -Resume: $OutputRoot"
}

$env:PYTHONPATH = $PSScriptRoot
& $Python -m unittest -v audit_tools.test_rp_v4_g2c audit_tools.test_rp_v4_stageD
if ($LASTEXITCODE -ne 0) {
    throw "RP v4 Stage D tests failed"
}

if (-not (Test-Path -LiteralPath $OutputRoot)) {
    New-Item -ItemType Directory -Path $OutputRoot | Out-Null
}

$pilot = Join-Path $OutputRoot "pilot"
$pilotArgs = @(
    (Join-Path $PSScriptRoot "rp_v4_stageD_pilot.py"),
    "--registry", $registry,
    "--calibration-model", $calibration,
    "--output", $pilot,
    "--limit", "8"
)
if ($Resume) {
    $pilotArgs += "--resume"
}
& $Python @pilotArgs
if ($LASTEXITCODE -ne 0) {
    throw "RP v4 Stage D synthetic pilot failed"
}

$sraPlan = Join-Path $OutputRoot "sra_plan"
if (-not $Resume) {
    & $Python (Join-Path $PSScriptRoot "rp_v4_stageD_sra_plan.py") `
        --input-dir $sourceMetadata `
        --output-dir $sraPlan
    if ($LASTEXITCODE -ne 0) {
        throw "RP v4 Stage D SRA plan failed"
    }
}

Write-Output "STAGE_D_TECHNICAL_ONLY_COMPLETE"
Write-Output "No final G2C, real WP2 effect, external outcome, or SRA download was run."
