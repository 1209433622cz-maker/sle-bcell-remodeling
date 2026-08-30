# SLE B-cell remodeling — npj Systems Biology and Applications 专项冻结后独立敌意审计

日期：2026-08-30  
目标期刊：**npj Systems Biology and Applications**  
建议稿件类型：Article  
当前 GitHub `main`：`0c7361022510b47e8cc7ae82baafd4b6dcff7c8e`  
target-specific refreeze commit：`1257119efe6b3f88e581e3456af7e36506a02e70`  
科学 release 内容 commit：`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`  
Zenodo：`10.5281/zenodo.22151739`  
上传 target ZIP SHA-256：`8E56CD61DBA88098B2015CC5E539036BFEAC7E1BA9E90C753AC8CD142C62FA7F`

---

## 1. 独立导师结论

本项目的**科学内容已经达到首投前停止扩展的节点**。

不建议首投前新增：

- cohort；
- mapper；
- clustering/state rescue；
- TF/regulon family；
- gene-set family；
- threshold/seed search；
- R1 rescue；
- C9R outcome unlock；
- 新的 exploratory disease-effect branch。

当前剩余问题不是 biology，而是 **target-specific implementation correctness、reader-facing semantic hardening、repository documentation、author/institutional authorization**。

但是，本轮独立审计发现：当前仓库记录的

`PASS_NPJ_SBA_TARGET_SPECIFIC_REFREEZE_AUTHOR_APPROVAL_REQUIRED`

不应直接进入 author exact-file approval。

更稳妥的当前独立状态应降级为：

`HOLD_NPJ_SBA_PREAPPROVAL_TECHNICAL_HARDENING_REQUIRED`

这是**技术性 HOLD，不是科学性 HOLD**。

建议插入一次非常窄的：

`NPJ_SBA_FINAL_SEMANTIC_AND_RENDER_HARDENING`

完成后再进入：

