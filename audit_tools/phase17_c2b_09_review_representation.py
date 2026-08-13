#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate C2B2-03: disease-blind representation diagnostics and review."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

MARKER_MODULES = {
    "B_identity": ["CD79A", "CD79B", "MS4A1", "CD19", "CD22", "CD37", "CD74"],
    "naive": ["TCL1A", "IGHD", "IL4R", "FCER2", "CCR7"],
    "memory": ["CD27", "AIM2", "GPR183", "TNFRSF13B", "BANK1"],
    "atypical": ["FCRL3", "FCRL5", "ITGAX", "TBX21", "ZEB2"],
    "plasmablast": ["MZB1", "JCHAIN", "XBP1", "SDC1", "TNFRSF17", "DERL3"],
    "interferon": ["IFI6", "IFIT1", "IFIT3", "ISG15", "MX1", "OAS1"],
    "T_NK": ["CD3D", "CD3E", "TRAC", "NKG7", "GNLY"],
    "myeloid": ["LYZ", "LST1", "TYROBP", "FCER1G", "S100A8"],
    "platelet": ["PPBP", "PF4", "GNG11", "RGS18"],
    "erythroid": ["HBA1", "HBA2", "HBB"],
}

PROTECTED_COLUMNS = {
    "disease", "disease_state", "diagnosis", "case_control", "case_status",
    "clinical_status", "sle_status", "activity", "disease_activity",
    "treatment", "medication", "response", "outcome", "flare", "ct_cov",
}


def resolution_key(resolution: float) -> str:
    return f"leiden_harmony_r{str(resolution).replace('.', '_')}"


def gene_lookup(var):
    lookup = {}
    for var_name, row in var.iterrows():
        for value in (var_name, row.get("gene_id", ""), row.get("feature_name", "")):
            symbol = str(value).upper()
            if symbol and symbol not in lookup:
                lookup[symbol] = str(var_name)
    return lookup


def extract_marker_expression(raw_path: Path, cell_ids, total_counts, chunk_size: int):
    import anndata as ad
    import numpy as np
    import pandas as pd

    raw = ad.read_h5ad(raw_path, backed="r")
    lookup = gene_lookup(raw.var)
    coverage_rows = []
    selected = []
    selected_symbols = []
    for module, genes in MARKER_MODULES.items():
        for gene in genes:
            var_name = lookup.get(gene)
            coverage_rows.append(
                {
                    "module": module,
                    "gene": gene,
                    "present": var_name is not None,
                    "var_name": var_name or "",
                }
            )
            if var_name is not None and var_name not in selected:
                selected.append(var_name)
                selected_symbols.append(gene)

    if not selected:
        raise RuntimeError("No marker genes were found in the raw object")
    row_positions = raw.obs_names.get_indexer(cell_ids)
    if (row_positions < 0).any():
        raise RuntimeError("Primary representation contains cells absent from the raw object")
    column_positions = raw.var_names.get_indexer(selected)
    normalized = np.zeros((len(cell_ids), len(selected)), dtype=np.float32)
    detected = np.zeros_like(normalized, dtype=bool)
    totals = np.asarray(total_counts, dtype=np.float64)
    for start in range(0, len(cell_ids), chunk_size):
        stop = min(start + chunk_size, len(cell_ids))
        positions = row_positions[start:stop]
        block = raw.X[positions]
        block = block[:, column_positions]
        dense = block.toarray() if hasattr(block, "toarray") else np.asarray(block)
        detected[start:stop] = dense > 0
        denominator = np.maximum(totals[start:stop, None], 1.0)
        normalized[start:stop] = np.log1p(dense / denominator * 1e4).astype(np.float32)
        print(f"[MARKERS] {stop:,}/{len(cell_ids):,} cells", flush=True)
    raw.file.close()
    return (
        pd.DataFrame(coverage_rows),
        selected_symbols,
        normalized,
        detected,
    )


