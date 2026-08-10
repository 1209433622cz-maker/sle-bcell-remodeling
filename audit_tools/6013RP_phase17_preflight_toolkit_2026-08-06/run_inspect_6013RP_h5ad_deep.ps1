#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ScriptPath = Join-Path $PSScriptRoot "inspect_6013RP_h5ad_deep.py"
$EnvFile = Join-Path $ProjectRoot "02_analysis\environment.yml"

if (-not (Test-Path $ScriptPath)) { throw "Missing script: $ScriptPath" }
if (-not (Test-Path $ProjectRoot -PathType Container)) { throw "Missing project root: $ProjectRoot" }

$EnvName = $null
if (Test-Path $EnvFile) {
    $NameLine = Get-Content $EnvFile -Encoding UTF8 |
        Where-Object { $_ -match '^\s*name\s*:\s*(.+?)\s*$' } |
        Select-Object -First 1
    if ($NameLine -and $NameLine -match '^\s*name\s*:\s*(.+?)\s*$') {
        $EnvName = $Matches[1].Trim()
    }
}

$CondaCandidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "C:\ProgramData\anaconda3\condabin\conda.bat",
    "$env:USERPROFILE\miniforge3\condabin\conda.bat",
    "$env:USERPROFILE\anaconda3\condabin\conda.bat",
    "$env:USERPROFILE\miniconda3\condabin\conda.bat"
)
$Conda = $CondaCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($Conda -and $EnvName) {
    Write-Host "Using conda environment: $EnvName" -ForegroundColor Cyan
    & $Conda run -n $EnvName python $ScriptPath --root $ProjectRoot
    if ($LASTEXITCODE -eq 0) { exit 0 }
    Write-Warning "Conda environment run failed; trying regular Python."
}

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) {
    & $Py.Source -3 $ScriptPath --root $ProjectRoot
    if ($LASTEXITCODE -eq 0) { exit 0 }
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & $Python.Source $ScriptPath --root $ProjectRoot
    if ($LASTEXITCODE -eq 0) { exit 0 }
}

throw @"
H5AD audit could not start because the selected Python lacks h5py/numpy.

Install into the Python you plan to use:
    py -3 -m pip install h5py numpy

Then rerun this PowerShell script.
"@
