#!/usr/bin/env python
"""Prepare prespecified GRCh38 SLE GWAS loci for regulatory follow-up."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import pandas as pd
import requests


TARGET_GENES = [
    "ZEB2",
    "TBX21",
    "ITGAX",
    "FCRL5",
    "FCRL3",
    "CD74",
    "HLA-DRA",
    "HLA-DRB1",
    "HLA-DPA1",
    "HLA-DPB1",
]
MHC_GENES = {"HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1"}
WINDOW_BP = 1_000_000
ENSEMBL_REST = "https://rest.ensembl.org"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def fetch_gene_coordinates(symbols: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    for symbol in symbols:
        response = requests.get(
            f"{ENSEMBL_REST}/lookup/symbol/homo_sapiens/{symbol}",
            params={"expand": 0},
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        item = response.json()
        rows.append(
            {
                "gene_symbol": symbol,
                "ensembl_gene_id": item["id"].split(".")[0],
                "chromosome": str(item["seq_region_name"]),
                "gene_start": int(item["start"]),
                "gene_end": int(item["end"]),
                "strand": int(item["strand"]),
                "locus_start": max(1, int(item["start"]) - WINDOW_BP),
                "locus_end": int(item["end"]) + WINDOW_BP,
                "window_bp": WINDOW_BP,
                "mhc_complex_region": symbol in MHC_GENES,
                "genome_build": "GRCh38",
                "coordinate_source": "Ensembl REST lookup/symbol",
            }
        )
    return pd.DataFrame(rows)


def detect_columns(columns: list[str]) -> tuple[str, str]:
    chromosome_candidates = ["chromosome", "hm_chrom"]
    position_candidates = ["base_pair_location", "hm_pos"]
    chrom_col = next((name for name in chromosome_candidates if name in columns), None)
    pos_col = next((name for name in position_candidates if name in columns), None)
    if not chrom_col or not pos_col:
        raise ValueError(
            "Could not identify chromosome and position columns. "
            f"Observed columns: {columns}"
        )
    return chrom_col, pos_col


def extract_loci(
    gwas_path: Path,
    loci: pd.DataFrame,
    out_dir: Path,
    chunk_size: int,
    accession: str,
) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    handles: dict[str, gzip.GzipFile] = {}
    counts = {symbol: 0 for symbol in loci["gene_symbol"]}
    header_written = {symbol: False for symbol in loci["gene_symbol"]}
    locus_records = loci.to_dict(orient="records")

    try:
        reader = pd.read_csv(
            gwas_path,
            sep="\t",
            compression="gzip",
            chunksize=chunk_size,
            low_memory=False,
        )
        for chunk_number, chunk in enumerate(reader, start=1):
            if chunk_number == 1:
                chrom_col, pos_col = detect_columns(list(chunk.columns))
            chunk[chrom_col] = chunk[chrom_col].astype(str).str.replace("chr", "", regex=False)
            position = pd.to_numeric(chunk[pos_col], errors="coerce")

            for locus in locus_records:
                symbol = locus["gene_symbol"]
                mask = (
                    (chunk[chrom_col] == str(locus["chromosome"]))
                    & position.between(locus["locus_start"], locus["locus_end"])
                )
                subset = chunk.loc[mask]
                if subset.empty:
                    continue

                output_path = out_dir / f"{accession}_{symbol}_plusminus1Mb.tsv.gz"
                if symbol not in handles:
                    handles[symbol] = gzip.open(output_path, "wt", encoding="utf-8", newline="")
                subset.to_csv(
                    handles[symbol],
                    sep="\t",
                    index=False,
                    header=not header_written[symbol],
                )
                header_written[symbol] = True
                counts[symbol] += len(subset)
    finally:
        for handle in handles.values():
            handle.close()

    return pd.DataFrame(
        [
            {
                "gene_symbol": row["gene_symbol"],
                "chromosome": row["chromosome"],
                "locus_start": row["locus_start"],
                "locus_end": row["locus_end"],
                "variant_rows": counts[row["gene_symbol"]],
                "mhc_complex_region": row["mhc_complex_region"],
                "output_file": str(
                    out_dir
                    / f"{accession}_{row['gene_symbol']}_plusminus1Mb.tsv.gz"
                ),
            }
            for row in locus_records
        ]
    )


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gwas",
        type=Path,
        default=root
        / "Data"
        / "external_regulatory"
        / "GCST90558100"
        / "GCST90558100.h.tsv.gz",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "03_results" / "regulatory_evidence" / "gwas_loci",
    )
    parser.add_argument("--accession", default="GCST90558100")
    parser.add_argument("--chunk-size", type=int, default=500_000)
    args = parser.parse_args()

    if not args.gwas.exists():
        raise FileNotFoundError(
            f"Missing GWAS file: {args.gwas}. Run 00_download_sle_gwas_gcst90558100.ps1."
        )

    tables_dir = args.out_dir.parent / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    loci = fetch_gene_coordinates(TARGET_GENES)
    loci.to_csv(tables_dir / "target_gene_loci_grch38.csv", index=False)

    extraction = extract_loci(
        args.gwas, loci, args.out_dir, args.chunk_size, args.accession
    )
    extraction.to_csv(
        tables_dir / f"{args.accession}_gwas_locus_extraction_summary.csv",
        index=False,
    )

    metadata = {
        "gwas_accession": args.accession,
        "genome_build": "GRCh38",
        "window_bp": WINDOW_BP,
        "target_genes": TARGET_GENES,
        "mhc_genes": sorted(MHC_GENES),
        "source_file": str(args.gwas.resolve()),
        "coordinate_source": ENSEMBL_REST,
    }
    (tables_dir / f"regulatory_locus_preparation_metadata_{args.accession}.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(extraction.to_string(index=False))
    print(f"\nWrote loci to: {args.out_dir}")
    print(f"Wrote metadata to: {tables_dir}")


if __name__ == "__main__":
    main()
