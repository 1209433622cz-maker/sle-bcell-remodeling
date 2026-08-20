# Gate C8B 下一阶段决策：作者声明、机构伦理与永久归档

**日期：** 2026-08-20
**进入条件：** `PASS_GATE_C8_SCIENTIFIC_TECHNICAL_SUBMISSION_PACKAGE_AUTHOR_DECLARATIONS_AND_ARCHIVE_REQUIRED`
**决策：** `GO_GATE_C8B_AUTHOR_DECLARATIONS_ARCHIVE_AND_PORTAL_PREFLIGHT`

## 目标

在不改变 Gate C7 科学冻结和 Gate C8 图文结构的前提下，清除所有作者控制占位符，建立可引用的永久代码归档，并完成 Genome Medicine 投稿门户预检。

## 工作顺序

1. 由两位作者和项目导师/机构确认最终作者名单是否完整、通讯作者安排是否有意且合适。
2. 填写 CRediT 分工，并获取所有作者对最终主文、图件、补充材料和投稿行为的书面批准。
3. 获取公开去标识人类数据二次分析的机构伦理判断；若为不需审查、豁免或 waived，使用机构批准的准确表述。
4. 完成 competing interests、funding、acknowledgements、originality 和非一稿多投声明。
5. 为 GitHub 仓库选择并加入开源许可证；建立 Zenodo 或等价不可变归档，取得版本 DOI。
6. 将最终 commit、release/tag、archive DOI 写入 Data and materials、投稿信和补充材料。
7. 从生成源重建无占位符 DOCX，再用 WPS 后台渲染全部页面并逐页检查。
8. 重跑 Gate C8 审计，要求 `portal_submission_authorized: true`，生成新的 SHA-256 清单和最终上传 ZIP。
9. 在 Genome Medicine 门户核对 article type、作者顺序、单位、ORCID、摘要、关键词、文件角色、图序、补充文件和 reviewer suggestions。

## 必须由用户/团队提供

- 最终作者名单与署名顺序确认。
- 通讯作者指定确认。
- ZC/TQ 的 CRediT 角色。
- 伦理/IRB/REC 正式判断及适用编号。
- 基金和利益冲突文本。
- 致谢文本。
- 所有作者批准、原创性和未一稿多投确认。
- 许可证选择；默认建议代码采用 MIT 或 BSD-3-Clause，但必须由权利人确认。
- 是否允许建立公开 Zenodo release 和 DOI。

## Gate C8B 通过标准

- 主文与投稿信中 `[[...]]` 占位符为 0。
- 作者名单完整性和通讯作者安排已记录。
- 全部 Declarations 为已批准的真实陈述。
- GitHub release/tag 与不可变 DOI 可访问，许可证明确。
- WPS 渲染后的主文、补充材料和投稿信全部页面通过视觉质控。
- 所有 DOI、图文件、源数据和 SHA-256 清单再次通过。
- 机器状态变为 `scientific_technical_package_pass: true` 且 `portal_submission_authorized: true`。

## 科学工作判断

Gate C8B 不应启动新的探索性分析。现有证据链已经达到可提交 Genome Medicine 的强度；此时新增公开数据集更可能稀释主线、增加异质性和产生选择性分析风险。

只有在以下情形才重启计算：

- 编辑或审稿人提出明确、可回答且会改变判定的分析问题。
- 数据或代码审计发现当前数字无法从冻结源重现。
- 新实验或直接功能证据已经获得，需要按预先冻结合同纳入。

## 投稿与转投路线

- 首投：Genome Medicine。
- 第一转投：Communications Biology，保持五图和核心结论，按其格式重排。
- 疾病专科转投：Journal of Autoimmunity。
- Nature Communications：只有新增患者匹配功能证据、直接 TF 结合或前瞻性临床验证后再评估。
