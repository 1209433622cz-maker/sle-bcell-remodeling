# SLE B-cell remodeling — npj Systems Biology and Applications 最终硬化后独立全量复核

日期：2026-08-30  
目标期刊：npj Systems Biology and Applications  
本轮角色：生物信息学 / 单细胞分析博士生导师级 hostile audit + QiTeng late-stage writing gate  
GitHub 最新 `main`：`a960fa81c730cd3f6da5f81ace6a9212bc4ede1f`  
Zenodo 科学冻结 DOI：`10.5281/zenodo.22151739`

## 1. 本轮结论

项目已经从“需要进一步科研分析”正式进入“exact-file author approval + institutional receipts + portal preflight”阶段。

最新 GitHub 最终硬化状态为：

`PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`

该 PASS 是技术/发布工程 PASS，不改变两条科学 HOLD：

- R1：`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`
- C9R：`HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`
- corrected external outcome unlock：false

首投前不建议新增 cohort、mapper、TF/regulon、gene-set family、threshold/seed search 或新的 disease-effect branch。

## 2. 一个重要的版本层级发现：用户本轮上传 ZIP 已被最新 GitHub 结果 supersede

用户上传：

`20260830_final_render_semantic_hardening.zip`

独立本地检查：

- bytes：71,490,330
- SHA-256：`2F1E63D89BC3D236CE1F6DAE13A02BA356E7EB109E2459D0E87486F003130A04`
- entries：289

该 ZIP 的内部 final audit 生成时间约为 08:03 +08，内部 package：

- bytes：15,355,994
- SHA-256：`414BD522D7108D4F7102F359AD8E3AE27A10FC9FB620BC560B4A0445909BB170`

它是一次较早的 final-hardening build。

最新 GitHub `a960fa8...` 的 authoritative final audit 生成时间为 11:07 +08，当前 package：

- bytes：15,221,543
- SHA-256：`F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`
- manifest verified：20/20
- deterministic double build：PASS
- submission_authorized：false
- exact_package_author_approved：false

因此：

**后续作者签字、JCR/APC 归档和 portal upload 必须绑定最新 `F4F8C493...` package，而不能绑定本轮上传的旧 `414BD522...` package。**

上传 ZIP 本身不是坏包，只是已被后续 GitHub final hardening supersede。

## 3. 科学目的与设计终局判断

论文当前最有价值的科学问题不是“重新发现 SLE 中存在 IFN”，而是：

> 当单细胞疾病研究中的 identity、composition 和 within-compartment transcription 被分离成不同 inferential layers，并且 state identity 本身接受 disease-blind stress test 后，哪些疾病信号仍具有可重复性？

当前 frozen evidence chain：

1. GSE174188 源 B-lineage 152,981 cells，hard QC 后 150,402 cells；
2. 259 donors / 271 biological samples / 88 libraries / 4 processing cohorts；
3. fine-grained hard identity solution 未通过预设稳定性；
4. B_CONV/B_ASC 只能作为 analysis scaffold；
5. frozen-representation broad partition 稳定，但 end-to-end R1 因 B_ASC state overlap 未达 0.95 而正式 HOLD；
6. B_CONV end-to-end assignment 极稳定；
7. propagation of observed boundary exchanges 未改变 primary B_ASC composition null；
8. primary B_CONV IFN/ISG 和 donor-nonoverlap IFN/ISG 均保持正向；
9. GSE135779 childhood donor analysis 提供 **source-label-defined** 独立 program-level replication；
10. genome-wide rho=0.026，不能声称 globally shared SLE transcriptome；
11. C9R corrected source-label-independent calibration 未达 frozen B_ASC precision gate，因此无 corrected disease effect；
12. STAT1/STAT2 仅为 convergent observational regulatory support；
13. CAMERA 有明确 discovery STAT2 exception；
14. broader M5911 depletion 显著削弱 discovery STAT2，因此不支持 overlap-independent regulation；
15. GSE23307 n=2 仅 descriptive；
16. 不支持 universal taxonomy、generalized B_ASC expansion、causal regulator、unique upstream ligand 或 clinical utility。

该证据结构已经达到 public-data computational single-cell study 的合理上限。

## 4. QiTeng Academic Writing Skill 终局判断

当前 target manuscript 已经整合晚期 QiTeng writing hardening：

- title 15 words；
- abstract 140 words；
- Introduction 采用 tension-first framing；
- novelty 不再写成“IFN 本身新”，而是 inferential hierarchy；
- `interferon activity and plasmablast biology are well established yet strongly context dependent`；
- GSE135779 明确为 source-label-defined replication；
- primary B_ASC 使用 “not supported” 而非 proof-of-absence；
- Discussion 不重复 Results，而以 evidence-layer contrast 作为 interpretive delta；
- 最终 landing 明确限制 taxonomy / abundance / regulator / stimulus / clinical utility。

