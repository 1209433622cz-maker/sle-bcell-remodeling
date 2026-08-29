# SLE B-cell remodeling：v1.1.0 / Zenodo 22151739 独立全量审计

日期：2026-08-29  
项目：`1209433622cz-maker/sle-bcell-remodeling`  
GitHub `main` latest：`395bb55de19416079f4cac0fbd87a61907a818d7`  
GitHub release：`v1.1.0`  
Release content commit：`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`  
Zenodo version DOI：`10.5281/zenodo.22151739`  
Concept DOI：`10.5281/zenodo.22086891`  
旧 version DOI：`10.5281/zenodo.22086892`（tombstone）  
当前科学基线：author-confirmed QiTeng R2  
目标：JCR Q1 / SCI 一区，尚未冻结具体期刊

---

## 1. 总体导师结论

项目科学主体已经完成。

当前没有新的生物信息学 P0，不建议首投前新增：

- cohort；
- clustering；
- mapper；
- TF/regulon；
- gene-set family；
- threshold search；
- seed/replicate rescue；
- C9R outcome unlock；
- R1 HOLD rescue。

当前真正剩余的高价值工作是：

1. 修复 GitHub `main` 的 release-documentation drift；
2. 正式核验 JCR Q1；
3. 选择目标期刊；
4. 仅做一次 journal-specific title/abstract/format adaptation；
5. exact-file author approval；
6. submission preflight。

---

## 2. GitHub 当前状态

### Latest `main`

`395bb55de19416079f4cac0fbd87a61907a818d7`

该提交记录：

- 旧 Zenodo 22086892 tombstone；
- 新 Zenodo 22151739；
- GitHub v1.1.0 release；
- 公开资产 hash 验证；
- 无新科学分析。

### GitHub `v1.1.0`

Annotated tag object：

`6e492e3dcd5e6ee89b386e6c459622dffe0d9269`

Peels to：

`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`

GitHub release：

- release ID：378885936
- draft：false
- prerelease：false
- latest release：true

公开 assets：

| Asset | Bytes | SHA-256 |
|---|---:|---|
| Research_Archive.zip | 25,577,813 | AAE67863FC6B34B0AC091F8D38524FFC55A7CF364FF7FF4B4D43FEDFA4AE0095 |
| Source_Code.zip | 78,040,863 | 51B1007908668F8EE25971E99270BF8477720A25ED7491BACD2F7572A4E24645 |
| SHA256SUMS.txt | 171 | BE96EEC9C0610208F867FE7258A3C7E672A63E8273C486CC09CAAE2BFCDB457B |

GitHub release 与 Zenodo v1.1.0 三个资产一致。

---

## 3. Zenodo 22151739

公开验证记录显示：

- status：`PASS_PUBLIC_ZENODO_RELEASE_VERIFIED`
- record ID：22151739
- DOI：10.5281/zenodo.22151739
- version：1.1.0
- publication date：2026-08-29
- open access
- 2 creators
- MIT + CC BY 4.0 scope
- R1 HOLD / C9R HOLD preserved
- corrected external outcome unlock = false

旧记录 22086892：

- API status 410
- tombstone visible
- removal reason stored as `retracted`
- old DOI citation retained
- concept DOI now resolves to 22151739

### 建议

新版本是当前正式 reproducibility DOI。

最终期刊稿的 Data Availability 可以只引用 22151739。旧 DOI 的历史替代关系已经由 Zenodo version chain / GitHub provenance 保留，不一定需要继续在 reader-facing journal text 中强调 tombstone。

---

## 4. 上传文件与 release 对齐

用户上传：

`Manuscript(1).docx`
SHA-256：
`3D8155E204241BA7C33F4CDE820F5D1B858EDB9713A5740453A97DC0410BF8C6`

`Manuscript(1).pdf`
SHA-256：
`117B694FD63C3FFEE421DFCD5A94F057F460689612E7D4AAE67E4F821CB1755C`

这两个 SHA 与 `zenodo_release.zip` 中：

