#!/usr/bin/env python3
"""Gate C2B-01: extract all hard-QC-passing raw-count B cells.

The working AnnData contains technical identifiers only. Disease and other
protected fields are written to a separate table for post-freeze analyses.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd

from phase17_c2a_01_prepare_smoke import (
    PROTECTED_OBS_CANDIDATES,
    SEED,
    TECHNICAL_OBS,
    decode,
    extract_csr_rows,
    read_var_vector,
    read_vector,
    resolve,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--gatec1-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--source",
        default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    source = resolve(project_root, args.source)
    gatec1 = Path(args.gatec1_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    qc_path = gatec1 / "10_per_cell_raw_qc.csv.gz"
    manifest_path = gatec1 / "00_input_manifest.json"
    if not source.is_file():
        raise FileNotFoundError(source)
    if not qc_path.is_file():
        raise FileNotFoundError(qc_path)

    qc = pd.read_csv(qc_path).sort_values("cell_index").reset_index(drop=True)
    expected = {
        "cell_index", "sample_uuid", "donor_id", "library_uuid",
        "Processing_Cohort", "n_counts", "n_genes", "pct_mito",
        "pct_hb", "pct_platelet", "n_blineage_markers_detected",
    }
    missing = sorted(expected - set(qc.columns))
    if missing:
        raise RuntimeError(f"Gate C1 QC is missing: {missing}")
    if not np.array_equal(qc["cell_index"].to_numpy(), np.arange(len(qc))):
        raise RuntimeError("cell_index is not a complete 0..n-1 sequence")

    decisions = {
        "qc_low_counts": qc["n_counts"] < 500,
        "qc_low_genes": qc["n_genes"] < 200,
        "qc_high_mito": qc["pct_mito"] > 10,
        "qc_high_hb": qc["pct_hb"] > 1,
        "qc_high_platelet": qc["pct_platelet"] > 0.5,
        "qc_no_blineage_marker": qc["n_blineage_markers_detected"] < 1,
    }
    for name, values in decisions.items():
        qc[name] = values
    qc["hard_qc_fail"] = qc[list(decisions)].any(axis=1)
    eligible_indices = qc.loc[~qc["hard_qc_fail"], "cell_index"].to_numpy()

    with h5py.File(source, "r") as handle:
        obs = handle["obs"]
        raw = handle["raw"]
        var = raw["var"]
        matrix_group = raw["X"]

        index_key = decode(obs.attrs.get("_index", "_index"))
        cell_ids = read_vector(obs, index_key)
        if len(cell_ids) != len(qc):
            raise RuntimeError(
                f"QC/H5AD row mismatch: QC={len(qc)}, H5AD={len(cell_ids)}"
            )

        raw_var_index_key = decode(var.attrs.get("_index", "_index"))
        gene_ids = read_vector(var, raw_var_index_key)
        gene_names, gene_name_field = read_var_vector(
            var,
            [
                "feature_name", "gene_name", "gene_symbol", "symbol",
                raw_var_index_key, "_index",
            ],
        )
        counts, sorted_indices = extract_csr_rows(
            matrix_group, eligible_indices, len(gene_ids)
        )

        work_obs = pd.DataFrame(
            index=pd.Index(cell_ids[sorted_indices], name="cell_id")
        )
        work_obs["source_cell_index"] = sorted_indices
        for field in TECHNICAL_OBS:
            if field not in obs:
                raise RuntimeError(f"Missing technical field: {field}")
            work_obs[field] = read_vector(obs, field)[sorted_indices]

        protected = pd.DataFrame(
            index=pd.Index(cell_ids[sorted_indices], name="cell_id")
        )
        protected["source_cell_index"] = sorted_indices
        for field in PROTECTED_OBS_CANDIDATES:
            if field in obs:
                protected[field] = read_vector(obs, field)[sorted_indices]

    var_df = pd.DataFrame(
        {"gene_id": gene_ids, "feature_name": gene_names},
        index=pd.Index(gene_ids, name="gene_id_index"),
    )
    if not var_df.index.is_unique:
        var_df.index = pd.Index(
            [f"{value}__{i}" for i, value in enumerate(var_df.index)],
            name="gene_id_index",
        )

    full = ad.AnnData(X=counts, obs=work_obs, var=var_df)
    full.uns["phase17"] = {
        "stage": "Gate C2B full raw preparation",
        "source_path": str(source),
        "source_sha256": (
            json.loads(manifest_path.read_text(encoding="utf-8")).get("sha256", "")
            if manifest_path.is_file() else ""
        ),
        "selected_cells": int(full.n_obs),
        "random_seed": SEED,
        "gene_name_field": gene_name_field,
        "disease_blind": True,
        "hard_qc": {
            "min_counts": 500,
            "min_genes": 200,
            "max_pct_mito": 10,
            "max_pct_hb": 1,
            "max_pct_platelet": 0.5,
            "min_blineage_markers_detected": 1,
        },
    }

    qc.to_csv(output / "01_full_qc_decisions.csv.gz", index=False, compression="gzip")
    retention = (
        qc.groupby(["Processing_Cohort", "disease"], observed=True)
        .agg(n_cells=("cell_index", "size"), n_hard_fail=("hard_qc_fail", "sum"))
        .reset_index()
    )
    retention["n_eligible"] = retention["n_cells"] - retention["n_hard_fail"]
    retention["hard_fail_fraction"] = retention["n_hard_fail"] / retention["n_cells"]
    retention.to_csv(
        output / "02_full_qc_retention_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    protected.to_csv(
        output / "03_protected_outcome_metadata.csv.gz", compression="gzip"
    )
    full.write_h5ad(output / "04_full_raw_counts.h5ad", compression="gzip")

    config = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "source": str(source),
        "gatec1_dir": str(gatec1),
        "output_dir": str(output),
        "eligible_cells": int(full.n_obs),
        "genes": int(full.n_vars),
        "disease_blind": True,
        "random_seed": SEED,
    }
    (output / "00_full_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    print(json.dumps(config, indent=2))
    return 0


if __name__ == "__main__":
    os.environ.setdefault("HDF5_USE_FILE_LOCKING", "FALSE")
    raise SystemExit(main())
