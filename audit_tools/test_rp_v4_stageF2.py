from __future__ import annotations

import csv
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from audit_tools import rp_v4_g2c_generator as stage_d_generator
from audit_tools import rp_v4_g2c_truth as stage_d_truth
from audit_tools import rp_v4_stageF2_adjudicator as adjudicator
from audit_tools import rp_v4_stageF2_common as common
from audit_tools import rp_v4_stageF2_generator as stage_f2_generator
from audit_tools import rp_v4_stageF2_truth as stage_f2_truth
from audit_tools.rp_v3_g2_estimation import TARGETS, responses
from audit_tools.rp_v4_g2c_hc3t import CRITICAL_VALUE, DF, METHOD, interval
from audit_tools.rp_v4_stageF2_common import ExecutionAuthorization
from audit_tools.rp_v4_stageF2_runner import run as run_outer
from audit_tools.rp_v4_stageF2_runner import verify_outer_payload


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "phase17_v7"
    / "rp_v4_redesign"
    / "20261010_stageC_single_g2c_external_input_protocol_freeze"
    / "05_G2C_FINAL_DGP_REGISTRY.csv"
)
MODEL = (
    ROOT
    / "phase17_v7"
    / "rp_v3_redesign"
    / "20261010_g2_implementation_freeze"
    / "02_G2_CALIBRATION_MODEL.json"
)


def authorization(stage: int, purpose: str, final: bool = False):
    return ExecutionAuthorization(stage=stage, purpose=purpose, final=final)


def valid_fit(
    *, point: float = 0.0, standard_error: float = 0.2
) -> dict:
    half = CRITICAL_VALUE * standard_error
    return {
        "estimand": "delta_profile",
        "point": point,
        "standard_error_HC3": standard_error,
        "df": DF,
        "critical_value": CRITICAL_VALUE,
        "ci_lower": point - half,
        "ci_upper": point + half,
        "max_point_leverage": 0.1,
        "method": METHOD,
        "data_kind": "SIMULATED_ONLY",
        "G2C_PASS": False,
        "WP2_REAL_EFFECT_UNLOCK": False,
    }


def attempt(attempt_id: int, *, status: str = "SUPPORTED") -> dict:
    row = {
        "scenario_id": "C0_X1",
        "scenario_index": 25,
        "attempt_id": attempt_id,
        "stage": 141,
        "seed_base": 2026101004,
        "data_kind": "SIMULATED_ONLY",
        "input_digest": "a" * 64,
        "status": status,
        "real_effects_fitted": False,
        "final_stream": True,
        "G2C_adjudicated": False,
        "external_disease_outcomes_fitted": False,
    }
    if status == "SUPPORTED":
        row["synthetic_HC3_t"] = valid_fit()
    elif status == "NUMERICAL_FAILURE":
        row["numerical_failure_type"] = "ArithmeticError"
    return row


class GeneratorTruthAndIntervalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.model = stage_f2_generator.load_inputs(REGISTRY, MODEL)

    def test_generator_matches_frozen_algorithm(self):
        old_stage = stage_d_generator.DEVELOPMENT_STAGE
        stage_d_generator.DEVELOPMENT_STAGE = 132
        try:
            for scenario_id in ("C0_X1", "C1_X2", "C2_X3"):
                index = next(
                    i for i, row in enumerate(self.rows) if row["scenario_id"] == scenario_id
                )
                expected = stage_d_generator.generate(
                    self.model, self.rows[index], index, 2, stage=132
                )
                observed = stage_f2_generator.generate(
                    self.model,
                    self.rows[index],
                    index,
                    2,
                    authorization(132, "outer"),
                )
                self.assertEqual(
                    stage_d_generator.data_digest(expected),
                    stage_f2_generator.data_digest(observed),
                )
        finally:
            stage_d_generator.DEVELOPMENT_STAGE = old_stage

    def test_truth_batch_matches_frozen_stage131_algorithm(self):
        scenario = self.rows[26]
        expected = stage_d_truth._coupled_batch(self.model, scenario, 26, 0, 64)
        observed = stage_f2_truth._coupled_batch(
            self.model,
            scenario,
            26,
            0,
            64,
            authorization(131, "truth"),
        )
        for key in ("attempts", "n0", "n1", "sum0", "sum1", "sq0", "sq1"):
            self.assertEqual(expected[key], observed[key])
        self.assertTrue(observed["independent_score_crosscheck"])

    def test_reference_score_is_independent_and_identical(self):
        auth = authorization(132, "outer")
        synthetic = stage_f2_generator.generate(
            self.model, self.rows[25], 25, 1, auth
        )
        expected_valid, expected_score = stage_d_truth._score_delta(
            synthetic["categories"], synthetic["n"], self.model
        )
        observed_valid, observed_score = stage_f2_truth._score_delta_reference(
            synthetic["categories"], synthetic["n"], self.model
        )
        self.assertTrue(np.array_equal(expected_valid, observed_valid))
        self.assertTrue(
            np.allclose(expected_score, observed_score, rtol=1e-12, atol=1e-12)
        )

    def test_interval_matches_direct_hc3_algebra(self):
        rng = np.random.default_rng(991)
        disease = np.r_[np.zeros(31), np.ones(37)]
        age = rng.normal(size=68)
        sex = np.r_[np.zeros(34), np.ones(34)]
        X = np.column_stack((np.ones(68), disease, age, sex))
        Y = rng.normal(size=(68, len(TARGETS)))
        observed = interval(X, Y, data_kind="SIMULATED_ONLY")
        target = TARGETS.index("delta_profile")
        inverse = np.linalg.inv(X.T @ X)
        beta = inverse @ X.T @ Y[:, target]
        residual = Y[:, target] - X @ beta
        leverage = np.einsum("ij,jk,ik->i", X, inverse, X)
        adjusted = residual / (1.0 - leverage)
        meat = X.T @ ((adjusted**2)[:, None] * X)
        covariance = inverse @ meat @ inverse
        expected_se = math.sqrt(covariance[1, 1])
        self.assertAlmostEqual(observed["point"], beta[1], places=12)
        self.assertAlmostEqual(observed["standard_error_HC3"], expected_se, places=12)
        adjudicator.validate_interval(observed)

    def test_interval_endpoint_shift_is_rejected(self):
        value = valid_fit()
        value["ci_lower"] += 0.001
        with self.assertRaises(ValueError):
            adjudicator.validate_interval(value)

    def test_interval_df_method_and_real_flags_are_rejected(self):
        for key, value in (
            ("df", 63),
            ("method", "alternate"),
            ("data_kind", "REAL"),
            ("G2C_PASS", True),
        ):
            fit = valid_fit()
            fit[key] = value
            with self.subTest(key=key), self.assertRaises((ValueError, PermissionError)):
                adjudicator.validate_interval(fit)


