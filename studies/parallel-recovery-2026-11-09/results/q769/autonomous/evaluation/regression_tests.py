import unittest
from pagination import paginate


class ExplicitZeroLimitTests(unittest.TestCase):
    def test_explicit_zero_returns_empty_page(self):
        self.assertEqual(paginate(["a", "b", "c"], limit=0), [])


if __name__ == "__main__":
    unittest.main()
