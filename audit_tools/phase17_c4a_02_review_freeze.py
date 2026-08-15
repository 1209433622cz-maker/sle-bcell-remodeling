#!/usr/bin/env python3
"""Gate C4A-02: review raw pseudobulk support and adjudicate the pre-effect freeze."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def check(name, passed, detail):
    return name, {"pass": bool(passed), "detail": str(detail)}


def numeric_rank(table, columns):
    import numpy as np

    return int(np.linalg.matrix_rank(table[list(columns)].to_numpy(dtype=float)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--raw-h5ad", required=True)
    parser.add_argument("--gate-c3-dir", required=True)
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import anndata as ad
    import numpy as np
    import pandas as pd
    from scipy import sparse

    run = Path(args.run_dir).resolve()
    raw_path = Path(args.raw_h5ad).resolve()
    gate_c3 = Path(args.gate_c3_dir).resolve()
    figures = run / "figures"
    figures.mkdir(exist_ok=True)

    audit = json.loads((run / "01_raw_input_and_cell_id_audit.json").read_text(encoding="utf-8"))
    contract = json.loads((run / "13_GATE_C4A_FREEZE_CONTRACT.json").read_text(encoding="utf-8"))
    matrix = sparse.load_npz(run / "02_pseudobulk_counts_all_branches.npz").tocsr()
    row_metadata = pd.read_csv(run / "03_pseudobulk_row_metadata.csv")
    genes = pd.read_csv(run / "04_gene_universe.csv.gz", low_memory=False)
    support = pd.read_csv(run / "05_compartment_support_audit.csv")
    primary = pd.read_csv(run / "06_primary_bconv_model_matrix.csv")
    validation = pd.read_csv(run / "07_validation_bconv_model_matrix.csv")
    flare = pd.read_csv(run / "08_flare_bconv_model_matrix.csv")
    overlap = pd.read_csv(run / "09_replication_nonoverlap_audit.csv")
    basc = pd.read_csv(run / "10_basc_pseudobulk_support.csv")
    dictionary = pd.read_csv(run / "11_program_dictionary.csv")
    availability = pd.read_csv(run / "12_program_gene_availability.csv")

    primary_columns = ("intercept", "is_managed", "age_centered", "ethnicity_asian")
    validation_columns = ("intercept", "is_managed", "age_centered")
    flare_columns = ("intercept", "is_flare", "age_centered", "ethnicity_european")
    program_summary = (
        availability.groupby(["program_id", "analysis_family"], observed=True)
        .agg(
            requested_genes=("gene_symbol", "size"),
            available_genes=("available", "sum"),
        )
        .reset_index()
    )
    program_summary["available_fraction"] = (
        program_summary["available_genes"] / program_summary["requested_genes"]
    )

    all_rows = row_metadata.loc[row_metadata["branch"] == "all_hard_qc"]
    sensitivity_rows = row_metadata.loc[row_metadata["branch"] == "residual_risk_negative"]
    all_cell_counts = int(
        all_rows.loc[all_rows["compartment"].isin(["B_CONV", "B_ASC"]), "cell_count"].sum()
    )
    sensitivity_cell_counts = int(
        sensitivity_rows.loc[
            sensitivity_rows["compartment"].isin(["B_CONV", "B_ASC"]), "cell_count"
        ].sum()
    )
    matrix_integer = bool(
        matrix.data.size == 0
        or (np.all(matrix.data >= 0) and np.all(matrix.data == np.floor(matrix.data)))
    )
    row_library_sizes = np.asarray(matrix.sum(axis=1)).ravel().astype(np.int64)

    cell = pd.read_csv(
        gate_c3 / "01_unlocked_cell_metadata.csv.gz",
        usecols=["residual_doublet_auto_call"],
    )
    keep_sensitivity = ~cell["residual_doublet_auto_call"].astype(str).str.lower().isin(
        {"true", "1", "yes"}
    ).to_numpy()
    raw = ad.read_h5ad(raw_path, backed="r")
    direct_all_gene = np.zeros(raw.n_vars, dtype=np.int64)
    direct_sensitivity_gene = np.zeros(raw.n_vars, dtype=np.int64)
    for start in range(0, raw.n_obs, 10000):
        end = min(start + 10000, raw.n_obs)
        chunk = raw.X[start:end, :]
        chunk = chunk.tocsr() if sparse.issparse(chunk) else sparse.csr_matrix(chunk)
        chunk = chunk.astype(np.int64)
        direct_all_gene += np.asarray(chunk.sum(axis=0)).ravel().astype(np.int64)
        direct_sensitivity_gene += np.asarray(
            chunk[keep_sensitivity[start:end], :].sum(axis=0)
        ).ravel().astype(np.int64)
    raw.file.close()
    all_indices = row_metadata.index[row_metadata["branch"] == "all_hard_qc"].to_numpy()
    sensitivity_indices = row_metadata.index[
        row_metadata["branch"] == "residual_risk_negative"
    ].to_numpy()
    pseudobulk_all_gene = np.asarray(matrix[all_indices, :].sum(axis=0)).ravel().astype(np.int64)
    pseudobulk_sensitivity_gene = np.asarray(
        matrix[sensitivity_indices, :].sum(axis=0)
    ).ravel().astype(np.int64)
    all_gene_difference = direct_all_gene - pseudobulk_all_gene
    sensitivity_gene_difference = direct_sensitivity_gene - pseudobulk_sensitivity_gene
    all_gene_equal = bool(np.array_equal(direct_all_gene, pseudobulk_all_gene))
    sensitivity_gene_equal = bool(
        np.array_equal(direct_sensitivity_gene, pseudobulk_sensitivity_gene)
    )
    gene_conservation = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "audit_method": "independent direct raw-X column sums versus final pseudobulk branch column sums",
        "genes": raw.n_vars,
        "all_hard_qc": {
            "exact_equal": all_gene_equal,
            "mismatched_genes": int(np.count_nonzero(all_gene_difference)),
            "maximum_absolute_difference": int(np.abs(all_gene_difference).max()),
        },
        "residual_risk_negative": {
            "exact_equal": sensitivity_gene_equal,
            "mismatched_genes": int(np.count_nonzero(sensitivity_gene_difference)),
            "maximum_absolute_difference": int(np.abs(sensitivity_gene_difference).max()),
        },
    }
    (run / "14_gene_count_conservation_audit.json").write_text(
        json.dumps(gene_conservation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run / "14_gene_count_conservation_audit.md").write_text(
        "\n".join(
            [
                "# Gate C4A per-gene count-conservation audit",
                "",
                "- Method: direct raw-X column sums compared with final pseudobulk branch column sums.",
                f"- Genes audited: {raw.n_vars:,}",
                f"- All-hard-QC exact equality: {all_gene_equal}; mismatches={int(np.count_nonzero(all_gene_difference))}; maximum absolute difference={int(np.abs(all_gene_difference).max())}",
                f"- Residual-risk-negative exact equality: {sensitivity_gene_equal}; mismatches={int(np.count_nonzero(sensitivity_gene_difference))}; maximum absolute difference={int(np.abs(sensitivity_gene_difference).max())}",
            ]
        ),
        encoding="utf-8",
    )

    checks = dict(
        [
            check(
                "extraction_status",
                audit.get("status") == "EXTRACTION_COMPLETE_REVIEW_REQUIRED",
                audit.get("status"),
            ),
            check(
                "effect_blind_contract",
                audit.get("effect_estimates_inspected") is False
                and contract.get("effect_estimates_inspected") is False,
                "no disease expression coefficient inspected",
            ),
            check(
                "raw_checksum",
                audit["raw_h5ad"]["sha256"]
                == "DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5",
                audit["raw_h5ad"]["sha256"],
            ),
            check(
                "exact_cell_ids",
                audit["cell_id_exact_set"] is True and audit["cell_id_exact_order"] is True,
                f"set={audit['cell_id_exact_set']}; order={audit['cell_id_exact_order']}",
            ),
            check(
                "raw_keys_concordant",
                sum(audit["key_mismatches"].values()) == 0,
                json.dumps(audit["key_mismatches"], sort_keys=True),
            ),
            check(
                "raw_integer_nonnegative",
                audit["raw_h5ad"]["minimum_nonzero"] >= 1 and matrix_integer,
                f"source range={audit['raw_h5ad']['minimum_nonzero']}-{audit['raw_h5ad']['maximum_nonzero']}; final integer={matrix_integer}",
            ),
            check(
                "pseudobulk_shape",
                matrix.shape == (len(row_metadata), len(genes)),
                f"matrix={matrix.shape}; rows={len(row_metadata)}; genes={len(genes)}",
            ),
            check(
                "pseudobulk_library_sizes",
                bool(np.array_equal(row_library_sizes, row_metadata["library_size_umi"].to_numpy(dtype=np.int64))),
                "matrix row sums equal row metadata",
            ),
            check(
                "raw_count_conservation",
                audit["count_conservation_pass"] is True
                and int(audit["primary_branch_umi_total"]) == int(audit["raw_h5ad"]["raw_umi_total"]),
                f"raw={audit['raw_h5ad']['raw_umi_total']}; all-hard-QC={audit['primary_branch_umi_total']}",
            ),
            check(
                "per_gene_count_conservation",
                all_gene_equal and sensitivity_gene_equal,
                f"all-hard-QC mismatches={int(np.count_nonzero(all_gene_difference))}; sensitivity mismatches={int(np.count_nonzero(sensitivity_gene_difference))}",
            ),
            check(
                "dual_branch_cell_counts",
                all_cell_counts == 150402 and sensitivity_cell_counts == 150402 - 1972,
                f"all={all_cell_counts}; sensitivity={sensitivity_cell_counts}",
            ),
            check(
                "gene_ids_unique",
                genes["ensembl_id"].is_unique and len(genes) == 30172,
                f"unique={genes['ensembl_id'].nunique()}; total={len(genes)}",
            ),
            check(
                "primary_bconv_support",
                len(primary) >= 80
                and int((primary["disease_state"] == "na").sum()) >= 40
                and int((primary["disease_state"] == "managed").sum()) >= 40,
                f"n={len(primary)}; normal={(primary['disease_state'] == 'na').sum()}; managed={(primary['disease_state'] == 'managed').sum()}",
            ),
            check(
                "validation_bconv_support",
                len(validation) >= 50
                and int((validation["disease_state"] == "na").sum()) >= 15
                and int((validation["disease_state"] == "managed").sum()) >= 25,
                f"n={len(validation)}; normal={(validation['disease_state'] == 'na').sum()}; managed={(validation['disease_state'] == 'managed').sum()}",
            ),
            check(
                "flare_bconv_support",
                len(flare) >= 30
                and int((flare["disease_state"] == "na").sum()) >= 15
                and int((flare["disease_state"] == "flare").sum()) >= 15,
                f"n={len(flare)}; normal={(flare['disease_state'] == 'na').sum()}; flare={(flare['disease_state'] == 'flare').sum()}",
            ),
            check(
                "design_ranks",
                numeric_rank(primary, primary_columns) == len(primary_columns)
                and numeric_rank(validation, validation_columns) == len(validation_columns)
                and numeric_rank(flare, flare_columns) == len(flare_columns),
                f"primary={numeric_rank(primary, primary_columns)}/{len(primary_columns)}; validation={numeric_rank(validation, validation_columns)}/{len(validation_columns)}; flare={numeric_rank(flare, flare_columns)}/{len(flare_columns)}",
            ),
            check(
                "replication_nonoverlap_support",
                int(overlap.loc[overlap["analysis"] == "validation", "nonoverlap_reference_n"].iloc[0]) >= 15
                and int(overlap.loc[overlap["analysis"] == "validation", "nonoverlap_exposed_n"].iloc[0]) >= 25,
                overlap.to_json(orient="records"),
            ),
            check(
                "program_dictionary_frozen",
                dictionary["program_id"].nunique() == 9
                and int((dictionary["analysis_family"] == "primary_confirmatory").groupby(dictionary["program_id"]).any().sum()) == 4,
                f"programs={dictionary['program_id'].nunique()}; primary={program_summary.loc[program_summary['analysis_family'] == 'primary_confirmatory', 'program_id'].nunique()}",
            ),
            check(
                "program_gene_availability",
                bool((program_summary["available_fraction"] >= 0.8).all()),
                f"minimum={program_summary['available_fraction'].min():.3f}",
            ),
            check(
                "hard_label_guard",
                contract["identity"]["hard_naive_memory_authorized"] is False,
                "continuous within-B_CONV programs only",
            ),
        ]
    )

    basc20 = basc.loc[basc["minimum_basc_cells"] == 20]
    basc_min_group = (
        basc20.groupby("analysis", observed=True)["eligible_strata"].min().to_dict()
    )
    basc_gene_level_authorized = bool(
        basc_min_group
        and all(value >= 10 for value in basc_min_group.values())
    )
    bconv_pass = all(result["pass"] for result in checks.values())
    decision = (
        "PASS_GATE_C4A_BCONV_RAW_PSEUDOBULK_AND_PROGRAM_FREEZE"
        if bconv_pass
        else "HOLD_GATE_C4A_REPAIR_REQUIRED"
    )

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))

    primary_support = support.loc[
        (support["branch"] == "all_hard_qc") & (support["bconv_cells"] >= 50)
    ]
    cohort_states = ["na", "managed", "flare", "treated"]
    support_matrix = (
        primary_support.groupby(["Processing_Cohort", "disease_state"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(index=[1.0, 2.0, 3.0, 4.0], columns=cohort_states, fill_value=0)
    )
    image = axes[0, 0].imshow(support_matrix.to_numpy(), cmap="Blues", aspect="auto", vmin=0)
    for row in range(support_matrix.shape[0]):
        for column in range(support_matrix.shape[1]):
            axes[0, 0].text(
                column, row, str(int(support_matrix.iloc[row, column])),
                ha="center", va="center", fontsize=7,
            )
    axes[0, 0].set_xticks(range(4), ["Normal", "Managed", "Flare", "Treated"])
    axes[0, 0].set_yticks(range(4), ["C1", "C2", "C3", "C4"])
    axes[0, 0].set(xlabel="Disease state", ylabel="Processing cohort")
    fig.colorbar(
        image, ax=axes[0, 0], fraction=0.046, pad=0.04,
        label="Conventional B-cell strata (>=50 cells)",
    )

    plot_basc = (
        basc.groupby(["analysis", "minimum_basc_cells"], observed=True)["eligible_strata"]
        .min()
        .reset_index()
    )
    analysis_order = ["primary_c4", "validation_c2_european_female", "flare_c3"]
    colors = ["#007C91", "#3366A6", "#D2691E"]
    for analysis, color in zip(analysis_order, colors):
        table = plot_basc.loc[plot_basc["analysis"] == analysis]
        axes[0, 1].plot(
            table["minimum_basc_cells"], table["eligible_strata"],
            marker="o", markersize=3.5, linewidth=1.1, color=color,
            label={
                "primary_c4": "Primary C4",
                "validation_c2_european_female": "Validation C2",
                "flare_c3": "Flare C3",
            }[analysis],
        )
    axes[0, 1].axhline(10, color="#555555", linestyle="--", linewidth=0.8)
    axes[0, 1].set_xticks([1, 5, 10, 20, 50])
    axes[0, 1].set(xlabel="Minimum ASC cells", ylabel="Minimum eligible strata per group")
    axes[0, 1].legend(frameon=False, fontsize=7)

    program_order = [
        "NAIVE_TO_MEMORY_AXIS", "ATYPICAL_LOW_NAIVE_AXIS", "APC_HLA", "IFN_ISG",
        "ACTIVATION_STRESS", "TLR7_INNATE", "PLATELET_AMBIENT_QC",
        "ASC_UPR_IDENTITY_QC", "PAN_B_IDENTITY_QC",
    ]
    program_labels = {
        "NAIVE_TO_MEMORY_AXIS": "Naive-to-memory",
        "ATYPICAL_LOW_NAIVE_AXIS": "Atypical/low-naive",
        "APC_HLA": "APC/HLA",
        "IFN_ISG": "IFN/ISG",
        "ACTIVATION_STRESS": "Activation/stress",
        "TLR7_INNATE": "TLR7/innate",
        "PLATELET_AMBIENT_QC": "Platelet/ambient QC",
        "ASC_UPR_IDENTITY_QC": "ASC/UPR identity QC",
        "PAN_B_IDENTITY_QC": "Pan-B identity QC",
    }
    program_plot = program_summary.set_index("program_id").loc[program_order].reset_index()
    axes[1, 0].barh(
        np.arange(len(program_plot)),
        100 * program_plot["available_fraction"],
        color=[
            "#007C91" if family == "primary_confirmatory" else "#9EA7AD"
            for family in program_plot["analysis_family"]
        ],
    )
    axes[1, 0].axvline(80, color="#555555", linestyle="--", linewidth=0.8)
    axes[1, 0].set_yticks(
        np.arange(len(program_plot)), [program_labels[value] for value in program_plot["program_id"]]
    )
    axes[1, 0].invert_yaxis()
    axes[1, 0].set(xlabel="Available program genes (%)", xlim=(0, 105))

    bconv_rows = row_metadata.loc[
        (row_metadata["branch"] == "all_hard_qc")
        & (row_metadata["compartment"] == "B_CONV")
        & (row_metadata["cell_count"] >= 50)
    ]
    cohort_values = [
        np.log10(
            bconv_rows.loc[
                bconv_rows["Processing_Cohort"] == cohort, "library_size_umi"
            ].to_numpy(dtype=float)
        )
        for cohort in (1, 2, 3, 4)
    ]
    boxes = axes[1, 1].boxplot(cohort_values, patch_artist=True, widths=0.55, showfliers=False)
    for patch, color in zip(boxes["boxes"], ["#6BAED6", "#74C476", "#FDAE6B", "#9E9AC8"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    axes[1, 1].set_xticks(range(1, 5), ["C1", "C2", "C3", "C4"])
    axes[1, 1].set(
        xlabel="Processing cohort", ylabel="log10 conventional B-cell pseudobulk UMIs"
    )

    for label, axis in zip("ABCD", axes.flat):
        axis.text(-0.16, 1.06, label, transform=axis.transAxes, fontsize=10, fontweight="bold")
        axis.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.20, right=0.98, bottom=0.11, top=0.96, wspace=0.48, hspace=0.40)
    fig.savefig(figures / "gate_c4a_raw_pseudobulk_and_program_freeze.png", dpi=300)
    fig.savefig(figures / "gate_c4a_raw_pseudobulk_and_program_freeze.pdf")
    plt.close(fig)

    review = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "effect_estimates_inspected": False,
        "bconv_gene_level_pseudobulk_authorized": bconv_pass,
        "bconv_continuous_program_models_authorized": bconv_pass,
        "basc_gene_level_pseudobulk_authorized": basc_gene_level_authorized,
        "basc_minimum_group_support_at_20_cells": basc_min_group,
        "checks": checks,
        "next_if_pass": "install and validate a negative-binomial pseudobulk engine, then fit Gate C4B exactly from the frozen B_CONV matrices and programs",
        "next_if_hold": "repair raw-count conservation, design support or program availability before any expression coefficient",
        "binding_interpretation": (
            "B_CONV raw-count pseudobulk and continuous-program analysis may proceed. B_ASC gene-level disease pseudobulk is not authorized because per-group sample support is inadequate."
            if bconv_pass and not basc_gene_level_authorized
            else "See authorization flags; no unsupported compartment may proceed."
        ),
    }
    (run / "14_GATE_C4A_ADVISOR_DECISION.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Gate C4A raw pseudobulk and program-freeze advisor decision",
        "",
        f"**Decision:** `{decision}`",
        "",
        f"- B_CONV gene-level pseudobulk authorized: {bconv_pass}",
        f"- B_CONV continuous-program models authorized: {bconv_pass}",
        f"- B_ASC gene-level disease pseudobulk authorized: {basc_gene_level_authorized}",
        f"- Primary B_CONV design: n={len(primary)} ({(primary['disease_state'] == 'na').sum()} normal / {(primary['disease_state'] == 'managed').sum()} managed)",
        f"- Validation B_CONV design: n={len(validation)} ({(validation['disease_state'] == 'na').sum()} normal / {(validation['disease_state'] == 'managed').sum()} managed)",
        f"- Flare B_CONV design: n={len(flare)} ({(flare['disease_state'] == 'na').sum()} normal / {(flare['disease_state'] == 'flare').sum()} flare)",
        f"- Programs available: {len(program_summary)}/{len(program_summary)}; minimum gene coverage={100 * program_summary['available_fraction'].min():.1f}%",
        "- Disease expression coefficients inspected: False",
        "",
        "## Checks",
        "",
    ]
    for name, result in checks.items():
        lines.append(f"- [{'PASS' if result['pass'] else 'FAIL'}] {name}: {result['detail']}")
    lines.extend(
        [
            "",
            "## Binding interpretation",
            "",
            review["binding_interpretation"],
            "",
            "## Next stage",
            "",
            review["next_if_pass"] if bconv_pass else review["next_if_hold"],
        ]
    )
    (run / "14_GATE_C4A_ADVISOR_DECISION.md").write_text("\n".join(lines), encoding="utf-8")

    status = {
        "status": decision,
        "raw_pseudobulk_complete": True,
        "effect_estimates_inspected": False,
        "bconv_gene_level_pseudobulk_authorized": bconv_pass,
        "bconv_continuous_program_models_authorized": bconv_pass,
        "basc_gene_level_pseudobulk_authorized": basc_gene_level_authorized,
    }
    (run / "00_GATE_C4A_RUN_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run / "00_GATE_C4A_RUN_STATUS.md").write_text(
        "\n".join(
            [
                "# Gate C4A run status",
                "",
                f"**Status:** `{decision}`",
                "",
                "- Raw pseudobulk extraction complete: True",
                "- Disease expression coefficients inspected: False",
                f"- B_CONV gene-level pseudobulk authorized: {bconv_pass}",
                f"- B_CONV continuous-program models authorized: {bconv_pass}",
                f"- B_ASC gene-level disease pseudobulk authorized: {basc_gene_level_authorized}",
                "",
                "See `14_GATE_C4A_ADVISOR_DECISION.md` and `13_GATE_C4A_FREEZE_CONTRACT.md`.",
            ]
        ),
        encoding="utf-8",
    )

    manifest_rows = []
    for path in sorted(run.rglob("*")):
        if (
            path.is_file()
            and path.name != "15_gate_c4a_integrity_manifest.csv"
            and "checkpoints" not in path.parts
        ):
            relative = path.relative_to(run).as_posix()
            manifest_rows.append(
                {
                    "relative_path": relative,
                    "size_bytes": path.stat().st_size,
                    "sha256": hash_file(path),
                    "distribution": (
                        "local_only_recomputable"
                        if path.suffix.lower() in {".npz", ".gz"}
                        else "git_trackable"
                    ),
                }
            )
    pd.DataFrame(manifest_rows).to_csv(
        run / "15_gate_c4a_integrity_manifest.csv", index=False, encoding="utf-8-sig"
    )
    print(json.dumps(review, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
