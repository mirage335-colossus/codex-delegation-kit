"""Public contract checks for the documented dashboard CLI."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).parent


def invoke(directory):
    return subprocess.run(
        [sys.executable, "-B", "-m", "source.dashboard", "--input", str(directory)],
        cwd=BASE, text=True, capture_output=True, check=False,
    )


def check_primary():
    result = invoke("fixturedata/deployments.json")
    assert result.returncode == 0, f"dashboard failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload == {"services": {
        "api": {"id": "api-13", "state": "running", "finished_at": "2026-11-09T09:20:00Z"},
        "worker": {"id": "worker-8", "state": "succeeded", "finished_at": "2026-11-09T09:20:00Z"},
    }}, f"wrong documented-command output: {payload!r}"


def check_generated():
    snapshots = {
        "api.json": {"service": "api", "captured_at": "2026-11-09T09:30:00Z", "deployments": [
            {"id": "api-a", "state": "running", "finished_at": "2026-11-09T09:20:00Z"},
            {"id": "api-z", "state": "succeeded", "finished_at": "2026-11-09T09:20:00Z"},
        ]},
        "worker.json": {"service": "worker", "captured_at": "2026-11-09T09:30:00Z", "deployments": [
            {"id": "worker-q", "state": "failed", "finished_at": "2026-11-09T09:19:00Z"},
        ]},
        "ui.json": {"service": "ui", "captured_at": "2026-11-09T09:31:00Z", "deployments": [
            {"id": "ui-4", "state": "running", "finished_at": "2026-11-09T09:25:00Z"},
        ]},
    }
    with tempfile.TemporaryDirectory(prefix="a2-input-") as temp:
        directory = Path(temp)
        for filename, snapshot in snapshots.items():
            (directory / filename).write_text(json.dumps(snapshot), encoding="utf-8")
        result = invoke(directory)
    assert result.returncode == 0, f"generated-input dashboard failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload == {"services": {
        "api": {"id": "api-z", "state": "succeeded", "finished_at": "2026-11-09T09:20:00Z"},
        "ui": {"id": "ui-4", "state": "running", "finished_at": "2026-11-09T09:25:00Z"},
        "worker": {"id": "worker-q", "state": "failed", "finished_at": "2026-11-09T09:19:00Z"},
    }}, f"generated same/different capture-time output was wrong: {payload!r}"


def run():
    failures = []
    for name, check in (("fixture", check_primary), ("generated input", check_generated)):
        try:
            check()
        except Exception as error:
            failures.append(f"{name}: {error}")
    assert not failures, "\n".join(failures)
    print("A2 acceptance: PASS (fixture and generated input)")

if __name__ == "__main__":
    run()
