# SLE B-cell Remodeling 项目对话全量总结与工作记录

**整理日期：2026-09-08**
**项目仓库：** `https://github.com/1209433622cz-maker/sle-bcell-remodeling`
**当前写作导向：** `npj Systems Biology and Applications`
**工作主线：** 手稿文本、主图/补图科学信息架构、来源驱动重绘、证据边界与可重复性
**明确不作为当前优先级：** 投稿门户、submission package、Release、Zenodo 推进
**基本原则：** 优先从冻结 Source Data 和正式 builder 重跑分析/重绘图，而不是手工修改已有 PNG/PDF；任何新主图只能在 evidence ownership、数值来源、实际刊宽可读性和跨文档同步均通过后进入 canonical baseline。

---

# 一、整个对话的核心目标

本轮对话围绕 SLE B-cell remodeling 手稿继续进行“科学呈现层面的最后强化”，而不是以尽快投稿为目标。用户反复明确：继续专注手稿文本与图片精修/重绘；尤其讨论既有子图的保留、修改或替换；尽可能追求逻辑闭环和 Nature/npj 风格的信息密度；优先从冻结来源数据和正式绘图脚本重跑，而不是修改旧结果文件；每轮完成后重新判断下一阶段目标。

后续优化的核心问题因此从“是否还有明显错误”升级为：

> **主文中最重要的科学结论与最关键的失败边界，是否都进入了读者第一视野？**

也就是说，后续不再追求增加结果数量，而是追求 claim 与 evidence owner 一一对应、正面结果与限制边界同时可见、主图与 Supplementary 分工清楚、负结果不被“救活”、机制语言不超过实际证据上限。

---

# 二、当前论文的核心科学定位

当前手稿题目为：

> **Disease-blind reconstruction distinguishes reproducible interferon remodeling from less stable B-cell state assignments in systemic lupus erythematosus**

标题已把论文核心从“寻找新的 SLE B-cell subtype”转移为比较不同生物学/推断层级的可重复性上限。当前 novelty 已稳定为：

> **reproducibility ceilings differ across inferential/biological layers**

具体而言：hard/fine B-cell state assignment 稳定性有限；broad B_CONV/B_ASC 只能作为 analysis scaffold；primary B_ASC composition 缺乏统计支持；B_CONV IFN/ISG transcriptional process 能在 discovery、internal robustness 和 source-label-defined external replication 中复现；但 source-label-independent transfer calibration 失败；STAT1/STAT2 只获得 observational convergence，不能升级为因果调控；broader IFN-response depletion 进一步定义 regulatory ceiling。

全文核心逻辑链：

```text
identity uncertainty
→ bounded B_CONV/B_ASC scaffold
→ primary B_ASC composition unsupported
→ reproducible B_CONV IFN/ISG process
→ source-label-defined independent replication
→ source-label-independent transfer calibration failure
→ convergent but observational regulator/response evidence
→ explicit causal/transfer limits
```

---

# 三、GSE174188 discovery 与身份重建

源 B-lineage matrix：152,981 cells、30,172 genes。hard QC 后保留 150,402 cells，代表 259 donors、271 biological samples、88 technical libraries、4 processing cohorts。

身份策略的重要结论：初始 five-state solution 未通过预设稳定性标准，失败被保留为负结果，没有重新命名后包装成成功 subtype；transition reconstruction 支持 broad B_CONV/B_ASC 两分区；naive-memory 被降为 B_CONV 内连续 program；platelet-associated signal 保留为 technical overlay。

---

# 四、Fixed representation 与 end-to-end reconstruction

在 frozen 50-dimensional Harmony representation 中，两分区通过预设标准：minimum mapped ARI 约 0.990，minimum mapping agreement 约 0.9998，minimum state-median Jaccard 约 0.991，B_ASC marker support 5/5。

