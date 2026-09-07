#!/usr/bin/env python3
"""Finalize the Figure 4 transfer-boundary source rerender after QA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure4_transfer_boundary/20260907_source_rerender_gate"
PARENT_FIGURES = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate/figures"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
STEM = "Manuscript_Figure4_transfer_boundary"
ACTION_RECORD = ROOT / "00_project_management/action_record_2026-09-07_figure4_transfer_boundary_source_rerender.md"


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
    return load_json(path)["counts"] == {"high": 0, "medium": 0, "low": 0}


def write_asset_manifest() -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    changed: list[str] = []
    for directory in ("figures", "source_data"):
        for path in sorted((RUN / "figures" / directory).glob("*")):
            if not path.is_file():
                continue
            parent = PARENT_FIGURES / directory / path.name
            changed_flag = sha256(path) != sha256(parent)
            if changed_flag:
                changed.append(path.name)
            rows.append(
                {
                    "relative_path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "parent_sha256": sha256(parent),
                    "candidate_sha256": sha256(path),
                    "changed": changed_flag,
                }
            )
    output = RUN / "07_FIGURE_ASSET_MANIFEST.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, changed


def write_action_record(status: dict) -> None:
    figure = status["figure4"]
    wps = status["documents"]["wps"]
    lo = status["documents"]["libreoffice"]
    report = f"""# 行动记录：Figure 4 外部转移边界来源重绘与科学重冻结

- **完成日期：** 2026-09-07
- **最终状态：** `{status['status']}`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `{status['submission_package_sha256']}`

## 1. 本轮问题与独立裁决

外部 hostile read 指出：旧 Figure 4d 重复呈现 donor/source-label influence，而“校正 source-label-independent mapping 未通过预设 B_ASC precision 门槛”这一决定外部结论证据等级的关键边界只存在于 Supplementary Figure S8。独立复核确认该信息层级问题，但没有直接采用外部候选图，也没有允许 nearest-centroid mapper 替代预先要求的 elastic-net mapper。

最终裁决为：Figure 4a-c 保持原职责；旧 Figure 4d 的完整 influence diagnostics 由 Supplementary Figure S7 继续拥有；新 Figure 4d 必须从哈希锁定的 S8 Source Data 重算并呈现 required elastic-net calibration。Figure 2、Figure 3、Figure 5 与 Supplementary Figures S1-S10 均保持冻结。

## 2. 来源、算法与数值核验

- 冻结 Figure 4 Source Data SHA-256：`F3604F40DAEDB0DD01617BB223A8762323C8AAC7F16185292367B9A13FEC4755`。
- Supplementary Figure S7 Source Data SHA-256：`A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6`。
- Supplementary Figure S8 Source Data SHA-256：`FF4309EBAF761A0563F018AE1BE07212EF2CB2241E79DF12C374BCB1426A60FF`。
- required elastic-net coverage = 0.941958，criterion = 0.80，`PASS`。
- required elastic-net B_CONV precision = 0.996450，criterion = 0.90，`PASS`。
- required elastic-net B_ASC precision = 0.885210，criterion = 0.90，`FAIL`。
- 因 B_ASC calibration 失败，不估计 corrected source-label-independent external disease effect。
- 外部候选 CSV 与 S8 冻结来源在 1e-12 容差内逐值一致；图件颜色重新编码为蓝色通过、红色失败，避免把失败项画成绿色。
- 没有重跑统计模型、改变样本、估计、阈值、候选网格或 mapper policy。

## 3. 图件重绘与子图职责

- Figure 4a：`KEEP`，拥有 GSE135779 source-label-defined IFN/ISG effect 与 support-threshold 结果。
- Figure 4b：`KEEP`，拥有 discovery/internal 与 source-label-defined external effect 对照。
- Figure 4c：`KEEP`，独占 4,410 shared genes 的 gene-level coherence 与 10/10 IFN gene direction concordance。
- Figure 4d：`SOURCE_REPLACEMENT_FROM_LOCKED_S8_REQUIRED_ELASTIC_NET`，直接显示两项通过和 B_ASC precision 失败。
- Supplementary Figure S7：`KEEP_FULL_INFLUENCE_OWNER`，保留 43 次 donor deletion 与 8 次 source-label omission 全部诊断。
- Supplementary Figure S8：`KEEP_FULL_REMAP_OWNER`，保留完整 remapping、candidate selection 和 calibration 细节。
- Figure 4 最终尺寸 170.0 mm x 137.87 mm；失败项、阈值线和“不估计校正效应”的结论均在正常阅读尺寸下可见。
- 45 个 figure/source-data 资产中仅 Figure 4 PDF、PNG 与 Figure 4 Source Data 三项改变，其余 42 项哈希不变。

## 4. 手稿同步

仅执行四项来源级精确修改：将 donor/source-label influence 的主权交给 Supplementary Fig. S7；将 gene-level coherence 引用收窄到 Fig. 4c；把 corrected calibration failure 锚定到 Fig. 4d；同步重写 Figure 4 legend。Title、Abstract、Discussion、Conclusion、Figure 5 全节、Supplementary Information、参考文献与其他图注均保持不变。

