#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

function Find-Rscript {
    $Candidates = @()
    $PathR = Get-Command Rscript -ErrorAction SilentlyContinue
    if ($null -ne $PathR) { $Candidates += $PathR.Source }
    $Candidates += Get-ChildItem -LiteralPath "C:\Program Files\R" -Recurse -Filter Rscript.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\bin\\x64\\" } |
        Sort-Object FullName -Descending |
        Select-Object -ExpandProperty FullName
    return $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}

$Rscript = Find-Rscript
if ([string]::IsNullOrWhiteSpace($Rscript)) {
    $Winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($null -eq $Winget) {
        throw "Rscript and winget were not found. Install R for Windows, then rerun."
    }
    Write-Host "R was not found. Installing R for Windows via winget..."
    & $Winget.Source install --id RProject.R --exact --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "winget could not install R." }
    $Rscript = Find-Rscript
}
if ([string]::IsNullOrWhiteSpace($Rscript)) {
    throw "R installation finished but Rscript.exe could not be located."
}

$SavedLocale = @{
    LANG = $env:LANG
    LC_ALL = $env:LC_ALL
    LC_CTYPE = $env:LC_CTYPE
}
Remove-Item Env:LANG, Env:LC_ALL, Env:LC_CTYPE -ErrorAction SilentlyContinue
try {
    & $Rscript (Join-Path $PSScriptRoot "phase17_c4b_00_install_packages.R")
    if ($LASTEXITCODE -ne 0) { throw "Gate C4B R package preparation failed." }
} finally {
    foreach ($Name in $SavedLocale.Keys) {
        if ($null -eq $SavedLocale[$Name]) {
            Remove-Item "Env:$Name" -ErrorAction SilentlyContinue
        } else {
            Set-Item "Env:$Name" $SavedLocale[$Name]
        }
    }
}
Write-Host "Gate C4B edgeR/limma environment is ready:"
Write-Host $Rscript
