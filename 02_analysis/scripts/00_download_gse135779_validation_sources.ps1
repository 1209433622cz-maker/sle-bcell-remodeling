param(
    [string]$OutDir = "Data\processed\GSE135779_nehar_validation\source",
    [switch]$DownloadRaw
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
    curl.exe -L --fail --retry 5 --retry-delay 5 -C - -o $OutFile $Url

    if ($ExpectedBytes -gt 0) {
        $actual = (Get-Item -LiteralPath $OutFile).Length
        if ($actual -ne $ExpectedBytes) {
            throw "Downloaded file size mismatch for $OutFile. Expected $ExpectedBytes bytes, got $actual bytes."
        }
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$downloads = @(
    @{
        Url = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/matrix/GSE135779_series_matrix.txt.gz"
        File = "GSE135779_series_matrix.txt.gz"
        Bytes = 5465
    },
    @{
        Url = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_genes.tsv.gz"
        File = "GSE135779_genes.tsv.gz"
        Bytes = 257271
    },
    @{
        Url = "https://raw.githubusercontent.com/dnehar/SingleCells_SLE_paper/master/Meta_cSLE_processed_0809202_small.csv"
        File = "Meta_cSLE_processed_0809202_small.csv"
        Bytes = 20902801
    },
    @{
        Url = "https://raw.githubusercontent.com/dnehar/SingleCells_SLE_paper/master/Meta_caSLE_processed_08092021_small.csv"
        File = "Meta_caSLE_processed_08092021_small.csv"
        Bytes = 22285464
    },
    @{
        Url = "https://raw.githubusercontent.com/dnehar/SingleCells_SLE_paper/master/libaries.csv"
        File = "libaries.csv"
        Bytes = 540
    }
)

foreach ($download in $downloads) {
    Download-WithResume -Url $download.Url -OutFile (Join-Path $OutDir $download.File) -ExpectedBytes $download.Bytes
}

if ($DownloadRaw) {
    Download-WithResume `
        -Url "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_RAW.tar" `
        -OutFile (Join-Path $OutDir "GSE135779_RAW.tar") `
        -ExpectedBytes 1299783680
} else {
    Write-Host ""
    Write-Host "Skipped GSE135779_RAW.tar by default because it is 1.30 GB."
    Write-Host "To download it later, run:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_gse135779_validation_sources.ps1 -DownloadRaw"
}

Write-Host ""
Write-Host "GSE135779 validation metadata/source download step complete."
