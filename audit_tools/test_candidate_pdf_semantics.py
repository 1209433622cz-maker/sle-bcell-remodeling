"""WPS extraction must exclude marginal line numbers, never scientific values."""

import unittest

from phase17_postc9_11_audit_candidate_semantics import is_margin_line_number


class MarginNumberTests(unittest.TestCase):
    def test_only_marginal_integer_is_a_line_number(self):
        self.assertTrue(is_margin_line_number("379", 38.28))
        for text, x in (("379",72), ("379",0), ("0.990",38.28), ("against379",38.28), ("43",108)):
            self.assertFalse(is_margin_line_number(text,x))


if __name__ == "__main__":
    unittest.main()
