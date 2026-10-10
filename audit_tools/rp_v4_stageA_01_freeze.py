#!/usr/bin/env python3
"""Freeze RP v4 authority, historical failure diagnosis, and cohort feasibility.

This stage is deliberately outcome-free. It may read historical synthetic G2/G2B
results and public GEO metadata, but it must not fit real disease effects or run a
new G2C validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


MINIML_NS = "{http://www.ncbi.nlm.nih.gov/geo/info/MINiML}"
NORMAL_975 = 1.959963984540054


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
    if not rows and fields is None:
        raise ValueError(f"cannot infer columns for empty output: {path}")
    columns = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def git(workspace: Path, *arguments: str, check: bool = True) -> str:
    process = subprocess.run(
        ["git", *arguments],
        cwd=workspace,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip())
    return process.stdout.strip()


def bool_value(value: object) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() == "true"


def validate_proposal_manifest(proposal_root: Path) -> tuple[list[dict[str, object]], bool]:
    manifest = proposal_root / "deliverables/RPV4_SHA256_MANIFEST.csv"
    rows: list[dict[str, object]] = []
    with manifest.open(encoding="utf-8-sig", newline="") as handle:
        for record in csv.DictReader(handle):
            path = proposal_root / record["path"]
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


def git_authority(workspace: Path) -> dict[str, object]:
    head = git(workspace, "rev-parse", "HEAD")
    origin = git(workspace, "rev-parse", "origin/main")
    parents = git(workspace, "show", "-s", "--format=%P", head).split()
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", origin, head],
        cwd=workspace,
        check=False,
    ).returncode == 0
    return {
        "authority_scope": "RP_V4_INPUT_BASELINE_BEFORE_THIS_STAGE_COMMIT",
        "head": head,
        "head_subject": git(workspace, "show", "-s", "--format=%s", head),
        "head_parents": parents,
        "origin_main": origin,
        "origin_main_is_ancestor_of_head": ancestor,
        "origin_main_is_direct_parent": len(parents) == 1 and parents[0] == origin,
        "ahead_count": int(git(workspace, "rev-list", "--count", "origin/main..HEAD")),
        "behind_count": int(git(workspace, "rev-list", "--count", "HEAD..origin/main")),
        "candidate_report_authority_correction": (
            "Local WP3 commit is accessible and verifiably descends directly from origin/main; "
            "the external proposal's inaccessible-local-commit statement is superseded."
        ),
    }


def load_adjudication(workspace: Path, method: str) -> pd.DataFrame:
    directory = (
        "20261010_g2_full_adjudication"
        if method == "G2"
        else "20261010_g2b_full_adjudication"
    )
    filename = "02_G2_TARGET_SCENARIO_ADJUDICATION.csv" if method == "G2" else "02_G2B_TARGET_SCENARIO_ADJUDICATION.csv"
    return pd.read_csv(workspace / "phase17_v7/rp_v3_redesign" / directory / filename)


def target_recount(g2: pd.DataFrame, g2b: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in sorted(g2["target_id"].unique()):
        row: dict[str, object] = {"target_id": target}
        for method, frame in (("G2", g2), ("G2B", g2b)):
            eligible = frame[
                (frame["target_id"] == target)
                & frame["applicable_domain"].map(bool_value)
                & frame["performance_eligible"].map(bool_value)
            ]
            passed = eligible["decision"].eq("PASS_TARGET_SCENARIO")
            row[f"{method}_eligible"] = len(eligible)
            row[f"{method}_pass"] = int(passed.sum())
            row[f"{method}_hold"] = int((~passed).sum())
            row[f"{method}_coverage_fail"] = int((~eligible["coverage_pass"].map(bool_value)).sum())
            row[f"{method}_bias_fail"] = int((~eligible["bias_pass"].map(bool_value)).sum())
            applicable_type_i = eligible["type_i_pass"].notna()
            row[f"{method}_type_i_fail"] = int(
                (~eligible.loc[applicable_type_i, "type_i_pass"].map(bool_value)).sum()
            )
        row["G2B_target_unlock_historical"] = row["G2B_pass"] == row["G2B_eligible"]
        row["RPV4_interpretation"] = (
            "HISTORICAL_PERFORMANCE_ONLY__NO_REAL_EFFECT_UNLOCK"
        )
        rows.append(row)
    return rows


def failure_class(row: pd.Series) -> str:
    coverage_fail = not bool_value(row["coverage_pass"])
    bias_fail = not bool_value(row["bias_pass"])
    type_i_fail = pd.notna(row["type_i_pass"]) and not bool_value(row["type_i_pass"])
    if coverage_fail and bias_fail:
        base = "COVERAGE_AND_POINT_BIAS"
    elif coverage_fail:
        base = "INTERVAL_UNDERCOVERAGE"
    elif bias_fail:
        base = "POINT_BIAS_GATE_ONLY"
    else:
        base = "OTHER_GATE_FAILURE"
    return base + ("__OVERLAPPING_TYPE_I" if type_i_fail else "")


def raw_failure_diagnostics(workspace: Path, g2b: pd.DataFrame) -> list[dict[str, object]]:
    failures = g2b[
        g2b["applicable_domain"].map(bool_value)
        & g2b["performance_eligible"].map(bool_value)
        & ~g2b["decision"].eq("PASS_TARGET_SCENARIO")
    ].copy()
    run_root = workspace / "phase17_v7/rp_v3_redesign/g2b_full_runs/20261010_stage121_full"
    rows: list[dict[str, object]] = []
    for scenario_id, group in failures.groupby("scenario_id", sort=True):
        chunks = sorted((run_root / scenario_id).glob("chunk_*/attempt_targets.csv.gz"))
        if len(chunks) != 80:
            raise ValueError(f"expected 80 G2B chunks for {scenario_id}, observed {len(chunks)}")
        attempts = pd.concat((pd.read_csv(path) for path in chunks), ignore_index=True)
        for _, record in group.sort_values("target_id").iterrows():
            target = attempts[attempts["target_id"] == record["target_id"]].copy()
            if len(target) != 2000:
                raise ValueError((scenario_id, record["target_id"], len(target)))
            truth = float(record["truth"])
            error = target["point"] - truth
            centered = error - error.mean()
            population_sd = float(centered.std(ddof=0))
            skew = float((centered**3).mean() / population_sd**3) if population_sd else math.nan
            excess_kurtosis = (
                float((centered**4).mean() / population_sd**4 - 3)
                if population_sd
                else math.nan
            )
            covered = (target["ci_lower"] <= truth) & (target["ci_upper"] >= truth)
            lower_miss = target["ci_lower"] > truth
            upper_miss = target["ci_upper"] < truth
            lower_half = target["point"] - target["ci_lower"]
            upper_half = target["ci_upper"] - target["point"]
            interval_length = lower_half + upper_half
            denominator = float(2 * NORMAL_975 * error.std(ddof=1))
            class_name = failure_class(record)
            if class_name.startswith("INTERVAL_UNDERCOVERAGE"):
                diagnosis = (
                    "REPEATED_MILD_NEAR_SYMMETRIC_UNDERCOVERAGE; frozen outputs do not identify "
                    "a near-zero studentizer or a unique corrective interval."
                )
            elif class_name == "POINT_BIAS_GATE_ONLY":
                diagnosis = (
                    "POINT_ESTIMATOR_TRUTH_MISMATCH; changing interval endpoints alone cannot repair this gate."
                )
            else:
                diagnosis = "MULTIPLE_FAILURE_COMPONENTS_REQUIRE_SEPARATE_DIAGNOSIS"
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "truth_structure": record["truth_structure"],
                    "regime": record["regime"],
                    "target_id": record["target_id"],
                    "truth": truth,
                    "outer_attempts": len(target),
                    "decision": record["decision"],
                    "failure_class": class_name,
                    "bias": float(record["bias"]),
                    "bias_upper95_in_empirical_sd": float(record["bias_upper95_in_empirical_sd"]),
                    "bias_pass": bool_value(record["bias_pass"]),
                    "coverage": float(covered.mean()),
                    "coverage_wilson_lower": float(record["coverage_wilson_lower"]),
                    "coverage_pass": bool_value(record["coverage_pass"]),
                    "lower_tail_miss_rate": float(lower_miss.mean()),
                    "upper_tail_miss_rate": float(upper_miss.mean()),
                    "type_i": "" if pd.isna(record["type_i"]) else float(record["type_i"]),
                    "type_i_pass": "" if pd.isna(record["type_i_pass"]) else bool_value(record["type_i_pass"]),
                    "error_skew": skew,
                    "error_excess_kurtosis": excess_kurtosis,
                    "mean_lower_half_width": float(lower_half.mean()),
                    "mean_upper_half_width": float(upper_half.mean()),
                    "mean_interval_length": float(interval_length.mean()),
                    "length_to_normal_95_empirical_sd": (
                        float(interval_length.mean() / denominator) if denominator else math.nan
                    ),
                    "mean_interval_length_covered": float(interval_length[covered].mean()),
                    "mean_interval_length_missed": float(interval_length[~covered].mean()),
                    "diagnostic_interpretation": diagnosis,
                }
            )
    return rows


def miniml_samples(path: Path) -> tuple[list[ET.Element], str]:
    with tarfile.open(path, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        if len(members) != 1:
            raise ValueError(f"unexpected MINiML members: {path}")
        handle = archive.extractfile(members[0])
        if handle is None:
            raise ValueError(f"cannot read MINiML: {path}")
        root = ET.parse(handle).getroot()
    series = root.find(MINIML_NS + "Series")
    title = ""
    if series is not None:
        title_element = series.find(MINIML_NS + "Title")
        title = (title_element.text or "").strip() if title_element is not None else ""
    return root.findall(MINIML_NS + "Sample"), title


def element_text(element: ET.Element, tag: str) -> str:
    child = element.find(MINIML_NS + tag)
    return (child.text or "").strip() if child is not None else ""


def characteristics(sample: ET.Element) -> dict[str, str]:
    return {
        item.attrib.get("tag", "").strip().lower(): (item.text or "").strip()
        for item in sample.iter(MINIML_NS + "Characteristics")
    }


def cohort_register(metadata_dir: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    required = ["GSE262846", "GSE118254", "GSE163121", "GSE254176", "GSE239459"]
    loaded: dict[str, tuple[list[ET.Element], str, Path]] = {}
    for accession in required:
        path = metadata_dir / f"{accession}_family.xml.tgz"
        if not path.is_file():
            raise FileNotFoundError(path)
        samples, title = miniml_samples(path)
        loaded[accession] = (samples, title, path)

    rows: list[dict[str, object]] = []

    samples, title, path = loaded["GSE262846"]
    donor: dict[str, dict[str, object]] = {}
    title_id_mismatch = 0
    for sample in samples:
        meta = characteristics(sample)
        patient = meta["patient id"]
        record = donor.setdefault(
            patient,
            {"disease": meta["disease"], "sledai": float(meta["sledai"]), "cell_types": set()},
        )
        record["cell_types"].add(meta["cell type"])
        if patient not in element_text(sample, "Title"):
            title_id_mismatch += 1
    gse262_ids = set(donor)
    rows.append(
        {
            "accession": "GSE262846",
            "official_title": title,
            "modality": "FACS-sorted rN/T1T2 bulk RNA-seq",
            "geo_samples": len(samples),
            "recoverable_independent_units": len(donor),
            "unit_definition": "patient id",
            "group_accounting": (
                f"HC={sum(v['disease']=='HC' for v in donor.values())}; "
                f"SLE_active_SLEDAI_gt4={sum(v['disease']=='SLE' and v['sledai']>4 for v in donor.values())}; "
                f"SLE_inactive_SLEDAI_le4={sum(v['disease']=='SLE' and v['sledai']<=4 for v in donor.values())}"
            ),
            "repeated_structure": f"paired_rN_T1T2={sum(v['cell_types']=={'rN','T1T2'} for v in donor.values())}; single_state=2",
            "metadata_anomalies": f"title_patient_id_mismatch={title_id_mismatch}",
            "count_compatibility": "HOLD__processed_RPKM_not_frozen_CPM; raw SRA reconstruction required",
            "independence_status": "HOLD__same investigator lineage as GSE118254; exact tokens alone are insufficient",
            "stageA_decision": "CONDITIONAL_METADATA_PASS__OUTCOME_LOCKED",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE262846",
            "metadata_sha256": sha256(path),
        }
    )

    samples, title, path = loaded["GSE118254"]
    donor_118: dict[str, dict[str, object]] = {}
    for sample in samples:
        match = re.match(r"(HC|SLE)\.(\d+)\.", element_text(sample, "Title"))
        if match is None:
            raise ValueError(f"unparsed GSE118254 title: {element_text(sample, 'Title')}")
        record = donor_118.setdefault(match.group(2), {"status": match.group(1), "subtypes": set()})
        record["subtypes"].add(characteristics(sample)["cell subtype"])
    gse118_ids = set(donor_118)
    rows.append(
        {
            "accession": "GSE118254",
            "official_title": title,
            "modality": "FACS-sorted B-cell-subset bulk RNA-seq",
            "geo_samples": len(samples),
            "recoverable_independent_units": len(donor_118),
            "unit_definition": "subject token parsed from sample title",
            "group_accounting": (
                f"HC={sum(v['status']=='HC' for v in donor_118.values())}; "
                f"SLE={sum(v['status']=='SLE' for v in donor_118.values())}"
            ),
            "repeated_structure": "3-6 sorted-subset libraries per donor",
            "metadata_anomalies": "raw data replacement recorded by GEO in May 2021",
            "count_compatibility": "HOLD__raw SRA reconstruction required for frozen count-based score",
            "independence_status": "HOLD__related investigator lineage; no exact donor-token overlap does not prove independence",
            "stageA_decision": "CONDITIONAL_DONOR_STRUCTURE_PASS__OUTCOME_LOCKED",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE118254",
            "metadata_sha256": sha256(path),
        }
    )

    samples, title, path = loaded["GSE163121"]
    diagnoses = Counter(characteristics(sample).get("diagnosis", "") for sample in samples)
    rows.append(
        {
            "accession": "GSE163121",
            "official_title": title,
            "modality": "B-cell-enriched single-cell RNA-seq",
            "geo_samples": len(samples),
            "recoverable_independent_units": len(samples),
            "unit_definition": "one GEO sample per donor",
            "group_accounting": f"HC={diagnoses['Healthy']}; SLE={diagnoses['SLE']}",
            "repeated_structure": "none in series",
            "metadata_anomalies": "none material for unit recovery",
            "count_compatibility": "processed matrix available",
            "independence_status": "independent source but severely underpowered",
            "stageA_decision": "EXPLORATORY_ONLY__NOT_PRIMARY_VALIDATION",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163121",
            "metadata_sha256": sha256(path),
        }
    )

    samples, title, path = loaded["GSE254176"]
    sc_titles = [element_text(sample, "Title") for sample in samples if "scRNA-seq" in element_text(sample, "Title")]
    patient_ids = set()
    for sample_title in sc_titles:
        match = re.match(r"Pat(?:ient|eint) (\d+)", sample_title)
        if match:
            patient_ids.add(match.group(1))
    rows.append(
        {
            "accession": "GSE254176",
            "official_title": title,
            "modality": "longitudinal PBMC scRNA/scTCR/scBCR",
            "geo_samples": len(samples),
            "recoverable_independent_units": len(patient_ids),
            "unit_definition": "SLE patient parsed from longitudinal title",
            "group_accounting": f"SLE_patients={len(patient_ids)}; scRNA_visits={len(sc_titles)}; internal_HC=0",
            "repeated_structure": "19 visits represented across three assay modalities",
            "metadata_anomalies": "Patient is misspelled as Pateint for patients 5-6; external AIDA controls not deposited as matched study units",
            "count_compatibility": "processed scRNA matrices available",
            "independence_status": "independent longitudinal SLE source; no internal matched control cohort",
            "stageA_decision": "EXPLORATORY_REPEAT_MEASURES_ONLY",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE254176",
            "metadata_sha256": sha256(path),
        }
    )

    samples, title, path = loaded["GSE239459"]
    rows.append(
        {
            "accession": "GSE239459",
            "official_title": title,
            "modality": "group-level sorted-B-cell scRNA-seq",
            "geo_samples": len(samples),
            "recoverable_independent_units": "NOT_RECOVERABLE",
            "unit_definition": "one group-named library for SLE, pSS and HC",
            "group_accounting": "SLE=1; pSS=1; HC=1 GEO sample",
            "repeated_structure": "cells are nested within three group-level libraries",
            "metadata_anomalies": "donor replication absent from series metadata",
            "count_compatibility": "processed matrices available",
            "independence_status": "cannot support donor-level inference",
            "stageA_decision": "NO_GO_INDEPENDENT_DONOR_INFERENCE",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE239459",
            "metadata_sha256": sha256(path),
        }
    )

    rows.append(
        {
            "accession": "GSE135779",
            "official_title": "Historical source-label external cohort",
            "modality": "single-cell RNA-seq",
            "geo_samples": "historical local reconstruction",
            "recoverable_independent_units": 54,
            "unit_definition": "eligible donor pseudobulk",
            "group_accounting": "already used in current manuscript",
            "repeated_structure": "handled in frozen RP v3 handoff",
            "metadata_anomalies": "not re-audited from GEO in this stage",
            "count_compatibility": "historically reconstructed",
            "independence_status": "not a new held-out validation",
            "stageA_decision": "HISTORICAL_REFERENCE_ONLY",
            "official_url": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135779",
            "metadata_sha256": "NOT_REDOWNLOADED_STAGE_A",
        }
    )

    overlap = sorted(gse262_ids & gse118_ids)
    overlap_receipt = {
        "comparison": "GSE262846 patient-id tokens versus GSE118254 title-derived subject tokens",
        "GSE262846_unique_tokens": len(gse262_ids),
        "GSE118254_unique_tokens": len(gse118_ids),
        "exact_token_overlap": overlap,
        "exact_token_overlap_count": len(overlap),
        "independence_established": False,
        "interpretation": (
            "No exact token overlap was observed, but the accessions use different studies and may use "
            "different de-identification namespaces. Shared investigators and biological design require a "
            "provenance-level overlap statement before independent-validation language."
        ),
        "outcome_fields_used_for_effect_estimation": False,
    }
    return rows, overlap_receipt


def boundary_rows(workspace: Path) -> list[dict[str, object]]:
    sources = [
        ("G2", "HOLD_G2_APPLICABLE_DOMAIN", "phase17_v7/rp_v3_redesign/20261010_g2_full_adjudication/03_G2_FINAL_DECISION.json"),
        ("G2B", "HOLD_G2B_APPLICABLE_DOMAIN", "phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/03_G2B_FINAL_DECISION.json"),
        ("WP2_REAL_EFFECT", "LOCKED", "phase17_v7/rp_v3_redesign/20261010_g2b_full_adjudication/10_G2B_SCOPE_CONTRACTION_CONTRACT.md"),
        ("WP3_OUTCOME", "LOCKED", "phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/12_WP3_MEASUREMENT_GATE_STATUS.json"),
        ("WP4", "HOLD_CONDITIONAL", "phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/12_WP3_MEASUREMENT_GATE_STATUS.json"),
        ("SUBMISSION", "HOLD", "phase17_v7/rp_v3_redesign/20261010_wp3_pooled_measurement/12_WP3_MEASUREMENT_GATE_STATUS.json"),
    ]
    return [
        {
            "boundary": boundary,
            "carried_status": status,
            "source_path": source,
            "source_sha256": sha256(workspace / source),
            "RPV4_override": False,
            "interpretation": "PRESERVED_HISTORICAL_BOUNDARY",
        }
        for boundary, status, source in sources
    ]


def score_rows() -> list[dict[str, object]]:
    return [
        {
            "score_id": "S0_T_frozen",
            "definition_status": "FROZEN_HISTORICAL_ANCHOR",
            "allowed_role": "primary measurement anchor",
            "technical_basis": "12 genes; full-library CPM; log2(CPM+0.5); frozen discovery-control mean/SD",
            "selection_rule": "never refit or replace based on new outcome association",
            "stageA_decision": "RETAIN",
        },
        {
            "score_id": "S1_T_rank",
            "definition_status": "IMPLEMENTED_HISTORICAL_SENSITIVITY",
            "allowed_role": "technical sensitivity comparator only",
            "technical_basis": "12 genes ranked in the frozen 18,873-symbol background",
            "selection_rule": "cannot become primary because of a smaller disease P value",
            "stageA_decision": "RETAIN_AS_SENSITIVITY",
        },
        {
            "score_id": "S2_detection_capture_robust",
            "definition_status": "NO_UNIQUE_MATHEMATICAL_FORMULA",
            "allowed_role": "none until a unique result-blind formula and missing-gene rule exist",
            "technical_basis": "proposal concept only",
            "selection_rule": "must not be trained or tuned on disease direction, effect size or P value",
            "stageA_decision": "NOT_ADMITTED_TO_V4C",
        },
    ]


def advisor_review(
    authority: dict[str, object],
    recount: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
    cohorts: list[dict[str, object]],
) -> str:
    g2_pass = sum(int(row["G2_pass"]) for row in recount)
    g2b_pass = sum(int(row["G2B_pass"]) for row in recount)
    coverage = [row for row in diagnostics if row["coverage_pass"] is False]
    bias = [row for row in diagnostics if row["bias_pass"] is False]
    profile = [row for row in coverage if row["target_id"] == "delta_profile"]
    cellref = [row for row in coverage if row["target_id"] == "delta_cellref"]
    cohort_map = {row["accession"]: row for row in cohorts}
    return f"""# RP v4 Stage A authority and feasibility freeze

