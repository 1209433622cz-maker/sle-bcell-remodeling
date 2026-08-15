#!/usr/bin/env python3
"""Freeze Gate C6B reference-resource metadata without calculating effects."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


COLLECTRI_URL = (
    "https://omnipathdb.org/interactions?datasets=collectri&format=tsv&genesymbols=1"
)
IFN_REGULATORS = ["STAT1", "STAT2", "IRF7", "IRF9"]
NEGATIVE_REGULATORS = ["E2F1", "FOXM1", "MYC", "MYBL2"]
CONTRAST_FILES = {
    "gse174188_primary": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "primary_base_gene_results.csv.gz"
    ),
    "gse174188_internal_nonoverlap": Path(
        "phase17_v7/gateC4B/20260815_edger_transcription/05_gene_results/"
        "validation_nonoverlap_gene_results.csv.gz"
    ),
    "gse135779_childhood": Path(
        "phase17_v7/gateC5B/20260815_gse135779_external_validation/05_gene_results/"
        "childhood_min50_gene_results.csv.gz"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("phase17_v7/gateC6B/20260815_pre_effect_resource_freeze"),
    )
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def download() -> bytes:
    request = urllib.request.Request(
        COLLECTRI_URL,
        headers={"User-Agent": "6013RP-GateC6B-resource-freeze/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        if response.status != 200:
            raise RuntimeError(f"CollecTRI HTTP status {response.status}")
        return response.read()


def is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    resource_dir = out_dir / "resources"
    resource_dir.mkdir(parents=True, exist_ok=True)
    resource_path = resource_dir / "collectri_human_omnipath_20260815.tsv.gz"

    if resource_path.exists() and not args.refresh:
        raw = gzip.decompress(resource_path.read_bytes())
        source_mode = "reused_frozen_local_copy"
    else:
        raw = download()
        resource_path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
        source_mode = "downloaded"

    decoded = raw.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded), delimiter="\t")
    rows = list(reader)
    required_columns = {
        "source_genesymbol",
        "target_genesymbol",
        "is_stimulation",
        "is_inhibition",
        "consensus_direction",
    }
    missing_columns = sorted(required_columns - set(reader.fieldnames or []))
    if missing_columns:
        raise ValueError(f"Missing CollecTRI columns: {missing_columns}")

    all_regulators = IFN_REGULATORS + NEGATIVE_REGULATORS
    coverage_rows = []
    signed_targets_by_regulator: dict[str, set[str]] = {}
    for regulator in all_regulators:
        exact = [row for row in rows if row["source_genesymbol"] == regulator]
        complex_rows = [
            row
            for row in rows
            if regulator in row["source_genesymbol"].replace("-", "_").split("_")
            and row["source_genesymbol"] != regulator
        ]
        targets = {row["target_genesymbol"] for row in exact if row["target_genesymbol"]}
        target_directions: dict[str, set[str]] = {}
        for row in exact:
            target = row["target_genesymbol"]
            if not target:
                continue
            directions = target_directions.setdefault(target, set())
            if is_true(row["consensus_stimulation"]):
                directions.add("positive")
            if is_true(row["consensus_inhibition"]):
                directions.add("negative")
        positive_targets = {
            target for target, directions in target_directions.items() if directions == {"positive"}
        }
        negative_targets = {
            target for target, directions in target_directions.items() if directions == {"negative"}
        }
        ambiguous_targets = {
            target for target, directions in target_directions.items() if len(directions) != 1
        }
        signed_targets = positive_targets | negative_targets
        signed_targets_by_regulator[regulator] = signed_targets
        coverage_rows.append(
            {
                "regulator": regulator,
                "family": "IFN_confirmatory"
                if regulator in IFN_REGULATORS
                else "proliferation_negative_control",
                "exact_interaction_rows": len(exact),
                "exact_unique_targets": len(targets),
                "consensus_positive_targets": len(positive_targets),
                "consensus_negative_targets": len(negative_targets),
                "ambiguous_or_unsigned_targets": len(ambiguous_targets),
                "signed_unique_targets": len(signed_targets),
                "complex_interaction_rows": len(complex_rows),
                "pre_effect_coverage_pass": len(signed_targets) >= 10,
            }
        )

    metadata = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PRE_EFFECT_RESOURCE_INVENTORY_COMPLETE",
        "regulatory_effects_inspected": False,
        "source_mode": source_mode,
        "collectri": {
            "url": COLLECTRI_URL,
            "organism": "human",
            "retrieval_date": "2026-08-15",
            "raw_size_bytes": len(raw),
            "raw_sha256": sha256_bytes(raw),
            "compressed_project_relative_path": resource_path.relative_to(root).as_posix(),
            "compressed_size_bytes": resource_path.stat().st_size,
            "compressed_sha256": sha256_bytes(resource_path.read_bytes()),
            "interaction_rows": len(rows),
            "columns": reader.fieldnames,
            "complex_policy_at_inventory": "observed but not split; final scoring policy pending contract",
        },
        "candidate_regulators": {
            "IFN_confirmatory": IFN_REGULATORS,
            "proliferation_negative_control": NEGATIVE_REGULATORS,
        },
        "all_exact_regulators_meet_10_target_inventory_floor": all(
            bool(row["pre_effect_coverage_pass"]) for row in coverage_rows
        ),
    }
    write_text(out_dir / "01_COLLECTRI_RESOURCE_METADATA.json", json.dumps(metadata, indent=2))
    write_csv(
        out_dir / "02_REGULATOR_TARGET_COVERAGE.csv",
        coverage_rows,
        [
            "regulator",
            "family",
            "exact_interaction_rows",
            "exact_unique_targets",
            "consensus_positive_targets",
            "consensus_negative_targets",
            "ambiguous_or_unsigned_targets",
            "signed_unique_targets",
            "complex_interaction_rows",
            "pre_effect_coverage_pass",
        ],
    )

    contrast_coverage_rows = []
    for contrast, relative_path in CONTRAST_FILES.items():
        path = root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Missing frozen gene table: {path}")
        with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
            gene_rows = list(csv.DictReader(handle))
        if not gene_rows:
            raise ValueError(f"Frozen gene table is empty: {path}")
        symbol_field = (
            "feature_name"
            if "feature_name" in gene_rows[0]
            else "gene_symbol_upper"
            if "gene_symbol_upper" in gene_rows[0]
            else "gene_symbol"
        )
        tested_symbols = {
            row[symbol_field].upper()
            for row in gene_rows
            if row["tested_filterByExpr"].strip().lower() == "true" and row[symbol_field]
        }
        for regulator in all_regulators:
            overlap = tested_symbols & signed_targets_by_regulator[regulator]
            contrast_coverage_rows.append(
                {
                    "contrast": contrast,
                    "regulator": regulator,
                    "family": "IFN_confirmatory"
                    if regulator in IFN_REGULATORS
                    else "proliferation_negative_control",
                    "tested_gene_symbols": len(tested_symbols),
                    "matched_signed_targets": len(overlap),
                    "pre_effect_minimum_10_pass": len(overlap) >= 10,
                }
            )
    write_csv(
        out_dir / "04_CONTRAST_REGULATOR_COVERAGE.csv",
        contrast_coverage_rows,
        [
            "contrast",
            "regulator",
            "family",
            "tested_gene_symbols",
            "matched_signed_targets",
            "pre_effect_minimum_10_pass",
        ],
    )
    metadata["confirmatory_contrast_coverage"] = {
        "contrasts": list(CONTRAST_FILES),
        "minimum_matched_signed_targets": min(
            row["matched_signed_targets"] for row in contrast_coverage_rows
        ),
        "all_regulator_contrasts_meet_10_target_floor": all(
            bool(row["pre_effect_minimum_10_pass"]) for row in contrast_coverage_rows
        ),
    }
    write_text(out_dir / "01_COLLECTRI_RESOURCE_METADATA.json", json.dumps(metadata, indent=2))

    report = [
        "# Gate C6B pre-effect resource inventory",
        "",
        f"**Status:** `{metadata['status']}`",
        "",
        "No GSE174188 or GSE135779 regulator effect was calculated during this step.",
        "",
        "## CollecTRI freeze candidate",
        "",
        f"- URL: `{COLLECTRI_URL}`",
        f"- retrieval date: 2026-08-15",
        f"- raw bytes: {len(raw):,}",
        f"- raw SHA-256: `{metadata['collectri']['raw_sha256']}`",
        f"- interaction rows: {len(rows):,}",
        "- organism: human",
        "- current complex policy: inspect without splitting; scoring policy remains locked",
        "",
        "## Candidate regulator coverage",
        "",
        "| Regulator | Family | Exact targets | Signed targets | Complex rows | Inventory floor |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in coverage_rows:
        report.append(
            f"| {row['regulator']} | {row['family']} | {row['exact_unique_targets']} | "
            f"{row['signed_unique_targets']} | {row['complex_interaction_rows']} | "
            f"{'PASS' if row['pre_effect_coverage_pass'] else 'FAIL'} |"
        )
    report.extend(
        [
            "",
            "## Orthogonal resources reviewed without effect calculation",
            "",
            "- MSigDB `HALLMARK_INTERFERON_ALPHA_RESPONSE`, systematic ID `M5911`, "
            "human Hallmark collection; exact release and member file must be frozen before scoring.",
            "- GSE23307, paired IFN-beta versus control primary human B cells from two healthy "
            "individuals; direct perturbation but too small for a powered confirmation.",
            "- GSE142637, four-hour IFN-alpha/IFN-lambda stimulation of human PBMC; relevant "
            "single-cell context but without donor-level replication suitable for inference.",
            "- GSE175913, sorted human naive and double-negative B-cell RNA-seq plus pSTAT1 "
            "flow-cytometry context; useful external biology, not a randomized transcriptomic perturbation.",
            "",
            "## Frozen contrast coverage",
            "",
            f"Across the three confirmatory gene universes, the minimum matched signed-target "
            f"count was {metadata['confirmatory_contrast_coverage']['minimum_matched_signed_targets']}. "
            f"All 24 regulator-by-contrast combinations passed the 10-target floor: "
            f"{metadata['confirmatory_contrast_coverage']['all_regulator_contrasts_meet_10_target_floor']}.",
            "",
            "## Decision consequence",
            "",
            "The final Gate C6B contract must choose one exact CollecTRI complex policy, "
            "freeze the MSigDB release/member checksum, declare the confirmatory contrasts "
            "and multiplicity family, and keep small perturbation datasets descriptive.",
        ]
    )
    write_text(out_dir / "03_RESOURCE_INVENTORY.md", "\n".join(report))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
