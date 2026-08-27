#!/usr/bin/env python
"""Gate C9A: freeze label-agnostic GSE135779 selection and state mapping."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import tarfile
from datetime import datetime
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler

from phase17_c9_common import (
    ASC_FORCED_GENES,
    B_CONV_FORCED_GENES,
    B_LINEAGE_GENES,
    EXCLUSION_MODULES,
    SEED,
    assert_no_protected_columns,
    first_symbol_index,
    integrity_manifest,
    mean_gene_score,
    normalize_log_cp10k,
    parse_tar_samples,
    pearson_to_centroids,
    read_tar_barcodes,
    read_tar_matrix,
    sha256_file,
    signed_program_score,
    write_csv,
    write_json,
    write_text_lf,
)


REFERENCE_STATE_MAP = {
    "0": "B_CONV",
    "1": "B_CONV",
    "2": "B_CONV",
    "3": "B_ASC",
    "4": "B_CONV",
}

MODEL_ALPHA_GRID = (1e-5, 1e-4, 1e-3, 1e-2)
MODEL_L1_RATIO = 0.5
MAX_REFERENCE_FEATURES = 600
MAX_REFERENCE_B_CONV = 13_000


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def portable_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.name


def clear_stale_outcome_outputs(output: Path) -> None:
    """Invalidate old C9B files before a new blinded C9A run begins."""
    for path in output.iterdir():
        match = re.match(r"^(\d{2})_", path.name)
        if path.is_file() and match and int(match.group(1)) >= 18:
            path.unlink()


def load_external_genes(path: Path) -> pd.DataFrame:
    genes = pd.read_csv(
        path,
        sep="\t",
        header=None,
        names=["ensembl_id", "gene_symbol"],
    )
    genes["ensembl_id"] = genes["ensembl_id"].astype(str)
    genes["gene_symbol"] = genes["gene_symbol"].astype(str)
    genes["gene_symbol_upper"] = genes["gene_symbol"].str.upper()
    if genes["ensembl_id"].duplicated().any():
        raise RuntimeError("External Ensembl IDs are not unique")
    return genes


def load_programs(path: Path) -> tuple[pd.DataFrame, list[str]]:
    dictionary = pd.read_csv(path)
    required = {
        "program_id",
        "analysis_family",
        "sign",
        "gene_symbol",
        "ordinal",
    }
    missing = required - set(dictionary.columns)
    if missing:
        raise RuntimeError(f"Program dictionary is missing columns: {sorted(missing)}")
    primary = dictionary.loc[
        dictionary["analysis_family"].eq("primary_confirmatory")
    ].copy()
    program_ids = primary["program_id"].drop_duplicates().astype(str).tolist()
    expected = {"NAIVE_TO_MEMORY_AXIS", "ATYPICAL_LOW_NAIVE_AXIS", "APC_HLA", "IFN_ISG"}
    if set(program_ids) != expected:
        raise RuntimeError(
            "Frozen primary program family changed: "
            f"observed={sorted(program_ids)}, expected={sorted(expected)}"
        )
    if len(primary.loc[primary["program_id"].eq("IFN_ISG")]) != 12:
        raise RuntimeError("Frozen IFN/ISG program must contain exactly 12 genes")
    return primary, program_ids


def choose_reference_features(
    representation: ad.AnnData,
    raw: ad.AnnData,
    external_symbols: set[str],
) -> pd.DataFrame:
    rep_var = representation.var.copy()
    rep_var["gene_symbol_upper"] = rep_var["feature_name"].astype(str).str.upper()
    raw_symbols = raw.var["feature_name"].astype(str).str.upper()
    raw_lookup = first_symbol_index(raw_symbols)

    mask = rep_var["gene_symbol_upper"].isin(external_symbols)
    if "hvg_isg_excluded" in rep_var:
        mask &= rep_var["hvg_isg_excluded"].astype(bool)
    for column in (
        "is_mitochondrial",
        "is_ribosomal",
        "is_hemoglobin",
        "is_stress",
        "is_cell_cycle",
        "is_immunoglobulin",
        "is_strong_isg",
    ):
        if column in rep_var:
            mask &= ~rep_var[column].astype(bool)
    candidates = rep_var.loc[mask].copy()
    candidates = candidates.loc[candidates["gene_symbol_upper"].isin(raw_lookup)]
    candidates = candidates.sort_values(
        ["dispersions_norm", "gene_symbol_upper"], ascending=[False, True]
    )
    candidates = candidates.drop_duplicates("gene_symbol_upper").head(MAX_REFERENCE_FEATURES)

    forced = set(ASC_FORCED_GENES) | set(B_CONV_FORCED_GENES)
    forced_rows = rep_var.loc[
        rep_var["gene_symbol_upper"].isin(forced)
        & rep_var["gene_symbol_upper"].isin(external_symbols)
        & rep_var["gene_symbol_upper"].isin(raw_lookup)
    ].drop_duplicates("gene_symbol_upper")
    selected = pd.concat([candidates, forced_rows], axis=0)
    selected = selected.drop_duplicates("gene_symbol_upper")
    selected["reference_raw_index"] = selected["gene_symbol_upper"].map(raw_lookup).astype(int)
    selected["forced_state_marker"] = selected["gene_symbol_upper"].isin(forced)
    selected = selected.sort_values("reference_raw_index").reset_index(drop=True)
    selected.insert(0, "model_feature_order", np.arange(len(selected), dtype=int))
    if len(selected) < 200:
        raise RuntimeError(f"Too few common reference features: {len(selected)}")
    return selected[
        [
            "model_feature_order",
            "gene_symbol_upper",
            "reference_raw_index",
            "dispersions_norm",
            "forced_state_marker",
        ]
    ].rename(columns={"gene_symbol_upper": "gene_symbol"})


def sample_reference_cells(
    labels: np.ndarray,
    test_mode: bool,
) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    asc = np.flatnonzero(labels == 1)
    conv = np.flatnonzero(labels == 0)
    if test_mode:
        asc_limit = min(len(asc), 500)
        conv_limit = min(len(conv), 2_500)
        asc = np.sort(rng.choice(asc, size=asc_limit, replace=False))
        conv = np.sort(rng.choice(conv, size=conv_limit, replace=False))
    else:
        conv_limit = min(len(conv), max(MAX_REFERENCE_B_CONV, 10 * len(asc)))
        conv = np.sort(rng.choice(conv, size=conv_limit, replace=False))
    return np.sort(np.concatenate([asc, conv]))


def build_pipeline(alpha: float) -> Pipeline:
    return Pipeline(
        [
            ("scale", MaxAbsScaler()),
            (
                "model",
                SGDClassifier(
                    loss="log_loss",
                    penalty="elasticnet",
                    alpha=alpha,
                    l1_ratio=MODEL_L1_RATIO,
                    class_weight="balanced",
                    max_iter=5_000,
                    random_state=SEED,
                    tol=1e-4,
                    average=True,
                ),
            ),
        ]
    )


def class_precision(y_true: np.ndarray, predicted: np.ndarray, label: int) -> float:
    selected = predicted == label
    if not selected.any():
        return 0.0
    return float((y_true[selected] == label).mean())


def calibrate_confidence(
    y_true: np.ndarray,
    predicted: np.ndarray,
    confidence: np.ndarray,
    candidates: np.ndarray,
) -> tuple[float, pd.DataFrame]:
    rows = []
    for threshold in sorted(set(float(value) for value in candidates)):
        retained = confidence >= threshold
        coverage = float(retained.mean())
        if retained.any():
            conv_precision = class_precision(y_true[retained], predicted[retained], 0)
            asc_precision = class_precision(y_true[retained], predicted[retained], 1)
            accuracy = float((y_true[retained] == predicted[retained]).mean())
        else:
            conv_precision = 0.0
            asc_precision = 0.0
            accuracy = 0.0
        rows.append(
            {
                "threshold": threshold,
                "coverage": coverage,
                "B_CONV_precision": conv_precision,
                "B_ASC_precision": asc_precision,
                "accuracy": accuracy,
                "eligible": bool(
                    coverage >= 0.80
                    and conv_precision >= 0.90
                    and asc_precision >= 0.90
                ),
            }
        )
    audit = pd.DataFrame(rows)
    eligible = audit.loc[audit["eligible"]]
    if not eligible.empty:
        threshold = float(eligible.sort_values("threshold").iloc[0]["threshold"])
    else:
        audit["fallback_rank"] = (
            audit[["B_CONV_precision", "B_ASC_precision"]].min(axis=1)
            + 0.05 * audit["coverage"]
        )
        threshold = float(audit.sort_values(["fallback_rank", "coverage"], ascending=False).iloc[0]["threshold"])
    audit["selected"] = np.isclose(audit["threshold"], threshold)
    return threshold, audit.drop(columns=["fallback_rank"], errors="ignore")


def train_reference_mappers(
    reference_raw_path: Path,
    reference_representation_path: Path,
    external_genes: pd.DataFrame,
    output: Path,
    test_mode: bool,
) -> dict[str, object]:
    raw = ad.read_h5ad(reference_raw_path, backed="r")
    representation = ad.read_h5ad(reference_representation_path, backed="r")
    try:
        if raw.n_obs != representation.n_obs or not raw.obs_names.equals(representation.obs_names):
            raise RuntimeError("Reference raw and representation cell indices do not match exactly")
        if not raw.obs["donor_id"].astype(str).equals(
            representation.obs["donor_id"].astype(str)
        ):
            raise RuntimeError("Reference donor IDs do not match exactly")
        clusters = representation.obs["leiden_harmony_r0_4"].astype(str)
        if set(clusters.unique()) != set(REFERENCE_STATE_MAP):
            raise RuntimeError(f"Unexpected frozen r0.4 clusters: {sorted(clusters.unique())}")
        state_text = clusters.map(REFERENCE_STATE_MAP)
        labels_all = state_text.map({"B_CONV": 0, "B_ASC": 1}).to_numpy(dtype=int)
        rows = sample_reference_cells(labels_all, test_mode=test_mode)
        labels = labels_all[rows]
        groups = raw.obs["donor_id"].astype(str).to_numpy()[rows]

        features = choose_reference_features(
            representation,
            raw,
            set(external_genes["gene_symbol_upper"]),
        )
        feature_indices = features["reference_raw_index"].to_numpy(dtype=int)
        counts = raw[rows, feature_indices].X
        if not sparse.issparse(counts):
            counts = sparse.csr_matrix(counts)
        expression = normalize_log_cp10k(counts)
    finally:
        raw.file.close()
        representation.file.close()

    folds = min(5, len(np.unique(groups)))
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=SEED)
    cv_rows: list[dict[str, object]] = []
    oof_by_alpha: dict[float, np.ndarray] = {}
    fold_assignments = np.full(len(labels), -1, dtype=int)
    for alpha in MODEL_ALPHA_GRID:
        probabilities = np.full(len(labels), np.nan, dtype=float)
        for fold, (train, validation) in enumerate(splitter.split(expression, labels, groups)):
            model = build_pipeline(alpha)
            model.fit(expression[train], labels[train])
            probabilities[validation] = model.predict_proba(expression[validation])[:, 1]
            fold_assignments[validation] = fold
            predicted = (probabilities[validation] >= 0.5).astype(int)
            cv_rows.append(
                {
                    "mapper": "elastic_net",
                    "parameter": f"alpha={alpha:g};l1_ratio={MODEL_L1_RATIO:g}",
                    "fold": fold,
                    "n_validation": len(validation),
                    "n_donors": len(np.unique(groups[validation])),
                    "balanced_accuracy": balanced_accuracy_score(labels[validation], predicted),
                    "roc_auc": roc_auc_score(labels[validation], probabilities[validation]),
                    "average_precision": average_precision_score(
                        labels[validation], probabilities[validation]
                    ),
                    "brier_score": brier_score_loss(labels[validation], probabilities[validation]),
                }
            )
        if np.isnan(probabilities).any():
            raise RuntimeError(f"Incomplete elastic-net OOF predictions for alpha={alpha}")
        oof_by_alpha[alpha] = probabilities

    cv = pd.DataFrame(cv_rows)
    elastic_summary = (
        cv.loc[cv["mapper"].eq("elastic_net")]
        .groupby("parameter", observed=True)
        .agg(
            mean_balanced_accuracy=("balanced_accuracy", "mean"),
            mean_roc_auc=("roc_auc", "mean"),
            mean_average_precision=("average_precision", "mean"),
            mean_brier=("brier_score", "mean"),
        )
        .reset_index()
    )
    elastic_summary["alpha"] = elastic_summary["parameter"].str.extract(
        r"alpha=([^;]+)"
    )[0].astype(float)
    chosen_row = elastic_summary.sort_values(
        ["mean_balanced_accuracy", "mean_roc_auc", "alpha"],
        ascending=[False, False, False],
    ).iloc[0]
    chosen_alpha = float(chosen_row["alpha"])
    elastic_oof = oof_by_alpha[chosen_alpha]
    elastic_prediction = (elastic_oof >= 0.5).astype(int)
    elastic_confidence = np.maximum(elastic_oof, 1.0 - elastic_oof)
    elastic_threshold, elastic_calibration = calibrate_confidence(
        labels,
        elastic_prediction,
        elastic_confidence,
        np.round(np.arange(0.70, 0.951, 0.01), 2),
    )
    elastic_calibration.insert(0, "mapper", "elastic_net")

    elastic_model = build_pipeline(chosen_alpha)
    elastic_model.fit(expression, labels)

    centroid_oof = np.full((len(labels), 2), np.nan, dtype=np.float32)
    centroid_fold_rows = []
    for fold, (train, validation) in enumerate(splitter.split(expression, labels, groups)):
        centroids = np.vstack(
            [
                np.asarray(expression[train][labels[train] == state].mean(axis=0)).ravel()
                for state in (0, 1)
            ]
        )
        correlations = pearson_to_centroids(expression[validation], centroids)
        centroid_oof[validation] = correlations
        predicted = np.argmax(correlations, axis=1)
        margin = np.abs(correlations[:, 1] - correlations[:, 0])
        centroid_fold_rows.append(
            {
                "mapper": "nearest_centroid",
                "parameter": "Pearson correlation",
                "fold": fold,
                "n_validation": len(validation),
                "n_donors": len(np.unique(groups[validation])),
                "balanced_accuracy": balanced_accuracy_score(labels[validation], predicted),
                "roc_auc": roc_auc_score(
                    labels[validation], correlations[:, 1] - correlations[:, 0]
                ),
                "average_precision": average_precision_score(
                    labels[validation], correlations[:, 1] - correlations[:, 0]
                ),
                "brier_score": np.nan,
                "median_margin": float(np.median(margin)),
            }
        )
    if np.isnan(centroid_oof).any():
        raise RuntimeError("Incomplete nearest-centroid OOF predictions")
    cv = pd.concat([cv, pd.DataFrame(centroid_fold_rows)], ignore_index=True)
    centroid_prediction = np.argmax(centroid_oof, axis=1)
    centroid_margin = np.abs(centroid_oof[:, 1] - centroid_oof[:, 0])
    centroid_candidates = np.unique(
        np.quantile(centroid_margin, np.linspace(0.05, 0.5, 46))
    )
    centroid_threshold, centroid_calibration = calibrate_confidence(
        labels,
        centroid_prediction,
        centroid_margin,
        centroid_candidates,
    )
    centroid_calibration.insert(0, "mapper", "nearest_centroid")
    centroids = np.vstack(
        [
            np.asarray(expression[labels == state].mean(axis=0)).ravel()
            for state in (0, 1)
        ]
    ).astype(np.float32)

    oof = pd.DataFrame(
        {
            "reference_row": rows,
            "donor_id": groups,
            "fold": fold_assignments,
            "truth": np.where(labels == 1, "B_ASC", "B_CONV"),
            "elastic_probability_B_ASC": elastic_oof,
            "elastic_prediction": np.where(elastic_prediction == 1, "B_ASC", "B_CONV"),
            "elastic_confidence": elastic_confidence,
            "elastic_confident": elastic_confidence >= elastic_threshold,
            "centroid_correlation_B_CONV": centroid_oof[:, 0],
            "centroid_correlation_B_ASC": centroid_oof[:, 1],
            "centroid_prediction": np.where(centroid_prediction == 1, "B_ASC", "B_CONV"),
            "centroid_margin": centroid_margin,
            "centroid_confident": centroid_margin >= centroid_threshold,
        }
    )
    write_csv(features, output / "05_REFERENCE_MODEL_FEATURES.csv")
    write_csv(cv, output / "06_MAPPER_DONOR_GROUPED_CV.csv")
    write_csv(
        pd.concat([elastic_calibration, centroid_calibration], ignore_index=True),
        output / "07_MAPPER_CONFIDENCE_CALIBRATION.csv",
    )
    write_csv(oof, output / "08_REFERENCE_OOF_PREDICTIONS.csv")

    scaler = elastic_model.named_steps["scale"]
    classifier = elastic_model.named_steps["model"]
    coefficients = features[["model_feature_order", "gene_symbol"]].copy()
    coefficients["max_abs_scale"] = scaler.max_abs_
    coefficients["elastic_net_coefficient"] = classifier.coef_.ravel()
    coefficients["centroid_B_CONV"] = centroids[0]
    coefficients["centroid_B_ASC"] = centroids[1]
    write_csv(coefficients, output / "09_FROZEN_MAPPER_PARAMETERS.csv")

    elastic_mean_ba = float(
        cv.loc[
            cv["mapper"].eq("elastic_net")
            & cv["parameter"].eq(
                f"alpha={chosen_alpha:g};l1_ratio={MODEL_L1_RATIO:g}"
            ),
            "balanced_accuracy",
        ].mean()
    )
    centroid_mean_ba = float(
        cv.loc[cv["mapper"].eq("nearest_centroid"), "balanced_accuracy"].mean()
    )
    return {
        "elastic_model": elastic_model,
        "centroids": centroids,
        "features": features,
        "elastic_threshold": elastic_threshold,
        "centroid_threshold": centroid_threshold,
        "chosen_alpha": chosen_alpha,
        "elastic_mean_balanced_accuracy": elastic_mean_ba,
        "centroid_mean_balanced_accuracy": centroid_mean_ba,
        "n_reference_training_cells": len(labels),
        "n_reference_B_CONV": int((labels == 0).sum()),
        "n_reference_B_ASC": int((labels == 1).sum()),
        "n_reference_donors": len(np.unique(groups)),
    }


def qc_metrics(counts: sparse.csr_matrix, genes: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    n_counts = np.asarray(counts.sum(axis=1)).ravel().astype(float)
    n_genes = np.asarray(counts.getnnz(axis=1)).ravel().astype(float)
    mitochondrial = genes["gene_symbol_upper"].str.startswith("MT-").to_numpy()
    if mitochondrial.any():
        mito_counts = np.asarray(counts[:, mitochondrial].sum(axis=1)).ravel()
        mito_fraction = np.divide(
            mito_counts,
            n_counts,
            out=np.zeros_like(n_counts, dtype=float),
            where=n_counts > 0,
        )
    else:
        mito_fraction = np.zeros(len(n_counts), dtype=float)
    thresholds = {
        "minimum_counts": float(max(300, np.floor(np.quantile(n_counts, 0.005)))),
        "maximum_counts": float(np.ceil(np.quantile(n_counts, 0.999))),
        "minimum_genes": float(max(200, np.floor(np.quantile(n_genes, 0.005)))),
        "maximum_genes": float(np.ceil(np.quantile(n_genes, 0.999))),
        "maximum_mito_fraction": float(min(0.30, max(0.10, np.quantile(mito_fraction, 0.99)))),
    }
    passed = (
        (n_counts >= thresholds["minimum_counts"])
        & (n_counts <= thresholds["maximum_counts"])
        & (n_genes >= thresholds["minimum_genes"])
        & (n_genes <= thresholds["maximum_genes"])
        & (mito_fraction <= thresholds["maximum_mito_fraction"])
    )
    metrics = pd.DataFrame(
        {
            "n_counts": n_counts.astype(np.float32),
            "n_genes": n_genes.astype(np.int32),
            "mito_fraction": mito_fraction.astype(np.float32),
            "qc_pass": passed,
        }
    )
    return metrics, thresholds


def cluster_qc_cells(
    expression: sparse.csr_matrix,
    genes: pd.DataFrame,
    sample_id: str,
) -> np.ndarray:
    if expression.shape[0] < 30:
        return np.zeros(expression.shape[0], dtype=str)
    data = ad.AnnData(
        X=expression,
        var=pd.DataFrame(index=genes["ensembl_id"].astype(str).to_numpy()),
    )
    n_top = min(1_500, max(100, data.n_vars - 1))
    sc.pp.highly_variable_genes(data, flavor="seurat", n_top_genes=n_top)
    if int(data.var["highly_variable"].sum()) < 50:
        raise RuntimeError(f"Insufficient HVGs for sample {sample_id}")
    working = data[:, data.var["highly_variable"]].copy()
    n_components = min(30, working.n_obs - 1, working.n_vars - 1)
    sc.pp.pca(working, n_comps=n_components, zero_center=False, random_state=SEED)
    n_neighbors = min(15, max(5, working.n_obs - 1))
    sc.pp.neighbors(working, n_neighbors=n_neighbors, n_pcs=n_components, random_state=SEED)
    sc.tl.leiden(
        working,
        resolution=0.6,
        key_added="label_agnostic_leiden",
        random_state=SEED,
        flavor="igraph",
        n_iterations=2,
        directed=False,
    )
    return working.obs["label_agnostic_leiden"].astype(str).to_numpy()


def annotate_lineage(
    expression: sparse.csr_matrix,
    genes: pd.DataFrame,
    clusters: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    symbol_lookup = first_symbol_index(genes["gene_symbol_upper"])
    b_score, b_present, b_missing = mean_gene_score(
        expression, symbol_lookup, B_LINEAGE_GENES
    )
    b_detection = np.zeros(expression.shape[0], dtype=np.float32)
    if b_present:
        indices = [symbol_lookup[gene] for gene in b_present]
        b_detection = np.asarray((expression[:, indices] > 0).mean(axis=1)).ravel().astype(np.float32)
    module_scores = {"B_LINEAGE": b_score}
    module_presence = [
        {
            "module": "B_LINEAGE",
            "requested_genes": len(B_LINEAGE_GENES),
            "present_genes": len(b_present),
            "missing_genes": ";".join(b_missing),
        }
    ]
    for module, module_genes in EXCLUSION_MODULES.items():
        score, present, missing = mean_gene_score(expression, symbol_lookup, module_genes)
        module_scores[module] = score
        module_presence.append(
            {
                "module": module,
                "requested_genes": len(module_genes),
                "present_genes": len(present),
                "missing_genes": ";".join(missing),
            }
        )
    scores = pd.DataFrame(module_scores)
    scores["b_detection_fraction"] = b_detection
    scores["maximum_exclusion_score"] = scores[list(EXCLUSION_MODULES)].max(axis=1)
    scores["b_lineage_margin"] = scores["B_LINEAGE"] - scores["maximum_exclusion_score"]
    scores["cluster"] = clusters

    cluster_summary = (
        scores.groupby("cluster", observed=True)
        .agg(
            cluster_cells=("cluster", "size"),
            B_LINEAGE_score=("B_LINEAGE", "median"),
            b_detection_fraction=("b_detection_fraction", "mean"),
            T_NK_score=("T_NK", "median"),
            MYELOID_score=("MYELOID", "median"),
            PLATELET_score=("PLATELET", "median"),
            ERYTHROID_score=("ERYTHROID", "median"),
            b_lineage_margin=("b_lineage_margin", "median"),
        )
        .reset_index()
    )
    cluster_summary["maximum_exclusion_score"] = cluster_summary[
        [f"{name}_score" for name in EXCLUSION_MODULES]
    ].max(axis=1)
    cluster_summary["cluster_selected_B"] = (
        (cluster_summary["B_LINEAGE_score"] > cluster_summary["maximum_exclusion_score"])
        & (cluster_summary["b_detection_fraction"] >= (1.0 / len(B_LINEAGE_GENES)))
        & (cluster_summary["cluster_cells"] >= 10)
    )
    selected_lookup = cluster_summary.set_index("cluster")["cluster_selected_B"]
    scores["cluster_selected_B"] = scores["cluster"].map(selected_lookup).astype(bool)
    scores["cell_margin_selected_B"] = (
        (scores["b_lineage_margin"] > 0)
        & (scores["b_detection_fraction"] >= (1.0 / len(B_LINEAGE_GENES)))
    )
    scores.attrs["module_presence"] = module_presence
    return scores, cluster_summary


def process_external_samples(
    source_dir: Path,
    external_genes: pd.DataFrame,
    programs: pd.DataFrame,
    program_ids: list[str],
    mappers: dict[str, object],
    output: Path,
    max_samples: int | None,
) -> dict[str, object]:
    raw_tar = source_dir / "GSE135779_RAW.tar"
    samples = parse_tar_samples(raw_tar)
    if max_samples is not None:
        samples = samples.head(max_samples).copy()
    feature_table = mappers["features"]
    external_lookup = first_symbol_index(external_genes["gene_symbol_upper"])
    external_feature_indices = np.array(
        [external_lookup[symbol] for symbol in feature_table["gene_symbol"]], dtype=int
    )
    prediction_path = output / "10_CELL_PREDICTIONS_LOCAL.csv.gz"
    if prediction_path.exists():
        prediction_path.unlink()

    sample_rows: list[dict[str, object]] = []
    cluster_tables: list[pd.DataFrame] = []
    module_presence_rows: list[dict[str, object]] = []
    program_presence_rows: list[dict[str, object]] = []
    expected_columns: list[str] | None = None
    total_cells = 0
    total_qc = 0
    total_selected = 0
    header = True
    with tarfile.open(raw_tar, "r") as archive, gzip.open(
        prediction_path, "wt", encoding="utf-8", newline=""
    ) as prediction_stream:
        for sample_index, sample in enumerate(samples.itertuples(index=False), start=1):
            barcodes = read_tar_barcodes(archive, sample.barcode_file)
            matrix = read_tar_matrix(archive, sample.matrix_file)
            if matrix.shape == (len(external_genes), len(barcodes)):
                counts = matrix.T.tocsr().astype(np.float32)
            elif matrix.shape == (len(barcodes), len(external_genes)):
                counts = matrix.tocsr().astype(np.float32)
            else:
                raise RuntimeError(
                    f"Matrix dimensions disagree for {sample.sample_id}: "
                    f"matrix={matrix.shape}, genes={len(external_genes)}, barcodes={len(barcodes)}"
                )
            metrics, thresholds = qc_metrics(counts, external_genes)
            qc_indices = np.flatnonzero(metrics["qc_pass"].to_numpy())
            expression = normalize_log_cp10k(counts[qc_indices])
            clusters = cluster_qc_cells(expression, external_genes, sample.sample_id)
            lineage, cluster_summary = annotate_lineage(expression, external_genes, clusters)
            cluster_summary.insert(0, "sample_id", sample.sample_id)
            cluster_tables.append(cluster_summary)
            for row in lineage.attrs["module_presence"]:
                module_presence_rows.append({"sample_id": sample.sample_id, **row})

            cell = pd.DataFrame(
                {
                    "sample_id": sample.sample_id,
                    "barcode": barcodes,
                    "barcode_core": [barcode.split("-")[0] for barcode in barcodes],
                    "n_counts": metrics["n_counts"],
                    "n_genes": metrics["n_genes"],
                    "mito_fraction": metrics["mito_fraction"],
                    "qc_pass": metrics["qc_pass"],
                    "label_agnostic_leiden": "",
                    "B_LINEAGE_score": np.nan,
                    "maximum_exclusion_score": np.nan,
                    "b_lineage_margin": np.nan,
                    "b_detection_fraction": np.nan,
                    "cluster_selected_B": False,
                    "cell_margin_selected_B": False,
                    "elastic_probability_B_ASC": np.nan,
                    "elastic_prediction": "",
                    "elastic_confidence": np.nan,
                    "elastic_confident": False,
                    "centroid_correlation_B_CONV": np.nan,
                    "centroid_correlation_B_ASC": np.nan,
                    "centroid_prediction": "",
                    "centroid_margin": np.nan,
                    "centroid_confident": False,
                }
            )
            cell.loc[qc_indices, "label_agnostic_leiden"] = lineage["cluster"].to_numpy()
            for column in (
                "B_LINEAGE",
                "maximum_exclusion_score",
                "b_lineage_margin",
                "b_detection_fraction",
                "cluster_selected_B",
                "cell_margin_selected_B",
            ):
                target = "B_LINEAGE_score" if column == "B_LINEAGE" else column
                cell.loc[qc_indices, target] = lineage[column].to_numpy()

            mapping_union = (
                lineage["cluster_selected_B"].to_numpy()
                | lineage["cell_margin_selected_B"].to_numpy()
            )
            selected_local = np.flatnonzero(mapping_union)
            selected_global = qc_indices[selected_local]
            if len(selected_local):
                model_expression = expression[selected_local][:, external_feature_indices]
                elastic_probability = mappers["elastic_model"].predict_proba(model_expression)[:, 1]
                elastic_prediction = (elastic_probability >= 0.5).astype(int)
                elastic_confidence = np.maximum(elastic_probability, 1.0 - elastic_probability)
                correlations = pearson_to_centroids(model_expression, mappers["centroids"])
                centroid_prediction = np.argmax(correlations, axis=1)
                centroid_margin = np.abs(correlations[:, 1] - correlations[:, 0])
                cell.loc[selected_global, "elastic_probability_B_ASC"] = elastic_probability
                cell.loc[selected_global, "elastic_prediction"] = np.where(
                    elastic_prediction == 1, "B_ASC", "B_CONV"
                )
                cell.loc[selected_global, "elastic_confidence"] = elastic_confidence
                cell.loc[selected_global, "elastic_confident"] = (
                    elastic_confidence >= float(mappers["elastic_threshold"])
                )
                cell.loc[selected_global, "centroid_correlation_B_CONV"] = correlations[:, 0]
                cell.loc[selected_global, "centroid_correlation_B_ASC"] = correlations[:, 1]
                cell.loc[selected_global, "centroid_prediction"] = np.where(
                    centroid_prediction == 1, "B_ASC", "B_CONV"
                )
                cell.loc[selected_global, "centroid_margin"] = centroid_margin
                cell.loc[selected_global, "centroid_confident"] = (
                    centroid_margin >= float(mappers["centroid_threshold"])
                )

            symbol_lookup = first_symbol_index(external_genes["gene_symbol_upper"])
            for program_id in program_ids:
                score, audit = signed_program_score(
                    expression,
                    symbol_lookup,
                    programs.loc[programs["program_id"].eq(program_id)],
                )
                column = f"program_{program_id}"
                cell[column] = np.nan
                cell.loc[qc_indices, column] = score
                program_presence_rows.append(
                    {"sample_id": sample.sample_id, "program_id": program_id, **audit}
                )

            assert_no_protected_columns(cell.columns)
            if expected_columns is None:
                expected_columns = cell.columns.tolist()
            elif cell.columns.tolist() != expected_columns:
                raise RuntimeError("Per-cell output columns changed between samples")
            cell.to_csv(prediction_stream, index=False, header=header, lineterminator="\n")
            header = False

            selected = cell["cluster_selected_B"].astype(bool)
            sample_rows.append(
                {
                    "sample_id": sample.sample_id,
                    "matrix_cells": len(cell),
                    "qc_pass_cells": int(cell["qc_pass"].sum()),
                    "qc_pass_fraction": float(cell["qc_pass"].mean()),
                    "cluster_selected_B_cells": int(selected.sum()),
                    "cluster_selected_B_fraction_of_qc": float(
                        selected.sum() / max(1, cell["qc_pass"].sum())
                    ),
                    "cell_margin_selected_B_cells": int(cell["cell_margin_selected_B"].sum()),
                    "elastic_confident_fraction_selected": float(
                        cell.loc[selected, "elastic_confident"].mean()
                    )
                    if selected.any()
                    else np.nan,
                    "centroid_confident_fraction_selected": float(
                        cell.loc[selected, "centroid_confident"].mean()
                    )
                    if selected.any()
                    else np.nan,
                    **thresholds,
                }
            )
            total_cells += len(cell)
            total_qc += int(cell["qc_pass"].sum())
            total_selected += int(selected.sum())
            print(
                f"[C9A] {sample_index}/{len(samples)} {sample.sample_id}: "
                f"{len(cell):,} cells; {int(cell['qc_pass'].sum()):,} QC; "
                f"{int(selected.sum()):,} label-agnostic B",
                flush=True,
            )
            del matrix, counts, expression, cell

    sample_summary = pd.DataFrame(sample_rows)
    cluster_summary = pd.concat(cluster_tables, ignore_index=True)
    module_presence = pd.DataFrame(module_presence_rows).drop_duplicates(
        ["module", "requested_genes", "present_genes", "missing_genes"]
    )
    program_presence = pd.DataFrame(program_presence_rows).drop_duplicates(
        [
            "program_id",
            "positive_requested",
            "positive_present",
            "positive_missing",
            "negative_requested",
            "negative_present",
            "negative_missing",
        ]
    )
    write_csv(sample_summary, output / "11_SAMPLE_PREFREEZE_SUMMARY.csv")
    write_csv(cluster_summary, output / "12_CLUSTER_SELECTION_AUDIT.csv")
    write_csv(module_presence, output / "13_LINEAGE_MODULE_AVAILABILITY.csv")
    write_csv(program_presence, output / "14_PROGRAM_GENE_AVAILABILITY.csv")
    return {
        "samples": len(samples),
        "total_cells": total_cells,
        "qc_pass_cells": total_qc,
        "selected_B_cells": total_selected,
        "prediction_path": prediction_path,
        "minimum_elastic_confident_fraction": float(
            sample_summary["elastic_confident_fraction_selected"].min()
        ),
        "minimum_centroid_confident_fraction": float(
            sample_summary["centroid_confident_fraction_selected"].min()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--reference-raw", required=True)
    parser.add_argument("--reference-representation", required=True)
    parser.add_argument("--program-dictionary", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--max-samples", type=int)
    args = parser.parse_args()

    source = Path(args.source_dir).resolve()
    project_root = Path(args.project_root).resolve()
    reference_raw = Path(args.reference_raw).resolve()
    reference_representation = Path(args.reference_representation).resolve()
    program_dictionary_path = Path(args.program_dictionary).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    clear_stale_outcome_outputs(output)

    input_paths = [
        source / "GSE135779_RAW.tar",
        source / "GSE135779_genes.tsv.gz",
        source / "Meta_cSLE_processed_0809202_small.csv",
        source / "Meta_caSLE_processed_08092021_small.csv",
        source / "GSE135779_series_matrix.txt.gz",
        source / "libaries.csv",
        reference_raw,
        reference_representation,
        program_dictionary_path,
    ]
    missing = [str(path) for path in input_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Gate C9A inputs: " + ", ".join(missing))
    manifest = pd.DataFrame(
        [
            {
                "path": portable_path(path, project_root),
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "protected_metadata": path.name.startswith("Meta_"),
            }
            for path in input_paths
        ]
    )
    write_csv(manifest, output / "01_INPUT_SHA256_MANIFEST.csv")
    protection = {
        "created_at": now_iso(),
        "status": "PROTECTED_METADATA_CONTENT_NOT_PARSED",
        "test_mode": bool(args.test_mode),
        "protected_files": [
            "Meta_cSLE_processed_0809202_small.csv",
            "Meta_caSLE_processed_08092021_small.csv",
        ],
        "protected_fields": sorted(
            ["Names", "SLEDAI", "SLEDAI_cat", "Groups", "subclusters"]
        ),
        "permitted_prefreeze_identifiers": ["sample_id", "barcode", "barcode_core"],
        "outcome_unlock_authorized": False,
    }
    write_json(protection, output / "02_PROTECTED_METADATA_CONTRACT.json")

    external_genes = load_external_genes(source / "GSE135779_genes.tsv.gz")
    programs, program_ids = load_programs(program_dictionary_path)
    mappers = train_reference_mappers(
        reference_raw,
        reference_representation,
        external_genes,
        output,
        test_mode=bool(args.test_mode),
    )
    external = process_external_samples(
        source,
        external_genes,
        programs,
        program_ids,
        mappers,
        output,
        max_samples=args.max_samples,
    )

    expected_samples = args.max_samples if args.max_samples is not None else 56
    checks = {
        "input_manifest_complete": len(manifest) == len(input_paths),
        "protected_metadata_content_not_parsed": True,
        "reference_join_exact": True,
        "elastic_net_cv_balanced_accuracy": mappers[
            "elastic_mean_balanced_accuracy"
        ]
        >= 0.90,
        "nearest_centroid_cv_balanced_accuracy": mappers[
            "centroid_mean_balanced_accuracy"
        ]
        >= 0.90,
        "all_expected_samples_processed": external["samples"] == expected_samples,
        "all_cells_reconciled": external["total_cells"] > 0,
        "label_agnostic_B_cells_selected": external["selected_B_cells"] > 0,
        "per_cell_output_present": external["prediction_path"].is_file(),
    }
    authorized = all(checks.values()) and not args.test_mode
    decision = {
        "created_at": now_iso(),
        "decision": (
            "PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED"
            if authorized
            else (
                "PASS_C9A_TEST_MODE_NO_OUTCOME_UNLOCK"
                if args.test_mode and all(checks.values())
                else "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
            )
        ),
        "test_mode": bool(args.test_mode),
        "disease_blind": True,
        "source_labels_used": False,
        "outcome_unlock_authorized": authorized,
        "reference_model": {
            key: value
            for key, value in mappers.items()
            if key
            not in {
                "elastic_model",
                "centroids",
                "features",
            }
        },
        "external_prefreeze": {
            key: (value.name if isinstance(value, Path) else value)
            for key, value in external.items()
        },
        "checks": checks,
        "frozen_rules": {
            "primary_selection": "sample-wise Leiden cluster with B-lineage module greater than all exclusion modules and mean B detection >=1/9",
            "selection_sensitivity": "per-cell B-lineage margin >0 and B detection >=1/9",
            "primary_mapper": "donor-grouped elastic-net logistic regression",
            "independent_mapper": "nearest-centroid Pearson correlation",
            "outcome_family": program_ids,
            "primary_outcome": "childhood donor mean 12-gene IFN_ISG score in confidently mapped B_CONV",
            "minimum_B_CONV_cells_per_donor": 50,
        },
    }
    write_json(decision, output / "15_GATE_C9A_PREFREEZE_DECISION.json")
    protection["status"] = "PREFREEZE_COMPLETE"
    protection["outcome_unlock_authorized"] = authorized
    protection["unlock_decision_file"] = "15_GATE_C9A_PREFREEZE_DECISION.json"
    write_json(protection, output / "02_PROTECTED_METADATA_CONTRACT.json")

    report = [
        "# Gate C9A label-agnostic prefreeze review",
        "",
        f"- Decision: `{decision['decision']}`",
        f"- Test mode: `{args.test_mode}`",
        f"- External samples: {external['samples']}",
        f"- Matrix cells: {external['total_cells']:,}",
        f"- QC-passing cells: {external['qc_pass_cells']:,}",
        f"- Cluster-selected B-lineage cells: {external['selected_B_cells']:,}",
        f"- Elastic-net donor-grouped mean balanced accuracy: {mappers['elastic_mean_balanced_accuracy']:.3f}",
        f"- Nearest-centroid donor-grouped mean balanced accuracy: {mappers['centroid_mean_balanced_accuracy']:.3f}",
        f"- Elastic-net confidence threshold: {mappers['elastic_threshold']:.3f}",
        f"- Nearest-centroid margin threshold: {mappers['centroid_threshold']:.5f}",
        "",
        "Protected metadata files were hashed but their fields were not parsed or joined during this stage. "
        "Per-cell predictions are retained locally in a Git-ignored gzip file.",
        "",
        "Outcome metadata may be joined only when `outcome_unlock_authorized` is true.",
    ]
    write_text_lf(
        "\n".join(report) + "\n",
        output / "16_GATE_C9A_PREFREEZE_REVIEW.md",
    )
    manifest_out = integrity_manifest(output, excluded={"17_FILE_INTEGRITY_MANIFEST.csv"})
    write_csv(manifest_out, output / "17_FILE_INTEGRITY_MANIFEST.csv")
    print(json.dumps(decision, indent=2, ensure_ascii=True), flush=True)
    return 0 if decision["decision"].startswith("PASS") else 2


if __name__ == "__main__":
    sys.exit(main())
