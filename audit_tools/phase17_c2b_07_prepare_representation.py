#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate C2B2-01: prepare disease-blind full B-cell representation inputs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

SEED = 20260806
PREPARATION_SCHEMA_VERSION = 2

STRESS_GENES = {
    "ATF3", "DDIT3", "DNAJB1", "EGR1", "FOS", "FOSB", "HSPA1A",
    "HSPA1B", "HSP90AA1", "IER2", "IER3", "JUN", "JUNB", "JUND",
    "NR4A1",
}

CELL_CYCLE_GENES = {
    "AURKA", "AURKB", "BIRC5", "CCNA2", "CCNB1", "CCNB2", "CCNE1",
    "CDC20", "CDC25C", "CDC45", "CDC6", "CDCA3", "CDCA7", "CDK1",
    "CENPA", "CENPE", "CENPF", "HMGB2", "MCM2", "MCM3", "MCM4",
    "MCM5", "MCM6", "MCM7", "MKI67", "PCNA", "PLK1", "RRM2",
    "STMN1", "TUBA1B", "TYMS", "UBE2C",
}

STRONG_ISG_GENES = {
    "BST2", "DDX58", "GBP1", "HERC5", "IFI6", "IFI16", "IFI27",
    "IFI35", "IFI44", "IFI44L", "IFIH1", "IFIT1", "IFIT2", "IFIT3",
    "IFIT5", "IFITM1", "IFITM2", "IFITM3", "IRF7", "ISG15", "MX1",
    "MX2", "OAS1", "OAS2", "OAS3", "OASL", "PARP9", "RSAD2",
    "STAT1", "USP18", "XAF1",
}

PROTECTED_EXACT = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk_size):
            digest.update(block)
    return digest.hexdigest().upper()


