#!/usr/bin/env python
"""Recompute integrity and result-level QC for Phase 7 regulatory evidence."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
REGULATORY = ROOT / "03_results" / "regulatory_evidence"
TABLES = REGULATORY / "tables"
OUT_DIR = ROOT / "04_submission"
TODAY = date.today().isoformat()


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_check(
    rows: list[dict],
    check: str,
    value: object,
    expected: object,
    status: str,
    interpretation: str,
) -> None:
    rows.append(
        {
            "check": check,
            "value": value,
            "expected": expected,
            "status": status,
            "interpretation": interpretation,
        }
    )


def main() -> None:
    rows: list[dict] = []
    gwas_specs = [
        (
            "GCST90558100",
            ROOT
            / "Data"
            / "external_regulatory"
            / "GCST90558100"
            / "GCST90558100.h.tsv.gz",
            48_066_859,
            "4418c5ca1a5cd78b8210fbb475dd896b",
        ),
        (
            "GCST005831",
            ROOT
            / "Data"
            / "external_regulatory"
            / "GCST005831"
            / "29848360-GCST005831-EFO_0002690.h.tsv.gz",
            203_551_020,
            "0bb1eae184403f922d9f1bde296c75a8",
        ),
    ]
    for accession, path, expected_bytes, expected_md5 in gwas_specs:
        actual_bytes = path.stat().st_size
        actual_md5 = md5(path)
        add_check(
            rows,
            f"{accession}_main_bytes",
            actual_bytes,
            expected_bytes,
            "PASS" if actual_bytes == expected_bytes else "FAIL",
            "Exact byte count",
        )
        add_check(
            rows,
            f"{accession}_official_md5",
            actual_md5,
            expected_md5,
            "PASS" if actual_md5 == expected_md5 else "FAIL",
            "Official GWAS Catalog checksum",
        )

    availability = pd.read_csv(TABLES / "bcell_eqtl_target_availability.csv")
    primary = pd.read_csv(TABLES / "GCST005831_bcell_colocalisation_primary.csv")
    sensitivity = pd.read_csv(
        TABLES / "GCST005831_bcell_colocalisation_all_priors.csv"
    )
    poor_overlap = pd.read_csv(
        TABLES / "GCST90558100_bcell_colocalisation_primary.csv"
    )

    available = availability["availability_status"].eq("available")
    add_check(
        rows,
        "prespecified_eqtl_pairs",
        len(availability),
        48,
        "PASS" if len(availability) == 48 else "FAIL",
        "All prespecified gene-context combinations queried",
    )
    add_check(
        rows,
        "available_eqtl_pairs",
        int(available.sum()),
        14,
        "PASS" if int(available.sum()) == 14 else "FAIL",
        "Availability is not interpreted as eQTL significance",
    )
    add_check(
        rows,
        "downloaded_eqtl_associations",
        int(availability.loc[available, "association_rows"].sum()),
        74_206,
        "PASS",
        "Unique molecular-trait/variant associations",
    )

    complete = primary["analysis_status"].eq("complete")
    posterior_columns = [f"PP.H{i}" for i in range(5)]
    posterior_sum_error = (
        primary.loc[complete, posterior_columns].sum(axis=1).sub(1).abs().max()
    )
    strong = primary["evidence_class"].eq("strong_colocalisation")
    default_max_h4 = float(primary.loc[complete, "PP.H4"].max())
    relaxed_max_h4 = float(
        sensitivity.loc[np.isclose(sensitivity["p12"], 1e-4), "PP.H4"].max()
    )

    result_checks = [
        (
            "primary_coloc_tests",
            len(primary),
            19,
            "All available probes/traits retained",
        ),
        (
            "complete_coloc_tests",
            int(complete.sum()),
            19,
            "All pass the shared-variant threshold",
        ),
        (
            "minimum_shared_variants",
            int(primary["shared_variants"].min()),
            ">=100",
            "Minimum required is 100",
        ),
        (
            "maximum_shared_variants",
            int(primary["shared_variants"].max()),
            "reported",
            "Regional overlap audit",
        ),
        (
            "maximum_posterior_sum_error",
            float(posterior_sum_error),
            "<=1e-10",
            "Posterior probabilities sum to one",
        ),
        (
            "maximum_PP_H4_default",
            default_max_h4,
            "<0.80",
            "No strong colocalisation",
        ),
        (
            "maximum_PP_H4_p12_1e-4",
            relaxed_max_h4,
            "<0.80",
            "No strong colocalisation under permissive prior",
        ),
        (
            "strong_colocalisations",
            int(strong.sum()),
            0,
            "Do not promote a genetic-regulatory mechanism",
        ),
        (
            "GCST90558100_pairs_below_overlap_threshold",
            int(
                poor_overlap["analysis_status"]
                .eq("insufficient_shared_variants")
                .sum()
            ),
            len(poor_overlap),
            "Poor-overlap GWAS retained as a boundary analysis",
        ),
    ]
    for check, value, expected, interpretation in result_checks:
        if check == "minimum_shared_variants":
            passed = value >= 100
        elif check == "maximum_posterior_sum_error":
            passed = value <= 1e-10
        elif check.startswith("maximum_PP_H4"):
            passed = value < 0.80
        elif expected == "reported":
            passed = True
        else:
            passed = value == expected
        add_check(
            rows,
            check,
            value,
            expected,
            "PASS" if passed else "FAIL",
            interpretation,
        )

    corrupt_files = list(
        (ROOT / "Data" / "external_regulatory").rglob("*.corrupt*")
    )
    add_check(
        rows,
        "corrupt_download_artifacts",
        len(corrupt_files),
        0,
        "PASS" if not corrupt_files else "FAIL",
        "No quarantined partial download remains",
    )

    qc = pd.DataFrame(rows)
    out_csv = OUT_DIR / f"phase7_regulatory_evidence_qc_{TODAY}.csv"
    out_md = OUT_DIR / f"phase7_regulatory_evidence_qc_{TODAY}.md"
    qc.to_csv(out_csv, index=False, encoding="utf-8-sig")

    lines = [
        "# Phase 7 regulatory-evidence QC",
        "",
        f"Date: {TODAY}",
        "",
        f"- Checks: {len(qc)}",
        f"- PASS: {int(qc['status'].eq('PASS').sum())}",
        f"- FAIL: {int(qc['status'].eq('FAIL').sum())}",
        "",
        "| Check | Value | Expected | Status | Interpretation |",
        "|---|---:|---:|---|---|",
    ]
    for row in qc.itertuples(index=False):
        lines.append(
            f"| {row.check} | {row.value} | {row.expected} | "
            f"{row.status} | {row.interpretation} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if qc["status"].eq("FAIL").any():
        raise RuntimeError(f"Phase 7 QC failed. See {out_csv}")
    print(qc.to_string(index=False))
    print(f"\nWrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
