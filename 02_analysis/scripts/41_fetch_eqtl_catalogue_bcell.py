#!/usr/bin/env python
"""Fetch prespecified B-cell eQTL Catalogue associations for target genes."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_BASE = "https://www.ebi.ac.uk/eqtl/api/v2"
PAGE_SIZE = 1000
TARGET_GENES = [
    "ZEB2",
    "TBX21",
    "ITGAX",
    "FCRL5",
    "FCRL3",
    "CD74",
]
DATASETS = [
    {
        "dataset_id": "QTD000080",
        "study_id": "QTS000009",
        "study_label": "Fairfax_2012",
        "sample_group": "B-cell_CD19",
        "sample_size": 281,
        "quant_method": "microarray",
        "evidence_tier": "primary_purified",
    },
    {
        "dataset_id": "QTD000073",
        "study_id": "QTS000007",
        "study_label": "CEDAR",
        "sample_group": "B-cell_CD19",
        "sample_size": 262,
        "quant_method": "microarray",
        "evidence_tier": "primary_purified",
    },
    {
        "dataset_id": "QTD000606",
        "study_id": "QTS000038",
        "study_label": "OneK1K",
        "sample_group": "B_intermediate",
        "sample_size": 977,
        "quant_method": "ge",
        "evidence_tier": "single_cell_replication",
    },
    {
        "dataset_id": "QTD000607",
        "study_id": "QTS000038",
        "study_label": "OneK1K",
        "sample_group": "B_memory",
        "sample_size": 981,
        "quant_method": "ge",
        "evidence_tier": "single_cell_replication",
    },
    {
        "dataset_id": "QTD000608",
        "study_id": "QTS000038",
        "study_label": "OneK1K",
        "sample_group": "B_naive",
        "sample_size": 980,
        "quant_method": "ge",
        "evidence_tier": "single_cell_replication",
    },
    {
        "dataset_id": "QTD000623",
        "study_id": "QTS000038",
        "study_label": "OneK1K",
        "sample_group": "Plasmablast",
        "sample_size": 795,
        "quant_method": "ge",
        "evidence_tier": "single_cell_replication",
    },
    {
        "dataset_id": "QTD000597",
        "study_id": "QTS000037",
        "study_label": "Perez_2022",
        "sample_group": "B",
        "sample_size": 191,
        "quant_method": "ge",
        "evidence_tier": "lupus_context_replication",
    },
    {
        "dataset_id": "QTD000474",
        "study_id": "QTS000026",
        "study_label": "Schmiedel_2018",
        "sample_group": "B-cell_naive",
        "sample_size": 91,
        "quant_method": "ge",
        "evidence_tier": "immune_reference_replication",
    },
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def make_session() -> requests.Session:
    retry = Retry(
        total=6,
        connect=6,
        read=6,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"Accept": "application/json"})
    return session


def fetch_associations(
    session: requests.Session,
    dataset_id: str,
    gene_id: str,
) -> tuple[list[dict], str]:
    rows: list[dict] = []
    start = 0
    while True:
        response = session.get(
            f"{API_BASE}/datasets/{dataset_id}/associations",
            params={"size": PAGE_SIZE, "start": start, "gene_id": gene_id},
            timeout=90,
        )
        no_results = response.status_code in (400, 404) and "No results" in response.text
        if no_results:
            if start == 0:
                return [], "not_available_in_released_matrix"
            break
        response.raise_for_status()
        payload = response.json()
        page = payload.get("value", []) if isinstance(payload, dict) else payload
        if not page:
            break
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        start += PAGE_SIZE
        time.sleep(0.15)
    return rows, "available" if rows else "not_available_in_released_matrix"


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loci",
        type=Path,
        default=root
        / "03_results"
        / "regulatory_evidence"
        / "tables"
        / "target_gene_loci_grch38.csv",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "03_results" / "regulatory_evidence" / "eqtl_catalogue",
    )
    args = parser.parse_args()

    loci = pd.read_csv(args.loci)
    loci = loci[loci["gene_symbol"].isin(TARGET_GENES)].copy()
    gene_lookup = dict(zip(loci["gene_symbol"], loci["ensembl_gene_id"]))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables_dir = args.out_dir.parent / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(DATASETS).to_csv(
        tables_dir / "prespecified_bcell_eqtl_datasets.csv", index=False
    )

    session = make_session()
    summary_rows: list[dict] = []
    for dataset in DATASETS:
        for symbol in TARGET_GENES:
            gene_id = gene_lookup[symbol]
            rows, status = fetch_associations(
                session, dataset["dataset_id"], gene_id
            )
            record = {
                **dataset,
                "gene_symbol": symbol,
                "ensembl_gene_id": gene_id,
                "availability_status": status,
                "association_rows": len(rows),
                "molecular_trait_count": 0,
                "minimum_eqtl_p": None,
                "output_file": None,
            }
            if rows:
                frame = pd.DataFrame(rows)
                frame = frame.drop_duplicates(
                    subset=["molecular_trait_id", "variant"], keep="first"
                )
                frame.insert(0, "gene_symbol", symbol)
                for key, value in reversed(list(dataset.items())):
                    frame.insert(0, key, value)
                output_path = (
                    args.out_dir
                    / f"{dataset['dataset_id']}_{dataset['sample_group']}_{symbol}.tsv.gz"
                )
                frame.to_csv(output_path, sep="\t", index=False, compression="gzip")
                record["association_rows"] = len(frame)
                record["molecular_trait_count"] = int(
                    frame["molecular_trait_id"].nunique()
                )
                record["minimum_eqtl_p"] = float(frame["pvalue"].min())
                record["output_file"] = str(output_path)

            summary_rows.append(record)
            print(
                f"{dataset['dataset_id']} {symbol}: "
                f"{record['association_rows']} rows ({status})"
            )
            time.sleep(0.15)

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(tables_dir / "bcell_eqtl_target_availability.csv", index=False)

    metadata = {
        "api_base": API_BASE,
        "page_size": PAGE_SIZE,
        "target_genes": TARGET_GENES,
        "datasets": DATASETS,
        "interpretation": (
            "A not_available status means the molecular trait was absent from the "
            "released dataset matrix; it is not evidence for absence of an eQTL."
        ),
    }
    (tables_dir / "eqtl_catalogue_fetch_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    available = summary[summary["availability_status"] == "available"]
    print(
        f"\nAvailable gene-context pairs: {len(available)} / {len(summary)}; "
        f"associations: {available['association_rows'].sum():,}"
    )
    print(f"Summary: {tables_dir / 'bcell_eqtl_target_availability.csv'}")


if __name__ == "__main__":
    main()
