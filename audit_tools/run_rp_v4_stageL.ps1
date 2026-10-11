param(
    [string]$Python = "D:\bioinfor\python.exe",
    [string]$StageKRoot = ".\phase17_v7\rp_v4_redesign\_software_tests\20261011_stageK_external_candidate\SLE_StageK",
    [string]$GSE262846 = ".\phase17_v7\rp_v4_redesign\20261010_stageA_authority_feasibility_freeze\source_metadata\GSE262846_family.xml.tgz",
    [string]$GSE263716 = ".\phase17_v7\rp_v4_redesign\_software_tests\20261011_stageL_metadata\source_metadata\GSE263716_family.xml.tgz",
    [string]$Output = ".\phase17_v7\rp_v4_redesign\20261011_stageL_external_cohort_gate"
)

$ErrorActionPreference = "Stop"
if (Test-Path -LiteralPath $Output) {
    throw "Stage L output already exists: $Output"
}

& $Python ".\audit_tools\rp_v4_stageL_01_external_gate.py" `
    --stage-k-root $StageKRoot `
    --stage-k-zip-sha256 "f81798c2e1dfb3159986d8977a8a843ab40b0636490056f95fcb4a4f6ba15e8f" `
    --gse262846 $GSE262846 `
    --gse263716 $GSE263716 `
    --output $Output

Write-Host "Stage L metadata and unique-question gate completed: $Output"
