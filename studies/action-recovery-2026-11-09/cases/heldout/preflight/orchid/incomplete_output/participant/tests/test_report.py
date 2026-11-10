from pathlib import Path
import tempfile
import unittest
from telemetry.feed import Meter, RowBudgetExceeded, leased_rows
from telemetry.reduce import summarize

ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def test_supplied_report(self):
        report = summarize(ROOT / "data/readings.csv", 4)
        self.assertEqual(report["audit"], {"rows_seen": 24, "max_live_rows": 4, "peak_live_rows": 1})
        self.assertEqual(report["sites"], [
            {"site": "east", "samples": 7, "sum_mv": 717, "min_mv": 99, "max_mv": 106},
            {"site": "north", "samples": 7, "sum_mv": 0, "min_mv": -5, "max_mv": 4},
            {"site": "west", "samples": 7, "sum_mv": 1480, "min_mv": 208, "max_mv": 215},
        ])

    def test_limit_is_enforced(self):
        meter = Meter(4)
        iterator = leased_rows(ROOT / "data/readings.csv", meter)
        held = [next(iterator) for _ in range(4)]
        with self.assertRaises(RowBudgetExceeded):
            next(iterator)
        for lease in held:
            lease.release()
        self.assertEqual(meter.live, 0)

    def test_invalid_rows_are_released_and_empty_is_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "readings.csv"
            path.write_text("sequence,site,millivolts,valid\n1,x,7,0\n2,x,9,1\n")
            self.assertEqual(summarize(path, 1)["sites"], [{"site": "x", "samples": 1, "sum_mv": 9, "min_mv": 9, "max_mv": 9}])
            path.write_text("sequence,site,millivolts,valid\n")
            self.assertEqual(summarize(path, 1), {"sites": [], "audit": {"rows_seen": 0, "max_live_rows": 1, "peak_live_rows": 0}})


if __name__ == "__main__":
    unittest.main()
