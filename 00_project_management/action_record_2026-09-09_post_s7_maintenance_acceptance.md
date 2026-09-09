# S7 后独立复核归档与维护状态确认

日期：2026-09-09。结果：SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY。

## 本轮请求与工作范围

用户提交独立复核并明确同意关闭 Supplementary Table S7 可读性开放项。此次工作是验证当前对象与已审计版本一致、归档外部意见、明确现行文档位置及维护规则。没有重新开展整篇论文的科学审稿，也没有生成新手稿或图件。

## 输入归档

输入文件：action_record_2026-09-09_post_s7_manuscript_figure_maintenance_audit.md。

SHA-256：`24FBEAE5016A2E1C01E35E8B3000937EE177C5CFFFC172425CBED40CD8A86742`。

按原始字节复制到 `00_project_management/post_s7_independent_review_2026-09-09/received/`。该文件作为外部复核证据归档；其中的科学评价归属于外部复核，不自动视为本轮重新独立验证的发现。

## 本轮实际核验

1. GitHub main 指向 `b1a9d28963fc9d82d407f4e2d1d5a01630ffde46`，与用户提供的基线一致。
2. 当前 S7 DOCX 哈希与 audit.json 一致：`57DEDF3D91E13994537A1B775B8405A7D12CCA14F4A0975DE770066CA2BFC716`。
3. WPS PDF 哈希一致：`E6747F721617560576A44DAE02C9DB4ECE75939D6672237502A70A2F43A08A9D`。
4. LibreOffice PDF 哈希一致：`9C5ACF804B5CC44A6F332A0FA1D11C07B85C5FD3A4B507EB63052C836A1DA591`。
5. 读取冻结资产清单并逐个计算 SHA-256，45/45 科学 Figure/Source Data 文件一致。
6. S7 audit.json 状态为 PASS_S7_READABILITY_MICRO_GATE，失败项为空。
7. 工作区既有未跟踪的 05_Record/ 保持原状。

前轮已完成的双引擎 15 页、仅第 4-6 页变化、图题同页与指纹、accessibility 0/0/0、208/208 回归结果在本轮作为历史证据引用。因为未改代码、科学文本或成品，本轮不重复渲染和测试，不将历史结果称为新运行。

## 实际变更与裁决

新增外部复核原件归档、本行动记录及 `00_project_management/SCIENTIFIC_PRESENTATION_STATUS.md`。状态文件明确：主文和科学图件继续使用 20260908_final_cross_document 基线；补充材料采用 20260909_source_rebuild/documents 中的 S7 修复版，避免从多个历史目录中误选旧布局。

关闭唯一开放项 Supplementary Table S7 actual-size readability micro-gate。维持主图 21/21 KEEP，继续保留 Figure 1d、4d、5d 的身份、外部迁移和机制解释边界。本文的 composition null 不表述为 B_ASC 生物学等效，观察性 STAT1/STAT2 证据不升级为因果机制。

本轮未修改主文、补充正文、图件、统计数据、投稿 ZIP、Release 或 Zenodo。项目状态与复核记录通过常规 Git 提交同步，不创建新 Release。

## 下一阶段目标

进入 SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY。等待具体问题驱动的局部修订；数值、归属、来源、实际尺寸缺陷、新数据或可检验的作者科学反馈出现时，记录明确对象与验收条件，再执行来源修改、重建和针对性核验。当前没有待运行的分析或待替换的 panel。
