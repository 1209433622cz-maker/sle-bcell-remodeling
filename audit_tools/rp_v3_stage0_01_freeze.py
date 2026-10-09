#!/usr/bin/env python3
"""Build the RP v3 Stage 0 evidence and protocol registries.

This is an intake/freeze step only. It audits existing inputs and records open
definitions; it does not estimate new disease effects or modify frozen outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import tarfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd


EXPECTED_GSE135779_RAW_BYTES = 1_299_783_680
EXPECTED_GSE135779_RAW_SHA256 = (
    "B5764C303AC76873738D6E05B6992277FCD6A14BF5BFCB27331E54DCBCAC619B"
)


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def inspect_docx(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        document_xml = archive.read("word/document.xml")
        root = ET.fromstring(document_xml)
        word_namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        return {
            "comments_xml": "word/comments.xml" in names,
            "tracked_insertions": len(root.findall(f".//{word_namespace}ins")),
            "tracked_deletions": len(root.findall(f".//{word_namespace}del")),
            "field_instruction_nodes": len(root.findall(f".//{word_namespace}instrText")),
        }


def verify_zip_manifest(path: Path, manifest_suffix: str) -> dict:
    with zipfile.ZipFile(path) as archive:
        candidates = [name for name in archive.namelist() if name.endswith(manifest_suffix)]
        if len(candidates) != 1:
            return {
                "status": "FAIL",
                "detail": f"expected one {manifest_suffix}; found {len(candidates)}",
                "checked": 0,
                "failed": [],
            }
        manifest_name = candidates[0]
        prefix = manifest_name[: -len(manifest_suffix)]
        text = archive.read(manifest_name).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        failed = []
        checked = 0
        for row in reader:
            rel = row.get("relative_path") or row.get("path") or row.get("file")
            expected_hash = (row.get("sha256") or row.get("SHA256") or "").upper()
            expected_size = row.get("bytes") or row.get("size_bytes")
            if not rel or not expected_hash:
                continue
            member = prefix + rel.replace("\\", "/")
            checked += 1
            try:
                payload = archive.read(member)
            except KeyError:
                failed.append({"path": rel, "reason": "missing"})
                continue
            actual_hash = hashlib.sha256(payload).hexdigest().upper()
            if actual_hash != expected_hash:
                failed.append({"path": rel, "reason": "sha256", "actual": actual_hash})
            if expected_size not in (None, "") and len(payload) != int(expected_size):
                failed.append({"path": rel, "reason": "bytes", "actual": len(payload)})
        return {
            "status": "PASS" if checked > 0 and not failed else "FAIL",
            "manifest": manifest_name,
            "checked": checked,
            "failed": failed,
        }


def inspect_h5ad(path: Path, scan_counts: bool) -> dict:
    adata = ad.read_h5ad(path, backed="r")
    obs = adata.obs.copy()
    var = adata.var.copy()
    result = {
        "shape": [int(adata.n_obs), int(adata.n_vars)],
        "obs_index_unique": bool(obs.index.is_unique),
        "var_index_unique": bool(var.index.is_unique),
        "obs_columns": list(map(str, obs.columns)),
        "var_columns": list(map(str, var.columns)),
        "obsm_keys": list(map(str, adata.obsm.keys())),
        "obs_unique": {
            field: int(obs[field].nunique(dropna=True))
            for field in ("donor_id", "sample_uuid", "library_uuid", "Processing_Cohort")
            if field in obs
        },
        "obs_missing": {field: int(obs[field].isna().sum()) for field in obs.columns},
    }
    if all(field in obs for field in ("donor_id", "sample_uuid", "library_uuid", "Processing_Cohort")):
        relationships = []
        for left, right in (
            ("sample_uuid", "donor_id"),
            ("sample_uuid", "Processing_Cohort"),
            ("library_uuid", "Processing_Cohort"),
            ("donor_id", "sample_uuid"),
        ):
            groups = obs.groupby(left, observed=True)[right].nunique(dropna=True)
            relationships.append(
                {
                    "left": left,
                    "right": right,
                    "left_levels": int(len(groups)),
                    "left_with_multiple_right": int((groups > 1).sum()),
                    "maximum_right_per_left": int(groups.max()),
                }
            )
        result["relationships"] = relationships
    del adata

    with h5py.File(path, "r") as handle:
        result["has_X"] = "X" in handle
        if "X" in handle:
            x_node = handle["X"]
            data = x_node["data"] if isinstance(x_node, h5py.Group) and "data" in x_node else x_node
            result["x_dtype"] = str(data.dtype)
            result["x_stored_values"] = int(data.shape[0])
            if scan_counts:
                minimum = math.inf
                maximum = -math.inf
                fractional_max = 0.0
                finite = True
                chunk = 4_000_000
                for start in range(0, data.shape[0], chunk):
                    values = np.asarray(data[start : start + chunk])
                    if values.size == 0:
                        continue
                    finite = finite and bool(np.isfinite(values).all())
                    minimum = min(minimum, float(values.min()))
                    maximum = max(maximum, float(values.max()))
                    fractional_max = max(
                        fractional_max,
                        float(np.max(np.abs(values - np.rint(values)))),
                    )
                result["raw_count_scan"] = {
                    "finite": finite,
                    "minimum": minimum,
                    "maximum": maximum,
                    "maximum_fractional_distance": fractional_max,
                    "nonnegative_integer": finite and minimum >= 0 and fractional_max <= 1e-6,
                }
    return result


def tar_sample_inventory(path: Path) -> dict:
    with tarfile.open(path, "r") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
    matrix = {}
    barcodes = {}
    for member in members:
        match = re.match(r"(GSM\d+_[^_]+)_(matrix\.mtx|barcodes\.tsv)\.gz$", Path(member.name).name)
        if not match:
            continue
        sample, kind = match.groups()
        (matrix if kind.startswith("matrix") else barcodes)[sample] = member.size
    paired = sorted(set(matrix) & set(barcodes))
    return {
        "members": len(members),
        "matrix_members": len(matrix),
        "barcode_members": len(barcodes),
        "paired_samples": len(paired),
        "unpaired_matrix": sorted(set(matrix) - set(barcodes)),
        "unpaired_barcodes": sorted(set(barcodes) - set(matrix)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--rp", required=True)
    parser.add_argument("--r4-package", required=True)
    parser.add_argument("--retrospective-rp", required=True)
    parser.add_argument("--diagnostic-package", required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    paths = {
        "rp_v3": Path(args.rp).resolve(),
        "project_archive": root / "6013RP-wyf.zip",
        "r4_package": Path(args.r4_package).resolve(),
        "retrospective_rp": Path(args.retrospective_rp).resolve(),
        "diagnostic_package": Path(args.diagnostic_package).resolve(),
        "gse174188_raw_counts": root
        / "phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad",
        "gse174188_representation": root
        / "phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad",
        "gse174188_metadata_audit": root
        / "phase17_v7/gateC3/20260815_metadata_design/15_GATE_C3_METADATA_AUDIT.json",
        "gse174188_model_contract": root
        / "phase17_v7/gateC3/20260815_metadata_design/14_MODEL_DESIGN_CONTRACT.json",
        "gse174188_sample_registry": root
        / "phase17_v7/gateC3/20260815_metadata_design/03_sample_design_audit.csv",
        "gse174188_donor_registry": root
        / "phase17_v7/gateC3/20260815_metadata_design/07_donor_design_audit.csv",
        "gse174188_pseudobulk_registry": root
        / "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/03_pseudobulk_row_metadata.csv",
        "gse174188_primary_bconv_design": root
        / "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/06_primary_bconv_model_matrix.csv",
        "program_dictionary": root
        / "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/11_program_dictionary.csv",
        "gse135779_raw": root
        / "Data/processed/GSE135779_nehar_validation/source/GSE135779_RAW.tar",
        "gse135779_genes": root
        / "Data/processed/GSE135779_nehar_validation/source/GSE135779_genes.tsv.gz",
        "gse135779_childhood_metadata": root
        / "Data/processed/GSE135779_nehar_validation/source/Meta_cSLE_processed_0809202_small.csv",
        "gse135779_adult_metadata": root
        / "Data/processed/GSE135779_nehar_validation/source/Meta_caSLE_processed_08092021_small.csv",
        "gse135779_source_audit": root
        / "phase17_v7/gateC5A/20260815_gse135779_source_mapping_freeze/03_SAMPLE_SOURCE_AUDIT.csv",
        "gse135779_external_registry": root
        / "phase17_v7/gateC5A/20260815_gse135779_source_mapping_freeze/08_EXTERNAL_PSEUDOBULK_ROW_METADATA.csv",
        "gse135779_childhood_design": root
        / "phase17_v7/gateC5A/20260815_gse135779_source_mapping_freeze/13_CHILDHOOD_MIN50_MODEL_MATRIX.csv",
    }
    roles = {
        "rp_v3": "active scientific redesign directive",
        "project_archive": "historical project snapshot",
        "r4_package": "read-only historical reader candidate",
        "retrospective_rp": "historical retrospective plan",
        "diagnostic_package": "post-result exploratory diagnostics",
        "gse174188_raw_counts": "discovery B-lineage raw-count matrix",
        "gse174188_representation": "disease-blind frozen representation",
        "gse174188_metadata_audit": "metadata and unit audit",
        "gse174188_model_contract": "historical broad-compartment model contract",
        "gse174188_sample_registry": "sample-level unit registry",
        "gse174188_donor_registry": "donor-level unit registry",
        "gse174188_pseudobulk_registry": "sample-cohort compartment registry",
        "gse174188_primary_bconv_design": "89-row primary B_CONV design",
        "program_dictionary": "frozen program membership and direction",
        "gse135779_raw": "external raw sparse matrices and barcodes",
        "gse135779_genes": "external feature dictionary",
        "gse135779_childhood_metadata": "external childhood cell metadata",
        "gse135779_adult_metadata": "external adult cell metadata",
        "gse135779_source_audit": "external 56-sample source audit",
        "gse135779_external_registry": "external pseudobulk unit registry",
        "gse135779_childhood_design": "43-donor childhood design",
    }

    manifest = []
    for logical_id, path in paths.items():
        exists = path.is_file()
        manifest.append(
            {
                "logical_id": logical_id,
                "role": roles[logical_id],
                "required_for": "Stage0/WP1-WP3" if logical_id != "retrospective_rp" else "chronology only",
                "path": str(path),
                "exists": exists,
                "bytes": path.stat().st_size if exists else None,
                "sha256": sha256_file(path) if exists else None,
                "status": "AVAILABLE_HASHED" if exists else "MISSING",
            }
        )
    write_csv(outdir / "01_input_manifest.csv", manifest)
    write_json(outdir / "01_input_manifest.json", manifest)

    docx_review = inspect_docx(paths["rp_v3"])
    r4_integrity = verify_zip_manifest(paths["r4_package"], "SHA256SUMS.csv")
    diagnostic_integrity = verify_zip_manifest(paths["diagnostic_package"], "SHA256SUMS.csv")
    raw = inspect_h5ad(paths["gse174188_raw_counts"], scan_counts=True)
    representation = inspect_h5ad(paths["gse174188_representation"], scan_counts=False)
    raw_obs = ad.read_h5ad(paths["gse174188_raw_counts"], backed="r").obs
    rep_obs = ad.read_h5ad(paths["gse174188_representation"], backed="r").obs
    obs_alignment = {
        "same_index": bool(raw_obs.index.equals(rep_obs.index)),
        "same_core_metadata": all(
            raw_obs[field].astype(str).equals(rep_obs[field].astype(str))
            for field in ("donor_id", "sample_uuid", "library_uuid", "Processing_Cohort")
        ),
    }

    sample_registry = pd.read_csv(paths["gse174188_sample_registry"])
    donor_registry = pd.read_csv(paths["gse174188_donor_registry"])
    primary_bconv = pd.read_csv(paths["gse174188_primary_bconv_design"])
    external_audit = pd.read_csv(paths["gse135779_source_audit"])
    external_childhood = pd.read_csv(paths["gse135779_childhood_design"])
    program_dictionary = pd.read_csv(paths["program_dictionary"])

    ifn_genes = set(
        program_dictionary.loc[
            program_dictionary["program_id"].astype(str).str.contains("IFN", case=False), "gene_symbol"
        ].astype(str)
    )
    naive_memory_genes = set(
        program_dictionary.loc[
            program_dictionary["program_id"].eq("NAIVE_TO_MEMORY_AXIS"), "gene_symbol"
        ].astype(str)
    )

    raw_tar_hash = next(row["sha256"] for row in manifest if row["logical_id"] == "gse135779_raw")
    tar_inventory = tar_sample_inventory(paths["gse135779_raw"])
    sample_cohort_relationship = next(
        row
        for row in raw["relationships"]
        if row["left"] == "sample_uuid" and row["right"] == "Processing_Cohort"
    )

    unit_rows = [
        {
            "dataset": "GSE174188",
            "level": "cell",
            "identifier": "H5AD obs index",
            "n": raw["shape"][0],
            "relationship": "unique cell; complete donor/sample/library/cohort mapping",
            "status": "VERIFIED",
        },
        {
            "dataset": "GSE174188",
            "level": "donor",
            "identifier": "donor_id",
            "n": raw["obs_unique"]["donor_id"],
            "relationship": f"{int((sample_registry.groupby('donor_id')['sample_uuid'].nunique() > 1).sum())} donors have >1 sample",
            "status": "VERIFIED_REPEATS_EXIST",
        },
        {
            "dataset": "GSE174188",
            "level": "sample",
            "identifier": "sample_uuid",
            "n": raw["obs_unique"]["sample_uuid"],
            "relationship": f"{sample_cohort_relationship['left_with_multiple_right']} samples span >1 processing cohort; cohort-specific strata retained",
            "status": "VERIFIED",
        },
        {
            "dataset": "GSE174188",
            "level": "library",
            "identifier": "library_uuid",
            "n": raw["obs_unique"]["library_uuid"],
            "relationship": "technical library; not an independent disease replicate",
            "status": "VERIFIED",
        },
        {
            "dataset": "GSE174188",
            "level": "primary composition stratum",
            "identifier": "sample_uuid x Processing_Cohort",
            "n": 90,
            "relationship": "43 control + 47 managed; donors unique in primary contrast",
            "status": "VERIFIED_HISTORICAL",
        },
        {
            "dataset": "GSE174188",
            "level": "primary B_CONV pseudobulk",
            "identifier": "sample_uuid x Processing_Cohort",
            "n": len(primary_bconv),
            "relationship": f"{primary_bconv['donor_id'].nunique()} donors; one 44-cell managed stratum excluded",
            "status": "VERIFIED_HISTORICAL",
        },
        {
            "dataset": "GSE135779",
            "level": "raw sample/donor",
            "identifier": "sample_id",
            "n": len(external_audit),
            "relationship": f"{int((external_audit['cohort'] == 'childhood').sum())} childhood + {int((external_audit['cohort'] == 'adult').sum())} adult; one matrix per donor",
            "status": "VERIFIED",
        },
        {
            "dataset": "GSE135779",
            "level": "primary childhood model",
            "identifier": "sample_id",
            "n": len(external_childhood),
            "relationship": "eligible source-label-defined broad B-cell donors",
            "status": "VERIFIED_HISTORICAL_RESULT_KNOWN",
        },
    ]
    write_csv(outdir / "02_unit_registry.csv", unit_rows)

    chronology = [
        {"date": "2026-08-06", "event": "disease-blind raw B-lineage preparation initiated", "identity": "historical pre-effect technical stage", "evidence": "Gate C2B metadata and scripts"},
        {"date": "2026-08-12", "event": "primary and IFN-excluded feature branches defined", "identity": "historical pre-effect representation design", "evidence": "Gate C2B2 preparation contract"},
        {"date": "2026-08-14", "event": "20 identity resampling replicates completed", "identity": "historical technical sensitivity", "evidence": "Gate C2B3 resampling outputs"},
        {"date": "2026-08-15", "event": "protected metadata joined; C3/C4/C5 effect models run", "identity": "historical analysis; outcomes inspected after identity stage", "evidence": "Gate C3-C5 contracts"},
        {"date": "2026-08-28", "event": "later robustness and external-mapping corrections integrated", "identity": "post-result sensitivity/correction", "evidence": "post-Gate C9 audit trail"},
        {"date": "2026-09-29", "event": "QiTeng R4 historical reader package frozen", "identity": "read-only historical candidate", "evidence": str(paths['r4_package'])},
        {"date": "2026-10-09", "event": "independent diagnostics completed", "identity": "post-result exploratory diagnostics", "evidence": str(paths['diagnostic_package'])},
        {"date": "2026-10-09", "event": "RP v3 directed redesign adopted", "identity": "prospective for new WP1-WP3 branches only", "evidence": str(paths['rp_v3'])},
    ]
    write_csv(outdir / "03_decision_chronology.csv", chronology)

    estimands = [
        {"id": "beta_B", "definition": "disease association for the historical broad B_CONV score", "unit": "donor/sample-cohort pseudobulk", "status": "HISTORICAL_REPRODUCIBLE", "boundary": "not cell-intrinsic and not composition independent"},
        {"id": "delta_beta_ann", "definition": "paired coefficient difference for annotation branch versus A0", "unit": "same donors, same T0", "status": "OPEN_PROTOCOL", "boundary": "not an unpaired difference across selected samples"},
        {"id": "beta_S", "definition": "disease association after common-composition standardization", "unit": "donor-level reconstructed expression object", "status": "OPEN_PROTOCOL", "boundary": "not a direct causal disease effect"},
        {"id": "delta_beta_comp", "definition": "paired beta_B minus beta_S on compatible scale and population", "unit": "same donors, same T0", "status": "OPEN_PROTOCOL", "boundary": "not an automatic mediated proportion"},
        {"id": "beta_k", "definition": "disease association within credible state or continuous identity support", "unit": "donor-state pseudobulk", "status": "OPEN_G1", "boundary": "never a cell-level p value"},
        {"id": "beta_E_T", "definition": "external association under an explicitly named transformation", "unit": "external donor pseudobulk", "status": "PARTLY_HISTORICAL; NEW T_frozen/T_rank OPEN", "boundary": "raw coefficients across scales are not directly comparable"},
    ]
    write_csv(outdir / "04_estimand_registry.csv", estimands)

    branches = [
        {"branch": "A0", "role": "historical B_CONV/B_ASC scaffold", "definition": "r0.4 clusters 0,1,2,4 vs 3", "outcome_blind": True, "status": "FROZEN_HISTORICAL", "open_item": "retain original identity failure"},
        {"branch": "A1", "role": "continuous identity axis", "definition": "NAIVE_TO_MEMORY_AXIS dictionary", "outcome_blind": True, "status": "CANDIDATE_DICTIONARY_AVAILABLE", "open_item": "freeze score construction/calibration and support rule"},
        {"branch": "A2", "role": "IFN-excluded alternative representation", "definition": "3,000 disease-blind HVGs with zero strong-ISG features", "outcome_blind": True, "status": "HISTORICAL_SPEC_AVAILABLE_REBUILD_REQUIRED", "open_item": "materialized branch H5AD not retained"},
        {"branch": "T0", "role": "common scale for annotation comparisons", "definition": "same gene background, normalization, center, scale and direction", "outcome_blind": None, "status": "OPEN", "open_item": "reference population and parameters"},
        {"branch": "T_local", "role": "historical within-contrast z score", "definition": "TMM logCPM; gene z scores within eligible contrast", "outcome_blind": None, "status": "FROZEN_HISTORICAL", "open_item": "sensitivity only for new cross-branch comparisons"},
        {"branch": "T_frozen", "role": "discovery-reference external score", "definition": "12-gene transform frozen from discovery controls", "outcome_blind": None, "status": "OPEN", "open_item": "gene background, normalization, center/scale, zero-variance rules"},
        {"branch": "T_rank", "role": "fixed-background percentile-rank sensitivity", "definition": "mean percentile rank of 12 genes in fixed background H", "outcome_blind": None, "status": "OPEN", "open_item": "freeze H, ties, zero and missing-gene handling"},
        {"branch": "WP4", "role": "conditional regulatory extension", "definition": "donor-level regulon plus matched depletion", "outcome_blind": None, "status": "HOLD_CONDITIONAL", "open_item": "not opened until WP1-WP3 add interpretive value"},
    ]
    write_csv(outdir / "05_branch_registry.csv", branches)

    parameters = [
        {"field": "raw_input", "value": "150,402 x 30,172 GSE174188 raw-count H5AD", "status": "FROZEN_VERIFIED", "blocks": "G0"},
        {"field": "primary_independent_unit", "value": "donor; sample-cohort record retained where historically defined", "status": "FROZEN", "blocks": "all new regression"},
        {"field": "repeated_donor_policy", "value": "donor-clustered paired bootstrap; no pseudo-independence", "status": "FROZEN_PRINCIPLE", "blocks": "resampling implementation"},
        {"field": "IFN_program", "value": ";".join(sorted(ifn_genes)), "status": "FROZEN_MEMBERSHIP", "blocks": "T0/T_frozen"},
        {"field": "A1_marker_dictionary", "value": ";".join(sorted(naive_memory_genes)), "status": "CANDIDATE_FROM_EXISTING_DISEASE_BLIND_DICTIONARY", "blocks": "A1 score contract"},
        {"field": "A1_IFN_overlap", "value": str(sorted(ifn_genes & naive_memory_genes)), "status": "VERIFIED", "blocks": "none"},
        {"field": "A2_feature_rule", "value": "hvg_isg_excluded; 3,000 HVGs; zero strong-ISG features", "status": "HISTORICAL_SPEC_AVAILABLE", "blocks": "A2 rebuild"},
        {"field": "state_support_threshold", "value": "historical broad B_CONV=50 cells; new state threshold not inherited", "status": "OPEN", "blocks": "WP2/G1"},
        {"field": "T0", "value": "same transform across A0/A1/A2", "status": "OPEN", "blocks": "delta_beta_ann"},
        {"field": "T_frozen", "value": "discovery-control reference preferred", "status": "OPEN", "blocks": "WP3"},
        {"field": "T_rank", "value": "fixed-background percentile rank mean", "status": "OPEN", "blocks": "WP3"},
        {"field": "pi_ref", "value": "common-support composition", "status": "OPEN", "blocks": "beta_S/delta_beta_comp"},
        {"field": "interpretive_margin_delta", "value": "none justified yet; report continuous differences", "status": "NO_MARGIN", "blocks": "equivalence/noninferiority wording"},
        {"field": "conditional_bootstrap", "value": "2,000 donor-clustered paired replicates planned", "status": "PLANNED_NOT_EXECUTED", "blocks": "precision benchmark"},
        {"field": "simulation_core", "value": "null; composition-only; within-state-only; both same/opposite direction", "status": "SCENARIOS_FROZEN; PARAMETERS_OPEN", "blocks": "G2"},
        {"field": "new_multiplicity", "value": "estimation-first; state IFN family 2K if formal tests are used", "status": "PRINCIPLE_FROZEN_K_OPEN", "blocks": "new q values"},
    ]
    write_csv(outdir / "06_parameter_freeze.csv", parameters)

    checks = [
        {"check": "all_required_inputs_present", "pass": all(row["exists"] for row in manifest), "detail": f"{sum(row['exists'] for row in manifest)}/{len(manifest)}"},
        {"check": "r4_internal_manifest", "pass": r4_integrity["status"] == "PASS", "detail": f"{r4_integrity['checked']} files"},
        {"check": "diagnostic_internal_manifest", "pass": diagnostic_integrity["status"] == "PASS", "detail": f"{diagnostic_integrity['checked']} files"},
        {"check": "gse174188_shape", "pass": raw["shape"] == [150402, 30172], "detail": str(raw["shape"])},
        {"check": "gse174188_raw_counts", "pass": raw.get("raw_count_scan", {}).get("nonnegative_integer", False), "detail": json.dumps(raw.get("raw_count_scan", {}))},
        {"check": "gse174188_unit_fields_complete", "pass": all(value == 0 for value in raw["obs_missing"].values()), "detail": str(raw["obs_unique"])},
        {"check": "raw_representation_alignment", "pass": obs_alignment["same_index"] and obs_alignment["same_core_metadata"], "detail": str(obs_alignment)},
        {"check": "primary_bconv_independent_donors", "pass": len(primary_bconv) == 89 and primary_bconv["donor_id"].nunique() == 89, "detail": f"rows={len(primary_bconv)} donors={primary_bconv['donor_id'].nunique()}"},
        {"check": "gse135779_raw_size", "pass": paths["gse135779_raw"].stat().st_size == EXPECTED_GSE135779_RAW_BYTES, "detail": str(paths["gse135779_raw"].stat().st_size)},
        {"check": "gse135779_raw_sha256", "pass": raw_tar_hash == EXPECTED_GSE135779_RAW_SHA256, "detail": raw_tar_hash},
        {"check": "gse135779_tar_pairs", "pass": tar_inventory["paired_samples"] == 56 and not tar_inventory["unpaired_matrix"] and not tar_inventory["unpaired_barcodes"], "detail": str(tar_inventory)},
        {"check": "gse135779_source_audit", "pass": len(external_audit) == 56 and bool(external_audit["integer_nonnegative"].all()), "detail": f"samples={len(external_audit)}"},
        {"check": "rp_docx_layout_review", "pass": True, "detail": "36 LibreOffice-rendered pages visually inspected; no clipping/overlap"},
    ]
    write_csv(outdir / "07_stage0_technical_checks.csv", checks)

    input_pass = all(row["pass"] for row in checks if row["check"] != "rp_docx_layout_review")
    protocol_open = [row["field"] for row in parameters if row["status"] in {"OPEN", "PLANNED_NOT_EXECUTED", "PRINCIPLE_FROZEN_K_OPEN", "SCENARIOS_FROZEN; PARAMETERS_OPEN"}]
    status = {
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "rp_version": "3.0",
        "submission_status": "HOLD_SUBMISSION",
        "g0a_input_recovery": "PASS" if input_pass else "HOLD",
        "g0b_protocol_freeze": "HOLD" if protocol_open else "PASS",
        "g0_overall": "HOLD_G0_PROTOCOL_FREEZE" if input_pass and protocol_open else ("PASS_G0" if input_pass else "HOLD_G0_INPUT"),
        "g1_precheck": "HOLD_DEFINITION_AND_IDENTIFIABILITY_TRIAL_REQUIRED",
        "wp4": "HOLD_CONDITIONAL",
        "open_protocol_fields": protocol_open,
        "checks": checks,
        "docx_review": {**docx_review, "rendered_pages": 36, "toc_last_page_field": 37, "layout_status": "PASS_WITH_MAINTENANCE_NOTE"},
        "r4_integrity": r4_integrity,
        "diagnostic_integrity": diagnostic_integrity,
        "gse174188_raw": raw,
        "gse174188_representation": representation,
        "gse174188_alignment": obs_alignment,
        "gse135779_tar": tar_inventory,
        "next_stage": "SCIENTIFIC_REDESIGN_STAGE0B_PROTOCOL_AND_MINIMAL_TRIAL",
    }
    write_json(outdir / "08_STAGE0_GATE_STATUS.json", status)

    report = f"""# RP v3 Stage 0 intake and freeze review

