#!/usr/bin/env python3
"""Build the author-approved, DOI-complete final submission sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRF" / "20260825_author_release"
MANUSCRIPT = ROOT / "01_manuscript" / "Manuscript.md"
SUPPLEMENT = ROOT / "01_manuscript" / "Supplementary_Information.md"
COVER = ROOT / "04_submission" / "Cover_Letter.md"
# Stable, version-neutral publication sources are authoritative. Historical dated
# drafts remain provenance records but must never overwrite these files.
SOURCE_MANUSCRIPT = MANUSCRIPT
SOURCE_SUPPLEMENT = SUPPLEMENT
SOURCE_COVER = COVER
AUTHOR_RECORD = ROOT / "04_submission" / "Author_Confirmation.md"
CHECKLIST = ROOT / "04_submission" / "Reporting_Checklist.md"
ZENODO_METADATA = ROOT / "04_submission" / "Zenodo_Metadata.json"
README = ROOT / "README.md"
CITATION = ROOT / "CITATION.cff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--doi", required=True)
    return parser.parse_args()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def replace_section(text: str, start: str, end: str | None, body: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin) if end else len(text)
    suffix = text[finish:] if end else ""
    return text[:begin] + start + "\n\n" + body.strip() + "\n\n" + suffix


def word_count(text: str) -> int:
    clean = re.sub(r"[`*_#|\[\]]", " ", text)
    return len(re.findall(r"\b[\w'-]+\b", clean))


def validate_doi(doi: str) -> str:
    value = doi.strip().removeprefix("https://doi.org/").removeprefix("doi:")
    if not re.fullmatch(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", value):
        raise ValueError(f"Invalid DOI: {doi}")
    return value


def build_manuscript(doi: str) -> tuple[str, int]:
    text = SOURCE_MANUSCRIPT.read_text(encoding="utf-8-sig")
    draft_metadata = "**Version:** Journal-facing author-completion draft v15, 25 August 2026\n\n**Date:** 25 August 2026\n\n"
    if draft_metadata in text:
        text = replace_once(text, draft_metadata, "", "manuscript drafting metadata")
    text = replace_section(
        text,
        "### Ethics approval and consent to participate",
        "### Consent for publication",
        """
This secondary study used only publicly available, de-identified human transcriptomic datasets and involved no participant recruitment, intervention or collection of new specimens. No additional ethics approval was required for this secondary analysis. Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,13].
""",
    )
    text = replace_section(
        text,
        "### Availability of data and materials",
        "### Competing interests",
        f"""
The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [14-16]. Version-controlled analysis code, machine-readable decisions, derived source-data tables and SHA-256 provenance records are available at https://github.com/1209433622cz-maker/sle-bcell-remodeling and in the immutable archive at doi:{doi} [17]. Original project code is licensed under the MIT License; original manuscript text, composite figures, project documentation and project-generated derived source-data tables are licensed under CC BY 4.0. These licences do not relicense GEO, CELLxGENE or other third-party source material. Large recomputable matrices are not duplicated from their source repositories.
""",
    )
    text = replace_section(
        text,
        "### Competing interests",
        "### Funding",
        "The authors declare that they have no competing interests.",
    )
    text = replace_section(
        text,
        "### Funding",
        "### Authors' contributions",
        "This research received no specific funding.",
    )
    text = replace_section(
        text,
        "### Authors' contributions",
        "### Acknowledgements",
        """
ZC: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - original draft. TQ: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing. Both authors read and approved the final manuscript, supplementary information, figures, source data and cover letter.
""",
    )
    text = replace_section(
        text,
        "### Acknowledgements",
        "## Additional files",
        """
Not applicable.

### Use of generative artificial intelligence

