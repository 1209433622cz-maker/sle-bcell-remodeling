# 6013RP-wyf Gate C8BRF 公开发布、DOI 激活与完整性复核行动报告

**日期：** 2026-08-25

**执行角色：** 生物信息学博士生导师级发布终审、科研软件发布工程与投稿前质量控制

**本轮最终决策：** `PASS_GATE_C8BRF_PUBLIC_RELEASE_INTEGRITY_AND_DOI_ACTIVATION`

**科学冻结来源：** Gate C8S

**科学估计是否改变：** 否

**GitHub 版本：** `v1.0.0`

**Zenodo DOI：** `10.5281/zenodo.22086892`

**下一阶段：** `GENOME_MEDICINE_PORTAL_ENTRY_AND_SUBMISSION_RECEIPT_FREEZE`

## 1. 本轮目标和授权边界

本轮承接 Gate C8BRF 作者完成、许可证治理、真实 DOI 回填、WPS 渲染和发布前冻结结果。在作者完成最终即时确认后，执行 GitHub 与 Zenodo 的公开发布，并对不可逆公开结果进行独立、机器可读和人工可见的交叉核查。

本轮只执行发布、验证和证据固化，不重跑科学分析，不改变主文、补充材料、图件、Source Data、统计结果或结论强度。`v1.0.0` 必须保持指向作者批准的冻结提交，发布后状态证据另行提交到 `main`，不得移动标签。

## 2. 发布前输入状态

- 项目仓库：<https://github.com/1209433622cz-maker/sle-bcell-remodeling>
- 冻结提交：`e23d863fc06ca6c065b7ea63cd201846d215bbc8`
- Annotated tag：`v1.0.0`
- Zenodo draft ID：`22086892`
- 预留 DOI：`10.5281/zenodo.22086892`
- Gate C8BRF 最终审计：`PASS_GATE_C8BR_RELEASE_PORTABILITY_AUTHOR_COMPLETION_AND_PORTAL_PREFLIGHT`
- 主图断言：46/46 PASS
- 补图断言：29/29 PASS
- WPS 人工逐页检查：43/43 页 PASS
- DOCX a11y：main、supplement、cover 均为 0/0/0

发布前工作树为干净状态，`main` 与远端同步；本轮公开动作未引入任何科学文件编辑。

## 3. GitHub 公开发布

### 3.1 推送与标签冻结

以下对象已成功推送到远端：

- `main` -> `e23d863fc06ca6c065b7ea63cd201846d215bbc8`
- annotated tag object -> `7e2786127bffc53dfc8b09c6e65f4527dba0ea73`
- `v1.0.0^{}` -> `e23d863fc06ca6c065b7ea63cd201846d215bbc8`

标签解析结果证明公开版本对应正确冻结提交，而不是发布后状态记录。

### 3.2 Release 状态

- Release URL：<https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.0.0>
- Tag：`v1.0.0`
- Draft：false
- Prerelease：false
- GitHub API `published_at`：`2026-08-24T21:08:02Z`
- 香港时间：`2026-08-25T05:08:02+08:00`
- Release 标题：`SLE B-cell remodeling analysis v1.0.0`
- Release 页面显示 DOI、许可证边界、科学解释边界和引用方式。

GitHub 页面显示 5 个 assets，其中 3 个为作者上传的冻结附件，另 2 个为 GitHub 根据标签自动生成的 source code ZIP 和 TAR.GZ。

## 4. Zenodo 公开发布与 DOI 激活

### 4.1 公开记录

- Record URL：<https://zenodo.org/records/22086892>
- DOI URL：<https://doi.org/10.5281/zenodo.22086892>
- Record status：`published`
- Resource type：Software
- Version：`1.0.0`
- Publication date：`2026-08-25`
- Access：Open
- Language：English
- Repository URL：<https://github.com/1209433622cz-maker/sle-bcell-remodeling>

Zenodo 页面公开显示 Zhi Chen 和 Teng Qi 的作者信息、ORCID、机构信息，并将 Teng Qi 标记为 Contact person。Rights 区同时显示 CC BY 4.0 与 MIT，版权声明为 `Copyright (c) 2026 Zhi Chen and Teng Qi`。

### 4.2 DOI 解析验证

直接访问 <https://doi.org/10.5281/zenodo.22086892> 后，浏览器成功跳转到 <https://zenodo.org/records/22086892>，页面标题、版本、作者、文件和 DOI 均与冻结元数据一致。

结论：DOI 已不再是仅预留状态，已注册、公开并可解析。

## 5. 跨平台文件完整性核查

| 文件 | Bytes | 本地/GitHub SHA-256 | 本地/Zenodo MD5 | 结果 |
|---|---:|---|---|---|
| `package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip` | 46,055,879 | `1FB1170B68E399EDBCF95400611FDF733BDCB3B64BA64640AF0958494CC7904A` | `21C301DCE8EA9A3C97CB2BED8DDD27EF` | PASS |
| `sle-bcell-remodeling-v1.0.0-source.zip` | 41,764,089 | `94FBE198A0EEAAA2D6A491EC1C10F5C4020D1D5A82985DAF19799ACDD73F6999` | `203A320A9EB6D3F1ECDBE82923156638` | PASS |
| `SHA256SUMS_v1.0.0.txt` | 235 | `EA45AE5A2EF565E05DFFC96AD952E56E14D192916D678F3AD46A5AF15C3372D5` | `CDC4376D9A1D7D3F2A8C2CD2B51C6DA0` | PASS |

