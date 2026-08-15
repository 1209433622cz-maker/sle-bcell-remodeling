# Action record: Gate C5B GSE135779 independent external validation

Date: 2026-08-15
Project: 6013RP-wyf / Phase 17 v7
Gate: C5B
Final decision: `PASS_GATE_C5B_INDEPENDENT_IFN_REPLICATION`

## 1. Objective and governance

This round tested whether the exact Gate C4A/C4B conventional-B-cell transcriptional
programs transfer to the independent GSE135779 SLE cohort. All source files,
source-label mappings, program genes, support thresholds, samples and model matrices
were frozen in Gate C5A before any new external disease coefficient was inspected.

The workflow enforced three locks:

1. verify every C5A artifact against its size and SHA256 manifest;
2. import all real matrices into R only for dimension and count-conservation checks,
   and qualify edgeR with synthetic null and signal data; and
3. fit the five real models only after the qualification decision passed.

Legacy GSE135779 scores and effect tables were not used as confirmatory inputs.

## 2. Frozen matrix exports

The source count object was
`07_EXTERNAL_PSEUDOBULK_COUNTS.npz`, SHA256
`2CB31DCDB5194C42CB52CBF3FD2D9530F137E9786F09BFDACDA4BE1EA9DC86C7`.
It was exported into five genes-by-samples integer matrices:

| Analysis | Role | Samples | HC | SLE | Total UMI | Design rank |
|---|---|---:|---:|---:|---:|---:|
| Childhood >=50 | primary | 43 | 11 | 32 | 89,498,882 | 2/2 |
| Combined >=50 | complementary | 54 | 16 | 38 | 98,962,678 | 3/3 |
| Adult >=50 | secondary | 11 | 5 | 6 | 9,463,796 | 2/2 |
| Combined >=20 | threshold sensitivity | 56 | 16 | 40 | 99,161,064 | 3/3 |
| Combined >=100 | threshold sensitivity | 51 | 16 | 35 | 98,136,354 | 3/3 |

Eight additional source-label omission matrices retained the same 43 childhood
donors and subtracted one of `B-caSC0` to `B-caSC7` from each donor's B_CONV counts.
No donor was reselected after subtraction. The minimum remaining support across
these analyses was 56 B cells, so every frozen primary donor remained analyzable.

All 13 matrices contained 32,738 unique Ensembl features. Python verified integer,
non-negative counts and column sums before export.

## 3. No-effect software and import qualification

The qualified environment was:

- R 4.6.0;
- Bioconductor 3.23;
- edgeR 4.10.1;
- limma 3.68.4;
- Matrix 1.7.5;
- statmod 1.5.2; and
- jsonlite 2.0.0.

R independently reproduced dimensions, sample-library sums, gene sums and integer
status for all five main and eight source-label matrices. Synthetic negative-binomial
qualification reproduced the C4B benchmark:

| Metric | Observed | Acceptance | Result |
|---|---:|---:|---:|
| Null P <0.05 fraction | 0.0553 | <=0.0800 | PASS |
| Null median log2FC | 0.0011 | absolute value <=0.10 | PASS |
| Signal median recovered log2FC | 1.1967 | >=0.80 | PASS |
| Signal sign concordance | 1.0000 | >=0.95 | PASS |
| Signal BH sensitivity | 1.0000 | >=0.80 | PASS |
| Signal empirical FDR | 0.0654 | <=0.10 | PASS |

No real external disease coefficient was fitted before all seven qualification
checks passed.

## 4. Gene-level models

Gene-level inference used TMM normalization, `filterByExpr`, robust dispersion
estimation and edgeR robust quasi-likelihood testing. BH correction was applied over
all tested genes within each contrast, while every full table retained all 32,738
Ensembl features.

