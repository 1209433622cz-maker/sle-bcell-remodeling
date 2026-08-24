param(
    [string]$EnvironmentFile = "",
    [string]$ExplicitSpec = ""
)

$ErrorActionPreference = "Stop"
$EnvironmentName = "sle-bcell-submission"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $EnvironmentFile) {
    $EnvironmentFile = Join-Path $PSScriptRoot "environment_submission.yml"
}
$EnvironmentFile = (Resolve-Path -LiteralPath $EnvironmentFile).Path

if (-not $ExplicitSpec) {
    $ExplicitSpec = Join-Path $PSScriptRoot "environment_submission_win64.txt"
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

$payload = (& $conda env list --json | ConvertFrom-Json)
$environmentExists = @(
    $payload.envs | Where-Object { (Split-Path -Leaf $_) -eq $EnvironmentName }
).Count -gt 0

if ($environmentExists) {
    Write-Host "Updating pinned environment $EnvironmentName..."
    & $conda env update --name $EnvironmentName --file $EnvironmentFile --prune
}
else {
    Write-Host "Creating pinned environment $EnvironmentName..."
    & $conda env create --file $EnvironmentFile
}
if ($LASTEXITCODE -ne 0) { throw "Conda environment creation or update failed." }

Write-Host "Exporting exact win-64 package specification..."
$explicitLines = & $conda list --name $EnvironmentName --explicit
if ($LASTEXITCODE -ne 0 -or -not ($explicitLines -contains "@EXPLICIT")) {
    throw "Unable to export the explicit conda package specification."
}
Set-Content -LiteralPath $ExplicitSpec -Value $explicitLines -Encoding utf8

$SmokeDir = Join-Path $Root "04_submission\.submission_environment_check"
& $conda run --name $EnvironmentName python `
    (Join-Path $PSScriptRoot "check_submission_environment.py") `
    --output-dir $SmokeDir
if ($LASTEXITCODE -ne 0) { throw "Submission environment qualification failed." }

Write-Host "Submission environment is ready: $EnvironmentName"
Write-Host "Explicit package specification: $ExplicitSpec"
