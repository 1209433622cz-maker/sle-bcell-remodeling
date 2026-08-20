# Gate C8 行动记录：Genome Medicine 投稿包与 WPS 终检

**日期：** 2026-08-20
**执行范围：** 期刊路线冻结、作者元数据、投稿版主文与补充材料、参考文献核验、DOCX 构建、WPS 后台渲染、逐页视觉质控、机器审计、完整性清单与交接 ZIP。
**上游科学冻结：** `PASS_GATE_C7_MANUSCRIPT_AND_FIVE_FIGURE_SCIENTIFIC_FREEZE`
**本轮最终决策：** `PASS_GATE_C8_SCIENTIFIC_TECHNICAL_SUBMISSION_PACKAGE_AUTHOR_DECLARATIONS_AND_ARCHIVE_REQUIRED`

## 1. 导师级结论

本项目已完成从“科学结果冻结”到“指定期刊投稿技术包”的转换。主文逻辑、五图证据链、数字来源、独立验证、外部调控证据和非因果边界均保持 Gate C7 冻结状态，没有为了适配期刊而更改结论或挑选新结果。

当前可以确认：

- 科学与技术投稿包通过 Gate C8。
- Genome Medicine 为当前最合理的首投目标。
- Communications Biology 为首个转投备份，Journal of Autoimmunity 为疾病专科备份。
- Nature Communications 仍只适合作为新增直接功能证据后的高风险路线。
- 当前不得进入投稿门户最终提交，因为作者控制的声明、机构伦理判断和永久归档尚未闭合。

## 2. 期刊路线与规范冻结

2026-08-20 按官方页面核查并冻结以下要求：

- Genome Medicine Research article。
- 结构式摘要 Background/Methods/Results/Conclusions，不超过 350 词。
- 3-10 个关键词。
- 正文含 Background、Methods、Results、Discussion、Conclusions、List of abbreviations 和完整 Declarations。
- 主文双倍行距、连续行号和页码。
- 图题不超过 15 词，图注不超过 300 词；单个图文件小于 10 MB。
- 可编辑主文与机器可读支持数据。

官方核查入口：

- https://link.springer.com/journal/13073/aims-and-scope
- https://link.springer.com/journal/13073/submission-guidelines
- https://link.springer.com/journal/13073/submission-guidelines/research

没有在项目文件中声称固定的 JCR/CAS 分区。该信息需由投稿单位在当前订阅版本中另行核查，避免把年度变化的分区当成永久事实。

## 3. 作者元数据处理

已写入并核查：

- 第一作者：Zhi Chen。
- 通讯作者：Teng Qi。
- 两位作者的 CUHK-Shenzhen School of Medicine 单位信息。
- 第一作者邮箱 `zhichen1@link.cuhk.edu.cn`。
- 通讯作者邮箱 `tengqi@link.cuhk.edu.cn` 与完整通讯地址。
- ORCID：Zhi Chen `0009-0001-0072-5576`；Teng Qi `0009-0007-7648-4776`。
- 两位作者的 MSc student in Bioinformatics 身份和已提供的作者简介。

需要团队书面确认但未擅自推断：

- 两人作者名单是否完整。
- Teng Qi 作为通讯作者是否为团队的有意安排。
- 导师、数据贡献者和其他参与者应署名、致谢还是不列入。
- CRediT 分工和所有作者最终批准。

## 4. 主文与支持文件

生成的主文采用期刊投稿型式而不是宣传型版式：Times New Roman、黑色层级、Letter 纸张、1 英寸页边距、主文双倍行距、连续行号、页码和运行页眉。

主文关键统计：

- 结构式摘要：机器审计 284 词；源构建器计数 285 词，均低于 350 词。
- 关键词：8 个。
- 正文参考文献：17 条。
- DOI 文献：13 条全部通过 Crossref 标题和元数据核对。
- 图注：5 个；标题 6-9 词；图注 80-101 词，均满足期刊限制。
- 主文保留 6 个醒目的作者/机构占位块，投稿信保留 2 个，占位内容均以红色显示，避免误提交。

补充材料包含：

- 4 个扩展方法部分。
- 5 张补充表。
- 数据集角色与推断单位。
- 支持与不支持的主张边界。
- 冻结定量锚点。
- Figure-source data 映射。
- Gate C7 到 Gate C8 的可重复性合同。

## 5. 科学真实性与逻辑边界复核

机器审计再次锁定以下定量锚点：

- 主要 B_ASC 组成效应：OR 0.947，95% CI 0.636-1.410，P=0.787。
- GSE174188 主要 IFN/ISG 效应：0.837。
- GSE174188 donor-nonoverlap 效应：1.086。
- GSE135779 childhood 独立验证效应：1.042。
- 跨数据集全转录组 Spearman rho：0.026。
- M5911 NES：3.187、3.050、3.527。
- GSE23307 两位供体效应：3.294、3.666；每位均为 12/12 冻结基因同向。

继续禁止以下越界表述：

- 不把不稳定的 naive/memory/atypical 分群写成硬亚型。
- 不把 B_ASC 丰度写成中心阳性发现。
- 不把 GSE174188 内部 donor-nonoverlap 称为独立队列。
- 不隐去 rho=0.026 的低全转录组一致性。
- 不把 CollecTRI 活性推断写成直接结合或因果调控。
- 不声称唯一上游 IFN 配体。
- 不使用已废弃的未变换 GSE23307 输出。