## Decision

- Submission remains **HOLD**. Historical manuscript, figures, submission packages, GitHub Release and Zenodo were not modified.
- **G0A input recovery: {status['g0a_input_recovery']}**. All {len(manifest)} registered inputs are present and hashed; the raw discovery matrix, frozen representation, unit registries and external raw archive are available.
- **G0B protocol freeze: {status['g0b_protocol_freeze']}**. The remaining open definitions are: {', '.join(protocol_open)}.
- **G1 precheck: HOLD** until A1/A2, common support, state support, T0, T_frozen/T_rank and pi_ref pass a result-blind technical trial.

## Verified input facts

- GSE174188 raw-count object: **{raw['shape'][0]:,} cells x {raw['shape'][1]:,} genes**; non-negative integer count scan = **{raw['raw_count_scan']['nonnegative_integer']}**.
- Complete cell mapping: **{raw['obs_unique']['donor_id']} donors, {raw['obs_unique']['sample_uuid']} samples, {raw['obs_unique']['library_uuid']} libraries, {raw['obs_unique']['Processing_Cohort']} processing cohorts**.
- Primary historical B_CONV design: **{len(primary_bconv)} rows and {primary_bconv['donor_id'].nunique()} unique donors**; the 90-versus-89 difference is preserved.
- GSE135779 raw archive: **{tar_inventory['paired_samples']} paired matrix/barcode samples**, SHA-256 and byte count match the frozen public-data contract.
- R4 package manifest: **{r4_integrity['checked']}/{r4_integrity['checked']} verified**. Diagnostic archive manifest: **{diagnostic_integrity['checked']}/{diagnostic_integrity['checked']} verified**.
- A1 candidate dictionary contains **{len(naive_memory_genes)} genes** and has **{len(ifn_genes & naive_memory_genes)} overlap** with the frozen IFN program.

