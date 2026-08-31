# 2026-08-31 selected supplementary replots and scientific harmonization action record

## 1. 本轮目标与边界

本轮继续执行“科学呈现优先，不以立即投稿为驱动”的路线，目标是独立复核全部 5 张主图和 10 张补图，裁决已有子图的保留、修改或替换方案，并从冻结源数据重画确有缺陷的图件。目标期刊 `npj Systems Biology and Applications` 仅作为写作和 Nature Portfolio 图件标准的方向约束。

本轮没有解冻疾病结局、细胞身份、调控分析或外部验证数据，没有新增 cohort、mapper、TF、gene set 或统计检验，也没有修改已确认的 npj 投稿 ZIP。

冻结投稿包：

- 文件：`04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`
- 大小：15,196,223 bytes
- SHA-256：`02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`
- 本轮结束状态：字节级未变化

## 2. 外部材料的使用方式

本轮阅读并独立核查了外部 supplementary information-density audit、claim-ownership proposal、manuscript candidate 以及 S4/S10 proof PDF。外部材料仅作为审稿建议和替代方案，不被视为项目指令、数值来源或可直接替换的正式产物。

独立检查确认外部建议的科学方向基本正确，但两个 proof PDF 不能直接采用：

- S4 proof 的 `0.05/0.10` 对数轴刻度重叠，panel b 图例覆盖数据。
- S10 proof 的 criterion 注释存在裁切与拥挤，panel a 仍混用了与 mapper/state 语义冲突的颜色。

因此，本轮从项目内冻结 CSV 和现有 builder 重画，而不是复制或修改外部 PDF。

## 3. 全部图件裁决

| 图件 | 裁决 | 依据 |
|---|---|---|
| Figure 1a | MODIFY + RETAIN | 保留 workflow，但将 audit/authorization 式措辞改为 retained analysis scaffold 与 unsupported fine-state boundary |
| Figure 1b-d | KEEP | 分别拥有 policy selection、broad-partition stability 与 state-overlap gate 证据 |
| Figures 2-4 | KEEP | 未发现数值、语义、信息密度或排版缺陷 |
| Figure 5a | MODIFY + RETAIN | 明确 6 个 confirmatory regulator-by-contrast 结果由 ULM 拥有 |
| Figure 5b-e | KEEP | 冻结估计、特异性对照、M5911 和 n=2 描述性边界均正确 |
| S1-S3 | KEEP | 分别承担 source QC、representation diagnostics 和 identity adjudication |
| S4a-b | KEEP | 分别承担 zero-ASC 与 covariance/cell-policy diagnostics |
| S4c-d | REPLOT | 比值轴改为 log scale，以显示 sub-null estimate 和宽 CI；数值不变 |
| S5-S9 | KEEP | 没有实质性 claim-ownership 或 information-density 缺陷 |
| S10a-d | REDESIGN | 颜色统一表示 mapper，形状表示 state；balanced accuracy 保留为 diagnostic，不再画成 gate |

该裁决同时记录在：

- `phase17_v7/npj_sba_selected_supplementary_refinement/20260831_s4_s10_semantic_harmonization/01_PANEL_DECISION_MATRIX.csv`
- `phase17_v7/npj_sba_selected_supplementary_refinement/20260831_s4_s10_semantic_harmonization/02_CLAIM_OWNERSHIP_MAP.md`

## 4. 图件实现

### 4.1 Figure 1a

- 将顶部身份结果定义为 `Retained analysis scaffold: B_CONV / B_ASC`。
- 显式分离 `B_ASC sample fractions` 与 `B_CONV donor pseudobulk`。
- 增加 `Retained scope: broad-compartment analyses`。
- 增加 `Boundary: hard fine-state assignments unsupported`。
- 第一轮三行 scaffold 文本与相邻节点间距不足，重新布局后消除重叠。

### 4.2 Figure 5a

- 将 evidence row 改为 `ULM STAT1/STAT2`，避免把 CAMERA/FRY sensitivity 或 TF-target prior 误读为 24-test family 的所有者。
- M5911 和 IFN-beta 两层仍分别标记为 orthogonal concordance 与 descriptive context。

### 4.3 Supplementary Figure S4c-d

