# RP v3｜Stage 0B 独立复核与 WP1 效应估计前审查

日期：2026-10-10
项目：SLE B-cell remodeling
收到的阶段：20261009_stage0b
本轮状态：**WP1_PRE_EFFECT_REVIEW_REQUIRED**
后续目标：**WP1_PRE_EFFECT_CONTRACT_ALIGNMENT_AND_PORTABLE_INPUT_EXPORT**

## 1. 执行结论

Stage 0B 已形成有价值的技术基础：最终 31 项完整性清单逐项匹配，A1 的 14 基因字典与冻结参数一致，A2 的 150,402 × 3,000 结构、有限 PCA/Harmony 坐标及 strong-ISG 标记排除能够在附件中核查。G0/G1 的原始状态文件被保留，不被本轮覆写。

但“技术许可进入 WP1”不等于“当前合同的统计对象已经没有歧义”。本轮发现：

1. A1 五箱各自有至少 72 名供体支持，但同时满足五箱均 ≥30 细胞者为 **68 名**，其余 **21 名**至少一箱不满足。68 只是尚未加入 A2 资格条件前的共同支持上限。
2. A2 的 strong-ISG 标记为零，但其冻结特征实际保留 IFN12 程序基因 **LY6E**。原 strong-list 排除事实成立；“全部 IFN12 排除”或“IFN 独立表征”则没有得到支持。
3. A1 分支已引入 `pi_ref` 标准化；它相对 A0 的系数差混合身份表示、组成/权重和可能的变换顺序影响，不应笼统称为纯注释效应。先混合线性表达后 T0 与先 T0 后加权必须明确区分。
4. 最终 `15_...` 清单 31/31 通过；较早 `01_...` 清单经过路径别名纠正后为 20 项匹配、5 项不匹配、2 项本地工程输入未打包。需要分清历史快照与最终清单，而非把两份清单均称为现行全通过。
5. 上传包缺少发现队列原始计数、A0 cell-level 参考以及 Stage 0B 项目生成器/原 6 项测试。不能在当前容器中据此完成真实三分支效应与 2,000 次配对 bootstrap。

这不是退回重新选题，也不是宣布 Stage 0B 科学失败；它是 WP1 第一次读取疾病系数前必须完成的对象级澄清。SUBMISSION=HOLD，WP4=HOLD_CONDITIONAL，完整 G2 尚未评估。

## 2. 本轮真实执行范围

### 2.1 输入身份

- 用户输入：`rp_v3_redesign.zip`。
- SHA-256：`A7C7C82D9FE55A48485EC9DE9FE08AC1DA1C0B698E3DFF967676738DFB6C5F1D`。
- ZIP：137 个条目，其中 120 个文件；展开字节 314,780,958；CRC 检查通过。
- 所有源文件解压到独立 received 目录；未运行输入包中的任意脚本。
- 原 RP v3、R4 投稿包和先前科学重评仅作为源文件/方法定义参照。
- GitHub 当前读取 main 仍定位于 `50e9855b8a3c4ddac53abe9986e8dc5ee51c51dc`。本轮不把该旧远端状态覆盖到更新的本地 Stage 0B。已通过连接器读取历史 C4 模型矩阵以确认其字段；没有获得可供本地逐字节核验的完整模型文件。原始 counts 在该提交的直接文件路径查询返回 404。

### 2.2 已执行与未执行

已执行：ZIP CRC；两份清单的路径规范化、字节长度与 SHA-256；HDF5 结构/细胞 ID/特征顺序/有限性；A1 字典及冻结 SD；IFN12 与 A1/A2 的逐基因交集；89×5 支持表重计；pi_ref 对自身计数列的算术复算；T0 参数结构；模拟汇总表的偏差、覆盖率与次数一致性检查。

未执行：原始细胞计数的全流程重建；A2 与 A0 的真实盲映射；ARI/NMI 独立重算；A1 150,402 个细胞评分从原 counts 重算；T0 43 对照均值/SD 从原 counts 重算；新疾病效应；外部病例—对照差异；bootstrap；完整模拟重跑；作者原 6 项测试；全仓回归。

新增审计共 38 个检查对象，36 个通过、2 个产生明确审阅观察：较早清单不一致，以及“全部 IFN12 排除”这一更强说法不成立。后一项不是原 strong-ISG 合同的失败，不应把它误写成 Stage 0B 2 项科学门未通过。

