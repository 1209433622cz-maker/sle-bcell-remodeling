param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$FigurePython = "D:\bioinfor\python.exe",
    [string]$Conda = "C:\ProgramData\miniforge3\condabin\conda.bat",
    [string]$RunDir = ".\phase17_v7\npj_sba_final_hardening\20260830_final_render_semantic_hardening",
    [string]$RepairRunDir = ".\phase17_v7\npj_sba_s8_narrow_repair\20260830_source_replot_rebuild"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root $RunDir))
$RepairRun = [System.IO.Path]::GetFullPath((Join-Path $Root $RepairRunDir))
$Documents = Join-Path $Run "documents"
$DocumentPages = Join-Path $Run "document_pages"
$LibreOfficeDocuments = Join-Path $Run "libreoffice_documents"
$LibreOfficePages = Join-Path $Run "libreoffice_pages"
$LibreOfficeRender = Join-Path $Run "libreoffice_render"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"

foreach ($Path in @($BundledPython, $FigurePython, $Conda, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required runtime is missing: $Path" }
}
if (-not $Run.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RunDir must resolve within phase17_v7: $Run"
}
if (-not $RepairRun.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RepairRunDir must resolve within phase17_v7: $RepairRun"
}

$Soffice = Get-ChildItem "C:\Program Files", "C:\Program Files (x86)" -Filter "soffice.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $Soffice) { throw "LibreOffice soffice.exe was not found" }
$env:PATH = $Soffice.DirectoryName + ";" + $env:PATH
$env:NPJ_SBA_RUN_DIR = $Run
$env:NPJ_SBA_S8_REPAIR_RUN_DIR = $RepairRun
$env:NPJ_SBA_APPROVAL_RUN_DIR = [System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7\npj_sba_submission_gate\20260830_exact_file_approval_preparation"))

Push-Location $Root
try {
    Write-Host "[1/12] Replotting S8 from the frozen overlap-depletion table..."
    & $FigurePython ".\audit_tools\phase17_npj_sba_08_s8_narrow_repair.py"
    if ($LASTEXITCODE -ne 0) { throw "S8 source replot failed" }

    Write-Host "[2/12] Rebuilding DOCX artifacts from the frozen Markdown sources..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_03_build_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "DOCX build failed" }

    Write-Host "[3/12] Rendering the three DOCX files with WPS..."
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Documents ($Name + ".docx")) `
            -OutputPdf (Join-Path $Documents ($Name + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $Name" }
    }

    Write-Host "[4/12] Auditing WPS pages..."
    & $FigurePython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $Documents --output-dir $DocumentPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }
    Copy-Item -LiteralPath (Join-Path $DocumentPages "document_render_audit.json") `
        -Destination (Join-Path $Run "05_WPS_RENDER_AUDIT.json") -Force

    Write-Host "[5/12] Cross-rendering with LibreOffice..."
    New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        $Output = Join-Path $LibreOfficeRender $Name
        & $BundledPython $Renderer (Join-Path $Documents ($Name + ".docx")) --output_dir $Output --emit_pdf
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed for $Name" }
        Copy-Item -LiteralPath (Join-Path $Documents ($Name + ".docx")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Name + ".docx")) -Force
        Copy-Item -LiteralPath (Join-Path $Output ($Name + ".pdf")) `
            -Destination (Join-Path $LibreOfficeDocuments ($Name + ".pdf")) -Force
    }

    Write-Host "[6/12] Auditing LibreOffice pages..."
    & $FigurePython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
        --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
    if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }
    Copy-Item -LiteralPath (Join-Path $LibreOfficePages "document_render_audit.json") `
        -Destination (Join-Path $Run "06_LIBREOFFICE_RENDER_AUDIT.json") -Force

    Write-Host "[7/12] Requiring heading/figure co-location and expected-image identity in both renderers..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_09_supplement_pagination_audit.py" `
        --wps-pdf (Join-Path $Documents "Supplementary_Information.pdf") `
        --libreoffice-pdf (Join-Path $LibreOfficeDocuments "Supplementary_Information.pdf") `
        --source-dir (Join-Path $Run "figures\figures") `
        --output (Join-Path $Run "07_SUPPLEMENT_PAGINATION_AUDIT.json")
    if ($LASTEXITCODE -ne 0) { throw "Supplement pagination audit failed" }

    Write-Host "[8/12] Running DOCX accessibility audits..."
    $Accessibility = Join-Path $Run "accessibility"
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Name + ".docx")) `
            --out_json (Join-Path $Accessibility ($Name + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Name" }
    }

    Write-Host "[9/12] Rebuilding and verifying the deterministic exact package..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_04_build_package.py"
    if ($LASTEXITCODE -ne 0) { throw "Package build failed" }

    Write-Host "[10/12] Running the final npj audit..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_05_final_audit.py"
    if ($LASTEXITCODE -ne 0) { throw "Final npj audit failed" }

    Write-Host "[11/12] Refreezing the exact-file approval gate..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_07_exact_file_approval_preparation.py"
    if ($LASTEXITCODE -ne 0) { throw "Exact-file approval preparation failed" }

    Write-Host "[12/12] Running the complete regression suite..."
    & $Conda run -n sle-bcell python -m unittest discover -s audit_tools -p "test_*.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression suite failed" }
} finally {
    Pop-Location
}

Write-Host "S8 narrow repair and exact-package refreeze completed."
Write-Host "Both-author exact-file approval, institutional JCR/APC receipts and portal authorization remain pending."
