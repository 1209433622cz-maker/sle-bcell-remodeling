# SLE B-cell remodeling — post-reader-path claim-owner hostile audit

**Date:** 2026-09-02  
**Independent status:** `MAINTENANCE_FREEZE_SCIENCE_VALID__THREE_TABLE_ANCHOR_SEMANTIC_MISALIGNMENTS_FOUND`  
**Scope:** manuscript wording, figure/table evidence ownership, reader path and Nature/npj-style scientific presentation. No submission package, Release, Zenodo or new biological analysis.

## Executive decision

The Supplementary Figure first-citation refreeze is valid and should be retained. The current manuscript now encounters Supplementary Figures in strict S1-S10 order, all 21 main panels and 38 Supplementary panels remain scientifically justified, and the 15-page Supplementary layout is clean.

No existing figure panel should be replaced or redrawn. The remaining defects are not numerical or graphical; they are three small **evidence-owner / citation-anchor semantics** introduced when Supplementary Tables S1-S8 were made discoverable in the main manuscript.

## 1. Figure adjudication

### Main Figures

- Figure 1a-d: **KEEP**
  - 1a owns the identity-to-disease inference boundary.
  - 1b-d own frozen-representation stability and broad-state scope.
- Figure 2a-d: **KEEP**
  - unique primary composition result, sensitivities and leave-one-out diagnostics.
- Figure 3a-d: **KEEP**
  - unique GSE174188 B_CONV program and gene-level evidence hierarchy.
- Figure 4a-d: **KEEP**
  - unique source-label-defined GSE135779 replication and cross-dataset boundary.
- Figure 5a-e: **KEEP**
  - 5a is necessary to constrain evidence class and causal ceiling;
  - 5b-e provide regulator and orthogonal response evidence.

### Supplementary Figures

- S1-S10: **KEEP all scientific panels**
- No further prune, replacement or new panel is justified.
- The display renumbering should remain frozen.
- No global typography rerun should be reopened.

## 2. Confirmed reader-path improvement

The current main manuscript now cites Supplementary Figures in strict first-occurrence order:

`S1 -> S2 -> S3 -> S4 -> S5 -> S6 -> S7 -> S8 -> S9 -> S10`

This is a genuine improvement and should not be reversed.

The current Supplementary Information is also structurally cleaner:
- Tables S1-S9;
- Figures S1-S10;
- S1 begins on the same page as the closing external-mapping note without clipping;
- all subsequent Supplementary Figures retain title, legend and artwork together.

## 3. Remaining semantic defect A2 — Supplementary Table S3 is cited from the wrong claim

Current Results wording places `(Supplementary Table S3)` after:

`None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.`

But Supplementary Table S3 is **Quantitative anchors and prespecified boundaries**. It tabulates ARI/Jaccard, composition ORs, IFN effects, cross-dataset rho, M5911 NES and GSE23307 effects. It does not own the causal-ceiling statement.

### Recommended repair

Move the S3 citation to the preceding synthesis sentence:

**Preferred**
`Taken together, these layers support an IFN-centred interpretation of the replicated program while defining its evidential ceiling, with principal quantitative anchors summarized in Supplementary Table S3.`

Then keep the causal-ceiling sentence without the S3 citation:

`CollecTRI activity is inferred from observational disease-ranked statistics, M5911 is a response signature, and GSE23307 is a small healthy-donor perturbation. None of these analyses identifies a unique initiating ligand, establishes direct TF binding or demonstrates causal regulation in SLE.`

Scientific content does not change.

## 4. Remaining semantic defect A3 — Table S4a/S4b ownership should be explicit

Current manuscript cites the parent `Supplementary Table S4` only in the correlation-aware paragraph.

But the repaired Supplementary Table S4 now has two explicit scientific sections:
- **S4a** — correlation-aware core-regulator sensitivity;
- **S4b** — IFN-overlap-depletion summary.

### Recommended repair

Correlation-aware paragraph:
`(Supplementary Fig. S9; Supplementary Table S4a)`

Overlap-depletion paragraph:
`(Supplementary Fig. S10; Supplementary Table S4b)`

This creates exact claim ownership and prevents S4b from being technically present but semantically unanchored.

## 5. Remaining semantic defect A4 — Tables S5-S8 are attached to a sentence they do not directly support

Current Reproducibility wording ends:

`Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version (Supplementary Tables S5-S8).`

Tables S5-S8 instead document:
- selected figure-source mapping;
- reproducibility records;
- statistical/multiplicity families;
- statistical-results archive structure.

They do not specifically document the handling of superseded manuscripts.

### Recommended repair

Move the citation to the first Reproducibility sentence:

`Analyses were organized in timestamped run directories with immutable source objects, deterministic seeds, environment records, machine-readable decisions and SHA-256 manifests (Supplementary Tables S5-S8).`

Then retain the next sentence without the citation:

`Disease effects were estimated only after input, design and statistical-implementation verification. Superseded manuscripts and figures were retained for provenance but were not used as numerical sources for the present version.`

This is shorter, more accurate and should not require pagination compensation.

## 6. Figure 1a and Figure 5a replacement discussion

### Figure 1a

**KEEP.**

A replacement UMAP, decorative workflow, Sankey or cell-icon schematic would make the paper visually more conventional but would weaken the actual methodological contribution. The key task of 1a is to state that identity is reconstructed and adjudicated **before** disease fields are joined.

Only reopen 1a if actual-size inspection finds a concrete layout defect such as overlapping labels, unreadable text or ambiguous arrow direction. Do not replace its scientific role.

### Figure 5a

**KEEP.**

A causal IFN -> STAT1/STAT2 -> ISG network would look more mechanistic than the evidence permits. The current evidence-class panel is valuable precisely because it prevents the observational ULM, M5911 response set and two-donor perturbation from being over-interpreted.

Only geometry/typography defects would justify a source redraw; the panel concept should remain.

## 7. Nature/npj direction

The current project remains well aligned to the target scope because the journal explicitly includes single-cell systems biology and systems immunology. The manuscript's systems-level contribution is the explicit hierarchy linking identity reconstruction, uncertainty propagation, composition, pseudobulk transcription, external replication, calibration failure and regulator/response sensitivity.

No extra network model or new cohort should be added merely to signal "systems biology".

The artwork strategy should remain:
- Arial/Helvetica;
- 5-7 pt ordinary figure text;
- 8 pt bold panel labels;
- vector/editable PDF;
- compact, non-decorative layout.

## 8. Next-stage decision

Proceed to a very narrow:

`SUPPLEMENTARY_TABLE_CLAIM_OWNER_SEMANTIC_MICROPASS`

Only:
1. relocate the Supplementary Table S3 citation;
2. split the Supplementary Table S4 citation into S4a/S4b;
3. relocate the Tables S5-S8 citation to the reproducibility sentence it actually supports;
4. rebuild the manuscript from canonical Markdown;
5. assert all numerical text, all figure files and all Source Data are unchanged;
6. verify WPS/LibreOffice pagination and cross-reference coverage.

If these three semantic anchors are corrected without new defects, return immediately to:

`SCIENTIFIC_PRESENTATION_MAINTENANCE_FREEZE`

No further active panel redesign, additional analysis or broad prose polishing is justified.