- `manuscript/Manuscript.docx`
- `manuscript/Manuscript.pdf`
- `wps_render/Manuscript_WPS.pdf`

完全一致。

因此本轮审阅对象就是 v1.1.0 Research Archive 内的正式 manuscript，不存在用户附件和 archive 之间的版本漂移。

---

## 5. Research Archive 独立完整性

`Research_Archive.zip`：

- 59 files including manifest
- `CONTENT_MANIFEST_SHA256.csv` payload rows：58
- 58/58 SHA-256 PASS
- 58/58 size PASS
- missing：0
- extra：0

主要包含：

- manuscript DOCX/MD/PDF；
- supplementary DOCX/MD/PDF；
- Figures 1–5；
- Supplementary Figures S1–S10；
- Figure Source Data；
- Full Statistical Results；
- Regulator Sensitivity；
- R1/C9R governance；
- reproducibility documents；
- license scope；
- quality-control receipts。

这是一个成熟的 reproducibility compendium。

---

## 6. Source_Code.zip 独立安全/边界检查

Source_Code.zip 是 exact Git archive of commit：

`f1859ff8498d5569a1d5027b36ed18c8b7c7536f`

快速扫描：

- 未发现 `.env` / credential / private-key filenames；
- 未发现 GitHub PAT、OpenAI key、AWS access key、private-key 等明显 secret patterns；
- 包中存在大量 action records、`received/` 和 pasted-review/text provenance。

因此目前没有发现 credential leak。

但 Source_Code.zip 是“完整 Git provenance snapshot”，不是“最小生产代码包”。它公开了较多内部审计与对话/收件材料。由于 repository 本身已经 public 且历史公开，这不是当前 P0；以后若新增对外代码包，可另行提供一个 minimal-source bundle，而不应破坏历史 Git provenance。

---

## 7. 一个新的 P0：GitHub `main` README / REPRODUCIBILITY 已落后于实际 release

最新 `Scientific_Freeze.md` 已正确写：

- Zenodo 22151739 已发布；
- GitHub v1.1.0 已发布；
- 22086892 已 tombstone。

但当前根目录 `README.md` 仍写：

- existing citable archive = 22086892；
- matching new archive required；
- new version not yet published；
- old record not deleted。

`REPRODUCIBILITY.md` 也仍以：

- initial DOI 不匹配 corrected package；
- matching archive / release pending

作为 current 状态。

### 这是当前最明确的 release-documentation defect

科学结果没有问题，但 reviewer/reuser 打开默认 README 会读到与 public release 相反的信息。

### 建议修复

仅在 `main` 更新：

- README current DOI -> 22151739；
- old DOI -> historical tombstone；
- GitHub `v1.1.0` -> public verified release；
- journal submission -> still not authorized；
- R1/C9R -> HOLD unchanged。

同时更新 `REPRODUCIBILITY.md` 的 current release section。

**不要移动 v1.1.0 tag，不要改已公开 assets。**

---

## 8. archive 内 author_freeze.json 的“旧状态”需要解释，而不是篡改

Research Archive 中的：

`governance/author_freeze.json`

仍记录：

- browser_publication_confirmation_completed=false
- new_zenodo_published=false
- old_zenodo_deleted=false

这不是科学错误，而是它保存的是“发布动作执行前的作者授权状态”。

顶层 `Release_Metadata.json`、Research Archive README 以及 post-release GitHub verification 则记录发布后的真实状态。

### 建议

不要修改已发布 v1.1.0。

在 `main` / 下一版本中把该文件明确标记为：

`pre-publication author authorization receipt`

并以 post-release verification JSON 作为 current administrative truth。

---

## 9. Manuscript 内容审计

当前 title：

> Disease-blind single-cell reconstruction distinguishes unstable B-cell state assignments from reproducible interferon remodeling in systemic lupus erythematosus

这个标题现在是准确的。

它避免将“state assignment instability”误写成 biological state 本身不存在。

### 科学叙事

当前层级正确：

1. identity validity；
2. composition；
3. B_CONV transcription；
4. independent source-label-defined GSE135779 replication；
5. corrected external-remapping limitation；
6. regulator/response convergence；
7. claim boundary。

