"""Build npj SBA manuscript, supplement and administrative sources from frozen text."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_MANUSCRIPT = ROOT / "04_submission/zenodo_release/manuscript/Manuscript.md"
BASE_SUPPLEMENT = ROOT / "01_manuscript/Supplementary_Information.md"
RUN = ROOT / "phase17_v7/npj_sba_target_refreeze/20260830_target_specific_refreeze"
SOURCES = RUN / "sources"
MANAGEMENT = ROOT / "00_project_management/npj_sba_target_refreeze_2026-08-30"
TITLE = (
    "Disease-blind reconstruction distinguishes reproducible interferon remodeling from unstable B-cell state assignments "
    "in systemic lupus erythematosus"
)
ABSTRACT = (
    "Single-cell disease studies can conflate cell identity, abundance and transcription when unstable annotations are treated "
    "as fixed biological states. We reanalysed public systemic lupus erythematosus datasets using disease-blind B-lineage "
    "reconstruction and donor-aware inference. Among 150,402 discovery B-lineage cells, end-to-end resampling failed a "
    "prespecified antibody-secreting-cell overlap criterion, restricting broad B-cell compartments to an analysis scaffold, yet "
    "propagation of observed assignment exchanges preserved the primary composition null and conventional-B IFN/ISG effect. "
    "The IFN/ISG program replicated in independent GSE135779 childhood donors using a source-label-defined broad B-cell analogue "
    "despite weak genome-wide concordance. Corrected source-label-independent remapping failed prespecified calibration, so no "
    "corrected external disease effect was estimated. STAT1/STAT2 analyses provided convergent but observational support and "
    "weakened after broader interferon-gene depletion. These results separate reproducible process-level interferon remodeling "
    "from less stable hard state assignments without establishing a universal B-cell taxonomy, causal regulator or clinical utility."
)
R1_HOLD = "HOLD_FULL_PIPELINE_TWO_COMPARTMENT_REPRODUCIBILITY"
C9R_HOLD = "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
DOI = "10.5281/zenodo.22151739"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text)
    if not match:
        raise ValueError(f"Missing section: {heading}")
    return match.group(1).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w/-]+\b", text))


def nature_references(reference_text: str) -> str:
    journal_abbrev = {
        "Nature Immunology": "Nat. Immunol.", "Arthritis & Rheumatology": "Arthritis Rheumatol.",
        "Nature Communications": "Nat. Commun.", "Journal of Autoimmunity": "J. Autoimmun.",
        "Genome Medicine": "Genome Med.", "Frontiers in Immunology": "Front. Immunol.",
        "The Journal of Immunology": "J. Immunol.", "Lupus Science & Medicine": "Lupus Sci. Med.",
        "Genome Biology": "Genome Biol.", "Nature Methods": "Nat. Methods", "Scientific Reports": "Sci. Rep.",
        "Bioinformatics Advances": "Bioinform. Adv.", "Nucleic Acids Research": "Nucleic Acids Res.",
        "Cell Systems": "Cell Syst.",
    }
    blocks = re.findall(r"(?ms)^\d+\.\s+(.*?)(?=\n\n\d+\.|\Z)", reference_text.strip())
    if len(blocks) != 32:
        raise ValueError(f"Expected 32 references, found {len(blocks)}")
    output = []
    for number, raw in enumerate(blocks, 1):
        raw = " ".join(raw.split())
        if raw.startswith("National Center for Biotechnology Information."):
            match = re.fullmatch(
                r"National Center for Biotechnology Information\. (.+?)\. (https://\S+)\. Accessed (.+?)\.", raw
            )
            if not match:
                raise ValueError(f"Cannot parse GEO reference {number}")
            formatted = f"National Center for Biotechnology Information. {match.group(1)}. {match.group(2)} (accessed {match.group(3)})."
        elif number == 32:
            formatted = (
                "Chen, Z. & Qi, T. SLE B-cell remodeling analysis: code, source data and reproducible release. "
                f"Zenodo https://doi.org/{DOI} (2026)."
            )
        else:
            match = re.fullmatch(r"(.+?)\. (.+?)\. ([^.]+)\. (\d{4});([^:]+):(.+?)\. doi:(\S+)\.", raw)
            if not match:
                raise ValueError(f"Cannot parse article reference {number}: {raw}")
            authors, title, journal, year, volume, pages, doi = match.groups()
            author_parts = [item.strip() for item in authors.replace(", et al", ", et al.").split(", ")]
            has_et_al = "et al." in authors
            first = author_parts[0]
            surname, initials = first.rsplit(" ", 1)
            initials = " ".join(char + "." for char in initials.replace("-", ""))
            if has_et_al or len(author_parts) > 5:
                author_text = f"{surname}, {initials} et al."
            else:
                converted = []
                for part in author_parts:
                    person_surname, person_initials = part.rsplit(" ", 1)
                    converted.append(f"{person_surname}, {' '.join(char + '.' for char in person_initials.replace('-', ''))}")
                author_text = ", ".join(converted[:-1]) + " & " + converted[-1] if len(converted) > 1 else converted[0]
            journal = journal_abbrev.get(journal, journal)
            volume = re.sub(r"\([^)]*\)", "", volume)
            formatted = f"{author_text} {title}. {journal} **{volume}**, {pages} ({year}). https://doi.org/{doi}."
        output.append(f"{number}. {formatted}")
    return "\n\n".join(output)


def build_manuscript(base: str) -> str:
    introduction = section(base, "Background")
    methods = section(base, "Methods").replace("Additional file 4", "Supplementary Data 3")
    results = section(base, "Results")
    discussion = section(base, "Discussion")
    conclusion = section(base, "Conclusions")
    legends = section(base, "Figure legends")
    references = nature_references(section(base, "References"))
    ethics = section(section(base, "Declarations"), "Ethics approval and consent to participate") if False else (
        "This secondary study used only publicly available, de-identified human transcriptomic datasets and involved no participant "
        "recruitment, intervention or collection of new specimens. No additional ethics approval was required for this secondary "
        "analysis. Ethics approval and consent procedures for the source studies are reported in the original publications [1,2,19]. "
        "Consent for publication was not applicable because no identifiable participant information was used."
    )
    data = (
        "The datasets analysed are publicly available through NCBI GEO under GSE174188, GSE135779 and GSE23307 [17,18,20]. "
        "Project-generated figure source data and complete statistical results are included as Supplementary Data 1-3 and in the "
        f"version-specific reproducibility archive at https://doi.org/{DOI} [32]. Large recomputable matrices are not duplicated from "
        "their source repositories. Third-party GEO and CELLxGENE data remain subject to their source terms."
    )
    code = (
        "Analysis code, executable decision records, environment specifications and restoration instructions are available at "
        "https://github.com/1209433622cz-maker/sle-bcell-remodeling (release v1.1.0; frozen scientific content commit "
        f"f1859ff8498d5569a1d5027b36ed18c8b7c7536f) and are archived at https://doi.org/{DOI} [32]. Original project code is "
        "licensed under the MIT License."
    )
    contributions = (
        "Z.C.: Conceptualization, Data curation, Formal analysis, Investigation, Methodology, Software, Visualization, Writing - "
        "original draft. T.Q.: Conceptualization, Methodology, Project administration, Validation, Writing - review and editing."
    )
    text = f"""# {TITLE}

