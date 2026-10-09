# SLE B-cell remodeling 项目：本对话全量总结与完整工作记录

> **项目**：`1209433622cz-maker/sle-bcell-remodeling`
> **当前目标期刊**：**npj Systems Biology and Applications**
> **当前 Zenodo version DOI**：`10.5281/zenodo.22151739`
> **当前 GitHub 最近一次已观察到的 main commit**：`0c7361022510b47e8cc7ae82baafd4b6dcff7c8e`
> **最新本地 hardening bundle**：`20260830_final_render_semantic_hardening.zip`
> **最新本地 hardening 状态**：`PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`
> **最新最终包 SHA-256**：`414BD522D7108D4F7102F359AD8E3AE27A10FC9FB620BC560B4A0445909BB170`
> **生成日期**：2026-09-08

---

## 0. 这份总结的范围与使用方式

这份 Markdown 汇总了本对话中围绕 `sle-bcell-remodeling` 项目的完整工作链，尽可能恢复并整理了：

- 最初的项目全量生信审计；
- manuscript / Methods / Results / Discussion 的结构重构；
- Figure 1–5 与 Supplementary Figure S1–S10 的 Nature-style 质控；
- Gate C7/C8/C8R/C8S/C8BRF；
- Round 6 R1/R2；
- Gate C9 与 C9R 技术纠错；
- QiTeng Academic Writing Skill 多轮精修；
- GitHub/Zenodo release、DOI、版本冻结；
- 从无指定 SCI 一区到 JCR Q1 选刊，再到最终锁定 `npj Systems Biology and Applications`；
- target-specific refreeze；
- 最终 render / semantic hardening；
- 当前 remaining gates、STOP rules 与下一阶段目标。

由于对话极长，部分早期消息在当前界面中以压缩/跳过形式存在，因此本总结综合使用了：当前对话可见内容、已生成的阶段报告、项目上下文、GitHub 状态、用户上传 artifact，以及最新 `20260830_final_render_semantic_hardening.zip` 中的 machine-readable status files。对不能从当前材料重新独立核验的极少数历史细节，本文会按“历史记录/此前审计结论”表述，而不会伪装成刚刚重新计算。

---

# 1. 用户贯穿全项目的固定要求

整个对话中，用户对这个项目的要求始终高度一致，核心原则可以归纳为以下十条：

1. **角色要求**：以生物信息学专家、博士生导师/PI 的标准进行全量核查，而不是只做语言润色。
2. **目标**：追求 SCI 一区水平，后期明确到 JCR Q1，最终锁定 `npj Systems Biology and Applications`。
3. **分析优先级**：能通过重跑分析、重画图解决的问题，优先重跑，不手工 patch 结果文件。
4. **科学真实性优先**：不为了投稿而改阈值、换 seed、删不利 replicate、挑 mapper、追显著性。
5. **图形要求**：主图和补图统一按 Nature-family 风格设计与自动质控。
6. **写作要求**：后期使用 `QiTeng_Academic_Writing_Skill` 精修，重点是逻辑、证据层级、claim boundary，而不是单纯英语润色。
7. **复现要求**：所有关键图有 Source Data，关键统计有 Full Statistical Results，代码、环境、manifest、SHA、DOI 与 release 闭环。
8. **版本治理**：旧版本不覆盖，重要阶段新建 gate / release；GitHub tag/Zenodo version 不 force-move。
9. **过程记录**：每轮任务结束要产出详细 Markdown 行动记录。
10. **最终哲学**：如果继续分析的边际收益低于 post-hoc 风险，就停止扩展科学分析，转入 publication engineering。

---

# 2. 项目的核心科学问题

项目最终形成的中心科学问题不是：

> “SLE 是否存在 IFN biology？”

也不是：

> “是否发现一个新的 B-cell subtype？”

而是：

> **当 cell identity、cell composition 和 within-compartment transcription 被拆分成不同 inferential layers 后，哪些疾病信号在 disease-blind reconstruction、biological-unit-aware inference、identity uncertainty propagation 和独立队列验证后仍然可重复？**

最终论文概念主轴被压缩为：

> **Hard B-cell state assignments have explicit reproducibility limits, whereas process-level IFN/ISG remodeling is more reproducible across increasingly stringent inferential and validation layers.**

换言之，论文真正的创新维度是：

- 不默认 cell-state taxonomy 稳定；
- 先检验 inferential granularity 是否可靠；
- 将 taxonomy-level、composition-level、program-level 证据分层；
- 在预设 gate 失败时保留 HOLD，而不是后验“救回 PASS”；
- 最终证明 process-level IFN signal 比 hard state membership 更可迁移。

---

# 3. 主要数据集与角色

## 3.1 GSE174188：主发现/内部验证数据

最终冻结的关键数字：

- 原始 B-lineage cells：**152,981**；
- hard-QC 后：**150,402**；
- genes：约 **30,172**；
- donors：**259**；
- biological samples：**271**；
- technical libraries：**88**；
- processing cohorts：**4**。

用途：

- disease-blind identity reconstruction；
- fine-state vs broad-state stability adjudication；
- primary composition analysis；
- primary B_CONV transcription/pseudobulk；
- internal validation；
- donor-nonoverlap internal sensitivity；
- R1 full-pipeline end-to-end resampling；
- identity-boundary propagation；
- regulator sensitivity。

## 3.2 GSE135779：独立外部复制数据

主要 childhood analysis：

- **11 controls**；
- **32 SLE**；
- 共 **43 donors**。

combined childhood+adult：

- **16 controls**；
- **38 SLE**；
- 共 **54 donors**。

adult-only：

- **5 controls**；
- **6 SLE**；
- statistical power 不足，仅作 directionally compatible。

用途：

- source-label-defined broad conventional-B analog 的独立 IFN/ISG replication；
- gene-level cross-dataset concordance；
- C9/C9R external remapping sensitivity。

## 3.3 GSE23307：极小样本扰动背景