但 end-to-end reconstruction 重新过滤基因、选择 HVG、重算 PCA、Harmony、neighbor graph 与 Leiden 后，20/20 replicates 完成且 20/20 Harmony 收敛。总体 median/minimum mapped ARI 约 0.963/0.930，median/minimum mapping agreement 约 0.99937/0.99877。state-specific：B_CONV median/minimum Jaccard 约 0.99936/0.99876；B_ASC median/minimum Jaccard 约 0.930/0.872。预设 state-median criterion 为 0.95，因此 B_ASC end-to-end reproducibility requirement 未通过。

这使 B_CONV/B_ASC 的定位被严格限制为：

> **disease-blind analysis scaffold**

而不是 transferable universal taxonomy。

Identity uncertainty propagation 将实际观察到的 boundary exchanges 回填后：primary composition OR 约 0.896–0.967，所有 CI 均包含 1；primary B_CONV IFN/ISG effect 约 0.836–0.845；donor-nonoverlap IFN/ISG 约 1.059–1.087；40 个 IFN 估计均保持正向且 CI > 0。因此 identity uncertainty 未推翻 downstream disease conclusions，但阻止了更强的 taxonomy-level interpretation。

---

# 五、Primary B_ASC composition

Primary comparison 使用 sample-cohort stratum 作为实验单位，不进行 cell-level disease test。主结果：OR 0.9467，95% CI 0.6357–1.4097，P 约 0.7873，q 约 0.7873；adjusted fractions 约为 control 1.61%、managed SLE 1.52%。

解释边界：不能说“B_ASC 没有变化”，不能说“等效”，不能用 secondary flare 取代 primary result。secondary flare OR 约 2.303，nominal P 约 0.0282，但 q 约 0.0845，因此只能作为 contextual heterogeneity。

---

# 六、B_CONV IFN/ISG transcription

Primary B_CONV pseudobulk：89 strata，43 control，46 managed SLE，约 59.87 million UMI counts。Primary IFN/ISG effect 约 0.837，95% CI 0.525–1.148，q 约 2.98×10^-6。Internal replication effect 约 0.856，q 约 0.00462；donor-nonoverlap internal replication effect 约 1.086，q 约 3.61×10^-4。

IFN/ISG 在 20-cell、100-cell、residual-doublet-risk-negative、89 leave-one-sample-out、internal replication 和 donor-nonoverlap 中保持正向，因此被稳定为四个 prespecified B_CONV programs 中唯一完成完整支持链的 program。

其他 programs：naive-to-memory primary lower，但 internal replication 未达到同等级支持；APC/HLA primary higher，但 internal replication 未充分重复；atypical/low-naive primary null。因此这些只能作为 secondary context。

---

# 七、GSE135779 独立外部重复

外部分析没有强行转移 fine state，而是使用 source-label-defined broad conventional-B analogue。Childhood analysis：43 donors（11 controls、32 SLE），effect 约 1.042，95% CI 0.681–1.402，q 约 2.98×10^-6。Combined：54 donors（16 controls、38 SLE），effect 约 0.996，95% CI 0.655–1.337，q 约 1.31×10^-6。Adult-only 只有 5 controls、6 SLE，effect 约 0.968，CI 跨 0，q 约 0.291，因此只能称 directional compatible。

两个 primary dataset 共有 4,410 jointly tested genes，genome-wide Spearman rho 约 0.026，但共同 tested 的 10 个 IFN genes 10/10 同方向 positive。因此论文明确区分 prespecified process-level replication 与 global transcriptome-wide concordance。

---

# 八、source-label-independent transfer 的关键失败

Corrected source-label-independent mapping 处理 56 个 GSE135779 matrices（363,083 cells），QC 后 353,527 cells，并在不使用 source labels 或 disease fields 的情况下选择 36,630 B-lineage candidates。required mapper 为 elastic-net；diagnostic threshold 0.95；预设 eligibility 为 coverage ≥0.80、B_CONV precision ≥0.90、B_ASC precision ≥0.90。

实际结果：coverage 0.941958（PASS）；B_CONV precision 0.996450（PASS）；B_ASC precision 0.885210（FAIL）。因此不估计 corrected source-label-independent external disease effect。

