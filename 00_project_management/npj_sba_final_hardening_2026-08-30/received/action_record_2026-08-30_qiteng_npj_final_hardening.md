# 2026-08-30 QiTeng v0.3.21 + npj SBA 终局前硬化行动记录

## 1. 本轮输入

- 目标期刊：npj Systems Biology and Applications
- GitHub 最新主线复核基线：`0c7361022510b47e8cc7ae82baafd4b6dcff7c8e`
- 当前公开 reproducibility DOI：`10.5281/zenodo.22151739`
- 当前 target-specific manuscript 输入：`Manuscript(2).docx`
- 写作框架：`QiTeng_Academic_Writing_Skill v0.3.21`
- 本轮没有使用 PubMed，也没有新增文献或新数据集。

## 2. QiTeng 规则实际应用

本轮不是一般语言润色，而是按 v0.3.21 的以下控制逻辑执行：

1. `CENTRAL CLAIM -> GAP -> EVIDENCE -> BOUNDARY -> NEXT TEST`；
2. claim strength 不超过 E2 robust association；
3. `RESULTS = effect + uncertainty + multiplicity + robustness + short boundary`；
4. `DISCUSSION = finding -> context -> interpretation -> implication -> boundary`；
5. late-stage 使用 Salience & Detail Economy，压缩重复 caveat，而不是删除关键边界；
6. Control Plane / Manuscript Plane Firewall：不把 HOLD/gate/audit 等内部控制术语写成读者正文；
7. Figure Claim Gate：视觉标签不得强于正文证据；
8. Figure Object Persistence Gate：本轮 DOCX image audit 确认主文无 embedded figure objects，因此文本修改不存在图对象丢失风险。

## 3. 科学判断

本论文当前可辩护的核心贡献仍然是 **inferential novelty** 而非新 IFN biology：

- fine hard-state assignments 没有达到冻结稳定性要求；
- broad B_CONV/B_ASC 只能作为分析 scaffold；
- R1 end-to-end sensitivity 保持 HOLD；
- primary B_ASC abundance 不支持一般性 enrichment；
- B_CONV IFN/ISG 在 discovery、internal donor-nonoverlap、独立 GSE135779 source-label-defined analysis 中保持支持；
- genome-wide rho=0.026 限制为 program-level replication；
- corrected source-label-independent mapper 因 calibration failure 而不打开 disease outcome；
- STAT1/STAT2/M5911/GSE23307 仍属于 observational/response context，不升级为 direct mechanism 或 clinical utility。

因此本轮没有新增 cohort、mapper、gene set、regulator、threshold、seed 或 corrected disease outcome。

## 4. 文稿实质修改

完成 9 类 QiTeng late-stage edits：

- Introduction 将 “neither interferon activity nor plasmablast biology is novel” 改为 “well established yet strongly context dependent”，避免编辑层面自我削弱；
- Introduction 尾段把 `intended contribution` 改成明确 research task / evidence hierarchy；
- Results heading 明确 GSE135779 replication 是 `source-label-defined`；
- Discussion 同步 source-label ownership；
- limitation paragraph 压缩重复防御性措辞但保留全部边界；
- 删除旧 Conclusions 残留造成的第二个重复终结段，合并为单一 landing；
- Methods 外部验证标题与 Results 术语一致；
- Figure 1/4 legends 同步 source-label-defined ownership；
- running title 统一 `reproducible` 术语。

没有改变任何数值、样本量、P/q、CI、引用顺序、DOI、作者信息、CRediT、伦理或数据可用性陈述。

## 5. 新 manuscript 构建与 QA

输出：

- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.docx`
- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.pdf`
- `SLE_Bcell_Manuscript_QiTeng_npj_Hardened_2026-08-30.md`

校验：

- pages：31（原 target DOCX 32 页；删除重复终结段后自然减少 1 页）
- abstract：140 words
- DOCX accessibility：high=0, medium=0, low=0
- inline/anchored drawings：0（与原 target manuscript 一致）
- PDF：31 pages, openable, non-encrypted, non-scanned
- 31/31 pages 已逐页打开 1547×2002 PNG 做 100% 单页人工视觉复核（并辅以 contact sheet）；未见 clipping、overlap、missing glyph、异常分页、页眉页脚错位或参考文献断裂。

SHA-256：

- DOCX `2ABC2B66D12D50DF9ABB2571F85D083E2A6998CAC782EF87E3EEFEAEE7D7CB90`
- PDF `8AADBC11006765D0492FB829C8D42CFC593051C47A65C4ACD74DD4B75DDAD8B2`
- MD `07EBF141C59604DE42A3DE312F9115D89141331765718172C696D302F8C27115`

## 6. 本轮发现但未在此环境重渲染的 figure-code P0

GitHub 当前 `apply_npj_sba_style()` 先把 npj 文字设为 8 pt、线宽提升到 >=1 pt，随后同一函数又执行旧 generic clamp，把非 panel text 压回 5-7 pt、线宽重新 clip 到 0.25-1.0 pt。

这会使 exported artifact 与声明的 npj contract 不完全一致。正确修复方式是修改绘图源码后**从冻结 source tables 重渲染全部 15 张图**，而不是手工编辑 PDF。

同时 `npj_statistics_reporting_map.csv` 的 R1、C3_PRIMARY、C5_GENOMEWIDE、TF_DEPLETION 行存在 claim/decision 语义反向，需要由 builder 修复并增加回归测试。

## 7. 当前状态

建议当前状态：

`HOLD_NPJ_SBA_PREAPPROVAL_TECHNICAL_HARDENING_REQUIRED`

这不是科学 HOLD，而是 author exact-file approval 前的技术硬化。

## 8. 下一阶段

下一阶段正式目标：

`NPJ_SBA_FINAL_RENDER_AND_SEMANTIC_HARDENING`

P0 顺序：

1. 修 `publication_style_contract.py` npj branch；
2. 增加 exported-PDF font/line-width artifact-level test；
3. source-driven rerender Figure 1-5 + S1-S10；
4. 保证 15/15 source CSV byte-identical；
5. Figure 2 panel wording从 `No primary B_ASC enrichment` 改为 `Primary B_ASC enrichment not supported`；
6. Figure 1/4 source-label-defined wording与新 manuscript 对齐；
7. 修 statistics reporting map 四个反向 claim；
8. 更新 README/REPRODUCIBILITY 当前状态；
9. 重建最终 target documents/package；
10. 双渲染、deterministic hash、exact-file author approval；
11. 再完成 JCR Q1 / APC-OA institutional receipts 与 portal authorization。

在此之前不新增科学分析，也不应让作者对旧 target package hashes 做终局签字。

## 9. 额外文字结构 QA

- Introduction：462 words（不变）
- Results：2,077 words（原 2,075；仅 source-label-defined heading/ownership 精度变化）
- Discussion：996 words（原 1,081；减少 85 words，主要来自 caveat consolidation 和重复 Conclusion 删除）
- Methods：2,222 words（不变）
- Figure legends：671 words（原 667；增加 external evidence ownership qualifier）
- References：32 条，正文首次出现顺序 1 -> 32 单调连续；missing=0，out-of-order=0。

这符合 QiTeng late-stage `SALIENCE REDISTRIBUTION`：中心证据不删，Discussion 防御性重复压缩，方法复现信息不牺牲。
