# Final scientific-object and numerical-traceability lock

Date: 2026-08-31  
Repository: `1209433622cz-maker/sle-bcell-remodeling`  
Baseline commit: `154e342e03af870cff44ccdbffc61b5a42e41740`  
Final run: `phase17_v7/npj_sba_traceability_lock/20260831_final_scientific_object_lock`  
Scope: scientific text, scientific objects, figure retention and numerical traceability only.

## 1. Objective

This round implemented and independently verified the next-stage target declared by the scientific-presentation freeze:

`FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCK`

The work was deliberately separated from submission engineering. It did not update or repack the journal submission ZIP, GitHub Release, Zenodo record, license, cover letter or journal metadata. It did not add a cohort, mapper, regulator, gene set, endpoint or post-hoc sensitivity branch.

The governing rule was:

1. verify the externally supplied traceability audit against repository objects rather than accepting its PASS language;
2. re-open a figure only when a numerical, biological-unit, claim-ownership or final-size legibility defect is demonstrated;
3. apply text corrections at source level and rebuild documents;
4. preserve all estimates, Source Data and figure exports byte-for-byte;
5. stop scientific editing once the traceability matrix is zero-defect.

## 2. Received evidence

The following external materials were retained under `00_project_management/traceability_lock_2026-08-31/received/`:

- `CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX_2026-08-31.csv`;
- `FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCK_AUDIT_2026-08-31.md`;
- the accompanying pasted audit narrative.

These files were treated as review evidence, not executable instructions or repository authority.

## 3. Independent audit judgment

The received matrix contained 24 traceability objects. Independent repository checks confirmed:

- C01-C22: numerical or derived Source Data relationships were coherent;
- C23: Supplementary Table S7 used an unnecessarily ambiguous cross-dataset biological-unit label;
- C24: Supplementary Table S6 overstated identity between the current presentation layer and the unchanged released Zenodo object;
- no effect estimate, confidence interval, P value, q value, threshold, sample count, donor count or direction required correction;
- no main or supplementary figure required numerical re-analysis or source replotting.

The pre-integration state was therefore correctly classified as:

`TRACEABILITY_LOCK_PENDING_2_SOURCE_TEXT_FIXES__NO_NUMERICAL_RERUN_REQUIRED`

## 4. Source-level corrections

Exactly three reversible source edits were made in Supplementary Information.

### 4.1 Table S6 provenance scope

Previous wording:

`Zenodo ... matches the frozen manuscript, figures and statistical outputs`

Final wording:

`Zenodo ...; version-specific archive of the released analysis code, Source Data and statistical outputs`

Reason: Figure 1a, Figure 5a and manuscript presentation had changed after the released archive, whereas Source Data and statistical results had not. The final wording accurately describes the released object without initiating a Zenodo update.

### 4.2 Table S7 gene-level unit

Previous wording:

`Donor/sample pseudobulk`

Final wording:

`Sample-cohort pseudobulk (GSE174188); donor pseudobulk (GSE135779)`

### 4.3 Table S7 four-program unit

The same dataset-specific biological-unit correction was applied to the four-program row.

The exact forward and reverse transformations are stored in `sources/TRACEABILITY_SOURCE_EDIT_LEDGER.csv`. Reverse application reconstructs the prior Supplementary source byte-for-byte. No numerical token was changed.

## 5. Main-figure decisions

All 21 main panels are retained.

| Panel group | Decision | Scientific reason |
|---|---|---|
| Figure 1a | KEEP | The prior source redraw already corrected the sample-cohort transcription unit and identity-adjudication sequence. The current traceability audit found no remaining object mismatch. |
| Figure 1b-d | KEEP | These panels uniquely own fixed-representation policy selection, replicate-level agreement and state-specific Jaccard/marker support. |
| Figure 2a-d | KEEP | The four panels distinguish observed composition, primary/secondary contrasts, prespecified sensitivities and leave-one-sample influence without converting a null result into equivalence. |
| Figure 3a-d | KEEP | The panels preserve program prioritization, replication sequence, gene-level testedness and prespecified specificity families. |
| Figure 4a-d | KEEP | The panels distinguish external donor-level program replication, internal/external evidence, weak genome-wide concordance and donor/source-label influence. |
| Figure 5a | KEEP | The prior source redraw now separates observed multiplicity-controlled results from interpretive evidence roles. |
| Figure 5b-e | KEEP | The panels separately own ULM estimates, proliferation comparators, M5911 response-set evidence and descriptive two-donor IFN-beta context. |

