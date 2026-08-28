# 外部意见响应、当前作者授权分离与审阅包更新行动记录

日期：2026-08-28。工作路径：`H:\cuhk-2025fALL\6013RP-wyf`。
起始 Git 提交：`f28cf6a481232408710862eee5ee2db735dec70b`；开始时工作区干净。

## 1. 本轮结论

**本轮完成了外部意见中可以由本代理执行的文字修正、授权文件治理和审阅包更新。**
未发现需要据本次意见重新打开疾病计算的已确认新缺陷。当前科学结论及两个
HOLD 不变；外部方法审阅的正式结论和两位作者对当前文件的批准仍没有代签。

当前包改为 `04_submission/author_review.zip`。上一轮 `correction_review.zip`
和更早的 `journal_submission` 保持原样，分别是历史审阅快照和历史投稿快照。
新旧包不能混用；当前确认表只针对最新审阅材料，不继承旧版勾选。

## 2. 本轮收到的材料与证据边界

读取了用户给出的独立审计 MD、行动矩阵 CSV 和粘贴意见 TXT，原字节复制到
`00_project_management/external_review_2026-08-28/received/`。三份文件的哈希为：

| 文件 | 字节 | SHA-256 |
|---|---:|---|
| independent_audit.md | 19,738 | 6EBF66BEE91FDDE64128D31447FF9957C932BE24E0C0EA8FFB7CC1F1CD59AFB5 |
| action_matrix.csv | 2,902 | 5A64213FAF327A3DBC7102BD2A64EA8CB7353C073DAFB331EC1C680EB169B478 |
| pasted_review.txt | 21,656 | 54C58FFF84CFF1140F6780AEC250C7892C75958B5F09ACE56072B08A78E24D55 |

外部意见被当作需要核对的审查材料，不是可自动执行的发布命令。意见确实
针对上一轮具体 commit 和 ZIP，并提出了可核实问题；本轮已据此响应。
但没有认证其审阅者身份、专业资格、与原分析的独立性及实际执行环境，
因此将状态记为 `FEEDBACK_RECEIVED_CLOSURE_PENDING`，而非“未收到任何意见”，
也不是“独立方法审查已经全部完成”。

本轮没有另行验算外部意见声称检查的 `6013RP-wyf(1).zip` 全部内容；
自己的完整性结论限于本地明确读取的冻结来源、旧/新审阅包和本轮生成物。
没有采用附件中 98%/99% 的完成度评分，因为这些百分比没有可重现的分母或评分标准。

## 3. 十五项行动矩阵逐项响应

| ID | 本轮状态 | 处置与边界 |
|---|---|---|
| GOV-01 | 完成 | 旧作者确认逐字节归档；稳定入口 Author_Confirmation.md 改为全新待确认记录 |
| GOV-02 | 完成 | 旧 reporting checklist 归档；当前清单只含当前事实，明确 42 数据/科学检查 + 5 字体检查 = 47 |
| EXT-01 | 准备完成，外部结论待补 | 新建 12 问方法审阅 dossier 和机器状态，不虚构审稿人或结论 |
| EXT-02 | 完成接收归档与响应 | 三份来稿及拷贝哈希保存，本表记录具体处置；不把一般赞许当复现凭证 |
| TEXT-01 | 完成 | Methods 从“selected thresholds”改为按预设资格规则“evaluated ... candidate confidence thresholds” |
| TEXT-02 | 完成 | Discussion 明确纠正归一化后 B_ASC 参考校准失败，故未估计纠错疾病结局 |
| FIG-S10 | 本轮不实施，可选项保留 | 现图准确表达门槛失败，未被指出决定性缺陷；不为增加变化而替换 panel d |
| AUTHOR-01 | 待作者 | 当前所有内容批准、独家投稿和最终上传授权框均未勾选 |
| JOURNAL-01 | 评估完成，未选定 | 核查三刊官网，记录适配、格式差距及分区未核实状态 |
| PACKAGE-01 | 待选刊 | 无指定期刊，不按猜测的精确图宽重画；本轮仅重建作者审阅包 |
| RELEASE-01 | 未执行 | 没有新 tag、没有移动旧 tag；代码同步不等于 release |
| RELEASE-02 | 未执行 | 没有新 Zenodo 版本或 DOI；旧 DOI 仍限定为初始快照 |
| QA-01 | 本轮审阅包完成，最终投稿包待定 | 当前 WPS/可访问性/manifest/确定性核验通过；选刊与 DOI 回填后需重新验收最终文件 |
| SUBMIT-01 | 未执行 | 所有 11 个上传角色仍为 DRAFT_NOT_FOR_UPLOAD，无投稿号或回执 |
| SCIENCE | 遵守本轮边界 | 未改变阈值、算法、seed、特征、队列、TF、基因集或原疾病统计 |

