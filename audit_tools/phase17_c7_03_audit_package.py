from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


RUN_REL = Path("phase17_v7/gateC7/20260820_manuscript_figure_integration")
FINAL_DECISION = "PASS_GATE_C7_MANUSCRIPT_AND_FIVE_FIGURE_SCIENTIFIC_FREEZE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the Gate C7 manuscript and five-figure package.")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    run_dir = root / RUN_REL
    manuscript_path = root / "01_manuscript/manuscript_v9_gateC7_submission_scientific_draft_2026-08-20.md"
    proposal_path = root / "01_manuscript/research_proposal_v16_gateC7_completed_2026-08-20.md"
    legends_path = root / "01_manuscript/main_figure_legends_v9_gateC7_2026-08-20.md"
    manuscript = manuscript_path.read_text(encoding="utf-8")
    proposal = proposal_path.read_text(encoding="utf-8")
    legends = legends_path.read_text(encoding="utf-8")

    checks: dict[str, dict[str, object]] = {}

    def record(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"pass": bool(passed), "detail": detail}

    decision_sources = {
        "C2B4": (
            root / "phase17_v7/gateC2B4/20260815_two_level_state_repair/06_GATE_C2B4_ADVISOR_DECISION.json",
            "PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED",
        ),
        "C3A": (
            root / "phase17_v7/gateC3A/20260815_frozen_abundance/09_GATE_C3A_ADVISOR_DECISION.json",
            "NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM",
        ),
        "C4B": (
            root / "phase17_v7/gateC4B/20260815_edger_transcription/15_GATE_C4B_ADVISOR_DECISION.json",
            "PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION",
        ),
        "C5B": (
            root / "phase17_v7/gateC5B/20260815_gse135779_external_validation/17_GATE_C5B_ADVISOR_DECISION.json",
            "PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION",
        ),
        "C6B": (
            root / "phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json",
            "PASS_GATE_C6B_UPPER_Q1_REGULATORY_FRAMING_AUTHORIZED_NONCAUSAL",
        ),
    }
    observed_decisions = {key: read_json(path).get("decision") for key, (path, _) in decision_sources.items()}
    decision_pass = all(observed_decisions[key] == expected for key, (_, expected) in decision_sources.items())
    record("frozen_gate_chain", decision_pass, "; ".join(f"{key}={value}" for key, value in observed_decisions.items()))

    results_block = manuscript.split("## Results", 1)[1].split("## Discussion", 1)[0]
    result_headings = [line for line in results_block.splitlines() if line.startswith("### ")]
    record("five_result_sections", len(result_headings) == 5, f"found {len(result_headings)} Results subsections")
    record("five_figure_legends", legends.count("### Figure ") == 5 and manuscript.count("### Figure ") == 5, "five legends in standalone file and manuscript")

    stale_phrases = [
        "pending Gate C6B",
        "no regulator effect has been inspected",
        "if subsequently supported",
        "The next analytical question",
        "regulatory effects remain locked",
    ]
    stale_hits = [phrase for phrase in stale_phrases if phrase.lower() in manuscript.lower() or phrase.lower() in proposal.lower()]
    record("no_stale_c6b_language", not stale_hits, f"hits={stale_hits}")

    required_boundaries = [
        "without establishing a discrete subtype, causal regulator or unique upstream stimulus",
        "do not identify a unique initiating ligand or establish causation in SLE",
        "do not prove that STAT1 or STAT2 initiated the in vivo state",
    ]
    normalized_manuscript = " ".join(manuscript.split())
    boundary_hits = [phrase in normalized_manuscript for phrase in required_boundaries]
    record("noncausal_boundaries_explicit", all(boundary_hits), f"required boundary passages={sum(boundary_hits)}/3")
    record("gene_label_permutation_wording", "gene-label permutations" in manuscript and "phenotype-label permutations" not in manuscript, "M5911 null described as gene-label permutations")

    prohibited_active_names = [
        "10_GSE23307_GENE_SAMPLE_EXPRESSION",
        "11_GSE23307_PAIRED_GENE_EFFECTS",
        "12_GSE23307_DONOR_PROGRAM_EFFECTS",
        "13_MSIGDB_M5911_PRERANKED_GSEA",
        "14_GATE_C6B4_ORTHOGONAL_DECISION",
    ]
    prohibited_hits = [name for name in prohibited_active_names if name in manuscript or name in legends]
    record("no_superseded_gse23307_citation", not prohibited_hits, f"active manuscript/legends hits={prohibited_hits}")

    regulators = pd.read_csv(root / "phase17_v7/gateC6B/20260815_regulatory_evidence/01_CONFIRMATORY_REGULATOR_RESULTS.csv")
    core = regulators.loc[regulators["regulator"].isin(["STAT1", "STAT2"])]
    core_pass = len(core) == 6 and (core["slope"] > 0).all() and (core["q_value_global24"] < 0.05).all()
    record("core_regulator_claim", core_pass, f"positive and global-q<0.05 rows={int(((core['slope'] > 0) & (core['q_value_global24'] < 0.05)).sum())}/6")

    c6_audit = read_json(root / "phase17_v7/gateC6B/20260815_regulatory_evidence/24_GATE_C6B_FINAL_AUDIT.json")
    robustness_pass = bool(c6_audit["checks"]["core_influence_pass"] and c6_audit["checks"]["resampling_row_counts_reconcile"])
    record("core_target_robustness", robustness_pass, "leave-one-target and 100x80% resampling audited by Gate C6B")

    gsea = pd.read_csv(root / "phase17_v7/gateC6B/20260815_regulatory_evidence/19_MSIGDB_M5911_PRERANKED_GSEA.csv")
    expected_nes = [3.186802649601297, 3.0498612816254838, 3.5271419267951707]
    gsea_pass = len(gsea) == 3 and all(abs(a - b) < 1e-12 for a, b in zip(gsea["normalized_enrichment_score"], expected_nes, strict=True)) and (gsea["permutations"] == 10000).all()
    record("m5911_values", gsea_pass, f"NES={','.join(f'{value:.3f}' for value in gsea['normalized_enrichment_score'])}; permutations=10000")

    donor = pd.read_csv(root / "phase17_v7/gateC6B/20260815_regulatory_evidence/18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv")
    donor_pass = list(donor["positive_genes"]) == [12, 12] and all(abs(a - b) < 1e-12 for a, b in zip(donor["mean_paired_log2p1_effect"], [3.293570512080079, 3.665668905432541], strict=True))
    record("gse23307_corrected_values", donor_pass, "HI1=3.294 and HI2=3.666; 12/12 genes positive in each")

    claim_table = pd.read_csv(run_dir / "02_CLAIM_NUMBER_CROSSWALK.csv")
    figure_table = pd.read_csv(run_dir / "03_FIGURE_SOURCE_CROSSWALK.csv")
    numeric_table = pd.read_csv(run_dir / "04_MANUSCRIPT_NUMERIC_SOURCE.csv")
    record("claim_crosswalk", len(claim_table) == 14 and claim_table["claim_id"].is_unique, f"{len(claim_table)} unique claims")
    record("figure_crosswalk", list(figure_table["figure"]) == [f"Figure{i}" for i in range(1, 6)], "Figures 1-5 map to frozen gates and source data")
    record("numeric_source_crosswalk", numeric_table["metric_id"].is_unique and len(numeric_table) >= 16, f"{len(numeric_table)} unique numeric sources")

    figure_checks = []
    source_checks = []
    expected_stems = [
        "Figure1_disease_blind_identity_scope",
        "Figure2_sample_level_composition",
        "Figure3_gse174188_bconv_transcription",
        "Figure4_independent_ifn_replication",
        "Figure5_regulatory_evidence",
    ]
    for index, stem in enumerate(expected_stems, start=1):
        png = run_dir / "figures" / f"{stem}.png"
        pdf = run_dir / "figures" / f"{stem}.pdf"
        with Image.open(png) as image:
            width, height = image.size
        figure_checks.append(png.stat().st_size > 300_000 and pdf.stat().st_size > 20_000 and width >= 4000 and height >= 3000)
        source_path = run_dir / "source_data" / f"Figure{index}_source_data.csv"
        source_checks.append(source_path.stat().st_size > 100 and len(pd.read_csv(source_path)) > 0)
    record("figure_files_and_dimensions", all(figure_checks), f"{sum(figure_checks)}/5 have PDF>20KB, PNG>300KB and at least 4000x3000 pixels")
    record("figure_source_data", all(source_checks), f"{sum(source_checks)}/5 nonempty source-data files")

    figure4_source = pd.read_csv(run_dir / "source_data/Figure4_source_data.csv")
    figure4_pass = len(figure4_source.loc[figure4_source["panel"].eq("c")]) == 4410 and len(figure4_source.loc[figure4_source["panel"].eq("d_source")]) == 8 and len(figure4_source.loc[figure4_source["panel"].eq("d_donor")]) == 1
    record("figure4_interface", figure4_pass, "4,410 shared genes, 8 source-label omissions and one donor-LOO summary")

    figure5_source = pd.read_csv(run_dir / "source_data/Figure5_source_data.csv")
    active_figure5 = pd.read_csv(root / "phase17_v7/gateC6B/20260815_regulatory_evidence/21_FIGURE5_SOURCE_DATA.csv")
    same_shape_columns = figure5_source.shape == active_figure5.shape and list(figure5_source.columns) == list(active_figure5.columns)
    numeric_columns = list(figure5_source.select_dtypes(include="number").columns)
    object_columns = [column for column in figure5_source.columns if column not in numeric_columns]
    numeric_equal = same_shape_columns and all(
        np.allclose(figure5_source[column], active_figure5[column], rtol=1e-12, atol=1e-14, equal_nan=True)
        for column in numeric_columns
    )
    object_equal = same_shape_columns and all(
        figure5_source[column].fillna("<NA>").equals(active_figure5[column].fillna("<NA>"))
        for column in object_columns
    )
    record("figure5_active_source", numeric_equal and object_equal, "Gate C7 Figure 5 source values equal corrected active Gate C6B source within serialization tolerance")

    proposal_completed = proposal.count("**Status:** completed") >= 3 and "**Status:** completed; Gate C6B passed" in proposal
    record("proposal_all_aims_completed", proposal_completed, "Aims 1-4 are recorded as completed")
    record("gse23307_reference_verified", "10.4049/jimmunol.0902314" in manuscript and "185:5888-5899" in manuscript, "PMID 20956346 journal citation represented")

    passed = all(item["pass"] for item in checks.values())
    decision = FINAL_DECISION if passed else "HOLD_GATE_C7_AUDIT_FAILURE"
    payload = {
        "created_at": "2026-08-20",
        "decision": decision,
        "checks": checks,
        "active_manuscript": manuscript_path.relative_to(root).as_posix(),
        "active_research_proposal": proposal_path.relative_to(root).as_posix(),
        "active_figures": [f"{RUN_REL.as_posix()}/figures/{stem}.pdf" for stem in expected_stems],
        "claim_boundary": "convergent observational IFN-centred regulatory evidence; not causal and not a unique upstream stimulus",
        "next_stage": "Gate C8 journal-specific submission package, reference verification, authorship/declarations and rendered document QA" if passed else "repair failed Gate C7 checks before submission packaging",
    }
    (run_dir / "06_GATE_C7_FINAL_AUDIT.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "# Gate C7 final scientific audit",
        "",
        f"## `{decision}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- [{'PASS' if value['pass'] else 'FAIL'}] `{key}`: {value['detail']}" for key, value in checks.items())
    lines.extend(
        [
            "",
            "## Frozen interpretation",
            "",
            "The active package authorizes independently replicated IFN/ISG remodeling within a disease-blind broad conventional-B compartment and convergent observational IFN-centred regulatory evidence. It does not authorize a hard IFN-high subtype, a unique upstream ligand, direct TF binding or causation.",
            "",
            "## Next stage",
            "",
            payload["next_stage"],
        ]
    )
    (run_dir / "06_GATE_C7_FINAL_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    manifest_paths = sorted(
        [path for path in run_dir.rglob("*") if path.is_file() and path.name != "07_INTEGRITY_MANIFEST.csv"]
        + [
            manuscript_path,
            proposal_path,
            legends_path,
            root / "audit_tools/phase17_c7_01_build_main_figures.py",
            root / "audit_tools/phase17_c7_02_integrate_manuscript.py",
            root / "audit_tools/phase17_c7_03_audit_package.py",
            root / "audit_tools/run_6013RP_phase17_gateC7_commit.ps1",
            root / "00_project_management/action_record_2026-08-20_gateC7_manuscript_five_figure_integration.md",
            root / "00_project_management/next_stage_decision_2026-08-20_gateC8_journal_submission_package.md",
        ],
        key=lambda path: path.as_posix(),
    )
    manifest = pd.DataFrame(
        [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in manifest_paths
        ]
    )
    manifest.to_csv(run_dir / "07_INTEGRITY_MANIFEST.csv", index=False)
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
