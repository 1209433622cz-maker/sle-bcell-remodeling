param(
    [string]$ReleasePython = "",
    [string]$PdfToPpm = "",
    [ValidateSet("Full", "PortableCore")]
    [string]$Mode = "Full",
    [switch]$SkipReferenceVerification,
    [switch]$SkipMainFigureBuild,
    [switch]$SkipPageRaster,
    [switch]$SkipRuntimeSmokeTest
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunDir = Join-Path $Root "phase17_v7\gateC8BR\20260825_release_portability_preflight"
$Package = Join-Path $Root "04_submission\package_genome_medicine_gateC8BR_release_portability_preflight_2026-08-25"
$EnvironmentFile = Join-Path $PSScriptRoot "environment_gateC8BR_release_2026-08-25.yml"
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
No qualified Gate C8BR release Python was found.
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

foreach ($required in @($EnvironmentFile, $RenderScript, $A11yAudit)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required repository file not found: $required" }
}

$Python = Resolve-ReleasePython
Set-Location -LiteralPath $Root
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null
Write-Host "Release Python: $Python"

if ($SkipRuntimeSmokeTest) {
    Write-Host "[1/9] Reusing Gate C8BR runtime qualification."
}
else {
    Write-Host "[1/9] Qualifying pinned imports, PNG/PDF savefig and DOCX creation..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8br_00_release_smoke_test.py") --output-dir (Join-Path $RunDir "_runtime_smoke")
    if ($LASTEXITCODE -ne 0) { throw "Release-runtime qualification failed." }
}

if ($SkipReferenceVerification) {
    Write-Host "[2/9] Reusing Gate C8BR reference verification."
}
else {
    Write-Host "[2/9] Verifying 28 DOI records, including Sayadi and Faheem 2026..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8br_01_verify_references.py")
    if ($LASTEXITCODE -ne 0) { throw "Reference verification failed." }
}

if ($SkipMainFigureBuild) {
    Write-Host "[3/9] Reusing Gate C8BR main figures."
}
else {
    Write-Host "[3/9] Rebuilding Figure 5 with parallel evidence branches and carrying frozen Figures 1-4..."
    & $Python (Join-Path $PSScriptRoot "phase17_c8br_00_build_main_figures.py")
    if ($LASTEXITCODE -ne 0) { throw "Main-figure build failed." }
}

Write-Host "[4/9] Building v14 manuscript, supplement and author-completion sources..."
& $Python (Join-Path $PSScriptRoot "phase17_c8br_02_build_submission_sources.py")
if ($LASTEXITCODE -ne 0) { throw "Submission-source build failed." }

Write-Host "[5/9] Building editable DOCX files and package assets..."
& $Python (Join-Path $PSScriptRoot "phase17_c8br_03_build_documents.py")
if ($LASTEXITCODE -ne 0) { throw "Document build failed." }

if ($Mode -eq "PortableCore") {
    $status = @{
        created_at = "2026-08-25"
        status = "PASS_GATE_C8BR_PORTABLE_CORE_BUILT"
        release_python = $Python
        submission_render_qa_completed = $false
        next_action = "Run the same command with -Mode Full on a Windows workstation with WPS and pdftoppm."
    } | ConvertTo-Json -Depth 4
    Set-Content -LiteralPath (Join-Path $RunDir "04B_GATE_C8BR_PORTABLE_CORE_STATUS.json") -Value $status -Encoding utf8
    Write-Host "Portable core completed. Full WPS/render QA was intentionally skipped."
    exit 0
}

$PdfRasterizer = Resolve-PdfToPpm
$Jobs = @(
    @{
        Name = "main_text"
        Input = Join-Path $Package "main_text\Genome_Medicine_Manuscript_GateC8BR_AUTHOR_COMPLETION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_main\Genome_Medicine_Manuscript_GateC8BR_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\main_text_a11y.json"
    },
    @{
        Name = "supplement"
        Input = Join-Path $Package "additional_files\Additional_file_1_Supplementary_Information_GateC8BR.docx"
        Output = Join-Path $Package "internal_qc\wps_render_supplement\Additional_file_1_Supplementary_Information_GateC8BR_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\supplement_a11y.json"
    },
    @{
        Name = "cover_letter"
        Input = Join-Path $Package "submission_docs\Genome_Medicine_Cover_Letter_GateC8BR_AUTHOR_CONFIRMATION_REQUIRED.docx"
        Output = Join-Path $Package "internal_qc\wps_render_cover_letter\Genome_Medicine_Cover_Letter_GateC8BR_AUTHOR_COMPLETION_REQUIRED_WPS.pdf"
        A11y = Join-Path $Package "internal_qc\cover_letter_a11y.json"
    }
)

Write-Host "[6/9] Rendering editable documents with WPS..."
foreach ($Job in $Jobs) {
    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -ExecutionPolicy Bypass -File $RenderScript -InputDocx $Job.Input -OutputPdf $Job.Output
    if ($LASTEXITCODE -ne 0) { throw "WPS rendering failed for $($Job.Input)." }
}

if ($SkipPageRaster) {
    Write-Host "[7/9] Reusing existing WPS page PNGs."
}
else {
    Write-Host "[7/9] Rasterizing every WPS page for visual review..."
    foreach ($Job in $Jobs) {
        $outputDirectory = (Resolve-Path -LiteralPath (Split-Path -Parent $Job.Output)).Path
        if (-not $outputDirectory.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean a render directory outside the Gate C8BR package: $outputDirectory"
        }
        Get-ChildItem -LiteralPath $outputDirectory -File | Where-Object {
            $_.Name -match '^(page|review-page|final-page)-.*\.png$' -or $_.Name -match '^.*contact_sheet.*\.png$'
        } | Remove-Item -Force
        & $PdfRasterizer -r 150 -png $Job.Output (Join-Path $outputDirectory "final-page")
        if ($LASTEXITCODE -ne 0) { throw "PDF page rasterization failed for $($Job.Output)." }
    }
}

Write-Host "[8/9] Running the repository-portable DOCX accessibility audit..."
foreach ($Job in $Jobs) {
    & $Python $A11yAudit $Job.Input --out_json $Job.A11y
    if ($LASTEXITCODE -ne 0) { throw "Accessibility audit failed for $($Job.Input)." }
}

Write-Host "[9/9] Running the Gate C8BR scientific-boundary and deterministic-package audit..."
& $Python (Join-Path $PSScriptRoot "phase17_c8br_04_final_audit.py")
if ($LASTEXITCODE -ne 0) { throw "Final Gate C8BR audit failed." }

Write-Host "Gate C8BR release-portability preflight rebuilt successfully:"
Write-Host (Join-Path $Root "04_submission\package_genome_medicine_gateC8BR_release_portability_preflight_2026-08-25.zip")
