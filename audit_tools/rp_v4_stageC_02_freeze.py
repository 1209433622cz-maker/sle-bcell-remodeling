"""Freeze RP v4 Stage C without running forward G2C or real outcomes."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_DIR = (
    REPO_ROOT
    / "phase17_v7/rp_v4_redesign/20261010_stageC_single_g2c_external_input_protocol_freeze"
)
SOURCE_DIR = STAGE_DIR / "source_metadata"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def scenario_registry() -> list[dict]:
    source = read_csv(
        REPO_ROOT
        / "phase17_v7/rp_v3_redesign/20261010_wp2_effect_free_prefit/08_G2_SCENARIO_REGISTRY_FROZEN_FOR_IMPLEMENTATION.csv"
    )
    rows: list[dict] = []
    applicable = {"baseline", "depth_imbalance", "RNA_capture_content"}
    for row in source:
        rows.append(
            {
                "scenario_id": row["scenario_id"],
                "family": "OLD_COMPARABLE",
                "truth_structure": row["truth_structure"],
                "stress": row["regime"],
                "parameters": json.dumps(
                    {
                        key: row[key]
                        for key in (
                            "composition_log_tilt",
                            "within_bin_log2fc",
                            "rare_bin_weight_multiplier",
                            "managed_depth_multiplier",
                            "adjacent_mislabel_probability",
                            "managed_capture_log_tilt",
                        )
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "adjudication_role": (
                    "APPLICABLE_CONJUNCTION"
                    if row["regime"] in applicable
                    else "MANDATORY_BOUNDARY_REPORT"
                ),
                "outer_attempts": 4000,
                "truth_rule": "reuse qualified old observed-measurement truth; exact-null symmetry retained",
            }
        )

    shifts = [
        (
            "X1",
            "GAMMA_POISSON_OVERDISPERSION",
            {
                "rate_multiplier": "independent Gamma(shape=10,scale=0.1) per donor-bin-category",
                "mean": 1.0,
                "coefficient_of_variation": 10 ** -0.5,
            },
        ),
        (
            "X2",
            "CORRELATED_CAPTURE_HETEROGENEITY",
            {
                "donor_log_sd": 0.35,
                "bin_log_sd": 0.20,
                "bin_AR1_rho": 0.60,
                "lognormal_mean_correction": True,
            },
        ),
        (
            "X3",
            "NONADJACENT_LABEL_CONTAMINATION",
            {
                "total_mislabel_probability": 0.08,
                "adjacent_component": 0.05,
                "nonadjacent_component": 0.03,
                "destination_rule": "equal probability within available adjacent/nonadjacent sets",
            },
        ),
    ]
    structures = [
        ("C0", "null"),
        ("C1", "composition_only"),
        ("C2", "within_bin_only"),
        ("C3", "same_direction"),
        ("C4", "opposite_direction"),
    ]
    for code, truth_structure in structures:
        for shift_id, stress, parameters in shifts:
            rows.append(
                {
                    "scenario_id": f"{code}_{shift_id}",
                    "family": "PRESPECIFIED_SHIFT",
                    "truth_structure": truth_structure,
                    "stress": stress,
                    "parameters": json.dumps(parameters, sort_keys=True, separators=(",", ":")),
                    "adjudication_role": "APPLICABLE_CONJUNCTION",
                    "outer_attempts": 4000,
                    "truth_rule": (
                        "exact zero by arm symmetry for C0; otherwise independent stage-142 observed-measurement truth"
                    ),
                }
            )
    if len(rows) != 40:
        raise RuntimeError("Stage C must freeze exactly 40 final scenarios")
    return rows


def sra_summary(accession: str, bioproject: str, file_name: str, role: str) -> dict:
    path = SOURCE_DIR / file_name
    rows = read_csv(path)
    experiments = {row["Experiment"] for row in rows}
    biosamples = {row["BioSample"] for row in rows}
    layouts = sorted({row["LibraryLayout"] for row in rows})
    strategies = sorted({row["LibraryStrategy"] for row in rows})
    platforms = sorted({row["Platform"] for row in rows})
    return {
        "accession": accession,
        "bioproject": bioproject,
        "official_runinfo_url": f"https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/runinfo?acc={bioproject}",
        "runinfo_sha256": sha256(path),
        "runs": len(rows),
        "experiments": len(experiments),
        "biosamples": len(biosamples),
        "spots": sum(int(row["spots"]) for row in rows),
        "bases": sum(int(row["bases"]) for row in rows),
        "sra_size_MB": sum(float(row["size_MB"]) for row in rows),
        "library_layout": ";".join(layouts),
        "library_strategy": ";".join(strategies),
        "platform": ";".join(platforms),
        "frozen_role": role,
        "input_decision": "RAW_SRA_RECONSTRUCTION_FEASIBLE__DOWNLOAD_PENDING",
        "provenance_decision": "TREAT_AS_POTENTIALLY_OVERLAPPING_WITH_OTHER_CANDIDATE",
        "outcome_unlock": False,
    }


def main() -> dict:
    required = [
        STAGE_DIR / "01_EXPOSED_STREAM_STUDENTIZER_DIAGNOSTIC.csv",
        STAGE_DIR / "02_SINGLE_CANDIDATE_DEVELOPMENT_PERFORMANCE.csv",
        STAGE_DIR / "03_DEVELOPMENT_DIAGNOSTIC_SUMMARY.json",
        SOURCE_DIR / "PRJNA1093470_RunInfo.csv",
        SOURCE_DIR / "PRJNA484963_RunInfo.csv",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Stage C inputs: " + ", ".join(missing))
    development = json.loads(required[2].read_text(encoding="utf-8"))
    if not development["all_applicable_development_pass"]:
        raise RuntimeError("The single candidate did not pass the exposed development set")

    method_contract = {
        "schema": "RP_V4_STAGE_C_G2C_METHOD_1.0",
        "bound_git_head_before_stageC_commit": git_head(),
        "estimand_id": "delta_profile",
        "estimand_formula": (
            "b_X[T0(sum_k pi_ref,k m_ikg)] - b_X[T0(sum_k q_UMI,ik m_ikg)]"
        ),
        "implementation_formula": (
            "OLS disease coefficient for donor response T0(fixed-profile mixture) - T0(pooled counts)"
        ),
        "scientific_interpretation": (
            "association difference between two observed measurement/mixing rules; not a causal mediation proportion"
        ),
        "selection_reason": (
            "delta_profile passed all 15 historical G2B point-bias gates and concentrated the residual problem in interval coverage"
        ),
        "primary_method": (
            "direct donor-level OLS delta_profile; HC3 influence variance; two-sided t critical with df=68-4=64"
        ),
        "alpha": 0.05,
        "degrees_of_freedom": 64,
        "fallback_method": None,
        "fallback_policy": "none; failure closes the decomposition branch and no G2D is permitted",
        "development_evidence": {
            "status": "EXPOSED_HISTORICAL_DEVELOPMENT_ONLY",
            "applicable_scenarios_passed": "15/15",
            "not_forward_confirmation": True,
            "minimum_bootstrap_se_p01_over_median": development[
                "minimum_se_p01_over_median"
            ],
            "maximum_point_leverage": development["maximum_point_leverage"],
            "maximum_inner_failures": development["maximum_inner_failures"],
            "minimum_betaB_profile_bootstrap_corr": development[
                "minimum_betaB_profile_bootstrap_corr"
            ],
            "maximum_delta_algebra_abs_error": development[
                "maximum_delta_algebra_abs_error"
            ],
        },
        "method_sources": [
            "https://doi.org/10.1016/0304-4076(85)90158-7",
            "https://doi.org/10.1080/00031305.2000.10474549",
        ],
        "kernel": "audit_tools/rp_v4_g2c_hc3t.py",
        "kernel_sha256": sha256(REPO_ROOT / "audit_tools/rp_v4_g2c_hc3t.py"),
        "real_effects_permitted": False,
        "automatic_unlock_permitted": False,
    }
    write_json(STAGE_DIR / "04_G2C_ESTIMAND_AND_METHOD_CONTRACT.json", method_contract)

    scenarios = scenario_registry()
    write_csv(STAGE_DIR / "05_G2C_FINAL_DGP_REGISTRY.csv", scenarios)
    seed_contract = {
        "schema": "RP_V4_G2C_FINAL_SEED_AND_BUDGET_1.0",
        "random_seed_base": 2026101004,
        "counter_address": [
            "seed_base",
            "stage",
            "scenario_index",
            "attempt_id",
            "component_id",
        ],
        "development_stage": 131,
        "final_outer_stage": 141,
        "final_truth_stage": 142,
        "final_scenarios": 40,
        "old_comparable_scenarios": 25,
        "shifted_scenarios": 15,
        "outer_attempts_per_scenario": 4000,
        "registered_outer_attempts": 160000,
        "inner_bootstraps": 0,
        "truth_effort_per_nonnull_shifted_scenario_per_arm": 131072,
        "truth_precision_rule": "truth MCSE <= 0.01 * fixed-design typical coefficient SE",
        "checkpoint_attempts": 100,
        "no_replenishment": True,
        "max_numerical_failure_fraction": 0.01,
        "minimum_supported_for_performance": 274,
        "coverage_gate": "Wilson 95% interval wholly within [0.925,0.975]",
        "bias_gate": "(abs(bias)+1.96*MCSE_bias)/EmpSD <= 0.10",
        "exact_null_type_i_gate": "Wilson 95% upper bound <= 0.075",
        "applicable_conjunction_scenarios": 30,
        "boundary_report_scenarios": 10,
        "estimated_runtime_note": (
            "analytic HC3-t removes the 2,000-fold inner bootstrap; Stage D must benchmark before final execution"
        ),
        "final_execution_authorized": False,
    }
    write_json(STAGE_DIR / "06_G2C_FINAL_SEED_AND_COMPUTE_CONTRACT.json", seed_contract)

    external = [
        sra_summary(
            "GSE262846",
            "PRJNA1093470",
            "PRJNA1093470_RunInfo.csv",
            "PRIMARY_CLINICAL_ACTIVITY_CANDIDATE__OUTCOME_LOCKED",
        ),
        sra_summary(
            "GSE118254",
            "PRJNA484963",
            "PRJNA484963_RunInfo.csv",
            "TECHNICAL_MEASUREMENT_BRIDGE__NOT_A_SECOND_INDEPENDENT_CONFIRMATION",
        ),
    ]
    write_csv(STAGE_DIR / "07_EXTERNAL_RAW_INPUT_MANIFEST.csv", external)

    raw_contract = """# RP v4 external raw-input reconstruction contract

