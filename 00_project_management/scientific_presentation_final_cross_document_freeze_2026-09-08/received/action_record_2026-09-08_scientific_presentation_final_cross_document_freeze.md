# SLE B-cell remodeling：科学呈现终局跨文档冻结审计与精修行动记录

**日期：** 2026-09-08  
**工作状态：** `SCIENTIFIC_PRESENTATION_FINAL_CROSS_DOCUMENT_FREEZE_PASS`  
**工作边界：** 仅处理手稿科学叙事、主图/补图信息架构、claim ownership、cross-reference 与来源一致性；**未推进 submission package、portal、Release 或 Zenodo**。  
**上游 Figure 5 状态：** `SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE`。

## 1. 本轮独立判断

本轮不再把“继续优化”理解为继续增加分析或继续替换子图，而是对当前五张主图和十张补图做一次终局 hostile cross-document read。判断标准不是“还能不能更漂亮”，而是：

1. 主文一级 claim 是否由最合适的主图直接拥有；
2. 关键失败边界是否进入 reader-first path，而不是只藏在 Supplementary；
3. 主图 summary 与 Supplementary full audit 是否分工清晰；
4. Figure legend、Results、Discussion、Supplementary source-data map 与 machine-readable source data 是否同向；
5. 是否存在任何理由重新开启统计模型或重新选择 panel。

结论：**没有新的主图/补图需要重绘或替换。** Figure 1d、4d、5d 三次 source-promotion 已把全文三个最重要的“ceiling”放入主图：identity ceiling → transfer ceiling → regulatory/mechanistic ceiling。Figure 2 与 Figure 3 的 8 个 panels 均仍具有独立信息职责，没有冗余到值得替换。

## 2. 21 个主图 panels 的最终裁决

- Figure 1：1a/1b/1c `KEEP`；1d `KEEP_SOURCE_REPLACEMENT_ALREADY_ACCEPTED`。逻辑是 workflow → conditional fixed-representation pass → stricter end-to-end B_ASC failure。
- Figure 2：2a–2d 全部 `KEEP`。分别承担 observed+adjusted composition、contrast hierarchy、mandatory sensitivities、90-deletion influence；没有可被更高信息量 panel 替代的槽位。
- Figure 3：3a–3d 全部 `KEEP`。分别承担 four-program family、IFN robustness ladder、gene-level IFN-arm coherence、technical/pan-B specificity；共同把“process-level reproducibility”建立起来。
- Figure 4：4a–4c `KEEP`；4d `KEEP_SOURCE_REPLACEMENT_ALREADY_ACCEPTED`。4d 必须继续显示 required elastic-net 的 B_ASC calibration failure，而不是回退到较弱的 influence-only panel。
- Figure 5：5a/5b/5c/5e `KEEP`；5d `KEEP_SOURCE_REPLACEMENT_ALREADY_ACCEPTED`。5d 的 depletion summary 明确显示：12-gene arm 去除后 6/6 ULM CI 仍在 0 右侧，而 broader M5911 depletion 后 discovery STAT2 变为 0.391 [−0.745, 1.526]、q=0.500；这比旧 3 根 NES bars 更能定义机制证据上限。

详见 `FINAL_MAIN_PANEL_DECISION_MATRIX_2026-09-08.csv`。

## 3. 本轮发现的两个真实跨文档缺陷

### 3.1 Discussion 最终 landing 少了 Figure 5 对应的机制边界

现行末句只写“within explicit identity and transfer limits”。这在 Figure 5d 被正式提升为 regulatory-ceiling owner 以后，已经不能完整闭合五图叙事。它不是科学错误，但会让最终 landing 只回收 Figure 1 + Figure 4，而没有回收 Figure 5。

**来源级修正：**

`within explicit identity and transfer limits`

→

`within explicit identity, transfer and mechanistic limits`

该修正不增加任何机制 claim，反而把“不建立因果机制”的 ceiling 明确纳入最终结论。

### 3.2 Supplementary Table S5 的 selected source-data map 落后于三次主图 promotion

S5 仍把 Figure 1 描述为 identity stability/two-compartment adjudication、Figure 4 描述为 replication/influence、Figure 5 描述为 regulatory/orthogonal evidence。三行都没有反映后来正式进入主图的 boundary panel。

**来源级修正：**

- Figure 1 → `Disease-blind identity stability, two-compartment adjudication and end-to-end B_ASC boundary`
- Figure 4 → `Source-label-defined GSE135779 replication, gene-level coherence and required calibration boundary`
- Figure 5 → `Regulatory convergence, IFN-overlap-depletion ceiling and orthogonal response evidence`