保留 `Author_Confirmation.md` 稳定文件名，而非增加两个容易混淆的当前入口。
其历史副本移入管理记录目录，不向期刊文件名引入版本号；归档不是删除历史。

## 4. 主文和科学数据的守恒

主文只修改两处：参考校准 Methods 的阈值措辞，以及 Discussion 的校准 HOLD 说明。
没有变动摘要、标题、样本数、效应值、CI、P/q、参考文献和图注。
补充材料、RP 和投稿信 Markdown 本轮没有改动；RP 已在前轮正确保留相关边界。

新增核验入口 `audit_tools/phase17_postc9_07_verify_author_review.py`，对上一轮
完整 ZIP 和当前 ZIP 作逐项比较，而不是仅凭 Git 差异宣称“没有改结果”：

- 当前主文恰好等于旧主文执行约定的两处字符串修改，没有额外改动。
- 主文 **854 个数字 token 的顺序完全不变**。这是一项防漂移检查，不代替统计复核。
- **40 项包内有效载荷逐字节不变**：30 份 PDF/PNG 图件、3 个统计 ZIP、
  3 份未修改的 Markdown 源及 4 份科学代码。
- 三个统计 ZIP 本身未变，因此内部 15/184/10 项 payload 及其科学来源不变。
- 完整统计附件保留 163 个历史 payload 和 20 个纠错校准文件，另有 1 份范围说明。
- 本地 C9R 的 16 项冻结有效载荷和 45 项图件/图源清单再次通过大小与 SHA-256 检查。
- 先归档后改写的两份历史授权文件、三份来稿、两份继承的算术复核文件，7/7 校验通过。

当前参考校准仍是 B_ASC precision 0.885210 < 0.90，C9R 疾病结局没有解锁。
R1 B_ASC median Jaccard 0.930323 < 0.95 的 HOLD 不变。
这些数值来自此前冻结结果，本轮没有重拟合模型来“再证明”它们。

## 5. 作者与外部审阅记录的重建

`04_submission/Author_Confirmation.md` 保留作者身份、邮箱、ORCID、单位，以及
作者此前提供的伦理、利益冲突、经费、致谢等事实来源，但不用勾选形式将其伪装
为当前材料的再次批准。当前正文、补充、S10、附件、投稿信、纠错说明、AI 披露、
原创性和一稿专投，均需要新的明确确认。

两位作者的 decision 均为 PENDING，date 和 evidence 均未记录。
确认时应提供当前包 SHA-256；后续实质改稿、DOI 回填和期刊格式变化需与最终
授权文件保持一致。没有代填签名、日期、批准或投稿结果。

外部方法 dossier 包含 12 个可检查问题：公式、全库计数对齐、候选算术、
state-specific 门槛、fallback、结局保护、56 矩阵完整性、供体分组、
非嵌套 CV 限制、禁止 centroid rescue、旧 C9 撤回和文稿/代码一致性。
问题附带具体函数、输出或回归测试入口，不要求审阅者先重跑全部细胞。
其结论仍由真实审阅者填写，不能由本代理的自检替代。

新验包规则要求上述表单、当前清单、dossier 和 `review_gate.json` 四项齐备，
并拒绝旧勾选表、伪造的作者通过状态、把收到反馈升级成外部方法批准、或
擅自声明已选期刊/新 DOI/可投稿。新规则是本次 review-only 包的守卫，
不是今后实际批准之后仍不可调整的永久门槛；届时须先有真实授权证据。

## 6. WPS 和版面复核

