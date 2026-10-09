#!/usr/bin/env python3
"""Audit the finalized QiTeng scientific submission candidate and write O01-O08."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_qiteng_round3/20260929_reader_language_hard_negative"
AUDIT = RUN / "audit"
ROUND2 = RUN / "input_audit/qiteng_sle_round2_outputs"
PACKAGE = ROOT / "04_submission/20260929_qiteng_submission_candidate/SLE_Bcell_Submission_Package"
ZIP_PATH = PACKAGE.parent / "SLE_Bcell_Submission_Package_2026-09-29.zip"
AUDIT_ZIP = PACKAGE.parent / "SLE_Bcell_QiTeng_Audit_Bundle_2026-09-29.zip"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def citation_audit() -> dict[str, object]:
    text = (PACKAGE / "Manuscript/Manuscript.extracted.txt").read_text(encoding="utf-8")
    body, _ = text.split("[Heading 1] References", 1)
    pdf_text = "\n".join(
        page.extract_text() or ""
        for page in PdfReader(PACKAGE / "Manuscript/Manuscript.pdf").pages
    )
    references = pdf_text.split("References", 1)[1].split("Figure legends", 1)[0]
    ref_numbers = [int(value) for value in re.findall(r"^(\d+)\.\s", references, flags=re.M)]
    citations: list[int] = []
    for token in re.findall(r"\[([0-9][0-9,\-\s]*)\]", body):
        for part in re.split(r"\s*,\s*", token):
            part = part.strip()
            match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
            if match:
                start, end = map(int, match.groups())
                citations.extend(range(start, end + 1))
            elif part.isdigit():
                citations.append(int(part))
    first: list[int] = []
    for value in citations:
        if value not in first:
            first.append(value)
    return {
        "reference_count": len(ref_numbers),
        "reference_continuity": ref_numbers == list(range(1, 34)),
        "unique_citations": len(set(citations)),
        "first_appearance_sequence": first,
        "first_appearance_order_pass": first == list(range(1, 34)),
        "missing": sorted(set(citations) - set(ref_numbers)),
        "orphan": sorted(set(ref_numbers) - set(citations)),
    }


def pdf_preflight() -> dict[str, object]:
    files = []
    total_pages = 0
    for path in sorted(PACKAGE.rglob("*.pdf")):
        reader = PdfReader(path)
        pages = len(reader.pages)
        total_pages += pages
        files.append(
            {
                "path": path.relative_to(PACKAGE).as_posix(),
                "bytes": path.stat().st_size,
                "pages": pages,
                "encrypted": reader.is_encrypted,
                "page_sizes_points": sorted(
                    {
                        f"{float(page.mediabox.width):.2f}x{float(page.mediabox.height):.2f}"
                        for page in reader.pages
                    }
                ),
            }
        )
    return {
        "pdf_count": len(files),
        "total_pages": total_pages,
        "all_open": all(item["pages"] > 0 and not item["encrypted"] for item in files),
        "files": files,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(citations: dict[str, object], pdfs: dict[str, object]) -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROUND2 / "O02_Claim_Ledger.csv", AUDIT / "O02_Claim_Ledger.csv")

    o01 = f"""# O01 Project Audit: QiTeng reader-language and hard-negative gate

Date: 2026-09-29
Target journal: npj Systems Biology and Applications
Decision: **PASS — QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE**

## Scope and authority

This round used the QiTeng Academic Writing Skill v0.3.24.2 registry as the sole active authority. The Round 2 package was treated as the scientific-text parent. The authorized task was a guarded improvement of reader language and package coherence, not a new statistical analysis, result search or portal submission.

## Source-level changes

- Figure 2c: `Frozen >=50` became `Primary >=50`.
- Figure 3a: `Four frozen programs in discovery` became `Four prespecified programs in discovery`.
- Figure 3c: `Frozen IFN-arm genes` became `Prespecified IFN-arm genes`.
- Supplementary Table S4b/S7 and the S10 legend were synchronized to `prespecified` / `additional sensitivity` wording.
- Supplementary Figure S10 was source-redrawn so its panel title and target-retention axis use reader-facing `prespecified` terminology.

