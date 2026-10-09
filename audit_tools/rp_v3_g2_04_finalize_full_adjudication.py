"""Freeze a compact, tracked record of a completed RP v3 full-G2 run.

The finalizer is deliberately downstream of the frozen generator, estimator,
truth engine and adjudicator. It re-adjudicates the raw chunks, requires an
exact match to the existing official adjudication, and never reads real WP2
responses.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import platform
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

try:
    from .rp_v3_g2_adjudicate import adjudicate
    from .rp_v3_g2_estimation import TARGETS
    from .rp_v3_g2_full_runner import REPO_ROOT, binding, verify_chunk
except ImportError:  # Direct script execution from audit_tools/.
    from rp_v3_g2_adjudicate import adjudicate
    from rp_v3_g2_estimation import TARGETS
    from rp_v3_g2_full_runner import REPO_ROOT, binding, verify_chunk


OFFICIAL_FILES = (
    "01_G2_ATTEMPT_ACCOUNTING.csv",
    "02_G2_TARGET_SCENARIO_ADJUDICATION.csv",
    "03_G2_FINAL_DECISION.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write an empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit_attempt_payloads(run_root: Path, expected_binding: str) -> dict:
    attempts: dict[tuple[str, int], tuple[str, int, int, int]] = {}
    chunk_count = 0
    for scenario_dir in sorted(path for path in run_root.iterdir() if path.is_dir()):
        if scenario_dir.name == "adjudication":
            continue
        for chunk_dir in sorted(path for path in scenario_dir.iterdir() if path.is_dir()):
            receipt = verify_chunk(chunk_dir, expected_binding)
            if receipt["real_effects_fitted"] is not False:
                raise RuntimeError(f"Real-effect flag is not false: {chunk_dir}")
            chunk_count += 1
            seen_in_chunk: dict[tuple[str, int], tuple[str, int, int, int]] = {}
            payload = chunk_dir / "attempt_targets.csv.gz"
            with gzip.open(payload, "rt", encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    key = (row["scenario_id"], int(row["attempt_id"]))
                    value = (
                        row["status"],
                        int(row["inner_attempted"]),
                        int(row["inner_successful"]),
                        int(row["inner_failures"]),
                    )
                    prior = seen_in_chunk.setdefault(key, value)
                    if prior != value:
                        raise RuntimeError(f"Inconsistent target-level attempt accounting: {key}")
                    if row["error_type"] or row["error"]:
                        raise RuntimeError(f"Persisted numerical error in {key}: {row['error_type']}")
            for key, value in seen_in_chunk.items():
                if key in attempts:
                    raise RuntimeError(f"Duplicated outer attempt: {key}")
                attempts[key] = value

    if chunk_count != 2000:
        raise RuntimeError(f"Expected 2,000 chunks, found {chunk_count}")
    if len(attempts) != 50000:
        raise RuntimeError(f"Expected 50,000 outer attempts, found {len(attempts)}")
    statuses = Counter(value[0] for value in attempts.values())
    return {
        "chunk_count": chunk_count,
        "outer_attempts": len(attempts),
        "interval_computed": statuses["INTERVAL_COMPUTED"],
        "support_stops": statuses["SUPPORT_STOP"],
        "numerical_failures": sum(
            count for status, count in statuses.items()
            if status not in {"INTERVAL_COMPUTED", "SUPPORT_STOP"}
        ),
        "inner_attempted": sum(value[1] for value in attempts.values()),
        "inner_successful": sum(value[2] for value in attempts.values()),
        "inner_failures": sum(value[3] for value in attempts.values()),
    }


def scenario_summary(rows: list[dict[str, str]]) -> list[dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["scenario_id"]].append(row)
    result = []
    for scenario_id in sorted(grouped):
        group = grouped[scenario_id]
        decisions = Counter(row["decision"] for row in group)
        applicable = as_bool(group[0]["applicable_domain"])
        result.append(
            {
                "scenario_id": scenario_id,
                "truth_structure": group[0]["truth_structure"],
                "regime": group[0]["regime"],
                "domain_classification": group[0]["domain_classification"],
                "applicable_domain": applicable,
                "target_rows": len(group),
                "pass_target_scenarios": decisions["PASS_TARGET_SCENARIO"],
                "hold_target_scenarios": sum(
                    count for decision, count in decisions.items() if decision.startswith("HOLD_")
                ),
                "boundary_target_scenarios": decisions["BOUNDARY_REPORTED"],
                "truth_precision_failures": sum(not as_bool(row["truth_precision_pass"]) for row in group),
                "bias_failures": sum(
                    row["bias_pass"] != "" and not as_bool(row["bias_pass"]) for row in group
                ),
                "coverage_failures": sum(
                    row["coverage_pass"] != "" and not as_bool(row["coverage_pass"]) for row in group
                ),
                "type_i_failures": sum(
                    row["type_i_pass"] != "" and not as_bool(row["type_i_pass"]) for row in group
                ),
                "numerical_failures": sum(not as_bool(row["numerical_pass"]) for row in group),
                "supported_attempts_min": min(int(row["supported_attempts"]) for row in group),
                "supported_attempts_max": max(int(row["supported_attempts"]) for row in group),
            }
        )
    if len(result) != 25:
        raise RuntimeError(f"Expected 25 scenario summaries, found {len(result)}")
    return result


def target_summary(rows: list[dict[str, str]], final_decision: dict) -> list[dict]:
    result = []
    for target in TARGETS:
        group = [row for row in rows if row["target_id"] == target and as_bool(row["applicable_domain"])]
        blockers = [row["scenario_id"] for row in group if row["decision"] != "PASS_TARGET_SCENARIO"]
        result.append(
            {
                "target_id": target,
                "applicable_target_scenarios": len(group),
                "pass_target_scenarios": sum(row["decision"] == "PASS_TARGET_SCENARIO" for row in group),
                "hold_target_scenarios": len(blockers),
                "truth_precision_failures": sum(not as_bool(row["truth_precision_pass"]) for row in group),
                "bias_failures": sum(not as_bool(row["bias_pass"]) for row in group),
                "coverage_failures": sum(not as_bool(row["coverage_pass"]) for row in group),
                "type_i_failures": sum(
                    row["type_i_pass"] != "" and not as_bool(row["type_i_pass"]) for row in group
                ),
                "numerical_failures": sum(not as_bool(row["numerical_pass"]) for row in group),
                "blocking_scenarios": ";".join(blockers),
                "unlock_recommended": bool(final_decision["target_unlock_recommendation"][target]),
            }
        )
    return result


def boundary_summary(
    accounting: list[dict[str, str]], rows: list[dict[str, str]]
) -> list[dict]:
    lookup = {row["scenario_id"]: row for row in rows}
    result = []
    for row in accounting:
        if row["regime"] not in {"rarity_support", "adjacent_mislabeling"}:
            continue
        outer = int(row["outer_attempts"])
        intervals = int(row["interval_computed"])
        result.append(
            {
                "scenario_id": row["scenario_id"],
                "truth_structure": lookup[row["scenario_id"]]["truth_structure"],
                "regime": row["regime"],
                "domain_classification": lookup[row["scenario_id"]]["domain_classification"],
                "outer_attempts": outer,
                "interval_computed": intervals,
                "support_stops": int(row["support_stops"]),
                "numerical_failures": int(row["numerical_failures"]),
                "support_rate": format(intervals / outer, ".6f"),
                "adjudication_role": "MANDATORY_REPORTED_BOUNDARY_NOT_IN_APPLICABLE_CONJUNCTION",
            }
        )
    if len(result) != 10:
        raise RuntimeError(f"Expected 10 boundary summaries, found {len(result)}")
    return result


def review_markdown(
    final_decision: dict,
    rows: list[dict[str, str]],
    payload: dict,
) -> str:
    applicable = [row for row in rows if as_bool(row["applicable_domain"])]
    decisions = Counter(row["decision"] for row in applicable)
    coverage_failures = [row for row in applicable if not as_bool(row["coverage_pass"])]
    undercoverage = sum(float(row["coverage_wilson_lower"]) < 0.925 for row in coverage_failures)
    overcoverage = sum(float(row["coverage_wilson_upper"]) > 0.975 for row in coverage_failures)
    bias_failures = [row for row in applicable if not as_bool(row["bias_pass"])]
    type_i_rows = [row for row in applicable if row["type_i_pass"] != ""]
    return f"""# RP v3 full-G2 post-adjudication review

