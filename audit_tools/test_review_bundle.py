"""Focused regression tests for immutable review packaging and portable checks."""

import unittest
import importlib
import json

from phase17_postc9_06_build_correction_package import manifest_bytes, zip_bytes
from verify_review_bundle import AUTHOR_APPROVAL_EDITS, CONFIRMED, CONFIRMED_SCOPE_PATHS, archive_entries, require_review_status, safe_name, sha256, verify_confirmed_snapshot_scope, verify_document_provenance, verify_entries, verify_review_governance


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

    def confirmed_governance(self):
        entries, gate = self.governance()
        reviewed = {name:b"reviewed payload\n" for name in CONFIRMED_SCOPE_PATHS}
        for name, (before, _) in AUTHOR_APPROVAL_EDITS.items():
            reviewed[name] = (before + "\n").encode()
        manifest = manifest_bytes(reviewed)
        entries.update(reviewed)
        for name, (_, after) in AUTHOR_APPROVAL_EDITS.items():
            entries[name] = (after + "\n").encode()
        entries["governance/Reviewed_Package_MANIFEST_SHA256.csv"] = manifest
        receipt = {"record_type":"USER_MESSAGE_REPORTING_BOTH_AUTHORS",
                   "authors":["Zhi Chen","Teng Qi"],"statement":"Both authors confirm current materials.",
                   "current_content_confirmed":True,"external_feedback_and_disposition_considered":True,
                   "confirmation_date":"2026-08-28",
                   "reviewed_package":{"path":"04_submission/author_review.zip","bytes":100,
                                       "sha256":"A"*64,"manifest_sha256":sha256(manifest)}}
        for key in ("independently_collected_author_signatures", "external_reviewer_identity_authenticated",
                    "target_journal_selected", "apc_commitment_authorized", "new_archive_release_authorized",
                    "future_material_changes_preapproved", "submission_authorized"):
            receipt[key] = False
        entries["governance/author_confirmation.json"] = json.dumps(receipt).encode()
        gate.update({"author_review_of_external_feedback":True,
                     "confirmation_evidence_sha256":sha256(entries["governance/author_confirmation.json"]),
                     "reviewed_package_sha256":"A"*64})
        for author in gate["authors"]:
            author.update({"decision":CONFIRMED,"date":"2026-08-28","evidence":"author_confirmation.json"})
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        entries["governance/Author_Confirmation.md"] = (
            CONFIRMED + "\n" + "A"*64 + "\n- [x] Content confirmed\n"
            "## Decisions reserved for the authors\n- [ ] Submission\n").encode()
        return entries, gate

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

    def test_confirmed_snapshot_has_bounded_scope(self):
        entries, gate = self.confirmed_governance()
        self.assertEqual(verify_review_governance(entries),gate)
        self.assertEqual(verify_confirmed_snapshot_scope(entries,gate),41)

    def test_confirmation_requires_preserved_evidence(self):
        for key in ("author_confirmation.json", "Reviewed_Package_MANIFEST_SHA256.csv"):
            entries, _ = self.confirmed_governance()
            del entries["governance/"+key]
            with self.assertRaisesRegex(ValueError,"receipt and reviewed manifest"):
                verify_review_governance(entries)

    def test_confirmation_receipt_and_manifest_are_hash_bound(self):
        for key in ("author_confirmation.json", "Reviewed_Package_MANIFEST_SHA256.csv"):
            entries, _ = self.confirmed_governance()
            entries["governance/"+key] += b" "
            with self.assertRaises(ValueError):
                verify_review_governance(entries)

    def test_confirmation_cannot_authorize_future_actions(self):
        for key in ("submission_authorized", "new_archive_release_authorized",
                    "future_material_changes_preapproved", "target_journal_selected", "apc_commitment_authorized"):
            entries, gate = self.confirmed_governance()
            receipt = json.loads(entries["governance/author_confirmation.json"])
            receipt[key] = True
            entries["governance/author_confirmation.json"] = json.dumps(receipt).encode()
            gate["confirmation_evidence_sha256"] = sha256(entries["governance/author_confirmation.json"])
            entries["governance/review_gate.json"] = json.dumps(gate).encode()
            with self.assertRaisesRegex(ValueError,"reserved actions"):
                verify_review_governance(entries)

    def test_confirmed_form_cannot_check_reserved_decisions(self):
        entries, _ = self.confirmed_governance()
        entries["governance/Author_Confirmation.md"] += b"- [x] Journal selected\n"
        with self.assertRaisesRegex(ValueError,"remain unchecked"):
            verify_review_governance(entries)

    def test_confirmation_cannot_approve_extra_prose_edits(self):
        for name in ("Manuscript", "Cover_Letter", "Supplementary_Information", "Research_Proposal"):
            entries, gate = self.confirmed_governance()
            entries[f"sources/{name}.md"] += b"New claim.\n"
            with self.assertRaisesRegex(ValueError,"Unapproved content change"):
                verify_confirmed_snapshot_scope(entries,gate)

    def test_confirmation_cannot_approve_changed_figures_or_statistics(self):
        for name in ("figures/Figure_1.pdf", "additional_files/Full_Statistical_Results.zip"):
            entries, gate = self.confirmed_governance()
            entries[name] += b"changed"
            with self.assertRaisesRegex(ValueError,"Unapproved content change"):
                verify_confirmed_snapshot_scope(entries,gate)

    def test_partial_author_confirmation_is_not_both_authors(self):
        entries, gate = self.confirmed_governance()
        gate["authors"][1]["decision"] = "PENDING"
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"mixed decision"):
            verify_review_governance(entries)

    def test_author_consideration_is_not_independent_review(self):
        entries, gate = self.confirmed_governance()
        gate["reviewer_independence_confirmed"] = True
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"external methods approval"):
            verify_review_governance(entries)

    def test_author_confirmation_dates_must_match(self):
        entries, gate = self.confirmed_governance()
        gate["authors"][1]["date"] = "2026-08-27"
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"dates and evidence"):
            verify_review_governance(entries)

    def test_explicit_manuscript_and_cover_approval_binds_current_sources(self):
        entries, gate = self.confirmed_governance()
        receipt = json.loads(entries["governance/author_confirmation.json"])
        receipt["supplemental_document_approval"] = {
            "statement":"Manuscript and cover letter approved.", "confirmation_date":"2026-08-28",
            "approved_source_sha256":{name:sha256(entries[name]) for name in AUTHOR_APPROVAL_EDITS}}
        entries["governance/author_confirmation.json"] = json.dumps(receipt).encode()
        gate["confirmation_evidence_sha256"] = sha256(entries["governance/author_confirmation.json"])
        self.assertEqual(verify_confirmed_snapshot_scope(entries,gate),41)
        entries["sources/Cover_Letter.md"] += b"Another statement.\n"
        with self.assertRaisesRegex(ValueError,"differs from its explicit approval"):
            verify_confirmed_snapshot_scope(entries,gate)

    def test_known_presentation_issue_requires_its_record(self):
        entries, gate = self.confirmed_governance()
        gate["postapproval_presentation_issue"] = {
            "id":"F1C_THRESHOLD_LABEL", "scientific_values_changed":False,
            "status":"CORRECTED_PREVIEW_NOT_YET_INTEGRATED", "record":"Figure_1_Legend_Correction.md"}
        entries["governance/review_gate.json"] = json.dumps(gate).encode()
        with self.assertRaisesRegex(ValueError,"not fully disclosed"):
            verify_review_governance(entries)
        entries["governance/Figure_1_Legend_Correction.md"] = b"Correction preview; not integrated.\n"
        self.assertEqual(verify_review_governance(entries),gate)


if __name__ == "__main__":
    unittest.main()
