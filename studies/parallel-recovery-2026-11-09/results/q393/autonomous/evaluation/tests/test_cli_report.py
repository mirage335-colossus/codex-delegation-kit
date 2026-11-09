import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from source.cli import main


class CliReportTests(unittest.TestCase):
    def test_cli_emits_filtered_team_report_and_warns_for_bad_rows(self):
        contents = (
            "date,team,status,amount\n"
            "2026-10-01,Blue,approved,$10.25\n"
            "2026-10-02,Red,approved,2.00\n"
            "2026-10-03,Blue,rejected,900.00\n"
            "2026-09-30,Red,approved,70.00\n"
            "2026-10-04,Blue,approved,0.75\n"
            "not-a-date,Other,approved,4.00\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "expenses.csv"
            csv_path.write_text(contents, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(main(["--input", str(csv_path), "--month", "2026-10"]), 0)

        self.assertEqual(json.loads(stdout.getvalue()), {
            "month": "2026-10",
            "grand_total": "13.00",
            "teams": {
                "Blue": {"count": 2, "total": "11.00"},
                "Red": {"count": 1, "total": "2.00"},
            },
        })
        self.assertTrue(stderr.getvalue().startswith("line 7:"))
        self.assertEqual(stdout.getvalue().count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
