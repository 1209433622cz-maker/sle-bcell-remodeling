param(
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [string]$FigurePython = "D:\bioinfor\python.exe",
    [switch]$SkipLibreOfficeCrossRender
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Run = Join-Path $Root "phase17_v7\npj_sba_target_refreeze\20260830_target_specific_refreeze"
$Documents = Join-Path $Run "documents"
$DocumentPages = Join-Path $Run "document_pages"
$LibreOfficeDocuments = Join-Path $Run "libreoffice_documents"
$LibreOfficePages = Join-Path $Run "libreoffice_pages"
$LibreOfficeRender = Join-Path $Run "libreoffice_render"
$DocumentSkill = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.826.12353\skills\documents"
$Renderer = Join-Path $DocumentSkill "render_docx.py"
$AccessibilityAudit = Join-Path $DocumentSkill "scripts\a11y_audit.py"

foreach ($Path in @($BundledPython, $FigurePython, $Renderer, $AccessibilityAudit)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required runtime or script is missing: $Path"
    }
}

Push-Location $Root
try {
    Write-Host "[1/8] Building the target-specific manuscript sources..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_01_build_sources.py"
    if ($LASTEXITCODE -ne 0) { throw "Source build failed" }

    Write-Host "[2/8] Rerendering all 15 figures from frozen source tables..."
    & $FigurePython ".\audit_tools\phase17_npj_sba_02_build_figures.py"
    if ($LASTEXITCODE -ne 0) { throw "Figure build failed" }

    Write-Host "[3/8] Building the manuscript, supplement and cover-letter DOCX files..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_03_build_documents.py"
    if ($LASTEXITCODE -ne 0) { throw "Document build failed" }

    Write-Host "[4/8] Rendering the three final DOCX files with WPS..."
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

    Write-Host "[5/8] Running an independent LibreOffice cross-render..."
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
            --document-dir $LibreOfficeDocuments --output-dir $LibreOfficePages
        if ($LASTEXITCODE -ne 0) { throw "LibreOffice page audit failed" }
        Copy-Item -LiteralPath (Join-Path $LibreOfficePages "document_render_audit.json") `
            -Destination (Join-Path $Run "06_LIBREOFFICE_RENDER_AUDIT.json") -Force
    } elseif (-not (Test-Path -LiteralPath (Join-Path $Run "06_LIBREOFFICE_RENDER_AUDIT.json"))) {
        throw "SkipLibreOfficeCrossRender requires an existing cross-render receipt"
    }

    Write-Host "[6/8] Running accessibility audits..."
    $Accessibility = Join-Path $Run "accessibility"
    New-Item -ItemType Directory -Force -Path $Accessibility | Out-Null
    foreach ($Name in @("Manuscript", "Supplementary_Information", "Cover_Letter")) {
        & $BundledPython $AccessibilityAudit (Join-Path $Documents ($Name + ".docx")) `
            --out_json (Join-Path $Accessibility ($Name + ".json"))
        if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $Name" }
    }

    Write-Host "[7/8] Building the deterministic target package..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_04_build_package.py"
    if ($LASTEXITCODE -ne 0) { throw "Target package build failed" }

    Write-Host "[8/8] Running the final target gate..."
    & $BundledPython ".\audit_tools\phase17_npj_sba_05_final_audit.py"
    if ($LASTEXITCODE -ne 0) { throw "Final target audit failed" }
} finally {
    Pop-Location
}

Write-Host "npj Systems Biology and Applications target refreeze completed."
Write-Host "Exact-file author approval, institutional receipts and submission authorization remain pending."
