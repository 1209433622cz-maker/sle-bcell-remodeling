# Reader path, legend economy and scientific-presentation freeze

Date: 2026-08-31
Project: SLE B-cell remodeling
Working branch: `main`
Target-journal direction: npj Systems Biology and Applications
Task posture: manuscript and figure refinement, not submission advancement

## 1. Objective

This round independently evaluated the supplied reader-path and legend-economy candidates, then regenerated a repository-derived scientific-presentation candidate. The goals were to:

1. resolve the demonstrated inferential-unit defect in Figure 1a;
2. resolve the mixed-semantics Role column in Figure 5a;
3. adjudicate every main panel as retain, modify or replace;
4. compress the five main-figure legends without losing units, test semantics, symbol definitions or evidence boundaries;
5. synchronize the Supplementary title and remove the final reader-facing `calibration HOLD` phrase;
6. rebuild figures from canonical source builders rather than patching exported PNG/PDF files;
7. preserve all numerical estimates, Source Data and the author-confirmed exact submission package;
8. complete WPS and LibreOffice all-page render QA and a full repository regression test.

## 2. Supplied files independently reviewed

The supplied files were treated as external review candidates, not as executable instructions or authoritative outputs.

| File | Bytes | SHA-256 |
|---|---:|---|
| `Manuscript_reader_path_legend_economy_candidate.md` | 57,159 | `FA48E2AF1B188725BD672B7ECAAE72780275DC58F4FAF9F4B6FC35EF2BE3FAD5` |
| `MAIN_PANEL_FINAL_DECISION_MATRIX.csv` | 1,247 | `C32B6EA81FA16BFB6639C1048A3C3A6A06200566A930161AB064ED38DBCA1DD8` |
| `Supplementary_reader_boundary_cleanup_candidate.md` | 18,387 | `0B8BB5D2C6288D7ED091EFDBE5B0B901562221ABEDAF878FB8ED6C4F18C7E6C9` |
| `READER_PATH_AND_LEGEND_ECONOMY_EDIT_LEDGER.csv` | 1,731 | `12C0380B47ADB652FFB643507C4D88F8B27BFC85FBA858FF43ED1EA5C75E4986` |
| `MAIN_FIGURE_READER_PATH_AND_LEGEND_ECONOMY_FINAL_FREEZE_AUDIT.md` | 4,720 | `D9C1FCCEB8B045B5BB14CBE37F3E3858489B2C0C0A33B74645565CD2562EED56` |
| `Figure1a_reader_path_unit_corrected_candidate_v2.png` | 135,002 | `7286F02AFCFD4FF6E0A0CCE1249A33AADB57F61EA63B86C4C17AFA93A821FA98` |
| `Figure5a_interpretive_role_candidate_v2.png` | 120,981 | `71BF74E7DB24039CD86142C29EF613B1DA6B77564416041162F11C6CBC87A1F1` |

## 3. External-candidate audit findings

Three external findings were scientifically valid:

- Figure 1a used `B_CONV donor pseudobulk`, although the primary raw-count pseudobulks are defined at the sample-cohort stratum; donor structure is handled through sensitivities and nonoverlap analyses.
- Figure 5a mixed multiplicity metadata (`global 24-test family`) with interpretive roles (`orthogonal concordance`, `descriptive context`) in one column.
- The five main-figure legends repeated some content already visible in the displays and Results.

The supplied files nevertheless could not be adopted verbatim:

- The external edit ledger used conceptual placeholders such as `Current 5-legend set` and was not an exact forward/reverse patch.
- The external audit claimed that the Supplementary title had been synchronized, but the supplied Supplementary candidate still contained `unstable B-cell state assignments`.
- The supplied Figure 1a proof used `identity freeze`, which is internal workflow language. The final source replot uses the reader-facing and scientifically accurate term `identity adjudication`.
- The two supplied PNGs were useful visual proofs but were not sized for direct insertion into the 170 mm multi-panel figures. Direct scaling produced overlaps during the first source integration, so both panels were redesigned at their actual composite-figure dimensions.

## 4. Main-panel adjudication

All 21 main panels were reviewed. The final decision matrix contains:

