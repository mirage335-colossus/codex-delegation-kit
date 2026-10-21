"""Deterministic policy checks. These do not establish live model behavior."""

import math
import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scheduling import estimated_cost, next_quantum, rank, should_preempt


def task(name, estimate=10, **fields):
    return dict(id=name, estimate_seconds=estimate, priority=0, origin="original",
                ready_at=0, created_at=0, resources={"processes": 1}, **fields)


class SchedulingTests(unittest.TestCase):
    def test_fast_first_respects_priority_setup_and_dependencies(self):
        cases = [task("slow", 80), task("quick", 2), task("setup", 1, setup_seconds=20),
                 task("unlock", 5, unlock_value=20)]
        self.assertEqual([item["id"] for item in rank(cases, 0, {})], ["unlock", "quick", "setup", "slow"])
        cases[0]["priority"] = 1
        self.assertEqual(rank(cases, 0, {})[0]["id"], "slow")
        self.assertNotIn("score", cases[0])

    def test_unknown_gets_discovery_opportunity_then_larger_service(self):
        unknown = task("unknown", None, quantum_seconds=4, initial_quantum_seconds=4)
        self.assertEqual(rank([task("expensive", 40), unknown], 0, {})[0]["id"], "unknown")
        unknown.update(preemptions=1, service_seconds=5)
        self.assertEqual(next_quantum(unknown, {}), 8)
        self.assertGreaterEqual(estimated_cost(unknown, {})[1], 10)
        unknown.update(preemptions=2, quantum_seconds=8)
        self.assertEqual(next_quantum(unknown, {}), 16)

    def test_censored_observation_is_not_completed_duration_or_subtraction(self):
        slow = task("stale", 2, service_seconds=9, quantum_seconds=3)
        _, expected, provenance = estimated_cost(slow, {})
        self.assertGreaterEqual(expected, 18)
        self.assertIn("censored", provenance)
        self.assertIn("provenance=", rank([slow], 10, {})[0]["selection_reason"])

    def test_aged_original_survives_continuing_auxiliary_arrivals(self):
        original = task("original", 1000)
        followup = task("aux", .01)
        followup.update(origin="followup", ready_at=301)
        self.assertEqual(rank([followup, original], 301, {"aging_seconds": 300})[0]["id"], "original")
        self.assertEqual(rank([followup, original], 1, {"aging_seconds": 300})[0]["id"], "aux")

    def test_worthwhile_preemption_and_justified_nonpreemption(self):
        running = task("slow", 100, started_at=0, quantum_seconds=5, preemption="restart", restart_seconds=2)
        quick = task("quick", 1)
        self.assertTrue(should_preempt(running, quick, 6, {}))
        self.assertFalse(should_preempt(running, quick, 2, {}))
        for values in ({"preemption": "never"}, {"preemptions": 2}, {"timing_required": True},
                       {"hold": "permission"}, {"remaining_seconds": 2, "remaining_observed_at": 5}):
            with self.subTest(values=values):
                self.assertFalse(should_preempt(dict(running, **values), quick, 6, {}))
        self.assertFalse(should_preempt(running, task("near", 90), 6, {}))

    def test_preemption_needs_resource_release_and_comparable_priority(self):
        active = task("active", 100, started_at=0, quantum_seconds=5, preemption="restart")
        candidate = task("candidate", 1)
        candidate["resources"] = {"reasoning": 1}
        self.assertFalse(should_preempt(active, candidate, 6, {}))
        candidate["resources"] = {"processes": 2}
        self.assertFalse(should_preempt(active, candidate, 6, {}))
        self.assertTrue(should_preempt(active, candidate, 6, {"available": {"processes": 1}}))
        candidate["resources"] = {"processes": 1}
        candidate["priority"] = -1
        self.assertFalse(should_preempt(active, candidate, 6, {}))

    def test_bad_numeric_observations_are_rejected(self):
        for bad in [math.nan, math.inf, True, "2"]:
            with self.subTest(value=bad), self.assertRaises(ValueError):
                rank([task("invalid", bad)], 0, {})

    def test_matched_benchmark_targets_and_disclosed_regression(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "benchmark.py"
        spec = importlib.util.spec_from_file_location("scheduling_benchmark", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.benchmark()
        self.assertTrue(report["passed"])
        self.assertEqual(report["kind"], "deterministic_simulation")
        for name, fixture in module.fixtures().items():
            for mode, result in report["results"][name].items():
                with self.subTest(fixture=name, mode=mode):
                    outcomes = [event["task"] for event in result["events"] if event["event"] == "useful_result"]
                    self.assertEqual(sorted(outcomes), sorted(task["id"] for task in fixture["tasks"]))
                    self.assertGreaterEqual(result["idle_slot_seconds"], 0)
                    self.assertAlmostEqual(result["dispatch_overhead_seconds"], result["dispatches"] * module.DISPATCH_SECONDS)
        poor = report["results"]["poor_estimates_and_unknown"]
        self.assertLess(poor["adaptive"]["early_useful_results"], poor["fifo"]["early_useful_results"])
        arrivals = report["results"]["continuing_auxiliary_arrivals"]["adaptive"]["events"]
        original = next(event for event in arrivals if event["task"] == "original-expensive" and event["event"] == "dispatch")
        self.assertLess(original["time"], 32)


if __name__ == "__main__":
    unittest.main()
