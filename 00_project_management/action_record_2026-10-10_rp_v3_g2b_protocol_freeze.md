# RP v3 G2B 单一方法整合、Windows 复核与前瞻冻结行动记录

**日期：** 2026-10-10
**父提交：** `e8265cefa5124b36e29f9acdf8ef6fe7bfe7e8a1`
**输入包：** `SLE_RPv3_G2_HOLD_Diagnostic_Single_G2B_Candidate_20261010.zip`
**输入包 SHA-256：** `8db6ac265f013cf7fb7208a85f05141015f26f4ce33dcc5db9bb8f437fea03d6`
**本轮决定：** `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`

## 1. 本轮目标和禁止事项

按照 RP v3 的 `RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`，本轮不直接
接受外部包结论，而是独立检查唯一 G2B 候选能否进入项目 canonical
命名空间并形成完整执行合同。

本轮允许：

- 核验外部包清单、代码、方法、合成开发和来源；
- 在 Windows canonical Python 中重跑测试、开发网格和独立数值对照；
- 只整合一个事先选择的 HC3 bootstrap-t 区间；
- 建立新的 stage 121 runner、独立 adjudicator、测试和恢复脚本；
- 冻结完整 G2B 前瞻合同。

本轮禁止：

- 读取或拟合真实 WP2 disease response；
- 修改原 G2 generator、point estimator、truth、target、scenario 或门槛；
- 删除 R1/R3、覆盖失败或单个 bias failure；
- 覆写原 G2 HOLD 或把技术资格写成覆盖率 PASS；
- 修改手稿、图件、投稿包、Release 或 Zenodo。

## 2. 外部包全量核验

ZIP 为 65,473,733 bytes，含 902 个文件条目和单一根目录。未发现路径
穿越、重复路径或 CRC 错误。`MANIFEST.csv` 注册的 901 个 payload 全部
通过文件存在性、字节数和 SHA-256 复核。

包内状态没有伪装成正式 G2B：

- 原 G2 保持 `HOLD_G2_APPLICABLE_DOMAIN`；
- `G2B=NOT_RUN`；
- `approved_for_full_G2B_execution=false`；
- formal runner 和 adjudicator 哈希为空；
- `WP2_REAL_EFFECT_UNLOCK=false`。

候选包冻结的 parent generator、estimator、calibration model、truth table、
target/scenario/acceptance registries 与当前仓库逐哈希一致。最关键的七项
SHA-256 均与 canonical G2 合同一致；因此候选不是在另一个 DGP、真值或
门槛上开发。

## 3. G2 HOLD 诊断的接受范围

外部诊断正确区分了三个对象：

1. 59/150 applicable target-scenario cells 的 coverage failure；
2. `C0_R4 / beta_bin_3` 的唯一 bias-gate failure；
3. R1/R3 的支持/误标边界。

区间更换只能研究第一项，不能修复第二项，也不能把第三项转换为适用域。
原 G2 的 60 个 applicable HOLD 永久保留为 percentile 方法的正式证据。

本轮核实两篇方法依据的 DOI 和出版来源：Hall 1988 支持研究学生化
bootstrap 区间的高阶性质；MacKinnon–White 1985 支持有限样本 HC 方差
修正。两篇论文均不能替代当前 empirical-template DGP 的完整验证。

## 4. 唯一方法候选

唯一候选为病例/对照分层、配对供体 pairs bootstrap-t，使用 HC3
studentizer：

```text
t*_bj = (beta*_bj - beta_hat_j) / se*_HC3,bj
CI_j  = [beta_hat_j - q_0.975(t*) se_HC3,j,
         beta_hat_j - q_0.025(t*) se_HC3,j]
```

点估计仍是原四列 OLS disease coefficient。十个目标共享同一个内层抽样
成功掩码；delta target 对成对 response difference 计算自己的 HC3 SE。
重复抽到的 donor 按显式展开行解释，频数权重 meat 使用 `w_i` 而不是
`w_i^2`，也不按 donor ID 再做 cluster sandwich。

数值保护保持前瞻固定：2,000 次内层，不补抽；非有限、秩不足、活动
leverage 大于等于 `1-1e-10` 或 SE 小于等于 `1e-12` 使共享 draw 失败；
失败超过 20 次时该 outer object fail closed，不给 normal/t fallback。

## 5. Windows 独立复核

运行时：

- `D:\bioinfor\python.exe`；
- Python 3.13.7；
- NumPy 2.3.3；
- pandas 2.3.3；
- SciPy 1.16.2；
- statsmodels 0.14.6；
- BLAS/OMP/MKL/NUMEXPR threads 固定为 1。

结果：

