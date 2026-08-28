# 2026-08-29 行动记录：QiTeng R2 科学冻结批准与 Zenodo 替换准备

## 1. 结果与未完成事项

**已完成：**将用户对 QiTeng R2、R1 永不救 PASS、C9R HOLD、作者声明及 Ethics 的确认绑定到确切文件；新增冻结核验与测试；读取 Zenodo 原记录和已发布版本；为计划中的旧版本删除完整备份三份原始公开附件；准备新版本元数据和发布顺序；整理 GitHub 入口。

**未完成：**没有创建/恢复 Zenodo 新版本草稿，没有预留新 DOI，没有构建或上传新版本归档，没有发布新版本，没有删除旧版本。早先浏览器域名解析失败；用户随后明确回复“ZENODO已经登录”，现已实际验证 Edge 中的所属账户上传列表及旧记录管理菜单。当前只等待创建关联草稿及预留 DOI 的操作时确认，不再是网络或登录障碍。

目前状态为 `SCIENTIFIC_FREEZE_CONFIRMED_AWAITING_DRAFT_CREATION_CONFIRMATION`。这不是科学结果未获批准，也不是要求用户再做一次大规模计算。没有用技术 PASS 冒充发表、DOI 激活或删除成功。

## 2. 用户确认与确切基线

起点 Git 为 `db26afd2eff852d104f5dc9d7afdfba6a85e9e18`，工作区起始干净。用户确认原文保存在 [User_Confirmation.txt](qiteng_r2_freeze_2026-08-29/User_Confirmation.txt)，其 SHA-256 为 `637C84292A3D1FB1F75C7E9FE9A91E4D68D3C7E5F9236667EBED25F9734FAA4C`。

本轮将 QiTeng R2 明确解释为上一轮已交付的精修主文，**不是** Round 6 R2 overlap-depletion 分析。三份文件对应内容提交 `82661a2d187c4023e6d985d1944cbfacedff1051`。

| 基线 | 字节数 | SHA-256 |
| --- | ---: | --- |
| Manuscript.docx | 37,842 | `F6DB97C146A6DC41EED1910C0D0E5FCAA03C9A03EACF29EDA2CFB9F3803BBE0B` |
| Manuscript.pdf | 253,145 | `DE6F9E1AAFD45995C99507FBC733AAF9FB8ACC1BD9AC6C1E2ED444AED60B7E73` |
| Manuscript.md | 63,712 | `D383FF7605144531DF8E6CF1F3DC710561ABB2D88E3B957EAE0DD94ABD8F7A32` |

正式范围见 [Scientific_Freeze.md](qiteng_r2_freeze_2026-08-29/Scientific_Freeze.md) 和 [author_freeze.json](qiteng_r2_freeze_2026-08-29/author_freeze.json)。作者身份与声明采用已经提供并确认的 Zhi Chen / Teng Qi 信息；不伪称独立收集到了两份电子签名，也不把作者 Ethics 确认写成新取得的机构伦理批件。

用户对新 Zenodo 版本及指定旧记录删除的意图已记录，不再标作“没有发布请求”。但请求与实际执行分开；浏览器对最终公开、个人信息传输及删除动作所需的操作时确认也不提前伪造。

## 3. 永久保留 R1 与 C9R HOLD

| 对象 | 原始决定 | 本轮约束 |
| --- | --- | --- |
| R1 | `HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY` | B_ASC median Jaccard 0.930323 < 0.95，不因全局高一致性或 propagation 稳健而改判 |
| C9R | `HOLD_C9A_PREFREEZE_REVIEW_REQUIRED` | 主 elastic-net 不合格；辅助 centroid 合格不能替代；outcome 不解锁 |

“永不救 PASS”固定为：不放宽阈值、不换主 mapper、不挑 seed 或 replicate、不删除失败记录、不以换名称或选择性重跑掩盖失败，也不追溯覆盖原 HOLD。将来另行授权的新研究不能改写这两个历史决定。

