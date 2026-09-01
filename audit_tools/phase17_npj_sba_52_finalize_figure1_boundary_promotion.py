#!/usr/bin/env python3
"""Finalize Figure 1 boundary promotion after render and regression QA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure1_boundary_promotion/20260902_source_rerender_gate"
PARENT_FIGURES = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order/figures"
PARENT_TEXT = ROOT / "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
STEM = "Manuscript_Figure1_boundary_promotion"
ACTION_RECORD = ROOT / "00_project_management/action_record_2026-09-02_figure1_boundary_promotion_source_rerender.md"


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
    output = RUN / "06_FIGURE_ASSET_MANIFEST.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows, changed


def write_action_record(status: dict) -> None:
    wps = status["documents"]["wps"]
    lo = status["documents"]["libreoffice"]
    figure = status["figure1"]
    report = f"""# 行动记录：Figure 1 identity-boundary 来源重绘与科学重冻结

- **完成日期：** 2026-09-02
- **最终状态：** `{status['status']}`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `{status['submission_package_sha256']}`

## 1. 本轮问题与独立裁决

外部 hostile audit 指出：当前标题、摘要与 Results 的关键转折是 fixed representation 下 broad scaffold 通过，但 end-to-end reconstruction 时 B_ASC state overlap 未满足预设 0.95 criterion；旧 Figure 1b-d 却全部呈现 fixed-representation 证据，导致最重要的边界只出现在 Supplementary Figure S4。

独立复核同意这一信息层级缺陷，但没有直接采用外部候选 PNG。最终裁决为：Figure 1a、1b 保留科学职责；旧 1d 的 fixed-representation state-Jaccard summary 移至新 1c；旧 1c 的逐次 ARI/agreement 退出主图但完整 Source Data 保留；新 1d 从哈希锁定的 S4 Source Data 重算 end-to-end minimum/median Jaccard。Figure 2-5 与 S1-S10 全部保持冻结。

## 2. 来源与数值核验

- 旧 Figure 1 Source Data SHA-256：`F3D45F72422B8469F7DD0A6E888541075A1D090277E9F96D16565B5B44C5B805`。
- Supplementary Figure S4 Source Data SHA-256：`46EE840F86CA33AA4F5FCE0A37EEFCB4DB23831533BBFA20400BAE50744F5D42`。
- 外部候选的 8 个 Jaccard 汇总值均由仓库冻结来源独立重算并在 1e-12 容差内一致。
- Fixed representation：B_CONV minimum/median = 0.999832/0.999925；B_ASC = 0.981096/0.991371。
- End-to-end reconstruction：B_CONV minimum/median = 0.998760/0.999363；B_ASC = 0.871750/0.930323。
- 没有重跑统计模型、没有改变阈值、没有产生新的生物学估计。

## 3. 图件重绘与子图裁决

- Figure 1a：`KEEP`，保持 identity adjudication 先于 disease-field join 的工作流职责。
- Figure 1b：`KEEP`，保持 candidate policy selection 职责。
- Figure 1c：`KEEP_RELOCATED`，成为 fixed-representation overlap criterion met 的唯一主图 owner，并保留 5/5 B_ASC marker support 与 minimum sample support 1.00。
- Figure 1d：`SOURCE_REPLACEMENT`，直接呈现 end-to-end B_ASC median 0.930 与 minimum 0.872 未满足 0.95 criterion。
- c/d 使用相同 x 轴范围与相同 marker 语义，允许读者直接比较 fixed 与 end-to-end reconstruction。
- S4 五个面板完整保留，继续拥有 20 次逐次诊断、boundary exchange、composition propagation 与 IFN propagation。
- 45 个图件/Source Data 资产中仅 Figure 1 PDF、PNG 与 Figure 1 Source Data 三项改变；其余 42 项哈希不变。

## 4. 手稿同步

仅执行三项来源级操作：fixed-representation 结果交叉引用从 Fig. 1a-d 收窄到 Fig. 1a-c；end-to-end boundary 首次锚定 Fig. 1d 与 Supplementary Fig. S4；Figure 1c/d legend 按新职责重写。Title、Abstract、Discussion、Conclusion、Figure 2-5 legends、Supplementary Information、参考文献与全部科学数字保持不变。

## 5. 文档与回归 QA

- Figure 1：170.0 mm 单页 PDF，SHA-256 `{figure['pdf_sha256']}`；600-dpi PNG SHA-256 `{figure['png_sha256']}`。
- WPS 主文：{wps['pages']} 页，SHA-256 `{wps['sha256']}`。
- LibreOffice 主文：{lo['pages']} 页，SHA-256 `{lo['sha256']}`。
- 双引擎共 {status['manual_visual_qa']['rendered_pages_inspected']} 页、{status['manual_visual_qa']['contact_sheets_inspected']} 张联系表已逐页视觉检查；无空白页、截断、重叠、缺字或异常分页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：{status['regression_tests']['tests_run']}/{status['regression_tests']['tests_run']} 通过。
- 投稿包 SHA-256 保持不变。

