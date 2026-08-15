#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$GateC4ARunDir = "",
    [string]$OutputDir = "",
    [string]$CondaEnvironment = "sle-bcell"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($GateC4ARunDir)) {
    $GateC4ARunDir = Join-Path $ProjectRoot "phase17_v7\gateC4A\20260815_raw_pseudobulk_freeze"
} elseif (-not [System.IO.Path]::IsPathRooted($GateC4ARunDir)) {
    $GateC4ARunDir = Join-Path $ProjectRoot $GateC4ARunDir
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot "phase17_v7\gateC4B\$(Get-Date -Format 'yyyyMMdd_HHmmss')_edger_transcription"
} elseif (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot $OutputDir
}
$GateC4ARunDir = [System.IO.Path]::GetFullPath($GateC4ARunDir)
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
    throw "Rscript was not found. Run run_6013RP_phase17_gateC4B_prepare_edger.ps1 first."
}

$SavedLocale = @{
    LANG = $env:LANG
    LC_ALL = $env:LC_ALL
    LC_CTYPE = $env:LC_CTYPE
}
Remove-Item Env:LANG, Env:LC_ALL, Env:LC_CTYPE -ErrorAction SilentlyContinue
try {
    Write-Host "[1/4] Exporting frozen C4A matrices..."
    & $CondaExe run --no-capture-output -n $CondaEnvironment python `
        (Join-Path $PSScriptRoot "phase17_c4b_01_export_frozen_matrices.py") `
        --gate-c4a-dir $GateC4ARunDir `
        --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) { throw "Frozen matrix export failed." }

    Write-Host "[2/4] Qualifying edgeR/limma before real-effect access..."
    $Qualification = Join-Path $OutputDir "04_EDGER_QUALIFICATION.json"
    & $Rscript `
        (Join-Path $PSScriptRoot "phase17_c4b_02_qualify_edger.R") `
        $OutputDir `
        $Qualification
    if ($LASTEXITCODE -ne 0) { throw "edgeR qualification failed; real effects remain locked." }
    $QualificationObject = Get-Content -LiteralPath $Qualification -Raw | ConvertFrom-Json
    if ($QualificationObject.status -ne "PASS_C4B_EDGER_QUALIFICATION") {
        throw "Qualification did not authorize real-effect fitting."
    }

    Write-Host "[3/4] Fitting the frozen real-effect models..."
    & $Rscript `
        (Join-Path $PSScriptRoot "phase17_c4b_03_fit_frozen_models.R") `
        $OutputDir `
        $GateC4ARunDir
    if ($LASTEXITCODE -ne 0) { throw "Frozen C4B model fitting failed." }

    Write-Host "[4/4] Auditing results and generating the publication figure..."
    & $CondaExe run --no-capture-output -n $CondaEnvironment python `
        (Join-Path $PSScriptRoot "phase17_c4b_04_review_and_figure.py") `
        --run-dir $OutputDir `
        --gate-c4a-dir $GateC4ARunDir
    if ($LASTEXITCODE -ne 0) { throw "C4B result adjudication failed." }
} finally {
    foreach ($Name in $SavedLocale.Keys) {
        if ($null -eq $SavedLocale[$Name]) {
            Remove-Item "Env:$Name" -ErrorAction SilentlyContinue
        } else {
            Set-Item "Env:$Name" $SavedLocale[$Name]
        }
    }
}

Write-Host "Gate C4B workflow completed:"
Write-Host (Join-Path $OutputDir "15_GATE_C4B_ADVISOR_DECISION.md")
