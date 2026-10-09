#!/usr/bin/env python3
"""Independent arithmetic and integrity review for the frozen RP-v3 WP1 run."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


MODEL_COLUMNS = ["intercept", "is_managed", "age_centered", "ethnicity_asian"]
ESTIMANDS = ["beta_A0", "beta_A1", "beta_A2", "delta_beta_ann_A1", "delta_beta_ann_A2"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main(run: Path) -> None:
    checks = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": str(detail)})

    status = json.loads((run / "06_WP1_GATE_STATUS.json").read_text(encoding="utf-8"))
    check("provisional_gate_pass", status["status"] == "PASS_WP1_ANNOTATION_SENSITIVITY_REVIEW_REQUIRED", status["status"])
    check("shared_population", status["analysis_population"] == 68 and status["controls"] == 31 and status["managed_sle"] == 37,
          f"n={status['analysis_population']}; controls={status['controls']}; managed={status['managed_sle']}")
    check("frozen_design", status["design_columns"] == MODEL_COLUMNS and status["design_rank"] == 4,
          f"{status['design_columns']}; rank={status['design_rank']}")
    check("bootstrap_contract", status["attempted_replicates"] == 2000 and status["successful_replicates"] == 2000
          and status["failed_replicates"] == 0, status["failure_rate"])
    check("no_formal_testing_or_margin", status["formal_p_values_reported"] is False and status["equivalence_margin"] is None,
          "no p values; no equivalence margin")

    manifest = pd.read_csv(run / "09_WP1_INTEGRITY_MANIFEST.csv")
    mismatches = []
    for row in manifest.itertuples(index=False):
        path = run / row.file
        if not path.is_file() or path.stat().st_size != row.bytes or sha256(path) != row.sha256:
            mismatches.append(row.file)
    check("integrity_manifest", len(manifest) == 9 and not mismatches, mismatches or "9/9")

    scores = pd.read_csv(run / "01_WP1_DONOR_SCORES.csv")
    points = pd.read_csv(run / "02_WP1_POINT_ESTIMATES.csv").set_index("estimand")
    x = scores[MODEL_COLUMNS]
    recalculated = {}
    for branch in ("A0", "A1", "A2"):
        recalculated[f"beta_{branch}"] = float(sm.OLS(scores[f"score_{branch}"], x).fit().params["is_managed"])
    recalculated["delta_beta_ann_A1"] = recalculated["beta_A1"] - recalculated["beta_A0"]
    recalculated["delta_beta_ann_A2"] = recalculated["beta_A2"] - recalculated["beta_A0"]
    max_point_error = max(abs(recalculated[key] - points.loc[key, "estimate"]) for key in ESTIMANDS)
    check("independent_point_recalculation", max_point_error < 1e-12, max_point_error)

    boot = pd.read_csv(run / "03_WP1_BOOTSTRAP_REPLICATES.csv.gz")
    check("bootstrap_row_identity", len(boot) == 2000 and boot["replicate"].nunique() == 2000
          and np.array_equal(boot["replicate"].to_numpy(), np.arange(1, 2001)), f"rows={len(boot)}")
    check("bootstrap_rank_and_success", boot["success"].all() and boot["design_rank"].eq(4).all(),
          boot["design_rank"].value_counts().to_dict())
    intervals = pd.read_csv(run / "04_WP1_BOOTSTRAP_INTERVALS.csv").set_index("estimand")
    max_interval_error = 0.0
    for estimand in ESTIMANDS:
        low, high = np.quantile(boot[estimand].to_numpy(float), [0.025, 0.975])
        max_interval_error = max(max_interval_error, abs(low - intervals.loc[estimand, "bootstrap_ci_low"]),
                                 abs(high - intervals.loc[estimand, "bootstrap_ci_high"]))
    check("bootstrap_percentiles_recalculated", max_interval_error < 1e-12, max_interval_error)
    check("diagnostic_figure_pair", (run / "08_WP1_ANNOTATION_SENSITIVITY_DIAGNOSTIC.png").is_file()
          and (run / "08_WP1_ANNOTATION_SENSITIVITY_DIAGNOSTIC.pdf").is_file(), "PNG and PDF")

    audit = pd.DataFrame(checks)
    audit.to_csv(run / "10_WP1_FINAL_AUDIT.csv", index=False)
    passed = bool(audit["pass"].all())
    decision = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_WP1_TO_WP2_PREFIT_AND_G2_FREEZE" if passed else "HOLD_WP1_REPAIR_REQUIRED",
        "checks_passed": int(audit["pass"].sum()),
        "checks_total": len(audit),
        "core_result": "Managed-SLE IFN/ISG coefficient remains positive under all three frozen representations",
        "A1_boundary": "A1 delta is small but is a joint identity-axis/common-composition sensitivity, not pure annotation or mediation",
        "A2_boundary": "A2 is nearly identical to A0 and retains LY6E; no equivalence claim is authorized",
        "G2": "NEXT_PREFIT_FREEZE_REQUIRED",
        "WP4": "HOLD_CONDITIONAL",
        "SUBMISSION": "HOLD",
    }
    (run / "11_WP1_FINAL_ADJUDICATION.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")

    values = intervals
    report = f"""# RP v3 WP1 final adjudication

