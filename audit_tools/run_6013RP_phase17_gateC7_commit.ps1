param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$SafeDirectory = $ProjectRoot.Replace("\", "/")
$AuditPath = Join-Path $ProjectRoot "phase17_v7\gateC7\20260820_manuscript_figure_integration\06_GATE_C7_FINAL_AUDIT.json"

if (-not (Test-Path -LiteralPath $AuditPath)) {
    throw "Gate C7 final audit is missing: $AuditPath"
}

$Decision = (Get-Content -LiteralPath $AuditPath -Raw | ConvertFrom-Json).decision
if ($Decision -ne "PASS_GATE_C7_MANUSCRIPT_AND_FIVE_FIGURE_SCIENTIFIC_FREEZE") {
    throw "Gate C7 is not passed. Observed decision: $Decision"
}

Set-Location -LiteralPath $ProjectRoot
$Branch = (& git -c "safe.directory=$SafeDirectory" branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read the current Git branch."
}
if ($Branch -ne "main") {
    throw "Expected branch main, observed: $Branch"
}

$Paths = @(
    "00_project_management/action_record_2026-08-20_gateC7_manuscript_five_figure_integration.md",
    "00_project_management/next_stage_decision_2026-08-20_gateC8_journal_submission_package.md",
    "01_manuscript/main_figure_legends_v9_gateC7_2026-08-20.md",
    "01_manuscript/manuscript_v9_gateC7_submission_scientific_draft_2026-08-20.md",
    "01_manuscript/research_proposal_v16_gateC7_completed_2026-08-20.md",
    "audit_tools/phase17_c7_01_build_main_figures.py",
    "audit_tools/phase17_c7_02_integrate_manuscript.py",
    "audit_tools/phase17_c7_03_audit_package.py",
    "audit_tools/run_6013RP_phase17_gateC7_commit.ps1",
    "phase17_v7/gateC7"
)

& git -c "safe.directory=$SafeDirectory" add -- @Paths
if ($LASTEXITCODE -ne 0) {
    throw "git add failed."
}

& git -c "safe.directory=$SafeDirectory" diff --cached --check
if ($LASTEXITCODE -ne 0) {
    throw "Staged whitespace or patch validation failed."
}

$Staged = @(& git -c "safe.directory=$SafeDirectory" diff --cached --name-only)
if ($LASTEXITCODE -ne 0 -or $Staged.Count -eq 0) {
    throw "No Gate C7 files were staged."
}

Write-Host "Staged Gate C7 files: $($Staged.Count)"
& git -c "safe.directory=$SafeDirectory" commit -m "Complete Gate C7 manuscript and five-figure integration"
if ($LASTEXITCODE -ne 0) {
    throw "git commit failed."
}

if (-not $NoPush) {
    & git -c "safe.directory=$SafeDirectory" push origin main
    if ($LASTEXITCODE -ne 0) {
        throw "Commit succeeded, but git push failed. Rerun: git push origin main"
    }
}

& git -c "safe.directory=$SafeDirectory" status --short --branch
