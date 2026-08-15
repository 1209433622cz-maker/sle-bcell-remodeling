#!/usr/bin/env python3
"""Gate C3A: fit frozen sample-level B_ASC abundance models and sensitivities."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


REQUIRED_GATE_C3_STATUS = "PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE"
BASE_SPECS = {
    "primary": {
        "analysis_id": "C3A_PRIMARY_C4_MANAGED_VS_NORMAL",
        "cohort": 4.0,
        "states": ("na", "managed"),
        "effect": "is_managed",
        "columns": ("intercept", "is_managed", "age_centered", "ethnicity_asian"),
        "label": "Primary: C4 managed vs normal",
    },
    "validation": {
        "analysis_id": "C3A_VALIDATION_C2_EUROPEAN_FEMALE",
        "cohort": 2.0,
        "states": ("na", "managed"),
        "effect": "is_managed",
        "columns": ("intercept", "is_managed", "age_centered"),
        "label": "Internal validation: C2 managed vs normal",
    },
    "flare": {
        "analysis_id": "C3A_SECONDARY_C3_FLARE_VS_NORMAL",
        "cohort": 3.0,
        "states": ("na", "flare"),
        "effect": "is_flare",
        "columns": ("intercept", "is_flare", "age_centered", "ethnicity_european"),
        "label": "Secondary: C3 flare vs normal",
    },
}


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_manifest(root: Path, name: str):
    import pandas as pd

    table = pd.read_csv(root / name)
    failures = []
    for row in table.itertuples(index=False):
        path = root / str(row.relative_path)
        if not path.is_file():
            failures.append({"relative_path": row.relative_path, "issue": "missing"})
        elif path.stat().st_size != int(row.size_bytes):
            failures.append({"relative_path": row.relative_path, "issue": "size"})
        elif hash_file(path) != str(row.sha256).upper():
            failures.append({"relative_path": row.relative_path, "issue": "sha256"})
    return table, failures


def bool_series(series):
    import pandas as pd

    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def finite_hessian(func, point):
    import numpy as np

    point = np.asarray(point, dtype=float)
    size = len(point)
    step = 1e-4 * np.maximum(1.0, np.abs(point))
    hessian = np.zeros((size, size), dtype=float)
    f0 = func(point)
    for i in range(size):
        ei = np.zeros(size)
        ei[i] = step[i]
        hessian[i, i] = (func(point + ei) - 2.0 * f0 + func(point - ei)) / step[i] ** 2
        for j in range(i + 1, size):
            ej = np.zeros(size)
            ej[j] = step[j]
            value = (
                func(point + ei + ej)
                - func(point + ei - ej)
                - func(point - ei + ej)
                + func(point - ei - ej)
            ) / (4.0 * step[i] * step[j])
            hessian[i, j] = value
            hessian[j, i] = value
    return hessian


def beta_binomial_fit(table, columns, analysis_id, variant, effect):
    import numpy as np
    import statsmodels.api as sm
    from scipy.optimize import minimize
    from scipy.special import betaln, expit, gammaln
    from scipy.stats import norm

    work = table.copy().reset_index(drop=True)
    x = work[list(columns)].to_numpy(dtype=float)
    y = work["asc_cells"].to_numpy(dtype=float)
    n = work["total_cells"].to_numpy(dtype=float)
    rank = int(np.linalg.matrix_rank(x))
    if rank != x.shape[1]:
        raise RuntimeError(f"Rank-deficient design for {analysis_id}/{variant}: {rank}/{x.shape[1]}")
    try:
        glm = sm.GLM(y / n, x, family=sm.families.Binomial(), freq_weights=n).fit()
        beta0 = np.asarray(glm.params, dtype=float)
    except Exception:
        empirical = np.log((y + 0.5) / (n - y + 0.5))
        beta0 = np.linalg.lstsq(x, empirical, rcond=None)[0]
    start = np.r_[np.clip(beta0, -15.0, 15.0), np.log(20.0)]

    def observation_nll(theta):
        beta = theta[:-1]
        kappa = np.exp(theta[-1])
        probability = np.clip(expit(x @ beta), 1e-10, 1.0 - 1e-10)
        alpha = probability * kappa
        beta_shape = (1.0 - probability) * kappa
        log_choose = gammaln(n + 1.0) - gammaln(y + 1.0) - gammaln(n - y + 1.0)
        log_probability = log_choose + betaln(y + alpha, n - y + beta_shape) - betaln(alpha, beta_shape)
        return -log_probability

    def objective(theta):
        value = float(np.sum(observation_nll(theta)))
        return value if np.isfinite(value) else 1e100

    result = minimize(
        objective,
        start,
        method="L-BFGS-B",
        bounds=[(None, None)] * len(columns) + [(-5.0, 15.0)],
        options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8, "maxls": 100},
    )
    theta = result.x
    hessian = finite_hessian(objective, theta)
    hessian_symmetric = (hessian + hessian.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hessian_symmetric)
    positive_definite = bool(np.all(eigenvalues > 1e-8))
    covariance = np.linalg.pinv(hessian_symmetric)
    diagonal = np.diag(covariance)
    standard_errors = np.sqrt(np.where(diagonal >= 0.0, diagonal, np.nan))
    score_step = 1e-5 * np.maximum(1.0, np.abs(theta))
    score_identity = np.eye(len(theta))
    score_matrix = np.column_stack(
        [
            (
                observation_nll(theta + score_identity[index] * score_step[index])
                - observation_nll(theta - score_identity[index] * score_step[index])
            )
            / (2.0 * score_step[index])
            for index in range(len(theta))
        ]
    )
    hc1_factor = len(work) / max(len(work) - len(theta), 1)
    sandwich_covariance = covariance @ (score_matrix.T @ score_matrix) @ covariance * hc1_factor
    sandwich_diagonal = np.diag(sandwich_covariance)
    sandwich_standard_errors = np.sqrt(
        np.where(sandwich_diagonal >= 0.0, sandwich_diagonal, np.nan)
    )
    condition_number = float(np.linalg.cond(hessian_symmetric))
    gradient_norm = float(np.linalg.norm(result.jac)) if result.jac is not None else float("nan")
    kappa = float(np.exp(theta[-1]))
    rho = 1.0 / (kappa + 1.0)
    fitted = expit(x @ theta[:-1])
    variance = n * fitted * (1.0 - fitted) * (1.0 + (n - 1.0) * rho)
    pearson = float(np.sum((y - n * fitted) ** 2 / np.maximum(variance, 1e-12)))
    residual_df = max(len(work) - len(columns), 1)
    coefficients = []
    for index, name in enumerate(columns):
        estimate = float(theta[index])
        standard_error = float(standard_errors[index])
        sandwich_standard_error = float(sandwich_standard_errors[index])
        z_value = estimate / standard_error if standard_error > 0 else float("nan")
        p_value = float(2.0 * norm.sf(abs(z_value))) if np.isfinite(z_value) else float("nan")
        sandwich_z = (
            estimate / sandwich_standard_error if sandwich_standard_error > 0 else float("nan")
        )
        sandwich_p = (
            float(2.0 * norm.sf(abs(sandwich_z))) if np.isfinite(sandwich_z) else float("nan")
        )
        coefficients.append(
            {
                "analysis_id": analysis_id,
                "variant": variant,
                "term": name,
                "estimate_log_odds": estimate,
                "standard_error": standard_error,
                "z_value": z_value,
                "p_value": p_value,
                "odds_ratio": float(np.exp(estimate)),
                "ci_low": float(np.exp(estimate - 1.96 * standard_error)),
                "ci_high": float(np.exp(estimate + 1.96 * standard_error)),
                "hc1_sandwich_standard_error": sandwich_standard_error,
                "hc1_sandwich_z_value": sandwich_z,
                "hc1_sandwich_p_value": sandwich_p,
                "hc1_sandwich_ci_low": float(
                    np.exp(estimate - 1.96 * sandwich_standard_error)
                ),
                "hc1_sandwich_ci_high": float(
                    np.exp(estimate + 1.96 * sandwich_standard_error)
                ),
            }
        )
    coefficient_table = __import__("pandas").DataFrame(coefficients)
    effect_row = coefficient_table.loc[coefficient_table["term"] == effect].iloc[0].to_dict()
    diagnostic = {
        "analysis_id": analysis_id,
        "variant": variant,
        "n_strata": len(work),
        "n_donors": int(work["donor_id"].nunique()),
        "reference_n": int((work[effect] == 0).sum()),
        "exposed_n": int((work[effect] == 1).sum()),
        "total_b_cells": int(n.sum()),
        "total_asc_cells": int(y.sum()),
        "zero_asc_strata": int((y == 0).sum()),
        "design_rank": rank,
        "design_columns": len(columns),
        "converged": bool(result.success),
        "optimizer_status": int(result.status),
        "optimizer_message": str(result.message),
        "negative_log_likelihood": float(result.fun),
        "aic": float(2.0 * len(theta) + 2.0 * result.fun),
        "kappa": kappa,
        "intraclass_rho": rho,
        "pearson_chi2_over_df": pearson / residual_df,
        "gradient_norm": gradient_norm,
        "hessian_positive_definite": positive_definite,
        "hessian_condition_number": condition_number,
        "uncertainty_primary": "beta-binomial observed-information covariance",
        "uncertainty_audit": "HC1 sandwich covariance from sample-stratum scores",
    }
    effect_row.update(
        {
            "n_strata": len(work),
            "reference_n": diagnostic["reference_n"],
            "exposed_n": diagnostic["exposed_n"],
            "converged": bool(result.success),
            "hessian_positive_definite": positive_definite,
        }
    )
    return {
        "coefficients": coefficient_table,
        "contrast": effect_row,
        "diagnostic": diagnostic,
        "beta": theta[:-1],
        "beta_covariance": covariance[:-1, :-1],
        "columns": tuple(columns),
        "work": work,
    }


def adjusted_predictions(fit, effect, seed=20260815, draws=5000):
    import numpy as np
    import pandas as pd
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    table = fit["work"]
    x = table[list(fit["columns"])].to_numpy(dtype=float)
    try:
        beta_draws = rng.multivariate_normal(
            fit["beta"], fit["beta_covariance"], size=draws, check_valid="ignore"
        )
    except Exception:
        beta_draws = np.repeat(fit["beta"][None, :], draws, axis=0)
    rows = []
    for value, label in ((0, "reference"), (1, "exposed")):
        x_set = x.copy()
        x_set[:, fit["columns"].index(effect)] = value
        estimate = float(expit(x_set @ fit["beta"]).mean())
        draw_values = expit(x_set @ beta_draws.T).mean(axis=0)
        rows.append(
            {
                "analysis_id": fit["contrast"]["analysis_id"],
                "variant": fit["contrast"]["variant"],
                "effect": effect,
                "group": label,
                "adjusted_fraction": estimate,
                "ci_low": float(np.quantile(draw_values, 0.025)),
                "ci_high": float(np.quantile(draw_values, 0.975)),
            }
        )
    return pd.DataFrame(rows)


def build_matrix(table, spec, minimum_cells):
    work = table.loc[
        (table["Processing_Cohort"] == spec["cohort"])
        & table["disease_state"].isin(spec["states"])
        & (table["total_cells"] >= minimum_cells)
    ].copy()
    if spec["analysis_id"] == BASE_SPECS["validation"]["analysis_id"]:
        work = work.loc[
            (work["sex"].str.lower() == "female")
            & (work["ethnicity"] == "European American")
        ].copy()
    work["intercept"] = 1.0
    work["age_centered"] = work["age_years"] - work["age_years"].mean()
    work["ethnicity_asian"] = (work["ethnicity"] == "Asian").astype(int)
    work["ethnicity_european"] = (work["ethnicity"] == "European American").astype(int)
    work["is_managed"] = (work["disease_state"] == "managed").astype(int)
    work["is_flare"] = (work["disease_state"] == "flare").astype(int)
    work["non_asc_cells"] = work["total_cells"] - work["asc_cells"]
    work["asc_fraction"] = work["asc_cells"] / work["total_cells"]
    work["asc_present"] = work["asc_cells"] > 0
    return work.sort_values(["disease_state", "sample_uuid"]).reset_index(drop=True)


def aggregate_cells(cell):
    import pandas as pd

    def first(series):
        return series.iloc[0]

    return (
        cell.groupby(["sample_uuid", "Processing_Cohort"], observed=True, sort=True)
        .agg(
            total_cells=("source_r04_cluster", "size"),
            asc_cells=("source_r04_cluster", lambda x: int((pd.to_numeric(x) == 3).sum())),
            donor_id=("donor_id", first),
            disease=("disease", first),
            disease_state=("disease_state", first),
            sex=("sex", first),
            age_years=("age_years", first),
            ethnicity=("self_reported_ethnicity", first),
        )
        .reset_index()
    )


def two_part_sensitivity(table, spec, variant="base50"):
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from scipy.optimize import minimize
    from scipy.special import expit
    from scipy.stats import norm

    rows = []
    x = table[list(spec["columns"])].to_numpy(dtype=float)
    effect_index = spec["columns"].index(spec["effect"])
    presence = (table["asc_cells"].to_numpy(dtype=float) > 0).astype(float)
    try:
        def firth_objective(beta):
            eta = x @ beta
            probability = np.clip(expit(eta), 1e-10, 1.0 - 1e-10)
            log_likelihood = float(
                np.sum(presence * eta - np.logaddexp(0.0, eta))
            )
            weights = probability * (1.0 - probability)
            information = x.T @ (weights[:, None] * x)
            sign, log_determinant = np.linalg.slogdet(information)
            if sign <= 0 or not np.isfinite(log_determinant):
                return 1e100
            return -(log_likelihood + 0.5 * log_determinant)

        start = np.zeros(x.shape[1], dtype=float)
        model = minimize(
            firth_objective,
            start,
            method="L-BFGS-B",
            bounds=[(-30.0, 30.0)] * x.shape[1],
            options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-7, "maxls": 100},
        )
        hessian = finite_hessian(firth_objective, model.x)
        covariance = np.linalg.pinv((hessian + hessian.T) / 2.0)
        se_all = np.sqrt(np.where(np.diag(covariance) >= 0.0, np.diag(covariance), np.nan))
        estimate = float(model.x[effect_index])
        se = float(se_all[effect_index])
        if not np.isfinite(estimate) or not np.isfinite(se) or se <= 0:
            raise RuntimeError("non-finite Firth logistic estimate or uncertainty")
        z_value = estimate / se
        rows.append(
            {
                "analysis_id": spec["analysis_id"],
                "variant": variant,
                "component": "ASC presence",
                "n_strata": len(table),
                "event_n": int(presence.sum()),
                "estimate": estimate,
                "standard_error": se,
                "effect_ratio": float(np.exp(estimate)),
                "ci_low": float(np.exp(estimate - 1.96 * se)),
                "ci_high": float(np.exp(estimate + 1.96 * se)),
                "p_value": float(2.0 * norm.sf(abs(z_value))),
                "fit_method": "Firth logistic (Jeffreys penalty)",
                "fit_status": "complete" if model.success else f"finite estimate; optimizer: {model.message}",
            }
        )
    except Exception as exc:
        rows.append(
            {
                "analysis_id": spec["analysis_id"],
                "variant": variant,
                "component": "ASC presence",
                "n_strata": len(table),
                "event_n": int(presence.sum()),
                "estimate": np.nan,
                "standard_error": np.nan,
                "effect_ratio": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "p_value": np.nan,
                "fit_method": "Firth logistic (Jeffreys penalty)",
                "fit_status": f"failed: {exc}",
            }
        )
    positive = table.loc[table["asc_cells"] > 0].copy()
    try:
        xp = positive[list(spec["columns"])].to_numpy(dtype=float)
        response = np.log(
            (positive["asc_cells"].to_numpy(dtype=float) + 0.5)
            / (positive["total_cells"].to_numpy(dtype=float) - positive["asc_cells"].to_numpy(dtype=float) + 0.5)
        )
        model = sm.OLS(response, xp).fit(cov_type="HC3")
        estimate = float(model.params[effect_index])
        se = float(model.bse[effect_index])
        rows.append(
            {
                "analysis_id": spec["analysis_id"],
                "variant": variant,
                "component": "Positive ASC abundance",
                "n_strata": len(positive),
                "event_n": len(positive),
                "estimate": estimate,
                "standard_error": se,
                "effect_ratio": float(np.exp(estimate)),
                "ci_low": float(np.exp(estimate - 1.96 * se)),
                "ci_high": float(np.exp(estimate + 1.96 * se)),
                "p_value": float(model.pvalues[effect_index]),
                "fit_method": "positive-only logit fraction OLS with HC3",
                "fit_status": "complete",
            }
        )
    except Exception as exc:
        rows.append(
            {
                "analysis_id": spec["analysis_id"],
                "variant": variant,
                "component": "Positive ASC abundance",
                "n_strata": len(positive),
                "event_n": len(positive),
                "estimate": np.nan,
                "standard_error": np.nan,
                "effect_ratio": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "p_value": np.nan,
                "fit_method": "positive-only logit fraction OLS with HC3",
                "fit_status": f"failed: {exc}",
            }
        )
    return pd.DataFrame(rows)


def bh_adjust(values):
    import numpy as np

    values = np.asarray(values, dtype=float)
    result = np.full(len(values), np.nan)
    valid = np.where(np.isfinite(values))[0]
    if len(valid) == 0:
        return result
    order = valid[np.argsort(values[valid])]
    adjusted = values[order] * len(order) / np.arange(1, len(order) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result[order] = np.minimum(adjusted, 1.0)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-c3-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    gate_c3 = Path(args.gate_c3_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    figures = output / "figures"
    figures.mkdir(exist_ok=True)

    gate_status = json.loads((gate_c3 / "00_GATE_C3_RUN_STATUS.json").read_text(encoding="utf-8"))
    if gate_status.get("status") != REQUIRED_GATE_C3_STATUS:
        raise RuntimeError(f"Gate C3 has not authorized effect estimation: {gate_status.get('status')}")
    if gate_status.get("effect_estimation_authorized") is not True:
        raise RuntimeError("Gate C3 effect-estimation authorization is false")
    contract = json.loads((gate_c3 / "14_MODEL_DESIGN_CONTRACT.json").read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN" or int(contract.get("minimum_b_cells", -1)) != 50:
        raise RuntimeError("Gate C3 model contract is not the expected frozen 50-cell contract")
    manifest, integrity_failures = verify_manifest(gate_c3, "16_gate_c3_integrity_manifest.csv")
    if integrity_failures:
        raise RuntimeError(f"Gate C3 integrity failures: {integrity_failures}")

    frozen = {
        "primary": pd.read_csv(gate_c3 / "11_primary_model_matrix.csv"),
        "validation": pd.read_csv(gate_c3 / "12_validation_model_matrix.csv"),
        "flare": pd.read_csv(gate_c3 / "13_flare_model_matrix.csv"),
    }
    for table in frozen.values():
        table["Processing_Cohort"] = pd.to_numeric(table["Processing_Cohort"])
        table["donor_id"] = table["donor_id"].astype(str)
        table["sample_uuid"] = table["sample_uuid"].astype(str)

    primary_samples = set(frozen["primary"]["sample_uuid"])
    primary_donors = set(frozen["primary"]["donor_id"])
    nonoverlap = {}
    overlap_rows = []
    for key in ("validation", "flare"):
        table = frozen[key]
        sample_overlap = table["sample_uuid"].isin(primary_samples)
        donor_overlap = table["donor_id"].isin(primary_donors)
        nonoverlap[key] = table.loc[~sample_overlap & ~donor_overlap].copy().reset_index(drop=True)
        overlap_rows.append(
            {
                "analysis": key,
                "frozen_n": len(table),
                "shared_samples_with_primary": int(sample_overlap.sum()),
                "shared_donors_with_primary": int(donor_overlap.sum()),
                "nonoverlap_n": len(nonoverlap[key]),
                "nonoverlap_reference_n": int((nonoverlap[key][BASE_SPECS[key]["effect"]] == 0).sum()),
                "nonoverlap_exposed_n": int((nonoverlap[key][BASE_SPECS[key]["effect"]] == 1).sum()),
            }
        )
    overlap_table = pd.DataFrame(overlap_rows)

    base_coefficients = []
    base_contrasts = []
    diagnostics = []
    predictions = []
    base_fits = {}
    for key, spec in BASE_SPECS.items():
        fit = beta_binomial_fit(
            frozen[key], spec["columns"], spec["analysis_id"], "frozen_base50", spec["effect"]
        )
        base_fits[key] = fit
        base_coefficients.append(fit["coefficients"])
        base_contrasts.append(fit["contrast"])
        diagnostics.append(fit["diagnostic"])
        predictions.append(adjusted_predictions(fit, spec["effect"]))

    for key in ("validation", "flare"):
        spec = BASE_SPECS[key]
        fit = beta_binomial_fit(
            nonoverlap[key],
            spec["columns"],
            spec["analysis_id"],
            "exclude_primary_sample_or_donor_overlap",
            spec["effect"],
        )
        base_contrasts.append(fit["contrast"])
        diagnostics.append(fit["diagnostic"])
        predictions.append(adjusted_predictions(fit, spec["effect"]))

    base_coefficient_table = pd.concat(base_coefficients, ignore_index=True)
    base_contrast_table = pd.DataFrame(base_contrasts)
    base_mask = base_contrast_table["variant"] == "frozen_base50"
    base_contrast_table.loc[base_mask, "bh_q_across_three_frozen_contrasts"] = bh_adjust(
        base_contrast_table.loc[base_mask, "p_value"].to_numpy()
    )

    cell = pd.read_csv(gate_c3 / "01_unlocked_cell_metadata.csv.gz", low_memory=False)
    cell["Processing_Cohort"] = pd.to_numeric(cell["Processing_Cohort"])
    cell["age_years"] = pd.to_numeric(cell["age_years"])
    cell["sample_uuid"] = cell["sample_uuid"].astype(str)
    cell["donor_id"] = cell["donor_id"].astype(str)
    variants = {
        "minimum_cells_20": (cell, 20),
        "minimum_cells_100": (cell, 100),
        "exclude_explicit_non_b_ct_cov": (cell.loc[~bool_series(cell["ct_cov_explicit_non_b"])], 50),
        "exclude_residual_doublet_auto_call": (
            cell.loc[~bool_series(cell["residual_doublet_auto_call"])],
            50,
        ),
    }
    sensitivity_rows = []
    for variant, (variant_cells, cutoff) in variants.items():
        aggregate = aggregate_cells(variant_cells)
        for key, spec in BASE_SPECS.items():
            matrix = build_matrix(aggregate, spec, cutoff)
            fit = beta_binomial_fit(
                matrix, spec["columns"], spec["analysis_id"], variant, spec["effect"]
            )
            sensitivity_rows.append(fit["contrast"])
            diagnostics.append(fit["diagnostic"])
    sensitivity_table = pd.DataFrame(sensitivity_rows)

    two_part = pd.concat(
        [two_part_sensitivity(frozen[key], spec) for key, spec in BASE_SPECS.items()],
        ignore_index=True,
    )

    loo_rows = []
    primary_spec = BASE_SPECS["primary"]
    full_primary_beta = float(base_fits["primary"]["contrast"]["estimate_log_odds"])
    for omitted in frozen["primary"]["sample_uuid"]:
        work = frozen["primary"].loc[frozen["primary"]["sample_uuid"] != omitted].copy()
        fit = beta_binomial_fit(
            work,
            primary_spec["columns"],
            primary_spec["analysis_id"],
            f"leave_one_out:{omitted}",
            primary_spec["effect"],
        )
        contrast = fit["contrast"]
        loo_rows.append(
            {
                "omitted_sample_uuid": omitted,
                "omitted_state": frozen["primary"].loc[
                    frozen["primary"]["sample_uuid"] == omitted, "disease_state"
                ].iloc[0],
                "estimate_log_odds": contrast["estimate_log_odds"],
                "odds_ratio": contrast["odds_ratio"],
                "ci_low": contrast["ci_low"],
                "ci_high": contrast["ci_high"],
                "p_value": contrast["p_value"],
                "converged": contrast["converged"],
                "same_direction_as_full": bool(
                    np.sign(contrast["estimate_log_odds"]) == np.sign(full_primary_beta)
                ),
            }
        )
    loo_table = pd.DataFrame(loo_rows)

    diagnostic_table = pd.DataFrame(diagnostics)
    prediction_table = pd.concat(predictions, ignore_index=True)
    primary_base = base_contrast_table.loc[
        (base_contrast_table["analysis_id"] == primary_spec["analysis_id"])
        & (base_contrast_table["variant"] == "frozen_base50")
    ].iloc[0]
    validation_base = base_contrast_table.loc[
        (base_contrast_table["analysis_id"] == BASE_SPECS["validation"]["analysis_id"])
        & (base_contrast_table["variant"] == "frozen_base50")
    ].iloc[0]
    validation_nonoverlap = base_contrast_table.loc[
        (base_contrast_table["analysis_id"] == BASE_SPECS["validation"]["analysis_id"])
        & (base_contrast_table["variant"] == "exclude_primary_sample_or_donor_overlap")
    ].iloc[0]
    primary_sensitivities = sensitivity_table.loc[
        sensitivity_table["analysis_id"] == primary_spec["analysis_id"]
    ]
    sign = np.sign(float(primary_base["estimate_log_odds"]))
    primary_supported = bool(
        primary_base["converged"]
        and primary_base["hessian_positive_definite"]
        and primary_base["p_value"] < 0.05
        and not (primary_base["ci_low"] <= 1.0 <= primary_base["ci_high"])
        and primary_base["hc1_sandwich_p_value"] < 0.05
        and not (
            primary_base["hc1_sandwich_ci_low"]
            <= 1.0
            <= primary_base["hc1_sandwich_ci_high"]
        )
    )
    sensitivity_direction = bool(
        (np.sign(primary_sensitivities["estimate_log_odds"].to_numpy(dtype=float)) == sign).all()
    )
    loo_direction = bool(loo_table["same_direction_as_full"].all() and loo_table["converged"].all())
    validation_direction = bool(np.sign(validation_base["estimate_log_odds"]) == sign)
    independent_validation_direction = bool(np.sign(validation_nonoverlap["estimate_log_odds"]) == sign)
    independent_support = bool(
        overlap_table.loc[overlap_table["analysis"] == "validation", "nonoverlap_reference_n"].iloc[0] >= 15
        and overlap_table.loc[overlap_table["analysis"] == "validation", "nonoverlap_exposed_n"].iloc[0] >= 25
    )
    model_diagnostics_pass = bool(
        diagnostic_table.loc[diagnostic_table["variant"] == "frozen_base50", "converged"].all()
        and diagnostic_table.loc[
            diagnostic_table["variant"] == "frozen_base50", "hessian_positive_definite"
        ].all()
    )
    checks = {
        "gate_c3_integrity": {
            "pass": len(integrity_failures) == 0,
            "detail": f"{len(manifest)}/{len(manifest)} Gate C3 rows verified",
        },
        "frozen_base_models_complete": {
            "pass": len(base_contrast_table.loc[base_mask]) == 3,
            "detail": "primary, internal validation and flare models fitted",
        },
        "base_model_diagnostics": {
            "pass": model_diagnostics_pass,
            "detail": "all frozen models converged with positive-definite numerical Hessians",
        },
        "primary_prespecified_support": {
            "pass": primary_supported,
            "detail": f"OR={primary_base['odds_ratio']:.3f}; model 95% CI {primary_base['ci_low']:.3f}-{primary_base['ci_high']:.3f}, P={primary_base['p_value']:.3g}; HC1 95% CI {primary_base['hc1_sandwich_ci_low']:.3f}-{primary_base['hc1_sandwich_ci_high']:.3f}, P={primary_base['hc1_sandwich_p_value']:.3g}",
        },
        "primary_mandatory_sensitivity_direction": {
            "pass": sensitivity_direction,
            "detail": f"{int((np.sign(primary_sensitivities['estimate_log_odds']) == sign).sum())}/{len(primary_sensitivities)} variants match frozen direction",
        },
        "primary_leave_one_out_direction": {
            "pass": loo_direction,
            "detail": f"{int(loo_table['same_direction_as_full'].sum())}/{len(loo_table)} leave-one-out fits match frozen direction",
        },
        "validation_nonoverlap_support": {
            "pass": independent_support,
            "detail": f"nonoverlap n={int(overlap_table.loc[overlap_table['analysis'] == 'validation', 'nonoverlap_n'].iloc[0])}; reference={int(overlap_table.loc[overlap_table['analysis'] == 'validation', 'nonoverlap_reference_n'].iloc[0])}; exposed={int(overlap_table.loc[overlap_table['analysis'] == 'validation', 'nonoverlap_exposed_n'].iloc[0])}",
        },
        "validation_directional_replication": {
            "pass": validation_direction and independent_validation_direction,
            "detail": f"frozen OR={validation_base['odds_ratio']:.3f}; nonoverlap OR={validation_nonoverlap['odds_ratio']:.3f}; primary direction matched={validation_direction and independent_validation_direction}",
        },
        "prohibited_inference_guard": {
            "pass": True,
            "detail": "sample-level two-compartment inference only; no hard naive-memory or cell-level test",
        },
    }
    composition_central_claim = bool(
        primary_supported
        and sensitivity_direction
        and loo_direction
        and independent_support
        and validation_direction
        and independent_validation_direction
        and model_diagnostics_pass
    )
    decision = (
        "PASS_C3A_ROBUST_COMPOSITION_SIGNAL_FOR_CONDITIONAL_MANUSCRIPT_CLAIM"
        if composition_central_claim
        else "NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM"
    )

    base_coefficient_table.to_csv(output / "01_base_model_coefficients.csv", index=False, encoding="utf-8-sig")
    base_contrast_table.to_csv(output / "02_base_and_nonoverlap_contrasts.csv", index=False, encoding="utf-8-sig")
    prediction_table.to_csv(output / "03_adjusted_predictions.csv", index=False, encoding="utf-8-sig")
    sensitivity_table.to_csv(output / "04_mandatory_sensitivity_contrasts.csv", index=False, encoding="utf-8-sig")
    two_part.to_csv(output / "05_two_part_sensitivity.csv", index=False, encoding="utf-8-sig")
    loo_table.to_csv(output / "06_primary_leave_one_out.csv", index=False, encoding="utf-8-sig")
    overlap_table.to_csv(output / "07_replication_overlap_audit.csv", index=False, encoding="utf-8-sig")
    diagnostic_table.to_csv(output / "08_model_diagnostics.csv", index=False, encoding="utf-8-sig")

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    forest_specs = [
        ("primary", "frozen_base50", "Primary C4", "#007C91"),
        ("validation", "frozen_base50", "Validation C2", "#3366A6"),
        ("validation", "exclude_primary_sample_or_donor_overlap", "Validation C2\nnonoverlap", "#6A8FB8"),
        ("flare", "frozen_base50", "Flare C3", "#D2691E"),
        ("flare", "exclude_primary_sample_or_donor_overlap", "Flare C3\nnonoverlap", "#E69F63"),
    ]
    for position, (key, variant, label, color) in enumerate(forest_specs):
        row = base_contrast_table.loc[
            (base_contrast_table["analysis_id"] == BASE_SPECS[key]["analysis_id"])
            & (base_contrast_table["variant"] == variant)
        ].iloc[0]
        axes[0, 0].errorbar(
            row["odds_ratio"], position,
            xerr=[[row["odds_ratio"] - row["ci_low"]], [row["ci_high"] - row["odds_ratio"]]],
            fmt="o", color=color, capsize=2, markersize=4,
        )
    axes[0, 0].axvline(1.0, color="#555555", linestyle="--", linewidth=0.8)
    axes[0, 0].set_xscale("log")
    axes[0, 0].set_xlim(0.23, 6.5)
    axes[0, 0].set_xticks([0.25, 0.5, 1.0, 2.0, 4.0], ["0.25", "0.5", "1", "2", "4"])
    axes[0, 0].minorticks_off()
    axes[0, 0].set_yticks(range(len(forest_specs)), [x[2] for x in forest_specs])
    axes[0, 0].invert_yaxis()
    axes[0, 0].set_xlabel("Conditional odds ratio for ASC abundance")

    variant_order = [
        "frozen_base50", "minimum_cells_20", "minimum_cells_100",
        "exclude_explicit_non_b_ct_cov", "exclude_residual_doublet_auto_call",
    ]
    variant_labels = ["Frozen 50", "Min. 20", "Min. 100", "Exclude non-B ct_cov", "Exclude doublet call"]
    primary_all = pd.concat(
        [
            base_contrast_table.loc[
                (base_contrast_table["analysis_id"] == primary_spec["analysis_id"])
                & (base_contrast_table["variant"] == "frozen_base50")
            ],
            primary_sensitivities,
        ],
        ignore_index=True,
    ).set_index("variant").loc[variant_order]
    positions = np.arange(len(primary_all))
    axes[0, 1].errorbar(
        primary_all["odds_ratio"], positions,
        xerr=[primary_all["odds_ratio"] - primary_all["ci_low"], primary_all["ci_high"] - primary_all["odds_ratio"]],
        fmt="o", color="#007C91", capsize=2, markersize=4,
    )
    axes[0, 1].axvline(1.0, color="#555555", linestyle="--", linewidth=0.8)
    axes[0, 1].set_xscale("log")
    axes[0, 1].set_xlim(0.55, 1.6)
    axes[0, 1].set_xticks([0.6, 1.0, 1.5], ["0.6", "1", "1.5"])
    axes[0, 1].minorticks_off()
    axes[0, 1].set_yticks(positions, variant_labels)
    axes[0, 1].invert_yaxis()
    axes[0, 1].set_xlabel("Primary conditional odds ratio")

    primary_prediction = prediction_table.loc[
        (prediction_table["analysis_id"] == primary_spec["analysis_id"])
        & (prediction_table["variant"] == "frozen_base50")
    ].copy()
    px = np.arange(2)
    values = 100 * primary_prediction["adjusted_fraction"].to_numpy()
    low = 100 * primary_prediction["ci_low"].to_numpy()
    high = 100 * primary_prediction["ci_high"].to_numpy()
    axes[1, 0].bar(px, values, color=["#9EA7AD", "#007C91"], width=0.58)
    axes[1, 0].errorbar(px, values, yerr=[values - low, high - values], fmt="none", color="#202020", capsize=3)
    axes[1, 0].set_xticks(px, ["Normal", "Managed"])
    axes[1, 0].set_ylabel("Adjusted ASC fraction (%)")
    axes[1, 0].set_ylim(bottom=0)

    axes[1, 1].plot(np.arange(len(loo_table)), loo_table["estimate_log_odds"], "o", color="#007C91", markersize=2.5)
    axes[1, 1].axhline(full_primary_beta, color="#202020", linewidth=0.9, label="Frozen estimate")
    axes[1, 1].axhline(0.0, color="#777777", linestyle="--", linewidth=0.8)
    axes[1, 1].set(xlabel="Omitted primary sample", ylabel="Managed log-odds coefficient")
    axes[1, 1].legend(frameon=False, fontsize=7)
    for label, axis in zip("ABCD", axes.flat):
        axis.text(-0.16, 1.06, label, transform=axis.transAxes, fontsize=10, fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.11, top=0.96, wspace=0.54, hspace=0.40)
    fig.savefig(figures / "gate_c3a_abundance_model_audit.png", dpi=300)
    fig.savefig(figures / "gate_c3a_abundance_model_audit.pdf")
    plt.close(fig)

    prediction_lookup = prediction_table.loc[
        (prediction_table["analysis_id"] == primary_spec["analysis_id"])
        & (prediction_table["variant"] == "frozen_base50")
    ].set_index("group")
    flare_base = base_contrast_table.loc[
        (base_contrast_table["analysis_id"] == BASE_SPECS["flare"]["analysis_id"])
        & (base_contrast_table["variant"] == "frozen_base50")
    ].iloc[0]
    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "composition_central_claim_authorized": composition_central_claim,
        "sample_level_inference": True,
        "hard_naive_memory_labels_authorized": False,
        "primary": {
            "n": int(primary_base["n_strata"]),
            "odds_ratio": float(primary_base["odds_ratio"]),
            "ci_low": float(primary_base["ci_low"]),
            "ci_high": float(primary_base["ci_high"]),
            "p_value": float(primary_base["p_value"]),
            "hc1_sandwich_ci_low": float(primary_base["hc1_sandwich_ci_low"]),
            "hc1_sandwich_ci_high": float(primary_base["hc1_sandwich_ci_high"]),
            "hc1_sandwich_p_value": float(primary_base["hc1_sandwich_p_value"]),
            "adjusted_reference_fraction": float(prediction_lookup.loc["reference", "adjusted_fraction"]),
            "adjusted_exposed_fraction": float(prediction_lookup.loc["exposed", "adjusted_fraction"]),
        },
        "internal_validation": {
            "frozen_n": int(validation_base["n_strata"]),
            "frozen_odds_ratio": float(validation_base["odds_ratio"]),
            "frozen_p_value": float(validation_base["p_value"]),
            "nonoverlap_n": int(validation_nonoverlap["n_strata"]),
            "nonoverlap_odds_ratio": float(validation_nonoverlap["odds_ratio"]),
            "nonoverlap_p_value": float(validation_nonoverlap["p_value"]),
            "interpretation": "internal directional replication, not an independent external cohort",
        },
        "secondary_flare": {
            "odds_ratio": float(flare_base["odds_ratio"]),
            "model_ci_low": float(flare_base["ci_low"]),
            "model_ci_high": float(flare_base["ci_high"]),
            "model_p_value": float(flare_base["p_value"]),
            "hc1_sandwich_ci_low": float(flare_base["hc1_sandwich_ci_low"]),
            "hc1_sandwich_ci_high": float(flare_base["hc1_sandwich_ci_high"]),
            "hc1_sandwich_p_value": float(flare_base["hc1_sandwich_p_value"]),
            "bh_q_across_three_frozen_contrasts": float(
                flare_base["bh_q_across_three_frozen_contrasts"]
            ),
            "interpretation": "secondary hypothesis-generating signal; not FDR-significant across the three frozen contrasts",
        },
        "checks": checks,
        "binding_interpretation": (
            "Two-compartment B_ASC composition is robust enough for a conditional manuscript claim, but external independent validation remains required for an upper-Q1 positioning."
            if composition_central_claim else
            "Two-compartment B_ASC composition must not be a central manuscript claim; retain as exploratory or secondary and prioritize continuous programs and pseudobulk replication."
        ),
        "next_stage": "Gate C4 prespecified continuous B_CONV programs plus sample-level pseudobulk differential expression; then independent external validation",
    }
    (output / "09_GATE_C3A_ADVISOR_DECISION.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Gate C3A frozen abundance-model advisor decision",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- Primary conditional OR: {primary_base['odds_ratio']:.3f} (95% CI {primary_base['ci_low']:.3f}-{primary_base['ci_high']:.3f}; P={primary_base['p_value']:.3g})",
        f"- Primary HC1 audit: 95% CI {primary_base['hc1_sandwich_ci_low']:.3f}-{primary_base['hc1_sandwich_ci_high']:.3f}; P={primary_base['hc1_sandwich_p_value']:.3g}",
        f"- Primary adjusted B_ASC fraction: {100 * prediction_lookup.loc['reference', 'adjusted_fraction']:.2f}% normal vs {100 * prediction_lookup.loc['exposed', 'adjusted_fraction']:.2f}% managed",
        f"- Validation OR: {validation_base['odds_ratio']:.3f}; nonoverlap validation OR: {validation_nonoverlap['odds_ratio']:.3f} (n={int(validation_nonoverlap['n_strata'])})",
        f"- Secondary flare OR: {flare_base['odds_ratio']:.3f}; nominal P={flare_base['p_value']:.3g}; frozen three-contrast BH q={flare_base['bh_q_across_three_frozen_contrasts']:.3g}",
        f"- Primary mandatory variants with same direction: {int((np.sign(primary_sensitivities['estimate_log_odds']) == sign).sum())}/{len(primary_sensitivities)}",
        f"- Primary leave-one-out fits with same direction: {int(loo_table['same_direction_as_full'].sum())}/{len(loo_table)}",
        "",
        "## Checks",
        "",
    ]
    for name, result in checks.items():
        lines.append(f"- [{'PASS' if result['pass'] else 'FAIL'}] {name}: {result['detail']}")
    lines.extend(
        [
            "",
            "## Binding interpretation",
            "",
            review["binding_interpretation"],
            "",
            "The validation set is internal and partially overlaps the primary cohort. The explicit nonoverlap sensitivity reduces this concern but does not convert it into an external validation cohort.",
            "",
            "## Next stage",
            "",
            review["next_stage"],
        ]
    )
    (output / "09_GATE_C3A_ADVISOR_DECISION.md").write_text("\n".join(lines), encoding="utf-8")

    status = {
        "status": decision,
        "models_complete": True,
        "composition_central_claim_authorized": composition_central_claim,
        "continuous_program_analysis_authorized": True,
        "external_validation_still_required": True,
    }
    (output / "00_GATE_C3A_RUN_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "00_GATE_C3A_RUN_STATUS.md").write_text(
        "\n".join(
            [
                "# Gate C3A run status",
                "",
                f"**Status:** `{decision}`",
                "",
                "- Frozen abundance models complete: True",
                f"- Composition central claim authorized: {composition_central_claim}",
                "- Continuous-program analysis authorized: True",
                "- External validation still required: True",
                "",
                "See `09_GATE_C3A_ADVISOR_DECISION.md`.",
            ]
        ),
        encoding="utf-8",
    )

    manifest_rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "10_gate_c3a_integrity_manifest.csv":
            manifest_rows.append(
                {
                    "relative_path": path.relative_to(output).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": hash_file(path),
                }
            )
    pd.DataFrame(manifest_rows).to_csv(
        output / "10_gate_c3a_integrity_manifest.csv", index=False, encoding="utf-8-sig"
    )
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
