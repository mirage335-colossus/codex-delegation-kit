import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TOOL = Path(__file__).with_name("aggregate_reviews.py")
SPEC = importlib.util.spec_from_file_location("aggregate_reviews", TOOL)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def review(domain):
    return {
        "domain_id": domain, "overall": "Supported",
        "rows": [{"id": f"{domain}-{number}", "disposition": "Supported",
                  "participant_evidence": ["locked:1"], "independent_checks": [],
                  "reason": "Fixture evidence", "remaining_action": None}
                 for number in (1, 2)],
        "depth_checks": [{"number": number, "disposition": "Supported boundary",
                          "evidence": ["locked:2"], "reason": "Fixture boundary"}
                         for number in range(1, 7)],
        "source_access_limits": [], "executed_checks": [],
        "unexecuted_checks": [], "resource_notes": [],
    }


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aggregate-reviews-", dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.matrix = self.root / "matrix.json"
        self.reviews = self.root / "reviews"
        self.reviews.mkdir()
        self.write(self.matrix, {"domains": [
            {"domain_id": domain, "criteria": [
                {"id": f"{domain}-1", "applicability": "essential"},
                {"id": f"{domain}-2", "applicability": "scoped_conditional"}]}
            for domain in ("A", "B")]})
        for domain in ("A", "B"):
            self.write(self.reviews / domain / "dispositions.json", review(domain))

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def run_cli(self, output=None):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--matrix", str(self.matrix),
                               "--reviews", str(self.reviews), "--output",
                               str(output or self.root / "aggregate.json")],
                              capture_output=True, text=True)

    def test_complete_preserves_author_disagreement_and_conditional_scope(self):
        data = review("A")
        data["overall"] = "Partial"
        data["rows"][1]["disposition"] = module.OUTSIDE
        self.write(self.reviews / "A/dispositions.json", data)
        before = {p: p.read_bytes() for p in self.reviews.rglob("*.json")}
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads((self.root / "aggregate.json").read_text())
        self.assertTrue(output["derived_ready"])
        self.assertEqual(output["domains"][0]["author_overall"], "Partial")
        self.assertFalse(output["domains"][0]["author_derived_readiness_agree"])
        self.assertEqual(output["domains"][0]["outside_conditional_row_ids"], ["A-2"])
        self.assertTrue(all(len(item["sha256"]) == 64 for item in output["inputs"]))
        self.assertEqual(before, {p: p.read_bytes() for p in self.reviews.rglob("*.json")})

    def test_partial_is_complete_aggregation_but_not_ready(self):
        data = review("A")
        data["rows"][0]["disposition"] = "Partial"
        data["depth_checks"][4]["disposition"] = "Unsupported"
        self.write(self.reviews / "A/dispositions.json", data)
        result = module.aggregate(self.matrix, self.reviews)
        self.assertEqual(result["validation_status"], "complete")
        self.assertFalse(result["derived_ready"])
        self.assertEqual(result["domains"][0]["unmet_row_ids"], ["A-1"])
        self.assertEqual(result["domains"][0]["unmet_depth_ids"], [5])

    def test_missing_reviewer_exits_nonzero_and_records_gap(self):
        (self.reviews / "B/dispositions.json").unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        output = json.loads((self.root / "aggregate.json").read_text())
        self.assertEqual(output["missing_domain_ids"], ["B"])
        self.assertFalse(output["derived_ready"])

    def test_duplicate_reviewer_is_invalid_even_with_complete_expected_set(self):
        self.write(self.reviews / "copied-review/dispositions.json", review("A"))
        result = module.aggregate(self.matrix, self.reviews)
        self.assertEqual(result["duplicate_domain_ids"], ["A"])
        self.assertEqual(result["validation_status"], "invalid")
        self.assertFalse(result["derived_ready"])

    def test_malformed_review_identities_and_dispositions(self):
        base = review("A")
        cases = {}
        def case(name):
            cases[name] = copy.deepcopy(base)
            return cases[name]
        case("same-count duplicate row")["rows"][1]["id"] = "A-1"
        case("same-count unknown row")["rows"][1]["id"] = "A-3"
        case("missing row")["rows"].pop()
        case("extra row")["rows"].append({**base["rows"][1], "id": "A-3"})
        case("duplicate depth")["depth_checks"][5]["number"] = 1
        case("extra depth")["depth_checks"].append({**base["depth_checks"][0], "number": 7})
        case("missing depth")["depth_checks"].pop()
        case("boolean depth")["depth_checks"][0]["number"] = True
        case("unknown domain")["domain_id"] = "UNKNOWN"
        case("essential outside")["rows"][0]["disposition"] = module.OUTSIDE
        case("depth outside")["depth_checks"][0]["disposition"] = module.OUTSIDE
        case("unknown disposition")["rows"][0]["disposition"] = "Pass"
        case("invalid overall")["overall"] = module.OUTSIDE
        case("missing evidence")["rows"][0].pop("participant_evidence")
        case("invalid rows type")["rows"] = {}
        for name, data in cases.items():
            with self.subTest(name=name):
                self.write(self.reviews / "A/dispositions.json", data)
                result = module.aggregate(self.matrix, self.reviews)
                self.assertEqual(result["validation_status"], "invalid")
                self.assertFalse(result["derived_ready"])
                self.assertTrue(result["errors"])

    def test_malformed_json_and_duplicate_json_keys_are_rejected(self):
        path = self.reviews / "A/dispositions.json"
        for raw in ('{', '{"domain_id":"B","domain_id":"A"}', '{"domain_id":NaN}'):
            with self.subTest(raw=raw):
                path.write_text(raw)
                result = module.aggregate(self.matrix, self.reviews)
                self.assertEqual(result["validation_status"], "invalid")
                self.assertTrue(result["errors"])
                self.assertEqual(len(result["inputs"][0]["sha256"]), 64)

    def test_bad_matrix_cannot_silently_remove_requirements(self):
        base = json.loads(self.matrix.read_text())
        for mutation in ("duplicate domain", "duplicate row", "unknown applicability", "empty"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(base)
                if mutation == "duplicate domain":
                    data["domains"].append(data["domains"][0])
                elif mutation == "duplicate row":
                    data["domains"][1]["criteria"][0]["id"] = "A-1"
                elif mutation == "unknown applicability":
                    data["domains"][0]["criteria"][0]["applicability"] = "optional"
                else:
                    data["domains"] = []
                self.write(self.matrix, data)
                result = module.aggregate(self.matrix, self.reviews)
                self.assertEqual(result["validation_status"], "invalid")
                self.assertFalse(result["derived_ready"])

    def test_existing_output_and_output_inside_reviews_are_refused(self):
        output = self.root / "aggregate.json"
        output.write_text("preserve me")
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(output.read_text(), "preserve me")
        nested = self.reviews / "new.json"
        self.assertEqual(self.run_cli(nested).returncode, 2)
        self.assertFalse(nested.exists())


if __name__ == "__main__":
    unittest.main()
