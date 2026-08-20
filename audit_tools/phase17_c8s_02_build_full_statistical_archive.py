#!/usr/bin/env python3
"""Build the Gate C8S reviewer-facing full statistical-results archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pandas as pd


FIXED_ZIP_TIME = (2026, 8, 21, 0, 0, 0)
RUN_RELATIVE = Path("phase17_v7/gateC8S/20260821_supplementary_traceability_freeze")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=RUN_RELATIVE)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def copy_file(root: Path, archive_root: Path, source_relative: str, target_relative: str) -> dict[str, object]:
    source = root / source_relative
    if not source.is_file():
        raise FileNotFoundError(source)
    target = archive_root / target_relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "archive_path": target.relative_to(archive_root).as_posix(),
        "source_project_path": source.relative_to(root).as_posix(),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
    }


def write_design_matrix(source: Path, target: Path, dataset: str) -> dict[str, object]:
    table = pd.read_csv(source)
    analysis_name = source.name.removesuffix("_samples.csv")
    if dataset == "GSE174188":
        keep = [
            "branch",
            "Processing_Cohort",
            "basc_cells",
            "bconv_cells",
            "basc_detected_genes",
            "bconv_detected_genes",
            "basc_library_size_umi",
            "bconv_library_size_umi",
            "matrix_library_size_umi",
            "intercept",
            "age_centered",
            "ethnicity_asian",
            "ethnicity_european",
            "is_managed",
            "is_flare",
        ]
        renamed = {"Processing_Cohort": "processing_cohort"}
    else:
        keep = [
            "cohort",
            "metadata_cells",
            "metadata_labels",
            "bconv_cells",
            "bconv_library_size_umi",
            "bconv_detected_genes",
            "matrix_library_size_umi",
            "intercept",
            "is_sle",
            "is_adult",
            "design_columns",
            "design_rank",
            "minimum_bconv_cells",
        ]
        renamed = {}
    missing = sorted(set(keep) - set(table.columns))
    if missing:
        raise RuntimeError(f"Missing design columns in {source}: {missing}")
    output = table[keep].rename(columns=renamed).copy()
    output.insert(0, "analysis_sample_index", range(1, len(output) + 1))
    output.insert(0, "analysis_name", analysis_name)
    output.insert(0, "dataset", dataset)
    target.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(target, index=False, lineterminator="\n")
    forbidden = {"sample_uuid", "stratum_id", "donor_id", "sample_id", "donor_name", "disease", "disease_state", "sex", "ethnicity", "age_years"}
    if forbidden.intersection(output.columns):
        raise RuntimeError(f"Identifier-bearing columns leaked into {target}")
    return {
        "archive_path": target.parent.name + "/" + target.name,
        "source_project_path": source.as_posix(),
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "rows": len(output),
    }


def write_deterministic_zip(output: Path, archive_root: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((item for item in archive_root.rglob("*") if item.is_file()), key=lambda item: item.relative_to(archive_root).as_posix()):
            relative = path.relative_to(archive_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    archive_root = output_dir / "full_statistical_results"
    if archive_root.exists():
        shutil.rmtree(archive_root)
    archive_root.mkdir(parents=True)

    provenance: list[dict[str, object]] = []
    c3 = "phase17_v7/gateC3A/20260815_frozen_abundance"
    c4 = "phase17_v7/gateC4B/20260815_edger_transcription"
    c5 = "phase17_v7/gateC5B/20260815_gse135779_external_validation"
    c6 = "phase17_v7/gateC6B/20260815_regulatory_evidence"
    c8r = "phase17_v7/gateC8R/20260820_pre_submission_repair"

    for name in (
        "01_base_model_coefficients.csv",
        "02_base_and_nonoverlap_contrasts.csv",
        "03_adjusted_predictions.csv",
        "04_mandatory_sensitivity_contrasts.csv",
        "05_two_part_sensitivity.csv",
        "06_primary_leave_one_out.csv",
        "07_replication_overlap_audit.csv",
        "08_model_diagnostics.csv",
    ):
        provenance.append(copy_file(root, archive_root, f"{c3}/{name}", f"composition/{name}"))

    c4_gene_names = (
        "primary_base",
        "primary_min20",
        "primary_min100",
        "primary_residual_risk_negative",
        "validation_full",
        "validation_nonoverlap",
        "flare_full",
    )
    c5_gene_names = ("childhood_min50", "combined_min20", "combined_min50", "combined_min100", "adult_min50")
    for name in c4_gene_names:
        filename = f"{name}_gene_results.csv.gz"
        provenance.append(copy_file(root, archive_root, f"{c4}/05_gene_results/{filename}", f"gene_level_results/GSE174188/{filename}"))
    for name in c5_gene_names:
        filename = f"{name}_gene_results.csv.gz"
        provenance.append(copy_file(root, archive_root, f"{c5}/05_gene_results/{filename}", f"gene_level_results/GSE135779/{filename}"))

    for name in (
        "05_MODEL_SUMMARY.csv",
        "07_PROGRAM_RESULTS.csv",
        "09_FROZEN_PROGRAM_ARM_CAMERA.csv",
        "10_PRIMARY_PROGRAM_LOO.csv",
        "11_PRIMARY_CONFIRMATORY_GENE_LOO.csv",
        "12_CROSS_COHORT_EFFECT_CONCORDANCE.csv",
        "13_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv",
    ):
        provenance.append(copy_file(root, archive_root, f"{c4}/{name}", f"transcription/GSE174188/{name}"))
    for name in (
        "05_MODEL_SUMMARY.csv",
        "07_PROGRAM_RESULTS.csv",
        "08_PROGRAM_SAMPLE_SCORES.csv.gz",
        "09_FROZEN_PROGRAM_ARM_CAMERA.csv",
        "10_PRIMARY_PROGRAM_DONOR_LOO.csv",
        "11_PRIMARY_CONFIRMATORY_GENE_DONOR_LOO.csv",
        "12_SOURCE_LABEL_LOO_PROGRAM_RESULTS.csv",
        "13_EXTERNAL_GENE_EFFECT_CONCORDANCE.csv",
        "14_PRIMARY_RANKED_QC_FAMILY_AUDIT.csv",
        "16_CROSS_DATASET_IFN_GENE_EFFECTS.csv",
        "16_CROSS_DATASET_IFN_PROGRAM_EFFECTS.csv",
    ):
        provenance.append(copy_file(root, archive_root, f"{c5}/{name}", f"transcription/GSE135779/{name}"))

    for name in (
        "01_CONFIRMATORY_REGULATOR_RESULTS.csv",
        "02_IFN_TARGET_INFLUENCE_SUMMARY.csv",
        "03_IFN_TARGET_LEAVE_ONE_OUT.csv",
        "04_IFN_TARGET_RESAMPLING.csv",
        "05_SUPPORTIVE_SENSITIVITY_REGULATOR_RESULTS.csv",
        "18_GSE23307_LOG2P1_DONOR_PROGRAM_EFFECTS.csv",
        "19_MSIGDB_M5911_PRERANKED_GSEA.csv",
    ):
        provenance.append(copy_file(root, archive_root, f"{c6}/{name}", f"regulatory_and_orthogonal/{name}"))
    for name in (
        "03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv",
        "04_CORRELATION_AWARE_STAT1_STAT2_DECISION.json",
    ):
        provenance.append(copy_file(root, archive_root, f"{c8r}/{name}", f"regulatory_and_orthogonal/{name}"))

    design_rows: list[dict[str, object]] = []
    for name in c4_gene_names:
        source = root / c4 / "02_matrix_exports" / f"{name}_samples.csv"
        target = archive_root / "sanitized_design_matrices" / f"GSE174188_{name}_design.csv"
        row = write_design_matrix(source, target, "GSE174188")
        row["source_project_path"] = source.relative_to(root).as_posix()
        design_rows.append(row)
    for name in c5_gene_names:
        source = root / c5 / "02_matrix_exports" / f"{name}_samples.csv"
        target = archive_root / "sanitized_design_matrices" / f"GSE135779_{name}_design.csv"
        row = write_design_matrix(source, target, "GSE135779")
        row["source_project_path"] = source.relative_to(root).as_posix()
        design_rows.append(row)
    provenance.extend(design_rows)

    framework = pd.DataFrame(
        [
            ["B_ASC composition", "sample-cohort stratum", "beta-binomial Wald", "two-sided", "BH across three frozen base contrasts", "primary plus frozen replication/secondary"],
            ["B_ASC composition sensitivity", "sample-cohort stratum", "beta-binomial Wald; observed-information and HC1 covariance", "two-sided", "nominal sensitivity estimates", "robustness only"],
            ["Two-part ASC presence", "sample-cohort stratum", "Firth logistic Wald", "two-sided", "nominal sensitivity estimates", "robustness only"],
            ["Two-part positive abundance", "ASC-positive sample-cohort stratum", "OLS with HC3 covariance", "two-sided", "nominal sensitivity estimates", "robustness only"],
            ["Gene-level differential expression", "donor/sample pseudobulk", "edgeR robust quasi-likelihood F test", "two-sided", "BH across filterByExpr-tested genes within each contrast", "gene-level inference"],
            ["Four frozen program scores", "donor/sample pseudobulk", "OLS with HC3 covariance", "two-sided", "BH across four programs within each analysis", "program-level inference"],
            ["Ranked program arms", "ranked gene statistics", "CAMERA competitive test", "directional", "BH across frozen program arms within each analysis", "ranked-list coherence"],
            ["TF-target activity", "ranked gene statistics", "signed-target slope t test", "two-sided", "global BH across 8 regulators x 3 confirmatory contrasts", "confirmatory regulatory evidence"],
            ["STAT1/STAT2 correlation sensitivity", "ranked gene statistics", "CAMERA and FRY", "positive-direction", "separate BH families of six tests per method", "correlation-aware sensitivity"],
            ["MSigDB M5911", "ranked gene statistics", "weighted preranked permutation test (10,000)", "positive-direction", "descriptive BH across three contrasts", "orthogonal support"],
            ["GSE23307 IFNB1 perturbation", "paired donor", "log2(x+1) paired difference", "not tested", "none; n=2", "descriptive perturbational support"],
        ],
        columns=["result_family", "biological_unit", "test_or_estimator", "sidedness", "multiplicity_control", "evidentiary_role"],
    )
    framework_path = archive_root / "statistical_framework" / "STATISTICAL_TEST_AND_MULTIPLICITY_MAP.csv"
    framework_path.parent.mkdir(parents=True, exist_ok=True)
    framework.to_csv(framework_path, index=False, lineterminator="\n")
    provenance.append({"archive_path": framework_path.relative_to(archive_root).as_posix(), "source_project_path": "generated by audit_tools/phase17_c8s_02_build_full_statistical_archive.py", "bytes": framework_path.stat().st_size, "sha256": sha256(framework_path)})

    readme = """# Gate C8S full statistical results

