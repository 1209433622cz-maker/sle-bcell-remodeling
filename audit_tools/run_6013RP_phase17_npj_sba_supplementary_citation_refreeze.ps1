param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$AuditPython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat",
    [switch]$ConfirmManualVisualQa
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_supplementary_citation_refreeze\20260901_first_citation_order"))
$Documents = Join-Path $Run "documents"
$Qa = Join-Path $Run "qa"
$Candidates = Join-Path $Qa "pagination_candidates"
$LibreOfficeDocuments = Join-Path $Qa "libreoffice_documents"
$FinalLibreOfficeRender = Join-Path $Qa "final_lo_render"
$FinalWpsPages = Join-Path $Qa "final_wps_pages"
$FinalLibreOfficePages = Join-Path $Qa "final_lo_pages"
$Accessibility = Join-Path $Qa "accessibility"
$DocumentSkill = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime\plugins\documents\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"
$MainStem = "Manuscript_scientific_maintenance_freeze"
$SupplementStem = "Supplementary_Information_scientific_maintenance_freeze"
$CandidateStems = @(
    "Supplementary_Information_standard_candidate",
    "Supplementary_Information_compact_candidate"
)

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
    Write-Host "[1/13] Reconstructing and applying the first-citation display map..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_43_integrate_supplementary_citation_refreeze.py"
    if ($LASTEXITCODE -ne 0) { throw "Citation-order integration failed" }

    Write-Host "[2/13] Building the manuscript and Supplementary pagination candidates..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_44_build_supplementary_citation_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "DOCX candidate build failed" }

    Write-Host "[3/13] Rendering both Supplementary candidates with WPS..."
    foreach ($Stem in $CandidateStems) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Candidates ($Stem + ".docx")) `
            -OutputPdf (Join-Path $Candidates ("wps\" + $Stem + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS candidate rendering failed for $Stem" }
    }

    Write-Host "[4/13] Cross-rendering both Supplementary candidates with LibreOffice..."
    & $BundledPython $Renderer (Join-Path $Candidates ($CandidateStems[0] + ".docx")) `
        --output_dir (Join-Path $Candidates ("lo_standard\" + $CandidateStems[0])) --emit_pdf
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice standard-candidate rendering failed" }
    & $BundledPython $Renderer (Join-Path $Candidates ($CandidateStems[1] + ".docx")) `
        --output_dir (Join-Path $Candidates ("lo_compact\" + $CandidateStems[1])) --emit_pdf
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice compact-candidate rendering failed" }

    Write-Host "[5/13] Adjudicating Supplementary pagination and figure fingerprints..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_45_select_supplementary_pagination.py"
    if ($LASTEXITCODE -ne 0) { throw "Supplementary candidate selection failed" }

    Write-Host "[6/13] Rendering final documents with WPS..."
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Documents ($Stem + ".docx")) `
            -OutputPdf (Join-Path $Documents ($Stem + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS final rendering failed for $Stem" }
    }

    Write-Host "[7/13] Cross-rendering final documents with LibreOffice..."
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        $Output = Join-Path $FinalLibreOfficeRender $Stem
        & $BundledPython $Renderer (Join-Path $Documents ($Stem + ".docx")) `
            --output_dir $Output --emit_pdf
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice final rendering failed for $Stem" }
        Copy-Item -LiteralPath (Join-Path $Documents ($Stem + ".docx")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".docx")) -Force
        Copy-Item -LiteralPath (Join-Path $Output ($Stem + ".pdf")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) -Force
    }

    Write-Host "[8/13] Rasterizing and auditing all WPS and LibreOffice pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $Documents --output-dir $FinalWpsPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $FinalLibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }

    Write-Host "[9/13] Checking final Supplementary pagination and figure identity..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_09_supplement_pagination_audit.py" `
        --wps-pdf (Join-Path $Documents ($SupplementStem + ".pdf")) `
        --libreoffice-pdf (Join-Path $LibreOfficeDocuments ($SupplementStem + ".pdf")) `
        --source-dir (Join-Path $Run "figures\figures") `
        --expected-pages 15 `
        --output (Join-Path $Run "07_FINAL_SUPPLEMENT_PAGINATION_AUDIT.json")
    if ($LASTEXITCODE -ne 0) { throw "Final Supplementary pagination audit failed" }

    Write-Host "[10/13] Running DOCX accessibility audits..."
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Stem + ".docx")) `
            --out_json (Join-Path $Accessibility ($Stem + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Stem" }
    }

    if (-not $ConfirmManualVisualQa) {
        Write-Host "Manual visual QA is required before finalization. Inspect:"
        Write-Host "  $FinalWpsPages"
        Write-Host "  $FinalLibreOfficePages"
        throw "Rerun with -ConfirmManualVisualQa only after all 18 contact sheets have been inspected"
    }

    Write-Host "[11/13] Writing the pre-regression scientific freeze..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_46_finalize_supplementary_citation_refreeze.py" `
        --confirm-manual-visual-qa
    if ($LASTEXITCODE -ne 0) { throw "Pre-regression citation-refreeze QA failed" }

    Write-Host "[12/13] Running the complete regression suite..."
    $CountOutput = & $Conda run -n sle-bcell python -c `
        "import unittest; print(unittest.defaultTestLoader.discover('audit_tools', pattern='test_*.py').countTestCases())"
    if ($LASTEXITCODE -ne 0) { throw "Could not count regression tests" }
    $TestCount = [int](($CountOutput | Select-Object -Last 1).Trim())
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }

    Write-Host "[13/13] Locking the regression result into the final status and action record..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_46_finalize_supplementary_citation_refreeze.py" `
        --confirm-manual-visual-qa --confirm-regression-pass --regression-tests-run $TestCount
    if ($LASTEXITCODE -ne 0) { throw "Final citation-refreeze QA failed" }
} finally {
    Pop-Location
}

Write-Host "Supplementary first-citation-order scientific refreeze completed."
Write-Host "No scientific estimate, figure pixel, Source Data value, submission package, Release or Zenodo record changed."
