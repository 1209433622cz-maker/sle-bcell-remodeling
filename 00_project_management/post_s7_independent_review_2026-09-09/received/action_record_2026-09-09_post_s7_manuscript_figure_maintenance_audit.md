# SLE B-cell remodeling：S7 修复后的手稿与主图独立维护审计

日期：2026-09-09  
项目：https://github.com/1209433622cz-maker/sle-bcell-remodeling  
当前 GitHub main 基线：`b1a9d28963fc9d82d407f4e2d1d5a01630ffde46`  
审计定位：只评估手稿文本、主图/子图职责、补充材料可读性与科学呈现；不推进投稿包、Release 或 Zenodo。

## 1. 本轮输入与独立核查范围

本轮将用户提供的 `action_record_2026-09-09_s7_source_readability_micro_gate.md` 和 `npj_sba_s7_readability.zip` 作为外部完成候选进行独立复核，并同步检查 GitHub `main` 当前状态、最新 S7 source rebuild commit、当前 `01_manuscript/Manuscript.md`、最终 21-panel decision matrix 与 Figure 1–5 claim ownership。

重点不是重复接受 `PASS` 标签，而是确认：
1. S7 修复是否真正来源重建而不是手工改成品；
2. WPS/LibreOffice 实际尺寸是否消除原来的词中断行；
3. 科学正文、字号、图件与 Source Data 是否保持冻结；
4. 21 个主图 panel 是否仍有值得修改、替换或重跑的对象；
5. 当前 manuscript reader path 是否仍完整闭合；
6. 是否还有足够高的信息增益支持重新开放分析。

## 2. S7 readability micro-gate：独立结论

结论：`PASS_S7_READABILITY_MICRO_GATE` 可以接受。

核查要点：
- S7 从冻结 Markdown/current builder 重建，而不是复制上一轮 non-canonical proof 的异常 OOXML 宽度；
- S7 保持 10.5 pt 正文字号，只调整六列宽度、cell padding 和 S2 pagination；
- S7 11 行文本、统计术语、数值和 multiplicity 描述不变；
- WPS 与 LibreOffice 均维持 15 页；
- 变化严格局限于 pp.4–6；
- 实际打开 WPS/LibreOffice 第 4 页，`Confirmatory`、`reproducibility` 等原问题词已完整显示，无词中断行；
- 第 5 页 S8/S9 表无裁切或拥挤；
- 第 6 页 S1 图题、正文和完整图件仍同页；
- a11y 0 high / 0 medium / 0 low；
- S1–S10 图题/图像同页及 fingerprint 通过；
- 45 个科学图件/Source Data 不变；
- 208/208 regression PASS；
- 原 submission ZIP、Release、Zenodo 未触碰。

因此，上一轮唯一允许重新打开的 actual-size defect 已关闭。

## 3. 手稿文本：当前科学逻辑是否还值得继续改

### 3.1 标题与摘要

当前标题把两个真正需要对照的层次放在同一句中：
- reproducible interferon remodeling；
- less stable B-cell state assignments。

这是全文最重要的 epistemic contrast，不建议为了简短而删去其中任一层。

摘要已经形成完整闭环：
`disease-blind reconstruction -> end-to-end identity failure -> assignment-exchange propagation -> source-label-defined external IFN replication -> failed source-label-independent calibration -> observational STAT1/STAT2 ceiling -> bounded conclusion`。

不建议继续压缩。再压缩会首先损失 negative boundary，而这正是本文区别于普通“发现 IFN signature”文章的价值。

### 3.2 Results

Results 的当前顺序应维持：
1. identity scaffold 与 end-to-end ceiling；
2. primary B_ASC composition negative boundary；
3. B_CONV IFN/ISG discovery；
4. source-label-defined independent replication；
5. corrected mapper calibration failure；
6. observational regulatory convergence + depletion ceiling。

这套顺序比“先展示显著 IFN，再补限制”更强，因为所有正结论先经过其对应的可解释性边界。

