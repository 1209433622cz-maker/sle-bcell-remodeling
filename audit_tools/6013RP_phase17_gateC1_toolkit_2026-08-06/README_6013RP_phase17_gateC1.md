# 6013RP-wyf Phase 17 Gate C1 工具

## 目的

在正式重聚类前完成：

1. 权威输入和 SHA-256 冻结；
2. raw/X 完整性；
3. donor–sample–library–cohort 层级；
4. repeated donor；
5. cohort × disease common support；
6. raw-count QC 分布；
7. sample-aware 候选阈值。

工具默认只读，不改 H5AD，不删除细胞。

## 放置

解压到：

```text
H:\cuhk-2025fALL\6013RP-wyf\audit_tools\phase17_gateC1\
```

## 依赖

```powershell
py -3 -m pip install h5py numpy pandas scipy
```

推荐最终重跑使用项目 Python 3.11 conda 环境，而不是临时 Python 3.13。

## 运行

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force

& "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\phase17_gateC1\run_6013RP_phase17_gateC1.ps1" `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

也可使用：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\phase17_gateC1\run_6013RP_phase17_gateC1.ps1" `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

## 输出

```text
H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\YYYYMMDD_HHMMSS\
```

上传整个最新目录。重点文件：

```text
00_INPUT_FREEZE_SUMMARY.md
00_input_manifest.csv
01_sample_manifest.csv
02_donor_manifest.csv
03_library_manifest.csv
04_cohort_disease_common_support.csv
05_repeated_donor_manifest.csv
06_metadata_conflicts.csv
08_sample_qc_summary.csv
09_sample_qc_candidate_thresholds.csv
02_RAW_COUNT_QC_SUMMARY.md
WORKFLOW_GATE_C1.md
```

`07_per_cell_raw_qc.csv.gz` 可能较大；若上传受限，可先不上传。
