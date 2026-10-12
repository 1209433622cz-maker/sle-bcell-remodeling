"""Build source-bound public summaries, copies and Git-scoped indexes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from verify_repository import FOLDERS, NAVIGATION, REPORT, sha256

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "phase17_v7/npj_sba_figure5_regulatory_ceiling/20260908_canonical_source_integration/figures/source_data"
GENERATED = {"0_admin/PUBLIC_ASSET_MANIFEST.csv", "0_admin/PUBLIC_REPOSITORY_INDEX.csv",
             "0_admin/REPOSITORY_STRUCTURE_STATUS.json", "7_report/action_records/PUBLIC_REPOSITORY_QA_2026-10-12.json"}


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def exactly(rows: list[dict], **criteria: str) -> dict:
    matches = [row for row in rows if all(row.get(key) == value for key, value in criteria.items())]
    if len(matches) != 1:
        raise ValueError(f"Non-unique source record: {criteria}: {len(matches)}")
    return matches[0]


def derive_public_files(root: Path) -> None:
    copies = []
    for number in range(1, 11):
        name = f"Supplementary_Figure_S{number}_source_data.csv"
        original = root / SOURCE / name
        target = root / "4_figures/Supplementary/source_data" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        copies.append({"path": target.relative_to(root).as_posix(), "source_path": original.relative_to(root).as_posix(),
                       "bytes": target.stat().st_size, "sha256": sha256(original)})
    write_csv(root / "4_figures/Supplementary/SUPPLEMENTARY_SOURCE_COPY_MANIFEST.csv", copies,
              ["path", "source_path", "bytes", "sha256"])
    local = root / "9_version/scientific_content_reaudit_2026-10-12/FULL_LOCAL_AUDIT_STATUS_2026-10-12.json"
    summary = json.loads(local.read_text(encoding="utf-8-sig"))
    summary["public_git_file_count"] = False
    summary["full_path_inventory_published"] = False
    summary["scientific_truth_certified"] = False
    (root / REPORT / "LOCAL_FILE_AUDIT_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    rows = []

    def add(owner: str, source: str, selector: dict, estimate: str, unit: str,
            interpretation: str, ci: tuple[str, str] = ("ci_low", "ci_high"),
            p: str = "p_value", q: str = "q_value_primary4") -> None:
        record = exactly(csv_rows(root / source), **selector)
        rows.append({"owner": owner, "source_path": source, "source_selector": json.dumps(selector, sort_keys=True),
                     "estimate": record[estimate], "ci_low": record.get(ci[0], ""), "ci_high": record.get(ci[1], ""),
                     "p_value": record.get(p, ""), "q_value": record.get(q, ""), "unit": unit, "interpretation": interpretation})

    f1 = "4_figures/Fig1/source_data/Figure_1_source_data.csv"
    add("Figure 1d", f1, {"panel": "d", "series": "median Jaccard", "category": "B_ASC"}, "estimate",
        "state overlap; 20 end-to-end resamples", "Below the unchanged 0.95 criterion; not disease-model replication")
    f2 = "4_figures/Fig2/source_data/Figure_2_source_data.csv"
    for analysis, note in [("C3A_PRIMARY_C4_MANAGED_VS_NORMAL", "Primary composition lacks enrichment support, not equivalence"),
                           ("C3A_SECONDARY_C3_FLARE_VS_NORMAL", "Secondary nominal signal fails three-contrast BH")]:
        add("Figure 2b", f2, {"panel": "b", "analysis_id": analysis, "variant": "frozen_base50"}, "odds_ratio",
            "conditional odds ratio; sample-cohort strata", note, q="bh_q_across_three_frozen_contrasts")
    f3 = "4_figures/Fig3/source_data/Figure_3_source_data.csv"
    for program in ("NAIVE_TO_MEMORY_AXIS", "ATYPICAL_LOW_NAIVE_AXIS", "APC_HLA", "IFN_ISG"):
        add("Figure 3a", f3, {"panel": "a", "analysis_name": "primary_base", "program_id": program}, "effect",
            "primary within-analysis standardized score; 89 pseudobulks", "Four-program confirmatory family")
    add("Figure 3d", f3, {"panel": "d", "analysis_name": "primary_base", "program_id": "PAN_B_IDENTITY_QC"}, "effect",
        "QC score difference", "Positive primary pan-B; nominal-only diagnostic, not a confirmatory program")
    f4 = "4_figures/Fig4/source_data/Figure_4_source_data.csv"
    for analysis, note in [("childhood_min50", "43 independent-accession donors; source-label-defined support"),
                           ("combined_min50", "Includes childhood donors; not an additional independent replication"),
                           ("adult_min50", "11 donors; CI spans zero; directional only")]:
        add("Figure 4a", f4, {"panel": "a", "analysis_name": analysis}, "effect",
            "within-analysis standardized program-score difference", note)
    for record in csv_rows(root / f4):
        if record["panel"] == "d":
            add("Figure 4d", f4, {"panel": "d", "metric": record["metric"]}, "observed", "reference calibration",
                f"Unchanged criterion={record['criterion']}; {record['status']}; no corrected disease effect")
    f5 = "4_figures/Fig5/source_data/Figure_5_source_data.csv"
    for record in csv_rows(root / f5):
        if record["panel"] == "D":
            add("Figure 5d", f5, {"panel": "D", "category": record["category"]}, "estimate", "signed-target ULM slope",
                "Observational depletion sensitivity; branch-specific six-test BH; not participant-level activity", q="q_value")
    stage = "3_results/current/StageK_Source_Data.csv"
    for record in csv_rows(root / stage):
        add("Supplementary Table S10", stage, {"interval_method": record["interval_method"]}, "point_estimate_T0",
            "T0 coefficient difference; same 68 donors", "SAME_DONORS_SAME_ESTIMAND; not independent replication",
            ci=("ci_95_low", "ci_95_high"), p="nominal_p_value")
    receipt = f"{REPORT}/INDEPENDENT_NUMERIC_RECOMPUTATION.json"
    rho = json.loads((root / receipt).read_text(encoding="utf-8-sig"))["rho"]
    rows.append({"owner": "Figure 4c", "source_path": receipt, "source_selector": "rho",
                 "estimate": repr(rho), "ci_low": "", "ci_high": "", "p_value": "", "q_value": "",
                 "unit": "4410 shared tested genes", "interpretation": "Weak genome-wide agreement alongside IFN-specific concordance"})
    write_csv(root / "3_results/scientific_summary/KEY_RESULTS.csv", rows, list(rows[0]))


def build_indexes(root: Path) -> dict:
    process = subprocess.run(["git", "ls-files", "-z", "--stage"], cwd=root, check=True, capture_output=True)
    objects = {}
    for item in process.stdout.decode("utf-8").split("\0"):
        if not item:
            continue
        metadata, path = item.split("\t", 1)
        mode, oid, stage = metadata.split()
        if stage != "0" or mode == "160000":
            raise ValueError(f"Unmerged path or unsupported submodule: {path}")
        objects[path] = oid
    paths = sorted(objects)
    index = []
    cache = {}
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as reader:
        for value in paths:
            if value in GENERATED:
                continue
            oid = objects[value]
            if oid not in cache:
                reader.stdin.write((oid + "\n").encode("ascii"))
                reader.stdin.flush()
                header = reader.stdout.readline().decode("ascii").split()
                if len(header) != 3 or header[1] != "blob":
                    raise ValueError(f"Cannot read staged Git blob: {value}")
                size = int(header[2])
                payload = reader.stdout.read(size)
                if len(payload) != size or reader.stdout.read(1) != b"\n":
                    raise ValueError(f"Truncated staged Git blob: {value}")
                cache[oid] = (size, hashlib.sha256(payload).hexdigest())
            size, digest = cache[oid]
            index.append({"path": value, "bytes": size, "sha256": digest, "git_blob": oid,
                          "folder": value.split("/")[0] if "/" in value else "root"})
        reader.stdin.close()
    write_csv(root / "0_admin/PUBLIC_REPOSITORY_INDEX.csv", index, ["path", "bytes", "sha256", "git_blob", "folder"])
    selected = set(NAVIGATION) | {"CITATION.cff", "0_admin/CITATION.cff", "2_code/audit_quality_control/verify_repository.py",
                                "2_code/audit_quality_control/build_public_navigation.py", "2_code/audit_quality_control/verify_git_inventory.py",
                                "2_code/tests/test_public_repository.py",
                                ".github/workflows/static-checks.yml", "3_results/scientific_summary/KEY_RESULTS.csv",
                                "4_figures/Supplementary/SUPPLEMENTARY_SOURCE_COPY_MANIFEST.csv"}
    selected.update(row["path"] for row in json.loads((root / REPORT / "PROTECTED_ASSET_INVENTORY.json").read_text(encoding="utf-8-sig")))
    selected.update(row["path"] for row in csv_rows(root / REPORT / "CANDIDATE_DELIVERABLE_MANIFEST.csv"))
    for row in index:
        value = row["path"]
        if value.startswith((REPORT + "/", "3_results/current/", "1_data/manifests/", "4_figures/Supplementary/source_data/")):
            selected.add(value)
    indexed = {row["path"]: row for row in index}
    if selected - indexed.keys():
        raise ValueError(f"Public assets not staged/tracked: {sorted(selected - indexed.keys())}")
    for value in selected:
        if sha256(root / value) != indexed[value]["sha256"]:
            raise ValueError(f"Working/staged bytes differ; check newline policy and stage again: {value}")
    manifest = [{"path": p, "bytes": indexed[p]["bytes"], "sha256": indexed[p]["sha256"],
                 "role": "review_candidate" if "candidate_" in p else "current_evidence_or_navigation"} for p in sorted(selected)]
    write_csv(root / "0_admin/PUBLIC_ASSET_MANIFEST.csv", manifest, ["path", "bytes", "sha256", "role"])
    status = {"schema": "PUBLIC_REPOSITORY_STRUCTURE_1", "date": "2026-10-12", "tracked_paths_seen": len(paths),
              "indexed_payloads": len(index), "indexed_bytes": sum(int(row["bytes"]) for row in index),
              "curated_manifest_assets": len(manifest), "primary_folders": list(FOLDERS),
              "index_self_exclusions": sorted(GENERATED), "candidate_adopted": False,
              "submission_package_refreshed": False, "frozen_backend_relocated": False}
    (root / "0_admin/REPOSITORY_STRUCTURE_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--refresh-index", action="store_true")
    args = parser.parse_args()
    if args.refresh_index:
        print(json.dumps(build_indexes(args.root.resolve()), indent=2))
    else:
        derive_public_files(args.root.resolve())
        print("PASS: ten source copies, compact local summary and source-bound key results built; stage them before --refresh-index")


if __name__ == "__main__":
    main()
