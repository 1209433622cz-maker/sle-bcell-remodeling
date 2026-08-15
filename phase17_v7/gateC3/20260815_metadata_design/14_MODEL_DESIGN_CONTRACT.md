# Gate C3 frozen model-design contract

**Status:** `FROZEN`

- Minimum frozen B cells per sample-cohort stratum: 50
- Biological replicate: `sample_uuid`
- Technical stratum: `sample_uuid x Processing_Cohort`
- Canonical individual key: `donor_id` (`ind_cov` is a verified alias)
- Primary: cohort 4 managed versus normal, age and ethnicity adjusted
- Internal validation: cohort 2 European-American females, age adjusted
- Secondary: cohort 3 flare versus normal, age and ethnicity adjusted
- Treated cohort-3 samples: descriptive only

## Binding restrictions

- cell-level inferential tests
- hard naive-versus-memory composition
- platelet-associated B-cell identity
- source cluster-4 publication subtype
- cohort or covariate selection after viewing effect estimates

No abundance effect estimate was inspected when this contract was generated.