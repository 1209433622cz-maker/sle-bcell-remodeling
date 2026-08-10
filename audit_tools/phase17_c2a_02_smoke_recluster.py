#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate C2A-02: disease-blind smoke reclustering and diagnostics."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import warnings
from pathlib import Path

SEED = 20260806
RESOLUTIONS = (0.2, 0.4, 0.6, 0.8, 1.0, 1.2)

MODULES = {
    "naive": ["TCL1A", "IGHD", "IL4R", "FCER2", "CCR7"],
    "memory": ["CD27", "AIM2", "GPR183", "TNFRSF13B", "BANK1"],
    "atypical": ["FCRL3", "FCRL5", "ITGAX", "TBX21", "ZEB2"],
    "plasmablast": ["MZB1", "JCHAIN", "XBP1", "SDC1", "CD38"],
    "ifn": ["IFI6", "IFIT1", "IFIT3", "ISG15", "MX1", "OAS1"],
    "platelet": ["PPBP", "PF4", "GNG11", "RGS18"],
    "erythroid": ["HBA1", "HBA2", "HBB"],
}


def gene_lookup(adata):
    mapping = {}
    for idx, row in adata.var.iterrows():
        for value in (idx, row.get("gene_id", ""), row.get("feature_name", "")):
            text = str(value)
            if text and text not in mapping:
                mapping[text] = idx
    return mapping


def score_modules(adata):
    import scanpy as sc

    lookup = gene_lookup(adata)
    used = {}
    for name, genes in MODULES.items():
        var_names = [lookup[g] for g in genes if g in lookup]
        used[name] = [g for g in genes if g in lookup]
        if len(var_names) >= 2:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sc.tl.score_genes(
                    adata,
                    gene_list=var_names,
                    score_name=f"score_{name}",
                    random_state=SEED,
                    use_raw=False,
                )
        else:
            adata.obs[f"score_{name}"] = float("nan")
    return used


def run_scrublet_by_library(adata):
    import numpy as np
    import pandas as pd
    import scrublet as scr

    scores = np.full(adata.n_obs, np.nan, dtype=float)
    predictions = np.zeros(adata.n_obs, dtype=bool)
    rows = []

    libraries = adata.obs["library_uuid"].astype(str)
    for library in sorted(libraries.unique()):
        positions = np.where(libraries.to_numpy() == library)[0]
        subset = adata.X[positions]
        status = "ok"
        threshold = np.nan
        message = ""
        predicted_count = 0

        if len(positions) < 100:
            status = "skipped_lt100_cells"
        else:
            try:
                model = scr.Scrublet(
                    subset,
                    expected_doublet_rate=0.06,
                    random_state=SEED,
                )
                n_prin = max(5, min(30, len(positions) - 2))
                library_scores, library_predictions = model.scrub_doublets(
                    # The Annoy backend can terminate the Windows process instead
                    # of raising a catchable exception. Exact neighbors are fast
                    # enough for the per-library smoke subsets and deterministic.
                    use_approx_neighbors=False,
                    min_counts=2,
                    min_cells=3,
                    min_gene_variability_pctl=85,
                    n_prin_comps=n_prin,
                    svd_solver="randomized",
                    verbose=False,
                )
                scores[positions] = library_scores
                predictions[positions] = library_predictions
                threshold = float(model.threshold_) if model.threshold_ is not None else np.nan
                predicted_count = int(library_predictions.sum())
            except Exception as exc:
                status = "error"
                message = f"{type(exc).__name__}: {exc}"

        rows.append(
            {
                "library_uuid": library,
                "n_cells": len(positions),
                "status": status,
                "threshold": threshold,
                "predicted_doublets": predicted_count,
                "predicted_doublet_fraction": (
                    predicted_count / len(positions) if len(positions) else np.nan
                ),
                "message": message,
            }
        )
        print(
            f"[SCRUBLET] {library}: n={len(positions)}, "
            f"status={status}, predicted={predicted_count}"
        )

    adata.obs["doublet_score"] = scores
    adata.obs["predicted_doublet"] = predictions
    return pd.DataFrame(rows)


