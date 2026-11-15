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
        if mode == "startup-wait":
            continue
        p = message["params"]
        thread_cwd = p["cwd"]
        (root / "thread-params").write_text(json.dumps(p))
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
        if mode in {"research-guard", "research-wait"}:
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn,
                "item":{"type":"agentMessage", "id":"finding", "text":"Source A section 3 rules out the first hypothesis."}}})
            emit({"method":"item/agentMessage/delta", "params":{"threadId":thread, "turnId":turn,
                "itemId":"unfinished", "delta":"Second source comparison remains "}})
            emit({"method":"item/agentMessage/delta", "params":{"threadId":thread, "turnId":turn,
                "itemId":"unfinished", "delta":"unfinished."}})
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn,
                "item":{"type":"reasoning", "text":"hidden reasoning must not enter recovery"}}})
            if mode == "research-guard":
                emit({"method":"item/started", "params":{"threadId":thread, "turnId":turn,
                    "item":{"type":"webSearch", "id":"denied-web"}}})
            continue
        if mode == "wait":
            continue
        if mode == "denied":
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn,
                "item":{"type":"commandExecution", "id":"denied", "command":"blocked", "cwd":thread_cwd,
                        "status":"declined", "exitCode":None}}})
            continue
        if mode in {"engineering", "wait-command"}:
            assert message["params"]["environments"] == [{"environmentId":"local", "cwd":thread_cwd, "runtimeWorkspaceRoots":[thread_cwd]}]
            assert message["params"]["sandboxPolicy"] == {"type": "workspaceWrite", "writableRoots": [thread_cwd],
                "networkAccess": False, "excludeSlashTmp": True, "excludeTmpdirEnvVar": True}
            command = {"type":"commandExecution", "id":"command-1", "command":"python3 -B test.py", "cwd":thread_cwd,
                "status":"inProgress", "processId":"pty-1", "exitCode":None, "aggregatedOutput":None}
            emit({"method":"item/started", "params":{"threadId":thread, "turnId":turn, "item":command}})
            command.update(status="completed", exitCode=0, aggregatedOutput="one actual synthetic assertion passed", durationMs=5)
            emit({"method":"item/completed", "params":{"threadId":thread, "turnId":turn, "item":command}})
            if mode == "wait-command":
                continue
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

    def test_common_guidance_delivered_with_profile_boundaries_and_run_settings(self):
        # Synthetic app-server captures the actual thread/start payload, not model behavior.
        for role in (None, "scout", "worker", "reviewer", "owner"):
            with self.subTest(role=role):
                if role is not None:
                    self.engineering(role)
                self.directory = self.root / (role or "reasoning")
                process, result = self.run_fake()
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(result["status"], "completed")
                params = json.loads((self.root / "thread-params").read_text())
                prompt = params["developerInstructions"]
                self.assertEqual(prompt.count(backend.COMMON_INSTRUCTIONS), 1)
                self.assertIn("For consequential scientific questions, begin with the original problem, requested outcome and operating envelope", prompt)
                self.assertIn("inspect relevant primary-source sections", prompt)
                self.assertIn("source identity, link and locator, access level, assumptions, conditions and limits", prompt)
                self.assertIn("An abstract or secondary summary cannot establish unseen methods, data or validation", prompt)
                self.assertIn("During ordinary development, when an important scientific gap could materially change direction", prompt)
                self.assertIn("without waiting for the user, while independent permitted work continues", prompt)
                self.assertIn("First reuse adequate curated research and verify current applicability", prompt)
                self.assertIn("the engineering or task owner commissions one pair of independent full-problem inquiries through existing eligible responsibilities", prompt)
                self.assertIn("neither receives the other inquiry's questions, map, findings or account, or the emerging engineering plan, until both first accounts are preserved", prompt)
                self.assertIn("An assigned inquiry requests bounded support through the controller, not another pair", prompt)
                self.assertIn("scouts and workers surface gaps but do not commission it", prompt)
                self.assertIn("before seeing authors' coverage maps, accounts or engineering plans", prompt)
                self.assertIn("Factual source context excludes engineering recommendations, including those appended to code observations", prompt)
                self.assertIn("Withhold engineering plans and prior tranche approvals through scientific disposition", prompt)
                self.assertIn("If an author map/account or engineering plan/approval was previously exposed, disclose that exposure", prompt)
                self.assertIn("Early architecture review uses a separate permitted responsibility within the same limits, or dependent commitments wait", prompt)
                self.assertIn("Request missing original context through the controller", prompt)
                self.assertIn("Check the weakest primary-source support, decisive quantitative comparisons and contrary or coupled cases", prompt)
                self.assertIn("cover the requested operating envelope with substantive explanations and discriminating evidence in each material domain; depth in one cannot offset an omitted or shallow other", prompt)
                self.assertIn("Assess bounded-step engineering readiness separately from scientific coverage; neither readiness nor one successful example per branch establishes broad grounding", prompt)
                self.assertIn("Retain each material question, including unanswered ones", prompt)
                self.assertIn("a successful example closes only distinctions it actually resolves", prompt)
                self.assertIn("Before treating missing deployment or calibration inputs as a boundary, complete feasible source comparisons or representative calculations", prompt)
                self.assertIn("Complete feasible research and changed-evidence scientific review before handoff, then verify engineering uptake and independently review resulting decisions before acceptance", prompt)
                self.assertIn("meaningful bounded derivation, reference calculation or public-observation check", prompt)
                self.assertIn("source-supported mechanisms and conditions to the development decision and affected code or check", prompt)
                self.assertIn("do not substitute assumptions or model predictions for measurements, omit contrary results or collapse source values and independent reconstructions", prompt)
                self.assertIn("When sources report both predictions and observations", prompt)
                self.assertIn("Treat _ref/ and _appraisal/ as user-curated", prompt)
                self.assertIn("no new research file or ledger is mandatory", prompt)
                self.assertIn("do not infer or claim any permission beyond the assignment, including browsing, network, tools, writes or continuation", prompt)
                if role in {"reviewer", "owner"}:
                    self.assertIn("The assignment selects scientific subject investigation, research leadership, scientific critique, or engineering ownership/review", prompt)
                    self.assertIn("A subject investigator owns that investigation as its sole substantive research assignment in a separate working context", prompt)
                    self.assertIn("an existing context already dedicated to that subject may continue", prompt)
                    self.assertIn("Develop the reusable scientific account before a compact integration handoff", prompt)
                    self.assertIn("The research lead owns cross-subject synthesis and unresolved relationships; the engineering owner owns the implementation plan", prompt)
                    self.assertIn("Engineering readiness, a compact coordinator return, and completion of a bounded lookup do not define completion of a scientific account", prompt)
                    self.assertIn("After preserving the independent full-problem discovery accounts", prompt)
                    self.assertIn("derives a revisable outline of scientific subjects from the original problem and inspected literature", prompt)
                    self.assertIn("For material subjects whose grounding is inadequate, commission focused subject investigations through the coordinator", prompt)
                    self.assertIn("Each author's sole substantive research assignment is its focused subject question in a separate working context", prompt)
                    self.assertIn("no fixed count, chapter, word or iteration quotas apply", prompt)
                    self.assertIn("the full problem and constraints, subject question and boundaries, relevant primary-source leads and factual context, and adjacent-subject relationships", prompt)
                    self.assertIn("Do not pass a settled integrated plan or acceptance verdict as its scientific target", prompt)
                    self.assertIn("schedule subjects sequentially within the existing shared allowance and staffing limits", prompt)
                    self.assertIn("A subject investigator develops the scientific explanation and its evidence before producing a compact integration handoff", prompt)
                    self.assertIn("compare materially different explanations and observations, and perform useful bounded quantitative or observational research checks", prompt)
                    self.assertIn("The lead retains end-to-end scientific responsibility across code audits and specialist partitions", prompt)
                    self.assertIn("subjects not yet investigated", prompt)
                    self.assertIn("routes unresolved relationships or corrections to their authors", prompt)
                    self.assertIn("Return an adequately developed subject account or an explicit partial account with the remaining scientific work and actual limiting dependency", prompt)
                    self.assertIn("the task owner retains responsibility through scientific correction and uptake", prompt)
                else:
                    self.assertNotIn("The assignment selects scientific subject investigation, research leadership, scientific critique, or engineering ownership/review", prompt)
                self.assertEqual((params["model"], params["config"]["model_reasoning_effort"],
                                  params["serviceTier"]), ("test-model", "medium", "default"))
                self.assertFalse(params["config"]["agents.enabled"])
                self.assertNotIn("astra", prompt.lower())
                if role is None:
                    self.assertIn("Do not call tools, spawn agents", prompt)
                    self.assertIn("execute commands, access services, or alter files", prompt)
                    self.assertIn("do not infer or claim any permission beyond the assignment, including browsing, network, tools, writes or continuation", prompt)
                    self.assertEqual(params["sandbox"], "read-only")
                else:
                    self.assertIn(f"You are the {role}", prompt)
                    self.assertIn("do not maintain duplicate records or spawn agents", prompt)
                    self.assertIn("Do not access network services", prompt)
                    self.assertIn("Use only the authorized repository and permitted command scope", prompt)
                    self.assertIn("Original repository (read-only)", prompt)
                    self.assertEqual(params["sandbox"], "read-only" if role in {"scout", "reviewer"} else "workspace-write")
                    if role == "reviewer":
                        self.assertIn("Do not modify the patch or source", prompt)

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

    def test_guard_preserves_public_research_and_supported_cleanup_without_acceptance(self):
        process, result = self.run_fake("research-guard")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(result["status"], "hold")
        self.assertIsNone(result["result"])
        self.assertIn("unexpected tool activity", result["detail"])
        self.assertEqual(result["termination_kind"], "error")
        recovery = result["recovery"]
        self.assertFalse(recovery["accepted"])
        self.assertEqual([m["text"] for m in recovery["messages"]], [
            "Source A section 3 rules out the first hypothesis.",
            "Second source comparison remains unfinished."])
        self.assertTrue(recovery["messages"][0]["completed_message"])
        self.assertFalse(recovery["messages"][1]["completed_message"])
        self.assertNotIn("hidden reasoning", json.dumps(recovery))
        self.assertEqual(result["cleanup_interrupt"], {"requested": True, "acknowledged": True,
                         "terminal_observed": True, "terminal_status": "interrupted"})
        self.assertIn("denied-web", Path(result["events"]).read_text())
        self.assertEqual((self.root / "calls").read_text().count("turn/start"), 1)

    def test_recovery_message_retention_is_bounded_and_marks_omissions(self):
        state = {"turn_id": "t", "recovery": {"messages": [], "omitted_messages": 0, "omitted_text_bytes": 0}}
        for index in range(20):
            backend._capture_public_message(state, "item/completed", {"turnId": "t", "item": {
                "type": "agentMessage", "id": str(index), "text": "finding " + str(index)}})
        self.assertEqual(len(state["recovery"]["messages"]), backend.MAX_RECOVERY_MESSAGES)
        self.assertEqual(state["recovery"]["omitted_messages"], 4)
        backend._capture_public_message(state, "item/agentMessage/delta", {
            "turnId": "t", "itemId": "large", "delta": "µ" * backend.MAX_RECOVERY_TEXT_BYTES})
        recovery = state["recovery"]
        self.assertLessEqual(sum(len(m["text"].encode()) for m in recovery["messages"]), backend.MAX_RECOVERY_TEXT_BYTES)
        self.assertTrue(recovery["messages"][-1]["text_truncated"])
        self.assertGreater(recovery["omitted_text_bytes"], 0)
        before = json.dumps(recovery)
        self.assertFalse(backend._capture_public_message(state, "item/agentMessage/delta", {
            "turnId": "other-turn", "itemId": "foreign", "delta": "foreign"}))
        self.assertEqual(json.dumps(recovery), before)

    def test_live_checkpoint_precedes_timeout_and_remains_unaccepted(self):
        (self.root / "mode").write_text("research-wait")
        self.task["timeout_seconds"] = 1.5
        spec = self.prepare()
        process = subprocess.Popen(spec["argv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 3
        checkpoint = None
        while time.monotonic() < deadline and process.poll() is None:
            path = self.directory / "backend-result.json"
            if path.exists():
                checkpoint = json.loads(path.read_text())
                if len(checkpoint.get("recovery", {}).get("messages", [])) == 2:
                    break
            time.sleep(.01)
        self.assertIsNone(process.poll(), "public checkpoint must exist while the operation is still running")
        self.assertEqual(checkpoint["detail"], "turn running")
        self.assertFalse(checkpoint["recovery"]["accepted"])
        _, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 1, stderr)
        result = backend.collect(self.directory, {"state": "completed", "released": True, "returncode": 1})
        self.assertEqual(len(result["recovery"]["messages"]), 2)
        self.assertIsNone(result["result"])
        self.assertIn("deadline expired", result["detail"])

    def test_checkpoint_denial_keeps_prior_evidence_and_still_closes_and_restores_signals(self):
        import engineering
        (self.root / "mode").write_text("research-guard")
        self.prepare()
        original_atomic, original_validate, original_close = backend._atomic, engineering.validate_artifact_paths, backend.Rpc.close
        denied, preserved, closed = [False], {}, []
        signals = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
        def checkpoint(path, state, **kwargs):
            if "unexpected tool activity" in state.get("detail", ""):
                if not denied[0]:
                    preserved["result"] = path.read_bytes()
                    preserved["events"] = (self.directory / "backend-events.jsonl").read_bytes()
                denied[0] = True
                raise ValueError("synthetic changed ignore rule denies checkpoint")
            return original_atomic(path, state, **kwargs)
        def validate(paths, **kwargs):
            if denied[0] and any(Path(path).name == "backend-events.jsonl" for path in paths):
                raise ValueError("synthetic changed ignore rule denies raw append")
            return original_validate(paths, **kwargs)
        def close(client):
            original_close(client)
            closed.append(client.process.poll())
        with patch.object(backend, "_atomic", side_effect=checkpoint), patch.object(backend.Rpc, "close", new=close), \
                patch.object(engineering, "validate_artifact_paths", side_effect=validate):
            with self.assertRaisesRegex(backend.BackendError, "original operation state: unexpected tool activity.*preservation error"):
                backend.run_request(self.directory / "backend-request.json")
        self.assertEqual(len(closed), 1)
        self.assertIsNotNone(closed[0])
        self.assertEqual({sig: signal.getsignal(sig) for sig in signals}, signals)
        self.assertEqual((self.directory / "backend-result.json").read_bytes(), preserved["result"])
        self.assertEqual((self.directory / "backend-events.jsonl").read_bytes(), preserved["events"])
        checkpoint = json.loads(preserved["result"])
        self.assertIn("Source A section 3", checkpoint["recovery"]["messages"][0]["text"])
        self.assertIn("turn/interrupt", (self.root / "calls").read_text())

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
        self.assertEqual(result["termination_kind"], "interrupted")
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

    def swarm(self):
        self.engineering("scout")
        scratch = Path(self.task["cwd"]) / ".scratch"
        self.task.update(swarm=True, scratch_directory=str(scratch), write_scope=[".scratch/"], timeout_seconds=.5)
        self.policy.update(model="gpt-6-luna", effort="medium")

    def test_swarm_keeps_run_settings_and_rejects_non_scratch_writes(self):
        self.swarm()
        self.prepare()
        request = json.loads((self.directory / "backend-request.json").read_text())
        self.assertTrue(request["swarm"])
        self.assertEqual((request["model"], request["effort"], request["service_tier"]),
                         ("gpt-6-luna", "medium", "default"))
        self.assertIn("inconclusive", backend._instructions(request))
        for change in ({"role": "worker"}, {"write_scope": [".scratch/", "sample.py"]},
                       {"write_scope": []}, {"scratch_directory": None}):
            with self.subTest(change=change), self.assertRaises(backend.BackendError):
                backend.prepare({**self.task, **change}, self.policy, self.root / "invalid")

    def test_swarm_acknowledged_timeout_retains_commands_and_needs_verified_release(self):
        self.swarm()
        process, result = self.run_fake("wait-command")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(result["status"], "cutoff")
        self.assertEqual(result["termination_kind"], "budget_cutoff")
        self.assertEqual(result["commands"][0]["exitCode"], 0)
        self.assertTrue(result["settings_verified"])
        before = (self.directory / "backend-result.json").read_bytes()
        self.assertEqual(backend.collect(self.directory, {"state": "running", "released": False})["status"], "hold")
        stopped = backend.collect(self.directory, {"state": "cancelled", "released": True, "returncode": 1,
                                                   "cancellation_reason": "user stop"})
        self.assertEqual(stopped["status"], "hold")
        self.assertEqual(stopped["termination_kind"], "error")
        timeout = backend.collect(self.directory, {"state": "cancelled", "released": True, "returncode": 1,
                                                   "cancellation_reason": "execution timeout"})
        self.assertEqual(timeout["status"], "cutoff")
        self.assertEqual(before, (self.directory / "backend-result.json").read_bytes())

    def test_swarm_setup_timeout_permission_denial_and_setting_mismatch_stay_held(self):
        self.swarm()
        for mode in ("startup-wait", "denied", "mismatch"):
            with self.subTest(mode=mode):
                self.directory = self.root / mode
                process, result = self.run_fake(mode)
                self.assertEqual(process.returncode, 1, process.stderr)
                self.assertEqual(result["status"], "hold")
                self.assertEqual(result["termination_kind"], "error")
                self.assertIsNone(result["result"])

    def test_non_swarm_timeout_preserves_existing_hold_contract(self):
        self.task["timeout_seconds"] = .5
        process, result = self.run_fake("wait")
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(result["status"], "hold")
        self.assertEqual(result["termination_kind"], "error")


if __name__ == "__main__":
    unittest.main()
