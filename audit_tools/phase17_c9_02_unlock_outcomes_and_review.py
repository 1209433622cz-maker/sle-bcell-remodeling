#!/usr/bin/env python
"""Gate C9B: unlock protected metadata after C9A and test frozen outcomes."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import mannwhitneyu

from phase17_c9_common import (
    bh_fdr,
    bootstrap_mean_difference,
    integrity_manifest,
    sha256_file,
    write_csv,
    write_json,
    write_text_lf,
)


MINIMUM_B_CONV_CELLS = 50
SELECTIONS = {
    "cluster_primary": "cluster_selected_B",
    "cell_margin_sensitivity": "cell_margin_selected_B",
}
MAPPERS = {
    "elastic_net": {
        "prediction": "elastic_prediction",
        "confident": "elastic_confident",
    },
    "nearest_centroid": {
        "prediction": "centroid_prediction",
        "confident": "centroid_confident",
    },
}
PRIMARY_PROGRAMS = (
    "NAIVE_TO_MEMORY_AXIS",
    "ATYPICAL_LOW_NAIVE_AXIS",
    "APC_HLA",
    "IFN_ISG",
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def bool_series(values: pd.Series) -> pd.Series:
    if values.dtype == bool:
        return values
    return values.astype(str).str.lower().isin({"true", "1", "yes"})


def verify_prefreeze(prefreeze: Path, project_root: Path) -> dict:
    decision_path = prefreeze / "15_GATE_C9A_PREFREEZE_DECISION.json"
    manifest_path = prefreeze / "01_INPUT_SHA256_MANIFEST.csv"
    integrity_path = prefreeze / "17_FILE_INTEGRITY_MANIFEST.csv"
    for path in (decision_path, manifest_path, integrity_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    if decision.get("decision") != "PASS_C9A_PREFREEZE_OUTCOME_UNLOCK_AUTHORIZED":
        raise RuntimeError(
            "Outcome unlock prohibited by C9A decision: "
            f"{decision.get('decision')}"
        )
    if not decision.get("outcome_unlock_authorized"):
        raise RuntimeError("C9A outcome_unlock_authorized is false")
    input_manifest = pd.read_csv(manifest_path)
    for row in input_manifest.itertuples(index=False):
        path = Path(row.path)
        if not path.is_absolute():
            path = project_root / path
        if not path.is_file():
            raise FileNotFoundError(path)
        observed = sha256_file(path)
        if observed != row.sha256:
            raise RuntimeError(f"Input changed after C9A prefreeze: {path}")
    integrity = pd.read_csv(integrity_path)
    prediction = prefreeze / "10_CELL_PREDICTIONS_LOCAL.csv.gz"
    frozen_prediction = integrity.loc[
        integrity["filename"].eq(prediction.name), "sha256"
    ]
    if len(frozen_prediction) != 1:
        raise RuntimeError("C9A integrity manifest lacks a unique per-cell prediction hash")
    if sha256_file(prediction) != frozen_prediction.iloc[0]:
        raise RuntimeError("Per-cell predictions changed after outcome freeze")
    return decision


def load_metadata(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metadata = pd.read_csv(path)
    required = {"index", "IDs", "Names", "SLEDAI", "subclusters"}
    missing = required - set(metadata.columns)
    if missing:
        raise RuntimeError(f"Protected metadata is missing columns: {sorted(missing)}")
    metadata = metadata.rename(
        columns={
            "IDs": "sample_id",
            "Names": "donor_name",
            "SLEDAI": "sledai",
            "subclusters": "source_label",
        }
    )
    metadata["sample_id"] = metadata["sample_id"].astype(str)
    metadata["barcode_core"] = metadata["index"].astype(str).str.split("-").str[0]
    metadata["donor_name"] = metadata["donor_name"].astype(str)
    metadata["source_label"] = metadata["source_label"].astype(str)
    if metadata.duplicated(["sample_id", "barcode_core"]).any():
        raise RuntimeError("Protected metadata has duplicate sample/barcode keys")
    uniqueness = metadata.groupby("sample_id", observed=True).agg(
        donor_names=("donor_name", "nunique"),
        sledai_values=("sledai", "nunique"),
    )
    if (uniqueness["donor_names"] != 1).any():
        raise RuntimeError("A GSE135779 sample maps to multiple donor names")
    sample_info = (
        metadata.groupby("sample_id", observed=True)
        .agg(donor_name=("donor_name", "first"), sledai=("sledai", "first"))
        .reset_index()
    )
    sample_info["cohort"] = np.where(
        sample_info["donor_name"].str.startswith("a"),
        "adult",
        np.where(sample_info["donor_name"].str.startswith("c"), "childhood", "unknown"),
    )
    sample_info["disease_group"] = np.where(
        sample_info["donor_name"].str.upper().str.contains("SLE"), "SLE", "HC"
    )
    if (sample_info["cohort"] == "unknown").any():
        raise RuntimeError("Unknown cohort prefix in protected metadata")
    if sample_info["donor_name"].duplicated().any():
        raise RuntimeError("A donor name maps to multiple sample IDs")
    return metadata, sample_info


def join_and_audit(
    predictions: pd.DataFrame,
    metadata: pd.DataFrame,
    sample_info: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, bool]]:
    if predictions.duplicated(["sample_id", "barcode_core"]).any():
        raise RuntimeError("Predictions have duplicate sample/barcode keys")
    sample_join = predictions[["sample_id"]].drop_duplicates().merge(
        sample_info,
        on="sample_id",
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    all_samples_joined = bool(sample_join["_merge"].eq("both").all())
    if not all_samples_joined:
        missing = sample_join.loc[sample_join["_merge"].ne("both"), "sample_id"].tolist()
        raise RuntimeError(f"Predicted samples lack outcome metadata: {missing}")
    cells = predictions.merge(
        metadata[["sample_id", "barcode_core", "source_label"]],
        on=["sample_id", "barcode_core"],
        how="left",
        validate="one_to_one",
        indicator="source_join",
    )
    cells = cells.merge(
        sample_info,
        on="sample_id",
        how="left",
        validate="many_to_one",
    )
    cells["source_label_known"] = cells["source_join"].eq("both")
    upper = cells["source_label"].fillna("").str.upper()
    cells["source_B_lineage"] = upper.str.startswith("B-") | upper.str.startswith("PC-")
    reconciliation = (
        cells.groupby("sample_id", observed=True)
        .agg(
            matrix_cells=("barcode_core", "size"),
            metadata_matched_cells=("source_label_known", "sum"),
            qc_pass_cells=("qc_pass", "sum"),
            source_B_lineage_cells=("source_B_lineage", "sum"),
            donor_name=("donor_name", "first"),
            cohort=("cohort", "first"),
            disease_group=("disease_group", "first"),
        )
        .reset_index()
    )
    reconciliation["metadata_match_fraction"] = (
        reconciliation["metadata_matched_cells"] / reconciliation["matrix_cells"]
    )
    checks = {
        "prediction_keys_unique": True,
        "metadata_keys_unique": True,
        "sample_join_one_to_one": all_samples_joined,
        "outcome_join_complete_by_sample": bool(cells["disease_group"].notna().all()),
        "cohort_join_complete": bool(cells["cohort"].notna().all()),
    }
    return cells, reconciliation, checks


def selection_and_mapping_audit(cells: pd.DataFrame) -> pd.DataFrame:
    qc = bool_series(cells["qc_pass"])
    source_known = bool_series(cells["source_label_known"])
    source_b = bool_series(cells["source_B_lineage"])
    rows = []
    for selection_name, selection_column in SELECTIONS.items():
        selected = bool_series(cells[selection_column]) & qc
        denominator = qc & source_known & source_b
        recovered = denominator & selected
        known_selected = selected & source_known
        contaminated = known_selected & ~source_b
        for mapper_name, mapper in MAPPERS.items():
            confident = bool_series(cells[mapper["confident"]])
            rows.append(
                {
                    "selection": selection_name,
                    "mapper": mapper_name,
                    "qc_cells": int(qc.sum()),
                    "selected_cells": int(selected.sum()),
                    "source_B_denominator": int(denominator.sum()),
                    "source_B_recovered": int(recovered.sum()),
                    "source_B_recovery": float(recovered.sum() / max(1, denominator.sum())),
                    "selected_with_source_label": int(known_selected.sum()),
                    "selected_non_B_source_label": int(contaminated.sum()),
                    "source_label_contamination": float(
                        contaminated.sum() / max(1, known_selected.sum())
                    ),
                    "source_label_unknown_fraction_selected": float(
                        (selected & ~source_known).sum() / max(1, selected.sum())
                    ),
                    "confident_cells": int((selected & confident).sum()),
                    "confident_fraction_selected": float(
                        (selected & confident).sum() / max(1, selected.sum())
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_donor_table(cells: pd.DataFrame) -> pd.DataFrame:
    rows = []
    qc = bool_series(cells["qc_pass"])
    program_columns = [f"program_{program}" for program in PRIMARY_PROGRAMS]
    missing = [column for column in program_columns if column not in cells]
    if missing:
        raise RuntimeError(f"Frozen program scores are missing: {missing}")
    for selection_name, selection_column in SELECTIONS.items():
        selection = bool_series(cells[selection_column]) & qc
        for mapper_name, mapper in MAPPERS.items():
            confident = bool_series(cells[mapper["confident"]])
            predicted_conv = cells[mapper["prediction"]].eq("B_CONV")
            predicted_asc = cells[mapper["prediction"]].eq("B_ASC")
            eligible_conv = selection & confident & predicted_conv
            eligible_asc = selection & confident & predicted_asc
            working = cells.loc[
                eligible_conv,
                [
                    "sample_id",
                    "donor_name",
                    "cohort",
                    "disease_group",
                    *program_columns,
                ],
            ].copy()
            if working.empty:
                continue
            summary = (
                working.groupby(
                    ["sample_id", "donor_name", "cohort", "disease_group"],
                    observed=True,
                )
                .agg(
                    B_CONV_cells=("sample_id", "size"),
                    **{column: (column, "mean") for column in program_columns},
                )
                .reset_index()
            )
            asc_counts = (
                cells.loc[eligible_asc]
                .groupby("sample_id", observed=True)
                .size()
                .rename("B_ASC_cells")
            )
            summary["B_ASC_cells"] = summary["sample_id"].map(asc_counts).fillna(0).astype(int)
            summary["B_ASC_fraction"] = summary["B_ASC_cells"] / (
                summary["B_CONV_cells"] + summary["B_ASC_cells"]
            )
            summary.insert(0, "mapper", mapper_name)
            summary.insert(0, "selection", selection_name)
            summary["minimum_B_CONV_cells"] = MINIMUM_B_CONV_CELLS
            summary["eligible_minimum_cells"] = (
                summary["B_CONV_cells"] >= MINIMUM_B_CONV_CELLS
            )
            rows.append(summary)
    if not rows:
        raise RuntimeError("No donor-level B_CONV table could be constructed")
    return pd.concat(rows, ignore_index=True)


def test_programs(donors: pd.DataFrame) -> pd.DataFrame:
    rows = []
    strata = {
        "childhood": donors["cohort"].eq("childhood"),
        "adult": donors["cohort"].eq("adult"),
        "combined": donors["cohort"].isin(["childhood", "adult"]),
    }
    for selection_name in SELECTIONS:
        for mapper_name in MAPPERS:
            base = donors.loc[
                donors["selection"].eq(selection_name)
                & donors["mapper"].eq(mapper_name)
                & donors["eligible_minimum_cells"]
            ]
            for stratum, _ in strata.items():
                if stratum == "combined":
                    work = base.copy()
                else:
                    work = base.loc[base["cohort"].eq(stratum)].copy()
                for program in PRIMARY_PROGRAMS:
                    column = f"program_{program}"
                    exposed = work.loc[work["disease_group"].eq("SLE"), column].dropna().to_numpy()
                    reference = work.loc[work["disease_group"].eq("HC"), column].dropna().to_numpy()
                    if len(exposed) and len(reference):
                        test = mannwhitneyu(exposed, reference, alternative="two-sided")
                        pvalue = float(test.pvalue)
                        statistic = float(test.statistic)
                        effect = float(exposed.mean() - reference.mean())
                        ci_low, ci_high = bootstrap_mean_difference(exposed, reference)
                    else:
                        pvalue = np.nan
                        statistic = np.nan
                        effect = np.nan
                        ci_low = np.nan
                        ci_high = np.nan
                    rows.append(
                        {
                            "selection": selection_name,
                            "mapper": mapper_name,
                            "stratum": stratum,
                            "program_id": program,
                            "n_HC": len(reference),
                            "n_SLE": len(exposed),
                            "mean_HC": float(reference.mean()) if len(reference) else np.nan,
                            "mean_SLE": float(exposed.mean()) if len(exposed) else np.nan,
                            "effect_SLE_minus_HC": effect,
                            "bootstrap_ci_low": ci_low,
                            "bootstrap_ci_high": ci_high,
                            "mannwhitney_u": statistic,
                            "pvalue": pvalue,
                        }
                    )
    results = pd.DataFrame(rows)
    results["qvalue"] = np.nan
    for _, indices in results.groupby(
        ["selection", "mapper", "stratum"], observed=True
    ).groups.items():
        results.loc[indices, "qvalue"] = bh_fdr(results.loc[indices, "pvalue"])
    return results


def leave_one_donor_out(donors: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mapper_name in MAPPERS:
        base = donors.loc[
            donors["selection"].eq("cluster_primary")
            & donors["mapper"].eq(mapper_name)
            & donors["eligible_minimum_cells"]
            & donors["cohort"].eq("childhood")
        ].copy()
        column = "program_IFN_ISG"
        for excluded in base["donor_name"]:
            work = base.loc[base["donor_name"].ne(excluded)]
            exposed = work.loc[work["disease_group"].eq("SLE"), column]
            reference = work.loc[work["disease_group"].eq("HC"), column]
            effect = (
                float(exposed.mean() - reference.mean())
                if len(exposed) and len(reference)
                else np.nan
            )
            rows.append(
                {
                    "mapper": mapper_name,
                    "excluded_donor": excluded,
                    "excluded_group": base.loc[
                        base["donor_name"].eq(excluded), "disease_group"
                    ].iloc[0],
                    "remaining_HC": len(reference),
                    "remaining_SLE": len(exposed),
                    "effect_SLE_minus_HC": effect,
                    "direction_positive": bool(effect > 0) if np.isfinite(effect) else False,
                }
            )
    return pd.DataFrame(rows)


def make_figure(
    output: Path,
    selection_audit: pd.DataFrame,
    cv: pd.DataFrame,
    donors: pd.DataFrame,
) -> pd.DataFrame:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )
    colors = {"HC": "#2878B5", "SLE": "#C44536"}
    fig, axes = plt.subplots(1, 3, figsize=(7.08, 2.35), constrained_layout=True)

    primary = selection_audit.loc[
        selection_audit["selection"].eq("cluster_primary")
    ].set_index("mapper")
    metrics = ["source_B_recovery", "confident_fraction_selected"]
    x = np.arange(len(MAPPERS))
    width = 0.32
    for offset, metric, label, color in zip(
        (-width / 2, width / 2),
        metrics,
        ("Source-B recovery", "Confident mapping"),
        ("#3A7D44", "#6C5B7B"),
    ):
        axes[0].bar(
            x + offset,
            primary.loc[list(MAPPERS), metric],
            width,
            color=color,
            label=label,
        )
    axes[0].axhline(0.8, color="#555555", linestyle="--", linewidth=0.7)
    axes[0].set_xticks(x, ["Elastic net", "Centroid"])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("Fraction")
    axes[0].legend(frameon=False, fontsize=6, loc="lower right")
    axes[0].set_title("Selection and mapping audit", fontsize=8)

    cv_summary = (
        cv.groupby("mapper", observed=True)["balanced_accuracy"]
        .agg(["mean", "min", "max"])
        .reindex(list(MAPPERS))
    )
    axes[1].errorbar(
        x,
        cv_summary["mean"],
        yerr=np.vstack(
            [
                cv_summary["mean"] - cv_summary["min"],
                cv_summary["max"] - cv_summary["mean"],
            ]
        ),
        fmt="o",
        color="#222222",
        ecolor="#777777",
        capsize=2,
        markersize=4,
    )
    axes[1].axhline(0.9, color="#555555", linestyle="--", linewidth=0.7)
    axes[1].set_xticks(x, ["Elastic net", "Centroid"])
    axes[1].set_ylim(0.5, 1.02)
    axes[1].set_ylabel("Balanced accuracy")
    axes[1].set_title("Donor-grouped reference CV", fontsize=8)

    plot_data = donors.loc[
        donors["selection"].eq("cluster_primary")
        & donors["eligible_minimum_cells"]
        & donors["cohort"].eq("childhood")
    ].copy()
    positions = {
        ("elastic_net", "HC"): 0,
        ("elastic_net", "SLE"): 1,
        ("nearest_centroid", "HC"): 3,
        ("nearest_centroid", "SLE"): 4,
    }
    rng = np.random.default_rng(20260828)
    for (mapper, group), position in positions.items():
        values = plot_data.loc[
            plot_data["mapper"].eq(mapper) & plot_data["disease_group"].eq(group),
            "program_IFN_ISG",
        ].to_numpy()
        jitter = rng.uniform(-0.10, 0.10, size=len(values))
        axes[2].scatter(
            np.full(len(values), position) + jitter,
            values,
            s=12,
            color=colors[group],
            edgecolor="white",
            linewidth=0.3,
            alpha=0.9,
        )
        if len(values):
            axes[2].plot(
                [position - 0.20, position + 0.20],
                [np.mean(values), np.mean(values)],
                color="#111111",
                linewidth=1.2,
            )
    axes[2].set_xticks([0.5, 3.5], ["Elastic net", "Centroid"])
    axes[2].set_ylabel("Mean IFN/ISG score")
    axes[2].set_title("Childhood B_CONV donors", fontsize=8)
    axes[2].legend(
        handles=[
            Line2D([0], [0], marker="o", linestyle="none", color=colors["HC"], label="HC", markersize=4),
            Line2D([0], [0], marker="o", linestyle="none", color=colors["SLE"], label="SLE", markersize=4),
        ],
        frameon=False,
        fontsize=6,
        loc="upper left",
    )
    for axis, label in zip(axes, "abc"):
        axis.text(
            -0.17,
            1.08,
            label,
            transform=axis.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
        )
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)

    for suffix in ("pdf", "svg", "png"):
        fig.savefig(
            output / f"25_GATE_C9_LABEL_AGNOSTIC_VALIDATION_FIGURE.{suffix}",
            dpi=600 if suffix == "png" else None,
            bbox_inches="tight",
        )
    plt.close(fig)
    svg_path = output / "25_GATE_C9_LABEL_AGNOSTIC_VALIDATION_FIGURE.svg"
    svg_text = svg_path.read_text(encoding="utf-8")
    write_text_lf(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        svg_path,
    )

    source_rows = []
    for row in selection_audit.itertuples(index=False):
        source_rows.append(
            {
                "panel": "a",
                "selection": row.selection,
                "mapper": row.mapper,
                "metric": "source_B_recovery",
                "value": row.source_B_recovery,
            }
        )
        source_rows.append(
            {
                "panel": "a",
                "selection": row.selection,
                "mapper": row.mapper,
                "metric": "confident_fraction_selected",
                "value": row.confident_fraction_selected,
            }
        )
    for row in cv.itertuples(index=False):
        source_rows.append(
            {
                "panel": "b",
                "mapper": row.mapper,
                "fold": row.fold,
                "metric": "balanced_accuracy",
                "value": row.balanced_accuracy,
            }
        )
    for row in plot_data.itertuples(index=False):
        source_rows.append(
            {
                "panel": "c",
                "selection": row.selection,
                "mapper": row.mapper,
                "sample_id": row.sample_id,
                "donor_name": row.donor_name,
                "disease_group": row.disease_group,
                "metric": "program_IFN_ISG",
                "value": row.program_IFN_ISG,
            }
        )
    return pd.DataFrame(source_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefreeze-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    prefreeze = Path(args.prefreeze_dir).resolve()
    project_root = Path(args.project_root).resolve()
    output = Path(args.output_dir).resolve() if args.output_dir else prefreeze
    output.mkdir(parents=True, exist_ok=True)
    metadata_path = Path(args.metadata).resolve()
    if not metadata_path.is_file():
        raise FileNotFoundError(metadata_path)

    decision = verify_prefreeze(prefreeze, project_root)
    unlock_log = {
        "created_at": now_iso(),
        "status": "OUTCOME_METADATA_UNLOCKED_AFTER_C9A_PASS",
        "c9a_decision": decision["decision"],
        "c9a_decision_sha256": sha256_file(
            prefreeze / "15_GATE_C9A_PREFREEZE_DECISION.json"
        ),
        "prediction_sha256": sha256_file(
            prefreeze / "10_CELL_PREDICTIONS_LOCAL.csv.gz"
        ),
        "metadata_path": metadata_path.relative_to(project_root).as_posix(),
        "metadata_sha256": sha256_file(metadata_path),
        "threshold_changes_after_unlock": False,
        "source_labels_role": "post hoc recovery and contamination audit only",
        "outcome_role": "frozen donor-level program tests only",
    }
    write_json(unlock_log, output / "18_OUTCOME_UNLOCK_LOG.json")

    predictions = pd.read_csv(
        prefreeze / "10_CELL_PREDICTIONS_LOCAL.csv.gz",
        low_memory=False,
    )
    for column in (
        "qc_pass",
        "cluster_selected_B",
        "cell_margin_selected_B",
        "elastic_confident",
        "centroid_confident",
    ):
        predictions[column] = bool_series(predictions[column])
    metadata, sample_info = load_metadata(metadata_path)
    cells, reconciliation, join_checks = join_and_audit(
        predictions, metadata, sample_info
    )
    selection_audit = selection_and_mapping_audit(cells)
    donors = build_donor_table(cells)
    program_results = test_programs(donors)
    loo = leave_one_donor_out(donors)

    write_csv(reconciliation, output / "19_SAMPLE_CELL_RECONCILIATION.csv")
    write_csv(selection_audit, output / "20_SELECTION_MAPPING_POSTHOC_AUDIT.csv")
    write_csv(donors, output / "21_FROZEN_DONOR_PROGRAM_SCORES.csv")
    write_csv(program_results, output / "22_COMPLETE_PROGRAM_STATISTICS.csv")
    write_csv(loo, output / "23_PRIMARY_IFN_DONOR_LOO.csv")

    source_label_summary = (
        cells.loc[bool_series(cells["qc_pass"])]
        .groupby("source_label", dropna=False, observed=True)
        .agg(
            qc_cells=("barcode_core", "size"),
            cluster_selected_cells=("cluster_selected_B", "sum"),
            margin_selected_cells=("cell_margin_selected_B", "sum"),
        )
        .reset_index()
        .sort_values("qc_cells", ascending=False)
    )
    write_csv(source_label_summary, output / "24_SOURCE_LABEL_SELECTION_AUDIT.csv")

    cv = pd.read_csv(prefreeze / "06_MAPPER_DONOR_GROUPED_CV.csv")
    chosen_alpha = float(decision["reference_model"]["chosen_alpha"])
    chosen_parameter = f"alpha={chosen_alpha:g};l1_ratio=0.5"
    cv_figure = cv.loc[
        cv["mapper"].eq("nearest_centroid")
        | (cv["mapper"].eq("elastic_net") & cv["parameter"].eq(chosen_parameter))
    ].copy()
    figure_source = make_figure(output, selection_audit, cv_figure, donors)
    write_csv(figure_source, output / "26_GATE_C9_FIGURE_SOURCE_DATA.csv")

    primary_audit = selection_audit.loc[
        selection_audit["selection"].eq("cluster_primary")
    ].set_index("mapper")
    primary_results = program_results.loc[
        program_results["selection"].eq("cluster_primary")
        & program_results["stratum"].eq("childhood")
        & program_results["program_id"].eq("IFN_ISG")
    ].set_index("mapper")
    loo_summary = loo.groupby("mapper", observed=True).agg(
        minimum_LOO_effect=("effect_SLE_minus_HC", "min"),
        all_LOO_positive=("direction_positive", "all"),
    )
    checks = {
        **join_checks,
        "source_B_recovery_at_least_80pct": bool(
            primary_audit["source_B_recovery"].min() >= 0.80
        ),
        "source_label_contamination_at_most_10pct": bool(
            primary_audit["source_label_contamination"].max() <= 0.10
        ),
        "mapping_confidence_at_least_80pct": bool(
            primary_audit["confident_fraction_selected"].min() >= 0.80
        ),
        "both_mappers_positive_childhood_IFN": bool(
            (primary_results["effect_SLE_minus_HC"] > 0).all()
            and len(primary_results) == 2
        ),
        "elastic_net_IFN_q_below_0_05": bool(
            primary_results.loc["elastic_net", "qvalue"] < 0.05
        )
        if "elastic_net" in primary_results.index
        else False,
        "no_single_donor_reverses_direction": bool(
            loo_summary["all_LOO_positive"].all() and len(loo_summary) == 2
        ),
        "minimum_50_B_CONV_cells_applied": bool(
            donors.loc[donors["eligible_minimum_cells"], "B_CONV_cells"].min()
            >= MINIMUM_B_CONV_CELLS
        ),
    }
    direction_failure = not checks["both_mappers_positive_childhood_IFN"]
    donor_dominated = not checks["no_single_donor_reverses_direction"]
    supportive = all(checks.values())
    if supportive:
        final_decision = "PASS_C9_LABEL_AGNOSTIC_EXTERNAL_SUPPORT"
        interpretation = (
            "The source-label-defined external IFN/ISG replication is supported by a "
            "fully label-agnostic B-lineage selection and broad-state mapping sensitivity."
        )
    elif direction_failure or donor_dominated:
        final_decision = "NO_GO_C9_LABEL_AGNOSTIC_EXTERNAL_SUPPORT"
        interpretation = (
            "The label-agnostic analysis is non-supportive because mapper direction or "
            "leave-one-donor robustness failed. Retain source-label-defined validation only."
        )
    else:
        final_decision = "HOLD_C9_DIRECTIONAL_ROBUSTNESS_ONLY"
        interpretation = (
            "Direction is retained but at least one prespecified significance or quality "
            "threshold failed. Do not strengthen the title or abstract."
        )

    result_payload = {
        "created_at": now_iso(),
        "decision": final_decision,
        "c9a_prefreeze_decision": decision["decision"],
        "threshold_changes_after_unlock": False,
        "minimum_B_CONV_cells_per_donor": MINIMUM_B_CONV_CELLS,
        "primary_results": primary_results.reset_index().to_dict(orient="records"),
        "primary_quality": primary_audit.reset_index().to_dict(orient="records"),
        "leave_one_donor_out": loo_summary.reset_index().to_dict(orient="records"),
        "checks": checks,
        "interpretation": interpretation,
        "manuscript_scope": (
            "supplementary robustness evidence; cannot convert formal R1 identity HOLD to PASS"
        ),
    }
    write_json(result_payload, output / "27_GATE_C9_ADVISOR_DECISION.json")

    report = [
        "# Gate C9 label-agnostic GSE135779 advisor review",
        "",
        f"**Decision:** `{final_decision}`",
        "",
        "## Frozen execution",
        "",
        f"- C9A authorization: `{decision['decision']}`.",
        "- Protected metadata were joined only after input and per-cell prediction hashes were reverified.",
        "- No selection, mapper, confidence, minimum-cell or program threshold changed after unlock.",
        f"- Minimum confidently mapped B_CONV support: {MINIMUM_B_CONV_CELLS} cells per donor/sample.",
        "",
        "## Primary childhood IFN/ISG result",
        "",
    ]
    for mapper, row in primary_results.iterrows():
        report.append(
            f"- {mapper}: n={int(row['n_HC'])} HC and {int(row['n_SLE'])} SLE; "
            f"effect={row['effect_SLE_minus_HC']:.4f}; 95% bootstrap CI "
            f"{row['bootstrap_ci_low']:.4f} to {row['bootstrap_ci_high']:.4f}; "
            f"P={row['pvalue']:.3g}; q={row['qvalue']:.3g}."
        )
    report.extend(["", "## Selection and mapping audit", ""])
    for mapper, row in primary_audit.iterrows():
        report.append(
            f"- {mapper}: source-B recovery {row['source_B_recovery']:.1%}; "
            f"non-B contamination {row['source_label_contamination']:.1%}; "
            f"confident assignment {row['confident_fraction_selected']:.1%}."
        )
    report.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            interpretation,
            "",
            "This sensitivity can strengthen the external-validation methods and supplementary "
            "evidence only. It does not repair the formal R1 state-overlap HOLD and does not "
            "authorize a discrete IFN-high B-cell subtype claim.",
        ]
    )
    write_text_lf(
        "\n".join(report) + "\n",
        output / "28_GATE_C9_ADVISOR_REVIEW.md",
    )
    manifest = integrity_manifest(output, excluded={"29_FILE_INTEGRITY_MANIFEST.csv"})
    write_csv(manifest, output / "29_FILE_INTEGRITY_MANIFEST.csv")
    print(json.dumps(result_payload, indent=2, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
