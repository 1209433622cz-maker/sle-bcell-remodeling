from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


FLAGGED_STATE = "Naive B III / small naive-like cluster"
STATE_ORDER = [
    "Naive B I",
    "Naive B II / SLE-enriched naive-like",
    "Memory B I",
    "Mixed naive-memory B",
    "Memory B II",
    "Atypical / ABC-like B",
    "Plasmablast / plasma cell",
]
CORE_STATES = [
    "Naive B II / SLE-enriched naive-like",
    "Memory B I",
    "Atypical / ABC-like B",
]
STATE_LABELS = {
    "Naive B I": "Resting naive",
    "Naive B II / SLE-enriched naive-like": "Activated SLE-naive",
    "Memory B I": "Memory-like I",
    "Mixed naive-memory B": "Mixed / transitional",
    "Memory B II": "TNFRSF13B+ memory",
    "Atypical / ABC-like B": "ABC/APC-like",
    "Plasmablast / plasma cell": "Plasmablast / ASC",
}
MODEL_COLUMNS = {
    "unadjusted": ["disease_sle"],
    "demographic_adjusted": [
        "disease_sle",
        "age_z",
        "sex",
        "self_reported_ethnicity",
    ],
    "full_adjusted": [
        "disease_sle",
        "age_z",
        "sex",
        "self_reported_ethnicity",
        "Processing_Cohort_simple",
        "log10_total_bcells_z",
    ],
}


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.09,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        ha="right",
        va="bottom",
    )


def build_composition(fractions: pd.DataFrame, pseudocount: float) -> pd.DataFrame:
    data = fractions.copy()
    data["donor_id"] = data["donor_id"].astype(str)
    data["n"] = pd.to_numeric(data["n"], errors="raise")
    retained = data[data["draft_state"].isin(STATE_ORDER)].copy()
    counts = retained.pivot(index="donor_id", columns="draft_state", values="n").reindex(columns=STATE_ORDER)
    if counts.isna().any().any():
        raise ValueError("The donor-by-state count matrix is incomplete.")
    smoothed = counts + pseudocount
    smoothed_fraction = smoothed.div(smoothed.sum(axis=1), axis=0)
    log_fraction = np.log(smoothed_fraction)
    clr = log_fraction.sub(log_fraction.mean(axis=1), axis=0)
    retained_fraction = counts.div(counts.sum(axis=1), axis=0)

    disease = retained.groupby("donor_id", observed=True)["disease"].first()
    original_fraction = retained.pivot(index="donor_id", columns="draft_state", values="fraction_within_donor").reindex(columns=STATE_ORDER)

    rows = []
    for state in STATE_ORDER:
        state_frame = pd.DataFrame(
            {
                "donor_id": counts.index,
                "draft_state": state,
                "state_label": STATE_LABELS[state],
                "n_cells": counts[state].to_numpy(),
                "retained_total": counts.sum(axis=1).to_numpy(),
                "disease": disease.reindex(counts.index).to_numpy(),
                "raw_fraction": original_fraction[state].to_numpy(),
                "retained_fraction": retained_fraction[state].to_numpy(),
                "smoothed_fraction": smoothed_fraction[state].to_numpy(),
                "clr": clr[state].to_numpy(),
            }
        )
        rows.append(state_frame)
    return pd.concat(rows, ignore_index=True)


def prepare_metadata(metadata: pd.DataFrame) -> pd.DataFrame:
    meta = metadata.copy()
    meta["donor_id"] = meta["donor_id"].astype(str)
    for column in ["age_years", "log10_total_bcells", "disease_sle"]:
        meta[column] = pd.to_numeric(meta[column], errors="coerce")
    for source, target in [("age_years", "age_z"), ("log10_total_bcells", "log10_total_bcells_z")]:
        mean = meta[source].mean()
        std = meta[source].std(ddof=0)
        meta[target] = (meta[source] - mean) / std
    return meta


def design_matrix(frame: pd.DataFrame, model: str) -> tuple[pd.DataFrame, pd.Series]:
    columns = MODEL_COLUMNS[model]
    numeric = [column for column in columns if column in {"disease_sle", "age_z", "log10_total_bcells_z"}]
    categorical = [column for column in columns if column not in numeric]
    x_parts = [frame[numeric].astype(float)]
    if categorical:
        x_parts.append(pd.get_dummies(frame[categorical].astype("category"), drop_first=True, dtype=float))
    x = pd.concat(x_parts, axis=1)
    x = sm.add_constant(x, has_constant="add")
    return x, frame["outcome"].astype(float)


