from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import sparse, stats

from publication_figure_style import PANEL_LABEL_SIZE, apply_nature_style, nature_figsize, save_nature_figure


REFINED_STATE_MAP = {
    "Naive B I": "Resting naive B",
    "Naive B II / SLE-enriched naive-like": "Activated SLE-naive-like B",
    "Memory B I": "Memory-like B I",
    "Mixed naive-memory B": "Mixed / transitional B",
    "Memory B II": "TNFRSF13B+ memory-like B",
    "Atypical / ABC-like B": "Atypical ABC/APC-like B",
    "Naive B III / small naive-like cluster": "Flagged platelet/ambient-high B",
    "Plasmablast / plasma cell": "Plasmablast / ASC",
}

FOCUS_STATE = "Atypical ABC/APC-like B"
FLAGGED_STATE = "Flagged platelet/ambient-high B"

STATE_ORDER = [
    "Resting naive B",
    "Activated SLE-naive-like B",
    "Memory-like B I",
    "Mixed / transitional B",
    "TNFRSF13B+ memory-like B",
    "Atypical ABC/APC-like B",
    "Flagged platelet/ambient-high B",
    "Plasmablast / ASC",
]

SIGNATURES: "OrderedDict[str, dict[str, object]]" = OrderedDict(
    [
        (
            "ABC_DN2_core",
            {
                "positive": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
                "negative": [],
                "anchor": "ABC/DN2-like B-cell literature seed",
                "expected_focus": "high",
            },
        ),
        (
            "ABC_low_naive_context",
            {
                "positive": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
                "negative": ["CR2", "FCER2", "IGHD", "TCL1A"],
                "anchor": "ABC/DN2 identity with low naive-context markers",
                "expected_focus": "high",
            },
        ),
        (
            "ZEB2_ABC_axis",
            {
                "positive": ["ZEB2", "FCRL5", "FCRL3", "HCK", "FGR", "MAP3K8", "TNFRSF1B", "ZBTB32"],
                "negative": [],
                "anchor": "ZEB2-linked ABC formation mechanism",
                "expected_focus": "high",
            },
        ),
        (
            "APC_HLA_B_cell",
            {
                "positive": ["CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "HLA-DQA1", "HLA-DQB1", "B2M", "CIITA", "CD86"],
                "negative": [],
                "anchor": "Antigen-presentation/APC-like B-cell program",
                "expected_focus": "high",
            },
        ),
        (
            "EBV_APC_like_B",
            {
                "positive": ["CD74", "HLA-DRA", "HLA-DRB1", "B2M", "CIITA", "CD86", "CD83", "IRF4"],
                "negative": [],
                "anchor": "EBV-positive APC-like autoreactive B-cell framing",
                "expected_focus": "high",
            },
        ),
        (
            "IFN_ISG",
            {
                "positive": ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6", "LY6E", "IRF7"],
                "negative": [],
                "anchor": "Type I interferon response",
                "expected_focus": "moderate",
            },
        ),
        (
            "TLR7_FTO_innate_axis",
            {
                "positive": ["TLR7", "MYD88", "IRAK1", "IRF7", "NFKB1", "RELA", "DDX58", "IFIH1", "FTO", "ATP6V1G1"],
                "negative": [],
                "anchor": "TLR7-FTO/m6A innate-sensing mechanism",
                "expected_focus": "moderate",
            },
        ),
        (
            "Age_associated_B_like",
            {
                "positive": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "CXCR3", "ZEB2", "TNFRSF1B"],
                "negative": ["CR2", "FCER2", "TCL1A"],
                "anchor": "Age-associated/atypical B-cell marker framing",
                "expected_focus": "high",
            },
        ),
        (
            "Naive_B_control",
            {
                "positive": ["TCL1A", "IGHD", "IGHM", "IL4R", "FCER2", "CCR7", "SELL", "CXCR4", "VPREB3"],
                "negative": [],
                "anchor": "Naive B-cell control",
                "expected_focus": "low",
            },
        ),
        (
            "Memory_B_control",
            {
                "positive": ["CD27", "TNFRSF13B", "AIM2", "BANK1", "CD40", "LTB", "GPR183"],
                "negative": [],
                "anchor": "Memory B-cell control",
                "expected_focus": "low",
            },
        ),
        (
            "Plasmablast_ASC_control",
            {
                "positive": ["MZB1", "XBP1", "PRDM1", "JCHAIN", "SDC1", "IRF4", "TNFRSF17", "DERL3", "FKBP11", "HSP90B1"],
                "negative": [],
                "anchor": "Plasmablast/ASC control",
                "expected_focus": "low",
            },
        ),
        (
            "Platelet_ambient_QC",
            {
                "positive": ["PPBP", "PF4", "NRGN", "TUBB1", "RGS18", "CAVIN2", "GNG11", "SPARC", "MYL9", "CLU"],
                "negative": [],
                "anchor": "Platelet/ambient RNA QC control",
                "expected_focus": "low",
            },
        ),
    ]
)

