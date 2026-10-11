# 2026-10-12 GitHub 重建、全量复核与投稿包终局行动记录

## 1. 本轮目标与执行边界

本轮按作者明确授权完成以下工作：删除原 GitHub 仓库、使用同一名称创建公开仓库、推送当前本地完整历史和标签、恢复历史 Release，核查本地全部文件的大小与内容，确认分类整理结果，重建并验证当前投稿包，记录有价值资产，并判断下一阶段目标。

本轮没有重跑统计模型，没有修改主文科学结论、Figure 1-5、Supplementary Figure S1-S10、Stage I write-once 结果或 Stage G 合成裁决，也没有下载 SRA、读取外部表达结局或执行期刊投稿。

## 2. GitHub 删除、重建与公开状态

- 原仓库：`1209433622cz-maker/sle-bcell-remodeling`。
- 删除前备份状态：`PASS_GITHUB_REPOSITORY_PREDELETE_BACKUP`。
- 删除后 REST/GraphQL 查询均返回不存在，确认旧远端已删除。
- 同名仓库随后重新创建为 `PUBLIC`，canonical URL 保持不变：
  `https://github.com/1209433622cz-maker/sle-bcell-remodeling`。
- 新仓库启用 Issues 与 Projects，关闭 Wiki，保留 MIT License。
- Topics：`systemic-lupus-erythematosus`、`single-cell-rna-seq`、`b-cells`、`bioinformatics`、`reproducible-research`。
- 本地完整 Git 历史推送至 `main`；重建后首次远端基线与本地精确一致：
  `09e931e7c929d4a66dc8ea3f334d6a11c1d1087f`。
- 标签 `v1.0.0` 与 `v1.1.0` 已恢复。

删除前已在 `8_archive/github_repository_recreation_2026-10-12/` 保存完整 Git bundle、远端/本地 refs、仓库元数据、Release 元数据、Release notes、六个附件以及 SHA-256 清单。bundle 验证为完整历史；备份清单 15/15 文件通过大小和 SHA-256 复核。

## 3. 历史 Release 恢复结果

两个历史 Release 均按删除前标题、说明和资产重建：

| Release | 资产 | 字节 | SHA-256 | 恢复结果 |
|---|---|---:|---|---|
| `v1.0.0` | `package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip` | 46,055,879 | `1fb1170b68e399edbcf95400611fdf733bdcb3b64ba64640af0958494cc7904a` | PASS |
| `v1.0.0` | `sle-bcell-remodeling-v1.0.0-source.zip` | 41,764,089 | `94fbe198a0eeaaa2d6a491ec1c10f5c4020d1d5a82985daf19799acdd73f6999` | PASS |
| `v1.0.0` | `SHA256SUMS_v1.0.0.txt` | 235 | `ea45ae5a2ef565e05dffc96ad952e56e14d192916d678f3ad46a5af15c3372d5` | PASS |
| `v1.1.0` | `Research_Archive.zip` | 25,577,813 | `aae67863fc6b34b0ac091f8d38524ffc55a7cf364ff7ff4b4d43fedfa4ae0095` | PASS |
| `v1.1.0` | `Source_Code.zip` | 78,040,863 | `51b1007908668f8ee25971e99270bf8477720a25ed7491bacd2f7572a4e24645` | PASS |
| `v1.1.0` | `SHA256SUMS.txt` | 171 | `be96eec9c0610208f867fe7258a3c7e672a63e8273c486cc09caae2bfcdb457b` | PASS |

远端 API 返回的资产文件名、字节数与 digest 均与删除前备份一致。Zenodo DOI 未修改；其历史记录继续指向同一 canonical GitHub URL。

## 4. 全量本地文件复核

文件级复核覆盖项目中的全部 regular files，仅排除 `.git` 内部对象和审计输出目录自身，以避免递归自计数。

| 指标 | 结果 |
|---|---:|
| 文件数 | 39,886 |
| 总大小 | 6,110,895,142 bytes（5.691215 GiB） |
| Git tracked | 4,707 |
| Git ignored local | 35,179 |
| 未跟踪文件 | 0 |
| 内容检查 PASS | 39,886 |
| HOLD / FAIL | 0 / 0 |
| 重复组 | 14,279 |
| 理论可重复字节 | 1,339,514,932 |

完整清单位于 `9_version/full_local_reaudit_2026-10-12/`，包括逐文件路径、字节数、SHA-256、Git 状态、文件类型、内容检查、重复组和价值角色。重复项不是自动删除对象；历史投稿包、负面裁决、sealed outputs、Release 资产和可重复性副本仍承担审计或恢复职责。

## 5. 分类整理与高价值资产

编号工作视图及其子目录已经建立并完成索引：

