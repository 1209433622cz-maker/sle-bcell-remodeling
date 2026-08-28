# 2026-08-29 行动记录：QiTeng 精修主文的证据边界核查与最小修订

## 1. 本轮结论

**决定：接受来稿的逻辑重构方向，完成窄范围的高风险文本核查，生成独立的待作者确认稿；不重开生信分析，不改冻结图件，不生成投稿包。**

按生信方法学审稿视角核查了全部 169 段正文、声明、五幅主图图注和 32 条参考文献，并将主要结果及其归属回查到现有图源数据。发现的问题集中在结论强度和证据归属，而不是新的数值计算错误。没有将附件自报的完成度、质量评分或“独立审计”身份视作已经验证的事实。

本轮在收到的精修 DOCX 上实施了 **20 处局部替换，涉及 17/169 段**，并修复页眉/页脚的重复边注行号。没有改动统计估计、参考文献身份、参考文献正文或五幅主图图注。最终 WPS PDF 与备用 LibreOffice 渲染均为 **18 页，18/18 页逐页视觉检查完成**。

最终状态为 `TEXT_AUDIT_COMPLETE_EXACT_AUTHOR_SIGNOFF_PENDING`，不是 `SUBMISSION_READY`。正式计算与源标签无关映射的 HOLD 仍然保留。下一阶段是作者对本套精修文件的内容确认及官方 JCR Q1 定刊，不是再次追加计算。

## 2. 输入、基线与范围

起点本地 Git 为 `8fa5262e001197d70b082a318406d67628fbadfb`，工作区起始干净。GitHub 仓库为 `1209433622cz-maker/sle-bcell-remodeling`。本轮开始时的 scientific corrected-candidate 源码提交仍为 `05e41f40284fc65c6cd18bbecaa2bf507e81b5f8`。

用户提供的行动记录基于更早的 Git `74678c7`。其后到本轮起点的变化没有改变被候选包绑定的科学主文，不能仅凭提交号不同断言输入过时。

收到的三份成品已按原字节保存在 [received](qiteng_text_audit_2026-08-29/received/)。写作 Skill ZIP 只读取相关规范，未安装、未执行其中程序，也未复制进仓库。

| 输入 | 字节数 | 实测 SHA-256 |
| --- | ---: | --- |
| SLE_Bcell_Manuscript_QiTeng_Refined_2026-08-29.docx | 37,657 | `86EF9D51C7D7B2472A434CE4851F5DAA2231479491FE43112AADFE5CAE719078` |
| SLE_Bcell_Manuscript_QiTeng_Refined_2026-08-29.pdf | 220,503 | `0605370085473800D7B2D4B991FF54619BB1DEEA6BA143A8AAAA2BFCBCD1C315` |
| SLE_Bcell_QiTeng_Manuscript_Refinement_Action_Record_2026-08-29.md | 12,141 | `044218312949D48FE0DC902903BCAF315FCF0F267A7AD4C7728800178E4B3C11` |
| QiTeng_Academic_Writing_Skill_v0.3.21_Full_Release_2026-08-26.zip | 10,953,826 | `C18AC4F0254286725B7449EA7B7E8DA89E8235B4FABA75B42A6E362D2AD87D99` |

**输入 PDF 的来源差异：**附带报告列出的 PDF SHA-256 是 `95121B630498DBB2D8D442816F772DAA8E6616D565ED1F81CFD8B33F635BAD70`，与实测值不符。收到的 PDF 与 DOCX 在规定的文本归一化后全文一致，但二进制差异原因未知；没有将其解释为“只是元数据变化”或“文件已损坏”。原始 PDF 保留不改。

附带报告提及的原始 refined Markdown 并未提供。本轮 [Received_Manuscript.md](qiteng_text_audit_2026-08-29/audit/Received_Manuscript.md) 是从 DOCX 提取的审阅源，不是找回了该原稿，更没有冒用报告中原 Markdown 的哈希。另生成 [Received_Paragraphs.md](qiteng_text_audit_2026-08-29/audit/Received_Paragraphs.md)，使用从零开始的 P000-P168 定位。

