param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$ResultDir = ".\phase17_v7\rp_v4_redesign\20261011_stageI_single_real_delta_profile",
    [string]$Authorization = ".\phase17_v7\rp_v4_redesign\20261011_stageI_single_real_delta_profile\00_STAGE_I_AUTHOR_GO.json"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $Repo
$env:PYTHONPATH = "$Repo;$Repo\audit_tools"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}

Write-Output "[1/2] Running Stage I postrun output-audit tests..."
& $Python -m unittest -v audit_tools.test_rp_v4_stageI_postrun_freeze
if ($LASTEXITCODE -ne 0) {
    throw "Stage I postrun tests failed"
}

Write-Output "[2/2] Freezing the existing two-file write-once result without refitting..."
& $Python .\audit_tools\rp_v4_stageI_postrun_freeze.py --result-dir $ResultDir --authorization $Authorization
if ($LASTEXITCODE -ne 0) {
    throw "Stage I postrun freeze failed"
}

Write-Output "Stage I output audit and freeze completed without reconstructing or refitting the response."
