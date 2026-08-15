#!/usr/bin/env python3
"""Gate C5B-01: export frozen GSE135779 matrices without fitting effects."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
from pathlib import Path


EXPECTED_C5A_DECISION = "PASS_GATE_C5A_TO_FROZEN_EXTERNAL_EFFECT_MODELING"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_text_lf(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_csv_lf(frame, path: Path, **kwargs) -> None:
    kwargs.setdefault("index", False)
    kwargs.setdefault("lineterminator", "\n")
    frame.to_csv(path, **kwargs)


def safe_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-c5a-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    import numpy as np
    import pandas as pd
    from scipy import sparse
    from scipy.io import mmwrite

    source = Path(args.gate_c5a_dir).resolve()
    output = Path(args.output_dir).resolve()
    matrix_dir = output / "02_matrix_exports"
    matrix_dir.mkdir(parents=True, exist_ok=True)

    decision = json.loads(
        (source / "17_GATE_C5A_ADVISOR_DECISION.json").read_text(encoding="utf-8")
    )
    if decision.get("decision") != EXPECTED_C5A_DECISION:
        raise RuntimeError(f"Gate C5A is not authorized: {decision.get('decision')}")
    if not decision.get("external_effect_unlock_authorized"):
        raise RuntimeError("Gate C5A does not authorize external-effect modeling")
    if decision.get("external_disease_effects_inspected"):
        raise RuntimeError("Gate C5A pre-effect contract is inconsistent")

    manifest = pd.read_csv(source / "19_gate_c5a_integrity_manifest.csv")
    failures = []
    for row in manifest.itertuples(index=False):
        path = source / str(row.relative_path)
        if not path.is_file():
            failures.append(f"missing:{row.relative_path}")
        elif path.stat().st_size != int(row.size_bytes):
            failures.append(f"size:{row.relative_path}")
        elif sha256(path) != str(row.sha256).upper():
            failures.append(f"sha256:{row.relative_path}")
    if failures:
        raise RuntimeError("C5A integrity failure: " + ", ".join(failures))

    counts_path = source / "07_EXTERNAL_PSEUDOBULK_COUNTS.npz"
    counts = sparse.load_npz(counts_path).tocsr()
    rows = pd.read_csv(source / "08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv")
    genes = pd.read_csv(source / "09_EXTERNAL_GENE_UNIVERSE.csv.gz")
    combined = pd.read_csv(source / "12_COMBINED_MIN50_MODEL_MATRIX.csv")
    childhood = pd.read_csv(source / "13_CHILDHOOD_MIN50_MODEL_MATRIX.csv")
    adult = pd.read_csv(source / "14_ADULT_MIN50_MODEL_MATRIX.csv")
    thresholds = pd.read_csv(source / "15_THRESHOLD_SENSITIVITY_MODEL_MATRICES.csv")

    if counts.shape != (len(rows), len(genes)):
        raise RuntimeError("C5A pseudobulk dimensions do not match metadata")
    if not np.array_equal(rows["pseudobulk_row"].to_numpy(), np.arange(len(rows))):
        raise RuntimeError("C5A pseudobulk row index is not contiguous")
    if counts.data.size and (
        counts.data.min() < 0 or not np.all(counts.data == np.floor(counts.data))
    ):
        raise RuntimeError("C5A matrix is not non-negative integer counts")
    if genes["ensembl_id"].duplicated().any():
        raise RuntimeError("C5A Ensembl key is not unique")

    min20 = thresholds.loc[
        thresholds["analysis_name"].eq("C5B_GSE135779_COMBINED_MIN20")
    ].copy()
    min100 = thresholds.loc[
        thresholds["analysis_name"].eq("C5B_GSE135779_COMBINED_MIN100")
    ].copy()
    definitions = [
        ("childhood_min50", childhood, ["intercept", "is_sle"], "primary"),
        ("combined_min50", combined, ["intercept", "is_sle", "is_adult"], "combined"),
        ("adult_min50", adult, ["intercept", "is_sle"], "secondary"),
        ("combined_min20", min20, ["intercept", "is_sle", "is_adult"], "threshold"),
        ("combined_min100", min100, ["intercept", "is_sle", "is_adult"], "threshold"),
    ]
    expected = {
        "childhood_min50": (43, 11, 32),
        "combined_min50": (54, 16, 38),
        "adult_min50": (11, 5, 6),
        "combined_min20": (56, 16, 40),
        "combined_min100": (51, 16, 35),
    }

    genes_path = matrix_dir / "gene_metadata.csv.gz"
    write_csv_lf(genes, genes_path, compression="gzip")
    compartment_rows = rows.loc[
        rows["representation"].eq("compartment")
        & rows["frozen_compartment"].eq("B_CONV_ANALOG")
    ].set_index("sample_id", drop=False)
    label_rows = rows.loc[
        rows["representation"].eq("source_label")
        & rows["frozen_compartment"].eq("B_CONV_ANALOG")
    ].set_index(["sample_id", "source_label"], drop=False)

    def write_export(name, design, matrix, selected, design_columns, role, extra=None):
        n_expected, hc_expected, sle_expected = expected.get(name, (len(design), None, None))
        n_sle = int(design["is_sle"].sum())
        n_hc = len(design) - n_sle
        if len(design) != n_expected:
            raise RuntimeError(f"Sample-size mismatch for {name}")
        if hc_expected is not None and (n_hc, n_sle) != (hc_expected, sle_expected):
            raise RuntimeError(f"Group-size mismatch for {name}: {(n_hc, n_sle)}")
        rank = int(np.linalg.matrix_rank(design[design_columns].to_numpy(dtype=float)))
        if rank != len(design_columns):
            raise RuntimeError(f"Rank-deficient design for {name}: {rank}/{len(design_columns)}")
        exported = matrix.transpose().tocsr()
        sample_metadata = design.copy().reset_index(drop=True)
        sample_metadata.insert(0, "matrix_col", np.arange(1, len(design) + 1))
        sample_metadata["matrix_pseudobulk_row"] = selected["pseudobulk_row"].to_numpy(dtype=int)
        sample_metadata["matrix_library_size_umi"] = np.asarray(exported.sum(axis=0)).ravel().astype(np.int64)
        if extra:
            for key, values in extra.items():
                sample_metadata[key] = values
        if "remaining_library_size_umi" in sample_metadata:
            expected_libraries = sample_metadata["remaining_library_size_umi"].to_numpy(dtype=np.int64)
        else:
            expected_libraries = selected["library_size_umi"].to_numpy(dtype=np.int64)
        if not np.array_equal(
            sample_metadata["matrix_library_size_umi"].to_numpy(dtype=np.int64),
            expected_libraries,
        ):
            raise RuntimeError(f"Column-sum conservation failed for {name}")

        matrix_path = matrix_dir / f"{name}_counts.mtx.gz"
        with gzip.open(matrix_path, "wb", compresslevel=6) as handle:
            mmwrite(handle, exported, field="integer", symmetry="general")
        sample_path = matrix_dir / f"{name}_samples.csv"
        write_csv_lf(sample_metadata, sample_path)
        gene_sums_path = matrix_dir / f"{name}_gene_sums.csv.gz"
        gene_sums = np.asarray(exported.sum(axis=1)).ravel().astype(np.int64)
        write_csv_lf(
            pd.DataFrame({"ensembl_id": genes["ensembl_id"], "count_sum": gene_sums}),
            gene_sums_path,
            compression="gzip",
        )
        return {
            "analysis_name": name,
            "analysis_id": str(design["analysis_name"].iloc[0]),
            "analysis_role": role,
            "effect_column": "is_sle",
            "design_columns": design_columns,
            "n_genes": int(exported.shape[0]),
            "n_samples": int(exported.shape[1]),
            "reference_n": n_hc,
            "exposed_n": n_sle,
            "design_rank": rank,
            "total_umi": int(exported.sum()),
            "minimum_cells_after_omission": int(sample_metadata["remaining_bconv_cells"].min())
            if "remaining_bconv_cells" in sample_metadata
            else None,
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

    audits = []
    exported_designs = {}
    for name, design, design_columns, role in definitions:
        design = design.copy().reset_index(drop=True)
        selected = compartment_rows.loc[design["sample_id"].astype(str)].reset_index(drop=True)
        if selected["sample_id"].astype(str).tolist() != design["sample_id"].astype(str).tolist():
            raise RuntimeError(f"Sample order mismatch for {name}")
        selected_indices = selected["pseudobulk_row"].to_numpy(dtype=int)
        matrix = counts[selected_indices, :]
        audits.append(write_export(name, design, matrix, selected, design_columns, role))
        exported_designs[name] = (design, selected, matrix, design_columns)

    primary_design, primary_selected, primary_matrix, primary_columns = exported_designs[
        "childhood_min50"
    ]
    source_labels = sorted(label_rows.index.get_level_values("source_label").unique())
    if source_labels != [f"B-caSC{index}" for index in range(8)]:
        raise RuntimeError(f"Unexpected B source-label dictionary: {source_labels}")
    source_audits = []
    for label in source_labels:
        selected_label = label_rows.loc[
            [(sample_id, label) for sample_id in primary_design["sample_id"].astype(str)]
        ].reset_index(drop=True)
        label_matrix = counts[selected_label["pseudobulk_row"].to_numpy(dtype=int), :]
        remaining = primary_matrix - label_matrix
        remaining.eliminate_zeros()
        if remaining.data.size and remaining.data.min() < 0:
            raise RuntimeError(f"Negative count after omitting {label}")
        remaining_cells = (
            primary_selected["cell_count"].to_numpy(dtype=int)
            - selected_label["cell_count"].to_numpy(dtype=int)
        )
        remaining_umi = (
            primary_selected["library_size_umi"].to_numpy(dtype=np.int64)
            - selected_label["library_size_umi"].to_numpy(dtype=np.int64)
        )
        if (remaining_cells <= 0).any() or (remaining_umi <= 0).any():
            raise RuntimeError(f"Source-label omission removes an entire sample: {label}")
        name = f"childhood_min50_without_{safe_name(label)}"
        item = write_export(
            name,
            primary_design,
            remaining,
            primary_selected,
            primary_columns,
            "source_label_sensitivity",
            extra={
                "omitted_source_label": [label] * len(primary_design),
                "omitted_source_label_cells": selected_label["cell_count"].to_numpy(dtype=int),
                "remaining_bconv_cells": remaining_cells,
                "remaining_library_size_umi": remaining_umi,
            },
        )
        item["omitted_source_label"] = label
        item["sample_set_policy"] = "retain the frozen 43 childhood_min50 donors"
        source_audits.append(item)

    audit = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_C5B_FROZEN_MATRIX_EXPORT",
        "real_effect_estimates_inspected": False,
        "source_c5a_decision": EXPECTED_C5A_DECISION,
        "source_counts_sha256": sha256(counts_path),
        "source_manifest_verified": True,
        "gene_metadata_relative_path": str(genes_path.relative_to(output)).replace("\\", "/"),
        "gene_metadata_sha256": sha256(genes_path),
        "analyses": audits,
        "source_label_sensitivities": source_audits,
    }
    write_text_lf(output / "03_MATRIX_EXPORT_AUDIT.json", json.dumps(audit, indent=2))
    lines = [
        "# Gate C5B frozen matrix export audit",
        "",
        "- Status: `PASS_C5B_FROZEN_MATRIX_EXPORT`",
        "- External disease effects inspected: **no**",
        "- Gate C5A integrity manifest: **verified**",
        f"- Frozen source-count SHA256: `{audit['source_counts_sha256']}`",
        "",
        "| Analysis | Role | Genes | Samples | HC | SLE | UMI | Rank |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in audits:
        lines.append(
            f"| {item['analysis_name']} | {item['analysis_role']} | {item['n_genes']:,} | "
            f"{item['n_samples']} | {item['reference_n']} | {item['exposed_n']} | "
            f"{item['total_umi']:,} | {item['design_rank']}/{len(item['design_columns'])} |"
        )
    lines.extend(
        [
            "",
            "Eight source-label omission matrices retain the same 43 childhood donors. "
            "Only the selected B-caSC count contribution is removed; samples are not reselected.",
        ]
    )
    write_text_lf(output / "03_MATRIX_EXPORT_AUDIT.md", "\n".join(lines) + "\n")
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