def summarize_markers(obs, cluster_key, symbols, expression, detected):
    import numpy as np
    import pandas as pd

    clusters = obs[cluster_key].astype(str).to_numpy()
    gene_rows = []
    for cluster in sorted(set(clusters), key=lambda value: (len(value), value)):
        mask = clusters == cluster
        for index, gene in enumerate(symbols):
            gene_rows.append(
                {
                    "cluster": cluster,
                    "gene": gene,
                    "n_cells": int(mask.sum()),
                    "mean_log_normalized_expression": float(expression[mask, index].mean()),
                    "fraction_detected": float(detected[mask, index].mean()),
                }
            )
    gene_table = pd.DataFrame(gene_rows)

    module_rows = []
    symbol_index = {symbol: index for index, symbol in enumerate(symbols)}
    for cluster in sorted(set(clusters), key=lambda value: (len(value), value)):
        mask = clusters == cluster
        for module, genes in MARKER_MODULES.items():
            indices = [symbol_index[gene] for gene in genes if gene in symbol_index]
            if not indices:
                continue
            module_rows.append(
                {
                    "cluster": cluster,
                    "module": module,
                    "n_cells": int(mask.sum()),
                    "n_genes": len(indices),
                    "mean_module_log_expression": float(expression[mask][:, indices].mean()),
                    "fraction_any_gene_detected": float(detected[mask][:, indices].any(axis=1).mean()),
                }
            )
    return gene_table, pd.DataFrame(module_rows)


