from __future__ import annotations

import json
from pathlib import Path

import anndata as ad
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE196830_onek1k_cellxgene" / "source"
OUT_DIR = PROJECT_ROOT / "03_results" / "onek1k_cellxgene_inspection"
TABLE_DIR = OUT_DIR / "tables"

H5AD = SOURCE_DIR / "onek1k_gse196830_cellxgene.h5ad"
COLLECTION_JSON = SOURCE_DIR / "cellxgene_collection_onek1k_gse196830.json"

B_CELL_TERMS = ["B cell", "plasma cell", "plasmablast", "memory B cell", "naive B cell"]
GENES_OF_INTEREST = [
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
    "MS4A1",
    "ISG15",
    "IFIT1",
    "MX1",
    "TLR7",
    "FTO",
]


def top_counts(series: pd.Series, n: int = 30) -> pd.DataFrame:
    counts = series.astype(str).value_counts(dropna=False).head(n)
    return counts.rename_axis(series.name or "value").reset_index(name="n")


def detect_columns(obs: pd.DataFrame) -> dict[str, str | None]:
    candidates = {
        "cell_type": ["cell_type", "celltype", "cell_type_ontology_term_id", "author_cell_type", "label"],
        "donor": ["donor_id", "donor", "individual", "sample_id", "sample"],
        "assay": ["assay", "assay_ontology_term_id"],
        "disease": ["disease", "disease_ontology_term_id"],
        "tissue": ["tissue", "tissue_ontology_term_id"],
    }
    found: dict[str, str | None] = {}
    lowered = {col.lower(): col for col in obs.columns}
    for semantic, names in candidates.items():
        found[semantic] = None
        for name in names:
            if name.lower() in lowered:
                found[semantic] = lowered[name.lower()]
                break
    return found


def gene_presence(var: pd.DataFrame) -> pd.DataFrame:
    symbol_columns = [col for col in ["feature_name", "gene_symbol", "gene_name", "name"] if col in var.columns]
    symbols = set(var.index.astype(str).str.upper())
    for col in symbol_columns:
        symbols.update(var[col].astype(str).str.upper())
    rows = []
    for gene in GENES_OF_INTEREST:
        rows.append({"gene": gene, "present": gene.upper() in symbols})
    return pd.DataFrame(rows)


def b_cell_summary(obs: pd.DataFrame, cell_type_col: str | None, donor_col: str | None) -> pd.DataFrame:
    if cell_type_col is None:
        return pd.DataFrame()
    cell_type = obs[cell_type_col].astype(str)
    mask = cell_type.str.contains("|".join(B_CELL_TERMS), case=False, regex=True, na=False)
    rows = [
        {"metric": "b_lineage_like_cells", "value": int(mask.sum())},
        {"metric": "total_cells", "value": int(len(obs))},
    ]
    if donor_col is not None:
        rows.append({"metric": "b_lineage_like_donors", "value": int(obs.loc[mask, donor_col].astype(str).nunique())})
        rows.append({"metric": "total_donors", "value": int(obs[donor_col].astype(str).nunique())})
    return pd.DataFrame(rows)


def read_collection_metadata() -> dict[str, object]:
    if not COLLECTION_JSON.exists():
        return {}
    data = json.loads(COLLECTION_JSON.read_text(encoding="utf-8"))
    dataset = data.get("datasets", [{}])[0] if data.get("datasets") else {}
    return {
        "collection_id": data.get("collection_id"),
        "collection_name": data.get("name"),
        "collection_doi": data.get("doi"),
        "dataset_id": dataset.get("dataset_id"),
        "dataset_title": dataset.get("title"),
        "cell_count": dataset.get("cell_count"),
        "published_at": data.get("published_at"),
        "h5ad_asset_size": next((a.get("filesize") for a in dataset.get("assets", []) if a.get("filetype") == "H5AD"), None),
    }


