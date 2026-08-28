# 2026-08-29 行动记录：纠错候选复核与 JCR Q1 定刊准备

## 1. 本轮结论

本轮承接 2026-08-28 的新审计与中断后的继续指令，于 2026-08-29 完成记录。起点 Git 为 `74678c7cf75e376d90cdae886b6a1a4cf1951714`。

**决定：保留当前 corrected candidate，不重开探索性计算，不重画 Figure 1，本轮也不改 S10。** 未发现需要改变科学结论或重跑分析的新证据。候选包和其 75 条源文件来源均复核未变。

本轮实质推进包括：找到港中深图书馆的正式 JCR 机构入口；核实两刊首投格式可灵活处理；厘清学校 APC 资格不能从香港校区直接继承；完成可直接使用的图书馆咨询草稿；核对短标题/摘要储备；完善 DOI 预留、最终文件批准和公开归档的顺序。

**尚未完成：官方 JCR rank/quartile、目标刊确定、APC 可行性确认、目标刊最终文件、对应新 DOI 和投稿授权。** 这些缺口没有用主观完成度百分比或技术 PASS 代替。

## 2. 输入材料与授权边界

本轮读取并按原字节保存了三份输入，原文均在 [received](jcr_q1_target_preparation_2026-08-29/received/)：

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| SLE_Bcell_corrected_candidate_independent_full_audit_2026-08-28.md | 10,300 | `550CA5904C2A812CB2554B159B2D1BBD1546F50FDD9666A1F9F72013D70E679C` |
| SLE_Bcell_JCRQ1_target_freeze_matrix_2026-08-28.csv | 2,175 | `3EDB13126134DE6952982B5B3283C55990100390111EAC978F816701A54CB51A` |
| pasted-text.txt | 19,534 | `3E7063154FABC8FAB603A6A59A82F98C0D9128E3463DEA00752E8BC590622AD1` |

附件自称独立审计，但没有提供可核验的独立评审者身份，本轮不将其升级为具名方法学签结。附件中的发布、收费、投稿步骤是建议，不是新增授权。两位作者对先前快照的批准仍有效，但不会自动延伸到未来改动后的文件。

## 3. 当前包与源文件核验

执行只读检查脚本 [phase17_postc9_13_audit_target_preparation.py](../audit_tools/phase17_postc9_13_audit_target_preparation.py)，产生 [candidate_no_drift_audit.json](jcr_q1_target_preparation_2026-08-29/candidate_no_drift_audit.json)。该脚本只写项目管理下的 JSON 回执，不生成或覆盖稿件、图件或 ZIP。

| 检查 | 本轮结果 |
| --- | --- |
| corrected_candidate.zip 大小 | 26,632,739 bytes |
| ZIP SHA256 | `D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150` |
| 外层 payload 校验 | 82/82 通过，含外层 manifest 共 83 entries |
| 展开目录与 ZIP | 逐项内容相同 |
| SOURCE_PROVENANCE | 75/75 当前源文件大小和 SHA256 相同 |
| 三份附件内部清单 | 15、184、10 行，技术校验通过 |
| 候选状态 | `PENDING_CORRECTED_CANDIDATE` |
| 目标期刊 / 对应新 DOI | 均未确定 |
| 投稿授权 | false |

由于包 SHA256 未变，包内 15 份图源数据、15 张图、四份 DOCX/PDF 和三份统计附件均保留原字节。主文、补充材料、RP、投稿信源码也由 source provenance 逐项确认未变。本轮没有再生成一个同内容的新 ZIP。

此前 60 页 WPS、图件字体和语义检查的证据继续适用，**不是本轮重新渲染或逐页新审阅的结果**。本轮没有宣称重跑全部数值分析、全量清理工作路径或重新检查大矩阵。

## 4. 科学边界与 S10 判断

读取了现有冻结的 calibration CSV、C9R decision JSON 和原完整性清单；两个文件的大小与哈希均相符。重新核对的只是现有表的布尔判据，未重新训练 mapper 或估计任何 disease effect。

| Mapper | 冻结候选数 | Eligible 数 | 选中 coverage | 选中 B_CONV precision | 选中 B_ASC precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| elastic_net | 26 | 0 | 0.941958 | 0.996450 | 0.885210 |
| nearest_centroid | 46 | 16 | 0.950000 | 0.992374 | 1.000000 |

elastic-net 的 selected 行是 diagnostic fallback，不是有效校准成功。主 mapper 的失败不能由辅助 centroid 的成功替代，C9R 仍为 `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`，`outcome_unlock_authorized=false`。

