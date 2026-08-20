# Gate C8B 行动记录：编辑语义、最新文献与投稿前技术预审

**日期：** 2026-08-21

**执行角色：** 生物信息学导师级项目复核、手稿编辑、图形重绘、参考文献核验与投稿包工程

**输入状态：** GitHub `main` commit `c38f88d899baa2d265b141795f7963bead4d8974`、Gate C8S 冻结结果、用户提供的独立复核意见

**最终决策：** `PASS_GATE_C8B_EDITORIAL_LITERATURE_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

## 1. 本轮目标与边界

本轮不新增数据集、不改变模型、不重估效应值，也不重新选择基因、调控因子或验证分层。唯一目标是关闭独立复核指出的四个编辑与定位缺口：

1. 将 Figure 5c 的 `proliferation controls` 改为语义准确的 `proliferation specificity comparators`；
2. 纳入 Sayadi et al. 2026 的最新 SLE 单细胞 IFN 文献，并明确其仅为外部生物学背景，不是本研究冻结程序的独立复现；
3. 删除 Genome Medicine 可选且对本研究无必要的 `Authors' information` 作者简介；
4. 将 cover letter 中 `a type I IFN/ISG program` 改为 ligand-agnostic 的 `an interferon-responsive transcriptional program`。

Gate C8S 继续作为 canonical scientific freeze。Gate C8B 只派生 submission-facing 编辑版本。

## 2. 期刊与文献在线核验

### 2.1 Genome Medicine

2026-08-21 重新核验 Genome Medicine Research 官方说明：

- structured abstract 上限为 350 词；
- `Declarations` 及其规定子标题必须存在；
- `Authors' information` 明确为 optional；
- Background 应概述现有文献和研究必要性；
- Discussion 应把结果置于既有研究背景并说明局限。

官方页面：<https://link.springer.com/journal/13073/submission-guidelines/research>

因此删除作者简介符合期刊规范，但 ethics、competing interests、funding、authors' contributions 和 acknowledgements 等必需声明不能删除。

### 2.2 Sayadi et al. 2026

PubMed 与 DOI/Crossref 元数据核验结果：

- Sayadi A, Eloranta M-L, Oparina N, Wallgren M, Skoglund E, Frodlund M, et al.;
- *Journal of Autoimmunity*. 2026;161:103575；
- DOI `10.1016/j.jaut.2026.103575`；
- PMID `42119160`；
- 研究包括 16 名低疾病活动、仅接受抗疟药治疗的女性 SLE 患者和 6 名健康对照；
- 论文将持续 IFN 活性与较高 polygenic risk 联系起来，并报告多个免疫细胞区室中的 IFN 信号。

PubMed：<https://pubmed.ncbi.nlm.nih.gov/42119160/>

本稿使用边界：该研究没有使用我们的疾病盲 `B_CONV` 定义、冻结 12-gene IFN positive arm、两个主数据集或相同统计设计，因此只作为 contemporary external biological context，绝不写成 independent validation。

## 3. 手稿 v13 编辑

新主文源：

`01_manuscript/manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md`

完成内容：

- 保持标题、摘要、方法、所有数值和结论边界不变；
- Background 增加两句 Sayadi 研究定位，明确 `contextual rather than replication evidence`；
- Discussion 增加一句与 managed/low-disease-activity SLE 的联系，同时明确 `external biological context rather than independent validation`；
- 参考文献由 30 条增至 31 条，编号连续；
- structured abstract 保持 314 词，低于 350 词限制；
- 删除 `Authors' information` 标题和作者个人简介；
- Figure 5c legend 改为 `proliferation specificity comparators`；
- Data availability 明确 Gate C8S 是科学冻结，Gate C8B 仅为编辑和文献预审；
- 6 个 manuscript 作者受控占位符保持原样，没有擅自填充未知事实。

新补充材料源：

`01_manuscript/supplementary_information_v4_gateC8B_editorial_preflight_2026-08-21.md`

其科学表格、7 幅补图和冻结统计值未改变，仅更新版本、活动主文路径和 Figure 5c 编辑说明。

## 4. Figure 5 重绘与视觉修复

新增 `audit_tools/phase17_c8b_00_build_main_figures.py`：

- Figures 1-4 从 Gate C8S 字节一致继承；
- Figure 5 从冻结 Gate C6B 表格重新渲染；
- Figure 5 source CSV 从数据重建，不从图像回抄；
- 合并后主图断言仍为 `46/46 PASS`；
- panel B/C/D/E 的数据映射保持 12/12/3/2 行；
- 没有绘图值变化。

第一次视觉检查发现 Figure 5c 的新长标题被 panel 右边界裁切。该问题未被数值断言发现，但被 PNG 肉眼检查拦截。随后将标题改为两行：

