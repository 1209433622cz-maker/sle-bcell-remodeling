# Gate C8S 行动记录：补充证据、统计可追溯性与投稿包冻结

**日期：** 2026-08-21

**执行角色：** 生物信息学导师级全量复核、分析工程、手稿与投稿包质控

**输入状态：** GitHub `main` 的 Gate C8R 冻结结果与外部独立复核意见

**最终决策：** `PASS_GATE_C8S_SUPPLEMENTARY_EVIDENCE_TRACEABILITY_FREEZE_AUTHOR_ACTION_REQUIRED`

## 1. 本轮目标与边界

本轮没有启动新的探索性生物学分析，也没有修改任何冻结上游效应值。目标是关闭独立复核指出的审稿人可见缺口：

1. 修复 Figure 5 机器可读源数据中 M5911 与 GSE23307 的面板归属；
2. 优化 Figure 1d 与 Figure 3c 的注释位置和过滤符号说明；
3. 从冻结结果重建 Supplementary Figures S1-S7，并为每幅图提供源数据和硬断言；
4. 建立完整统计结果归档，覆盖全部基因级分支、设计矩阵、模型结果和多重校正体系；
5. 精修主文标题、统计方法、precision-medicine 边界、数据可用性和补充材料；
6. 使用 WPS 后台渲染并逐页检查最终 DOCX；
7. 建立可一键重建、可自动失败的 Gate C8S 最终审计与确定性投稿 ZIP。

科学边界保持不变：支持的是 broad `B_CONV` 内可重复的 IFN/ISG remodeling，以及收敛但非因果的调控/响应证据；不支持稳定的细粒度 naive-memory 亚型、普遍 B_ASC 扩增、唯一上游刺激、直接 TF 结合或治疗预测效用。

## 2. 主图修复

更新了 `audit_tools/phase17_c7_01_build_main_figures.py`，并从冻结 Gate C2B4-C6B 表格完整重跑五幅主图。

### Figure 1

- 将 B_ASC marker 注释放回 B_ASC 数据区域附近；
- 保留 `DERL3, JCHAIN, MZB1, TNFRSF17, XBP1` 和 sample support = 1.00；
- 避免注释与 B_CONV 主体视觉混淆。

### Figure 3

- 将 panel c 标题压缩为 `Frozen IFN positive-arm genes`；
- 用独立脚注明确 dagger 与 double-dagger：
  - dagger：两个对比均未进行基因级检验；
  - double dagger：primary 对比未进行基因级检验；
- 未检验值仍保持缺失，不被绘制为零或插补值。

### Figure 5

- 删除复用旧 `21_FIGURE5_SOURCE_DATA.csv` 的路径；
- 从冻结 regulator、M5911 和 GSE23307 输出重新构建机器可读源数据；
- 当前精确映射为：
  - panel B：12 行 regulator activity；
  - panel C：12 行 control regulator activity；
  - panel D：3 行 `MSigDB_M5911_NES`；
  - panel E：2 行 `GSE23307_mean_paired_log2p1_effect`；
- 两个 GSE23307 donor 均保持 12/12 frozen IFN genes 为正向。

主图硬断言由 43 项扩展为 46 项，最终 `46/46 PASS`。

## 3. Supplementary Figures S1-S7

新增 `audit_tools/phase17_c8s_01_build_supplementary_figures.py`。所有图均由冻结结果重绘，输出 PDF、600-dpi PNG 和机器可读 CSV；没有从图像或手稿反向抄数。

| Figure | 审稿功能 | 冻结内容 |
|---|---|---|
| S1 | Source integrity and QC | hard-QC retention、88 个 library checkpoint、1,972 个 residual-risk sensitivity calls |
| S2 | Representation diagnostics | unintegrated/Harmony mixing、bridge distance、resolution concordance、marker-module localization |
| S3 | Identity adjudication | 5/4/3/2-level stability、cluster Jaccard、transition matrix、最终二分 compartment 稳定性 |
| S4 | Composition diagnostics | zero-ASC strata、covariance/cell-policy sensitivity、two-part presence 与 positive abundance |
| S5 | Pseudobulk diagnostics | tested/significant genes、edgeR dispersion、ranked-list QC、IFN branch effects |
| S6 | Independent validation | GSE135779 donor support、四程序结果、source-label omission、donor deletion |
| S7 | Correlation sensitivity | CAMERA/FRY concordance、inter-gene correlation、exact q values、target counts |

图形质控过程中识别并重跑解决了三项排版问题：

- S1 将 residual-risk 构成改为百分比和精确计数同时可见；
- S4b 扩展横轴并将方法图例移出效应区，避免与最上方置信区间重叠；
- S5b 将重叠的 dispersion 文本改为配对线表达。

最终 supplementary panel assertions 为 `29/29 PASS`；所有可见文字不小于 5 pt。

## 4. 完整统计结果归档

新增 `audit_tools/phase17_c8s_02_build_full_statistical_archive.py`，构建：

`Additional_file_4_Full_Statistical_Results_GateC8S.zip`

归档包含：

- 12 个完整 `filterByExpr` 基因级结果分支；
- 12 个去直接标识的设计矩阵；
- composition 的系数、对比、预测、敏感性、leave-one-out 与诊断；
- transcription 的 program、ranked-list、influence 与 concordance 结果；
- ULM、target influence、CAMERA、FRY、M5911 与 GSE23307 结果；
- `STATISTICAL_TEST_AND_MULTIPLICITY_MAP.csv`；
- README、source provenance 与逐文件 SHA-256 manifest。

冻结状态：

