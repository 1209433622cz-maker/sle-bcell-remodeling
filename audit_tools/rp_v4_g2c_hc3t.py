"""RP v4 G2C synthetic-only influence-function interval kernel.

The sole registered estimand is ``delta_profile``.  Its donor-level response is
the frozen fixed-profile score minus the pooled score.  The point estimator is
the disease coefficient from the unchanged four-column OLS design.  Inference
uses the HC3 influence-function variance and a two-sided Student-t critical
value with n-p=64 degrees of freedom.

This module is deliberately incapable of accepting real WP2 responses.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.stats import t

try:
    from .rp_v3_g2_estimation import TARGETS
    from .rp_v3_g2b_studentized import weighted_hc3
except ImportError:  # Direct script execution from audit_tools/.
    from rp_v3_g2_estimation import TARGETS
    from rp_v3_g2b_studentized import weighted_hc3


REPO_ROOT = Path(__file__).resolve().parents[1]
PARENT_ESTIMATOR = REPO_ROOT / "audit_tools" / "rp_v3_g2_estimation.py"
EXPECTED_PARENT_SHA256 = (
    "0973b83fca955fa76d1d9fb47cd8792138ea7ff3b9c2dce1b873f6931b3f6b40"
)
ESTIMAND = "delta_profile"
TARGET_INDEX = TARGETS.index(ESTIMAND)
N_DONORS = 68
N_PARAMETERS = 4
DF = N_DONORS - N_PARAMETERS
ALPHA = 0.05
CRITICAL_VALUE = float(t.ppf(1.0 - ALPHA / 2.0, DF))
METHOD = "direct donor-level OLS delta_profile; HC3 influence variance; t(64) interval"


if hashlib.sha256(PARENT_ESTIMATOR.read_bytes()).hexdigest() != EXPECTED_PARENT_SHA256:
    raise RuntimeError("Frozen parent G2 estimator hash mismatch")


def interval(X: np.ndarray, Y: np.ndarray, *, data_kind: str | None = None) -> dict:
    """Return the single registered G2C interval and auditable diagnostics."""
    if data_kind != "SIMULATED_ONLY":
        raise PermissionError("Real WP2 responses remain locked")
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.shape != (N_DONORS, N_PARAMETERS) or Y.shape != (N_DONORS, len(TARGETS)):
        raise ValueError("Changed frozen dimensions")
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("Nonfinite design or response")
    if not np.all(X[:, 0] == 1) or np.sum(X[:, 1] == 0) != 31 or np.sum(X[:, 1] == 1) != 37:
        raise ValueError("Changed fixed 31/37 donor design")

    coefficients, standard_errors, valid, leverage = weighted_hc3(
        X, Y, np.ones((1, N_DONORS), dtype=float)
    )
    if not valid[0]:
        raise ValueError("Invalid HC3 point fit or studentizer")
    point = float(coefficients[0, TARGET_INDEX])
    standard_error = float(standard_errors[0, TARGET_INDEX])
    half_width = CRITICAL_VALUE * standard_error
    return {
        "estimand": ESTIMAND,
        "point": point,
        "standard_error_HC3": standard_error,
        "df": DF,
        "critical_value": CRITICAL_VALUE,
        "ci_lower": point - half_width,
        "ci_upper": point + half_width,
        "max_point_leverage": float(leverage[0]),
        "method": METHOD,
        "data_kind": "SIMULATED_ONLY",
        "G2C_PASS": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
    }