Article type: Article

Authors: Zhi Chen [1] and Teng Qi [1,*]

Affiliation 1: School of Medicine, The Chinese University of Hong Kong, Shenzhen, Shenzhen 518172, China

Corresponding author: Teng Qi, School of Medicine, The Chinese University of Hong Kong, Shenzhen, MED Start-up Building, 2001 Longxiang Boulevard, Longgang District, Shenzhen 518172, China; tengqi@link.cuhk.edu.cn

ORCID identifiers: Zhi Chen, https://orcid.org/0009-0001-0072-5576; Teng Qi, https://orcid.org/0009-0007-7648-4776

Author emails: Zhi Chen, zhichen1@link.cuhk.edu.cn; Teng Qi, tengqi@link.cuhk.edu.cn

Running title: Replicated IFN remodeling in SLE B cells

## Abstract

{ABSTRACT}

## Introduction

{introduction}

## Results

{results}

## Discussion

{discussion}

{conclusion}

## Methods

{methods}

### Ethics and consent

{ethics}

## Data availability

{data}

## Code availability

{code}

## Acknowledgements

This study received no funding.

## Author contributions

{contributions}

## Competing interests

The authors declare no competing interests.

## References

{references}

## Figure legends

{legends}
"""
    return text.replace("## Background", "## Introduction").strip() + "\n"


def build_supplement(base: str) -> str:
    start = base.index("## Supplementary Table S1")
    retained = base[start:]
    retained = retained.replace("Figure Source Data additional file", "Supplementary Data 1")
    retained = retained.replace("Full Statistical Results additional file", "Supplementary Data 3")
    retained = retained.replace("Regulator Sensitivity additional file", "Supplementary Data 2")
    old = (
        "| Initial immutable archive | Zenodo doi:10.5281/zenodo.22086892; predates post-freeze robustness and correction; "
        "a matching updated archive is required before submission |"
    )
    new = f"| Version-specific archive | Zenodo https://doi.org/{DOI}; matches the frozen manuscript, figures and statistical outputs |"
    retained = retained.replace(old, new)
    return f"""# Supplementary information

