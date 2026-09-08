#!/usr/bin/env python3
"""Integrate the final cross-document scientific-presentation freeze."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration"
RUN = ROOT / "phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document"
RECEIVED = ROOT / "00_project_management/scientific_presentation_final_cross_document_freeze_2026-09-08/received"
PACKAGE = ROOT / "04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"

EXTERNAL_INPUTS = {
    "action_record_2026-09-08_scientific_presentation_final_cross_document_freeze.md": Path(
        r"C:\Users\Administrator\Downloads\action_record_2026-09-08_scientific_presentation_final_cross_document_freeze.md"
    ),
    "FINAL_CROSS_DOCUMENT_AUDIT.csv": Path(r"C:\Users\Administrator\Downloads\FINAL_CROSS_DOCUMENT_AUDIT.csv"),
    "FINAL_CLAIM_OWNER_MATRIX_2026-09-08.csv": Path(
        r"C:\Users\Administrator\Downloads\FINAL_CLAIM_OWNER_MATRIX_2026-09-08.csv"
    ),
    "FINAL_MAIN_PANEL_DECISION_MATRIX_2026-09-08.csv": Path(
        r"C:\Users\Administrator\Downloads\FINAL_MAIN_PANEL_DECISION_MATRIX_2026-09-08.csv"
    ),
    "Supplementary_Information_Scientific_Presentation_Freeze_2026-09-08.md": Path(
        r"C:\Users\Administrator\Downloads\Supplementary_Information_Scientific_Presentation_Freeze_2026-09-08.md"
    ),
    "Manuscript_Scientific_Presentation_Freeze_2026-09-08.md": Path(
        r"C:\Users\Administrator\Downloads\Manuscript_Scientific_Presentation_Freeze_2026-09-08.md"
    ),
    "Manuscript_Scientific_Presentation_Freeze_2026-09-08.pdf": Path(
        r"C:\Users\Administrator\Downloads\Manuscript_Scientific_Presentation_Freeze_2026-09-08.pdf"
    ),
    "Manuscript_Scientific_Presentation_Freeze_2026-09-08.docx": Path(
        r"C:\Users\Administrator\Downloads\Manuscript_Scientific_Presentation_Freeze_2026-09-08.docx"
    ),
}

OLD_LANDING = "within explicit identity and transfer limits."
NEW_LANDING = "within explicit identity, transfer and mechanistic limits."
S5_REPLACEMENTS = {
    "| Figure 1 | Disease-blind identity stability and two-compartment adjudication | Figure1_source_data.csv |":
        "| Figure 1 | Disease-blind identity stability, two-compartment adjudication and end-to-end B_ASC boundary | Figure1_source_data.csv |",
    "| Figure 4 | Source-label-defined GSE135779 replication and influence analyses | Figure4_source_data.csv |":
        "| Figure 4 | Source-label-defined GSE135779 replication, gene-level coherence and required calibration boundary | Figure4_source_data.csv |",
    "| Figure 5 | Regulatory and orthogonal response evidence | Figure5_source_data.csv |":
        "| Figure 5 | Regulatory convergence, IFN-overlap-depletion ceiling and orthogonal response evidence | Figure5_source_data.csv |",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def archive_inputs() -> list[dict[str, object]]:
    RECEIVED.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, source in EXTERNAL_INPUTS.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = RECEIVED / name
        shutil.copy2(source, target)
        if source.read_bytes() != target.read_bytes():
            raise RuntimeError(f"External input archive is not byte-identical: {name}")
        rows.append({"file": name, "bytes": target.stat().st_size, "sha256": sha256(target)})
    return rows


def unique(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matches = [row for row in rows if all(row.get(key) == value for key, value in criteria.items())]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one row for {criteria}, found {len(matches)}")
    return matches[0]


def reproduce_cross_document_audit(main: str, supplement: str) -> list[dict[str, object]]:
    source_dir = RUN / "figures/source_data"
    figure1 = read_csv(source_dir / "Figure1_source_data.csv")
    figure2 = read_csv(source_dir / "Figure2_source_data.csv")
    figure3 = read_csv(source_dir / "Figure3_source_data.csv")
    figure4 = read_csv(source_dir / "Figure4_source_data.csv")
    figure5 = read_csv(source_dir / "Figure5_source_data.csv")
    rows: list[dict[str, object]] = []

    def add(check: str, passed: bool, detail: str) -> None:
        rows.append({"check": check, "pass": passed, "detail": detail})

    f1 = unique(figure1, panel="d", series="median Jaccard", category="B_ASC")
    f1_value = float(f1["estimate"])
    add("F1d B_ASC median Jaccard source=0.930323", abs(f1_value - 0.9303233364573571) < 1e-12, f"{f1_value:.16g}")
    add(
        "F1d manuscript reports B_ASC median 0.930 and criterion failure",
        "minimum state-median Jaccard was 0.930" in main and "below the unchanged 0.95 criterion" in main,
        "text anchor",
    )

    primary = unique(
        figure2,
        panel="b",
        series="frozen contrast",
        analysis_id="C3A_PRIMARY_C4_MANAGED_VS_NORMAL",
        variant="frozen_base50",
    )
    primary_or = float(primary["odds_ratio"])
    add("F2 primary OR source=0.946653", abs(primary_or - 0.9466531606629468) < 1e-12, f"{primary_or:.16g}")
    add(
        "F2 primary manuscript rounded OR/CI/P aligned",
        "conditional odds ratio was 0.947 (95% confidence interval 0.636-1.410; P=0.787)" in main,
        "text anchor",
    )
    flare = unique(
        figure2,
        panel="b",
        series="frozen contrast",
        analysis_id="C3A_SECONDARY_C3_FLARE_VS_NORMAL",
        variant="frozen_base50",
    )
    flare_q = float(flare["bh_q_across_three_frozen_contrasts"])
    add("F2 flare q source=0.084521 not supported", abs(flare_q - 0.084521309341416) < 1e-12, f"{flare_q:.15g}")

    f3 = unique(figure3, panel="a", analysis_name="primary_base", program_id="IFN_ISG")
    f3_effect = float(f3["effect"])
    add("F3 primary IFN source effect=0.836556", abs(f3_effect - 0.836556476435973) < 1e-12, f"{f3_effect:.15g}")
    add(
        "F3 primary IFN manuscript rounded effect/CI/q aligned",
        "effect 0.837, 95% confidence interval 0.525-1.148; q=2.98 x 10^-6" in main,
        "text anchor",
    )

    f4_metrics = {row["metric"]: row for row in figure4 if row.get("panel") == "d" and row.get("metric")}
    coverage = float(f4_metrics["Coverage"]["observed"])
    conv_precision = float(f4_metrics["B_CONV precision"]["observed"])
    asc_precision = float(f4_metrics["B_ASC precision"]["observed"])
    add("F4d coverage passes", coverage >= 0.8 and abs(coverage - 0.941958041958042) < 1e-12, f"{coverage:.15g} >= 0.8")
    add("F4d B_CONV precision passes", conv_precision >= 0.9 and abs(conv_precision - 0.9964495087110892) < 1e-12, f"{conv_precision:.16g}")
    add("F4d B_ASC precision fails", asc_precision < 0.9 and abs(asc_precision - 0.8852097130242825) < 1e-12, f"{asc_precision:.16g}")
    add(
        "F4d manuscript blocks corrected disease effect",
        "B_ASC precision was 0.885 (<0.90), so no corrected external disease effect was estimated" in main,
        "text anchor",
    )

    f5 = unique(
        figure5,
        panel="D",
        series="ULM_IFN_overlap_depletion",
        branch="m5911_depleted",
        contrast="gse174188_primary",
        regulator="STAT2",
    )
    estimate, low, high, q_value = (float(f5[key]) for key in ("estimate", "ci_low", "ci_high", "q_value"))
    add(
        "F5d discovery STAT2 M5911-depleted CI crosses zero",
        abs(estimate - 0.390657714569951) < 1e-12
        and abs(low + 0.745046177194798) < 1e-12
        and abs(high - 1.5263616063347) < 1e-12
        and abs(q_value - 0.500111148687377) < 1e-12
        and low < 0 < high,
        f"{estimate:.6f} [{low:.6f},{high:.6f}], q={q_value:.6f}",
    )
    add(
        "F5d manuscript aligned with source",
        "ULM slope of 0.391 (95% confidence interval -0.745 to 1.526; q=0.500)" in main,
        "text anchor",
    )
    ifn12 = [row for row in figure5 if row.get("panel") == "D" and row.get("branch") == "frozen_ifn12_depleted"]
    min_low = min(float(row["ci_low"]) for row in ifn12)
    add("F5d 12-gene arm: 6/6 ULM CIs >0", len(ifn12) == 6 and min_low > 0, f"n={len(ifn12)}, min CI low={min_low:.6f}")

    for anchor in (
        "Fig. 1d", "Fig. 2a-d", "Fig. 3a-c", "Fig. 3d", "Fig. 4a,b", "Fig. 4c",
        "Fig. 4d", "Fig. 5a-c", "Fig. 5d", "Fig. 5e", "Supplementary Fig. S4",
        "Supplementary Fig. S7", "Supplementary Fig. S8", "Supplementary Fig. S9",
        "Supplementary Fig. S10",
    ):
        add(f"Cross-ref present: {anchor}", anchor in main, anchor)
    for number in range(1, 6):
        add(f"Figure {number} legend present", f"### Figure {number} |" in main, f"Figure {number}")
    for number in range(1, 11):
        add(
            f"Supplementary Figure S{number} legend present",
            f"## Supplementary Figure S{number} |" in supplement,
            f"S{number}",
        )
    for number, description in (
        (1, "Disease-blind identity stability, two-compartment adjudication and end-to-end B_ASC boundary"),
        (4, "Source-label-defined GSE135779 replication, gene-level coherence and required calibration boundary"),
        (5, "Regulatory convergence, IFN-overlap-depletion ceiling and orthogonal response evidence"),
    ):
        add(f"S5 source map updated: Figure {number}", description in supplement, description)
    add("Discussion landing closes identity-transfer-mechanistic triad", NEW_LANDING in main, "final sentence")
    for phrase in (
        "universally reproducible taxonomy",
        "causal STAT1/STAT2 regulation",
        "predictive biomarker is established",
        "B_ASC is unchanged",
    ):
        add(f"Forbidden overclaim absent: {phrase}", phrase not in main, phrase)

    panel_rows = read_csv(RUN / "03_FINAL_MAIN_PANEL_DECISION_MATRIX.csv")
    replacements = [
        row["panel"]
        for row in panel_rows
        if "source replacement already accepted" in row["final_decision"].lower()
    ]
    add("Main panel inventory is 21 panels", len(panel_rows) == 21, str(len(panel_rows)))
    add(
        "Only historical source replacements are F1d/F4d/F5d",
        replacements == ["Figure 1d", "Figure 4d", "Figure 5d"],
        str(replacements),
    )
    if len(rows) != 54:
        raise RuntimeError(f"Expected 54 reproduced audit rows, found {len(rows)}")
    return rows


def main() -> None:
    parent_status = json.loads((PARENT / "08_FIGURE5_REGULATORY_CEILING_REFREEZE_STATUS.json").read_text(encoding="utf-8"))
    if parent_status["status"] != "SCIENTIFIC_FIGURE5_REGULATORY_CEILING_REFREEZE" or parent_status["failed_checks"]:
        raise RuntimeError("Parent Figure 5 scientific refreeze is not locked")
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed submission package hash changed")

    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "sources").mkdir(exist_ok=True)
    external_manifest = archive_inputs()
    write_csv(RUN / "00_EXTERNAL_INPUT_MANIFEST.csv", external_manifest, ["file", "bytes", "sha256"])

    shutil.copytree(PARENT / "figures", RUN / "figures", dirs_exist_ok=True)
    root_main_path = ROOT / "01_manuscript/Manuscript.md"
    root_supp_path = ROOT / "01_manuscript/Supplementary_Information.md"
    parent_main_path = PARENT / "sources/Manuscript_figure5_regulatory_ceiling.md"
    parent_supp_path = PARENT / "sources/Supplementary_Information_unchanged.md"
    before_main = parent_main_path.read_text(encoding="utf-8")
    before_supp = parent_supp_path.read_text(encoding="utf-8")
    if before_main.count(OLD_LANDING) != 1 or NEW_LANDING in before_main:
        raise RuntimeError("Discussion landing is not in the expected pre-freeze state")
    main = before_main.replace(OLD_LANDING, NEW_LANDING, 1)
    supplement = before_supp
    for old, new in S5_REPLACEMENTS.items():
        if supplement.count(old) != 1 or new in supplement:
            raise RuntimeError(f"Supplementary S5 row is not in the expected state: {old}")
        supplement = supplement.replace(old, new, 1)

    source_main_before = RUN / "sources/Manuscript_before_final_cross_document_freeze.md"
    source_main = RUN / "sources/Manuscript_scientific_presentation_freeze.md"
    source_supp_before = RUN / "sources/Supplementary_Information_before_final_cross_document_freeze.md"
    source_supp = RUN / "sources/Supplementary_Information_scientific_presentation_freeze.md"
    source_main_before.write_text(before_main, encoding="utf-8", newline="\n")
    source_main.write_text(main, encoding="utf-8", newline="\n")
    source_supp_before.write_text(before_supp, encoding="utf-8", newline="\n")
    source_supp.write_text(supplement, encoding="utf-8", newline="\n")

    candidate_main = EXTERNAL_INPUTS["Manuscript_Scientific_Presentation_Freeze_2026-09-08.md"].read_text(encoding="utf-8")
    candidate_supp = EXTERNAL_INPUTS["Supplementary_Information_Scientific_Presentation_Freeze_2026-09-08.md"].read_text(encoding="utf-8")
    if main != candidate_main or supplement != candidate_supp:
        raise RuntimeError("Source-driven reconstruction differs from the external candidate Markdown")

    current_main = root_main_path.read_text(encoding="utf-8")
    current_supp = root_supp_path.read_text(encoding="utf-8")
    if current_main not in (before_main, main) or current_supp not in (before_supp, supplement):
        raise RuntimeError("Root scientific sources diverged from both the parent and integrated states")
    root_main_path.write_text(main, encoding="utf-8", newline="\n")
    root_supp_path.write_text(supplement, encoding="utf-8", newline="\n")

    shutil.copy2(EXTERNAL_INPUTS["FINAL_CLAIM_OWNER_MATRIX_2026-09-08.csv"], RUN / "02_FINAL_CLAIM_OWNER_MATRIX.csv")
    shutil.copy2(EXTERNAL_INPUTS["FINAL_MAIN_PANEL_DECISION_MATRIX_2026-09-08.csv"], RUN / "03_FINAL_MAIN_PANEL_DECISION_MATRIX.csv")
    external_audit = read_csv(EXTERNAL_INPUTS["FINAL_CROSS_DOCUMENT_AUDIT.csv"])
    reproduced_audit = reproduce_cross_document_audit(main, supplement)
    write_csv(RUN / "01_FINAL_CROSS_DOCUMENT_AUDIT_REPRODUCED.csv", reproduced_audit, ["check", "pass", "detail"])

    claim_rows = read_csv(RUN / "02_FINAL_CLAIM_OWNER_MATRIX.csv")
    panel_rows = read_csv(RUN / "03_FINAL_MAIN_PANEL_DECISION_MATRIX.csv")
    asset_rows = []
    for directory in ("figures", "source_data"):
        for candidate in sorted((RUN / "figures" / directory).glob("*")):
            if not candidate.is_file():
                continue
            parent = PARENT / "figures" / directory / candidate.name
            asset_rows.append(
                {
                    "relative_path": candidate.relative_to(ROOT).as_posix(),
                    "bytes": candidate.stat().st_size,
                    "parent_sha256": sha256(parent),
                    "candidate_sha256": sha256(candidate),
                    "unchanged": sha256(parent) == sha256(candidate),
                }
            )
    write_csv(
        RUN / "04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv",
        asset_rows,
        ["relative_path", "bytes", "parent_sha256", "candidate_sha256", "unchanged"],
    )
    edit_rows = [
        {"document": "Manuscript", "object": "Discussion final landing", "operation": "REPLACE_ONCE", "old": OLD_LANDING, "new": NEW_LANDING, "scientific_value_changed": False},
        *[
            {"document": "Supplementary Information", "object": f"Supplementary Table S5 {new.split('|')[1].strip()}", "operation": "REPLACE_ONCE", "old": old, "new": new, "scientific_value_changed": False}
            for old, new in S5_REPLACEMENTS.items()
        ],
    ]
    write_csv(
        RUN / "05_TEXT_EDIT_LEDGER.csv",
        edit_rows,
        ["document", "object", "operation", "old", "new", "scientific_value_changed"],
    )

    replacements = [row["panel"] for row in panel_rows if "source replacement already accepted" in row["final_decision"].lower()]
    checks = {
        "parent_figure5_refreeze_locked": True,
        "source_reconstruction_matches_external_main_md": main == candidate_main,
        "source_reconstruction_matches_external_supplement_md": supplement == candidate_supp,
        "external_audit_54_of_54_pass": len(external_audit) == 54 and all(row["pass"].lower() == "true" for row in external_audit),
        "independent_audit_54_of_54_pass": len(reproduced_audit) == 54 and all(bool(row["pass"]) for row in reproduced_audit),
        "claim_owner_matrix_11_keep": len(claim_rows) == 11 and all(row["status"] == "KEEP" for row in claim_rows),
        "main_panel_matrix_21_keep": len(panel_rows) == 21 and all(row["final_decision"].startswith("KEEP") for row in panel_rows),
        "only_historical_source_replacements_f1d_f4d_f5d": replacements == ["Figure 1d", "Figure 4d", "Figure 5d"],
        "all_45_figure_assets_byte_identical": len(asset_rows) == 45 and all(row["unchanged"] for row in asset_rows),
        "exactly_four_text_edits": len(edit_rows) == 4,
        "root_sources_match_integrated_sources": sha256(root_main_path) == sha256(source_main) and sha256(root_supp_path) == sha256(source_supp),
        "submission_package_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FINAL_CROSS_DOCUMENT_SOURCE_INTEGRATION_RENDER_REQUIRED" if not failed else "FAIL_FINAL_CROSS_DOCUMENT_SOURCE_INTEGRATION",
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
        "historical_source_replacements": replacements,
        "submission_package_sha256": sha256(PACKAGE),
        "submission_package_changed": False,
        "github_release_changed": False,
        "zenodo_changed": False,
        "next_step": "Rebuild editable documents and complete WPS/LibreOffice visual QA before maintenance freeze.",
    }
    (RUN / "06_FINAL_CROSS_DOCUMENT_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (RUN / ".gitignore").write_text(
        "qa/accessibility/\nqa/libreoffice_documents/\nqa/supplement_pagination_audit.json\n"
        "qa/lo_render/\nqa/wps_pages/\nqa/lo_pages/\nqa/final_lo_render/\nqa/lr/\n"
        "qa/final_wps_pages/*/\nqa/final_lo_pages/*/\nqa/parent_wps_pages/*/\n",
        encoding="ascii",
        newline="\n",
    )
    print(json.dumps(status, indent=2))
    if failed:
        raise RuntimeError(f"Final cross-document integration checks failed: {failed}")


if __name__ == "__main__":
    main()
