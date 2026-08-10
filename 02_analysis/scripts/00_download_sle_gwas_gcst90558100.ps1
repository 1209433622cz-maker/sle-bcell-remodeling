# Downloads harmonised SLE GWAS summary statistics from the NHGRI-EBI GWAS Catalog.
#
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_sle_gwas_gcst90558100.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OutDir = Join-Path $ProjectRoot "Data\external_regulatory\GCST90558100"
$BaseUrl = "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST90558001-GCST90559000/GCST90558100/harmonised"

$Files = @(
    @{
        Name = "GCST90558100.h.tsv.gz"
        ExpectedBytes = 48066859
        ExpectedMd5 = "4418c5ca1a5cd78b8210fbb475dd896b"
    },
    @{
        Name = "GCST90558100.h.tsv.gz.tbi"
        ExpectedBytes = 1419473
        ExpectedMd5 = "84365f7e5903f0c1533781de23a9eba4"
    },
    @{
        Name = "GCST90558100.h.tsv.gz-meta.yaml"
        ExpectedBytes = 963
        ExpectedMd5 = $null
    },
    @{
        Name = "md5sum.txt"
        ExpectedBytes = 116
        ExpectedMd5 = $null
    }
)

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "curl.exe was not found."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

foreach ($FileSpec in $Files) {
    $Name = $FileSpec.Name
    $OutFile = Join-Path $OutDir $Name
    $Url = "$BaseUrl/$Name"
    $DownloadRequired = $true

    if (Test-Path -LiteralPath $OutFile) {
        $ExistingBytes = (Get-Item -LiteralPath $OutFile).Length
        if ($ExistingBytes -gt $FileSpec.ExpectedBytes) {
            throw "Existing file is larger than expected: $OutFile. Remove this corrupted file and rerun."
        }
        if ($ExistingBytes -eq $FileSpec.ExpectedBytes) {
            $DownloadRequired = $false
        }
    }

    Write-Host ""
    if ($DownloadRequired) {
        Write-Host "Downloading: $Name"
        curl.exe --fail --location --continue-at - --retry 20 --retry-all-errors `
            --retry-delay 10 --connect-timeout 60 --output "$OutFile" "$Url"
    } else {
        Write-Host "Already complete by size; verifying: $Name"
    }

    if (-not (Test-Path -LiteralPath $OutFile)) {
        throw "Download did not create the expected file: $OutFile"
    }

    $ActualBytes = (Get-Item -LiteralPath $OutFile).Length
    if ($ActualBytes -ne $FileSpec.ExpectedBytes) {
        throw "Size mismatch for $Name. Expected $($FileSpec.ExpectedBytes), got $ActualBytes. Rerun to resume."
    }

    if ($FileSpec.ExpectedMd5) {
        $ActualMd5 = (Get-FileHash -LiteralPath $OutFile -Algorithm MD5).Hash.ToLowerInvariant()
        if ($ActualMd5 -ne $FileSpec.ExpectedMd5) {
            throw "MD5 mismatch for $Name. Expected $($FileSpec.ExpectedMd5), got $ActualMd5."
        }
    }

    Write-Host "Verified: $Name ($ActualBytes bytes)"
}

$Manifest = Join-Path $OutDir "download_manifest_gcst90558100.csv"
[PSCustomObject]@{
    accession = "GCST90558100"
    trait = "Systemic lupus erythematosus"
    pmid = "40262193"
    ancestry = "European"
    cases = 6547
    controls = 648130
    genome_build = "GRCh38"
    harmonised = $true
    source = "NHGRI-EBI GWAS Catalog"
    source_url = $BaseUrl
    downloaded_at = (Get-Date).ToString("s")
    primary_file = (Join-Path $OutDir "GCST90558100.h.tsv.gz")
} | Export-Csv -LiteralPath $Manifest -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "All GCST90558100 files passed size and MD5 checks."
Write-Host "Output directory: $OutDir"
