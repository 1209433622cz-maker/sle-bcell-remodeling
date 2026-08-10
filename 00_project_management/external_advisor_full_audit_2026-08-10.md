# 6013RP-wyf 论文项目博士生导师级全量核查与下一阶段重构报告

**审计日期：** 2026-08-10  
**审计对象：** 用户上传 `6013RP-wyf(2).zip`  
**审计角色：** 生物信息学 / 单细胞转录组方向博士生导师级方法学与论文质控  
**当前结论：** **NO-GO for submission；继续 Phase 17 / v7 重分析。**

---

## 1. 总体判断

这个项目目前已经从“对旧 v6 稿件做投稿前润色”进入了“重新定义统计对象和证据链的 v7 重构阶段”。这一变化是正确的，而且是项目当前最重要的进步。

旧 v6 的主要问题不是排版或英文表达，而是推断对象和分析层级存在根本性风险：继承 PBMC 全局表示而非在 B 细胞内重建状态；部分状态命名含有疾病信息；processing cohort 与疾病状态缺乏全局 common support；重复生物样本被 donor 聚合；旧 pseudobulk 对比实际检验的是“某状态 vs 其他状态”而非“同一状态内 SLE vs control”；外部验证没有真正转移被冻结的 discovery state。

v7 已将核心问题收敛为：

> **SLE 对外周 B 细胞的重塑，是主要通过改变中性 B-cell states 的相对组成、改变相同 state 内部的转录程序，还是二者同时发生；这些效应能否跨 cohort / 外部队列复现？**

这是一个比旧“ABC/APC-like 致病亚群”叙事更稳健、更可证伪、也更容易形成高质量论文的核心问题。

---

## 2. 本次压缩包实际可核查范围

上传包共约 610 MB，顶层只有：

- `00_project_management`
- `01_manuscript`
- `02_analysis`
- `04_submission`

本包中 **没有 `03_results`、没有 Data、没有任何 H5AD、没有 `phase17_v7` 活跃结果目录、也没有最新 `audit_tools` 运行目录**。因此本次可以做到：

1. 对项目管理文档、v6/v7 manuscript 逻辑、方法学设计、脚本静态质量、旧图件、v7 图件架构和投稿包进行全量交叉核查；
2. 对 8 月 10 日文档中记录的 Phase 17 数值和 Gate 状态进行一致性评估；
3. 不能仅依据这个 ZIP 对 150,402-cell v7 活跃 H5AD 和 Gate C2B1/C2B2 结果做独立数值复算。

这构成当前项目归档与可复现性的一个明确缺口，应在下一版 review pack 中补齐。

---

## 3. 当前已确认的 authoritative discovery 设计

项目最新审计文档记录的 discovery source 为 `bcell_subset_full.h5ad` 的 `raw/X`：

- 152,981 B-lineage cells
- 30,172 genes
- 259 donors
- 271 biological samples
- 88 technical libraries
- 4 processing cohorts
- 11 donors 有重复 biological samples
- 53 biological samples 跨 processing cohorts

v7 hard-QC 后记录为 150,402 cells × 30,172 genes，并已将 `disease` / `disease_state` / `ct_cov` 从工作 AnnData 中物理移除，避免在 state reconstruction 阶段被使用。

这一“保护 outcome → 先冻结 representation/state → 再解锁疾病变量”的方向是正确的。

---

## 4. common support 是论文统计设计的决定性约束

在严格的 ambiguity-free biological subset（每 donor 仅一个 sample 且只属于一个 processing cohort，n=195）中：

| Processing cohort | Normal | SLE | 允许的推断 |
|---|---:|---:|---|
| 1 | 28 | 0 | state discovery / technical QC only |
| 2 | 1 | 87 | 不支持可信直接疾病比较 |
| 3 | 5 | 8 | exploratory replication |
| 4 | 41 | 25 | **primary disease comparison** |

因此不能再使用“所有 cohort pooled + cohort dummy”来产生一个全局疾病系数。缺乏组间 overlap 是设计问题，不是加协变量就能修复的问题。

**论文主推断必须锚定 cohort 4；cohort 3 只能作为探索性方向复核；cohort 1/2 只能参与状态发现、技术稳定性和其他不依赖病例-对照对比的工作。**

