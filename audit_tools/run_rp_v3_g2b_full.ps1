param(
    [string]$Python = 'D:\bioinfor\python.exe',
    [Parameter(Mandatory = $true)][string]$OutputRoot,
    [string[]]$Regimes = @('R0'),
    [ValidateRange(1, 2000)][int]$ChunkSize = 25,
    [switch]$ValidateOnly,
    [switch]$Adjudicate
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Runner = Join-Path $PSScriptRoot 'rp_v3_g2b_full_runner.py'
$Adjudicator = Join-Path $PSScriptRoot 'rp_v3_g2b_adjudicate.py'
$ScenarioRegistry = Join-Path $RepoRoot 'phase17_v7\rp_v3_redesign\20261010_wp2_effect_free_prefit\08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv'

# powershell.exe -File passes comma-separated values as one string, whereas
# direct invocation can pass a real string array. Normalize both forms before
# validating so the documented commands behave identically.
$AllowedRegimes = @('R0', 'R1', 'R2', 'R3', 'R4')
$Regimes = @(
    $Regimes |
        ForEach-Object { $_ -split ',' } |
        ForEach-Object { $_.Trim().ToUpperInvariant() } |
        Where-Object { $_ } |
        Select-Object -Unique
)
$InvalidRegimes = @($Regimes | Where-Object { $AllowedRegimes -notcontains $_ })
if ($InvalidRegimes.Count -gt 0) {
    throw "Invalid regime(s): $($InvalidRegimes -join ', '). Allowed values: $($AllowedRegimes -join ', ')."
}
if ($Regimes.Count -eq 0) { throw 'At least one regime is required.' }

if (-not (Test-Path -LiteralPath $Python)) { throw "Python executable not found: $Python" }
if (-not (Test-Path -LiteralPath $ScenarioRegistry)) { throw "Scenario registry not found: $ScenarioRegistry" }

$OutputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:NUMEXPR_NUM_THREADS = '1'

Write-Host '[1/3] Running frozen G2 and G2B implementation tests...'
& $Python -m unittest -v audit_tools.test_rp_v3_g2 audit_tools.test_rp_v3_g2b
if ($LASTEXITCODE -ne 0) { throw 'G2/G2B implementation tests failed.' }
if ($ValidateOnly) {
    Write-Host 'Validation passed. No G2B outer attempt was executed and real WP2 effects remain locked.'
    return
}

$registered = Import-Csv -LiteralPath $ScenarioRegistry
$selected = @($registered | Where-Object {
    $suffix = ($_.scenario_id -split '_')[1]
    $Regimes -contains $suffix
})
if ($selected.Count -eq 0) { throw 'No scenarios selected.' }

Write-Host "[2/3] Running $($selected.Count) registered G2B scenarios in chunks of $ChunkSize..."
foreach ($scenario in $selected) {
    for ($start = 1; $start -le 2000; $start += $ChunkSize) {
        $end = [Math]::Min(2000, $start + $ChunkSize - 1)
        Write-Host ("[G2B] {0} attempts {1}-{2}" -f $scenario.scenario_id, $start, $end)
        & $Python $Runner `
            --output-root $OutputRoot `
            --scenario $scenario.scenario_id `
            --attempt-start $start `
            --attempt-end $end
        if ($LASTEXITCODE -ne 0) {
            throw 'G2B chunk failed. Preserve the output and rerun the same command to verify or resume.'
        }
    }
}

if ($Adjudicate) {
    $allRegimes = $AllowedRegimes
    if (@($allRegimes | Where-Object { $Regimes -notcontains $_ }).Count -gt 0) {
        throw '-Adjudicate requires all five regimes. Partial results cannot receive a final G2B decision.'
    }
    $AdjudicationDir = Join-Path $OutputRoot 'adjudication'
    Write-Host '[3/3] Adjudicating the complete 25-scenario G2B grid...'
    & $Python $Adjudicator --run-root $OutputRoot --output-dir $AdjudicationDir
    if ($LASTEXITCODE -ne 0) { throw 'Full-G2B adjudication failed.' }
} else {
    Write-Host '[3/3] Adjudication not requested. This is a partial checkpoint, not a G2B decision.'
}

Write-Host 'Completed requested synthetic G2B work. Real WP2 effects remain locked pending a separate post-G2B review.'
