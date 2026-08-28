"""Bind rendered Figure 1 and the corrected legend to the exact candidate files."""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from pypdf import PdfReader

from verify_review_bundle import CANDIDATE_EDITS, sha256


def is_margin_line_number(text, x):
    return bool(re.fullmatch(r"\s*\d+\s*", text)) and 0 < x < 60


def pdf_text(path, exclude_line_numbers=False):
    fragments = []
    def collect(text, cm, tm, font, size):
        # WPS places manuscript line numbers at x=38.28, outside the 72-pt body margin.
        fragments.append("\n" if exclude_line_numbers and is_margin_line_number(text, tm[4]) else text)
    for page in PdfReader(path).pages:
        page.extract_text(visitor_text=collect)
        fragments.append("\n")
    return " ".join("".join(fragments).split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    review, audit = args.review_dir.resolve(), args.audit_dir.resolve()
    manuscript = root/"01_manuscript/Manuscript.md"
    source = manuscript.read_text(encoding="utf-8")
    pdf = review/"documents/Manuscript.pdf"
    docx = review/"documents/Manuscript.docx"
    figure = review/"figures/Figure1_disease_blind_identity_scope.pdf"
    text, figure_text = pdf_text(pdf, exclude_line_numbers=True), pdf_text(figure)
    with zipfile.ZipFile(docx) as archive:
        xml = ET.fromstring(archive.read("word/document.xml"))
    docx_text = " ".join(" ".join(xml.itertext()).split())
    caption = "minimum mapping-agreement criterion of 0.990"
    methods = source.split("## Methods\n", 1)[1].split("## Results\n", 1)[0]
    checks = {
        "source_corrected_caption":caption in source,
        "docx_corrected_caption":caption in docx_text,
        "pdf_corrected_caption":caption in text,
        "no_old_caption":all("minimum mapped-ARI criterion of 0.990" not in value for value in (source, docx_text, text)),
        "figure_corrected_label":"minimum agreement criterion" in figure_text,
        "figure_no_old_label":"minimum mapped-ARI criterion" not in figure_text,
        "source_label_claim_bounded":"arguing against dependence on any single contributing source label" in text,
        "ai_disclosure_already_in_methods":"### Generative AI assistance" in methods,
        "candidate_approval_not_invented":"Final approval of this corrected candidate is pending." in text,
    }
    numeric_counts = {}
    for name, changes in CANDIDATE_EDITS.items():
        prior = (audit/"prior_snapshot"/name).read_text(encoding="utf-8")
        current = source if name.endswith("Manuscript.md") else (root/"04_submission/Cover_Letter.md").read_text(encoding="utf-8")
        expected = prior
        for before, after in changes:
            expected = expected.replace(before, after)
        checks[name+"_exact_delta"] = current == expected
        old_numbers = re.findall(r"\d+(?:\.\d+)?", prior)
        checks[name+"_unchanged_numbers"] = old_numbers == re.findall(r"\d+(?:\.\d+)?", current)
        numeric_counts[name] = len(old_numbers)
    files = {
        "sources/Manuscript.md":manuscript, "sources/Cover_Letter.md":root/"04_submission/Cover_Letter.md",
        "figures/Figure_1.pdf":figure, "figures/Figure_1.png":figure.with_suffix(".png"),
        "main_text/Manuscript.docx":docx, "main_text/Manuscript.pdf":pdf}
    result = {"status":"PASS_CORRECTED_CANDIDATE_SEMANTICS" if all(checks.values()) else "FAIL",
              "checks":checks,"unchanged_numeric_token_counts":numeric_counts,
              "files":[{"path":name,"bytes":path.stat().st_size,"sha256":sha256(path.read_bytes())}
                       for name,path in files.items()], "submission_authorized":False}
    (audit/"candidate_semantic_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not all(checks.values()):
        raise SystemExit("Candidate semantic audit failed")


if __name__ == "__main__":
    main()
