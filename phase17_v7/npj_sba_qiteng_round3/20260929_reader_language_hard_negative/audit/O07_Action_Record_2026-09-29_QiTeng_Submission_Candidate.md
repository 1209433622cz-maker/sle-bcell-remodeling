# 本轮详细行动记录：QiTeng reader-language、硬负面与投稿候选冻结

日期：2026-09-29
目标：严格按照 QiTeng Academic Writing Skill v0.3.24.2 继续优化论文与投稿包，并给出下一阶段裁决。
最终状态：**PASS — QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE**

## 1. 输入与边界

本轮以用户上传的 QiTeng Round 2 投稿包及其审计包为父版本，并以 v0.3.24.2 的 `VERSION_REGISTRY.json`、Authority Model、Standard Output Contract、Submission Final Gate、Hard Negative Audit 和 Compression Governance 为规范。Round 2 已完成主文与投稿信的 guarded refinement，因此本轮没有重新改写已经稳定的标题、摘要、Results、Discussion 或声明，也没有重新打开 composition、pseudobulk、external mapper、ULM/CAMERA/FRY、M5911 或 perturbation 统计模型。

## 2. 独立发现的问题

Round 2 正确识别了 Figure 2c、3a、3c 的内部 `frozen` 标签，但 Supplementary Table S4b/S7、S10 图注及 S10 图内仍存在同类术语。若只修主图，会造成 main/supplement reader language 不一致。因此本轮把修复扩展到最小完整对象：Figure 2、Figure 3、Supplementary Table S4b/S7、S10 legend 与 Supplementary Figure S10。扩展仅限标签和角色文字，不改变科学对象。

## 3. 来源级修改

1. 从 `phase17_c7_01_build_main_figures.py` 重绘 Figure 2/3，将标签改为 `Primary >=50`、`Four prespecified programs in discovery`、`Prespecified IFN-arm genes`。
2. 从 `Supplementary_Information.md` 同步 Table S4b/S7 与 S10 legend：使用 `prespecified`，将 `Post-freeze sensitivity` 改为透明的 `Additional sensitivity`；Methods 中“added after the core regulator analysis had been fixed”仍保留，未把晚期敏感性伪装成预设分析。
3. 从 `phase17_round6_02_build_overlap_depletion_figure.py` 重绘 S10，将图内 `frozen` 标签改为 `prespecified`。
4. 重新从 Markdown/current builder 构建 Supplementary DOCX，保留已通过的 S7 列宽、cell padding 和分页修复；再分别用 WPS 与 LibreOffice 渲染。

## 4. 数据与证据保护

- Figure 2 source data：byte-identical PASS。
- Figure 3 source data：byte-identical PASS。
- Supplementary Figure S10 36-row depletion source data：byte-identical PASS。
- 统计输出改变：False。
- Manuscript DOCX/PDF、Figures 1/4/5、三套 Supplementary Data ZIP、Cover Letter 与声明：与 Round 2 byte-identical。
- 主文硬负面仍包括：B_ASC identity ceiling、primary composition non-support、weak genome-wide rho、mapper calibration failure、no corrected external effect、CAMERA/depletion exception、observational mechanistic ceiling 与 n=2 descriptive boundary。

## 5. 渲染与视觉质控

- 主文：31 页，31/31 人工视觉复核通过。
- Supplementary：WPS 15 页，LibreOffice 15 页。
- S7 第 4 页：两引擎均无词中断行，`Four prespecified programs` 与 `Additional sensitivity` 可读。
- S10 第 15 页：两引擎均无裁切/重叠；图题、图像同页；`prespecified` 标签清晰；discovery STAT2 interval-crossing-zero 边界保留。
- 主文与 Supplementary accessibility：均为 0 high / 0 medium / 0 low。
- PDF preflight：20 个 PDF，共 99 页，全部可打开且未加密。

## 6. QiTeng QA 与引用核查

QiTeng 自带 `qiteng_qa.py` 对两个 DOCX 均确认无 comments、tracked insertions 或 tracked deletions，期望术语存在且禁止术语不存在。该工具不能识别 Word 自动编号的参考文献，因此报告 `reference_count=0`；这属于已知解析限制，不作为 PASS 依据。独立 style-aware extraction 验证参考文献 1–33 连续、正文首次出现顺序 1–33、无 missing、无 orphan。

## 7. 回归与包完整性

- 历史 208 项测试中最初有 5 项仅因旧测试要求 Supplementary 根源文件与 9 月 8 日快照逐字节相同而失败。
- 已将测试更新为“除登记的 reader-language substitutions 外必须与历史快照完全一致”，并新增 7 项本轮专用测试。
- 最终回归：**215/215 PASS**。
- 最终包：38 个 manifest payloads；原目录和独立解包目录均通过 Verify_Package.py；ZIP 39 members；CRC PASS。
- ZIP SHA-256：`EBC9017D24FEACC5628DF978C09FF6D9CD33ABF41BBB7F2CE259A5EC80796709`。

## 8. 未执行事项

本轮没有提交期刊，没有填写 portal 账户字段，没有更新 GitHub Release，没有更新 Zenodo/DOI，没有重新计算生信结果，也没有触碰无关的 `05_Record/` 内容。

## 9. 下一阶段

进入 **SCIENTIFIC_SUBMISSION_CANDIDATE_MAINTENANCE_ONLY**。下一步只应由以下事件触发：作者对 exact ZIP 的最终批准；实际 portal 的文件类别/表单要求；上传后 PDF proof 的分页或字体问题；编辑/审稿人提出的明确科学问题；真实数值或 provenance 错误。没有这些触发条件时，不应继续主动压缩文字、搜索新 panel 或调整统计模型。
