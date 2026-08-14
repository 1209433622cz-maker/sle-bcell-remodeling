#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate C2B2-02: fit full disease-blind B-cell representation branches."""

from __future__ import annotations

import argparse
import datetime as dt
import gc
import itertools
import json
import math
from pathlib import Path

SEED = 20260806
BRANCH_SCHEMA_VERSION = 2
DEFAULT_RESOLUTIONS = (0.2, 0.4, 0.6, 0.8, 1.0, 1.2)

BRANCHES = (
    {
        "name": "primary_all_cells",
        "var_flag": "hvg_primary",
        "cell_policy": "all_hard_qc",
        "run_unintegrated": True,
        "run_umap": True,
        "filename": "06_primary_all_cells_representation.h5ad",
    },
    {
        "name": "singlet_sensitivity",
        "var_flag": "hvg_primary",
        "cell_policy": "residual_risk_negative",
        "run_unintegrated": False,
        "run_umap": False,
        "filename": "07_singlet_sensitivity_representation.h5ad",
    },
    {
        "name": "isg_excluded",
        "var_flag": "hvg_isg_excluded",
        "cell_policy": "all_hard_qc",
        "run_unintegrated": False,
        "run_umap": False,
        "filename": "08_isg_excluded_representation.h5ad",
    },
)


def resolution_key(resolution: float) -> str:
    return f"leiden_harmony_r{str(resolution).replace('.', '_')}"


def neighbor_mixing(distance_matrix, obs, representation: str):
    import numpy as np
    import pandas as pd

    matrix = distance_matrix.tocsr()
    rows = []
    for field in ("library_uuid", "sample_uuid", "Processing_Cohort"):
        values = obs[field].astype(str).to_numpy()
        global_groups = len(np.unique(values))
        same = np.full(len(obs), np.nan, dtype=np.float32)
        entropy = np.full(len(obs), np.nan, dtype=np.float32)
        for index in range(len(obs)):
            start, stop = matrix.indptr[index], matrix.indptr[index + 1]
            neighbors = matrix.indices[start:stop]
            neighbors = neighbors[neighbors != index]
            if len(neighbors) == 0:
                continue
            neighbor_values = values[neighbors]
            same[index] = np.mean(neighbor_values == values[index])
            _, counts = np.unique(neighbor_values, return_counts=True)
            probabilities = counts / counts.sum()
            raw_entropy = -np.sum(probabilities * np.log(probabilities + 1e-12))
            maximum_local_groups = max(2, min(len(neighbors), global_groups))
            entropy[index] = raw_entropy / math.log(maximum_local_groups)
        rows.append(
            {
                "representation": representation,
                "field": field,
                "n_evaluable_cells": int(np.isfinite(same).sum()),
                "mean_same_group_fraction": float(np.nanmean(same)),
                "median_same_group_fraction": float(np.nanmedian(same)),
                "mean_local_entropy": float(np.nanmean(entropy)),
                "median_local_entropy": float(np.nanmedian(entropy)),
            }
        )
    return pd.DataFrame(rows)


def bridge_centroid_distances(obs, representation, representation_name: str):
    import numpy as np
    import pandas as pd

    n_dims = min(30, representation.shape[1])
    columns = [f"PC{i + 1}" for i in range(n_dims)]
    table = pd.DataFrame(representation[:, :n_dims], index=obs.index, columns=columns)
    table["sample_uuid"] = obs["sample_uuid"].astype(str).to_numpy()
    table["Processing_Cohort"] = obs["Processing_Cohort"].astype(str).to_numpy()
    centroids = table.groupby(["sample_uuid", "Processing_Cohort"], observed=True)[columns].mean()
    counts = obs.groupby(
        [obs["sample_uuid"].astype(str), obs["Processing_Cohort"].astype(str)], observed=True
    ).size()
    rows = []
    for sample_uuid, sample_centroids in centroids.groupby(level=0, observed=True):
        cohorts = list(sample_centroids.index.get_level_values(1))
        if len(cohorts) < 2:
            continue
        vectors = sample_centroids.to_numpy()
        for left, right in itertools.combinations(range(len(cohorts)), 2):
            a, b = vectors[left], vectors[right]
            denom = np.linalg.norm(a) * np.linalg.norm(b)
            cosine_distance = 1.0 - float(np.dot(a, b) / denom) if denom else np.nan
            rows.append(
                {
                    "representation": representation_name,
                    "sample_uuid": sample_uuid,
                    "cohort_a": cohorts[left],
                    "cohort_b": cohorts[right],
                    "cells_a": int(counts.loc[(sample_uuid, cohorts[left])]),
                    "cells_b": int(counts.loc[(sample_uuid, cohorts[right])]),
                    "euclidean_centroid_distance": float(np.linalg.norm(a - b)),
                    "cosine_centroid_distance": cosine_distance,
                }
            )
    return pd.DataFrame(rows)


