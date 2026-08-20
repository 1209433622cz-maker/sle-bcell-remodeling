# 下一阶段决策：完成 Gate C8B 作者事实与永久归档

**日期：** 2026-08-21

**前序状态：** `PASS_GATE_C8B_EDITORIAL_LITERATURE_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

**科学冻结：** Gate C8S，保持不变

**投稿门户：** NOT AUTHORIZED

## 1. 下一阶段唯一目标

将 8 个可见作者占位符替换为经作者、通讯作者和机构确认的事实，添加适用的代码许可与不可变归档 DOI，然后执行一次最终 WPS 和投稿门户预检。不得重新打开科学分析。

## 2. 需要作者立即提供的事实

请在 `04_submission/author_completion_form_gateC8B_2026-08-21.md` 中确认：

1. 机构对公开、去标识人类数据二次分析的 ethics determination，以及 committee name/reference number（如适用）；
2. Zhi Chen 与 Teng Qi 各自的 financial/non-financial competing interests；
3. funding、grant number、recipient initials 和 funder role，或确认 no specific funding；
4. 两位作者的 CRediT roles；
5. acknowledgements，或确认 `Not applicable`；
6. 两位作者均批准最终稿与投稿；
7. 稿件未发表、未在其他期刊审理；
8. 作者顺序、通讯作者与联系信息最终确认。

这些内容属于现实世界事实，不能由 Codex、分析脚本或统计结果代填。

## 3. 许可与 DOI 顺序

1. 作者选择并批准根目录代码 licence；
2. 清除稿件和 cover letter 的所有占位符；
3. 建立最终 release-candidate commit；
4. 创建 GitHub release；
5. 通过 Zenodo 或等效服务生成不可变 DOI；
6. 将 DOI 回填 manuscript data availability、cover letter、README 和 release metadata；
7. 再生成最终确定性投稿 ZIP。

代码 licence 只覆盖本仓库原创代码与文本，不重新许可 GEO/CELLxGENE 原始数据。

## 4. Gate C8B 最终通过标准

- manuscript `[[...]]` count = 0；
- cover letter `[[...]]` count = 0；
- ethics、interests、funding、CRediT、acknowledgements、approval 和 originality 均有作者确认；
- licence 存在且范围准确；
- DOI 可解析并对应最终 release commit；
- Gate C8S full-statistics SHA-256 保持 `AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5`；
- 46/46 main assertions 与 29/29 supplementary assertions 保持 PASS；
- 三份 DOCX 无障碍 high/medium/low 均为 0；
- 最终 WPS 全页无裁切、重叠或错误占位符；
- 最终 package ZIP 双重重建字节一致；
- portal author order、affiliation、correspondence、files 和 declarations 与稿件逐项一致。

## 5. 明确停止条件

不再执行第四数据集、post hoc gene/regulator selection、阈值优化、因果调控扩写或临床预测声明。只有出现以下情况才允许重开科学 gate：

- 冻结数字无法从源表重现；
- 作者发现样本/供者映射事实错误；
- 期刊明确要求当前包未包含的必要分析；
- 新证据证明核心方法或数据来源存在实质性错误。

## 6. 导师结论

下一步不是计算，而是作者事实闭环。收到完整 author completion form 后，应直接制作无占位符 release candidate、归档 DOI 和 portal preflight；不要再以“追求更高分区”为理由增加低收益的公开数据挖掘。
