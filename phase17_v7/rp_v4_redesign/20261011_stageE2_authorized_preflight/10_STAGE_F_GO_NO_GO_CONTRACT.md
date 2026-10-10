# RP v4 Stage F exact-code GO/NO-GO contract

Stage F is an authorization review, not an analysis run by implication.

Required before any final stream is opened:

1. Commit the Stage E2 implementation and confirm a clean synchronized Git HEAD.
2. Recompute and verify `04_STAGE_E2_SOURCE_BINDING.csv` against that checkout.
3. Have Zhi Chen and Teng Qi approve the exact commit and manifest SHA-256.
4. Replace the unissued template with a new signed GO receipt; never edit the
   historical template in place.
5. Re-run the Windows preflight and require stage141/stage142 authorization to
   resolve only for that exact receipt, commit and manifest.

If any item fails, keep `HOLD_EXACT_CODE_GO`. A future full run must execute all
40 x 4,000 outer attempts without replenishment and the independent stage142
truth calculation before result-blind adjudication. A G2C failure closes the
decomposition branch; there is no G2D. A G2C pass still does not unlock real
outcomes automatically.