审计建议的 coverage-vs-B_ASC-precision frontier 可以帮助解释，但两个坐标轴并不包含全部判据：B_CONV precision 同样须 >=0.90，主 mapper 与辅助 mapper 的角色也不同。若将右上象限直接标为完整 gate 的 eligible region，会产生新的误解。

当前 S10 已展示 state-specific precision、coverage 和 donor-grouped accuracy，解释功能足够。因此本轮不进行 P1 可选重绘。若之后确有审稿需求，必须从当前冻结表重绘、注明额外条件、区分两种 mapper，不改变 grid、threshold、seed、features 或 outcome。

R1 HOLD、B_ASC composition null、source-label-defined IFN 复现、低全基因组相关及观察性 regulator 证据继续保持。不能把正式 HOLD 改称成功的 source-label-independent validation。

## 5. 字数与写作准备

本轮对源码按固定口径重新计数：以空格分词，排除 Markdown 标题和结构式摘要段首标签，连字符词计为一个 token。该计数用于比较准备工作，不替代目标刊门户的词数计算。

| 项目 | 当前计数 |
| --- | ---: |
| 主标题 | 16 |
| Abstract 正文 | 309 |
| Background 正文 | 425 |
| Methods 正文 | 1,981 |
| Results 正文 | 1,849 |
| Discussion 正文 | 891 |
| 已有短标题草案 | 13 |
| 已有摘要草案 | 117 |

输入审计的摘要约 337 词和部分节字数与此口径不同，不据此推断文件漂移；文件哈希已经证明源码未变。应在定稿时统一统计方法，而不是沿用不同工具的数值作为硬证据。

[原有短标题/摘要草案](author_confirmation_2026-08-28/Journal_Format_Draft.md)已经覆盖重要科学限制，包括源标签定义的外部复现与校正后 mapper 校准失败。无需另起一套相似草案；目标刊确认后对该草案一次精修并应用。目前仍未插入主文。

## 6. 首投要求与最终出版规格分开