附件中的后续建议作为审阅输入，不自动产生批准、发布、收费或投稿授权。本轮没有证明具名独立外部方法学评审已签结。

## 3. 冻结包与科学文件无漂移

重新执行既有只读审计器，回执见 [frozen_candidate_audit.json](qiteng_text_audit_2026-08-29/frozen_candidate_audit.json)。

| 项目 | 核查结果 |
| --- | --- |
| corrected_candidate.zip | 26,632,739 bytes |
| ZIP SHA-256 | `D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150` |
| 包内 payload | 82/82 通过；含 manifest 为 83 entries |
| SOURCE_PROVENANCE | 75/75 当前来源大小和哈希不变 |
| 三个嵌套附件清单 | 15、184、10 行核验通过 |
| 规范主文、补充材料、RP、投稿信 | 未改，仍对应原候选 |
| 五主图、十补图及统计附件 | 未重绘、未替换 |
| 本轮独立图源数据指纹 | 15 个 CSV 纳入证据清单 |
| 新分析、mapper 训练、阈值或 outcome 解锁 | 均未执行 |

33 项输入/成品/证据/代码的大小和 SHA-256 见 [evidence_manifest.csv](qiteng_text_audit_2026-08-29/evidence_manifest.csv)。它不是整个工作路径的全量清单，本轮也没有重读数十 GB 矩阵或进行路径删除。冻结包内既往 60 页渲染证据因字节不变继续适用，但不能算作本轮新增的逐页检查。

## 4. 高风险问题与处理

| 定位 | 原表述或风险 | 本轮处置 |
| --- | --- | --- |
| Abstract P010-P012 | 外部复现可能被理解为也采用 disease-blind 重建身份 | 明示 source-label-defined conventional-B analog，摘要加入 C9R 校准失败且未估计纠正后的外部 disease effect |
| Abstract P011 | `estimate 0.947` 未命名估计对象 | 改为 `odds ratio 0.947` |
| Results P061 | 标题可能把 B_ASC 特定失败扩大为整个分类无复现性 | 改为 scaffold with state-specific stability limits |
| Results P067-P068 | `does not explain`、`was not higher` 把不显著结果当作排除解释或没有增加 | 改为无统计支持的差异，明确 CI 不能证明等效或排除增加 |
| Results P070 | `dominates transcription` 暗示全局主导或方差贡献分析 | 限定为四个预设 B_CONV 程序中支持最一致的 IFN/ISG |
| Results P075/P080、Discussion P093 | 低相关被写成否定完整共享转录组 | 限定为共享已检验基因集，改为不建立更强的全局共同状态主张 |
| Results P077 | 0.965/0.939 的阈值敏感性未明确所属分析 | 明确属于 combined_min20/combined_min100，不归给 childhood-only |
| Results P083 | heading 中的 IFN-centred control 有因果暗示 | 改为 convergent observational evidence |
| Discussion P091/P095 | `survives full hierarchy` 会掩盖 R1/C9R 正式失败 | 逐项说明 discovery、internal、source-label-defined external 支持 |
| Discussion P098 | hard labels 与程序的“更可重复”容易被当作同指标比较 | 明示 Jaccard 与程序关联复现是不同评估，不构成同尺度统计优越性检验 |
| Conclusions P100 | 最终主张过于概括 | 逐个写明发现队列、外部身份来源、C9R 无 outcome、无因果及临床效用 |
| Declarations P115 | 旧批准可能被自动迁移 | 改为这些 exact refined files 待批准 |
| 页眉/页脚 | 附件中额外边注计数 36 个 | 仅抑制 header/footer line numbering，保留正文连续行号与 Page 字段 |