---

## 5. 旧 v6 为什么不能继续直接投稿

### 5.1 表示空间不是 B-cell de novo reconstruction

v6 继承来源 PBMC 的 PCA/UMAP。它可以用于描述，但不足以证明 B-cell compartment 内的状态结构是由本项目从 raw counts 独立重建并稳定复现的。

### 5.2 outcome-informed state 命名造成 double dipping

如 `SLE-naive-like` 这种标签把疾病信息嵌入状态定义，再对该状态做疾病比较，推断上存在循环性。v7 必须使用疾病盲、中性标签并在 outcome unlock 前冻结。

### 5.3 统计单位处理错误

旧 donor-level aggregation 会合并同一 donor 的重复 biological samples。应以 biological sample 为疾病效应的基本单位，donor 用随机效应或其他相关结构处理；technical library 不是独立生物重复。

### 5.4 旧 pseudobulk 回答了错误的问题

`focus state vs mean(other states)` 主要检验 state identity。真正的疾病转录效应应当是：**在冻结的同一 state 内，sample-level SLE vs control raw-count pseudobulk。**

### 5.5 外部验证叙事超过了证据

旧 GSE135779 工作更可靠地支持 interferon activity，ZEB2 等轴的证据相对有限；且没有把 discovery 中冻结的状态直接映射到 validation dataset，validation threshold 也曾在外部数据内部重新计算。它不能被称为独立复制了一个“扩增的 ABC/APC-like state”。

因此旧图、旧 numerical-QC 即使技术上全部通过，也只能说明“旧分析结果可追溯”，不等于“旧统计推断有效”。

---

## 6. 当前 Gate 状态

| Gate / 模块 | 当前状态 | 导师判断 |
|---|---|---|
| Source/raw-count hierarchy audit | PASS | 基础可靠 |
| Gate C2A smoke representation | GO | 支持进入全数据分析 |
| Smoke Scrublet calls | NO-GO for freeze | 不能作为最终 doublet 决策 |
| Gate C2B-01 full hard-QC raw prep | PASS | 已具备全数据入口 |
| Gate C2B1 complete-library residual doublet review | **PENDING** | 当前最高优先级 |
| Gate C2B2 full disease-blind representation | PENDING | 不应提前做疾病推断 |
| Gate C2B3 neutral state freeze | PENDING | 决定后续所有生物学结果 |
| Gate C3 composition | PENDING | v7 主结果尚未生成 |
| Gate C4 within-state transcription | PENDING | v7 主结果尚未生成 |
| Gate C5 frozen external validation | PENDING | v7 外部证据尚未建立 |
| Manuscript final Results / Discussion | PENDING | 不能从 v6 直接继承 |
| Submission | **NO-GO** | 当前不应投稿 |

---

## 7. Gate C2B1：doublet 策略必须做的一次关键修订

原 Perez 数据的上游流程已经使用 Freemuxlet 进行 donor assignment，并结合 Scrublet 去除 doublets。因此 v7 当前完整 library Scrublet 应首先被解释为 **residual doublet-risk diagnostic**，而不是重新执行一次无条件的第二轮 doublet 删除。

建议 C2B1 保留两个并行分支：

- `all-hard-QC` 主分支；
- `high-confidence-singlet` sensitivity 分支。

最终是否删除某一类细胞，应综合：原始 source doublet provenance、当前 Scrublet score/threshold、library loading、nUMI/nGene、mixed-lineage markers、cluster localization，而不是仅靠一个 global threshold。

尤其对于 activated/transitional B-cell states，过强双细胞过滤可能反而删掉真实高 RNA / 高活化状态。

---

## 8. 另一个必须冻结的设计：53 个 bridge samples

53 个 biological samples 跨 processing cohorts，是当前最容易被审稿人抓住、但也最有机会转化为优势的结构。

### 主疾病模型

建议 primary disease inference 只使用 **strict single-processing-cohort biological samples**。跨 cohort 的 bridge sample 不参与决定性疾病系数，避免 cohort 归属不唯一。

### 技术验证

bridge samples 应被主动利用为天然技术重复，用于检验：

