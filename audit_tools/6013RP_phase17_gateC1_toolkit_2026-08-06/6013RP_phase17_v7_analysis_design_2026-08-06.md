# 6013RP-wyf Phase 17 / v7 分析设计规范

## 0. 版本原则

- v6：冻结，不覆盖。
- v7：新建独立目录。
- 原始输入只读。
- 每一步生成：
  - script
  - config
  - log
  - table
  - source data
  - workflow Markdown
  - checksum
- 所有主图必须可追溯到最终统计表。
- 禁止手工修改结果 CSV 后重新画图。

建议目录：

```text
H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\
├─ 00_config
├─ 01_input_manifest
├─ 02_metadata
├─ 03_qc
├─ 04_reclustering
├─ 05_annotation
├─ 06_composition
├─ 07_pseudobulk_de
├─ 08_pathway_tf
├─ 09_validation
├─ 10_figures
├─ 11_manuscript
├─ 12_source_data
├─ 13_logs
└─ 14_workflows
```

---

## 1. 输入冻结

### Discovery

```text
Data/processed/GSE174188_perez_cellxgene/bcell_subset_full.h5ad
```

使用：

```text
raw/X
raw/var
obs
```

不使用：

```text
source X
source X_pca
source X_umap
```

作为 v7 主降维结果。

### Validation

```text
Data/processed/GSE135779_nehar_validation/gse135779_b_subcluster_counts.h5ad
Data/processed/GSE163121_bcell_validation/gse163121_bcell_counts.h5ad
```

### 输入审计

必须输出：

- absolute path
- relative path
- file size
- SHA-256
- n_obs
- n_vars
- matrix encoding
- raw count integrity sample
- obs/var fields
- run environment

---

## 2. Metadata hierarchy

### 主要字段

```text
donor_id
sample_uuid
library_uuid
Processing_Cohort
disease
disease_state
sex
self_reported_ethnicity
development_stage
```

### 必须完成

1. sample → donor 一致性；
2. sample → disease/disease_state 一致性；
3. sample → cohort/library 关系；
4. donor 多 sample 列表；
5. donor disease-state trajectory；
6. donor 跨 cohort 记录；
7. age 解析；
8. missingness；
9. normal 与 SLE 的共同支持；
10. primary analysis sample set 的书面规则。

### 重复 donor 处理

推荐三层：

1. Primary：
   - 每 donor 一个基线或预先定义 sample；
   - 规则必须不依赖结果。
2. Secondary：
   - 全 sample mixed model / cluster-robust donor SE。
3. Longitudinal：
   - flare → treated 配对分析，独立呈现。

不得把多个 sample 直接合并为 donor fraction 后忽略时间和状态。

---

## 3. Raw-count QC

### 计算

- total UMI
- detected genes
- mitochondrial fraction
- ribosomal fraction
- hemoglobin fraction
- platelet/megakaryocyte contamination score
- B-lineage marker support
- ambient contamination indicators
- doublet score

### 阈值原则

- sample-aware；
- median/MAD 或 quantile 候选；
- 先展示分布；
- 再冻结阈值；
- 阈值不得基于 disease outcome；
- 记录每 sample 保留率。

### doublet

优先：

- Scrublet per library/sample；
- 或 scDblFinder；
- 不能全数据一次性估算后忽略 library。

### ambient RNA

原始 droplets 若不可得，应透明说明；可采用：

- DecontX sensitivity；
- platelet/erythroid contamination exclusion；
- stringent marker QC；
- flagged state sensitivity。

不能把污染 cluster 简单保留并仅在补图说明，而不评估其对邻居图和其他状态的影响。

---

## 4. B-cell-specific representation

### 主流程

1. raw counts；
2. gene identifier harmonization；
3. QC filtering；
4. library-size normalization；
5. log1p；
6. sample-aware HVG；
7. scaling with clipping；
8. PCA；
9. unintegrated neighbor graph；
10. batch-aware representation；
11. UMAP；
12. Leiden multi-resolution。

### batch-aware 候选

- Harmony on PCA，batch=`library_uuid`；
- scVI，batch=`library_uuid`，必要时加入 continuous covariates；
- 不把 disease 作为 integration covariate；
- 不以“疾病混合更均匀”为唯一标准。

### 选择标准

- canonical B-cell biology preserved；
- donor/library mixing improved；
- disease signal没有被强制消除；
- state marker specificity；
- cluster stability；
- rare state reproducibility；
- batch predictability metrics；
- kBET/LISI 仅作辅助。

---

## 5. Cluster stability and annotation

### Resolution grid

```text
0.2, 0.4, 0.6, 0.8, 1.0, 1.2
```

### 稳定性

- adjusted Rand index；
- normalized mutual information；
- bootstrap/subsample stability；
- donor coverage；
- sample coverage；
- cluster size；
- marker reproducibility。

### Annotation

阶段 1：隐藏疾病信息。

使用：

- MS4A1, CD79A, CD37, CD74
- IGHD, TCL1A, IL4R, FCER2
- CD27, AIM2, GPR183, TNFRSF13B
- FCRL3, FCRL5, ITGAX, TBX21, ZEB2
- MZB1, JCHAIN, XBP1, SDC1, CD38
- HLA class II
- IFN genes

