param(
    [Parameter(Mandatory = $true)]
    [string]$InputDocx,

    [Parameter(Mandatory = $true)]
    [string]$OutputPdf
)

$ErrorActionPreference = "Stop"
$inputPath = (Resolve-Path -LiteralPath $InputDocx).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputPdf)
$outputDirectory = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}

$wps = $null
$document = $null
try {
    $wps = New-Object -ComObject KWPS.Application
    $wps.Visible = $false
    try { $wps.DisplayAlerts = 0 } catch { }
    $document = $wps.Documents.Open($inputPath, $false, $true)
    try {
        # 17 is the Word/WPS fixed-format PDF value.
        $document.ExportAsFixedFormat($outputPath, 17)
    }
    catch {
        $document.SaveAs2($outputPath, 17)
    }
    if (-not (Test-Path -LiteralPath $outputPath)) {
        throw "WPS did not create the requested PDF: $outputPath"
    }
    $pdf = Get-Item -LiteralPath $outputPath
    if ($pdf.Length -le 0) {
        throw "WPS created an empty PDF: $outputPath"
    }
    Write-Output ("WPS_PDF_OK`t{0}`t{1}" -f $pdf.Length, $pdf.FullName)
}
finally {
    if ($null -ne $document) {
        try { $document.Close($false) } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($null -ne $wps) {
        try { $wps.Quit() } catch { }
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wps)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
