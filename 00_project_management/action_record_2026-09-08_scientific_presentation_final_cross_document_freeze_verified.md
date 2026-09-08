# 行动记录：科学呈现终局跨文档冻结的独立复核与落地

- **完成日期：** 2026-09-08
- **最终状态：** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`
- **工作边界：** 手稿、补充材料、图件职责、数值可追溯性与跨文档渲染；未推进投稿包、GitHub Release 或 Zenodo
- **上游状态：** `SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE`
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮如何处理外部候选

Downloads 中的终局冻结候选被视为待验证输入，而不是项目指令或自动批准。8 个输入文件已逐字节归档并记录 SHA-256。正文与补充材料均从当前 GitHub canonical source 重新构建；重建结果分别与外部 Markdown 候选完全一致后才写回项目。外部 DOCX/PDF 仅用于敌意复核，不作为 canonical 成品复制来源。

外部 54 项 cross-document audit 为 54/54 PASS；本项目脚本又直接读取冻结 Figure 1-5 Source Data、正文、补充材料和 21-panel matrix，独立重做同一组 54 项检查，结果同样为 54/54 PASS。

## 2. 实际来源级修订

本轮仅执行 4 个文本操作：

1. Discussion 最终 landing 从 `identity and transfer limits` 收束为 `identity, transfer and mechanistic limits`。
2. Supplementary Table S5 的 Figure 1 描述增加 `end-to-end B_ASC boundary`。
3. Figure 4 描述增加 `gene-level coherence and required calibration boundary`。
4. Figure 5 描述增加 `IFN-overlap-depletion ceiling`。

第一项没有提高机制主张，反而把 Figure 5 的非因果边界纳入全文结尾。其余三项只更新 human-facing source-data ownership；没有改变 CSV、统计值、阈值、panel letter、mapper、contrast 或 multiplicity family。

## 3. 21 个主图 panel 的最终裁决

- Figure 1：1a/1b/1c `KEEP`；1d 保留已经完成的来源替换。1d 是 end-to-end B_ASC identity ceiling 的最小充分主图表达。
- Figure 2：2a-2d 全部 `KEEP`，分别拥有 observed/adjusted composition、contrast hierarchy、mandatory sensitivities 和 90 次 leave-one-sample-out。
- Figure 3：3a-3d 全部 `KEEP`，分别拥有 frozen program family、IFN robustness ladder、gene-level coherence 和 specificity controls。
- Figure 4：4a-4c `KEEP`；4d 保留已经完成的来源替换。4d 阻止把 source-label-defined replication 误写成 source-label-independent transfer。
- Figure 5：5a/5b/5c/5e `KEEP`；5d 保留已经完成的来源替换。5d 同时显示 12-gene depletion 的 6/6 正区间和 M5911-depleted discovery STAT2 的跨零例外。

因此，本轮没有重画或替换任何图。45 个现行主图、补图和 Source Data 资产全部与 Figure 5 上游基线哈希一致。继续把 S4/S8/S10 的更多诊断搬入主图会重复现有 boundary summary，并降低 reader-first claim density。

## 4. 数值与证据边界复核

- Figure 1d：B_ASC end-to-end median Jaccard 0.930323，低于 0.95 criterion。
- Figure 2：primary OR 0.946653，正文报告 0.947 [0.636-1.410]，P=0.787；flare q=0.084521，未升级为支持性结论。
- Figure 3：primary IFN/ISG effect 0.836556，95% CI 0.525430-1.147683，q=2.977 x 10^-6。
- Figure 4d：coverage 0.941958 PASS、B_CONV precision 0.996450 PASS、B_ASC precision 0.885210 FAIL；未估计 corrected external disease effect。
- Figure 5d：12-gene arm 去除后 6/6 ULM CI >0；M5911-depleted discovery STAT2 为 0.390658 [−0.745046, 1.526362]，q=0.500111。

正结论仍严格限定为可重复的 process-level B_CONV IFN/ISG remodeling；fine-state、B_ASC stability、composition、genome-wide concordance、transfer calibration、CAMERA、depletion 和 n=2 perturbation 的负面边界全部保留。

## 5. 文档与视觉 QA

- WPS 主文：31 页，SHA-256 `5936E699167148357E38526DE87B8E20DBEA69181FE5854D67F8E2F64D6E61AE`。
- LibreOffice 主文：31 页，SHA-256 `6F491C929A21BFAB4B2E82ED1324007470957B9029260706C9C368223DC025B3`。
- WPS 补充材料：15 页；LibreOffice 补充材料：15 页。
- 双引擎共 92 页、18 张联系表完成逐页视觉检查；无空白页、越界文本、图文错页、裁切、重叠或未解析标记。
- 相对上游 WPS 基线，主文 30/31 页逐像素一致，唯一变化为第 15 页；补充材料 11/15 页逐像素一致，变化严格局限于第 3-6 页。补充材料的受控差异来自 S5 三处 ownership 文本更新、S5 列宽优化及随后连续表格的重新流排；第 7-15 页恢复逐像素一致，同时消除了试构建中出现的空白页。
- Supplementary S1-S10 的标题、嵌图同页和图像指纹在 WPS/LibreOffice 两套 PDF 中全部通过。
- 两份 DOCX accessibility audit 均为 0 high / 0 medium / 0 low。
- 全量回归：208/208 通过。

## 6. 冻结与下一阶段

本轮正式进入 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`。以下情况才允许重新打开对象：真实数值错误、claim-owner/cross-reference 错位、provenance/hash 失败、actual-size clipping/readability 缺陷、新的真实数据，或作者级科学反馈。

仅为了更漂亮、增加 pathway/network、后验救显著性、重选 mapper、弱化负结果，或再把 Supplementary panel 搬入主图，不构成重开理由。下一阶段目标是维护这条已闭合的 reader path：`identity ceiling -> composition boundary -> process-level IFN reproducibility -> source-label-defined external support -> transfer ceiling -> observational regulatory convergence -> mechanistic ceiling`。