核查逻辑：

1. 本地重新计算每个文件的 bytes、SHA-256 和 MD5。
2. GitHub Release API 返回的 3 个上传 assets 文件名、bytes 和 SHA-256 与本地逐项一致。
3. Zenodo API 返回的 3 个公开文件名、bytes 和 MD5 与本地逐项一致。
4. GitHub、Zenodo 和本地三方文件集合完全一致。
5. Zenodo 页面显示三个文件均可公开下载，总量约 87.8 MB。

结论：不存在断点上传、截断、错版本、错文件名或平台间资产漂移。

## 6. 公开内容真实性与范围复核

公开记录支持以下经过冻结的证据链：

- disease-blind conventional-B identity scope；
- sample-level composition analysis；
- within-compartment IFN/ISG transcription；
- independent external replication；
- prespecified regulator and perturbational evidence；
- 完整主图、补图、Source Data、gene-level statistics、环境和审计记录。

公开说明继续明确观察性边界：结果不证明离散新 B-cell 亚型、因果调控因子、唯一上游刺激或治疗获益。没有利用公开发布过程扩大结论，也没有修改任何数值结果。

## 7. 许可证和第三方材料边界

- 原创代码：MIT License。
- 原创稿件文本、复合图、项目文档和项目生成的派生 source tables：CC BY 4.0。
- GEO、CELLxGENE、第三方论文、数据库和软件材料不被重新许可，继续受其原始来源条款约束。

GitHub Release 与 Zenodo metadata 均显示双许可证；仓库中的 `LICENSE_SCOPE.md` 是具体适用范围的控制文件。

## 8. 隐私与作者元数据复核

作者已明确批准公开发布稿件、补充材料、图表、原始数据、投稿信及生成式人工智能使用声明。本轮发布包含已经确认的作者姓名、学术身份、机构、邮箱、ORCID 和通讯地址。

公开分析数据不含研究参与者姓名、邮箱或直接身份字段。Figure 2 的 UUID 为公开 CELLxGENE 来源中的分析单位标识，已经通过 `PASS_FIGURE2_PUBLIC_NON_IDENTIFYING_SOURCE_UUIDS` 治理，不是本地生成的患者直接标识。

## 9. 发布后机器可读证据

新增：

- `phase17_v7/gateC8BRF/20260825_author_release/09_PUBLIC_RELEASE_STATUS.json`
- `phase17_v7/gateC8BRF/20260825_author_release/09_PUBLIC_RELEASE_STATUS.md`

机器状态记录包含 release URL、record URL、DOI、标签对象、冻结提交、平台状态、文件哈希和逐项检查结果。该记录在 `v1.0.0` 之后提交是有意设计：标签保持冻结，`main` 仅新增发布后审计证据。

## 10. 本轮质量判定

逐项结果：

- GitHub Release public：PASS
- GitHub Release non-draft/non-prerelease：PASS
- `v1.0.0` resolves to frozen commit：PASS
- GitHub uploaded assets 3/3：PASS
- GitHub SHA-256 matches local 3/3：PASS
- Zenodo status published：PASS
- Zenodo files 3/3：PASS
- Zenodo MD5 matches local 3/3：PASS
- DOI resolution：PASS
- Creator ORCID and contact metadata：PASS
- Licence metadata：PASS
- Repository link：PASS
- Scientific estimates unchanged：PASS

最终机器与导师判定：

`PASS_GATE_C8BRF_PUBLIC_RELEASE_INTEGRITY_AND_DOI_ACTIVATION`

## 11. 下一阶段导师判断

当前不应重新开启探索性生信分析，也不应继续改动已发布的 `v1.0.0`。下一阶段唯一合理目标是：

`GENOME_MEDICINE_PORTAL_ENTRY_AND_SUBMISSION_RECEIPT_FREEZE`

建议执行顺序：

1. 使用 `portal_upload_required` 的 11 项文件进入 Genome Medicine 投稿系统。
2. Supplementary Information 已嵌入 S1-S7，7 个 standalone supplementary figures 仅在 portal 明确要求时上传，避免重复。
3. 逐字段录入作者、机构、通讯作者、ethics、consent、competing interests、funding、AI disclosure、data/code availability 和 DOI。
4. 上传后检查 portal 自动生成 PDF，重点核对作者顺序、邮箱、图件分辨率、Supplement 分页和 declarations。
5. 正式投稿前由通讯作者完成最后一次人类确认。
6. 投稿成功后冻结 manuscript number、receipt、提交时间、实际上传文件列表与 SHA-256，生成下一轮详细行动报告。

从科学、写作、图件、可重复性、许可证和公开归档状态看，本项目已完成投稿前技术闭环。后续优先级已经从“继续分析”转为“准确完成期刊门户录入并保全提交证据”。
