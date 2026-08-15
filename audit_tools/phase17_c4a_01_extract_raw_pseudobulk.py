#!/usr/bin/env python3
"""Gate C4A-01: aggregate audited raw counts and freeze pre-effect designs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path


EXPECTED_RAW_SHA256 = "DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5"
EXPECTED_C3_STATUS = "PASS_GATE_C3_METADATA_JOIN_AND_MODEL_DESIGN_FREEZE"
EXPECTED_C3A_STATUS = "NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM"
EXPECTED_C2B1_DECISION = "PASS_TO_C2B2_WITH_DUAL_BRANCH"
BRANCHES = ("all_hard_qc", "residual_risk_negative")
COMPARTMENTS = ("B_CONV", "B_ASC")

PROGRAMS = [
    {
        "program_id": "NAIVE_TO_MEMORY_AXIS",
        "program_label": "Naive-to-memory axis",
        "analysis_family": "primary_confirmatory",
        "publication_role": "continuous B_CONV program; no hard subtype",
        "positive": ["CD27", "TNFRSF13B", "AIM2", "BANK1", "CD40", "LTB", "GPR183"],
        "negative": ["TCL1A", "IL4R", "FCER2", "CCR7", "SELL", "CXCR4", "VPREB3"],
        "provenance": "disease-blind C2A anchors plus pre-existing citation audit controls",
    },
    {
        "program_id": "ATYPICAL_LOW_NAIVE_AXIS",
        "program_label": "Atypical/ABC with low-naive context",
        "analysis_family": "primary_confirmatory",
        "publication_role": "continuous B_CONV program; no ABC hard identity",
        "positive": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
        "negative": ["CR2", "FCER2", "TCL1A"],
        "provenance": "pre-existing literature-signature and citation audit",
    },
    {
        "program_id": "APC_HLA",
        "program_label": "Antigen-presentation program",
        "analysis_family": "primary_confirmatory",
        "publication_role": "continuous B_CONV program",
        "positive": [
            "CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1",
            "HLA-DQA1", "HLA-DQB1", "B2M", "CIITA", "CD86",
        ],
        "negative": [],
        "provenance": "pre-existing literature-signature and citation audit",
    },
    {
        "program_id": "IFN_ISG",
        "program_label": "Type I interferon response",
        "analysis_family": "primary_confirmatory",
        "publication_role": "continuous B_CONV program",
        "positive": [
            "ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2",
            "OAS1", "OAS2", "IFI44L", "IFI6", "LY6E", "IRF7",
        ],
        "negative": [],
        "provenance": "Perez context plus pre-existing citation audit",
    },
    {
        "program_id": "ACTIVATION_STRESS",
        "program_label": "Activation/immediate-early response",
        "analysis_family": "secondary_contextual",
        "publication_role": "context and technical-stress sensitivity",
        "positive": ["CD69", "CD83", "CD86", "NFKBIA", "JUNB", "FOS", "FOSB", "DUSP1", "NR4A2"],
        "negative": [],
        "provenance": "pre-existing disease-blind marker program",
    },
    {
        "program_id": "TLR7_INNATE",
        "program_label": "TLR7/innate-sensing context",
        "analysis_family": "secondary_contextual",
        "publication_role": "mechanistic context only",
        "positive": ["TLR7", "MYD88", "IRAK1", "IRF7", "NFKB1", "RELA", "IFIH1", "FTO", "ATP6V1G1"],
        "negative": [],
        "provenance": "pre-existing citation audit; boundary context",
    },
    {
        "program_id": "PLATELET_AMBIENT_QC",
        "program_label": "Platelet/ambient overlay",
        "analysis_family": "qc_only",
        "publication_role": "sensitivity/QC only; never a B-cell identity",
        "positive": ["PPBP", "PF4", "NRGN", "TUBB1", "RGS18", "CAVIN2", "GNG11", "SPARC", "MYL9", "CLU"],
        "negative": [],
        "provenance": "disease-blind dataset-specific ranked-marker QC",
    },
    {
        "program_id": "ASC_UPR_IDENTITY_QC",
        "program_label": "ASC/UPR identity control",
        "analysis_family": "identity_qc_only",
        "publication_role": "B_ASC identity QC; not a new outcome-informed state",
        "positive": ["MZB1", "XBP1", "PRDM1", "JCHAIN", "SDC1", "IRF4", "TNFRSF17", "DERL3", "FKBP11", "HSP90B1"],
        "negative": [],
        "provenance": "C2B4 required ASC panel plus pre-existing control signature",
    },
    {
        "program_id": "PAN_B_IDENTITY_QC",
        "program_label": "Pan-B identity control",
        "analysis_family": "identity_qc_only",
        "publication_role": "B-lineage extraction QC only",
        "positive": ["MS4A1", "CD79A", "CD79B", "CD74", "CD19"],
        "negative": [],
        "provenance": "pre-existing B-lineage extraction QC",
    },
]


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_manifest(root: Path, filename: str):
    import pandas as pd

    manifest = pd.read_csv(root / filename)
    failures = []
    for row in manifest.itertuples(index=False):
        path = root / str(row.relative_path)
        if not path.is_file():
            failures.append({"relative_path": row.relative_path, "issue": "missing"})
        elif path.stat().st_size != int(row.size_bytes):
            failures.append({"relative_path": row.relative_path, "issue": "size"})
        elif hash_file(path) != str(row.sha256).upper():
            failures.append({"relative_path": row.relative_path, "issue": "sha256"})
    return manifest, failures


def bool_series(series):
    import pandas as pd

    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def first(series):
    return series.iloc[0]


def build_design(support, analysis_id, cohort, states, minimum_cells=50, validation=False):
    import numpy as np

    work = support.loc[
        (support["branch"] == "all_hard_qc")
        & (support["Processing_Cohort"] == float(cohort))
        & support["disease_state"].isin(states)
        & (support["bconv_cells"] >= minimum_cells)
    ].copy()
    if validation:
        work = work.loc[
            (work["sex"].str.lower() == "female")
            & (work["ethnicity"] == "European American")
        ].copy()
    work.insert(0, "analysis_id", analysis_id)
    work["intercept"] = 1.0
    work["age_centered"] = work["age_years"] - work["age_years"].mean()
    work["ethnicity_asian"] = (work["ethnicity"] == "Asian").astype(int)
    work["ethnicity_european"] = (work["ethnicity"] == "European American").astype(int)
    work["is_managed"] = (work["disease_state"] == "managed").astype(int)
    work["is_flare"] = (work["disease_state"] == "flare").astype(int)
    return work.sort_values(["disease_state", "sample_uuid"]).reset_index(drop=True)


def design_rank(table, columns):
    import numpy as np

    return int(np.linalg.matrix_rank(table[list(columns)].to_numpy(dtype=float)))


def atomic_save_npz(path, matrix):
    from scipy import sparse

    temporary = path.with_name(path.stem + ".tmp.npz")
    sparse.save_npz(temporary, matrix, compressed=True)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-h5ad", required=True)
    parser.add_argument("--gate-c2b1-dir", required=True)
    parser.add_argument("--gate-c3-dir", required=True)
    parser.add_argument("--gate-c3a-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--chunk-cells", type=int, default=5000)
    args = parser.parse_args()

    import anndata as ad
    import numpy as np
    import pandas as pd
    from scipy import sparse

    raw_path = Path(args.raw_h5ad).resolve()
    gate_c2b1 = Path(args.gate_c2b1_dir).resolve()
    gate_c3 = Path(args.gate_c3_dir).resolve()
    gate_c3a = Path(args.gate_c3a_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = output / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    c2b1_decision = json.loads(
        (gate_c2b1 / "17_GATE_C2B1_DECISION.json").read_text(encoding="utf-8")
    )
    c3_status = json.loads((gate_c3 / "00_GATE_C3_RUN_STATUS.json").read_text(encoding="utf-8"))
    c3a_status = json.loads((gate_c3a / "00_GATE_C3A_RUN_STATUS.json").read_text(encoding="utf-8"))
    c3_manifest, c3_failures = verify_manifest(gate_c3, "16_gate_c3_integrity_manifest.csv")
    c3a_manifest, c3a_failures = verify_manifest(gate_c3a, "10_gate_c3a_integrity_manifest.csv")
    if c2b1_decision.get("decision") != EXPECTED_C2B1_DECISION:
        raise RuntimeError("Gate C2B1 dual-branch decision is not valid")
    if c3_status.get("status") != EXPECTED_C3_STATUS:
        raise RuntimeError("Gate C3 model design is not frozen")
    if c3a_status.get("status") != EXPECTED_C3A_STATUS:
        raise RuntimeError("Gate C3A status is not the expected composition no-go")
    if c3a_status.get("continuous_program_analysis_authorized") is not True:
        raise RuntimeError("Gate C3A has not authorized continuous-program analysis")
    if c3_failures or c3a_failures:
        raise RuntimeError(f"Upstream integrity failures: C3={c3_failures}; C3A={c3a_failures}")

    raw_sha256 = hash_file(raw_path)
    if raw_sha256 != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"Raw-count H5AD checksum mismatch: {raw_sha256}")

    cell = pd.read_csv(gate_c3 / "01_unlocked_cell_metadata.csv.gz", low_memory=False)
    required_cell_columns = {
        "cell_id", "sample_uuid", "donor_id", "Processing_Cohort", "disease",
        "disease_state", "sex", "self_reported_ethnicity", "age_years",
        "source_r04_cluster", "residual_doublet_auto_call",
        "hard_naive_memory_label_authorized",
    }
    missing_columns = sorted(required_cell_columns - set(cell.columns))
    if missing_columns:
        raise RuntimeError(f"Gate C3 cell metadata columns missing: {missing_columns}")
    cell["cell_id"] = cell["cell_id"].astype(str)
    cell["sample_uuid"] = cell["sample_uuid"].astype(str)
    cell["donor_id"] = cell["donor_id"].astype(str)
    cell["Processing_Cohort"] = pd.to_numeric(cell["Processing_Cohort"])
    cell["age_years"] = pd.to_numeric(cell["age_years"])
    cell["source_r04_cluster"] = pd.to_numeric(cell["source_r04_cluster"]).astype(int)
    cell["residual_doublet_auto_call"] = bool_series(cell["residual_doublet_auto_call"])
    if bool_series(cell["hard_naive_memory_label_authorized"]).any():
        raise RuntimeError("Hard naive-memory labels were unexpectedly authorized")

    raw = ad.read_h5ad(raw_path, backed="r")
    raw_ids = raw.obs_names.astype(str)
    exact_order = bool(np.array_equal(raw_ids.to_numpy(), cell["cell_id"].to_numpy()))
    exact_set = bool(
        len(raw_ids) == len(cell)
        and raw_ids.is_unique
        and cell["cell_id"].is_unique
        and set(raw_ids) == set(cell["cell_id"])
    )
    if not exact_order or not exact_set:
        raise RuntimeError("Raw-count H5AD cell IDs do not exactly match Gate C3 in order and set")
    if raw.shape != (len(cell), 30172):
        raise RuntimeError(f"Unexpected raw-count shape: {raw.shape}")

    raw_key_mismatches = {}
    for column in ("sample_uuid", "donor_id", "Processing_Cohort"):
        left = raw.obs[column].astype(str).to_numpy()
        right = cell[column].astype(str).to_numpy()
        raw_key_mismatches[column] = int((left != right).sum())
    if any(raw_key_mismatches.values()):
        raise RuntimeError(f"Raw/Gate C3 key mismatches: {raw_key_mismatches}")

    invariant_fields = [
        "donor_id", "disease", "disease_state", "sex", "self_reported_ethnicity", "age_years"
    ]
    conflicts = (
        cell.groupby(["sample_uuid", "Processing_Cohort"], observed=True)[invariant_fields]
        .nunique(dropna=False)
        .gt(1)
    )
    if int(conflicts.sum().sum()) != 0:
        raise RuntimeError("Sample-cohort metadata invariants failed")
    strata = (
        cell.groupby(["sample_uuid", "Processing_Cohort"], observed=True, sort=True)
        .agg(
            donor_id=("donor_id", first),
            disease=("disease", first),
            disease_state=("disease_state", first),
            sex=("sex", first),
            ethnicity=("self_reported_ethnicity", first),
            age_years=("age_years", first),
        )
        .reset_index()
        .sort_values(["Processing_Cohort", "sample_uuid"])
        .reset_index(drop=True)
    )
    strata.insert(0, "stratum_index", np.arange(len(strata), dtype=int))
    strata.insert(
        1,
        "stratum_id",
        strata["sample_uuid"] + "__C" + strata["Processing_Cohort"].astype(int).astype(str),
    )
    stratum_lookup = dict(zip(strata["stratum_id"], strata["stratum_index"]))
    cell_stratum_id = (
        cell["sample_uuid"] + "__C" + cell["Processing_Cohort"].astype(int).astype(str)
    )
    stratum_index = cell_stratum_id.map(stratum_lookup).to_numpy(dtype=int)
    compartment_index = (cell["source_r04_cluster"].to_numpy() == 3).astype(int)
    if set(cell["source_r04_cluster"].unique()) != {0, 1, 2, 3, 4}:
        raise RuntimeError("Unexpected source r0.4 cluster set")

    n_strata = len(strata)
    rows = []
    for branch_index, branch in enumerate(BRANCHES):
        for compartment_value, compartment in enumerate(COMPARTMENTS):
            for row in strata.itertuples(index=False):
                rows.append(
                    {
                        "pseudobulk_row": branch_index * len(COMPARTMENTS) * n_strata
                        + compartment_value * n_strata
                        + int(row.stratum_index),
                        "branch": branch,
                        "compartment": compartment,
                        **row._asdict(),
                    }
                )
    row_metadata = pd.DataFrame(rows).sort_values("pseudobulk_row").reset_index(drop=True)
    n_pb_rows = len(row_metadata)
    primary_row = compartment_index * n_strata + stratum_index
    sensitivity_row = len(COMPARTMENTS) * n_strata + primary_row
    include_sensitivity = ~cell["residual_doublet_auto_call"].to_numpy(dtype=bool)
    expected_cell_counts = np.bincount(primary_row, minlength=n_pb_rows)
    expected_cell_counts += np.bincount(
        sensitivity_row[include_sensitivity], minlength=n_pb_rows
    )

    var = raw.var.copy().reset_index().rename(columns={raw.var.index.name or "index": "ensembl_id"})
    if "ensembl_id" not in var.columns:
        var = var.rename(columns={var.columns[0]: "ensembl_id"})
    var["ensembl_id"] = var["ensembl_id"].astype(str)
    var["gene_id"] = var["gene_id"].astype(str)
    var["feature_name"] = var["feature_name"].astype(str)
    if not var["ensembl_id"].is_unique:
        raise RuntimeError("Raw feature Ensembl IDs are not unique")

    contract_payload = {
        "raw_sha256": raw_sha256,
        "cell_metadata_sha256": hash_file(gate_c3 / "01_unlocked_cell_metadata.csv.gz"),
        "shape": list(raw.shape),
        "chunk_cells": args.chunk_cells,
        "branches": list(BRANCHES),
        "compartments": list(COMPARTMENTS),
        "n_pseudobulk_rows": n_pb_rows,
        "row_mapping": "branch-major, compartment-major, stable sample-cohort stratum",
    }
    contract_hash = hashlib.sha256(
        json.dumps(contract_payload, sort_keys=True).encode("utf-8")
    ).hexdigest().upper()
    checkpoint_contract_path = checkpoint_dir / "checkpoint_contract.json"
    if checkpoint_contract_path.exists():
        existing = json.loads(checkpoint_contract_path.read_text(encoding="utf-8"))
        if existing.get("contract_hash") != contract_hash:
            raise RuntimeError("Existing C4A checkpoints belong to another extraction contract")
    else:
        checkpoint_contract_path.write_text(
            json.dumps({**contract_payload, "contract_hash": contract_hash}, indent=2),
            encoding="utf-8",
        )

    checkpoint_paths = []
    full_nonzero_values = 0
    full_raw_umi_total = 0
    minimum_nonzero = None
    maximum_nonzero = None
    for start in range(0, raw.n_obs, args.chunk_cells):
        end = min(start + args.chunk_cells, raw.n_obs)
        checkpoint = checkpoint_dir / f"chunk_{start:07d}_{end:07d}.npz"
        checkpoint_json = checkpoint.with_suffix(".json")
        if checkpoint.exists() and checkpoint_json.exists():
            chunk_pb = sparse.load_npz(checkpoint)
            metadata = json.loads(checkpoint_json.read_text(encoding="utf-8"))
            if (
                metadata.get("contract_hash") != contract_hash
                or chunk_pb.shape != (n_pb_rows, raw.n_vars)
            ):
                raise RuntimeError(f"Invalid checkpoint: {checkpoint}")
        else:
            chunk = raw.X[start:end, :]
            chunk = chunk.tocsr() if sparse.issparse(chunk) else sparse.csr_matrix(chunk)
            if len(chunk.data):
                if np.any(chunk.data < 0) or np.any(chunk.data != np.floor(chunk.data)):
                    raise RuntimeError(f"Non-integer or negative raw count in rows {start}:{end}")
                chunk.data = chunk.data.astype(np.int64)
            local_size = end - start
            local_columns = np.arange(local_size, dtype=int)
            assignment_rows = [primary_row[start:end]]
            assignment_columns = [local_columns]
            sensitivity_local = include_sensitivity[start:end]
            assignment_rows.append(sensitivity_row[start:end][sensitivity_local])
            assignment_columns.append(local_columns[sensitivity_local])
            assignment = sparse.csr_matrix(
                (
                    np.ones(sum(len(values) for values in assignment_rows), dtype=np.int64),
                    (np.concatenate(assignment_rows), np.concatenate(assignment_columns)),
                ),
                shape=(n_pb_rows, local_size),
            )
            chunk_pb = (assignment @ chunk).tocsr()
            chunk_pb.sum_duplicates()
            atomic_save_npz(checkpoint, chunk_pb)
            metadata = {
                "contract_hash": contract_hash,
                "start": start,
                "end": end,
                "source_nnz": int(chunk.nnz),
                "source_umi_total": int(chunk.sum()),
                "primary_branch_umi_total": int(
                    chunk_pb[: len(COMPARTMENTS) * n_strata, :].sum()
                ),
                "sensitivity_branch_umi_total": int(
                    chunk_pb[len(COMPARTMENTS) * n_strata :, :].sum()
                ),
                "minimum_nonzero": int(chunk.data.min()) if chunk.nnz else None,
                "maximum_nonzero": int(chunk.data.max()) if chunk.nnz else None,
            }
            temporary_json = checkpoint_json.with_suffix(".tmp.json")
            temporary_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            os.replace(temporary_json, checkpoint_json)
        if metadata["source_umi_total"] != metadata["primary_branch_umi_total"]:
            raise RuntimeError(f"Count conservation failed in checkpoint {checkpoint.name}")
        full_nonzero_values += int(metadata["source_nnz"])
        full_raw_umi_total += int(metadata["source_umi_total"])
        if metadata.get("minimum_nonzero") is not None:
            minimum_nonzero = (
                int(metadata["minimum_nonzero"])
                if minimum_nonzero is None
                else min(minimum_nonzero, int(metadata["minimum_nonzero"]))
            )
            maximum_nonzero = (
                int(metadata["maximum_nonzero"])
                if maximum_nonzero is None
                else max(maximum_nonzero, int(metadata["maximum_nonzero"]))
            )
        checkpoint_paths.append(checkpoint)
        print(f"[C4A] raw-count chunk {len(checkpoint_paths)}/{(raw.n_obs + args.chunk_cells - 1) // args.chunk_cells}: cells {start:,}-{end:,}")

    aggregate = sparse.csr_matrix((n_pb_rows, raw.n_vars), dtype=np.int64)
    for checkpoint in checkpoint_paths:
        aggregate = aggregate + sparse.load_npz(checkpoint).astype(np.int64)
    aggregate.sum_duplicates()
    aggregate.eliminate_zeros()
    if np.any(aggregate.data < 0) or np.any(aggregate.data != np.floor(aggregate.data)):
        raise RuntimeError("Final pseudobulk matrix contains invalid counts")
    primary_rows_end = len(COMPARTMENTS) * n_strata
    primary_umi_total = int(aggregate[:primary_rows_end, :].sum())
    sensitivity_umi_total = int(aggregate[primary_rows_end:, :].sum())
    if primary_umi_total != full_raw_umi_total:
        raise RuntimeError("Final all-hard-QC pseudobulk counts do not conserve raw UMIs")
    count_path = output / "02_pseudobulk_counts_all_branches.npz"
    atomic_save_npz(count_path, aggregate)

    row_metadata["cell_count"] = expected_cell_counts
    row_metadata["library_size_umi"] = np.asarray(aggregate.sum(axis=1)).ravel().astype(np.int64)
    row_metadata["detected_genes"] = np.diff(aggregate.indptr).astype(int)
    row_metadata.to_csv(output / "03_pseudobulk_row_metadata.csv", index=False, encoding="utf-8-sig")

    symbols = var["feature_name"]
    var["is_mitochondrial"] = symbols.str.upper().str.startswith("MT-")
    var["is_ribosomal"] = symbols.str.upper().str.match(r"^RP[SL]")
    var["is_hemoglobin"] = symbols.str.upper().str.match(r"^HB[ABDEGQZ]")
    var["is_immunoglobulin"] = symbols.str.upper().str.match(r"^IG[HKL]")
    var.to_csv(output / "04_gene_universe.csv.gz", index=False, compression="gzip", encoding="utf-8")

    support = (
        row_metadata.pivot_table(
            index=[
                "branch", "stratum_index", "stratum_id", "sample_uuid", "Processing_Cohort",
                "donor_id", "disease", "disease_state", "sex", "ethnicity", "age_years",
            ],
            columns="compartment",
            values=["cell_count", "library_size_umi", "detected_genes"],
            aggfunc="first",
            fill_value=0,
        )
        .reset_index()
    )
    support.columns = [
        "_".join([str(item) for item in column if str(item)])
        if isinstance(column, tuple)
        else str(column)
        for column in support.columns
    ]
    support = support.rename(
        columns={
            "cell_count_B_CONV": "bconv_cells",
            "cell_count_B_ASC": "basc_cells",
            "library_size_umi_B_CONV": "bconv_library_size_umi",
            "library_size_umi_B_ASC": "basc_library_size_umi",
            "detected_genes_B_CONV": "bconv_detected_genes",
            "detected_genes_B_ASC": "basc_detected_genes",
        }
    )
    support.to_csv(output / "05_compartment_support_audit.csv", index=False, encoding="utf-8-sig")

    primary = build_design(
        support, "C4B_PRIMARY_C4_BCONV_MANAGED_VS_NORMAL", 4, ("na", "managed")
    )
    validation = build_design(
        support,
        "C4B_VALIDATION_C2_BCONV_EUROPEAN_FEMALE",
        2,
        ("na", "managed"),
        validation=True,
    )
    flare = build_design(
        support, "C4B_SECONDARY_C3_BCONV_FLARE_VS_NORMAL", 3, ("na", "flare")
    )
    primary_columns = ("intercept", "is_managed", "age_centered", "ethnicity_asian")
    validation_columns = ("intercept", "is_managed", "age_centered")
    flare_columns = ("intercept", "is_flare", "age_centered", "ethnicity_european")
    for table, columns, name in (
        (primary, primary_columns, "primary"),
        (validation, validation_columns, "validation"),
        (flare, flare_columns, "flare"),
    ):
        rank = design_rank(table, columns)
        if rank != len(columns):
            raise RuntimeError(f"Rank-deficient {name} B_CONV design: {rank}/{len(columns)}")
    primary.to_csv(output / "06_primary_bconv_model_matrix.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(output / "07_validation_bconv_model_matrix.csv", index=False, encoding="utf-8-sig")
    flare.to_csv(output / "08_flare_bconv_model_matrix.csv", index=False, encoding="utf-8-sig")

    primary_samples = set(primary["sample_uuid"])
    primary_donors = set(primary["donor_id"])
    overlap_rows = []
    for name, table, effect in (
        ("validation", validation, "is_managed"),
        ("flare", flare, "is_flare"),
    ):
        sample_overlap = table["sample_uuid"].isin(primary_samples)
        donor_overlap = table["donor_id"].isin(primary_donors)
        keep = ~sample_overlap & ~donor_overlap
        overlap_rows.append(
            {
                "analysis": name,
                "frozen_n": len(table),
                "shared_samples_with_primary": int(sample_overlap.sum()),
                "shared_donors_with_primary": int(donor_overlap.sum()),
                "nonoverlap_n": int(keep.sum()),
                "nonoverlap_reference_n": int((table.loc[keep, effect] == 0).sum()),
                "nonoverlap_exposed_n": int((table.loc[keep, effect] == 1).sum()),
            }
        )
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(output / "09_replication_nonoverlap_audit.csv", index=False, encoding="utf-8-sig")

    basc_rows = []
    analysis_filters = {
        "primary_c4": support.loc[
            (support["branch"] == "all_hard_qc")
            & (support["Processing_Cohort"] == 4)
            & support["disease_state"].isin(["na", "managed"])
        ],
        "validation_c2_european_female": support.loc[
            (support["branch"] == "all_hard_qc")
            & (support["Processing_Cohort"] == 2)
            & support["disease_state"].isin(["na", "managed"])
            & (support["sex"].str.lower() == "female")
            & (support["ethnicity"] == "European American")
        ],
        "flare_c3": support.loc[
            (support["branch"] == "all_hard_qc")
            & (support["Processing_Cohort"] == 3)
            & support["disease_state"].isin(["na", "flare"])
        ],
    }
    for analysis, table in analysis_filters.items():
        for threshold in (1, 5, 10, 20, 50):
            eligible = table.loc[table["basc_cells"] >= threshold]
            for state in sorted(table["disease_state"].unique()):
                basc_rows.append(
                    {
                        "analysis": analysis,
                        "minimum_basc_cells": threshold,
                        "disease_state": state,
                        "total_strata": int((table["disease_state"] == state).sum()),
                        "eligible_strata": int((eligible["disease_state"] == state).sum()),
                        "eligible_donors": int(
                            eligible.loc[eligible["disease_state"] == state, "donor_id"].nunique()
                        ),
                    }
                )
    basc_support = pd.DataFrame(basc_rows)
    basc_support.to_csv(output / "10_basc_pseudobulk_support.csv", index=False, encoding="utf-8-sig")

    dictionary_rows = []
    availability_rows = []
    symbol_to_ids = (
        var.groupby("feature_name", observed=True)["ensembl_id"]
        .agg(lambda values: "|".join(sorted(set(values.astype(str)))))
        .to_dict()
    )
    for program in PROGRAMS:
        ordinal = 0
        for sign, genes in ((1, program["positive"]), (-1, program["negative"])):
            for gene in genes:
                ordinal += 1
                dictionary_rows.append(
                    {
                        "program_id": program["program_id"],
                        "program_label": program["program_label"],
                        "analysis_family": program["analysis_family"],
                        "publication_role": program["publication_role"],
                        "sign": sign,
                        "gene_symbol": gene,
                        "ordinal": ordinal,
                        "provenance": program["provenance"],
                    }
                )
                ids = symbol_to_ids.get(gene, "")
                availability_rows.append(
                    {
                        "program_id": program["program_id"],
                        "analysis_family": program["analysis_family"],
                        "sign": sign,
                        "gene_symbol": gene,
                        "available": bool(ids),
                        "matched_ensembl_count": len(ids.split("|")) if ids else 0,
                        "matched_ensembl_ids": ids,
                        "duplicate_symbol_policy": "sum all matching Ensembl features before scoring",
                    }
                )
    dictionary = pd.DataFrame(dictionary_rows)
    availability = pd.DataFrame(availability_rows)
    dictionary.to_csv(output / "11_program_dictionary.csv", index=False, encoding="utf-8-sig")
    availability.to_csv(output / "12_program_gene_availability.csv", index=False, encoding="utf-8-sig")

    design_contract = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PRE_EFFECT_FROZEN",
        "effect_estimates_inspected": False,
        "raw_count_source": {
            "path_role": "Gate C2B1 all-hard-QC raw-count H5AD",
            "sha256": raw_sha256,
            "shape": list(raw.shape),
            "matrix": "X; non-negative integer raw counts",
            "cell_join": "exact cell ID; exact row order verified",
        },
        "branches": {
            "primary": "all_hard_qc",
            "sensitivity": "residual_risk_negative",
        },
        "identity": {
            "B_CONV": "source r0.4 clusters 0,1,2,4",
            "B_ASC": "source r0.4 cluster 3",
            "hard_naive_memory_authorized": False,
        },
        "bconv_minimum_cells": 50,
        "bconv_threshold_sensitivities": [20, 100],
        "primary": {
            "analysis_id": primary["analysis_id"].iloc[0],
            "n": len(primary),
            "counts": primary["disease_state"].value_counts().to_dict(),
            "fixed_effects": list(primary_columns[1:]),
            "rank": design_rank(primary, primary_columns),
        },
        "validation": {
            "analysis_id": validation["analysis_id"].iloc[0],
            "n": len(validation),
            "counts": validation["disease_state"].value_counts().to_dict(),
            "fixed_effects": list(validation_columns[1:]),
            "rank": design_rank(validation, validation_columns),
            "interpretation": "internal directional replication plus nonoverlap sensitivity",
        },
        "secondary_flare": {
            "analysis_id": flare["analysis_id"].iloc[0],
            "n": len(flare),
            "counts": flare["disease_state"].value_counts().to_dict(),
            "fixed_effects": list(flare_columns[1:]),
            "rank": design_rank(flare, flare_columns),
        },
        "program_score": {
            "input": "B_CONV pseudobulk raw counts",
            "normalization": "TMM logCPM from the frozen negative-binomial engine",
            "gene_scaling": "z-score each available gene across eligible strata within each frozen contrast",
            "formula": "mean positive-gene z scores minus mean negative-gene z scores",
            "duplicate_symbol_policy": "sum all matching Ensembl features before normalization",
            "minimum_gene_availability_per_sign": 0.8,
            "primary_multiplicity": "BH across four primary_confirmatory program coefficients",
        },
        "gene_level_pseudobulk": {
            "preferred_engine": "edgeR TMM robust quasi-likelihood",
            "filter": "filterByExpr frozen per contrast before coefficient inspection",
            "multiplicity": "genome-wide BH within contrast",
            "inferential_unit": "sample_uuid x Processing_Cohort B_CONV pseudobulk",
        },
        "prohibited": [
            "cell-level differential expression",
            "scaled source X for count modeling",
            "source_cell_index as a full-source row position",
            "hard naive-memory composition",
            "outcome-adaptive program membership",
            "B_ASC gene-level disease inference without support-gate authorization",
        ],
    }
    (output / "13_GATE_C4A_FREEZE_CONTRACT.json").write_text(
        json.dumps(design_contract, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    contract_lines = [
        "# Gate C4A pre-effect raw-count and program contract",
        "",
        "**Status:** `PRE_EFFECT_FROZEN`",
        "",
        f"- Raw counts: {raw.shape[0]:,} cells x {raw.shape[1]:,} Ensembl features",
        f"- Raw H5AD SHA256: `{raw_sha256}`",
        "- Exact Gate C3 cell-ID set and row order: verified",
        "- Primary branch: all hard-QC cells",
        "- Sensitivity branch: residual-risk automatic calls excluded",
        "- B_CONV minimum cells per sample-cohort pseudobulk: 50",
        f"- Primary B_CONV design: n={len(primary)}",
        f"- Internal validation B_CONV design: n={len(validation)}",
        f"- Secondary flare B_CONV design: n={len(flare)}",
        f"- Frozen programs: {len(PROGRAMS)}; primary multiplicity family: 4",
        "- Disease expression coefficients inspected: False",
        "",
        "## Binding restrictions",
        "",
    ]
    contract_lines.extend(f"- {item}" for item in design_contract["prohibited"])
    (output / "13_GATE_C4A_FREEZE_CONTRACT.md").write_text(
        "\n".join(contract_lines), encoding="utf-8"
    )

    audit = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "EXTRACTION_COMPLETE_REVIEW_REQUIRED",
        "effect_estimates_inspected": False,
        "upstream_integrity": {
            "gate_c3": f"{len(c3_manifest)}/{len(c3_manifest)}",
            "gate_c3a": f"{len(c3a_manifest)}/{len(c3a_manifest)}",
        },
        "raw_h5ad": {
            "sha256": raw_sha256,
            "size_bytes": raw_path.stat().st_size,
            "shape": list(raw.shape),
            "nonzero_values": full_nonzero_values,
            "minimum_nonzero": minimum_nonzero,
            "maximum_nonzero": maximum_nonzero,
            "raw_umi_total": full_raw_umi_total,
        },
        "cell_id_exact_set": exact_set,
        "cell_id_exact_order": exact_order,
        "key_mismatches": raw_key_mismatches,
        "cells": len(cell),
        "strata": n_strata,
        "residual_risk_calls": int(cell["residual_doublet_auto_call"].sum()),
        "primary_branch_umi_total": primary_umi_total,
        "sensitivity_branch_umi_total": sensitivity_umi_total,
        "pseudobulk_shape": list(aggregate.shape),
        "pseudobulk_nnz": int(aggregate.nnz),
        "checkpoint_chunks": len(checkpoint_paths),
        "count_conservation_pass": primary_umi_total == full_raw_umi_total,
        "next": "independent Gate C4A support, program-availability and integrity review",
    }
    (output / "01_raw_input_and_cell_id_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    audit_lines = [
        "# Gate C4A raw-count extraction audit",
        "",
        "**Status:** `EXTRACTION_COMPLETE_REVIEW_REQUIRED`",
        "",
        f"- Raw cells/features: {raw.shape[0]:,} / {raw.shape[1]:,}",
        f"- Exact cell-ID set: {exact_set}",
        f"- Exact cell-ID row order: {exact_order}",
        f"- Raw nonzero range: {minimum_nonzero}-{maximum_nonzero}",
        f"- Raw UMI total: {full_raw_umi_total:,}",
        f"- Pseudobulk matrix: {aggregate.shape[0]:,} rows x {aggregate.shape[1]:,} genes",
        f"- Pseudobulk nonzero entries: {aggregate.nnz:,}",
        f"- Residual-risk calls excluded in sensitivity branch: {int(cell['residual_doublet_auto_call'].sum()):,}",
        f"- Count conservation: {primary_umi_total == full_raw_umi_total}",
        "- Disease expression coefficients inspected: False",
    ]
    (output / "01_raw_input_and_cell_id_audit.md").write_text(
        "\n".join(audit_lines), encoding="utf-8"
    )
    raw.file.close()
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