根据 QiTeng v0.3.21 的 late-stage salience/detail economy 原则：

**本轮不建议再进行第三次 broad prose rewrite。**

这不是“没有继续精修”，而是一个主动的 TEXT FREEZE 决策：继续改写的收益已经小于造成 wording drift、citation drift 或 author-approval drift 的风险。

投稿前只允许：
- 真实错误修正；
- 期刊要求格式调整；
- exact wording consistency repair；
- editor/reviewer-specific revision。

## 5. 当前 manuscript 结构评价

当前结构：

- Article
- 15-word title
- 140-word unstructured Abstract
- Introduction
- Results
- Discussion
- Methods
- Data availability
- Code availability
- Acknowledgements
- Author contributions
- Competing interests
- 32 Nature-style references
- Figure legends

符合 npj SBA reader-facing narrative 的总体方向。

中央 argument 可以压缩成一句：

> The contribution is not the rediscovery of interferon involvement in SLE, but the identification of an inferential level at which that involvement remains reproducible when cell-state identity itself is stress-tested.

这是当前最适合 editor 的 framing。

## 6. 分析方法是否还需要重跑

### 不需要重跑的内容

首投前不重开：

- clustering / Leiden / Harmony 参数；
- state definitions；
- beta-binomial composition；
- edgeR pseudobulk；
- HC3 program models；
- external GSE135779 primary source-label-defined analysis；
- corrected C9R；
- regulator ULM/CAMERA/FRY；
- M5911 depletion；
- GSE23307；
- seed families。

### 唯一重新计算分析的触发条件

只有新发现的 **decision-changing implementation defect** 才允许重开计算。

当前最终 GitHub hardening 没有发现这种 defect。

所以 analysis state：

**SCIENCE FREEZE。**

## 7. Figure / Nature-style 最终状态

最新 final-hardening 已修复此前 npj style branch 的 generic-clamp 回退问题。

最新 figure contract：

- 15 publication figures；
- single-page vector PDF；
- Arial；
- target visible text 8 pt；
- panel labels bold lower-case 8 pt；
- positive line width >=1 pt；
- RGB；
- white background；
- 15/15 source tables byte-identical。

final audit 还要求：

- figure exported-artifact contract PASS；
- source-data byte identity PASS；
- all figure sources individually identical；
- five main vector PDFs single-page；
- manual review of all 15 contact sheets / high-risk panels；
- no clipping / overlap / missing labels。

### Figure 5

最新 Figure 5 已在上传旧 ZIP 之后再次重排；当前 metadata 为约：

- width 170 mm
- height 211 mm
- font 7–8 pt
- minimum line 1 pt

该高度超过旧的通用 Nature 170-mm-height经验值，但并不自动构成 npj initial-submission blocker。npj 初稿允许较灵活的格式，且 211 mm 可以在 A4/Letter 页面中放置。

最终 portal preflight 应特别目视检查：
- portal 是否自动缩放 Figure 5；
- 缩放后 panel d/e 文字是否仍清晰；
- 轴标签是否有拥挤；
- legend 与 figure 是否易于联读。

不建议仅为了旧的 170-mm Nature 通用高度再次压缩 Figure 5，因为压缩反而可能降低阅读性。

### Supplementary Figure S8

同理属于高信息密度 figure；当前 postflight PASS。只需在 portal-generated PDF 中确认实际缩放。

## 8. Machine-readable statistics map

此前发现的语义反向已在最新 GitHub 中修复：

- R1：明确写 criterion not met；
- C3_PRIMARY：明确写 primary B_ASC difference not supported；
- C5_GENOMEWIDE：明确写 genome-wide concordance weak；
- C9R：明确写 did not qualify for outcome estimation；
- TF_DEPLETION：明确写 broader M5911 overlap-independence not supported。

因此 statistics map 现在可以继续作为 reporting integrity layer。

## 9. 本轮新增发现：README 仍有一个 reader-facing 逻辑错误

最新 README 的 frozen evidence chain 中仍有一句：

> “End-to-end resampling formally holds because B_ASC median Jaccard is 0.930, below the unchanged 0.95 criterion.”

这句话在逻辑上自相矛盾。

0.930 < 0.95 正是 R1 正式 HOLD 的原因。

建议在 author exact-file approval 前修为：

> **“End-to-end resampling formally remains on HOLD because B_ASC median Jaccard is 0.930, below the unchanged 0.95 criterion.”**

或更自然：

> **“End-to-end resampling did not meet the frozen state-overlap criterion because B_ASC median Jaccard was 0.930, below 0.95.”**

