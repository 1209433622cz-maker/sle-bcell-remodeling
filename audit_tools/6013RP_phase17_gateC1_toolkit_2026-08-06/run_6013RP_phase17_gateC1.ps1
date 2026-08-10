#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf",
    [string]$OutputRoot = "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir = Join-Path $OutputRoot $Stamp
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$Scripts = @{
    Freeze   = Join-Path $PSScriptRoot "phase17_00_freeze_and_verify_inputs.py"
    Metadata = Join-Path $PSScriptRoot "phase17_01_metadata_hierarchy_audit.py"
    QC       = Join-Path $PSScriptRoot "phase17_02_raw_count_qc_profile.py"
}

foreach ($Item in $Scripts.GetEnumerator()) {
    if (-not (Test-Path -LiteralPath $Item.Value)) {
        throw "Missing script: $($Item.Value)"
    }
}

$Python = $null
$Prefix = @()
$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) {
    $Python = $Py.Source
    $Prefix = @("-3")
} else {
    $Cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($Cmd) { $Python = $Cmd.Source }
}
if (-not $Python) { throw "Python 3 not found." }

Write-Host "Phase 17 Gate C1" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host "Output : $RunDir"

& $Python @Prefix $Scripts.Freeze `
    --project-root $ProjectRoot `
    --output-dir $RunDir
if ($LASTEXITCODE -ne 0) { throw "Input freeze failed: $LASTEXITCODE" }

& $Python @Prefix $Scripts.Metadata `
    --project-root $ProjectRoot `
    --output-dir $RunDir
if ($LASTEXITCODE -ne 0) { throw "Metadata audit failed: $LASTEXITCODE" }

& $Python @Prefix $Scripts.QC `
    --project-root $ProjectRoot `
    --output-dir $RunDir
if ($LASTEXITCODE -ne 0) { throw "Raw QC profile failed: $LASTEXITCODE" }

$Workflow = @"
# Phase 17 Gate C1 workflow

- Time: $(Get-Date -Format o)
- Project: ``$ProjectRoot``
- Output: ``$RunDir``

## Completed

1. Input SHA-256 and raw/X integrity.
2. Sample/donor/library/cohort hierarchy.
3. Common-support tables.
4. Repeated-donor manifest.
5. Raw-count QC profile.
6. Sample-aware candidate thresholds.

No source file was modified and no cell was removed.
"@
$Workflow | Set-Content -LiteralPath (Join-Path $RunDir "WORKFLOW_GATE_C1.md") -Encoding UTF8

$Latest = Join-Path $OutputRoot "_LATEST_GATE_C1.txt"
"run_dir=$RunDir" | Set-Content -LiteralPath $Latest -Encoding UTF8

Write-Host ""
Write-Host "Gate C1 completed:" -ForegroundColor Green
Write-Host $RunDir
