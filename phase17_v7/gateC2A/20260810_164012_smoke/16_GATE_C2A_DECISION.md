# Gate C2A post-hoc decision

**Run:** `H:\cuhk-2025fALL\6013RP-wyf\phase17_v7\gateC2A\20260810_164012_smoke`  
**Review date:** 2026-08-10T17:02:38+08:00  
**Representation:** GO to full Gate C2B  
**Smoke doublet calls:** NO-GO for freezing  
**Cluster labels:** provisional, disease-blind annotation still required  
**Submission:** NO-GO

## Evidence

- The embedding retained 16,996 cells after provisional smoke doublet exclusion.
- Harmony reduced the mean same-group neighbor fraction for every audited technical field: Processing_Cohort 0.665 to 0.432, library_uuid 0.067 to 0.015, sample_uuid 0.044 to 0.017.
- At resolution 0.6, all clusters contained at least 227 cells, 97 donors and 72 libraries; the largest single-library contribution was 4.4%.
- Adjacent-resolution ARI ranged from 0.251 to 0.674; this supports continuity assessment but does not freeze a final resolution.
- Scrublet predicted a median 14.8% and maximum 43.7% doublets per successful library; 17 libraries exceeded 20%. These rates are not accepted because smoke sampling occurred before per-library doublet modeling.
- Protected outcome labels were merged only after representation and marker review. Cell-level disease proportions are saved for diagnostic balance checks and must not be used as inferential replicates.

## Binding actions for Gate C2B

1. Run Scrublet on every complete eligible library before any balancing or subsampling.
2. Save scores, automatic thresholds and diagnostic distributions; do not silently cap rates or overwrite calls.
3. Carry all hard-QC cells plus a high-confidence singlet sensitivity branch until doublet diagnostics are approved.
4. Rebuild raw-count HVGs, PCA, unintegrated and Harmony graphs on the full data.
5. Freeze neutral B-cell states using markers, donor/sample coverage and resampling stability before outcome labels are unlocked.
6. Use sample-level composition and sample-by-state pseudobulk as the inferential units, with donor clustering for repeated samples and within-cohort effects where common support exists.
