# Next-stage decision: Gate C4 continuous programs and true pseudobulk

## Advisor decision

Gate C3A is complete. The managed-state ASC composition effect is unsupported and
is prohibited as a central manuscript claim. Gate C4 is authorized because the
two-compartment identity freeze remains valid and continuous program analysis was
explicitly authorized by Gate C2B4 and Gate C3A.

Gate C4 must seek state-internal transcriptional evidence, not relabel the weak
composition result.

## Critical input finding

The 150,402-cell representation H5AD contains embeddings, graph structures,
metadata and 3,000 gene annotations, but intentionally has no `X`, layers or raw
matrix. It cannot support pseudobulk expression.

The 1,263,676-cell CELLxGENE source H5AD contains:

- scaled values in `.X`, including negative values, which are prohibited for
  pseudobulk count models; and
- 30,172-gene integer counts in `.raw.X`, verified on the first 1,000,000 nonzero
  entries (range 1-590; zero fractional values).

Gate C4 must therefore extract `.raw.X` by exact cell ID. `source_cell_index` is not
a valid source-row position and remains prohibited for this purpose.

## Gate C4A: pre-effect extraction and design freeze

Before any disease coefficient is calculated:

1. Reverify the Gate C3A and Gate C3 integrity manifests.
2. Match all 150,402 selected cell IDs uniquely to source `.obs_names`.
3. Read source `.raw.X` in bounded chunks and retain all 30,172 Ensembl features.
4. Aggregate integer counts by `sample_uuid x Processing_Cohort` within frozen
   `B_CONV` cells (source r0.4 clusters 0, 1, 2 and 4).
5. Build a separate B_ASC support audit; do not promise B_ASC pseudobulk because
   many strata contain very few ASC cells.
6. Verify count conservation, non-negativity, integer values, unique feature IDs,
   sample metadata invariants and full-rank model designs.
7. Freeze all model matrices, gene filters and program dictionaries before viewing
   disease effects.

The extraction script must checkpoint chunks because source `.raw.X` contains more
than one billion nonzero values. This is an appropriate local-compute task.

## Disease-blind program freeze

Continuous programs must be frozen from prior disease-blind markers and external
biological knowledge, not selected by Gate C4 disease P values. At minimum audit:

- naive-to-memory axis within `B_CONV`;
- atypical/activation program;
- interferon-response program;
- antigen-presentation program;
- B-cell activation/stress program; and
- platelet-associated overlay as a sensitivity/QC program only.

ASC/UPR markers (`DERL3`, `JCHAIN`, `MZB1`, `TNFRSF17`, `XBP1`) remain an identity
QC panel and may support the secondary flare interpretation. They must not be used
to create a new outcome-informed hard state.

Exact gene membership, score direction, missing-gene policy and multiplicity family
must be recorded in a JSON/Markdown contract before effects are inspected.

## Frozen cohort logic

Retain the Gate C3 cohort logic unless a pre-effect B_CONV cell-count support audit
fails:

- primary: cohort 4, managed versus normal, age and ethnicity adjusted;
- internal directional validation: cohort 2 European-American females, age
  adjusted, plus exclusion of primary-overlapping samples/donors; and
- secondary: cohort 3 flare versus normal, age and ethnicity adjusted.

No global cross-cohort disease model is authorized because processing cohort and
disease state lack common support.

## Gene-level pseudobulk contract

Use a validated negative-binomial pseudobulk engine with library-size normalization
and empirical-Bayes dispersion moderation. The preferred implementation is edgeR
TMM plus robust quasi-likelihood; a validated DESeq2-equivalent implementation is
acceptable only if concordance checks are documented.

Required rules:

- inferential unit is the sample-cohort pseudobulk, never the cell;
- raw integer counts only;
- pre-effect expression filter, such as `filterByExpr`, frozen per contrast;
- exact frozen design covariates and contrasts;
- genome-wide BH FDR within each contrast;
- effect sizes and confidence intervals before significance labels;
- immunoglobulin, mitochondrial, ribosomal, hemoglobin and stress families flagged
  explicitly, with non-immunoglobulin sensitivity where relevant; and
- pathway/program evidence based on ranked statistics, not only significant-gene
  lists.

R and edgeR are not currently installed, and neither `pydeseq2` nor `diffxpy` is
present in the Python environment. Gate C4A extraction and design can proceed in
Python, but gene-level differential expression must wait for a reproducible
pseudobulk environment rather than substituting an ad hoc cell-level test.

## Acceptance criteria

A transcriptional result may enter the main manuscript only when all applicable
criteria pass:

- exact raw-count extraction and count-conservation QC;
- full-rank frozen sample-level design;
- primary cohort-4 program or gene-set support after its frozen multiplicity rule;
- concordant direction in cohort 2, including the nonoverlap sensitivity;
- robustness to cell-count threshold and QC-family handling;
- no single sample dominates the effect; and
- biological coherence across gene-level, program and pathway summaries.

The flare signal remains secondary even if cohort-3 transcription is coherent. It
can be promoted only after independent disease-cohort replication.

## Planned outputs

- raw-count extraction and conservation audit;
- sample-cohort B_CONV pseudobulk count matrix and metadata;
- B_ASC pseudobulk support/no-go audit;
- frozen program dictionary and model-design contract;
- cohort-specific gene-level effect tables and diagnostics;
- program/pathway forest and effect-size heatmap;
- internal nonoverlap replication table;
- Nature-style main/supplementary candidate figures; and
- Gate C4 advisor decision plus SHA-256 manifest.

## Publication position after Gate C3A

The earlier composition-plus-transcription framing is no longer supported. The
defensible working narrative is now:

**Cohort-resolved analysis finds limited managed-state B-cell compartment change
but tests whether SLE activity is encoded in continuous conventional-B-cell
transcriptional programs.**

An upper-Q1 target remains possible only if Gate C4 produces a coherent replicated
program and the result transfers to an independent SLE dataset. Otherwise the
realistic positioning should be a rigorous methods-aware negative/secondary
composition study with narrower biological claims.

## Immediate next action

Implement Gate C4A only: chunked exact-cell-ID extraction from source `.raw.X`,
program-dictionary freeze, B_CONV/B_ASC support audit and pre-effect model-design
contract. Do not inspect any Gate C4 disease coefficient until that contract and
its integrity manifest pass.
