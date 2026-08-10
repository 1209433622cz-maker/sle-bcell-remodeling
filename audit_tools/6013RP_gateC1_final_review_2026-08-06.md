# 6013RP-wyf Gate C1 最终复核与 Gate C2 决策

> **2026-08-10 勘误：** 本历史报告第 3 节的严格共同支持数字为不可复算的手工汇总，禁止继续引用。绑定更正来源为 `phase17_v7/gateC1/20260806_134213_hotfix_v1_1/15_strict_common_support_reaudit.csv` 和 `16_STRICT_COMMON_SUPPORT_ERRATUM.md`；正确的 cohort 1-4 normal/SLE 数为 28/0、1/87、5/8、41/25。

- 项目：SLE B-cell single-cell transcriptomics
- Gate C1 输出：`phase17_v7\gateC1\20260806_134213_hotfix_v1_1`
- 复核日期：2026-08-06
- 决策：**Gate C1 PASS；允许进入 Gate C2A 疾病盲法 smoke test**
- 当前仍不允许：直接全量重聚类后覆盖 v6、直接改写论文结论、直接投稿

---

## 1. Gate C1 已确认的权威输入

```text
H:\cuhk-2025fALL\6013RP-wyf\Data\processed\
GSE174188_perez_cellxgene\bcell_subset_full.h5ad
```

| 项目 | 结果 |
|---|---:|
| SHA-256 | `fbd4692e033a57412fcc9dfe761180a9e4bdae37c4fda8f5ecc2e28fde46371b` |
| Cells | 152,981 |
| Genes | 30,172 |
| `raw/X` | 存在 |
| raw count 抽样整数比例 | 1.0 |
| raw count 非负 | True |
| Gate | PASS |

因此 Phase 17 的唯一主入口继续冻结为：

```text
bcell_subset_full.h5ad::raw/X
```

不能从 first-pass processed/labeled 对象的缩放 `X` 开始。

---

## 2. 样本与技术层级的最终解释

| 层级 | 数量 | 正确角色 |
|---|---:|---|
| donor | 259 | 受试者、重复测量聚类单位 |
| sample | 271 | 主要生物学实验单位 |
| library | 88 | 多样本复用技术池 |
| processing cohort | 4 | 技术处理分层 |

### 已确认

- 11 个 donor 有重复 sample；
- 11 个 donor 有多个 disease state；
- 271/271 sample 都跨至少 2 个 library；
- 53 个 sample 跨多个 processing cohort；
- 56 个 donor 跨多个 processing cohort；
- **真实 sample 生物学字段冲突：0**；
- **真实 donor identity 冲突：0**；
- **library 内 processing cohort 冲突：0**。

### 对旧判断的修正

上一版把 sample 中多个 library/cohort 计为 271 个 metadata conflict，这是错误的。  
真实结构是：

```text
donor
└─ biological sample
   ├─ technical library A
   ├─ technical library B
   └─ ...
```

一个 library 平均包含约 15.6 个 sample/donor，说明它是 multiplexed technical pool，而非单个生物学样本。

### 统计设计影响

- composition 的生物学单位：`sample_uuid`；
- repeated measure 聚类单位：`donor_id`；
- doublet/QC 的技术单位：`library_uuid`；
- batch representation：`library_uuid`，并保留 `Processing_Cohort`；
- sample 跨多个 library 的 counts 可以在技术一致性确认后聚合；
- sample 跨多个 cohort 时不能粗暴赋一个 cohort 标签。

---

## 3. Common-support 的重新解释

按 sample–cohort 技术记录统计：

| Cohort | Normal samples | SLE samples | Normal B cells | SLE B cells |
|---|---:|---:|---:|---:|
| 1 | 47 | 0 | 23,763 | 0 |
| 2 | 22 | 118 | 10,203 | 60,224 |
| 3 | 18 | 32 | 7,730 | 10,991 |
| 4 | 44 | 51 | 18,529 | 21,541 |

但在“每 donor 一个 sample、且 sample 只属于一个 cohort”的严格子集中，结构仍接近：

| Cohort | Normal | SLE |
|---|---:|---:|
| 1 | 28 | 0 |
| 2 | 1 | 78 |
| 3 | 5 | 15 |
| 4 | 38 | 23 |

因此：

1. cohort 4 是最可靠的直接 case–control stratum；
2. cohort 3 可作探索性 stratum；
3. cohort 1 无 SLE；
4. cohort 2 的 normal 支持主要来自跨 cohort 技术拆分样本；
5. 53 个 bridge samples 对技术批次估计有价值，但不能被当作新增独立生物学重复。

---

## 4. Raw-count QC 结果

全局分布：

| 指标 | Median | 95% | 99% | Max |
|---|---:|---:|---:|---:|
| UMI | 1,926 | 4,006 | 6,246 | 26,048 |
| Detected genes | 643 | 1,131 | 1,669 | 3,952 |
| Mitochondrial % | 3.44 | 6.94 | 10.32 | 59.43 |
| Hemoglobin % | 0 | 0.094 | 0.184 | 4.14 |
| Platelet-marker % | 0 | 0.113 | 0.201 | 0.906 |
| B-lineage markers detected | 6 | 9 | 9 | 10 |