nearest-centroid mapper 虽达到 diagnostic criteria，但因为结果已经查看，不能在 outcome exposure 后替代 required elastic-net mapper。这个失败不否定 source-label-defined IFN replication，但阻止 de novo taxonomy transfer、source-label-independent replication 和 corrected external disease-effect claim。

---

# 九、STAT1/STAT2 regulatory evidence

IFN-centred regulators：STAT1、STAT2、IRF7、IRF9；proliferation comparators：E2F1、FOXM1、MYC、MYBL2；confirmatory contrasts：GSE174188 primary、GSE174188 donor-nonoverlap、GSE135779 childhood；global family 为 24 tests。

STAT1/STAT2 在三个 contrasts 中均为 positive，ULM family 提供 observational convergence，proliferation comparators 不形成一致正向模式，leave-one-target 与 80% target resampling 支持结果不是单一 target 驱动。但结论被严格限制为 observational regulatory context，不能称 causal TF regulation。

CAMERA/FRY sensitivity：6 个 STAT1/STAT2 core tests 方向均正；CAMERA 5/6 multiplicity-supported；discovery STAT2 是明确例外，CAMERA q 约 0.1355；FRY 对 discovery STAT2 仍 positive/significant。因此用语稳定为 “cross-contrast concordance with a defined CAMERA limitation”，而不是 universal significance across methods。

---

# 十、IFN-overlap depletion 与 regulatory ceiling

Branch A：删除 12 个 frozen IFN/ISG positive-arm genes 后，6/6 ULM estimates 仍 positive，6/6 95% CI >0，6-test q<0.05；CAMERA 6/6 positive、5/6 significant；FRY 6/6 positive/significant；至少 78.6% matched targets 保留，minimum ULM slope retains 约 53.5% baseline。说明 STAT1/STAT2 不是简单由 12 个 program genes 重述。

Branch B：删除 broader M5911 response set 后 attenuation 更明显：18 method-level directions 仍 positive；ULM 5/6 significant；CAMERA 2/6；FRY 5/6；discovery STAT2 只剩 8/14 targets，ULM slope 0.391，95% CI -0.745–1.526，q 0.500，CAMERA q 0.623，FRY q 0.099。

最终解释：regulatory evidence 不是 12-gene program 的简单重复，但仍部分嵌入 broader interferon-response transcriptome。这被定义为 regulatory ceiling，而不是机制性失败。

---

# 十一、M5911 与 GSE23307

M5911 Hallmark interferon-alpha response 在三个 contrasts 中 NES 约 3.187、3.050、3.527，每个 contrast 使用 10,000 gene-label permutations。定位为 response-set concordance，不是 causal regulator proof。

GSE23307 为 2 healthy donors 的 IFN-beta perturbation。12-gene IFN positive arm 在两 donor 中均 12/12 positive，24/24 donor-gene effects positive，donor mean paired log2(x+1) effects 约 3.294 与 3.666。因为 n=2，不计算 inferential P，gene 不能作为 biological replicate，只能称 descriptive perturbational context。

---

# 十二、Figure 1 boundary promotion

早期 hostile audit 发现标题、Abstract、Results 都把 “fixed representation pass，但 end-to-end B_ASC fails” 作为全文第一科学转折，但旧 Figure 1 的量化 panels 都停留在 frozen representation，真正 end-to-end B_ASC failure 只在 Supplementary Fig. S4。

因此裁决为：接受信息架构问题，但拒绝直接采用候选 PNG，只允许从哈希锁定 Source Data 正式重绘。

最终 panel 决策：Figure 1a KEEP；1b KEEP；旧 1d 重排为新 1c；旧 1c 退出主图但 Source Data 保留；新 1d 从 Supplementary S4 frozen source 重算 end-to-end Jaccard summary。

新 Figure 1 逻辑：

```text
workflow
→ policy selection
→ fixed-representation criterion met
→ end-to-end B_ASC criterion not met
```

Supplementary Figure S4 继续作为完整 audit owner，保留 20 replicate-level diagnostics、boundary exchange、composition propagation 与 IFN propagation。

