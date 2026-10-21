"""Real owned subprocesses with a synthetic agent adapter; no model integration.

The adapter runs bounded Python programs in actual private Git copies and
classifies their recorded output. These tests establish process ownership,
controller replenishment and recovery, not app-server or model behavior.
"""
from __future__ import annotations

import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import controller
from controller_store import Store
import execution


class SwarmExecutionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="swarm-execution-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        (self.repo / "calc.py").write_text("def total(values):\n    return sum(values[1:])\n")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "calc.py"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Fixture",
                        "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath=/dev/null",
                        "commit", "-qm", "fixture baseline"], check=True, capture_output=True)
        self.run = self.root / "run"
        self.programs = {}
        self.launches = []
        self.known_processes = []
        for patcher in (
            mock.patch.object(controller, "runtime_identity", return_value={"fixture": "swarm-process-v1"}),
            mock.patch("agent_backend.prepare", side_effect=self.prepare),
            mock.patch("agent_backend.collect", side_effect=self.collect),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.stop_owned)

    def stop_owned(self):
        if (self.run / "state.sqlite3").exists():
            controller.control(self.run, "stop", "bounded test cleanup")
            directories = list((self.run / "operations").glob("*"))
            for directory in directories:
                execution.cancel(directory, "bounded test cleanup")
            end = time.monotonic() + 4
            while time.monotonic() < end:
                if all(execution.observe(path).get("released") or
                       execution.observe(path)["state"] == "uncertain" for path in directories):
                    break
                time.sleep(.02)
        # The lost-runner test retains exact start identities for its own cleanup.
        for identity in self.known_processes:
            if execution._alive(identity):
                execution._signal_owned(identity, signal.SIGKILL)
        end = time.monotonic() + 1
        while any(execution._alive(identity) for identity in self.known_processes) and time.monotonic() < end:
            time.sleep(.02)

    def task(self, name, **changes):
        return {"id": name, "role": "swarm", "cwd": str(self.repo),
                "prompt": "Run the bounded singleton experiment and report actual evidence.",
                "hypothesis": "total skips the first input",
                "experiment": "Compare total([7]) with the specified expected value 7.",
                "comparison": {"input": [7], "expected": 7, "environment": "disposable Python fixture"},
                "allowed_commands": ["Read calc.py and run the bounded Python singleton experiment"],
                "estimate_seconds": .05, **changes}

    def initialize(self, tasks):
        return controller.initialize(self.run, {
            "version": 1, "id": "swarm-process-fixture", "workspace": str(self.repo),
            "policy": {"capacity": {"reasoning": 1, "processes": 1, "cpu": 1, "memory_mb": 128},
                       "allowed_cwds": [str(self.repo)], "allowed_executables": [str(Path(sys.executable).resolve())],
                       "process_boundary": "inherited", "boundary_description": "Disposable real-process test; synthetic agent adapter.",
                       "network": False, "approval": "never", "sandbox": "workspace-write", "agent_profile": "engineering",
                       "model": "synthetic-no-model", "effort": "medium", "service_tier": "default",
                       "max_active_seconds": 120, "deadline_seconds": 120}, "tasks": tasks})

    def prepare(self, task, policy, directory):
        self.launches.append(task["id"])
        script = self.programs.get(task["id"],
            "import json; from calc import total; print(json.dumps({'actual': total([7]), 'expected': 7}), flush=True)")
        # Only generated scratch is used for writable markers; -B avoids pycache.
        return {"argv": [sys.executable, "-B", "-c", script, task["scratch_directory"]],
                "cwd": task["cwd"], "env": {}, "timeout_seconds": task["timeout_seconds"]}

    def collect(self, directory, observation):
        directory = Path(directory)
        stdout = (directory / "stdout").read_text() if (directory / "stdout").exists() else ""
        spec = json.loads((directory / "spec.json").read_text())
        command = {"id": "actual-owned-python", "command": spec["argv"], "cwd": spec["cwd"],
                   "completed": observation.get("state") == "completed", "exitCode": observation.get("returncode"),
                   "aggregatedOutput": stdout, "status": observation.get("state")}
        (directory / "backend-events.jsonl").write_text(json.dumps(command) + "\n")
        normal = observation.get("state") == "completed" and observation.get("returncode") == 0
        result = None
        if normal:
            comparison = json.loads(stdout)
            result = {"outcome": "failure_reproduced" if comparison["actual"] != comparison["expected"] else "hypothesis_rejected",
                      "findings": "Actual bounded subprocess output: " + stdout.strip(),
                      "evidence": [str(directory / "stdout")]}
        cutoff = observation.get("detail") == "execution timeout"
        return {"status": "completed" if normal else "cutoff" if cutoff else "hold", "result": result,
                "termination_kind": "budget_cutoff" if cutoff else "interrupted" if not normal else None,
                "commands": [command],
                "file_changes": [], "effective": {"adapter": "synthetic; no model call"},
                "detail": "Actual owned process receipt; synthetic diagnostic classification."}

    def state(self):
        store = Store(self.run)
        try:
            return store.read()
        finally:
            store.close()

    def execute(self, seconds=5):
        instance = controller.Controller(self.run)
        try:
            return instance.run(max_seconds=seconds)
        finally:
            instance.close()

    def wait_for(self, read, predicate, seconds=3):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            value = read()
            if predicate(value):
                return value
            time.sleep(.02)
        self.fail(f"bounded process condition was not reached: {value}")

    def test_timeout_waits_for_escaped_child_then_replenishes_without_coverage(self):
        child = ("import os,signal,sys,time; from pathlib import Path; os.setsid(); "
                 "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                 "Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(10)")
        self.programs["slow"] = (
            "import subprocess,sys,time; from pathlib import Path; "
            f"subprocess.Popen([sys.executable,'-B','-c',{child!r},str(Path(sys.argv[1])/'child-pid')]); "
            "print('slow experiment started',flush=True); time.sleep(10)")
        self.initialize([self.task("slow", timeout_seconds=.4, priority=10), self.task("next"),
                         self.task("needs-slow", depends_on=[{"task": "slow", "evidence": "result"}])])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            state = self.state()
            task = state["tasks"]["slow"]
            aid = task["attempts"][0]
            private = Path(task["cwd"])
            marker = Path(task["scratch_directory"]) / "child-pid"
            self.wait_for(marker.exists, bool)
            child_identity = execution._identity(int(marker.read_text()))
            self.known_processes.append(child_identity)
            directory = instance.operation_directory(aid)
            receipt = self.wait_for(lambda: execution.observe(directory),
                                    lambda value: value.get("cancellation_reason") == "execution timeout")
            self.assertFalse(receipt["released"])
            self.assertTrue(execution._alive(child_identity))
            instance.tick()
            held = self.state()
            self.assertFalse(held["attempts"][aid]["released"])
            self.assertTrue(private.exists(), "private bytes cannot be deleted while descendants own them")
            self.assertEqual(held["tasks"]["next"]["attempts"], [])
        finally:
            instance.close()
        summary = self.execute(seconds=4)
        state = self.state()
        slow = state["tasks"]["slow"]
        self.assertEqual(slow["outcome"], "inconclusive")
        self.assertNotIn("result", slow["evidence"])
        self.assertNotIn("success", slow["evidence"])
        self.assertFalse(execution._alive(child_identity))
        self.assertTrue(state["attempts"][aid]["released"])
        self.assertTrue(state["attempts"][aid]["ingested"])
        self.assertEqual(state["tasks"]["needs-slow"]["attempts"], [])
        self.assertEqual(state["tasks"]["next"]["status"], "completed")
        successor = state["attempts"][state["tasks"]["next"]["attempts"][0]]
        self.assertGreaterEqual(successor["claimed_at"], state["attempts"][aid]["finished_at"])
        self.assertEqual(self.launches, ["slow", "next"])
        self.assertFalse(private.exists(), "released swarm workspace should be cleaned automatically")
        self.assertTrue((directory / "engineering-after.json").is_file())
        self.assertTrue((directory / "backend-events.jsonl").is_file())
        self.assertEqual(summary["valid_passes"], 0)
        self.assertEqual(summary["valid_failures"], 0)
        self.assertEqual(summary["completed"], 1, "only the completed next experiment is useful work")
        self.assertFalse(summary["all_original_complete"])

    def test_stop_survives_recovery_and_only_explicit_resume_dispatches_pending_work(self):
        self.programs["active"] = (
            "import sys,time; from pathlib import Path; "
            "Path(sys.argv[1],'started').write_text('once'); print('active',flush=True); time.sleep(10)")
        self.initialize([self.task("active", timeout_seconds=15, priority=10), self.task("pending")])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            task = self.state()["tasks"]["active"]
            aid = task["attempts"][0]
            self.wait_for((Path(task["scratch_directory"]) / "started").exists, bool)
        finally:
            instance.close()
        controller.control(self.run, "stop", "explicit durable user stop")
        summary = self.execute()
        self.assertEqual(summary["mode"], "stopped")
        self.assertEqual(summary["active"], 0)
        self.assertEqual(self.state()["tasks"]["active"]["attempts"], [aid])
        self.assertEqual(self.state()["tasks"]["active"]["status"], "cancelled")
        self.assertEqual(self.state()["tasks"]["pending"]["attempts"], [])
        self.assertEqual(self.execute()["mode"], "stopped")
        self.assertEqual(self.launches, ["active"])
        self.assertEqual(summary["valid_passes"], 0)
        self.assertEqual(summary["valid_failures"], 0)
        controller.control(self.run, "resume")
        self.execute()
        self.assertEqual(self.launches, ["active", "pending"])
        self.assertEqual(self.state()["tasks"]["active"]["attempts"], [aid])
        self.assertEqual(self.state()["tasks"]["pending"]["status"], "completed")

    def test_lost_runner_preserves_workspace_ownership_hold_and_prevents_replacement(self):
        self.programs["uncertain"] = "import time; print('owned command alive',flush=True); time.sleep(10)"
        self.initialize([self.task("uncertain", timeout_seconds=15, priority=10), self.task("pending")])
        instance = controller.Controller(self.run)
        try:
            instance.tick()
            task = self.state()["tasks"]["uncertain"]
            aid = task["attempts"][0]
            directory = instance.operation_directory(aid)
            receipt = self.wait_for(lambda: execution.observe(directory), lambda value: "command" in value)
            self.known_processes.append(receipt["command"])
            self.assertTrue(execution._signal_owned(receipt["runner"], signal.SIGKILL))
            self.wait_for(lambda: execution.observe(directory), lambda value: value["state"] == "uncertain")
        finally:
            instance.close()
        recovered = controller.Controller(self.run)
        try:
            summary = recovered.tick()
            state = self.state()
            self.assertEqual(summary["active"], 1)
            self.assertEqual(state["holds"]["uncertain"]["category"], "ownership")
            self.assertFalse(state["attempts"][aid]["released"])
            self.assertTrue(Path(task["cwd"]).exists())
            self.assertTrue(execution._alive(receipt["command"]))
            self.assertEqual(state["tasks"]["pending"]["attempts"], [])
            self.assertEqual(self.launches, ["uncertain"])
            controller.control(self.run, "stop", "stop cannot infer lost execution release")
            self.assertEqual(recovered.tick()["mode"], "stopped")
            self.assertFalse(self.state()["attempts"][aid]["released"])
            self.assertIn("uncertain", self.state()["holds"])
        finally:
            recovered.close()


if __name__ == "__main__":
    unittest.main()
