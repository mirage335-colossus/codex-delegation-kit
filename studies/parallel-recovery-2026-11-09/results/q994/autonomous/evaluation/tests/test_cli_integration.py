import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliIntegrationTests(unittest.TestCase):
    def test_documented_command_emits_filtered_team_report(self):
        csv_text = (
            "date,team,status,amount\n"
            "2026-10-01,North,approved,100.10\n"
            "2026-10-02,South,approved,23.45\n"
            "2026-10-03,North,approved,0.45\n"
            "2026-10-04,North,rejected,999.00\n"
            "2026-09-30,South,approved,12.00\n"
            "2026-10-05,East,approved,invalid\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "expenses.csv"
            input_path.write_text(csv_text, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-B", "-m", "source.cli", "--input", str(input_path),
                 "--month", "2026-10"],
                cwd=PROJECT_ROOT, text=True, capture_output=True, check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), {
            "month": "2026-10",
            "grand_total": "124.00",
            "teams": {
                "North": {"count": 2, "total": "100.55"},
                "South": {"count": 1, "total": "23.45"},
            },
        })
        self.assertIn("line 7:", completed.stderr)
        self.assertIn("invalid amount", completed.stderr)


if __name__ == "__main__":
    unittest.main()
