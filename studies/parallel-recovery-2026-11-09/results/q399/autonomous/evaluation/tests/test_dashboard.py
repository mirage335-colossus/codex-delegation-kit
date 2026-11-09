import json
import tempfile
import unittest
from pathlib import Path

from source.loader import SnapshotLoader
from source.select import build_dashboard


class DashboardTests(unittest.TestCase):
    def test_same_capture_time_keeps_service_snapshots_separate(self):
        payloads = {
            "api.json": {
                "service": "api",
                "captured_at": "2026-11-09T09:30:00Z",
                "deployments": [{"id": "api-1", "state": "running", "finished_at": "2026-11-09T09:20:00Z"}],
            },
            "worker.json": {
                "service": "worker",
                "captured_at": "2026-11-09T09:30:00Z",
                "deployments": [{"id": "worker-1", "state": "failed", "finished_at": "2026-11-09T09:21:00Z"}],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for filename, payload in payloads.items():
                path = Path(directory, filename)
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)

            loader = SnapshotLoader()
            dashboard = build_dashboard([loader.load(path) for path in paths])

        self.assertEqual(set(dashboard["services"]), {"api", "worker"})
        self.assertEqual(dashboard["services"]["api"]["id"], "api-1")
        self.assertEqual(dashboard["services"]["worker"]["id"], "worker-1")


if __name__ == "__main__":
    unittest.main()