- state fraction 跨 processing cohort 一致性；
- pseudobulk expression correlation；
- frozen state assignment concordance；
- Harmony 前后技术批次偏差变化；
- ICC / Bland–Altman / rank correlation 等技术稳定性。

如果这些结果好，Figure 2 或 Extended Data 中将形成一个很强的“同一样本跨处理批次可重复”的技术证据层。

---

## 9. Disease-blind clustering 仍需防止“隐性 disease-driven state”

把 disease labels 隐藏并不自动等于没有 circularity。如果强 IFN/stress genes 本身主导 HVG 和 clustering，最终得到的 state 仍可能主要是“疾病响应强度层级”。

建议增加一个预注册 sensitivity：

- primary HVG：library-aware recurrent HVG；
- 排除 mitochondrial / ribosomal / stress / cell-cycle 等 nuisance genes；
- immunoglobulin-dominance 进行敏感性检查；
- 增加“去除强 ISG module 后重建 state”的 identity-stability sensitivity；
- 可再做一个 control-reference 或 outcome-blind anchor sensitivity，检验 SLE 细胞映射到同一中性 state framework 后结论是否保持。

目标不是把疾病生物学“校正掉”，而是证明主 state identity 不是单纯由疾病激活程序定义。

---

## 10. B-lineage extraction completeness 建议补做

当前分析以来源注释后的 B-lineage subset 为起点。审稿人可能质疑：是否有 atypical / activated B-like cells 在全 PBMC 注释阶段被错误分到其他 lineage，从而人为改变 B-cell composition？

建议从完整 PBMC source 做一次轻量 QC：

- 在所有 PBMC 中计算 B-cell marker/reference score；
- 检查 source B/plasmablast 标签之外是否存在明显 B-like population；
- 若极少，作为 Extended Data / Methods QC；
- 若显著，则需重新定义 B-lineage extraction。

这是一次性完整性检查，不需要把整篇论文改成全 PBMC atlas。

---

## 11. Composition 分析的推荐最终合同

主问题是相对组成，而非绝对细胞计数，因此写作中应使用 **relative abundance / compositional shift**，除非有外周血绝对计数证据，否则避免直接写“absolute expansion/depletion”。

推荐：

- biological unit：sample；
- primary：strict cohort 4；
- exploratory：strict cohort 3；
- per-state model：beta-binomial mixed model / sum-constrained beta-binomial，donor repeated measure 用 random intercept；
- global composition test：同时检验多状态组成改变；
- sensitivity：one-sample-per-donor、不同 min-cell threshold、all-hard-QC vs singlet sensitivity、CLR/scCODA/sccomp；
- 报告 effect size + 95% CI/credible interval + multiplicity correction，而不是只报 P 值。

协变量应先画 DAG 决定。age/sex/ancestry 可以考虑，但不要机械调整可能是疾病后果的变量（如治疗、疾病活动），否则可能产生 overadjustment。处理批次在 primary 设计中以 restriction 解决，而不是继续用参数“修掉”。

---

## 12. Within-state pseudobulk 的推荐最终合同

建议以 raw counts 在 `sample × frozen_state` 层面聚合，technical library contributions 先在同一 biological sample 内求和。

推荐主框架：dreamlet/voom mixed model 或 edgeR QL；重复 donor 用 donor random effect/correlation；cohort 4 primary，cohort 3 exploratory。

必须预先冻结：

- 每个 sample-state 的最低细胞数；
- 每个 state 最低病例/对照 sample 数；
- rare-state 的降级规则（例如 descriptive only）；
- FDR family；
- covariate set；
- influential sample diagnostics。

建议图中明确区分四层证据：

1. state marker；
2. disease DE within state；
3. pathway / gene-set activity；
4. candidate regulator。

不要再把 state marker 当作 disease mechanism。

---

## 13. 外部验证应从“signature confirmation”升级为真正 frozen transfer

GSE135779 本身包含两个明显不同的 validation strata：childhood SLE 33 vs 11 control；adult SLE 8 vs 6 control。最强方案不是把 56 个样本直接混在一个总体比较里，而是：

