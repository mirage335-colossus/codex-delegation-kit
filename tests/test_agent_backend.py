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
from unittest.mock import patch

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
thread_cwd = None
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
        thread_cwd = p["cwd"]
        assert p["allowProviderModelFallback"] is False
        assert p["config"]['mcp_servers.example.enabled'] is False
        sandbox = {"type": "readOnly", "networkAccess": False}
        if p["sandbox"] == "workspace-write":
            assert p["config"]["features.shell_tool"] is True
            assert p["config"]["features.unified_exec"] is True
            sandbox = {"type": "workspaceWrite", "writableRoots": [thread_cwd], "networkAccess": False,
                       "excludeSlashTmp": True, "excludeTmpdirEnvVar": True}
        result = {"thread": {"id": thread, "environments": p["environments"]}, "model": p["model"],
            "reasoningEffort": p["config"]["model_reasoning_effort"], "serviceTier": p["serviceTier"],
            "approvalPolicy": "never", "sandbox": sandbox, "cwd": thread_cwd,
            "runtimeWorkspaceRoots": p["runtimeWorkspaceRoots"]}
        if mode == "mismatch":
            result["model"] = "not-requested"
            result["unrelatedSecret"] = "synthetic-secret-must-not-be-persisted"
        if mode == "broader-roots":
            sandbox["writableRoots"].append("/tmp")
        if mode == "shared-tmp":
            sandbox["excludeSlashTmp"] = False
        if mode == "legacy-roots":
            result["runtimeWorkspaceRoots"] = []
            sandbox["writableRoots"] = []
        if mode == "foreign-runtime-roots":
            result["runtimeWorkspaceRoots"] = ["/tmp"]
        if mode == "foreign-environment":
            result["thread"]["environments"] = [{"environmentId":"remote", "cwd":thread_cwd, "runtimeWorkspaceRoots":[thread_cwd]}]
    elif method == "turn/start":
        emit({"id": identity, "result": {"turn": {"id": turn}}})
        if mode == "wait":
            continue
        if mode == "engineering":
            assert message["params"]["environments"] == [{"environmentId":"local", "cwd":thread_cwd, "runtimeWorkspaceRoots":[thread_cwd]}]
            assert message["params"]["sandboxPolicy"] == {"type": "workspaceWrite", "writableRoots": [thread_cwd],
                "networkAccess": False, "excludeSlashTmp": True, "excludeTmpdirEnvVar": True}
            command = {"type":"commandExecution", "id":"command-1", "command":"python3 -B test.py", "cwd":thread_cwd,
                "status":"inProgress", "processId":"pty-1", "exitCode":None, "aggregatedOutput":None}
            emit({"method":"item/started", "params":{"threadId":thread, "turnId":turn, "item":command}})
            command.update(status="completed", exitCode=0, aggregatedOutput="one actual synthetic assertion passed", durationMs=5)
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn, "item":command}})
            change = {"type":"fileChange", "id":"patch-1", "status":"completed", "changes":[{"path":"sample.py", "kind":{"type":"update"}, "diff":"synthetic patch"}]}
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn, "item":change}})
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

    def engineering(self, role="worker"):
        workspace = self.root / "repo"
        workspace.mkdir(exist_ok=True)
        source = self.root / "original"
        source.mkdir(exist_ok=True)
        self.policy.update(agent_profile="engineering", sandbox="workspace-write")
        self.task.update(cwd=str(workspace), role=role, allowed_commands=["Read source and run python3 -B test.py"],
                         write_scope=["sample.py"] if role in {"worker", "owner"} else [], source_repository=str(source))

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
        self.assertFalse(params["config"]["features.code_mode_host"])
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
        self.assertTrue(result["settings_verified"])

    def test_mismatched_settings_hold_before_turn(self):
        process, result = self.run_fake("mismatch")
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(result["status"], "hold")
        self.assertIn("resolved model differs", result["detail"])
        self.assertNotIn("turn/start", (self.root / "calls").read_text())
        self.assertFalse(result["settings_verified"])
        self.assertEqual(result["effective"], {})
        self.assertEqual(result["observed_settings"]["model"], "not-requested")
        self.assertEqual(result["observed_settings"]["reasoningEffort"], "medium")
        self.assertNotIn("synthetic-secret-must-not-be-persisted", (self.directory / "backend-result.json").read_text())

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

    def test_engineering_observes_commands_and_changes_without_model_acceptance(self):
        self.engineering()
        process, result = self.run_fake("engineering")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(result["configured"]["sandbox"], "workspace-write")
        self.assertEqual(result["effective"]["runtimeWorkspaceRoots"], [self.task["cwd"]])
        self.assertEqual(len(result["commands"]), 1)
        command = result["commands"][0]
        self.assertEqual(command["exitCode"], 0)
        self.assertEqual(command["aggregatedOutput"], "one actual synthetic assertion passed")
        self.assertTrue(command["completed"])
        self.assertEqual(command["processId"], "pty-1")
        self.assertEqual(result["file_changes"][0]["changes"][0]["path"], "sample.py")
        self.assertIn("controller validation", result["detail"])
        calls = (self.root / "calls").read_text()
        self.assertNotIn("thread/shellCommand", calls)

    def test_readonly_responsibilities_enable_shell_without_write_authority(self):
        for role in ("scout", "reviewer"):
            with self.subTest(role=role):
                self.engineering(role)
                directory = self.root / role
                backend.prepare(self.task, self.policy, directory)
                request = json.loads((directory / "backend-request.json").read_text())
                params = backend._thread_params(request, {"config": {}, "layers": []})
                self.assertEqual(request["sandbox"], "read-only")
                self.assertEqual(params["sandbox"], "read-only")
                self.assertTrue(params["config"]["features.shell_tool"])
                self.assertTrue(params["config"]["features.unified_exec"])
                self.assertTrue(params["config"]["features.code_mode_host"])
                self.assertFalse(params["config"]["features.code_mode"])
                self.assertFalse(params["config"]["features.multi_agent"])
                self.assertFalse(params["config"]["features.plugins"])
                self.assertEqual(backend._sandbox_policy(request), {"type": "readOnly", "networkAccess": False})

    def test_engineering_scope_and_permission_conflicts_refused(self):
        self.engineering()
        task, policy = self.task.copy(), self.policy.copy()
        invalid = [({"role": "reviewer"}, {}), ({"role": "unknown"}, {}),
                   ({"write_scope": []}, {}), ({"write_scope": ["../outside"]}, {}),
                   ({"write_scope": ["/tmp"]}, {}), ({"write_scope": [".git/config"]}, {}),
                   ({"allowed_commands": []}, {}), ({}, {"sandbox": "read-only"}),
                   ({"source_repository": None}, {}), ({"source_repository": task["cwd"]}, {}),
                   ({"source_repository": str(self.root)}, {})]
        for changes, policy_changes in invalid:
            with self.subTest(changes=changes, policy=policy_changes), self.assertRaises(backend.BackendError):
                backend.prepare({**task, **changes}, {**policy, **policy_changes}, self.directory)
        with self.assertRaisesRegex(backend.BackendError, "outside its workspace"):
            backend.prepare(task, policy, Path(task["cwd"]) / "receipts")

    def test_engineering_broader_effective_permissions_hold_before_inference(self):
        for mode in ("broader-roots", "shared-tmp", "foreign-runtime-roots", "foreign-environment"):
            with self.subTest(mode=mode):
                self.engineering()
                self.directory = self.root / mode
                (self.root / "calls").unlink(missing_ok=True)
                process, result = self.run_fake(mode)
                self.assertEqual(process.returncode, 1)
                self.assertEqual(result["status"], "hold")
                self.assertNotIn("turn/start", (self.root / "calls").read_text())

    def test_legacy_empty_additional_roots_preserve_exact_cwd_and_explicit_turn_policy(self):
        self.engineering()
        process, result = self.run_fake("legacy-roots")
        self.assertEqual(process.returncode, 0, process.stderr)
        effective = result["effective"]
        self.assertEqual(effective["runtimeWorkspaceRoots"], [])
        self.assertEqual(effective["sandbox"]["writableRoots"], [])
        self.assertEqual(effective["cwd"], self.task["cwd"])
        self.assertEqual(effective["requested_workspace"], self.task["cwd"])
        self.assertEqual(effective["turn_sandbox_policy"]["writableRoots"], [self.task["cwd"]])
        self.assertIn("legacy explicit roots empty", effective["workspace_evidence"])
        self.assertIn("no read isolation", effective["workspace_evidence"])

    def test_engineering_observations_keep_denials_and_cannot_grant_other_tools(self):
        self.engineering("scout")
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        state = {"commands": [], "file_changes": []}
        item = {"type": "commandExecution", "id": "denied", "command": "python3 -B test.py",
                "cwd": request["cwd"], "status": "declined", "exitCode": None}
        with self.assertRaisesRegex(backend.BackendError, "permission hold"):
            backend._observe_tool(request, state, item, True)
        self.assertEqual(state["commands"][0]["status"], "declined")
        with self.assertRaisesRegex(backend.BackendError, "read-only responsibility"):
            backend._observe_tool(request, state, {"type": "fileChange", "id": "patch", "changes": []}, True)
        with self.assertRaisesRegex(backend.BackendError, "unexpected tool"):
            backend._observe_tool(request, state, {"type": "mcpToolCall", "id": "mcp"}, True)

    def test_command_output_summary_is_bounded_and_explicitly_truncated(self):
        self.engineering()
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        state = {"commands": [], "file_changes": []}
        backend._observe_tool(request, state, {"type": "commandExecution", "id": "cmd", "command": "read",
            "cwd": request["cwd"], "status": "completed", "exitCode": 0, "aggregatedOutput": "x" * 9000}, True)
        self.assertEqual(len(state["commands"][0]["aggregatedOutput"]), 4096)
        self.assertTrue(state["commands"][0]["output_truncated"])

    def test_scout_private_experiment_scope_preserves_original_readonly(self):
        self.engineering("scout")
        self.task["write_scope"] = ["scratch/", "sample.py"]
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        self.assertEqual(request["sandbox"], "workspace-write")
        self.assertEqual(request["source_repository"], self.task["source_repository"])
        self.assertNotIn(request["source_repository"], backend._sandbox_policy(request)["writableRoots"])
        prompt = backend._instructions(request)
        self.assertIn("Original repository (read-only)", prompt)
        self.assertIn("temporary wrappers", prompt)
        self.assertIn("python -B", prompt)
        with self.assertRaisesRegex(backend.BackendError, "disjoint directories"):
            backend.prepare({**self.task, "source_repository": self.task["cwd"]}, self.policy, self.root / "other")

    def test_reviewer_private_scratch_is_narrow_and_sets_local_temporary_environment(self):
        self.engineering("reviewer")
        scratch = Path(self.task["cwd"]) / ".scratch"
        self.task.update(scratch_directory=str(scratch), write_scope=[".scratch/"])
        spec = self.prepare()
        self.assertEqual(spec["env"], {"TMPDIR": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"})
        request = json.loads((self.directory / "backend-request.json").read_text())
        self.assertEqual(request["scratch_directory"], str(scratch))
        self.assertEqual(request["sandbox"], "workspace-write")
        self.assertIn("Do not modify the patch", backend._instructions(request))
        self.assertNotIn(request["source_repository"], backend._sandbox_policy(request)["writableRoots"])
        invalid = [dict(write_scope=[".scratch/", "sample.py"]), dict(write_scope=["."]),
                   dict(scratch_directory=self.task["cwd"]), dict(scratch_directory=str(self.root / "shared")),
                   dict(scratch_directory=".scratch"), dict(write_scope=[])]
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(backend.BackendError):
                backend.prepare({**self.task, **change}, self.policy, self.root / "invalid")

    def test_engineering_selects_verified_local_environment_and_refuses_remote_override(self):
        self.engineering()
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        params = backend._thread_params(request, {"config": {}, "layers": []})
        self.assertEqual(params["environments"], [{"environmentId": "local", "cwd": self.task["cwd"],
                                                 "runtimeWorkspaceRoots": [self.task["cwd"]]}])
        with patch.dict(os.environ, {"CODEX_EXEC_SERVER_URL": "https://unsupported.invalid"}):
            with self.assertRaisesRegex(backend.BackendError, "CODEX_EXEC_SERVER_URL"):
                backend.prepare(self.task, self.policy, self.root / "other")
            process = subprocess.run([sys.executable, str(ROOT / "agent_backend.py"), "run",
                                      str(self.directory / "backend-request.json")], capture_output=True, text=True, timeout=5)
        self.assertEqual(process.returncode, 1, process.stderr)
        result = json.loads((self.directory / "backend-result.json").read_text())
        self.assertIn("CODEX_EXEC_SERVER_URL", result["detail"])
        self.assertFalse((self.root / "calls").exists())


if __name__ == "__main__":
    unittest.main()
