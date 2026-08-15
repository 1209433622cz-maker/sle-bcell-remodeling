#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC5ARunDir = "",
    [string]$GateC4BRunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($GateC5ARunDir)) {
    $GateC5ARunDir = Join-Path $ProjectRoot "phase17_v7\gateC5A\20260815_gse135779_source_mapping_freeze"
} elseif (-not [System.IO.Path]::IsPathRooted($GateC5ARunDir)) {
    $GateC5ARunDir = Join-Path $ProjectRoot $GateC5ARunDir
}
if ([string]::IsNullOrWhiteSpace($GateC4BRunDir)) {
    $GateC4BRunDir = Join-Path $ProjectRoot "phase17_v7\gateC4B\20260815_edger_transcription"
} elseif (-not [System.IO.Path]::IsPathRooted($GateC4BRunDir)) {
    $GateC4BRunDir = Join-Path $ProjectRoot $GateC4BRunDir
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC5B\$(Get-Date -Format 'yyyyMMdd_HHmmss')_gse135779_external_validation"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot $OutputDir
}
$GateC5ARunDir = [System.IO.Path]::GetFullPath($GateC5ARunDir)
$GateC4BRunDir = [System.IO.Path]::GetFullPath($GateC4BRunDir)
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$CondaCandidates = @(
    "C:\ProgramData\miniforge3\condabin\conda.bat",
    "$env:USERPROFILE\miniforge3\condabin\conda.bat"
)
$PathConda = Get-Command conda -ErrorAction SilentlyContinue
if ($null -ne $PathConda) { $CondaCandidates += $PathConda.Source }
$CondaExe = $CondaCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    throw "Conda was not found. Prepare the existing sle-bcell environment first."
}

$RCandidates = @()
$PathR = Get-Command Rscript -ErrorAction SilentlyContinue
if ($null -ne $PathR) { $RCandidates += $PathR.Source }
$RCandidates += Get-ChildItem -LiteralPath "C:\Program Files\R" -Recurse -Filter Rscript.exe -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\bin\\x64\\" } |
    Sort-Object FullName -Descending |
    Select-Object -ExpandProperty FullName
$Rscript = $RCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($Rscript)) {
    throw "Rscript was not found. Prepare the Gate C4B edgeR environment first."
}

$SavedLocale = @{
    LANG = $env:LANG
    LC_ALL = $env:LC_ALL
    LC_CTYPE = $env:LC_CTYPE
}
Remove-Item Env:LANG, Env:LC_ALL, Env:LC_CTYPE -ErrorAction SilentlyContinue
try {
    Write-Host "[1/4] Exporting the frozen C5A external matrices..."
    & $CondaExe run --no-capture-output -n $CondaEnvironment python `
        (Join-Path $PSScriptRoot "phase17_c5b_01_export_frozen_matrices.py") `
        --gate-c5a-dir $GateC5ARunDir `
        --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) { throw "Frozen C5B matrix export failed." }

    Write-Host "[2/4] Qualifying all R imports and edgeR before real-effect access..."
    $Qualification = Join-Path $OutputDir "04_EDGER_QUALIFICATION.json"
    & $Rscript `
        (Join-Path $PSScriptRoot "phase17_c5b_02_qualify_edger.R") `
        $OutputDir `
        $Qualification
    if ($LASTEXITCODE -ne 0) { throw "C5B edgeR qualification failed; effects remain locked." }
    $QualificationObject = Get-Content -LiteralPath $Qualification -Raw | ConvertFrom-Json
    if ($QualificationObject.status -ne "PASS_C5B_EDGER_QUALIFICATION") {
        throw "C5B qualification did not authorize real-effect fitting."
    }

    Write-Host "[3/4] Fitting the five frozen external models and influence analyses..."
    & $Rscript `
        (Join-Path $PSScriptRoot "phase17_c5b_03_fit_frozen_models.R") `
        $OutputDir `
        $GateC5ARunDir
    if ($LASTEXITCODE -ne 0) { throw "Frozen C5B model fitting failed." }

    Write-Host "[4/4] Independently auditing replication and generating the figure..."
    & $CondaExe run --no-capture-output -n $CondaEnvironment python `
        (Join-Path $PSScriptRoot "phase17_c5b_04_review_and_figure.py") `
        --run-dir $OutputDir `
        --gate-c5a-dir $GateC5ARunDir `
        --gate-c4b-dir $GateC4BRunDir
    if ($LASTEXITCODE -ne 0) { throw "C5B result adjudication failed." }
} finally {
    foreach ($Name in $SavedLocale.Keys) {
        if ($null -eq $SavedLocale[$Name]) {
            Remove-Item "Env:$Name" -ErrorAction SilentlyContinue
        } else {
            Set-Item "Env:$Name" $SavedLocale[$Name]
        }
    }
}

Write-Host "Gate C5B workflow completed:"
Write-Host (Join-Path $OutputDir "17_GATE_C5B_ADVISOR_DECISION.md")