1. discovery 内训练/freeze mapper；
2. donor-stratified CV，并设 uncertainty/abstention；
3. external mapping 完全不使用 disease label；
4. childhood 和 adult 分层估计 abundance / within-state signature effect；
5. 比较方向一致性，必要时做 meta-analysis；
6. 对无法可靠映射的 state 明确报告 negative/uncertain result。

若 exact state transfer 很弱，不要强行宣称 state replication，可退回“program-level replication”。这种诚实降级反而更可信。

GSE163121 继续只作方向性参考；OneK1K 只能做 healthy reference context，不是 SLE disease validation。

---

## 14. 高价值增强项：重复 donor 的纵向/配对分析

项目已有 11 个 repeated donors。若其中包含 flare / treatment-follow-up 等时间点，建议在主 v7 结果冻结后做一个严格的 secondary paired analysis：

- paired state composition change；
- paired within-state IFN / atypical-B program change；
- paired effect-size plot；
- donor connecting lines；
- 不把其解释为治疗因果效应，因为 time、activity、treatment 可能共同变化。

这种 within-person evidence 的价值通常高于再增加一个随机公共数据库，因为它对个体间异质性天然控制，且能增加“动态疾病重塑”的故事深度。

---

## 15. 推荐的 manuscript 结构

当前 v7 blueprint 的证据顺序正确，但建议把“Robustness and generalizability boundaries”不要单独放成第 6 个主 Results 章节，而是让 robustness 与每个核心结果绑定，剩余边界放入 Discussion / Extended Data，以避免主文尾部失去生物学高潮。

### Introduction（3 段即可）

1. SLE 中 B-cell remodeling 的生物学重要性；
2. 当前文献无法清晰区分 composition change 与 state-internal transcription，并且单细胞研究容易受到 pseudoreplication / technical cohort / outcome-informed state 的影响；
3. 本研究采用 outcome-locked、cohort-resolved、sample-aware framework 回答这两个层次是否独立发生以及能否外部复现。

### Results（5 个主章节，对应 5 个主图）

1. Study hierarchy defines valid disease contrasts；
2. Disease-blind reconstruction yields stable neutral B-cell states；
3. Cohort-resolved SLE compositional remodeling；
4. Within-state transcriptional remodeling is distinct from abundance；
5. Frozen external mapping separates reproducible from cohort-specific effects。

### Discussion

第一段直接回答 process-level finding；然后解释 composition vs transcription 的生物学意义；再讨论外部复现/不复现的边界；接着讨论 bridge samples / technical hierarchy 对单细胞疾病研究的启示；candidate regulator 只作 hypothesis；最后写公开观察性数据、治疗、ancestry、source extraction 等限制和未来功能实验。

---

## 16. Title 建议

现工作标题已经合格：

**Donor- and cohort-resolved single-cell analysis separates compositional and transcriptional B-cell remodeling in systemic lupus erythematosus**

若 v7 最终同时获得强 composition + transcription + external replication，可进一步压缩成：

**Systemic lupus erythematosus remodels B cells through separable compositional and transcriptional programs**

标题不要在 Freeze D 前写入具体 ABC/APC-like、ZEB2/TBX21 或机制性动词。

---

## 17. Nature-style 图件总规范与当前脚本问题

项目 v7 figure architecture 已基本对齐 Nature 的宽度、字体和色板思路：183 mm 双栏、≤170 mm 高、Arial/Helvetica、5–7 pt 正文字、8 pt 小写粗体 panel label、白底、可访问色板、Type 42 字体。

但 `50_make_v7_figure1_study_design.py` 仍有几处需要修：

- retention panel 存在 background x-grid，应去掉；
- 多处使用彩色文字（percentage、Primary/Exploratory、bridge annotation），严格 Nature 风格应改为黑/白文字 + 彩色符号/keyline；
- workflow 的淡色背景盒可以保留功能性结构，但应减少装饰感；
- retention x-axis 仅 96.5–100%，视觉上会夸大很小的 QC 差异，建议换成 excluded fraction 或更中性的展示；
- main figure 应优先提交可编辑 vector PDF/EPS；PNG 适合作 QC preview，不应把多面板主图最终扁平化成 PNG。

---

## 18. 五个主图的最终设计建议

### Figure 1 — Study design / hierarchy / common support