Frozen representation Jaccard：B_CONV min/median 0.999832/0.999925；B_ASC 0.981096/0.991371。End-to-end：B_CONV 0.998760/0.999363；B_ASC 0.871750/0.930323；criterion 0.95。

最终状态：`SCIENTIFIC_FIGURE1_BOUNDARY_PROMOTION_REFREEZE`。QA：WPS 31 pages、LibreOffice 31 pages、62 rendered pages、12 contact sheets、无 clipping/overlap/blank page/tail page，accessibility 0/0/0，regression 187/187 PASS。对应 working commit 曾确认为 `d317c4619cfc84134934910cfea87b65ee41e059`，message `Promote end-to-end identity boundary in Figure 1`。

---

# 十三、FULL_MAIN_FIGURE_CLAIM_DENSITY_HOSTILE_READ

Figure 1 重冻结后，下一阶段转为 `FULL_MAIN_FIGURE_CLAIM_DENSITY_HOSTILE_READ`，专门检查 Figure 2–5 是否仍存在“正文一级结论或关键限制只在 Supplementary，而主图 slot 被低信息量或重复 panel 占据”的问题。

## Figure 2

2a、2b、2c、2d 全部 KEEP。四个 panel 分别拥有 observed distribution + adjusted estimate、primary/internal/nonoverlap/flare contrast hierarchy、minimum-cell/explicit non-B/residual-doublet sensitivity、90 leave-one-sample-out influence。无明显重复。

## Figure 3

3a、3b、3c、3d 全部 KEEP。分别拥有 four-program discovery family、IFN robustness ladder、gene-level positive-arm coherence、specificity/technical controls。无主图信息架构缺口。

---

# 十四、Figure 4 hostile read 与最终实施

Hostile read 发现 Figure 4 存在真正类似 Figure 1 的问题。旧 Figure 4d 展示 donor/source-label influence，但完整 influence diagnostics 已由 Supplementary Figure S7 拥有；与此同时更重要的 corrected source-label-independent elastic-net calibration failure 只在 Supplementary S8 可视化，尽管它已经进入 Abstract、Results 独立 subsection、Discussion 和 limitations。

因此 Figure 4d 被判定为真正值得替换的主图 slot。

用户后续上传的正式结果说明这一建议已经通过真实项目链完成 source rerender，而不是停留在候选 PNG。

最终状态：`SCIENTIFIC_FIGURE4_TRANSFER_BOUNDARY_PROMOTION_REFREEZE`，完成日期 2026-09-07。

最终 panel ownership：4a KEEP，拥有 GSE135779 source-label-defined IFN/ISG effect 与 support thresholds；4b KEEP，拥有 discovery/internal 与 source-label-defined external direct comparison；4c KEEP，独占 4,410 shared genes、rho=0.026 和 10/10 IFN concordance；4d 被 SOURCE REPLACEMENT 为 required corrected elastic-net calibration。

新 4d 显示：coverage 0.942 ≥0.80，B_CONV precision 0.996 ≥0.90，B_ASC precision 0.885 <0.90，并明确 “B_ASC criterion not met / no corrected effect estimated”。旧 4d 的 influence role 转交给 S7。

冻结来源哈希：Figure 4 Source Data `F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755`；S7 `A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6`；S8 `FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF`。

最终 Figure 4 尺寸 170.0 mm × 137.87 mm。PDF SHA-256 `B1120AA60E9B03FBE835E9979F0449F67B483B792C9339737CB0CD40C5A2B75F`；PNG SHA-256 `6FBF35DE2D5D425E11B46B029D2239AF61084A4685DBA672C19CC59F8C6F9BD7`。WPS 31 pages，SHA-256 `0DB51A93BE06F84DD09D47648BA8C6553C336FECA6B73913BC0D5475D074CE51`；LibreOffice 31 pages，SHA-256 `F4324AD59C9A3E4D8A8BE0B00CA1D7523006A56359A2FF2AA38A4E7B9CD49114`。62 rendered pages、12 contact sheets 均检查，无 blank page/clipping/overlap/missing glyph/abnormal pagination/cross-render tail page，accessibility 0/0/0，regression 194/194 PASS。45 个 figure/source-data assets 中仅 Figure 4 PDF、PNG、Source Data 变化，其余 42 项 hash unchanged。

