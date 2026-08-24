# Journal-facing prefreeze final audit

**Decision:** `PASS_GATE_C8BR_JOURNAL_FACING_PREFREEZE_AUTHOR_ACTION_REQUIRED`

**Technical package:** PASS

**Scientific estimates changed:** NO

**Portal submission authorized:** NO - author-controlled hard stops remain.

## Checks

| Check | Result | Detail |
|---|---:|---|
| `portable_release_runtime` | PASS | python=3.13.7; exact win-64 package spec present |
| `reproducibility_record` | PASS | tokens=7; separate analysis/release locks documented |
| `main_figure_assertions` | PASS | passed=46/46; source data unchanged |
| `supplementary_figure_assertions` | PASS | frozen assertions passed=29/29 |
| `publication_figure_files` | PASS | pairs=12; each PNG >=4000x3000 and each PDF non-empty |
| `reader_facing_figure_semantics` | PASS | Figure 1 graphical workflow; Figure 4 sequential omission labels; Figure 5 parallel branches |
| `figure_source_data` | PASS | 12/12 SHA manifest entries; all five main sources byte-identical; B-caSC0-7 retained |
| `frozen_statistical_archive` | PASS | entries=63; byte-identical sha256=AE903A53A19D7935464C601E2693192910EB4B59F5804D43DCA6ACA965D0B1F5 |
| `manuscript_reader_contract` | PASS | abstract=318; references=32; optional author biography omitted |
| `supplement_reader_contract` | PASS | exact resampling mechanics present; internal history absent; figures=7; tables=8 |
| `source_build_contract` | PASS | v15 manuscript and v6 supplement PASS; scientific estimates unchanged |
| `journal_target_and_cover` | PASS | Genome Medicine retained; claim-bounded cover letter; quartile not frozen |
| `reference_verification` | PASS | DOI identities PASS=28/28; numbered references=32 |
| `document_build_status` | PASS | {'Genome_Medicine_Manuscript_AUTHOR_COMPLETION_REQUIRED.docx': 59723, 'Supplementary_Information.docx': 2775576, 'Cover_Letter_AUTHOR_CONFIRMATION_REQUIRED.docx': 40181} |
| `portal_preview_aliases` | PASS | 18 unique clean aliases; source/alias/manifest hashes match; upload blocked |
| `main_docx_ooxml` | PASS | line_numbers=True; page_field=True; even_odd=True; double_spacing=True |
| `supplement_docx_structure` | PASS | tables=8; explicit_geometry=8; inline_figures=7 |
| `docx_accessibility` | PASS | [{'file': 'main_text_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'supplement_a11y.json', 'high': 0, 'medium': 0, 'low': 0}, {'file': 'cover_letter_a11y.json', 'high': 0, 'medium': 0, 'low': 0}] |
| `wps_render_integrity` | PASS | [{'document': 'main', 'pages': 28, 'page_pngs': 28, 'bytes': 251073}, {'document': 'supplement', 'pages': 13, 'page_pngs': 13, 'bytes': 3288063}, {'document': 'cover', 'pages': 1, 'page_pngs': 1, 'bytes': 84468}] |
| `confirmed_author_identity` | PASS | names, order, emails, ORCIDs, titles and supplied Zhi Chen biography preserved without inferring a Teng Qi biography |
| `hard_stops_visible` | PASS | manuscript placeholders=6; cover placeholders=2; author actions=21 |

## Author-controlled hard stops

- institutional ethics determination
- competing interests
- funding
- final CRediT contributions and all-author approval
- acknowledgements
- all-author originality and exclusive-submission confirmation
- correspondence-address approval
- author-approved repository licence and immutable archive DOI
- APC or institutional agreement check

## Next stage

Complete author-controlled declarations and institutional ethics determination; approve the correspondence address and repository licence; create an immutable release DOI; then replace all placeholders and run the zero-placeholder WPS and portal-field preflight without reopening scientific analysis.
