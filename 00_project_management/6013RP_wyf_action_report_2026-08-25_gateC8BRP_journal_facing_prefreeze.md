# 6013RP-wyf Gate C8BRP 期刊可读版预冻结行动报告

**日期：** 2026-08-25

**角色：** 生物信息学导师级全项目复核、论文与投稿工程终检

**本轮决策：** `PASS_GATE_C8BR_JOURNAL_FACING_PREFREEZE_AUTHOR_ACTION_REQUIRED`

**科学冻结来源：** Gate C8S

**科学估计是否改变：** 否

**Portal 投稿是否授权：** 否

## 1. 本轮目标

本轮不是增加探索性分析，而是把已经封板的科学结果整理成无内部审计痕迹、可复现、可人工签署并可进入最终投稿预检的期刊可读版。具体目标为：

1. 修复过期的可重复性说明并分离科学分析环境与发布环境。
2. 生成不含 Gate、preflight、superseded history 等内部工程语言的 Supplement v6。
3. 从冻结代码和结果中完整报告 identity resampling 的真实算法，不重跑、不修改阈值。
4. 更新 manuscript v15 的语义精度和读者措辞。
5. 对 Figure 1a、Figure 4d 进行纯视觉重绘，保持 Source Data 逐字节不变。
6. 由构建器生成干净的期刊 portal 上传别名及可追溯映射。
7. 重建 DOCX、WPS PDF、逐页 PNG、无障碍报告和确定性 ZIP。
8. 对 42 页 WPS 输出和五张主图执行人工视觉检查。
9. 明确作者事实与作者停点，判断下一阶段目标。

## 2. 本轮输入与独立复核意见

已逐条核对以下外部复核材料：

- `SLE_Bcell_GateC8BR_release_portability_author_completion_matrix_2026-08-21.md`
- `SLE_Bcell_GateC8BR_final_release_action_matrix_2026-08-25.csv`
- 用户粘贴的 Gate C8BR 独立终局复核文本
- 用户再次确认的 Zhi Chen 与 Teng Qi 作者信息

外部复核给出的核心判断被采纳：停止新增队列、聚类、阈值、基因、调控因子和 signature；剩余工作转入 submission-facing polish、author facts、licence、DOI 与 release integrity。

## 3. 作者信息处理

以下信息被视为用户已确认事实：

| 项目 | Zhi Chen | Teng Qi |
|---|---|---|
| 作者角色 | 第一作者 | 通讯作者 |
| Email | zhichen1@link.cuhk.edu.cn | tengqi@link.cuhk.edu.cn |
| Academic title | MSc student in Bioinformatics | MSc student in Bioinformatics |
| Affiliation | School of Medicine, The Chinese University of Hong Kong, Shenzhen | 同左 |
| ORCID | 0009-0001-0072-5576 | 0009-0007-7648-4776 |

Zhi Chen 的个人简介经过英文校订后保存在 author completion matrix 中。Genome Medicine 的 Authors' information 为可选部分，主文继续不设置该小节。由于用户未提供 Teng Qi 简介，本轮没有推断或编写其个人简介。

通讯地址仍需 Teng Qi 本人确认；两人作者名单是否完整也仍需两位作者共同确认。

## 4. 可重复性修复

### 4.1 双环境锁定

`REPRODUCIBILITY.md` 已从旧 C8S/Codex runtime 描述更新为两层环境：

- 科学分析层：`sle-bcell-v7`，保留 explicit conda、pip freeze 和 resolved YAML。
- 发布层：`sle-bcell-c8br-release`，保留 pinned YAML 和新生成的 exact win-64 explicit specification。

新增发布环境锁：

`audit_tools/environment_gateC8BR_release_explicit_win64_2026-08-25.txt`

环境 smoke test 验证 Python 3.13.7、matplotlib 3.10.7、numpy 2.3.3、pandas 2.3.3、Pillow 12.3.0、python-docx 1.2.0 和 pypdf 6.10.0，并实际生成 PNG、PDF 与 DOCX。

### 4.2 Identity resampling 真实方法报告

Supplement v6 现明确报告：

- 使用全部 150,402 个细胞和冻结的 50 维 `X_pca_harmony`。
- 20 次重采样，每次在每个 `library_uuid` 内无放回抽取 80% 细胞，最少保留两个。
- 不重新计算 HVG、PCA 或 Harmony。
- 每次重新计算 15-nearest-neighbour graph 和 Leiden 0.4、0.6、0.8。
- 基础 seed 为 20260806；采样 seed 为 `20260806 + 1000 + r`，graph/Leiden seed 为 `20260806 + r`。
- 重采样 cluster 按 observed-by-reference contingency table 的逐行最大重叠映射至完整数据 reference cluster。
- 报告 ARI、AMI、majority mapping agreement、state Jaccard 和 recall。
- 完整报告 5、4、3 state 的原阈值和失败边界，以及 2-compartment 更严格阈值与实际通过值。
- `DERL3`、`JCHAIN`、`MZB1`、`TNFRSF17`、`XBP1` 的 B_ASC sample support 均为 1.00。