## Decision

**{final_decision['decision']}**

The complete 25-scenario grid was adjudicated under the frozen binding
`{final_decision['binding_sha256']}`. The grid contains 50,000 outer attempts,
{payload['inner_attempted']:,} paired-bootstrap fits and no numerical failures.
Real WP2 effects were not loaded or fitted.

The applicable domain contains 150 target-scenario cells. Of these,
{decisions['PASS_TARGET_SCENARIO']} passed and {decisions['HOLD_TARGET_SCENARIO']}
were held. None of the ten targets passed all 15 required applicable scenarios,
so no target is recommended for unlock and `WP2_REAL_EFFECT_UNLOCK` remains false.

## Failure anatomy

- Truth precision: 150/150 applicable cells passed.
- Numerical stability: 150/150 applicable cells passed.
- Bias: {len(applicable) - len(bias_failures)}/150 passed. The single failure was
  `{bias_failures[0]['scenario_id']} / {bias_failures[0]['target_id']}`.
- Coverage: {len(applicable) - len(coverage_failures)}/150 passed and
  {len(coverage_failures)}/150 failed. Among failed cells, {undercoverage} had a
  Wilson lower bound below 0.925 and {overcoverage} had an upper bound above 0.975.
- Exact-null type-I error: {sum(as_bool(row['type_i_pass']) for row in type_i_rows)}/{len(type_i_rows)}
  registered cells passed.

