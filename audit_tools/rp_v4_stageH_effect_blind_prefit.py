#!/usr/bin/env python3
"""RP v4 Stage H real-data applicability preflight without effect fitting."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .rp_v3_g2_estimation import solve_batch
    from .rp_v3_wp2_kernels import rank_no_lapack
except ImportError:
    from rp_v3_g2_estimation import solve_batch
    from rp_v3_wp2_kernels import rank_no_lapack


ROOT = Path(__file__).resolve().parents[1]
WP1_FREEZE = ROOT / "phase17_v7/rp_v3_redesign/20261010_wp1_prefit_freeze"
WP1_CONTRACT = ROOT / "phase17_v7/rp_v3_redesign/20261010_wp1_prefit_contract"
WP2_PREFIT = ROOT / "phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit"
CALIBRATION = ROOT / "phase17_v7/rp_v3_redesign/20261010_g2_implementation_freeze/02_G2_CALIBRATION_MODEL.json"
STAGE_C = ROOT / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze"
STAGE_G = ROOT / "phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation"
EXECUTION_SCRIPT = ROOT / "audit_tools/rp_v4_stageI_real_delta_profile.py"
MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def write_text_new(path: Path, content: str) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_csv_new(path: Path, rows: list[dict], columns: list[str]) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def leverage_values(design: np.ndarray) -> np.ndarray:
    design = np.asarray(design, dtype=float)
    crossprod = design.T @ design
    inverse, valid = solve_batch(crossprod[None, :, :], np.eye(4)[None, :, :])
    if not valid[0]:
        raise ValueError("Four-column design inverse failed")
    leverage = np.einsum("ni,ij,nj->n", design, inverse[0], design)
    if not np.isfinite(leverage).all() or not np.isclose(leverage.sum(), 4.0, atol=1e-10):
        raise ValueError("Invalid outcome-blind leverage values")
    return leverage


def manifest_hashes(path: Path) -> dict[str, dict]:
    frame = pd.read_csv(path)
    return {str(row["relative_path"]): row for row in frame.to_dict("records")}


def require_hash(path: Path, expected: str) -> None:
    if not path.is_file() or sha256_file(path).lower() != str(expected).lower():
        raise ValueError(f"Hash mismatch: {path}")


def binding_row(path: Path, role: str) -> dict:
    relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path), "role": role}


def run(output: Path) -> dict:
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Stage H output must be a new directory")
    output.mkdir(parents=True)

    wp1_gate = read_json(WP1_CONTRACT / "04_PREFIT_GATE_STATUS.json")
    wp2_gate = read_json(WP2_PREFIT / "04_PREFIT_STATUS.json")
    stage_g = read_json(STAGE_G / "11_FINAL_SYNTHETIC_GATE.json")
    if wp1_gate.get("status") != "PASS_WP1_PREFIT_UNLOCK" or wp1_gate.get("disease_coefficients_fitted") is not False:
        raise ValueError("WP1 effect-blind parent gate is not valid")
    if wp2_gate.get("status") != "PASS_STRUCTURAL_PREFIT_ONLY" or wp2_gate.get("real_disease_effects_fitted") is not False:
        raise ValueError("WP2 effect-blind parent gate is not valid")
    if stage_g.get("decision") != "G2C_SYNTHETIC_PASS__SEPARATE_REAL_OUTCOME_REVIEW_REQUIRED":
        raise ValueError("Stage G synthetic gate is not valid")
    if stage_g.get("real_WP2_outcomes_authorized") is not False:
        raise ValueError("Unexpected real-outcome authorization")

    wp1_manifest = manifest_hashes(WP1_CONTRACT / "05_PREFIT_INPUT_HASHES.csv")
    wp2_manifest = manifest_hashes(WP2_PREFIT / "12_WP2_PREFIT_INTEGRITY_MANIFEST.csv")
    selected = [
        (WP1_CONTRACT / "02_SHARED_ANALYSIS_SET.csv", wp1_gate["shared_donor_ID_hash"], "frozen 68-donor support"),
        (WP1_CONTRACT / "03_SHARED_DESIGN_MATRIX.csv", wp1_gate["shared_covariate_matrix_hash"], "frozen four-column design"),
        (WP1_CONTRACT / "04_PREFIT_GATE_STATUS.json", None, "effect-blind WP1 parent gate"),
        (WP1_FREEZE / "A1_bin_sufficient_raw_counts.csv", wp1_manifest["A1_bin_sufficient_raw_counts.csv"]["sha256"], "canonical donor-bin raw sufficient counts"),
        (WP1_FREEZE / "09_PI_REF.csv", wp1_gate["pi_ref_hash"], "fixed-profile weights"),
        (WP1_FREEZE / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv", wp1_gate["T0_reference_hash"], "frozen score reference"),
        (WP2_PREFIT / "01_geometry_no_disease_effect.csv", wp2_manifest["01_geometry_no_disease_effect.csv"]["sha256"], "effect-blind observed geometry"),
        (WP2_PREFIT / "02_fixed_composition_coordinates.csv", wp2_manifest["02_fixed_composition_coordinates.csv"]["sha256"], "effect-blind composition coordinates"),
        (WP2_PREFIT / "04_PREFIT_STATUS.json", wp2_manifest["04_PREFIT_STATUS.json"]["sha256"], "effect-blind WP2 parent gate"),
        (CALIBRATION, None, "synthetic calibration anchor"),
        (STAGE_C / "04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json", None, "single-estimand method contract"),
        (STAGE_C / "05_G2C_FINAL_DGP_REGISTRY.csv", None, "synthetic applicability registry"),
        (STAGE_G / "11_FINAL_SYNTHETIC_GATE.json", None, "final synthetic decision"),
        (STAGE_G / "13_STAGE_G_METRIC_SUMMARY.json", None, "synthetic operating-characteristic boundaries"),
        (EXECUTION_SCRIPT, None, "prospective single-result execution code"),
    ]
    for path, expected, _ in selected:
        if not path.is_file():
            raise FileNotFoundError(path)
        if expected:
            require_hash(path, expected)
    binding = [binding_row(path, role) for path, _, role in selected]
    write_csv_new(output / "01_REAL_INPUT_BINDING_MANIFEST.csv", binding, ["path", "bytes", "sha256", "role"])

    shared = pd.read_csv(WP1_CONTRACT / "02_SHARED_ANALYSIS_SET.csv", dtype={"donor_id": str})
    design_frame = pd.read_csv(WP1_CONTRACT / "03_SHARED_DESIGN_MATRIX.csv", dtype={"donor_id": str})
    if len(shared) != 68 or shared["stratum_id"].nunique() != 68 or shared["donor_id"].nunique() != 68:
        raise ValueError("Common-support donor set changed")
    design_frame = design_frame.set_index("stratum_id").loc[shared["stratum_id"]].reset_index()
    if not design_frame["donor_id"].equals(shared["donor_id"]):
        raise ValueError("Donor/design join changed")
    design = design_frame[MODEL_COLUMNS].to_numpy(float)
    if not np.isfinite(design).all() or rank_no_lapack(design) != 4:
        raise ValueError("Design is missing, non-finite or rank deficient")
    if design_frame["is_managed"].value_counts().to_dict() != {1: 37, 0: 31}:
        raise ValueError("Frozen arm support changed")
    leverage = leverage_values(design)

    geometry = pd.read_csv(WP2_PREFIT / "01_geometry_no_disease_effect.csv", dtype={"donor_id": str})
    if len(geometry) != 340 or geometry.duplicated(["stratum_id", "A1_bin"]).any():
        raise ValueError("Observed donor-bin geometry changed")
    expected_index = pd.MultiIndex.from_product([shared["stratum_id"], range(1, 6)], names=["stratum_id", "A1_bin"])
    geometry = geometry.set_index(["stratum_id", "A1_bin"]).loc[expected_index].reset_index()
    numeric = geometry[["cells", "full_captured_UMI", "p_cell", "q_UMI", "captured_UMI_per_cell", "fixed_pi"]]
    if numeric.isna().any().any() or not np.isfinite(numeric.to_numpy(float)).all():
        raise ValueError("Missing/non-finite observed geometry")
    cells = geometry["cells"].to_numpy(int).reshape(68, 5)
    libraries = geometry["full_captured_UMI"].to_numpy(int).reshape(68, 5)
    rates = geometry["captured_UMI_per_cell"].to_numpy(float).reshape(68, 5)
    p_cell = geometry["p_cell"].to_numpy(float).reshape(68, 5)
    q_umi = geometry["q_UMI"].to_numpy(float).reshape(68, 5)
    if cells.min() < 30 or (libraries <= 0).any():
        raise ValueError("Observed support or library condition failed")

    model = read_json(CALIBRATION)
    model_n = np.asarray(model["template_n"], dtype=int)
    model_rate = np.asarray(model["template_rate"], dtype=float)
    model_design = np.asarray(model["synthetic_design"], dtype=float)
    model_pi = np.asarray(model["pi"], dtype=float)
    pi = pd.read_csv(WP1_FREEZE / "09_PI_REF.csv").sort_values("a1_bin")["pi_ref"].to_numpy(float)
    raw = pd.read_csv(WP1_FREEZE / "A1_bin_sufficient_raw_counts.csv", dtype={"donor_id": str})
    raw = raw.set_index(["stratum_id", "A1_bin"]).loc[expected_index].reset_index()
    genes = list(model["gene_order"])
    program = raw[[f"raw_IFN_{gene}" for gene in genes]].to_numpy(float).reshape(68, 5, 12)
    background = libraries - program.sum(axis=2)
    if (background < 0).any():
        raise ValueError("Program counts exceed full libraries")
    categories = np.concatenate([program, background[:, :, None]], axis=2)
    regularizer = float(model["probability_regularizer"])
    observed_probs = (categories + regularizer) / (libraries[:, :, None] + 13 * regularizer)
    model_probs = np.asarray(model["template_probs"], dtype=float)

    comparisons = [
        {"check": "design_anchor_identity", "observed": float(np.max(np.abs(design - model_design))), "criterion": "max_abs_difference = 0", "pass": bool(np.array_equal(design, model_design)), "boundary": "same 68x4 design used by synthetic validation"},
        {"check": "cell_template_identity", "observed": float(np.max(np.abs(cells - model_n))), "criterion": "max_abs_difference = 0", "pass": bool(np.array_equal(cells, model_n)), "boundary": "same 68x5 support template"},
        {"check": "capture_rate_identity", "observed": float(np.max(np.abs(rates - model_rate))), "criterion": "max_abs_difference <= 1e-9", "pass": bool(np.allclose(rates, model_rate, atol=1e-9, rtol=0)), "boundary": "same captured-UMI-per-cell anchor"},
        {"check": "regularized_category_probability_identity", "observed": float(np.max(np.abs(observed_probs - model_probs))), "criterion": "max_abs_difference = 0", "pass": bool(np.array_equal(observed_probs, model_probs)), "boundary": "same 12 genes plus background probabilities"},
        {"check": "fixed_profile_identity", "observed": float(np.max(np.abs(pi - model_pi))), "criterion": "max_abs_difference <= 1e-15", "pass": bool(np.allclose(pi, model_pi, atol=1e-15, rtol=0)), "boundary": "same pi_ref"},
        {"check": "minimum_bin_support", "observed": int(cells.min()), "criterion": ">= 30 cells in all 340 donor-bins", "pass": bool(cells.min() >= 30), "boundary": "no donor removal or threshold change"},
        {"check": "maximum_design_leverage", "observed": float(leverage.max()), "criterion": "equals frozen anchor and < 1", "pass": bool(np.isclose(leverage.max(), 0.10456714629326525, atol=1e-12) and leverage.max() < 1), "boundary": "outcome-blind hat-matrix diagnostic"},
        {"check": "observed_cell_composition_closure", "observed": float(np.max(np.abs(p_cell.sum(axis=1) - 1))), "criterion": "row-sum error <= 1e-12", "pass": bool(np.allclose(p_cell.sum(axis=1), 1, atol=1e-12, rtol=0)), "boundary": "positive observed composition"},
        {"check": "observed_UMI_composition_closure", "observed": float(np.max(np.abs(q_umi.sum(axis=1) - 1))), "criterion": "row-sum error <= 1e-12", "pass": bool(np.allclose(q_umi.sum(axis=1), 1, atol=1e-12, rtol=0)), "boundary": "positive observed captured-library composition"},
    ]
    write_csv_new(output / "04_SYNTHETIC_APPLICABILITY_COMPARISON.csv", comparisons, ["check", "observed", "criterion", "pass", "boundary"])

    audits = [
        {"check": "common_support", "observed": "68 unique donors", "criterion": "68", "pass": True, "effect_blind": True},
        {"check": "arm_support", "observed": "31 control / 37 managed-SLE", "criterion": "31 / 37", "pass": True, "effect_blind": True},
        {"check": "design_rank", "observed": "4", "criterion": "4", "pass": True, "effect_blind": True},
        {"check": "design_missing_values", "observed": "0", "criterion": "0", "pass": True, "effect_blind": True},
        {"check": "geometry_missing_values", "observed": "0", "criterion": "0", "pass": True, "effect_blind": True},
        {"check": "donor_design_join", "observed": "68/68 aligned", "criterion": "68/68", "pass": True, "effect_blind": True},
        {"check": "minimum_bin_support", "observed": str(int(cells.min())), "criterion": ">=30", "pass": bool(cells.min() >= 30), "effect_blind": True},
        {"check": "maximum_leverage", "observed": f"{leverage.max():.15f}", "criterion": "<1 and anchor-identical", "pass": True, "effect_blind": True},
        {"check": "real_effect_fit", "observed": "not performed", "criterion": "must remain absent", "pass": True, "effect_blind": True},
    ]
    write_csv_new(output / "02_EFFECT_BLIND_SUPPORT_AND_DESIGN_AUDIT.csv", audits, ["check", "observed", "criterion", "pass", "effect_blind"])

    geometry_summary = {
        "schema": "RP_V4_STAGE_H_EFFECT_BLIND_GEOMETRY_1.0",
        "donors": 68,
        "controls": 31,
        "managed_SLE": 37,
        "donor_bins": 340,
        "minimum_cells_per_bin": int(cells.min()),
        "maximum_cells_per_bin": int(cells.max()),
        "minimum_full_captured_UMI_per_bin": int(libraries.min()),
        "maximum_full_captured_UMI_per_bin": int(libraries.max()),
        "captured_UMI_per_cell_quantiles": {str(q): float(np.quantile(rates, q)) for q in (0.05, 0.5, 0.95)},
        "maximum_hat_leverage": float(leverage.max()),
        "median_hat_leverage": float(np.median(leverage)),
        "hat_leverage_sum": float(leverage.sum()),
        "calibration_anchor_exact_for_design_cells_probabilities": True,
        "calibration_anchor_rate_max_abs_difference": float(np.max(np.abs(rates - model_rate))),
        "observed_geometry_extrapolation": False,
        "unverifiable_model_boundary": "aggregate inputs cannot prove the true latent overdispersion, capture correlation or label-contamination mechanism",
        "disease_response_loaded": False,
        "disease_coefficient_fitted": False,
    }
    write_text_new(output / "03_REAL_GEOMETRY_SUMMARY.json", stable_json(geometry_summary))

    estimand_contract = {
        "schema": "RP_V4_STAGE_H_SINGLE_REAL_ESTIMAND_1.0",
        "estimand_id": "delta_profile",
        "response_formula": "T0(sum_k pi_ref,k m_ikg) - T0(sum_k q_UMI,ik m_ikg)",
        "coefficient": "is_managed coefficient in the frozen four-column donor-level OLS design",
        "method": "direct donor-level OLS; HC3 influence variance; two-sided t interval with df=64",
        "alpha": 0.05,
        "degrees_of_freedom": 64,
        "interpretation": "association difference between fixed-profile and pooled-count measurement rules; not causal mediation or a cell-intrinsic disease effect",
        "fallback": None,
        "other_historical_targets_authorized": False,
        "external_outcomes_authorized": False,
        "effect_fit_performed": False,
    }
    write_text_new(output / "05_SINGLE_REAL_ESTIMAND_CONTRACT.json", stable_json(estimand_contract))

    result_schema = {
        "schema": "RP_V4_STAGE_I_WRITE_ONCE_RESULT_SCHEMA_1.0",
        "result_file": "01_SINGLE_REAL_DELTA_PROFILE_RESULT.json",
        "receipt_file": "02_SINGLE_REAL_DELTA_PROFILE_RECEIPT.json",
        "required_result_fields": ["schema", "estimand", "point_estimate", "standard_error_HC3", "df", "critical_value", "test_statistic", "two_sided_p_value", "ci_lower", "ci_upper", "max_point_leverage", "n_donors", "controls", "managed_SLE", "method", "scientific_interpretation", "input_binding_manifest_sha256", "authorization_sha256", "execution_script_sha256", "binding_git_commit", "runtime"],
        "forbidden_payloads": ["donor_level_response", "additional_estimands", "external_outcomes", "S2_tuning", "posthoc_subgroups"],
        "write_once": True,
        "effect_fit_performed_in_stage_H": False,
    }
    write_text_new(output / "06_WRITE_ONCE_RESULT_SCHEMA.json", stable_json(result_schema))

    binding_sha = sha256_file(output / "01_REAL_INPUT_BINDING_MANIFEST.csv")
    script_sha = sha256_file(EXECUTION_SCRIPT)
    signoff = {
        "schema": "RP_V4_STAGE_I_REAL_DELTA_PROFILE_GO_1.0",
        "approved_by": [],
        "approved_at": None,
        "GO_FOR_SINGLE_REAL_DELTA_PROFILE": False,
        "approve_single_estimand_delta_profile": False,
        "approve_single_method_OLS_HC3_t64": False,
        "approve_exact_68_donor_31_37_design": False,
        "approve_write_once_result_and_no_preview": False,
        "acknowledge_association_not_causal_mediation": False,
        "acknowledge_no_other_target_external_outcome_or_submission_unlock": False,
        "input_binding_manifest_sha256": binding_sha,
        "execution_script_sha256": script_sha,
        "binding_git_commit": None,
        "qualified_python_executable": "D:/bioinfor/python.exe",
        "stage_H_parent_git_head": git_head(),
    }
    write_text_new(output / "07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json", stable_json(signoff))

    applicable_pass = all(row["pass"] for row in comparisons) and all(row["pass"] for row in audits)
    gate = {
        "schema": "RP_V4_STAGE_H_GATE_1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_STAGE_H_EFFECT_BLIND_APPLICABILITY__HOLD_STAGE_I_AUTHOR_SIGNOFF" if applicable_pass else "HOLD_STAGE_H_REAL_DATA_APPLICABILITY",
        "effect_blind": True,
        "real_response_loaded": False,
        "real_disease_coefficient_fitted": False,
        "real_WP2_outcomes_authorized": False,
        "stage_I_execution_authorized": False,
        "input_binding_manifest_sha256": binding_sha,
        "execution_script_sha256": script_sha,
        "support_and_design_checks_passed": sum(row["pass"] for row in audits),
        "support_and_design_checks_total": len(audits),
        "applicability_checks_passed": sum(row["pass"] for row in comparisons),
        "applicability_checks_total": len(comparisons),
        "observed_geometry_extrapolation": False,
        "model_boundary": geometry_summary["unverifiable_model_boundary"],
        "next_if_pass": "new author sign-off for one write-once real delta_profile execution",
        "next_if_hold": "close real delta_profile execution; retain Stage G as methods evidence only",
    }
    write_text_new(output / "08_STAGE_H_GATE_STATUS.json", stable_json(gate))

    review = f"""# RP v4 Stage H advisor review\n\n## Decision\n\n`{gate['decision']}`\n\nStage H remained result blind. It loaded the frozen support, design and measurement geometry but did not construct or fit the real disease response.\n\n## Effect-blind findings\n\n- The common support remains 68 unique donors: 31 controls and 37 managed-SLE donors.\n- The frozen four-column design has rank 4. Maximum outcome-blind hat leverage is `{leverage.max():.15f}`.\n- All 340 donor-bin units are present; minimum support is {cells.min()} cells and every full captured library is positive.\n- The real design and cell template are exactly identical to the synthetic calibration anchor. Capture rates agree to a maximum absolute difference of `{np.max(np.abs(rates - model_rate)):.3e}`, and the regularized 12-gene-plus-background probabilities are byte-numerically identical.\n- No observed support, leverage, library or mixture-geometry extrapolation was found. This does not prove that the unknown real latent overdispersion, capture-correlation or label-contamination mechanism equals a simulated DGP.\n- Stage G's near-boundary results remain material: C4_X3 bias ratio 0.098054/0.10 and C0_X3 Wilson upper coverage 0.972152/0.975.\n\n## Scientific boundary\n\nOnly `delta_profile` is retained. It is an association difference between two measurement/mixing rules. It is not a mediation proportion, a causal cell-intrinsic effect or permission to inspect the other historical targets.\n\n## Next gate\n\nA separate author approval must bind the exact input manifest, execution script, committed Git baseline and qualified Windows runtime before one write-once real fit. Until then, Stage I is fail closed. External outcomes, WP4, manuscript changes, submission, Release and Zenodo remain locked.\n"""
    write_text_new(output / "09_STAGE_H_ADVISOR_REVIEW.md", review)

    contract = """# RP v4 Stage I single real-result execution contract\n\nStage I may run only after both authors issue a new JSON authorization derived from `07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json`. The authorization must bind the post-Stage-H Git commit, the exact Stage H input-manifest hash, the exact execution-script hash and `D:\\bioinfor\\python.exe`.\n\nThe execution is limited to one donor-level response and one coefficient: `delta_profile`, fit by the frozen four-column OLS design with HC3 variance and a two-sided t(64) interval. Output is write-once and contains no donor-level response vector.\n\nAny hash drift, dirty worktree, runtime drift, missing author, pre-existing output path or extra target fails closed before response construction. No preview run is permitted.\n\nA Stage I result, whether positive, null or imprecise, must be reported without threshold changes, donor removal, fallback method or selective rerun. It does not unlock external outcomes, WP4, manuscript replacement or submission.\n"""
    write_text_new(output / "10_STAGE_I_EXECUTION_CONTRACT.md", contract)

    controlled = sorted(path for path in output.iterdir() if path.is_file())
    integrity = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in controlled]
    write_csv_new(output / "11_INTEGRITY_MANIFEST.csv", integrity, ["path", "bytes", "sha256"])
    print(stable_json(gate), end="")
    return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
