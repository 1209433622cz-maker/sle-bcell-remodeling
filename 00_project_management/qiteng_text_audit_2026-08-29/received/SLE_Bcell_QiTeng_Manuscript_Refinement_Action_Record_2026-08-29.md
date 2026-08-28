# SLE B-cell remodeling manuscript refinement - action record

Date: 2026-08-29  
Project: `1209433622cz-maker/sle-bcell-remodeling`  
Source snapshot: GitHub `main` at `74678c7cf75e376d90cdae886b6a1a4cf1951714`; the manuscript source corresponds to the corrected candidate integrated at `05e41f40284fc65c6cd18bbecaa2bf507e81b5f8`.  
Writing framework: `QiTeng Academic Writing Skill v0.3.21`  
Scope: manuscript prose only. No new analysis, no figure redraw, no submission package, and no PubMed lookup.

## 1. Input and immutable scientific boundary

The refinement started from the corrected candidate manuscript after the Figure 1c criterion-label correction had been integrated. The following scientific boundaries were treated as immutable:

- R1 end-to-end identity result remains a B_ASC-specific reproducibility failure at the prespecified criterion; B_CONV/B_ASC is an analysis scaffold, not a universal taxonomy.
- Primary B_ASC composition remains null.
- Primary and donor-nonoverlap B_CONV IFN/ISG effects remain positive.
- Source-label-defined GSE135779 childhood IFN/ISG replication remains the independent external replication layer.
- Genome-wide cross-dataset correlation remains low and does not support transcriptome-wide replication.
- C9R corrected source-label-independent remapping remains calibration-limited; no corrected disease outcome was estimated.
- STAT1/STAT2 evidence remains observational and overlap-qualified; it is not causal proof.
- GSE23307 remains descriptive at n=2.
- No figure, source-data table, threshold, contrast, gene set, regulator family or cohort was changed.

## 2. QiTeng argument map used for the rewrite

### Central claim

The reproducible level of SLE B-cell remodeling is a process-level IFN/ISG transcriptional program, whereas hard cell-state assignments have explicit reproducibility limits.

### Unresolved problem

Single-cell disease studies can conflate cell identity, abundance and transcription when cluster labels are outcome-informed, cells are treated as replicates, or technical/cohort structure is not separated from disease effects.

### Novelty

The contribution is not rediscovery of interferon activity. The study tests the inferential granularity itself: identity is defined without disease labels, biological units are respected, state-assignment uncertainty is propagated, the central program is tested in an independent cohort, and failed stability/calibration criteria remain visible as evidence boundaries.

### Evidence ladder

- E1/E2: disease-blind identity and composition/transcription analyses.
- E2: donor-nonoverlap robustness and independent GSE135779 program replication.
- E2, qualified: STAT1/STAT2 cross-method convergence and overlap-depletion sensitivities.
- Contextual/orthogonal: M5911 response-set enrichment and two-donor GSE23307 perturbation.
- Explicit ceiling: no universal taxonomy, no discrete IFN-high subtype, no causal TF, no unique ligand, no demonstrated clinical utility.

## 3. Major editorial actions

### 3.1 Title

Changed only the principal verb:

- Before: `... reconstruction separates unstable ...`
- Refined: `... reconstruction distinguishes unstable ...`

Rationale: `distinguishes` better expresses an inferential contrast without implying that the two biological phenomena are physically separable entities.

### 3.2 Abstract

Rebuilt using the QiTeng original-research route:

`GAP -> METHODS -> CORE RESULT -> EXTERNAL VALIDATION -> BOUNDARY -> BOUNDED CONTRIBUTION`

Key changes:

- opened with the inferential problem rather than a generic SLE description;
- kept the B_ASC end-to-end failure visible because it changes the claim ceiling;
- prioritized the primary IFN effect and independent childhood replication;
- compressed regulator sensitivities into one qualified sentence instead of listing every sensitivity result;
- landed on process-level reproducibility versus taxonomy-level instability.

Final abstract length: approximately 342 words.

### 3.3 Background

Reconstructed from five background-like units into four argument-driven paragraphs:

1. single-cell resolution creates an inferential problem;
2. SLE interferon/plasmablast biology is established but context-dependent;
3. the unresolved gap is the reproducible inferential layer, not whether IFN exists;
4. the study response is a staged, disease-blind and biological-unit-aware hierarchy.

This makes the final paragraph a research contract rather than another background paragraph.

### 3.4 Methods

Preserved reproducibility-critical detail while reducing internal QA language.

Structural improvement:

- split `Disease-blind representation, identity adjudication and end-to-end sensitivity` into:
  - `Disease-blind representation and identity adjudication`;
  - `End-to-end identity sensitivity and uncertainty propagation`.

Other changes:

- converted repeated internal-control-plane wording into conventional scientific prose;
- reduced uses of `frozen` where `prespecified`, `fixed` or ordinary methodological wording conveyed the same scientific meaning;
- retained all thresholds, denominators, analysis units, model families, multiplicity definitions, seeds/iteration-relevant descriptions and validation-class distinctions;
- retained the corrected external-mapping failure as a technical repair with no corrected disease outcome.

### 3.5 Results

Rebuilt subsection headings to be answer-oriented and evidence-class explicit:

- `Disease-blind reconstruction supports an analysis scaffold, not a reproducible taxonomy`
- `B_ASC abundance does not explain the primary disease contrast`
- `A prespecified IFN/ISG program dominates within-B_CONV transcription`
- `Independent GSE135779 replicates the IFN program, not a transcriptome-wide state`
- `Corrected external remapping does not satisfy the prespecified calibration criterion`
- `Regulatory and response evidence converges on, but does not establish, IFN-centred control`

