#!/usr/bin/env python3
"""Finalize document render QA for the scientific-harmonization candidate."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RUN = (
    ROOT
    / "phase17_v7/npj_sba_selected_supplementary_refinement/"
    "20260831_s4_s10_semantic_harmonization"
)
DOCUMENTS = RUN / "documents"
QA = RUN / "qa"
FINAL_CONTACTS = QA / "final_contact_sheets"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
EXPECTED_PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_pdf(path: Path) -> list[str]:
    return [(page.extract_text() or "").strip() for page in PdfReader(path).pages]


def copy_final_pdf(render_dir: Path, name: str) -> Path:
    source = render_dir / name
    target = DOCUMENTS / name
    if not source.is_file():
        raise FileNotFoundError(source)
    shutil.copy2(source, target)
    return target


def copy_contact_sheets(render_dir: Path, pattern: str) -> list[Path]:
    FINAL_CONTACTS.mkdir(parents=True, exist_ok=True)
    outputs = []
    for source in sorted((render_dir / "contact_input").glob(pattern)):
        target = FINAL_CONTACTS / source.name
        shutil.copy2(source, target)
        outputs.append(target)
    if not outputs:
        raise FileNotFoundError(f"No contact sheets matched {pattern} in {render_dir}")
    return outputs


def main() -> None:
    manuscript_name = "Manuscript_scientific_harmonization_candidate.pdf"
    supplement_name = "Supplementary_Information_scientific_harmonization_candidate.pdf"
    manuscript = copy_final_pdf(QA / "manuscript_render_final", manuscript_name)
    supplement = copy_final_pdf(QA / "supplement_render_final", supplement_name)
    manuscript_contacts = copy_contact_sheets(
        QA / "manuscript_render_final", "contact_sheet_manuscript_final_*.png"
    )
    supplement_contacts = copy_contact_sheets(
        QA / "supplement_render_final", "contact_sheet_supplement_final_*.png"
    )

    manuscript_pages = read_pdf(manuscript)
    supplement_pages = read_pdf(supplement)
    manuscript_text = "\n".join(manuscript_pages)
    supplement_text = "\n".join(supplement_pages)
    manuscript_normalized = " ".join(manuscript_text.split())
    supplement_normalized = " ".join(supplement_text.split())
    manuscript_a11y = json.loads((QA / "manuscript_a11y.json").read_text(encoding="utf-8"))
    supplement_a11y = json.loads((QA / "supplement_a11y.json").read_text(encoding="utf-8"))
    package_sha = sha256(PACKAGE)

    manuscript_checks = {
        "page_count_32": len(manuscript_pages) == 32,
        "no_blank_pages": all(len(text) >= 80 for text in manuscript_pages),
        "title_on_page_1": "Disease-blind reconstruction distinguishes" in manuscript_pages[0],
        "data_availability_on_page_24": "Data availability" in manuscript_pages[23],
        "references_start_on_page_25": "References" in manuscript_pages[24],
        "figure_legends_start_on_page_29": "Figure legends" in manuscript_pages[28],
        "figure5_boundary_on_page_32": "descriptive at n=2" in manuscript_pages[31],
        "anti_pseudoreplication_present": (
            "no inferential test treated genes as biological replicates" in manuscript_normalized
        ),
        "figure5_ulm_ownership_present": (
            "ULM STAT1/STAT2 activity was positive" in manuscript_normalized
        ),
        "isolated_x_absent": not any(line.strip() == "X" for line in manuscript_text.splitlines()),
        "a11y_zero": manuscript_a11y.get("counts") == {"high": 0, "medium": 0, "low": 0},
    }
    supplement_checks = {
        "page_count_16": len(supplement_pages) == 16,
        "no_blank_pages": all(len(text) >= 80 for text in supplement_pages),
        "table_s7_on_page_4": "Supplementary Table S7" in supplement_pages[3],
        "table_s9_on_page_5": "Supplementary Table S9" in supplement_pages[4],
        "s1_on_page_7": "Supplementary Figure S1" in supplement_pages[6],
        "s4_on_page_10": "Supplementary Figure S4" in supplement_pages[9],
        "s10_on_page_16": "Supplementary Figure S10" in supplement_pages[15],
        "log_scale_semantics_present": "logarithmic ratio axes" in supplement_normalized,
        "mapper_semantics_present": "Mapper colour is held constant" in supplement_normalized,
        "balanced_accuracy_diagnostic_only": (
            "balanced accuracy is diagnostic only" in supplement_normalized
        ),
        "a11y_zero": supplement_a11y.get("counts") == {"high": 0, "medium": 0, "low": 0},
    }
    global_checks = {
        "package_sha_unchanged": package_sha == EXPECTED_PACKAGE_SHA256,
        "four_manuscript_contact_sheets": len(manuscript_contacts) == 4,
        "three_supplement_contact_sheets": len(supplement_contacts) == 3,
    }
    checks = {
        "manuscript": manuscript_checks,
        "supplement": supplement_checks,
        "global": global_checks,
    }
    failed = [
        f"{group}.{name}"
        for group, group_checks in checks.items()
        for name, passed in group_checks.items()
        if not passed
    ]
    if failed:
        raise RuntimeError(f"Final render QA failed: {failed}")

    render_intermediates = [
        QA / "manuscript_render",
        QA / "supplement_render",
        QA / "manuscript_render_final",
        QA / "supplement_render_final",
    ]
    qa_resolved = QA.resolve()
    for directory in render_intermediates:
        resolved = directory.resolve()
        if qa_resolved not in resolved.parents:
            raise RuntimeError(f"Refusing to remove render intermediates outside QA: {resolved}")
        if resolved.is_dir():
            shutil.rmtree(resolved)

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_SCIENTIFIC_HARMONIZATION_DOCUMENT_RENDER_AND_VISUAL_QA",
        "documents": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "pages": len(manuscript_pages) if path == manuscript else len(supplement_pages),
            }
            for path in (manuscript, supplement)
        },
        "checks": checks,
        "visual_review": {
            "all_48_pages_reviewed": True,
            "manuscript_pages_reviewed": list(range(1, 33)),
            "supplement_pages_reviewed": list(range(1, 17)),
            "clipping_overlap_or_missing_glyphs": False,
            "supplement_whitespace_repair": (
                "Removed the forced pre-Table-S7 page break; the supplement contracted from 17 to 16 pages."
            ),
            "render_intermediates_removed_after_finalization": True,
            "contact_sheets": [
                path.relative_to(ROOT).as_posix()
                for path in manuscript_contacts + supplement_contacts
            ],
        },
        "package_sha256": package_sha,
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "exact_submission_package_modified": False,
    }
    (RUN / "03_RENDER_QA_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"status": status["status"], "documents": status["documents"]}, indent=2))


if __name__ == "__main__":
    main()