- 健康供体：**n=2**；
- IFN-beta paired perturbational context；
- 只作 descriptive support；
- 明确不计算 inferential P value。

---

# 4. 最终冻结的核心科学结果

## 4.1 Identity：fine-grained hard states 不足以承担稳定疾病推断

最初 disease-blind fine-state solution 未通过冻结稳定性门槛，因此项目没有为了“做出 subtype 结果”而继续重命名或后验调参。

最终保留 broad scaffold：

- `B_CONV`
- `B_ASC`

但它被严格定义为：

> **analysis scaffold**，不是 universally reproducible taxonomy。

## 4.2 Frozen-representation broad-state resampling

在冻结 50-D Harmony representation 下，20 次 graph resampling：

- minimum mapped ARI ≈ **0.990**；
- minimum mapping agreement ≈ **0.9998**；
- minimum state-median Jaccard ≈ **0.991**；
- broad partition 在 frozen representation 条件下稳定。

这部分后来被明确限定为：

> **conditional on a frozen representation**。

它不是完整 HVG/PCA/Harmony 的 end-to-end bootstrap。

## 4.3 Round 6 R1：full-pipeline end-to-end resampling 正式 HOLD

这是本项目最重要的负面边界之一。

全量 R1：

- 150,402-cell pool；
- 20 replicates；
- 每次 within-library 80% resampling；
- 每 replicate 约 **120,320 cells**；
- 3,000 HVGs；
- normalization → HVG → PCA → Harmony → graph → Leiden 全流程重跑；
- 20/20 replicates 完成；
- 20/20 Harmony converged。

冻结门槛与实际值：

| 指标 | 实际值 | 阈值 | 判定 |
|---|---:|---:|---|
| median mapped ARI | 0.962972 | ≥0.950 | PASS |
| minimum mapped ARI | 0.929697 | ≥0.900 | PASS |
| median mapping agreement | 0.999368 | ≥0.995 | PASS |
| minimum mapping agreement | 0.998770 | ≥0.990 | PASS |
| minimum state median Jaccard | **0.930323** | ≥0.950 | **FAIL** |

正式状态：

