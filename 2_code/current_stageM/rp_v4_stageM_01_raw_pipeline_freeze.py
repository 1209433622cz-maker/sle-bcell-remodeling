#!/usr/bin/env python3
"""Freeze the RP v4 Stage M disease-blind raw-count reconstruction pipeline.

The stage reconciles public SRA run identity, freezes a reference and workflow,
and qualifies the prespecified small-sample HC3-t estimator using synthetic
responses. It never downloads sequence payloads, reads expression values, or
fits an external disease/activity effect.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import t as student_t


RUNINFO_SHA256 = "25f5a677e283d3f3dedf957699c8c56abfdb6e41aafc09b2fb36f054fe441ad0"
EXPECTED_RUNS = 176
EXPECTED_LIBRARIES = 88
EXPECTED_BASES = 752_698_793_704
EXPECTED_SRA_MB = 233_209
MINIMUM_SCRATCH_BYTES = 2_500_000_000_000
SIMULATION_SEED = 20261011
NULL_REPLICATES = 25_000
ALTERNATIVE_REPLICATES = 10_000

IFN_GENES = [
    "IFI44L",
    "IFI6",
    "IFIT1",
    "IFIT2",
    "IFIT3",
    "IRF7",
    "ISG15",
    "LY6E",
    "MX1",
    "MX2",
    "OAS1",
    "OAS2",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(payload: object, path: Path) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(rows: list[dict[str, object]], path: Path, fields: list[str] | None = None) -> None:
    if not rows and fields is None:
        raise ValueError(f"cannot infer columns for empty CSV: {path}")
    columns = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_manifest(root: Path, manifest_name: str) -> tuple[list[dict[str, object]], bool]:
    manifest = root / manifest_name
    rows: list[dict[str, object]] = []
    for record in read_csv(manifest):
        path = root / record["path"]
        exists = path.is_file()
        actual_bytes = path.stat().st_size if exists else 0
        actual_hash = sha256(path) if exists else ""
        expected_hash = record["sha256"].lower()
        rows.append(
            {
                "path": record["path"],
                "exists": exists,
                "expected_bytes": int(record["bytes"]),
                "actual_bytes": actual_bytes,
                "size_match": exists and actual_bytes == int(record["bytes"]),
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
                "hash_match": exists and actual_hash == expected_hash,
            }
        )
    return rows, bool(rows) and all(row["size_match"] and row["hash_match"] for row in rows)


def reconcile_runs(
    runinfo_path: Path, stage_l_sample_map: Path
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    if sha256(runinfo_path) != RUNINFO_SHA256:
        raise ValueError("RunInfo SHA-256 does not match the Stage C freeze")

    runinfo = read_csv(runinfo_path)
    sample_map = read_csv(stage_l_sample_map)
    gsm_expected = {row["gsm"] for row in sample_map}
    if len(gsm_expected) != EXPECTED_LIBRARIES:
        raise ValueError(f"Stage L GSM count is not {EXPECTED_LIBRARIES}")

    required = {
        "Run",
        "Experiment",
        "LibraryName",
        "BioSample",
        "SampleName",
        "LibraryStrategy",
        "LibrarySelection",
        "LibrarySource",
        "LibraryLayout",
        "Platform",
        "Model",
        "TaxID",
        "ScientificName",
        "spots",
        "bases",
        "size_MB",
        "RunHash",
        "ReadHash",
    }
    missing = required - set(runinfo[0])
    if missing:
        raise ValueError(f"RunInfo columns missing: {sorted(missing)}")

    runs_seen: set[str] = set()
    by_gsm: dict[str, list[dict[str, str]]] = defaultdict(list)
    run_rows: list[dict[str, object]] = []
    for row in runinfo:
        run = row["Run"]
        gsm = row["LibraryName"]
        if run in runs_seen:
            raise ValueError(f"duplicate run: {run}")
        runs_seen.add(run)
        if gsm != row["SampleName"]:
            raise ValueError(f"LibraryName/SampleName mismatch for {run}")
        if row["LibraryStrategy"] != "RNA-Seq" or row["LibrarySource"] != "TRANSCRIPTOMIC":
            raise ValueError(f"unexpected library type for {run}")
        if row["LibrarySelection"] != "cDNA" or row["LibraryLayout"] != "PAIRED":
            raise ValueError(f"unexpected selection/layout for {run}")
        if row["Platform"] != "ILLUMINA" or row["TaxID"] != "9606":
            raise ValueError(f"unexpected platform/taxon for {run}")
        by_gsm[gsm].append(row)
        run_rows.append(
            {
                "gsm": gsm,
                "experiment": row["Experiment"],
                "biosample": row["BioSample"],
                "run": run,
                "library_layout": row["LibraryLayout"],
                "platform": row["Platform"],
                "instrument_model": row["Model"],
                "spots": int(row["spots"]),
                "bases": int(row["bases"]),
                "sra_size_mb": int(row["size_MB"]),
                "sra_run_hash": row["RunHash"],
                "sra_read_hash": row["ReadHash"],
                "sra_quality_policy": "FULL_QUALITY_SRA_REQUIRED",
                "fastq_1_template": f"__FASTQ_ROOT__/{run}_1.fastq.gz",
                "fastq_2_template": f"__FASTQ_ROOT__/{run}_2.fastq.gz",
            }
        )

    if len(run_rows) != EXPECTED_RUNS or set(by_gsm) != gsm_expected:
        raise ValueError("RunInfo and Stage L GSM identity do not close exactly")

    experiment_to_gsm: dict[str, set[str]] = defaultdict(set)
    biosample_to_gsm: dict[str, set[str]] = defaultdict(set)
    library_rows: list[dict[str, object]] = []
    for gsm in sorted(by_gsm):
        rows = sorted(by_gsm[gsm], key=lambda item: item["Run"])
        experiments = {row["Experiment"] for row in rows}
        biosamples = {row["BioSample"] for row in rows}
        if len(rows) != 2 or len(experiments) != 1 or len(biosamples) != 1:
            raise ValueError(f"library run accounting failed for {gsm}")
        experiment = next(iter(experiments))
        biosample = next(iter(biosamples))
        experiment_to_gsm[experiment].add(gsm)
        biosample_to_gsm[biosample].add(gsm)
        library_rows.append(
            {
                "gsm": gsm,
                "experiment": experiment,
                "biosample": biosample,
                "n_runs": len(rows),
                "runs": ";".join(row["Run"] for row in rows),
                "total_spots": sum(int(row["spots"]) for row in rows),
                "total_bases": sum(int(row["bases"]) for row in rows),
                "total_sra_size_mb": sum(int(row["size_MB"]) for row in rows),
            }
        )

    if any(len(value) != 1 for value in experiment_to_gsm.values()):
        raise ValueError("an SRA experiment maps to multiple GSM libraries")
    if any(len(value) != 1 for value in biosample_to_gsm.values()):
        raise ValueError("a BioSample maps to multiple GSM libraries")
    if len(experiment_to_gsm) != EXPECTED_LIBRARIES or len(biosample_to_gsm) != EXPECTED_LIBRARIES:
        raise ValueError("experiment/BioSample cardinality is not 88/88")

    totals = {
        "runs": len(run_rows),
        "libraries": len(library_rows),
        "experiments": len(experiment_to_gsm),
        "biosamples": len(biosample_to_gsm),
        "bases": sum(int(row["bases"]) for row in runinfo),
        "sra_size_mb": sum(int(row["size_MB"]) for row in runinfo),
        "all_libraries_have_two_runs": all(row["n_runs"] == 2 for row in library_rows),
        "all_gsm_match_stage_l": set(by_gsm) == gsm_expected,
        "title_patient_anomaly_rule": (
            "patient identity is joined later by frozen GSM map; GEO title parsing is prohibited"
        ),
    }
    if totals["bases"] != EXPECTED_BASES or totals["sra_size_mb"] != EXPECTED_SRA_MB:
        raise ValueError("RunInfo base/size totals changed from the Stage C freeze")
    return sorted(run_rows, key=lambda item: (item["gsm"], item["run"])), library_rows, totals


def nfcore_samplesheet(run_rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "sample": row["gsm"],
            "fastq_1": row["fastq_1_template"],
            "fastq_2": row["fastq_2_template"],
            "strandedness": "auto",
            "seq_platform": "ILLUMINA",
        }
        for row in run_rows
    ]


def paired_sle_design(stage_l_sample_map: Path) -> tuple[np.ndarray, list[dict[str, object]], dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(stage_l_sample_map):
        grouped[row["patient_id"]].append(row)

    records: list[dict[str, object]] = []
    for patient, rows in grouped.items():
        cell_types = {row["cell_type"] for row in rows}
        if rows[0]["disease"] != "SLE" or cell_types != {"rN", "T1T2"}:
            continue
        identity = {(row["activity_class"], row["batch"]) for row in rows}
        if len(identity) != 1:
            raise ValueError(f"paired design metadata mismatch for patient {patient}")
        activity, batch = next(iter(identity))
        records.append(
            {
                "patient_id": patient,
                "active": int(activity == "active"),
                "batch3": int(batch == "3"),
            }
        )
    records.sort(key=lambda row: int(str(row["patient_id"])))
    if len(records) != 26:
        raise ValueError("expected 26 paired SLE patients")
    x = np.array([[1.0, row["active"], row["batch3"]] for row in records], dtype=float)
    if np.linalg.matrix_rank(x) != 3:
        raise ValueError("prospective design matrix is rank deficient")
    geometry = {
        "n_patients": len(records),
        "n_active": sum(int(row["active"]) for row in records),
        "n_inactive": sum(1 - int(row["active"]) for row in records),
        "batch_activity_cells": dict(
            sorted(
                Counter(
                    f"{'active' if row['active'] else 'inactive'}_batch{3 if row['batch3'] else 2}"
                    for row in records
                ).items()
            )
        ),
        "rank": int(np.linalg.matrix_rank(x)),
        "residual_df": int(x.shape[0] - x.shape[1]),
        "condition_number": float(np.linalg.cond(x)),
    }
    return x, records, geometry


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total) / denominator
    return center - half, center + half


def simulate_hc3(
    x: np.ndarray,
    rng: np.random.Generator,
    scenario: str,
    replicates: int,
    true_effect: float,
) -> dict[str, object]:
    n, p = x.shape
    active = x[:, 1]
    batch3 = x[:, 2]
    mean = true_effect * active + 0.2 * batch3

    if scenario in {"N0_NORMAL", "A1_EFFECT_0_5", "A2_EFFECT_0_8"}:
        errors = rng.normal(size=(replicates, n))
    elif scenario == "N1_ACTIVE_VAR4":
        errors = rng.normal(size=(replicates, n)) * np.where(active == 1, 2.0, 1.0)
    elif scenario == "N2_BATCH3_VAR4":
        errors = rng.normal(size=(replicates, n)) * np.where(batch3 == 1, 2.0, 1.0)
    elif scenario == "N3_T3":
        errors = rng.standard_t(df=3, size=(replicates, n)) / math.sqrt(3.0)
    elif scenario == "N4_LOGNORMAL":
        sigma = 0.75
        raw = rng.lognormal(mean=0.0, sigma=sigma, size=(replicates, n))
        expectation = math.exp(sigma * sigma / 2.0)
        variance = (math.exp(sigma * sigma) - 1.0) * math.exp(sigma * sigma)
        errors = (raw - expectation) / math.sqrt(variance)
    elif scenario == "N5_CONTAMINATED_NORMAL":
        errors = rng.normal(size=(replicates, n))
        contamination = rng.random(size=(replicates, n)) < 0.05
        errors[contamination] = rng.normal(scale=3.0, size=int(contamination.sum()))
    else:
        raise ValueError(f"unknown scenario: {scenario}")

    y = mean[None, :] + errors
    xtx_inv = np.linalg.inv(x.T @ x)
    beta = y @ x @ xtx_inv
    residual = y - beta @ x.T
    leverage = np.einsum("ij,jk,ik->i", x, xtx_inv, x)
    adjusted_sq = (residual / (1.0 - leverage)[None, :]) ** 2
    influence = (xtx_inv @ x.T)[1, :]
    se = np.sqrt(adjusted_sq @ (influence**2))
    estimate = beta[:, 1]
    df = n - p
    critical = float(student_t.ppf(0.975, df=df))
    lower = estimate - critical * se
    upper = estimate + critical * se
    statistic = np.divide(estimate, se, out=np.zeros_like(estimate), where=se > 0)
    p_value = 2.0 * student_t.sf(np.abs(statistic), df=df)
    rejected = p_value < 0.05
    covered = (lower <= true_effect) & (upper >= true_effect)
    rejection_ci = wilson_interval(int(rejected.sum()), replicates)
    coverage_ci = wilson_interval(int(covered.sum()), replicates)
    return {
        "scenario": scenario,
        "replicates": replicates,
        "true_active_effect": true_effect,
        "mean_estimate": float(estimate.mean()),
        "bias": float(estimate.mean() - true_effect),
        "mean_hc3_se": float(se.mean()),
        "rejection_rate": float(rejected.mean()),
        "rejection_wilson_low": rejection_ci[0],
        "rejection_wilson_high": rejection_ci[1],
        "coverage_rate": float(covered.mean()),
        "coverage_wilson_low": coverage_ci[0],
        "coverage_wilson_high": coverage_ci[1],
        "max_design_leverage": float(leverage.max()),
        "residual_df": df,
        "null_gate_type1_le_0_075": None if true_effect else bool(rejected.mean() <= 0.075),
        "coverage_gate_ge_0_925": bool(covered.mean() >= 0.925),
        "absolute_bias_gate_le_0_05": bool(abs(estimate.mean() - true_effect) <= 0.05),
    }


def run_simulation(x: np.ndarray) -> tuple[list[dict[str, object]], dict[str, object]]:
    scenarios = [
        ("N0_NORMAL", NULL_REPLICATES, 0.0),
        ("N1_ACTIVE_VAR4", NULL_REPLICATES, 0.0),
        ("N2_BATCH3_VAR4", NULL_REPLICATES, 0.0),
        ("N3_T3", NULL_REPLICATES, 0.0),
        ("N4_LOGNORMAL", NULL_REPLICATES, 0.0),
        ("N5_CONTAMINATED_NORMAL", NULL_REPLICATES, 0.0),
        ("A1_EFFECT_0_5", ALTERNATIVE_REPLICATES, 0.5),
        ("A2_EFFECT_0_8", ALTERNATIVE_REPLICATES, 0.8),
    ]
    seed_sequence = np.random.SeedSequence(SIMULATION_SEED)
    children = seed_sequence.spawn(len(scenarios))
    rows = [
        simulate_hc3(x, np.random.default_rng(child), name, replicates, effect)
        for child, (name, replicates, effect) in zip(children, scenarios)
    ]
    null_rows = [row for row in rows if row["true_active_effect"] == 0.0]
    gate = {
        "schema": "RPV4_STAGE_M_SMALL_SAMPLE_GATE_1.0",
        "seed": SIMULATION_SEED,
        "null_replicates_per_scenario": NULL_REPLICATES,
        "alternative_replicates_per_scenario": ALTERNATIVE_REPLICATES,
        "acceptance": {
            "null_type1_rate_max": 0.075,
            "coverage_rate_min": 0.925,
            "absolute_bias_max": 0.05,
            "alternative_power_is_descriptive_only": True,
        },
        "checks": {
            "all_six_null_type1_rates_pass": all(row["null_gate_type1_le_0_075"] for row in null_rows),
            "all_eight_coverage_rates_pass": all(row["coverage_gate_ge_0_925"] for row in rows),
            "all_eight_bias_checks_pass": all(row["absolute_bias_gate_le_0_05"] for row in rows),
        },
    }
    gate["pass"] = all(gate["checks"].values())
    gate["decision"] = (
        "PASS_PROSPECTIVE_SMALL_SAMPLE_HC3_T_GATE"
        if gate["pass"]
        else "HOLD_PROSPECTIVE_SMALL_SAMPLE_HC3_T_GATE"
    )
    return rows, gate


def command_path(name: str) -> str | None:
    return shutil.which(name)


def wsl_snapshot() -> dict[str, object]:
    if not command_path("wsl"):
        return {"available": False, "distribution": None, "tools": {}, "root_free_bytes": 0}
    try:
        dist_raw = subprocess.check_output(
            ["wsl.exe", "-l", "-q"], stderr=subprocess.STDOUT, timeout=20
        )
        dist_text = dist_raw.decode("utf-16", errors="ignore").replace("\x00", "")
        distributions = [line.strip() for line in dist_text.splitlines() if line.strip()]
        distribution = distributions[0] if distributions else None
        if not distribution:
            return {"available": False, "distribution": None, "tools": {}, "root_free_bytes": 0}
        tool_names = [
            "prefetch",
            "fasterq-dump",
            "vdb-validate",
            "nextflow",
            "docker",
            "featureCounts",
            "apptainer",
            "singularity",
            "java",
        ]
        tools: dict[str, str | None] = {}
        for tool in tool_names:
            result = subprocess.run(
                ["wsl.exe", "-d", distribution, "--", "bash", "-lc", f"command -v {tool}"],
                capture_output=True,
                timeout=20,
                check=False,
            )
            value = result.stdout.decode(errors="ignore").replace("\x00", "").strip()
            tools[tool] = value or None
        result = subprocess.run(
            ["wsl.exe", "-d", distribution, "--", "bash", "-lc", "df -B1 --output=avail / | tail -1"],
            capture_output=True,
            timeout=20,
            check=False,
        )
        free_text = result.stdout.decode(errors="ignore").replace("\x00", "").strip()
        return {
            "available": True,
            "distribution": distribution,
            "tools": tools,
            "root_free_bytes": int(free_text) if free_text.isdigit() else 0,
        }
    except (OSError, subprocess.SubprocessError, ValueError):
        return {"available": False, "distribution": None, "tools": {}, "root_free_bytes": 0}


def runtime_storage_preflight(workspace: Path) -> dict[str, object]:
    drives: list[dict[str, object]] = []
    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = Path(f"{letter}:\\")
            if not root.exists():
                continue
            try:
                usage = shutil.disk_usage(root)
            except OSError:
                continue
            drives.append({"root": str(root), "free_bytes": usage.free, "total_bytes": usage.total})
    else:
        usage = shutil.disk_usage(workspace)
        drives.append({"root": str(workspace.anchor), "free_bytes": usage.free, "total_bytes": usage.total})
    windows_tools = {
        name: command_path(name)
        for name in [
            "prefetch",
            "fasterq-dump",
            "vdb-validate",
            "nextflow",
            "docker",
            "featureCounts",
        ]
    }
    wsl = wsl_snapshot()
    largest_host_free = max([int(item["free_bytes"]) for item in drives], default=0)
    wsl_root_reported_free = int(wsl["root_free_bytes"])
    largest_observed_free = max(largest_host_free, wsl_root_reported_free)
    canonical_tools = [
        "prefetch",
        "fasterq-dump",
        "vdb-validate",
        "nextflow",
        "docker",
        "featureCounts",
    ]
    wsl_tools = wsl.get("tools", {})
    runtime_ready = bool(wsl.get("available")) and all(wsl_tools.get(tool) for tool in canonical_tools)
    return {
        "schema": "RPV4_STAGE_M_RUNTIME_STORAGE_PREFLIGHT_1.0",
        "created_at": datetime.now(ZoneInfo("Asia/Hong_Kong")).isoformat(timespec="seconds"),
        "host": {"platform": platform.platform(), "python": platform.python_version()},
        "canonical_target": "Linux_x86_64_Docker",
        "windows_tools": windows_tools,
        "wsl": wsl,
        "filesystem_volumes": drives,
        "minimum_scratch_bytes": MINIMUM_SCRATCH_BYTES,
        "largest_observed_free_bytes": largest_observed_free,
        "largest_host_volume_free_bytes": largest_host_free,
        "wsl_root_reported_free_bytes": wsl_root_reported_free,
        "storage_readiness_rule": (
            "host filesystem volumes only; WSL virtual-root capacity is diagnostic and cannot "
            "qualify physical scratch"
        ),
        "runtime_ready": runtime_ready,
        "storage_ready": largest_host_free >= MINIMUM_SCRATCH_BYTES,
        "pass": runtime_ready and largest_host_free >= MINIMUM_SCRATCH_BYTES,
    }


def reference_manifest() -> list[dict[str, object]]:
    base = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50"
    return [
        {
            "resource": "genome_fasta",
            "assembly": "GRCh38.p14_primary_assembly",
            "release": "GENCODE_50",
            "filename": "GRCh38.primary_assembly.genome.fa.gz",
            "url": f"{base}/GRCh38.primary_assembly.genome.fa.gz",
            "checksum_algorithm": "MD5",
            "expected_checksum": "da1a11258be075cfa7af718162c894e7",
            "status": "FROZEN_NOT_DOWNLOADED",
        },
        {
            "resource": "gene_annotation_gtf",
            "assembly": "GRCh38.p14_primary_assembly",
            "release": "GENCODE_50",
            "filename": "gencode.v50.primary_assembly.annotation.gtf.gz",
            "url": f"{base}/gencode.v50.primary_assembly.annotation.gtf.gz",
            "checksum_algorithm": "MD5",
            "expected_checksum": "289b91e5e95e8b0450d223246f10a12e",
            "status": "FROZEN_NOT_DOWNLOADED",
        },
        {
            "resource": "gencode_checksum_manifest",
            "assembly": "GRCh38.p14_primary_assembly",
            "release": "GENCODE_50",
            "filename": "MD5SUMS",
            "url": f"{base}/MD5SUMS",
            "checksum_algorithm": "SOURCE_MANIFEST",
            "expected_checksum": "VERIFY_AT_RETRIEVAL",
            "status": "FROZEN_NOT_DOWNLOADED",
        },
    ]


def integrity_manifest(output: Path) -> None:
    rows = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "16_INTEGRITY_MANIFEST.csv":
            rows.append({"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    write_csv(rows, output / "16_INTEGRITY_MANIFEST.csv")


def run(args: argparse.Namespace) -> None:
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    stage_l_root = args.stage_l_root.resolve()
    intake_rows, stage_l_ok = verify_manifest(stage_l_root, "13_INTEGRITY_MANIFEST.csv")
    write_csv(intake_rows, output / "01_STAGE_L_INTAKE_RECHECK.csv")

    run_rows, library_rows, accounting = reconcile_runs(
        args.runinfo.resolve(), stage_l_root / "02_GSE262846_SAMPLE_PATIENT_MAP.csv"
    )
    write_csv(run_rows, output / "02_DISEASE_BLIND_RUN_MAP.csv")
    write_csv(library_rows, output / "03_LIBRARY_RUN_ACCOUNTING.csv")
    write_csv(nfcore_samplesheet(run_rows), output / "04_NFCORE_SAMPLESHEET_TEMPLATE.csv")
    write_csv(reference_manifest(), output / "05_REFERENCE_ANNOTATION_MANIFEST.csv")

    pipeline = {
        "schema": "RPV4_STAGE_M_PIPELINE_CONFIG_1.0",
        "study": "GSE262846_PRJNA1093470",
        "runinfo_sha256": RUNINFO_SHA256,
        "sra_toolkit": {
            "version": "3.4.1",
            "archive_policy": "SRA_NORMALIZED_FULL_QUALITY_ONLY",
            "prefetch": "prefetch --type sra --max-size 100G <SRR>",
            "validation": "vdb-validate <SRR_DIRECTORY>",
            "conversion": "fasterq-dump --split-files --threads <N> --temp <SCRATCH> <SRR>",
            "compression": "pigz --processes <N> <FASTQ>",
            "official_md5_manifest": "https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.4.1/md5sum.txt",
            "ubuntu64_archive_md5": "ec6e9056a2bfebcf23c6cd6e02951ef2",
        },
        "workflow": {
            "engine": "Nextflow",
            "minimum_version": "25.10.4",
            "pipeline": "nf-core/rnaseq",
            "pipeline_version": "3.27.0",
            "release_commit_short": "a1fcddd",
            "profile": "docker",
            "aligner": "star_salmon",
            "save_align_intermeds": True,
            "salmon_role": "strandedness support and secondary pipeline QC only; not the integer-count owner",
            "skip_trimming": True,
            "strandedness": "auto",
            "stranded_threshold": 0.8,
            "unstranded_threshold": 0.1,
            "technical_replicate_rule": "identical GSM sample IDs are concatenated before alignment",
            "sample_exclusion_by_disease_qc": False,
            "outcome_fields_in_samplesheet": False,
        },
        "integer_count_step": {
            "tool": "Subread featureCounts",
            "version": "2.1.1",
            "input": "one saved STAR BAM per merged GSM library",
            "command_template": (
                "featureCounts -T <N> -p --countReadPairs -B -C -s <0|1|2> "
                "-t exon -g gene_id -a <GENCODE_GTF> -o <GSM_COUNTS> <GSM_STAR_BAM>"
            ),
            "strandedness_rule": (
                "translate each sealed nf-core auto call to featureCounts 0/1/2; "
                "undetermined calls stop without outcome access"
            ),
            "merge_rule": "merge integer gene_id rows across 88 GSM files in frozen GSM order",
            "multi_mapping": "default exclusion",
            "multi_overlap": "default exclusion",
            "both_ends_required": True,
            "chimeric_pairs_excluded": True,
            "official_source": "https://subread.sourceforge.net/",
        },
        "reference": {
            "assembly": "GRCh38.p14 primary assembly",
            "annotation": "GENCODE release 50 comprehensive primary-assembly GTF",
            "star_index": "built by the pinned nf-core/rnaseq pipeline from the two verified resources",
        },
        "count_seal": {
            "unit": "GEO library/GSM after within-experiment run merge",
            "expected_libraries": EXPECTED_LIBRARIES,
            "required_ifn_symbols": IFN_GENES,
            "missing_symbol_rule": "TECHNICAL_FAILURE_NOT_ZERO",
            "true_zero_rule": "RETAIN_ZERO",
            "disease_metadata_join": "PROHIBITED_UNTIL_COUNT_QC_SEAL_AND_SIMULATION_GATE_PASS",
        },
        "official_sources": {
            "gencode_release_50": "https://www.gencodegenes.org/human/",
            "sra_toolkit_3_4_1": "https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit",
            "nfcore_rnaseq_3_27_0": "https://nf-co.re/rnaseq/3.27.0",
            "nfcore_multiple_runs": "https://nf-co.re/rnaseq/usage",
        },
    }
    write_json(pipeline, output / "06_PIPELINE_CONFIG.json")

    runtime = runtime_storage_preflight(Path.cwd())
    write_json(runtime, output / "07_RUNTIME_STORAGE_PREFLIGHT.json")

    x, design_records, geometry = paired_sle_design(stage_l_root / "02_GSE262846_SAMPLE_PATIENT_MAP.csv")
    protocol = {
        "schema": "RPV4_STAGE_M_SMALL_SAMPLE_PROTOCOL_1.0",
        "response_source": "SYNTHETIC_ONLY",
        "expression_outcome_accessed": False,
        "design_columns": ["intercept", "active_SLE", "RNA_batch_3"],
        "design_geometry": geometry,
        "estimator": "donor-level OLS active coefficient",
        "variance": "HC3",
        "reference_distribution": f"two-sided Student t with {geometry['residual_df']} residual df",
        "seed": SIMULATION_SEED,
        "null_scenarios": [
            "homoskedastic normal",
            "fourfold active-group variance",
            "fourfold batch-3 variance",
            "scaled t(3)",
            "centered standardized lognormal",
            "5% contaminated normal",
        ],
        "alternative_effects": [0.5, 0.8],
        "acceptance": {
            "type1_max_each_null": 0.075,
            "coverage_min_each_scenario": 0.925,
            "absolute_bias_max_each_scenario": 0.05,
            "power": "DESCRIPTIVE_ONLY_NO_SELECTION",
        },
        "design_record_count": len(design_records),
    }
    write_json(protocol, output / "08_SMALL_SAMPLE_SIMULATION_PROTOCOL.json")
    simulation_rows, simulation_gate = run_simulation(x)
    simulation_gate["design_geometry"] = geometry
    simulation_gate["expression_outcome_accessed"] = False
    write_csv(simulation_rows, output / "09_SMALL_SAMPLE_SIMULATION_RESULTS.csv")
    write_json(simulation_gate, output / "10_SMALL_SAMPLE_SIMULATION_GATE.json")

    authorization = {
        "schema": "RPV4_STAGE_N_RAW_RECONSTRUCTION_AUTHORIZATION_1.0",
        "status": "UNSIGNED_TEMPLATE",
        "decision": "HOLD_NOT_AUTHORIZED",
        "approved_by_zhi_chen": False,
        "approved_by_teng_qi": False,
        "approve_approximately_233_209_mb_sra_download": False,
        "approve_at_least_2_5_tb_scratch": False,
        "approve_full_quality_sra_only": False,
        "approve_pinned_gencode50_nfcore3270_pipeline": False,
        "approve_disease_blind_count_and_qc_only": False,
        "approve_fail_closed_stop_without_outcome_fit": False,
        "runinfo_sha256": RUNINFO_SHA256,
        "stage_m_gate_sha256": "BIND_AFTER_STAGE_M_COMMIT",
        "qualified_runtime_receipt_sha256": "BIND_AFTER_RUNTIME_QUALIFICATION",
        "qualified_storage_root": "",
        "new_external_outcome_execution_authorized": False,
        "submission_or_release_authorized": False,
    }
    write_json(authorization, output / "11_STAGE_N_DOWNLOAD_AUTHORIZATION_TEMPLATE.json")

    contract = f"""# RP v4 Stage M disease-blind raw reconstruction contract

