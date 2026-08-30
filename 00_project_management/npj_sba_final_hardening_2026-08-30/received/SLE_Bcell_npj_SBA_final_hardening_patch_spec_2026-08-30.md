# npj SBA final hardening patch specification

Date: 2026-08-30  
Repository: `1209433622cz-maker/sle-bcell-remodeling`  
Observed head: `0c7361022510b47e8cc7ae82baafd4b6dcff7c8e`

This document is a patch specification only. No GitHub mutation was performed in this review.

## 1. Fix `audit_tools/publication_style_contract.py`

Current defect in `apply_npj_sba_style()`:

- the first half correctly sets text to 8 pt and raises positive line widths to >=1 pt;
- the second half then reapplies the generic 5-7 pt / 0.25-1.0 pt clamp;
- exported artifacts therefore do not fully satisfy the declared npj line-width contract.

Required source fix:

1. Keep the npj branch independent from the generic branch.
2. After setting Arial, target 8 pt typography and `>=1.0 pt` positive line widths, return/end the function.
3. Do not execute the generic clamp inside `apply_npj_sba_style()`.

## 2. Add artifact-level figure tests

Do not validate only Matplotlib objects or status JSON.

After PDF export, parse each PDF and assert:

- page count = 1;
- width = target width within tolerance;
- visible fonts are Arial/Helvetica-compatible;
- visible text size matches the frozen npj contract;
- every positive vector drawing width is >=1 pt under the journal-specific contract;
- no clipping;
- no red-green-only semantic contrast;
- source CSV SHA is unchanged.

Current exported main-figure audit:

- Figure 1: min vector width = 0.60 pt; fonts 7-8 pt;
- Figure 2: min vector width = 1.00 pt; fonts 7-8 pt;
- Figure 3: min vector width = 1.00 pt; fonts 7-8 pt;
- Figure 4: min vector width = 1.00 pt; fonts 7-8 pt;
- Figure 5: min vector width = 0.90 pt; fonts 7-8 pt.

## 3. Fix `npj_statistics_reporting_map.csv` at the builder level

Correct human-readable claims:

- `R1`: `End-to-end broad-state reproducibility did not meet the frozen state-specific criterion because B_ASC median Jaccard was below 0.95.`
- `C3_PRIMARY`: `The primary B_ASC composition analysis did not support a difference in source-defined managed SLE.`
- `C5_GENOMEWIDE`: `Genome-wide cross-dataset effect concordance was weak (Spearman rho=0.026).`
- `C9R`: `Corrected source-label-independent mapping did not satisfy the frozen calibration gate; no corrected disease outcome was estimated.`
- `TF_DEPLETION`: `Narrow 12-gene depletion retained support, whereas broader M5911 depletion did not support overlap-independent STAT1/STAT2 regulation.`

Add exact regression assertions for these rows.

## 4. Reader-facing manuscript synchronisation

Use the QiTeng-hardened candidate as the prose target.

Key changes:

- avoid the self-deprecating phrase `neither ... is novel`;
- Introduction should end on the evidence-hierarchy research task;
- GSE135779 replication should be consistently labelled `source-label-defined` where the ownership of the external identity scope matters;
- collapse the duplicate end-of-Discussion / old-Conclusion residue into one landing paragraph;
- retain R1 and C9R as evidence boundaries, not as internal gate jargon in reader-facing prose.

## 5. Figure semantics during rerender

- Figure 2 panel label: `No primary B_ASC enrichment` -> `Primary B_ASC enrichment not supported`.
- Figure 1 external node: use `GSE135779 source-label-defined replication`.
- Figure 4 title/panel label: make source-label-defined scope explicit.
- Preserve all numeric values and source-data hashes.

## 6. Repository documentation

Update current `README.md` and `REPRODUCIBILITY.md` to state:

- target journal is npj Systems Biology and Applications;
- target-specific package has been built;
- current stage is final render/semantic hardening before exact-file approval;
- Zenodo `10.5281/zenodo.22151739` and GitHub `v1.1.0` remain the frozen scientific reproducibility release;
- no new scientific analysis has been performed;
- current target documents have WPS/LibreOffice cross-render QA where applicable;
- official JCR-Q1 and CUHK-Shenzhen APC/OA receipts remain pending.

Do not move the v1.1.0 tag and do not alter the Zenodo release for this formatting-only hardening.
