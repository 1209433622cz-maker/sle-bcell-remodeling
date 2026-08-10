from __future__ import annotations

import argparse
import tarfile
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "Data" / "processed" / "GSE135779_nehar_validation" / "source"
OUT_DIR = PROJECT_ROOT / "03_results" / "gse135779_validation_readiness"
TABLE_DIR = OUT_DIR / "tables"


def inspect_tar(raw_tar: Path, max_inner: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    inner_rows = []
    with tarfile.open(raw_tar, "r") as outer:
        members = outer.getmembers()
        for member in members:
            rows.append(
                {
                    "name": member.name,
                    "size_bytes": member.size,
                    "is_file": member.isfile(),
                    "suffix": "".join(Path(member.name).suffixes),
                }
            )
            if member.isfile() and member.name.endswith((".tar.gz", ".tgz")):
                handle = outer.extractfile(member)
                if handle is None:
                    continue
                try:
                    with tarfile.open(fileobj=handle, mode="r:gz") as inner:
                        for inner_member in inner.getmembers()[:max_inner]:
                            inner_rows.append(
                                {
                                    "outer_name": member.name,
                                    "inner_name": inner_member.name,
                                    "inner_size_bytes": inner_member.size,
                                    "inner_is_file": inner_member.isfile(),
                                    "inner_suffix": "".join(Path(inner_member.name).suffixes),
                                }
                            )
                except tarfile.TarError as exc:
                    inner_rows.append(
                        {
                            "outer_name": member.name,
                            "inner_name": f"ERROR: {exc}",
                            "inner_size_bytes": 0,
                            "inner_is_file": False,
                            "inner_suffix": "",
                        }
                    )
    return pd.DataFrame(rows), pd.DataFrame(inner_rows)


def write_summary(path: Path, raw_tar: Path, manifest: pd.DataFrame, inner_manifest: pd.DataFrame) -> None:
    lines = [
        "# GSE135779 RAW Tar Inspection",
        "",
        f"- Raw tar: `{raw_tar}`",
        f"- Outer entries: {len(manifest)}.",
        f"- Nested entries sampled: {len(inner_manifest)}.",
        "",
        "## Next Decision",
        "",
        "Use this manifest to decide whether the raw tar is organized as per-sample 10x matrices, a combined MTX/TSV package, or another custom layout. After this inspection, build the full GSE135779 B-cell validation parser against the observed structure.",
    ]
    if not manifest.empty:
        suffix_counts = manifest["suffix"].value_counts().reset_index()
        lines.extend(["", "## Outer Suffix Counts", ""])
        for row in suffix_counts.itertuples(index=False):
            lines.append(f"- {row.suffix or '[none]'}: {row.count}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_missing_summary(path: Path, raw_tar: Path) -> None:
    lines = [
        "# GSE135779 RAW Tar Inspection",
        "",
        f"`{raw_tar}` is not present yet.",
        "",
        "Download it from the project root with:",
        "",
        "```powershell",
        "powershell -ExecutionPolicy Bypass -File .\\02_analysis\\scripts\\00_download_gse135779_validation_sources.ps1 -DownloadRaw",
        "```",
        "",
        "Then rerun:",
        "",
        "```powershell",
        '& "C:\\ProgramData\\miniforge3\\condabin\\conda.bat" run -n sle-bcell python .\\02_analysis\\scripts\\29_inspect_gse135779_raw_tar.py',
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the GSE135779 processed RAW tar after download.")
    parser.add_argument("--raw-tar", default=str(SOURCE_DIR / "GSE135779_RAW.tar"))
    args = parser.parse_args()

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    raw_tar = Path(args.raw_tar)
    if not raw_tar.exists():
        write_missing_summary(OUT_DIR / "gse135779_raw_tar_inspection_summary.md", raw_tar)
        print(f"Missing {raw_tar}")
        print(f"Wrote instructions to {OUT_DIR / 'gse135779_raw_tar_inspection_summary.md'}")
        return

    manifest, inner_manifest = inspect_tar(raw_tar)
    manifest.to_csv(TABLE_DIR / "gse135779_raw_tar_manifest.csv", index=False)
    inner_manifest.to_csv(TABLE_DIR / "gse135779_raw_tar_inner_manifest.csv", index=False)
    write_summary(OUT_DIR / "gse135779_raw_tar_inspection_summary.md", raw_tar, manifest, inner_manifest)
    print(f"Wrote raw tar inspection outputs to {OUT_DIR}")
    print(manifest.head(30).to_string(index=False))


if __name__ == "__main__":
    main()
