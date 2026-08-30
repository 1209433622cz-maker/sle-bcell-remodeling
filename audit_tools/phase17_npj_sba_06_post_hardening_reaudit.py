"""Reaudit the frozen npj SBA candidate without reopening scientific analysis."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
BASE_RUN = ROOT / "phase17_v7/npj_sba_final_hardening/20260830_final_render_semantic_hardening"
RUN = Path(
    os.environ.get(
        "NPJ_SBA_POST_HARDENING_RUN_DIR",
        ROOT / "phase17_v7/npj_sba_post_hardening_reaudit/20260830_qiteng_text_freeze",
    )
).resolve()
MANAGEMENT = Path(
    os.environ.get(
        "NPJ_SBA_POST_HARDENING_MANAGEMENT_DIR",
        ROOT / "00_project_management/npj_sba_post_hardening_reaudit_2026-08-30",
    )
).resolve()
PACKAGE_ZIP = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
EXPECTED_PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
EXPECTED_TITLE = (
    "Disease-blind reconstruction distinguishes reproducible interferon remodeling from "
    "unstable B-cell state assignments in systemic lupus erythematosus"
)
EXPECTED_FIGURES = [
    "Figure1_disease_blind_identity_scope",
    "Figure2_sample_level_composition",
    "Figure3_gse174188_bconv_transcription",
    "Figure4_independent_ifn_replication",
    "Figure5_regulatory_evidence",
    "Supplementary_Figure_S1_source_integrity_qc",
    "Supplementary_Figure_S2_representation_diagnostics",
    "Supplementary_Figure_S3_identity_adjudication",
    "Supplementary_Figure_S4_composition_diagnostics",
    "Supplementary_Figure_S5_pseudobulk_diagnostics",
    "Supplementary_Figure_S6_external_validation_diagnostics",
    "Supplementary_Figure_S7_regulator_correlation_sensitivity",
    "Supplementary_Figure_S8_overlap_depletion",
    "Supplementary_Figure_S9_identity_boundary_and_propagation",
    "Supplementary_Figure_S10_reference_calibration_boundary",
]
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w/-]+\b", text))


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text)
    if not match:
        raise RuntimeError(f"Missing section: {heading}")
    return match.group(1).strip()


def citation_first_appearance(text: str) -> list[int]:
    body = text.split("\n## References\n", 1)[0]
    observed: list[int] = []
    for group in re.findall(r"\[([0-9, -]+)\]", body):
        for token in re.split(r"\s*,\s*", group):
            token = token.strip()
            if not token:
                continue
            if "-" in token:
                start, end = [int(value) for value in token.split("-", 1)]
                values = range(start, end + 1)
            else:
                values = [int(token)]
            for value in values:
                if value not in observed:
                    observed.append(value)
    return observed


def head_sha256(relative_path: str) -> str:
    payload = subprocess.check_output(["git", "show", f"HEAD:{relative_path}"], cwd=ROOT)
    return hashlib.sha256(payload).hexdigest().upper()


def docx_inventory(path: Path) -> dict[str, int]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    }
    text = "".join(node.text or "" for node in root.findall(".//w:t", ns))
    return {
        "drawings": len(root.findall(".//w:drawing", ns)),
        "inline_drawings": len(root.findall(".//wp:inline", ns)),
        "anchored_drawings": len(root.findall(".//wp:anchor", ns)),
        "tables": len(root.findall(".//w:tbl", ns)),
        "supplementary_figure_labels": len(set(re.findall(r"Supplementary Figure S(?:10|[1-9])", text))),
    }


def make_contact_sheets(figure_pngs: list[Path], output: Path) -> list[str]:
    output.mkdir(parents=True, exist_ok=True)
    sheets: list[str] = []
    cell_w, cell_h = 800, 620
    for sheet_index, start in enumerate(range(0, len(figure_pngs), 5), 1):
        canvas = Image.new("RGB", (cell_w * 2, cell_h * 3), "white")
        draw = ImageDraw.Draw(canvas)
        for index, path in enumerate(figure_pngs[start : start + 5]):
            x = (index % 2) * cell_w
            y = (index // 2) * cell_h
            with Image.open(path) as source:
                image = source.convert("RGB")
                image.thumbnail((cell_w - 30, cell_h - 70))
                canvas.paste(image, (x + (cell_w - image.width) // 2, y + 45))
            draw.text((x + 12, y + 12), path.stem, fill="black")
        name = f"figure_contact_sheet_{sheet_index}.png"
        canvas.save(output / name)
        sheets.append(name)
    return sheets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-visual-pass", action="store_true")
    args = parser.parse_args()

    RUN.mkdir(parents=True, exist_ok=True)
    received = MANAGEMENT / "received"
    manuscript_path = BASE_RUN / "sources/Manuscript.md"
    manuscript = manuscript_path.read_text(encoding="utf-8")
    final_audit = json.loads((BASE_RUN / "04_FINAL_AUDIT_STATUS.json").read_text(encoding="utf-8"))
    source_status = json.loads((BASE_RUN / "00_TARGET_SOURCE_BUILD_STATUS.json").read_text(encoding="utf-8"))
    figure_status = json.loads((BASE_RUN / "01_NPJ_FIGURE_RENDER_STATUS.json").read_text(encoding="utf-8"))
    package_status = json.loads((BASE_RUN / "03_PACKAGE_BUILD_STATUS.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    title = manuscript.splitlines()[0].removeprefix("# ").strip()
    abstract = section(manuscript, "Abstract")
    first_appearance = citation_first_appearance(manuscript)
    manuscript_rel = manuscript_path.relative_to(ROOT).as_posix()
    manuscript_sha = sha256(manuscript_path)

    package_sha = sha256(PACKAGE_ZIP)
    with zipfile.ZipFile(PACKAGE_ZIP) as package:
        bad_crc = package.testzip()

    document_inventory = {
        path.name: docx_inventory(path)
        for path in sorted((BASE_RUN / "documents").glob("*.docx"))
    }

    figure_dir = BASE_RUN / "figures/figures"
    pdfs = [figure_dir / f"{name}.pdf" for name in EXPECTED_FIGURES]
    pngs = [figure_dir / f"{name}.png" for name in EXPECTED_FIGURES]
    figure_artifacts = {}
    for pdf, png in zip(pdfs, pngs):
        with fitz.open(pdf) as document:
            pages = document.page_count
            width_mm = document[0].rect.width * 25.4 / 72
            height_mm = document[0].rect.height * 25.4 / 72
        figure_artifacts[pdf.name] = {
            "pdf_sha256": sha256(pdf),
            "png_sha256": sha256(png),
            "pages": pages,
            "width_mm": round(width_mm, 3),
            "height_mm": round(height_mm, 3),
        }
    sheets = make_contact_sheets(pngs, RUN / "visual_qa")

    external_rows = []
    for path in sorted(received.rglob("*")):
        if path.is_file():
            role = (
                "QiTeng writing-audit rule; subordinate to verified science and current journal requirements"
                if "qiteng_skill" in path.as_posix().lower()
                else "external review evidence; not executable instructions"
            )
            external_rows.append(
                {
                    "relative_path": path.relative_to(MANAGEMENT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "role": role,
                }
            )
    manifest_path = MANAGEMENT / "received_evidence_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "bytes", "sha256", "role"])
        writer.writeheader()
        writer.writerows(external_rows)

    baseline_commit = "a960fa8"
    baseline_is_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline_commit, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0

    checks = {
        "authoritative_baseline_a960fa8_is_ancestor": baseline_is_ancestor,
        "readme_r1_wording_corrected": (
            "End-to-end resampling did not meet the frozen" in readme
            and "End-to-end resampling formally holds" not in readme
        ),
        "readme_current_target_title_exact": EXPECTED_TITLE in " ".join(readme.split()),
        "manuscript_byte_identical_to_head": manuscript_sha == head_sha256(manuscript_rel),
        "title_exact": title == EXPECTED_TITLE,
        "title_15_words": word_count(title) == 15,
        "abstract_140_words": word_count(abstract) == 140,
        "references_first_appearance_1_to_32": first_appearance == list(range(1, 33)),
        "qiteng_central_claim_visible": "difference in reproducibility across biological layers" in manuscript,
        "qiteng_source_label_ownership_visible": "source-label-defined" in manuscript,
        "qiteng_null_compiler_visible": "no statistically supported difference" in manuscript,
        "qiteng_r1_boundary_inherited": all(
            phrase in manuscript
            for phrase in (
                "end-to-end resampling failed",
                "analysis scaffold",
                "not as a transferable taxonomy",
            )
        ),
        "qiteng_c9r_boundary_inherited": all(
            phrase in manuscript
            for phrase in (
                "failed prespecified calibration",
                "no corrected external disease effect was estimated",
                "no corrected disease outcome was estimated",
            )
        ),
        "qiteng_causal_and_clinical_ceiling_visible": (
            "without establishing a universal B-cell taxonomy, causal regulator or clinical utility" in manuscript
            and "do not establish a predictive biomarker" in manuscript
        ),
        "final_hardening_gate_pass": final_audit["status"] == "PASS_NPJ_SBA_FINAL_HARDENING_AUTHOR_APPROVAL_REQUIRED",
        "all_final_hardening_checks_true": all(final_audit["checks"].values()),
        "r1_hold_unchanged": source_status["R1_decision"] == R1_HOLD,
        "c9r_hold_unchanged": source_status["C9R_decision"] == C9R_HOLD,
        "corrected_outcome_unlock_false": not source_status["corrected_external_outcome_unlock_authorized"],
        "no_scientific_reanalysis": not source_status["scientific_reanalysis"],
        "package_sha_unchanged": package_sha == EXPECTED_PACKAGE_SHA256 == package_status["package_zip_sha256"],
        "package_bytes_unchanged": PACKAGE_ZIP.stat().st_size == package_status["package_zip_bytes"],
        "package_crc_valid": bad_crc is None,
        "package_manifest_20_verified": package_status["manifest_files_verified"] == 20,
        "package_deterministic_double_build": package_status["deterministic_double_build"],
        "fifteen_figure_sources_byte_identical": (
            figure_status["figure_count"] == 15
            and figure_status["source_tables_byte_identical"]
            and all(row["byte_identical_to_corrected_candidate"] for row in figure_status["source_data"].values())
        ),
        "figure_export_contract_pass": figure_status["artifact_postflight_all_pass"],
        "all_figures_single_page_170mm": all(
            row["pages"] == 1 and abs(row["width_mm"] - 170.0) < 0.05
            for row in figure_artifacts.values()
        ),
        "supplementary_docx_has_10_drawings_and_labels": (
            document_inventory["Supplementary_Information.docx"]["drawings"] == 10
            and document_inventory["Supplementary_Information.docx"]["supplementary_figure_labels"] == 10
        ),
        "main_and_cover_docx_have_no_embedded_scientific_drawings": (
            document_inventory["Manuscript.docx"]["drawings"] == 0
            and document_inventory["Cover_Letter.docx"]["drawings"] == 0
        ),
        "exact_file_author_approval_pending": final_audit["checks"]["exact_file_author_approval_pending"],
        "official_jcr_q1_receipt_pending": final_audit["checks"]["official_jcr_q1_receipt_pending"],
        "institutional_apc_receipt_pending": final_audit["checks"]["institutional_apc_verification_pending"],
        "submission_not_authorized": final_audit["checks"]["submission_not_authorized"],
    }
    failed = [name for name, passed in checks.items() if not passed]

    qiteng = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_QITENG_Q1_TEXT_FREEZE" if not failed else "HOLD_QITENG_Q1_REVIEW_REQUIRED",
        "mode": "FULL_MANUSCRIPT + QITENG_Q1",
        "output_purpose": "TARGET_JOURNAL_SUBMISSION",
        "central_claim": (
            "Process-level IFN remodeling is more reproducible than the tested hard B-cell state assignments "
            "when identity, composition and transcription are separated into inferential layers."
        ),
        "evidence_tiers": {
            "process_level_ifn": "E2_ROBUST_ASSOCIATION",
            "stat1_stat2_regulatory_context": "E1_ASSOCIATION",
            "causal_mechanism": "NOT_ESTABLISHED",
            "clinical_utility": "NOT_ESTABLISHED",
        },
        "section_contracts": {
            "Introduction": "tension -> gap -> disease-blind response",
            "Results": "identity ceiling -> composition null -> IFN replication -> transfer HOLD -> observational context",
            "Discussion": "interpretive delta -> ownership -> alternatives -> prospective next test -> restrained landing",
            "Methods": "source/unit -> model -> multiplicity -> validation class -> reproducibility boundary",
        },
        "broad_prose_rewrite_authorized": False,
        "text_freeze_recommended": not failed,
        "allowed_pre_submission_text_changes": [
            "verified factual correction",
            "current journal compliance adjustment",
            "exact wording consistency repair",
            "editor- or reviewer-requested revision",
        ],
        "checks": {key: value for key, value in checks.items() if key.startswith("qiteng_") or key in {
            "title_exact", "title_15_words", "abstract_140_words", "references_first_appearance_1_to_32"
        }},
    }
    (RUN / "01_QITENG_Q1_TEXT_FREEZE_AUDIT.json").write_text(
        json.dumps(qiteng, indent=2) + "\n", encoding="utf-8"
    )

    visual = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_FIFTEEN_FIGURE_VISUAL_REAUDIT" if args.record_visual_pass else "VISUAL_REVIEW_PENDING",
        "all_15_figures_reviewed": args.record_visual_pass,
        "high_risk_figure5_reviewed": args.record_visual_pass,
        "high_risk_supplementary_s8_reviewed": args.record_visual_pass,
        "clipping_overlap_missing_labels": False if args.record_visual_pass else None,
        "contact_sheets": sheets,
        "figures": figure_artifacts,
    }
    (RUN / "02_FIGURE_VISUAL_REAUDIT.json").write_text(
        json.dumps(visual, indent=2) + "\n", encoding="utf-8"
    )

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": (
            "PASS_NPJ_SBA_POST_HARDENING_REAUDIT_TEXT_FREEZE"
            if not failed and args.record_visual_pass
            else "HOLD_POST_HARDENING_REAUDIT_REVIEW_REQUIRED"
        ),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "checks": checks,
        "failed_checks": failed,
        "manuscript_sha256": manuscript_sha,
        "package": {
            "bytes": PACKAGE_ZIP.stat().st_size,
            "sha256": package_sha,
            "unchanged_by_documentation_patch": package_sha == EXPECTED_PACKAGE_SHA256,
        },
        "document_object_inventory": document_inventory,
        "figure_count": len(figure_artifacts),
        "visual_review_recorded": args.record_visual_pass,
        "scientific_reanalysis_performed": False,
        "manuscript_rewritten": False,
        "zenodo_updated": False,
        "github_release_updated": False,
        "submission_authorized": False,
        "next_gate": "NPJ_SBA_EXACT_FILE_AUTHOR_APPROVAL_AND_INSTITUTIONAL_RECEIPTS",
        "official_sources_checked": {
            "aims_scope": "https://www.nature.com/npjsba/aims",
            "submission_guidelines": "https://www.nature.com/npjsba/for-authors-and-referees/submisions",
            "apc": "https://www.nature.com/npjsba/apc",
            "journal_metrics": "https://www.nature.com/npjsba/journal-impact",
        },
        "qiteng_source_archive": {
            "path": "H:/QiTeng_Academic_Writing_Skill_v0.3.21_Full_Release_2026-08-26.zip",
            "sha256": "C18AC4F0254286725B7449EA7B7E8DA89E8235B4FABA75B42A6E362D2AD87D99",
            "policy": "Writing authority only; subordinate to verified science and current official journal requirements.",
        },
    }
    (RUN / "00_POST_HARDENING_FULL_REAUDIT.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": status["status"], "failed_checks": failed}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