This reviewer-facing archive contains complete result tables supporting the frozen manuscript, not raw sequencing data. GSE174188 is the discovery and internal donor-nonoverlap resource; the latter is not an independent dataset. GSE135779 is the independent childhood validation dataset. GSE23307 contains two paired donors after IFNB1 stimulation and is descriptive only.

## Contents

- `gene_level_results/`: all filterByExpr-tested gene results for seven GSE174188 and five GSE135779 model branches.
- `composition/`: frozen beta-binomial composition estimates, predictions, sensitivities, leave-one-out results and diagnostics.
- `transcription/`: model summaries, four-program tests, ranked-list coherence, influence diagnostics and cross-dataset concordance.
- `regulatory_and_orthogonal/`: global-24 regulator results, target influence/resampling, CAMERA/FRY sensitivity, M5911 enrichment and two-donor perturbation summaries.
- `sanitized_design_matrices/`: the 12 analysis design tables with direct sample, donor and UUID fields removed. `analysis_sample_index` is local to each table and cannot be joined to source identities.
- `statistical_framework/`: the prespecified testing, sidedness and multiplicity map.

BH q values are family-specific as documented in `STATISTICAL_TEST_AND_MULTIPLICITY_MAP.csv`; they must not be compared as if they came from one universal family. Unless explicitly labelled directional, reported tests are two-sided and confidence intervals are 95%. No prospective power calculation was performed because this is a retrospective secondary analysis of public datasets; available biological units after frozen eligibility rules determined each analysis size.

