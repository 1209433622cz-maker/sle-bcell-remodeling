"""Write-once final adjudication driver with mandatory payload reconciliation."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

try:
    from .rp_v4_stageF2_adjudicator import adjudicate_one, full_conjunction
    from .rp_v4_stageF2_common import (
        atomic_write_text,
        authorize_final,
        read_json,
        sha256_file,
        stable_json,
    )
    from .rp_v4_stageF2_runner import verify_outer_payload
    from .rp_v4_stageF2_truth import verify_truth_payload
except ImportError:
    from rp_v4_stageF2_adjudicator import adjudicate_one, full_conjunction
    from rp_v4_stageF2_common import (
        atomic_write_text,
        authorize_final,
        read_json,
        sha256_file,
        stable_json,
    )
    from rp_v4_stageF2_runner import verify_outer_payload
    from rp_v4_stageF2_truth import verify_truth_payload


def _boolean(value: object) -> bool:
    if value is True or value == "True":
        return True
    if value is False or value == "False":
        return False
    raise ValueError(f"Expected strict boolean, received {value!r}")


def _read_csv(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_registry(path: Path) -> list[dict]:
    rows = _read_csv(path)
    if len(rows) != 40 or len({row["scenario_id"] for row in rows}) != 40:
        raise ValueError("Frozen registry must contain 40 unique scenarios")
    for index, row in enumerate(rows):
        row["scenario_index"] = index
        if int(row["outer_attempts"]) != 4000:
            raise ValueError("Frozen outer-attempt count drift")
    return rows


def load_oracles(
    old_truth_path: Path, shifted_truth_path: Path, registry: list[dict]
) -> dict[str, dict]:
    old_rows = [
        row for row in _read_csv(old_truth_path) if row["target_id"] == "delta_profile"
    ]
    if len(old_rows) != 25:
        raise ValueError("Historical delta_profile truth must contain 25 scenarios")
    oracles = {}
    for row in old_rows:
        if not _boolean(row["precision_pass"]):
            raise ValueError("Historical truth precision failure")
        oracles[row["scenario_id"]] = {
            "scenario_id": row["scenario_id"],
            "truth": float(row["truth"]),
            "truth_mcse": float(row["truth_mcse"]),
            "typical_coefficient_se": float(row["typical_coefficient_se"]),
            "precision_pass": True,
            "exact_null_registered": _boolean(row["true_null_registered"]),
            "truth_basis": row["truth_basis"],
            "provenance": "HISTORICAL_QUALIFIED_OLD25",
        }
    shifted_rows = _read_csv(shifted_truth_path)
    if len(shifted_rows) != 15:
        raise ValueError("Final shifted truth must contain 15 scenarios")
    for row in shifted_rows:
        if int(row["stage"]) != 142 or not _boolean(row["final"]):
            raise ValueError("Shifted truth is not from final stage142")
        if not _boolean(row["precision_pass"]):
            raise ValueError("Shifted truth precision failure")
        if not _boolean(row["independent_score_crosscheck"]):
            raise ValueError("Shifted truth lacks independent score cross-check")
        oracles[row["scenario_id"]] = {
            "scenario_id": row["scenario_id"],
            "truth": float(row["truth"]),
            "truth_mcse": float(row["truth_mcse"]),
            "typical_coefficient_se": float(row["typical_coefficient_se"]),
            "precision_pass": True,
            "exact_null_registered": _boolean(row["exact_null_registered"]),
            "truth_basis": row["truth_basis"],
            "provenance": "FINAL_SHIFTED_STAGE142",
        }
    expected = {row["scenario_id"] for row in registry}
    if set(oracles) != expected:
        raise ValueError("Oracle inventory does not match frozen registry")
    return oracles


def _load_attempts(outer_root: Path, scenario_id: str) -> list[dict]:
    paths = sorted((outer_root / "attempts" / scenario_id).glob("*.jsonl"))
    if len(paths) != 40:
        raise ValueError(f"Expected 40 checkpoint chunks for {scenario_id}")
    rows = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def run(
    *,
    registry_path: Path,
    calibration_model_path: Path,
    old_truth_path: Path,
    outer_root: Path,
    shifted_truth_root: Path,
    authorization_path: Path,
    binding_manifest_path: Path,
    runtime_qualification_path: Path,
    output: Path,
) -> dict:
    outer_authorization = authorize_final(
        purpose="outer",
        authorization_path=authorization_path,
        binding_manifest_path=binding_manifest_path,
        runtime_qualification_path=runtime_qualification_path,
    )
    truth_authorization = authorize_final(
        purpose="truth",
        authorization_path=authorization_path,
        binding_manifest_path=binding_manifest_path,
        runtime_qualification_path=runtime_qualification_path,
    )
    if outer_authorization.authorization_sha256 != truth_authorization.authorization_sha256:
        raise RuntimeError("Outer and truth authorization receipts differ")

    outer_receipt = verify_outer_payload(outer_root)
    truth_receipt = verify_truth_payload(
        shifted_truth_root,
        registry_path=registry_path,
        calibration_model_path=calibration_model_path,
    )
    outer_contract = read_json(outer_root / "00_RUN_CONTRACT.json")
    truth_contract = read_json(shifted_truth_root / "00_TRUTH_CONTRACT.json")
    if any(
        [
            outer_contract.get("mode") != "final",
            outer_contract.get("stage") != 141,
            outer_contract.get("attempts_per_scenario") != 4000,
            outer_receipt.get("scenario_count") != 40,
            outer_receipt.get("attempts") != 160000,
            outer_receipt.get("chunk_count") != 1600,
            outer_receipt.get("final") is not True,
            truth_contract.get("mode") != "final",
            truth_contract.get("stage") != 142,
            truth_receipt.get("scenario_count") != 15,
            truth_receipt.get("checkpoint_count") != 240,
            truth_receipt.get("all_precision_pass") is not True,
            truth_receipt.get("all_independent_score_crosschecks_pass") is not True,
            truth_receipt.get("final") is not True,
        ]
    ):
        raise ValueError("Final outer/truth receipts are incomplete")
    authorization_sha = outer_authorization.authorization_sha256
    manifest_sha = outer_authorization.binding_manifest_sha256
    runtime_sha = outer_authorization.runtime_receipt_sha256
    for payload in (outer_contract, outer_receipt, truth_contract, truth_receipt):
        if (
            payload.get("authorization_sha256") != authorization_sha
            or payload.get("binding_manifest_sha256") != manifest_sha
            or payload.get("runtime_receipt_sha256") != runtime_sha
        ):
            raise PermissionError("Final output does not bind exact GO/code/runtime")

    registry = load_registry(registry_path)
    shifted_truth_path = shifted_truth_root / "02_SHIFTED_TRUTH.csv"
    oracles = load_oracles(old_truth_path, shifted_truth_path, registry)
    results = [
        adjudicate_one(
            _load_attempts(outer_root, scenario["scenario_id"]),
            scenario,
            oracles[scenario["scenario_id"]],
        )
        for scenario in registry
    ]
    conjunction = full_conjunction(results, registry)

    output = Path(output)
    if output.exists():
        raise FileExistsError("Adjudication output exists; result is write-once")
    output.mkdir(parents=True)
    fieldnames = sorted({key for row in results for key in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(results)
    result_path = output / "01_SCENARIO_ADJUDICATION.csv"
    atomic_write_text(result_path, stream.getvalue())
    synthetic_pass = conjunction["g2c_synthetic_applicable_conjunction_pass"]
    gate = {
        "schema": "RP_V4_STAGE_G_SYNTHETIC_ADJUDICATION_1.0",
        **conjunction,
        "decision": (
            "G2C_SYNTHETIC_PASS__SEPARATE_REAL_OUTCOME_REVIEW_REQUIRED"
            if synthetic_pass
            else "G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE"
        ),
        "authorization_sha256": authorization_sha,
        "binding_manifest_sha256": manifest_sha,
        "runtime_receipt_sha256": runtime_sha,
        "outer_contract_sha256": sha256_file(outer_root / "00_RUN_CONTRACT.json"),
        "outer_chunk_manifest_sha256": sha256_file(
            outer_root / "01_CHUNK_MANIFEST.csv"
        ),
        "outer_accounting_sha256": sha256_file(
            outer_root / "02_ATTEMPT_ACCOUNTING.csv"
        ),
        "outer_receipt_sha256": sha256_file(outer_root / "03_RUN_RECEIPT.json"),
        "truth_contract_sha256": sha256_file(
            shifted_truth_root / "00_TRUTH_CONTRACT.json"
        ),
        "truth_scenario_manifest_sha256": sha256_file(
            shifted_truth_root / "01_TRUTH_SCENARIO_MANIFEST.csv"
        ),
        "truth_csv_sha256": sha256_file(shifted_truth_path),
        "truth_receipt_sha256": sha256_file(
            shifted_truth_root / "03_TRUTH_RECEIPT.json"
        ),
        "old_truth_sha256": sha256_file(old_truth_path),
        "scenario_adjudication_sha256": sha256_file(result_path),
        "real_WP2_outcomes_authorized": False,
        "external_disease_outcomes_authorized": False,
        "large_SRA_download_authorized": False,
        "manuscript_replacement_authorized": False,
        "G2D_permitted": False,
    }
    atomic_write_text(output / "02_FINAL_SYNTHETIC_GATE.json", stable_json(gate))
    return gate


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--calibration-model", type=Path, required=True)
    parser.add_argument("--old-truth", type=Path, required=True)
    parser.add_argument("--outer-root", type=Path, required=True)
    parser.add_argument("--shifted-truth-root", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--runtime-qualification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(
        stable_json(
            run(
                registry_path=arguments.registry,
                calibration_model_path=arguments.calibration_model,
                old_truth_path=arguments.old_truth,
                outer_root=arguments.outer_root,
                shifted_truth_root=arguments.shifted_truth_root,
                authorization_path=arguments.authorization,
                binding_manifest_path=arguments.binding_manifest,
                runtime_qualification_path=arguments.runtime_qualification,
                output=arguments.output,
            )
        ),
        end="",
    )