这是当前唯一新发现的明确 reader-facing repository wording bug。

不涉及 scientific results，也不需要改 Zenodo v1.1.0。

## 10. Zenodo / release

继续以：

`10.5281/zenodo.22151739`

作为 frozen scientific reproducibility DOI。

不需要因为 target manuscript 的格式和图形重渲染立即更新该 DOI。

只有在作者希望将 **exact submitted npj version** 也作为新的 immutable archive version 保存时，才创建后续 Zenodo New Version。

当前最重要的是保持：

- v1.1.0 scientific release immutable；
- target submission package independently governed；
- scientific source-data hashes不变。

## 11. npj Systems Biology and Applications 匹配度

官方 scope 明确包括：

- computational/mathematical analysis of complex biological systems；
- disease modeling；
- single-cell systems biology；
- systems immunology。

所以当前稿件与目标刊高度匹配。

官方 2025 journal metrics：

- JIF 4.4；
- 5-year JIF 4.2；
- median first editorial decision 8 days；
- median submission-to-acceptance 155 days。

APC 当前：

- GBP 2,690；
- USD 3,490；
- EUR 2,990；
- taxes may apply。

这些公开信息不能替代作者要求的正式 **JCR Q1 receipt**。

## 12. JCR / APC 两个非科学硬门

在用户要求“SCI一区 / JCR Q1”为硬条件的前提下，提交前必须保存机构或 Clarivate JCR profile：

- metric year；
- category/categories；
- rank；
- denominator；
- quartile。

同样：

The Chinese University of Hong Kong 的公开 Springer Nature OA agreement 不能自动推定 The Chinese University of Hong Kong, Shenzhen 一定符合 APC coverage。

需要 CUHK-Shenzhen library / OA office 的明确确认。

## 13. 官方 Nature Portfolio forms

当前 repository 中 Reporting Summary / Editorial Policy Checklist 是准备/草稿层。

正式 portal preflight 前需要：
- 使用当期官方 Reporting Summary；
- 使用当期 Editorial Policy Checklist；
- 两位作者复核；
- 不为 sex/gender 等表单字段临时开 post-hoc exploratory analysis；
- 对不可统一分析的元数据限制如实说明。

## 14. 当前 readiness

| 模块 | Readiness |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1/C9R boundary discipline | 99% |
| QiTeng manuscript logic | 99% |
| Main manuscript target structure | 99% |
| Supplement structure | 99% |
| Source-data integrity | 100% |
| Statistics-map semantics | 100% |
| Figure code/render contract | 99% |
| Package deterministic integrity | 100% |
| Repository current-state wording | 97%（README 一处 typo） |
| Official forms | pending |
| Official JCR Q1 receipt | pending |
| APC/OA institutional receipt | pending |
| Exact-file author approval | pending |
| Submission authorization | pending |
| Overall first-submission readiness | ~97% |

## 15. 下一阶段

正式下一阶段：

`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

但执行前做一个 5 分钟级 repository patch：

1. 修 README `formally holds` -> `formally remains on HOLD` / `did not meet criterion`；
2. rerun lightweight documentation regression；
3. 不改变 manuscript、figures、statistics、Zenodo；
4. 确认 final package 仍为最新 `F4F8C493...` 或在 documentation-only rebuild 后记录新 hash。

然后进入：

1. 取用最新 GitHub/local build，而不是本轮上传的 superseded ZIP；
2. 对最新 Figure 5 做一次 human visual sign-off；
3. 两位作者批准 exact Manuscript/Supplement/Figures/Cover/package hashes；
4. 归档官方 JCR Q1 receipt；
5. 归档 CUHK-Shenzhen APC/OA receipt；
6. 完成官方 Reporting Summary；
7. 完成官方 Editorial Policy Checklist；
8. 明确 submission authorization / APC commitment；
9. portal upload；
10. 检查 portal-generated PDF；
11. 保存 manuscript number、receipt、timestamp、实际 uploaded-file hashes。

## 16. STOP rule

从现在到首投，不再新增科学探索。

只有：
- decision-changing implementation defect；
- editor/reviewer明确提出；
才允许重新打开生信计算。

## 17. 最终导师判断

当前稿件已经不存在“需要再加一层分析才够 npj SBA”的问题。

最重要的是保持这篇论文现在已经建立起来的可信度结构：

- failed gates 没有被调参救回；
- null result 没有被写成 proof of absence；
- external replication 的 source-label ownership 清楚；
- regulatory evidence 保持 observational；
- process-level IFN signal 与 taxonomy-level uncertainty 被明确分层。

继续大改正文或继续新增分析，反而会破坏这套结构。

下一轮应该是 **author/institutional closure + portal preflight**，而不是新的 scientific gate。