def compact_representation(work, branch, resolutions, harmony_max_iter: int):
    import anndata as ad

    compact = ad.AnnData(X=None, obs=work.obs.copy(), var=work.var.copy())
    for key in ("X_pca", "X_pca_harmony", "X_umap_unintegrated", "X_umap_harmony"):
        if key in work.obsm:
            compact.obsm[key] = work.obsm[key].copy()
    if "PCs" in work.varm:
        compact.varm["PCs"] = work.varm["PCs"].copy()
    if "pca" in work.uns:
        compact.uns["pca"] = work.uns["pca"]
    compact.uns["phase17_c2b2_branch"] = {
        "schema_version": BRANCH_SCHEMA_VERSION,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "disease_blind": True,
        "branch": branch["name"],
        "cell_policy": branch["cell_policy"],
        "var_flag": branch["var_flag"],
        "resolutions": list(resolutions),
        "integration_covariate": "library_uuid",
        "harmony_max_iter": harmony_max_iter,
        "harmony_iterations": work.uns["phase17_harmony"]["iterations"],
        "harmony_converged": work.uns["phase17_harmony"]["converged"],
        "harmony_final_relative_objective_change": work.uns["phase17_harmony"][
            "final_relative_objective_change"
        ],
        "seed": SEED,
    }
    return compact


def validate_checkpoint(path: Path, branch_name: str, resolutions, harmony_max_iter: int | None = None):
    import anndata as ad

    if not path.exists():
        return None
    try:
        checkpoint = ad.read_h5ad(path)
        metadata = checkpoint.uns.get("phase17_c2b2_branch", {})
        required = {resolution_key(value) for value in resolutions}
        harmony_diagnostics_valid = (
            harmony_max_iter is None
            or (
                metadata.get("harmony_max_iter", 0) >= harmony_max_iter
                and metadata.get("harmony_iterations") is not None
                and metadata.get("harmony_converged") is not None
            )
        )
        if (
            metadata.get("branch") == branch_name
            and metadata.get("schema_version") == BRANCH_SCHEMA_VERSION
            and metadata.get("disease_blind") is True
            and required.issubset(checkpoint.obs.columns)
            and "X_pca_harmony" in checkpoint.obsm
            and harmony_diagnostics_valid
        ):
            return checkpoint
    except Exception:
        return None
    return None


