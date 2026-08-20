# Gate C8B editorial and literature preflight audit

**Decision:** `PASS_GATE_C8B_EDITORIAL_LITERATURE_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

**Technical package:** PASS

**Scientific estimates changed:** NO

**Portal submission authorized:** NO - author-controlled hard stops remain.

## Checks

| Check | Result | Detail |
|---|---:|---|
| `main_figure_assertions` | PASS | passed=46/46 |
| `supplementary_figure_assertions` | PASS | frozen C8S assertions passed=29/29 |
| `publication_figure_files` | PASS | pairs=12; all >=4000x3000 and non-empty |
| `figure5c_specificity_wording` | PASS | Prespecified proliferation specificity comparators |
| `figure_source_data` | PASS | csv=12; Figure5 panels={'B': 12, 'C': 12, 'D': 3, 'E': 2} |
| `frozen_statistical_archive` | PASS | entries=63; sha256=AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5 |
| `manuscript_editorial_literature_contract` | PASS | abstract=314; references=31; missing=none; Authors information absent |
| `cover_letter_scope` | PASS | ligand-agnostic interferon-responsive wording present |
| `reference_verification` | PASS | Crossref PASS=27/27; manuscript references=31; PMID 42119160 recorded |
| `source_build_contract` | PASS | v13 source PASS; 7 supplement figure markers; estimates unchanged |
| `journal_target` | PASS | Genome Medicine retained without a frozen quartile assertion |
| `document_build_status` | PASS | {'Genome_Medicine_Manuscript_GateC8B_AUTHOR_COMPLETION_REQUIRED.docx': 59329, 'Additional_file_1_Supplementary_Information_GateC8B.docx': 2775124, 'Genome_Medicine_Cover_Letter_GateC8B_AUTHOR_CONFIRMATION_REQUIRED.docx': 40168} |
| `main_docx_ooxml` | PASS | line_numbers=True; page_field=True; even_odd=True; double_spacing=True |
| `supplement_docx_structure` | PASS | tables=8; explicit_geometry=8; inline_figures=7 |
| `docx_accessibility` | PASS | [{'file': 'main_text_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'supplement_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'cover_letter_a11y.json', 'high': 0, 'medium': 0, 'low': 0}] |
| `wps_render_integrity` | PASS | [{'document': 'main', 'pages': 27, 'page_pngs': 27, 'bytes': 247860}, {'document': 'supplement', 'pages': 12, 'page_pngs': 12, 'bytes': 3287320}, {'document': 'cover', 'pages': 1, 'page_pngs': 1, 'bytes': 84175}] |
| `author_identity` | PASS | names, emails, ORCIDs and affiliation present |
| `hard_stops_visible` | PASS | manuscript placeholders=6; cover placeholders=2 |

## Author-controlled hard stops

- institutional ethics determination
- competing interests
- funding
- final CRediT contributions and all-author approval
- acknowledgements
- all-author originality/submission confirmation
- open-source licence and immutable archive DOI

## Next stage

Complete Gate C8B author-controlled declarations, institutional ethics determination, repository licence and immutable archive DOI; then replace placeholders, run one final WPS review and portal preflight without reopening scientific analysis
