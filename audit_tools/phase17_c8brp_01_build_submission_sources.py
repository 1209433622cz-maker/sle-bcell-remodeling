#!/usr/bin/env python3
"""Build journal-facing manuscript, supplement and release-support sources."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRP" / "20260825_journal_facing_prefreeze"
C8BR_RUN = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
MANUSCRIPT_SOURCE = ROOT / "01_manuscript" / "manuscript_v14_genome_medicine_release_preflight_2026-08-25.md"
MANUSCRIPT = ROOT / "01_manuscript" / "manuscript_v15_genome_medicine_journal_facing_prefreeze_2026-08-25.md"
SUPPLEMENT_SOURCE = ROOT / "01_manuscript" / "supplementary_information_v5_release_preflight_2026-08-25.md"
SUPPLEMENT = ROOT / "01_manuscript" / "supplementary_information_v6_journal_facing_2026-08-25.md"
SUBMISSION = ROOT / "04_submission"
TITLE = "Disease-blind single-cell reconstruction separates unstable B-cell states from reproducible interferon remodeling in systemic lupus erythematosus"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def words(text: str) -> int:
    clean = re.sub(r"[`*_#|\[\]]", " ", text)
    return len(re.findall(r"\b[\w'-]+\b", clean))


def section(text: str, start: str, end: str | None) -> str:
    begin = text.index(start) + len(start)
    finish = text.index(end, begin) if end else len(text)
    return text[begin:finish].strip()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def replace_section(text: str, heading: str, next_heading: str, body: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[:start] + heading + "\n\n" + body.strip() + "\n\n" + text[end:]


def build_manuscript() -> tuple[str, int, int]:
    manuscript = MANUSCRIPT_SOURCE.read_text(encoding="utf-8-sig")
    placeholders = manuscript.count("[[")
    manuscript = replace_once(
        manuscript,
        "**Version:** Pre-submission release-portability preflight v14, 25 August 2026",
        "**Version:** Journal-facing author-completion draft v15, 25 August 2026",
        "manuscript version",
    )
    manuscript = replace_once(
        manuscript,
        "resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but not stable hard naive-memory subtypes.",
        "resampling supported broad conventional-B (B_CONV) and antibody-secreting-cell (B_ASC) compartments but did not support stable fine-grained naive/memory subtype assignments.",
        "abstract identity precision",
    )
    manuscript = replace_once(
        manuscript,
        "**d,** Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Donors are the biological units in GSE135779; the adult estimate is directional only.",
        "**d,** Full childhood estimate, range across 43 donor deletions and estimates after omission of each of eight source B-cell labels. Sequential display labels 1-8 correspond to the original source codes retained in Figure 4 Source Data. Donors are the biological units in GSE135779; the adult estimate is directional only.",
        "Figure 4d legend",
    )
    manuscript = replace_once(
        manuscript,
        "edgeR : a Bioconductor package",
        "edgeR: a Bioconductor package",
        "edgeR reference punctuation",
    )
    manuscript = replace_once(
        manuscript,
        "the primary rank-based ULM results were supplemented by a post-audit sensitivity analysis that did not alter",
        "the primary rank-based ULM results were supplemented by a correlation-aware sensitivity analysis that did not alter",
        "correlation sensitivity reader wording",
    )
    manuscript = replace_once(
        manuscript,
        "Earlier untransformed GSE23307 files were retained solely as superseded audit artifacts and were excluded from every active result, figure and claim.",
        "Only log2(x+1)-transformed GSE23307 values contributed to the reported results, figures and claims.",
        "orthogonal response reader wording",
    )
    manuscript = replace_once(
        manuscript,
        "The post-audit STAT1/STAT2 CAMERA and FRY analyses were prespecified positive-direction sensitivity tests",
        "The STAT1/STAT2 CAMERA and FRY analyses used positive-direction sensitivity tests",
        "sensitivity family reader wording",
    )

    abstract_words = words(section(manuscript, "## Abstract", "## Keywords"))
    references = [
        int(value)
        for value in re.findall(
            r"^(\d+)\.\s", section(manuscript, "## References", None), flags=re.M
        )
    ]
    required = [
        TITLE,
        "did not support stable fine-grained naive/memory subtype assignments",
        "Sequential display labels 1-8",
        "edgeR: a Bioconductor package",
        "doi:10.1136/lupus-2026-002042",
    ]
    forbidden = [
        "technical- library",
        "statistical- engine",
        "proliferation controls",
        "edgeR :",
        "Gate C8S remains",
        "Gate C8B adds",
        "post-audit",
        "superseded audit artifacts",
    ]
    missing = [token for token in required if token not in manuscript]
    present_forbidden = [token for token in forbidden if token in manuscript]
    if abstract_words > 350 or references != list(range(1, 33)) or missing or present_forbidden:
        raise RuntimeError(
            f"Journal-facing manuscript contract failed: abstract={abstract_words}; "
            f"references={len(references)}; missing={missing}; forbidden={present_forbidden}"
        )
    if manuscript.count("[[") != placeholders:
        raise RuntimeError("Author-controlled manuscript placeholder count changed")
    return manuscript, abstract_words, placeholders


def build_supplement() -> str:
    supplement = SUPPLEMENT_SOURCE.read_text(encoding="utf-8-sig")
    supplement = replace_once(
        supplement,
        "**Version:** Pre-submission release-portability preflight, 25 August 2026",
        "**Version:** Submission draft, 25 August 2026",
        "supplement version",
    )
    supplement = replace_section(
        supplement,
        "## Supplementary overview",
        "## Supplementary Methods 1 | Prespecification and outcome protection",
        """