不建议新增 pathway/network 结果，也不建议把 external atypical/low-naive、flare composition 或更多 regulator 家族升级为主线。它们会稀释唯一真正跨数据集稳定的 process-level claim。

### 3.3 Discussion

当前 Discussion 的终局结构已经达到高成熟度：
- 第一段定义“不是新 taxonomy”；
- 第二段与既有 SLE biology 对接；
- 第三段解释 program-specific replication 与 genome-wide rho≈0 的共存；
- 第四段限制 regulatory evidence；
- 第五段明确哪些 tempting narratives 不成立；
- 第六段只提出 prospective translational implication；
- 第七段系统列出 remaining evidence gap；
- 结尾用 `identity, transfer and mechanistic limits` 三重 ceiling 收束。

不建议继续做语义强化。尤其不应把：
- “IFN-centred regulatory context”改成“STAT1/STAT2-driven mechanism”；
- “source-label-defined replication”改成“transferable state replication”；
- primary composition null 改写成“B_ASC unchanged”；
- n=2 GSE23307 改成独立机制验证。

## 4. 21 个主图 panel：修改 / 保留 / 替换裁决

### Figure 1 — identity ceiling
- **1a KEEP**：workflow 是 disease-blind identity -> disease inference 的唯一 reader map。不要换成 UMAP 作为开场，否则视觉上会重新制造“taxonomy-first”印象。
- **1b KEEP**：fixed-representation ARI 说明条件性稳定。
- **1c KEEP**：fixed-representation state Jaccard 与 1d 构成必要对照。
- **1d KEEP，且不得退回旧 panel**：它是 end-to-end B_ASC boundary 的主图 owner。只有来源数值错误或实际尺寸问题才能重开。

替换方案评估：
- 加 UMAP：信息增益低，taxonomy overread 风险高；
- 把更多 S4 replicate diagnostics 搬入主图：重复且拥挤；
- 只保留 1d 删除 1b/1c：会失去“conditional pass vs end-to-end fail”的方法学逻辑。
因此当前 4-panel 架构最优。

### Figure 2 — composition boundary
- **2a KEEP**：observed fractions + adjusted means 是描述与模型的桥梁。
- **2b KEEP**：primary/internal/nonoverlap/flare 层次不可少。
- **2c KEEP**：prespecified sensitivities 防止“null 只是模型脆弱”质疑。
- **2d KEEP**：90 次 leave-one-sample-out 是最直观的影响诊断。

替换方案评估：
- 用 violin/boxplot 取代 2a：会弱化 sample-level model ownership；
- 删除 2d：会丢失最易理解的 robustness evidence；
- 把 flare 单独做显著 panel：会错误放大 secondary result。
因此全部保留。

### Figure 3 — process-level discovery
- **3a KEEP**：四个 frozen programs 建立 IFN/ISG 的相对优先级。
- **3b KEEP**：IFN robustness ladder 是主结果的中心 owner。
- **3c KEEP**：gene-level positive-arm coherence 给 process-level result 提供粒度更细的支持。
- **3d KEEP**：platelet/ambient、ASC/UPR、pan-B specificity 是排除 generic/technical explanation 的必要负控。

替换方案评估：
- 用 volcano plot：会把文章重新导向 genome-wide discovery，偏离 prespecified program inference；
- 用 GSEA 网络：信息密度低、机制暗示过强；
- 删除 3d：会让 IFN specificity 的防守不足。
因此当前 4-panel 设计优于常规 DEG/volcano 风格。

### Figure 4 — independent replication + transfer ceiling
- **4a KEEP**：外部 childhood/combined/adult/support-threshold hierarchy。
- **4b KEEP**：直接连接 discovery/internal 与 external。
- **4c KEEP**：4,410 shared genes 的 rho≈0.026 与 ten IFN genes 同向同时展示，是全文最关键的“program-specific vs transcriptome-wide”区分之一。
- **4d KEEP，且不得退回旧 panel**：corrected elastic-net B_ASC precision 0.885 < 0.90，明确阻止 source-label-independent transfer overclaim。