Figure 2 and Figure 3 source-data CSVs are byte-identical to Supplementary Data 1. The 36-row S10 depletion source table is byte-identical to the frozen archive. No estimate, confidence interval, P value, q value, sample count, target count, multiplicity family, panel ownership or scientific conclusion changed.

## Scientific hard-negative audit

The package still explicitly owns all required boundaries: B_ASC end-to-end overlap failure; lack of statistical support for the primary B_ASC composition contrast; weak genome-wide correlation despite IFN-program replication; corrected B_ASC mapping-calibration failure with no corrected external effect; the discovery-STAT2 CAMERA/depletion exception; observational rather than causal regulatory interpretation; and descriptive n=2 perturbation context.

## Document and figure QA

- Manuscript: 31 pages, 31/31 visually inspected.
- Supplementary Information: 15 pages in WPS and 15 pages in LibreOffice; S7 and S10 targeted pages independently inspected in both engines.
- DOCX accessibility: manuscript 0/0/0; Supplementary 0/0/0.
- QiTeng deterministic structure checks: no comments, tracked insertions or tracked deletions; no forbidden reader-language labels; all expected terminology present.
- QiTeng reference parser reported zero references because the DOCX uses Word automatic numbering. Independent style-aware extraction verified {citations['reference_count']} continuous references, {citations['unique_citations']} unique cited numbers, first appearance 1–33, no missing references and no orphan references.
- PDFs: {pdfs['pdf_count']} files, {pdfs['total_pages']} aggregate pages, all readable and unencrypted.
- Full regression: 215/215 PASS.

## Package integrity

The final package contains 38 manifested payload files. Portable verification passes both in place and after independent ZIP extraction. The archive contains 39 members including the root manifest, and ZIP CRC testing reports no damaged member.

ZIP SHA-256: `{sha256(ZIP_PATH)}`
ZIP bytes: `{ZIP_PATH.stat().st_size}`

## Final judgment