| Analysis | Tested genes | FDR <0.05 | Up | Down |
|---|---:|---:|---:|---:|
| Childhood >=50 | 8,469 | 240 | 165 | 75 |
| Combined >=50 | 8,601 | 259 | 161 | 98 |
| Adult >=50 | 6,277 | 0 | 0 | 0 |
| Combined >=20 | 8,458 | 274 | 169 | 105 |
| Combined >=100 | 8,754 | 202 | 134 | 68 |

The leading childhood genes were dominated by coherent interferon-response genes,
including `IFI27`, `LGALS3BP`, `USP18`, `IFI44`, `IFI44L`, `OASL`, `RSAD2`,
`CMPK2`, `HERC5`, `IFI6`, `EPSTI1` and `OAS3`.

Independent Python review reloaded all five complete tables, confirmed unique
Ensembl keys, matched tested-gene counts and exactly reproduced every within-model
BH value.

## 5. Frozen program results

Program scores used the exact C4B formula: duplicate symbols summed, TMM logCPM,
within-analysis gene z scores, signed-arm aggregation and HC3 sandwich uncertainty.
Multiplicity was BH across the four confirmatory programs within each model.

| Program | Childhood effect / q | Combined effect / q | Adult effect / q |
|---|---:|---:|---:|
| Naive-to-memory | 0.231 / 0.319 | 0.229 / 0.474 | 0.362 / 0.662 |
| Atypical/low-naive | 1.191 / 0.000510 | 1.031 / 0.00115 | 0.662 / 0.386 |
| APC/HLA | 0.266 / 0.211 | 0.082 / 0.607 | -0.414 / 0.291 |
| IFN/ISG | 1.042 / 2.98e-06 | 0.996 / 1.31e-06 | 0.968 / 0.291 |

Only IFN/ISG is promoted as a cross-dataset result. The external atypical/low-naive
signal is strong in childhood and combined GSE135779, but the corresponding GSE174188
primary result was null and slightly negative. It is therefore dataset-specific or
composition-sensitive evidence, not independent replication. Naive-to-memory changes
direction relative to GSE174188 and is external-null. APC/HLA is directionally positive
in childhood but external-null. These axes cannot share the central claim.

## 6. Independent IFN/ISG replication

The exact 12-gene IFN/ISG program passed every frozen external criterion:

- childhood primary: effect 1.042, 95% CI 0.681 to 1.402,
  P=7.44e-07 and four-program BH q=2.98e-06;
- combined age-adjusted: effect 0.996, 95% CI 0.655 to 1.337,
  P=3.28e-07 and q=1.31e-06;
- adult secondary: effect 0.968, 95% CI -0.123 to 2.060 and q=0.291;
- combined >=20: effect 0.965 and q=6.75e-07; and
- combined >=100: effect 0.939 and q=4.06e-06.

The small adult stratum is imprecise but strongly direction-compatible and shows no
persuasive reversal. It is not presented as an independently significant adult test.

The positive IFN arm contained all 12 frozen genes in childhood and combined models.
All 12 had positive gene-level effects in both analyses. Ranked competitive evidence
was strongly coherent: childhood camera FDR 1.85e-07 and combined FDR 1.59e-07.

## 7. Influence and source-label robustness

All 43 leave-one-donor-out childhood IFN estimates remained positive:

- full effect: 1.042;
- LOO range: 0.987 to 1.094; and
- largest absolute change: 0.055.

No source-label omission weakened the interpretation:

- eight omission effects ranged from 1.019 to 1.051;
- every omission remained four-program significant;
- the smallest effect was well above the predeclared 50% full-effect floor of
  0.521; and
- each analysis retained all 43 childhood donors.

The result is therefore neither a single-donor event nor an artifact of one source
`B-caSC` label.

## 8. Cross-dataset coherence and its boundary

Among the 12 frozen IFN genes, ten passed gene-level expression filtering in both
GSE174188 primary and GSE135779 childhood analyses. All ten were positive in both
datasets. `IFIT1` and `IFIT2` did not pass the GSE174188 gene-level filter but were
available to the frozen program score and were strongly positive in GSE135779.

