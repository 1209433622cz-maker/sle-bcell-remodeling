"""Fail-closed tests for public repository verification."""
from __future__ import annotations

import importlib.util
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "audit_quality_control/verify_repository.py"
SPEC = importlib.util.spec_from_file_location("public_repository", MODULE)
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)
sys.path.insert(0, str(MODULE.parent))
import verify_git_inventory as git_verify


class PublicRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "payload.txt").write_text("fixed evidence\n", encoding="utf-8")
        self.row = {"path": "payload.txt", "bytes": (self.root / "payload.txt").stat().st_size,
                    "sha256": verify.sha256(self.root / "payload.txt")}

    def test_valid_manifest(self):
        self.assertEqual(verify.validate_manifest(self.root, [self.row]), [])

    def test_altered_payload(self):
        (self.root / "payload.txt").write_text("changed evidence\n", encoding="utf-8")
        self.assertTrue(verify.validate_manifest(self.root, [self.row]))

    def test_missing_payload(self):
        (self.root / "payload.txt").unlink()
        self.assertTrue(verify.validate_manifest(self.root, [self.row]))

    def test_wrong_size(self):
        self.assertTrue(verify.validate_manifest(self.root, [dict(self.row, bytes=999)]))

    def test_wrong_hash(self):
        self.assertTrue(verify.validate_manifest(self.root, [dict(self.row, sha256="0" * 64)]))

    def test_duplicate_manifest(self):
        self.assertTrue(verify.validate_manifest(self.root, [self.row, self.row]))

    def test_empty_manifest(self):
        self.assertTrue(verify.validate_manifest(self.root, []))

    def test_path_traversal(self):
        for path in ("../secret", "/secret", "C:/secret", "folder\\secret", "./payload.txt", "folder/../payload.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                verify.safe_asset(self.root, path)

    def test_bad_metadata(self):
        for row in ({"path": "payload.txt"}, dict(self.row, bytes=-1), dict(self.row, sha256="bad")):
            with self.subTest(row=row):
                self.assertTrue(verify.validate_manifest(self.root, [row]))

    def test_links_and_external_skip(self):
        (self.root / "README.md").write_text("[local](payload.txt) [web](https://example.org/x) [anchor](#test)", encoding="utf-8")
        self.assertEqual(verify.validate_links(self.root, ("README.md",)), (1, []))

    def test_broken_links(self):
        (self.root / "README.md").write_text("[missing](absent.txt)", encoding="utf-8")
        self.assertTrue(verify.validate_links(self.root, ("README.md",))[1])

    def test_outside_link(self):
        (self.root / "README.md").write_text("[escape](../../secret)", encoding="utf-8")
        self.assertTrue(verify.validate_links(self.root, ("README.md",))[1])

    def test_gate_fail_closed(self):
        gate = {"decision": "PASS_STAGE_M_FROZEN__HOLD_OUTCOMES",
                "checks": {key: False for key in ("raw_download_started", "external_outcome_fitted", "expression_outcome_accessed")},
                "automatic_unlocks": {key: False for key in ("raw_download", "count_reconstruction", "external_outcomes", "submission")}}
        self.assertEqual(verify.gate_boundary_errors(gate), [])
        gate["automatic_unlocks"]["external_outcomes"] = True
        self.assertTrue(verify.gate_boundary_errors(gate))

    def test_missing_gate_flags(self):
        self.assertTrue(verify.gate_boundary_errors({"decision": "PASS_STAGE_M_FROZEN"}))


class GitInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "config", "core.autocrlf", "false"], check=True)
        (self.root / "evidence.txt").write_bytes(b"frozen\n")
        subprocess.run(["git", "-C", str(self.root), "add", "evidence.txt"], check=True)
        self.row = {"path": "evidence.txt", "bytes": 7, "sha256": hashlib.sha256(b"frozen\n").hexdigest(),
                    "git_blob": git_verify.git_objects(self.root)["evidence.txt"]}

    def test_valid_git_inventory_and_checkout_eol(self):
        (self.root / "evidence.txt").write_bytes(b"frozen\r\n")
        self.assertEqual(git_verify.verify_inventory(self.root, [self.row])["status"], "PASS")

    def test_git_inventory_wrong_hash_or_object(self):
        for row in (dict(self.row, sha256="0" * 64), dict(self.row, git_blob="0" * 40)):
            with self.subTest(row=row):
                self.assertEqual(git_verify.verify_inventory(self.root, [row])["status"], "FAIL")

    def test_git_inventory_duplicate_or_empty(self):
        for rows in ([], [self.row, self.row]):
            self.assertEqual(git_verify.verify_inventory(self.root, rows)["status"], "FAIL")

    def test_git_inventory_missing_coverage(self):
        (self.root / "extra.txt").write_bytes(b"extra\n")
        subprocess.run(["git", "-C", str(self.root), "add", "extra.txt"], check=True)
        self.assertEqual(git_verify.verify_inventory(self.root, [self.row])["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
