#!/usr/bin/env python3
"""Build the journal-facing C8BR prefreeze figures from frozen scientific inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import phase17_c7_01_build_main_figures as base


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRP" / "20260825_journal_facing_prefreeze"
C8BR_RUN = ROOT / "phase17_v7" / "gateC8BR" / "20260825_release_portability_preflight"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    figure_dir = RUN_DIR / "figures"
    source_dir = RUN_DIR / "source_data"
    for directory in (figure_dir, source_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    for number in (2, 3):
        for source in sorted((C8BR_RUN / "figures").glob(f"Figure{number}_*.*")):
            shutil.copy2(source, figure_dir / source.name)
        shutil.copy2(
            C8BR_RUN / "source_data" / f"Figure{number}_source_data.csv",
            source_dir / f"Figure{number}_source_data.csv",
        )

    prior_assertions = json.loads(
        (C8BR_RUN / "02_PANEL_DATA_ASSERTIONS.json").read_text(encoding="utf-8")
    )["checks"]
    carried = [
        row
        for row in prior_assertions
        if not str(row.get("check", "")).startswith(
            ("Figure1.", "Figure1_", "Figure4.", "Figure4_", "Figure5.", "Figure5_")
        )
    ]

    base.ASSERTIONS.clear()
    base.configure_style()
    base.build_figure1(
        ROOT,
        figure_dir,
        source_dir,
        graphical_validation_workflow=True,
    )
    base.build_figure4(
        ROOT,
        figure_dir,
        source_dir,
        reader_facing_source_labels=True,
    )
    base.build_figure5(
        ROOT,
        figure_dir,
        source_dir,
        proliferation_specificity_comparators=True,
        parallel_evidence_branches=True,
    )
    assertions = carried + list(base.ASSERTIONS)
    if len(assertions) != 46 or not all(row.get("pass") is True for row in assertions):
        raise RuntimeError(f"Expected 46 passing assertions; found {len(assertions)}")

    source_hashes: dict[str, str] = {}
    for number in range(1, 6):
        current = source_dir / f"Figure{number}_source_data.csv"
        prior = C8BR_RUN / "source_data" / current.name
        if sha256(current) != sha256(prior):
            raise RuntimeError(f"Visual-only rebuild changed source data: {current.name}")
        source_hashes[current.name] = sha256(current)

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_GATE_C8BRP_JOURNAL_FACING_FIGURES_BUILT",
        "figures": 5,
        "formats": ["PDF", "PNG_600_DPI"],
        "source_data_files": 5,
        "scientific_estimates_changed": False,
        "visual_only_changes": [
            "Figure 1a validation sequence uses aligned graphical nodes and arrows",
            "Figure 4d uses sequential reader-facing omission labels while source codes remain in Source Data",
        ],
        "figure5_semantics_preserved": "parallel regulatory and response-evidence branches",
        "all_source_data_match_gateC8BR": True,
        "source_data_sha256": source_hashes,
        "panel_data_assertions": len(assertions),
        "panel_data_assertions_passed": True,
    }
    (RUN_DIR / "01_FIGURE_BUILD_STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (RUN_DIR / "02_PANEL_DATA_ASSERTIONS.json").write_text(
        json.dumps(
            {"created_at": "2026-08-25", "status": "PASS", "checks": assertions},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