新增导出/审计组件测试 **21/21 PASS**；它们使用人工构造的小矩阵，不是作者原 6 项测试或生物学验证。只读审计重复执行两次，6 个最终审计结果文件均逐字节一致。这是确定性重复运行，不是第二种独立生物统计验证。

## 3. A1：逐箱支持与共同支持是两个不同问题

| A1 箱 | 满足 ≥30 细胞的供体 | 由原汇总表报告的 normal / managed |
|---|---:|---:|
| 1 | 72 | 33 / 39 |
| 2 | 78 | 36 / 42 |
| 3 | 84 | 40 / 44 |
| 4 | 85 | 41 / 44 |
| 5 | 83 | 40 / 43 |
| 五箱交集 | **68** | 当前本地尚未用完整 ID-linked design 独立核实 |

逐条读取 `08_A1_DONOR_BIN_SUPPORT.csv`，共 445 行，89 个 stratum、89 个 donor，恰好每人 5 箱。按原 ≥30 规则，21 人至少有一箱不支持。逐人、逐箱计数与剔除原因已输出 `A1_complete_support_membership.csv`。

因为 pi_ref 的五个权重均大于零，若 A1 的每人分数需要五箱的完整观测，则不能对缺箱者在剩余箱中各自重新归一化权重。那会使不同供体具有不同参考组成，也不能把缺箱值补零或在看完 β 后合箱。

建议把候选集合记作 U_A1，而不是立刻宣告最终 U0：

`U_A1 = 原 89 个 C4 单位 ∩ 五箱均满足 30 细胞`

`U* = U_A1 ∩ A0 资格 ∩ A2 资格 ∩ 完整且可识别的原协变量设计`

A0、A1、A2 的配对主比较均在同一个 U* 上重估。A0 的 89 人结果最多作为参考，不能与 A1 的 68 人结果直接相减当作注释效应。A2 的继承支持规则（例如广义 B_CONV ≥50）需要在执行附录里明确，而不是在得到效应之后选择。

U* 缩小不要求重新估计 T0。Stage 0B 的 43 个原对照及其 gene mean/SD 仍保持冻结；不能改用 U* 中剩余对照重新定标。pi_ref 也不因排除了部分供体而静默重选。

## 4. A2：保留历史分支，但准确标注排除范围

在 `03_A2_FROZEN_FEATURES.csv` 与 canonical HDF5 中均核实：3,000 个特征、strong-ISG flag=0、immunoglobulin flag=0；其与 `04_SCORE_CONTRACTS.json` 中 12 基因程序的交集却是 `LY6E`。

因此可以保留的表述是：**排除了冻结 strong-ISG 清单所标记特征的历史替代表征**。不能说完整 IFN12 被排除，也不能仅凭字面不重叠或少量重叠证明统计独立或去除了所有 IFN 生物学信息。

推荐保留当前 A2 文件和现有哈希，不直接删 LY6E 后覆盖成品。若作者明确需要“IFN12 完全排除”作为不同科学操纵，应另列新分支、在疾病效应前冻结特征和参数，并与旧 A2 同时报告；这不是本轮自动授权的新分支，也不应根据哪一个 β 更漂亮来选取。

A2 canonical final cluster sizes 为 97,405 / 45,489 / 5,486 / 1,331 / 691；它们是聚类数，不是已经完成的宽区室计数。不得把 A2 的 cluster 3 直接当作 A0 的 B_ASC cluster 3，必须按共同 cell ID 的重叠映射。

## 5. 归一化修复：应该按来源定义核实，而不是以 ARI 提高作为正确性证明

附件记录首次错误地在 3,000 特征内归一化；修复使用冻结的 16,357 基因背景计算分母，再截取 A2 特征。两者即使 feature list 相同，也具有不同的逐细胞缩放因子，故 PCA/Harmony/聚类改变在逻辑上并不意外。

但本轮只能核实最终 prepared/final 对象的哈希、结构与元数据；缺少 raw counts 和完整 16,357 背景选择生成器，不能独立证明每个分母都已逐值复现。ARI=0.795、NMI=0.680 在本轮保留为作者归档结果，不冒充本轮重算。正确修复的依据应是与历史定义一致，不是“较大的 ARI”。

尤其要分别记录三个不同背景：A2 身份学习的 16,357 背景；T0 的完整原始测量背景；T_rank 的 18,873 共同符号背景。不能因 A2 已修复，就在 T0 中误用同一个分母。新导出器会用原 30,172 特征全库总计重建 T0，并与冻结 43-control 参数比较；数值不一致则停止，不改写参考参数。

## 6. 最重要的协议问题：A1 相对 A0 的差异是什么？

