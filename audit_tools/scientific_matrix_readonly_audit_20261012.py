"""Read-only CSR/count and observation integrity checks; no model fitting."""
from pathlib import Path
import hashlib
import json
import tarfile

import h5py
import numpy as np


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def vector(group, key):
    obj = group[key]
    if isinstance(obj, h5py.Group):
        categories = obj["categories"].asstr()[:]
        codes = obj["codes"][:]
        if np.any(codes < 0):
            raise ValueError("Missing observation identifier")
        return categories[codes]
    return obj.asstr()[:] if obj.dtype.kind in "OSU" else obj[:]


def main():
    root = Path.cwd()
    raw = root / "phase17_v7/gateC2B1/20260810_171000_full_library_doublets/04_full_raw_counts.h5ad"
    representation = root / "phase17_v7/gateC2B2/20260812_full_representation/06_primary_all_cells_representation.h5ad"
    checks = []
    def check(name, passed, detail):
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
    with h5py.File(raw, "r") as f, h5py.File(representation, "r") as g:
        x = f["X"]
        shape = tuple(int(i) for i in x.attrs["shape"])
        check("Raw count shape", shape == (150402, 30172), list(shape))
        pointer = x["indptr"][:]
        nnz = len(x["data"])
        check("CSR pointer integrity", len(pointer) == shape[0] + 1 and pointer[0] == 0 and pointer[-1] == nnz and np.all(np.diff(pointer) >= 0), {"nnz": nnz, "pointer_rows": len(pointer)})
        check("CSR index/data length", len(x["indices"]) == nnz, nnz)
        finite = integer = nonnegative = valid_indices = True
        total = 0
        for start in range(0, nnz, 2_000_000):
            values = x["data"][start:start + 2_000_000]
            indices = x["indices"][start:start + 2_000_000]
            finite &= bool(np.all(np.isfinite(values)))
            integer &= bool(np.all(values == np.floor(values)))
            nonnegative &= bool(np.all(values >= 0))
            valid_indices &= bool(np.all((indices >= 0) & (indices < shape[1])))
            total += int(np.sum(values, dtype=np.int64))
        check("All CSR values finite", finite, nnz)
        check("All raw values nonnegative integer", integer and nonnegative, {"total_counts": total})
        check("All gene indices in bounds", valid_indices, shape[1])
        ids = vector(f["obs"], "cell_id")
        check("Unique cell IDs", len(set(ids)) == shape[0], len(ids))
        check("Representation cell ordering", np.array_equal(ids, vector(g["obs"], "cell_id")), "embedding and raw counts retain the same cell order")
        for key, expected in [("donor_id", 259), ("sample_uuid", 271), ("library_uuid", 88)]:
            count = len(set(vector(f["obs"], key)))
            check(key + " unique support", count == expected, count)
        check("Representation is embedding-only", "X" not in g and len(g["layers"]) == 0, "not a substitute for the separately retained raw count matrix")
        for key in ["X_pca", "X_pca_harmony", "X_umap_harmony", "X_umap_unintegrated"]:
            values = g["obsm"][key][:]
            check(key + " dimensions and finiteness", values.shape[0] == shape[0] and np.all(np.isfinite(values)), list(values.shape))
    archive = root / "Data/processed/GSE135779_nehar_validation/source/GSE135779_RAW.tar"
    with tarfile.open(archive, "r:") as stream:
        members = stream.getmembers()
        regular = [m for m in members if m.isfile()]
        names = [m.name for m in members]
        safe = all(not Path(n).is_absolute() and ".." not in Path(n).parts for n in names)
        check("External source TAR member structure", safe and len(names) == len(set(names)), {"regular_members": len(regular), "compressed_matrix_members": sum(m.name.endswith(".mtx.gz") for m in regular)})
    files = [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in [raw, representation, archive]]
    result = {"read_only": True, "models_refitted": False, "checks": checks, "pass_count": sum(c["pass"] for c in checks), "fail_count": sum(not c["pass"] for c in checks), "files": files, "limits": "Does not revalidate all biological annotations, refit disease models, or decompress and re-estimate every external matrix."}
    target = root / "7_report/scientific_narrative_reaudit_2026-10-12/RAW_MATRIX_READONLY_AUDIT.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["fail_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
