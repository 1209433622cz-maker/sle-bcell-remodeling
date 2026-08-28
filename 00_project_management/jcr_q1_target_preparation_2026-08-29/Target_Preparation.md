# JCR Q1 target preparation

Date: 2026-08-29. Internal decision support, not submission authorization.

## Current decision

Keep the corrected candidate unchanged. Do not reopen exploratory analyses or
redraw Figure 1. Retain Supplementary Figure S10 unless a concrete target-journal
or reviewer requirement warrants a source-driven change.

The conditional fit-first preference remains npj Systems Biology and Applications;
Communications Biology remains a parallel option. This is not a claim that either
journal's current JCR Q1 status is verified. Do not infer quartile from impact
factor, SJR, CAS partition or the favorable language in incoming review reports.
The earlier [journal assessment](../jcr_q1_refreeze_2026-08-28/Journal_Decision.md)
remains the ranking record; this note adds a practical institutional route and
clarifies the publication-stage requirements.

## Obtain the missing evidence

The CUHK-Shenzhen Library's [JCR guide](https://cuhk-shenzhen.libguides.com/c.php?g=964056)
links directly to the [institutional JCR bridge](https://idp.cuhk.edu.cn/bridge/jcr).
If off-campus access is needed, follow the library's
[off-campus instructions](https://library.cuhk.edu.cn/off-campus).
Do not share login credentials with the project.

The bridge was opened in this round. Its returned JCR table showed only the
npj public metadata already recorded: SCIE, Mathematical & Computational Biology,
most recent JCR data year 2025. Rank and quartile were not obtained. No institutional
profile was downloaded and no Q1 decision is justified by this access attempt.

Request profiles for both exact titles/ISSNs:

| Journal | Electronic ISSN | Required evidence |
| --- | --- | --- |
| npj Systems Biology and Applications | 2056-7189 | Latest applicable JCR year, every category, JIF rank/denominator and quartile |
| Communications Biology | 2399-3642 | Same fields; include all profile pages containing categories |

Retain the original PDF/export and record its source, date and SHA256. If a
journal has mixed quartiles across categories, disclose all of them and apply
the authors' institutional evaluation rule; do not silently select the most
favorable category. A profile export is sufficient for the project evidence
record; a paid certification is not automatically necessary.

The library describes a service that can verify JCR quartiles, but whether it
will issue a standalone pre-submission journal comparison should be confirmed.
The general library contact is `library@cuhk.edu.cn`, as displayed in the JCR
guide footer. The guide's subject-librarian email text and mailto target differed
at the time of inspection, so the draft does not guess that recipient.
[Library service](https://library.cuhk.edu.cn/zh-hans/research-output-certificates).

## Resolve cost feasibility

The publisher's Hong Kong agreement table names CUHK; Shenzhen eligibility cannot
be inferred from that entry. [Agreement listing](https://www.springernature.com/gp/open-science/oa-agreements/hong-kong).

The [npj institution lookup](https://www.nature.com/npjsba/open-access-funding)
was tested with the university name and Shenzhen. It returned no usable
institution-specific coverage result; the update control stayed disabled.
This is an inconclusive lookup, not proof that coverage is absent.

Ask the library to confirm the exact institution, journal, article type, date
range, student corresponding-author eligibility, funding cap and any approval
needed before submission. Do not change the authors' real affiliation to obtain
a benefit. A no-funding declaration is not evidence of an APC waiver.

Published original-research list prices previously checked on 2026-08-28 were
GBP 2,690 / USD 3,490 / EUR 2,990 for npj and GBP 3,250 / USD 4,390 / EUR 3,650
for Communications Biology. Recheck before a cost decision; taxes may apply and
acceptance-date pricing controls. [npj APC](https://www.nature.com/npjsba/apc),
[Communications Biology APC](https://www.nature.com/commsbio/open-access).

Discretionary waiver requests are considered individually. The support guide
states that the submission checkbox alone is not the complete application;
follow the actual system's request link and deadline when authorized to submit.
No waiver request or payment has been made.
[Publisher waiver instructions](https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers).

## One bounded formatting pass

Both journals permit flexible initial formatting. The final production guide
must not be described as a mandatory pre-submission hurdle.
[npj author guidance](https://www.nature.com/npjsba/for-authors-and-referees),
[Communications Biology guidance](https://www.nature.com/commsbio/submit/submission-guidelines).

After choosing an eligible journal:

1. Apply the existing [13-word title and 117-word abstract draft](../author_confirmation_2026-08-28/Journal_Format_Draft.md), with a final claim-by-claim edit. It already retains the R1 and corrected-mapping limitations. Do not compress the Results merely to mimic another journal.
2. Arrange sections and declarations for the selected journal. Preserve the limitations in prose; Methods already contains the AI-use disclosure. Communications Biology's acceptance guide calls for a Statistics and Reproducibility subsection, so consolidate the existing relevant material there if that journal is chosen; do not invent experiments or replicates.
3. Check the actual upload-stage requirements. Create a combined manuscript/figure review file when useful or requested. Do not upload the internal governance dossier as manuscript content.
4. Redraw only if actual size, readability, font or line requirements justify it. The current 170 mm figures are reviewed candidate figures, not a universal final-production template. Do not hand-resize PDF output.
5. Rebuild changed DOCX/PDF from source and verify all pages, captions, source-data links, accessibility and manifests. Retain all HOLDs and do not unlock new disease outcomes.

The acceptance-stage subsection guidance above is from the journal's linked
[style guide](https://www.nature.com/documents/commsj-life-style-formatting-guide-accept.pdf),
not a claim that a missing heading currently prevents initial submission.

## S10 disposition

The frozen calibration table has 26 elastic-net candidates, none eligible, and
46 centroid candidates, 16 eligible. The selected elastic-net diagnostic fallback
has coverage 0.941958 and B_ASC precision 0.885210. The selected centroid has
coverage 0.95 and B_ASC precision 1.0. Neither high overall balanced accuracy nor
a successful auxiliary mapper substitutes for the failed primary criterion.

The suggested two-axis frontier displays only coverage and B_ASC precision.
The actual rule also requires B_CONV precision >=0.90. If a frontier is requested
later, state that additional condition and distinguish the two mappers. Do not
label the two-dimensional quadrant as full Gate C9 eligibility. The current
S10 already shows the relevant state precision and coverage, so this round does
not add another figure candidate or reopen its approval scope.

## DOI and approval sequence

Keep the historical archive unchanged. Before creating a new version, inspect
existing drafts and GitHub-Zenodo automation to avoid duplicate records. New
draft creation, DOI reservation and public release are different actions and
require appropriately scoped authorization.

Zenodo permits reserving a DOI before publication and creating a linked new-version
draft. Once authorized, the preferred order is: obtain the new-version draft DOI,
insert it into the intended files, rebuild and verify, identify the final source
commit and file hashes, obtain exact-file author approval plus archive-publication
authorization, then publish the matching archive/release. Check the resulting
public DOI and uploaded hashes before journal submission. This avoids publishing
an archive before the DOI-bound files exist.
[DOI reservation](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/),
[Versioning](https://help.zenodo.org/docs/deposit/manage-versions/).

This is a proposed execution order, not a newly created draft or reserved DOI.
The existing record DOI must not be relabeled as the corrected candidate's DOI.
Journal submission still needs separate explicit authorization after the exact
files and journal are settled.