数据明显已经经过来源数据的基础过滤：

- 最低 UMI：403；
- 最低基因数：178；
- 低质量空液滴不是主要问题；
- 高 UMI/高 gene tail 更应作为 doublet 候选，而不是在 Scrublet 之前一刀切删除。

### 旧候选 flag 不能直接作为过滤规则

旧 MAD 诊断平均标记约 37.5% cells，主要因为：

- sample 内 hemoglobin median/MAD 常为 0；
- platelet median/MAD 常为 0；
- 因而任何极低非零表达都会超过阈值。

具体贡献：

| 原因 | 标记比例 |
|---|---:|
| 任意 platelet expression 高于零 MAD threshold | 25.5% |
| hemoglobin expression 高于零 MAD threshold | 10.0% |
| high mitochondrial | 5.6% |
| high genes | 2.35% |
| high counts | 1.77% |

因此 `13/14_*candidate_thresholds.csv` 只能作为诊断产物，**不能直接用于过滤**。

---

## 5. Gate C2A 冻结的保守 hard-QC 起点

Smoke test 建议先使用：

```text
n_counts >= 500
n_genes >= 200
pct_mito <= 10
pct_hb <= 1
pct_platelet <= 0.5
n_blineage_markers_detected >= 1
```

该规则预计仅排除约：

```text
2,579 / 152,981 = 1.69%
```

按 cohort/disease 的预计排除比例约 1.0%–2.7%，没有出现极端单组清除。

### 不在 hard-QC 阶段处理

- high counts；
- high genes；
- immunoglobulin-high cells；
- 低但非零 B-lineage marker cells；
- suspected plasmablasts。

这些必须结合：

- per-library Scrublet；
- cluster-level markers；
- plasma-cell biology；
- contamination scores；

再决定是否排除。

---

## 6. Sample inclusion 规则

原始 sample B-cell 数：

- median：451；
- 22 个 sample 少于 100 cells；
- 51 个 sample 少于 200 cells；
- 低 cell-count sample 在 SLE 中更常见。

因此 composition 不得只使用单一 cell-count threshold。建议：

| 分析 | 规则 |
|---|---|
| Primary composition | ≥100 retained B cells/sample |
| Sensitivity A | ≥50 |
| Sensitivity B | ≥200 |
| Pseudobulk | 由每个 frozen state 的 sample-state cell 数决定 |
| State-specific DE 起点 | ≥20 cells/sample-state，随后做 10/30/50 sensitivity |

按保守 QC、每 donor 一个预设 sample、≥100 B cells，预计保留：

```text
240 donors/samples
Normal = 96
SLE = 144
```

---

## 7. Repeated donor 的预设规则

11 个 repeated donors 均为 SLE，且都有 flare sample。

### Primary case–control

每 donor 仅选一个 sample：

1. 优先 untreated/pre-treatment flare；
2. 若没有 flare，使用预先定义的最早时间点；
3. 绝不能根据 cluster fraction、QC retained cells 或目标基因表达选择 sample。

### Secondary longitudinal

单独分析：

```text
flare → managed
flare → treated
```

使用 donor-paired contrast，不与横断面 case–control 混写。

---

## 8. Gate C2A 为什么先做 20,000-cell smoke test

不能立即对 152,981 cells 启动全量正式分析，因为需要先验证：

1. `raw/X` 能否无损重建新的 AnnData；
2. per-library Scrublet 是否在 88 个 library 中稳定；
3. library-aware HVG 是否保留 B-cell biology；
4. unintegrated PCA 与 Harmony representation 的差别；
5. Harmony 是否过度消除真实状态结构；
6. 多分辨率 Leiden 的 cluster 数、sample/donor coverage；
7. atypical/plasmablast/memory/naive markers 是否出现；
8. 污染细胞是否形成独立 cluster；
9. 疾病字段是否确实没有参与 clustering。

Gate C2A 只用于方法验证，不产生论文主结果。

---

## 9. Gate C2A 的 Go/No-Go

### GO to full Gate C2B

必须满足：

- ≥95% libraries 的 Scrublet 成功；
- hard-QC 后无 library 大规模异常清除；
- 主要 clusters 覆盖多个 sample/donor/library；
- naive、memory、atypical、plasmablast markers 可以解释；
- Harmony 降低 library segregation，但没有压平稀有状态；
- resolution 0.4–1.0 之间主要生物结构稳定；
- 未查看 disease 后即可冻结初步 neutral cluster framework。

### NO-GO / 需要调整

若：

- Harmony 把全部状态混成连续云；
- atypical cluster 只由单 library/sample 组成；
- Scrublet 在大量 library 失败；
- QC 主要清除某 cohort；
- marker genes 在 feature_name 中异常缺失；
- 结果强依赖单一 resolution。

---

## 10. 当前阶段判断

> Gate C1 已经解决“输入是否真实、raw count 是否存在、样本层级是否冲突”的问题。结果支持继续推进，但也进一步证明 library/cohort 技术结构复杂，不能沿用旧 donor-level 折叠策略。

下一步应运行 Gate C2A smoke test，而不是继续修改 v6 图件或手稿。
