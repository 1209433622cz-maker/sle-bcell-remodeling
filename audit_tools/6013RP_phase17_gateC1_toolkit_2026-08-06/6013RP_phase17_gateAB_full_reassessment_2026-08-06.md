# 6013RP-wyf Phase 17 Gate A/B 全量复核报告

- 项目：SLE 外周血 B 细胞单细胞转录组
- 本地项目：`H:\cuhk-2025fALL\6013RP-wyf`
- 复核对象：Phase 17 H5AD 审计 + 542 文件紧凑科学审阅包
- 复核日期：2026-08-06
- 角色：生物信息学博士生导师 / 论文与统计方法全量质控
- 决策：**Gate A/B 通过；v6 直接投稿不通过；进入 Gate C 原始计数层重构**

---

## 一、最终执行结论

本次全量复核修正了早期基于精简上传包形成的“本地缺失 Data、02_analysis、03_results 和阶段脚本”判断。真实本地项目已经具备：

- 完整 `Data`；
- 完整 `02_analysis`，脚本链覆盖 `01_check_scanpy_env.py` 至 `49_build_cover_letter.py`；
- 完整 `03_results`；
- 9 个可读取 H5AD；
- 最新 v6 手稿、主图、补充材料和投稿工程文件；
- discovery、GSE135779、GSE163121、OneK1K 和 regulatory evidence 分支。

因此，项目不是“缺数据、无法重跑”，而是：

> **数据和代码资产基本齐备，但核心分析设计、样本层级、批次共同支持、状态内疾病差异和独立状态复现尚未形成一区论文所需的闭环。**

### 投稿决定

| 决策项 | 结论 |
|---|---|
| 继续润色 v6 并直接投稿 | **NO-GO** |
| 冻结 v6 作为历史基线 | **GO** |
| 从 discovery 原始计数层重跑 | **GO** |
| 现有图仅做排版微调 | **NO-GO** |
| 重构中心科学问题与 5 张主图 | **GO** |
| Genome Medicine 作为当前直接投稿目标 | **暂缓，v7 完成后再评估** |
| Nature Communications | **仅在跨队列组成效应、状态内转录效应和冻结映射验证均成功时作为 stretch target** |

---

## 二、已经确认的原始资产

### 2.1 Discovery 数据

权威重跑入口：

```text
Data/processed/GSE174188_perez_cellxgene/bcell_subset_full.h5ad
```

- 细胞数：152,981
- 基因数：30,172
- donor：259
- sample：271
- library：88
- processing cohort：4
- disease：
  - Normal：99 donors
  - SLE：160 donors
- `raw/X`：非负、抽样值 100% 整数型，符合原始 UMI count 特征
- `X`：存在负数，属于标准化/缩放表达空间
- 现有 `X_pca`、`X_umap`：继承自来源 PBMC 对象

### 2.2 现有 first-pass 对象

```text
03_results/first_pass_bcell_full/bcell_first_pass_processed.h5ad
03_results/first_pass_bcell_full/bcell_first_pass_labeled.h5ad
```

- 细胞数和基因数与 discovery B-cell subset 相同；
- `raw` 已被清除；
- `X` 为含负数的缩放矩阵；
- 不能作为 Phase 17 主重跑入口。

### 2.3 外部数据

| 数据 | 规模 | 适用角色 |
|---|---:|---|
| GSE135779 | 32,179 B cells；16 HC + 40 SLE donor/sample names | 主独立验证 |
| GSE163121 | 25,037 B cells；2 HC + 3 SLE | 方向性补充验证 |
| OneK1K | 1,248,980 cells；981 健康 donor | 健康参考，不是疾病复现 |

---

## 三、现有分析链的决定性问题

## 3.1 现有 B 细胞空间不是从 B 细胞原始计数重新建立

`03_scanpy_bcell_first_pass.py` 在检测到负值后进入 `preprocessed` 模式：

