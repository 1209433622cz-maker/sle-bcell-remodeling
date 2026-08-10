# Downloads the CELLxGENE/HCA H5AD for Perez/GSE174188.
# This is the cleanest public processed-data route, but the file is large (~12.2 GB).
#
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_perez_gse174188_cellxgene.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OutDir = Join-Path $ProjectRoot "Data\processed\GSE174188_perez_cellxgene"
$OutFile = Join-Path $OutDir "perez_gse174188_cellxgene.h5ad"
$Manifest = Join-Path $OutDir "download_manifest_cellxgene.csv"

$CollectionId = "436154da-bcf1-4130-9c8b-120ff9a888f2"
$DatasetId = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
$Url = "https://datasets.cellxgene.cziscience.com/c55dc602-d168-4d15-acc1-5de4f2f5d551.h5ad"
$ExpectedBytes = 12218105530

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

[PSCustomObject]@{
    source = "CELLxGENE / HCA"
    collection_id = $CollectionId
    dataset_id = $DatasetId
    url = $Url
    expected_bytes = $ExpectedBytes
    output_file = $OutFile
    download_date = (Get-Date).ToString("s")
} | Export-Csv -LiteralPath $Manifest -NoTypeInformation -Encoding UTF8

Write-Host "Downloading CELLxGENE H5AD to:"
Write-Host "  $OutFile"
Write-Host "Expected size: $ExpectedBytes bytes (~12.2 GB)"
Write-Host ""

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "curl.exe was not found. Install curl or replace the download command with Invoke-WebRequest."
}

$MaxAttempts = 50
$Attempt = 0
$LastBytes = -1

while ($Attempt -lt $MaxAttempts) {
    $Attempt += 1
    $CurrentBytes = 0
    if (Test-Path -LiteralPath $OutFile) {
        $CurrentBytes = (Get-Item -LiteralPath $OutFile).Length
    }

    if ($CurrentBytes -eq $ExpectedBytes) {
        break
    }
    if ($CurrentBytes -gt $ExpectedBytes) {
        throw "Existing file is larger than expected. Delete it manually and rerun: $OutFile"
    }

    $Percent = [math]::Round(($CurrentBytes / $ExpectedBytes) * 100, 2)
    Write-Host ""
    Write-Host "Attempt $Attempt / $MaxAttempts"
    Write-Host "Current size: $CurrentBytes / $ExpectedBytes bytes ($Percent%)"
    Write-Host "Resuming download..."

    curl.exe --fail --location --continue-at - --retry 20 --retry-delay 15 --connect-timeout 60 --output "$OutFile" "$Url"

    $NewBytes = 0
    if (Test-Path -LiteralPath $OutFile) {
        $NewBytes = (Get-Item -LiteralPath $OutFile).Length
    }

    if ($NewBytes -eq $ExpectedBytes) {
        break
    }

    if ($NewBytes -le $LastBytes) {
        Write-Host "No progress detected in this attempt. Waiting before retry..."
        Start-Sleep -Seconds 30
    }

    $LastBytes = $NewBytes
}

$ActualBytes = (Get-Item -LiteralPath $OutFile).Length
if ($ActualBytes -ne $ExpectedBytes) {
    throw "Downloaded file size mismatch after $MaxAttempts attempts. Expected $ExpectedBytes bytes, got $ActualBytes bytes. Rerun this script to continue from the partial file."
}

Write-Host "Download size check passed."
Write-Host "File ready: $OutFile"
