import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

METER = Path(__file__).with_name("research_meter.py")
SPEC = importlib.util.spec_from_file_location("research_meter", METER)
research_meter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(research_meter)


class ResearchMeterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write_allocations(4, {"alpha": 3, "beta": 1})

    def tearDown(self):
        self.tmp.cleanup()

    def write_allocations(self, total, runs):
        (self.root / "allocations.json").write_text(
            json.dumps({"total_cap": total, "runs": runs}), encoding="utf-8")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(METER), *map(str, args)],
                              text=True, capture_output=True)

    def reserve(self, run, request):
        return self.cli("reserve", "--root", self.root, "--run", run,
                        "--request-json", json.dumps(request))

    def parsed(self, result):
        return json.loads(result.stdout)

    def test_batch_counts_each_item_and_failed_attempt_keeps_consumed_budget(self):
        result = self.reserve("alpha", {
            "search_query": [{"q": "one"}, {"q": "two"}],
            "open": [{"ref_id": "source"}], "response_length": "short"})
        self.assertEqual(result.returncode, 0, result.stderr)
        ticket = self.parsed(result)
        self.assertTrue(ticket["admitted"])
        self.assertEqual(ticket["operations"], 3)
        self.assertEqual(ticket["remaining"], {"run": 0, "total": 1})
        finish = self.cli("finish", "--root", self.root, "--run", "alpha",
                          "--id", ticket["id"], "--status", "error",
                          "--metadata-json", '{"error":"timeout"}')
        self.assertEqual(finish.returncode, 0, finish.stderr)
        receipt = json.loads((self.root / "receipts" / f"{ticket['id']}.json").read_text())
        self.assertEqual(receipt["status"], "error")
        self.assertEqual(receipt["result"], {"error": "timeout"})
        denied = self.parsed(self.reserve("alpha", {"find": [{"pattern": "next"}]}))
        self.assertFalse(denied["admitted"])
        self.assertEqual(denied["error"].split()[0], "per-run")

    def test_global_cap_enforced_across_runs(self):
        self.write_allocations(2, {"alpha": 2, "beta": 1})
        first = self.parsed(self.reserve("alpha", {"open": [{"ref_id": "a"}, {"ref_id": "b"}]}))
        self.assertTrue(first["admitted"])
        second = self.parsed(self.reserve("beta", {"search_query": [{"q": "c"}]}))
        self.assertFalse(second["admitted"])
        self.assertIn("total cap", second["error"])
        state = json.loads((self.root / "meter.json").read_text())
        self.assertEqual(state["used"], {"alpha": 2})

    def test_invalid_requests_and_unknown_or_unsafe_runs_have_no_receipts(self):
        cases = [
            ("alpha", {"query": "not a web.run field"}),
            ("alpha", {"search_query": "not-an-array"}),
            ("../beta", {"search_query": [{"q": "x"}]}),
            ("missing", {"search_query": [{"q": "x"}]}),
        ]
        for run, request in cases:
            with self.subTest(run=run, request=request):
                result = self.reserve(run, request)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.parsed(result).get("admitted", False))
                self.assertFalse((self.root / "meter.json").exists())
                receipts = self.root / "receipts"
                self.assertFalse(receipts.exists() and list(receipts.iterdir()))

    def test_finish_rejects_wrong_run_and_duplicate_finish(self):
        ticket = self.parsed(self.reserve("alpha", {"click": [{"id": 1, "ref_id": "x"}]}))
        wrong = self.cli("finish", "--root", self.root, "--run", "beta",
                         "--id", ticket["id"], "--status", "returned")
        self.assertNotEqual(wrong.returncode, 0)
        first = self.cli("finish", "--root", self.root, "--run", "alpha",
                         "--id", ticket["id"], "--status", "returned")
        self.assertEqual(first.returncode, 0, first.stderr)
        duplicate = self.cli("finish", "--root", self.root, "--run", "alpha",
                             "--id", ticket["id"], "--status", "error")
        self.assertNotEqual(duplicate.returncode, 0)

    def test_parallel_reservations_do_not_overspend(self):
        self.write_allocations(3, {"alpha": 3})
        request = json.dumps({"search_query": [{"q": "x"}]})
        processes = [subprocess.Popen(
            [sys.executable, str(METER), "reserve", "--root", str(self.root),
             "--run", "alpha", "--request-json", request],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for _ in range(6)]
        results = [process.communicate() + (process.returncode,) for process in processes]
        admitted = [json.loads(out) for out, _, code in results if code == 0]
        denied = [json.loads(out) for out, _, code in results if code != 0]
        self.assertEqual(len(admitted), 3)
        self.assertEqual(len(denied), 3)
        state = json.loads((self.root / "meter.json").read_text())
        self.assertEqual(state["used"], {"alpha": 3})

    def test_receipt_write_failure_charges_usage_before_any_ticket_escapes(self):
        original_atomic_json = research_meter._atomic_json

        def fail_receipt_write(path, value):
            path = Path(path)
            if path.parent == self.root / "receipts":
                raise OSError("injected receipt write failure")
            original_atomic_json(path, value)

        with mock.patch.object(research_meter, "_atomic_json", side_effect=fail_receipt_write):
            with self.assertRaisesRegex(OSError, "injected receipt write failure"):
                research_meter.reserve(
                    self.root, "alpha", {"search_query": [{"q": "charged"}]})

        state = json.loads((self.root / "meter.json").read_text())
        self.assertEqual(state["used"], {"alpha": 1})
        self.assertEqual(len(state["receipts"]), 1)
        receipt_dir = self.root / "receipts"
        self.assertFalse(receipt_dir.exists() and list(receipt_dir.glob("*.json")))
        next_ticket = research_meter.reserve(
            self.root, "alpha", {"search_query": [{"q": "next"}]})
        self.assertTrue(next_ticket["admitted"])
        self.assertEqual(next_ticket["remaining"]["run"], 1)


if __name__ == "__main__":
    unittest.main()