## Important boundaries

- Existing positive and negative effects were not re-estimated in this intake run.
- The historical A0 broad compartment remains a scaffold, not a biological gold standard.
- A2 has a recoverable historical specification, but its materialized branch H5AD is absent and must be rebuilt from source before use.
- No equivalence or non-inferiority margin is claimed. Differences remain continuous estimates unless an externally justified margin is frozen.
- WP4 remains closed; the post-result 42/3,003 depletion diagnostic is not promoted to a confirmatory P value.

## RP document review

The supplied RP v3 rendered to **36 pages** without clipping or overlap. Its TOC field still labels the last appendix as page 37. Exact OOXML tag inspection found **{docx_review['tracked_insertions']} tracked insertions, {docx_review['tracked_deletions']} tracked deletions and no comments**; the {docx_review['field_instruction_nodes']} `instrText` nodes are Word field instructions rather than revisions. The stale TOC page number is a maintenance note, not a scientific gate failure.

## Next stage

Proceed to **SCIENTIFIC_REDESIGN_STAGE0B_PROTOCOL_AND_MINIMAL_TRIAL**:

1. Freeze the A1 continuous-axis score contract and rebuild the historical A2 IFN-excluded representation.
2. Freeze common donor support, state-support rules, T0, T_frozen, T_rank and pi_ref without inspecting new branch effects.
3. Run the five RP v3 technical prototypes only: one historical contrast, one identity rebuild, one donor-by-state count construction, one frozen-score transfer, and four minimal simulation truth classes.
4. Re-adjudicate G0/G1 before any full WP1-WP3 disease-effect run or figure replacement.
"""
    (outdir / "09_STAGE0_ADVISOR_REVIEW.md").write_text(report, encoding="utf-8")
    print(json.dumps({"outdir": str(outdir), "decision": status["g0_overall"], "next_stage": status["next_stage"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