不放 UMAP。核心是：outcome lock、donor-sample-library-processing hierarchy、bridge samples、strict common support、primary/exploratory strata。它是统计可信度的“立论图”。

### Figure 2 — Disease-blind B-cell state reconstruction

主图只放真正决定 state freeze 的内容：unintegrated vs Harmony、neutral state UMAP、marker dotplot、stability/coverage。大部分 doublet diagnostics 放 Supplement。若 bridge sample concordance 很强，可用一个 panel 取代过多 doublet QC，使 Figure 2 更有技术亮点。

### Figure 3 — Composition

必须以 sample-level effect 为中心，不以 cell number 制造视觉优势。建议：样本组成 overview + primary state effect forest + selected raw sample dots + cohort3 direction replication + method sensitivity matrix。

### Figure 4 — State-internal transcription

避免多个重复 volcano。更推荐：state × gene/pathway effect-size heatmap + top pathway forest + regulator evidence + composition-vs-transcription quadrant。把“identity marker”和“disease DE”彻底分开。

### Figure 5 — Frozen external validation

展示 mapper calibration / abstention、external mapping quality、childhood/adult stratum effect、directional replication/meta-effect 和 replication scorecard。明确把 negative findings 也放进 scorecard。

---

## 19. Supplementary / Extended Data 建议

建议保持 S1–S8 左右，但每张只承担一个质控问题：

- S1 source hierarchy / metadata audit
- S2 QC + residual doublet diagnostics
- S3 HVG / integration / batch sensitivity
- S4 clustering resolution / resampling stability
- S5 composition model sensitivity
- S6 pseudobulk diagnostic / alternative model
- S7 external mapping calibration / uncertainty
- S8 negative evidence / regulator / extra cohort / paired-donor secondary analysis

旧 v6 Figures 1–6 不应直接“换标题复用”；只允许复用绘图代码结构和视觉语言，所有主 panel 应从冻结的 v7 source tables 重生成。

---

## 20. 当前代码与可复现性审计

`02_analysis/scripts` 共有 52 个 Python 脚本，本次静态 `py_compile` 检查全部通过，说明没有明显 Python 语法错误。

但 `environment.yml` 只锁定了 `python=3.11`，Scanpy/AnnData/Pandas/Numpy/Harmony 等都没有 exact version pin；对于最终投稿复现仍不足。

建议：

- Python：`conda-lock` / `pixi.lock` 或 explicit spec；
- R：`renv.lock`；
- 每次冻结输出记录 package versions；
- 建立 figure-panel → source-table → script → checksum manifest；
- active v7 与 `legacy/v6` 彻底分离；
- `node_modules`、render cache、临时 manuscript build 不进入 canonical scientific archive；
- 加入 data accession / checksum / provenance manifest；
- 最终用 GitHub release + Zenodo DOI 固化投稿版本。

当前 ZIP 中约 605 MB 集中在 `04_submission`，大量为历史 build/artifact 内容，而真正当前 Phase 17 数据和结果并未包含。这一结构应反转：科学可复现材料优先，临时渲染缓存剥离。

---

## 21. 当前完成度（按 v7，而不是旧 v6）

以下为基于本次可见文件和 Gate 状态的导师级估计，不是软件自动计算分数：

| 模块 | 完成度估计 | 说明 |
|---|---:|---|
| 科学问题与总体设计 | **90%** | v7 核心问题和证据层已明确 |
| source / hierarchy / common-support audit | **90–95%** | 结构性问题已识别 |
| hard-QC / raw extraction | **75–80%** | 全量入口已建立，但 active files 本包缺失 |
| residual doublet policy | **40–50%** | smoke 已做，C2B1 未冻结 |
| full representation / state freeze | **25–30%** | C2B2/C2B3 未完成 |
| v7 composition inference | **10–15%** | 旧 v6 结果不能计入 |
| v7 within-state transcription | **10–15%** | 旧 pseudobulk 不能计入 |
| frozen external validation | **15–20%** | 有旧外部材料，但 v7 transfer 未完成 |
| manuscript architecture / Methods scaffold | **70–80%** | blueprint 强，最终 Results 尚不能写死 |
| v7 Results / Discussion 实体内容 | **15–20%** | 依赖 C3–C5 |
| v7 publication figures | **20–25%** | Figure 1 设计/脚本存在，Fig 2–5 尚未冻结 |
| reproducible active submission package | **40–50%** | 设计文件强，但 active results 未纳入本 ZIP |