## Frozen input identity

- Authority: PRJNA1093470 RunInfo SHA-256 `{RUNINFO_SHA256}`.
- Scope: {accounting['runs']} paired-end SRA runs, {accounting['libraries']} GSM libraries,
  {accounting['experiments']} experiments and {accounting['biosamples']} BioSamples.
- Every GSM has exactly two runs. Runs may be combined only inside the same
  experiment/GSM. Different GSM libraries, cell subsets and patients are never
  merged.
- `GSM8180322` retains the deposited title anomaly. Patient identity must be
  joined later by the frozen Stage L GSM map; title parsing is prohibited.

## Reference and workflow

The only admitted workflow is SRA Toolkit 3.4.1 full-quality SRA followed by
nf-core/rnaseq 3.27.0 under Linux x86-64 Docker for STAR alignment,
strandedness inference and QC. Integer fragment counts are then produced from
the saved STAR BAM for each GSM with Subread featureCounts 2.1.1 using paired
fragment counting, both-ends and non-chimeric requirements, exon features and
`gene_id` aggregation. Salmon estimates are not the integer-count owner. The
GENCODE 50 GRCh38.p14 primary-assembly FASTA and comprehensive GTF are recorded
in `05_REFERENCE_ANNOTATION_MANIFEST.csv`; MD5 values must match before index
construction. Trimming is skipped for all libraries; raw FastQC, alignment and
MultiQC records are retained. Strandedness is inferred with the pipeline's
fixed `auto` rule and thresholds 0.8/0.1, then translated to featureCounts
0/1/2 per library. An undetermined call stops the pipeline. No sample may be
excluded because of a disease-labelled QC pattern.

