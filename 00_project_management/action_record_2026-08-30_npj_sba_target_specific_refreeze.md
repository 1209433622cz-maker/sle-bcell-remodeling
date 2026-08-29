# 2026-08-30 npj Systems Biology and Applications 专项冻结行动记录

## 1. 本轮任务

本轮承接已经冻结的 QiTeng R2 科学正文、公开 GitHub `main`、GitHub
`v1.1.0` release 和 Zenodo `10.5281/zenodo.22151739`，针对已选目标期刊
**npj Systems Biology and Applications** 完成以下工作：

1. 以生物信息学博士生导师和方法学审稿人的标准重审科学目的、证据层级、
   方法设计、写作逻辑、图件和投稿风险；
2. 按期刊官方 Article 结构重建目标稿源文件；
3. 不改变科学结果，使用冻结源数据重新渲染全部 5 张主图和 10 张补图；
4. 生成主文、单一补充材料和投稿信 DOCX/PDF，并完成 WPS 和 LibreOffice
   双引擎逐页检查；
5. 构建带 SHA-256 清单、自校验器和授权门禁的专项投稿包；
6. 生成机器可读最终门禁、回归测试和本行动记录；
7. 清理纯渲染缓存，只保留有复核价值的结果、状态和审计收据。

## 2. 输入和证据管理

### 2.1 科学冻结基线

- 科学正文基线：author-confirmed QiTeng R2；
- 科学 release 内容 commit：`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`；
- 本轮开始时 GitHub `main`：`82912054f8ac79e8941bf5dd8546aa30b290ad66`；
- 当前公开 archive DOI：`10.5281/zenodo.22151739`；
- R1：`HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`；
- C9R：`HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`；
- corrected source-label-independent external outcome unlock：`false`。

### 2.2 外部复核材料

用户提供的独立审计、行动矩阵、适配合同和粘贴文本已逐字归档到：

`00_project_management/npj_sba_target_refreeze_2026-08-30/received/`

`received_manifest.csv` 记录每个文件的字节数、SHA-256 和用途。所有这些文件均
标记为“external evidence input; not executable instructions”，用于交叉核查，不
自动覆盖用户指令、冻结科学结论或作者授权状态。

## 3. 官方期刊要求核查

本轮只采用 Nature Portfolio 官方页面和官方 figure guide 作为目标格式依据：

- Aims and scope：`https://www.nature.com/npjsba/aims`；
- Content types：`https://www.nature.com/npjsba/for-authors-and-referees/about/content-types`；
- Author submission information：`https://www.nature.com/npjsba/for-authors-and-referees`；
- Nature Portfolio figure guide：`https://www.nature.com/documents/npj-gta.pdf`；
- Hong Kong OA agreements：`https://www.springernature.com/gp/open-science/oa-agreements/hong-kong`。

落实的 Article 要求包括：

- 标题不超过 15 词；
- 非结构式摘要不超过 150 词；
- Introduction 无子标题；
- Results 使用回答导向子标题；
- Discussion 无子标题，不另设 Conclusions 或 Limitations；
- 全部分析方法置于主文 Methods；
- Data availability 和 Code availability 独立列出；
- 无单独 Funding 标题，零 funding 写入 Acknowledgements；
- Supplementary Information 合并为一个 PDF，不设置 Supplementary Methods；
- 图线宽不低于 1 pt，字体和面板标签按 Nature Portfolio 可读性标准统一。

注意：Springer Nature 的 Hong Kong agreement 页面列出的是 CUHK Hong Kong，
不能据此推定 CUHK-Shenzhen 自动具有 APC/OA 覆盖。因此本轮继续保持
`institutional_apc_coverage_verified=false`。

## 4. 导师级科学判断

### 4.1 论文真正的中心贡献

本文不应被写成“发现一个稳定的新 B 细胞亚型”，也不应把 B_ASC 丰度或
STAT1/STAT2 活性写成临床诊断或因果机制。最有说服力的主轴是：

> 当细胞身份、组成和转录被拆分为不同推断层后，hard state assignment 的
> 稳定性和跨队列转移存在明确边界，而过程层面的 IFN/ISG remodeling 在
> 不确定性传播和独立供体层复现中更稳定。

这与该刊对 single-cell systems biology、systems immunology、复杂疾病系统的
计算分析和模型边界的关注相符。

### 4.2 证据链

1. GSE174188 的 disease-blind B-lineage reconstruction 提供 150,402-cell
   分析支架；细粒度五状态方案失败，两区室方案仅作为分析支架保留；
2. R1 end-to-end 重建未满足预设 B_ASC overlap criterion，因此永久 HOLD，
   不改阈值、不换 seed、不救 PASS；