def mixing_metrics(representation, obs, label):
    import numpy as np
    import pandas as pd
    from sklearn.neighbors import NearestNeighbors

    n_neighbors = min(16, len(obs))
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
    nn.fit(representation)
    neighbors = nn.kneighbors(return_distance=False)[:, 1:]

    results = []
    for field in ("library_uuid", "Processing_Cohort", "sample_uuid"):
        values = obs[field].astype(str).to_numpy()
        local_same = []
        local_entropy = []
        for i, row in enumerate(neighbors):
            neighbor_values = values[row]
            local_same.append(float((neighbor_values == values[i]).mean()))
            _, counts = np.unique(neighbor_values, return_counts=True)
            probabilities = counts / counts.sum()
            entropy = -float(np.sum(probabilities * np.log(probabilities + 1e-12)))
            normalized = entropy / math.log(max(2, len(counts)))
            local_entropy.append(normalized)
        results.append(
            {
                "representation": label,
                "field": field,
                "mean_same_group_fraction": float(np.mean(local_same)),
                "median_same_group_fraction": float(np.median(local_same)),
                "mean_local_entropy": float(np.mean(local_entropy)),
                "median_local_entropy": float(np.median(local_entropy)),
            }
        )
    return pd.DataFrame(results)


def save_ranked_markers(adata, groupby, output):
    import scanpy as sc

    sc.tl.rank_genes_groups(
        adata,
        groupby=groupby,
        method="wilcoxon",
        use_raw=False,
        pts=True,
    )
    result = sc.get.rank_genes_groups_df(adata, group=None)
    feature_names = adata.var.get("feature_name")
    if feature_names is not None:
        symbol_map = feature_names.astype(str).to_dict()
        result.insert(
            result.columns.get_loc("names") + 1,
            "feature_name",
            result["names"].map(symbol_map),
        )
    result.to_csv(output, index=False, encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-hvg", type=int, default=3000)
    args = parser.parse_args()

    import anndata as ad
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import scanpy as sc
    import scanpy.external as sce

    output = Path(args.output_dir).resolve()
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    sc.settings.seed = SEED
    sc.settings.figdir = figures
    sc.settings.verbosity = 2

    raw = ad.read_h5ad(args.input_h5ad)
    if any(field in raw.obs for field in ("disease", "disease_state")):
        raise RuntimeError("Disease outcome columns are present in working AnnData")

    scrublet_summary = run_scrublet_by_library(raw)
    scrublet_summary.to_csv(
        output / "06_scrublet_library_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Smoke embedding excludes predicted doublets for representation diagnostics only.
    # These calls cannot be frozen because balanced smoke sampling occurred before
    # per-library Scrublet. Gate C2B must call doublets on each complete library.
    keep = ~raw.obs["predicted_doublet"].fillna(False).to_numpy()
    adata = raw[keep].copy()

    sc.pp.filter_genes(adata, min_cells=10)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=min(args.n_hvg, adata.n_vars),
        flavor="seurat",
        batch_key="library_uuid",
    )
    if int(adata.var["highly_variable"].sum()) < 1000:
        raise RuntimeError("Fewer than 1000 HVGs were selected")

    work = adata[:, adata.var["highly_variable"]].copy()
    sc.pp.scale(work, max_value=10)
    sc.tl.pca(
        work,
        n_comps=min(50, work.n_vars - 1),
        svd_solver="randomized",
        random_state=SEED,
    )

    sc.pp.neighbors(
        work,
        n_neighbors=15,
        n_pcs=min(30, work.obsm["X_pca"].shape[1]),
        use_rep="X_pca",
        key_added="unintegrated",
        random_state=SEED,
    )
    sc.tl.umap(
        work,
        neighbors_key="unintegrated",
        random_state=SEED,
    )
    work.obsm["X_umap_unintegrated"] = work.obsm["X_umap"].copy()

    sce.pp.harmony_integrate(
        work,
        key="library_uuid",
        basis="X_pca",
        adjusted_basis="X_pca_harmony",
        random_state=SEED,
    )
    sc.pp.neighbors(
        work,
        n_neighbors=15,
        use_rep="X_pca_harmony",
        key_added="harmony",
        random_state=SEED,
    )
    sc.tl.umap(
        work,
        neighbors_key="harmony",
        random_state=SEED,
    )
    work.obsm["X_umap_harmony"] = work.obsm["X_umap"].copy()

    for resolution in RESOLUTIONS:
        key = f"leiden_harmony_r{str(resolution).replace('.', '_')}"
        sc.tl.leiden(
            work,
            resolution=resolution,
            neighbors_key="harmony",
            key_added=key,
            random_state=SEED,
        )

    # Transfer representations and labels to full-gene log object.
    for key in (
        "X_pca", "X_pca_harmony",
        "X_umap_unintegrated", "X_umap_harmony",
    ):
        adata.obsm[key] = work.obsm[key].copy()

    for resolution in RESOLUTIONS:
        key = f"leiden_harmony_r{str(resolution).replace('.', '_')}"
        adata.obs[key] = work.obs[key].astype(str).to_numpy()

    used_modules = score_modules(adata)
    primary_cluster = "leiden_harmony_r0_6"

    # Batch-mixing diagnostics.
    mixing = pd.concat(
        [
            mixing_metrics(
                work.obsm["X_pca"][:, : min(30, work.obsm["X_pca"].shape[1])],
                work.obs,
                "unintegrated_pca",
            ),
            mixing_metrics(
                work.obsm["X_pca_harmony"][:, : min(30, work.obsm["X_pca_harmony"].shape[1])],
                work.obs,
                "harmony_pca",
            ),
        ],
        ignore_index=True,
    )
    mixing.to_csv(
        output / "07_batch_mixing_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Cluster coverage for every resolution.
    coverage_rows = []
    for resolution in RESOLUTIONS:
        key = f"leiden_harmony_r{str(resolution).replace('.', '_')}"
        for cluster, group in adata.obs.groupby(key, observed=True):
            max_library_fraction = (
                group["library_uuid"].value_counts(normalize=True).iloc[0]
            )
            max_sample_fraction = (
                group["sample_uuid"].value_counts(normalize=True).iloc[0]
            )
            coverage_rows.append(
                {
                    "resolution": resolution,
                    "cluster": cluster,
                    "n_cells": len(group),
                    "n_samples": group["sample_uuid"].nunique(),
                    "n_donors": group["donor_id"].nunique(),
                    "n_libraries": group["library_uuid"].nunique(),
                    "n_processing_cohorts": group["Processing_Cohort"].nunique(),
                    "max_library_fraction": float(max_library_fraction),
                    "max_sample_fraction": float(max_sample_fraction),
                }
            )
    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(
        output / "08_cluster_coverage.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Adjacent-resolution concordance is descriptive only; final state labels also
    # require marker coherence, sample coverage and bootstrap/subsample stability.
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    stability_rows = []
    for lower, upper in zip(RESOLUTIONS[:-1], RESOLUTIONS[1:]):
        lower_key = f"leiden_harmony_r{str(lower).replace('.', '_')}"
        upper_key = f"leiden_harmony_r{str(upper).replace('.', '_')}"
        stability_rows.append(
            {
                "lower_resolution": lower,
                "upper_resolution": upper,
                "lower_n_clusters": int(adata.obs[lower_key].nunique()),
                "upper_n_clusters": int(adata.obs[upper_key].nunique()),
                "adjusted_rand_index": float(
                    adjusted_rand_score(adata.obs[lower_key], adata.obs[upper_key])
                ),
                "normalized_mutual_information": float(
                    normalized_mutual_info_score(
                        adata.obs[lower_key], adata.obs[upper_key]
                    )
                ),
            }
        )
    pd.DataFrame(stability_rows).to_csv(
        output / "08b_resolution_stability.csv",
        index=False,
        encoding="utf-8-sig",
    )

    score_columns = [f"score_{name}" for name in MODULES]
    marker_scores = (
        adata.obs.groupby(primary_cluster, observed=True)[score_columns]
        .agg(["mean", "median", "count"])
    )
    marker_scores.columns = [f"{a}_{b}" for a, b in marker_scores.columns]
    marker_scores.reset_index().to_csv(
        output / "09_marker_scores_by_cluster.csv",
        index=False,
        encoding="utf-8-sig",
    )

    save_ranked_markers(
        adata,
        primary_cluster,
        output / "10_ranked_markers_r06.csv",
    )

    assignments = adata.obs.copy()
    assignments.insert(0, "cell_id", assignments.index)
    assignments.to_csv(
        output / "11_smoke_cell_assignments.csv.gz",
        index=False,
        compression="gzip",
    )

    # Diagnostic figures; no disease outcomes are plotted.
    for basis, prefix in (
        ("umap_unintegrated", "unintegrated"),
        ("umap_harmony", "harmony"),
    ):
        for color in ("Processing_Cohort", primary_cluster, "library_uuid"):
            sc.pl.embedding(
                adata,
                basis=basis,
                color=color,
                show=False,
                frameon=False,
                legend_loc="right margin",
            )
            plt.tight_layout()
            plt.savefig(
                figures / f"{prefix}_{color}.png",
                dpi=220,
                bbox_inches="tight",
            )
            plt.close()

    lookup = gene_lookup(adata)
    marker_order = [
        "MS4A1", "CD79A", "CD74", "TCL1A", "IGHD", "CD27",
        "AIM2", "FCRL5", "ITGAX", "TBX21", "ZEB2",
        "MZB1", "JCHAIN", "XBP1", "SDC1", "IFIT1", "ISG15", "MX1",
        "PPBP", "PF4", "HBA1",
    ]
    marker_var_names = [lookup[g] for g in marker_order if g in lookup]
    if marker_var_names:
        sc.pl.dotplot(
            adata,
            var_names=marker_var_names,
            gene_symbols="feature_name",
            groupby=primary_cluster,
            show=False,
            standard_scale="var",
        )
        plt.savefig(
            figures / "marker_dotplot_r06.png",
            dpi=240,
            bbox_inches="tight",
        )
        plt.close()

    # Save compact HVG object with embeddings and clustering.
    hvg_object = adata[:, adata.var["highly_variable"]].copy()
    hvg_object.uns["phase17_c2a"] = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "disease_blind": True,
        "resolutions": list(RESOLUTIONS),
        "primary_diagnostic_resolution": 0.6,
        "modules_used": used_modules,
        "input_h5ad": str(args.input_h5ad),
    }
    hvg_object.write_h5ad(
        output / "12_smoke_reclustered_hvg.h5ad",
        compression="gzip",
    )

    summary = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "input_cells": int(raw.n_obs),
        "predicted_doublets": int(raw.obs["predicted_doublet"].sum()),
        "embedding_cells": int(adata.n_obs),
        "genes_after_min_cells": int(adata.n_vars),
        "highly_variable_genes": int(adata.var["highly_variable"].sum()),
        "successful_scrublet_libraries": int(
            (scrublet_summary["status"] == "ok").sum()
        ),
        "total_libraries": int(len(scrublet_summary)),
        "doublet_calls_freezable": False,
        "doublet_call_reason": (
            "Balanced smoke sampling preceded per-library Scrublet; "
            "rerun each complete library before final exclusion."
        ),
        "disease_blind": True,
    }
    (output / "13_GATE_C2A_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
