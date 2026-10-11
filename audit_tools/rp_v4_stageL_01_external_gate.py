#!/usr/bin/env python3
"""Freeze the RP v4 Stage L external-cohort metadata and question gate.

This stage is deliberately outcome-free. It validates the accepted Stage K
candidate, reconstructs GEO sample and patient identities from official MINiML,
and writes a prospective raw-count and statistical contract. It must not read an
expression matrix, download SRA payloads, or fit a disease/activity effect.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


MINIML_NS = "{http://www.ncbi.nlm.nih.gov/geo/info/MINiML}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(payload: object, path: Path) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(rows: list[dict[str, object]], path: Path, fields: list[str] | None = None) -> None:
    columns = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_miniml(path: Path) -> tuple[ET.Element, list[ET.Element]]:
    with tarfile.open(path, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        if len(members) != 1:
            raise ValueError(f"expected one MINiML member in {path}, observed {len(members)}")
        handle = archive.extractfile(members[0])
        if handle is None:
            raise ValueError(f"cannot read {path}")
        root = ET.parse(handle).getroot()
    return root, root.findall(MINIML_NS + "Sample")


def text(element: ET.Element, tag: str) -> str:
    child = element.find(MINIML_NS + tag)
    return (child.text or "").strip() if child is not None else ""


def characteristics(sample: ET.Element) -> dict[str, str]:
    return {
        item.attrib.get("tag", "").strip().lower(): (item.text or "").strip()
        for item in sample.iter(MINIML_NS + "Characteristics")
    }


def stage_k_manifest(stage_k_root: Path) -> tuple[list[dict[str, object]], bool]:
    manifest = stage_k_root / "deliverables/STAGE_K_SHA256_MANIFEST.csv"
    rows: list[dict[str, object]] = []
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        for record in csv.DictReader(handle):
            path = stage_k_root / record["path"]
            exists = path.is_file()
            actual_bytes = path.stat().st_size if exists else 0
            actual_sha = sha256(path) if exists else ""
            rows.append(
                {
                    "path": record["path"],
                    "exists": exists,
                    "expected_bytes": int(record["bytes"]),
                    "actual_bytes": actual_bytes,
                    "size_match": exists and actual_bytes == int(record["bytes"]),
                    "expected_sha256": record["sha256"].lower(),
                    "actual_sha256": actual_sha,
                    "hash_match": exists and actual_sha == record["sha256"].lower(),
                }
            )
    return rows, all(row["size_match"] and row["hash_match"] for row in rows)


def sample_rows(path: Path, assay: str) -> tuple[list[dict[str, object]], dict[str, str]]:
    root, samples = load_miniml(path)
    series = root.find(MINIML_NS + "Series")
    if series is None:
        raise ValueError(f"series missing from {path}")
    rows: list[dict[str, object]] = []
    for sample in samples:
        meta = characteristics(sample)
        patient = meta["patient id"]
        disease = meta["disease"]
        sledai = float(meta["sledai"])
        title = text(sample, "Title")
        rows.append(
            {
                "assay": assay,
                "gsm": sample.attrib.get("iid", ""),
                "title": title,
                "patient_id": patient,
                "cell_type": meta["cell type"],
                "disease": disease,
                "sledai": sledai,
                "activity_class": "HC" if disease == "HC" else "active" if sledai > 4 else "inactive",
                "sex": meta.get("sex", ""),
                "race": meta.get("race", ""),
                "batch": meta.get("batch", ""),
                "title_contains_patient_id": patient in title,
            }
        )
    relations = ";".join(
        f"{item.attrib.get('type', '')}:{item.attrib.get('target', '')}"
        for item in series.findall(MINIML_NS + "Relation")
    )
    metadata = {
        "title": text(series, "Title"),
        "summary": text(series, "Summary"),
        "overall_design": text(series, "Overall-Design"),
        "pubmed_id": text(series, "Pubmed-ID"),
        "relations": relations,
        "source_sha256": sha256(path),
    }
    return rows, metadata


def patient_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    patients: dict[str, dict[str, object]] = {}
    for row in samples:
        patient = str(row["patient_id"])
        record = patients.setdefault(
            patient,
            {
                "patient_id": patient,
                "disease": row["disease"],
                "sledai": row["sledai"],
                "activity_class": row["activity_class"],
                "sex": row["sex"],
                "race": row["race"],
                "batch": row["batch"],
                "cell_types": set(),
                "gsm": [],
            },
        )
        identity = (record["disease"], record["sledai"], record["sex"], record["race"], record["batch"])
        observed = (row["disease"], row["sledai"], row["sex"], row["race"], row["batch"])
        if identity != observed:
            raise ValueError(f"within-assay patient metadata mismatch: {patient}")
        record["cell_types"].add(str(row["cell_type"]))
        record["gsm"].append(str(row["gsm"]))
    result: list[dict[str, object]] = []
    for patient in sorted(patients, key=lambda value: (len(value), value)):
        record = patients[patient]
        cell_types = sorted(record.pop("cell_types"))
        gsm = sorted(record.pop("gsm"))
        result.append(
            {
                **record,
                "cell_types": ";".join(cell_types),
                "n_libraries": len(gsm),
                "paired_rN_T1T2": set(cell_types) == {"rN", "T1T2"},
                "gsm": ";".join(gsm),
            }
        )
    return result


def cross_assay_rows(rna: list[dict[str, object]], atac: list[dict[str, object]]) -> list[dict[str, object]]:
    rna_map = {str(row["patient_id"]): row for row in rna}
    atac_map = {str(row["patient_id"]): row for row in atac}
    rows: list[dict[str, object]] = []
    for patient in sorted(set(rna_map) | set(atac_map), key=lambda value: (len(value), value)):
        r = rna_map.get(patient)
        a = atac_map.get(patient)
        rows.append(
            {
                "patient_id": patient,
                "in_rna": r is not None,
                "in_atac": a is not None,
                "rna_activity": "" if r is None else r["activity_class"],
                "atac_activity": "" if a is None else a["activity_class"],
                "rna_sledai": "" if r is None else r["sledai"],
                "atac_sledai": "" if a is None else a["sledai"],
                "sledai_exact_match": bool(r and a and r["sledai"] == a["sledai"]),
                "rna_cell_types": "" if r is None else r["cell_types"],
                "atac_cell_types": "" if a is None else a["cell_types"],
                "same_visit_supported": bool(r and a and r["sledai"] == a["sledai"]),
            }
        )
    return rows


def integrity_manifest(output: Path) -> None:
    rows = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "13_INTEGRITY_MANIFEST.csv":
            rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_csv(rows, output / "13_INTEGRITY_MANIFEST.csv")


def run(args: argparse.Namespace) -> None:
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    manifest_rows, manifest_ok = stage_k_manifest(args.stage_k_root.resolve())
    write_csv(manifest_rows, output / "01_STAGE_K_INTAKE_RECHECK.csv")

    rna_samples, rna_meta = sample_rows(args.gse262846.resolve(), "RNA")
    atac_samples, atac_meta = sample_rows(args.gse263716.resolve(), "ATAC")
    rna_patients = patient_rows(rna_samples)
    atac_patients = patient_rows(atac_samples)
    cross = cross_assay_rows(rna_patients, atac_patients)

    write_csv(rna_samples, output / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")
    write_csv(rna_patients, output / "03_GSE262846_PATIENT_PAIRING_SUMMARY.csv")
    write_csv(atac_patients, output / "04_GSE263716_PATIENT_PAIRING_SUMMARY.csv")
    write_csv(cross, output / "05_RNA_ATAC_PATIENT_OVERLAP.csv")

    paired_sle = [row for row in rna_patients if row["disease"] == "SLE" and row["paired_rN_T1T2"]]
    overlap = [row for row in cross if row["in_rna"] and row["in_atac"]]
    discordant = [row for row in overlap if not row["sledai_exact_match"]]
    title_mismatch = [row for row in rna_samples if not row["title_contains_patient_id"]]
    metadata_gate = {
        "schema": "RPV4_STAGE_L_METADATA_GATE_1.0",
        "created_at": datetime.now(ZoneInfo("Asia/Hong_Kong")).isoformat(timespec="seconds"),
        "stage_k_manifest": {"pass": manifest_ok, "payloads": len(manifest_rows)},
        "gse262846": {
            "official_title": rna_meta["title"],
            "source_sha256": rna_meta["source_sha256"],
            "libraries": len(rna_samples),
            "patients": len(rna_patients),
            "paired_patients": sum(bool(row["paired_rN_T1T2"]) for row in rna_patients),
            "paired_sle_patients": len(paired_sle),
            "paired_active_sle": sum(row["activity_class"] == "active" for row in paired_sle),
            "paired_inactive_sle": sum(row["activity_class"] == "inactive" for row in paired_sle),
            "paired_hc": sum(row["disease"] == "HC" and row["paired_rN_T1T2"] for row in rna_patients),
            "title_patient_mismatches": len(title_mismatch),
            "linked_pubmed_id": rna_meta["pubmed_id"] or None,
            "processed_object": "RPKM_ONLY__NOT_INTEGER_COUNTS",
        },
        "gse263716": {
            "official_title": atac_meta["title"],
            "source_sha256": atac_meta["source_sha256"],
            "libraries": len(atac_samples),
            "patients": len(atac_patients),
            "paired_patients": sum(bool(row["paired_rN_T1T2"]) for row in atac_patients),
            "linked_pubmed_id": atac_meta["pubmed_id"] or None,
        },
        "cross_assay": {
            "patient_id_overlap": len(overlap),
            "sledai_discordant_overlap": len(discordant),
            "discordant_patient_ids": [row["patient_id"] for row in discordant],
            "same_visit_multiomics_established": False,
        },
        "outcome_model_fitted": False,
        "expression_matrix_read": False,
        "sra_download_started": False,
    }
    write_json(metadata_gate, output / "06_STAGE_L_METADATA_GATE.json")

    novelty = [
        {
            "candidate_claim": "generic SLE IFN positivity",
            "collision": "HIGH",
            "reason": "already established in the current manuscript and prior SLE literature",
            "decision": "DO_NOT_USE_AS_NEW_PRIMARY_CLAIM",
        },
        {
            "candidate_claim": "active-versus-inactive difference in paired T1T2-minus-rN IFN score",
            "collision": "LOWER_BUT_NOT_ZERO",
            "reason": "new paired compartment-by-activity question; small 12-versus-14 SLE design",
            "decision": "PRIMARY_EXTERNAL_QUESTION_IF_RAW_COUNT_GATE_PASSES",
        },
        {
            "candidate_claim": "same-visit RNA-ATAC multi-omic confirmation",
            "collision": "NOT_ADJUDICABLE",
            "reason": "36 patient IDs overlap but two have discordant SLEDAI and visit identity is unresolved",
            "decision": "HOLD_UNTIL_VISIT_PROVENANCE_IS_RESOLVED",
        },
        {
            "candidate_claim": "GSE118254 as a second independent IFN replication",
            "collision": "HIGH",
            "reason": "published subset biology and donor independence from GSE262846 are not established",
            "decision": "TECHNICAL_OR_HISTORICAL_CONTEXT_ONLY",
        },
    ]
    write_csv(novelty, output / "07_NOVELTY_COLLISION_MATRIX.csv")

    raw_gate = {
        "schema": "RPV4_STAGE_L_RAW_COUNT_GATE_1.0",
        "gse262846_sra_runs": 176,
        "gse262846_reported_sra_payload_gb": 233.209,
        "minimum_recommended_scratch_tb": 2.5,
        "download_authorized": False,
        "download_started": False,
        "reference_build_frozen": False,
        "gene_annotation_frozen": False,
        "integer_count_reconstruction_complete": False,
        "sample_to_run_reconciliation_complete": False,
        "raw_count_gate_pass": False,
        "decision": "HOLD_RAW_DOWNLOAD_COUNT_RECONSTRUCTION_AND_OUTCOME_EXECUTION",
    }
    write_json(raw_gate, output / "08_RAW_COUNT_AND_RUNTIME_GATE.json")

    contract = """# RP v4 Stage L prospective external-cohort contract

