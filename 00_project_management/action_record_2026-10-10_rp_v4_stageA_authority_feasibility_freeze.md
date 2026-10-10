# Action record: RP v4 Stage A authority and feasibility freeze

**Date:** 2026-10-10

**Workspace:** `H:\cuhk-2025fALL\6013RP-wyf`

**Final decision:** `PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`

## Request and operating boundary

The user asked to continue according to Research Plan v4 and to determine the
next stage. The supplied ZIP was treated as an external proposal/audit candidate,
not as an instruction source or an automatically valid gate.

This round was restricted to:

- proposal integrity and Git authority;
- inheritance of RP v3 negative gates;
- diagnosis of existing synthetic G2/G2B outputs;
- metadata-only external-cohort feasibility;
- result-blind score governance; and
- a prospective next-stage protocol boundary.

No new WP2/WP3 disease coefficient, new-cohort group summary, P value, confidence
interval or clinical calibration was fitted. No manuscript, figure, submission
package, release or Zenodo record was changed.

## Inputs

### External proposal bundle

`C:\Users\Administrator\Downloads\SLE_Bcell_RP_v4_Proposal_Audit_20261010.zip`

- bytes: 224,853;
- SHA-256: `ad4f422f185a75ead5cec4d7fe91b2bd3b36cbe1b5f3dce227016cd8c2fd3b05`;
- ZIP entries: 11;
- unsafe paths: 0;
- duplicate paths: 0;
- manifest-controlled files: 10/10 byte-size and SHA-256 PASS.

The extracted bundle is retained locally under the ignored path
`phase17_v7/rp_v4_redesign/20261010_proposal_external_candidate/`.

### Historical synthetic evidence

- canonical G2 adjudication and ignored full attempt-level run;
- canonical G2B adjudication and ignored stage-121 full attempt-level run;
- RP v3 G2B scope-contraction contract;
- RP v3 WP3 pooled-measurement gate and score contract.

### Official public metadata

Official NCBI GEO MINiML archives were downloaded for GSE262846, GSE118254,
GSE163121, GSE254176 and GSE239459. Raw MINiML archives are retained in the
ignored `source_metadata/` directory; their SHA-256 values are recorded in the
tracked cohort register. Expression matrices were not downloaded.

Official records used:

- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE262846
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE118254
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163121
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE254176
- https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE239459

## Implemented changes

### Reproducible tooling

Created:

- `audit_tools/rp_v4_stageA_01_freeze.py`;
- `audit_tools/run_rp_v4_stageA.ps1`;
- `audit_tools/test_rp_v4_stageA.py`.

The Python tool validates the proposal manifest, records the input Git ancestry,
recounts G2/G2B, reads the attempt-level G2B failures, parses MINiML with the
standard XML parser, freezes score roles and writes a self-hashed Stage A record.
It contains no outcome model call. Five focused tests cover Boolean parsing,
failure classification, MINiML parsing, S2 exclusion and the outcome-lock source
contract.

### Repository policy

Updated `.gitignore` so that the external proposal extraction and official raw
MINiML archives remain local. Compact derived outputs, code, statuses and action
records are tracked.

Updated `README.md` to make RP v4 the active branch, retain RP v3 as historical
provenance, expose the current gate and document the exact reproduction command.
Created `00_project_management/RP_V4_REDESIGN_STATUS.md` as the current status
authority; `RP_V3_REDESIGN_STATUS.md` remains unchanged as the bounded historical
record.

## Verification and results

### Git authority

At Stage A intake:

- local baseline: `8cba83172a52b71528cc2ab44dd3a936cb4dd8c7`;
- remote-tracking `origin/main`: `f2eca1abec44afb73688823f57e42ab78b971203`;
- remote-tracking commit is the direct parent of the local baseline;
- local baseline was one commit ahead and zero behind.

This supersedes the external proposal report's statement that the local WP3
commit was inaccessible. The report was reasonable for its environment but is
not authoritative for the current workspace.

### G2/G2B independent recount

The project-side tool reproduced:

| Method | Applicable cells PASS | HOLD |
|---|---:|---:|
| G2 | 90/150 | 60/150 |
| G2B | 133/150 | 17/150 |

G2B residual failures consist of:

- 11 coverage failures;
- six bias failures;
- one exact-null type-I failure overlapping a coverage failure.

Target localization:

- `delta_profile`: 9 coverage failures, including the overlapping type-I cell;
- `delta_cellref`: 2 coverage failures and 1 separate bias failure;
- `beta_B`: 1 bias failure;
- `beta_bin_2`: 2 bias failures;
- `beta_bin_3`: 1 bias failure;
- `beta_bin_4`: 1 bias failure.

