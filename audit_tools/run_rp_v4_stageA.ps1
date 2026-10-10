param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$OutputDir = ".\phase17_v7\rp_v4_redesign\20261010_stageA_authority_feasibility_freeze",
    [string]$ProposalRoot = ".\phase17_v7\rp_v4_redesign\20261010_proposal_external_candidate",
    [string]$ProposalZip = "C:\Users\Administrator\Downloads\SLE_Bcell_RP_v4_Proposal_Audit_20261010.zip"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $OutputDir))
$ProposalPath = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $ProposalRoot))
$MetadataPath = Join-Path $OutputPath "source_metadata"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python executable not found: $Python"
}
if (-not (Test-Path -LiteralPath $ProposalPath)) {
    throw "Proposal evidence directory not found: $ProposalPath"
}
if (-not (Test-Path -LiteralPath $ProposalZip)) {
    throw "Proposal ZIP not found: $ProposalZip"
}
if (-not (Test-Path -LiteralPath $MetadataPath)) {
    throw "Official GEO MINiML metadata directory not found: $MetadataPath"
}
if (Get-ChildItem -LiteralPath $OutputPath -Filter "[0-9][0-9]_*" -ErrorAction SilentlyContinue) {
    throw "Stage A numbered outputs already exist: $OutputPath"
}

Push-Location $RepoRoot
try {
    Write-Host "[1/2] Running RP v4 Stage A tests..."
    & $Python -m unittest -v audit_tools.test_rp_v4_stageA
    if ($LASTEXITCODE -ne 0) {
        throw "RP v4 Stage A tests failed."
    }

    Write-Host "[2/2] Freezing authority, historical diagnosis and cohort feasibility..."
    & $Python .\audit_tools\rp_v4_stageA_01_freeze.py `
        --workspace $RepoRoot `
        --output $OutputPath `
        --proposal-root $ProposalPath `
        --proposal-zip $ProposalZip `
        --metadata-dir $MetadataPath
    if ($LASTEXITCODE -ne 0) {
        throw "RP v4 Stage A freeze failed."
    }
}
finally {
    Pop-Location
}

Write-Host "RP v4 Stage A completed:"
Write-Host $OutputPath
