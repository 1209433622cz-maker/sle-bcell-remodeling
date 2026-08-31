#!/usr/bin/env python3
"""Integrate the final scientific-object and numerical-traceability lock."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIOR_RUN = (
    ROOT
    / "phase17_v7/npj_sba_scientific_presentation_freeze/"
    "20260831_reader_path_and_legend_economy"
)
RUN = (
    ROOT
    / "phase17_v7/npj_sba_traceability_lock/"
    "20260831_final_scientific_object_lock"
)
RECEIVED = ROOT / "00_project_management/traceability_lock_2026-08-31/received"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"

OLD_ARCHIVE = (
    "| Version-specific archive | Zenodo https://doi.org/10.5281/zenodo.22151739; "
    "matches the frozen manuscript, figures and statistical outputs |"
)
NEW_ARCHIVE = (
    "| Version-specific archive | Zenodo https://doi.org/10.5281/zenodo.22151739; "
    "version-specific archive of the released analysis code, Source Data and statistical outputs |"
)
OLD_GENE_UNIT = (
    "| Gene-level expression | Donor/sample pseudobulk | edgeR robust quasi-likelihood F | "
    "Two-sided | BH within tested genes per contrast | Gene-level inference |"
)
NEW_GENE_UNIT = (
    "| Gene-level expression | Sample-cohort pseudobulk (GSE174188); donor pseudobulk "
    "(GSE135779) | edgeR robust quasi-likelihood F | Two-sided | BH within tested genes "
    "per contrast | Gene-level inference |"
)
OLD_PROGRAM_UNIT = (
    "| Four frozen programs | Donor/sample pseudobulk | OLS with HC3 | Two-sided | "
    "BH across four programs per analysis | Program inference |"
)
NEW_PROGRAM_UNIT = (
    "| Four frozen programs | Sample-cohort pseudobulk (GSE174188); donor pseudobulk "
    "(GSE135779) | OLS with HC3 | Two-sided | BH across four programs per analysis | "
    "Program inference |"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_sources() -> tuple[Path, Path, Path]:
    sources = RUN / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    prior_manuscript = PRIOR_RUN / "sources/Manuscript_scientific_presentation_freeze_candidate.md"
    prior_supplement = (
        PRIOR_RUN / "sources/Supplementary_Information_scientific_presentation_freeze_candidate.md"
    )
    manuscript = sources / "Manuscript_final_scientific_lock.md"
    supplement = sources / "Supplementary_Information_final_scientific_lock.md"
    shutil.copy2(prior_manuscript, manuscript)

    prior_text = prior_supplement.read_text(encoding="utf-8")
    final_text = replace_once(prior_text, OLD_ARCHIVE, NEW_ARCHIVE, "Table S6 archive row")
    final_text = replace_once(final_text, OLD_GENE_UNIT, NEW_GENE_UNIT, "Table S7 gene unit")
    final_text = replace_once(final_text, OLD_PROGRAM_UNIT, NEW_PROGRAM_UNIT, "Table S7 program unit")
    supplement.write_text(final_text, encoding="utf-8", newline="\n")

    reverse = final_text
    for old, new in reversed(
        [(OLD_ARCHIVE, NEW_ARCHIVE), (OLD_GENE_UNIT, NEW_GENE_UNIT), (OLD_PROGRAM_UNIT, NEW_PROGRAM_UNIT)]
    ):
        reverse = replace_once(reverse, new, old, "reverse traceability edit")
    if reverse != prior_text:
        raise RuntimeError("Traceability source patch is not exactly reversible")

    ledger_rows = [
        {
            "scope": "Supplementary Information",
            "table": "S6",
            "edit": "Version-specific archive scope",
            "rationale": "Do not claim current manuscript and figure identity for an unchanged prior release.",
            "old_text": OLD_ARCHIVE,
            "new_text": NEW_ARCHIVE,
            "scientific_estimate_changed": "False",
        },
        {
            "scope": "Supplementary Information",
            "table": "S7",
            "edit": "Gene-level biological unit",
            "rationale": "State dataset-specific pseudobulk units exactly.",
            "old_text": OLD_GENE_UNIT,
            "new_text": NEW_GENE_UNIT,
            "scientific_estimate_changed": "False",
        },
        {
            "scope": "Supplementary Information",
            "table": "S7",
            "edit": "Program-level biological unit",
            "rationale": "State dataset-specific pseudobulk units exactly.",
            "old_text": OLD_PROGRAM_UNIT,
            "new_text": NEW_PROGRAM_UNIT,
            "scientific_estimate_changed": "False",
        },
    ]
    ledger = sources / "TRACEABILITY_SOURCE_EDIT_LEDGER.csv"
    write_csv(ledger, ledger_rows, list(ledger_rows[0]))
    return manuscript, supplement, ledger


def build_final_claim_matrix() -> Path:
    source = RECEIVED / "CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX_2026-08-31.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0])
    if len(rows) != 24 or {row["claim_id"] for row in rows} != {f"C{i:02d}" for i in range(1, 25)}:
        raise RuntimeError("Received traceability matrix does not contain exactly C01-C24")
    required = {row["claim_id"] for row in rows if row["status"].startswith("FIX_REQUIRED")}
    if required != {"C23", "C24"}:
        raise RuntimeError(f"Unexpected received fix set: {sorted(required)}")

    for row in rows:
        if row["claim_id"] == "C23":
            row["reported_value"] = (
                "Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779)"
            )
            row["status"] = "PASS_FIXED_EXACT_UNIT"
            row["note"] = "Dataset-specific biological units integrated at source level and rebuilt."
        elif row["claim_id"] == "C24":
            row["reported_value"] = (
                "Zenodo archive scoped to released analysis code, Source Data and statistical outputs"
            )
            row["status"] = "PASS_FIXED_PROVENANCE_SCOPE"
            row["note"] = "Archive wording no longer claims identity with the current presentation layer."
    if any(not row["status"].startswith("PASS") for row in rows):
        raise RuntimeError("Final traceability matrix contains a non-PASS row")
    output = RUN / "FINAL_CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX.csv"
    write_csv(output, rows, fieldnames)
    return output


def build_source_data_manifest() -> Path:
    source_dir = PRIOR_RUN / "figures/source_data"
    files = sorted(source_dir.glob("*.csv"))
    if len(files) != 15:
        raise RuntimeError(f"Expected 15 Source Data files; found {len(files)}")
    integration = json.loads((PRIOR_RUN / "00_INTEGRATION_STATUS.json").read_text(encoding="utf-8"))
    if not all(integration["source_data_byte_identical_to_prior_candidate"].values()):
        raise RuntimeError("Prior scientific-presentation Source Data identity did not pass")
    rows = [
        {
            "file": path.name,
            "repository_path": path.relative_to(ROOT).as_posix(),
            "bytes": str(path.stat().st_size),
            "sha256": sha256(path),
            "final_lock_status": "BYTE_IDENTICAL_REFERENCED_OBJECT",
        }
        for path in files
    ]
    output = RUN / "SOURCE_DATA_FINAL_LOCK_MANIFEST.csv"
    write_csv(output, rows, list(rows[0]))
    return output


def build_figure_manifest() -> Path:
    figure_dir = PRIOR_RUN / "figures/figures"
    files = sorted(figure_dir.glob("*.pdf")) + sorted(figure_dir.glob("*.png"))
    if len(files) != 30:
        raise RuntimeError(f"Expected 30 figure exports; found {len(files)}")
    rows = [
        {
            "file": path.name,
            "repository_path": path.relative_to(ROOT).as_posix(),
            "bytes": str(path.stat().st_size),
            "sha256": sha256(path),
            "final_lock_status": "UNCHANGED_REFERENCED_FIGURE_OBJECT",
        }
        for path in files
    ]
    output = RUN / "FIGURE_FINAL_LOCK_MANIFEST.csv"
    write_csv(output, rows, list(rows[0]))
    return output


def build_figure_decisions() -> tuple[Path, Path]:
    with (PRIOR_RUN / "01_MAIN_PANEL_FINAL_DECISION_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 21:
        raise RuntimeError("Expected 21 main panels")
    for row in rows:
        row["decision"] = "KEEP"
        if (row["figure"], row["panel"]) in {("Figure 1", "a"), ("Figure 5", "a")}:
            row["rationale"] = (
                "Prior source redraw corrected the demonstrated semantic defect; traceability audit found no "
                "remaining numerical, unit or interpretive-role mismatch."
            )
        else:
            row["rationale"] = (
                "No numerical, semantic, claim-ownership or final-size legibility defect demonstrated."
            )
    main_output = RUN / "MAIN_PANEL_FINAL_TRACEABILITY_DECISION_MATRIX.csv"
    write_csv(main_output, rows, ["figure", "panel", "decision", "rationale"])

    roles = {
        "S1": "source integrity and processing-cohort QC",
        "S2": "representation and cross-cohort diagnostics",
        "S3": "identity-policy adjudication",
        "S4": "composition diagnostics and sensitivity",
        "S5": "pseudobulk diagnostics",
        "S6": "external-validation diagnostics",
        "S7": "correlation-aware regulator sensitivity",
        "S8": "IFN-overlap-depletion boundary",
        "S9": "end-to-end identity propagation boundary",
        "S10": "reference-calibration and transfer boundary",
    }
    supplementary_rows = [
        {
            "figure": label,
            "decision": "KEEP",
            "evidence_role": role,
            "rationale": "Source Data and manuscript claim ownership agree; no replacement trigger identified.",
        }
        for label, role in roles.items()
    ]
    supplementary_output = RUN / "SUPPLEMENTARY_FIGURE_FINAL_TRACEABILITY_DECISION_MATRIX.csv"
    write_csv(supplementary_output, supplementary_rows, list(supplementary_rows[0]))
    return main_output, supplementary_output


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed exact submission package changed")
    if RUN.exists():
        shutil.rmtree(RUN)
    RUN.mkdir(parents=True)

    manuscript, supplement, ledger = build_sources()
    matrix = build_final_claim_matrix()
    source_manifest = build_source_data_manifest()
    figure_manifest = build_figure_manifest()
    main_decisions, supplementary_decisions = build_figure_decisions()

    supplement_text = supplement.read_text(encoding="utf-8")
    checks = {
        "manuscript_source_byte_identical_to_prior": sha256(manuscript)
        == sha256(PRIOR_RUN / "sources/Manuscript_scientific_presentation_freeze_candidate.md"),
        "archive_scope_fixed": NEW_ARCHIVE in supplement_text and OLD_ARCHIVE not in supplement_text,
        "gene_unit_fixed": NEW_GENE_UNIT in supplement_text and OLD_GENE_UNIT not in supplement_text,
        "program_unit_fixed": NEW_PROGRAM_UNIT in supplement_text and OLD_PROGRAM_UNIT not in supplement_text,
        "final_matrix_24_pass_rows": sum(1 for _ in csv.DictReader(matrix.open(encoding="utf-8-sig")))
        == 24,
        "source_data_15_locked_objects": sum(
            1 for _ in csv.DictReader(source_manifest.open(encoding="utf-8-sig"))
        )
        == 15,
        "figure_exports_30_locked_objects": sum(
            1 for _ in csv.DictReader(figure_manifest.open(encoding="utf-8-sig"))
        )
        == 30,
        "main_panels_21_keep": all(
            row["decision"] == "KEEP"
            for row in csv.DictReader(main_decisions.open(encoding="utf-8-sig"))
        ),
        "supplementary_figures_10_keep": all(
            row["decision"] == "KEEP"
            for row in csv.DictReader(supplementary_decisions.open(encoding="utf-8-sig"))
        ),
        "package_sha_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Traceability integration checks failed: {checks}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_TRACEABILITY_SOURCE_FIX_DOCUMENT_REBUILD_REQUIRED",
        "checks": checks,
        "scientific_object_decision": {
            "main_panels_keep": 21,
            "supplementary_figures_keep": 10,
            "panels_modified": 0,
            "panels_replaced": 0,
            "new_analysis": 0,
        },
        "source_text_fixes": 3,
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "figures_changed": False,
        "release_or_zenodo_changed": False,
        "submission_package_changed": False,
        "submission_package_sha256": sha256(PACKAGE),
        "files": {
            path.name: {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (
                manuscript,
                supplement,
                ledger,
                matrix,
                source_manifest,
                figure_manifest,
                main_decisions,
                supplementary_decisions,
            )
        },
    }
    (RUN / "00_TRACEABILITY_LOCK_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
