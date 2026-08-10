# Creates the recommended conda/mamba environment for the single-cell workflow.
# Requires conda, mamba, or micromamba to be installed and available on PATH.
#
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_create_conda_env.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$EnvFile = Join-Path $ProjectRoot "02_analysis\environment.yml"

function Find-CondaCommand {
    $commands = @("mamba", "micromamba", "conda")
    foreach ($cmd in $commands) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) {
            return @{ Kind = $cmd; Path = $found.Source }
        }
    }

    $candidates = @(
        "C:\ProgramData\miniforge3\condabin\conda.bat",
        "C:\ProgramData\miniforge3\Scripts\conda.exe",
        "$env:USERPROFILE\miniforge3\condabin\conda.bat",
        "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat",
        "$env:LOCALAPPDATA\Programs\Miniforge3\condabin\conda.bat",
        "$env:LOCALAPPDATA\Programs\miniforge3\condabin\conda.bat"
    )
    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            return @{ Kind = "conda"; Path = $path }
        }
    }

    return $null
}

$Conda = Find-CondaCommand
if (-not $Conda) {
    throw "No conda, mamba, or micromamba found. Miniforge may be installed but not in a known location."
}

Write-Host "Using $($Conda.Kind): $($Conda.Path)"

if ($Conda.Kind -eq "mamba") {
    & $Conda.Path env create -f $EnvFile
} elseif ($Conda.Kind -eq "micromamba") {
    & $Conda.Path create -f $EnvFile -y
} else {
    $existing = & $Conda.Path env list
    if ($existing -match "sle-bcell") {
        Write-Host "Environment sle-bcell already exists. Updating it..."
        & $Conda.Path env update -n sle-bcell -f $EnvFile --prune
    } else {
        & $Conda.Path env create -f $EnvFile
    }
}

Write-Host ""
Write-Host "Environment ready."
Write-Host ""
Write-Host "If conda is available in your PowerShell, activate it with:"
Write-Host "  conda activate sle-bcell"
Write-Host ""
Write-Host "PATH-independent verification command:"
Write-Host "  & `"$($Conda.Path)`" run -n sle-bcell python `"$ProjectRoot\02_analysis\scripts\01_check_scanpy_env.py`""
