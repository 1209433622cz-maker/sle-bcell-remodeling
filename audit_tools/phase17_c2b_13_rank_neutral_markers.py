#!/usr/bin/env python3
"""Gate C2B3-03: full-gene, disease-blind descriptive marker ranking."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

SEED = 20260806
PROTECTED_COLUMNS = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}


def resolution_key(value: float) -> str:
    return f"leiden_harmony_r{str(value).replace('.', '_')}"


def nuisance_gene(symbol: str) -> bool:
    value = str(symbol).upper()
    return bool(
        value.startswith("MT-")
        or re.match(r"^RP[SL][0-9]", value)
        or re.match(r"^HB[ABDEGQZ][0-9]", value)
        or value in {"MALAT1", "NEAT1", "XIST"}
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-h5ad", required=True)
    parser.add_argument("--primary-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resolutions", default="0.4,0.6")
    parser.add_argument("--chunk-size", type=int, default=5000)
    parser.add_argument("--top-per-cluster", type=int, default=100)
    parser.add_argument("--max-cells", type=int, default=0)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd
    from scipy import sparse

    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    resolutions = tuple(float(value) for value in args.resolutions.split(",") if value.strip())
    raw = ad.read_h5ad(Path(args.raw_h5ad).resolve(), backed="r")
    primary = ad.read_h5ad(Path(args.primary_h5ad).resolve())
    protected = sorted(column for column in primary.obs.columns if column.lower() in PROTECTED_COLUMNS)
    if protected:
        raise RuntimeError(f"Protected outcome columns found: {protected}")
    if not raw.obs_names.equals(primary.obs_names):
        raise RuntimeError("Raw-count and primary representation cell order does not align")
    for resolution in resolutions:
        if resolution_key(resolution) not in primary.obs:
            raise RuntimeError(f"Primary representation lacks {resolution_key(resolution)}")

    rng = np.random.default_rng(SEED)
    positions = np.arange(primary.n_obs)
    if 0 < args.max_cells < primary.n_obs:
        libraries = primary.obs["library_uuid"].astype(str).to_numpy()
        selected = []
        for library in sorted(set(libraries)):
            local = np.flatnonzero(libraries == library)
            target = max(2, int(round(args.max_cells * len(local) / len(libraries))))
            selected.extend(rng.choice(local, size=min(target, len(local)), replace=False).tolist())
        positions = np.asarray(sorted(set(selected)), dtype=int)
        if len(positions) > args.max_cells:
            positions = np.sort(rng.choice(positions, size=args.max_cells, replace=False))
    obs = primary.obs.iloc[positions]
    n_genes = raw.n_vars
    symbols = raw.var.get("feature_name", pd.Series(raw.var_names, index=raw.var_names)).astype(str).to_numpy()
    gene_ids = raw.var_names.astype(str).to_numpy()
    cluster_levels = {
        resolution: sorted(obs[resolution_key(resolution)].astype(str).unique(), key=lambda value: (len(value), value))
        for resolution in resolutions
    }
    cluster_codes = {
        resolution: pd.Categorical(
            obs[resolution_key(resolution)].astype(str), categories=cluster_levels[resolution]
        ).codes
        for resolution in resolutions
    }
    sums = {
        resolution: np.zeros((len(cluster_levels[resolution]), n_genes), dtype=np.float64)
        for resolution in resolutions
    }
    detections = {
        resolution: np.zeros((len(cluster_levels[resolution]), n_genes), dtype=np.int64)
        for resolution in resolutions
    }
    cell_counts = {
        resolution: np.bincount(cluster_codes[resolution], minlength=len(cluster_levels[resolution]))
        for resolution in resolutions
    }

    for start in range(0, len(positions), args.chunk_size):
        stop = min(start + args.chunk_size, len(positions))
        block = raw.X[positions[start:stop]]
        if not sparse.issparse(block):
            block = sparse.csr_matrix(block)
        binary = block.copy()
        binary.data = np.ones_like(binary.data)
        for resolution in resolutions:
            local_codes = cluster_codes[resolution][start:stop]
            for cluster_code in np.unique(local_codes):
                mask = local_codes == cluster_code
                sums[resolution][cluster_code] += np.asarray(block[mask].sum(axis=0)).ravel()
                detections[resolution][cluster_code] += np.asarray(binary[mask].sum(axis=0)).ravel().astype(np.int64)
        print(f"[MARKER RANK] {stop:,}/{len(positions):,} cells", flush=True)

    nuisance = np.asarray([nuisance_gene(symbol) for symbol in symbols])
    ranked_frames = []
    for resolution in resolutions:
        total_sum = sums[resolution].sum(axis=0)
        total_detection = detections[resolution].sum(axis=0)
        total_cells = int(cell_counts[resolution].sum())
        for code, cluster in enumerate(cluster_levels[resolution]):
            cluster_sum = sums[resolution][code]
            rest_sum = total_sum - cluster_sum
            cluster_cells = int(cell_counts[resolution][code])
            rest_cells = total_cells - cluster_cells
            cluster_cpm = cluster_sum / max(cluster_sum.sum(), 1) * 1e6
            rest_cpm = rest_sum / max(rest_sum.sum(), 1) * 1e6
            log2fc = np.log2((cluster_cpm + 1) / (rest_cpm + 1))
            cluster_detection = detections[resolution][code] / max(cluster_cells, 1)
            rest_detection = (total_detection - detections[resolution][code]) / max(rest_cells, 1)
            detection_difference = cluster_detection - rest_detection
            score = log2fc * np.maximum(detection_difference, 0)
            eligible = (cluster_detection >= 0.05) & (log2fc > 0.25) & (detection_difference > 0.01)
            eligible_positions = np.flatnonzero(eligible)
            order = eligible_positions[np.argsort(score[eligible_positions])[::-1]][: args.top_per_cluster]
            ranked_frames.append(
                pd.DataFrame(
                    {
                        "resolution": resolution,
                        "cluster": cluster,
                        "rank": np.arange(1, len(order) + 1),
                        "gene_id": gene_ids[order],
                        "gene": symbols[order],
                        "n_cells": cluster_cells,
                        "cluster_cpm": cluster_cpm[order],
                        "rest_cpm": rest_cpm[order],
                        "log2_fold_change": log2fc[order],
                        "cluster_detection_fraction": cluster_detection[order],
                        "rest_detection_fraction": rest_detection[order],
                        "detection_difference": detection_difference[order],
                        "marker_score": score[order],
                        "technical_nuisance": nuisance[order],
                    }
                )
            )
    ranked = pd.concat(ranked_frames, ignore_index=True)

    selected_gene_ids = ranked["gene_id"].drop_duplicates().tolist()
    selected_gene_positions = raw.var_names.get_indexer(selected_gene_ids)
    marker_block = raw.X[positions][:, selected_gene_positions]
    if not sparse.issparse(marker_block):
        marker_block = sparse.csr_matrix(marker_block)
    marker_binary = marker_block.copy()
    marker_binary.data = np.ones_like(marker_binary.data)
    selected_lookup = {gene_id: index for index, gene_id in enumerate(selected_gene_ids)}
    sample_ids = obs["sample_uuid"].astype(str).to_numpy()
    support_rows = []
    for resolution in resolutions:
        labels = obs[resolution_key(resolution)].astype(str).to_numpy()
        group_values = pd.Series(list(zip(labels, sample_ids)))
        group_codes, group_levels = pd.factorize(group_values, sort=True)
        group_indicator = sparse.csr_matrix(
            (np.ones(len(group_codes)), (group_codes, np.arange(len(group_codes)))),
            shape=(len(group_levels), len(group_codes)),
        )
        group_detection = group_indicator @ marker_binary
        group_n_cells = np.bincount(group_codes)
        group_clusters = np.asarray([value[0] for value in group_levels])
        for cluster in cluster_levels[resolution]:
            eligible_groups = (group_clusters == cluster) & (group_n_cells >= 5)
            eligible_count = int(eligible_groups.sum())
            cluster_markers = ranked[
                np.isclose(ranked["resolution"], resolution) & (ranked["cluster"].astype(str) == cluster)
            ]
            for gene_id in cluster_markers["gene_id"]:
                column = selected_lookup[gene_id]
                group_fraction = np.asarray(group_detection[eligible_groups, column].todense()).ravel() / group_n_cells[eligible_groups]
                support_rows.append(
                    {
                        "resolution": resolution,
                        "cluster": cluster,
                        "gene_id": gene_id,
                        "eligible_samples": eligible_count,
                        "samples_with_at_least_5pct_detection": int((group_fraction >= 0.05).sum()),
                        "sample_support_fraction": float((group_fraction >= 0.05).mean()) if eligible_count else 0.0,
                    }
                )
    support = pd.DataFrame(support_rows)
    ranked = ranked.merge(support, on=["resolution", "cluster", "gene_id"], how="left")
    ranked.to_csv(output / "11_ranked_neutral_markers.csv", index=False, encoding="utf-8-sig")
    dictionary = (
        ranked[~ranked["technical_nuisance"]]
        .sort_values(["resolution", "cluster", "marker_score"], ascending=[True, True, False])
        .groupby(["resolution", "cluster"], observed=True)
        .head(20)
        .copy()
    )
    dictionary.to_csv(output / "12_neutral_marker_dictionary.csv", index=False, encoding="utf-8-sig")
    dictionary_summary = (
        dictionary.groupby(["resolution", "cluster"], observed=True)
        .agg(
            markers=("gene", "size"),
            markers_log2fc_ge_05=("log2_fold_change", lambda values: int((values >= 0.5).sum())),
            median_sample_support=("sample_support_fraction", "median"),
            minimum_eligible_samples=("eligible_samples", "min"),
        )
        .reset_index()
    )
    dictionary_summary.to_csv(output / "13_neutral_marker_dictionary_summary.csv", index=False, encoding="utf-8-sig")

    status = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "SOFTWARE_TEST_COMPLETE" if args.max_cells > 0 else "FULL_MARKER_RANKING_COMPLETE_REVIEW_REQUIRED",
        "disease_blind": True,
        "test_mode": bool(args.max_cells > 0),
        "source_cells": int(primary.n_obs),
        "analysis_cells": int(len(positions)),
        "genes": int(raw.n_vars),
        "resolutions": list(resolutions),
        "ranking_is_inferential_test": False,
        "ranking_role": "descriptive neutral-state annotation only",
    }
    (output / "14_MARKER_RANKING_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    raw.file.close()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
