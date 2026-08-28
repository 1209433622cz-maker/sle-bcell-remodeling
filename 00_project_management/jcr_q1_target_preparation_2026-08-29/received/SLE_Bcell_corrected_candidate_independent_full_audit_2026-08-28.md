# SLE B-cell remodeling：Corrected Candidate 独立全量审计与 JCR Q1 最终冻结建议

日期：2026-08-28  
项目：`1209433622cz-maker/sle-bcell-remodeling`  
GitHub latest main：`74678c7cf75e376d90cdae886b6a1a4cf1951714`  
Candidate source commit：`05e41f40284fc65c6cd18bbecaa2bf507e81b5f8`  
当前候选包：`corrected_candidate.zip`  
Candidate SHA-256：`D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150`  
Manifest payload：82/82 PASS  
当前状态：journal-neutral corrected candidate；submission authorization = false  
选刊硬条件：JCR Q1；具体期刊未冻结  
历史 DOI：`10.5281/zenodo.22086892`，仅对应旧 snapshot；最终修订版需要新 version-specific DOI

## 一、导师总判断

当前 corrected candidate 已关闭上一轮唯一确定的 submission-facing 图件语义错误：

- Figure 1c 的 0.990 guide 已从错误的 `minimum mapped-ARI criterion` 改为正确的 `minimum agreement criterion`；
- Figure 1 legend 已同步改为 `minimum mapping-agreement criterion of 0.990`；
- Figure 1a interpretation boxes 的重叠已通过源码重排解决；
- Figure 1 Source Data SHA 保持 `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`；
- 其他 14 张 publication figures 与上一审阅 build 保持冻结；
- source-label omission 的 `excluding dependence` 已降级为 `arguing against dependence`；
- manuscript 数字 token 未改变；
- R1 HOLD、C9R HOLD、未估计 corrected external disease outcomes 等科学边界全部保持。

因此：**首投前不应重新打开 exploratory science。**

真正剩余的工作已收敛为：

`JCR Q1 journal verification → target selection → one-shot journal formatting → final exact-file approval → revised release/DOI → portal submission`

## 二、Candidate ZIP 独立完整性

独立检查：

- ZIP bytes：26,632,739
- SHA-256：`D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150`
- ZIP entries：83（含 manifest）
- manifest payload：82
- size/hash：82/82 PASS
- missing：0
- unexpected：0

STATUS：

- `review_only = true`
- `submission_authorized = false`
- `author_reapproval = PENDING_CORRECTED_CANDIDATE`
- `prior_author_approval = CONFIRMED_REVIEWED_SNAPSHOT`
- `target_journal = null`
- `matching_archive_doi = null`
- `corrected_disease_outcomes_estimated = false`
- `calibration_status = HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- `identity_status = HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

11 个 portal roles 全部仍为 `DRAFT_NOT_FOR_UPLOAD`。

## 三、文档 QA

当前 candidate：

- Manuscript：34 页
- Supplement：19 页
- Research Proposal：6 页
- Cover Letter：1 页
- 总计：60 页

Package audit：

- accessibility：4/4 DOCX 均 0 high / 0 medium / 0 low findings
- semantic checks：13/13 PASS
- Figure 1 fresh assertions：9/9 PASS
- candidate portable verification：PASS
- source/commit provenance：PASS

独立渲染 34 页 Manuscript contact sheet 未见新增裁切、空白页、字符缺失或明显版面溢出。

## 四、Figure 1 纠错独立确认

当前 PDF 中 panel c 已显示：

`minimum agreement criterion`

line = 0.990。

真实 frozen criteria：

- minimum mapped ARI >= 0.900
- minimum mapping agreement >= 0.990

因此最新 Figure 1 和 legend 现在语义一致。

Figure 1a 的底部 interpretation nodes 已分离，无重叠；整体 evidence hierarchy 清晰。

## 五、15 张图 Nature-style audit

独立 PDF 结构检查：

- Figures 1-5 + S1-S10 共 15 张
- 全部 width = 170.0 mm
- 全部 Arial/Arial Bold
- 最小可见正文 = 5.0-6.0 pt
- 最大非 panel text <=7 pt
- 唯一 8 pt 字符均为 lower-case bold panel labels
- vector PDF
- all figure heights <=163.05 mm

当前 journal-neutral typography 达到严格 Nature general style 的核心要求。

但 170 mm 是 review/candidate width，不应被当作所有 Nature Portfolio 子刊的 final production width。目标期刊确定后应从代码重新应用其自身尺寸、字体和线宽要求。

## 六、科学证据链最终冻结

核心结果不变：

1. GSE174188 150,402 B-lineage cells；259 donors / 271 samples / 88 libraries。
2. Fine-grained state assignments 不足以承担稳定 disease inference。
3. B_CONV/B_ASC 仅作为 analysis scaffold。
4. R1 end-to-end HOLD：B_ASC median Jaccard 0.930323 < 0.95；B_CONV 稳定。
5. Boundary propagation 保留 primary B_ASC composition null 和 B_CONV IFN/ISG effects。
6. Primary B_ASC OR 0.947，95% CI 0.636-1.410，P=0.787。
7. Primary B_CONV IFN/ISG effect 0.837；donor-nonoverlap 1.086。
8. Source-label-defined independent GSE135779 childhood effect 1.042。
9. Genome-wide rho=0.026；只授权 program-specific replication。
10. STAT1/STAT2 为 observational convergent evidence。
11. CAMERA 6/6 同向、5/6 BH-significant；FRY 6/6 同向并 significant。
12. M5911 depletion materially attenuates discovery STAT2；不授权 overlap-independent regulation。
13. GSE23307 n=2 descriptive。
14. C9R corrected calibration HOLD；无 corrected disease outcome。
15. 不支持 universal taxonomy、discrete IFN-high subtype、causal TF、unique ligand 或 clinical utility。

