#!/usr/bin/env python3
"""Refine B-like candidates outside source B labels using gene-level evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse


CORE_B = ["CD79A", "CD79B", "MS4A1", "CD19", "CD22"]
SUPPORT_B = ["CD37", "BANK1"]
SHARED_APC = ["CD74", "HLA-DRA", "CD40"]
CORE_PLASMA = ["MZB1", "JCHAIN", "SDC1", "DERL3", "TNFRSF17", "SEC11C"]
SUPPORT_PLASMA = ["CD38"]
NON_B = ["CD3D", "CD3E", "NKG7", "GNLY", "LST1", "TYROBP", "FCER1G", "S100A8", "S100A9", "FCGR3A", "PPBP", "PF4"]
MODULES = {
    "core_b": CORE_B,
    "support_b": SUPPORT_B,
    "shared_apc": SHARED_APC,
    "core_plasma": CORE_PLASMA,
    "support_plasma": SUPPORT_PLASMA,
    "non_b": NON_B,
}


def feature_lookup(adata: ad.AnnData) -> dict[str, int]:
    var = adata.raw.var if adata.raw is not None else adata.var
    names = var["feature_name"].astype(str) if "feature_name" in var else pd.Series(var.index.astype(str))
    lookup: dict[str, int] = {}
    for index, name in enumerate(names):
        lookup.setdefault(name.upper(), index)
    return lookup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--chunk-size", type=int, default=10000)
    args = parser.parse_args()

    input_h5ad = Path(args.input_h5ad).resolve()
    candidate_path = Path(args.candidates).resolve()
    output = Path(args.output_dir).resolve()
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    candidates = pd.read_csv(candidate_path)
    if not candidates["cell_id"].is_unique:
        raise RuntimeError("Candidate cell IDs are not unique")
    candidate_ids = set(candidates["cell_id"].astype(str))

    adata = ad.read_h5ad(input_h5ad, backed="r")
    matrix = adata.raw.X if adata.raw is not None else adata.X
    lookup = feature_lookup(adata)
    genes = [gene for module in MODULES.values() for gene in module if gene.upper() in lookup]
    indices = [lookup[gene.upper()] for gene in genes]

    obs_names = np.asarray(adata.obs_names.astype(str))
    positions = np.flatnonzero(np.fromiter((name in candidate_ids for name in obs_names), dtype=bool))
    if len(positions) != len(candidate_ids):
        missing = candidate_ids.difference(obs_names[positions])
        raise RuntimeError(f"Candidate-to-H5AD mismatch: {len(missing)} IDs missing")

    gene_chunks: list[pd.DataFrame] = []
    for start in range(0, adata.n_obs, args.chunk_size):
        stop = min(start + args.chunk_size, adata.n_obs)
        left = int(np.searchsorted(positions, start, side="left"))
        right = int(np.searchsorted(positions, stop, side="left"))
        if left == right:
            continue
        block = matrix[start:stop]
        block = block[positions[left:right] - start][:, indices]
        values = block.toarray() if sparse.issparse(block) else np.asarray(block)
        frame = pd.DataFrame(values, columns=[f"umi_{gene}" for gene in genes])
        frame.insert(0, "cell_id", obs_names[positions[left:right]])
        gene_chunks.append(frame)
        print(f"[B-LINEAGE-REFINE] {stop:,}/{adata.n_obs:,} cells", flush=True)

    gene_profiles = pd.concat(gene_chunks, ignore_index=True)
    profile = candidates.merge(gene_profiles, on="cell_id", how="left", validate="one_to_one")
    if profile[[f"umi_{gene}" for gene in genes]].isna().any().any():
        raise RuntimeError("Gene-level candidate profile contains missing values")

    for name, module_genes in MODULES.items():
        columns = [f"umi_{gene}" for gene in module_genes if gene in genes]
        profile[f"{name}_detected_refined"] = profile[columns].gt(0).sum(axis=1)
        profile[f"{name}_umi_refined"] = profile[columns].sum(axis=1)

    profile["core_b_identity"] = (
        profile["core_b_detected_refined"].ge(2) & profile["core_b_umi_refined"].ge(2)
    )
    profile["plasma_like_program"] = (
        profile["core_plasma_detected_refined"].ge(2) & profile["core_plasma_umi_refined"].ge(2)
    )
    profile["core_b_identity_low_non_b"] = (
        profile["core_b_identity"]
        & profile["non_b_detected_refined"].le(1)
        & profile["non_b_umi_refined"].le(2)
    )
    profile.to_csv(output / "07_blineage_candidate_gene_profiles.csv.gz", index=False, compression="gzip")

    label_summary = (
        profile.groupby("cell_type", observed=False)
        .agg(
            strict_candidates=("cell_id", "size"),
            core_b_identity=("core_b_identity", "sum"),
            plasma_like_program=("plasma_like_program", "sum"),
            core_b_identity_low_non_b=("core_b_identity_low_non_b", "sum"),
            median_core_b_detected=("core_b_detected_refined", "median"),
            median_shared_apc_detected=("shared_apc_detected_refined", "median"),
            median_non_b_detected=("non_b_detected_refined", "median"),
        )
        .reset_index()
    )
    label_summary["cell_type"] = label_summary["cell_type"].astype(str)
    label_summary["core_b_identity_fraction"] = (
        label_summary["core_b_identity"] / label_summary["strict_candidates"]
    )
    label_summary.to_csv(output / "08_blineage_refined_candidates_by_source_label.csv", index=False)

    prevalence_rows = []
    for label, group in profile.groupby("cell_type", observed=False):
        for gene in genes:
            prevalence_rows.append(
                {
                    "cell_type": str(label),
                    "gene": gene,
                    "candidate_cells": len(group),
                    "detected_cells": int(group[f"umi_{gene}"].gt(0).sum()),
                    "detected_fraction": float(group[f"umi_{gene}"].gt(0).mean()),
                    "median_umi_among_detected": float(
                        group.loc[group[f"umi_{gene}"].gt(0), f"umi_{gene}"].median()
                    ),
                }
            )
    pd.DataFrame(prevalence_rows).to_csv(output / "09_blineage_candidate_gene_prevalence.csv", index=False)

    strict_count = len(profile)
    identity_count = int(profile["core_b_identity"].sum())
    clean_count = int(profile["core_b_identity_low_non_b"].sum())
    plasma_program_count = int(profile["plasma_like_program"].sum())
    source_b_count = 152981
    decision = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "strict_candidates": strict_count,
        "core_b_identity_candidates": identity_count,
        "core_b_identity_fraction_of_strict": identity_count / strict_count,
        "core_b_identity_fraction_of_source_b_input": identity_count / source_b_count,
        "core_b_identity_low_non_b": clean_count,
        "plasma_like_program_candidates_not_counted_as_identity": plasma_program_count,
        "input_policy": "SOURCE_B_LABELS_PRIMARY_WITH_CANDIDATE_MAPPING_SENSITIVITY",
        "automatic_append_authorized": False,
        "protected_outcomes_used": False,
        "next_required_evidence": "map refined candidates into the disease-blind Gate C2B2 state graph",
    }
    (output / "11_BLINEAGE_INPUT_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )

    plot = label_summary.sort_values("strict_candidates")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.barh(plot["cell_type"], plot["strict_candidates"], color="#BBBBBB", label="Initial strict rule")
    ax.barh(plot["cell_type"], plot["core_b_identity"], color="#4477AA", label="Core BCR identity")
    ax.barh(
        plot["cell_type"],
        plot["core_b_identity_low_non_b"],
        color="#228833",
        label="Core BCR + low non-B",
    )
    ax.set(xlabel="Candidate cells", ylabel="Source cell type")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(figures / "blineage_candidate_refinement.png", dpi=300, facecolor="white")
    fig.savefig(figures / "blineage_candidate_refinement.pdf", facecolor="white")
    plt.close(fig)

    report = f"""# B-lineage candidate refinement and input decision