## Locked decision

Both candidates have public paired-end RNA-seq runs and are technically
reconstructable from SRA.  Neither processed RPKM nor previously deposited
normalized values may be used as if they were the frozen count/CPM scale.
Downloading and reconstruction do not unlock disease or activity outcomes.

## Provenance boundary

GSE262846 and GSE118254 use different de-identification namespaces but have
related investigator lineage.  Public token comparison cannot prove distinct
people.  Until depositor-level provenance is available they are treated as
potentially overlapping.  They must never be counted as two independent
confirmations, pooled as independent donors, or used in a two-study meta-analysis.

## Reconstruction pipeline to implement before download

1. Freeze the exact SRA run list from the two hashed NCBI RunInfo files.
2. Prefetch each SRR with SRA Toolkit; verify toolkit validation and run hashes.
3. Convert paired reads with `fasterq-dump --split-files`; compress with `pigz`.
4. Record FastQC/MultiQC metrics.  Adapter trimming is allowed only under one
   fixed `fastp` rule applied to both studies; samples are not excluded by
   disease-labelled quality patterns.
5. Align all libraries with one frozen STAR/GRCh38/GENCODE build and emit raw
   gene counts.  The genome FASTA, GTF, STAR index and software hashes must be
   frozen before the first outcome join.
6. Merge multiple runs only within the same SRA experiment/GEO library.  Never
   merge rN with T1T2 or different sorted subsets.  Donor is the inferential
   unit; libraries/subsets are repeated measurements nested in donor.
