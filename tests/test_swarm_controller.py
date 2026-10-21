"""Deterministic swarm admission/evidence/cleanup tests; no model calls."""
import json
from pathlib import Path
import shutil
import time
import unittest
from unittest import mock

import test_engineering_controller as fixtures
import controller
import engineering
from controller_store import Store


class SimulatedCrash(BaseException):
    pass


class SwarmControllerTests(unittest.TestCase):
    setUp = fixtures.EngineeringControllerTests.setUp
    repository = fixtures.EngineeringControllerTests.repository
    initialize = fixtures.EngineeringControllerTests.initialize
    state = fixtures.EngineeringControllerTests.state
    task_repo = fixtures.EngineeringControllerTests.task_repo
    begin = fixtures.EngineeringControllerTests.begin
    finish = fixtures.EngineeringControllerTests.finish
    worker = fixtures.EngineeringControllerTests.worker

    def swarm(self, **extra):
        packet = fixtures.EngineeringControllerTests.scout(self, "probe", role="swarm", **extra)
        packet.pop("timeout_seconds", None)
        return packet

    def cleanup(self):
        instance = controller.Controller(self.run)
        try:
            instance.cleanup_swarm()
            return instance.summary()
        finally:
            instance.close()

    def completed(self, outcome="observed"):
        self.initialize([self.swarm()])
        aid = self.begin("probe")
        task = self.state()["tasks"]["probe"]
        (Path(task["scratch_directory"]) / "wrapper.py").write_text("print('matched comparison')\n")
        self.finish(aid, {"outcome": outcome, "findings": "observed one matched result; cause remains uncertain", "evidence": ["synthetic command observation"]})
        return aid

    def test_compact_scope_budget_and_model_preserved(self):
        self.initialize([self.swarm(write_scope=[])], model="restricted-model", effort="medium", service_tier="default")
        task = self.state()["tasks"]["probe"]
        self.assertTrue(task["swarm"])
        self.assertEqual(task["role"], "scout")
        self.assertEqual(task["timeout_seconds"], 60)
        self.assertEqual(task["write_scope"], [Path(task["scratch_directory"]).name + "/"])
        instance = controller.Controller(self.run)
        try:
            _, _, policy = instance.claim(time.time())
        finally:
            instance.close()
        self.assertEqual([policy[k] for k in ("model", "effort", "service_tier")], ["restricted-model", "medium", "default"])
        self.assertIn("next discriminator", task["prompt"])

    def test_admission_rejects_non_scratch_and_missing_experiment(self):
        policy = {"sandbox": "workspace-write", "source_workspace": str(self.workspace), "allowed_sources": [str(self.workspace)]}
        for updates in ({"write_scope": ["calc.py"]}, {"experiment": None}, {"comparison": {}}, {"allowed_commands": []}, {"swarm": True}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                controller.prepare_engineering(self.swarm(**updates), policy, self.run / "workspaces")
        with self.assertRaisesRegex(ValueError, "workspace-write"):
            controller.prepare_engineering(self.swarm(), dict(policy, sandbox="read-only"), self.run / "workspaces")

    def test_default_budget_clamps_to_small_run(self):
        self.initialize([self.swarm()], deadline_seconds=10, max_active_seconds=12)
        self.assertEqual(self.state()["tasks"]["probe"]["timeout_seconds"], 10)

    def test_inconclusive_is_terminal_without_result_or_useful_coverage(self):
        self.initialize([self.swarm(), self.worker(depends_on=[{"task": "probe", "evidence": "result"}])])
        aid = self.begin("probe")
        self.finish(aid, {"outcome": "inconclusive", "findings": "No discriminator completed; next test is a matched singleton", "evidence": ["retained source"]})
        summary = self.cleanup()
        state = self.state()
        self.assertEqual(state["tasks"]["probe"]["status"], "unmapped")
        self.assertEqual(state["tasks"]["probe"]["evidence"], {})
        self.assertEqual(summary["completed"], 0)
        self.assertEqual(summary["useful_results_per_second"], 0)
        self.assertEqual(summary["inconclusive"], 1)
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
        finally:
            instance.close()

    def test_cleanup_preserves_source_and_supports_historical_assessment(self):
        original = engineering.snapshot(self.repo)["digest"]
        aid = self.completed()
        before = self.state()["tasks"]["probe"]
        self.cleanup()
        task = self.state()["tasks"]["probe"]
        self.assertEqual(task["cleanup"]["state"], "complete")
        self.assertFalse(Path(task["cwd"]).exists())
        self.assertEqual(engineering.snapshot(self.repo)["digest"], original)
        capsule = engineering.verify_capsule(task["cleanup"])
        after = json.loads((self.run / "operations" / aid / "engineering-after.json").read_text())
        self.assertIn(Path(before["scratch_directory"]).name + "/wrapper.py", after["contents"])
        self.assertIn("calc.py", after["contents"])
        self.assertFalse(capsule["full_replay_claimed"])
        controller.assess_diagnostic(self.run, "probe", "failure_reproduced", "The retained matched command demonstrates the contract mismatch")
        self.assertEqual(self.state()["tasks"]["probe"]["outcome"], "observed")
        self.assertEqual(len(self.state()["tasks"]["probe"]["attempts"]), 1)
        (self.run / "operations" / aid / "engineering-after.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            controller.assess_diagnostic(self.run, "probe", "failure_reproduced", "The retained matched command demonstrates the contract mismatch")

    def test_intent_crashes_resume_cleanup_without_experiment(self):
        for after_delete in (False, True):
            with self.subTest(after_delete=after_delete):
                # Use a new run for each crash boundary, preserving the fixture.
                self.run = self.root / ("run-after" if after_delete else "run-before")
                aid = self.completed()
                original_remove = engineering.remove_private_workspace
                def crash(*args):
                    if after_delete:
                        original_remove(*args)
                    raise SimulatedCrash()
                with mock.patch.object(engineering, "remove_private_workspace", side_effect=crash), self.assertRaises(SimulatedCrash):
                    self.cleanup()
                task = self.state()["tasks"]["probe"]
                self.assertEqual(task["cleanup"]["state"], "intent")
                self.assertEqual(Path(task["cwd"]).exists(), not after_delete)
                self.cleanup()
                task = self.state()["tasks"]["probe"]
                self.assertEqual(task["cleanup"]["state"], "complete")
                self.assertEqual(task["attempts"], [aid])

    def test_unreleased_or_held_work_keeps_workspace(self):
        aid = self.completed()
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["attempts"][aid]["released"] = False
            self.cleanup()
            self.assertTrue(self.task_repo("probe").exists())
            with store.transaction() as (state, _):
                state["attempts"][aid]["released"] = True
                state["holds"]["probe"] = {"category": "permission", "operation": aid, "notice": "denied"}
            self.cleanup()
            self.assertNotIn("cleanup", self.state()["tasks"]["probe"])
        finally:
            store.close()

    def test_symlink_replacement_refuses_deletion_and_does_not_retry(self):
        self.completed()
        path = self.task_repo("probe")
        retained = path.with_name("retained-original-copy")
        path.rename(retained)
        path.symlink_to(self.repo, target_is_directory=True)
        original = engineering.snapshot(self.repo)["digest"]
        self.cleanup()
        self.assertEqual(self.state()["tasks"]["probe"]["cleanup"]["state"], "failed")
        self.assertTrue(retained.exists())
        self.assertEqual(engineering.snapshot(self.repo)["digest"], original)
        with mock.patch.object(engineering, "remove_private_workspace", side_effect=AssertionError("failed cleanup retried")):
            self.cleanup()

    def test_missing_target_without_intent_is_not_success(self):
        self.completed()
        shutil.rmtree(self.task_repo("probe"))
        self.cleanup()
        self.assertEqual(self.state()["tasks"]["probe"]["cleanup"]["state"], "failed")

    def test_compiled_binary_omission_allows_cleanup_but_large_wrapper_kept(self):
        for binary in (True, False):
            with self.subTest(binary=binary):
                self.run = self.root / ("run-binary" if binary else "run-text")
                self.initialize([self.swarm()])
                aid = self.begin("probe")
                task = self.state()["tasks"]["probe"]
                path = Path(task["scratch_directory"]) / ("compiled" if binary else "wrapper.py")
                path.write_bytes((b"\0\xff" if binary else b"x=") * engineering.MAX_TEXT_BYTES)
                self.finish(aid, {"outcome": "observed", "findings": "fixture", "evidence": ["fixture"]})
                self.cleanup()
                task = self.state()["tasks"]["probe"]
                self.assertEqual(task["cleanup"]["state"], "complete" if binary else "failed")
                self.assertEqual(Path(task["cwd"]).exists(), not binary)

    def test_scope_violation_keeps_copy_and_original_unchanged(self):
        self.initialize([self.swarm()])
        aid = self.begin("probe")
        (self.task_repo("probe") / "calc.py").write_text("unauthorized baseline edit")
        self.finish(aid, {"outcome": "observed", "findings": "changed", "evidence": ["fixture"]})
        self.cleanup()
        self.assertEqual(self.state()["tasks"]["probe"]["status"], "blocked")
        self.assertNotIn("cleanup", self.state()["tasks"]["probe"])
        self.assertIn("sum(values[1:])", (self.repo / "calc.py").read_text())

    def test_permission_hold_does_not_become_timeout_and_cannot_retry(self):
        self.initialize([self.swarm()])
        aid = self.begin("probe")
        instance = controller.Controller(self.run)
        try:
            with instance.store.transaction() as (state, _):
                task, attempt = state["tasks"]["probe"], state["attempts"][aid]
                attempt.update(released=True, ingested=True)
                backend = {"status": "hold", "termination_kind": "error", "detail": "permission denied", "commands": [], "file_changes": []}
                with mock.patch("agent_backend.collect", return_value=backend):
                    controller.ingest_result(state, task, attempt, {"status": "cancelled", "detail": "execution timeout", "released": True}, instance.operation_directory(aid), time.time())
            instance.cleanup_swarm()
        finally:
            instance.close()
        self.assertEqual(self.state()["tasks"]["probe"]["status"], "blocked")
        self.assertEqual(self.state()["holds"]["probe"]["notice"], "permission denied")
        with self.assertRaisesRegex(ValueError, "single-attempt"):
            controller.resolve(self.run, "probe", aid, {"evidence": ["operator inspected"]})
        self.assertTrue(self.task_repo("probe").exists())

    def test_capsule_parses_only_the_bytes_it_verified(self):
        self.completed()
        self.cleanup()
        cleanup = self.state()["tasks"]["probe"]["cleanup"]
        # The former hash-then-Path.read_text implementation trusted replacement
        # bytes. Parsing now consumes exactly the bytes hashed from one fd.
        with mock.patch.object(Path, "read_text", return_value='{"evidence_files":{},"task":"replacement"}'):
            capsule = engineering.verify_capsule(cleanup)
        self.assertEqual(capsule["task"], "probe")


if __name__ == "__main__":
    unittest.main()
