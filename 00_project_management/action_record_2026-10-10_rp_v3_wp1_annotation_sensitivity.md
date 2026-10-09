# RP v3 WP1 注释敏感性分析行动记录

**日期：** 2026-10-10
**阶段：** RP v3 Stage 1 / WP1
**最终裁决：** `PASS_WP1_TO_WP2_PREFIT_AND_G2_FREEZE`
**投稿状态：** `HOLD`
**WP4 状态：** `HOLD_CONDITIONAL`

## 1. 本轮目标与边界

本轮承接 Stage 0B 与外部独立复核，只回答一个限定问题：在相同供体、相同 T0 量尺和相同协变量设计下，历史 A0、连续身份轴/共同组成 A1、以及历史 strong-ISG-list-excluded A2 是否改变 managed-SLE 的 12 基因 IFN/ISG 系数。

本轮没有修改主文、主图、Supplementary Information、投稿包、GitHub Release 或 Zenodo；没有启动 WP2/WP3/WP4；没有设置等效界值或新增正式 P 值家族。

## 2. 输入与独立复核

独立复核工具包解压至：

`phase17_v7/rp_v3_redesign/20261010_independent_prefit_review`

外部复核指出的三项关键问题均被接受并正式处理：

1. A1 五个 bin 同时达到每 bin至少 30 个细胞的共同支持不是 89 人，而是 68 人。
2. A1 的线性表达重构与 log 后 score 加权不可交换，必须在首次效应拟合前选择算子。
3. A2 只排除了历史 strong-ISG 列表，仍保留 12 基因程序中的 `LY6E`，不得称为完全 IFN12 排除。

四个关键输入的 SHA-256 均与冻结合同一致：raw count H5AD、A0 表征 H5AD、历史 primary model matrix、A2 表征 H5AD。

## 3. prefit 工具验证与修复

### 3.1 单元测试

外部工具初次在 Downloads 中文路径执行 `unittest discover` 时发生路径导入解析失败。将工具复制到项目内 ASCII 工作路径后，21 项中 20 项通过；唯一失败来自 Windows 根相对路径的测试期望未调用 `.resolve()`。修正测试断言后 21/21 PASS。

增加无 LAPACK 设计秩检查及互补 dummy 共线测试后，最终外部/prefit 组件测试为 **23/23 PASS**。

### 3.2 Windows NumPy 原生异常

第一次和第二次真实 prefit 导出均在写完共同支持表后无 Python traceback 退出。使用 `-X faulthandler` 定位为当前 `sle-bcell` 环境中：

`numpy.linalg.matrix_rank -> SVD -> Windows fatal exception 0xc06d007f`

该故障发生在 68 x 5 设计矩阵秩检查，数据导出、映射和充分统计量此前均已完成。为避免变更已冻结科学环境，只将该小矩阵秩检查替换为确定性、带部分主元的高斯消元；新增测试后通过。

### 3.3 冻结设计纠正

外部 exporter 初稿错误地同时检查：

`intercept + is_managed + age_centered + ethnicity_asian + ethnicity_european`

在当前队列中 `ethnicity_asian + ethnicity_european = intercept`，因此秩为 4/5。查回 Gate C3/C4B 冻结合同后确认历史 primary-base 模型实际为：

`intercept + is_managed + age_centered + ethnicity_asian`

因此工具被纠正为继承原四列设计，最终秩为 **4/4**。这不是根据 WP1 效应删协变量，而是恢复历史冻结模型定义；纠正发生在首次 WP1 系数拟合前。

## 4. 疾病盲 prefit 结果

canonical prefit 目录：

`phase17_v7/rp_v3_redesign/20261010_wp1_prefit_freeze`

canonical prefit ZIP SHA-256：

`CA7B2B8310A8CB01C35564EAD3FC1B330FB9C461FE4E10987AEBA5DCCBE5D7A9`

主要结果：

- 原 primary 单位：89 名供体。
- A1 五 bin 均达到每 bin至少 30 个细胞：68 名供体。
- A2 至少 50 个映射 B_CONV 细胞未再排除这 68 人。
- 最终共同支持：68 名供体，31 controls、37 managed SLE。
- 共同设计：4/4 满秩。
- 原 43-control T0 参考保持不变。
- A2→A0 映射无平局、无 compartment collapse，五个 A2 cluster 均完成映射。
- A2 cluster 最低 reference-concordance purity：0.964688；该数值只表示相对 A0 scaffold 的一致性，不是生物学真值准确率。

prefit 最终合同目录：

`phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract`

合同在疾病系数拟合前记录 `first_effect_fit_time = NOT_STARTED`，并冻结以下内容：