四份 DOCX 从当前 Markdown 重建，继续使用既有版式；WPS 后台输出新 PDF，
Poppler 按页渲染。总页数仍为：主文 34、补充材料 19、RP 6、投稿信 1，共 **60 页**。

逐页图像比较得到 **33 页与上一轮 PNG 文件完全相同**。其余 **27 页，即主文
第 8-34 页**，因新增文字及行号/分页移动而发生变化；本轮逐页打开这些原尺寸图像，
检查边界、标题与正文、声明、图注和参考文献衔接，没有发现需要修复的遮挡或裁切。
第 8 页可见新 Methods 措辞，第 23 页可见新的 Discussion 限制句。
这不是重新逐句独立审查全部参考文献的声明。

自动结果：60 页均无画布外文本和未解析标记；四份 DOCX 可访问性审计均为
高/中/低问题计数 0。构建记录绑定四份 Markdown 与四份 DOCX 的哈希，
渲染记录绑定四份 DOCX 和四份 PDF，避免修改正文后沿用旧 PDF 验收。

运行中如实记录的限制：

- `render_docx.py` 因本机缺少 LibreOffice/soffice 不能完成其转换链；
  沿用用户指定的 WPS 后台流程，未声称完成双渲染器验证。
- bundled Python 没有 PyMuPDF，PDF 检查脚本首次报告缺少 fitz。
  DOCX 仍使用 bundled Python；PDF 页面核验改用本机已配置的
  `D:\bioinfor\python.exe` 和 Poppler，成功完成。
- 第一份批量文字补丁因同一文件重复操作被 apply_patch 拒绝，没有部分写入；
  改为读取原文后生成精确替换补丁，后续差异核验确认仅两处主文修改。

## 7. 新审阅包与测试

当前包：`04_submission/author_review.zip`。

| 项目 | 实测结果 |
|---|---:|
| ZIP 大小 | 26,022,917 字节 |
| ZIP 条目 | 73，含外层清单 |
| 外层 payload | 72 |
| 新增 governance 文件 | 4 |
| Figure Source Data / Full Statistics / Regulator ZIP 清单 | 15 / 184 / 10 |
| 作者批准 | PENDING |
| 外部方法审阅 | FEEDBACK_RECEIVED_CLOSURE_PENDING |
| 投稿授权 | false |

SHA-256：

```text
EA046B266681940AD551851354726907B8ABD14E948DCD28025100061283791F
```

从 `C:\Users\Administrator` 使用构建脚本的绝对路径运行成功，确认入口不依赖
调用者先切换工作目录。构建只向新的 `author_review` 目录写入，不覆盖历史包。
固定相同输入字节的两次 ZIP 构建完全一致。

新 ZIP 展开到带空格的另一目录后，运行自带 `python -I -S` 验证器通过，
不依赖原始数据目录或第三方 Python 包。当前 ZIP 与其展开目录逐字节对应。
旧包也用自己的原版验证器再验一次，仍通过；新 schema 不倒改旧包。
该测试是便携完整性验证，不是干净机器重跑整篇论文的科学计算。

| 测试 | 结果 |
|---|---|
| 科学校准/结局门控回归 | 9/9 |
| 文档生成回归 | 3/3 |
| 审阅包与授权保护回归 | 11/11，其中本轮新增 4 项 |
| 合计 | 23/23 |
| PowerShell 递归语法检查 | 37 文件，0 错误 |
| 新旧包边界与守恒核验 | PASS |
| Git 差异空白检查 | PASS |

## 8. 选刊判断及对外部建议的修正

本轮直接查阅候选期刊官网，而非照抄附件的期刊排序和格式断言。
详细依据在 `external_review_2026-08-28/Journal_Fit_and_Format_Assessment.md`。

按当前概念匹配度，优先评估 npj Systems Biology and Applications，
Communications Biology 为另一重点候选；Genome Medicine 是较高风险路线。
这一排序是本代理根据稿件与官方范围作出的推断，不能保证送审、接收或 Q1。
机构认可的 JCR/CAS 年份和类别尚未核实，不能拿品牌或 SJR 代替。

两个会影响下一阶段的具体发现：

