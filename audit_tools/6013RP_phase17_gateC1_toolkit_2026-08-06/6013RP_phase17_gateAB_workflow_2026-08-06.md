# Workflow：6013RP-wyf Phase 17 Gate A/B

- 日期：2026-08-06
- 输入：
  - `_phase17_h5ad_audit/20260806_120148`
  - `_phase17_review_pack/20260806_120548`
- 审阅文件数：542
- H5AD：9

## 已执行

1. 核查 discovery、validation 和 reference H5AD；
2. 确认 `bcell_subset_full.h5ad::raw/X` 为 Phase 17 权威 count 入口；
3. 核查 01–49 分析脚本；
4. 核查 v6 手稿；
5. 核查主图和补图；
6. 重建 donor–sample–library–cohort 层级；
7. 复核 raw fraction、OLS、CLR、pseudobulk 和外部验证；
8. 复核 regulatory evidence；
9. 重新评估投稿路线；
10. 制定 v7 分析规范；
11. 编写 Gate C1 输入冻结、metadata hierarchy 和 raw-count QC 工具。

## 关键决定

- v6 冻结；
- 不直接投稿；
- 不再修补旧 UMAP；
- 从 raw/X 重跑；
- sample 为主要实验单位；
- composition 采用 cohort-resolved model；
- 新增真实 state-internal pseudobulk；
- GSE135779 改为 frozen mapping validation；
- 主图重构为 5 张。

## 下一步

运行 Gate C1 工具，生成：

```text
H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC1\
```

审阅 metadata 冲突和 sample-aware QC 后，再启动 full B-cell reclustering。