PATHOGENIC_SIGNATURES = [
    "ABC_DN2_core",
    "ABC_low_naive_context",
    "ZEB2_ABC_axis",
    "APC_HLA_B_cell",
    "EBV_APC_like_B",
    "IFN_ISG",
    "TLR7_FTO_innate_axis",
    "Age_associated_B_like",
]

CONTROL_SIGNATURES = ["Naive_B_control", "Memory_B_control", "Plasmablast_ASC_control", "Platelet_ambient_QC"]

SIGNATURE_REFERENCES = {
    "ABC_DN2_core": (
        "Jenks2018;Wang2018;Sanz2019",
        "10.1016/j.immuni.2018.08.015;10.1038/s41467-018-03750-7;10.3389/fimmu.2019.02458",
    ),
    "ABC_low_naive_context": (
        "Jenks2018;Sanz2019",
        "10.1016/j.immuni.2018.08.015;10.3389/fimmu.2019.02458",
    ),
    "ZEB2_ABC_axis": (
        "Dai2024;Jenks2018",
        "10.1126/science.adf8531;10.1016/j.immuni.2018.08.015",
    ),
    "APC_HLA_B_cell": (
        "Younis2025",
        "10.1126/scitranslmed.ady0210",
    ),
    "EBV_APC_like_B": (
        "Younis2025",
        "10.1126/scitranslmed.ady0210",
    ),
    "IFN_ISG": (
        "Perez2022;NeharBelaid2020",
        "10.1126/science.abf1970;10.1038/s41590-020-0743-0",
    ),
    "TLR7_FTO_innate_axis": (
        "Zeng2025;Jenks2018",
        "10.1126/scitranslmed.adu6015;10.1016/j.immuni.2018.08.015",
    ),
    "Age_associated_B_like": (
        "Dai2024;Wang2018;Sanz2019",
        "10.1126/science.adf8531;10.1038/s41467-018-03750-7;10.3389/fimmu.2019.02458",
    ),
    "Naive_B_control": (
        "Sanz2019;Perez2022",
        "10.3389/fimmu.2019.02458;10.1126/science.abf1970",
    ),
    "Memory_B_control": (
        "Sanz2019;Perez2022",
        "10.3389/fimmu.2019.02458;10.1126/science.abf1970",
    ),
    "Plasmablast_ASC_control": (
        "Tipton2015;Sanz2019",
        "10.1038/ni.3175;10.3389/fimmu.2019.02458",
    ),
    "Platelet_ambient_QC": (
        "Internal marker-based QC panel",
        "",
    ),
}