7. Require all 12 frozen IFN genes to map uniquely by approved gene symbol.
   A true zero count remains zero; an absent annotation is a technical failure,
   not a zero.  `S0` uses full assigned-library counts for CPM and the unchanged
   43-control discovery mean/SD.  `S1` uses only the frozen 18,873-symbol
   background and remains a sensitivity.
8. Seal a count-only technical object and QC receipt before joining any disease,
   activity or treatment field.

## Resource envelope

- GSE262846: 176 runs, 752.70 G bases, approximately 233.21 GB SRA payload.
- GSE118254: 85 runs, 174.96 G bases, approximately 64.37 GB SRA payload.
- Combined: approximately 297.57 GB SRA payload and 927.66 G sequenced bases.
- Reserve at least 2.5 TB temporary disk for uncompressed paired FASTQ,
  alignment scratch, counts and checksums.  Download may be delegated to the
  author workstation after the Stage D runbook is generated.

## Outcome lock

No case-control, active-inactive, SLEDAI or score-direction result may be fitted
or inspected during intake.  GSE262846 remains a candidate for a prespecified
clinical-activity analysis; GSE118254 remains a technical measurement bridge.
"""
    (STAGE_DIR / "08_EXTERNAL_RAW_RECONSTRUCTION_AND_PROVENANCE_CONTRACT.md").write_text(
        raw_contract, encoding="utf-8", newline="\n"
    )

    score_contract = {
        "schema": "RP_V4_STAGE_C_SCORE_CONTRACT_1.0",
        "S0": {
            "status": "PRIMARY_FROZEN_ANCHOR",
            "genes": [
                "IFI44L",
                "IFI6",
                "IFIT1",
                "IFIT2",
                "IFIT3",
                "IRF7",
                "ISG15",
                "LY6E",
                "MX1",
                "MX2",
                "OAS1",
                "OAS2",
            ],
            "formula": "mean_g[(log2(full-library CPM_g + 0.5)-mu_g_43HC)/sd_g_43HC]",
            "missing_annotation_rule": "technical failure; never impute an absent gene as zero",
            "zero_count_rule": "retain zero and apply the frozen +0.5 offset",
            "reference_refit_permitted": False,
        },
        "S1": {
            "status": "TECHNICAL_SENSITIVITY_ONLY",
            "formula": "mean percentile rank of the same 12 genes within the frozen 18,873-symbol background",
            "missing_background_rule": "intersect only after a sealed mapping audit; report retained background fraction",
            "clinical_promotion_permitted": False,
        },
        "S2": {
            "status": "ABANDONED_NOT_ADMITTED",
            "reason": "no unique result-blind formula, denominator and missing-feature rule",
        },
        "outcome_based_score_selection": False,
        "outcome_unlock": False,
    }
    write_json(STAGE_DIR / "09_S0_S1_TECHNICAL_MEASUREMENT_CONTRACT.json", score_contract)

    checks = [
        ("single_estimand", method_contract["estimand_id"] == "delta_profile", "exactly one registered estimand"),
        ("single_primary_method", method_contract["fallback_method"] is None, "one HC3-t method; no fallback search"),
        ("development_not_final", not development["forward_validation_executed"], "historical streams labelled development only"),
        ("development_grid", development["candidate_development_passes"] == 15, "15/15 exposed applicable cells; not confirmatory"),
        ("new_seed_base", seed_contract["random_seed_base"] != 2026101002, "independent base 2026101004"),
        ("new_dgp_shifts", len([r for r in scenarios if r["family"] == "PRESPECIFIED_SHIFT"]) == 15, "15 shifted scenarios"),
        ("full_attempt_accounting", seed_contract["registered_outer_attempts"] == 160000, "40 x 4,000; no replenishment"),
        ("no_inner_method_search", seed_contract["inner_bootstraps"] == 0, "analytic single method"),
        ("raw_runinfo_262846", external[0]["runs"] == 176 and external[0]["experiments"] == 88, "NCBI RunInfo reconciled"),
        ("raw_runinfo_118254", external[1]["runs"] == 85 and external[1]["experiments"] == 83, "NCBI RunInfo reconciled"),
        ("provenance_fail_closed", all("POTENTIALLY_OVERLAPPING" in row["provenance_decision"] for row in external), "no false independent-cohort claim"),
        ("S0_locked", score_contract["S0"]["status"] == "PRIMARY_FROZEN_ANCHOR", "unchanged primary score"),
        ("S1_limited", score_contract["S1"]["status"] == "TECHNICAL_SENSITIVITY_ONLY", "cannot be promoted by P value"),
        ("S2_excluded", score_contract["S2"]["status"] == "ABANDONED_NOT_ADMITTED", "no arbitrary new score"),
        ("real_outcome_lock", not method_contract["real_effects_permitted"] and not any(row["outcome_unlock"] for row in external), "WP2 and external outcomes locked"),
        ("final_execution_lock", not seed_contract["final_execution_authorized"], "exact protocol sign-off required"),
    ]
    check_rows = [
        {"check": name, "pass": passed, "detail": detail}
        for name, passed, detail in checks
    ]
    write_csv(STAGE_DIR / "10_STAGE_C_CHECKS.csv", check_rows)
    all_pass = all(row["pass"] for row in check_rows)
    gate = {
        "created_at": "2026-10-10T00:00:00+08:00",
        "decision": (
            "PASS_RPV4_STAGE_C_PROTOCOL_FREEZE__AUTHOR_SIGNOFF_REQUIRED_BEFORE_FINAL"
            if all_pass
            else "HOLD_RPV4_STAGE_C_PROTOCOL_FREEZE"
        ),
        "checks_passed": sum(row["pass"] for row in check_rows),
        "checks_total": len(check_rows),
        "G2C_estimand": "delta_profile",
        "G2C_method": method_contract["primary_method"],
        "G2C_forward_validation": "NOT_RUN",
        "WP2_REAL_EFFECT": "LOCKED",
        "EXTERNAL_DISEASE_ACTIVITY_OUTCOMES": "LOCKED",
        "S2": "ABANDONED_NOT_ADMITTED",
        "submission": "HOLD",
        "stageD_technical_pilot_authorized": all_pass,
        "final_G2C_authorized": False,
        "external_large_download_authorized": False,
        "next_stage": "RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT",
        "stop_rule": "one final G2C failure closes decomposition; no G2D",
    }
    write_json(STAGE_DIR / "11_RPV4_STAGE_C_GATE_STATUS.json", gate)

    review = f"""# RP v4 Stage C advisor review

