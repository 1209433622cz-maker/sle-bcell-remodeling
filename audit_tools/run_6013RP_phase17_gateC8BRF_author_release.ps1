param(
    [Parameter(Mandatory = $true)]
    [string]$Doi,
    [string]$ReleasePython = "",
    [string]$PdfToPpm = "",
    [ValidateSet("Full", "PortableCore")]
    [string]$Mode = "Full",
    [switch]$SkipMainFigureBuild,
    [switch]$SkipPageRaster,
    [switch]$SkipRuntimeSmokeTest
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root "phase17_v7\gateC8BRF\20260825_author_release"
$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8BRF_author_release_2026-08-25"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"
$A11yAudit = Join-Path $PSScriptRoot "docx_a11y_audit.py"
$ContactSheets = Join-Path $PSScriptRoot "build_page_contact_sheets.py"

function Test-ReleasePython([string]$Path) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return $false }
    & $Path -c "import matplotlib,numpy,pandas,PIL,docx,pypdf" 2>$null
    return $LASTEXITCODE -eq 0
}

function Resolve-ReleasePython {
    $candidates = @()
    if ($ReleasePython) { $candidates += $ReleasePython }
    if ($env:SLE_BCELL_RELEASE_PYTHON) { $candidates += $env:SLE_BCELL_RELEASE_PYTHON }
    $candidates += (Join-Path $env:ProgramData "miniforge3\envs\sle-bcell-c8br-release\python.exe")
    $candidates += (Join-Path $Root ".conda\envs\sle-bcell-c8br-release\python.exe")
    $candidates += (Get-Command python -All -ErrorAction SilentlyContinue | ForEach-Object { $_.Source })
    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-ReleasePython $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    throw "No qualified sle-bcell-c8br-release Python was found. Run audit_tools\00_create_gateC8BR_release_env.ps1 or pass -ReleasePython."
}

function Resolve-PdfToPpm {
    if ($PdfToPpm -and (Test-Path -LiteralPath $PdfToPpm)) {
        return (Resolve-Path -LiteralPath $PdfToPpm).Path
    }
    if ($env:SLE_BCELL_PDFTOPPM -and (Test-Path -LiteralPath $env:SLE_BCELL_PDFTOPPM)) {
        return (Resolve-Path -LiteralPath $env:SLE_BCELL_PDFTOPPM).Path
    }
    $command = Get-Command pdftoppm -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    $candidates = @(
        (Join-Path $env:ProgramFiles "MiKTeX\miktex\bin\x64\pdftoppm.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64\pdftoppm.exe")
    )
    $resolved = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($resolved) { return (Resolve-Path -LiteralPath $resolved).Path }
    throw "pdftoppm was not found. Pass -PdfToPpm or install Poppler/MiKTeX."
}

foreach ($required in @($RenderScript, $A11yAudit, $ContactSheets)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required file not found: $required" }
}
if ($Doi -notmatch '^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$') {
    throw "-Doi must be a DOI such as 10.5281/zenodo.12345678"
}

$Python = Resolve-ReleasePython
Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
Write-Host "Release Python: $Python"
Write-Host "Release DOI: $Doi"

if ($SkipRuntimeSmokeTest) {
    Write-Host "[1/9] Reusing release-runtime qualification."
}
else {
    Write-Host "[1/9] Qualifying pinned PNG/PDF/DOCX runtime..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8br_00_release_smoke_test.py") --output-dir (Join-Path $RunDir "_runtime_smoke")
    if ($LASTEXITCODE -ne 0) { throw "Release-runtime qualification failed." }
}

if ($SkipMainFigureBuild) {
    Write-Host "[2/9] Reusing final 170-mm main figures."
}
else {
    Write-Host "[2/9] Rebuilding all five main figures at 170 mm..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8brf_00_build_main_figures.py")
    if ($LASTEXITCODE -ne 0) { throw "Final main-figure build failed." }
}

Write-Host "[3/9] Auditing Figure 2 public UUID provenance and privacy..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brf_01_uuid_governance.py")
if ($LASTEXITCODE -ne 0) { throw "Figure 2 UUID governance audit failed." }

Write-Host "[4/9] Building DOI-complete author-approved sources..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brf_02_build_submission_sources.py") --doi $Doi
if ($LASTEXITCODE -ne 0) { throw "Final source build failed." }

Write-Host "[5/9] Building editable DOCX files and REQUIRED/OPTIONAL portal maps..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brf_03_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Final document build failed." }

if ($Mode -eq "PortableCore") {
    $status = @{
        created_at = "2026-08-25"
        status = "PASS_GATE_C8BRF_PORTABLE_CORE_BUILT"
        doi = $Doi
        release_python = $Python
        submission_render_qa_completed = $false
        next_action = "Run -Mode Full on Windows with WPS and pdftoppm before release."
    } | ConvertTo-Json -Depth 4
    Set-Content -LiteralPath (Join-Path $RunDir "05B_PORTABLE_CORE_STATUS.json") -Value $status -Encoding utf8
    Write-Host "Portable core completed; full WPS/render QA remains required."
    exit 0
}

$PdfRasterizer = Resolve-PdfToPpm
$Jobs = @(
    @{
        Name = "main"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\main_text_a11y.json"
    },
    @{
        Name = "supplement"
        Input = Join-Path $Package "additional_files\Supplementary_Information.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Supplementary_Information_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\supplement_a11y.json"
    },
    @{
        Name = "cover"
        Input = Join-Path $Package "submission_docs\Cover_Letter.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Cover_Letter_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Write-Host "[6/9] Rendering all final documents with WPS..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
}

if ($SkipPageRaster) {
    Write-Host "[7/9] Reusing existing page PNGs."
}
else {
    Write-Host "[7/9] Rasterizing every WPS page and building review contact sheets..."
    foreach ($Job in $Jobs) {
        $outputDirectory = (Resolve-Path -LiteralPath (Split-Path -Parent $Job.Output)).Path
        if (-not $outputDirectory.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean a render directory outside the final package: $outputDirectory"
        }
        Get-ChildItem -LiteralPath $outputDirectory -File | Where-Object {
            $_.Name -match '^(page|review-page|final-page)-.*\.png$' -or $_.Name -match '^contact_sheet_.*\.png$'
        } | Remove-Item -Force
        & $PdfRasterizer -r 150 -png $Job.Output (Join-Path $outputDirectory "final-page")
        if ($LASTEXITCODE -ne 0) { throw "PDF rasterization failed for $($Job.Output)." }
        & $Python $ContactSheets $outputDirectory --label $Job.Name
        if ($LASTEXITCODE -ne 0) { throw "Contact-sheet build failed for $($Job.Name)." }
    }
}

Write-Host "[8/9] Running DOCX accessibility audits..."
foreach ($Job in $Jobs) {
    & $Python $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[9/9] Running final author-release and deterministic-package audit..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brf_04_final_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8BRF audit failed." }

Write-Host "Gate C8BRF author release rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip")
