import json
from pathlib import Path
import unittest
from billing.ledger import load_ledger
from billing.summary import summarize

ROOT = Path(__file__).resolve().parents[1]


class SummaryTests(unittest.TestCase):
    def test_existing_artifact_matches_all_rows(self):
        expected = summarize(load_ledger(ROOT / "data/ledger.csv"))
        self.assertEqual(json.loads((ROOT / "deliverables/weekly_summary.json").read_text()), expected)
        self.assertEqual(expected["grand_total_cents"], 4925)

    def test_void_and_nonbillable_rules(self):
        report = summarize(load_ledger(ROOT / "data/ledger.csv"))
        self.assertEqual(report["accounts"][0], {"account": "alder", "charge_count": 2, "total_cents": 1625})
        self.assertEqual(report["accounts"][1], {"account": "birch", "charge_count": 1, "total_cents": 700})

    def test_empty_ledger(self):
        self.assertEqual(summarize([]), {"currency": "USD", "accounts": [], "grand_total_cents": 0})


if __name__ == "__main__":
    unittest.main()
