#!/usr/bin/env python3
"""Freeze MSigDB and GSE23307 resources without inspecting expression effects."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


MSIGDB_VERSION = "2026.1.Hs"
MSIGDB_URL = (
    "https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2026.1.Hs/"
    "h.all.v2026.1.Hs.symbols.gmt"
)
GSE23307_MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE23nnn/GSE23307/matrix/"
    "GSE23307_series_matrix.txt.gz"
)
GPL6104_ANNOT_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL6nnn/GPL6104/annot/"
    "GPL6104.annot.gz"
)
PROGRAM_DICTIONARY = Path(
    "phase17_v7/gateC4A/20260815_raw_pseudobulk_freeze/11_program_dictionary.csv"
)


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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def retrieve(url: str, path: Path, refresh: bool) -> tuple[bytes, str]:
    if path.is_file() and not refresh:
        return path.read_bytes(), "reused_frozen_local_copy"
    request = urllib.request.Request(
        url, headers={"User-Agent": "6013RP-GateC6B-resource-freeze/1.0"}
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        data = response.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data, "downloaded"


def parse_msigdb(data: bytes) -> tuple[str, list[str]]:
    matches = []
    for line in data.decode("utf-8").splitlines():
        fields = line.rstrip("\n").split("\t")
        if fields and fields[0] == "HALLMARK_INTERFERON_ALPHA_RESPONSE":
            matches.append(fields)
    if len(matches) != 1:
        raise ValueError(f"Expected one Hallmark IFNA row, found {len(matches)}")
    fields = matches[0]
    description = fields[1]
    genes = [gene.upper() for gene in fields[2:] if gene]
    if len(genes) != 97 or len(set(genes)) != 97:
        raise ValueError(f"Unexpected M5911 gene count: {len(genes)} / {len(set(genes))}")
    return description, genes


def parse_series_metadata(data: bytes) -> tuple[list[dict[str, str]], list[str]]:
    text = gzip.decompress(data).decode("utf-8")
    metadata: dict[str, list[str]] = {}
    table_columns: list[str] = []
    for line in text.splitlines():
        if line.startswith("!Sample_"):
            fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
            metadata[fields[0]] = fields[1:]
        elif line.startswith('"ID_REF"'):
            table_columns = next(csv.reader([line], delimiter="\t", quotechar='"'))
            break
    accessions = metadata.get("!Sample_geo_accession", [])
    titles = metadata.get("!Sample_title", [])
    if len(accessions) != 6 or len(titles) != 6:
        raise ValueError(f"Unexpected GSE23307 sample metadata: {len(accessions)}, {len(titles)}")
    rows = []
    for index, (accession, title) in enumerate(zip(accessions, titles, strict=True), start=1):
        title_lower = title.lower()
        cell_type = "B_cell" if title_lower.startswith("b cells") else "monocyte"
        condition = (
            "IFN_beta" if "ifn-beta" in title_lower else "control" if "control" in title_lower else "unknown"
        )
        donor_match = re.search(r"hi no\.(\d+)", title_lower)
        donor_id = f"HI{donor_match.group(1)}" if donor_match else "unknown"
        include = cell_type == "B_cell" and donor_id in {"HI1", "HI2"} and condition != "unknown"
        rows.append(
            {
                "sample_order": index,
                "geo_accession": accession,
                "title": title,
                "cell_type": cell_type,
                "donor_id": donor_id,
                "condition": condition,
                "include_paired_bcell": include,
            }
        )
    included = [row for row in rows if row["include_paired_bcell"]]
    if len(included) != 4:
        raise ValueError(f"Expected four paired B-cell samples, found {len(included)}")
    for donor in ("HI1", "HI2"):
        conditions = {row["condition"] for row in included if row["donor_id"] == donor}
        if conditions != {"IFN_beta", "control"}:
            raise ValueError(f"Incomplete pair for {donor}: {conditions}")
    return rows, table_columns


def parse_platform_annotation(data: bytes) -> dict[str, Any]:
    text = gzip.decompress(data).decode("utf-8", errors="replace")
    header: list[str] | None = None
    row_count = 0
    in_table = False
    for line in text.splitlines():
        if line == "!platform_table_begin":
            in_table = True
            continue
        if line == "!platform_table_end":
            break
        if not in_table or not line.strip():
            continue
        fields = next(csv.reader([line], delimiter="\t", quotechar='"'))
        if header is None:
            header = fields
        else:
            row_count += 1
    if header is None or row_count == 0:
        raise ValueError("GPL6104 annotation is empty")
    symbol_candidates = [
        name for name in header if "symbol" in name.lower() or name.lower() == "gene symbol"
    ]
    return {
        "columns": header,
        "annotation_rows": row_count,
        "symbol_column_candidates": symbol_candidates,
    }


def read_frozen_ifn_genes(root: Path) -> list[str]:
    with (root / PROGRAM_DICTIONARY).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    genes = [
        row["gene_symbol"].upper()
        for row in rows
        if row["program_id"] == "IFN_ISG" and float(row["sign"]) > 0
    ]
    if len(genes) != 12 or len(set(genes)) != 12:
        raise ValueError(f"Expected 12 frozen IFN genes, found {genes}")
    return genes


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    resources = out_dir / "resources"
    resources.mkdir(parents=True, exist_ok=True)

    msigdb_path = resources / "h.all.v2026.1.Hs.symbols.gmt"
    matrix_path = resources / "GSE23307_series_matrix.txt.gz"
    annot_path = resources / "GPL6104.annot.gz"
    msigdb_data, msigdb_mode = retrieve(MSIGDB_URL, msigdb_path, args.refresh)
    matrix_data, matrix_mode = retrieve(GSE23307_MATRIX_URL, matrix_path, args.refresh)
    annot_data, annot_mode = retrieve(GPL6104_ANNOT_URL, annot_path, args.refresh)

    msigdb_description, msigdb_genes = parse_msigdb(msigdb_data)
    sample_rows, table_columns = parse_series_metadata(matrix_data)
    annotation = parse_platform_annotation(annot_data)
    frozen_ifn = read_frozen_ifn_genes(root)

    gene_rows = [
        {
            "systematic_id": "M5911",
            "standard_name": "HALLMARK_INTERFERON_ALPHA_RESPONSE",
            "msigdb_version": MSIGDB_VERSION,
            "ordinal": index,
            "gene_symbol": gene,
            "in_frozen_12_gene_ifn_arm": gene in frozen_ifn,
        }
        for index, gene in enumerate(msigdb_genes, start=1)
    ]
    write_csv(
        out_dir / "05_MSIGDB_M5911_GENE_SET.csv",
        gene_rows,
        [
            "systematic_id",
            "standard_name",
            "msigdb_version",
            "ordinal",
            "gene_symbol",
            "in_frozen_12_gene_ifn_arm",
        ],
    )
    write_csv(
        out_dir / "06_GSE23307_SAMPLE_PAIRING.csv",
        sample_rows,
        [
            "sample_order",
            "geo_accession",
            "title",
            "cell_type",
            "donor_id",
            "condition",
            "include_paired_bcell",
        ],
    )

    resource_rows = []
    for resource_id, url, path, data, mode in [
        ("MSIGDB_HALLMARK_2026_1", MSIGDB_URL, msigdb_path, msigdb_data, msigdb_mode),
        ("GSE23307_SERIES_MATRIX", GSE23307_MATRIX_URL, matrix_path, matrix_data, matrix_mode),
        ("GPL6104_ANNOTATION", GPL6104_ANNOT_URL, annot_path, annot_data, annot_mode),
    ]:
        resource_rows.append(
            {
                "resource_id": resource_id,
                "url": url,
                "project_relative_path": path.relative_to(root).as_posix(),
                "size_bytes": len(data),
                "sha256": sha256(data),
                "source_mode": mode,
                "repository_policy": "local_recomputable",
            }
        )
    write_csv(
        out_dir / "07_EXTERNAL_RESOURCE_MANIFEST.csv",
        resource_rows,
        [
            "resource_id",
            "url",
            "project_relative_path",
            "size_bytes",
            "sha256",
            "source_mode",
            "repository_policy",
        ],
    )

    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "PRE_EFFECT_EXTERNAL_RESOURCES_FROZEN",
        "regulatory_effects_inspected": False,
        "expression_effects_inspected": False,
        "msigdb": {
            "version": MSIGDB_VERSION,
            "systematic_id": "M5911",
            "standard_name": "HALLMARK_INTERFERON_ALPHA_RESPONSE",
            "description_url": msigdb_description,
            "genes": len(msigdb_genes),
            "frozen_12_gene_overlap": len(set(msigdb_genes) & set(frozen_ifn)),
        },
        "gse23307": {
            "samples": len(sample_rows),
            "paired_bcell_samples": sum(bool(row["include_paired_bcell"]) for row in sample_rows),
            "paired_donors": ["HI1", "HI2"],
            "matrix_columns": len(table_columns),
            "platform": "GPL6104",
            "platform_annotation_rows": annotation["annotation_rows"],
            "symbol_column_candidates": annotation["symbol_column_candidates"],
        },
        "resource_checks": {
            "msigdb_exact_97_unique": len(msigdb_genes) == 97 and len(set(msigdb_genes)) == 97,
            "frozen_ifn_exact_12_unique": len(frozen_ifn) == 12 and len(set(frozen_ifn)) == 12,
            "gse23307_two_complete_pairs": all(
                {
                    row["condition"]
                    for row in sample_rows
                    if row["include_paired_bcell"] and row["donor_id"] == donor
                }
                == {"IFN_beta", "control"}
                for donor in ("HI1", "HI2")
            ),
            "platform_annotation_present": annotation["annotation_rows"] > 0,
        },
    }
    write_text(out_dir / "08_EXTERNAL_RESOURCE_FREEZE.json", json.dumps(payload, indent=2))
    report = [
        "# Gate C6B external-resource freeze",
        "",
        f"**Status:** `{payload['status']}`",
        "",
        "No disease-ranked regulator activity or GSE23307 expression difference was calculated.",
        "",
        "## MSigDB",
        "",
        f"- human release: `{MSIGDB_VERSION}`",
        "- set: `M5911 / HALLMARK_INTERFERON_ALPHA_RESPONSE`",
        f"- members: {len(msigdb_genes)} unique gene symbols",
        f"- overlap with frozen 12-gene IFN arm: {payload['msigdb']['frozen_12_gene_overlap']}/12",
        f"- GMT SHA-256: `{resource_rows[0]['sha256']}`",
        "",
        "## GSE23307",
        "",
        "- paired B-cell donors: HI1 and HI2",
        "- conditions per donor: IFN-beta and untreated control",
        "- monocyte samples excluded from the frozen B-cell perturbation comparison",
        f"- series-matrix SHA-256: `{resource_rows[1]['sha256']}`",
        f"- GPL6104 annotation SHA-256: `{resource_rows[2]['sha256']}`",
        f"- annotation rows: {annotation['annotation_rows']:,}",
        "",
        "## Lock",
        "",
        "Expression rows remain locked until Gate C6B-1 software and synthetic-data "
        "qualification passes. GSE23307 has two paired donors and will be reported "
        "directionally without a powered P value.",
    ]
    write_text(out_dir / "08_EXTERNAL_RESOURCE_FREEZE.md", "\n".join(report))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
