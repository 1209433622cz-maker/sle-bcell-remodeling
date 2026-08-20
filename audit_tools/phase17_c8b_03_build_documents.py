#!/usr/bin/env python3
"""Create the Gate C8B editable documents and package assets."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import phase17_c8s_04_build_documents as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8B" / "20260821_editorial_literature_preflight"
C8S_RUN = ROOT / "phase17_v7" / "gateC8S" / "20260821_supplementary_traceability_freeze"
PACKAGE = ROOT / "04_submission" / "package_genome_medicine_gateC8B_editorial_preflight_2026-08-21"
MANUSCRIPT_MD = ROOT / "01_manuscript" / "manuscript_v13_genome_medicine_gateC8B_editorial_preflight_2026-08-21.md"
SUPPLEMENT_MD = ROOT / "01_manuscript" / "supplementary_information_v4_gateC8B_editorial_preflight_2026-08-21.md"
COVER_MD = ROOT / "04_submission" / "cover_letter_genome_medicine_gateC8B_AUTHOR_COMPLETION_REQUIRED_2026-08-21.md"
REFERENCE_SOURCE = RUN_DIR / "references"
SENSITIVITY_SOURCE = ROOT / "phase17_v7" / "gateC8R" / "20260820_pre_submission_repair"


def copy_file(source: Path, target: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def prepare_package_assets() -> dict[str, object]:
    figures_dir = PACKAGE / "figures"
    supp_figures_dir = PACKAGE / "figures_supplementary"
    source_dir = PACKAGE / "additional_files" / "source_data"
    refs_dir = PACKAGE / "references"
    docs_dir = PACKAGE / "submission_docs"
    sensitivity_dir = PACKAGE / "additional_files" / "regulator_sensitivity"
    for directory in (figures_dir, supp_figures_dir, source_dir, refs_dir, docs_dir, sensitivity_dir):
        directory.mkdir(parents=True, exist_ok=True)

    figure_files = [copy_file(path, figures_dir / path.name) for path in sorted((RUN_DIR / "figures").glob("Figure*.*"))]
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
        + "\n".join(f"{path.name},{path.stat().st_size},{base.sha256(path)}" for path in source_files)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    source_zip = PACKAGE / "additional_files" / "Additional_file_2_Figure_Source_Data_GateC8B.zip"
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
        + "\n".join(f"{path.name},{path.stat().st_size},{base.sha256(path)}" for path in sensitivity_files)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sensitivity_zip = PACKAGE / "additional_files" / "Additional_file_3_Regulator_Sensitivity_GateC8B.zip"
    base.write_deterministic_zip(sensitivity_zip, sensitivity_files + [sensitivity_manifest])

    full_stats = copy_file(
        C8S_RUN / "Additional_file_4_Full_Statistical_Results_GateC8S.zip",
        PACKAGE / "additional_files" / "Additional_file_4_Full_Statistical_Results_GateC8S_FROZEN.zip",
    )
    for path in sorted(REFERENCE_SOURCE.glob("*")):
        if path.is_file():
            copy_file(path, refs_dir / path.name)
    for stem in (
        "author_completion_form",
        "journal_target_decision",
        "reporting_checklist",
    ):
        path = ROOT / "04_submission" / f"{stem}_gateC8B_2026-08-21.md"
        copy_file(path, docs_dir / path.name)
    copy_file(COVER_MD, docs_dir / COVER_MD.name)

    return {
        "main_figure_files": len(figure_files),
        "supplementary_figure_files": len(supp_figure_files),
        "source_files": len(source_files),
        "source_zip": source_zip.relative_to(ROOT).as_posix(),
        "source_zip_bytes": source_zip.stat().st_size,
        "sensitivity_zip": sensitivity_zip.relative_to(ROOT).as_posix(),
        "sensitivity_zip_bytes": sensitivity_zip.stat().st_size,
        "full_statistical_zip": full_stats.relative_to(ROOT).as_posix(),
        "full_statistical_zip_bytes": full_stats.stat().st_size,
        "full_statistical_zip_sha256": base.sha256(full_stats),
    }


def main() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True, exist_ok=True)

    outputs = [
        base.markdown_to_docx(
            MANUSCRIPT_MD,
            PACKAGE / "main_text" / "Genome_Medicine_Manuscript_GateC8B_AUTHOR_COMPLETION_REQUIRED.docx",
            body_size=12,
            double_space=True,
            line_numbers=True,
            running_header="Genome Medicine | Research | Gate C8B",
            title_override="Genome Medicine manuscript Gate C8B",
        ),
        base.markdown_to_docx(
            SUPPLEMENT_MD,
            PACKAGE / "additional_files" / "Additional_file_1_Supplementary_Information_GateC8B.docx",
            body_size=11,
            double_space=False,
            line_numbers=False,
            running_header="Supplementary information | Gate C8B",
            title_override="Supplementary information Gate C8B",
        ),
        base.markdown_to_docx(
            COVER_MD,
            PACKAGE / "submission_docs" / "Genome_Medicine_Cover_Letter_GateC8B_AUTHOR_CONFIRMATION_REQUIRED.docx",
            body_size=10.5,
            double_space=False,
            line_numbers=False,
            running_header=None,
            title_override="Genome Medicine cover letter Gate C8B",
            compact=True,
        ),
    ]
    assets = prepare_package_assets()
    status = {
        "created_at": "2026-08-21",
        "status": "PASS_GATE_C8B_DOCUMENTS_BUILT",
        "design_preset": "standard_business_brief",
        "named_override": "Genome Medicine scientific submission: Times New Roman, black hierarchy, manuscript double spacing and continuous line numbering",
        "outputs": outputs,
        "assets": assets,
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "04_GATE_C8B_DOCUMENT_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
