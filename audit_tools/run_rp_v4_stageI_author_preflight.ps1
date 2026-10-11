param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$Output = ".\phase17_v7\rp_v4_redesign\_software_tests\20261011_stageI_author_decision_packet"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $Repo
$env:PYTHONPATH = "$Repo;$Repo\audit_tools"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}
if (Test-Path -LiteralPath $Output) {
    throw "Stage I author-preflight output already exists; overwrite is forbidden: $Output"
}

Write-Output "[1/2] Running Stage I author-preflight tests..."
& $Python -m unittest -v audit_tools.test_rp_v4_stageI_author_preflight
if ($LASTEXITCODE -ne 0) {
    throw "Stage I author-preflight tests failed"
}

Write-Output "[2/2] Building the unsigned, commit-bound author decision packet..."
& $Python .\audit_tools\rp_v4_stageI_author_preflight.py --output $Output
if ($LASTEXITCODE -ne 0) {
    throw "Stage I author preflight failed"
}

Write-Output "Stage I remains unauthorized. No real response was constructed or fitted."
Write-Output "Unsigned local decision packet: $Output"
