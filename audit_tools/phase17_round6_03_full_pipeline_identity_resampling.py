#!/usr/bin/env python3
"""Round 6 full-pipeline disease-blind B_CONV/B_ASC resampling."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import re
from datetime import datetime
from pathlib import Path

import anndata as ad
import harmonypy
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score

from phase17_c2b_07_prepare_representation import classify_genes, select_ranked


SEED = 20260806
EXPECTED_INPUT_SHA256 = "DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5"
EXPECTED_INPUT_SHAPE = (150402, 30172)
REFERENCE_KEY = "leiden_harmony_r0_4"
ASC_REFERENCE_CLUSTER = "3"
PROTECTED_EXACT = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}
THRESHOLDS = {
    "median_mapped_ari": 0.95,
    "minimum_mapped_ari": 0.90,
    "median_mapping_agreement": 0.995,
    "minimum_mapping_agreement": 0.990,
    "minimum_state_median_jaccard": 0.95,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", type=Path, required=True)
    parser.add_argument("--reference-h5ad", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--fraction", type=float, default=0.8)
    parser.add_argument("--max-cells", type=int, default=0)
    parser.add_argument("--resolutions", default="0.4,0.6,0.8")
    parser.add_argument("--n-hvg", type=int, default=3000)
    parser.add_argument("--hvg-candidate-pool", type=int, default=7000)
    parser.add_argument("--min-cells", type=int, default=20)
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--unintegrated-pcs", type=int, default=30)
    parser.add_argument("--harmony-max-iter", type=int, default=50)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalized_field(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def balanced_cap(groups: pd.Series, maximum: int, seed: int) -> np.ndarray:
    if maximum <= 0 or maximum >= len(groups):
        return np.arange(len(groups), dtype=int)
    rng = np.random.default_rng(seed)
    values = groups.astype(str).to_numpy()
    selected: list[int] = []
    for level in sorted(set(values)):
        positions = np.flatnonzero(values == level)
        target = max(2, int(round(maximum * len(positions) / len(values))))
        selected.extend(rng.choice(positions, size=min(target, len(positions)), replace=False).tolist())
    selected_array = np.asarray(sorted(set(selected)), dtype=int)
    if len(selected_array) > maximum:
        selected_array = np.sort(rng.choice(selected_array, size=maximum, replace=False))
    elif len(selected_array) < maximum:
        remaining = np.setdiff1d(np.arange(len(values)), selected_array, assume_unique=True)
        extra = rng.choice(remaining, size=maximum - len(selected_array), replace=False)
        selected_array = np.sort(np.concatenate([selected_array, extra]))
    return selected_array


def sample_within_library(groups: pd.Series, fraction: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    values = groups.astype(str).to_numpy()
    selected: list[int] = []
    for level in sorted(set(values)):
        positions = np.flatnonzero(values == level)
        target = min(len(positions), max(2, int(round(len(positions) * fraction))))
        selected.extend(rng.choice(positions, size=target, replace=False).tolist())
    return np.asarray(sorted(selected), dtype=int)


def leiden_key(branch: str, resolution: float) -> str:
    token = str(resolution).replace(".", "_")
    return f"leiden_{branch}_r{token}"


def evaluate_mapping(
    observed: np.ndarray,
    reference: np.ndarray,
    replicate: int,
    branch: str,
    resolution: float,
) -> tuple[dict[str, object], list[dict[str, object]], dict[str, str], np.ndarray]:
    contingency = pd.crosstab(
        pd.Series(observed, name="observed"),
        pd.Series(reference, name="reference"),
    )
    mapping = contingency.idxmax(axis=1).to_dict()
    mapped = np.asarray([mapping[value] for value in observed])
    agreement = mapped == reference
    metric = {
        "replicate": replicate,
        "branch": branch,
        "resolution": resolution,
        "n_cells": len(reference),
        "reference_states": len(set(reference)),
        "observed_clusters": len(set(observed)),
        "mapped_adjusted_rand_index": adjusted_rand_score(reference, mapped),
        "mapped_adjusted_mutual_information": adjusted_mutual_info_score(reference, mapped),
        "majority_mapping_agreement": float(agreement.mean()),
    }
    state_rows: list[dict[str, object]] = []
    for state in ("B_CONV", "B_ASC"):
        expected = reference == state
        recovered = mapped == state
        intersection = np.logical_and(expected, recovered).sum()
        union = np.logical_or(expected, recovered).sum()
        state_rows.append(
            {
                "replicate": replicate,
                "branch": branch,
                "resolution": resolution,
                "reference_state": state,
                "reference_cells": int(expected.sum()),
                "mapped_cells": int(recovered.sum()),
                "jaccard": float(intersection / union) if union else 0.0,
                "recall": float(intersection / expected.sum()) if expected.sum() else 0.0,
            }
        )
    return metric, state_rows, mapping, mapped


def valid_checkpoint(directory: Path, contract: dict[str, object]) -> bool:
    status_path = directory / "00_REPLICATE_STATUS.json"
    required = (
        directory / "01_REPLICATE_METRICS.csv",
        directory / "02_STATE_METRICS.csv",
        directory / "03_SELECTED_HVGS.csv",
        directory / "04_R04_CELL_ASSIGNMENTS.csv.gz",
    )
    if not status_path.exists() or not all(path.exists() for path in required):
        return False
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return status.get("status") == "COMPLETE" and status.get("contract") == contract


def main() -> None:
    args = parse_args()
    if args.replicates < 2:
        raise ValueError("At least two replicates are required")
    if not 0.5 <= args.fraction < 1.0:
        raise ValueError("--fraction must be in [0.5, 1.0)")
    resolutions = tuple(float(value) for value in args.resolutions.split(",") if value.strip())
    if 0.4 not in resolutions:
        raise ValueError("Resolution 0.4 is required for the frozen identity readout")

    input_path = args.input_h5ad.resolve()
    reference_path = args.reference_h5ad.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    test_mode = args.max_cells > 0

    input_sha256 = sha256_file(input_path)
    if input_sha256 != EXPECTED_INPUT_SHA256:
        raise RuntimeError("Hard-QC raw-count H5AD SHA-256 mismatch")
    raw = ad.read_h5ad(input_path)
    reference = ad.read_h5ad(reference_path, backed="r")
    if raw.shape != EXPECTED_INPUT_SHAPE:
        raise RuntimeError(f"Unexpected raw input shape: {raw.shape}")
    protected = sorted(column for column in raw.obs.columns if normalized_field(column) in PROTECTED_EXACT)
    if protected:
        raise RuntimeError(f"Protected outcome columns present: {protected}")
    if REFERENCE_KEY not in reference.obs:
        raise RuntimeError(f"Reference lacks {REFERENCE_KEY}")
    if not raw.obs_names.equals(reference.obs_names):
        raise RuntimeError("Raw input and frozen reference cell order differ")
    if not sparse.issparse(raw.X):
        raise RuntimeError("Expected a sparse raw-count matrix")
    sample_values = raw.X.data
    sampled_values = sample_values[
        np.linspace(0, len(sample_values) - 1, min(200_000, len(sample_values)), dtype=int)
    ]
    if sampled_values.min(initial=0) < 0 or not np.allclose(sampled_values, np.rint(sampled_values)):
        raise RuntimeError("Input matrix is not non-negative integer counts")

    pool_positions = balanced_cap(raw.obs["library_uuid"], args.max_cells, args.seed)
    pool_obs = raw.obs.iloc[pool_positions]
    reference_clusters = reference.obs[REFERENCE_KEY].astype(str).to_numpy()[pool_positions]
    reference_broad = np.where(reference_clusters == ASC_REFERENCE_CLUSTER, "B_ASC", "B_CONV")
    if set(reference_broad) != {"B_CONV", "B_ASC"}:
        raise RuntimeError("Frozen broad reference does not contain both B_CONV and B_ASC")

    contract = {
        "schema_version": 1,
        "disease_blind": True,
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "input_sha256": input_sha256,
        "reference_key": REFERENCE_KEY,
        "asc_reference_cluster": ASC_REFERENCE_CLUSTER,
        "replicates": args.replicates,
        "fraction": args.fraction,
        "max_cells": args.max_cells,
        "resolutions": list(resolutions),
        "n_hvg": args.n_hvg,
        "hvg_candidate_pool": args.hvg_candidate_pool,
        "min_cells": args.min_cells,
        "pca_components": 50,
        "primary_harmony_dimensions": "all_50",
        "unintegrated_pcs": args.unintegrated_pcs,
        "n_neighbors": args.n_neighbors,
        "harmony_max_iter": args.harmony_max_iter,
        "leiden_flavor": "leidenalg",
        "seed": args.seed,
        "thresholds": THRESHOLDS,
        "test_mode": test_mode,
        "software": {
            package: importlib.metadata.version(package)
            for package in ("scanpy", "anndata", "harmonypy", "leidenalg", "scikit-learn")
        },
    }
    (output / "00_RUN_CONTRACT.json").write_text(
        json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    sc.settings.verbosity = 1
    all_metric_frames: list[pd.DataFrame] = []
    all_state_frames: list[pd.DataFrame] = []
    harmony_convergence: list[bool] = []

    for replicate_index in range(args.replicates):
        replicate = replicate_index + 1
        replicate_dir = output / f"replicate_{replicate:03d}"
        replicate_dir.mkdir(parents=True, exist_ok=True)
        replicate_contract = {**contract, "replicate": replicate}
        if valid_checkpoint(replicate_dir, replicate_contract):
            print(f"[RESUME] replicate {replicate}/{args.replicates}", flush=True)
            all_metric_frames.append(pd.read_csv(replicate_dir / "01_REPLICATE_METRICS.csv"))
            all_state_frames.append(pd.read_csv(replicate_dir / "02_STATE_METRICS.csv"))
            checkpoint_status = json.loads(
                (replicate_dir / "00_REPLICATE_STATUS.json").read_text(encoding="utf-8")
            )
            harmony_convergence.append(bool(checkpoint_status["harmony_converged"]))
            continue

        selected_in_pool = sample_within_library(
            pool_obs["library_uuid"], args.fraction, args.seed + 1000 + replicate_index
        )
        selected = pool_positions[selected_in_pool]
        selected_reference = reference_broad[selected_in_pool]
        work_all = raw[selected].copy()
        before_genes = work_all.n_vars
        sc.pp.filter_genes(work_all, min_cells=args.min_cells)
        sc.pp.normalize_total(work_all, target_sum=1e4)
        sc.pp.log1p(work_all)
        candidate_pool = min(max(args.hvg_candidate_pool, args.n_hvg * 2), work_all.n_vars)
        sc.pp.highly_variable_genes(
            work_all,
            n_top_genes=candidate_pool,
            flavor="seurat",
            batch_key="library_uuid",
            inplace=True,
        )
        symbols = work_all.var.get(
            "feature_name", pd.Series(work_all.var_names, index=work_all.var_names)
        ).astype(str)
        gene_classes = classify_genes(symbols)
        for key, values in gene_classes.items():
            work_all.var[key] = values
        nuisance = (
            work_all.var["is_mitochondrial"]
            | work_all.var["is_ribosomal"]
            | work_all.var["is_hemoglobin"]
            | work_all.var["is_stress"]
            | work_all.var["is_cell_cycle"]
            | work_all.var["is_immunoglobulin"]
        ).to_numpy(bool)
        selected_hvgs = select_ranked(work_all.var, ~nuisance, args.n_hvg)
        hvg_table = work_all.var.loc[selected_hvgs].copy()
        hvg_table.insert(0, "gene_index", hvg_table.index.astype(str))
        hvg_table.to_csv(replicate_dir / "03_SELECTED_HVGS.csv", index=False)

        work = work_all[:, selected_hvgs].copy()
        del work_all
        sc.pp.scale(work, max_value=10)
        n_components = min(50, work.n_vars - 1, work.n_obs - 1)
        fit_seed = args.seed + replicate_index
        sc.tl.pca(
            work,
            n_comps=n_components,
            svd_solver="randomized",
            random_state=fit_seed,
        )

        sc.pp.neighbors(
            work,
            n_neighbors=args.n_neighbors,
            n_pcs=min(args.unintegrated_pcs, n_components),
            use_rep="X_pca",
            key_added="unintegrated",
            random_state=fit_seed,
        )
        for resolution in resolutions:
            sc.tl.leiden(
                work,
                resolution=resolution,
                neighbors_key="unintegrated",
                key_added=leiden_key("unintegrated", resolution),
                random_state=fit_seed,
                flavor="leidenalg",
            )

        harmony = harmonypy.run_harmony(
            work.obsm["X_pca"].astype(np.float64),
            work.obs,
            "library_uuid",
            random_state=fit_seed,
            max_iter_harmony=args.harmony_max_iter,
            verbose=False,
        )
        harmony_coordinates = np.asarray(harmony.Z_corr)
        if harmony_coordinates.shape[0] == work.n_obs:
            work.obsm["X_pca_harmony"] = harmony_coordinates
        elif harmony_coordinates.shape[1] == work.n_obs:
            work.obsm["X_pca_harmony"] = harmony_coordinates.T
        else:
            raise RuntimeError(
                f"Harmony coordinate shape does not match cells: {harmony_coordinates.shape}"
            )
        sc.pp.neighbors(
            work,
            n_neighbors=args.n_neighbors,
            use_rep="X_pca_harmony",
            key_added="harmony",
            random_state=fit_seed,
        )
        for resolution in resolutions:
            sc.tl.leiden(
                work,
                resolution=resolution,
                neighbors_key="harmony",
                key_added=leiden_key("harmony", resolution),
                random_state=fit_seed,
                flavor="leidenalg",
            )

        metric_rows: list[dict[str, object]] = []
        state_rows: list[dict[str, object]] = []
        assignment_frames: list[pd.DataFrame] = []
        for branch in ("harmony", "unintegrated"):
            for resolution in resolutions:
                observed = work.obs[leiden_key(branch, resolution)].astype(str).to_numpy()
                metric, states, mapping, mapped = evaluate_mapping(
                    observed, selected_reference, replicate, branch, resolution
                )
                metric_rows.append(metric)
                state_rows.extend(states)
                if np.isclose(resolution, 0.4):
                    assignment_frames.append(
                        pd.DataFrame(
                            {
                                "cell_id": work.obs_names.astype(str),
                                "source_cell_index": work.obs["source_cell_index"].to_numpy(),
                                "branch": branch,
                                "resolution": resolution,
                                "reference_state": selected_reference,
                                "observed_cluster": observed,
                                "mapped_state": mapped,
                                "mapping_agreement": mapped == selected_reference,
                            }
                        )
                    )

        metrics = pd.DataFrame(metric_rows)
        states = pd.DataFrame(state_rows)
        metrics.to_csv(replicate_dir / "01_REPLICATE_METRICS.csv", index=False)
        states.to_csv(replicate_dir / "02_STATE_METRICS.csv", index=False)
        pd.concat(assignment_frames, ignore_index=True).to_csv(
            replicate_dir / "04_R04_CELL_ASSIGNMENTS.csv.gz",
            index=False,
            compression="gzip",
        )
        harmony_objectives = [float(value) for value in harmony.objective_harmony]
        harmony_converged = (
            bool(harmony.check_convergence(1)) if len(harmony_objectives) >= 2 else False
        )
        harmony_convergence.append(harmony_converged)
        replicate_status = {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "status": "COMPLETE",
            "contract": replicate_contract,
            "cells": work.n_obs,
            "genes_before_min_cells": before_genes,
            "genes_after_min_cells": len(symbols),
            "selected_hvgs": len(selected_hvgs),
            "harmony_iterations": max(0, len(harmony_objectives) - 1),
            "harmony_converged": harmony_converged,
        }
        (replicate_dir / "00_REPLICATE_STATUS.json").write_text(
            json.dumps(replicate_status, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        all_metric_frames.append(metrics)
        all_state_frames.append(states)
        print(
            f"[COMPLETE] replicate {replicate}/{args.replicates}: "
            f"{work.n_obs:,} cells x {work.n_vars:,} HVGs",
            flush=True,
        )
        del work, harmony
        gc.collect()

    metrics = pd.concat(all_metric_frames, ignore_index=True)
    states = pd.concat(all_state_frames, ignore_index=True)
    metrics.to_csv(output / "01_ALL_REPLICATE_METRICS.csv", index=False)
    states.to_csv(output / "02_ALL_STATE_METRICS.csv", index=False)
    state_summary = (
        states.groupby(["branch", "resolution", "reference_state"], observed=True)
        .agg(
            median_jaccard=("jaccard", "median"),
            minimum_jaccard=("jaccard", "min"),
            median_recall=("recall", "median"),
            minimum_recall=("recall", "min"),
        )
        .reset_index()
    )
    summary = (
        metrics.groupby(["branch", "resolution"], observed=True)
        .agg(
            replicates=("replicate", "nunique"),
            median_mapped_ari=("mapped_adjusted_rand_index", "median"),
            minimum_mapped_ari=("mapped_adjusted_rand_index", "min"),
            median_mapped_ami=("mapped_adjusted_mutual_information", "median"),
            minimum_mapped_ami=("mapped_adjusted_mutual_information", "min"),
            median_mapping_agreement=("majority_mapping_agreement", "median"),
            minimum_mapping_agreement=("majority_mapping_agreement", "min"),
        )
        .reset_index()
        .merge(
            state_summary.groupby(["branch", "resolution"], observed=True)
            .agg(minimum_state_median_jaccard=("median_jaccard", "min"))
            .reset_index(),
            on=["branch", "resolution"],
            how="left",
        )
    )
    summary.to_csv(output / "03_BRANCH_RESOLUTION_SUMMARY.csv", index=False)
    state_summary.to_csv(output / "04_STATE_SUMMARY.csv", index=False)

    primary = summary.loc[
        summary["branch"].eq("harmony") & np.isclose(summary["resolution"], 0.4)
    ]
    if len(primary) != 1:
        raise RuntimeError("Expected one Harmony r=0.4 summary row")
    primary_row = primary.iloc[0]
    checks = {
        "replicates_complete": bool(int(primary_row["replicates"]) == args.replicates),
        "all_harmony_replicates_converged": bool(
            len(harmony_convergence) == args.replicates and all(harmony_convergence)
        ),
        "median_mapped_ari": bool(primary_row["median_mapped_ari"] >= THRESHOLDS["median_mapped_ari"]),
        "minimum_mapped_ari": bool(primary_row["minimum_mapped_ari"] >= THRESHOLDS["minimum_mapped_ari"]),
        "median_mapping_agreement": bool(primary_row["median_mapping_agreement"] >= THRESHOLDS["median_mapping_agreement"]),
        "minimum_mapping_agreement": bool(primary_row["minimum_mapping_agreement"] >= THRESHOLDS["minimum_mapping_agreement"]),
        "minimum_state_median_jaccard": bool(primary_row["minimum_state_median_jaccard"] >= THRESHOLDS["minimum_state_median_jaccard"]),
    }
    if test_mode:
        decision = "PASS_SOFTWARE_QUALIFICATION_NO_SCIENTIFIC_INTERPRETATION"
    elif args.replicates == 20 and all(checks.values()):
        decision = "PASS_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
    else:
        decision = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "COMPLETE",
        "decision": decision,
        "disease_blind": True,
        "test_mode": test_mode,
        "analysis_pool_cells": len(pool_positions),
        "replicates": args.replicates,
        "fraction": args.fraction,
        "primary_branch": "harmony",
        "primary_resolution": 0.4,
        "harmony_replicates_converged": int(sum(harmony_convergence)),
        "primary_metrics": {
            key: float(primary_row[key])
            for key in (
                "median_mapped_ari",
                "minimum_mapped_ari",
                "median_mapped_ami",
                "minimum_mapped_ami",
                "median_mapping_agreement",
                "minimum_mapping_agreement",
                "minimum_state_median_jaccard",
            )
        },
        "thresholds": THRESHOLDS,
        "checks": checks,
        "interpretation": (
            "Software-test metrics are non-scientific and cannot update the manuscript."
            if test_mode
            else "Passing strengthens end-to-end broad-identity reproducibility; holding narrows the claim to the frozen representation."
        ),
    }
    (output / "05_FULL_PIPELINE_RESAMPLING_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