Generative artificial intelligence tools, including OpenAI Codex and ChatGPT, were used to assist with code development, reproducibility checks, language editing and preparation of submission materials. The authors reviewed and verified the analyses, code, text, references, figures and source data, take full responsibility for the submitted work, and did not use generative artificial intelligence to create or alter primary research data.
""",
    )
    old_legend = "**a,** Audited GSE174188 hierarchy, hard-quality-control retention and separation of disease-blind identity reconstruction from sample-level outcome inference. **b,** Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 resamples; policies are discrete alternatives and are not connected as a trajectory. **c,** Mapped adjusted Rand index and mapping agreement in each two-compartment resampling run. **d,** Minimum and median state Jaccard indices for `B_CONV` and `B_ASC`, with frozen antibody-secreting marker support. Cell-level summaries define identity stability and are not disease replicates."
    new_legend = "**a,** Audited GSE174188 hierarchy, hard-quality-control retention and separation of disease-blind identity reconstruction from sample-level outcome inference. **b,** Median mapped adjusted Rand index and minimum-to-median interval for each candidate identity policy across 20 resamples; policies are discrete alternatives and are not connected as a trajectory. The short dashed segment applies only to the two-compartment minimum-ARI criterion of 0.90. **c,** Mapped adjusted Rand index and mapping agreement in each two-compartment resampling run; the dashed horizontal guide marks the minimum mapped-ARI criterion of 0.990. **d,** Minimum and median state Jaccard indices for `B_CONV` and `B_ASC`, with frozen antibody-secreting marker support; the dashed vertical guide marks the minimum state-median Jaccard criterion of 0.95. Cell-level summaries define identity stability and are not disease replicates."
    if old_legend in text:
        text = replace_once(text, old_legend, new_legend, "Figure 1 legend")
    old_reference = "17. SLE B-cell remodeling analysis repository. GitHub. https://github.com/1209433622cz-maker/sle-bcell-remodeling. Accessed 21 Aug 2026."
    new_reference = f"17. Chen Z, Qi T. SLE B-cell remodeling analysis: code, source data and reproducible release. Zenodo. 2026. doi:{doi}."
    if old_reference in text:
        text = replace_once(text, old_reference, new_reference, "release reference")
    elif new_reference not in text:
        raise RuntimeError("Final release reference is absent or inconsistent")

    abstract = text[text.index("## Abstract") + len("## Abstract") : text.index("## Keywords")]
    references = [
        int(value)
        for value in re.findall(
            r"^(\d+)\.\s", text[text.index("## References") :], flags=re.M
        )
    ]
    if text.count("[[") != 0:
        raise RuntimeError("Final manuscript still contains placeholders")
    if references != list(range(1, 33)):
        raise RuntimeError("Final manuscript reference sequence changed")
    if word_count(abstract) > 350:
        raise RuntimeError("Final abstract exceeds 350 words")
    if text.count(doi) < 2:
        raise RuntimeError("DOI is not present in availability and reference list")
    return text, word_count(abstract)


def build_supplement(doi: str) -> str:
    text = SOURCE_SUPPLEMENT.read_text(encoding="utf-8-sig")
    draft_metadata = "**Version:** Submission draft, 25 August 2026\n\n"
    if draft_metadata in text:
        text = replace_once(text, draft_metadata, "", "supplement drafting metadata")
    pending_release = "| Immutable release | Final archive DOI will be inserted in the main manuscript availability statement after author approval |"
    final_release = f"| Immutable archive | Zenodo doi:{doi} |"
    if pending_release in text:
        text = replace_once(text, pending_release, final_release, "supplement release record")
    elif final_release not in text:
        raise RuntimeError("Final supplement release record is absent or inconsistent")
    if text.count("[[") != 9 or text.count("[[SUPPLEMENTARY_FIGURE:S") != 9:
        raise RuntimeError("Supplement contains unexpected placeholders")
    return text


def build_cover(doi: str) -> str:
    text = SOURCE_COVER.read_text(encoding="utf-8-sig")
    pending_release = "The submission includes five 600-dpi main figures, seven supplementary figures, machine-readable source data, a complete statistical-results archive, supplementary information and a separate six-test regulator-sensitivity attachment. [[PRE-SUBMISSION ACTION REQUIRED: insert immutable archive DOI and licence information.]]"
    previous_release = f"The submission includes five vector main figures rendered at 170 mm with 600-dpi PNG companions, seven supplementary figures, machine-readable source data, a complete statistical-results archive, supplementary information and a separate six-test regulator-sensitivity attachment. The versioned release is archived at doi:{doi}. Original project code is MIT-licensed; original manuscript text, composite figures, documentation and project-generated derived source-data tables are available under CC BY 4.0, without relicensing third-party datasets."
    previous_final_release = f"The submission includes five vector main figures rendered at 170 mm with 600-dpi PNG companions, eight supplementary figures, machine-readable source data, a complete statistical-results archive, supplementary information and a regulator-sensitivity attachment containing baseline and prespecified overlap-depletion analyses. The archived release is available at doi:{doi}. Original project code is MIT-licensed; original manuscript text, composite figures, documentation and project-generated derived source-data tables are available under CC BY 4.0, without relicensing third-party datasets."
    final_release = f"The submission includes five vector main figures rendered at 170 mm with 600-dpi PNG companions, nine supplementary figures, machine-readable source data, a complete statistical-results archive including end-to-end identity robustness, supplementary information and a regulator-sensitivity attachment containing baseline and prespecified overlap-depletion analyses. The archived release is available at doi:{doi}. Original project code is MIT-licensed; original manuscript text, composite figures, documentation and project-generated derived source-data tables are available under CC BY 4.0, without relicensing third-party datasets."
    if pending_release in text:
        text = replace_once(text, pending_release, final_release, "cover release statement")
    elif previous_release in text:
        text = replace_once(text, previous_release, final_release, "cover release statement")
    elif previous_final_release in text:
        text = replace_once(text, previous_final_release, final_release, "cover release statement")
    elif final_release not in text:
        raise RuntimeError("Final cover release statement is absent or inconsistent")

    pending_confirmation = "[[AUTHOR CONFIRMATION REQUIRED: confirm that all authors approved the manuscript and its submission; that the work has not been published and is not under consideration elsewhere; and disclose any policy issues or competing interests.]]"
    final_confirmation = "Both authors approved the manuscript, supplementary information, figures, source data, cover letter and submission. The work is original, is submitted exclusively to Genome Medicine and is not under consideration by another journal. The authors declare no competing interests and no specific funding. The manuscript transparently discloses the authors' reviewed use of generative artificial intelligence assistance."
    if pending_confirmation in text:
        text = replace_once(text, pending_confirmation, final_confirmation, "cover author confirmation")
    elif final_confirmation not in text:
        raise RuntimeError("Final cover author confirmation is absent or inconsistent")

    overlap_sentence = "Post-freeze depletion of either the frozen 12-gene arm or the broader M5911 set preserved every method-level direction, while transparently exposing substantial attenuation of the low-coverage discovery STAT2 model after broad depletion."
    if overlap_sentence not in text:
        anchor = "Orthogonal enrichment of the independently curated M5911 response set"
        text = replace_once(text, anchor, overlap_sentence + " " + anchor, "cover overlap-depletion summary")
    if "[[" in text or doi not in text:
        raise RuntimeError("Final cover letter contract failed")
    return text


def author_record(doi: str) -> str:
    return f"""# Final author and release confirmation record

