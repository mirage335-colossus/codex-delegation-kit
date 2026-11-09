import json
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path


class CliReportTests(unittest.TestCase):
    def test_documented_command_emits_approved_team_report(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-B", "-m", "source.cli", "--input",
             "fixturedata/expenses.csv", "--month", "2026-10"],
            cwd=root, capture_output=True, text=True, check=True,
        )
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout), {
            "month": "2026-10",
            "grand_total": "1281.00",
            "teams": {
                "North": {"count": 2, "total": "1241.00"},
                "South": {"count": 1, "total": "40.00"},
            },
        })

    def test_malformed_row_is_warned_and_skipped(self):
        with TemporaryDirectory() as directory:
            root = Path(__file__).resolve().parents[1]
            csv_path = Path(directory) / "expenses.csv"
            csv_path.write_text(
                "date,team,status,amount\n"
                "2026-10-02,East,approved,1.25\n"
                "2026-10-03,West,approved,not-money\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-B", "-m", "source.cli", "--input",
                 str(csv_path), "--month", "2026-10"],
                cwd=root, capture_output=True, text=True, check=True,
            )
        self.assertIn("line 3: invalid amount", result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "month": "2026-10",
            "grand_total": "1.25",
            "teams": {"East": {"count": 1, "total": "1.25"}},
        })


if __name__ == "__main__":
    unittest.main()
