# SLE B-cell remodeling：作者确认后 JCR Q1 投稿前独立终局审计

日期：2026-08-28  
项目：`1209433622cz-maker/sle-bcell-remodeling`  
GitHub latest main：`c68775982f47a637dbc2bfa1b89df3640984b31d`  
作者确认包：`author_confirmed_review.zip`  
作者确认包 SHA-256：`0363C066FB7F8FAD5E867FC820ED7F80C8F3D1A10E0A1CB43B8A7A51FCA92234`  
当前科学边界：
- R1：`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`
- C9 原 PASS：撤回支持性效力
- C9R corrected calibration：`HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- corrected C9 disease outcomes：未解锁、未估计
- source-label-defined GSE135779 childhood IFN/ISG replication：保留
- 作者对 identified reviewed snapshot：`CONFIRMED_REVIEWED_SNAPSHOT`
- 投稿授权：否
- 目标期刊：未选择
- 选刊硬条件：JCR Q1

---

## 1. 导师总判断

项目科学主体已经完成，不应再开启新的 exploratory science gate。

目前不是“再跑什么分析能提高论文”，而是“如何把已经透明、边界清楚的科学证据转化为一个符合 JCR Q1 目标期刊格式、修正已知 Figure 1c 标注错误、绑定新 DOI 并获得最终文件级作者授权的 submission release”。

下一阶段建议正式定义为：

`JCR_Q1_JOURNAL_SELECTION_AND_FINAL_CORRECTION_REFREEZE`

当前唯一明确的 submission-facing P0 技术错误是：

> 作者确认包中的 Figure 1c 和对应 legend 仍把 0.990 虚线错误写成 minimum mapped-ARI criterion；冻结规则中 0.990 实际是 minimum mapping-agreement criterion，minimum mapped-ARI criterion 是 0.900。

绘图源代码已经修复并生成独立 preview，但修正尚未整合进 author-confirmed package。该错误不改变任何科学数值，但在最终稿必须通过代码重绘和文档重建关闭。

---

## 2. author_confirmed_review.zip 独立完整性核验

独立检查：

- ZIP bytes：26,034,837
- SHA-256：`0363C066FB7F8FAD5E867FC820ED7F80C8F3D1A10E0A1CB43B8A7A51FCA92234`
- ZIP entries：76
- manifest payload：75
- payload size/SHA：75/75 PASS
- missing：0
- unexpected：0

STATUS：

- review_only = true
- submission_authorized = false
- author_reapproval = `CONFIRMED_REVIEWED_SNAPSHOT`
- external_methods_review_status = `FEEDBACK_RECEIVED_CLOSURE_PENDING`
- target_journal = null
- matching_archive_doi = null
- corrected_disease_outcomes_estimated = false
- calibration_status = `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- identity_status = `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

11 个 portal roles 全部仍为：

`DRAFT_NOT_FOR_UPLOAD`

所以作者内容确认并不等于 portal upload authorization；这个治理逻辑正确。

---

## 3. 文档和图件独立复核

当前包：

- Manuscript PDF：34 页
- Supplementary Information PDF：19 页
- Research Proposal PDF：6 页
- Cover Letter PDF：1 页
- 总计：60 页

Publication figures：

- 5 main figures
- 10 supplementary figures
- 全部 170 mm 宽
- Arial / Arial Bold
- vector PDF
- visible text minimum = 5 pt
- non-panel maximum = 7 pt
- panel labels = 8 pt

因此当前 typography 已达到严格 Nature-style 核心规范：

- Arial/Helvetica
- panel labels 8 pt bold lower-case
- other text 5–7 pt
- editable/vector artwork

不建议为了“更像 Nature”在未选刊前把 170 mm 强制改成 Nature 183 mm。最终 width 应由目标期刊决定，然后从代码一次性 rerender。

---

## 4. Figure 1c 是当前唯一确定的图件 blocker

author_confirmed_review.zip 中 Figure 1c 的 PDF 文本仍是：

`minimum mapped-ARI criterion`

而 current Manuscript Figure 1 legend 仍写：

> the dashed horizontal guide marks the minimum mapped-ARI criterion of 0.990.

冻结规则实际为：

- minimum mapped ARI >= 0.900
- minimum mapping agreement >= 0.990

所以这不是审美问题，而是 threshold type 写错。

正确修复已经在代码中完成：

- 不移动线
- 不改阈值
- 不改 Source Data
- 只把 panel c 标注改为 `minimum agreement criterion`
- legend 改为 `minimum mapping-agreement criterion of 0.990`

最终必须：

1. 从修复后的 builder 重跑 Figure 1；
2. 同步替换 legend；
3. 再构建 Manuscript DOCX/PDF；
4. 做 Figure 1/legend semantic assertion；
5. 对这个 delta 做最终作者确认。

不要手工编辑 PDF。

---

## 5. 科学证据链最终评价

当前最稳的中央证据仍成立：

1. GSE174188 150,402 B-lineage cells；
2. 259 donors / 271 samples / 88 libraries；
3. fine-grained hard state assignments 不满足稳定 disease inference；
4. frozen-representation B_CONV/B_ASC 可作为 analysis scaffold；
5. full end-to-end R1 正式 HOLD，且 failure B_ASC-specific：
   - B_ASC median Jaccard 0.930323 < 0.95
   - B_CONV median Jaccard ~0.99936
6. identity-boundary propagation 后 primary B_ASC composition null 保持；
7. primary B_CONV IFN/ISG positive；
8. donor-nonoverlap internal IFN/ISG positive；
9. source-label-defined independent GSE135779 childhood IFN/ISG replication 保留；
10. genome-wide rho=0.026，明确拒绝 transcriptome-wide replication；
11. STAT1/STAT2 ULM + CAMERA/FRY = convergent observational evidence；
12. narrow 12-gene depletion 不能解释全部 regulator signal；
13. M5911 depletion 明显削弱 discovery STAT2，因此不支持 overlap-independent regulation；
14. GSE23307 n=2 仅 descriptive；
15. corrected source-label-agnostic mapping calibration HOLD，未估计 corrected disease outcomes。

最强 conceptual contribution：

> Inferential granularity must be validated rather than assumed: hard state membership has explicit reproducibility limits, whereas process-level IFN remodeling survives biological-unit inference, identity-boundary propagation and independent source-label-defined cohort validation.

不应再新增 cohort / mapper / TF / signature 去提高“PASS 数量”。

---

## 6. Manuscript 写作逻辑

### 当前结构优点

当前 narrative 顺序已经很好：

1. identity validity
2. composition
3. within-B_CONV transcription
4. independent source-label-defined validation
5. corrected external-mapping limitation
6. regulator / response convergence
7. explicit claim boundaries

标题里的 `state assignments` 比旧的 `states` 更准确，建议保留这一语义原则。

### 当前 manuscript 小计

- Abstract：约 342 words
- Background：约 432 words
- Methods：约 2,095 words
- Results：约 2,064 words
- Discussion：约 902 words
- Background + Results + Discussion：约 3,398 words

所以正文长度不是主要问题；目标期刊一旦选定，最可能需要重构的是 abstract/title 格式，而不是删科学内容。

### 一个 P1 文字修正

GSE135779 source-label omission 当前写：

> excluding dependence on a single source label

建议改为：

> arguing against dependence on any single contributing source label

因为逐个 omission 支持“不是被某一个 label 单独驱动”，但不能逻辑上完全排除 source-annotation scheme 的组合依赖。

---

## 7. AI disclosure 的目标期刊适配

当前 AI disclosure 放在 Declarations。

Nature Portfolio 当前指导要求 LLM use 应在 Methods 中透明记录；Communications Biology 的当前 Submission Guidelines 明确要求 LLM use documented in Methods。

所以如果最终选择 npj Systems Biology and Applications 或 Communications Biology：

- 保留现有作者责任边界；
- 在 Methods 加一个很短的 `Generative AI assistance` / `Software and AI assistance` subsection；
- 可以在 Declarations 保留或按期刊模板移动；
- 不改变作者贡献或科学内容。

这是 journal-policy formatting，不是新的研究分析。

---

## 8. JCR Q1 候选期刊重新排序

### A. npj Systems Biology and Applications — fit-based lead，前提是 JCR Q1 被正式核实

官方 scope 明确包括：

- computational/mathematical analysis of complex biological systems
- disease modeling
- single-cell systems biology
- systems immunology

Publisher-reported 2025 JIF = 4.4。

当前还有 open `Systems immunology` Collection，deadline = 12 September 2026。

与本文的逻辑匹配非常高：

> state-assignment uncertainty + process-level reproducibility + systems immunology + computational single-cell inference

但 public publisher pages 不提供足够的 current JCR category/quartile proof，因此正式列为首选前必须取得机构 JCR profile/export，记录：

- metric year
- category
- rank
- quartile

### B. Communications Biology — 并列强候选

官方 scope 明确接受：

- secondary data analysis
- innovative computational methods

并强调：

- novel insight
- strong evidence
- technically sound data
- significance to the biological subfield

Publisher-reported current JIF = 5.8。

从 paper-to-journal fit 和当前透明 robustness 结构看，它是非常自然的 Nature Portfolio 目标。

同样，JCR Q1 必须正式核实，不能由 JIF 推断。

### C. Genome Medicine — stretch candidate

科学 scope 仍匹配，但 desk risk 更高：

- IFN biology 已知；
- public-data secondary analysis；
- source-label-independent external robustness 未建立；
- no prospective treatment cohort；
- no direct patient functional perturbation；
- no clinical utility demonstration。

如果目标是“最大医学影响力”，可以考虑；
如果目标是“JCR Q1 + 逻辑匹配 + 不重构科学故事”，优先核查 npj Systems Biology and Applications / Communications Biology。

---

## 9. 如果选择 Nature Portfolio 候选，标题和 abstract 建议

当前 title 约 16 words；若目标 journal 使用约 15-word title guide，应压短。

建议 candidate title：

> **Interferon remodeling persists despite uncertain B-cell state assignments in systemic lupus erythematosus**

它保留：

- process-level IFN
- state-assignment uncertainty
- disease context

并避免暗示 biological states 本身不存在。

### Candidate ~130-word unstructured abstract

> Systemic lupus erythematosus B-cell studies can conflate cell identity, abundance and transcriptional state. We reanalysed public single-cell datasets using disease-blind reconstruction and donor-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a prespecified antibody-secreting-cell state-overlap criterion, whereas propagating assignment uncertainty preserved the primary composition null and conventional-B IFN/ISG effects. The IFN/ISG program replicated in 43 independent childhood donors using a source-label-defined broad B-cell analog despite weak genome-wide effect concordance. A post-freeze attempt to reconstruct the external mapping without source labels failed corrected B_ASC reference calibration, so no corrected disease outcome was estimated. STAT1/STAT2 analyses provided convergent but observational support, with attenuation after broader interferon-gene depletion. These results support reproducible process-level interferon remodeling without establishing a universal B-cell taxonomy, causal regulator or unique upstream stimulus.

这是 journal-format candidate，不应覆盖已批准 manuscript，直到具体期刊确定。

---

## 10. 外部方法审阅的真实状态

当前：

`FEEDBACK_RECEIVED_CLOSURE_PENDING`

作者已经确认：

- reviewed current materials；
- considered external methodological feedback and disposition。

但是：

- reviewer identity 未经认证；
- independence 未经认证；
- 没有独立 methods-decision signature。

这个缺口应继续透明保留。

它不是一般期刊投稿的硬性要求，因此不应无限期阻塞选刊和 formatting。

如果能找到真正独立的生信/单细胞同行做 12-question dossier review，这是高价值 P1；
如果没有，不应由同一个分析代理自我认证成“independent external review”。

---

## 11. Release governance

当前 author confirmation 只绑定 identified reviewed snapshot。

它不授权：

- Figure 1c 后续修正版；
- journal-specific title/abstract restructuring；
- final journal-formatted documents；
- new GitHub release；
- Zenodo new version；
- actual portal upload。

因此最有效率的流程不是现在再向作者请求一次确认，而是：

1. 先选定 JCR Q1 journal；
2. 一次性整合 Figure 1c；
3. 一次性做 target-journal title/abstract/section/AI-policy formatting；
4. 从代码 rerender final figures；
5. rebuild all documents；
6. new release DOI；
7. 最后只做一次 exact-hash final author approval。

---

## 12. 当前完成度

| Module | Readiness |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1 boundary transparency | 99% |
| Identity uncertainty propagation | 98% |
| Source-label-defined independent validation | 96% |
| Source-label-independent external robustness | HOLD / unresolved |
| Regulatory robustness | 97% |
| Manuscript logic | 98% |
| Main figure science | 99% |
| Nature typography | 99% |
| Figure 1 final semantic correctness | 90% — corrected preview exists, package still old |
| Supplementary evidence | 98% |
| Source-data traceability | 99% |
| Reproducibility | 98% |
| Author approval of reviewed snapshot | 100% |
| Author approval of final future formatted payload | pending |
| Verified JCR Q1 target | pending |
| Matching new archive DOI | pending |
| Portal-ready package | pending |

---

## 13. 下一阶段唯一正确目标

`JCR_Q1_JOURNAL_SELECTION_AND_FINAL_CORRECTION_REFREEZE`

### Phase A — journal decision

1. obtain institutional/current JCR evidence；
2. verify category + quartile + metric year；
3. select target；
4. record APC/waiver implications separately。

### Phase B — one-shot final source rebuild

1. integrate Figure 1c corrected source + legend；
2. rerun Figure 1 from code；
3. ideally rerun all figures with the selected journal's exact final dimensions；
4. preserve all figure Source Data；
5. target-specific title；
6. target-specific abstract；
7. target-specific section order；
8. AI-use disclosure in required location；
9. keep R1 HOLD and C9R HOLD unchanged。

### Phase C — final release

1. full DOCX/PDF rebuild；
2. WPS all-page audit；
3. accessibility；
4. figure semantics/font/size assertions；
5. deterministic package；
6. exact final Git commit；
7. create new release tag such as `v1.1.0` without moving v1.0.0；
8. Zenodo New Version；
9. exact version DOI insertion；
10. rebuild again after DOI insertion；
11. exact-hash author approval and explicit submission authorization；
12. portal preflight；
13. submit and freeze receipt.

---

## 14. STOP rules

Before first submission, do not:

- open a new cohort；
- retune C9；
- replace failed elastic mapper with centroid；
- alter R1 thresholds；
- search new TF/regulon databases；
- add new gene-set families；
- change seeds to obtain PASS；
- manually alter final PDF figures。

Only a newly discovered decision-changing implementation defect should reopen computation.

---

## 15. 最终导师判断

这篇稿件现在最值得保护的是它的“可信度结构”，而不是继续增加阳性结果。

R1 和 C9R 的 HOLD 并没有摧毁论文；相反，它们证明作者愿意让预定义门槛约束自己的结论。

当前文章已经能够非常清楚地区分：

- taxonomy-level uncertainty；
- composition-level null；
- process-level replicated IFN signal；
- observational regulatory convergence；
- unresolved source-label-independent transfer。

真正剩余的 P0 是：

**正式核实 JCR Q1 目标 → 一次性整合 Figure 1c + journal formatting → 新版本 DOI → exact-file final author approval → submit。**
