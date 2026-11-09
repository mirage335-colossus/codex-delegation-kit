import unittest
from duration import display


class DurationTest(unittest.TestCase):
    def test_other_durations(self):
        self.assertEqual(display(0), "0 seconds")
        self.assertEqual(display(2), "2 seconds")

