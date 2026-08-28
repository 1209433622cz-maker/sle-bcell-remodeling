"""Build isolated journal-neutral review documents, without replacing the release."""

import argparse
import json
import hashlib
from pathlib import Path

from phase17_c8s_04_build_documents import markdown_to_docx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path)
    parser.add_argument("--include-cover", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    review = args.review_dir.resolve()
    output = review / "documents"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    jobs = [
        ("Manuscript", 12, True, True, "Research manuscript"),
        ("Supplementary_Information", 11, False, False, "Supplementary information"),
        ("Research_Proposal", 11, False, False, "Research proposal"),
    ]
    if args.include_cover:
        jobs.append(("Cover_Letter", 10.5, False, False, None))
    for name, body, double, line, header in jobs:
        source_folder = "04_submission" if name == "Cover_Letter" else "01_manuscript"
        results.append(markdown_to_docx(
            root / source_folder / f"{name}.md", output / f"{name}.docx",
            body_size=body, double_space=double, line_numbers=line, running_header=header,
            compact=name == "Cover_Letter",
            title_override=name.replace("_", " "),
            page_break_before_headings={
                "Supplementary Table S7 | Statistical tests and multiplicity families",
                "Supplementary Table S9 | Reference-calibrated external mapping boundary",
            },
            supplementary_figure_dirs=[args.figure_dir.resolve() if args.figure_dir else review / "figures"],
        ))
        results[-1]["source_sha256"] = hashlib.sha256((root/source_folder/f"{name}.md").read_bytes()).hexdigest().upper()
        results[-1]["docx_sha256"] = hashlib.sha256((output/f"{name}.docx").read_bytes()).hexdigest().upper()
    (review / "03_REVIEW_DOCUMENT_BUILD.json").write_text(
        json.dumps({"status":"REVIEW_DOCUMENTS_BUILT","next_step":"WPS export and final render audit; this build record alone is not release approval","documents":results},indent=2)+"\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