def fit_models(composition: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    merged = composition.merge(metadata, on="donor_id", how="inner", validate="many_to_one")
    outcomes = {"raw_fraction": "raw_fraction", "clr": "clr"}
    rows = []
    required_meta = [
        "disease_sle",
        "age_z",
        "sex",
        "self_reported_ethnicity",
        "Processing_Cohort_simple",
        "log10_total_bcells_z",
    ]
    for analysis, outcome_column in outcomes.items():
        for model in MODEL_COLUMNS:
            required = list(dict.fromkeys(MODEL_COLUMNS[model] + [outcome_column]))
            for state in STATE_ORDER:
                frame = merged[merged["draft_state"] == state].copy()
                frame["outcome"] = frame[outcome_column]
                frame = frame.dropna(subset=required)
                x, y = design_matrix(frame, model)
                result = sm.OLS(y, x).fit(cov_type="HC3")
                beta = float(result.params["disease_sle"])
                ci_low, ci_high = result.conf_int().loc["disease_sle"].astype(float)
                outcome_sd = float(y.std(ddof=0))
                rows.append(
                    {
                        "analysis": analysis,
                        "model": model,
                        "draft_state": state,
                        "state_label": STATE_LABELS[state],
                        "n_donors": int(result.nobs),
                        "disease_sle_beta": beta,
                        "ci_low": float(ci_low),
                        "ci_high": float(ci_high),
                        "standardized_beta": beta / outcome_sd if outcome_sd > 0 else np.nan,
                        "standardized_ci_low": float(ci_low) / outcome_sd if outcome_sd > 0 else np.nan,
                        "standardized_ci_high": float(ci_high) / outcome_sd if outcome_sd > 0 else np.nan,
                        "pvalue": float(result.pvalues["disease_sle"]),
                        "r_squared": float(result.rsquared),
                        "condition_number": float(result.condition_number),
                        "n_complete_full_metadata": int(frame[required_meta].notna().all(axis=1).sum()),
                    }
                )
    models = pd.DataFrame(rows)
    models["fdr_bh"] = np.nan
    for _, index in models.groupby(["analysis", "model"], observed=True).groups.items():
        models.loc[index, "fdr_bh"] = multipletests(models.loc[index, "pvalue"], method="fdr_bh")[1]
    return models


def build_core_comparison(models: pd.DataFrame, original_models: pd.DataFrame | None) -> pd.DataFrame:
    core = models[
        (models["draft_state"].isin(CORE_STATES))
        & (models["model"] == "full_adjusted")
    ].copy()
    core["source"] = core["analysis"].map(
        {
            "raw_fraction": "Matched refit: raw fraction",
            "clr": "Compositional sensitivity: CLR",
        }
    )
    columns = [
        "source",
        "draft_state",
        "state_label",
        "n_donors",
        "disease_sle_beta",
        "ci_low",
        "ci_high",
        "standardized_beta",
        "pvalue",
        "fdr_bh",
    ]
    output = core[columns]
    if original_models is not None:
        original = original_models[
            (original_models["draft_state"].isin(CORE_STATES))
            & (original_models["model"] == "full_adjusted")
            & (original_models["error"].fillna("") == "")
        ].copy()
        original["source"] = "Published primary fraction model"
        original["state_label"] = original["draft_state"].map(STATE_LABELS)
        original["standardized_beta"] = np.nan
        output = pd.concat([original[columns], output], ignore_index=True)
    return output


def plot_clr_distributions(ax: plt.Axes, composition: pd.DataFrame) -> None:
    data = composition[composition["draft_state"].isin(CORE_STATES)].copy()
    data["state_label"] = pd.Categorical(
        data["state_label"],
        categories=[STATE_LABELS[x] for x in CORE_STATES],
        ordered=True,
    )
    disease_order = ["normal", "systemic lupus erythematosus"]
    palette = {"normal": "#9BA8B4", "systemic lupus erythematosus": "#B23A48"}
    sns.boxplot(
        data=data,
        y="state_label",
        x="clr",
        hue="disease",
        hue_order=disease_order,
        palette=palette,
        showfliers=False,
        linewidth=0.7,
        ax=ax,
    )
    sns.stripplot(
        data=data,
        y="state_label",
        x="clr",
        hue="disease",
        hue_order=disease_order,
        palette=palette,
        dodge=True,
        alpha=0.25,
        size=1.6,
        linewidth=0,
        ax=ax,
    )
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    ax.axvline(0, color="0.35", linewidth=0.6)
    ax.set_title("Core-state CLR distributions", loc="left")
    ax.set_xlabel("Centered log-ratio abundance")
    ax.set_ylabel("")
    ax.text(0.78, 1.02, "Normal", color=palette["normal"], fontweight="bold", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.0)
    ax.text(0.98, 1.02, "SLE", color=palette["systemic lupus erythematosus"], fontweight="bold", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.0)


def plot_clr_forest(ax: plt.Axes, models: pd.DataFrame) -> None:
    sub = models[(models["analysis"] == "clr") & (models["model"] == "full_adjusted")].copy()
    sub = sub.sort_values("disease_sle_beta")
    y = np.arange(len(sub))
    colors = np.where(sub["disease_sle_beta"] >= 0, "#B23A48", "#4C78A8")
    for position, (_, row), color in zip(y, sub.iterrows(), colors, strict=True):
        ax.errorbar(
            row["disease_sle_beta"],
            position,
            xerr=[[row["disease_sle_beta"] - row["ci_low"]], [row["ci_high"] - row["disease_sle_beta"]]],
            fmt="o",
            color=color,
            capsize=2,
            markersize=3.2,
        )
    ax.axvline(0, color="0.25", linewidth=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(sub["state_label"], fontsize=5.0)
    for tick, state in zip(ax.get_yticklabels(), sub["draft_state"], strict=True):
        if state in CORE_STATES:
            tick.set_fontweight("bold")
    ax.set_xlabel("Full-adjusted SLE coefficient (CLR)")
    ax.set_title("Compositional effect estimates", loc="left")


def plot_robustness_heatmap(ax: plt.Axes, models: pd.DataFrame) -> None:
    keep = models[
        models["model"].isin(["unadjusted", "full_adjusted"])
    ].copy()
    keep["column"] = keep["analysis"].map({"raw_fraction": "Raw fraction", "clr": "CLR"}) + ": " + keep["model"].map(
        {"unadjusted": "unadjusted", "full_adjusted": "full adjusted"}
    )
    keep["signed_log10_fdr"] = -np.log10(keep["fdr_bh"].clip(lower=1e-300)) * np.sign(keep["disease_sle_beta"])
    columns = [
        "Raw fraction: unadjusted",
        "Raw fraction: full adjusted",
        "CLR: unadjusted",
        "CLR: full adjusted",
    ]
    matrix = keep.pivot(index="state_label", columns="column", values="signed_log10_fdr")
    matrix = matrix.reindex(index=[STATE_LABELS[x] for x in STATE_ORDER], columns=columns)
    matrix.columns = ["Raw\nunadjusted", "Raw\nfull adjusted", "CLR\nunadjusted", "CLR\nfull adjusted"]
    sns.heatmap(
        matrix,
        cmap="vlag",
        center=0,
        vmin=-20,
        vmax=20,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Signed -log10(FDR)", "shrink": 0.75},
    )
    ax.set_title("Direction and significance robustness", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=0, labelsize=4.8)
    ax.tick_params(axis="y", labelsize=5.0)


def make_figure(path: Path, composition: pd.DataFrame, models: pd.DataFrame) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(6.8, 5.5), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[0.88, 1.15], width_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, :])
    plot_clr_distributions(ax_a, composition)
    plot_clr_forest(ax_b, models)
    plot_robustness_heatmap(ax_c, models)
    for ax, label in zip([ax_a, ax_b, ax_c], "abc", strict=True):
        add_panel_label(ax, label)
    save_nature_figure(fig, path)
    plt.close(fig)


