#!/usr/bin/env python3
"""Fit the effect-unlocked, frozen Gate C6B regulator analyses."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from math import fsum, sqrt
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


REGULATORS = ["STAT1", "STAT2", "IRF7", "IRF9", "E2F1", "FOXM1", "MYC", "MYBL2"]
CORE = {"STAT1", "STAT2"}
IFN_FAMILY = {"STAT1", "STAT2", "IRF7", "IRF9"}
CONTROLS = {"E2F1", "FOXM1", "MYC", "MYBL2"}
COLLECTRI_RAW_SHA256 = "98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1"
CONFIRMATORY = {
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
SENSITIVITY = {
    "gse174188_validation_full": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "validation_full_gene_results.csv.gz"
    ),
    "gse174188_primary_min20": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "primary_min20_gene_results.csv.gz"
    ),
    "gse174188_primary_min100": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "primary_min100_gene_results.csv.gz"
    ),
    "gse174188_primary_residual_risk_negative": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "primary_residual_risk_negative_gene_results.csv.gz"
    ),
    "gse174188_flare_full": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "flare_full_gene_results.csv.gz"
    ),
    "gse135779_combined_min20": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "combined_min20_gene_results.csv.gz"
    ),
    "gse135779_combined_min50": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "combined_min50_gene_results.csv.gz"
    ),
    "gse135779_combined_min100": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "combined_min100_gene_results.csv.gz"
    ),
    "gse135779_adult_directional": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "adult_min50_gene_results.csv.gz"
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
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("phase17_v7/gateC6B/20260815_regulatory_evidence"),
    )
    parser.add_argument("--seed", type=int, default=20260815)
    parser.add_argument("--resamples", type=int, default=100)
    parser.add_argument("--resample-fraction", type=float, default=0.8)
    return parser.parse_args()


def is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def bh_adjust(p_values: list[float]) -> np.ndarray:
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranked = values[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.clip(adjusted, 0.0, 1.0)
    return result


def load_network(path: Path) -> dict[str, dict[str, float]]:
    raw = gzip.decompress(path.read_bytes())
    if hashlib.sha256(raw).hexdigest().upper() != COLLECTRI_RAW_SHA256:
        raise ValueError("CollecTRI raw SHA-256 mismatch")
    rows = csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t")
    directions: dict[str, dict[str, set[float]]] = {
        regulator: {} for regulator in REGULATORS
    }
    for row in rows:
        regulator = row["source_genesymbol"]
        target = row["target_genesymbol"].strip().upper()
        if regulator not in directions or not target:
            continue
        signs = directions[regulator].setdefault(target, set())
        if is_true(row["consensus_stimulation"]):
            signs.add(1.0)
        if is_true(row["consensus_inhibition"]):
            signs.add(-1.0)
    return {
        regulator: {
            target: next(iter(signs))
            for target, signs in targets.items()
            if len(signs) == 1
        }
        for regulator, targets in directions.items()
    }


def load_ranked_statistics(path: Path) -> tuple[list[str], np.ndarray, dict[str, Any]]:
    values: dict[str, list[float]] = defaultdict(list)
    tested_rows = 0
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        symbol_field = (
            "feature_name"
            if "feature_name" in fields
            else "gene_symbol_upper"
            if "gene_symbol_upper" in fields
            else "gene_symbol"
        )
        for row in reader:
            if not is_true(row["tested_filterByExpr"]):
                continue
            tested_rows += 1
            symbol = row[symbol_field].strip().upper()
            if not symbol or not row["logFC"] or not row["F"]:
                raise ValueError(f"Missing tested effect value in {path}: {row}")
            log_fc = float(row["logFC"])
            f_value = float(row["F"])
            if f_value < 0 or not np.isfinite(log_fc) or not np.isfinite(f_value):
                raise ValueError(f"Invalid tested effect value in {path}: {row}")
            values[symbol].append(float(np.sign(log_fc) * np.sqrt(f_value)))
    symbols = sorted(values)
    statistics = np.asarray([float(np.mean(values[symbol])) for symbol in symbols])
    audit = {
        "input_path": path.as_posix(),
        "input_sha256": sha256_file(path),
        "tested_rows": tested_rows,
        "unique_symbols": len(symbols),
        "duplicate_symbol_rows": tested_rows - len(symbols),
        "statistic_min": float(statistics.min()),
        "statistic_max": float(statistics.max()),
    }
    return symbols, statistics, audit


def ulm(y: np.ndarray, x: np.ndarray) -> dict[str, float]:
    n = len(x)
    sx = fsum(float(value) for value in x)
    sy = fsum(float(value) for value in y)
    sxx = fsum(float(value) ** 2 for value in x) - sx**2 / n
    if sxx <= 0:
        raise ValueError("ULM predictor has zero variance")
    sxy = (
        fsum(float(xv) * float(yv) for xv, yv in zip(x, y, strict=True))
        - sx * sy / n
    )
    slope = sxy / sxx
    intercept = sy / n - slope * sx / n
    residual_ss = fsum(
        (float(yv) - intercept - slope * float(xv)) ** 2
        for xv, yv in zip(x, y, strict=True)
    )
    df = n - 2
    se = sqrt((residual_ss / df) / sxx)
    statistic = slope / se
    critical = float(stats.t.ppf(0.975, df=df))
    return {
        "slope": slope,
        "se": se,
        "t_statistic": statistic,
        "df": df,
        "p_value": float(2.0 * stats.t.sf(abs(statistic), df=df)),
        "ci_low": slope - critical * se,
        "ci_high": slope + critical * se,
    }


def build_predictor(symbols: list[str], weights: dict[str, float]) -> np.ndarray:
    return np.asarray([weights.get(symbol, 0.0) for symbol in symbols], dtype=float)


def fit_regulator(
    contrast: str,
    symbols: list[str],
    y: np.ndarray,
    regulator: str,
    weights: dict[str, float],
    input_role: str,
) -> dict[str, Any]:
    x = build_predictor(symbols, weights)
    fit = ulm(y, x)
    matched = [symbol for symbol in symbols if symbol in weights]
    return {
        "contrast": contrast,
        "input_role": input_role,
        "regulator": regulator,
        "family": "IFN_confirmatory" if regulator in IFN_FAMILY else "proliferation_control",
        "tested_unique_symbols": len(symbols),
        "matched_targets": len(matched),
        "matched_positive_targets": sum(weights[symbol] > 0 for symbol in matched),
        "matched_negative_targets": sum(weights[symbol] < 0 for symbol in matched),
        **fit,
        "direction": "positive" if fit["slope"] > 0 else "negative" if fit["slope"] < 0 else "zero",
    }


def stable_seed(base_seed: int, contrast: str, regulator: str) -> int:
    token = f"{base_seed}|{contrast}|{regulator}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(token).digest()[:8], "little")


def influence_diagnostics(
    contrast: str,
    symbols: list[str],
    y: np.ndarray,
    regulator: str,
    weights: dict[str, float],
    full_slope: float,
    seed: int,
    resamples: int,
    fraction: float,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    matched = [symbol for symbol in symbols if symbol in weights]
    symbol_array = np.asarray(symbols)
    loo_rows: list[dict[str, Any]] = []
    for target in matched:
        keep = symbol_array != target
        fit = ulm(y[keep], build_predictor(symbol_array[keep].tolist(), weights))
        loo_rows.append(
            {
                "contrast": contrast,
                "regulator": regulator,
                "deleted_target": target,
                "slope": fit["slope"],
                "same_direction_as_full": np.sign(fit["slope"]) == np.sign(full_slope),
            }
        )

    rng = np.random.default_rng(stable_seed(seed, contrast, regulator))
    sample_size = max(2, int(np.ceil(len(matched) * fraction)))
    resample_rows: list[dict[str, Any]] = []
    for replicate in range(1, resamples + 1):
        selected = sorted(rng.choice(matched, size=sample_size, replace=False).tolist())
        sampled_weights = {target: weights[target] for target in selected}
        fit = ulm(y, build_predictor(symbols, sampled_weights))
        resample_rows.append(
            {
                "contrast": contrast,
                "regulator": regulator,
                "replicate": replicate,
                "sampled_targets": sample_size,
                "slope": fit["slope"],
                "positive": fit["slope"] > 0,
                "same_direction_as_full": np.sign(fit["slope"]) == np.sign(full_slope),
            }
        )
    summary = {
        "contrast": contrast,
        "regulator": regulator,
        "matched_targets": len(matched),
        "full_slope": full_slope,
        "loo_min_slope": min(row["slope"] for row in loo_rows),
        "loo_max_slope": max(row["slope"] for row in loo_rows),
        "loo_same_direction_fraction": float(
            np.mean([row["same_direction_as_full"] for row in loo_rows])
        ),
        "loo_all_same_direction": all(row["same_direction_as_full"] for row in loo_rows),
        "resamples": resamples,
        "resample_fraction": fraction,
        "resample_sampled_targets": sample_size,
        "resample_positive_fraction": float(
            np.mean([row["positive"] for row in resample_rows])
        ),
        "resample_same_direction_fraction": float(
            np.mean([row["same_direction_as_full"] for row in resample_rows])
        ),
    }
    return summary, loo_rows, resample_rows


def main() -> None:
    args = parse_args()
    if not 0 < args.resample_fraction <= 1:
        raise ValueError("--resample-fraction must be in (0, 1]")
    root = args.project_root.resolve()
    resource_dir = args.resource_dir if args.resource_dir.is_absolute() else root / args.resource_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    qualification = json.loads(
        (resource_dir / "11_C6B1_QUALIFICATION_DECISION.json").read_text(encoding="utf-8")
    )
    if qualification["decision"] != "PASS_GATE_C6B1_NO_EFFECT_QUALIFICATION":
        raise RuntimeError("Gate C6B-1 qualification did not authorize effect inspection")
    if qualification["regulatory_effects_inspected"]:
        raise RuntimeError("Qualification record must be a no-effect record")

    network_path = resource_dir / "resources/collectri_human_omnipath_20260815.tsv.gz"
    network = load_network(network_path)
    confirmatory_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []
    input_audit_rows: list[dict[str, Any]] = []
    contrast_data: dict[str, tuple[list[str], np.ndarray]] = {}

    for contrast, relative_path in CONFIRMATORY.items():
        symbols, y, audit = load_ranked_statistics(root / relative_path)
        audit.update({"contrast": contrast, "input_role": "confirmatory"})
        input_audit_rows.append(audit)
        contrast_data[contrast] = (symbols, y)
        confirmatory_rows.extend(
            fit_regulator(contrast, symbols, y, regulator, network[regulator], "confirmatory")
            for regulator in REGULATORS
        )

    global_q = bh_adjust([row["p_value"] for row in confirmatory_rows])
    for row, q_value in zip(confirmatory_rows, global_q, strict=True):
        row["q_value_global24"] = float(q_value)
    for contrast in CONFIRMATORY:
        positions = [index for index, row in enumerate(confirmatory_rows) if row["contrast"] == contrast]
        q_values = bh_adjust([confirmatory_rows[index]["p_value"] for index in positions])
        for index, q_value in zip(positions, q_values, strict=True):
            confirmatory_rows[index]["q_value_within_contrast_descriptive"] = float(q_value)

    influence_rows: list[dict[str, Any]] = []
    loo_rows: list[dict[str, Any]] = []
    resample_rows: list[dict[str, Any]] = []
    for row in confirmatory_rows:
        if row["regulator"] not in IFN_FAMILY:
            continue
        symbols, y = contrast_data[row["contrast"]]
        summary, loo, resampling = influence_diagnostics(
            row["contrast"],
            symbols,
            y,
            row["regulator"],
            network[row["regulator"]],
            row["slope"],
            args.seed,
            args.resamples,
            args.resample_fraction,
        )
        influence_rows.append(summary)
        loo_rows.extend(loo)
        resample_rows.extend(resampling)

    for contrast, relative_path in SENSITIVITY.items():
        symbols, y, audit = load_ranked_statistics(root / relative_path)
        audit.update({"contrast": contrast, "input_role": "supportive_sensitivity"})
        input_audit_rows.append(audit)
        sensitivity_rows.extend(
            fit_regulator(
                contrast,
                symbols,
                y,
                regulator,
                network[regulator],
                "supportive_sensitivity",
            )
            for regulator in REGULATORS
        )
    sensitivity_q = bh_adjust([row["p_value"] for row in sensitivity_rows])
    for row, q_value in zip(sensitivity_rows, sensitivity_q, strict=True):
        row["q_value_descriptive_all_sensitivities"] = float(q_value)

    result_fields = [
        "contrast",
        "input_role",
        "regulator",
        "family",
        "tested_unique_symbols",
        "matched_targets",
        "matched_positive_targets",
        "matched_negative_targets",
        "slope",
        "se",
        "t_statistic",
        "df",
        "p_value",
        "ci_low",
        "ci_high",
        "direction",
        "q_value_global24",
        "q_value_within_contrast_descriptive",
    ]
    write_csv(output_dir / "01_CONFIRMATORY_REGULATOR_RESULTS.csv", confirmatory_rows, result_fields)
    write_csv(
        output_dir / "02_IFN_TARGET_INFLUENCE_SUMMARY.csv",
        influence_rows,
        list(influence_rows[0]),
    )
    write_csv(output_dir / "03_IFN_TARGET_LEAVE_ONE_OUT.csv", loo_rows, list(loo_rows[0]))
    write_csv(output_dir / "04_IFN_TARGET_RESAMPLING.csv", resample_rows, list(resample_rows[0]))
    sensitivity_fields = [field for field in result_fields if not field.startswith("q_value_")]
    sensitivity_fields.append("q_value_descriptive_all_sensitivities")
    write_csv(output_dir / "05_SUPPORTIVE_SENSITIVITY_REGULATOR_RESULTS.csv", sensitivity_rows, sensitivity_fields)
    write_csv(output_dir / "06_INPUT_AUDIT.csv", input_audit_rows, list(input_audit_rows[0]))

    by_key = {(row["contrast"], row["regulator"]): row for row in confirmatory_rows}
    core_positive = all(
        by_key[(contrast, regulator)]["slope"] > 0
        for contrast in CONFIRMATORY
        for regulator in CORE
    )
    core_significant_each = all(
        any(
            by_key[(contrast, regulator)]["slope"] > 0
            and by_key[(contrast, regulator)]["q_value_global24"] < 0.05
            for regulator in CORE
        )
        for contrast in CONFIRMATORY
    )
    ifn_pattern = all(
        sum(by_key[(contrast, regulator)]["slope"] > 0 for regulator in IFN_FAMILY) >= 3
        and not any(
            by_key[(contrast, regulator)]["slope"] < 0
            and by_key[(contrast, regulator)]["q_value_global24"] < 0.05
            for regulator in IFN_FAMILY
        )
        for contrast in CONFIRMATORY
    )
    control_specificity = not any(
        all(
            by_key[(contrast, regulator)]["slope"] > 0
            and by_key[(contrast, regulator)]["q_value_global24"] < 0.05
            for contrast in CONFIRMATORY
        )
        for regulator in CONTROLS
    )
    core_influence = all(
        row["loo_all_same_direction"] and row["resample_positive_fraction"] >= 0.95
        for row in influence_rows
        if row["regulator"] in CORE
    )
    checks = {
        "core_positive_all_three": core_positive,
        "core_global_q_each_contrast": core_significant_each,
        "ifn_family_direction_and_no_reversal": ifn_pattern,
        "proliferation_control_specificity": control_specificity,
        "core_leave_one_out_and_resampling": core_influence,
        "confirmatory_family_exactly_24": len(confirmatory_rows) == 24,
        "qualification_unlock_verified": True,
    }
    decision = (
        "PASS_GATE_C6B2_REGULATOR_LAYER_PENDING_ORTHOGONAL_REVIEW"
        if all(checks.values())
        else "HOLD_GATE_C6B2_REGULATOR_LAYER_CENTRAL_CLAIM_NOT_AUTHORIZED"
    )
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "regulatory_effects_inspected": True,
        "confirmatory_tests": len(confirmatory_rows),
        "global_bh_family": "8 frozen regulators x 3 frozen confirmatory contrasts",
        "seed": args.seed,
        "target_resamples": args.resamples,
        "target_resample_fraction": args.resample_fraction,
        "checks": checks,
        "collectri_compressed_sha256": sha256_file(network_path),
        "next_if_pass": "run frozen MSigDB and GSE23307 orthogonal response analyses",
        "next_if_hold": "retain replicated IFN/ISG program and remove a central regulator claim",
    }
    write_text(output_dir / "07_GATE_C6B2_DECISION.json", json.dumps(payload, indent=2))
    report = [
        "# Gate C6B-2 frozen regulator decision",
        "",
        f"## `{decision}`",
        "",
        "The 24-test family and all target diagnostics follow the pre-effect contract.",
        "",
        "## Checks",
        "",
    ]
    report.extend(
        f"- [{'PASS' if passed else 'FAIL'}] {name}" for name, passed in checks.items()
    )
    report.extend(["", "## Confirmatory estimates", ""])
    for row in confirmatory_rows:
        report.append(
            f"- {row['contrast']} / {row['regulator']}: slope={row['slope']:.4f}, "
            f"95% CI {row['ci_low']:.4f} to {row['ci_high']:.4f}, "
            f"global q={row['q_value_global24']:.3g}, targets={row['matched_targets']}"
        )
    report.extend(
        [
            "",
            "## Consequence",
            "",
            payload["next_if_pass"] if decision.startswith("PASS") else payload["next_if_hold"],
        ]
    )
    write_text(output_dir / "07_GATE_C6B2_DECISION.md", "\n".join(report))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
