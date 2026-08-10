from __future__ import annotations

import gzip
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE135779_nehar_validation" / "source"
OUT_DIR = PROJECT_ROOT / "03_results" / "gse135779_validation_readiness"
TABLE_DIR = OUT_DIR / "tables"

PROGRAMS = {
    "ABC_APC_focus": ["FCRL5", "FCRL3", "ZEB2", "ITGAX", "TBX21", "CD74", "HLA-DRA", "HLA-DPB1", "MS4A1"],
    "ABC_DN2_core": ["TBX21", "ITGAX", "FCRL5", "FCRL3", "ZEB2", "CXCR3", "TLR7"],
    "APC_HLA": ["CD74", "HLA-DRA", "HLA-DRB1", "HLA-DPA1", "HLA-DPB1", "CIITA", "CD86"],
    "IFN_ISG": ["ISG15", "IFIT1", "IFIT2", "IFIT3", "MX1", "MX2", "OAS1", "OAS2", "IFI44L", "IFI6"],
    "Naive_B": ["TCL1A", "VPREB3", "IGHD", "IL4R", "CXCR4", "CD79B"],
    "Plasmablast_ASC": ["XBP1", "PRDM1", "MZB1", "JCHAIN", "SDC1", "TNFRSF17"],
}


def read_series_field(path: Path, prefix: str) -> list[str]:
    values: list[str] = []
    with gzip.open(path, "rt", errors="replace") as handle:
        for line in handle:
            if line.startswith(prefix):
                value = line.split("\t", 1)[1].strip().strip('"')
                values.append(value)
    return values


def load_metadata() -> tuple[pd.DataFrame, pd.DataFrame]:
    csle = pd.read_csv(SOURCE_DIR / "Meta_cSLE_processed_0809202_small.csv")
    casle = pd.read_csv(SOURCE_DIR / "Meta_caSLE_processed_08092021_small.csv")
    for df, cohort in [(csle, "childhood"), (casle, "childhood_adult")]:
        df["cohort_file"] = cohort
        df["sample_name"] = df["Names"].astype(str)
        df["disease_label"] = df["sample_name"].str.extract(r"^([ca]?SLE|[ca]?HD)", expand=False)
        df["disease_group"] = df["sample_name"].map(
            lambda x: "SLE" if "SLE" in str(x).upper() else ("HC" if "HD" in str(x).upper() else "unknown")
        )
        df["is_b_subcluster"] = df["subclusters"].astype(str).str.upper().str.startswith("B")
    return csle, casle


def read_genes() -> pd.DataFrame:
    path = SOURCE_DIR / "GSE135779_genes.tsv.gz"
    genes = pd.read_csv(path, sep="\t", header=None)
    if genes.shape[1] == 1:
        genes.columns = ["gene_symbol"]
        genes["gene_id"] = genes["gene_symbol"]
    else:
        genes = genes.iloc[:, :2]
        genes.columns = ["gene_id", "gene_symbol"]
    genes["gene_symbol_upper"] = genes["gene_symbol"].astype(str).str.upper()
    return genes