- 若存在 `X_pca`，直接用来源对象 `X_pca` 建邻居图；
- 若已有 `X_umap`，保留来源 UMAP；
- 未重新完成 B-cell-specific HVG、PCA、邻居图和 UMAP；
- 最终设置 `adata.raw = None`。

这意味着现有 Figure 2 的“B-cell atlas”本质上是：

> 在全 PBMC 来源降维空间中截取 B-lineage，再进行邻居重建和 Leiden 分群。

它可以用于探索，但不足以支撑以 B 细胞精细状态发现为核心的一区论文。

**必须重跑：**
原始 count → B-cell QC → HVG → PCA → unintegrated/batch-aware representation → neighbors → Leiden/UMAP。

---

## 3.2 “ABC-like state discovery”与来源注释高度重合

现有 cluster 5：

- 非缺失 `ct_cov` 细胞中 79.9% 已被来源数据标为 `B_atypical`；
- 按 cluster 全部细胞计算，约 70.8% 为 `B_atypical`；
- 11.4% `ct_cov` 缺失；
- 其 ABC/DN2 signature 最高。

因此，现稿中的“identify an ABC/APC-like state”容易被审稿人理解为发现新的状态，但实际更接近：

> 在来源数据已有 atypical B 注释基础上，重新聚类并给该群增加 APC/HLA 程序描述。

这不否定该群的生物学意义，但明显削弱“atlas”“identify”“novel state”的新颖性。

---

## 3.3 状态命名使用疾病结果，存在解释循环

现有 cluster annotation evidence 包含：

- donor fraction 是否在 SLE 中升高；
- 标签 `Naive B II / SLE-enriched naive-like`；
- Figure label `SLE-naive-like`；
- focus state 的选择部分依赖疾病差异。

聚类边界本身并非由疾病标签直接监督生成，但“命名—选焦点—再检验疾病差异”的链条会造成解释性 double-dipping。

### v7 要求

1. 聚类和初始注释阶段隐藏：
   - disease
   - disease_state
   - SLEDAI
   - treatment
2. 仅使用：
   - marker expression
   - reference mapping
   - neutral state terminology
3. 冻结标签后再解锁疾病信息。
4. 旧 `ct_cov` 仅用于外部一致性评估，不作为新发现本身。

建议中性命名：

- Resting naive-like
- Activated naive-like
- Memory-like I
- Memory-like II
- Mixed/transitional
- Atypical FCRL5/ZEB2-positive
- Plasmablast/ASC
- QC-flagged contaminant-like

---

## 3.4 donor、sample、library 和 cohort 层级未被正确分离

Discovery 包含：

- 259 donor
- 271 sample
- 88 library
- 4 processing cohort
- 11 donor 有多个 sample
- 11 donor 有多个 disease_state
- 56 donor 跨多个 processing cohort

现有 abundance 流程把 donor 内多个值折叠为：

- `Processing_Cohort_simple = multiple`
- `disease_state_simple = mixed`

这会丢失纵向和技术层级信息。

### 正确统计单位

| 层级 | 角色 |
|---|---|
| `sample_uuid` | 主要生物学实验单位 |
| `donor_id` | 受试者/重复测量聚类单位 |
| `library_uuid` | 技术批次 |
| `Processing_Cohort` | 处理/队列分层 |
| cell | 测量单位，不是独立统计重复 |

主分析应以 sample-level composition 和 sample-state pseudobulk 为基础；重复 donor 通过基线样本规则、混合模型或 cluster-robust inference 处理。

---

## 3.5 processing cohort 与 disease 存在严重共同支持问题

donor-level cross-tab：

| Processing cohort | Normal | SLE |
|---|---:|---:|
| 1 | 28 | 0 |
| 2 | 1 | 87 |
| 3 | 5 | 16 |
| 4 | 41 | 25 |
| multiple | 24 | 32 |

这说明：

