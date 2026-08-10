param(
    [string]$OutDir = "Data\processed\GSE163121_bcell_validation\source"
)

$ErrorActionPreference = "Stop"

function Download-WithResume {
    param(
        [string]$Url,
        [string]$OutFile,
        [long]$ExpectedBytes = 0
    )

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutFile) | Out-Null
    Write-Host "Downloading:" $Url
    Write-Host "To:" (Resolve-Path -LiteralPath (Split-Path -Parent $OutFile)).Path
    curl.exe -L --fail --retry 5 --retry-delay 5 -C - -o $OutFile $Url

    if ($ExpectedBytes -gt 0) {
        $actual = (Get-Item -LiteralPath $OutFile).Length
        if ($actual -ne $ExpectedBytes) {
            throw "Downloaded file size mismatch for $OutFile. Expected $ExpectedBytes bytes, got $actual bytes."
        }
    }
}

$rawUrl = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE163nnn/GSE163121/suppl/GSE163121_RAW.tar"
$matrixUrl = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE163nnn/GSE163121/matrix/GSE163121_series_matrix.txt.gz"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Download-WithResume -Url $matrixUrl -OutFile (Join-Path $OutDir "GSE163121_series_matrix.txt.gz") -ExpectedBytes 2213
Download-WithResume -Url $rawUrl -OutFile (Join-Path $OutDir "GSE163121_RAW.tar") -ExpectedBytes 95979520

Write-Host ""
Write-Host "GSE163121 B-cell validation source download complete."
Write-Host "Next:"
Write-Host "  python .\02_analysis\scripts\27_inspect_gse163121_validation.py"