- `0_admin`：导航、目录分类规则和价值登记。
- `1_data`：当前/历史数据入口、元数据与大型本地对象索引。
- `2_code`：Stage M 当前执行入口、测试、Windows runner、环境与历史分析代码索引。
- `3_results`：Stage I/K/L/M 当前结果副本和历史结果索引。
- `4_figures/Fig1` 至 `4_figures/Fig8`：全部图片按科学职责、主图/补图/QA/历史候选分类，并保留来源路径和哈希。
- `5_manuscript`：Stage K 当前主文与 Supplementary Information。
- `6_release`：当前投稿主包、历史候选、GitHub/Zenodo 与完整性记录。
- `7_report`：当前审查报告和逐轮行动记录。
- `8_archive`：恢复材料和不可作为当前科学基线的历史对象。
- `8_reference`：RP、写作规范和外部参考索引。
- `9_version`：Git 历史、文件清单、哈希、审计和版本回执。

全量审计识别的主要高价值角色如下：

| 角色 | 文件数 | 字节 |
|---|---:|---:|
| current main figures | 10 | 3,029,068 |
| current Stage K manuscript | 127 | 61,899,415 |
| current submission package | 42 | 41,207,785 |
| GitHub recreation backup | 17 | 556,978,867 |
| governance and navigation | 22 | 124,125 |
| inventory and integrity | 25 | 38,666,908 |
| RP v4 decisive evidence | 70 | 650,841 |
| work and action records | 5 | 134,103 |

## 6. 当前投稿包

当前投稿主包：

- 目录：`6_release/SLE_Bcell_Submission_Package_2026-10-12/`
- ZIP：`6_release/SLE_Bcell_Submission_Package_2026-10-12.zip`
- ZIP 字节数：20,091,489
- ZIP SHA-256：`349d69afa3d5a3b93b9e601186e6016ac5c9494eb64e79d00b36d607e561ed6e`
- payload：40/40 SHA-256 PASS
- 状态：`PRE_SUBMISSION_MASTER_PACKAGE__NOT_SUBMITTED`

包内包含 Stage K limited-integration 主文与补充材料、冻结主图/补图、Source Data、投稿信草稿、作者与声明材料、许可证和内部 verifier。该包尚未提交，也未把 Stage L/M 外部 outcome 写入论文。期刊若发生变化，仅应做目标期刊格式、投稿信与 metadata 适配，不应借机改变冻结结论。

## 7. 当前科学成果与边界

1. 稳定主结论仍为可重复的 process-level `B_CONV` IFN/ISG remodeling。
2. identity ceiling、transfer ceiling 与 mechanistic ceiling 已在主文和主图中显式保留；负面边界是可信度组成部分，不是待“救阳性”的缺陷。
3. Stage G 的 G2C 资格在 30/30 个适用合成情景通过，10/10 个强制边界情景保留；该结论只限定区间方法适用域。
4. Stage I write-once 结果为 68 donors 的 `delta_profile = 0.034925002`，HC3 SE 0.011559，95% CI 0.011834-0.058016，P=0.003612。
5. Stage I 与 RP v3 WP1 是同一 estimand，不是独立重复；Stage K 因此只把它有限解释为 measurement-rule sensitivity。
6. Stage L 已冻结 GSE262846 的独立问题：26 paired SLE patients 中 T1T2-minus-rN IFN/ISG score difference 与 activity group 的关系；表达结局仍未读取。
7. Stage M 已冻结 176 runs / 88 libraries 的 disease-blind raw-count workflow、GENCODE 50、nf-core/rnaseq 3.27.0 与 HC3-t(23) 协议；没有自动授权下载或外部效应分析。
8. 主文和图件目前处于 maintenance-level scientific freeze；没有发现足以支持主动重开统计模型或替换 panel 的新问题。

## 8. 最终裁决与下一阶段

本轮裁决：

`PASS_PUBLIC_GITHUB_RECREATION__PASS_FULL_LOCAL_REAUDIT__PASS_PRE_SUBMISSION_PACKAGE`

下一阶段仍为：

`RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION`

启动条件保持不变：

1. 合格的 Linux x86-64 执行环境；
2. 至少 2.5 TB 可验证 scratch 空间；
3. 两位作者对原始数据下载与一次性重构的明确授权；
4. Stage M 的冻结 reference、workflow、sample/run manifest 与 integrity gate 不变；
5. 重构阶段保持 disease blind，不读取或拟合 external activity outcome。

在这些条件通过前，不应下载约 233 GB SRA、不应执行 Stage O outcome analysis，也不应将 Stage L/M 描述成已完成的外部验证。当前投稿包应作为 bounded pre-submission snapshot 保存。

## 9. 最终质量检查

- Git 工作树在本轮记录写入前为 clean。
- 新仓库为 PUBLIC，default branch 为 `main`。
- 本地与重建后首次远端 `main` SHA 完全一致。
- 两个 tags 和两个 Releases 可公开读取。
- 六个 Release 资产恢复前后大小与 SHA-256 全部一致。
- README 已同步当前 Stage N gate、目录导航、全量审计、投稿包和公共存档信息。
- 本地备份、全量审计与投稿包均保留机器可读状态文件和校验清单。

