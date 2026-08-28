param(
    [string]$Python = "python",
    [string]$OutputDir = "04_submission\author_review",
    [string]$DocumentDir = "phase17_v7\post_gateC9\20260828_external_review\documents",
    [string]$FigureReview = "phase17_v7\post_gateC9\20260828_advisor_correction_review",
    [string]$AuditDir = "00_project_management\external_review_2026-08-28"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Push-Location -LiteralPath $Root
try {
    & $Python (Join-Path $PSScriptRoot "phase17_postc9_06_build_correction_package.py") `
        --output-dir $OutputDir --document-dir $DocumentDir `
        --figure-review $FigureReview --audit-dir $AuditDir
    if ($LASTEXITCODE -ne 0) { throw "Correction review build failed; nothing is authorized for submission." }
}
finally {
    Pop-Location
}
