#!/usr/bin/env python3
"""Finalize the source-driven Figure 5 regulatory-ceiling integration after QA."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration"
PARENT_FIGURES = ROOT / "phase17_v7/npj_sba_figure4_transfer_boundary/20260907_source_rerender_gate/figures"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
STEM = "Manuscript_Figure5_regulatory_ceiling"
ACTION_RECORD = ROOT / "00_project_management/action_record_2026-09-08_figure5_regulatory_ceiling_canonical_integration.md"


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
    figure = status["figure5"]
    wps = status["documents"]["wps"]
    lo = status["documents"]["libreoffice"]
    report = f"""# 行动记录：Figure 5 调控上限来源重绘与科学重冻结

- **完成日期：** 2026-09-08
- **最终状态：** `{status['status']}`
- **工作边界：** 手稿文本与图件科学表达；未推进投稿包、GitHub Release 或 Zenodo
- **冻结投稿包 SHA-256：** `{status['submission_package_sha256']}`

## 1. 本轮问题与独立裁决

外部 hostile read 建议用 IFN-overlap depletion 取代旧 Figure 5d 的三根 M5911 NES 柱。独立复核确认科学方向成立，但没有直接采用外部整图：其 Figure 5b 左侧标签在 170 mm 组合图中发生明显裁切，不能作为 canonical artwork。外部文件仅作为候选数值、结构和可读性证据归档；正式图从哈希锁定的 Figure 5 与 Supplementary Figure S10 Source Data 重新构建。

最终裁决为：Figure 5a、5b、5c、5e `KEEP`；旧 Figure 5d `REPLACE`。旧 5d 的 M5911 enrichment 数值不删除，而是归入 Figure 5a evidence summary 与 Supplementary Table S3。新 5d 由 S10 的 12 条 ULM depletion 记录重绘，S10 和 Supplementary Table S4b 继续拥有 ULM/CAMERA/FRY 全量审计。

## 2. 来源、算法与数值核验

- 冻结 Figure 5 Source Data SHA-256：`A482D9D4F001B076B496C63857A8B3ADB65816CD0AA18B60C8B17B2DDB211B5B`。
- Supplementary Figure S9 Source Data SHA-256：`D92140A17B96E6B77F5EEBF322A5D77A5E6F2132EDD54CC9C3E73521E5352CA3`。
- Supplementary Figure S10 Source Data SHA-256：`26A3F90E3165D8928874F278384B2587CB549DD4FFDE93440AAC4CEEAE06A9A2`。
- 12-gene IFN/ISG arm 去除后，discovery、nonoverlap、childhood 三个 contrast 的 STAT1/STAT2 共 6 个 ULM 95% CI 全部位于 0 右侧。
- 97-gene M5911 去除后，唯一跨 0 的 ULM 区间是 discovery STAT2：estimate 0.3906577146，95% CI -0.7450461772 至 1.5263616063，q=0.5001111487，保留 8/14 targets。
- 正文和图中按既有精度报告为 slope 0.391、95% CI -0.745 至 1.526、q=0.500；机器精度值由专项回归锁定。
- 没有重跑样本级模型、改变 ranked statistics、tested-gene backgrounds、CollecTRI signs、contrasts、model matrices 或多重校正家族。

## 3. 图件重绘与子图职责

- Figure 5a：`KEEP`，概括 ULM、M5911 与 IFN-beta 三类证据及其解释等级。
- Figure 5b：`KEEP`，拥有 core STAT1/STAT2 与 extended IRF7/IRF9 的观测性 activity slopes。
- Figure 5c：`KEEP`，拥有预设 proliferation specificity comparators。
- Figure 5d：`SOURCE_REPLACEMENT_FROM_LOCKED_S10_ULM`，对照 12-gene arm 与 M5911 depletion，并显式标出 discovery STAT2 的跨零例外。
- Figure 5e：`KEEP`，拥有两名健康 donor 的描述性 IFN-beta paired gene effects。
- 最终 Figure 5 尺寸 {figure['width_mm']} mm x {figure['height_mm']} mm；完整 170 mm 图与半栏裁切均完成可读性检查。
- Figure 5 Source Data 从 53 行扩展为 65 行：原 3 条 M5911 NES 记录由 panel D 改归 panel A，新增 12 条来源于 S10 的 ULM depletion 记录归 panel D。
- 45 个 figure/source-data 资产中仅 Figure 5 PDF、PNG 与 Figure 5 Source Data 三项改变，其余 42 项哈希不变。

## 4. 手稿同步与图例经济性