- cohort 1 没有 SLE；
- cohort 2 仅 1 个 normal；
- 主要可直接比较的单一 cohort 是 cohort 4；
- cohort 3 样本较少；
- `multiple` 组不是一个真实处理队列。

现有 full-adjusted OLS 加入 cohort dummy 不能自动解决 lack of common support；模型可能依赖跨队列外推。

### 已有结果的合理解释

现有方向在 cohort 4 和部分其他分层中仍一致：

- Activated naive-like：cohort 4 SLE-HC mean difference约 +0.160；
- Memory-like I：cohort 4约 −0.081；
- ABC-like：cohort 4约 +0.019。

这说明信号可能真实，但必须改为：

1. cohort 内效应；
2. 可比较 cohort 的 meta-analysis；
3. leave-one-cohort-out；
4. 重复 donor 敏感性；
5. compositional model。

---

## 3.6 现有 abundance 分析不是正式 compositional model

现有流程包括：

- donor fraction + Mann–Whitney；
- OLS + HC3；
- donor-wise CLR + OLS；
- pseudocount sensitivity。

这些是有价值的敏感性分析，但不是 scCODA、sccomp、Dirichlet-multinomial 或 beta-binomial 组成模型。

### 当前三条核心方向

| 状态 | Raw mean difference | Full-adjusted fraction beta | Full-adjusted CLR方向 |
|---|---:|---:|---|
| Activated naive-like | +0.1456 | +0.1491 | 正 |
| Memory-like I | −0.1014 | −0.0999 | 负 |
| ABC/APC-like | +0.0291 | +0.0175 | 正 |

排除多 sample donor 后方向仍保持；但这只能支持“信号稳健候选”，不能替代 cohort-resolved composition inference。

---

## 3.7 现有 pseudobulk 回答了错误的问题

`19_pseudobulk_state_expression.py`：

- 按 donor × disease × disease_state × refined_state 聚合；
- 仅汇总预设 marker/program；
- 将 ABC/APC focus state 与同 donor 的其他状态平均比较；
- 使用 paired Wilcoxon。

它回答的是：

> “该状态与其他 B 细胞状态有何不同？”

而不是：

> “在同一状态内部，SLE 相对于 HC 发生了哪些转录变化？”

因此现稿不能把它作为状态内疾病 pseudobulk DE。

### v7 必须增加

- raw count genome-wide aggregation；
- `sample_uuid × frozen_state`；
- 每个状态中 SLE-vs-HC；
- edgeR quasi-likelihood / muscat；
- cohort、age、sex、ethnicity 和重复 donor 处理；
- GSEA、TF activity 从正式 DE 结果产生。

---

## 3.8 现有独立验证没有映射 discovery 状态

GSE135779 当前验证：

- 选择元数据中的 B-cell subclusters；
- 在全部 B cells 中计算手工 curated program scores；
- `ABC/APC-high` 阈值使用验证数据自身 HC 细胞的 95% 分位数；
- 未使用 discovery 冻结 centroid/classifier；
- 未执行 label transfer；
- 未复现同一状态的 abundance 或状态内 DE。

### GSE135779 实际结果

| 指标 | SLE-HC delta | FDR | 判断 |
|---|---:|---:|---|
| IFN/ISG | +0.2810 | 0.000872 | 稳健复现 |
| ZEB2/TBX21/ITGAX | +0.0351 | 0.0448 | 边界支持 |
| Plasmablast/ASC | +0.0246 | 0.0448 | 支持 |
| ABC/APC-high fraction | +0.0567 | 0.0788 | 趋势 |
| ABC/DN2 core | +0.0370 | 0.1086 | 未通过 |
| ABC/APC focus | +0.0425 | 0.1754 | 未通过 |
| APC/HLA | +0.0342 | 0.3491 | 未通过 |
| HLA/CD74 | +0.0144 | 0.8349 | 未通过 |

因此现有证据只允许写：

> GSE135779 robustly reproduced interferon activation and provided limited directional support for an atypical-B-cell-associated ZEB2/TBX21/ITGAX axis.

