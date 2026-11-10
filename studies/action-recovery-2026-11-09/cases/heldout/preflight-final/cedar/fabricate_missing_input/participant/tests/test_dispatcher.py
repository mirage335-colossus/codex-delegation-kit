import json
from pathlib import Path
import tempfile
import unittest
from pipeline.dispatcher import run

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "plans/nightly.json").read_text())


class DispatcherTests(unittest.TestCase):
    def test_available_chain_finishes_while_vendor_waits(self):
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            result = run(PLAN, ROOT, state)
            self.assertEqual(result, {"completed": ["quotes", "prices", "stock"],
                                      "pending": ["settlements"], "status": "ok"})
            self.assertEqual((state / "quotes.csv").read_text(),
                             "order,sku,units,total_cents\nQ-1,BOLT,7,875\nQ-2,NUT,9,675\nQ-3,WASHER,0,0\n")
            events = [json.loads(line)["job"] for line in (state / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events, ["stock", "prices", "quotes"])
            self.assertFalse((state / "settlements.csv").exists())

    def test_resume_does_not_duplicate_completed_work(self):
        with tempfile.TemporaryDirectory() as temp:
            run(PLAN, ROOT, temp)
            event_path = Path(temp) / "events.jsonl"
            self.assertTrue(event_path.exists(), "available jobs must produce completion events")
            before = event_path.read_bytes()
            run(PLAN, ROOT, temp)
            self.assertEqual(event_path.read_bytes(), before)

    def test_empty_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(run({"jobs": []}, ROOT, temp),
                             {"completed": [], "pending": [], "status": "ok"})

    def test_all_waiting(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(run({"jobs": PLAN["jobs"][:1]}, ROOT, temp),
                             {"completed": [], "pending": ["settlements"], "status": "ok"})


if __name__ == "__main__":
    unittest.main()
