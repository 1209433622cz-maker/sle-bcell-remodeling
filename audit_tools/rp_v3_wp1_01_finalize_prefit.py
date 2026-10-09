#!/usr/bin/env python3
"""Freeze the RP-v3 WP1 pre-effect contract without fitting disease effects."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]
BOOTSTRAP_SEED = 20261010
BOOTSTRAP_REPLICATES = 2000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def matrix_rank_elimination(values: np.ndarray, tolerance: float = 1e-10) -> int:
    matrix = np.asarray(values, dtype=float).copy()
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError("Design matrix must be finite and two-dimensional")
    rank = 0
    for column in range(matrix.shape[1]):
        if rank >= matrix.shape[0]:
            break
        pivot = rank + int(np.argmax(np.abs(matrix[rank:, column])))
        if abs(matrix[pivot, column]) <= tolerance:
            continue
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        matrix[rank] /= matrix[rank, column]
        for row in range(matrix.shape[0]):
            if row != rank:
                matrix[row] -= matrix[row, column] * matrix[rank]
        rank += 1
    return rank


def main(prefit: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Use a new output directory: {output}")
    output.mkdir(parents=True)

    status = json.loads((prefit / "STATUS.json").read_text(encoding="utf-8"))
    if status.get("status") != "PREFIT_EXPORT_COMPLETE_REVIEW_REQUIRED":
        raise ValueError("The disease-blind prefit export is incomplete")
    if status.get("disease_coefficients_fitted") is not False:
        raise ValueError("Prefit export unexpectedly reports fitted disease coefficients")

    support = pd.read_csv(prefit / "candidate_joint_support.csv", dtype={"donor_id": str})
    design = pd.read_csv(prefit / "primary_design_fixed.csv", dtype={"donor_id": str})
    shared = support.loc[
        support["candidate_common_if_A2_ge50_adopted"].astype(bool),
        ["stratum_id", "donor_id", "is_managed", "A0_ge50", "A1_all_five_ge30", "A2_ge50_diagnostic"],
    ].copy()
    shared = shared.merge(
        design[["stratum_id", "donor_id"] + MODEL_COLUMNS],
        on=["stratum_id", "donor_id"],
        validate="one_to_one",
        suffixes=("_support", ""),
    )
    if "is_managed_support" in shared:
        if not np.array_equal(shared["is_managed_support"].to_numpy(), shared["is_managed"].to_numpy()):
            raise ValueError("Disease-arm fields disagree between support and frozen design")
        shared = shared.drop(columns="is_managed_support")
    if len(shared) != 68 or shared["donor_id"].nunique() != 68:
        raise ValueError("Expected 68 unique complete-case donors")
    arm_counts = shared.groupby("is_managed")["donor_id"].nunique().to_dict()
    if arm_counts != {0: 31, 1: 37}:
        raise ValueError(f"Unexpected shared-support arm counts: {arm_counts}")
    if shared[MODEL_COLUMNS].isna().any().any():
        raise ValueError("Missing frozen covariates in the shared support set")
    rank = matrix_rank_elimination(shared[MODEL_COLUMNS].to_numpy(float))
    if rank != len(MODEL_COLUMNS):
        raise ValueError(f"Frozen primary design is rank deficient: {rank}/{len(MODEL_COLUMNS)}")
    if not shared[["A0_ge50", "A1_all_five_ge30", "A2_ge50_diagnostic"]].all().all():
        raise ValueError("The shared set violates a frozen support rule")

    mapping = pd.read_csv(prefit / "A2_to_A0_overlap_mapping.csv", dtype={"A2_cluster": str})
    if mapping["mapped_A0_broad"].nunique() != 2:
        raise ValueError("A2 overlap mapping does not retain both broad compartments")
    if mapping["cluster_purity_vs_A0"].min() <= 0.5:
        raise ValueError("A2 mapping contains a tied or non-majority cluster")

    shared_path = output / "02_SHARED_ANALYSIS_SET.csv"
    design_path = output / "03_SHARED_DESIGN_MATRIX.csv"
    shared.to_csv(shared_path, index=False)
    shared[["stratum_id", "donor_id"] + MODEL_COLUMNS].to_csv(design_path, index=False)

    prefit_zip = prefit.with_suffix(".zip")
    source_manifest = prefit / "SHA256SUMS.csv"
    completion = {
        "status": "PASS_WP1_PREFIT_UNLOCK",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "disease_coefficients_fitted": False,
        "A1_operator_and_target": (
            "expression reconstruction on linear CPM: sum_k(pi_ref_k * CPM_ikg), "
            "then identical frozen T0 log2(CPM+0.5) and 43-control z standardization"
        ),
        "A1_delta_semantic_label": "joint identity-axis/common-composition standardization sensitivity",
        "A2_feature_scope": "historical strong-ISG-list exclusion; LY6E retained",
        "A2_overlap_mapping_hash": sha256(prefit / "A2_to_A0_overlap_mapping.csv"),
        "A2_support_rule": "at least 50 mapped A2 B_CONV cells per donor stratum",
        "shared_donors": 68,
        "shared_donors_by_is_managed": {str(k): int(v) for k, v in arm_counts.items()},
        "shared_donor_ID_hash": sha256(shared_path),
        "shared_covariate_matrix_hash": sha256(design_path),
        "shared_covariate_matrix_rank": rank,
        "model_columns": MODEL_COLUMNS,
        "T0_reference_hash": sha256(prefit / "11_T0_FROZEN_REFERENCE_PARAMETERS.csv"),
        "pi_ref_hash": sha256(prefit / "09_PI_REF.csv"),
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "attempted_replicates": BOOTSTRAP_REPLICATES,
            "sampling": "case-control-stratified donor bootstrap with replacement; one shared draw for A0/A1/A2",
            "duplicate_handling": "expanded replicate rows; each sampled donor occurrence contributes once",
            "interval": "paired percentile 95% interval from successful replicates",
            "failures": "non-finite input/output, missing arm, or design rank <4; every attempt counts; no replenishment",
            "stop_rule": "HOLD when failures exceed 1% of 2,000 attempted replicates",
            "conditioning": "A2 mapping, A1 cutpoints, pi_ref, T0 and the 68-donor support set remain fixed",
        },
        "sufficient_count_manifest_hash": sha256(source_manifest),
        "sufficient_count_archive_hash": sha256(prefit_zip) if prefit_zip.is_file() else None,
        "first_effect_fit_time": "NOT_STARTED",
        "G2": "NOT_ASSESSED_FULL_PROTOCOL_PENDING",
        "WP4": "HOLD_CONDITIONAL",
        "SUBMISSION": "HOLD",
    }
    status_path = output / "04_PREFIT_GATE_STATUS.json"
    status_path.write_text(json.dumps(completion, indent=2), encoding="utf-8")

    inputs = []
    for path in sorted(prefit.iterdir()):
        if path.is_file():
            inputs.append({"relative_path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    pd.DataFrame(inputs).to_csv(output / "05_PREFIT_INPUT_HASHES.csv", index=False)

    text = f"""# WP1 pre-effect execution addendum - final freeze

