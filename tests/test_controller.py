"""Controller acceptance tests: real processes, plus labeled synthetic history.

No model calls. Process tests exercise automatic dispatch/observation/replenishment;
history tests exercise the durable reducer without claiming live agent behavior.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import controller
from controller_store import Store, encoded


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="controller-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.run = self.root / "run"
        # Parallel development can legitimately alter source files. These tests
        # pin the runtime identity fixture, not the runtime being evaluated.
        self.runtime = mock.patch.object(controller, "runtime_identity", return_value={"fixture": "stable-runtime"})
        self.runtime.start()
        self.addCleanup(self.runtime.stop)
        self.addCleanup(self.stop_owned)

    def stop_owned(self):
        if not (self.run / "state.sqlite3").exists():
            return
        try:
            controller.control(self.run, "stop", "test cleanup")
            instance = controller.Controller(self.run)
            try:
                instance.run(max_seconds=4)
            finally:
                instance.close()
        except ValueError:
            # Schema preservation tests intentionally leave an unsupported
            # database, and they never launch execution.
            pass

    def task(self, name, code="pass", **fields):
        task = {"id": name, "kind": "process", "argv": [sys.executable, "-c", code],
                "estimate_seconds": 0.05, "timeout_seconds": 4,
                "acceptance": {"type": "exit", "success_codes": [0], "failure_codes": [],
                               "category": "test", "evidence": "check"}}
        task.update(fields)
        return task

    def inventory(self, tasks, slots=2, **policy):
        settings = {
            "capacity": {"reasoning": 2, "processes": slots, "cpu": slots, "memory_mb": 256},
            "allowed_cwds": [str(self.workspace)],
            "allowed_executables": [str(Path(sys.executable).resolve())],
            "process_boundary": "inherited",
            "boundary_description": "Disposable local fixture; inherits the test runner's OS restrictions.",
            "network": False, "sandbox": "read-only", "approval": "never",
            "max_active_seconds": 20, "deadline_seconds": 30,
        }
        settings.update(policy)
        return {"version": 1, "id": "fixture", "workspace": str(self.workspace),
                "policy": settings, "tasks": tasks}

    def initialize(self, tasks, slots=2, **policy):
        return controller.initialize(self.run, self.inventory(tasks, slots, **policy))

    def state(self):
        store = Store(self.run)
        try:
            return store.read()
        finally:
            store.close()

    def execute(self, max_seconds=8):
        instance = controller.Controller(self.run)
        try:
            return instance.run(max_seconds=max_seconds)
        finally:
            instance.close()

    def test_real_processes_replenish_dependency_chain_without_another_turn(self):
        self.initialize([
            self.task("first", "import time; time.sleep(0.08)"),
            self.task("second", depends_on=["first"]),
            self.task("third", depends_on=["second"]),
        ], slots=1)
        summary = self.execute()
        self.assertTrue(summary["all_original_complete"], summary)
        self.assertEqual(summary["valid_passes"], 3)
        state = self.state()
        first, second, third = [state["attempts"][state["tasks"][name]["attempts"][0]]
                                for name in ("first", "second", "third")]
        self.assertGreaterEqual(second["claimed_at"], first["finished_at"])
        self.assertGreaterEqual(third["claimed_at"], second["finished_at"])
        self.assertTrue(all(a["released"] and a["ingested"] for a in state["attempts"].values()))

    def test_valid_failure_releases_only_explicit_result_dependents(self):
        failed = self.task("failure", "raise SystemExit(7)")
        failed["acceptance"]["failure_codes"] = [7]
        self.initialize([
            failed,
            self.task("diagnosis", depends_on=[{"task": "failure", "evidence": "check"}]),
            self.task("needs-success", depends_on=["failure"]),
            self.task("unrelated"),
        ])
        summary = self.execute()
        self.assertEqual(summary["valid_failures"], 1)
        self.assertEqual(summary["valid_passes"], 2)
        self.assertFalse(summary["all_original_complete"])
        state = self.state()
        self.assertEqual(state["tasks"]["diagnosis"]["status"], "completed")
        self.assertEqual(state["tasks"]["needs-success"]["status"], "blocked")
        self.assertFalse(state["tasks"]["needs-success"]["attempts"])

    def test_setup_or_unclassified_exit_is_not_a_demonstrated_test_failure(self):
        self.initialize([self.task("setup", "raise SystemExit(2)")])
        summary = self.execute()
        self.assertEqual(summary["valid_failures"], 0)
        self.assertEqual(summary["completed"], 0)
        self.assertEqual(self.state()["tasks"]["setup"]["status"], "setup_error")

    def test_stdout_contract_reads_actual_executor_output(self):
        task = self.task("output", "print('expected')")
        task["acceptance"]["stdout_equals"] = "expected\n"
        self.initialize([task])
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 1, summary)

    def test_pause_survives_new_controller_and_requires_explicit_resume(self):
        self.initialize([self.task("pending")])
        self.assertEqual(controller.control(self.run, "pause"), "paused")
        summary = self.execute()
        self.assertEqual(summary["mode"], "paused")
        self.assertFalse(self.state()["attempts"])
        controller.control(self.run, "resume")
        self.assertEqual(self.execute()["valid_passes"], 1)

    def test_stop_cancels_owned_work_and_recovery_does_not_dispatch_successor(self):
        self.initialize([self.task("active", "import time; time.sleep(3)", priority=10),
                         self.task("pending")], slots=1)
        instance = controller.Controller(self.run)
        try:
            first = instance.tick()
            self.assertEqual(first["active"], 1)
        finally:
            instance.close()
        controller.control(self.run, "stop", "explicit user stop fixture")
        summary = self.execute()
        self.assertEqual(summary["mode"], "stopped")
        self.assertEqual(summary["active"], 0)
        state = self.state()
        self.assertFalse(state["tasks"]["pending"]["attempts"])
        self.assertEqual(state["tasks"]["active"]["status"], "cancelled")
        self.assertEqual(summary["valid_failures"], 0)
        self.assertEqual(self.execute()["mode"], "stopped")

    def test_stop_between_launch_intent_and_adapter_launch_prevents_command_side_effect(self):
        import execution
        marker = self.workspace / "must-not-exist.txt"
        self.initialize([self.task("race", "from pathlib import Path; Path('must-not-exist.txt').write_text('ran')")])
        original_launch = execution.launch
        invoked = []
        def stopped_launch(directory, spec):
            invoked.append(spec["operation_id"])
            controller.control(self.run, "stop", "stop after durable launch intent")
            return original_launch(directory, spec)
        with mock.patch("execution.launch", side_effect=stopped_launch):
            summary = self.execute()
        self.assertEqual(len(invoked), 1)
        self.assertEqual(summary["mode"], "stopped")
        self.assertEqual(summary["active"], 0)
        self.assertFalse(marker.exists(), "command launched after stop was persisted")
        self.assertEqual(summary["valid_passes"], 0)
        self.assertEqual(summary["valid_failures"], 0)

    def test_recovery_observes_surviving_attempt_without_duplicate_launch(self):
        self.initialize([self.task("surviving", "import time; time.sleep(0.2)")], slots=1)
        instance = controller.Controller(self.run)
        try:
            instance.tick()
        finally:
            instance.close()
        original = self.state()["tasks"]["surviving"]["attempts"][:]
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 1)
        self.assertEqual(self.state()["tasks"]["surviving"]["attempts"], original)

    def test_launch_acknowledgment_loss_reconciles_the_original_operation(self):
        self.initialize([self.task("ack-loss", "import time; time.sleep(0.15)")])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            with instance.store.transaction() as (state, _):
                attempt = next(iter(state["attempts"].values()))
                attempt.pop("launch_observation", None)
                original = attempt["id"]
        finally:
            instance.close()
        self.assertEqual(self.execute()["valid_passes"], 1)
        self.assertEqual(self.state()["tasks"]["ack-loss"]["attempts"], [original])

    def test_claim_before_launch_is_recovered_without_counting_false_result(self):
        self.initialize([self.task("unlaunched")])
        instance = controller.Controller(self.run)
        try:
            task, attempt, _ = instance.claim(time.time())
        finally:
            instance.close()
        summary = self.execute()
        state = self.state()
        self.assertTrue(state["attempts"][attempt["id"]]["released"])
        self.assertEqual(len(state["tasks"][task["id"]]["attempts"]), 2)
        self.assertEqual(summary["valid_passes"], 1)

    def test_concurrent_controller_authority_is_rejected(self):
        self.initialize([self.task("pending")])
        with controller.authority(self.run):
            with self.assertRaisesRegex(ValueError, "another controller"):
                self.execute(max_seconds=0.01)
        self.assertFalse(self.state()["attempts"])

    def test_exclusive_output_serializes_only_conflicting_tasks(self):
        self.initialize([
            self.task("writer-a", "import time; time.sleep(0.15)", outputs=["shared.out"], priority=3),
            self.task("writer-b", outputs=["shared.out"], priority=2),
            self.task("independent", "import time; time.sleep(0.05)", priority=1),
        ], slots=2)
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 3, summary)
        state = self.state()
        attempts = {name: state["attempts"][task["attempts"][0]] for name, task in state["tasks"].items()}
        self.assertGreaterEqual(attempts["writer-b"]["claimed_at"], attempts["writer-a"]["finished_at"])
        self.assertLess(attempts["independent"]["claimed_at"], attempts["writer-a"]["finished_at"])

    def test_timer_reconsiders_deferred_work_without_a_worker_completion(self):
        eligible_at = time.time() + 0.15
        self.initialize([self.task("timer", not_before=eligible_at)])
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 1)
        attempt = next(iter(self.state()["attempts"].values()))
        self.assertGreaterEqual(attempt["claimed_at"], eligible_at)

    def preemption_exercise(self, preemption):
        """Real owned processes; late ready work arrives while one slot is held."""
        code = ("from pathlib import Path; import time; "
                "Path('slow-started.txt').write_text('started'); time.sleep(0.4); "
                "p=Path('slow-completions.txt'); "
                "p.write_text((p.read_text() if p.exists() else '') + 'done\\n')")
        self.initialize([
            self.task("slow", code, estimate_seconds=5, quantum_seconds=0.03,
                      initial_quantum_seconds=0.03, preemption=preemption,
                      restart_safe=preemption == "restart",
                      outputs=["slow-started.txt", "slow-completions.txt"]),
        ], slots=1, minimum_service_seconds=0.03, minimum_gain_seconds=0,
            discovery_seconds=0.03, max_quantum_seconds=2, deferral_seconds=0)
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            deadline = time.monotonic() + 2
            while not (self.workspace / "slow-started.txt").exists() and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertTrue((self.workspace / "slow-started.txt").exists())
            controller.submit(self.run, [self.task("fast", "import time; time.sleep(0.02)", estimate_seconds=0.02)])
            summary = instance.run(max_seconds=8)
            return summary, instance.store.read(), instance.store.events()
        finally:
            instance.close()

    def test_real_preemption_releases_before_fast_dispatch_then_finishes_slow_once(self):
        summary, state, events = self.preemption_exercise("restart")
        self.assertTrue(summary["all_original_complete"], summary)
        slow = state["tasks"]["slow"]
        self.assertEqual(slow["preemptions"], 1)
        self.assertGreater(slow["quantum_seconds"], 0.03)
        self.assertEqual(len(slow["attempts"]), 2)
        interrupted, successful = [state["attempts"][aid] for aid in slow["attempts"]]
        fast = state["attempts"][state["tasks"]["fast"]["attempts"][0]]
        self.assertEqual(interrupted["observation"]["state"], "cancelled")
        self.assertTrue(interrupted["released"])
        self.assertEqual(interrupted["cancel_reason"], "quantum")
        self.assertGreaterEqual(fast["claimed_at"], interrupted["finished_at"])
        self.assertGreaterEqual(successful["claimed_at"], fast["finished_at"])
        self.assertEqual(successful["observation"]["state"], "completed")
        self.assertEqual((self.workspace / "slow-completions.txt").read_text(), "done\n")
        self.assertEqual(summary["valid_passes"], 2)
        self.assertEqual(summary["valid_failures"], 0)
        self.assertEqual(sum(e["kind"] == "observed_result" and e["data"]["observation"]["state"] == "cancelled" for e in events), 1)
        self.assertGreaterEqual(slow["service_seconds"], interrupted["service_seconds"] + successful["service_seconds"])

    def test_real_nonpreemptible_work_finishes_before_fast_replacement(self):
        summary, state, events = self.preemption_exercise("never")
        self.assertTrue(summary["all_original_complete"], summary)
        slow = state["tasks"]["slow"]
        self.assertEqual(slow["preemptions"], 0)
        self.assertEqual(len(slow["attempts"]), 1)
        slow_attempt = state["attempts"][slow["attempts"][0]]
        fast_attempt = state["attempts"][state["tasks"]["fast"]["attempts"][0]]
        self.assertGreaterEqual(fast_attempt["claimed_at"], slow_attempt["finished_at"])
        self.assertEqual((self.workspace / "slow-completions.txt").read_text(), "done\n")
        self.assertFalse(any(e["kind"] == "cancel_requested" for e in events))

    def test_worker_submission_uses_same_admission_and_cannot_spawn_hidden_capacity(self):
        self.initialize([self.task("parent", "import time; time.sleep(0.2)")], slots=1)
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            attempt = self.state()["tasks"]["parent"]["attempts"][0]
            controller.submit(self.run, [self.task("child")], parent_attempt=attempt)
            instance.tick()
            state = self.state()
            self.assertEqual(state["tasks"]["child"]["origin"], "followup")
            self.assertFalse(state["tasks"]["child"]["attempts"])
            with self.assertRaisesRegex(ValueError, "cannot hide"):
                controller.submit(self.run, [self.task("hidden", resources={"processes": 0})], parent_attempt=attempt)
        finally:
            instance.close()
        self.assertEqual(self.execute()["valid_passes"], 2)
        with self.assertRaisesRegex(ValueError, "active attempt"):
            controller.submit(self.run, [self.task("late-child")], parent_attempt=attempt)

    def test_drain_finishes_active_work_without_claiming_pending_work(self):
        self.initialize([self.task("active", "import time; time.sleep(0.12)", priority=10),
                         self.task("pending")], slots=1)
        instance = controller.Controller(self.run)
        try:
            instance.tick()
        finally:
            instance.close()
        controller.control(self.run, "drain")
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 1)
        self.assertEqual(summary["mode"], "draining")
        self.assertFalse(self.state()["tasks"]["pending"]["attempts"])

    def test_input_change_during_attempt_invalidates_only_that_result(self):
        (self.workspace / "input.txt").write_text("before")
        self.initialize([
            self.task("changing", "from pathlib import Path; Path('input.txt').write_text('after')", inputs=["input.txt"]),
            self.task("unrelated"),
        ])
        summary = self.execute()
        self.assertEqual(summary["valid_passes"], 1)
        self.assertEqual(self.state()["tasks"]["changing"]["acceptance_status"], "invalid")
        self.assertFalse(self.state()["tasks"]["changing"]["evidence"])

    def test_later_input_change_cannot_release_new_dependent_from_stale_evidence(self):
        path = self.workspace / "input.txt"
        path.write_text("before")
        self.initialize([self.task("checked", inputs=["input.txt"]), self.task("unrelated")])
        self.assertEqual(self.execute()["valid_passes"], 2)
        path.write_text("after")
        controller.submit(self.run, [self.task("dependent", depends_on=["checked"])])
        self.execute()
        state = self.state()
        self.assertFalse(state["tasks"]["dependent"]["attempts"], "stale prerequisite evidence launched dependent")
        self.assertTrue(state["tasks"]["unrelated"]["evidence"]["success"]["valid"])

    def test_partial_artifact_releases_only_its_dependents_and_retains_producer_slot(self):
        self.initialize([
            self.task("producer", "from pathlib import Path; import time; Path('chunk.txt').write_text('usable'); time.sleep(0.8)",
                      outputs=["chunk.txt"], partials={"chunk": {"path": "chunk.txt", "text": "usable"}}, priority=2),
            self.task("partial-consumer", depends_on=[{"task": "producer", "evidence": "chunk"}]),
            self.task("final-consumer", depends_on=["producer"]),
        ], slots=2)
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            aid = self.state()["tasks"]["producer"]["attempts"][0]
            limit = time.monotonic() + 2
            while not (self.workspace / "chunk.txt").exists() and time.monotonic() < limit:
                time.sleep(0.01)
            self.assertTrue((self.workspace / "chunk.txt").exists())
            with self.assertRaisesRegex(ValueError, "predeclared"):
                controller.publish(self.run, "producer", aid, "not-declared")
            with self.assertRaisesRegex(ValueError, "stale"):
                controller.publish(self.run, "producer", "wrong-attempt", "chunk")
            controller.publish(self.run, "producer", aid, "chunk")
            controller.publish(self.run, "producer", aid, "chunk")
            state = self.state()
            self.assertFalse(state["attempts"][aid]["released"])
            self.assertEqual(controller.usage(state)[0]["processes"], 1)
            instance.tick()
            state = self.state()
            self.assertTrue(state["tasks"]["partial-consumer"]["attempts"])
            self.assertFalse(state["tasks"]["final-consumer"]["attempts"])
            self.assertFalse(state["attempts"][aid]["released"])
            self.assertEqual(controller.usage(state)[0]["processes"], 2)
            self.assertEqual(sum(e["kind"] == "partial" for e in instance.store.events()), 1)
        finally:
            instance.close()
        self.assertEqual(self.execute()["valid_passes"], 3)

    def test_partial_requires_matching_content_owned_output_and_unchanged_inputs(self):
        (self.workspace / "source.txt").write_text("before")
        self.initialize([self.task("producer", "import time; time.sleep(0.5)",
                                  inputs=["source.txt"], outputs=["chunk.txt"],
                                  partials={"chunk": {"path": "chunk.txt", "text": "usable"},
                                            "unowned": {"path": "other.txt", "text": "usable"}})])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            aid = self.state()["tasks"]["producer"]["attempts"][0]
            (self.workspace / "chunk.txt").write_text("wrong")
            with self.assertRaisesRegex(ValueError, "content contract"):
                controller.publish(self.run, "producer", aid, "chunk")
            (self.workspace / "other.txt").write_text("usable")
            with self.assertRaisesRegex(ValueError, "owned output"):
                controller.publish(self.run, "producer", aid, "unowned")
            (self.workspace / "chunk.txt").write_text("usable")
            (self.workspace / "source.txt").write_text("changed")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                controller.publish(self.run, "producer", aid, "chunk")
            self.assertFalse(self.state()["tasks"]["producer"]["evidence"])
        finally:
            instance.close()

    def test_input_invalidation_propagates_through_only_its_evidence_chain(self):
        source = self.workspace / "source.txt"
        source.write_text("before")
        self.initialize([
            self.task("a", inputs=["source.txt"]),
            self.task("b", depends_on=["a"]),
            self.task("c", depends_on=["b"]),
            self.task("unrelated"),
        ])
        self.assertEqual(self.execute()["valid_passes"], 4)
        source.write_text("after")
        instance = controller.Controller(self.run)
        try:
            instance.tick()
        finally:
            instance.close()
        state = self.state()
        for name in ("a", "b", "c"):
            self.assertEqual(state["tasks"][name]["acceptance_status"], "invalid", name)
            self.assertFalse(state["tasks"][name]["evidence"]["success"]["valid"], name)
            self.assertEqual(len(state["tasks"][name]["attempts"]), 1, "invalidation must preserve original evidence")
        self.assertEqual(state["tasks"]["unrelated"]["status"], "completed")

    def test_hold_resolution_requires_same_released_operation_and_preserves_stop(self):
        self.initialize([self.task("held", "import time; time.sleep(0.2)")])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            with instance.store.transaction() as (state, _):
                aid = state["tasks"]["held"]["attempts"][0]
                hold = {"category": "setup", "operation": aid, "notice": "exact original notice", "at": time.time()}
                state["holds"]["held"] = hold
                state["tasks"]["held"].update(status="blocked", reason="held fixture")
            with self.assertRaisesRegex(ValueError, "match the held operation"):
                controller.resolve(self.run, "held", "wrong-operation", {"evidence": ["resolution.log"]})
            with self.assertRaisesRegex(ValueError, "resolution evidence"):
                controller.resolve(self.run, "held", aid, {"evidence": []})
            with self.assertRaisesRegex(ValueError, "verifiably released"):
                controller.resolve(self.run, "held", aid, {"evidence": ["resolution.log"]})
        finally:
            instance.close()
        controller.control(self.run, "stop", "preserve explicit stop")
        self.execute()
        before = self.state()
        self.assertTrue(before["attempts"][aid]["released"])
        controller.resolve(self.run, "held", aid, {"evidence": ["resolution.log"]})
        state = self.state()
        self.assertEqual(state["mode"], "stopped")
        self.assertEqual(state["stop_reason"], "preserve explicit stop")
        self.assertNotIn("held", state["holds"])
        self.assertEqual(state["tasks"]["held"]["hold_history"][0]["hold"], hold)
        self.assertEqual(state["tasks"]["held"]["service_seconds"], before["tasks"]["held"]["service_seconds"])
        self.execute()
        self.assertEqual(len(self.state()["tasks"]["held"]["attempts"]), 1)

    def test_runtime_migration_requires_quiescence_and_does_not_resume(self):
        self.initialize([self.task("active", "import time; time.sleep(0.2)")])
        with mock.patch.object(controller, "runtime_identity", return_value={"fixture": "reviewed-upgrade"}):
            with self.assertRaisesRegex(ValueError, "pause or drain"):
                controller.migrate(self.run, "reviewed upgrade")
        instance = controller.Controller(self.run)
        try:
            instance.tick()
        finally:
            instance.close()
        controller.control(self.run, "pause")
        with mock.patch.object(controller, "runtime_identity", return_value={"fixture": "reviewed-upgrade"}):
            with self.assertRaisesRegex(ValueError, "active execution"):
                controller.migrate(self.run, "reviewed upgrade")
        self.execute()
        before = self.state()["tasks"]["active"]["attempts"][:]
        with mock.patch.object(controller, "runtime_identity", return_value={"fixture": "reviewed-upgrade"}):
            with self.assertRaisesRegex(ValueError, "review reason"):
                controller.migrate(self.run, "")
            controller.migrate(self.run, "reviewed upgrade")
            state = self.state()
            self.assertEqual(state["runtime_identity"], {"fixture": "reviewed-upgrade"})
            self.assertEqual(state["mode"], "paused")
            self.assertEqual(state["tasks"]["active"]["attempts"], before)

    def test_task_budget_is_cumulative_across_resolved_attempts(self):
        # Synthetic consumed service is a replayed historical observation. The
        # second claim must reserve only the remainder, not a fresh task budget.
        self.initialize([self.task("bounded", "import time; time.sleep(1)", active_budget_seconds=0.2)])
        instance = controller.Controller(self.run)
        try:
            with instance.store.transaction() as (state, _):
                task = state["tasks"]["bounded"]
                task["service_seconds"] = 0.15
                state["active_service_seconds"] = 0.15
                old = {"id": "bounded-original", "task": "bounded", "released": True, "ingested": True,
                       "service_seconds": 0.15, "input_identity": {}, "configuration_identity": "original"}
                state["attempts"][old["id"]] = old
                task["attempts"] = [old["id"]]
                task["status"] = "blocked"
                state["holds"]["bounded"] = {"operation": old["id"], "category": "setup", "notice": "retained"}
            controller.resolve(self.run, "bounded", "bounded-original", {"evidence": ["resolved.log"]})
            claim = instance.claim(time.time())
            self.assertIsNotNone(claim)
            _, attempt, _ = claim
            self.assertLessEqual(attempt["service_budget_reserved"], 0.051)
            instance.dispatch(claim)
        finally:
            instance.close()
        summary = self.execute()
        self.assertEqual(summary["valid_failures"], 0)
        state = self.state()
        self.assertEqual(len(state["tasks"]["bounded"]["attempts"]), 2)
        self.assertGreaterEqual(state["tasks"]["bounded"]["service_seconds"], 0.2)
        # A new authorized resolution cannot reset consumed service either.
        instance = controller.Controller(self.run)
        try:
            with instance.store.transaction() as (state, _):
                state["tasks"]["bounded"]["status"] = "pending"
            self.assertIsNone(instance.claim(time.time()))
            self.assertEqual(instance.store.read()["tasks"]["bounded"]["status"], "deadline")
        finally:
            instance.close()

    def test_submissions_deduplicate_and_keep_authorization_and_graph_checks(self):
        self.initialize([])
        spec = self.task("incremental")
        controller.submit(self.run, [copy.deepcopy(spec)])
        controller.submit(self.run, [copy.deepcopy(spec)])
        self.assertEqual(len(self.state()["tasks"]), 1)
        changed = copy.deepcopy(spec)
        changed["argv"][-1] = "raise SystemExit(1)"
        with self.assertRaisesRegex(ValueError, "different input"):
            controller.submit(self.run, [changed])
        with self.assertRaisesRegex(ValueError, "outside authorized"):
            controller.submit(self.run, [self.task("outside", cwd=str(self.root))])
        with self.assertRaisesRegex(ValueError, "missing dependency"):
            controller.submit(self.run, [self.task("missing", depends_on=["absent"])])
        self.assertEqual(set(self.state()["tasks"]), {"incremental"})

    def test_missing_dependency_and_cycle_fail_before_creating_run(self):
        with self.assertRaisesRegex(ValueError, "missing dependency"):
            self.initialize([self.task("a", depends_on=["missing"])])
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            self.initialize([self.task("a", depends_on=["b"]), self.task("b", depends_on=["a"])])
        self.assertFalse((self.run / "state.sqlite3").exists())

    def test_hard_service_budget_stops_execution_and_cannot_be_resumed(self):
        self.initialize([self.task("long", "import time; time.sleep(3)")], max_active_seconds=0.08)
        summary = self.execute()
        self.assertEqual(summary["mode"], "stopped")
        self.assertEqual(summary["active"], 0)
        self.assertEqual(summary["valid_failures"], 0)
        self.assertIn("budget", summary["stop_reason"])
        with self.assertRaisesRegex(ValueError, "budget exhausted"):
            controller.control(self.run, "resume")

    def test_schema_migration_preserves_original_history_and_unknown_version(self):
        self.initialize([])
        store = Store(self.run)
        try:
            original = "original exact evidence\n  retained"
            with store.transaction() as (state, emit):
                state["schema"] = 1
                state.pop("holds")
                state.pop("observations")
                emit("historical", {"payload_text": original}, operation="historic-1")
            before = store.events()
            with store.transaction() as (state, _):
                self.assertEqual(state["schema"], 2)
                self.assertEqual(state["holds"], {})
            self.assertEqual(store.events(), before)
            with store.transaction() as (state, _):
                state["schema"] = 99
            data = store.connection.execute("SELECT value FROM snapshot").fetchone()[0]
            with self.assertRaisesRegex(ValueError, "unsupported"):
                with store.transaction():
                    pass
            self.assertEqual(store.connection.execute("SELECT value FROM snapshot").fetchone()[0], data)
        finally:
            store.close()

    def test_event_idempotency_and_conflicting_operation_roll_back_atomically(self):
        self.initialize([])
        store = Store(self.run)
        try:
            with store.transaction() as (_, emit):
                self.assertTrue(emit("result", {"value": 1}, operation="stable"))
                self.assertFalse(emit("result", {"value": 1}, operation="stable"))
            before = store.read()
            with self.assertRaisesRegex(ValueError, "identity reused"):
                with store.transaction() as (state, emit):
                    state["mode"] = "stopped"
                    emit("result", {"value": 2}, operation="stable")
            self.assertEqual(store.read(), before)
            self.assertEqual(sum(e["operation"] == "stable" for e in store.events()), 1)
        finally:
            store.close()

    def helper_fixture(self):
        """Synthetic worker reports test reducer integration, not model quality."""
        packet = {"baseline": "synthetic baseline", "scope": ["fixture.py"], "contracts": [],
                  "decisions": [], "acceptance_checks": ["unit"], "allowed_commands": ["python -m unittest"],
                  "budget": {"seconds": 60, "max_worker_results": 2}, "stop_conditions": ["ambiguous contract"]}
        (self.workspace / "fixture.py").write_text("def answer():\n    return 42\n")
        task = {"id": "patch", "kind": "agent", "prompt": "synthetic, never dispatched", "outputs": ["fixture.py"],
                "acceptance": {"type": "helper", "packet": packet}}
        self.initialize([task], model="fixture-model", effort="medium", service_tier="default")
        now = time.time()
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                task = state["tasks"]["patch"]
                controller.helper_event(task, "open", "supervisor", packet, now)
                attempt = {"id": "worker-1", "task": "patch", "input_identity": {}, "configuration_identity": "fixture",
                           "released": True, "ingested": True}
                state["attempts"]["worker-1"] = attempt
                task["attempts"] = ["worker-1"]
                task["status"] = "awaiting_acceptance"
        finally:
            store.close()
        return {"status": "completed", "changed_paths": ["fixture.py"],
                "checks": {"passed": ["unit"], "failed": [], "unexecuted": []}, "evidence": ["fixture.log"]}

    def automatic_helper_fixture(self, *, repair=False, material=True, mutate_review=False):
        """Mocked model reports with actual controller/process execution.

        These reports establish scheduling/reducer integration only. They are
        deliberately not live model integration or an engineering quality test.
        """
        packet = {"baseline": "synthetic baseline", "scope": ["fixture.py"], "contracts": [],
                  "decisions": [], "acceptance_checks": ["unit"], "allowed_commands": ["python -m unittest"],
                  "budget": {"seconds": 60, "max_worker_results": 2}, "stop_conditions": ["ambiguous contract"]}
        if material:
            (self.workspace / "fixture.py").write_text("def answer():\n    return 42\n")
        task = {"id": "patch", "kind": "agent", "prompt": "Implement answer() returning the integer 42.",
                "outputs": ["fixture.py"],
                "timeout_seconds": 4,
                "continuations": {"review": "Independently review the bounded patch and evidence.",
                                  "worker": "Apply the one evidence-based bounded repair."},
                "acceptance": {"type": "helper", "packet": packet}}
        self.initialize([task, self.task("downstream", depends_on=["patch"])],
                        model="fixture-model", effort="medium", service_tier="default")
        passed = {"status": "completed", "changed_paths": ["fixture.py"],
                  "checks": {"passed": ["unit"], "failed": [], "unexecuted": []}, "evidence": ["fixture.log"]}
        failed = dict(passed, checks={"passed": [], "failed": ["unit"], "unexecuted": []},
                      new_evidence=["cause.log"])
        assignments = {}
        policies = []
        def prepare(task, policy, directory):
            assignments[Path(directory).name] = copy.deepcopy(task)
            policies.append(copy.deepcopy(policy))
            if mutate_review and task["acceptance"].get("kind") == "review":
                (self.workspace / "fixture.py").write_text("def answer():\n    return 7\n")
            return {"argv": [sys.executable, "-c", "pass"], "cwd": task["cwd"], "env": {}, "timeout_seconds": 4}
        def collect(directory, observation):
            task = assignments[Path(directory).name]
            if task["id"] == "patch":
                result = failed if repair else passed
            elif task["acceptance"]["kind"] == "review":
                result = dict(passed, verdict="accept")
            else:
                result = passed
            return {"status": "completed", "result": copy.deepcopy(result),
                    "effective": {"model": "fixture-model", "effort": "medium"},
                    "detail": "synthetic collector, not a live model"}
        with mock.patch("agent_backend.prepare", side_effect=prepare), mock.patch("agent_backend.collect", side_effect=collect):
            summary = self.execute(max_seconds=1 if not material or mutate_review else 8)
        return summary, self.state(), policies, failed

    def test_automatic_helper_review_replenishes_original_dependents_under_same_policy(self):
        summary, state, policies, _ = self.automatic_helper_fixture()
        self.assertTrue(summary["all_original_complete"], summary)
        self.assertEqual(summary["original_completed"], 2)
        self.assertEqual(summary["original_total"], 2)
        parent = state["tasks"]["patch"]
        self.assertEqual(parent["acceptance_status"], "done")
        self.assertEqual(len(parent["attempts"]), 1)
        self.assertEqual(set(state["tasks"]), {"patch", "patch.review.1", "downstream"})
        self.assertEqual(state["tasks"]["patch.review.1"]["origin"], "followup")
        self.assertTrue(state["tasks"]["patch.review.1"]["required_for_original"])
        review = state["tasks"]["patch.review.1"]
        self.assertIn("fixture.py", review["inputs"])
        self.assertIn("Implement answer() returning the integer 42.", review["prompt"])
        self.assertIn("return 42", review["prompt"])
        review_attempt = state["attempts"][review["attempts"][0]]
        self.assertIn("fixture.py", review_attempt["input_identity"])
        original_attempt = state["attempts"][parent["attempts"][0]]
        self.assertAlmostEqual(parent["service_seconds"], original_attempt["service_seconds"] + review_attempt["service_seconds"], places=6)
        events = parent["helper_events"]
        self.assertEqual([event["kind"] for event in events], ["open", "worker", "review"])
        self.assertNotEqual(events[1]["actor"], events[2]["actor"])
        self.assertEqual(len(policies), 2)
        self.assertTrue(all((p["model"], p["effort"], p["service_tier"]) == ("fixture-model", "medium", "default") for p in policies))
        self.assertEqual(summary["valid_passes"], 2, "administrative review must not inflate useful pass count")

    def test_automatic_repair_preserves_original_failure_deadline_and_repair_allowance(self):
        summary, state, policies, failed = self.automatic_helper_fixture(repair=True)
        self.assertTrue(summary["all_original_complete"], summary)
        parent = state["tasks"]["patch"]
        events = parent["helper_events"]
        self.assertEqual([event["kind"] for event in events], ["open", "worker", "worker", "review"])
        self.assertEqual(json.loads(events[1]["payload_text"]), failed)
        _, derived = controller.supervisor.derive(events, time.time())
        self.assertTrue(derived["repair_used"])
        self.assertEqual(derived["worker_results"], 2)
        self.assertEqual(derived["deadline"], events[0]["recorded_at"] + 60)
        self.assertNotIn(events[-1]["actor"], [e["actor"] for e in events if e["kind"] == "worker"])
        self.assertEqual(parent["continuation_counts"], {"worker": 1, "review": 1})
        self.assertEqual(summary["original_completed"], 2)
        self.assertEqual(len(policies), 3)
        self.assertEqual(summary["valid_passes"], 2, "repair/review stages are not extra accepted outcomes")
        all_parent_service = sum(a["service_seconds"] for a in state["attempts"].values()
                                 if a["task"] == "patch" or state["tasks"][a["task"]].get("budget_owner") == "patch")
        self.assertAlmostEqual(parent["service_seconds"], all_parent_service, places=6)

    def test_missing_review_material_preserves_report_and_release_without_acceptance(self):
        summary, state, policies, _ = self.automatic_helper_fixture(material=False)
        self.assertFalse(summary["all_original_complete"])
        parent = state["tasks"]["patch"]
        self.assertEqual(parent["status"], "awaiting_acceptance")
        self.assertIn("needs engineering decision", parent["reason"])
        self.assertIn("owned concrete review artifact", parent["reason"])
        self.assertEqual([e["kind"] for e in parent["helper_events"]], ["open", "worker"])
        self.assertEqual(json.loads(parent["helper_events"][1]["payload_text"])["changed_paths"], ["fixture.py"])
        attempt = state["attempts"][parent["attempts"][0]]
        self.assertTrue(attempt["released"])
        self.assertTrue(attempt["ingested"])
        self.assertEqual(summary["active"], 0)
        self.assertFalse(state["tasks"]["downstream"]["attempts"])
        self.assertEqual(len(policies), 1)
        self.assertNotIn("patch.review.1", state["tasks"])
        self.assertNotIn("success", parent["evidence"])

    def test_review_artifact_mutation_after_claim_cannot_accept_parent(self):
        summary, state, _, _ = self.automatic_helper_fixture(mutate_review=True)
        self.assertFalse(summary["all_original_complete"])
        self.assertEqual(state["tasks"]["patch.review.1"]["acceptance_status"], "invalid")
        self.assertNotIn("success", state["tasks"]["patch"]["evidence"])
        self.assertFalse(state["tasks"]["downstream"]["attempts"])

    def test_embedded_review_material_changed_before_claim_is_not_silently_rebound(self):
        result = self.helper_fixture()
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["tasks"]["patch"]["continuations"] = {"review": "Review the actual bounded artifact."}
        finally:
            store.close()
        controller.record(self.run, "patch", "worker", "worker-1", result)
        before = self.state()
        review = before["tasks"]["patch.review.1"]
        self.assertIn("return 42", review["prompt"])
        frozen_identity = copy.deepcopy(review["prompt_input_identity"])
        (self.workspace / "fixture.py").write_text("def answer():\n    return 7\n")
        instance = controller.Controller(self.run)
        try:
            self.assertIsNone(instance.claim(time.time()))
            state = instance.store.read()
        finally:
            instance.close()
        review = state["tasks"]["patch.review.1"]
        self.assertEqual(review["status"], "invalid")
        self.assertIn("prompt inputs changed", review["reason"])
        self.assertFalse(review["attempts"])
        self.assertEqual(review["prompt_input_identity"], frozen_identity)
        self.assertNotIn("success", state["tasks"]["patch"]["evidence"])

    def test_manual_review_cannot_bypass_existing_backend_hold(self):
        result = self.helper_fixture()
        controller.record(self.run, "patch", "worker", "worker-1", result)
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                state["holds"]["patch"] = {"category": "backend", "operation": "worker-1", "notice": "original service hold"}
            before = store.read()
        finally:
            store.close()
        with self.assertRaisesRegex(ValueError, "held assignment"):
            controller.record(self.run, "patch", "review", "reviewer-1", dict(result, verdict="accept"))
        state = self.state()
        self.assertEqual(state["holds"], before["holds"])
        self.assertEqual(state["tasks"]["patch"]["helper_events"], before["tasks"]["patch"]["helper_events"])
        self.assertNotIn("success", state["tasks"]["patch"]["evidence"])

    def test_helper_stage_reserves_only_remaining_original_assignment_budget(self):
        result = self.helper_fixture()
        store = Store(self.run)
        try:
            with store.transaction() as (state, _):
                parent = state["tasks"]["patch"]
                parent["continuations"] = {"review": "Review the actual bounded artifact."}
                parent["active_budget_seconds"] = 1
                parent["service_seconds"] = 0.95
                state["active_service_seconds"] = 0.95
        finally:
            store.close()
        controller.record(self.run, "patch", "worker", "worker-1", result)
        instance = controller.Controller(self.run)
        try:
            claim = instance.claim(time.time())
            self.assertIsNotNone(claim)
            task, attempt, _ = claim
            self.assertEqual(task["id"], "patch.review.1")
            self.assertEqual(task["budget_owner"], "patch")
            self.assertLessEqual(attempt["service_budget_reserved"], 0.051)
            self.assertGreater(attempt["service_budget_reserved"], 0)
            self.assertEqual(instance.store.read()["tasks"]["patch"]["service_seconds"], 0.95)
        finally:
            instance.close()

    def test_helper_worker_cannot_accept_own_patch_and_preserves_raw_records(self):
        result = self.helper_fixture()
        raw = json.dumps(result, indent=3) + "\n"
        controller.record(self.run, "patch", "worker", "worker-1", raw)
        state = self.state()
        self.assertEqual(state["tasks"]["patch"]["acceptance_status"], "review_required")
        self.assertEqual(state["tasks"]["patch"]["helper_events"][-1]["payload_text"], raw)
        review = dict(result, verdict="accept")
        with self.assertRaisesRegex(ValueError, "own assignment"):
            controller.record(self.run, "patch", "review", "worker-1", review)
        controller.record(self.run, "patch", "review", "reviewer-1", review)
        self.assertEqual(self.state()["tasks"]["patch"]["status"], "completed")

    def test_helper_original_failure_and_one_repair_survive_reopen(self):
        result = self.helper_fixture()
        failed = dict(result, checks={"passed": [], "failed": ["unit"], "unexecuted": []}, new_evidence=["cause.log"])
        raw = json.dumps(failed, indent=2) + "\n"
        controller.record(self.run, "patch", "worker", "worker-1", raw)
        self.assertEqual(self.state()["tasks"]["patch"]["acceptance_status"], "repair_allowed")
        controller.record(self.run, "patch", "worker", "worker-2", result)
        rejected = dict(result, verdict="substantive_reject")
        controller.record(self.run, "patch", "review", "reviewer-1", rejected)
        state = self.state()
        task = state["tasks"]["patch"]
        _, derived = controller.supervisor.derive(task["helper_events"], time.time())
        self.assertTrue(derived["repair_used"])
        self.assertEqual(derived["state"], "takeover")
        self.assertEqual(task["helper_events"][1]["payload_text"], raw)
        with self.assertRaisesRegex(ValueError, "budget exhausted|already stopped"):
            controller.record(self.run, "patch", "worker", "worker-3", result)


if __name__ == "__main__":
    unittest.main()
