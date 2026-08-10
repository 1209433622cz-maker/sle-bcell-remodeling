# Workflow：Gate C1 hotfix v1.1

- 原运行：`20260806_132230`
- 输入冻结：PASS
- 失败原因：categorical `feature_name` 被当作 dataset
- 逻辑修正：library/cohort 一对多不再计为生物学 metadata conflict

## 新增输出

- `07_sample_library_manifest.csv`
- `08_sample_cohort_manifest.csv`
- `09_relationship_flags.csv`
- `11_sample_qc_summary.csv`
- `12_library_qc_summary.csv`
- `13_sample_qc_candidate_thresholds.csv`
- `14_library_qc_candidate_thresholds.csv`

旧失败目录保留，不覆盖。
