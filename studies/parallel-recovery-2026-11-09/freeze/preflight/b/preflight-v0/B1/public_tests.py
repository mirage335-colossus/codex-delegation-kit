import unittest
from sequence import assign_sequences


class SequenceTests(unittest.TestCase):
    def test_project_local_sequences_and_input_order(self):
        rows = [("e1", "alpha"), ("e2", "beta"), ("e3", "alpha"),
                ("e4", "beta"), ("e5", "alpha")]
        self.assertEqual(assign_sequences(rows), [
            ("e1", "alpha", 1), ("e2", "beta", 1),
            ("e3", "alpha", 2), ("e4", "beta", 2),
            ("e5", "alpha", 3),
        ])

    def test_empty_input(self):
        self.assertEqual(assign_sequences([]), [])

    def test_single_project_and_duplicate_event_ids(self):
        rows = [("same", "cedar"), ("same", "cedar"), ("last", "cedar")]
        self.assertEqual(assign_sequences(rows), [
            ("same", "cedar", 1), ("same", "cedar", 2), ("last", "cedar", 3),
        ])

    def test_project_sequences_restart_and_input_is_unchanged(self):
        rows = [("x", "one"), ("y", "two"), ("z", "one"), ("w", "two")]
        before = list(rows)
        actual = assign_sequences(rows)
        self.assertEqual([row[2] for row in actual], [1, 1, 2, 2])
        self.assertEqual(rows, before)



if __name__ == "__main__":
    unittest.main()
