# RP v3 WP2 效应前预检与 G2 执行锁审查行动记录

**日期：** 2026-10-10
**执行范围：** WP1 独立复算复核、真实本地 WP2 无效应结构预检、目标/情景/验收注册表冻结、G2 执行锁缺口审查
**最终裁决：** `PASS_WP2_EFFECT_FREE_PREFLIGHT__HOLD_G2_EXECUTION_IMPLEMENTATION_REQUIRED`

## 1. 本轮原则

本轮没有把外部候选包的 PASS 标签直接转成项目结论。所有判断均区分：

1. 候选包已经完成的供体评分层 WP1 复算；
2. 本轮在完整本地 canonical 充分统计量上新完成的 effect-free preflight；
3. 已冻结但尚未执行的 G2 目标、情景和验收表；
4. 尚未实现、因此不能伪装成已冻结的模拟生成器与独立真值引擎；
5. 明确禁止查看的 WP2 新疾病效应。

主文、主补图、投稿包、GitHub Release、Zenodo 和 WP4 均未打开。

## 2. 输入与候选包核查

接收文件：
`SLE_RPv3_WP1复算_WP2预检与G2协议候选_20261010.zip`。

- 文件大小：331,915 bytes；
- SHA-256：`F83361BB57C94641CC51E6C1B3DFF06CC4F07E871CBA1F43569CBDCAA3806B6F`；
- ZIP 内容清单与 CRC 可读；
- 包内 verifier 重新执行后为 `47/47 manifested payloads verified`；
- 包内 39 项组件和合成集成测试在本机重新执行为 `39/39 PASS`；
- 包含两次相同种子的 WP1 独立复算、effect-free preflight 工具和 25 单元 G2 协议候选；
- 不包含完整 G2 生成器、独立真值实现、真实本地 preflight 结果或完整 G2 运行结果。

收到的解包树保留在本地
`phase17_v7/rp_v3_redesign/20261010_wp2_external_candidate/`，仅作为外部审阅输入，已 Git-ignore；项目侧脚本与 canonical gate 才是后续权威对象。

## 3. WP1 独立复算复核

从 Git-verified 的供体评分和冻结设计重新执行 OLS 与 2,000 次分层配对供体 bootstrap：

- 68 名唯一供体，31 controls、37 source-defined managed SLE；
- 设计秩 4/4；
- 2,000 次尝试、2,000 次成功、0 次替补；
- 与 canonical 结果的最大数值误差 `6.66e-16`；
- 66/68 名供体的 A2 与 A0 评分完全相同；
- 仅两名 managed-SLE 供体发生 A2 评分变化；
- 244/2,000 次 bootstrap 同时遗漏这两名供体，精确对应 244 次零差值。

因此，A2 的近零差异来自当前共同支持集上的稀疏实际扰动，不是统计等效证明，也不能外推为任意合理注释均不影响结果。A1 相对 A0 的小幅正向偏移仍应称为联合身份轴/固定 profile-mixture 敏感性，而非纯组成效应或中介效应。

## 4. 真实本地 effect-free preflight

正式项目脚本：

- `audit_tools/rp_v3_wp2_kernels.py`；
- `audit_tools/rp_v3_wp2_01_effect_free_prefit.py`；
- `audit_tools/rp_v3_wp2_02_review_prefit.py`；
- `audit_tools/run_rp_v3_wp2_prefit.ps1`；
- `audit_tools/test_rp_v3_wp2_prefit.py`。

canonical 输出：
`phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/`。

外部脚本和项目侧脚本生成的 `01_geometry_no_disease_effect.csv`、`02_fixed_composition_coordinates.csv` 与 `04_PREFIT_STATUS.json` 字节级一致；项目侧 `03_input_verification.csv` 额外记录了 bytes 字段，因此其哈希按预期不同。

### 4.1 支持和闭合

- 68/68 名供体均具有五个 A1 箱；
- 最低 donor-bin 细胞数为 30；
- A1 逐箱 12 基因原始计数之和精确回收 A0；
- A1 逐箱 full captured-library totals 之和精确回收 A0；
- A1 逐箱细胞数之和精确回收 A0；
- 捕获 UMI 权重重构 pooled CPM 的最大绝对误差为 `1.1369e-13`。

### 4.2 组成测量几何

对供体 i、箱 k：

- `p_cell = n_ik / sum(n_i)`；
- `q_UMI = L_ik / sum(L_i)`；
- `m_ikg = 1e6 * C_ikg / L_ik`；
- pooled CPM 精确满足 `sum_k q_UMI,ik * m_ikg`，一般不等于 `sum_k p_cell,ik * m_ikg`。

实测无分组诊断显示：