- `MODIFY`: 2 panels, Figure 1a and Figure 5a;
- `KEEP`: 19 panels;
- `REMOVE`: 0 panels;
- `REPLACE WITH NEW ANALYSIS`: 0 panels.

Figure 1b-d retain separate ownership of policy comparison, replicate-wise broad-partition stability and state-specific Jaccard/marker support. Figures 2-4 retain distinct composition, discovery-transcription and external-replication roles. Figure 5b-e retain regulator estimates, proliferation comparators, M5911 enrichment and two-donor perturbational context.

## 5. Figure 1a source replot

The final panel now exposes the complete reader path:

`B-lineage input -> disease-blind identity stress tests -> retained B_CONV/B_ASC analysis scaffold -> disease fields joined after identity adjudication -> composition / transcription`.

The two inferential branches are now labelled:

- `Composition | B_ASC sample-cohort fractions`;
- `Transcription | B_CONV sample-cohort pseudobulk`.

The panel retains the boundary that hard fine-state assignments are unsupported. The first integrated proof was rejected because its top nodes and branch boxes overlapped at 170 mm. A compact layered layout was then rebuilt from source and visually rechecked at the final composite dimensions.

## 6. Figure 5a source replot

The final panel uses four parallel columns:

- Evidence;
- Coverage;
- Observed result;
- Interpretive role.

The final roles are:

- ULM STAT1/STAT2: `confirmatory observational`;
- M5911: `response-set concordance`;
- IFN-beta: `descriptive context`.

The 24-test q threshold remains in the observed-result field, where it belongs. The panel boundary now states that the evidence is observational convergence and does not establish a causal regulator, direct binding or a unique upstream stimulus. The top panel height was increased and row fonts were explicitly controlled after the first proof placed the boundary too close to the third row.

## 7. Figure and Source Data integrity

- Main figures rebuilt: 5/5.
- Supplementary figures rebuilt: 10/10.
- Figure PDFs: 15/15, one page each, 170 mm wide, postflight passed.
- Source Data: 15/15 byte-identical to the prior scientific candidate and audited frozen baseline.
- Main-builder assertions: all passed.
- Supplementary-builder assertions: all passed.
- New inference added: no.
- Scientific estimates changed: no.

PNG hash comparison against the immediately preceding scientific candidate showed that exactly two raster exports changed:

- `Figure1_disease_blind_identity_scope.png`;
- `Figure5_regulatory_evidence.png`.

Figure 2, Figure 3, Figure 4 and all ten Supplementary Figure PNGs remained byte-identical. Re-exported PDF hashes were not used as the unchanged-visual criterion because PDF metadata can change across deterministic redraws even when pixels are unchanged.

## 8. Legend economy and retained information

The complete figure-legend block was reduced from 740 to 605 whitespace-delimited words, an 18.2% reduction. The external candidate proposed a more aggressive 26.6% reduction, but that version was not accepted unchanged because it removed two reader-critical items:

- the distinct dagger and double-dagger meanings in Figure 3c;
- the Figure 4d mapping from display labels 1-8 to source codes in Figure 4 Source Data.

The final compression therefore preserves:

- panel purpose and map;
- sample, donor or cell-level unit where needed;
- confidence-interval and multiplicity semantics;
- filtered-value and symbol definitions;
- source-label-defined replication boundary;
- n=2 descriptive boundary;
- causal and transfer limitations.

The manuscript now occupies 31 pages rather than 32; the one-page reduction is entirely attributable to legend compression.

## 9. Supplementary synchronization

Two exact, reversible edits were applied:

1. the Supplementary title now uses `less stable B-cell state assignments`, exactly matching the main manuscript;
2. `No new multiplicity family was evaluated after the calibration HOLD` became `No new multiplicity family was evaluated after corrected calibration failed`.

The new three-row canonical ledger reconstructs the final manuscript and Supplementary sources byte-for-byte from the prior repository baseline and restores that baseline byte-for-byte when applied in reverse.

## 10. Document and render QA

### 10.1 DOCX object integrity