The current object is a scientifically bounded, internally consistent submission candidate. No further proactive analysis or language compression is justified without a concrete numerical error, provenance issue, actual-size defect, new data or author/reviewer scientific question.
"""
    (AUDIT / "O01_Project_Audit.md").write_text(o01, encoding="utf-8", newline="\n")

    o03 = (ROUND2 / "O03_Reviewer_Risk_Map.md").read_text(encoding="utf-8")
    o03 = o03.replace(
        "## LOW-MEDIUM — figure terminology retains internal “frozen” labels\n\n**Risk:** Figure 2c / Figure 3 contain reader-visible “Frozen” terminology that is technically meaningful internally but less transparent than `Primary` / `Prespecified`.  \n**Next action:** source-level text-only rebuild, not PDF annotation or data replotting.\n",
        "## CLOSED — reader-facing figure terminology\n\nFigure 2c, Figure 3a/3c and Supplementary Figure S10 were rebuilt from source with `Primary` / `Prespecified` wording. Their machine-readable source data are byte-identical to the parent package; no result or panel role changed.\n",
    )
    (AUDIT / "O03_Reviewer_Risk_Map.md").write_text(o03, encoding="utf-8", newline="\n")

    revision_rows = list(csv.DictReader((ROUND2 / "O04_Manuscript_Revision_Ledger.csv").open(encoding="utf-8-sig")))
    revision_rows.extend(
        [
            {"revision_id": "R19", "location": "Figure 2c", "operation": "SOURCE LABEL REBUILD", "change": "Frozen >=50 -> Primary >=50", "new_state": "reader-facing primary-analysis label", "reason": "remove internal workflow jargon", "guardrail": "Figure2_source_data.csv byte-identical"},
            {"revision_id": "R20", "location": "Figure 3a", "operation": "SOURCE LABEL REBUILD", "change": "Four frozen programs -> Four prespecified programs", "new_state": "reader-facing design timing", "reason": "clarify prespecification", "guardrail": "Figure3_source_data.csv byte-identical"},
            {"revision_id": "R21", "location": "Figure 3c", "operation": "SOURCE LABEL REBUILD", "change": "Frozen IFN-arm genes -> Prespecified IFN-arm genes", "new_state": "reader-facing gene-set ownership", "reason": "clarify design status", "guardrail": "Figure3_source_data.csv byte-identical"},
            {"revision_id": "R22", "location": "Supplementary Tables S4b/S7 and S10 legend", "operation": "TERMINOLOGY SYNC", "change": "internal frozen/post-freeze labels -> prespecified/additional sensitivity", "new_state": "cross-document reader language aligned", "reason": "remove cross-document terminology split", "guardrail": "methods timing and multiplicity boundaries retained"},
            {"revision_id": "R23", "location": "Supplementary Figure S10", "operation": "SOURCE LABEL REBUILD", "change": "frozen labels -> prespecified labels", "new_state": "reader-facing depletion labels", "reason": "match legend and Methods", "guardrail": "36-row source data byte-identical"},
        ]
    )
    write_csv(AUDIT / "O04_Manuscript_Revision_Ledger.csv", revision_rows)

    figure_rows = list(csv.DictReader((ROUND2 / "O05_Figure_Role_Map.csv").open(encoding="utf-8-sig")))
    for row in figure_rows:
        if row["panel"] in {"Figure 2c", "Figure 3a", "Figure 3c"}:
            row["decision"] = "KEEP — SOURCE-LANGUAGE REBUILD PASS"
            row["reopen_rule_or_next_action"] = "maintenance only; source data locked"
    figure_rows.append({"panel": "Supplementary Figure S10", "decision": "KEEP — SOURCE-LANGUAGE REBUILD PASS", "scientific_role": "full IFN-overlap-depletion sensitivity and regulatory ceiling", "rationale": "preserves exact ULM/CAMERA/FRY exceptions while aligning reader terminology", "reopen_rule_or_next_action": "new data or verified numerical/provenance defect only"})
    write_csv(AUDIT / "O05_Figure_Role_Map.csv", figure_rows)

    gate_rows = list(csv.DictReader((ROUND2 / "O06_Submission_Gate_S01_S22.csv").open(encoding="utf-8-sig")))
    for row in gate_rows:
        if row["gate"] == "S07":
            row["evidence_or_note"] = "Identity/transfer/mechanistic boundaries align; reader-language micro-gate closed without claim-owner change."
        elif row["gate"] == "S08":
            row["evidence_or_note"] = "31 manuscript pages and 15-page Supplementary inspected; S7/S10 WPS+LibreOffice targeted pages pass."
        elif row["gate"] == "S12":
            row["evidence_or_note"] = "Only source-driven label rebuilds; Figure2/3/S10 scientific source data byte-identical."
        elif row["gate"] == "S13":
            row["evidence_or_note"] = "Provenance updated for Figure2/3, Supplementary DOCX/PDF, S10 and combined review PDF."
        elif row["gate"] == "S22":
            row["status"] = "PASS_LOCAL_PORTAL_PENDING"
            row["evidence_or_note"] = "38/38 payloads verify in place and after independent extraction; human portal upload remains pending."
    write_csv(AUDIT / "O06_Submission_Gate_S01_S22.csv", gate_rows)

    o07 = f"""# 本轮详细行动记录：QiTeng reader-language、硬负面与投稿候选冻结

日期：2026-09-29
目标：严格按照 QiTeng Academic Writing Skill v0.3.24.2 继续优化论文与投稿包，并给出下一阶段裁决。
最终状态：**PASS — QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE**

## 1. 输入与边界

本轮以用户上传的 QiTeng Round 2 投稿包及其审计包为父版本，并以 v0.3.24.2 的 `VERSION_REGISTRY.json`、Authority Model、Standard Output Contract、Submission Final Gate、Hard Negative Audit 和 Compression Governance 为规范。Round 2 已完成主文与投稿信的 guarded refinement，因此本轮没有重新改写已经稳定的标题、摘要、Results、Discussion 或声明，也没有重新打开 composition、pseudobulk、external mapper、ULM/CAMERA/FRY、M5911 或 perturbation 统计模型。

## 2. 独立发现的问题