完整替换前后与原因分别见 [editorial_changes.json](qiteng_text_audit_2026-08-29/editorial_changes.json) 和 [build_receipt.json](qiteng_text_audit_2026-08-29/review_candidate/build_receipt.json)。这些修改没有通过改图、改表、改阈值来使叙事“成立”。

## 5. 主要结论的证据归属

以下为对冻结图源表和决策的回查，不是重新拟合模型，也不是所有论文引用的完整文献审查。图源文件位于 `phase17_v7/post_gateC9/20260828_corrected_candidate/source_data/`。

| 主张 | 现有证据及主要数值 | 允许的解释与边界 |
| --- | --- | --- |
| B_ASC 主比较 | Figure 2b：OR 0.946653，95% CI 0.635705-1.409699，P=0.787279，90 strata | 没有统计支持的主差异；不是等效、介导排除或无生物学作用 |
| 次要 flare | Figure 2b：OR 2.302866，P=0.028174，q=0.084521 | 不替代主结果；未过原三比较校正 |
| 发现队列 IFN | Figure 3：effect 0.836556，CI 0.525430-1.147683，q=2.977e-6 | B_CONV 内程序关联，不是细胞级疾病重复或新的离散 subtype |
| 内部验证 | 同一 GSE174188 的完整及 donor-nonoverlap 分支；非重叠 effect 1.086 | 内部复现，去除 donor overlap 不把同 accession 自动变为独立队列 |
| 外部 childhood | Figure 4a：1.041757，CI 0.681166-1.402348，q=2.976e-6；11 HC/32 SLE | 独立 accession，身份范围仍是预定 source-label-defined analog |
| 外部 combined | Figure 4a：0.995974，q=1.310e-6；16 HC/38 SLE | 主要外部补充比较；不新增分析 |
| 20/100-cell 敏感性 | Figure 4a：combined_min20=0.964930，q=6.751e-7；combined_min100=0.938706，q=4.061e-6 | 必须标注 combined；不能用在 childhood-only 结果名下 |
| 外部 adult | Figure 4a：0.968416，CI -0.123444-2.060276，q=0.291356；5 HC/6 SLE | 方向相容但不精确，不能称独立 confirmatory 成功 |
| 跨队列广泛一致性 | Figure 4c：4,410 个 shared tested genes，Spearman rho=0.026；10 个 joint-tested IFN genes 双队列同向 | 支持预设程序复现，不建立全转录组共同疾病状态；也不证明所有共同生物学不存在 |
| 端到端身份稳定性 | S9：median/min ARI 约 0.963/0.930；B_ASC median Jaccard 0.930 < 0.95 | 正式 HOLD；不能用全局高指标覆盖特定状态失败 |
| 身份不确定性传播 | S9：20 个 composition OR 0.896-0.967，CI 均跨 1；40 个 IFN 估计 CI 均在零上 | 同数据 perturbation 支持结论耐受性，不是新独立样本或通过 taxonomy transfer |
| C9R 校准 | S10 及 calibration CSV：elastic-net coverage 0.941958，B_CONV precision 0.996450，B_ASC precision 0.885210 < 0.90 | 诊断 fallback，不是 eligible；辅助 centroid 成功不能替代主 mapper，无纠正后的 disease effect |
| 调控相关性敏感性 | S7：CAMERA 5/6、FRY 6/6；primary STAT2 CAMERA q=0.135472，FRY q=4.909e-5 | 保留方法例外，不写成所有方法普遍显著 |
| IFN 重叠耗竭 | S8：12-gene depletion ULM/CAMERA/FRY 分别 6/6、5/6、6/6；M5911 depletion 为 5/6、2/6、5/6 | 不是完全 overlap-independent 的调控证据 |
| 更宽耗竭的 STAT2 | S8：剩余 8/14 targets，ULM 0.391，CI -0.745-1.526，q=0.500；CAMERA q=0.623，FRY q=0.099 | 广泛 IFN-response 依赖仍然存在 |
| 外部响应情境 | Figure 5：M5911 NES 3.187/3.050/3.527；GSE23307 两位健康供者 paired log2(x+1) 均值 3.294/3.666 | 响应层支持，不建立 SLE 患者体内因果；n=2 无推断 P 值 |