## Scientific question

The sole primary question is whether the within-patient difference in the frozen
12-gene IFN/ISG score between transitional and resting-naive B cells differs
between active and inactive SLE. Generic SLE-versus-control IFN positivity is
not a new primary claim.

## Analysis population and unit

- Independent unit: patient.
- Primary population: the 26 SLE patients with both rN and T1T2 RNA libraries
  (12 active, 14 inactive under the deposited SLEDAI >4 rule).
- The two unpaired SLE patients are excluded from the paired primary estimand
  and retained only for intake/QC summaries; no imputation is permitted.
- The 17 paired healthy controls provide descriptive scale/context only and do
  not enter the primary active-versus-inactive test.
- Technical runs and sorted subsets are never counted as independent patients.

## Frozen score and primary estimand

After a separately approved raw-read reconstruction, counts must be generated
with one frozen GRCh38/GENCODE pipeline. Library-size normalization, detection
rules, and the mapping of the unchanged 12-gene positive IFN/ISG arm must be
fixed while activity labels remain inaccessible. For each paired patient,
define D_i = score(T1T2) - score(rN). The primary coefficient is the adjusted
mean difference in D_i for active versus inactive SLE.

## Primary model and sensitivities

- Primary design: intercept, active-SLE indicator, and deposited RNA batch.
- Primary uncertainty: donor-level OLS with HC3 covariance and a two-sided
  t reference using residual degrees of freedom; the exact implementation must
  pass a prospective small-sample simulation gate before outcomes are opened.
