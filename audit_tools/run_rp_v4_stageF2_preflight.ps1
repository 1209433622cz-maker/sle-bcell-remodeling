param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$WorkRoot = ".\phase17_v7\rp_v4_redesign\_software_tests\20261011_stageF2",
    [string]$CanonicalOutput = ".\phase17_v7\rp_v4_redesign\20261011_stageF2_integrity_hardening",
    [string]$ExternalZip = "C:\Users\Administrator\Downloads\SLE_RPv4_StageF_ExactCode_IntegrityReview_20261011.zip",
    [string]$ExternalRoot = "C:\Users\Administrator\Downloads\SLE_RPv4_StageF_ExactCode_IntegrityReview_20261011_extracted\SLE_RPv4_StageF_Review_20261011"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $Repo
$env:PYTHONPATH = "$Repo;$Repo\audit_tools"

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python executable not found: $Python"
}
if (Test-Path -LiteralPath $WorkRoot) {
    throw "WorkRoot already exists; use a new path: $WorkRoot"
}
if (Test-Path -LiteralPath $CanonicalOutput) {
    throw "Canonical output already exists: $CanonicalOutput"
}
if (-not (Test-Path -LiteralPath $ExternalZip -PathType Leaf)) {
    throw "External Stage F ZIP not found: $ExternalZip"
}
if (-not (Test-Path -LiteralPath $ExternalRoot -PathType Container)) {
    throw "Extracted Stage F review root not found: $ExternalRoot"
}

$WorkRoot = [System.IO.Path]::GetFullPath((Join-Path $Repo $WorkRoot))
$CanonicalOutput = [System.IO.Path]::GetFullPath((Join-Path $Repo $CanonicalOutput))
New-Item -ItemType Directory -Path $WorkRoot | Out-Null

$Registry = Join-Path $Repo "phase17_v7\rp_v4_redesign\20261010_stageC_single_g2c_external_input_protocol_freeze\05_G2C_FINAL_DGP_REGISTRY.csv"
$Model = Join-Path $Repo "phase17_v7\rp_v3_redesign\20261010_g2_implementation_freeze\02_G2_CALIBRATION_MODEL.json"
$AuthorSignoff = Join-Path $Repo "phase17_v7\rp_v4_redesign\20261011_stageE2_authorized_preflight\02_AUTHOR_CONTRACT_SIGNOFF.json"
$Prepared = Join-Path $WorkRoot "prepared"
$Outer = Join-Path $WorkRoot "outer_qualification"
$Truth = Join-Path $WorkRoot "truth_qualification"
$PreflightReceipt = Join-Path $WorkRoot "stageF2_windows_qualification.json"

function Invoke-PythonChecked {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')"
    }
}