Figure 4 手稿同步只允许四类 narrow edits：donor/source-label influence ownership 转给 S7；gene-level coherence citation 收窄到 Fig. 4c；corrected calibration failure 锚定到 Fig. 4d；Figure 4 legend 同步重写。Title、Abstract、Discussion、Conclusion、Figure 5、Supplementary Information、references、other legends、effect sizes、thresholds、mapper policy、cohort definitions 均不改变。

---

# 十五、Figure 5 hostile read：当前唯一尚未完全冻结的主图问题

当前 Figure 5：5a evidence-class summary；5b IFN-centred regulator ULM；5c proliferation comparators；5d M5911 NES；5e two-donor IFN-beta paired effects。

5a KEEP：全文重要 causal-ceiling owner，把 ULM STAT1/STAT2、M5911、GSE23307 区分为不同 evidence classes，不能换成 causal network。5b KEEP：STAT1/STAT2 + IRF7/IRF9 三 contrasts 的 quantitative owner。5c KEEP：proliferation specificity，防止 IFN regulator pattern 被误解为 generic proliferation activation。5e KEEP：two-donor IFN-beta perturbational context。

唯一仍处于 active gate 的是 5d。Current 5d 只显示 M5911 NES 3.187/3.050/3.527，数值量较少，正文已明确给出，5a 已声明 M5911 是 response-set concordance，Supplementary Table S3 也有 quantitative anchor，因此被认为是 Figure 5 中信息增量最低的 panel。

候选 new 5d 方向：用 S10 冻结数据重绘 12-gene depletion 与 M5911 depletion 下 STAT1/STAT2 的 ULM slope + 95% CI，突出 discovery STAT2 在 broader M5911 depletion 后 CI crossing zero：slope 0.391，95% CI -0.745 to 1.526，q 0.500。目的不是证明机制更强，而是把 regulatory evidence 的 ceiling 放入 main reader path。

---

# 十六、Figure 5 正式 gate

下一阶段已确定为：

`FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE`

不是直接采用 candidate。必须从正式项目 builder 重绘，使用锁定 S10 Source Data，在 170 mm 完整 Figure 5 中真实组合，比较 current M5911 5d 与 candidate depletion 5d 的信息增益、clutter、CI readability、legend cost 和 evidence ownership；保证 discovery STAT2 CI-crossing-zero 清晰可见；不遮蔽 5a–c/e；不改变 regulator family、multiplicity family、target set 或 causal wording。

如果 candidate 只是更复杂但不更清晰，则 KEEP current 5d；如果真实组合中明显更强，才 SOURCE-REPLACE current 5d。

---

# 十七、Supplementary Figure ownership

S4：完整 owner 为 end-to-end reconstruction、20 replicate diagnostics、boundary exchange、composition propagation、IFN propagation；main Figure 1d 只提升 summary boundary。

S5：composition diagnostics、zero-ASC motivation、covariance variants、two-part model 等完整 owner。

S6：pseudobulk ranked-list diagnostics、filterByExpr、dispersion、technical-family checks。

S7：GSE135779 donor deletion、source-label omission、external robustness；Figure 4d 不再承担这些职责。

S8：corrected remapping、legacy normalization mismatch、both mappers、candidate calibration、donor-grouped folds、coverage/precision diagnostics；main Figure 4d 只保留 required elastic-net decision gate。

S9：correlation-aware CAMERA/FRY sensitivity、discovery STAT2 CAMERA exception、target-count verification。

S10：12-gene/M5911 overlap-depletion、ULM/CAMERA/FRY、target retention、leave-one-target、method-specific multiplicity。即使新 Figure 5d 最终采用，S10 仍保留完整 detailed ownership。

