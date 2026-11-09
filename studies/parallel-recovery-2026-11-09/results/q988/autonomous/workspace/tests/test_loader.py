import json
import tempfile
import unittest
from pathlib import Path

from source.loader import SnapshotLoader


class SnapshotLoaderTests(unittest.TestCase):
    def test_same_capture_time_does_not_alias_distinct_services(self):
        captured_at = "2026-11-09T09:30:00Z"
        snapshots = {
            "api": {
                "service": "api",
                "captured_at": captured_at,
                "deployments": [{
                    "id": "api-13",
                    "state": "Running",
                    "finished_at": "2026-11-09T09:20:00Z",
                }],
            },
            "worker": {
                "service": "worker",
                "captured_at": captured_at,
                "deployments": [{
                    "id": "worker-8",
                    "state": "Succeeded",
                    "finished_at": "2026-11-09T09:20:00Z",
                }],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            paths = {}
            for service, payload in snapshots.items():
                path = Path(directory) / f"{service}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths[service] = path

            loader = SnapshotLoader()
            api = loader.load(paths["api"])
            worker = loader.load(paths["worker"])

        self.assertEqual(api["service"], "api")
        self.assertEqual(worker["service"], "worker")
        self.assertEqual(api["deployments"][0]["id"], "api-13")
        self.assertEqual(worker["deployments"][0]["id"], "worker-8")


if __name__ == "__main__":
    unittest.main()
