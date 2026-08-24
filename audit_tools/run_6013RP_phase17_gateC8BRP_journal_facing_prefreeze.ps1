param(
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
$RunDir = Join-Path $Root "phase17_v7\gateC8BRP\20260825_journal_facing_prefreeze"
$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25"
$EnvironmentFile = Join-Path $PSScriptRoot "environment_gateC8BR_release_2026-08-25.yml"
$ExplicitSpec = Join-Path $PSScriptRoot "environment_gateC8BR_release_explicit_win64_2026-08-25.txt"
$RenderScript = Join-Path $PSScriptRoot "render_docx_with_wps.ps1"
$A11yAudit = Join-Path $PSScriptRoot "docx_a11y_audit.py"

function Get-CondaExecutable {
    $command = Get-Command conda -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    $candidates = @(
        (Join-Path $env:ProgramData "miniforge3\condabin\conda.bat"),
        (Join-Path $env:USERPROFILE "miniforge3\condabin\conda.bat"),
        (Join-Path $env:USERPROFILE "mambaforge\condabin\conda.bat"),
        (Join-Path $env:USERPROFILE "anaconda3\condabin\conda.bat")
    )
    return $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

function Get-NamedEnvironmentPython {
    $conda = Get-CondaExecutable
    if (-not $conda) { return $null }
    try {
        $payload = (& $conda env list --json | ConvertFrom-Json)
        foreach ($environmentPath in $payload.envs) {
            if ((Split-Path -Leaf $environmentPath) -eq "sle-bcell-c8br-release") {
                $python = Join-Path $environmentPath "python.exe"
                if (Test-Path -LiteralPath $python) { return $python }
            }
        }
    }
    catch { return $null }
    return $null
}

function Test-ReleasePython([string]$Path) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) { return $false }
    & $Path -c "import matplotlib,numpy,pandas,PIL,docx,pypdf" 2>$null
    return $LASTEXITCODE -eq 0
}

function Resolve-ReleasePython {
    $candidates = @()
    if ($ReleasePython) { $candidates += $ReleasePython }
    if ($env:SLE_BCELL_RELEASE_PYTHON) { $candidates += $env:SLE_BCELL_RELEASE_PYTHON }
    $named = Get-NamedEnvironmentPython
    if ($named) { $candidates += $named }
    $repoEnvironment = Join-Path $Root ".conda\envs\sle-bcell-c8br-release\python.exe"
    if (Test-Path -LiteralPath $repoEnvironment) { $candidates += $repoEnvironment }
    $candidates += (Get-Command python -All -ErrorAction SilentlyContinue | ForEach-Object { $_.Source })
    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-ReleasePython $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    throw @"
No qualified journal-release Python was found.
Create the pinned environment, then rerun:
  powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\00_create_gateC8BR_release_env.ps1"
Or pass -ReleasePython / set SLE_BCELL_RELEASE_PYTHON to a Python matching:
  $EnvironmentFile
"@
}

function Resolve-PdfToPpm {
    if ($PdfToPpm -and (Test-Path -LiteralPath $PdfToPpm)) { return (Resolve-Path -LiteralPath $PdfToPpm).Path }
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
    throw "pdftoppm was not found. Pass -PdfToPpm, set SLE_BCELL_PDFTOPPM, or add Poppler/MiKTeX to PATH."
}

foreach ($required in @($EnvironmentFile, $ExplicitSpec, $RenderScript, $A11yAudit)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required repository file not found: $required" }
}

$Python = Resolve-ReleasePython
Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
Write-Host "Release Python: $Python"

if ($SkipRuntimeSmokeTest) {
    Write-Host "[1/8] Reusing release-runtime qualification."
}
else {
    Write-Host "[1/8] Qualifying pinned imports and PNG/PDF/DOCX output..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8br_00_release_smoke_test.py") --output-dir (Join-Path $RunDir "_runtime_smoke")
    if ($LASTEXITCODE -ne 0) { throw "Release-runtime qualification failed." }
}

if ($SkipMainFigureBuild) {
    Write-Host "[2/8] Reusing journal-facing main figures."
}
else {
    Write-Host "[2/8] Rebuilding Figures 1, 4 and 5 from frozen tables; carrying Figures 2 and 3..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8brp_00_build_main_figures.py")
    if ($LASTEXITCODE -ne 0) { throw "Journal-facing figure build failed." }
}

Write-Host "[3/8] Building manuscript v15, journal-facing Supplement v6 and release sources..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brp_01_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Journal-facing source build failed." }

Write-Host "[4/8] Building editable DOCX files, package assets and clean portal aliases..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brp_02_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Journal-facing document build failed." }

if ($Mode -eq "PortableCore") {
    $status = @{
        created_at = "2026-08-25"
        status = "PASS_GATE_C8BRP_PORTABLE_CORE_BUILT"
        release_python = $Python
        submission_render_qa_completed = $false
        portal_submission_authorized = $false
        next_action = "Run -Mode Full on a Windows workstation with WPS and pdftoppm after author review."
    } | ConvertTo-Json -Depth 4
    Set-Content -LiteralPath (Join-Path $RunDir "04B_GATE_C8BRP_PORTABLE_CORE_STATUS.json") -Value $status -Encoding utf8
    Write-Host "Portable core completed. Full WPS/render QA remains required."
    exit 0
}

$PdfRasterizer = Resolve-PdfToPpm
$Jobs = @(
    @{
        Name = "main_text"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_AUTHOR_COMPLETION_REQUIRED.docx"
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
        Name = "cover_letter"
        Input = Join-Path $Package "submission_docs\Cover_Letter_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Cover_Letter_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Write-Host "[5/8] Rendering editable documents with WPS..."
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
        $outputDirectory = (Resolve-Path -LiteralPath (Split-Path -Parent $Job.Output)).Path
        if (-not $outputDirectory.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean a render directory outside the journal-facing package: $outputDirectory"
        }
        Get-ChildItem -LiteralPath $outputDirectory -File | Where-Object {
            $_.Name -match '^(page|review-page|final-page)-.*\.png$' -or $_.Name -match '^.*contact_sheet.*\.png$'
        } | Remove-Item -Force
        & $PdfRasterizer -r 150 -png $Job.Output (Join-Path $outputDirectory "final-page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[7/8] Running the repository-portable DOCX accessibility audit..."
foreach ($Job in $Jobs) {
    & $Python $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[8/8] Running scientific-boundary, alias and deterministic-package audit..."
& $Python (Join-Path $PSScriptRoot "phase17_c8brp_03_final_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final journal-facing prefreeze audit failed." }

Write-Host "Journal-facing C8BR prefreeze rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25.zip")
