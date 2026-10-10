# RP v4 Stage E2 作者合同签署、Windows canonical pipeline 绑定与独立预检记录

**执行日期：** 2026-10-11（Asia/Hong_Kong）

**项目路径：** `H:\cuhk-2025fALL\6013RP-wyf`

**执行范围：** 仅限 synthetic-only G2C 执行前工程和治理门

**最终裁决：** `PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`

## 1. 本轮授权解释

用户明确回复“都批准”，本轮据此记录 Zhi Chen 和 Teng Qi 对下列冻结科学合同的批准：

1. 唯一 estimand 为 `delta_profile`；
2. 唯一方法为 donor-level OLS、HC3 influence variance 和双侧 `t(64)` 区间；
3. 固定 40 个 DGP、每个 4,000 次、总计 160,000 次；
4. 固定 seed base `2026101004`，终局 outer stage 141，truth stage 142；
5. 保留原 truth precision、bias、Wilson coverage、exact-null type-I 和数值失败门；
6. 不补抽、不删场景、不调阈值、不增加备用方法；
7. G2C 失败即关闭分解分支，不设置 G2D；
8. G2C 通过也不自动解锁真实 WP2、外部疾病结果、SRA 大下载、手稿或投稿。

这次批准发生在最终 Stage E2 代码提交之前，因此被严格拆成两层：

- 作者科学合同签署：本轮已完成；
- 对最终 Git commit 和代码 manifest 的 exact-code GO：本轮未签发。

因此，“都批准”没有被扩大解释为立即启动 `stage141/142`。

## 2. 输入与来源

### 2.1 外部 Stage E 包

- 文件：`SLE_RPv4_StageE_Preflight_20261011.zip`
- 大小：688,646 bytes
- SHA-256：`fe603e4d31031037428a3fa241678b7d5b14752d111fa739b317574215741e74`
- ZIP 条目：154
- CRC：PASS
- manifest 控制负载：153/153 大小和 SHA-256 PASS

外部包仅作为待复核证据输入，未直接视为项目授权。

### 2.2 仓库 authority

- Stage C estimand/method contract；
- Stage C 40-scenario DGP registry；
- Stage C final seed/compute contract；
- Stage D canonical technical freeze；
- calibration model；
- 历史 25 场景 `delta_profile` truth table；
- 当前 GitHub `main` 的 Stage D 基线。

## 3. 外部包独立复核

### 3.1 支持的结论

1. 外部 adjudicator 的 14/14 专项测试通过；
2. 15 个 shifted-DGP 的开发流 truth budget 全部达到 1% MCSE precision 门；
3. 最大 `MCSE / typical coefficient SE` 为 0.007754569；
4. 外部 gate 正确保留 `stage141_started=false` 和 `stage142_started=false`；
5. 旧 G2/G2B HOLD、真实 WP2、外部 outcome 和 SRA 下载均未被解锁。

### 3.2 Windows 独立数值复算

使用项目合格运行时 `D:\bioinfor\python.exe` 对全部 15 个 shifted-DGP 在 stage 131、每组 131,072、16 batches 下重算：

- 状态一致：15/15；
- 最大 truth 绝对差：0；
- 最大 truth MCSE 绝对差：`4.34e-19`；
- Windows 最大 `MCSE / typical SE`：0.007754569。

这证明外部 truth-budget 结果可以跨 Linux/Windows 数值复现，但仍只是 development-stage feasibility，不是 final truth 或 G2C 性能结果。

### 3.3 发现的真实缺陷

外部 `rpv4_stageE_preflight.py` 在 Windows canonical 运行时失败：

```text
UnicodeDecodeError: 'gbk' codec can't decode byte ...
```

原因是读取 CSV 时没有显式指定 UTF-8，Windows 使用 GBK 默认编码。外部 14/14 adjudicator 测试不覆盖该路径，因此不能原样晋升。

项目侧修复策略：

- 所有 CSV/JSON/JSONL 输入显式使用 UTF-8 或 UTF-8-SIG；
- 长路径 manifest 核验使用 Windows extended path；
- 外部 candidate defect 写入 canonical receipt，不隐藏失败；
- 重新执行完整 Windows preflight。

