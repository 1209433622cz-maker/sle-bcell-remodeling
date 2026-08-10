# Downloads the 2026 Zenodo BPCells conversion for Perez/GSE174188.
# This script is prepared but not run automatically because the matrix archive is ~1.4 GB.

$ErrorActionPreference = "Stop"

$RecordId = "20406617"
$ApiUrl = "https://zenodo.org/api/records/$RecordId"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OutDir = Join-Path $ProjectRoot "Data\processed\GSE174188_perez_zenodo_20406617"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$record = Invoke-RestMethod -Uri $ApiUrl
$record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $OutDir "zenodo_record_20406617.json") -Encoding UTF8

$manifest = foreach ($file in $record.files) {
    [PSCustomObject]@{
        key = $file.key
        size_bytes = $file.size
        checksum = $file.checksum
        download_url = $file.links.self
    }
}

$manifest | Export-Csv -LiteralPath (Join-Path $OutDir "download_manifest.csv") -NoTypeInformation -Encoding UTF8

foreach ($file in $record.files) {
    $dest = Join-Path $OutDir $file.key
    if (Test-Path -LiteralPath $dest) {
        Write-Host "Already exists: $dest"
    } else {
        Write-Host "Downloading $($file.key) ..."
        Invoke-WebRequest -Uri $file.links.self -OutFile $dest
    }

    if ($file.checksum -like "md5:*") {
        $expected = $file.checksum.Substring(4).ToLowerInvariant()
        $actual = (Get-FileHash -LiteralPath $dest -Algorithm MD5).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "MD5 mismatch for $($file.key): expected $expected, got $actual"
        }
        Write-Host "MD5 ok: $($file.key)"
    }
}

Write-Host "Download complete: $OutDir"