---

# 十八、当前 Figure 1–5 状态矩阵

| Figure | Panel | 当前决策 |
|---|---|---|
| Fig. 1 | a | KEEP |
| Fig. 1 | b | KEEP |
| Fig. 1 | c | KEEP / relocated fixed-representation Jaccard |
| Fig. 1 | d | SOURCE-REPLACED with end-to-end B_ASC boundary |
| Fig. 2 | a | KEEP |
| Fig. 2 | b | KEEP |
| Fig. 2 | c | KEEP |
| Fig. 2 | d | KEEP |
| Fig. 3 | a | KEEP |
| Fig. 3 | b | KEEP |
| Fig. 3 | c | KEEP |
| Fig. 3 | d | KEEP |
| Fig. 4 | a | KEEP |
| Fig. 4 | b | KEEP |
| Fig. 4 | c | KEEP |
| Fig. 4 | d | SOURCE-REPLACED with elastic-net calibration failure |
| Fig. 5 | a | KEEP |
| Fig. 5 | b | KEEP |
| Fig. 5 | c | KEEP |
| Fig. 5 | d | UNDER ACTIVE GATE |
| Fig. 5 | e | KEEP |

当前 21 个 main panels 中，20 个已经 KEEP/accepted source replacement，唯一仍在主动 gate 的是 Figure 5d。

---

# 十九、当前理想主图总逻辑

如果 Figure 5d regulatory-ceiling promotion 通过，则五个主图会形成：

- Figure 1：identity scaffold + reconstruction ceiling
- Figure 2：composition boundary
- Figure 3：discovery IFN program + internal robustness + specificity
- Figure 4：independent source-label-defined replication + gene-level coherence + transfer calibration ceiling
- Figure 5：regulatory convergence + specificity + broader-IFN depletion ceiling + orthogonal perturbational context

总逻辑：

```text
reconstruction boundary
→ composition boundary
→ reproducible IFN program
→ independent replication
→ transfer boundary
→ regulatory convergence
→ regulatory ceiling
→ no causal overclaim
```

---

# 二十、当前手稿写作原则

目前不建议大规模重写正文。主要问题已从“文字不够准确”转成“图件是否把正文已经准确写出的关键边界放到第一视野”。

明确避免：universal B-cell taxonomy、stable disease-defining subtype、source-label-independent replication、causal STAT1/STAT2 regulation、unique interferon ligand、direct TF binding、predictive biomarker、clinical utility、B_ASC unchanged、equivalent abundance。

允许且推荐：analysis scaffold、process-level IFN/ISG replication、source-label-defined independent replication、observational regulatory convergence、regulatory context、defined calibration failure、explicit stability limit、transfer limit、prospective translational implication。

---

# 二十一、实验单位与方法边界

Composition 的 experimental unit 为 sample-cohort stratum，并对 repeated samples 做 donor-aware sensitivity，不是 cell-level inference。Pseudobulk raw counts 也按 sample-cohort stratum within B_CONV 汇总，technical-library contributions 只在 cell-ID/count conservation 后合并。因此 Figure 1 workflow、Figure 2/3 legend 或正文都必须避免把常规主分析写成 “donor pseudobulk”。

---

# 二十二、Multiplicity architecture

当前 multiplicity 不应再重开：primary B_ASC composition 为 3 prespecified base contrasts BH；gene-level edgeR 在每 contrast tested genes 内 BH；B_CONV frozen programs 为 4-program BH family；regulator ULM 为 24-test global BH family；CAMERA/FRY core sensitivity 为 method-specific 6-test families；overlap-depletion 为 branch × method 的 separate 6-test post-freeze families；M5911 为 descriptive three-contrast correction；GSE23307 n=2 无 inferential P。

不允许因为 Figure 5 重绘而重新定义 multiplicity family。

---

# 二十三、可重复性与 provenance 原则

项目已建立 timestamped run directories、immutable source objects、deterministic seeds、SHA-256 manifests、machine-readable decisions、superseded figures/manuscripts retained 等 provenance。新图只能由当前 frozen source data + builder 生成。

