# Phase 7 runbook: external genetic-regulatory evidence

## Objective

Test whether the manuscript's B-cell state genes are supported by shared SLE GWAS and
B-cell cis-eQTL signals. This phase is confirmatory and must not be used to convert
correlation into mechanism.

## Prespecified primary GWAS

- Accession: GCST90558100
- Trait: systemic lupus erythematosus
- PMID: 40262193
- Population: 6,547 European-ancestry cases and 648,130 European-ancestry controls
- Build: GRCh38 harmonised summary statistics
- Source: NHGRI-EBI GWAS Catalog
- Download:

```powershell
powershell -ExecutionPolicy Bypass -File .\02_analysis\scripts\00_download_sle_gwas_gcst90558100.ps1
```

## Prespecified genes and loci

Primary non-MHC targets:

- ZEB2
- TBX21
- ITGAX
- FCRL5
- FCRL3
- CD74

MHC targets, analysed and interpreted separately because of long-range LD and multiple
independent signals:

- HLA-DRA
- HLA-DRB1
- HLA-DPA1
- HLA-DPB1

The extraction window is each gene boundary plus/minus 1 Mb on GRCh38. No target may be
removed because its result is null.

## eQTL hierarchy

Primary:

1. Fairfax_2012 purified CD19+ B cells, QTD000080, n=281.
2. CEDAR purified CD19+ B cells, QTD000073, n=262.

Biological replication:

3. OneK1K B intermediate, QTD000606, n=977.
4. OneK1K memory B cells, QTD000607, n=981.
5. OneK1K naive B cells, QTD000608, n=980.
6. OneK1K plasmablasts, QTD000623, n=795.
7. Perez lupus PBMC B-cell compartment, QTD000597, n=191.
8. Schmiedel_2018 naive B cells, QTD000474, n=91.

Whole blood, PBMC-wide, LCL and non-B-cell contexts are secondary specificity controls,
not substitutes for primary B-cell evidence.

## Analysis rules

1. Use expression-level cis-eQTL summary statistics and retain all variants available in
   the shared GWAS/eQTL locus.
2. Harmonise by chromosome, position, REF and ALT. In eQTL Catalogue data, ALT is the
   effect allele. Remove irreconcilable allele pairs and duplicated variant records.
3. Require at least 100 shared variants per locus-context pair before colocalisation.
4. Use `coloc.abf` with explicit case-control parameters for SLE and quantitative-trait
   parameters for eQTL. Record priors and rerun prior sensitivity.
5. Primary evidence threshold: PP.H4 >= 0.80, with PP.H4 / (PP.H3 + PP.H4) >= 0.90.
6. Supportive evidence: 0.50 <= PP.H4 < 0.80, reported as suggestive only.
7. Treat PP.H3 dominance as distinct causal signals, not a negative expression result.
8. Do not apply frequentist FDR correction to Bayesian posterior probabilities. Report
   every prespecified gene-context pair, the complete posterior vector and prior
   sensitivity; require cross-dataset replication for a promoted claim.
9. For the MHC, do not claim gene-level colocalisation from an unconditional single-signal
   model. Conditional or fine-mapped signals are required.
10. A null result remains a result and sets the boundary of the manuscript's mechanistic
    interpretation.

## Stop/go decision

- Go to an upper-Q1 regulatory-convergence claim only if at least one non-MHC manuscript
  gene has robust colocalisation in a primary purified B-cell dataset and independent
  support in another B-cell context.
- If this criterion is not met, retain the current observational multi-cohort paper,
  report the null boundary if scientifically useful, and target the best-fit genomics or
  autoimmunity journal without implying causal regulation.

## Completed outcome: 2026-07-27

- GCST90558100 failed the prespecified overlap criterion and contained no variants in
  chr6:30-35 Mb.
- GCST005831 provided adequate FCRL3/FCRL5 overlap after exact GRCh38 allele alignment.
- Nineteen molecular-trait tests had 2,339-2,635 shared variants.
- Maximum PP.H4 was 0.0542 at p12=1e-5 and 0.364 at p12=1e-4.
- No test met the strong-colocalisation threshold.
- The go criterion was not met. The regulatory analysis is retained as an internal
  boundary audit and is not promoted into the manuscript.

## Provenance

- GWAS Catalog summary-statistics documentation:
  https://www.ebi.ac.uk/gwas/docs/methods/summary-statistics
- eQTL Catalogue data access and allele convention:
  https://www.ebi.ac.uk/eqtl/Data_access/
- eQTL Catalogue study inventory:
  https://www.ebi.ac.uk/eqtl/Studies/
- eQTL Catalogue API tutorial:
  https://github.com/eQTL-Catalogue/eQTL-Catalogue-resources/blob/master/tutorials/API_v2/eQTL_API_tutorial.md
