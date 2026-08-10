# Installs Miniforge3 with winget.
# Run from any directory:
#   powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_install_miniforge_with_winget.ps1"
#
# After installation, close and reopen PowerShell, then run:
#   conda --version
#   powershell -ExecutionPolicy Bypass -File "H:\cuhk-2025fALL\6013RP-wyf\02_analysis\scripts\00_create_conda_env.ps1"

$ErrorActionPreference = "Stop"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget was not found. Install Miniforge manually from the conda-forge Miniforge releases page."
}

Write-Host "Installing Miniforge3 via winget..."
winget install --id CondaForge.Miniforge3 --source winget --accept-package-agreements --accept-source-agreements

Write-Host ""
Write-Host "Miniforge installation command finished."
Write-Host "Close and reopen PowerShell, then check:"
Write-Host "  conda --version"
