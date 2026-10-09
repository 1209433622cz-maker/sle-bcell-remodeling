#!/usr/bin/env python3
"""Freeze RP v3 Stage 0B contracts and materialize the disease-blind A2 input."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


SEED = 20261009
IFN_PROGRAM = (
    "IFI44L", "IFI6", "IFIT1", "IFIT2", "IFIT3", "IRF7",
    "ISG15", "LY6E", "MX1", "MX2", "OAS1", "OAS2",
)


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n", encoding="utf-8-sig")


def bool_series(series):
    return series.astype(str).str.lower().map({"true": True, "false": False}).fillna(False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd
    import scanpy as sc
    from scipy import sparse

    workspace = Path(args.workspace).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    a2_dir = output / "a2_rebuild"
    a2_dir.mkdir(parents=True, exist_ok=True)

    raw_path = workspace / "phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad"
    primary_path = workspace / "phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad"
    recurrence_path = workspace / "phase17_v7/gateC2B2/20260812_full_representation/01_hvg_recurrence_table.csv"
    prep_contract_path = workspace / "phase17_v7/gateC2B2/20260812_full_representation/04_GATE_C2B2_PREPARATION.json"
    program_path = workspace / "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/11_program_dictionary.csv"
    external_genes_path = workspace / "Data/processed/GSE135779_nehar_validation/source/GSE135779_genes.tsv.gz"
    required = [
        raw_path, primary_path, recurrence_path, prep_contract_path, program_path,
        external_genes_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Stage 0B inputs: " + ", ".join(missing))

    created_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    programs = pd.read_csv(program_path, encoding="utf-8-sig")
    a1 = programs.loc[programs["program_id"] == "NAIVE_TO_MEMORY_AXIS"].copy()
    if len(a1) != 14 or set(a1["sign"].astype(int)) != {-1, 1}:
        raise RuntimeError("Frozen A1 dictionary is not the expected 14-gene signed dictionary")
    a1["stage0b_role"] = "continuous_identity_axis"
    a1["score_orientation"] = np.where(
        a1["sign"].astype(int) > 0, "positive_memory_direction", "negative_naive_direction"
    )
    a1["outcome_adaptive"] = False
    write_csv(a1, output / "02_A1_CONTINUOUS_AXIS_DICTIONARY.csv")

    recurrence = pd.read_csv(recurrence_path, encoding="utf-8-sig")
    a2_mask = bool_series(recurrence["hvg_isg_excluded"])
    a2_features = recurrence.loc[a2_mask].copy()
    if len(a2_features) != 3000:
        raise RuntimeError(f"Expected 3,000 A2 features, found {len(a2_features):,}")
    if bool_series(a2_features["is_strong_isg"]).any():
        raise RuntimeError("A2 feature list contains strong ISG genes")
    write_csv(a2_features, output / "03_A2_FROZEN_FEATURES.csv")

    raw = ad.read_h5ad(raw_path)
    primary = ad.read_h5ad(primary_path)
    if not raw.obs_names.equals(primary.obs_names):
        raise RuntimeError("Raw and primary representation cell order differs")
    if raw.n_obs != 150_402 or raw.n_vars != 30_172:
        raise RuntimeError(f"Unexpected raw shape: {raw.shape}")
    if list(raw.obs.columns) != [
        "source_cell_index", "donor_id", "sample_uuid", "library_uuid", "Processing_Cohort"
    ]:
        raise RuntimeError("Raw disease-blind H5AD contains unexpected observation columns")

    score_table = primary.obs[[
        "source_cell_index", "library_uuid", "residual_doublet_score",
        "residual_doublet_auto_call",
    ]].copy()
    score_table.insert(0, "cell_id", score_table.index.astype(str))
    score_table = score_table.rename(columns={
        "residual_doublet_score": "doublet_score",
        "residual_doublet_auto_call": "predicted_doublet",
    })
    write_csv(score_table, output / "04_RECONSTRUCTED_RESIDUAL_DOUBLET_SCORES.csv.gz")

    raw_index = pd.Index(raw.var_names.astype(str))
    requested = pd.Index(a2_features["var_name"].astype(str))
    positions = raw_index.get_indexer(requested)
    if (positions < 0).any():
        missing_features = requested[positions < 0].tolist()
        raise RuntimeError(f"A2 features missing from raw H5AD: {missing_features[:10]}")
    a2_prepared_path = a2_dir / "03_a2_prepared.h5ad"
    rebuild_a2 = True
    if a2_prepared_path.exists():
        existing = ad.read_h5ad(a2_prepared_path)
        metadata = existing.uns.get("phase17_c2b2_preparation", {})
        rebuild_a2 = not (
            existing.shape == (150_402, 3_000)
            and metadata.get("disease_blind") is True
            and metadata.get("normalization_background_genes") == len(recurrence)
            and metadata.get("normalization")
            == "full_16357_gene_filtered_background_cp10k_then_log1p"
        )
    if rebuild_a2:
        a2 = raw[:, positions].copy()
        a2.obs["residual_doublet_score"] = primary.obs["residual_doublet_score"].to_numpy(float)
        a2.obs["residual_doublet_auto_call"] = primary.obs[
            "residual_doublet_auto_call"
        ].to_numpy(bool)
        a2.obs["analysis_branch_primary"] = "all_hard_qc"
        a2.obs["analysis_branch_singlet_sensitivity"] = np.where(
            a2.obs["residual_doublet_auto_call"].to_numpy(bool), "excluded", "included"
        )
        recurrence_index = a2_features.set_index("var_name")
        for column in (
            "gene_id", "feature_name", "highly_variable", "highly_variable_nbatches",
            "means", "dispersions", "dispersions_norm", "is_mitochondrial",
            "is_ribosomal", "is_hemoglobin", "is_stress", "is_cell_cycle",
            "is_immunoglobulin", "is_strong_isg", "hvg_primary",
            "hvg_isg_excluded", "hvg_union",
        ):
            if column in recurrence_index:
                values = recurrence_index.loc[a2.var_names, column]
                if column.startswith("is_") or column.startswith("hvg_") or column == "highly_variable":
                    values = bool_series(values)
                a2.var[column] = values.to_numpy()
        a2.var["hvg_isg_excluded"] = True
        background_positions = raw_index.get_indexer(
            pd.Index(recurrence["var_name"].astype(str))
        )
        if (background_positions < 0).any():
            raise RuntimeError("Frozen 16,357-gene normalization background is incomplete")
        background_totals = np.asarray(
            raw.X[:, background_positions].sum(axis=1)
        ).ravel().astype(float)
        if (background_totals <= 0).any():
            raise RuntimeError("A cell has zero counts in the frozen normalization background")
        factors = 1e4 / background_totals
        a2.X = sparse.diags(factors) @ a2.X.tocsr()
        a2.X.data = np.log1p(a2.X.data)
        a2.uns["phase17_c2b2_preparation"] = {
            "schema_version": 2,
            "created_at": created_at,
            "status": "STAGE0B_A2_MATERIALIZED_FROM_FROZEN_FEATURE_LIST",
            "disease_blind": True,
            "source_raw_h5ad_sha256": sha256_file(raw_path),
            "source_frozen_feature_sha256": sha256_file(recurrence_path),
            "cells": int(a2.n_obs),
            "genes": int(a2.n_vars),
            "normalization": "full_16357_gene_filtered_background_cp10k_then_log1p",
            "normalization_background_genes": int(len(recurrence)),
            "feature_policy": "historical hvg_isg_excluded flag; no HVG reselection",
            "strong_isg_features": int(a2.var["is_strong_isg"].sum()),
            "protected_outcome_columns": [],
            "seed": SEED,
        }
        a2.write_h5ad(a2_prepared_path, compression="gzip")
    else:
        check = existing

    external_genes = pd.read_csv(
        external_genes_path, sep="\t", header=None, names=["ensembl_id", "gene_symbol"]
    )
    discovery_symbols = raw.var["feature_name"].astype(str).str.upper()
    external_symbols = external_genes["gene_symbol"].astype(str).str.upper()
    shared_background = sorted(
        (set(discovery_symbols) & set(external_symbols)) - {"", "NAN", "NONE"}
    )
    if len(shared_background) < 4_000:
        raise RuntimeError(f"Insufficient fixed rank background: {len(shared_background):,}")

    a1_contract = {
        "created_at": created_at,
        "status": "FROZEN_FOR_STAGE0B",
        "outcome_blind": True,
        "input": "raw non-negative integer single-cell counts",
        "cell_normalization": "full-library counts normalized to 10,000 then log1p",
        "gene_standardization": "gene-wise mean and population SD across all 150,402 disease-blind cells",
        "formula": "mean(z of seven positive genes) minus mean(z of seven negative genes)",
        "orientation": "positive values indicate the frozen memory-directed marker pole",
        "hard_subtype_authorized": False,
        "technical_support_bins": "five global A1 quantile bins; audit scaffold only",
        "gene_availability_rule": "at least 80% of genes in each sign; observed 7/7 and 7/7",
        "dictionary_sha256": sha256_file(program_path),
    }
    write_json(a1_contract, output / "02_A1_CONTINUOUS_AXIS_CONTRACT.json")

    a2_contract = {
        "created_at": created_at,
        "status": "FROZEN_AND_MATERIALIZED_FOR_STAGE0B",
        "outcome_blind": True,
        "feature_policy": "historical hvg_isg_excluded",
        "features": 3_000,
        "strong_isg_features": 0,
        "immunoglobulin_features": int(bool_series(a2_features["is_immunoglobulin"]).sum()),
        "technical_nuisance_features": int(
            (
                bool_series(a2_features["is_mitochondrial"])
                | bool_series(a2_features["is_ribosomal"])
                | bool_series(a2_features["is_hemoglobin"])
                | bool_series(a2_features["is_stress"])
                | bool_series(a2_features["is_cell_cycle"])
            ).sum()
        ),
        "normalization": "full 16,357-gene filtered background cp10k then log1p; A2 subset afterward",
        "pca": "randomized PCA, up to 50 components",
        "integration": "Harmony by library_uuid; max_iter=20; seed=20260806",
        "neighbors": 15,
        "identity_resolution": 0.4,
        "minimal_trial": "one full-cell A2 rebuild; no disease fields; no disease-effect inspection",
        "prepared_h5ad": str(a2_prepared_path),
        "prepared_h5ad_sha256": sha256_file(a2_prepared_path),
        "frozen_features_sha256": sha256_file(output / "03_A2_FROZEN_FEATURES.csv"),
    }
    write_json(a2_contract, output / "03_A2_REPRESENTATION_CONTRACT.json")

    score_contracts = {
        "created_at": created_at,
        "status": "FROZEN_FOR_STAGE0B",
        "program_members": list(IFN_PROGRAM),
        "duplicate_symbol_policy": "sum all matching features before normalization",
        "T0": {
            "purpose": "same scoring transform across A0, A1 and A2 annotation branches",
            "input": "sample-cohort B_CONV/state pseudobulk raw counts",
            "transform": "log2(full-background CPM + 0.5)",
            "reference": "A0 primary normal-control strata, fixed once",
            "score": "mean of 12 reference-standardized IFN/ISG genes",
            "branch_restandardization": False,
        },
        "T_frozen": {
            "purpose": "external transfer without external outcome-dependent restandardization",
            "input": "external source-label B_CONV donor pseudobulk raw counts",
            "transform": "log2(full measured-library CPM + 0.5)",
            "reference": "the same discovery A0 normal-control gene means and SDs used by T0",
            "external_restandardization": False,
        },
        "T_rank": {
            "purpose": "platform-robust sensitivity",
            "background": "fixed disease-blind intersection of discovery and external gene symbols",
            "background_size": len(shared_background),
            "ties": "average percentile rank after duplicate-symbol sum",
            "score": "mean percentile rank of all 12 IFN/ISG genes",
            "minimum_program_coverage": "12/12",
        },
    }
    write_json(score_contracts, output / "04_SCORE_CONTRACTS.json")
    write_csv(pd.DataFrame({"gene_symbol": shared_background}), output / "04_T_RANK_BACKGROUND.csv.gz")

    support_contract = {
        "created_at": created_at,
        "status": "FROZEN_FOR_TECHNICAL_IDENTIFIABILITY_TRIAL",
        "technical_state_scaffold": "five global quantile bins of continuous A1; not biological subtypes",
        "minimum_cells_per_donor_bin": 30,
        "minimum_independent_donors_per_bin_overall": 20,
        "future_inferential_minimum_donors_per_comparison_arm": 10,
        "failure_policy": "drop unsupported donor-bin rows and report support; never merge after effect inspection",
        "common_support": "only bins meeting the prespecified support rule in every compared branch",
        "pi_ref": "pooled A1-bin composition across eligible A0 normal-control donor strata",
        "pi_ref_freeze_timing": "computed in the Stage 0B trial before any disease coefficient is estimated",
        "publication_state_labels_authorized": False,
    }
    write_json(support_contract, output / "05_COMMON_SUPPORT_AND_PI_REF_CONTRACT.json")

    simulation_contract = {
        "created_at": created_at,
        "status": "SCENARIOS_AND_OUTPUTS_FROZEN; FULL_ACCEPTANCE_THRESHOLDS_DEFERRED",
        "seed": SEED,
        "technical_replicates_per_scenario": 400,
        "planned_full_replicates_per_scenario": 2_000,
        "scenarios": [
            "null", "composition_only", "within_state_only",
            "composition_and_within_same_direction", "composition_and_within_opposite_direction",
        ],
        "estimands": [
            "broad_compartment_difference", "common_composition_standardized_difference",
            "state_specific_differences",
        ],
        "required_outputs": [
            "bias", "rmse", "empirical_95pct_coverage", "sign_error",
            "fit_failure_rate", "truth_recovery_direction",
        ],
        "technical_pass_rule": "all scenarios complete; finite outputs; analytic truth reproduced within Monte Carlo tolerance",
        "full_G2_note": "technical completion does not authorize a G2 PASS or publication inference",
    }
    write_json(simulation_contract, output / "06_SIMULATION_CONTRACT.json")

    manifest_rows = []
    for path in sorted(output.glob("*.json")) + sorted(output.glob("*.csv")) + sorted(output.glob("*.csv.gz")):
        if path.name == "00_STAGE0B_RUN_STATUS.json":
            continue
        manifest_rows.append({
            "file": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "role": "stage0b frozen contract or source inventory",
        })
    manifest_rows.extend([
        {
            "file": str(raw_path.relative_to(workspace)),
            "size_bytes": raw_path.stat().st_size,
            "sha256": sha256_file(raw_path),
            "role": "read-only discovery raw counts",
        },
        {
            "file": str(primary_path.relative_to(workspace)),
            "size_bytes": primary_path.stat().st_size,
            "sha256": sha256_file(primary_path),
            "role": "read-only historical primary representation",
        },
        {
            "file": str(a2_prepared_path.relative_to(workspace)),
            "size_bytes": a2_prepared_path.stat().st_size,
            "sha256": sha256_file(a2_prepared_path),
            "role": "new disease-blind A2 prepared checkpoint",
        },
    ])
    write_csv(pd.DataFrame(manifest_rows), output / "01_STAGE0B_INPUT_AND_CONTRACT_MANIFEST.csv")

    protocol = f"""# RP v3 Stage 0B protocol freeze

