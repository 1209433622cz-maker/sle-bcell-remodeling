param(
    [string]$EnvironmentFile = "",
    [string]$ExplicitSpec = ""
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $EnvironmentFile) {
    $EnvironmentFile = Join-Path $PSScriptRoot "environment_gateC8BR_release_2026-08-25.yml"
}
$EnvironmentFile = (Resolve-Path -LiteralPath $EnvironmentFile).Path
if (-not $ExplicitSpec) {
    $ExplicitSpec = Join-Path $PSScriptRoot "environment_gateC8BR_release_explicit_win64_2026-08-25.txt"
}
$ExplicitSpec = [System.IO.Path]::GetFullPath($ExplicitSpec)

$command = Get-Command conda -ErrorAction SilentlyContinue | Select-Object -First 1
$candidates = @(
    $(if ($command) { $command.Source }),
    (Join-Path $env:ProgramData "miniforge3\condabin\conda.bat"),
    (Join-Path $env:USERPROFILE "miniforge3\condabin\conda.bat"),
    (Join-Path $env:USERPROFILE "mambaforge\condabin\conda.bat"),
    (Join-Path $env:USERPROFILE "anaconda3\condabin\conda.bat")
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
$conda = $candidates | Select-Object -First 1
if (-not $conda) {
    throw "Conda was not found. Install Miniforge or add conda to PATH, then rerun."
}

$environmentExists = $false
try {
    $payload = (& $conda env list --json | ConvertFrom-Json)
    $environmentExists = @($payload.envs | Where-Object { (Split-Path -Leaf $_) -eq "sle-bcell-c8br-release" }).Count -gt 0
}
catch { throw "Unable to query conda environments with $conda" }

if ($environmentExists) {
    Write-Host "Updating pinned environment sle-bcell-c8br-release..."
    & $conda env update --name sle-bcell-c8br-release --file $EnvironmentFile --prune
}
else {
    Write-Host "Creating pinned environment sle-bcell-c8br-release..."
    & $conda env create --file $EnvironmentFile
}
if ($LASTEXITCODE -ne 0) { throw "Conda environment creation/update failed." }

Write-Host "Exporting exact win-64 package specification..."
$explicitLines = & $conda list --name sle-bcell-c8br-release --explicit
if ($LASTEXITCODE -ne 0 -or -not ($explicitLines -contains "@EXPLICIT")) {
    throw "Unable to export the explicit conda package specification."
}
Set-Content -LiteralPath $ExplicitSpec -Value $explicitLines -Encoding utf8

Write-Host "Qualifying the release environment..."
& $conda run --name sle-bcell-c8br-release python (Join-Path $PSScriptRoot "phase17_c8br_00_release_smoke_test.py") --output-dir (Join-Path $Root "phase17_v7\gateC8BR\20260825_release_portability_preflight\_runtime_smoke")
if ($LASTEXITCODE -ne 0) { throw "Gate C8BR release-environment smoke test failed." }
Write-Host "Explicit package specification: $ExplicitSpec"
Write-Host "Gate C8BR release environment is ready."
