from __future__ import annotations

import argparse
import re
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from matplotlib.patches import Patch
from scipy import stats

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


CORE_STATES = [
    "Naive B II / SLE-enriched naive-like",
    "Memory B I",
    "Atypical / ABC-like B",
]

STATE_LABELS = {
    "Naive B I": "Resting naive B",
    "Naive B II / SLE-enriched naive-like": "Activated SLE-naive-like",
    "Memory B I": "Memory-like B I",
    "Mixed naive-memory B": "Mixed/transitional",
    "Memory B II": "TNFRSF13B+ memory-like",
    "Atypical / ABC-like B": "ABC/APC-like",
    "Naive B III / small naive-like cluster": "Flagged platelet/ambient-high",
    "Plasmablast / plasma cell": "Plasmablast/ASC",
}

MODEL_SPECS = {
    "unadjusted": [],
    "demographic_adjusted": ["age_years", "sex", "self_reported_ethnicity"],
    "full_adjusted": ["age_years", "sex", "self_reported_ethnicity", "Processing_Cohort_simple", "log10_total_bcells"],
}

DISEASE_ORDER = ["normal", "systemic lupus erythematosus"]
DISEASE_LABELS = {"normal": "Normal", "systemic lupus erythematosus": "SLE"}
DISEASE_STATE_ORDER = ["na", "managed", "flare", "treated", "mixed"]
DISEASE_STATE_LABELS = {"na": "Normal", "managed": "SLE managed", "flare": "SLE flare", "treated": "SLE treated", "mixed": "SLE mixed"}