def write_summary(
    path: Path,
    fractions: pd.DataFrame,
    composition: pd.DataFrame,
    models: pd.DataFrame,
    pseudocount_sensitivity: pd.DataFrame,
    pseudocount: float,
) -> None:
    clr_full = models[(models["analysis"] == "clr") & (models["model"] == "full_adjusted")].set_index("draft_state")
    lines = [
        "# Compositional Abundance Sensitivity",
        "",
        f"- Donors: {composition['donor_id'].nunique()}.",
        f"- Retained biological states: {len(STATE_ORDER)}.",
        f"- Excluded technical state: `{FLAGGED_STATE}`.",
        f"- Zero donor-state counts before replacement: {int((composition['n_cells'] == 0).sum())}.",
        f"- Count-scale pseudocount: {pseudocount}.",
        "- Transformation: smoothed retained-state proportions followed by donor-wise centered log-ratio (CLR).",
        "- Models: OLS with HC3 robust standard errors; age and log10 B-lineage cell count standardized; categorical covariates dummy encoded.",
        f"- Pseudocount sensitivity values: {', '.join(str(x) for x in sorted(pseudocount_sensitivity['pseudocount'].unique()))}.",
        "",
        "## Core full-adjusted CLR results",
        "",
    ]
    for state in CORE_STATES:
        row = clr_full.loc[state]
        sensitivity_state = pseudocount_sensitivity[pseudocount_sensitivity["draft_state"] == state]
        same_direction = bool((np.sign(sensitivity_state["disease_sle_beta"]) == np.sign(row["disease_sle_beta"])).all())
        lines.append(
            f"- {STATE_LABELS[state]}: beta {row['disease_sle_beta']:.3f}; "
            f"95% CI {row['ci_low']:.3f} to {row['ci_high']:.3f}; FDR {row['fdr_bh']:.2e}; "
            f"direction stable across pseudocounts: {same_direction}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The compositional sensitivity is considered supportive when the activated SLE-naive-like and ABC/APC-like states remain positive and the memory-like I state remains negative after CLR transformation and full covariate adjustment.",
            "CLR coefficients are relative to the geometric mean abundance of all retained states and should not be interpreted as absolute cell-number changes.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run donor-level compositional sensitivity analysis of B-cell state abundance.")
    parser.add_argument("--donor-fractions", required=True)
    parser.add_argument("--donor-metadata", required=True)
    parser.add_argument("--original-models")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--pseudocount", type=float, default=0.5)
    parser.add_argument("--pseudocount-grid", default="0.1,0.5,1.0")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    tabledir = outdir / "tables"
    figdir = outdir / "figures"
    tabledir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)

    fractions = pd.read_csv(args.donor_fractions)
    metadata = prepare_metadata(pd.read_csv(args.donor_metadata))
    composition = build_composition(fractions, args.pseudocount)
    models = fit_models(composition, metadata)
    original_models = pd.read_csv(args.original_models) if args.original_models else None
    core_comparison = build_core_comparison(models, original_models)
    pseudocount_rows = []
    pseudocount_grid = sorted({float(value.strip()) for value in args.pseudocount_grid.split(",") if value.strip()})
    for pseudocount in pseudocount_grid:
        sensitivity_composition = build_composition(fractions, pseudocount)
        sensitivity_models = fit_models(sensitivity_composition, metadata)
        sensitivity_core = sensitivity_models[
            (sensitivity_models["analysis"] == "clr")
            & (sensitivity_models["model"] == "full_adjusted")
            & (sensitivity_models["draft_state"].isin(CORE_STATES))
        ].copy()
        sensitivity_core.insert(0, "pseudocount", pseudocount)
        pseudocount_rows.append(sensitivity_core)
    pseudocount_sensitivity = pd.concat(pseudocount_rows, ignore_index=True)

    composition.to_csv(tabledir / "donor_state_compositional_abundance.csv", index=False, encoding="utf-8-sig")
    models.to_csv(tabledir / "compositional_abundance_models.csv", index=False, encoding="utf-8-sig")
    core_comparison.to_csv(tabledir / "core_state_compositional_comparison.csv", index=False, encoding="utf-8-sig")
    pseudocount_sensitivity.to_csv(tabledir / "core_state_pseudocount_sensitivity.csv", index=False, encoding="utf-8-sig")
    make_figure(figdir / "supplementary_figure_s4_compositional_sensitivity.png", composition, models)
    write_summary(
        outdir / "compositional_abundance_sensitivity_summary.md",
        fractions,
        composition,
        models,
        pseudocount_sensitivity,
        args.pseudocount,
    )

    clr_full = models[
        (models["analysis"] == "clr")
        & (models["model"] == "full_adjusted")
        & (models["draft_state"].isin(CORE_STATES))
    ]
    print(f"Wrote compositional sensitivity outputs to: {outdir}")
    print(clr_full[["draft_state", "disease_sle_beta", "ci_low", "ci_high", "pvalue", "fdr_bh"]].to_string(index=False))


if __name__ == "__main__":
    main()
