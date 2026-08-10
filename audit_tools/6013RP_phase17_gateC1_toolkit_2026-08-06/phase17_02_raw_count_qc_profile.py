#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 17 Gate C1-02: raw-count QC profile without filtering.

Reads raw/X from authoritative B-cell H5AD in row chunks.
Outputs sample-aware QC summaries and candidate MAD thresholds.
It does NOT modify the H5AD and does NOT remove cells.
"""

from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

def decode(x: Any) -> str:
    return x.decode("utf-8", errors="replace") if isinstance(x, bytes) else str(x)

def read_obs_column(obs, key: str):
    import numpy as np
    obj = obs[key]
    if hasattr(obj, "keys") and "codes" in obj and "categories" in obj:
        codes = obj["codes"][:]
        cats = [decode(x) for x in obj["categories"][:]]
        return np.array([cats[int(i)] if int(i) >= 0 else "" for i in codes], dtype=object)
    return np.array([decode(x) for x in obj[:]], dtype=object)

def read_gene_names(var):
    key = "feature_name" if "feature_name" in var else decode(var.attrs.get("_index", "_index"))
    return [decode(x) for x in var[key][:]]

def robust_limits(values, low_mad=3.0, high_mad=3.0, floor=None, ceiling=None):
    import numpy as np
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med)))
    scale = 1.4826 * mad
    low = med - low_mad * scale
    high = med + high_mad * scale
    if floor is not None:
        low = max(low, floor)
    if ceiling is not None:
        high = min(high, ceiling)
    return med, mad, low, high

def resolve_project_path(root: Path, value: str) -> Path:
    """Resolve Windows- or POSIX-style project-relative paths."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    normalized = value.replace("\\", os.sep).replace("/", os.sep)
    return root / normalized

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=r"H:\cuhk-2025fALL\6013RP-wyf")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument(
        "--discovery",
        default=r"Data\processed\GSE174188_perez_cellxgene\bcell_subset_full.h5ad",
    )
    ap.add_argument("--chunk-rows", type=int, default=5000)
    ap.add_argument("--mad", type=float, default=3.0)
    args = ap.parse_args()

    import h5py
    import numpy as np
    import pandas as pd
    from scipy.sparse import csr_matrix

    root = Path(args.project_root).resolve()
    source = resolve_project_path(root, args.discovery)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with h5py.File(source, "r") as f:
        obs = f["obs"]
        raw = f["raw"]
        x = raw["X"]
        var = raw["var"]

        if not (hasattr(x, "keys") and {"data", "indices", "indptr"} <= set(x.keys())):
            raise RuntimeError("raw/X is not CSR encoded; this script expects H5AD CSR matrix")

        genes = np.array(read_gene_names(var), dtype=object)
        upper = np.char.upper(genes.astype(str))
        mt_mask = np.char.startswith(upper, "MT-")
        ribo_mask = np.char.startswith(upper, "RPS") | np.char.startswith(upper, "RPL")
        hb_mask = np.isin(upper, ["HBA1", "HBA2", "HBB", "HBD", "HBG1", "HBG2"])
        platelet_mask = np.isin(upper, ["PPBP", "PF4", "NRGN", "GNG11", "SDPR", "RGS18"])

        sample_uuid = read_obs_column(obs, "sample_uuid")
        donor_id = read_obs_column(obs, "donor_id")
        library_uuid = read_obs_column(obs, "library_uuid")
        cohort = read_obs_column(obs, "Processing_Cohort")
        disease = read_obs_column(obs, "disease")

        n_obs = len(sample_uuid)
        n_counts = np.zeros(n_obs, dtype=np.float64)
        n_genes = np.zeros(n_obs, dtype=np.int32)
        mt_counts = np.zeros(n_obs, dtype=np.float64)
        ribo_counts = np.zeros(n_obs, dtype=np.float64)
        hb_counts = np.zeros(n_obs, dtype=np.float64)
        platelet_counts = np.zeros(n_obs, dtype=np.float64)

        indptr_all = x["indptr"][:]
        n_vars = len(genes)

        for start in range(0, n_obs, args.chunk_rows):
            end = min(n_obs, start + args.chunk_rows)
            p0, p1 = int(indptr_all[start]), int(indptr_all[end])
            data = x["data"][p0:p1]
            indices = x["indices"][p0:p1]
            indptr = indptr_all[start:end + 1] - p0
            mat = csr_matrix((data, indices, indptr), shape=(end - start, n_vars))
            n_counts[start:end] = np.asarray(mat.sum(axis=1)).ravel()
            n_genes[start:end] = np.diff(mat.indptr)
            if mt_mask.any():
                mt_counts[start:end] = np.asarray(mat[:, mt_mask].sum(axis=1)).ravel()
            if ribo_mask.any():
                ribo_counts[start:end] = np.asarray(mat[:, ribo_mask].sum(axis=1)).ravel()
            if hb_mask.any():
                hb_counts[start:end] = np.asarray(mat[:, hb_mask].sum(axis=1)).ravel()
            if platelet_mask.any():
                platelet_counts[start:end] = np.asarray(mat[:, platelet_mask].sum(axis=1)).ravel()
            print(f"[QC] {end:,}/{n_obs:,}")

    denom = np.maximum(n_counts, 1.0)
    cells = pd.DataFrame({
        "cell_index": np.arange(n_obs),
        "sample_uuid": sample_uuid,
        "donor_id": donor_id,
        "library_uuid": library_uuid,
        "Processing_Cohort": cohort,
        "disease": disease,
        "n_counts": n_counts,
        "n_genes": n_genes,
        "pct_mito": 100 * mt_counts / denom,
        "pct_ribo": 100 * ribo_counts / denom,
        "pct_hb": 100 * hb_counts / denom,
        "pct_platelet": 100 * platelet_counts / denom,
    })

    metrics = ["n_counts", "n_genes", "pct_mito", "pct_ribo", "pct_hb", "pct_platelet"]
    def q01(x):
        return x.quantile(0.01)
    def q05(x):
        return x.quantile(0.05)
    def q95(x):
        return x.quantile(0.95)
    def q99(x):
        return x.quantile(0.99)

    summary = (
        cells.groupby("sample_uuid", observed=True)[metrics]
        .agg(["count", "min", "median", "mean", "max", q01, q05, q95, q99])
    )
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()

    threshold_rows = []
    for sample, sub in cells.groupby("sample_uuid", observed=True):
        count_med, count_mad, count_low, count_high = robust_limits(
            np.log10(sub["n_counts"] + 1), args.mad, args.mad
        )
        gene_med, gene_mad, gene_low, gene_high = robust_limits(
            np.log10(sub["n_genes"] + 1), args.mad, args.mad
        )
        mito_med, mito_mad, mito_low, mito_high = robust_limits(
            sub["pct_mito"], args.mad, args.mad, floor=0, ceiling=100
        )
        candidate = (
            (np.log10(sub["n_counts"] + 1) < count_low)
            | (np.log10(sub["n_counts"] + 1) > count_high)
            | (np.log10(sub["n_genes"] + 1) < gene_low)
            | (np.log10(sub["n_genes"] + 1) > gene_high)
            | (sub["pct_mito"] > mito_high)
        )
        threshold_rows.append({
            "sample_uuid": sample,
            "n_cells": len(sub),
            "log10_counts_median": count_med,
            "log10_counts_mad": count_mad,
            "log10_counts_low_candidate": count_low,
            "log10_counts_high_candidate": count_high,
            "log10_genes_median": gene_med,
            "log10_genes_mad": gene_mad,
            "log10_genes_low_candidate": gene_low,
            "log10_genes_high_candidate": gene_high,
            "pct_mito_median": mito_med,
            "pct_mito_mad": mito_mad,
            "pct_mito_high_candidate": mito_high,
            "candidate_flagged_cells": int(candidate.sum()),
            "candidate_flagged_fraction": float(candidate.mean()),
        })
    thresholds = pd.DataFrame(threshold_rows)

    # Compact outputs; full per-cell table is gzip compressed.
    cells.to_csv(out / "07_per_cell_raw_qc.csv.gz", index=False, compression="gzip")
    summary.to_csv(out / "08_sample_qc_summary.csv", index=False, encoding="utf-8-sig")
    thresholds.to_csv(out / "09_sample_qc_candidate_thresholds.csv", index=False, encoding="utf-8-sig")

    report = f"""# Gate C1-02 raw-count QC profile

- Time: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}
- Source: `{source}`
- Cells profiled: {len(cells):,}
- Samples: {cells['sample_uuid'].nunique():,}
- Genes: {len(genes):,}
- Mito genes detected: {int(mt_mask.sum())}
- Ribosomal genes detected: {int(ribo_mask.sum())}
- Hemoglobin genes detected: {int(hb_mask.sum())}
- Platelet marker genes detected: {int(platelet_mask.sum())}
- Candidate MAD multiplier: {args.mad}

Important: candidate thresholds are diagnostic only.
No cell was removed and the source H5AD was not modified.
Doublet scoring and ambient-RNA correction remain separate Gate C2 tasks.
"""
    (out / "02_RAW_COUNT_QC_SUMMARY.md").write_text(report, encoding="utf-8")
    print(report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
