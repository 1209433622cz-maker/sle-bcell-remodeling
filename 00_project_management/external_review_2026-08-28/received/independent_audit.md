# SLE B-cell remodeling：C9 技术纠错后独立终局审计与下一阶段建议

日期：2026-08-28  
项目：`1209433622cz-maker/sle-bcell-remodeling`  
GitHub latest main：`f28cf6a481232408710862eee5ee2db735dec70b`  
当前科学状态：
- R1：`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`
- C9 原 PASS：已撤回支持性效力
- C9R corrected calibration：`HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- corrected C9 disease outcomes：未解锁、未估计
- correction review bundle：技术完整性 PASS，但 review-only / NOT FOR UPLOAD
- renewed author approval：PENDING
- target journal：未冻结

---

## 1. 导师总判断

这次 C9 技术纠错是项目治理上非常重要的一次“负面修正”。

旧 C9 的正向结果不能继续作为论文支持性证据，原因不是后来出现了一个阴性疾病效应，而是原先 outcome unlock 本身不满足冻结校准门槛，而且参考/外部 mapper 输入的 library-size denominator 不一致。

纠错后：

- reference 与 external 均按 full-library log1p(CP10K) 后再 feature-subset；
- calibration gate fail-closed；
- elastic-net B_ASC precision = 0.885210 < 0.90；
- corrected outcome access = false；
- 无 corrected disease effect / CI / P / q；
- centroid 单独通过不能被事后升级成替代验证器。

因此正式结论必须是：

> Source-label-defined GSE135779 primary IFN/ISG replication remains part of the central evidence, but source-label-independent external robustness is not established.

这不会推翻现有 IFN 主结论；它撤回的是一条额外 robustness claim。

---

## 2. 独立文件与包完整性核验

### correction_review.zip

独立复核：

- bytes：26,013,157
- SHA-256：`DA07D1D7F87E559A7778618FDFAE5BD55DA77291E1F0BAA44B915CDE209B5993`
- ZIP entries：69
- manifest payload：68
- payload size/SHA：68/68 PASS
- missing：0
- unexpected：0

状态文件明确：

- `review_only = true`
- `submission_authorized = false`
- `author_reapproval = PENDING`
- `target_journal = null`
- `matching_archive_doi = null`
- `corrected_disease_outcomes_estimated = false`
- `calibration_status = HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- `identity_status = HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`

11 个 portal roles 全部为 `DRAFT_NOT_FOR_UPLOAD`。

### Nested archives

- Figure Source Data：15/15 manifest PASS
- Full Statistical Results：184/184 manifest PASS
- historical scientific payloads：163 unchanged
- corrected calibration extension：20 files

### 6013RP-wyf(1).zip

- bytes：285,531,381
- SHA-256：`B7368F5EAF6C46B529F8B4E7935F61DBB29E490653164B4B59BA075AD636ECB0`
- entries：872
- embedded `04_submission/correction_review.zip` 与独立上传 review ZIP 字节完全一致
- `Manuscript.md` / `Supplementary_Information.md` / `Research_Proposal.md` / `Cover_Letter.md` 与 review bundle 中 source files 字节一致

它是 manuscript/release-engineering workspace snapshot，不是完整 analysis-run archive；完整可重现性仍依赖 exact Git commit、tracked compact outputs、公共原始数据获取记录及后续 version-specific archive。

---

## 3. C9 纠错：技术判断

### 原 C9 两个阻断缺陷

1. reference mapper 先截取约 601 个 features，再用 feature-only count total 做 CP10K；
2. external data 使用 full-transcriptome library total 做 CP10K 后再 feature subset。

因此 reference/external feature vectors 不在同一 normalization denominator 下。

第二个缺陷是：

- 原 elastic threshold = 0.95；
- B_ASC precision 未达到冻结 0.90；
- fallback threshold 却能够授权 outcome unlock。

这使旧 C9 PASS 的 gate authorization 无效。

### Corrected C9R

冻结规则未改：

