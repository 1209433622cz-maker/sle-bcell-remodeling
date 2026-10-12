# Code and Verification

Run from the repository root. Public verification uses Python 3.11+ and only
the standard library: no data download, Office call or outcome-model fit.

```bash
python 2_code/audit_quality_control/verify_repository.py
python 2_code/audit_quality_control/verify_git_inventory.py
python -m unittest discover -s 2_code/tests -p "test_public_repository.py" -v
```

The verifier fails on altered/missing selected assets, unsafe manifest paths,
wrong critical copies, invalid gate boundaries or broken selected navigation.
Passing is provenance verification, not validation of biological truth.

The second command requires a Git checkout and verifies every indexed blob,
including byte size, SHA-256, Git object ID and exact path coverage. It checks
Git bytes rather than platform-dependent checkout line endings. The four
generated self-exclusions are recorded in the repository status.

## Backend Code

| Task | Authoritative code |
|---|---|
| Environment/acquisition | [02_analysis](../02_analysis/) |
| Frozen analysis and tests | [audit_tools](../audit_tools/) |
| Candidate build | [scientific_narrative_reaudit_20261012.py](../audit_tools/scientific_narrative_reaudit_20261012.py) |
| Matrix audit | [scientific_matrix_readonly_audit_20261012.py](../audit_tools/scientific_matrix_readonly_audit_20261012.py) |
| Figure 1 source export | [rerender_figure1_truetype_20261012.py](../audit_tools/rerender_figure1_truetype_20261012.py) |
| Local full QA | [scientific_candidate_final_qa_20261012.py](../audit_tools/scientific_candidate_final_qa_20261012.py) |
| Public indexes/summary build | [build_public_navigation.py](audit_quality_control/build_public_navigation.py) |

Frozen scripts are not moved: contracts bind their paths. `current_stageM/`
is a documented snapshot, not a second authority. Read [REPRODUCIBILITY.md](../REPRODUCIBILITY.md)
and stage contracts before executing scientific runners.

Candidate build/full QA require python-docx, PyMuPDF, the supplied Skill, WPS,
author-host accessibility tools and local input objects. They are **not**
portable no-data reproduction commands. The Skill is not distributed in Git;
public verification checks saved compact evidence.

Stage I is write-once and complete. Stage N/external outcomes require qualified
inputs and separate approvals. This push is not permission to execute them.