def unique_preserving_order(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def to_csr(matrix) -> sparse.csr_matrix:
    if sparse.issparse(matrix):
        return matrix.tocsr()
    return sparse.csr_matrix(matrix)


def row_sums_backed(matrix, n_rows: int, chunk_size: int) -> np.ndarray:
    sums = np.zeros(n_rows, dtype=float)
    for start in range(0, n_rows, chunk_size):
        stop = min(start + chunk_size, n_rows)
        chunk = matrix[start:stop, :]
        if sparse.issparse(chunk):
            sums[start:stop] = np.asarray(chunk.sum(axis=1)).ravel()
        else:
            sums[start:stop] = np.asarray(chunk).sum(axis=1)
    return sums


def build_gene_index(var: pd.DataFrame, gene_symbol_column: str, genes: list[str]) -> tuple[list[str], list[int], list[str]]:
    if gene_symbol_column and gene_symbol_column in var.columns:
        symbols = var[gene_symbol_column].astype(str)
    else:
        symbols = pd.Series(var.index.astype(str), index=var.index)
    symbol_to_idx: dict[str, int] = {}
    for idx, symbol in enumerate(symbols):
        symbol_to_idx.setdefault(str(symbol), idx)
    present = [gene for gene in genes if gene in symbol_to_idx]
    missing = [gene for gene in genes if gene not in symbol_to_idx]
    indices = [symbol_to_idx[gene] for gene in present]
    return present, indices, missing


def aggregate_by_group(counts: sparse.csr_matrix, total_counts: np.ndarray, metadata: pd.DataFrame, group_cols: list[str]) -> tuple[pd.DataFrame, sparse.csr_matrix, np.ndarray]:
    group_frame = metadata[group_cols].astype(str)
    group_key = group_frame.agg("||".join, axis=1)
    codes, uniques = pd.factorize(group_key, sort=False)
    indicator = sparse.csr_matrix((np.ones(len(codes), dtype=np.float32), (codes, np.arange(len(codes)))), shape=(len(uniques), len(codes)))
    grouped_counts = indicator @ counts
    grouped_totals = np.bincount(codes, weights=total_counts, minlength=len(uniques)).astype(float)
    n_cells = np.bincount(codes, minlength=len(uniques)).astype(int)
    groups = pd.Series(uniques, name="group_key").str.split(r"\|\|", expand=True)
    groups.columns = group_cols
    groups["n_cells"] = n_cells
    groups["total_raw_counts"] = grouped_totals
    return groups, grouped_counts.tocsr(), grouped_totals


def long_gene_table(groups: pd.DataFrame, counts: sparse.csr_matrix, totals: np.ndarray, genes: list[str]) -> pd.DataFrame:
    dense_counts = counts.toarray().astype(float)
    safe_totals = totals.copy()
    safe_totals[safe_totals <= 0] = np.nan
    cp10k = dense_counts / safe_totals[:, None] * 10000.0
    log_cp10k = np.log1p(cp10k)
    rows = []
    for gene_idx, gene in enumerate(genes):
        part = groups.copy()
        part["gene"] = gene
        part["raw_count_sum"] = dense_counts[:, gene_idx]
        part["cp10k"] = cp10k[:, gene_idx]
        part["log1p_cp10k"] = log_cp10k[:, gene_idx]
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def signature_catalog(present: set[str]) -> pd.DataFrame:
    rows = []
    for signature, info in SIGNATURES.items():
        positive = [g for g in info["positive"] if g in present]
        negative = [g for g in info["negative"] if g in present]
        reference_keys, reference_dois = SIGNATURE_REFERENCES[signature]
        if signature == "Platelet_ambient_QC":
            source_type = "Internal technical-QC marker panel"
            provenance_note = "Marker-based contamination control; not a published biological signature."
        elif signature in CONTROL_SIGNATURES:
            source_type = "Manually curated biological control panel"
            provenance_note = "Marker panel assembled from cited compartment biology; not a verbatim published signature."
        else:
            source_type = "Manually curated literature-informed panel"
            provenance_note = "Genes selected from cited biological framing; not a verbatim published signature."
        rows.append(
            {
                "signature": signature,
                "anchor": info["anchor"],
                "expected_focus": info["expected_focus"],
                "source_type": source_type,
                "source_reference_keys": reference_keys,
                "source_dois": reference_dois,
                "provenance_note": provenance_note,
                "positive_genes": ";".join(info["positive"]),
                "negative_genes": ";".join(info["negative"]),
                "positive_present": ";".join(positive),
                "negative_present": ";".join(negative),
                "n_positive_present": len(positive),
                "n_negative_present": len(negative),
            }
        )
    return pd.DataFrame(rows)


def signature_scores(gene_long: pd.DataFrame) -> pd.DataFrame:
    base_cols = [c for c in ["donor_id", "disease", "disease_state", "refined_state", "n_cells", "total_raw_counts"] if c in gene_long.columns]
    rows = []
    for signature, info in SIGNATURES.items():
        pos = [g for g in info["positive"] if g in set(gene_long["gene"])]
        neg = [g for g in info["negative"] if g in set(gene_long["gene"])]
        if not pos:
            continue
        pos_scores = (
            gene_long[gene_long["gene"].isin(pos)]
            .groupby(base_cols, observed=True)["log1p_cp10k"]
            .mean()
            .rename("positive_score")
            .reset_index()
        )
        if neg:
            neg_scores = (
                gene_long[gene_long["gene"].isin(neg)]
                .groupby(base_cols, observed=True)["log1p_cp10k"]
                .mean()
                .rename("negative_score")
                .reset_index()
            )
            merged = pos_scores.merge(neg_scores, on=base_cols, how="left")
            merged["signature_score"] = merged["positive_score"] - merged["negative_score"]
        else:
            merged = pos_scores
            merged["negative_score"] = np.nan
            merged["signature_score"] = merged["positive_score"]
        merged["signature"] = signature
        merged["anchor"] = info["anchor"]
        merged["expected_focus"] = info["expected_focus"]
        merged["n_positive_genes"] = len(pos)
        merged["n_negative_genes"] = len(neg)
        rows.append(merged)
    return pd.concat(rows, ignore_index=True)


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


def compare_focus_vs_others(scores: pd.DataFrame, min_cells: int) -> pd.DataFrame:
    sub = scores[(scores["n_cells"] >= min_cells) & (scores["refined_state"] != FLAGGED_STATE)].copy()
    rows = []
    for signature, part in sub.groupby("signature", observed=True):
        focus = (
            part.loc[part["refined_state"] == FOCUS_STATE]
            .groupby("donor_id", observed=True)["signature_score"]
            .mean()
            .rename("focus")
        )
        other = (
            part.loc[part["refined_state"] != FOCUS_STATE]
            .groupby("donor_id", observed=True)["signature_score"]
            .mean()
            .rename("other")
        )
        paired = pd.concat([focus, other], axis=1, join="inner").dropna()
        differences = paired["focus"] - paired["other"]
        if paired.empty:
            stat, pvalue = np.nan, np.nan
        elif np.allclose(differences.to_numpy(float), 0.0):
            stat, pvalue = 0.0, 1.0
        else:
            stat, pvalue = stats.wilcoxon(paired["focus"], paired["other"], alternative="two-sided")
        rows.append(
            {
                "signature": signature,
                "n_paired_donors": int(len(paired)),
                "mean_focus": float(paired["focus"].mean()) if len(paired) else np.nan,
                "mean_other": float(paired["other"].mean()) if len(paired) else np.nan,
                "median_focus": float(paired["focus"].median()) if len(paired) else np.nan,
                "median_other": float(paired["other"].median()) if len(paired) else np.nan,
                "delta_focus_minus_other": float(differences.mean()) if len(paired) else np.nan,
                "median_paired_difference": float(differences.median()) if len(paired) else np.nan,
                "wilcoxon_statistic": float(stat) if not pd.isna(stat) else np.nan,
                "pvalue": pvalue,
            }
        )
    out = pd.DataFrame(rows)
    out["fdr_bh"] = benjamini_hochberg(out["pvalue"])
    return out.sort_values("delta_focus_minus_other", ascending=False)


def state_signature_summary(scores: pd.DataFrame, min_cells: int) -> pd.DataFrame:
    sub = scores[scores["n_cells"] >= min_cells].copy()
    out = (
        sub.groupby(["refined_state", "signature"], observed=True)
        .agg(
            n_donor_states=("donor_id", "nunique"),
            mean_signature_score=("signature_score", "mean"),
            median_signature_score=("signature_score", "median"),
            mean_positive_score=("positive_score", "mean"),
            mean_negative_score=("negative_score", "mean"),
            mean_n_cells=("n_cells", "mean"),
        )
        .reset_index()
    )
    return out


def specificity_rank(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for signature, part in summary.groupby("signature", observed=True):
        ranked = part.sort_values("mean_signature_score", ascending=False).reset_index(drop=True)
        ranked["rank_desc"] = np.arange(1, len(ranked) + 1)
        focus = ranked[ranked["refined_state"] == FOCUS_STATE]
        if focus.empty:
            continue
        rows.append(
            {
                "signature": signature,
                "focus_rank_desc": int(focus.iloc[0]["rank_desc"]),
                "focus_score": float(focus.iloc[0]["mean_signature_score"]),
                "top_state": str(ranked.iloc[0]["refined_state"]),
                "top_score": float(ranked.iloc[0]["mean_signature_score"]),
                "n_states_ranked": int(len(ranked)),
            }
        )
    return pd.DataFrame(rows)


def p_label(value: float) -> str:
    if pd.isna(value):
        return "n.s."
    if value < 1e-4:
        return f"{value:.1e}"
    return f"{value:.3f}"


def add_panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=PANEL_LABEL_SIZE, fontweight="bold", ha="right", va="bottom")


SIGNATURE_DISPLAY = {
    "ABC_DN2_core": "ABC DN2 core",
    "ABC_low_naive_context": "ABC low-naive context",
    "ZEB2_ABC_axis": "ZEB2 ABC axis",
    "APC_HLA_B_cell": "APC/HLA B-cell",
    "EBV_APC_like_B": "EBV APC-like B",
    "IFN_ISG": "IFN/ISG",
    "TLR7_FTO_innate_axis": "TLR7/FTO innate axis",
    "Age_associated_B_like": "Age-associated B-like",
    "Naive_B_control": "Naive B control",
    "Memory_B_control": "Memory B control",
    "Plasmablast_ASC_control": "Plasmablast/ASC control",
    "Platelet_ambient_QC": "Platelet ambient QC",
}

STATE_DISPLAY = {
    "Resting naive B": "Resting naive",
    "Activated SLE-naive-like B": "Activated SLE-naive",
    "Memory-like B I": "Memory-like I",
    "Mixed / transitional B": "Mixed / transitional",
    "TNFRSF13B+ memory-like B": "TNFRSF13B+ memory",
    "Atypical ABC/APC-like B": "ABC/APC-like",
    "Flagged platelet/ambient-high B": "Flagged QC state",
    "Plasmablast / ASC": "Plasmablast / ASC",
}


def plot_heatmap(ax, summary: pd.DataFrame) -> None:
    signature_order = PATHOGENIC_SIGNATURES + CONTROL_SIGNATURES
    mat = summary.pivot(index="signature", columns="refined_state", values="mean_signature_score").reindex(index=signature_order, columns=STATE_ORDER)
    z = mat.sub(mat.mean(axis=1), axis=0).div(mat.std(axis=1).replace(0, np.nan), axis=0)
    z = z.rename(index=SIGNATURE_DISPLAY, columns=STATE_DISPLAY)
    sns.heatmap(
        z,
        ax=ax,
        cmap="vlag",
        center=0,
        vmin=-2.2,
        vmax=2.2,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Row z-score", "shrink": 0.72},
    )
    ax.set_title("Literature-informed signatures across B-cell states")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=32, labelsize=4.8)
    ax.tick_params(axis="y", labelsize=4.8)


