# GitHub 目录重构与科学候选同步行动记录

日期：2026-10-12；工作区：`H:/cuhk-2025fALL/6013RP-wyf`。

## 1. 本轮任务与权限边界

用户要求依据已整理的本地结果和论文状态，重构并推送 GitHub，至少包含截图中的八个主目录。本轮操作对象是现有公开仓库 `1209433622cz-maker/sle-bcell-remodeling` 的 `main`，不是再次删除仓库、重新创建仓库、发布 Release、更新 Zenodo 或正式投稿。

开始时本地与远端均为 `9840b159651c0622aee63ae6668394b4fc9de0c9`，没有双方独有提交。本轮保护既有分析路径、作者批准基线、历史负面裁决和投稿包，不将上一轮科学候选自动升级为 canonical。

## 2. 目录重构的实际实现

| 主目录 | 内容与用途 |
|---|---|
| `0_admin` | 权威入口、状态、引用信息、公开范围政策、Git 文件索引和精选资产完整性清单 |
| `1_data` | 数据取得说明、输入清单和元数据/设计入口；不上传大型表达矩阵或 SRA reads |
| `2_code` | 分析代码导航、环境说明、可独立运行的标准库校验工具和安全性测试 |
| `3_results` | 现行结果和 Gate、29 条可回溯关键结果；保留数值单位与解释边界 |
| `4_figures` | Fig1–Fig8、S1–S10、源数据及隔离的 Figure 1 TrueType 候选；Fig6–Fig8 仅为预留 |
| `5_manuscript` | Stage K 既有基线与 2026-10-12 叙事候选分开，均保留可编辑文档及阅读版 |
| `6_release` | 既有投稿包、清单与其实际覆盖范围；不宣称已收录本轮候选 |
| `7_report` | 工作记录、科学审查、子图矩阵、编辑台账、数值和呈现 QA |

截图 `7.Report` 使用现有 `7_report` 实现同一用途，避免另建重复报告入口和破坏绑定路径。`8_archive`、`8_reference`、`9_version` 继续承担历史、参考和版本用途。`audit_tools`、`phase17_v7`、`02_analysis` 等冻结后端保留原位；主目录提供真实文件与精确导航，而不是移动后端制造路径失效。

## 3. README、引用与公开范围

根 README 重新组织为：起点导航 → 八目录职责 → Figure 1–5 证据链 → 基线/候选/投稿包差异 → RP v4 状态与硬门 → 数据恢复及校验 → 审计限制 → 许可证、引用和作者信息。

八个主目录 README、管理总索引、图件与补充图入口同步更新。根和管理目录的 `CITATION.cff` 修正为历史核心归档 v1.1.0 / DOI `10.5281/zenodo.22151739`，不再推荐已撤回的初始 DOI。历史 DOI 不被描述为已覆盖 RP v4 或本轮候选。修改前 README、引用和总索引保存在 `8_archive/navigation_restructure_2026-10-12/`。

第三方 QiTeng Skill 分发包、完整机器路径清单、逐页渲染缓存、重复 proof 和大矩阵不进入本轮 Git 增量；Skill 原始 QA 失败与限制仍保留在公开审计中。本轮不重新许可第三方材料。

## 4. 可回溯结果与科学边界

- 核心正结论仍是 process-level B_CONV IFN/ISG association，而不是新 taxonomy、临床 biomarker 或因果调控机制。
- Figure 1d B_ASC end-to-end median Jaccard 0.930323 低于既定 0.95；固定表示的条件稳定性不代替端到端稳定性。
- Figure 2 主要组成 OR 约 0.947；缺乏富集证据不等于 abundance equivalence。
- Figure 3 主要 IFN/ISG 效应约 0.837；pan-B 主要诊断对照为 nominal 阳性，不再描述为 null。
- Figure 4 的 childhood 支持依赖原标签；4,410 基因的 genome-wide rho 约 0.026；B_ASC calibration precision 0.885210 低于 0.90，不存在 corrected external disease coefficient。
- Figure 5 保留 broader M5911 depletion 后 discovery STAT2 区间跨零、q 约 0.500 的边界；两供者扰动仅为描述性背景。
- Stage I 的 `delta_profile=0.034925002` 与 WP1 来自同一 68 名供者、同一估计对象；两种区间不是两次独立发现，nominal P 也不是新的盲法确认。
- Stage M 只冻结外部结果盲技术计划；Stage N 的合格运行时、至少 2.5 TB 物理 scratch 与独立下载授权仍为硬门。本轮未新增外部表达效应。

29 行 `KEY_RESULTS.csv` 由冻结 CSV/JSON 的结构化选择器导出，记录 source path、source selector、单位和解释；没有拟合新模型。S1–S10 的十份 CSV 与冻结后端逐字节相同，并保留原始来源清单。

## 5. 完整性设计与测试

`PUBLIC_REPOSITORY_INDEX.csv` 对 Git 暂存区实际 blob 字节建立大小、SHA-256 和 Git object ID 索引，不把 Windows 工作区换行字节冒充 Linux checkout 字节。精选清单进一步保护科学文件和导航；四份派生清单/状态/QA 收据排除自引用哈希，排除列表明文登记。