## 4. Canonical Stage E2 实现

新增工具：

- `audit_tools/rp_v4_stageE2_common.py`
- `audit_tools/rp_v4_stageE2_generator.py`
- `audit_tools/rp_v4_stageE2_truth.py`
- `audit_tools/rp_v4_stageE2_runner.py`
- `audit_tools/rp_v4_stageE2_adjudicator.py`
- `audit_tools/rp_v4_stageE2_adjudicate_run.py`
- `audit_tools/rp_v4_stageE2_preflight.py`
- `audit_tools/rp_v4_stageE2_freeze.py`
- `audit_tools/test_rp_v4_stageE2.py`
- `audit_tools/run_rp_v4_stageE2_preflight.ps1`

### 4.1 Outer runner

- 非终局资格流固定使用 stage 132；
- 终局流固定使用 stage 141；
- stage 141 必须提供新的 exact-code GO；
- final 模式固定 40 x 4,000；
- checkpoint 为每 100 attempts；
- 文件原子写入，已有输出默认拒绝覆盖；
- resume 必须通过 scenario、attempt ID、stage、seed、data kind 和安全字段复核；
- support stop 不补抽；
- numerical failure 被计数，不转成备用方法；
- runner 不执行结果裁决。

### 4.2 Independent truth runner

- 非终局资格流固定使用 stage 132；
- 终局 shifted truth 固定使用 stage 142；
- 使用独立 Philox stream，不导入 outer generator、HC3 kernel 或真实 outcome；
- 15 个 shifted-DGP 每组 131,072、16 batches；
- truth precision 不通过即停止，不追加 Monte Carlo 抽样；
- old 25 truth 只从已冻结历史 truth table 读取。

### 4.3 Adjudicator

逐 scenario 强制检查：

- 4,000 个连续且唯一的 attempt ID；
- scenario ID、scenario index、stage 141 和 seed base；
- `SIMULATED_ONLY`；
- 不得包含 donor/sample/patient/outcome linkage 字段；
- stopped/failed attempt 不得携带 fitted interval；
- truth precision 必须通过；
- numerical failure fraction 不超过 0.01；
- applicable scenario 的 supported attempts 不少于 274；
- normalized bias upper bound 不超过 0.10；
- Wilson coverage 区间完整落在 [0.925, 0.975]；
- exact-null Wilson type-I upper bound 不超过 0.075。

完整驱动器要求：

- 25 个历史 truth + 15 个 final stage-142 truth 恰好覆盖 40 scenarios；
- 30 个 applicable scenarios 全部 PASS；
- 10 个 mandatory boundary scenarios 全部完整报告且无超门数值失败；
- 输出 write-once；
- 即使 synthetic G2C PASS，也保持真实 outcome、SRA、手稿和投稿锁定。

### 4.4 Exact-code authorization

final token 同时验证：

- 新 GO receipt 的完整布尔合同；
- 两位作者姓名；
- GO 时间；
- 当前 Git HEAD；
- source-binding manifest SHA-256；
- manifest 内每个 code/contract/calibration/truth 文件的 size 和 SHA-256；
- 分别授权 stage 141 和 stage 142。

当前 `08_FULL_G2C_GO_TEMPLATE.json` 的所有执行字段均为 false，并且 commit 为空，因此 final runner 必须拒绝执行。

## 5. 验证结果

### 5.1 单元和拒绝测试

项目侧 15/15 PASS，覆盖：

- Stage E2 generator 与冻结 Stage D 算法的摘要一致性；
- truth batch 与冻结 stage-131 oracle 的一致性；
- wrong-purpose token 拒绝；
- final inputs 缺失拒绝；
- checkpoint resume；
- missing/duplicate attempts；
- real-data payload 拒绝；
- excessive numerical failure；
- truth precision failure；
- boundary reporting；
- Wilson reference；
- 40-scenario conjunction；
- stage-132 truth 冒充 final stage-142 的拒绝。

### 5.2 Windows stage-132 qualification

运行时：

