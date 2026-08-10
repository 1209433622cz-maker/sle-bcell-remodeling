from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "04_submission" / "manuscript_numeric_qc"


def contains_number(text: str, value: str) -> bool:
    pattern = rf"(?<![0-9A-Za-z]){re.escape(value)}(?![0-9A-Za-z])"
    return bool(re.search(pattern, text))


def add_claim(
    rows: list[dict[str, object]],
    manuscript: str,
    claim: str,
    source: str,
    raw_value: float | int,
    rendered_value: str,
) -> None:
    rows.append(
        {
            "claim": claim,
            "source_file": source,
            "source_value": raw_value,
            "manuscript_value": rendered_value,
            "present_in_manuscript": contains_number(manuscript, rendered_value),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-check key manuscript numbers against source CSV outputs.")
    parser.add_argument(
        "--manuscript",
        default=str(PROJECT_ROOT / "01_manuscript" / "manuscript_v5_genome_medicine_targeted.md"),
    )
    parser.add_argument("--date", default="2026-07-27")
    args = parser.parse_args()

    manuscript_path = Path(args.manuscript)
    if not manuscript_path.is_absolute():
        manuscript_path = PROJECT_ROOT / manuscript_path
    manuscript = manuscript_path.read_text(encoding="utf-8")
    rows: list[dict[str, object]] = []

    dataset_source = "03_results/figure1_dataset_overview/tables/figure1_dataset_summary.csv"
    dataset = pd.read_csv(PROJECT_ROOT / dataset_source).iloc[0]
    for column, label in [
        ("source_cells", "Discovery source cells"),
        ("source_donors", "Discovery source donors"),
        ("b_cells", "Discovery B-lineage cells"),
        ("b_donors", "Discovery B-lineage donors"),
        ("b_normal_donors", "Normal donors"),
        ("b_sle_donors", "SLE donors"),
    ]:
        value = int(dataset[column])
        add_claim(rows, manuscript, label, dataset_source, value, f"{value:,}")

    covariate_source = "03_results/figure4_covariate_sensitivity/tables/state_abundance_covariate_models.csv"
    covariate = pd.read_csv(PROJECT_ROOT / covariate_source)
    covariate = covariate[(covariate["model"] == "full_adjusted") & (covariate["error"].fillna("") == "")].set_index("draft_state")
    covariate_specs = [
        ("Naive B II / SLE-enriched naive-like", "Activated SLE-naive full beta", "disease_sle_beta", ".4f"),
        ("Naive B II / SLE-enriched naive-like", "Activated SLE-naive full FDR", "fdr_bh", ".2e"),
        ("Memory B I", "Memory-like I full beta", "disease_sle_beta", ".4f"),
        ("Memory B I", "Memory-like I full FDR", "fdr_bh", ".2e"),
        ("Atypical / ABC-like B", "ABC/APC-like full beta", "disease_sle_beta", ".4f"),
        ("Atypical / ABC-like B", "ABC/APC-like full FDR", "fdr_bh", ".2e"),
    ]
    for state, label, column, fmt in covariate_specs:
        value = float(covariate.loc[state, column])
        add_claim(rows, manuscript, label, covariate_source, value, format(value, fmt))

    clr_source = "03_results/compositional_abundance_sensitivity/tables/compositional_abundance_models.csv"
    clr = pd.read_csv(PROJECT_ROOT / clr_source)
    clr = clr[(clr["analysis"] == "clr") & (clr["model"] == "full_adjusted")].set_index("draft_state")
    clr_specs = [
        ("Naive B II / SLE-enriched naive-like", "Activated SLE-naive CLR beta", "disease_sle_beta", ".3f"),
        ("Naive B II / SLE-enriched naive-like", "Activated SLE-naive CLR FDR", "fdr_bh", ".2e"),
        ("Memory B I", "Memory-like I CLR beta", "disease_sle_beta", ".3f"),
        ("Memory B I", "Memory-like I CLR FDR", "fdr_bh", ".2e"),
        ("Atypical / ABC-like B", "ABC/APC-like CLR beta", "disease_sle_beta", ".3f"),
        ("Atypical / ABC-like B", "ABC/APC-like CLR FDR", "fdr_bh", ".2e"),
    ]
    for state, label, column, fmt in clr_specs:
        value = float(clr.loc[state, column])
        add_claim(rows, manuscript, label, clr_source, value, format(value, fmt))

    validation_source = "03_results/gse135779_bcell_validation/tables/gse135779_donor_program_score_tests.csv"
    validation = pd.read_csv(PROJECT_ROOT / validation_source)
    all_donor = validation[validation["stratum"] == "all"].set_index("metric")
    validation_specs = [
        ("IFN_ISG_score", "GSE135779 IFN delta", "delta_sle_minus_hc", ".4f"),
        ("IFN_ISG_score", "GSE135779 IFN FDR", "fdr", ".2e"),
        ("ZEB2_TBX21_ITGAX_axis_score", "GSE135779 ZEB2 axis delta", "delta_sle_minus_hc", ".4f"),
        ("ZEB2_TBX21_ITGAX_axis_score", "GSE135779 ZEB2 axis FDR", "fdr", ".2e"),
        ("ABC_APC_focus_high_fraction", "GSE135779 high-fraction delta", "delta_sle_minus_hc", ".4f"),
        ("ABC_APC_focus_high_fraction", "GSE135779 high-fraction FDR", "fdr", ".2e"),
    ]
    for metric, label, column, fmt in validation_specs:
        value = float(all_donor.loc[metric, column])
        add_claim(rows, manuscript, label, validation_source, value, format(value, fmt))

    onek_source = "03_results/onek1k_bcell_reference_context/tables/onek1k_bcell_cell_type_counts.csv"
    onek = pd.read_csv(PROJECT_ROOT / onek_source)
    add_claim(rows, manuscript, "OneK1K B-lineage cells", onek_source, int(onek["n_cells"].sum()), f"{int(onek['n_cells'].sum()):,}")
    add_claim(rows, manuscript, "OneK1K donors", onek_source, int(onek["n_donors"].max()), f"{int(onek['n_donors'].max()):,}")

    output = pd.DataFrame(rows)
    output["status"] = output["present_in_manuscript"].map({True: "PASS", False: "FAIL"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / f"{manuscript_path.stem}_numeric_qc_{args.date}.csv"
    md_path = OUT_DIR / f"{manuscript_path.stem}_numeric_qc_{args.date}.md"
    output.to_csv(csv_path, index=False, encoding="utf-8-sig")

    lines = [
        f"# {manuscript_path.stem} Numeric Consistency QC",
        "",
        f"Date: {args.date}",
        "",
        f"- Claims checked: {len(output)}.",
        f"- Passed: {int((output['status'] == 'PASS').sum())}.",
        f"- Failed: {int((output['status'] == 'FAIL').sum())}.",
        "",
        "| Claim | Source value | Manuscript rendering | Status |",
        "|---|---:|---:|---|",
    ]
    for row in output.itertuples(index=False):
        lines.append(f"| {row.claim} | {row.source_value} | {row.manuscript_value} | {row.status} |")
    lines.extend(
        [
            "",
            "The check tests exact rendered values at the manuscript's stated precision. A PASS does not replace contextual scientific review.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(output[["claim", "manuscript_value", "status"]].to_string(index=False))
    if (output["status"] == "FAIL").any():
        raise SystemExit("Numeric consistency QC failed.")


if __name__ == "__main__":
    main()