Raw H5AD, FASTQ and full count matrices are intentionally excluded from this attachment. Public source accessions and reproducibility instructions are provided in the manuscript and repository. File-level provenance and SHA-256 values are recorded in `SOURCE_PROVENANCE.csv` and `MANIFEST_SHA256.csv`.
"""
    readme_path = archive_root / "README_FULL_STATISTICAL_RESULTS.md"
    readme_path.write_text(readme, encoding="utf-8", newline="\n")
    provenance.append({"archive_path": readme_path.relative_to(archive_root).as_posix(), "source_project_path": "generated by audit_tools/phase17_c8s_02_build_full_statistical_archive.py", "bytes": readme_path.stat().st_size, "sha256": sha256(readme_path)})

    provenance_path = archive_root / "SOURCE_PROVENANCE.csv"
    with provenance_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["archive_path", "source_project_path", "bytes", "sha256"])
        writer.writeheader()
        for row in sorted(provenance, key=lambda item: str(item["archive_path"])):
            writer.writerow({key: row[key] for key in writer.fieldnames})

    manifest_path = archive_root / "MANIFEST_SHA256.csv"
    payload_files = sorted((path for path in archive_root.rglob("*") if path.is_file() and path != manifest_path), key=lambda path: path.relative_to(archive_root).as_posix())
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["relative_path", "bytes", "sha256"])
        for path in payload_files:
            writer.writerow([path.relative_to(archive_root).as_posix(), path.stat().st_size, sha256(path)])

    gene_files = list((archive_root / "gene_level_results").rglob("*.csv.gz"))
    design_files = list((archive_root / "sanitized_design_matrices").glob("*.csv"))
    if len(gene_files) != 12 or len(design_files) != 12:
        raise RuntimeError(f"Archive cardinality failure: gene={len(gene_files)}, design={len(design_files)}")
    if any(path.stat().st_size == 0 for path in archive_root.rglob("*") if path.is_file()):
        raise RuntimeError("Zero-byte file in statistical archive")

    zip_path = output_dir / "Additional_file_4_Full_Statistical_Results_GateC8S.zip"
    write_deterministic_zip(zip_path, archive_root)
    first_hash = sha256(zip_path)
    verification_path = output_dir / "Additional_file_4_Full_Statistical_Results_GateC8S.verify.zip"
    write_deterministic_zip(verification_path, archive_root)
    second_hash = sha256(verification_path)
    verification_path.unlink()
    if first_hash != second_hash:
        raise RuntimeError("Deterministic ZIP verification failed")

    status = {
        "created_at": "2026-08-21",
        "status": "PASS_GATE_C8S_FULL_STATISTICAL_ARCHIVE_BUILT",
        "complete_gene_result_files": len(gene_files),
        "sanitized_design_matrices": len(design_files),
        "payload_files": len(list(path for path in archive_root.rglob("*") if path.is_file())),
        "payload_bytes": sum(path.stat().st_size for path in archive_root.rglob("*") if path.is_file()),
        "archive": zip_path.relative_to(root).as_posix(),
        "archive_bytes": zip_path.stat().st_size,
        "archive_sha256": first_hash,
        "deterministic_rebuild_match": True,
        "direct_identifiers_in_design_matrices": False,
    }
    (output_dir / "05_FULL_STATISTICAL_RESULTS_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