- Python 3.13.7；
- NumPy 2.3.3；
- SciPy 1.16.2；
- statsmodels 0.14.6；
- Windows 11 build 26200。

Outer qualification：

- 场景：C0_X1、C1_X2、C2_X3；
- attempts：24；
- accounting SHA-256：`b4365e015f237f545b98984b695c5754c321189be0b02227194ca75bd8ae9dc8`；
- resume 与 fresh stable tree：一致；
- real effects：未拟合。

Truth qualification：

- 场景：C0_X1、C1_X2、C2_X3；
- 每组抽样：131,072；
- 3/3 precision PASS；
- 最大 `MCSE / typical SE`：0.005907134；
- stage：132；
- final：false。

### 5.3 Final namespace lock

- stage 141：未启动；
- stage 142：未启动；
- exact-code GO：false；
- real WP2：未加载；
- external outcome：未加载；
- SRA：未下载；
- manuscript/submission：未修改。

## 6. Canonical 交付

目录：`phase17_v7/rp_v4_redesign/20261011_stageE2_authorized_preflight/`

主要文件：

- `01_EXTERNAL_STAGE_E_RECEIPT.json`
- `02_AUTHOR_CONTRACT_SIGNOFF.json`
- `03_WINDOWS_RUNTIME_QUALIFICATION.json`
- `04_STAGE_E2_SOURCE_BINDING.csv`
- `05_STAGE_E2_QUALIFICATION_RECEIPT.json`
- `06_STAGE_E2_CHECKS.csv`
- `07_STAGE_E2_GATE_STATUS.json`
- `08_FULL_G2C_GO_TEMPLATE.json`
- `09_STAGE_E2_ADVISOR_REVIEW.md`
- `10_STAGE_F_GO_NO_GO_CONTRACT.md`
- `11_INTEGRITY_MANIFEST.csv`

Canonical integrity manifest 为 10/10 PASS。Source-binding manifest SHA-256：

```text
3941ec72ba39bc3ceedf64926fc4ffcbcd8f14e160155e0c68fc65f9e9abcbb0
```

## 7. 执行中断与修复记录

第一次 canonical freeze 在外部 payload exact-file 检查处停止，因为本轮新增的 Windows replay 文件和 Python `__pycache__` 被误归类为原 ZIP 负载。第二次仍因一个超过传统 Windows path limit 的 manifest 文件被 Python `Path.exists()` 误判缺失而停止。

修复：

- 原 ZIP 的条目完整性由 ZIP CRC + 154 条目检查负责；
- 153 个 manifest payload 使用 extended path 单独核验；
- 本轮追加的 replay 和运行缓存不冒充原包文件；
- 每次失败后使用新的工作目录重跑；
- 旧未提交 freeze 移入 Git 忽略的 `_software_tests`，没有删除证据。

第三次完整执行 PASS。上述失败没有触碰 final random stream 或 scientific result。

## 8. 科学判断

Stage E2 解决的是“能否在作者 Windows 主机上，按冻结代码安全启动一次独立终局模拟”的执行资格问题。它没有回答 G2C 是否具有合格 bias、coverage 或 type-I error。

当前仍成立：

- G2 HOLD；
- G2B HOLD；
- RP v3 的真实 WP2 分解不可声称；
- IFN/ISG 历史正结论不因本轮增强；
- identity、transfer 和 mechanistic ceilings 不变。

## 9. 下一阶段裁决

下一阶段为：

```text
RPV4_STAGE_F__POST_COMMIT_EXACT_CODE_GO_REVIEW
```

顺序固定：

1. 提交并同步本轮代码和 canonical receipts；
2. 在 clean Git HEAD 上重新核对 source-binding manifest；
3. 两位作者审阅并批准 exact commit + manifest SHA-256；
4. 另行创建新的 GO receipt，不修改历史 false template；
5. 再次运行 Windows preflight；
6. 只有 exact-code token 通过后，才可单独启动 full synthetic G2C。

在 Stage F GO 之前，不运行 160,000 次 outer simulation，不运行 final stage-142 truth，不下载 SRA，不计算真实疾病效应，不更新手稿或投稿包。