def paired_signature_values(scores: pd.DataFrame, signatures: list[str], min_cells: int) -> pd.DataFrame:
    sub = scores[
        (scores["n_cells"] >= min_cells)
        & (scores["refined_state"] != FLAGGED_STATE)
        & (scores["signature"].isin(signatures))
    ].copy()
    focus = (
        sub[sub["refined_state"] == FOCUS_STATE]
        .groupby(["donor_id", "signature"], observed=True)["signature_score"]
        .mean()
        .rename("ABC/APC-like")
    )
    other = (
        sub[sub["refined_state"] != FOCUS_STATE]
        .groupby(["donor_id", "signature"], observed=True)["signature_score"]
        .mean()
        .rename("Other retained states")
    )
    paired = pd.concat([focus, other], axis=1, join="inner").dropna().reset_index()
    return paired.melt(
        id_vars=["donor_id", "signature"],
        value_vars=["ABC/APC-like", "Other retained states"],
        var_name="comparison_group",
        value_name="signature_score",
    )


def plot_pathogenic_boxplots(ax, scores: pd.DataFrame, min_cells: int) -> None:
    sub = paired_signature_values(scores, PATHOGENIC_SIGNATURES, min_cells)
    order = PATHOGENIC_SIGNATURES
    palette = {"Other retained states": "#AEB7C2", "ABC/APC-like": "#B23A48"}
    sns.boxplot(data=sub, x="signature", y="signature_score", hue="comparison_group", order=order, palette=palette, fliersize=0, linewidth=0.8, ax=ax)
    ax.set_title("Pathogenic signatures in paired donors")
    ax.set_xlabel("")
    ax.set_ylabel("Signature score")
    ax.tick_params(axis="x", rotation=35, labelsize=5.5)
    ax.legend(frameon=False, fontsize=5.5, title="")


