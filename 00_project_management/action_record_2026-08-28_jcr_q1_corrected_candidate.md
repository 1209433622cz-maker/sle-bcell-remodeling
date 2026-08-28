# 2026-08-28 行动记录：图文纠错整合与 JCR Q1 投稿候选包

## 1. 本轮结论

本轮已把此前仅停留在预览的 Figure 1c 纠错正式整合到候选图、主文图注和重建文档中，并修复了额外发现的 Figure 1a 框间重叠。新候选包通过了完整性、文档语义、便携性和差异范围检查。

当前交付物是 **已完成技术验证、尚待选刊定稿的 corrected candidate**，不是已获授权的期刊投稿包。原作者批准记录和原包完整保留；没有将旧批准自动覆盖到新文件。JCR Q1 的官方排名和分区证据仍未齐备。

本轮没有重算疾病效应、修改阈值或删除历史失败记录。图像修改来自绘图源码，文档修改来自 Markdown 源码；未直接涂改结果表、DOCX 或 PDF。

## 2. 输入与工作范围

- 用户要求：继续推进，完成后判断下一阶段，并产出本轮详细 Markdown 报告。
- 已确认背景：两位作者批准前一审阅快照、主文及投稿信；投稿标准为 JCR Q1。
- 本轮起点 Git：`c68775982f47a637dbc2bfa1b89df3640984b31d`。
- 输入审计、16 项行动矩阵及粘贴文本均按原字节存入 [received](jcr_q1_refreeze_2026-08-28/received/)，哈希见 [integration audit](jcr_q1_refreeze_2026-08-28/candidate_integration_audit.json)。
- 附件中的“发布”“投稿”等建议视为待评估工作项，不视为用户新增对外发布、付款或提交授权。
- 本轮是有边界的图文纠错整合与投稿准备，不宣称重新审计了整个硬盘或重跑了所有数值分析。

## 3. 对新审计意见的判断

| 事项 | 核查判断 | 本轮处理 |
| --- | --- | --- |
| Figure 1c 的 0.990 被误写为 mapped ARI | 成立；0.990 属于 mapping agreement，ARI 判据为 0.900 | 图和主文图注同步纠正 |
| source-label omission 的 excluding dependence 过强 | 成立 | 改为 arguing against，明确是 contributing source label |
| Methods 缺少 AI 披露 | 与当前源码不符 | 已存在 Generative AI assistance 小节，保留而不重复添加 |
| 统一 Nature-style 数值即可满足所有子刊 | 不成立 | 保留当前审阅规格；定刊后按实际指南复核 |
| 新包可以继承旧作者批准 | 不成立 | 明确旧快照已批准、新候选待批准 |
| JIF 或历史 Q1 名单足以确定 JCR Q1 | 不成立 | 索取当年官方类别、排名和 quartile |
| 独立方法学复核已正式签结 | 证据不足 | 保留反馈已收到、闭环待完成状态，不伪造独立审稿人 |

额外发现：Figure 1a 底部三个 interpretation 节点在实际输出中挤压重叠。本轮将原词句重新分成三行，未改变节点含义。最终边界框最小间距为 **18.7749 pt**，高于本地至少 2 pt 的防重叠检查标准。

## 4. 具体文本与图件修改

主文源码只有三处声明过的替换：

1. 图注由 `minimum mapped-ARI criterion of 0.990` 改为 `minimum mapping-agreement criterion of 0.990`。
2. 由 `excluding dependence on a single source label` 改为 `arguing against dependence on any single contributing source label`。
3. 作者批准说明改为：前一快照已批准，当前纠错候选的最终批准待完成。

投稿信只有一处管理状态替换，区分旧快照批准与新候选、选刊、最终格式及提交授权。

主文 **854 个数字 token**、投稿信 **10 个数字 token** 的值和顺序完全不变。标题、摘要和章节顺序未改。Supplementary Information 和 RP 源码字节不变。

Figure 1 从现有绘图器重新生成，使用原冻结数据：

- Figure 1c 标签纠正，0.990 参考线、0.900 ARI 判据、数据点及科学判定不变。
- Figure 1a 仅改变三个底部节点的换行与间距。
- 最终 PDF/PNG 同时进入当前图件目录和候选包，不再仅作为未整合预览。
- 全部 15 份 figure source CSV 原字节保留；其他 14 张图的 PDF/PNG 共 28 个文件均字节不变。
- 图 1 的最初重绘和最终布局修复重绘分别留存审计记录；实际交付使用 `figure1_final_redraw` 的结果。

