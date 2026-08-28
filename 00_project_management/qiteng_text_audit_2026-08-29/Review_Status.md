# 精修主文审阅状态

**后续状态更新：**用户已确认本页哈希识别的主文为 QiTeng R2 科学正文冻结基线，确认作者/声明及 Ethics，并要求永久保留 R1/C9R HOLD。见[正式冻结确认](../qiteng_r2_freeze_2026-08-29/Scientific_Freeze.md)。下文保留的是本次确认之前的审阅记录，不再代表作者确认待办；原始 DOCX/PDF 不回写，后续 DOI/批准句的行政更新另行构建。

日期：2026-08-29。状态：**正文窄范围复核完成，当前精修文件待两位作者确认。**

## 当前应审阅的文件

- [主文 DOCX](review_candidate/Manuscript.docx)
- [WPS 后台导出的主文 PDF](review_candidate/Manuscript.pdf)
- [对应 Markdown 审阅源](review_candidate/Manuscript.md)
- [本轮详细行动报告](../action_record_2026-08-29_qiteng_manuscript_text_audit.md)

这三份文件是一套独立审阅稿，尚未替换 `01_manuscript/Manuscript.md` 或 `04_submission/corrected_candidate.zip`。文件名没有版本号；日期和审计状态只出现在管理路径。无需再次运行大矩阵或下载数据。

## 修改范围

保留来稿的 `GAP → RESPONSE → EVIDENCE → INTERPRETATION → BOUNDARY` 结构和 `distinguishes` 标题。169 段中局部修订 17 段，共 20 处替换：明确 B_ASC 不显著结果不等于等效或排除增加，IFN 支持限于预设程序比较，外部复现由源标签定义，R1/C9R 失败仍是解释边界。Jaccard 稳定性和程序关联复现不作为同一尺度上的统计比较。

数值、32 条参考文献身份、参考文献内容及五幅主图图注未改。修复了页眉/页脚重复边注行号，正文连续行号保留。最终 WPS 和备用 LibreOffice 渲染均为 18 页，均完成逐页视觉检查和全文文本比对。

收到的 PDF 与附带行动报告所列 SHA-256 不一致。其正文与收到的 DOCX 一致，但不据此解释二进制差异的原因；本次文件使用下列新校验值。

## Exact-File 校验值

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Manuscript.docx | 37,842 | `F6DB97C146A6DC41EED1910C0D0E5FCAA03C9A03EACF29EDA2CFB9F3803BBE0B` |
| Manuscript.pdf | 253,145 | `DE6F9E1AAFD45995C99507FBC733AAF9FB8ACC1BD9AC6C1E2ED444AED60B7E73` |
| Manuscript.md | 63,712 | `D383FF7605144531DF8E6CF1F3DC710561ABB2D88E3B957EAE0DD94ABD8F7A32` |

完整输入、15 份图源数据和核验脚本指纹见 [evidence_manifest.csv](evidence_manifest.csv)，汇总回执见 [final_verification.json](final_verification.json)。

## 作者确认范围

Zhi Chen 与 Teng Qi 的姓名、单位、邮箱、ORCID 及已确认的伦理/利益冲突/资助/致谢信息没有重新推断或变更。既有批准只覆盖此前识别的文件，不能自动作为这三份新文件的批准。主文 Authors' contributions 已明确标为当前精修文件待批准。

下一步需要两位作者审阅并确认本页识别文件的科学叙事与解释边界，尤其是：

1. 主结果是 B_CONV IFN/ISG 关联及源标签定义的外部复现，不是新 B 细胞分类体系。
2. B_ASC 主比较不显著不等于不存在作用，R1 的 B_ASC 稳定性失败与 C9R 的校准失败均保留。
3. 调控分析为观察性支持；不宣称直接结合、唯一配体、因果机制或临床效用。

本页不是已签署的批准表，也不预勾选任何同意事项。对这套审阅稿的认可不包含未来期刊化修改、归档发布、费用或投稿授权。

## 下一阶段判断

**不再以增加 cohort、mapper、TF 或 sensitivity 作为默认任务。** 在没有新错误证据的前提下，科学计算维持冻结。

当前窄范围正文审计已完成。下一阶段为 `AUTHOR_TEXT_SIGNOFF_AND_JOURNAL_TARGET_FREEZE`：作者确认本稿内容；取得目标刊的官方 JCR 年度、类别、排名/分母和 quartile 证据，以及 APC/减免书面条件，再确定唯一目标刊。已有[学校咨询草稿](../jcr_q1_target_preparation_2026-08-29/Institutional_Request_Draft.md)可继续使用，本轮没有发送邮件。

定刊后只做一次必要的标题、摘要、章节、图文组合与投稿信适配。当前摘要按固定空格分词为 330 词，不宣称满足任何指定刊的限制。既有短摘要草稿不是本次精修稿的获批替代物，需要保留本轮收紧的边界后再使用。

最后将适配后的主文、补充材料、图表、数据与投稿信作为一套文件核验，完成匹配代码/数据的新版本 DOI 和 exact-file 最终批准。已有 DOI 对应历史快照，不标作当前修订的归档。当前没有新 release、tag、DOI 或投稿提交。
