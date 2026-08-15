#!/usr/bin/env python3
"""Gate C4B-01: export analysis-specific matrices from the frozen C4A counts."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path


EXPECTED_C4A_STATUS = "PASS_GATE_C4A_BCONV_RAW_PSEUDOBULK_AND_PROGRAM_FREEZE"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def normalize_id(value) -> str:
    text = str(value)
    return text[:-2] if text.endswith(".0") else text


def build_threshold_design(support, threshold: int):
    work = support.loc[
        (support["branch"] == "all_hard_qc")
        & (support["Processing_Cohort"] == 4)
        & support["disease_state"].isin(["na", "managed"])
        & (support["bconv_cells"] >= threshold)
    ].copy()
    work.insert(0, "analysis_id", f"C4B_PRIMARY_C4_BCONV_MIN{threshold}")
    work["intercept"] = 1.0
    work["age_centered"] = work["age_years"] - work["age_years"].mean()
    work["ethnicity_asian"] = (work["ethnicity"] == "Asian").astype(int)
    work["ethnicity_european"] = (work["ethnicity"] == "European American").astype(int)
    work["is_managed"] = (work["disease_state"] == "managed").astype(int)
    work["is_flare"] = 0
    return work.sort_values(["disease_state", "sample_uuid"]).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-c4a-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import numpy as np
    import pandas as pd
    from scipy import sparse
    from scipy.io import mmwrite

    source = Path(args.gate_c4a_dir).resolve()
    output = Path(args.output_dir).resolve()
    matrix_dir = output / "02_matrix_exports"
    matrix_dir.mkdir(parents=True, exist_ok=True)

    decision = json.loads((source / "14_GATE_C4A_ADVISOR_DECISION.json").read_text(encoding="utf-8"))
    if decision.get("decision") != EXPECTED_C4A_STATUS:
        raise RuntimeError(f"Gate C4A is not authorized: {decision.get('decision')}")
    if decision.get("effect_estimates_inspected"):
        raise RuntimeError("Gate C4A contract reports pre-freeze effect inspection")

    manifest = pd.read_csv(source / "15_gate_c4a_integrity_manifest.csv")
    manifest_failures = []
    for row in manifest.itertuples(index=False):
        path = source / str(row.relative_path)
        if not path.is_file():
            manifest_failures.append(f"missing:{row.relative_path}")
        elif path.stat().st_size != int(row.size_bytes):
            manifest_failures.append(f"size:{row.relative_path}")
        elif sha256(path) != str(row.sha256).upper():
            manifest_failures.append(f"sha256:{row.relative_path}")
    if manifest_failures:
        raise RuntimeError("C4A integrity failure: " + ", ".join(manifest_failures))

    counts_path = source / "02_pseudobulk_counts_all_branches.npz"
    counts = sparse.load_npz(counts_path).tocsr()
    rows = pd.read_csv(source / "03_pseudobulk_row_metadata.csv")
    genes = pd.read_csv(source / "04_gene_universe.csv.gz")
    support = pd.read_csv(source / "05_compartment_support_audit.csv")
    primary = pd.read_csv(source / "06_primary_bconv_model_matrix.csv")
    validation = pd.read_csv(source / "07_validation_bconv_model_matrix.csv")
    flare = pd.read_csv(source / "08_flare_bconv_model_matrix.csv")

    if counts.shape != (len(rows), len(genes)):
        raise RuntimeError("Frozen C4A matrix dimensions do not match metadata")
    if not np.array_equal(rows["pseudobulk_row"].to_numpy(), np.arange(len(rows))):
        raise RuntimeError("Frozen pseudobulk row index is not contiguous")
    if counts.data.size and (counts.data.min() < 0 or not np.all(counts.data == np.floor(counts.data))):
        raise RuntimeError("Frozen matrix is not a non-negative integer matrix")

    primary_samples = set(primary["sample_uuid"].astype(str))
    primary_donors = set(primary["donor_id"].map(normalize_id))
    validation_nonoverlap = validation.loc[
        ~validation["sample_uuid"].astype(str).isin(primary_samples)
        & ~validation["donor_id"].map(normalize_id).isin(primary_donors)
    ].copy()

    definitions = [
        ("primary_base", primary, "all_hard_qc", ["intercept", "is_managed", "age_centered", "ethnicity_asian"], "is_managed"),
        ("primary_min20", build_threshold_design(support, 20), "all_hard_qc", ["intercept", "is_managed", "age_centered", "ethnicity_asian"], "is_managed"),
        ("primary_min100", build_threshold_design(support, 100), "all_hard_qc", ["intercept", "is_managed", "age_centered", "ethnicity_asian"], "is_managed"),
        ("primary_residual_risk_negative", primary.copy(), "residual_risk_negative", ["intercept", "is_managed", "age_centered", "ethnicity_asian"], "is_managed"),
        ("validation_full", validation, "all_hard_qc", ["intercept", "is_managed", "age_centered"], "is_managed"),
        ("validation_nonoverlap", validation_nonoverlap, "all_hard_qc", ["intercept", "is_managed", "age_centered"], "is_managed"),
        ("flare_full", flare, "all_hard_qc", ["intercept", "is_flare", "age_centered", "ethnicity_european"], "is_flare"),
    ]

    expected = {
        "primary_base": (89, 43, 46),
        "primary_min20": (94, 44, 50),
        "primary_min100": (87, 41, 46),
        "primary_residual_risk_negative": (89, 43, 46),
        "validation_full": (64, 21, 43),
        "validation_nonoverlap": (54, 21, 33),
        "flare_full": (34, 18, 16),
    }

    genes_path = matrix_dir / "gene_metadata.csv.gz"
    genes.to_csv(genes_path, index=False, compression="gzip", encoding="utf-8")
    row_lookup = rows.set_index(["branch", "compartment", "stratum_index"], drop=False)
    audits = []

    for name, design, branch, design_columns, effect_column in definitions:
        design = design.copy()
        design["stratum_index"] = design["stratum_index"].astype(int)
        keys = [(branch, "B_CONV", int(index)) for index in design["stratum_index"]]
        try:
            selected = row_lookup.loc[keys].reset_index(drop=True)
        except KeyError as exc:
            raise RuntimeError(f"Missing frozen pseudobulk row for {name}: {exc}") from exc
        if selected["stratum_id"].astype(str).tolist() != design["stratum_id"].astype(str).tolist():
            raise RuntimeError(f"Stratum order mismatch for {name}")
        selected_rows = selected["pseudobulk_row"].to_numpy(dtype=int)
        exported = counts[selected_rows, :].transpose().tocsr()

        n_expected, reference_expected, exposed_expected = expected[name]
        exposed = int(design[effect_column].sum())
        if (len(design), len(design) - exposed, exposed) != (
            n_expected,
            reference_expected,
            exposed_expected,
        ):
            raise RuntimeError(f"Frozen group-size mismatch for {name}")
        rank = int(np.linalg.matrix_rank(design[design_columns].to_numpy(dtype=float)))
        if rank != len(design_columns):
            raise RuntimeError(f"Rank-deficient export design for {name}: {rank}/{len(design_columns)}")

        sample_metadata = design.copy()
        sample_metadata.insert(0, "matrix_col", np.arange(1, len(design) + 1, dtype=int))
        sample_metadata["matrix_pseudobulk_row"] = selected_rows
        sample_metadata["matrix_branch"] = branch
        sample_metadata["matrix_library_size_umi"] = np.asarray(exported.sum(axis=0)).ravel().astype(np.int64)
        if not np.array_equal(
            sample_metadata["matrix_library_size_umi"].to_numpy(dtype=np.int64),
            selected["library_size_umi"].to_numpy(dtype=np.int64),
        ):
            raise RuntimeError(f"Column-sum conservation failed for {name}")

        matrix_path = matrix_dir / f"{name}_counts.mtx.gz"
        with gzip.open(matrix_path, "wb", compresslevel=6) as handle:
            mmwrite(handle, exported, field="integer", symmetry="general")
        sample_path = matrix_dir / f"{name}_samples.csv"
        sample_metadata.to_csv(sample_path, index=False, encoding="utf-8-sig")
        gene_sums = np.asarray(exported.sum(axis=1)).ravel().astype(np.int64)
        gene_sums_path = matrix_dir / f"{name}_gene_sums.csv.gz"
        pd.DataFrame({"ensembl_id": genes["ensembl_id"], "count_sum": gene_sums}).to_csv(
            gene_sums_path, index=False, compression="gzip", encoding="utf-8"
        )

        audits.append(
            {
                "analysis_name": name,
                "analysis_id": str(design["analysis_id"].iloc[0]),
                "branch": branch,
                "effect_column": effect_column,
                "design_columns": design_columns,
                "n_genes": int(exported.shape[0]),
                "n_samples": int(exported.shape[1]),
                "reference_n": int(len(design) - exposed),
                "exposed_n": exposed,
                "design_rank": rank,
                "total_umi": int(exported.sum()),
                "matrix_relative_path": str(matrix_path.relative_to(output)).replace("\\", "/"),
                "matrix_size_bytes": matrix_path.stat().st_size,
                "matrix_sha256": sha256(matrix_path),
                "sample_relative_path": str(sample_path.relative_to(output)).replace("\\", "/"),
                "sample_size_bytes": sample_path.stat().st_size,
                "sample_sha256": sha256(sample_path),
                "gene_sums_relative_path": str(gene_sums_path.relative_to(output)).replace("\\", "/"),
                "gene_sums_size_bytes": gene_sums_path.stat().st_size,
                "gene_sums_sha256": sha256(gene_sums_path),
                "column_sums_conserved": True,
                "integer_nonnegative": True,
            }
        )

    audit = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_C4B_FROZEN_MATRIX_EXPORT",
        "effect_estimates_inspected": False,
        "source_c4a_decision": EXPECTED_C4A_STATUS,
        "source_counts_sha256": sha256(counts_path),
        "source_manifest_verified": True,
        "gene_metadata_relative_path": str(genes_path.relative_to(output)).replace("\\", "/"),
        "gene_metadata_sha256": sha256(genes_path),
        "analyses": audits,
    }
    (output / "03_MATRIX_EXPORT_AUDIT.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    lines = [
        "# Gate C4B frozen matrix export audit",
        "",
        "- Status: `PASS_C4B_FROZEN_MATRIX_EXPORT`",
        "- Disease-effect estimates inspected: **no**",
        "- C4A integrity manifest: **verified**",
        f"- Frozen source-count SHA256: `{audit['source_counts_sha256']}`",
        "",
        "| Analysis | Branch | Genes | Samples | Reference | Exposed | UMI | Rank |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in audits:
        lines.append(
            f"| {item['analysis_name']} | {item['branch']} | {item['n_genes']:,} | "
            f"{item['n_samples']} | {item['reference_n']} | {item['exposed_n']} | "
            f"{item['total_umi']:,} | {item['design_rank']}/{len(item['design_columns'])} |"
        )
    lines.extend(
        [
            "",
            "All matrices are genes-by-samples sparse integer Matrix Market exports. "
            "Column sums were independently compared with frozen C4A pseudobulk libraries.",
        ]
    )
    (output / "03_MATRIX_EXPORT_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