`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

---

## 2. 上传专项投稿包：独立完整性 PASS

对用户上传的：

`SLE_Bcell_npj_Systems_Biology_and_Applications.zip`

独立计算：

- bytes：14,884,957
- SHA-256：`8E56CD61DBA88098B2015CC5E539036BFEAC7E1BA9E90C753AC8CD142C62FA7F`
- ZIP entries：21
- manifest-listed payloads：20
- ZIP CRC：PASS
- manifest SHA/size：20/20 PASS

独立附件 SHA：

- Manuscript DOCX：`6E4532912F519871046A7596A9A721B77E181B83988FF478865F6D2322688C97`
- Supplementary Information DOCX：`D3B04CAA65D8A8A8CBDD28E8D491F13CC2B3AAB5A2C1B6C16C53C253C589C811`
- Cover Letter DOCX：`8133DEBDAD5249FB2DAEAAAEBAF364E6CCDA0DEC4EA3A31DD5ABAF0D0A4730B6`

Standalone Manuscript/Cover Letter 与 package 内版本 byte-identical。

Supplement DOCX 不在 portal package 中是设计选择；portal package 使用单一 merged Supplement PDF。

---

## 3. 科学源结果没有漂移

target package 中三个统计/源数据 ZIP 与上一轮 journal-neutral package 逐字节一致：

### Supplementary Data 1 — Figure Source Data
SHA-256：

`79CB89AE4E0D0E14E5C8A9883BC667025478FE45302FF8134247ED869C62576D`

### Supplementary Data 2 — Regulator Sensitivity
SHA-256：

`C1F40EB90D344A150D61DE472C9F6B37FA9470CDD2CD0BBC45988D18B8CEA7F8`

### Supplementary Data 3 — Full Statistical Results
SHA-256：

`A3E1F5328BBF8A84C55FF075FD15D50DDB4AF7CA65ED700DE3C7820D1664314D`

三项均 byte-identical。

因此 target adaptation **没有偷偷改变统计结果、source data 或分析选择**。

---

## 4. 科学目的与证据层级复核

当前文章最合理的中心问题不是：

> SLE 是否存在 IFN biology？

也不是：

> 是否发现一个稳定的新 B-cell subtype？

而是：

> 当 identity、composition、within-compartment transcription 被拆分成不同 inferential layers 后，哪些层面的疾病信号在 disease-blind reconstruction、biological-unit-aware inference、identity uncertainty propagation 和独立队列中仍可重复？

当前证据链仍然成立：

1. GSE174188 hard QC retained 150,402 B-lineage cells；
2. fine hard-state assignment 不满足冻结稳定性要求；
3. broad B_CONV/B_ASC 只能作为 analysis scaffold；
4. end-to-end R1 因 B_ASC state overlap 未达阈值而 HOLD；
5. observed assignment exchange propagation 不改变 primary B_ASC null 和 B_CONV IFN/ISG 正向结果；
6. primary B_ASC abundance 不支持一般性 enrichment；
7. B_CONV IFN/ISG 在 discovery、accession-internal donor-nonoverlap、独立 GSE135779 source-label-defined donor analysis 中正向；
8. genome-wide cross-dataset agreement 很弱，不能升级成 globally shared transcriptome；
9. corrected label-independent remapping 因 frozen calibration failure 而 HOLD，不打开 disease effect；
10. STAT1/STAT2 + M5911 + GSE23307 只能支持 convergent observational/response context，不构成直接 binding、唯一 ligand、causal regulator 或 clinical utility。

这一层级是本稿真正的 Q1 竞争力。

---

## 5. target manuscript：整体已经显著改善

当前 target manuscript 已完成：

- 15-word title；
- 140-word unstructured abstract；
- Introduction；
- Results；
- Discussion；
- Methods；
- Data availability；
- Code availability；
- Acknowledgements；
- Author contributions；
- Competing interests；
- 32 条 Nature-style references；
- Figure legends。

R1/C9R 边界在 Abstract、Results、Discussion、Methods 中基本一致。

Supplement 已经：

- 改为与主文一致标题；
- 删除 Supplementary Methods；
- 单一 18-page PDF；
- 保留 Tables S1-S9 + S4B；
- 保留 Figures S1-S10。

这些改动方向正确。

---

## 6. P0-1：npj figure style contract 存在真实实现 bug

这是本轮最重要的新发现。

当前 `publication_style_contract.py` 中 `apply_npj_sba_style()` 的执行逻辑是：

1. 先把 visible text 设为 8 pt；
2. 先把 positive line width 提升到至少 1 pt；
3. **随后同一个函数又执行一轮旧 generic Nature contract：**
   - non-panel text 被重新压回 5–7 pt；
   - line width 被重新 clip 到 0.25–1.0 pt。

因此“npj >=1 pt”设置被函数后半段部分撤销。

### 独立检查 exported PDFs

| Figure | Width | Font range | Minimum exported drawing width |
|---|---:|---:|---:|
| Figure 1 | 170 mm | 7–8 pt | **0.60 pt** |
| Figure 2 | 170 mm | 7–8 pt | 1.00 pt |
| Figure 3 | 170 mm | 7–8 pt | 1.00 pt |
| Figure 4 | 170 mm | 7–8 pt | 1.00 pt |
| Figure 5 | 170 mm | 7–8 pt | **0.90 pt** |

Figure 1 中低于 1 pt 的对象不只是不可见装饰，包括：

- workflow node borders；
- arrows；
- interpretation boxes。

所以当前 action record 中：

> “所有正线宽至少 1 pt”

并不完全成立。

### 为什么现有自动审计没有发现

`phase17_npj_sba_02_build_figures.py`：

- 记录 style contract；
- 检查 source-data byte identity；
- 检查 PDF 页数和尺寸；

但没有解析 **exported PDF 的实际 font/line operators**。

`phase17_npj_sba_05_final_audit.py` 只检查：

- 15 张图存在；
- source data identical；
- five main PDFs single-page；

也没有独立检查实际 exported line width/font。

所以这是一个典型的：

> declared-contract PASS ≠ rendered-artifact PASS

### 修复方案

不要手改 PDF。

修改 source code：

- `apply_npj_sba_style()` 在 npj contract 完成后不再执行 generic clamp；
- 或将 generic branch 与 npj branch彻底拆开；
- 新增 exported-PDF postflight，逐张验证：
  - font family；
  - visible font range；
  - min positive line width；
  - width/height；
  - single page；
  - text clipping；
  - source-data SHA。

然后**统一重渲染 5 主图 + S1-S10 全 15 张**。

科学 source data 必须继续 15/15 byte-identical。

---

## 7. P0-2：`npj_statistics_reporting_map.csv` 存在 claim/decision 语义反向

当前 map 的 decision 大多正确，但部分 `claim` 字段写成了待检验命题或相反结论。

### 具体问题

#### R1

当前 claim：

> End-to-end broad-state reproducibility criterion held

但 decision：

> `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

应改成类似：

> End-to-end broad-state reproducibility did not meet the frozen state-specific criterion because B_ASC median Jaccard was below 0.95.

#### C3_PRIMARY

当前 claim：

> Primary B_ASC composition differs in managed SLE

但 decision：

> `NOT_SUPPORTED`

应改成：

> The primary B_ASC composition analysis did not support a difference in managed SLE.

#### C5_GENOMEWIDE

当前 claim：

> Genome-wide effects agree across datasets

但 decision：

> `WEAK_RHO_0.026`

应改成：

> Genome-wide cross-dataset effect concordance was weak (Spearman rho=0.026).

