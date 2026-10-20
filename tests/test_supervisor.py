"""Deterministic ledger tests, not model-routing or model-quality smoke tests."""

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("supervisor", Path(__file__).resolve().parents[1] / "supervisor.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.store = Path(self.temporary.name) / "state"
        self.packet = {
            "baseline": "disposable fixture at baseline abc123",
            "scope": ["change fixture.py"], "contracts": ["negative inputs raise ValueError"],
            "decisions": [], "acceptance_checks": ["unit", "contract"],
            "allowed_commands": ["python3 -m unittest"],
            "budget": {"seconds": 60, "max_worker_results": 2},
            "stop_conditions": ["contract ambiguity: hand back immediately"],
        }

    def open(self, assignment="case", packet=None, now=100):
        return ledger.open_assignment(self.store, assignment, json.dumps(packet or self.packet), now=now)

    def result(self, *, failed=(), unexecuted=(), status="completed", new_evidence=None, verdict=None):
        result = {
            "status": status, "changed_paths": ["fixture.py"],
            "checks": {"passed": [check for check in ["unit", "contract"]
                                  if check not in failed and check not in unexecuted],
                       "failed": list(failed), "unexecuted": list(unexecuted)},
            "evidence": ["logs/unit.txt"],
        }
        if new_evidence is not None:
            result["new_evidence"] = new_evidence
        if verdict is not None:
            result["verdict"] = verdict
        return json.dumps(result, indent=3) + "\n"

    def record(self, raw=None, *, kind="worker", actor="luna-1", now=101):
        return ledger.record_result(self.store, "case", kind, actor, raw or self.result(), now=now)

    def validation(self, outcome="blocked", *, now=102, **fields):
        result = {"outcome": outcome, "command": "python3 -m unittest", "evidence": ["logs/wrapper.txt"]}
        result.update(fields)
        return ledger.record_result(self.store, "case", "validation", "supervisor",
                                    json.dumps(result, ensure_ascii=False), now=now)

    def interruption(self, outcome="blocked", *, now=102, **fields):
        result = {
            "outcome": outcome,
            "category": "model_refusal",
            "operation": "run the authorized unit test command",
            "notice": "I cannot continue with this request.",
            "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt"],
        }
        result.update(fields)
        return ledger.record_result(self.store, "case", "interruption", "supervisor",
                                    json.dumps(result, ensure_ascii=False, indent=2) + "\n", now=now)

    def test_success_requires_independent_review(self):
        self.assertEqual(self.open()["next_action"], "dispatch_luna")
        self.assertEqual(self.record()["next_action"], "strong_review")
        with self.assertRaisesRegex(ledger.LedgerError, "cannot review"):
            self.record(self.result(verdict="accept"), kind="review", now=102)
        accepted = self.record(self.result(verdict="accept"), kind="review", actor="sol-review", now=102)
        self.assertEqual(accepted["state"], "done")

    def test_failed_acceptance_without_new_evidence_takes_over(self):
        self.open()
        summary = self.record(self.result(failed=["unit"]))
        self.assertEqual(summary["next_action"], "strong_takeover")
        self.assertEqual(summary["reason"], "no_new_evidence_for_repair")
        finished = self.record(kind="strong", actor="supervisor", now=102)
        self.assertEqual(finished["state"], "done")

    def test_repair_allowance_survives_worker_replacement_and_retains_exact_original(self):
        self.open()
        original = self.result(failed=["unit"], new_evidence=["logs/traceback.txt"])
        first = self.record(original)
        self.assertEqual(first["next_action"], "luna_repair")
        original_event_path = Path(first["events"][-1])
        original_event_bytes = original_event_path.read_bytes()
        # A separate invocation and a new worker label cannot reset the allowance.
        self.assertTrue(ledger.status(self.store, "case", now=102)["repair_used"])
        second = self.record(self.result(failed=["unit"], new_evidence=["logs/second-trace.txt"]),
                             actor="luna-replacement", now=103)
        self.assertEqual(second["reason"], "repair_exhausted")
        with self.assertRaisesRegex(ledger.LedgerError, "already exists"):
            self.open(now=104)
        with self.assertRaisesRegex(ledger.LedgerError, "already stopped"):
            self.record(actor="luna-third", now=104)
        self.assertEqual(original_event_path.read_bytes(), original_event_bytes)
        self.assertEqual(json.loads(original_event_bytes)["payload_text"], original)
        self.assertIn("logs/traceback.txt", second["evidence"])

    def test_repair_can_succeed_then_requires_review(self):
        self.open()
        self.record(self.result(failed=["contract"], new_evidence=["logs/contract-cause.txt"]))
        self.assertEqual(self.record(actor="luna-2", now=102)["next_action"], "strong_review")

    def test_substantive_review_rejection_overrides_passing_tests(self):
        self.open()
        self.record()
        rejected = self.record(self.result(verdict="substantive_reject"), kind="review",
                               actor="sol-review", now=102)
        self.assertEqual(rejected["next_action"], "strong_takeover")
        self.assertEqual(rejected["reason"], "substantive_review_rejection")

    def test_immediate_handoffs_and_unverified_prerequisite(self):
        for status in ["needs_decision", "blocked", "budget_exhausted"]:
            with self.subTest(status=status):
                assignment = status.replace("_", "-")
                self.open(assignment)
                result = ledger.record_result(self.store, assignment, "worker", "luna-1",
                                              self.result(status=status), now=101)
                self.assertEqual(result["next_action"], "strong_takeover")
        self.open()
        self.assertEqual(self.record(self.result(unexecuted=["contract"]))["reason"],
                         "verification_incomplete")

    def test_deadline_enforced_on_status_and_record_with_late_evidence_retained(self):
        self.open()
        self.assertEqual(ledger.status(self.store, "case", now=160)["reason"], "deadline_expired")
        late = self.record(now=161)
        self.assertEqual(late["next_action"], "strong_takeover")
        self.assertEqual(len(late["events"]), 3)
        with self.assertRaisesRegex(ledger.LedgerError, "already stopped"):
            self.record(actor="luna-another", now=162)
        self.assertEqual(self.record(kind="strong", actor="sol", now=162)["state"], "done")

    def test_status_retains_deadline_stop_and_refuses_clock_rollback(self):
        self.open()
        expired = ledger.status(self.store, "case", now=160)
        self.assertEqual(json.loads(Path(expired["events"][-1]).read_text())["kind"], "budget")
        with self.assertRaisesRegex(ledger.LedgerError, "clock went backwards"):
            ledger.status(self.store, "case", now=159)

    def test_result_budget_can_disallow_repair(self):
        self.packet["budget"]["max_worker_results"] = 1
        self.open()
        result = self.record(self.result(failed=["unit"], new_evidence=["logs/cause.txt"]))
        self.assertEqual(result["reason"], "worker_result_budget_exhausted")

    def test_expired_single_result_budget_admits_only_pending_original(self):
        self.packet["budget"]["max_worker_results"] = 1
        self.open()
        self.assertEqual(self.record(now=160)["worker_results"], 1)
        with self.assertRaisesRegex(ledger.LedgerError, "worker result budget exhausted"):
            self.record(actor="luna-replacement", now=161)
        self.assertEqual(ledger.status(self.store, "case", now=162)["worker_results"], 1)

    def test_expired_authorized_repair_accepts_one_late_report_without_reopening_luna(self):
        self.open()
        self.record(self.result(failed=["unit"], new_evidence=["logs/new-cause.txt"]))
        expired = ledger.status(self.store, "case", now=160)
        self.assertEqual(expired["next_action"], "strong_takeover")
        late = self.record(actor="luna-repair", now=161)
        self.assertEqual(late["worker_results"], 2)
        self.assertEqual(late["next_action"], "strong_takeover")
        with self.assertRaisesRegex(ledger.LedgerError, "worker result budget exhausted"):
            self.record(actor="luna-third", now=162)

    def test_optional_handoff_fields_are_validated_and_retained_exactly(self):
        self.open()
        result = json.loads(self.result(status="needs_decision"))
        result.update(commands=["python3 -m unittest"], decisions=["do not alter shared contract"],
                      remaining_acceptance_conditions=["resolve the ownership decision"])
        original = json.dumps(result, indent=4) + "\n"
        recorded = self.record(original)
        self.assertEqual(json.loads(Path(recorded["events"][-1]).read_text())["payload_text"], original)
        self.assertEqual(recorded["next_action"], "strong_takeover")
        for field in ("commands", "decisions", "remaining_acceptance_conditions"):
            with self.subTest(field=field):
                malformed = dict(result, **{field: "invalid scalar"})
                with self.assertRaisesRegex(ledger.LedgerError, field):
                    ledger.validate_result(malformed, self.packet, "worker")

    def test_invalid_or_unbounded_budgets_are_rejected(self):
        for value in [0, -1, True, 1.5, float("inf"), float("nan"), 86401]:
            with self.subTest(seconds=value):
                self.packet["budget"]["seconds"] = value
                with self.assertRaises(ledger.LedgerError):
                    self.open()
        self.packet["budget"] = {"seconds": 60, "max_worker_results": 3}
        with self.assertRaises(ledger.LedgerError):
            self.open()

    def test_acceptance_cannot_be_weakened_and_bad_input_leaves_no_event(self):
        self.open()
        result = json.loads(self.result())
        result["checks"]["passed"] = ["unit"]
        with self.assertRaisesRegex(ledger.LedgerError, "partition"):
            self.record(json.dumps(result))
        self.assertEqual(len(list((self.store / "case").glob("*.json"))), 1)
        with self.assertRaisesRegex(ledger.LedgerError, "duplicate JSON key"):
            self.record('{"status":"completed","status":"blocked"}')

    def test_concurrent_open_keeps_one_original_and_concurrent_record_cannot_overwrite(self):
        def concurrent_open(_):
            try:
                self.open()
                return True
            except ledger.LedgerError:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(concurrent_open, range(8))), 1)

        def concurrent_record(index):
            try:
                self.record(actor=f"luna-{index}")
                return True
            except ledger.LedgerError:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(concurrent_record, range(8))), 1)
        summary = ledger.status(self.store, "case", now=102)
        self.assertEqual(summary["next_action"], "strong_review")
        self.assertEqual(len(summary["events"]), 2)

    def test_changed_original_is_detected(self):
        opened = self.open()
        path = Path(opened["events"][0])
        event = json.loads(path.read_text())
        event["payload_text"] += " "
        path.chmod(0o644)
        path.write_text(json.dumps(event))
        with self.assertRaisesRegex(ledger.LedgerError, "checksum"):
            ledger.status(self.store, "case", now=101)

    def test_validation_pause_resume_keeps_repair_allowance_and_original_report(self):
        self.open()
        original = self.result(failed=["unit"], new_evidence=["logs/cause.txt"])
        self.record(original)
        self.assertTrue(ledger.status(self.store, "case", now=102)["repair_used"])
        pause = self.validation(original_report=original)
        self.assertEqual(pause["state"], "validation_paused")
        self.assertEqual(pause["worker_results"], 1)
        self.assertTrue(pause["repair_used"])
        event = json.loads(Path(pause["events"][-1]).read_text())
        self.assertEqual(json.loads(event["payload_text"])["original_report"], original)
        ready = self.validation("ready", now=103)
        self.assertEqual(ready["state"], "repair_allowed")
        self.assertEqual(ready["next_action"], "verify_existing_work")
        self.assertTrue(ready["repair_used"])
        second = self.record(self.result(failed=["unit"], new_evidence=["logs/new-cause.txt"]),
                             actor="luna-2", now=104)
        self.assertEqual(second["reason"], "repair_exhausted")

    def test_validation_review_pause_cannot_become_worker_ready(self):
        self.open()
        self.record()
        self.validation()
        restored = self.validation("ready", now=103)
        self.assertEqual(restored["state"], "review_required")
        self.assertEqual(restored["next_action"], "strong_review")

    def test_validation_unresolved_takes_over_and_cannot_resume(self):
        self.open()
        self.validation("unresolved")
        with self.assertRaisesRegex(ledger.LedgerError, "after takeover"):
            self.validation("ready", now=103)

    def test_validation_deadline_expires_while_paused(self):
        self.open()
        self.validation(now=101)
        expired = ledger.status(self.store, "case", now=160)
        self.assertEqual(expired["reason"], "deadline_expired")
        self.assertEqual(json.loads(Path(expired["events"][-1]).read_text())["kind"], "budget")
        with self.assertRaisesRegex(ledger.LedgerError, "after takeover"):
            self.validation("ready", now=161)

    def test_validation_recovery_preserves_one_pending_original_late_report(self):
        self.open()
        self.validation(now=101)
        ready = self.validation("ready", now=102)
        self.assertEqual(ready["worker_results"], 0)
        self.assertFalse(ready["repair_used"])
        ledger.status(self.store, "case", now=160)
        with self.assertRaisesRegex(ledger.LedgerError, "after takeover"):
            self.validation("ready", now=161)
        original = self.result()
        late = self.record(original, now=161)
        self.assertEqual(late["worker_results"], 1)
        self.assertEqual(late["next_action"], "strong_takeover")
        self.assertEqual(late["reason"], "deadline_expired")
        self.assertEqual(json.loads(Path(late["events"][-1]).read_text())["payload_text"], original)
        with self.assertRaisesRegex(ledger.LedgerError, "already stopped"):
            self.record(actor="luna-another", now=162)
        self.assertEqual(ledger.status(self.store, "case", now=162)["events"], late["events"])

    def test_validation_recovery_preserves_pending_repair_late_report(self):
        self.open()
        self.record(self.result(failed=["unit"], new_evidence=["logs/cause.txt"]))
        self.validation()
        ready = self.validation("ready", now=103)
        self.assertTrue(ready["repair_used"])
        ledger.status(self.store, "case", now=160)
        late = self.record(actor="luna-repair", now=161)
        self.assertEqual(late["worker_results"], 2)
        self.assertTrue(late["repair_used"])
        self.assertEqual(late["next_action"], "strong_takeover")
        with self.assertRaisesRegex(ledger.LedgerError, "worker result budget exhausted"):
            self.record(actor="luna-third", now=162)
        with self.assertRaisesRegex(ledger.LedgerError, "after takeover"):
            self.validation("blocked", now=162)
        self.assertEqual(ledger.status(self.store, "case", now=162)["events"], late["events"])

    def test_validation_recovery_keeps_single_result_budget_for_late_report(self):
        self.packet["budget"]["max_worker_results"] = 1
        self.open()
        self.validation(now=101)
        self.validation("ready", now=102)
        # Recording the pending report enforces expiry even without a prior status call.
        late = self.record(now=160)
        self.assertEqual(late["worker_results"], 1)
        self.assertEqual(late["next_action"], "strong_takeover")
        with self.assertRaisesRegex(ledger.LedgerError, "worker result budget exhausted"):
            self.record(actor="luna-replacement", now=161)
        self.assertEqual(ledger.status(self.store, "case", now=162)["events"], late["events"])

    def test_invalid_validation_outcome_types_leave_no_event(self):
        self.open()
        for outcome in ([], {}, None, True, 1, 1.5, "unknown"):
            with self.subTest(outcome=outcome):
                with self.assertRaisesRegex(ledger.LedgerError, "invalid validation outcome"):
                    self.validation(outcome, now=101)
                self.assertEqual(len(list((self.store / "case").glob("*.json"))), 1)

    def test_invalid_validation_does_not_append_event(self):
        opened = self.open()
        malformed = json.dumps({"outcome": "blocked", "command": "", "evidence": ["e"]})
        with self.assertRaisesRegex(ledger.LedgerError, "command"):
            ledger.record_result(self.store, "case", "validation", "supervisor", malformed, now=101)
        self.assertEqual(len(list((self.store / "case").glob("*.json"))), 1)

    def test_strong_completion_guides_new_distinct_assignment_to_luna(self):
        self.open()
        self.validation("unresolved")
        completed = self.record(kind="strong", actor="sol", now=103)
        self.assertEqual(completed["state"], "done")
        self.assertEqual(completed["next_action"], "done")
        self.assertEqual(completed["downstream_guidance"],
                         "consider_luna_for_separable_downstream_implementation")
        new = self.open("next-case", now=104)
        self.assertEqual(new["next_action"], "dispatch_luna")

    def test_interruption_retains_exact_context_and_does_not_consume_repair_or_result(self):
        self.open()
        first_report = self.result(failed=["unit"], new_evidence=["logs/root-cause.txt"])
        repair = self.record(first_report, now=101)
        self.assertEqual(repair["state"], "repair_allowed")
        self.assertTrue(repair["repair_used"])
        self.assertEqual(repair["worker_results"], 1)

        held_raw = json.dumps({
            "outcome": "blocked",
            "category": "service_safety_access",
            "operation": "run the integration verification command",
            "notice": "Request blocked by cyber_policy; prior unit check completed.",
            "model": "gpt-6-luna",
            "effort": "high",
            "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt", "logs/root-cause.txt"],
            "changed_paths": ["tests/test_supervisor.py"],
            "decisions": ["keep the integration command blocked"],
        }, ensure_ascii=False, indent=2) + "\n"
        held = self.record(held_raw, kind="interruption", actor="supervisor", now=102)
        self.assertEqual(held["state"], "interruption_paused")
        self.assertEqual(held["next_action"], "assess_interruption")
        self.assertEqual(held["interruption_resume_state"], "repair_allowed")
        self.assertEqual(held["worker_results"], 1)
        self.assertTrue(held["repair_used"])
        self.assertIn("logs/partial-test-output.txt", held["evidence"])
        self.assertIn("logs/root-cause.txt", held["evidence"])
        self.assertIn("tests/test_supervisor.py", held["changed_paths"])
        retained = json.loads(Path(held["events"][-1]).read_text())
        self.assertEqual(retained["payload_text"], held_raw)

        resumed = self.record(json.dumps({
            "outcome": "resolved",
            "category": "service_safety_access",
            "operation": "run the integration verification command",
            "notice": "Synthetic fixture: supported resolution recorded; no real service was contacted.",
            "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt"],
            "resolution_evidence": ["records/synthetic-supported-resolution.txt"],
        }), kind="interruption", actor="supervisor", now=103)
        self.assertEqual(resumed["state"], "repair_allowed")
        self.assertEqual(resumed["next_action"], "verify_existing_work")
        self.assertEqual(resumed["worker_results"], 1)
        self.assertTrue(resumed["repair_used"])
        self.assertIn("records/synthetic-supported-resolution.txt", resumed["evidence"])

        exhausted = self.record(self.result(failed=["unit"], new_evidence=["logs/repair.txt"]),
                                actor="luna-repair", now=104)
        self.assertEqual(exhausted["reason"], "repair_exhausted")
        self.assertEqual(exhausted["worker_results"], 2)

    def test_interruption_hold_cannot_be_laundered_through_other_record_kinds(self):
        self.open()
        self.interruption(now=101)
        before = ledger.status(self.store, "case", now=101)
        attempts = [
            ("worker", "luna-2", self.result()),
            ("review", "sol-review", self.result(verdict="accept")),
            ("strong", "sol", self.result()),
            ("validation", "supervisor", json.dumps({
                "outcome": "blocked", "command": "python3 -m unittest", "evidence": ["logs/denial.txt"]
            })),
        ]
        for kind, actor, raw in attempts:
            with self.subTest(kind=kind):
                with self.assertRaises(ledger.LedgerError):
                    ledger.record_result(self.store, "case", kind, actor, raw, now=102)
                self.assertEqual(ledger.status(self.store, "case", now=101)["events"], before["events"])
        duplicate = {
            "outcome": "blocked", "category": "model_uncertainty",
            "operation": "a different operation", "notice": "uncertain", "scope": ["other"],
            "evidence": ["logs/other.txt"],
        }
        with self.assertRaisesRegex(ledger.LedgerError, "match the held operation"):
            ledger.record_result(self.store, "case", "interruption", "supervisor",
                                 json.dumps(duplicate), now=102)
        self.assertEqual(ledger.status(self.store, "case", now=101)["events"], before["events"])

    def test_interruption_deadline_keeps_hold_blocked_and_forbids_resolution(self):
        self.open()
        self.interruption(now=101)
        expired = ledger.status(self.store, "case", now=160)
        self.assertEqual(expired["state"], "interruption_paused")
        self.assertEqual(expired["next_action"], "assess_interruption")
        self.assertEqual(expired["reason"], "model_refusal")
        self.assertEqual(expired["remaining_seconds"], 0)
        self.assertEqual(len(expired["events"]), 2)
        resolution = {
            "outcome": "resolved", "category": "model_refusal",
            "operation": "run the authorized unit test command",
            "notice": "prior notice retained", "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt"],
            "resolution_evidence": ["records/resolution.txt"],
        }
        with self.assertRaisesRegex(ledger.LedgerError, "after the original deadline"):
            self.record(json.dumps(resolution), kind="interruption", now=161)
        self.assertEqual(ledger.status(self.store, "case", now=160)["events"], expired["events"])

    def test_interruption_restores_genuine_takeover_to_strong_takeover(self):
        self.open()
        takeover = self.record(self.result(status="needs_decision"), now=101)
        self.assertEqual(takeover["state"], "takeover")
        held = self.interruption(now=102)
        self.assertEqual(held["interruption_resume_state"], "takeover")
        resolved = self.record(json.dumps({
            "outcome": "resolved", "category": "model_refusal",
            "operation": "run the authorized unit test command", "notice": "refusal retained",
            "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt"],
            "resolution_evidence": ["records/refusal-resolution.txt"],
        }), kind="interruption", now=103)
        self.assertEqual(resolved["state"], "takeover")
        self.assertEqual(resolved["next_action"], "strong_takeover")
        finished = self.record(kind="strong", actor="sol", now=104)
        self.assertEqual(finished["state"], "done")

    def test_interruption_evidence_does_not_change_first_repair_eligibility(self):
        self.open()
        self.interruption(now=101, evidence=["logs/diagnosis.txt"])
        self.interruption("resolved", now=102, evidence=["logs/diagnosis.txt"],
                          resolution_evidence=["records/synthetic-resolution.txt"])
        failed = self.record(self.result(failed=["unit"], new_evidence=["logs/diagnosis.txt"]), now=103)
        self.assertEqual(failed["next_action"], "luna_repair")
        self.assertTrue(failed["repair_used"])
        self.assertIn("logs/diagnosis.txt", failed["evidence"])

    def test_expired_interruption_retains_late_original_report_without_resuming(self):
        self.open()
        held = self.interruption(now=101)
        attachments = self.store / "case" / "attachments"
        attachments.mkdir()
        original = self.result(failed=["unit"], new_evidence=["logs/late-cause.txt"])
        report = attachments / "late-worker-result.json"
        report.write_text(original)
        retained = self.interruption(now=161, evidence=[str(report)], changed_paths=["fixture.py"])
        self.assertEqual(retained["state"], "interruption_paused")
        self.assertEqual(retained["next_action"], "assess_interruption")
        self.assertEqual(retained["interruption_resume_state"], held["interruption_resume_state"])
        self.assertEqual(retained["deadline_utc"], held["deadline_utc"])
        self.assertEqual(retained["remaining_seconds"], 0)
        self.assertEqual(retained["worker_results"], 0)
        self.assertFalse(retained["repair_used"])
        self.assertIn(str(report), retained["evidence"])
        self.assertIn("fixture.py", retained["changed_paths"])
        self.assertEqual(report.read_text(), original)
        self.assertEqual(len(retained["events"]), 3)

    def test_interruption_restores_validation_pause_without_opening_worker_route(self):
        self.open()
        paused = self.validation(now=101)
        self.assertEqual(paused["state"], "validation_paused")
        held = self.interruption(now=102)
        self.assertEqual(held["interruption_resume_state"], "validation_paused")
        resolved = self.record(json.dumps({
            "outcome": "resolved", "category": "model_refusal",
            "operation": "run the authorized unit test command", "notice": "refusal retained",
            "scope": ["tests/test_supervisor.py"],
            "evidence": ["logs/partial-test-output.txt"],
            "resolution_evidence": ["records/refusal-resolution.txt"],
        }), kind="interruption", now=103)
        self.assertEqual(resolved["state"], "validation_paused")
        self.assertEqual(resolved["next_action"], "resolve_validation")
        ready = self.validation("ready", now=104)
        self.assertEqual(ready["state"], "ready")
        self.assertEqual(ready["next_action"], "verify_existing_work")

    def test_interruption_schema_and_matching_rejections_append_no_events(self):
        opened = self.open()
        malformed_results = [
            {"outcome": "blocked", "category": "model_refusal", "operation": "op",
             "notice": "notice", "scope": ["scope"], "evidence": []},
            {"outcome": "resolved", "category": "model_refusal", "operation": "op",
             "notice": "notice", "scope": ["scope"], "evidence": ["e"]},
            {"outcome": "blocked", "category": "unknown", "operation": "op",
             "notice": "notice", "scope": ["scope"], "evidence": ["e"]},
            {"outcome": "blocked", "category": "model_refusal", "operation": "op",
             "notice": "notice", "scope": ["scope"], "evidence": ["e"], "resolution_evidence": ["r"]},
            {"outcome": "blocked", "category": "model_refusal", "operation": "op",
             "notice": "notice", "scope": "scope", "evidence": ["e"]},
        ]
        for malformed in malformed_results:
            with self.subTest(malformed=malformed):
                with self.assertRaises(ledger.LedgerError):
                    self.record(json.dumps(malformed), kind="interruption", now=101)
                self.assertEqual(ledger.status(self.store, "case", now=100)["events"], opened["events"])

        self.interruption(now=101)
        held = ledger.status(self.store, "case", now=101)
        for field, replacement in (("category", "model_uncertainty"),
                                   ("operation", "a different operation"),
                                   ("scope", ["a different scope"])):
            resolution = {
                "outcome": "resolved", "category": "model_refusal",
                "operation": "run the authorized unit test command", "notice": "resolution",
                "scope": ["tests/test_supervisor.py"],
                "evidence": ["logs/partial-test-output.txt"],
                "resolution_evidence": ["records/resolution.txt"],
            }
            resolution[field] = replacement
            with self.subTest(mismatch=field):
                with self.assertRaisesRegex(ledger.LedgerError, "match the held operation"):
                    self.record(json.dumps(resolution), kind="interruption", now=102)
                self.assertEqual(ledger.status(self.store, "case", now=101)["events"], held["events"])


if __name__ == "__main__":
    unittest.main()