def fit_branch(
    prepared,
    branch,
    output: Path,
    resolutions,
    n_neighbors: int,
    n_pcs: int,
    harmony_max_iter: int,
):
    import scanpy as sc
    import harmonypy
    import numpy as np

    output_path = output / branch["filename"]
    checkpoint = validate_checkpoint(
        output_path, branch["name"], resolutions, harmony_max_iter
    )
    primary_metrics = (
        output / "10_primary_neighbor_mixing.csv",
        output / "11_primary_bridge_centroid_distances.csv",
    )
    if checkpoint is not None and (
        branch["name"] != "primary_all_cells" or all(path.exists() for path in primary_metrics)
    ):
        print(f"[RESUME] valid branch checkpoint: {output_path}", flush=True)
        return checkpoint

    cell_mask = None
    if branch["cell_policy"] == "residual_risk_negative":
        cell_mask = ~prepared.obs["residual_doublet_auto_call"].to_numpy(bool)
    else:
        cell_mask = slice(None)
    var_mask = prepared.var[branch["var_flag"]].to_numpy(bool)
    work = prepared[cell_mask, var_mask].copy()
    if work.n_obs < 100 or work.n_vars < 100:
        raise RuntimeError(f"Branch {branch['name']} is too small: {work.shape}")

    print(f"[FIT] {branch['name']}: {work.n_obs:,} cells x {work.n_vars:,} HVGs", flush=True)
    sc.pp.scale(work, max_value=10)
    n_components = min(50, work.n_vars - 1, work.n_obs - 1)
    sc.tl.pca(
        work,
        n_comps=n_components,
        svd_solver="randomized",
        random_state=SEED,
    )
    use_pcs = min(n_pcs, work.obsm["X_pca"].shape[1])

    mixing_frames = []
    bridge_frames = []
    if branch["run_unintegrated"]:
        sc.pp.neighbors(
            work,
            n_neighbors=n_neighbors,
            n_pcs=use_pcs,
            use_rep="X_pca",
            key_added="unintegrated",
            random_state=SEED,
        )
        mixing_frames.append(
            neighbor_mixing(work.obsp["unintegrated_distances"], work.obs, "unintegrated_pca")
        )
        bridge_frames.append(
            bridge_centroid_distances(work.obs, work.obsm["X_pca"], "unintegrated_pca")
        )
        if branch["run_umap"]:
            sc.tl.umap(work, neighbors_key="unintegrated", random_state=SEED)
            work.obsm["X_umap_unintegrated"] = work.obsm["X_umap"].copy()

    print(f"[HARMONY] {branch['name']} by library_uuid", flush=True)
    harmony_out = harmonypy.run_harmony(
        work.obsm["X_pca"].astype(np.float64),
        work.obs,
        "library_uuid",
        random_state=SEED,
        max_iter_harmony=harmony_max_iter,
    )
    work.obsm["X_pca_harmony"] = harmony_out.Z_corr.T
    objectives = [float(value) for value in harmony_out.objective_harmony]
    if len(objectives) >= 2:
        final_relative_change = (
            (objectives[-2] - objectives[-1]) / abs(objectives[-2])
            if objectives[-2] != 0
            else float("nan")
        )
        converged = bool(harmony_out.check_convergence(1))
    else:
        final_relative_change = float("nan")
        converged = False
    work.uns["phase17_harmony"] = {
        "iterations": max(0, len(objectives) - 1),
        "converged": converged,
        "final_relative_objective_change": final_relative_change,
        "epsilon_harmony": float(harmony_out.epsilon_harmony),
        "objective_harmony": objectives,
    }
    sc.pp.neighbors(
        work,
        n_neighbors=n_neighbors,
        use_rep="X_pca_harmony",
        key_added="harmony",
        random_state=SEED,
    )
    if branch["run_unintegrated"]:
        mixing_frames.append(
            neighbor_mixing(work.obsp["harmony_distances"], work.obs, "harmony_pca")
        )
        bridge_frames.append(
            bridge_centroid_distances(work.obs, work.obsm["X_pca_harmony"], "harmony_pca")
        )
    if branch["run_umap"]:
        sc.tl.umap(work, neighbors_key="harmony", random_state=SEED)
        work.obsm["X_umap_harmony"] = work.obsm["X_umap"].copy()

    for resolution in resolutions:
        key = resolution_key(resolution)
        sc.tl.leiden(
            work,
            resolution=resolution,
            neighbors_key="harmony",
            key_added=key,
            random_state=SEED,
            flavor="leidenalg",
        )
        print(f"[LEIDEN] {branch['name']} r={resolution:g}: {work.obs[key].nunique()} clusters", flush=True)

    if mixing_frames:
        import pandas as pd

        pd.concat(mixing_frames, ignore_index=True).to_csv(
            output / "10_primary_neighbor_mixing.csv", index=False, encoding="utf-8-sig"
        )
        nonempty_bridge = [frame for frame in bridge_frames if not frame.empty]
        if nonempty_bridge:
            pd.concat(nonempty_bridge, ignore_index=True).to_csv(
                output / "11_primary_bridge_centroid_distances.csv",
                index=False,
                encoding="utf-8-sig",
            )
        else:
            pd.DataFrame(
                columns=[
                    "representation", "sample_uuid", "cohort_a", "cohort_b",
                    "cells_a", "cells_b", "euclidean_centroid_distance",
                    "cosine_centroid_distance",
                ]
            ).to_csv(output / "11_primary_bridge_centroid_distances.csv", index=False)

    compact = compact_representation(work, branch, resolutions, harmony_max_iter)
    print(f"[CHECKPOINT] {output_path}", flush=True)
    compact.write_h5ad(output_path, compression="gzip")
    del work
    gc.collect()
    return compact


