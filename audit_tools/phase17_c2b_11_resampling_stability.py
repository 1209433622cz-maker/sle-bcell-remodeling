#!/usr/bin/env python3
"""Gate C2B3-01: disease-blind graph-resampling stability diagnostics."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

SEED = 20260806
PROTECTED_COLUMNS = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}


def resolution_key(value: float) -> str:
    return f"leiden_harmony_r{str(value).replace('.', '_')}"


def stratified_sample(groups, fraction: float, rng):
    import numpy as np

    selected = []
    values = groups.astype(str).to_numpy()
    for level in sorted(set(values)):
        positions = np.flatnonzero(values == level)
        target = min(len(positions), max(2, int(round(len(positions) * fraction))))
        selected.extend(rng.choice(positions, size=target, replace=False).tolist())
    return np.asarray(sorted(selected), dtype=int)


def balanced_cap(groups, maximum: int, rng):
    import numpy as np

    if maximum <= 0 or maximum >= len(groups):
        return np.arange(len(groups), dtype=int)
    values = groups.astype(str).to_numpy()
    selected = []
    for level in sorted(set(values)):
        positions = np.flatnonzero(values == level)
        target = max(2, int(round(maximum * len(positions) / len(values))))
        target = min(target, len(positions))
        selected.extend(rng.choice(positions, size=target, replace=False).tolist())
    selected = np.asarray(sorted(set(selected)), dtype=int)
    if len(selected) > maximum:
        selected = np.sort(rng.choice(selected, size=maximum, replace=False))
    elif len(selected) < maximum:
        remaining = np.setdiff1d(np.arange(len(values)), selected, assume_unique=True)
        extra = rng.choice(remaining, size=min(maximum - len(selected), len(remaining)), replace=False)
        selected = np.sort(np.concatenate([selected, extra]))
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resolutions", default="0.4,0.6,0.8")
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--fraction", type=float, default=0.8)
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--n-pcs", type=int, default=30)
    parser.add_argument("--max-cells", type=int, default=0)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd
    import scanpy as sc
    from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score

    if args.replicates < 2:
        raise ValueError("At least two resampling replicates are required")
    if not 0.5 <= args.fraction < 1:
        raise ValueError("--fraction must be in [0.5, 1.0)")
    resolutions = tuple(float(value) for value in args.resolutions.split(",") if value.strip())
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    primary = ad.read_h5ad(Path(args.primary_h5ad).resolve())
    protected = sorted(column for column in primary.obs.columns if column.lower() in PROTECTED_COLUMNS)
    if protected:
        raise RuntimeError(f"Protected outcome columns found: {protected}")
    if "X_pca_harmony" not in primary.obsm:
        raise RuntimeError("Primary representation lacks X_pca_harmony")
    for resolution in resolutions:
        if resolution_key(resolution) not in primary.obs:
            raise RuntimeError(f"Primary representation lacks {resolution_key(resolution)}")

    rng = np.random.default_rng(SEED)
    analysis_positions = balanced_cap(primary.obs["library_uuid"], args.max_cells, rng)
    obs = primary.obs.iloc[analysis_positions].copy()
    embedding = np.asarray(primary.obsm["X_pca_harmony"])[analysis_positions, : args.n_pcs].astype(np.float32)
    test_mode = bool(args.max_cells > 0)
    replicate_rows = []
    cluster_rows = []
    cell_counts = {resolution: np.zeros(len(obs), dtype=np.int16) for resolution in resolutions}
    cell_agreement = {resolution: np.zeros(len(obs), dtype=np.int16) for resolution in resolutions}

    for replicate in range(args.replicates):
        replicate_rng = np.random.default_rng(SEED + 1000 + replicate)
        selected = stratified_sample(obs["library_uuid"], args.fraction, replicate_rng)
        work = ad.AnnData(X=embedding[selected], obs=obs.iloc[selected].copy())
        sc.pp.neighbors(
            work,
            n_neighbors=min(args.n_neighbors, work.n_obs - 1),
            n_pcs=None,
            use_rep="X",
            random_state=SEED + replicate,
        )
        for resolution in resolutions:
            full_key = resolution_key(resolution)
            replicate_key = f"resampled_r{str(resolution).replace('.', '_')}"
            sc.tl.leiden(
                work,
                resolution=resolution,
                key_added=replicate_key,
                random_state=SEED + replicate,
            )
            reference = work.obs[full_key].astype(str).to_numpy()
            observed = work.obs[replicate_key].astype(str).to_numpy()
            contingency = pd.crosstab(
                pd.Series(observed, name="observed"),
                pd.Series(reference, name="reference"),
            )
            mapping = contingency.idxmax(axis=1).to_dict()
            mapped = np.asarray([mapping[value] for value in observed])
            agreement = mapped == reference
            cell_counts[resolution][selected] += 1
            cell_agreement[resolution][selected] += agreement.astype(np.int16)
            replicate_rows.append(
                {
                    "replicate": replicate + 1,
                    "resolution": resolution,
                    "n_cells": int(len(selected)),
                    "reference_clusters": int(len(set(reference))),
                    "resampled_clusters": int(len(set(observed))),
                    "adjusted_rand_index": float(adjusted_rand_score(reference, observed)),
                    "adjusted_mutual_information": float(adjusted_mutual_info_score(reference, observed)),
                    "majority_mapping_agreement": float(agreement.mean()),
                }
            )
            for cluster in sorted(set(reference), key=lambda value: (len(value), value)):
                expected = reference == cluster
                recovered = mapped == cluster
                union = np.logical_or(expected, recovered).sum()
                cluster_rows.append(
                    {
                        "replicate": replicate + 1,
                        "resolution": resolution,
                        "reference_cluster": cluster,
                        "reference_cells": int(expected.sum()),
                        "mapped_cells": int(recovered.sum()),
                        "jaccard": float(np.logical_and(expected, recovered).sum() / union) if union else 0.0,
                        "recall": float(np.logical_and(expected, recovered).sum() / expected.sum()),
                    }
                )
        print(f"[STABILITY] replicate {replicate + 1}/{args.replicates}: {len(selected):,} cells", flush=True)

    replicate_table = pd.DataFrame(replicate_rows)
    cluster_table = pd.DataFrame(cluster_rows)
    replicate_table.to_csv(output / "01_resampling_replicate_metrics.csv", index=False, encoding="utf-8-sig")
    cluster_table.to_csv(output / "02_resampling_cluster_metrics.csv", index=False, encoding="utf-8-sig")
    summary = (
        replicate_table.groupby("resolution", observed=True)
        .agg(
            replicates=("replicate", "nunique"),
            median_ari=("adjusted_rand_index", "median"),
            minimum_ari=("adjusted_rand_index", "min"),
            median_ami=("adjusted_mutual_information", "median"),
            median_mapping_agreement=("majority_mapping_agreement", "median"),
            minimum_mapping_agreement=("majority_mapping_agreement", "min"),
        )
        .reset_index()
    )
    cluster_summary = (
        cluster_table.groupby(["resolution", "reference_cluster"], observed=True)
        .agg(median_jaccard=("jaccard", "median"), minimum_jaccard=("jaccard", "min"), median_recall=("recall", "median"))
        .reset_index()
    )
    summary = summary.merge(
        cluster_summary.groupby("resolution", observed=True)
        .agg(minimum_cluster_median_jaccard=("median_jaccard", "min"), minimum_cluster_median_recall=("median_recall", "min"))
        .reset_index(),
        on="resolution",
        how="left",
    )
    summary.to_csv(output / "03_resampling_resolution_summary.csv", index=False, encoding="utf-8-sig")
    cluster_summary.to_csv(output / "04_resampling_cluster_summary.csv", index=False, encoding="utf-8-sig")

    cell_frames = []
    for resolution in resolutions:
        denominator = cell_counts[resolution]
        stability = np.divide(
            cell_agreement[resolution], denominator,
            out=np.full(len(obs), np.nan, dtype=float), where=denominator > 0,
        )
        cell_frames.append(
            pd.DataFrame(
                {
                    "cell_id": obs.index,
                    "resolution": resolution,
                    "times_sampled": denominator,
                    "times_majority_mapping_agreed": cell_agreement[resolution],
                    "mapping_stability": stability,
                }
            )
        )
    pd.concat(cell_frames, ignore_index=True).to_csv(
        output / "05_resampling_cell_stability.csv.gz", index=False, compression="gzip"
    )
    status = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SOFTWARE_TEST_COMPLETE" if test_mode else "FULL_RESAMPLING_COMPLETE_REVIEW_REQUIRED",
        "disease_blind": True,
        "test_mode": test_mode,
        "source_cells": int(primary.n_obs),
        "analysis_cells": int(len(obs)),
        "replicates": args.replicates,
        "fraction": args.fraction,
        "n_neighbors": args.n_neighbors,
        "n_pcs": args.n_pcs,
        "resolutions": list(resolutions),
        "seed": SEED,
    }
    (output / "06_RESAMPLING_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    primary.file.close() if getattr(primary, "isbacked", False) else None
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