替换方案评估：
- 只展示 external IFN effect 而删除 4c/4d：文章会从严谨 replication 退化成简单 confirmatory signature paper；
- 把 centroid mapper 的通过结果升级：违反 prespecified required-mapper policy；
- 再调 elastic-net threshold：属于 post-outcome retuning，不应做。
因此当前 4-panel 结构应冻结。

### Figure 5 — observational regulatory context + mechanistic ceiling
- **5a KEEP**：必须维持“evidence classes / interpretive roles”式 schematic，不应改成 causal network。
- **5b KEEP**：STAT1/STAT2 + IRF7/IRF9 quantitative owner。
- **5c KEEP**：proliferation comparators 是 specificity control。
- **5d KEEP，且不得退回旧 M5911-only bars**：12-gene depletion 后 6/6 ULM CI 仍 >0，但 broader M5911 depletion 使 discovery STAT2 跨零；这是最重要 mechanistic ceiling。
- **5e KEEP**：n=2 GSE23307 只作为 descriptive perturbational context。只有真正增加 biological replicates 后才值得替换。

替换方案评估：
- 新增 TF network/cell-signalling network：会把 observational evidence 图形化成因果机制；
- 删除 5d：会让 Figure 5 过于“正向”；
- 放大 5e：n=2 权重不应超过三组 disease contrasts。
因此当前 5-panel 架构是信息/风险比最佳版本。

## 5. Supplementary figures / tables 的维护判断

S1–S10 继续作为 full-audit owner，而不是主图候选池：
- S4：full end-to-end identity diagnostics；
- S5：composition diagnostics；
- S6：ranked-list / pseudobulk diagnostics；
- S7：external replication influence；
- S8：reference calibration boundary；
- S9：correlation-aware regulator sensitivity；
- S10：完整 overlap-depletion sensitivity。

不建议再把 S4/S8/S10 进一步搬到主图。当前 F1d/F4d/F5d 已经分别抽取了最小充分 boundary summary。

Supplementary Table S7 本轮已修好，因此不再是 open item。

## 6. 是否还需要“优先重跑分析”

当前答案：**没有证据支持主动重跑**。

可重跑的合法触发条件仅包括：
1. 真实数值错误；
2. claim-owner / cross-reference 错位；
3. provenance/hash failure；
4. actual-size clipping/readability defect；
5. 新的真实数据；
6. 明确的作者级科学反馈提出可检验的新问题。

以下不应成为重跑理由：
- 为了获得更显著结果；
- 为了增加 pathway/network；
- 为了换 mapper；
- 为了让 B_ASC composition 变成正结果；
- 为了弱化 rho≈0.026 或 CAMERA exception；
- 为了把 n=2 perturbation 包装成机制验证。

## 7. 当前科学状态

建议当前状态定义为：

`SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY`

主正结论：
**process-level B_CONV IFN/ISG remodeling 在 prespecified discovery、internal robustness 和 source-label-defined external analysis 中具有可重复性。**

必须并存的三个 ceiling：
- **identity ceiling**：B_ASC end-to-end overlap criterion failure；
- **transfer ceiling**：corrected source-label-independent mapper calibration failure；
- **mechanistic ceiling**：regulator evidence observational，且 broader IFN-response depletion 可明显削弱 discovery STAT2。

这三个 ceiling 不是“论文弱点需要修掉”，而是文章可信度和方法学价值的一部分。

## 8. 下一阶段目标

下一阶段不应进入 submission-oriented work，也不应主动寻找新的 panel 或 pathway。

建议进入：
`SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY`

工作方式：
- 仅对真实新问题局部重开；
- 每次重开必须有明确 object、scientific reason、source-level rebuild、before/after audit 和 stop rule；
- 不允许直接手改 canonical DOCX/PDF；
- 不改变当前 21-panel ownership；
- 不推进 submission ZIP、Release 或 Zenodo，除非用户之后明确改变工作边界。

结论：S7 micro-gate 已关闭；当前没有新的高信息增益科学/图形对象值得主动重开。继续修改的 post-hoc 风险已经高于预期收益。
