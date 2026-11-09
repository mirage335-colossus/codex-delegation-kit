import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from source.cli import main


class CLITests(unittest.TestCase):
    def test_monthly_team_report_filters_rows_and_warns_on_malformed(self):
        contents = (
            "date,team,status,amount\n"
            "2026-10-01,East,approved,1.20\n"
            "2026-10-02,West,approved,3.00\n"
            "2026-10-03,East,approved,0.80\n"
            "2026-10-04,East,rejected,90.00\n"
            "2026-11-01,West,approved,20.00\n"
            "bad-date,West,approved,2.00\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expenses.csv"
            path.write_text(contents, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(main(["--input", str(path), "--month", "2026-10"]), 0)

        self.assertEqual(json.loads(stdout.getvalue()), {
            "month": "2026-10",
            "grand_total": "5.00",
            "teams": {
                "East": {"count": 2, "total": "2.00"},
                "West": {"count": 1, "total": "3.00"},
            },
        })
        self.assertIn("line 7:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