明确禁止：在 Illustrator/PPT 手动改数、Photoshop 修 panel、把 candidate PNG 直接当 canonical、因为另一个 mapper 看起来更好就 post hoc 换 mapper、为追求全 PASS 删除失败 gate。

---

# 二十四、投稿相关状态：仅记录，不作为当前任务

历史冻结 submission package SHA-256：

`02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

在 Figure 1 与 Figure 4 科学重绘过程中均保持不变。Figure 4 action record 明确 Release 未触碰、Zenodo 未触碰、submission package 未触碰。因此当前属于 scientific manuscript/figure refinement branch，不是 submission engineering。

---

# 二十五、QA 里程碑

Figure 1 refreeze：187/187 regression PASS；WPS 31 pages；LibreOffice 31 pages；accessibility 0/0/0。

Figure 4 refreeze：194/194 regression PASS；WPS 31 pages；LibreOffice 31 pages；62 rendered pages、12 contact sheets；accessibility 0/0/0；42/45 assets unchanged。

这些结果说明 main-panel promotion 没有产生跨文档污染。

---

# 二十六、当前真正剩余工作

现在不再需要新增 cohort、新加机制网络、新加 pathway panel、重开 Figure 1/2/3/4、重写 Abstract/Introduction/Discussion、再“救” B_ASC composition、再“救” source-label-independent mapper。

当前唯一值得继续的 main-figure scientific task：

> **Figure 5d regulatory ceiling promotion gate**

---

# 二十七、下一阶段执行路径

## Stage 1

`FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE`

正式动作：锁定 Figure 5 Source Data 与 S10 Source Data；通过正式 builder 生成 current M5911 5d baseline 与 depletion candidate 5d；重新组合完整 170 mm Figure 5；actual-size visual inspection；比较 claim gain、clutter、CI readability、legend cost、evidence ownership；如 candidate 胜出，只重写 panel d legend、在 overlap-depletion Results 加 Fig. 5d、M5911 paragraph 不再依赖旧 5d、S10 保持 full owner；双引擎 render；full regression；hash inventory。

## Stage 2

若 Figure 5 gate PASS，进入 `SCIENTIFIC_MAIN_FIGURE_FINAL_FREEZE`，冻结 Figure 1–5、main figure legends、claim-owner matrix 与 cross-reference map。

## Stage 3

随后进入 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`，仅接受明确数字错误、cross-reference 错误、clipping/overlap、evidence-owner mismatch、actual-size readability defect；不再接受“感觉可以更漂亮”“再加一组分析”“把负结果救成正结果”“再搬 Supplementary 到 main”。

---

# 二十八、当前论文成熟度判断

整个对话显示项目已从分析设计修复进入证据层级和图文 ownership 的最终精修阶段。当前最强的科学优势不是某个极大 effect size，而是主动保留 fine-state failure、end-to-end B_ASC Jaccard failure、primary B_ASC unsupported composition、genome-wide rho≈0.026、corrected source-label-independent mapper failure、CAMERA discovery STAT2 exception、M5911 depletion attenuation、GSE23307 n=2 descriptive boundary。这些负边界共同使正结论 “reproducible B_CONV IFN/ISG process-level remodeling” 更可信。

一句话主旨：

> **This study does not claim a new universal SLE B-cell taxonomy; it shows that a prespecified interferon transcriptional process is more reproducible across datasets than the hard B-cell state assignments used to contextualize it, while explicitly preserving identity, transfer and mechanistic limits.**

中文概括：

> **这篇论文的贡献不是提出一个新的 SLE B 细胞分类体系，而是证明：在显式保留身份重建、外部转移和机制证据边界的前提下，B_CONV 中的 IFN/ISG 过程级信号比硬性 B 细胞状态标签更可重复。**

---

# 二十九、截至 2026-09-08 的当前终局状态

