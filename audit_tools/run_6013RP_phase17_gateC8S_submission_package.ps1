param(
    [switch]$SkipMainFigureBuild,
    [switch]$SkipSupplementaryFigureBuild,
    [switch]$SkipStatisticalArchiveBuild,
    [switch]$SkipPageRaster
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root "phase17_v7\gateC8S\20260821_supplementary_traceability_freeze"
$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8S_2026-08-21"
$AnalysisPython = "C:\ProgramData\miniforge3\envs\sle-bcell-v7\python.exe"
$BundledRoot = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies"
$BundledPython = Join-Path $BundledRoot "python\python.exe"
$PdfToPpm = Join-Path $BundledRoot "native\poppler\Library\bin\pdftoppm.exe"
$A11yAudit = Join-Path $env:USERPROFILE ".codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\scripts\a11y_audit.py"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"

foreach ($Required in @($AnalysisPython, $BundledPython, $RenderScript, $A11yAudit)) {
    if (-not (Test-Path -LiteralPath $Required)) {
        throw "Required Gate C8S dependency was not found: $Required"
    }
}
if (-not $SkipPageRaster -and -not (Test-Path -LiteralPath $PdfToPpm)) {
    throw "Bundled pdftoppm was not found: $PdfToPpm"
}

Set-Location -LiteralPath $Root

if ($SkipMainFigureBuild) {
    Write-Host "[1/9] Reusing the frozen five main figures and 46 assertions."
}
else {
    Write-Host "[1/9] Rebuilding five main figures from frozen result tables..."
    & $AnalysisPython (Join-Path $PSScriptRoot "phase17_c7_01_build_main_figures.py") --project-root $Root --output-dir $RunDir
    if ($LASTEXITCODE -ne 0) { throw "Main-figure build failed." }
}

if ($SkipSupplementaryFigureBuild) {
    Write-Host "[2/9] Reusing seven supplementary figures and 29 assertions."
}
else {
    Write-Host "[2/9] Rebuilding seven reviewer-facing supplementary figures..."
    & $AnalysisPython (Join-Path $PSScriptRoot "phase17_c8s_01_build_supplementary_figures.py")
    if ($LASTEXITCODE -ne 0) { throw "Supplementary-figure build failed." }
}

if ($SkipStatisticalArchiveBuild) {
    Write-Host "[3/9] Reusing the verified complete statistical-results archive."
}
else {
    Write-Host "[3/9] Rebuilding the complete statistical-results archive..."
    & $BundledPython (Join-Path $PSScriptRoot "phase17_c8s_02_build_full_statistical_archive.py")
    if ($LASTEXITCODE -ne 0) { throw "Full statistical-results archive build failed." }
}

Write-Host "[4/9] Rebuilding manuscript, supplement and submission sources..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8s_03_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Submission-source build failed." }

Write-Host "[5/9] Rebuilding editable DOCX files and package assets..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8s_04_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Document build failed." }

$Jobs = @(
    @{
        Name = "main_text"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_GateC8S_AUTHOR_COMPLETION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_GateC8S_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\main_text_a11y.json"
    },
    @{
        Name = "supplement"
        Input = Join-Path $Package "additional_files\Additional_file_1_Supplementary_Information_GateC8S.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Additional_file_1_Supplementary_Information_GateC8S_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\supplement_a11y.json"
    },
    @{
        Name = "cover_letter"
        Input = Join-Path $Package "submission_docs\Genome_Medicine_Cover_Letter_GateC8S_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Genome_Medicine_Cover_Letter_GateC8S_AUTHOR_CONFIRMATION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Write-Host "[6/9] Rendering all editable documents with WPS..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
}

if ($SkipPageRaster) {
    Write-Host "[7/9] Reusing existing final-page PNGs."
}
else {
    Write-Host "[7/9] Rasterizing every WPS page for visual review..."
    foreach ($Job in $Jobs) {
        $OutputDirectory = (Resolve-Path -LiteralPath (Split-Path -Parent $Job.Output)).Path
        if (-not $OutputDirectory.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean a page-render directory outside the Gate C8S package: $OutputDirectory"
        }
        Get-ChildItem -LiteralPath $OutputDirectory -File | Where-Object {
            $_.Name -match '^(page|review-page|final-page)-.*\.png$' -or $_.Name -match '^.*contact_sheet.*\.png$'
        } | Remove-Item -Force
        & $PdfToPpm -r 150 -png $Job.Output (Join-Path $OutputDirectory "final-page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[8/9] Auditing DOCX accessibility..."
foreach ($Job in $Jobs) {
    & $BundledPython $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[9/9] Running the Gate C8S scientific, document and deterministic-package audit..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8s_05_final_submission_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8S audit failed." }

Write-Host "Gate C8S package rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8S_2026-08-21.zip")
