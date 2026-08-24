# 6013RP-wyf Gate C8BRF 作者完成、预留 DOI 与发布前冻结行动报告

**日期：** 2026-08-25

**角色：** 生物信息学博士生导师级终局复核、论文精修、图件与发布工程质控

**本轮决策：** `PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`

**科学冻结来源：** Gate C8S

**科学估计是否改变：** 否

**预留 DOI：** `10.5281/zenodo.22086892`

**版本：** `v1.0.0`

**公开发布状态：** GitHub Release 与 Zenodo record 尚未公开；等待作者对不可逆公开发布动作作最后即时确认

## 1. 本轮目的与边界

本轮将 Gate C8BRP 的期刊可读预冻结状态转为作者事实完整、许可证明确、真实 DOI 已回填、可进入发布与期刊 portal 的最终候选版本。严格执行既有 STOP/SCIENCE 边界，不增加数据集、聚类、阈值、基因、调控因子、signature 或结局分析，不通过修改结果文件制造更强结论。

本轮目标为：

1. 将作者确认的 ethics、competing interests、funding、acknowledgements、CRediT、完整稿件批准、原创性与一稿专投声明写入最终稿。
2. 完成代码 MIT、原创内容 CC BY 4.0、第三方数据不重新许可的许可证治理。
3. 在 Zenodo 预留 DOI，并将真实 DOI 回填到稿件、补充材料、投稿信、README 与 `CITATION.cff`。
4. 将五张主图统一重建为 170 mm 宽，修正 Figure 1 出版数据与阈值语义，不改变科学估计。
5. 独立核查 Figure 2 UUID 的公开来源、分析角色与隐私属性。
6. 生成干净 DOCX、WPS PDF、逐页 PNG、portal REQUIRED/OPTIONAL 上传集合和确定性 ZIP。
7. 完成自动断言、无障碍、逐页视觉、文件哈希和发布前完整性审计。

## 2. 作者事实与声明关闭

### 2.1 作者元数据

| 项目 | Zhi Chen | Teng Qi |
|---|---|---|
| 作者角色 | 第一作者 | 通讯作者 |
| Email | zhichen1@link.cuhk.edu.cn | tengqi@link.cuhk.edu.cn |
| Academic title | MSc student in Bioinformatics | MSc student in Bioinformatics |
| Affiliation | School of Medicine, The Chinese University of Hong Kong, Shenzhen | 同左 |
| ORCID | 0009-0001-0072-5576 | 0009-0007-7648-4776 |

通讯地址使用：MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China。

### 2.2 作者确认后写入的声明

- 本研究为公开、去标识化人类转录组数据的二次分析，不招募参与者、不实施干预、不采集新样本，因此无需额外伦理审批。
- 稿件不含可识别个体信息，Consent for publication 为 Not applicable。
- 两位作者声明无 competing interests。
- 本研究无 specific funding。
- Acknowledgements 为 Not applicable。
- 两位作者已批准稿件、补充材料、图表、源数据和投稿信。
- 两位作者确认论文原创、一稿专投，且未在其他期刊审稿。
- 两位作者批准公开生成式人工智能辅助声明。
- 生成式人工智能仅用于代码开发辅助、工作流文档、语言编辑与质量检查；未用于生成或修改原始研究数据；全部分析、文本、引用、图件和源数据均由作者核查并承担责任。

### 2.3 CRediT

- Zhi Chen: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft.
- Teng Qi: Conceptualization, Methodology, Project administration, Validation, Writing - review & editing.
- Both authors read and approved the final manuscript and associated submission materials.

没有推断或添加 Teng Qi 的 Supervision 角色。

## 3. Zenodo DOI 与元数据

Zenodo 已通过作者账户保存未公开草稿：

- Draft record: `https://zenodo.org/uploads/22086892`
- Reserved DOI: `10.5281/zenodo.22086892`
- Resource type: Software
- Version: `1.0.0`
- Publication date: 2026-08-25
- Repository: `https://github.com/1209433622cz-maker/sle-bcell-remodeling`
- Creators: Zhi Chen、Teng Qi，均含 ORCID 与机构信息
- Teng Qi 在 Zenodo creator metadata 中标记为 Contact person
- Licences: CC BY 4.0 与 MIT
- Language: English
- Programming language: Python

DOI 目前仅为预留状态。记录公开发布后 DOI 才注册并解析；在发布前删除草稿会失去该预留 DOI。本轮没有把草稿误记为已公开记录。

## 4. 许可证治理

新增：

- `LICENSE`: 原创代码采用 MIT License。
- `LICENSE_CONTENT_CC_BY_4.0.md`: 原创稿件文本、复合图、项目文档和项目生成的派生 source tables 采用 CC BY 4.0。
- `LICENSE_SCOPE.md`: 明确双许可证边界与第三方排除项。

许可证不适用于、也不重新许可 GEO、CELLxGENE、第三方文章、数据库内容、软件或其派生受限材料。原始第三方数据继续受原来源条款约束。

