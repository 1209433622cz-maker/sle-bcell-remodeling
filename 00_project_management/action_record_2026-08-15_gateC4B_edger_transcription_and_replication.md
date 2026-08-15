# Action record: Gate C4B frozen B_CONV transcription and internal replication

Date: 2026-08-15
Project: 6013RP-wyf / Phase 17 v7
Gate: C4B
Final decision: `PASS_GATE_C4B_TO_INDEPENDENT_SLE_VALIDATION`

## 1. Objective and governance

This round tested whether disease-associated transcription within the disease-blind
`B_CONV` compartment could support a central manuscript result. The analysis was
constrained by the Gate C4A pre-effect freeze. No B-cell subtype was redefined, no
sample was added after effect inspection, no program gene was changed, and B_ASC
gene-level disease inference remained prohibited.

The workflow enforced two sequential locks:

1. qualify the statistical software and matrix import without fitting any real
   disease coefficient; and
2. unlock the seven frozen real-effect analyses only after all qualification checks
   passed.

## 2. Frozen input and matrix exports

The source was the Gate C4A all-branch pseudobulk count matrix:

- path: `phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/02_pseudobulk_counts_all_branches.npz`;
- SHA256: `28DF02DD8C46232000F5492B3A6B026AD2D94DC1C77319B2925C5AA770DE4B11`;
- source C4A integrity manifest: fully reverified before export;
- gene universe: 30,172 frozen Ensembl features; and
- count policy: non-negative integer raw pseudobulk counts only.

Seven genes-by-samples Matrix Market objects were exported:

| Analysis | Branch | Samples | Reference | Exposed | Total UMI | Design rank |
|---|---|---:|---:|---:|---:|---:|
| Primary C4, >=50 cells | all hard QC | 89 | 43 | 46 | 59,873,385 | 4/4 |
| Primary C4, >=20 cells | all hard QC | 94 | 44 | 50 | 60,143,685 | 4/4 |
| Primary C4, >=100 cells | all hard QC | 87 | 41 | 46 | 59,493,597 | 4/4 |
| Primary C4, residual-risk negative | sensitivity branch | 89 | 43 | 46 | 58,989,619 | 4/4 |
| Validation C2, full | all hard QC | 64 | 21 | 43 | 56,214,928 | 3/3 |
| Validation C2, donor nonoverlap | all hard QC | 54 | 21 | 33 | 46,156,989 | 3/3 |
| Secondary flare C3 | all hard QC | 34 | 18 | 16 | 35,877,776 | 4/4 |

For every export, Python independently computed column and gene sums. R then
reimported the compressed sparse matrix and reproduced both sets of sums exactly.

## 3. Statistical-engine qualification

The machine already contained R but it was not on `PATH`. The workflow now locates
`Rscript.exe` directly and records:

- R 4.6.0;
- Bioconductor 3.23;
- edgeR 4.10.1;
- limma 3.68.4;
- Matrix 1.7.5;
- statmod 1.5.2; and
- jsonlite 2.0.0.

The qualification suite imported the real primary matrix only for dimensions and
count conservation. It did not fit a real disease coefficient. Synthetic negative-
binomial tests then produced:

| Qualification metric | Observed | Acceptance | Result |
|---|---:|---:|---:|
| Null P < 0.05 fraction | 0.0553 | <=0.0800 | PASS |
| Null median log2FC | 0.0011 | absolute value <=0.10 | PASS |
| Signal median recovered log2FC | 1.1967 | >=0.80 | PASS |
| Signal sign concordance | 1.0000 | >=0.95 | PASS |
| Signal BH sensitivity | 1.0000 | >=0.80 | PASS |
| Signal empirical FDR | 0.0654 | <=0.10 | PASS |

All ten qualification checks passed before the real-effect stage was unlocked.

## 4. Frozen models

Gene-level analysis used edgeR TMM normalization, `filterByExpr`, robust dispersion
estimation and robust quasi-likelihood testing. BH adjustment was performed across
all tested genes within each contrast. Every full result table retains all 30,172
features and explicitly flags genes not passing `filterByExpr`.

Program scores followed the C4A formula exactly: raw counts with duplicate symbols
summed before normalization, TMM logCPM, within-contrast gene z scores, positive-arm
mean minus negative-arm mean, and HC3 sandwich uncertainty. Multiplicity was frozen
as BH across the four confirmatory programs.

| Analysis | Tested genes | FDR <0.05 | Up | Down |
|---|---:|---:|---:|---:|
| Primary C4 | 4,414 | 282 | 158 | 124 |
| Primary >=20 | 4,098 | 252 | 126 | 126 |
| Primary >=100 | 4,524 | 260 | 139 | 121 |
| Primary residual-risk negative | 4,432 | 289 | 155 | 134 |
| Validation full | 6,099 | 157 | 134 | 23 |
| Validation nonoverlap | 6,077 | 189 | 156 | 33 |
| Flare secondary | 7,761 | 289 | 177 | 112 |

## 5. Confirmatory program findings

