#!/usr/bin/env python3
"""Fit the frozen RP-v3 WP1 annotation-sensitivity estimands and paired bootstrap."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm


MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]
BRANCHES = ["beta_A0", "beta_A1", "beta_A2"]
OUTPUTS = BRANCHES + ["delta_beta_ann_A1", "delta_beta_ann_A2"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def t0_score(counts: np.ndarray, totals: np.ndarray, means: np.ndarray, sds: np.ndarray) -> np.ndarray:
    counts = np.asarray(counts, dtype=float)
    totals = np.asarray(totals, dtype=float)
    if counts.ndim != 2 or len(totals) != counts.shape[0] or (totals <= 0).any():
        raise ValueError("Invalid pseudobulk counts or full-library totals")
    log_expression = np.log2(counts * 1e6 / totals[:, None] + 0.5)
    return ((log_expression - means) / sds).mean(axis=1)


def reconstruct_a1_score(
    counts: np.ndarray,
    totals: np.ndarray,
    weights: np.ndarray,
    means: np.ndarray,
    sds: np.ndarray,
) -> np.ndarray:
    """Reconstruct linear CPM across bins before applying frozen T0."""
    counts = np.asarray(counts, dtype=float)
    totals = np.asarray(totals, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if counts.ndim != 3 or counts.shape[1] != len(weights):
        raise ValueError("A1 counts must be donor x bin x gene")
    if totals.shape != counts.shape[:2] or (totals <= 0).any():
        raise ValueError("A1 full-library totals are missing or non-positive")
    if (weights <= 0).any() or not np.isclose(weights.sum(), 1.0, atol=1e-12, rtol=0):
        raise ValueError("pi_ref must contain positive weights summing to one")
    bin_cpm = counts * 1e6 / totals[:, :, None]
    reconstructed_cpm = np.sum(bin_cpm * weights[None, :, None], axis=1)
    log_expression = np.log2(reconstructed_cpm + 0.5)
    return ((log_expression - means) / sds).mean(axis=1)


def design_rank(values: np.ndarray, tolerance: float = 1e-10) -> int:
    matrix = np.asarray(values, dtype=float).copy()
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        return 0
    rank = 0
    for column in range(matrix.shape[1]):
        if rank >= matrix.shape[0]:
            break
        pivot = rank + int(np.argmax(np.abs(matrix[rank:, column])))
        if abs(matrix[pivot, column]) <= tolerance:
            continue
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        matrix[rank] /= matrix[rank, column]
        for row in range(rank + 1, matrix.shape[0]):
            matrix[row] -= matrix[row, column] * matrix[rank]
        rank += 1
    return rank


def ols_coefficient(response: np.ndarray, design: np.ndarray, coefficient_index: int = 1) -> float:
    response = np.asarray(response, dtype=float)
    design = np.asarray(design, dtype=float)
    if not np.isfinite(response).all() or design_rank(design) != design.shape[1]:
        raise ValueError("Non-finite or rank-deficient OLS input")
    beta = np.linalg.lstsq(design, response, rcond=None)[0]
    return float(beta[coefficient_index])


def score_branch(frame: pd.DataFrame, genes: list[str], means: np.ndarray, sds: np.ndarray) -> np.ndarray:
    counts = frame[[f"raw_IFN_{gene}" for gene in genes]].to_numpy(float)
    totals = frame["full_raw_library_total"].to_numpy(float)
    return t0_score(counts, totals, means, sds)


def percentile_interval(values: pd.Series) -> tuple[float, float]:
    clean = values.dropna().to_numpy(float)
    if not len(clean):
        return float("nan"), float("nan")
    low, high = np.quantile(clean, [0.025, 0.975])
    return float(low), float(high)


def plot_results(intervals: pd.DataFrame, output: Path) -> None:
    labels = {
        "beta_A0": "A0 historical scaffold",
        "beta_A1": "A1 common-composition reconstruction",
        "beta_A2": "A2 strong-ISG-list-excluded representation",
        "delta_beta_ann_A1": "A1 - A0",
        "delta_beta_ann_A2": "A2 - A0",
    }
    frame = intervals.set_index("estimand").loc[OUTPUTS].reset_index()
    y = np.arange(len(frame))[::-1]
    colors = ["#2C7BB6", "#D95F02", "#1B9E77", "#D95F02", "#1B9E77"]
    fig, ax = plt.subplots(figsize=(7.1, 4.3))
    for idx, row in frame.iterrows():
        ax.errorbar(
            row["estimate"], y[idx],
            xerr=[[row["estimate"] - row["bootstrap_ci_low"]], [row["bootstrap_ci_high"] - row["estimate"]]],
            fmt="o", color=colors[idx], capsize=3, linewidth=1.5, markersize=6,
        )
    ax.axvline(0, color="#555555", linestyle="--", linewidth=1)
    ax.axhline(1.5, color="#BDBDBD", linewidth=0.8)
    ax.set_yticks(y, [labels[item] for item in frame["estimand"]])
    ax.set_xlabel("Managed-SLE coefficient or paired coefficient difference")
    ax.set_title("WP1 annotation-sensitivity estimates", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0.01, -0.20,
        "Points: frozen 68-donor analysis set; intervals: 2,000-attempt paired percentile bootstrap",
        transform=ax.transAxes, fontsize=8, va="top",
    )
    fig.tight_layout()
    fig.savefig(output.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main(prefit: Path, contract_dir: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Use a new output directory: {output}")
    output.mkdir(parents=True)

    gate = json.loads((contract_dir / "04_PREFIT_GATE_STATUS.json").read_text(encoding="utf-8"))
    if gate.get("status") != "PASS_WP1_PREFIT_UNLOCK" or gate.get("disease_coefficients_fitted") is not False:
        raise ValueError("WP1 prefit gate has not passed")
    bootstrap = gate["bootstrap"]
    seed = int(bootstrap["seed"])
    attempted = int(bootstrap["attempted_replicates"])
    if attempted != 2000:
        raise ValueError("The frozen bootstrap contract requires exactly 2,000 attempts")

    shared = pd.read_csv(contract_dir / "02_SHARED_ANALYSIS_SET.csv", dtype={"donor_id": str})
    design_frame = pd.read_csv(contract_dir / "03_SHARED_DESIGN_MATRIX.csv", dtype={"donor_id": str})
    if sha256(contract_dir / "02_SHARED_ANALYSIS_SET.csv") != gate["shared_donor_ID_hash"]:
        raise ValueError("Shared analysis-set hash mismatch")
    if sha256(contract_dir / "03_SHARED_DESIGN_MATRIX.csv") != gate["shared_covariate_matrix_hash"]:
        raise ValueError("Shared design-matrix hash mismatch")
    if MODEL_COLUMNS != gate["model_columns"]:
        raise ValueError("Frozen model-column order mismatch")

    t0 = pd.read_csv(prefit / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv")
    genes = t0["gene_symbol"].astype(str).tolist()
    means = t0["control_mean_log2_cpm_plus_0_5"].to_numpy(float)
    sds = t0["control_population_sd_log2_cpm_plus_0_5"].to_numpy(float)
    if len(genes) != 12 or (sds <= 0).any() or not t0["reference_strata"].eq(43).all():
        raise ValueError("Frozen T0 reference is invalid")
    if sha256(prefit / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv") != gate["T0_reference_hash"]:
        raise ValueError("T0 reference hash mismatch")

    order = pd.Index(shared["stratum_id"])
    frames = {}
    for branch in ("A0", "A2"):
        frame = pd.read_csv(prefit / f"{branch}_sufficient_raw_counts.csv", dtype={"donor_id": str})
        frame = frame.set_index("stratum_id").loc[order].reset_index()
        if not np.array_equal(frame["donor_id"].to_numpy(), shared["donor_id"].to_numpy()):
            raise ValueError(f"{branch} donor alignment failure")
        frames[branch] = frame

    pi = pd.read_csv(prefit / "09_PI_REF.csv").sort_values("a1_bin")
    if sha256(prefit / "09_PI_REF.csv") != gate["pi_ref_hash"]:
        raise ValueError("pi_ref hash mismatch")
    weights = pi["pi_ref"].to_numpy(float)
    a1 = pd.read_csv(prefit / "A1_bin_sufficient_raw_counts.csv", dtype={"donor_id": str})
    a1 = a1[a1["stratum_id"].isin(order)].copy()
    a1["stratum_order"] = order.get_indexer(a1["stratum_id"])
    a1 = a1.sort_values(["stratum_order", "A1_bin"])
    if len(a1) != len(order) * 5 or not np.array_equal(a1["A1_bin"].to_numpy(), np.tile(np.arange(1, 6), len(order))):
        raise ValueError("A1 common-support bins are incomplete or out of order")
    a1_counts = a1[[f"raw_IFN_{gene}" for gene in genes]].to_numpy(float).reshape(len(order), 5, len(genes))
    a1_totals = a1["full_raw_library_total"].to_numpy(float).reshape(len(order), 5)

    scores = design_frame.copy()
    scores["score_A0"] = score_branch(frames["A0"], genes, means, sds)
    scores["score_A1"] = reconstruct_a1_score(a1_counts, a1_totals, weights, means, sds)
    scores["score_A2"] = score_branch(frames["A2"], genes, means, sds)
    if len(scores) != 68 or scores["donor_id"].nunique() != 68 or not np.isfinite(scores.filter(like="score_")).all().all():
        raise ValueError("Invalid WP1 donor-score table")
    scores.to_csv(output / "01_WP1_DONOR_SCORES.csv", index=False)

    x = scores[MODEL_COLUMNS].to_numpy(float)
    if design_rank(x) != 4:
        raise ValueError("Frozen shared design is not full rank")
    point_rows = []
    responses = {}
    for branch in ("A0", "A1", "A2"):
        response = scores[f"score_{branch}"].to_numpy(float)
        responses[branch] = response
        fit = sm.OLS(response, x).fit(cov_type="HC3", use_t=True)
        point_rows.append({
            "estimand": f"beta_{branch}",
            "estimate": float(fit.params[1]),
            "hc3_se_diagnostic": float(fit.bse[1]),
            "hc3_ci_low_diagnostic": float(fit.conf_int(alpha=0.05)[1, 0]),
            "hc3_ci_high_diagnostic": float(fit.conf_int(alpha=0.05)[1, 1]),
            "n_donors": len(scores),
            "design_rank": design_rank(x),
        })
    points = pd.DataFrame(point_rows)
    point = dict(zip(points["estimand"], points["estimate"]))
    delta_rows = [
        {"estimand": "delta_beta_ann_A1", "estimate": point["beta_A1"] - point["beta_A0"]},
        {"estimand": "delta_beta_ann_A2", "estimate": point["beta_A2"] - point["beta_A0"]},
    ]
    for row in delta_rows:
        row.update({"hc3_se_diagnostic": np.nan, "hc3_ci_low_diagnostic": np.nan,
                    "hc3_ci_high_diagnostic": np.nan, "n_donors": len(scores), "design_rank": design_rank(x)})
    points = pd.concat([points, pd.DataFrame(delta_rows)], ignore_index=True)
    points.to_csv(output / "02_WP1_POINT_ESTIMATES.csv", index=False)

    rng = np.random.default_rng(seed)
    arms = scores["is_managed"].to_numpy(int)
    arm_indices = {arm: np.flatnonzero(arms == arm) for arm in (0, 1)}
    replicate_rows = []
    for replicate in range(1, attempted + 1):
        sampled = np.concatenate([
            rng.choice(arm_indices[0], size=len(arm_indices[0]), replace=True),
            rng.choice(arm_indices[1], size=len(arm_indices[1]), replace=True),
        ])
        xr = x[sampled]
        row = {
            "replicate": replicate,
            "attempted": True,
            "unique_donors": int(np.unique(sampled).size),
            "unique_controls": int(np.unique(sampled[:len(arm_indices[0])]).size),
            "unique_managed": int(np.unique(sampled[len(arm_indices[0]):]).size),
            "design_rank": design_rank(xr),
            "success": False,
            "failure_reason": "",
        }
        try:
            if row["design_rank"] != 4:
                raise ValueError("rank_deficient")
            estimates = {branch: ols_coefficient(responses[branch][sampled], xr) for branch in ("A0", "A1", "A2")}
            if not np.isfinite(list(estimates.values())).all():
                raise ValueError("nonfinite_estimate")
            row.update({
                "beta_A0": estimates["A0"],
                "beta_A1": estimates["A1"],
                "beta_A2": estimates["A2"],
                "delta_beta_ann_A1": estimates["A1"] - estimates["A0"],
                "delta_beta_ann_A2": estimates["A2"] - estimates["A0"],
                "success": True,
            })
        except Exception as exc:
            row["failure_reason"] = str(exc)
            for column in OUTPUTS:
                row[column] = np.nan
        replicate_rows.append(row)
    replicates = pd.DataFrame(replicate_rows)
    replicates.to_csv(output / "03_WP1_BOOTSTRAP_REPLICATES.csv.gz", index=False, compression="gzip")

    successful = replicates[replicates["success"]].copy()
    interval_rows = []
    point_lookup = dict(zip(points["estimand"], points["estimate"]))
    for estimand in OUTPUTS:
        low, high = percentile_interval(successful[estimand])
        interval_rows.append({
            "estimand": estimand,
            "estimate": point_lookup[estimand],
            "bootstrap_ci_low": low,
            "bootstrap_ci_high": high,
            "successful_replicates": len(successful),
            "attempted_replicates": attempted,
            "failure_rate": 1 - len(successful) / attempted,
            "interval_method": "paired percentile",
        })
    intervals = pd.DataFrame(interval_rows)
    intervals.to_csv(output / "04_WP1_BOOTSTRAP_INTERVALS.csv", index=False)

    diagnostics = pd.DataFrame([
        {"comparison": "A1_vs_A0", "pearson_score_correlation": scores[["score_A1", "score_A0"]].corr().iloc[0, 1],
         "mean_score_difference": float((scores["score_A1"] - scores["score_A0"]).mean()),
         "sd_score_difference": float((scores["score_A1"] - scores["score_A0"]).std(ddof=1))},
        {"comparison": "A2_vs_A0", "pearson_score_correlation": scores[["score_A2", "score_A0"]].corr().iloc[0, 1],
         "mean_score_difference": float((scores["score_A2"] - scores["score_A0"]).mean()),
         "sd_score_difference": float((scores["score_A2"] - scores["score_A0"]).std(ddof=1))},
    ])
    diagnostics.to_csv(output / "05_WP1_PAIRWISE_DIAGNOSTICS.csv", index=False)

    failures = attempted - len(successful)
    failure_rate = failures / attempted
    pass_bootstrap = failure_rate <= 0.01 and np.isfinite(intervals[["estimate", "bootstrap_ci_low", "bootstrap_ci_high"]]).all().all()
    gate_status = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_WP1_ANNOTATION_SENSITIVITY_REVIEW_REQUIRED" if pass_bootstrap else "HOLD_WP1_BOOTSTRAP_FAILURE",
        "first_effect_fit_time": datetime.now(timezone.utc).isoformat(),
        "analysis_population": 68,
        "controls": int((arms == 0).sum()),
        "managed_sle": int((arms == 1).sum()),
        "design_columns": MODEL_COLUMNS,
        "design_rank": design_rank(x),
        "A1_operator": "linear CPM reconstruction with frozen pi_ref, followed by frozen T0",
        "A1_interpretation": "joint identity-axis/common-composition standardization sensitivity",
        "A2_interpretation": "historical strong-ISG-list-excluded representation; LY6E retained",
        "bootstrap_seed": seed,
        "attempted_replicates": attempted,
        "successful_replicates": len(successful),
        "failed_replicates": failures,
        "failure_rate": failure_rate,
        "failure_threshold": 0.01,
        "interval_method": "paired percentile",
        "formal_p_values_reported": False,
        "equivalence_margin": None,
        "conditional_on_frozen_objects": ["A2 mapping", "A1 cutpoints", "pi_ref", "T0", "68-donor support set"],
        "G2": "NOT_ASSESSED_FULL_PROTOCOL_PENDING",
        "WP4": "HOLD_CONDITIONAL",
        "SUBMISSION": "HOLD",
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "statsmodels": sm.__version__,
        },
    }
    (output / "06_WP1_GATE_STATUS.json").write_text(json.dumps(gate_status, indent=2), encoding="utf-8")
    plot_results(intervals, output / "08_WP1_ANNOTATION_SENSITIVITY_DIAGNOSTIC")

    values = intervals.set_index("estimand")
    review = f"""# RP v3 WP1 annotation-sensitivity review

