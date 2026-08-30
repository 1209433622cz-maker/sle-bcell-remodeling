param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$RunDir = ".\phase17_v7\npj_sba_post_hardening_reaudit\20260830_qiteng_text_freeze",
    [string]$ManagementDir = ".\00_project_management\npj_sba_post_hardening_reaudit_2026-08-30",
    [switch]$RecordVisualPass
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root $RunDir))
$Management = [System.IO.Path]::GetFullPath((Join-Path $Root $ManagementDir))

if (-not $Run.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RunDir must resolve within phase17_v7: $Run"
}
if (-not $Management.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "00_project_management")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "ManagementDir must resolve within 00_project_management: $Management"
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python runtime not found: $Python"
}

$PreviousRun = $env:NPJ_SBA_POST_HARDENING_RUN_DIR
$PreviousManagement = $env:NPJ_SBA_POST_HARDENING_MANAGEMENT_DIR
$env:NPJ_SBA_POST_HARDENING_RUN_DIR = $Run
$env:NPJ_SBA_POST_HARDENING_MANAGEMENT_DIR = $Management

Push-Location $Root
try {
    $Arguments = @(
        ".\audit_tools\phase17_npj_sba_06_post_hardening_reaudit.py"
    )
    if ($RecordVisualPass) {
        $Arguments += "--record-visual-pass"
    }
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Post-hardening reaudit failed" }
    if ($RecordVisualPass) {
        & $Python ".\audit_tools\test_npj_sba_post_hardening_reaudit.py"
        if ($LASTEXITCODE -ne 0) { throw "Post-hardening regression tests failed" }
    }
} finally {
    Pop-Location
    $env:NPJ_SBA_POST_HARDENING_RUN_DIR = $PreviousRun
    $env:NPJ_SBA_POST_HARDENING_MANAGEMENT_DIR = $PreviousManagement
}
