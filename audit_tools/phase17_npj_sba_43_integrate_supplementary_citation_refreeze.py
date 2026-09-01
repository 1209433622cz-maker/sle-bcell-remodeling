#!/usr/bin/env python3
"""Renumber Supplementary Figures by first citation without changing science."""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import shutil
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase17_v7/npj_sba_supplementary_table_reader_path/20260901_s4_reader_path_refreeze"
RUN = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
RECEIVED = ROOT / "00_project_management/supplementary_first_citation_order_2026-09-01/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"

EXTERNAL_INPUTS = {
    Path("C:/Users/Administrator/Downloads/SUPPLEMENTARY_FIGURE_FIRST_CITATION_RENUMBER_MAP.csv"):
        "SUPPLEMENTARY_FIGURE_FIRST_CITATION_RENUMBER_MAP.csv",
    Path("C:/Users/Administrator/Downloads/SUPPLEMENTARY_RENUMBER_AND_CROSS_REFERENCE_PATCH_SPEC.md"):
        "SUPPLEMENTARY_RENUMBER_AND_CROSS_REFERENCE_PATCH_SPEC.md",
    Path("C:/Users/Administrator/Downloads/action_record_2026-09-01_supplementary_first_citation_order_hostile_audit.md"):
        "action_record_2026-09-01_supplementary_first_citation_order_hostile_audit.md",
    Path("C:/Users/Administrator/.codex/attachments/cd4dfb08-d4d7-446b-bd05-48e23990615f/pasted-text.txt"):
        "pasted_supplementary_first_citation_review_2026-09-01.txt",
}

# Ordered by the intended reader path, not by the old display identifier.
RENUMBER = OrderedDict(
    [
        (1, 1),
        (2, 2),
        (3, 3),
        (9, 4),
        (4, 5),
        (5, 6),
        (6, 7),
        (10, 8),
        (7, 9),
        (8, 10),
    ]
)