| 核验 | 结果 |
|---|---:|
| 外部包 verifier | 901/901 PASS |
| 外部候选 tests | 42/42 PASS |
| Windows development replay | 150/150 outer accounted |
| 支持/停止 | 90 intervals / 60 support stops |
| development inner attempts | 180,000 |
| inner numerical failures | 0 |
| resume 新增对象 | 0 |
| 独立 expanded-row statsmodels fits | 4,500/4,500 PASS |
| 最大 coefficient error | `1.47e-14` |
| 最大 HC3 SE error | `4.00e-15` |

Linux 与 Windows 开发输出的 150 个状态完全一致；counts、cells、design、
templates 在 150/150 精确一致，bootstrap indices 和 success masks 在
90/90 精确一致。最大 response 差 `8.88e-16`，最大 bootstrap coefficient
差 `3.11e-15`，最大 interval endpoint 差 `2.66e-15`。

这些结果是实现可移植性证据，不是覆盖率验证，也不是新的独立生物样本。

## 6. 项目侧实现

新增而不修改原 G2：

- `audit_tools/rp_v3_g2b_studentized.py`：唯一 HC3 bootstrap-t kernel；
- `audit_tools/rp_v3_g2b_full_runner.py`：stage 121、chunked、resumable runner；
- `audit_tools/rp_v3_g2b_adjudicate.py`：独立应用原 G2 验收规则；
- `audit_tools/test_rp_v3_g2b.py`：20 项项目集成与故障测试；
- `audit_tools/run_rp_v3_g2b_full.ps1`：validate-only、全量执行与 adjudication；
- `phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/`：方法、合同、
  Windows receipt、advisor review 和 runbook。

canonical kernel 对外部候选作了一项不改变统计结果的工程修复：当故障
注入使全部 2,000 个 bootstrap draw 无效时，`max_bootstrap_leverage`
明确返回 `null`，不再触发 `All-NaN slice` RuntimeWarning。新增测试要求
该路径无 warning、无 fallback、interval 全 NaN 且 gate 为 HOLD。

## 7. 合同和测试

正式 binding：

```text
ce40a673df8c051e4eb7036292fe5827eb6ce8b552ee56964affc61d1fa25d0c
```

它绑定 generator、parent estimator、G2B kernel、full runner、独立
adjudicator、calibration model、truth、domain policy、三个 registries 和
方法规范。stage 固定为 121，outer seed base 固定为 2026101002。

项目内 58/58 tests PASS，覆盖 Stage 0、Stage 0B、WP1、WP2 preflight、
原 G2 和新 G2B。G2B 的 20 项测试包括：

- parent estimator 字节冻结；
- stage 121 可重复且与 21/41 不同；
- point/bootstrap coefficients 与原 estimator 一致；
- explicit expanded-row HC3 对照；
- paired delta studentizer；
- inverse quantile 公式；
- real response 拒绝；
- old binding 和非空未绑定目录拒绝；
- 原/new adjudicator 规则等价；
- R1/R3 boundary 永不转 PASS；
- 所有 registry 哈希不变。

PowerShell `-ValidateOnly` 入口再次通过 30/30 parent-G2 + G2B tests，并
确认没有写 outer attempt。

## 8. 本轮裁决

可以把唯一候选提升为前瞻冻结的 G2B 协议；不能把它写成 G2B PASS。

```text
original G2: HOLD_G2_APPLICABLE_DOMAIN
G2B: NOT_RUN
current gate: PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED
WP2_REAL_EFFECT_UNLOCK: false
WP4: HOLD_CONDITIONAL
submission: HOLD
```

## 9. 下一阶段

下一阶段为：

```text
G2B_FULL_SYNTHETIC_EXECUTION_AND_INDEPENDENT_ADJUDICATION
```

应一次性执行全部 25 scenarios × 2,000 outer attempts；每个 supported
outer object 固定 2,000 paired inner draws。R0/R2/R4 进入适用域 conjunction，
R1/R3 继续完整报告但不改域。完整 G2B 完成后必须先运行 bound adjudicator，
再作独立 post-G2B review。

若 G2B PASS，只能产生 unlock review recommendation，真实效应不会自动
运行。若 G2B HOLD，必须停止 interval-method 开发，进入
`HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`；不得再试第二种区间、
换 seed、调 threshold 或删 scenario。

详细命令见：
`phase17_v7/rp_v3_redesign/20261010_g2b_protocol_freeze/06_G2B_FULL_RUN_RUNBOOK.md`。

## 10. 未发生的工作

本轮没有运行 full G2B，没有计算真实 WP2 disease coefficient，没有修改
manuscript、figures、submission package、GitHub Release 或 Zenodo。没有
删除、覆盖或重命名原 full-G2 结果。
