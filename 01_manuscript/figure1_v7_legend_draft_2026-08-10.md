# Figure 1 | Outcome-locked study design, experimental hierarchy and prespecified inference strata

**a,** Outcome-locked analysis workflow for the v7 study. Raw B-cell counts were audited before hard quality control (QC), disease and outcome fields were kept physically separate during representation learning and state definition, and disease associations were evaluated only after the state model had been frozen. Composition was assessed at the biological-sample level, whereas transcriptional remodeling was tested using within-state raw-count pseudobulks. External validation was prespecified as frozen mapping to GSE135779 rather than de novo relabeling. Cell totals denote the audited input (152,981 cells) and the hard-QC-eligible analysis object (150,402 cells); doublet scoring is pending and these totals are therefore not final retained-cell counts.

**b,** Biological and technical hierarchy of the discovery resource. The dataset contains 259 donors, 271 biological samples, 1,373 sample-library records and 88 technical libraries. Eleven donors have repeated biological samples, and 53 biological samples bridge processing cohorts. The biological sample is the primary compositional unit; library is a technical unit and is not treated as an independent biological replicate.

**c,** Apparent technical common support compared with the strict biological subset used to define inferential roles. Left, unique sample-cohort records observed within each processing-cohort and disease stratum (normal/SLE: cohort 1, 47/0; cohort 2, 22/118; cohort 3, 18/32; cohort 4, 44/51). Right, counts among donors represented by exactly one biological sample and one processing cohort (n = 195; normal/SLE: cohort 1, 28/0; cohort 2, 1/87; cohort 3, 5/8; cohort 4, 41/25). Bubble area is proportional to the displayed count. The 53 cohort-bridging samples support technical diagnostics but do not create independent disease support.

**d,** Percentage of cells excluded by prespecified hard QC in each observed processing-cohort and disease stratum. The axis starts at zero so small differences are not visually exaggerated. Values are descriptive cell-level summaries and are not inferential replicates. Cohort 1 contains no SLE stratum. Doublet calls were not included because full per-library residual doublet-risk scoring had not yet passed its freeze gate.

**e,** Prespecified inferential roles derived from strict biological support. Cohorts 1 and 2 are discovery-only strata because they lack meaningful within-cohort disease overlap; cohort 3 is exploratory; and cohort 4 is the primary within-cohort disease-comparison stratum. Bridge samples are reserved for technical diagnostics. Any combined estimate must retain cohort structure and biological-sample-level uncertainty.

Normal, unaffected control; SLE, systemic lupus erythematosus; QC, quality control.

## Source freeze

- Hierarchy and common-support source: `phase17_v7/gateC1/20260806_134213_hotfix_v1_1/`
- Binding strict-support source: `15_strict_common_support_reaudit.csv` and `16_STRICT_COMMON_SUPPORT_ERRATUM.md`
- Hard-QC source: `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/`
- Figure source script: `02_analysis/scripts/50_make_v7_figure1_study_design.py`
- Current status: design/QC figure; not manuscript-frozen until Gate C2B1 doublet review is complete.