## 5. 代码与方法修复

### 5.1 主图构建器

`audit_tools/phase17_c7_01_build_main_figures.py` 增加物理宽度控制，图件按目标宽度缩放并保留纵横比与字体点数。Figure 1 构建器增加 publication source-data 与 explicit threshold semantics 开关。

Figure 1 的出版版 source data 仅删除两个不用于绘图的 `gate_decision` 内部审计行；其余数据不变。三条虚线标准均在图中直接标注：

- two-compartment minimum mapped ARI: 0.90
- minimum mapped ARI guide: 0.990
- minimum median Jaccard criterion: 0.95

### 5.2 新增 Gate C8BRF 工作流

- `phase17_c8brf_00_build_main_figures.py`: 重建五张 170 mm 主图并验证 46 项 panel-data assertions。
- `phase17_c8brf_01_uuid_governance.py`: 核查 Figure 2 UUID 的公开来源与隐私属性。
- `phase17_c8brf_02_build_submission_sources.py`: 强制使用真实 DOI 构建 manuscript v16、Supplement v7、cover、作者确认、reporting checklist、Zenodo metadata、README 与 `CITATION.cff`。
- `phase17_c8brf_03_build_documents.py`: 构建三份可编辑 DOCX、portal REQUIRED/OPTIONAL 目录与上传映射。
- `phase17_c8brf_04_final_audit.py`: 执行声明、DOI、许可证、图件、source data、UUID、DOCX、WPS、a11y、S7 分页、统计归档与确定性 ZIP 审计。
- `run_6013RP_phase17_gateC8BRF_author_release.ps1`: 统一执行九阶段发布冻结流程。

Supplement DOCX 构建器在 S7 标题前强制分页，避免标题与图件跨页。

## 6. 最终稿件

### 6.1 Manuscript v16

文件：`01_manuscript/manuscript_v16_genome_medicine_final_2026-08-25.md`

- 结构式摘要 318 词。
- 参考文献 32 条且连续。
- 作者、机构、通讯地址、Email 和 ORCID 完整。
- Declarations 全部关闭。
- 数据与代码可用性包含 GitHub 地址、`v1.0.0` 和 DOI。
- Generative AI disclosure 已写入。
- 主文与 cover 的未决 placeholder 均为 0。

### 6.2 Supplement v7

文件：`01_manuscript/supplementary_information_v7_final_2026-08-25.md`

- Supplementary Methods 完整保留预注册、疾病盲身份重建、样本层组合、pseudobulk、外部验证、调控与敏感性设计。
- Tables S1-S8 完整。
- Figures S1-S7 完整嵌入 DOCX。
- 仅保留 7 个用于文档构建的补图嵌入 marker，非作者待填 placeholder。
- S7 在 WPS 输出中从第 13 页新页开始，标题与第一数据内容同页。

### 6.3 Cover letter

投稿信已删除所有作者待填项，保持一页，并明确研究增量、证据边界、公开资源、许可证、作者批准、原创性、一稿专投、无利益冲突、无特定经费和生成式人工智能辅助声明。

## 7. 图件与 Source Data 终审

### 7.1 五张主图物理尺寸

| 图件 | 宽度 | 高度 |
|---|---:|---:|
| Figure 1 | 170.000 mm | 130.677 mm |
| Figure 2 | 170.000 mm | 134.274 mm |
| Figure 3 | 170.000 mm | 137.870 mm |
| Figure 4 | 170.000 mm | 137.870 mm |
| Figure 5 | 170.000 mm | 148.660 mm |

每张主图均保留 vector PDF 与 600-dpi PNG。五张主图已逐张原始分辨率人工检查，未发现裁切、重叠、标签歧义或不可读文本。

### 7.2 数值一致性

- Main-figure panel-data assertions: 46/46 PASS。
- Supplementary-figure assertions: 29/29 PASS。
- Figures 2-5 Source Data 与 Gate C8BRP 逐字节一致。
- Figure 1 出版 Source Data 仅删除两条未绘制内部审计行。
- Scientific estimates changed: NO。

Source Data SHA-256：

| 文件 | SHA-256 |
|---|---|
| Figure1_source_data.csv | `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805` |
| Figure2_source_data.csv | `DAA6DDBAB469E0D510AB578BEE0A21AA73FA2D71184739E3F361C3EA6EC8DFE2` |
| Figure3_source_data.csv | `DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8` |
| Figure4_source_data.csv | `1C04F4071F7F064CA1AB4E47A281F0AA14074466E06BAB6FA30078029F570A9E` |
| Figure5_source_data.csv | `21925F6916DDAF97760CF73622ED8E4B4CCBE5AE0B3B53C721FDF607C1C6F9A4` |

## 8. Figure 2 UUID 治理

独立审计结论为 `PASS_FIGURE2_PUBLIC_NON_IDENTIFYING_SOURCE_UUIDS`：

