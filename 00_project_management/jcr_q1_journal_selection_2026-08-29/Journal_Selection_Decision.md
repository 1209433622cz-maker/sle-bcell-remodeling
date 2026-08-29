# JCR Q1 目标期刊条件决策

日期：2026-08-29。状态：**条件首选已形成，但尚未取得可归档的 JCR Q1 rank/quartile 证据，因此未正式冻结目标期刊。**

## 当前决策

1. 条件首选：**npj Systems Biology and Applications**，文章类型为 `Article`。
2. 第二顺位：**Communications Biology**，文章类型为 primary research Article。
3. 高风险 stretch：**Genome Medicine**；不因历史投稿包或期刊影响力惯性将其设为默认首投。
4. `selected_target` 继续为 `null`，直到取得 2026 JCR release（反映 2025 data）的机构或 Clarivate profile，记录全部类别、rank/denominator 与 quartile，并确认学校的多类别认定规则。

这是一项 fit-first 条件决策，不是“影响因子高所以 Q1”的替代论证。JIF、SJR、中科院分区和第三方排行榜均不能替代用户指定的 JCR JIF quartile。

## 为什么 npj SBA 是条件首选

官方 scope 明确包含 computational/mathematical analysis of complex biological systems、disease modeling、single-cell systems biology 和 systems immunology。本文的主要贡献不是再次发现 SLE IFN biology，而是证明：细粒度状态指派不稳定时，预设的 conventional-B IFN process inference 仍可在明确边界内复现。这一“identity uncertainty 与 process-level reproducibility 分离”的方法学主轴与 systems biology 的编辑框架最一致。

官方 2025 publisher metrics 为 JIF 4.4、median first editorial decision 8 days、median submission-to-acceptance 155 days。这些指标支持时效评估，但**不证明 JCR Q1**。

`Systems immunology: multi-omics approaches, dynamical modeling and novel agentic AI approaches` Collection 当前显示 open，deadline 为 2026-09-12。其征稿描述欢迎用真实数据研究 immunological states/disorders 及 phenotype/cell-state 关系的 computational work。本文主题高度贴合；是否选择 Collection 应在目标期刊正式冻结后写入 cover letter，不应为了赶 deadline 跳过 JCR/APC 与 exact-file author approval。

官方来源：

- https://www.nature.com/npjsba/aims
- https://www.nature.com/npjsba/journal-impact
- https://www.nature.com/npjsba/content-types
- https://www.nature.com/collections/heaibjjajc/how-to-submit

## Communications Biology 的定位

Communications Biology 官方 scope 接受 secondary data analysis 和 innovative computational methods，但要求 significant advance 和 new biological insight。当前证据的强项是审计严谨、负面边界透明和 process-level reproducibility；SLE IFN biology 本身并非新发现，因此该刊的 editorial novelty risk 高于 npj SBA。

官方 2025 publisher metrics 为 JIF 5.8、median first editorial decision 6 days、median submission-to-acceptance 217 days。其初投稿允许 flexible formatting，且明确要求 LLM 使用在 Methods 中披露；如果选择该刊，Methods 还需要集中形成 Statistics and reproducibility subsection。这些是 target adaptation，不是新增统计分析。

官方来源：

- https://www.nature.com/commsbio/aims
- https://www.nature.com/commsbio/journal-impact
- https://www.nature.com/commsbio/submit/submission-guidelines

## JCR 证据边界

Clarivate 已于 2026-06-17 发布 2026 JCR，反映 2025 data。公开 publisher metrics 和 SCIE indexing 只能证明期刊被收录及 JIF 数值，不能提供本项目要求的完整类别 rank/quartile。当前仍缺：

- npj Systems Biology and Applications（eISSN `2056-7189`）全部 JCR categories；
- Communications Biology（eISSN `2399-3642`）全部 JCR categories；
- 每个 category 的 JIF rank、denominator、quartile；
- CUHK-Shenzhen 对多类别期刊的实际 Q1 认定规则；
- 通讯作者单位、文章类型和接受日期对应的 OA/APC 协议资格。

Clarivate release source：https://clarivate.com/news/clarivate-releases-journal-citation-reports-2026/

## 目标冻结规则

1. 如果 npj SBA 按学校规则被正式认定为 JCR Q1，且 APC/OA 路径可行，则冻结 `npj Systems Biology and Applications / Article` 为首投目标，并优先考虑 Systems Immunology Collection。
2. 如果 npj SBA 不满足 Q1 或成本路径不可行，而 Communications Biology 满足 Q1 且可行，则冻结 Communications Biology。
3. 如果两者均不满足，或存在无法解释的多类别冲突，则不提交、不把 SJR/Q1 代替 JCR Q1，扩展一个新的 fit-first 候选矩阵。
4. Genome Medicine 只作为明确接受较高 desk risk 的 stretch，不以增加新 cohort、mapper、TF sweep 或救 HOLD 来“配期刊”。

## npj SBA 一次性格式适配范围

当前发布稿标题按空格计 16 words，摘要按 Markdown 空白分词计 334 words。npj Article 要求 title 不超过 15 words、unstructured abstract 不超过 150 words。现有内部候选 title 为 13 words、abstract 为 117 words，尚未写入冻结稿。

正式选刊后只允许一次受控适配：

- 以已准备的 13-word title 和 117-word abstract 为起点，逐 claim 核对后替换；
- `Background` 改为 `Introduction`；
- Discussion 去除子标题，把 limitation substance 保留在连续 Discussion 中；
- 独立 Conclusions section 的内容并入 Discussion，不删除结论边界；
- Methods 留在主文并保留 AI disclosure；
- 保留 mandatory Data availability、Code availability、Author contributions 和 Competing interests；
- 按该刊规则将 funding 表述放入 Acknowledgments；若无 funding，使用准确的无资助表述；
- reader-facing Data Availability 只引用 `10.5281/zenodo.22151739`，旧 tombstone 关系保留在 provenance/release records；
- 初投稿可使用当前清晰的 170 mm 矢量图；只有 journal-specific exact width/font/line requirement 确认需要时，才从代码重渲染，禁止手工编辑 PDF；
- Collection 选择与 cover-letter 表述仅在 target freeze 后加入。

不得改动 R1/C9R HOLD、统计值、source data、gene/program/TF 选择、external outcome lock 或科学结论。

## 下一动作

执行 [JCR_Profile_Capture_Runbook.md](JCR_Profile_Capture_Runbook.md)，取得两刊官方 profile/export 与 APC 回复。完成后才能把 `selected_target` 从 `null` 改为具体期刊，并进入 target-specific DOCX/PDF build、WPS QA、exact-file author approval 和 portal preflight。当前仍无投稿或 APC 支付授权。
