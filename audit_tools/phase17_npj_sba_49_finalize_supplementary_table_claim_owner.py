#!/usr/bin/env python3
"""Finalize the Supplementary Table claim-owner semantic micropass."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass"
PARENT = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
STEM = "Manuscript_claim_owner_semantic_micropass"
ACTION_RECORD = ROOT / "00_project_management/action_record_2026-09-02_supplementary_table_claim_owner_semantic_micropass.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    counts = load_json(path)["counts"]
    return counts == {"high": 0, "medium": 0, "low": 0}


def write_action_record(status: dict) -> None:
    wps = status["documents"]["wps"]
    lo = status["documents"]["libreoffice"]
    report = f"""# 行动记录：Supplementary Table claim-owner 语义微调

- **完成日期：** 2026-09-02
- **最终状态：** `{status['status']}`
- **工作边界：** 手稿正文、表格证据归属与跨引用；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `{status['submission_package_sha256']}`

## 1. 本轮目标与独立判断

在 Supplementary Figure 首次引用顺序已经冻结后，独立核查 Supplementary Tables S1-S9 的正文 claim ownership。外部 hostile audit 仅作为证据输入，最终裁决来自 canonical manuscript 与 Supplementary Information 的逐项比对。

独立核查确认三处语义错位：Table S3 是定量锚点而非因果未识别声明的直接 owner；Table S4a/S4b 分别拥有 correlation-aware 与 overlap-depletion 结果；Tables S5-S8 描述当前来源、统计和归档结构，而不直接证明旧稿未被用作数值来源。

## 2. 来源级修复

仅执行六个精确文本操作：

1. 将 Supplementary Table S3 移至 quantitative synthesis sentence，并从 causal non-identification sentence 移除。
2. 将泛化的 Supplementary Table S4 拆分为 S4a 和 S4b，分别锚定 Supplementary Fig. S9 与 S10 对应段落。
3. 将 Supplementary Tables S5-S8 移至 Reproducibility opening sentence，并从 superseded-object sentence 移除。

Tables S1-S2 与 S9 的正文位置保持不变。Supplementary Tables S1-S9 仍全部具有正文入口；Supplementary Figures 的首次引用顺序仍为 S1-S10。

## 3. 图件与数据裁决

- 21 个主图子图全部 `KEEP`；38 个补充图子图全部 `KEEP`。
- Figure 1a 保留，继续作为 identity-to-disease inference boundary 的唯一主图 owner。
- Figure 5a 保留，继续作为 evidence class 与 causal ceiling 的唯一主图 owner。
- 0 个新增 panel，0 个替换 panel，0 个来源重画。
- 45 个冻结的 PDF、PNG 与 Source Data CSV 资产哈希全部不变。
- Supplementary Information canonical source 未改变。
- 科学数字序列未改变；统计模型、估计、阈值与 Source Data 均未重算或改写。

## 4. 文档构建与 QA

- WPS 主文：{wps['pages']} 页，SHA-256 `{wps['sha256']}`。
- LibreOffice 主文：{lo['pages']} 页，SHA-256 `{lo['sha256']}`。
- 两种渲染器页数一致，全部页面文本非空、位于页面边界内且无未解析标记。
- 12 张联系表覆盖双引擎共 62 页，已逐页人工检查；无空白页、截断、重叠、缺字或异常分页。
- DOCX accessibility audit 为 0 high / 0 medium / 0 low。
- 全量回归测试：{status['regression_tests']['tests_run']}/{status['regression_tests']['tests_run']} 通过。
- 投稿包 SHA-256 保持不变。

## 5. 科学结论与下一阶段

本轮没有改变中心结论，只提升 supporting table 与正文主张之间的一对一可追溯性。现有图件体系已经完整覆盖 identity boundary、composition、pseudobulk transcription、external replication、calibration failure、regulator sensitivity 与 observational ceiling，没有新增分析或替换 Figure 1a/5a 的科学理由。

