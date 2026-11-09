"""Deterministic public acceptance checks for the documented command."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent


def run():
    result = subprocess.run(
        [sys.executable, "-B", "-m", "source.cli", "--input", "fixturedata/expenses.csv", "--month", "2026-10"],
        cwd=BASE, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    report = json.loads(result.stdout)
    assert report == {
        "month": "2026-10",
        "grand_total": "1281.00",
        "teams": {
            "North": {"count": 2, "total": "1241.00"},
            "South": {"count": 1, "total": "40.00"},
        },
    }, f"wrong documented-command output: {report!r}"
    # Guard: rejected and out-of-month rows must not contribute.
    assert report["grand_total"] != "2188.00"
    print("A1 acceptance: PASS")

if __name__ == "__main__":
    run()