这三处只修改 source-data map 的 human-facing description；CSV 来源、数值、panel letter、multiplicity family 与统计模型均不改变。

## 4. 数值与 claim-owner 终局核验

自动 cross-document audit 共 **54/54 PASS**。关键检查包括：

- Figure 1d：B_ASC end-to-end median Jaccard 0.930323，低于 0.95 criterion；
- Figure 2：primary OR 0.946653，正文 0.947 [0.636–1.410]，P=0.787；secondary flare q=0.084521，未升级；
- Figure 3：primary IFN/ISG effect 0.836556，正文 0.837 [0.525–1.148]；
- Figure 4d：coverage 0.941958 PASS、B_CONV precision 0.996450 PASS、B_ASC precision 0.885210 FAIL，正文明确“不估计 corrected external disease effect”；
- Figure 5d：12-gene depletion 6/6 ULM CI >0；M5911-depleted discovery STAT2 0.390658 [−0.745046, 1.526362]，q=0.500111，CI crosses 0；
- Fig. 1–5 与 Supplementary Fig. S1–S10 legends/cross-references 均存在且 ownership 对齐；
- 21 个 main panels inventory 完整；历史 source replacements 仅为 1d/4d/5d。

详见 `FINAL_CROSS_DOCUMENT_AUDIT.csv/json` 与 `FINAL_CLAIM_OWNER_MATRIX_2026-09-08.csv`。

## 5. 图件复核：为什么本轮不继续重绘

五张主图整体已经形成完整的信息梯度：

`identity ceiling → composition boundary → reproducible IFN process → independent source-label-defined replication → transfer ceiling → observational regulatory convergence → regulatory/mechanistic ceiling`。

Supplementary S1–S10 继续承担 full diagnostic ownership。重新移动 S4/S8/S10 的更多细节到主图会产生两类损失：一是重复已经存在的 boundary summary，二是使主图从“结论 + ceiling”退化为“审计结果堆叠”。因此，本轮 **不重新绘制任何 panel** 是主动的科学信息架构决策，而不是停止质控。

Figure 5 当前 170 mm composite 复核无标签裁切、CI 遮挡或 annotation collision；5d 的 discovery STAT2 crossing-zero annotation 可读，5a 的 evidence-class boundary 与 5e 的 `n=2; descriptive` 限制也在第一视野。

## 6. 文档重建与版式 QA

只从可编辑 DOCX/source markdown 修正，不手工修改 PDF。

- 新 DOCX/PDF：31 pages；
- 与上一 canonical DOCX 使用同一 renderer 比较：**30/31 pages pixel-identical**；仅 page 15 因最终 Discussion landing 增加 `mechanistic` 而发生预期变化；
- page 15 实际渲染无溢出、孤行或分页漂移，Methods 仍从同页正常开始；
- 全 31 页联系表复核无 clipping、overlap、blank page、tail page；
- DOCX accessibility audit：**0 high / 0 medium / 0 low**；
- PDF preflight：31 pages、可打开、未加密、非扫描 PDF。

## 7. 当前论文的科学成熟度

当前手稿已经不应再通过“多加分析”增强。它最强的地方是正结论和负边界共同构成证据层级：

- fine-state failure 被保留；
- B_ASC end-to-end overlap criterion failure 被保留；
- primary B_ASC composition 不支持被保留；
- genome-wide rho≈0.026 被保留；
- source-label-independent mapping calibration failure 被保留；
- discovery STAT2 CAMERA exception 被保留；
- broader-IFN depletion attenuation 被保留；
- GSE23307 n=2 被严格限制为 descriptive context。

因此最可信的 central claim 仍是：**process-level B_CONV IFN/ISG remodeling 比用于承载它的 hard state assignments 更可重复，但这种可重复性明确受 identity、transfer 和 mechanistic evidence ceilings 限制。**

## 8. 下一阶段裁决

本轮完成后不再进入新的“scientific enhancement gate”。下一阶段应正式切换为：

> **`SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`**

只有下列情况允许重新打开对象：

1. machine-readable source 与正文数值不一致；
2. claim owner / cross-reference 错位；
3. panel clipping、overlap、actual-size unreadability；
4. source provenance/hash 失败；
5. 新的真实数据或作者级科学反馈要求改变证据解释。

以下理由不再允许重开：仅为了“更漂亮”、增加更多 pathway/network、后验救显著性、重选 mapper、把 negative boundary 移除、再从 Supplementary 搬 panel 到 main。

**下一阶段目标不是投稿工程，而是维持当前 scientific baseline 的稳定性，等待真实的新证据或作者反馈。**
