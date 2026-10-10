param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$Output = ".\phase17_v7\rp_v4_redesign\20261011_stageH_effect_blind_prefit"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $Repo
$env:PYTHONPATH = "$Repo;$Repo\audit_tools"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}
if (Test-Path -LiteralPath $Output) {
    throw "Stage H output already exists; overwrite is forbidden: $Output"
}

Write-Output "[1/2] Running Stage H effect-firewall tests..."
& $Python -m unittest -v audit_tools.test_rp_v4_stageH
if ($LASTEXITCODE -ne 0) {
    throw "Stage H tests failed"
}

Write-Output "[2/2] Running canonical effect-blind applicability preflight..."
& $Python .\audit_tools\rp_v4_stageH_effect_blind_prefit.py --output $Output
if ($LASTEXITCODE -ne 0) {
    throw "Stage H preflight failed"
}

Write-Output "Stage H completed without constructing or fitting the real disease response."
Write-Output "Canonical output: $Output"
Write-Output "Stage I remains HOLD until a new exact author sign-off is committed."