- 56 matrices / 363,083 cells；
- 353,527 QC-pass；
- 36,630 B-lineage candidates；
- 13,000 B_CONV + 1,300 B_ASC reference cells；
- 258 donors；
- 601 common features；
- elastic alpha = 0.0001；
- coverage >=0.80；
- B_CONV precision >=0.90；
- B_ASC precision >=0.90；
- both required mappers must satisfy frozen eligibility.

纠错后：

- elastic coverage = 0.941958
- elastic B_CONV precision = 0.996450
- elastic B_ASC precision = 0.885210 -> FAIL
- centroid B_CONV precision ~=0.992
- centroid B_ASC precision =1.000 -> passes its own calibration
- formal result remains HOLD because selective centroid rescue is prohibited.

这是正确的 fail-closed governance。

---

## 4. 不建议“修复” C9 HOLD

不要做以下操作：

- 把 B_ASC precision threshold 从 0.90 改成 0.88；
- 因中心 outcome 主要是 B_CONV，就事后改为 B_CONV-only calibration；
- 丢弃 elastic-net，仅留下通过的 centroid；
- 扩 alpha/confidence candidate grid 直到 PASS；
- 更换 seed；
- 重新设计 feature space 以获得更高 precision；
- 使用旧 C9 positive outcomes 做 post hoc model selection。

这些都会把一个透明的技术纠错变成 outcome-informed rescue。

如果未来 reviewer 明确要求 source-label-independent external corroboration，正确做法应是：
- 新的独立数据集；
- 或一个单独、事先冻结的新 validation design；
而不是回头修改 C9R 的既定 gate。

---

## 5. 论文中央证据链重新冻结

当前最稳的证据链仍然成立：

1. GSE174188：150,402 B-lineage cells；
2. 259 donors / 271 samples / 88 libraries；
3. fine-grained hard state assignments 不足以承担稳定 disease inference；
4. frozen-representation broad B_CONV/B_ASC analysis scaffold 可用；
5. full end-to-end R1 正式 HOLD，失败是 B_ASC-specific：
   - B_ASC median Jaccard = 0.930323 < 0.95；
   - B_CONV median Jaccard = 0.999363；
   - B_CONV minimum Jaccard = 0.998760；
6. boundary propagation 后 primary B_ASC OR 仍为 null；
7. primary B_CONV IFN/ISG 仍为正；
8. donor-nonoverlap internal IFN 仍为正；
9. source-label-defined independent GSE135779 childhood IFN replication 保留；
10. genome-wide rho=0.026，拒绝 transcriptome-wide replication；
11. STAT1/STAT2 ULM + CAMERA/FRY 为 convergent observational support；
12. 12-gene depletion 后支持保留；
13. M5911 depletion 后 discovery STAT2 明显衰减，因此不支持 overlap-independent regulation；
14. GSE23307 n=2 仅 descriptive；
15. corrected C9 outcome 未估计，source-label-independent external robustness unresolved。

### 最强 conceptual contribution

> Inferential granularity must be validated rather than assumed: hard state membership has explicit reproducibility limits, whereas process-level IFN remodeling survives biological-unit inference, identity-boundary propagation and independent source-label-defined cohort validation.

这仍是论文最值得投稿一区的逻辑。

---

## 6. Manuscript 当前状态

标题建议保留：

> Disease-blind single-cell reconstruction separates unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus

当前 abstract ~342 words，主线层级基本正确，而且没有把 corrected C9 放进 abstract，建议继续保持。

### 目前做得好的地方

- “state assignments” 避免否定生物学状态本身；
- R1 HOLD 在 Abstract/Methods/Results/Discussion 中一致；
- B_CONV/B_ASC 被定义为 analysis scaffold，不是 universal taxonomy；
- independent GSE135779 是 source-label-defined broad analog；
- corrected C9 结果段明确：calibration failed -> disease outcomes not estimated；
- no causal TF / unique ligand / clinical utility overclaim；
- old DOI 被明确限定为 historical initial snapshot；
- renewed final author approval 标为 pending；
- AI-use disclosure 保留作者责任。

