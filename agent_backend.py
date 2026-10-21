"""Bounded Codex app-server adapter, using the documented stdio JSON protocol.

These are independent externally controlled sessions, not native chat subagents.
The initial profile supports supplied-context, read-only reasoning. It disables
execution, delegation and connected tools; it does not claim an exhaustive
builtin-tool allowlist. A request for literal tool-free execution is rejected.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
import math
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import tempfile
import time

MAX_BYTES = 1024 * 1024
PROFILE = "read-only-no-exec"
# Verified by the local runtime feature catalog. Unknown feature names cause
# startup failure, which is retained as a hold rather than silently ignored.
DISABLED_FEATURES = (
    "shell_tool", "unified_exec", "multi_agent", "apps", "plugins",
    "browser_use", "browser_use_external", "computer_use", "image_generation",
    "hooks", "view_image", "tool_suggest", "code_mode", "code_mode_host",
    "memories", "goals", "sleep_tool", "request_permissions_tool",
    "multi_agent_v2", "multi_agent_v2_dynamic_tools", "skill_mcp_dependency_install",
    "skill_search", "skill_env_var_dependency_prompt", "remote_plugin",
)


class BackendError(ValueError):
    pass


def _json(raw):
    if len(raw.encode()) > MAX_BYTES:
        raise BackendError("backend JSON exceeds 1 MiB")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BackendError("duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise BackendError(f"nonfinite JSON number: {value}")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def _atomic(path, value, *, identical=False):
    encoded = (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()
    if path.is_symlink():
        raise BackendError("backend file must not be a symlink")
    if identical and path.exists():
        if path.read_bytes() != encoded:
            raise BackendError("operation identity reused with different backend request")
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def prepare(task, policy, directory):
    """Prepare an immutable request; never run inference or change global config.

    Explicit settings are required because an independent session cannot inherit
    the calling chat's model/effort/permissions. Only this conservative first
    profile is supported. Arbitrary config overrides are intentionally absent.
    """
    directory = Path(directory).absolute()
    if any(p.is_symlink() for p in (directory, *directory.parents)):
        raise BackendError("backend directory must not traverse symlinks")
    for key in ("model", "effort", "service_tier", "codex_binary"):
        if not isinstance(policy.get(key), str) or not policy[key].strip():
            raise BackendError(f"agent policy requires explicit {key}")
    if policy.get("sandbox") != "read-only" or policy.get("approval") != "never":
        raise BackendError("this backend requires read-only sandbox and never approval")
    if policy.get("network") not in (False, "disabled"):
        raise BackendError("this backend requires disabled worker network access")
    if policy.get("agent_profile") != PROFILE or policy.get("tools") == "none":
        raise BackendError(f"explicit agent_profile={PROFILE!r} is required; literal tool-free is not verified")
    if policy.get("nested_delegation", False):
        raise BackendError("nested delegation is not supported")
    binary = Path(policy["codex_binary"])
    if not binary.is_absolute() or not binary.is_file() or not os.access(binary, os.X_OK):
        raise BackendError("codex_binary must be an available absolute executable")
    cwd = Path(task["cwd"]).resolve()
    if not cwd.is_dir():
        raise BackendError("agent cwd does not exist")
    prompt = task.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode()) > MAX_BYTES // 2:
        raise BackendError("agent prompt must be nonempty and at most 512 KiB")
    timeout = task.get("timeout_seconds", policy.get("agent_timeout_seconds", 300))
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise BackendError("agent timeout must be finite and positive")
    request = {
        "version": 1, "operation_id": task.get("operation_id", directory.name),
        "task_id": task["id"], "cwd": str(cwd), "prompt": prompt,
        "model": policy["model"], "effort": policy["effort"],
        "service_tier": policy["service_tier"], "codex_binary": str(binary),
        "timeout_seconds": timeout, "agent_tools": PROFILE,
        "sandbox": "read-only", "approval": "never", "network": False,
        "output_schema": task.get("output_schema"),
    }
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    _atomic(directory / "backend-request.json", request, identical=True)
    return {"argv": [sys.executable, str(Path(__file__).resolve()), "run", str(directory / "backend-request.json")],
            "cwd": str(cwd), "env": {}, "timeout_seconds": timeout + 10,
            "operation_id": request["operation_id"]}


def _overrides(request, directory):
    settings = {
        "model": request["model"], "model_reasoning_effort": request["effort"],
        "service_tier": request["service_tier"], "approval_policy": "never",
        "sandbox_mode": "read-only", "web_search": "disabled",
        "sandbox_workspace_write.network_access": False,
        "agents.enabled": False, "sqlite_home": str(directory / "runtime-state"),
        "log_dir": str(directory / "runtime-logs"),
    }
    settings.update({f"features.{key}": False for key in DISABLED_FEATURES})
    return settings


def _thread_params(request, effective_config):
    # config/read(includeLayers=true) supplies all known layer server names.
    # Disable each entry instead of assuming an empty map clears merged config.
    servers = set()
    if not isinstance(effective_config, dict):
        raise BackendError("config/read did not return an object")
    layers = effective_config.get("layers") or []
    if not isinstance(layers, list) or any(not isinstance(layer, dict) for layer in layers):
        raise BackendError("config/read returned malformed configuration layers")
    for config in [effective_config.get("config") or {}, *(layer.get("config") or {} for layer in layers)]:
        if not isinstance(config, dict) or not isinstance(config.get("mcp_servers") or {}, dict):
            raise BackendError("config/read returned malformed MCP configuration")
        servers.update(config.get("mcp_servers") or {})
    # Unlike CLI TOML text, app-server's config map splits dotted keys literally.
    # Quoting a segment creates a different server named with quote characters.
    # Fail closed for names whose safe addressing this backend cannot establish.
    if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name) for name in servers):
        raise BackendError("MCP server name cannot be safely addressed by the app-server dotted config override")
    overrides = {f"mcp_servers.{name}.enabled": False for name in sorted(servers)}
    overrides.update({f"features.{key}": False for key in DISABLED_FEATURES})
    overrides.update({"agents.enabled": False, "web_search": "disabled",
                      "model_reasoning_effort": request["effort"]})
    return {
        "model": request["model"], "serviceTier": request["service_tier"],
        "allowProviderModelFallback": False, "cwd": request["cwd"],
        "sandbox": "read-only", "approvalPolicy": "never",
        "environments": [], "runtimeWorkspaceRoots": [request["cwd"]],
        "config": overrides, "ephemeral": True,
        "developerInstructions": (
            "You are a bounded reasoning worker in an externally controlled run. "
            "Work only from supplied context. Do not call tools, spawn agents, "
            "execute commands, access services, or alter files. Return one JSON "
            "object as your final answer. Report missing context explicitly. "
            "Your completion is a proposed result, not engineering acceptance."
        ),
    }


def verify_effective(request, response):
    """Require the server's resolved settings before sending any model turn."""
    if not isinstance(response, dict):
        raise BackendError("runtime returned malformed thread settings")
    result = {key: response.get(key) for key in (
        "model", "modelProvider", "reasoningEffort", "serviceTier", "sandbox",
        "approvalPolicy", "activePermissionProfile", "runtimeWorkspaceRoots")}
    expected = {"model": request["model"], "reasoningEffort": request["effort"],
                "serviceTier": request["service_tier"], "approvalPolicy": "never"}
    for key, value in expected.items():
        if response.get(key) != value:
            raise BackendError(f"resolved {key} differs from requested setting: {response.get(key)!r}")
    sandbox = response.get("sandbox") or {}
    if sandbox.get("type") != "readOnly" or sandbox.get("networkAccess", False):
        raise BackendError("runtime did not resolve read-only, network-disabled sandbox")
    thread = response.get("thread") or {}
    if thread.get("environments") != []:
        raise BackendError("runtime did not confirm disabled environment access")
    if not isinstance(thread.get("id"), str) or not thread["id"]:
        raise BackendError("runtime did not provide a thread identity")
    result["environments"] = []
    result["settings_evidence"] = "app-server thread/start response; not provider-side per-token telemetry"
    result["tool_limit"] = "known execution/delegation/connectors disabled; exhaustive builtin tool-free guarantee unavailable"
    return result


