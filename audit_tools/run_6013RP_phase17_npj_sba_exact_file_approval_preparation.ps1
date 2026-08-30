param(
    [string]$PythonExe = "D:\bioinfor\python.exe",
    [string]$ManagementDir = "",
    [string]$RunDir = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $ManagementDir) {
    $ManagementDir = Join-Path $RepoRoot "00_project_management\npj_sba_exact_file_approval_2026-08-30"
}
if (-not $RunDir) {
    $RunDir = Join-Path $RepoRoot "phase17_v7\npj_sba_submission_gate\20260830_exact_file_approval_preparation"
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}
if (-not (Test-Path -LiteralPath $ManagementDir)) {
    throw "Management directory not found: $ManagementDir"
}

Write-Host "[1/2] Verifying exact package, official forms and pending approval boundaries..."
& $PythonExe `
    (Join-Path $PSScriptRoot "phase17_npj_sba_07_exact_file_approval_preparation.py") `
    --management-dir $ManagementDir `
    --run-dir $RunDir
if ($LASTEXITCODE -ne 0) {
    throw "Exact-file approval preparation gate failed."
}

Write-Host "[2/2] Running focused regression tests..."
$env:NPJ_SBA_APPROVAL_RUN_DIR = $RunDir
& $PythonExe -m unittest `
    (Join-Path $PSScriptRoot "test_npj_sba_exact_file_approval_preparation.py")
if ($LASTEXITCODE -ne 0) {
    throw "Exact-file approval preparation tests failed."
}

Write-Host "Exact-file approval preparation completed:"
Write-Host (Join-Path $RunDir "00_EXACT_FILE_APPROVAL_PREPARATION.json")
