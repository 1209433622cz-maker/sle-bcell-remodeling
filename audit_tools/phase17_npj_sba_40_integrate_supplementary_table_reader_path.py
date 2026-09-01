#!/usr/bin/env python3
"""Integrate the localized Supplementary Table S4 reader-path repair."""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase17_v7/npj_sba_nature_artwork_micropass/20260901_role_aware_typography_refreeze"
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_reader_path/20260901_s4_reader_path_refreeze"
RECEIVED = ROOT / "00_project_management/supplementary_table_s4_reader_path_2026-09-01/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
EXTERNAL_INPUTS = {
    Path("C:/Users/Administrator/Downloads/SLE_Bcell_Post_Typography_Maintenance_Audit_2026-09-01.md"):
        "SLE_Bcell_Post_Typography_Maintenance_Audit_2026-09-01.md",
    Path("C:/Users/Administrator/.codex/attachments/104f95f1-d590-41ad-b419-75a0290054a8/pasted-text.txt"):
        "pasted_post_typography_review_2026-09-01.txt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_hashes(directory: Path, pattern: str) -> dict[str, str]:
    return {path.name: sha256(path) for path in sorted(directory.glob(pattern))}


def main() -> None:
    sources = RUN / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    RECEIVED.mkdir(parents=True, exist_ok=True)

    archived_inputs: dict[str, dict[str, object]] = {}
    for source, name in EXTERNAL_INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = RECEIVED / name
        shutil.copy2(source, destination)
        archived_inputs[name] = {
            "source": str(source),
            "archived": destination.relative_to(ROOT).as_posix(),
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
            "byte_identical": sha256(source) == sha256(destination),
        }

    shutil.copytree(BASE / "figures", RUN / "figures", dirs_exist_ok=True)
    shutil.copy2(BASE / "02_PANEL_DECISION_MATRIX.csv", RUN / "02_PANEL_DECISION_MATRIX.csv")

    base_main = BASE / "sources/Manuscript_nature_artwork_micropass.md"
    base_supplement = BASE / "sources/Supplementary_Information_nature_artwork_micropass.md"
    main_destination = sources / "Manuscript_scientific_maintenance_freeze.md"
    supplement_destination = sources / "Supplementary_Information_s4_reader_path_micropass.md"
    shutil.copy2(base_main, main_destination)

    before = base_supplement.read_text(encoding="utf-8")
    replacements = [
        (
            "## Supplementary Table S4 | Correlation-aware core-regulator sensitivity",
            "## Supplementary Table S4 | Regulator-sensitivity summaries\n\n"
            "**a, Correlation-aware core-regulator sensitivity**",
        ),
        (
            "## Supplementary Table S4B | IFN-overlap-depletion summary",
            "**b, IFN-overlap-depletion summary**",
        ),
        (
            "Sample-level composition and asserted 43/47 primary groups",
            "Sample-level composition in the 43-control/47-managed-SLE primary comparison",
        ),
    ]
    after = before
    for old, new in replacements:
        if after.count(old) != 1:
            raise RuntimeError(f"Expected exactly one occurrence before replacement: {old}")
        after = after.replace(old, new)
    supplement_destination.write_text(after, encoding="utf-8", newline="\n")
    (ROOT / "01_manuscript/Supplementary_Information.md").write_text(
        after, encoding="utf-8", newline="\n"
    )

    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="Supplementary_Information_before.md",
            tofile="Supplementary_Information_after.md",
        )
    )
    (RUN / "01_SUPPLEMENTARY_TEXT_EDIT_LEDGER.diff").write_text(
        diff, encoding="utf-8", newline="\n"
    )
    with (RUN / "03_TEXT_EDIT_LEDGER.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["edit_id", "object", "before", "after", "scientific_value_changed"],
        )
        writer.writeheader()
        for index, (old, new) in enumerate(replacements, start=1):
            writer.writerow(
                {
                    "edit_id": f"T{index}",
                    "object": "Supplementary Information",
                    "before": old,
                    "after": new.replace("\n", " | "),
                    "scientific_value_changed": False,
                }
            )

    table_numbers = [
        int(number)
        for number in re.findall(r"(?m)^## Supplementary Table S(\d+) \|", after)
    ]
    base_figure_hashes = file_hashes(BASE / "figures/figures", "*")
    new_figure_hashes = file_hashes(RUN / "figures/figures", "*")
    base_source_hashes = file_hashes(BASE / "figures/source_data", "*.csv")
    new_source_hashes = file_hashes(RUN / "figures/source_data", "*.csv")
    checks = {
        "received_inputs_archived_byte_identically": all(
            item["byte_identical"] for item in archived_inputs.values()
        ),
        "numbered_tables_are_exactly_s1_to_s9": table_numbers == list(range(1, 10)),
        "orphan_s4b_removed": "Supplementary Table S4B" not in after,
        "s4_parent_heading_present": (
            "## Supplementary Table S4 | Regulator-sensitivity summaries" in after
        ),
        "s4a_subheading_present": (
            "**a, Correlation-aware core-regulator sensitivity**" in after
        ),
        "s4b_subheading_present": "**b, IFN-overlap-depletion summary**" in after,
        "overview_remains_s1_to_s9": "contains Tables S1-S9 and Figures S1-S10" in after,
        "table_s5_reader_wording_present": (
            "Sample-level composition in the 43-control/47-managed-SLE primary comparison"
            in after
        ),
        "exactly_three_local_replacements": len(replacements) == 3,
        "all_figure_files_byte_identical": new_figure_hashes == base_figure_hashes,
        "all_15_source_data_byte_identical": (
            new_source_hashes == base_source_hashes and len(new_source_hashes) == 15
        ),
        "panel_decision_matrix_byte_identical": sha256(RUN / "02_PANEL_DECISION_MATRIX.csv")
        == sha256(BASE / "02_PANEL_DECISION_MATRIX.csv"),
        "main_source_byte_identical": sha256(main_destination) == sha256(base_main),
        "root_main_byte_identical": sha256(ROOT / "01_manuscript/Manuscript.md")
        == sha256(base_main),
        "root_supplement_exact_parity": sha256(
            ROOT / "01_manuscript/Supplementary_Information.md"
        )
        == sha256(supplement_destination),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": (
            "PASS_SUPPLEMENTARY_TABLE_S4_READER_PATH_INTEGRATION_DOCX_REQUIRED"
            if not failed
            else "FAIL_SUPPLEMENTARY_TABLE_S4_READER_PATH_INTEGRATION"
        ),
        "checks": checks,
        "failed_checks": failed,
        "archived_inputs": archived_inputs,
        "table_numbers": table_numbers,
        "text_edits": len(replacements),
        "figures_changed": False,
        "source_data_changed": False,
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_SUPPLEMENTARY_TABLE_S4_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Integration checks failed: {failed}")


if __name__ == "__main__":
    main()
