#!/usr/bin/env python3
"""Freeze the recommended figure candidates and synchronize manuscript legends."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = (
    ROOT
    / "phase17_v7/npj_sba_main_figure_concept_refinement/20260831_figure1a_figure5a_candidates"
)
BASELINE = (
    ROOT
    / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
)
RECOMMENDED = RUN_DIR / "recommended_scientific_candidate"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} block, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if RECOMMENDED.exists():
        shutil.rmtree(RECOMMENDED)
    figure_dir = RECOMMENDED / "figures"
    source_dir = RECOMMENDED / "source_data"
    manuscript_dir = RECOMMENDED / "sources"
    for directory in (figure_dir, source_dir, manuscript_dir):
        directory.mkdir(parents=True, exist_ok=True)

    selections = {
        "Figure1": RUN_DIR / "Figure1A_workflow_scope",
        "Figure5": RUN_DIR / "Figure5B_quantitative_matrix",
    }
    copied: dict[str, dict[str, str]] = {}
    for figure_name, candidate in selections.items():
        stem = {
            "Figure1": "Figure1_disease_blind_identity_scope",
            "Figure5": "Figure5_regulatory_evidence",
        }[figure_name]
        for extension in ("pdf", "png"):
            source = candidate / "figures" / f"{stem}.{extension}"
            target = figure_dir / source.name
            shutil.copy2(source, target)
        source_csv = candidate / "source_data" / f"{figure_name}_source_data.csv"
        target_csv = source_dir / source_csv.name
        shutil.copy2(source_csv, target_csv)
        baseline_csv = BASELINE / "figures/source_data" / source_csv.name
        if sha256(target_csv) != sha256(baseline_csv):
            raise RuntimeError(f"Recommended {figure_name} Source Data differs from baseline")
        copied[figure_name] = {
            "candidate": candidate.name,
            "pdf_sha256": sha256(figure_dir / f"{stem}.pdf"),
            "png_sha256": sha256(figure_dir / f"{stem}.png"),
            "source_data_sha256": sha256(target_csv),
        }

    baseline_manuscript = BASELINE / "sources/Manuscript.md"
    manuscript = baseline_manuscript.read_text(encoding="utf-8")
    old_figure1 = (
        "a, Study design and evidence hierarchy. GSE174188 B-lineage cells passed hard quality control before construction of a disease-blind B_CONV/B_ASC analysis scaffold and separation into B_ASC composition and B_CONV pseudobulk/program analyses. GSE174188 internal validation and GSE135779 source-label-defined independent replication are displayed in parallel, followed by three interpretation-only evidence classes."
    )
    new_figure1 = (
        "a, Disease-blind workflow and identity scope. The GSE174188 B-lineage input was subjected to disease-blind resampling to define the permissible B_CONV/B_ASC scaffold shown in b-d. The scaffold was then separated into sample-level B_ASC composition and donor-aware B_CONV pseudobulk analyses. The diagram distinguishes the authorized broad-compartment analyses from hard fine-state assignments, which were not authorized."
    )
    old_figure5 = (
        "a, Three parallel interpretation branches for the replicated IFN/ISG program: same-data regulator robustness, curated M5911 response-set concordance and separate GSE23307 perturbational context. Equal branch weight does not imply causal ordering; the bottom boundary states that no causal regulator or unique upstream ligand is established."
    )
    new_figure5 = (
        "a, Quantitative summary of three evidence classes for the replicated IFN/ISG program. STAT1/STAT2 were positive and passed the global 24-test q<0.05 criterion in all six regulator-by-contrast tests; M5911 normalized enrichment scores exceeded 3.0 in all three contrasts; and all 12 genes increased in each of two IFN-beta-exposed donors. The regulator family provides confirmatory observational evidence, M5911 provides orthogonal response-set concordance and GSE23307 provides descriptive perturbational context. Together these layers support observational convergence but not a causal regulator, direct binding or a uniquely upstream ligand."
    )
    manuscript = replace_once(manuscript, old_figure1, new_figure1, "Figure 1a legend")
    manuscript = replace_once(manuscript, old_figure5, new_figure5, "Figure 5a legend")
    candidate_manuscript = manuscript_dir / "Manuscript_figure_refinement_candidate.md"
    candidate_manuscript.write_text(manuscript, encoding="utf-8", newline="\n")

    ledger_path = RECOMMENDED / "01_TEXT_EDIT_LEDGER.csv"
    with ledger_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["location", "decision", "old_text", "new_text", "scientific_estimate_changed"],
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "location": "Figure 1a legend",
                    "decision": "REPLACE_TO_MATCH_WORKFLOW_SCOPE_PANEL",
                    "old_text": old_figure1,
                    "new_text": new_figure1,
                    "scientific_estimate_changed": False,
                },
                {
                    "location": "Figure 5a legend",
                    "decision": "REPLACE_TO_MATCH_QUANTITATIVE_EVIDENCE_MATRIX",
                    "old_text": old_figure5,
                    "new_text": new_figure5,
                    "scientific_estimate_changed": False,
                },
            ]
        )

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_RECOMMENDED_SCIENTIFIC_CANDIDATE_REFROZEN",
        "selection": copied,
        "selection_rationale": {
            "Figure1a": "workflow_scope directly links panels b-d to the broad identity scaffold and downstream biological units without duplicating Figure 4 validation",
            "Figure5a": "quantitative_matrix states coverage, observed result and inferential role without causal arrows or equal-weight ambiguity",
        },
        "panels_retained_without_numeric_change": ["Figure1b-d", "Figure5b-e"],
        "baseline_manuscript_sha256": sha256(baseline_manuscript),
        "candidate_manuscript_sha256": sha256(candidate_manuscript),
        "manuscript_edits": 2,
        "edits_limited_to_legends": True,
        "scientific_estimates_changed": False,
        "exact_submission_package_modified": False,
    }
    (RECOMMENDED / "00_RECOMMENDED_CANDIDATE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