A0 是广义 B_CONV 聚合，A2 改变相应成员归属；A1 却在连续身份轴上分箱，再按固定 pi_ref 标准化。因此 A1→A0 同时改变身份表示和组合/权重，不能无条件解释为“仅标签不同”的效果。

RP v3 §6/§9 明确区分 beta_B、beta_S、delta_beta_ann 与 delta_beta_comp，并要求正式共同组成对象在线性预测表达尺度上重构后再应用 T0。Stage 0B 的 WP1 合同写了“donor-level score standardized to pi_ref”，但没有将操作顺序写成公式或代码。

令 x_ik 表示供体 i、箱 k 的同尺度线性表达，T0 包含 log2(x+0.5)。两种算子是：

`score_first_i = sum_k pi_ref_k * T0(x_ik)`

`expression_first_i = T0(sum_k pi_ref_k * x_ik)`

它们一般不相等。一个不涉及任何患者的数值例子：x=(1,9) CPM、权重=(0.5,0.5)、示意的参考均值=0/SD=1。先评分后加权约为 1.91645，先加权后评分约为 2.45943。这个差异完全由变换顺序产生。

此外，广义 pseudobulk 的 RNA/library-size 加权并不自动等于按细胞比例加权；仅观察箱内归一化表达并加权，不自动识别每个细胞的直接效应。

必须在 β 解锁前作出一个可审计决定：

- 若采用“箱内评分后 pi_ref 加权”，将 beta_A1 明确定义为**固定组成的箱评分加权关联**，将 delta_A1 解释为表示/组成标准化联合对比；不能称为纯注释效应，也不能等同 RP v3 的预测表达重构 beta_S。
- 若目标是 RP v3 中的共同组成标准化表达，则需要冻结线性表达预测、测量深度约定、重构步骤与模型重拟合的 bootstrap。不能仅用一句文字替换就宣告已完成。

保留原 beta_A1/delta 字段以利追踪是可以的；但 semantic label、算子及数据对象必须同步。新导出器只输出两条后续路线都需要的原始计数充分对象，**不替作者决定算子**。

## 7. Bootstrap 与模拟的解释边界

原合同的 2,000 次配对供体聚类 bootstrap、共享抽样索引、失败率 >1% 停止、连续估计和区间优先均应保留。本轮没有运行该 bootstrap。

执行前需补齐：随机种子；非分层还是按研究组分层抽样；区间类型；一次重复如何判定失败；有效独立 donor 数与抽样重数的记录；任何秩亏/类别缺失不得静默丢弃或额外补抽掩盖失败率。供体被抽到两次，应重复其整个 cluster，而不是只标注为抽到一次；所有分支使用同一次抽样。

如果 A2 mapping、A1 cutpoints、pi_ref、T0 均固定，那么该 bootstrap 是**条件于这些冻结对象和共同支持集合的供体抽样不确定性**，并不包括重新学习表征或估计参考参数的不确定性。若另做全流程重学习，应分开命名，不混写为同一个 2,000 次结果。

没有解释性容许差异就不作等效性/非劣效性判断。“差值 CI 包含 0”不证明二者等效。两个点态 95% CI 也不是两个差值的联合 95% 区间；不报告新 p/q 时，保留 estimation-first 解释而非全家族显著性结论。

模拟汇总的 5 场景、每个汇总 400 次、最大 |bias|=0.00231454、覆盖 0.925–0.970、无报告的拟合失败，在算术上相符；但本轮没有 simulation generator 或 replicate-level 结果，未重跑真值生成过程。原合同明确将完整 G2 阈值留待后续，故技术试验通过不等于 G2。还需评价与真实 T0、A1 算子和缺箱支持规则一致的目标量，不能用线性状态参数替代对数评分真值。

## 8. 两层完整性清单与可移植性

最终 `15_STAGE0B_INTEGRITY_MANIFEST.csv` 的 31 项全部匹配，是当前 canonical 技术对象的有效核验。

较早 `01_STAGE0B_INPUT_AND_CONTRACT_MANIFEST.csv` 的 5 项不匹配为：A1 summary、A2 structural summary、Gate status、该清单自身，以及 final integrity manifest。其另两项 raw counts/A0 reference 指向本地工程，并不在上传包中；A2 prepared 的 root-qualified 路径别名已正确解析，不能误报为第三个缺失文件。

建议下一次生成导出专用、无自引用的 manifest；旧 01 原样保留为历史记录并声明角色，不能擦除差异。避免让一份清单同时承担“执行前输入”与“最终输出”两个时间身份。