## Gate decision

**{gate_status['status']}**

The first disease-effect fit was performed only after the dated prefit contract passed. All three branches use the same 68 donors, the same frozen four-column design and the original 43-control T0 reference.

## Estimates

| Estimand | Estimate | Paired bootstrap 95% CI |
|---|---:|---:|
| beta_A0 | {values.loc['beta_A0','estimate']:.6f} | {values.loc['beta_A0','bootstrap_ci_low']:.6f} to {values.loc['beta_A0','bootstrap_ci_high']:.6f} |
| beta_A1 | {values.loc['beta_A1','estimate']:.6f} | {values.loc['beta_A1','bootstrap_ci_low']:.6f} to {values.loc['beta_A1','bootstrap_ci_high']:.6f} |
| beta_A2 | {values.loc['beta_A2','estimate']:.6f} | {values.loc['beta_A2','bootstrap_ci_low']:.6f} to {values.loc['beta_A2','bootstrap_ci_high']:.6f} |
| delta beta A1 - A0 | {values.loc['delta_beta_ann_A1','estimate']:.6f} | {values.loc['delta_beta_ann_A1','bootstrap_ci_low']:.6f} to {values.loc['delta_beta_ann_A1','bootstrap_ci_high']:.6f} |
| delta beta A2 - A0 | {values.loc['delta_beta_ann_A2','estimate']:.6f} | {values.loc['delta_beta_ann_A2','bootstrap_ci_low']:.6f} to {values.loc['delta_beta_ann_A2','bootstrap_ci_high']:.6f} |

Bootstrap completion was {len(successful)}/{attempted}; failure rate {failure_rate:.3%}. No formal p value, multiplicity claim, equivalence margin or causal interpretation is introduced.

## Interpretation boundary

`beta_A1` is estimated after common-composition reconstruction on the linear CPM scale and therefore combines identity-axis representation with composition standardization. Its delta from A0 is not a pure annotation effect and is not a mediated fraction. A2 excludes the historical strong-ISG feature list but retains LY6E, so it is not a fully IFN12-excluded representation.

WP1 does not unlock WP4, manuscript replacement or submission. The next gate is a result-blind full G2 simulation that exactly reproduces the final A1 operator, 68-donor support/missingness process and paired bootstrap estimator.
"""
    (output / "07_WP1_ADVISOR_REVIEW.md").write_text(review, encoding="utf-8")

    manifest_rows = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "09_WP1_INTEGRITY_MANIFEST.csv":
            manifest_rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    pd.DataFrame(manifest_rows).to_csv(output / "09_WP1_INTEGRITY_MANIFEST.csv", index=False)
    print(json.dumps(gate_status, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefit", type=Path, required=True)
    parser.add_argument("--contract-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    main(args.prefit, args.contract_dir, args.output)
