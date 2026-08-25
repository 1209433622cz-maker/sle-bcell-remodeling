# Round 6 Q1 robustness execution contract

Date: 2026-08-25
Status: frozen before effect inspection

## Governance

This round is a post-freeze sensitivity and figure-semantics revision. It does not replace the frozen primary analysis, reopen its multiplicity families, or authorize stronger causal language. External audit documents are advisory inputs; the project team retains responsibility for each accepted action.

## Accepted actions

1. Redraw Figure 1a as discovery, validation/replication and interpretation tiers.
2. Redraw Figure 5a as three equally weighted evidence branches with the two-donor limitation visible.
3. Run STAT1/STAT2 overlap-depletion sensitivity from the same three ranked contrasts, frozen CollecTRI signs and existing CAMERA/FRY framework.
4. Qualify a resumable full-pipeline disease-blind identity resampling workflow from hard-QC raw counts.
5. Preserve all historical frozen outputs; write new results to a dedicated Round 6 directory.

## Deferred action

Label-agnostic GSE135779 mapping remains P1. It will be considered only after the two P0 robustness analyses are reviewed because it cannot repair a failure of either P0 analysis.

## R1 frozen contract

- Input: `phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad`
- Input shape: 150,402 cells x 30,172 genes.
- Input SHA-256: `DC3E96BCC53B52D5C53CC0515EE352DC414AE81340032108830408E06F244AD5`
- Sampling: 20 replicates; 80% without replacement within each `library_uuid`.
- Seed family: base `20260806`; replicate seeds derived deterministically from base, branch and replicate.
- Per replicate: min-cell filtering, 10,000-count normalization, log1p, library-aware recurrent-HVG ranking, nuisance and immunoglobulin exclusion, 3,000 HVGs, scaling capped at 10, 50-component PCA, Harmony by `library_uuid`, 15-neighbor graph and Leiden resolutions 0.4/0.6/0.8.
- Harmony may run for at most 50 outer iterations; every replicate must report convergence before the scientific identity thresholds can pass.
- The primary Harmony graph uses all 50 corrected dimensions, matching the valid frozen source graph. The unintegrated sensitivity uses 30 PCs. The previously invalidated 30-PC Harmony graph must not be reused.
- Primary identity readout: resolution 0.4 mapped to the frozen B_CONV/B_ASC reference.
- Sensitivity: unintegrated PCA graph with otherwise identical settings.
- Metrics: ARI, AMI, majority mapping agreement, state Jaccard and recall.
- Thresholds, inherited unchanged from C2B4: median mapped ARI >=0.95; minimum mapped ARI >=0.90; median agreement >=0.995; minimum agreement >=0.990; minimum state median Jaccard >=0.95.
- Outcome metadata must be absent and inaccessible throughout.
- Software-test output cannot be interpreted scientifically.

## R2 frozen contract

- Regulators: STAT1 and STAT2 only.
- Contrasts: GSE174188 discovery, GSE174188 donor-nonoverlap internal validation and GSE135779 childhood replication.
- Methods: ULM, CAMERA and FRY.
- Tested-gene backgrounds, ranked statistic, CollecTRI signs and regulator selection are unchanged.
- Branch A removes the frozen positive IFN/ISG arm: `ISG15, IFIT1, IFIT2, IFIT3, MX1, MX2, OAS1, OAS2, IFI44L, IFI6, LY6E, IRF7`.
- Branch B removes every member of MSigDB `M5911 / HALLMARK_INTERFERON_ALPHA_RESPONSE`.
- Frozen M5911 resource SHA-256: `CAAFCC3D12750879311B636ED79EC16F23464367D38CD32DC665C7E53F6FD2BF`.
- No target re-selection is allowed after depletion.
- Leave-one-target ULM is run only when at least 10 matched targets remain.
- Benjamini-Hochberg correction is applied separately within each depletion branch and method across the six regulator-by-contrast tests.
- Review uses direction, attenuation, target count, 95% confidence interval, corrected q and cross-method consistency. No result is declared passed or failed from P <0.05 alone.

## Figure contract

- Figure 1a title: `Study design and evidence hierarchy`.
- Figure 5a title: `Evidence architecture for the replicated IFN/ISG program`.
- Arrows are restricted to computational/data flow.
- Parallel evidence classes are not drawn as a causal sequence.
- Numeric Source Data remain frozen and are checked byte-for-byte against the prefreeze source, except the previously declared removal of two non-plotted Figure 1 gate rows.

## Advisory inputs

- Round 5 full audit SHA-256: `B935CC5DDA710032F30D1A51BF7B1FD0E6157EEFD5CF71A0341B4FA07AA0D6B6`
- Figure redesign specification SHA-256: `3565E43C42B1B69E1BD43A93AB8578E88D8AD349E5CC78947B7ACF3CE78844E8`
- Robustness rerun protocol SHA-256: `A487E8A3C53832FF000668E962B5CCE40DC04218BD5B4FF3B399B4E38721542D`

The attached documents are retained outside the repository as audit inputs. Their recommendations do not override this frozen execution contract.