- A1 算子：先对各 bin 用 full raw library total 计算线性 CPM，再以 `pi_ref` 重构共同组成表达，最后应用相同 `log2(CPM+0.5)` 和 43-control T0 标准化。
- A1 差值语义：joint identity-axis/common-composition standardization sensitivity。
- A2 支持阈值：每 donor stratum 至少 50 个映射 B_CONV 细胞。
- bootstrap：seed 20261010，2,000 次尝试，case/control 分层供体有放回抽样，三分支共享同一抽样，percentile 95% CI，失败不补抽，失败率超过 1% 则 HOLD。
- bootstrap 条件于固定 A2 mapping、A1 cutpoints、`pi_ref`、T0 和 68 人支持集，不代表全流程表征不确定性。

## 5. WP1 实际分析

分析脚本：

- `audit_tools/rp_v3_wp1_01_finalize_prefit.py`
- `audit_tools/rp_v3_wp1_02_fit_annotation_sensitivity.py`
- `audit_tools/rp_v3_wp1_03_review.py`
- `audit_tools/test_rp_v3_wp1.py`
- `audit_tools/run_rp_v3_wp1.ps1`

WP1 自建测试为 **6/6 PASS**。首次效应拟合仅在 prefit gate PASS 和测试完成后执行。

结果目录：

`phase17_v7/rp_v3_redesign/20261010_wp1_annotation_sensitivity`

### 5.1 同一 68 人下的三分支系数

| 目标量 | 估计值 | 2,000 次成对 bootstrap 95% CI |
|---|---:|---:|
| `beta_A0` | 1.037152 | 0.598263–1.477349 |
| `beta_A1` | 1.072077 | 0.630517–1.518759 |
| `beta_A2` | 1.037718 | 0.598753–1.477793 |
| `delta_beta_ann_A1 = A1 - A0` | 0.034925 | 0.013789–0.057130 |
| `delta_beta_ann_A2 = A2 - A0` | 0.000567 | 0.000000–0.001424 |

三分支 donor score 相关性：

- A1 vs A0 Pearson r = 0.999186。
- A2 vs A0 Pearson r = 0.999999。

2,000/2,000 bootstrap 均成功，0 次失败；所有重复设计秩均为 4。平均每个重复包含约 43.35 个不同供体，范围 34–52；这是有放回 cluster bootstrap 的预期现象，不是样本丢失。

### 5.2 科学解释

在已测试的三类表示和 68 人共同支持下，managed-SLE 的 IFN/ISG 系数方向和量级保持一致。A2 与 A0 几乎完全重合，说明历史 strong-ISG-list-excluded 身份学习分支没有实质改变该系数；但 A2 保留 `LY6E`，且本分析没有等效界值，因此不能写成“完全 IFN 独立”或“统计等效”。

A1 相对 A0 的增加约 0.035，数值小但 bootstrap 区间未跨零。由于 A1 同时改变身份表达与共同组成标准化，这一差值不能解释为纯注释误差、细胞内效应、因果机制或中介比例。它应被报告为一个小的联合敏感性偏移。

## 6. 最终核验

最终机器审计为 **11/11 PASS**：

- provisional gate、分析人群、冻结设计和 bootstrap 合同一致；
- 无正式 P 值或等效界值；
- 第一版 9 项完整性清单 9/9 哈希匹配；
- OLS 点估计独立复算最大误差 `6.25e-17`；
- 2,000 个 replicate ID 完整且全部满秩；
- bootstrap percentile 区间独立复算最大误差 `5.88e-17`；
- PNG/PDF 诊断图均存在并完成实际视觉检查。

最终裁决文件：

- `10_WP1_FINAL_AUDIT.csv`
- `11_WP1_FINAL_ADJUDICATION.json`
- `12_WP1_FINAL_ADJUDICATION.md`
- `13_WP1_FINAL_INTEGRITY_MANIFEST.csv`

## 7. 非 canonical 诊断目录

以下目录记录了修复前的中断或被替代运行，不用于科学结论：

- `20261010_wp1_prefit_export`
- `20261010_wp1_prefit_export_rerun`
- `20261010_wp1_prefit_export_final`

它们被保留作为运行事故与设计纠正的可追溯证据；canonical 对象仅为 `20261010_wp1_prefit_freeze`、`20261010_wp1_prefit_contract` 和 `20261010_wp1_annotation_sensitivity`。

## 8. 下一阶段裁决

下一阶段为：

**`WP2_PREFIT_IDENTIFIABILITY_AND_FULL_G2_SIMULATION_FREEZE`**

在任何 WP2 疾病效应拟合前，必须先冻结：

1. 可信状态或连续身份目标及其与 A1 的关系；
2. 组成坐标和闭合约束处理；
3. 未观测/低支持状态处理，禁止填零或按结果合并；
4. `beta_B`、共同组成 `beta_S` 和可估计状态内目标的兼容量尺；
5. 五个核心模拟场景及至少稀有性、深度、误标和 RNA 含量压力场景；
6. 非线性评分真值的独立大样本数值计算；
7. 2,000 次/场景的 Monte Carlo 指标、区间和 acceptance table。

通过 G2 后才能对相应 WP2 真实结果作层级解释。WP4、主文重写、主图替换、投稿包、GitHub Release、Zenodo 与投稿继续保持 HOLD。
