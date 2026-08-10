# Verifies the sle-bcell environment without requiring `conda activate`.
# Run from any directory:
#   powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\01_check_scanpy_env_conda.ps1"

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CheckScript = Join-Path $ProjectRoot "02_analysis\scripts\01_check_scanpy_env.py"

$candidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "C:\ProgramData\miniforge3\Scripts\conda.exe",
    "$env:USERPROFILE\miniforge3\condabin\conda.bat",
    "$env:LOCALAPPDATA\miniforge3\condabin\conda.bat",
    "$env:LOCALAPPDATA\Programs\Miniforge3\condabin\conda.bat",
    "$env:LOCALAPPDATA\Programs\miniforge3\condabin\conda.bat"
)

$CondaPath = $null
$cmd = Get-Command conda -ErrorAction SilentlyContinue
if ($cmd) {
    $CondaPath = $cmd.Source
} else {
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            $CondaPath = $candidate
            break
        }
    }
}

if (-not $CondaPath) {
    throw "Could not find conda. Expected C:\ProgramData\miniforge3\condabin\conda.bat or conda on PATH."
}

Write-Host "Using conda: $CondaPath"
& $CondaPath run -n sle-bcell python $CheckScript