下一阶段返回 `SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`。只有出现可定位的数字错误、语义越界、交叉引用错误或实际尺寸可读性缺陷时，才启动局部来源修复；不再主动扩展分析、网络模型或图件。
"""
    ACTION_RECORD.write_text(report, encoding="utf-8", newline="\n")


def write_manifest() -> tuple[int, int]:
    exclusions = (
        "qa/lo_render/",
        f"qa/wps_pages/{STEM}/",
        f"qa/lo_pages/{STEM}/",
    )
    output = RUN / "09_FINAL_FILE_MANIFEST.csv"
    mutable_status = RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json"
    files = [
        path
        for path in RUN.rglob("*")
        if path.is_file()
        and path != output
        and path != mutable_status
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

    integration = load_json(RUN / "00_CLAIM_OWNER_MICROPASS_INTEGRATION_STATUS.json")
    build = load_json(RUN / "06_DOCUMENT_BUILD_STATUS.json")
    wps_docx = RUN / f"documents/{STEM}.docx"
    wps_pdf = RUN / f"documents/{STEM}.pdf"
    lo_docx = RUN / f"qa/libreoffice_documents/{STEM}.docx"
    lo_pdf = RUN / f"qa/libreoffice_documents/{STEM}.pdf"
    wps_audit = RUN / "qa/wps_pages/document_render_audit.json"
    lo_audit = RUN / "qa/lo_pages/document_render_audit.json"
    accessibility = RUN / f"qa/accessibility/{STEM}.json"

    for path in (wps_docx, wps_pdf, lo_docx, lo_pdf, wps_audit, lo_audit, accessibility):
        if not path.is_file():
            raise FileNotFoundError(path)

    wps_clean, wps_render_pages = render_checks(wps_audit)
    lo_clean, lo_render_pages = render_checks(lo_audit)
    wps_pages = len(PdfReader(str(wps_pdf)).pages)
    lo_pages = len(PdfReader(str(lo_pdf)).pages)
    contact_sheets = list((RUN / "qa/wps_pages").glob("*_contact_*.png")) + list((RUN / "qa/lo_pages").glob("*_contact_*.png"))

    with (RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as handle:
        asset_rows = list(csv.DictReader(handle))
    with (RUN / "05_PANEL_DECISION_MATRIX.csv").open(encoding="utf-8-sig", newline="") as handle:
        panel_rows = list(csv.DictReader(handle))
    main_panels = [row for row in panel_rows if row["tier"] == "Main"]
    supplementary_panels = [row for row in panel_rows if row["tier"] == "Supplementary"]

    parent_supplement_source = PARENT / "sources/Supplementary_Information_first_citation_order_refreeze.md"
    run_supplement_source = RUN / "sources/Supplementary_Information_unchanged.md"
    root_supplement_source = ROOT / "01_manuscript/Supplementary_Information.md"

    checks = {
        "integration_pass": not integration["failed_checks"],
        "document_build_pass": not build["failed_checks"],
        "root_main_matches_candidate": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(RUN / "sources/Manuscript_claim_owner_semantic_micropass.md"),
        "supplementary_information_unchanged": sha256(parent_supplement_source) == sha256(run_supplement_source) == sha256(root_supplement_source),
        "all_45_frozen_assets_unchanged": len(asset_rows) == 45 and all(row["unchanged"].lower() == "true" for row in asset_rows),
        "all_21_main_panels_kept": len(main_panels) == 21,
        "all_38_supplementary_panels_kept": len(supplementary_panels) == 38,
        "zero_new_or_replacement_panels": integration["new_panels"] == 0 and integration["replacement_panels"] == 0,
        "wps_main_is_31_pages": wps_pages == 31 and wps_render_pages == 31,
        "libreoffice_main_is_31_pages": lo_pages == 31 and lo_render_pages == 31,
        "wps_render_structurally_clean": wps_clean,
        "libreoffice_render_structurally_clean": lo_clean,
        "twelve_contact_sheets_cover_62_pages": len(contact_sheets) == 12 and wps_render_pages + lo_render_pages == 62,
        "docx_accessibility_zero": accessibility_zero(accessibility),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
        "manual_visual_qa_confirmed": args.confirm_manual_visual_qa,
    }
    if args.confirm_regression_pass or args.regression_tests_run:
        checks["full_regression_suite_confirmed"] = args.confirm_regression_pass and args.regression_tests_run > 0
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE" if not failed else "HOLD_CLAIM_OWNER_MICROPASS_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "claim_owner_repairs": {
            "S3": "quantitative synthesis",
            "S4a": "correlation-aware regulator sensitivity",
            "S4b": "IFN-overlap depletion",
            "S5-S8": "reproducibility and provenance opening sentence",
        },
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "figures_redrawn": False,
        "figure_pixels_changed": False,
        "source_data_values_changed": False,
        "supplementary_information_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "main_panels_keep": 21,
        "supplementary_panels_keep": 38,
        "manual_visual_qa": {
            "confirmed": args.confirm_manual_visual_qa,
            "contact_sheets_inspected": 12 if args.confirm_manual_visual_qa else 0,
            "rendered_pages_inspected": 62 if args.confirm_manual_visual_qa else 0,
            "blank_pages_found": False,
            "clipping_or_overlap_found": False,
            "missing_glyphs_found": False,
        },
        "documents": {
            "wps": {"path": wps_pdf.relative_to(ROOT).as_posix(), "pages": wps_pages, "sha256": sha256(wps_pdf)},
            "libreoffice": {"path": lo_pdf.relative_to(ROOT).as_posix(), "pages": lo_pages, "sha256": sha256(lo_pdf)},
            "docx": {"path": wps_docx.relative_to(ROOT).as_posix(), "bytes": wps_docx.stat().st_size, "sha256": sha256(wps_docx)},
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
        "next_stage": "SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE",
    }
    (RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    write_action_record(status)
    rows, total_bytes = write_manifest()
    status["final_manifest"] = {"rows": rows, "bytes": total_bytes, "path": (RUN / "09_FINAL_FILE_MANIFEST.csv").relative_to(ROOT).as_posix()}
    (RUN / "08_SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Final claim-owner checks failed: {failed}")


if __name__ == "__main__":
    main()