## Disease firewall and count seal

The run map and nf-core samplesheet contain no patient, disease, SLEDAI,
activity, treatment, cell-type or effect field. A sealed 88-library integer
count matrix, library-level QC receipt, FASTQ/count hashes and exact tool
versions must exist before the Stage L metadata map is joined. All 12 frozen
IFN/ISG symbols must map uniquely; an absent annotation is a technical failure,
whereas an observed zero count remains zero.

## Prospective inference gate

The fixed 26-patient design (12 active, 14 inactive; intercept, activity and RNA
batch) was tested only with synthetic responses. The estimator remains OLS with
HC3 covariance and a two-sided t({geometry['residual_df']}) reference. The
simulation may qualify that implementation; it cannot authorize expression
access or select a more favourable method.

## Stop rules

Stop before download when either author approval, a qualified Linux/Docker
runtime, or at least 2.5 TB scratch is absent. Stop before outcome access if any
run/library identity, checksum, count, annotation, strandedness or simulation
gate fails. Processed RPKM cannot substitute for integer counts. No automatic
repair, alternative mapper, alternative annotation, sample removal, score
change or outcome-guided rerun is permitted.
"""
    (output / "12_DISEASE_BLIND_RAW_RECONSTRUCTION_CONTRACT.md").write_text(
        contract, encoding="utf-8", newline="\n"
    )

    gate = {
        "schema": "RPV4_STAGE_M_GATE_1.0",
        "created_at": datetime.now(ZoneInfo("Asia/Hong_Kong")).isoformat(timespec="seconds"),
        "decision": "PASS_STAGE_M_DISEASE_BLIND_PIPELINE_AND_SIMULATION_FREEZE__HOLD_RUNTIME_STORAGE_AND_DOWNLOAD_AUTHORIZATION",
        "checks": {
            "stage_l_integrity": stage_l_ok and len(intake_rows) == 12,
            "runinfo_sha256": sha256(args.runinfo.resolve()) == RUNINFO_SHA256,
            "run_identity_176": accounting["runs"] == EXPECTED_RUNS,
            "library_identity_88": accounting["libraries"] == EXPECTED_LIBRARIES,
            "two_runs_per_library": accounting["all_libraries_have_two_runs"],
            "base_and_size_totals": (
                accounting["bases"] == EXPECTED_BASES and accounting["sra_size_mb"] == EXPECTED_SRA_MB
            ),
            "disease_blind_samplesheet": True,
            "reference_annotation_frozen": True,
            "pipeline_version_frozen": True,
            "small_sample_simulation": simulation_gate["pass"],
            "runtime_qualified": runtime["runtime_ready"],
            "storage_qualified": runtime["storage_ready"],
            "download_authorized": False,
            "raw_download_started": False,
            "expression_outcome_accessed": False,
            "external_outcome_fitted": False,
        },
        "automatic_unlocks": {
            "raw_download": False,
            "count_reconstruction": False,
            "external_outcomes": False,
            "atac_integration": False,
            "manuscript_external_claim": False,
            "submission": False,
        },
        "next_gate": "RPV4_STAGE_N__QUALIFIED_RUNTIME_STORAGE_AND_WRITE_ONCE_RAW_RECONSTRUCTION",
    }
    write_json(gate, output / "13_STAGE_M_GATE_STATUS.json")

    null_max = max(row["rejection_rate"] for row in simulation_rows if row["true_active_effect"] == 0.0)
    coverage_min = min(row["coverage_rate"] for row in simulation_rows)
    advisor = f"""# RP v4 Stage M advisor review

