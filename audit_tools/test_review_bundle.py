"""Focused regression tests for immutable review packaging and portable checks."""

import unittest
import importlib
import json

from phase17_postc9_06_build_correction_package import manifest_bytes, zip_bytes
from verify_review_bundle import archive_entries, require_review_status, safe_name, sha256, verify_document_provenance, verify_entries, verify_review_governance


class ReviewBundleTests(unittest.TestCase):
    def governance(self):
        gate = {"gate":"EXTERNAL_METHODS_REVIEW_AND_AUTHOR_REAPPROVAL_GATE",
                "external_feedback_received":True,
                "external_methods_review_status":"FEEDBACK_RECEIVED_CLOSURE_PENDING",
                "reviewer_identity":None,"reviewer_independence_confirmed":False,
                "external_methods_review_decision":None,"submission_authorized":False,
                "authors":[{"name":name,"decision":"PENDING","date":None,"evidence":None}
                           for name in ("Zhi Chen","Teng Qi")]}
        entries = {"governance/"+name:b"- [ ] Pending\n" for name in
                   ("Author_Confirmation.md","Reporting_Checklist.md","External_Methods_Review.md")}
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        return entries, gate

    def payload(self):
        entries = {"data/result.csv":b"name,value\nA,1\n"}
        entries["MANIFEST_SHA256.csv"] = manifest_bytes(entries)
        return entries

    def test_valid_manifest_and_deterministic_zip(self):
        entries = self.payload()
        self.assertEqual(verify_entries(entries,"MANIFEST_SHA256.csv"),1)
        first = zip_bytes(entries)
        self.assertEqual(first,zip_bytes(dict(reversed(list(entries.items())))))
        self.assertEqual(archive_entries(first),entries)

    def test_tampered_payload_rejected(self):
        entries = self.payload()
        entries["data/result.csv"] = b"name,value\nA,2\n"
        with self.assertRaises(ValueError):
            verify_entries(entries,"MANIFEST_SHA256.csv")

    def test_missing_and_extra_payloads_rejected(self):
        for missing in (True,False):
            entries = self.payload()
            if missing:
                del entries["data/result.csv"]
            else:
                entries["unlisted.txt"] = b"extra"
            with self.assertRaises(ValueError):
                verify_entries(entries,"MANIFEST_SHA256.csv")

    def test_path_escape_rejected(self):
        for value in ("../data", "/absolute", "C:/data", "data\\file", "a/../b", "a//b"):
            with self.assertRaises(ValueError):
                safe_name(value)

    def test_review_status_cannot_be_promoted(self):
        valid = {"review_only":True,"submission_authorized":False,
                 "corrected_disease_outcomes_estimated":False,
                 "matching_archive_doi":None,"author_reapproval":"PENDING"}
        require_review_status(valid)
        for key,value in (("submission_authorized",True),("corrected_disease_outcomes_estimated",True),
                          ("matching_archive_doi","10.0000/example"),("author_reapproval","APPROVED")):
            with self.assertRaises(ValueError):
                require_review_status({**valid,key:value})

    def test_legacy_source_and_package_writers_are_retired(self):
        for name in ("phase17_c8brf_02_build_submission_sources", "phase17_c8brf_03_build_documents"):
            with self.assertRaisesRegex(RuntimeError, "Retired"):
                importlib.import_module(name).main()

    def test_stale_markdown_cannot_share_document_approval(self):
        entries, rows = {}, []
        for name in ("Manuscript","Supplementary_Information","Research_Proposal","Cover_Letter"):
            entries[f"sources/{name}.md"] = b"source"
            entries[f"documents/{name}.docx"] = b"document"
            rows.append({"source":f"source/{name}.md","output":f"documents/{name}.docx",
                         "source_sha256":sha256(b"source"),"docx_sha256":sha256(b"document")})
        verify_document_provenance(entries,rows)
        entries["sources/Manuscript.md"] = b"changed after render"
        with self.assertRaisesRegex(ValueError,"different snapshots"):
            verify_document_provenance(entries,rows)

    def test_current_governance_is_complete_and_pending(self):
        entries, gate = self.governance()
        self.assertEqual(verify_review_governance(entries),gate)
        del entries["governance/External_Methods_Review.md"]
        with self.assertRaisesRegex(ValueError,"incomplete"):
            verify_review_governance(entries)

    def test_feedback_cannot_become_external_signoff(self):
        entries, gate = self.governance()
        gate["external_methods_review_decision"] = "APPROVED"
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"external methods approval"):
            verify_review_governance(entries)

    def test_author_approval_cannot_be_invented(self):
        entries, gate = self.governance()
        gate["authors"][0]["decision"] = "APPROVED"
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"author reapproval"):
            verify_review_governance(entries)

    def test_old_checked_forms_are_rejected(self):
        for name,text in (("Author_Confirmation.md",b"- [X] Approved\n"),
                          ("Reporting_Checklist.md",b"Earlier package record: 46/46\n")):
            entries, _ = self.governance()
            entries["governance/"+name] = text
            with self.assertRaises(ValueError):
                verify_review_governance(entries)


if __name__ == "__main__":
    unittest.main()
