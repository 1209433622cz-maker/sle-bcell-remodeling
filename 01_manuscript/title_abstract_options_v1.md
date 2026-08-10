# Title And Abstract Options v1

## Working Title Options

1. Donor-aware single-cell analysis identifies an expanded ABC/APC-like B-cell state in systemic lupus erythematosus
2. An atypical ABC/APC-like B-cell state defines donor-level B-cell remodeling in systemic lupus erythematosus
3. Single-cell B-lineage remodeling in systemic lupus erythematosus prioritizes an ABC/APC-like pathogenic candidate state
4. Donor-level B-cell state analysis reveals ABC/DN2 and antigen-presentation programs in systemic lupus erythematosus
5. A public single-cell atlas nominates an expanded antigen-presenting ABC-like B-cell state in systemic lupus erythematosus

## Recommended Current Title

Donor-aware single-cell analysis identifies an expanded ABC/APC-like B-cell state in systemic lupus erythematosus

Rationale: this title captures the strongest current evidence without overclaiming causality, mechanism, or multi-omic validation that has not yet been completed.

## Structured Abstract Draft

**Background:** B-cell dysregulation is central to systemic lupus erythematosus (SLE), but the donor-level disease-associated B-cell states captured in large public single-cell datasets remain incompletely resolved.

**Objective:** To define disease-associated B-lineage cell states in SLE and prioritize candidate pathogenic B-cell programs using a donor-aware single-cell analysis framework.

**Methods:** We analyzed the public Perez/GSE174188 CELLxGENE H5AD object containing 1,263,676 immune cells from 261 donors. B-lineage cells were selected using standardized cell-type annotations, yielding 152,981 B-lineage cells from 259 donors. Because the CELLxGENE `X` matrix was preprocessed/scaled, state mapping used available low-dimensional representations, while marker refinement and donor-state expression summaries used count-like `adata.raw.X`. Refined B-cell states were assessed using raw-count marker programs, donor-level abundance tests, sensitivity analysis excluding a platelet/ambient-RNA-high cluster, and donor-state pseudobulk program analysis.

**Results:** SLE was associated with expansion of an activated naive-like B-cell state and an atypical ABC/APC-like B-cell state, together with reduction or redistribution of a memory-like B-cell state. The ABC/APC-like state was expanded in SLE donors compared with normal donors and remained significant after excluding the flagged platelet/ambient-RNA-high cluster. Donor-state pseudobulk analysis showed that this state carried ABC ranked, ABC/DN2, and APC/HLA programs, with additional modest IFN-response enrichment. Plasmablasts were transcriptionally well defined but were not the dominant donor-level abundance signal in this cohort.

**Conclusions:** This donor-aware analysis supports a model in which SLE B-cell remodeling is anchored by expansion of an atypical ABC/APC-like state with antigen-presentation and ABC/DN2-associated programs. These findings nominate the ABC/APC-like state as a candidate pathogenic B-cell population for further validation.

## Short Abstract Draft

We analyzed a public single-cell immune atlas of SLE to define donor-level B-cell state remodeling. From 1,263,676 immune cells, we extracted 152,981 B-lineage cells across 259 donors and refined B-cell states using public metadata, raw-count marker summaries, donor-level abundance testing, and donor-state pseudobulk program analysis. SLE was associated with expansion of an activated naive-like B-cell state and an atypical ABC/APC-like B-cell state, as well as reduction or redistribution of a memory-like state. The ABC/APC-like state remained significantly expanded after excluding a platelet/ambient-RNA-high QC cluster and showed donor-aware enrichment of ABC/DN2 and APC/HLA programs. These results nominate an expanded antigen-presenting ABC-like B-cell state as a central candidate population in SLE B-cell remodeling.

## Positioning Notes For Q1/Q2 Submission

- Emphasize donor-aware analysis rather than single-cell-level p values.
- Lead with the ABC/APC-like state and use activated naive-like remodeling as a second major result.
- Keep plasmablasts as a well-identified endpoint but not the central disease signal.
- Preserve the flagged-cluster QC story because it strengthens credibility.
- Avoid causal language unless additional validation or perturbation evidence is added.
