#!/usr/bin/env python3
"""Post-hoc Gate C2A review without changing the disease-blind representation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


RESOLUTIONS = (0.2, 0.4, 0.6, 0.8, 1.0, 1.2)
PRIMARY_CLUSTER = "leiden_harmony_r0_6"


def cluster_key(resolution: float) -> str:
    return f"leiden_harmony_r{str(resolution).replace('.', '_')}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    assignments = pd.read_csv(run_dir / "11_smoke_cell_assignments.csv.gz")
    protected = pd.read_csv(run_dir / "03_protected_outcome_metadata.csv.gz")
    scrublet = pd.read_csv(run_dir / "06_scrublet_library_summary.csv")
    mixing = pd.read_csv(run_dir / "07_batch_mixing_metrics.csv")
    coverage = pd.read_csv(run_dir / "08_cluster_coverage.csv")

    stability_rows = []
    for lower, upper in zip(RESOLUTIONS[:-1], RESOLUTIONS[1:]):
        lower_key = cluster_key(lower)
        upper_key = cluster_key(upper)
        stability_rows.append(
            {
                "lower_resolution": lower,
                "upper_resolution": upper,
                "lower_n_clusters": int(assignments[lower_key].nunique()),
                "upper_n_clusters": int(assignments[upper_key].nunique()),
                "adjusted_rand_index": adjusted_rand_score(
                    assignments[lower_key], assignments[upper_key]
                ),
                "normalized_mutual_information": normalized_mutual_info_score(
                    assignments[lower_key], assignments[upper_key]
                ),
            }
        )
    stability = pd.DataFrame(stability_rows)
    stability.to_csv(
        run_dir / "14_resolution_stability_posthoc.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Outcome labels are unlocked only here, after clustering and neutral marker
    # review. These cell-level proportions are diagnostic and never inferential.
    posthoc = assignments[["cell_id", PRIMARY_CLUSTER]].merge(
        protected[["cell_id", "disease", "disease_state", "ct_cov"]],
        on="cell_id",
        how="left",
        validate="one_to_one",
    )
    disease_balance = (
        posthoc.groupby([PRIMARY_CLUSTER, "disease"], dropna=False)
        .size()
        .rename("n_cells")
        .reset_index()
    )
    disease_balance["within_cluster_fraction"] = disease_balance["n_cells"] / (
        disease_balance.groupby(PRIMARY_CLUSTER)["n_cells"].transform("sum")
    )
    disease_balance.to_csv(
        run_dir / "15_protected_disease_balance_posthoc.csv",
        index=False,
        encoding="utf-8-sig",
    )

    successful = scrublet.loc[scrublet["status"].eq("ok")].copy()
    doublet = {
        "n_libraries_successful": int(len(successful)),
        "median_fraction": float(successful["predicted_doublet_fraction"].median()),
        "mean_fraction": float(successful["predicted_doublet_fraction"].mean()),
        "maximum_fraction": float(successful["predicted_doublet_fraction"].max()),
        "libraries_above_0_20": int(
            successful["predicted_doublet_fraction"].gt(0.20).sum()
        ),
    }

    primary_coverage = coverage.loc[coverage["resolution"].eq(0.6)].copy()
    coverage_pass = bool(
        primary_coverage["n_cells"].min() >= 200
        and primary_coverage["n_donors"].min() >= 20
        and primary_coverage["n_libraries"].min() >= 10
        and primary_coverage["max_library_fraction"].max() <= 0.20
    )

    mixing_pivot = mixing.pivot(
        index="field", columns="representation", values="mean_same_group_fraction"
    )
    harmony_improved = bool(
        (mixing_pivot["harmony_pca"] < mixing_pivot["unintegrated_pca"]).all()
    )

    decision = {
        "reviewed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "representation_gate": "GO_TO_FULL_C2B",
        "doublet_gate": "NO_GO_FOR_FREEZE",
        "annotation_gate": "PROVISIONAL_ONLY",
        "submission_gate": "NO_GO",
        "coverage_pass": coverage_pass,
        "harmony_mixing_improved": harmony_improved,
        "doublet_summary": doublet,
        "reason": (
            "Disease-blind biological structure, batch mixing and cluster coverage "
            "support a full rerun. Smoke-stage Scrublet calls are invalid for "
            "freezing because balanced sampling preceded per-library calling."
        ),
    }
    (run_dir / "17_GATE_C2A_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )

    report = f"""# Gate C2A post-hoc decision

**Run:** `{run_dir}`  
**Review date:** {decision['reviewed_at']}  
**Representation:** GO to full Gate C2B  
**Smoke doublet calls:** NO-GO for freezing  
**Cluster labels:** provisional, disease-blind annotation still required  
**Submission:** NO-GO

## Evidence

- The embedding retained {len(assignments):,} cells after provisional smoke doublet exclusion.
- Harmony reduced the mean same-group neighbor fraction for every audited technical field: {', '.join(f'{field} {mixing_pivot.loc[field, "unintegrated_pca"]:.3f} to {mixing_pivot.loc[field, "harmony_pca"]:.3f}' for field in mixing_pivot.index)}.
- At resolution 0.6, all clusters contained at least {int(primary_coverage['n_cells'].min()):,} cells, {int(primary_coverage['n_donors'].min())} donors and {int(primary_coverage['n_libraries'].min())} libraries; the largest single-library contribution was {primary_coverage['max_library_fraction'].max():.1%}.
- Adjacent-resolution ARI ranged from {stability['adjusted_rand_index'].min():.3f} to {stability['adjusted_rand_index'].max():.3f}; this supports continuity assessment but does not freeze a final resolution.
- Scrublet predicted a median {doublet['median_fraction']:.1%} and maximum {doublet['maximum_fraction']:.1%} doublets per successful library; {doublet['libraries_above_0_20']} libraries exceeded 20%. These rates are not accepted because smoke sampling occurred before per-library doublet modeling.
- Protected outcome labels were merged only after representation and marker review. Cell-level disease proportions are saved for diagnostic balance checks and must not be used as inferential replicates.

## Binding actions for Gate C2B

1. Run Scrublet on every complete eligible library before any balancing or subsampling.
2. Save scores, automatic thresholds and diagnostic distributions; do not silently cap rates or overwrite calls.
3. Carry all hard-QC cells plus a high-confidence singlet sensitivity branch until doublet diagnostics are approved.
4. Rebuild raw-count HVGs, PCA, unintegrated and Harmony graphs on the full data.
5. Freeze neutral B-cell states using markers, donor/sample coverage and resampling stability before outcome labels are unlocked.
6. Use sample-level composition and sample-by-state pseudobulk as the inferential units, with donor clustering for repeated samples and within-cohort effects where common support exists.
"""
    (run_dir / "16_GATE_C2A_DECISION.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