### Abstract

按本轮简单 tokenization 约 350+ words（约 356；Word/期刊 tokenizer 可有差异）。

因此：

- journal-neutral 阶段不是问题；
- 若目标要求 <=350，必须压缩；
- Communications Biology / 部分 Nature Portfolio 若要求更短 abstract，则需要 target-specific rewrite。

不要在选刊前继续无目标改写。

### References

- 32 numbered references；
- new Zenodo DOI 出现 2 次；
- old DOI 出现 1 次；
- no reference-number drift detected。

---

## 10. Manuscript DOCX/PDF QA

### PDF

- pages：18
- US Letter
- WPS-rendered
- fonts embedded：
  - Times New Roman
  - Arial
  - Arial Bold
- no encryption
- no forms
- no JavaScript

18/18 页面视觉复核：

- 无 clipping；
- 无 overlap；
- 无缺字；
- 无异常分页；
- references 未溢出。

### DOCX

- tracked insertions：0
- tracked deletions：0
- comment references：0
- orphan empty `comments.xml` exists，但无可见/锚定 comments
- accessibility：
  - high = 0
  - medium = 0
  - low = 5（均为 raw URL hyperlink display）

因此当前 manuscript 文件本身可作为高质量 review baseline。

---

## 11. Figures 1–5 + S1–S10 独立 Nature-style audit

共 15 张 publication PDFs。

### Physical dimensions

全部：

- width = 170.0 mm

height：

- main figures最大约 163.05 mm
- supplementary figures最大约 160 mm

### Typography

全部：

- Arial / Arial Bold
- minimum visible text = 5.0–6.0 pt
- maximum non-panel text <= 7 pt
- panel labels = 8 pt
- vector PDF

### 视觉

未发现新的：

- clipping；
- overlap；
- hidden labels；
- Figure 1 threshold semantic error；
- Figure 5 causal-chain misrepresentation。

结论：

**journal-neutral Nature-style typography PASS。**

170 mm 不是 Nature 自身 183-mm production width；在 target journal 未确定前，不应该再为了尺寸重跑图件。

---

## 12. 当前科学证据链

保持：

- 150,402 discovery B-lineage cells；
- 259 donors / 271 samples / 88 libraries；
- fine-grained hard state assignment not sufficiently stable；
- B_CONV/B_ASC = analysis scaffold；
- R1 formal HOLD；
- R1 HOLD driven by B_ASC median Jaccard 0.930323 <0.95；
- B_CONV median Jaccard ~0.99936；
- assignment-boundary propagation retains B_ASC composition null；
- primary B_CONV IFN/ISG positive；
- donor-nonoverlap internal IFN positive；
- source-label-defined GSE135779 childhood replication positive；
- genome-wide rho=0.026；
- STAT1/STAT2 observational convergence；
- narrow overlap depletion retains support；
- M5911 depletion attenuates discovery STAT2；
- C9R corrected calibration HOLD；
- no corrected external disease outcome；
- no universal taxonomy / causal TF / unique ligand / clinical utility claim。

该证据链已经达到 public-data computational study 的合理上限。

---

## 13. 旧 Zenodo tombstone 的表达风险

旧 22086892 tombstone 的 machine-readable removal reason 为：

`retracted`

但真实执行语义是：

“verified replacement 后的 administrative withdrawal”。

GitHub v1.1.0 release body已经明确写明这是 replacement 后 withdrawn，而不是科学 misconduct / result invalidation。

### 建议

最终期刊稿只引用新 DOI 22151739。

如果期刊或 reviewer询问旧 DOI，再解释：

> the initial reproducibility snapshot was administratively withdrawn after verified replacement by v1.1.0; the DOI tombstone is preserved for citation history.

不要把 old tombstone 放成正文亮点。

---

## 14. Journal strategy

当前不应依据 JIF/SJR 自动声称 JCR Q1，最终 Q1 必须由 Clarivate / 机构 JCR profile 核验。

### Fit-based candidate 1：npj Systems Biology and Applications

官方 scope 直接包括：