**Decision:** `SOURCE_B_LABELS_PRIMARY_WITH_CANDIDATE_MAPPING_SENSITIVITY`

- Initial strict candidates outside source B labels: {strict_count:,}
- Candidates supported by at least two core B-receptor genes: {identity_count:,} ({identity_count / strict_count:.2%})
- Core-BCR-supported candidates with low non-B signal: {clean_count:,} ({clean_count / strict_count:.2%})
- Core-BCR-supported candidates relative to the 152,981-cell source B-lineage input: {identity_count / source_b_count:.2%}
- Candidates with a plasma-like program, retained as context rather than identity evidence: {plasma_program_count:,}
- Disease or outcome fields used: none

## Binding decision

The original strict rule is deliberately sensitive and is not sufficiently
specific for automatic relabeling because shared APC and supporting B genes can
be detected in dendritic populations. Plasma-associated genes are also kept
separate from identity because they are prominent among source pDC labels. The primary Gate C2B2 input
therefore remains the source `B cell` plus `plasmablast` definition after hard
QC. Refined candidates are retained as a prespecified mapping sensitivity and
must be projected onto the disease-blind state graph. Expansion is authorized
only if core-identity-supported candidates form a coherent B-cell population
rather than dispersed APC or mixed-lineage profiles.
"""
    (output / "10_BLINEAGE_INPUT_DECISION.md").write_text(report, encoding="utf-8")
    adata.file.close()
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