1. 两个 Nature Portfolio 候选的 Article/接收稿指导均指向约 150 词摘要，
   因而不能把附件建议的 320-330 词作为最终目标。两刊又均允许初投不完全遵循
   最终格式，不能把这说成所有初投的硬性阻断。
2. Communications Biology 的图件指南提出最终大小以 8 pt 字体为佳、最细线
   不小于 1 pt，说明当前项目的 Nature-style 5-7 pt 方案不是全品牌统一规范。
   无指定期刊时不机械重画全部图；选刊后按实际要求从代码重渲染。

依据：[npj Article 类型](https://www.nature.com/npjsba/content-types)、
[npj 作者指南](https://www.nature.com/npjsba/for-authors-and-referees)、
[Communications Biology 投稿指南](https://www.nature.com/commsbio/submit/submission-guidelines)、
[接收稿格式指南](https://www.nature.com/documents/commsj-life-style-formatting-guide-accept.pdf)。

没有为了适配尚未选择的期刊提前改短标题、摘要、补充材料文件角色或图件尺寸。
没有依据专题截止日期跳过审查；没有承诺机构 APC 减免。

## 9. Git、归档与公开范围

外部来稿、旧授权文件和继承的校准复核记录采用明确字节保留规则，避免 Git
换行转换破坏归档哈希。当前文档构建和精简渲染核验 JSON 保留进 Git，
逐页 PNG、WPS 二进制文档、ZIP、测试展开目录及原始矩阵不进入新提交。

暂存区的 79 项字节核验通过：62 项既有图件/数据源/校准输出/科学代码、
7 项来稿及历史记录，以及 10 项审阅包对应的正文源、治理文件和验证器。
Git 暂存差异检查发现来稿 Markdown 原有的行末双空格；这些空格属于来稿，
本轮没有改动，仅在 `received/` 归档目录豁免空白规则，保持其已记录哈希。

同步状态在本轮收尾核实后补充；不得以准备提交代替已同步的事实。
无论代码同步是否成功，本轮均不创建 release、tag、Zenodo 新版本或投稿。

## 10. 下一阶段目标

**先关闭真实审查与作者决策，再做期刊特定重排和对应归档。**

1. 审阅者基于 12 问 dossier 给出具体结论，声明身份、独立性、所看输入和
   实际执行的核验；未检查项不得默认为通过。
2. Zhi Chen 与 Teng Qi 明确确认当前作者审阅包中的科学内容和纠错边界。
   当前可先批准科学内容；选刊、APC、最终文件及上传授权另行明确。
3. 通过机构认可的分区凭证确定期刊，再制作短标题、约 150 词非结构式摘要、
   Code availability 与相应补充 PDF/图件格式，全部由源码重建。
4. 对最终新版本预留并回填 DOI，验证最终内容、commit、归档与文件哈希一致后
   再发布；旧 DOI 和旧 tag 保持不变。
5. 经最终作者授权后才做门户预检与实际提交，记录真实回执与稿件编号。

本轮无需用户再下载大文件或进行耗时计算。若外部审阅发现新的决定性代码缺陷，
应先记录具体问题及纠错范围再重跑；不能为追求 PASS 放松门槛或挑选结果。

## 11. 交付物

- 本报告：`00_project_management/action_record_2026-08-28_external_review_author_gate.md`。
- 当前审阅包：`04_submission/author_review.zip` 及同名展开目录。
- 当前作者确认：`04_submission/Author_Confirmation.md`。
- 当前 reporting checklist：`04_submission/Reporting_Checklist.md`。
- 外部方法 dossier 与机器门控：`external_review_2026-08-28/External_Methods_Review.md`、`review_gate.json`。
- 选刊依据：同目录 `Journal_Fit_and_Format_Assessment.md`。
- 原件/历史保留校验：同目录 `received_and_history_manifest.json`。
- 包构建回执、守恒核查与换目录测试：同目录 `correction_package_build.json`、
  `post_edit_consistency.json`、`portable_verification.json`。
- WPS 文档哈希：同目录 `document_pages/document_render_audit.json`。

当前材料更容易核查，但仍不等于外部方法结论已认证、作者已经再次批准或期刊已接收。
