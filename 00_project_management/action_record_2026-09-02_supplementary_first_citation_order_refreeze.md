# 行动记录：Supplementary Figure 首次引用顺序科学呈现冻结

- **完成日期：** 2026-09-02
- **最终状态：** `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`
- **工作边界：** 手稿、补充材料与图件科学呈现；未推进投稿包、GitHub Release 或 Zenodo 发布
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮目标

独立复核外部 hostile audit 指出的 Supplementary Figure 首次引用顺序问题，判断是否需要保留、修改或替换既有子图，并在不改变任何统计估计、Source Data 数值或科学结论的前提下完成来源驱动的交叉引用修复。

## 2. 独立复核结果

修复前，正文首次出现 Supplementary Figure 的顺序确认为 `S1, S2, S3, S9, S4, S5, S6, S10, S7, S8`。这不是统计错误，也不是图件内容错误，而是显示编号与 reader path 不一致。外部提供的映射经独立重建后完全一致：

`S1->S1; S2->S2; S3->S3; S9->S4; S4->S5; S5->S6; S6->S7; S10->S8; S7->S9; S8->S10`。

修复后，正文首次引用顺序为严格的 `S1-S10`。Supplementary Information 中标题、占位标记、图件文件名、Figure Source Data 文件名及 Supplementary Table S5 的 figure-source map 同步更新。

## 3. 子图保留、修改与替换判断

- 21 个主图子图全部 `KEEP`；0 个新增，0 个替换。
- 38 个补充图子图全部 `KEEP`；仅显示编号变化，科学对象逐字节不变。
- Figure 1a 保留：它仍是 identity-to-disease inference boundary 的唯一主图责任面板。
- Figure 5a 保留：它仍是 evidence class 与 causal ceiling 的唯一主图责任面板。
- S1-S10 的 PDF、PNG 与 Source Data CSV 共 30 个映射对象均与旧显示编号下的对象 SHA-256 相同。
- 本轮没有重新运行统计模型，没有重画图，没有修改任何数值或阈值。

## 4. 文本与交叉引用修复

正文仅增加四个功能性 Supplementary Table 导航锚点：Tables S1-S2、Table S3、Table S4、Tables S5-S8；既有 Table S9 引用保留。Tables S1-S9 现在均可由正文定位。锚点均并入原句或既有括号引用，未新增科学主张。

## 5. 文档构建与跨渲染修复

补充材料比较了 16 页标准候选与 15 页紧凑候选。两种候选均通过 WPS/LibreOffice 图题同页和图像指纹检查；采用 15 页候选，因为它移除了 S1 前的冗余手工分页，未缩字号、未压缩表格、未改变科学内容。

新增导航锚点最初使 LibreOffice 将 Figure 5 图例最后两行推到第 32 页。最终修复没有删减图例或缩小字号，而是将五个主图图例标题的段前/段后间距统一为 6/2 pt。主文随后在 WPS 与 LibreOffice 中均为 31 页。

WPS PDF 文本抽取会去除部分词间空格，导致候选选择器的完整 S1 图例匹配出现假阴性。QA 解析器已改为忽略空白的规范化匹配；10 张图的身份指纹在修复前后始终通过。

## 6. 最终 QA

- WPS 主文：31 页，SHA-256 `3744A4CCC48C6F889D900DF88316E913832B2994182AE5E1DCB624D5FE4F9902`。
- LibreOffice 主文：31 页，SHA-256 `B8BEDCBD37B1AEF4E7A6065C397777270AD454FF715772B5DDBDD9F5B37E0743`。
- WPS Supplementary Information：15 页，SHA-256 `417DA08BA22B0978982245638C607ADE55FB7E99F4050E7DBFD669326B0948A5`。
- LibreOffice Supplementary Information：15 页，SHA-256 `8D7565D47F7D07A254FFB49555DC70DE1494FDC208C3A3904AF9B6BFC78ABAE8`。
- 18 张联系表覆盖双引擎共 92 个页面，已逐页人工检查；无空白页、截断、重叠、缺字或错图。
- 最终补充材料重新选择后，六张 Supplementary 联系表 SHA-256 与人工检查版本完全一致。
- S1-S10 在两种渲染器中均保持标题、图例和图像同页；10/10 图像指纹匹配。
- 两份 DOCX 的 accessibility audit 均为 0 high / 0 medium / 0 low。
- 全量回归测试：170/170 通过。
- 作者已确认的投稿包保持 `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`，未被本轮覆盖。

## 7. 科学结论与下一阶段

本轮修复提升了 Supplementary reader path 和可核查性，但没有改变论文的中心结论：可重复证据支持 broad B_CONV IFN/ISG process-level remodeling；hard fine-state assignment、source-label-independent external transfer 与 causal regulator inference 仍保持明确边界。

下一阶段进入 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`。当前不应重新打开统计模型、Figure 1a、Figure 5a 或任何补图。只有发现新的、可定位的数值错误、语义越界、交叉引用错误或实际尺寸可读性缺陷时，才执行局部来源重跑；否则不再以“继续完善”为由增加分析或重画图。
