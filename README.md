# SLE B-cell remodeling

Auditable analysis of cell identity, abundance and interferon-associated
transcription in systemic lupus erythematosus (SLE), with manuscript sources,
figure source data, bounded method-development records and reproducibility checks.

**Authors:** Zhi Chen; Teng Qi (corresponding author).
School of Medicine, The Chinese University of Hong Kong, Shenzhen.

**Repository state, 12 October 2026:** RP v4 scientific work is active; journal
submission and new external expression outcomes remain on hold. The latest
scientific-presentation files are **review candidates**, not a silently replaced
author-approved manuscript or a new DOI release.

## Start Here

| Goal | Entry point |
|---|---|
| Understand the scientific conclusions and their limits | [Evidence summary](3_results/scientific_summary/README.md) |
| Read the existing manuscript baseline | [Current manuscript](5_manuscript/current/Manuscript.pdf) |
| Review the latest text candidate | [Candidate manuscript](5_manuscript/scientific_narrative_candidate_2026-10-12/Manuscript.pdf) and [editable DOCX](5_manuscript/scientific_narrative_candidate_2026-10-12/Manuscript.docx) |
| Review the candidate supplement | [Supplementary Information](5_manuscript/scientific_narrative_candidate_2026-10-12/Supplementary_Information.pdf) |
| Inspect figures and their numerical sources | [Figure index](4_figures/README.md) |
| Understand what was changed | [Scientific audit and edit ledger](7_report/scientific_narrative_reaudit_2026-10-12/README.md) |
| Verify the public checkout | [Verification instructions](2_code/README.md) |
| Find the earlier submission materials | [Package status](6_release/README.md) |

This repository update is documented in the
[directory-restructure action record](7_report/action_records/action_record_2026-10-12_github_structure_sync_scientific_candidates.md).

## Organized Repository

The eight primary folders follow the requested working layout. `7_report` is the
report folder shown as `7.Report` in the reference screenshot; its existing name
is retained so bound paths and links remain valid.

```text
0_admin/       Project status, authority map, public integrity manifest
1_data/        Data acquisition guides, input manifests, metadata/design indexes
2_code/        Runnable verification, code navigation, environments and tests
3_results/     Compact current results, gates and source-bound scientific summary
4_figures/     Fig1-Fig8, Supplementary figures, source data and candidates
5_manuscript/  Current manuscript baseline and separately labelled candidates
6_release/     Existing pre-submission package, checksums and package status
7_report/      Action records, scientific reviews, edit ledgers and QA receipts
```

Additional folders preserve [archives](8_archive/), [reference navigation](8_reference/)
and [version/integrity records](9_version/). The historical backend remains in
`audit_tools/`, `phase17_v7/`, `02_analysis/` and related directories because
execution contracts bind their original paths. The organized folders provide
real deliverables, executable verification and explicit indexes; this update
does **not** move or rewrite frozen backend files. See the
[authority map](0_admin/MASTER_INDEX.md) and
[publication policy](0_admin/REPOSITORY_PUBLICATION_POLICY.md).

## Scientific Reading Path

The core supported conclusion is a reproducible **process-level B_CONV IFN/ISG
association**, not a new universal B-cell taxonomy or causal regulatory mechanism.

1. **Figure 1: identity scope.** Disease-blind reconstruction defines a broad
   B_CONV/B_ASC analysis scaffold. Fixed-representation stability does not imply
   end-to-end stability: B_ASC median Jaccard is 0.930323, below the frozen 0.95
   criterion. Fine-state and end-to-end identity failures remain reported.
2. **Figure 2: composition boundary.** The primary adjusted B_ASC odds ratio is
   0.947 (95% CI 0.636-1.410) in 90 sample-cohort strata. Lack of enrichment
   support is not an equivalence test or proof of unchanged abundance.
3. **Figure 3: program-level transcription.** The frozen IFN/ISG score differs
   by 0.837 (95% CI 0.525-1.148; four-program q=2.98e-6) in 89 pseudobulks.
   Internal nonoverlap analyses are within-accession support, not another
   independent study. The primary pan-B specificity control is positive at
   nominal significance and must not be described as null.
4. **Figure 4: external support and transfer ceiling.** GSE135779 childhood
   analysis uses 43 donors, with effect 1.042 (95% CI 0.681-1.402). It is
   source-label-defined replication. Genome-wide concordance across 4,410
   shared tested genes is weak (Spearman rho=0.026). Corrected required mapping
   fails B_ASC precision (0.885210 < 0.90), so no corrected source-label-independent
   external disease effect was estimated.
5. **Figure 5: observational regulatory context.** STAT1/STAT2 signed-target
   models support an IFN-centered interpretation, but broader M5911 depletion
   attenuates discovery STAT2 (95% CI crosses zero; q approximately 0.500).
   Target-model intervals are not participant-level TF activity. The two-donor
   IFN-beta experiment is descriptive; no causal regulator, direct binding,
   unique upstream ligand or clinical utility is established.

All **21 main panels and 38 supplementary panels** retain their scientific
roles. Fig6-Fig8 are reserved folders, not additional results. The
[59-panel decision matrix](7_report/scientific_narrative_reaudit_2026-10-12/PANEL_SELECTION_DECISION_MATRIX.csv)
records retention decisions, units and rejected alternatives. Numerical values
are traceable to the source tables, not selected from an edited final image.

## Manuscript Baseline and Candidate

