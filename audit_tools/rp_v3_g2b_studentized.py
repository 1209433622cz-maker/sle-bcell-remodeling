"""Synthetic-only RP v3 G2B interval kernel.

The point estimator, response construction and paired donor resampling are
unchanged from G2. G2B replaces only the percentile interval with an
equal-tailed bootstrap-t interval using an HC3 studentizer. Real WP2 responses
are rejected and no result from this module can unlock them.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

try:
    from . import rp_v3_g2_estimation as parent
except ImportError:  # Direct script execution from audit_tools/.
    import rp_v3_g2_estimation as parent


REPO_ROOT = Path(__file__).resolve().parents[1]
PARENT_ESTIMATOR = REPO_ROOT / "audit_tools" / "rp_v3_g2_estimation.py"
EXPECTED_PARENT_SHA256 = "0973b83fca955fa76d1d9fb47cd8792138ea7ff3b9c2dce1b873f6931b3f6b40"
LEVERAGE_EPS = 1e-10
SE_EPS = 1e-12
ATTEMPTS = 2000
INTERVAL_METHOD = "equal-tailed paired donor bootstrap-t with HC3 studentizer"


if hashlib.sha256(PARENT_ESTIMATOR.read_bytes()).hexdigest() != EXPECTED_PARENT_SHA256:
    raise RuntimeError("Frozen parent G2 estimator hash mismatch")


def weighted_hc3(
    X: np.ndarray, Y: np.ndarray, weights: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fit weighted OLS and HC3 as explicit frequency-expanded bootstrap rows."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if (
        X.ndim != 2
        or X.shape[1] != 4
        or Y.ndim != 2
        or len(Y) != len(X)
        or weights.ndim != 2
        or weights.shape[1] != len(X)
    ):
        raise ValueError("Shape mismatch")
    if not all(np.isfinite(value).all() for value in (X, Y, weights)):
        raise ValueError("Inputs must be finite")
    if (weights < 0).any() or not np.equal(weights, np.floor(weights)).all():
        raise ValueError("Bootstrap frequency weights must be nonnegative integers")
    if (weights.sum(axis=1) <= X.shape[1]).any():
        raise ValueError("Insufficient expanded rows")

    scale = np.maximum(np.max(np.abs(X), axis=0), 1.0)
    scaled_X = X / scale
    batch = len(weights)
    targets = Y.shape[1]
    crossprod = np.empty((batch, 4, 4))
    right = np.empty((batch, 4, targets + 4))
    for j in range(4):
        for k in range(4):
            crossprod[:, j, k] = weights @ (scaled_X[:, j] * scaled_X[:, k])
        right[:, j, :targets] = weights @ (scaled_X[:, j, None] * Y)
    right[:, :, targets:] = np.eye(4)

    solved, valid = parent.solve_batch(crossprod, right)
    coefficients = solved[:, :, :targets]
    inverse = solved[:, :, targets:]
    leverage = np.einsum("ni,bij,nj->bn", scaled_X, inverse, scaled_X, optimize=True)
    active = weights > 0
    max_leverage = np.max(np.where(active, leverage, -np.inf), axis=1)
    valid &= np.all((~active) | (leverage < 1.0 - LEVERAGE_EPS), axis=1)

    disease_influence = (
        np.einsum("ni,bi->bn", scaled_X, inverse[:, :, 1], optimize=True) / scale[1]
    )
    residual = Y[None, :, :] - np.einsum(
        "ni,bij->bnj", scaled_X, coefficients, optimize=True
    )
    denominator = np.where(active, 1.0 - leverage, 1.0)
    meat_weight = weights * (disease_influence / denominator) ** 2
    variance = np.einsum("bn,bnj->bj", meat_weight, residual**2, optimize=True)
    standard_error = np.sqrt(np.maximum(variance, 0.0))
    disease_coefficient = coefficients[:, 1, :] / scale[1]
    valid &= (
        np.isfinite(disease_coefficient).all(axis=1)
        & np.isfinite(standard_error).all(axis=1)
        & (standard_error > SE_EPS).all(axis=1)
    )
    disease_coefficient[~valid] = np.nan
    standard_error[~valid] = np.nan
    return disease_coefficient, standard_error, valid, max_leverage


def validate_indices(X: np.ndarray, indices: np.ndarray) -> np.ndarray:
    indices = np.asarray(indices)
    if (
        indices.shape != (ATTEMPTS, 68)
        or indices.dtype.kind not in "iu"
        or (indices < 0).any()
        or (indices >= 68).any()
    ):
        raise ValueError("Invalid bootstrap index matrix")
    if not (np.sum(X[indices, 1] == 0, axis=1) == 31).all():
        raise ValueError("Changed control-arm bootstrap size")
    if not (np.sum(X[indices, 1] == 1, axis=1) == 37).all():
        raise ValueError("Changed SLE-arm bootstrap size")
    return indices


def paired_studentized(
    X: np.ndarray,
    Y: np.ndarray,
    rng: np.random.Generator | None = None,
    *,
    data_kind: str | None = None,
    indices: np.ndarray | None = None,
    attempts: int = ATTEMPTS,
) -> dict:
    """Return the frozen paired bootstrap-t interval for all ten targets."""
    if data_kind != "SIMULATED_ONLY":
        raise PermissionError("Real WP2 responses remain locked")
    if attempts != ATTEMPTS:
        raise ValueError("Exactly 2000 inner attempts are required")
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if X.shape != (68, 4) or Y.shape != (68, 10):
        raise ValueError("Changed frozen dimensions")
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("Nonfinite design or response")
    if not np.all(X[:, 0] == 1):
        raise ValueError("Intercept missing")
    arm0 = np.flatnonzero(X[:, 1] == 0)
    arm1 = np.flatnonzero(X[:, 1] == 1)
    if len(arm0) != 31 or len(arm1) != 37:
        raise ValueError("Changed fixed arm support")

    if indices is None:
        if rng is None:
            raise ValueError("A fixed random stream is required")
        indices = np.concatenate(
            [
                rng.choice(arm0, (attempts, len(arm0)), replace=True),
                rng.choice(arm1, (attempts, len(arm1)), replace=True),
            ],
            axis=1,
        )
    else:
        indices = validate_indices(X, indices)

    weights = np.zeros((attempts, 68))
    np.add.at(
        weights,
        (np.repeat(np.arange(attempts), 68), indices.ravel()),
        1.0,
    )
    point, point_se, point_valid, point_leverage = weighted_hc3(
        X, Y, np.ones((1, 68))
    )
    if not point_valid[0]:
        raise ValueError("Invalid point fit or point studentizer")

    estimates = np.empty((attempts, 10))
    bootstrap_se = np.empty_like(estimates)
    valid = np.zeros(attempts, dtype=bool)
    bootstrap_leverage = np.empty(attempts)
    for start in range(0, attempts, 250):
        block = slice(start, start + 250)
        (
            estimates[block],
            bootstrap_se[block],
            valid[block],
            bootstrap_leverage[block],
        ) = weighted_hc3(X, Y, weights[block])

    studentized = (estimates - point[0]) / bootstrap_se
    valid &= np.isfinite(studentized).all(axis=1)
    failures = int((~valid).sum())
    interval = np.full((10, 2), np.nan)
    if failures <= 20:
        quantiles = np.quantile(
            studentized[valid], [0.025, 0.975], axis=0, method="linear"
        )
        interval[:, 0] = point[0] - quantiles[1] * point_se[0]
        interval[:, 1] = point[0] - quantiles[0] * point_se[0]

    finite_bootstrap_leverage = bootstrap_leverage[np.isfinite(bootstrap_leverage)]
    max_bootstrap_leverage = (
        float(finite_bootstrap_leverage.max())
        if finite_bootstrap_leverage.size
        else None
    )
    return {
        "point": point[0],
        "se_point_HC3": point_se[0],
        "estimates": estimates,
        "se_star_HC3": bootstrap_se,
        "studentized_errors": studentized,
        "interval": interval,
        "success": valid,
        "indices": indices,
        "attempted": attempts,
        "failures": failures,
        "no_replenishment": True,
        "max_point_leverage": float(point_leverage[0]),
        "max_bootstrap_leverage": max_bootstrap_leverage,
        "gate": (
            "TECHNICAL_INTERVAL_COMPUTED"
            if failures <= 20
            else "HOLD_NUMERICAL_IMPLEMENTATION"
        ),
        "data_kind": "SIMULATED_ONLY",
        "G2B_PASS": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "interval_method": INTERVAL_METHOD,
    }
