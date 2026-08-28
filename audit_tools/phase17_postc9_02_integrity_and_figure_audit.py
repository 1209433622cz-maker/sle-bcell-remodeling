"""Read-only project content audit plus explicit figure and corrected-freeze checks."""

import argparse
import ast
import csv
from datetime import datetime
import gzip
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
from importlib.metadata import version

import fitz
import pandas as pd
from PIL import Image, ImageDraw


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest().upper()


def write_csv(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check_csv(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t" if ".tsv" in path.name else ",")
        first = next(reader, [])
        count = 0
        for row in reader:
            if row and len(row) != len(first):
                raise ValueError(f"Ragged CSV row {count + 2}: {len(row)} vs {len(first)}")
            count += 1
    return f"parsed {count} data rows; {len(first)} columns"


def inspect(path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        json.loads(path.read_text(encoding="utf-8-sig"))
        return "JSON parsed"
    if suffix in {".csv", ".tsv"} or path.name.endswith((".csv.gz", ".tsv.gz")):
        return check_csv(path)
    if suffix == ".py":
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        return "Python AST parsed; not executed"
    if suffix in {".md", ".txt", ".ps1", ".r", ".yaml", ".yml", ".cff"}:
        path.read_text(encoding="utf-8-sig")
        return "UTF-8 decoded; semantic review separate"
    if suffix == ".pdf":
        with fitz.open(path) as document:
            for page in document:
                page.get_text()
            return f"PDF parsed; {len(document)} pages"
    if suffix in {".png", ".jpg", ".jpeg"}:
        with Image.open(path) as image:
            image.verify()
        return "Image decoded and verified"
    if suffix in {".zip", ".docx", ".xlsx"}:
        with zipfile.ZipFile(path) as archive:
            failure = archive.testzip()
            if failure:
                raise ValueError(f"ZIP CRC failed: {failure}")
            if suffix in {".docx", ".xlsx"}:
                for member in archive.namelist():
                    if member.endswith(".xml"):
                        ET.fromstring(archive.read(member))
        return "ZIP CRC / Office XML verified"
    if suffix == ".svg":
        ET.parse(path)
        return "SVG XML parsed"
    return "SHA-256 and size only; no semantic-content assertion"


def verify_manifest(directory, filename, key):
    records = []
    with (directory / filename).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            path = (directory / row[key]).resolve()
            if not path.is_relative_to(directory.resolve()):
                raise ValueError(f"Out-of-scope manifest path {path}")
            expected_size = row.get("size_bytes", row.get("bytes", ""))
            passed = path.is_file() and sha256(path) == row["sha256"]
            passed = passed and (not expected_size or path.stat().st_size == int(expected_size))
            records.append({"manifest":filename,"path":row[key],"pass":passed})
    return records


def figure_audit(review, output):
    rows, violations, renders = [], [], []
    render_dir = output / "figure_renders"
    render_dir.mkdir(exist_ok=True)
    for path in sorted((review / "figures").glob("*.pdf")):
        with fitz.open(path) as doc:
            page = doc[0]
            spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                     for line in b["lines"] for s in line["spans"] if s["text"].strip()]
            for span in spans:
                text = span["text"].strip()
                panel = bool(re.fullmatch("[a-z]", text) and "Bold" in span["font"])
                size = span["size"]
                if not ((7.95 <= size <= 8.05) if panel else (4.95 <= size <= 7.05)):
                    violations.append({"figure":path.name,"issue":"font_size","text":text,"size":size})
                rect = fitz.Rect(span["bbox"])
                if rect.x0 < -0.5 or rect.y0 < -0.5 or rect.x1 > page.rect.width+.5 or rect.y1 > page.rect.height+.5:
                    violations.append({"figure":path.name,"issue":"out_of_canvas","text":text,"bbox":list(rect)})
            rows.append({"figure":path.name,"width_mm":page.rect.width*25.4/72,
                         "height_mm":page.rect.height*25.4/72,"text_spans":len(spans),
                         "min_pt":min(s["size"] for s in spans),"max_pt":max(s["size"] for s in spans),
                         "fonts":";".join(sorted(set(s["font"] for s in spans)))})
            target = render_dir / (path.stem + ".png")
            page.get_pixmap(dpi=150, alpha=False).save(target)
            renders.append(target)
    for begin in range(0, len(renders), 6):
        sheet = Image.new("RGB", (1600, 1350), "white")
        draw = ImageDraw.Draw(sheet)
        for i, path in enumerate(renders[begin:begin+6]):
            x, y = (i % 2)*800, (i // 2)*450
            with Image.open(path) as picture:
                picture.thumbnail((780, 410))
                sheet.paste(picture, (x+(800-picture.width)//2, y+30))
            draw.text((x+10, y+8), path.stem, fill="black")
        sheet.save(output / f"contact_{begin//6+1}.png")
    write_csv(output / "figure_typography.csv", rows)
    write_csv(output / "figure_violations.csv", violations)
    return {"figures":len(rows),"widths_170mm":all(abs(r["width_mm"]-170)<.01 for r in rows),
            "font_or_canvas_violations":violations}


def document_checks(review, output):
    render = json.loads((output / "document_pages/document_render_audit.json").read_text())
    expected = {f"{name}.{ext}" for name in ("Manuscript", "Supplementary_Information", "Research_Proposal")
                for ext in ("docx", "pdf")}
    records = render.get("document_hashes", [])
    hash_matches = len(records) == 6 and {row["file"] for row in records} == expected
    for row in records:
        if row["file"] not in expected:
            hash_matches = False
            continue
        path = review / "documents" / row["file"]
        hash_matches = hash_matches and path.is_file() and sha256(path) == row["sha256"]
    rows = render["page_checks"]
    supplement = [row for row in rows if row["document"] == "Supplementary_Information.pdf"]
    return {"pages":render["pages"],"document_hashes_match_rendered_files":hash_matches,
            "page_counts":{name:sum(row["document"] == name for row in rows)
                           for name in sorted({row["document"] for row in rows})},
            "all_pages_within_canvas":render["all_pages_within_canvas"],
            "all_markers_resolved":render["all_markers_resolved"],
            "ten_supplementary_inline_figures":bool(supplement) and all(row["document_inline_figures"] == 10 for row in supplement)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root",type=Path,default=Path.cwd())
    parser.add_argument("--review-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args = parser.parse_args()
    root, review, output = args.project_root.resolve(), args.review_dir.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=True)
    originals = [
        root / "phase17_v7/gateC8BRF/20260825_author_release/source_data",
        root / "phase17_v7/gateC8S/20260821_supplementary_traceability_freeze/supplementary_source_data",
        root / "phase17_v7/round6_q1_robustness/20260825_overlap_depletion/source_data",
        root / "phase17_v7/round6_q1_robustness/20260827_r1_hold_integration/source_data",
    ]
    source_checks = []
    for new_path in (review / "source_data").glob("*.csv"):
        for original in originals:
            old_path = original / new_path.name
            if not old_path.exists():
                continue
            new_table, old_table = pd.read_csv(new_path), pd.read_csv(old_path)
            pd.testing.assert_frame_equal(new_table, old_table, check_dtype=False,
                                          check_exact=False, rtol=1e-12, atol=1e-12)
            source_checks.append({"file":new_path.name,"rows":len(new_table),"pass":True})
    write_csv(output / "figure_source_equivalence.csv", source_checks)
    review_manifest = [{"filename":p.relative_to(review).as_posix(),"size_bytes":p.stat().st_size,"sha256":sha256(p)}
                       for folder in ("figures","source_data") for p in sorted((review/folder).iterdir()) if p.is_file()]
    write_csv(review / "02_REVIEW_FIGURE_MANIFEST.csv", review_manifest)
    inventory, issues = [], []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"} and (Path(current)/d).resolve() != output]
        for filename in sorted(files):
            path = Path(current) / filename
            record = {"path":path.relative_to(root).as_posix(),"size_bytes":path.stat().st_size,"sha256":sha256(path)}
            try:
                record["content_check"] = inspect(path)
                record["status"] = "PASS_WITH_SCOPE_AS_STATED"
            except Exception as error:
                record["content_check"] = f"{type(error).__name__}: {error}"
                record["status"] = "REVIEW"
                issues.append(record.copy())
            inventory.append(record)
            if len(inventory) % 250 == 0:
                print(f"Audited {len(inventory)} files",flush=True)
    write_csv(output / "all_file_inventory.csv", inventory)
    write_csv(output / "content_issues.csv", issues)
    old = root / "phase17_v7/gateC9/20260828_gse135779_label_agnostic_validation"
    new = root / "phase17_v7/gateC9R/20260828_normalization_correction"
    manifests = verify_manifest(old,"29_FILE_INTEGRITY_MANIFEST.csv","filename")
    manifests += verify_manifest(new,"17_FILE_INTEGRITY_MANIFEST.csv","filename")
    manifests += verify_manifest(root / "04_submission/journal_submission","MANIFEST_SHA256.csv","relative_path")
    write_csv(output / "manifest_verification.csv",manifests)
    status = json.loads((new / "15_GATE_C9A_PREFREEZE_DECISION.json").read_text())
    outcome_files = [p.name for p in new.iterdir() if re.match(r"^(1[89]|2[0-9])_",p.name)]
    summary = {"created_at":datetime.now().astimezone().isoformat(timespec="seconds"),
               "files":len(inventory),"bytes":sum(r["size_bytes"] for r in inventory),"content_issues":len(issues),
               "manifest_checks":len(manifests),"manifest_all_pass":all(r["pass"] for r in manifests),
               "corrected_decision":status["decision"],"corrected_outcome_unlock":status["outcome_unlock_authorized"],
               "corrected_outcome_files":outcome_files,"figure_audit":figure_audit(review,output),
               "document_audit":document_checks(review,output),
               "unchanged_scientific_figure_source_tables":len(source_checks),
               "scope":"All workspace files except .git, __pycache__, and this audit output. SHA-256 for all; content checks by format; no claim of rerunning all historical models or validating every biological entry."}
    (output / "audit_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    known_template = "Data/processed/GSE135779_nehar_validation/source/libaries.csv"
    known_hash = "3A854C6D571616FE04299AE3C5052988C076E7F390608D0F5D2C18ABD17D7125"
    docs, figures = summary["document_audit"], summary["figure_audit"]
    checks = {
        "frozen_manifests":summary["manifest_all_pass"] and len(manifests) == 229,
        "historical_source_tables_unchanged":len(source_checks) == 14,
        "fifteen_figures_within_style_contract":figures["figures"] == 15 and figures["widths_170mm"] and not figures["font_or_canvas_violations"],
        "rendered_document_hashes":docs["document_hashes_match_rendered_files"],
        "document_structure":docs["all_pages_within_canvas"] and docs["all_markers_resolved"] and docs["ten_supplementary_inline_figures"],
        "corrected_calibration_hold_obeyed":status["decision"] == "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED" and not status["outcome_unlock_authorized"] and not outcome_files,
        "no_unclassified_content_issues":all(row["path"] == known_template and row["sha256"] == known_hash for row in issues),
    }
    qa = {"created_at":summary["created_at"],"checks":checks,"all_automated_checks_pass":all(checks.values()),
          "release_authorized":False,"scientific_status":status["decision"],
          "visual_review_record":"00_project_management/action_record_2026-08-28_post_gateC9_advisor_correction_audit.md",
          "interpretation":"Automated technical checks are not publication approval or independent biological validation.",
          "runtime":{"python":platform.python_version(),"packages":{name:version(name) for name in ("pandas","PyMuPDF","Pillow")}}}
    (output / "final_review_qa.json").write_text(json.dumps(qa,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2),flush=True)
    if not all(checks.values()):
        raise SystemExit("Final technical checks require review; release remains HOLD")


if __name__=="__main__":
    main()