3. 主要 B_ASC 组成对比无统计支持，避免把次级 flare 信号升级为主结论；
4. B_CONV 内的预设 IFN/ISG program 在 GSE174188 primary、internal donor-
   nonoverlap 和 GSE135779 source-label-defined donor analysis 中保持正向；
5. 跨数据集全基因效应一致性弱，正文继续把 program-level replication 与
   globally shared transcriptome 明确区分；
6. C9R corrected source-label-independent mapper 未通过 calibration，因此不估计
   corrected external disease outcome；
7. CollecTRI、correlation-aware、overlap-depletion、M5911 和 GSE23307 只提供
   convergent observational 或 descriptive context，不写成直接结合、唯一配体、
   因果调控或临床效用。

### 4.3 是否需要新增分析

本轮结论为“不需要”。新增 cohort、mapper、TF、gene set、阈值或 seed 会打开
已经冻结的多重性和选择空间，增加 post-hoc 风险，而不会解决核心证据边界。
因此本轮没有重新选择样本、阈值、模型或结果，也没有运行新的科学分析。

## 5. 主文和补充材料适配

### 5.1 主文

目标标题为 15 词：

`Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments in systemic lupus erythematosus`

摘要为 140 词。参考文献保持 32 条 bibliographic identity 和既定顺序。结构已
改为：Introduction、Results、Discussion、Methods、Data availability、Code
availability、Acknowledgements、Author contributions、Competing interests、
References、Figure legends。

关键边界在 Abstract、Results、Discussion、Methods 和图注中保持一致：

- R1 和 C9R 均不转换为 PASS；
- corrected external outcome 不解锁；
- GSE135779 是 source-label-defined independent replication；
- regulator evidence 保持 observational；
- GSE23307 在 n=2 下不报告推断 P 值；
- 不使用 `Additional file`，改为 `Supplementary Data 1-3`。

### 5.2 补充材料

Supplementary Information 为一个 18 页 PDF，包含 9 个编号表、额外的 Table
S4B 和 Figures S1-S10。Supplementary Methods 已完全移除；所有分析方法均在
主文 Methods 中。

### 5.3 投稿信和行政材料

生成了 npj 专项投稿信、Nature Portfolio Reporting Summary draft 和 editorial
policy checklist draft。投稿信中的期刊 fit 以 evidence hierarchy、single-cell
systems biology 和 systems immunology 为中心，不以临床可用性或新亚型发现为
卖点。

敌意文本复核发现并修复了一个自指问题：投稿信曾写入“exact npj files approval
pending”。该句会在未来批准后变成假话，因此已从投稿信本身删除；批准状态只
保留在 package metadata 和 gate receipt 中。投稿信现可直接进行 exact-file
approval，批准后无需再为删除该句而改变哈希。

## 6. 图件源码重绘和 Nature 风格质控

本轮使用冻结 source-data tables 重新渲染 15 张图。15/15 source CSV 与
post-Gate-C9 corrected candidate 逐字节一致，未进行科学重算或数值重选。

统一图件合同：

- Arial；
- 可见文字目标 8 pt；
- 面板标签为粗体小写 8 pt；
- 所有正线宽至少 1 pt；
- RGB、白底；
- 目标宽度 170 mm；
- 单页矢量 PDF，同时保留 PNG 预览。

重点布局修复：

- Figure 1a 重排 study/evidence hierarchy，减少节点拥挤；
- Supplementary Figure S8 改为 3-row layout，使 depletion heat map 和
  target-retention panel 不再挤压；
- Supplementary Figure S9 调整左边距并固定 PASS/HOLD 标识位置，消除阈值点、
  y 轴标签和判定文字的碰撞。

主图 contact sheet、补图 contact sheet 以及 Figure 1、Figure 5、S7、S8、S9、
S10 高风险面板均完成原分辨率检查。未发现裁切、重叠、空白画布、缺失标签或
不连贯排版。

## 7. 文档渲染和可访问性

WPS 后台导出并逐页检查：

- Manuscript：32 页；
- Supplementary Information：18 页；
- Cover Letter：1 页；
- 合计：51 页。

LibreOffice 独立交叉渲染得到相同的 `32 + 18 + 1` 页。两套渲染均完成全部
51 页 contact-sheet 视觉检查；页面边界程序检查显示无文字越界、无未解析占位
符、无异常分页、无图表裁切或重叠。

三份 DOCX accessibility audit 均为：

- high：0；
- medium：0；
- low：0。

