#!/usr/bin/env python3
"""Re-run only Harmony and graph construction with the isolated legacy runtime."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


SEED = 20260806


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-representation", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resolution", type=float, default=0.4)
    parser.add_argument("--n-neighbors", type=int, default=15)
    parser.add_argument("--n-pcs", type=int, default=30)
    parser.add_argument("--harmony-max-iter", type=int, default=20)
    args = parser.parse_args()

    import anndata as ad
    import harmonypy
    import numpy as np
    import scanpy as sc

    source = Path(args.input_representation).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    target = output / "08_isg_excluded_representation.h5ad"

    work = ad.read_h5ad(source)
    if "X_pca" not in work.obsm:
        raise RuntimeError("Input representation lacks the pre-Harmony PCA coordinates")
    if work.uns.get("phase17_c2b2_branch", {}).get("disease_blind") is not True:
        raise RuntimeError("Input representation is not marked disease blind")

    version = getattr(harmonypy, "__version__", "unknown")
    print(f"[LEGACY HARMONY] version={version}; cells={work.n_obs:,}", flush=True)
    harmony = harmonypy.run_harmony(
        work.obsm["X_pca"].astype(np.float64),
        work.obs,
        "library_uuid",
        random_state=SEED,
        max_iter_harmony=args.harmony_max_iter,
    )
    corrected = np.asarray(harmony.Z_corr)
    if corrected.shape[0] == work.n_obs:
        work.obsm["X_pca_harmony"] = corrected
    elif corrected.ndim == 2 and corrected.shape[1] == work.n_obs:
        work.obsm["X_pca_harmony"] = corrected.T
    else:
        raise RuntimeError(
            f"Legacy Harmony output does not align: {corrected.shape} vs {work.n_obs} cells"
        )

    use_pcs = min(args.n_pcs, work.obsm["X_pca_harmony"].shape[1])
    sc.pp.neighbors(
        work,
        n_neighbors=args.n_neighbors,
        n_pcs=use_pcs,
        use_rep="X_pca_harmony",
        key_added="harmony",
        random_state=SEED,
    )
    key = f"leiden_harmony_r{str(args.resolution).replace('.', '_')}"
    sc.tl.leiden(
        work,
        resolution=args.resolution,
        neighbors_key="harmony",
        key_added=key,
        random_state=SEED,
        flavor="leidenalg",
    )
    objectives = [float(value) for value in getattr(harmony, "objective_harmony", [])]
    work.uns["phase17_c2b2_branch"] = {
        "schema_version": 2,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "disease_blind": True,
        "branch": "isg_excluded",
        "cell_policy": "all_hard_qc",
        "var_flag": "hvg_isg_excluded",
        "resolutions": [args.resolution],
        "integration_covariate": "library_uuid",
        "harmony_max_iter": args.harmony_max_iter,
        "harmony_version": version,
        "harmony_device": "legacy_numpy_cpu",
        "harmony_iterations": max(0, len(objectives) - 1),
        "harmony_objective": objectives,
        "seed": SEED,
        "pca_source": str(source),
    }
    work.write_h5ad(target, compression="gzip")
    status = {
        "status": "LEGACY_HARMONY_REPAIR_COMPLETE",
        "harmony_version": version,
        "cells": int(work.n_obs),
        "features": int(work.n_vars),
        "clusters": int(work.obs[key].nunique()),
        "output": str(target),
    }
    (output / "legacy_harmony_repair_status.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(status, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