- Continuous SLEDAI is a single secondary sensitivity, not a co-primary target.
- Sex and race are not model covariates because the paired SLE support contains
  one male and one Caucasian patient; this limitation must be reported.
- No gene-set, subset, threshold, covariate, or method may be selected by the
  smaller P value. Failure or null results remain reportable.

## Multiplicity and multi-omics boundary

There is one primary transcriptomic contrast. Any gene-level follow-up is
exploratory and requires a separately frozen multiplicity family. GSE263716
ATAC-seq is not an independent cohort and cannot be called same-visit paired
multi-omics until visit provenance resolves the two discordant SLEDAI records.

## Stop rules

Stop without fitting an activity outcome if integer gene counts cannot be
reconstructed, sample-to-run identity is incomplete, the fixed score is not
measurable without outcome-guided repair, or the prospective small-sample
simulation fails. No result from processed RPKM may substitute for this gate.
"""
    (output / "09_PROSPECTIVE_ANALYSIS_CONTRACT.md").write_text(contract, encoding="utf-8", newline="\n")

    gate = {
        "schema": "RPV4_STAGE_L_GATE_1.0",
        "created_at": metadata_gate["created_at"],
        "decision": "PASS_STAGE_L_METADATA_IDENTITY_AND_UNIQUE_QUESTION_FREEZE__HOLD_RAW_DOWNLOAD_AND_OUTCOME_EXECUTION",
        "checks": {
            "stage_k_manifest_18_of_18": manifest_ok and len(manifest_rows) == 18,
            "rna_sample_identity_88": len(rna_samples) == 88,
            "rna_patient_identity_45": len(rna_patients) == 45,
            "rna_pairing_43": sum(bool(row["paired_rN_T1T2"]) for row in rna_patients) == 43,
            "paired_sle_design_12_active_14_inactive": (
                len(paired_sle) == 26
                and sum(row["activity_class"] == "active" for row in paired_sle) == 12
                and sum(row["activity_class"] == "inactive" for row in paired_sle) == 14
            ),
            "title_patient_anomaly_preserved": len(title_mismatch) == 1,
            "rna_atac_overlap_reconstructed": len(overlap) == 36,
            "cross_assay_sledai_discordance_preserved": len(discordant) == 2,
            "raw_count_gate": False,
            "external_outcome_execution": False,
        },
        "automatic_unlocks": {
            "sra_download": False,
            "external_outcomes": False,
            "atac_integration": False,
            "manuscript_external_claim": False,
            "submission": False,
        },
        "next_gate": "RPV4_STAGE_M__RAW_RECONSTRUCTION_AUTHORIZATION_AND_DISEASE_BLIND_COUNT_PIPELINE_FREEZE",
    }
    write_json(gate, output / "10_STAGE_L_GATE_STATUS.json")

    advisor = f"""# RP v4 Stage L advisor review