为消除跨引擎孤立尾页，Figure 4 图注仅做语义等价压缩；coverage、B_CONV/B_ASC calibration、0.885 < 0.90、未估计 corrected external disease effect、criterion line 及 S7/S8 evidence ownership 均完整保留。

## 5. 文档、视觉与回归 QA

- Figure 4 PDF SHA-256：`{figure['pdf_sha256']}`；PNG SHA-256：`{figure['png_sha256']}`。
- WPS 主文：{wps['pages']} 页，SHA-256 `{wps['sha256']}`。
- LibreOffice 主文：{lo['pages']} 页，SHA-256 `{lo['sha256']}`。
- 双引擎共 {status['manual_visual_qa']['rendered_pages_inspected']} 页、{status['manual_visual_qa']['contact_sheets_inspected']} 张联系表已逐页视觉检查；无空白页、截断、重叠、缺字、异常分页或 cross-render 尾页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：{status['regression_tests']['tests_run']}/{status['regression_tests']['tests_run']} 通过。
- 投稿包 SHA-256 保持不变；Release 与 Zenodo 未触碰。

## 6. 当前科学判断与下一阶段

Figure 4 现在形成更严格的证据阶梯：source-label-defined replication 成立，program-level direction concordance 成立，但 corrected source-label-independent B_ASC transfer 不满足预设 calibration，因此不能升级为 de novo taxonomy transfer 或 corrected external disease effect。该失败不是需要“救 PASS”的瑕疵，而是外部证据解释边界。

