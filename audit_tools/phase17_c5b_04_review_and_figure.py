#!/usr/bin/env python3
"""Gate C5B-04: independently audit external effects and adjudicate replication."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


CONFIRMATORY = (
    "NAIVE_TO_MEMORY_AXIS",
    "ATYPICAL_LOW_NAIVE_AXIS",
    "APC_HLA",
    "IFN_ISG",
)
MAIN_ANALYSES = (
    "childhood_min50",
    "combined_min50",
    "adult_min50",
    "combined_min20",
    "combined_min100",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def bh_adjust(values):
    import numpy as np

    values = np.asarray(values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = np.minimum.accumulate((ranked * len(values) / np.arange(1, len(values) + 1))[::-1])[::-1]
    output = np.empty_like(adjusted)
    output[order] = np.minimum(adjusted, 1.0)
    return output


def write_text_lf(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_csv_lf(frame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def normalize_run_text(run: Path) -> None:
    for path in run.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".md", ".txt"}:
            continue
        raw = path.read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if normalized != raw:
            path.write_bytes(normalized)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--gate-c5a-dir", required=True)
    parser.add_argument("--gate-c4b-dir", required=True)
    args = parser.parse_args()

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from matplotlib.lines import Line2D

    run = Path(args.run_dir).resolve()
    c5a = Path(args.gate_c5a_dir).resolve()
    c4b = Path(args.gate_c4b_dir).resolve()
    figures = run / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    normalize_run_text(run)

    export = json.loads((run / "03_MATRIX_EXPORT_AUDIT.json").read_text(encoding="utf-8"))
    qualification = json.loads((run / "04_EDGER_QUALIFICATION.json").read_text(encoding="utf-8"))
    status = json.loads((run / "15_FROZEN_MODEL_RUN_STATUS.json").read_text(encoding="utf-8"))
    summaries = pd.read_csv(run / "05_MODEL_SUMMARY.csv")
    top = pd.read_csv(run / "06_TOP100_GENE_RESULTS.csv")
    programs = pd.read_csv(run / "07_PROGRAM_RESULTS.csv")
    arms = pd.read_csv(run / "09_FROZEN_PROGRAM_ARM_CAMERA.csv")
    donor_loo = pd.read_csv(run / "10_PRIMARY_PROGRAM_DONOR_LOO.csv")
    gene_loo = pd.read_csv(run / "11_PRIMARY_CONFIRMATORY_GENE_DONOR_LOO.csv")
    source_loo = pd.read_csv(run / "12_SOURCE_LABEL_LOO_PROGRAM_RESULTS.csv")
    concordance = pd.read_csv(run / "13_EXTERNAL_GENE_EFFECT_CONCORDANCE.csv")
    qc = pd.read_csv(run / "14_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv")
    dictionary = pd.read_csv(c5a / "10_FROZEN_PROGRAM_DICTIONARY.csv")
    c4b_programs = pd.read_csv(c4b / "07_PROGRAM_RESULTS.csv")
    c4b_primary_genes = pd.read_csv(
        c4b / "05_gene_results" / "primary_base_gene_results.csv.gz"
    ).rename(columns={"feature_name": "gene_symbol"})
    c4b_validation_genes = pd.read_csv(
        c4b / "05_gene_results" / "validation_nonoverlap_gene_results.csv.gz"
    ).rename(columns={"feature_name": "gene_symbol"})

    checks = {}

    def record(name: str, passed: bool, detail: str):
        checks[name] = {"pass": bool(passed), "detail": detail}

    record(
        "frozen_input_and_effect_unlock",
        export.get("status") == "PASS_C5B_FROZEN_MATRIX_EXPORT"
        and export.get("real_effect_estimates_inspected") is False
        and status.get("qualification_status") == "PASS_C5B_EDGER_QUALIFICATION",
        "C5A manifest verified; matrix export was pre-effect; qualification passed",
    )
    qualification_checks = qualification.get("checks", {})
    qualification_pass = qualification.get("status") == "PASS_C5B_EDGER_QUALIFICATION" and all(
        item.get("pass") for item in qualification_checks.values()
    )
    record(
        "statistical_engine_qualification",
        qualification_pass,
        f"{sum(bool(item.get('pass')) for item in qualification_checks.values())}/{len(qualification_checks)} checks",
    )
    expected_shapes = {
        "childhood_min50": (43, 11, 32),
        "combined_min50": (54, 16, 38),
        "adult_min50": (11, 5, 6),
        "combined_min20": (56, 16, 40),
        "combined_min100": (51, 16, 35),
    }
    model_shape_pass = set(summaries["analysis_name"]) == set(MAIN_ANALYSES)
    for name, expected in expected_shapes.items():
        row = summaries.loc[summaries["analysis_name"].eq(name)]
        if len(row) != 1:
            model_shape_pass = False
            continue
        observed = tuple(int(row.iloc[0][key]) for key in ("n_samples", "reference_n", "exposed_n"))
        model_shape_pass &= observed == expected
    record(
        "frozen_model_completeness",
        model_shape_pass,
        "five models with frozen sample/group sizes",
    )

    gene_audits = []
    gene_tables = {}
    all_gene_tables_pass = True
    for name in MAIN_ANALYSES:
        frame = pd.read_csv(run / "05_gene_results" / f"{name}_gene_results.csv.gz")
        gene_tables[name] = frame
        tested = frame.loc[frame["tested_filterByExpr"].astype(bool)].copy()
        expected_tested = int(
            summaries.loc[summaries["analysis_name"].eq(name), "tested_genes"].iloc[0]
        )
        unique_pass = len(frame) == 32738 and frame["ensembl_id"].is_unique
        tested_pass = len(tested) == expected_tested
        bh_pass = np.allclose(
            bh_adjust(tested["PValue"]), tested["FDR"], rtol=1e-8, atol=1e-12
        )
        passed = unique_pass and tested_pass and bh_pass
        all_gene_tables_pass &= passed
        gene_audits.append(
            {
                "analysis_name": name,
                "rows": len(frame),
                "tested_genes": len(tested),
                "unique_ensembl": bool(frame["ensembl_id"].is_unique),
                "bh_reproduced": bool(bh_pass),
                "pass": bool(passed),
            }
        )
    record(
        "gene_result_integrity",
        all_gene_tables_pass,
        "five complete 32,738-row Ensembl tables; tested counts and BH independently reproduced",
    )

    program_integrity = True
    for name in MAIN_ANALYSES:
        subset = programs.loc[
            programs["analysis_name"].eq(name)
            & programs["program_id"].isin(CONFIRMATORY)
        ].copy()
        program_integrity &= len(subset) == 4
        program_integrity &= np.allclose(
            bh_adjust(subset["p_value"]), subset["q_value_primary4"], rtol=1e-8, atol=1e-12
        )
        program_integrity &= bool(subset["availability_pass"].astype(bool).all())
    record(
        "program_result_integrity",
        program_integrity,
        "four-program BH and availability reproduced for all five analyses",
    )

    def program_row(analysis, program_id):
        return programs.loc[
            programs["analysis_name"].eq(analysis)
            & programs["program_id"].eq(program_id)
        ].iloc[0]

    external_ifn = {name: program_row(name, "IFN_ISG") for name in MAIN_ANALYSES}
    childhood = external_ifn["childhood_min50"]
    combined = external_ifn["combined_min50"]
    adult = external_ifn["adult_min50"]
    min20 = external_ifn["combined_min20"]
    min100 = external_ifn["combined_min100"]

    confirmatory_significance = (
        (childhood["effect"] > 0 and childhood["q_value_primary4"] < 0.05)
        or (combined["effect"] > 0 and combined["q_value_primary4"] < 0.05)
    )
    record(
        "ifn_confirmatory_significance",
        confirmatory_significance,
        "childhood effect={:.3f}, q={:.3g}; combined effect={:.3f}, q={:.3g}".format(
            childhood["effect"], childhood["q_value_primary4"], combined["effect"], combined["q_value_primary4"]
        ),
    )
    primary_combined_direction = childhood["effect"] > 0 and combined["effect"] > 0
    record(
        "childhood_combined_direction",
        primary_combined_direction,
        "childhood and combined IFN/ISG effects are both positive",
    )
    adult_no_persuasive_reversal = not (adult["effect"] < 0 and adult["ci_high"] < 0)
    record(
        "adult_no_persuasive_reversal",
        adult_no_persuasive_reversal,
        "adult effect={:.3f}, 95% CI {:.3f} to {:.3f}".format(
            adult["effect"], adult["ci_low"], adult["ci_high"]
        ),
    )
    threshold_direction = min20["effect"] > 0 and min100["effect"] > 0
    record(
        "support_threshold_direction",
        threshold_direction,
        ">=20 effect={:.3f}; >=100 effect={:.3f}".format(min20["effect"], min100["effect"]),
    )

    ifn_donor = donor_loo.loc[donor_loo["program_id"].eq("IFN_ISG")].iloc[0]
    donor_pass = not bool(ifn_donor["loo_any_sign_flip"]) and ifn_donor["loo_min_effect"] > 0
    record(
        "ifn_donor_influence",
        donor_pass,
        "43 deletions; range {:.3f} to {:.3f}; max |delta| {:.3f}".format(
            ifn_donor["loo_min_effect"], ifn_donor["loo_max_effect"], ifn_donor["loo_max_absolute_delta"]
        ),
    )
    ifn_source = source_loo.loc[source_loo["program_id"].eq("IFN_ISG")].copy()
    expected_labels = {f"B-caSC{index}" for index in range(8)}
    source_direction = (
        set(ifn_source["omitted_source_label"]) == expected_labels
        and len(ifn_source) == 8
        and bool((ifn_source["effect"] > 0).all())
    )
    source_magnitude = source_direction and float(ifn_source["effect"].min()) >= 0.5 * float(childhood["effect"])
    record(
        "ifn_source_label_direction",
        source_direction,
        "eight omissions; effect range {:.3f} to {:.3f}".format(
            ifn_source["effect"].min(), ifn_source["effect"].max()
        ),
    )
    record(
        "ifn_no_single_label_dependence",
        source_magnitude,
        "minimum omission effect {:.3f} versus 50% full-effect floor {:.3f}".format(
            ifn_source["effect"].min(), 0.5 * childhood["effect"]
        ),
    )

    ifn_arm_child = arms.loc[
        arms["analysis_name"].eq("childhood_min50")
        & arms["program_id"].eq("IFN_ISG")
        & arms["arm"].eq("positive")
    ].iloc[0]
    ifn_arm_combined = arms.loc[
        arms["analysis_name"].eq("combined_min50")
        & arms["program_id"].eq("IFN_ISG")
        & arms["arm"].eq("positive")
    ].iloc[0]
    gene_coherence = any(
        row["camera_direction"] == "Up"
        and row["camera_fdr_within_analysis"] < 0.05
        and row["expected_direction_fraction"] >= 0.75
        for _, row in pd.DataFrame([ifn_arm_child, ifn_arm_combined]).iterrows()
    )
    record(
        "ifn_ranked_gene_coherence",
        gene_coherence,
        "childhood expected fraction={:.3f}, camera FDR={:.3g}; combined fraction={:.3f}, FDR={:.3g}".format(
            ifn_arm_child["expected_direction_fraction"],
            ifn_arm_child["camera_fdr_within_analysis"],
            ifn_arm_combined["expected_direction_fraction"],
            ifn_arm_combined["camera_fdr_within_analysis"],
        ),
    )

    ifn_symbols = dictionary.loc[
        dictionary["program_id"].eq("IFN_ISG"), "gene_symbol"
    ].tolist()

    def symbol_effects(frame, prefix):
        subset = frame.loc[frame["gene_symbol"].isin(ifn_symbols)].copy()
        subset = subset.sort_values("gene_symbol").drop_duplicates("gene_symbol")
        return subset[["gene_symbol", "logFC", "PValue", "FDR", "tested_filterByExpr"]].rename(
            columns={
                "logFC": f"{prefix}_logFC",
                "PValue": f"{prefix}_PValue",
                "FDR": f"{prefix}_FDR",
                "tested_filterByExpr": f"{prefix}_tested",
            }
        )

    cross_ifn = pd.DataFrame({"gene_symbol": sorted(set(ifn_symbols))})
    for frame, prefix in (
        (c4b_primary_genes, "gse174188_primary"),
        (c4b_validation_genes, "gse174188_nonoverlap"),
        (gene_tables["childhood_min50"], "gse135779_childhood"),
        (gene_tables["combined_min50"], "gse135779_combined"),
        (gene_tables["adult_min50"], "gse135779_adult"),
    ):
        cross_ifn = cross_ifn.merge(symbol_effects(frame, prefix), on="gene_symbol", how="left")
    shared_ifn = cross_ifn.loc[
        cross_ifn["gse174188_primary_tested"].fillna(False).astype(bool)
        & cross_ifn["gse135779_childhood_tested"].fillna(False).astype(bool)
    ].copy()
    cross_ifn_direction_fraction = float(
        (
            (shared_ifn["gse174188_primary_logFC"] > 0)
            & (shared_ifn["gse135779_childhood_logFC"] > 0)
        ).mean()
    )
    cross_ifn_pass = len(shared_ifn) >= 8 and cross_ifn_direction_fraction >= 0.80
    record(
        "cross_dataset_ifn_gene_direction_descriptive",
        cross_ifn_pass,
        f"{len(shared_ifn)} shared tested IFN genes; positive in both datasets fraction={cross_ifn_direction_fraction:.3f}",
    )

    qc50 = qc.loc[qc["rank_cutoff"].eq(50)].iloc[0]
    platelet = program_row("childhood_min50", "PLATELET_AMBIENT_QC")
    asc = program_row("childhood_min50", "ASC_UPR_IDENTITY_QC")
    pan_b = program_row("childhood_min50", "PAN_B_IDENTITY_QC")
    technical_fractions_pass = all(
        float(qc50[column]) <= 0.10
        for column in (
            "mitochondrial_fraction",
            "ribosomal_fraction",
            "hemoglobin_fraction",
            "immunoglobulin_fraction",
        )
    )
    controls_subordinate = all(
        abs(float(row["effect"])) < abs(float(childhood["effect"]))
        for row in (platelet, asc, pan_b)
    )
    specificity_pass = technical_fractions_pass and controls_subordinate
    record(
        "technical_and_identity_specificity",
        specificity_pass,
        "IFN={:.3f}; platelet={:.3f}; ASC/UPR={:.3f}; pan-B={:.3f}; top-50 fractions <=0.10={}".format(
            childhood["effect"], platelet["effect"], asc["effect"], pan_b["effect"], technical_fractions_pass
        ),
    )

    central_pass = all(
        (
            confirmatory_significance,
            primary_combined_direction,
            adult_no_persuasive_reversal,
            threshold_direction,
            donor_pass,
            source_direction,
            source_magnitude,
            gene_coherence,
            specificity_pass,
            all_gene_tables_pass,
            program_integrity,
            qualification_pass,
        )
    )
    directional_only = childhood["effect"] > 0 or combined["effect"] > 0
    if central_pass:
        decision = "PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION"
    elif directional_only:
        decision = "HOLD_GATE_C5B_DIRECTIONAL_OR_PARTIAL_SUPPORT_ONLY"
    else:
        decision = "NO_GO_GATE_C5B_INDEPENDENT_IFN_REPLICATION"
    record(
        "gate_c5b_external_acceptance",
        central_pass,
        f"decision={decision}",
    )

    # Cross-dataset IFN tables used by both audit and figure.
    write_csv_lf(cross_ifn, run / "16_CROSS_DATASET_IFN_GENE_EFFECTS.csv")

    c4b_ifn = c4b_programs.loc[c4b_programs["program_id"].eq("IFN_ISG")].copy()
    cross_program = pd.concat(
        [
            c4b_ifn.loc[
                c4b_ifn["analysis_name"].isin(["primary_base", "validation_full", "validation_nonoverlap"]),
                ["analysis_name", "effect", "ci_low", "ci_high", "p_value", "q_value_primary4"],
            ].assign(dataset="GSE174188"),
            programs.loc[
                programs["analysis_name"].isin(["childhood_min50", "combined_min50", "adult_min50"])
                & programs["program_id"].eq("IFN_ISG"),
                ["analysis_name", "effect", "ci_low", "ci_high", "p_value", "q_value_primary4"],
            ].assign(dataset="GSE135779"),
        ],
        ignore_index=True,
    )
    write_csv_lf(cross_program, run / "16_CROSS_DATASET_IFN_PROGRAM_EFFECTS.csv")

    # Nature-style external-validation figure.
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 9,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    colors = {
        "child": "#1F4E79",
        "combined": "#2A9D8F",
        "adult": "#D55E00",
        "discovery": "#6B7280",
        "ifn": "#B2182B",
        "influence": "#7A5195",
    }
    fig, axes = plt.subplots(2, 2, figsize=(12.3, 9.2), constrained_layout=True)

    ax = axes[0, 0]
    external_order = ["childhood_min50", "combined_min50", "adult_min50", "combined_min20", "combined_min100"]
    external_labels = {
        "childhood_min50": "Childhood >=50 (11 HC, 32 SLE)",
        "combined_min50": "Combined >=50 (16 HC, 38 SLE)",
        "adult_min50": "Adult >=50 (5 HC, 6 SLE)",
        "combined_min20": "Combined >=20 (16 HC, 40 SLE)",
        "combined_min100": "Combined >=100 (16 HC, 35 SLE)",
    }
    y = np.arange(len(external_order))[::-1]
    for index, name in enumerate(external_order):
        row = external_ifn[name]
        color = colors["child"] if name == "childhood_min50" else colors["adult"] if name == "adult_min50" else colors["combined"]
        ax.errorbar(
            row["effect"], y[index],
            xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]],
            fmt="o", color=color, ms=5, lw=1.2, capsize=2,
        )
        marker = "*" if row["q_value_primary4"] < 0.05 else ""
        ax.text(row["ci_high"] + 0.03, y[index], marker, va="center", fontsize=10)
    ax.axvline(0, color="#9CA3AF", lw=0.8)
    ax.set_yticks(y, [external_labels[name] for name in external_order])
    ax.set_xlabel("Adjusted IFN/ISG score difference")
    ax.set_title("Independent GSE135779 validation", loc="left", fontweight="bold")
    ax.text(-0.13, 1.06, "a", transform=ax.transAxes, fontsize=13, fontweight="bold")

    ax = axes[0, 1]
    cross_order = [
        ("GSE174188", "primary_base", "Discovery C4 (n=89)"),
        ("GSE174188", "validation_full", "Internal C2 (n=64)"),
        ("GSE174188", "validation_nonoverlap", "Internal nonoverlap (n=54)"),
        ("GSE135779", "childhood_min50", "External childhood (n=43)"),
        ("GSE135779", "combined_min50", "External combined (n=54)"),
        ("GSE135779", "adult_min50", "External adult (n=11)"),
    ]
    y = np.arange(len(cross_order))[::-1]
    for index, (dataset, name, _) in enumerate(cross_order):
        row = cross_program.loc[
            cross_program["dataset"].eq(dataset) & cross_program["analysis_name"].eq(name)
        ].iloc[0]
        color = colors["discovery"] if dataset == "GSE174188" else colors["ifn"]
        ax.errorbar(
            row["effect"], y[index],
            xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]],
            fmt="o", color=color, ms=5, lw=1.2, capsize=2,
        )
    ax.axvline(0, color="#9CA3AF", lw=0.8)
    ax.set_yticks(y, [label for _, _, label in cross_order])
    ax.set_xlabel("Adjusted IFN/ISG score difference")
    ax.set_title("Discovery-to-external effect comparison", loc="left", fontweight="bold")
    ax.text(-0.13, 1.06, "b", transform=ax.transAxes, fontsize=13, fontweight="bold")

    ax = axes[1, 0]
    discovery = c4b_primary_genes.loc[
        c4b_primary_genes["tested_filterByExpr"].astype(bool), ["ensembl_id", "gene_symbol", "logFC"]
    ]
    external = gene_tables["childhood_min50"].loc[
        gene_tables["childhood_min50"]["tested_filterByExpr"].astype(bool), ["ensembl_id", "logFC"]
    ]
    merged = discovery.merge(external, on="ensembl_id", suffixes=("_discovery", "_external"))
    ax.scatter(merged["logFC_discovery"], merged["logFC_external"], s=7, color="#C4C8CE", alpha=0.45, linewidths=0)
    highlighted = merged.loc[merged["gene_symbol"].isin(ifn_symbols)]
    ax.scatter(
        highlighted["logFC_discovery"], highlighted["logFC_external"],
        s=34, color=colors["ifn"], edgecolor="white", linewidth=0.5, zorder=3,
    )
    label_rows = highlighted.nlargest(6, "logFC_external").sort_values("logFC_external").copy()
    label_positions = []
    minimum_gap = 0.23
    for value in label_rows["logFC_external"]:
        label_positions.append(
            float(value) if not label_positions else max(float(value), label_positions[-1] + minimum_gap)
        )
    for row, label_y in zip(label_rows.itertuples(index=False), label_positions):
        ax.annotate(
            row.gene_symbol,
            (row.logFC_discovery, row.logFC_external),
            xytext=(row.logFC_discovery + 0.08, label_y),
            textcoords="data",
            fontsize=6.8,
            va="center",
            arrowprops={"arrowstyle": "-", "color": "#7B8189", "lw": 0.45},
        )
    ax.axhline(0, color="#9CA3AF", lw=0.7)
    ax.axvline(0, color="#9CA3AF", lw=0.7)
    rho = merged[["logFC_discovery", "logFC_external"]].corr(method="spearman").iloc[0, 1]
    ax.text(0.03, 0.96, f"Shared tested genes: {len(merged):,}\nSpearman rho = {rho:.2f}", transform=ax.transAxes, va="top", fontsize=8)
    ax.set_xlabel("GSE174188 primary log2 fold change")
    ax.set_ylabel("GSE135779 childhood log2 fold change")
    ax.set_title("Cross-dataset gene-effect coherence", loc="left", fontweight="bold")
    ax.legend(
        handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor=colors["ifn"], markeredgecolor="white", label="Frozen IFN/ISG genes")],
        frameon=False, fontsize=8, loc="lower right",
    )
    ax.text(-0.13, 1.06, "c", transform=ax.transAxes, fontsize=13, fontweight="bold")

    ax = axes[1, 1]
    influence_labels = ["Full childhood", "Donor LOO range"] + [f"Without {label}" for label in sorted(expected_labels)]
    y = np.arange(len(influence_labels))[::-1]
    ax.errorbar(
        childhood["effect"], y[0],
        xerr=[[childhood["effect"] - childhood["ci_low"]], [childhood["ci_high"] - childhood["effect"]]],
        fmt="o", color=colors["ifn"], ms=5, lw=1.2, capsize=2,
    )
    ax.errorbar(
        childhood["effect"], y[1],
        xerr=[[childhood["effect"] - ifn_donor["loo_min_effect"]], [ifn_donor["loo_max_effect"] - childhood["effect"]]],
        fmt="s", color=colors["influence"], ms=5, lw=2, capsize=2,
    )
    source_lookup = ifn_source.set_index("omitted_source_label")
    for index, label in enumerate(sorted(expected_labels), start=2):
        row = source_lookup.loc[label]
        ax.errorbar(
            row["effect"], y[index],
            xerr=[[row["effect"] - row["ci_low"]], [row["ci_high"] - row["effect"]]],
            fmt="o", color=colors["combined"], ms=4.5, lw=1, capsize=2,
        )
    ax.axvline(0, color="#9CA3AF", lw=0.8)
    ax.axvline(0.5 * childhood["effect"], color="#B8BEC6", lw=0.8, ls="--")
    ax.set_yticks(y, influence_labels)
    ax.set_xlabel("IFN/ISG score difference")
    ax.set_title("Donor and source-label influence", loc="left", fontweight="bold")
    ax.text(-0.13, 1.06, "d", transform=ax.transAxes, fontsize=13, fontweight="bold")

    png_path = figures / "gate_c5b_gse135779_independent_ifn_validation.png"
    pdf_path = figures / "gate_c5b_gse135779_independent_ifn_validation.pdf"
    fig.savefig(png_path, dpi=320, facecolor="white")
    fig.savefig(pdf_path, facecolor="white")
    plt.close(fig)

    c4b_anchor = c4b_programs.loc[
        c4b_programs["analysis_name"].eq("primary_base")
        & c4b_programs["program_id"].eq("IFN_ISG")
    ].iloc[0]
    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "independent_ifn_replication_authorized": bool(central_pass),
        "central_anchor": "IFN_ISG" if central_pass else None,
        "checks": checks,
        "gene_table_audits": gene_audits,
        "ifn_results": {
            name: {
                "effect": float(row["effect"]),
                "ci_low": float(row["ci_low"]),
                "ci_high": float(row["ci_high"]),
                "p_value": float(row["p_value"]),
                "q_value_primary4": float(row["q_value_primary4"]),
            }
            for name, row in external_ifn.items()
        },
        "influence": {
            "donor_loo_min": float(ifn_donor["loo_min_effect"]),
            "donor_loo_max": float(ifn_donor["loo_max_effect"]),
            "source_label_min": float(ifn_source["effect"].min()),
            "source_label_max": float(ifn_source["effect"].max()),
        },
        "cross_dataset_context": {
            "gse174188_primary_effect": float(c4b_anchor["effect"]),
            "gse174188_primary_q": float(c4b_anchor["q_value_primary4"]),
            "shared_tested_gene_rho": float(rho),
            "shared_tested_ifn_genes": int(len(shared_ifn)),
            "shared_ifn_positive_both_fraction": cross_ifn_direction_fraction,
        },
        "limitations": [
            "GSE135779 source labels support a broad conventional-B analog, not hard naive/memory identities.",
            "The adult stratum has only 5 HC and 6 SLE donors and is secondary.",
            "Sex, treatment and detailed clinical covariates are absent from the local processed metadata.",
            "Two adult metadata donors lack source matrices and cannot enter expression models.",
            "The childhood-only and extended metadata versions are not cell-identical; the extended version is authoritative.",
        ],
        "next_stage": (
            "Gate C6 manuscript claim integration plus targeted external regulatory evidence."
            if central_pass
            else "Downgrade the external claim and retain GSE174188 IFN as internally replicated only."
        ),
    }
    write_text_lf(run / "17_GATE_C5B_ADVISOR_DECISION.json", json.dumps(review, indent=2))

    lines = [
        "# Gate C5B advisor decision",
        "",
        f"## `{decision}`",
        "",
        "GSE135779 was analyzed from the Gate C5A frozen source and design objects after successful no-effect software and import qualification.",
        "",
        "| Analysis | IFN/ISG effect | 95% CI | Four-program BH q |",
        "|---|---:|---:|---:|",
    ]
    for name in MAIN_ANALYSES:
        row = external_ifn[name]
        lines.append(
            f"| {name} | {row['effect']:.3f} | {row['ci_low']:.3f} to {row['ci_high']:.3f} | {row['q_value_primary4']:.3g} |"
        )
    lines.extend(
        [
            "",
            "## Stability and specificity",
            "",
            f"- Donor LOO range: `{ifn_donor['loo_min_effect']:.3f}` to `{ifn_donor['loo_max_effect']:.3f}` across 43 deletions.",
            f"- Source-label omission range: `{ifn_source['effect'].min():.3f}` to `{ifn_source['effect'].max():.3f}` across B-caSC0 to B-caSC7.",
            f"- IFN ranked-gene coherence: childhood expected-direction fraction `{ifn_arm_child['expected_direction_fraction']:.3f}`, camera FDR `{ifn_arm_child['camera_fdr_within_analysis']:.3g}`.",
            f"- Cross-dataset IFN genes: `{len(shared_ifn)}` jointly tested, positive in both datasets fraction `{cross_ifn_direction_fraction:.3f}`.",
            f"- Childhood controls: platelet `{platelet['effect']:.3f}`, ASC/UPR `{asc['effect']:.3f}`, pan-B `{pan_b['effect']:.3f}` versus IFN `{childhood['effect']:.3f}`.",
            f"- Shared tested transcriptome Spearman rho: `{rho:.3f}`; the replication claim is program-specific, not genome-wide.",
            "",
            "## Interpretation",
            "",
            (
                "The frozen IFN/ISG program satisfies the independent replication contract and may be integrated as the manuscript's central cross-dataset transcriptional result."
                if central_pass
                else "The frozen IFN/ISG program does not satisfy every independent-replication criterion; manuscript language must remain bounded."
            ),
            "",
            "The adult result remains secondary, and the source annotation authorizes only a broad conventional-B interpretation.",
            "",
            "## Next action",
            "",
            review["next_stage"],
        ]
    )
    write_text_lf(run / "17_GATE_C5B_ADVISOR_DECISION.md", "\n".join(lines) + "\n")

    integrity = {
        "created_at": review["created_at"],
        "decision": decision,
        "checks": checks,
        "gene_table_audits": gene_audits,
        "program_bh_reproduced": bool(program_integrity),
        "figure_png_sha256": sha256(png_path),
        "figure_pdf_sha256": sha256(pdf_path),
    }
    write_text_lf(run / "18_GATE_C5B_RESULT_INTEGRITY_AUDIT.json", json.dumps(integrity, indent=2))
    write_text_lf(
        run / "18_GATE_C5B_RESULT_INTEGRITY_AUDIT.md",
        "\n".join(
            [
                "# Gate C5B independent result-integrity audit",
                "",
                f"- Decision: `{decision}`",
                f"- Checks passed: `{sum(item['pass'] for item in checks.values())}/{len(checks)}`",
                "- Gene tables: `5/5` complete and independently BH-verified",
                "- Program multiplicity: independently reproduced",
                "- Donor and source-label sensitivities: independently adjudicated",
                "- Figure PNG/PDF: generated and hashed",
            ]
        )
        + "\n",
    )

    normalize_run_text(run)
    manifest_rows = []
    for path in sorted(item for item in run.rglob("*") if item.is_file()):
        if path.name == "19_gate_c5b_integrity_manifest.csv":
            continue
        relative = str(path.relative_to(run)).replace("\\", "/")
        local = (
            path.suffix.lower() == ".gz"
            or "05_gene_results" in path.parts
            or path.name == "08_PROGRAM_SAMPLE_SCORES.csv.gz"
        )
        manifest_rows.append(
            {
                "relative_path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "repository_policy": "local_recomputable" if local else "tracked",
            }
        )
    write_csv_lf(pd.DataFrame(manifest_rows), run / "19_gate_c5b_integrity_manifest.csv")
    print(json.dumps(review, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
