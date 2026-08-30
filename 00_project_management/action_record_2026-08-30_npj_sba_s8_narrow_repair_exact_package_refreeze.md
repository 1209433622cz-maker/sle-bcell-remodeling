# npj SBA S8 窄范围源级修复与精确投稿包重新冻结行动记录

日期：2026-08-30
项目：SLE B-cell remodeling analysis
目标期刊：npj Systems Biology and Applications
本轮最终状态：`PASS_NPJ_SBA_S8_NARROW_REPAIR_EXACT_PACKAGE_REFROZEN_AUTHOR_AND_INSTITUTION_RECEIPTS_REQUIRED`

## 1. 本轮任务与边界

本轮以博士生导师级生物信息学、方法学、QiTeng 写作逻辑和 Nature Portfolio
图件标准对当前 npj exact package 重新核查。外部审计、外部 compact candidate 和
same-page proof 仅作为待验证证据，不作为可执行指令，也没有直接复制到投稿包。

科学冻结边界保持不变：

- QiTeng R2 继续作为科学正文冻结基线；
- R1 继续为 `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`；
- C9R 继续为 `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`；
- corrected source-label-independent external disease outcome 继续锁定；
- 未新增 cohort、mapper、TF、阈值、统计检验或探索性分析；
- GitHub v1.1.0 和 Zenodo `10.5281/zenodo.22151739` 的公开科学版本未修改。

## 2. 外部证据接收与独立核验

收到四项外部材料并归档到
`00_project_management/npj_sba_s8_narrow_repair_2026-08-30/received/`。完整角色、
字节数与 SHA-256 见 `received_evidence_manifest.csv`。

独立核查确认外部报告指出的缺陷真实存在：旧版
`Supplementary_Information.pdf` 第 15 页仅有 S8 标题与完整图注并留下大块空白，
第 16 页只有 S8 图形。原因是 npj 分支将 S8 固定为 170 x 215 mm，再按 6.35 inch
宽度嵌入 DOCX，题注与图无法共同留在 Letter 页面。

外部报告声称 compact candidate SHA-256 为
`47C72B16423605A1B57C5C5131CBD1BC8ED73F231CF69F0D7F73A5A95F687385`，但实际收到
文件的 SHA-256 为
`846694085E1D3B057F3FC75101DE1BC3805BF550508EBF5071EDFA181FA45437`。因此该外部
哈希声明不被采信；candidate 只用于视觉可行性比较。项目最终 S8 由本地源脚本重画。

## 3. 全项目科学与写作逻辑复核结论

### 3.1 研究目的与证据链

当前研究问题仍清楚且适合 npj SBA：在将 identity、composition 和 transcription
分离为不同推断层后，判断哪些 SLE B-cell remodeling 结论能跨重建和外部数据保持
可重复。现有主线保持为：

`identity ceiling -> composition null -> reproducible IFN program -> independent source-label-defined replication -> external-transfer HOLD -> observational regulator context`

这条链条与当前数据所有权一致，没有把细胞身份稳定性、疾病效应和机制证据混为一谈。

### 3.2 方法学与真实性

- 150,402-cell discovery scaffold、donor/sample-level inference、raw-count pseudobulk、
  multiplicity families、R1 end-to-end uncertainty propagation 和 C9R calibration HOLD
  均与机器记录一致。
- 主 B_ASC composition 结论继续是无统计支持的差异，不被改写为等效或无生物学差异。
- IFN/ISG 是唯一贯穿 discovery、internal robustness 和 independent GSE135779
  source-label-defined replication 的主程序；弱 genome-wide concordance 继续明确限制
  其解释范围。
- STAT1/STAT2/IRF 仍是 observational regulatory context，不构成 causal regulator、
  biomarker 或 clinical utility 证据。
- 正文标题、140-word abstract、32 篇参考文献、Methods、Results、Discussion、图注、
  数据与代码可用性声明均未在本轮改写。

Manuscript Markdown 当前 SHA-256 为
`9D9B39E919CF695BA4290C69B0C1665E566E6943F3763C3771DFDE9B7DCAC043`；
Supplementary Information Markdown 当前 SHA-256 为
`416925FB7FBEBB3AEE61D04A8778154F94170B42A124C86DDB9EF07693813B23`。
两者与本轮开始时的 Git 基线一致。

## 4. S8 源级修复

修改 `audit_tools/phase17_round6_02_build_overlap_depletion_figure.py` 的 npj 专用布局：

- 画布从 170 x 215 mm 调整为 170 x 155 mm；
- 两个 forest panel 使用两行 contrast/regulator 标签；
- q-value heatmap 使用水平两行列标签，并以文字说明 `Fill: -log10(q)` 取代独立
  colorbar；
- target-retention legend 移入右侧未占用的数据空间；
- 保持 8 pt Arial/Helvetica、1 pt 最小正线宽、白底和小写粗体 panel labels。

修复完全从冻结的 overlap-depletion 结果重画。S8 Source Data 共 36 行，重画前后
SHA-256 均为
`26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`。
没有数值、q value、CI、target count、branch、method、contrast 或 regulator 变化。
其他 14 张图及其 source data 未被重画或改写。