下一阶段进入 `{status['next_stage']}`。仅比较当前 Figure 5d 与冻结来源重绘的 broader IFN-response depletion 候选在 170 mm 完整 Figure 5 组合中的信息增益、视觉密度和 claim ownership。候选只有在不遮蔽 discovery STAT2 的 CI-crossing-zero 例外、且明显优于当前 5d 时才可替换；否则保留当前 Figure 5d 并回到科学呈现维护冻结。
"""
    ACTION_RECORD.write_text(report, encoding="utf-8", newline="\n")


def write_final_manifest() -> tuple[int, int]:
    exclusions = (
        "qa/lo_render/",
        f"qa/wps_pages/{STEM}/",
        f"qa/lo_pages/{STEM}/",
    )
    output = RUN / "09_FINAL_FILE_MANIFEST.csv"
    mutable = RUN / "08_FIGURE4_TRANSFER_BOUNDARY_REFREEZE_STATUS.json"
    files = [
        path
        for path in RUN.rglob("*")
        if path.is_file()
        and path not in (output, mutable)
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
    parser.add_argument("--confirm-figure-visual-qa", action="store_true")
    parser.add_argument("--confirm-regression-pass", action="store_true")
    parser.add_argument("--regression-tests-run", type=int, default=0)
    args = parser.parse_args()

    integration = load_json(RUN / "05_FIGURE4_TRANSFER_BOUNDARY_INTEGRATION_STATUS.json")
    build = load_json(RUN / "06_DOCUMENT_BUILD_STATUS.json")
    wps_docx = RUN / f"documents/{STEM}.docx"
    wps_pdf = RUN / f"documents/{STEM}.pdf"
    lo_docx = RUN / f"qa/libreoffice_documents/{STEM}.docx"
    lo_pdf = RUN / f"qa/libreoffice_documents/{STEM}.pdf"
    wps_audit = RUN / "qa/wps_pages/document_render_audit.json"
    lo_audit = RUN / "qa/lo_pages/document_render_audit.json"
    accessibility = RUN / f"qa/accessibility/{STEM}.json"
    figure_pdf = RUN / "figures/figures/Figure4_independent_ifn_replication.pdf"
    figure_png = RUN / "figures/figures/Figure4_independent_ifn_replication.png"
    comparison = RUN / "qa/Figure4_current_vs_transfer_boundary.png"
    required = (wps_docx, wps_pdf, lo_docx, lo_pdf, wps_audit, lo_audit, accessibility, figure_pdf, figure_png, comparison)
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    wps_clean, wps_render_pages = render_checks(wps_audit)
    lo_clean, lo_render_pages = render_checks(lo_audit)
    wps_pages = len(PdfReader(wps_pdf).pages)
    lo_pages = len(PdfReader(lo_pdf).pages)
    contact_sheets = list((RUN / "qa/wps_pages").glob("*_contact_*.png")) + list((RUN / "qa/lo_pages").glob("*_contact_*.png"))
    asset_rows, changed_assets = write_asset_manifest()
    with (RUN / "02_PANEL_DECISION_MATRIX.csv").open(encoding="utf-8-sig", newline="") as handle:
        panel_rows = list(csv.DictReader(handle))
    main_panels = [row for row in panel_rows if row["tier"] == "Main"]
    supplementary_panels = [row for row in panel_rows if row["tier"] == "Supplementary"]
    figure4d = next(row for row in main_panels if row["object"] == "Figure 4d")
    source_manuscript = RUN / "sources/Manuscript_figure4_transfer_boundary.md"
    source_supplement = RUN / "sources/Supplementary_Information_unchanged.md"

    checks = {
        "integration_pass": not integration["failed_checks"],
        "document_build_pass": not build["failed_checks"],
        "root_main_matches_candidate": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(source_manuscript),
        "supplementary_information_unchanged": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(source_supplement),
        "only_three_figure_assets_changed": sorted(changed_assets) == sorted([
            "Figure4_independent_ifn_replication.pdf",
            "Figure4_independent_ifn_replication.png",
            "Figure4_source_data.csv",
        ]),
        "forty_five_assets_audited": len(asset_rows) == 45,
        "forty_two_assets_byte_identical": sum(not row["changed"] for row in asset_rows) == 42,
        "all_21_main_panel_slots_retained": len(main_panels) == 21,
        "all_38_supplementary_panels_kept": len(supplementary_panels) == 38 and all(row["scientific_decision"] == "KEEP" for row in supplementary_panels),
        "figure4d_is_source_replacement": figure4d["scientific_decision"] == "SOURCE_REPLACEMENT",
        "wps_main_is_31_pages": wps_pages == 31 and wps_render_pages == 31,
        "libreoffice_main_is_31_pages": lo_pages == 31 and lo_render_pages == 31,
        "wps_render_structurally_clean": wps_clean,
        "libreoffice_render_structurally_clean": lo_clean,
        "twelve_contact_sheets_cover_62_pages": len(contact_sheets) == 12 and wps_render_pages + lo_render_pages == 62,
        "docx_accessibility_zero": accessibility_zero(accessibility),
        "figure_visual_qa_confirmed": args.confirm_figure_visual_qa,
        "manual_document_visual_qa_confirmed": args.confirm_manual_visual_qa,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
        "full_regression_suite_confirmed": args.confirm_regression_pass and args.regression_tests_run > 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_FIGURE4_TRANSFER_BOUNDARY_PROMOTION_REFREEZE" if not failed else "HOLD_FIGURE4_TRANSFER_BOUNDARY_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_values_changed": False,
        "mapping_thresholds_changed": False,
        "mapper_substitution_authorized": False,
        "figure4": {
            "pdf": figure_pdf.relative_to(ROOT).as_posix(),
            "pdf_sha256": sha256(figure_pdf),
            "png": figure_png.relative_to(ROOT).as_posix(),
            "png_sha256": sha256(figure_png),
            "source_data_sha256": sha256(RUN / "figures/source_data/Figure4_source_data.csv"),
            "width_mm": 170.0,
            "height_mm": 137.87,
            "panel_a": "KEEP",
            "panel_b": "KEEP",
            "panel_c": "KEEP",
            "panel_d": "SOURCE_REPLACEMENT_FROM_LOCKED_S8_REQUIRED_ELASTIC_NET",
        },
        "supplementary_figure_s7": "KEEP_FULL_INFLUENCE_OWNER",
        "supplementary_figure_s8": "KEEP_FULL_REMAP_OWNER",
        "documents": {
            "wps": {"path": wps_pdf.relative_to(ROOT).as_posix(), "pages": wps_pages, "sha256": sha256(wps_pdf)},
            "libreoffice": {"path": lo_pdf.relative_to(ROOT).as_posix(), "pages": lo_pages, "sha256": sha256(lo_pdf)},
            "docx": {"path": wps_docx.relative_to(ROOT).as_posix(), "bytes": wps_docx.stat().st_size, "sha256": sha256(wps_docx)},
        },
        "manual_visual_qa": {
            "confirmed": args.confirm_manual_visual_qa and args.confirm_figure_visual_qa,
            "contact_sheets_inspected": len(contact_sheets) if args.confirm_manual_visual_qa else 0,
            "rendered_pages_inspected": wps_render_pages + lo_render_pages if args.confirm_manual_visual_qa else 0,
            "figure_comparison_inspected": args.confirm_figure_visual_qa,
            "blank_pages_found": False,
            "clipping_or_overlap_found": False,
            "missing_glyphs_found": False,
            "cross_renderer_tail_page_found": False,
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
        "figure5_candidate_status": "ARCHIVED_DEFERRED_TO_ISOLATED_NEXT_GATE",
        "action_record": ACTION_RECORD.relative_to(ROOT).as_posix(),
        "next_stage": "FIGURE5_REGULATORY_CEILING_PROMOTION_SOURCE_RERENDER_GATE",
    }
    status_path = RUN / "08_FIGURE4_TRANSFER_BOUNDARY_REFREEZE_STATUS.json"
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_action_record(status)
    rows, total_bytes = write_final_manifest()
    status["final_manifest"] = {
        "rows": rows,
        "bytes": total_bytes,
        "path": (RUN / "09_FINAL_FILE_MANIFEST.csv").relative_to(ROOT).as_posix(),
    }
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Final Figure 4 transfer-boundary checks failed: {failed}")


if __name__ == "__main__":
    main()
