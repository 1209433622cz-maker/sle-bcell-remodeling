# Gate C8S full statistical results

This reviewer-facing archive contains complete result tables supporting the frozen manuscript, not raw sequencing data. GSE174188 is the discovery and internal donor-nonoverlap resource; the latter is not an independent dataset. GSE135779 is the independent childhood validation dataset. GSE23307 contains two paired donors after IFNB1 stimulation and is descriptive only.

## Contents

- `gene_level_results/`: all filterByExpr-tested gene results for seven GSE174188 and five GSE135779 model branches.
- `composition/`: frozen beta-binomial composition estimates, predictions, sensitivities, leave-one-out results and diagnostics.
- `transcription/`: model summaries, four-program tests, ranked-list coherence, influence diagnostics and cross-dataset concordance.
- `regulatory_and_orthogonal/`: global-24 regulator results, target influence/resampling, CAMERA/FRY sensitivity, M5911 enrichment and two-donor perturbation summaries.
- `sanitized_design_matrices/`: the 12 analysis design tables with direct sample, donor and UUID fields removed. `analysis_sample_index` is local to each table and cannot be joined to source identities.
- `statistical_framework/`: the prespecified testing, sidedness and multiplicity map.

BH q values are family-specific as documented in `STATISTICAL_TEST_AND_MULTIPLICITY_MAP.csv`; they must not be compared as if they came from one universal family. Unless explicitly labelled directional, reported tests are two-sided and confidence intervals are 95%. No prospective power calculation was performed because this is a retrospective secondary analysis of public datasets; available biological units after frozen eligibility rules determined each analysis size.

Raw H5AD, FASTQ and full count matrices are intentionally excluded from this attachment. Public source accessions and reproducibility instructions are provided in the manuscript and repository. File-level provenance and SHA-256 values are recorded in `SOURCE_PROVENANCE.csv` and `MANIFEST_SHA256.csv`.
