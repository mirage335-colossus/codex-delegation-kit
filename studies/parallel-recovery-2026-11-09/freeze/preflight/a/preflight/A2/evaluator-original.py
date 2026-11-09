"""Deterministic acceptance and boundary checks for the dashboard."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent


def run():
    result = subprocess.run(
        [sys.executable, "-B", "-m", "source.dashboard", "--input", "fixturedata/deployments.json"],
        cwd=BASE, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, f"dashboard failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload == {"services": {
        "api": {"id": "api-13", "state": "running", "finished_at": "2026-11-09T09:20:00Z"},
        "worker": {"id": "worker-8", "state": "succeeded", "finished_at": "2026-11-09T09:20:00Z"},
    }}, f"wrong documented-command output: {payload!r}"
    # Guard: both service boundaries and same-time ID tie-break are observable.
    assert payload["services"]["api"]["id"] != payload["services"]["worker"]["id"]
    print("A2 acceptance: PASS")

if __name__ == "__main__":
    run()
