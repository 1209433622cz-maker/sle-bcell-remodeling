#!/usr/bin/env python3
"""Apply the narrow Supplementary Table claim-owner semantic micropass."""

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
PARENT = ROOT / "phase17_v7/npj_sba_supplementary_citation_refreeze/20260901_first_citation_order"
RUN = ROOT / "phase17_v7/npj_sba_supplementary_table_claim_owner/20260902_semantic_micropass"
RECEIVED = ROOT / "00_project_management/supplementary_table_claim_owner_2026-09-02/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"

EXTERNAL_INPUTS = {
    Path("C:/Users/Administrator/Downloads/action_record_2026-09-02_post_readerpath_claim_owner_hostile_audit.md"):
        "action_record_2026-09-02_post_readerpath_claim_owner_hostile_audit.md",
    Path("C:/Users/Administrator/Downloads/SUPPLEMENTARY_TABLE_CLAIM_OWNER_DECISION_MATRIX.csv"):
        "SUPPLEMENTARY_TABLE_CLAIM_OWNER_DECISION_MATRIX.csv",
    Path("C:/Users/Administrator/Downloads/EXACT_TEXT_PATCH_SUPPLEMENTARY_TABLE_CLAIM_OWNER.md"):
        "EXACT_TEXT_PATCH_SUPPLEMENTARY_TABLE_CLAIM_OWNER.md",
    Path("C:/Users/Administrator/.codex/attachments/7c5ee0bd-3097-4482-b2aa-022f93fcdec2/pasted-text.txt"):
        "pasted_post_readerpath_claim_owner_review_2026-09-02.txt",
}

