# Downloads harmonised European-ancestry SLE GWAS summary statistics.
#
# Run from the project root:
#   powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_sle_gwas_gcst005831.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OutDir = Join-Path $ProjectRoot "Data\external_regulatory\GCST005831"
$BaseUrl = "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST005001-GCST006000/GCST005831/harmonised"
$MainName = "29848360-GCST005831-EFO_0002690.h.tsv.gz"
$MetaName = "29848360-GCST005831-EFO_0002690.h.tsv.gz-meta.yaml"
$MainBytes = 203551020
$MetaBytes = 825
$MainMd5 = "0bb1eae184403f922d9f1bde296c75a8"

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "curl.exe was not found."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Files = @(
    @{Name = $MainName; ExpectedBytes = $MainBytes},
    @{Name = $MetaName; ExpectedBytes = $MetaBytes}
)

foreach ($FileSpec in $Files) {
    $OutFile = Join-Path $OutDir $FileSpec.Name
    $DownloadRequired = $true

    if (Test-Path -LiteralPath $OutFile) {
        $ExistingBytes = (Get-Item -LiteralPath $OutFile).Length
        if ($ExistingBytes -gt $FileSpec.ExpectedBytes) {
            throw "Existing file is larger than expected: $OutFile. Remove the corrupted file and rerun."
        }
        if ($ExistingBytes -eq $FileSpec.ExpectedBytes) {
            $DownloadRequired = $false
        }
    }

    Write-Host ""
    if ($DownloadRequired) {
        Write-Host "Downloading: $($FileSpec.Name)"
        curl.exe --fail --location --continue-at - --retry 20 --retry-all-errors `
            --retry-delay 10 --connect-timeout 60 --output "$OutFile" `
            "$BaseUrl/$($FileSpec.Name)"
    } else {
        Write-Host "Already complete by size; verifying: $($FileSpec.Name)"
    }

    $ActualBytes = (Get-Item -LiteralPath $OutFile).Length
    if ($ActualBytes -ne $FileSpec.ExpectedBytes) {
        throw "Size mismatch for $($FileSpec.Name). Expected $($FileSpec.ExpectedBytes), got $ActualBytes."
    }
    Write-Host "Verified size: $($FileSpec.Name) ($ActualBytes bytes)"
}

$MainFile = Join-Path $OutDir $MainName
$ActualMd5 = (Get-FileHash -LiteralPath $MainFile -Algorithm MD5).Hash.ToLowerInvariant()
if ($ActualMd5 -ne $MainMd5) {
    throw "MD5 mismatch for $MainName. Expected $MainMd5, got $ActualMd5."
}
$Sha256 = (Get-FileHash -LiteralPath $MainFile -Algorithm SHA256).Hash.ToLowerInvariant()

[PSCustomObject]@{
    accession = "GCST005831"
    trait = "Systemic lupus erythematosus"
    pmid = "29848360"
    ancestry = "European"
    cases = 4943
    controls = 8483
    reported_variant_count = 7110321
    harmonised_build = "GRCh38"
    source = "NHGRI-EBI GWAS Catalog"
    source_url = $BaseUrl
    downloaded_at = (Get-Date).ToString("s")
    expected_bytes = $MainBytes
    official_md5 = $MainMd5
    sha256 = $Sha256
    primary_file = $MainFile
} | Export-Csv -LiteralPath (Join-Path $OutDir "download_manifest_gcst005831.csv") `
    -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "GCST005831 passed exact-size and official MD5 checks; SHA-256 recorded."
Write-Host "Output directory: $OutDir"