def plot_representation(primary, cluster_key: str, figures: Path):
    import matplotlib.pyplot as plt
    import numpy as np

    if "X_umap_unintegrated" not in primary.obsm or "X_umap_harmony" not in primary.obsm:
        return
    cohort = primary.obs["Processing_Cohort"].astype(str)
    clusters = primary.obs[cluster_key].astype(str)
    cohort_levels = sorted(cohort.unique())
    cluster_levels = sorted(clusters.unique(), key=lambda value: (len(value), value))
    cohort_palette = dict(zip(cohort_levels, plt.get_cmap("Dark2").colors))
    cluster_palette = dict(zip(cluster_levels, plt.get_cmap("tab20").colors * 4))
    point_size = 2.0 if primary.n_obs <= 10_000 else 0.35

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.5), constrained_layout=True)
    for row, (basis, title) in enumerate(
        (("X_umap_unintegrated", "Unintegrated"), ("X_umap_harmony", "Harmony"))
    ):
        coordinates = primary.obsm[basis]
        for level in cohort_levels:
            mask = cohort.to_numpy() == level
            axes[row, 0].scatter(
                coordinates[mask, 0], coordinates[mask, 1], s=point_size,
                color=cohort_palette[level], alpha=0.65, linewidths=0, rasterized=True,
                label=level,
            )
        for level in cluster_levels:
            mask = clusters.to_numpy() == level
            axes[row, 1].scatter(
                coordinates[mask, 0], coordinates[mask, 1], s=point_size,
                color=cluster_palette[level], alpha=0.7, linewidths=0, rasterized=True,
                label=level,
            )
        axes[row, 0].set_title(f"{title}: processing cohort", loc="left", fontsize=10)
        axes[row, 1].set_title(f"{title}: neutral cluster ID", loc="left", fontsize=10)
        for axis in axes[row]:
            axis.set_xticks([])
            axis.set_yticks([])
            for spine in axis.spines.values():
                spine.set_visible(False)
    axes[0, 0].legend(frameon=False, markerscale=4, fontsize=7, ncol=2, loc="best")
    axes[0, 1].legend(frameon=False, markerscale=4, fontsize=6, ncol=2, loc="best")
    fig.savefig(figures / "c2b2_representation_audit.png", dpi=260, bbox_inches="tight")
    fig.savefig(figures / "c2b2_representation_audit.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_marker_modules(module_table, figures: Path):
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    expression = module_table.pivot(
        index="cluster", columns="module", values="mean_module_log_expression"
    )
    detection = module_table.pivot(
        index="cluster", columns="module", values="fraction_any_gene_detected"
    ).reindex_like(expression)
    expression = expression.reindex(
        sorted(expression.index, key=lambda value: (len(str(value)), str(value)))
    )
    detection = detection.reindex(expression.index)
    column_order = [module for module in MARKER_MODULES if module in expression.columns]
    expression = expression[column_order]
    detection = detection[column_order]
    zscore = expression.apply(
        lambda column: (column - column.mean()) / column.std(ddof=0)
        if column.std(ddof=0) > 0 else column * 0,
        axis=0,
    )

    fig_width = max(8.5, len(column_order) * 0.9)
    fig_height = max(4.5, len(expression.index) * 0.38)
    fig, axis = plt.subplots(figsize=(fig_width, fig_height))
    color_map = plt.get_cmap("RdBu_r")
    for y, cluster in enumerate(expression.index):
        for x, module in enumerate(column_order):
            value = float(zscore.loc[cluster, module])
            size = 18 + 240 * float(detection.loc[cluster, module])
            axis.scatter(
                x, y, s=size, c=[value], cmap=color_map, vmin=-2.5, vmax=2.5,
                edgecolors="#333333", linewidths=0.25,
            )
    axis.set_xticks(range(len(column_order)), column_order, rotation=45, ha="right")
    axis.set_yticks(range(len(expression.index)), expression.index)
    axis.set_xlabel("")
    axis.set_ylabel("Disease-blind cluster ID")
    axis.invert_yaxis()
    axis.grid(False)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    color_mappable = plt.cm.ScalarMappable(
        norm=plt.Normalize(vmin=-2.5, vmax=2.5), cmap=color_map
    )
    color_mappable.set_array([])
    color_bar = fig.colorbar(color_mappable, ax=axis, fraction=0.025, pad=0.02)
    color_bar.set_label("Mean expression z score")
    size_handles = [
        axis.scatter(
            [], [], s=18 + 240 * fraction, facecolor="#bdbdbd",
            edgecolor="#333333", linewidth=0.25, label=f"{fraction:.0%}",
        )
        for fraction in (0.25, 0.50, 0.75, 1.00)
    ]
    axis.legend(
        handles=size_handles,
        title="Any module gene detected",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.10, 1.0),
        borderaxespad=0,
    )
    fig.tight_layout()
    fig.savefig(figures / "c2b2_marker_module_dotplot.png", dpi=280, bbox_inches="tight")
    fig.savefig(figures / "c2b2_marker_module_dotplot.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_branch_concordance(concordance, figures: Path):
    import matplotlib.pyplot as plt
    import seaborn as sns

    branch = concordance[concordance["comparison"].str.startswith("primary_all_cells_vs_")].copy()
    if branch.empty:
        return
    branch["comparison"] = branch["comparison"].str.replace("primary_all_cells_vs_", "", regex=False)
    branch["comparison"] = branch["comparison"].str.replace("_", " ", regex=False)
    matrix = branch.pivot(index="comparison", columns="resolution", values="adjusted_rand_index")
    fig, axis = plt.subplots(figsize=(7.2, 3.2))
    sns.heatmap(
        matrix, cmap="viridis", vmin=0, vmax=1, annot=True, fmt=".2f",
        linewidths=0.5, linecolor="white", cbar_kws={"label": "Adjusted Rand index"}, ax=axis,
    )
    axis.set_xlabel("Leiden resolution")
    axis.set_ylabel("")
    fig.tight_layout()
    fig.savefig(figures / "c2b2_branch_concordance.png", dpi=280, bbox_inches="tight")
    fig.savefig(figures / "c2b2_branch_concordance.pdf", bbox_inches="tight")
    plt.close(fig)


def check(name: str, passed: bool, detail: str):
    return name, {"pass": bool(passed), "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--primary-resolution", type=float, default=0.6)
    parser.add_argument("--chunk-size", type=int, default=10000)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd

    run_dir = Path(args.run_dir).resolve()
    figures = run_dir / "figures_review"
    figures.mkdir(parents=True, exist_ok=True)
    required_files = {
        "preparation": run_dir / "04_GATE_C2B2_PREPARATION.json",
        "fit": run_dir / "16_GATE_C2B2_FIT_SUMMARY.json",
        "hvg": run_dir / "02_hvg_branch_summary.csv",
        "feature_sensitivity": run_dir / "02b_feature_space_sensitivity_availability.csv",
        "mixing": run_dir / "10_primary_neighbor_mixing.csv",
        "bridge": run_dir / "11_primary_bridge_centroid_distances.csv",
        "coverage": run_dir / "12_primary_cluster_coverage.csv",
        "risk": run_dir / "13_residual_risk_localization.csv",
        "concordance": run_dir / "14_branch_and_resolution_concordance.csv",
        "primary": run_dir / "06_primary_all_cells_representation.h5ad",
        "singlet": run_dir / "07_singlet_sensitivity_representation.h5ad",
        "isg": run_dir / "08_isg_excluded_representation.h5ad",
    }
    missing = [str(path) for path in required_files.values() if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing Gate C2B2 files: {missing}")

    preparation = json.loads(required_files["preparation"].read_text(encoding="utf-8"))
    fit = json.loads(required_files["fit"].read_text(encoding="utf-8"))
    hvg = pd.read_csv(required_files["hvg"])
    feature_sensitivity = pd.read_csv(required_files["feature_sensitivity"])
    mixing = pd.read_csv(required_files["mixing"])
    bridge = pd.read_csv(required_files["bridge"])
    coverage = pd.read_csv(required_files["coverage"])
    risk = pd.read_csv(required_files["risk"])
    concordance = pd.read_csv(required_files["concordance"])
    primary = ad.read_h5ad(required_files["primary"])
    branch_objects = {
        "primary_all_cells": primary,
        "singlet_sensitivity": ad.read_h5ad(required_files["singlet"]),
        "isg_excluded": ad.read_h5ad(required_files["isg"]),
    }
    cluster_key = resolution_key(args.primary_resolution)
    if cluster_key not in primary.obs:
        raise RuntimeError(f"Primary representation lacks {cluster_key}")

    protected = sorted(
        column for obj in branch_objects.values() for column in obj.obs.columns
        if str(column).lower() in PROTECTED_COLUMNS
    )
    prep_metadata = ad.read_h5ad(run_dir / "03_prepared_log_union_hvg.h5ad", backed="r")
    raw_path = Path(prep_metadata.uns["phase17_c2b2_preparation"]["input_h5ad"])
    prep_metadata.file.close()
    residual_diagnostics = raw_path.parent / "10_residual_doublet_cell_diagnostics.csv.gz"
    if not residual_diagnostics.exists():
        raise RuntimeError(f"Residual diagnostics with total counts not found: {residual_diagnostics}")
    totals = pd.read_csv(residual_diagnostics, usecols=["cell_id", "total_counts"]).set_index("cell_id")
    aligned_totals = totals.reindex(primary.obs_names)
    if aligned_totals["total_counts"].isna().any():
        raise RuntimeError("Total-count diagnostics do not align to primary cells")

    marker_coverage, symbols, expression, detected = extract_marker_expression(
        raw_path, primary.obs_names, aligned_totals["total_counts"].to_numpy(), args.chunk_size
    )
    marker_coverage.to_csv(run_dir / "18_marker_coverage.csv", index=False, encoding="utf-8-sig")
    gene_summary, module_summary = summarize_markers(
        primary.obs, cluster_key, symbols, expression, detected
    )
    gene_summary.to_csv(run_dir / "19_marker_gene_by_cluster.csv", index=False, encoding="utf-8-sig")
    module_summary.to_csv(run_dir / "20_marker_module_by_cluster.csv", index=False, encoding="utf-8-sig")

    all_gene_summaries = []
    all_module_summaries = []
    for resolution in fit["resolutions"]:
        key = resolution_key(float(resolution))
        if key not in primary.obs:
            continue
        genes_at_resolution, modules_at_resolution = summarize_markers(
            primary.obs, key, symbols, expression, detected
        )
        genes_at_resolution.insert(0, "resolution", float(resolution))
        modules_at_resolution.insert(0, "resolution", float(resolution))
        all_gene_summaries.append(genes_at_resolution)
        all_module_summaries.append(modules_at_resolution)
    pd.concat(all_gene_summaries, ignore_index=True).to_csv(
        run_dir / "23_marker_gene_all_resolutions.csv", index=False, encoding="utf-8-sig"
    )
    pd.concat(all_module_summaries, ignore_index=True).to_csv(
        run_dir / "24_marker_module_all_resolutions.csv", index=False, encoding="utf-8-sig"
    )

    plot_representation(primary, cluster_key, figures)
    plot_marker_modules(module_summary, figures)
    plot_branch_concordance(concordance, figures)

    calls = int(primary.obs["residual_doublet_auto_call"].sum())
    branch_metadata = {
        name: obj.uns.get("phase17_c2b2_branch", {}) for name, obj in branch_objects.items()
    }
    harmony_diagnostics_captured = all(
        metadata.get("harmony_converged") is not None for metadata in branch_metadata.values()
    )
    harmony_all_converged = harmony_diagnostics_captured and all(
        metadata.get("harmony_converged") is True for metadata in branch_metadata.values()
    )
    mixing_index = mixing.set_index(["representation", "field"])
    library_before = float(mixing_index.loc[("unintegrated_pca", "library_uuid"), "mean_same_group_fraction"])
    library_after = float(mixing_index.loc[("harmony_pca", "library_uuid"), "mean_same_group_fraction"])
    cohort_before = float(mixing_index.loc[("unintegrated_pca", "Processing_Cohort"), "mean_same_group_fraction"])
    cohort_after = float(mixing_index.loc[("harmony_pca", "Processing_Cohort"), "mean_same_group_fraction"])
    bridge_medians = bridge.groupby("representation", observed=True)[
        ["euclidean_centroid_distance", "cosine_centroid_distance"]
    ].median()
    bridge_improved = (
        {"unintegrated_pca", "harmony_pca"}.issubset(bridge_medians.index)
        and bridge_medians.loc["harmony_pca", "cosine_centroid_distance"]
        <= bridge_medians.loc["unintegrated_pca", "cosine_centroid_distance"]
    )
    primary_coverage = coverage[np.isclose(coverage["resolution"], args.primary_resolution)]
    primary_risk = risk[np.isclose(risk["resolution"], args.primary_resolution)]
    branch_at_primary = concordance[
        np.isclose(pd.to_numeric(concordance["resolution"], errors="coerce"), args.primary_resolution)
        & concordance["comparison"].str.startswith("primary_all_cells_vs_")
    ].set_index("comparison")
    singlet_ari = float(
        branch_at_primary.loc[
            "primary_all_cells_vs_singlet_sensitivity", "adjusted_rand_index"
        ]
    )
    isg_ari = float(
        branch_at_primary.loc[
            "primary_all_cells_vs_isg_excluded", "adjusted_rand_index"
        ]
    )
    expected_hvg = int(hvg["n_hvg"].iloc[0])
    test_mode = bool(preparation.get("test_mode"))
    ig_row = feature_sensitivity.loc[
        feature_sensitivity["sensitivity"] == "immunoglobulin_dominance"
    ].iloc[0]

    checks = dict(
        [
            check("fit_complete", fit.get("status") == "REPRESENTATION_FIT_COMPLETE_REVIEW_REQUIRED", fit.get("status", "missing")),
            check("outcome_lock", not protected, f"protected columns={protected or 'none'}"),
            check("primary_cells", primary.n_obs == preparation["working_cells"], f"{primary.n_obs:,}/{preparation['working_cells']:,}"),
            check("singlet_branch_exact", branch_objects["singlet_sensitivity"].n_obs == primary.n_obs - calls, f"{branch_objects['singlet_sensitivity'].n_obs:,} = {primary.n_obs:,} - {calls:,}"),
            check("hvg_counts", bool((hvg["n_hvg"] == expected_hvg).all()), f"all branches={expected_hvg:,}"),
            check("technical_nuisance_excluded", bool((hvg["n_technical_nuisance"] == 0).all()), f"maximum={int(hvg['n_technical_nuisance'].max())}"),
            check("primary_ig_excluded", int(hvg.loc[hvg["branch"] == "primary_ig_excluded", "n_immunoglobulin"].iloc[0]) == 0, "primary immunoglobulin HVGs=0"),
            check("isg_branch_excluded", int(hvg.loc[hvg["branch"] == "isg_excluded", "n_strong_isg"].iloc[0]) == 0, "ISG-excluded strong ISG HVGs=0"),
            check(
                "ig_dominance_sensitivity_documented",
                ig_row["status"] == "NOT_EVALUABLE_SOURCE_FEATURE_SPACE"
                and int(ig_row["canonical_ig_loci_in_source"]) < 10
                and int(ig_row["canonical_constant_genes_present"]) == 0,
                (
                    f"status={ig_row['status']}; canonical IG loci="
                    f"{int(ig_row['canonical_ig_loci_in_source'])}; constant genes="
                    f"{int(ig_row['canonical_constant_genes_present'])}"
                ),
            ),
            check("mixing_improved", library_after <= library_before and cohort_after <= cohort_before, f"library {library_before:.3f}->{library_after:.3f}; cohort {cohort_before:.3f}->{cohort_after:.3f}"),
            check("bridge_consistency", bool(bridge_improved), "Harmony median bridge-pair cosine distance did not increase"),
            check("cluster_technical_coverage", bool((primary_coverage["max_library_fraction"] <= 0.50).all()), f"maximum library fraction={primary_coverage['max_library_fraction'].max():.3f}"),
            check("cluster_biological_coverage", bool((primary_coverage["n_samples"] >= 3).all()), f"minimum samples={int(primary_coverage['n_samples'].min())}"),
            check("residual_risk_not_dominant", bool((primary_risk["residual_auto_call_fraction"] <= 0.25).all()), f"maximum={primary_risk['residual_auto_call_fraction'].max():.3f}"),
            check("singlet_branch_stability", singlet_ari >= 0.70, f"ARI={singlet_ari:.3f}; threshold=0.700"),
            check("isg_excluded_branch_stability", isg_ari >= 0.70, f"ARI={isg_ari:.3f}; threshold=0.700"),
            check("marker_coverage", bool(marker_coverage.groupby("module")["present"].sum().ge(2).all()), "at least two genes present per marker module"),
            check("harmony_diagnostics_captured", harmony_diagnostics_captured, "convergence fields stored for all branches"),
            check("harmony_all_converged", harmony_all_converged, "all representation branches converged within the configured limit"),
        ]
    )

    structural_names = {
        "fit_complete", "outcome_lock", "primary_cells", "singlet_branch_exact",
        "hvg_counts", "technical_nuisance_excluded", "primary_ig_excluded",
        "isg_branch_excluded", "ig_dominance_sensitivity_documented",
        "mixing_improved", "bridge_consistency",
        "singlet_branch_stability", "isg_excluded_branch_stability",
        "marker_coverage",
    }
    structural_pass = all(checks[name]["pass"] for name in structural_names)
    if test_mode:
        decision = (
            "SOFTWARE_TEST_PASS_NOT_BIOLOGICAL_GATE" if structural_pass
            else "SOFTWARE_TEST_FAIL"
        )
    else:
        decision = (
            "READY_FOR_C2B3_ADVISOR_REVIEW"
            if all(value["pass"] for value in checks.values())
            else "HOLD_GATE_C2B2_REVIEW_REQUIRED"
        )

    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "disease_blind": True,
        "test_mode": test_mode,
        "primary_resolution": args.primary_resolution,
        "checks": checks,
        "manual_review_still_required": [
            "marker coherence and contaminant localization",
            "rare-state biological and technical coverage",
            "branch discordance interpretation",
            "B-lineage outside-label candidate mapping",
        ],
    }
    (run_dir / "22_GATE_C2B2_REVIEW.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Gate C2B2 disease-blind representation review",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- Primary cells: {primary.n_obs:,}",
        f"- Residual-risk-negative sensitivity cells: {branch_objects['singlet_sensitivity'].n_obs:,}",
        f"- Primary diagnostic resolution: {args.primary_resolution:g}",
        f"- Disease/outcome fields used: none",
        f"- Software-test mode: {test_mode}",
        "",
        "## Programmatic checks",
        "",
    ]
    for name, result in checks.items():
        status = "PASS" if result["pass"] else "FAIL"
        lines.append(f"- [{status}] {name}: {result['detail']}")
    if test_mode:
        interpretation = [
            "Software-test output verifies execution and file contracts only. It does not",
            "authorize full-data state names, cell exclusions or biological claims.",
        ]
    else:
        interpretation = [
            "This full-data output verifies the representation and diagnostic contracts at",
            "the selected backbone resolution. State names, cell exclusions and biological",
            "claims remain unauthorized until resampling stability, ranked markers and",
            "outside-label candidate mapping pass advisor review at Gate C2B3.",
        ]
    lines.extend(["", "## Binding interpretation", "", *interpretation, ""])
    (run_dir / "21_GATE_C2B2_REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(review, ensure_ascii=False, indent=2), flush=True)
    return 0 if not decision.endswith("FAIL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