## {TITLE}

**Authors:** Zhi Chen and Teng Qi

## Supplementary overview

This single Supplementary Information file contains Tables S1-S9 and Figures S1-S10 supporting the main Article. All analytical methods required to interpret the work are reported in the main manuscript. Machine-readable figure source data, regulator sensitivity results and complete statistical outputs are supplied separately as Supplementary Data 1-3. Original external-mapping sensitivity outcomes are superseded, and no corrected disease effect was estimated after calibration failed.

{retained.strip()}
"""


def cover_letter() -> str:
    return f"""# Cover letter

30 August 2026

Editors  
npj Systems Biology and Applications

Dear Editors,

Please consider our Article, \"{TITLE}\", for publication in npj Systems Biology and Applications.

The manuscript addresses a systems-biology problem that is central to single-cell disease research: whether conclusions remain stable when cell identity, composition and transcription are treated as distinct inferential layers. Using public systemic lupus erythematosus datasets, we combined disease-blind B-lineage reconstruction, biological-unit-aware inference, end-to-end assignment sensitivity and independent source-label-defined replication. The analysis preserves two prespecified negative gates rather than tuning them away: the broad B-cell partition remains an analysis scaffold after an antibody-secreting-cell overlap criterion failed, and corrected source-label-independent external remapping did not qualify for disease-effect estimation.

The main contribution is therefore an evidence hierarchy. Hard state assignments have explicit reproducibility and transfer limits, whereas a prespecified IFN/ISG process-level signal persists through uncertainty propagation and independent donor-level replication. This focus aligns with the journal's scope in single-cell systems biology, systems immunology and computational analysis of complex disease systems. Regulatory analyses provide convergent but observational context and are not presented as causal proof.

All analysed datasets are publicly available. Code, decision records, figure source data and complete statistical outputs are available through GitHub and the version-specific archive at https://doi.org/{DOI}. The work is original, is not under consideration elsewhere, and the authors declare no competing interests.

Thank you for your consideration.

Sincerely,

Teng Qi  
Corresponding author  
School of Medicine, The Chinese University of Hong Kong, Shenzhen  
tengqi@link.cuhk.edu.cn  
ORCID: https://orcid.org/0009-0007-7648-4776
"""


def reporting_summary() -> str:
    return f"""# Nature Portfolio Reporting Summary draft

Status: `DRAFT_FOR_PORTAL_FORM_TRANSCRIPTION_AND_AUTHOR_REVIEW`

## Study design

- Secondary analysis of publicly available, de-identified human transcriptomic data.
- Discovery: GSE174188; independent source-label-defined replication: GSE135779; descriptive perturbational context: GSE23307.
- Disease fields were protected during B-lineage identity reconstruction.
- Biological units were sample-by-processing-cohort strata for GSE174188 and donors for GSE135779.

## Replication and robustness

- Twenty within-library frozen-representation resamples and twenty end-to-end reconstruction resamples.
- R1 decision retained as `{R1_HOLD}`; no threshold or seed rescue.
- C9R decision retained as `{C9R_HOLD}`; no corrected external disease effect estimated.
- Assignment exchanges were propagated through frozen composition and IFN/ISG models as same-data sensitivity analyses.

