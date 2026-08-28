"""Shared utilities for Gate C9 label-agnostic GSE135779 validation."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import tarfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.io import mmread


SEED = 20260828

B_LINEAGE_GENES = (
    "CD19",
    "MS4A1",
    "CD79A",
    "CD79B",
    "CD37",
    "CD74",
    "HLA-DRA",
    "CD22",
    "CD83",
)

EXCLUSION_MODULES = {
    "T_NK": ("CD3D", "CD3E", "CD3G", "TRBC1", "TRBC2", "NKG7", "GNLY"),
    "MYELOID": (
        "LST1",
        "TYROBP",
        "FCER1G",
        "CTSS",
        "LILRB1",
        "S100A8",
        "S100A9",
        "CTSD",
    ),
    "PLATELET": ("PPBP", "PF4", "NRGN", "TUBB1", "RGS18"),
    "ERYTHROID": ("HBB", "HBA1", "HBA2", "AHSP", "ALAS2"),
}

ASC_FORCED_GENES = (
    "MZB1",
    "XBP1",
    "PRDM1",
    "JCHAIN",
    "SDC1",
    "IRF4",
    "TNFRSF17",
    "DERL3",
    "FKBP11",
    "HSP90B1",
)

B_CONV_FORCED_GENES = (
    "MS4A1",
    "CD79A",
    "CD79B",
    "CD74",
    "CD19",
    "CD22",
    "CD37",
    "TCL1A",
    "CD27",
    "TNFRSF13B",
)

PROTECTED_COLUMNS = {
    "names",
    "disease",
    "disease_group",
    "disease_label",
    "group",
    "groups",
    "sle",
    "is_sle",
    "sledai",
    "sledai_cat",
    "subclusters",
    "source_label",
}


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_csv(frame: pd.DataFrame, path: Path, **kwargs) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs.setdefault("index", False)
    kwargs.setdefault("lineterminator", "\n")
    frame.to_csv(path, **kwargs)


def write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")


def write_text_lf(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def parse_tar_samples(raw_tar: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with tarfile.open(raw_tar, "r") as archive:
        names = set(archive.getnames())
        for name in sorted(names):
            if not name.endswith("_barcodes.tsv.gz"):
                continue
            basename = Path(name).name
            parts = basename.split("_")
            if len(parts) < 3:
                raise RuntimeError(f"Unexpected GSE135779 archive member: {name}")
            matrix_name = name.replace("_barcodes.tsv.gz", "_matrix.mtx.gz")
            if matrix_name not in names:
                raise FileNotFoundError(f"Missing matrix paired with {name}")
            rows.append(
                {
                    "accession": parts[0],
                    "sample_id": parts[1],
                    "barcode_file": name,
                    "matrix_file": matrix_name,
                }
            )
    if not rows:
        raise RuntimeError(f"No sample matrix pairs found in {raw_tar}")
    frame = pd.DataFrame(rows).sort_values("sample_id").reset_index(drop=True)
    if frame["sample_id"].duplicated().any():
        raise RuntimeError("Duplicate sample IDs in GSE135779 archive")
    return frame


def read_tar_barcodes(archive: tarfile.TarFile, member_name: str) -> list[str]:
    handle = archive.extractfile(member_name)
    if handle is None:
        raise FileNotFoundError(member_name)
    with gzip.open(handle, "rt") as stream:
        return [line.strip() for line in stream if line.strip()]


def read_tar_matrix(archive: tarfile.TarFile, member_name: str) -> sparse.csr_matrix:
    handle = archive.extractfile(member_name)
    if handle is None:
        raise FileNotFoundError(member_name)
    with gzip.open(handle, "rb") as stream:
        matrix = mmread(stream).tocsr()
    return matrix


def normalize_log_cp10k(
    counts: sparse.spmatrix, *, library_totals: np.ndarray | None = None
) -> sparse.csr_matrix:
    """Normalize to full-library totals, including when counts are feature-subsetted."""
    matrix = counts.tocsr().astype(np.float32, copy=True)
    if not np.isfinite(matrix.data).all() or (matrix.data < 0).any():
        raise ValueError("Counts must be finite and nonnegative")
    subset_totals = np.asarray(matrix.sum(axis=1)).ravel().astype(np.float32)
    totals = subset_totals if library_totals is None else np.asarray(library_totals, dtype=np.float32)
    if totals.shape != (matrix.shape[0],):
        raise ValueError("One library total per cell is required")
    if not np.isfinite(totals).all() or (totals < 0).any():
        raise ValueError("Library totals must be finite and nonnegative")
    if (totals + 1e-5 * np.maximum(subset_totals, 1) < subset_totals).any():
        raise ValueError("Library totals cannot be smaller than selected-feature counts")
    factors = np.divide(
        10_000.0,
        totals,
        out=np.zeros_like(totals, dtype=np.float32),
        where=totals > 0,
    )
    matrix = matrix.multiply(factors[:, None]).tocsr()
    matrix.data = np.log1p(matrix.data)
    return matrix


def first_symbol_index(symbols: Iterable[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for index, symbol in enumerate(symbols):
        key = str(symbol).upper()
        if key and key not in mapping:
            mapping[key] = index
    return mapping


def mean_gene_score(
    matrix: sparse.csr_matrix,
    symbol_to_index: dict[str, int],
    genes: Iterable[str],
) -> tuple[np.ndarray, list[str], list[str]]:
    requested = [str(gene).upper() for gene in genes]
    present = [gene for gene in requested if gene in symbol_to_index]
    missing = [gene for gene in requested if gene not in symbol_to_index]
    if not present:
        return np.full(matrix.shape[0], np.nan, dtype=np.float32), present, missing
    indices = [symbol_to_index[gene] for gene in present]
    score = np.asarray(matrix[:, indices].mean(axis=1)).ravel().astype(np.float32)
    return score, present, missing


def signed_program_score(
    matrix: sparse.csr_matrix,
    symbol_to_index: dict[str, int],
    rows: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object]]:
    positive = rows.loc[rows["sign"].astype(float) > 0, "gene_symbol"].astype(str).tolist()
    negative = rows.loc[rows["sign"].astype(float) < 0, "gene_symbol"].astype(str).tolist()
    positive_score, positive_present, positive_missing = mean_gene_score(
        matrix, symbol_to_index, positive
    )
    if negative:
        negative_score, negative_present, negative_missing = mean_gene_score(
            matrix, symbol_to_index, negative
        )
        score = positive_score - negative_score
    else:
        negative_present = []
        negative_missing = []
        score = positive_score
    audit = {
        "positive_requested": len(positive),
        "positive_present": len(positive_present),
        "positive_missing": ";".join(positive_missing),
        "negative_requested": len(negative),
        "negative_present": len(negative_present),
        "negative_missing": ";".join(negative_missing),
    }
    return score.astype(np.float32), audit


def bh_fdr(values: Iterable[float]) -> np.ndarray:
    pvalues = np.asarray(list(values), dtype=float)
    adjusted = np.full_like(pvalues, np.nan)
    finite = np.isfinite(pvalues)
    if not finite.any():
        return adjusted
    p = pvalues[finite]
    order = np.argsort(p)
    ranked = p[order]
    n = len(ranked)
    q = np.empty(n, dtype=float)
    running = 1.0
    for index in range(n - 1, -1, -1):
        running = min(running, ranked[index] * n / (index + 1))
        q[index] = running
    restored = np.empty(n, dtype=float)
    restored[order] = np.clip(q, 0.0, 1.0)
    adjusted[finite] = restored
    return adjusted


def pearson_to_centroids(
    matrix: sparse.csr_matrix,
    centroids: np.ndarray,
) -> np.ndarray:
    """Return row-wise Pearson correlations to dense reference centroids."""
    x = matrix.tocsr().astype(np.float64, copy=False)
    centroids = np.asarray(centroids, dtype=np.float64)
    centered = centroids - centroids.mean(axis=1, keepdims=True)
    centroid_norm = np.sqrt(np.sum(centered**2, axis=1))
    row_sum = np.asarray(x.sum(axis=1)).ravel()
    row_sq_sum = np.asarray(x.multiply(x).sum(axis=1)).ravel()
    row_norm = np.sqrt(np.maximum(row_sq_sum - (row_sum**2 / x.shape[1]), 0.0))
    numerator = np.asarray(x @ centered.T)
    denominator = row_norm[:, None] * centroid_norm[None, :]
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0,
    ).astype(np.float32)


def bootstrap_mean_difference(
    exposed: np.ndarray,
    reference: np.ndarray,
    iterations: int = 10_000,
    seed: int = SEED,
) -> tuple[float, float]:
    exposed = np.asarray(exposed, dtype=float)
    reference = np.asarray(reference, dtype=float)
    if len(exposed) == 0 or len(reference) == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    differences = np.empty(iterations, dtype=float)
    for index in range(iterations):
        differences[index] = (
            rng.choice(exposed, size=len(exposed), replace=True).mean()
            - rng.choice(reference, size=len(reference), replace=True).mean()
        )
    low, high = np.quantile(differences, [0.025, 0.975])
    return float(low), float(high)


def assert_no_protected_columns(columns: Iterable[str]) -> None:
    normalized = {str(column).strip().lower() for column in columns}
    found = sorted(normalized & PROTECTED_COLUMNS)
    if found:
        raise RuntimeError(f"Protected columns leaked into prefreeze output: {found}")


def integrity_manifest(directory: Path, excluded: set[str] | None = None) -> pd.DataFrame:
    excluded = excluded or set()
    rows = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.name in excluded:
            continue
        rows.append(
            {
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return pd.DataFrame(rows)
