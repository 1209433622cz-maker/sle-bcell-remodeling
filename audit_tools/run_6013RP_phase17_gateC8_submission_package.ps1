param(
    [switch]$SkipReferenceRefresh,
    [switch]$SkipPageRaster
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$BundledPdfToPpm = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe"
$Python = if (Test-Path -LiteralPath $BundledPython) { $BundledPython } else { "python" }

$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8_2026-08-20"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"
$Jobs = @(
    @{
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_GateC8_AUTHOR_COMPLETION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_GateC8_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
    },
    @{
        Input = Join-Path $Package "additional_files\Additional_file_1_Supplementary_Information_GateC8.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Additional_file_1_Supplementary_Information_GateC8_WPS.pdf"
    },
    @{
        Input = Join-Path $Package "submission_docs\Genome_Medicine_Cover_Letter_GateC8_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Genome_Medicine_Cover_Letter_GateC8_AUTHOR_CONFIRMATION_REQUIRED_WPS.pdf"
    }
)

Set-Location -LiteralPath $Root

if (-not $SkipReferenceRefresh) {
    Write-Host "[1/5] Refreshing DOI metadata from Crossref..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8_01_verify_references.py")
    if ($LASTEXITCODE -ne 0) { throw "Reference verification failed." }
}
else {
    Write-Host "[1/5] Reusing the frozen Gate C8 reference verification."
}

Write-Host "[2/5] Rebuilding journal-specific Markdown sources..."
& $Python (Join-Path $PSScriptRoot "phase17_c8_02_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Submission source build failed." }

Write-Host "[3/5] Rebuilding editable DOCX files and package assets..."
& $Python (Join-Path $PSScriptRoot "phase17_c8_03_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Document build failed." }

Write-Host "[4/5] Rendering all editable documents with the WPS COM backend..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
    if (-not $SkipPageRaster) {
        if (-not (Test-Path -LiteralPath $BundledPdfToPpm)) {
            throw "Bundled pdftoppm was not found. Re-run with -SkipPageRaster only if page PNGs already exist."
        }
        $OutputDirectory = Split-Path -Parent $Job.Output
        Get-ChildItem -LiteralPath $OutputDirectory -Filter "page-*.png" -ErrorAction SilentlyContinue | Remove-Item -Force
        & $BundledPdfToPpm -r 150 -png $Job.Output (Join-Path $OutputDirectory "page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[5/5] Running the final scientific, technical and packaging audit..."
& $Python (Join-Path $PSScriptRoot "phase17_c8_04_final_submission_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8 audit failed." }

Write-Host "Gate C8 package rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8_2026-08-20.zip")