class Rpc:
    """Minimal newline JSON client; bounded reads and no guessed server APIs."""
    def __init__(self, argv, cwd):
        self.process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=None, bufsize=0)
        self.serial = 0
        self.buffer = bytearray()
        self.notifications = deque()

    def send(self, method, params=None, *, notification=False):
        self.serial += 1
        message = {"method": method, "params": params or {}}
        if not notification:
            message["id"] = self.serial
        self.process.stdin.write((json.dumps(message) + "\n").encode())
        self.process.stdin.flush()
        return self.serial

    def read(self, deadline):
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("app-server response deadline expired")
            ready, _, _ = select.select([self.process.stdout], [], [], min(.2, remaining))
            if not ready:
                continue
            block = os.read(self.process.stdout.fileno(), 65536)
            if not block:
                raise BackendError("app-server closed its output before a result; inspect stderr")
            self.buffer.extend(block)
            if len(self.buffer) > MAX_BYTES:
                raise BackendError("app-server message exceeds 1 MiB")
        line, _, self.buffer = self.buffer.partition(b"\n")
        return _json(line.decode())

    def call(self, method, params, deadline):
        identity = self.send(method, params)
        while True:
            message = self.read(deadline)
            if message.get("id") == identity and "method" not in message:
                if "error" in message:
                    raise BackendError(json.dumps(message["error"], ensure_ascii=False))
                return message.get("result", {})
            self.handle_unexpected(message)

    def handle_unexpected(self, message):
        if "method" in message and "id" in message:
            # This backend never approves tools or permission expansion.
            self.process.stdin.write((json.dumps({"id": message["id"], "error": {
                "code": -32601, "message": "controller profile does not permit interactive tools or approval"}}) + "\n").encode())
            self.process.stdin.flush()
            raise BackendError(f"unexpected server request: {message['method']}")
        self.notifications.append(message)

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=1)


