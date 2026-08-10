#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf",
    [double]$MaxResultMB = 30,
    [double]$MaxDataMB = 25
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ScriptPath = Join-Path $PSScriptRoot "build_6013RP_phase17_review_pack.py"

if (-not (Test-Path -LiteralPath $ScriptPath)) {
    throw "Missing script: $ScriptPath"
}
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "Project root does not exist: $ProjectRoot"
}

$Python = $null
$Prefix = @()
$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) {
    $Python = $Py.Source
    $Prefix = @("-3")
} else {
    $Cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($Cmd) { $Python = $Cmd.Source }
}
if (-not $Python) {
    throw "Python 3 not found in PATH."
}

& $Python @Prefix $ScriptPath `
    --root $ProjectRoot `
    --max-result-mb $MaxResultMB `
    --max-data-mb $MaxDataMB

if ($LASTEXITCODE -ne 0) {
    throw "Review-pack build failed with exit code $LASTEXITCODE"
}

$Latest = Join-Path $ProjectRoot "_phase17_review_pack\_LATEST_REVIEW_PACK.txt"
if (Test-Path $Latest) {
    Write-Host ""
    Get-Content $Latest
}
