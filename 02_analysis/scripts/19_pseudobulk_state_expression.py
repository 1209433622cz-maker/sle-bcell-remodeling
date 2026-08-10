from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


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


MARKER_PROGRAMS: "OrderedDict[str, list[str]]" = OrderedDict(
    [
        ("ABC_ranked", ["FCRL5", "HSPB1", "RGS2", "EMP3", "CIB1", "FCRL3", "FGR", "MAP3K8", "ZEB2", "TNFRSF1B", "HCK", "ZBTB32"]),
        ("ABC_DN2", ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"]),
        ("APC_HLA", ["CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "HLA-DQA1", "HLA-DQB1", "B2M", "CIITA", "CD86"]),
        ("Activation", ["CD69", "CD83", "NFKBIA", "JUNB", "FOS", "FOSB", "DUSP1", "NR4A2"]),
        ("IFN_response", ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6", "LY6E"]),
        ("Naive_B", ["TCL1A", "IL4R", "FCER2", "CCR7", "SELL", "CXCR4", "VPREB3"]),
        ("Memory_B", ["CD27", "TNFRSF13B", "AIM2", "BANK1", "CD40", "LTB", "GPR183"]),
        ("Plasmablast", ["MZB1", "XBP1", "PRDM1", "JCHAIN", "SDC1", "IRF4", "TNFRSF17", "DERL3", "FKBP11", "HSP90B1"]),
        ("Platelet_ambient", ["PPBP", "PF4", "NRGN", "TUBB1", "RGS18", "CAVIN2", "GNG11", "SPARC", "MYL9", "CLU"]),
        ("Pan_B", ["MS4A1", "CD79A", "CD79B", "CD74", "CD19"]),
    ]
)


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


def aggregate_by_group(counts: sparse.csr_matrix, total_counts: np.ndarray, metadata: pd.DataFrame) -> tuple[pd.DataFrame, sparse.csr_matrix, np.ndarray]:
    group_cols = ["donor_id", "disease", "disease_state", "refined_state"]
    group_frame = metadata[group_cols].astype(str)
    group_key = group_frame.agg("||".join, axis=1)
    codes, uniques = pd.factorize(group_key, sort=False)
    n_groups = len(uniques)
    indicator = sparse.csr_matrix(
        (np.ones(len(codes), dtype=np.float32), (codes, np.arange(len(codes)))),
        shape=(n_groups, len(codes)),
    )
    aggregated_counts = indicator @ counts
    aggregated_totals = np.bincount(codes, weights=total_counts, minlength=n_groups).astype(float)
    n_cells = np.bincount(codes, minlength=n_groups).astype(int)
    groups = pd.Series(uniques, name="group_key").str.split(r"\|\|", expand=True)
    groups.columns = group_cols
    groups["n_cells"] = n_cells
    groups["total_raw_counts"] = aggregated_totals
    return groups, aggregated_counts.tocsr(), aggregated_totals


def long_gene_table(groups: pd.DataFrame, counts: sparse.csr_matrix, totals: np.ndarray, genes: list[str]) -> pd.DataFrame:
    rows = []
    dense_counts = counts.toarray().astype(float)
    safe_totals = totals.copy()
    safe_totals[safe_totals <= 0] = np.nan
    cp10k = dense_counts / safe_totals[:, None] * 10000.0
    log_cp10k = np.log1p(cp10k)
    for gene_idx, gene in enumerate(genes):
        part = groups.copy()
        part["gene"] = gene
        part["raw_count_sum"] = dense_counts[:, gene_idx]
        part["cp10k"] = cp10k[:, gene_idx]
        part["log1p_cp10k"] = log_cp10k[:, gene_idx]
        rows.append(part)
    out = pd.concat(rows, ignore_index=True)
    return out


def program_table(gene_long: pd.DataFrame, gene_to_programs: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    group_cols = ["donor_id", "disease", "disease_state", "refined_state", "n_cells", "total_raw_counts"]
    for program, genes in MARKER_PROGRAMS.items():
        present = [g for g in genes if g in set(gene_long["gene"])]
        if not present:
            continue
        sub = gene_long[gene_long["gene"].isin(present)]
        agg = (
            sub.groupby(group_cols, observed=True)
            .agg(
                mean_log1p_cp10k=("log1p_cp10k", "mean"),
                mean_cp10k=("cp10k", "mean"),
                n_genes=("gene", "nunique"),
            )
            .reset_index()
        )
        agg["program"] = program
        rows.append(agg)
    return pd.concat(rows, ignore_index=True)


def compare_focus_vs_others(gene_long: pd.DataFrame, program_long: pd.DataFrame, min_cells: int, exclude_flagged: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    def prep(df: pd.DataFrame, value_col: str, feature_col: str) -> pd.DataFrame:
        x = df[df["n_cells"] >= min_cells].copy()
        if exclude_flagged:
            x = x[x["refined_state"] != FLAGGED_STATE].copy()
        x["comparison_group"] = np.where(x["refined_state"] == FOCUS_STATE, FOCUS_STATE, "Other retained states")
        return x

    gene_df = prep(gene_long, "log1p_cp10k", "gene")
    program_df = prep(program_long, "mean_log1p_cp10k", "program")

    gene_tests = feature_tests(gene_df, "gene", "log1p_cp10k")
    program_tests = feature_tests(program_df, "program", "mean_log1p_cp10k")
    return gene_tests, program_tests


def feature_tests(df: pd.DataFrame, feature_col: str, value_col: str) -> pd.DataFrame:
    rows = []
    for feature, sub in df.groupby(feature_col, observed=True):
        focus = (
            sub.loc[sub["comparison_group"] == FOCUS_STATE]
            .groupby("donor_id", observed=True)[value_col]
            .mean()
            .rename("focus")
        )
        other = (
            sub.loc[sub["comparison_group"] == "Other retained states"]
            .groupby("donor_id", observed=True)[value_col]
            .mean()
            .rename("other")
        )
        paired = pd.concat([focus, other], axis=1, join="inner").dropna()
        differences = paired["focus"] - paired["other"]
        if paired.empty:
            pvalue = np.nan
            stat = np.nan
        elif np.allclose(differences.to_numpy(float), 0.0):
            pvalue = 1.0
            stat = 0.0
        else:
            test = wilcoxon(paired["focus"], paired["other"], alternative="two-sided")
            stat = float(test.statistic)
            pvalue = float(test.pvalue)
        rows.append(
            {
                feature_col: feature,
                "n_paired_donors": int(len(paired)),
                "mean_focus": float(paired["focus"].mean()) if len(paired) else np.nan,
                "mean_other": float(paired["other"].mean()) if len(paired) else np.nan,
                "median_focus": float(paired["focus"].median()) if len(paired) else np.nan,
                "median_other": float(paired["other"].median()) if len(paired) else np.nan,
                "delta_focus_minus_other": float(differences.mean()) if len(paired) else np.nan,
                "median_paired_difference": float(differences.median()) if len(paired) else np.nan,
                "wilcoxon_statistic": stat,
                "pvalue": pvalue,
            }
        )
    out = pd.DataFrame(rows)
    mask = out["pvalue"].notna()
    out["fdr_bh"] = np.nan
    if mask.any():
        out.loc[mask, "fdr_bh"] = multipletests(out.loc[mask, "pvalue"], method="fdr_bh")[1]
    return out.sort_values(["fdr_bh", "delta_focus_minus_other"], ascending=[True, False])


def disease_state_summary(program_long: pd.DataFrame, min_cells: int) -> pd.DataFrame:
    sub = program_long[(program_long["refined_state"] == FOCUS_STATE) & (program_long["n_cells"] >= min_cells)].copy()
    out = (
        sub.groupby(["disease_state", "program"], observed=True)
        .agg(
            n_donor_states=("donor_id", "nunique"),
            mean_log1p_cp10k=("mean_log1p_cp10k", "mean"),
            median_log1p_cp10k=("mean_log1p_cp10k", "median"),
            mean_n_cells=("n_cells", "mean"),
        )
        .reset_index()
        .sort_values(["program", "disease_state"])
    )
    return out


def write_summary(path: Path, present: list[str], missing: list[str], program_tests: pd.DataFrame, gene_tests: pd.DataFrame, disease_summary: pd.DataFrame) -> None:
    top_programs = program_tests.sort_values("delta_focus_minus_other", ascending=False).head(10)
    top_genes = gene_tests.sort_values("delta_focus_minus_other", ascending=False).head(20)
    lines = [
        "# Donor-State Pseudobulk Expression Summary",
        "",
        f"Focus state: `{FOCUS_STATE}`",
        "",
        f"- Genes requested: {len(present) + len(missing)}",
        f"- Genes present: {len(present)}",
        f"- Genes missing: {len(missing)}",
    ]
    if missing:
        lines.append(f"- Missing genes: {', '.join(missing)}")
    lines.extend(["", "## Top Programs In Focus State", ""])
    for row in top_programs.itertuples(index=False):
        lines.append(
            f"- {row.program}: delta {row.delta_focus_minus_other:.3f}; "
            f"focus mean {row.mean_focus:.3f}; other mean {row.mean_other:.3f}; FDR {row.fdr_bh:.2e}"
        )
    lines.extend(["", "## Top Genes In Focus State", ""])
    for row in top_genes.itertuples(index=False):
        lines.append(
            f"- {row.gene}: delta {row.delta_focus_minus_other:.3f}; "
            f"focus mean {row.mean_focus:.3f}; other mean {row.mean_other:.3f}; FDR {row.fdr_bh:.2e}"
        )
    lines.extend(["", "## Focus State Disease-State Summary", ""])
    for row in disease_summary.itertuples(index=False):
        if row.program in {"ABC_ranked", "ABC_DN2", "APC_HLA", "Activation", "IFN_response"}:
            lines.append(
                f"- {row.disease_state} / {row.program}: n={row.n_donor_states}; "
                f"mean {row.mean_log1p_cp10k:.3f}; median {row.median_log1p_cp10k:.3f}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create donor-state pseudobulk expression summaries from raw counts.")
    parser.add_argument("--input", required=True, help="B-cell subset h5ad containing .raw.X")
    parser.add_argument("--labels", required=True, help="CSV with obs index and draft state labels")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--gene-symbol-column", default="feature_name")
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument("--min-cells", type=int, default=10)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    tabledir = outdir / "tables"
    tabledir.mkdir(parents=True, exist_ok=True)

    all_markers = unique_preserving_order([gene for genes in MARKER_PROGRAMS.values() for gene in genes])

    labels = pd.read_csv(args.labels, index_col=0, low_memory=False)
    labels["refined_state"] = labels["draft_state"].map(REFINED_STATE_MAP)
    source = ad.read_h5ad(args.input, backed="r")
    if source.raw is None:
        raise SystemExit("Input AnnData has no .raw matrix.")
    labels = labels.reindex(source.obs_names)
    if labels["refined_state"].isna().any():
        raise SystemExit("Labels do not align with AnnData obs_names or refined state map.")

    present, indices, missing = build_gene_index(source.raw.var, args.gene_symbol_column, all_markers)
    print(f"Using {len(present)} marker genes; missing {len(missing)}")
    counts = to_csr(source.raw.X[:, indices])
    total_counts = row_sums_backed(source.raw.X, source.n_obs, args.chunk_size)
    try:
        source.file.close()
    except Exception:
        pass

    metadata = labels[["donor_id", "disease", "disease_state", "refined_state"]].copy()
    groups, grouped_counts, grouped_totals = aggregate_by_group(counts, total_counts, metadata)
    gene_long = long_gene_table(groups, grouped_counts, grouped_totals, present)
    program_long = program_table(gene_long, {gene: [p for p, genes in MARKER_PROGRAMS.items() if gene in genes] for gene in present})

    gene_tests, program_tests = compare_focus_vs_others(gene_long, program_long, args.min_cells, exclude_flagged=True)
    disease_summary = disease_state_summary(program_long, args.min_cells)

    pd.DataFrame({"gene": present}).to_csv(tabledir / "pseudobulk_genes_present.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"gene": missing}).to_csv(tabledir / "pseudobulk_genes_missing.csv", index=False, encoding="utf-8-sig")
    groups.to_csv(tabledir / "donor_state_pseudobulk_groups.csv", index=False, encoding="utf-8-sig")
    gene_long.to_csv(tabledir / "donor_state_gene_pseudobulk_long.csv", index=False, encoding="utf-8-sig")
    program_long.to_csv(tabledir / "donor_state_program_pseudobulk_long.csv", index=False, encoding="utf-8-sig")
    gene_tests.to_csv(tabledir / "abc_apc_vs_other_gene_tests.csv", index=False, encoding="utf-8-sig")
    program_tests.to_csv(tabledir / "abc_apc_vs_other_program_tests.csv", index=False, encoding="utf-8-sig")
    disease_summary.to_csv(tabledir / "abc_apc_program_by_disease_state.csv", index=False, encoding="utf-8-sig")
    write_summary(outdir / "pseudobulk_state_expression_summary.md", present, missing, program_tests, gene_tests, disease_summary)
    print(f"Wrote pseudobulk outputs to: {outdir}")
    print(program_tests.sort_values("delta_focus_minus_other", ascending=False).head(10).to_string(index=False))


if __name__ == "__main__":
    main()