阶段 2：冻结 label。

阶段 3：解锁 disease，执行 abundance/DE。

### Reference mapping

- 原始 `ct_cov`；
- OneK1K；
- 公开 B-cell reference；
- 仅作 concordance，不代替 de novo evidence。

---

## 6. Composition analysis

### 数据

```text
sample_uuid × state counts
```

附带：

```text
donor_id
disease
Processing_Cohort
library_uuid
age
sex
ethnicity
disease_state
total_B_cells
```

### Primary model

候选：

- scCODA；
- sccomp；
- Dirichlet-multinomial；
- beta-binomial per state + multiplicity control。

### 核心设计

1. cohort 4 direct comparison；
2. cohort 3 exploratory；
3. cohort 1/2 不进行无支持的直接主推断；
4. cohort-specific effects；
5. random-effects meta-analysis；
6. leave-one-cohort-out；
7. one-sample-per-donor；
8. all-sample repeated-donor sensitivity；
9. minimum B-cell count filter；
10. reference-state sensitivity。

### 报告

- absolute proportion；
- log-ratio/compositional effect；
- 95% CI / credible interval；
- heterogeneity；
- donor/sample points；
- no sole reliance on FDR heatmaps。

---

## 7. State-internal pseudobulk DE

### 聚合

```text
sample_uuid × frozen_state × gene
```

原始 count 求和。

### Inclusion

建议起点：

- ≥20 cells per sample-state；
- ≥10 samples per disease group；
- ≥5 expressed samples per group；
- 最终阈值通过 sensitivity。

### 模型

edgeR QL 示例：

```text
~ Processing_Cohort + age + sex + ethnicity + disease
```

重复 donor：

- primary one-sample-per-donor；
- secondary duplicateCorrelation / mixed strategy / cluster-robust；
- longitudinal paired contrast 单独处理。

### 输出

- log2FC；
- CI；
- FDR；
- CPM；
- sample-state counts；
- Cook/influence diagnostics；
- cohort-specific effect；
- meta effect。

### 禁止

- 把 cell 当重复；
- 仅对 marker list 做差异；
- focus state vs other states 代替 SLE-vs-HC；
- 用 disease-informed state label 再证明 disease enrichment。

---

## 8. Pathway and TF activity

基于 genome-wide pseudobulk DE：

- Hallmark；
- Reactome；
- GO BP；
- interferon modules；
- BCR/TLR；
- antigen presentation；
- plasma-cell differentiation；
- DoRothEA/decoupleR TF activity。

报告：

- NES/effect；
- FDR；
- leading edge；
- cross-cohort direction；
- discovery–validation overlap。

---

## 9. External validation

## 9.1 冻结 discovery model

冻结：

- gene set；
- preprocessing；
- state centroids/classifier；
- probability threshold；
- QC；
- primary endpoints。

## 9.2 GSE135779

Primary endpoints：

1. mapped atypical/activated state fraction；
2. mapped-state SLE-vs-HC pseudobulk effect；
3. IFN program；
4. ZEB2/TBX21/ITGAX axis；
5. plasmablast signal。

模型应考虑：

- adult/child cohort；
- donor/sample；
- cell count；
- state mapping confidence。

### 禁止

- 在验证数据中重新定义 HC 95% threshold；
- 根据验证结果改 gene panel；
- 把 broad B-cell program scoring称为state replication。

## 9.3 GSE163121

只作：

- direction；
- effect estimate；
- uncertainty；
- 不做强显著性结论。

---

## 10. Manuscript writing rules

### 标题

避免：

- atlas
- identify
- novel state
- independent validation confirms

除非 v7 证据真正满足。

### 结果结构

1. Cohort hierarchy and common support
2. De novo B-cell reconstruction
3. Cohort-resolved composition
4. State-internal transcription
5. External frozen validation
6. Sensitivity and limitations

### 语言强度

| 证据 | 推荐用词 |
|---|---|
| 单队列探索 | suggested / nominated |
| 调整后但有混杂 | remained directionally consistent |
| compositional + cohort meta | supported |
| 独立冻结状态复现 | replicated |
| 多数据、多模型、一致 | robustly replicated |

---

## 11. 计算资源建议

Discovery 152,981 × 30,172 sparse count：

- RAM：建议 32 GB，最低 16 GB；
- 运行位置：WSL Ubuntu 22.04 或稳定 conda Python 3.11；
- 临时磁盘：50–100 GB；
- 禁止在 Python 3.13 临时环境中直接启动完整 Scanpy 重跑；
- 每个重步骤保存 checkpoint H5AD；
- 使用 tmux；
- 输出 session info。

---

## 12. 第一批实际执行任务

1. 运行 Gate C1 工具；
2. 上传 Gate C1 输出；
3. 冻结 QC 规则；
4. 生成 Phase17 v7 conda 环境；
5. 编写 B-cell de novo 重聚类脚本；
6. 先运行 20k smoke；
7. 再运行 full；
8. 完成 disease-blind annotation review；
9. 冻结 state labels；
10. 才开始 composition 和 disease DE。