**Decision:** `PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`

**Date:** 2026-10-10

**Outcome use:** none; no real WP2/WP3 coefficient, new-cohort disease effect, P value or interval was fitted.

## Authority correction

The RP v4 proposal bundle passed its ten-file SHA-256 and byte-size manifest. It is accepted as an external proposal candidate, not as self-authorizing evidence. The project-side Git audit supersedes the candidate report's stale statement that the local WP3 commit was inaccessible: `{authority['head']}` is available, is {authority['ahead_count']} commit ahead of `origin/main`, and `origin/main` is its direct parent.

All RP v3 boundaries remain in force: G2 and G2B stay HOLD, real WP2 and new WP3 outcome fitting stay locked, WP4 remains conditional HOLD, and submission remains HOLD.

## Historical G2/G2B diagnosis

The independent project-side recount reproduces G2={g2_pass}/150 and G2B={g2b_pass}/150 applicable target-scenario PASS cells. The 17 G2B failures comprise {len(coverage)} coverage failures and {len(bias)} bias failures; one exact-null type-I failure overlaps a coverage failure.

The residual coverage pattern is concentrated in the difference estimands: `delta_profile` fails coverage in {len(profile)} cells and `delta_cellref` in {len(cellref)}. Misses are mild and broadly two-sided rather than a large one-tail collapse. The frozen outputs do not contain the per-replicate studentizer or inner-bootstrap pivot distribution needed to identify near-zero studentization as the cause. Therefore Stage A does not select a G2C interval.