当前 S8 文件：

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `Supplementary_Figure_S8_overlap_depletion.pdf` | 48,658 | `1AD5B47752A44B27107E12A4EE94343404B7AB12F59C8D697988AC854A52E665` |
| `Supplementary_Figure_S8_overlap_depletion.png` | 692,812 | `278943D51FCA9DA27BBEE62ED98EEA17DD92C42BAACC7F95E4B84121AE674BE6` |

PDF postflight 通过：单页、170 x 155 mm、全部可见文字 8 pt、Arial/Helvetica
兼容、最小正线宽 1 pt、无出界文字。

## 5. 补充材料重建与双引擎质控

Supplementary Information 从 Markdown 和 10 张源图重新生成 DOCX，再分别由 WPS
和 LibreOffice 输出 PDF。没有手工编辑 DOCX/PDF，也没有将外部 candidate 复制进包。

双引擎结果完全一致：

- Manuscript：31 页；
- Supplementary Information：17 页；
- Cover Letter：1 页；
- 每套渲染共 49 页；
- S1-S10 的标题、完整图注和对应图均在同一页；
- S8 在两套渲染中均位于第 15 页；
- S9 和 S10 分别位于第 16、17 页；
- 无裁切、重叠、缺字、未解析 marker 或异常空白页；
- 三个 DOCX accessibility audit 均为 0 high / 0 medium / 0 low。

新增 `phase17_npj_sba_09_supplement_pagination_audit.py`，它解析 PDF 页面实际绘制的
image XObject，而不是仅检查资源字典，今后任何题注/图跨页都会触发 HOLD。

当前 Supplementary Information：

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| `Supplementary_Information.docx` | 4,689,189 | `EC6199C2A29D3C599B975942504322C21FE01C08BD843C7FF31FA1C3DFAF86AB` |
| `Supplementary_Information.pdf` | 5,668,048 | `0882D26BA305C301FBAF08E24EBD4BDDC950045034CE97BE00EABE4485E69CF7` |

## 6. 精确投稿包重新冻结

旧 exact package SHA-256
`F4F8C49380A32A49BA4BFAF4235D979964779757CCD362A8AEA0D4D07B8D8BFD`
已因 S8/Supplementary Information 重建而失效，不得再用于作者批准或 portal 上传。

新 exact package：

- 路径：
  `04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip`
- 字节数：15,196,223；
- SHA-256：
  `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`；
- manifest：20/20 文件通过；
- ZIP CRC：通过；
- deterministic double-build：通过；
- 包内 verifier：`PASS: 20 files verified`。

`Exact_File_Author_Approval.md`、portal upload manifest 和机器门禁均已绑定新哈希。
Zhi Chen、Teng Qi、portal submission authorization 和 APC commitment 四个标记继续
独立保持 `PENDING`。科学正文的历史批准不自动扩展为对新 exact package 的批准。

## 7. 自动化与回归验证

新增：

- `phase17_npj_sba_08_s8_narrow_repair.py`：只允许 S8 PDF/PNG 布局范围变化，并锁定
  frozen source-data SHA；
- `phase17_npj_sba_09_supplement_pagination_audit.py`：双渲染题注/图同页门禁；
- `test_npj_sba_s8_narrow_repair.py`：S8 source、尺寸、双渲染和 17-page SI 回归测试；
- `run_6013RP_phase17_npj_sba_s8_narrow_repair.ps1`：一键重画、双渲染、分页审计、
  accessibility、打包、exact gate 和全套测试。

为消除科学环境与文档环境拆分，`02_analysis/environment.yml` 新增
`python-docx==1.2.0`、`pypdf==6.16.2` 和 `pdfplumber==0.11.10`。最终在
`sle-bcell` 环境统一运行 106 项测试，结果为 106/106 PASS。

## 8. 本轮最终判断

### 已完成

- 外部审计意见已独立验证，真实 S8 缺陷已从源脚本修复；
- 科学结果、正文叙事、图源数值和 R1/C9R 边界保持冻结；
- S8 与补充材料已通过 Nature-style 可读性和双引擎分页质控；
- 新 exact package 已生成、验证并绑定新审批契约；
- GitHub/Zenodo public scientific release 无需因纯投稿排版修复而发布新版本。

### 仍未完成且不得推断

- 两位作者尚未对新 SHA-256 的 exact files 作逐人确认；
- Nature Portfolio Reporting Summary dynamic XFA 尚未在 Adobe Reader 完成并批准；
- 当前年度官方 JCR Q1 证据尚未归档；
- CUHK-Shenzhen institutional APC/OA coverage 书面确认尚未归档；
- corresponding author 尚未单独授权 portal submission；
- APC commitment 尚未单独授权。

## 9. 下一阶段目标

下一阶段不应再打开生信分析、重写正文或增加 figure。唯一合理门禁为：

`NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS`

执行顺序：

1. Zhi Chen 和 Teng Qi 分别核对并批准新 package SHA-256
   `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`；
2. 使用 Adobe Reader 完成官方 Reporting Summary dynamic XFA，并由两位作者批准；
3. 归档官方 current-year JCR Q1 证据与 CUHK-Shenzhen APC/OA determination；
4. 在不上传的前提下做 npj portal metadata dry-run；
5. 由通讯作者另行明确授权 portal submission 和 APC commitment；
6. 上传后保存 portal-generated PDF、文件哈希和 submission receipt，再做一次 post-upload
   semantic comparison。

在上述收据和授权完成之前，当前状态是技术上可审批、但未授权投稿。