这些内容来自冻结脚本和既有结果，没有重新分析或调整阈值。

## 5. 主文与 Supplement 修复

### 5.1 Manuscript v15

生成：

`01_manuscript/manuscript_v15_genome_medicine_journal_facing_prefreeze_2026-08-25.md`

完成项目：

- Abstract 将 identity 结论改为 `did not support stable fine-grained naive/memory subtype assignments`，避免暗示生物状态不存在。
- Abstract 为 318 词，低于 Genome Medicine Research 的 350 词上限。
- 32 条参考文献序号连续。
- 修复 `edgeR :` 为 `edgeR:`。
- Figure 4d legend 说明显示标签 1-8 与 Source Data 原始 source code 的关系。
- 清除残留的 `post-audit`、`superseded audit artifacts` 等内部工程措辞。
- 保持现有标题；导师判断其编辑吸引力高于更长的 precision 备选标题，语义风险已由 Abstract 和正文边界充分缓解。
- 作者事实已写入；Authors' information 小节继续省略。
- 6 个作者控制 placeholder 保持可见，未伪造 ethics、funding、COI、CRediT 等事实。

### 5.2 Supplement v6

生成：

`01_manuscript/supplementary_information_v6_journal_facing_2026-08-25.md`

完成项目：

- 清除 Gate、preflight、release-portability、superseded 和修错历史。
- 保留 Supplementary Methods、Tables S1-S8、Figures S1-S7、统计家族图谱和可重复性映射。
- 七个补图 marker 和八张表全部成功转为 DOCX 内容。
- exact resampling mechanics 已加入 Supplementary Methods 2。

## 6. 图件修复与科学边界

### 6.1 Visual-only changes

- Figure 1a：将 ASCII `->` 句子改为三组对齐节点和箭头。
- Figure 4d：显示 `Omit source label 1` 至 `Omit source label 8`。
- Figure 5a：继续保持 regulatory branch 与 response branch 的平行证据结构。
- Figure 5c：继续使用 `proliferation specificity comparators`。

### 6.2 Source Data 不变证明

五张主图 Source Data 与 Gate C8BR 逐文件 SHA-256 完全一致：

| 文件 | SHA-256 |
|---|---|
| Figure1_source_data.csv | `60BED18114D447076538BB4C2355DCD7E29EA74701D5DF39654D1E4335200944` |
| Figure2_source_data.csv | `DAA6DDBAB469E0D510AB578BEE0A21AA73FA2D71184739E3F361C3EA6EC8DFE2` |
| Figure3_source_data.csv | `DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8` |
| Figure4_source_data.csv | `1C04F4071F7F064CA1AB4E47A281F0AA14074466E06BAB6FA30078029F570A9E` |
| Figure5_source_data.csv | `21925F6916DDAF97760CF73622ED8E4B4CCBE5AE0B3B53C721FDF607C1C6F9A4` |

Figure 4 Source Data 继续保留 `B-caSC0` 至 `B-caSC7`，因此读者标签没有破坏原始映射。

### 6.3 Nature 风格几何和字体检查

五张主图均为约 180.1 mm 宽，最高为 Figure 5 的 157.5 mm；每张 PDF 均检测到 Arial 与 Arial Bold。主图保留 vector PDF 和 600-dpi PNG。该设置与 Nature final artwork 对标准 sans-serif、panel labels 和 vector artwork 的通用要求一致，但不构成任何期刊接收保证。

官方参考：<https://www.nature.com/nature/for-authors/final-submission>

## 7. 文档、WPS 与可访问性

构建器生成：

| 文件 | 大小 |
|---|---:|
| Main manuscript DOCX | 59,723 bytes |
| Supplementary Information DOCX | 2,775,576 bytes |
| Cover letter DOCX | 40,181 bytes |

WPS 渲染与逐页检查：

| 文档 | 页数 | PDF 大小 | 页面 PNG | 视觉结论 |
|---|---:|---:|---:|---|
| Main manuscript | 28 | 251,073 bytes | 28 | PASS |
| Supplementary Information | 13 | 3,288,063 bytes | 13 | PASS |
| Cover letter | 1 | 84,468 bytes | 1 | PASS |

合计 42/42 页完成检查。未发现空白页、裁切、文本/图件重叠、表格不可读、图件 marker 断裂或 cover overflow。

三个 DOCX 的 accessibility audit 均为：high 0、medium 0、low 0。

## 8. 投稿文件名和确定性打包

构建器自动生成 18 个 clean portal aliases，包括：

- `Genome_Medicine_Manuscript.docx`
- `Supplementary_Information.docx`
- `Cover_Letter.docx`
- `Figure_Source_Data.zip`
- `Regulator_Sensitivity.zip`
- `Full_Statistical_Results.zip`
- `Figure_1.pdf` 至 `Figure_5.pdf`
- `Supplementary_Figure_S1.pdf` 至 `Supplementary_Figure_S7.pdf`

