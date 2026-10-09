"""Result-blind geometry and audit helpers for RP v3 WP2.

These functions define measurement geometry and Monte Carlo reporting only.
They do not fit disease effects or authorize a G2 decision.
"""

from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np


def finite_array(values, name: str, ndim: int | None = None) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if not np.isfinite(array).all():
        raise ValueError(f"{name}: non-finite values")
    if ndim is not None and array.ndim != ndim:
        raise ValueError(f"{name}: expected {ndim} dimensions, got {array.ndim}")
    return array


def close_rows(values) -> np.ndarray:
    array = finite_array(values, "composition", 2)
    if (array < 0).any() or (array.sum(axis=1) <= 0).any():
        raise ValueError("Negative mass or empty row; no implicit replacement")
    return array / array.sum(axis=1, keepdims=True)


def composition_geometry(counts, totals, cells, reference_weights) -> dict[str, np.ndarray]:
    """Return cell-, UMI- and reference-weighted expression objects.

    ``counts`` is donor x bin x gene. ``totals`` contains the full captured
    library size, not the sum over the program genes. Returned profiles are
    captured-relative expression and must not be called absolute RNA/cell.
    """

    gene_counts = finite_array(counts, "counts", 3)
    library_totals = finite_array(totals, "totals", 2)
    cell_counts = finite_array(cells, "cells", 2)
    pi_ref = finite_array(reference_weights, "reference_weights", 1)

    if gene_counts.shape[:2] != library_totals.shape:
        raise ValueError("Count and library axes differ")
    if cell_counts.shape != library_totals.shape:
        raise ValueError("Cell and library axes differ")
    if gene_counts.shape[1] != len(pi_ref):
        raise ValueError("Reference-weight axis differs")
    if (gene_counts < 0).any() or (library_totals <= 0).any() or (cell_counts <= 0).any():
        raise ValueError("A missing or empty bin is not an expression zero")
    if (gene_counts.sum(axis=2) > library_totals + 1e-8).any():
        raise ValueError("Program-gene counts exceed the full library")
    if (pi_ref <= 0).any() or not math.isclose(
        float(pi_ref.sum()), 1.0, rel_tol=0, abs_tol=1e-12
    ):
        raise ValueError("Reference weights must be positive and closed")

    bin_cpm = gene_counts * 1e6 / library_totals[:, :, None]
    p_cell = close_rows(cell_counts)
    q_umi = close_rows(library_totals)
    captured_umi_per_cell = library_totals / cell_counts
    pooled_cpm = gene_counts.sum(axis=1) * 1e6 / library_totals.sum(axis=1, keepdims=True)
    reconstructed_cpm = np.einsum("nk,nkg->ng", q_umi, bin_cpm)
    if not np.allclose(pooled_cpm, reconstructed_cpm, atol=1e-8, rtol=1e-12):
        raise AssertionError("Captured-UMI mass-balance identity failed")

    cellref_umi_weights = close_rows(pi_ref[None, :] * captured_umi_per_cell)
    return {
        "p_cell": p_cell,
        "q_umi": q_umi,
        "captured_umi_per_cell": captured_umi_per_cell,
        "bin_cpm": bin_cpm,
        "pooled_cpm": pooled_cpm,
        "q_reconstructed_cpm": reconstructed_cpm,
        "p_reconstructed_cpm": np.einsum("nk,nkg->ng", p_cell, bin_cpm),
        "pi_profile_reconstructed_cpm": np.einsum("k,nkg->ng", pi_ref, bin_cpm),
        "pi_cellref_umiweights": cellref_umi_weights,
        "pi_cellref_reconstructed_cpm": np.einsum(
            "nk,nkg->ng", cellref_umi_weights, bin_cpm
        ),
    }


def frozen_score(cpm, means, standard_deviations) -> np.ndarray:
    values = finite_array(cpm, "CPM")
    means = finite_array(means, "means", 1)
    standard_deviations = finite_array(standard_deviations, "standard_deviations", 1)
    if values.shape[-1] != len(means) or standard_deviations.shape != means.shape:
        raise ValueError("Frozen score axes differ")
    if (standard_deviations <= 0).any() or (values < 0).any():
        raise ValueError("Frozen score contract failure")
    return ((np.log2(values + 0.5) - means) / standard_deviations).mean(axis=-1)


def ilr_basis(bin_count: int = 5) -> np.ndarray:
    if bin_count < 2:
        raise ValueError("At least two bins are required")
    basis = np.zeros((bin_count - 1, bin_count))
    for index in range(1, bin_count):
        basis[index - 1, :index] = 1 / math.sqrt(index * (index + 1))
        basis[index - 1, index] = -index / math.sqrt(index * (index + 1))
    return basis


def ilr_positive(composition) -> np.ndarray:
    values = finite_array(composition, "composition", 2)
    if (values <= 0).any() or not np.allclose(
        values.sum(axis=1), 1, atol=1e-12, rtol=0
    ):
        raise ValueError("ILR requires positive closed data; no automatic pseudocount")
    return np.log(values) @ ilr_basis(values.shape[1]).T


def rank_no_lapack(design, tolerance: float = 1e-10) -> int:
    """Compute column rank by scaled row elimination without a LAPACK call."""

    matrix = finite_array(design, "design", 2).copy()
    scales = np.max(np.abs(matrix), axis=0)
    scales[scales == 0] = 1
    matrix /= scales
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


def wilson_interval(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    if trials <= 0 or not 0 <= successes <= trials or not 0 < alpha < 1:
        raise ValueError("Invalid binomial inputs")
    z_value = NormalDist().inv_cdf(1 - alpha / 2)
    proportion = successes / trials
    denominator = 1 + z_value**2 / trials
    center = (proportion + z_value**2 / (2 * trials)) / denominator
    half_width = (
        z_value
        * math.sqrt(
            proportion * (1 - proportion) / trials
            + z_value**2 / (4 * trials**2)
        )
        / denominator
    )
    return max(0.0, center - half_width), min(1.0, center + half_width)


def freeze_ready(contract: dict) -> dict:
    required_hashes = [
        "prefit_receipt_sha256",
        "raw_counts_sha256",
        "branch_assignments_sha256",
        "simulation_generator_sha256",
        "independent_truth_code_sha256",
        "truth_receipt_sha256",
        "calibration_inputs_sha256",
        "runtime_lock_sha256",
        "scenario_registry_sha256",
        "acceptance_table_sha256",
    ]
    missing = []
    for field in required_hashes:
        value = contract.get(field)
        if not isinstance(value, str) or len(value) != 64:
            missing.append(field)
            continue
        if any(character not in "0123456789abcdefABCDEF" for character in value):
            missing.append(field)
    ready = not missing and contract.get("approved_for_execution") is True
    return {
        "ready": ready,
        "missing": missing,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "G2_PASS": False,
    }