def plot_effects(ax, tests: pd.DataFrame) -> None:
    sub = tests[tests["signature"].isin(PATHOGENIC_SIGNATURES)].sort_values("delta_focus_minus_other", ascending=True)
    sub["display_signature"] = sub["signature"].map(SIGNATURE_DISPLAY)
    colors = ["#B23A48" if x > 0 else "#AEB7C2" for x in sub["delta_focus_minus_other"]]
    ax.barh(sub["display_signature"], sub["delta_focus_minus_other"], color=colors, height=0.68)
    xmax = max(0.15, float(sub["delta_focus_minus_other"].max()) + 0.18)
    xmin = min(-0.05, float(sub["delta_focus_minus_other"].min()) - 0.05)
    ax.set_xlim(xmin, xmax)
    for y, row in enumerate(sub.itertuples(index=False)):
        x = row.delta_focus_minus_other + 0.015 if row.delta_focus_minus_other >= 0 else 0.015
        ax.text(x, y, f"FDR {p_label(row.fdr_bh)}", va="center", fontsize=4.8)
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.set_xlabel("Paired donor difference\nABC/APC-like minus other states")
    ax.set_ylabel("")
    ax.set_title("ABC/APC-like signature enrichment in paired donors")
    ax.tick_params(axis="y", labelsize=5.0)