不允许写：

> Independent validation identified or confirmed an expanded ABC/APC-like state.

---

## 3.9 GSE163121 与 OneK1K 的定位需要降级

### GSE163121

- 2 HC + 3 SLE；
- 所有 FDR ≥ 0.5；
- 只能作为方向性补充；
- 不能承担验证结论。

### OneK1K

- 全部为健康 donor；
- 可用于健康参考分布、reference mapping 或 annotation；
- 不能复现 SLE disease effect；
- 建议移至补充材料或从核心论文删除。

---

## 3.10 regulatory evidence 当前为阴性/不可判定

`bcell_colocalisation_primary.csv` 的 19 行主分析全部为：

```text
insufficient_shared_variants
```

因此：

- 不存在可报告的正向 colocalization；
- 不能用于机制闭环；
- 可作为补充方法探索或删除；
- 不应占据主图。

---

## 四、现有手稿的逻辑重构

## 4.1 旧主线

```text
单细胞 atlas
→ ABC/APC-like state
→ donor abundance
→ pseudobulk support
→ literature signatures
→ independent validation
```

主要问题：

- atlas 新颖性弱；
- 状态与来源注释高度重合；
- abundance 受 cohort confounding；
- pseudobulk 不是真正 disease DE；
- validation 未映射状态；
- signature panel 证据重复。

## 4.2 新主线

```text
样本与队列层级审计
→ B-cell-specific de novo state reconstruction
→ disease-blind state definition
→ cohort-resolved composition effects
→ state-internal SLE transcriptional effects
→ composition与transcription的分离
→ frozen mapping external replication
```

中心问题：

> SLE B-cell remodeling究竟主要表现为细胞状态组成变化，还是同一状态内部的疾病相关转录激活？这些效应能否在处理队列内部及独立队列中复现？

推荐暂定标题：

**Donor- and cohort-resolved single-cell analysis separates compositional and transcriptional B-cell remodeling in systemic lupus erythematosus**

最终状态名称必须在 v7 结果冻结后决定。

---

## 五、Nature 风格主图重构

## Figure 1：Study design, hierarchy and common support

必须包含：

- discovery/validation 数据与纳入流程；
- donor–sample–library–cohort 层级图；
- cohort × disease common-support mosaic；
- repeated donor 结构；
- analysis DAG；
- QC 流失表。

禁止：

- 大段 workflow 文字框；
- 把 guardrails 当主结果；
- 过多细小文本。

## Figure 2：De novo B-cell landscape and neutral state definition

必须包含：

- B-cell-specific UMAP；
- unintegrated vs batch-aware representation 对照；
- neutral state labels；
- canonical marker dot plot；
- reference-label concordance；
- multi-resolution stability；
- sample/cohort mixing QC。

## Figure 3：Cohort-resolved compositional remodeling

必须包含：

- sample-level state proportions；
- cohort-specific forest plot；
- random-effects/meta-analysis；
- leave-one-cohort-out；
- compositional model posterior/effect；
- repeated donor sensitivity。

## Figure 4：State-internal transcriptional remodeling

必须包含：

- state-specific SLE-vs-HC pseudobulk volcano/forest；
- pathway enrichment；
- TF activity；
- composition effect vs transcription effect 二维图；
- 明确区分“状态增加”与“状态内激活”。

## Figure 5：Frozen external mapping and replication

必须包含：

- discovery classifier/centroid 冻结流程；
- GSE135779 mapping confidence；
- mapped state abundance；
- state-internal replicated pathways；
- IFN、atypical axis 和 plasmablast signal；
- discovery–validation effect correlation。

### 补充材料

- GSE163121；
- OneK1K；
- 旧 curated signature panels；
- QC-flagged cluster；
- regulatory evidence；
- 全部 pseudocount 和 resolution sensitivity。

---

## 六、现有资产保留与重跑矩阵

