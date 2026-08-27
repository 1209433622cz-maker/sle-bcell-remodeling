#!/usr/bin/env python3
"""Refit frozen B_ASC composition models after each R1 boundary exchange."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NUMERICAL_REPRODUCTION_TOLERANCE = 5e-4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r1-run-dir", type=Path, required=True)
    parser.add_argument("--gate-c3-dir", type=Path, required=True)
    parser.add_argument("--gate-c3a-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def load_composition_module():
    path = ROOT / "audit_tools" / "phase17_c3_02_fit_frozen_abundance.py"
    spec = importlib.util.spec_from_file_location("round6_c3a", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the frozen composition implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def composition_designs(module, aggregate: pd.DataFrame) -> dict[str, tuple]:
    designs: dict[str, tuple] = {}
    for key in ("primary", "validation", "flare"):
        spec = module.BASE_SPECS[key]
        designs[key] = (module.build_matrix(aggregate, spec, 50), spec)
    primary_samples = set(designs["primary"][0]["sample_uuid"])
    primary_donors = set(designs["primary"][0]["donor_id"])
    validation, spec = designs["validation"]
    keep = ~validation["sample_uuid"].isin(primary_samples) & ~validation["donor_id"].isin(
        primary_donors
    )
    designs["validation_nonoverlap"] = (validation.loc[keep].reset_index(drop=True), spec)
    return designs


def fit_designs(module, aggregate: pd.DataFrame, replicate: int) -> list[dict]:
    rows: list[dict] = []
    for name, (table, spec) in composition_designs(module, aggregate).items():
        fit = module.beta_binomial_fit(
            table,
            spec["columns"],
            spec["analysis_id"],
            f"round6_r1_{name}",
            spec["effect"],
        )
        result = fit["contrast"]
        rows.append(
            {
                "replicate": replicate,
                "analysis": name,
                "effect_term": spec["effect"],
                "n_strata": int(result["n_strata"]),
                "reference_n": int(result["reference_n"]),
                "exposed_n": int(result["exposed_n"]),
                "estimate_log_odds": float(result["estimate_log_odds"]),
                "odds_ratio": float(result["odds_ratio"]),
                "ci_low": float(result["ci_low"]),
                "ci_high": float(result["ci_high"]),
                "p_value": float(result["p_value"]),
                "converged": bool(result["converged"]),
                "hessian_positive_definite": bool(result["hessian_positive_definite"]),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    module = load_composition_module()
    cell = pd.read_csv(
        args.gate_c3_dir.resolve() / "01_unlocked_cell_metadata.csv.gz", low_memory=False
    )
    cell["source_cell_index"] = pd.to_numeric(cell["source_cell_index"]).astype(int)
    if not cell["source_cell_index"].is_unique:
        raise RuntimeError("Gate C3 source-cell indices are not unique")
    source_to_row = pd.Series(
        np.arange(len(cell), dtype=int), index=cell["source_cell_index"].to_numpy()
    )
    base_aggregate = module.aggregate_cells(cell)
    aggregate_index = pd.MultiIndex.from_frame(
        base_aggregate[["sample_uuid", "Processing_Cohort"]].astype(
            {"sample_uuid": str, "Processing_Cohort": float}
        )
    )

    rows = fit_designs(module, base_aggregate, 0)
    frozen = pd.read_csv(
        args.gate_c3a_dir.resolve() / "02_base_and_nonoverlap_contrasts.csv"
    )
    baseline_map = {
        "primary": ("C3A_PRIMARY_C4_MANAGED_VS_NORMAL", "frozen_base50"),
        "validation": ("C3A_VALIDATION_C2_EUROPEAN_FEMALE", "frozen_base50"),
        "validation_nonoverlap": (
            "C3A_VALIDATION_C2_EUROPEAN_FEMALE",
            "exclude_primary_sample_or_donor_overlap",
        ),
        "flare": ("C3A_SECONDARY_C3_FLARE_VS_NORMAL", "frozen_base50"),
    }
    baseline_differences: dict[str, float] = {}
    for result in rows:
        analysis_id, variant = baseline_map[result["analysis"]]
        frozen_row = frozen.loc[
            frozen["analysis_id"].eq(analysis_id) & frozen["variant"].eq(variant)
        ].iloc[0]
        difference = abs(result["odds_ratio"] - float(frozen_row["odds_ratio"]))
        baseline_differences[result["analysis"]] = difference
        if difference > NUMERICAL_REPRODUCTION_TOLERANCE:
            raise RuntimeError(f"Baseline composition did not reproduce for {result['analysis']}")

    for replicate in range(1, 21):
        assignment_path = (
            args.r1_run_dir.resolve()
            / f"replicate_{replicate:03d}"
            / "04_R04_CELL_ASSIGNMENTS.csv.gz"
        )
        assignments = pd.read_csv(
            assignment_path,
            usecols=["source_cell_index", "branch", "reference_state", "mapped_state"],
        )
        changed = assignments.loc[
            assignments["branch"].eq("harmony")
            & assignments["reference_state"].ne(assignments["mapped_state"])
        ].copy()
        changed["raw_row_index"] = pd.to_numeric(changed["source_cell_index"]).map(source_to_row)
        if changed["raw_row_index"].isna().any():
            raise RuntimeError(f"Replicate {replicate} contains unknown source indices")
        changed_indices = changed["raw_row_index"].astype(int).to_numpy()
        metadata = cell.iloc[changed_indices][["sample_uuid", "Processing_Cohort"]].copy()
        metadata["delta_asc"] = np.where(changed["mapped_state"].to_numpy() == "B_ASC", 1, -1)
        delta = metadata.groupby(["sample_uuid", "Processing_Cohort"], observed=True)[
            "delta_asc"
        ].sum()
        adjusted = base_aggregate.copy()
        adjusted["asc_cells"] = adjusted["asc_cells"].to_numpy(int) + delta.reindex(
            aggregate_index, fill_value=0
        ).to_numpy(int)
        if (adjusted["asc_cells"] < 0).any() or (
            adjusted["asc_cells"] > adjusted["total_cells"]
        ).any():
            raise RuntimeError(f"Replicate {replicate} composition adjustment is invalid")
        rows.extend(fit_designs(module, adjusted, replicate))
        print(f"[COMPOSITION] replicate {replicate}/20 fitted", flush=True)

    results = pd.DataFrame(rows)
    results.to_csv(output / "07_COMPOSITION_UNCERTAINTY_RESULTS.csv", index=False)
    sensitivity = results.loc[results["replicate"].gt(0)]
    summary = (
        sensitivity.groupby("analysis", observed=True)
        .agg(
            replicates=("replicate", "nunique"),
            minimum_odds_ratio=("odds_ratio", "min"),
            median_odds_ratio=("odds_ratio", "median"),
            maximum_odds_ratio=("odds_ratio", "max"),
            minimum_p_value=("p_value", "min"),
            maximum_p_value=("p_value", "max"),
            all_converged=("converged", "all"),
            all_hessians_positive=("hessian_positive_definite", "all"),
        )
        .reset_index()
    )
    interval_checks = (
        sensitivity.assign(
            interval_contains_one=lambda frame: (frame["ci_low"] <= 1)
            & (frame["ci_high"] >= 1)
        )
        .groupby("analysis", observed=True)["interval_contains_one"]
        .all()
        .to_dict()
    )
    summary["all_intervals_include_one"] = summary["analysis"].map(interval_checks)
    summary.to_csv(output / "08_COMPOSITION_UNCERTAINTY_SUMMARY.csv", index=False)
    primary = summary.loc[summary["analysis"].eq("primary")].iloc[0]
    checks = {
        "baseline_reproduced_within_numerical_tolerance": max(baseline_differences.values())
        <= NUMERICAL_REPRODUCTION_TOLERANCE,
        "twenty_replicates_per_analysis": bool((summary["replicates"] == 20).all()),
        "all_models_converged": bool(summary["all_converged"].all()),
        "all_hessians_positive": bool(summary["all_hessians_positive"].all()),
        "primary_all_intervals_include_one": bool(primary["all_intervals_include_one"]),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Composition uncertainty checks failed: {checks}")
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_R1_IDENTITY_UNCERTAINTY_COMPOSITION_PROPAGATION",
        "method": "full frozen partition with replicate-specific sampled-cell boundary exchanges; original beta-binomial design and fixed sample eligibility",
        "numerical_reproduction_tolerance": NUMERICAL_REPRODUCTION_TOLERANCE,
        "baseline_absolute_or_differences": baseline_differences,
        "primary": {
            "minimum_odds_ratio": float(primary["minimum_odds_ratio"]),
            "median_odds_ratio": float(primary["median_odds_ratio"]),
            "maximum_odds_ratio": float(primary["maximum_odds_ratio"]),
            "all_intervals_include_one": bool(primary["all_intervals_include_one"]),
        },
        "checks": checks,
        "interpretation": "The primary B_ASC null boundary is retained under observed R1 broad-state assignment exchanges.",
    }
    (output / "09_COMPOSITION_UNCERTAINTY_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
