#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRootWindows = "H:\cuhk-2025fALL\6013RP-wyf",
    [string]$WslDistribution = "Ubuntu-22.04"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$BashScript = Join-Path $PSScriptRoot "run_6013RP_phase17_gateC2A_smoke.sh"
if (-not (Test-Path -LiteralPath $BashScript)) {
    throw "Missing bash runner: $BashScript"
}

$ToolDirWsl = (& wsl.exe -d $WslDistribution wslpath -a $PSScriptRoot).Trim()
$ProjectRootWsl = (& wsl.exe -d $WslDistribution wslpath -a $ProjectRootWindows).Trim()

if ([string]::IsNullOrWhiteSpace($ToolDirWsl)) {
    throw "Could not resolve toolkit directory in WSL."
}
if ([string]::IsNullOrWhiteSpace($ProjectRootWsl)) {
    throw "Could not resolve project root in WSL."
}

$Command = "cd '$ToolDirWsl' && bash ./run_6013RP_phase17_gateC2A_smoke.sh '$ProjectRootWsl'"
Write-Host "Running in WSL:" -ForegroundColor Cyan
Write-Host $Command

& wsl.exe -d $WslDistribution bash -lc $Command
if ($LASTEXITCODE -ne 0) {
    throw "Gate C2A WSL runner failed: $LASTEXITCODE"
}
