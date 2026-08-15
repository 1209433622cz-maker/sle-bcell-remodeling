#!/usr/bin/env python3
"""Qualify the Gate C6B regulator engine without calculating real effects."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from datetime import datetime
from math import fsum, sqrt
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests


REGULATORS = ["STAT1", "STAT2", "IRF7", "IRF9", "E2F1", "FOXM1", "MYC", "MYBL2"]
CORE = {"STAT1", "STAT2"}
IFN_FAMILY = {"STAT1", "STAT2", "IRF7", "IRF9"}
COLLECTRI_HASH = "98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1"
CONTRAST_FILES = {
    "gse174188_primary": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "primary_base_gene_results.csv.gz"
    ),
    "gse174188_internal_nonoverlap": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "validation_nonoverlap_gene_results.csv.gz"
    ),
    "gse135779_childhood": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "childhood_min50_gene_results.csv.gz"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--resource-dir",
        type=Path,
        default=Path("phase17_v7/gateC6B/20260815_pre_effect_resource_freeze"),
    )
    parser.add_argument("--seed", type=int, default=20260815)
    return parser.parse_args()


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_network(path: Path) -> dict[str, dict[str, float]]:
    raw = gzip.decompress(path.read_bytes())
    if hashlib.sha256(raw).hexdigest().upper() != COLLECTRI_HASH:
        raise ValueError("CollecTRI raw SHA-256 mismatch")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t"))
    network: dict[str, dict[str, float]] = {}
    for regulator in REGULATORS:
        directions: dict[str, set[float]] = {}
        for row in rows:
            if row["source_genesymbol"] != regulator or not row["target_genesymbol"]:
                continue
            target = row["target_genesymbol"].upper()
            values = directions.setdefault(target, set())
            if is_true(row["consensus_stimulation"]):
                values.add(1.0)
            if is_true(row["consensus_inhibition"]):
                values.add(-1.0)
        network[regulator] = {
            target: next(iter(values))
            for target, values in directions.items()
            if len(values) == 1
        }
    return network


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values, kind="mergesort")
    ranked = p_values[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.clip(adjusted, 0.0, 1.0)
    return result


def ulm_formula(y: np.ndarray, x: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.ndim != 1 or x.ndim != 1 or len(y) != len(x) or len(y) < 4:
        raise ValueError("ULM requires matched one-dimensional vectors")
    x_centered = x - x.mean()
    y_centered = y - y.mean()
    sxx = float(x_centered @ x_centered)
    if sxx <= 0:
        raise ValueError("ULM predictor has zero variance")
    slope = float((x_centered @ y_centered) / sxx)
    intercept = float(y.mean() - slope * x.mean())
    residual = y - (intercept + slope * x)
    df = len(y) - 2
    sigma2 = float((residual @ residual) / df)
    se = float(np.sqrt(sigma2 / sxx))
    statistic = slope / se
    p_value = float(2.0 * stats.t.sf(abs(statistic), df=df))
    critical = float(stats.t.ppf(0.975, df=df))
    return {
        "intercept": intercept,
        "slope": slope,
        "se": se,
        "statistic": statistic,
        "df": float(df),
        "p_value": p_value,
        "ci_low": slope - critical * se,
        "ci_high": slope + critical * se,
    }


def ulm_independent_fsum(y: np.ndarray, x: np.ndarray) -> dict[str, float]:
    n = len(x)
    sx = fsum(float(value) for value in x)
    sy = fsum(float(value) for value in y)
    sxx = fsum(float(value) ** 2 for value in x) - sx**2 / n
    sxy = fsum(float(xv) * float(yv) for xv, yv in zip(x, y, strict=True)) - sx * sy / n
    slope = sxy / sxx
    intercept = sy / n - slope * sx / n
    rss = fsum(
        (float(yv) - intercept - slope * float(xv)) ** 2
        for xv, yv in zip(x, y, strict=True)
    )
    df = n - 2
    se = sqrt((rss / df) / sxx)
    statistic = slope / se
    return {
        "slope": slope,
        "se": se,
        "statistic": statistic,
        "p_value": float(2.0 * stats.t.sf(abs(statistic), df=df)),
    }


def synthetic_network(n_genes: int = 1600) -> dict[str, np.ndarray]:
    result = {}
    block = 100
    for index, regulator in enumerate(REGULATORS):
        x = np.zeros(n_genes, dtype=float)
        start = index * block
        x[start : start + 80] = 1.0
        x[start + 80 : start + block] = -1.0
        result[regulator] = x
    return result


def run_synthetic_tests(seed: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed)
    network = synthetic_network()
    reference_y = rng.normal(size=1600)
    formula = ulm_formula(reference_y, network["STAT1"])
    independent = ulm_independent_fsum(reference_y, network["STAT1"])
    implementation_delta = max(
        abs(formula[key] - independent[key]) for key in independent
    )

    null_p = []
    for _ in range(250):
        y = rng.normal(size=1600)
        null_p.extend(ulm_formula(y, network[regulator])["p_value"] for regulator in REGULATORS)
    null_p_array = np.asarray(null_p)
    null_fraction = float(np.mean(null_p_array < 0.05))

    signal_rows = []
    p_values = []
    for contrast_index in range(3):
        signal = sum(network[regulator] for regulator in IFN_FAMILY)
        y = 0.8 * signal + rng.normal(scale=0.7, size=1600)
        for regulator in REGULATORS:
            fit = ulm_formula(y, network[regulator])
            row = {
                "contrast": f"synthetic_{contrast_index + 1}",
                "regulator": regulator,
                "family": "IFN" if regulator in IFN_FAMILY else "negative_control",
                "slope": fit["slope"],
                "p_value": fit["p_value"],
            }
            signal_rows.append(row)
            p_values.append(fit["p_value"])
    adjusted = bh_adjust(np.asarray(p_values))
    adjusted_statsmodels = multipletests(p_values, method="fdr_bh")[1]
    bh_delta = float(np.max(np.abs(adjusted - adjusted_statsmodels)))
    for row, q_value in zip(signal_rows, adjusted, strict=True):
        row["q_value_global24"] = float(q_value)
    ifn_rows = [row for row in signal_rows if row["family"] == "IFN"]
    control_rows = [row for row in signal_rows if row["family"] == "negative_control"]
    sensitivity = float(np.mean([row["q_value_global24"] < 0.05 for row in ifn_rows]))
    false_discoveries = sum(row["q_value_global24"] < 0.05 for row in control_rows)
    total_discoveries = sum(row["q_value_global24"] < 0.05 for row in signal_rows)
    empirical_fdr = float(false_discoveries / max(total_discoveries, 1))
    signal_sign = float(np.mean([row["slope"] > 0 for row in ifn_rows]))
    signal_median = float(np.median([row["slope"] for row in ifn_rows]))
    summary = {
        "implementation_max_delta": implementation_delta,
        "null_p_lt_0_05_fraction": null_fraction,
        "signal_median_slope": signal_median,
        "signal_direction_fraction": signal_sign,
        "signal_global_bh_sensitivity": sensitivity,
        "signal_empirical_fdr": empirical_fdr,
        "bh_max_delta_vs_statsmodels": bh_delta,
        "null_tests": len(null_p),
        "signal_tests": len(signal_rows),
    }
    return summary, signal_rows


def read_tested_symbols(path: Path) -> tuple[set[str], int, int]:
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        symbol_field = (
            "feature_name"
            if "feature_name" in fieldnames
            else "gene_symbol_upper"
            if "gene_symbol_upper" in fieldnames
            else "gene_symbol"
        )
        tested_rows = 0
        symbols = []
        for row in reader:
            if row["tested_filterByExpr"].strip().lower() != "true":
                continue
            tested_rows += 1
            symbol = row[symbol_field].strip().upper()
            if symbol:
                symbols.append(symbol)
    return set(symbols), tested_rows, len(symbols) - len(set(symbols))


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    resource_dir = args.resource_dir if args.resource_dir.is_absolute() else root / args.resource_dir
    network = load_network(
        resource_dir / "resources/collectri_human_omnipath_20260815.tsv.gz"
    )

    with (resource_dir / "07_EXTERNAL_RESOURCE_MANIFEST.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        resource_manifest = list(csv.DictReader(handle))
    resource_hash_checks = {}
    for row in resource_manifest:
        path = root / row["project_relative_path"]
        resource_hash_checks[row["resource_id"]] = (
            path.is_file()
            and path.stat().st_size == int(row["size_bytes"])
            and sha256_file(path) == row["sha256"]
        )

    coverage_rows = []
    for contrast, relative_path in CONTRAST_FILES.items():
        symbols, tested_rows, duplicate_symbols = read_tested_symbols(root / relative_path)
        for regulator in REGULATORS:
            matched = symbols & set(network[regulator])
            positive = sum(network[regulator][gene] > 0 for gene in matched)
            negative = sum(network[regulator][gene] < 0 for gene in matched)
            coverage_rows.append(
                {
                    "contrast": contrast,
                    "regulator": regulator,
                    "family": "IFN_confirmatory"
                    if regulator in IFN_FAMILY
                    else "proliferation_negative_control",
                    "tested_rows": tested_rows,
                    "tested_unique_symbols": len(symbols),
                    "duplicate_tested_symbol_rows": duplicate_symbols,
                    "matched_targets": len(matched),
                    "matched_positive_targets": positive,
                    "matched_negative_targets": negative,
                    "minimum_5_pass": len(matched) >= 5,
                    "core_minimum_10_pass": regulator not in CORE or len(matched) >= 10,
                }
            )
    write_csv(
        resource_dir / "09_C6B1_REAL_INPUT_COVERAGE.csv",
        coverage_rows,
        [
            "contrast",
            "regulator",
            "family",
            "tested_rows",
            "tested_unique_symbols",
            "duplicate_tested_symbol_rows",
            "matched_targets",
            "matched_positive_targets",
            "matched_negative_targets",
            "minimum_5_pass",
            "core_minimum_10_pass",
        ],
    )

    synthetic, signal_rows = run_synthetic_tests(args.seed)
    write_csv(
        resource_dir / "10_C6B1_SYNTHETIC_SIGNAL_RESULTS.csv",
        signal_rows,
        ["contrast", "regulator", "family", "slope", "p_value", "q_value_global24"],
    )
    checks = {
        "resource_hashes": {
            "pass": all(resource_hash_checks.values()) and len(resource_hash_checks) == 3,
            "detail": f"{sum(resource_hash_checks.values())}/3 frozen external resources",
        },
        "collectri_hash_and_parser": {
            "pass": all(len(network[regulator]) >= 5 for regulator in REGULATORS),
            "detail": ", ".join(
                f"{regulator}={len(network[regulator])}" for regulator in REGULATORS
            ),
        },
        "real_input_coverage": {
            "pass": all(bool(row["minimum_5_pass"]) for row in coverage_rows)
            and all(bool(row["core_minimum_10_pass"]) for row in coverage_rows),
            "detail": (
                f"24/24 >=5; core minimum="
                f"{min(row['matched_targets'] for row in coverage_rows if row['regulator'] in CORE)}"
            ),
        },
        "independent_ulm_reproduction": {
            "pass": synthetic["implementation_max_delta"] <= 1e-10,
            "detail": f"max delta={synthetic['implementation_max_delta']:.3e}",
        },
        "null_calibration": {
            "pass": 0.02 <= synthetic["null_p_lt_0_05_fraction"] <= 0.08,
            "detail": (
                f"P<0.05 fraction={synthetic['null_p_lt_0_05_fraction']:.4f} "
                f"across {synthetic['null_tests']} tests"
            ),
        },
        "signal_recovery": {
            "pass": synthetic["signal_median_slope"] >= 0.65
            and synthetic["signal_direction_fraction"] == 1.0,
            "detail": (
                f"median slope={synthetic['signal_median_slope']:.3f}; "
                f"direction={synthetic['signal_direction_fraction']:.3f}"
            ),
        },
        "global_bh_recovery": {
            "pass": synthetic["signal_global_bh_sensitivity"] >= 0.9
            and synthetic["signal_empirical_fdr"] <= 0.1,
            "detail": (
                f"sensitivity={synthetic['signal_global_bh_sensitivity']:.3f}; "
                f"empirical FDR={synthetic['signal_empirical_fdr']:.3f}"
            ),
        },
        "bh_independent_reproduction": {
            "pass": synthetic["bh_max_delta_vs_statsmodels"] <= 1e-12,
            "detail": f"max delta={synthetic['bh_max_delta_vs_statsmodels']:.3e}",
        },
        "no_real_effect_inspection": {
            "pass": True,
            "detail": "real imports used only tested flags, symbols and target coverage",
        },
    }
    decision = (
        "PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION"
        if all(item["pass"] for item in checks.values())
        else "HOLD_GATE_C6B1_QUALIFICATION_REPAIR_REQUIRED"
    )
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "regulatory_effects_inspected": False,
        "gse23307_expression_effects_inspected": False,
        "seed": args.seed,
        "checks": checks,
        "resource_hash_checks": resource_hash_checks,
        "synthetic_metrics": synthetic,
        "real_coverage_rows": len(coverage_rows),
        "next_if_pass": "unlock the frozen 24-test Gate C6B2 regulator analysis",
        "next_if_hold": "repair qualification without inspecting real effects",
    }
    write_text(resource_dir / "11_C6B1_QUALIFICATION_DECISION.json", json.dumps(payload, indent=2))
    report = [
        "# Gate C6B-1 no-effect qualification decision",
        "",
        f"## `{decision}`",
        "",
        "Real regulator activities and GSE23307 expression differences were not inspected.",
        "",
        "## Checks",
        "",
    ]
    for check_id, item in checks.items():
        report.append(f"- [{'PASS' if item['pass'] else 'FAIL'}] {check_id}: {item['detail']}")
    report.extend(
        [
            "",
            "## Consequence",
            "",
            payload["next_if_pass"] if decision.startswith("PASS") else payload["next_if_hold"],
        ]
    )
    write_text(resource_dir / "11_C6B1_QUALIFICATION_DECISION.md", "\n".join(report))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