This supplementary information reports the prespecified workflow, diagnostic analyses, statistical families and source-data structure supporting the main manuscript. Seven supplementary figures were reconstructed from the same frozen analysis tables used for the main results. Every displayed panel is linked to machine-readable source data and exact numerical assertions; no exploratory analysis was added during preparation of this document.
""",
    )
    supplement = replace_section(
        supplement,
        "## Supplementary Methods 2 | Identity stability boundary",
        "## Supplementary Methods 3 | Biological units and contrast hierarchy",
        """
Identity stability was evaluated without disease, activity, treatment or outcome fields. The analysis used all 150,402 cells and the complete frozen 50-dimensional Harmony-adjusted principal-component representation. Twenty replicates were generated by selecting 80% of cells without replacement separately within each `library_uuid`; the target within each library was the rounded 80% count with a minimum of two cells. The recurrent highly variable genes, principal components and Harmony coordinates were not recomputed. Each replicate instead reconstructed a 15-nearest-neighbour graph from the selected frozen coordinates and reran Leiden clustering at resolutions 0.4, 0.6 and 0.8 using the `leidenalg` implementation.

The base seed was 20260806. For zero-based replicate `r=0,...,19`, within-library sampling used seed `20260806 + 1000 + r`, whereas neighbour-graph and Leiden random states used `20260806 + r`. Each resampled cluster was mapped to the full-data reference cluster with the largest cell overlap, using the row-wise maximum of the observed-by-reference contingency table. Stability summaries included adjusted Rand index (ARI), adjusted mutual information, majority-mapping agreement, state-level Jaccard index and recall.

At resolution 0.4, candidate policies were evaluated in a fixed order: the original five clusters; a four-state policy merging source cluster 2 into cluster 0; a three-state policy merging clusters 2 and 4 into cluster 0; and a two-compartment policy merging clusters 1, 2 and 4 into cluster 0 while retaining cluster 3 as the antibody-secreting compartment. The five-, four- and three-state candidates were required to achieve median ARI at least 0.75, minimum ARI at least 0.65, median mapping agreement at least 0.80 and minimum state median Jaccard at least 0.60; each failed at least the minimum-ARI criterion. The two-compartment policy was reconstructed from the saved disease-blind transition tables, with agreement reproduced to a maximum absolute difference of 1.11 x 10^-16, and was evaluated against stricter thresholds: median mapped ARI at least 0.95, minimum mapped ARI at least 0.90, median mapping agreement at least 0.995, minimum mapping agreement at least 0.990 and minimum state median Jaccard at least 0.95. It passed with values of 0.996, 0.990, 0.9999, 0.9998 and 0.991, respectively. The antibody-secreting compartment additionally required sample support of at least 0.90 for DERL3, JCHAIN, MZB1, TNFRSF17 and XBP1; observed support was 1.00 for every required marker. Fine naive/memory structure was therefore retained only as continuous transcriptional context rather than as hard disease-inference subtypes.
""",
    )
    supplement = replace_once(
        supplement,
        "This was post-audit robustness testing and not independent replication.",
        "This was a robustness analysis and not independent replication.",
        "correlation sensitivity wording",
    )
    supplement = replace_section(
        supplement,
        "## Supplementary Table S5 | Main-figure source-data map",
        "## Supplementary Table S6 | Reproducibility record",
        """