**Status:** `PROTOCOL_FROZEN_MINIMAL_TRIAL_PENDING`

- A1 is a continuous 14-gene identity axis. It is not a hard subtype and has no disease-adaptive cutpoint.
- A2 is the historical 3,000-HVG IFN-excluded representation rebuilt from the frozen feature list.
- T0 uses one discovery-control reference and cannot be restandardized by annotation branch.
- T_frozen transfers the same discovery reference to GSE135779 without external outcome-dependent scaling.
- T_rank is a fixed-background percentile-rank sensitivity over {len(shared_background):,} shared symbols.
- Five A1 quantile bins are permitted only as a support/standardization scaffold, not biological states.
- The minimal trial may inspect coverage, alignment, score computability and simulation truth recovery.
- Disease coefficients and new biological claims remain locked until the post-trial gate review.

The A2 prepared checkpoint contains only technical identifiers and disease-blind representation fields.
No manuscript, figure, submission package, release or archive is modified by this workflow.
"""
    (output / "01_STAGE0B_PROTOCOL_FREEZE.md").write_text(protocol, encoding="utf-8")

    status = {
        "created_at": created_at,
        "status": "PROTOCOL_FROZEN_MINIMAL_TRIAL_PENDING",
        "g0a_input_recovery": "PASS",
        "g0b_protocol_freeze": "PASS_STAGE0B",
        "g1": "PENDING_MINIMAL_TRIAL",
        "a1_genes": int(len(a1)),
        "a2_features": int(len(a2_features)),
        "t_rank_background": int(len(shared_background)),
        "a2_prepared": str(a2_prepared_path),
        "disease_effects_inspected": False,
        "next": "RUN_A2_FIT_AND_STAGE0B_MINIMAL_TRIAL",
    }
    write_json(status, output / "00_STAGE0B_RUN_STATUS.json")
    print(json.dumps(status, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
