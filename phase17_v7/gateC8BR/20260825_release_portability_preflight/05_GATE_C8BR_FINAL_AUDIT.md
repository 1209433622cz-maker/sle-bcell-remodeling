# Gate C8BR release-portability and editorial preflight audit

**Decision:** `PASS_GATE_C8BR_PORTABILITY_EDITORIAL_PREFLIGHT_AUTHOR_ACTION_REQUIRED`

**Technical package:** PASS

**Scientific estimates changed:** NO

**Portal submission authorized:** NO - author-controlled hard stops remain.

## Checks

| Check | Result | Detail |
|---|---:|---|
| `portable_release_runtime` | PASS | python=3.13.7; executable=C:\ProgramData\miniforge3\envs\sle-bcell-c8br-release\python.exe; machine-local defaults absent |
| `main_figure_assertions` | PASS | passed=46/46 |
| `supplementary_figure_assertions` | PASS | frozen C8S assertions passed=29/29 |
| `publication_figure_files` | PASS | pairs=12; all >=4000x3000 and non-empty |
| `figure5c_specificity_wording` | PASS | Prespecified proliferation specificity comparators |
| `figure5a_parallel_evidence_semantics` | PASS | ['Parallel evidence architecture', 'Replicated IFN/ISG remodeling', 'Regulatory branch', 'Response branch'] |
| `figure_source_data` | PASS | csv=12; Figure5 panels={'B': 12, 'C': 12, 'D': 3, 'E': 2}; Figure5 source matches Gate C8B=True |
| `frozen_statistical_archive` | PASS | entries=63; sha256=AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5 |
| `manuscript_release_reader_contract` | PASS | abstract=314; references=32; missing=none; forbidden=none |
| `cover_letter_scope` | PASS | ligand-agnostic IFN wording and unambiguous M5911 independence wording present |
| `reference_verification` | PASS | Crossref PASS=28/28; manuscript references=32; PMIDs 42119160 and 42373139 recorded |
| `source_build_contract` | PASS | v14 source PASS; 7 supplement figure markers; estimates unchanged |
| `journal_target` | PASS | Genome Medicine retained without a frozen quartile assertion |
| `document_build_status` | PASS | {'Genome_Medicine_Manuscript_GateC8BR_AUTHOR_COMPLETION_REQUIRED.docx': 59720, 'Additional_file_1_Supplementary_Information_GateC8BR.docx': 2775076, 'Genome_Medicine_Cover_Letter_GateC8BR_AUTHOR_CONFIRMATION_REQUIRED.docx': 40181} |
| `main_docx_ooxml` | PASS | line_numbers=True; page_field=True; even_odd=True; double_spacing=True |
| `supplement_docx_structure` | PASS | tables=8; explicit_geometry=8; inline_figures=7 |
| `docx_accessibility` | PASS | [{'file': 'main_text_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'supplement_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'cover_letter_a11y.json', 'high': 0, 'medium': 0, 'low': 0}] |
| `wps_render_integrity` | PASS | [{'document': 'main', 'pages': 28, 'page_pngs': 28, 'bytes': 251033}, {'document': 'supplement', 'pages': 12, 'page_pngs': 12, 'bytes': 3286526}, {'document': 'cover', 'pages': 1, 'page_pngs': 1, 'bytes': 84468}] |
| `author_identity` | PASS | names, emails, ORCIDs and affiliation present |
| `hard_stops_visible` | PASS | manuscript placeholders=6; cover placeholders=2 |

## Author-controlled hard stops

- institutional ethics determination
- competing interests
- funding
- final CRediT contributions and all-author approval
- acknowledgements
- all-author originality/submission confirmation
- author/institution-approved code licence and immutable archive DOI
- APC or institutional agreement check

## Next stage

Complete author-controlled declarations and institutional ethics determination; approve a code licence; create an immutable release DOI; then replace all placeholders and run the zero-placeholder WPS and portal preflight without reopening scientific analysis
