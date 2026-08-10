#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate C2A-01: disease-blind preparation of a 20k raw-count smoke object.

Reads source H5AD and Gate C1 per-cell QC. It applies frozen conservative
hard-QC, performs disease-blind balanced sampling, extracts raw/X directly
from the HDF5 CSR matrix, and writes a new raw-count AnnData.

Source files are read-only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SEED = 20260806
TECHNICAL_OBS = [
    "donor_id", "sample_uuid", "library_uuid", "Processing_Cohort",
]
PROTECTED_OBS_CANDIDATES = [
    "disease", "disease_state", "ct_cov", "sex",
    "self_reported_ethnicity", "development_stage",
]


def decode(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / value.replace("\\", os.sep).replace("/", os.sep)


def read_vector(group, key: str):
    import numpy as np

    obj = group[key]
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]
        categories = [decode(x) for x in obj["categories"][:]]
        return np.array(
            [categories[int(i)] if 0 <= int(i) < len(categories) else "" for i in codes],
            dtype=object,
        )
    return np.array([decode(x) for x in obj[:]], dtype=object)


def read_var_vector(var, candidates):
    for key in dict.fromkeys(candidates):
        if key and key in var:
            return read_vector(var, key), key
    raise RuntimeError(f"No readable var vector. Available keys: {list(var.keys())}")


def extract_csr_rows(matrix_group, selected_indices, n_vars):
    import numpy as np
    from scipy.sparse import csr_matrix

    selected = np.asarray(selected_indices, dtype=np.int64)
    selected.sort()
    source_indptr = matrix_group["indptr"][:]

    lengths = source_indptr[selected + 1] - source_indptr[selected]
    target_indptr = np.zeros(len(selected) + 1, dtype=np.int64)
    target_indptr[1:] = np.cumsum(lengths)
    total_nnz = int(target_indptr[-1])

    source_data = matrix_group["data"]
    source_indices = matrix_group["indices"]
    data = np.empty(total_nnz, dtype=source_data.dtype)
    indices = np.empty(total_nnz, dtype=source_indices.dtype)

    cursor = 0
    for row_index, length in zip(selected, lengths):
        start = int(source_indptr[row_index])
        end = int(source_indptr[row_index + 1])
        next_cursor = cursor + int(length)
        data[cursor:next_cursor] = source_data[start:end]
        indices[cursor:next_cursor] = source_indices[start:end]
        cursor = next_cursor

    return csr_matrix(
        (data, indices, target_indptr),
        shape=(len(selected), n_vars),
    ), selected


