# Gate C6B pre-effect resource inventory

**Status:** `PRE_EFFECT_RESOURCE_INVENTORY_COMPLETE`

No GSE174188 or GSE135779 regulator effect was calculated during this step.

## CollecTRI freeze candidate

- URL: `https://omnipathdb.org/interactions?datasets=collectri&format=tsv&genesymbols=1`
- retrieval date: 2026-08-15
- raw bytes: 4,061,567
- raw SHA-256: `98EF1163146D2E28EE413E7C909174998CD9D742EA93D97CCFE93F3A14C160C1`
- interaction rows: 64,516
- organism: human
- current complex policy: inspect without splitting; scoring policy remains locked

## Candidate regulator coverage

| Regulator | Family | Exact targets | Signed targets | Complex rows | Inventory floor |
|---|---|---:|---:|---:|---|
| STAT1 | IFN_confirmatory | 303 | 291 | 0 | PASS |
| STAT2 | IFN_confirmatory | 50 | 50 | 0 | PASS |
| IRF7 | IFN_confirmatory | 34 | 32 | 0 | PASS |
| IRF9 | IFN_confirmatory | 27 | 25 | 0 | PASS |
| E2F1 | proliferation_negative_control | 314 | 299 | 0 | PASS |
| FOXM1 | proliferation_negative_control | 96 | 93 | 0 | PASS |
| MYC | proliferation_negative_control | 886 | 787 | 0 | PASS |
| MYBL2 | proliferation_negative_control | 52 | 43 | 0 | PASS |

## Orthogonal resources reviewed without effect calculation

- MSigDB `HALLMARK_INTERFERON_ALPHA_RESPONSE`, systematic ID `M5911`, human Hallmark collection; exact release and member file must be frozen before scoring.
- GSE23307, paired IFN-beta versus control primary human B cells from two healthy individuals; direct perturbation but too small for a powered confirmation.
- GSE142637, four-hour IFN-alpha/IFN-lambda stimulation of human PBMC; relevant single-cell context but without donor-level replication suitable for inference.
- GSE175913, sorted human naive and double-negative B-cell RNA-seq plus pSTAT1 flow-cytometry context; useful external biology, not a randomized transcriptomic perturbation.

## Frozen contrast coverage

Across the three confirmatory gene universes, the minimum matched signed-target count was 5. All 24 regulator-by-contrast combinations passed the 10-target floor: False.

## Decision consequence

The final Gate C6B contract must choose one exact CollecTRI complex policy, freeze the MSigDB release/member checksum, declare the confirmatory contrasts and multiplicity family, and keep small perturbation datasets descriptive.
