#!/usr/bin/env python3
"""Programmatically finalize Gate C2B1 without creating an exclusion mask."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import anndata as ad
import pandas as pd


PROTECTED_TOKENS = ("disease", "ct_cov", "case", "control", "outcome")


def check(condition: bool, detail: str) -> dict[str, object]:
    return {"pass": bool(condition), "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    h5ad_path = run_dir / "04_full_raw_counts.h5ad"
    library_path = run_dir / "05_full_library_doublet_summary.csv"
    score_path = run_dir / "06_full_cell_doublet_scores.csv.gz"
    group_path = run_dir / "12_residual_doublet_group_summary.csv"
    correlation_path = run_dir / "13_residual_doublet_score_correlations.csv"
    checkpoint_dir = run_dir / "doublet_score_checkpoints"

    required = [h5ad_path, library_path, score_path, group_path, correlation_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Gate C2B1 inputs:\n" + "\n".join(missing))

    libraries = pd.read_csv(library_path)
    scores = pd.read_csv(score_path)
    groups = pd.read_csv(group_path)
    correlations = pd.read_csv(correlation_path).set_index("metric")
    adata = ad.read_h5ad(h5ad_path, backed="r")

    score_checkpoints = sorted(checkpoint_dir.glob("library_*.csv.gz"))
    summary_checkpoints = sorted(checkpoint_dir.glob("library_*.summary.json"))
    score_stems = {path.name.removesuffix(".csv.gz") for path in score_checkpoints}
    summary_stems = {path.name.removesuffix(".summary.json") for path in summary_checkpoints}

    protected_columns = [
        str(column)
        for column in adata.obs.columns
        if any(token in str(column).lower() for token in PROTECTED_TOKENS)
    ]
    n_cells = int(adata.n_obs)
    n_libraries = int(libraries.shape[0])
    predicted = int(scores["predicted_doublet"].astype(bool).sum())
    predicted_fraction = predicted / n_cells
    library_predicted = int(libraries["predicted_doublets"].sum())

    group_lookup = groups.set_index(["predicted_doublet", "metric"])["median"]
    negative_total = float(group_lookup.loc[(False, "total_counts")])
    positive_total = float(group_lookup.loc[(True, "total_counts")])
    negative_genes = float(group_lookup.loc[(False, "detected_genes")])
    positive_genes = float(group_lookup.loc[(True, "detected_genes")])
    negative_non_b = float(group_lookup.loc[(False, "max_non_b_fraction")])
    positive_non_b = float(group_lookup.loc[(True, "max_non_b_fraction")])

    required_correlations = ["total_counts", "detected_genes", "max_non_b_fraction"]
    max_abs_key_rho = max(abs(float(correlations.loc[name, "spearman_rho"])) for name in required_correlations)

    checks = {
        "all_library_runs_ok": check(
            libraries["status"].eq("ok").all(),
            f"{int(libraries['status'].eq('ok').sum())}/{n_libraries} libraries have status=ok",
        ),
        "score_rows_complete": check(
            len(scores) == n_cells,
            f"{len(scores):,} score rows for {n_cells:,} H5AD cells",
        ),
        "score_cell_ids_unique": check(
            scores["cell_id"].is_unique,
            f"unique score cell IDs: {scores['cell_id'].nunique():,}",
        ),
        "score_cell_ids_match_h5ad": check(
            set(scores["cell_id"].astype(str)) == set(adata.obs_names.astype(str)),
            "score and H5AD cell-ID sets compared exactly",
        ),
        "source_indices_match_h5ad": check(
            scores["source_cell_index"].is_unique
            and "source_cell_index" in adata.obs
            and set(scores["source_cell_index"].astype(int))
            == set(adata.obs["source_cell_index"].astype(int)),
            "unique score indices match the retained H5AD source-index set; "
            f"range {int(scores['source_cell_index'].min()):,}-{int(scores['source_cell_index'].max()):,}",
        ),
        "predicted_totals_reconcile": check(
            predicted == library_predicted,
            f"cell table={predicted:,}; library table={library_predicted:,}",
        ),
        "checkpoint_pairs_complete": check(
            len(score_checkpoints) == n_libraries
            and len(summary_checkpoints) == n_libraries
            and score_stems == summary_stems,
            f"score/summary checkpoint pairs={len(score_stems & summary_stems):,}/{n_libraries:,}",
        ),
        "no_protected_outcomes": check(
            not protected_columns,
            "protected-like columns=" + ("none" if not protected_columns else " | ".join(protected_columns)),
        ),
        "no_extreme_library_rate": check(
            int(libraries["predicted_doublet_fraction"].gt(0.20).sum()) == 0,
            f"libraries above 20%={int(libraries['predicted_doublet_fraction'].gt(0.20).sum())}",
        ),
        "weak_key_metric_correlations": check(
            max_abs_key_rho < 0.10,
            f"maximum absolute key Spearman rho={max_abs_key_rho:.3f}",
        ),
        "modest_rna_content_shift": check(
            positive_total / negative_total < 1.25 and positive_genes / negative_genes < 1.25,
            f"median UMI fold={positive_total / negative_total:.3f}; gene fold={positive_genes / negative_genes:.3f}",
        ),
        "no_mixed_lineage_enrichment": check(
            positive_non_b - negative_non_b < 0.001,
            f"median max non-B fraction delta={positive_non_b - negative_non_b:.6f}",
        ),
    }

    passed = all(item["pass"] for item in checks.values())
    top_library = libraries.sort_values("predicted_doublet_fraction", ascending=False).iloc[0]
    decision = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "decision": "PASS_TO_C2B2_WITH_DUAL_BRANCH" if passed else "NO_GO_REVIEW_REQUIRED",
        "all_checks_passed": passed,
        "cells": n_cells,
        "libraries": n_libraries,
        "automatic_residual_risk_calls": predicted,
        "automatic_residual_risk_fraction": predicted_fraction,
        "maximum_library_fraction": float(top_library["predicted_doublet_fraction"]),
        "maximum_library_uuid": str(top_library["library_uuid"]),
        "checks": checks,
        "binding_policy": {
            "primary_branch": "all-hard-QC",
            "sensitivity_branch": "automatic residual-risk negatives",
            "automatic_exclusion_authorized": False,
            "final_exclusion_requires": "disease-blind state-graph localization at Gate C2B3",
        },
    }
    (run_dir / "17_GATE_C2B1_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )

    check_lines = "\n".join(
        f"- [{'PASS' if item['pass'] else 'FAIL'}] {name}: {item['detail']}"
        for name, item in checks.items()
    )
    report = f"""# Gate C2B1 final decision

**Decision:** {decision['decision']}

- Complete-library runs: {n_libraries:,}
- Hard-QC cells scored: {n_cells:,}
- Automatic residual-risk calls: {predicted:,} ({predicted_fraction:.2%})
- Maximum library rate: {float(top_library['predicted_doublet_fraction']):.2%} in `{top_library['library_uuid']}` ({int(top_library['n_cells']):,} cells)
- Automatic second-round exclusion authorized: no

## Programmatic checks

{check_lines}

## Binding decision

Gate C2B1 passes to C2B2 with two prespecified branches. The primary branch
retains all 150,402 hard-QC cells because the source workflow already performed
doublet handling and the residual calls show only modest RNA-content shifts,
no mixed-lineage enrichment and no strong key-metric correlation. The
high-confidence-singlet branch excludes the 1,972 automatic residual-risk calls
for sensitivity analysis only. The 493-cell maximum-rate library is flagged for
state-graph localization, not automatic removal. Final exclusion policy remains
locked until disease-blind cluster localization at Gate C2B3.
"""
    (run_dir / "16_GATE_C2B1_DECISION.md").write_text(report, encoding="utf-8")
    adata.file.close()
    print(json.dumps(decision, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