本轮重新读了两刊官方指南。npj Systems Biology and Applications 和 Communications Biology 都允许初次投稿使用灵活格式，不应把最终 production 规范全部写成首投硬门槛。[npj 指南](https://www.nature.com/npjsba/for-authors-and-referees)、[Communications Biology 指南](https://www.nature.com/commsbio/submit/submission-guidelines)。

因此后续只进行必要的、一次性的期刊化整理：短标题、非结构式摘要、章节与声明的位置、实际要求的图文组合和文件命名。字体、线宽、最终尺寸按所选刊及投稿阶段核对，需要改变时从源码重绘，不机械地把全部图重做一遍。

Communications Biology 所链接的接受阶段 style guide 还要求 Methods 有 Statistics and Reproducibility 小节。若选择该刊，应整合已有统计设计、样本和重复定义到相应小节，而不是添加未经实施的实验。此项属于已识别的格式准备，不是当前科学方法缺失或首投自动被拒的证据。[官方 style guide](https://www.nature.com/documents/commsj-life-style-formatting-guide-accept.pdf)。

当前 Methods 中的 AI 使用披露继续保留，不再重复新增。文件名及面向读者内容保持清洁；内部审计状态、旧稿和批准历史不伪装为期刊正文。

## 7. JCR 与学校出版费用核查

新增实用路径：

- [港中深图书馆 JCR 指南](https://cuhk-shenzhen.libguides.com/c.php?g=964056)
- [该指南实际链接的机构入口](https://idp.cuhk.edu.cn/bridge/jcr)
- [校外访问说明](https://library.cuhk.edu.cn/off-campus)

机构入口实际打开后，仍只取得 npj 的公开元数据：SCIE、MATHEMATICAL & COMPUTATIONAL BIOLOGY、最新 JCR 数据年 2025。没有拿到完整排名、分母、quartile 或全部类别的官方导出。因此继续记录 **JCR Q1 未核实**，不把“找到入口”当作“取得资格证明”。

学校图书馆说明其服务涉及 JCR 指标核验；本轮使用其指南页脚一致显示的通用联系地址 `library@cuhk.edu.cn` 准备咨询。页面中 subject-librarian 可见邮件文字与 mailto 目标不一致，所以没有猜测具体馆员邮箱或发送邮件。[学校服务说明](https://library.cuhk.edu.cn/zh-hans/research-output-certificates)。

APC 方面，公开的香港协议表列有 CUHK，但不能据此认定深圳校区适用。还尝试了 npj 的机构查询控件，没有得到可用覆盖结果；这不是“确定没有资助”的证据。学校真实单位、学生通讯作者资格、两刊是否覆盖、有效期和额度仍需书面确认。[npj 资助查询](https://www.nature.com/npjsba/open-access-funding)。

已准备 [Institutional_Request_Draft.md](jcr_q1_target_preparation_2026-08-29/Institutional_Request_Draft.md)，一次咨询两刊 JCR 档案与 APC 资格。未发送、未申请付费服务、未承诺自费。申请减免也不等于获得减免，提交界面勾选后可能还须完成独立申请流程。[出版社减免说明](https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers)。

## 8. 输入行动矩阵处置

| ID | 本轮处置 |
| --- | --- |
| JCR-01 | 找到并测试学校入口，完整官方分区证据待取得 |
| JCR-02 | 保留 npj 为内容匹配度条件首选，尚未定刊 |
| COST-01 | 核实资格风险，准备学校咨询；费用未授权 |
| FMT-01 | 已有短标题/摘要可用，定刊后应用 |
| FIG-01 | 按实际投稿阶段要求决定，不把全部重绘设为通用硬门槛 |
| FIG-S10 | 本轮决定保留；可选 frontier 须注明完整条件 |
| QA-01 | 本轮包和源文件无漂移核验完成；未变化文档不重复渲染 |
| REL-01 | 当前源码仍对应原候选；真正的期刊最终冻结待定 |
| REL-02 | 未执行；新版本归档和公开操作需明确授权 |
| REL-03 | 未执行；先预留再写入最终文件的顺序已说明 |
| AUTHOR-01 | 旧批准保留，未来 exact-file 批准待目标和 DOI 明确后进行 |
| SUBMIT-01 | 未执行；未授权上传或提交 |
| SCIENCE | 遵守冻结，不做 exploratory rescue |

本轮不采用附件中的 96%-100%“完成度”评分。科学可信度、技术完整性、选刊资格和作者授权不是同一条可以相加的百分比进度。

## 9. 代码、测试与变更范围

新增一个只读核验脚本及六个小型测试，覆盖 section 边界、分词、缺失节、非有限指标、B_CONV 条件和 mapper 角色分离。未修改原有绘图器、分析器、packager、verifier 或主文源码。

运行 `test_review_bundle` 和 `test_target_preparation`，**39 项测试通过**，即 33 项既有包/批准边界测试加 6 项新增测试。没有把上一轮 46 项测试或 60 页渲染当作本轮新执行数量。集成审计再次核验 82 payloads 与 75 条 source provenance。

新增材料包括本报告、[定刊准备说明](jcr_q1_target_preparation_2026-08-29/Target_Preparation.md)、[结构化待办状态](jcr_q1_target_preparation_2026-08-29/target_readiness.json)、只读审计 JSON 和原始附件。README 只添加新入口；.gitattributes 保留新审计附件的原始字节。不修改仍被候选包哈希绑定的 REPRODUCIBILITY 或批准记录。

执行过程中的浏览器问题均限定处理：部分官方网页在网页读取工具中超时，改用实际浏览器读取学校指南；机构查询控件没有返回有效结果，未推断资助资格；中断后旧浏览器标签被清理，没有重复使用失效页面继续作出判断。本轮未索取密码或读取浏览器凭据。

## 10. 下一阶段与同步

完整顺序见 [Target_Preparation.md](jcr_q1_target_preparation_2026-08-29/Target_Preparation.md)：

1. 作者通过学校入口或图书馆取得两刊官方 JCR 档案，同时确认 APC 覆盖或可接受预算。
2. 按已核实的 Q1 资格、内容匹配度与费用可行性选定一个目标。
3. 对已有稿件做一次必要的期刊化整理，保持科学结果、HOLD 和因果限制不变。
4. 在明确授权后检查现有归档草稿及自动化，预留新版本 DOI；把 DOI 写入预期最终文件再重建，不先公开一个随后必须换文件的归档。
5. 确认最终 source commit 与文件哈希，获得两位作者的 exact-file 批准及归档发布授权，发布相匹配的归档并核验 DOI。
6. 独立确认投稿授权后才进入门户，检查系统 PDF 并保存正式回执。

Zenodo 官方支持预留 DOI 和创建链接到原记录的新版本草稿。本轮只明确顺序，没有创建草稿、预留 DOI、发布 release、移动 tag 或提交稿件。[DOI 预留](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)、[版本管理](https://help.zenodo.org/docs/deposit/manage-versions/)。

本轮 GitHub 同步将单独保存 [git_sync_receipt.json](jcr_q1_target_preparation_2026-08-29/git_sync_receipt.json)，以实际远端核验为准。源码/报告同步不构成公开新归档或授权期刊提交。

**下一阶段最需要的是外部证据与选刊决定，不是再增加分析或制造新版本。** 若输入仍只是重复肯定当前候选的审计意见，保留冻结状态；取得 JCR/费用信息后即可推进一次性定稿，避免无依据的反复改图、重建和重新批准。
