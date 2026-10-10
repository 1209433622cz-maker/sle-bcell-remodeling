#!/usr/bin/env python3
"""Independently recompute the canonical WP3 pooled measurement outputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from pathlib import Path

from scipy import sparse


PROGRAM = (
    "IFI44L", "IFI6", "IFIT1", "IFIT2", "IFIT3", "IRF7",
    "ISG15", "LY6E", "MX1", "MX2", "OAS1", "OAS2",
)
QUANTILES = (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0)
QUANTILE_NAMES = ("min", "q05", "q25", "median", "q75", "q95", "max")


def read_csv(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    output = [0.0] * len(values)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        tied_rank = ((start + 1) + stop) / 2
        for index in order[start:stop]:
            output[index] = tied_rank
        start = stop
    return output


def mean(values: list[float]) -> float:
    return math.fsum(values) / len(values)


def rank_correlation(left: list[float], right: list[float]) -> float:
    x = ranks(left)
    y = ranks(right)
    x_mean = mean(x)
    y_mean = mean(y)
    numerator = math.fsum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    denominator = math.sqrt(
        math.fsum((a - x_mean) ** 2 for a in x)
        * math.fsum((b - y_mean) ** 2 for b in y)
    )
    if denominator == 0:
        raise ValueError("undefined constant-score correlation")
    return numerator / denominator


def quantiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    output = {}
    for name, quantile in zip(QUANTILE_NAMES, QUANTILES):
        position = (len(ordered) - 1) * quantile
        lower = math.floor(position)
        upper = math.ceil(position)
        output[name] = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return output


def run(workspace: Path, results: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    stage0b = workspace / "phase17_v7/rp_v3_redesign/20261009_stage0b"
    external = stage0b / "external_source_rebuild"
    matrix = sparse.load_npz(external / "07_EXTERNAL_PSEUDOBULK_COUNTS.npz").tocsr()
    metadata = read_csv(external / "08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv")
    eligible = sorted(
        [
            row for row in metadata
            if row["representation"] == "compartment"
            and row["frozen_compartment"] == "B_CONV_ANALOG"
            and int(row["cell_count"]) >= 50
        ],
        key=lambda row: row["sample_id"],
    )
    if len(eligible) != 54:
        raise ValueError("unexpected eligible count")
    symbols = [row["gene_symbol_upper"].upper() for row in read_csv(external / "09_EXTERNAL_GENE_UNIVERSE.csv.gz")]
    background = [row["gene_symbol"] for row in read_csv(stage0b / "04_T_RANK_BACKGROUND.csv.gz")]
    reference = read_csv(stage0b / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv")
    if [row["gene_symbol"] for row in reference] != list(PROGRAM):
        raise ValueError("reference order")
    reference_mean = [float(row["control_mean_log2_cpm_plus_0_5"]) for row in reference]
    reference_sd = [float(row["control_population_sd_log2_cpm_plus_0_5"]) for row in reference]
    symbol_map: dict[str, list[int]] = {}
    for index, symbol in enumerate(symbols):
        if symbol and symbol not in {"NAN", "NONE"}:
            symbol_map.setdefault(symbol, []).append(index)
    if not set(background).issubset(symbol_map):
        raise ValueError("missing background")
    program_positions = [background.index(gene) for gene in PROGRAM]

    program_counts: list[list[int]] = []
    transformed: list[list[float]] = []
    z_scores: list[list[float]] = []
    gene_ranks: list[list[float]] = []
    frozen: list[float] = []
    ranked: list[float] = []
    leave_one_out: list[list[float]] = []
    for row in eligible:
        dense = matrix[int(row["pseudobulk_row"])].toarray().ravel().tolist()
        library = sum(dense)
        if library != int(row["library_size_umi"]) or library <= 0:
            raise ValueError("library mismatch")
        counts = [sum(dense[index] for index in symbol_map[gene]) for gene in PROGRAM]
        log_values = [math.log2(count * 1e6 / library + 0.5) for count in counts]
        z_values = [
            (value - ref_mean) / ref_sd
            for value, ref_mean, ref_sd in zip(log_values, reference_mean, reference_sd)
        ]
        background_counts = [sum(dense[index] for index in symbol_map[symbol]) for symbol in background]
        all_ranks = ranks(background_counts)
        program_rank = [all_ranks[index] / len(background) for index in program_positions]
        program_counts.append(counts)
        transformed.append(log_values)
        z_scores.append(z_values)
        gene_ranks.append(program_rank)
        frozen.append(mean(z_values))
        ranked.append(mean(program_rank))
        leave_one_out.append([mean(z_values[:index] + z_values[index + 1:]) for index in range(12)])

    checks = 0
    max_error = 0.0

    def compare(observed, recomputed, tolerance: float = 1e-11) -> None:
        nonlocal checks, max_error
        error = abs(float(observed) - float(recomputed))
        if not math.isfinite(error) or error > tolerance:
            raise AssertionError((observed, recomputed, error, tolerance))
        checks += 1
        max_error = max(max_error, error)

    score_rows = read_csv(results / "10_POOLED_SCORE_SOURCE_DATA.csv")
    frozen_ranks = ranks(frozen)
    ranked_ranks = ranks(ranked)
    for index, row in enumerate(score_rows):
        if row["blind_key"] != f"D{index + 1:03}":
            raise AssertionError("blind key drift")
        compare(row["T_frozen"], frozen[index])
        compare(row["T_rank"], ranked[index])
        compare(row["T_frozen_pooled_rank"], frozen_ranks[index], 0)
        compare(row["T_rank_pooled_rank"], ranked_ranks[index], 0)

    for row in read_csv(results / "11_GENE_AND_LOO_SOURCE_DATA.csv"):
        sample_index = int(row["blind_key"][1:]) - 1
        gene_index = PROGRAM.index(row["gene"])
        expected = {
            "raw_count": program_counts[sample_index][gene_index],
            "log2_full_CPM_plus_0_5": transformed[sample_index][gene_index],
            "frozen_z": z_scores[sample_index][gene_index],
            "additive_contribution_z_div12": z_scores[sample_index][gene_index] / 12,
            "rank_percentile": gene_ranks[sample_index][gene_index],
            "T_frozen_without_gene": leave_one_out[sample_index][gene_index],
        }
        for field, value in expected.items():
            compare(row[field], value)

    for row in read_csv(results / "04_POOLED_SCORE_DISTRIBUTIONS.csv"):
        values = frozen if row["transform"] == "T_frozen" else ranked
        for name, value in quantiles(values).items():
            compare(row[name], value)
        compare(row["mean"], mean(values))
        population_sd = math.sqrt(mean([(value - mean(values)) ** 2 for value in values]))
        compare(row["population_sd"], population_sd)

    pooled = json.loads((results / "05_POOLED_RANK_CONCORDANCE.json").read_text(encoding="utf-8"))
    compare(pooled["T_frozen_T_rank_spearman"], rank_correlation(frozen, ranked))
    displacement = [abs(left - right) for left, right in zip(frozen_ranks, ranked_ranks)]
    compare(pooled["between_transform_max_abs_rank_displacement"], max(displacement), 0)
    compare(pooled["between_transform_mean_abs_rank_displacement"], mean(displacement))

    for row in read_csv(results / "06_LEAVE_ONE_GENE_OUT.csv"):
        gene_index = PROGRAM.index(row["omitted_gene"])
        values = [sample[gene_index] for sample in leave_one_out]
        loo_ranks = ranks(values)
        displacement = [abs(left - right) for left, right in zip(frozen_ranks, loo_ranks)]
        expected = {
            "spearman_vs_full": rank_correlation(frozen, values),
            "max_abs_rank_displacement": max(displacement),
            "mean_abs_rank_displacement": mean(displacement),
            "donors_with_changed_rank": sum(value > 0 for value in displacement),
            "max_abs_score_change": max(abs(left - right) for left, right in zip(values, frozen)),
        }
        for field, value in expected.items():
            compare(row[field], value)

    mean_absolute = [mean([abs(sample[index] / 12) for sample in z_scores]) for index in range(12)]
    for row in read_csv(results / "07_GENE_DETECTION_CONTRIBUTIONS.csv"):
        gene_index = PROGRAM.index(row["gene"])
        values = [sample[gene_index] for sample in z_scores]
        detected = sum(sample[gene_index] > 0 for sample in program_counts)
        expected = {
            "measured_feature_count": len(symbol_map[PROGRAM[gene_index]]),
            "detected_pseudobulks": detected,
            "pseudobulks": 54,
            "pseudobulk_detection_fraction": detected / 54,
            "reference_population_sd": reference_sd[gene_index],
            "z_mean": mean(values),
            "z_population_sd": math.sqrt(mean([(value - mean(values)) ** 2 for value in values])),
            "contribution_mean": mean(values) / 12,
            "contribution_mean_abs": mean_absolute[gene_index],
            "share_of_pooled_mean_abs_contributions": mean_absolute[gene_index] / math.fsum(mean_absolute),
            **{f"z_{name}": value for name, value in quantiles(values).items()},
        }
        for field, value in expected.items():
            compare(row[field], value)

    receipt = {
        "all_passed": True,
        "checks": checks,
        "max_absolute_error": max_error,
        "tolerance": 1e-11,
        "population": 54,
        "primary_pipeline_imported": False,
        "independent_rank_implementation": "Python sorted exact tie groups",
        "disease_stratification": False,
        "p_values_or_intervals": False,
    }
    output.mkdir(parents=True)
    (output / "13_INDEPENDENT_NUMERICAL_CHECK.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    run(arguments.workspace.resolve(), arguments.results.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    main()
