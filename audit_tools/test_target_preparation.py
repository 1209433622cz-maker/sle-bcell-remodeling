import unittest

from phase17_postc9_13_audit_target_preparation import calibration_summary, section, word_count


def rows():
    return [
        {"mapper": "elastic_net", "threshold": ".95", "coverage": ".94", "B_CONV_precision": ".99",
         "B_ASC_precision": ".885", "eligible": "False", "selected": "True", "diagnostic_fallback_only": "True"},
        {"mapper": "nearest_centroid", "threshold": ".12", "coverage": ".95", "B_CONV_precision": ".99",
         "B_ASC_precision": "1", "eligible": "True", "selected": "True", "diagnostic_fallback_only": "False"},
    ]


class TargetPreparationTests(unittest.TestCase):
    def test_section_keeps_subheadings_but_not_next_section(self):
        text = "## Abstract\n\n**Results:** B-cell response.\n\n### Detail\nMore evidence.\n\n## Methods\nIgnore."
        self.assertEqual(word_count(section(text, "Abstract")), 4)
        self.assertNotIn("Ignore", section(text, "Abstract"))

    def test_missing_section_fails(self):
        with self.assertRaises(ValueError):
            section("## Methods\nText", "Abstract")

    def test_mapper_eligibility_is_not_collapsed_into_any_pass(self):
        result = calibration_summary(rows())
        self.assertFalse(result[0]["selected_eligible"])
        self.assertTrue(result[0]["diagnostic_fallback_only"])
        self.assertTrue(result[1]["selected_eligible"])

    def test_conv_precision_is_required(self):
        data = rows()
        data[1]["B_CONV_precision"] = ".89"
        with self.assertRaises(ValueError):
            calibration_summary(data)

    def test_nonfinite_value_fails(self):
        data = rows()
        data[0]["coverage"] = "nan"
        with self.assertRaises(ValueError):
            calibration_summary(data)

    def test_duplicate_selected_candidate_fails(self):
        data = rows()
        data.append(dict(data[0]))
        with self.assertRaises(ValueError):
            calibration_summary(data)


if __name__ == "__main__":
    unittest.main()
