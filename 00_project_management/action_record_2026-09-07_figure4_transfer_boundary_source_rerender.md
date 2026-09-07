# 行动记录：Figure 4 外部转移边界来源重绘与科学重冻结

- **完成日期：** 2026-09-07
- **最终状态：** `SCIENTIFIC_FIGURE4_TRANSFER_BOUNDARY_PROMOTION_REFREEZE`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮问题与独立裁决

外部 hostile read 指出：旧 Figure 4d 重复呈现 donor/source-label influence，而“校正 source-label-independent mapping 未通过预设 B_ASC precision 门槛”这一决定外部结论证据等级的关键边界只存在于 Supplementary Figure S8。独立复核确认该信息层级问题，但没有直接采用外部候选图，也没有允许 nearest-centroid mapper 替代预先要求的 elastic-net mapper。

最终裁决为：Figure 4a-c 保持原职责；旧 Figure 4d 的完整 influence diagnostics 由 Supplementary Figure S7 继续拥有；新 Figure 4d 必须从哈希锁定的 S8 Source Data 重算并呈现 required elastic-net calibration。Figure 2、Figure 3、Figure 5 与 Supplementary Figures S1-S10 均保持冻结。

## 2. 来源、算法与数值核验

- 冻结 Figure 4 Source Data SHA-256：`F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755`。
- Supplementary Figure S7 Source Data SHA-256：`A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6`。
- Supplementary Figure S8 Source Data SHA-256：`FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF`。
- required elastic-net coverage = 0.941958，criterion = 0.80，`PASS`。
- required elastic-net B_CONV precision = 0.996450，criterion = 0.90，`PASS`。
- required elastic-net B_ASC precision = 0.885210，criterion = 0.90，`FAIL`。
- 因 B_ASC calibration 失败，不估计 corrected source-label-independent external disease effect。
- 外部候选 CSV 与 S8 冻结来源在 1e-12 容差内逐值一致；图件颜色重新编码为蓝色通过、红色失败，避免把失败项画成绿色。
- 没有重跑统计模型、改变样本、估计、阈值、候选网格或 mapper policy。

## 3. 图件重绘与子图职责

- Figure 4a：`KEEP`，拥有 GSE135779 source-label-defined IFN/ISG effect 与 support-threshold 结果。
- Figure 4b：`KEEP`，拥有 discovery/internal 与 source-label-defined external effect 对照。
- Figure 4c：`KEEP`，独占 4,410 shared genes 的 gene-level coherence 与 10/10 IFN gene direction concordance。
- Figure 4d：`SOURCE_REPLACEMENT_FROM_LOCKED_S8_REQUIRED_ELASTIC_NET`，直接显示两项通过和 B_ASC precision 失败。
- Supplementary Figure S7：`KEEP_FULL_INFLUENCE_OWNER`，保留 43 次 donor deletion 与 8 次 source-label omission 全部诊断。
- Supplementary Figure S8：`KEEP_FULL_REMAP_OWNER`，保留完整 remapping、candidate selection 和 calibration 细节。
- Figure 4 最终尺寸 170.0 mm x 137.87 mm；失败项、阈值线和“不估计校正效应”的结论均在正常阅读尺寸下可见。
- 45 个 figure/source-data 资产中仅 Figure 4 PDF、PNG 与 Figure 4 Source Data 三项改变，其余 42 项哈希不变。

## 4. 手稿同步

仅执行四项来源级精确修改：将 donor/source-label influence 的主权交给 Supplementary Fig. S7；将 gene-level coherence 引用收窄到 Fig. 4c；把 corrected calibration failure 锚定到 Fig. 4d；同步重写 Figure 4 legend。Title、Abstract、Discussion、Conclusion、Figure 5 全节、Supplementary Information、参考文献与其他图注均保持不变。

为消除跨引擎孤立尾页，Figure 4 图注仅做语义等价压缩；coverage、B_CONV/B_ASC calibration、0.885 < 0.90、未估计 corrected external disease effect、criterion line 及 S7/S8 evidence ownership 均完整保留。

## 5. 文档、视觉与回归 QA

- Figure 4 PDF SHA-256：`B1120AA60E9B03FBE835E9979F0449F67B483B792C9339737CB0CD40C5A2B75F`；PNG SHA-256：`6FBF35DE2D5D425E11B46B029D2239AF61084A4685DBA672C19CC59F8C6F9BD7`。
- WPS 主文：31 页，SHA-256 `0DB51A93BE06F84DD09D47648BA8C6553C336FECA6B73913BC0D5475D074CE51`。
- LibreOffice 主文：31 页，SHA-256 `F4324AD59C9A3E4D8A8BE0B00CA1D7523006A56359A2FF2AA38A4E7B9CD49114`。
- 双引擎共 62 页、12 张联系表已逐页视觉检查；无空白页、截断、重叠、缺字、异常分页或 cross-render 尾页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：194/194 通过。
- 投稿包 SHA-256 保持不变；Release 与 Zenodo 未触碰。

## 6. 当前科学判断与下一阶段

Figure 4 现在形成更严格的证据阶梯：source-label-defined replication 成立，program-level direction concordance 成立，但 corrected source-label-independent B_ASC transfer 不满足预设 calibration，因此不能升级为 de novo taxonomy transfer 或 corrected external disease effect。该失败不是需要“救 PASS”的瑕疵，而是外部证据解释边界。

下一阶段进入 `FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE`。仅比较当前 Figure 5d 与冻结来源重绘的 broader IFN-response depletion 候选在 170 mm 完整 Figure 5 组合中的信息增益、视觉密度和 claim ownership。候选只有在不遮蔽 discovery STAT2 的 CI-crossing-zero 例外、且明显优于当前 5d 时才可替换；否则保留当前 Figure 5d 并回到科学呈现维护冻结。
