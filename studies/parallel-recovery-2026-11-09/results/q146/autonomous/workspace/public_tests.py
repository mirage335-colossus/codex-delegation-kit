import unittest
from pagination import paginate

class PaginationTests(unittest.TestCase):
    def test_omitted_limit_uses_default(self):
        values = list(range(30))
        self.assertEqual(len(paginate(values)), 20)

    def test_explicit_zero_limit_returns_empty_list(self):
        self.assertEqual(paginate(list(range(30)), limit=0), [])

    def test_positive_limit_and_offset(self):
        self.assertEqual(paginate(["a", "b", "c", "d"], offset=1, limit=2), ["b", "c"])

    def test_empty_input_and_offset_past_end(self):
        self.assertEqual(paginate([]), [])
        self.assertEqual(paginate(["a", "b"], offset=5, limit=2), [])

    def test_negative_offset_is_clamped(self):
        self.assertEqual(paginate(["a", "b", "c"], offset=-4, limit=2), ["a", "b"])

if __name__ == "__main__":
    unittest.main()
