# Gate C6B external-resource freeze

**Status:** `PRE_EFFECT_EXTERNAL_RESOURCES_FROZEN`

No disease-ranked regulator activity or GSE23307 expression difference was calculated.

## MSigDB

- human release: `2026.1.Hs`
- set: `M5911 / HALLMARK_INTERFERON_ALPHA_RESPONSE`
- members: 97 unique gene symbols
- overlap with frozen 12-gene IFN arm: 8/12
- GMT SHA-256: `EECAF6DAD908334AE885406EC72BDC0646D8917588ED7C219FAC92FC5363F596`

## GSE23307

- paired B-cell donors: HI1 and HI2
- conditions per donor: IFN-beta and untreated control
- monocyte samples excluded from the frozen B-cell perturbation comparison
- series-matrix SHA-256: `771D9F5C0D77447BC09330C18ECE17D9628E260A36E184C4EE76B1AB947EDF97`
- GPL6104 annotation SHA-256: `82AE57D6D9EC26CE2BCFF01CCD1DB498BB8055EE01471829DEC0A5AB5666D518`
- annotation rows: 22,185

## Lock

Expression rows remain locked until Gate C6B-1 software and synthetic-data qualification passes. GSE23307 has two paired donors and will be reported directionally without a powered P value.