`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

后续确认：

- failure 主要由 **B_ASC** 驱动；
- B_ASC median Jaccard ≈ **0.930323**；
- B_ASC minimum Jaccard ≈ **0.872**；
- B_CONV median Jaccard ≈ **0.999363**；
- B_CONV minimum Jaccard ≈ **0.998760**。

这意味着：

> broad scaffold 在 global agreement 上高度一致，但 B_ASC 的 state-specific membership overlap 没达到预设 0.95 门槛，因此不能升级成 end-to-end universally reproducible taxonomy。

## 4.4 Identity-boundary propagation

项目没有尝试“修复”R1 HOLD，而是把实际观察到的 state assignment exchange 传播到疾病效应模型。

结果：

- primary composition OR across 20 perturbed partitions：约 **0.896–0.967**；
- 所有 confidence intervals 均包含 1；
- primary B_CONV IFN/ISG effect：约 **0.836–0.845**；
- donor-nonoverlap IFN/ISG effect：约 **1.059–1.087**；
- 40/40 IFN estimates 均为正且 CI > 0。

因此 R1 HOLD 没有推翻疾病级结论，反而限定了 taxonomy claim。

## 4.5 Primary B_ASC composition：不支持一般性 expansion

Primary processing-cohort-4：

- OR = **0.947**；
- 95% CI = **0.636–1.410**；
- P = **0.787**；
- adjusted fractions：controls **1.61%** vs managed SLE **1.52%**。

HC1 sensitivity：

- 95% CI = **0.651–1.376**；
- P = **0.774**。

Secondary flare：

- OR = **2.303**；
- nominal P = **0.0282**；
- frozen q = **0.0845**；
- 不升级为 central result。

最终 claim：

> primary B_ASC abundance difference **not supported**；
> 也不宣称 equivalence，因为 CI 仍允许某种程度上升。

## 4.6 Primary B_CONV IFN/ISG：论文最稳定的中央结果

Primary GSE174188 B_CONV pseudobulk：

- 89 pseudobulk strata；
- 43 reference / 46 SLE；
- effect = **0.837**；
- 95% CI = **0.525–1.148**；
- q = **2.98e-6**。

Sensitivity：

- 20-cell threshold：positive；
- 100-cell threshold：positive；
- residual-doublet-risk exclusion：positive；
- 89/89 leave-one-sample-out：positive。

基因层：

- 10 个 tested positive-arm genes 全部同向；
- leading genes 包括 `USP18`, `IFI44L`, `EPSTI1`, `IFIT3`, `MX1`, `IFI6`, `OAS2`, `ISG15`, `STAT1` 等。

## 4.7 Internal validation / donor-nonoverlap

同一 GSE174188 accession：

- full internal effect ≈ **0.856**，q ≈ **0.00462**；
- donor-nonoverlap effect ≈ **1.086**，q ≈ **3.61e-4**。

重要写作边界：

> 这是 **internal validation/internal replication**，不是 independent cohort。

## 4.8 Independent GSE135779 IFN/ISG replication

Childhood：

- 11 controls / 32 SLE；
- effect = **1.042**；
- 95% CI = **0.681–1.402**；
- q = **2.98e-6**。

Combined childhood+adult：

- effect ≈ **0.996**；
- 95% CI ≈ **0.655–1.337**；
- q ≈ **1.31e-6**。

Adult-only：

- effect ≈ **0.968**；
- 95% CI ≈ **-0.123–2.060**；
- q ≈ **0.291**；
- 不作阳性确认。

LOO：

- 43 childhood donor deletions 全保持正向；
- 8 个 source B-cell label omission 也保持正向。

最终写作边界：

> independent dataset 上的 **source-label-defined broad B-cell analogue** 重复了 frozen IFN/ISG program。

## 4.9 Genome-wide cross-dataset concordance 很弱

- shared tested genes：**4,410**；
- Spearman rho ≈ **0.026**。

因此：

> 只支持 program-level replication，**不支持 globally shared SLE transcriptome**。

这条 negative boundary 被明确保留，是项目可信度的重要组成部分。

---

# 5. Regulatory / response evidence

## 5.1 Prespecified regulators

IFN-centered：

- STAT1
- STAT2
- IRF7
- IRF9

Proliferation controls：

- E2F1
- FOXM1
- MYC
- MYBL2

全局 8 regulators × 3 contrasts = **24 tests**，global BH。

## 5.2 ULM

STAT1 / STAT2：

- GSE174188 primary：positive/global significant；
- GSE174188 donor-nonoverlap：positive/global significant；
- GSE135779 childhood：positive/global significant。

## 5.3 CAMERA / FRY correlation-aware sensitivity

Target counts：

- STAT1：98 / 129 / 161；
- STAT2：14 / 19 / 20。

CAMERA：

- 6/6 directions positive；
- 5/6 BH significant。

明确 exception：

- GSE174188 primary STAT2；
- inter-gene correlation ≈ **0.122503**；
- CAMERA q ≈ **0.135472**。

FRY：

- 6/6 positive；
- 6/6 BH significant；
- discovery STAT2 FRY q ≈ **4.909e-5**。

最终 claim：

> regulator evidence 是 cross-contrast convergent observational support，而不是 universal method-independent significance。

## 5.4 Round 6 R2 overlap-depletion

R2 的目的：判断 STAT1/STAT2 支持是否只是由 frozen IFN genes 的 circular overlap 驱动。

结果：

- 12-gene narrow depletion：整体支持保留；
- M5911 broader depletion：明显衰减；
- 36/36 method-level directions 保持 positive；
- 但部分 ULM/CAMERA/FRY 显著性下降；
- discovery STAT2 在 broader depletion 后尤其变弱。

最终边界：

> regulator support **not reducible to the 12 core genes**，但**partly coupled to the broader interferon-response transcriptome**；
> 不支持 overlap-independent causal regulation。

## 5.5 M5911

三组 confirmatory contrasts 均正向富集；作为 orthogonal response-set concordance。

## 5.6 GSE23307

- IFN-beta paired context；
- n=2 healthy donors；
- 12/12 genes positive；
- 只作 descriptive perturbational context；
- no inferential P。

---

# 6. Gate C9 与 C9R：一次非常重要的技术纠错

## 6.1 最初 C9

最初 Gate C9 试图回答：

> GSE135779 independent IFN result 是否依赖 source-provided B-cell labels？

初版曾获得：

`PASS_C9_LABEL_AGNOSTIC_EXTERNAL_SUPPORT`

主要记录：

- matrix cells：363,083；
- samples：56；
- QC pass：353,527；
- label-agnostic selected B-lineage candidates：36,630；
- source-B recovery：约 **98.69%**；
- conditional non-B contamination：约 **3.32%**；
- childhood：11 HC / 32 SLE；
- elastic-net effect ≈ **0.30597**, q≈0.002347；
- nearest-centroid effect ≈ **0.30418**, q≈0.002117；
- LOO 全正；
- per-cell margin contamination ≈ **15.05%**，因此仅 secondary sensitivity。

## 6.2 后续独立审计发现 C9 的两处阻断性问题

### 问题 1：reference/external normalization denominator 不一致

旧 reference：

- 先截取 mapping features；
- 再以 feature-only count total 做 CP10K。

external：

- 以 full-transcriptome library total 做 CP10K；
- 再截取 features。

因此两侧不在同一 normalization denominator。

### 问题 2：calibration gate 没有真正 fail-closed

旧 elastic threshold 下：

- B_ASC precision 未满足 frozen 0.90；
- 但 diagnostic fallback 仍可能授权 outcome unlock。

这使旧 C9 PASS 的授权逻辑失效。

## 6.3 C9R corrected calibration

纠错后：

- reference/external 都按 full-library log1p(CP10K) 后再 feature subset；
- frozen rules 不变；
- formal gate fail-closed。

Elastic-net：

- coverage ≈ **0.941958**；
- B_CONV precision ≈ **0.996450**；
- B_ASC precision ≈ **0.885210** < **0.90**。

Nearest centroid 单独通过，但：

> 不能在看到结果后用 centroid rescue elastic-net。

正式状态：

`HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`

并且：

- corrected external disease outcome unlock = **false**；
- corrected disease effects = **not estimated**。

这次纠错的意义非常大：

> 项目主动撤回一条曾经的 positive robustness claim，而不是修规则让它继续 PASS。

最终论文保留：

- source-label-defined independent GSE135779 replication；
- source-label-independent robustness = unresolved/HOLD。

---

# 7. Figure 体系的演化

## 7.1 主图最终架构

### Figure 1 — Disease-blind identity / evidence hierarchy

核心：

- study/evidence hierarchy；
- fine-state failure；
- broad scaffold；
- frozen-representation stability；
- R1 full-pipeline boundary。

曾出现过两个重要修复：

1. panel a evidence nodes/interpretation branch 重排；
2. panel c 的 0.990 guide 曾被错误写成 `minimum mapped-ARI criterion`，后修正为：
   - 0.900 = minimum mapped ARI；
   - 0.990 = minimum mapping agreement。

## 7.2 Figure 2 — Composition

核心：

- primary B_ASC composition null；
- secondary flare context；
- sample-level inference。

后期 semantic hardening 将：

> `No primary B_ASC enrichment`

收紧为：

> `Primary B_ASC enrichment not supported`

避免把“未支持差异”写成“证明不存在”。

## 7.3 Figure 3 — B_CONV transcription

核心：

- 四个 frozen programs；
- IFN/ISG 为最稳定 positive program；
- gene-level coherence；
- internal/donor-nonoverlap support。

曾修正 filtered-gene annotation wording，防止读者误解哪些 gene 在 primary/nonoverlap 被过滤。

## 7.4 Figure 4 — Independent external replication

核心：

- GSE135779 source-label-defined replication；
- childhood strongest；
- adult underpowered；
- shared IFN genes 同向；
- genome-wide rho=0.026。

后期进一步把 reader-facing wording 从笼统 `independent validation` 收紧成：

> `source-label-defined replication`

防止与 C9R 的 source-label-independent transfer 混淆。

## 7.5 Figure 5 — Regulatory/response evidence

核心：

- STAT1/STAT2 regulator convergence；
- proliferation controls；
- M5911；
- GSE23307 perturbational context。

Round 6 重绘时特别避免把：

> regulator → M5911 → IFN-beta

画成单一因果链，而是并列三条支持路径。

---

# 8. Supplementary Figure 体系

最终已形成 S1–S10：

- **S1**：source integrity / hard QC / doublet / residual-risk；
- **S2**：representation diagnostics / Harmony / bridge / technical mixing；
- **S3**：fine-state instability / identity adjudication；
- **S4**：composition diagnostics；
- **S5**：pseudobulk / filter / model diagnostics；
- **S6**：external validation diagnostics；
- **S7**：STAT1/STAT2 correlation-aware CAMERA/FRY sensitivity；
- **S8**：overlap-depletion sensitivity；
- **S9**：R1 full-pipeline identity boundary + propagation；
- **S10**：corrected external reference calibration boundary / C9R HOLD。

其中 S8 曾有 page-split/版式问题，后被重绘并修复；当前 latest hardening bundle 已包含新的 source-redrawn S8。

---

# 9. Nature-style / npj-specific 图件质控演化

## 9.1 Generic Nature-style 阶段

早期统一：

- Arial；
- panel label 8 pt bold lowercase；
- body 5–7 pt；
- vector PDF；
- 600 dpi PNG；
- white background；
- 约 170 mm width；
- source-data assertions。

## 9.2 npj target-specific 审计发现 style-contract bug

曾发现 `apply_npj_sba_style()` 的实现逻辑：

1. 先把 text 设为 8 pt、line width >=1 pt；
2. 后面又执行 generic clamp，将 non-panel text 压回 5–7 pt、line width clip 到 0.25–1.0 pt。

导致导出的实际 PDF：

- Figure 1 minimum line ≈ **0.60 pt**；
- Figure 5 minimum line ≈ **0.90 pt**。

这暴露出：

> declared style contract PASS ≠ exported artifact PASS。

## 9.3 Final render semantic hardening 已关闭该问题

最新上传的 `20260830_final_render_semantic_hardening.zip` 显示：

`01_NPJ_FIGURE_RENDER_STATUS.json`：

- 15 figures；
- 5 main + 10 supplementary；
- 170.0 mm；
- Arial；
- target visible text 8 pt；
- minimum positive line width 1.0 pt；
- RGB；
- white background；
- 15/15 source tables byte-identical；
- exported artifact contract PASS。

最终 gate `04_FINAL_AUDIT_STATUS.json` 进一步确认：

- `figure_gate_pass = true`
- `figure_exported_artifact_contract_pass = true`
- `figure_source_tables_byte_identical = true`
- `all_figure_sources_individually_identical = true`
- 5 main PDFs single-page = true。

这说明此前发现的 figure-style implementation bug 已在最新本地 hardening 版本关闭。

---

# 10. Source Data / machine-readable 统计体系

## 10.1 Figure Source Data

项目后期做到：

- Figure 1–5 + S1–S10 全部有 machine-readable source table；
- source SHA 在重绘时保持 byte-identical；
- 图形重渲染只改 typography/layout，不改数值。

## 10.2 Figure 5 Source Data 曾发现 panel provenance defect

早期审计发现：

- GSE23307 2-row source data 被标成 panel D；
- 实际 figure 是 panel E。

此问题通过 rerun source-data construction 修复，而不是手改 CSV。

## 10.3 Full Statistical Results

项目后期加入完整统计结果归档，包括：

- GSE174188 primary edgeR tables；
- internal/nonoverlap；
- GSE135779 childhood/combined/adult；
- programs；
- composition；
- regulator summaries；
- M5911；
- C9R calibration；
- design/model matrices；
- README / manifest / SHA。

## 10.4 npj statistics reporting map 曾发现 semantic bug

在 target-specific package 中，曾发现：

- R1 claim 写“criterion held”，decision 却是 HOLD；
- C3 claim 写“B_ASC differs”，decision 是 NOT_SUPPORTED；
- C5 genomewide claim 写“effects agree”，decision 是 WEAK_RHO_0.026；
- C9R claim 写“mapper qualifies”，decision 是 HOLD；
- TF depletion claim 写“overlap-independent”，decision 是 NOT_SUPPORTED。

因此新增 semantic hardening：

- 不能只存 statistical decision；
- human-readable claim 也必须与 decision 同向。

## 10.5 最新 hardening 已关闭统计 map 语义问题

`04_FINAL_AUDIT_STATUS.json`：

- `statistics_reporting_map_complete = true`
- `statistics_map_contains_hold_boundaries = true`
- `statistics_map_claims_match_decisions = true`

说明此前 machine-readable semantic bug 已在最新本地 hardening 中关闭。

---

# 11. Manuscript 写作演化与 QiTeng Academic Writing Skill

## 11.1 从早期稿到“scientific narrative freeze”

项目经过多轮：

- manuscript v11 / v15 / v16 / v20；
- Genome Medicine-oriented 版本；
- journal-neutral QiTeng 版本；
- target-specific npj 版本；
- QiTeng hardened npj 版本。

## 11.2 QiTeng Skill 使用原则

后期使用 `QiTeng_Academic_Writing_Skill v0.3.21`，核心不是简单 grammar polishing，而是：

- `KNOWN → GAP/TENSION → RESPONSE → EVIDENCE → INTERPRETATION → BOUNDARY`；
- claim-strength governor；
- Results effect-first；
- Discussion interpretive delta；
- salience redistribution；
- control-plane / manuscript-plane firewall；
- Figure Claim Gate；
- 不把内部 gate jargon 带入 reader-facing manuscript。

## 11.3 标题演化

曾经历：

1. `Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence...`
2. `Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling...`
3. 为避免否定 biological states 本身，改为：
   - `unstable B-cell state assignments`
4. journal-neutral QiTeng 版本：
   - `Disease-blind single-cell reconstruction distinguishes unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus`
5. npj 15-word target title：
   - **`Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus`**

最终标题的优点：

- 15 words；
- 不暗示 biological states 不存在；
- 直接对比 process reproducibility 与 assignment instability；
- 对 npj systems-biology 编辑更直观。

## 11.4 Abstract 演化

早期 structured abstract：约 314–356 words。

npj 要求：

- unstructured；
- ≤150 words。

最终 target abstract：**140 words**。

重点保留：

- 150,402 discovery cells；
- R1 state-overlap criterion failed；
- composition null + B_CONV IFN preserved；
- independent GSE135779 source-label-defined replication；
- corrected label-independent remapping HOLD；
- STAT1/STAT2 observational；
- no taxonomy / causal regulator / clinical utility。

## 11.5 Introduction 的关键精修

旧表述：

> “neither interferon activity nor plasmablast biology is novel”

后改为：

> **“interferon activity and plasmablast biology are well established yet strongly context dependent.”**

这样既不伪装 novelty，又不在开篇主动削弱稿件价值。

Introduction 最终任务句改为：

> 测试一个 evidence hierarchy：哪些 B-cell features 在越来越严格的 reconstruction / validation 下仍成立，哪些 remain cohort-specific / representation-dependent / mechanistically unproven。

## 11.6 Results 结构

最终 Results 按答案导向组织：

1. disease-blind reconstruction 与 state-specific stability limits；
2. primary B_ASC abundance lacks statistical support；
3. IFN/ISG 是四个 frozen B_CONV programs 中最稳定；
4. GSE135779 source-label-defined replication + low genome-wide concordance；
5. corrected external remapping fails calibration；
6. convergent regulator/response evidence remains observational。

## 11.7 Discussion 精修

QiTeng late-stage refinement 重点：

- 避免 Results 重述；
- 把 R1/C9R HOLD 变成 interpretive boundary；
- 不把不同 reproducibility metric 直接数值比较；
- translational implication 降级为 future testable hypothesis；
- 删除重复 landing。

Discussion 后期从约 1081 words 压到约 **996 words**。

最终 landing 逻辑：

> process-level IFN association reproducible；
> hard state assignments 有明确 stability/transfer limits；
> failed criteria narrowing the conclusion rather than weakening it；
> no universal taxonomy / generalized B_ASC expansion / causal regulator / unique stimulus / clinical utility。

---

# 12. npj Systems Biology and Applications 选刊过程

## 12.1 早期目标不固定

最开始：

- SCI 一区；
- 后来考虑 Genome Medicine；
- Communications Biology；
- Journal of Autoimmunity；
- Nature Communications / Genome Biology 被认为收益不高。

## 12.2 为什么逐渐不再把 Genome Medicine 作为首选

原因：

- IFN biology 本身已知；
- public-data secondary analysis；
- no prospective cohort；
- no demonstrated clinical utility；
- source-label-independent external transfer 后来又是 HOLD。

因此 Genome Medicine 被重新定位为 stretch。

## 12.3 Communications Biology

优点：

- Nature Portfolio；
- 接受 secondary data analysis；
- 接受 computational methods；
- technical soundness 与项目匹配。

风险：

- biological novelty gate 更高；
- “SLE IFN biology 已知”可能导致 editor 认为更偏 rigorous reanalysis。

## 12.4 最终锁定 npj Systems Biology and Applications

原因：

其 scope 与本文真正 novelty 非常贴合：

- single-cell systems biology；
- systems immunology；
- computational analysis of complex biological systems；
- disease modeling。

论文可以按：

> **inferential robustness across biological layers**

来投稿，而不必装成临床转化论文。

当前公开 journal metrics 在对话中曾记录：

- 2025 JIF ≈ **4.4**；
- 5-year JIF ≈ **4.2**；
- median first editorial decision ≈ **8 days**；
- median submission-to-acceptance ≈ **155 days**。

但项目一直坚持：

> JCR Q1 必须最终由 Clarivate/机构 profile 正式核实，不能仅凭 JIF/SJR 推断。

---

# 13. npj target-specific adaptation

## 13.1 Title / Abstract

- title：≤15 words；
- abstract：140 words unstructured。

## 13.2 Main manuscript 结构

从旧 BMC/Genome Medicine 风格：

- Background
- Methods
- Results
- Discussion
- Conclusions
- Abbreviations
- Declarations

重构为 npj Article：

- Introduction
- Results
- Discussion
- Methods
- Data availability
- Code availability
- Acknowledgements
- Author contributions
- Competing interests
- References
- Figure legends

## 13.3 Supplement 重构

npj 不允许 Supplementary Methods，因此：

- Supplementary Methods 全部移除；
- main Methods 承担必要解释；
- 极细 reproducibility implementation 留在 GitHub/Zenodo；
- Supplement 保留 Tables/Figures；
- 单一 merged Supplement PDF。

## 13.4 Supplementary Data

BMC 风格 `Additional file 1–4` 被改成 npj/Nature 友好的：

- Supplementary Data 1 — Figure source data；
- Supplementary Data 2 — Regulator sensitivity；
- Supplementary Data 3 — Full statistical results。

## 13.5 Funding / Acknowledgements

独立 Funding section 删除；

funding 状态合并到 Acknowledgements。

## 13.6 AI disclosure

Nature Portfolio 要求 LLM use 在 Methods 中披露，因此保留：

- Codex/ChatGPT 用于 code drafting / workflow documentation / language editing / QA；
- primary research data 和数值来自本地计算与冻结 outputs；
- authors 对全部内容负责；
- AI 不作为作者。

---

# 14. GitHub / Zenodo / Release 演化

## 14.1 v1.0.0

早期 public release：

- GitHub v1.0.0；
- Zenodo DOI：`10.5281/zenodo.22086892`。

后续 Round 6 / C9 / C9R / QiTeng 发生实质更新，因此 v1.0.0 被保留历史，不 force-move。

## 14.2 旧 Zenodo tombstone

旧 `22086892` 后被 replacement/tombstone；machine removal reason 显示 `retracted`，但实际项目语义是：

> administrative withdrawal after verified replacement，非 science misconduct/retraction。

因此最终 reader-facing manuscript 推荐主要引用新 DOI。

## 14.3 v1.1.0

公开 release：

- GitHub tag object：`6e492e3d...`；
- peeled content commit：`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`；
- GitHub release ID：`378885936`；
- Zenodo version DOI：**`10.5281/zenodo.22151739`**；
- concept DOI：`10.5281/zenodo.22086891`。

release assets 曾包括：

- Research_Archive.zip；
- Source_Code.zip；
- SHA256SUMS.txt。

Research Archive / Source Code / GitHub release / Zenodo 之间做过 SHA 一致性验证。

---

# 15. 重要 GitHub commits（按对话中反复出现的关键节点）

以下是项目对话中最重要的 commit 节点，便于追踪：

- `6705ed79...` — Gate C8R pre-submission repair；
- `ad0397a...` — C8BR journal-facing prefreeze（截图阶段）；
- `e6f4cac...` — public release / DOI activation 记录；
- `b094bbe...` — Round 6 R2 + R1 runner readiness；
- `b180b474...` — initial Gate C9 label-agnostic validation；
- `f28cf6a...` — C9 correction-review / corrected HOLD state；
- `c687759...` — author-confirmation synchronization；
- `05e41f4...` — corrected Figure 1 integration；
- `74678c7...` — corrected candidate verification；
- `cf8cc7e...` / `a03ff9a...` — scientific freeze / Zenodo replacement preparation/synchronization；
- `f1859ff...` — DOI-integrated reproducibility release content；
- `395bb55...` — Zenodo tombstone + GitHub v1.1.0 release record；
- `2054edd...` — release documentation repair / JCR Q1 selection preparation；
- `8291205...` — current journal-neutral submission package；
- `1257119...` — npj SBA target-specific submission refreeze；
- `0c73610...` — preserve npj audit evidence bytes。

**最新本地 hardening bundle 的完成状态尚未在当前已观察 GitHub main 中显示为新的 commit，因此应视为“本地完成、待 GitHub 同步/作者签字”的最新阶段。**

---

# 16. Gate/状态演化总表

| 阶段 | 核心决策 | 含义 |
|---|---|---|
| C7/C8 | 主稿/五图/Genome Medicine package | 基础 submission architecture |
| C8R | scientific/figure reproducibility repair PASS + author action required | 修 Figure2 / regulator sensitivity / source traceability |
| C8S | supplementary evidence + traceability freeze | 补 S1–S7 / full stats / Fig5 provenance |
| C8BR/C8BRF | journal-facing prefreeze / public release integrity | 科学冻结，转作者/伦理/发布工程 |
| Round6 R2 | overlap-depletion sensitivity | regulator claim 降级、边界更清楚 |
| Round6 R1 | `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` | B_ASC-specific end-to-end failure |
| C9 | initial label-agnostic external support PASS | 后因技术缺陷被撤回 |
| C9R | `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED` | corrected calibration fail-closed，no disease outcome |
| QiTeng text rounds | manuscript logic / claim boundary hardening | scientific narrative freeze |
| v1.1.0 | GitHub/Zenodo reproducibility release | DOI 22151739 |
| npj target refreeze | Article-specific title/abstract/structure/figures | target package 构建 |
| preapproval independent audit | 发现 figure-style bug + stats-map semantic bug | 暂停作者签字 |
| final render semantic hardening | `PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED` | 两个技术 bug 已关闭 |

---

# 17. 最新上传的 final render semantic hardening：当前真实终局状态

用户在本总结请求时同时上传：

`20260830_final_render_semantic_hardening.zip`

这是当前对话中**最新的本地技术状态**。

## 17.1 Hardening evidence audit

`00_HARDENING_EVIDENCE_AUDIT.json`：

`PASS_HARDENING_EVIDENCE_AUDIT`

确认：

- candidate hashes 与外部 receipt 一致；
- scientific numeric tokens preserved；
- source-label-defined scope explicit；
- self-weakening novelty phrase removed；
- duplicate Discussion landing removed；
- R1 reader boundary preserved；
- C9R reader boundary preserved；
- no scientific reanalysis。

## 17.2 Target sources

`00_TARGET_SOURCE_BUILD_STATUS.json`：

`PASS_NPJ_SBA_HARDENED_SOURCES_BUILT_SCIENCE_FROZEN`

确认：

- selected target = npj Systems Biology and Applications；
- content type = Article；
- title = 15 words；
- abstract = 140 words；
- references = 32；
- Supplementary Methods removed；
- no scientific reanalysis；
- no numerical result reselection；
- R1 HOLD preserved；
- C9R HOLD preserved；
- corrected external outcome unlock=false；
- JCR/APC/author approval/submission authorization 仍 pending。

## 17.3 Figure render

`01_NPJ_FIGURE_RENDER_STATUS.json`：

- 15 figures；
- 5 main + 10 supplementary；
- 170 mm；
- Arial；
- target text 8 pt；
- min positive line width 1 pt；
- RGB；
- white background；
- 15/15 source tables byte-identical。

说明此前 npj figure style bug 已经通过源码修复和重渲染解决。

## 17.4 Document build

- Manuscript：31 pages；
- Supplementary Information：18 pages；
- Cover Letter：1 page；
- main manuscript no inline figures；
- supplement 内 10 figures；
- placeholders=0；
- WPS + LibreOffice cross-render 完成。

## 17.5 Final audit

`04_FINAL_AUDIT_STATUS.json`：

`PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`

关键 checks 全 PASS：

- target exact；
- Article exact；
- title <=15 words；
- abstract <=150 words；
- reference identity count retained；
- required structure；
- no forbidden headings；
- Supplementary Methods absent；
- current DOI foregrounded；
- R1 HOLD preserved；
- C9R HOLD preserved；
- no scientific reanalysis；
- figure artifact contract PASS；
- figure source byte-identical；
- WPS / LibreOffice page counts match；
- no clipping / unresolved markers；
- accessibility 0/0/0；
- statistics map complete；
- statistics claims match decisions；
- deterministic package integrity PASS。

## 17.6 最新最终包

`03_PACKAGE_BUILD_STATUS.json`：

- status：`PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`；
- bytes：**15,355,994**；
- SHA-256：

`414BD522D7108D4F7102F359AD8E3AE27A10FC9FB620BC560B4A0445909BB170`

- manifest files verified：20；
- deterministic double build：true；
- 5 main figures；
- one Supplementary PDF；
- 3 Supplementary Data archives；
- no new scientific analysis；
- exact package author approved = false；
- submission authorized = false；
- APC commitment authorized = false。

## 17.7 当前 next gate

最新 `04_FINAL_AUDIT_STATUS.json` 已把 next gate 明确为：

> **`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`**

这意味着：

> **此前技术 hardening 阶段已经在本地完成，科学与 publication engineering 均已闭环；现在真正剩余的是作者和机构层面的确认，而不是继续做分析。**

---

# 18. 当前需要作者/机构真正确认的事项

## 18.1 两位作者 exact-file approval

当前还没有对最新硬化后的 exact hashes 完成最终签字。

需要确认：

- manuscript；
- Supplementary Information；
- 5 main figures；
- Supplementary Data 1–3；
- Cover Letter；
- Reporting Summary；
- Editorial Policy Checklist；
- Data/Code availability；
- AI disclosure；
- CRediT；
- ethics；
- competing interests；
- funding/acknowledgements；
- DOI；
- submission authorization。

## 18.2 JCR Q1 receipt

用户已明确：

> 目标必须满足 JCR Q1 / SCI 一区。

因此必须保存：

- metric year；
- category/categories；
- rank/denominator；
- quartile。

不能用 JIF、SJR、CAS 替代正式 JCR Q1 证据。

## 18.3 APC/OA eligibility

历史对话中记录 npj Original Research APC 约：

- £2,690；
- US$3,490；
- €2,990；
- 另可能加税。

Springer Nature 公共页面曾显示 `The Chinese University of Hong Kong` 可能有 Nature Portfolio OA coverage，但当前 affiliation 是：

> The Chinese University of Hong Kong, Shenzhen

因此不能自动推定 Shenzhen eligible，必须由 CUHK-Shenzhen library/OA office 确认。

## 18.4 Nature Portfolio official forms

此前 package 中是 Markdown draft；最终需要使用当期官方：

- Reporting Summary；
- Editorial Policy Checklist。

作者应逐项复核。

---

# 19. 最终 STOP rules

整个项目到当前阶段已经形成非常清楚的禁止项：

首投前**不要再**：

- 新增 cohort；
- 新增 clustering；
- 替换 mapper；
- 修改 confidence/precision threshold；
- 换 seed；
- 删除 weak replicate；
- 救 R1；
- 救 C9R；
- 重新打开 corrected external disease outcome；
- 新增 TF/regulon database；
- 新增 gene-set family；
- 为显著性换统计模型；
- 手工修改 final PDF figures；
- force-move v1.1.0 tag；
- 覆盖 Zenodo 22151739。

只有两类情况允许重新打开计算：

1. 发现 decision-changing implementation defect；
2. reviewer 明确提出会改变稿件判断的科学问题。

---

# 20. 当前论文的最终科学定位

最推荐的 editor-facing framing：

> **The contribution is not the rediscovery of interferon involvement in SLE, but the identification of an inferential level at which that involvement remains reproducible when cell-state identity itself is stress-tested.**

中文概括：

> 本文不是再次“发现”SLE 的 IFN 生物学，而是通过 disease-blind single-cell reconstruction、分层统计推断、end-to-end resampling、identity uncertainty propagation 与独立队列复制，确定：**hard cell-state assignment 的可重复性边界比 process-level IFN remodeling 更脆弱**。

这也是为什么：

- R1 HOLD；
- C9R HOLD；
- genome-wide rho=0.026；
- B_ASC primary null；

并没有把论文“做坏”，反而构成了整篇稿件可信度结构的一部分。

---

# 21. 当前论文不支持的结论

全文多轮审计后，明确不支持：

- universal B-cell taxonomy；
- stable hard naive/memory/atypical publication subtypes across contexts；
- generalized B_ASC/plasmablast expansion in managed SLE；
- globally shared SLE transcriptome；
- unique IFN-high discrete subtype；
- direct STAT1/STAT2 binding；
- causal STAT1/STAT2 initiation；
- unique upstream ligand；
- source-label-independent GSE135779 disease-effect replication；
- predictive biomarker；
- treatment-selection rule；
- clinical cutoff；
- demonstrated patient benefit。

---

# 22. 当前论文支持的结论

可以支持：

1. disease-blind fine-state assignments 有稳定性限制；
2. broad B_CONV/B_ASC 可作为有限 analysis scaffold；
3. end-to-end full-pipeline stability 在 B_ASC-specific Jaccard criterion 上失败；
4. 这种 identity uncertainty 不改变 primary composition null；
5. 也不改变 B_CONV IFN/ISG positive association；
6. IFN/ISG 在 GSE174188 internal/donor-nonoverlap 中保持；
7. source-label-defined GSE135779 childhood 独立重复 IFN/ISG；
8. replication 是 program-specific，而不是 transcriptome-wide；
9. STAT1/STAT2 有跨对比 observational convergence；
10. broader IFN-gene depletion 会削弱 regulator evidence；
11. M5911/GSE23307 提供 response/perturbational context；
12. process-level signal 在本文测试过的 inferential hierarchy 下比 hard state assignment 更可重复。

---

# 23. 对话中形成的最重要方法学经验

这个项目的对话实际上逐渐形成了一套非常成熟的计算论文治理方法：

## 23.1 先验证 identity，再谈 disease effect

不能默认 cluster label 就是 biological truth。

## 23.2 biological unit 优先于 cell count

donor/sample 才是 inferential unit，避免 cell-level pseudo-replication。

## 23.3 负面 gate 必须保留

HOLD 不是失败，它是对 claim strength 的约束。

## 23.4 post-freeze sensitivity 不能回头重定义 primary analysis

R1/R2/C9R 都是很好的例子。

## 23.5 source-data / statistical map / figure / manuscript 必须四方一致

项目多次发现的真实问题恰恰来自：

- Figure 5 panel provenance；
- Figure 1 threshold wording；
- C9 normalization denominator；
- statistics map claim/decision mismatch；
- style contract 声明与 exported PDF 不一致。

这些都说明：

> 自动 PASS 不能只看 builder 内部状态，必须审计最终 artifact。

## 23.6 “追求完美”不等于“继续加分析”

本项目后期最重要的转变是：

> 完美 = 更少的 post-hoc freedom + 更清楚的 boundary + 更强的 provenance + 更准确的 journal fit。

---

# 24. 当前最终完成度（基于 latest local hardening bundle）

| 模块 | 当前判断 |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1 boundary transparency | 99% |
| C9R correction governance | 99% |
| Identity uncertainty propagation | 98% |
| Source-label-defined independent validation | 96% |
| Regulatory robustness | 97% |
| Manuscript logic | 99% |
| QiTeng writing architecture | 99% |
| npj title/abstract/structure compliance | 100% |
| Main figures scientific content | 99% |
| npj figure artifact contract | 100%（latest hardening） |
| Supplementary evidence | 99% |
| Source-data integrity | 100% |
| Statistics-map semantics | 100%（latest hardening） |
| WPS/LibreOffice QA | 100% |
| Accessibility | 100%（0/0/0） |
| Deterministic package integrity | 100% |
| Exact-file author approval | pending |
| Official JCR Q1 receipt | pending |
| Institutional APC/OA receipt | pending |
| Official Nature forms | pending |
| Submission authorization | pending |

---

# 25. 当前唯一正确的下一阶段

基于最新 `20260830_final_render_semantic_hardening.zip`，此前建议的：

`NPJ_SBA_FINAL_RENDER_AND_SEMANTIC_HARDENING`

**已经完成。**

现在真正的 next gate 是：

> **`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`**

执行顺序：

1. 将 latest hardening 结果同步 GitHub（如果尚未同步）；
2. 两位作者核对 latest exact package hashes；
3. 两位作者批准 latest manuscript/supplement/figures/cover/data/code/AI/declarations；
4. 保存 official JCR Q1 receipt；
5. 获取 CUHK-Shenzhen APC/OA eligibility receipt；
6. 完成 Nature Portfolio Reporting Summary；
7. 完成 Editorial Policy Checklist；
8. corresponding author 明确 authorize upload/submission；
9. portal preflight；
10. 检查 portal-generated PDF；
11. submit；
12. 冻结 manuscript number、submission time、receipt email、实际 uploaded files 及 SHA。

建议投稿后状态：

> `PASS_NPJ_SBA_PORTAL_SUBMISSION_RECEIPT_FREEZE`

---

# 26. 对整个对话的最终总结

本对话最初是一个“请以博士生导师身份全量检查 SLE B-cell 单细胞论文”的请求，随后演化成了一套非常完整的科学与出版治理流程。

项目没有沿着“找到更多阳性结果”的常见路径前进，而是反复通过：

- identity reconstruction；
- statistical hierarchy；
- negative gate preservation；
- full-pipeline resampling；
- uncertainty propagation；
- independent replication；
- regulator correlation sensitivity；
- overlap depletion；
- corrected external mapping；
- source-data audit；
- machine-readable semantic audit；
- figure artifact postflight；
- QiTeng writing refinement；
- GitHub/Zenodo versioning；
- journal-specific refreeze；

把论文从“一个公共单细胞数据的 SLE IFN reanalysis”逐步变成了：

> **一个以 inferential granularity 和 reproducibility boundary 为核心的 single-cell systems biology 研究。**

目前，科学上最重要的事情已经完成：

- R1 HOLD 没被救；
- C9 旧 PASS 被主动撤回并纠错为 C9R HOLD；
- source-label-defined independent IFN replication 保留；
- global transcriptome replication 被明确否定；
- regulator evidence 被严格限制为 observational/convergent；
- clinical utility 没被过度声明；
- figures、source data、statistics map、DOI、GitHub/Zenodo provenance 已基本闭环；
- npj Systems Biology and Applications 的 target-specific manuscript/figures/package 已完成最终 hardening。

因此，**现在项目已经不处于“继续科研分析”的阶段，而处于“作者和机构授权 → portal submission”的阶段。**

---

# 27. 推荐把这份文档作为后续 thread / handoff 的主索引

后续如果开启新对话或交给另一位分析者，建议先读取本文件，然后再读取：

1. latest final hardening status JSON；
2. latest target Manuscript；
3. latest Supplement；
4. latest Figure Source Data；
5. latest Full Statistical Results；
6. GitHub `README.md` / `REPRODUCIBILITY.md`；
7. Zenodo `10.5281/zenodo.22151739`；
8. exact final package SHA；
9. author approval receipt；
10. JCR/APC institutional receipts。

这样可以避免未来重新打开已经冻结的科学问题，或者重复经历 R1/C9R 这种已经完成的判定。

---

## 最终一句话状态

> **Science frozen; R1 and C9R negative boundaries retained; npj-specific render/semantic hardening locally passed; final exact-file author approval, JCR-Q1/APC institutional receipts, official Nature forms and portal submission remain.**
