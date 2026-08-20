# Supplementary information

## Disease-blind single-cell reconstruction identifies replicated interferon remodeling and convergent regulatory evidence in systemic lupus erythematosus B cells

**Version:** Gate C8, 20 August 2026

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This file documents the prespecified governance, identity boundary, inferential units, validation hierarchy and reproducibility assets supporting the main manuscript. It does not introduce post hoc disease-defined cell states or new claims beyond the Gate C7 scientific freeze.

## Supplementary Methods 1 | Gate governance and outcome protection

The workflow used sequential gates for source integrity, hard quality control, disease-blind identity reconstruction, sample-level composition, within-compartment pseudobulk analysis, independent validation and external regulatory evidence. Protected disease fields were separated during identity reconstruction. Real outcome effects were unlocked only after the relevant input, mapping, contrast and statistical-engine contracts had been recorded. Each gate retained a machine-readable decision and SHA-256 integrity manifest.

## Supplementary Methods 2 | Identity stability boundary

The initial five-state model failed the prespecified resampling thresholds. Repair analyses evaluated four-, three- and two-level mappings without consulting disease labels. Only the broad B_CONV/B_ASC solution met all stability criteria across 20 resampling runs. Fine naive-memory structure was therefore retained as continuous transcriptional context rather than a hard publication subtype. This negative boundary is part of the result, not a quality-control artifact to be removed.

## Supplementary Methods 3 | Biological units and contrast hierarchy

GSE174188 composition and expression analyses used sample-by-processing-cohort strata; donor-aware sensitivities addressed repeated samples. GSE135779 used donors as the biological units. Primary, internal, donor-nonoverlap, secondary flare, childhood, combined and adult contrasts remained separate. No bridge stratum was used to manufacture a pooled disease coefficient, and internal GSE174188 estimates were not described as independent validation.

## Supplementary Methods 4 | Robustness and specificity

Prespecified sensitivity analyses varied minimum cell support, excluded residual-doublet-risk cells, deleted samples or donors one at a time, omitted source labels and compared platelet/ambient, ASC/UPR and pan-B control programs. The TF-target family used one global correction across 24 tests. STAT1 and STAT2 core results underwent leave-one-target and deterministic 80% target-resampling analyses. The GSE23307 two-donor perturbation remained descriptive.

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
| Primary B_ASC composition | odds ratio 0.947; 95% CI 0.636-1.410; P=0.787 |
| GSE174188 primary IFN/ISG | effect 0.837; 95% CI 0.525-1.148; q=2.98 x 10^-6 |
| GSE174188 donor-nonoverlap IFN/ISG | effect 1.086; q=3.61 x 10^-4 |
| GSE135779 childhood IFN/ISG | effect 1.042; 95% CI 0.681-1.402; q=2.98 x 10^-6 |
| Cross-dataset genome-wide agreement | 4,410 genes; Spearman rho=0.026 |
| M5911 enrichment | NES 3.187, 3.050 and 3.527 |
| GSE23307 perturbation | donor effects 3.294 and 3.666; 12/12 genes positive in each |

## Supplementary Table S4 | Figure and source-data map

| Figure | Frozen gate | Machine-readable source |
|---|---|---|
| Figure 1 | C2B4 identity freeze | Figure1_source_data.csv |
| Figure 2 | C3A composition decision | Figure2_source_data.csv |
| Figure 3 | C4B GSE174188 transcription | Figure3_source_data.csv |
| Figure 4 | C5B independent replication | Figure4_source_data.csv |
| Figure 5 | C6B regulatory framing | Figure5_source_data.csv |

## Supplementary Table S5 | Reproducibility contract

| Component | Frozen record |
|---|---|
| Gate C7 scientific audit | `phase17_v7/gateC7/20260820_manuscript_figure_integration/06_GATE_C7_FINAL_AUDIT.json` |
| Claim-number crosswalk | `phase17_v7/gateC7/20260820_manuscript_figure_integration/02_CLAIM_NUMBER_CROSSWALK.csv` |
| Figure-source crosswalk | `phase17_v7/gateC7/20260820_manuscript_figure_integration/03_FIGURE_SOURCE_CROSSWALK.csv` |
| Numeric-source crosswalk | `phase17_v7/gateC7/20260820_manuscript_figure_integration/04_MANUSCRIPT_NUMERIC_SOURCE.csv` |
| Active manuscript source | `01_manuscript/manuscript_v10_genome_medicine_submission_2026-08-20.md` |
| Repository commit inherited by Gate C8 | `05d5d60` |

## Supplementary note on superseded artifacts

Earlier manuscripts and figures remain in the repository for provenance but are not numerical sources for this submission. In particular, the previous ABC/APC-like hard-subtype narrative and untransformed GSE23307 outputs are superseded and excluded from every active claim, figure and submission file.
