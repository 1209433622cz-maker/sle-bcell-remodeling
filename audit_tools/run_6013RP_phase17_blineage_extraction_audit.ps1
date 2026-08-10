#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$PythonExe = "",
    [int]$ChunkSize = 10000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $PythonCandidates = @(
        "C:\ProgramData\miniforge3\envs\sle-bcell-v7\python.exe",
        "C:\ProgramData\miniforge3\envs\sle-bcell\python.exe"
    )
    $PathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $PathPython) { $PythonCandidates += $PathPython.Source }
    $PythonExe = $PythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

$InputH5ad = Join-Path $ProjectRoot "Data\processed\GSE174188_perez_cellxgene\perez_gse174188_cellxgene.h5ad"
$OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC2B2_prechecks\blineage_extraction_completeness"
if ([string]::IsNullOrWhiteSpace($PythonExe) -or -not (Test-Path -LiteralPath $PythonExe)) {
    throw "No usable Python environment found. Pass -PythonExe explicitly."
}
if (-not (Test-Path -LiteralPath $InputH5ad)) { throw "Full PBMC H5AD not found: $InputH5ad" }

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
& $PythonExe (Join-Path $ProjectRoot "audit_tools\phase17_c2b_04_blineage_extraction_audit.py") `
    --input-h5ad $InputH5ad `
    --output-dir $OutputDir `
    --chunk-size $ChunkSize
if ($LASTEXITCODE -ne 0) { throw "B-lineage extraction audit failed with exit code $LASTEXITCODE" }

Write-Host "B-lineage extraction audit completed; review required:" -ForegroundColor Green
Write-Host (Join-Path $OutputDir "06_BLINEAGE_EXTRACTION_AUDIT.md")