| Object | Status |
|---|---|
| `5_manuscript/current/` | Preserved RP v4 Stage K limited-integration baseline; 32-page manuscript and 16-page supplement |
| `5_manuscript/scientific_narrative_candidate_2026-10-12/` | New source-level narrative candidate; 33-page manuscript and 16-page supplement; exact author review required |
| `4_figures/Fig1/canonical/` | Unchanged current Figure 1 delivery copy |
| `4_figures/Fig1/candidate_2026-10-12_truetype/` | Numerical source unchanged; TrueType export and unobstructed panel-b legend; author review required |
| `6_release/SLE_Bcell_Submission_Package_2026-10-12/` | Earlier pre-submission master package; **does not contain the new text/Figure 1 candidate** |

The new candidate corrects a Figure 3 claim-owner reference, explicitly reports
the positive primary pan-B control, separates the later 68-donor sensitivity
from regulatory evidence, clarifies TF-model units and repairs inherited body
font/S1 pagination issues. It does not alter statistical estimates or turn
historical HOLD decisions into PASS.

The latest editable authority is DOCX. Older `01_manuscript/*.md` mirrors are
retained for history and are **not byte-equivalent to the current DOCX**. Candidate
Markdown is exported from its candidate DOCX, avoiding a mixture of versions.

## RP v4: Completed Work and Next Gate

Stages 141/142 completed one frozen G2C procedure: 40 scenarios and 160,000
synthetic attempts, with 30 applicable scenarios passing and ten mandatory
boundary scenarios reported. This is qualification under the tested generating
mechanisms, not proof that every latent real-data measurement mechanism is known.
Earlier G2/G2B HOLD decisions for other targets remain in force.

Stage I estimates the **same 68-donor `delta_profile` already observed in WP1**:
0.034925 T0 units, HC3-t(64) 95% CI 0.011834-0.058016, nominal P=0.003612.
The [two source rows](3_results/current/StageK_Source_Data.csv) compare its
interval with the earlier paired bootstrap interval. These are not two
independent discoveries; method development was outcome-exposed. This sensitivity
is not a composition-mediated fraction or a cell-intrinsic disease effect, and
its scale/population differ from the primary TMM-score model.

The current prospective external question concerns within-patient transitional
versus resting-naive B-cell IFN differences and SLE activity in GSE262846.
[Stage M](3_results/current/StageM_Gate.json) freezes the disease-blind count
workflow and 176-run/88-library identity map, but does not unlock outcomes.

```text
PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE
__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION

Next: RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION
```

A qualified pinned toolchain, at least 2.5 TB physical scratch and separate
download authorization are still required. No GSE262846 expression effect is a
current manuscript result. Do not rerun the write-once Stage I procedure to
obtain another P value. [Detailed scientific governance](00_project_management/RP_V4_REDESIGN_STATUS.md)
and [reproducibility history](REPRODUCIBILITY.md) remain available.

## Data and Verification

Large GEO/CELLxGENE matrices, raw reads, full Monte Carlo checkpoints, machine-local
inventories, page-render caches and the supplied third-party writing-skill package
are **not uploaded by this update**. Restore data from their original accessions
and verify recorded checksums; a clone alone cannot rerun the complete biology.
See [data scope](1_data/README.md) and [retrieval guide](Data/README.md).

Public-file integrity checks use Python's standard library, without Scanpy,
R, WPS, authentication or a download:

```bash
python 2_code/audit_quality_control/verify_repository.py
python 2_code/audit_quality_control/verify_git_inventory.py
python -m unittest discover -s 2_code/tests -p "test_public_repository.py" -v
```

This verifies the curated published asset manifest, required structure,
source-copy identity, current gate boundaries and selected navigation links.
It does not rerun disease models or certify scientific validity. Full analytical
environment and execution contracts are documented in
[2_code](2_code/README.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

The latest local audit snapshot examined 41,249 ordinary files (about 5.748 GiB)
with applicable structural checks. This is a **local snapshot**, not the count
of uploaded Git files. The public checkout inventory is maintained separately
in [PUBLIC_REPOSITORY_INDEX.csv](0_admin/PUBLIC_REPOSITORY_INDEX.csv).

## Audit Limits

The scientific candidate QA recorded 127/127 checks, 49 visually inspected WPS
pages and 45 unchanged protected scientific assets. It did not rerun the full
pipeline, revalidate the complete primary text of all 33 references or perform
a new LibreOffice dual-engine qualification.

QiTeng v0.3.24.2's active CORE matches the supplied ZIP, but its own package
manifest QA reports **464 mismatches** outside that verified CORE. Raw results
and the automatic-numbered-reference parser limitation are disclosed in the
[audit report](7_report/scientific_narrative_reaudit_2026-10-12/action_record_2026-10-12_full_local_scientific_narrative_and_panel_reaudit.md).
The third-party Skill is not redistributed or treated as passing its package QA.

## Citation, License and Contact

The historical core archive is
[Zenodo 10.5281/zenodo.22151739](https://doi.org/10.5281/zenodo.22151739), mirrored
by [GitHub v1.1.0](https://github.com/1209433622cz-maker/sle-bcell-remodeling/releases/tag/v1.1.0).
It predates the later RP v3/RP v4 analyses and the present manuscript candidate.
The withdrawn initial DOI is not the recommended citation. See [CITATION.cff](CITATION.cff).

Original code: [MIT](LICENSE). Original manuscript, composite figures,
documentation and derived source-data tables: [CC BY 4.0](LICENSE_CONTENT_CC_BY_4.0.md).
Third-party data, publications, fonts, templates and writing-skill material retain
their original terms; see [LICENSE_SCOPE.md](LICENSE_SCOPE.md).

- Zhi Chen: zhichen1@link.cuhk.edu.cn; [ORCID](https://orcid.org/0009-0001-0072-5576).
- Teng Qi, corresponding author: tengqi@link.cuhk.edu.cn; [ORCID](https://orcid.org/0009-0007-7648-4776).

The material is research output, not clinical guidance. No journal submission,
new DOI publication or replacement of immutable historical releases is implied
by a GitHub push.