### P1 写作精修 1

Methods 目前写：

> Reference donor-grouped cross-validation selected regularization and confidence thresholds.

纠错后更准确的写法应是：

> Reference donor-grouped cross-validation evaluated regularization and candidate confidence thresholds under the prespecified state-specific eligibility criteria.

原因：elastic-net 没有任何 candidate 达到完整 eligibility，所以“selected confidence thresholds”容易给人已经获得合格阈值的感觉。

### P1 写作精修 2

Discussion limitations 目前已充分报告 R1、source-label reliance、adult underpower、regulator limitation，但 corrected C9 HOLD 可以再加一句：

> A post-freeze attempt to reconstruct external B-lineage selection without source labels failed its frozen B_ASC reference-calibration criterion after normalization was corrected, so no corrected disease outcome was estimated.

这样 editor/reviewer 不需要从 Results 才能发现 correction boundary。

### Abstract

不增加 C9 calibration 数字。
若后续目标期刊偏短摘要，可从 342 words 压到 320–330，但不属于当前 P0。

---

## 7. Supplementary Information

当前 supplement 的 S10 定位正确：

> corrected reference calibration and unresolved external transfer

它不是疾病-effect figure，也没有展示旧 C9 positive outcome。

Supplementary Table S9 也正确区分：

- full-library normalization；
- elastic calibration failure；
- centroid cannot replace required mapper；
- no corrected disease effects；
- old C9 outcomes excluded；
- original pseudobulk primary and unexecuted C9 estimand 不可直接比较。

这是非常重要的透明性设计。

---

## 8. Figure / Nature-style 独立质控

当前 correction review 有：

- 5 main figures
- S1–S10
- 共 15 张 publication figures

全部约 170 mm 宽。

独立 PDF text-span audit：

- 所有非 panel 文字 >=5 pt 且 <=7 pt；
- 所有 >7 pt 的文字仅为 8 pt lower-case panel labels；
- Arial / Arial Bold；
- vector PDF；
- 600-dpi PNG；
- 没有 <5 pt 的可见文字；
- 没有非 panel 的 8 pt title。

因此严格 Nature typography 现在已经真正 PASS。

Nature 官方当前生产规范的核心是：

- Arial/Helvetica；
- panel labels 8 pt bold lower-case；
- 其他 text 5–7 pt；
- 线宽约 0.25–1 pt；
- text/vector editable；
- Nature standard width 89/183 mm，max height 170 mm。

目前 170 mm 不是 Nature 自己的标准 double-column 183 mm，但在尚未冻结目标期刊时，没有必要仅为了 183 mm 再重跑全部图。选刊后再从代码按目标期刊 exact width rerender。

### S10 当前可投稿性

S10 当前已经清楚显示：

- normalization mismatch correction；
- frozen precision gate；
- frozen coverage gate；
- donor-grouped calibration folds。

无 clipping/overlap，科学含义正确。

### S10 的一个可选 P1 优化

如果追求“最强 reviewer communication”，可以用 frozen calibration table 重画 panel d：

当前：
- donor-grouped balanced accuracy folds

可替换成：
- calibration frontier / candidate tradeoff：
  coverage vs B_ASC precision（或 state-minimum precision）；
  标出 eligible region：coverage >=0.80 且 precision >=0.90。

原因：balanced accuracy 很高容易视觉上造成“模型总体很好，为何 HOLD？”的认知冲突；真正决定 HOLD 的是 state-specific calibration gate。

这只读取冻结 `07_MAPPER_CONFIDENCE_CALIBRATION.csv`，不重跑任何疾病模型。

不是 P0；现 S10 已足够用于外部方法审阅。

---

## 9. 当前 release-document governance 还剩两个值得修的点

### 9.1 Reporting_Checklist 的旧状态容易混淆

当前 checklist 顶部已经正确声明 correction HOLD。

但下方 `Earlier package record` 仍保留旧的：
- 46/46 main panel assertion；
- “both authors approved every submission component”；
- old DOI/release checks。