## Decision

`{gate['decision']}`

Stage C freezes one estimand and one method.  It does not run or imply a final
G2C PASS.  Real WP2 effects, new-cohort outcomes, manuscript changes and
submission work remain locked.

## Why `delta_profile`

`delta_profile` is the clean interval-calibration problem: all 15 historical
G2B point-bias gates passed, while nine cells failed coverage.  `delta_cellref`
was not selected because its historical failures mix interval undercoverage
with a point-bias failure.  The registered interpretation is an association
difference between two observed measurement/mixing rules, never a mediation
percentage or cell-intrinsic causal effect.

## Historical-development diagnosis

The exposed development replay found:

- 15/15 applicable cells passed the single HC3-t candidate;
- bootstrap-SE p01/median was never below {development['minimum_se_p01_over_median']:.3f};
- maximum point leverage was {development['maximum_point_leverage']:.3f};
- no inner bootstrap failed in the diagnostic subset;
- beta_B and beta_S_profile bootstrap correlation was at least
  {development['minimum_betaB_profile_bootstrap_corr']:.3f}; and
- direct delta equalled the coefficient difference to within
  {development['maximum_delta_algebra_abs_error']:.3g}.

These results argue against a near-zero studentizer, non-smooth delta or gross
leverage failure.  They support a small-sample influence-function correction,
but they are exposed development evidence only.  Confirmation requires the
new seed base, 40 frozen DGPs and 160,000 registered outer attempts.