```text
Figure 1: refrozen
Figure 2: frozen
Figure 3: frozen
Figure 4: refrozen with transfer-calibration boundary promoted
Figure 5: only panel d remains under isolated gate
Supplementary S1–S10: retained
Main manuscript logic: stable
Methods/inference units: stable
Multiplicity architecture: stable
Submission package: untouched
Release/Zenodo: untouched
```

当前最新正式科学状态：

> `SCIENTIFIC_FIGURE4_TRANSFER_BOUNDARY_PROMOTION_REFREEZE`

下一阶段：

> `FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE`

若 Figure 5d gate 通过，应进入：

> `SCIENTIFIC_MAIN_FIGURE_FINAL_FREEZE`

随后转为：

> `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`

---

# 三十、当前重要文件与产物索引

最新 Figure 4 正式产物：`Figure4_independent_ifn_replication.pdf`、`Manuscript_Figure4_transfer_boundary.docx`、`Manuscript_Figure4_transfer_boundary.pdf`、`action_record_2026-09-07_figure4_transfer_boundary_source_rerender.md`、`npj_sba_figure4_transfer_boundary.zip`。

前一阶段 hostile-read 产物：`action_record_2026-09-02_full_main_figure_claim_density_hostile_read.md`、`FULL_MAIN_FIGURE_CLAIM_DENSITY_PANEL_MATRIX.csv`、`PROPOSED_TEXT_SYNC_LEDGER.csv`、`FIGURE4_EXTERNAL_TRANSFER_BOUNDARY_PROMOTION_SOURCE_RERENDER_GATE.md`、`SOURCE_HASH_PROVENANCE.txt`。

Figure 5 candidate 讨论产物：`Figure5d_overlap_depletion_boundary_candidate_v2.png`、`Figure5d_overlap_depletion_boundary_candidate_v2.pdf`、`Figure5d_candidate_depletion_values.csv`。这些 candidate 只作为设计假设，必须经正式 project builder 后才能进入 canonical。

---

# 三十一、后续工作约束清单

1. Figure 1 不主动重开。
2. Figure 2 不主动重开。
3. Figure 3 不主动重开。
4. Figure 4 已正式 refreeze，不主动重开。
5. Figure 5 仅允许重开 panel d。
6. S7/S8/S9/S10 继续作为完整 detailed evidence owner。
7. 不增加新的 disease-effect estimate。
8. 不改变任何阈值。
9. 不替换 required mapper。
10. 不改变 multiplicity family。
11. 不把 GSE23307 作为独立 inferential evidence。
12. 不把 CollecTRI 写成 causal regulation。
13. 不把 M5911 写成 ligand-specific evidence。
14. 不把 B_CONV/B_ASC 写成 universal taxonomy。
15. 不把 primary B_ASC null 写成 equivalence。
16. 不让 secondary flare 取代 primary composition。
17. 不把 GSE174188 internal replication 写成 independent replication。
18. external independent replication 仍是 source-label-defined。
19. 所有图件修改优先 source rerender。
20. candidate PNG 不能直接进入最终稿。

---

# 三十二、最终总结

本对话已经形成非常明确的论文终局科学呈现路线：先通过 Figure 1 把 identity stability pass 与 end-to-end B_ASC failure 同时放入主图；再对 Figure 2–5 做 hostile claim-density audit，确认 Figure 2/3 已足够成熟，不应继续扰动；随后发现 Figure 4 主图遗漏了决定外部证据等级的 corrected elastic-net calibration failure，并已通过正式 source rerender 完成替换与 refreeze；最后识别 Figure 5 的唯一剩余机会，即评估是否将 broader IFN-response depletion 对 discovery STAT2 的 attenuation 从 Supplementary S10 提升到 main Figure 5d。

因此截至目前，论文已经非常接近 main-scientific-figure 终冻状态。下一轮不应再大范围修改全文，而应只完成一个隔离式判断：

> **Figure 5d 到底保留 M5911 NES，还是正式换成 broader IFN-response depletion regulatory-ceiling panel。**

这个 gate 完成后，如果没有新的来源级错误，应立即停止主动重构，进入科学呈现维护冻结。