def benjamini_hochberg(pvalues: pd.Series) -> pd.Series:
    p = pd.to_numeric(pvalues, errors="coerce")
    out = pd.Series(np.nan, index=p.index, dtype=float)
    valid = p.dropna()
    if valid.empty:
        return out
    order = np.argsort(valid.to_numpy())
    ranked = valid.to_numpy()[order]
    n = len(ranked)
    adjusted = ranked * n / (np.arange(n) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    out.loc[valid.index[order]] = adjusted
    return out


def parse_age(value: str) -> float:
    ages = [float(match) for match in re.findall(r"(\d+(?:\.\d+)?)\s*-?\s*year", str(value))]
    if ages:
        return float(np.median(ages))
    return np.nan


def collapse_unique(values: pd.Series) -> str:
    clean = values.dropna().astype(str)
    clean = clean[clean.str.lower() != "nan"]
    unique = sorted(clean.unique())
    if not unique:
        return ""
    return " | ".join(unique)


def make_donor_metadata(bcell_h5ad: str, donor_fractions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = [
        "donor_id",
        "disease",
        "disease_state",
        "sex",
        "self_reported_ethnicity",
        "development_stage",
        "Processing_Cohort",
        "sample_uuid",
        "library_uuid",
        "suspension_uuid",
    ]
    source = ad.read_h5ad(bcell_h5ad, backed="r")
    obs = source.obs[columns].copy()
    try:
        source.file.close()
    except Exception:
        pass

    grouped = obs.groupby("donor_id", observed=True)
    rows = []
    for donor_id, sub in grouped:
        row: dict[str, object] = {"donor_id": str(donor_id), "n_blineage_cells_obs": int(len(sub))}
        for col in columns:
            if col == "donor_id":
                continue
            clean = sub[col].dropna().astype(str)
            clean = clean[clean.str.lower() != "nan"]
            row[f"{col}_n_unique"] = int(clean.nunique())
            row[col] = collapse_unique(sub[col])
        row["age_years"] = parse_age(row.get("development_stage", ""))
        row["Processing_Cohort_simple"] = "multiple" if row.get("Processing_Cohort_n_unique", 0) > 1 else row.get("Processing_Cohort", "")
        if row.get("disease", "") == "normal":
            row["disease_state_simple"] = "na"
        else:
            row["disease_state_simple"] = "mixed" if row.get("disease_state_n_unique", 0) > 1 else row.get("disease_state", "")
        rows.append(row)
    donor_meta = pd.DataFrame(rows)

    donor_totals = (
        donor_fractions[["donor_id", "donor_total"]]
        .drop_duplicates()
        .assign(donor_id=lambda x: x["donor_id"].astype(str))
    )
    donor_meta = donor_meta.merge(donor_totals, on="donor_id", how="left")
    donor_meta["log10_total_bcells"] = np.log10(pd.to_numeric(donor_meta["donor_total"], errors="coerce").clip(lower=1))
    donor_meta["disease_label"] = donor_meta["disease"].map(DISEASE_LABELS).fillna(donor_meta["disease"])
    donor_meta["disease_sle"] = (donor_meta["disease"] == "systemic lupus erythematosus").astype(int)

    audit_rows = []
    audit_columns = [
        "disease",
        "disease_state",
        "disease_state_simple",
        "sex",
        "self_reported_ethnicity",
        "development_stage",
        "age_years",
        "Processing_Cohort",
        "Processing_Cohort_simple",
        "donor_total",
    ]
    for col in audit_columns:
        nonmissing = donor_meta[col].notna() & (donor_meta[col].astype(str) != "")
        unique_col = f"{col}_n_unique"
        audit_rows.append(
            {
                "field": col,
                "n_donors_nonmissing": int(nonmissing.sum()),
                "pct_donors_nonmissing": float(nonmissing.mean() * 100),
                "n_donors_with_multiple_values": int((donor_meta[unique_col] > 1).sum()) if unique_col in donor_meta else 0,
                "n_unique_values": int(donor_meta.loc[nonmissing, col].nunique()) if col in donor_meta else np.nan,
            }
        )
    audit = pd.DataFrame(audit_rows)
    return donor_meta, audit


def covariate_balance(donor_meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    categorical_rows = []
    for covar in ["sex", "self_reported_ethnicity", "Processing_Cohort_simple", "disease_state_simple"]:
        counts = donor_meta.groupby(["disease", covar], observed=True).size().rename("n").reset_index()
        totals = counts.groupby("disease", observed=True)["n"].transform("sum")
        counts["fraction"] = counts["n"] / totals
        counts["covariate"] = covar
        counts = counts.rename(columns={covar: "level"})
        categorical_rows.append(counts[["covariate", "disease", "level", "n", "fraction"]])
    categorical = pd.concat(categorical_rows, ignore_index=True)

    age_summary = (
        donor_meta.groupby("disease", observed=True)["age_years"]
        .agg(n="count", mean="mean", median="median", std="std", min="min", max="max")
        .reset_index()
    )
    return categorical, age_summary


def design_matrix(df: pd.DataFrame, covariates: list[str]) -> pd.DataFrame:
    x = pd.DataFrame({"disease_sle": df["disease_sle"].astype(float)}, index=df.index)
    numeric_covars = [c for c in covariates if c in {"age_years", "log10_total_bcells"}]
    for covar in numeric_covars:
        values = pd.to_numeric(df[covar], errors="coerce")
        scale = values.std(ddof=0)
        x[covar] = (values - values.mean()) / scale if pd.notna(scale) and scale > 0 else 0.0

    categorical_covars = [c for c in covariates if c not in numeric_covars]
    if categorical_covars:
        dummies = pd.get_dummies(df[categorical_covars].astype(str), columns=categorical_covars, drop_first=True, dtype=float)
        x = pd.concat([x, dummies], axis=1)

    x = x.loc[:, x.nunique(dropna=False) > 1]
    if "disease_sle" not in x.columns:
        x["disease_sle"] = df["disease_sle"].astype(float)
    x = sm.add_constant(x, has_constant="add")
    return x.astype(float)


def fit_models(donor_fractions: pd.DataFrame, donor_meta: pd.DataFrame) -> pd.DataFrame:
    fraction_cols_to_drop = [col for col in ["disease"] if col in donor_fractions.columns]
    model_data = (
        donor_fractions.drop(columns=fraction_cols_to_drop)
        .assign(donor_id=lambda x: x["donor_id"].astype(str))
        .merge(donor_meta, on="donor_id", how="left")
    )
    rows = []
    for model_name, covariates in MODEL_SPECS.items():
        needed = ["fraction_within_donor", "disease_sle"] + covariates
        for state, sub in model_data.groupby("draft_state", observed=True):
            keep = sub.dropna(subset=[c for c in needed if c in sub.columns]).copy()
            keep = keep[(keep["disease"].isin(DISEASE_ORDER)) & keep["fraction_within_donor"].notna()]
            if keep["disease_sle"].nunique() < 2 or len(keep) < 20:
                rows.append({"model": model_name, "draft_state": state, "n_donors": int(len(keep)), "error": "insufficient complete cases"})
                continue
            y = pd.to_numeric(keep["fraction_within_donor"], errors="coerce").astype(float)
            x = design_matrix(keep, covariates)
            try:
                fit = sm.OLS(y, x).fit(cov_type="HC3")
                coef = float(fit.params["disease_sle"])
                se = float(fit.bse["disease_sle"])
                pvalue = float(fit.pvalues["disease_sle"])
                ci_low, ci_high = fit.conf_int().loc["disease_sle"].astype(float).tolist()
                rows.append(
                    {
                        "model": model_name,
                        "draft_state": state,
                        "state_label": STATE_LABELS.get(state, state),
                        "n_donors": int(len(keep)),
                        "n_normal": int((keep["disease_sle"] == 0).sum()),
                        "n_sle": int((keep["disease_sle"] == 1).sum()),
                        "disease_sle_beta": coef,
                        "disease_sle_se_hc3": se,
                        "ci_low": float(ci_low),
                        "ci_high": float(ci_high),
                        "pvalue": pvalue,
                        "r_squared": float(fit.rsquared),
                        "condition_number": float(fit.condition_number),
                        "n_parameters": int(len(fit.params)),
                        "error": "",
                    }
                )
            except Exception as exc:
                rows.append({"model": model_name, "draft_state": state, "state_label": STATE_LABELS.get(state, state), "n_donors": int(len(keep)), "error": str(exc)})
    out = pd.DataFrame(rows)
    if "pvalue" in out:
        out["fdr_bh"] = out.groupby("model", observed=True)["pvalue"].transform(benjamini_hochberg)
    return out


def disease_state_summary(donor_fractions: pd.DataFrame, donor_meta: pd.DataFrame) -> pd.DataFrame:
    data = donor_fractions.assign(donor_id=lambda x: x["donor_id"].astype(str)).merge(
        donor_meta[["donor_id", "disease_state_simple"]], on="donor_id", how="left"
    )
    data["disease_state_final"] = data["disease_state_simple"]
    summary = (
        data.groupby(["disease_state_final", "draft_state"], observed=True)["fraction_within_donor"]
        .agg(n_donors="count", mean_fraction="mean", median_fraction="median", std_fraction="std")
        .reset_index()
    )
    summary["state_label"] = summary["draft_state"].map(STATE_LABELS).fillna(summary["draft_state"])
    summary["disease_state_label"] = summary["disease_state_final"].map(DISEASE_STATE_LABELS).fillna(summary["disease_state_final"])
    return summary


def write_summary(path: Path, donor_meta: pd.DataFrame, audit: pd.DataFrame, models: pd.DataFrame) -> None:
    core_full = models[(models["model"] == "full_adjusted") & (models["draft_state"].isin(CORE_STATES))].copy()
    lines = [
        "# Covariate Sensitivity Summary",
        "",
        f"- Donors audited: {donor_meta['donor_id'].nunique()}.",
        f"- Normal donors: {(donor_meta['disease'] == 'normal').sum()}.",
        f"- SLE donors: {(donor_meta['disease'] == 'systemic lupus erythematosus').sum()}.",
        "",
        "## Metadata Completeness",
        "",
    ]
    for row in audit.itertuples(index=False):
        lines.append(f"- {row.field}: {row.n_donors_nonmissing} donors ({row.pct_donors_nonmissing:.1f}%); multi-value donors {row.n_donors_with_multiple_values}.")
    lines.extend(["", "## Full-Adjusted Core State Results", ""])
    for row in core_full.sort_values("draft_state").itertuples(index=False):
        lines.append(
            f"- {row.state_label}: beta {row.disease_sle_beta:.4f}; "
            f"95% CI {row.ci_low:.4f} to {row.ci_high:.4f}; FDR {row.fdr_bh:.2e}."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The main activated SLE-naive-like expansion, memory-like B-cell reduction, and ABC/APC-like expansion remain directionally stable after adjusting for age, sex, self-reported ethnicity, processing cohort, and donor B-lineage cell count.",
            "Disease-state analyses should remain descriptive because disease_state is structurally nested within disease status.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.10, 1.06, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", ha="right", va="bottom")


def plot_age(ax, donor_meta: pd.DataFrame) -> None:
    order = ["Normal", "SLE"]
    data = donor_meta.copy()
    sns.boxplot(data=data, x="disease_label", y="age_years", order=order, hue="disease_label", palette={"Normal": "#AEB7C2", "SLE": "#D36B6B"}, ax=ax, fliersize=0, legend=False)
    sns.stripplot(data=data, x="disease_label", y="age_years", order=order, color="#333333", alpha=0.35, size=2.5, ax=ax)
    normal = data.loc[data["disease_label"] == "Normal", "age_years"].dropna()
    sle = data.loc[data["disease_label"] == "SLE", "age_years"].dropna()
    pvalue = stats.mannwhitneyu(normal, sle, alternative="two-sided").pvalue if len(normal) and len(sle) else np.nan
    ax.text(0.5, 0.91, f"Age balance p={pvalue:.2g}", transform=ax.transAxes, ha="center", va="top", fontsize=5.5)
    ax.set_xlabel("")
    ax.set_ylabel("Age, years")
    ax.set_title("Donor age distribution")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Normal\n(n=99)", "SLE\n(n=160)"])


def plot_stacked(ax, donor_meta: pd.DataFrame, covariate: str, title: str) -> None:
    tab = donor_meta.groupby(["disease_label", covariate], observed=True).size().unstack(fill_value=0)
    tab = tab.reindex(["Normal", "SLE"])
    prop = tab.div(tab.sum(axis=1), axis=0)
    colors = sns.color_palette("Set2", n_colors=prop.shape[1])
    bottom = np.zeros(len(prop))
    x = np.arange(len(prop))
    for color, level in zip(colors, prop.columns):
        values = prop[level].to_numpy()
        ax.bar(x, values, bottom=bottom, color=color, label=str(level), width=0.65)
        bottom += values
    ax.set_xticks(x)
    ax.set_xticklabels(prop.index)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Fraction of donors")
    ax.set_title(title)
    ax.legend(frameon=False, fontsize=5, loc="upper left", bbox_to_anchor=(1.01, 1.0))


def plot_covariate_balance(ax, donor_meta: pd.DataFrame) -> None:
    label_map = {
        "1.0": "Cohort 1",
        "2.0": "Cohort 2",
        "3.0": "Cohort 3",
        "4.0": "Cohort 4",
        "multiple": "Multiple cohorts",
        "African American": "African American",
        "Asian": "Asian",
        "European American": "European American",
        "Hispanic or Latin": "Hispanic or Latin",
    }
    rows = []
    for covariate, group_label in [
        ("Processing_Cohort_simple", "Processing cohort"),
        ("self_reported_ethnicity", "Ethnicity"),
    ]:
        tab = donor_meta.groupby(["disease_label", covariate], observed=True).size().unstack(fill_value=0)
        tab = tab.reindex(["Normal", "SLE"], fill_value=0)
        prop = tab.div(tab.sum(axis=1), axis=0)
        for level in prop.columns:
            rows.append(
                {
                    "label": label_map.get(str(level), str(level)),
                    "difference": float(prop.loc["SLE", level] - prop.loc["Normal", level]),
                    "group": group_label,
                }
            )
    balance = pd.DataFrame(rows)
    balance["abs_difference"] = balance["difference"].abs()
    balance = balance.sort_values(["group", "abs_difference"], ascending=[True, False]).reset_index(drop=True)
    colors = balance["group"].map({"Processing cohort": "#4C78A8", "Ethnicity": "#E07A5F"})
    y = np.arange(len(balance))
    ax.barh(y, balance["difference"], color=colors, height=0.68)
    ax.axvline(0, color="0.25", linewidth=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(balance["label"], fontsize=5.0)
    ax.invert_yaxis()
    limit = max(0.05, float(balance["abs_difference"].max()) * 1.25)
    ax.set_xlim(-limit, limit)
    ax.set_xlabel("Proportion difference (SLE - normal)")
    ax.set_title("Categorical covariate balance")
    ax.legend(
        handles=[
            Patch(facecolor="#4C78A8", label="Processing cohort"),
            Patch(facecolor="#E07A5F", label="Ethnicity"),
        ],
        frameon=False,
        fontsize=5.0,
        loc="lower right",
    )


def plot_effect_sensitivity(ax, models: pd.DataFrame) -> None:
    sub = models[(models["draft_state"].isin(CORE_STATES)) & (models["error"].fillna("") == "")].copy()
    sub["model_label"] = sub["model"].map(
        {
            "unadjusted": "Unadjusted",
            "demographic_adjusted": "Demographic",
            "full_adjusted": "Full adjusted",
        }
    )
    sub["state_label"] = sub["draft_state"].map(STATE_LABELS)
    state_order = [STATE_LABELS[s] for s in CORE_STATES]
    model_order = ["Unadjusted", "Demographic", "Full adjusted"]
    offsets = {"Unadjusted": -0.18, "Demographic": 0.0, "Full adjusted": 0.18}
    colors = {"Unadjusted": "#AEB7C2", "Demographic": "#D9822B", "Full adjusted": "#B23A48"}
    y_positions = {state: i for i, state in enumerate(state_order)}
    for model_label in model_order:
        m = sub[sub["model_label"] == model_label]
        for row in m.itertuples(index=False):
            y = y_positions[row.state_label] + offsets[model_label]
            ax.errorbar(
                row.disease_sle_beta,
                y,
                xerr=[[row.disease_sle_beta - row.ci_low], [row.ci_high - row.disease_sle_beta]],
                fmt="o",
                color=colors[model_label],
                capsize=3,
                label=model_label,
            )
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(
        unique.values(),
        unique.keys(),
        frameon=False,
        fontsize=4.8,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=3,
        borderaxespad=0,
        columnspacing=0.7,
        handletextpad=0.2,
    )
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_xlim(-0.16, 0.24)
    ax.set_yticks(range(len(state_order)))
    ax.set_yticklabels(state_order)
    ax.set_ylim(len(state_order) - 0.5, -1.10)
    ax.tick_params(axis="y", labelsize=5.5)
    ax.set_xlabel("SLE coefficient on donor fraction")
    ax.set_title("Model sensitivity")


def plot_fdr_heatmap(ax, models: pd.DataFrame) -> None:
    ok = models[models["error"].fillna("") == ""].copy()
    ok["state_label"] = ok["draft_state"].map(STATE_LABELS).fillna(ok["draft_state"])
    ok["model_label"] = ok["model"].map({"unadjusted": "Unadjusted", "demographic_adjusted": "Demographic", "full_adjusted": "Full adjusted"})
    ok["signed_log10_fdr"] = -np.log10(ok["fdr_bh"].clip(lower=1e-300)) * np.sign(ok["disease_sle_beta"])
    order = [STATE_LABELS[s] for s in ok.sort_values("draft_state")["draft_state"].drop_duplicates()]
    mat = ok.pivot(index="state_label", columns="model_label", values="signed_log10_fdr").reindex(order)
    mat = mat[["Unadjusted", "Demographic", "Full adjusted"]]
    sns.heatmap(
        mat,
        cmap="vlag",
        center=0,
        vmin=-20,
        vmax=20,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Signed -log10(FDR)", "shrink": 0.72},
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("All-state adjusted significance")
    ax.tick_params(axis="y", labelsize=5.5)
    ax.tick_params(axis="x", labelsize=5.5, rotation=45)


def plot_disease_state_heatmap(ax, summary: pd.DataFrame) -> None:
    sub = summary[summary["draft_state"].isin(CORE_STATES)].copy()
    state_order = [STATE_LABELS[s] for s in CORE_STATES]
    disease_order = [DISEASE_STATE_LABELS[s] for s in DISEASE_STATE_ORDER]
    mat = sub.pivot(index="state_label", columns="disease_state_label", values="mean_fraction").reindex(index=state_order, columns=disease_order)
    mat = mat.dropna(axis=1, how="all")
    sns.heatmap(mat, cmap="YlOrRd", linewidths=0.5, linecolor="white", annot=False, ax=ax, cbar_kws={"label": "Mean donor fraction"})
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("Disease-state descriptive abundance")
    ax.tick_params(axis="y", labelsize=5.5)
    ax.tick_params(axis="x", labelsize=5.5, rotation=45)


def make_figure(out_png: Path, donor_meta: pd.DataFrame, models: pd.DataFrame, disease_summary: pd.DataFrame) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(6.8, 5.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[0.90, 1.18], width_ratios=[0.78, 1.22])
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1]),
    ]
    plot_age(axes[0], donor_meta)
    plot_covariate_balance(axes[1], donor_meta)
    plot_effect_sensitivity(axes[2], models)
    plot_fdr_heatmap(axes[3], models)
    for ax, label in zip(axes, list("abcd")):
        add_panel_label(ax, label)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    save_nature_figure(fig, out_png)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit donor metadata and test covariate sensitivity of B-cell state abundance.")
    parser.add_argument("--bcell-h5ad", required=True)
    parser.add_argument("--donor-fractions", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    tabledir = outdir / "tables"
    figdir = outdir / "figures"
    tabledir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)

    donor_fractions = pd.read_csv(args.donor_fractions)
    donor_fractions["donor_id"] = donor_fractions["donor_id"].astype(str)
    donor_meta, audit = make_donor_metadata(args.bcell_h5ad, donor_fractions)
    categorical_balance, age_summary = covariate_balance(donor_meta)
    models = fit_models(donor_fractions, donor_meta)
    disease_summary = disease_state_summary(donor_fractions, donor_meta)

    donor_meta.to_csv(tabledir / "donor_metadata_covariates.csv", index=False, encoding="utf-8-sig")
    audit.to_csv(tabledir / "donor_metadata_completeness_audit.csv", index=False, encoding="utf-8-sig")
    categorical_balance.to_csv(tabledir / "donor_covariate_balance_categorical.csv", index=False, encoding="utf-8-sig")
    age_summary.to_csv(tabledir / "donor_age_balance_summary.csv", index=False, encoding="utf-8-sig")
    models.to_csv(tabledir / "state_abundance_covariate_models.csv", index=False, encoding="utf-8-sig")
    disease_summary.to_csv(tabledir / "state_abundance_by_disease_state_summary.csv", index=False, encoding="utf-8-sig")

    write_summary(outdir / "covariate_sensitivity_summary.md", donor_meta, audit, models)
    make_figure(figdir / "figure4_v1_covariate_sensitivity.png", donor_meta, models, disease_summary)

    print(f"Wrote covariate sensitivity outputs to: {outdir}")
    core = models[(models["model"] == "full_adjusted") & (models["draft_state"].isin(CORE_STATES))]
    print(core[["draft_state", "disease_sle_beta", "ci_low", "ci_high", "pvalue", "fdr_bh"]].to_string(index=False))


if __name__ == "__main__":
    main()