**综合研究执行完成度：约 45%。**  
**当前 manuscript 内容完成度：约 35–40%。**  
**真正投稿成熟度：约 20–25%。**

不能把旧 v6 已完成的文字、旧图和旧 QC 当作 v7 的“80%完成”，因为决定文章结论的 C2B3/C3/C4/C5 目前仍未冻结。

---

## 22. 下一阶段按优先级推进

### P0：先封住推断漏洞

1. 完成 Gate C2B1 complete-library residual doublet review；
2. 明确源数据已做 Freemuxlet/Scrublet，禁止盲目二次删除；
3. 冻结 53 bridge sample 的 inference exclusion / technical validation policy；
4. 更新 README、active tree、exact environment lock。

### P1：冻结“细胞是什么”

5. C2B2 full disease-blind representation；
6. unintegrated reference + Harmony sensitivity；
7. bridge-sample batch reproducibility；
8. C2B3 多 resolution + marker + donor/sample/library coverage + resampling stability；
9. 增加 disease-program/ISG-exclusion state-stability sensitivity；
10. 补 source B-lineage completeness audit；
11. freeze neutral states。

### P2：回答“数量是否改变、同一状态是否改变”

12. C3 strict cohort4 sample-level composition；cohort3 exploratory；
13. global composition + beta-binomial/sccomp/scCODA sensitivity；
14. C4 sample×state raw-count pseudobulk；
15. pathway/regulon 只做 supporting evidence。

### P3：真正外部复现并增强生物学深度

16. discovery-only frozen mapper；
17. GSE135779 childhood/adult 分层映射和效应估计；
18. replication scorecard + abstention；
19. 11 repeated donors 的 paired secondary analysis（若时间点临床含义适合）。

### P4：最后才做投稿定稿

20. 由 frozen v7 source tables 重画 5 个主图；
21. 每图 Source Data；
22. 重新写 Results / Abstract / Discussion；
23. 完整 traceability + checksum；
24. 再决定 journal tier 和最终投稿包。

---

## 23. 投稿层级判断

如果 v7 最终只是“更严谨地重做一个已知 IFN/SLE 单细胞故事”，Nature Communications 的编辑新颖性门槛仍会偏高。

若能够同时得到：

- neutral states 稳定；
- cohort4 composition 有清晰可信 effect；
- within-state transcription 是独立于 composition 的另一层；
- GSE135779 frozen transfer 跨 childhood/adult 至少有一层主效应重复；
- bridge technical reproducibility 好；
- paired donor secondary evidence 提供动态支持；

则论文会从“公共数据再分析”提升为“对 SLE B-cell remodeling 的统计和生物学重解释”。这时才有资格认真评估 Nature Communications 级别的 stretch submission。

若获得强疾病基因组/单细胞结果和外部验证，但广泛机制/动态证据较弱，Genome Medicine 仍是非常合理的主目标；若是技术上严谨、专门领域内形成明确新生物学认识，Communications Biology 是可信的备选。

---

## 24. 最终导师意见

**不建议现在继续润色 v6 或修旧主图。**当前最有价值的工作不是“把论文写得更像论文”，而是完成 Gate C2B1→C2B3，把 state definition 真正冻结。只有这一步完成，后面的 composition、pseudobulk、external validation 才有统计意义。

项目目前不是失败，而是完成了一次必要的“推断层级校正”。真正决定论文能否从普通公共数据重分析提升到高质量 Q1 的，不是再增加多少通路、多少 regulator、多少 volcano，而是四个问题是否被回答得非常干净：

1. **state 是否在 disease-blind 条件下稳定存在？**
2. **SLE 是否改变这些 state 的相对组成？**
3. **在同一 state 内，SLE 是否还有独立的转录重塑？**
4. **这些结论哪些能被 frozen external transfer 复制，哪些不能？**

如果这四层做扎实，即使旧的 ABC/APC-like 结论最终被推翻，v7 仍然可以形成一篇逻辑完整、方法严谨且更值得发表的论文。
