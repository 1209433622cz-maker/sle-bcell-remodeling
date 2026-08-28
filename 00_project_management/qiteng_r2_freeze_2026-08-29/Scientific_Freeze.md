# QiTeng R2 科学正文冻结

确认日期：2026-08-29。状态：**作者已确认科学正文冻结；新 Zenodo 版本发布与旧版本删除已请求，尚未执行。**

## 冻结对象

用户本轮所称 QiTeng R2 对应上一轮交付的独立精修主文，内容提交为 `82661a2d187c4023e6d985d1944cbfacedff1051`，同步记录提交为 `db26afd2eff852d104f5dc9d7afdfba6a85e9e18`。这里的 QiTeng R2 是写作基线别名，不是 Round 6 R2 overlap-depletion 分析。

| 确认对象 | 路径 | SHA-256 |
| --- | --- | --- |
| DOCX | `../qiteng_text_audit_2026-08-29/review_candidate/Manuscript.docx` | `F6DB97C146A6DC41EED1910C0D0E5FCAA03C9A03EACF29EDA2CFB9F3803BBE0B` |
| WPS PDF | `../qiteng_text_audit_2026-08-29/review_candidate/Manuscript.pdf` | `DE6F9E1AAFD45995C99507FBC733AAF9FB8ACC1BD9AC6C1E2ED444AED60B7E73` |
| Markdown | `../qiteng_text_audit_2026-08-29/review_candidate/Manuscript.md` | `D383FF7605144531DF8E6CF1F3DC710561ABB2D88E3B957EAE0DD94ABD8F7A32` |

[用户确认原文](User_Confirmation.txt)单独保存。该记录是用户报告的作者确认，不伪装成独立采集的两份电子签名或机构伦理决定。

## 永久保留的负面结论

1. R1 正式决定保持 `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY`。B_ASC median Jaccard 为 0.930323，小于原 0.95 标准。全局指标很高和后续不确定性传播稳健，不改变此项失败。
2. C9R 正式决定保持 `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED`。主 elastic-net 校准不合格；辅助 centroid 合格不能替代它。`outcome_unlock_authorized=false` 保持，无纠正后的外部 disease effect。
3. “永不救 PASS”在本项目中具体表示：不放宽阈值、不替换主 mapper、不挑选 seed/replicate、不删失败记录、不以新命名掩盖失败、不把历史原决定改写为成功。技术完整性检查可以通过，但不得据此称科学 HOLD 已通过。
4. 原始输出、失败证据和对应 Git 历史继续保存。任何将来另行授权的新研究，也不能追溯覆盖本研究的原 HOLD。

## 作者与声明

Zhi Chen 为第一作者，Teng Qi 为通讯作者；姓名、单位、邮箱、ORCID 采用已提供并确认的信息。用户本次确认作者与声明部分及 Ethics，包括既有公开、去标识二次分析的伦理说明，以及已确认的无利益冲突、无特定资助、无致谢和 AI 使用披露。

上一轮文件中“exact refined files approval pending”是当时的历史状态，现由本记录的科学正文/声明确认取代。为保持已确认文件的指纹，本轮不回写该历史 DOCX/PDF。新归档稿可在 DOI 预留成功后一次性更新批准句、Data Availability 与归档引用，然后重新渲染并验证科学正文未变。

当前冻结的是科学内容，不代表目标期刊已选定或期刊投稿已获授权。JCR Q1 证明、APC 承诺、期刊最终格式与实际投稿仍独立处理。

## Zenodo 操作边界

用户已请求新版本发布，以及删除旧 Zenodo 记录 `22086892`，即 `10.5281/zenodo.22086892`。该请求不延伸为删除本地历史文件、Git 标签、GitHub releases、原始数据或其他 Zenodo 记录。

正确顺序：检查账户及已有草稿，创建/恢复同一版本链的新版本并预留 DOI，构建对应冻结内容，核对科学正文和哈希，发布并验证新版本，最后使用平台支持的删除流程处理指定旧版本。

按 Zenodo 当前官方说明，发布后 30 天内所有者可删除记录，删除后仍有包含引用的 tombstone 页面，不是抹除 DOI 或学术历史。[官方记录管理说明](https://help.zenodo.org/docs/deposit/manage-records/)。新版本具有自己的 DOI，并与既有版本相连。[官方版本管理说明](https://help.zenodo.org/docs/deposit/manage-versions/)。

如果平台不支持在保留新版本的同时删除指定旧版本，不删除整条版本链，也不虚构版权或隐私理由；届时报告平台的实际限制。浏览器的最终发布、个人信息传输和删除操作须在具体页面按要求完成操作时确认。

## 检查入口

[冻结清单](frozen_evidence_manifest.csv)绑定三份主文、十五份图源数据和三份 R1/C9R 决策/校准证据。只读检查器同时检查正文各节的规范化哈希、作者确认范围和两个 HOLD 的具体字段，而不是只看包含 `PASS` 的技术状态名。

```powershell
Set-Location 'H:\cuhk-2025fALL\6013RP-wyf'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' audit_tools/phase17_postc9_16_verify_scientific_freeze.py --output 00_project_management/qiteng_r2_freeze_2026-08-29/freeze_verification.json
```

冻结确认见 [author_freeze.json](author_freeze.json)。最终网络、DOI、删除和 Git 同步的实绩见本轮行动报告，不用计划状态替代已执行事实。