## External-input decision

Official NCBI RunInfo confirms 176 runs/88 experiments for GSE262846 and 85
runs/83 experiments for GSE118254.  The combined SRA payload is about 297.57 GB
and contains 927.66 G bases.  Raw reconstruction is feasible but pending.  At
least 2.5 TB scratch space should be reserved.

The two studies are conservatively treated as potentially overlapping because
different de-identification tokens cannot resolve shared-donor provenance.
GSE262846 may become the primary clinical-activity candidate only after sealed
count reconstruction.  GSE118254 is a technical measurement bridge and cannot
be counted as a second independent confirmation.

## Measurement decision

S0 remains the primary frozen score; S1 remains a technical sensitivity.  S2 is
abandoned because no unique result-blind formula was justified.  Neither score
may be selected or promoted using disease direction, P value or AUC.

## Next stage

Proceed only to `RPV4_STAGE_D__G2C_IMPLEMENTATION_AND_EXTERNAL_RAW_INTAKE_TECHNICAL_PILOT`:

1. implement and unit-test the three shifted generators and independent truth engine;
2. benchmark a small non-adjudicative technical grid without final performance claims;
3. generate a resumable SRA download/count runbook and checksum plan;
4. obtain exact author sign-off on the frozen protocol before any final G2C run;
5. keep all real outcomes sealed.

