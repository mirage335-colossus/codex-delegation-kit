"""Synthetic backend observations against real disposable repository snapshots.

These tests exercise admission, evidence and acceptance transitions without
model calls. Command events are fixtures, not proof of live shell integration.
"""
from __future__ import annotations

import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import controller
import engineering
import supervisor
from controller_store import Store, file_identity


class EngineeringControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-controller-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.run = self.root / "run"
        self.repo = self.repository("repo")
        self.runtime = mock.patch.object(controller, "runtime_identity", return_value={"fixture": "synthetic-backend-v1"})
        self.runtime.start()
        self.addCleanup(self.runtime.stop)

    def repository(self, name):
        path = self.workspace / name
        path.mkdir(parents=True)
        (path / "calc.py").write_text("def total(values):\n    return sum(values[1:])\n")
        (path / "test_calc.py").write_text("# Existing acceptance fixture; must not be weakened.\n")
        subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(path), "add", "calc.py", "test_calc.py"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(path), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture baseline"], check=True, capture_output=True)
        return path

    def worker(self, name="fix", repo=None, **extra):
        return {"id": name, "role": "worker", "cwd": str(repo or self.repo),
                "prompt": "Include every input in total; preserve the original acceptance.",
                "write_scope": ["calc.py"], "allowed_commands": ["Read source and run python -B -m unittest"],
                "acceptance_checks": ["unit"], "timeout_seconds": 20, **extra}

    def scout(self, name="hypothesis", repo=None, **extra):
        return {"id": name, "role": "scout", "cwd": str(repo or self.repo),
                "prompt": "Inspect actual code and distinguish the stated hypothesis.",
                "allowed_commands": ["Read source and run bounded python -B diagnostic"],
                "hypothesis": "The first item is skipped.",
                "experiment": "Compare total([7]) with total([0, 7]) using the actual implementation.",
                "comparison": {"input": [7], "environment": "disposable Python fixture"},
                "timeout_seconds": 20, **extra}

    def initialize(self, tasks, **policy):
        return controller.initialize(self.run, {
            "version": 1, "id": "engineering-fixture", "workspace": str(self.workspace),
            "policy": {"capacity": {"reasoning": 4, "processes": 4, "cpu": 4, "memory_mb": 256},
                       "allowed_cwds": [str(self.workspace)], "allowed_executables": [str(Path(sys.executable).resolve())],
                       "process_boundary": "inherited", "boundary_description": "Disposable synthetic backend fixture.",
                       "network": False, "approval": "never", "sandbox": "workspace-write",
                       "agent_profile": "engineering", "model": "fixture-model", "effort": "medium", "service_tier": "default",
                       "max_active_seconds": 300, "deadline_seconds": 300, **policy},
            "tasks": tasks})

    def state(self):
        store = Store(self.run)
        try:
            return store.read()
        finally:
            store.close()

    def task_repo(self, task_id):
        return Path(self.state()["tasks"][task_id]["cwd"])

    def input_name(self, task_id, name):
        state = self.state()
        return str(Path(state["tasks"][task_id]["cwd"]).relative_to(Path(state["workspace"])) / name)

    def competing_writer(self, state, original="fix"):
        """Admission probe for an unrelated writer to the same physical copy."""
        task = copy.deepcopy(state["tasks"][original])
        task.update(id="unrelated-writer", budget_owner="unrelated-writer", attempts=[])
        return task

    def begin(self, expected):
        """Claim normally, then supply a synthetic backend launch boundary."""
        instance = controller.Controller(self.run)
        try:
            claim = instance.claim(time.time())
            self.assertIsNotNone(claim, instance.summary())
            task, attempt, _ = claim
            self.assertEqual(task["id"], expected)
            directory = instance.operation_directory(attempt["id"])
            directory.mkdir(parents=True)
            if task.get("scratch_directory"):
                Path(task["scratch_directory"]).mkdir(mode=0o700, exist_ok=True)
            before = engineering.snapshot(task["cwd"], task.get("audit_scope", task["write_scope"]))
            with instance.store.transaction() as (state, _):
                state["attempts"][attempt["id"]].update(
                    engineering_before=before, launch_intent={"synthetic": True})
            return attempt["id"]
        finally:
            instance.close()

    def proposed(self, *, failed=False, review=False):
        report = {"status": "completed", "changed_paths": [],
                  "checks": {"passed": [] if failed else ["unit"], "failed": ["unit"] if failed else [], "unexecuted": []},
                  "evidence": ["synthetic command fixture"], "commands": ["python -B -m unittest"]}
        if failed:
            report["new_evidence"] = ["first observed unit failure"]
        if review:
            report["verdict"] = "substantive_reject" if failed else "accept"
        return report

    def finish(self, aid, result, *, commands=True, outcome="completed", returncode=0):
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                attempt = state["attempts"][aid]
                task = state["tasks"][attempt["task"]]
                attempt.update(released=True, ingested=True, finished_at=time.time())
                command_events = [{"id": "synthetic-check", "command": "python -B -m unittest",
                                   "cwd": task["cwd"], "status": "completed", "exitCode": returncode,
                                   "aggregatedOutput": "synthetic command evidence", "completed": True}] if commands else []
                backend = {"status": "completed", "result": result, "commands": command_events,
                           "file_changes": [], "effective": {"model": "fixture-model", "reasoningEffort": "medium"}}
                observation = {"status": outcome, "state": outcome, "returncode": returncode, "released": True}
                with mock.patch("agent_backend.collect", return_value=backend):
                    controller.ingest_result(state, task, attempt, observation, self.run / "operations" / aid, time.time())
        finally:
            store.close()
        return self.state()

    def legacy_invalid_report(self):
        """Retained receipt from an older helper rejecting model command objects."""
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        raw = self.proposed()
        raw["commands"] = [{"command": "python -B -m unittest", "claimed_exit": 0}]
        with mock.patch.object(controller, "helper_event", side_effect=ValueError("legacy commands must be strings")):
            state = self.finish(aid, raw)
        self.assertEqual(state["tasks"]["fix"]["status"], "invalid")
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["attempts"][aid]["observation"] = {
                    "status": "completed", "state": "completed", "returncode": 0, "released": True}
                state["tasks"]["fix"]["service_seconds"] = 7.25
                state["active_service_seconds"] = 8.5
        finally:
            store.close()
        directory = self.run / "operations" / aid
        (directory / "backend-events.jsonl").write_text('{"synthetic":"retained completed receipt"}\n')
        (directory / "backend-result.json").write_text(json.dumps(raw))
        return aid, raw

    def test_model_command_objects_are_replaced_by_observed_receipt_references(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        raw = self.proposed()
        raw["commands"] = [{"command": "model claimed this ran", "exit": "unverified"}]
        untouched = copy.deepcopy(raw)
        state = self.finish(aid, raw)
        parent = state["tasks"]["fix"]
        self.assertEqual(parent["status"], "awaiting_acceptance")
        self.assertEqual(state["attempts"][aid]["agent_result"]["result"], untouched)
        validated = json.loads(parent["helper_events"][-1]["payload_text"])
        self.assertEqual(validated["commands"], [
            f"synthetic-check: exit=0; {self.run / 'operations' / aid / 'backend-events.jsonl'}"])
        self.assertEqual(state["tasks"]["fix.review.1"]["role"], "reviewer")
        self.assertNotIn("success", parent["evidence"])

    def test_retained_invalid_report_revalidates_without_execution_or_artifact_rewrite(self):
        aid, raw = self.legacy_invalid_report()
        controller.control(self.run, "pause", "user pause survives report validation")
        before = self.state()
        directory = self.run / "operations" / aid
        artifacts = {path: path.read_bytes() for path in directory.iterdir() if path.is_file()}
        reason = "Reviewed the helper format correction; validate the original completed receipt."
        with mock.patch("agent_backend.collect") as collect, mock.patch("execution.launch") as launch:
            controller.continue_engineering(self.run, "fix", reason)
        collect.assert_not_called()
        launch.assert_not_called()
        state = self.state()
        parent = state["tasks"]["fix"]
        self.assertEqual(state["mode"], "paused")
        self.assertEqual(parent["attempts"], [aid])
        self.assertEqual(set(state["attempts"]), {aid})
        self.assertEqual(parent["service_seconds"], before["tasks"]["fix"]["service_seconds"])
        self.assertEqual(state["active_service_seconds"], before["active_service_seconds"])
        self.assertEqual(parent["helper_events"][0], before["tasks"]["fix"]["helper_events"][0])
        self.assertEqual([event["kind"] for event in parent["helper_events"]], ["open", "worker"])
        self.assertEqual(parent["status"], "awaiting_acceptance")
        self.assertNotIn("success", parent["evidence"])
        self.assertEqual(state["tasks"]["fix.review.1"]["attempts"], [])
        self.assertEqual(state["attempts"][aid]["agent_result"]["result"], raw)
        history = parent["report_validation_history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["attempt"], aid)
        self.assertEqual(history[0]["original_error"], before["tasks"]["fix"]["reason"])
        self.assertEqual(history[0]["reason"], reason)
        self.assertEqual({path: path.read_bytes() for path in artifacts}, artifacts)

    def test_retained_report_rejects_expiry_or_mutated_patch_without_replacement(self):
        for condition in ("run_expired", "assignment_expired", "mutated_patch"):
            with self.subTest(condition=condition):
                self.run = self.root / condition
                aid, _ = self.legacy_invalid_report()
                store = Store(self.run)
                try:
                    with store.transaction() as (state, _):
                        if condition == "run_expired":
                            state["deadline"] = time.time() - 1
                        elif condition == "assignment_expired":
                            state["tasks"]["fix"]["helper_events"][0]["recorded_at"] = time.time() - 1000
                finally:
                    store.close()
                if condition == "mutated_patch":
                    (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return 999\n")
                before = self.state()
                with self.assertRaises(ValueError):
                    controller.continue_engineering(self.run, "fix", "Revalidate only the retained original report.")
                self.assertEqual(self.state(), before)
                self.assertEqual(set(self.state()["attempts"]), {aid})
                self.assertNotIn("fix.review.1", self.state()["tasks"])

    def test_compact_packet_generates_ids_and_submission_is_idempotent(self):
        self.initialize([])
        task = self.worker()
        del task["id"]
        first = controller.submit(self.run, task)
        second = controller.submit(self.run, copy.deepcopy(task))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)
        normalized = self.state()["tasks"][first[0]]
        self.assertTrue(normalized["engineering"])
        self.assertEqual(normalized["acceptance"]["packet"]["acceptance_checks"], ["unit"])
        self.assertEqual(set(normalized["continuations"]), {"review", "worker", "strong"})
        self.assertEqual(normalized["attempts"], [])

    def test_authorized_patch_preserves_baseline_and_requires_review(self):
        source_hash = file_identity(self.repo / "calc.py")
        self.initialize([self.worker()])
        aid = self.begin("fix")
        input_name = self.input_name("fix", "calc.py")
        original = self.state()["attempts"][aid]["input_identity"][input_name]
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(aid, self.proposed())
        parent, attempt = state["tasks"]["fix"], state["attempts"][aid]
        self.assertEqual(parent["status"], "awaiting_acceptance")
        self.assertNotIn("success", parent["evidence"])
        self.assertEqual(attempt["input_identity"][input_name], original)
        self.assertNotEqual(attempt["produced_identity"][input_name], original)
        self.assertIn("-    return sum(values[1:])", attempt["engineering_result"]["patch"])
        reviewer = state["tasks"]["fix.review.1"]
        self.assertEqual(reviewer["role"], "reviewer")
        self.assertEqual(reviewer["write_scope"], [Path(reviewer["scratch_directory"]).name + "/"])
        self.assertFalse(engineering.owns("calc.py", reviewer["write_scope"]))
        self.assertEqual(reviewer["expected_workspace"], attempt["engineering_result"]["after_digest"])
        self.assertNotEqual(self.task_repo("fix"), self.repo)
        self.assertEqual(file_identity(self.repo / "calc.py"), source_hash, "managed edits must leave the original repository unchanged")

    def test_overlapping_experiments_receive_independent_matched_copies(self):
        self.initialize([
            self.scout("one", priority=2, write_scope=["calc.py"]),
            self.scout("two", priority=1, write_scope=["calc.py"]),
        ])
        first, second = self.task_repo("one"), self.task_repo("two")
        self.assertNotEqual(first, second)
        self.assertNotEqual(first, self.repo)
        self.assertNotEqual(second, self.repo)
        self.assertEqual(engineering.snapshot(first)["files"], engineering.snapshot(second)["files"])
        first_aid = self.begin("one")
        second_aid = self.begin("two")
        (first / "calc.py").write_text("def total(values):\n    return 7\n")
        state = self.finish(first_aid, {"outcome": "hypothesis_rejected", "findings": "Private counterexample experiment.",
                                       "evidence": ["synthetic observation"]})
        self.assertEqual(state["tasks"]["one"]["outcome"], "hypothesis_rejected")
        self.assertFalse(state["attempts"][second_aid]["released"])
        self.assertEqual((second / "calc.py").read_bytes(), (self.repo / "calc.py").read_bytes())

    def test_unowned_write_holds_evidence_without_approving_patch(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "test_calc.py").write_text("# Silently weakened check must be held.\n")
        state = self.finish(aid, self.proposed())
        self.assertEqual(state["tasks"]["fix"]["status"], "blocked")
        self.assertEqual(state["holds"]["fix"]["category"], "workspace")
        self.assertIn("test_calc.py", state["attempts"][aid]["engineering_result"]["violations"])
        self.assertNotIn("success", state["tasks"]["fix"]["evidence"])
        self.assertTrue(state["attempts"][aid]["released"])

    def test_diagnostic_outcomes_require_observations_and_are_not_votes(self):
        self.initialize([self.scout()])
        aid = self.begin("hypothesis")
        state = self.finish(aid, {"outcome": "failure_reproduced", "findings": "The model agrees with the hypothesis.",
                                  "evidence": ["reasoning only"]}, commands=False)
        task = state["tasks"]["hypothesis"]
        self.assertEqual(task["outcome"], "not_tested")
        self.assertNotEqual(task["status"], "completed")
        self.assertNotIn("failure_reproduced", task["evidence"])

    def test_diagnostic_setup_failure_does_not_release_result_dependency(self):
        self.initialize([self.scout()])
        aid = self.begin("hypothesis")
        state = self.finish(aid, {"outcome": "setup_failed", "findings": "The required fixture was unavailable.",
                                  "evidence": ["missing fixture"]}, commands=False)
        task = state["tasks"]["hypothesis"]
        self.assertEqual(task["status"], "setup_error")
        self.assertEqual(task["outcome"], "setup_failed")
        self.assertEqual(task["evidence"], {})

    def test_malformed_diagnostic_result_is_invalid_without_losing_ingestion(self):
        self.initialize([self.scout()])
        aid = self.begin("hypothesis")
        state = self.finish(aid, {"outcome": "confirmed-by-three-agents", "findings": "agreement",
                                  "evidence": ["unsupported result kind"]})
        self.assertEqual(state["tasks"]["hypothesis"]["status"], "invalid")
        self.assertTrue(state["attempts"][aid]["released"])
        self.assertTrue(state["attempts"][aid]["ingested"])
        self.assertFalse(state["tasks"]["hypothesis"]["evidence"])

    def test_prompt_fast_result_releases_implementation_while_slow_branch_runs(self):
        slow_repo = self.repository("slow")
        implementation_repo = self.repository("implementation")
        self.initialize([
            self.scout("fast", priority=3), self.scout("slow", repo=slow_repo, priority=2),
            self.worker("fix", repo=implementation_repo, priority=1,
                        depends_on=[{"task": "fast", "evidence": "failure_reproduced"}]),
        ])
        fast = self.begin("fast")
        slow = self.begin("slow")
        state = self.finish(fast, {"outcome": "failure_reproduced", "findings": "Actual singleton input returns zero.",
                                   "evidence": ["synthetic observed failing command"]}, returncode=1)
        original_evidence = copy.deepcopy(state["tasks"]["fast"]["evidence"]["failure_reproduced"])
        fix = self.begin("fix")
        self.assertFalse(self.state()["attempts"][slow]["released"])
        self.assertNotEqual(fix, fast)
        (self.task_repo("fast") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                controller.refresh(state, time.time())
        finally:
            store.close()
        retained = self.state()["tasks"]["fast"]["evidence"]["failure_reproduced"]
        self.assertEqual(retained, original_evidence)
        self.assertTrue(retained["historical"])
        self.assertIn("hypothesis", retained)
        self.assertIn("comparison", retained)

    def test_readonly_experiments_share_repo_but_writer_waits(self):
        self.initialize([self.scout("one", priority=3)], sandbox="read-only")
        self.begin("one")
        state = self.state()
        reader = copy.deepcopy(state["tasks"]["one"])
        reader.update(id="second-read", attempts=[])
        self.assertTrue(controller.fits(reader, state))
        writer = copy.deepcopy(reader)
        writer.update(id="writer", role="worker", write_scope=["calc.py"])
        self.assertFalse(controller.fits(writer, state))
        writer["cwd"] = str(Path(reader["cwd"]) / "nested")
        self.assertFalse(controller.fits(writer, state), "nested workspace writes also conflict with the reader")
        self.assertEqual(controller.usage(state)[0]["reasoning"], 1)

    def test_workspace_ownership_survives_review_gap_and_releases_after_acceptance(self):
        self.initialize([self.worker(priority=3)])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(aid, self.proposed())
        self.assertEqual(controller.usage(state)[0]["reasoning"], 0)
        self.assertFalse(controller.fits(self.competing_writer(state), state))
        self.assertTrue(controller.fits(state["tasks"]["fix.review.1"], state))
        review = self.begin("fix.review.1")
        state = self.finish(review, self.proposed(review=True))
        self.assertEqual(state["tasks"]["fix"]["status"], "completed")
        self.assertTrue(controller.fits(self.competing_writer(state), state))

    def test_repair_review_binds_final_bytes_and_preserves_original_failure(self):
        self.initialize([self.worker(priority=3)])
        original = self.begin("fix")
        failed = self.proposed(failed=True)
        state = self.finish(original, failed, returncode=1)
        self.assertEqual(state["tasks"]["fix"]["acceptance_status"], "repair_allowed")
        repair = self.begin("fix.worker.1")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(repair, self.proposed())
        self.assertEqual(state["tasks"]["fix"]["producing_attempt"], repair)
        review = self.begin("fix.review.1")
        state = self.finish(review, self.proposed(review=True))
        parent = state["tasks"]["fix"]
        self.assertEqual(parent["status"], "completed")
        self.assertEqual(parent["evidence"]["success"]["attempt"], review)
        self.assertEqual(parent["producing_attempt"], repair)
        self.assertEqual(parent["evidence"]["success"]["inputs"][self.input_name("fix", "calc.py")], file_identity(self.task_repo("fix") / "calc.py"))
        original_report = json.loads(parent["helper_events"][1]["payload_text"])
        self.assertEqual(original_report["checks"]["failed"], ["unit"])
        self.assertEqual(state["attempts"][original]["agent_result"]["result"], failed)
        self.assertTrue(controller.fits(self.competing_writer(state), state), "accepted repair must release its workspace owner")

    def test_takeover_patch_requires_another_independent_review(self):
        self.initialize([self.worker()])
        original = self.begin("fix")
        self.finish(original, self.proposed())
        review = self.begin("fix.review.1")
        self.finish(review, self.proposed(failed=True, review=True))
        owner = self.begin("fix.strong.1")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(owner, self.proposed())
        self.assertEqual(state["tasks"]["fix"]["status"], "awaiting_acceptance")
        self.assertNotIn("success", state["tasks"]["fix"]["evidence"])
        independent = self.begin("fix.review.2")
        self.assertNotEqual(owner, independent)
        state = self.finish(independent, self.proposed(review=True))
        self.assertEqual(state["tasks"]["fix"]["status"], "completed")
        self.assertEqual(state["tasks"]["fix"]["evidence"]["success"]["attempt"], independent)
        self.assertEqual(state["tasks"]["fix"]["producing_attempt"], owner)

    def test_changed_patch_before_review_is_held_before_backend_dispatch(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        self.finish(aid, self.proposed())
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return -1\n")
        instance = controller.Controller(self.run)
        try:
            claim = instance.claim(time.time())
            self.assertEqual(claim[0]["id"], "fix.review.1")
            with mock.patch("execution.launch") as launch, mock.patch("agent_backend.prepare") as prepare:
                instance.dispatch(claim)
            launch.assert_not_called()
            prepare.assert_not_called()
        finally:
            instance.close()
        state = self.state()
        self.assertEqual(state["tasks"]["fix.review.1"]["status"], "blocked")
        self.assertIn("workspace changed", state["holds"]["fix.review.1"]["notice"])
        self.assertNotIn("success", state["tasks"]["fix"]["evidence"])

    def test_recovered_controller_preserves_active_attempt_patch_and_user_pause(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        patch_hash = file_identity(self.task_repo("fix") / "calc.py")
        controller.control(self.run, "pause", "user paused dispatch")
        instance = controller.Controller(self.run)
        try:
            with mock.patch("execution.observe", return_value={"state": "running", "released": False,
                                                                "started_at": time.time() - .1}), \
                    mock.patch("execution.launch") as launch:
                instance.run(max_seconds=.01)
            launch.assert_not_called()
        finally:
            instance.close()
        state = self.state()
        self.assertEqual(state["mode"], "paused")
        self.assertEqual(state["tasks"]["fix"]["attempts"], [aid])
        self.assertFalse(state["attempts"][aid]["released"])
        self.assertEqual(file_identity(self.task_repo("fix") / "calc.py"), patch_hash)
        state = self.finish(aid, self.proposed())
        self.assertEqual(state["mode"], "paused")
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
        finally:
            instance.close()
        controller.control(self.run, "resume")
        review = self.begin("fix.review.1")
        self.assertNotEqual(review, aid)
        self.assertEqual(self.state()["tasks"]["fix"]["attempts"], [aid])

    def test_interrupted_patch_requires_reconciliation_and_preserves_user_stop(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(aid, self.proposed(), outcome="cancelled")
        task = state["tasks"]["fix"]
        self.assertEqual(task["status"], "blocked")
        self.assertIn("return sum(values)", (self.run / "operations" / aid / "patch.diff").read_text())
        self.assertNotIn("success", task["evidence"])
        controller.control(self.run, "stop", "explicit user stop")
        with self.assertRaisesRegex(ValueError, "workspace_digest"):
            controller.resolve(self.run, "fix", aid, {"evidence": ["looked at patch"]})
        resolution = {"evidence": ["reviewed the retained patch and command ownership"], "action": "continue",
                      "workspace_digest": engineering.snapshot(self.task_repo("fix"), ["calc.py"])["digest"]}
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["attempts"][aid]["released"] = False
            with self.assertRaisesRegex(ValueError, "verifiably released"):
                controller.resolve(self.run, "fix", aid, resolution)
            with store.transaction() as (state, _):
                state["attempts"][aid]["released"] = True
        finally:
            store.close()
        controller.resolve(self.run, "fix", aid, resolution)
        state = self.state()
        self.assertEqual(state["mode"], "stopped")
        self.assertEqual(state["tasks"]["fix"]["attempts"], [aid])
        self.assertEqual(state["tasks"]["fix"]["continuation_context"]["previous_attempt"], aid)
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
        finally:
            instance.close()
        controller.control(self.run, "resume")
        resumed = self.begin("fix")
        self.assertNotEqual(resumed, aid)
        state = self.state()
        self.assertEqual(state["tasks"]["fix"]["attempts"], [aid, resumed])
        self.assertEqual(state["attempts"][resumed]["engineering_before"]["files"]["calc.py"], file_identity(self.task_repo("fix") / "calc.py"))

    def test_resolved_setup_hold_reuses_existing_scratch_through_actual_dispatch(self):
        self.initialize([self.worker()])
        instance = controller.Controller(self.run)
        try:
            first = instance.claim(time.time())
            self.assertIsNotNone(first)
            original = first[1]["id"]

            def prepared(task, policy, directory):
                return {"argv": [sys.executable, "-B", "-c", "pass"], "cwd": task["cwd"],
                        "env": {}, "timeout_seconds": task["timeout_seconds"]}

            # Exercise dispatch's actual scratch creation, immutable snapshot,
            # and launch-intent path. No executable or model is launched.
            with mock.patch("agent_backend.prepare", side_effect=prepared), \
                    mock.patch("execution.launch", return_value={"state": "running", "released": False}) as launch:
                instance.dispatch(first)
            launch.assert_called_once()
            scratch = Path(self.state()["tasks"]["fix"]["scratch_directory"])
            self.assertTrue(scratch.is_dir())
            marker = scratch / "retained-setup.log"
            marker.write_text("Retain this partial setup evidence across explicit continuation.\n")
            marker_hash = file_identity(marker)
            observed = {"state": "completed", "released": True, "returncode": 1,
                        "started_at": first[1]["claimed_at"], "finished_at": time.time()}
            held = {"status": "hold", "result": None, "commands": [], "file_changes": [],
                    "detail": "synthetic pre-inference runtime contract mismatch", "effective": {}}
            with mock.patch("execution.observe", return_value=observed), \
                    mock.patch("agent_backend.collect", return_value=held):
                instance.observe(time.time())
            state = self.state()
            self.assertEqual(state["tasks"]["fix"]["status"], "blocked")
            self.assertEqual(state["holds"]["fix"]["category"], "backend")
            self.assertTrue(state["attempts"][original]["released"])
            self.assertTrue(state["attempts"][original]["ingested"])
            task = state["tasks"]["fix"]
            controller.resolve(self.run, "fix", original, {
                "action": "continue", "workspace_digest": engineering.snapshot(task["cwd"], task["audit_scope"])["digest"],
                "evidence": ["synthetic runtime contract correction reviewed; retain the existing scratch evidence"],
            })
            second = instance.claim(time.time())
            self.assertIsNotNone(second)
            continued = second[1]["id"]
            self.assertNotEqual(continued, original)
            self.assertEqual(second[0]["scratch_directory"], str(scratch))
            with mock.patch("agent_backend.prepare", side_effect=prepared) as prepare, \
                    mock.patch("execution.launch", return_value={"state": "running", "released": False}) as launch:
                instance.dispatch(second)
            prepare.assert_called_once()
            launch.assert_called_once()
            state = self.state()
            self.assertNotIn("fix", state["holds"])
            self.assertEqual(state["tasks"]["fix"]["status"], "active")
            self.assertEqual(state["tasks"]["fix"]["attempts"], [original, continued])
            self.assertIn("launch_intent", state["attempts"][continued])
            self.assertEqual(file_identity(marker), marker_hash)
            self.assertEqual(state["attempts"][continued]["engineering_before"]["files"][scratch.name + "/retained-setup.log"], marker_hash)
            self.assertEqual(len(state["tasks"]["fix"]["hold_history"]), 1)
        finally:
            instance.close()

    def test_engineering_rejects_automatic_restart_and_manual_acceptance(self):
        with self.assertRaisesRegex(ValueError, "automatically restarted"):
            self.initialize([self.worker(preemption="restart", restart_safe=True)])
        self.run = self.root / "valid-run"
        self.initialize([self.worker()])
        aid = self.begin("fix")
        self.finish(aid, self.proposed())
        with self.assertRaisesRegex(ValueError, "independent controller stage"):
            controller.record(self.run, "fix", "review", "operator", self.proposed(review=True))

    def test_public_acceptance_contract_cannot_bypass_independent_review(self):
        self.initialize([])
        for acceptance in ({"type": "json", "equals": {"ok": True}},
                           {"type": "helper_stage", "assignment": "other", "kind": "review"}):
            with self.subTest(acceptance=acceptance):
                with self.assertRaisesRegex(ValueError, "cannot bypass"):
                    controller.submit(self.run, self.worker(acceptance=acceptance))
                self.assertFalse(self.state()["tasks"])
                self.assertFalse(list(Path(self.state()["workspace"]).iterdir()))

    def test_malformed_helper_evidence_retains_result_and_release(self):
        for index, evidence in enumerate((None, [{"unhashable": "evidence"}], [["nested"]])):
            with self.subTest(evidence=evidence):
                self.run = self.root / f"malformed-{index}"
                self.initialize([self.worker()])
                aid = self.begin("fix")
                proposed = self.proposed()
                proposed["evidence"] = evidence
                state = self.finish(aid, proposed)
                task, attempt = state["tasks"]["fix"], state["attempts"][aid]
                self.assertEqual(task["status"], "invalid")
                self.assertEqual(task["acceptance_status"], "invalid")
                self.assertTrue(attempt["released"])
                self.assertTrue(attempt["ingested"])
                self.assertEqual(attempt["agent_result"]["result"], proposed)
                self.assertEqual([event["kind"] for event in task["helper_events"]], ["open"])
                self.assertNotIn("success", task["evidence"])

    def test_blocked_worker_report_holds_without_repair_or_takeover(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        proposed = self.proposed()
        proposed.update(status="blocked", evidence=["Permission denied by the declared execution boundary"],
                        checks={"passed": [], "failed": [], "unexecuted": ["unit"]})
        state = self.finish(aid, proposed)
        task = state["tasks"]["fix"]
        self.assertEqual(task["status"], "blocked")
        self.assertEqual(state["holds"]["fix"]["category"], "engineering_operation")
        self.assertEqual(state["holds"]["fix"]["notice"], proposed)
        self.assertEqual([event["kind"] for event in task["helper_events"]], ["open"])
        _, derived = supervisor.derive(task["helper_events"], time.time(), require_strong_review=True)
        self.assertEqual(derived["worker_results"], 0)
        self.assertFalse(derived["repair_used"])
        self.assertEqual(set(state["tasks"]), {"fix"})
        self.assertIn("return sum(values)", state["attempts"][aid]["engineering_result"]["patch"])
        controller.control(self.run, "pause")
        controller.control(self.run, "resume")
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
        finally:
            instance.close()
        self.assertIn("fix", self.state()["holds"], "resume must not clear a permission hold")

    def test_failed_submit_cleans_private_copy_and_same_id_can_be_corrected(self):
        self.initialize([])
        bad = self.worker("same-id", depends_on=["missing-prerequisite"])
        source_before = engineering.snapshot(self.repo)
        with self.assertRaisesRegex(ValueError, "missing dependency"):
            controller.submit(self.run, bad)
        self.assertEqual(self.state()["tasks"], {})
        self.assertFalse(list(Path(self.state()["workspace"]).iterdir()), "failed submission leaked an orphan private copy")
        corrected = self.worker("same-id")
        self.assertEqual(controller.submit(self.run, corrected), ["same-id"])
        state = self.state()
        self.assertEqual(set(state["tasks"]), {"same-id"})
        self.assertEqual(list(Path(state["workspace"]).iterdir()), [self.task_repo("same-id")])
        self.assertEqual(engineering.snapshot(self.repo)["digest"], source_before["digest"])

    def test_explicit_input_output_paths_bind_the_actual_private_copy(self):
        self.initialize([])
        controller.submit(self.run, self.worker(inputs=["calc.py"], outputs=["calc.py"]))
        state = self.state()
        task = state["tasks"]["fix"]
        expected = str(Path(task["cwd"]).relative_to(Path(state["workspace"])) / "calc.py")
        self.assertEqual(task["inputs"], [expected])
        self.assertEqual(task["outputs"], [str(Path(task["cwd"]) / "calc.py")])
        self.assertEqual(task["input_identity"][expected], file_identity(Path(task["cwd"]) / "calc.py"))

    def test_explicit_owner_continuation_preserves_history_budget_and_user_controls(self):
        for mode in ("pause", "stop"):
            with self.subTest(mode=mode):
                self.run = self.root / f"continue-{mode}"
                self.initialize([self.worker(active_budget_seconds=120)])
                original = self.begin("fix")
                self.finish(original, self.proposed(failed=True), returncode=1)
                repair = self.begin("fix.worker.1")
                self.finish(repair, self.proposed(failed=True), returncode=1)
                owner = self.begin("fix.strong.1")
                (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values) - 1\n")
                incomplete = self.proposed(failed=True)
                incomplete["status"] = "needs_decision"
                self.finish(owner, incomplete, returncode=1)
                controller.control(self.run, mode, "retain explicit user control")
                store = Store(self.run)
                try:
                    with store.transaction() as (state, _):
                        state["tasks"]["fix"]["service_seconds"] = 7.25
                        state["active_service_seconds"] = 8.5
                finally:
                    store.close()
                prior = self.state()
                history = copy.deepcopy(prior["tasks"]["fix"]["helper_events"])
                controller.continue_engineering(self.run, "fix", "Continue the same owner responsibility with the new counterexample.")
                state = self.state()
                parent, followup = state["tasks"]["fix"], state["tasks"]["fix.strong.2"]
                self.assertEqual(state["mode"], "paused" if mode == "pause" else "stopped")
                self.assertEqual(parent["helper_events"], history)
                self.assertEqual(parent["active_budget_seconds"], 120)
                self.assertEqual(parent["service_seconds"], 7.25)
                self.assertEqual(state["active_service_seconds"], 8.5)
                self.assertEqual(state["deadline"], prior["deadline"])
                self.assertEqual(followup["budget_owner"], "fix")
                self.assertEqual(followup["cwd"], parent["cwd"])
                self.assertEqual(followup["role"], "owner")
                _, derived = supervisor.derive(history, time.time(), require_strong_review=True)
                self.assertTrue(derived["repair_used"])
                self.assertEqual(derived["worker_results"], 2)
                self.assertNotIn("fix.worker.2", state["tasks"])
                with self.assertRaisesRegex(ValueError, "existing continuation"):
                    controller.continue_engineering(self.run, "fix", "Must not duplicate pending continuation.")
                instance = controller.Controller(self.run)
                try:
                    self.assertIsNone(instance.claim(time.time()))
                finally:
                    instance.close()
                controller.control(self.run, "resume")
                next_owner = self.begin("fix.strong.2")
                (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
                state = self.finish(next_owner, self.proposed())
                self.assertEqual(state["tasks"]["fix"]["status"], "awaiting_acceptance")
                self.assertNotIn("success", state["tasks"]["fix"]["evidence"])
                for author in (owner, next_owner):
                    with self.assertRaisesRegex(ValueError, "own|author"):
                        controller.helper_event(copy.deepcopy(state["tasks"]["fix"]), "review", author,
                                                self.proposed(review=True), time.time())
                review = self.begin("fix.review.1")
                state = self.finish(review, self.proposed(review=True))
                self.assertEqual(state["tasks"]["fix"]["status"], "completed")
                self.assertEqual(state["tasks"]["fix"]["evidence"]["success"]["attempt"], review)
                self.assertEqual(state["tasks"]["fix"]["producing_attempt"], next_owner)
                self.assertEqual(state["tasks"]["fix"]["helper_events"][:len(history)], history)

    def test_reviewer_scratch_is_audited_without_authorizing_patch_changes(self):
        for change_patch in (False, True):
            with self.subTest(change_patch=change_patch):
                self.run = self.root / f"review-scratch-{change_patch}"
                self.initialize([self.worker()])
                author = self.begin("fix")
                (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
                producer_scratch = Path(self.state()["tasks"]["fix"]["scratch_directory"])
                (producer_scratch / "producer.log").write_text("actual producer fixture evidence\n")
                self.finish(author, self.proposed())
                review = self.begin("fix.review.1")
                state = self.state()
                reviewer = state["tasks"]["fix.review.1"]
                scratch = Path(reviewer["scratch_directory"])
                self.assertNotEqual(scratch, producer_scratch)
                self.assertEqual(reviewer["write_scope"], [scratch.name + "/"])
                self.assertIn(producer_scratch.name + "/", reviewer["audit_scope"])
                (scratch / "targeted-check.log").write_text("independent test output\n")
                if change_patch:
                    (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return -1\n")
                state = self.finish(review, self.proposed(review=True))
                audit = state["attempts"][review]["engineering_result"]
                self.assertIn(scratch.name + "/targeted-check.log", audit["changed_paths"])
                if change_patch:
                    self.assertEqual(state["tasks"]["fix.review.1"]["status"], "blocked")
                    self.assertEqual(audit["violations"], ["calc.py"])
                    self.assertNotIn("success", state["tasks"]["fix"]["evidence"])
                else:
                    parent = state["tasks"]["fix"]
                    self.assertEqual(parent["status"], "completed")
                    self.assertEqual(audit["violations"], [])
                    self.assertEqual(parent["producing_attempt"], author)
                    self.assertEqual(parent["snapshot_attempt"], review)
                    self.assertEqual(parent["evidence"]["success"]["attempt"], review)
                    controller.refresh(state, time.time())
                    self.assertTrue(parent["evidence"]["success"]["valid"])

    def test_owner_continues_after_review_scratch_and_retains_all_audit_inputs(self):
        self.initialize([self.worker()])
        author = self.begin("fix")
        self.finish(author, self.proposed())
        rejected_review = self.begin("fix.review.1")
        scratch = Path(self.state()["tasks"]["fix.review.1"]["scratch_directory"])
        (scratch / "counterexample.log").write_text("The singleton input still fails.\n")
        state = self.finish(rejected_review, self.proposed(failed=True, review=True))
        self.assertEqual(state["tasks"]["fix"]["producing_attempt"], author)
        owner_task = state["tasks"]["fix.strong.1"]
        self.assertEqual(owner_task["expected_workspace"], state["attempts"][rejected_review]["engineering_result"]["after_digest"])
        self.assertIn(scratch.name + "/", owner_task["audit_scope"])
        owner = self.begin("fix.strong.1")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        state = self.finish(owner, self.proposed())
        self.assertEqual(state["tasks"]["fix.strong.1"]["status"], "completed")
        self.assertEqual((scratch / "counterexample.log").read_text(), "The singleton input still fails.\n")
        review = self.begin("fix.review.2")
        state = self.finish(review, self.proposed(review=True))
        parent = state["tasks"]["fix"]
        self.assertEqual(parent["status"], "completed")
        self.assertEqual(parent["producing_attempt"], owner)
        self.assertEqual(parent["snapshot_attempt"], review)
        scratch_input = str((scratch / "counterexample.log").relative_to(Path(state["workspace"])))
        self.assertEqual(parent["evidence"]["success"]["inputs"][scratch_input], file_identity(scratch / "counterexample.log"))

    def test_original_dependency_digest_survives_repair_and_final_review(self):
        self.initialize([
            self.scout("diagnosis", priority=2),
            self.worker(depends_on=[{"task": "diagnosis", "evidence": "failure_reproduced"}]),
        ])
        diagnostic = self.begin("diagnosis")
        self.finish(diagnostic, {"outcome": "failure_reproduced", "findings": "Actual singleton input fails.",
                                 "evidence": ["synthetic failing command"]}, returncode=1)
        author = self.begin("fix")
        dependencies = copy.deepcopy(self.state()["attempts"][author]["dependencies"])
        self.assertEqual(len(dependencies), 1)
        self.finish(author, self.proposed(failed=True), returncode=1)
        self.assertEqual(self.state()["tasks"]["fix.worker.1"]["expected_dependencies"], dependencies)
        repair = self.begin("fix.worker.1")
        (self.task_repo("fix") / "calc.py").write_text("def total(values):\n    return sum(values)\n")
        self.finish(repair, self.proposed())
        self.assertEqual(self.state()["tasks"]["fix.review.1"]["expected_dependencies"], dependencies)
        review = self.begin("fix.review.1")
        state = self.finish(review, self.proposed(review=True))
        self.assertEqual(state["tasks"]["fix"]["evidence"]["success"]["dependencies"], dependencies)
        self.assertEqual(state["attempts"][repair]["dependencies"], dependencies)
        self.assertEqual(state["attempts"][review]["dependencies"], dependencies)
        state["tasks"]["diagnosis"]["evidence"]["failure_reproduced"]["result"]["findings"] = "Changed evidence from a different observation."
        controller.refresh(state, time.time())
        self.assertFalse(state["tasks"]["fix"]["evidence"]["success"]["valid"])
        self.assertEqual(state["tasks"]["fix"]["status"], "invalid")

    def test_repair_cannot_rebind_to_replaced_prerequisite_evidence(self):
        self.initialize([
            self.scout("diagnosis", priority=2),
            self.worker(depends_on=[{"task": "diagnosis", "evidence": "failure_reproduced"}]),
        ])
        diagnostic = self.begin("diagnosis")
        self.finish(diagnostic, {"outcome": "failure_reproduced", "findings": "Actual singleton input fails.",
                                 "evidence": ["synthetic failing command"]}, returncode=1)
        author = self.begin("fix")
        self.finish(author, self.proposed(failed=True), returncode=1)
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["tasks"]["diagnosis"]["evidence"]["failure_reproduced"]["result"]["findings"] = "Replacement observation."
        finally:
            store.close()
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
        finally:
            instance.close()
        state = self.state()
        self.assertEqual(state["tasks"]["fix.worker.1"]["status"], "invalid")
        self.assertIn("original prerequisite evidence changed", state["tasks"]["fix.worker.1"]["reason"])
        self.assertEqual(state["tasks"]["fix.worker.1"]["attempts"], [])
        self.assertNotIn("success", state["tasks"]["fix"]["evidence"])

    def observed_diagnostic(self, *, commands=True, extra_tasks=()):
        self.initialize([self.scout("observed", priority=2), *extra_tasks])
        aid = self.begin("observed")
        raw = {"outcome": "observed", "findings": "The actual singleton input produced zero; expected seven.",
               "evidence": ["synthetic command item synthetic-check"]}
        events = self.run / "operations" / aid / "backend-events.jsonl"
        events.write_text(json.dumps({"method": "item/completed", "params": {"item": {
            "type": "commandExecution", "id": "synthetic-check", "status": "completed", "exitCode": 1,
            "command": "python -B -m unittest", "aggregatedOutput": "expected 7, observed 0"}}}) + "\n")
        state = self.finish(aid, raw, commands=commands, returncode=1)
        return aid, raw, events, state

    def test_diagnostic_assessment_releases_exact_dependency_without_completion_credit(self):
        dependent = self.worker(depends_on=[{"task": "observed", "evidence": "failure_reproduced"}])
        unrelated = self.worker("other-hypothesis", depends_on=[{"task": "observed", "evidence": "hypothesis_rejected"}])
        aid, raw, events, before = self.observed_diagnostic(extra_tasks=[dependent, unrelated])
        original_evidence = copy.deepcopy(before["tasks"]["observed"]["evidence"])
        instance = controller.Controller(self.run)
        try:
            clock = before["created_at"] + 10
            summary_before = instance.summary(clock)
            self.assertIsNone(instance.claim(time.time()))
            reason = "The matched command output demonstrates the requested singleton failure, not merely source agreement."
            controller.assess_diagnostic(self.run, "observed", "failure_reproduced", reason)
            after = self.state()
            task = after["tasks"]["observed"]
            evidence = task["evidence"]["failure_reproduced"]
            self.assertEqual(task["outcome"], "observed")
            self.assertEqual(task["diagnostic_result"], raw)
            self.assertEqual(after["attempts"][aid]["agent_result"]["result"], raw)
            self.assertEqual(task["acceptance_status"], before["tasks"]["observed"]["acceptance_status"])
            self.assertNotIn("success", task["evidence"])
            for label, value in original_evidence.items():
                self.assertEqual(task["evidence"][label], value)
            self.assertEqual(evidence["category"], "diagnostic_assessment")
            self.assertTrue(evidence["historical"])
            self.assertEqual(evidence["attempt"], aid)
            self.assertEqual(evidence["inputs"], after["attempts"][aid]["produced_identity"])
            self.assertEqual(evidence["dependencies"], after["attempts"][aid]["dependencies"])
            self.assertEqual(evidence["assessment"]["outcome"], "failure_reproduced")
            self.assertEqual(evidence["assessment"]["reason"], reason)
            self.assertIn(str(events), json.dumps(evidence))
            summary_after = instance.summary(clock)
            for field in ("completed", "original_completed", "valid_passes", "valid_failures", "acceptance_stages_completed", "useful_results_per_second"):
                self.assertEqual(summary_after[field], summary_before[field], field)
            claim = instance.claim(time.time())
            self.assertIsNotNone(claim)
            self.assertEqual(claim[0]["id"], "fix")
            self.assertEqual(self.state()["tasks"]["other-hypothesis"]["status"], "blocked")
        finally:
            instance.close()

    def test_diagnostic_assessment_is_idempotent_and_conflicts_are_rejected(self):
        aid, raw, events, _ = self.observed_diagnostic()
        reason = "The observed command discriminates this failure."
        controller.assess_diagnostic(self.run, "observed", "failure_reproduced", reason)
        before = self.state()
        store = Store(self.run)
        try:
            before_events = store.events()
        finally:
            store.close()
        controller.assess_diagnostic(self.run, "observed", "failure_reproduced", reason)
        self.assertEqual(self.state(), before)
        store = Store(self.run)
        try:
            self.assertEqual(store.events(), before_events)
        finally:
            store.close()
        for outcome, changed_reason in (("hypothesis_rejected", reason), ("failure_reproduced", "Different justification")):
            with self.subTest(outcome=outcome, reason=changed_reason):
                with self.assertRaises(ValueError):
                    controller.assess_diagnostic(self.run, "observed", outcome, changed_reason)
                self.assertEqual(self.state(), before)

    def test_diagnostic_assessment_rejects_unverified_or_changed_evidence(self):
        for condition in ("no-command", "incomplete-command", "unreleased", "uningested", "held", "changed-copy", "expired"):
            with self.subTest(condition=condition):
                self.run = self.root / ("assessment-" + condition)
                aid, _, _, _ = self.observed_diagnostic(commands=condition != "no-command")
                store = Store(self.run)
                try:
                    with store.transaction() as (state, _):
                        attempt = state["attempts"][aid]
                        if condition == "incomplete-command":
                            attempt["engineering_result"]["commands"][0].update(completed=False, status="running", exitCode=None)
                        elif condition == "unreleased":
                            attempt["released"] = False
                        elif condition == "uningested":
                            attempt["ingested"] = False
                        elif condition == "held":
                            state["holds"]["observed"] = {"operation": aid, "category": "ownership", "notice": "unresolved"}
                        elif condition == "expired":
                            state["deadline"] = time.time() - 1
                finally:
                    store.close()
                if condition == "changed-copy":
                    (self.task_repo("observed") / "calc.py").write_text("def total(values):\n    return 999\n")
                before = self.state()
                with self.assertRaises(ValueError):
                    controller.assess_diagnostic(self.run, "observed", "failure_reproduced", "Attempt to classify insufficient evidence.")
                self.assertEqual(self.state(), before)
                self.assertNotIn("failure_reproduced", self.state()["tasks"]["observed"]["evidence"])

    def test_diagnostic_assessment_cannot_accept_worker_implementation(self):
        self.initialize([self.worker()])
        aid = self.begin("fix")
        self.finish(aid, self.proposed())
        before = self.state()
        with self.assertRaises(ValueError):
            controller.assess_diagnostic(self.run, "fix", "failure_reproduced", "This is not a diagnostic result.")
        self.assertEqual(self.state(), before)
        self.assertEqual(self.state()["tasks"]["fix"]["status"], "awaiting_acceptance")
        self.assertNotIn("success", self.state()["tasks"]["fix"]["evidence"])

    def test_assess_cli_preserves_pause_and_identical_replay_after_deadline(self):
        self.observed_diagnostic()
        controller.control(self.run, "pause", "user decision remains in force")
        args = ["--run", str(self.run), "assess", "--task", "observed", "--outcome", "hypothesis_rejected",
                "--reason", "The observed matched comparison rules out input coercion while retaining the original failure."]
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(controller.main(args), 0)
        self.assertEqual(json.loads(output.getvalue()), {"assessed": "observed", "outcome": "hypothesis_rejected"})
        self.assertEqual(self.state()["mode"], "paused")
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["deadline"] = time.time() - 1
        finally:
            store.close()
        previous = self.state()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(controller.main(args), 0)
        self.assertEqual(self.state(), previous, "idempotent replay may not reopen a completed assessment or reset time")


if __name__ == "__main__":
    unittest.main()