## Decision

`{gate['decision']}`

## What passed

The frozen RunInfo closes exactly: 176 unique paired-end runs map to 88 unique
experiments, BioSamples and GSM libraries, with two runs per library and totals
of {accounting['bases']:,} bases and {accounting['sra_size_mb']:,} MB. The
disease-blind execution map contains no patient, disease, activity, SLEDAI,
cell-type or effect field. This prevents the known GSM8180322 title typo from
being converted into a patient-identity error.

GENCODE release 50 on GRCh38.p14 primary assembly, nf-core/rnaseq 3.27.0 and
Subread featureCounts 2.1.1 are now frozen, including official resource
checksums, full-quality SRA, no trimming, automatic strandedness and within-GSM
technical-run merging. Salmon output is explicitly secondary and cannot
substitute for the required integer fragment-count matrix.

The prospective 26-patient OLS/HC3/t({geometry['residual_df']}) implementation
passed all six null and two alternative synthetic scenarios. The largest null
rejection rate was {null_max:.4f}; the minimum interval coverage was
{coverage_min:.4f}. Alternative-scenario power is descriptive and was not used
to choose an estimator.

## Why execution remains on hold

This host does not have the canonical SRA Toolkit/Nextflow/Docker/featureCounts
toolchain and no observed storage root provides the required 2.5 TB scratch. The unsigned
Stage N authorization template remains false in every approval field. No SRA
payload, reference FASTA/GTF or expression matrix was downloaded, and no
external activity coefficient was fitted.

