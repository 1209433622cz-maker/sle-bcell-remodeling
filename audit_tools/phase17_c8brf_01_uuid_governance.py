#!/usr/bin/env python3
"""Audit Figure 2 sample UUID provenance and publication privacy."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "phase17_v7" / "gateC8BRF" / "20260825_author_release"
FIGURE2 = RUN_DIR / "source_data" / "Figure2_source_data.csv"
MODEL = ROOT / "phase17_v7" / "gateC3" / "20260815_metadata_design" / "11_primary_model_matrix.csv"
LOO = ROOT / "phase17_v7" / "gateC3A" / "20260815_frozen_abundance" / "06_primary_leave_one_out.csv"
H5AD_INFO = ROOT / "02_analysis" / "data_inventory" / "h5ad_inspection" / "GSE174188_cellxgene" / "basic_info.json"
OBS_SUMMARY = ROOT / "02_analysis" / "data_inventory" / "h5ad_inspection" / "GSE174188_cellxgene" / "obs_columns_summary.csv"
COLLECTION = ROOT / "00_project_management" / "cellxgene_collection_436154da_2026-06-22.json"
SOURCE_H5AD = ROOT / "Data" / "processed" / "GSE174188_perez_cellxgene" / "perez_gse174188_cellxgene.h5ad"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def nonempty(frame: pd.DataFrame, column: str) -> set[str]:
    return set(frame[column].dropna().astype(str))


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    figure = pd.read_csv(FIGURE2)
    model = pd.read_csv(MODEL)
    loo = pd.read_csv(LOO)
    h5ad_info = json.loads(H5AD_INFO.read_text(encoding="utf-8-sig"))
    obs_summary = pd.read_csv(OBS_SUMMARY)
    collection = json.loads(COLLECTION.read_text(encoding="utf-8-sig"))

    figure_sample_ids = nonempty(figure, "sample_uuid")
    figure_omitted_ids = nonempty(figure, "omitted_sample_uuid")
    figure_ids = figure_sample_ids | figure_omitted_ids
    upstream_ids = nonempty(model, "sample_uuid") | nonempty(loo, "omitted_sample_uuid")
    parsed = {value: uuid.UUID(value) for value in figure_ids}
    uuid_versions = sorted({item.version for item in parsed.values()})
    unmapped = sorted(figure_ids - upstream_ids)

    sample_obs = obs_summary.loc[obs_summary["column"].eq("sample_uuid")]
    if len(sample_obs) != 1:
        raise RuntimeError("Expected one sample_uuid row in public H5AD inventory")
    public_unique = int(sample_obs.iloc[0]["n_unique"])
    asset = collection["datasets"][0]["assets"][0]
    forbidden = {
        "name",
        "patient_name",
        "medical_record_number",
        "mrn",
        "email",
        "phone",
        "address",
        "date_of_birth",
        "dob",
    }
    forbidden_present = sorted(forbidden.intersection(map(str.lower, figure.columns)))

    checks = {
        "source_collection_is_public": collection.get("visibility") == "PUBLIC",
        "source_asset_url_is_public_cellxgene": str(asset["url"]).startswith(
            "https://datasets.cellxgene.cziscience.com/"
        ),
        "source_h5ad_size_matches_public_asset": SOURCE_H5AD.stat().st_size
        == int(asset["filesize"]),
        "sample_uuid_is_direct_public_obs_column": "sample_uuid" in h5ad_info["obs_columns"],
        "public_h5ad_reports_274_sample_uuid_values": public_unique == 274,
        "figure_ids_are_uuid_v4": uuid_versions == [4],
        "figure_ids_map_to_frozen_analysis_inputs": not unmapped,
        "no_direct_identifier_columns_in_figure_source": not forbidden_present,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Figure 2 UUID governance failed: {checks}")

    status = {
        "created_at": "2026-08-25",
        "status": "PASS_FIGURE2_PUBLIC_NON_IDENTIFYING_SOURCE_UUIDS",
        "decision": "retain sample_uuid and omitted_sample_uuid",
        "rationale": (
            "They are UUIDv4 values copied from the public CELLxGENE H5AD obs.sample_uuid "
            "field and are the frozen biological analysis unit; they are not locally generated "
            "author identifiers or direct personal identifiers."
        ),
        "public_collection_url": collection["collection_url"],
        "public_dataset_url": asset["url"],
        "public_dataset_visibility": collection["visibility"],
        "source_h5ad_bytes": SOURCE_H5AD.stat().st_size,
        "source_h5ad_inventory_sha256": sha256(H5AD_INFO),
        "figure2_source_sha256": sha256(FIGURE2),
        "figure_sample_uuid_count": len(figure_sample_ids),
        "figure_omitted_sample_uuid_count": len(figure_omitted_ids),
        "figure_union_uuid_count": len(figure_ids),
        "public_h5ad_sample_uuid_count": public_unique,
        "uuid_versions": uuid_versions,
        "unmapped_figure_ids": unmapped,
        "forbidden_direct_identifier_columns": forbidden_present,
        "checks": checks,
    }
    (RUN_DIR / "03_FIGURE2_UUID_GOVERNANCE.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    report = f"""# Figure 2 UUID governance audit

**Decision:** `{status['status']}`

The 90 unique values in `sample_uuid` and `omitted_sample_uuid` are retained. They are UUIDv4 identifiers carried from the public CELLxGENE H5AD `obs.sample_uuid` field through the frozen Gate C3 model matrix and Gate C3A leave-one-out analysis. All 90 publication values map to those frozen inputs; none is locally generated for a patient, and no direct identifying field is present in Figure 2 Source Data.

Public provenance: {collection['collection_url']}

- Public source H5AD: {SOURCE_H5AD.relative_to(ROOT).as_posix()}
- Public asset size: {SOURCE_H5AD.stat().st_size:,} bytes, matching the CELLxGENE metadata
- Public H5AD `sample_uuid` levels: {public_unique}
- Figure 2 UUID union: {len(figure_ids)}
- UUID version set: {uuid_versions}
- Unmapped publication IDs: {len(unmapped)}
- Direct identifier columns: {len(forbidden_present)}

No substitution with a local analysis index is required.
"""
    (RUN_DIR / "03_FIGURE2_UUID_GOVERNANCE.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
