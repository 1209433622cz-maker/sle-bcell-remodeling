# 2026-08-29 行动记录：QiTeng R2 Zenodo 公开发布与独立核验

## 1. 最终结论

Zenodo 新版本已公开发布并完成独立核验：

- 记录：`22151739`
- 版本 DOI：`10.5281/zenodo.22151739`
- 概念 DOI：`10.5281/zenodo.22086891`
- 版本：`1.1.0`
- 公开状态：`published`、`open`
- DOI 解析终点：`https://zenodo.org/records/22151739`
- 版本链：最新 `22151739`，历史 `22086892`

R1 与 C9R HOLD 未改变，没有解锁 corrected external outcome，没有重开分析、统计或图件。旧记录 `22086892` 尚未删除，GitHub release/tag 尚未创建，期刊投稿尚未执行。

## 2. 操作授权与边界

用户在动作时明确回复“确认上传并公开发布”，授权向草稿 `22151739` 传输三件校验文件及其中作者姓名、邮箱、ORCID、单位和项目材料，并保存元数据和公开发布。该确认明确排除旧记录删除、GitHub release/tag 和期刊投稿。

上传时 `SHA256SUMS.txt` 首次在 Zenodo 完成阶段遇到 `504`，显示 `Pending / N/A`。同时 Zenodo 表单前端意外生成 4 个完全为空的可选元数据行。按照浏览器安全边界再次取得“确认清理草稿并重传校验文件”后，仅删除四个空行和卡死的 171 字节草稿文件，再上传同一本地文件。两个已经完成的 ZIP、旧公开记录和本地文件均未触碰。

## 3. 公开元数据核验

发布前 Preview 与发布后公开 REST API 均核对：

| 字段 | 公开值 |
| --- | --- |
| 标题 | SLE B-cell remodeling analysis: code, source data and reproducible release |
| 资源类型 | Software |
| 日期 | 2026-08-29 |
| 作者 | Chen, Zhi；Qi, Teng |
| ORCID | `0009-0001-0072-5576`；`0009-0007-7648-4776` |
| 单位 | School of Medicine, The Chinese University of Hong Kong, Shenzhen |
| 语言 | English |
| GitHub | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| 许可 | CC BY 4.0；MIT |
| 关键词 | systemic lupus erythematosus；B cells；single-cell RNA sequencing；pseudobulk；interferon；reproducibility |

公开 API 证明服务器保存的是英文长描述；浏览器页面偶尔显示中文是浏览器翻译层，不是 Zenodo 元数据被改写。描述明确保留 R1 HOLD、C9R HOLD、无 corrected external disease effect，以及非因果、非临床效用和非同行评审文章边界。

## 4. 公开文件核验

| 文件 | 字节数 | Zenodo MD5 | 本地 SHA-256 |
| --- | ---: | --- | --- |
| Research_Archive.zip | 25,577,813 | `e684cd92599dcbd9fee39b42e7a93f8e` | `AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095` |
| Source_Code.zip | 78,040,863 | `972157ae86be2d1b450cbfc797cc8f44` | `51B1007908668F8EE25971E99270BF8477720A25ED7491BACD2F7572A4E24645` |
| SHA256SUMS.txt | 171 | `c47ddcf56c062ee1c7fa22e010e89290` | `BE96EEC9C0610208F867FE7258A3C7E672A63E8273C486CC09CAAE2BFCDB457B` |

公开 API 文件清单与本地三件文件一一对应；字节数与 MD5 一致。公开下载的 `SHA256SUMS.txt` 与本地 171 字节内容完全相同，其中两个 ZIP 的 SHA-256 与本地重新计算结果一致。

## 5. 可重复核验

新增只读脚本 `audit_tools/phase17_postc9_19_verify_zenodo_publication.py`。它不需要账户令牌，检查公开 API、英文元数据、作者/ORCID、关键科学边界、文件大小和 MD5、公开 checksum 文件、两种许可、版本链和 DOI 跳转。回执状态为 `PASS_PUBLIC_ZENODO_RELEASE_VERIFIED`，保存在 `qiteng_r2_release_2026-08-29/zenodo_publication_verification.json`。

公开归档内的 `author_freeze.json` 是上传前构建时点快照，因此其中 `new_zenodo_published=false` 是当时事实；发布后的真实状态由本报告、公开 API 和 GitHub 上的新验证回执续接，不改写已公开 ZIP 字节。

## 6. 旧记录检查与下一阶段

旧记录 `22086892` 页面明确提示存在较新版本，并在所属账户的“管理记录”菜单中显示可用的“删除记录”入口。仅做了只读检查，没有点击删除。根据当前风险排序，下一阶段应为：

1. 在独立动作时确认后，只删除旧记录 `22086892`，保留新记录、概念 DOI、本地历史证据和 Git 历史；随后验证 tombstone 和版本链行为。
2. 在独立动作时确认后，以源码提交 `f1859ff8498d5569a1d5027b36ed18c8b7c7536f` 创建 GitHub `v1.1.0` tag/release，并附加与 Zenodo 完全相同的三个文件和哈希。
3. 不再重开生信分析。待目标 JCR Q1 期刊确定后，只做 journal-specific 文本与格式适配；期刊投稿仍需独立授权。

因此本轮判断为：**科学与可重复性公开层已经闭环，剩余是旧版本治理和 GitHub release 镜像，不是分析缺口。**
