# SLE B-cell 项目全量本地审查、QiTeng 科学叙事与子图选择行动记录

日期：2026-10-12；时区：Asia/Hong_Kong。

## 1. 本轮裁决与授权范围

**裁决：`PASS_LOCAL_SCIENTIFIC_CANDIDATE_QA__HOLD_EXACT_AUTHOR_REVIEW_AND_CANONICAL_ADOPTION`。**

本轮按医学/生信导师级审查视角，核查本地文件、关键计数对象、结果来源、统计单位、主文与补充材料、五张主图和十张补充图，并依据上传的 QiTeng v0.3.24.2 构建独立正文候选。此裁决只说明本轮明确列出的检查通过，不是对全部历史计算、全部参考文献或投稿成功的保证。

本轮没有覆盖 canonical 主文、补充材料、图件或统计结果；没有推送 GitHub、更新 Release/Zenodo、制作新投稿包、下载 SRA、拟合新的疾病效应或再运行终局模拟。既往作者批准不自动等于批准本轮新文件。

输入 Git HEAD：`9840b159651c0622aee63ae6668394b4fc9de0c9`。开始时工作区干净。本轮新增候选、工具、Skill 解包和审查记录保持独立未提交。

## 2. 输入权威与版本漂移

本轮以 `5_manuscript/current/Manuscript.docx` 和 `Supplementary_Information.docx` 为可编辑文本权威。它们包含现行有限 Stage K 整合，原主文 32 页、补充材料 16 页。历史 Markdown 镜像没有完全同步，包括标题、缩写展开和若干图注措辞；不能将旧 MD 直接当作当前 DOCX 的精确来源。

本轮保存了 `BASELINE_DOCX_TEXT.md`、`PREEXISTING_MD_DOCX_DRIFT.diff`，从新可编辑候选导出 MD，避免混合两个文本版本。候选标题沿用当前 DOCX 的：

> Interferon remodeling remains reproducible despite less stable B cell state assignments in systemic lupus erythematosus

主图来源是 `4_figures/Fig1..Fig5/canonical/` 及其 source_data。补充图 S1–S10 的现行 CSV 使用 `phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration/figures/source_data/`，与 2026-10-12 当前包的 Supplementary Data 1 对应成员逐字节核对。

旧 `04_submission/journal_submission/portal_upload_required/Figure_Source_Data.zip` 只含 S1–S9，是历史来源陷阱；本轮没有据此误判当前包缺失 S10。`RP_V4_REDESIGN_STATUS.md` 顶部当前门与下部历史导航也有时间层差异；当前状态以 Stage M Gate 为准，不把历史“尚未运行模拟”段落当作今天的状态。

## 3. 全量文件核查的实际覆盖

快照时间：2026-10-12 07:45:03 UTC。目录：`9_version/scientific_content_reaudit_2026-10-12/`。

| 项目 | 结果 |
|---|---:|
| 普通文件 | 41,249 |
| 文件总大小 | 6,172,113,475 bytes，约 5.748 GiB |
| Git tracked | 4,719 |
| ignored local | 35,192 |
| untracked | 1,338 |
| 格式/结构检查 PASS | 41,249 |
| 格式/结构 HOLD / FAIL | 0 / 0 |
| 相同内容哈希组 | 14,474 |
| 理论重复字节 | 1,371,368,402 |

快照包含当时的项目普通文件，排除 `.git` 内部对象及该核查输出目录；早于本轮最终候选生成，不冒称最终文件总数。全量格式检查根据格式执行解析、结构或可读取性核验，**不等于逐字人工读完 41,249 文件，也不等于每个历史科学结论正确**。文件数量、大小、SHA-256、扩展名、角色、重复组及有价值资产均已登记。

本轮不做删除、移动或批量重命名。重复文件可能是版本冻结、独立审查、恢复包或投稿快照，不应仅按重复哈希清理。尤其 Git bundle、删除前恢复包、失败运行与授权合同必须保留。

主要输出：`FULL_LOCAL_FILE_INVENTORY_2026-10-12.csv`、`TOP_LEVEL_SIZE_SUMMARY_2026-10-12.csv`、`FILE_TYPE_SUMMARY_2026-10-12.csv`、`DUPLICATE_GROUPS_2026-10-12.csv`、`VALUABLE_ASSET_REGISTER_2026-10-12.csv`。

