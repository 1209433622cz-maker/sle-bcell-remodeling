param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$AuditPython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_supplementary_table_reader_path\20260901_s4_reader_path_refreeze"))
$Documents = Join-Path $Run "documents"
$Qa = Join-Path $Run "qa"
$WpsPages = Join-Path $Qa "wps_pages"
$LibreOfficeDocuments = Join-Path $Qa "libreoffice_documents"
$LibreOfficePages = Join-Path $Qa "lo_pages"
$LibreOfficeRender = Join-Path $Qa "lo_render"
$Accessibility = Join-Path $Qa "accessibility"
$Stem = "Supplementary_Information_scientific_maintenance_freeze"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"

foreach ($Path in @($BundledPython, $AuditPython, $Conda, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required runtime is missing: $Path" }
}
$Phase17 = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7"))
if (-not $Run.StartsWith($Phase17, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Run directory must resolve within phase17_v7: $Run"
}

$Soffice = Get-ChildItem "C:\Program Files", "C:\Program Files (x86)" -Filter "soffice.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $Soffice) { throw "LibreOffice soffice.exe was not found" }
$env:PATH = $Soffice.DirectoryName + ";" + $env:PATH

Push-Location $Root
try {
    Write-Host "[1/10] Integrating the localized S4 reader-path repair..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_40_integrate_supplementary_table_reader_path.py"
    if ($LASTEXITCODE -ne 0) { throw "S4 reader-path integration failed" }

    Write-Host "[2/10] Building Supplementary Information only..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_41_build_supplementary_table_reader_document.py"
    if ($LASTEXITCODE -ne 0) { throw "Supplementary DOCX build failed" }

    Write-Host "[3/10] Rendering Supplementary Information with WPS..."
    & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
        -InputDocx (Join-Path $Documents ($Stem + ".docx")) `
        -OutputPdf (Join-Path $Documents ($Stem + ".pdf"))
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed" }

    Write-Host "[4/10] Auditing WPS pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $Documents --output-dir $WpsPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }

    Write-Host "[5/10] Cross-rendering with LibreOffice..."
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    $Output = Join-Path $LibreOfficeRender $Stem
    & $BundledPython $Renderer (Join-Path $Documents ($Stem + ".docx")) --output_dir $Output --emit_pdf
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed" }
    Copy-Item -LiteralPath (Join-Path $Documents ($Stem + ".docx")) `
        -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".docx")) -Force
    Copy-Item -LiteralPath (Join-Path $Output ($Stem + ".pdf")) `
        -Destination (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) -Force

    Write-Host "[6/10] Auditing LibreOffice pages..."
    & $AuditPython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }

    Write-Host "[7/10] Checking Supplementary pagination and figure fingerprints..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_09_supplement_pagination_audit.py" `
        --wps-pdf (Join-Path $Documents ($Stem + ".pdf")) `
        --libreoffice-pdf (Join-Path $LibreOfficeDocuments ($Stem + ".pdf")) `
        --source-dir (Join-Path $Run "figures\figures") `
        --expected-pages 16 `
        --output (Join-Path $Run "05_SUPPLEMENT_PAGINATION_AUDIT.json")
    if ($LASTEXITCODE -ne 0) { throw "Supplement pagination audit failed" }

    Write-Host "[8/10] Running DOCX accessibility audit..."
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Stem + ".docx")) `
        --out_json (Join-Path $Accessibility ($Stem + ".json"))
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed" }

    Write-Host "[9/10] Finalizing the reader-path maintenance freeze..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_42_finalize_supplementary_table_reader_path.py"
    if ($LASTEXITCODE -ne 0) { throw "Final reader-path QA failed" }

    Write-Host "[10/10] Running the complete regression suite..."
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }
} finally {
    Pop-Location
}

Write-Host "Supplementary Table S4 reader-path micropass completed."
Write-Host "No figure, Source Data, submission package, GitHub release or Zenodo record was changed."
