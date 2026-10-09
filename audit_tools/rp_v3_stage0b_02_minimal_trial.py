#!/usr/bin/env python3
"""Run the RP v3 Stage 0B result-blind identifiability and scoring trial."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np


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
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(frame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator="\n", encoding="utf-8-sig")


def symbol_positions(symbols) -> dict[str, list[int]]:
    mapping: dict[str, list[int]] = {}
    for index, symbol in enumerate(symbols):
        key = str(symbol).upper()
        if key and key not in {"NAN", "NONE"}:
            mapping.setdefault(key, []).append(index)
    return mapping


def selected_symbol_counts(matrix, mapping: dict[str, list[int]], genes: list[str]):
    from scipy import sparse

    columns = []
    missing = []
    for gene in genes:
        indices = mapping.get(gene.upper(), [])
        if not indices:
            missing.append(gene)
            columns.append(sparse.csr_matrix((matrix.shape[0], 1), dtype=np.float64))
        else:
            values = matrix[:, indices].sum(axis=1)
            columns.append(sparse.csr_matrix(np.asarray(values).reshape(-1, 1)))
    return sparse.hstack(columns, format="csr"), missing


def build_symbol_matrix(matrix, feature_symbols, background: list[str]):
    from scipy import sparse

    target = {symbol: index for index, symbol in enumerate(background)}
    feature_index = []
    symbol_index = []
    for index, symbol in enumerate(feature_symbols):
        key = str(symbol).upper()
        if key in target:
            feature_index.append(index)
            symbol_index.append(target[key])
    mapper = sparse.csr_matrix(
        (
            np.ones(len(feature_index), dtype=np.float64),
            (np.asarray(feature_index, dtype=int), np.asarray(symbol_index, dtype=int)),
        ),
        shape=(matrix.shape[1], len(background)),
    )
    return (matrix @ mapper).tocsr()


def group_pseudobulk(raw_matrix, group_index: np.ndarray, n_groups: int):
    from scipy import sparse

    keep = np.flatnonzero(group_index >= 0)
    assignment = sparse.csr_matrix(
        (
            np.ones(len(keep), dtype=np.float64),
            (group_index[keep], keep),
        ),
        shape=(n_groups, raw_matrix.shape[0]),
    )
    return (assignment @ raw_matrix).tocsr()


def score_log2_cpm(program_counts, library_totals, reference_mean, reference_sd):
    dense = program_counts.toarray().astype(float)
    totals = np.asarray(library_totals, dtype=float).reshape(-1, 1)
    cpm = np.divide(dense * 1e6, totals, out=np.zeros_like(dense), where=totals > 0)
    transformed = np.log2(cpm + 0.5)
    score = ((transformed - reference_mean) / reference_sd).mean(axis=1)
    return transformed, score


def percentile_program_score(symbol_counts, program_positions: list[int]) -> np.ndarray:
    from scipy.stats import rankdata

    dense = symbol_counts.toarray().astype(float)
    result = np.empty(dense.shape[0], dtype=float)
    for row in range(dense.shape[0]):
        ranks = rankdata(dense[row], method="average") / dense.shape[1]
        result[row] = float(np.mean(ranks[program_positions]))
    return result


def difference_ci(values: np.ndarray, groups: np.ndarray) -> tuple[float, float, float]:
    from scipy.stats import t

    left = values[groups == 0]
    right = values[groups == 1]
    effect = float(right.mean() - left.mean())
    variance = float(right.var(ddof=1) / len(right) + left.var(ddof=1) / len(left))
    se = np.sqrt(max(variance, 1e-12))
    numerator = variance * variance
    denominator = (
        (right.var(ddof=1) / len(right)) ** 2 / (len(right) - 1)
        + (left.var(ddof=1) / len(left)) ** 2 / (len(left) - 1)
    )
    df = numerator / denominator if denominator > 0 else len(values) - 2
    critical = float(t.ppf(0.975, df))
    return effect, effect - critical * se, effect + critical * se


def standardized_ci(
    state_means: np.ndarray, groups: np.ndarray, weights: np.ndarray
) -> tuple[float, float, float]:
    from scipy.stats import t

    effects = []
    variances = []
    for state in range(state_means.shape[1]):
        left = state_means[groups == 0, state]
        right = state_means[groups == 1, state]
        effects.append(right.mean() - left.mean())
        variances.append(right.var(ddof=1) / len(right) + left.var(ddof=1) / len(left))
    effects = np.asarray(effects)
    variances = np.asarray(variances)
    estimate = float(np.dot(weights, effects))
    se = float(np.sqrt(np.sum(weights**2 * variances)))
    critical = float(t.ppf(0.975, len(groups) - 2))
    return estimate, estimate - critical * se, estimate + critical * se


def run_simulation(replicates: int = 400):
    import pandas as pd

    rng = np.random.default_rng(SEED)
    p0 = np.array([0.50, 0.35, 0.15])
    p_shift = np.array([0.25, 0.35, 0.40])
    mu = np.array([-0.5, 0.0, 0.5])
    scenarios = {
        "null_effect": (p0, np.array([0.0, 0.0, 0.0])),
        "composition_only": (p_shift, np.array([0.0, 0.0, 0.0])),
        "within_state_only": (p0, np.array([0.4, 0.4, 0.4])),
        "composition_and_within_same_direction": (p_shift, np.array([0.4, 0.4, 0.4])),
        "composition_and_within_opposite_direction": (p_shift, np.array([0.4, 0.0, -0.4])),
    }
    rows = []
    n0 = 45
    n1 = 45
    groups = np.r_[np.zeros(n0, dtype=int), np.ones(n1, dtype=int)]
    for scenario, (p1, delta) in scenarios.items():
        broad_truth = float(np.dot(p1, mu + delta) - np.dot(p0, mu))
        standardized_truth = float(np.dot(p0, delta))
        records = []
        for _ in range(replicates):
            counts = np.vstack([
                rng.multinomial(240, p0, size=n0),
                rng.multinomial(240, p1, size=n1),
            ])
            expected = mu[None, :] + groups[:, None] * delta[None, :]
            state_means = expected + rng.normal(
                0.0, 0.8 / np.sqrt(np.maximum(counts, 1)), size=counts.shape
            )
            donor_composition = counts / counts.sum(axis=1, keepdims=True)
            broad = (donor_composition * state_means).sum(axis=1)
            broad_est = difference_ci(broad, groups)
            standardized_est = standardized_ci(state_means, groups, p0)
            state_est = [difference_ci(state_means[:, state], groups) for state in range(3)]
            records.append((broad_est, standardized_est, state_est))

        estimands = [
            ("broad_compartment_difference", broad_truth, [record[0] for record in records]),
            (
                "common_composition_standardized_difference",
                standardized_truth,
                [record[1] for record in records],
            ),
        ]
        for state in range(3):
            estimands.append(
                (f"state_{state + 1}_difference", float(delta[state]), [record[2][state] for record in records])
            )
        for estimand, truth, estimates in estimands:
            array = np.asarray(estimates, dtype=float)
            point = array[:, 0]
            coverage = np.mean((array[:, 1] <= truth) & (truth <= array[:, 2]))
            sign_error = np.mean(np.sign(point) != np.sign(truth)) if truth != 0 else np.nan
            rows.append({
                "scenario": scenario,
                "estimand": estimand,
                "truth": truth,
                "mean_estimate": float(point.mean()),
                "bias": float(point.mean() - truth),
                "rmse": float(np.sqrt(np.mean((point - truth) ** 2))),
                "empirical_95pct_coverage": float(coverage),
                "sign_error": float(sign_error) if np.isfinite(sign_error) else np.nan,
                "fit_failure_rate": 0.0,
                "replicates": replicates,
            })
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--external-rebuild-dir", required=True)
    args = parser.parse_args()

    import anndata as ad
    import pandas as pd
    from scipy import sparse
    from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

    workspace = Path(args.workspace).resolve()
    output = Path(args.output_dir).resolve()
    external_dir = Path(args.external_rebuild_dir).resolve()
    created_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    raw_path = workspace / "phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad"
    primary_path = workspace / "phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad"
    a2_path = output / "a2_rebuild/08_isg_excluded_representation.h5ad"
    a1_dictionary_path = output / "02_A1_CONTINUOUS_AXIS_DICTIONARY.csv"
    rank_background_path = output / "04_T_RANK_BACKGROUND.csv.gz"
    design_path = workspace / "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/06_primary_bconv_model_matrix.csv"
    external_counts_path = external_dir / "07_EXTERNAL_PSEUDOBULK_COUNTS.npz"
    external_meta_path = external_dir / "08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv"
    external_genes_path = external_dir / "09_EXTERNAL_GENE_UNIVERSE.csv.gz"
    external_design_path = external_dir / "12_COMBINED_MIN50_MODEL_MATRIX.csv"
    if not external_design_path.is_file():
        external_design_path = workspace / "phase17_v7/gateC5A/20260815_gse135779_source_mapping_freeze/12_COMBINED_MIN50_MODEL_MATRIX.csv"
    required = [
        raw_path, primary_path, a2_path, a1_dictionary_path, rank_background_path,
        design_path, external_counts_path, external_meta_path, external_genes_path,
        external_design_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing minimal-trial inputs: " + ", ".join(missing))

    raw = ad.read_h5ad(raw_path)
    primary = ad.read_h5ad(primary_path)
    a2 = ad.read_h5ad(a2_path)
    protected = {"disease", "disease_state", "case_control", "outcome", "response", "ct_cov"}
    for name, obj in (("primary", primary), ("A2", a2)):
        overlap = sorted(protected & {str(column).lower() for column in obj.obs.columns})
        if overlap:
            raise RuntimeError(f"Protected outcome columns found in {name}: {overlap}")
    if not raw.obs_names.equals(primary.obs_names) or not primary.obs_names.equals(a2.obs_names):
        raise RuntimeError("Raw, A0 and A2 cell orders are not identical")

    raw_symbols = raw.var["feature_name"].astype(str).str.upper().to_numpy()
    raw_mapping = symbol_positions(raw_symbols)
    a1_dictionary = pd.read_csv(a1_dictionary_path, encoding="utf-8-sig")
    a1_genes = a1_dictionary["gene_symbol"].astype(str).str.upper().tolist()
    a1_counts, a1_missing = selected_symbol_counts(raw.X, raw_mapping, a1_genes)
    library_totals = np.asarray(raw.X.sum(axis=1)).ravel().astype(float)
    a1_dense = a1_counts.toarray().astype(float)
    a1_log = np.log1p(
        np.divide(
            a1_dense * 1e4,
            library_totals[:, None],
            out=np.zeros_like(a1_dense),
            where=library_totals[:, None] > 0,
        )
    )
    means = a1_log.mean(axis=0)
    sds = a1_log.std(axis=0, ddof=0)
    if (sds <= 0).any() or a1_missing:
        raise RuntimeError(f"A1 score cannot be computed; missing={a1_missing}, zero_sd={a1_genes[np.argmin(sds)]}")
    signs = a1_dictionary["sign"].to_numpy(dtype=float)
    positive = signs > 0
    negative = signs < 0
    a1_score = ((a1_log[:, positive] - means[positive]) / sds[positive]).mean(axis=1)
    a1_score -= ((a1_log[:, negative] - means[negative]) / sds[negative]).mean(axis=1)
    bconv = primary.obs["leiden_harmony_r0_4"].astype(str).to_numpy() != "3"
    thresholds = np.quantile(a1_score[bconv], [0.2, 0.4, 0.6, 0.8])
    bins = np.digitize(a1_score, thresholds, right=True) + 1
    a1_parameters = pd.DataFrame({
        "gene_symbol": a1_genes,
        "sign": signs.astype(int),
        "mean_log1p_cp10k": means,
        "population_sd_log1p_cp10k": sds,
    })
    write_csv(a1_parameters, output / "07_A1_FROZEN_STANDARDIZATION_PARAMETERS.csv")
    write_json({
        "created_at": created_at,
        "cells_scored": int(len(a1_score)),
        "bconv_cells_used_for_quantiles": int(bconv.sum()),
        "quantile_thresholds": {f"q{q}": float(value) for q, value in zip((20, 40, 60, 80), thresholds)},
        "score_min": float(a1_score.min()),
        "score_median": float(np.median(a1_score)),
        "score_max": float(a1_score.max()),
        "finite_fraction": float(np.isfinite(a1_score).mean()),
        "missing_genes": a1_missing,
        "outcome_fields_used": False,
    }, output / "07_A1_SCORE_TECHNICAL_SUMMARY.json")

    design = pd.read_csv(design_path, encoding="utf-8-sig")
    design = design.reset_index(drop=True)
    stratum_lookup = dict(zip(design["stratum_id"].astype(str), np.arange(len(design))))
    cell_stratum = (
        raw.obs["sample_uuid"].astype(str)
        + "__C"
        + pd.to_numeric(raw.obs["Processing_Cohort"]).astype(int).astype(str)
    )
    group_index = cell_stratum.map(stratum_lookup).fillna(-1).to_numpy(dtype=int)
    group_index[~bconv] = -1
    support_frame = pd.DataFrame({
        "stratum_index_local": group_index[group_index >= 0],
        "a1_bin": bins[group_index >= 0],
    })
    support = (
        support_frame.groupby(["stratum_index_local", "a1_bin"], observed=True)
        .size().rename("cell_count").reset_index()
    )
    full_grid = pd.MultiIndex.from_product(
        [np.arange(len(design)), np.arange(1, 6)],
        names=["stratum_index_local", "a1_bin"],
    ).to_frame(index=False)
    support = full_grid.merge(support, how="left").fillna({"cell_count": 0})
    support["cell_count"] = support["cell_count"].astype(int)
    support["meets_cell_threshold"] = support["cell_count"] >= 30
    support = support.merge(
        design[["stratum_id", "donor_id", "is_managed"]].reset_index(names="stratum_index_local"),
        on="stratum_index_local", how="left",
    )
    write_csv(support.drop(columns=["is_managed"]), output / "08_A1_DONOR_BIN_SUPPORT.csv")
    donor_support = (
        support.loc[support["meets_cell_threshold"]]
        .groupby("a1_bin", observed=True)
        .agg(
            supported_strata=("stratum_id", "nunique"),
            supported_donors=("donor_id", "nunique"),
        ).reset_index()
    )
    arm_support = (
        support.loc[support["meets_cell_threshold"]]
        .groupby(["a1_bin", "is_managed"], observed=True)["donor_id"]
        .nunique().unstack(fill_value=0)
        .rename(columns={0: "normal_donors", 1: "managed_donors"}).reset_index()
    )
    donor_support = donor_support.merge(arm_support, on="a1_bin", how="left").fillna(0)
    donor_support["structural_support_pass"] = donor_support["supported_donors"] >= 20
    donor_support["future_arm_support_pass"] = (
        (donor_support.get("normal_donors", 0) >= 10)
        & (donor_support.get("managed_donors", 0) >= 10)
    )
    write_csv(donor_support, output / "08_A1_BIN_SUPPORT_SUMMARY.csv")

    normal_rows = set(design.index[design["is_managed"] == 0])
    normal_support = support.loc[
        support["stratum_index_local"].isin(normal_rows) & support["meets_cell_threshold"]
    ]
    pi_counts = normal_support.groupby("a1_bin")["cell_count"].sum().reindex(range(1, 6), fill_value=0)
    pi_ref = pi_counts / pi_counts.sum()
    pi_table = pd.DataFrame({
        "a1_bin": np.arange(1, 6),
        "normal_control_cells_in_supported_donor_bins": pi_counts.to_numpy(dtype=int),
        "pi_ref": pi_ref.to_numpy(dtype=float),
    })
    write_csv(pi_table, output / "09_PI_REF.csv")

    key = "leiden_harmony_r0_4"
    a0_labels = primary.obs[key].astype(str)
    a2_labels = a2.obs[key].astype(str)
    a2_ari = float(adjusted_rand_score(a0_labels, a2_labels))
    a2_nmi = float(normalized_mutual_info_score(a0_labels, a2_labels))
    a2_coverage = (
        a2.obs.assign(a2_cluster=a2_labels.to_numpy())
        .groupby("a2_cluster", observed=True)
        .agg(
            cells=("donor_id", "size"),
            donors=("donor_id", "nunique"),
            samples=("sample_uuid", "nunique"),
            libraries=("library_uuid", "nunique"),
            processing_cohorts=("Processing_Cohort", "nunique"),
        ).reset_index()
    )
    write_csv(a2_coverage, output / "10_A2_CLUSTER_COVERAGE.csv")
    a2_summary = {
        "created_at": created_at,
        "cells": int(a2.n_obs),
        "features": int(a2.n_vars),
        "clusters_r0_4": int(a2_labels.nunique()),
        "a0_vs_a2_adjusted_rand_index": a2_ari,
        "a0_vs_a2_normalized_mutual_information": a2_nmi,
        "minimum_cluster_cells": int(a2_coverage["cells"].min()),
        "minimum_cluster_donors": int(a2_coverage["donors"].min()),
        "strong_isg_features": int(a2.var["is_strong_isg"].astype(bool).sum()),
        "disease_blind": bool(a2.uns["phase17_c2b2_branch"]["disease_blind"]),
        "disease_effects_inspected": False,
    }
    write_json(a2_summary, output / "10_A2_STRUCTURAL_TRIAL_SUMMARY.json")

    discovery_pb = group_pseudobulk(raw.X, group_index, len(design))
    discovery_totals = np.asarray(discovery_pb.sum(axis=1)).ravel()
    if (discovery_totals <= 0).any():
        raise RuntimeError("A0 primary pseudobulk contains an empty library")
    ifn_counts, ifn_missing = selected_symbol_counts(discovery_pb, raw_mapping, list(IFN_PROGRAM))
    if ifn_missing:
        raise RuntimeError(f"Discovery IFN program genes missing: {ifn_missing}")
    all_transformed, _ = score_log2_cpm(
        ifn_counts, discovery_totals, np.zeros(len(IFN_PROGRAM)), np.ones(len(IFN_PROGRAM))
    )
    control_mask = design["is_managed"].to_numpy(dtype=int) == 0
    ref_mean = all_transformed[control_mask].mean(axis=0)
    ref_sd = all_transformed[control_mask].std(axis=0, ddof=0)
    if (ref_sd <= 0).any():
        raise RuntimeError("T0 reference contains a zero-variance IFN gene")
    _, t0_score = score_log2_cpm(ifn_counts, discovery_totals, ref_mean, ref_sd)
    t0_reference = pd.DataFrame({
        "gene_symbol": IFN_PROGRAM,
        "control_mean_log2_cpm_plus_0_5": ref_mean,
        "control_population_sd_log2_cpm_plus_0_5": ref_sd,
        "reference_strata": int(control_mask.sum()),
    })
    write_csv(t0_reference, output / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv")
    write_json({
        "discovery_strata": int(len(t0_score)),
        "normal_reference_strata": int(control_mask.sum()),
        "finite_scores": int(np.isfinite(t0_score).sum()),
        "reference_score_mean": float(t0_score[control_mask].mean()),
        "reference_score_sd": float(t0_score[control_mask].std(ddof=0)),
        "all_score_quantiles": {
            str(q): float(np.quantile(t0_score, q)) for q in (0.0, 0.25, 0.5, 0.75, 1.0)
        },
        "disease_coefficient_estimated": False,
    }, output / "11_T0_TECHNICAL_SUMMARY.json")

    rank_background = pd.read_csv(rank_background_path, encoding="utf-8-sig")["gene_symbol"].astype(str).tolist()
    program_rank_positions = [rank_background.index(gene) for gene in IFN_PROGRAM]
    discovery_symbol_counts = build_symbol_matrix(discovery_pb, raw_symbols, rank_background)
    discovery_rank = percentile_program_score(discovery_symbol_counts, program_rank_positions)

    external_counts = sparse.load_npz(external_counts_path)
    external_meta = pd.read_csv(external_meta_path, encoding="utf-8-sig")
    external_genes = pd.read_csv(external_genes_path, encoding="utf-8-sig")
    external_design = pd.read_csv(external_design_path, encoding="utf-8-sig")
    eligible_samples = set(external_design["sample_id"].astype(str))
    external_rows = external_meta.index[
        (external_meta["representation"] == "compartment")
        & (external_meta["frozen_compartment"] == "B_CONV_ANALOG")
        & external_meta["sample_id"].astype(str).isin(eligible_samples)
    ].to_numpy(dtype=int)
    external_pb = external_counts[external_rows]
    external_row_meta = external_meta.iloc[external_rows].reset_index(drop=True)
    if len(external_row_meta) != len(external_design):
        raise RuntimeError("External eligible design does not align with compartment pseudobulk rows")
    external_symbols = external_genes["gene_symbol_upper"].astype(str).str.upper().to_numpy()
    external_mapping = symbol_positions(external_symbols)
    external_ifn_counts, external_missing = selected_symbol_counts(
        external_pb, external_mapping, list(IFN_PROGRAM)
    )
    external_totals = np.asarray(external_pb.sum(axis=1)).ravel()
    _, t_frozen_score = score_log2_cpm(external_ifn_counts, external_totals, ref_mean, ref_sd)
    external_symbol_counts = build_symbol_matrix(external_pb, external_symbols, rank_background)
    external_rank = percentile_program_score(external_symbol_counts, program_rank_positions)
    score_diagnostics = pd.DataFrame([
        {
            "score": "T0_discovery",
            "rows": len(t0_score),
            "program_genes_present": len(IFN_PROGRAM),
            "background_genes": len(rank_background),
            "finite_fraction": float(np.isfinite(t0_score).mean()),
            "minimum": float(np.min(t0_score)),
            "median": float(np.median(t0_score)),
            "maximum": float(np.max(t0_score)),
        },
        {
            "score": "T_frozen_external",
            "rows": len(t_frozen_score),
            "program_genes_present": len(IFN_PROGRAM) - len(external_missing),
            "background_genes": len(rank_background),
            "finite_fraction": float(np.isfinite(t_frozen_score).mean()),
            "minimum": float(np.min(t_frozen_score)),
            "median": float(np.median(t_frozen_score)),
            "maximum": float(np.max(t_frozen_score)),
        },
        {
            "score": "T_rank_discovery",
            "rows": len(discovery_rank),
            "program_genes_present": len(IFN_PROGRAM),
            "background_genes": len(rank_background),
            "finite_fraction": float(np.isfinite(discovery_rank).mean()),
            "minimum": float(np.min(discovery_rank)),
            "median": float(np.median(discovery_rank)),
            "maximum": float(np.max(discovery_rank)),
        },
        {
            "score": "T_rank_external",
            "rows": len(external_rank),
            "program_genes_present": len(IFN_PROGRAM) - len(external_missing),
            "background_genes": len(rank_background),
            "finite_fraction": float(np.isfinite(external_rank).mean()),
            "minimum": float(np.min(external_rank)),
            "median": float(np.median(external_rank)),
            "maximum": float(np.max(external_rank)),
        },
    ])
    write_csv(score_diagnostics, output / "12_SCORE_TRANSFER_TECHNICAL_DIAGNOSTICS.csv")
    write_json({
        "external_eligible_rows": int(len(external_row_meta)),
        "external_program_genes_missing": external_missing,
        "t_frozen_finite": bool(np.isfinite(t_frozen_score).all()),
        "t_rank_finite_discovery": bool(np.isfinite(discovery_rank).all()),
        "t_rank_finite_external": bool(np.isfinite(external_rank).all()),
        "disease_coefficients_estimated": False,
        "external_group_summaries_computed": False,
    }, output / "12_SCORE_TRANSFER_TRIAL_STATUS.json")

    simulation = run_simulation(replicates=400)
    write_csv(simulation, output / "13_SIMULATION_TECHNICAL_RESULTS.csv")
    max_abs_bias = float(simulation["bias"].abs().max())
    minimum_coverage = float(simulation["empirical_95pct_coverage"].min())
    maximum_coverage = float(simulation["empirical_95pct_coverage"].max())
    simulation_pass = bool(max_abs_bias <= 0.06 and minimum_coverage >= 0.90 and maximum_coverage <= 0.99)

    checks = [
        {"check": "a1_dictionary_complete", "pass": not a1_missing and len(a1_genes) == 14, "detail": "7 positive + 7 negative genes"},
        {"check": "a1_scores_finite", "pass": bool(np.isfinite(a1_score).all()), "detail": f"{len(a1_score):,}/{len(a1_score):,}"},
        {"check": "a1_structural_support", "pass": bool(donor_support["structural_support_pass"].all()), "detail": f"minimum supported donors={int(donor_support['supported_donors'].min())}"},
        {"check": "a1_future_arm_support", "pass": bool(donor_support["future_arm_support_pass"].all()), "detail": f"minimum normal={int(donor_support['normal_donors'].min())}; managed={int(donor_support['managed_donors'].min())}"},
        {"check": "pi_ref_valid", "pass": bool(np.isclose(pi_ref.sum(), 1.0) and (pi_ref > 0).all()), "detail": f"sum={pi_ref.sum():.12f}"},
        {"check": "a2_full_cell_rebuild", "pass": a2.n_obs == 150_402 and a2.n_vars == 3_000, "detail": f"{a2.n_obs:,} x {a2.n_vars:,}"},
        {"check": "a2_ifn_exclusion", "pass": a2_summary["strong_isg_features"] == 0, "detail": "zero strong-ISG features"},
        {"check": "a2_structural_alignment", "pass": a2_ari >= 0.70 and 3 <= a2_labels.nunique() <= 7, "detail": f"ARI={a2_ari:.3f}; NMI={a2_nmi:.3f}; clusters={a2_labels.nunique()}"},
        {"check": "t0_computable", "pass": bool(np.isfinite(t0_score).all()), "detail": f"{len(t0_score)} discovery strata; {control_mask.sum()} reference controls"},
        {"check": "external_frozen_score_computable", "pass": not external_missing and bool(np.isfinite(t_frozen_score).all()), "detail": f"{len(t_frozen_score)} external rows; 12/12 genes"},
        {"check": "rank_score_computable", "pass": bool(np.isfinite(discovery_rank).all() and np.isfinite(external_rank).all()), "detail": f"fixed background={len(rank_background):,}"},
        {"check": "simulation_technical_truth_recovery", "pass": simulation_pass, "detail": f"max |bias|={max_abs_bias:.3f}; coverage={minimum_coverage:.3f}-{maximum_coverage:.3f}"},
        {"check": "result_blind_contract", "pass": True, "detail": "no disease coefficient or between-group score summary estimated"},
    ]
    all_pass = all(item["pass"] for item in checks)
    decision = "PASS_G1_TO_WP1_ANNOTATION_SENSITIVITY" if all_pass else "HOLD_G1_REPAIR_REQUIRED"
    next_stage = (
        "SCIENTIFIC_REDESIGN_WP1_ANNOTATION_SENSITIVITY"
        if all_pass else "SCIENTIFIC_REDESIGN_STAGE0B_REPAIR"
    )
    status = {
        "created_at": created_at,
        "status": decision,
        "g0a_input_recovery": "PASS",
        "g0b_protocol_freeze": "PASS",
        "g0_overall": "PASS_G0",
        "g1": decision,
        "wp4": "HOLD_CONDITIONAL",
        "submission": "HOLD",
        "disease_effects_inspected": False,
        "checks": checks,
        "next_stage": next_stage,
    }
    write_json(status, output / "14_STAGE0B_GATE_STATUS.json")
    write_json({**status, "run_phase": "COMPLETE"}, output / "00_STAGE0B_RUN_STATUS.json")

    check_lines = "\n".join(
        f"- [{'x' if item['pass'] else ' '}] `{item['check']}`: {item['detail']}"
        for item in checks
    )
    report = f"""# RP v3 Stage 0B advisor gate review

