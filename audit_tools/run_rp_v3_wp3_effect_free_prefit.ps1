param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$OutputDir = ".\phase17_v7\rp_v3_redesign\20261010_wp3_effect_free_prefit"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputDir))

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python executable not found: $Python"
}
if (Test-Path -LiteralPath $OutputPath) {
    throw "Output directory already exists: $OutputPath"
}

Push-Location $RepoRoot
try {
    Write-Host "[1/2] Running WP3 effect-free prefit tests..."
    & $Python -m unittest -v audit_tools.test_rp_v3_wp3_effect_free_prefit
    if ($LASTEXITCODE -ne 0) {
        throw "WP3 effect-free prefit tests failed."
    }

    Write-Host "[2/2] Auditing canonical external inputs without fitting outcomes..."
    & $Python .\audit_tools\rp_v3_wp3_01_effect_free_prefit.py `
        --workspace $RepoRoot `
        --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "WP3 effect-free prefit failed."
    }
}
finally {
    Pop-Location
}

Write-Host "WP3 effect-free prefit completed:"
Write-Host $OutputPath