每个 alias 均与 provenance source 做 SHA-256 对照，并写入 `PORTAL_UPLOAD_FILENAME_MAP.csv`。Portal preview 内保留 `DO_NOT_UPLOAD_AUTHOR_ACTION_REQUIRED.txt`，因此当前没有误上传授权。

Full Statistical Results 保持与 Gate C8S 逐字节一致：

`AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`

本轮确定性投稿包：

- 文件：`04_submission/package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25.zip`
- 大小：44,159,282 bytes
- SHA-256：`1869A48700162B6CDF92002D60DDD4E7BE2B65008FC1A212CFFAB9BE8F0C4F05`
- Manifest payload：138 files
- 两次独立重建 SHA 一致：PASS

该包仍是 author-completion prefreeze，不是可直接上传的 final release。

## 9. 自动断言结果

- 主图数值与 panel-data assertions：46/46 PASS。
- 补图 assertions：29/29 PASS。
- DOI identity verification：28/28 PASS。
- Manuscript references：32。
- 主图 Source Data：5/5 与上一冻结状态一致。
- Supplement internal-history tokens：0。
- Full Statistical Results：63 entries，12 complete gene branches，12 sanitized design matrices。
- Portal aliases：18/18 哈希匹配。
- WPS 页面：42/42 完成。
- Accessibility findings：0。
- Scientific estimates changed：NO。

## 10. 上传行动矩阵关闭情况

### 10.1 本轮已关闭的 code-owned P0

- FINAL-01 `REPRODUCIBILITY.md` 更新：完成。
- FINAL-02 journal-facing Supplement v6：完成。
- FINAL-03 identity-resampling mechanics：完成，无重跑。
- FINAL-04 checklist/target provenance：完成。
- FINAL-12 clean upload filenames：完成并纳入 manifest。
- 当前轮 WPS/a11y/确定性 archive 预冻结检查：完成。

### 10.2 本轮已关闭的 P1 polish

- POLISH-01 Figure 1a graphical workflow：完成。
- POLISH-02 Figure 4d reader-facing source labels：完成。
- POLISH-03 Abstract semantic precision：完成；标题经判断保留。
- POLISH-04 exact win-64 release environment spec：完成。
- STROBE-informed internal checklist：完成。
- Vancouver reference punctuation：完成。

### 10.3 继续冻结的科学任务

STOP/SCIENCE 被严格执行：未增加数据集、细胞聚类、阈值、基因、TF、signature 或结局分析。

## 11. 当前不能由代码关闭的作者停点

以下内容必须由作者或机构提供真实、可签署信息：

1. 公开去标识化人类数据二次分析的机构 ethics determination，以及委员会名称/编号（如适用）。
2. 两位作者的 financial 与 non-financial competing interests。
3. Funding、grant number、recipient initials、funder role，或明确的 no-specific-funding statement。
4. ZC/TQ 的最终 CRediT roles。
5. Acknowledgements 或 `Not applicable`。
6. 两位作者对完整作者名单、稿件、补充材料、图片、源数据和 cover 的批准。
7. Originality、exclusive submission 和未同时投稿确认。
8. Generative-AI assistance disclosure 的作者批准。
9. Teng Qi 对通讯地址的批准。
10. 代码 licence 的作者/机构批准；不得重新许可 GEO/CELLxGENE 公共数据。
11. APC institutional agreement、funding 或 waiver 策略。

Genome Medicine 当前 Research 指南要求结构式摘要不超过 350 词、完整机构地址和 Declarations；即使人类数据伦理审批被免除，也需要明确的 ethics statement。官方来源：<https://link.springer.com/journal/13073/submission-guidelines/research>

## 12. 下一阶段导师判断

下一阶段不应创建新的生信分析 Gate。唯一合理目标是：

`PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`

建议执行顺序：

1. 作者填写并签署上述 11 类事实。
2. 两位作者批准通讯地址、作者名单和 licence。
3. 选择 licence，完成最终 author-completed commit。
4. 建立 GitHub release，并用 Zenodo 或等效服务绑定该 exact commit，获得 immutable DOI。
5. 将 DOI 回填至 manuscript、cover letter、README、repository citation 和 portal fields。
6. 将主文 6 个 placeholder 和 cover 2 个 placeholder 降为 0。
7. 运行同一 full runner，重新执行 42+ 页 WPS、a11y、alias、manifest 和两次 ZIP 重建。
8. 冻结最终 ZIP bytes、SHA-256、release tag、commit 与 DOI。
9. 按 portal field-by-field matrix 做 Genome Medicine 最终预检后再提交。

## 13. 最终导师结论

论文的科学与统计层已经成熟并应继续冻结。本轮已经关闭独立审计指出的全部 code-owned P0/P1 缺口，使主文、Supplement、图件、环境锁、上传别名和确定性包处于一致状态。当前风险不再是计算结果，而是作者事实、机构伦理措辞、licence、DOI 和最终 portal 一致性。

在作者停点关闭前，不应上传当前 portal preview，也不应为追求“更完整”重新打开探索性生信分析。