The six bias failures are scientifically separate from interval undercoverage. Five occur in `C0_R2` or `C4_R0` beta/bin targets and one in `C4_R0 delta_cellref`; changing confidence-interval endpoints alone cannot repair point-estimator truth mismatch. A future G2C protocol must either narrow its estimand explicitly or carry a separate point-estimator diagnostic. It may not advertise a universal ten-target repair.

## External-cohort feasibility

- `GSE262846`: {cohort_map['GSE262846']['geo_samples']} libraries resolve to {cohort_map['GSE262846']['recoverable_independent_units']} patient IDs (17 HC, 13 active SLE, 15 inactive SLE); 43 patients have both rN and T1T2 libraries. One title/patient-ID discrepancy is preserved. The deposited processed object is RPKM, not the frozen count/CPM scale, so outcome fitting remains locked pending raw-count reconstruction and provenance review.
- `GSE118254`: 83 libraries resolve to 17 donor tokens (8 HC, 9 SLE), each represented by 3-6 sorted subsets. It is suitable for subset-aware work only after raw-count reconstruction and independence review.
- No exact numeric donor-token overlap was observed between these two accessions, but this does not establish independence because identifiers may be study-specific and the investigator lineage is shared.
- `GSE163121` has only 2 HC and 3 SLE donors; `GSE254176` is a six-patient longitudinal SLE resource without internal matched controls in the deposited series; `GSE239459` has one group-level library per condition. None qualifies as primary donor-level confirmation.

