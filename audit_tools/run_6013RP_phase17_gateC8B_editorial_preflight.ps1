param(
    [string]$AnalysisPython = "D:\bioinfor\python.exe",
    [string]$BundledPython = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    [switch]$SkipReferenceVerification,
    [switch]$SkipMainFigureBuild,
    [switch]$SkipPageRaster
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root "phase17_v7\gateC8B\20260821_editorial_literature_preflight"
$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8B_editorial_preflight_2026-08-21"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"
$A11yAudit = "C:\Users\Administrator\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\scripts\a11y_audit.py"
$PdfToPpm = "C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe"

foreach ($Path in @($AnalysisPython, $BundledPython, $RenderScript, $A11yAudit, $PdfToPpm)) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Required dependency not found: $Path" }
}

Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

if ($SkipReferenceVerification) {
    Write-Host "[1/8] Reusing Gate C8B reference verification."
}
else {
    Write-Host "[1/8] Verifying 27 DOI records, including Sayadi et al. 2026..."
    & $BundledPython (Join-Path $PSScriptRoot "phase17_c8b_01_verify_references.py")
    if ($LASTEXITCODE -ne 0) { throw "Reference verification failed." }
}

if ($SkipMainFigureBuild) {
    Write-Host "[2/8] Reusing Gate C8B main figures."
}
else {
    Write-Host "[2/8] Rerendering Figure 5 with specificity wording and carrying forward frozen Figures 1-4..."
    & $AnalysisPython (Join-Path $PSScriptRoot "phase17_c8b_00_build_main_figures.py")
    if ($LASTEXITCODE -ne 0) { throw "Main-figure build failed." }
}

Write-Host "[3/8] Building v13 manuscript and editorial-preflight sources..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8b_02_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Submission-source build failed." }

Write-Host "[4/8] Building editable DOCX files and package assets..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8b_03_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Document build failed." }

$Jobs = @(
    @{
        Name = "main_text"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_GateC8B_AUTHOR_COMPLETION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_GateC8B_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\main_text_a11y.json"
    },
    @{
        Name = "supplement"
        Input = Join-Path $Package "additional_files\Additional_file_1_Supplementary_Information_GateC8B.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Additional_file_1_Supplementary_Information_GateC8B_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\supplement_a11y.json"
    },
    @{
        Name = "cover_letter"
        Input = Join-Path $Package "submission_docs\Genome_Medicine_Cover_Letter_GateC8B_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Genome_Medicine_Cover_Letter_GateC8B_AUTHOR_CONFIRMATION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Write-Host "[5/8] Rendering all editable documents with WPS..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
}

if ($SkipPageRaster) {
    Write-Host "[6/8] Reusing existing WPS page PNGs."
}
else {
    Write-Host "[6/8] Rasterizing every WPS page for visual review..."
    foreach ($Job in $Jobs) {
        $OutputDirectory = (Resolve-Path -LiteralPath (Split-Path -Parent $Job.Output)).Path
        if (-not $OutputDirectory.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean a render directory outside the Gate C8B package: $OutputDirectory"
        }
        Get-ChildItem -LiteralPath $OutputDirectory -File | Where-Object {
            $_.Name -match '^(page|review-page|final-page)-.*\.png$' -or $_.Name -match '^.*contact_sheet.*\.png$'
        } | Remove-Item -Force
        & $PdfToPpm -r 150 -png $Job.Output (Join-Path $OutputDirectory "final-page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[7/8] Auditing DOCX accessibility..."
foreach ($Job in $Jobs) {
    & $BundledPython $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[8/8] Running the Gate C8B technical and deterministic-package audit..."
& $BundledPython (Join-Path $PSScriptRoot "phase17_c8b_04_final_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8B audit failed." }

Write-Host "Gate C8B editorial preflight package rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8B_editorial_preflight_2026-08-21.zip")
