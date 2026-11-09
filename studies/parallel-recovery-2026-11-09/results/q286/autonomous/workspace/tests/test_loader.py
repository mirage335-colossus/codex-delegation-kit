import json
import tempfile
import unittest
from pathlib import Path

from source.loader import SnapshotLoader


class SnapshotLoaderTests(unittest.TestCase):
    def test_same_capture_time_keeps_service_snapshots_separate(self):
        captured_at = "2026-11-09T09:30:00Z"
        payloads = {
            "api.json": {
                "service": "api",
                "captured_at": captured_at,
                "deployments": [],
            },
            "worker.json": {
                "service": "worker",
                "captured_at": captured_at,
                "deployments": [],
            },
        }

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            paths = []
            for name, payload in payloads.items():
                path = root / name
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)

            loader = SnapshotLoader()
            snapshots = [loader.load(path) for path in paths]

        self.assertEqual([snapshot["service"] for snapshot in snapshots], ["api", "worker"])
        self.assertIsNot(snapshots[0], snapshots[1])


if __name__ == "__main__":
    unittest.main()