class OuterIntegrityTests(unittest.TestCase):
    def _run(self, root: Path, scenarios=("C0_X1",), attempts=2):
        return run_outer(
            registry_path=REGISTRY,
            calibration_model_path=MODEL,
            output=root,
            mode="qualification",
            selected_scenarios=scenarios,
            qualification_attempts=attempts,
        )

    def test_resume_is_byte_stable_and_fully_reconciled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outer"
            first = self._run(root)
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            second = run_outer(
                registry_path=REGISTRY,
                calibration_model_path=MODEL,
                output=root,
                mode="qualification",
                resume=True,
                selected_scenarios=("C0_X1",),
                qualification_attempts=2,
            )
            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)
            self.assertEqual(first["attempts"], 2)
            self.assertEqual(second["invocation_reused_chunks"], 1)
            verify_outer_payload(root)

    def test_chunk_payload_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outer"
            self._run(root)
            payload = next((root / "attempts").rglob("*.jsonl"))
            rows = [json.loads(line) for line in payload.read_text(encoding="utf-8").splitlines()]
            rows[0]["status"] = "SUPPORT_STOP"
            payload.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaises(RuntimeError):
                verify_outer_payload(root)

    def test_accounting_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outer"
            self._run(root)
            accounting = root / "02_ATTEMPT_ACCOUNTING.csv"
            accounting.write_text(
                accounting.read_text(encoding="utf-8").replace(",2,", ",3,"),
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                verify_outer_payload(root)

    def test_chunk_swap_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "outer"
            self._run(root, scenarios=("C0_X1", "C1_X2"), attempts=1)
            paths = sorted((root / "attempts").rglob("*.jsonl"))
            first, second = paths[0].read_bytes(), paths[1].read_bytes()
            paths[0].write_bytes(second)
            paths[1].write_bytes(first)
            with self.assertRaises(RuntimeError):
                verify_outer_payload(root)

    def test_final_requires_all_exact_code_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(PermissionError):
                run_outer(
                    registry_path=REGISTRY,
                    calibration_model_path=MODEL,
                    output=Path(temporary) / "final",
                    mode="final",
                )


class AuthorizationAndTruthCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.model = stage_f2_generator.load_inputs(REGISTRY, MODEL)

    def _manifest(self, root: Path, omit: str | None = None) -> Path:
        rows = []
        for relative in sorted(common.REQUIRED_BINDING_PATHS):
            if relative == omit:
                continue
            source = ROOT / relative
            rows.append(
                {
                    "path": relative,
                    "bytes": source.stat().st_size,
                    "sha256": common.sha256_file(source),
                }
            )
        path = root / "binding.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("path", "bytes", "sha256"))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_truth_helper_is_mandatory_in_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._manifest(
                Path(temporary), omit="audit_tools/rp_v4_g2c_truth.py"
            )
            with self.assertRaises(ValueError):
                common.verify_binding_manifest(manifest)

    def test_runtime_version_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self._manifest(root)
            manifest_sha = common.verify_binding_manifest(manifest)
            receipt = {
                "schema": "RP_V4_STAGE_F2_WINDOWS_QUALIFICATION_1.0",
                **common.runtime_identity(),
                "binding_manifest_sha256": manifest_sha,
                "stage141_started": False,
                "stage142_started": False,
            }
            receipt["numpy"] = "0.0.0"
            path = root / "runtime.json"
            path.write_text(common.stable_json(receipt), encoding="utf-8")
            with self.assertRaises(PermissionError):
                common.verify_runtime_qualification(path, manifest_sha)

    def test_dirty_worktree_gate_is_fail_closed(self):
        completed = mock.Mock(stdout=" M README.md\n")
        with mock.patch("audit_tools.rp_v4_stageF2_common.subprocess.run", return_value=completed):
            with self.assertRaises(PermissionError):
                common.require_clean_worktree()

    def test_truth_partial_file_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "truth"
            root.mkdir()
            (root / "orphan.partial").write_text("x", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                stage_f2_truth.run(
                    registry_path=REGISTRY,
                    calibration_model_path=MODEL,
                    output=root,
                    mode="qualification",
                    resume=True,
                    selected_scenarios=("C0_X1",),
                )

    def test_truth_checkpoint_reproduces_fixed_stream_and_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            auth = authorization(132, "truth")
            scenario = self.rows[25]
            expected = stage_f2_truth._coupled_batch(
                self.model, scenario, 25, 0, 64, auth
            )
            contract = root / "00_TRUTH_CONTRACT.json"
            contract.write_text("{}\n", encoding="utf-8")
            payload, seal = stage_f2_truth._batch_paths(root, "C0_X1", 0)
            payload.parent.mkdir(parents=True)
            common.atomic_write_text(payload, common.stable_json(expected))
            stage_f2_truth._batch_seal(
                root, payload, seal, common.sha256_file(contract)
            )
            stage_f2_truth._verify_batch_pair(
                root=root,
                payload=payload,
                seal=seal,
                contract_sha=common.sha256_file(contract),
                expected=expected,
            )
            altered = dict(expected)
            altered["sum1"] += 0.01
            payload.write_text(common.stable_json(altered), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                stage_f2_truth._verify_batch_pair(
                    root=root,
                    payload=payload,
                    seal=seal,
                    contract_sha=common.sha256_file(contract),
                    expected=expected,
                )


class AdjudicatorSafetyTests(unittest.TestCase):
    def test_missing_duplicate_and_real_attempts_are_rejected(self):
        with self.assertRaises(ValueError):
            adjudicator.validate_attempts([attempt(1)], "C0_X1", 25)
        rows = [attempt(i) for i in range(1, 4001)]
        rows[-1]["attempt_id"] = 1
        with self.assertRaises(ValueError):
            adjudicator.validate_attempts(rows, "C0_X1", 25)
        rows = [attempt(i) for i in range(1, 4001)]
        rows[0]["disease_group"] = "SLE"
        with self.assertRaises(PermissionError):
            adjudicator.validate_attempts(rows, "C0_X1", 25)

    def test_attempt_interval_algebra_is_mandatory(self):
        rows = [attempt(i) for i in range(1, 4001)]
        rows[0]["synthetic_HC3_t"]["ci_upper"] += 0.01
        with self.assertRaises(ValueError):
            adjudicator.validate_attempts(rows, "C0_X1", 25)

    def test_wilson_reference(self):
        lower, upper = adjudicator.wilson_interval(3800, 4000)
        self.assertGreater(lower, 0.94)
        self.assertLess(upper, 0.96)


if __name__ == "__main__":
    unittest.main()
