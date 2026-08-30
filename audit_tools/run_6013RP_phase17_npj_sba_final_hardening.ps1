param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$FigurePython = "D:\bioinfor\python.exe",
    [string]$RunDir = ".\phase17_v7\npj_sba_final_hardening\20260830_final_render_semantic_hardening",
    [string]$ManagementDir = ".\00_project_management\npj_sba_final_hardening_2026-08-30",
    [switch]$SkipLibreOfficeCrossRender
)

$ErrorActionPreference = "Stop"
$Root = (Split-Path -Parent $PSScriptRoot)
$Run = [System.IO.Path]::GetFullPath((Join-Path $Root $RunDir))
$Management = [System.IO.Path]::GetFullPath((Join-Path $Root $ManagementDir))
$Documents = Join-Path $Run "documents"
$DocumentPages = Join-Path $Run "document_pages"
$LibreOfficeDocuments = Join-Path $Run "libreoffice_documents"
$LibreOfficePages = Join-Path $Run "libreoffice_pages"
$LibreOfficeRender = Join-Path $Run "libreoffice_render"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"

if (-not $Run.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "phase17_v7")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "RunDir must resolve within phase17_v7: $Run"
}
if (-not $Management.StartsWith([System.IO.Path]::GetFullPath((Join-Path $Root "00_project_management")), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "ManagementDir must resolve within 00_project_management: $Management"
}
foreach ($Path in @($BundledPython, $FigurePython, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required runtime or script is missing: $Path"
    }
}

$PreviousRunDir = $env:NPJ_SBA_RUN_DIR
$PreviousManagementDir = $env:NPJ_SBA_MANAGEMENT_DIR
$env:NPJ_SBA_RUN_DIR = $Run
$env:NPJ_SBA_MANAGEMENT_DIR = $Management
New-Item -ItemType Directory -Force -Path $Run, $Management | Out-Null

Push-Location $Root
try {
    Write-Host "[1/10] Building the final-hardened manuscript sources..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_01_build_sources.py"
    if ($LASTEXITCODE -ne 0) { throw "Source build failed" }

    Write-Host "[2/10] Auditing received evidence and scientific-token preservation..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_00_audit_hardening_evidence.py"
    if ($LASTEXITCODE -ne 0) { throw "Hardening evidence audit failed" }

    Write-Host "[3/10] Rerendering all 15 figures and inspecting exported PDF artifacts..."
    & $FigurePython ".\audit_tools\phase17_npj_sba_02_build_figures.py"
    if ($LASTEXITCODE -ne 0) { throw "Figure build or artifact postflight failed" }

    Write-Host "[4/10] Building manuscript, supplement and cover-letter DOCX files..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_03_build_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "Document build failed" }

    Write-Host "[5/10] Rendering the three final DOCX files with WPS..."
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        & powershell -ExecutionPolicy Bypass -File ".\audit_tools\render_docx_with_wps.ps1" `
            -InputDocx (Join-Path $Documents ($Name + ".docx")) `
            -OutputPdf (Join-Path $Documents ($Name + ".pdf"))
        if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $Name" }
    }
    & $FigurePython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
        --document-dir $Documents --output-dir $DocumentPages
    if ($LASTEXITCODE -ne 0) { throw "WPS page audit failed" }
    Copy-Item -LiteralPath (Join-Path $DocumentPages "document_render_audit.json") `
        -Destination (Join-Path $Run "05_WPS_RENDER_AUDIT.json") -Force

    Write-Host "[6/10] Running an independent LibreOffice cross-render..."
    if (-not $SkipLibreOfficeCrossRender) {
        $Soffice = Get-ChildItem "C:\Program Files", "C:\Program Files (x86)" `
            -Filter "soffice.exe" -Recurse -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if (-not $Soffice) { throw "LibreOffice soffice.exe was not found" }
        $env:PATH = $Soffice.DirectoryName + ";" + $env:PATH
        New-Item -ItemType Directory -Force -Path $LibreOfficeDocuments | Out-Null
        foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
            $Output = Join-Path $LibreOfficeRender $Name
            & $BundledPython $Renderer (Join-Path $Documents ($Name + ".docx")) `
                --output_dir $Output --emit_pdf
            if ($LASTEXITCODE -ne 0) { throw "LibreOffice rendering failed for $Name" }
            Copy-Item -LiteralPath (Join-Path $Documents ($Name + ".docx")) `
                -Destination (Join-Path $LibreOfficeDocuments ($Name + ".docx")) -Force
            Copy-Item -LiteralPath (Join-Path $Output ($Name + ".pdf")) `
                -Destination (Join-Path $LibreOfficeDocuments ($Name + ".pdf")) -Force
        }
        & $FigurePython ".\audit_tools\phase17_postc9_04_document_render_audit.py" `
            --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages `
            --engine-label "LibreOffice PDF export followed by Poppler 110-dpi page rendering"
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }
        Copy-Item -LiteralPath (Join-Path $LibreOfficePages "document_render_audit.json") `
            -Destination (Join-Path $Run "06_LIBREOFFICE_RENDER_AUDIT.json") -Force
    } elseif (-not (Test-Path -LiteralPath (Join-Path $Run "06_LIBREOFFICE_RENDER_AUDIT.json"))) {
        throw "SkipLibreOfficeCrossRender requires an existing cross-render receipt"
    }

    Write-Host "[7/10] Running accessibility audits..."
    $Accessibility = Join-Path $Run "accessibility"
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Name + ".docx")) `
            --out_json (Join-Path $Accessibility ($Name + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Name" }
    }

    Write-Host "[8/10] Building the deterministic final-hardened package..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_04_build_package.py"
    if ($LASTEXITCODE -ne 0) { throw "Target package build failed" }

    Write-Host "[9/10] Running regression tests..."
    & $BundledPython ".\audit_tools\test_npj_sba_target_refreeze.py"
    if ($LASTEXITCODE -ne 0) { throw "Regression tests failed" }

    Write-Host "[10/10] Running the final hardening gate..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_05_final_audit.py"
    if ($LASTEXITCODE -ne 0) { throw "Final hardening gate failed" }
} finally {
    Pop-Location
    $env:NPJ_SBA_RUN_DIR = $PreviousRunDir
    $env:NPJ_SBA_MANAGEMENT_DIR = $PreviousManagementDir
}

Write-Host "npj SBA final render and semantic hardening completed."
Write-Host "Exact-file author approval, institutional receipts and submission authorization remain pending."