新增字节绑定候选和 CSV 使用 `.gitattributes -text`，保留 exact bytes。CRLF 的 diff whitespace 识别显式配置，不靠改变绑定文件内容消除警告。

本轮已完成的本地验证：

| 验证 | 状态 |
|---|---|
| 八个主目录和 README | PASS |
| 精选公开资产大小/SHA-256、候选边界、Stage M 不解锁约束 | PASS |
| 45 个受保护科学 Figure/Source Data | 哈希不变 |
| 十个补充源数据副本 | 与冻结来源一致 |
| 新增校验器的负面/正面测试 | 18/18 PASS，包括四项 Git 对象专项测试 |
| 全量 Git 对象索引 | 4,785 项 PASS，大小、SHA-256、object ID、路径覆盖全部匹配；四份派生对象明文排除自引用 |
| 分析脚本及新工具语法编译 | PASS |
| 暂存区 diff whitespace | PASS |
| 新增/变更文件发布范围检查 | 无 95 MB 以上文件、禁止路径或指定凭据模式；模式检查不等于形式化隐私认证 |

上一轮 127/127 candidate QA、49 页 WPS 可视核查、accessibility 0/0/0 为保留的审计记录，本轮没有将其冒充一次新的双引擎渲染或完整生物学重跑。41,249 文件、6,172,113,475 字节是上一轮本地快照，不是 Git 文件总数；本轮另建 Git scoped inventory。

## 6. 提交与远端核验

干净 `git archive` 导出中精选 124 个文件和 125 条导航全部通过。但第一次将全量 Git blob 索引直接应用于 Windows tar 导出文件时发现 94 项不一致：其中主要为按 Git 属性转换的文本换行，另有中文文件名被原生 tar 错误解码。该失败没有被抹掉或标记为 PASS。新增独立 Git 对象校验器，直接检查 index 的 path / object ID / size / SHA-256 与覆盖完整性，避免将 archive/checkout 字节与 Git blob 字节混淆；精选科学文件仍由文件级校验保护。

进一步复核确认：93 项内容差异全部为 CRLF/LF 等价；另一个历史中文路径在该 tar 导出中未按索引名称找到。Python 普通路径还触发了 44 个 Windows 长路径假缺失，使用 extended-length path 后仅剩上述一个导出名称问题。最终 Git 对象校验没有这些导出/路径问题，4,785/4,785 PASS；精选清单在加入新校验器后为 125/125，导航 125/125。本轮没有改写历史文件来迁就导出工具。

当前记录状态：`PASS_GITHUB_STRUCTURE_SYNC__SCIENTIFIC_CANDIDATE_REVIEW_REQUIRED`。

重构内容已非 force 推送，提交为 `c9ee10120ee755efd033879490161fc72080c21f`；86 个变更文件。`git ls-remote` 确认远端 `main` 指向同一提交。GitHub API 在该精确提交下确认八个主目录均存在；远端 README 的 Git object ID `b36054fbb3a3dbb336a4718a0e76feb62bae0dbe` 与本地一致。

GitHub Actions 的 [Static checks 38246420810](https://github.com/1209433622cz-maker/sle-bcell-remodeling/actions/runs/38246420810) 已完成，结论 `success`；包含脚本语法编译、18 项测试、精选公开文件/导航校验与全量 Git blob 索引校验。仓库维持 PUBLIC，简介更新为可审计的 SLE B-cell 分析、图件、源数据、稿件候选及有边界的可复现记录，避免将未解锁工作表述为完整外部验证。

本记录的推送后补录与同步索引另作一个小型收尾提交，避免改写首轮提交历史；最终收尾 SHA、远端一致性和 CI 收据保存在本地 `GITHUB_PUSH_RECEIPT_2026-10-12.json`，排除自引用和重复提交循环。Git 索引共 4,789 个受跟踪路径，4,785 项可索引负载，四份派生文件排除自引用；不是新增 4,789 文件，也不是上传大型本地原始数据。

本轮 `tmp/public_repository_export_20261012_98ff207/` 临时 tar/checkout 的清理指令被工具策略拒绝，未删除，也未使用其他方式绕过。它仍为 Git 忽略的本地取证临时目录，不进入推送；该限制不影响完整性核验或公开同步结果。

## 7. 未变更对象与下一阶段

既有投稿 ZIP SHA-256 仍为 `349d69afa3d5a3b93b9e601186e6016ac5c9494eb64e79d00b36d607e561ed6e`。它不包含 2026-10-12 新叙事/Figure 1 候选；本轮不另制包、不替换 canonical、不创建 DOI 或 Release、不重跑 write-once Stage I、不变更历史 G2/G2B HOLD。

本轮结束后的优先目标是两位作者针对新候选的 exact-file 审阅与采纳决定；采纳后才可单独授权更新正式稿件和投稿包。RP v4 继续推进时，下一科学工程目标仍为 Stage N 的运行时/存储/原始计数重构资格，不能因目录推送而自动开放疾病效应或下载。

后续修改只因真实数值、来源、交叉引用、actual-size 可读性问题、新数据或明确作者科学反馈触发；不通过追加显著性检验强化既有结果。
