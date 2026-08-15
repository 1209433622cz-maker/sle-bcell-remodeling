#!/usr/bin/env python3
"""Build and audit the Gate C6A manuscript claim freeze."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SOURCE_FILES = {
    "c2b4": Path(
        "phase17_v7/gateC2B4/20260815_two_level_state_repair/"
        "06_GATE_C2B4_ADVISOR_DECISION.json"
    ),
    "c3a": Path(
        "phase17_v7/gateC3A/20260815_frozen_abundance/"
        "09_GATE_C3A_ADVISOR_DECISION.json"
    ),
    "c4b": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/"
        "15_GATE_C4B_ADVISOR_DECISION.json"
    ),
    "c5b": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/"
        "17_GATE_C5B_ADVISOR_DECISION.json"
    ),
    "c5b_programs": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/"
        "07_PROGRAM_RESULTS.csv"
    ),
}

DOCUMENT_FILES = [
    Path("01_manuscript/manuscript_v8_gateC6A_claim_integrated_2026-08-15.md"),
    Path("01_manuscript/research_proposal_v15_gateC6A_integrated_2026-08-15.md"),
    Path("01_manuscript/figure4_gateC5B_legend_draft_2026-08-15.md"),
    Path("04_submission/figure_architecture_v8_gateC6A_2026-08-15.md"),
    Path("00_project_management/gateC6B_regulatory_evidence_freeze_contract_2026-08-15.md"),
    Path("00_project_management/action_record_2026-08-15_gateC6A_claim_integration.md"),
    Path("00_project_management/next_stage_decision_2026-08-15_gateC6B.md"),
]

ADDITIONAL_ARTIFACTS = [
    (Path(".gitignore"), "tracked"),
    (Path("audit_tools/phase17_c6a_01_integrate_claims.py"), "tracked"),
    (Path("audit_tools/phase17_c6b_00_inventory_resources.py"), "tracked"),
    (
        Path(
            "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/"
            "01_COLLECTRI_RESOURCE_METADATA.json"
        ),
        "tracked",
    ),
    (
        Path(
            "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/"
            "02_REGULATOR_TARGET_COVERAGE.csv"
        ),
        "tracked",
    ),
    (
        Path(
            "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/"
            "03_RESOURCE_INVENTORY.md"
        ),
        "tracked",
    ),
    (
        Path(
            "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/"
            "04_CONTRAST_REGULATOR_COVERAGE.csv"
        ),
        "tracked",
    ),
    (
        Path(
            "phase17_v7/gateC6B/20260815_pre_effect_resource_freeze/resources/"
            "collectri_human_omnipath_20260815.tsv.gz"
        ),
        "local_recomputable",
    ),
]

EXPECTED_DECISIONS = {
    "c2b4": "PASS_C2B4_TWO_COMPARTMENT_FREEZE_OUTCOME_UNLOCK_AUTHORIZED",
    "c3a": "NO_GO_C3A_COMPOSITION_AS_CENTRAL_CLAIM",
    "c4b": "PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION",
    "c5b": "PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("phase17_v7/gateC6A/20260815_claim_integration"),
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def program_by_id(c4b: dict[str, Any], program_id: str) -> dict[str, Any]:
    matches = [
        row for row in c4b["confirmatory_programs"] if row["program_id"] == program_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one C4B program {program_id}, found {len(matches)}")
    return matches[0]


def external_program(
    rows: list[dict[str, str]], analysis_name: str, program_id: str
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["analysis_name"] == analysis_name and row["program_id"] == program_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one C5B row for {analysis_name}/{program_id}, found {len(matches)}"
        )
    return matches[0]


def format_num(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    out_dir = args.out_dir
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    source_paths = {key: root / value for key, value in SOURCE_FILES.items()}
    missing_sources = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing_sources:
        raise FileNotFoundError(f"Missing frozen sources: {missing_sources}")

    data = {key: read_json(source_paths[key]) for key in EXPECTED_DECISIONS}
    c5_programs = read_csv(source_paths["c5b_programs"])
    decision_checks = {
        key: data[key].get("decision") == expected
        for key, expected in EXPECTED_DECISIONS.items()
    }
    if not all(decision_checks.values()):
        raise ValueError(f"Frozen decision mismatch: {decision_checks}")

    c2b4 = data["c2b4"]
    c3a = data["c3a"]
    c4b = data["c4b"]
    c5b = data["c5b"]
    c4_ifn = program_by_id(c4b, "IFN_ISG")
    c4_naive = program_by_id(c4b, "NAIVE_TO_MEMORY_AXIS")
    c4_apc = program_by_id(c4b, "APC_HLA")
    c4_atypical = program_by_id(c4b, "ATYPICAL_LOW_NAIVE_AXIS")
    c5_atypical = external_program(
        c5_programs, "childhood_min50", "ATYPICAL_LOW_NAIVE_AXIS"
    )

    claim_rows = [
        {
            "claim_id": "C6A-01",
            "tier": "foundation",
            "claim": "Disease-blind reconstruction supports B_CONV and B_ASC as broad identity compartments.",
            "status": "authorized",
            "evidence": (
                f"20/20 resamples; minimum mapped ARI "
                f"{c2b4['two_compartment_metrics']['minimum_mapped_ari']:.3f}; "
                f"minimum state median Jaccard "
                f"{c2b4['two_compartment_metrics']['minimum_state_median_jaccard']:.3f}."
            ),
            "analysis_unit": "cell graph for identity; sample support for markers",
            "source": SOURCE_FILES["c2b4"].as_posix(),
            "allowed_wording": "broad conventional-B compartment; antibody-secreting compartment",
            "prohibited_wording": "hard naive/memory subtype; disease-defined subtype",
            "manuscript_location": "Results 1; Figure 1",
        },
        {
            "claim_id": "C6A-02",
            "tier": "negative_boundary",
            "claim": "Five-, four- and three-state hard identity models were not stable enough to publish.",
            "status": "required_negative_result",
            "evidence": "Gate C2B3 HOLD preserved by C2B4; naive-memory retained as a continuous axis.",
            "analysis_unit": "20 disease-blind graph resamples",
            "source": "phase17_v7/gateC2B3/20260813_full_neutral_state_freeze/16_GATE_C2B3_ADVISOR_REVIEW.json",
            "allowed_wording": "fine-grained identity was unstable",
            "prohibited_wording": "C2B4 validated the original five clusters",
            "manuscript_location": "Results 1; Methods; Discussion",
        },
        {
            "claim_id": "C6A-03",
            "tier": "secondary",
            "claim": "B_ASC relative abundance is not a central SLE-control finding.",
            "status": "authorized_secondary_only",
            "evidence": (
                f"Primary OR {c3a['primary']['odds_ratio']:.3f}, 95% CI "
                f"{c3a['primary']['ci_low']:.3f}-{c3a['primary']['ci_high']:.3f}, "
                f"P={c3a['primary']['p_value']:.3f}; flare q="
                f"{c3a['secondary_flare']['bh_q_across_three_frozen_contrasts']:.3f}."
            ),
            "analysis_unit": "sample-cohort stratum",
            "source": SOURCE_FILES["c3a"].as_posix(),
            "allowed_wording": "secondary compositional context; no primary B_ASC difference",
            "prohibited_wording": "B_ASC expansion is a central replicated result",
            "manuscript_location": "Results 2; Figure 2 or Extended Data",
        },
        {
            "claim_id": "C6A-04",
            "tier": "central",
            "claim": "SLE is associated with an IFN/ISG transcriptional shift within GSE174188 B_CONV.",
            "status": "authorized",
            "evidence": (
                f"Primary effect {c4_ifn['primary_effect']:.3f}, 95% CI "
                f"{c4_ifn['primary_ci'][0]:.3f}-{c4_ifn['primary_ci'][1]:.3f}, "
                f"four-program BH q={c4_ifn['primary_q']:.3g}."
            ),
            "analysis_unit": "sample-cohort B_CONV pseudobulk",
            "source": SOURCE_FILES["c4b"].as_posix(),
            "allowed_wording": "SLE-associated within-compartment IFN remodeling",
            "prohibited_wording": "IFN causes the B-cell state",
            "manuscript_location": "Results 3; Figure 3",
        },
        {
            "claim_id": "C6A-05",
            "tier": "central_support",
            "claim": "The GSE174188 IFN result is internally reproducible across a donor-nonoverlap contrast.",
            "status": "authorized",
            "evidence": (
                f"Full internal effect {c4_ifn['validation_full_effect']:.3f}, q="
                f"{c4_ifn['validation_full_q']:.3g}; donor-nonoverlap effect "
                f"{c4_ifn['validation_nonoverlap_effect']:.3f}, q="
                f"{c4_ifn['validation_nonoverlap_q']:.3g}."
            ),
            "analysis_unit": "sample-cohort B_CONV pseudobulk",
            "source": SOURCE_FILES["c4b"].as_posix(),
            "allowed_wording": "internal replication within GSE174188",
            "prohibited_wording": "independent external cohort",
            "manuscript_location": "Results 3; Figure 3",
        },
        {
            "claim_id": "C6A-06",
            "tier": "central",
            "claim": "The frozen IFN/ISG program replicates independently in GSE135779.",
            "status": "authorized",
            "evidence": (
                f"Childhood effect {c5b['ifn_results']['childhood_min50']['effect']:.3f}, "
                f"95% CI {c5b['ifn_results']['childhood_min50']['ci_low']:.3f}-"
                f"{c5b['ifn_results']['childhood_min50']['ci_high']:.3f}, q="
                f"{c5b['ifn_results']['childhood_min50']['q_value_primary4']:.3g}; "
                f"combined effect {c5b['ifn_results']['combined_min50']['effect']:.3f}, q="
                f"{c5b['ifn_results']['combined_min50']['q_value_primary4']:.3g}."
            ),
            "analysis_unit": "donor-level broad conventional-B pseudobulk",
            "source": SOURCE_FILES["c5b"].as_posix(),
            "allowed_wording": "independently replicated IFN/ISG program",
            "prohibited_wording": "independently replicated B-cell subtype",
            "manuscript_location": "Results 4; Figure 4",
        },
        {
            "claim_id": "C6A-07",
            "tier": "boundary",
            "claim": "The adult GSE135779 estimate is directionally compatible but not confirmatory.",
            "status": "authorized_directional_only",
            "evidence": (
                f"Adult n=11 donors; effect {c5b['ifn_results']['adult_min50']['effect']:.3f}, "
                f"95% CI {c5b['ifn_results']['adult_min50']['ci_low']:.3f}-"
                f"{c5b['ifn_results']['adult_min50']['ci_high']:.3f}, q="
                f"{c5b['ifn_results']['adult_min50']['q_value_primary4']:.3f}."
            ),
            "analysis_unit": "donor-level broad conventional-B pseudobulk",
            "source": SOURCE_FILES["c5b"].as_posix(),
            "allowed_wording": "positive but underpowered adult estimate",
            "prohibited_wording": "adult replication confirmed",
            "manuscript_location": "Results 4; Discussion; Figure 4",
        },
        {
            "claim_id": "C6A-08",
            "tier": "boundary",
            "claim": "Cross-dataset agreement is IFN-program-specific, not transcriptome-wide.",
            "status": "required_boundary",
            "evidence": (
                f"Shared tested-gene Spearman rho "
                f"{c5b['cross_dataset_context']['shared_tested_gene_rho']:.3f}; "
                f"{c5b['cross_dataset_context']['shared_tested_ifn_genes']} shared tested IFN genes, "
                f"all positive in both datasets."
            ),
            "analysis_unit": "shared tested genes across two datasets",
            "source": SOURCE_FILES["c5b"].as_posix(),
            "allowed_wording": "program-specific replication despite genome-wide heterogeneity",
            "prohibited_wording": "global transcriptomic concordance",
            "manuscript_location": "Results 4; Discussion; Figure 4",
        },
        {
            "claim_id": "C6A-09",
            "tier": "supporting_internal",
            "claim": "Naive-to-memory and APC/HLA are supporting GSE174188 axes, not external replications.",
            "status": "authorized_supporting_only",
            "evidence": (
                f"Primary naive effect {c4_naive['primary_effect']:.3f}, q={c4_naive['primary_q']:.3f}; "
                f"APC effect {c4_apc['primary_effect']:.3f}, q={c4_apc['primary_q']:.3f}; "
                "GSE135779 childhood estimates were null for both."
            ),
            "analysis_unit": "sample/donor-level program score",
            "source": SOURCE_FILES["c4b"].as_posix(),
            "allowed_wording": "supporting internal axes",
            "prohibited_wording": "externally replicated naive-memory or APC program",
            "manuscript_location": "Results 3-4; Discussion; Extended Data",
        },
        {
            "claim_id": "C6A-10",
            "tier": "external_only",
            "claim": "The GSE135779 atypical/low-naive signal is external-cohort-specific.",
            "status": "authorized_observation_only",
            "evidence": (
                f"GSE174188 primary effect {c4_atypical['primary_effect']:.3f}, q="
                f"{c4_atypical['primary_q']:.3f}; GSE135779 childhood effect "
                f"{float(c5_atypical['effect']):.3f}, q="
                f"{float(c5_atypical['q_value_primary4']):.3g}."
            ),
            "analysis_unit": "sample/donor-level program score",
            "source": SOURCE_FILES["c5b_programs"].as_posix(),
            "allowed_wording": "external-only observation",
            "prohibited_wording": "replicated atypical/ABC program",
            "manuscript_location": "Results 4; Discussion; Extended Data",
        },
        {
            "claim_id": "C6A-11",
            "tier": "future",
            "claim": "Regulator activity and perturbational support remain untested at C6A.",
            "status": "locked_pending_C6B",
            "evidence": "A pre-effect C6B contract is required before regulator effects are inspected.",
            "analysis_unit": "not applicable",
            "source": "00_project_management/gateC6B_regulatory_evidence_freeze_contract_2026-08-15.md",
            "allowed_wording": "candidate regulatory hypothesis",
            "prohibited_wording": "mechanistic validation; causal regulator",
            "manuscript_location": "Discussion only until C6B passes",
        },
    ]

    claim_fields = [
        "claim_id",
        "tier",
        "claim",
        "status",
        "evidence",
        "analysis_unit",
        "source",
        "allowed_wording",
        "prohibited_wording",
        "manuscript_location",
    ]
    write_csv(out_dir / "01_CLAIM_TO_EVIDENCE_MATRIX.csv", claim_rows, claim_fields)

    numeric_rows = [
        {
            "metric_id": "identity_min_ari",
            "value": c2b4["two_compartment_metrics"]["minimum_mapped_ari"],
            "display": format_num(c2b4["two_compartment_metrics"]["minimum_mapped_ari"]),
            "source": SOURCE_FILES["c2b4"].as_posix(),
            "field": "two_compartment_metrics.minimum_mapped_ari",
            "role": "identity foundation",
        },
        {
            "metric_id": "composition_primary_or",
            "value": c3a["primary"]["odds_ratio"],
            "display": format_num(c3a["primary"]["odds_ratio"]),
            "source": SOURCE_FILES["c3a"].as_posix(),
            "field": "primary.odds_ratio",
            "role": "secondary negative result",
        },
        {
            "metric_id": "c4_ifn_primary_effect",
            "value": c4_ifn["primary_effect"],
            "display": format_num(c4_ifn["primary_effect"]),
            "source": SOURCE_FILES["c4b"].as_posix(),
            "field": "confirmatory_programs.IFN_ISG.primary_effect",
            "role": "central discovery",
        },
        {
            "metric_id": "c4_ifn_primary_q",
            "value": c4_ifn["primary_q"],
            "display": f"{c4_ifn['primary_q']:.3g}",
            "source": SOURCE_FILES["c4b"].as_posix(),
            "field": "confirmatory_programs.IFN_ISG.primary_q",
            "role": "central discovery",
        },
        {
            "metric_id": "c4_ifn_nonoverlap_effect",
            "value": c4_ifn["validation_nonoverlap_effect"],
            "display": format_num(c4_ifn["validation_nonoverlap_effect"]),
            "source": SOURCE_FILES["c4b"].as_posix(),
            "field": "confirmatory_programs.IFN_ISG.validation_nonoverlap_effect",
            "role": "internal replication",
        },
        {
            "metric_id": "c5_ifn_childhood_effect",
            "value": c5b["ifn_results"]["childhood_min50"]["effect"],
            "display": format_num(c5b["ifn_results"]["childhood_min50"]["effect"]),
            "source": SOURCE_FILES["c5b"].as_posix(),
            "field": "ifn_results.childhood_min50.effect",
            "role": "independent replication",
        },
        {
            "metric_id": "c5_ifn_childhood_q",
            "value": c5b["ifn_results"]["childhood_min50"]["q_value_primary4"],
            "display": f"{c5b['ifn_results']['childhood_min50']['q_value_primary4']:.3g}",
            "source": SOURCE_FILES["c5b"].as_posix(),
            "field": "ifn_results.childhood_min50.q_value_primary4",
            "role": "independent replication",
        },
        {
            "metric_id": "c5_ifn_combined_effect",
            "value": c5b["ifn_results"]["combined_min50"]["effect"],
            "display": format_num(c5b["ifn_results"]["combined_min50"]["effect"]),
            "source": SOURCE_FILES["c5b"].as_posix(),
            "field": "ifn_results.combined_min50.effect",
            "role": "external sensitivity",
        },
        {
            "metric_id": "c5_ifn_adult_effect",
            "value": c5b["ifn_results"]["adult_min50"]["effect"],
            "display": format_num(c5b["ifn_results"]["adult_min50"]["effect"]),
            "source": SOURCE_FILES["c5b"].as_posix(),
            "field": "ifn_results.adult_min50.effect",
            "role": "directional boundary",
        },
        {
            "metric_id": "cross_dataset_rho",
            "value": c5b["cross_dataset_context"]["shared_tested_gene_rho"],
            "display": format_num(c5b["cross_dataset_context"]["shared_tested_gene_rho"]),
            "source": SOURCE_FILES["c5b"].as_posix(),
            "field": "cross_dataset_context.shared_tested_gene_rho",
            "role": "required limitation",
        },
    ]
    write_csv(
        out_dir / "02_MANUSCRIPT_NUMERIC_SOURCE.csv",
        numeric_rows,
        ["metric_id", "value", "display", "source", "field", "role"],
    )

    matrix_md = [
        "# Gate C6A claim-to-evidence matrix",
        "",
        "This view is generated from the frozen C2B4, C3A, C4B and C5B decisions.",
        "The CSV is the complete structured source.",
        "",
        "| ID | Tier | Status | Manuscript claim |",
        "|---|---|---|---|",
    ]
    for row in claim_rows:
        matrix_md.append(
            f"| {row['claim_id']} | {row['tier']} | {row['status']} | {row['claim']} |"
        )
    matrix_md.extend(
        [
            "",
            "## Binding central sentence",
            "",
            "> A disease-blind broad conventional-B-cell compartment exhibits reproducible "
            "SLE-associated type I interferon transcriptional remodeling across GSE174188 "
            "and the independent GSE135779 cohort.",
            "",
            "Regulatory language remains locked pending Gate C6B.",
        ]
    )
    write_text(out_dir / "01_CLAIM_TO_EVIDENCE_MATRIX.md", "\n".join(matrix_md))

    missing_documents = [str(path) for path in DOCUMENT_FILES if not (root / path).is_file()]
    combined_text = ""
    if not missing_documents:
        combined_text = "\n".join(
            (root / path).read_text(encoding="utf-8") for path in DOCUMENT_FILES[:5]
        ).lower()

    required_phrases = {
        "broad_conventional_boundary": "broad conventional-b",
        "association_boundary": "association rather than causation",
        "program_specific_boundary": "program-specific",
        "adult_boundary": "adult" if combined_text else "__missing__",
        "pseudobulk_unit": "pseudobulk",
        "genomewide_rho": "0.026",
    }
    prohibited_phrases = [
        "global transcriptomic concordance",
        "novel pathogenic b-cell subtype",
        "adult replication was confirmed",
        "replicated atypical/abc program",
        "mechanistically drives sle",
    ]
    text_qc_rows: list[dict[str, Any]] = []
    for check_id, phrase in required_phrases.items():
        present = phrase in combined_text
        text_qc_rows.append(
            {
                "check_id": check_id,
                "check_type": "required",
                "phrase": phrase,
                "pass": present,
                "detail": "present" if present else "missing",
            }
        )
    for phrase in prohibited_phrases:
        absent = phrase not in combined_text
        text_qc_rows.append(
            {
                "check_id": "prohibited_" + phrase.replace(" ", "_"),
                "check_type": "prohibited",
                "phrase": phrase,
                "pass": absent,
                "detail": "absent" if absent else "present",
            }
        )
    write_csv(
        out_dir / "04_GATE_C6A_TEXT_QC.csv",
        text_qc_rows,
        ["check_id", "check_type", "phrase", "pass", "detail"],
    )

    central_count = sum(row["tier"] == "central" for row in claim_rows)
    boundary_count = sum(
        row["tier"] in {"boundary", "negative_boundary"} for row in claim_rows
    )
    checks = {
        "frozen_source_decisions": {
            "pass": all(decision_checks.values()),
            "detail": f"{sum(decision_checks.values())}/4 expected decisions",
        },
        "claim_matrix_complete": {
            "pass": len(claim_rows) == 11,
            "detail": f"{len(claim_rows)} claims; {central_count} central; {boundary_count} boundaries",
        },
        "numeric_source_complete": {
            "pass": len(numeric_rows) == 10,
            "detail": f"{len(numeric_rows)} manuscript-critical metrics",
        },
        "document_set_complete": {
            "pass": not missing_documents,
            "detail": "all seven C6A governance documents present"
            if not missing_documents
            else "; ".join(missing_documents),
        },
        "text_claim_boundaries": {
            "pass": bool(text_qc_rows) and all(bool(row["pass"]) for row in text_qc_rows),
            "detail": f"{sum(bool(row['pass']) for row in text_qc_rows)}/{len(text_qc_rows)} checks",
        },
        "regulatory_effect_lock": {
            "pass": True,
            "detail": "C6A performs no regulator-activity or perturbation-effect calculation",
        },
    }
    decision = (
        "PASS_GATE_C6A_CLAIM_AND_MANUSCRIPT_FREEZE"
        if all(item["pass"] for item in checks.values())
        else "HOLD_GATE_C6A_REVIEW_REQUIRED"
    )
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision": decision,
        "central_claim": (
            "A disease-blind broad conventional-B-cell compartment exhibits reproducible "
            "SLE-associated type I interferon transcriptional remodeling across GSE174188 "
            "and independent GSE135779."
        ),
        "checks": checks,
        "claim_counts": {
            "total": len(claim_rows),
            "central": central_count,
            "boundary_or_negative": boundary_count,
        },
        "regulatory_effects_inspected": False,
        "next_stage": "Gate C6B pre-effect regulatory resource qualification and frozen analysis.",
    }
    write_text(
        out_dir / "05_GATE_C6A_ADVISOR_DECISION.json",
        json.dumps(payload, indent=2, ensure_ascii=True),
    )
    decision_md = [
        "# Gate C6A advisor decision",
        "",
        f"## `{decision}`",
        "",
        payload["central_claim"],
        "",
        "## Checks",
        "",
    ]
    for check_id, item in checks.items():
        marker = "PASS" if item["pass"] else "FAIL"
        decision_md.append(f"- [{marker}] {check_id}: {item['detail']}")
    decision_md.extend(
        [
            "",
            "## Binding boundaries",
            "",
            "- B_CONV is a broad conventional-B analog, not a hard naive/memory subtype.",
            "- B_ASC composition is secondary and not a central disease result.",
            "- Independent replication is IFN-program-specific, not transcriptome-wide.",
            "- The adult external estimate is directional and underpowered.",
            "- Association rather than causation remains the governing interpretation.",
            "",
            "## Next stage",
            "",
            payload["next_stage"],
        ]
    )
    write_text(out_dir / "05_GATE_C6A_ADVISOR_DECISION.md", "\n".join(decision_md))

    manifest_targets = [
        out_dir / "01_CLAIM_TO_EVIDENCE_MATRIX.csv",
        out_dir / "01_CLAIM_TO_EVIDENCE_MATRIX.md",
        out_dir / "02_MANUSCRIPT_NUMERIC_SOURCE.csv",
        out_dir / "04_GATE_C6A_TEXT_QC.csv",
        out_dir / "05_GATE_C6A_ADVISOR_DECISION.json",
        out_dir / "05_GATE_C6A_ADVISOR_DECISION.md",
    ] + [root / path for path in DOCUMENT_FILES]
    manifest_policy = {path.resolve(): "tracked" for path in manifest_targets}
    for relative_path, policy in ADDITIONAL_ARTIFACTS:
        path = root / relative_path
        manifest_targets.append(path)
        manifest_policy[path.resolve()] = policy
    manifest_rows = []
    for path in manifest_targets:
        if not path.is_file():
            continue
        manifest_rows.append(
            {
                "project_relative_path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "repository_policy": manifest_policy[path.resolve()],
            }
        )
    write_csv(
        out_dir / "06_GATE_C6A_INTEGRITY_MANIFEST.csv",
        manifest_rows,
        ["project_relative_path", "size_bytes", "sha256", "repository_policy"],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
