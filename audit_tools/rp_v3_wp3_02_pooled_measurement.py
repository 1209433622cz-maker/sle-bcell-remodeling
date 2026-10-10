#!/usr/bin/env python3
"""Run the bounded RP v3 WP3 pooled measurement diagnostics.

This stage generates real expression-derived scores for all eligible external
B_CONV pseudobulks, but it never loads phenotype fields, fits disease effects,
computes P values or produces subgroup summaries. The frozen Stage 0B scoring
module remains the source operator and is checked against an independent local
implementation before any output is written.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import rankdata


PROGRAM = (
    "IFI44L", "IFI6", "IFIT1", "IFIT2", "IFIT3", "IRF7",
    "ISG15", "LY6E", "MX1", "MX2", "OAS1", "OAS2",
)
QUANTILES = (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0)
QUANTILE_NAMES = ("min", "q05", "q25", "median", "q75", "q95", "max")
BLIND_COLUMNS = ("blind_key", "pseudobulk_row", "cell_count", "library_size_umi")


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(frame, path: Path) -> None:
    pd.DataFrame(frame).to_csv(
        path,
        index=False,
        lineterminator="\n",
        float_format="%.17g",
        encoding="utf-8",
    )


def write_json(payload: dict, path: Path) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
    path.write_bytes((text + "\n").encode("utf-8"))


def load_stage0b_operator(path: Path):
    spec = importlib.util.spec_from_file_location("rp_v3_stage0b_frozen", path)
    require(spec is not None and spec.loader is not None, "cannot load Stage 0B operator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_counts(matrix: sparse.csr_matrix) -> None:
    require(np.issubdtype(matrix.dtype, np.integer), "counts must be integer typed")
    require(np.isfinite(matrix.data).all(), "counts must be finite")
    require((matrix.data >= 0).all(), "counts must be nonnegative")
    require(matrix.has_canonical_format, "sparse counts must be canonical")


def symbol_positions(symbols: list[str]) -> dict[str, list[int]]:
    mapping: dict[str, list[int]] = {}
    for index, symbol in enumerate(symbols):
        key = str(symbol).upper()
        if key and key not in {"NAN", "NONE"}:
            mapping.setdefault(key, []).append(index)
    return mapping


def aggregate_symbols(
    matrix: sparse.csr_matrix,
    symbols: list[str],
    background: list[str],
) -> sparse.csr_matrix:
    validate_counts(matrix)
    require(len(symbols) == matrix.shape[1], "feature length mismatch")
    require(len(background) > 0, "empty rank background")
    require(len(background) == len(set(background)), "duplicate rank background")
    mapping = symbol_positions(symbols)
    require(set(background).issubset(mapping), "missing measured rank-background symbol")
    source_columns: list[int] = []
    target_columns: list[int] = []
    for target, symbol in enumerate(background):
        source_columns.extend(mapping[symbol])
        target_columns.extend([target] * len(mapping[symbol]))
    mapper = sparse.csr_matrix(
        (
            np.ones(len(source_columns), dtype=np.int64),
            (source_columns, target_columns),
        ),
        shape=(len(symbols), len(background)),
    )
    return (matrix @ mapper).tocsr()


def frozen_scores(
    program_counts: np.ndarray,
    library_totals: np.ndarray,
    reference_mean: np.ndarray,
    reference_sd: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    counts = np.asarray(program_counts, dtype=float)
    totals = np.asarray(library_totals, dtype=float)
    means = np.asarray(reference_mean, dtype=float)
    sds = np.asarray(reference_sd, dtype=float)
    require(counts.ndim == 2, "program count shape")
    require(counts.shape[1] == len(means) == len(sds), "reference shape mismatch")
    require(totals.shape == (counts.shape[0],), "library shape mismatch")
    require(np.isfinite(totals).all() and (totals > 0).all(), "nonpositive library")
    require(np.isfinite(counts).all() and (counts >= 0).all(), "invalid program counts")
    require(np.all(counts == np.floor(counts)), "program counts must be integer valued")
    require(np.all(counts.sum(axis=1) <= totals), "program exceeds full library")
    require(np.isfinite(means).all(), "nonfinite reference mean")
    require(np.isfinite(sds).all() and (sds > 0).all(), "invalid reference SD")
    transformed = np.log2(counts * 1e6 / totals[:, None] + 0.5)
    z_scores = (transformed - means) / sds
    return transformed, z_scores, z_scores.mean(axis=1)


def rank_scores(
    symbol_counts: np.ndarray,
    program_positions: list[int],
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.asarray(symbol_counts)
    require(counts.ndim == 2 and counts.shape[1] > 0, "empty rank counts")
    require(np.isfinite(counts).all() and (counts >= 0).all(), "invalid rank counts")
    require(len(set(program_positions)) == len(program_positions) > 0, "rank positions")
    ranks = rankdata(counts, method="average", axis=1) / counts.shape[1]
    scores = np.asarray(
        [float(np.mean(ranks[row, program_positions])) for row in range(counts.shape[0])]
    )
    return ranks[:, program_positions], scores


def rank_concordance(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    require(left.ndim == right.ndim == 1 and len(left) == len(right) > 1, "rank shape")
    require(np.isfinite(left).all() and np.isfinite(right).all(), "nonfinite rank input")
    x = rankdata(left, method="average")
    y = rankdata(right, method="average")
    x = x - x.mean()
    y = y - y.mean()
    denominator = np.sqrt(np.dot(x, x) * np.dot(y, y))
    require(denominator > 0, "undefined constant-score concordance")
    return float(np.dot(x, y) / denominator)


def pooled_quantiles(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    require(np.isfinite(values).all(), "nonfinite pooled values")
    observed = np.quantile(values, QUANTILES, method="linear")
    return dict(zip(QUANTILE_NAMES, map(float, observed)))


def validate_blind_handoff(frame: pd.DataFrame) -> None:
    require(tuple(frame.columns) == BLIND_COLUMNS, "unexpected blinded handoff columns")
    require(frame.blind_key.is_unique, "duplicate blind key")
    require(frame.pseudobulk_row.is_unique, "duplicate pseudobulk row")
    require(frame.blind_key.str.fullmatch(r"D[0-9]{3}").all(), "invalid blind key")
    require(frame.cell_count.ge(50).all(), "support threshold failure")


def canonical_paths(workspace: Path) -> dict[str, Path]:
    stage0b = workspace / "phase17_v7/rp_v3_redesign/20261009_stage0b"
    external = stage0b / "external_source_rebuild"
    prefit = workspace / "phase17_v7/rp_v3_redesign/20261010_wp3_effect_free_prefit"
    return {
        "counts": external / "07_EXTERNAL_PSEUDOBULK_COUNTS.npz",
        "metadata": external / "08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv",
        "genes": external / "09_EXTERNAL_GENE_UNIVERSE.csv.gz",
        "source": external / "03_SAMPLE_SOURCE_AUDIT.csv",
        "background": stage0b / "04_T_RANK_BACKGROUND.csv.gz",
        "reference": stage0b / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv",
        "contract": stage0b / "04_SCORE_CONTRACTS.json",
        "operator": workspace / "audit_tools/rp_v3_stage0b_02_minimal_trial.py",
        "protocol": prefit / "11_WP3_EFFECT_FREE_MEASUREMENT_SCOPE_PROTOCOL.md",
        "parent_gate": prefit / "10_WP3_PREFIT_GATE_STATUS.json",
    }


def run(workspace: Path, output: Path) -> None:
    workspace = workspace.resolve()
    output = output.resolve()
    require(not output.exists(), "output exists; use a new directory")
    paths = canonical_paths(workspace)
    for path in paths.values():
        require(path.is_file(), f"missing canonical input: {path}")
    initial_hashes = {name: sha256(path) for name, path in paths.items()}

    parent_gate = json.loads(paths["parent_gate"].read_text(encoding="utf-8"))
    require(
        parent_gate["status"] == "PASS_WP3_AVAILABLE_OBJECTS_PREFIT__HOLD_OUTCOME_EXECUTION",
        "unexpected parent gate",
    )
    require(parent_gate["WP3_OUTCOME_EXECUTION_AUTHORIZED"] is False, "outcome gate drift")

    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        require(condition, name)
        checks.append({"check": name, "pass": True, "detail": detail})

    counts = sparse.load_npz(paths["counts"]).tocsr()
    metadata = pd.read_csv(
        paths["metadata"],
        usecols=(
            "pseudobulk_row", "representation", "sample_id", "frozen_compartment",
            "source_label", "cell_count", "library_size_umi", "detected_genes",
        ),
        keep_default_na=False,
    )
    genes = pd.read_csv(paths["genes"], usecols=["gene_symbol_upper"], keep_default_na=False)
    source = pd.read_csv(
        paths["source"],
        usecols=["sample_id", "bconv_cells", "bconv_library_size_umi"],
        keep_default_na=False,
    )
    background = pd.read_csv(paths["background"], keep_default_na=False).gene_symbol.tolist()
    reference = pd.read_csv(paths["reference"])
    contract = json.loads(paths["contract"].read_text(encoding="utf-8-sig"))
    operator = load_stage0b_operator(paths["operator"])

    validate_counts(counts)
    check("raw_count_shape", counts.shape == (672, 32738), "672 x 32,738")
    check("metadata_row_index", np.array_equal(metadata.pseudobulk_row, np.arange(672)))
    check(
        "full_library_denominator_all_rows",
        np.array_equal(np.asarray(counts.sum(axis=1)).ravel(), metadata.library_size_umi),
    )
    check("detected_gene_count_all_rows", np.array_equal(counts.getnnz(axis=1), metadata.detected_genes))

    broad = metadata[
        metadata.representation.eq("compartment")
        & metadata.frozen_compartment.eq("B_CONV_ANALOG")
    ].sort_values("sample_id").copy()
    check("broad_sample_count", len(broad) == 56 and broad.sample_id.nunique() == 56)
    require(not source.sample_id.duplicated().any(), "duplicate source support sample")
    linked = broad.merge(source, on="sample_id", how="left", validate="one_to_one", indicator=True)
    check("neutral_source_link_complete", linked._merge.eq("both").all())
    check(
        "neutral_source_support_exact",
        linked.cell_count.eq(linked.bconv_cells).all()
        and linked.library_size_umi.eq(linked.bconv_library_size_umi).all(),
    )
    for row in broad.itertuples():
        bins = metadata[
            metadata.sample_id.eq(row.sample_id)
            & metadata.source_label.isin([f"B-caSC{index}" for index in range(8)])
        ]
        require(len(bins) == 8 and bins.source_label.nunique() == 8, "label partition cardinality")
        observed = np.asarray(counts[bins.pseudobulk_row].sum(axis=0)).ravel()
        expected = counts[row.pseudobulk_row].toarray().ravel()
        require(np.array_equal(observed, expected), "label partition count closure")
        require(int(bins.cell_count.sum()) == int(row.cell_count), "label partition cell closure")
    check("all_56_label_partitions_close", True)

    eligible = broad[broad.cell_count.ge(50)].reset_index(drop=True)
    check("frozen_min50_eligible", len(eligible) == 54)
    eligible["blind_key"] = [f"D{index:03}" for index in range(1, 55)]
    handoff = eligible[list(BLIND_COLUMNS)].copy()
    validate_blind_handoff(handoff)
    check("neutral_handoff_schema", True, "no sample, donor, cohort, age or disease field")

    matrix = counts[handoff.pseudobulk_row.to_numpy()]
    library = handoff.library_size_umi.to_numpy(dtype=float)
    symbols = genes.gene_symbol_upper.astype(str).str.upper().tolist()
    mapping = symbol_positions(symbols)
    check("program_contract_order", tuple(contract["program_members"]) == PROGRAM)
    check("reference_program_order", tuple(reference.gene_symbol) == PROGRAM)
    check("reference_population_43", reference.reference_strata.eq(43).all())
    check("background_unique_18873", len(background) == len(set(background)) == 18873)
    check("program_symbols_measured", set(PROGRAM).issubset(mapping))
    check("background_symbols_measured", set(background).issubset(mapping))

    background_counts = aggregate_symbols(matrix, symbols, background)
    positions = [background.index(gene) for gene in PROGRAM]
    program_counts = background_counts[:, positions].toarray()
    means = reference.control_mean_log2_cpm_plus_0_5.to_numpy(dtype=float)
    sds = reference.control_population_sd_log2_cpm_plus_0_5.to_numpy(dtype=float)

    transformed, z_scores, frozen = frozen_scores(program_counts, library, means, sds)
    gene_ranks, ranked = rank_scores(background_counts.toarray(), positions)
    source_program_counts, missing = operator.selected_symbol_counts(
        matrix, operator.symbol_positions(symbols), list(PROGRAM)
    )
    source_background = operator.build_symbol_matrix(matrix, symbols, background)
    source_transformed, source_frozen = operator.score_log2_cpm(
        source_program_counts, library, means, sds
    )
    source_ranked = operator.percentile_program_score(source_background, positions)
    check("source_program_counts_exact", not missing and np.array_equal(source_program_counts.toarray(), program_counts))
    check("source_background_counts_exact", np.array_equal(source_background.toarray(), background_counts.toarray()))
    check("source_frozen_operator_exact", np.array_equal(source_transformed, transformed) and np.array_equal(source_frozen, frozen))
    check("source_rank_operator_exact", np.array_equal(source_ranked, ranked))
    check("all_measurements_finite", all(np.isfinite(item).all() for item in (transformed, z_scores, frozen, gene_ranks, ranked)))
    check("rank_percentiles_bounded", (gene_ranks >= 1 / len(background)).all() and (gene_ranks <= 1).all())

    leave_one_out = np.column_stack(
        [np.delete(z_scores, index, axis=1).mean(axis=1) for index in range(12)]
    )
    check(
        "leave_one_out_formula",
        np.allclose(leave_one_out, (12 * frozen[:, None] - z_scores) / 11, atol=1e-14, rtol=1e-14),
    )
    contributions = z_scores / 12
    check("contribution_reconstruction", np.allclose(contributions.sum(axis=1), frozen, atol=1e-14, rtol=1e-14))

    frozen_rank = rankdata(frozen, method="average")
    ranked_rank = rankdata(ranked, method="average")
    concordance = {
        "scope": "pooled_54_only",
        "n": 54,
        "T_frozen_T_rank_spearman": rank_concordance(frozen, ranked),
        "between_transform_max_abs_rank_displacement": float(np.max(np.abs(frozen_rank - ranked_rank))),
        "between_transform_mean_abs_rank_displacement": float(np.mean(np.abs(frozen_rank - ranked_rank))),
        "p_values_computed": False,
        "confidence_intervals_computed": False,
        "disease_or_age_stratification_performed": False,
        "primary_transform": "T_frozen",
        "sensitivity_transform": "T_rank",
        "transform_selection_performed": False,
    }

    loo_rows = []
    gene_rows = []
    source_rows = []
    mean_absolute_contribution = np.mean(np.abs(contributions), axis=0)
    for gene_index, gene in enumerate(PROGRAM):
        loo_rank = rankdata(leave_one_out[:, gene_index], method="average")
        displacement = np.abs(loo_rank - frozen_rank)
        loo_rows.append(
            {
                "omitted_gene": gene,
                "n": 54,
                "retained_genes": 11,
                "spearman_vs_full": rank_concordance(frozen, leave_one_out[:, gene_index]),
                "max_abs_rank_displacement": float(displacement.max()),
                "mean_abs_rank_displacement": float(displacement.mean()),
                "donors_with_changed_rank": int((displacement > 0).sum()),
                "max_abs_score_change": float(np.max(np.abs(leave_one_out[:, gene_index] - frozen))),
            }
        )
        gene_z = z_scores[:, gene_index]
        gene_rows.append(
            {
                "gene": gene,
                "measured_feature_count": len(mapping[gene]),
                "detected_pseudobulks": int((program_counts[:, gene_index] > 0).sum()),
                "pseudobulks": 54,
                "pseudobulk_detection_fraction": float((program_counts[:, gene_index] > 0).mean()),
                "reference_population_sd": float(sds[gene_index]),
                "z_mean": float(gene_z.mean()),
                "z_population_sd": float(gene_z.std(ddof=0)),
                **{f"z_{key}": value for key, value in pooled_quantiles(gene_z).items()},
                "contribution_mean": float(contributions[:, gene_index].mean()),
                "contribution_mean_abs": float(mean_absolute_contribution[gene_index]),
                "share_of_pooled_mean_abs_contributions": float(
                    mean_absolute_contribution[gene_index] / mean_absolute_contribution.sum()
                ),
            }
        )
        for row_index in range(54):
            source_rows.append(
                {
                    "blind_key": handoff.blind_key.iloc[row_index],
                    "gene": gene,
                    "raw_count": int(program_counts[row_index, gene_index]),
                    "log2_full_CPM_plus_0_5": float(transformed[row_index, gene_index]),
                    "frozen_z": float(z_scores[row_index, gene_index]),
                    "additive_contribution_z_div12": float(contributions[row_index, gene_index]),
                    "rank_percentile": float(gene_ranks[row_index, gene_index]),
                    "T_frozen_without_gene": float(leave_one_out[row_index, gene_index]),
                }
            )

    symbol_counts = pd.Series(symbols).value_counts()
    duplicate_rows = [
        {
            "symbol": symbol,
            "measured_feature_count": int(symbol_counts[symbol]),
            "in_fixed_rank_background": symbol in set(background),
            "in_IFN12": symbol in PROGRAM,
        }
        for symbol in sorted(symbol_counts.index)
        if symbol not in {"", "NAN", "NONE"} and symbol_counts[symbol] > 1
    ]
    background_fraction = np.asarray(background_counts.sum(axis=1)).ravel() / library
    denominator_receipt = {
        "measured_features": len(symbols),
        "unique_valid_measured_symbols": len(set(symbols) - {"", "NAN", "NONE"}),
        "duplicate_symbols_count": len(duplicate_rows),
        "rank_background": len(background),
        "rank_background_captured_library_fraction": pooled_quantiles(background_fraction),
        "detection_unit": "donor pseudobulk aggregated UMI > 0; not individual cells",
        "normalization_denominator": "all 32738 measured features, including features outside rank background",
    }

    check("canonical_inputs_unchanged_after_compute", all(sha256(paths[name]) == digest for name, digest in initial_hashes.items()))
    status = {
        "status": "PASS_WP3_POOLED_MEASUREMENT_DIAGNOSTICS__HOLD_OUTCOME_EXECUTION",
        "checks_passed": len(checks),
        "n_eligible": 54,
        "real_scores_generated": True,
        "disease_labels_loaded": False,
        "disease_or_age_stratification_performed": False,
        "new_disease_effects_fitted": False,
        "confidence_intervals_or_p_values_generated": False,
        "cross_platform_equivalence_validated": False,
        "clinical_calibration_validated": False,
        "T_frozen_remains_primary": True,
        "T_rank_remains_sensitivity": True,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "WP3_OUTCOME_EXECUTION_AUTHORIZED": False,
        "WP4": "HOLD_CONDITIONAL",
        "manuscript_replacement": "HOLD",
        "submission": "HOLD",
        "next_stage": "RP_V3_AUTHOR_SCOPE_CLOSURE_DECISION",
        "stage0b_operator_sha256": initial_hashes["operator"],
    }

    output.mkdir(parents=True)
    receipts = [
        {
            "path": paths[name].relative_to(workspace).as_posix(),
            "bytes": paths[name].stat().st_size,
            "sha256": initial_hashes[name],
        }
        for name in sorted(paths)
    ]
    write_csv(receipts, output / "01_WP3_MEASUREMENT_INPUT_RECEIPTS.csv")
    write_csv(checks, output / "02_WP3_MEASUREMENT_CHECKS.csv")
    write_csv(handoff, output / "03_BLINDED_ELIGIBLE_OBJECTS.csv")
    write_csv(
        [
            {
                "transform": name,
                "n": 54,
                "mean": float(values.mean()),
                "population_sd": float(values.std(ddof=0)),
                **pooled_quantiles(values),
            }
            for name, values in (("T_frozen", frozen), ("T_rank", ranked))
        ],
        output / "04_POOLED_SCORE_DISTRIBUTIONS.csv",
    )
    write_json(concordance, output / "05_POOLED_RANK_CONCORDANCE.json")
    write_csv(loo_rows, output / "06_LEAVE_ONE_GENE_OUT.csv")
    write_csv(gene_rows, output / "07_GENE_DETECTION_CONTRIBUTIONS.csv")
    write_json(denominator_receipt, output / "08_SYMBOL_DENOMINATOR_RECEIPT.json")
    write_csv(duplicate_rows, output / "09_DUPLICATE_SYMBOL_AUDIT.csv")
    write_csv(
        [
            {
                "blind_key": handoff.blind_key.iloc[index],
                "T_frozen": frozen[index],
                "T_rank": ranked[index],
                "T_frozen_pooled_rank": frozen_rank[index],
                "T_rank_pooled_rank": ranked_rank[index],
            }
            for index in range(54)
        ],
        output / "10_POOLED_SCORE_SOURCE_DATA.csv",
    )
    write_csv(source_rows, output / "11_GENE_AND_LOO_SOURCE_DATA.csv")
    write_json(status, output / "12_WP3_MEASUREMENT_GATE_STATUS.json")
    print(json.dumps(status, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    run(arguments.workspace, arguments.output)


if __name__ == "__main__":
    main()