## 4. 原始矩阵与分析对象的深入只读验证

使用 `scientific_matrix_readonly_audit_20261012.py`，17/17 PASS，未拟合疾病模型。

| 对象 | 核验结果 |
|---|---|
| 硬 QC raw counts | 150,402 cells × 30,172 genes；CSR 103,783,938 个存储值 |
| 计数合法性 | 全部有限、非负整数；总计数 323,179,379 |
| CSR 结构 | indptr、indices、data 长度及索引范围合法 |
| 身份 | 150,402 唯一 cell ID；259 donors、271 samples、88 libraries |
| 对齐 | raw counts 与冻结 representation 的细胞顺序一致 |
| PCA/Harmony | 均为 150,402 × 50，数值有限 |
| 两套 UMAP | 均为 150,402 × 2，数值有限 |
| representation 无 X | embedding-only 对象的预期设计，不是原始表达矩阵丢失 |
| GSE135779 RAW.tar | 112 个普通成员，56 个压缩矩阵成员；无重复/不安全路径 |

三项文件大小及哈希保存在 `RAW_MATRIX_READONLY_AUDIT.json`：raw counts 270,671,628 bytes，representation 114,432,893 bytes，外部 TAR 1,299,783,680 bytes。

局限：本轮没有逐一解压外部全部矩阵后重新做疾病推断，没有重新判定全部生物学注释，也没有重新运行全部双细胞、pseudobulk、edgeR、mapper 或 CAMERA/FRY。这个只读核验解决的是对象结构、整数计数、身份与对齐的可靠性。

## 5. QiTeng v0.3.24.2 的使用与诚实披露

上传 ZIP：`C:/Users/Administrator/Desktop/QiTeng_Academic_Writing_Skill_v0.3.24.2_CompressionGovernance_Release_2026-09-20.zip`。

ZIP SHA-256：`d52d3804bf067f9ef469c9bc732ddc1acb4c123a49d086db5cec0b728e8ff17b`。

已读取版本注册、活跃 CORE、Compression Governance、global orchestration、figure/layout 规范。实际执行的写作原则是：GAP → RESPONSE → EVIDENCE → INTERPRETATION → BOUNDARY；每个 major claim 必须有明确 owner；压缩不能删除统计单位、负面边界、置信区间或 multiplicity family；不以固定字数指标强行缩写。

必须保留两项工具限制：

1. Skill 自带 package QA 返回失败，464 个 manifest 条目不一致。活跃 CORE 没有不一致，版本注册、CORE 与 QA 实现均与上传 ZIP 原始字节相符。没有修写包内 manifest，也没有把失败标成 PASS。原始报告见 `QITENG_PACKAGE_QA_RAW.json`、`QITENG_AUTHORITY_AND_LIMITATION.json`。
2. Skill DOCX 引用解析器把自动编号列表误当作没有参考文献。实际 33 篇条目用 OOXML paragraph `numPr` 编号；本轮独立核对 33 篇 bibliographic identities 不变、正文首次出现连续 1–33、无 orphan citation。原始工具结果保留在 `QITENG_DOCX_QA_RAW.json`，不能仅靠该解析器判断稿件引用完整性。

570 个 behavioral specifications 是规范条目数量，不是本轮执行了 570 个自动测试。没有声称 Skill 完整包通过，也没有声称 33 篇原始论文全文在本轮全部重新核实。

## 6. 科学主线与创新性重新判断

### 6.1 最可信的主结论

**在明确的身份与迁移限制下，供者/样本单位的 B_CONV IFN/ISG 过程关联，比本项目测试的硬状态赋值更能保留可重复支持。**

这不是新发现 SLE 中存在 IFN 信号，也不是提出通用 B-cell taxonomy。原始公开研究已经报道 IFN 相关异质性。可以主张的增量是：在同一分析框架中区分 identity、abundance、program、external mapping 与 regulatory interpretation，并公开失败边界。

“不同层面的可重复性”应限于本项目实际测试的层面与规则，不能升级为对所有 single-cell 方法的普遍排名。观察性 SLE 关联仍可能受到治疗、年龄、疾病定义、技术捕获及未测混杂影响，不能因此称为细胞内在作用、临床预测器或因果机制。

