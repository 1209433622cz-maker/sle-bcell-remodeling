# Next-stage decision after Gate C8R

**Decision date:** 20 August 2026

**Current gate:** C8R scientific, figure and reproducibility repair

**Decision:** PASS C8R and advance to Gate C8B author-controlled completion

## Advisor judgment

The project has moved beyond the stage at which another exploratory analysis is
the main rate-limiting step. The strongest defensible paper is now a carefully
bounded human single-cell methods-and-disease study: disease-blind identity
reconstruction prevents overinterpretation of unstable fine states, sample- or
donor-level inference rejects primary B_ASC expansion, and a within-B_CONV
IFN/ISG program survives internal donor non-overlap, independent cohort
validation and orthogonal regulatory/response evidence.

This is a coherent submission narrative. Additional unplanned computational
screens would now create more multiplicity and claim drift than value unless a
reviewer asks a specific question. The next gate should therefore preserve the
frozen numerical result and complete the author-controlled submission facts.

## Target strategy

**Primary route: Genome Medicine.** The package is written and formatted for
this target. The principal editorial risk is conceptual breadth for a
public-data-only study, not missing statistical housekeeping.

**Transfer route 1: Communications Biology.** Use if the primary decision
emphasizes limited broad-interest novelty; the five-figure architecture and
bounded claims transfer with modest restructuring.

**Transfer route 2: Journal of Autoimmunity.** Use if a disease-specialist
audience is preferred; anticipate stronger requests for direct functional
mechanism.

**Nature Communications is not the efficient first route for the current
evidence.** It becomes rational only with a materially new evidence layer such
as matched patient perturbation, direct TF occupancy, prospective clinical
validation or an experimentally supported upstream mechanism.

No JCR quartile or CAS category is frozen here. The institution should verify
the current subscription edition immediately before submission or programme
reporting.

## Gate C8B required inputs

The corresponding author and all authors must provide or confirm:

1. Institutional ethics determination for this secondary public-data analysis,
   including committee name and reference/waiver wording where applicable.
2. Competing interests for every author.
3. Funding source, grant number, recipient and funder role, or confirmed no
   specific funding.
4. CRediT roles for Zhi Chen and Teng Qi, final authorship order, corresponding
   author designation and all-author manuscript approval.
5. Acknowledgements or confirmed `Not applicable`.
6. Originality, exclusive consideration and submission approval.
7. Repository public-release decision and an open-source licence.
8. Immutable Zenodo or equivalent archive DOI tied to the final public commit.
9. Suggested/opposed reviewers, if used, with independently verifiable
   institutional contact information.

These entries must not be guessed or silently replaced with boilerplate.

## Gate C8B execution order

1. Complete the author form in the local Gate C8R package.
2. Replace all six manuscript and two cover-letter placeholders in the source
   Markdown, preserving the surrounding claims.
3. Add the repository licence, scrub non-shareable metadata, make the intended
   release public and create the immutable archive DOI.
4. Insert the final repository URL, release commit and DOI in the manuscript,
   cover letter and data-availability statement.
5. Run the full Gate C8R rebuild command without skip switches.
6. Confirm that the final audit reports zero placeholders and author hard stops,
   then change portal authorization only through a dedicated C8B audit.
7. Upload editable DOCX files, individual figure files and additional files
   according to `README_GATE_C8R_PACKAGE.md`; keep `internal_qc/` local unless
   requested by the journal.

## Freeze policy during C8B

- Do not rerun clustering, change state definitions or add outcome-informed
  annotations.
- Do not select new genes, regulators or validation strata after seeing current
  results.
- Do not upgrade the CAMERA statement from 5/6 BH-significant tests.
- Do not describe GSE174188 donor non-overlap as independent-cohort validation.
- Do not infer causality, direct binding, a unique ligand or a discrete IFN-high
  subtype.
- Any genuine scientific change must create a new gate, regenerate affected
  figures/tables and invalidate the current C8R archive hash.

## Optional future research, not a pre-submission requirement

For a later higher-risk journal version or follow-up study, the highest-value
new evidence would be prospective patient sampling with matched clinical
covariates and ex vivo perturbation of the STAT1/STAT2-IFN axis in purified B-cell
compartments. Direct TF occupancy or chromatin-accessibility evidence would
raise the regulator claim beyond activity inference. These are new experiments,
not missing analyses that should delay the current Genome Medicine submission.
