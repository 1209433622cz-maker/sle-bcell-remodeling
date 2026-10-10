# RP v3 WP3 结果盲数据预检、算子核验与有限测量范围冻结行动记录

**日期：** 2026-10-10
**父提交：** `dc0972a0e47d24d1b94e4ce9253070bdd0d1848a`
**输入包：** `SLE_RPv3_G2B_FullAudit_ScopeContraction_WP3_Prefit_20261010.zip`
**输入包 SHA-256：** `50edf874db3446058ae6507cff25bd55618814309fc815c3f2bf7f1b7e0ef38c`
**本轮决定：** `PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION`

## 1. 本轮目的

本轮只核查 G2B 后的范围收缩与 WP3 结果盲数据预检，不接受外部包标签
作为 canonical 决定。允许检查输入身份、供体支持、计数闭合、冻结基因/
背景与源评分算子；禁止生成疾病组表达汇总、真实疾病系数、置信区间、
P 值、ROC 或机制结论。

## 2. 外部包核查

ZIP 含 12,189 个条目、解压后 52,724,494 bytes；未发现路径穿越或重复
路径。包内 manifest 为 12,188/12,188 PASS。按 README 正确入口运行测试
后为 20/20 PASS。

包中绝大多数内容是 G2/G2B 的 4,000 个 chunk 和已有输入快照，因此整个
解包目录作为本地审计缓存保留并排除于 Git。项目侧只重建必要的 prefit
代码、紧凑结果和合同。

## 3. 输入身份复核

候选 `input_receipts.csv` 登记的 22 个文件全部与当前本地 canonical 文件
逐字节一致，包括：

- Stage 0B external sufficient counts、row metadata 和 gene universe；
- score contract、18,873-symbol rank background 和 43-control reference；
- 五个历史 sanitized design matrices；
- 带 sample ID 的 43-donor childhood design。

外部 NPZ 为 672 行乘 32,738 特征，4,537,683 个存储非零项。672 行包含
多个表示，不是 672 个供体。实际为 56 个样本和 56 个唯一 donor。

## 4. 可移植性复核

候选 verifier 为 12,188/12,188 PASS。独立 Windows 重跑候选 effect-free
audit 时，10 个输出中 8 个逐字节一致；`input_receipts.csv` 因 POSIX/Windows
路径分隔符和排序不同、`PREFLIGHT_RECEIPT.json` 因 LF/CRLF 不同而字节
不同。归一化路径/排序后 22 个 receipt 行完全一致，两个 JSON 语义完全
一致。

因此候选的科学结果可复现，但“10/10 byte-identical”只对其同平台双目录
重跑成立，不能直接写成跨平台字节同一。项目侧实现固定了 POSIX 相对
路径、排序和 LF 输出。

## 5. 项目侧实现和检查

新增：

- `audit_tools/rp_v3_wp3_01_effect_free_prefit.py`；
- `audit_tools/test_rp_v3_wp3_effect_free_prefit.py`；
- `audit_tools/run_rp_v3_wp3_effect_free_prefit.ps1`；
- `phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit/`。

项目测试 9/9 PASS，real-input checks 22/22 PASS。核心结果：

| 对象 | 结果 |
|---|---:|
| 源样本/唯一供体 | 56/56 |
| 八标签到 B_CONV count/cell closure | 56/56 |
| min50 合格供体 | 54 |
| 儿童主集合 | 43（11 HC、32 SLE） |
| 成人 min50 | 11/12 |
| IFN program coverage | 12/12 |
| frozen rank background | 18,873/18,873 |
| 已验证协变量 | 仅 intercept + is_sle；年龄、性别、祖源、治疗、活动和 batch 均未在当前 ID-linked design 中核实 |

两名成人仅有 metadata、无源矩阵，不补造；另两名供体低于冻结 50-cell
门槛。该预检从已归档 sufficient counts 开始，没有重新从 RAW TAR/barcode
构建矩阵，也没有重开失败的 source-label-independent mapper。

在第二个全新输出目录重跑项目侧工具后，10/10 个 machine-produced 文件
逐字节一致，确认固定路径、排序和换行后的 Windows 可重复性。

## 6. 评分算子身份

候选协议把 percentile 约定列为待确认。本轮已直接定位并测试 Stage 0B
源实现：

```text
scipy.stats.rankdata(method="average") / M
```

其中 M 为固定 18,873-symbol background。合成 ties/zeros 对照与源函数精确
一致。`T_frozen` 仍使用全部测量特征的库总计、`log2(CPM+0.5)` 和原 43
个 discovery A0 controls 的固定均值/总体 SD。

Stage 0B 已经在不做疾病组汇总的前提下证明 54 个外部 `T_frozen/T_rank`
均有限。因此本轮不能宣传“首次计算可行性”；新增价值是 donor linkage、
闭合、完整输入 hash、协变量缺口和项目侧 fail-closed 边界。

## 7. 科学裁决

本轮 PASS 只表示对象、支持、闭合、feature coverage 和源算子可用。它不
表示跨平台量尺等价、临床校准或不确定性方案通过，也不授权真实 WP3
disease outcome。

```text
WP2 current branch: CLOSED
WP3 available-object prefit: PASS
WP3 score/outcome inference: HOLD
WP4: HOLD_CONDITIONAL
manuscript/submission/release/Zenodo: HOLD
```

## 8. 下一阶段

唯一允许的下一阶段为：

```text
WP3_EFFECT_FREE_MEASUREMENT_SENSITIVITY_PROTOCOL_AND_DRY_RUN
```

只允许在 54 个合格对象上、不使用疾病/年龄分层地描述 `T_frozen` 与
`T_rank` 的 pooled rank concordance、leave-one-gene-out 稳定性、检测率和
gene contribution。不得输出组均值、疾病效应、区间、P 值或选择更有利的
评分。若该步骤不能增加超出 Stage 0B 可计算性和旧 IFN 复现的解释信息，
则关闭或重新定题 RP v3，不再扩增方法、基因集或队列。
