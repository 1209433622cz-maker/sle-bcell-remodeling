# 2026-08-29 行动记录：旧 Zenodo tombstone 与 GitHub v1.1.0 release

## 1. 本轮结论

经用户动作时明确确认后，旧 Zenodo 记录 `22086892` 已删除并保留公开 tombstone；新记录、概念 DOI、本地备份与 Git 历史均未删除。GitHub `v1.1.0` 带注释标签和公开 release 已建立，三个 release 资产与已验证 Zenodo 上传文件逐字节对应。

本轮只完成发布治理、公开状态核验和审计凭据更新。没有重跑生信分析，没有修改图表、统计量或科学正文；R1 与 C9R HOLD 均保持，corrected external outcome unlock 仍为 `false`，未进行期刊投稿或 APC 承诺。

## 2. 授权范围

用户原文确认“删除旧记录并创建 GitHub v1.1.0 release”。执行范围严格限定为：

- 删除 Zenodo 旧记录 `22086892`，不删除新记录 `22151739`、概念 DOI、本地备份、Git 历史或其他记录；
- 创建 GitHub `v1.1.0`，精确指向冻结内容提交 `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`；
- 仅上传 `Research_Archive.zip`、`Source_Code.zip` 和 `SHA256SUMS.txt`；
- 公开 release 保留 R1/C9R 失败边界、非因果边界、许可范围及替代 DOI；
- 不删除旧 GitHub `v1.0.0` release/tag，不授权期刊投稿。

## 3. 旧 Zenodo 记录处理与核验

Zenodo 删除确认页提示原 DOI 不可复用、三件旧文件被移除并转为 tombstone。两项确认框均核对后，删除理由选择 `Retraction/Withdrawal of a record`，随后只删除记录 `22086892`。

删除后的独立只读核验结果：

| 检查项 | 结果 |
| --- | --- |
| 旧记录 API | HTTP `410`，`message=Record deleted` |
| tombstone 可见性 | `is_visible=true` |
| 删除原因 | `retracted` |
| 删除策略 | `grace-period-v1` |
| 删除时间 | `2026-08-29T05:20:04.133175+00:00` |
| 旧 DOI | `10.5281/zenodo.22086892` 解析至旧记录 tombstone，HTTP `410` |
| 新 DOI | `10.5281/zenodo.22151739` 继续解析至公开新记录，HTTP `200` |
| 概念 DOI | `10.5281/zenodo.22086891` 解析至新记录 `22151739` |
| live versions API | 仅返回 `[22151739]`；旧版本由 tombstone 单独保留 |

删除没有抹除 DOI 或引用历史。旧 tombstone 页面仍保留原引用和删除日期；新记录的公开元数据、许可和三个文件均未改变。

## 4. Git 标签与 release

先创建并推送带注释标签 `v1.1.0`。标签对象为 `6e492e3dcd5e6ee89b386e6c459622dffe0d9269`，剥离后的提交精确为 `f1859ff8498d5569a1d5027b36ed18c8b7c7536f`。最初用 PowerShell 执行带 `^{commit}` 的 `git cat-file` 形式时出现一次 shell 解析提示；该提示不影响标签创建或推送，随后分别通过本地 `git rev-list`、远端 ref 和 GitHub tag API 再次验证了精确目标。

GitHub 浏览器草稿表单已填入标题和科学边界，但浏览器扩展两次在接管现有页面时超时。第一次文件选择器尝试没有选中文件、没有传输数据，也没有生成 release。为避免重复页面操作，在确认公共 API 尚无 `v1.1.0` release 后，改用 GitHub 官方 REST API 和本机既有 Git 凭据完成发布；凭据只在进程内用于认证，未记录、显示或写入项目文件。

发布采用先建 draft、逐件上传并核验、最后转为公开 release 的顺序。公开结果如下：

- release ID：`378885936`
- 标题：`SLE B-cell remodeling reproducibility release`
- 状态：`draft=false`、`prerelease=false`、latest release
- URL：`https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.1.0`
- 科学边界：QiTeng R2 冻结；R1 HOLD；C9R HOLD；无 corrected external disease effect；调控证据不构成因果、唯一上游配体或临床效用证明

## 5. 公开资产一致性

GitHub API 返回的 `digest` 与本地重新计算的 SHA-256 完全一致：

| 文件 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Research_Archive.zip | 25,577,813 | `AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095` |
| Source_Code.zip | 78,040,863 | `51B1007908668F8EE25971E99270BF8477720A25ED7491BACD2F7572A4E24645` |
| SHA256SUMS.txt | 171 | `BE96EEC9C0610208F867FE7258A3C7E672A63E8273C486CC09CAAE2BFCDB457B` |

这三项值同时与 Zenodo 公共文件清单、本地上传目录和 `SHA256SUMS.txt` 一致。GitHub release 因而是 Zenodo `1.1.0` 的可验证镜像，不是另一个内容版本。

## 6. 新增审计入口

- `audit_tools/phase17_postc9_19_verify_zenodo_publication.py`：现同时验证新记录、概念 DOI、旧记录 `410` tombstone、删除原因、live version 列表与旧 DOI 解析。
- `audit_tools/phase17_postc9_20_verify_github_release.py`：验证 release 状态、标题和边界、latest 标记、带注释标签目标以及三件资产的字节数和 SHA-256。
- `qiteng_r2_release_2026-08-29/zenodo_publication_verification.json`：状态 `PASS_PUBLIC_ZENODO_RELEASE_VERIFIED`。
- `qiteng_r2_release_2026-08-29/github_release_verification.json`：状态 `PASS_PUBLIC_GITHUB_RELEASE_VERIFIED`。

冻结完整性检查和 59 项回归测试在本轮改动后重新运行。它们只证明冻结材料、HOLD 边界和发布治理没有被改写，不将技术检查结果解释为 R1 或 C9R 的科学 PASS。

## 7. 下一阶段判断

发布治理现已闭环，项目不再有需要通过新增数据、重跑分析或改图来补救的发布缺口。下一阶段应转为 `JCR_Q1_JOURNAL_SELECTION_AND_FORMAT_ADAPTATION`：建立当前年份的候选期刊矩阵，核验 JCR Q1 证据、范围匹配、文章类型、字数/图数/数据政策和 APC，再对冻结主文进行窄范围的 journal-specific 标题、摘要与格式适配，并由两位作者批准 exact final files。

期刊选择、格式适配与最终投稿是三个不同动作。当前没有实际投稿授权，因此不得上传期刊系统、承诺 APC 或把 release 完成误写成期刊接受/同行评审完成。