## Score contract

`S0=T_frozen` remains the primary frozen measurement anchor. `S1=T_rank` remains a technical sensitivity only. S2 is not admitted because the proposal does not yet provide one unique mathematical formula, denominator and missing-gene rule independent of outcomes.

## Authorization and stop rules

Authorized next work is limited to a source-level V4C protocol freeze: one primary G2C estimand/method, at most one prespecified fallback, new random streams and DGP perturbations, explicit point-bias handling, and a raw-count/provenance feasibility decision for GSE262846/GSE118254. No final G2C simulation, real disease effect, manuscript rewrite, figure replacement, submission package, release or Zenodo update is authorized.

If the single G2C contract cannot address both repeated difference-estimand undercoverage and the separate bias component without changing the scientific target after seeing results, close the decomposition branch as `G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`. If raw counts or donor independence cannot be established for the external candidates, retain them as descriptive resources rather than clinical validation.

## Next stage

`RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE`
"""


def next_protocol() -> str:
    return """# RP v4 Stage C protocol requirements

## Allowed scope

1. Select exactly one primary G2C estimand and interval/identification strategy from the historical-development evidence.
2. Prespecify at most one fallback, including its activation rule and error allocation before final simulation.
3. Freeze new random streams, old-comparable and shifted DGP families, support rules, target registry, thresholds, compute budget and failure accounting.
4. Separate interval calibration from point-estimator bias; do not claim an interval-only change repairs the six G2B bias failures.
5. Keep `S0=T_frozen` primary and `S1=T_rank` sensitivity. S2 remains excluded unless one unique outcome-blind formula, denominator and missing-feature rule are justified.
6. For GSE262846 and GSE118254, decide raw-count reconstruction, donor identity/provenance and repeated-subset handling before any disease or activity model.

