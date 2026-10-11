# 2026-10-12 全工作区审计、分类整理与投稿包行动记录

## 1. 本轮目标与边界

本轮对 `H:\cuhk-2025fALL\6013RP-wyf` 进行了文件级全量审计，建立截图所示的编号目录，完成全部视觉资产分类，生成当前投稿主包，并准备 GitHub 同步。

为保护 RP v3/RP v4 已冻结的相对路径、合同与 SHA-256，本轮采用非破坏式整理：原始分析树不移动、不改名、不删除；新的编号目录保存 current canonical copies、完整目录索引和来源收据。大文件与历史副本仅被分类，不因“看起来重复”而直接删除。

执行前 Git 基线：`main`，commit `c0af11487eb3f0c49fb58ec54755f6aa175bc645`。

## 2. 全量文件审计结果

| 指标 | 结果 |
|---|---:|
| 基线文件 | 39,521 |
| 总字节数 | 5,403,475,540 bytes（5.032 GiB） |
| Git 已跟踪 | 4,395 |
| 本地忽略 | 35,126 |
| 最终审计时未跟踪 | 0 |
| 内容检查 PASS | 39,521 |
| 内容检查 HOLD / FAIL | 0 / 0 |
| 重复内容组 | 14,256 |
| 理论重复占用 | 1,090,906,240 bytes（1.016 GiB） |
| P3/可再生成层 | 4,869 files，约 0.984 GiB |

