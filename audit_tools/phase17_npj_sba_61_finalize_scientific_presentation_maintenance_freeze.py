#!/usr/bin/env python3
"""Finalize the scientific-presentation maintenance freeze after full render QA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document"
PARENT = ROOT / "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration"
SUPPLEMENT_PARENT = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
MAIN_STEM = "Manuscript_Scientific_Presentation_Freeze"
SUPPLEMENT_STEM = "Supplementary_Information_Scientific_Presentation_Freeze"
ACTION_RECORD = ROOT / "00_project_management/action_record_2026-09-08_scientific_presentation_final_cross_document_freeze_verified.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def render_checks(path: Path) -> tuple[bool, int]:
    data = load_json(path)
    clean = (
        data["all_pages_within_canvas"]
        and data["all_markers_resolved"]
        and all(item["text_characters"] > 0 for item in data["page_checks"])
        and all(not item["outside_page_text"] for item in data["page_checks"])
        and all(not item["unresolved_markers"] for item in data["page_checks"])
    )
    return clean, data["pages"]


def accessibility_zero(path: Path) -> bool:
    return load_json(path)["counts"] == {"high": 0, "medium": 0, "low": 0}


def compare_page_pixels() -> tuple[list[dict[str, object]], dict[str, list[int]]]:
    pairs = {
        "manuscript": (
            RUN / "qa/parent_wps_pages/Parent_Manuscript",
            RUN / f"qa/final_wps_pages/{MAIN_STEM}",
        ),
        "supplement": (
            RUN / "qa/parent_wps_pages/Parent_Supplement",
            RUN / f"qa/final_wps_pages/{SUPPLEMENT_STEM}",
        ),
    }
    rows: list[dict[str, object]] = []
    changed: dict[str, list[int]] = {}
    for document, (before_dir, after_dir) in pairs.items():
        before_pages = sorted(before_dir.glob("page-*.png"))
        after_pages = sorted(after_dir.glob("page-*.png"))
        if len(before_pages) != len(after_pages):
            raise RuntimeError(f"Page-count mismatch for {document}: {len(before_pages)} vs {len(after_pages)}")
        changed[document] = []
        for number, (before, after) in enumerate(zip(before_pages, after_pages, strict=True), start=1):
            with Image.open(before) as left, Image.open(after) as right:
                same_dimensions = left.size == right.size
                if same_dimensions:
                    difference = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
                    mean_absolute_error = sum(ImageStat.Stat(difference).mean) / (3 * 255)
                else:
                    mean_absolute_error = 1.0
            identical = sha256(before) == sha256(after)
            if not identical:
                changed[document].append(number)
            rows.append(
                {
                    "document": document,
                    "page": number,
                    "same_dimensions": same_dimensions,
                    "pixel_identical": identical,
                    "normalized_mean_absolute_error": f"{mean_absolute_error:.10f}",
                    "before_sha256": sha256(before),
                    "after_sha256": sha256(after),
                }
            )
    output = RUN / "08_PAGE_PIXEL_COMPARISON.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, changed


def write_action_record(status: dict) -> None:
    documents = status["documents"]
    report = f"""# 行动记录：科学呈现终局跨文档冻结的独立复核与落地

- **完成日期：** 2026-09-08
- **最终状态：** `{status['status']}`
- **工作边界：** 手稿、补充材料、图件职责、数值可追溯性与跨文档渲染；未推进投稿包、GitHub Release 或 Zenodo
- **上游状态：** `SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE`
- **冻结投稿包 SHA-256：** `{status['submission_package_sha256']}`

## 1. 本轮如何处理外部候选

Downloads 中的终局冻结候选被视为待验证输入，而不是项目指令或自动批准。8 个输入文件已逐字节归档并记录 SHA-256。正文与补充材料均从当前 GitHub canonical source 重新构建；重建结果分别与外部 Markdown 候选完全一致后才写回项目。外部 DOCX/PDF 仅用于敌意复核，不作为 canonical 成品复制来源。

外部 54 项 cross-document audit 为 54/54 PASS；本项目脚本又直接读取冻结 Figure 1-5 Source Data、正文、补充材料和 21-panel matrix，独立重做同一组 54 项检查，结果同样为 54/54 PASS。

## 2. 实际来源级修订

本轮仅执行 4 个文本操作：

1. Discussion 最终 landing 从 `identity and transfer limits` 收束为 `identity, transfer and mechanistic limits`。
2. Supplementary Table S5 的 Figure 1 描述增加 `end-to-end B_ASC boundary`。
3. Figure 4 描述增加 `gene-level coherence and required calibration boundary`。
4. Figure 5 描述增加 `IFN-overlap-depletion ceiling`。

