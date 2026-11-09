import tempfile
import unittest
from pathlib import Path

from source.loader import SnapshotLoader


class SnapshotLoaderTests(unittest.TestCase):
    def test_same_capture_time_does_not_mix_services(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            timestamp = "2026-11-09T09:30:00Z"
            api = root / "api.json"
            worker = root / "worker.json"
            api.write_text(
                '{"service":"api","captured_at":"' + timestamp +
                '","deployments":[]}', encoding="utf-8"
            )
            worker.write_text(
                '{"service":"worker","captured_at":"' + timestamp +
                '","deployments":[]}', encoding="utf-8"
            )

            loader = SnapshotLoader()
            self.assertEqual(loader.load(api)["service"], "api")
            self.assertEqual(loader.load(worker)["service"], "worker")


if __name__ == "__main__":
    unittest.main()