Paragraphs were edited toward the QiTeng evidence packet:

`DIRECTION/MAGNITUDE -> UNCERTAINTY -> MULTIPLICITY -> ROBUSTNESS -> BOUNDARY`

The B_ASC instability and C9R calibration failure remain in the main Results because they change the claim class.

### 3.6 Discussion

Reconstructed to require an interpretive delta from the Results:

1. contribution reset: process-level reproducibility vs taxonomy-level reproducibility;
2. reconciliation with established SLE IFN/plasmablast literature;
3. explanation of program-level replication despite genome-wide rho=0.026;
4. regulator convergence with explicit cross-method and overlap limits;
5. removal of unsupported co-equal narratives;
6. prospective translational implication and decisive next test;
7. consolidated limitations and evidence ceiling;
8. restrained integrated landing.

The Discussion now treats negative evidence as boundary-changing evidence rather than as defensive caveats.

### 3.7 Conclusions

Rewritten to compress the adjudicated claim rather than repeat the full Results:

- reproducible IFN/ISG process;
- unstable hard state assignments;
- independent validation and qualified regulatory support;
- no universal taxonomy, generalized B_ASC expansion, causal regulator or unique ligand.

## 4. Citation and reference integrity

The rewrite changed citation placement, so a global reference-order repair was performed rather than leaving the old numbering in place.

Checks completed:

- all 32 bibliographic identities preserved;
- no reference added or removed;
- no PubMed search performed;
- references globally renumbered by first appearance;
- first-appearance sequence now runs continuously from 1 through 32;
- no orphan or out-of-range citation remains;
- bibliography contains exactly the same 32 source identities as the input manuscript.

A machine-readable renumber map was generated internally during QA.

## 5. Quantitative manuscript comparison

| Section | Input words | Refined words | Editorial interpretation |
|---|---:|---:|---|
| Abstract | 342 | 342 | Same budget, stronger hierarchy |
| Background | 432 | 463 | Added inferential tension and explicit gap |
| Methods | 2,095 | 2,174 | Slight expansion to improve reconstructability and identity-sensitivity separation |
| Results | 2,066 | 2,072 | Essentially unchanged length; stronger effect-first architecture |
| Discussion | 902 | 1,010 | Added interpretive delta, contradiction resolution and future test |
| Conclusions | 71 | 82 | More precise claim compression |
| References | 32 | 32 | Same bibliographic identities; renumbered by first appearance |

The goal was not compression for its own sake. The manuscript was already mature, so edits were concentrated where they changed reader state, claim calibration or section function.

## 6. Document production and QA

### DOCX/PDF generation

- Markdown was converted to DOCX without carrying forward the previous reference-document rendering artifact.
- The final DOCX was styled as a clean research manuscript with continuous line numbering, Arial typography, structured headings, header/footer and page numbering.
- The PDF was generated from the final DOCX with LibreOffice.

### Visual QA

Final manuscript: 18 pages.

All 18 rendered pages were visually inspected. No clipping, overlap, broken glyphs, empty pages, malformed references or heading/page-break defects were observed.

A rendering artifact found in an earlier reference-style build (`X` after the Data Availability paragraph) was traced to the old reference-document path. The final DOCX was rebuilt from a clean Pandoc document and restyled programmatically; the artifact is absent from the final DOCX/PDF.

### Accessibility QA

DOCX audit:

- high-severity findings: 0
- medium-severity findings: 0
- low-severity findings: 6

All six low-severity findings are raw-URL display text for ORCID, GitHub and GEO links. They were retained intentionally because literal repository/accession URLs are useful in a scientific manuscript and do not create a layout or scientific-integrity problem.

### Final hashes

- DOCX SHA-256: `86ef9d51c7d7b2472a434ce4851f5daa2231479491fe43112aadfe5cae719078`
- PDF SHA-256: `95121b630498dbb2d8d442816f772daa8e6616d565ed1f81cfd8b33f635bad70`
- Refined Markdown SHA-256: `23211e9dfd05e5a7875b13fb4c38cb6967240e9e4ffdd806387107ff09d013f6`

## 7. What was deliberately not done

- No figure was redrawn or edited.
- No new cohort, mapper, threshold, gene set, TF family or sensitivity was added.
- No disease effect was recomputed.
- No submission package was produced.
- No journal-specific formatting was applied.
- No PubMed search or published-version lookup was performed.
- No existing negative/HOLD result was softened to create a stronger claim.

## 8. Current manuscript readiness

My assessment after this round:

- scientific logic: 98-99%
- claim calibration: 99%
- Methods-Results mirror: 98%
- Discussion interpretive depth: 98%
- citation/reference surface integrity: 100% for current 32-reference set
- document rendering quality: PASS
- journal-specific readiness: intentionally not assessed because no target journal is currently selected

## 9. Recommended next stage

Do **not** reopen exploratory bioinformatics.

The next high-value stage should be a very narrow:

`PRE_JOURNAL_HOSTILE_TEXT_AUDIT_AND_AUTHOR_SIGNOFF`

Recommended scope:

1. line-by-line claim-evidence ownership audit;
2. check that every material R1/C9R negative boundary propagates consistently through title, abstract, Results, Discussion and Conclusion;
3. test the five strongest hostile-review objections without rewriting successful sections;
4. verify every figure legend remains semantically aligned with the unchanged figures and refined main text;
5. have both authors review the exact refined DOCX/PDF rather than a prior snapshot;
6. only after a journal is selected, perform one target-specific title/abstract/section/format pass.

The scientific work should remain frozen unless this hostile audit reveals a decision-changing implementation error. The next improvement should come from final claim-surface consistency and author adjudication, not from adding more analyses.