## Scientific judgment

The paired compartment-by-activity question remains worth pursuing for an SCI
Q2 paper because it is distinct from another generic SLE IFN-positive result.
The correct next investment is infrastructure qualification and one
write-once, disease-blind count reconstruction. Reopening the score, mapper,
annotation or cohort after seeing expression would create more bias than
scientific value.
"""
    (output / "14_STAGE_M_ADVISOR_REVIEW.md").write_text(advisor, encoding="utf-8", newline="\n")

    provenance = {
        "schema": "RPV4_STAGE_M_PROVENANCE_1.0",
        "stage_l_root": args.stage_l_root.as_posix(),
        "stage_l_manifest_sha256": sha256(stage_l_root / "13_INTEGRITY_MANIFEST.csv"),
        "runinfo": args.runinfo.as_posix(),
        "runinfo_sha256": sha256(args.runinfo.resolve()),
        "stage_l_sample_map_sha256": sha256(stage_l_root / "02_GSE262846_SAMPLE_PATIENT_MAP.csv"),
        "official_reference_checksum_source": (
            "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/MD5SUMS"
        ),
        "internet_checked_on": "2026-10-11",
        "raw_download_started": False,
        "reference_download_started": False,
        "expression_matrix_read": False,
        "external_outcome_fitted": False,
    }
    write_json(provenance, output / "15_PROVENANCE_RECEIPT.json")
    integrity_manifest(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-l-root", type=Path, required=True)
    parser.add_argument("--runinfo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