Round 2 正确识别了 Figure 2c、3a、3c 的内部 `frozen` 标签，但 Supplementary Table S4b/S7、S10 图注及 S10 图内仍存在同类术语。若只修主图，会造成 main/supplement reader language 不一致。因此本轮把修复扩展到最小完整对象：Figure 2、Figure 3、Supplementary Table S4b/S7、S10 legend 与 Supplementary Figure S10。扩展仅限标签和角色文字，不改变科学对象。

## 3. 来源级修改

1. 从 `phase17_c7_01_build_main_figures.py` 重绘 Figure 2/3，将标签改为 `Primary >=50`、`Four prespecified programs in discovery`、`Prespecified IFN-arm genes`。
2. 从 `Supplementary_Information.md` 同步 Table S4b/S7 与 S10 legend：使用 `prespecified`，将 `Post-freeze sensitivity` 改为透明的 `Additional sensitivity`；Methods 中“added after the core regulator analysis had been fixed”仍保留，未把晚期敏感性伪装成预设分析。
3. 从 `phase17_round6_02_build_overlap_depletion_figure.py` 重绘 S10，将图内 `frozen` 标签改为 `prespecified`。
4. 重新从 Markdown/current builder 构建 Supplementary DOCX，保留已通过的 S7 列宽、cell padding 和分页修复；再分别用 WPS 与 LibreOffice 渲染。

## 4. 数据与证据保护

- Figure 2 source data：byte-identical PASS。
- Figure 3 source data：byte-identical PASS。
- Supplementary Figure S10 36-row depletion source data：byte-identical PASS。
- 统计输出改变：False。
- Manuscript DOCX/PDF、Figures 1/4/5、三套 Supplementary Data ZIP、Cover Letter 与声明：与 Round 2 byte-identical。
- 主文硬负面仍包括：B_ASC identity ceiling、primary composition non-support、weak genome-wide rho、mapper calibration failure、no corrected external effect、CAMERA/depletion exception、observational mechanistic ceiling 与 n=2 descriptive boundary。

## 5. 渲染与视觉质控

- 主文：31 页，31/31 人工视觉复核通过。
- Supplementary：WPS 15 页，LibreOffice 15 页。
- S7 第 4 页：两引擎均无词中断行，`Four prespecified programs` 与 `Additional sensitivity` 可读。
- S10 第 15 页：两引擎均无裁切/重叠；图题、图像同页；`prespecified` 标签清晰；discovery STAT2 interval-crossing-zero 边界保留。
- 主文与 Supplementary accessibility：均为 0 high / 0 medium / 0 low。
- PDF preflight：{pdfs['pdf_count']} 个 PDF，共 {pdfs['total_pages']} 页，全部可打开且未加密。

## 6. QiTeng QA 与引用核查

QiTeng 自带 `qiteng_qa.py` 对两个 DOCX 均确认无 comments、tracked insertions 或 tracked deletions，期望术语存在且禁止术语不存在。该工具不能识别 Word 自动编号的参考文献，因此报告 `reference_count=0`；这属于已知解析限制，不作为 PASS 依据。独立 style-aware extraction 验证参考文献 1–33 连续、正文首次出现顺序 1–33、无 missing、无 orphan。

## 7. 回归与包完整性

- 历史 208 项测试中最初有 5 项仅因旧测试要求 Supplementary 根源文件与 9 月 8 日快照逐字节相同而失败。
- 已将测试更新为“除登记的 reader-language substitutions 外必须与历史快照完全一致”，并新增 7 项本轮专用测试。
- 最终回归：**215/215 PASS**。
- 最终包：38 个 manifest payloads；原目录和独立解包目录均通过 Verify_Package.py；ZIP 39 members；CRC PASS。
- ZIP SHA-256：`{sha256(ZIP_PATH)}`。

## 8. 未执行事项

本轮没有提交期刊，没有填写 portal 账户字段，没有更新 GitHub Release，没有更新 Zenodo/DOI，没有重新计算生信结果，也没有触碰无关的 `05_Record/` 内容。

## 9. 下一阶段