- payload files：63；
- payload bytes：8,566,938；
- ZIP bytes：8,314,122；
- SHA-256：`AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`；
- 两次独立重建字节一致；
- 设计矩阵不含直接 donor/sample identifiers 或自由文本临床字段。

## 5. 主文 v12 与 Supplement v3

新增：

- `01_manuscript/manuscript_v12_genome_medicine_gateC8S_2026-08-21.md`；
- `01_manuscript/supplementary_information_v3_gateC8S_2026-08-21.md`。

### 主文逻辑优化

标题更新为：

> Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling in systemic lupus erythematosus

该标题把论文真正的双重贡献放在同一逻辑句中：不稳定的硬亚型边界与可重复的 within-compartment IFN remodeling。

新增统一的 `Statistical analysis and multiplicity` 小节，明确：

- retrospective secondary analysis 未进行 prospective power calculation；
- primary composition 在三个冻结 base contrasts 内 BH；
- gene-level 在每个 contrast 的 tested genes 内 BH；
- frozen programs 在每个 analysis 的四程序内 BH；
- CollecTRI 为 8 regulators x 3 contrasts 的 global 24-test family；
- CAMERA 与 FRY 分别为独立的六检验 BH family；
- M5911 为三对比 descriptive BH；
- GSE23307 仅两个 donor，不计算推断性 P 值。

新增克制的 precision-medicine 段落：连续 B_CONV IFN/ISG score 可作为未来 molecular stratification 或 pharmacodynamic monitoring 的候选，但当前研究不建立 predictive biomarker、治疗选择规则、临床 cutoff 或 patient benefit。

数据可用性现正确表述为“GitHub repository currently public”；仍保留 open-source licence 和 immutable DOI 的提交前硬停止。

主文最终状态：

- structured abstract：314 words；
- manuscript：6,715 words；
- references：30；
- main figures：5；
- author-controlled manuscript placeholders：6。

### 补充材料结构

Supplement v3 包含：

- 8 张 Supplementary Tables；
- 7 幅 Supplementary Figures；
- 统一 test/multiplicity family 表；
- full statistical archive map；
- C8R/C8S superseded-artifact provenance；
- Figure 5 panel D/E 机器可读修复说明。

## 6. RP 版本谱系修复

更新 `research_proposal_v16_gateC7_completed_2026-08-20.md` 的版本说明：

- v14 是 pre-outcome methodological provenance；
- v16 是 outcome-integrated completed-study record，不是 prospective preregistration；
- manuscript v12 是当前投稿的数值、补充证据和统计可追溯性 canonical report。

README 不再错误地将 v14 称为唯一 active RP，也不覆盖原始 RP 的方法学历史。

## 7. DOCX、WPS 与可访问性质控

新增 `audit_tools/phase17_c8s_04_build_documents.py`，生成：

- 主文 DOCX：27 页；
- Supplementary Information DOCX：12 页、8 tables、7 inline figures；
- Cover letter DOCX：1 页。

WPS 后台渲染过程中发现并解决：

1. Supplementary Figure S3-S7 的标题/图例与图像跨页；
2. Supplementary Table S8 被拆成两页；
3. cover-letter 地址最初被合并为一行；
4. 地址分段后 cover letter 溢出到第 2 页；
5. manuscript v12 的显示日期仍为 20 August；
6. 最终审计对 Figure 5 `series` 名称的预期过窄。

最终版式通过以下约束：

- S8 完整位于 supplementary page 5；
- S1-S7 完整位于 pages 6-12，每幅图的标题、图例和图像位于同一页；
- cover letter 使用专用 compact style，在保留规范地址分段后为 1 页；
- 主文日期与 Gate C8S 版本统一为 21 August 2026；
- 40/40 WPS page PNG 完成视觉检查；
- 三份 DOCX accessibility audit 均为 high=0、medium=0、low=0。

## 8. 一键重建与最终机器审计

新增：

- `audit_tools/run_6013RP_phase17_gateC8S_submission_package.ps1`；
- `audit_tools/phase17_c8s_05_final_submission_audit.py`。

完整重建命令：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8S_submission_package.ps1
```

九步 runner 已从头成功执行：五主图、七补图、统计归档、Markdown、DOCX、WPS、逐页 raster、accessibility 和 final audit。

最终审计的 16 个域全部 PASS，包括：

- main assertions 46/46；
- supplementary assertions 29/29；
- 12 组 figure PDF/PNG；
- 12 个 source-data CSV 与 SHA-256；
- 63-entry full statistical archive；
- manuscript scope/statistics；
- 8-table/7-figure supplement structure；
- author identity 与 30 references；
- DOCX OOXML；
- accessibility；
- WPS 27+12+1 pages；
- attachment integrity；
- visible hard stops。

## 9. 最终投稿包

本地生成目录：

`04_submission/package_genome_medicine_gateC8S_2026-08-21/`

确定性归档：

`04_submission/package_genome_medicine_gateC8S_2026-08-21.zip`

归档状态：

- manifested files：106；
- ZIP bytes：31,631,792；
- SHA-256：`91D9DA265956544C2751540E065B58568E4E05A0013E4DEB47DDEA48BCEEA3D2`；
- 两次固定顺序、时间戳和权限重建完全一致。

## 10. 未完成事项与结论

当前不是科学或技术 HOLD。唯一剩余阻断来自作者和机构控制的信息：

1. institutional ethics determination；
2. competing interests；
3. funding；
4. CRediT contributions 与 all-author approval；
5. acknowledgements；
6. originality/submission confirmation；
7. open-source licence 与 immutable archive DOI。

因此 Gate C8S 正式冻结。下一阶段为 Gate C8B，不再新增公共数据集或修改冻结效应值；只完成作者声明、许可、归档 DOI 和投稿门户预检。