对应记录：[figure1_label_correction.json](jcr_q1_refreeze_2026-08-28/figure1_label_correction.json)、[纠错说明](jcr_q1_refreeze_2026-08-28/Figure_1_Legend_Correction.md)。

## 5. 冻结的科学结论没有改变

当前论文应继续围绕“状态划分不稳定与程序层面 IFN 信号可复现的区分”组织，而不是宣称获得普适 B 细胞亚型或完整外部映射验证。

- 发现集为 150,402 个 QC 后 B-lineage 细胞，259 位供者、271 个样本、88 个文库。
- R1 端到端重采样的 B_ASC median Jaccard 为 0.930323，未达到 0.95；仍为 HOLD。B_CONV/B_ASC 是分析框架，不是普适稳定分类学。
- 校正后的 C9R B_ASC precision 为 0.8852097130242825，未达到 0.90；仍为 HOLD，没有打开校正后的外部疾病结局。
- 旧 C9 PASS 已因归一化与授权逻辑问题失效，不用于支持正文结论；历史输出保留作审计。
- source-label 定义的儿童 GSE135779 IFN 复现保留，不等同于 source-label-independent robustness 成功。
- 主分析的 B_ASC 相对丰度为阴性；全基因组相关 rho=0.026 不支持整体转录组复现。
- STAT1/STAT2、M5911 和扰动情境证据仍受观察性、基因重叠与配体非唯一性限制，不能升级为直接结合或因果机制。

这些结论的限度是科学发现的一部分，不是通过调整阈值或改写 HOLD 可消除的排版问题。本轮未新增队列、调参、seed 搜索、TF 筛选或 outcome-informed rescue。

## 6. 文档重建与视觉复核

四份文档均从当前源码重新构建 DOCX，经 WPS 后台导出 PDF，再用 Poppler 110 dpi 渲染全部页面：

| 文档 | 页数 | PDF 字节数 |
| --- | ---: | ---: |
| Manuscript | 34 | 276,326 |
| Supplementary Information | 19 | 5,046,722 |
| Research Proposal | 6 | 164,299 |
| Cover Letter | 1 | 71,931 |
| 合计 | 60 | 不将不同文档合并解释为一篇主文 |

60 页均完成文本边界与未解析占位符检查，未检出越界或未解析标记。相对于前轮渲染，56 页 PNG 字节相同；本轮对另外 4 个变化页逐页进行了整页视觉检查：主文第 17、25、27 页以及投稿信第 1 页。未发现新增遮挡、截字或错页。最终 Figure 1 PNG 另外单独检查，底部框重叠已消除。

本轮并非对 56 个字节相同页面重新做一遍人工视觉审阅；继承前轮视觉证据并用图像哈希限定未变范围。实际渲染引擎是 WPS + Poppler，不声称 LibreOffice 双引擎复核，当前环境未找到 soffice。

全部 15 张当前 figure PDF 重新检查 170 mm 审阅宽度、字体和字号及画布边界，本地规则下没有 violations。此结果不等于任何目标子刊的最终 production 规格已经通过；尤其线宽和目标刊字号需定刊后分别核查。

主文当前仍是独立文本文件，五张主图另附；如目标刊要求或推荐图文合一审稿 PDF，应在定刊排版阶段生成，不能把当前 34 页主文称作已内嵌所有主图。

记录：[document_render_audit.json](jcr_q1_refreeze_2026-08-28/document_pages/document_render_audit.json)、[figure_typography.csv](jcr_q1_refreeze_2026-08-28/figure_typography.csv)。

## 7. 自动验证与可重复性

| 验证 | 本轮结果 | 范围说明 |
| --- | --- | --- |
| Review bundle / approval 单元测试 | 33/33 通过 | 覆盖旧批准与新候选状态、篡改拒绝及 prior snapshot 绑定 |
| WPS PDF 行号过滤回归测试 | 1/1 通过 | 仅过滤边栏行号，不删除正文数字 |
| 文档构建测试 | 3/3 通过 | 使用文档依赖环境 |
| C9 科学契约测试 | 9/9 通过 | 使用已有 sle-bcell 环境；不是重跑 C9 分析 |
| 单元测试总数 | 46 | 不把下面集成检查重复计入 |
| Figure 1 重绘断言 | 9/9 通过 | 当前图断言新跑；其他图断言明确继承 |
| 图文语义检查 | 13/13 通过 | 源码、DOCX、PDF、标签、批准状态和数字范围 |
| PowerShell 解析 | 33 个脚本，0 个错误 | audit_tools 下现有 ps1 |
| 新候选包验证 | 82 payloads 通过 | 外层清单、内层附件、来源与批准边界 |
| 换目录验证 | 通过 | 含空格路径、Python `-I -S`、无项目相对路径依赖 |
| 原已批准包验证 | 75 payloads 通过 | 使用其自己的 verifier，原包未变 |
| 确定性 ZIP 双构建 | 通过 | 同一候选输入的包字节一致 |

