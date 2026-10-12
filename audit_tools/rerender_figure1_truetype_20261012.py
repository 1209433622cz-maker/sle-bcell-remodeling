"""Re-export the unchanged Figure 1 source with editable TrueType PDF fonts."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

import phase17_npj_sba_50_integrate_figure1_boundary_promotion as builder


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "4_figures/Fig1/candidate_2026-10-12_truetype"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state_summary(source, panel):
    rows = []
    for state in ["B_ASC", "B_CONV"]:
        selected = source.loc[source["panel"].eq(panel) & source["category"].eq(state)]
        minimum = selected.loc[selected["series"].eq("minimum Jaccard"), "estimate"].item()
        median = selected.loc[selected["series"].eq("median Jaccard"), "estimate"].item()
        rows.append(dict(state=state, minimum=minimum, median=median))
    return pd.DataFrame(rows)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_path = ROOT / "4_figures/Fig1/source_data/Figure_1_source_data.csv"
    source = pd.read_csv(source_path)
    frozen, rebuilt = state_summary(source, "c"), state_summary(source, "d")
    plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})
    figure, axes = plt.subplots(2, 2, figsize=(7.09, 5.45), constrained_layout=True)
    builder.draw_panel_a(axes[0, 0])
    builder.draw_panel_b(axes[0, 1], source)
    axes[0, 1].legend(frameon=False, fontsize=6, loc="upper left")
    builder.draw_jaccard_panel(axes[1, 0], frozen, panel="c", title="Fixed representation: overlap criterion met", marker_note=True)
    builder.draw_jaccard_panel(axes[1, 1], rebuilt, panel="d", title="End-to-end reconstruction: B_ASC criterion not met", marker_note=False)
    for axis in axes[1]:
        axis.set_xticks([0.875, 0.900, 0.925, 0.950, 0.975, 1.000])
    builder.artwork.ASSERTIONS.clear()
    builder.artwork.set_output_width_mm(170.0)
    builder.artwork.save_figure(figure, OUTPUT, "Figure_1")
    shutil.copy2(source_path, OUTPUT / "Figure_1_source_data.csv")
    a = np.array(Image.open(ROOT / "4_figures/Fig1/canonical/Figure_1.png").convert("RGB"))
    b = np.array(Image.open(OUTPUT / "Figure_1.png").convert("RGB"))
    proof = dict(source_sha256=sha(source_path), source_copy_sha256=sha(OUTPUT / "Figure_1_source_data.csv"), builder_sha256=sha(Path(builder.__file__)), shared_artwork_sha256=sha(Path(builder.artwork.__file__)), python_executable=__import__("sys").executable, matplotlib=__import__("matplotlib").__version__, canonical_unchanged=True, explicit_changes=["pdf.fonttype=42", "b legend moved away from minimum-ARI points", "c/d fixed ticks match the parent figure"], original_pixels=list(a.shape), candidate_pixels=list(b.shape), exact_pixel_match=bool(a.shape == b.shape and np.array_equal(a, b)))
    if a.shape == b.shape:
        proof["changed_pixel_fraction"] = float(np.any(a != b, axis=2).mean())
    (OUTPUT / "SOURCE_RERENDER_RECEIPT.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