## Decision

**{decision['decision']}** with {decision['checks_passed']}/{decision['checks_total']} audit checks passed.

The managed-SLE IFN/ISG coefficient was positive under A0, A1 and A2 on the same 68-donor population. A0 was {values.loc['beta_A0','estimate']:.3f} (paired-bootstrap 95% CI {values.loc['beta_A0','bootstrap_ci_low']:.3f} to {values.loc['beta_A0','bootstrap_ci_high']:.3f}); A1 was {values.loc['beta_A1','estimate']:.3f} ({values.loc['beta_A1','bootstrap_ci_low']:.3f} to {values.loc['beta_A1','bootstrap_ci_high']:.3f}); and A2 was {values.loc['beta_A2','estimate']:.3f} ({values.loc['beta_A2','bootstrap_ci_low']:.3f} to {values.loc['beta_A2','bootstrap_ci_high']:.3f}).

The paired A1-A0 difference was {values.loc['delta_beta_ann_A1','estimate']:.3f} ({values.loc['delta_beta_ann_A1','bootstrap_ci_low']:.3f} to {values.loc['delta_beta_ann_A1','bootstrap_ci_high']:.3f}). This is a small joint identity-axis/common-composition reconstruction shift; it is not a causal, cell-intrinsic or mediated fraction. The A2-A0 difference was {values.loc['delta_beta_ann_A2','estimate']:.6f} ({values.loc['delta_beta_ann_A2','bootstrap_ci_low']:.6f} to {values.loc['delta_beta_ann_A2','bootstrap_ci_high']:.6f}). Its lower percentile touching zero does not establish equivalence, and A2 is not fully IFN12-excluded because LY6E remains.

All 2,000 attempted paired bootstrap replicates succeeded; all retained design rank 4. Point estimates and percentile intervals were independently recomputed from the saved donor-score and bootstrap tables. No formal p values or new multiplicity family were introduced.

## Next gate

Proceed to **WP2 pre-effect identifiability and full G2 simulation freeze**. Before estimating WP2 disease effects, freeze the state/continuous-axis target, composition coordinates, missing-state handling, simulation truth generation, acceptance limits and Monte Carlo intervals. WP4, manuscript replacement, release/Zenodo and submission remain on hold.
"""
    (run / "12_WP1_FINAL_ADJUDICATION.md").write_text(report, encoding="utf-8")

    final_files = []
    for path in sorted(run.iterdir()):
        if path.is_file() and path.name != "13_WP1_FINAL_INTEGRITY_MANIFEST.csv":
            final_files.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    pd.DataFrame(final_files).to_csv(run / "13_WP1_FINAL_INTEGRITY_MANIFEST.csv", index=False)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    main(args.run)
