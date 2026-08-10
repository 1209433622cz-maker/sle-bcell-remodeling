# Gate C1 hotfix v1.1

本版本修复：

1. `raw/var/feature_name` 为 AnnData categorical group 时无法 `[:]` 读取；
2. 多个 `library_uuid` / `Processing_Cohort` 被错误标记为 sample metadata conflict；
3. 新增 sample-library、sample-cohort 和 library-level QC。

## 运行

解压 ZIP 后执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force

$hotfix = Get-ChildItem `
  -Path "H:\cuhk-2025fALL\6013RP-wyf\audit_tools" `
  -Recurse `
  -Filter "run_6013RP_phase17_gateC1_hotfix_v1_1.ps1" |
  Select-Object -First 1

& $hotfix.FullName `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf" `
  -PreviousRunDir "H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\20260806_132230"
```

会复用已经成功的 SHA-256，不重新计算。

输出：

```text
H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\YYYYMMDD_HHMMSS_hotfix_v1_1\
```

上传整个新目录；`10_per_cell_raw_qc.csv.gz` 若过大可暂不上传。