新验证器不把技术通过解释成作者批准。候选必须保留原 gate、原批准收据及被替换的四个旧 payload，并验证严格声明的文字差异。Figure 1 记录、语义报告与实际图文文件均绑定大小和 SHA256。

本轮未把所有文件做为新的全项目内容审计；大矩阵及无关工作目录未重新读取或删除。未发生数据下载、批量清理、计算环境安装或长时科学计算。

## 8. 交付物与完整性

当前本地交付：[corrected_candidate.zip](../04_submission/corrected_candidate.zip)。

| 包 | 字节数 | 内容与状态 |
| --- | ---: | --- |
| corrected_candidate.zip | 26,632,739 | 82 payloads，加外层清单共 83 ZIP entries；待候选批准 |
| author_confirmed_review.zip | 26,034,837 | 原 75 payloads；原字节及原批准不变 |

新候选 SHA256：

```text
D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150
```

原已批准包 SHA256：

```text
0363C066FB7F8FAD5E867FC820ED7F80C8F3D1A10E0A1CB43B8A7A51FCA92234
```

41 项科学范围对照中，37 项字节一致，仅主文源码、投稿信源码、Figure 1 PDF/PNG 四项变化。三份统计附件 ZIP 全部字节一致，内层清单分别为 Figure Source Data 15 行、Full Statistical Results 184 行、Regulator Sensitivity 10 行。四份 DOCX/PDF 因重建另行记录哈希，不混入上述 41 项口径。

旧 Figure 1 只作为 `governance/prior_snapshot/` 的批准历史留存，不能误作当前图。包已经创建后不允许原地覆盖；未来期刊定稿应另建明确的候选目录与包。

当前状态为 `PENDING_CORRECTED_CANDIDATE`，`submission_authorized=false`，`target_journal=null`，`matching_archive_doi=null`。本轮没有生成新的 DOI、release 或 tag，没有修改历史 v1.0.0，也没有登录投稿系统上传或付款。

## 9. 选刊和费用判断

完整证据及条件排序见 [Journal_Decision.md](jcr_q1_refreeze_2026-08-28/Journal_Decision.md)，结构化状态见 [journal_evidence.json](jcr_q1_refreeze_2026-08-28/journal_evidence.json)。