| Program | Primary effect | 95% CI | Primary BH q | Full validation effect / q | Nonoverlap effect / q |
|---|---:|---:|---:|---:|---:|
| Naive-to-memory | -0.541 | -0.978 to -0.103 | 0.0213 | -0.581 / 0.167 | -0.443 / 0.415 |
| Atypical/low-naive | -0.057 | -0.407 to 0.294 | 0.748 | -0.120 / 0.739 | 0.184 / 0.655 |
| APC/HLA | 0.268 | 0.052 to 0.483 | 0.0213 | 0.361 / 0.167 | 0.340 / 0.415 |
| IFN/ISG | 0.837 | 0.525 to 1.148 | 2.98e-06 | 0.856 / 0.00462 | 1.086 / 0.000361 |

The IFN/ISG program is the only result promoted to the central external-validation
anchor. It is multiplicity-supported in primary, full internal validation and
donor-nonoverlap validation. Its effect is positive at both cell thresholds and in
the residual-risk-negative branch. The secondary flare contrast is also positive
(`effect=1.368`, `q=5.47e-04`) but does not replace the managed-state primary test.

Naive-to-memory and APC/HLA satisfy the predeclared primary, direction, sensitivity,
LOO and ranked-arm coherence checks. However, their internal validation confidence
intervals cross zero and their validation BH q values are not significant. They are
supporting axes only. The atypical/low-naive program failed.

## 6. Gene, pathway and influence coherence

The leading primary genes were dominated by coherent interferon-response genes,
including `USP18`, `IFI44L`, `EPSTI1`, `IFIT3`, `MX1`, `IFI6`, `OAS2`, `ISG15` and
`STAT1`. The frozen IFN positive arm showed 10/10 tested genes in the expected
direction and competitive ranked enrichment FDR of approximately `2e-06`.

Across 4,398 genes tested in both primary and nonoverlap validation:

- Spearman effect correlation: 0.162 (bootstrap 95% CI 0.132 to 0.191); and
- direction concordance among the 500 leading primary genes: 0.690 (95% CI 0.647
  to 0.730).

The genome-wide correlation is modest and is reported as such. The central argument
rests on the frozen IFN program and coherent genes, not a claim of globally identical
cohort effects.

All 89 leave-one-sample-out IFN program estimates remained positive. The full effect
was 0.837, the LOO range was 0.793 to 0.874, and the largest absolute change was
0.043. Confirmatory-gene LOO diagnostics likewise showed stable IFN members.

## 7. Technical and identity controls

- Platelet/ambient program: effect 0.015, p=0.880.
- ASC/UPR identity program: effect -0.036, p=0.651.
- Top-50 primary genes: 0% mitochondrial, ribosomal, hemoglobin and immunoglobulin.
- Top-500 primary genes: mitochondrial 0.4%, ribosomal 7.8%, hemoglobin 0%,
  immunoglobulin 0%.
- Therefore immunoglobulin exclusion does not alter the leading ranked summary or
  the frozen program analyses.

The pan-B identity control was positive (`effect=0.409`, `p=0.00624`). This is an
explicit external-validation sensitivity flag. It does not explain away the stronger
IFN effect, because platelet/ASC controls are null and the leading genes are specific
ISGs, but it prevents an unqualified claim that all transcriptional differences are
state-specific rather than partly reflecting B-lineage identity or composition.

## 8. Integrity audit and incident log

Independent Python review reloaded every output and reproduced:

- seven of seven complete 30,172-row gene tables;
- unique Ensembl keys in every table;
- tested-gene counts in all model summaries;
- gene-level BH values exactly; and
- all 63 program rows and the four-program BH values exactly.

The output manifest contains 50 audited artifacts plus the manifest itself. Tracked
outputs account for 27 files and about 1.04 MB. Twenty-three compressed matrices,
gene sums, full gene tables and score tables are local recomputable outputs totaling
about 22.47 MB.

One implementation defect was detected and repaired by full rerun: the UTF-8 BOM in
the frozen C4A program dictionary caused R to misread the first column, producing
empty program/LOO/pathway tables. The gene-level edgeR results were unaffected, but
no partial result was accepted. The script was changed to use explicit `UTF-8-BOM`
decoding and strict required-column checks, QC booleans were normalized explicitly,
and all seven models and review outputs were regenerated. The final run emitted no
model warnings.

## 9. Reproducibility assets

Added scripts:

- `audit_tools/phase17_c4b_00_install_packages.R`;
- `audit_tools/phase17_c4b_01_export_frozen_matrices.py`;
- `audit_tools/phase17_c4b_02_qualify_edger.R`;
- `audit_tools/phase17_c4b_03_fit_frozen_models.R`;
- `audit_tools/phase17_c4b_04_review_and_figure.py`;
- `audit_tools/run_6013RP_phase17_gateC4B_prepare_edger.ps1`; and
- `audit_tools/run_6013RP_phase17_gateC4B_transcription.ps1`.

The total launcher was executed end to end against the final run directory and
completed all four stages. Windows `C.UTF-8` environment variables are temporarily
removed only for child R processes and are restored in `finally` blocks.

## 10. Manuscript consequence

The results justify a focused B_CONV interferon transcription claim and a move to
independent validation. They do not yet justify an upper-Q1 mechanistic framing.
Cohort 2 remains internal to GSE174188, managed-state treatment and clinical
confounding remain possible, and no regulatory mechanism has been established.

The next stage is Gate C5 independent SLE validation. GSE135779 must be rerun from
source with the exact frozen C4A/C4B program definitions and donor-level inference.
Existing older GSE135779 outputs are feasibility evidence only because they predate
this freeze and use a different 10-gene IFN score.
