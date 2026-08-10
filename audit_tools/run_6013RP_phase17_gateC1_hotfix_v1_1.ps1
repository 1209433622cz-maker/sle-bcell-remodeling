#requires -Version 5.1
[CmdletBinding()]
param(
  [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf",
  [string]$PreviousRunDir = "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\20260806_132230",
  [string]$OutputRoot = "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1"
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

$Freeze=Join-Path $PSScriptRoot "phase17_00_freeze_and_verify_inputs_v2.py"
$Meta=Join-Path $PSScriptRoot "phase17_01_metadata_hierarchy_audit_v2.py"
$QC=Join-Path $PSScriptRoot "phase17_02_raw_count_qc_profile_v2.py"
foreach($p in @($Freeze,$Meta,$QC)){if(-not(Test-Path $p)){throw "Missing $p"}}
$Py=Get-Command py -ErrorAction Stop
& $Py.Source -3 -c "import h5py,numpy,pandas,scipy"
if($LASTEXITCODE-ne 0){throw "Install: py -3 -m pip install h5py numpy pandas scipy"}

$Stamp=Get-Date -Format "yyyyMMdd_HHmmss"
$RunDir=Join-Path $OutputRoot "${Stamp}_hotfix_v1_1"
New-Item -ItemType Directory -Force -Path $RunDir|Out-Null

$reused=$false
if(Test-Path $PreviousRunDir){
  $files=@("00_INPUT_FREEZE_SUMMARY.md","00_input_manifest.csv","00_input_manifest.json")
  if(($files|ForEach-Object{Test-Path(Join-Path $PreviousRunDir $_)})-notcontains $false){
    $files|ForEach-Object{Copy-Item(Join-Path $PreviousRunDir $_)(Join-Path $RunDir $_)}
    $reused=$true
    Write-Host "[PASS] Reused prior SHA-256/input freeze." -ForegroundColor Green
  }
}
if(-not $reused){
  & $Py.Source -3 $Freeze --project-root $ProjectRoot --output-dir $RunDir
  if($LASTEXITCODE-ne 0){throw "Freeze failed: $LASTEXITCODE"}
}
& $Py.Source -3 $Meta --project-root $ProjectRoot --output-dir $RunDir
if($LASTEXITCODE-ne 0){throw "Metadata v2 failed: $LASTEXITCODE"}
& $Py.Source -3 $QC --project-root $ProjectRoot --output-dir $RunDir
if($LASTEXITCODE-ne 0){throw "QC v2 failed: $LASTEXITCODE"}

@"
# Gate C1 hotfix v1.1 workflow
- Time: $(Get-Date -Format o)
- Project: ``$ProjectRoot``
- Previous: ``$PreviousRunDir``
- Output: ``$RunDir``
- Reused input freeze: $reused

Corrected categorical raw/var decoding and separated biological conflicts from technical multiplicity.
No cells were removed.
"@ | Set-Content (Join-Path $RunDir "WORKFLOW_GATE_C1_HOTFIX_V1_1.md") -Encoding UTF8
"run_dir=$RunDir"|Set-Content(Join-Path $OutputRoot "_LATEST_GATE_C1.txt")-Encoding UTF8
Write-Host "Completed: $RunDir" -ForegroundColor Green