MAIN_ANCHORS = [
    (
        "This design tests an evidence hierarchy: which B-cell features survive increasingly stringent reconstruction and replication tests, and which remain cohort-specific, representation-dependent or mechanistically unproven.",
        "This design tests an evidence hierarchy: which B-cell features survive increasingly stringent reconstruction and replication tests, and which remain cohort-specific, representation-dependent or mechanistically unproven (Supplementary Tables S1 and S2).",
        "Dataset-role and claim-boundary anchor",
    ),
    (
        "None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.",
        "None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE (Supplementary Table S3).",
        "Quantitative-anchor table citation",
    ),
    (
        "(Supplementary Fig. S9).",
        "(Supplementary Fig. S9; Supplementary Table S4).",
        "Regulator-sensitivity table anchor",
    ),
    (
        "Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version.",
        "Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version (Supplementary Tables S5-S8).",
        "Reproducibility-table anchor",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def remap_references(text: str) -> str:
    patterns = [
        re.compile(r"Supplementary Fig\. S(10|[1-9])"),
        re.compile(r"Supplementary Figure S(10|[1-9])"),
        re.compile(r"\[\[SUPPLEMENTARY_FIGURE:S(10|[1-9])\]\]"),
        re.compile(r"Supplementary_Figure_S(10|[1-9])"),
    ]

    def replace(match: re.Match[str]) -> str:
        old = int(match.group(1))
        new = RENUMBER[old]
        return match.group(0).replace(f"S{old}", f"S{new}")

    for pattern in patterns:
        text = pattern.sub(replace, text)
    return text


def first_citation_order(text: str) -> list[int]:
    body = text.split("## Figure legends", 1)[0]
    seen: list[int] = []
    for value in re.findall(r"Supplementary Fig(?:ure)?\. S(10|[1-9])", body):
        number = int(value)
        if number not in seen:
            seen.append(number)
    return seen


def table_citation_coverage(text: str) -> list[int]:
    body = text.split("## Figure legends", 1)[0]
    covered = {int(value) for value in re.findall(r"Supplementary Table S(\d+)", body)}
    for match in re.finditer(r"Supplementary Tables S(\d+)(?:-S(\d+)| and S(\d+))", body):
        first = int(match.group(1))
        if match.group(2):
            covered.update(range(first, int(match.group(2)) + 1))
        elif match.group(3):
            covered.update((first, int(match.group(3))))
    return sorted(covered)


def transform_supplement(text: str) -> str:
    heading = re.compile(r"(?m)^## Supplementary Figure S(10|[1-9]) \|")
    matches = list(heading.finditer(text))
    if [int(match.group(1)) for match in matches] != list(range(1, 11)):
        raise RuntimeError("Expected Supplementary Figure blocks S1-S10 in the frozen source")

    prefix = remap_references(text[: matches[0].start()])
    blocks: dict[int, str] = {}
    for index, match in enumerate(matches):
        old = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[RENUMBER[old]] = remap_references(text[match.start() : end])

    old_rows = (
        "| Supplementary Figure S10 | STAT1/STAT2 IFN-overlap-depletion sensitivity | Supplementary_Figure_S10_source_data.csv |\n"
        "| Supplementary Figure S4 | End-to-end identity boundary and downstream propagation | Supplementary_Figure_S4_source_data.csv |\n"
        "| Supplementary Figure S8 | Corrected reference calibration and unresolved external transfer | Supplementary_Figure_S8_source_data.csv |"
    )
    new_rows = (
        "| Supplementary Figure S4 | End-to-end identity boundary and downstream propagation | Supplementary_Figure_S4_source_data.csv |\n"
        "| Supplementary Figure S8 | Corrected reference calibration and unresolved external transfer | Supplementary_Figure_S8_source_data.csv |\n"
        "| Supplementary Figure S10 | STAT1/STAT2 IFN-overlap-depletion sensitivity | Supplementary_Figure_S10_source_data.csv |"
    )
    if prefix.count(old_rows) != 1:
        raise RuntimeError("Could not identify the remapped Supplementary Table S5 rows")
    prefix = prefix.replace(old_rows, new_rows)
    normalized_blocks = [blocks[number].rstrip() + "\n\n" for number in range(1, 11)]
    return (prefix.rstrip() + "\n\n" + "".join(normalized_blocks)).rstrip() + "\n"


def remapped_name(name: str) -> str:
    match = re.match(r"^(Supplementary_Figure_)S(10|[1-9])(.*)$", name)
    if not match:
        return name
    return f"{match.group(1)}S{RENUMBER[int(match.group(2))]}{match.group(3)}"


def copy_remapped_figures() -> list[dict[str, object]]:
    source_root = BASE / "figures"
    destination_root = RUN / "figures"
    if destination_root.exists():
        shutil.rmtree(destination_root)
    rows: list[dict[str, object]] = []
    for source in sorted(item for item in source_root.rglob("*") if item.is_file()):
        relative = source.relative_to(source_root)
        destination_relative = relative.with_name(remapped_name(relative.name))
        destination = destination_root / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        match = re.match(r"^Supplementary_Figure_S(10|[1-9])", source.name)
        if match:
            old = int(match.group(1))
            rows.append(
                {
                    "old_display_id": f"S{old}",
                    "new_display_id": f"S{RENUMBER[old]}",
                    "object_type": source.suffix.lower().lstrip("."),
                    "old_relative_path": source.relative_to(ROOT).as_posix(),
                    "new_relative_path": destination.relative_to(ROOT).as_posix(),
                    "bytes": destination.stat().st_size,
                    "old_sha256": sha256(source),
                    "new_sha256": sha256(destination),
                    "byte_identical": sha256(source) == sha256(destination),
                }
            )
    return rows


def remap_panel_matrix() -> None:
    source = BASE / "02_PANEL_DECISION_MATRIX.csv"
    output = RUN / "02_PANEL_DECISION_MATRIX.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0])
    for row in rows:
        match = re.match(r"Supplementary Figure S(10|[1-9])([a-z])$", row["object"])
        if match:
            old = int(match.group(1))
            row["object"] = f"Supplementary Figure S{RENUMBER[old]}{match.group(2)}"
            row["artwork_action"] = "DISPLAY_ID_RENUMBER_ONLY"
            row["rationale"] = "Scientific panel retained byte-identically; display identifier follows first-citation order."
        else:
            row["artwork_action"] = "KEEP_EXACT"
            row["rationale"] = "Main scientific panel retained without change."
    rows.sort(
        key=lambda row: (
            0 if row["tier"] == "Main" else 1,
            int(re.search(r"(?:Figure |Figure S)(\d+)", row["object"]).group(1)),
            row["object"],
        )
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_diff(path: Path, before: str, after: str, before_name: str, after_name: str) -> None:
    path.write_text(
        "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=before_name,
                tofile=after_name,
            )
        ),
        encoding="utf-8",
        newline="\n",
    )


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

    external_map = {}
    with (RECEIVED / "SUPPLEMENTARY_FIGURE_FIRST_CITATION_RENUMBER_MAP.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            external_map[int(row["old_display_id"][1:])] = int(row["new_display_id"][1:])

    base_main_path = BASE / "sources/Manuscript_scientific_maintenance_freeze.md"
    base_supplement_path = BASE / "sources/Supplementary_Information_s4_reader_path_micropass.md"
    before_main = base_main_path.read_text(encoding="utf-8")
    before_supplement = base_supplement_path.read_text(encoding="utf-8")
    old_order = first_citation_order(before_main)

    after_main = remap_references(before_main)
    applied_anchors = []
    for old, new, label in MAIN_ANCHORS:
        if after_main.count(old) != 1:
            raise RuntimeError(f"Expected one anchor target for {label}: {old}")
        after_main = after_main.replace(old, new)
        applied_anchors.append({"object": label, "before": old, "after": new})
    after_supplement = transform_supplement(before_supplement)

    main_destination = sources / "Manuscript_first_citation_order_refreeze.md"
    supplement_destination = sources / "Supplementary_Information_first_citation_order_refreeze.md"
    main_destination.write_text(after_main, encoding="utf-8", newline="\n")
    supplement_destination.write_text(after_supplement, encoding="utf-8", newline="\n")
    (ROOT / "01_manuscript/Manuscript.md").write_text(after_main, encoding="utf-8", newline="\n")
    (ROOT / "01_manuscript/Supplementary_Information.md").write_text(
        after_supplement, encoding="utf-8", newline="\n"
    )

    write_diff(
        RUN / "01_MANUSCRIPT_TEXT_EDIT_LEDGER.diff",
        before_main,
        after_main,
        "Manuscript_before.md",
        "Manuscript_after.md",
    )
    write_diff(
        RUN / "02_SUPPLEMENTARY_TEXT_EDIT_LEDGER.diff",
        before_supplement,
        after_supplement,
        "Supplementary_Information_before.md",
        "Supplementary_Information_after.md",
    )

    provenance_rows = copy_remapped_figures()
    with (RUN / "03_SUPPLEMENTARY_DISPLAY_ID_PROVENANCE.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        fieldnames = list(provenance_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(provenance_rows)
    remap_panel_matrix()

    with (RUN / "04_MAIN_TEXT_ANCHOR_LEDGER.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["edit_id", "object", "before", "after", "scientific_value_changed"],
        )
        writer.writeheader()
        for index, row in enumerate(applied_anchors, start=1):
            writer.writerow(
                {
                    "edit_id": f"A{index}",
                    **row,
                    "scientific_value_changed": False,
                }
            )

    new_order = first_citation_order(after_main)
    table_coverage = table_citation_coverage(after_main)
    supplement_headings = [
        int(value)
        for value in re.findall(r"(?m)^## Supplementary Figure S(10|[1-9]) \|", after_supplement)
    ]
    supplement_markers = [
        int(value)
        for value in re.findall(r"\[\[SUPPLEMENTARY_FIGURE:S(10|[1-9])\]\]", after_supplement)
    ]
    provenance_pairs = {
        (int(row["old_display_id"][1:]), int(row["new_display_id"][1:]))
        for row in provenance_rows
    }
    checks = {
        "external_inputs_archived_byte_identically": all(
            item["byte_identical"] for item in archived_inputs.values()
        ),
        "external_map_matches_independent_map": external_map == dict(RENUMBER),
        "old_first_citation_order_reproduced": old_order == [1, 2, 3, 9, 4, 5, 6, 10, 7, 8],
        "new_first_citation_order_is_s1_to_s10": new_order == list(range(1, 11)),
        "all_supplementary_tables_cited": table_coverage == list(range(1, 10)),
        "supplement_headings_are_s1_to_s10": supplement_headings == list(range(1, 11)),
        "supplement_markers_are_s1_to_s10": supplement_markers == list(range(1, 11)),
        "all_remapped_files_byte_identical": all(row["byte_identical"] for row in provenance_rows),
        "all_ten_display_pairs_audited": provenance_pairs == set(RENUMBER.items()),
        "ten_supplementary_pdfs": len(list((RUN / "figures/figures").glob("Supplementary_Figure_S*.pdf"))) == 10,
        "ten_supplementary_pngs": len(list((RUN / "figures/figures").glob("Supplementary_Figure_S*.png"))) == 10,
        "ten_supplementary_source_csvs": len(list((RUN / "figures/source_data").glob("Supplementary_Figure_S*_source_data.csv"))) == 10,
        "four_functional_anchors_only": len(applied_anchors) == 4,
        "root_main_matches_candidate": sha256(ROOT / "01_manuscript/Manuscript.md") == sha256(main_destination),
        "root_supplement_matches_candidate": sha256(ROOT / "01_manuscript/Supplementary_Information.md") == sha256(supplement_destination),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": (
            "PASS_SUPPLEMENTARY_CITATION_REFREEZE_INTEGRATION_DOCX_REQUIRED"
            if not failed
            else "FAIL_SUPPLEMENTARY_CITATION_REFREEZE_INTEGRATION"
        ),
        "checks": checks,
        "failed_checks": failed,
        "archived_inputs": archived_inputs,
        "renumber_map": {f"S{old}": f"S{new}" for old, new in RENUMBER.items()},
        "first_citation_order_before": [f"S{number}" for number in old_order],
        "first_citation_order_after": [f"S{number}" for number in new_order],
        "supplementary_table_citation_coverage": [f"S{number}" for number in table_coverage],
        "main_text_anchor_edits": len(applied_anchors),
        "scientific_estimates_changed": False,
        "statistical_models_rerun": False,
        "figures_redrawn": False,
        "figure_pixels_changed": False,
        "source_data_values_changed": False,
        "new_panels": 0,
        "replacement_panels": 0,
        "main_panels_keep": 21,
        "supplementary_panels_keep": 38,
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_SUPPLEMENTARY_CITATION_REFREEZE_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Integration checks failed: {failed}")


if __name__ == "__main__":
    main()