def summarize_metadata(csle: pd.DataFrame, casle: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_meta = pd.concat([csle, casle], ignore_index=True, sort=False)
    summary = (
        all_meta.groupby(["cohort_file", "disease_group"], observed=True)
        .agg(
            n_cells=("index", "size"),
            n_donors=("Names", "nunique"),
            n_ids=("IDs", "nunique"),
            n_b_subcluster_cells=("is_b_subcluster", "sum"),
        )
        .reset_index()
    )
    donor_summary = (
        all_meta.groupby(["cohort_file", "Names", "IDs", "disease_group"], observed=True)
        .agg(n_cells=("index", "size"), n_b_subcluster_cells=("is_b_subcluster", "sum"))
        .reset_index()
    )
    subcluster_summary = (
        all_meta.groupby(["cohort_file", "disease_group", "subclusters"], observed=True)
        .size()
        .reset_index(name="n_cells")
        .sort_values(["cohort_file", "disease_group", "n_cells"], ascending=[True, True, False])
    )
    return summary, donor_summary, subcluster_summary


def marker_presence(genes: pd.DataFrame) -> pd.DataFrame:
    available = set(genes["gene_symbol_upper"])
    rows = []
    for program, gene_list in PROGRAMS.items():
        for gene in gene_list:
            rows.append({"program": program, "gene": gene, "present": gene.upper() in available})
    return pd.DataFrame(rows)


def write_summary(
    path: Path,
    series_summary: str,
    series_design: str,
    summary: pd.DataFrame,
    donor_summary: pd.DataFrame,
    presence: pd.DataFrame,
    raw_exists: bool,
) -> None:
    extended = summary[summary["cohort_file"] == "childhood_adult"]
    extended_cells = int(extended["n_cells"].sum())
    extended_b_cells = int(extended["n_b_subcluster_cells"].sum())
    extended_donors = int(donor_summary.loc[donor_summary["cohort_file"] == "childhood_adult", "Names"].nunique())
    lines = [
        "# GSE135779 Validation Readiness Summary",
        "",
        "## Source",
        "",
        "- GEO accession: GSE135779.",
        "- Primary paper: Nehar-Belaid et al., Nature Immunology 2020.",
        f"- Series summary: {series_summary}",
        f"- Overall design: {series_design}",
        "",
        "## Local Source Status",
        "",
        f"- Metadata files downloaded: yes.",
        f"- Gene list downloaded: yes.",
        f"- Processed RAW tar downloaded: {'yes' if raw_exists else 'no'}; expected size 1,299,783,680 bytes.",
        "",
        "## Metadata Readiness",
        "",
        "- Two metadata files are present: one childhood-only file and one childhood-plus-adult extended file. They should not be summed as independent cohorts.",
        f"- Extended childhood-plus-adult metadata rows/cells: {extended_cells:,}.",
        f"- Extended unique donor/sample names: {extended_donors}.",
        f"- Extended B-subcluster metadata rows: {extended_b_cells:,}.",
        "",
        "## Program Gene Coverage",
        "",
    ]
    coverage = presence.groupby("program")["present"].agg(["sum", "count"]).reset_index()
    for row in coverage.itertuples(index=False):
        lines.append(f"- {row.program}: {int(row.sum)}/{int(row.count)} genes present.")
    lines.extend(
        [
            "",
            "## Recommended Use",
            "",
            "After downloading `GSE135779_RAW.tar`, use this dataset as the main independent cohort-level validation layer. It is larger and more defensible than GSE163121, with pediatric and adult SLE/control cohorts and cell-level metadata containing B-cell subcluster labels.",
            "",
            "The first validation target should be donor-level B-subcluster scoring for ABC/DN2, ABC/APC-focus, APC/HLA, IFN/ISG, naive B, and plasmablast programs. If raw extraction is slow, begin with B-subcluster metadata and marker score summaries only.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    csle, casle = load_metadata()
    genes = read_genes()
    summary, donor_summary, subcluster_summary = summarize_metadata(csle, casle)
    presence = marker_presence(genes)

    series_path = SOURCE_DIR / "GSE135779_series_matrix.txt.gz"
    series_summary = " ".join(read_series_field(series_path, "!Series_summary"))
    series_design = " ".join(read_series_field(series_path, "!Series_overall_design"))
    raw_exists = (SOURCE_DIR / "GSE135779_RAW.tar").exists()

    summary.to_csv(TABLE_DIR / "gse135779_metadata_summary.csv", index=False)
    donor_summary.to_csv(TABLE_DIR / "gse135779_donor_metadata_summary.csv", index=False)
    subcluster_summary.to_csv(TABLE_DIR / "gse135779_subcluster_counts.csv", index=False)
    presence.to_csv(TABLE_DIR / "gse135779_program_gene_presence.csv", index=False)
    write_summary(OUT_DIR / "gse135779_validation_readiness_summary.md", series_summary, series_design, summary, donor_summary, presence, raw_exists)

    print(f"Wrote GSE135779 readiness outputs to {OUT_DIR}")
    print(summary.to_string(index=False))
    print(presence.groupby("program")["present"].agg(["sum", "count"]).to_string())


if __name__ == "__main__":
    main()
