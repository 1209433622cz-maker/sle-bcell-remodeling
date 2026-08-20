param(
    [switch]$SkipFigureBuild,
    [switch]$SkipCorrelationSensitivity,
    [switch]$SkipReferenceRefresh,
    [switch]$SkipPageRaster
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BundledRoot = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies"
$BundledPython = Join-Path $BundledRoot "python\python.exe"
$BundledPdfToPpm = Join-Path $BundledRoot "native\poppler\Library\bin\pdftoppm.exe"
$A11yAudit = Join-Path $env:USERPROFILE ".codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\scripts\a11y_audit.py"
$AnalysisPython = "C:\ProgramData\miniforge3\envs\sle-bcell-v7\python.exe"
$Rscript = "C:\Program Files\R\R-4.6.0\bin\Rscript.exe"

foreach ($Required in @($BundledPython, $AnalysisPython, $Rscript)) {
    if (-not (Test-Path -LiteralPath $Required)) {
        throw "Required executable was not found: $Required"
    }
}

$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8R_2026-08-20"
$RunDir = Join-Path $Root "phase17_v7\gateC8R\20260820_pre_submission_repair"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"
$Jobs = @(
    @{
        Name = "main_text"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_GateC8R_AUTHOR_COMPLETION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_GateC8R_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\main_text_a11y.json"
    },
    @{
        Name = "supplement"
        Input = Join-Path $Package "additional_files\Additional_file_1_Supplementary_Information_GateC8R.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Additional_file_1_Supplementary_Information_GateC8R_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\supplement_a11y.json"
    },
    @{
        Name = "cover_letter"
        Input = Join-Path $Package "submission_docs\Genome_Medicine_Cover_Letter_GateC8R_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Genome_Medicine_Cover_Letter_GateC8R_AUTHOR_CONFIRMATION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Set-Location -LiteralPath $Root

if (-not $SkipFigureBuild) {
    Write-Host "[1/8] Rebuilding five figures with panel-data assertions..."
    & $AnalysisPython (Join-Path $PSScriptRoot "phase17_c7_01_build_main_figures.py") --project-root $Root --output-dir $RunDir
    if ($LASTEXITCODE -ne 0) { throw "Figure build failed." }
}
else {
    Write-Host "[1/8] Reusing frozen Gate C8R figures and 43 panel assertions."
}

if (-not $SkipCorrelationSensitivity) {
    Write-Host "[2/8] Rebuilding correlation-aware STAT1/STAT2 sensitivity..."
    $PreviousLcAll = $env:LC_ALL
    $PreviousLang = $env:LANG
    try {
        $env:LC_ALL = "C"
        $env:LANG = "C"
        & $Rscript (Join-Path $PSScriptRoot "phase17_c8r_01_correlation_aware_regulator_sensitivity.R") $Root $RunDir
        if ($LASTEXITCODE -ne 0) { throw "Correlation-aware sensitivity failed." }
    }
    finally {
        $env:LC_ALL = $PreviousLcAll
        $env:LANG = $PreviousLang
    }
}
else {
    Write-Host "[2/8] Reusing frozen Gate C8R regulator sensitivity."
}

if (-not $SkipReferenceRefresh) {
    Write-Host "[3/8] Refreshing and verifying DOI metadata..."
    & $BundledPython (Join-Path $PSScriptRoot "phase17_c8r_02_verify_references.py")
    if ($LASTEXITCODE -ne 0) { throw "Reference verification failed." }
}
else {
    Write-Host "[3/8] Reusing frozen Gate C8R reference verification."
}

Write-Host "[4/8] Rebuilding journal-specific Markdown sources..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8r_03_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Submission source build failed." }

Write-Host "[5/8] Rebuilding editable DOCX files and package assets..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8r_04_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Document build failed." }

Write-Host "[6/8] Rendering all editable documents with the WPS COM backend..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
    if (-not $SkipPageRaster) {
        if (-not (Test-Path -LiteralPath $BundledPdfToPpm)) {
            throw "Bundled pdftoppm was not found. Re-run with -SkipPageRaster only if current page PNGs exist."
        }
        $OutputDirectory = Split-Path -Parent $Job.Output
        Get-ChildItem -LiteralPath $OutputDirectory -Filter "page-*.png" -File -ErrorAction SilentlyContinue | Remove-Item -Force
        Get-ChildItem -LiteralPath $OutputDirectory -Filter "review-page-*.png" -File -ErrorAction SilentlyContinue | Remove-Item -Force
        & $BundledPdfToPpm -r 150 -png $Job.Output (Join-Path $OutputDirectory "page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[7/8] Auditing DOCX accessibility..."
if (-not (Test-Path -LiteralPath $A11yAudit)) {
    throw "Bundled DOCX accessibility auditor was not found: $A11yAudit"
}
foreach ($Job in $Jobs) {
    & $BundledPython $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[8/8] Running scientific, figure, document and deterministic-package audit..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8r_05_final_submission_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8R audit failed." }

Write-Host "Gate C8R package rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8R_2026-08-20.zip")