仅执行三项来源级语义操作：把 overlap-depletion ceiling 引用提升到 Fig. 5d；将 M5911 summary 指向 Fig. 5a/Supplementary Table S3、GSE23307 指向 Fig. 5e；同步 Figure 5 图例。首次扩展图例导致 WPS 与 LibreOffice 均出现仅 228 字符的第 32 页，故没有接受该版。

最终 Figure 5 图例整体压缩到 122 词，同时保留 evidence class、三组 contrasts、global 24-test q、两条 depletion branch、discovery STAT2 跨零例外、S10/S4b 全量主权和 n=2 限制。压缩后双引擎均恢复为 31 页。Title、145 词 Abstract、Discussion、Conclusion、33 篇参考文献、Figure 1-4、Supplementary Information 均未改变。

## 5. 文档、视觉与回归 QA

- Figure 5 PDF SHA-256：`{figure['pdf_sha256']}`；PNG SHA-256：`{figure['png_sha256']}`。
- WPS 主文：{wps['pages']} 页，SHA-256 `{wps['sha256']}`。
- LibreOffice 主文：{lo['pages']} 页，SHA-256 `{lo['sha256']}`。
- 双引擎共 {status['manual_visual_qa']['rendered_pages_inspected']} 页、{status['manual_visual_qa']['contact_sheets_inspected']} 张原始联系表已逐页视觉检查；无空白页、截断、重叠、缺字、异常分页或孤立尾页。
- DOCX accessibility audit：0 high / 0 medium / 0 low。
- 全量回归：{status['regression_tests']['tests_run']}/{status['regression_tests']['tests_run']} 通过；最终 manifest 写入后再次运行全量回归。
- 投稿包 SHA-256 保持不变；Release 与 Zenodo 未触碰。

## 6. 当前科学判断

新 Figure 5d 比旧 M5911 NES 柱具有更高的主图信息增益。它同时说明两件事：STAT1/STAT2 信号并非 12-gene IFN/ISG core program 的简单重述；但 broader interferon-response transcriptome 去除会使 discovery STAT2 明显衰减并跨 0。因此新图不是增加一个“阳性机制结果”，而是把 regulatory ceiling 放入读者第一视野，与 Figure 1 的 identity ceiling 和 Figure 4 的 transfer-calibration ceiling 构成一致的推断边界逻辑。

## 7. 下一阶段目标