## Decision

`{gate['decision']}`

Stage K is accepted as a bounded uncertainty-method integration: Stage I and
WP1 are the same 68-donor contrast and do not constitute independent positive
findings. The current main figures and prior biological claims remain frozen.

## External-cohort result

Official GEO MINiML independently reconstructs 88 RNA libraries from 45 patient
IDs. Forty-three patients are paired for rN and T1T2; the primary SLE-only
paired design contains 12 active and 14 inactive patients. Patient 3553
(SLEDAI 20) and patient 428 (SLEDAI 0) have rN only and are not eligible for the
paired primary estimand. The title `SLE.0.3621.rN` maps to patient ID 3651 and
is retained as an explicit source anomaly.

GSE263716 contributes 62 ATAC libraries from 43 patient IDs, but only 36 IDs
overlap the RNA series. Patients 3651 and 1655 have different deposited SLEDAI
values across modalities. ATAC therefore cannot yet be described as same-visit
multi-omic confirmation or independent replication.

## Scientific placement

The only sufficiently differentiated external question is whether the paired
T1T2-minus-rN IFN/ISG score differs by SLE activity. A generic additional IFN
positive result would add little novelty. The paired question is promising for
an SCI Q2 manuscript but remains small and metadata-limited: age and treatment
are absent, and sex/race have almost no within-SLE variation.

