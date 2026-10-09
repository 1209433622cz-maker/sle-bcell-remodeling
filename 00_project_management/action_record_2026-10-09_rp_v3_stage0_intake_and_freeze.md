# RP v3 Stage 0 输入恢复、执行冻结与门控行动记录

**日期：** 2026-10-09
**研究阶段：** `SCIENTIFIC_REDESIGN_STAGE0`
**依据文件：** `SLE_Bcell_RP_v3_定向科学重设计研究计划书_20261009.docx`
**本轮边界：** 只执行 WP0 输入恢复、来源核查、单位登记、目标量/分支/参数登记和 G0/G1 预检；不估计新的疾病效应，不修改旧主稿、旧图、投稿包、GitHub Release 或 Zenodo。

## 1. 本轮目标

RP v3 将项目状态从此前的投稿维护冻结，调整为 `GO_FOR_FOCUSED_SCIENTIFIC_REDESIGN / HOLD_SUBMISSION`。本轮据此完成 Stage 0 的第一部分：

1. 核实 RP v3 的正文、表格、修订/批注结构和实际渲染；
2. 恢复并哈希 GSE174188、GSE135779 与历史证据包的关键输入；
3. 建立 `input_manifest`、`unit_registry`、`decision_chronology`、`estimand_registry`、`branch_registry` 和 `parameter_freeze`；
4. 重新判定 G0 输入可行性与 G1 可识别性预检；
5. 固定下一阶段的技术试跑边界，防止在看到新结果后再选择分支或量尺。

## 2. RP v3 文件核查

- 文件大小：293,419 bytes；SHA-256：`14E7150A1CCB941B72558575C218AA0A6964CD0D90240FD15DD4CAB9F3065F4A`。
- 结构：394 个段落、19 张表、3 个内嵌图形、1 个 section。
- LibreOffice 实际渲染：36 页，逐页 contact-sheet 核查未见裁切、重叠、表格越界或图片缺失。
- OOXML 精确标签核查：0 个 tracked insertion、0 个 tracked deletion、无 comments part；25 个 `instrText` 为 Word 字段指令，不是修订痕迹。
- 维护项：目录仍把附录 E 标为第 37 页，而实际末页为第 36 页。该问题不影响科学执行，但下次正式更新 RP 时应刷新目录字段。

## 3. 输入恢复与完整性结果

### 3.1 GSE174188

- 原始计数对象：`150,402 cells x 30,172 genes`，270,671,628 bytes。
- 稀疏矩阵逐块扫描：全部有限、非负、整数值；最小非零值 1，最大值 7,836，最大整数偏差 0。
- 细胞索引唯一，`donor_id`、`sample_uuid`、`library_uuid`、`Processing_Cohort` 均无缺失。
- 单位结构：259 名 donor、271 个 sample、88 个 technical library、4 个 processing cohort。
- 11 名 donor 具有多个 sample；53 个 sample 跨越多个 processing cohort，因此新分析必须保留 donor 成簇不确定性和 sample-cohort stratum 身份。
- 原始计数 H5AD 与冻结表征 H5AD 的 150,402 个细胞顺序及四个核心单位字段完全一致。
- 历史主组成设计为 90 个 strata；历史主 B_CONV 转录设计为 89 个 pseudobulk 且对应 89 名唯一 donor。缺少的一项仍是原来仅有 44 个 B_CONV 细胞的 managed-SLE stratum，未改写准入规则。

### 3.2 GSE135779

- RAW archive：1,299,783,680 bytes；SHA-256 与项目冻结值 `B5764C303AC76873738D6E05B6992277FCD6A14BF5BFCB27331E54DCBCAC619B` 一致。
- TAR 内含 112 个文件，严格对应 56 个 matrix/barcode 配对样本，无孤立 matrix 或 barcode 文件。
- 来源审计为 44 个 childhood 和 12 个 adult 样本；所有稀疏计数均为非负整数。
- 历史 childhood 主模型保留 43 名合格 donor。该结果已经被团队查看过，后续只能称结果已知背景下的外部评价，不能重新命名为全新盲法验证。
- `libaries.csv` 仍是带 `SampleX` 和占位路径的示例模板，不进入单位选择、映射或疾病推断。

### 3.3 历史包与诊断包

- QiTeng R4 历史投稿候选：内部 manifest 38/38 文件通过字节数和 SHA-256 校验。
- 2026-10-09 独立诊断包：内部 manifest 34/34 文件通过校验。
- RP v3、R4、旧回溯性 RP 与独立诊断包已复制到本轮 `inputs_readonly`，后续复跑不依赖 Downloads。
- 旧投稿候选保持只读；本轮没有将后验诊断升级为确认性证据。

## 4. 六项 Stage 0 登记表

### 4.1 `input_manifest`

登记 21 个关键文件，21/21 存在并完成 SHA-256。包含计划依据、历史读者稿、诊断包、GSE174188 原始计数/表征/单位/模型对象和 GSE135779 RAW/元数据/外部单位对象。

### 4.2 `unit_registry`

明确 cell、donor、sample、technical library、sample-cohort stratum 和 pseudobulk 的层级。疾病效应的独立抽样单位固定为 donor；技术文库和细胞数不增加独立重复数。

### 4.3 `decision_chronology`

将 2026-08-06 至 2026-08-15 的疾病盲技术阶段、后续效应分析、2026-08-28 后加敏感性/纠正、2026-09-29 R4 读者稿和 2026-10-09 诊断/RP v3 分开登记。RP v3 只对新的 WP1-WP3 分支具有前向协议身份。

### 4.4 `estimand_registry`