| 模块 | 处理 |
|---|---|
| 原始 H5AD、raw counts | 保留，作为权威输入 |
| 数据下载与 inventory | 保留 |
| 环境文件 | 升级并冻结 |
| source-data 追踪框架 | 保留 |
| publication figure style helper | 保留并重构图 |
| first-pass UMAP/Leiden | 仅作为历史敏感性 |
| 现有 disease-informed labels | 废弃为主标签 |
| donor fraction/MW/OLS/CLR | 保留为补充敏感性 |
| abundance 主分析 | 重跑 |
| marker-focused paired pseudobulk | 改名为 state-identity contrast，移补充 |
| genome-wide state-internal DE | 新增 |
| GSE135779 program scoring | 保留为补充 |
| frozen state mapping | 新增 |
| GSE163121 | 降级 |
| OneK1K | 降级或删除 |
| regulatory colocalization | 移补充或删除 |
| v6 manuscript | 冻结 |
| 主图 1–6 | 全部重构 |

---

## 七、下一阶段 Gate C

### Gate C1：输入冻结、样本层级和 raw-count QC

目标：

1. 冻结权威 H5AD 路径和 SHA-256；
2. 导出 sample/donor/library/cohort manifest；
3. 标记 repeated donor 和 disease-state changes；
4. 建立 cohort common-support 表；
5. 计算 raw-count QC 分布；
6. 生成 sample-aware 候选阈值，但暂不自动删除细胞。

交付物：

```text
_phase17_gateC1/YYYYMMDD_HHMMSS/
```

### Gate C2：B-cell de novo 重聚类

开始条件：

- Gate C1 metadata 无重大不可修复冲突；
- raw/X 确认为 counts；
- QC 规则经审阅；
- 环境和内存评估通过。

### Gate C3–C7

- C3：盲法注释与稳定性；
- C4：composition；
- C5：state-internal DE；
- C6：external mapping；
- C7：手稿与图组重写。

---

## 八、Go/No-Go 标准

### 允许进入 v7 投稿写作

至少满足：

1. B-cell-specific de novo embedding；
2. neutral frozen annotation；
3. cohort 4 或其他有共同支持队列中方向一致；
4. compositional model 支持主要状态；
5. 每个主状态有足够 sample-state pseudobulk；
6. 至少一个关键状态内疾病程序在 GSE135779 方向一致并通过预设检验；
7. discovery–validation 不使用验证集重新拟合阈值；
8. 主图全部显示 effect size、CI、sample points 和 cohort heterogeneity。

### 应降级论文目标或改变主线

若：

- atypical state 在 de novo analysis 不稳定；
- composition effect 仅由无共同支持 cohort 驱动；
- state-internal DE 无稳定信号；
- external mapping 无法复现 atypical state；
- 最终仅 IFN program 稳健。

此时应把主线改为：

> cohort-aware dissection of interferon-linked B-cell remodeling

而不是 ABC/APC state discovery。

---

## 九、综合评分

| 维度 | v6 当前状态 | v7 目标 |
|---|---:|---:|
| 数据资产 | 8.5/10 | 9/10 |
| 可重复性工程 | 7/10 | 9/10 |
| 生物学问题 | 6/10 | 8.5/10 |
| 聚类与状态定义 | 4/10 | 8.5/10 |
| 统计设计 | 4/10 | 8.5/10 |
| 独立验证 | 3.5/10 | 8/10 |
| 图件技术质量 | 7/10 | 9/10 |
| 图件科学表达 | 5/10 | 9/10 |
| 当前投稿成熟度 | 4.5/10 | — |

**导师级最终判断：**

> 项目值得继续，且本地资产足以支持高质量重构。当前最优策略不是修补 v6，而是把 v6 冻结为探索性基线，从 `bcell_subset_full.h5ad::raw/X` 开始重建样本层级、B-cell state、组成效应、状态内疾病效应和冻结验证。只有这样才有机会达到 SCI 一区水平。