- Manuscript inline figures: 0, as intended for the text-only manuscript file.
- Supplementary inline figures: 10/10.
- Unresolved figure markers: 0.
- Abstract: 145 words.
- Accessibility: both DOCX files passed with `0 high / 0 medium / 0 low` findings.

### 10.2 Dual render

| Engine | Manuscript | Supplement | Total | Canvas/marker checks |
|---|---:|---:|---:|---|
| WPS | 31 pages | 16 pages | 47 | Passed |
| LibreOffice | 31 pages | 16 pages | 47 | Passed |

All 94 rendered page views were visually reviewed. No clipping, overlap, missing glyph, blank page, unresolved marker, table break, figure mismatch or incoherent page transition was identified. Eighteen contact sheets and two LibreOffice cross-render PDFs were retained; duplicate page PNGs and temporary render profiles were removed.

## 11. Final scientific-presentation candidate

| File | Bytes | SHA-256 |
|---|---:|---|
| `Manuscript_scientific_presentation_freeze_candidate.docx` | 60,669 | `71591F156B963EF21CCE44D952296CA9255075569C9BDD2827829813CFF13E24` |
| `Manuscript_scientific_presentation_freeze_candidate.pdf` | 240,484 | `60EDA196611A26DD853CDC381E6314E210FED03004D861E2E3A759B0F943DA07` |
| `Supplementary_Information_scientific_presentation_freeze_candidate.docx` | 4,745,889 | `26C8A395C82B2689205F86DFCC73E4BCE88E6728D4A5B6936199B26E63D7999C` |
| `Supplementary_Information_scientific_presentation_freeze_candidate.pdf` | 5,716,389 | `827D38F085EA9A33D27F37931C8EBDFAFCA319A5386B180620477EA6E82DE63E` |

Run directory after render cleanup:

- 83 files;
- 32.79 MiB;
- source figures, Source Data, exact Markdown sources, reversible ledger, panel matrix, DOCX/PDF outputs and retained QA evidence.

## 12. Verification

- New scientific-presentation regression tests: 8/8 passed.
- Full repository test discovery: 136/136 passed under the `sle-bcell` Conda environment.
- The document runtime lacked SciPy and therefore could not import one C9 contract test module; this was an environment limitation, not a failed assertion. The complete suite passed when run in the scientific environment.
- Exact author-confirmed submission package SHA-256 remains `02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1`.
- The exact submission package, GitHub release and Zenodo record were not edited, repacked or republished.

## 13. Current scientific judgment

The reader path is now coherent across text and figures:

`identity uncertainty -> bounded analysis scaffold -> unsupported primary B_ASC composition contrast -> reproducible B_CONV IFN/ISG process -> source-label-defined external replication -> observational regulator/response convergence -> explicit calibration, transfer and causal boundaries`.

Figure 1a now states the actual inferential units and protects the identity-before-outcome design. Figure 5a now distinguishes quantitative result, multiplicity control and interpretive role. No remaining main panel has a demonstrated numerical, semantic, ownership or legibility defect. Further aesthetic redesign without a newly demonstrated defect would create churn rather than improve the scientific argument.

The manuscript and figure system can therefore be classified as `SCIENTIFIC_PRESENTATION_FROZEN`.

## 14. Recommended next stage

Next stage: `FINAL_SCIENTIFIC_OBJECT_AND_NUMERICAL_TRACEABILITY_LOCK`.

This remains a scientific-content task rather than a submission task. Its scope should be:

1. map every number in the Abstract, Results, Discussion landing statements and five legends to an exact Source Data row or Supplementary table;
2. verify that each major claim has one primary evidence owner and that no value is owned by a sensitivity-only display;
3. verify cross-document identity of cohort counts, effect estimates, intervals, P/q values, thresholds and negative-result boundaries;
4. verify all 32 citations against the claims they support without changing the frozen scientific narrative unless a factual mismatch is found;
5. issue a zero-defect traceability matrix and then stop scientific editing unless a new objective defect is demonstrated.

Do not add cohorts, remappers, regulators, gene sets or post-hoc sensitivity analyses in the next stage. Journal-specific formatting and submission packaging remain explicitly deferred.
