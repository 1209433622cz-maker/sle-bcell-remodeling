# WP1 pre-effect execution addendum - final freeze

Date: 2026-10-10
Status: **PASS_WP1_PREFIT_UNLOCK**
Disease coefficients inspected while preparing this addendum: **No**

## Frozen analysis population and design

- One shared complete-case population is used for A0, A1 and A2: **68 unique donors**.
- Arm support is **31 controls** and **37 managed-SLE donors**.
- A0 requires at least 50 historical B_CONV cells; A1 requires all five bins to contain at least 30 cells; A2 requires at least 50 mapped B_CONV cells.
- The frozen primary design is `intercept + is_managed + age_centered + ethnicity_asian`; observed rank is **4/4**.
- The original 43-control T0 reference is retained. T0 is not recomputed on the reduced analysis set.

## A1 operator and estimand

For donor `i`, bin `k` and gene `g`, raw counts are divided by the full-bin raw library total to obtain linear CPM. The common-composition expression is

`CPM_A1_ig = sum_k pi_ref_k * CPM_ikg`.

The identical frozen transform is then applied:

`T0_A1_ig = [log2(CPM_A1_ig + 0.5) - mu0_g] / sd0_g`,

followed by the mean over the 12 frozen IFN/ISG genes. This is expression reconstruction before transformation. It is not the average of logged bin scores. `delta_beta_ann_A1` is therefore labelled a **joint identity-axis/common-composition standardization sensitivity**, not a pure annotation effect or causal mediation quantity.

## A2 semantics and mapping

- A2 is the frozen historical strong-ISG-list-excluded representation; it retains `LY6E` from the 12-gene program.
- A2 clusters were mapped to A0 broad compartments by disease-blind cell overlap before the disease design was read.
- Mapping retained B_CONV and B_ASC with no ties or class collapse. Minimum cluster purity versus A0 was **0.964688**; this is agreement to a reference scaffold, not biological accuracy.

## Bootstrap contract

- Seed: `20261010`.
- Exactly `2000` attempted replicates; no replacement of failed attempts.
- Sampling is stratified by `is_managed`, with replacement within the 31-control and 37-SLE arms.
- A single shared donor draw is applied to all three branches and both paired deltas.
- Duplicate donors are represented by repeated rows in that replicate.
- Primary intervals are 2.5th and 97.5th percentiles over successful paired replicates.
- A replicate fails for a missing arm, non-finite values or design rank below 4.
- WP1 is held if more than 1% of attempted replicates fail.
- A2 mapping, A1 cutpoints, `pi_ref`, T0 and the 68-donor support set are conditioned on and are not rebuilt inside the bootstrap.

## Boundaries

No equivalence margin, p-value family, causal interpretation, manuscript replacement, WP4 unlock, GitHub release, Zenodo update or submission action is authorized by this gate. G2 remains unassessed until full simulations match the final operator and missingness procedure.

## Frozen hashes

- Shared analysis set: `042C3C32912FAECA302B22F426B1DBB259F032EE88ABCEE522FD81231D3C1E08`
- Shared design matrix: `878418ECAE53E2F846B079A048B30BB987272534EF442D1512A147A9C9A4F54A`
- A2 overlap mapping: `9CF9E19E54175030E518219A64C387162634A3BC35253D9936498B75988D1F13`
- T0 reference: `0244242AB31441F7D46305A5E69AD77714FBF2A2833EE09D16CF893F3D9E610F`
- `pi_ref`: `D8492404E9EA19F5D6735A2995A4E52B0ED7A867B7B1A0577D0237BBDE131BB4`
- Sufficient-count manifest: `276091FDD223F6D3B8734402387E19C793E2C739E34DA7DAF4245693AA56A9BF`