**Recorded:** 25 August 2026

**Release DOI:** `{doi}`

## Authors and correspondence

- [x] Complete author order: Zhi Chen, first author; Teng Qi, corresponding author.
- [x] Both authors are MSc students in Bioinformatics, School of Medicine, The Chinese University of Hong Kong, Shenzhen.
- [x] Emails and ORCIDs match the manuscript.
- [x] Correspondence address: MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China.

## Author-controlled declarations

- [x] No additional ethics approval was required for this secondary analysis of public de-identified data.
- [x] No identifiable individual information appears in the submission files.
- [x] Both authors declare no competing interests.
- [x] The research received no specific funding.
- [x] CRediT roles are conservatively mapped to documented contributions without inferring supervision.
- [x] Acknowledgements: Not applicable.
- [x] Both authors approved the manuscript, supplementary information, figures, source data, cover letter and submission.
- [x] Both authors confirm originality, exclusive submission and no concurrent journal review.
- [x] Both authors approve public disclosure of generative artificial intelligence assistance.

## Licence and release

- [x] Original code: MIT License.
- [x] Original text, composite figures, documentation and project-generated derived source-data tables: CC BY 4.0.
- [x] GEO, CELLxGENE and other third-party source material is explicitly excluded from project relicensing.
- [x] Public source UUID provenance and privacy audit passed.
- [x] Persistent DOI: `https://doi.org/{doi}`.