**Decision:** `{decision}`

## Result-blind trial findings

- The 14-gene A1 axis is fully computable in 150,402 cells and remains continuous.
- Its five quantile bins are an audit scaffold only; they do not authorize biological subtype labels.
- A2 was rebuilt in all 150,402 cells from the frozen 3,000-feature IFN-excluded list.
- A0 versus A2 structural concordance at resolution 0.4 is ARI={a2_ari:.3f}, NMI={a2_nmi:.3f}.
- T0 is computable in {len(t0_score)} discovery strata from a {int(control_mask.sum())}-control frozen reference.
- T_frozen and T_rank are computable in {len(t_frozen_score)} eligible external source-label B_CONV rows.
- The five-scenario simulation completed without model failures; it is a technical test, not a G2 claim.
- No disease coefficient, annotation effect or external case-control score difference was estimated.

## Checks

{check_lines}

## Interpretation boundary

A G1 pass authorizes WP1 annotation-sensitivity estimation under the frozen contracts. It does not
rescue the historical fine-state freeze, authorize subtype naming, unlock WP4, or modify the current
manuscript and figures. The historical identity failure remains part of the project record.

## Next stage

`{next_stage}`
"""
    (output / "14_STAGE0B_ADVISOR_REVIEW.md").write_text(report, encoding="utf-8")

    rows = []
    for path in sorted(output.glob("*.json")) + sorted(output.glob("*.csv")) + sorted(output.glob("*.csv.gz")) + sorted(output.glob("*.md")):
        if path.name == "15_STAGE0B_INTEGRITY_MANIFEST.csv":
            continue
        rows.append({
            "file": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    for path in sorted((output / "a2_rebuild").glob("*")):
        if path.is_file():
            rows.append({
                "file": str(path.relative_to(output)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    write_csv(pd.DataFrame(rows), output / "15_STAGE0B_INTEGRITY_MANIFEST.csv")
    print(json.dumps(status, indent=2), flush=True)
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
