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
$InternalBuilder = Join-Path $PSScriptRoot "run_6013RP_phase17_gateC8BRF_author_release.ps1"
if (-not (Test-Path -LiteralPath $InternalBuilder)) {
    throw "Internal submission builder not found: $InternalBuilder"
}

$Arguments = @{
    Doi = $Doi
    Mode = $Mode
}
if ($ReleasePython) { $Arguments.ReleasePython = $ReleasePython }
if ($PdfToPpm) { $Arguments.PdfToPpm = $PdfToPpm }
if ($SkipMainFigureBuild) { $Arguments.SkipMainFigureBuild = $true }
if ($SkipPageRaster) { $Arguments.SkipPageRaster = $true }
if ($SkipRuntimeSmokeTest) { $Arguments.SkipRuntimeSmokeTest = $true }

& $InternalBuilder @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Submission package build failed."
}