def run_request(path):
    path = Path(path).absolute()
    request = _json(path.read_text())
    directory = path.parent
    destination = directory / "backend-result.json"
    # Execution's operation lock prevents duplicates. A separate launch marker
    # prevents accidental direct replay of this internal entry point as well.
    try:
        fd = os.open(directory / "backend-started", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise BackendError("backend operation already started; reconcile, never replay")
    with os.fdopen(fd, "w") as stream:
        stream.write(str(time.time()))
        stream.flush()
        os.fsync(stream.fileno())
    state = {"status": "hold", "result": None, "effective": {}, "usage": None,
             "configured": {key: request[key] for key in ("model", "effort", "service_tier", "sandbox", "approval", "network", "agent_tools")},
             "operation_id": request["operation_id"], "thread_id": None, "turn_id": None,
             "detail": "startup not yet acknowledged"}
    _atomic(destination, state)
    interrupted = [False]
    def on_signal(signum, frame):
        interrupted[0] = True
    previous_signals = {sig: signal.signal(sig, on_signal) for sig in (signal.SIGTERM, signal.SIGINT)}
    client = None
    try:
        argv = [request["codex_binary"], "app-server"]
        for key, value in _overrides(request, directory).items():
            argv.extend(["-c", f"{key}={json.dumps(value)}"])
        client = Rpc(argv, request["cwd"])
        deadline = time.monotonic() + request["timeout_seconds"]
        setup_deadline = min(deadline, time.monotonic() + 30)
        client.call("initialize", {"clientInfo": {"name": "codex-delegation-kit", "title": "Delegation kit", "version": "1"},
                                   "capabilities": {"experimentalApi": True}}, setup_deadline)
        client.send("initialized", notification=True)
        configuration = client.call("config/read", {"cwd": request["cwd"], "includeLayers": True}, setup_deadline)
        # Never persist configuration values: MCP environments may include secrets.
        response = client.call("thread/start", _thread_params(request, configuration), setup_deadline)
        state["thread_id"] = response["thread"]["id"]
        _atomic(destination, state)
        state["effective"] = verify_effective(request, response)
        state["detail"] = "thread created; turn not yet acknowledged"
        _atomic(destination, state)
        if interrupted[0]:
            raise BackendError("cancelled before turn dispatch")
        params = {"threadId": state["thread_id"], "model": request["model"], "effort": request["effort"],
                  "serviceTier": request["service_tier"], "serviceTierForTurn": request["service_tier"],
                  "approvalPolicy": "never", "sandboxPolicy": {"type": "readOnly", "networkAccess": False},
                  "environments": [], "input": [{"type": "text", "text": request["prompt"]}],
                  "clientUserMessageId": request["operation_id"]}
        if request.get("output_schema") is not None:
            params["outputSchema"] = request["output_schema"]
        # The durable marker is before dispatch. A crash in this interval is
        # uncertain, never permission to send the same turn again.
        state["detail"] = "turn dispatch may have occurred; do not retry this operation"
        _atomic(destination, state)
        response = client.call("turn/start", params, setup_deadline)
        state["turn_id"] = response["turn"]["id"]
        state["detail"] = "turn running"
        _atomic(destination, state)
        final_text = None
        cancellation_sent = False
        with (directory / "backend-events.jsonl").open("a") as events:
            while True:
                if interrupted[0] and not cancellation_sent:
                    client.send("turn/interrupt", {"threadId": state["thread_id"], "turnId": state["turn_id"]})
                    cancellation_sent = True
                    state["detail"] = "interruption requested; awaiting confirmation"
                    _atomic(destination, state)
                if client.notifications:
                    message = client.notifications.popleft()
                else:
                    try:
                        message = client.read(min(deadline, time.monotonic() + .2))
                    except TimeoutError:
                        if time.monotonic() >= deadline:
                            raise
                        continue
                if "id" in message and "method" not in message:
                    continue  # interruption response; completion is authoritative
                if "id" in message and "method" in message:
                    client.handle_unexpected(message)
                method = message.get("method", "")
                body = message.get("params", {})
                if body.get("threadId", state["thread_id"]) != state["thread_id"]:
                    continue
                events.write(json.dumps(message, ensure_ascii=False) + "\n")
                events.flush()
                if method == "model/rerouted":
                    raise BackendError("runtime rerouted the requested model; result held")
                if method == "thread/tokenUsage/updated":
                    state["usage"] = body.get("tokenUsage")
                if method == "item/completed":
                    item = body.get("item", {})
                    if item.get("type") == "agentMessage":
                        final_text = item.get("text")
                    elif item.get("type") in {"commandExecution", "mcpToolCall", "dynamicToolCall", "collabAgentToolCall", "fileChange", "webSearch"}:
                        raise BackendError(f"unexpected tool activity: {item.get('type')}; result held")
                if method == "turn/completed" and body.get("turn", {}).get("id") == state["turn_id"]:
                    turn = body["turn"]
                    if turn.get("status") != "completed" or cancellation_sent:
                        raise BackendError("turn did not complete normally: " + json.dumps(turn.get("error") or turn.get("status")))
                    if final_text is None:
                        # Some runtimes include final items in the turn snapshot.
                        for item in turn.get("items", []):
                            if item.get("type") == "agentMessage":
                                final_text = item.get("text")
                    if not isinstance(final_text, str):
                        raise BackendError("completed turn has no final text")
                    result = _json(final_text)
                    if not isinstance(result, dict):
                        raise BackendError("final result must be one JSON object")
                    state.update(status="completed", result=result, detail="model turn completed; acceptance requires controller validation")
                    break
    except (OSError, ValueError, KeyError, TypeError, TimeoutError) as error:
        state.update(status="hold", detail=str(error))
    finally:
        if client:
            client.close()
        _atomic(destination, state)
        for sig, previous in previous_signals.items():
            signal.signal(sig, previous)
    return 0 if state["status"] == "completed" else 1


def collect(directory, observation):
    directory = Path(directory)
    path = directory / "backend-result.json"
    if not observation.get("released", False):
        return {"status": "hold", "result": None, "effective": {}, "detail": "owned execution has not been released"}
    if not path.exists() or path.is_symlink():
        return {"status": "hold", "result": None, "effective": {}, "detail": "backend result unavailable; inspect execution stderr"}
    try:
        state = _json(path.read_text())
        request = _json((directory / "backend-request.json").read_text())
        if not isinstance(state, dict) or not isinstance(request, dict):
            raise BackendError("backend request and result must be JSON objects")
        if state.get("operation_id") != request.get("operation_id"):
            raise BackendError("backend result belongs to another operation")
        if state.get("status") not in {"completed", "failed", "hold", "invalid"}:
            raise BackendError("invalid backend status")
        if observation.get("state", observation.get("status")) in {"cancelled", "setup_error", "uncertain"} or observation.get("returncode") != 0:
            state.update(status="hold", result=None, detail="execution did not finish normally: " + state.get("detail", ""))
        if state["status"] == "completed" and not isinstance(state.get("result"), dict):
            raise BackendError("completed backend has no JSON result")
        return state
    except (OSError, ValueError, TypeError) as error:
        return {"status": "invalid", "result": None, "effective": {}, "detail": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run"])
    parser.add_argument("request")
    args = parser.parse_args()
    try:
        return run_request(args.request)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