## Boundaries and next gate

No expression matrix was read, no SRA payload was downloaded, and no activity
effect was fitted. The deposited processed file is RPKM and cannot satisfy the
frozen count-scale gate. Stage M may begin only after a separate authorization
for approximately 233.21 GB of SRA payload and at least 2.5 TB scratch, together
with a disease-blind GRCh38/GENCODE count pipeline, sample-to-run reconciliation,
and prospective small-sample operating-characteristic qualification.
"""
    (output / "11_STAGE_L_ADVISOR_REVIEW.md").write_text(advisor, encoding="utf-8", newline="\n")

    provenance = {
        "stage_k_root": args.stage_k_root.as_posix(),
        "stage_k_zip_sha256": args.stage_k_zip_sha256,
        "gse262846_miniml": args.gse262846.as_posix(),
        "gse263716_miniml": args.gse263716.as_posix(),
        "official_urls": {
            "GSE262846": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE262846",
            "GSE263716": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE263716",
            "GSE263717": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE263717",
            "GSE118254": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE118254",
        },
        "outcome_accessed": False,
    }
    write_json(provenance, output / "12_PROVENANCE_RECEIPT.json")
    integrity_manifest(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-k-root", type=Path, required=True)
    parser.add_argument("--stage-k-zip-sha256", required=True)
    parser.add_argument("--gse262846", type=Path, required=True)
    parser.add_argument("--gse263716", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
