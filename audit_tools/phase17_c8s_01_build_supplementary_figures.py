#!/usr/bin/env python3
"""Build reviewer-facing Gate C8S supplementary figures from frozen outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np
import pandas as pd


COLORS = {
    "blue": "#2C6EAD",
    "red": "#C43C39",
    "teal": "#238B8E",
    "gold": "#E69F00",
    "purple": "#7B6BA8",
    "green": "#009E73",
    "grey": "#777777",
    "light": "#C8CED4",
    "dark": "#222222",
}
ASSERTIONS: list[dict[str, Any]] = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("phase17_v7/gateC8S/20260821_supplementary_traceability_freeze"),
    )
    return parser.parse_args()


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "axes.titlesize": 7.5,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.3,
            "ytick.labelsize": 6.3,
            "legend.fontsize": 6,
            "axes.linewidth": 0.7,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def assert_equal(name: str, actual: Any, expected: Any) -> None:
    passed = actual == expected
    ASSERTIONS.append({"check": name, "actual": actual, "expected": expected, "pass": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, observed {actual!r}")


def assert_true(name: str, condition: bool, detail: str) -> None:
    passed = bool(condition)
    ASSERTIONS.append({"check": name, "actual": detail, "expected": "true", "pass": passed})
    if not passed:
        raise AssertionError(f"{name}: {detail}")


def style_axis(axis: plt.Axes) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(direction="out")


def panel_label(axis: plt.Axes, label: str, x: float = -0.12, y: float = 1.06) -> None:
    axis.text(x, y, label, transform=axis.transAxes, fontsize=8, fontweight="bold", va="bottom", ha="left")


def write_source(path: Path, panels: list[pd.DataFrame]) -> None:
    data = pd.concat(panels, ignore_index=True, sort=False)
    data.to_csv(path, index=False, lineterminator="\n")


def save_figure(figure: plt.Figure, figure_dir: Path, basename: str) -> None:
    from publication_style_contract import apply_publication_style
    apply_publication_style(figure)
    visible_sizes = [
        float(item.get_fontsize())
        for item in figure.findobj(match=Text)
        if item.get_visible() and item.get_text().strip()
    ]
    minimum = min(visible_sizes)
    assert_true(f"{basename}.minimum_visible_font_pt", minimum >= 5.0, f"{minimum:.2f} pt")
    figure.savefig(figure_dir / f"{basename}.pdf")
    figure.savefig(figure_dir / f"{basename}.png", dpi=600)
    plt.close(figure)


def forest(axis: plt.Axes, frame: pd.DataFrame, label_col: str, effect: str, low: str, high: str, colors: list[str]) -> None:
    y = np.arange(len(frame))[::-1]
    for index, (_, row) in enumerate(frame.iterrows()):
        axis.errorbar(
            float(row[effect]),
            y[index],
            xerr=[[float(row[effect]) - float(row[low])], [float(row[high]) - float(row[effect])]],
            fmt="o",
            color=colors[index],
            ms=3.2,
            lw=0.8,
            capsize=1.5,
        )
    axis.axvline(0, color=COLORS["grey"], lw=0.6, ls="--")
    axis.set_yticks(y, frame[label_col])
    style_axis(axis)


def build_s1(root: Path, figure_dir: Path, source_dir: Path) -> None:
    gate = root / "phase17_v7/gateC2B1/20260810_171000_full_library_doublets"
    retention = read_csv(gate / "02_full_qc_retention_summary.csv")
    libraries = read_csv(gate / "05_full_library_doublet_summary.csv")
    decision = json.loads((gate / "17_GATE_C2B1_DECISION.json").read_text(encoding="utf-8"))
    assert_equal("S1.hard_qc_cells", int(retention["n_eligible"].sum()), 150402)
    assert_equal("S1.library_runs", len(libraries), 88)
    assert_equal("S1.library_runs_ok", int(libraries["status"].eq("ok").sum()), 88)
    assert_equal("S1.residual_risk_calls", int(libraries["predicted_doublets"].sum()), 1972)

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.15), constrained_layout=True)
    labels = [f"C{int(row.Processing_Cohort)} | {'HC' if row.disease == 'normal' else 'SLE'}" for row in retention.itertuples()]
    colors = [COLORS["blue"] if row.disease == "normal" else COLORS["red"] for row in retention.itertuples()]
    axes[0, 0].bar(np.arange(len(retention)), retention["hard_fail_fraction"] * 100, color=colors, width=0.7)
    axes[0, 0].set_xticks(np.arange(len(retention)), labels, rotation=35, ha="right")
    axes[0, 0].set_ylabel("Hard-QC failure (%)")
    axes[0, 0].set_title("Hard-QC retention by cohort and disease", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    scatter = axes[0, 1].scatter(libraries["n_cells"], libraries["predicted_doublet_fraction"] * 100, c=libraries["score_median"], cmap="viridis", s=12, linewidths=0)
    axes[0, 1].set_xlabel("Cells per library")
    axes[0, 1].set_ylabel("Residual-risk calls (%)")
    axes[0, 1].set_title("Library-level residual-risk review", loc="left")
    colorbar = figure.colorbar(scatter, ax=axes[0, 1], fraction=0.05, pad=0.03)
    colorbar.set_label("Median score", fontsize=6)
    colorbar.ax.tick_params(labelsize=5.5)
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    risk = int(decision["automatic_residual_risk_calls"])
    negative = int(decision["cells"]) - risk
    total = negative + risk
    percentages = np.array([negative, risk], dtype=float) / total * 100
    bars = axes[1, 0].bar(
        [0, 1], percentages, color=[COLORS["teal"], COLORS["gold"]], width=0.62
    )
    axes[1, 0].set_xticks([0, 1], ["Risk-negative", "Sensitivity flag"])
    axes[1, 0].set_ylim(0, 108)
    axes[1, 0].set_ylabel("Hard-QC B-lineage cells (%)")
    for bar, pct, count in zip(bars, percentages, [negative, risk]):
        label_inside = pct > 50
        axes[1, 0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() - 5 if label_inside else bar.get_height() + 2,
            f"{pct:.2f}%\n({count:,})",
            ha="center",
            va="top" if label_inside else "bottom",
            fontsize=5.5,
            color="white" if label_inside else COLORS["dark"],
        )
    axes[1, 0].set_title("Hard-QC cell retention", loc="left")
    style_axis(axes[1, 0]); panel_label(axes[1, 0], "c")

    ordered = libraries.sort_values("score_q95").reset_index(drop=True)
    x = np.arange(len(ordered)) + 1
    axes[1, 1].plot(x, ordered["score_median"], color=COLORS["blue"], lw=0.8, label="Median")
    axes[1, 1].plot(x, ordered["score_q95"], color=COLORS["teal"], lw=0.8, label="95th percentile")
    axes[1, 1].plot(x, ordered["threshold"], color=COLORS["red"], lw=0.8, label="Library threshold")
    axes[1, 1].set_xlabel("Libraries ordered by score 95th percentile")
    axes[1, 1].set_ylabel("Residual-risk score")
    axes[1, 1].set_xlim(1, len(ordered) + 18)
    for label, column, color in (
        ("Median", "score_median", COLORS["blue"]),
        ("95th percentile", "score_q95", COLORS["teal"]),
        ("Threshold", "threshold", COLORS["red"]),
    ):
        axes[1, 1].text(
            len(ordered) + 2,
            float(ordered[column].iloc[-1]),
            label,
            color=color,
            va="center",
            ha="left",
        )
    axes[1, 1].set_title("Library-level checkpoint profiles", loc="left")
    style_axis(axes[1, 1]); panel_label(axes[1, 1], "d")

    write_source(
        source_dir / "Supplementary_Figure_S1_source_data.csv",
        [
            retention.assign(panel="a", source_table="hard_qc_retention"),
            libraries.assign(panel="b/d", source_table="library_doublet_summary"),
            pd.DataFrame({"panel": ["c", "c"], "category": ["risk_negative", "sensitivity_flag"], "n_cells": [negative, risk]}),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S1_source_integrity_qc")


def build_s2(root: Path, figure_dir: Path, source_dir: Path) -> None:
    gate = root / "phase17_v7/gateC2B2/20260812_full_representation"
    mixing = read_csv(gate / "10_primary_neighbor_mixing.csv")
    bridge = read_csv(gate / "11_primary_bridge_centroid_distances.csv")
    concordance = read_csv(gate / "14_branch_and_resolution_concordance.csv")
    markers = read_csv(gate / "20_marker_module_by_cluster.csv")
    assert_equal("S2.mixing_rows", len(mixing), 6)
    assert_equal("S2.bridge_rows", len(bridge), 138)
    assert_equal("S2.primary_cells", int(mixing["n_evaluable_cells"].min()), 150402)

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.25), constrained_layout=True)
    field_order = ["library_uuid", "sample_uuid", "Processing_Cohort"]
    field_labels = ["Library", "Sample", "Cohort"]
    x = np.arange(3)
    width = 0.34
    for offset, representation, color, label in [(-width / 2, "unintegrated_pca", COLORS["blue"], "Unintegrated"), (width / 2, "harmony_pca", COLORS["red"], "Harmony")]:
        values = mixing.set_index(["representation", "field"]).loc[[(representation, field) for field in field_order], "mean_same_group_fraction"].to_numpy()
        axes[0, 0].bar(x + offset, values, width=width, color=color, label=label)
    axes[0, 0].set_xticks(x, field_labels)
    axes[0, 0].set_ylabel("Mean same-group neighbour fraction")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].set_title("Technical-neighbourhood concentration", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    representations = ["unintegrated_pca", "harmony_pca"]
    data = [bridge.loc[bridge["representation"].eq(rep), "cosine_centroid_distance"].to_numpy() for rep in representations]
    box = axes[0, 1].boxplot(data, patch_artist=True, widths=0.5, showfliers=False)
    for patch, color in zip(box["boxes"], [COLORS["blue"], COLORS["red"]], strict=True):
        patch.set_facecolor(color); patch.set_alpha(0.55)
    rng = np.random.default_rng(20260821)
    for index, values in enumerate(data, start=1):
        axes[0, 1].scatter(rng.normal(index, 0.045, len(values)), values, s=5, alpha=0.35, color=[COLORS["blue"], COLORS["red"]][index - 1], linewidths=0)
    axes[0, 1].set_xticks([1, 2], ["Unintegrated", "Harmony"])
    axes[0, 1].set_ylabel("Bridge-pair cosine distance")
    axes[0, 1].set_title("Bridge consistency", loc="left")
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    selected = concordance.loc[concordance["comparison"].isin(["primary_all_cells_vs_singlet_sensitivity", "primary_all_cells_vs_isg_excluded"])].copy()
    selected["resolution_numeric"] = pd.to_numeric(selected["resolution"])
    for comparison, label, color, marker in [
        ("primary_all_cells_vs_singlet_sensitivity", "Residual-risk negative", COLORS["teal"], "o"),
        ("primary_all_cells_vs_isg_excluded", "Strong-ISG excluded", COLORS["gold"], "s"),
    ]:
        subset = selected.loc[selected["comparison"].eq(comparison)].sort_values("resolution_numeric")
        axes[1, 0].plot(subset["resolution_numeric"], subset["adjusted_rand_index"], marker=marker, ms=3, lw=0.8, color=color, label=label)
    axes[1, 0].axhline(0.70, color=COLORS["grey"], lw=0.6, ls="--")
    axes[1, 0].axvline(0.4, color="#BBBBBB", lw=0.6, ls=":")
    axes[1, 0].set_xlabel("Leiden resolution")
    axes[1, 0].set_ylabel("Adjusted Rand index")
    axes[1, 0].legend(frameon=False)
    axes[1, 0].set_title("Primary-resolution branch concordance", loc="left")
    style_axis(axes[1, 0]); panel_label(axes[1, 0], "c")

    modules = [item for item in ["B_identity", "naive", "memory", "ASC_UPR", "platelet", "IFN_ISG"] if item in set(markers["module"])]
    pivot = markers.loc[markers["module"].isin(modules)].pivot(index="cluster", columns="module", values="mean_module_log_expression").reindex(columns=modules)
    image = axes[1, 1].imshow(pivot.to_numpy(), aspect="auto", cmap="RdBu_r")
    axes[1, 1].set_xticks(np.arange(len(modules)), modules, rotation=35, ha="right")
    axes[1, 1].set_yticks(np.arange(len(pivot)), [f"Cluster {item}" for item in pivot.index])
    axes[1, 1].set_title("Biological marker-module localization", loc="left")
    colorbar = figure.colorbar(image, ax=axes[1, 1], fraction=0.05, pad=0.03)
    colorbar.set_label("Mean log expression", fontsize=6)
    colorbar.ax.tick_params(labelsize=5.5)
    panel_label(axes[1, 1], "d")

    write_source(
        source_dir / "Supplementary_Figure_S2_source_data.csv",
        [
            mixing.assign(panel="a", source_table="neighbor_mixing"),
            bridge.assign(panel="b", source_table="bridge_centroid_distance"),
            selected.assign(panel="c", source_table="branch_concordance"),
            markers.loc[markers["module"].isin(modules)].assign(panel="d", source_table="marker_modules"),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S2_representation_diagnostics")


def build_s3(root: Path, figure_dir: Path, source_dir: Path) -> None:
    c2b3 = root / "phase17_v7/gateC2B3/20260813_full_neutral_state_freeze"
    c2b4 = root / "phase17_v7/gateC2B4/20260815_two_level_state_repair"
    policy = read_csv(c2b4 / "02_reconstructed_policy_summary.csv")
    cluster_policy = read_csv(c2b3 / "04b_resampling_r04_policy_cluster_summary.csv")
    transitions = read_csv(c2b3 / "02b_resampling_reference_transitions.csv")
    state_summary = read_csv(c2b4 / "04_two_compartment_state_summary.csv")
    assert_equal("S3.resampling_policies", len(policy), 4)
    assert_equal("S3.two_compartment_states", len(state_summary), 2)
    assert_true("S3.two_compartment_minimum_ari", float(policy.loc[policy["n_states"].eq(2), "minimum_mapped_ari"].iloc[0]) >= 0.99, "minimum mapped ARI >= 0.99")

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.25), constrained_layout=True)
    labels = ["5-state", "4-state", "3-state", "2-compartment"]
    x = np.arange(4)
    axes[0, 0].plot(x, policy["median_mapped_ari"], "o", color=COLORS["blue"], label="Median ARI")
    axes[0, 0].plot(x, policy["minimum_mapped_ari"], "D", color=COLORS["gold"], label="Minimum ARI")
    for index, row in policy.iterrows():
        axes[0, 0].plot([index, index], [row["minimum_mapped_ari"], row["median_mapped_ari"]], color=COLORS["light"], lw=1, zorder=0)
    axes[0, 0].axhline(0.90, color=COLORS["grey"], lw=0.6, ls="--")
    axes[0, 0].set_xticks(x, labels, rotation=25, ha="right")
    axes[0, 0].set_ylabel("Mapped adjusted Rand index")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].set_title("Fine partitions fail worst-case stability", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    policy_order = ["five_state", "four_state_platelet_overlay_merged", "three_state_identity_core"]
    offsets = np.linspace(-0.22, 0.22, max(cluster_policy.groupby("policy").size()))
    for index, current in enumerate(policy_order):
        subset = cluster_policy.loc[cluster_policy["policy"].eq(current)]
        axes[0, 1].scatter(np.full(len(subset), index) + offsets[: len(subset)], subset["median_jaccard"], color=COLORS["teal"], s=13, label="Cluster median" if index == 0 else None)
        axes[0, 1].scatter(np.full(len(subset), index) + offsets[: len(subset)], subset["minimum_jaccard"], color=COLORS["red"], marker="x", s=13, label="Cluster minimum" if index == 0 else None)
    axes[0, 1].axhline(0.60, color=COLORS["grey"], lw=0.6, ls="--")
    axes[0, 1].set_xticks(np.arange(3), ["5-state", "4-state", "3-state"])
    axes[0, 1].set_ylabel("State Jaccard")
    axes[0, 1].legend(frameon=False)
    axes[0, 1].set_title("Failure localizes to fine-state membership", loc="left")
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    trans = transitions.loc[pd.to_numeric(transitions["resolution"]).eq(0.4)].copy()
    grouped = trans.groupby(["reference_cluster", "mapped_reference_cluster"], as_index=False)["fraction_of_reference_cluster"].mean()
    pivot = grouped.pivot(index="reference_cluster", columns="mapped_reference_cluster", values="fraction_of_reference_cluster").fillna(0)
    image = axes[1, 0].imshow(pivot.to_numpy(), cmap="Blues", vmin=0, vmax=1, aspect="auto")
    axes[1, 0].set_xticks(np.arange(len(pivot.columns)), [str(item) for item in pivot.columns])
    axes[1, 0].set_yticks(np.arange(len(pivot.index)), [str(item) for item in pivot.index])
    axes[1, 0].set_xlabel("Mapped reference cluster")
    axes[1, 0].set_ylabel("Original reference cluster")
    axes[1, 0].set_title("Mean r=0.4 transition matrix across resamples", loc="left")
    colorbar = figure.colorbar(image, ax=axes[1, 0], fraction=0.05, pad=0.03)
    colorbar.set_label("Mean fraction", fontsize=6); colorbar.ax.tick_params(labelsize=5.5)
    panel_label(axes[1, 0], "c")

    state_labels = ["B_CONV" if int(value) == 0 else "B_ASC" for value in state_summary["reference_state"]]
    y = np.arange(2)[::-1]
    for index, row in state_summary.iterrows():
        axes[1, 1].plot([row["minimum_jaccard"], row["median_jaccard"]], [y[index], y[index]], color=COLORS["teal"], lw=1.1)
        axes[1, 1].plot(row["minimum_jaccard"], y[index], "D", color=COLORS["gold"], ms=3.2)
        axes[1, 1].plot(row["median_jaccard"], y[index], "o", color=COLORS["teal"], ms=3.7)
    axes[1, 1].axvline(0.95, color=COLORS["grey"], lw=0.6, ls="--")
    axes[1, 1].set_yticks(y, state_labels)
    axes[1, 1].set_xlim(0.94, 1.002)
    axes[1, 1].set_xlabel("State Jaccard (minimum to median)")
    axes[1, 1].text(0.02, 0.08, "20/20 disease-blind resamples", transform=axes[1, 1].transAxes, fontsize=6, color="#444444")
    axes[1, 1].set_title("Two-compartment adjudication passes", loc="left")
    style_axis(axes[1, 1]); panel_label(axes[1, 1], "d")

    write_source(
        source_dir / "Supplementary_Figure_S3_source_data.csv",
        [
            policy.assign(panel="a", source_table="policy_summary"),
            cluster_policy.assign(panel="b", source_table="policy_cluster_summary"),
            grouped.assign(panel="c", source_table="mean_reference_transitions"),
            state_summary.assign(panel="d", source_table="two_compartment_state_summary"),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S3_identity_adjudication")


def build_s4(
    root: Path,
    figure_dir: Path,
    source_dir: Path,
    *,
    log_ratio_two_part: bool = False,
) -> None:
    gate = root / "phase17_v7/gateC3A/20260815_frozen_abundance"
    base = read_csv(gate / "02_base_and_nonoverlap_contrasts.csv")
    sensitivity = read_csv(gate / "04_mandatory_sensitivity_contrasts.csv")
    two_part = read_csv(gate / "05_two_part_sensitivity.csv")
    diagnostics = read_csv(gate / "08_model_diagnostics.csv")
    diagnostics_base = diagnostics.loc[diagnostics["variant"].eq("frozen_base50")].copy()
    assert_equal("S4.frozen_composition_contrasts", len(base), 5)
    assert_equal("S4.primary_raw_points", int(base.loc[base["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL") & base["variant"].eq("frozen_base50"), "n_strata"].iloc[0]), 90)
    assert_equal("S4.two_part_rows", len(two_part), 6)

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.25), constrained_layout=True)
    contrast_labels = {"C3A_PRIMARY_C4_MANAGED_VS_NORMAL": "Primary C4", "C3A_VALIDATION_C2_EUROPEAN_FEMALE": "Internal C2", "C3A_SECONDARY_C3_FLARE_VS_NORMAL": "Flare C3"}
    labels = [contrast_labels[value] for value in diagnostics_base["analysis_id"]]
    x = np.arange(len(labels))
    axes[0, 0].bar(x, diagnostics_base["n_strata"], color=COLORS["light"], label="All strata")
    axes[0, 0].bar(x, diagnostics_base["zero_asc_strata"], color=COLORS["gold"], label="Zero ASC")
    axes[0, 0].set_xticks(x, labels)
    axes[0, 0].set_ylabel("Sample-cohort strata")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].set_title("Zero-ASC strata motivate count-aware modeling", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    primary = pd.concat([
        base.loc[base["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL") & base["variant"].eq("frozen_base50")],
        sensitivity.loc[sensitivity["analysis_id"].eq("C3A_PRIMARY_C4_MANAGED_VS_NORMAL")],
    ], ignore_index=True)
    variant_labels = {
        "frozen_base50": "Base >=50",
        "minimum_cells_20": ">=20 cells",
        "minimum_cells_100": ">=100 cells",
        "exclude_explicit_non_b_ct_cov": "Exclude non-B",
        "exclude_residual_doublet_risk": "Risk-negative",
        "exclude_residual_doublet_auto_call": "Risk-negative",
    }
    primary["label"] = primary["variant"].map(variant_labels).fillna(primary["variant"])
    y = np.arange(len(primary))[::-1]
    for index, row in primary.iterrows():
        axes[0, 1].errorbar(row["odds_ratio"], y[index] + 0.10, xerr=[[row["odds_ratio"] - row["ci_low"]], [row["ci_high"] - row["odds_ratio"]]], fmt="o", color=COLORS["blue"], ms=3, lw=0.8, capsize=1.3, label="Observed information" if index == 0 else None)
        axes[0, 1].errorbar(row["odds_ratio"], y[index] - 0.10, xerr=[[row["odds_ratio"] - row["hc1_sandwich_ci_low"]], [row["hc1_sandwich_ci_high"] - row["odds_ratio"]]], fmt="s", color=COLORS["red"], ms=2.8, lw=0.8, capsize=1.3, label="HC1 sandwich" if index == 0 else None)
    axes[0, 1].axvline(1, color=COLORS["grey"], lw=0.6, ls="--")
    axes[0, 1].set_yticks(y, primary["label"])
    axes[0, 1].set_xlim(0.5, 2.05)
    axes[0, 1].set_xlabel("B_ASC relative-abundance odds ratio")
    axes[0, 1].set_title("Primary null is stable to covariance and cell policy", loc="left")
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    for axis, component, title, panel in [
        (axes[1, 0], "ASC presence", "Two-part ASC-presence component", "c"),
        (axes[1, 1], "Positive ASC abundance", "Two-part positive-abundance component", "d"),
    ]:
        subset = two_part.loc[two_part["component"].eq(component)].copy().reset_index(drop=True)
        subset["label"] = subset["analysis_id"].map(contrast_labels)
        y = np.arange(len(subset))[::-1]
        for index, row in subset.iterrows():
            axis.errorbar(row["effect_ratio"], y[index], xerr=[[row["effect_ratio"] - row["ci_low"]], [row["ci_high"] - row["effect_ratio"]]], fmt="o", color=[COLORS["blue"], COLORS["teal"], COLORS["gold"]][index], ms=3.2, lw=0.8, capsize=1.5)
        axis.axvline(1, color=COLORS["grey"], lw=0.6, ls="--")
        axis.set_yticks(y, subset["label"])
        if log_ratio_two_part:
            axis.set_xscale("log")
            if component == "ASC presence":
                ticks = [0.05, 0.2, 1.0, 5.0, 20.0, 60.0]
                axis.set_xlim(0.04, 70.0)
                axis.set_xticks(ticks, ["0.05", "0.2", "1", "5", "20", "60"])
            else:
                ticks = [0.5, 1.0, 2.0, 5.0]
                axis.set_xlim(0.5, 6.5)
                axis.set_xticks(ticks, ["0.5", "1", "2", "5"])
            axis.minorticks_off()
            axis.set_xlabel("Effect ratio (95% CI; log scale)")
        else:
            axis.set_xlabel("Effect ratio (95% CI)")
        axis.set_title(title, loc="left")
        style_axis(axis); panel_label(axis, panel)

    write_source(
        source_dir / "Supplementary_Figure_S4_source_data.csv",
        [
            diagnostics_base.assign(panel="a", source_table="model_diagnostics"),
            primary.assign(panel="b", source_table="primary_covariance_sensitivity"),
            two_part.loc[two_part["component"].eq("ASC presence")].assign(panel="c", source_table="two_part_presence"),
            two_part.loc[two_part["component"].eq("Positive ASC abundance")].assign(panel="d", source_table="two_part_positive_abundance"),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S4_composition_diagnostics")


def build_s5(root: Path, figure_dir: Path, source_dir: Path) -> None:
    gate = root / "phase17_v7/gateC4B/20260815_edger_transcription"
    models = read_csv(gate / "05_MODEL_SUMMARY.csv")
    programs = read_csv(gate / "07_PROGRAM_RESULTS.csv")
    ranked_qc = read_csv(gate / "13_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv")
    assert_equal("S5.model_runs", len(models), 7)
    assert_equal("S5.primary_tested_genes", int(models.loc[models["analysis_name"].eq("primary_base"), "tested_genes"].iloc[0]), 4414)

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.35), constrained_layout=True)
    label_map = {"primary_base": "Primary", "primary_min20": ">=20", "primary_min100": ">=100", "primary_residual_risk_negative": "Risk-negative", "validation_full": "Internal", "validation_nonoverlap": "Nonoverlap", "flare_full": "Flare"}
    labels = [label_map[value] for value in models["analysis_name"]]
    x = np.arange(len(models))
    axes[0, 0].bar(x, models["tested_genes"], color=COLORS["light"], label="Tested")
    axes[0, 0].bar(x, models["fdr_0_05_genes"], color=COLORS["red"], label="BH q<0.05")
    axes[0, 0].set_xticks(x, labels, rotation=35, ha="right")
    axes[0, 0].set_ylabel("Genes")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].set_title("filterByExpr-tested and significant genes", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    axes[0, 1].plot(x, models["common_dispersion"], "o-", color=COLORS["blue"], ms=3.4, lw=0.8, label="Common")
    axes[0, 1].plot(x, models["median_tagwise_dispersion"], "s-", color=COLORS["gold"], ms=3.2, lw=0.8, label="Median tagwise")
    axes[0, 1].set_xticks(x, labels, rotation=35, ha="right")
    axes[0, 1].set_ylabel("Dispersion")
    axes[0, 1].legend(frameon=False, ncol=2, loc="upper left")
    axes[0, 1].set_title("edgeR dispersion diagnostics", loc="left")
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    for metric, color, marker in [("mitochondrial_fraction", COLORS["red"], "o"), ("ribosomal_fraction", COLORS["blue"], "s"), ("hemoglobin_fraction", COLORS["gold"], "^"), ("immunoglobulin_fraction", COLORS["teal"], "D")]:
        axes[1, 0].plot(ranked_qc["rank_cutoff"], ranked_qc[metric] * 100, marker=marker, ms=3, lw=0.8, color=color, label=metric.replace("_fraction", "").capitalize())
    axes[1, 0].set_xlabel("Top-ranked genes")
    axes[1, 0].set_ylabel("Technical-family fraction (%)")
    axes[1, 0].legend(frameon=False, ncol=2)
    axes[1, 0].set_title("Ranked-list technical-family audit", loc="left")
    style_axis(axes[1, 0]); panel_label(axes[1, 0], "c")

    ifn = programs.loc[programs["program_id"].eq("IFN_ISG")].copy()
    ifn["label"] = ifn["analysis_name"].map(label_map)
    forest(axes[1, 1], ifn, "label", "effect", "ci_low", "ci_high", [COLORS["red"] if value.startswith("primary") else COLORS["teal"] if "validation" in value else COLORS["gold"] for value in ifn["analysis_name"]])
    axes[1, 1].set_xlabel("Adjusted IFN/ISG score difference")
    axes[1, 1].set_title("IFN/ISG coherence across frozen model branches", loc="left")
    panel_label(axes[1, 1], "d")

    write_source(
        source_dir / "Supplementary_Figure_S5_source_data.csv",
        [
            models.assign(panel="a/b", source_table="model_summary"),
            ranked_qc.assign(panel="c", source_table="ranked_qc"),
            ifn.assign(panel="d", source_table="ifn_program_results"),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S5_pseudobulk_diagnostics")


def build_s6(root: Path, figure_dir: Path, source_dir: Path) -> None:
    gate = root / "phase17_v7/gateC5B/20260815_gse135779_external_validation"
    models = read_csv(gate / "05_MODEL_SUMMARY.csv")
    programs = read_csv(gate / "07_PROGRAM_RESULTS.csv")
    donor_loo = read_csv(gate / "10_PRIMARY_PROGRAM_DONOR_LOO.csv")
    source_loo = read_csv(gate / "12_SOURCE_LABEL_LOO_PROGRAM_RESULTS.csv")
    assert_equal("S6.external_model_runs", len(models), 5)
    assert_equal("S6.childhood_donors", int(models.loc[models["analysis_name"].eq("childhood_min50"), "n_samples"].iloc[0]), 43)
    assert_equal("S6.source_label_omissions", int(source_loo["omitted_source_label"].nunique()), 8)

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.35), constrained_layout=True)
    label_map = {"childhood_min50": "Childhood", "combined_min50": "Combined >=50", "adult_min50": "Adult", "combined_min20": "Combined >=20", "combined_min100": "Combined >=100"}
    models = models.copy(); models["label"] = models["analysis_name"].map(label_map)
    x = np.arange(len(models))
    axes[0, 0].bar(x, models["reference_n"], color=COLORS["blue"], label="Control")
    axes[0, 0].bar(x, models["exposed_n"], bottom=models["reference_n"], color=COLORS["red"], label="SLE")
    axes[0, 0].set_xticks(x, models["label"], rotation=35, ha="right")
    axes[0, 0].set_ylabel("Donors")
    axes[0, 0].legend(frameon=False)
    axes[0, 0].set_title("External validation support by stratum", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    primary_programs = programs.loc[programs["analysis_name"].eq("childhood_min50") & programs["analysis_family"].eq("primary_confirmatory")].copy()
    primary_programs["label"] = primary_programs["program_id"].map({"NAIVE_TO_MEMORY_AXIS": "Naive-to-memory", "ATYPICAL_LOW_NAIVE_AXIS": "Atypical/low-naive", "APC_HLA": "APC/HLA", "IFN_ISG": "IFN/ISG"})
    forest(axes[0, 1], primary_programs, "label", "effect", "ci_low", "ci_high", [COLORS["blue"], COLORS["purple"], COLORS["teal"], COLORS["red"]])
    axes[0, 1].set_xlabel("Adjusted program-score difference")
    axes[0, 1].set_title("Childhood primary program family", loc="left")
    panel_label(axes[0, 1], "b")

    source_ifn = source_loo.loc[source_loo["program_id"].eq("IFN_ISG")].sort_values("omitted_source_label")
    y = np.arange(len(source_ifn))[::-1]
    for index, row in source_ifn.iterrows():
        axes[1, 0].errorbar(row["effect"], y[list(source_ifn.index).index(index)], xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]], fmt="o", color=COLORS["teal"], ms=3, lw=0.8, capsize=1.4)
    axes[1, 0].axvline(0, color=COLORS["grey"], lw=0.6, ls="--")
    axes[1, 0].set_yticks(y, source_ifn["omitted_source_label"])
    axes[1, 0].set_xlabel("IFN/ISG effect after source-label omission")
    axes[1, 0].set_title("Mapping-label omission sensitivity", loc="left")
    style_axis(axes[1, 0]); panel_label(axes[1, 0], "c")

    donor_primary = donor_loo.loc[donor_loo["analysis_family"].eq("primary_confirmatory")].copy()
    donor_primary["label"] = donor_primary["program_id"].map({"NAIVE_TO_MEMORY_AXIS": "Naive-to-memory", "ATYPICAL_LOW_NAIVE_AXIS": "Atypical/low-naive", "APC_HLA": "APC/HLA", "IFN_ISG": "IFN/ISG"})
    y = np.arange(len(donor_primary))[::-1]
    for index, row in donor_primary.iterrows():
        y_value = y[list(donor_primary.index).index(index)]
        axes[1, 1].plot([row["loo_min_effect"], row["loo_max_effect"]], [y_value, y_value], color=COLORS["light"], lw=1.2)
        axes[1, 1].plot(row["full_effect"], y_value, "o", color=COLORS["red"] if row["program_id"] == "IFN_ISG" else COLORS["purple"], ms=3.4)
    axes[1, 1].axvline(0, color=COLORS["grey"], lw=0.6, ls="--")
    axes[1, 1].set_yticks(y, donor_primary["label"])
    axes[1, 1].set_xlabel("Full effect and donor-deletion range")
    axes[1, 1].set_title("Childhood donor influence", loc="left")
    style_axis(axes[1, 1]); panel_label(axes[1, 1], "d")

    write_source(
        source_dir / "Supplementary_Figure_S6_source_data.csv",
        [
            models.assign(panel="a", source_table="external_model_summary"),
            primary_programs.assign(panel="b", source_table="childhood_programs"),
            source_ifn.assign(panel="c", source_table="source_label_loo"),
            donor_primary.assign(panel="d", source_table="donor_loo"),
        ],
    )
    save_figure(figure, figure_dir, "Supplementary_Figure_S6_external_validation_diagnostics")


def build_s7(root: Path, figure_dir: Path, source_dir: Path) -> None:
    sensitivity = read_csv(root / "phase17_v7/gateC8R/20260820_pre_submission_repair/03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv")
    assert_equal("S7.core_tests", len(sensitivity), 6)
    assert_equal("S7.camera_bh_significant", int((sensitivity["camera_q_core6"] < 0.05).sum()), 5)
    assert_equal("S7.fry_bh_significant", int((sensitivity["fry_q_core6"] < 0.05).sum()), 6)
    assert_equal("S7.target_counts", "/".join(str(int(value)) for value in sensitivity["matched_signed_targets"]), "98/14/129/19/161/20")

    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.25), constrained_layout=True)
    labels = [f"{row.contrast.replace('gse174188_', '').replace('gse135779_', '')}\n{row.regulator}" for row in sensitivity.itertuples()]
    compact_labels = [
        f"{ {'primary': 'D', 'internal_nonoverlap': 'N', 'childhood': 'C'}[row.contrast.replace('gse174188_', '').replace('gse135779_', '')] }\n{row.regulator}"
        for row in sensitivity.itertuples()
    ]
    colors = [COLORS["red"] if row.camera_q_core6 >= 0.05 else COLORS["blue"] if row.regulator == "STAT1" else COLORS["teal"] for row in sensitivity.itertuples()]
    x = -np.log10(sensitivity["camera_q_core6"])
    y = -np.log10(sensitivity["fry_q_core6"])
    axes[0, 0].scatter(x, y, c=colors, s=22)
    point_labels = ["D1", "D2", "N1", "N2", "C1", "C2"]
    point_offsets = [(5, 5), (5, -13), (-17, 5), (5, 5), (-17, -13), (5, -13)]
    for xv, yv, label, offset in zip(x, y, point_labels, point_offsets, strict=True):
        axes[0, 0].annotate(
            label,
            (xv, yv),
            xytext=offset,
            textcoords="offset points",
            va="center",
            ha="center",
        )
    axes[0, 0].text(
        0.98,
        0.15,
        "D/N/C: discovery/nonoverlap/childhood\n1/2: STAT1/STAT2",
        transform=axes[0, 0].transAxes,
        ha="right",
        va="bottom",
        color="#444444",
        linespacing=1.15,
    )
    axes[0, 0].set_xlim(0.82, 2.65)
    axes[0, 0].set_ylim(1.0, 7.0)
    threshold = -np.log10(0.05)
    axes[0, 0].axvline(threshold, color=COLORS["grey"], lw=0.6, ls="--")
    axes[0, 0].axhline(threshold, color=COLORS["grey"], lw=0.6, ls="--")
    axes[0, 0].set_xlabel("CAMERA -log10(BH q)")
    axes[0, 0].set_ylabel("FRY -log10(BH q)")
    axes[0, 0].set_title("Correlation-aware method concordance", loc="left")
    style_axis(axes[0, 0]); panel_label(axes[0, 0], "a")

    axes[0, 1].bar(np.arange(6), sensitivity["camera_inter_gene_correlation"], color=colors)
    axes[0, 1].set_xticks(np.arange(6), compact_labels)
    axes[0, 1].set_ylabel("Estimated inter-gene correlation")
    axes[0, 1].set_title("Residual-estimated regulon correlation", loc="left")
    style_axis(axes[0, 1]); panel_label(axes[0, 1], "b")

    matrix = -np.log10(sensitivity[["camera_q_core6", "fry_q_core6"]].to_numpy())
    image = axes[1, 0].imshow(matrix, aspect="auto", cmap="YlGnBu")
    axes[1, 0].set_xticks([0, 1], ["CAMERA", "FRY"])
    axes[1, 0].set_yticks(np.arange(6), compact_labels)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            axes[1, 0].text(col, row, f"q={sensitivity.iloc[row][['camera_q_core6', 'fry_q_core6'][col]]:.3g}", ha="center", va="center", fontsize=5.2, color="white" if matrix[row, col] > 2.4 else COLORS["dark"])
    axes[1, 0].set_title("Exact six-test BH results", loc="left")
    colorbar = figure.colorbar(image, ax=axes[1, 0], fraction=0.05, pad=0.03)
    colorbar.set_label("-log10(BH q)", fontsize=6); colorbar.ax.tick_params(labelsize=5.5)
    panel_label(axes[1, 0], "c")

    axes[1, 1].bar(np.arange(6), sensitivity["matched_signed_targets"], color=colors)
    axes[1, 1].set_xticks(np.arange(6), compact_labels)
    axes[1, 1].set_ylabel("Frozen matched signed targets")
    axes[1, 1].set_title("Target counts match the frozen ULM family", loc="left")
    style_axis(axes[1, 1]); panel_label(axes[1, 1], "d")

    write_source(source_dir / "Supplementary_Figure_S7_source_data.csv", [sensitivity.assign(panel="a-d", source_table="camera_fry_core6")])
    save_figure(figure, figure_dir, "Supplementary_Figure_S7_regulator_correlation_sensitivity")


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    figure_dir = output_dir / "supplementary_figures"
    source_dir = output_dir / "supplementary_source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)
    ASSERTIONS.clear()
    configure_style()
    for builder in (build_s1, build_s2, build_s3, build_s4, build_s5, build_s6, build_s7):
        builder(root, figure_dir, source_dir)
    payload = {
        "created_at": "2026-08-21",
        "status": "PASS_GATE_C8S_SUPPLEMENTARY_FIGURES_BUILT",
        "figures": 7,
        "formats": ["PDF", "PNG_600_DPI"],
        "source_data_files": 7,
        "source_policy": "reviewer-facing redraws of frozen Gate C2B1-C8R outputs; no exploratory biology",
        "panel_data_assertions": len(ASSERTIONS),
        "panel_data_assertions_passed": all(item["pass"] for item in ASSERTIONS),
    }
    (output_dir / "03_SUPPLEMENTARY_PANEL_DATA_ASSERTIONS.json").write_text(
        json.dumps({"created_at": "2026-08-21", "status": "PASS", "checks": ASSERTIONS}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "04_SUPPLEMENTARY_FIGURE_BUILD_STATUS.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