创新性目前是审稿风险，而不是软件 bug。新的 IFN 阳性图、网络或额外富集不能自动解决这个风险。SCI 分区和录用无法由本轮 QA 保证；当前科学规划仍以既定 SCI 二区目标为背景，不在这一轮另作期刊承诺。

### 6.2 建议的全文阅读链

1. **GAP**：身份稳定性、比例变化和转录程序经常被同一状态标签混合解释。
2. **RESPONSE**：先做疾病盲身份裁决，再按生物学单位分析；失败的 fine states 不进入疾病结论。
3. **EVIDENCE**：Figure 1 确定边界；Figure 2 报告组成结果；Figure 3 给出过程级 IFN 与 specificity；Figure 4 同时呈现外部支持、全基因弱一致性与 transfer failure；Figure 5 给出观察性调控语境和 depletion ceiling。
4. **INTERPRETATION**：可重复的程序关联不需要稳定的细粒度 taxonomy，但不证明广义状态赋值或因果调控成立。
5. **BOUNDARY**：identity、transfer、mechanistic 三个 ceiling 必须回收到 Discussion 结尾；后加的测量规则敏感性只承担同一 estimand 的区间重估。

这是证据组织，不是择优拼接显著结果。未通过门的结果不能删除、改成 PASS 或用另一种 mapper/检验替代。

## 7. 关键结果与不可跨越的解释边界

| 证据 | 核验的数值/单位 | 正确解释 |
|---|---|---|
| End-to-end identity | B_ASC median Jaccard 0.930323；criterion 0.95；minimum 0.871750 | 固定表示通过不等于端到端通过；R1 HOLD 保留 |
| Primary composition | 90 strata：43 control、47 managed SLE；OR 0.946653，95% CI 约 0.636–1.410，P=0.787 | 没有主要富集支持，不是等效性或“完全不变” |
| Secondary flare | OR 约 2.303；nominal P=0.0282，三对比 q=0.0845 | 次要、未通过对应多重校正 |
| Primary IFN/ISG | 89 pseudobulks：43 control、46 managed SLE；effect 0.836556，CI 0.525430–1.147683；四程序 q=2.977e-6 | 不把 150,402 cells 当疾病重复数；50-cell 规则排除一个仅 44 B_CONV cells 的 stratum |
| 内部分析 | full 64、donor-nonoverlap 54；IFN 保持支持 | 同一 accession 的内部支持，不是另一独立研究 |
| Primary pan-B specificity | effect 0.408921，CI 0.119030–0.698812，nominal P=0.006241 | 不能称全部对照为零；donor-nonoverlap CI 跨零，仍不能证明没有污染 |
| GSE135779 childhood | 43 donors：11 control、32 SLE；effect 1.041757，CI 0.681166–1.402348，q=2.976e-6 | source-label-defined broad-B analogue 的独立 accession 支持 |
| Combined/adult | combined 54 包含 childhood；adult 11 的 CI 跨零 | combined 不能算第二次独立复现；adult 仅方向性 |
| 全基因 vs IFN | 4,410 共同 tested genes；重算 Spearman rho=0.026051909；10 个共同 IFN genes 同向 | 特定程序一致，不是全 SLE 转录组重现 |
| Required calibration | coverage 0.941958；B_CONV precision 0.996450；B_ASC precision 0.885210 < 0.90 | C9R HOLD；没有 corrected external disease effect；centroid 不救援 |
| TF-target ULM | 8 regulators × 3 contrasts；global 24-test BH；STAT1/2 6/6 正向 | 模型行是带符号靶基因统计量，不是新增供者 TF 活性样本 |
| CAMERA/FRY | CAMERA 5/6；discovery STAT2 q 约 0.1355；FRY 6/6 | 保留相关性敏感性例外，不包装成全方法一致 |
| Overlap depletion | 去 12 genes 后 6/6 区间正；去 M5911 后 discovery STAT2 0.391，CI -0.745–1.526，q 约 0.500 | 支持更广泛 IFN 转录组耦合，不支持 overlap-independent causal regulator |
| IFN-beta context | 2 healthy donors，12/12 genes 各供者均正；没有 inferential P | 描述性背景；12 genes 不能充当 12 个 biological replicates |
| 测量规则敏感性 | 同一 68 donors：31 control、37 managed SLE；delta_profile=0.034925002 | WP1 与 Stage I 是同一结果对象，不是两次独立阳性发现 |