## APC handling

- [x] Springer Nature lists The Chinese University of Hong Kong as participating in a Hong Kong open-access agreement. Eligibility for the Shenzhen affiliation and corresponding-author account must still be confirmed in the submission portal or with the institutional library; this record does not assert a guaranteed APC waiver.
"""


def reporting_checklist(doi: str) -> str:
    return f"""# Genome Medicine final reporting and release checklist

## Scientific freeze

- [x] Primary scientific families remain frozen; the declared post-freeze STAT1/STAT2 overlap-depletion sensitivity does not replace them.
- [x] Main panel-data assertions pass 46/46.
- [x] Legacy supplementary-figure panel-data assertions pass 29/29; Supplementary Figures S8 and S9 have separate verified 36-row and 128-row source-data contracts.
- [x] End-to-end identity reconstruction completed 20/20 replicates and retained its formal B_ASC-specific HOLD at the unchanged state-overlap criterion.
- [x] Boundary-exchange propagation retained the primary composition null and both tested GSE174188 B_CONV IFN/ISG effects.
- [x] No new cohort, cluster, primary threshold, regulator or signature was selected; depletion used two prespecified frozen gene sets and identity propagation reused frozen models.
- [x] Primary B_ASC composition remains a null boundary.
- [x] Central claim remains independently replicated IFN/ISG remodeling within broad B_CONV.

## Final publication engineering

- [x] Figures 1-5 were rerendered at exactly 170 mm, with vector PDFs, 600-dpi PNGs, 5-7 pt text and 8 pt panel labels; Figures 1a and 5a encode evidence hierarchy without causal ordering.
- [x] Figure 1 Source Data removes only two non-plotted internal gate-decision rows; plotted rows are unchanged.
- [x] Figure 1 threshold guides are explicitly defined.
- [x] Figure 2 UUID provenance and privacy audit passed.
- [x] Supplementary Table S7 starts on a new page.
- [x] Portal REQUIRED and OPTIONAL upload maps are separate.
- [x] Manuscript and cover letter contain zero placeholders.

## Declarations and release

- [x] Ethics, consent, competing interests, funding, contributions, acknowledgements and AI-use statements are complete.
- [x] Both authors approved every submission component and confirmed originality and exclusive submission.
- [x] Repository licence scope excludes third-party public data.
- [x] Release DOI: `https://doi.org/{doi}`.
- [x] Deterministic ZIP rebuild, WPS all-page review and accessibility audit are required to pass before journal upload.
"""


def validate_readme(doi: str) -> None:
    text = README.read_text(encoding="utf-8-sig")
    required = (
        "01_manuscript/Manuscript.md",
        "01_manuscript/Supplementary_Information.md",
        "04_submission/journal_submission/",
        doi,
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise RuntimeError(f"README is missing current submission pointers: {missing}")


def citation_cff(doi: str) -> str:
    return f"""cff-version: 1.2.0
message: "If you use this software or its derived source data, please cite the archived release."
title: "SLE B-cell remodeling analysis: code, source data and reproducible release"
type: software
version: 1.0.0
date-released: 2026-08-25
doi: "{doi}"
repository-code: "https://github.com/1209433622cz-maker/sle-bcell-remodeling"
license: MIT
authors:
  - family-names: Chen
    given-names: Zhi
    orcid: "https://orcid.org/0009-0001-0072-5576"
    affiliation: "School of Medicine, The Chinese University of Hong Kong, Shenzhen"
  - family-names: Qi
    given-names: Teng
    orcid: "https://orcid.org/0009-0007-7648-4776"
    affiliation: "School of Medicine, The Chinese University of Hong Kong, Shenzhen"