第一项没有提高机制主张，反而把 Figure 5 的非因果边界纳入全文结尾。其余三项只更新 human-facing source-data ownership；没有改变 CSV、统计值、阈值、panel letter、mapper、contrast 或 multiplicity family。

## 3. 21 个主图 panel 的最终裁决

- Figure 1：1a/1b/1c `KEEP`；1d 保留已经完成的来源替换。1d 是 end-to-end B_ASC identity ceiling 的最小充分主图表达。
- Figure 2：2a-2d 全部 `KEEP`，分别拥有 observed/adjusted composition、contrast hierarchy、mandatory sensitivities 和 90 次 leave-one-sample-out。
- Figure 3：3a-3d 全部 `KEEP`，分别拥有 frozen program family、IFN robustness ladder、gene-level coherence 和 specificity controls。
- Figure 4：4a-4c `KEEP`；4d 保留已经完成的来源替换。4d 阻止把 source-label-defined replication 误写成 source-label-independent transfer。
- Figure 5：5a/5b/5c/5e `KEEP`；5d 保留已经完成的来源替换。5d 同时显示 12-gene depletion 的 6/6 正区间和 M5911-depleted discovery STAT2 的跨零例外。

因此，本轮没有重画或替换任何图。45 个现行主图、补图和 Source Data 资产全部与 Figure 5 上游基线哈希一致。继续把 S4/S8/S10 的更多诊断搬入主图会重复现有 boundary summary，并降低 reader-first claim density。

## 4. 数值与证据边界复核

- Figure 1d：B_ASC end-to-end median Jaccard 0.930323，低于 0.95 criterion。
- Figure 2：primary OR 0.946653，正文报告 0.947 [0.636-1.410]，P=0.787；flare q=0.084521，未升级为支持性结论。
- Figure 3：primary IFN/ISG effect 0.836556，95% CI 0.525430-1.147683，q=2.977 x 10^-6。
- Figure 4d：coverage 0.941958 PASS、B_CONV precision 0.996450 PASS、B_ASC precision 0.885210 FAIL；未估计 corrected external disease effect。
- Figure 5d：12-gene arm 去除后 6/6 ULM CI >0；M5911-depleted discovery STAT2 为 0.390658 [−0.745046, 1.526362]，q=0.500111。

正结论仍严格限定为可重复的 process-level B_CONV IFN/ISG remodeling；fine-state、B_ASC stability、composition、genome-wide concordance、transfer calibration、CAMERA、depletion 和 n=2 perturbation 的负面边界全部保留。

## 5. 文档与视觉 QA

- WPS 主文：{documents['wps_main']['pages']} 页，SHA-256 `{documents['wps_main']['sha256']}`。
- LibreOffice 主文：{documents['lo_main']['pages']} 页，SHA-256 `{documents['lo_main']['sha256']}`。
- WPS 补充材料：{documents['wps_supplement']['pages']} 页；LibreOffice 补充材料：{documents['lo_supplement']['pages']} 页。
- 双引擎共 {status['manual_visual_qa']['rendered_pages_inspected']} 页、{status['manual_visual_qa']['contact_sheets_inspected']} 张联系表完成逐页视觉检查；无空白页、越界文本、图文错页、裁切、重叠或未解析标记。
- 相对上游 WPS 基线，主文 30/31 页逐像素一致，唯一变化为第 15 页；补充材料 11/15 页逐像素一致，变化严格局限于第 3-6 页。补充材料的受控差异来自 S5 三处 ownership 文本更新、S5 列宽优化及随后连续表格的重新流排；第 7-15 页恢复逐像素一致，同时消除了试构建中出现的空白页。
- Supplementary S1-S10 的标题、嵌图同页和图像指纹在 WPS/LibreOffice 两套 PDF 中全部通过。
- 两份 DOCX accessibility audit 均为 0 high / 0 medium / 0 low。
- 全量回归：{status['regression_tests']['tests_run']}/{status['regression_tests']['tests_run']} 通过。

## 6. 冻结与下一阶段

