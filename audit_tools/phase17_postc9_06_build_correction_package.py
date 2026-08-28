"""Build a separate, deterministic correction-review bundle; never publish it."""

import argparse
import csv
import io
import json
from pathlib import Path
import zipfile

from docx_a11y_audit import audit as a11y_audit
from verify_review_bundle import CONFIRMED, archive_entries, csv_records, safe_name, sha256, verify_bundle, verify_entries, verify_review_governance


ROOT = Path(__file__).resolve().parents[1]
ZIP_TIME = (2026, 8, 28, 0, 0, 0)
C9_NAMES = (
    "01_INPUT_SHA256_MANIFEST.csv", "02_PROTECTED_METADATA_CONTRACT.json",
    "04_EXECUTION_PROVENANCE.json", "05_REFERENCE_MODEL_FEATURES.csv",
    "06_MAPPER_DONOR_GROUPED_CV.csv", "07_MAPPER_CONFIDENCE_CALIBRATION.csv",
    "09_FROZEN_MAPPER_PARAMETERS.csv", "11_SAMPLE_PREFREEZE_SUMMARY.csv",
    "12_CLUSTER_SELECTION_AUDIT.csv", "13_LINEAGE_MODULE_AVAILABILITY.csv",
    "14_PROGRAM_GENE_AVAILABILITY.csv", "15_GATE_C9A_PREFREEZE_DECISION.json",
    "16_GATE_C9A_PREFREEZE_REVIEW.md", "17_FILE_INTEGRITY_MANIFEST.csv",
)


def csv_bytes(rows):
    if not rows:
        raise ValueError("Cannot write an empty manifest")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def manifest_bytes(entries):
    return csv_bytes([{"relative_path":name,"bytes":len(payload),"sha256":sha256(payload)}
                      for name,payload in sorted(entries.items())])