| Figure | Evidence basis | Machine-readable source |
|---|---|---|
| Figure 1 | Disease-blind identity stability and two-compartment adjudication | Figure1_source_data.csv |
| Figure 2 | Sample-level composition and asserted 43/47 primary groups | Figure2_source_data.csv |
| Figure 3 | Raw-count pseudobulk transcription with explicit tested-gene symbols | Figure3_source_data.csv |
| Figure 4 | Independent GSE135779 validation and influence analyses | Figure4_source_data.csv |
| Figure 5 | Regulatory and orthogonal response evidence | Figure5_source_data.csv |
""",
    )
    supplement = replace_section(
        supplement,
        "## Supplementary Table S6 | Reproducibility record",
        "## Supplementary Table S7 | Statistical tests and multiplicity families",
        """
| Component | Reader-accessible record |
|---|---|
| Main and supplementary figure data | Figure Source Data additional file with SHA-256 manifest |
| Complete statistical results | Full Statistical Results additional file with 12 gene-level branches and 12 sanitized design matrices |
| Correlation-aware sensitivity | Regulator Sensitivity additional file |
| Analysis code and decisions | `https://github.com/1209433622cz-maker/sle-bcell-remodeling` |
| Environment reconstruction | Pinned scientific and release environments documented in `REPRODUCIBILITY.md` |
| Immutable release | Final archive DOI will be inserted in the main manuscript availability statement after author approval |
""",
    )
    note_heading = "## Supplementary note on superseded artifacts"
    if note_heading not in supplement:
        raise RuntimeError("Expected the repository-provenance note in Supplement v5")
    supplement = supplement[: supplement.index(note_heading)].rstrip() + "\n"

    forbidden = [
        "Gate C",
        "preflight",
        "superseded",
        "release-portability",
        "C2B1-C8R",
        "post-audit",
    ]
    present = [token for token in forbidden if token in supplement]
    required = [
        "selecting 80% of cells without replacement separately within each `library_uuid`",
        "complete frozen 50-dimensional Harmony-adjusted principal-component representation",
        "15-nearest-neighbour graph",
        "resolutions 0.4, 0.6 and 0.8",
        "20260806 + 1000 + r",
        "row-wise maximum of the observed-by-reference contingency table",
        "minimum mapped ARI at least 0.90",
        "observed support was 1.00 for every required marker",
        "[[SUPPLEMENTARY_FIGURE:S7]]",
    ]
    missing = [token for token in required if token not in supplement]
    if present or missing or supplement.count("[[SUPPLEMENTARY_FIGURE:S") != 7:
        raise RuntimeError(
            f"Journal-facing supplement contract failed: forbidden={present}; missing={missing}"
        )
    return supplement


def author_matrix() -> str:
    return """# Final author and release completion matrix

The scientific analysis and journal-facing technical package are frozen. Complete every unchecked item before portal submission. Do not replace an unchecked item with an assumption.

## Confirmed author metadata

- [x] Author order: Zhi Chen first author; Teng Qi corresponding author.
- [x] Zhi Chen email: zhichen1@link.cuhk.edu.cn.
- [x] Teng Qi email: tengqi@link.cuhk.edu.cn.
- [x] Both authors: MSc students in Bioinformatics.
- [x] Shared affiliation: School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China.
- [x] ORCID: Zhi Chen 0009-0001-0072-5576; Teng Qi 0009-0007-7648-4776.
- [x] Official School postal address independently matched to <https://med.cuhk.edu.cn/en/page/1489> on 25 August 2026.
- [ ] Teng Qi confirms use of MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China as the submission correspondence address.
- [ ] Both authors confirm that the two-person author list is complete and that no contributor meeting authorship criteria has been omitted.

## Optional biography retained outside the manuscript

Zhi Chen is an MSc student in Bioinformatics at The Chinese University of Hong Kong, Shenzhen. His research focuses on multi-omics analysis and clinical cancer research, particularly integrated multi-omics analysis and the tumour microenvironment. He holds a BSc in Biomedical Sciences from Queen Mary University of London and an MB in Clinical Medicine from Nanchang University.

The journal's Authors' information section is optional and remains omitted from the manuscript. No biography for Teng Qi was inferred because none was supplied.

## Ethics and consent

- [ ] Institution-approved determination for this secondary analysis of public de-identified human data: not required, exempt or waived.
- [ ] Committee name and reference number if applicable.
- [ ] Confirmation that no identifiable individual information appears in any submission file.

## Declarations

