# Supplementary information

## Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells

**Version:** Gate C8R, 20 August 2026

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This file documents the prespecified governance, identity boundary, inferential units, validation hierarchy and reproducibility assets supporting the main manuscript. Gate C8R corrects the Figure 2a control-group rendering, applies explicit panel-data assertions, adds a correlation-aware STAT1/STAT2 sensitivity and updates the narrative without altering frozen upstream estimates.

## Supplementary Methods 1 | Gate governance and outcome protection

The workflow used sequential gates for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Real outcome effects were unlocked only after the relevant input, mapping, contrast and statistical-engine contracts had been recorded. Each gate retained a machine-readable decision and SHA-256 integrity manifest.

## Supplementary Methods 2 | Identity stability boundary

The initial five-state model failed the prespecified resampling thresholds. Repair analyses evaluated four-, three- and two-level mappings without consulting disease labels. Only the broad B_CONV/B_ASC solution met all stability criteria across 20 resampling runs. Fine naive-memory structure was therefore retained as continuous transcriptional context rather than a hard publication subtype. This negative boundary is part of the result, not a quality-control artifact to be removed.

## Supplementary Methods 3 | Biological units and contrast hierarchy

GSE174188 composition and expression analyses used sample-by-processing-cohort strata; donor-aware sensitivities addressed repeated samples. GSE135779 used donors as the biological units. Primary, internal, donor-nonoverlap, secondary flare, childhood, combined and adult contrasts remained separate. No bridge stratum was used to manufacture a pooled disease coefficient, and internal GSE174188 estimates were not described as independent validation.

## Supplementary Methods 4 | Robustness and specificity

Prespecified sensitivity analyses varied minimum cell support, excluded residual-doublet-risk cells, deleted samples or donors one at a time, omitted source labels and compared platelet/ambient, ASC/UPR and pan-B control programs. The TF-target family used one global correction across 24 tests. STAT1 and STAT2 core results underwent leave-one-target and deterministic 80% target-resampling analyses. The GSE23307 two-donor perturbation remained descriptive.

## Supplementary Methods 5 | Correlation-aware regulator sensitivity

The Gate C8R sensitivity reused frozen STAT1/STAT2 signed targets, model matrices, contrasts and tested-gene backgrounds. Voom precision weights fed CAMERA with residual-estimated inter-gene correlation and FRY directional rotation tests. BH adjustment was applied across six core tests within each method. Exact agreement with frozen ULM matched-target counts was mandatory. The analysis was post-audit robustness testing and did not constitute independent replication.

## Supplementary Table S1 | Dataset roles and inferential units

| Resource | Role | Biological unit | Active scope |
|---|---|---|---|
| GSE174188 | Discovery and internal validation | Sample-cohort stratum; donor sensitivities | Disease-blind B_CONV/B_ASC identity, composition and B_CONV transcription |
| GSE135779 | Independent SLE validation | Donor | Broad conventional-B analog; childhood primary |
| CollecTRI/OmniPath | Curated regulator prior | Ranked genes within contrast | Prespecified eight-regulator, three-contrast family |
| MSigDB M5911 | Orthogonal response prior | Ranked genes within contrast | Hallmark interferon-alpha response enrichment |
| GSE23307 | Orthogonal perturbation support | Paired profile within donor | Descriptive IFN-beta response, n=2 donors |

## Supplementary Table S2 | Claim boundaries

| Supported | Not supported |
|---|---|
| Broad disease-blind B_CONV and B_ASC identity | Stable hard naive, memory or atypical subtypes |
| Null primary B_ASC relative-abundance result | General B_ASC expansion in SLE |
| Replicated IFN/ISG remodeling within B_CONV | Genome-wide shared disease transcriptome |
| Convergent STAT1/STAT2 target activity | Causal TF activation or direct binding |
| IFN-centred response evidence | A unique initiating IFN ligand in SLE |

## Supplementary Table S3 | Frozen quantitative anchors