def build_diagnostics(branches, output: Path, resolutions):
    import numpy as np
    import pandas as pd
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    primary = branches["primary_all_cells"]
    coverage_rows = []
    doublet_rows = []
    for resolution in resolutions:
        key = resolution_key(resolution)
        for cluster, group in primary.obs.groupby(key, observed=True):
            library_fraction = group["library_uuid"].astype(str).value_counts(normalize=True)
            sample_fraction = group["sample_uuid"].astype(str).value_counts(normalize=True)
            residual_calls = group["residual_doublet_auto_call"].to_numpy(bool)
            coverage_rows.append(
                {
                    "resolution": resolution,
                    "cluster": str(cluster),
                    "n_cells": len(group),
                    "n_samples": int(group["sample_uuid"].nunique()),
                    "n_donors": int(group["donor_id"].nunique()),
                    "n_libraries": int(group["library_uuid"].nunique()),
                    "n_processing_cohorts": int(group["Processing_Cohort"].nunique()),
                    "max_library_fraction": float(library_fraction.iloc[0]),
                    "max_sample_fraction": float(sample_fraction.iloc[0]),
                }
            )
            doublet_rows.append(
                {
                    "resolution": resolution,
                    "cluster": str(cluster),
                    "n_cells": len(group),
                    "residual_auto_calls": int(residual_calls.sum()),
                    "residual_auto_call_fraction": float(residual_calls.mean()),
                    "median_residual_doublet_score": float(group["residual_doublet_score"].median()),
                    "max_library_fraction": float(library_fraction.iloc[0]),
                }
            )
    pd.DataFrame(coverage_rows).to_csv(
        output / "12_primary_cluster_coverage.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(doublet_rows).to_csv(
        output / "13_residual_risk_localization.csv", index=False, encoding="utf-8-sig"
    )

    concordance_rows = []
    for resolution in resolutions:
        key = resolution_key(resolution)
        reference = primary.obs[key].astype(str)
        for branch_name, branch in branches.items():
            if branch_name == "primary_all_cells":
                continue
            common = reference.index.intersection(branch.obs_names)
            left = reference.reindex(common)
            right = branch.obs.loc[common, key].astype(str)
            concordance_rows.append(
                {
                    "resolution": resolution,
                    "comparison": f"primary_all_cells_vs_{branch_name}",
                    "n_common_cells": len(common),
                    "primary_clusters": int(left.nunique()),
                    "comparison_clusters": int(right.nunique()),
                    "adjusted_rand_index": float(adjusted_rand_score(left, right)),
                    "normalized_mutual_information": float(normalized_mutual_info_score(left, right)),
                }
            )
    for lower, upper in zip(resolutions[:-1], resolutions[1:]):
        left = primary.obs[resolution_key(lower)].astype(str)
        right = primary.obs[resolution_key(upper)].astype(str)
        concordance_rows.append(
            {
                "resolution": f"{lower:g}_to_{upper:g}",
                "comparison": "primary_adjacent_resolution",
                "n_common_cells": len(primary.obs),
                "primary_clusters": int(left.nunique()),
                "comparison_clusters": int(right.nunique()),
                "adjusted_rand_index": float(adjusted_rand_score(left, right)),
                "normalized_mutual_information": float(normalized_mutual_info_score(left, right)),
            }
        )
    pd.DataFrame(concordance_rows).to_csv(
        output / "14_branch_and_resolution_concordance.csv", index=False, encoding="utf-8-sig"
    )

    assignments = primary.obs.copy()
    assignments.insert(0, "cell_id", assignments.index.astype(str))
    assignments.to_csv(
        output / "15_primary_cell_assignments.csv.gz", index=False, compression="gzip"
    )

    primary_risk = pd.DataFrame(doublet_rows)
    maximum_cluster_risk = float(primary_risk["residual_auto_call_fraction"].max())
    maximum_cluster_library = float(primary_risk["max_library_fraction"].max())
    return {
        "maximum_cluster_residual_auto_call_fraction": maximum_cluster_risk,
        "maximum_cluster_library_fraction": maximum_cluster_library,
        "bridge_samples": int(
            primary.obs.groupby("sample_uuid", observed=True)["Processing_Cohort"].nunique().gt(1).sum()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--n-pcs", type=int, default=30)
    parser.add_argument("--harmony-max-iter", type=int, default=20)
    parser.add_argument("--resolutions", default=",".join(str(x) for x in DEFAULT_RESOLUTIONS))
    parser.add_argument(
        "--branches",
        default=",".join(branch["name"] for branch in BRANCHES),
        help="Comma-separated branches to fit; existing checkpoints for other branches are reused.",
    )
    args = parser.parse_args()

    import anndata as ad

    prepared_path = Path(args.prepared_h5ad).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    resolutions = tuple(float(value) for value in args.resolutions.split(",") if value.strip())
    if not resolutions:
        raise RuntimeError("At least one Leiden resolution is required")
    requested = {value.strip() for value in args.branches.split(",") if value.strip()}
    known = {branch["name"] for branch in BRANCHES}
    unknown = sorted(requested - known)
    if unknown:
        raise RuntimeError(f"Unknown representation branches: {unknown}")
    if not requested:
        raise RuntimeError("At least one representation branch is required")

    print(f"[LOAD] {prepared_path}", flush=True)
    prepared = ad.read_h5ad(prepared_path)
    prep = prepared.uns.get("phase17_c2b2_preparation", {})
    if prep.get("disease_blind") is not True:
        raise RuntimeError("Prepared object is not marked disease-blind")
    for flag in ("hvg_primary", "hvg_isg_excluded"):
        if flag not in prepared.var:
            raise RuntimeError(f"Prepared object lacks {flag}")
    if "residual_doublet_auto_call" not in prepared.obs:
        raise RuntimeError("Prepared object lacks residual doublet calls")

    branch_objects = {}
    for branch in BRANCHES:
        if branch["name"] in requested:
            branch_objects[branch["name"]] = fit_branch(
                prepared,
                branch,
                output,
                resolutions,
                args.n_neighbors,
                args.n_pcs,
                args.harmony_max_iter,
            )
        else:
            checkpoint = validate_checkpoint(
                output / branch["filename"],
                branch["name"],
                resolutions,
                args.harmony_max_iter,
            )
            if checkpoint is not None:
                branch_objects[branch["name"]] = checkpoint

    missing = sorted(known - set(branch_objects))
    if missing:
        partial = {
            "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "status": "PARTIAL_CHECKPOINTS_VALID",
            "disease_blind": True,
            "completed_branches": sorted(branch_objects),
            "missing_branches": missing,
        }
        (output / "16_GATE_C2B2_PARTIAL.json").write_text(
            json.dumps(partial, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(partial, ensure_ascii=False, indent=2), flush=True)
        return 0

    diagnostics = build_diagnostics(branch_objects, output, resolutions)

    summary = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "REPRESENTATION_FIT_COMPLETE_REVIEW_REQUIRED",
        "disease_blind": True,
        "prepared_h5ad": str(prepared_path),
        "cells_primary": int(branch_objects["primary_all_cells"].n_obs),
        "cells_singlet_sensitivity": int(branch_objects["singlet_sensitivity"].n_obs),
        "resolutions": list(resolutions),
        "harmony_max_iter": args.harmony_max_iter,
        "branches": {
            name: {
                "cells": int(obj.n_obs),
                "genes": int(obj.n_vars),
                "harmony_iterations": obj.uns["phase17_c2b2_branch"].get("harmony_iterations"),
                "harmony_converged": obj.uns["phase17_c2b2_branch"].get("harmony_converged"),
                "harmony_final_relative_objective_change": obj.uns[
                    "phase17_c2b2_branch"
                ].get("harmony_final_relative_objective_change"),
                "clusters": {
                    str(resolution): int(obj.obs[resolution_key(resolution)].nunique())
                    for resolution in resolutions
                },
            }
            for name, obj in branch_objects.items()
        },
        **diagnostics,
    }
    (output / "16_GATE_C2B2_FIT_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        "# Gate C2B2 representation fit",
        "",
        f"**Status:** `{summary['status']}`",
        "",
        f"- Primary cells: {summary['cells_primary']:,}",
        f"- Residual-risk-negative sensitivity cells: {summary['cells_singlet_sensitivity']:,}",
        f"- Bridge samples spanning processing cohorts: {summary['bridge_samples']}",
        f"- Maximum cluster residual-risk fraction: {summary['maximum_cluster_residual_auto_call_fraction']:.2%}",
        f"- Maximum cluster contribution from one library: {summary['maximum_cluster_library_fraction']:.2%}",
        "",
        "This file records representation completion only. Neutral state labels and any",
        "cell exclusion remain unauthorized until marker coherence, cluster coverage,",
        "branch concordance and residual-risk localization are reviewed at Gate C2B3.",
        "",
    ]
    (output / "17_GATE_C2B2_FIT_STATUS.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
