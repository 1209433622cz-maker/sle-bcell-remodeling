# 6013RP Phase 17 Gate C2A：疾病盲法 20k smoke test 设计

## 输入

- Discovery：`bcell_subset_full.h5ad::raw/X`
- Gate C1：`20260806_134213_hotfix_v1_1`
- 目标：20,000 cells
- 随机种子：20260806

## Disease-blind 约束

工作 AnnData 仅保留：

```text
cell_id
cell_index
donor_id
sample_uuid
library_uuid
Processing_Cohort
```

以下字段单独写入 protected metadata，不进入 clustering object：

```text
disease
disease_state
ct_cov
sex
ethnicity
development_stage
```

smoke clustering、HVG、PCA、Harmony、Leiden、resolution 选择均不得读取 protected metadata。

## QC

Hard-QC：

```text
UMI >= 500
genes >= 200
mito <= 10%
hemoglobin <= 1%
platelet <= 0.5%
at least 1 B-lineage marker
```

High UMI/high gene 不预先 hard filter；先运行 per-library Scrublet。

## Sampling

1. 每个 biological sample 最多先抽 40 cells；
2. 确保每个 library 至少有 smoke cells；
3. 剩余名额按 inverse-sqrt(sample size) 权重补足；
4. 不使用 disease 进行配额；
5. 输出 protected disease balance，仅用于检查抽样是否意外严重失衡。

## Representation

### Unintegrated

```text
log-normalization
library-aware HVG
PCA
neighbors
UMAP
```

### Batch-aware

```text
PCA
Harmony(batch = library_uuid)
neighbors
UMAP
```

两者同时保留，不自动宣布 Harmony 为最终表示。

## Clustering

Harmony graph：

```text
Leiden resolution = 0.2, 0.4, 0.6, 0.8, 1.0, 1.2
```

输出每个 cluster 的：

- cells；
- samples；
- donors；
- libraries；
- processing cohorts；
- 最大 library 占比；
- 最大 sample 占比。

## Neutral marker modules

- naive；
- memory；
- atypical；
- plasmablast/ASC；
- IFN；
- platelet contamination；
- erythroid contamination。

不使用：

```text
SLE-enriched
disease-associated
ABC/APC-expanded
```

作为 smoke cluster 名称。

## Gate C2A 输出

```text
00_config.json
01_qc_decisions.csv.gz
02_qc_retention_summary.csv
03_protected_outcome_metadata.csv.gz
04_smoke_selection_summary.csv
05_smoke_raw_counts.h5ad
06_scrublet_library_summary.csv
07_batch_mixing_metrics.csv
08_cluster_coverage.csv
09_marker_scores_by_cluster.csv
10_ranked_markers_r06.csv
11_smoke_cell_assignments.csv.gz
12_smoke_reclustered_hvg.h5ad
figures/
WORKFLOW_GATE_C2A.md
```