内容检查不是仅看扩展名。审计器实际完成 SHA-256 和格式级读取，包括 PDF 页结构、DOCX/ZIP CRC、PNG/JPEG/TIFF 像素完整性、H5AD/HDF5 根键、GZIP CRC 与完整解压、TAR 成员、JSON/JSONL 解析、CSV/TSV 行列结构、NumPy 文件及 UTF-8 文本。Windows 超长路径通过 `\\?\` 读取层处理；一个 274 字符的 QiTeng QA 路径已专门回归验证。

### 主要空间分布

| 原目录 | 文件数 | 体积 |
|---|---:|---:|
| `phase17_v7` | 35,839 | 2.362 GiB |
| `Data` | 7 | 1.251 GiB |
| `04_submission` | 690 | 0.777 GiB |
| `00_project_management` | 1,282 | 0.291 GiB |
| 根目录 `6013RP-wyf.zip` | 1 | 0.257 GiB |
| `PAPER` | 9 | 0.052 GiB |
| `tmp` | 514 | 0.024 GiB |

最大文件是 `Data/processed/GSE135779_nehar_validation/source/GSE135779_RAW.tar`（1,299,783,680 bytes）。其后是根目录冻结归档和多个 H5AD。它们均已通过读取检查，但仍保留在原位，不进入 Git。

按类型，空间主要由 TAR（1.211 GiB）、PNG（1.100 GiB）、ZIP（1.095 GiB）、H5AD（0.596 GiB）、PDF（0.367 GiB）与 DOCX（0.196 GiB）构成。

## 3. 新目录与用途

- `0_admin`：项目治理、许可证、引用、总索引和价值资产登记。
- `1_data`：当前数据清单；大型数据留在冻结来源路径。
- `2_code`：当前 Stage M 执行入口与 1,321 个代码对象索引。
- `3_results`：Stage I/K/L/M 当前 gate/result copies 与 23,562 个历史结果索引。
- `4_figures`：Fig1-Fig8、Supplementary、QA_Renders、Other_Visuals。
- `5_manuscript`：Stage K 主文和补充材料 current copies。
- `6_release`：完整、可验证的投稿主包。
- `7_report`：本轮行动记录和全部报告/工作记录索引。
- `8_archive`：归档及删除候选索引；本轮未删除绑定证据。
- `8_reference`：文献索引；文献 PDF 留在 `PAPER` 原路径。
- `9_version`：全量 inventory、哈希、格式检查、重复组、复制 provenance 和状态 JSON。

## 4. 图片与图件分类

全部 3,461 个位图/矢量图与 662 个科学图件 PDF 均已分类，未分类数均为 0；合计 4,123 条视觉资产记录。

| 类别 | 数量 | 决策 |
|---|---:|---|
| Fig1 | 95 | current canonical PDF/PNG + source data；历史候选仅索引 |
| Fig2 | 70 | current canonical PDF/PNG + source data |
| Fig3 | 70 | current canonical PDF/PNG + source data |
| Fig4 | 72 | current canonical PDF/PNG + source data |
| Fig5 | 106 | current canonical PDF/PNG + source data |
| Fig6-Fig8 | 0 | 当前手稿未使用，明确保留为空的 future slots |
| Supplementary S1-S10 | 690 | current PDF/PNG copies + 全量历史索引 |
| Manuscript/QA page renders | 2,682 | 单列 QA，不冒充科学 panel |
| Figure QA/comparisons | 213 | 单列候选、proof、crop、comparison |
| Unnumbered scientific visual | 51 | Gate 诊断图与其他未编号科学图 |
| Document/admin visual | 74 | 文档 PDF 或行政视觉，避免误归 Fig1-Fig8 |

每个 Fig1-Fig8 目录都有 README 和 `ALL_MATCHING_ASSETS` 表。这样既实现精确归类，也避免复制 1.1 GiB 历史 PNG 并破坏原路径。

## 5. 当前投稿包

投稿包目录：`6_release/SLE_Bcell_Submission_Package_2026-10-12/`

ZIP：`6_release/SLE_Bcell_Submission_Package_2026-10-12.zip`

状态：`PRE_SUBMISSION_MASTER_PACKAGE__NOT_SUBMITTED`。

| 对象 | 核验 |
|---|---|
| 主文 | Stage K limited integration；DOCX + 32-page PDF |
| 主图 | 5 PDF + 5 PNG；QiTeng 2026-09-29 reader-language freeze |
| 补充材料 | DOCX + 16-page PDF；包含 Supplementary Table S10 |
| 独立补图 | S1-S10 共 10 PDF |
| Supplementary Data | 3 个既有 ZIP + Stage K measurement-rule CSV |
| 作者与声明 | DOCX/PDF/MD + reporting information |
| 投稿信 | 12 October 2026 标题同步后的 npj Systems Biology and Applications 草稿，文件名标记 `DRAFT` |
| 完整性 | 40 payload files verified；`SHA256SUMS.csv` + verifier |
| 外层 ZIP | 20,091,489 bytes；SHA-256 `510286f49e71d59ff87486111e786db2b360f1fb77ea79650edadea87ee85eba` |

该包可用于后续目标期刊适配，但不能被描述为已经投稿。若目标不是 npj Systems Biology and Applications，只应修改期刊侧格式、投稿信和 metadata，不应改动冻结科学结论。

## 6. 有价值成果与长期保留对象

1. **稳定科学主结论**：可重复的 process-level `B_CONV` IFN/ISG remodeling。
2. **必须永久保留的三条边界**：B_ASC identity ceiling、source-label-independent transfer ceiling、STAT1/STAT2 mechanistic ceiling。
3. **Stage G**：G2C 在 30/30 个适用合成情景通过，10/10 个强制边界情景保留；这是方法适用域资格，不是新的生物学复现。
4. **Stage I**：68 donor 的 `delta_profile=0.034925002`，HC3 SE 0.011559，95% CI 0.011834-0.058016，P=0.003612。它与 RP v3 WP1 是同一 estimand，只能解释为 measurement-rule sensitivity。
5. **Stage K**：上述敏感性已有限加入 Methods、Discussion、Supplementary Table S10 和 Source Data；主图未被改写。
6. **Stage L**：GSE262846 的独立问题已冻结为 26 paired SLE patients（12 active、14 inactive）的 T1T2-minus-rN IFN/ISG score difference；尚未读取表达结局。
7. **Stage M**：176 run / 88 library 疾病盲 raw-count workflow、GENCODE 50、nf-core/rnaseq 3.27.0 和 HC3-t(23) 小样本协议已冻结；下载和外部效应仍未解锁。
8. **可重复性资产**：Stage I/K/L/M gate、当前脚本、全量清单、哈希、报告索引、图件 provenance 与投稿包 verifier 均应长期保留。

## 7. 清理裁决

本轮没有物理移动或删除历史文件。原因是 14,256 个重复组中包含大量已经进入合同、manifest、source binding、Git 历史或行动记录的对象。按名称批量删除会造成比节省空间更严重的审计损失。

后续如果确需释放空间，只能另开一轮 `HASH_AWARE_SAFE_CLEANUP`，优先处理：

1. `__pycache__`、`.pyc`、临时 render 和 `_software_tests`；
2. 已由 canonical SHA 覆盖、且未被合同引用的旧 QA 页面；
3. 已被新 release 完整替代的本地 submission ZIP；
4. 每一项删除前必须反查 `DUPLICATE_GROUPS`、`WORKSPACE_FILE_INVENTORY` 和源码引用。

不得直接删除根目录 `6013RP-wyf.zip`、RP v3/RP v4 stage directories、Stage G/I sealed outputs、原始 TAR/H5AD 或历史 Zenodo/GitHub release evidence。

## 8. 下一阶段判断

科学下一阶段仍应是：

`RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION`

但当前必须维持 HOLD，直到同时满足：

1. 合格的 Linux x86-64 Docker/WSL2 runtime；
2. SRA Toolkit 3.4.1、Nextflow、nf-core/rnaseq 3.27.0、Subread featureCounts 2.1.1；
3. 至少 2.5 TB 可验证的物理 scratch；
4. 两位作者对 233.209 GB raw download 的独立书面授权；
5. write-once、disease-blind count/QC seal 在任何 disease/activity join 之前完成。

在这些条件未满足前，不应下载 SRA、不应拟合外部 activity effect，也不应把 Stage L/M 写成外部验证。投稿包可以作为当前冻结快照保存，但若研究战略仍优先追求真正的新外部问题，建议先完成 Stage N，再做一次有限的 Stage O outcome analysis 与稿件整合裁决。

## 9. 终局验证

- 全量内容：39,521/39,521 PASS。
- 图片：3,461/3,461 classified。
- 科学图件 PDF：662/662 classified。
- 投稿包 payload：40/40 SHA-256 PASS。
- 主文/补充 PDF：32/16 pages。
- 原文件：0 moved，0 deleted。
- 完整机器记录：`9_version/ORGANIZATION_STATUS_2026-10-12.json`。

## 10. GitHub 同步结果

组织与投稿包 commit 为 `23f241268e5ad6d9f1c65daea065886f7ccc1fdb`，远端 `main` 从 `c0af11487eb3f0c49fb58ec54755f6aa175bc645` 非强制快进到该 commit。

本机 Git smart-HTTP 到 `github.com:443` 在推送阶段被网络重置，但 GitHub API 与已登录 `gh` 账号正常。为避免改变提交身份，本轮通过 Git Database API 上传本地 index 中的 125 个唯一 blob（161 个路径），逐一要求远端 blob SHA 与本地一致；随后生成的 tree SHA `dcad22de851bae2fa652fb1a7a0ba18f2ee9c983` 和 commit SHA 均与本地 Git 对象完全一致。分支更新使用 `force=false`，更新前后均回读远端 SHA；没有覆盖、重写或强推历史。