Date: 2026-10-10
Status: **PASS_WP1_PREFIT_UNLOCK**
Disease coefficients inspected while preparing this addendum: **No**

## Frozen analysis population and design

- One shared complete-case population is used for A0, A1 and A2: **68 unique donors**.
- Arm support is **31 controls** and **37 managed-SLE donors**.
- A0 requires at least 50 historical B_CONV cells; A1 requires all five bins to contain at least 30 cells; A2 requires at least 50 mapped B_CONV cells.
- The frozen primary design is `intercept + is_managed + age_centered + ethnicity_asian`; observed rank is **4/4**.
- The original 43-control T0 reference is retained. T0 is not recomputed on the reduced analysis set.

## A1 operator and estimand

For donor `i`, bin `k` and gene `g`, raw counts are divided by the full-bin raw library total to obtain linear CPM. The common-composition expression is

`CPM_A1_ig = sum_k pi_ref_k * CPM_ikg`.

The identical frozen transform is then applied:

`T0_A1_ig = [log2(CPM_A1_ig + 0.5) - mu0_g] / sd0_g`,

followed by the mean over the 12 frozen IFN/ISG genes. This is expression reconstruction before transformation. It is not the average of logged bin scores. `delta_beta_ann_A1` is therefore labelled a **joint identity-axis/common-composition standardization sensitivity**, not a pure annotation effect or causal mediation quantity.

## A2 semantics and mapping

- A2 is the frozen historical strong-ISG-list-excluded representation; it retains `LY6E` from the 12-gene program.
- A2 clusters were mapped to A0 broad compartments by disease-blind cell overlap before the disease design was read.
- Mapping retained B_CONV and B_ASC with no ties or class collapse. Minimum cluster purity versus A0 was **{mapping['cluster_purity_vs_A0'].min():.6f}**; this is agreement to a reference scaffold, not biological accuracy.

## Bootstrap contract

- Seed: `{BOOTSTRAP_SEED}`.
- Exactly `{BOOTSTRAP_REPLICATES}` attempted replicates; no replacement of failed attempts.
- Sampling is stratified by `is_managed`, with replacement within the 31-control and 37-SLE arms.
- A single shared donor draw is applied to all three branches and both paired deltas.
- Duplicate donors are represented by repeated rows in that replicate.
- Primary intervals are 2.5th and 97.5th percentiles over successful paired replicates.
- A replicate fails for a missing arm, non-finite values or design rank below 4.
- WP1 is held if more than 1% of attempted replicates fail.
- A2 mapping, A1 cutpoints, `pi_ref`, T0 and the 68-donor support set are conditioned on and are not rebuilt inside the bootstrap.

## Boundaries

No equivalence margin, p-value family, causal interpretation, manuscript replacement, WP4 unlock, GitHub release, Zenodo update or submission action is authorized by this gate. G2 remains unassessed until full simulations match the final operator and missingness procedure.

## Frozen hashes

- Shared analysis set: `{completion['shared_donor_ID_hash']}`
- Shared design matrix: `{completion['shared_covariate_matrix_hash']}`
- A2 overlap mapping: `{completion['A2_overlap_mapping_hash']}`
- T0 reference: `{completion['T0_reference_hash']}`
- `pi_ref`: `{completion['pi_ref_hash']}`
- Sufficient-count manifest: `{completion['sufficient_count_manifest_hash']}`
"""
    (output / "01_WP1_PREFIT_EXECUTION_ADDENDUM_FINAL.md").write_text(text, encoding="utf-8")
    print(json.dumps(completion, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    main(args.prefit, args.output)
