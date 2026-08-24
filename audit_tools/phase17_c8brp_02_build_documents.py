#!/usr/bin/env python3
"""Build journal-facing prefreeze documents and clean portal-preview aliases."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import phase17_c8s_04_build_documents as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRP" / "20260825_journal_facing_prefreeze"
C8S_RUN = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"
C8BR_RUN = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"
PACKAGE = ROOT / "04_submission" / "package_genome_medicine_gateC8BRP_journal_facing_prefreeze_2026-08-25"
MANUSCRIPT_MD = ROOT / "01_manuscript" / "manuscript_v15_genome_medicine_journal_facing_prefreeze_2026-08-25.md"
SUPPLEMENT_MD = ROOT / "01_manuscript" / "supplementary_information_v6_journal_facing_2026-08-25.md"
COVER_MD = ROOT / "04_submission" / "cover_letter_genome_medicine_gateC8BRP_AUTHOR_COMPLETION_REQUIRED_2026-08-25.md"
SENSITIVITY_SOURCE = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair"


def copy_file(source: Path, target: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def build_portal_aliases(
    main_docx: Path,
    supplement_docx: Path,
    cover_docx: Path,
    source_zip: Path,
    sensitivity_zip: Path,
    stats_zip: Path,
) -> list[dict[str, object]]:
    preview = PACKAGE / "portal_upload_preview"
    preview.mkdir(parents=True, exist_ok=True)
    mappings: list[tuple[Path, Path, str]] = [
        (main_docx, preview / "Genome_Medicine_Manuscript.docx", "main manuscript"),
        (supplement_docx, preview / "Supplementary_Information.docx", "additional file 1"),
        (cover_docx, preview / "Cover_Letter.docx", "cover letter"),
        (source_zip, preview / "Figure_Source_Data.zip", "additional file 2"),
        (sensitivity_zip, preview / "Regulator_Sensitivity.zip", "additional file 3"),
        (stats_zip, preview / "Full_Statistical_Results.zip", "additional file 4"),
    ]
    for number in range(1, 6):
        source = next((RUN_DIR / "figures").glob(f"Figure{number}_*.pdf"))
        mappings.append((source, preview / f"Figure_{number}.pdf", f"main figure {number}"))
    for number in range(1, 8):
        source = next((C8S_RUN / "supplementary_figures").glob(f"Supplementary_Figure_S{number}_*.pdf"))
        mappings.append(
            (source, preview / f"Supplementary_Figure_S{number}.pdf", f"supplementary figure S{number}")
        )

    rows: list[dict[str, object]] = []
    for source, alias, role in mappings:
        copy_file(source, alias)
        source_hash = base.sha256(source)
        alias_hash = base.sha256(alias)
        if source_hash != alias_hash:
            raise RuntimeError(f"Portal alias hash mismatch: {alias.name}")
        rows.append(
            {
                "role": role,
                "provenance_path": source.relative_to(ROOT).as_posix(),
                "portal_alias": alias.relative_to(PACKAGE).as_posix(),
                "bytes": alias.stat().st_size,
                "sha256": alias_hash,
            }
        )

    mapping_path = PACKAGE / "submission_docs" / "PORTAL_UPLOAD_FILENAME_MAP.csv"
    with mapping_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["role", "provenance_path", "portal_alias", "bytes", "sha256"],
        )
        writer.writeheader()
        writer.writerows(rows)
    (preview / "DO_NOT_UPLOAD_AUTHOR_ACTION_REQUIRED.txt").write_text(
        "These clean aliases are a portal-layout preview only.\n"
        "Do not upload until ethics, declarations, author approval, licence and DOI are complete, "
        "all placeholders are zero, and the final workflow has been rerun.\n",
        encoding="utf-8",
        newline="\n",
    )
    return rows


def prepare_package_assets(main_docx: Path, supplement_docx: Path, cover_docx: Path) -> dict[str, object]:
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

    figure_files = [
        copy_file(path, figures_dir / path.name)
        for path in sorted((RUN_DIR / "figures").glob("Figure*.*"))
    ]
    supp_figure_files = [
        copy_file(path, supp_figures_dir / path.name)
        for path in sorted((C8S_RUN / "supplementary_figures").glob("Supplementary_Figure_S*.*"))
    ]
    source_files = [
        copy_file(path, source_dir / path.name)
        for path in sorted((RUN_DIR / "source_data").glob("Figure*_source_data.csv"))
    ]
    source_files.extend(
        copy_file(path, source_dir / path.name)
        for path in sorted((C8S_RUN / "supplementary_source_data").glob("Supplementary_Figure_S*_source_data.csv"))
    )
    source_manifest = source_dir / "SHA256SUMS.csv"
    source_manifest.write_text(
        "file,bytes,sha256\n"
        + "\n".join(
            f"{path.name},{path.stat().st_size},{base.sha256(path)}" for path in source_files
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
    base.write_deterministic_zip(sensitivity_zip, sensitivity_files + [sensitivity_manifest])

    stats_zip = copy_file(
        C8S_RUN / "Additional_file_4_Full_Statistical_Results_GateC8S.zip",
        PACKAGE / "additional_files" / "Full_Statistical_Results.zip",
    )
    for path in sorted((C8BR_RUN / "references").glob("*")):
        if path.is_file():
            copy_file(path, refs_dir / path.name)

    support_sources = [
        ROOT / "04_submission" / name
        for name in (
            "author_completion_matrix_gateC8BRP_2026-08-25.md",
            "journal_target_decision_gateC8BRP_2026-08-25.md",
            "reporting_checklist_gateC8BRP_2026-08-25.md",
            "cover_letter_genome_medicine_gateC8BRP_AUTHOR_COMPLETION_REQUIRED_2026-08-25.md",
        )
    ]
    for path in support_sources:
        copy_file(path, docs_dir / path.name)

    reproducibility_sources = [
        ROOT / "REPRODUCIBILITY.md",
        ROOT / "audit_tools" / "environment_phase17_v7_explicit_win64_2026-08-10.txt",
        ROOT / "audit_tools" / "environment_phase17_v7_pip_freeze_2026-08-10.txt",
        ROOT / "audit_tools" / "environment_phase17_v7_resolved_2026-08-10.yml",
        ROOT / "audit_tools" / "environment_gateC8BR_release_2026-08-25.yml",
        ROOT / "audit_tools" / "environment_gateC8BR_release_explicit_win64_2026-08-25.txt",
        ROOT / "audit_tools" / "00_create_gateC8BR_release_env.ps1",
        ROOT / "audit_tools" / "phase17_c8br_00_release_smoke_test.py",
        ROOT / "audit_tools" / "docx_a11y_audit.py",
        ROOT / "audit_tools" / "run_6013RP_phase17_gateC8BRP_journal_facing_prefreeze.ps1",
    ]
    reproducibility_files = [
        copy_file(path, reproducibility_dir / path.name) for path in reproducibility_sources
    ]

    aliases = build_portal_aliases(
        main_docx,
        supplement_docx,
        cover_docx,
        source_zip,
        sensitivity_zip,
        stats_zip,
    )
    return {
        "main_figure_files": len(figure_files),
        "supplementary_figure_files": len(supp_figure_files),
        "source_files": len(source_files),
        "source_zip": source_zip.relative_to(ROOT).as_posix(),
        "source_zip_bytes": source_zip.stat().st_size,
        "sensitivity_zip": sensitivity_zip.relative_to(ROOT).as_posix(),
        "sensitivity_zip_bytes": sensitivity_zip.stat().st_size,
        "full_statistical_zip": stats_zip.relative_to(ROOT).as_posix(),
        "full_statistical_zip_bytes": stats_zip.stat().st_size,
        "full_statistical_zip_sha256": base.sha256(stats_zip),
        "reproducibility_files": len(reproducibility_files),
        "portal_aliases": len(aliases),
        "portal_alias_hashes_match": all(row["sha256"] for row in aliases),
    }


def main() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True, exist_ok=True)

    main_docx = PACKAGE / "main_text" / "Genome_Medicine_Manuscript_AUTHOR_COMPLETION_REQUIRED.docx"
    supplement_docx = PACKAGE / "additional_files" / "Supplementary_Information.docx"
    cover_docx = PACKAGE / "submission_docs" / "Cover_Letter_AUTHOR_CONFIRMATION_REQUIRED.docx"
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
        "status": "PASS_GATE_C8BRP_DOCUMENTS_AND_PORTAL_PREVIEW_BUILT",
        "design_preset": "standard_business_brief",
        "named_override": "Genome Medicine submission: Times New Roman, manuscript double spacing and continuous line numbering",
        "outputs": outputs,
        "assets": assets,
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "04_GATE_C8BRP_DOCUMENT_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