def zip_bytes(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name,payload in sorted(entries.items()):
            safe_name(name)
            info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info,payload,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return stream.getvalue()


def verify_directory_manifest(directory, name):
    rows = csv_records((directory/name).read_bytes())
    for row in rows:
        rel = safe_name(row.get("relative_path",row.get("filename", "")))
        path = directory/rel
        if not path.resolve().is_relative_to(directory.resolve()):
            raise ValueError("Manifest path leaves source directory")
        payload = path.read_bytes()
        if len(payload) != int(row.get("bytes",row.get("size_bytes"))) or sha256(payload) != row["sha256"]:
            raise ValueError(f"Frozen source changed: {path}")
    return rows


def build(args):
    output, documents, figures, audit_dir = args.output_dir.resolve(), args.document_dir.resolve(), args.figure_review.resolve(), args.audit_dir.resolve()
    if not output.is_relative_to(ROOT/"04_submission") or output == ROOT/"04_submission/journal_submission":
        raise ValueError("Output must be a new review directory inside 04_submission, never the historical package")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Review output is not empty; preserve it and choose a new output directory")
    archive_path = output.with_suffix(".zip")
    if archive_path.exists():
        raise ValueError("Review archive already exists; no overwrite permitted")
    old = ROOT/"04_submission/journal_submission"
    c9 = ROOT/"phase17_v7/gateC9R/20260828_normalization_correction"
    verify_directory_manifest(old,"MANIFEST_SHA256.csv")
    verify_directory_manifest(figures,"02_REVIEW_FIGURE_MANIFEST.csv")
    c9_manifest = verify_directory_manifest(c9,"17_FILE_INTEGRITY_MANIFEST.csv")
    decision = json.loads((c9/"15_GATE_C9A_PREFREEZE_DECISION.json").read_text())
    if decision["outcome_unlock_authorized"] or decision["decision"] != "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED":
        raise ValueError("This builder represents the corrected HOLD only")
    for row in csv_records((c9/"01_INPUT_SHA256_MANIFEST.csv").read_bytes()):
        if row["path"].startswith("audit_tools/") and sha256((ROOT/row["path"]).read_bytes()) != row["sha256"]:
            raise ValueError("Scientific code changed since the corrected run")
    recount = json.loads((audit_dir/"calibration_recount_audit.json").read_text())
    if recount["status"] != "PASS_INDEPENDENT_IMPLEMENTATION_RECOUNT" or recount["calibration_rows"] != 72:
        raise ValueError("Calibration recount is missing or incomplete")
    document_build = documents.parent/"03_REVIEW_DOCUMENT_BUILD.json"
    builds = json.loads(document_build.read_text())["documents"]
    if len(builds) != 4:
        raise ValueError("Four current DOCX build records are required")
    for row in builds:
        if sha256((ROOT/row["source"]).read_bytes()) != row["source_sha256"] or sha256((ROOT/row["output"]).read_bytes()) != row["docx_sha256"]:
            raise ValueError("Canonical sources or DOCX changed since document generation")

    payloads, provenance, portal = {}, [], []

    def add(source, name):
        safe_name(name)
        if name in payloads:
            raise ValueError(f"Duplicate target {name}")
        payloads[name] = source.read_bytes()
        provenance.append({"package_path":name,"source_path":source.relative_to(ROOT).as_posix(),
                           "bytes":len(payloads[name]),"sha256":sha256(payloads[name])})

    for title, folder in (("Manuscript","main_text"),("Supplementary_Information","additional_files"),
                          ("Cover_Letter","submission_docs"),("Research_Proposal","research_plan")):
        for ext in ("docx","pdf"):
            add(documents/f"{title}.{ext}",f"{folder}/{title}.{ext}")
        source_folder = "04_submission" if title == "Cover_Letter" else "01_manuscript"
        add(ROOT/source_folder/f"{title}.md",f"sources/{title}.md")
    for path in sorted((figures/"figures").iterdir()):
        if path.suffix not in {".pdf", ".png"}:
            continue
        if path.name.startswith("Figure"):
            number = path.stem.split("_")[0].removeprefix("Figure")
            name = f"figures/Figure_{number}{path.suffix}"
        else:
            number = path.stem.split("_")[2]
            name = f"figures_supplementary/Supplementary_Figure_{number}{path.suffix}"
        add(path, name)
    if len([name for name in payloads if name.startswith("figures/")]) != 10 or len([name for name in payloads if name.startswith("figures_supplementary/")]) != 20:
        raise ValueError("Expected five main and ten supplementary figures, PDF and PNG")
    source_entries = {path.name:path.read_bytes() for path in (figures/"source_data").glob("*.csv")}
    if len(source_entries) != 15:
        raise ValueError("Expected fifteen figure source tables")
    source_entries["MANIFEST_SHA256.csv"] = manifest_bytes(source_entries)
    payloads["additional_files/Figure_Source_Data.zip"] = zip_bytes(source_entries)
    regulator = old/"additional_files/Regulator_Sensitivity.zip"
    verify_entries(archive_entries(regulator.read_bytes()),"SHA256SUMS.csv")
    add(regulator,"additional_files/Regulator_Sensitivity.zip")
    old_stats_path = old/"additional_files/Full_Statistical_Results.zip"
    old_stats = archive_entries(old_stats_path.read_bytes())
    if verify_entries(old_stats,"MANIFEST_SHA256.csv") != 163:
        raise ValueError("Unexpected historical statistical archive")
    stats = {name:payload for name,payload in old_stats.items() if name != "MANIFEST_SHA256.csv"}
    extension = {name:(c9/name).read_bytes() for name in C9_NAMES}
    for name in ("calibration_recount.csv","calibration_recount_audit.json"):
        extension[name] = (audit_dir/name).read_bytes()
    extension["Supplementary_Figure_S10_source_data.csv"] = source_entries["Supplementary_Figure_S10_source_data.csv"]
    extension["CORRECTION_CONTRACT.md"] = (ROOT/"00_project_management/gateC9_technical_correction_contract_2026-08-28.md").read_bytes()
    omitted = [row for row in c9_manifest if row["filename"] not in C9_NAMES]
    extension["LOCAL_ONLY_PAYLOADS.csv"] = csv_bytes(omitted)
    extension["README.md"] = (
        "# Corrected external-mapping calibration\n\n"
        "Reference and external cells use full-library log1p(CP10K). All 56 matrices "
        "were processed, but the primary elastic-net B_ASC precision (0.885210) did "
        "not meet 0.90. No corrected disease outcome was estimated. Original C9 "
        "effects are excluded from supporting evidence. The source-label-defined "
        "primary GSE135779 replication is unchanged.\n\n"
        "The 72 candidate rows and donor-grouped folds are reference calibration "
        "diagnostics, not independently held-out performance. Original outcomes "
        "were known before correction. Centroid success does not replace the "
        "required primary mapper.\n\n"
        "The original 17_FILE_INTEGRITY_MANIFEST.csv records a LOCAL run, including "
        "three omitted per-cell payloads listed in LOCAL_ONLY_PAYLOADS.csv. It is "
        "provenance, not a completeness manifest for this subset. The enclosing "
        "MANIFEST_SHA256.csv is the complete attachment manifest.\n"
    ).encode()
    if len(extension) != 20 or len(omitted) != 3:
        raise ValueError("Calibration extension differs from Supplementary Table S8")
    for name,payload in extension.items():
        stats["external_mapping_calibration/"+name] = payload
    stats["README_CURRENT_SCOPE.md"] = (
        "# Current review scope\n\nThe 163 historical statistical payloads remain byte-identical. "
        "external_mapping_calibration/ adds 20 correction records; no new disease "
        "effects are present. This supplement is review-only and has no matching new DOI.\n"
    ).encode()
    if not all(stats[name] == payload for name,payload in old_stats.items() if name != "MANIFEST_SHA256.csv"):
        raise ValueError("Historical statistical payload changed")
    stats["MANIFEST_SHA256.csv"] = manifest_bytes(stats)
    payloads["additional_files/Full_Statistical_Results.zip"] = zip_bytes(stats)
    code_names = ["phase17_c9_common.py","phase17_c9_01_prefreeze_label_agnostic_mapping.py",
                  "phase17_c9_02_unlock_outcomes_and_review.py","run_6013RP_phase17_gateC9_label_agnostic_gse135779.ps1",
                  "test_phase17_c9_contracts.py","phase17_postc9_05_recheck_calibration.py",
                  "phase17_postc9_06_build_correction_package.py","docx_a11y_audit.py"]
    for name in code_names:
        add(ROOT/"audit_tools"/name,"reproducibility/"+name)
    add(ROOT/"audit_tools/verify_review_bundle.py","verify_review_bundle.py")
    for name in ("REPRODUCIBILITY.md","LICENSE","LICENSE_CONTENT_CC_BY_4.0.md","LICENSE_SCOPE.md"):
        add(ROOT/name,"reproducibility/"+name)
    add(ROOT/"Data/README.md","reproducibility/DATA_RETRIEVAL.md")
    for name in ("Author_Confirmation.md", "Reporting_Checklist.md"):
        add(ROOT/"04_submission"/name, "governance/"+name)
    for name in ("External_Methods_Review.md", "review_gate.json"):
        add(audit_dir/name, "governance/"+name)
    if (audit_dir/"author_confirmation.json").exists():
        for name in ("author_confirmation.json", "Reviewed_Package_MANIFEST_SHA256.csv"):
            add(audit_dir/name, "governance/"+name)
    if (audit_dir/"Figure_1_Legend_Correction.md").exists():
        add(audit_dir/"Figure_1_Legend_Correction.md", "governance/Figure_1_Legend_Correction.md")
    governance = verify_review_governance(payloads)
    author_state = governance["authors"][0]["decision"]
    if author_state == CONFIRMED:
        reviewed = json.loads(payloads["governance/author_confirmation.json"])["reviewed_package"]
        reviewed_path = (ROOT/safe_name(reviewed["path"])).resolve()
        if not reviewed_path.is_relative_to(ROOT/"04_submission"):
            raise ValueError("Reviewed snapshot is outside the submission workspace")
        reviewed_bytes = reviewed_path.read_bytes()
        if len(reviewed_bytes) != reviewed["bytes"] or sha256(reviewed_bytes) != reviewed["sha256"]:
            raise ValueError("Author-reviewed package changed after confirmation")
        reviewed_entries = archive_entries(reviewed_bytes)
        verify_entries(reviewed_entries, "MANIFEST_SHA256.csv")
        if reviewed_entries["MANIFEST_SHA256.csv"] != payloads["governance/Reviewed_Package_MANIFEST_SHA256.csv"]:
            raise ValueError("Reviewed snapshot manifest differs from the preserved ZIP")
    add(audit_dir/"document_pages/document_render_audit.json","quality_control/document_render_audit.json")
    add(document_build,"quality_control/document_build.json")
    accessibility = []
    for title in ("Manuscript","Supplementary_Information","Cover_Letter","Research_Proposal"):
        record = a11y_audit(documents/f"{title}.docx")
        record["file"] = title+".docx"
        accessibility.append(record)
    payloads["quality_control/accessibility.json"] = (json.dumps(accessibility,indent=2)+"\n").encode()
    add(figures/"01_FIGURE_BUILD_ASSERTIONS.json","quality_control/figure_build_assertions.json")
    add(ROOT/"00_project_management/post_gateC9_audit_2026-08-28/figure_typography.csv","quality_control/figure_typography.csv")
    payloads["SOURCE_PROVENANCE.csv"] = csv_bytes(provenance)
    roles = [("main manuscript","main_text/Manuscript.docx"),
             ("supplementary information","additional_files/Supplementary_Information.docx"),
             ("cover letter","submission_docs/Cover_Letter.docx")]
    roles += [(name.removesuffix(".zip"),"additional_files/"+name) for name in ("Figure_Source_Data.zip","Regulator_Sensitivity.zip","Full_Statistical_Results.zip")]
    roles += [(f"main figure {number}",f"figures/Figure_{number}.pdf") for number in range(1,6)]
    for role,name in roles:
        portal.append({"role":role,"path":name,"bytes":len(payloads[name]),"sha256":sha256(payloads[name]),"authorization":"DRAFT_NOT_FOR_UPLOAD"})
    payloads["PORTAL_FILES.csv"] = csv_bytes(portal)
    payloads["STATUS.json"] = (json.dumps({
        "review_only":True,"submission_authorized":False,"author_reapproval":author_state,
        "reviewed_package_sha256":governance.get("reviewed_package_sha256"),
        "author_review_of_external_feedback":governance.get("author_review_of_external_feedback",False),
        "journal_requirement":governance.get("journal_requirement"),
        "postapproval_presentation_issue":governance.get("postapproval_presentation_issue"),
        "external_methods_review_status":governance["external_methods_review_status"],
        "target_journal":None,"matching_archive_doi":None,"initial_archive_doi":"10.5281/zenodo.22086892",
        "corrected_disease_outcomes_estimated":False,"calibration_status":decision["decision"],
        "identity_status":"HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY",
        "historical_statistical_payloads_unchanged":163,"calibration_extension_files":20,
        "historical_statistical_archive_sha256":sha256(old_stats_path.read_bytes()),
    },indent=2)+"\n").encode()
    payloads["README.md"] = (
        "# Correction review bundle\n\n**REVIEW ONLY. NOT AUTHORIZED FOR SUBMISSION.**\n\n"
        "The original C9 PASS is superseded. Corrected calibration remains HOLD; "
        "no new disease outcome was estimated. R1 identity HOLD also remains. "
        "The source-label-defined primary IFN replication is unchanged.\n\n"
        "This package contains four review documents, five main and ten supplementary "
        "figures, fifteen figure source tables, full statistical results and compact "
        "correction provenance. PORTAL_FILES.csv contains draft roles, not upload "
        "authorization. Filenames are journal-neutral.\n\n"
        "governance/ records current author decisions, a current-only checklist "
        "and an external methods-review dossier. When confirmation is recorded, "
        "its receipt binds the earlier reviewed ZIP and permits only the specified "
        "administrative approval-statement updates. It is not approval of future "
        "scientific changes, journal choice, a new release or actual submission. "
        "Reviewer identity and an independent methods decision remain unverified.\n\n"
        "STATUS.json also records any known postapproval presentation issue. "
        "Its correction preview is separate; do not submit a reviewed snapshot "
        "before the documented correction is integrated and checked.\n\n"
        "Run `python -I -S verify_review_bundle.py --bundle .` after extraction. "
        "A passing result verifies technical integrity and boundaries, not scientific "
        "validity, author identity, a new DOI, or journal submission. The verifier "
        "requires no site packages or access to the original workspace.\n\n"
        "Large matrices and cell-level predictions are not included. Recomputing "
        "the analysis requires the public data and scientific environment described "
        "in reproducibility/. The old DOI is an initial snapshot, not this package.\n"
    ).encode()
    payloads["MANIFEST_SHA256.csv"] = manifest_bytes(payloads)
    output.mkdir(parents=True,exist_ok=True)
    for name,payload in payloads.items():
        target = output/safe_name(name)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(payload)
    verification = verify_bundle(output)
    first, second = zip_bytes(payloads), zip_bytes(dict(reversed(list(payloads.items()))))
    if first != second:
        raise ValueError("Deterministic archive check failed")
    archive_path.write_bytes(first)
    audit = {**verification,"bundle":output.relative_to(ROOT).as_posix(),
             "zip_bytes":len(first),"zip_sha256":sha256(first),"deterministic_double_build":True,
             "historical_statistical_payloads_unchanged":163,"source_manifests_verified":True}
    (audit_dir/"correction_package_build.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--document-dir", type=Path, required=True)
    parser.add_argument("--figure-review", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    build(parser.parse_args())
