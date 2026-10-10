# RP v3 G2B 全量执行、独立复裁与范围收缩行动记录

**日期：** 2026-10-10  
**父提交：** `256c0620e67f3e4218b3b898854e5dc302323916`  
**本轮决定：** `HOLD_G2B_APPLICABLE_DOMAIN`  
**范围决定：** `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`

## 1. 本轮目标

本轮从用户提供的 PowerShell 日志继续处理 G2B 全量计算。目标不是把
候选区间“救成 PASS”，而是：

1. 判断中断是否损坏已完成的 chunk；
2. 在不覆盖既有结果的条件下恢复运行；
3. 完成全部 25 个场景并独立复裁；
4. 按预先冻结的停止规则决定 WP2 是否解锁；
5. 生成紧凑、可入 Git 的正式裁决包和下一阶段合同。

本轮继续禁止读取真实 WP2 response、修改阈值、删除不利场景、改变
seed、开启 WP4、修改手稿图件或推进投稿/Release/Zenodo。

## 2. 中断诊断和恢复

失败点为：

```text
C1_R4 / chunk_1276_1300
Partial G2B chunk must be preserved and rerun elsewhere
```

检查时没有活动 Python 进程。该 chunk 目录存在但完全为空，说明进程在
创建目录后、写入 payload 前被中止；不是数值故障，也没有半写 CSV/JSON。

中断前的全量核查结果：

- 772 个 chunk 目录中 771 个完整、1 个空目录；
- 19,275 个 outer attempts 和 192,750 条 target rows 完整；
- 所有已完成 manifest/payload hash 与 stage-121 binding 一致；
- 所有 receipt 均为 `WP2_REAL_EFFECT_UNLOCK=false`。

恢复操作：

- 把空目录移动到本地 quarantine，未删除证据；
- 只复算 `C1_R4` 的 1276-1300 注册区间；
- 未覆盖任何已有 payload；
- 缺失区间返回 25/25 `INTERVAL_COMPUTED`；
- 随后从统一 PowerShell wrapper 恢复并完成全网格。

## 3. 全量运行结果

运行入口：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_rp_v3_g2b_full.ps1 `
  -Python D:\bioinfor\python.exe `
  -OutputRoot .\phase17_v7\rp_v3_redesign\g2b_full_runs\20261010_stage121_full `
  -Regimes R0,R1,R2,R3,R4 `
  -ChunkSize 25 `
  -Adjudicate
```

由于 wrapper 已在上一提交修正 PowerShell 参数归一化，上述逗号分隔调用
被正确解析为五个注册 regime。前置测试 30/30 PASS，进程正常退出。

完整性统计：

| 对象 | 结果 |
|---|---:|
| 场景 | 25/25 |
| 完整 chunks | 2,000/2,000 |
| partial chunks | 0 |
| outer attempts | 50,000 |
| target rows | 500,000 |
| interval computed | 30,056 |
| support stops | 19,944 |
| numerical failures | 0 |
| inner attempts/successes | 60,112,000 / 60,112,000 |
| canonical raw files | 6,004 |
| canonical raw size | 17,994,581 bytes |

独立复裁另生成 3 个文件；包含它们后的本地 run root 为 6,007 个文件、
18,077,293 bytes。

运行时为 `D:\bioinfor\python.exe`，Python 3.13.7、NumPy 2.3.3、
Windows 11 build 26200。真实 WP2 effect 未被读取或拟合。

## 4. 独立复裁

使用独立 adjudicator 对同一完整 run root 重新裁决。正式与独立输出的
三个文件逐字节一致：

| 文件 | SHA-256 |
|---|---|
| `01_G2B_ATTEMPT_ACCOUNTING.csv` | `45e1111aa2b5fefb42fc133c71f3b9c28ed915643a858e7c6ee5f381baa47002` |
| `02_G2B_TARGET_SCENARIO_ADJUDICATION.csv` | `eaac768a71b68ec4d13d487e9c06c09ef2fafe884da85a5b26d40324aa27f4f7` |
| `03_G2B_FINAL_DECISION.json` | `df0ec5859b5709762c95763d1cc9d5803758756097f5b905fee378a84760a3c1` |

## 5. G2B 科学裁决

适用域 R0/R2/R4 共 150 个 target-scenario 单元：

- 133 PASS，17 HOLD；
- 6 个 bias failures；
- 11 个 coverage failures；
- 1 个 exact-null type-I failure，与一个 coverage failure 重叠；
- 0 truth-precision failure；
- 0 numerical failure。

四个 target 在 15/15 场景通过：`beta_bin_1`、`beta_bin_5`、
`beta_S_cellref`、`beta_S_profile`。但是冻结合同要求十个 target 的完整
联合门，且正式 JSON 明确记录
`recommended_for_post_G2B_unlock_review=false`。因此不允许拆分解锁。

与 G2 相比，PASS 从 90/150 提升到 133/150，coverage failures 从 59
降到 11，说明 bootstrap-t/HC3 修订确实改善了原 percentile interval 的
系统性欠覆盖。但 `delta_profile` 从 8/15 降到 6/15，整体仍有 17 个
阻断单元，所以结果只能是：

```text
HOLD_G2B_APPLICABLE_DOMAIN
WP2_REAL_EFFECT_UNLOCK=false
```

G2B 没有改变 point estimator。独立 seed 下新增的 bias failures 不能写成
“区间方法造成”，也不能靠继续换 seed 消除；它们显示当前估计对象在冻结
场景中的 near-threshold 不稳定性。

## 6. 范围收缩

按照 RP v3 的预设 stop rule，本轮正式终止当前 WP2 区间方法开发：

```text
HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION
```

以下操作永久禁止于当前 WP2 分支：第三种 interval、门槛放宽、不利场景
删除、stage/seed 更换、target 子集择优、真实 disease effect 拟合，以及用
real-data P 值覆盖 simulation HOLD。

WP1 仍是有效的已完成结果。WP4 继续关闭。WP3 与 WP2 可分离，但 G2B
HOLD 不会自动解锁 WP3；只允许先做一个不看结果的增量知识 GO/NO-GO
预检，冻结 `T_frozen`、`T_rank`、biological unit、calibration、test family
和 stop rule。若 WP3 只能重复“IFN 仍为阳性”，则应停止当前 RP v3
扩展或重新定题，而不是继续增加队列救结果。

## 7. 文件治理

原始 2,000 个 chunk 保留在本地、由 `.gitignore` 排除。Git 只跟踪：

- 正式 accounting、250 条 adjudication 与 decision JSON；
- scenario/target/boundary/G2-G2B 汇总；
- run receipt、post-adjudication review、scope contract；
- 文件级 integrity manifest；
- 本行动记录及更新后的状态/README/复现说明。

这避免把 6,004 个 canonical 可再生文件提交到远端，同时保留足以审计最终
判断的完整紧凑证据。

## 8. 下一阶段

下一阶段固定为：

```text
RP_V3_SCOPE_CONTRACTION_AND_WP3_RESULT_BLIND_GO_NO_GO
```

只允许完成范围收缩决定、WP3 增量问题与 claim-owner map、结果盲的
eligibility/score/calibration 协议、effect-free dry run 和 GO/NO-GO。
在该门通过前，不运行真实 WP3，不重开 WP2/WP4，不修改手稿与投稿包。