- Figure 2 的 `sample_uuid` 与 `omitted_sample_uuid` 并非本地生成作者标识，而是公开 CELLxGENE H5AD `obs.sample_uuid` 字段中的 UUIDv4。
- Figure 2 中 90 个唯一 UUID 全部映射到冻结的 Gate C3/C3A 分析输入。
- 公开 H5AD 报告 274 个 sample UUID。
- 本地 H5AD 大小 12,218,105,530 bytes，与公开资产一致。
- Figure 2 Source Data 中无姓名、Email、patient name 或其他直接身份字段。
- 这些 UUID 是冻结的生物分析单位，因此保留原值比替换为本地序号更有利于可追溯性。

## 9. DOCX、WPS、无障碍与人工视觉检查

| 文档 | DOCX 大小 | WPS 页数 | WPS PDF 大小 | a11y high/medium/low | 视觉结论 |
|---|---:|---:|---:|---:|---|
| Main manuscript | 60,005 bytes | 29 | 252,452 bytes | 0/0/0 | PASS |
| Supplementary Information | 2,775,576 bytes | 13 | 3,287,905 bytes | 0/0/0 | PASS |
| Cover letter | 40,291 bytes | 1 | 73,004 bytes | 0/0/0 | PASS |

共 43/43 页完成逐页 PNG contact-sheet 人工检查。未见空白异常页、裁切、文本或图件重叠、表格越界、图件 marker 遗留或 cover overflow。

## 10. Portal 上传集合

最终 portal preview 明确分为：

- REQUIRED: 11 files，包括 manuscript、Supplementary Information、cover、3 个附件 ZIP 和 Figure 1-5。
- OPTIONAL: 7 files，为单独 Supplementary Figure S1-S7；Supplement DOCX 已嵌入全部补图，因此默认不重复上传。

`portal_required` 和 `portal_optional` 内的干净文件名均由构建器生成，并保留 provenance 与哈希映射。Portal upload set 已通过技术授权，但尚未执行期刊提交。

## 11. 确定性投稿包

- 文件：`04_submission/package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip`
- 大小：46,055,879 bytes
- SHA-256：`1FB1170B68E399EDBCF95400611FDF733BDCB3B64BA64640AF0958494CC7904A`
- Manifest payload files: 151
- 两次独立确定性重建哈希一致：PASS
- Frozen Full Statistical Results SHA-256：`AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`
- 未纳入受限大体积原始数据：PASS

## 12. 自动审计总结果

最终机器判定：

`PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`

关键断言：

- zero manuscript placeholders: PASS
- author declarations complete: PASS
- persistent citation complete: PASS
- licence scope: PASS
- 170 mm main-figure contract: PASS
- Figure 1 publication source: PASS
- Figure 2 UUID governance: PASS
- supplementary assertions 29/29: PASS
- portal REQUIRED/OPTIONAL policy: PASS
- DOCX structure and content: PASS
- DOCX accessibility: PASS
- WPS render integrity: PASS
- S7 pagination: PASS
- frozen statistical archive: PASS
- no restricted large source data: PASS

构建过程中的 `pdftoppm` elevated-privilege 与 MiKTeX Windows compatibility 文本来自页面栅格化工具环境；页面 PNG 数量、PDF 解析、视觉检查及最终审计均通过，不构成输出缺失或科学错误。

## 13. 仍未执行的公开动作

以下动作具有外部公开与不可逆属性，必须在即时确认后执行：

1. 将本轮变更推送到 GitHub `main`。
2. 创建并推送 `v1.0.0` tag。
3. 创建公开 GitHub Release 并上传最终投稿包、source archive 与 checksums。
4. 将冻结文件上传至 Zenodo draft 22086892。
5. 发布 Zenodo record，使 DOI `10.5281/zenodo.22086892` 注册并公开解析。
6. 核对 GitHub Release URL、Zenodo record、DOI resolution 与文件哈希。

## 14. 下一阶段导师判断

不应建立新的生信分析 Gate。下一阶段唯一合理目标为：

`PUBLIC_RELEASE_INTEGRITY_AND_GENOME_MEDICINE_PORTAL_ENTRY`

执行顺序：

1. 获得作者对 GitHub Release 与 Zenodo record 公开发布的即时确认。
2. 发布完全冻结的 `v1.0.0`，验证 DOI 和双向链接。
3. 按 REQUIRED 11 项逐字段录入 Genome Medicine portal；7 个 standalone supplement figures 保持 OPTIONAL，避免与嵌入式 SI 重复。
4. 投稿前由通讯作者对 portal 自动生成 PDF、作者顺序、通讯邮箱、声明、文件分类和 DOI 再做一次人类终检。
5. 完成投稿后冻结 portal receipt、manuscript number、提交时间和实际上传文件哈希。

从科学与工程质量看，当前稿件已经达到可公开归档并进入 Genome Medicine portal 的条件；继续增加探索性分析的边际收益低于破坏冻结一致性的风险。
