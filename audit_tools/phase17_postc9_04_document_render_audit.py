"""Render every WPS PDF page and record document structure and page bounds."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import fitz
from PIL import Image, ImageDraw


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--document-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    output=args.output_dir.resolve()
    output.mkdir(parents=True,exist_ok=True)
    poppler=shutil.which("pdftoppm")
    if not poppler:
        raise RuntimeError("Poppler pdftoppm is required")
    rows=[]
    hashes=[]
    for pdf in sorted(args.document_dir.glob("*.pdf")):
        pages=output/pdf.stem
        pages.mkdir(exist_ok=True)
        subprocess.run([poppler,"-r","110","-png",str(pdf.resolve()),str(pages/"page")],check=True)
        docx=pdf.with_suffix(".docx")
        for path in (pdf, docx):
            hashes.append({"file":path.name,"bytes":path.stat().st_size,"sha256":sha256(path)})
        with zipfile.ZipFile(docx) as archive:
            xml=ET.fromstring(archive.read("word/document.xml"))
            texts=" ".join(xml.itertext())
            image_count=len(xml.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline"))
            unresolved="[[SUPPLEMENTARY_FIGURE" in texts
        with fitz.open(pdf) as document:
            page_count=len(document)
            for number,page in enumerate(document,1):
                outside=[]
                for block in page.get_text("dict")["blocks"]:
                    for line in block.get("lines",[]):
                        for span in line["spans"]:
                            box=fitz.Rect(span["bbox"])
                            if box.x0<0 or box.y0<0 or box.x1>page.rect.width+.5 or box.y1>page.rect.height+.5:
                                outside.append(span["text"])
                rows.append({"document":pdf.name,"page":number,"text_characters":len(page.get_text()),
                             "outside_page_text":outside,"unresolved_markers":unresolved,
                             "document_inline_figures":image_count})
        images=[pages/f"page-{number:0{len(str(page_count))}d}.png" for number in range(1,page_count+1)]
        if not all(path.is_file() for path in images):
            raise RuntimeError(f"Incomplete page rendering for {pdf.name}")
        for start in range(0,len(images),6):
            sheet=Image.new("RGB",(1500,1500),"white")
            draw=ImageDraw.Draw(sheet)
            for index,path in enumerate(images[start:start+6]):
                x=(index%3)*500; y=(index//3)*750
                with Image.open(path) as picture:
                    picture.thumbnail((490,705))
                    sheet.paste(picture,(x+(500-picture.width)//2,y+25))
                draw.text((x+10,y+5),pdf.stem+" "+path.stem,fill="black")
            sheet.save(output/f"{pdf.stem}_contact_{start//6+1}.png")
    (output/"document_render_audit.json").write_text(json.dumps({
        "created_at":datetime.now().astimezone().isoformat(timespec="seconds"),
        "engine":"WPS PDF export followed by Poppler 110-dpi page rendering",
        "document_hashes":hashes,
        "pages":len(rows),"page_checks":rows,
        "all_pages_within_canvas":all(not row["outside_page_text"] for row in rows),
        "all_markers_resolved":all(not row["unresolved_markers"] for row in rows),
        "visual_review":"Page images require human/model visual inspection; structural checks alone are insufficient",
    },indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
