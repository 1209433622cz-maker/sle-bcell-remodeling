# Gate C8S final submission audit

**Decision:** `PASS_GATE_C8S_SUPPLEMENTARY_EVIDENCE_TRACEABILITY_FREEZE_AUTHOR_ACTION_REQUIRED`

**Scientific and technical package:** PASS

**Portal submission authorized:** NO - author-controlled hard stops remain.

## Checks

| Check | Result | Detail |
|---|---:|---|
| `main_figure_assertions` | PASS | passed=46/46; Figure5={'Figure5.panel_d.source_rows': 3, 'Figure5.panel_e.source_rows': 2, 'Figure5.panel_e.donors_with_12_positive_genes': 2} |
| `supplementary_figure_assertions` | PASS | passed=29/29; figures=7 |
| `publication_figure_files` | PASS | pairs=12; all >=4000x3000 and non-empty |
| `figure_source_data` | PASS | csv=12; hashes=12; Figure5 panels={'B': 12, 'C': 12, 'D': 3, 'E': 2} |
| `full_statistical_archive` | PASS | entries=63; sha256=AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5 |
| `manuscript_scope_and_statistics` | PASS | abstract=314; references=30; missing=none; stale=none |
| `supplementary_source_contract` | PASS | 7 figure markers; 8 tables; active C8S source status PASS |
| `author_identity` | PASS | first author and corresponding-author identity, emails, ORCIDs and affiliation present |
| `journal_target` | PASS | Genome Medicine primary without a frozen quartile assertion |
| `document_build_status` | PASS | {'Genome_Medicine_Manuscript_GateC8S_AUTHOR_COMPLETION_REQUIRED.docx': 59072, 'Additional_file_1_Supplementary_Information_GateC8S.docx': 2775025, 'Genome_Medicine_Cover_Letter_GateC8S_AUTHOR_CONFIRMATION_REQUIRED.docx': 40165} |
| `main_docx_ooxml` | PASS | line_numbers=True; page_field=True; even_odd=True; double_spacing=True |
| `supplement_docx_structure` | PASS | tables=8; explicit_geometry=8; inline_figures=7 |
| `docx_accessibility` | PASS | [{'file': 'main_text_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'supplement_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'cover_letter_a11y.json', 'high': 0, 'medium': 0, 'low': 0}] |
| `wps_render_and_visual_review` | PASS | [{'document': 'main', 'pages': 27, 'page_pngs': 27, 'bytes': 246934}, {'document': 'supplement', 'pages': 12, 'page_pngs': 12, 'bytes': 3286530}, {'document': 'cover', 'pages': 1, 'page_pngs': 1, 'bytes': 84312}]; S8 page=5; S1-S7 pages=6-12; visual_review=PASS_ALL_40_PAGES |
| `reference_verification` | PASS | Crossref PASS=26/26; manuscript references=30 |
| `attachment_integrity` | PASS | source entries=13; regulator entries=3; statistical entries=63 |
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

Gate C8B author declarations, institutional ethics determination, repository licence and immutable archive DOI; then rebuild once and complete portal preflight without changing frozen scientific results