The dominant defect is therefore interval undercoverage, not truth imprecision,
false-positive inflation at the registered exact nulls, support replenishment or
numerical instability. Small disease coefficients in real data cannot override
this simulation result.

## Boundary regimes

R1 (`rarity_support`) and R3 (`adjacent_mislabeling`) remain mandatory reported
stress domains. They do not enter the applicable-domain conjunction and cannot
be converted into PASS rows. Across the full grid, {payload['support_stops']:,}
outer attempts stopped for prespecified support reasons; these are reported
rather than replenished.

## Scientific interpretation

The current paired percentile-bootstrap implementation does not satisfy the
predeclared G2 coverage contract across the applicable domain. RP v3 therefore
does not authorize estimation or interpretation of real WP2 disease effects
with this implementation. This HOLD is an informative result about the proposed
estimation route, not a failure to obtain a preferred biological direction.

## Next stage

Proceed only to `RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`. This stage may
diagnose the interval procedure and prospectively freeze one scientifically
justified replacement implementation. It may not relax acceptance thresholds,
remove adverse scenarios, inspect real WP2 responses or overwrite this HOLD.
Any amended G2B must use a new versioned binding, the unchanged target/scenario
contract, fresh random streams and a complete new adjudication before a separate
unlock review can even be considered.
"""


def next_stage_contract() -> str:
    return """# RP v3 next-stage contract after full-G2 HOLD

## Gate name

`RP_V3_G2_HOLD_DIAGNOSTIC_AND_AMENDMENT_GATE`

## Objective

Determine whether the WP2 interval procedure has one defensible, prospectively
specified repair. The current G2 result remains the canonical assessment of the
frozen percentile-bootstrap implementation.

## Permitted work

1. Diagnose undercoverage using synthetic outputs and mathematical properties of
   the interval construction.
2. Compare candidate interval constructions only in a clearly labelled
   development sandbox that cannot read real WP2 responses.
3. Select at most one replacement on methodological grounds, then freeze its
   code, estimands, scenario grid, thresholds, random-stream namespace and
   adjudicator before any full G2B execution.
4. Re-run all 25 registered scenarios with 2,000 outer attempts and 2,000 paired
   bootstrap attempts per supported outer attempt, preserving support stops and
   all failure rows.

## Prohibited work

- loading, fitting or previewing real WP2 disease responses;
- relaxing the frozen bias, coverage, type-I or numerical thresholds;
- deleting or reclassifying adverse scenarios after seeing results;
- changing targets, truth values or the applicable/boundary domain split to
  obtain PASS;
- overwriting the current G2 output or describing it as passed;
- proceeding to manuscript claims, WP4, submission or release work.

## Exit states

- `HOLD_CURRENT_WP2_METHOD__RP_V3_SCOPE_CONTRACTION`: no single defensible repair
  is frozen; real WP2 effects stay locked and the research question is narrowed.
- `PROSPECTIVE_G2B_PROTOCOL_FROZEN__REAL_WP2_STILL_LOCKED`: one amended method is
  frozen and ready for full synthetic execution.
- Only a complete G2B PASS followed by an independent post-G2B review may produce
  an unlock recommendation. Unlock is never automatic.
