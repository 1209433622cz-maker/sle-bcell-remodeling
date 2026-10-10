#!/usr/bin/env python3
"""Authorized write-once execution of the single real RP v4 delta_profile result."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import statsmodels
from scipy.stats import t

try:
    from .rp_v3_g2b_studentized import weighted_hc3
except ImportError:
    from rp_v3_g2b_studentized import weighted_hc3


ROOT = Path(__file__).resolve().parents[1]
MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]
EXPECTED_AUTHORS = ["Zhi Chen", "Teng Qi"]
EXPECTED_PYTHON = Path(r"D:\bioinfor\python.exe")
RESULT_NAME = "01_SINGLE_REAL_DELTA_PROFILE_RESULT.json"
RECEIPT_NAME = "02_SINGLE_REAL_DELTA_PROFILE_RECEIPT.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def atomic_write_new(path: Path, content: str) -> None:
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Refusing overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    if partial.exists():
        raise RuntimeError(f"Unclean partial file: {partial}")
    with partial.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    os.replace(partial, path)


def read_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def git_head() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def require_clean_worktree() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        raise PermissionError("Stage I requires a completely clean Git worktree")


def runtime_identity() -> dict:
    executable = Path(sys.executable).resolve()
    return {
        "python_executable": str(executable),
        "python_executable_sha256": sha256_file(executable),
        "python_version": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
    }


def verify_authorization(authorization_path: Path, binding_manifest: Path) -> dict:
    authorization = read_json(authorization_path)
    required_true = [
        "GO_FOR_SINGLE_REAL_DELTA_PROFILE",
        "approve_single_estimand_delta_profile",
        "approve_single_method_OLS_HC3_t64",
        "approve_exact_68_donor_31_37_design",
        "approve_write_once_result_and_no_preview",
        "acknowledge_association_not_causal_mediation",
        "acknowledge_no_other_target_external_outcome_or_submission_unlock",
    ]
    if authorization.get("schema") != "RP_V4_STAGE_I_REAL_DELTA_PROFILE_GO_1.0":
        raise PermissionError("Wrong or absent Stage I authorization schema")
    if authorization.get("approved_by") != EXPECTED_AUTHORS or not authorization.get("approved_at"):
        raise PermissionError("Both frozen authors have not approved Stage I")
    if any(authorization.get(field) is not True for field in required_true):
        raise PermissionError("Stage I approval is incomplete")
    if authorization.get("input_binding_manifest_sha256") != sha256_file(binding_manifest):
        raise PermissionError("Authorization does not bind the Stage H input manifest")
    if authorization.get("execution_script_sha256") != sha256_file(Path(__file__).resolve()):
        raise PermissionError("Authorization does not bind this execution script")
    if authorization.get("binding_git_commit") != git_head():
        raise PermissionError("Authorization does not bind current Git HEAD")
    if Path(sys.executable).resolve() != EXPECTED_PYTHON.resolve():
        raise PermissionError("Stage I must use D:\\bioinfor\\python.exe")
    if str(authorization.get("qualified_python_executable", "")).replace("/", "\\").casefold() != str(EXPECTED_PYTHON).casefold():
        raise PermissionError("Authorization names a different Python executable")
    require_clean_worktree()
    return authorization


def verify_binding_manifest(path: Path) -> dict[str, Path]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or set(rows[0]) != {"path", "bytes", "sha256", "role"}:
        raise ValueError("Invalid Stage H binding manifest")
    resolved: dict[str, Path] = {}
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe binding path")
        source = (ROOT / relative).resolve()
        if not source.is_file() or source.stat().st_size != int(row["bytes"]) or sha256_file(source) != row["sha256"]:
            raise ValueError(f"Bound input drift: {relative.as_posix()}")
        resolved[relative.name] = source
    required = {
        "02_SHARED_ANALYSIS_SET.csv",
        "03_SHARED_DESIGN_MATRIX.csv",
        "A1_bin_sufficient_raw_counts.csv",
        "09_PI_REF.csv",
        "11_T0_FROZEN_REFERENCE_PARAMETERS.csv",
        "02_G2_CALIBRATION_MODEL.json",
        "04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json",
        "11_FINAL_SYNTHETIC_GATE.json",
    }
    missing = required.difference(resolved)
    if missing:
        raise ValueError(f"Stage H binding manifest is incomplete: {sorted(missing)}")
    return resolved


def construct_single_response(paths: dict[str, Path]) -> tuple[np.ndarray, np.ndarray]:
    shared = pd.read_csv(paths["02_SHARED_ANALYSIS_SET.csv"], dtype={"donor_id": str})
    design_frame = pd.read_csv(paths["03_SHARED_DESIGN_MATRIX.csv"], dtype={"donor_id": str})
    if len(shared) != 68 or shared["stratum_id"].nunique() != 68:
        raise ValueError("Frozen support changed")
    design_frame = design_frame.set_index("stratum_id").loc[shared["stratum_id"]].reset_index()
    if not design_frame["donor_id"].equals(shared["donor_id"]):
        raise ValueError("Frozen design alignment changed")
    design = design_frame[MODEL_COLUMNS].to_numpy(float)
    if design.shape != (68, 4) or not np.isfinite(design).all():
        raise ValueError("Invalid frozen design")
    if design_frame["is_managed"].value_counts().to_dict() != {1: 37, 0: 31}:
        raise ValueError("Frozen arm support changed")

    model = read_json(paths["02_G2_CALIBRATION_MODEL.json"])
    genes = list(model["gene_order"])
    t0 = pd.read_csv(paths["11_T0_FROZEN_REFERENCE_PARAMETERS.csv"])
    if t0["gene_symbol"].astype(str).tolist() != genes or not t0["reference_strata"].eq(43).all():
        raise ValueError("Frozen T0 reference changed")
    means = t0["control_mean_log2_cpm_plus_0_5"].to_numpy(float)
    sds = t0["control_population_sd_log2_cpm_plus_0_5"].to_numpy(float)
    if (sds <= 0).any():
        raise ValueError("Invalid T0 standard deviations")
    pi = pd.read_csv(paths["09_PI_REF.csv"]).sort_values("a1_bin")["pi_ref"].to_numpy(float)
    if not np.allclose(pi, np.asarray(model["pi"], float), atol=1e-15, rtol=0):
        raise ValueError("Fixed-profile weights changed")

    order = pd.MultiIndex.from_product([shared["stratum_id"], range(1, 6)], names=["stratum_id", "A1_bin"])
    raw = pd.read_csv(paths["A1_bin_sufficient_raw_counts.csv"], dtype={"donor_id": str})
    raw = raw.set_index(["stratum_id", "A1_bin"]).loc[order].reset_index()
    counts = raw[[f"raw_IFN_{gene}" for gene in genes]].to_numpy(float).reshape(68, 5, 12)
    libraries = raw["full_raw_library_total"].to_numpy(float).reshape(68, 5)
    cells = raw["cell_count"].to_numpy(float).reshape(68, 5)
    if not np.array_equal(cells, np.asarray(model["template_n"], float)) or (libraries <= 0).any():
        raise ValueError("Bound support no longer matches calibrated input")
    bin_cpm = counts * 1e6 / libraries[:, :, None]
    profile_cpm = np.einsum("k,ikg->ig", pi, bin_cpm)
    pooled_cpm = counts.sum(axis=1) * 1e6 / libraries.sum(axis=1)[:, None]
    profile_score = np.mean((np.log2(profile_cpm + 0.5) - means) / sds, axis=1)
    pooled_score = np.mean((np.log2(pooled_cpm + 0.5) - means) / sds, axis=1)
    response = profile_score - pooled_score
    if response.shape != (68,) or not np.isfinite(response).all():
        raise ValueError("Single real response construction failed")
    return design, response


def execute(authorization_path: Path, binding_manifest: Path, output: Path) -> dict:
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Stage I output must not already exist")
    authorization = verify_authorization(authorization_path, binding_manifest)
    paths = verify_binding_manifest(binding_manifest)
    design, response = construct_single_response(paths)
    coefficient, standard_error, valid, leverage = weighted_hc3(
        design, response[:, None], np.ones((1, 68), dtype=float)
    )
    if not valid[0]:
        raise ValueError("Frozen HC3 fit failed")
    point = float(coefficient[0, 0])
    se = float(standard_error[0, 0])
    df = 64
    critical = float(t.ppf(0.975, df))
    statistic = point / se
    p_value = float(2 * t.sf(abs(statistic), df))
    runtime = runtime_identity()
    result = {
        "schema": "RP_V4_STAGE_I_SINGLE_REAL_DELTA_PROFILE_RESULT_1.0",
        "estimand": "delta_profile",
        "point_estimate": point,
        "standard_error_HC3": se,
        "df": df,
        "critical_value": critical,
        "test_statistic": statistic,
        "two_sided_p_value": p_value,
        "ci_lower": point - critical * se,
        "ci_upper": point + critical * se,
        "max_point_leverage": float(leverage[0]),
        "n_donors": 68,
        "controls": 31,
        "managed_SLE": 37,
        "method": "direct donor-level OLS delta_profile; HC3 influence variance; two-sided t(64) interval",
        "scientific_interpretation": "association difference between fixed-profile and pooled-count measurement rules; not causal mediation or a cell-intrinsic disease effect",
        "input_binding_manifest_sha256": sha256_file(binding_manifest),
        "authorization_sha256": sha256_file(authorization_path),
        "execution_script_sha256": sha256_file(Path(__file__).resolve()),
        "binding_git_commit": git_head(),
        "runtime": runtime,
        "other_historical_targets_fitted": False,
        "external_outcomes_fitted": False,
        "automatic_manuscript_or_submission_unlock": False,
    }
    output.mkdir(parents=True)
    result_path = output / RESULT_NAME
    atomic_write_new(result_path, stable_json(result))
    receipt = {
        "schema": "RP_V4_STAGE_I_SINGLE_REAL_RESULT_RECEIPT_1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result_path": RESULT_NAME,
        "result_bytes": result_path.stat().st_size,
        "result_sha256": sha256_file(result_path),
        "authorization_sha256": sha256_file(authorization_path),
        "input_binding_manifest_sha256": sha256_file(binding_manifest),
        "write_once": True,
        "single_estimand_only": True,
        "donor_level_response_exported": False,
    }
    atomic_write_new(output / RECEIPT_NAME, stable_json(receipt))
    print(stable_json(receipt), end="")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--binding-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    execute(args.authorization, args.binding_manifest, args.output)


if __name__ == "__main__":
    main()
