param(
    [string]$OutDir = "Data\processed\GSE196830_onek1k_cellxgene\source"
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
    Write-Host "To:" $OutFile
    curl.exe -L --fail --retry 5 --retry-delay 5 -C - -o $OutFile $Url

    if ($ExpectedBytes -gt 0) {
        $actual = (Get-Item -LiteralPath $OutFile).Length
        if ($actual -ne $ExpectedBytes) {
            throw "Downloaded file size mismatch for $OutFile. Expected $ExpectedBytes bytes, got $actual bytes."
        }
    }
}

$collectionUrl = "https://api.cellxgene.cziscience.com/curation/v1/collections/dde06e0f-ab3b-46be-96a2-a8082383c4a1"
$h5adUrl = "https://datasets.cellxgene.cziscience.com/1e44db10-b572-46cc-adae-dcc7acd44ca6.h5ad"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Download-WithResume `
    -Url $collectionUrl `
    -OutFile (Join-Path $OutDir "cellxgene_collection_onek1k_gse196830.json") `
    -ExpectedBytes 22062

Download-WithResume `
    -Url $h5adUrl `
    -OutFile (Join-Path $OutDir "onek1k_gse196830_cellxgene.h5ad") `
    -ExpectedBytes 4434273970

Write-Host ""
Write-Host "OneK1K/GSE196830 CELLxGENE download complete."
Write-Host "Next:"
Write-Host "  conda run -n sle-bcell python .\02_analysis\scripts\31_inspect_onek1k_cellxgene.py"
