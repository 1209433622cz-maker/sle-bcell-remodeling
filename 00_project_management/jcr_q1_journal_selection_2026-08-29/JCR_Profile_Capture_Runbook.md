# JCR profile 与 APC 证据采集运行单

目的：补齐当前唯一阻断目标期刊冻结的外部证据。该运行单不要求提供学校密码、Cookie、验证码或个人登录信息。

## 需要获取的两个 profile

| Journal | eISSN | JCR release |
| --- | --- | --- |
| npj Systems Biology and Applications | `2056-7189` | 2026 release / 2025 data |
| Communications Biology | `2399-3642` | 2026 release / 2025 data |

通过学校图书馆 JCR 入口或直接登录 Clarivate JCR 后，对每个 journal：

1. 用 exact title 或 eISSN 搜索。
2. 确认页面年份为 2026 JCR release，指标数据年为 2025。
3. 展开并保存所有 JCR categories，不只保存最有利的一项。
4. 保存每一类别的 `rank / denominator / quartile`。
5. 导出完整 profile PDF；如果平台支持 CSV/XLSX，再同时导出原始表格。
6. 文件名建议为 `JCR2026_2056-7189_full_profile.pdf` 和 `JCR2026_2399-3642_full_profile.pdf`。
7. 不截图裁掉年份、类别名、rank denominator 或来源标识。

学校入口：

- https://cuhk-shenzhen.libguides.com/c.php?g=964056
- https://idp.cuhk.edu.cn/bridge/jcr

## 本地校验

将导出文件放入一个单独目录后，在 PowerShell 运行：

```powershell
Get-ChildItem -File | Select-Object Name, Length, LastWriteTime
Get-FileHash -Algorithm SHA256 -Path .\* | Format-Table Path, Hash -AutoSize
```

把原始 profile/export 文件交回项目，不要只提供手工抄写的 Q1 结论。项目将记录 exact file hash、全部类别和学校适用规则。

## APC/OA 需要图书馆确认的字段

沿用现有 `../jcr_q1_target_preparation_2026-08-29/Institutional_Request_Draft.md`，要求回复明确：

- 真实单位 `School of Medicine, The Chinese University of Hong Kong, Shenzhen` 是否适用；
- 通讯作者为 MSc student 是否影响资格；
- 两刊及 Article 类型是否被覆盖；
- 协议有效期和以 submission date 还是 acceptance date 判断；
- 覆盖比例、额度、名额、税费和投稿前审批要求；
- 若不覆盖，是否可申请 waiver、学校资助或作者自费。

未取得回复前，不能把香港校区协议推定给深圳校区，也不能把“无 funding”写成“APC 已获豁免”。本运行单不发送邮件、不申请付费证明、不承诺付款。
