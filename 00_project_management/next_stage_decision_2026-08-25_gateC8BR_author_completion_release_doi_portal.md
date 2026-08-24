# 下一阶段决策：Gate C8BR 作者完成、永久归档与投稿门户预检

**日期：** 2026-08-25

**前序状态：** `PASS_GATE_C8BR_PORTABILITY_EDITORIAL_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

**科学冻结：** Gate C8S，保持不变

**投稿门户：** NOT AUTHORIZED

## 1. 唯一目标

完成作者和机构控制的现实事实，批准代码许可，创建与最终 release commit 对应的不可变 DOI，清除全部占位符，然后执行最后一次 WPS 全页和 portal preflight。不得为了继续推进而重开科学分析。

## 2. 作者立即完成项

在 `04_submission/author_completion_matrix_gateC8BR_2026-08-25.md` 中确认并提供：

1. 两人作者名单、顺序、通讯作者指定、投稿通讯地址及非作者贡献是否完整；
2. 机构对公开去标识人类数据二次分析的 ethics determination，及适用的 committee/reference number；
3. 两位作者的 financial/non-financial competing interests；
4. funding、grant number、recipient initials 和 funder role，或明确 no specific funding；
5. Zhi Chen 与 Teng Qi 的最终 CRediT roles；
6. acknowledgements，或确认 `Not applicable`；
7. 全体作者批准最终稿、投稿信和向 Genome Medicine 投稿；
8. 稿件未发表且未在其他期刊审理；
9. author/institution-approved code licence；
10. APC institutional agreement、经费或 waiver strategy。

任何一项都不能由代码、统计结果或 Codex 推断。

## 3. Release 与 DOI 顺序

1. 作者批准 licence 及其覆盖范围；
2. 回填 manuscript 和 cover letter 的 8 个可见占位符；
3. 生成 zero-placeholder release-candidate commit；
4. 创建 GitHub release；
5. 通过 Zenodo 或等效服务生成不可变 DOI；
6. 将 DOI 回填 manuscript、cover letter、README 和 portal；
7. 最后重建确定性投稿 ZIP，并再次核对 DOI 对应的 commit。

代码 licence 只覆盖仓库原创代码和适用文本，不重新许可 GEO/CELLxGENE 原始数据。

## 4. 最终通过标准

- manuscript `[[...]]` count = 0；
- cover letter `[[...]]` count = 0；
- 所有作者/机构声明有书面确认；
- licence 存在且范围准确；
- DOI 可解析并对应最终 release commit；
- full-statistics SHA-256 仍为 `AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`；
- main assertions `46/46 PASS`；
- supplementary assertions `29/29 PASS`；
- 三份 DOCX accessibility 为 `0/0/0`；
- WPS 41 页或最终实际页数逐页无裁切、重叠、缺字或残留占位符；
- package ZIP 两次重建字节一致；
- portal 的作者、单位、通讯、声明、文件和 DOI 与投稿文件逐项一致。

全部满足后才能记录：

`PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`

## 5. 停止条件

不再执行第四数据集、post hoc 基因/调控因子选择、阈值优化、临床预测、因果结合或 ligand-specific 扩写。只有冻结数字不可重现、样本映射出现事实错误、期刊提出必要的新分析，或核心数据/方法出现实质性错误时，才允许重开科学 gate。

## 6. 导师判断

当前瓶颈不是算力，也不是生物信息学方法，而是作者事实与永久发布治理。收到完整 author-completion matrix 后，下一轮应直接完成 licence/release/DOI、零占位符重建和 portal 对照检查。