def write_summary(
    path: Path,
    metadata: dict[str, object],
    adata: ad.AnnData,
    columns: dict[str, str | None],
    b_summary: pd.DataFrame,
    gene_table: pd.DataFrame,
) -> None:
    lines = [
        "# OneK1K / GSE196830 CELLxGENE Inspection",
        "",
        "## Source",
        "",
        f"- Collection: {metadata.get('collection_name', 'unknown')}.",
        f"- Collection ID: `{metadata.get('collection_id', 'unknown')}`.",
        f"- Dataset ID: `{metadata.get('dataset_id', 'unknown')}`.",
        f"- DOI: {metadata.get('collection_doi', 'not recorded')}.",
        f"- Downloaded H5AD size: {H5AD.stat().st_size:,} bytes.",
        "",
        "## H5AD Structure",
        "",
        f"- Cells: {adata.n_obs:,}.",
        f"- Features: {adata.n_vars:,}.",
        f"- Layers: {', '.join(adata.layers.keys()) if len(adata.layers.keys()) else 'none visible in backed mode'}.",
        f"- Obsm keys: {', '.join(adata.obsm.keys()) if len(adata.obsm.keys()) else 'none'}.",
        f"- Obs columns: {len(adata.obs.columns)}.",
        f"- Var columns: {len(adata.var.columns)}.",
        "",
        "## Detected Metadata Columns",
        "",
    ]
    for key, value in columns.items():
        lines.append(f"- {key}: `{value}`")
    if not b_summary.empty:
        lines.extend(["", "## B-Lineage-Like Scan", ""])
        for row in b_summary.itertuples(index=False):
            lines.append(f"- {row.metric}: {row.value:,}")
    present = int(gene_table["present"].sum())
    lines.extend(
        [
            "",
            "## Gene Coverage For Current Manuscript Axes",
            "",
            f"- Genes present: {present}/{len(gene_table)}.",
            "- Missing genes: "
            + ("; ".join(gene_table.loc[~gene_table["present"], "gene"].tolist()) if present < len(gene_table) else "none."),
            "",
            "## Recommended Use",
            "",
            "Use OneK1K as an external immune reference, not as another SLE validation cohort. The most appropriate next analysis is a compact B-cell reference/regulatory context table for manuscript genes including `ZEB2`, `TBX21`, `ITGAX`, `FCRL5/FCRL3`, HLA/CD74, and IFN/ISG genes.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not H5AD.exists():
        raise FileNotFoundError(f"Missing {H5AD}. Run 00_download_onek1k_gse196830_cellxgene.ps1 first.")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    metadata = read_collection_metadata()
    adata = ad.read_h5ad(H5AD, backed="r")
    obs = adata.obs.copy()
    var = adata.var.copy()
    columns = detect_columns(obs)
    gene_table = gene_presence(var)
    b_summary = b_cell_summary(obs, columns["cell_type"], columns["donor"])

    pd.DataFrame([metadata]).to_csv(TABLE_DIR / "onek1k_cellxgene_collection_metadata.csv", index=False)
    pd.DataFrame({"obs_column": obs.columns}).to_csv(TABLE_DIR / "onek1k_obs_columns.csv", index=False)
    pd.DataFrame({"var_column": var.columns}).to_csv(TABLE_DIR / "onek1k_var_columns.csv", index=False)
    gene_table.to_csv(TABLE_DIR / "onek1k_manuscript_gene_presence.csv", index=False)
    if not b_summary.empty:
        b_summary.to_csv(TABLE_DIR / "onek1k_b_lineage_like_summary.csv", index=False)
    for semantic, col in columns.items():
        if col is not None and col in obs.columns:
            top_counts(obs[col], 40).to_csv(TABLE_DIR / f"onek1k_top_{semantic}_counts.csv", index=False)

    write_summary(OUT_DIR / "onek1k_cellxgene_inspection_summary.md", metadata, adata, columns, b_summary, gene_table)
    adata.file.close()

    print(f"Wrote OneK1K inspection outputs to {OUT_DIR}")
    print(f"Shape: {adata.n_obs} cells x {adata.n_vars} features")
    print(pd.DataFrame([columns]).to_string(index=False))
    print(gene_table.to_string(index=False))


if __name__ == "__main__":
    main()