本轮独立重算四程序 CI 恒等式、4,410-gene Spearman rho、Stage I 的 t/P/CI 恒等式，并核对 Figure 5d 全部 12 条 depletion 来源记录；未重新拟合这些模型。

Stage I SE=0.011558535，HC3–t(64) CI=0.011834175–0.058015829，nominal P=0.003612459；WP1 paired percentile bootstrap CI=0.013789274–0.057129573。点估计差为约 6.94e-18。新方法开发在 WP1 阳性结果已知之后，必须称为 outcome-exposed uncertainty re-estimation。

T0 fixed-reference scoring 与主分析 TMM 的计分算子及入组人群不同，0.034925 不能除以主 IFN effect 当作组成介导比例。G2C 的 160,000 次记录、40 场景、30 applicable PASS/10 boundary 是本轮读取并核对已封存结果表与 Gate/hash，不是本轮再次执行或逐 attempt 重裁决。条件性模拟资格不能解除旧 G2/G2B 的其他目标 HOLD，也不证明现实数据全部潜在测量机制都被正确建模。

## 8. 所有子图的保留、修改或替换裁决

`PANEL_SELECTION_DECISION_MATRIX.csv` 列出全部 59 个子图：21 main + 38 supplementary，每行有科学职责、单位、裁决、边界和被拒绝的替代方案。`CLAIM_EVIDENCE_OWNERSHIP_MATRIX.csv` 列出 15 项 claim/design 的准确来源。

| 主图 | 子图职责与本轮决定 |
|---|---|
| Figure 1，a–d | workflow、fine/broad policy、fixed-representation overlap、end-to-end failure；科学内容全 KEEP，做源级导出候选修复 |
| Figure 2，a–d | observed/adjusted composition、contrast hierarchy、mandatory sensitivities、90×LOO；全 KEEP |
| Figure 3，a–d | 四程序竞争、IFN robustness、gene coherence、specificity controls；全 KEEP，正文补足 3d owner |
| Figure 4，a–d | 外部对比、跨分析展示、program/genome-wide 分离、required calibration failure；全 KEEP |
| Figure 5，a–e | evidence classes、core/extended TF、proliferation specificity、depletion ceiling、n=2 context；全 KEEP |

替代方案逐项拒绝理由：增加 UMAP 会强化 taxonomy-first 误读；volcano/network 不能替代预设程序对比；删 composition null/LOO 会损失关键诊断；将更多 S4/S8/S10 搬入主图会重复边界信息；causal-arrow signalling network 会越过观察性证据；旧 M5911 三柱图不能替代现行 5d；Stage I 不应升级成 Fig6 的“独立新发现”。Fig6–8 保留为目录预留，不为填满文件夹生成图。

补充图全部保留现行科学职责：S1 来源/QC，S2 表示，S3 fine-state failure，S4 identity propagation，S5 composition diagnostics，S6 pseudobulk/ranking，S7 external robustness，S8 calibration，S9 correlation-aware regulator sensitivity，S10 depletion。38 个 supplementary panel 无科学替换。

## 9. Figure 1 源驱动修复

实质排版问题：canonical Figure 1 PDF 使用 Type3 字体；panel b 的低位图例遮挡 minimum-ARI 数据点。其它 14 张现行图 PDF 未发现相同字体问题。

使用现行 Figure 1 builder 和完全相同 CSV，不修改原 PDF/PNG。从源重新渲染：`pdf.fonttype=42`；panel b 图例移至空白上部；panel c/d 保留父图固定刻度。输出在 `4_figures/Fig1/candidate_2026-10-12_truetype/`。

候选 PDF 为 170 mm 宽、可选文本、嵌入 TrueType；CSV SHA 与父源均为 `cdc5d50d16bb718ae410516a5456e16b513bd6c62c752e87480c149f0a0bd3e2`。PNG 仍为 4015 × 3086，但字体与图例调整造成约 6.50% 像素变化，不能称逐像素相同。源 builder、shared artwork、运行时与改变项均写入 `SOURCE_RERENDER_RECEIPT.json`。

