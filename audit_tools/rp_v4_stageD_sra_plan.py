"""Build the RP v4 plan-only SRA ledger without downloading or fitting outcomes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


EXPECTED = {
    "PRJNA1093470": {
        "runs": 176,
        "experiments": 88,
        "size_MB": 233209.0,
        "sha256": "25f5a677e283d3f3dedf957699c8c56abfdb6e41aafc09b2fb36f054fe441ad0",
        "role": "PRIMARY_ACTIVITY_CANDIDATE",
    },
    "PRJNA484963": {
        "runs": 85,
        "experiments": 83,
        "size_MB": 64365.0,
        "sha256": "5a6b62806ffe2a56a3d6d352f623d091afda320314d49faef19d8bc6a77dc47f",
        "role": "TECHNICAL_BRIDGE__NOT_INDEPENDENT_CONFIRMATION",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plan(input_dir: Path, output_dir: Path) -> dict:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError("Refusing to overwrite an SRA plan or receipt")

    run_rows: list[dict] = []
    study_rows: list[dict] = []
    all_runs: set[str] = set()
    for bioproject, expected in EXPECTED.items():
        source = input_dir / f"{bioproject}_RunInfo.csv"
        if not source.is_file() or sha256(source) != expected["sha256"]:
            raise ValueError(f"Frozen RunInfo hash mismatch: {bioproject}")
        with source.open(encoding="utf-8-sig", newline="") as handle:
            records = list(csv.DictReader(handle))
        runs = [record["Run"] for record in records]
        experiments = {record["Experiment"] for record in records}
        if (
            len(records) != expected["runs"]
            or len(experiments) != expected["experiments"]
            or len(set(runs)) != len(runs)
        ):
            raise ValueError(f"Unexpected run or experiment count: {bioproject}")
        if any(
            record["BioProject"] != bioproject
            or record["LibraryLayout"] != "PAIRED"
            or record["LibraryStrategy"] != "RNA-Seq"
            or record["Platform"] != "ILLUMINA"
            or not re.fullmatch(r"SRR\d+", record["Run"])
            for record in records
        ):
            raise ValueError(f"RunInfo metadata mismatch: {bioproject}")
        size_mb = sum(float(record["size_MB"]) for record in records)
        if abs(size_mb - expected["size_MB"]) > 1.5:
            raise ValueError(f"RunInfo resource total mismatch: {bioproject}")
        if any(run in all_runs for run in runs):
            raise ValueError("An SRR identifier appears in both studies")
        all_runs.update(runs)
        for record in records:
            run_rows.append(
                {
                    "BioProject": bioproject,
                    "Run": record["Run"],
                    "Experiment": record["Experiment"],
                    "BioSample": record["BioSample"],
                    "Sample": record["Sample"],
                    "size_MB": record["size_MB"],
                    "bases": record["bases"],
                    "role": expected["role"],
                    "downloaded": "NO__PLAN_ONLY",
                    "sra_verified": "NO__PENDING",
                    "fastq_verified": "NO__PENDING",
                    "gene_counts_verified": "NO__PENDING",
                }
            )
        study_rows.append(
            {
                "BioProject": bioproject,
                "runs": len(records),
                "experiments": len(experiments),
                "BioSamples": len({record["BioSample"] for record in records}),
                "size_MB": size_mb,
                "source_sha256": sha256(source),
                "status": "PLAN_ONLY_NO_DOWNLOAD",
            }
        )

    output_dir.mkdir(parents=True)
    write_csv(output_dir / "01_SRA_RUN_PLAN.csv", run_rows)
    write_csv(output_dir / "02_SRA_RESOURCE_LEDGER.csv", study_rows)
    receipt = {
        "schema": "RPV4_STAGE_D_SRA_PLAN_ONLY_1.0",
        "runs": len(run_rows),
        "experiments": sum(row["experiments"] for row in study_rows),
        "aggregate_reported_size_MB": sum(row["size_MB"] for row in study_rows),
        "minimum_recommended_scratch_TB": 2.5,
        "donor_independence": "UNRESOLVED__TREAT_POTENTIAL_OVERLAP",
        "disease_activity_results_inspected": False,
        "download_started": False,
        "alignment_started": False,
        "execute_option_available": False,
        "author_signoff_for_download": False,
    }
    (output_dir / "03_SRA_PLAN_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    arguments = parser.parse_args()
    if arguments.execute:
        raise PermissionError("Stage D does not authorize an SRA download")
    print(json.dumps(plan(arguments.input_dir, arguments.output_dir), indent=2))