这虽然有 historical heading，但对于 author-facing 当前 checklist 仍有误勾选风险。

建议：
- 将旧 block 移到 `Historical_Reporting_Checklist_v1.0.0.md`；
- 当前 checklist 只保留 current review status；
- 或所有旧项目明确加 `HISTORICAL ONLY - NOT CURRENT AUTHORIZATION`。

另外当前 correction figure checker的 main checks为：
- 42 个 scientific/data checks
- 5 个 main-figure typography checks
- 共 47/47 current checks

因此 checklist 中旧 “46/46” 不应继续充当 current truth。

### 9.2 Author_Confirmation 应建立新的 current record

现文件已经用 scope clarification 正确说明：
> checked boxes 是 25 Aug 旧版确认；corrected package 需要 renewed approval。

但标题仍是 `Final author and release confirmation record`，下面大量 `[x]` 容易造成误读。

建议保留旧文件为历史记录，新增：

`Author_Confirmation_Current_Correction.md`

其中只保留身份/长期事实可继承项；所有对“当前 corrected manuscript / supplement / figures / cover / originality / exclusive submission”的批准框重新设为 `[ ]`，由作者真正确认后勾选。

这是当前最重要的 release-governance P0 之一。

---

## 10. correction review bundle 当前不能上传期刊

review bundle 自己已经正确写：

- review_only=true
- submission_authorized=false
- author_reapproval=PENDING
- target_journal=null
- matching_archive_doi=null

Portal 11 files 也全部为：

`DRAFT_NOT_FOR_UPLOAD`

所以当前状态非常清楚：

**技术审阅包已经成熟，但不是 submission package。**

不要为了“已经 WPS 60 页全通过”就跳过外部方法审阅与作者重新批准。

---

## 11. Journal target 重新评估

纠错后，source-label-independent external robustness 被撤回，因此投稿策略应比 C9 PASS 时更保守一些。

### 第一推荐：npj Systems Biology and Applications

从“论文逻辑匹配”角度，我现在认为它比 Genome Medicine 更自然。

其 scope 明确覆盖：
- computational/mathematical analysis of complex biological systems；
- disease modeling；
- single-cell systems biology；
- systems immunology。

当前还有 systems immunology 相关开放 collection，与本文“单细胞 + identity uncertainty + systems immunology + process-level reproducibility”高度吻合。

如果作者机构确认当前 JCR/CAS 分区满足你们的 Q1 要求，这是最值得优先评估的目标。

### 第二推荐：Communications Biology

这是当前证据结构下非常合理的 Nature Portfolio 目标。

官方 scope 明确接受：
- secondary data analysis；
- innovative computational methods；
并要求：
- novel insight；
- strong evidence；
- technically sound；
- 对具体 biological field 有重要性。

当前稿件的透明负面边界、完整可重复性和独立 cohort program-level validation，与其 editorial criteria 很匹配。

### Genome Medicine

仍可作为“高风险 stretch”，但我不再把它列为最优首选。

风险主要不是统计，而是：
- IFN biology 已知；
- public-data reanalysis；
- source-label-independent external robustness 未建立；
- no prospective cohort；
- no direct functional causality；
- no demonstrated clinical utility。

如果作者优先追求期刊临床/医学影响力，仍可先冲；如果优先追求“一区 + 文章逻辑匹配 + 不重构稿件”，则更推荐 npj Systems Biology and Applications / Communications Biology。

### 暂不建议

Nature Communications / Genome Biology：
当前缺少 prospective/functional/multi-omic/treatment-response 层，投入产出比低。

疾病专科（如 Journal of Autoimmunity）：
可作为后续路线，但 mechanistic reviewer 可能更强烈要求直接功能实验。

最终 JCR/CAS Q1 状态应由作者所在机构在正式投稿日确认，不在项目冻结包中写死。

---

## 12. 当前完成度重新评分

