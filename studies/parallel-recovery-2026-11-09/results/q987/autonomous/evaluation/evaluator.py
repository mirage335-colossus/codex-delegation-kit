"""Public contract checks for the real finance CLI entrypoint."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).parent


def invoke(input_path, month):
    return subprocess.run(
        [sys.executable, "-B", "-m", "source.cli", "--input", str(input_path), "--month", month],
        cwd=BASE, text=True, capture_output=True, check=False,
    )


def check_primary():
    result = invoke("fixturedata/expenses.csv", "2026-10")
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


def check_generated():
    content = (
        "date,team,status,amount\n"
        "2026-11-01,Blue,approved,2.335\n"
        "2026-11-15,Blue,approved,1.005\n"
        "2026-11-25,Red,approved,0.10\n"
        "2026-11-02,Blue,rejected,7.00\n"
        "2026-12-01,Red,approved,900.00\n"
        "bad-date,Blue,approved,3.00\n"
    )
    with tempfile.TemporaryDirectory(prefix="a1-input-") as temp:
        path = Path(temp) / "generated.csv"
        path.write_text(content, encoding="utf-8")
        result = invoke(path, "2026-11")
    assert result.returncode == 0, f"generated-input CLI failed: {result.stderr}"
    report = json.loads(result.stdout)
    assert report == {
        "month": "2026-11",
        "grand_total": "3.45",
        "teams": {
            "Blue": {"count": 2, "total": "3.35"},
            "Red": {"count": 1, "total": "0.10"},
        },
    }, f"generated multi-month/status/cents output was wrong: {report!r}"
    assert "line 7:" in result.stderr, f"malformed row warning was not emitted: {result.stderr!r}"


def run():
    failures = []
    for name, check in (("fixture", check_primary), ("generated input", check_generated)):
        try:
            check()
        except Exception as error:
            failures.append(f"{name}: {error}")
    assert not failures, "\n".join(failures)
    print("A1 acceptance: PASS (fixture and generated input)")

if __name__ == "__main__":
    run()
