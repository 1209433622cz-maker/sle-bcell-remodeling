# RP v4 Stage A authority and feasibility freeze

**Decision:** `PASS_RPV4_STAGE_A_AND_V4B_HISTORICAL_DIAGNOSIS__HOLD_G2C_AND_NEW_COHORT_OUTCOMES`

**Date:** 2026-10-10

**Outcome use:** none; no real WP2/WP3 coefficient, new-cohort disease effect, P value or interval was fitted.

## Authority correction

The RP v4 proposal bundle passed its ten-file SHA-256 and byte-size manifest. It is accepted as an external proposal candidate, not as self-authorizing evidence. The project-side Git audit supersedes the candidate report's stale statement that the local WP3 commit was inaccessible: `8cba83172a52b71528cc2ab44dd3a936cb4dd8c7` is available, is 1 commit ahead of `origin/main`, and `origin/main` is its direct parent.

All RP v3 boundaries remain in force: G2 and G2B stay HOLD, real WP2 and new WP3 outcome fitting stay locked, WP4 remains conditional HOLD, and submission remains HOLD.

## Historical G2/G2B diagnosis

The independent project-side recount reproduces G2=90/150 and G2B=133/150 applicable target-scenario PASS cells. The 17 G2B failures comprise 11 coverage failures and 6 bias failures; one exact-null type-I failure overlaps a coverage failure.

The residual coverage pattern is concentrated in the difference estimands: `delta_profile` fails coverage in 9 cells and `delta_cellref` in 2. Misses are mild and broadly two-sided rather than a large one-tail collapse. The frozen outputs do not contain the per-replicate studentizer or inner-bootstrap pivot distribution needed to identify near-zero studentization as the cause. Therefore Stage A does not select a G2C interval.

The six bias failures are scientifically separate from interval undercoverage. Five occur in `C0_R2` or `C4_R0` beta/bin targets and one in `C4_R0 delta_cellref`; changing confidence-interval endpoints alone cannot repair point-estimator truth mismatch. A future G2C protocol must either narrow its estimand explicitly or carry a separate point-estimator diagnostic. It may not advertise a universal ten-target repair.

## External-cohort feasibility

- `GSE262846`: 88 libraries resolve to 45 patient IDs (17 HC, 13 active SLE, 15 inactive SLE); 43 patients have both rN and T1T2 libraries. One title/patient-ID discrepancy is preserved. The deposited processed object is RPKM, not the frozen count/CPM scale, so outcome fitting remains locked pending raw-count reconstruction and provenance review.
- `GSE118254`: 83 libraries resolve to 17 donor tokens (8 HC, 9 SLE), each represented by 3-6 sorted subsets. It is suitable for subset-aware work only after raw-count reconstruction and independence review.
- No exact numeric donor-token overlap was observed between these two accessions, but this does not establish independence because identifiers may be study-specific and the investigator lineage is shared.
- `GSE163121` has only 2 HC and 3 SLE donors; `GSE254176` is a six-patient longitudinal SLE resource without internal matched controls in the deposited series; `GSE239459` has one group-level library per condition. None qualifies as primary donor-level confirmation.

## Score contract

`S0=T_frozen` remains the primary frozen measurement anchor. `S1=T_rank` remains a technical sensitivity only. S2 is not admitted because the proposal does not yet provide one unique mathematical formula, denominator and missing-gene rule independent of outcomes.

## Authorization and stop rules

Authorized next work is limited to a source-level V4C protocol freeze: one primary G2C estimand/method, at most one prespecified fallback, new random streams and DGP perturbations, explicit point-bias handling, and a raw-count/provenance feasibility decision for GSE262846/GSE118254. No final G2C simulation, real disease effect, manuscript rewrite, figure replacement, submission package, release or Zenodo update is authorized.

If the single G2C contract cannot address both repeated difference-estimand undercoverage and the separate bias component without changing the scientific target after seeing results, close the decomposition branch as `G2C_HOLD__WP2_DECOMPOSITION_NOT_CLAIMABLE`. If raw counts or donor independence cannot be established for the external candidates, retain them as descriptive resources rather than clinical validation.

## Next stage

`RPV4_STAGE_C__SINGLE_G2C_AND_EXTERNAL_INPUT_PROTOCOL_FREEZE`
