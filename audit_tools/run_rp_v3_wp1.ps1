param(
    [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf",
    [string]$PrefitDir = "phase17_v7\rp_v3_redesign\20261010_wp1_prefit_freeze",
    [string]$ContractDir = "phase17_v7\rp_v3_redesign\20261010_wp1_prefit_contract",
    [string]$RunDir = "phase17_v7\rp_v3_redesign\20261010_wp1_annotation_sensitivity",
    [string]$Python = "D:\bioinfor\python.exe"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $ProjectRoot

Write-Host "[1/3] Finalizing the outcome-free WP1 prefit contract..."
& $Python ".\audit_tools\rp_v3_wp1_01_finalize_prefit.py" `
    --prefit $PrefitDir `
    --output $ContractDir
if ($LASTEXITCODE -ne 0) { throw "WP1 prefit finalization failed" }

Write-Host "[2/3] Running WP1 unit tests..."
& $Python -m unittest ".\audit_tools\test_rp_v3_wp1.py" -v
if ($LASTEXITCODE -ne 0) { throw "WP1 unit tests failed" }

Write-Host "[3/3] Fitting the frozen WP1 estimands and paired bootstrap..."
& $Python ".\audit_tools\rp_v3_wp1_02_fit_annotation_sensitivity.py" `
    --prefit $PrefitDir `
    --contract-dir $ContractDir `
    --output $RunDir
if ($LASTEXITCODE -ne 0) { throw "WP1 fitting failed" }

Write-Host "WP1 workflow complete: $RunDir"
