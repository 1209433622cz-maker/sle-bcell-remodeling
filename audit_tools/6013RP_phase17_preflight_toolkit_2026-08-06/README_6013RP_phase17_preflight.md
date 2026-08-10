# 6013RP-wyf Phase 17 预检工具包

## 内容

- `inspect_6013RP_h5ad_deep.py`
- `run_inspect_6013RP_h5ad_deep.ps1`
- `build_6013RP_phase17_review_pack.py`
- `run_build_6013RP_phase17_review_pack.ps1`
- `6013RP_audit_interpretation_next_stage_2026-08-06.md`

## 放置位置

将这些文件解压到：

```text
H:\cuhk-2025fALL\6013RP-wyf\audit_tools\phase17_preflight\
```

## 第一步：H5AD 深度审计

```powershell
cd "H:\cuhk-2025fALL\6013RP-wyf\audit_tools\phase17_preflight"
Set-ExecutionPolicy -Scope Process Bypass

.\run_inspect_6013RP_h5ad_deep.ps1 `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

若提示缺少 h5py：

```powershell
py -3 -m pip install h5py numpy
```

然后重新执行。脚本采用 HDF5 backed/lightweight 读取，不会把 11.38 GB 的表达矩阵完整加载进内存。

## 第二步：生成紧凑审阅包

```powershell
.\run_build_6013RP_phase17_review_pack.ps1 `
  -ProjectRoot "H:\cuhk-2025fALL\6013RP-wyf"
```

输出：

```text
H:\cuhk-2025fALL\6013RP-wyf\_phase17_review_pack\YYYYMMDD_HHMMSS.zip
```

上传这个 ZIP 和最新 H5AD 审计目录即可。
