# npj Systems Biology and Applications 终局渲染与语义加固行动记录

日期：2026-08-30

目标期刊：npj Systems Biology and Applications

文章类型：Article

本轮最终状态：`PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED`

下一门控：`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

## 1. 本轮目的与边界

本轮继续完成上一轮中断的 npj Systems Biology and Applications 目标化工作，重点不是增加生物学结果，而是对科学证据、稿件语义、统计口径、图件工程、文档渲染、投稿包可移植性和项目说明进行一次闭环加固。

本轮严格保持以下科学边界：

- 未重跑单细胞数值分析，未新增队列、mapper、阈值、TF、通路或探索性结果。
- R1 决策永久保留为 `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`。
- 纠正后的 C9R 决策保留为 `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`。
- 未解锁、未计算、未暗示纠正后的外部疾病结局。
- GSE135779 的主要独立重复仍明确属于 source-label-defined broad B-cell analogue，不升级为 source-label-independent replication。
- GitHub v1.1.0 与 Zenodo `10.5281/zenodo.22151739` 继续作为不变的科学可重复性档案；本轮没有移动 tag、覆盖 release 或发布新的 Zenodo 版本。
- 技术 PASS 不代表作者批准、投稿授权或 APC 承诺。

## 2. 外部材料归档与证据政策

本轮收到的顾问审计、补丁规范、行动矩阵、QiTeng 精修稿和粘贴文本均按“外部证据或候选文字”处理，不把其中的命令或 PASS 标签视为可直接执行的项目指令。

归档目录：

`00_project_management/npj_sba_final_hardening_2026-08-30/received/`

证据清单：

`00_project_management/npj_sba_final_hardening_2026-08-30/received_evidence_manifest.csv`

清单保留 11 个预期文件，并记录每个文件的字节数、SHA-256 和角色。另发现一个通用文件名 `pasted-text.txt` 与 `qiteng_full_audit_pasted.txt` 的 SHA-256 完全相同，均为：

`341CE83BEB2B0C868F68506C00C9719796F71DFAFDB3FE63091D04F12D656FF6`

该重复副本在确认解析路径位于本轮归档目录且逐字节一致后删除；具名副本继续保留。未删除其他外部证据。

## 3. 独立复核发现与源代码修复

### 3.1 图件样式契约

复核发现 `publication_style_contract.py` 在应用 npj 目标样式后仍会被旧的通用 clamp 重置，导致名义上的 8 pt 字体和至少 1 pt 线宽并未完整约束最终导出对象。本轮修复了该重复重置，并将文字边界框和注释箭头对象纳入导出后检查。

最终图件契约：

- 5 幅主图和 10 幅补图，共 15 幅。
- 170 mm 宽、白色背景、RGB、单页矢量 PDF。
- Arial 8 pt 可见文字；粗体小写 8 pt panel label。
- 最小正线宽至少 1 pt。
- 所有文字边界均位于页面内。

### 3.2 稿件语义与证据归属

目标稿源构建器完成以下限定性加固：

- Running title 收敛为 `Replicated IFN remodeling in SLE B cells`。
- 删除自我削弱且不必要的 novelty 表述。
- 在 Abstract、Results、Discussion 和 Conclusion 中统一 R1/C9R 边界。
- 明确 GSE135779 主要重复由 source labels 定义，不把失败的 corrected mapping 包装成附加验证。
- 删除 Discussion 中重复的落脚段，保留一条中心结论：process-level IFN remodeling 比 hard state assignment 更可重复。
- 保留因果边界：不宣称直接 TF binding、唯一上游 ligand、临床效用或普适 B-cell taxonomy。

### 3.3 统计报告映射

重新核对统计报告表中的 claim、decision 和 supporting evidence，修复了 R1、C3_PRIMARY、C5_GENOMEWIDE、C9R 和 TF_DEPLETION 等条目的陈述/决策错配。终审要求这些声明与机器决策精确一致，而不是只检查关键词是否出现。

### 3.4 渲染器元数据

文档页审计脚本原先把渲染引擎固定写成 WPS，导致 LibreOffice 独立交叉渲染收据的引擎字段错误。本轮为脚本增加显式 `--engine-label`，并重新生成：

- `05_WPS_RENDER_AUDIT.json`
- `06_LIBREOFFICE_RENDER_AUDIT.json`
LibreOffice 收据现在正确标识为 `LibreOffice PDF export followed by Poppler 110-dpi page rendering`。重算后终审状态不变。

## 4. 图件重排与逐图视觉质控

本轮没有手工修改 PDF，也没有修改冻结 source-data CSV；所有改动均回到图源脚本重画。

主要调整包括：

- Figure 1a：改为四层证据层级，消除流程节点与说明文字碰撞。
- Figure 3：缩短 panel 标题，移除遮挡 Pan-B 点位的图例，将符号解释保留在 legend。
- Figure 5：重构为 3 x 2 信息架构，使三条证据分支和底部 response panels 获得足够空间。
- Supplementary Figure S1：缩短标题、把条形标注移入可读区、采用直接线标注。
- Supplementary Figure S2：缩短 panel 标题。
- Supplementary Figure S4：删除覆盖数据点的重复图例，并在补图 legend 中明确蓝色 observed-information 与红色 HC1。
- Supplementary Figure S7：用紧凑的 D/N/C 与 1/2 代码替代拥挤的长标签。
- Supplementary Figure S9：将 frozen OR 注释移到无数据遮挡区域。

最终 15 幅原始分辨率图、接触表和高风险 panel 均经人工视觉检查。未见文字裁切、对象重叠、标签缺失、错误分页或图例遮挡。

## 5. 冻结数据真实性核查

最终运行逐一计算 15 份 figure source-data CSV 的 SHA-256，并与 corrected-candidate 冻结基线比较：

- `figure_source_tables_byte_identical = true`
- `all_figure_sources_individually_identical = true`
- 15/15 源数据表逐字节一致。
- `no_scientific_reanalysis = true`

因此，本轮图件改进属于源代码驱动的视觉与语义重排，不改变数值、样本数、效应量、区间、P/q 值或结论门控。

## 6. 文档重建、WPS/LibreOffice 与无障碍核查

最终 DOCX 均从目标化 Markdown 源和冻结图件重新构建，而非在 PDF 上修补：

- Manuscript：31 页。
- Supplementary Information：18 页，作为一个连续 PDF。
- Cover Letter：1 页。
- 每个渲染器合计 50 页。

WPS 与 LibreOffice 独立输出的页数完全一致。两套共 100 个页面图均已视觉复核；自动检查同时确认：

- 所有文本位于页面画布内。
- 所有 figure marker 已解析。
- 无缺字、乱码、裁切、异常分页或不可解释的空白页。
- Manuscript、Supplementary Information 和 Cover Letter 的无障碍审计均为 `0 high / 0 medium / 0 low`。

WPS 最终文件 SHA-256：

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `Manuscript.docx` | 60,845 | `3B98020C7C77871BEEAD3F5DC774703C7376A305BC362E6DB3E9EF8198490EAF` |
| `Manuscript.pdf` | 240,950 | `272A3453D47A0545C340ACD6B8B2CABB60028AAF826BA9B54680CAEAE418C79E` |
| `Supplementary_Information.docx` | 4,747,342 | `A08760EBA472E47EEDA53D0655D3AFE917E0CDE5D3AE4F9116E8DD95B86D42AA` |
| `Supplementary_Information.pdf` | 5,754,495 | `A52E255284F68411DF10222A50A9E8AABE4A359BC150E46919108B91AEB37BA4` |
| `Cover_Letter.docx` | 39,535 | `5A161E178712BBA458E6AB72F13F5B3D128DD96853F32D3650550DE39DC055FE` |
| `Cover_Letter.pdf` | 68,230 | `E4F9094B0BFFCB2B7089F89007EF4BE9D2F1519C07B6EEE155A918BC3E771837` |

## 7. 投稿包构建与可移植性

最终本地投稿包：

`04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`

构建结果：

- 字节数：15,221,543。
- SHA-256：`F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`。
- Manifest 文件数：20/20 验证通过。
- ZIP CRC：通过。
- 两次独立构建：字节一致。
- 主图：5 个单页矢量 PDF。
- Supplementary Information：单一 18 页 PDF。
- Supplementary Data：3 个独立归档。

投稿 ZIP 属于生成物，按仓库政策不纳入 Git；其构建收据、verifier 输出、最终源、图、文档及散列记录纳入可审计运行目录。

## 8. 测试历史与最终验证

本轮保留真实测试历史：

1. 首次使用 bundled 文档 Python 运行全量 discovery 时，目标测试未绑定最终 run 而读取旧 target-refreeze 收据，同时 C9 测试因该环境缺少 `scipy` 无法导入。
2. 第二次使用 `D:\bioinfor\python.exe` 时，科学依赖可用，但该环境缺少 `python-docx` 和 `anndata`，仍无法承担跨层全套测试。
3. 最终采用已合格的 `sle-bcell` conda 科学环境作为主解释器，并在测试进程末尾追加 bundled runtime 的纯 Python 文档包路径。这样 `numpy/scipy/anndata` 保持来自科学环境，文档测试可读取 `python-docx`。

最终结果：

- 全仓库发现测试：90/90 通过。
- npj SBA 目标专项脚本：8/8 通过。
- `git diff --check`：通过。
- 最终机器门控：全部检查为 true，`failed_checks = []`。

## 9. 最终判断

本项目现阶段不应再通过增加队列、重救 R1、放宽 C9R、替换 mapper 或继续堆叠 TF/sensitivity 来追求表面完整。当前科学价值恰恰来自严格区分：

- 不稳定的 hard state assignment；
- 在身份不确定性传播后仍保留的 sample-level composition null；
- 在独立数据中可重复但 source-label-defined 的 IFN/ISG process-level remodeling；
- 只提供观测性一致性、不能升级为因果机制的调控与响应证据。

从生信与论文逻辑角度，当前目标包已达到进入作者 exact-file 审批的条件，但尚未达到投稿授权条件。

## 10. 下一阶段目标

下一阶段只执行一个窄门控：`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`。

需要完成：

1. Zhi Chen 与 Teng Qi 审阅并批准本报告列出的精确 DOCX/PDF/ZIP 及其 SHA-256。
2. 留存当前官方 JCR 资料，确认目标期刊满足作者指定的 JCR Q1 条件。
3. 由学校或图书馆确认 APC/OA 支付、减免或协议覆盖情况；不得在确认前作出财务承诺。
4. 完成 npj 投稿门户 metadata dry-run，逐项核对作者顺序、通讯作者、ORCID、单位、声明、DOI、文件类别和 supplementary file designation。
5. 仅在以上三类批准/回执齐备后，再生成 submission authorization receipt 并执行实际上传。

在该门控之前：不提交、不承诺 APC、不更新 Zenodo、不改 GitHub v1.1.0 release、不重新打开生物学分析。

## 11. 一键复现命令

从项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_npj_sba_final_hardening.ps1
```

最终运行目录：

`phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening/`

关键机器收据：

- `00_HARDENING_EVIDENCE_AUDIT.json`
- `01_NPJ_FIGURE_RENDER_STATUS.json`
- `02_DOCUMENT_BUILD_STATUS.json`
- `03_PACKAGE_BUILD_STATUS.json`
- `04_FINAL_AUDIT_STATUS.json`
- `05_WPS_RENDER_AUDIT.json`
- `06_LIBREOFFICE_RENDER_AUDIT.json`