function Get-TreeInventory {
    param([string]$Root)
    $resolved = (Resolve-Path -LiteralPath $Root).Path
    return @(
        Get-ChildItem -LiteralPath $resolved -Recurse -File |
            Sort-Object FullName |
            ForEach-Object {
                $relative = $_.FullName.Substring($resolved.Length).TrimStart('\')
                $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLower()
                "$relative|$($_.Length)|$hash"
            }
    )
}

Write-Output "[1/8] Preparing the exact Stage F2 source binding..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_freeze.py" "prepare" "--output" $Prepared
$Binding = Join-Path $Prepared "04_STAGE_F2_SOURCE_BINDING.csv"
$GoDraft = Join-Path $Prepared "08_STAGE_G_EXACT_CODE_GO_DRAFT.json"

Write-Output "[2/8] Running RP v4 regression and adversarial tests..."
$TestModules = @(
    "audit_tools.test_rp_v4_g2c",
    "audit_tools.test_rp_v4_stageA",
    "audit_tools.test_rp_v4_stageD",
    "audit_tools.test_rp_v4_stageE2",
    "audit_tools.test_rp_v4_stageF2"
)
$TestStdout = Join-Path $WorkRoot "unit_tests.stdout.txt"
$TestStderr = Join-Path $WorkRoot "unit_tests.stderr.txt"
$TestProcess = Start-Process -FilePath $Python `
    -ArgumentList (@("-m", "unittest") + $TestModules + @("-v")) `
    -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput $TestStdout `
    -RedirectStandardError $TestStderr
$TestOutput = @(
    Get-Content -LiteralPath $TestStdout
    Get-Content -LiteralPath $TestStderr
)
$TestExit = $TestProcess.ExitCode
$TestOutput | ForEach-Object { Write-Output $_ }
if ($TestExit -ne 0) {
    throw "RP v4 regression suite failed"
}
$TestText = $TestOutput -join "`n"
$Match = [regex]::Match($TestText, "Ran\s+(\d+)\s+tests?")
if (-not $Match.Success) {
    throw "Could not parse the test count"
}
$TestCount = [int]$Match.Groups[1].Value
$TestSummary = "$TestCount/$TestCount PASS"
$TamperSummary = "Stage F2 integrity/adversarial tests included; $TestSummary"

Write-Output "[3/8] Running hash-sealed outer qualification and resume verification..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_runner.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--output" $Outer `
    "--mode" "qualification" `
    "--qualification-attempts" "8" `
    "--scenarios" "C0_X1" "C1_X2" "C2_X3"
$OuterBefore = Get-TreeInventory $Outer
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_runner.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--output" $Outer `
    "--mode" "qualification" `
    "--resume" `
    "--qualification-attempts" "8" `
    "--scenarios" "C0_X1" "C1_X2" "C2_X3"
$OuterAfter = Get-TreeInventory $Outer
if (Compare-Object $OuterBefore $OuterAfter) {
    throw "Outer qualification tree changed during resume"
}

Write-Output "[4/8] Running checkpointed truth qualification and resume verification..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_truth.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--output" $Truth `
    "--mode" "qualification" `
    "--scenarios" "C0_X1" "C1_X2" "C2_X3"
$TruthBefore = Get-TreeInventory $Truth
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_truth.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--output" $Truth `
    "--mode" "qualification" `
    "--resume" `
    "--scenarios" "C0_X1" "C1_X2" "C2_X3"
$TruthAfter = Get-TreeInventory $Truth
if (Compare-Object $TruthBefore $TruthAfter) {
    throw "Truth qualification tree changed during resume"
}

Write-Output "[5/8] Issuing the Windows runtime qualification receipt..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_preflight.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--author-signoff" $AuthorSignoff `
    "--go-draft" $GoDraft `
    "--binding-manifest" $Binding `
    "--outer-root" $Outer `
    "--truth-root" $Truth `
    "--unit-and-regression-tests" $TestSummary `
    "--negative-tamper-tests" $TamperSummary `
    "--output" $PreflightReceipt

Write-Output "[6/8] Proving stage141/stage142 remain fail-closed..."
$FinalOuterAttempt = Join-Path $WorkRoot "forbidden_stage141"
$FinalOuterStdout = Join-Path $WorkRoot "forbidden_stage141.stdout.txt"
$FinalOuterStderr = Join-Path $WorkRoot "forbidden_stage141.stderr.txt"
$FinalOuterProcess = Start-Process -FilePath $Python `
    -ArgumentList @(
        ".\audit_tools\rp_v4_stageF2_runner.py",
        "--registry", $Registry,
        "--calibration-model", $Model,
        "--output", $FinalOuterAttempt,
        "--mode", "final",
        "--authorization", $GoDraft,
        "--binding-manifest", $Binding,
        "--runtime-qualification", $PreflightReceipt
    ) `
    -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput $FinalOuterStdout `
    -RedirectStandardError $FinalOuterStderr
$FinalOuterExit = $FinalOuterProcess.ExitCode
if ($FinalOuterExit -eq 0 -or (Test-Path -LiteralPath $FinalOuterAttempt)) {
    throw "Stage141 did not fail closed"
}
$FinalTruthAttempt = Join-Path $WorkRoot "forbidden_stage142"
$FinalTruthStdout = Join-Path $WorkRoot "forbidden_stage142.stdout.txt"
$FinalTruthStderr = Join-Path $WorkRoot "forbidden_stage142.stderr.txt"
$FinalTruthProcess = Start-Process -FilePath $Python `
    -ArgumentList @(
        ".\audit_tools\rp_v4_stageF2_truth.py",
        "--registry", $Registry,
        "--calibration-model", $Model,
        "--output", $FinalTruthAttempt,
        "--mode", "final",
        "--authorization", $GoDraft,
        "--binding-manifest", $Binding,
        "--runtime-qualification", $PreflightReceipt
    ) `
    -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput $FinalTruthStdout `
    -RedirectStandardError $FinalTruthStderr
$FinalTruthExit = $FinalTruthProcess.ExitCode
if ($FinalTruthExit -eq 0 -or (Test-Path -LiteralPath $FinalTruthAttempt)) {
    throw "Stage142 did not fail closed"
}

Write-Output "[7/8] Freezing the canonical Stage F2 evidence bundle..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_freeze.py" "finalize" `
    "--prepared" $Prepared `
    "--preflight-receipt" $PreflightReceipt `
    "--external-zip" $ExternalZip `
    "--external-root" $ExternalRoot `
    "--output" $CanonicalOutput

Write-Output "[8/8] Final compact verification..."
Invoke-PythonChecked ".\audit_tools\rp_v4_stageF2_preflight.py" `
    "--registry" $Registry `
    "--calibration-model" $Model `
    "--author-signoff" $AuthorSignoff `
    "--go-draft" $GoDraft `
    "--binding-manifest" $Binding `
    "--outer-root" $Outer `
    "--truth-root" $Truth `
    "--unit-and-regression-tests" $TestSummary `
    "--negative-tamper-tests" $TamperSummary `
    "--output" (Join-Path $WorkRoot "second_preflight_receipt.json")

Write-Output "Stage F2 workflow completed."
Write-Output "Canonical bundle: $CanonicalOutput"
Write-Output "Tests: $TestSummary"
Write-Output "HOLD_POST_COMMIT_EXACT_CODE_GO: stage141/stage142 were not started."
