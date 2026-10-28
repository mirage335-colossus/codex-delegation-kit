import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "recompute_verification_usage.py"
DATASET = ROOT / "verification" / "telemetry" / "usage-records.jsonl"

sys.path.insert(0, str(SCRIPT.parent))
import recompute_verification_usage as usage  # noqa: E402


def record(**overrides):
    result = {
        "cohort": "earlier",
        "role": "delegated",
        "model": "gpt-6-luna",
        "participant": "worker_a",
        "attempt": "attempt-01",
        "response": "response-0001",
        "input_tokens": 10,
        "cached_input_tokens": 8,
        "output_tokens": 4,
        "reasoning_output_tokens": 2,
        "total_tokens": 14,
    }
    result.update(overrides)
    return result


class VerificationUsageTests(unittest.TestCase):
    def read_text(self, text):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "records.jsonl"
            path.write_text(text, encoding="utf-8")
            return usage.read_records(path)

    def test_bundled_data_reconciles_historical_counts_and_totals(self):
        rows = usage.read_records(DATASET)
        self.assertEqual(len(rows), 1112)
        summary = usage.summarize(rows)
        self.assertEqual(summary["by_cohort"]["earlier"]["totals"]["records"], 262)
        self.assertEqual(summary["by_cohort"]["latest"]["totals"]["records"], 850)
        self.assertEqual(
            summary["by_cohort"]["earlier"]["by_role"]["main_chat"]["totals"]["total_tokens"],
            13631431,
        )
        self.assertEqual(
            summary["by_cohort"]["latest"]["by_role"]["main_chat"]["totals"]["total_tokens"],
            25915508,
        )
        self.assertEqual(
            summary["by_cohort"]["latest"]["by_role"]["delegated"]["by_model"]["gpt-6-luna"]["records"],
            502,
        )
        self.assertEqual(
            summary["by_cohort"]["latest"]["luna_share"]["delegated"]["total_tokens"],
            31417854 / 43502302,
        )

    def test_relocated_input_reproduces_same_summary(self):
        expected = usage.summarize(usage.read_records(DATASET))
        with tempfile.TemporaryDirectory() as temp:
            relocated = Path(temp) / "moved" / "usage.jsonl"
            relocated.parent.mkdir()
            shutil.copyfile(DATASET, relocated)
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--input", str(relocated)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual(json.loads(result.stdout), expected)

    def test_duplicate_public_key_is_rejected(self):
        row = record()
        duplicate = record(role="main_chat")
        with self.assertRaisesRegex(ValueError, "duplicate public response key"):
            self.read_text(json.dumps(row) + "\n" + json.dumps(duplicate) + "\n")

    def test_duplicate_json_metric_key_is_rejected(self):
        raw = json.dumps(record())
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            self.read_text('{"input_tokens":999,' + raw[1:] + "\n")

    def test_subset_and_total_violations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "cached input"):
            self.read_text(json.dumps(record(cached_input_tokens=11)) + "\n")
        with self.assertRaisesRegex(ValueError, "reasoning output"):
            self.read_text(json.dumps(record(reasoning_output_tokens=5)) + "\n")
        with self.assertRaisesRegex(ValueError, "total must equal"):
            self.read_text(json.dumps(record(total_tokens=15)) + "\n")

    def test_missing_malformed_nonfinite_and_empty_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "field mismatch"):
            self.read_text(json.dumps({"cohort": "earlier"}) + "\n")
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self.read_text('{"cohort":\n')
        with self.assertRaisesRegex(ValueError, "non-finite"):
            self.read_text(json.dumps(record(input_tokens=float("nan"))) + "\n")
        with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
            self.read_text(json.dumps(record(input_tokens=1e999)) + "\n")
        with self.assertRaisesRegex(ValueError, "no records"):
            self.read_text("")


if __name__ == "__main__":
    unittest.main()
