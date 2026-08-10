#!/usr/bin/env python3
"""Gate C2B-02: resumable per-library Scrublet on complete libraries."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scrublet as scr


SEED = 20260806
EXPECTED_DOUBLET_RATE = 0.06


def checkpoint_name(library: str) -> str:
    digest = hashlib.sha1(library.encode("utf-8")).hexdigest()[:12]
    return f"library_{digest}.csv.gz"


def summary_checkpoint_name(library: str) -> str:
    digest = hashlib.sha1(library.encode("utf-8")).hexdigest()[:12]
    return f"library_{digest}.summary.json"


def run_library(adata, positions: np.ndarray, library: str) -> tuple[pd.DataFrame, dict]:
    subset = adata.X[positions]
    model = scr.Scrublet(
        subset,
        expected_doublet_rate=EXPECTED_DOUBLET_RATE,
        random_state=SEED,
    )
    n_prin = max(5, min(30, len(positions) - 2))
    scores, predictions = model.scrub_doublets(
        use_approx_neighbors=False,
        min_counts=2,
        min_cells=3,
        min_gene_variability_pctl=85,
        n_prin_comps=n_prin,
        svd_solver="randomized",
        verbose=False,
    )
    cells = pd.DataFrame(
        {
            "cell_id": adata.obs_names[positions].astype(str),
            "source_cell_index": adata.obs.iloc[positions]["source_cell_index"].to_numpy(),
            "library_uuid": library,
            "doublet_score": scores,
            "predicted_doublet": predictions,
        }
    )
    summary = {
        "library_uuid": library,
        "n_cells": int(len(positions)),
        "status": "ok",
        "threshold": float(model.threshold_) if model.threshold_ is not None else np.nan,
        "predicted_doublets": int(predictions.sum()),
        "predicted_doublet_fraction": float(predictions.mean()),
        "score_median": float(np.median(scores)),
        "score_q95": float(np.quantile(scores, 0.95)),
        "message": "",
    }
    return cells, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()

    input_h5ad = Path(args.input_h5ad).resolve()
    output = Path(args.output_dir).resolve()
    checkpoints = output / "doublet_score_checkpoints"
    figures = output / "figures"
    checkpoints.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    adata = ad.read_h5ad(input_h5ad)
    forbidden = {"disease", "disease_state", "ct_cov"} & set(adata.obs.columns)
    if forbidden:
        raise RuntimeError(f"Protected fields leaked into working AnnData: {sorted(forbidden)}")
    if "library_uuid" not in adata.obs or "source_cell_index" not in adata.obs:
        raise RuntimeError("Working AnnData lacks library_uuid or source_cell_index")

    libraries = adata.obs["library_uuid"].astype(str).to_numpy()
    summaries = []
    cell_tables = []
    for library in sorted(np.unique(libraries)):
        positions = np.flatnonzero(libraries == library)
        checkpoint = checkpoints / checkpoint_name(library)
        summary_checkpoint = checkpoints / summary_checkpoint_name(library)
        if checkpoint.is_file() and summary_checkpoint.is_file() and not args.restart:
            cells = pd.read_csv(checkpoint)
            if len(cells) != len(positions) or set(cells["library_uuid"].astype(str)) != {library}:
                raise RuntimeError(f"Invalid checkpoint: {checkpoint}")
            summary = json.loads(summary_checkpoint.read_text(encoding="utf-8"))
            if summary.get("library_uuid") != library or int(summary.get("n_cells", -1)) != len(cells):
                raise RuntimeError(f"Invalid summary checkpoint: {summary_checkpoint}")
            summary["status"] = "resumed"
            summary["message"] = "Cell scores and threshold restored from paired checkpoints."
        elif len(positions) < 100:
            cells = pd.DataFrame(
                {
                    "cell_id": adata.obs_names[positions].astype(str),
                    "source_cell_index": adata.obs.iloc[positions]["source_cell_index"].to_numpy(),
                    "library_uuid": library,
                    "doublet_score": np.nan,
                    "predicted_doublet": False,
                }
            )
            summary = {
                "library_uuid": library,
                "n_cells": int(len(positions)),
                "status": "skipped_lt100_cells",
                "threshold": np.nan,
                "predicted_doublets": 0,
                "predicted_doublet_fraction": 0.0,
                "score_median": np.nan,
                "score_q95": np.nan,
                "message": "Too few cells for stable per-library modeling.",
            }
            cells.to_csv(checkpoint, index=False, compression="gzip")
            summary_checkpoint.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        else:
            if checkpoint.is_file() and not summary_checkpoint.is_file() and not args.restart:
                print(f"[SCRUBLET] {library}: incomplete legacy checkpoint; rerunning to recover threshold")
            try:
                cells, summary = run_library(adata, positions, library)
                cells.to_csv(checkpoint, index=False, compression="gzip")
                summary_checkpoint.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            except Exception as exc:
                cells = pd.DataFrame()
                summary = {
                    "library_uuid": library,
                    "n_cells": int(len(positions)),
                    "status": "error",
                    "threshold": np.nan,
                    "predicted_doublets": 0,
                    "predicted_doublet_fraction": np.nan,
                    "score_median": np.nan,
                    "score_q95": np.nan,
                    "message": f"{type(exc).__name__}: {exc}",
                }
        summaries.append(summary)
        if not cells.empty:
            cell_tables.append(cells)
        print(
            f"[SCRUBLET] {library}: n={len(positions)}, "
            f"status={summary['status']}, predicted={summary['predicted_doublets']}"
        )

    summary_df = pd.DataFrame(summaries)
    scores_df = pd.concat(cell_tables, ignore_index=True)
    if scores_df["cell_id"].duplicated().any():
        raise RuntimeError("Duplicate cell IDs in doublet score table")
    summary_df.to_csv(
        output / "05_full_library_doublet_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    scores_df.to_csv(
        output / "06_full_cell_doublet_scores.csv.gz",
        index=False,
        compression="gzip",
    )

    ok = summary_df[summary_df["status"].isin(["ok", "resumed"])].copy()
    ok["fraction_minus_expected"] = ok["predicted_doublet_fraction"] - EXPECTED_DOUBLET_RATE
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    axes[0].hist(
        scores_df["doublet_score"].dropna(), bins=60, color="#4477AA", edgecolor="white"
    )
    axes[0].set(xlabel="Scrublet score", ylabel="Cells")
    axes[1].hist(
        ok["predicted_doublet_fraction"].dropna(),
        bins=np.linspace(0, max(0.25, ok["predicted_doublet_fraction"].max()), 25),
        color="#CC6677",
        edgecolor="white",
    )
    axes[1].axvline(EXPECTED_DOUBLET_RATE, color="black", linewidth=1, linestyle="--")
    axes[1].set(xlabel="Predicted fraction per library", ylabel="Libraries")
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures / "full_library_doublet_diagnostics.png", dpi=300)
    fig.savefig(figures / "full_library_doublet_diagnostics.pdf")
    plt.close(fig)

    total_predicted = int(scores_df["predicted_doublet"].sum())
    decision = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "input_h5ad": str(input_h5ad),
        "input_cells": int(adata.n_obs),
        "scored_cells": int(scores_df["doublet_score"].notna().sum()),
        "predicted_doublets": total_predicted,
        "predicted_doublet_fraction": total_predicted / int(adata.n_obs),
        "successful_or_resumed_libraries": int(len(ok)),
        "skipped_libraries": int(summary_df["status"].eq("skipped_lt100_cells").sum()),
        "error_libraries": int(summary_df["status"].eq("error").sum()),
        "median_library_fraction": float(ok["predicted_doublet_fraction"].median()),
        "maximum_library_fraction": float(ok["predicted_doublet_fraction"].max()),
        "libraries_above_0_20": int(ok["predicted_doublet_fraction"].gt(0.20).sum()),
        "freeze_status": "REVIEW_REQUIRED_DO_NOT_EXCLUDE_YET",
        "diagnostic_role": "RESIDUAL_DOUBLET_RISK_AFTER_SOURCE_PIPELINE",
        "branch_policy": ["all-hard-QC", "high-confidence-singlet sensitivity"],
        "disease_blind": True,
    }
    (output / "07_GATE_C2B1_DOUBLET_REVIEW.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    report = f"""# Gate C2B1 residual doublet-risk review

**Status:** REVIEW REQUIRED; no cells have been excluded from the authoritative full raw object.

The Perez source workflow already applied donor demultiplexing and doublet
handling. This second Scrublet pass is a residual-risk diagnostic, not an
independent mandate for another automatic deletion step.

- Input cells: {adata.n_obs:,}
- Cells with Scrublet scores: {decision['scored_cells']:,}
- Automatic predicted fraction: {decision['predicted_doublet_fraction']:.2%}
- Median library fraction: {decision['median_library_fraction']:.2%}
- Maximum library fraction: {decision['maximum_library_fraction']:.2%}
- Libraries above 20%: {decision['libraries_above_0_20']}
- Libraries skipped below 100 eligible cells: {decision['skipped_libraries']}
- Library errors: {decision['error_libraries']}

Automatic calls are diagnostic until score distributions, library rates and
mixed-lineage marker enrichment are reviewed. The full raw object remains unchanged.
The primary branch retains all hard-QC cells; a high-confidence-singlet branch
is carried only as a sensitivity analysis until cluster-localization review is complete.
"""
    (output / "08_GATE_C2B1_DOUBLET_REVIEW.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