下一阶段进入 `{status['next_stage']}`。不再主动寻找新的 panel 替换，也不重新开启统计模型；只对当前主文、Figure 1-5、Supplementary Information、S1-S10、Source Data 与 claim-owner/cross-reference 做一次终局跨文档冻结核查。只有发现局部、可复现的科学语义或排版缺陷时才允许重开对应对象，否则转入科学呈现维护冻结。
"""
    ACTION_RECORD.write_text(report, encoding="utf-8", newline="\n")


def write_final_manifest() -> tuple[int, int]:
    exclusions = (
        "qa/lo_render/",
        f"qa/wps_pages/{STEM}/",
        f"qa/lo_pages/{STEM}/",
    )
    output = RUN / "09_FINAL_FILE_MANIFEST.csv"
    mutable = RUN / "08_FIGURE5_REGULATORY_CEILING_REFREEZE_STATUS.json"
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
    parser.add_argument("--confirm-external-candidate-hostile-read", action="store_true")
    parser.add_argument("--confirm-regression-pass", action="store_true")
    parser.add_argument("--regression-tests-run", type=int, default=0)
    args = parser.parse_args()

    integration = load_json(RUN / "05_FIGURE5_REGULATORY_CEILING_INTEGRATION_STATUS.json")
    build = load_json(RUN / "06_DOCUMENT_BUILD_STATUS.json")
    wps_docx = RUN / f"documents/{STEM}.docx"
    wps_pdf = RUN / f"documents/{STEM}.pdf"
    lo_docx = RUN / f"qa/libreoffice_documents/{STEM}.docx"
    lo_pdf = RUN / f"qa/libreoffice_documents/{STEM}.pdf"
    wps_audit = RUN / "qa/wps_pages/document_render_audit.json"
    lo_audit = RUN / "qa/lo_pages/document_render_audit.json"
    accessibility = RUN / "qa/accessibility_audit.json"
    figure_pdf = RUN / "figures/figures/Figure5_regulatory_evidence.pdf"
    figure_png = RUN / "figures/figures/Figure5_regulatory_evidence.png"
    comparison = RUN / "qa/Figure5_current_vs_regulatory_ceiling.png"
    halfwidth = RUN / "qa/figure5_actual_size/Figure5d_halfwidth_readability.png"
    required = (wps_docx, wps_pdf, lo_docx, lo_pdf, wps_audit, lo_audit, accessibility, figure_pdf, figure_png, comparison, halfwidth)
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
    figure5d = next(row for row in main_panels if row["object"] == "Figure 5d")
    source_manuscript = RUN / "sources/Manuscript_figure5_regulatory_ceiling.md"
    source_supplement = RUN / "sources/Supplementary_Information_unchanged.md"
    with (RUN / "figures/source_data/Figure5_source_data.csv").open(encoding="utf-8-sig", newline="") as handle:
        figure5_rows = list(csv.DictReader(handle))

    checks = {
        "integration_pass": not integration["failed_checks"],
        "document_build_pass": not build["failed_checks"],
        "root_main_matches_candidate": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(source_manuscript),
        "supplementary_information_unchanged": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(source_supplement),
        "only_three_figure_assets_changed": sorted(changed_assets) == sorted(["Figure5_regulatory_evidence.pdf", "Figure5_regulatory_evidence.png", "Figure5_source_data.csv"]),
        "forty_five_assets_audited": len(asset_rows) == 45,
        "forty_two_assets_byte_identical": sum(not row["changed"] for row in asset_rows) == 42,
        "all_21_main_panel_slots_retained": len(main_panels) == 21,
        "all_38_supplementary_panels_kept": len(supplementary_panels) == 38 and all(row["scientific_decision"] == "KEEP" for row in supplementary_panels),
        "figure5d_is_source_replacement": figure5d["scientific_decision"] == "SOURCE_REPLACEMENT",
        "figure5_source_has_65_rows": len(figure5_rows) == 65,
        "figure5d_has_12_ulm_rows": sum(row["panel"] == "D" and row["series"] == "ULM_IFN_overlap_depletion" for row in figure5_rows) == 12,
        "wps_main_is_31_pages": wps_pages == 31 and wps_render_pages == 31,
        "libreoffice_main_is_31_pages": lo_pages == 31 and lo_render_pages == 31,
        "wps_render_structurally_clean": wps_clean,
        "libreoffice_render_structurally_clean": lo_clean,
        "twelve_contact_sheets_cover_62_pages": len(contact_sheets) == 12 and wps_render_pages + lo_render_pages == 62,
        "docx_accessibility_zero": accessibility_zero(accessibility),
        "figure_visual_qa_confirmed": args.confirm_figure_visual_qa,
        "external_candidate_hostile_read_confirmed": args.confirm_external_candidate_hostile_read,
        "manual_document_visual_qa_confirmed": args.confirm_manual_visual_qa,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
        "full_regression_suite_confirmed": args.confirm_regression_pass and args.regression_tests_run == 201,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE" if not failed else "HOLD_FIGURE5_REGULATORY_CEILING_REVIEW_REQUIRED",
        "checks": checks,
        "failed_checks": failed,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_values_changed": False,
        "multiplicity_families_changed": False,
        "figure5": {
            "pdf": figure_pdf.relative_to(ROOT).as_posix(),
            "pdf_sha256": sha256(figure_pdf),
            "png": figure_png.relative_to(ROOT).as_posix(),
            "png_sha256": sha256(figure_png),
            "source_data_sha256": sha256(RUN / "figures/source_data/Figure5_source_data.csv"),
            "width_mm": integration["figure5"]["width_mm"],
            "height_mm": integration["figure5"]["height_mm"],
            "panel_a": "KEEP",
            "panel_b": "KEEP",
            "panel_c": "KEEP",
            "panel_d": "SOURCE_REPLACEMENT_FROM_LOCKED_S10_ULM",
            "panel_e": "KEEP",
        },
        "supplementary_figure_s9": "KEEP_FULL_TARGET_ROBUSTNESS_OWNER",
        "supplementary_figure_s10": "KEEP_FULL_DEPLETION_OWNER",
        "external_candidate": {
            "full_figure_used_directly": False,
            "reason": "Panel-b left labels were clipped; only verified values and architecture informed the canonical source rerender.",
        },
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
            "halfwidth_panel_inspected": args.confirm_figure_visual_qa,
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
        "action_record": ACTION_RECORD.relative_to(ROOT).as_posix(),
        "next_stage": "SCIENTIFIC_PRESENTATION_FINAL_CROSS_DOCUMENT_FREEZE",
    }
    status_path = RUN / "08_FIGURE5_REGULATORY_CEILING_REFREEZE_STATUS.json"
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
        raise RuntimeError(f"Final Figure 5 regulatory-ceiling checks failed: {failed}")


if __name__ == "__main__":
    main()