PATCHES = [
    (
        "A2a",
        "Supplementary Table S3 quantitative owner",
        "Taken together, these layers support an IFN-centred interpretation of the replicated program while defining its evidential ceiling.",
        "Taken together, these layers support an IFN-centred interpretation of the replicated program while defining its evidential ceiling, with principal quantitative anchors summarized in Supplementary Table S3.",
    ),
    (
        "A2b",
        "Remove S3 from causal-ceiling non-identification sentence",
        "None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE (Supplementary Table S3).",
        "None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.",
    ),
    (
        "A3a",
        "Supplementary Table S4a correlation-aware owner",
        "(Supplementary Fig. S9; Supplementary Table S4).",
        "(Supplementary Fig. S9; Supplementary Table S4a).",
    ),
    (
        "A3b",
        "Supplementary Table S4b overlap-depletion owner",
        "(Supplementary Fig. S10).",
        "(Supplementary Fig. S10; Supplementary Table S4b).",
    ),
    (
        "A4a",
        "Supplementary Tables S5-S8 reproducibility owner",
        "Analyses were organized in timestamped run directories with immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 manifests.",
        "Analyses were organized in timestamped run directories with immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 manifests (Supplementary Tables S5-S8).",
    ),
    (
        "A4b",
        "Remove S5-S8 from superseded-object sentence",
        "Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version (Supplementary Tables S5-S8).",
        "Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version.",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def transform(text: str) -> tuple[str, list[dict[str, object]]]:
    output = text
    ledger = []
    for edit_id, owner, before, after in PATCHES:
        if output.count(before) != 1:
            raise RuntimeError(f"Expected exactly one source anchor for {edit_id}: {before}")
        output = output.replace(before, after)
        ledger.append(
            {
                "edit_id": edit_id,
                "claim_owner": owner,
                "before": before,
                "after": after,
                "scientific_value_changed": False,
            }
        )
    return output, ledger


def first_figure_citation_order(text: str) -> list[int]:
    body = text.split("## Figure legends", 1)[0]
    order: list[int] = []
    for value in re.findall(r"Supplementary Fig(?:ure)?\. S(10|[1-9])", body):
        number = int(value)
        if number not in order:
            order.append(number)
    return order


def table_coverage(text: str) -> list[int]:
    body = text.split("## Figure legends", 1)[0]
    covered = {int(value) for value in re.findall(r"Supplementary Table S(\d+)", body)}
    for match in re.finditer(r"Supplementary Tables S(\d+)(?:-S(\d+)| and S(\d+))", body):
        first = int(match.group(1))
        if match.group(2):
            covered.update(range(first, int(match.group(2)) + 1))
        elif match.group(3):
            covered.update((first, int(match.group(3))))
    return sorted(covered)


def scientific_numbers(text: str) -> list[str]:
    body = re.sub(
        r"Supplementary (?:Tables?|Figs?|Figures?) S\d+(?:[ab])?(?:-S\d+| and S\d+)?",
        "",
        text,
    )
    return re.findall(r"(?<![A-Za-z])[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:e[-+]?\d+)?(?:\s*x\s*10\^-?\d+)?%?", body)


def selected_front_matter(text: str) -> str:
    return text.split("## Results", 1)[0]


def frozen_assets() -> list[Path]:
    figure_dir = PARENT / "figures/figures"
    source_dir = PARENT / "figures/source_data"
    return sorted(figure_dir.glob("*.pdf")) + sorted(figure_dir.glob("*.png")) + sorted(source_dir.glob("*.csv"))


def write_diff(path: Path, before: str, after: str) -> None:
    raw = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="Manuscript_before_claim_owner.md",
            tofile="Manuscript_after_claim_owner.md",
        )
    )
    clean = "\n".join(line.rstrip(" \t") for line in raw.splitlines()).rstrip() + "\n"
    path.write_text(clean, encoding="utf-8", newline="\n")


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "sources").mkdir(parents=True, exist_ok=True)
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

    before_path = PARENT / "sources/Manuscript_first_citation_order_refreeze.md"
    supplement_path = PARENT / "sources/Supplementary_Information_first_citation_order_refreeze.md"
    before = before_path.read_text(encoding="utf-8")
    supplement = supplement_path.read_text(encoding="utf-8")
    after, ledger = transform(before)

    root_main = ROOT / "01_manuscript/Manuscript.md"
    root_supplement = ROOT / "01_manuscript/Supplementary_Information.md"
    current_main_hash = sha256(root_main)
    allowed_main_hashes = {hashlib.sha256(before.encode()).hexdigest().upper(), hashlib.sha256(after.encode()).hexdigest().upper()}
    if current_main_hash not in allowed_main_hashes:
        raise RuntimeError("Root manuscript is neither the frozen parent nor this exact micropass candidate")
    if root_supplement.read_text(encoding="utf-8") != supplement:
        raise RuntimeError("Root Supplementary Information drifted from the frozen parent")

    asset_paths = frozen_assets()
    assets_before = {path: sha256(path) for path in asset_paths}

    source_before = RUN / "sources/Manuscript_before_claim_owner.md"
    source_after = RUN / "sources/Manuscript_claim_owner_semantic_micropass.md"
    source_supplement = RUN / "sources/Supplementary_Information_unchanged.md"
    source_before.write_text(before, encoding="utf-8", newline="\n")
    source_after.write_text(after, encoding="utf-8", newline="\n")
    source_supplement.write_text(supplement, encoding="utf-8", newline="\n")
    root_main.write_text(after, encoding="utf-8", newline="\n")

    write_diff(RUN / "03_MANUSCRIPT_CLAIM_OWNER_EDIT_LEDGER.diff", before, after)
    with (RUN / "01_CLAIM_OWNER_EDIT_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)

    decision_rows = [
        {"object": "Supplementary Tables S1-S2", "decision": "KEEP", "claim_owner": "dataset roles and inferential boundaries", "main_location": "Introduction evidence-hierarchy sentence"},
        {"object": "Supplementary Table S3", "decision": "MOVE", "claim_owner": "principal quantitative anchors", "main_location": "Results quantitative synthesis sentence"},
        {"object": "Supplementary Table S4a", "decision": "REFINE", "claim_owner": "correlation-aware regulator sensitivity", "main_location": "Results correlation-aware paragraph"},
        {"object": "Supplementary Table S4b", "decision": "ADD_PRECISE_SUBANCHOR", "claim_owner": "IFN-overlap depletion", "main_location": "Results overlap-depletion paragraph"},
        {"object": "Supplementary Tables S5-S8", "decision": "MOVE", "claim_owner": "source mapping, reproducibility, statistical families and archive", "main_location": "Methods reproducibility opening sentence"},
        {"object": "Supplementary Table S9", "decision": "KEEP", "claim_owner": "reference-calibrated external mapping boundary", "main_location": "Results corrected-remapping paragraph"},
    ]
    with (RUN / "02_CLAIM_OWNER_DECISION_MATRIX.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decision_rows[0]))
        writer.writeheader()
        writer.writerows(decision_rows)

    assets_after = {path: sha256(path) for path in asset_paths}
    with (RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = ["relative_path", "bytes", "sha256_before", "sha256_after", "unchanged"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for path in asset_paths:
            writer.writerow(
                {
                    "relative_path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256_before": assets_before[path],
                    "sha256_after": assets_after[path],
                    "unchanged": assets_before[path] == assets_after[path],
                }
            )

    shutil.copy2(PARENT / "02_PANEL_DECISION_MATRIX.csv", RUN / "05_PANEL_DECISION_MATRIX.csv")
    (RUN / ".gitignore").write_text(
        "qa/lo_render/\nqa/wps_pages/*/\nqa/lo_pages/*/\n",
        encoding="ascii",
        newline="\n",
    )

    checks = {
        "external_inputs_archived_byte_identically": all(item["byte_identical"] for item in archived_inputs.values()),
        "six_exact_text_operations": len(ledger) == 6,
        "supplementary_table_coverage_s1_to_s9": table_coverage(after) == list(range(1, 10)),
        "supplementary_figure_first_citation_order_s1_to_s10": first_figure_citation_order(after) == list(range(1, 11)),
        "s3_attached_to_quantitative_synthesis": after.count("principal quantitative anchors summarized in Supplementary Table S3") == 1,
        "s3_absent_from_causal_nonidentification_sentence": "causal regulation in SLE (Supplementary Table S3)" not in after,
        "s4a_exact_owner_present": after.count("Supplementary Fig. S9; Supplementary Table S4a") == 1,
        "s4b_exact_owner_present": after.count("Supplementary Fig. S10; Supplementary Table S4b") == 1,
        "generic_s4_anchor_absent": "Supplementary Table S4)" not in after,
        "s5_s8_attached_to_reproducibility_sentence": after.count("SHA-256 manifests (Supplementary Tables S5-S8)") == 1,
        "s5_s8_absent_from_superseded_sentence": "present version (Supplementary Tables S5-S8)" not in after,
        "title_and_abstract_unchanged": selected_front_matter(before) == selected_front_matter(after),
        "scientific_number_sequence_unchanged": scientific_numbers(before) == scientific_numbers(after),
        "supplementary_information_unchanged": root_supplement.read_text(encoding="utf-8") == supplement,
        "all_frozen_figure_and_source_assets_unchanged": assets_before == assets_after,
        "forty_five_frozen_assets_audited": len(asset_paths) == 45,
        "root_main_matches_candidate": root_main.read_text(encoding="utf-8") == after,
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_CLAIM_OWNER_MICROPASS_INTEGRATION_DOCX_REQUIRED" if not failed else "FAIL_CLAIM_OWNER_MICROPASS_INTEGRATION",
        "checks": checks,
        "failed_checks": failed,
        "archived_inputs": archived_inputs,
        "claim_owner_defects_repaired": ["A2", "A3", "A4"],
        "exact_text_operations": len(ledger),
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
        "parent_commit": "b087de3b385e2f6486499466470355e001c75bc1",
        "submission_package_sha256": sha256(PACKAGE),
    }
    (RUN / "00_CLAIM_OWNER_MICROPASS_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Integration checks failed: {failed}")


if __name__ == "__main__":
    main()