- single-cell systems biology；
- systems immunology；
- disease modeling；
- computational/mathematical analysis of complex systems。

2025 publisher-reported JIF：4.4。

当前开放 Systems Immunology Collection，deadline：2026-09-12。

从论文 conceptual fit 看，当前最自然。

### Fit-based candidate 2：Communications Biology

官方 scope 明确接受：

- secondary data analysis；
- innovative computational methods。

2025 publisher-reported JIF：5.8。

优点：品牌/广度更强。
风险：editor 对“known SLE IFN biology 是否提供足够 novel biological insight”要求更高。

### Stretch：Genome Medicine

scope仍匹配，但当前：

- secondary public-data study；
- known IFN biology；
- source-label-independent external robustness unresolved；
- no prospective cohort；
- no demonstrated clinical utility。

因此不应因历史准备惯性默认首投。

### 当前导师排序

若机构确认 JCR Q1：

1. **npj Systems Biology and Applications**
2. **Communications Biology**
3. **Genome Medicine（stretch）**

---

## 15. 当前完成度

| Module | Readiness |
|---|---:|
| Scientific design | 98% |
| Statistical rigor | 98% |
| R1 boundary transparency | 99% |
| Identity uncertainty propagation | 98% |
| Source-label-defined independent validation | 96% |
| C9R correction governance | 99% |
| Regulatory robustness | 97% |
| Manuscript logic | 98% |
| Main figures | 99% |
| Supplementary figures | 99% |
| Source-data traceability | 99% |
| Research Archive integrity | 100% |
| GitHub/Zenodo asset integrity | 100% |
| Public release governance | 98% |
| GitHub current documentation consistency | 82% |
| Journal target verification | pending |
| Target-specific final files | pending |
| Portal readiness | pending journal selection |

---

## 16. 下一阶段唯一正确目标

建议状态：

`JCR_Q1_JOURNAL_SELECTION_AND_FORMAT_ADAPTATION`

### Phase 0：先修当前 repo documentation drift

只更新 main：

1. README；
2. REPRODUCIBILITY；
3. 可选新增 `CURRENT_RELEASE_STATUS.md`。

不改 scientific results；
不移动 v1.1.0；
不重发 Zenodo。

### Phase 1：JCR Q1 verification

从 Clarivate/机构获取：

- metric year；
- category；
- rank / denominator；
- quartile；
- APC/OA agreement。

### Phase 2：target freeze

若 npj SBA 与 Communications Biology 均为机构认可的 JCR Q1：

优先推荐：
**npj Systems Biology and Applications**

尤其当前 Systems Immunology Collection 与文章主题高度契合。

### Phase 3：一次性 target-specific adaptation

只改：

- title；
- abstract；
- section order；
- AI disclosure placement；
- journal exact figure size；
- cover letter；
- journal-required declarations。

不改：

- R1/C9R HOLD；
- statistics；
- source data；
- gene/program/TF selections；
- scientific conclusions。

### Phase 4：exact-file author approval + submission

目标期刊格式冻结后：

- WPS/PDF QA；
- hashes；
- 两位作者 exact-file approval；
- portal preflight；
- submission receipt freeze。

---

## 17. STOP rules

首投前不再：

- 新 cohort；
- 新 mapper；
- 新 classifier threshold；
- seed rescue；
- new gene set；
- new regulon database；
- new TF sweep；
- R1/C9R rescue；
- manual PDF edits。

只有 decision-changing implementation defect 才重新打开 computation。

---

## 18. 最终导师判断

v1.1.0 / Zenodo 22151739 已经是一个高质量、可验证的科学 reproducibility release。

当前最大的真实缺口不是生物信息学，而是：

> GitHub 默认 README / REPRODUCIBILITY 尚未同步到已经发生的 v1.1.0 + tombstone 状态，以及 JCR Q1 目标尚未正式冻结。

科学上继续分析的边际收益已经为负。

下一阶段应从“研究”切换到：

**release documentation cleanup -> JCR Q1 selection -> journal-specific adaptation -> exact-file approval -> submission。**