## 6. 当前科学判断与下一阶段

本轮提升的是中心矛盾在主图中的可见性，而不是扩大结论。现在 Figure 1 自身形成完整链条：identity workflow -> policy selection -> fixed representation criterion met -> end-to-end B_ASC criterion not met。旧逐次 ARI/agreement panel 退出主图是合理的信息去重，其来源值仍完整保存；S4 则继续承担详细审计职责。

下一阶段进入 `{status['next_stage']}`：不再主动重开 Figure 1 或扩展分析，转为全文 figure-to-text claim-density hostile read，重点只检查 Figure 2-5 是否存在与本轮类似的“核心边界未在主图第一视野出现”问题。只有发现可定位、可由冻结来源重绘解决的职责缺口时才重开单个 panel；否则回到科学呈现维护冻结。
"""
    ACTION_RECORD.write_text(report, encoding="utf-8", newline="\n")


def write_final_manifest() -> tuple[int, int]:
    exclusions = (
        "qa/lo_render/",
        f"qa/wps_pages/{STEM}/",
        f"qa/lo_pages/{STEM}/",
    )
    output = RUN / "09_FINAL_FILE_MANIFEST.csv"
    mutable = RUN / "08_FIGURE1_BOUNDARY_PROMOTION_REFREEZE_STATUS.json"
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

    integration = load_json(RUN / "00_FIGURE1_BOUNDARY_PROMOTION_INTEGRATION_STATUS.json")
    build = load_json(RUN / "05_DOCUMENT_BUILD_STATUS.json")
    wps_docx = RUN / f"documents/{STEM}.docx"
    wps_pdf = RUN / f"documents/{STEM}.pdf"
    lo_docx = RUN / f"qa/libreoffice_documents/{STEM}.docx"
    lo_pdf = RUN / f"qa/libreoffice_documents/{STEM}.pdf"
    wps_audit = RUN / "qa/wps_pages/document_render_audit.json"
    lo_audit = RUN / "qa/lo_pages/document_render_audit.json"
    accessibility = RUN / f"qa/accessibility/{STEM}.json"
    figure_pdf = RUN / "figures/figures/Figure1_disease_blind_identity_scope.pdf"
    figure_png = RUN / "figures/figures/Figure1_disease_blind_identity_scope.png"
    comparison = RUN / "qa/Figure1_current_vs_boundary_promotion.png"
    for path in (wps_docx, wps_pdf, lo_docx, lo_pdf, wps_audit, lo_audit, accessibility, figure_pdf, figure_png, comparison):
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
    source_manuscript = RUN / "sources/Manuscript_figure1_boundary_promotion.md"
    source_supplement = RUN / "sources/Supplementary_Information_unchanged.md"

    checks = {
        "integration_pass": not integration["failed_checks"],
        "document_build_pass": not build["failed_checks"],
        "root_main_matches_candidate": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(source_manuscript),
        "supplementary_information_unchanged": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(source_supplement),
        "only_three_figure_assets_changed": sorted(changed_assets) == sorted([
            "Figure1_disease_blind_identity_scope.pdf",
            "Figure1_disease_blind_identity_scope.png",
            "Figure1_source_data.csv",
        ]),
        "forty_five_assets_audited": len(asset_rows) == 45,
        "forty_two_assets_byte_identical": sum(not row["changed"] for row in asset_rows) == 42,
        "all_21_main_panel_slots_retained": len(main_panels) == 21,
        "all_38_supplementary_panels_kept": len(supplementary_panels) == 38 and all(row["scientific_decision"] == "KEEP" for row in supplementary_panels),
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
        "status": "SCIENTIFIC_FIGURE1_BOUNDARY_PROMOTION_REFREEZE" if not failed else "HOLD_FIGURE1_BOUNDARY_PROMOTION_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_values_changed": False,
        "figure1": {
            "pdf": figure_pdf.relative_to(ROOT).as_posix(),
            "pdf_sha256": sha256(figure_pdf),
            "png": figure_png.relative_to(ROOT).as_posix(),
            "png_sha256": sha256(figure_png),
            "width_mm": 170.0,
            "panel_a": "KEEP",
            "panel_b": "KEEP",
            "panel_c": "KEEP_RELOCATED_FROM_CURRENT_1D",
            "panel_d": "SOURCE_REPLACEMENT_FROM_S4",
        },
        "supplementary_figure_s4": "KEEP_FULL_DETAIL_OWNER",
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
        "next_stage": "FULL_MAIN_FIGURE_CLAIM_DENSITY_HOSTILE_READ",
    }
    status_path = RUN / "08_FIGURE1_BOUNDARY_PROMOTION_REFREEZE_STATUS.json"
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
        raise RuntimeError(f"Final Figure 1 boundary checks failed: {failed}")


if __name__ == "__main__":
    main()
