"""Synthetic protocol tests; these do not establish live model integration."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agent_backend", ROOT / "agent_backend.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)

FAKE = r'''#!/usr/bin/env python3
import json, pathlib, sys
root = pathlib.Path(__file__).parent
mode = (root / "mode").read_text() if (root / "mode").exists() else "complete"
thread = "synthetic-thread"
turn = "synthetic-turn"
def emit(value):
    print(json.dumps(value), flush=True)
for line in sys.stdin:
    message = json.loads(line)
    method = message["method"]
    with (root / "calls").open("a") as f:
        f.write(method + "\n")
    identity = message.get("id")
    if method == "initialized":
        continue
    if method == "initialize":
        result = {"userAgent": "synthetic"}
    elif method == "config/read":
        result = {"config": {"mcp_servers": {"example": {"enabled": True}}}, "layers": []}
    elif method == "thread/start":
        p = message["params"]
        assert p["allowProviderModelFallback"] is False
        assert p["config"]['mcp_servers.example.enabled'] is False
        result = {"thread": {"id": thread, "environments": []}, "model": p["model"],
            "reasoningEffort": p["config"]["model_reasoning_effort"], "serviceTier": p["serviceTier"],
            "approvalPolicy": "never", "sandbox": {"type": "readOnly", "networkAccess": False}}
        if mode == "mismatch":
            result["model"] = "not-requested"
    elif method == "turn/start":
        emit({"id": identity, "result": {"turn": {"id": turn}}})
        if mode == "wait":
            continue
        item = {"type": "agentMessage", "text": '{"answer":42}'}
        if mode == "tool":
            item = {"type": "commandExecution", "command": "not actually run"}
        emit({"method": "item/completed", "params": {"threadId": thread, "turnId": turn, "item": item}})
        emit({"method": "thread/tokenUsage/updated", "params": {"threadId": thread, "tokenUsage": {"total": {"inputTokens": 10, "outputTokens": 5}}}})
        emit({"method": "turn/completed", "params": {"threadId": thread, "turn": {"id": turn, "status": "completed"}}})
        continue
    elif method == "turn/interrupt":
        emit({"id": identity, "result": {}})
        emit({"method": "turn/completed", "params": {"threadId": thread, "turn": {"id": turn, "status": "interrupted"}}})
        continue
    else:
        emit({"id": identity, "error": {"code": -32601, "message": method}})
        continue
    emit({"id": identity, "result": result})
'''


class AgentBackendTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.runtime = self.root / "fake-runtime"
        self.runtime.write_text(FAKE)
        self.runtime.chmod(0o700)
        self.directory = self.root / "operation"
        self.task = {"id": "reason", "cwd": str(self.root), "prompt": "Return an answer as JSON.", "timeout_seconds": 5}
        self.policy = {"model": "test-model", "effort": "medium", "service_tier": "default",
                       "codex_binary": str(self.runtime), "sandbox": "read-only", "approval": "never",
                       "network": False, "agent_profile": "read-only-no-exec"}

    def prepare(self):
        return backend.prepare(self.task, self.policy, self.directory)

    def run_fake(self, mode="complete"):
        (self.root / "mode").write_text(mode)
        spec = self.prepare()
        result = subprocess.run(spec["argv"], cwd=spec["cwd"], capture_output=True, text=True, timeout=10)
        return result, backend.collect(self.directory, {"state": "completed", "released": True, "returncode": result.returncode})

    def test_prepare_is_structured_idempotent_and_preserves_config(self):
        first = self.prepare()
        self.assertEqual(first, self.prepare())
        self.assertEqual(first["argv"][0], sys.executable)
        self.assertNotIn("--ignore-user-config", first["argv"])
        self.assertEqual(first["env"], {})
        self.task["prompt"] = "different input"
        with self.assertRaisesRegex(backend.BackendError, "identity reused"):
            self.prepare()

    def test_unsupported_boundaries_and_missing_settings_refused(self):
        changes = [{"model": ""}, {"effort": None}, {"service_tier": ""}, {"sandbox": "workspace-write"},
                   {"approval": "on-request"}, {"network": True}, {"agent_profile": "none"},
                   {"tools": "none"}, {"nested_delegation": True}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(backend.BackendError):
                backend.prepare(self.task, {**self.policy, **change}, self.directory)

    def test_known_connected_tools_disabled_across_layers(self):
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        params = backend._thread_params(request, {"config": {"mcp_servers": {"node_repl": {}}},
                                                  "layers": [{"config": {"mcp_servers": {"two-with-dash": {}}}}]})
        self.assertFalse(params["allowProviderModelFallback"])
        self.assertFalse(params["config"]["mcp_servers.node_repl.enabled"])
        self.assertFalse(params["config"]["mcp_servers.two-with-dash.enabled"])
        self.assertFalse(any('"' in key for key in params["config"]))
        self.assertFalse(params["config"]["features.multi_agent"])
        self.assertEqual(params["environments"], [])

    def test_unsafe_server_keys_refused_and_null_optional_layers_handled(self):
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        for name in ("two.with.dot", 'quoted"name', "space name"):
            with self.subTest(name=name), self.assertRaisesRegex(backend.BackendError, "safely addressed"):
                backend._thread_params(request, {"config": {"mcp_servers": {name: {}}}})
        params = backend._thread_params(request, {"config": None, "layers": None})
        self.assertFalse(params["config"]["features.multi_agent"])

    def test_synthetic_protocol_dispatch_observe_collect(self):
        process, result = self.run_fake()
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result"], {"answer": 42})
        self.assertEqual(result["thread_id"], "synthetic-thread")
        self.assertEqual(result["turn_id"], "synthetic-turn")
        self.assertEqual(result["effective"]["reasoningEffort"], "medium")
        self.assertEqual(result["usage"]["total"]["outputTokens"], 5)
        self.assertIn("not provider-side", result["effective"]["settings_evidence"])

    def test_mismatched_settings_hold_before_turn(self):
        process, result = self.run_fake("mismatch")
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(result["status"], "hold")
        self.assertIn("resolved model differs", result["detail"])
        self.assertNotIn("turn/start", (self.root / "calls").read_text())

    def test_unexpected_tool_activity_holds_result(self):
        process, result = self.run_fake("tool")
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(result["status"], "hold")
        self.assertIn("unexpected tool activity", result["detail"])

    def test_duplicate_internal_run_never_dispatches_twice(self):
        process, _ = self.run_fake()
        self.assertEqual(process.returncode, 0)
        calls = (self.root / "calls").read_text()
        spec = self.prepare()
        again = subprocess.run(spec["argv"], capture_output=True, text=True, timeout=5)
        self.assertEqual(again.returncode, 2)
        self.assertIn("already started", again.stderr)
        self.assertEqual(calls, (self.root / "calls").read_text())

    def test_cancelled_execution_cannot_accept_late_result(self):
        self.run_fake()
        before = (self.directory / "backend-result.json").read_bytes()
        result = backend.collect(self.directory, {"state": "cancelled", "released": True, "returncode": 0})
        self.assertEqual(result["status"], "hold")
        self.assertIsNone(result["result"])
        self.assertEqual(before, (self.directory / "backend-result.json").read_bytes())

    def test_unreleased_or_malformed_results_never_complete(self):
        self.prepare()
        self.assertEqual(backend.collect(self.directory, {"released": False})["status"], "hold")
        (self.directory / "backend-result.json").write_text('{"status":"completed","status":"hold"}')
        self.assertEqual(backend.collect(self.directory, {"released": True})["status"], "invalid")

    def test_protocol_interrupt_is_requested_and_preserved(self):
        (self.root / "mode").write_text("wait")
        spec = self.prepare()
        process = subprocess.Popen(spec["argv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            calls = (self.root / "calls").read_text() if (self.root / "calls").exists() else ""
            if "turn/start" in calls:
                break
            time.sleep(.02)
        else:
            self.fail("synthetic turn did not start")
        process.send_signal(signal.SIGTERM)
        _, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 1, stderr)
        self.assertIn("turn/interrupt", (self.root / "calls").read_text())
        result = json.loads((self.directory / "backend-result.json").read_text())
        self.assertEqual(result["status"], "hold")
        self.assertIn("interrupted", result["detail"])
        self.assertEqual(result["turn_id"], "synthetic-turn")


if __name__ == "__main__":
    unittest.main()