| Analysis | Frozen result |
|---|---|
| Identity stability | minimum mapped ARI 0.990; minimum agreement 0.9998; minimum median Jaccard 0.991 |
| Primary B_ASC composition | 43 controls and 47 managed SLE; odds ratio 0.947; 95% CI 0.636-1.410; P=0.787 |
| GSE174188 primary IFN/ISG | effect 0.837; 95% CI 0.525-1.148; q=2.98 x 10^-6 |
| GSE174188 donor-nonoverlap IFN/ISG | effect 1.086; q=3.61 x 10^-4 |
| GSE135779 childhood IFN/ISG | effect 1.042; 95% CI 0.681-1.402; q=2.98 x 10^-6 |
| Cross-dataset genome-wide agreement | 4,410 genes; Spearman rho=0.026 |
| M5911 enrichment | NES 3.187, 3.050 and 3.527 |
| GSE23307 perturbation | donor effects 3.294 and 3.666; 12/12 genes positive in each |

## Supplementary Table S4 | Correlation-aware core-regulator sensitivity

| Contrast | Regulator | Matched targets | Inter-gene correlation | CAMERA BH q | FRY BH q |
|---|---|---:|---:|---:|---:|
| GSE174188 primary | STAT1 | 98 | 0.0362 | 0.0263 | 6.043e-06 |
| GSE174188 primary | STAT2 | 14 | 0.1225 | 0.1355 | 4.909e-05 |
| GSE174188 donor-nonoverlap | STAT1 | 129 | 0.0209 | 0.0263 | 8.49e-06 |
| GSE174188 donor-nonoverlap | STAT2 | 19 | 0.1191 | 0.0263 | 4.277e-07 |
| GSE135779 childhood | STAT1 | 161 | 0.0301 | 0.0263 | 2.685e-05 |
| GSE135779 childhood | STAT2 | 20 | 0.1223 | 0.03026 | 1.231e-05 |

CAMERA and FRY directions were positive in all six tests. CAMERA passed BH correction in five of six; the explicit exception was GSE174188 primary STAT2 (q=0.1355). FRY passed BH correction in all six.

## Supplementary Table S5 | Figure and source-data map

| Figure | Frozen gate | Machine-readable source |
|---|---|---|
| Figure 1 | C2B4 identity freeze; C8R render repair | Figure1_source_data.csv |
| Figure 2 | C3A composition decision; C8R group-map repair | Figure2_source_data.csv |
| Figure 3 | C4B transcription; C8R label clarification | Figure3_source_data.csv |
| Figure 4 | C5B replication; C8R axis clarification | Figure4_source_data.csv |
| Figure 5 | C6B regulatory framing; C8R hierarchy clarification | Figure5_source_data.csv |

## Supplementary Table S6 | Reproducibility contract

| Component | Frozen record |
|---|---|
| C8R panel-data assertions | `phase17_v7/gateC8R/20260820_pre_submission_repair/02_PANEL_DATA_ASSERTIONS.json` |
| Correlation-aware sensitivity | `phase17_v7/gateC8R/20260820_pre_submission_repair/03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv` |
| Correlation-aware decision | `phase17_v7/gateC8R/20260820_pre_submission_repair/04_CORRELATION_AWARE_STAT1_STAT2_DECISION.json` |
| Active manuscript source | `01_manuscript/manuscript_v11_genome_medicine_gateC8R_2026-08-20.md` |
| Public repository | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Immutable release | Author-controlled licence and archive DOI remain required before portal submission |

## Supplementary note on superseded artifacts

Earlier manuscripts, Gate C7 figures and the Gate C8 package remain in the repository for provenance but are not active submission sources. Figure 2a in Gate C8 omitted control points because the plotting layer expected `normal` while the frozen source encoded controls as `na`; Gate C8R maps the frozen values explicitly and asserts 43 controls, 47 managed-SLE strata and 90 total points before rendering. No composition estimate changed. The previous ABC/APC-like hard-subtype narrative and untransformed GSE23307 outputs remain superseded and excluded from every active claim, figure and submission file.
