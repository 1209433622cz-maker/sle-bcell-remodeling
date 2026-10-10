# RP v4 Stage E2 advisor review

## Decision

`PASS_RPV4_STAGE_E2_AUTHOR_CONTRACT_AND_CANONICAL_PIPELINE_BINDING__HOLD_EXACT_CODE_GO`

The two authors' approval of the frozen scientific contract is recorded. The
Windows canonical environment, resumable outer runner, independent shifted-DGP
truth runner and result-blind adjudicator are now byte-bound and technically
qualified on non-final stage 132. No stage 141 or 142 stream was consumed.

## Independent findings

The received Stage E package is internally complete (153/153 payload hashes,
clean ZIP CRC) and its shifted truth budget reproduces on Windows. Its preflight
script is not directly portable to the canonical Windows runtime because CSV
files are opened without an explicit encoding and fail under the GBK default.
The project-side implementation fixes this by requiring UTF-8 for every text
input and adds a regression gate for fail-closed final authorization.

## Scientific boundary

This stage establishes execution readiness only. It does not establish bias,
coverage, type-I error or a G2C scientific PASS. G2/G2B HOLD remains unchanged.
Real WP2 effects, external disease outcomes, SRA download, manuscript changes
and submission remain locked.

## Next stage

After this Stage E2 code is committed, both authors must review the exact Git
commit and source-binding manifest and issue a separate exact-code GO. Until
that receipt exists, the canonical runner refuses stage 141 and stage 142.