- `median |p_cell - q_UMI| = 0.0159536`；
- `max |p_cell - q_UMI| = 0.0932746`。

因此，“固定细胞比例”和“固定相对表达 profile 混合权重”不能使用同一个名称。新增桥接目标 `beta_S_cellref` 固定细胞参考比例，同时保留每供体每箱观察到的 captured UMI/cell；它仍同时包含生物学 RNA 输出和技术捕获效率，不能称作绝对 RNA/cell 或直接因果效应。

### 4.3 组成闭合与设计秩

- 基础设计：4/4 满秩；
- 截距、基础设计和五个 raw fractions：8/9，符合闭合冗余；
- 基础设计和四个冻结 Helmert-ILR 坐标：8/8 满秩；
- 没有自动伪计数、补零、合箱或依据效应删除坐标。

本结果只说明可计算性，不消除未测混杂、疾病引起的组成变化或条件化偏倚。

## 5. 冻结的 G2 注册对象

在任何 G2 结果出现前，现已冻结：

- 11 项目标注册，包括 WP1 数学别名、`beta_S_cellref`、五个轴区间目标和单独管理的可选 ILR 条件诊断；
- 25 个情景单元：C0 null、C1 composition-only、C2 within-bin-only、C3 同向、C4 反向，分别与 baseline、rarity、depth、adjacent mislabel 和 RNA/capture stress 交叉；
- 每单元 2,000 次外层尝试及 2,000 次配对 bootstrap；
- bias、coverage、true-null type-I、数值失败、truth precision 与完整 attempt accounting 的 fail-closed 验收规则；
- 外层 seed `2026101002` 与真值 seed `2026101003`。

这些阈值是本项目运行容差，不是生物学等效界值，也不是通用方法学标准。R0 是必需核心域；R1-R4 必须分别报告，不能用平均通过率掩盖失败范围。

## 6. 为什么 G2 仍然 HOLD

项目侧已绑定：

- prefit receipt；
- A1 sufficient raw counts；
- cell mapping/A1 branch assignment；
- result-blind geometry calibration；
- Python/NumPy/pandas/BLAS runtime receipt；
- target、scenario 和 acceptance registries。

`10_G2_IMPLEMENTATION_CONTRACT.json` 仍准确保留三个空哈希：

1. `simulation_generator_sha256`；
2. `independent_truth_code_sha256`；
3. `truth_receipt_sha256`。

所以当前不能写成 `G2 execution frozen`，也不能计算或解释新的 WP2 疾病效应。这个 HOLD 是正确的质量控制结果，不是分析失败。

## 7. 验证结果

- 外部 bundle manifest：47/47 PASS；
- 外部组件/合成集成测试：39/39 PASS；
- 项目侧 WP2 聚焦测试：12/12 PASS；
- Stage 0、Stage 0B、WP1、WP2 项目侧联合回归：28/28 PASS；
- canonical integrity manifest：13/13 文件大小与 SHA-256 PASS；
- canonical final audit：全部检查 PASS；
- 项目侧 preflight 没有输出疾病系数、分组表达均值或新 IFN 分数；
- `WP2_REAL_EFFECT_UNLOCK=false`；
- `G2=NOT_RUN`。

测试过程中发现的两个失败均属于测试期望本身：Wilson 零事件下界的机器浮点舍入，以及一个合成闭合矩阵的预期秩误写。修正测试后全部通过；真实 preflight 数值与 Gate 未改变。

## 8. 当前科学判断

WP1 的条件性表示稳健性可复现。WP2 preflight 进一步证明当前数据结构足以区分 cell fraction、captured-UMI fraction 和固定 profile mixture 这三个测量对象，并允许建立四维 ILR 条件诊断。它尚未证明组成不影响 IFN 关联，更没有证明 cell-intrinsic、介导或因果效应。

## 9. 下一阶段

下一阶段固定为：

`G2_GENERATOR_TRUTH_ENGINE_AND_TECHNICAL_PILOT`

必须完成：

1. 以 donor x bin sufficient counts 为生成层，保留 full-background denominator、供体相关和基因相关；
2. 独立实现非线性 `raw counts -> full-background CPM -> T0` 真值程序；
3. 证明生成器与真值实现不互相调用待评估拟合输出；
4. 实现实际的 2,000 次配对 bootstrap 区间，而不是用 HC3 冒充；
5. 运行小规模非裁决 technical pilot，验证 attempt accounting、支持停止、随机流、断点续跑和资源需求；
6. 只有 truth precision 与 pilot 均通过后，补齐三个哈希并批准 full G2 execution。

在 applicable G2 domain 通过之前，WP2 新疾病效应、WP4、手稿/图片替换、投稿包、Release 和 Zenodo 均继续 HOLD。
