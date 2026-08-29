# 2026-08-29 行动记录：QiTeng R2 Zenodo 新版本执行与发布候选终检

> 后续发布更新：新版本 `22151739` 已公开发布并通过 API、DOI 和文件哈希验证。本文保留上传前终检过程；最终发布事实见 `action_record_2026-08-29_qiteng_r2_zenodo_publication_and_verification.md`。

## 1. 本轮结论

本轮完成了关联 Zenodo 新版本草稿创建、DOI 预留、行政 DOI 版主文重建、DOCX/PDF 双引擎渲染质控、科学冻结复核、确定性发布包构建与 Git 内容快照固定。Zenodo 草稿为 `22151739`，预留 DOI 为 `10.5281/zenodo.22151739`。该 DOI **尚未因公开发布而注册**；三个本地上传文件尚未传输，旧记录 `22086892` 尚未删除。

科学结论没有重开。QiTeng R2 的 9 个科学章节保持冻结，R1 仍为 `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`，C9R 仍为 `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`，`corrected_external_outcome_unlock_authorized=false`。本轮没有新增分析、重算统计量、重画图、修改补充材料或推进期刊投稿。

## 2. Zenodo 账户操作

在用户确认只创建关联草稿和预留 DOI、不公开发布、不删除旧记录后，通过已登录的 Zenodo 所属账户从公开记录 `22086892` 的“新版本”入口创建了同一版本链草稿。页面显示：

| 项目 | 实际状态 |
| --- | --- |
| 新草稿 URL | `https://zenodo.org/uploads/22151739` |
| 新记录 ID | `22151739` |
| 预留 DOI | `10.5281/zenodo.22151739` |
| 继承作者 | Zhi Chen；Teng Qi |
| 继承 ORCID / 单位 / 许可 | 页面已显示继承 |
| 上传 | 未执行 |
| 元数据保存 | 未执行本轮最终修改 |
| 公开发布 | 未执行 |
| 旧记录删除 | 未执行 |

草稿当前为零文件状态。没有读取密码、令牌或浏览器凭据，也没有把本地作者邮箱、ORCID、单位或项目文件传给平台。最终上传、元数据保存、公开发布和删除均保留动作时确认。

## 3. 行政版主文

构建器 `audit_tools/phase17_postc9_17_build_zenodo_manuscript.py` 只允许三项行政变化：

1. Data Availability 写入预留 DOI，并保留初始 DOI 的被替代关系和许可边界。
2. Authors' contributions 将历史 pending 句替换为用户报告的批准范围，并声明 DOI 整合不改科学正文。
3. 参考文献 32 改为预留 DOI。

第一次试运行因 DOCX 自动编号不包含可见的 `32.` 而安全失败，没有生成错误交付件。随后将 Markdown 显式编号与 Word 自动编号分别匹配，成功重建；实际改变 DOCX 段落仅为 `109`、`115`、`168`。最终文件：

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Manuscript.docx | 37,793 | `3D8155E204241BA7C33F4CDE820F5D1B858EDB9713A5740453A97DC0410BF8C6` |
| Manuscript.pdf（WPS） | 252,321 | `117B694FD63C3FFEE421DFCD5A94F057F460689612E7D4AAE67E4F821CB1755C` |
| Manuscript.md | 63,673 | `ECA52AA68520B1D21F86E8320ED5D4B151820588385EEDC38A4699E6AA266586` |

## 4. 文档和科学质控

- LibreOffice 渲染 18 页，18/18 页逐页检查通过。
- WPS 后台渲染 18 页，18/18 页逐页检查通过，并固定为最终 PDF。
- 未见裁切、重叠、缺字、错误分页、参考文献溢出或 Data Availability 末尾多余 `X`。
- PDF 文本审计：新 DOI 2 次、历史 DOI 1 次、pending 句 0 次、尾随 `X` 伪影 0 次。
- DOCX accessibility：0 high、0 medium、5 low；5 项均为 ORCID/GEO 原始 URL 显示，不是结构或可读性错误。
- 科学冻结检查：21 个证据文件、9 个科学章节全部通过；状态为 `PASS_FREEZE_INTEGRITY_NOT_SCIENTIFIC_GATE_PASS`，不把技术完整性 PASS 冒充科学 gate PASS。
- 回归测试：59/59 通过。

## 5. 干净发布包

构建器 `audit_tools/phase17_postc9_18_build_zenodo_archives.py` 从内容提交 `f1859ff8498d5569a1d5027b36ed18c8b7c7536f` 生成精确源码快照，并从已验证的 corrected candidate 中只抽取未改动补充材料、5 个主图、10 个补图和三个派生结果附件。研究归档同时加入许可、数据获取说明、R1/C9R 原决定、C9R 校准、科学冻结和文档质控记录。

| 上传文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Research_Archive.zip | 25,577,813 | `AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095` |
| Source_Code.zip | 78,040,863 | `51B1007908668F8EE25971E99270BF8477720A25ED7491BACD2F7572A4E24645` |
| SHA256SUMS.txt | 171 | `BE96EEC9C0610208F867FE7258A3C7E672A63E8273C486CC09CAAE2BFCDB457B` |

Research Archive 含 59 个文件、58 行内容清单、55 行来源追踪。ZIP CRC、内部字节数与 SHA-256、科学正文哈希、R1/C9R 字段均通过。连续两次重建的三个文件 SHA-256 完全一致。

明确排除：旧投稿信、期刊门户文件、旧主文、历史 prior snapshot、原始/可重算大矩阵、单细胞缓存、凭据、日志和第三方 QiTeng 写作工具包。文件名采用稳定的投稿中性名称，不在公开文件名中暴露内部轮次号。

## 6. Git 与可追溯性

内容提交 `f1859ff8498d5569a1d5027b36ed18c8b7c7536f` 固定了 DOI 状态、两套构建器、行政版构建回执、科学冻结回执、可访问性与 PDF 审计。`Source_Code.zip` 正好对应此提交；本报告和归档构建回执作为后续账本提交，不纳入源码 ZIP，避免自引用哈希。

本地大 ZIP 位于 `04_submission/zenodo_release/upload/`，受 `.gitignore` 管理，不推入 Git 仓库。GitHub 只保存代码、轻量审计记录和状态账本。

## 7. 风险判断与下一阶段目标

当前已从“科学文本冻结”进入 `ZENODO_UPLOAD_METADATA_PUBLICATION` 门。下一阶段不是继续生信分析，而是在动作时确认后：

1. 向 Zenodo 草稿 `22151739` 上传上述三个精确文件；该传输包含主文中的作者姓名、邮箱、ORCID、单位及项目材料。
2. 将版本、描述、作者、许可、GitHub 提交和被替代 DOI 与本地元数据计划逐项核对并保存。
3. 在单独明确确认后公开发布，随后从公开页面/API 反查 DOI、文件大小和 SHA-256。
4. 只有新版本完全验证后，再单独确认并仅处理旧记录 `22086892`；若 Zenodo 不支持只删除旧版本，则保留旧版本链，不扩大删除范围。
5. GitHub `v1.1.0` tag/release 属于另一项公开发布动作，应与 Zenodo 实际 DOI 和资产哈希对齐后再执行；不与期刊投稿授权混同。

因此本轮最终判断为：**本地发布候选已达到上传前冻结标准；公开性动作尚未发生。**
