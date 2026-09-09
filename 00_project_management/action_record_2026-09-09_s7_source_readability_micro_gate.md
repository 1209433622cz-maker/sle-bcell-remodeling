# S7 实际尺寸可读性修复与来源重建记录

日期：2026-09-09。父版本：0150179774e84dd1c71d908ec07888d8e92556bd。最终状态：PASS_S7_READABILITY_MICRO_GATE。

## 发现与判断

本轮接受外部意见指出的真实问题：Supplementary Table S7 的窄列导致 Confirmatory、reproducibility 等词在词中间断行。上一轮联系表检查不足以排除这一局部缺陷，故撤回“呈现无需局部修复”的过强判断，仅重新打开 S7 排版。

用户提供的 DOCX/PDF 为非 canonical proof。检查其 OOXML 时发现 grid/tcW 宽度异常，例如第一列 tcW=868680 twips，远超页面宽度；其显示效果依赖渲染器纠正。正式实现没有复制这些宽度值，而是在当前项目 builder 基础上从冻结 Markdown 重建补充材料。

## 实现

- 新增 `audit_tools/phase17_npj_sba_62_s7_readability.py`，复用上一轮 Markdown builder 和 S5 修复函数。
- S7 总宽度为 165.1 mm，六列比例为 19:27:24:19:23:18，约为 24.13/34.29/30.48/24.13/29.21/22.86 mm。
- 单元格左右及 start/end 内边距均为 50 twips；固定布局，保持 10.5 pt 正文字号。
- S7 的全部 11 行（含表头）、统计术语、数值和多重检验描述保持不变。整个 DOCX 的文本节点及字号节点序列与父版一致。
- S7 压缩后，为 S2 添加显式段前分页，并将段前距设为 0 pt。初次渲染曾使 S2 下移 6 pt；修正后第 7 页恢复与父版逐像素一致。
- 只生成新的补充材料。原主文、Markdown 科学正文和上一轮成品保留，旧审计结果作为历史记录不被覆盖。

## 验证结果

1. WPS 和 LibreOffice 均为 15 页。
2. 两引擎变化页均严格为第 4、5、6 页；其余 12 页分别与各自引擎的父 PDF 逐像素一致，包含第 7-15 页。
3. S7 全部七字母及以上英文词在 PDF 第 4 页存在完整词形；结合该页放大图人工检查，未发现原来的词中断行。自然连字符处换行保留。
4. 六张联系表覆盖双引擎 30 页，另对第 4-6 页逐页放大核查，未见裁切、表格覆盖页脚、空白页或图题分离。
5. S1-S10 图题/图像同页及图像指纹检查在两引擎全部通过。S1 位置随第 6 页流排变化，其图像内容没有改变。
6. 新补充材料 DOCX accessibility 为 0 high / 0 medium / 0 low。主文未重新生成，沿用父版本已验证结果。
7. 45 个科学图件/Source Data 文件与冻结清单 SHA-256 一致；根目录主文和补充 Markdown 与冻结源一致。
8. 原投稿 ZIP SHA-256 仍为 `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`。本轮未操作 Release 或 Zenodo。
9. 全量回归：208 项全部通过，0 failure、0 error、0 skip。执行命令为 conda run -n sle-bcell python -m unittest discover -s audit_tools -p 'test_*.py'，本次执行耗时 6.317 秒。

## 产物与复现

当前补充材料版本位于 `phase17_v7/npj_sba_s7_readability/20260909_source_rebuild/documents/`；LibreOffice 交叉验证 PDF 位于同运行目录 `lo_final/`。主文及主图仍使用 20260908_final_cross_document 基线。

来源重建使用 bundled Python 运行 `audit_tools/phase17_npj_sba_62_s7_readability.py`。随后运行现有 `render_docx_with_wps.ps1` 和文档技能 `render_docx.py --emit_pdf`，分别输出到 documents 和 lo_final。使用现有 `phase17_npj_sba_09_supplement_pagination_audit.py` 检查两份 PDF（expected-pages=15，source-dir 指向父版 figures/figures），输出 pagination.json；使用文档技能 a11y_audit.py 输出 a11y.json。最后用 D:/bioinfor/python.exe 运行 `audit_tools/phase17_npj_sba_63_audit_s7_readability.py --visual-confirmed`；此参数仅在实际查看本次输出后传入。

本轮 audit.json 记录两引擎页面变化、全文/字号一致性、哈希和人工检查确认；page_comparison.csv 记录 30 次逐页比较；input_provenance.json 记录五个外部 proof 输入的大小与哈希。旧试渲染保留在本地忽略目录，避免被误当成当前版本。

## 子图裁决与下一阶段

本轮明确维持 21/21 主图子图 KEEP。Figure 1d 的身份边界、Figure 4d 的校准失败、Figure 5d 的 depletion 例外继续各自承担主文证据职责；没有新事实支持替换它们，也没有重跑统计分析的必要。

本次修复通过后进入 SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY。后续只按明确的数值/引用/来源问题、实际尺寸缺陷或新增作者科学反馈局部重开。继续维护 process-level B_CONV IFN/ISG remodeling 的正结论，同时完整保留 identity、transfer 与 mechanistic limits。局部排版通过不等于对整篇论文再次作全新科学审计，也不构成投稿或发表质量保证。