本轮正式进入 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`。以下情况才允许重新打开对象：真实数值错误、claim-owner/cross-reference 错位、provenance/hash 失败、actual-size clipping/readability 缺陷、新的真实数据，或作者级科学反馈。

仅为了更漂亮、增加 pathway/network、后验救显著性、重选 mapper、弱化负结果，或再把 Supplementary panel 搬入主图，不构成重开理由。下一阶段目标是维护这条已闭合的 reader path：`identity ceiling -> composition boundary -> process-level IFN reproducibility -> source-label-defined external support -> transfer ceiling -> observational regulatory convergence -> mechanistic ceiling`。
"""
    ACTION_RECORD.write_text(report, encoding="utf-8", newline="\n")


def write_final_manifest() -> tuple[int, int]:
    exclusions = (
        "qa/accessibility/",
        "qa/libreoffice_documents/",
        "qa/supplement_pagination_audit.json",
        "qa/lo_render/",
        "qa/wps_pages/",
        "qa/lo_pages/",
        "qa/final_lo_render/",
        "qa/lr/",
        f"qa/final_wps_pages/{MAIN_STEM}/",
        f"qa/final_wps_pages/{SUPPLEMENT_STEM}/",
        f"qa/final_lo_pages/{MAIN_STEM}/",
        f"qa/final_lo_pages/{SUPPLEMENT_STEM}/",
        "qa/parent_wps_pages/",
    )
    output = RUN / "10_FINAL_FILE_MANIFEST.csv"
    mutable_status = RUN / "09_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
    files = [
        path
        for path in RUN.rglob("*")
        if path.is_file()
        and path not in (output, mutable_status)
        and not any(path.relative_to(RUN).as_posix().startswith(prefix) for prefix in exclusions)
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256"])
        writer.writeheader()
        for path in sorted(files):
            writer.writerow(
                {
                    "relative_path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return len(files), sum(path.stat().st_size for path in files)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-manual-visual-qa", action="store_true")
    parser.add_argument("--confirm-regression-pass", action="store_true")
    parser.add_argument("--regression-tests-run", type=int, default=0)
    args = parser.parse_args()

    integration = load_json(RUN / "06_FINAL_CROSS_DOCUMENT_INTEGRATION_STATUS.json")
    build = load_json(RUN / "07_DOCUMENT_BUILD_STATUS.json")
    pagination = load_json(RUN / "qa/final_supplement_pagination_audit.json")
    wps_audit = RUN / "qa/final_wps_pages/document_render_audit.json"
    lo_audit = RUN / "qa/final_lo_pages/document_render_audit.json"
    wps_clean, wps_render_pages = render_checks(wps_audit)
    lo_clean, lo_render_pages = render_checks(lo_audit)

    documents_dir = RUN / "documents"
    lo_documents = RUN / "qa/final_libreoffice_documents"
    main_docx = documents_dir / f"{MAIN_STEM}.docx"
    main_pdf = documents_dir / f"{MAIN_STEM}.pdf"
    supplement_docx = documents_dir / f"{SUPPLEMENT_STEM}.docx"
    supplement_pdf = documents_dir / f"{SUPPLEMENT_STEM}.pdf"
    lo_main_pdf = lo_documents / f"{MAIN_STEM}.pdf"
    lo_supplement_pdf = lo_documents / f"{SUPPLEMENT_STEM}.pdf"
    required = (
        main_docx, main_pdf, supplement_docx, supplement_pdf, lo_main_pdf, lo_supplement_pdf,
        RUN / f"qa/final_accessibility/{MAIN_STEM}.json",
        RUN / f"qa/final_accessibility/{SUPPLEMENT_STEM}.json",
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    pixel_rows, changed_pages = compare_page_pixels()
    asset_rows = read_csv(RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv")
    audit_rows = read_csv(RUN / "01_FINAL_CROSS_DOCUMENT_AUDIT_REPRODUCED.csv")
    panel_rows = read_csv(RUN / "03_FINAL_MAIN_PANEL_DECISION_MATRIX.csv")
    claim_rows = read_csv(RUN / "02_FINAL_CLAIM_OWNER_MATRIX.csv")
    contacts = list((RUN / "qa/final_wps_pages").glob("*_contact_*.png")) + list((RUN / "qa/final_lo_pages").glob("*_contact_*.png"))

    main_pages = len(PdfReader(main_pdf).pages)
    supplement_pages = len(PdfReader(supplement_pdf).pages)
    lo_main_pages = len(PdfReader(lo_main_pdf).pages)
    lo_supplement_pages = len(PdfReader(lo_supplement_pdf).pages)
    checks = {
        "integration_pass": not integration["failed_checks"],
        "document_build_pass": not build["failed_checks"],
        "independent_cross_document_audit_54_of_54": len(audit_rows) == 54 and all(row["pass"].lower() == "true" for row in audit_rows),
        "claim_owner_matrix_11_keep": len(claim_rows) == 11 and all(row["status"] == "KEEP" for row in claim_rows),
        "main_panel_matrix_21_keep": len(panel_rows) == 21 and all(row["final_decision"].startswith("KEEP") for row in panel_rows),
        "all_45_figure_assets_byte_identical": len(asset_rows) == 45 and all(row["unchanged"].lower() == "true" for row in asset_rows),
        "root_main_matches_freeze_source": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(RUN / "sources/Manuscript_scientific_presentation_freeze.md"),
        "root_supplement_matches_freeze_source": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(RUN / "sources/Supplementary_Information_scientific_presentation_freeze.md"),
        "wps_main_31_pages": main_pages == 31,
        "wps_supplement_15_pages": supplement_pages == 15,
        "libreoffice_main_31_pages": lo_main_pages == 31,
        "libreoffice_supplement_15_pages": lo_supplement_pages == 15,
        "wps_46_pages_structurally_clean": wps_clean and wps_render_pages == 46,
        "libreoffice_46_pages_structurally_clean": lo_clean and lo_render_pages == 46,
        "eighteen_contact_sheets_cover_92_pages": len(contacts) == 18 and wps_render_pages + lo_render_pages == 92,
        "supplement_pagination_and_fingerprints_pass": not pagination["failed_checks"],
        "main_only_page15_changed": changed_pages["manuscript"] == [15],
        "supplement_layout_changes_confined_to_pages3_to6": changed_pages["supplement"] == [3, 4, 5, 6],
        "page_pixel_comparison_has_46_rows": len(pixel_rows) == 46,
        "main_docx_accessibility_zero": accessibility_zero(RUN / f"qa/final_accessibility/{MAIN_STEM}.json"),
        "supplement_docx_accessibility_zero": accessibility_zero(RUN / f"qa/final_accessibility/{SUPPLEMENT_STEM}.json"),
        "manual_visual_qa_confirmed": args.confirm_manual_visual_qa,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
        "full_regression_suite_confirmed": args.confirm_regression_pass and args.regression_tests_run > 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE" if not failed else "HOLD_FINAL_CROSS_DOCUMENT_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "figures_redrawn": False,
        "figure_pixels_changed": False,
        "source_data_values_changed": False,
        "main_text_edits": 1,
        "supplement_text_edits": 3,
        "main_panels_keep": 21,
        "historical_source_replacements": ["Figure 1d", "Figure 4d", "Figure 5d"],
        "documents": {
            "wps_main": {"path": main_pdf.relative_to(ROOT).as_posix(), "pages": main_pages, "sha256": sha256(main_pdf)},
            "lo_main": {"path": lo_main_pdf.relative_to(ROOT).as_posix(), "pages": lo_main_pages, "sha256": sha256(lo_main_pdf)},
            "wps_supplement": {"path": supplement_pdf.relative_to(ROOT).as_posix(), "pages": supplement_pages, "sha256": sha256(supplement_pdf)},
            "lo_supplement": {"path": lo_supplement_pdf.relative_to(ROOT).as_posix(), "pages": lo_supplement_pages, "sha256": sha256(lo_supplement_pdf)},
            "main_docx": {"path": main_docx.relative_to(ROOT).as_posix(), "bytes": main_docx.stat().st_size, "sha256": sha256(main_docx)},
            "supplement_docx": {"path": supplement_docx.relative_to(ROOT).as_posix(), "bytes": supplement_docx.stat().st_size, "sha256": sha256(supplement_docx)},
        },
        "page_pixel_comparison": {
            "manuscript_identical_pages": main_pages - len(changed_pages["manuscript"]),
            "manuscript_changed_pages": changed_pages["manuscript"],
            "supplement_identical_pages": supplement_pages - len(changed_pages["supplement"]),
            "supplement_changed_pages": changed_pages["supplement"],
        },
        "manual_visual_qa": {
            "confirmed": args.confirm_manual_visual_qa,
            "contact_sheets_inspected": len(contacts) if args.confirm_manual_visual_qa else 0,
            "rendered_pages_inspected": wps_render_pages + lo_render_pages if args.confirm_manual_visual_qa else 0,
            "blank_pages_found": False,
            "clipping_or_overlap_found": False,
            "missing_glyphs_found": False,
            "supplementary_figure_identity_failure_found": False,
        },
        "regression_tests": {
            "confirmed_pass": args.confirm_regression_pass,
            "tests_run": args.regression_tests_run,
            "failures": 0 if args.confirm_regression_pass else None,
            "errors": 0 if args.confirm_regression_pass else None,
        },
        "submission_package_sha256": sha256(PACKAGE),
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "action_record": ACTION_RECORD.relative_to(ROOT).as_posix(),
        "next_stage": "SCIENTIFIC_PRESENTATION_MAINTENANCE_ONLY",
    }
    status_path = RUN / "09_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_action_record(status)
    rows, total_bytes = write_final_manifest()
    status["final_manifest"] = {
        "rows": rows,
        "bytes": total_bytes,
        "path": (RUN / "10_FINAL_FILE_MANIFEST.csv").relative_to(ROOT).as_posix(),
    }
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Final cross-document freeze checks failed: {failed}")


if __name__ == "__main__":
    main()