Final main-panel count:

- KEEP: 21;
- MODIFY in this round: 0;
- REMOVE: 0;
- REPLACE: 0;
- new analysis: 0.

The complete panel-by-panel record is `MAIN_PANEL_FINAL_TRACEABILITY_DECISION_MATRIX.csv`.

## 6. Supplementary-figure decisions

All ten supplementary figures are retained.

| Figure | Decision | Evidence ownership |
|---|---|---|
| S1 | KEEP | Source integrity and processing-cohort QC. |
| S2 | KEEP | Representation and cross-cohort diagnostics. |
| S3 | KEEP | Identity-policy adjudication. |
| S4 | KEEP | Composition diagnostics and sensitivity. |
| S5 | KEEP | Pseudobulk diagnostics. |
| S6 | KEEP | External-validation diagnostics. |
| S7 | KEEP | Correlation-aware regulator sensitivity, including the discovery STAT2 CAMERA exception. |
| S8 | KEEP | Frozen-IFN and M5911 overlap-depletion boundaries. |
| S9 | KEEP | End-to-end identity reconstruction and downstream propagation boundary. |
| S10 | KEEP | Corrected reference-calibration and unresolved transfer boundary. |

Final supplementary count:

- KEEP: 10;
- MODIFY in this round: 0;
- REMOVE: 0;
- REPLACE: 0.

The complete record is `SUPPLEMENTARY_FIGURE_FINAL_TRACEABILITY_DECISION_MATRIX.csv`.

## 7. Numerical traceability lock

The final matrix contains 24/24 PASS objects:

- 22 objects retained their verified numerical/derived PASS state;
- C23 is now `PASS_FIXED_EXACT_UNIT`;
- C24 is now `PASS_FIXED_PROVENANCE_SCOPE`;
- 0 objects require a numerical rerun;
- 0 objects require figure replacement.

Representative repository-level checks included:

- minimum fixed-representation mapped ARI `0.9902066569784328`;
- minimum fixed-representation mapping agreement `0.9998337765957448`;
- B_ASC state-median Jaccard `0.9913709736725989`;
- primary B_ASC OR `0.9466531606629468`, P `0.7872791209333905`, 43/47 strata;
- primary IFN/ISG effect `0.836556476435973`, q `2.9770041796839e-6`;
- childhood GSE135779 effect `1.04175695248946`, q `2.97551134813137e-6`;
- six positive and globally significant STAT1/STAT2 ULM estimates;
- three M5911 NES values above 3.0;
- 24/24 positive descriptive GSE23307 donor-gene effects;
- end-to-end minimum mapped ARI `0.929696806592458` and failed state-median Jaccard criterion `0.9303233364573572 < 0.95`;
- elastic-net coverage `0.941958041958042` and B_ASC precision `0.8852097130242825`, preserving the failed calibration boundary.

The final matrix is `FINAL_CORE_CLAIM_NUMERICAL_TRACEABILITY_MATRIX.csv`.

## 8. Source Data and figure-object integrity

The final lock references, rather than duplicates, the scientific-presentation figure objects.

- Source Data: 15/15 objects SHA-256 locked;
- figure exports: 30/30 objects SHA-256 locked, comprising 15 PDF and 15 PNG files;
- Source Data changed: false;
- figure exports changed: false;
- scientific estimates changed: false.

The exact inventories are:

- `SOURCE_DATA_FINAL_LOCK_MANIFEST.csv`;
- `FIGURE_FINAL_LOCK_MANIFEST.csv`.

## 9. Reproducible document rebuild

The final paired documents were rebuilt from Markdown sources. Existing DOCX/PDF files were not hand-edited.

Object inventory:

- manuscript: 150 paragraphs, 0 tables, 0 inline figures, 0 unresolved markers;
- Supplementary Information: 69 paragraphs, 10 tables, 10 inline figures, 0 unresolved markers;
- abstract: 145 words;
- accessibility: 0 high, 0 medium and 0 low findings in both DOCX files.

## 10. Cross-render defect and repair

The first dual-render attempt exposed a real layout defect:

- WPS: 31-page manuscript plus 16-page supplement;
- LibreOffice: 31-page manuscript plus 17-page supplement;
- the additional LibreOffice page was blank between Table S7 and the hard page break before Table S8.