约 82 MB 的 CPU diagnostic 和 legacy runtime 仍在附件中，但不在 final scientific 清单内；本轮没有将其升级为 canonical，也未删除或覆盖它。

本地 G0=PASS 与当前容器没有原始 counts/A0 并不矛盾：前者是作者机器上的输入恢复状态，后者是上传交付的范围。本轮不据此撤销 G0，但也不能把不存在于当前运行时的 H: 路径当成已读取文件。

## 9. 已交付的安全导出程序

`code/export_wp1_prefit.py` 应在有原始工程的本地运行。它：

- 验证原 counts、A0、C4 design、A2 及最终 Stage 0B 清单的固定哈希。
- 以 source_cell_index 唯一对齐三套细胞及供体/样本/文库/队列字段。
- 在解析 disease design 前按 cell overlap 冻结 A2→A0 宽区室映射；平局、缺类或不一致立即停止。
- 从原始 CSR 全基因计数计算分母，并聚合同名基因；重算 A1 以验证冻结矩与支持表。
- 输出 A0/A2 逐单位、A1 逐单位×箱的 12 基因 raw sums、全库总计和细胞数。
- 检查 T0 43-control 参数，不重新定标；输出候选共同支持、协变量秩和组别覆盖。
- 不决定 A1 加权算子，不拟合疾病系数，不运行 bootstrap，不打开 WP4/投稿。

代码已通过 21 项组件测试及语法检查，但没有在缺失的真实发现队列输入上完成端到端执行。遇到 schema、浮点数或哈希不一致会输出 HOLD 诊断，不能直接修改冻结参数以让代码通过。

这是原始全库分母保留的充分计数导出，不是用去 IFN 特征的 3,000 维表达矩阵冒充原 counts。后续真值和模型审查仍需保留原工程；便携导出不等于未来所有 WP2 模型都能只靠 12 个基因完成。

## 10. 下一阶段与停止条件

继续推进 WP1 的来源级准备，不进入主文/主图/投稿包修改。最近一步只关闭四件事：

1. 明确 A1 实际算子及 delta_A1 的联合对比身份。
2. 明确 A2 仅是 strong-list exclusion，保留 LY6E 的来源事实；如新增完全排除分支则独立冻结，不能替换旧分支。
3. 完成 A2 盲映射后，以 ID-linked design 冻结最终 U*、每组供体数和协变量可识别性。
4. 补齐 bootstrap 运行规格并取得经验证的原始或充分计数输入。

通过后才进入 beta_A0/beta_A1/beta_A2、两个配对差值及 2,000 次条件 bootstrap。不得根据效应方向改变分箱、阈值、参考人群、缺失处理或映射器。

**本轮疾病效应数=0；真实 bootstrap 次数=0；原手稿、主图、Source Data、投稿包、GitHub、Release、Zenodo 均未改动。**

## 来源索引

S1：上传包 `20261009_stage0b/01_STAGE0B_PROTOCOL_FREEZE.md` 及 02–06 合同。

S2：同目录 `07_A1_SCORE_TECHNICAL_SUMMARY.json`、`08_A1_DONOR_BIN_SUPPORT.csv`、`08_A1_BIN_SUPPORT_SUMMARY.csv`、`09_PI_REF.csv`、`11_T0_FROZEN_REFERENCE_PARAMETERS.csv`。

S3：`03_A2_FROZEN_FEATURES.csv`、`a2_rebuild/03_a2_prepared.h5ad`、`a2_rebuild/08_isg_excluded_representation.h5ad`、16_IMPLEMENTATION_INCIDENTS。

S4：`13_SIMULATION_TECHNICAL_RESULTS.csv`、`14_STAGE0B_GATE_STATUS.json`、`17_WP1_ANNOTATION_SENSITIVITY_EXECUTION_CONTRACT.md`。

S5：`15_STAGE0B_INTEGRITY_MANIFEST.csv`、`01_STAGE0B_INPUT_AND_CONTRACT_MANIFEST.csv`、Stage0 input manifest。

S6：RP v3 §6、§8、§9、§11，尤其线性预测表达重构后应用 T0 的要求；由 Files 原文检索核对，不以先前摘要代替。

D1：本包 `audit/manifest_verification.csv`、`identity_IFN_overlap_audit.csv`、`A1_complete_support_membership.csv`、`independent_checks.csv`、`independent_status.json`。

D2：新增组件测试记录及重复执行结果；不冒称作者原 6 项测试或完整 G2。