- [ ] Financial and non-financial competing interests for both authors.
- [ ] Funder names, grant numbers, recipient initials and funder roles, or an explicit no-specific-funding statement.
- [ ] Final CRediT roles mapped to ZC and TQ.
- [ ] Acknowledgements with permission, or `Not applicable`.
- [ ] Both authors approve the manuscript, supplement, figures, source data and cover letter.
- [ ] Both authors confirm originality, exclusive submission and that the work is not under consideration elsewhere.
- [ ] Both authors approve the disclosure of generative-AI assistance.

## Repository release

- [ ] Select and approve an open-source licence covering original repository code and applicable text without relicensing GEO/CELLxGENE data.
- [ ] Confirm that no restricted raw data, credentials or direct identifiers are tracked.
- [ ] Create the final author-completed commit and GitHub release.
- [ ] Archive the exact release in Zenodo or an equivalent service and obtain a resolvable DOI.
- [ ] Insert the DOI into the manuscript, cover letter, README, repository citation and portal fields.

## Submission operations

- [ ] Check APC institutional agreement, funding or waiver strategy.
- [ ] Replace all manuscript and cover-letter placeholders.
- [ ] Run the final WPS, accessibility and deterministic-archive workflow.
- [ ] Match portal title, authors, affiliation, correspondence, declarations, files and DOI to the final manuscript.

## Hard stop

Portal submission remains unauthorized until every unchecked author, institution, licence, DOI and submission item above is documented.
"""


def target_decision() -> str:
    return """# Genome Medicine journal target and transfer plan

**Original route decision:** 20 August 2026

**Latest evidence and requirements review:** 25 August 2026

## Primary route

**Primary submission: Genome Medicine.** The manuscript is positioned as a human disease-genomics study whose main advance is inferential hierarchy, disease-blind state-definition validity and transfer of process-level biology across cohorts. It is not positioned as discovery of interferon involvement in SLE.

## Transfer-ready routes

1. Communications Biology: specialist biological advance with manageable reformatting.
2. Journal of Autoimmunity: strong disease fit but a higher likelihood of requests for direct mechanism.
3. Nature Communications: reach option only after new functional or prospective evidence, not after additional retrospective polishing.

## Evidence ceiling

The scientific analysis is closed. Matched patient perturbation, direct binding and prospective clinical validation remain absent. Additional public-data exploration would add heterogeneity and analytic flexibility without materially changing the submission decision.

## Current requirements review

The Genome Medicine Research guidance reviewed on 25 August 2026 requires a structured abstract of at most 350 words, three to ten keywords, complete Declarations headings, explicit ethics wording for human data even when approval is waived, full author institutional addresses and availability information that identifies supporting datasets. The journal encourages persistent identifiers for public data and software records.

Official source: <https://link.springer.com/journal/13073/submission-guidelines/research>

## Classification caveat

No JCR quartile or CAS category is frozen here. The submitting institution must verify the current edition for programme reporting.
"""


def reporting_checklist() -> str:
    return """# Genome Medicine reporting and submission checklist

## Scientific freeze

- [x] Canonical scientific freeze is Gate C8S.
- [x] Main numerical assertions pass 46/46.
- [x] Supplementary numerical assertions pass 29/29.
- [x] Primary B_ASC composition remains a null boundary.
- [x] Central claim remains independent IFN/ISG replication within broad B_CONV.
- [x] Regulatory language remains observational and non-causal.
- [x] Complete statistical archive retains 12 gene-level branches, 12 sanitized design matrices and its frozen SHA-256.

## Journal-facing reporting

- [x] Structured abstract is at most 350 words and contains no references.
- [x] Eight keywords are present.
- [x] Required main sections and all Declarations headings are present.
- [x] Supplement contains no internal gate history, repair history or superseded-artifact note.
- [x] Identity resampling reports fraction, stratification, frozen versus recomputed steps, mapping, thresholds and seeds.
- [x] Figure 1a uses graphical workflow nodes rather than ASCII arrows.
- [x] Figure 4d uses reader-facing sequential labels with original source codes retained in Source Data.
- [x] Figure 5a presents regulatory and response evidence as parallel branches.
- [x] Reference punctuation and 32-item sequence are checked.

## STROBE-informed internal mapping

- [x] Study design and secondary public-data setting are identified.
- [x] Eligibility, quality-control and minimum-cell rules are described.
- [x] Biological units, repeated donors and sample-cohort strata are explicit.
- [x] Exact analysis sizes accompany major results and figure panels.
- [x] Statistical models, sidedness and multiplicity families are mapped.
- [x] Sensitivity analyses and missing clinical covariates are reported.
- [x] Internal versus independent validation is distinguished.
- [x] Limitations and claim boundaries are explicit.
- [x] Public accessions and repository location are reported.
- [ ] Immutable release DOI will replace the mutable repository-only citation after author approval.