def plot_control_boxplots(ax, scores: pd.DataFrame, min_cells: int) -> None:
    sub = paired_signature_values(scores, CONTROL_SIGNATURES, min_cells)
    palette = {"Other retained states": "#AEB7C2", "ABC/APC-like": "#B23A48"}
    sns.boxplot(data=sub, x="signature", y="signature_score", hue="comparison_group", order=CONTROL_SIGNATURES, palette=palette, fliersize=0, linewidth=0.8, ax=ax)
    ax.set_title("Control signatures")
    ax.set_xlabel("")
    ax.set_ylabel("Signature score")
    ax.tick_params(axis="x", rotation=30, labelsize=5.5)
    ax.legend(frameon=False, fontsize=5.5, title="")


def plot_specificity(ax, ranks: pd.DataFrame) -> None:
    sub = ranks[ranks["signature"].isin(PATHOGENIC_SIGNATURES + CONTROL_SIGNATURES)].copy()
    sub["category"] = np.where(sub["signature"].isin(PATHOGENIC_SIGNATURES), "Pathogenic", "Control")
    sub = sub.sort_values(["category", "focus_rank_desc", "signature"], ascending=[False, True, True])
    colors = sub["category"].map({"Pathogenic": "#B23A48", "Control": "#6A4C93"})
    y = np.arange(len(sub))
    ax.hlines(y, 1, sub["focus_rank_desc"], color="0.82", linewidth=0.8)
    ax.scatter(sub["focus_rank_desc"], y, s=18, color=colors, zorder=3)
    ax.set_xlim(0.5, max(8.5, sub["focus_rank_desc"].max() + 1))
    ax.set_yticks(y)
    ax.set_yticklabels(sub["signature"].map(SIGNATURE_DISPLAY), fontsize=4.8)
    ax.invert_yaxis()
    ax.set_xlabel("ABC/APC-like rank among states\n1 = highest")
    ax.set_title("Signature specificity rank")


