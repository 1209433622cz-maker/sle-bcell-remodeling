# RP v4 Stage I single real-result execution contract

Stage I may run only after both authors issue a new JSON authorization derived from `07_STAGE_I_AUTHOR_SIGNOFF_TEMPLATE.json`. The authorization must bind the post-Stage-H Git commit, the exact Stage H input-manifest hash, the exact execution-script hash and `D:\bioinfor\python.exe`.

The execution is limited to one donor-level response and one coefficient: `delta_profile`, fit by the frozen four-column OLS design with HC3 variance and a two-sided t(64) interval. Output is write-once and contains no donor-level response vector.

Any hash drift, dirty worktree, runtime drift, missing author, pre-existing output path or extra target fails closed before response construction. No preview run is permitted.

A Stage I result, whether positive, null or imprecise, must be reported without threshold changes, donor removal, fallback method or selective rerun. It does not unlock external outcomes, WP4, manuscript replacement or submission.
