"""Recount frozen C9 calibration from OOF records without importing its mapper code."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest().upper()


def run(source, output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(source / "17_FILE_INTEGRITY_MANIFEST.csv")
    for row in manifest.itertuples():
        path = source / row.filename
        if path.parent.resolve() != source.resolve():
            raise ValueError("Out-of-scope frozen path")
        assert path.stat().st_size == row.size_bytes and digest(path) == row.sha256, row.filename
    oof = pd.read_csv(source / "08_REFERENCE_OOF_PREDICTIONS.csv")
    frozen = pd.read_csv(source / "07_MAPPER_CONFIDENCE_CALIBRATION.csv")
    summary = pd.read_csv(source / "11_SAMPLE_PREFREEZE_SUMMARY.csv")
    decision = json.loads((source / "15_GATE_C9A_PREFREEZE_DECISION.json").read_text())
    assert not oof.reference_row.duplicated().any()
    assert (oof.groupby("donor_id").fold.nunique() == 1).all()
    assert set(oof.fold) == set(range(5)) and len(oof) == 14300
    truth = oof.truth.to_numpy()
    rows = []
    for row in frozen.itertuples():
        elastic = row.mapper == "elastic_net"
        column = "elastic_confidence" if elastic else "centroid_margin"
        # CSV round-trips float32 centroid margins; compare in the original dtype.
        score = oof[column].to_numpy(dtype=np.float64 if elastic else np.float32)
        prediction = oof["elastic_prediction" if elastic else "centroid_prediction"].to_numpy()
        retained = score >= row.threshold
        values = {"coverage":float(retained.mean()), "accuracy":float((truth[retained] == prediction[retained]).mean())}
        for state in ("B_CONV", "B_ASC"):
            selected = retained & (prediction == state)
            values[f"{state}_precision"] = float((truth[selected] == state).mean()) if selected.any() else 0.0
        eligible = values["coverage"] >= .80 and min(values["B_CONV_precision"], values["B_ASC_precision"]) >= .90
        assert eligible == row.eligible
        for key, value in values.items():
            assert np.isclose(value, getattr(row, key), rtol=0, atol=1e-12), (row.mapper, row.threshold, key)
        rows.append({"mapper":row.mapper,"threshold":row.threshold,**values,"eligible":eligible,
                     "selected":row.selected,"recomputed_matches_frozen":True})
    recomputed = pd.DataFrame(rows)
    recomputed.to_csv(output / "calibration_recount.csv", index=False, lineterminator="\n")
    selected = recomputed.loc[recomputed.selected].set_index("mapper")
    assert len(selected) == 2 and not selected.loc["elastic_net", "eligible"]
    assert selected.loc["nearest_centroid", "eligible"]
    assert summary.sample_id.nunique() == len(summary) == 56
    for column, expected in (("matrix_cells", 363083), ("qc_pass_cells", 353527), ("cluster_selected_B_cells", 36630)):
        assert summary[column].sum() == expected
    assert decision["decision"] == "HOLD_C9A_PREFREEZE_REVIEW_REQUIRED"
    assert decision["outcome_unlock_authorized"] is False
    assert decision["test_mode"] is False
    record = {"created_at":datetime.now().astimezone().isoformat(timespec="seconds"),
              "status":"PASS_INDEPENDENT_IMPLEMENTATION_RECOUNT", "calibration_rows":len(rows),
              "reference_cells":len(oof),"donors":oof.donor_id.nunique(),"folds":5,
              "donor_fold_leakage":False,"sample_matrices":56,
              "elastic_B_ASC_precision":float(selected.loc["elastic_net","B_ASC_precision"]),
              "outcome_unlock_authorized":False,
              "scope":"Independent implementation of arithmetic checks by the same auditing agent; not a separate external reviewer, model refit, or disease analysis.",
              "inputs":[{"file":row.filename,"bytes":row.size_bytes,"sha256":row.sha256} for row in manifest.itertuples()]}
    (output / "calibration_recount_audit.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({key:value for key,value in record.items() if key != "inputs"},indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.source.resolve(), args.output_dir.resolve())