#### TF_DEPLETION

当前 claim：

> STAT1/STAT2 evidence is overlap-independent

但 decision：

> `NOT_SUPPORTED_FOR_BROAD_M5911_INDEPENDENCE`

应改成：

> Narrow 12-gene depletion retained support, but broader M5911 depletion did not support overlap-independent STAT1/STAT2 regulation.

### 风险

这个文件位于最终 package 的 `06_Integrity`，如果作为 reviewer/reproducibility material 被查看，会造成：

> machine-readable decision 与 human-readable claim 自相矛盾。

### 修复方案

修 builder，不手改 CSV。

增加 regression tests：

- HOLD/NOT_SUPPORTED row 不允许 claim 使用 `held`, `differs`, `agree`, `independent` 等反向肯定语句；
- 至少对 R1/C3/C5_GENOMEWIDE/TF_DEPLETION 做 exact expected-claim assertion。

---

## 8. P0-3：GitHub root README / REPRODUCIBILITY 再次落后于 target-specific state

最新 `main` 已经包含 target-specific refreeze 和 final audit。

但 root README 仍写：

- no target-specific submission package has been created；
- no journal is formally selected；
- next stage is JCR Q1 journal selection and target adaptation。

这与当前事实冲突。

当前 `REPRODUCIBILITY.md` 仍写：

- no target journal is fixed；
- target-specific title/abstract/layout/figure dimensions/cover letter 仍待构建；
- earlier release environment 段落仍称 LibreOffice unavailable / no cross-renderer verification。

而本轮 target action record 已经记录：

- target = npj Systems Biology and Applications；
- package 已构建；
- WPS + LibreOffice 51 pages cross-render PASS。

### 风险

Manuscript 的 Code Availability 会直接把 reviewer 带到 GitHub。

因此 public root documentation 不应比 target package 落后一轮。

### 修复方案

只改 current `main` reader-facing status：

- README；
- REPRODUCIBILITY；
- 可选 `CURRENT_SUBMISSION_STATUS.md`。

不要：

- 移动 v1.1.0 tag；
- 修改 Zenodo 22151739；
- 改 scientific release commit；
- 重跑 biology。

---

## 9. P1：最后一次 reader-facing semantic hardening

由于所有图现在本来就需要 source-driven rerender，建议顺手修正以下措辞。

### Figure 2b

当前 panel title：

> No primary B_ASC enrichment

但 95% CI 并未证明等价或排除增加。

正文自己已经正确说明：

> interval does not establish equivalent abundance or exclude an increase.

因此 panel title 建议：

> **Primary B_ASC enrichment not supported**

比 `No ... enrichment` 更严格。

### GSE135779 external replication

当前：

- Results heading：`Independent GSE135779 replicates IFN/ISG...`
- Figure 4：`Independent GSE135779 validation`
- Figure 1 workflow：`GSE135779 independent replication`

“independent”在 cohort 意义上正确，但由于 C9R 的 label-independent transfer 失败，敌意 reviewer 可能把它读成 identity transfer 也 independent。

建议统一改成：

- Results heading：
  **Independent GSE135779 provides source-label-defined replication of IFN/ISG despite low genome-wide concordance**
- Figure 4 title/legend：
  **GSE135779 provides source-label-defined replication of the frozen IFN/ISG program**
- Figure 4 panel a：
  **Source-label-defined GSE135779 validation**
- Figure 1 node：
  **GSE135779 source-label-defined replication**

这是 claim precision，不是降级科学结果。

### Introduction 的 framing

当前一句：

> neither interferon activity nor plasmablast biology is novel

虽然诚实，但 editorial framing 略有自我削弱。

建议改成：

> interferon activity and plasmablast biology are well established in SLE, but both are strongly context dependent.

这样仍不冒充 novelty，同时更自然地把 novelty 转向 inferential hierarchy。

---

## 10. Reporting Summary / Editorial Policy Checklist：当前仍只是 draft

package 中目前是 Markdown draft。

官方 Nature Partner Journal Guide 明确要求 life-science research article 提供：

- completed reporting summary；
- all-author editorial policy checklist。

因此正式 portal preflight 前仍需：

1. 下载/打开当期官方表单；
2. 将现有 draft 内容转录；
3. 处理 sex/gender reporting 等适用字段；
4. 两位作者复核；
5. 以官方表单格式保存。

当前不需要为了 sex/gender reporting 临时做 post-hoc analysis。

如果跨 cohort 没有一致 sex covariate，应在表单中如实说明设计/metadata limitation。

---

## 11. JCR 与 APC

Nature 官方当前页面可以确认：

- journal active；
- SCIE indexed；
- 2025 JIF = 4.4；
- 5-year JIF = 4.2；
- median first editorial decision = 8 days；
- median submission-to-acceptance = 155 days。