def plot_control_effects(ax, tests: pd.DataFrame) -> None:
    sub = tests[tests["signature"].isin(CONTROL_SIGNATURES)].sort_values("delta_focus_minus_other", ascending=True).copy()
    sub["display_signature"] = sub["signature"].map(SIGNATURE_DISPLAY)
    colors = ["#6A4C93" if x > 0 else "#8CA0B3" for x in sub["delta_focus_minus_other"]]
    ax.barh(sub["display_signature"], sub["delta_focus_minus_other"], color=colors, height=0.62)
    ax.axvline(0, color="0.25", linewidth=0.7)
    limit = max(0.1, float(sub["delta_focus_minus_other"].abs().max()) * 1.35)
    ax.set_xlim(-limit, limit)
    for y, row in enumerate(sub.itertuples(index=False)):
        ax.text(
            limit * 0.96,
            y,
            f"FDR {p_label(row.fdr_bh)}",
            va="center",
            ha="right",
            fontsize=4.7,
        )
    ax.set_xlabel("Paired donor difference")
    ax.set_ylabel("")
    ax.set_title("Control signature effects")
    ax.tick_params(axis="y", labelsize=4.8)


def make_figure(out_png: Path, scores: pd.DataFrame, summary: pd.DataFrame, tests: pd.DataFrame, ranks: pd.DataFrame, min_cells: int) -> None:
    sns.set_theme(style="white", context="paper")
    apply_nature_style()
    fig = plt.figure(figsize=nature_figsize(6.8, 6.35), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.30, 1.0, 0.90], width_ratios=[0.92, 1.08])
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, :])
    ax_c = fig.add_subplot(gs[2, 0])
    ax_d = fig.add_subplot(gs[2, 1])
    plot_heatmap(ax_a, summary)
    plot_effects(ax_b, tests)
    plot_control_effects(ax_c, tests)
    plot_specificity(ax_d, ranks)
    for ax, label in zip([ax_a, ax_b, ax_c, ax_d], list("abcd")):
        add_panel_label(ax, label)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    save_nature_figure(fig, out_png)
    plt.close(fig)


