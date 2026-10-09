# O01 Project Audit — SLE B-cell remodeling

**Date:** 2026-09-29
**Framework:** QiTeng Academic Writing Skill v0.3.24.2, `QITENG_Q1_GUARDED` + `QITENG_FIGURE_Q1_GUARDED` + `SUBMISSION_GATE_MODE` + hard-negative audit.
**Target journal used as direction:** npj Systems Biology and Applications.
**Baseline:** completed `SLE_Bcell_Submission_Package.zip`; original package preserved and not overwritten.

## Scientific purpose

The manuscript does **not** aim to rediscover that interferon biology exists in SLE or to establish a new B-cell taxonomy. Its contribution is an evidence hierarchy showing that reproducibility differs across biological layers. A prespecified process-level B_CONV IFN/ISG program is reproducible across discovery, internal robustness analyses and source-label-defined external analysis, whereas hard state assignment, source-label-independent transfer and mechanistic attribution retain explicit limits.

## Current evidence architecture

`identity ceiling -> composition boundary -> process-level IFN/ISG discovery -> source-label-defined external replication -> weak genome-wide concordance -> transfer ceiling -> observational regulatory convergence -> mechanistic ceiling`

The architecture is mature and internally coherent. The correct late-stage strategy is guarded refinement, not global rewriting or new exploratory analysis.

## Fixable defects identified and repaired this round

1. Reader-facing definitions for UMI, TMM, ULM and M5911 were incomplete or delayed.
2. Several instances of project-internal wording (`frozen program`, `post-freeze`) could be made reader-facing without changing design semantics.
3. The source-label-independent calibration paragraph had an awkward closing sentence that could be misread as stronger external transfer.
4. The overlap-depletion timing and multiplicity family needed a transparent human-facing description rather than project-stage jargon.
5. Figure 4/5 legends could be compressed by removing duplicated explanation while retaining each panel's evidence owner and boundary.
6. Cover-letter significance was under-focused: it described contents more than the central reproducibility hierarchy.
7. AI-assistance wording needed explicit synchronization across manuscript, cover letter, author declarations and reporting information.
8. Human-facing package metadata needed a current journal-policy recheck date and refreshed hashes/provenance after revision.

## Non-fixable evidence limits that must remain visible

- B_ASC end-to-end overlap criterion failure: cannot be repaired by relabelling or cosmetic replotting.
- Primary B_ASC composition contrast lacks statistical support; this is not an equivalence result.
- Genome-wide cross-dataset effect correlation is weak despite program-specific IFN concordance.
- Corrected source-label-independent elastic-net mapping does not meet the B_ASC precision threshold, so no corrected external disease effect is estimated.
- Regulatory evidence is observational; overlap-depletion exposes partial coupling to the broader interferon-response transcriptome.
- External adult stratum is small; GSE23307 has only two healthy donors.
- Public metadata do not provide a harmonized full set of sex, treatment and detailed clinical covariates.
- No prospective clinical utility, treatment-selection rule, direct binding or causal regulator is established.

## Analysis rerun judgment

No statistical rerun is scientifically justified in this round. The manuscript already preserves the negative and limiting results that would otherwise motivate robustness work. Rerunning solely to obtain stronger significance, tune the mapper after seeing outcomes, add decorative pathway/network analyses or rescue B_ASC would create post-hoc risk rather than improve evidence quality.

## Artifact status after this round

- Manuscript DOCX/PDF refined; final render returned to **31 pages** without shrinking typography.
- Cover Letter, Authors and Declarations, Reporting Information and README synchronized.
- Figures 1-5 and Supplementary Information remain byte-identical to the baseline package.
- Main manuscript, cover letter and declarations accessibility audits: **0 high / 0 medium / 0 low**.
- All package PDFs pass preflight with no warnings/errors.
- Current package hash manifest rebuilt and local verifier passes all payloads.

## Project-audit conclusion

`PASS_LATE_STAGE_GUARDED_REFINEMENT`

The scientific structure should remain closed. Further work should be limited to source-level reader-facing figure terminology and one final hard-negative/cross-document consistency gate.