但这些信息**不能替代正式 JCR quartile receipt**。

如果用户要求“JCR Q1 / SCI 一区”为硬门槛，则仍需机构或 Clarivate JCR profile 保存：

- metric year；
- category/categories；
- rank / denominator；
- quartile。

当前 npj Original Research APC：

- £2,690
- US$3,490
- €2,990
- plus applicable taxes。

Springer Nature 公共 agreement 页面列出 `The Chinese University of Hong Kong` 的 Nature Portfolio coverage，但不能自动推导 `The Chinese University of Hong Kong, Shenzhen` 的 eligibility。

因此 CUHK-Shenzhen 应取得书面/系统 eligibility confirmation。

---

## 12. Figure / Supplement visual audit

### Main figures

整体视觉结构已经成熟：

- Figure 1：evidence hierarchy 清楚；
- Figure 2：composition null 与 secondary flare 分层清楚；
- Figure 3：program hierarchy 和 gene coherence 清楚；
- Figure 4：program-specific replication 与 low genome-wide rho 并置有效；
- Figure 5：regulator / M5911 / perturbation 三分支避免了因果链误读。

没有发现：

- clipping；
- missing label；
- broken panel；
- page overflow。

### Supplement

18-page merged PDF结构清楚。

S1-S10 诊断覆盖足够，不需要再新增 Supplementary Figure。

S8 图因信息量大跨 legend/figure 两页，不是科学问题；当前可读性可接受。

---

## 13. 是否还应新增科学分析

**不建议。**

当前最可能提高首投成功率的动作不是增加一个新的 positive analysis，而是：

1. 修图件 style implementation bug；
2. 修统计 reporting map 的语义；
3. 修 public GitHub reader-facing status；
4. 做最后一次 source-label-defined / null-result semantic hardening；
5. 完成官方表单与作者/机构 gate。

新增分析的边际收益已经低于 post-hoc 风险。

---

## 14. 当前 readiness

| 模块 | 独立判断 |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1/C9R transparency | 99% |
| External replication claim boundary | 96% |
| Regulator claim boundary | 98% |
| Manuscript logic | 98% |
| Target manuscript structure | 99% |
| Supplement structure | 98% |
| Scientific source-data integrity | 100% |
| Package byte integrity | 100% |
| Main-figure visual quality | 97% |
| npj exported-line-style compliance | **88%** |
| Machine-readable statistics-map semantics | **82%** |
| GitHub public current-state documentation | **80%** |
| Reporting Summary / policy form completion | 70% |
| JCR Q1 institutional verification | pending |
| APC/OA institutional verification | pending |
| Exact-file author approval | pending |
| Overall first-submission readiness | **~92%** |

---

## 15. 下一阶段

不要直接 author-sign 当前 hash。

先做：

`NPJ_SBA_FINAL_SEMANTIC_AND_RENDER_HARDENING`

### P0 execution order

1. 修 `publication_style_contract.py` 的 npj branch；
2. 增加 exported-PDF line/font postflight；
3. source-driven rerender all 15 figures；
4. 继续要求 15/15 source-data SHA byte-identical；
5. 修 Figure 2 null wording；
6. 修 GSE135779 source-label-defined reader-facing wording；
7. 修 `npj_statistics_reporting_map.csv` builder + tests；
8. 更新 README / REPRODUCIBILITY；
9. rebuild Manuscript / Supplement / Cover Letter；
10. WPS + LibreOffice QA；
11. deterministic package rebuild；
12. 生成新 exact hashes；
13. 再进入 author approval。

### 然后

`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

完成：

- 两位作者 exact-file approval；
- official JCR Q1 receipt；
- CUHK-Shenzhen APC/OA receipt；
- official Reporting Summary；
- official Editorial Policy Checklist；
- corresponding-author portal authorization。

---

## 16. STOP rules

本阶段不得：

- 新增 cohort；
- 改 disease contrast；
- 改 threshold；
- 换 mapper；
- 救 R1；
- 救 C9R；
- 增加 TF/regulon family；
- 增加 gene-set family；
- 重新打开 corrected external disease outcome；
- 手工编辑 PDF 图。

---

## 17. 最终导师结论

论文科学主体已经成熟，目标期刊匹配度高。

但当前 `PASS_NPJ_SBA_TARGET_SPECIFIC_REFREEZE_AUTHOR_APPROVAL_REQUIRED` 存在一个可复现的 figure-style implementation false positive，以及一个 machine-readable claim/decision semantic inconsistency。

因此当前最值得做的不是再增加分析，而是完成一次**最后的源代码驱动技术硬化**。

修完后，项目才应该冻结 exact hashes 并交两位作者签字。