| 模块 | 完成度 |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1 identity-boundary transparency | 99% |
| Identity uncertainty propagation | 98% |
| Source-label-defined independent validation | 96% |
| Source-label-independent robustness | HOLD / unresolved |
| Regulatory robustness | 97% |
| Correction governance | 98% |
| Manuscript logic | 97% |
| Main figures scientific content | 99% |
| Strict Nature typography | 99% |
| Supplementary evidence | 98% |
| Source-data traceability | 99% |
| Reproducibility engineering | 98% |
| External independent methods review | 0% / pending |
| Renewed author approval | pending |
| Matching revised archive DOI | pending |
| Journal-specific package | pending |
| Portal readiness | BLOCKED by review/approval/release, not computation |

---

## 13. 下一阶段唯一正确目标

建议正式命名：

`EXTERNAL_METHODS_REVIEW_AND_AUTHOR_REAPPROVAL_GATE`

### P0-A：外部方法复核

交给非本分析代理的 reviewer，限定检查：

1. reference/external normalization formula；
2. full-library totals 实现；
3. calibration candidate arithmetic；
4. state-specific precision/coverage gate；
5. diagnostic fallback 是否彻底 fail-closed；
6. outcome metadata 是否确实未解锁；
7. formal run 是否固定 56 matrices / 363,083 cells；
8. donor-grouped fold 无 leakage；
9. feature/alpha tuning 非完整 nested CV 的 limitation；
10. “centroid PASS 不能 rescue elastic FAIL”治理逻辑；
11. old C9 outcome 如何被 supersede；
12. current manuscript 的 claim boundary 是否与代码一致。

不要求 reviewer 重跑 363k cells；首先做 code/output/material audit。

### P0-B：当前文件治理

1. 新建 current author confirmation；
2. 把 old approval 显式历史化；
3. 修 current Reporting Checklist 状态；
4. Methods 的 “selected thresholds” 改成 “evaluated candidates under eligibility rule”；
5. Discussion 加 1 句 corrected C9 HOLD limitation。

### P1-C：S10 可选优化

仅从冻结 calibration table 重画 panel d 为 calibration frontier。
如果外部方法 reviewer 认为当前 S10 已充分，则不必改。

### P0-D：作者重新批准

两位作者确认当前：
- manuscript；
- supplement；
- S10；
- source-data/statistical attachments；
- cover letter；
- correction disclosure；
- old DOI scope；
- AI disclosure；
- originality/exclusive submission；
- target journal。

### P0-E：选刊与 release

作者批准后：

1. 确认 target journal 和机构认可的 Q1 状态；
2. 按该期刊从 code rerender exact figure width；
3. target-specific cover/portal files；
4. final WPS/a11y；
5. exact final Git commit；
6. 新 tag（例如 v1.1.0；不移动 v1.0.0）；
7. Zenodo New Version；
8. version-specific DOI；
9. DOI 回填；
10. deterministic final package；
11. portal preflight；
12. submit。

---

## 14. STOP 规则

首投前不再：

- 新 cohort；
- 新 clustering；
- 新 mapper；
- 新 threshold；
- 新 gene set；
- 新 TF；
- C9 calibration rescue；
- R1 HOLD rescue；
- 为显著性修改模型。

只有外部方法 reviewer 发现 decision-changing implementation defect，才重新打开计算。

---

## 15. 最终导师结论

项目当前最有价值的品质已经不是“所有敏感性都 PASS”，而是：

- R1 的 B_ASC-specific HOLD 被完整保留；
- C9 的原错误 PASS 被主动撤回；
- corrected C9 fail-closed，没有读取新的 disease outcome；
- 中央 source-label-defined independent IFN replication 仍在；
- process-level effect 对内部 identity boundary propagation 仍稳定；
- regulator evidence 保持 observational/overlap-qualified；
- 文档、图件和 source data 的可追溯性已经接近发布级。

因此不要再把“完美”等同于更多阳性分析。

下一轮的完美目标是：

**让独立方法审阅者和两位作者确认：这份稿件对自己不能证明的内容也同样清楚。**

通过后，再选刊、发布匹配的新版本归档并投稿。
