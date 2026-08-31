#!/usr/bin/env python3
"""Integrate the reference, evidence-terminology and S6 source-redraw lock."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import phase17_c8s_01_build_supplementary_figures as supplementary_figures


ROOT = Path(__file__).resolve().parents[1]
PRIOR = (
    ROOT
    / "phase17_v7/npj_sba_traceability_lock/"
    "20260831_final_scientific_object_lock"
)
PRIOR_FIGURES = (
    ROOT
    / "phase17_v7/npj_sba_scientific_presentation_freeze/"
    "20260831_reader_path_and_legend_economy/figures"
)
RUN = (
    ROOT
    / "phase17_v7/npj_sba_reference_terminology_lock/"
    "20260901_reference_terminology_s6_refreeze"
)
RECEIVED = ROOT / "00_project_management/reference_terminology_s6_refreeze_2026-09-01/received"
PACKAGE = (
    ROOT
    / "04_submission/npj_systems_biology_and_applications/"
    "SLE_Bcell_npj_Systems_Biology_and_Applications.zip"
)
PACKAGE_SHA256 = "02A3855FB1EFEAC790C1138396CF783050D0DE744D23B5B5E0C1E97875BA83A1"
S6_SOURCE_SHA256 = "A1D1DCBF9D20BA01D0022D4DA0F73A618776D34A687E764F18AB83439204DBF6"

EDGE_R_WORKFLOW_REFERENCE = (
    "25. Chen, Y., Lun, A. T. L. & Smyth, G. K. From reads to genes to pathways: "
    "differential expression analysis of RNA-Seq experiments using Rsubread and the edgeR "
    "quasi-likelihood pipeline. F1000Res. **5**, 1438 (2016). "
    "https://doi.org/10.12688/f1000research.8987.2."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"Refusing to reset path outside project root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def shift_body_citations(body: str, minimum: int = 25) -> str:
    pattern = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")

    def shift(match: re.Match[str]) -> str:
        content = re.sub(
            r"\d+",
            lambda value: str(
                int(value.group(0)) + 1
                if int(value.group(0)) >= minimum
                else int(value.group(0))
            ),
            match.group(1),
        )
        return f"[{content}]"

    return pattern.sub(shift, body)


def shift_reference_numbers(reference_block: str, minimum: int = 25) -> str:
    pattern = re.compile(r"(?m)^(\d+)\. ")

    def shift(match: re.Match[str]) -> str:
        number = int(match.group(1))
        return f"{number + 1 if number >= minimum else number}. "

    return pattern.sub(shift, reference_block)


def renumber_for_new_reference(text: str) -> str:
    reference_heading = "## References\n"
    legend_heading = "## Figure legends\n"
    if text.count(reference_heading) != 1 or text.count(legend_heading) != 1:
        raise RuntimeError("Could not isolate the references and figure legends")
    body, tail = text.split(reference_heading, 1)
    references, legends = tail.split(legend_heading, 1)
    body = shift_body_citations(body)
    references = shift_reference_numbers(references)
    return body + reference_heading + references + legend_heading + legends


def validate_reference_sequence(text: str) -> dict[str, object]:
    body, tail = text.split("## References\n", 1)
    references, _ = tail.split("## Figure legends\n", 1)
    reference_numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", references)]
    citation_numbers: list[int] = []
    first_appearance: list[int] = []
    for match in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
        numbers: list[int] = []
        for item in match.group(1).split(","):
            item = item.strip()
            if "-" in item:
                start, end = [int(value.strip()) for value in item.split("-", 1)]
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(item))
        for number in numbers:
            citation_numbers.append(number)
            if number not in first_appearance:
                first_appearance.append(number)
    expected = list(range(1, 34))
    checks = {
        "references_1_to_33_contiguous": reference_numbers == expected,
        "citations_within_1_to_33": bool(citation_numbers)
        and min(citation_numbers) == 1
        and max(citation_numbers) == 33,
        "all_references_cited": sorted(set(citation_numbers)) == expected,
        "first_appearance_1_to_33": first_appearance == expected,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Reference-sequence validation failed: {checks}")
    return {"checks": checks, "first_appearance": first_appearance}


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manuscript_source() -> tuple[Path, list[dict[str, object]], dict[str, object]]:
    source = PRIOR / "sources/Manuscript_final_scientific_lock.md"
    text = renumber_for_new_reference(source.read_text(encoding="utf-8"))
    edits: list[tuple[str, str, str]] = [
        (
            "Abstract biological-unit scope",
            "disease-blind B-lineage reconstruction and donor-aware inference",
            "disease-blind B-lineage reconstruction and biological-unit-aware inference",
        ),
        (
            "Composition internal evidence class",
            "The internal validation estimate remained below one",
            "The internal replication estimate remained below one",
        ),
        (
            "Pseudobulk group terminology",
            "comprising 43 reference and 46 SLE strata",
            "comprising 43 control and 46 source-defined managed-SLE strata",
        ),
        (
            "Internal contrast evidence class",
            "the full internal GSE174188 validation contrast",
            "the full internal GSE174188 replication contrast",
        ),
        (
            "Internal program evidence class",
            "but neither retained multiplicity-supported internal validation.",
            "but neither was multiplicity-supported in the internal replication analysis.",
        ),
        (
            "Regulator evidence ceiling",
            "Collectively, these analyses justify an IFN-centred regulatory interpretation",
            "Collectively, these analyses support an IFN-centred regulatory context",
        ),
        (
            "Limitations internal evidence class",
            "the GSE174188 donor-nonoverlap validation remains accession-internal",
            "the GSE174188 donor-nonoverlap replication remains accession-internal",
        ),
        (
            "Dataset role",
            "served as the independent SLE validation dataset",
            "served as the independent SLE replication dataset",
        ),
        (
            "Primary source-defined label",
            "processing-cohort-4 source-metadata managed SLE versus normal",
            "processing-cohort-4 source-defined managed SLE versus normal",
        ),
        (
            "Secondary source-defined label",
            "the source-metadata flare category",
            "the source-defined flare category",
        ),
        (
            "External-method heading",
            "### Source-label-defined GSE135779 validation",
            "### Source-label-defined GSE135779 replication",
        ),
        (
            "edgeR workflow citation",
            "Genes were filtered with edgeR [24] filterByExpr",
            "Genes were filtered with edgeR [24,25] filterByExpr",
        ),
        (
            "FRY implementation attribution",
            "CAMERA [30] estimated inter-gene correlation from model residuals and performed a competitive rank test, whereas FRY [31] provided a rotation-based directional test.",
            "CAMERA [30] estimated inter-gene correlation from model residuals and performed a competitive rank test, whereas FRY [28,31] provided a fast self-contained approximation to the directional mroast/ROAST gene-set test.",
        ),
        (
            "MSigDB exact title",
            "32. Liberzon, A. et al. The Molecular Signatures Database Hallmark Gene Set Collection.",
            "32. Liberzon, A. et al. The Molecular Signatures Database (MSigDB) hallmark gene set collection.",
        ),
    ]
    ledger: list[dict[str, object]] = []
    for label, old, new in edits:
        text = replace_once(text, old, new, label)
        ledger.append(
            {
                "scope": "Manuscript",
                "edit": label,
                "old_text": old,
                "new_text": new,
                "estimate_changed": False,
            }
        )

    insertion_point = (
        "24. Robinson, M. D., McCarthy, D. J. & Smyth, G. K. edgeR: a Bioconductor package "
        "for differential expression analysis of digital gene expression data. Bioinformatics **26**, "
        "139-140 (2010). https://doi.org/10.1093/bioinformatics/btp616.\n"
    )
    text = replace_once(
        text,
        insertion_point,
        insertion_point + "\n" + EDGE_R_WORKFLOW_REFERENCE + "\n",
        "edgeR workflow reference insertion",
    )
    ledger.append(
        {
            "scope": "References",
            "edit": "Add exact edgeR quasi-likelihood workflow reference",
            "old_text": "No workflow-specific reference after reference 24",
            "new_text": EDGE_R_WORKFLOW_REFERENCE,
            "estimate_changed": False,
        }
    )
    reference_validation = validate_reference_sequence(text)
    output = RUN / "sources/Manuscript_reference_terminology_s6_refreeze.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger, reference_validation


def build_supplement_source() -> tuple[Path, list[dict[str, object]]]:
    source = PRIOR / "sources/Supplementary_Information_final_scientific_lock.md"
    text = source.read_text(encoding="utf-8")
    edits = [
        (
            "Table S1 GSE174188 evidence class",
            "| GSE174188 | Discovery and internal validation |",
            "| GSE174188 | Discovery and internal replication |",
        ),
        (
            "Table S1 GSE135779 evidence class",
            "| GSE135779 | Independent SLE validation |",
            "| GSE135779 | Independent SLE replication |",
        ),
        (
            "Table S5 Figure 4 evidence class",
            "| Figure 4 | Independent GSE135779 validation and influence analyses |",
            "| Figure 4 | Source-label-defined GSE135779 replication and influence analyses |",
        ),
        (
            "Table S8 source-label terminology",
            "The original source-label-based pseudobulk effect",
            "The original source-label-defined pseudobulk effect",
        ),
        (
            "Supplementary Figure S6 title",
            "## Supplementary Figure S6 | Independent-validation diagnostics",
            "## Supplementary Figure S6 | GSE135779 replication and robustness diagnostics",
        ),
    ]
    ledger: list[dict[str, object]] = []
    for label, old, new in edits:
        text = replace_once(text, old, new, label)
        ledger.append(
            {
                "scope": "Supplementary Information",
                "edit": label,
                "old_text": old,
                "new_text": new,
                "estimate_changed": False,
            }
        )
    output = RUN / "sources/Supplementary_Information_reference_terminology_s6_refreeze.md"
    output.write_text(text, encoding="utf-8", newline="\n")
    return output, ledger


def rebuild_s6() -> tuple[Path, Path, Path, dict[str, object]]:
    figure_root = RUN / "figures"
    figure_dir = figure_root / "figures"
    source_dir = figure_root / "source_data"
    shutil.copytree(PRIOR_FIGURES / "figures", figure_dir)
    shutil.copytree(PRIOR_FIGURES / "source_data", source_dir)
    for path in figure_dir.glob("Supplementary_Figure_S6_*"):
        path.unlink()
    supplementary_figures.ASSERTIONS.clear()
    supplementary_figures.configure_style()
    supplementary_figures.build_s6(
        ROOT,
        figure_dir,
        source_dir,
        replication_terminology=True,
    )
    pdf = figure_dir / "Supplementary_Figure_S6_replication_robustness_diagnostics.pdf"
    png = figure_dir / "Supplementary_Figure_S6_replication_robustness_diagnostics.png"
    source = source_dir / "Supplementary_Figure_S6_source_data.csv"
    prior_source = PRIOR_FIGURES / "source_data/Supplementary_Figure_S6_source_data.csv"
    received_source = RECEIVED / "Supplementary_Figure_S6_source_data.csv"
    checks = {
        "builder_assertions_pass": all(item["pass"] for item in supplementary_figures.ASSERTIONS),
        "source_matches_prior": sha256(source) == sha256(prior_source) == S6_SOURCE_SHA256,
        "source_matches_received": received_source.exists() and sha256(source) == sha256(received_source),
        "one_s6_pdf": len(list(figure_dir.glob("Supplementary_Figure_S6_*.pdf"))) == 1,
        "one_s6_png": len(list(figure_dir.glob("Supplementary_Figure_S6_*.png"))) == 1,
        "fifteen_figure_pdfs": len(list(figure_dir.glob("*.pdf"))) == 15,
        "fifteen_figure_pngs": len(list(figure_dir.glob("*.png"))) == 15,
        "fifteen_source_csvs": len(list(source_dir.glob("*.csv"))) == 15,
    }
    if not all(checks.values()):
        raise RuntimeError(f"S6 rebuild checks failed: {checks}")
    return pdf, png, source, checks


def build_decision_matrices() -> tuple[Path, Path]:
    with (PRIOR / "MAIN_PANEL_FINAL_TRACEABILITY_DECISION_MATRIX.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        main_rows = list(csv.DictReader(handle))
    for row in main_rows:
        row["decision"] = "KEEP"
        row["rationale"] = (
            "No new numerical, semantic, claim-ownership or final-size legibility defect was demonstrated."
        )
    main_output = RUN / "MAIN_PANEL_REFERENCE_TERMINOLOGY_DECISION_MATRIX.csv"
    write_csv(main_output, main_rows, ["figure", "panel", "decision", "rationale"])

    roles = {
        "S1": "source integrity and processing-cohort QC",
        "S2": "representation and cross-cohort diagnostics",
        "S3": "identity-policy adjudication",
        "S4": "composition diagnostics and sensitivity",
        "S5": "pseudobulk diagnostics",
        "S6": "GSE135779 replication and robustness diagnostics",
        "S7": "correlation-aware regulator sensitivity",
        "S8": "IFN-overlap-depletion boundary",
        "S9": "end-to-end identity propagation boundary",
        "S10": "reference-calibration and transfer boundary",
    }
    supplementary_rows = []
    for label, role in roles.items():
        modified = label == "S6"
        supplementary_rows.append(
            {
                "figure": label,
                "decision": "MODIFY_SOURCE_REDRAW" if modified else "KEEP",
                "evidence_role": role,
                "rationale": (
                    "Frozen Source Data were re-read without numerical change; validation/mapping-label wording was replaced by replication/source-label wording."
                    if modified
                    else "No source-data, semantic, claim-ownership or legibility defect was demonstrated."
                ),
            }
        )
    supplementary_output = RUN / "SUPPLEMENTARY_FIGURE_REFERENCE_TERMINOLOGY_DECISION_MATRIX.csv"
    write_csv(supplementary_output, supplementary_rows, list(supplementary_rows[0]))
    return main_output, supplementary_output


def build_reference_verification() -> Path:
    rows = [
        {
            "issue": "edgeR quasi-likelihood workflow",
            "decision": "ADD_METHOD_REFERENCE",
            "primary_source": "https://pubmed.ncbi.nlm.nih.gov/27508061/",
            "support": "Filtering, normalization and edgeR quasi-likelihood workflow",
        },
        {
            "issue": "FRY implementation attribution",
            "decision": "REWORD_METHOD",
            "primary_source": "https://bioconductor.org/packages/release/bioc/manuals/limma/man/limma.pdf",
            "support": "fry is a fast approximation to mroast; the test is self-contained and directional",
        },
        {
            "issue": "ROAST framework",
            "decision": "RETAIN_PRIMARY_REFERENCE",
            "primary_source": "https://pubmed.ncbi.nlm.nih.gov/20610611/",
            "support": "Rotation gene-set framework and uni-/bi-directional testing",
        },
        {
            "issue": "MSigDB hallmark title",
            "decision": "CORRECT_BIBLIOGRAPHIC_TITLE",
            "primary_source": "https://pubmed.ncbi.nlm.nih.gov/26771021/",
            "support": "Exact published title",
        },
    ]
    output = RUN / "REFERENCE_CLAIM_SUPPORT_VERIFICATION_MATRIX.csv"
    write_csv(output, rows, list(rows[0]))
    return output


def build_manifest() -> Path:
    files = sorted(path for path in RUN.rglob("*") if path.is_file())
    rows = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    output = RUN / "SOURCE_INTEGRATION_FILE_MANIFEST.csv"
    write_csv(output, rows, list(rows[0]))
    return output


def main() -> None:
    if sha256(PACKAGE) != PACKAGE_SHA256:
        raise RuntimeError("Author-confirmed exact submission package changed")
    safe_reset(RUN)
    manuscript, manuscript_ledger, reference_validation = build_manuscript_source()
    supplement, supplement_ledger = build_supplement_source()
    s6_pdf, s6_png, s6_source, s6_checks = rebuild_s6()
    main_matrix, supplementary_matrix = build_decision_matrices()
    reference_matrix = build_reference_verification()

    ledger_rows = manuscript_ledger + supplement_ledger + [
        {
            "scope": "Supplementary Figure S6",
            "edit": "Source redraw from frozen Source Data",
            "old_text": "Independent-validation / external-validation / mapping-label terminology",
            "new_text": "GSE135779 replication / donor support / source-label terminology",
            "estimate_changed": False,
        }
    ]
    ledger = RUN / "REFERENCE_TERMINOLOGY_SOURCE_EDIT_LEDGER.csv"
    write_csv(ledger, ledger_rows, list(ledger_rows[0]))

    manuscript_text = manuscript.read_text(encoding="utf-8")
    supplement_text = supplement.read_text(encoding="utf-8")
    prohibited = [
        "donor-aware inference",
        "43 reference and 46 SLE strata",
        "internal validation estimate",
        "full internal GSE174188 validation contrast",
        "multiplicity-supported internal validation",
        "independent SLE validation dataset",
        "Source-label-defined GSE135779 validation",
        "source-metadata managed SLE",
        "source-metadata flare",
        "justify an IFN-centred regulatory interpretation",
    ]
    supplement_prohibited = [
        "Discovery and internal validation",
        "Independent SLE validation",
        "Independent GSE135779 validation",
        "source-label-based pseudobulk",
        "Independent-validation diagnostics",
    ]
    checks = {
        "manuscript_prohibited_terms_absent": not any(term in manuscript_text for term in prohibited),
        "supplement_prohibited_terms_absent": not any(
            term in supplement_text for term in supplement_prohibited
        ),
        "generic_validation_boundary_retained": "they are not independent validation" in manuscript_text,
        "credit_validation_retained": "Project administration, Validation" in manuscript_text,
        "prospective_clinical_validation_retained": "prospective clinical validation" in manuscript_text,
        "edgeR_workflow_reference_present": EDGE_R_WORKFLOW_REFERENCE in manuscript_text,
        "s6_source_sha_locked": sha256(s6_source) == S6_SOURCE_SHA256,
        "main_panel_decisions_21_keep": sum(
            1 for row in csv.DictReader(main_matrix.open(encoding="utf-8-sig")) if row["decision"] == "KEEP"
        ) == 21,
        "supplement_s6_only_modified": [
            row["figure"]
            for row in csv.DictReader(supplementary_matrix.open(encoding="utf-8-sig"))
            if row["decision"] != "KEEP"
        ]
        == ["S6"],
        "package_sha_unchanged": sha256(PACKAGE) == PACKAGE_SHA256,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Reference/terminology integration checks failed: {checks}")

    status = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PASS_REFERENCE_TERMINOLOGY_S6_SOURCE_INTEGRATION_DOCUMENT_REBUILD_REQUIRED",
        "checks": checks,
        "reference_validation": reference_validation,
        "s6_checks": s6_checks,
        "source_edits": len(ledger_rows),
        "reference_count": 33,
        "main_panels": {"keep": 21, "modify": 0, "replace": 0},
        "supplementary_figures": {"keep": 9, "modify_source_redraw": 1, "replace": 0},
        "scientific_estimates_changed": False,
        "source_data_changed": False,
        "release_or_zenodo_changed": False,
        "submission_package_changed": False,
        "submission_package_sha256": sha256(PACKAGE),
        "files": {
            path.name: {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (
                manuscript,
                supplement,
                s6_pdf,
                s6_png,
                s6_source,
                ledger,
                main_matrix,
                supplementary_matrix,
                reference_matrix,
            )
        },
    }
    (RUN / "00_SOURCE_INTEGRATION_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    build_manifest()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