def write_summary(path: Path, catalog: pd.DataFrame, tests: pd.DataFrame, ranks: pd.DataFrame) -> None:
    key = tests[tests["signature"].isin(PATHOGENIC_SIGNATURES)].sort_values("delta_focus_minus_other", ascending=False)
    rank_map = ranks.set_index("signature")["focus_rank_desc"].to_dict()
    lines = [
        "# Literature-Informed Signature Validation Summary",
        "",
        f"- Signatures evaluated: {catalog['signature'].nunique()}.",
        f"- Signature gene slots present: {int(catalog['n_positive_present'].sum() + catalog['n_negative_present'].sum())}.",
        "",
        "## Pathogenic Signature Effects In ABC/APC-Like State",
        "",
    ]
    for row in key.itertuples(index=False):
        lines.append(
            f"- {row.signature}: delta {row.delta_focus_minus_other:.3f}; "
            f"focus mean {row.mean_focus:.3f}; other mean {row.mean_other:.3f}; "
            f"FDR {row.fdr_bh:.2e}; focus rank {rank_map.get(row.signature, 'NA')}."
        )
    lines.extend(["", "## Interpretation", ""])
    lines.append(
        "The ABC/APC-like state is specifically enriched for ABC/DN2, ZEB2-linked ABC, APC/HLA, EBV/APC-like, IFN, and age-associated/atypical B-cell signatures. The TLR7/FTO innate-axis signature is not focus-state specific in this analysis and should be treated as a broader mechanistic context rather than a central state-defining result. Control signatures help distinguish the focus state from naive, memory, plasmablast, and platelet/ambient profiles."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate refined B-cell states against literature-informed marker signatures.")
    parser.add_argument("--input", required=True, help="B-cell subset h5ad containing .raw.X")
    parser.add_argument("--labels", required=True, help="CSV with obs index and draft state labels")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--gene-symbol-column", default="feature_name")
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument("--min-cells", type=int, default=10)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    tabledir = outdir / "tables"
    figdir = outdir / "figures"
    tabledir.mkdir(parents=True, exist_ok=True)
    figdir.mkdir(parents=True, exist_ok=True)

    all_genes = unique_preserving_order(
        [gene for info in SIGNATURES.values() for gene in list(info["positive"]) + list(info["negative"])]
    )
    labels = pd.read_csv(args.labels, index_col=0, low_memory=False)
    labels["refined_state"] = labels["draft_state"].map(REFINED_STATE_MAP)

    source = ad.read_h5ad(args.input, backed="r")
    if source.raw is None:
        raise SystemExit("Input AnnData has no .raw matrix.")
    labels = labels.reindex(source.obs_names)
    if labels["refined_state"].isna().any():
        raise SystemExit("Some cells are missing refined_state labels after reindexing.")

    present, indices, missing = build_gene_index(source.raw.var, args.gene_symbol_column, all_genes)
    print(f"Using {len(present)} signature genes; missing {len(missing)}")
    counts = to_csr(source.raw.X[:, indices])
    total_counts = row_sums_backed(source.raw.X, source.n_obs, args.chunk_size)
    try:
        source.file.close()
    except Exception:
        pass

    metadata = labels[["donor_id", "disease", "disease_state", "refined_state"]].copy()
    groups, grouped_counts, grouped_totals = aggregate_by_group(
        counts, total_counts, metadata, ["donor_id", "disease", "disease_state", "refined_state"]
    )
    gene_long = long_gene_table(groups, grouped_counts, grouped_totals, present)
    catalog = signature_catalog(set(present))
    scores = signature_scores(gene_long)
    tests = compare_focus_vs_others(scores, args.min_cells)
    summary = state_signature_summary(scores, args.min_cells)
    ranks = specificity_rank(summary)

    pd.DataFrame({"gene": present}).to_csv(tabledir / "signature_genes_present.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"gene": missing}).to_csv(tabledir / "signature_genes_missing.csv", index=False, encoding="utf-8-sig")
    catalog.to_csv(tabledir / "literature_informed_signature_catalog.csv", index=False, encoding="utf-8-sig")
    scores.to_csv(tabledir / "donor_state_literature_signature_scores_long.csv", index=False, encoding="utf-8-sig")
    tests.to_csv(tabledir / "abc_apc_vs_other_literature_signature_tests.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(tabledir / "state_literature_signature_summary.csv", index=False, encoding="utf-8-sig")
    ranks.to_csv(tabledir / "abc_apc_signature_specificity_ranks.csv", index=False, encoding="utf-8-sig")
    write_summary(outdir / "literature_signature_validation_summary.md", catalog, tests, ranks)
    make_figure(figdir / "figure5_v1_literature_signature_validation.png", scores, summary, tests, ranks, args.min_cells)

    print(f"Wrote literature-informed signature validation outputs to: {outdir}")
    print(tests[tests["signature"].isin(PATHOGENIC_SIGNATURES)].to_string(index=False))


if __name__ == "__main__":
    main()