Root cause:

- the generic table builder inserts a blank spacing paragraph after every table;
- the longer, corrected Table S7 unit caused that spacer to move to a new page in LibreOffice;
- the following hard page break then moved Table S8 to the next page, leaving the spacer page blank.

Rejected intermediate repair:

- the first spacer-removal rule classified image-only paragraphs as blank;
- the DOCX structural check immediately detected fewer than ten supplementary figures;
- that document was rejected before rendering or release.

Final repair:

- remove a pre-page-break paragraph only when it contains no text, no page break and no drawing object;
- preserve all ten figure paragraphs;
- do not change text size, table content, scientific values or figure scale.

Final dual render:

| Engine | Manuscript | Supplement | Total |
|---|---:|---:|---:|
| WPS | 31 | 16 | 47 |
| LibreOffice | 31 | 16 | 47 |

All 94 page views were inspected. No blank page, clipping, overlap, missing glyph, unresolved marker, figure mismatch or incoherent page transition remained. Table S6/S7 wrapping and the transition to Table S8 passed in both engines.

## 11. Runtime routing note

The first page-audit invocation used the `sle-bcell` environment, which does not contain `PyMuPDF/fitz`. A second attempt with the bundled document Python found the same missing module. The page audit was then executed with the existing `D:\bioinfor\python.exe`, which contains `fitz` and Pillow. These were import-stage environment failures only; neither attempt changed a document or produced a partial scientific result.

## 12. Final files and hashes

| File | Bytes | SHA-256 |
|---|---:|---|
| `Manuscript_final_scientific_lock.docx` | 60,659 | `18FCDD46E01B990D73756388A50269F1268E8F234A24E854665EAEB71E04AAE9` |
| `Manuscript_final_scientific_lock.pdf` | 240,454 | `41A5B0F7470044F12297A124A405892EAA8AE83F42B21C0A69D21B668743D5CD` |
| `Supplementary_Information_final_scientific_lock.docx` | 4,745,941 | `77D41CD77B047A5860C2DD4339BAE1A743927D16712E1413692323297672AE29` |
| `Supplementary_Information_final_scientific_lock.pdf` | 5,716,634 | `22EB754513AC2BC47CDF3F0C89A32D421EC8FE841D50EBF4EB69F406EC8EAA87` |

Run inventory after QA cleanup:

- files: 39;
- size: 23.25 MiB;
- retained QA: 18 contact sheets, two LibreOffice cross-render PDFs, two accessibility reports and two structural render audits.

## 13. Verification

- traceability-lock regression tests: 9/9 passed;
- full repository test discovery: 145/145 passed;
- final traceability objects: 24/24 PASS;
- Source Data manifest: 15/15 locked;
- figure export manifest: 30/30 locked;
- author-confirmed exact package SHA-256 remains `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`;
- Release, Zenodo and submission package were not changed.

## 14. Final scientific status

The project now satisfies:

`FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCKED`

The complete reader path remains:

`identity uncertainty -> bounded broad-compartment scaffold -> unsupported primary B_ASC composition contrast -> reproducible B_CONV IFN/ISG remodeling -> source-label-defined independent replication -> observational regulator/response convergence -> explicit reconstruction, calibration, transfer and causal boundaries`

No main or supplementary panel has a demonstrated numerical, semantic, ownership or final-size legibility defect. Further figure redesign is not scientifically justified unless a new objective mismatch is identified.

## 15. Next-stage target

The next scientific-content stage should be:

`FINAL_REFERENCE_CLAIM_SUPPORT_AND_TERMINOLOGY_LOCK`

Its scope should remain narrow:

1. verify all 32 reference identities and confirm that each citation supports the exact clause to which it is attached;
2. issue a claim-to-reference matrix covering Background, Methods rationale and Discussion interpretation;
3. lock the cross-document terminology dictionary for `disease-blind`, `bounded analysis scaffold`, `sample-cohort stratum`, `donor`, `source-label-defined`, `observational`, `descriptive`, `managed SLE` and negative-result boundaries;
4. change text only when a citation-scope or terminology defect is objectively demonstrated;
5. do not reopen a figure, numerical analysis or Source Data object without a new localized factual defect.

This is still manuscript science and reporting quality work, not journal submission preparation.