当前最强 conceptual contribution：

> Hard cell-state membership has explicit reproducibility limits, whereas process-level IFN remodeling survives biological-unit-aware inference, assignment-boundary propagation and independent source-label-defined cohort validation.

## 七、Manuscript 逻辑与写作

当前 title = 16 words：

`Disease-blind single-cell reconstruction separates unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus`

Abstract 当前约 337 words。

Background ~431 words；Methods ~2,080；Results ~2,050；Discussion ~896。

结构已足够成熟；首投前不要再增加结果层。

如果最终选择 Communications Biology/Nature Portfolio 风格，推荐采用更短的 reader-facing title：

`Interferon remodeling persists despite uncertain B-cell state assignments in systemic lupus erythematosus`

并把 Abstract 重新写为 <=150-word unstructured summary。该修改只应在具体目标期刊确认后一次性完成，不应现在覆盖 journal-neutral approved science source。

## 八、S10 的唯一可选图形优化

S10 当前科学上 PASS：

- matched/corrected normalization
- state-specific precision
- coverage
- donor-grouped calibration folds

但 panel d 的 balanced accuracy 很高，可能使非专业读者疑惑“为何 overall accuracy 高但仍 HOLD”。

若外部方法审阅者也认为需要增强，可仅从冻结 calibration candidate table 重画为：

`coverage vs B_ASC precision calibration frontier`

并显示 eligible quadrant：

- coverage >=0.80
- B_ASC precision >=0.90

这属于 P1 reader-communication improvement，不是科学 P0，且不能改变 mapper、grid 或 threshold。

## 九、JCR Q1 目标策略

### 1. npj Systems Biology and Applications — conditional lead

Fit 很高：
- computational analysis of complex biological systems
- disease modeling
- single-cell systems biology
- systems immunology

Publisher 2025 JIF = 4.4。

公共第三方当前记录将其列为 2025 JCR Q1，但正式项目 gate 仍应以 Clarivate/institutional JCR profile/export 为准，记录完整 category/rank/quartile。

### 2. Communications Biology — parallel strong candidate

Scope 明确接受：
- secondary data analysis
- innovative computational methods

Publisher 2025 JIF = 5.8。

其 editorial emphasis 是 novel biological insight + strong evidence + technical soundness。当前稿件证据透明度与其匹配很好。

公共 Springer Nature research-service material/第三方均指向 Q1，但正式提交 gate 同样应保留机构 JCR export。

### 3. Genome Medicine — stretch

Human genomics/systems medicine scope 仍匹配，但 desk risk 较高：

- IFN biology 已知
- secondary public-data analysis
- source-label-independent external robustness 未建立
- no prospective clinical cohort
- no direct matched patient perturbation
- no clinical utility demonstrated

因此不应因为历史 preparation inertia 继续默认 Genome Medicine。

## 十、下一阶段

建议定义：

`JCR_Q1_TARGET_SELECTION_AND_FINAL_FILE_FREEZE`

执行顺序：

1. 获取官方/机构 JCR profile/export；
2. 记录 metric year、所有 assigned categories、rank/denominator、quartile；
3. 若 npj SBA 与 Communications Biology 均 Q1，则优先按 fit 决策；
4. 确认 APC/waiver feasibility；
5. 只做一次 target-journal source reformat：
   - title
   - abstract
   - section order
   - AI disclosure placement
   - figure final dimensions/fonts/line widths
6. 不改变任何科学 HOLD 或结果；
7. rebuild DOCX/PDF；
8. WPS all-page QA + accessibility + semantic assertions；
9. freeze exact final commit；
10. create new tag/version（建议 v1.1.0，不移动 v1.0.0）；
11. Zenodo New Version；
12. insert exact version-specific DOI；
13. rebuild after DOI insertion；
14. 两位作者批准 exact final hashes；
15. 明确 submission authorization；
16. portal preflight；
17. submit and freeze receipt/manuscript number/upload hashes。

## 十一、STOP 规则

首投前不再：

- 新 cohort
- 新 clustering
- 新 mapper
- threshold relaxation
- seed rescue
- new TF/regulon database
- new gene-set family
- outcome-informed C9 rescue
- manual PDF figure editing

只有新发现的 decision-changing implementation defect 才允许重新打开计算。

## 十二、最终导师判断

Corrected candidate 已经解决 Figure 1c 的最后一个明确 presentation error，并保持所有科学 source data 与统计结果冻结。

当前论文最值得保护的是它的可信度结构：

- R1 HOLD 被保留；
- C9 原错误 PASS 被撤回；
- C9R fail-closed；
- independent source-label-defined IFN replication 仍成立；
- global transcriptome replication 被明确否定；
- regulator/perturbation evidence 受严格因果边界约束。

因此，后续“追求完美”的正确方向已经不是增加分析，而是：

**正式 JCR Q1 选刊 → 一次性 journal-specific refreeze → exact-file author approval → new DOI → submit。**
