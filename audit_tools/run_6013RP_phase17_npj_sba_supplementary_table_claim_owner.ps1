param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$AuditPython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat",
    [switch]$ConfirmManualVisualQa
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_supplementary_table_claim_owner\20260902_semantic_micropass"))
$Documents = Join-Path $Run "documents"
$Qa = Join-Path $Run "qa"
$LibreOfficeDocuments = Join-Path $Qa "libreoffice_documents"
$LibreOfficeRender = Join-Path $Qa "lo_render"
$WpsPages = Join-Path $Qa "wps_pages"
$LibreOfficePages = Join-Path $Qa "lo_pages"
$Accessibility = Join-Path $Qa "accessibility"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"
$Stem = "Manuscript_claim_owner_semantic_micropass"

foreach ($Path in @($BundledPython, $AuditPython, $Conda, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required runtime is missing: $Path" }
}
$Phase17 = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7"))
if (-not $Run.StartsWith($Phase17, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Run directory must resolve within phase17_v7: $Run"
}
$Soffice = "C:\Program Files\LibreOffice\program\soffice.exe"
if (-not (Test-Path -LiteralPath $Soffice)) { throw "LibreOffice was not found: $Soffice" }
$env:PATH = (Split-Path -Parent $Soffice) + ";" + $env:PATH

Push-Location $Root
try {
    Write-Host "[1/9] Applying exact claim-owner edits and locking frozen assets..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_47_integrate_supplementary_table_claim_owner.py"
    if ($LASTEXITCODE -ne 0) { throw "Claim-owner integration failed" }

    Write-Host "[2/9] Building the canonical manuscript DOCX..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_48_build_supplementary_table_claim_owner_document.py"
    if ($LASTEXITCODE -ne 0) { throw "Claim-owner DOCX build failed" }

    Write-Host "[3/9] Rendering the manuscript with WPS..."
    & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
        -InputDocx (Join-Path $Documents ($Stem + ".docx")) `
        -OutputPdf (Join-Path $Documents ($Stem + ".pdf"))
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed" }

    Write-Host "[4/9] Cross-rendering the manuscript with LibreOffice..."
    $Output = Join-Path $LibreOfficeRender $Stem
    & $BundledPython $Renderer (Join-Path $Documents ($Stem + ".docx")) --output_dir $Output --emit_pdf
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed" }
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    Copy-Item -LiteralPath (Join-Path $Documents ($Stem + ".docx")) -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".docx")) -Force
    Copy-Item -LiteralPath (Join-Path $Output ($Stem + ".pdf")) -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) -Force

    Write-Host "[5/9] Rasterizing and structurally auditing both renderers..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" --document-dir $Documents --output-dir $WpsPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }

    Write-Host "[6/9] Running DOCX accessibility audit..."
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Stem + ".docx")) --out_json (Join-Path $Accessibility ($Stem + ".json"))
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed" }

    if (-not $ConfirmManualVisualQa) {
        Write-Host "Manual visual QA is required before finalization. Inspect:"
        Write-Host "  $WpsPages"
        Write-Host "  $LibreOfficePages"
        throw "Rerun with -ConfirmManualVisualQa only after all 12 contact sheets have been inspected"
    }

    Write-Host "[7/9] Writing the pre-regression maintenance freeze..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_49_finalize_supplementary_table_claim_owner.py" --confirm-manual-visual-qa
    if ($LASTEXITCODE -ne 0) { throw "Pre-regression finalization failed" }

    Write-Host "[8/9] Running the complete regression suite..."
    $CountOutput = & $Conda run -n sle-bcell python -c `
        "import unittest; print(unittest.defaultTestLoader.discover('audit_tools', pattern='test_*.py').countTestCases())"
    if ($LASTEXITCODE -ne 0) { throw "Could not count regression tests" }
    $TestCount = [int](($CountOutput | Select-Object -Last 1).Trim())
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }

    Write-Host "[9/9] Locking regression result and action record..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_49_finalize_supplementary_table_claim_owner.py" `
        --confirm-manual-visual-qa --confirm-regression-pass --regression-tests-run $TestCount
    if ($LASTEXITCODE -ne 0) { throw "Final claim-owner QA failed" }
} finally {
    Pop-Location
}

Write-Host "Supplementary Table claim-owner semantic micropass completed."
Write-Host "No estimate, model, artwork pixel, Source Data value, submission package, Release or Zenodo record changed."