## Package and files

- [x] Editable manuscript, Supplementary Information and cover-letter DOCX files.
- [x] Figures 1-5 and Supplementary Figures S1-S7 in vector PDF and 600-dpi PNG.
- [x] Figure Source Data, Regulator Sensitivity and Full Statistical Results archives.
- [x] Clean portal filename aliases are generated by the builder and hash-mapped to provenance files.
- [x] WPS review PDFs, page-image QA and accessibility reports are package-controlled.

## Author and release hard stops

- [ ] Ethics determination.
- [ ] Competing interests and funding.
- [ ] CRediT, acknowledgements, all-author approval and originality/exclusivity.
- [ ] Correspondence address approval.
- [ ] Repository licence and immutable DOI.
- [ ] APC or institutional agreement check.
- [ ] Zero-placeholder rebuild and final portal field comparison.

**Current status:** journal-facing scientific and technical prefreeze may pass; portal submission remains blocked by the unchecked author and release items.
"""


def copy_reference_state() -> None:
    target = RUN_DIR / "references"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(C8BR_RUN / "references", target)
    prior = json.loads(
        (C8BR_RUN / "01_GATE_C8BR_REFERENCE_STATUS.json").read_text(encoding="utf-8")
    )
    status = {
        "created_at": "2026-08-25",
        "decision": "PASS",
        "doi_records": prior["doi_records"],
        "manuscript_references": prior["manuscript_references"],
        "source": "byte-identical Gate C8BR verified reference state",
        "source_status_sha256": sha256(C8BR_RUN / "01_GATE_C8BR_REFERENCE_STATUS.json"),
    }
    (RUN_DIR / "01_GATE_C8BRP_REFERENCE_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    manuscript, abstract_words, placeholders = build_manuscript()
    supplement = build_supplement()
    MANUSCRIPT.write_text(manuscript, encoding="utf-8", newline="\n")
    SUPPLEMENT.write_text(supplement, encoding="utf-8", newline="\n")

    outputs = {
        "cover": SUBMISSION / "cover_letter_genome_medicine_gateC8BRP_AUTHOR_COMPLETION_REQUIRED_2026-08-25.md",
        "author_matrix": SUBMISSION / "author_completion_matrix_gateC8BRP_2026-08-25.md",
        "target": SUBMISSION / "journal_target_decision_gateC8BRP_2026-08-25.md",
        "checklist": SUBMISSION / "reporting_checklist_gateC8BRP_2026-08-25.md",
    }
    cover = (
        SUBMISSION / "cover_letter_genome_medicine_gateC8BR_AUTHOR_COMPLETION_REQUIRED_2026-08-25.md"
    ).read_text(encoding="utf-8-sig")
    outputs["cover"].write_text(cover, encoding="utf-8", newline="\n")
    outputs["author_matrix"].write_text(author_matrix(), encoding="utf-8", newline="\n")
    outputs["target"].write_text(target_decision(), encoding="utf-8", newline="\n")
    outputs["checklist"].write_text(reporting_checklist(), encoding="utf-8", newline="\n")
    copy_reference_state()

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BRP_JOURNAL_FACING_SOURCES_BUILT",
        "source_scientific_freeze": "Gate C8S",
        "scientific_estimates_changed": False,
        "abstract_words": abstract_words,
        "references": 32,
        "manuscript_author_placeholders": placeholders,
        "supplement_figure_markers": supplement.count("[[SUPPLEMENTARY_FIGURE:S"),
        "supplement_internal_history_tokens": 0,
        "identity_resampling_reporting": {
            "cells": 150402,
            "replicates": 20,
            "fraction": 0.8,
            "stratification": "library_uuid",
            "frozen_dimensions": 50,
            "recomputed": "15-nearest-neighbour graph and Leiden 0.4/0.6/0.8",
            "base_seed": 20260806,
        },
        "author_metadata_confirmed": [
            "names",
            "emails",
            "MSc student in Bioinformatics titles",
            "affiliation",
            "ORCIDs",
        ],
        "outputs": {
            "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
            "supplement": SUPPLEMENT.relative_to(ROOT).as_posix(),
            **{name: path.relative_to(ROOT).as_posix() for name, path in outputs.items()},
        },
    }
    (RUN_DIR / "03_GATE_C8BRP_SOURCE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