R1 记录中的 `PASS_R1_HOLD_INDEPENDENT_AUDIT_AND_PROPAGATION_PREP` 是技术审计状态；实际科学决定在 `r1_decision` 字段。本轮检查器专门读取该字段，避免把字符串含有 PASS 当作科学通过。

冻结对象包括三份主文、十五份图源数据、R1 决策、C9R 决策和 calibration CSV，共 **21 份文件**。清单 SHA-256 为 `917B91BFFD3A87CCD562EFB8F4372B30DF9E465B67A38E8C9C3B5F57353B0880`。另记录 Title、Abstract、Background、Methods、Results、Discussion、Conclusions、abbreviations、figure legends 共 **9 部分**的规范化文本哈希。

未来仅更新批准句或实际新 DOI 时，可使用 `--candidate-markdown` 检查科学部分未变。该检查不是对未来元数据语义或整个投稿包的自动批准，仍需完整构建核验。

## 4. 本轮文件与数值完整性

新核验器结果见 [freeze_verification.json](qiteng_r2_freeze_2026-08-29/freeze_verification.json)：21/21 文件通过、9/9 科学部分通过、两项 HOLD 保留、纠正后外部 outcome 解锁仍为 false。

另重新执行历史候选检查，[historical_candidate_integrity.json](qiteng_r2_freeze_2026-08-29/historical_candidate_integrity.json)确认：

- `corrected_candidate.zip` 大小为 26,632,739 bytes，SHA-256 仍为 `D87F83BEBE281E748E54DF0736E34B38E1CB0FF83C746C934B43E730373BA150`。
- 82/82 payload、75/75 source provenance 与 15/184/10 行嵌套清单均通过。
- 没有重跑分析、重画图或改动统计结果，没有回写历史批准/失败记录。

上一轮精修 DOCX/PDF 原字节保留。其“批准待定”句是当时状态，现由本轮确认记录取代；待真正取得新 DOI，再在新归档稿中一次性更新批准句与 Data Availability/归档引用，并重新渲染。这避免先改一个虚构 DOI，再不断改变已确认文件的指纹。

`01_manuscript/Manuscript.md` 和历史包仍保留前一候选，README 已明确区分它们与新确认的 QiTeng R2。冻结基线通过精确路径和哈希生效，不以静默覆盖旧包实现。后续 DOI 行政整合后再更新面向当前归档的入口。

## 5. Zenodo 公开记录核查

原始 API 返回已保存为 [zenodo_existing_record.json](qiteng_r2_freeze_2026-08-29/zenodo_existing_record.json) 和 [zenodo_published_versions.json](qiteng_r2_freeze_2026-08-29/zenodo_published_versions.json)。

| 项目 | 实际观察 |
| --- | --- |
| 旧 record ID | 22086892 |
| 旧版本 DOI | 10.5281/zenodo.22086892 |
| Concept DOI | 10.5281/zenodo.22086891 |
| 版本 | 1.0.0 |
| Publication date | 2026-08-25 |
| 当前公开版本数 | 1；ID 为 22086892 |
| 原始公开文件数 | 3 |
| 未公开新版本草稿 | 所属账户上传列表未见本项目草稿；旧记录提供 New version 入口 |

