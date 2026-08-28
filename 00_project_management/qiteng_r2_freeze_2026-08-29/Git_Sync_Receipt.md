# Scientific Freeze Git Synchronization Receipt

Observed at 2026-08-29 07:46 HKT.

- Repository: https://github.com/1209433622cz-maker/sle-bcell-remodeling
- Branch: `main`.
- Starting commit: `db26afd2eff852d104f5dc9d7afdfba6a85e9e18`.
- Content commit: `cf8cc7edbbfbee136349aa429c31d449820dbc2e`.
- Commit subject: Record author-confirmed scientific freeze and Zenodo replacement preparation.
- `git push origin main` completed successfully.
- Subsequent `git ls-remote origin refs/heads/main` returned the content commit.
- Scope: 17 files, 784 insertions and 20 deletions.
- The three confirmed manuscript files, 15 figure source tables, R1 decision,
  C9R decision and calibration evidence were not modified.
- 59 unit tests passed; the 21-file and nine-section freeze check passed.
- The eight new JSON evidence/plan files were parsed successfully.
- `git diff --cached --check` passed before the content commit.

This receipt is a follow-up document, not part of the content commit above.
It does not claim its own future commit hash or publication status.

## Remote Publication Boundary

Authenticated Zenodo record management is accessible after the user reported
login. No project draft was visible in the account uploads list; the existing
record offers New version. Creating the linked draft and reserving its DOI is
awaiting the precise browser action-time confirmation already requested.

No new DOI, Zenodo publication, old-record deletion, Git tag or GitHub release
was created. Git synchronization must not be interpreted as any of those actions.
The locally verified historical Zenodo backups remain outside Git.

The subsequent sequence is DOI reservation, administrative-only document
integration and rendering, verified archive publication, then handling only
old record 22086892 after replacement verification. R1 and C9R HOLD remain final.