def select_smoke(qc, target_cells, seed):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed)
    eligible = qc.loc[~qc["hard_qc_fail"]].copy()
    if len(eligible) <= target_cells:
        eligible["smoke_selected"] = True
        return eligible.index.to_numpy()

    selected = set()

    # Biological-sample coverage, independent of disease.
    for _, group in eligible.groupby("sample_uuid", observed=True):
        take = min(40, len(group))
        chosen = rng.choice(group.index.to_numpy(), size=take, replace=False)
        selected.update(map(int, chosen))

    # Ensure technical-library coverage.
    selected_array = np.array(sorted(selected), dtype=np.int64)
    selected_libraries = set(eligible.loc[selected_array, "library_uuid"])
    for library, group in eligible.groupby("library_uuid", observed=True):
        current = int((eligible.loc[list(selected), "library_uuid"] == library).sum())
        required = max(0, min(30, len(group)) - current)
        if required:
            pool = group.index.difference(pd.Index(selected)).to_numpy()
            if len(pool):
                chosen = rng.choice(pool, size=min(required, len(pool)), replace=False)
                selected.update(map(int, chosen))

    if len(selected) > target_cells:
        chosen = rng.choice(
            np.array(sorted(selected), dtype=np.int64),
            size=target_cells,
            replace=False,
        )
        return np.sort(chosen)

    remaining_n = target_cells - len(selected)
    if remaining_n > 0:
        pool = eligible.loc[~eligible.index.isin(selected)].copy()
        sample_sizes = eligible.groupby("sample_uuid", observed=True).size()
        weights = pool["sample_uuid"].map(lambda x: 1.0 / (sample_sizes[x] ** 0.5))
        weights = weights.to_numpy(dtype=float)
        weights /= weights.sum()
        chosen = rng.choice(
            pool.index.to_numpy(),
            size=min(remaining_n, len(pool)),
            replace=False,
            p=weights,
        )
        selected.update(map(int, chosen))

    return np.array(sorted(selected), dtype=np.int64)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--gatec1-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--source",
        default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad",
    )
    parser.add_argument("--target-cells", type=int, default=20000)
    args = parser.parse_args()

    import anndata as ad
    import h5py
    import numpy as np
    import pandas as pd

    project_root = Path(args.project_root).resolve()
    source = resolve(project_root, args.source)
    gatec1 = Path(args.gatec1_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    qc_path = gatec1 / "10_per_cell_raw_qc.csv.gz"
    manifest_path = gatec1 / "00_input_manifest.json"
    if not qc_path.is_file():
        raise FileNotFoundError(qc_path)
    if not source.is_file():
        raise FileNotFoundError(source)

    qc = pd.read_csv(qc_path)
    expected_columns = {
        "cell_index", "sample_uuid", "donor_id", "library_uuid",
        "Processing_Cohort", "n_counts", "n_genes", "pct_mito",
        "pct_hb", "pct_platelet", "n_blineage_markers_detected",
    }
    missing = sorted(expected_columns - set(qc.columns))
    if missing:
        raise RuntimeError(f"Gate C1 QC is missing: {missing}")

    qc = qc.sort_values("cell_index").reset_index(drop=True)
    if not np.array_equal(qc["cell_index"].to_numpy(), np.arange(len(qc))):
        raise RuntimeError("cell_index is not a complete 0..n-1 sequence")

    reason_columns = {
        "qc_low_counts": qc["n_counts"] < 500,
        "qc_low_genes": qc["n_genes"] < 200,
        "qc_high_mito": qc["pct_mito"] > 10,
        "qc_high_hb": qc["pct_hb"] > 1,
        "qc_high_platelet": qc["pct_platelet"] > 0.5,
        "qc_no_blineage_marker": qc["n_blineage_markers_detected"] < 1,
    }
    for name, values in reason_columns.items():
        qc[name] = values
    qc["hard_qc_fail"] = qc[list(reason_columns)].any(axis=1)

    selected_indices = select_smoke(qc, args.target_cells, SEED)
    qc["smoke_selected"] = False
    qc.loc[selected_indices, "smoke_selected"] = True

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
            matrix_group,
            selected_indices,
            len(gene_ids),
        )

        work_obs = pd.DataFrame(index=pd.Index(cell_ids[sorted_indices], name="cell_id"))
        work_obs["source_cell_index"] = sorted_indices
        for field in TECHNICAL_OBS:
            if field not in obs:
                raise RuntimeError(f"Missing technical field: {field}")
            work_obs[field] = read_vector(obs, field)[sorted_indices]

        protected_fields = [
            field for field in PROTECTED_OBS_CANDIDATES if field in obs
        ]
        protected = pd.DataFrame(
            index=pd.Index(cell_ids[sorted_indices], name="cell_id")
        )
        protected["source_cell_index"] = sorted_indices
        for field in protected_fields:
            protected[field] = read_vector(obs, field)[sorted_indices]

    var_df = pd.DataFrame(
        {
            "gene_id": gene_ids,
            "feature_name": gene_names,
        },
        index=pd.Index(gene_ids, name="gene_id_index"),
    )
    if not var_df.index.is_unique:
        var_df.index = pd.Index(
            [f"{x}__{i}" for i, x in enumerate(var_df.index)],
            name="gene_id_index",
        )

    smoke = ad.AnnData(
        X=counts,
        obs=work_obs,
        var=var_df,
    )
    smoke.uns["phase17"] = {
        "stage": "Gate C2A smoke raw preparation",
        "source_path": str(source),
        "source_sha256": (
            json.loads(manifest_path.read_text(encoding="utf-8")).get("sha256", "")
            if manifest_path.is_file() else ""
        ),
        "target_cells": int(args.target_cells),
        "selected_cells": int(smoke.n_obs),
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

    qc.to_csv(
        output / "01_qc_decisions.csv.gz",
        index=False,
        compression="gzip",
    )

    retention = (
        qc.groupby(["Processing_Cohort", "disease"], observed=True)
        .agg(
            n_cells=("cell_index", "size"),
            n_hard_fail=("hard_qc_fail", "sum"),
            n_smoke_selected=("smoke_selected", "sum"),
        )
        .reset_index()
    )
    retention["hard_fail_fraction"] = (
        retention["n_hard_fail"] / retention["n_cells"]
    )
    retention.to_csv(
        output / "02_qc_retention_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    protected.to_csv(
        output / "03_protected_outcome_metadata.csv.gz",
        compression="gzip",
    )

    selection_summary = (
        qc.loc[qc["smoke_selected"]]
        .groupby(["sample_uuid", "library_uuid"], observed=True)
        .size()
        .rename("n_selected")
        .reset_index()
    )
    selection_summary.to_csv(
        output / "04_smoke_selection_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    smoke.write_h5ad(
        output / "05_smoke_raw_counts.h5ad",
        compression="gzip",
    )

    config = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "source": str(source),
        "gatec1_dir": str(gatec1),
        "output_dir": str(output),
        "selected_cells": int(smoke.n_obs),
        "genes": int(smoke.n_vars),
        "disease_blind": True,
        "random_seed": SEED,
    }
    (output / "00_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(config, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