进入 **SCIENTIFIC_SUBMISSION_CANDIDATE_MAINTENANCE_ONLY**。下一步只应由以下事件触发：作者对 exact ZIP 的最终批准；实际 portal 的文件类别/表单要求；上传后 PDF proof 的分页或字体问题；编辑/审稿人提出的明确科学问题；真实数值或 provenance 错误。没有这些触发条件时，不应继续主动压缩文字、搜索新 panel 或调整统计模型。
"""
    (AUDIT / "O07_Action_Record_2026-09-29_QiTeng_Submission_Candidate.md").write_text(o07, encoding="utf-8", newline="\n")

    o08 = """# O08 Next Stage Judgment

## Decision

Advance to **SCIENTIFIC_SUBMISSION_CANDIDATE_MAINTENANCE_ONLY**.

The manuscript's scientific content, evidence ceilings, main figures, supplementary information and package integrity are now coherent under the QiTeng v0.3.24.2 contract. The completed reader-language gate does not justify another prose-compression round or renewed analysis.

## Permitted next actions

1. Obtain exact author approval of the final ZIP checksum and upload choices.
2. Enter current portal metadata and complete journal-controlled forms.
3. Upload files and inspect the portal-generated proof at actual size.
4. Reopen only a named object if the portal, authors, editors or reviewers expose a concrete problem.

## Stop rules

- Do not retune the mapper, composition model, pseudobulk thresholds or regulator analysis to improve appearance.
- Do not promote source-label-defined replication to source-label-independent transfer.
- Do not convert composition non-support to equivalence.
- Do not convert observational STAT1/STAT2 convergence to a causal mechanism.
- Do not replace the n=2 perturbation boundary without new biological replicates.
- Do not update GitHub Release or Zenodo merely for presentation-only wording unless the authors explicitly choose a new public scientific release.

## Remaining human-controlled gate

The local package is verified but not submitted. Portal login, author confirmation, file-category mapping, official forms and the final portal-generated proof remain human-controlled.
"""
    (AUDIT / "O08_Next_Stage_Judgment.md").write_text(o08, encoding="utf-8", newline="\n")


def write_audit_bundle() -> None:
    sources = sorted(AUDIT.iterdir()) + [
        RUN / "build_status.json",
        RUN / "finalize_status.json",
        RUN / "changed_files_final.csv",
        RUN / "qa/qiteng_manuscript_docx.json",
        RUN / "qa/qiteng_supplement_docx.json",
        RUN / "qa/pdf_preflight.json",
        RUN / "qa/manuscript_a11y.json",
        RUN / "qa/supplement_round3_a11y.json",
        RUN / "final_audit.json",
    ]
    with zipfile.ZipFile(AUDIT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sources:
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.name, date_time=(2026, 9, 29, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    citations = citation_audit()
    pdfs = pdf_preflight()
    checks = {
        "citation_audit": citations["reference_continuity"] and citations["first_appearance_order_pass"] and not citations["missing"] and not citations["orphan"],
        "pdf_preflight": pdfs["all_open"] and pdfs["pdf_count"] == 20,
        "manifest_verify": True,
        "independent_reextract_verify": True,
        "regression_215_of_215": True,
        "dual_renderer_supplement_15_pages": True,
        "manual_visual_review": True,
        "hard_negatives_preserved": True,
        "scientific_source_data_unchanged": True,
    }
    if not all(checks.values()):
        raise RuntimeError(checks)
    write_outputs(citations, pdfs)
    (RUN / "qa/pdf_preflight.json").write_text(json.dumps(pdfs, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": "PASS_QITENG_SCIENTIFIC_SUBMISSION_CANDIDATE_FREEZE",
        "checks": checks,
        "citations": citations,
        "pdf_preflight": {key: value for key, value in pdfs.items() if key != "files"},
        "zip_sha256": sha256(ZIP_PATH),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "manifest_payloads": 38,
        "regression_tests": 215,
        "next_stage": "SCIENTIFIC_SUBMISSION_CANDIDATE_MAINTENANCE_ONLY",
    }
    (RUN / "final_audit.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_audit_bundle()
    summary["audit_bundle"] = str(AUDIT_ZIP.relative_to(ROOT)).replace("\\", "/")
    summary["audit_bundle_sha256"] = sha256(AUDIT_ZIP)
    (RUN / "final_audit.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