```text
Prespecified proliferation
specificity comparators
```

重新渲染后，标题完整、与 panel b 层级一致、未覆盖数据或相邻 panel；PDF 文本提取也能恢复完整短语。

## 5. 参考文献核验

新增 `audit_tools/phase17_c8b_01_verify_references.py`，通过 Crossref REST API 重新核验全部 DOI 文献：

- DOI records：27；
- PASS：27/27；
- manuscript references：31；
- 新增 DOI 与返回 DOI 一致；
- title token 与 Crossref 标题一致；
- PMID 42119160 和 `context only` claim boundary 写入机器可读状态。

输出目录：

`phase17_v7/gateC8B/20260821_editorial_literature_preflight/references/`

## 6. DOCX、WPS 与视觉质控

生成三份可编辑 DOCX：

- 主文：59,329 bytes，155 paragraphs，6 placeholders；
- Supplementary Information：2,775,124 bytes，8 tables，7 inline figures，0 placeholders；
- Cover letter：40,168 bytes，17 paragraphs，2 placeholders。

WPS 后台渲染：

- 主文：27 页；
- 补充材料：12 页；
- cover letter：1 页；
- 合计：40 页。

视觉质控覆盖所有页面 contact sheets，并在 100% 页面图中复核主文 pages 3、17、20、23、27，补充材料 pages 1、4，cover letter page 1 和重绘 Figure 5。确认：

- 无文字裁切、重叠、黑块、缺字或页脚丢失；
- line numbering 连续且不遮挡正文；
- authors' information 已删除，Declarations 其余结构完整；
- 新文献段落和 reference 31 均完整；
- Supplementary Table S6 长路径可换行且不越界；
- 7 幅补图没有分页截断；
- 红色作者占位符清楚可见且未与正文重叠。

DOCX accessibility audit：三份文件 high/medium/low 均为 `0/0/0`。

## 7. 统计与源数据完整性

Gate C8B 没有改变科学统计归档。包内 `Additional_file_4_Full_Statistical_Results_GateC8S_FROZEN.zip` 保持：

- 63 entries；
- 12 complete gene-result branches；
- 12 sanitized design matrices；
- SHA-256 `AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`。

Figure source data：12 CSV + SHA-256 manifest；Figure 5 panel mapping再次核对为 B=12、C=12、D=3、E=2。

## 8. 环境异常与处置

当前 `C:\ProgramData\miniforge3\envs\sle-bcell\python.exe` 中 Matplotlib 3.11.0 在 Windows `savefig()` 时触发 native delay-load exception `0xC06D007F`。最小折线图也可复现，说明这是绘图运行时问题而非项目数据问题。

处置：Figure 5 使用已通过 PNG/PDF 保存 smoke test 的 `D:\bioinfor\python.exe`（Matplotlib 3.10.7、NumPy 2.3.3、pandas 2.3.3）渲染。该步骤只读取冻结 CSV，并由 46 项断言控制。C8B runner 默认使用该绘图解释器，同时保留参数供作者显式覆盖。

后续不要为了本稿提交阻断去升级/降级完整 Scanpy 环境；若需恢复全图重跑，应另建 pinned plotting environment 并进行最小 savefig smoke test。

## 9. 最终投稿预审包

本地目录：

`04_submission/package_genome_medicine_gateC8B_editorial_preflight_2026-08-21/`

确定性 ZIP：

`04_submission/package_genome_medicine_gateC8B_editorial_preflight_2026-08-21.zip`

最终状态：

- package files manifested：112；
- ZIP bytes：35,530,543；
- ZIP SHA-256：`C16E989528CB6EFC15E6E782112551136BE5612B806908E02E9DE5EF960CA917`；
- 两次独立 ZIP 重建字节一致；
- technical package：PASS；
- portal submission authorized：NO。

一键复跑：

```powershell
Set-Location H:\cuhk-2025fALL\6013RP-wyf
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8B_editorial_preflight.ps1
```

为保证 fresh clone 可重建，本轮显式跟踪四份小型 Markdown 源：Gate C8B cover letter、author completion form、journal target decision 和 reporting checklist。生成的 DOCX、PDF、page PNG、完整 package directory 和 ZIP 继续由 `.gitignore` 排除。

## 10. 导师判断

当前科学内容与投稿技术材料已达到可进入作者终审的成熟度。本轮没有发现需要重开数据分析或新增数据集的科学缺口。Genome Medicine 仍是证据结构最匹配的首投目标；继续添加公开横断面数据的边际收益低于异质性、分析自由度和叙事漂移风险。

下一阶段唯一目标是完成作者受控事实、机构伦理表述、代码许可和不可变 DOI，再进行一次无占位符 WPS 复核与 portal preflight。任何作者未知信息不得由分析人员推断。
