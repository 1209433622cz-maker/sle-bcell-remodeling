# 下一阶段决策：Gate C8B 作者声明、许可与不可变归档

**日期：** 2026-08-21

**前序闸门：** Gate C8S PASS

**下一闸门：** Gate C8B

**科学结果状态：** FROZEN

**投稿门户状态：** NOT AUTHORIZED

## 1. 导师判断

Gate C8S 已关闭本轮独立复核提出的 reviewer-facing evidence 与 statistical traceability 缺口。继续加入新的公共数据集、继续变换图形或继续探索调控网络，当前预期收益低于引入分析自由度、叙事漂移和提交延迟的风险。

Genome Medicine 仍是与现有证据结构最匹配的首投目标。当前工作的优势是疾病盲身份重建、对不稳定亚型的负边界、样本/供者级推断、独立队列程序复现和可审计的调控敏感性；其上限仍由缺乏 matched patient perturbation、direct TF occupancy、prospective treatment-annotated validation 和 clinical utility evaluation 决定。仅靠再挖掘公开横断面数据，不足以可靠提升到更高风险 upper-Q1 的机制或转化证据门槛。

## 2. Gate C8B 唯一目标

完成作者、机构和发布控制的信息，并从冻结 C8S 重建一次无占位符的最终投稿包。不得在 Gate C8B 中修改冻结科学估计、重新选择模型或加入 post hoc 生物学结果。

## 3. 需要作者提供或确认的信息

### 3.1 Ethics

需要学校/导师确认该公开、去标识二次分析应使用以下哪一种准确表述：

- institutional review not required；
- exempt；
- waived；
- 或需要 committee name/reference number。

在得到机构确认前，不应由分析人员推断或代填。

### 3.2 Competing interests

由 Zhi Chen 与 Teng Qi 逐人确认 financial 和 non-financial interests；若无，确认可使用标准 no competing interests statement。

### 3.3 Funding

提供 funder、grant number、recipient initials 和 funder role；若无专项资助，确认 no specific funding。

### 3.4 CRediT 与作者批准

确定两位作者的 CRediT roles，并确认：

- 作者顺序；
- 通讯作者责任；
- 两位作者均阅读并批准最终手稿；
- 两位作者同意投稿；
- 稿件未发表且未在其他期刊审理。

### 3.5 Acknowledgements

列出需致谢人员并取得许可，或确认 `Not applicable`。

### 3.6 Repository licence

仓库当前已经公开，但根目录没有 licence。Gate C8B 需要作者选择代码许可。建议优先评估 MIT 或 BSD-3-Clause；公共数据本身继续受原始数据库和研究的许可/使用条款约束，不因代码 licence 被重新许可。

### 3.7 Immutable DOI

在 GitHub 最终 release commit 后建立 Zenodo 或等效不可变归档，并获得 DOI。DOI 必须同时进入：

- manuscript data availability；
- cover letter；
- repository README；
- package manifest/status；
- 最终 release metadata。

## 4. Gate C8B 执行顺序

1. 作者填写 `author_completion_form_gateC8S_2026-08-21.md`；
2. 锁定 ethics、interests、funding、CRediT、acknowledgements 和 approval 原文；
3. 添加经作者确认的根目录 licence；
4. 更新 Markdown 生成源，清除全部 8 个可见占位符；
5. 提交并推送最终 release candidate commit；
6. 创建 GitHub release 与 Zenodo/等效 DOI；
7. 回填 DOI 与 release commit；
8. 使用 frozen-output 快速重建：

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\audit_tools\run_6013RP_phase17_gateC8S_submission_package.ps1 `
  -SkipMainFigureBuild `
  -SkipSupplementaryFigureBuild `
  -SkipStatisticalArchiveBuild
```

9. 再次完成 WPS 40-page visual QA、accessibility audit、manifest 和 deterministic ZIP；
10. 在投稿门户逐项核对 article type、authors、affiliation、files、data availability、ethics、funding 和 conflicts。

## 5. Gate C8B 通过标准

Gate C8B 仅在以下条件全部满足时 PASS：

- manuscript 与 cover letter 中 `[[...]]` 占位符为 0；
- ethics 文本经机构/导师确认；
- interests、funding、CRediT、acknowledgements 与 author approval 完整；
- 根目录 licence 存在且适用范围清楚；
- immutable DOI 可解析并指向 frozen release；
- release commit 与 DOI 记录一致；
- 五主图、七补图及所有冻结数值哈希不变；
- 3 份 DOCX、3 份 WPS review PDF、40 个 page PNG 通过；
- accessibility high/medium/low 均为 0；
- final package ZIP 双重重建字节一致；
- 投稿门户文件映射与 package README 一致。

## 6. 明确禁止事项

Gate C8B 不执行：

- 新增第四个或更多公共队列；
- 因期望显著性而调整阈值、模型、对比或基因集；
- 把内部 donor-nonoverlap 对比称为独立队列；
- 对 GSE23307 的两个 donor 计算或暗示推断性显著性；
- 将 STAT1/STAT2 target activity 写成直接结合或因果激活；
- 将连续 IFN/ISG 程序改写成离散 IFN-high 亚型；
- 在没有 prospective evidence 时宣称预测治疗反应或临床效用。

## 7. 最终结论

下一阶段不是继续计算，而是完成“作者事实 + 合规声明 + 可引用归档 + 门户预检”。Gate C8S 的科学技术包已经达到首投 Genome Medicine 的可提交前状态；Gate C8B 完成后，应立即进入投稿，而不是再次打开探索性分析。
