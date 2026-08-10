#requires -Version 5.1
<#
.SYNOPSIS
    6013RP-wyf 项目一键只读清点入口。

.DESCRIPTION
    自动寻找 py / python，调用 audit_6013RP_wyf.py。
    所有审计输出默认写入：
    H:\cuhk-2025fALL\6013RP-wyf\_project_audit\<时间戳>

    不移动、不重命名、不删除原项目文件。

.EXAMPLE
    Set-ExecutionPolicy -Scope Process Bypass
    .\run_6013RP_wyf_audit.ps1

.EXAMPLE
    .\run_6013RP_wyf_audit.ps1 -HashMode all -OpenReport

.EXAMPLE
    .\run_6013RP_wyf_audit.ps1 `
      -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf" `
      -HashMode smart `
      -MaxHashGB 20 `
      -VerboseAudit
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectRoot = "H:\cuhk-2025fALL\6013RP-wyf",

    [Parameter()]
    [ValidateSet("none", "smart", "all")]
    [string]$HashMode = "smart",

    [Parameter()]
    [ValidateRange(0.1, 10000)]
    [double]$MaxHashGB = 20,

    [Parameter()]
    [ValidateRange(1, 2048)]
    [double]$MaxTextMB = 20,

    [Parameter()]
    [ValidateRange(0.01, 10000)]
    [double]$LargeFileGB = 1,

    [Parameter()]
    [ValidateRange(1, 30)]
    [int]$TreeDepth = 6,

    [Parameter()]
    [ValidateRange(100, 1000000)]
    [int]$TreeMaxEntries = 10000,

    [Parameter()]
    [switch]$SkipRParse,

    [Parameter()]
    [switch]$SkipH5AD,

    [Parameter()]
    [switch]$SkipMedia,

    [Parameter()]
    [switch]$VerboseAudit,

    [Parameter()]
    [switch]$OpenReport
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AuditScript = Join-Path $PSScriptRoot "audit_6013RP_wyf.py"

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "项目目录不存在：$ProjectRoot"
}
if (-not (Test-Path -LiteralPath $AuditScript -PathType Leaf)) {
    throw "找不到 Python 审计脚本：$AuditScript。请确保两个文件放在同一目录。"
}

$PythonCommand = $null
$PythonPrefix = @()

$PyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
if ($null -ne $PyLauncher) {
    $PythonCommand = $PyLauncher.Source
    $PythonPrefix = @("-3")
}
else {
    $PythonExe = Get-Command "python" -ErrorAction SilentlyContinue
    if ($null -ne $PythonExe) {
        $PythonCommand = $PythonExe.Source
    }
}

if ($null -eq $PythonCommand) {
    throw @"
未找到 Windows Python。
请任选一种方式：
1. 安装 Python 3，并确保 py 或 python 位于 PATH；
2. 在 WSL 中运行：
   python3 /mnt/h/<脚本所在目录>/audit_6013RP_wyf.py `
     --root /mnt/h/cuhk-2025fALL/6013RP-wyf
"@
}

$Arguments = @()
$Arguments += $PythonPrefix
$Arguments += @(
    $AuditScript,
    "--root", $ProjectRoot,
    "--hash-mode", $HashMode,
    "--max-hash-gb", $MaxHashGB.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--max-text-mb", $MaxTextMB.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--large-file-gb", $LargeFileGB.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--tree-depth", $TreeDepth.ToString(),
    "--tree-max-entries", $TreeMaxEntries.ToString()
)

if ($SkipRParse) { $Arguments += "--skip-r-parse" }
if ($SkipH5AD) { $Arguments += "--skip-h5ad" }
if ($SkipMedia) { $Arguments += "--skip-media" }
if ($VerboseAudit) { $Arguments += "--verbose" }

Write-Host "============================================================"
Write-Host "6013RP-wyf 项目全量只读清点" -ForegroundColor Cyan
Write-Host "ProjectRoot : $ProjectRoot"
Write-Host "HashMode    : $HashMode"
Write-Host "Python      : $PythonCommand"
Write-Host "============================================================"

& $PythonCommand @Arguments
$ExitCode = $LASTEXITCODE

if ($ExitCode -ne 0) {
    throw "审计脚本失败，退出码：$ExitCode"
}

$LatestFile = Join-Path $ProjectRoot "_project_audit\_LATEST_AUDIT.txt"
if (Test-Path -LiteralPath $LatestFile) {
    $LatestLines = Get-Content -LiteralPath $LatestFile -Encoding UTF8
    $SummaryLine = $LatestLines | Where-Object { $_ -like "summary=*" } | Select-Object -First 1
    if ($SummaryLine) {
        $SummaryPath = $SummaryLine.Substring("summary=".Length)
        Write-Host ""
        Write-Host "审计完成：" -ForegroundColor Green
        Write-Host $SummaryPath
        if ($OpenReport -and (Test-Path -LiteralPath $SummaryPath)) {
            Start-Process -FilePath $SummaryPath
        }
    }
}
