#!/usr/bin/env python3
"""Gate C2B3-02: map outside-label B-lineage candidates without changing the primary input."""

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


def normalized_entropy(values) -> float:
    import numpy as np

    counts = np.asarray(list(values), dtype=float)
    counts = counts[counts > 0]
    if len(counts) <= 1:
        return 0.0
    probabilities = counts / counts.sum()
    return float(-(probabilities * np.log(probabilities)).sum() / np.log(len(counts)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-h5ad", required=True)
    parser.add_argument("--primary-h5ad", required=True)
    parser.add_argument("--candidate-profiles", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resolutions", default="0.4,0.6,0.8")
    parser.add_argument("--n-neighbors", type=int, default=25)
    parser.add_argument("--n-pcs", type=int, default=30)
    parser.add_argument("--max-reference-cells", type=int, default=0)
    args = parser.parse_args()

    import anndata as ad
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from scipy import sparse
    from sklearn.neighbors import NearestNeighbors

    output = Path(args.output_dir).resolve()
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    resolutions = tuple(float(value) for value in args.resolutions.split(",") if value.strip())
    profiles = pd.read_csv(Path(args.candidate_profiles).resolve())
    candidates = profiles[
        profiles["core_b_identity"].astype(bool) & ~profiles["source_b_lineage"].astype(bool)
    ].copy()
    if candidates.empty:
        raise RuntimeError("No core-B-identity outside-label candidates were found")
    if not candidates["cell_id"].is_unique:
        raise RuntimeError("Candidate cell IDs are not unique")

    primary = ad.read_h5ad(Path(args.primary_h5ad).resolve())
    protected = sorted(column for column in primary.obs.columns if column.lower() in PROTECTED_COLUMNS)
    if protected:
        raise RuntimeError(f"Protected outcome columns found in primary representation: {protected}")
    required_var = {"mean", "std"}
    if not required_var.issubset(primary.var.columns) or "PCs" not in primary.varm:
        raise RuntimeError("Primary representation lacks PCA scaling parameters or loadings")
    for resolution in resolutions:
        if resolution_key(resolution) not in primary.obs:
            raise RuntimeError(f"Primary representation lacks {resolution_key(resolution)}")

    source = ad.read_h5ad(Path(args.source_h5ad).resolve(), backed="r")
    if source.raw is None:
        raise RuntimeError("Full PBMC source lacks raw counts")
    positions = source.obs_names.get_indexer(candidates["cell_id"].astype(str))
    if (positions < 0).any():
        missing = candidates.loc[positions < 0, "cell_id"].head(5).tolist()
        raise RuntimeError(f"Candidates missing from the full PBMC source: {missing}")
    gene_positions = source.raw.var_names.get_indexer(primary.var_names)
    if (gene_positions < 0).any():
        raise RuntimeError("Primary HVGs do not align to the full PBMC raw feature space")

    order = np.argsort(positions)
    inverse = np.argsort(order)
    raw_block = source.raw.X[positions[order]]
    raw_block = raw_block[inverse]
    total_counts = np.asarray(raw_block.sum(axis=1)).ravel().astype(np.float64)
    selected = raw_block[:, gene_positions]
    selected = selected.toarray() if sparse.issparse(selected) else np.asarray(selected)
    selected = np.log1p(selected / np.maximum(total_counts[:, None], 1.0) * 1e4)
    means = primary.var["mean"].to_numpy(dtype=np.float64)
    standard_deviations = primary.var["std"].to_numpy(dtype=np.float64)
    standard_deviations[standard_deviations == 0] = 1.0
    scaled = np.clip((selected - means) / standard_deviations, -10, 10)
    candidate_pca = scaled @ np.asarray(primary.varm["PCs"])[:, : args.n_pcs]
    reference_pca = np.asarray(primary.obsm["X_pca"])[:, : args.n_pcs]

    rng = np.random.default_rng(SEED)
    reference_positions = np.arange(primary.n_obs)
    if 0 < args.max_reference_cells < primary.n_obs:
        selected_reference = []
        libraries = primary.obs["library_uuid"].astype(str).to_numpy()
        for library in sorted(set(libraries)):
            local = np.flatnonzero(libraries == library)
            target = max(5, int(round(args.max_reference_cells * len(local) / len(libraries))))
            selected_reference.extend(rng.choice(local, size=min(target, len(local)), replace=False).tolist())
        reference_positions = np.asarray(sorted(set(selected_reference)), dtype=int)
        if len(reference_positions) > args.max_reference_cells:
            reference_positions = np.sort(
                rng.choice(reference_positions, size=args.max_reference_cells, replace=False)
            )
    reference_obs = primary.obs.iloc[reference_positions]
    reference_pca = reference_pca[reference_positions]

    mapped = candidates[
        [
            "cell_id", "cell_type", "donor_id", "sample_uuid", "library_uuid",
            "Processing_Cohort", "core_b_identity_low_non_b", "non_b_detected_refined",
            "non_b_umi_refined", "core_b_detected_refined", "core_b_umi_refined",
        ]
    ].copy()
    mapped["total_counts"] = total_counts
    mapped["median_neighbor_distance"] = np.nan
    mapped["reference_q95_distance"] = np.nan
    mapped["within_reference_distance_support"] = False
    mapped["mapping_reference_scope"] = ""
    for resolution in resolutions:
        token = str(resolution).replace(".", "_")
        mapped[f"mapped_cluster_r{token}"] = ""
        mapped[f"mapping_confidence_r{token}"] = np.nan
        mapped[f"mapping_entropy_r{token}"] = np.nan

    candidate_libraries = candidates["library_uuid"].astype(str).to_numpy()
    reference_libraries = reference_obs["library_uuid"].astype(str).to_numpy()
    candidate_cohorts = candidates["Processing_Cohort"].astype(str).to_numpy()
    reference_cohorts = reference_obs["Processing_Cohort"].astype(str).to_numpy()
    for library in sorted(set(candidate_libraries)):
        candidate_local = np.flatnonzero(candidate_libraries == library)
        reference_local = np.flatnonzero(reference_libraries == library)
        scope = "same_library"
        if len(reference_local) < 5:
            cohort_values = sorted(set(candidate_cohorts[candidate_local]))
            if len(cohort_values) != 1:
                raise RuntimeError(f"Library {library} spans multiple processing cohorts")
            reference_local = np.flatnonzero(reference_cohorts == cohort_values[0])
            scope = "same_processing_cohort_fallback"
        if len(reference_local) < 5:
            raise RuntimeError(f"No technically matched reference support for library {library}")
        neighbors = min(args.n_neighbors, len(reference_local) - 1)
        model = NearestNeighbors(n_neighbors=neighbors + 1, metric="euclidean", n_jobs=-1)
        model.fit(reference_pca[reference_local])
        reference_distances, _ = model.kneighbors(reference_pca[reference_local])
        reference_median = np.median(reference_distances[:, 1:], axis=1)
        q95 = float(np.quantile(reference_median, 0.95))
        candidate_distances, candidate_neighbors = model.kneighbors(
            candidate_pca[candidate_local], n_neighbors=neighbors
        )
        median_distance = np.median(candidate_distances, axis=1)
        mapped.loc[mapped.index[candidate_local], "median_neighbor_distance"] = median_distance
        mapped.loc[mapped.index[candidate_local], "reference_q95_distance"] = q95
        mapped.loc[mapped.index[candidate_local], "within_reference_distance_support"] = median_distance <= q95
        mapped.loc[mapped.index[candidate_local], "mapping_reference_scope"] = scope
        neighbor_reference_positions = reference_local[candidate_neighbors]
        for resolution in resolutions:
            token = str(resolution).replace(".", "_")
            labels = reference_obs[resolution_key(resolution)].astype(str).to_numpy()[neighbor_reference_positions]
            for row_offset, candidate_index in enumerate(candidate_local):
                values, counts = np.unique(labels[row_offset], return_counts=True)
                winner = int(np.argmax(counts))
                mapped.loc[mapped.index[candidate_index], f"mapped_cluster_r{token}"] = values[winner]
                mapped.loc[mapped.index[candidate_index], f"mapping_confidence_r{token}"] = counts[winner] / counts.sum()
                mapped.loc[mapped.index[candidate_index], f"mapping_entropy_r{token}"] = normalized_entropy(counts)
        print(f"[CANDIDATES] {library}: {len(candidate_local)} candidates ({scope})", flush=True)

    if mapped["median_neighbor_distance"].isna().any():
        missing_libraries = sorted(mapped.loc[mapped["median_neighbor_distance"].isna(), "library_uuid"].astype(str).unique())
        raise RuntimeError(f"Candidate libraries lack reference support: {missing_libraries}")
    mapped["distance_q95_ratio"] = (
        mapped["median_neighbor_distance"] / mapped["reference_q95_distance"]
    )
    mapped.to_csv(output / "07_outside_label_candidate_mapping.csv.gz", index=False, compression="gzip")

    summary_rows = []
    for resolution in resolutions:
        token = str(resolution).replace(".", "_")
        for cluster, group in mapped.groupby(f"mapped_cluster_r{token}", observed=True):
            summary_rows.append(
                {
                    "resolution": resolution,
                    "mapped_cluster": cluster,
                    "n_candidates": len(group),
                    "n_source_labels": group["cell_type"].nunique(),
                    "median_mapping_confidence": group[f"mapping_confidence_r{token}"].median(),
                    "distance_support_fraction": group["within_reference_distance_support"].mean(),
                    "low_non_b_fraction": group["core_b_identity_low_non_b"].mean(),
                }
            )
    mapping_summary = pd.DataFrame(summary_rows)
    mapping_summary.to_csv(output / "08_candidate_mapping_by_cluster.csv", index=False, encoding="utf-8-sig")
    source_summary = (
        mapped.groupby("cell_type", observed=True)
        .agg(
            n_candidates=("cell_id", "size"),
            distance_support_fraction=("within_reference_distance_support", "mean"),
            low_non_b_fraction=("core_b_identity_low_non_b", "mean"),
            median_non_b_detected=("non_b_detected_refined", "median"),
        )
        .reset_index()
        .sort_values("n_candidates", ascending=False)
    )
    source_summary.to_csv(output / "09_candidate_mapping_by_source_label.csv", index=False, encoding="utf-8-sig")

    r04_confidence = mapped["mapping_confidence_r0_4"]
    support_fraction = float(mapped["within_reference_distance_support"].mean())
    low_non_b_fraction = float(mapped["core_b_identity_low_non_b"].mean())
    strong_mapping = bool(support_fraction >= 0.80 and r04_confidence.median() >= 0.70)
    decision = "MAPPING_COMPLETE_NO_AUTOMATIC_APPEND"
    result = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "disease_blind": True,
        "automatic_append_authorized": False,
        "test_mode": bool(args.max_reference_cells > 0),
        "candidates": int(len(mapped)),
        "reference_cells": int(len(reference_obs)),
        "distance_support_fraction": support_fraction,
        "median_r04_mapping_confidence": float(r04_confidence.median()),
        "low_non_b_fraction": low_non_b_fraction,
        "mapping_coherence_threshold_met": strong_mapping,
        "interpretation": (
            "Outside-label candidates remain a sensitivity set. Their mapping does not change "
            "the source-label primary analysis, and only 57 candidates met the prespecified "
            "core-B plus low-non-B rule before projection."
        ),
    }
    (output / "10_CANDIDATE_MAPPING_DECISION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.4), constrained_layout=True)
    axes[0].hist(mapped["mapping_confidence_r0_4"], bins=np.linspace(0, 1, 21), color="#277DA1", edgecolor="white")
    axes[0].set(xlabel="r=0.4 mapping confidence", ylabel="Candidates")
    axes[1].scatter(
        mapped["distance_q95_ratio"], mapped["mapping_confidence_r0_4"],
        s=7, alpha=0.45, color="#4D908E", linewidths=0,
    )
    axes[1].axvline(1, color="#D1495B", linewidth=1)
    axes[1].set(xlabel="Distance / library reference q95", ylabel="r=0.4 confidence")
    proportions = mapping_summary[np.isclose(mapping_summary["resolution"], 0.4)].copy()
    proportions["fraction"] = proportions["n_candidates"] / proportions["n_candidates"].sum()
    axes[2].bar(proportions["mapped_cluster"].astype(str), proportions["fraction"], color="#F9C74F")
    axes[2].set(xlabel="Neutral r=0.4 cluster", ylabel="Candidate fraction")
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
    fig.savefig(figures / "candidate_mapping_audit.png", dpi=280, bbox_inches="tight")
    fig.savefig(figures / "candidate_mapping_audit.pdf", bbox_inches="tight")
    plt.close(fig)

    lines = [
        "# Outside-label B-lineage candidate mapping",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- Core-B-identity candidates mapped: {len(mapped):,}",
        f"- Within-library reference-distance support: {support_fraction:.1%}",
        f"- Median r=0.4 mapping confidence: {r04_confidence.median():.3f}",
        f"- Prespecified low-non-B fraction: {low_non_b_fraction:.1%}",
        "- Disease/outcome fields used: none",
        "- Automatic append to the primary input: not authorized",
        "",
        "Mapping is a sensitivity analysis. Coherent nearest-state placement cannot override",
        "the prespecified fact that most candidates carry non-B signal; primary conclusions",
        "continue to use source B-cell and plasmablast labels after hard QC.",
        "",
    ]
    (output / "10_CANDIDATE_MAPPING_DECISION.md").write_text("\n".join(lines), encoding="utf-8")
    source.file.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