登记 `beta_B`、`delta_beta_ann`、`beta_S`、`delta_beta_comp`、`beta_k` 和 `beta_E(T)`。所有目标量绑定人群、供者单位和评分变换；组成标准化目标不称疾病直接因果效应。

### 4.5 `branch_registry`

- `A0`：历史 B_CONV/B_ASC scaffold，保留原身份失败；
- `A1`：已有 14 基因 disease-blind naive-to-memory 候选字典，与冻结 IFN 程序 0 基因重叠，但评分构造及支持规则尚未冻结；
- `A2`：已有 3,000 个 IFN-excluded HVG 的历史规范，强 ISG 数为 0；materialized branch H5AD 已清理，必须从原始输入重建；
- `T_local`：历史量尺；
- `T0`、`T_frozen`、`T_rank`：仍为开放协议对象；
- `WP4`：继续 `HOLD_CONDITIONAL`。

### 4.6 `parameter_freeze`

已冻结原始输入、donor 抽样单位、重复 donor 原则、12 基因 IFN 成员、A1 候选成员、A2 历史特征规则和四类核心模拟情景。仍开放：新状态支持阈值、`T0`、`T_frozen`、`T_rank`、`pi_ref`、bootstrap 精度执行、模拟参数/验收界限和新检验家族中的 K。

没有可辩护的等效或非劣 margin；因此后续只报告连续差值及区间，禁止写“等效”“非劣”或“组成无关已证明”。

## 5. 门控裁决

### G0A：输入恢复

**PASS。** 21/21 输入可用；13 项技术检查全部通过。GSE174188 原始计数、冻结表征、单位映射、历史模型对象和 GSE135779 RAW 均可用于限定技术试跑。

### G0B：协议冻结

**HOLD。** HOLD 来自真实协议字段尚未冻结，而不是数据缺失。开放字段为：`state_support_threshold`、`T0`、`T_frozen`、`T_rank`、`pi_ref`、bootstrap 执行精度、simulation 参数/验收界限及新 multiplicity 中的 K。

### G1：可识别性预检

**HOLD_DEFINITION_AND_IDENTIFIABILITY_TRIAL_REQUIRED。** A1/A2、共同 donor 支持、可信状态覆盖和共同组成重构尚未通过结果盲技术试跑。不得提前生成精确的组成贡献百分比或状态内疾病结论。

### 投稿与 WP4

- `HOLD_SUBMISSION`；
- `WP4 = HOLD_CONDITIONAL`；
- 不更新 GitHub Release、Zenodo、投稿包或结果型标题；
- 原 42/3,003 STAT2 数量/符号匹配低尾比例继续是后验诊断，不成为新 P 值。

## 6. 新增工具与复跑方法

新增：

- `audit_tools/rp_v3_stage0_01_freeze.py`
- `audit_tools/run_rp_v3_stage0.ps1`
- `audit_tools/test_rp_v3_stage0_freeze.py`

复跑命令：

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"
powershell -ExecutionPolicy Bypass -File .\audit_tools\run_rp_v3_stage0.ps1
C:\ProgramData\miniforge3\envs\sle-bcell\python.exe -m unittest -v audit_tools.test_rp_v3_stage0_freeze
```

入口脚本优先解析本轮 `inputs_readonly`，避免 PowerShell 5.1 对中文脚本字面量的编码问题，也避免依赖 Downloads。

## 7. 验证记录

- Stage 0 脚本完整执行：PASS；
- 新增回归测试：4/4 PASS；
- Python `py_compile`：PASS；
- `git diff --check`：PASS；
- 在相同项目内只读输入上再次执行后，9 个稳定输出 SHA-256 全部不变；
- 动态 `08_STAGE0_GATE_STATUS.json` 仅允许 `created_at` 更新，科学裁决和检查内容保持不变。

稳定输出包括输入清单、单位登记、时间线、目标量登记、分支登记、参数冻结、技术检查和导师级 Stage 0 复核报告。

## 8. 本轮产物

主输出目录：`phase17_v7/rp_v3_redesign/20261009_stage0/`

- `01_input_manifest.csv/json`
- `02_unit_registry.csv`
- `03_decision_chronology.csv`
- `04_estimand_registry.csv`
- `05_branch_registry.csv`
- `06_parameter_freeze.csv`
- `07_stage0_technical_checks.csv`
- `08_STAGE0_GATE_STATUS.json`
- `09_STAGE0_ADVISOR_REVIEW.md`
- `inputs_readonly/`
- `source_review/`（RP 渲染页、contact sheets 与 H5AD 结构检查）

## 9. 下一阶段目标

下一阶段固定为：

**`SCIENTIFIC_REDESIGN_STAGE0B_PROTOCOL_AND_MINIMAL_TRIAL`**

按以下顺序执行：

1. 固定 A1 连续轴计分合同，并从现有原始计数/准备脚本重建 A2 IFN-excluded 表征；
2. 在不查看新分支疾病效应的条件下固定共同 donor 集合、状态支持、`T0`、`T_frozen`、`T_rank` 和 `pi_ref`；
3. 只运行 RP v3 指定的五类技术原型：一个历史 contrast、一次身份重建、一个 donor-by-state 计数构造、一次冻结评分外推和四类最小模拟真值；
4. 根据技术失败率、量尺兼容性和共同支持重新裁决 G0/G1；
5. 只有 G0/G1 通过后，才允许全面执行 WP1-WP3。任何新 Figure 1-4 结果图均在此之后生成。

这一顺序优先回答“能否识别研究问题”，而不是优先寻找更显著的 IFN 结果。
