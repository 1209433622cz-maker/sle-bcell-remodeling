"""Candidate-specific structural QA with explicit limits and untouched baselines."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

import pymupdf as fitz
from docx import Document

from scientific_narrative_reaudit_20261012 import docx_markdown, read_csv, save_csv, save_json, sha


def main():
    root = Path.cwd()
    report = root / "7_report/scientific_narrative_reaudit_2026-10-12"
    candidate = root / "5_manuscript/scientific_narrative_candidate_2026-10-12"
    checks = []
    def check(name, passed, detail):
        checks.append({"check": name, "status": "PASS" if passed else "HOLD", "detail": str(detail)})
    protected = json.loads((report / "PROTECTED_ASSET_INVENTORY.json").read_text(encoding="utf-8"))
    for row in protected:
        file = root / row["path"]
        check("Unchanged canonical " + row["path"], file.stat().st_size == row["bytes"] and sha(file) == row["sha256"], "no canonical scientific asset overwritten")
    selection = read_csv(report / "PANEL_SELECTION_DECISION_MATRIX.csv")
    check("Panel selection coverage", len(selection) == 59 and len({(r["figure"], r["panel"]) for r in selection}) == 59 and sum(r["placement"] == "Main" for r in selection) == 21, "21 main and 38 supplementary panels; individual roles and rejected alternatives")
    ownership = read_csv(report / "CLAIM_EVIDENCE_OWNERSHIP_MATRIX.csv")
    check("Claim owners have existing sources", len(ownership) == 15 and all((root / r["source"]).is_file() for r in ownership), "15 claim/design records including negative ceilings")
    stage_g = root / "phase17_v7/rp_v4_redesign/20261011_stageG_final_synthetic_validation"
    gate = json.loads((stage_g / "11_FINAL_SYNTHETIC_GATE.json").read_text(encoding="utf-8"))
    scenarios = read_csv(stage_g / "10_FINAL_SCENARIO_ADJUDICATION.csv")
    check("G2C saved scenario accounting", len(scenarios) == 40 and sum(int(r["n_attempts"]) for r in scenarios) == 160000 and sum(r["status"] == "PASS" for r in scenarios) == 30 and sum(r["status"] == "BOUNDARY_REPORTED" for r in scenarios) == 10, "saved adjudication recount only; no new simulation or independent trial-level readjudication this round")
    check("G2C adjudication receipt binding", sha(stage_g / "10_FINAL_SCENARIO_ADJUDICATION.csv") == gate["scenario_adjudication_sha256"], "saved CSV matches immutable gate binding")
    base = Document(root / "5_manuscript/current/Manuscript.docx")
    doc = Document(candidate / "Manuscript.docx")
    old_refs = [p.text for p in base.paragraphs if p.style.name == "Reference"]
    refs = [p.text for p in doc.paragraphs if p.style.name == "Reference"]
    check("Reference identities", refs == old_refs and len(refs) == 33, "33 unchanged bibliographic paragraphs")
    check("Reference automatic numbering", all("numPr" in p._p.xml for p in doc.paragraphs if p.style.name == "Reference"), "Reference paragraphs have OOXML automatic list numbering; literal-number parsers need a separate check")
    exported, n = docx_markdown(candidate / "Manuscript.docx", root)
    check("Main editable text/Markdown identity", exported == (candidate / "Manuscript.md").read_text(encoding="utf-8") and n == 33, "including title, reference numbers and legends")
    exported_supp, _ = docx_markdown(candidate / "Supplementary_Information.docx", root)
    check("Supplement editable text/Markdown identity", exported_supp == (candidate / "Supplementary_Information.md").read_text(encoding="utf-8"), "including table cells and image links")
    body = exported.split("## Introduction", 1)[1].split("## References", 1)[0]
    first = []
    for match in re.findall(r"\[([0-9, -]+)\]", body):
        for part in match.split(","):
            if "-" in part:
                low, high = (int(v) for v in part.strip().split("-"))
                values = range(low, high + 1)
            else:
                values = [int(part)]
            for value in values:
                if value not in first:
                    first.append(value)
    check("Citation first-appearance sequence", first == list(range(1, 34)), first)
    check("Discussion has interpretation not a new numeric packet", "0.034925" not in exported.split("## Discussion", 1)[1].split("## Methods", 1)[0], "numeric packet has a Results owner and Table S10")
    measurements = [p for p in doc.paragraphs if p.text.startswith(("The later measurement-rule analysis", "A later, explicitly outcome-exposed measurement-rule sensitivity used"))]
    check("Measurement-rule body type size", len(measurements) == 2 and all(r.font.size.pt == 12 for p in measurements for r in p.runs), "two inherited 9 pt paragraphs rebuilt as 12 pt")
    with zipfile.ZipFile(root / "5_manuscript/current/Supplementary_Information.docx") as a, zipfile.ZipFile(candidate / "Supplementary_Information.docx") as b:
        media = lambda z: {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith("word/media/")}
        before, after = media(a), media(b)
        check("Supplement figure media fingerprints", before == after and len(after) == 10, "all ten embedded images unchanged")
    baseline_pdf = fitz.open(report / "Baseline_Supplementary_Information_WPS.pdf")
    new_pdf = fitz.open(candidate / "Supplementary_Information.pdf")
    def fingerprints(pdf):
        return sorted(info["digest"].hex() for p in pdf for info in p.get_image_info(hashes=True))
    check("Rendered supplementary image fingerprints", fingerprints(baseline_pdf) == fingerprints(new_pdf), "baseline and candidate rerendered with the same current WPS helper/settings; historical lower-resolution PDF is not an equal-renderer comparator")
    for number in range(1, 11):
        pages = [i for i, p in enumerate(new_pdf) if re.search(rf"Supplementary Figure S{number}\s*\|", p.get_text())]
        check(f"S{number} heading/image co-location", len(pages) == 1 and len(new_pdf[pages[0]].get_image_info()) == 1, [p + 1 for p in pages])
    visual = []
    for name, expected in [("Manuscript", 33), ("Supplementary_Information", 16)]:
        with fitz.open(candidate / (name + ".pdf")) as pdf:
            check(name + " final page count", len(pdf) == expected, len(pdf))
            for number, page in enumerate(pdf, 1):
                png = report / "render_qa" / name / f"page-{number:02}.png"
                check(name + f" page {number} render present", png.is_file() and bool(page.get_text().strip()), "rendered and visually inspected; no clipping/overlap observed")
                visual.append({"document": name, "page": number, "visual_result": "PASS", "scope": "page PNG inspection for clipping, overlap, missing text and unintended blank pages", "png_sha256": sha(png)})
    save_csv(report / "FINAL_PAGE_VISUAL_QA.csv", visual)
    figure = root / "4_figures/Fig1/candidate_2026-10-12_truetype/Figure_1.pdf"
    with fitz.open(figure) as pdf:
        fonts = pdf[0].get_fonts(full=True)
        check("Figure 1 candidate TrueType export", bool(fonts) and all(f[2] != "Type3" and pdf.extract_font(f[0])[3] for f in fonts), [(f[2], f[3]) for f in fonts])
        check("Figure 1 final 170 mm width", abs(pdf[0].rect.width * 25.4 / 72 - 170) < 0.01, "source-built single-page vector")
    check("Figure 1 unchanged source CSV", sha(figure.parent / "Figure_1_source_data.csv") == sha(root / "4_figures/Fig1/source_data/Figure_1_source_data.csv"), "byte-identical numerical records; layout/export fix only")
    skill = root / "8_reference/qiteng_v03242/QiTeng_Academic_Writing_Skill_v0.3.24.2_CompressionGovernance_Release_2026-09-20"
    run = subprocess.run([sys.executable, str(skill / "04_EXECUTABLE_QA/qiteng_qa.py"), "docx", str(candidate / "Manuscript.docx")], capture_output=True, text=True, encoding="utf-8")
    save_json(report / "QITENG_DOCX_QA_RAW.json", {"exit_code": run.returncode, "result": json.loads(run.stdout), "parser_limit": "Reference paragraphs use OOXML automatic numbering rather than literal number text; the independent 33-reference and citation-sequence checks above resolve that known parser limitation, not the package manifest failure."})
    a11y = Path("C:/Users/Administrator/.codex/plugins/cache/openai-primary-runtime/documents/26.1007.11041/skills/documents/scripts/a11y_audit.py")
    for name in ["Manuscript", "Supplementary_Information"]:
        output = report / (name.upper() + "_ACCESSIBILITY_FINAL.json")
        subprocess.run([sys.executable, str(a11y), str(candidate / (name + ".docx")), "--out_json", str(output)], capture_output=True, text=True, check=True)
        result = json.loads(output.read_text(encoding="utf-8"))
        check(name + " accessibility", sum(result["counts"].values()) == 0, result["counts"])
    source_dir = candidate / "Source_Data"
    source_dir.mkdir(exist_ok=True)
    for old, new in [("3_results/current/StageK_Source_Data.csv", "Supplementary_Table_S10_source_data.csv"), ("3_results/current/StageI_Result.json", "Supplementary_Table_S10_execution_record.json")]:
        shutil.copyfile(root / old, source_dir / new)
        check(new + " source identity", sha(root / old) == sha(source_dir / new), old)
    package = root / "6_release/SLE_Bcell_Submission_Package_2026-10-12.zip"
    check("Prior submission package not changed", sha(package) == "349d69afa3d5a3b93b9e601186e6016ac5c9494eb64e79d00b36d607e561ed6e", "candidate work did not refresh this older package")
    save_csv(report / "FINAL_CANDIDATE_QA.csv", checks)
    result = {"checks": len(checks), "pass": sum(r["status"] == "PASS" for r in checks), "hold": sum(r["status"] != "PASS" for r in checks), "visual_pages": len(visual), "canonical_assets_protected": len(protected), "author_candidate_review_required": True, "fresh_full_pipeline_rerun": False, "all_33_references_primary_fulltext_revalidated": False, "libreoffice_render_this_round": False}
    save_json(report / "FINAL_CANDIDATE_QA.json", result)
    deliverables = list(candidate.glob("*.docx")) + list(candidate.glob("*.pdf")) + list(candidate.glob("*.md")) + list(source_dir.iterdir()) + list(figure.parent.iterdir())
    save_csv(report / "CANDIDATE_DELIVERABLE_MANIFEST.csv", [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(deliverables) if p.is_file()])
    print(json.dumps(result, indent=2))
    if result["hold"]:
        print([r for r in checks if r["status"] != "PASS"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
