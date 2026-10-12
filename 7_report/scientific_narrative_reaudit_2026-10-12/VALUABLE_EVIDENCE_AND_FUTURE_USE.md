# 有价值成果与未来用途登记

日期：2026-10-12。此文件是本轮内容审查的导航，不替代原始运行目录或其冻结合同。不同阶段的 PASS/HOLD 不可相互覆盖。

| 资产 | 当前用途 | 未来用途 | 使用边界 |
|---|---|---|---|
| `5_manuscript/current/` | 本轮可编辑正文基线 | 作者比较与回退 | 本轮没有覆盖；其 Markdown 镜像有漂移 |
| `5_manuscript/scientific_narrative_candidate_2026-10-12/` | 新正文、补充材料及可编辑候选 | 精确文件级作者科学审阅 | 候选，不是已批准的新 canonical，也不是新投稿包 |
| `4_figures/Fig1..Fig5/canonical/` | 五张主图、21 子图 | 当前论文主体 | Figure 1 原 PDF 有 Type3 字体；候选已从源重导出 |
| `4_figures/Fig1/candidate_2026-10-12_truetype/` | 数值不变的字体和图例修复候选 | 经审阅后局部替换 Figure 1 导出 | CSV 字节不变，PNG 并非逐像素相同 |
| `4_figures/Supplementary/` | S1–S10 图件、38 子图 | 边界与诊断完整报告 | 不为“让主图更强”而继续迁入主图 |
| `phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration/figures/source_data/` | S1–S10 当前来源 CSV | 精确再绘制 | 已与 2026-10-12 包中 Supplementary Data 1 对应成员核对；旧 portal ZIP 不完整 |
| `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad` | 硬 QC 后整数计数 | 精确 pseudobulk 或身份重建 | 150,402 × 30,172；不是整个原始 CELLxGENE 对象 |
| `phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad` | PCA/Harmony/UMAP 坐标 | 身份诊断与冻结图的来源 | embedding-only，无 X 是设计如此；不能拿它代替计数 |
| `Data/processed/GSE135779_nehar_validation/source/GSE135779_RAW.tar` | 外部来源矩阵包 | 独立 accession 的复算 | 112 个普通成员，包括 56 个压缩矩阵；本轮未逐一解压重估疾病效应 |
| `3_results/current/StageK_Source_Data.csv`、`StageI_Result.json` | 同一 68 供者 delta_profile 的双区间记录 | Table S10、测量规则讨论 | 已知 WP1 点估计后的不确定性重估，不是第二次独立阳性发现 |
| RP v3 G2/G2B HOLD 记录 | 失败目标与方法边界 | 方法学限制、避免重复开发 | G2C PASS 不解除这些 HOLD，不删除不利记录 |
| RP v4 G2C 冻结合成记录与代码绑定 | 单一方法的条件性模拟资格 | 独立方法复核 | 本轮没有再运行 160,000 次终局模拟；不能据此宣称覆盖了全部真实机制 |
| `3_results/current/StageL_Gate.json`、`StageM_Gate.json` | 新队列身份、配对与前向合同 | GSE262846 活动度×区室问题 | 无外部表达结论；先关闭 Stage N 运行时、空间与下载授权门 |
| `7_report/`、旧 `phase17_v7/` 审查报告和合同 | 失败原因、修复过程、授权、溯源 | 审稿答复与研究诚信核验 | 工作记录是资产，但历史结论不是当前权威状态 |
| `9_version/scientific_content_reaudit_2026-10-12/` | 41,249 文件的全量大小、格式、哈希、重复与角色快照 | 精确文件定位、后续增量审计 | 快照早于本轮成品；重复数量不是删除许可 |
| `8_reference/qiteng_v03242/` | 上传 Skill 的规范与 QA 实现 | 写作与压缩治理参照 | 活跃 CORE 与上传 ZIP 一致；包内 464 个 manifest 不一致必须保留披露 |
| `6_release/SLE_Bcell_Submission_Package_2026-10-12.zip` | 先前已打包材料 | 历史比较 | 本轮未更新，不能冒称已含本轮候选 |
| GitHub 删除前恢复包与 Git bundle | 可恢复历史 | 灾难恢复、引用历史提交 | 不是应删除的普通副本；本轮不做清理 |

## 不应丢弃的负面资产

fine-state failure、end-to-end B_ASC failure、primary composition null、弱 genome-wide concordance、required elastic-net calibration failure、CAMERA exception、M5911 depletion attenuation，以及两供者 perturbation 的低样本量边界均应永久保留。

## 不应纳入当前论文结果的资产

未通过 G2/G2B 的目标、被纠正后废弃的外部 mapper 疾病效应、还没完成 raw-count 重构的 GSE262846 活动度结果，以及为了填满 Fig6–8 而产生的占位图均不应进入当前主叙事。

## 下一阶段

先审阅本轮 exact DOCX/PDF、Figure 1 候选和编辑账本。若需要真正的新增科学贡献，另按 RP v4 Stage N 冻结合同准备运行环境与物理存储；不能用继续检验同一 68 人差值替代独立新问题。
