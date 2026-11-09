import unittest
from source.normalize import normalize_state
from source.timeutil import parse_time
from source.validation import validate_snapshot
from source.select import deployment_rank

class HelperTests(unittest.TestCase):
    def test_state_alias(self):
        self.assertEqual(normalize_state("Succeeded"), "succeeded")

    def test_z_timestamp(self):
        self.assertEqual(parse_time("2026-11-09T09:30:00Z").isoformat(), "2026-11-09T09:30:00+00:00")

    def test_snapshot_validation_rejects_duplicate_ids(self):
        payload = {"service": "api", "captured_at": "2026-11-09T09:30:00Z", "deployments": [
            {"id": "d1", "state": "running", "finished_at": "2026-11-09T09:20:00Z"},
            {"id": "d1", "state": "failed", "finished_at": "2026-11-09T09:21:00Z"}]}
        with self.assertRaisesRegex(ValueError, "duplicate deployment id"):
            validate_snapshot(payload)

    def test_rank_uses_id_after_timestamp(self):
        a = {"id": "job-a", "finished_at": "2026-11-09T09:20:00Z"}
        b = {"id": "job-b", "finished_at": "2026-11-09T09:20:00Z"}
        self.assertGreater(deployment_rank(b), deployment_rank(a))

if __name__ == "__main__":
    unittest.main()