Nature 图件指南使用 5–7 pt 正文和 8 pt bold panel label 等建议，要求合适的嵌入字体，而不是所有文本一概至少 8 pt。因此本轮没有把父图 170 mm 下 5.5–6 pt 字号机械判为 FAIL。本轮未取得 npj 当日专属全部要求的可靠页面，不能声称已完成最新 journal-specific 全面合规认证。

参考：[Nature Research Figure Guide](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)。IFN 已有研究背景核对参见 [Nehar-Belaid et al. 原始论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7442743/)。其余文献本轮未全篇重审。

## 10. 正文与补充材料的具体改进

共 18 条受控编辑记录，完整 before/after 与理由见 `QITENG_EDIT_LEDGER.csv`。关键编辑包括：

- Abstract 保持 159 words，补充 primary OR、89 pseudobulks 的 IFN effect/CI/四程序 q、43 external childhood donors 和 rho，不提高结论强度。
- 四程序比较错误指向 Figure 3d，改为 Figure 3a。
- Results 为 3d 增加准确 owner，主动报告 primary pan-B positive nominal 结果，保留污染解释边界。
- 同一 68 donors 的结果从 Discussion 移到独立 Results 小节；Discussion 保留测量算子解释、年代顺序与不同量尺边界。
- Methods 与 Figure 5 legend 明确 ULM 不确定性属于 signed-target gene-statistic model，不是 participant-level TF activity。
- Figure 4 legend 明确 within-analysis standardization；combined/childhood 重叠，图上共同坐标不等于 meta-analysis 或共同绝对表达量尺。
- Data/Code availability 区分旧核心 DOI 22151739 与后加 Table S10/Stage I，不声称 August archive 含 October 新结果。
- Supplementary overview 更新 Tables S1–S10，保留 Figures S1–S10。
- 修复 Stage K 遗留的两个 9 pt 主文段落为 12 pt Times New Roman，不靠缩字挤页面。
- Table S10 整合后 S1 heading/legend 与图像原来跨 pp.6–7，源级 keep-with-next 修复到同页；其图像内容不变。
- 从最后可编辑候选生成同步 Markdown，33 篇引用 identity 和顺序不变。

这些改动多数解决真实 evidence ownership、单位、年代或版面缺陷，不是为了让英文更强。未改病例定义、排除规则、effect/CI/P/q、multiplicity family、源标签、mapper、模拟门或作者/声明。

## 11. 构建与终局验证结果

| 检查层 | 本轮结果与含义 |
|---|---|
| 全量文件结构快照 | 41,249 PASS；不是科学真值认证 |
| 关键 raw/representation 只读 | 17/17 PASS |
| Source/unit 初始核查 | 43/44 PASS，1 HOLD：canonical F1 Type3；候选解决但原件保留 |
| 候选最终检查 | 127/127 PASS，0 HOLD |
| 主文 WPS 成品 | 33 页，逐页视觉检查 |
| 补充材料 WPS 成品 | 16 页，逐页视觉检查 |
| DOCX accessibility | 主文及补充材料各 0 high / 0 medium / 0 low |
| 文献结构 | 33 identities 保持，首次出现 1–33，自动编号独立解析 |
| MD/DOCX | 新候选导出文本一致 |
| S1–S10 | heading/image 同页，10 个 DOCX 媒体 SHA 不变 |
| 同引擎图像 fingerprint | 用同一 WPS helper 重渲染父版本后核对，通过 |
| 科学资产保护 | 45 个冻结 Figure/Source Data assets SHA-256 不变 |
| Table S10 来源 | CSV 和 execution JSON 与 Stage K/Stage I 权威对象逐字节一致 |
| 历史投稿包 | 未改变，也未自动包含本轮候选 |

视觉 QA 检查的是实际渲染页，不只看 JSON；未观察到 clipping、遮挡或异常字符。新增 Results 小节后重新渲染并复查受影响主文页，最终输出仍为 33 页。主文没有嵌入五张主图，因此其 33 页视觉 QA 不能代替外置图件 QA；本轮另看全部五主图与十补充图及 Figure 1 候选。

