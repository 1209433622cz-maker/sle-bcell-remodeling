param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$AuditPython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat",
    [switch]$ConfirmManualVisualQa
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_scientific_presentation_maintenance_freeze\20260908_final_cross_document"))
$Documents = Join-Path $Run "documents"
$Qa = Join-Path $Run "qa"
$WpsPages = Join-Path $Qa "final_wps_pages"
$LibreOfficeDocuments = Join-Path $Qa "final_libreoffice_documents"
$LibreOfficeRender = Join-Path $Qa "lr"
$LibreOfficePages = Join-Path $Qa "final_lo_pages"
$ParentWpsPages = Join-Path $Qa "parent_wps_pages"
$Accessibility = Join-Path $Qa "final_accessibility"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.905.11957\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"
$MainStem = "Manuscript_Scientific_Presentation_Freeze"
$SupplementStem = "Supplementary_Information_Scientific_Presentation_Freeze"
$ParentMainPdf = Join-Path $Root "phase17_v7\npj_sba_figure5_regulatory_ceiling\20260908_canonical_source_integration\documents\Manuscript_Figure5_regulatory_ceiling.pdf"
$ParentSupplementPdf = Join-Path $Root "phase17_v7\npj_sba_supplementary_citation_refreeze\20260901_first_citation_order\documents\Supplementary_Information_scientific_maintenance_freeze.pdf"

foreach ($Path in @($BundledPython, $AuditPython, $Conda, $Renderer, $AccessibilityAudit, $ParentMainPdf, $ParentSupplementPdf)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required input or runtime is missing: $Path" }
}
$Phase17 = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7"))
if (-not $Run.StartsWith($Phase17, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Run directory must resolve within phase17_v7: $Run"
}
$Soffice = "C:\Program Files\LibreOffice\program\soffice.exe"
if (-not (Test-Path -LiteralPath $Soffice)) { throw "LibreOffice was not found: $Soffice" }
$Pdftoppm = (Get-Command pdftoppm -ErrorAction Stop).Source
$env:PATH = (Split-Path -Parent $Soffice) + ";" + $env:PATH

Push-Location $Root
try {
    Write-Host "[1/11] Integrating the two source-level cross-document repairs..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_59_integrate_final_cross_document_freeze.py"
    if ($LASTEXITCODE -ne 0) { throw "Cross-document integration failed" }

    Write-Host "[2/11] Building manuscript and Supplementary DOCX files..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_60_build_final_cross_document_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "Document build failed" }

    Write-Host "[3/11] Rendering both documents with WPS..."
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Documents ($Stem + ".docx")) `
            -OutputPdf (Join-Path $Documents ($Stem + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $Stem" }
    }

    Write-Host "[4/11] Cross-rendering both documents with LibreOffice..."
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    $ShortRenderFolders = @{}
    $ShortRenderFolders[$MainStem] = "M"
    $ShortRenderFolders[$SupplementStem] = "S"
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        $Output = Join-Path $LibreOfficeRender $ShortRenderFolders[$Stem]
        & $BundledPython $Renderer (Join-Path $Documents ($Stem + ".docx")) --output_dir $Output --emit_pdf
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed for $Stem" }
        Copy-Item -LiteralPath (Join-Path $Documents ($Stem + ".docx")) -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".docx")) -Force
        Copy-Item -LiteralPath (Join-Path $Output ($Stem + ".pdf")) -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) -Force
    }

    Write-Host "[5/11] Rasterizing and structurally auditing 92 rendered pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" --document-dir $Documents --output-dir $WpsPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }

    Write-Host "[6/11] Rendering parent WPS baselines for page-pixel comparison..."
    $ParentMainPages = Join-Path $ParentWpsPages "Parent_Manuscript"
    $ParentSupplementPages = Join-Path $ParentWpsPages "Parent_Supplement"
    New-Item -ItemType Directory -Force -Path $ParentMainPages, $ParentSupplementPages | Out-Null
    & $Pdftoppm -r 110 -png $ParentMainPdf (Join-Path $ParentMainPages "page")
    if ($LASTEXITCODE -ne 0) { throw "Parent manuscript rasterization failed" }
    & $Pdftoppm -r 110 -png $ParentSupplementPdf (Join-Path $ParentSupplementPages "page")
    if ($LASTEXITCODE -ne 0) { throw "Parent Supplementary rasterization failed" }

    Write-Host "[7/11] Checking Supplementary pagination and all ten figure fingerprints..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_09_supplement_pagination_audit.py" `
        --wps-pdf (Join-Path $Documents ($SupplementStem + ".pdf")) `
        --libreoffice-pdf (Join-Path $LibreOfficeDocuments ($SupplementStem + ".pdf")) `
        --source-dir (Join-Path $Run "figures\figures") `
        --expected-pages 15 `
        --output (Join-Path $Qa "final_supplement_pagination_audit.json")
    if ($LASTEXITCODE -ne 0) { throw "Supplementary pagination audit failed" }

    Write-Host "[8/11] Running accessibility audits for both DOCX files..."
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Stem in @($MainStem, $SupplementStem)) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Stem + ".docx")) `
            --out_json (Join-Path $Accessibility ($Stem + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Stem" }
    }

    if (-not $ConfirmManualVisualQa) {
        Write-Host "Manual visual QA is required before finalization. Inspect all contact sheets in:"
        Write-Host "  $WpsPages"
        Write-Host "  $LibreOfficePages"
        throw "Rerun with -ConfirmManualVisualQa only after all 18 contact sheets have been inspected"
    }

    Write-Host "[9/11] Running the complete regression suite..."
    $CountOutput = & $Conda run -n sle-bcell python -c `
        "import unittest; print(unittest.defaultTestLoader.discover('audit_tools', pattern='test_*.py').countTestCases())"
    if ($LASTEXITCODE -ne 0) { throw "Could not count regression tests" }
    $TestCount = [int](($CountOutput | Select-Object -Last 1).Trim())
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }

    Write-Host "[10/11] Finalizing the scientific-presentation maintenance freeze..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_61_finalize_scientific_presentation_maintenance_freeze.py" `
        --confirm-manual-visual-qa --confirm-regression-pass --regression-tests-run $TestCount
    if ($LASTEXITCODE -ne 0) { throw "Maintenance-freeze finalization failed" }

    Write-Host "[11/11] Re-running regression tests against the final manifest..."
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Post-finalization regression suite failed" }
} finally {
    Pop-Location
}

Write-Host "Scientific-presentation final cross-document freeze completed."
Write-Host "No estimate, model, figure pixel, Source Data value, submission package, Release or Zenodo record changed."