**最终论文主轴：**在明确的身份定义和稳定性限制下，B_CONV IFN/ISG 程序关联得到发现、内部和源标签定义的外部支持；本研究不建立通用硬状态分类、普遍 B_ASC 扩张、特定因果调控器或临床使用规则。

## 6. 引用、图注和语言结构

从当前 canonical Markdown 与收到 DOCX 分别提取参考文献，按 29 个 DOI 身份和 3 个 GEO accession 身份匹配：**32/32 一一对应，重编号后每条 bibliography text 相同**。正文首次出现顺序为 1-32，无未列文献的引用号或孤立文献。作者单位的 `[1]` 不作为论文引用统计。完整旧号/新号映射在 [text_integrity_audit.json](qiteng_text_audit_2026-08-29/audit/text_integrity_audit.json)。

本轮有限核实了两篇现有文献在新 Discussion 中的位置，而非查找本项目已发表版本，也没有增删参考文献。Sayadi 等的 [2026 年原始论文页面](https://www.sciencedirect.com/science/article/pii/S0896841126000533)是既有 IFN 异质性背景；Faheem 等的 [原始研究全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13331238/)为 IFN 与 B-cell activation/differentiation 提供生物学背景。它们不是本研究程序或 mapper 的直接验证。其余 30 条没有重新做全文级核查，不能把“身份与编号正确”写成“32 篇引用的所有主张均独立核实”。

五幅主图的全部图注经空白/Markdown 格式归一化后与当前 canonical 图注一致。Figure 1c 的 0.990 仍明确表示 minimum mapping-agreement criterion；没有退回错误的 ARI 阈值语义。补图在本轮未重画，正文相关描述按上述源表和 HOLD 决策核对。本轮不冒称新做了一次全部图件的 Nature-style 视觉设计审查。

保留 tension-first Background、identity adjudication 与 end-to-end uncertainty propagation 的分离、answer-oriented Results 和解释增量型 Discussion。改变的是 unsupported strength，不是为了更吸引人而放大 effect。

## 7. 字数口径

以下使用同一计数函数：空格分词，排除 Markdown 标题和结构式摘要段首标签；不是期刊门户的计数器。

| 部分 | 冻结 canonical | 收到精修稿 | 本轮修订稿 |
| --- | ---: | ---: | ---: |
| Abstract | 309 | 310 | 330 |
| Background | 425 | 461 | 461 |
| Methods | 1,981 | 2,054 | 2,054 |
| Results | 1,849 | 1,850 | 1,875 |
| Discussion | 891 | 997 | 1,004 |
| Conclusions | 71 | 81 | 73 |
| Figure legends | 611 | 611 | 611 |

收到稿 Methods 的数字 token 集与 canonical 一致。其他部分的 token 差异来自表达位置和计数语境：摘要省去但 Results 保留 OR 范围 0.896-0.967；Background 去掉既有文献样本量 16 的一句；Results 明示已有总数 90 和 n=2、减少一次重复的 12；Discussion 重述已有 rho=0.026 和 12-gene 边界。逐条语义判读未发现改写后的数值估计与现有源表矛盾。

本轮 17 段局部修订另有数字 token 不变的程序防护。该防护不是语义正确性的充分条件，不能替代本轮证据归属审阅。摘要因加入 C9R 边界增加到 330 词；未定刊时不为追逐任意字数删掉决定性限制。

## 8. DOCX、PDF 与视觉质控

收到 DOCX 有 169 段，无表格、嵌入图、批注或 tracked insertions/deletions。图件在独立文件中交付，主文没有 embedded media 并非丢图。

最小修订通过 DOCX 原有样式与局部 OOXML 完成；修订前后未请求改变的段落文本逐项检查未变。未手工改 PDF。WPS 以后台只读方式打开新 DOCX 导出最终 PDF，备用使用 documents skill 的 `render_docx.py` 经 LibreOffice 渲染，再检查每一页 PNG。

| 检查 | 收到的 PDF | 最终 WPS PDF | 最终 DOCX 的 LibreOffice 渲染 |
| --- | --- | --- | --- |
| 页数 | 18 | 18 | 18 |
| 全文与对应 DOCX 归一化一致 | 是 | 是 | 是 |
| 超出物理页边界字符 | 0 | 0 | 0 |
| 页眉/页脚额外边注数字 | 36 | 0 | 0 |
| 正文连续行号 | 本轮未据此认定全版式通过 | 1-719 | 1-720 |
| 逐页视觉核查 | 来稿重渲染只抽查第 1、18 页 | 18/18 | 18/18 |
| 裁切、重叠、缺字、参考文献溢出 | 不宣称原件全量视觉通过 | 未发现 | 未发现 |

两种引擎的换行略有差异，因此正文行数不同，但页数与内容相同。主文段落在页末继续至下一页属于正常排版。最终结果没有段首孤立标题、页脚重复计数或异常参考文献溢出。accessibility audit 为 **0 high / 0 medium / 6 low raw-URL**，六项对应 ORCID、GitHub、GEO 直接链接；不为消除低级提示而改动链接身份。

文本核对只做 NFKC、空白和 soft-hyphen 归一化；PDF crop 为 x=65 至物理页宽、y=50-742 pt，排除页眉/页脚及正文左侧行号。早期把 crop 右边界设为 552 pt 时漏取 18 个右缘字符，随后修复为完整页宽；这是一处核验器裁剪错误，不是 PDF 缺字。测试专门证明额外 `X` 不会被归一化隐藏。

原始附件的“18/18 人工检查”自述与本轮检查分开。本轮的 18/18 指代理逐页查看生成图像，不声称有新增独立人类审稿者。渲染 PNG 留本地但不进入 Git；最终交付 PDF 采用 WPS 输出，备用 LO PDF 不作为第二套最终稿。

## 9. 代码与测试

新增并使用：

- [phase17_postc9_14_audit_refined_manuscript.py](../audit_tools/phase17_postc9_14_audit_refined_manuscript.py)：DOCX 提取、引用映射、段落/数字比较、PDF 文本/页边界/行号核查，只写管理目录。
- [phase17_postc9_15_build_refined_review.py](../audit_tools/phase17_postc9_15_build_refined_review.py)：校验收到 DOCX 的固定哈希后应用局部替换，只允许写独立 `review_candidate`；每段数值不变、图注和参考文献不变。
- [test_refined_manuscript.py](../audit_tools/test_refined_manuscript.py)：11 项新测试覆盖引用丢失/重复/逆序、数字保护、额外 X、非目标段落、重复替换及页眉计数修复幂等性。

最终组合执行 **50 项唯一测试通过**：33 个包/批准边界测试、6 个定刊准备核验测试、11 个本轮新测试。第一次从项目根目录按模块路径运行 unittest 因现有本地 import 约定产生三项加载错误；切换至 `audit_tools` 使用既有模块名后全通过，无需改动无关 import 结构。不能把加载失败写成科学模型失败。

复核命令：

```powershell
Set-Location 'H:\cuhk-2025fALL\6013RP-wyf\audit_tools'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest test_review_bundle test_target_preparation test_refined_manuscript -v
Set-Location 'H:\cuhk-2025fALL\6013RP-wyf'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' audit_tools/phase17_postc9_13_audit_target_preparation.py --output 00_project_management/qiteng_text_audit_2026-08-29/frozen_candidate_audit.json
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' audit_tools/phase17_postc9_14_audit_refined_manuscript.py --docx 00_project_management/qiteng_text_audit_2026-08-29/review_candidate/Manuscript.docx --pdf 00_project_management/qiteng_text_audit_2026-08-29/review_candidate/Manuscript.pdf --output-dir 00_project_management/qiteng_text_audit_2026-08-29/audit_review --no-extracts
```

这些是已完成的核验，不是要求用户再运行。再次执行审计会更新时间和回执哈希；重建 DOCX/PDF 也可能产生新二进制哈希，所以不能沿用本页的旧批准标识，须重建对应证据清单。

## 10. 成品与准确批准范围

成品入口为 [Review_Status.md](qiteng_text_audit_2026-08-29/Review_Status.md)，逐项收敛回执为 [final_verification.json](qiteng_text_audit_2026-08-29/final_verification.json)。

| 当前审阅成品 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Manuscript.docx | 37,842 | `F6DB97C146A6DC41EED1910C0D0E5FCAA03C9A03EACF29EDA2CFB9F3803BBE0B` |
| Manuscript.pdf | 253,145 | `DE6F9E1AAFD45995C99507FBC733AAF9FB8ACC1BD9AC6C1E2ED444AED60B7E73` |
| Manuscript.md | 63,712 | `D383FF7605144531DF8E6CF1F3DC710561ABB2D88E3B957EAE0DD94ABD8F7A32` |

Zhi Chen 与 Teng Qi 的身份信息、利益冲突、资助、伦理及 AI 使用声明保留用户已确认的事实；不推断其批准了新的 exact files。本轮独立精修稿明确待批准。当前 canonical/补充材料/投稿信不静默同步到这套新文本，避免产生“新主文配旧批准/旧包”的假象。

Git 仅收纳有价值的原件、修订稿、审计和工作记录。`.gitattributes` 保留输入和哈希证据的字节，`.gitignore` 新增三处 render cache 和一份重复 PDF 纯文本缓存排除。未删除用户文件，没有对全工作区再执行清理。未修改受冻结来源清单约束的 REPRODUCIBILITY、旧批准表、分析器、绘图器或 packager。

Git 同步采用普通提交和 push，不创建 release/tag。真实提交号与远端核对记录在本轮 [Git_Sync_Receipt.md](qiteng_text_audit_2026-08-29/Git_Sync_Receipt.md)，其生成时间在内容提交之后，避免预先把计划写成已完成。GitHub 源码同步不等于作者批准、Zenodo 发布或论文投稿。

## 11. 下一阶段判断

本轮建议的 `PRE_JOURNAL_HOSTILE_TEXT_AUDIT` 已完成，不再把相同正文反复送入无限精修循环。没有新错误证据时，不新增 cohort、mapper、TF 或 exploratory sensitivity。

下一阶段为 **`AUTHOR_TEXT_SIGNOFF_AND_JOURNAL_TARGET_FREEZE`**：

1. 两位作者确认本页哈希识别的精修稿科学叙事和限制；这一步是内容确认，不等于投稿授权。
2. 取得目标刊官方 JCR 数据年、全部相关类别、rank/denominator/quartile 和 APC/减免的书面条件，确定唯一目标刊。既有学校咨询草稿继续适用，本轮没有重新验证 JCR、替作者发邮件或承诺费用。
3. 定刊后只做一次必要的标题、摘要、章节、声明和图文文件适配；摘要保留 source-label-defined replication、R1/C9R 和观察性边界。当前 330 词不能默认符合指定刊。
4. 适配后的整套材料再统一核验，准备匹配代码/数据的新版本归档。预留 DOI、写入目标稿、生成最终文件和签署 exact-file 批准应保持一致；旧 DOI 不冒充当前修订归档。公开发布与实际投稿另按明确授权执行。

**本轮未完成且不宣称完成的事项：**具名独立外部方法学签结、32 篇文献全文复审、全工作区大文件检查、期刊最终格式、官方 JCR Q1 证明、APC 资格、当前精修文件的两作者批准、新 DOI/release，以及投稿。论文可信度和投稿资格不使用一个主观百分比替代这些分别可核验的条件。
