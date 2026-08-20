# Gate C8R final submission audit

**Decision:** `PASS_GATE_C8R_SCIENTIFIC_FIGURE_REPRODUCIBILITY_REPAIR_AUTHOR_ACTION_REQUIRED`

**Scientific and technical package:** PASS

**Portal submission authorized:** NO

## Checks

| Check | Result | Detail |
|---|---:|---|
| `figure_build_freeze` | PASS | status=C8R_MAIN_FIGURES_BUILT_WITH_ASSERTIONS; figures=5 |
| `panel_data_assertions` | PASS | passed=43/43; Figure2a={'Figure2.panel_a.control_raw_points': 43, 'Figure2.panel_a.managed_sle_raw_points': 47, 'Figure2.panel_a.total_raw_points': 90} |
| `journal_target` | PASS | Genome Medicine primary; transfer routes frozen without quartile assertion |
| `author_identity` | PASS | missing=none |
| `structured_abstract` | PASS | computed_words=314; frozen_words=314; labels=4/4 |
| `keywords` | PASS | keywords=8; allowed=3-10 |
| `required_sections` | PASS | missing=none |
| `declaration_structure` | PASS | missing=none |
| `figure_legends` | PASS | count=5; details=[{'figure': 1, 'title_words': 7, 'legend_words': 85}, {'figure': 2, 'title_words': 9, 'legend_words': 83}, {'figure': 3, 'title_words': 8, 'legend_words': 109}, {'figure': 4, 'title_words': 8, 'legend_words': 89}, {'figure': 5, 'title_words': 6, 'legend_words': 109}] |
| `figure_files` | PASS | [{'figure': 1, 'png_bytes': 524199, 'pdf_bytes': 60738, 'pixels': (4254, 3270)}, {'figure': 2, 'png_bytes': 454608, 'pdf_bytes': 49848, 'pixels': (4254, 3360)}, {'figure': 3, 'png_bytes': 454067, 'pdf_bytes': 55055, 'pixels': (4254, 3450)}, {'figure': 4, 'png_bytes': 628446, 'pdf_bytes': 56820, 'pixels': (4254, 3450)}, {'figure': 5, 'png_bytes': 579776, 'pdf_bytes': 54763, 'pixels': (4254, 3720)}] |
| `correlation_aware_sensitivity` | PASS | targets=98/14/129/19/161/20; CAMERA Up=6/6, BH=5/6; FRY Up=6/6, BH=6/6; exception=discovery STAT2 CAMERA q=0.1355 |
| `reference_verification` | PASS | Crossref PASS=26/26; total manuscript references=30 |
| `frozen_numeric_anchors` | PASS | missing=none |
| `no_stale_claim_language` | PASS | hits=none |
| `noncausal_boundaries` | PASS | present=4/4 |
| `editable_documents` | PASS | {'Genome_Medicine_Manuscript_GateC8R_AUTHOR_COMPLETION_REQUIRED.docx': 58157, 'Additional_file_1_Supplementary_Information_GateC8R.docx': 44632, 'Genome_Medicine_Cover_Letter_GateC8R_AUTHOR_CONFIRMATION_REQUIRED.docx': 40061} |
| `document_build_status` | PASS | outputs=3; figure_assets=10 |
| `main_docx_ooxml` | PASS | line_numbers=True; page_field=True; even_odd=True; headers=2; double_spacing=True; title_border_absent=True |
| `supplement_table_geometry` | PASS | tables=6; explicit_geometry=6/6 |
| `docx_accessibility` | PASS | [{'file': 'main_text_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'supplement_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'cover_letter_a11y.json', 'high': 0, 'medium': 0, 'low': 0}] |
| `figure_source_data` | PASS | csv=5; checksums=5; zip_entries=6 |
| `regulator_sensitivity_attachment` | PASS | checksums=2; zip_entries=3 |
| `wps_render_outputs` | PASS | [{'document': 'main', 'pdf_bytes': 240343, 'pdf_pages': 26, 'png_pages': 26}, {'document': 'supplement', 'pdf_bytes': 127749, 'pdf_pages': 4, 'png_pages': 4}, {'document': 'cover', 'pdf_bytes': 83963, 'pdf_pages': 1, 'png_pages': 1}]; visual_review=PASS_ALL_31_PAGES |
| `hard_stops_visible` | PASS | manuscript placeholders=6; cover placeholders=2; unresolved hard stops=7 |

## Author-controlled hard stops

- institutional ethics determination
- competing interests
- funding
- final CRediT contributions and all-author approval
- acknowledgements
- all-author originality/submission confirmation
- open-source licence and immutable archive DOI

## Next stage

Gate C8B author declarations, institutional ethics determination, repository licence and immutable archive DOI; then final portal preflight and submission
