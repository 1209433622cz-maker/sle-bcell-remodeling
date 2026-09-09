"""Check source integrity and both rendered S7 layouts against the frozen parent."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
import fitz
from PIL import Image, ImageDraw
from zipfile import ZipFile
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'phase17_v7/npj_sba_s7_readability/20260909_source_rebuild'
PARENT = ROOT/'phase17_v7/npj_sba_scientific_presentation_maintenance_freeze/20260908_final_cross_document'
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def xml(path):
    with ZipFile(path) as z:
        return ET.fromstring(z.read('word/document.xml'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--visual-confirmed', action='store_true')
    args = parser.parse_args()
    stem = 'Supplementary_Information_S7_readability'
    oldstem = 'Supplementary_Information_Scientific_Presentation_Freeze'
    current = xml(RUN / 'documents' / (stem + '.docx'))
    old = xml(PARENT / 'documents' / (oldstem + '.docx'))
    s7 = next(t for t in current.findall('.//w:tbl',NS) if t.find('.//w:t',NS).text == 'Result family')
    terms = set(re.findall(r'[A-Za-z]{7,}', ' '.join(t.text or '' for t in s7.findall('.//w:t',NS))))
    checks = {'all_document_text_identical': [t.text for t in current.findall('.//w:t',NS)] == [t.text for t in old.findall('.//w:t',NS)],
              'all_run_font_sizes_identical': [ET.tostring(t) for t in current.findall('.//w:sz',NS)] == [ET.tostring(t) for t in old.findall('.//w:sz',NS)]}
    page_rows = []
    for engine, before, after in [('wps', PARENT/'documents', RUN/'documents'),
                                  ('lo', PARENT/'qa/final_libreoffice_documents', RUN/'lo_final')]:
        a, b = fitz.open(before/(oldstem+'.pdf')), fitz.open(after/(stem+'.pdf'))
        checks[engine+'_15_pages'] = len(a) == len(b) == 15
        changes = []
        for i, (left, right) in enumerate(zip(a, b)):
            identical = left.get_pixmap().samples == right.get_pixmap().samples
            page_rows.append({'engine': engine, 'page': i+1, 'pixel_identical': identical})
            if not identical:
                changes.append(i+1)
        checks[engine+'_changes_only_pages4_to6'] = changes == [4,5,6]
        words = set(re.findall(r'[A-Za-z]+', b[3].get_text()))
        missing = sorted(terms - words)
        checks[engine+'_s7_long_words_unbroken'] = not missing
        print(engine, 'changed:', changes, 'missing full long words:', missing)
        for start in range(0, 15, 6):
            sheet = Image.new('RGB', (1500, 1500), 'white')
            draw = ImageDraw.Draw(sheet)
            for j in range(start, min(start+6, 15)):
                pix = b[j].get_pixmap(matrix=fitz.Matrix(1.5,1.5))
                im = Image.frombytes('RGB', (pix.width,pix.height), pix.samples)
                im.thumbnail((480,710))
                x,y = ((j-start)%3)*500, ((j-start)//3)*750
                sheet.paste(im, (x,y+20)); draw.text((x+5,y+3), f'{engine} page {j+1}', fill='black')
            sheet.save(RUN / f'{engine}_contact_{start//6+1}.png')
        for i in (3,4,5):
            b[i].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(RUN/f'{engine}_page{i+1}.png')
    with (RUN/'page_comparison.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=page_rows[0]);w.writeheader();w.writerows(page_rows)
    with (PARENT/'04_FROZEN_FIGURE_AND_SOURCE_DATA_MANIFEST.csv').open(encoding='utf-8-sig') as f:
        inventory=list(csv.DictReader(f))
    # Read the committed manifest to identify the exact inherited assets.
    print('Asset manifest columns:', list(inventory[0]))
    checks['45_assets_unchanged'] = len(inventory)==45 and all(
        sha(ROOT/row['relative_path']) == row['candidate_sha256'] for row in inventory)
    checks['main_source_unchanged'] = sha(ROOT/'01_manuscript/Manuscript.md') == sha(PARENT/'sources/Manuscript_scientific_presentation_freeze.md')
    checks['supplement_source_unchanged'] = sha(ROOT/'01_manuscript/Supplementary_Information.md') == sha(PARENT/'sources/Supplementary_Information_scientific_presentation_freeze.md')
    checks['accessibility_zero'] = json.loads((RUN/'a11y.json').read_text())['counts'] == {'high':0,'medium':0,'low':0}
    pagination=json.loads((RUN/'pagination.json').read_text())
    checks['pagination_fingerprints'] = pagination['status']=='PASS_SUPPLEMENT_PAGINATION_COHERENCE'
    checks['package_unchanged'] = sha(ROOT/'04_submission/npj_systems_biology_and_applications/SLE_Bcell_npj_Systems_Biology_and_Applications.zip') == '02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1'
    checks['visual_confirmed'] = args.visual_confirmed
    downloads=Path('C:/Users/Administrator/Downloads')
    inputs=['SLE_S7_Readability_Micro_Gate_Proof_2026-09-08.zip',
            'Supplementary_Information_Scientific_Presentation_Maintenance_v2.docx',
            'Supplementary_Information_Scientific_Presentation_Maintenance_v2.pdf',
            'action_record_2026-09-08_s7_actual_size_readability_micro_gate (1).md',
            'S7_proof_page4_actual_size.png']
    (RUN/'input_provenance.json').write_text(json.dumps([
        {'filename':n,'bytes':(downloads/n).stat().st_size,'sha256':sha(downloads/n)} for n in inputs],indent=2))
    result={'status':'PASS_S7_READABILITY_MICRO_GATE' if all(checks.values()) else 'REVIEW_REQUIRED',
            'checks':checks,'failed_checks':[k for k,v in checks.items() if not v],
            'document_sha256':sha(RUN/'documents'/(stem+'.docx')),
            'wps_pdf_sha256':sha(RUN/'documents'/(stem+'.pdf')),
            'lo_pdf_sha256':sha(RUN/'lo_final'/(stem+'.pdf'))}
    (RUN/'audit.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    if args.visual_confirmed and not all(checks.values()):
        raise RuntimeError(result['failed_checks'])

if __name__=='__main__':
    main()