preferred-citation:
  type: generic
  title: "SLE B-cell remodeling analysis: code, source data and reproducible release"
  year: 2026
  doi: "{doi}"
  authors:
    - family-names: Chen
      given-names: Zhi
    - family-names: Qi
      given-names: Teng
"""


def zenodo_metadata(doi: str) -> dict[str, object]:
    return {
        "title": "SLE B-cell remodeling analysis: code, source data and reproducible release",
        "upload_type": "software",
        "publication_date": "2026-08-25",
        "version": "1.0.0",
        "doi": doi,
        "description": (
            "Author-approved reproducible release supporting a disease-blind single-cell "
            "analysis of B-cell remodeling in systemic lupus erythematosus. The archive "
            "contains versioned code, publication figures, derived source data, statistical "
            "results, manuscript materials and integrity records."
        ),
        "creators": [
            {
                "name": "Chen, Zhi",
                "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
                "orcid": "0009-0001-0072-5576",
            },
            {
                "name": "Qi, Teng",
                "affiliation": "School of Medicine, The Chinese University of Hong Kong, Shenzhen",
                "orcid": "0009-0007-7648-4776",
            },
        ],
        "keywords": [
            "systemic lupus erythematosus",
            "B cells",
            "single-cell RNA sequencing",
            "pseudobulk",
            "interferon",
            "reproducibility",
        ],
        "licenses": ["MIT", "CC-BY-4.0"],
        "related_identifiers": [
            {
                "identifier": "https://github.com/1209433622cz-maker/sle-bcell-remodeling",
                "relation": "isSupplementTo",
                "resource_type": "software",
            }
        ],
        "language": "eng",
        "access_right": "open",
    }


def main() -> None:
    args = parse_args()
    doi = validate_doi(args.doi)
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    manuscript, abstract_words = build_manuscript(doi)
    supplement = build_supplement(doi)
    cover = build_cover(doi)
    MANUSCRIPT.write_text(manuscript, encoding="utf-8", newline="\n")
    SUPPLEMENT.write_text(supplement, encoding="utf-8", newline="\n")
    COVER.write_text(cover, encoding="utf-8", newline="\n")
    AUTHOR_RECORD.write_text(author_record(doi), encoding="utf-8", newline="\n")
    CHECKLIST.write_text(reporting_checklist(doi), encoding="utf-8", newline="\n")
    metadata = zenodo_metadata(doi)
    ZENODO_METADATA.write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    validate_readme(doi)
    CITATION.write_text(citation_cff(doi), encoding="utf-8", newline="\n")

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BRF_AUTHOR_APPROVED_ZERO_PLACEHOLDER_SOURCES_BUILT",
        "doi": doi,
        "abstract_words": abstract_words,
        "references": 32,
        "manuscript_placeholders": manuscript.count("[["),
        "cover_placeholders": cover.count("[["),
        "supplement_embedding_markers": supplement.count("[[SUPPLEMENTARY_FIGURE:S"),
        "ethics_approval_required": False,
        "competing_interests": False,
        "specific_funding": False,
        "acknowledgements": "Not applicable",
        "all_author_approval": True,
        "originality_and_exclusive_submission": True,
        "generative_ai_disclosure_approved": True,
        "licences": ["MIT", "CC-BY-4.0"],
        "third_party_data_relicensed": False,
        "outputs": [
            path.relative_to(ROOT).as_posix()
            for path in (
                MANUSCRIPT,
                SUPPLEMENT,
                COVER,
                AUTHOR_RECORD,
                CHECKLIST,
                ZENODO_METADATA,
                CITATION,
            )
        ],
    }
    (RUN_DIR / "04_SOURCE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
