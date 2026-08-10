#!/usr/bin/env python
"""Run Wakefield approximate-Bayes-factor colocalisation for SLE and B-cell eQTLs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.special import logsumexp

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PRIMARY_P12 = 1e-5
P12_SENSITIVITY = (1e-6, 1e-5, 1e-4)
P1 = 1e-4
P2 = 1e-4
MIN_SHARED_VARIANTS = 100
CASE_CONTROL_PRIOR_SD = 0.20
QUANTITATIVE_PRIOR_SD = 0.15
GWAS_SAMPLE_INFO = {
    "GCST005831": {"cases": 4943, "controls": 8483},
    "GCST90558100": {"cases": 6547, "controls": 648130},
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def wakefield_log_abf(beta: np.ndarray, se: np.ndarray, prior_sd: float) -> np.ndarray:
    variance = np.square(se)
    prior_variance = prior_sd**2
    shrinkage = prior_variance / (prior_variance + variance)
    z_score = beta / se
    return 0.5 * (np.log1p(-shrinkage) + shrinkage * np.square(z_score))


def logdiffexp(log_a: float, log_b: float) -> float:
    if not np.isfinite(log_b):
        return log_a
    if log_b >= log_a:
        return -np.inf
    return log_a + math.log1p(-math.exp(log_b - log_a))


def coloc_posteriors(
    gwas_log_abf: np.ndarray,
    eqtl_log_abf: np.ndarray,
    p12: float,
) -> dict[str, float]:
    log_sum_1 = float(logsumexp(gwas_log_abf))
    log_sum_2 = float(logsumexp(eqtl_log_abf))
    log_sum_12 = float(logsumexp(gwas_log_abf + eqtl_log_abf))
    log_h3_component = logdiffexp(log_sum_1 + log_sum_2, log_sum_12)

    log_hypotheses = np.array(
        [
            0.0,
            math.log(P1) + log_sum_1,
            math.log(P2) + log_sum_2,
            math.log(P1) + math.log(P2) + log_h3_component,
            math.log(p12) + log_sum_12,
        ]
    )
    posterior = np.exp(log_hypotheses - logsumexp(log_hypotheses))
    return {f"PP.H{i}": float(value) for i, value in enumerate(posterior)}


def prepare_gwas(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t", compression="gzip", low_memory=False)
    if "hm_variant_id" in frame and frame["hm_variant_id"].notna().any():
        explicit_variant = frame["hm_variant_id"]
    else:
        explicit_variant = frame["variant_id"]
    parsed = explicit_variant.str.split("_", n=3, expand=True)
    frame["variant_ref"] = parsed[2].str.upper()
    frame["variant_alt"] = parsed[3].str.upper()
    frame["variant"] = (
        "chr"
        + parsed[0].astype(str)
        + "_"
        + parsed[1].astype(str)
        + "_"
        + frame["variant_ref"]
        + "_"
        + frame["variant_alt"]
    )

    effect = frame["effect_allele"].astype(str).str.upper()
    other = frame["other_allele"].astype(str).str.upper()
    aligned = (effect == frame["variant_alt"]) & (other == frame["variant_ref"])
    reversed_effect = (effect == frame["variant_ref"]) & (
        other == frame["variant_alt"]
    )
    beta = (
        pd.to_numeric(frame["beta"], errors="coerce")
        if "beta" in frame
        else pd.Series(np.nan, index=frame.index)
    )
    frame["beta_alt"] = np.where(
        aligned,
        beta,
        np.where(reversed_effect, -beta, np.nan),
    )
    z_score = (
        pd.to_numeric(frame["z"], errors="coerce")
        if "z" in frame
        else pd.Series(np.nan, index=frame.index)
    )
    frame["z_alt"] = np.where(
        aligned,
        z_score,
        np.where(reversed_effect, -z_score, np.nan),
    )
    if "standard_error" not in frame:
        frame["standard_error"] = np.nan
    frame["standard_error"] = pd.to_numeric(
        frame["standard_error"], errors="coerce"
    )
    frame = frame.dropna(subset=["variant"])
    return frame.drop_duplicates(subset=["variant"], keep="first")


def prepare_eqtl(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["ref"] = frame["ref"].str.upper()
    frame["alt"] = frame["alt"].str.upper()
    frame["variant"] = (
        "chr"
        + frame["chromosome"].astype(str).str.replace("chr", "", regex=False)
        + "_"
        + frame["position"].astype(int).astype(str)
        + "_"
        + frame["ref"]
        + "_"
        + frame["alt"]
    )
    frame = frame.dropna(subset=["beta", "se", "variant"])
    frame = frame[frame["se"] > 0]
    return frame.drop_duplicates(subset=["molecular_trait_id", "variant"], keep="first")


def evidence_label(h2: float, h3: float, h4: float) -> str:
    conditional_h4 = h4 / (h3 + h4) if h3 + h4 > 0 else 0.0
    if h4 >= 0.80 and conditional_h4 >= 0.90:
        return "strong_colocalisation"
    if h4 >= 0.50:
        return "suggestive_colocalisation"
    if h2 >= max(h3, h4):
        return "eqtl_signal_without_regional_gwas_support"
    if h3 > h4:
        return "distinct_signals_preferred"
    return "insufficient_colocalisation"


def run_pair(
    gwas: pd.DataFrame,
    eqtl: pd.DataFrame,
    p12: float,
    gwas_accession: str,
) -> dict:
    merged = gwas.merge(
        eqtl,
        on="variant",
        how="inner",
        suffixes=("_gwas", "_eqtl"),
    )
    merged = merged.replace([np.inf, -np.inf], np.nan)
    merged["gwas_beta_for_abf"] = merged["beta_alt"]
    merged["gwas_se_for_abf"] = merged["standard_error"]
    merged["gwas_effect_method"] = "reported_beta_se"

    sample_info = GWAS_SAMPLE_INFO.get(gwas_accession)
    fallback = (
        merged["gwas_beta_for_abf"].isna()
        | merged["gwas_se_for_abf"].isna()
        | (merged["gwas_se_for_abf"] <= 0)
    )
    if fallback.any() and sample_info:
        total_n = sample_info["cases"] + sample_info["controls"]
        case_fraction = sample_info["cases"] / total_n
        maf = pd.to_numeric(merged["maf"], errors="coerce")
        valid_maf = maf.between(0.001, 0.499)
        variance = 1.0 / (
            2.0
            * total_n
            * case_fraction
            * (1.0 - case_fraction)
            * maf
            * (1.0 - maf)
        )
        can_approximate = fallback & valid_maf & merged["z_alt"].notna()
        merged.loc[can_approximate, "gwas_se_for_abf"] = np.sqrt(
            variance[can_approximate]
        )
        merged.loc[can_approximate, "gwas_beta_for_abf"] = (
            merged.loc[can_approximate, "z_alt"]
            * merged.loc[can_approximate, "gwas_se_for_abf"]
        )
        merged.loc[can_approximate, "gwas_effect_method"] = (
            "z_with_eqtl_maf_proxy"
        )

    merged = merged.dropna(
        subset=["gwas_beta_for_abf", "gwas_se_for_abf", "beta_eqtl", "se"]
    )
    merged = merged[
        (merged["gwas_se_for_abf"] > 0)
        & (merged["se"] > 0)
    ]
    if len(merged) < MIN_SHARED_VARIANTS:
        return {
            "shared_variants": len(merged),
            "analysis_status": "insufficient_shared_variants",
        }

    gwas_log_abf = wakefield_log_abf(
        merged["gwas_beta_for_abf"].to_numpy(float),
        merged["gwas_se_for_abf"].to_numpy(float),
        CASE_CONTROL_PRIOR_SD,
    )
    eqtl_log_abf = wakefield_log_abf(
        merged["beta_eqtl"].to_numpy(float),
        merged["se"].to_numpy(float),
        QUANTITATIVE_PRIOR_SD,
    )
    posteriors = coloc_posteriors(gwas_log_abf, eqtl_log_abf, p12)

    gwas_top = merged.iloc[int(np.argmax(gwas_log_abf))]
    eqtl_top = merged.iloc[int(np.argmax(eqtl_log_abf))]
    shared_top = merged.iloc[int(np.argmax(gwas_log_abf + eqtl_log_abf))]
    conditional_h4 = posteriors["PP.H4"] / (
        posteriors["PP.H3"] + posteriors["PP.H4"]
    )
    return {
        "shared_variants": len(merged),
        "analysis_status": "complete",
        "gwas_effect_method": "|".join(
            sorted(merged["gwas_effect_method"].unique())
        ),
        **posteriors,
        "PP.H4_given_H3_or_H4": conditional_h4,
        "evidence_class": evidence_label(
            posteriors["PP.H2"], posteriors["PP.H3"], posteriors["PP.H4"]
        ),
        "top_gwas_variant": gwas_top["variant"],
        "top_gwas_p": gwas_top["p_value"],
        "top_eqtl_variant": eqtl_top["variant"],
        "top_eqtl_p": eqtl_top["pvalue"],
        "top_shared_variant": shared_top["variant"],
    }


def make_diagnostic_figure(primary: pd.DataFrame, output_stem: Path) -> None:
    complete = primary[primary["analysis_status"] == "complete"].copy()
    if complete.empty:
        return
    complete["context"] = (
        complete["study_label"]
        + " | "
        + complete["sample_group"]
        + " | "
        + complete["molecular_trait_id"]
    )
    matrix = complete.pivot_table(
        index="context", columns="gene_symbol", values="PP.H4", aggfunc="max"
    )
    matrix = matrix.reindex(columns=[gene for gene in ("FCRL3", "FCRL5") if gene in matrix])

    fig_height = max(3.2, 0.32 * len(matrix) + 1.4)
    fig, ax = plt.subplots(figsize=(6.6, fig_height))
    values = matrix.to_numpy(float)
    image = ax.imshow(values, aspect="auto", vmin=0, vmax=1, cmap="viridis")
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            if np.isfinite(value):
                text_color = "white" if value < 0.45 else "black"
                ax.text(
                    column_index,
                    row_index,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color=text_color,
                )
    ax.set_xticks(np.arange(len(matrix.columns)), matrix.columns.tolist())
    ax.set_yticks(np.arange(len(matrix.index)), matrix.index.tolist())
    colorbar = fig.colorbar(image, ax=ax, shrink=0.72, pad=0.03)
    colorbar.set_label("Colocalisation posterior PP.H4", fontsize=8)
    colorbar.ax.tick_params(labelsize=7)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("SLE GWAS and B-cell eQTL colocalisation", fontsize=10, pad=10)
    ax.tick_params(axis="x", rotation=0, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=7)
    fig.subplots_adjust(left=0.49, right=0.91, top=0.91, bottom=0.08)
    fig.savefig(output_stem.with_suffix(".png"), dpi=600, bbox_inches="tight")
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regulatory-dir",
        type=Path,
        default=root / "03_results" / "regulatory_evidence",
    )
    parser.add_argument("--gwas-accession", default="GCST90558100")
    parser.add_argument(
        "--gwas-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--make-figure",
        action="store_true",
        help="Create an exploratory PP.H4 heatmap after the statistical run.",
    )
    args = parser.parse_args()

    eqtl_dir = args.regulatory_dir / "eqtl_catalogue"
    gwas_dir = args.gwas_dir or (args.regulatory_dir / "gwas_loci")
    tables_dir = args.regulatory_dir / "tables"
    figures_dir = args.regulatory_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    result_rows: list[dict] = []
    for eqtl_path in sorted(eqtl_dir.glob("*.tsv.gz")):
        eqtl_all = prepare_eqtl(pd.read_csv(eqtl_path, sep="\t", compression="gzip"))
        gene_symbol = str(eqtl_all["gene_symbol"].iloc[0])
        gwas_path = (
            gwas_dir
            / f"{args.gwas_accession}_{gene_symbol}_plusminus1Mb.tsv.gz"
        )
        if not gwas_path.exists():
            continue
        gwas = prepare_gwas(gwas_path)

        metadata_columns = [
            "dataset_id",
            "study_id",
            "study_label",
            "sample_group",
            "sample_size",
            "quant_method",
            "evidence_tier",
        ]
        metadata = {column: eqtl_all[column].iloc[0] for column in metadata_columns}
        for trait_id, eqtl in eqtl_all.groupby("molecular_trait_id"):
            for p12 in P12_SENSITIVITY:
                result_rows.append(
                    {
                        **metadata,
                        "gene_symbol": gene_symbol,
                        "molecular_trait_id": trait_id,
                        "p1": P1,
                        "p2": P2,
                        "p12": p12,
                        "prior_sensitivity": p12 != PRIMARY_P12,
                        **run_pair(gwas, eqtl, p12, args.gwas_accession),
                    }
                )

    results = pd.DataFrame(result_rows)
    results.to_csv(
        tables_dir / f"{args.gwas_accession}_bcell_colocalisation_all_priors.csv",
        index=False,
    )
    primary = results[results["p12"] == PRIMARY_P12].copy()
    primary.to_csv(
        tables_dir / f"{args.gwas_accession}_bcell_colocalisation_primary.csv",
        index=False,
    )

    if args.make_figure:
        make_diagnostic_figure(
            primary,
            figures_dir
            / f"{args.gwas_accession}_regulatory_colocalisation_diagnostic",
        )

    complete = primary[primary["analysis_status"] == "complete"]
    effect_methods = (
        sorted(complete["gwas_effect_method"].dropna().unique())
        if "gwas_effect_method" in complete
        else []
    )
    strong = (
        complete[complete["evidence_class"] == "strong_colocalisation"]
        if "evidence_class" in complete
        else complete
    )
    summary_lines = [
        "# Regulatory colocalisation summary",
        "",
        f"- Prespecified eQTL traits analysed: {len(primary)}",
        f"- Complete tests with >= {MIN_SHARED_VARIANTS} variants: {len(complete)}",
        f"- Strong colocalisations: {len(strong)}",
        "- Primary priors: p1=1e-4, p2=1e-4, p12=1e-5",
        f"- GWAS accession: {args.gwas_accession}",
        f"- GWAS effect input: {', '.join(effect_methods) if effect_methods else 'not analysable'}",
        "",
        "## Primary results",
        "",
    ]
    if complete.empty:
        summary_lines.append("No gene-context pair had enough shared variants.")
    else:
        for _, row in complete.sort_values("PP.H4", ascending=False).iterrows():
            summary_lines.append(
                f"- {row['gene_symbol']}, {row['study_label']}/{row['sample_group']}, "
                f"{row['molecular_trait_id']}: n={row['shared_variants']}, "
                f"PP.H4={row['PP.H4']:.4f}, "
                f"PP.H3={row['PP.H3']:.4f}, {row['evidence_class']}."
            )

    summary_path = (
        args.regulatory_dir
        / f"{args.gwas_accession}_regulatory_colocalisation_summary.md"
    )
    summary_path.write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )
    metadata = {
        "method": "Wakefield approximate Bayes factors, coloc.abf-equivalent equations",
        "gwas_accession": args.gwas_accession,
        "gwas_sample_info": GWAS_SAMPLE_INFO.get(args.gwas_accession),
        "gwas_effect_methods": effect_methods,
        "maf_proxy_caveat": (
            "When beta and standard error were unavailable, the case-control "
            "variance approximation used the matched B-cell eQTL MAF as a "
            "European-frequency proxy."
        ),
        "case_control_prior_sd": CASE_CONTROL_PRIOR_SD,
        "quantitative_prior_sd": QUANTITATIVE_PRIOR_SD,
        "p1": P1,
        "p2": P2,
        "p12_values": P12_SENSITIVITY,
        "minimum_shared_variants": MIN_SHARED_VARIANTS,
        "allele_alignment": "GRCh38 CHR_POS_REF_ALT; ALT is the effect allele",
    }
    (tables_dir / f"{args.gwas_accession}_colocalisation_method_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    display = (
        primary.sort_values("PP.H4", ascending=False)
        if "PP.H4" in primary
        else primary
    )
    print(display.to_string(index=False))
    print(f"\nSummary: {summary_path}")


if __name__ == "__main__":
    main()