## 6. 图件与源数据质控

五张主图均具备：

- 独立 PDF。
- 600 dpi PNG。
- PNG 尺寸至少 4254 x 3270 px。
- 单文件小于 10 MB。
- 对应的机器可读 CSV。
- Figure source-data ZIP 和 SHA-256 校验表。

图 1-5 继续分别对应 C2B4 identity freeze、C3A composition decision、C4B GSE174188 transcription、C5B independent replication 和 C6B regulatory framing，不存在图文结果来源漂移。

## 7. WPS 后台渲染与视觉质控

按用户要求，最终视觉基准改为本机 WPS COM 后台渲染，而不是只依赖 LibreOffice。

最终页数：

- 主文：21 页。
- 补充材料：3 页。
- 投稿信：1 页。
- 合计逐页检查：25/25 页。

发现并修复的排版缺陷：

1. 初次 WPS 渲染中，补充材料第 3 页的 `Supplementary Table S4` 标题被横向裁掉前半段。
2. 第一次修复恢复标题后，标题仍进入页眉区域并遮蔽运行页眉。
3. 最终在 DOCX 构建器中加入 S4 的确定性分页和 36 pt 页首缓冲。
4. 重建、重新 WPS 渲染并逐页复核后，S4 标题、页眉、表格和长路径全部完整。

最终未发现：

- 文字或表格越界。
- 重叠、缺字、黑块或特殊字符损坏。
- 标题底部残留蓝线。
- 行号/页码丢失。
- 长 DOI、SHA-256 或路径裁切。
- 补充表列宽失控或跨页断裂。

最终主文和投稿信渲染与已检查版本逐像素一致；补充材料修复版重新检查全部 3 页通过。

## 8. 自动化审计结果

`phase17_c8_04_final_submission_audit.py` 对以下方面执行 19 项独立检查，全部通过：

- Gate C7 上游冻结。
- 期刊目标。
- 作者身份和联系信息。
- 摘要与关键词。
- 正文和声明结构。
- 五个图题与图注长度。
- 五图文件、尺寸和大小。
- 三个可编辑 DOCX。
- 主文 OOXML 中的行号、页码、双倍行距、奇偶页眉和无标题边框。
- 补充表显式 DXA 几何。
- 13/13 DOI 核验。
- 冻结数字锚点。
- 过时主张清除。
- 非因果边界。
- 五份源数据及校验和。
- WPS PDF 页数和 25 个页面 PNG。
- 作者待填项保持可见。

机器判定：

- `scientific_technical_package_pass: true`
- `portal_submission_authorized: false`

## 9. 生成的核心文件

- `01_manuscript/manuscript_v10_genome_medicine_submission_2026-08-20.md`
- `01_manuscript/supplementary_information_v1_gateC8_2026-08-20.md`
- `04_submission/package_genome_medicine_gateC8_2026-08-20/`
- `04_submission/package_genome_medicine_gateC8_2026-08-20.zip`
- `phase17_v7/gateC8/20260820_genome_medicine_submission_package/03_GATE_C8_FINAL_AUDIT.json`
- `phase17_v7/gateC8/20260820_genome_medicine_submission_package/03_GATE_C8_FINAL_AUDIT.md`
- `phase17_v7/gateC8/20260820_genome_medicine_submission_package/04_GATE_C8_INTEGRITY_MANIFEST.csv`
- `phase17_v7/gateC8/20260820_genome_medicine_submission_package/05_GATE_C8_PACKAGE_STATUS.json`
- `audit_tools/run_6013RP_phase17_gateC8_submission_package.ps1`

最终交接 ZIP：

- 大小：10,651,523 bytes。
- SHA-256：`869983a00ad94995957aef2f3a8b2ac287e2c6cafedab52df51523361f9dfc00`。
- 包内清单记录 62 个文件；ZIP 额外包含完整性清单本身。

## 10. 仍未完成的硬性事项

以下信息只能由作者和机构确认，本轮没有编造：

1. 公开去标识数据二次分析的机构伦理判断：不需审查、豁免或 waived，以及适用时的委员会和编号。
2. 利益冲突声明。
3. 基金名称、项目号、受资助作者和资助方角色，或明确无专项资助。
4. 作者名单完整性、通讯作者安排、CRediT 分工和所有作者批准。
5. 致谢内容或明确 Not applicable。
6. 原创性、未一稿多投、所有作者同意投稿和政策问题确认。
7. GitHub 仓库开源许可证与 Zenodo 或等价永久归档 DOI。

APC/机构协议也应在投稿前由学校确认，但它不改变科学判定。

## 11. 下一阶段判断

下一阶段应进入 `Gate C8B`，优先封闭作者声明、伦理、署名完整性和永久归档，而不是继续探索性挖掘或新增图。

只有在 C8B 完成并重新生成无占位符版本后，才执行 Genome Medicine 投稿门户最终预检和提交。若首投后发生编辑拒稿，按已冻结路线优先转投 Communications Biology；除非补充患者匹配功能实验、直接结合证据或前瞻性验证，否则不建议为追求 Nature Communications 再堆叠公开数据集。