## Statistical reporting

- Exact tests, biological units, sidedness, multiplicity families, sample sizes, P values, q values and confidence intervals are indexed in `npj_statistics_reporting_map.csv`.
- No inferential P value was calculated for GSE23307 at n=2 donors.
- No cells or donors were excluded after outcome inspection; all eligibility rules are described in Methods and executable decision records.

## Data and code

- GEO accessions: GSE174188, GSE135779 and GSE23307.
- Code: https://github.com/1209433622cz-maker/sle-bcell-remodeling
- Frozen reproducibility archive: https://doi.org/{DOI}

## Software

Pinned environments and package versions are recorded in `REPRODUCIBILITY.md` and the archived environment files. This draft must be transcribed into the journal's current portal form and checked by both authors before submission.
"""


def editorial_checklist() -> str:
    return f"""# npj Systems Biology and Applications editorial policy checklist draft

Status: `TECHNICAL_DRAFT_EXACT_FILE_AUTHOR_APPROVAL_REQUIRED`

- [x] Article title is 15 words and contains no punctuation.
- [x] Abstract is unstructured and no more than 150 words.
- [x] Introduction has no subheadings.
- [x] Results uses subheadings.
- [x] Discussion has no subheadings and no separate Conclusions section.
- [x] All analytical Methods are in the main manuscript.
- [x] Data availability and Code availability are separate sections after Methods.
- [x] Funding is stated in Acknowledgements; no separate Funding section.
- [x] Author contributions and competing interests are present.
- [x] Generative-AI assistance is disclosed in Methods.
- [x] Supplementary Information is one merged file and contains no Supplementary Methods.
- [x] Five main and ten supplementary figures are source-rerendered under the npj style contract.
- [x] R1 remains `{R1_HOLD}`.
- [x] C9R remains `{C9R_HOLD}` and corrected external outcome unlock remains false.
- [ ] Current official JCR Q1 profile archived by the institution.
- [ ] CUHK-Shenzhen APC/OA eligibility confirmed by the institution.
- [ ] Exact manuscript, supplement, figures, cover letter and package hashes approved by both authors.
- [ ] Portal upload and submission explicitly authorized.
- [ ] APC commitment explicitly authorized.
"""


def statistics_map() -> list[dict[str, str]]:
    return [
        {"claim_id":"R1","location":"Results 1; Fig. 1; Fig. S9","claim":"End-to-end broad-state reproducibility criterion held","unit_n":"150,402 cells; 20 resamples","test":"Prespecified ARI/agreement/Jaccard thresholds","sidedness":"not tested","p_value":"NA","q_value":"NA","confidence_interval":"NA","multiplicity":"five fixed criteria","decision":R1_HOLD,"source":"phase17_v7/round6_q1_robustness/20260827_r1_hold_integration/06_AUDIT_AND_PROPAGATION_PREP_STATUS.json"},
        {"claim_id":"C3_PRIMARY","location":"Results 2; Fig. 2","claim":"Primary B_ASC composition differs in managed SLE","unit_n":"43 controls; 47 SLE sample-cohort strata","test":"Beta-binomial Wald","sidedness":"two-sided","p_value":"0.787","q_value":"0.787","confidence_interval":"OR 0.636-1.410","multiplicity":"BH across three frozen base contrasts","decision":"NOT_SUPPORTED","source":"phase17_v7/gateC3A/20260815_frozen_abundance/09_GATE_C3A_ADVISOR_DECISION.json"},
        {"claim_id":"C4_IFN_PRIMARY","location":"Results 3; Fig. 3","claim":"GSE174188 primary B_CONV IFN/ISG program is higher in SLE","unit_n":"89 pseudobulk strata","test":"OLS with HC3 covariance","sidedness":"two-sided","p_value":"7.33e-07","q_value":"2.98e-06","confidence_interval":"0.525-1.148","multiplicity":"BH across four frozen programs","decision":"SUPPORTED","source":"phase17_v7/gateC4B/20260815_edger_transcription/15_GATE_C4B_ADVISOR_DECISION.json"},
        {"claim_id":"C4_IFN_NONOVERLAP","location":"Results 3; Fig. 3","claim":"Donor-nonoverlap internal IFN/ISG effect is positive","unit_n":"54 pseudobulk strata","test":"OLS with HC3 covariance","sidedness":"two-sided","p_value":"9.01e-05","q_value":"3.61e-04","confidence_interval":"0.573-1.599","multiplicity":"BH across four frozen programs","decision":"SUPPORTED_INTERNAL","source":"phase17_v7/gateC4B/20260815_edger_transcription/15_GATE_C4B_ADVISOR_DECISION.json"},
        {"claim_id":"C5_IFN_CHILD","location":"Results 4; Fig. 4","claim":"GSE135779 childhood IFN/ISG program replicates","unit_n":"11 controls; 32 SLE donors","test":"OLS with HC3 covariance","sidedness":"two-sided","p_value":"7.45e-07","q_value":"2.98e-06","confidence_interval":"0.681-1.402","multiplicity":"BH across four frozen programs","decision":"SUPPORTED_INDEPENDENT_SOURCE_LABEL_DEFINED","source":"phase17_v7/gateC5B/20260815_gse135779_external_validation/17_GATE_C5B_ADVISOR_DECISION.json"},
        {"claim_id":"C5_GENOMEWIDE","location":"Results 4; Fig. 4","claim":"Genome-wide effects agree across datasets","unit_n":"4,410 shared tested genes","test":"Spearman correlation","sidedness":"descriptive","p_value":"NA","q_value":"NA","confidence_interval":"NA","multiplicity":"none","decision":"WEAK_RHO_0.026","source":"phase17_v7/gateC5B/20260815_gse135779_external_validation/17_GATE_C5B_ADVISOR_DECISION.json"},
        {"claim_id":"C9R","location":"Results 5; Fig. S10","claim":"Corrected source-label-independent mapper qualifies for outcome estimation","unit_n":"258 reference donors; 56 external matrices","test":"Prespecified coverage and per-state precision calibration","sidedness":"not tested","p_value":"NA","q_value":"NA","confidence_interval":"NA","multiplicity":"fixed calibration family","decision":C9R_HOLD,"source":"phase17_v7/gateC9R/20260828_corrected_external_mapping/15_GATE_C9A_PREFREEZE_DECISION.json"},
        {"claim_id":"TF_ULM","location":"Results 6; Fig. 5","claim":"STAT1/STAT2 slopes are positive across three contrasts","unit_n":"6 regulator-by-contrast tests","test":"Signed-target slope t test","sidedness":"two-sided","p_value":"see Supplementary Data 2","q_value":"global 24-test BH","confidence_interval":"see Supplementary Data 2","multiplicity":"BH across 24 tests","decision":"CONVERGENT_OBSERVATIONAL","source":"phase17_v7/gateC5B/20260815_gse135779_external_validation/regulatory"},
        {"claim_id":"TF_CORRELATED","location":"Results 6; Table S4; Fig. S7","claim":"Correlation-aware STAT1/STAT2 direction is retained","unit_n":"6 tests per method","test":"CAMERA and FRY","sidedness":"positive-direction","p_value":"see Supplementary Data 2","q_value":"CAMERA 5/6; FRY 6/6 q<0.05","confidence_interval":"NA","multiplicity":"separate BH family of six per method","decision":"SUPPORTED_WITH_DISCOVERY_STAT2_EXCEPTION","source":"phase17_v7/gateC6B/20260819_regulatory_sensitivity"},
        {"claim_id":"TF_DEPLETION","location":"Results 6; Table S4B; Fig. S8","claim":"STAT1/STAT2 evidence is overlap-independent","unit_n":"6 tests per branch and method","test":"ULM, CAMERA and FRY after fixed depletion","sidedness":"two-sided ULM; positive CAMERA/FRY","p_value":"see Supplementary Data 2","q_value":"branch-specific BH","confidence_interval":"see Supplementary Data 2","multiplicity":"six tests per branch and method","decision":"NOT_SUPPORTED_FOR_BROAD_M5911_INDEPENDENCE","source":"phase17_v7/round6_q1_robustness/20260825_overlap_depletion/01_OVERLAP_DEPLETION_RESULTS.csv"},
        {"claim_id":"M5911","location":"Results 6; Fig. 5","claim":"M5911 is positively enriched in three contrasts","unit_n":"3 ranked contrasts","test":"10,000-permutation preranked test","sidedness":"positive-direction","p_value":"see Supplementary Data 3","q_value":"descriptive BH across three contrasts","confidence_interval":"NA","multiplicity":"three contrasts","decision":"ORTHOGONAL_RESPONSE_SUPPORT","source":"phase17_v7/gateC5B/20260815_gse135779_external_validation/orthogonal"},
        {"claim_id":"GSE23307","location":"Results 6; Fig. 5","claim":"IFN-beta increases the 12-gene arm","unit_n":"2 healthy donors","test":"Mean paired log2(x+1) difference","sidedness":"not tested","p_value":"NA","q_value":"NA","confidence_interval":"NA","multiplicity":"none","decision":"DESCRIPTIVE_ONLY","source":"phase17_v7/gateC5B/20260815_gse135779_external_validation/orthogonal"},
    ]


def main() -> None:
    SOURCES.mkdir(parents=True, exist_ok=True)
    MANAGEMENT.mkdir(parents=True, exist_ok=True)
    manuscript = build_manuscript(BASE_MANUSCRIPT.read_text(encoding="utf-8-sig"))
    supplement = build_supplement(BASE_SUPPLEMENT.read_text(encoding="utf-8-sig"))
    if len(TITLE.split()) != 15 or word_count(ABSTRACT) > 150:
        raise RuntimeError(f"Title/abstract limits failed: {len(TITLE.split())} words; abstract {word_count(ABSTRACT)} words")
    required = [R1_HOLD, C9R_HOLD]
    # Decisions are stored in the contract and statistics map, while reader-facing text uses prose boundaries.
    for phrase in ("no corrected external disease effect was estimated", "analysis scaffold", "causal regulator"):
        if phrase.lower() not in manuscript.lower():
            raise RuntimeError(f"Required claim boundary missing: {phrase}")
    if "Supplementary Methods" in supplement or "## Conclusions" in manuscript or "## Background" in manuscript:
        raise RuntimeError("Target structure contains a prohibited legacy section")
    if manuscript.count("## Introduction") != 1 or "###" in section(manuscript, "Introduction"):
        raise RuntimeError("Introduction structure is invalid")
    if manuscript.count("## Methods") != 1 or "### Generative AI assistance" not in manuscript:
        raise RuntimeError("Methods or AI disclosure is missing")
    paths = {
        "Manuscript.md": manuscript,
        "Supplementary_Information.md": supplement,
        "Cover_Letter.md": cover_letter(),
        "Nature_Portfolio_Reporting_Summary_Draft.md": reporting_summary(),
        "Editorial_Policy_Checklist_Draft.md": editorial_checklist(),
    }
    for name, content in paths.items():
        (SOURCES / name).write_text(content.strip() + "\n", encoding="utf-8", newline="\n")
    with (RUN / "npj_statistics_reporting_map.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        rows = statistics_map()
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    status = {
        "created_at": "2026-08-30",
        "status": "PASS_NPJ_SBA_SOURCES_BUILT_SCIENCE_FROZEN",
        "selected_target": "npj Systems Biology and Applications",
        "content_type": "Article",
        "title_words": len(TITLE.split()),
        "abstract_words": word_count(ABSTRACT),
        "reference_count": 32,
        "supplementary_methods_removed": True,
        "scientific_reanalysis": False,
        "numerical_results_reselected": False,
        "R1_decision": R1_HOLD,
        "C9R_decision": C9R_HOLD,
        "corrected_external_outcome_unlock_authorized": False,
        "jcr_q1_verified": False,
        "institutional_apc_coverage_verified": False,
        "exact_file_author_approval": False,
        "submission_authorized": False,
        "apc_commitment_authorized": False,
        "inputs": {str(BASE_MANUSCRIPT.relative_to(ROOT)): sha256(BASE_MANUSCRIPT), str(BASE_SUPPLEMENT.relative_to(ROOT)): sha256(BASE_SUPPLEMENT)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in sorted(SOURCES.iterdir()) if path.is_file()},
    }
    (RUN / "00_TARGET_SOURCE_BUILD_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
