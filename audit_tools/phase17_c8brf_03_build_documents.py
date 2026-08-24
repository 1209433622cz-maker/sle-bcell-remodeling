#!/usr/bin/env python3
"""Build final author-approved documents, package assets and portal maps."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import phase17_c8s_04_build_documents as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRF" / "20260825_author_release"
C8S_RUN = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"
C8BR_RUN = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
SENSITIVITY_SOURCE = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair"
PACKAGE = ROOT / "04_submission" / "package_genome_medicine_gateC8BRF_author_release_2026-08-25"
MANUSCRIPT_MD = ROOT / "01_manuscript" / "manuscript_v16_genome_medicine_final_2026-08-25.md"
SUPPLEMENT_MD = ROOT / "01_manuscript" / "supplementary_information_v7_final_2026-08-25.md"
COVER_MD = ROOT / "04_submission" / "cover_letter_genome_medicine_final_2026-08-25.md"


def copy_file(source: Path, target: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def write_map(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "classification",
                "role",
                "provenance_path",
                "portal_alias",
                "bytes",
                "sha256",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_portal_maps(
    main_docx: Path,
    supplement_docx: Path,
    cover_docx: Path,
    source_zip: Path,
    sensitivity_zip: Path,
    stats_zip: Path,
) -> dict[str, object]:
    required_dir = PACKAGE / "portal_upload_required"
    optional_dir = PACKAGE / "portal_upload_optional"
    required: list[tuple[Path, Path, str]] = [
        (main_docx, required_dir / "Genome_Medicine_Manuscript.docx", "main manuscript"),
        (supplement_docx, required_dir / "Supplementary_Information.docx", "additional file 1"),
        (cover_docx, required_dir / "Cover_Letter.docx", "cover letter"),
        (source_zip, required_dir / "Figure_Source_Data.zip", "additional file 2"),
        (sensitivity_zip, required_dir / "Regulator_Sensitivity.zip", "additional file 3"),
        (stats_zip, required_dir / "Full_Statistical_Results.zip", "additional file 4"),
    ]
    for number in range(1, 6):
        source = next((RUN_DIR / "figures").glob(f"Figure{number}_*.pdf"))
        required.append((source, required_dir / f"Figure_{number}.pdf", f"main figure {number}"))

    optional: list[tuple[Path, Path, str]] = []
    for number in range(1, 8):
        source = next(
            (C8S_RUN / "supplementary_figures").glob(
                f"Supplementary_Figure_S{number}_*.pdf"
            )
        )
        optional.append(
            (
                source,
                optional_dir / f"Supplementary_Figure_S{number}.pdf",
                f"standalone supplementary figure S{number}",
            )
        )

    rows: list[dict[str, object]] = []
    for classification, mappings in (("REQUIRED", required), ("OPTIONAL", optional)):
        for source, alias, role in mappings:
            copy_file(source, alias)
            source_hash = base.sha256(source)
            alias_hash = base.sha256(alias)
            if source_hash != alias_hash:
                raise RuntimeError(f"Portal alias hash mismatch: {alias.name}")
            rows.append(
                {
                    "classification": classification,
                    "role": role,
                    "provenance_path": source.relative_to(ROOT).as_posix(),
                    "portal_alias": alias.relative_to(PACKAGE).as_posix(),
                    "bytes": alias.stat().st_size,
                    "sha256": alias_hash,
                }
            )

    docs_dir = PACKAGE / "submission_docs"
    required_rows = [row for row in rows if row["classification"] == "REQUIRED"]
    optional_rows = [row for row in rows if row["classification"] == "OPTIONAL"]
    write_map(docs_dir / "PORTAL_UPLOAD_FILENAME_MAP.csv", rows)
    write_map(docs_dir / "PORTAL_UPLOAD_REQUIRED.csv", required_rows)
    write_map(docs_dir / "PORTAL_UPLOAD_OPTIONAL.csv", optional_rows)
    (required_dir / "UPLOAD_POLICY.txt").write_text(
        "Default portal set: upload these 11 files.\n"
        "Do not also upload standalone Supplementary Figures S1-S7 when "
        "Supplementary_Information.docx is accepted as Additional file 1.\n",
        encoding="utf-8",
        newline="\n",
    )
    (optional_dir / "UPLOAD_ONLY_IF_PORTAL_REQUIRES_STANDALONE_SUPPLEMENTARY_FIGURES.txt").write_text(
        "These seven PDFs duplicate figures already embedded in Supplementary_Information.docx.\n"
        "Upload them only if the journal portal explicitly requires separate supplementary figures.\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "required": len(required_rows),
        "optional": len(optional_rows),
        "required_roles": [str(row["role"]) for row in required_rows],
        "optional_roles": [str(row["role"]) for row in optional_rows],
    }


def prepare_package_assets(
    main_docx: Path, supplement_docx: Path, cover_docx: Path
) -> dict[str, object]:
    figures_dir = PACKAGE / "figures"
    supp_figures_dir = PACKAGE / "figures_supplementary"
    source_dir = PACKAGE / "additional_files" / "source_data"
    refs_dir = PACKAGE / "references"
    docs_dir = PACKAGE / "submission_docs"
    sensitivity_dir = PACKAGE / "additional_files" / "regulator_sensitivity"
    reproducibility_dir = PACKAGE / "reproducibility"
    for directory in (
        figures_dir,
        supp_figures_dir,
        source_dir,
        refs_dir,
        docs_dir,
        sensitivity_dir,
        reproducibility_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    main_figures = [
        copy_file(path, figures_dir / path.name)
        for path in sorted((RUN_DIR / "figures").glob("Figure*.*"))
    ]
    supp_figures = [
        copy_file(path, supp_figures_dir / path.name)
        for path in sorted(
            (C8S_RUN / "supplementary_figures").glob("Supplementary_Figure_S*.*")
        )
    ]
    source_files = [
        copy_file(path, source_dir / path.name)
        for path in sorted((RUN_DIR / "source_data").glob("Figure*_source_data.csv"))
    ]
    source_files.extend(
        copy_file(path, source_dir / path.name)
        for path in sorted(
            (C8S_RUN / "supplementary_source_data").glob(
                "Supplementary_Figure_S*_source_data.csv"
            )
        )
    )
    source_manifest = source_dir / "SHA256SUMS.csv"
    source_manifest.write_text(
        "file,bytes,sha256\n"
        + "\n".join(
            f"{path.name},{path.stat().st_size},{base.sha256(path)}"
            for path in source_files
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    source_zip = PACKAGE / "additional_files" / "Figure_Source_Data.zip"
    base.write_deterministic_zip(source_zip, source_files + [source_manifest])

    sensitivity_files = [
        copy_file(SENSITIVITY_SOURCE / name, sensitivity_dir / name)
        for name in (
            "03_CORRELATION_AWARE_STAT1_STAT2_SENSITIVITY.csv",
            "04_CORRELATION_AWARE_STAT1_STAT2_DECISION.json",
        )
    ]
    sensitivity_manifest = sensitivity_dir / "SHA256SUMS.csv"
    sensitivity_manifest.write_text(
        "file,bytes,sha256\n"
        + "\n".join(
            f"{path.name},{path.stat().st_size},{base.sha256(path)}"
            for path in sensitivity_files
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sensitivity_zip = PACKAGE / "additional_files" / "Regulator_Sensitivity.zip"
    base.write_deterministic_zip(
        sensitivity_zip, sensitivity_files + [sensitivity_manifest]
    )
    stats_zip = copy_file(
        C8S_RUN / "Additional_file_4_Full_Statistical_Results_GateC8S.zip",
        PACKAGE / "additional_files" / "Full_Statistical_Results.zip",
    )

    for path in sorted((C8BR_RUN / "references").glob("*")):
        if path.is_file():
            copy_file(path, refs_dir / path.name)

    for path in (
        ROOT / "04_submission" / "author_release_confirmation_gateC8BRF_2026-08-25.md",
        ROOT / "04_submission" / "reporting_checklist_gateC8BRF_2026-08-25.md",
        ROOT / "04_submission" / "zenodo_metadata_gateC8BRF_2026-08-25.json",
        COVER_MD,
        MANUSCRIPT_MD,
        SUPPLEMENT_MD,
    ):
        copy_file(path, docs_dir / path.name)

    reproducibility_sources = [
        ROOT / "README.md",
        ROOT / "REPRODUCIBILITY.md",
        ROOT / "LICENSE",
        ROOT / "LICENSE_SCOPE.md",
        ROOT / "LICENSE_CONTENT_CC_BY_4.0.md",
        ROOT / "CITATION.cff",
        ROOT / "audit_tools" / "environment_phase17_v7_explicit_win64_2026-08-10.txt",
        ROOT / "audit_tools" / "environment_phase17_v7_pip_freeze_2026-08-10.txt",
        ROOT / "audit_tools" / "environment_phase17_v7_resolved_2026-08-10.yml",
        ROOT / "audit_tools" / "environment_gateC8BR_release_2026-08-25.yml",
        ROOT / "audit_tools" / "environment_gateC8BR_release_explicit_win64_2026-08-25.txt",
        ROOT / "audit_tools" / "00_create_gateC8BR_release_env.ps1",
        ROOT / "audit_tools" / "phase17_c8br_00_release_smoke_test.py",
        ROOT / "audit_tools" / "docx_a11y_audit.py",
        ROOT / "audit_tools" / "run_6013RP_phase17_gateC8BRF_author_release.ps1",
    ]
    reproducibility_files = [
        copy_file(path, reproducibility_dir / path.name)
        for path in reproducibility_sources
    ]

    portal = build_portal_maps(
        main_docx,
        supplement_docx,
        cover_docx,
        source_zip,
        sensitivity_zip,
        stats_zip,
    )
    return {
        "main_figure_files": len(main_figures),
        "supplementary_figure_files": len(supp_figures),
        "source_files": len(source_files),
        "source_zip": source_zip.relative_to(ROOT).as_posix(),
        "source_zip_sha256": base.sha256(source_zip),
        "sensitivity_zip": sensitivity_zip.relative_to(ROOT).as_posix(),
        "sensitivity_zip_sha256": base.sha256(sensitivity_zip),
        "full_statistical_zip": stats_zip.relative_to(ROOT).as_posix(),
        "full_statistical_zip_sha256": base.sha256(stats_zip),
        "reproducibility_files": len(reproducibility_files),
        "portal": portal,
    }


def main() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True, exist_ok=True)

    main_docx = PACKAGE / "main_text" / "Genome_Medicine_Manuscript.docx"
    supplement_docx = PACKAGE / "additional_files" / "Supplementary_Information.docx"
    cover_docx = PACKAGE / "submission_docs" / "Cover_Letter.docx"
    outputs = [
        base.markdown_to_docx(
            MANUSCRIPT_MD,
            main_docx,
            body_size=12,
            double_space=True,
            line_numbers=True,
            running_header="Genome Medicine | Research",
            title_override="Genome Medicine manuscript",
        ),
        base.markdown_to_docx(
            SUPPLEMENT_MD,
            supplement_docx,
            body_size=11,
            double_space=False,
            line_numbers=False,
            running_header="Supplementary information",
            title_override="Supplementary information",
            page_break_before_headings={
                "Supplementary Table S7 | Statistical tests and multiplicity families"
            },
        ),
        base.markdown_to_docx(
            COVER_MD,
            cover_docx,
            body_size=10.5,
            double_space=False,
            line_numbers=False,
            running_header=None,
            title_override="Genome Medicine cover letter",
            compact=True,
        ),
    ]
    assets = prepare_package_assets(main_docx, supplement_docx, cover_docx)
    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BRF_DOCUMENTS_AND_PORTAL_MAPS_BUILT",
        "design_preset": "standard_business_brief",
        "named_override": "Genome Medicine submission: Times New Roman, manuscript double spacing and continuous line numbering",
        "supplement_s7_pagination": "forced page break before S7 title",
        "outputs": outputs,
        "assets": assets,
    }
    (RUN_DIR / "05_DOCUMENT_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