当前 **按内容匹配度有条件优先考虑 npj Systems Biology and Applications，Communications Biology 并列保留**。这是基于研究边界的编辑判断，不是已确认 Q1、承诺录用或确定的投稿目标。[npj scope](https://www.nature.com/npjsba/aims)、[Communications Biology scope](https://www.nature.com/commsbio/aims)。

实际打开 Clarivate JCR 后，npj 的公开结果显示 SCIE、MATHEMATICAL & COMPUTATIONAL BIOLOGY、最新 JCR 数据年 2025；公开表没有可核验的 rank/quartile，且没有证明类别列表完整。JCR 2026 发布年与数据年 2025 应分别记录。Communications Biology 的完整 JCR 档案尚未取得。[JCR 入口](https://access.clarivate.com/jcr/)。

已请作者从学校 JCR 入口导出两刊的官方档案 PDF，保留年份、全部类别、排名及 quartile。没有索取账号密码，也没有代为接受登录相关隐私或跨境同意。

预算必须单独确认。当前 original research APC 分别为 npj GBP 2,690 / USD 3,490 / EUR 2,990、Communications Biology GBP 3,250 / USD 4,390 / EUR 3,650；税费可能另计，按接受日定价。无 funding 不代表自动豁免或同意自费，学校协议覆盖尚未核实。[npj APC](https://www.nature.com/npjsba/apc)、[Communications Biology APC](https://www.nature.com/commsbio/open-access)。

## 10. 输入行动矩阵逐项处置

| ID | 本轮状态 | 剩余动作或解释 |
| --- | --- | --- |
| JCR-01 | 部分完成 | 已取官方部分元数据；等待当前年份所有类别及 rank/quartile |
| JCR-02 | 待决 | Q1 证据与费用可行性明确后选一个目标 |
| FIG1-01 | 完成 | 纠错图已进入当前候选；数据不变 |
| FIG1-02 | 完成 | 主文图注及 DOCX/PDF 同步 |
| FMT-01 | 待选刊 | 不提前反复改标题、摘要、章节 |
| TEXT-01 | 完成 | contributing source label 表述已收敛 |
| AI-01 | 现有内容满足 | Methods 小节本来存在，本轮验证而非重复添加 |
| FIG-ALL | 当前规格检查完成 | 目标刊规格待定，附件统一字号要求不盲目套用 |
| EXT-01 | 可选增强待完成 | 可接收真实独立方法学签结，不能由同一分析代理自证独立 |
| DOC-01 | 当前候选完成 | 目标刊格式及 DOI 改动后仍需一次最终重建 |
| REL-01 | 本轮源码同步 | 不是期刊最终 release 冻结；见单独 Git 回执 |
| REL-02 | 未执行 | 等待最终来源与明确的新归档发布授权 |
| REL-03 | 未执行 | 没有新 DOI，不能插入虚构或不匹配 DOI |
| AUTHOR-01 | 旧批准保留，新候选待批准 | 最终选刊和 DOI 绑定文件明确后一次核对 |
| SUBMIT-01 | 未执行 | 未获得 exact-file 提交授权，不进入投稿门户 |
| SCIENCE | 遵守 | 未开展探索性 rescue 或改变冻结阈值 |

额外已完成项：Figure 1a interpretation 节点间距修复及对应回归断言。

## 11. 执行中发现的问题及修复

- 初次语义检查被 WPS 边栏行号切断的句子误报。修复提取逻辑为按页面坐标忽略边栏纯数字，不删除正文数字，新增回归测试后通过；未手改 PDF。
- 文档专用 Python 不含 scipy，首次科学契约测试因此未启动成功；切换现有 sle-bcell 环境后 9 项通过，没有临时改环境或跳过测试。
- 一次调用了不存在的文档构建脚本名，核对现有脚本后改用 `phase17_postc9_03_build_review_documents.py`，随后完成构建。
- 初次 Figure 1 重绘暴露 panel a 旧布局问题，回到源码换行修复后重新绘图并检查，再构建最终包。
- Nature 网页有 cookie 重定向错误，改用能正常读取的官方页面核验；没有用第三方排名猜测填补 JCR 缺口。
- JCR 未认证访问只得到部分元数据，记录为未闭合项，没有把登录失败解释成该刊不是 Q1。

## 12. GitHub 同步与下一阶段

本轮提交只包含当前源码、相应 figure/source manifest、验证脚本及必要审计记录。大矩阵、候选 ZIP、DOCX/PDF 文档渲染、页面 PNG 和便携性临时解包目录继续留在本地并受 ignore 规则管理。保留旧批准与原包，不做破坏性清理。

源码提交 **`05e41f40284fc65c6cd18bbecaa2bf507e81b5f8`** 已推送到 GitHub，随后通过 `git ls-remote` 确认远端 `main` 为同一提交。75 条 package source provenance 全部与本地文件一致，其中 66 条对应已提交 Git blob；另外 9 条是受 ignore 管理的 8 份 DOCX/PDF 和原 Regulator Sensitivity ZIP。45 条图件/源数据 manifest 也逐项与提交字节核对，去重后共验证 81 个 Git-bound payload，全部一致。

完整回执见 [git_sync_receipt.json](jcr_q1_refreeze_2026-08-28/git_sync_receipt.json)。回执和本段同步说明在源码提交之后另行作为文档提交，避免把提交哈希写进自身而造成循环。此次只是 GitHub 源码同步，不是新期刊 release 或 DOI 发布。

下一阶段依次为：

1. 取得 JCR 官方导出，确认数据年、全部类别、排名及 JIF Q1；不满足条件的候选退出本次 Q1 路径。
2. 确定一个目标期刊并解决 APC 预算或减免申请可行性，不替作者承诺付款。
3. 一次完成该刊标题、摘要、章节、图文组合、线宽字号和 checklist 的源文件格式调整，保持科学边界及全部 HOLD 不变。
4. 重建全部目标期刊文档与必要图件，完成语义、图文、源数据、哈希、便携性和门户前检查。
5. 明确授权后制作与实际最终来源相匹配的新归档版本和 DOI；保留历史记录，插入 DOI 后再次重建验证。
6. 两位作者对期刊、DOI 和 exact-file 哈希进行最终批准，并明确授权投稿；之后才进入门户 PDF 审查与提交。

当前优先级是 **完成官方选刊证据和一次期刊化定稿**，不是重新开展大规模计算，也不是继续增加没有新证据支撑的机制叙事。技术闭环已经取得实质进展，但论文新颖性、方法学限制、Q1 资格与作者对外授权仍分别判断。
