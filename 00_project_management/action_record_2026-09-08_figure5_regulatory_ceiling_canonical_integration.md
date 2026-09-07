# 行动记录：Figure 5 调控上限来源重绘与科学重冻结

- **完成日期：** 2026-09-08
- **最终状态：** `SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`

## 1. 本轮问题与独立裁决

外部 hostile read 建议用 IFN-overlap depletion 取代旧 Figure 5d 的三根 M5911 NES 柱。独立复核确认科学方向成立，但没有直接采用外部整图：其 Figure 5b 左侧标签在 170 mm 组合图中发生明显裁切，不能作为 canonical artwork。外部文件仅作为候选数值、结构和可读性证据归档；正式图从哈希锁定的 Figure 5 与 Supplementary Figure S10 Source Data 重新构建。

最终裁决为：Figure 5a、5b、5c、5e `KEEP`；旧 Figure 5d `REPLACE`。旧 5d 的 M5911 enrichment 数值不删除，而是归入 Figure 5a evidence summary 与 Supplementary Table S3。新 5d 由 S10 的 12 条 ULM depletion 记录重绘，S10 和 Supplementary Table S4b 继续拥有 ULM/CAMERA/FRY 全量审计。

## 2. 来源、算法与数值核验

- 冻结 Figure 5 Source Data SHA-256：`A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B`。
- Supplementary Figure S9 Source Data SHA-256：`D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3`。
- Supplementary Figure S10 Source Data SHA-256：`26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`。
- 12-gene IFN/ISG arm 去除后，discovery、nonoverlap、childhood 三个 contrast 的 STAT1/STAT2 共 6 个 ULM 95% CI 全部位于 0 右侧。
- 97-gene M5911 去除后，唯一跨 0 的 ULM 区间是 discovery STAT2：estimate 0.3906577146，95% CI -0.7450461772 至 1.5263616063，q=0.5001111487，保留 8/14 targets。
- 正文和图中按既有精度报告为 slope 0.391、95% CI -0.745 至 1.526、q=0.500；机器精度值由专项回归锁定。
- 没有重跑样本级模型、改变 ranked statistics、tested-gene backgrounds、CollecTRI signs、contrasts、model matrices 或多重校正家族。

## 3. 图件重绘与子图职责

- Figure 5a：`KEEP`，概括 ULM、M5911 与 IFN-beta 三类证据及其解释等级。
- Figure 5b：`KEEP`，拥有 core STAT1/STAT2 与 extended IRF7/IRF9 的观测性 activity slopes。
- Figure 5c：`KEEP`，拥有预设 proliferation specificity comparators。
- Figure 5d：`SOURCE_REPLACEMENT_FROM_LOCKED_S10_ULM`，对照 12-gene arm 与 M5911 depletion，并显式标出 discovery STAT2 的跨零例外。
- Figure 5e：`KEEP`，拥有两名健康 donor 的描述性 IFN-beta paired gene effects。
- 最终 Figure 5 尺寸 170.0 mm x 211.0 mm；完整 170 mm 图与半栏裁切均完成可读性检查。
- Figure 5 Source Data 从 53 行扩展为 65 行：原 3 条 M5911 NES 记录由 panel D 改归 panel A，新增 12 条来源于 S10 的 ULM depletion 记录归 panel D。
- 45 个 figure/source-data 资产中仅 Figure 5 PDF、PNG 与 Figure 5 Source Data 三项改变，其余 42 项哈希不变。

## 4. 手稿同步与图例经济性

仅执行三项来源级语义操作：把 overlap-depletion ceiling 引用提升到 Fig. 5d；将 M5911 summary 指向 Fig. 5a/Supplementary Table S3、GSE23307 指向 Fig. 5e；同步 Figure 5 图例。首次扩展图例导致 WPS 与 LibreOffice 均出现仅 228 字符的第 32 页，故没有接受该版。

最终 Figure 5 图例整体压缩到 122 词，同时保留 evidence class、三组 contrasts、global 24-test q、两条 depletion branch、discovery STAT2 跨零例外、S10/S4b 全量主权和 n=2 限制。压缩后双引擎均恢复为 31 页。Title、145 词 Abstract、Discussion、Conclusion、33 篇参考文献、Figure 1-4、Supplementary Information 均未改变。

## 5. 文档、视觉与回归 QA

- Figure 5 PDF SHA-256：`287E6A792E5CD7AE656258301BD406FEEFF4F0D75F160BC6A0F7168BDB97943A`；PNG SHA-256：`D49135815FFB555170E6AE9B1B3909411BE2775AE8FA5ED50000CD987A921A5A`。
- WPS 主文：31 页，SHA-256 `58C3463C02BA45D176E891A4BDC037B740F0940155A03AE29E4D5ED4EB36A4F8`。
- LibreOffice 主文：31 页，SHA-256 `BECCFB18E69EA1E577B18F5FCD346A1345A7E93D18DE997898037BEDFE14940D`。
- 双引擎共 62 页、12 张原始联系表已逐页视觉检查；无空白页、截断、重叠、缺字、异常分页或孤立尾页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：201/201 通过；最终 manifest 写入后再次运行全量回归。
- 投稿包 SHA-256 保持不变；Release 与 Zenodo 未触碰。

## 6. 当前科学判断

新 Figure 5d 比旧 M5911 NES 柱具有更高的主图信息增益。它同时说明两件事：STAT1/STAT2 信号并非 12-gene IFN/ISG core program 的简单重述；但 broader interferon-response transcriptome 去除会使 discovery STAT2 明显衰减并跨 0。因此新图不是增加一个“阳性机制结果”，而是把 regulatory ceiling 放入读者第一视野，与 Figure 1 的 identity ceiling 和 Figure 4 的 transfer-calibration ceiling 构成一致的推断边界逻辑。

## 7. 下一阶段目标

下一阶段进入 `SCIENTIFIC_PRESENTATION_FINAL_CROSS_DOCUMENT_FREEZE`。不再主动寻找新的 panel 替换，也不重新开启统计模型；只对当前主文、Figure 1-5、Supplementary Information、S1-S10、Source Data 与 claim-owner/cross-reference 做一次终局跨文档冻结核查。只有发现局部、可复现的科学语义或排版缺陷时才允许重开对应对象，否则转入科学呈现维护冻结。