官方说明允许所有者在发布后 30 天内删除记录，之后仍保留带引用的 tombstone；超过窗口须符合平台理由和支持流程。本记录目前的公开日期位于该窗口内，但本轮没有看到所属账户的实际删除控件，不能声称已经确认 UI 可删除。[Zenodo 记录管理](https://help.zenodo.org/docs/deposit/manage-records/)。

新版本是同一版本链中的独立记录，拥有自己的文件和持久标识；因此应先使用 New version，而不是另建一个无关联的同名项目。[Zenodo 版本管理](https://help.zenodo.org/docs/deposit/manage-versions/)。预留 DOI 也不等于已注册，只有发布完成才成为公开记录。[Zenodo 上传与 DOI 说明](https://help.zenodo.org/docs/deposit/create-new-upload/)。

本轮不会虚构版权/隐私理由，也不会删除整条版本链。如果实际删除控件无法仅处理指定旧版本，须报告并保留新版本，不能以“删除旧的”推断可以删除所有记录。

## 6. 删除前历史备份

旧版三份公开附件已保存到本地 `04_submission/zenodo_history/22086892/`，该目录遵守原有 Git 忽略策略，不再次上传约 87.8 MB 的历史二进制。回执见 [old_record_backup_receipt.json](qiteng_r2_freeze_2026-08-29/old_record_backup_receipt.json)。

| 文件 | 字节数 | SHA-256 | Zenodo MD5 |
| --- | ---: | --- | --- |
| SHA256SUMS_v1.0.0.txt | 235 | `EA45AE5A2EF565E05DFFC96AD952E56E14D192916D678F3AD46A5AF15C3372D5` | `cdc4376d9a1d7d3f2a8c2cd2b51c6da0` |
| package_genome_medicine_gateC8BRF_author_release_2026-08-25.zip | 46,055,879 | `1FB1170B68E399EDBCF95400611FDF733BDCB3B64BA64640AF0958494CC7904A` | `21c301dce8ea9a3c97cb2bed8ddd27ef` |
| sle-bcell-remodeling-v1.0.0-source.zip | 41,764,089 | `94FBE198A0EEAAA2D6A491EC1C10F5C4020D1D5A82985DAF19799ACDD73F6999` | `203a320a9eb6d3f1ecdbe82923156638` |

总大小 **87,820,203 bytes**。三个本地 SHA-256 与原发布记录及当前 GitHub release asset digest 一致，三个 MD5 与当前 Zenodo API 一致。

最初 Zenodo 的大附件下载停滞，已终止该下载进程，改从同一项目的原 GitHub release 镜像获取两份 ZIP；校验文本来自 Zenodo。不是只凭文件名认定镜像等价。两份 ZIP 分别有 152 与 1,180 entries，CRC 检查通过，未解压或执行其中代码。失败下载遗留的本轮 `.partial` 文件在验证绝对路径后移除，共 16,830,464 bytes；三份完整历史文件保留。

没有删除任何远端数据、Git 标签、GitHub release、本地历史稿或原始失败证据。

## 7. 访问障碍及已尝试的恢复

内置浏览器首次访问旧记录返回 `ERR_NAME_NOT_RESOLVED`；重试进入同一错误页面。随后使用可用 Edge 连接访问，同样返回域名解析错误。未绕过浏览器安全提示，未修改 DNS、代理、VPN 或浏览器配置，未读取 Cookie、会话存储或密码。

系统只读 DNS 查询返回地址；本机 curl 对公开 Zenodo API 的请求成功，且获取了实际 JSON。由此只能判断当前浏览器路径与公开 API 路径的可达性不同，不能断言 Zenodo 整体宕机，也不能判断作者账户已退出登录。

仅检查了 `ZENODO_ACCESS_TOKEN` / `ZENODO_TOKEN` 两个命名环境变量是否配置，均未配置；未搜索凭据文件或索取用户秘密。没有借 GitHub 已登录推断拥有 Zenodo 写权限。

已请用户在 Edge 打开旧记录，恢复正常访问并确认所属账户已登录，明确无需发送密码或令牌。用户随后回复“ZENODO已经登录”。2026-08-29 07:44 HKT 已实际读取所属账户上传列表、旧记录 22086892，以及 Manage / Edit / New version / Share 菜单。仅记录本项目状态，不操作同账户下的其他项目。

旧记录仍为公开 1.0.0，作者、许可证、三个附件与公开 API 相符。上传列表未见本项目草稿，New version 入口可见。已就“创建关联草稿及预留 DOI，沿用作者姓名、ORCID、单位和许可证，不发布、不删除”发送精确的操作时确认；该步骤尚未执行。先前的 DNS 失败保留为过程记录，不继续错误标作当前阻断。

## 8. 新版本准备与剩余顺序

[Zenodo_New_Version_Plan.json](qiteng_r2_freeze_2026-08-29/Zenodo_New_Version_Plan.json)已准备标题、两位作者、ORCID、单位、双许可证适用范围、研究解释边界和旧记录替换说明。它是本地计划，**不是已保存的 Zenodo 草稿或可直接提交的 API 请求体**。

建议内部新版本为 1.1.0，但须先检查账户是否已有草稿；不重复生成记录。对外文件名使用 `Research_Archive.zip`、`Source_Code.zip`、`SHA256SUMS.txt`，不把内部 gate/迭代编号写进面向使用者的文件名。

账户访问已恢复，按以下顺序继续：

1. 检查并创建或恢复同一版本链的草稿，预留真实的新版本 DOI。
2. 只更新新归档稿的批准句、Data Availability、归档参考文献和引用元数据，检查 9 部分科学内容及冻结证据不变。
3. 重新渲染有行政修改的 DOCX/PDF，构建科学复现归档与对应源码快照，校验完整清单。历史投稿信/门户清单不冒充本次已确认文件。
4. 完成具体文件/作者信息/目标记录的操作时确认，发布后验证 record 状态、DOI 解析、文件集、大小与校验值。
5. 新版本 verified 后才处理旧 record 22086892；确认删除范围只限旧版本，保存 tombstone 和新旧关联。保留本地备份与 Git 历史。

无需为了进行本次已请求的科学归档而重开生信分析或先确定目标刊。JCR Q1 证明、APC 可行性、期刊最终格式和真正投稿仍是独立的后续事项。

## 9. 代码、测试与同步

新增 [phase17_postc9_16_verify_scientific_freeze.py](../audit_tools/phase17_postc9_16_verify_scientific_freeze.py) 与 [test_scientific_freeze.py](../audit_tools/test_scientific_freeze.py)。九项新测试覆盖批准越界、HOLD 缺失、技术 PASS 与科学 HOLD 分离、outcome 解锁、科学词句/标题漂移、行政 DOI 区分、缺失段落、证据篡改/重复和路径越界。

组合执行 **59 项唯一测试通过**，即上一轮 50 项加本轮 9 项。冻结检查和历史候选检查均实跑通过。本轮没有新增 DOCX/PDF，因此没有把上一轮 18 页渲染算作新做的排版质控。

复核命令：

```powershell
Set-Location 'H:\cuhk-2025fALL\6013RP-wyf\audit_tools'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest test_review_bundle test_target_preparation test_refined_manuscript test_scientific_freeze -v
Set-Location 'H:\cuhk-2025fALL\6013RP-wyf'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' audit_tools/phase17_postc9_16_verify_scientific_freeze.py --output 00_project_management/qiteng_r2_freeze_2026-08-29/freeze_verification.json
```

这两项已执行，不要求用户重复运行。执行途中 `gh` 不在 PATH，改用现有 GitHub connector 获取 release 元数据；一条嵌套引号形式的 ZIP CRC 命令出现语法错误，改为 PowerShell here-string 传入 Python 后通过。以上均未修改科学文件。

README 现在以 `distinguishes` 的新确认标题为入口，并明确新版本请求尚未执行；原审阅页追加本轮确认链接，旧机器审计和原始文件不回写。`.gitattributes` 为新证据目录保留原字节。Git 同步实绩将在 [Git_Sync_Receipt.md](qiteng_r2_freeze_2026-08-29/Git_Sync_Receipt.md)记录，不把源码同步等同于 DOI 发布。

最终逐项状态见 [publication_readiness.json](qiteng_r2_freeze_2026-08-29/publication_readiness.json)。**下一阶段为真实 DOI 预留、行政信息整合、受控发布与旧记录处理；账户访问已经恢复，不再请求重新批准已经确认的科学主轴，也不进行救 PASS 分析。**