没有完成 LibreOffice 双引擎复核。历史 supplement PDF 与本轮 WPS helper 使用不同图像输出分辨率，不适合直接判 decoded-image SHA 相同；本轮用同设置重渲染父 DOCX 建立 apples-to-apples 基线，并同时保护原 DOCX media SHA。首次 QA 中的两项比较问题经修正测试设计后通过，不是通过改科学结果解决。

本轮没有把以前 208/208 的历史 regression 标签搬来冒充本轮重新执行。127 是当前候选脚本的检查项数，不是 127 个独立科学实验。

既有包 `6_release/SLE_Bcell_Submission_Package_2026-10-12.zip`：20,091,489 bytes；SHA-256 `349d69afa3d5a3b93b9e601186e6016ac5c9494eb64e79d00b36d607e561ed6e`，未修改。

## 12. 当前成果、未来资产与下一阶段

当前已经具备完整的五主图证据链、保留失败边界的外部分析、精确来源数据、供者/样本推断、条件性 G2C 方法资格以及同一测量规则差值的有限补充整合。主要贡献不是一个越来越大的显著结果集合，而是清楚区分哪些结论可重复、哪些规则失败、哪些解释不能作出。

所有有价值的计数矩阵、embedding、源 CSV、分析脚本、失败结果、冻结合同、工作记录、恢复包与新候选用途见 `VALUABLE_EVIDENCE_AND_FUTURE_USE.md`。本轮没有清理这些资产。

### 12.1 立即下一阶段

`EXACT_SCIENTIFIC_CANDIDATE_AUTHOR_REVIEW_AND_SOURCE_ADOPTION_GATE`

先审阅本轮 exact 主文 DOCX/PDF、Supplementary DOCX/PDF、Figure 1 候选与 18 条账本。重点确认：positive primary pan-B 的正确落点；同一 68 donors 的非独立性和 outcome-exposed 年代；ULM 的单位；旧 DOI 与后加结果的区别。作者批准以后才考虑源级纳入 canonical，并做对应增量回归，不以“上一版本已批准”代替新文件批准。

不建议重跑原 composition、主 IFN、mapper 或 TF 模型。出现真实数值错误、身份/来源错误、新数据或明确可检验的作者科学问题时才重新开启。

### 12.2 独立的新科学目标

RP v4 当前权威 Stage M 为 `PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION`，下一门是 `RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION`。

GSE262846 的价值是不同的前向问题：分选 resting-naive/transitional B 区室的供者内差异与活动度关系，而不是再次证明 IFN 阳性。现有计划涉及 176 runs、88 libraries、约 233 GB SRA；实际物理临时存储和合格运行时仍是硬门。26 个 paired SLE donors 的 12 active/14 inactive 规划不能被直接转写为已经得到的表达结果。

若要推进这项独立问题，必须先关闭 Stage N 的存储、运行时和下载授权条件，再执行统一参考的 raw-count 重构，并按原冻结前向合同分析。现在不能把尚未计算的队列放入 Figure 6，也不能用继续检验同一 68 人差值替代新信息。

## 13. 可复现工具与交付位置

工具位于 `audit_tools/`：

- `scientific_narrative_reaudit_20261012.py`：来源/单位核查与独立可编辑候选构建。
- `scientific_matrix_readonly_audit_20261012.py`：关键 raw/representation/TAR 深入只读核验。
- `rerender_figure1_truetype_20261012.py`：数值不变的 Figure 1 字体/图例重导出。
- `scientific_candidate_final_qa_20261012.py`：资产保护、引用、媒体、渲染、accessibility 与当前候选验证。

正文候选：`5_manuscript/scientific_narrative_candidate_2026-10-12/`。

图件候选：`4_figures/Fig1/candidate_2026-10-12_truetype/`。

全量目录快照：`9_version/scientific_content_reaudit_2026-10-12/`。

审查、账本、逐页 PNG、原始 Skill QA 与交付哈希：`7_report/scientific_narrative_reaudit_2026-10-12/`。

`CANDIDATE_DELIVERABLE_MANIFEST.csv` 记录候选成品 SHA 与大小，`FINAL_PAGE_VISUAL_QA.csv` 记录最终 49 页的视觉核验与图像哈希。新候选是待审查对象，不是已获批准的投稿包或新公开科学版本。
