param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$OutputDir = ".\phase17_v7\rp_v3_redesign\20261010_wp3_pooled_measurement"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputDir))
$IndependentPath = Join-Path $OutputPath "independent_recompute"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python executable not found: $Python"
}
if (Test-Path -LiteralPath $OutputPath) {
    throw "Output directory already exists: $OutputPath"
}

Push-Location $RepoRoot
try {
    Write-Host "[1/3] Running WP3 pooled-measurement boundary tests..."
    & $Python -m unittest -v audit_tools.test_rp_v3_wp3_pooled_measurement
    if ($LASTEXITCODE -ne 0) {
        throw "WP3 pooled-measurement tests failed."
    }

    Write-Host "[2/3] Running pooled diagnostics without phenotype fields..."
    & $Python .\audit_tools\rp_v3_wp3_02_pooled_measurement.py `
        --workspace $RepoRoot `
        --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "WP3 pooled-measurement execution failed."
    }

    Write-Host "[3/3] Independently recomputing all reported numbers..."
    & $Python .\audit_tools\rp_v3_wp3_03_independent_recompute.py `
        --workspace $RepoRoot `
        --results $OutputPath `
        --output $IndependentPath
    if ($LASTEXITCODE -ne 0) {
        throw "WP3 independent recomputation failed."
    }
}
finally {
    Pop-Location
}

Write-Host "WP3 pooled measurement completed:"
Write-Host $OutputPath
