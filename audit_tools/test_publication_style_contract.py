import os
import unittest

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from publication_style_contract import apply_npj_sba_style


class PublicationStyleContractTests(unittest.TestCase):
    def test_role_hierarchy_and_line_hierarchy_are_preserved(self):
        figure, axis = plt.subplots()
        axis.set_title("Panel title", fontsize=7.5)
        axis.set_xlabel("Axis label", fontsize=6.5)
        axis.tick_params(labelsize=6.0)
        ordinary, = axis.plot([0, 1], [0, 1], linewidth=0.6, label="Series")
        emphasized, = axis.plot([0, 1], [1, 0], linewidth=1.2)
        hairline, = axis.plot([0, 1], [0.5, 0.5], linewidth=0.2)
        legend = axis.legend(fontsize=6.0)
        panel = axis.text(-0.1, 1.05, "a", transform=axis.transAxes, fontsize=7, fontweight="bold")
        annotation = axis.text(0.5, 0.5, "boundary", fontsize=5.2)
        oversized = axis.text(0.5, 0.6, "section heading", fontsize=8.2)

        apply_npj_sba_style(figure)

        self.assertEqual(axis.title.get_fontsize(), 7.5)
        self.assertEqual(axis.xaxis.label.get_fontsize(), 6.5)
        self.assertTrue(all(item.get_fontsize() == 6.0 for item in axis.get_xticklabels()))
        self.assertTrue(all(item.get_fontsize() == 6.0 for item in legend.get_texts()))
        self.assertEqual(panel.get_fontsize(), 8.0)
        self.assertEqual(annotation.get_fontsize(), 5.5)
        self.assertEqual(oversized.get_fontsize(), 8.0)
        self.assertEqual(ordinary.get_linewidth(), 0.6)
        self.assertEqual(emphasized.get_linewidth(), 1.2)
        self.assertEqual(hairline.get_linewidth(), 0.5)
        visible = [
            item
            for item in figure.findobj(matplotlib.text.Text)
            if item.get_visible() and item.get_text().strip()
        ]
        self.assertTrue(all("Arial" in item.get_fontfamily() for item in visible))
        plt.close(figure)


if __name__ == "__main__":
    unittest.main()