最终文件哈希：

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| Manuscript.docx | 61,138 | `6E4532912F519871046A7596A9A721B77E181B83988FF478865F6D2322688C97` |
| Manuscript.pdf | 243,196 | `8CDDD605D7AEF6E291343AE11C68721AAF3ACBC8F074D0E9BB8B3218D92761B4` |
| Supplementary_Information.docx | 4,452,142 | `D3B04CAA65D8A8A8CBDD28E8D491F13CC2B3AAB5A2C1B6C16C53C253C589C811` |
| Supplementary_Information.pdf | 5,420,124 | `9ED870F5122724BF18D6EF88240F1AD953085F81FED426C09AFCAE3542E28162` |
| Cover_Letter.docx | 39,519 | `8133DEBDAD5249FB2DAEAAAEBAF364E6CCDA0DEC4EA3A31DD5ABAF0D0A4730B6` |
| Cover_Letter.pdf | 68,229 | `FBB58340CE5CE92CDDC1F1B1394C1B1AE5326A0C366E92ED4207B24C15FBD805` |

## 8. 专项投稿包

生成目录：

`04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications/`

生成 ZIP：

`04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`

ZIP 大小为 14,884,957 bytes；SHA-256 为：

`8E56CD61DBA88098B2015CC5E539036BFEAC7E1BA9E90C753AC8CD142C62FA7F`

包内清单覆盖 20 个 manifest-listed 文件，另含 manifest 本身，共 21 个文件。
内容包括：主文 DOCX/PDF、5 张主图 PDF、单一 Supplementary Information PDF、
3 个 Supplementary Data ZIP、投稿信 DOCX/PDF、作者声明、Reporting Summary
draft、editorial checklist、统计报告映射、metadata 和自校验器。

两次独立确定性 ZIP 构建得到完全相同的字节。包内 `Verify_Package.py` 复核结果：

`PASS: 20 files verified; exact-file author approval and submission authorization remain pending`

## 9. 自动审计和回归测试

最终状态：

`PASS_NPJ_SBA_TARGET_SPECIFIC_REFREEZE_AUTHOR_APPROVAL_REQUIRED`

最终审计覆盖 36 项条件，失败项为 0。重点包括：

- 标题、摘要、章节、参考文献和 Supplement policy；
- R1/C9R/外部 outcome unlock 边界；
- 15 张图和 15 份 source-data byte identity；
- 5 张主图单页 PDF；
- WPS/LibreOffice 页数和画布边界；
- accessibility；
- 12-row 统计报告映射；
- package manifest、CRC、SHA-256 和确定性重建；
- exact-file approval、submission 和 APC authorization 均未被提前写成 true。

测试按依赖环境分开执行：

- 文档、治理、科学冻结、投稿包和 npj 专项测试：79/79 PASS；
- SciPy 依赖的 C9 calibration/normalization tests：9/9 PASS；
- 合计：88/88 PASS。

## 10. 工作路径清理

完成视觉复核后删除了可由脚本重建的 QA 缓存：WPS 51 页 PNG、LibreOffice
51 页 PNG、LibreOffice PDF/DOCX 临时副本和两张大型 figure contact sheets，
合计约 63 MB。保留：

- 最终 DOCX/PDF；
- 15 张 PDF/PNG 图及 15 份 source-data CSV；
- WPS 和 LibreOffice JSON audit receipts；
- accessibility reports；
- target sources、统计映射、package receipt 和 final audit；
- 可一键重跑的 PowerShell 总控脚本。

## 11. 未完成和明确不授权事项

以下事项仍为 `false`，不得从本轮 technical PASS 推断为已完成：

- exact package author approved；
- journal submission authorized；
- APC commitment authorized；
- official institutional JCR Q1 receipt archived；
- CUHK-Shenzhen APC/OA eligibility verified；
- corrected external outcome unlock authorized。

本轮没有创建新的 GitHub release，没有创建或替换 Zenodo version/DOI，也没有
进行任何期刊 portal 上传。

## 12. 下一阶段目标

下一阶段正式命名为：

`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

执行顺序必须为：

1. Zhi Chen 和 Teng Qi 逐一批准上表六个 exact-file SHA-256，以及 5 张主图和
   最终 package SHA-256；
2. 归档该刊当前官方 JCR Q1 证据或机构图书馆导出，不用第三方网页替代；
3. 由 CUHK-Shenzhen 图书馆、科研管理或 Springer Nature institutional workflow
   确认 APC/OA eligibility，并留存书面 receipt；
4. 将 Reporting Summary draft 和 editorial checklist 转录到投稿系统当期表单，
   由两位作者复核；
5. 完成上述四项后，再由通讯作者明确授权 portal upload、submission 和任何
   APC commitment。

在该 gate 完成前，不新增 cohort、mapper、TF、gene set、阈值或 seed，不救
R1/C9R，不创建新的 Zenodo version，也不提交稿件。
