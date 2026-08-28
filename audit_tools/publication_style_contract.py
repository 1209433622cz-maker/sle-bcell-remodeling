"""Shared final-size typography for source-driven scientific figure redraws."""

import re
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text
import numpy as np


def apply_publication_style(figure, width_mm=170.0):
    width, height = figure.get_size_inches()
    figure.set_size_inches(width_mm / 25.4, height * width_mm / (25.4 * width), forward=True)
    figure.canvas.draw()
    for item in figure.findobj(Text):
        if not item.get_visible() or not item.get_text().strip():
            continue
        panel = re.fullmatch(r"[a-z]", item.get_text().strip()) and item.get_fontweight() in ("bold", 700)
        item.set_fontsize(8 if panel else min(7, max(5, item.get_fontsize())))
        item.set_fontfamily("Arial")
    for item in figure.findobj():
        if isinstance(item, (Line2D, Patch)) and item.get_linewidth() > 0:
            item.set_linewidth(min(1.0, max(0.25, item.get_linewidth())))
        if isinstance(item, Line2D) and item.get_markeredgewidth() > 0:
            item.set_markeredgewidth(min(1.0, max(0.25, item.get_markeredgewidth())))
        if isinstance(item, LineCollection):
            widths = np.asarray(item.get_linewidths())
            item.set_linewidths(np.where(widths > 0, np.clip(widths, 0.25, 1.0), widths))
    figure.canvas.draw()