- 使用冻结 effect ratio 和 95% CI 重新绘制。
- panel c 采用 log x-axis，覆盖低于 1 的 estimate 与最高 60 左右的 CI。
- panel d 采用 log x-axis，并保持 multiplicative null = 1。
- Source Data 行、数值、模型与不确定性全部不变。

### 4.4 Supplementary Figure S10

- panel a 改为中性灰，避免与 mapper 颜色发生冲突。
- panels b-d 使用 blue/orange 区分 elastic net 与 centroid。
- panel b 使用 circle/square 区分 B_CONV/B_ASC。
- 0.90 state precision 和 0.80 coverage 保留为真正的 eligibility criteria。
- balanced accuracy panel 删除非门控参考线，均值改为黑色横线和直接标签，并明确 `diagnostic only`。

## 5. 数值与 Source Data 完整性

本轮生成 15 份 candidate Source Data，共 5,315 行；所有文件均与各自已审计基线 byte-identical。

| 文件 | 行数 | SHA-256 |
|---|---:|---|
| Figure1_source_data.csv | 55 | `F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805` |
| Figure2_source_data.csv | 191 | `DAA6DDBAB469E0D510AB578BEE0A21AA73FA2D71184739E3F361C3EA6EC8DFE2` |
| Figure3_source_data.csv | 38 | `DEFABF8C16D879362E3AD197C857A9197CD6D0691B20FDFA4AC97BEFF3710BC8` |
| Figure4_source_data.csv | 4,430 | `F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755` |
| Figure5_source_data.csv | 53 | `A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B` |
| Supplementary Figure S1 | 97 | `A140D1D900A3EA869551097146AFFD3872BC7AC78E9E9712E4BDAC834A57CB68` |
| Supplementary Figure S2 | 176 | `E46FE5B33B11D45319DD80C3D669AEEB83F2517095CD0C1FD5EEFA1F57C58731` |
| Supplementary Figure S3 | 39 | `133E973C2753F4946A24739C049308152299A915A3FC6754B30AD0521F979C96` |
| Supplementary Figure S4 | 14 | `7BA2660E5A50ADCF28407BCC92A91C791576DD69A9A1ABA9618DEB045C3A4E19` |
| Supplementary Figure S5 | 17 | `F6682D636C1FF3A1784E0B9E8AEFF5C5D1BB075176312E87FCB938F65C4DA897` |
| Supplementary Figure S6 | 21 | `A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6` |
| Supplementary Figure S7 | 6 | `D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3` |
| Supplementary Figure S8 | 36 | `26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2` |
| Supplementary Figure S9 | 128 | `46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42` |
| Supplementary Figure S10 | 14 | `FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF` |

全部 15 张 PDF 均为单页、170 mm 宽、Arial-compatible vector output，最小可见字号 8 pt，最小正线宽 1 pt，所有 text span 均位于页面范围内。

## 6. 手稿与图例精修

基于 claim ownership 只执行 9 项窄幅修改，并用 CSV ledger 保存 old/new text：

1. `authoritative source` 改为事实性的 `source matrix`。
2. 外部验证从 `qualified/statistical engine` 改为可复现的 `checked/verified statistical implementation`。
3. `camera FDR` 修正为 `CAMERA FDR`。
4. `analog` 统一为英式 `analogue`。
5. Methods 中外部验证工程措辞同步收敛。
6. GSE23307 明确 genes 未被当作 biological replicates。
7. Reproducibility 中 `statistical-engine qualification` 改为 `statistical-implementation verification`。
8. Figure 1 legend 明确 retained scaffold 与未保留的 hard fine states。
9. Figure 5 legend 明确 ULM evidence ownership 与 frozen positive-arm wording。

没有修改任何 cell/donor/sample count、effect、CI、P/q value、NES、target count、reference 或 citation 编号。

## 7. 文档生成与逐页 QA

生成文件：

- `documents/Manuscript_scientific_harmonization_candidate.docx`
- `documents/Manuscript_scientific_harmonization_candidate.pdf`
- `documents/Supplementary_Information_scientific_harmonization_candidate.docx`
- `documents/Supplementary_Information_scientific_harmonization_candidate.pdf`

主文保持 32 页。补充材料第一轮渲染为 17 页，发现 Table S6 续表后人为强制 Table S7 换页，造成第 4 页大面积空白。移除该强制分页后，最终补充材料为 16 页；Table S7 与 S6 续表在第 4 页自然衔接，S1-S10 均各自保持同页图题与图像。