Across all 4,410 shared tested genes, however, the discovery-to-external Spearman
effect correlation was only 0.026. This low genome-wide correlation is retained as
an explicit scope boundary. The evidence supports replication of a predeclared IFN
module, not broad transcriptome-wide agreement between cohorts.

Within GSE135779, childhood-versus-combined gene effects were highly concordant
(rho=0.945). Childhood-versus-adult concordance was modest (rho=0.140), consistent
with the small adult sample and differing age context.

## 9. Technical and identity controls

In the childhood primary program model:

- IFN/ISG effect: 1.042;
- platelet/ambient control: 0.049, P=0.800;
- ASC/UPR control: 0.221, P=0.0583; and
- pan-B identity control: -0.232, P=0.179.

All three controls were smaller in absolute magnitude than IFN. The top 50 genes
contained 0% mitochondrial, ribosomal, hemoglobin and immunoglobulin features. The
top 500 contained 0.2% mitochondrial and 0% for the other three families.

The near-nominal ASC/UPR control remains a caution but cannot explain the stronger,
gene-coherent and source-label-stable IFN result. Direct PC/ASC disease inference
remains outside the conventional-B confirmatory endpoint.

## 10. Figure and visual quality control

The final four-panel external-validation figure contains:

1. the five GSE135779 IFN forest estimates;
2. GSE174188 discovery/internal and GSE135779 external effect comparison;
3. genome-wide effect context with frozen IFN genes highlighted; and
4. donor and source-label influence estimates.

PNG was exported at 320 dpi and a vector PDF was generated. Full-resolution visual
review checked panel spacing, confidence intervals, text fit, zero lines, legends and
gene labels. The first review exposed crowded IFN labels in panel c; the figure code
was changed to label six representative genes with leader lines and rerun. No result
value was altered.

## 11. Integrity and reproducibility

Added:

- `audit_tools/phase17_c5b_01_export_frozen_matrices.py`;
- `audit_tools/phase17_c5b_02_qualify_edger.R`;
- `audit_tools/phase17_c5b_03_fit_frozen_models.R`;
- `audit_tools/phase17_c5b_04_review_and_figure.py`; and
- `audit_tools/run_6013RP_phase17_gateC5B_external_validation.ps1`.

The integrity manifest contains 69 pre-manifest artifacts: 36 compact tracked files
totaling approximately 0.85 MB and 33 local recomputable matrices, full gene tables
and score objects totaling approximately 31.05 MB. Text outputs are normalized to LF
before manifest hashing so a fresh Git checkout preserves byte-level verification.

The independent reviewer reproduced model sizes, all five full gene tables, tested
gene counts, gene-level BH, four-program BH, donor influence, source-label influence,
ranked IFN coherence and technical-family summaries.

## 12. Limitations

- GSE135779 source labels authorize a broad conventional-B analog, not hard
  naive/memory/atypical identities.
- Adult inference contains only 5 HC and 6 SLE donors.
- Sex, treatment and detailed clinical covariates are absent from the processed
  local metadata.
- Two adult metadata donors lack source matrices.
- Childhood metadata versions are not cell-identical; the extended version remains
  authoritative.
- Independent replication is IFN-program-specific and not genome-wide.
- No perturbational experiment has established a causal upstream mechanism.

## 13. Manuscript consequence and next target

The manuscript may now state that a disease-blind broad conventional-B compartment
shows independently replicated SLE-associated IFN remodeling across GSE174188 and
GSE135779. It may not claim global transcriptomic replication, a hard B-cell subtype,
or a causal regulatory mechanism.

The next target is Gate C6: freeze the central claim and rebuild the manuscript and
main-figure logic around IFN/ISG, while pre-registering a targeted external regulatory
evidence layer. Secondary B-cell axes must be demoted unless they satisfy their own
cross-dataset evidence requirements.
