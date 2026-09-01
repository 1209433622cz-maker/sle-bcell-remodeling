#!/usr/bin/env python3
"""Synchronize canonical sources and perform the title-only S4 semantic redraw."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops
from pypdf import PdfReader

import phase17_c8s_01_build_supplementary_figures as supplementary_figures


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "phase17_v7/npj_sba_integrated_reader_refreeze/"
    "20260901_s3_s5_reader_path_refreeze"
)
RUN = (
    ROOT
    / "phase17_v7/npj_sba_scientific_stop_gate/"
    "20260901_canonical_source_s4b_refreeze"
)
RECEIVED = ROOT / "00_project_management/scientific_stop_gate_2026-09-01/received"
ROOT_MANUSCRIPT = ROOT / "01_manuscript/Manuscript.md"
ROOT_SUPPLEMENT = ROOT / "01_manuscript/Supplementary_Information.md"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
S4_NAME = "Supplementary_Figure_S4_composition_diagnostics"
S4_SOURCE = "Supplementary_Figure_S4_source_data.csv"
S4_SOURCE_SHA256 = "7BA2660E5A50ADCF28407BCC92A91C791576DD69A9A1ABA9618DEB045C3A4E19"
OLD_S4_TITLE = "Primary null is stable to covariance and cell policy"
NEW_S4_TITLE = "B_ASC estimate across covariance and cell policies"
OLD_CHILDHOOD = (
    "The childhood analysis included 43 donors (11 controls and 32 SLE) with at least "
    "50 mapped cells per donor."
)
NEW_CHILDHOOD = (
    "The childhood analysis included 43 donors (11 controls and 32 SLE) with at least "
    "50 eligible cells in the source-label-defined broad-B analogue per donor."
)
OLD_TABLE_TITLE = "## Supplementary Table S5 | Main-figure source-data map"
NEW_TABLE_TITLE = "## Supplementary Table S5 | Selected figure source-data map"
INPUTS = {
    "FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE_AUDIT_2026-09-01.md": Path(
        r"C:\Users\Administrator\Downloads\FINAL_TEXT_FIGURE_CROSS_REFERENCE_AND_SEMANTIC_STOP_GATE_AUDIT_2026-09-01.md"
    ),
    "LOCALIZED_PATCH_SPEC_2026-09-01.md": Path(
        r"C:\Users\Administrator\Downloads\LOCALIZED_PATCH_SPEC_2026-09-01.md"
    ),
    "pasted_stop_gate_review_2026-09-01.txt": Path(
        r"C:\Users\Administrator\.codex\attachments\716f3364-5c03-48c3-a349-7e5a993ebaed\pasted-text.txt"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    phase17 = (ROOT / "phase17_v7").resolve()
    if not resolved.is_relative_to(phase17):
        raise RuntimeError(f"Refusing to reset outside phase17_v7: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}; observed {count}")
    return text.replace(old, new, 1)


def normalized(value: str) -> str:
    return " ".join(value.split())


def archive_received_inputs() -> dict[str, dict[str, object]]:
    RECEIVED.mkdir(parents=True, exist_ok=True)
    archived: dict[str, dict[str, object]] = {}
    for name, source in INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = RECEIVED / name
        shutil.copy2(source, target)
        archived[name] = {
            "source": str(source),
            "archived": target.relative_to(ROOT).as_posix(),
            "bytes": target.stat().st_size,
            "sha256": sha256(target),
            "byte_identical": sha256(source) == sha256(target),
        }
    return archived


def synchronize_sources() -> tuple[Path, Path, dict[str, object]]:
    source_dir = RUN / "sources"
    source_dir.mkdir(parents=True)
    base_main = BASE / "sources/Manuscript_integrated_reader_refreeze.md"
    base_supp = BASE / "sources/Supplementary_Information_integrated_reader_refreeze.md"
    main_before = base_main.read_text(encoding="utf-8")
    supp_before = base_supp.read_text(encoding="utf-8")
    main_after = replace_once(
        main_before, OLD_CHILDHOOD, NEW_CHILDHOOD, "GSE135779 source-label-defined donor sentence"
    )
    supp_after = replace_once(
        supp_before, OLD_TABLE_TITLE, NEW_TABLE_TITLE, "Supplementary Table S5 title"
    )

    manuscript = source_dir / "Manuscript_scientific_stop_gate.md"
    supplement = source_dir / "Supplementary_Information_scientific_stop_gate.md"
    for path, text in (
        (manuscript, main_after),
        (supplement, supp_after),
        (ROOT_MANUSCRIPT, main_after),
        (ROOT_SUPPLEMENT, supp_after),
    ):
        path.write_text(text, encoding="utf-8", newline="\n")

    main_changed_lines = sum(
        left != right for left, right in zip(main_before.splitlines(), main_after.splitlines())
    )
    supp_changed_lines = sum(
        left != right for left, right in zip(supp_before.splitlines(), supp_after.splitlines())
    )
    checks = {
        "main_exactly_one_changed_line": main_changed_lines == 1,
        "supplement_exactly_one_changed_line": supp_changed_lines == 1,
        "root_manuscript_exact_phase17_parity": ROOT_MANUSCRIPT.read_bytes() == manuscript.read_bytes(),
        "root_supplement_exact_phase17_parity": ROOT_SUPPLEMENT.read_bytes() == supplement.read_bytes(),
        "ambiguous_mapped_cells_sentence_absent": OLD_CHILDHOOD not in main_after,
        "source_label_defined_sentence_present": NEW_CHILDHOOD in main_after,
        "selected_figure_table_title_present": NEW_TABLE_TITLE in supp_after,
        "old_table_title_absent": OLD_TABLE_TITLE not in supp_after,
        "credit_validation_retained": "Project administration, Validation, Writing" in main_after,
        "methodological_validation_boundaries_retained": (
            "not independent validation of the full feature-selection and tuning pipeline" in main_after
            and "prospective clinical validation" in main_after
        ),
    }
    return manuscript, supplement, checks


def redraw_s4() -> dict[str, object]:
    figure_dir = RUN / "figures/figures"
    source_dir = RUN / "figures/source_data"
    base_figure_dir = BASE / "figures/figures"
    old_png = base_figure_dir / f"{S4_NAME}.png"
    old_pdf = base_figure_dir / f"{S4_NAME}.pdf"

    os.environ["NPJ_SBA_STYLE"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    supplementary_figures.ASSERTIONS.clear()
    supplementary_figures.configure_style()
    supplementary_figures.build_s4(
        ROOT,
        figure_dir,
        source_dir,
        log_ratio_two_part=True,
        panel_b_title=NEW_S4_TITLE,
    )

    new_png = figure_dir / f"{S4_NAME}.png"
    new_pdf = figure_dir / f"{S4_NAME}.pdf"
    difference = ImageChops.difference(
        Image.open(old_png).convert("RGB"), Image.open(new_png).convert("RGB")
    )
    difference_box = difference.getbbox()
    old_page = PdfReader(old_pdf).pages[0]
    new_page = PdfReader(new_pdf).pages[0]
    old_text = old_page.extract_text() or ""
    new_text = new_page.extract_text() or ""
    old_without_title = normalized(old_text.replace(OLD_S4_TITLE, ""))
    new_without_title = normalized(new_text.replace(NEW_S4_TITLE, ""))
    dimensions_equal = (
        float(old_page.mediabox.width) == float(new_page.mediabox.width)
        and float(old_page.mediabox.height) == float(new_page.mediabox.height)
    )
    title_region_only = bool(
        difference_box
        and difference_box[0] >= 2000
        and difference_box[1] <= 180
        and difference_box[3] <= 220
    )
    return {
        "old_pdf_sha256": sha256(old_pdf),
        "new_pdf_sha256": sha256(new_pdf),
        "old_png_sha256": sha256(old_png),
        "new_png_sha256": sha256(new_png),
        "source_sha256": sha256(source_dir / S4_SOURCE),
        "pixel_difference_bbox": list(difference_box) if difference_box else None,
        "title_region_only_pixel_change": title_region_only,
        "all_extracted_text_except_title_identical": old_without_title == new_without_title,
        "page_dimensions_identical": dimensions_equal,
        "new_title_present": NEW_S4_TITLE in new_text,
        "old_title_absent": OLD_S4_TITLE not in new_text,
        "builder_assertions": list(supplementary_figures.ASSERTIONS),
    }


def compare_frozen_objects() -> dict[str, object]:
    base_figures = BASE / "figures/figures"
    new_figures = RUN / "figures/figures"
    base_sources = BASE / "figures/source_data"
    new_sources = RUN / "figures/source_data"
    figure_rows: list[dict[str, object]] = []
    for old in sorted(path for path in base_figures.iterdir() if path.is_file()):
        new = new_figures / old.name
        figure_rows.append(
            {
                "file": old.name,
                "base_sha256": sha256(old),
                "new_sha256": sha256(new),
                "byte_identical": old.read_bytes() == new.read_bytes(),
                "expected_change": old.stem == S4_NAME,
            }
        )
    source_rows: list[dict[str, object]] = []
    for old in sorted(path for path in base_sources.iterdir() if path.is_file()):
        new = new_sources / old.name
        source_rows.append(
            {
                "file": old.name,
                "sha256": sha256(new),
                "byte_identical": old.read_bytes() == new.read_bytes(),
            }
        )
    return {
        "figure_rows": figure_rows,
        "source_rows": source_rows,
        "all_non_s4_figures_byte_identical": all(
            row["byte_identical"] for row in figure_rows if not row["expected_change"]
        ),
        "only_s4_figure_files_changed": all(
            (not row["byte_identical"]) == row["expected_change"] for row in figure_rows
        ),
        "all_source_data_byte_identical": all(row["byte_identical"] for row in source_rows),
        "source_file_count_unchanged": len(source_rows)
        == len([path for path in base_sources.iterdir() if path.is_file()]),
    }


def write_ledgers() -> None:
    rows = [
        {
            "object": "01_manuscript/Manuscript.md",
            "decision": "MODIFY",
            "change": "Synchronize from current refreeze and replace ambiguous mapped-cells sentence",
            "scientific_estimates_changed": False,
        },
        {
            "object": "01_manuscript/Supplementary_Information.md",
            "decision": "MODIFY",
            "change": "Synchronize from current refreeze and rename Table S5 as selected-figure map",
            "scientific_estimates_changed": False,
        },
        {
            "object": "Supplementary Figure S4b",
            "decision": "MODIFY_TITLE_ONLY",
            "change": NEW_S4_TITLE,
            "scientific_estimates_changed": False,
        },
        {
            "object": "All other main and Supplementary panels",
            "decision": "KEEP",
            "change": "None",
            "scientific_estimates_changed": False,
        },
    ]
    with (RUN / "CANONICAL_SOURCE_S4B_EDIT_LEDGER.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_status = json.loads(
        (BASE / "04_FINAL_INTEGRATED_READER_REFREEZE_STATUS.json").read_text(encoding="utf-8")
    )
    safe_reset(RUN)
    archived = archive_received_inputs()
    shutil.copytree(BASE / "figures", RUN / "figures")
    manuscript, supplement, source_checks = synchronize_sources()
    s4 = redraw_s4()
    frozen = compare_frozen_objects()
    write_ledgers()

    checks = {
        "base_scientific_refreeze_locked": base_status.get("status")
        == "INTEGRATED_READER_PATH_AND_DISPLAY_PRUNE_SCIENTIFIC_REFREEZE_LOCKED",
        "all_received_inputs_archived_byte_identically": all(
            item["byte_identical"] for item in archived.values()
        ),
        **source_checks,
        "s4_frozen_source_hash_unchanged": s4["source_sha256"] == S4_SOURCE_SHA256,
        "s4_title_only_text_change": s4["all_extracted_text_except_title_identical"],
        "s4_title_only_pixel_region": s4["title_region_only_pixel_change"],
        "s4_page_geometry_unchanged": s4["page_dimensions_identical"],
        "s4_neutral_title_present": s4["new_title_present"],
        "s4_old_title_absent": s4["old_title_absent"],
        "s4_builder_assertions_pass": all(
            assertion.get("pass", False) for assertion in s4["builder_assertions"]
        ),
        "all_non_s4_figures_byte_identical": frozen["all_non_s4_figures_byte_identical"],
        "only_s4_figure_files_changed": frozen["only_s4_figure_files_changed"],
        "all_source_data_byte_identical": frozen["all_source_data_byte_identical"],
        "source_file_count_unchanged": frozen["source_file_count_unchanged"],
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Semantic stop-gate integration failed: {failed}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_CANONICAL_SOURCE_SYNC_AND_S4B_SOURCE_REDRAW_DOCUMENT_REBUILD_REQUIRED",
        "checks": checks,
        "failed_checks": [],
        "archived_inputs": archived,
        "sources": {
            "manuscript": manuscript.relative_to(ROOT).as_posix(),
            "supplement": supplement.relative_to(ROOT).as_posix(),
            "root_manuscript_sha256": sha256(ROOT_MANUSCRIPT),
            "root_supplement_sha256": sha256(ROOT_SUPPLEMENT),
        },
        "s4": s4,
        "frozen_object_comparison": frozen,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "source_data_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "title_only_redraws": ["Supplementary Figure S4b"],
        "submission_package_sha256": PACKAGE_SHA256,
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
    }
    (RUN / "00_CANONICAL_SOURCE_S4B_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