The undercoverage is mild and broadly balanced across lower and upper tails.
The mean interval lengths are close to a normal 95% empirical-SD benchmark, but
per-attempt coverage remains below the frozen Wilson-lower-bound gate. The
frozen outputs do not retain the replicate-level studentizer/pivot distribution,
so Stage A cannot truthfully diagnose a near-zero studentizer or choose one
corrective interval. The six point-bias failures also show that an interval-only
change cannot repair the complete ten-target contract.

### External-cohort unit audit

#### GSE262846

- 88 GEO libraries;
- 45 unique `patient id` values;
- 17 HC, 13 active SLE (`SLEDAI > 4`), 15 inactive SLE;
- 43 donors have both rN and T1T2 libraries; two have rN only;
- one title/patient-ID mismatch: title `SLE.0.3621.rN`, metadata patient ID
  `3651`;
- processed object is RPKM, not the frozen count/CPM scale.

Decision: conditional metadata PASS; raw-count compatibility, sample anomaly and
provenance must be closed before outcomes.

#### GSE118254

- 83 GEO libraries;
- 17 title-derived donor tokens: 8 HC and 9 SLE;
- 3-6 sorted B-cell-subset libraries per donor;
- GEO records a raw-data replacement in May 2021;
- no count-scale object compatible with the frozen score was accepted in this
  round.

Decision: conditional donor-structure PASS; raw reconstruction and independence
remain HOLD.

#### Cross-accession overlap

There are zero exact numeric donor-token overlaps between GSE262846 and
GSE118254. This is not proof of independence because identifiers may be
study-specific and both accessions share investigator lineage. Independent-
validation language remains prohibited without a stronger provenance statement.

#### Other candidates

- GSE163121: 2 HC and 3 SLE donors; exploratory only.
- GSE254176: 57 GEO samples represent 19 longitudinal visits from 6 SLE patients
  across scRNA/scTCR/scBCR; no internal matched HC series units; exploratory only.
- GSE239459: one group-level scRNA library each for SLE, pSS and HC; no donor-
  level inference.
- GSE135779: historical external source, not a new held-out validation.

### Score governance

- S0 remains the frozen primary anchor.
- S1 remains a technical sensitivity.
- S2 is not admitted because no unique outcome-blind formula, denominator and
  missing-gene policy have been specified.

### Tests and integrity

- focused RP v4 tests: 5/5 PASS;
- Stage A checks: 11 PASS and 2 intentional fail-closed HOLDs
  (`external_count_compatibility`, `S2_unique_formula`);
- generated numbered files: 13 plus integrity manifest;
- integrity manifest: 13/13 SHA-256 and byte-size rechecks PASS.

The intentional false checks are not workflow failures. They encode the exact
reasons outcome execution and S2 remain locked.

## Scientific decision

Stage A and the historical component of V4B are complete. The evidence supports
continuing to one protocol-freeze round, not to final simulation or clinical
analysis.

The most defensible G2C research problem is not "make all ten targets pass".
It is whether one explicitly selected difference estimand can obtain calibrated
uncertainty under a newly frozen validation design, while separately accounting
for point-estimator bias. If this cannot be specified without changing the
scientific target after seeing historical outcomes, the decomposition branch
should close.

The strongest external candidate is GSE262846 because donor ID, SLEDAI and paired
rN/T1T2 structure are recoverable. It is not yet analysis-ready because the
processed scale is incompatible with S0 and its independence/provenance is not
fully established. GSE118254 is a useful subset-aware comparator, not a second
independent confirmation by default.

## Next stage

`RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE`

Required next outputs:

1. one primary G2C estimand and method plus at most one prespecified fallback;
2. independent final-simulation random streams, DGP shifts, acceptance gates and
   compute/checkpoint budget;
3. explicit separation of interval undercoverage from point-estimator bias;
4. raw-count reconstruction feasibility for GSE262846 and GSE118254;
5. donor-overlap/provenance decision stronger than exact token comparison;
6. S0/S1 technical contract; S2 remains excluded unless uniquely defined;
7. author sign-off before any final G2C or disease/activity outcome execution.

If the single frozen G2C strategy later fails, the branch closes as
`G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`; no G2D rescue is permitted.

## Git and GitHub synchronization

The Stage A implementation was committed locally as
`03f54424f82f87cda5acd5dc873a485b836d872a` before this synchronization note was
added. A direct `git push origin main` was attempted at 2026-10-10 22:38 HKT and
failed before authentication because the workstation could not connect to
`github.com:443`.

At that point `origin/main` remained
`f2eca1abec44afb73688823f57e42ab78b971203`, while local `main` was two commits
ahead: the prior RP v3 WP3 commit plus this RP v4 Stage A commit. No GitHub API
file-by-file reconstruction was used because that would create a divergent
history rather than push the audited local commits. A later successful normal
Git push should transmit both commits together.

After the action record was added, one final normal push retry also failed
before authentication with `Recv failure: Connection was reset`. The remote
tracking reference remained unchanged; this is a network transport blocker, not
a scientific, test, merge or credential failure.