视觉检查：

- 主文 32/32 页检查完成。
- 补充材料 16/16 页检查完成。
- 合计 48/48 页，无 clipping、overlap、missing glyph、异常孤立 `X`、空白页或参考文献溢出。
- 主文 accessibility：0 high / 0 medium / 0 low。
- 补充材料 accessibility：0 high / 0 medium / 0 low。
- 最终 contact sheets 保存在 `qa/final_contact_sheets/`；逐页临时 PNG 与第一轮失败版式已清理。

最终 PDF：

- Manuscript：245,280 bytes；SHA-256 `7F17F2C8AB393DF6C86488C0B175F1BEE5EDB1034A34DC4AB0D16E3170D7C50D`
- Supplementary Information：2,713,086 bytes；SHA-256 `D7DBB0151AE79F9A47027996FE94E93057612E7264703C376336857CDF1686CB`

## 8. 自动化与测试

新增或扩展：

- `audit_tools/phase17_npj_sba_16_integrate_selected_supplementary_refinement.py`
- `audit_tools/phase17_npj_sba_17_build_scientific_harmonization_documents.py`
- `audit_tools/phase17_npj_sba_18_finalize_scientific_harmonization_qa.py`
- `audit_tools/test_npj_sba_selected_supplementary_refinement.py`
- main/S4/S10 builders 的 opt-in refinement flags；默认行为保持不变。

测试结果：

- 新增定向测试：6/6 PASS。
- 全仓库 `unittest`：122/122 PASS。
- 环境未安装 pytest；按项目既有规范使用标准库 `unittest`，没有临时安装新依赖。

## 9. 本轮科学判断

目前最强、最诚实且逻辑闭合的主轴仍是：过程层面的 B_CONV IFN/ISG remodeling 比 hard state assignment 更可重复。R1 的 B_ASC-specific HOLD 和 corrected external remapping 的 calibration HOLD 都应作为结论边界保留，永不通过改图或改措辞“救成 PASS”。

本轮没有发现要求重跑 Figures 2-4、S1-S3 或 S5-S9 的实质缺陷。继续对这些图做审美性重绘的收益已经低于风格漂移、引入错误和 claim duplication 的风险。因此，当前 5 主图 + 10 补图可冻结为新的 scientific presentation candidate，但不能自动替换作者已确认的 exact submission package。

## 10. 下一阶段目标

建议下一阶段命名为：

`FULL_SCIENTIFIC_CANDIDATE_COHERENCE_AND_CLAIM_ORDER_REFREEZE`

工作范围应限制为：

1. 逐段检查 Title、Abstract、Results headings、Discussion 和 Conclusion 的 claim 顺序是否都遵循同一 evidence hierarchy。
2. 删除 Results 与 Discussion 间的重复数字或重复边界陈述，但不弱化 R1/C9R HOLD。
3. 检查每个主图 legend 与正文第一次引用是否有明确 evidence owner。
4. 检查 Supplementary Tables S2/S3/S9 与主文 boundary wording 是否逐项一致。
5. 完成后对 exact DOCX/PDF 做一次 LibreOffice + WPS 双渲染 refreeze；除发现可定位的科学或版式缺陷外，不再重画图或重跑分析。

下一阶段不应新增 cohort、mapper、regulator、gene set 或 post hoc sensitivity，也不应进入投稿 portal 工程。

## 11. 复现命令

```powershell
Set-Location "H:\cuhk-2025fALL\6013RP-wyf"

python .\audit_tools\phase17_npj_sba_16_integrate_selected_supplementary_refinement.py

& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell `
  python .\audit_tools\phase17_npj_sba_17_build_scientific_harmonization_documents.py

# DOCX rendering uses the bundled document renderer and LibreOffice before finalization.

& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell `
  python .\audit_tools\phase17_npj_sba_18_finalize_scientific_harmonization_qa.py

& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell `
  python .\audit_tools\test_npj_sba_selected_supplementary_refinement.py -v

& "C:\ProgramData\miniforge3\condabin\conda.bat" run -n sle-bcell `
  python -m unittest discover -s audit_tools -p "test_*.py"
```