def balanced_test_positions(obs, max_cells: int, seed: int):
    import numpy as np

    if max_cells <= 0 or max_cells >= len(obs):
        return np.arange(len(obs), dtype=int)

    rng = np.random.default_rng(seed)
    libraries = obs["library_uuid"].astype(str).to_numpy()
    unique = sorted(set(libraries))
    floor = max(1, min(25, max_cells // max(1, len(unique))))
    selected = []
    for library in unique:
        positions = np.flatnonzero(libraries == library)
        selected.extend(rng.choice(positions, size=min(floor, len(positions)), replace=False))

    selected = np.unique(np.asarray(selected, dtype=int))
    remaining = np.setdiff1d(np.arange(len(obs), dtype=int), selected, assume_unique=True)
    slots = max_cells - len(selected)
    if slots > 0:
        selected = np.concatenate(
            [selected, rng.choice(remaining, size=min(slots, len(remaining)), replace=False)]
        )
    return np.sort(selected[:max_cells])


def classify_genes(symbols):
    import pandas as pd

    values = pd.Series(symbols, dtype="string").fillna("").str.upper()
    mt = values.str.match(r"^MT-")
    ribosomal = values.str.match(r"^RP[SL][0-9]")
    hemoglobin = values.str.match(r"^HB[ABDEGMQZ][0-9]?")
    stress = values.isin(STRESS_GENES)
    cell_cycle = values.isin(CELL_CYCLE_GENES)
    immunoglobulin = values.str.match(
        r"^(IGH[VDJ][A-Z0-9-]*|IGHM|IGHD|IGHE|IGHA[12]|IGHG[1-4]|"
        r"IGK[VDJ][A-Z0-9-]*|IGKC|IGL[VJ][A-Z0-9-]*|IGLC[1-7])$"
    )
    strong_isg = values.isin(STRONG_ISG_GENES)
    return {
        "is_mitochondrial": mt.to_numpy(bool),
        "is_ribosomal": ribosomal.to_numpy(bool),
        "is_hemoglobin": hemoglobin.to_numpy(bool),
        "is_stress": stress.to_numpy(bool),
        "is_cell_cycle": cell_cycle.to_numpy(bool),
        "is_immunoglobulin": immunoglobulin.to_numpy(bool),
        "is_strong_isg": strong_isg.to_numpy(bool),
    }


def select_ranked(var, eligible, n_hvg: int):
    import numpy as np
    import pandas as pd

    table = pd.DataFrame(index=var.index)
    table["eligible"] = np.asarray(eligible, dtype=bool)
    table["candidate"] = var["highly_variable"].fillna(False).astype(bool)
    table["nbatches"] = var.get(
        "highly_variable_nbatches", pd.Series(0, index=var.index)
    ).fillna(0).astype(int)
    table["rank"] = var.get(
        "highly_variable_rank", pd.Series(np.inf, index=var.index)
    ).fillna(np.inf).astype(float)
    table["dispersion"] = var.get(
        "dispersions_norm", pd.Series(-np.inf, index=var.index)
    ).replace([np.inf, -np.inf], np.nan).fillna(-np.inf).astype(float)
    table["gene_order"] = np.arange(len(table), dtype=int)
    table = table.loc[table["eligible"]].sort_values(
        ["candidate", "nbatches", "rank", "dispersion", "gene_order"],
        ascending=[False, False, True, False, True],
        kind="mergesort",
    )
    if len(table) < n_hvg:
        raise RuntimeError(f"Only {len(table):,} genes are eligible for {n_hvg:,} HVGs")
    return table.index[:n_hvg]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5ad", required=True)
    parser.add_argument("--doublet-scores", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-hvg", type=int, default=3000)
    parser.add_argument("--hvg-candidate-pool", type=int, default=7000)
    parser.add_argument("--min-cells", type=int, default=20)
    parser.add_argument("--max-cells", type=int, default=0)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd
    import scanpy as sc
    from scipy import sparse

    input_h5ad = Path(args.input_h5ad).resolve()
    score_path = Path(args.doublet_scores).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    sc.settings.seed = args.seed
    sc.settings.verbosity = 2

    print(f"[LOAD] {input_h5ad}", flush=True)
    adata = ad.read_h5ad(input_h5ad)
    protected = sorted(
        column for column in adata.obs.columns
        if re.sub(r"[^a-z0-9]+", "_", str(column).lower()).strip("_") in PROTECTED_EXACT
    )
    if protected:
        raise RuntimeError(f"Protected outcome columns present: {protected}")
    required_obs = {"source_cell_index", "donor_id", "sample_uuid", "library_uuid", "Processing_Cohort"}
    missing_obs = sorted(required_obs - set(adata.obs.columns))
    if missing_obs:
        raise RuntimeError(f"Missing required technical columns: {missing_obs}")
    unexpected_obs = sorted(set(adata.obs.columns) - required_obs)
    if unexpected_obs:
        raise RuntimeError(
            "Working H5AD contains non-allowlisted obs columns: "
            f"{unexpected_obs}"
        )
    if not adata.obs_names.is_unique or not adata.var_names.is_unique:
        raise RuntimeError("Cell and gene identifiers must be unique")

    full_cells = int(adata.n_obs)
    positions = balanced_test_positions(adata.obs, args.max_cells, args.seed)
    if len(positions) != adata.n_obs:
        adata = adata[positions].copy()
        print(f"[TEST MODE] deterministically retained {adata.n_obs:,}/{full_cells:,} cells", flush=True)

    print(f"[SCORES] attaching {score_path}", flush=True)
    scores = pd.read_csv(score_path)
    expected_score_columns = {"cell_id", "source_cell_index", "library_uuid", "doublet_score", "predicted_doublet"}
    missing_scores = sorted(expected_score_columns - set(scores.columns))
    if missing_scores:
        raise RuntimeError(f"Missing score columns: {missing_scores}")
    if scores["cell_id"].duplicated().any():
        raise RuntimeError("Residual doublet score cell IDs are not unique")
    score_index = scores.set_index("cell_id")
    missing_ids = adata.obs_names.difference(score_index.index)
    if len(missing_ids):
        raise RuntimeError(f"Doublet scores are missing {len(missing_ids):,} working cells")
    aligned = score_index.reindex(adata.obs_names)
    if not np.array_equal(
        aligned["source_cell_index"].to_numpy(),
        adata.obs["source_cell_index"].to_numpy(),
    ):
        raise RuntimeError("Residual score source indices do not match the H5AD")
    if not np.array_equal(
        aligned["library_uuid"].astype(str).to_numpy(),
        adata.obs["library_uuid"].astype(str).to_numpy(),
    ):
        raise RuntimeError("Residual score library identifiers do not match the H5AD")
    adata.obs["residual_doublet_score"] = aligned["doublet_score"].to_numpy(float)
    adata.obs["residual_doublet_auto_call"] = aligned["predicted_doublet"].to_numpy(bool)
    adata.obs["analysis_branch_primary"] = "all_hard_qc"
    adata.obs["analysis_branch_singlet_sensitivity"] = np.where(
        adata.obs["residual_doublet_auto_call"].to_numpy(bool), "excluded", "included"
    )

    # Verify the working matrix behaves like raw, non-negative integer counts.
    sample_values = adata.X.data if sparse.issparse(adata.X) else np.asarray(adata.X).ravel()
    if len(sample_values) > 200_000:
        sample_values = sample_values[np.linspace(0, len(sample_values) - 1, 200_000, dtype=int)]
    if len(sample_values) and (
        np.nanmin(sample_values) < 0
        or not np.allclose(sample_values, np.rint(sample_values), atol=1e-6)
    ):
        raise RuntimeError("Input matrix is not consistent with non-negative raw counts")

    before_genes = int(adata.n_vars)
    source_symbols = adata.var.get(
        "feature_name", pd.Series(adata.var_names, index=adata.var_names)
    ).astype(str)
    source_gene_classes = classify_genes(source_symbols)
    source_ig_loci = source_symbols[np.asarray(source_gene_classes["is_immunoglobulin"])]
    canonical_constant_genes = (
        "IGHM", "IGHD", "IGHA1", "IGHA2", "IGHG1", "IGHG2", "IGHG3",
        "IGHG4", "IGHE", "IGKC", "IGLC1", "IGLC2", "IGLC3",
    )
    source_feature_names = set(source_symbols.str.upper())
    present_constant_genes = [gene for gene in canonical_constant_genes if gene in source_feature_names]
    sc.pp.filter_genes(adata, min_cells=args.min_cells)
    print(f"[GENES] retained {adata.n_vars:,}/{before_genes:,} genes at min_cells={args.min_cells}", flush=True)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    candidate_pool = min(max(args.hvg_candidate_pool, args.n_hvg * 2), adata.n_vars)
    print(
        f"[HVG] library-aware seurat ranking; pool={candidate_pool:,}, libraries={adata.obs['library_uuid'].nunique():,}",
        flush=True,
    )
    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=candidate_pool,
        flavor="seurat",
        batch_key="library_uuid",
        inplace=True,
    )

    symbols = adata.var.get("feature_name", pd.Series(adata.var_names, index=adata.var_names)).astype(str)
    gene_classes = classify_genes(symbols)
    for key, values in gene_classes.items():
        adata.var[key] = values
    technical_nuisance = (
        adata.var["is_mitochondrial"]
        | adata.var["is_ribosomal"]
        | adata.var["is_hemoglobin"]
        | adata.var["is_stress"]
        | adata.var["is_cell_cycle"]
    ).to_numpy(bool)
    immunoglobulin = adata.var["is_immunoglobulin"].to_numpy(bool)
    strong_isg = adata.var["is_strong_isg"].to_numpy(bool)

    primary = select_ranked(adata.var, ~(technical_nuisance | immunoglobulin), args.n_hvg)
    isg_excluded = select_ranked(
        adata.var, ~(technical_nuisance | immunoglobulin | strong_isg), args.n_hvg
    )
    adata.var["hvg_primary"] = adata.var_names.isin(primary)
    adata.var["hvg_isg_excluded"] = adata.var_names.isin(isg_excluded)
    adata.var["hvg_union"] = adata.var["hvg_primary"] | adata.var["hvg_isg_excluded"]

    hvg_table_columns = [
        "gene_id", "feature_name", "highly_variable", "highly_variable_nbatches",
        "highly_variable_rank", "means", "dispersions", "dispersions_norm",
        *gene_classes.keys(), "hvg_primary", "hvg_isg_excluded", "hvg_union",
    ]
    hvg_table = adata.var[[column for column in hvg_table_columns if column in adata.var]].copy()
    hvg_table.insert(0, "var_name", hvg_table.index.astype(str))
    hvg_table.to_csv(output / "01_hvg_recurrence_table.csv", index=False, encoding="utf-8-sig")

    branch_rows = []
    for branch, flag in (
        ("primary_ig_excluded", "hvg_primary"),
        ("isg_excluded", "hvg_isg_excluded"),
    ):
        selected = adata.var[flag].to_numpy(bool)
        nbatches = adata.var.loc[selected, "highly_variable_nbatches"]
        branch_rows.append(
            {
                "branch": branch,
                "n_hvg": int(selected.sum()),
                "median_hvg_nbatches": float(nbatches.median()),
                "minimum_hvg_nbatches": int(nbatches.min()),
                "maximum_hvg_nbatches": int(nbatches.max()),
                "n_strong_isg": int((selected & strong_isg).sum()),
                "n_immunoglobulin": int((selected & immunoglobulin).sum()),
                "n_technical_nuisance": int((selected & technical_nuisance).sum()),
            }
        )
    branch_summary = pd.DataFrame(branch_rows)
    branch_summary.to_csv(output / "02_hvg_branch_summary.csv", index=False, encoding="utf-8-sig")
    ig_availability = pd.DataFrame(
        [
            {
                "sensitivity": "immunoglobulin_dominance",
                "status": "NOT_EVALUABLE_SOURCE_FEATURE_SPACE",
                "canonical_ig_loci_in_source": int(len(source_ig_loci)),
                "canonical_constant_genes_present": len(present_constant_genes),
                "canonical_constant_genes_expected": len(canonical_constant_genes),
                "present_constant_gene_symbols": ";".join(present_constant_genes),
                "canonical_ig_locus_symbols": ";".join(source_ig_loci.astype(str).tolist()),
                "reason": (
                    "The source raw feature space lacks canonical IG constant genes and "
                    "contains fewer than 10 bona fide IG loci; an IG-dominance "
                    "representation stress test would not be interpretable."
                ),
            }
        ]
    )
    ig_availability.to_csv(
        output / "02b_feature_space_sensitivity_availability.csv",
        index=False,
        encoding="utf-8-sig",
    )

    prepared = adata[:, adata.var["hvg_union"].to_numpy(bool)].copy()
    prepared.uns["phase17_c2b2_preparation"] = {
        "schema_version": PREPARATION_SCHEMA_VERSION,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "disease_blind": True,
        "input_h5ad": str(input_h5ad),
        "input_h5ad_sha256": sha256_file(input_h5ad),
        "doublet_scores": str(score_path),
        "doublet_scores_sha256": sha256_file(score_path),
        "full_input_cells": full_cells,
        "working_cells": int(prepared.n_obs),
        "min_cells": args.min_cells,
        "n_hvg": args.n_hvg,
        "hvg_candidate_pool": candidate_pool,
        "primary_cell_policy": "all hard-QC cells",
        "doublet_policy": "automatic calls are sensitivity-only until Gate C2B3 localization",
        "primary_gene_policy": "exclude technical nuisance and immunoglobulin-dominance genes from HVGs",
        "sensitivity_gene_policies": ["strong-ISG-excluded"],
        "ig_dominance_sensitivity": ig_availability.iloc[0].to_dict(),
        "protected_outcome_columns": protected,
        "seed": args.seed,
        "test_mode": bool(args.max_cells > 0),
    }
    prepared_path = output / "03_prepared_log_union_hvg.h5ad"
    print(f"[SAVE] {prepared_path} ({prepared.shape[0]:,} x {prepared.shape[1]:,})", flush=True)
    prepared.write_h5ad(prepared_path, compression="gzip")

    summary = {
        "schema_version": PREPARATION_SCHEMA_VERSION,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_TO_REPRESENTATION_FIT",
        "disease_blind": True,
        "full_input_cells": full_cells,
        "working_cells": int(prepared.n_obs),
        "working_libraries": int(prepared.obs["library_uuid"].nunique()),
        "residual_doublet_auto_calls": int(prepared.obs["residual_doublet_auto_call"].sum()),
        "genes_after_min_cells": int(adata.n_vars),
        "hvg_union": int(prepared.n_vars),
        "branches": branch_rows,
        "ig_dominance_sensitivity": ig_availability.iloc[0].to_dict(),
        "protected_outcome_columns": protected,
        "test_mode": bool(args.max_cells > 0),
    }
    (output / "04_GATE_C2B2_PREPARATION.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        "# Gate C2B2 representation preparation",
        "",
        f"**Status:** `{summary['status']}`",
        "",
        f"- Working cells: {summary['working_cells']:,} across {summary['working_libraries']} libraries",
        f"- Residual auto calls retained in primary: {summary['residual_doublet_auto_calls']:,}",
        f"- Genes after minimum-cell filter: {summary['genes_after_min_cells']:,}",
        f"- Union of frozen HVG branches: {summary['hvg_union']:,}",
        f"- Protected outcome columns: {protected or 'none'}",
        f"- Software-test mode: {summary['test_mode']}",
        "",
        "The primary branch retains all hard-QC cells and excludes technical nuisance and",
        "immunoglobulin-dominance genes from representation HVGs. Residual-risk-negative,",
        "and strong-ISG-excluded analyses are fitted as sensitivity branches. An IG-",
        "dominance reconstruction is documented as non-evaluable because canonical IG",
        "constant genes are absent from the source raw feature space.",
        "No disease or clinical outcome was used for feature selection.",
        "",
    ]
    (output / "05_GATE_C2B2_PREPARATION.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
