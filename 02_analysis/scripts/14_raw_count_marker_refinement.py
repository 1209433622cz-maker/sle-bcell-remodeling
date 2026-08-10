from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse


MARKER_PROGRAMS: "OrderedDict[str, list[str]]" = OrderedDict(
    [
        ("Pan_B", ["MS4A1", "CD79A", "CD79B", "CD74", "HLA-DRA"]),
        ("Naive_B", ["TCL1A", "IGHD", "IGHM", "IL4R", "FCER2", "CCR7", "SELL", "CD24"]),
        ("Memory_B", ["CD27", "TNFRSF13B", "AIM2", "BANK1", "CD40", "LTB"]),
        ("ABC_DN2", ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7", "ZEB2"]),
        ("Low_naive_context", ["CR2", "FCER2", "IGHD", "TCL1A"]),
        ("Plasmablast", ["MZB1", "XBP1", "PRDM1", "JCHAIN", "SDC1", "IRF4", "TNFRSF17", "DERL3"]),
        ("Antigen_presentation", ["HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "CD74", "CIITA", "CD86"]),
        ("IFN_response", ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6"]),
        ("Activation", ["CD69", "CD83", "CD86", "NFKBIA", "JUNB", "FOS", "FOSB", "DUSP1"]),
        ("TLR7_innate", ["TLR7", "MYD88", "IRF7", "NFKB1", "RELA", "DDX58", "IFIH1"]),
        ("Proliferation", ["MKI67", "TOP2A", "STMN1", "TYMS"]),
        ("Platelet_ambient", ["PPBP", "PF4", "NRGN", "TUBB1", "RGS18", "CAVIN2", "GNG11", "SPARC", "MYL9", "CLU"]),
    ]
)


PLOT_GENES = [
    "MS4A1",
    "CD79A",
    "CD74",
    "TCL1A",
    "IGHD",
    "IGHM",
    "FCER2",
    "IL4R",
    "CD27",
    "TNFRSF13B",
    "AIM2",
    "BANK1",
    "TBX21",
    "ITGAX",
    "FCRL5",
    "FCRL3",
    "ZEB2",
    "CXCR3",
    "TLR7",
    "CR2",
    "HLA-DRA",
    "HLA-DPB1",
    "CD86",
    "ISG15",
    "IFIT1",
    "MX1",
    "MZB1",
    "XBP1",
    "PRDM1",
    "JCHAIN",
    "SDC1",
    "IRF4",
    "TNFRSF17",
    "PPBP",
    "PF4",
    "NRGN",
    "TUBB1",
    "RGS18",
    "CAVIN2",
    "GNG11",
    "SPARC",
]


def unique_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def build_gene_index(raw_var: pd.DataFrame, gene_symbol_column: str, genes: list[str]) -> tuple[list[str], list[int], list[str]]:
    if gene_symbol_column not in raw_var.columns:
        raise ValueError(f"raw.var does not contain gene symbol column: {gene_symbol_column}")
    symbols = raw_var[gene_symbol_column].astype(str)
    symbol_to_indices: dict[str, list[int]] = {}
    for idx, symbol in enumerate(symbols):
        symbol_to_indices.setdefault(symbol, []).append(idx)

    present: list[str] = []
    indices: list[int] = []
    missing: list[str] = []
    for gene in genes:
        hits = symbol_to_indices.get(gene, [])
        if hits:
            present.append(gene)
            indices.append(hits[0])
        else:
            missing.append(gene)
    return present, indices, missing


def to_csr(x) -> sparse.csr_matrix:
    if sparse.issparse(x):
        return x.tocsr()
    return sparse.csr_matrix(np.asarray(x))


def row_sums_backed(x, n_obs: int, chunk_size: int) -> np.ndarray:
    sums = np.zeros(n_obs, dtype=float)
    for start in range(0, n_obs, chunk_size):
        end = min(n_obs, start + chunk_size)
        chunk = to_csr(x[start:end, :])
        sums[start:end] = np.asarray(chunk.sum(axis=1)).ravel()
        print(f"Computed raw total counts for cells {start:,}-{end:,} / {n_obs:,}")
    return sums


def group_summary(
    counts: sparse.csr_matrix,
    log_norm: sparse.csr_matrix,
    groups: pd.Series,
    genes: list[str],
    group_col: str,
) -> pd.DataFrame:
    rows = []
    groups = groups.astype(str)
    order = list(pd.unique(groups))
    for group in order:
        mask = groups.to_numpy() == group
        n_cells = int(mask.sum())
        c_sub = counts[mask, :]
        l_sub = log_norm[mask, :]
        pct = np.asarray((c_sub > 0).mean(axis=0)).ravel()
        mean_log = np.asarray(l_sub.mean(axis=0)).ravel()
        mean_counts = np.asarray(c_sub.mean(axis=0)).ravel()
        for gene, p, ml, mc in zip(genes, pct, mean_log, mean_counts, strict=True):
            rows.append(
                {
                    group_col: group,
                    "gene": gene,
                    "n_cells": n_cells,
                    "pct_expressing": float(p),
                    "mean_log1p_cp10k": float(ml),
                    "mean_raw_counts": float(mc),
                }
            )
    return pd.DataFrame(rows)


def program_summary(marker_summary: pd.DataFrame, group_col: str, gene_to_programs: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for (group, program), sub in marker_summary.assign(
        program=marker_summary["gene"].map(lambda g: "|".join(gene_to_programs.get(g, [])))
    ).groupby([group_col, "program"], dropna=False):
        if not program:
            continue
        programs = str(program).split("|")
        for p in programs:
            p_sub = sub[sub["gene"].map(lambda g: p in gene_to_programs.get(g, []))]
            rows.append(
                {
                    group_col: group,
                    "program": p,
                    "n_genes": int(p_sub["gene"].nunique()),
                    "mean_log1p_cp10k": float(p_sub["mean_log1p_cp10k"].mean()),
                    "mean_pct_expressing": float(p_sub["pct_expressing"].mean()),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.drop_duplicates([group_col, "program"]).sort_values([group_col, "mean_log1p_cp10k"], ascending=[True, False])


def make_dotplot(marker_summary: pd.DataFrame, group_col: str, plot_genes: list[str], output: Path, title: str) -> None:
    sub = marker_summary[marker_summary["gene"].isin(plot_genes)].copy()
    sub["gene"] = pd.Categorical(sub["gene"], categories=[g for g in plot_genes if g in set(sub["gene"])], ordered=True)
    groups = list(pd.unique(sub[group_col]))
    sub[group_col] = pd.Categorical(sub[group_col], categories=groups, ordered=True)
    sub = sub.sort_values([group_col, "gene"])

    x = sub["gene"].cat.codes.to_numpy()
    y = sub[group_col].cat.codes.to_numpy()
    size = 20 + 380 * sub["pct_expressing"].to_numpy()
    color = sub["mean_log1p_cp10k"].to_numpy()

    fig_w = max(10, 0.36 * len(sub["gene"].cat.categories) + 4)
    fig_h = max(4.8, 0.48 * len(groups) + 1.8)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    scatter = ax.scatter(x, y, s=size, c=color, cmap="viridis", edgecolors="0.3", linewidths=0.25)
    ax.set_xticks(range(len(sub["gene"].cat.categories)))
    ax.set_xticklabels(list(sub["gene"].cat.categories), rotation=60, ha="right")
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels(groups)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cbar = fig.colorbar(scatter, ax=ax, pad=0.01)
    cbar.set_label("Mean log1p(CP10K)")

    for pct, label in [(0.1, "10%"), (0.4, "40%"), (0.8, "80%")]:
        ax.scatter([], [], s=20 + 380 * pct, c="lightgray", edgecolors="0.3", linewidths=0.25, label=label)
    ax.legend(title="Expressing", loc="upper left", bbox_to_anchor=(1.14, 1.0), frameon=False)
    ax.grid(axis="both", color="0.92", linewidth=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    plt.close(fig)


def write_markdown_report(
    output: Path,
    present: list[str],
    missing: list[str],
    state_program: pd.DataFrame,
    marker_summary: pd.DataFrame,
    state_col: str,
) -> None:
    lines = [
        "# Raw-Count Marker Refinement Summary",
        "",
        "This report uses `adata.raw.X`, which was inspected as a non-negative integer count matrix.",
        "Values were normalized to CP10K and transformed with log1p before state-level summaries.",
        "",
        f"- Marker genes requested: {len(present) + len(missing)}",
        f"- Marker genes present: {len(present)}",
        f"- Marker genes missing: {len(missing)}",
    ]
    if missing:
        lines.append(f"- Missing genes: {', '.join(missing)}")
    lines.extend(["", "## Top Programs By State", ""])
    for state in pd.unique(state_program[state_col]):
        sub = state_program[state_program[state_col] == state].sort_values("mean_log1p_cp10k", ascending=False).head(5)
        lines.append(f"### {state}")
        for row in sub.itertuples(index=False):
            lines.append(
                f"- {row.program}: mean log1p(CP10K) {row.mean_log1p_cp10k:.3f}; "
                f"mean expressing fraction {row.mean_pct_expressing:.3f}; genes {row.n_genes}"
            )
        marker_sub = marker_summary[marker_summary[state_col] == state].sort_values("mean_log1p_cp10k", ascending=False).head(10)
        genes = ", ".join(
            f"{r.gene} ({r.mean_log1p_cp10k:.2f}, {100*r.pct_expressing:.0f}%)"
            for r in marker_sub.itertuples(index=False)
        )
        lines.append(f"- Top marker genes in panel: {genes}")
        lines.append("")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize curated B-cell marker expression from raw counts.")
    parser.add_argument("--input", required=True, help="B-cell subset h5ad containing raw counts in .raw.X")
    parser.add_argument("--labels", required=True, help="CSV with obs index and Leiden/state labels")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--gene-symbol-column", default="feature_name")
    parser.add_argument("--state-column", default="draft_state")
    parser.add_argument("--cluster-column", default="leiden")
    parser.add_argument("--chunk-size", type=int, default=5000)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    figdir = outdir / "figures"
    tabledir = outdir / "tables"
    figdir.mkdir(parents=True, exist_ok=True)
    tabledir.mkdir(parents=True, exist_ok=True)

    all_markers = unique_preserving_order([gene for genes in MARKER_PROGRAMS.values() for gene in genes])
    gene_to_programs: dict[str, list[str]] = {}
    for program, genes in MARKER_PROGRAMS.items():
        for gene in genes:
            gene_to_programs.setdefault(gene, []).append(program)

    labels = pd.read_csv(args.labels, index_col=0, low_memory=False)
    adata = ad.read_h5ad(args.input, backed="r")
    if adata.raw is None:
        raise SystemExit("Input AnnData has no .raw matrix.")
    labels = labels.reindex(adata.obs_names)
    if labels[args.state_column].isna().any():
        n_missing = int(labels[args.state_column].isna().sum())
        raise SystemExit(f"Labels do not align to AnnData obs_names; missing {n_missing} state labels.")

    present, indices, missing = build_gene_index(adata.raw.var, args.gene_symbol_column, all_markers)
    if not present:
        raise SystemExit("None of the requested marker genes were found.")

    print(f"Using {len(present)} marker genes; missing {len(missing)}")
    counts = to_csr(adata.raw.X[:, indices])
    total_counts = row_sums_backed(adata.raw.X, adata.n_obs, args.chunk_size)
    total_counts[total_counts <= 0] = np.nan
    scale = 10000.0 / total_counts
    norm = counts.multiply(scale[:, None]).tocsr()
    norm.data = np.log1p(norm.data)

    state_summary = group_summary(counts, norm, labels[args.state_column], present, args.state_column)
    cluster_summary = group_summary(counts, norm, labels[args.cluster_column], present, args.cluster_column)
    state_summary["programs"] = state_summary["gene"].map(lambda g: ";".join(gene_to_programs.get(g, [])))
    cluster_summary["programs"] = cluster_summary["gene"].map(lambda g: ";".join(gene_to_programs.get(g, [])))

    state_program = program_summary(state_summary, args.state_column, gene_to_programs)
    cluster_program = program_summary(cluster_summary, args.cluster_column, gene_to_programs)

    state_summary.to_csv(tabledir / "raw_count_marker_summary_by_state.csv", index=False, encoding="utf-8-sig")
    cluster_summary.to_csv(tabledir / "raw_count_marker_summary_by_cluster.csv", index=False, encoding="utf-8-sig")
    state_program.to_csv(tabledir / "raw_count_program_summary_by_state.csv", index=False, encoding="utf-8-sig")
    cluster_program.to_csv(tabledir / "raw_count_program_summary_by_cluster.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"gene": present}).to_csv(tabledir / "raw_count_marker_genes_present.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"gene": missing}).to_csv(tabledir / "raw_count_marker_genes_missing.csv", index=False, encoding="utf-8-sig")

    plot_genes = [gene for gene in PLOT_GENES if gene in present]
    make_dotplot(
        state_summary,
        args.state_column,
        plot_genes,
        figdir / "raw_count_state_marker_dotplot.png",
        "Raw-count marker support by B-cell state",
    )
    make_dotplot(
        cluster_summary,
        args.cluster_column,
        plot_genes,
        figdir / "raw_count_cluster_marker_dotplot.png",
        "Raw-count marker support by Leiden cluster",
    )
    write_markdown_report(
        outdir / "raw_count_marker_refinement_summary.md",
        present,
        missing,
        state_program,
        state_summary,
        args.state_column,
    )
    try:
        adata.file.close()
    except Exception:
        pass
    print(f"Wrote marker refinement outputs to: {outdir}")


if __name__ == "__main__":
    main()