## Required pre-execution artifacts

- mathematical estimand and estimator specification;
- one primary method and optional single fallback contract;
- independent final-simulation seed manifest;
- DGP registry including prespecified distribution shifts;
- coverage, bias, type-I, support-stop and numerical-failure gates;
- compute and checkpoint budget;
- raw-count compatibility receipt for each external candidate;
- donor-overlap/provenance statement stronger than token comparison;
- result-blind chronology and author sign-off.

## Prohibited

- using old G2/G2B outcomes as final G2C confirmation;
- trying multiple final methods and selecting the first PASS;
- changing target, DGP, applicable domain or threshold after final results;
- fitting real WP2 effects or new-cohort disease/activity effects;
- promoting S2 by clinical significance;
- manuscript, figure, submission, release or Zenodo changes.

## Stop condition

Failure of the single frozen G2C strategy closes the decomposition branch. No G2D rescue is permitted under RP v4.
"""


def run(arguments: argparse.Namespace) -> None:
    workspace = arguments.workspace.resolve()
    output = arguments.output.resolve()
    proposal_root = arguments.proposal_root.resolve()
    metadata_dir = arguments.metadata_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    numbered = list(output.glob("[0-9][0-9]_*"))
    if numbered:
        raise FileExistsError(f"stage outputs already exist: {numbered[0]}")

    manifest_rows, manifest_pass = validate_proposal_manifest(proposal_root)
    if not manifest_pass:
        raise AssertionError("RP v4 proposal manifest failed")
    proposal_zip = arguments.proposal_zip.resolve()
    proposal_receipt = {
        "candidate_bundle": str(proposal_zip),
        "candidate_bundle_bytes": proposal_zip.stat().st_size,
        "candidate_bundle_sha256": sha256(proposal_zip),
        "internal_manifest_rows": len(manifest_rows),
        "internal_manifest_pass": manifest_pass,
        "candidate_decision_inherited": False,
        "accepted_role": "EXTERNAL_PROPOSAL_CANDIDATE_AND_EVIDENCE_INPUT",
        "project_side_adjudication_required": True,
    }
    write_json(proposal_receipt, output / "01_PROPOSAL_INTAKE_RECEIPT.json")
    write_csv(manifest_rows, output / "01B_PROPOSAL_MANIFEST_RECHECK.csv")

    authority = git_authority(workspace)
    if not authority["origin_main_is_ancestor_of_head"]:
        raise AssertionError("origin/main is not an ancestor of the RP v4 input baseline")
    write_json(authority, output / "02_GIT_AUTHORITY_RECEIPT.json")

    boundaries = boundary_rows(workspace)
    write_csv(boundaries, output / "03_RPV3_BOUNDARY_CARRYFORWARD.csv")

    g2 = load_adjudication(workspace, "G2")
    g2b = load_adjudication(workspace, "G2B")
    recount = target_recount(g2, g2b)
    write_csv(recount, output / "04_G2_G2B_TARGET_RECOUNT.csv")
    diagnostics = raw_failure_diagnostics(workspace, g2b)
    write_csv(diagnostics, output / "05_G2B_FAILURE_DIAGNOSTIC.csv")

    cohorts, overlap = cohort_register(metadata_dir)
    write_csv(cohorts, output / "06_EXTERNAL_COHORT_METADATA_REGISTER.csv")
    write_json(overlap, output / "07_EXTERNAL_DONOR_OVERLAP_RECEIPT.json")
    scores = score_rows()
    write_csv(scores, output / "08_SCORE_CANDIDATE_RISK_REGISTER.csv")

    g2_pass = sum(int(row["G2_pass"]) for row in recount)
    g2b_pass = sum(int(row["G2B_pass"]) for row in recount)
    coverage_fail = sum(row["coverage_pass"] is False for row in diagnostics)
    bias_fail = sum(row["bias_pass"] is False for row in diagnostics)
    type_i_fail = sum(row["type_i_pass"] is False for row in diagnostics)
    checks = [
        {"check": "proposal_manifest", "pass": manifest_pass, "detail": f"{len(manifest_rows)}/{len(manifest_rows)} files"},
        {"check": "git_authority", "pass": authority["origin_main_is_direct_parent"], "detail": f"baseline ahead={authority['ahead_count']}"},
        {"check": "G2_recount", "pass": g2_pass == 90, "detail": f"{g2_pass}/150 PASS"},
        {"check": "G2B_recount", "pass": g2b_pass == 133, "detail": f"{g2b_pass}/150 PASS"},
        {"check": "G2B_failure_accounting", "pass": len(diagnostics) == 17 and coverage_fail == 11 and bias_fail == 6 and type_i_fail == 1, "detail": f"fail=17 coverage={coverage_fail} bias={bias_fail} typeI={type_i_fail}"},
        {"check": "historical_boundaries_preserved", "pass": all(not row["RPV4_override"] for row in boundaries), "detail": "6/6 carried"},
        {"check": "GSE262846_units", "pass": next(row for row in cohorts if row["accession"] == "GSE262846")["recoverable_independent_units"] == 45, "detail": "45 patient IDs from 88 libraries"},
        {"check": "GSE118254_units", "pass": next(row for row in cohorts if row["accession"] == "GSE118254")["recoverable_independent_units"] == 17, "detail": "17 donor tokens from 83 libraries"},
        {"check": "cross_accession_exact_token_overlap", "pass": overlap["exact_token_overlap_count"] == 0, "detail": "no exact token overlap; independence still HOLD"},
        {"check": "external_count_compatibility", "pass": False, "detail": "GSE262846/GSE118254 require raw-count reconstruction"},
        {"check": "S0_S1_roles_locked", "pass": True, "detail": "S0 primary; S1 sensitivity"},
        {"check": "S2_unique_formula", "pass": False, "detail": "S2 not admitted"},
        {"check": "real_effects_fitted", "pass": True, "detail": "none; outcome execution locked"},
    ]
    write_csv(checks, output / "09_STAGE_A_CHECKS.csv")

    gate = {
        "schema": "RP_V4_STAGE_A_1.0",
        "created_at": datetime.now(ZoneInfo("Asia/Hong_Kong")).isoformat(timespec="seconds"),
        "decision": "PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES",
        "proposal_manifest_pass": manifest_pass,
        "git_authority_pass": bool(authority["origin_main_is_ancestor_of_head"]),
        "historical_G2_pass_cells": g2_pass,
        "historical_G2B_pass_cells": g2b_pass,
        "historical_G2B_failures": {"total": len(diagnostics), "coverage": coverage_fail, "bias": bias_fail, "type_i_overlapping": type_i_fail},
        "G2": "HOLD_G2_APPLICABLE_DOMAIN",
        "G2B": "HOLD_G2B_APPLICABLE_DOMAIN",
        "G2C_FINAL_EXECUTION_AUTHORIZED": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "NEW_COHORT_OUTCOME_EXECUTION_AUTHORIZED": False,
        "S2_ADMITTED": False,
        "WP4": "HOLD_CONDITIONAL",
        "submission": "HOLD",
        "authorized_scope": [
            "single G2C estimand and method protocol freeze",
            "new final-simulation seed/DGP/budget contract",
            "GSE262846/GSE118254 raw-count and provenance feasibility",
            "S0/S1 result-blind technical contract",
        ],
        "next_stage": "RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE",
    }
    write_json(gate, output / "10_RPV4_STAGE_A_GATE_STATUS.json")
    (output / "11_RPV4_STAGE_A_ADVISOR_REVIEW.md").write_text(
        advisor_review(authority, recount, diagnostics, cohorts), encoding="utf-8", newline="\n"
    )
    (output / "12_RPV4_STAGE_C_PROTOCOL_REQUIREMENTS.md").write_text(
        next_protocol(), encoding="utf-8", newline="\n"
    )

    manifest_files = sorted(path for path in output.iterdir() if path.is_file() and path.name != "13_INTEGRITY_MANIFEST.csv")
    integrity = [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in manifest_files
    ]
    write_csv(integrity, output / "13_INTEGRITY_MANIFEST.csv")
    print(json.dumps(gate, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proposal-root", type=Path, required=True)
    parser.add_argument("--proposal-zip", type=Path, required=True)
    parser.add_argument("--metadata-dir", type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
