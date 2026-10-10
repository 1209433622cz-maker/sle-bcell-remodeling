# RP v4 Stage F2 advisor review

**Decision:** `PASS_STAGE_F2_INTEGRITY_HARDENING_AND_REBIND__HOLD_POST_COMMIT_EXACT_CODE_GO`.

The Stage F blockers were reproduced and repaired in an additive implementation.
The complete source dependency set is bound under `e69ca282c046e43325ee2ae1f0b53f76bf2ee017771423ace1e866c646bf21a8`. The Windows
qualification preserved the registered estimand, method, random stages and
thresholds; final stages were not consumed.

The new outer runner seals and reconciles every chunk, while the truth engine
uses deterministic per-scenario checkpoints, independent score cross-checking
and write-once receipts. The final adjudicator verifies outer accounting,
chunk payloads, truth CSV, checkpoint inventory and HC3-t(64) interval algebra.

This is still not authorization to execute stages 141/142. Both authors must
approve the new exact commit, this source-binding digest and the qualified
runtime receipt after the commit is published. Real WP2 outcomes, SRA, WP4,
manuscript replacement and submission remain locked.