"""


def finalize(run_root: Path, output_dir: Path, repo_root: Path = REPO_ROOT) -> dict:
    run_root = run_root.resolve()
    output_dir = output_dir.resolve()
    official_dir = run_root / "adjudication"
    if output_dir.exists():
        raise FileExistsError(f"Final output must be new: {output_dir}")
    staging = output_dir.parent / f"{output_dir.name}.staging"
    if staging.exists():
        raise FileExistsError(f"Staging directory already exists: {staging}")
    if not all((official_dir / name).is_file() for name in OFFICIAL_FILES):
        raise FileNotFoundError(f"Incomplete official adjudication: {official_dir}")

    current_binding = binding(repo_root)
    run_binding = json.loads((run_root / "run_binding.json").read_text(encoding="utf-8"))
    if current_binding != run_binding:
        raise RuntimeError("Run binding does not match the current frozen implementation")

    with tempfile.TemporaryDirectory(prefix="_readjudication_", dir=run_root) as tmp:
        independent_dir = Path(tmp) / "adjudication"
        independent = adjudicate(run_root, independent_dir, repo_root=repo_root)
        for name in OFFICIAL_FILES:
            if (independent_dir / name).read_bytes() != (official_dir / name).read_bytes():
                raise RuntimeError(f"Independent adjudication differs from official output: {name}")

    payload = audit_attempt_payloads(run_root, current_binding["binding_sha256"])
    accounting = read_csv(official_dir / OFFICIAL_FILES[0])
    rows = read_csv(official_dir / OFFICIAL_FILES[1])
    final_decision = json.loads((official_dir / OFFICIAL_FILES[2]).read_text(encoding="utf-8"))
    if independent != final_decision:
        raise RuntimeError("Independent adjudication decision object differs from official output")
    if final_decision["decision"] != "HOLD_G2_APPLICABLE_DOMAIN":
        raise RuntimeError("This post-HOLD finalizer received a non-HOLD G2 decision")
    if final_decision["WP2_REAL_EFFECT_UNLOCK"] is not False:
        raise RuntimeError("WP2 real-effect lock is not preserved")

    scenario_rows = scenario_summary(rows)
    target_rows = target_summary(rows, final_decision)
    boundary_rows = boundary_summary(accounting, rows)
    all_files = [path for path in run_root.rglob("*") if path.is_file()]
    receipt = {
        "schema": "RP_V3_G2_POST_ADJUDICATION_1.0",
        "decision": final_decision["decision"],
        "binding_sha256": current_binding["binding_sha256"],
        "source_run_root": str(run_root.relative_to(repo_root)),
        "source_file_count": len(all_files),
        "source_total_bytes": sum(path.stat().st_size for path in all_files),
        **payload,
        "scenario_count": 25,
        "target_count": 10,
        "applicable_target_scenario_rows": 150,
        "boundary_target_scenario_rows": 100,
        "official_adjudication_byte_identical_to_independent_rerun": True,
        "real_effects_loaded_or_fitted": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
        "python_executable": sys.executable,
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "platform": platform.platform(),
    }

    staging.mkdir(parents=True)
    for name in OFFICIAL_FILES:
        source = official_dir / name
        if source.suffix == ".csv":
            # Tracked CSVs are LF-normalized; byte identity is checked above on
            # the untouched official and independent raw adjudications.
            (staging / name).write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
        else:
            shutil.copy2(source, staging / name)
    write_csv(staging / "04_G2_SCENARIO_FAILURE_MODE_SUMMARY.csv", scenario_rows)
    write_csv(staging / "05_G2_TARGET_UNLOCK_SUMMARY.csv", target_rows)
    write_csv(staging / "06_G2_BOUNDARY_SUPPORT_SUMMARY.csv", boundary_rows)
    (staging / "07_G2_RUN_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    (staging / "08_G2_POST_ADJUDICATION_REVIEW.md").write_text(
        review_markdown(final_decision, rows, payload), encoding="utf-8", newline="\n"
    )
    (staging / "09_G2_NEXT_STAGE_CONTRACT.md").write_text(
        next_stage_contract(), encoding="utf-8", newline="\n"
    )
    manifest = [
        {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(staging.iterdir())
        if path.is_file()
    ]
    write_csv(staging / "10_G2_INTEGRITY_MANIFEST.csv", manifest)
    staging.replace(output_dir)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(finalize(args.run_root, args.output_dir), indent=2, sort_keys=True))
