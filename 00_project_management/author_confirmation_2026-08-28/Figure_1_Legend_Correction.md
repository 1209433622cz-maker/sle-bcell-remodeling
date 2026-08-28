# Figure 1c threshold-label correction

Status: corrected source and separately generated preview; not yet integrated
into the author-approved manuscript/figure snapshot or authorized for submission.
Identified on 28 August 2026 during visual review of the approval-statement update.

## Finding

The current Figure 1c annotation and manuscript legend incorrectly name the
0.990 horizontal guide as a minimum mapped-ARI criterion. The frozen decision
`phase17_v7/gateC2B4/20260815_two_level_state_repair/06_GATE_C2B4_ADVISOR_DECISION.json`
states minimum mapped ARI = 0.900 and minimum mapping agreement = 0.990.
The observed minimum mapped ARI is 0.9902066569784328, not a prespecified 0.990
ARI threshold. Confusing an observed value with a decision threshold is incorrect.

## Exact correction for the final manuscript

Replace only:

> the dashed horizontal guide marks the minimum mapped-ARI criterion of 0.990.

With:

> the dashed horizontal guide marks the minimum mapping-agreement criterion of 0.990.

The 0.900 ARI criterion is already identified in panel b. Panel c is zoomed to
0.985-1.0008; the 0.900 ARI criterion is therefore outside that panel's range.
Do not move the line, change thresholds, replace an observed value or rerun
the biological models to repair this presentation error.

## Code and preview

The live `audit_tools/phase17_c7_01_build_main_figures.py` now reads the agreement
threshold directly from the frozen decision JSON and names it accordingly.
`audit_tools/phase17_postc9_09_preview_figure1_agreement_label.py` regenerates
Figure 1 into `phase17_v7/post_gateC9/20260828_figure1_label_review/`, checks the
actual plotted line and annotation, and verifies byte-identical source data.

This is a presentation correction, not a new statistical result or a reversal
of either scientific HOLD. Author approval of the preceding snapshot is retained
as historical fact. Final integration and final-file review must address this
known issue; the review package must not be mistaken for a submission-ready file.