Failure of the single final strategy will produce
`G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`; RP v4 permits no G2D rescue.
"""
    (STAGE_DIR / "12_RPV4_STAGE_C_ADVISOR_REVIEW.md").write_text(
        review, encoding="utf-8", newline="\n"
    )

    pilot = """# RP v4 Stage D technical-pilot protocol

## Allowed

- Implement the frozen HC3-t kernel wrapper, shifted DGP generator and truth engine.
- Run unit tests and a tiny counter-addressed technical pilot for shape, support,
  reproducibility, checkpoint and manifest validation.
- Generate (but do not automatically start) resumable NCBI SRA download and
  count-reconstruction scripts.
- Verify S0/S1 feature mapping using count-only objects with outcome fields absent.

## Not allowed

- Do not run the 160,000-attempt final G2C grid.
- Do not alter the estimand, t(64) method, 40 scenarios, thresholds or seed base.
- Do not inspect or fit real WP2, case-control, activity or treatment effects.
- Do not describe GSE262846 and GSE118254 as independent confirmations.
- Do not modify manuscript, figures, submission package, Release or Zenodo.

## Stage D exit

PASS requires deterministic replay, independent truth precision qualification,
all implementation tests, a complete checkpoint/run manifest, resource benchmark
and exact author approval of the final contract.  Only a later explicit gate may
authorize final simulation or large external download.
"""
    (STAGE_DIR / "13_STAGE_D_TECHNICAL_PILOT_PROTOCOL.md").write_text(
        pilot, encoding="utf-8", newline="\n"
    )

    manifest_rows = []
    for path in sorted(STAGE_DIR.iterdir()):
        if path.is_file() and path.name != "14_INTEGRITY_MANIFEST.csv":
            manifest_rows.append(
                {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            )
    write_csv(STAGE_DIR / "14_INTEGRITY_MANIFEST.csv", manifest_rows)
    return gate


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
