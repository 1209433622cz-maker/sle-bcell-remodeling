param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$FigurePython = "D:\bioinfor\python.exe",
    [string]$AuditPython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_reference_terminology_lock\20260901_reference_terminology_s6_refreeze"))
$Documents = Join-Path $Run "documents"
$Qa = Join-Path $Run "qa"
$WpsPages = Join-Path $Qa "wps_pages"
$LibreOfficeDocuments = Join-Path $Qa "libreoffice_documents"
$LibreOfficePages = Join-Path $Qa "lo_pages"
$LibreOfficeRender = Join-Path $Qa "lo_render"
$Accessibility = Join-Path $Qa "accessibility"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"
$Stems = @(
    "Manuscript_reference_terminology_s6_refreeze",
    "Supplementary_Information_reference_terminology_s6_refreeze"
)

foreach ($Path in @($BundledPython, $FigurePython, $AuditPython, $Conda, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required runtime is missing: $Path" }
}
if (-not $Run.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Run directory must resolve within phase17_v7: $Run"
}

$Soffice = Get-ChildItem "C:\Program Files", "C:\Program Files (x86)" -Filter "soffice.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $Soffice) { throw "LibreOffice soffice.exe was not found" }
$env:PATH = $Soffice.DirectoryName + ";" + $env:PATH

Push-Location $Root
try {
    Write-Host "[1/10] Integrating references, terminology and the S6 source redraw..."
    & $FigurePython ".\audit_tools\phase17_npj_sba_28_integrate_reference_terminology_s6.py"
    if ($LASTEXITCODE -ne 0) { throw "Source integration failed" }

    Write-Host "[2/10] Building manuscript and Supplementary DOCX files..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_29_build_reference_terminology_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "DOCX build failed" }

    Write-Host "[3/10] Rendering both DOCX files with WPS..."
    foreach ($Stem in $Stems) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Documents ($Stem + ".docx")) `
            -OutputPdf (Join-Path $Documents ($Stem + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $Stem" }
    }

    Write-Host "[4/10] Auditing and rasterizing all WPS pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $Documents --output-dir $WpsPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }

    Write-Host "[5/10] Cross-rendering both documents with LibreOffice..."
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    foreach ($Stem in $Stems) {
        $Output = Join-Path $LibreOfficeRender $Stem
        & $BundledPython $Renderer (Join-Path $Documents ($Stem + ".docx")) --output_dir $Output --emit_pdf
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed for $Stem" }
        Copy-Item -LiteralPath (Join-Path $Documents ($Stem + ".docx")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".docx")) -Force
        Copy-Item -LiteralPath (Join-Path $Output ($Stem + ".pdf")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) -Force
    }

    Write-Host "[6/10] Auditing and rasterizing all LibreOffice pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }

    Write-Host "[7/10] Checking Supplementary heading/figure co-location..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_09_supplement_pagination_audit.py" `
        --wps-pdf (Join-Path $Documents ($Stems[1] + ".pdf")) `
        --libreoffice-pdf (Join-Path $LibreOfficeDocuments ($Stems[1] + ".pdf")) `
        --source-dir (Join-Path $Run "figures\figures") `
        --expected-pages 16 `
        --output (Join-Path $Run "02_SUPPLEMENT_PAGINATION_AUDIT.json")
    if ($LASTEXITCODE -ne 0) { throw "Supplement pagination audit failed" }

    Write-Host "[8/10] Running DOCX accessibility audits..."
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Stem in $Stems) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Stem + ".docx")) `
            --out_json (Join-Path $Accessibility ($Stem + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Stem" }
    }

    Write-Host "[9/10] Finalizing the scientific refreeze QA and action report..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_30_finalize_reference_terminology_s6_qa.py"
    if ($LASTEXITCODE -ne 0) { throw "Final refreeze QA failed" }

    Write-Host "[10/10] Running the complete regression suite..."
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }
} finally {
    Pop-Location
}

Write-Host "Reference, terminology and S6 scientific refreeze completed."
Write-Host "No submission package, GitHub release or Zenodo record was changed."
