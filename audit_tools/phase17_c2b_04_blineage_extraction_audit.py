#!/usr/bin/env python3
"""Audit B-lineage extraction completeness from the full PBMC raw matrix."""

from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse


B_SPECIFIC = ["CD79A", "CD79B", "MS4A1", "CD19", "CD22", "CD37", "BANK1"]
B_APC = ["CD74", "HLA-DRA", "CD40"]
PLASMA = ["MZB1", "JCHAIN", "SDC1", "DERL3", "TNFRSF17", "SEC11C", "CD38"]
NON_B = [
    "CD3D", "CD3E", "TRBC1", "TRBC2", "NKG7", "GNLY", "LST1", "TYROBP",
    "FCER1G", "S100A8", "S100A9", "FCGR3A", "PPBP", "PF4",
]
SOURCE_B_LABELS = {"B cell", "plasmablast"}


def feature_lookup(adata: ad.AnnData) -> dict[str, int]:
    var = adata.raw.var if adata.raw is not None else adata.var
    names = var["feature_name"].astype(str) if "feature_name" in var else pd.Series(var.index.astype(str))
    lookup: dict[str, int] = {}
    for idx, name in enumerate(names):
        lookup.setdefault(name.upper(), idx)
    return lookup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--chunk-size", type=int, default=10000)
    args = parser.parse_args()

    input_h5ad = Path(args.input_h5ad).resolve()
    output = Path(args.output_dir).resolve()
    figures = output / "figures"
    output.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    adata = ad.read_h5ad(input_h5ad, backed="r")
    if "cell_type" not in adata.obs:
        raise RuntimeError("Full PBMC object lacks source cell_type labels")
    matrix = adata.raw.X if adata.raw is not None else adata.X
    lookup = feature_lookup(adata)
    modules = {"b_specific": B_SPECIFIC, "b_apc": B_APC, "plasma": PLASMA, "non_b": NON_B}
    found = {name: [gene for gene in genes if gene.upper() in lookup] for name, genes in modules.items()}
    missing = {name: [gene for gene in genes if gene.upper() not in lookup] for name, genes in modules.items()}
    union = []
    for genes in found.values():
        for gene in genes:
            if gene not in union:
                union.append(gene)
    indices = [lookup[gene.upper()] for gene in union]
    union_position = {gene: idx for idx, gene in enumerate(union)}

    coverage_rows = []
    for name, genes in modules.items():
        coverage_rows.append(
            {
                "module": name,
                "requested_genes": len(genes),
                "found_genes": len(found[name]),
                "found": " | ".join(found[name]),
                "missing": " | ".join(missing[name]),
            }
        )
    pd.DataFrame(coverage_rows).to_csv(output / "02_blineage_marker_coverage.csv", index=False)

    safe_obs = adata.obs[["cell_type", "donor_id", "sample_uuid", "library_uuid", "Processing_Cohort"]].copy()
    safe_obs.index = safe_obs.index.astype(str)
    chunks = []
    for start in range(0, adata.n_obs, args.chunk_size):
        stop = min(start + args.chunk_size, adata.n_obs)
        # Backed CSR performs poorly when row and non-contiguous column indexing
        # are combined. Read contiguous rows first, then select the small marker
        # panel from the in-memory sparse block.
        block = matrix[start:stop]
        block = block[:, indices]
        values = block.toarray() if sparse.issparse(block) else np.asarray(block)
        row = {"cell_id": safe_obs.index[start:stop].to_numpy()}
        for name, genes in found.items():
            positions = [union_position[gene] for gene in genes]
            module = values[:, positions] if positions else np.zeros((stop - start, 0))
            row[f"{name}_detected"] = np.count_nonzero(module, axis=1)
            row[f"{name}_umi"] = module.sum(axis=1)
        chunks.append(pd.DataFrame(row))
        print(f"[B-LINEAGE] {stop:,}/{adata.n_obs:,} cells", flush=True)

    scores = pd.concat(chunks, ignore_index=True).set_index("cell_id")
    diagnostics = safe_obs.join(scores, how="left", validate="one_to_one")
    b_umi = diagnostics["b_specific_umi"] + diagnostics["b_apc_umi"] + diagnostics["plasma_umi"]
    diagnostics["b_panel_purity"] = b_umi / np.maximum(b_umi + diagnostics["non_b_umi"], 1)
    diagnostics["source_b_lineage"] = diagnostics["cell_type"].isin(SOURCE_B_LABELS)

    outside = diagnostics.loc[~diagnostics["source_b_lineage"]].copy()
    rule_rows = []
    for min_specific in [1, 2, 3]:
        for min_total in [2, 3, 4]:
            for purity in [0.50, 0.75, 0.90]:
                total_detected = outside["b_specific_detected"] + outside["b_apc_detected"] + outside["plasma_detected"]
                flag = (
                    outside["b_specific_detected"].ge(min_specific)
                    & total_detected.ge(min_total)
                    & outside["b_panel_purity"].ge(purity)
                )
                rule_rows.append(
                    {
                        "min_b_specific_detected": min_specific,
                        "min_total_b_panel_detected": min_total,
                        "min_b_panel_purity": purity,
                        "candidate_cells_outside_source_b": int(flag.sum()),
                        "candidate_fraction_outside_source_b": float(flag.mean()),
                    }
                )
    rules = pd.DataFrame(rule_rows)
    rules.to_csv(output / "03_blineage_candidate_rule_sensitivity.csv", index=False)

    strict_flag = (
        outside["b_specific_detected"].ge(2)
        & (outside["b_specific_detected"] + outside["b_apc_detected"] + outside["plasma_detected"]).ge(3)
        & outside["b_panel_purity"].ge(0.75)
    )
    candidates = outside.loc[strict_flag].copy()
    candidates.reset_index(names="cell_id").to_csv(
        output / "04_blineage_strict_candidates.csv.gz", index=False, compression="gzip"
    )
    candidate_by_label = (
        candidates.groupby("cell_type", observed=False)
        .agg(
            candidate_cells=("cell_type", "size"),
            donors=("donor_id", "nunique"),
            samples=("sample_uuid", "nunique"),
            libraries=("library_uuid", "nunique"),
            median_b_specific_detected=("b_specific_detected", "median"),
            median_b_panel_purity=("b_panel_purity", "median"),
        )
        .reset_index()
    )
    candidate_by_label["cell_type"] = candidate_by_label["cell_type"].astype(str)
    source_counts = (
        diagnostics["cell_type"].astype(str).value_counts().rename_axis("cell_type").reset_index(name="source_cells")
    )
    candidate_by_label = source_counts.merge(candidate_by_label, on="cell_type", how="left")
    numeric_columns = [column for column in candidate_by_label.columns if column != "cell_type"]
    candidate_by_label[numeric_columns] = candidate_by_label[numeric_columns].fillna(0)
    candidate_by_label["candidate_fraction_within_source_label"] = (
        candidate_by_label["candidate_cells"] / candidate_by_label["source_cells"]
    )
    candidate_by_label.to_csv(output / "05_blineage_candidates_by_source_label.csv", index=False)
    source_counts.to_csv(output / "01_blineage_source_summary.csv", index=False)

    plot = candidate_by_label.sort_values("candidate_cells", ascending=True)
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    ax.barh(plot["cell_type"], plot["candidate_cells"], color="#4477AA")
    ax.set(xlabel="Strict B-like candidates outside source B labels", ylabel="Source cell type")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figures / "blineage_candidates_by_source_label.png", dpi=300, facecolor="white")
    fig.savefig(figures / "blineage_candidates_by_source_label.pdf", facecolor="white")
    plt.close(fig)

    source_b = int(diagnostics["source_b_lineage"].sum())
    candidate_fraction = len(candidates) / len(outside)
    report = f"""# B-lineage extraction completeness audit

**Status:** REVIEW REQUIRED; this audit does not relabel or append cells.

- Full PBMC cells: {adata.n_obs:,}
- Source B cell/plasmablast labels: {source_b:,}
- Cells outside source B labels: {len(outside):,}
- Strict B-like candidates outside source labels: {len(candidates):,} ({candidate_fraction:.3%})
- Candidate donors/samples/libraries: {candidates['donor_id'].nunique():,} / {candidates['sample_uuid'].nunique():,} / {candidates['library_uuid'].nunique():,}
- Disease fields used or exported: none

## Binding interpretation

The strict rule requires at least two B-specific genes, at least three genes
across the B/plasma panel and at least 75% B-panel purity relative to the
prespecified non-B marker panel. The full threshold grid is retained because no
single marker rule can establish cell identity on its own.

Review candidate source labels, marker combinations and later disease-blind
graph localization. Expand the B-lineage input only if a coherent, broadly
represented B-like population was materially omitted; otherwise retain the
source B/plasmablast definition and report this as completeness QC.
"""
    (output / "06_BLINEAGE_EXTRACTION_AUDIT.md").write_text(report, encoding="utf-8")
    adata.file.close()
    print(output / "06_BLINEAGE_EXTRACTION_AUDIT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
