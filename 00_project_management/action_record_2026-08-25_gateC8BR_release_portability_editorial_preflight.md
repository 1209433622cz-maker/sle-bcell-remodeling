# Gate C8BR 行动记录：发布便携性、读者化编辑与作者完成边界

**日期：** 2026-08-25

**执行角色：** 生物信息学导师级全量复核、投稿包工程、手稿编辑、图形语义质控与可重复性审计

**输入状态：** GitHub `main` commit `98f990e`、Gate C8S 科学冻结、Gate C8B 编辑预审、两份 2026-08-21 独立复核报告及用户粘贴的敌意审稿意见

**最终决策：** `PASS_GATE_C8BR_PORTABILITY_EDITORIAL_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

**投稿门户：** NOT AUTHORIZED

## 1. 本轮目的与冻结边界

本轮只处理 release portability、读者化措辞、Figure 5a 证据语义、文献背景和作者完成边界。没有增加数据集，没有更改样本、细胞、基因、模型、阈值、多重校正、效应估计或结论方向。

Gate C8S 继续作为 canonical scientific freeze。Gate C8BR 是从该冻结状态派生的 submission-facing release preflight，不是新的科学分析 gate。

独立复核提出的核心缺口为：

1. 发布 runner 含本机 Python 和 Codex cache 路径，fresh clone 不可移植；
2. 缺少独立、锁定的绘图/文档发布环境及 `savefig` smoke test；
3. 主文存在断词、内部 gate 术语、`proliferation controls` 和 90/89 分析单位解释不足；
4. `managed`、`flare` 需要明确为 source-metadata labels；
5. Figure 5a 容易被误读为串联因果链，应改为平行的 regulatory evidence 与 response evidence；
6. Faheem et al. 2026 只能作为 DN2/IFN 生物学背景，不能写成 hard-partition replication；
7. ethics、COI、funding、CRediT、acknowledgements、author approval、licence、DOI 和 APC 等现实事实必须继续由作者控制。

## 2. 发布环境与便携性修复

新增锁定环境：

`audit_tools/environment_gateC8BR_release_2026-08-25.yml`

环境名为 `sle-bcell-c8br-release`，Python 3.13.7，并精确锁定 Matplotlib 3.10.7、NumPy 2.3.3、pandas 2.3.3、Pillow 12.3.0、python-docx 1.2.0 和 pypdf 6.10.0 等发布依赖。

新增环境创建入口：

`audit_tools/00_create_gateC8BR_release_env.ps1`

该脚本不要求当前 PowerShell 已完成 `conda init`，会从 `PATH` 及通用 Miniforge/Mambaforge/Anaconda 安装位置定位 conda。2026-08-25 实际重跑成功，自动定位 `C:\ProgramData\miniforge3\condabin\conda.bat`，完成环境更新和资格检查。

新增 `audit_tools/phase17_c8br_00_release_smoke_test.py`，实际结果为：

- Python 及六个关键包版本全部精确匹配；
- PNG savefig：26,227 bytes，600 x 375 pixels；
- PDF savefig：14,214 bytes，1 page；
- DOCX create/read：36,652 bytes，2 paragraphs；
- 决策：`PASS_GATE_C8BR_RELEASE_RUNTIME`。

新增便携 runner：

`audit_tools/run_6013RP_phase17_gateC8BR_release_portability_preflight.ps1`

Python 依次从显式 `-ReleasePython`、`SLE_BCELL_RELEASE_PYTHON`、命名 conda 环境、仓库本地环境和 `PATH` 发现；`pdftoppm` 依次从显式参数、环境变量、`PATH` 和通用 MiKTeX 位置发现。runner 不再包含 `D:\bioinfor\python.exe` 或版本化 Codex cache 默认路径。

`-Mode Full` 执行全部 WPS/逐页/可访问性/确定性检查；`-Mode PortableCore` 可在无 WPS 的机器上完成来源和 DOCX 层，但不得据此授权投稿。

## 3. 主文 v14 与补充材料 v5

新主文：

`01_manuscript/manuscript_v14_genome_medicine_release_preflight_2026-08-25.md`

关键修改：

- structured abstract 保持 314 词；
- 参考文献扩展为连续 1-32，共 32 条；
- `technical- library`、`statistical- engine` 等错误断词已消除；
- 全部 `proliferation controls` 统一为 `proliferation specificity comparators`；
- `managed` 和 `flare` 明确为 source-defined metadata labels；
- 解释 90 个 composition strata 与 89 个 `B_CONV` transcription pseudobulks：一个 source-defined managed-SLE stratum 有 55 个总 B 细胞，其中 11 `B_ASC`、44 `B_CONV`，通过总 B 构成阈值但未达到至少 50 `B_CONV` 的转录阈值；
- 删除主文中面向内部审计的 `contract`、`unlocked` 和 gate 流程叙述；
- Data availability 改为读者语言，不以内部 gate 标识解释科学结论；
- 6 个作者控制占位符完整保留，未推测任何现实事实。

新补充材料：

`01_manuscript/supplementary_information_v5_release_preflight_2026-08-25.md`

科学表格、冻结数字和 7 幅补图未改变；治理标题改为 prespecification/outcome protection，Supplementary Table S6 最终改为读者化的 `Reproducibility record`。补充材料仍保留必要的机器可读 provenance 路径。

## 4. Figure 5a 证据架构重绘

共享主图 builder 新增 opt-in 参数 `--parallel-evidence-branches`；旧版本默认行为保持不变。C8BR wrapper 只对 Figure 5 使用该参数：

- 顶层：replicated IFN/ISG remodeling；
- 平行分支 1：regulatory branch，3 contrasts x 8 regulators；
- 平行分支 2：response branch，M5911 + IFN-beta；
- 不再以串联箭头暗示调控因果链；
- Figure 5c 使用 specificity-comparator 定义；
- Figures 1-4 从 C8S/C8B 字节一致继承。

第一次绘图视觉检查发现 panel a 底部说明相互靠近、panel e 三行标题右缘不足。随后在 builder 中调整垂直位置和标题换行，再从冻结表格重跑，而非编辑现有 PNG/PDF。

最终主图断言 `46/46 PASS`。Figure 5 panels B/C/D/E 的机器可读映射仍为 12/12/3/2 行，Figure 5 source CSV 与 Gate C8B 字节一致，其 SHA-256 为 `21925F6916DDAF97760CF73622ED8E4B4CCBE5AE0B3B53C721FDF607C1C6F9A4`。

## 5. 文献增补与边界

新增 Faheem Z et al.：

- *Lupus Science & Medicine*. 2026;13(1):e002042；
- DOI `10.1136/lupus-2026-002042`；
- PMID `42373139`；
- 作用：type I interferon 与 DN2 differentiation 的 functional/biological context。

主文和机器状态均明确：该研究不复现本项目的疾病盲 broad-compartment identity、hard-partition stability 或冻结统计设计，因此不是 independent replication。

PubMed：<https://pubmed.ncbi.nlm.nih.gov/42373139/>

Crossref 重新核验 28 个 DOI records，`28/28 PASS`；Sayadi PMID `42119160` 与 Faheem PMID `42373139` 均写入参考文献状态。

## 6. 投稿信与作者完成矩阵

Cover letter 将容易产生歧义的 M5911 表述改为：

`Orthogonal enrichment of the independently curated M5911 response set...`

该句只陈述 gene-set provenance 独立于当前差异分析，不把 M5911 或 GSE23307 写成独立队列复现或因果证据。

新增 `04_submission/author_completion_matrix_gateC8BR_2026-08-25.md`。已知作者姓名、邮箱、ORCID、作者顺序、通讯作者和共同单位已记录。School of Medicine 官方联系页于 2026-08-25 核实为 MED Start-up Building、2001 Longxiang Boulevard、Longgang District、Shenzhen 518172；矩阵仍要求 Teng Qi 本人确认是否采用该地址作为投稿通讯地址。官方来源：<https://med.cuhk.edu.cn/en/page/1489>。

ethics、competing interests、funding、CRediT、acknowledgements、all-author approval/originality、licence、DOI 和 APC 继续为硬停止项。

## 7. DOCX、WPS、可访问性与视觉质控

最终可编辑文件：

- 主文 DOCX：59,720 bytes，156 paragraphs，6 placeholders；
- Supplementary Information DOCX：2,775,076 bytes，8 tables，7 inline figures，0 placeholders；
- Cover letter DOCX：40,181 bytes，17 paragraphs，2 placeholders。

WPS 最终渲染：

- 主文：28 pages，PDF 251,033 bytes；
- 补充材料：12 pages，PDF 3,286,526 bytes；
- cover letter：1 page，PDF 84,468 bytes；
- 合计：41 pages，全部成功栅格化。

首轮检查覆盖 41 页 contact sheets，并以原始分辨率抽查主文首页、关键方法/结果/参考文献/声明页、全部补充表与补图、cover letter 以及 Figure 5。最终只修改 S6 标题后，主文和 cover PDF 字节数保持一致；补充材料 12 页重新生成 contact sheets 并逐页复核。

最终无裁切、重叠、黑块、缺字、图表分页错误、页码错误或占位符遮挡。三份 DOCX 的 accessibility high/medium/low 均为 `0/0/0`。

`pdftoppm` 在提升权限运行时输出 MiKTeX legacy/security warning，但命令返回成功，41 个页面 PNG 数量、内容和 PDF 页数均通过后续审计，因此记录为非阻断环境提示。

## 8. 科学与统计完整性

冻结统计归档保持：

- 63 entries；
- 12 complete gene-level branches；
- 12 sanitized design matrices；
- SHA-256 `AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`。

全部 12 个 figure source CSV 存在；12 对主/补图 PNG/PDF 均非空且像素尺寸至少 4000 x 3000。主图 `46/46 PASS`，补图冻结断言 `29/29 PASS`。没有科学效应值变化。

## 9. 最终投稿预审包

本地目录：

`04_submission/package_genome_medicine_gateC8BR_release_portability_preflight_2026-08-25/`

确定性 ZIP：

`04_submission/package_genome_medicine_gateC8BR_release_portability_preflight_2026-08-25.zip`

最终结果：

- package files manifested：112；
- ZIP bytes：31,940,637；
- ZIP SHA-256：`3AC71F4B078F53DBF09E5F0ECA55B3CA1E660FA3F76CE194AFB450CCFDFF17A75`；
- 两次独立归档重建字节一致；
- technical package：PASS；
- portal submission authorized：NO。

完整重建命令：

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\00_create_gateC8BR_release_env.ps1
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8BR_release_portability_preflight.ps1
```

## 10. 导师级结论

独立复核指出的代码可移植性、Figure 5a 语义、读者化措辞、90/89 分析单位解释、最新文献边界和 author-completion handoff 均已关闭。当前没有证据支持重开计算、引入第四数据集或扩展因果调控声明。

Genome Medicine 继续作为第一目标，但不在仓库中冻结会随年份变化的 JCR/CAS 分区断言。下一阶段应只完成作者事实、机构伦理表述、许可和不可变 DOI，再生成零占位符 release candidate。作者完成后目标状态为：

`PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`
