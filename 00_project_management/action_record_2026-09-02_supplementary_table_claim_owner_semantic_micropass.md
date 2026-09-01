# 行动记录：Supplementary Table claim-owner 语义微调

- **完成日期：** 2026-09-02
- **最终状态：** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`
- **工作边界：** 手稿正文、表格证据归属与跨引用；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮目标与独立判断

在 Supplementary Figure 首次引用顺序已经冻结后，独立核查 Supplementary Tables S1-S9 的正文 claim ownership。外部 hostile audit 仅作为证据输入，最终裁决来自 canonical manuscript 与 Supplementary Information 的逐项比对。

独立核查确认三处语义错位：Table S3 是定量锚点而非因果未识别声明的直接 owner；Table S4a/S4b 分别拥有 correlation-aware 与 overlap-depletion 结果；Tables S5-S8 描述当前来源、统计和归档结构，而不直接证明旧稿未被用作数值来源。

## 2. 来源级修复

仅执行六个精确文本操作：

1. 将 Supplementary Table S3 移至 quantitative synthesis sentence，并从 causal non-identification sentence 移除。
2. 将泛化的 Supplementary Table S4 拆分为 S4a 和 S4b，分别锚定 Supplementary Fig. S9 与 S10 对应段落。
3. 将 Supplementary Tables S5-S8 移至 Reproducibility opening sentence，并从 superseded-object sentence 移除。

Tables S1-S2 与 S9 的正文位置保持不变。Supplementary Tables S1-S9 仍全部具有正文入口；Supplementary Figures 的首次引用顺序仍为 S1-S10。

## 3. 图件与数据裁决

- 21 个主图子图全部 `KEEP`；38 个补充图子图全部 `KEEP`。
- Figure 1a 保留，继续作为 identity-to-disease inference boundary 的唯一主图 owner。
- Figure 5a 保留，继续作为 evidence class 与 causal ceiling 的唯一主图 owner。
- 0 个新增 panel，0 个替换 panel，0 个来源重画。
- 45 个冻结的 PDF、PNG 与 Source Data CSV 资产哈希全部不变。
- Supplementary Information canonical source 未改变。
- 科学数字序列未改变；统计模型、估计、阈值与 Source Data 均未重算或改写。

## 4. 文档构建与 QA

- WPS 主文：31 页，SHA-256 `3487C0D69BBC29727E44744CBDD2041A08B7BA5720B14B043719B2F8FCF49B0F`。
- LibreOffice 主文：31 页，SHA-256 `2777488A0B3959BE7766B2BFB43BD3B86377EEEF3A6A2BE2B8EDF192B157A62A`。
- 两种渲染器页数一致，全部页面文本非空、位于页面边界内且无未解析标记。
- 12 张联系表覆盖双引擎共 62 页，已逐页人工检查；无空白页、截断、重叠、缺字或异常分页。
- DOCX accessibility audit 为 0 high / 0 medium / 0 low。
- 全量回归测试：180/180 通过。
- 投稿包 SHA-256 保持不变。

## 5. 科学结论与下一阶段

本轮没有改变中心结论，只提升 supporting table 与正文主张之间的一对一可追溯性。现有图件体系已经完整覆盖 identity boundary、composition、pseudobulk transcription、external replication、calibration failure、regulator sensitivity 与 observational ceiling，没有新增分析或替换 Figure 1a/5a 的科学理由。

下一阶段返回 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`。只有出现可定位的数字错误、语义越界、交叉引用错误或实际尺寸可读性缺陷时，才启动局部来源修复；不再主动扩展分析、网络模型或图件。
