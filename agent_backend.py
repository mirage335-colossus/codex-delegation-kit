"""Bounded Codex app-server adapter, using the documented stdio JSON protocol.

These are independent externally controlled sessions, not native chat subagents.
The reasoning profile uses supplied context. The engineering profile enables
the runtime's sandboxed shell and file editing in one authorized workspace.
Neither profile claims an exhaustive builtin-tool allowlist. Runtime sandboxing
is distinct from assignment command guidance and the controller's patch audit.
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
ENGINEERING_PROFILE = "engineering"
# Verified by the installed app-server's default selection and environment/info.
# Explicit selection avoids inheriting a future remote default environment.
LOCAL_ENVIRONMENT = "local"
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
    the calling chat's model/effort/permissions. Arbitrary config overrides are
    intentionally absent. Commands use the runtime's sandbox, never the
    unsandboxed thread/shellCommand API.
    """
    directory = Path(directory).absolute()
    if any(p.is_symlink() for p in (directory, *directory.parents)):
        raise BackendError("backend directory must not traverse symlinks")
    for key in ("model", "effort", "service_tier", "codex_binary"):
        if not isinstance(policy.get(key), str) or not policy[key].strip():
            raise BackendError(f"agent policy requires explicit {key}")
    profile = policy.get("agent_profile")
    if profile not in {PROFILE, ENGINEERING_PROFILE} or policy.get("tools") == "none":
        raise BackendError("an explicit supported agent_profile is required; literal tool-free is not verified")
    if policy.get("approval") != "never" or policy.get("sandbox") not in {"read-only", "workspace-write"}:
        raise BackendError("this backend requires a restricted sandbox and never approval")
    if profile == PROFILE and policy["sandbox"] != "read-only":
        raise BackendError("the supplied-context profile requires read-only sandbox")
    if policy.get("network") not in (False, "disabled"):
        raise BackendError("this backend requires disabled worker network access")
    if policy.get("nested_delegation", False):
        raise BackendError("nested delegation is not supported")
    binary = Path(policy["codex_binary"])
    if not binary.is_absolute() or not binary.is_file() or not os.access(binary, os.X_OK):
        raise BackendError("codex_binary must be an available absolute executable")
    cwd = Path(task["cwd"]).resolve()
    if not cwd.is_dir():
        raise BackendError("agent cwd does not exist")
    sandbox = "read-only"
    role, scope, commands, source, scratch = None, [], [], None, None
    if profile == ENGINEERING_PROFILE:
        if os.environ.get("CODEX_EXEC_SERVER_URL"):
            raise BackendError("engineering local execution refuses CODEX_EXEC_SERVER_URL override")
        role, scope, commands = task.get("role"), task.get("write_scope", []), task.get("allowed_commands")
        if role not in {"scout", "worker", "reviewer", "owner"}:
            raise BackendError("engineering requires scout, worker, reviewer or owner responsibility")
        original = task.get("source_repository")
        if not isinstance(original, str) or not Path(original).is_absolute():
            raise BackendError("engineering requires an explicit original source_repository")
        source = Path(original).resolve()
        if not source.is_dir() or source.is_relative_to(cwd) or cwd.is_relative_to(source):
            raise BackendError("engineering workspace and original repository must be disjoint directories")
        if not isinstance(scope, list) or any(not isinstance(p, str) or not p.strip() for p in scope):
            raise BackendError("engineering write_scope must be relative paths")
        for name in scope:
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts or ".git" in relative.parts or not (cwd / name).resolve().is_relative_to(cwd):
                raise BackendError("engineering write scope escapes workspace or includes Git metadata")
        if not isinstance(commands, list) or not commands or any(not isinstance(c, str) or not c.strip() for c in commands):
            raise BackendError("engineering requires bounded allowed_commands guidance")
        scratch_name = task.get("scratch_directory")
        if scratch_name is not None:
            if not isinstance(scratch_name, str) or not Path(scratch_name).is_absolute():
                raise BackendError("scratch_directory must be an absolute private directory")
            scratch = Path(scratch_name)
            if (not scratch.resolve().is_relative_to(cwd) or scratch.resolve() == cwd
                    or any(p.is_symlink() for p in (scratch, *scratch.parents))
                    or (scratch.exists() and not scratch.is_dir())):
                raise BackendError("scratch_directory must be an unaliased directory inside the private workspace")
            scratch = scratch.resolve()
            relative_scratch = scratch.relative_to(cwd).as_posix()
            if relative_scratch not in {str(Path(name)) for name in scope}:
                raise BackendError("scratch_directory needs its exact owned write scope")
        if role == "reviewer" and scope and (scratch is None or any(str(Path(name)) != relative_scratch for name in scope)):
            raise BackendError("reviewers may write only their declared private scratch directory")
        if role in {"worker", "owner"} and not scope:
            raise BackendError("editing responsibilities require private-copy write scope")
        if scope:
            if policy["sandbox"] != "workspace-write":
                raise BackendError("private-copy writes require workspace-write authorization")
            sandbox = "workspace-write"
        # An editing worker must not be able to alter the controller's receipts.
        if directory.is_relative_to(cwd):
            raise BackendError("engineering operation records must be outside its workspace")
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
        "timeout_seconds": timeout, "agent_tools": profile,
        "sandbox": sandbox, "approval": "never", "network": False,
        "output_schema": task.get("output_schema"),
    }
    if profile == ENGINEERING_PROFILE:
        request.update(role=role, write_scope=scope, allowed_commands=commands,
                       resources=task.get("resources", {}), source_repository=str(source),
                       execution_environment=LOCAL_ENVIRONMENT)
        if scratch is not None:
            request["scratch_directory"] = str(scratch)
    if len(json.dumps(request, ensure_ascii=False).encode()) > MAX_BYTES:
        raise BackendError("bounded backend request exceeds 1 MiB")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    _atomic(directory / "backend-request.json", request, identical=True)
    environment = {"PYTHONDONTWRITEBYTECODE": "1"} if profile == ENGINEERING_PROFILE else {}
    if scratch is not None:
        environment["TMPDIR"] = str(scratch)
    return {"argv": [sys.executable, str(Path(__file__).resolve()), "run", str(directory / "backend-request.json")],
            "cwd": str(cwd), "env": environment, "timeout_seconds": timeout + 10,
            "operation_id": request["operation_id"]}


def _feature_overrides(request):
    values = {f"features.{key}": False for key in DISABLED_FEATURES}
    if request["agent_tools"] == ENGINEERING_PROFILE:
        # Some models expose the native shell through functions.exec even with
        # code_mode=false. The bundled host dispatches those registered tools;
        # disabling it makes the otherwise enabled shell fail before execution.
        values.update({"features.shell_tool": True, "features.unified_exec": True,
                       "features.code_mode_host": True})
    return values


def _sandbox_policy(request):
    if request["sandbox"] == "workspace-write":
        return {"type": "workspaceWrite", "writableRoots": [request["cwd"]],
                "networkAccess": False, "excludeSlashTmp": True, "excludeTmpdirEnvVar": True}
    return {"type": "readOnly", "networkAccess": False}


def _environments(request):
    if request["agent_tools"] == ENGINEERING_PROFILE:
        return [{"environmentId": LOCAL_ENVIRONMENT, "cwd": request["cwd"],
                 "runtimeWorkspaceRoots": [request["cwd"]]}]
    return []


def _sandbox_config(request):
    return {"sandbox_mode": request["sandbox"], "sandbox_workspace_write.network_access": False,
            "sandbox_workspace_write.writable_roots": [request["cwd"]] if request["sandbox"] == "workspace-write" else [],
            "sandbox_workspace_write.exclude_slash_tmp": True,
            "sandbox_workspace_write.exclude_tmpdir_env_var": True}


def _overrides(request, directory):
    settings = {
        "model": request["model"], "model_reasoning_effort": request["effort"],
        "service_tier": request["service_tier"], "approval_policy": "never",
        "web_search": "disabled",
        "agents.enabled": False, "sqlite_home": str(directory / "runtime-state"),
        "log_dir": str(directory / "runtime-logs"),
    }
    settings.update(_sandbox_config(request))
    settings.update(_feature_overrides(request))
    return settings


def _instructions(request):
    if request["agent_tools"] == PROFILE:
        return (
            "You are a bounded reasoning worker in an externally controlled run. "
            "Work only from supplied context. Do not call tools, spawn agents, "
            "execute commands, access services, or alter files. Return one JSON "
            "object as your final answer. Report missing context explicitly. "
            "Your completion is a proposed result, not engineering acceptance."
        )
    role = request["role"]
    responsibility = {
        "scout": "Inspect actual source and run bounded diagnostic commands. You may create temporary wrappers, compile, test or modify copies only within owned private-workspace paths. Never modify the original repository. Report findings, evidence and uncertainties.",
        "worker": "Investigate the bounded assignment, modify only owned private-copy paths, run relevant checks and return actual results and remaining issues. Never modify the original repository.",
        "reviewer": "Independently inspect the actual patch, source and evidence. Run targeted checks when useful. You may create temporary wrappers and compilation outputs only in the declared private scratch directory. Do not modify the patch or source. Accept or reject with concrete findings; do not approve a patch you authored.",
        "owner": "Continue consequential diagnosis or repair from the existing patch. Preserve earlier changes, original failures, repair history, budgets and acceptance criteria. Your patch still requires independent review.",
    }[role]
    return (
        f"You are the {role} for one bounded engineering assignment. {responsibility}\n"
        "You share the codebase. Preserve other contributors' changes. Read applicable project instructions. "
        "The controller owns scheduling, attempts, ledgers and replenishment; do not maintain duplicate records or spawn agents. "
        "Use only the authorized repository and permitted command scope below. Do not access network services, change global configuration, "
        "commit, push, publish, or request broader permissions. A denied operation is a hold, not permission to retry through another route. "
        "Run checks through the runtime shell; report exact commands and actual results, including failures and unexecuted checks. "
        "For read-only checks use python -B or PYTHONDONTWRITEBYTECODE=1 to avoid creating bytecode caches. "
        "Do not leave background work running. Preserve diagnostic comparisons and distinguish setup failure from a reproduced defect. "
        "Return one JSON object in the assignment's requested schema; a completed turn is not engineering acceptance.\n"
        f"Original repository (read-only): {request['source_repository']}\n"
        f"Private working copy: {request['cwd']}\nOwned write paths in this copy: {json.dumps(request['write_scope'])}\n"
        f"Permitted command scope: {json.dumps(request['allowed_commands'])}\n"
        f"Declared resource allocation (shared by your command descendants): {json.dumps(request['resources'])}\n"
        f"Private scratch directory/TMPDIR: {request.get('scratch_directory', 'not provided; do not assume shared temporary writes')}\n"
        "The filesystem sandbox bounds writes to the workspace, not individual owned files. Command guidance is not an OS allowlist. "
        "You must honor the narrower assignment scope. A scratch-enabled reviewer can technically write workspace files, "
        "but any patch/source modification violates the assignment and invalidates independent acceptance."
    )


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
    overrides.update(_feature_overrides(request))
    overrides.update(_sandbox_config(request))
    overrides.update({"agents.enabled": False, "web_search": "disabled",
                      "model_reasoning_effort": request["effort"]})
    return {
        "model": request["model"], "serviceTier": request["service_tier"],
        "allowProviderModelFallback": False, "cwd": request["cwd"],
        "sandbox": request["sandbox"], "approvalPolicy": "never",
        "environments": _environments(request), "runtimeWorkspaceRoots": [request["cwd"]],
        "config": overrides, "ephemeral": True,
        "developerInstructions": _instructions(request),
    }


def verify_effective(request, response):
    """Require the server's resolved settings before sending any model turn."""
    if not isinstance(response, dict):
        raise BackendError("runtime returned malformed thread settings")
    result = {key: response.get(key) for key in (
        "model", "modelProvider", "reasoningEffort", "serviceTier", "sandbox",
        "approvalPolicy", "activePermissionProfile", "runtimeWorkspaceRoots", "cwd")}
    expected = {"model": request["model"], "reasoningEffort": request["effort"],
                "serviceTier": request["service_tier"], "approvalPolicy": "never"}
    for key, value in expected.items():
        if response.get(key) != value:
            raise BackendError(f"resolved {key} differs from requested setting: {response.get(key)!r}")
    sandbox = response.get("sandbox") or {}
    expected_sandbox = _sandbox_policy(request)
    if sandbox.get("type") != expected_sandbox["type"] or sandbox.get("networkAccess", False):
        raise BackendError("runtime did not resolve requested network-disabled sandbox")
    if request["agent_tools"] == ENGINEERING_PROFILE:
        workspace_roots = response.get("runtimeWorkspaceRoots")
        # This runtime's legacy sandbox response may report no additional roots:
        # workspaceWrite still includes its exact cwd. Do not mistake that empty
        # list for broadened authority or accept any different explicit root.
        if response.get("cwd") != request["cwd"] or workspace_roots not in ([], [request["cwd"]]):
            raise BackendError("runtime did not confirm the authorized workspace")
        result["requested_workspace"] = request["cwd"]
        result["turn_sandbox_policy"] = expected_sandbox
        result["workspace_evidence"] = (
            "legacy explicit roots empty; exact cwd is implicit workspace-write root; "
            "turn supplies explicit sandboxPolicy; no read isolation"
            if not workspace_roots and request["sandbox"] == "workspace-write" else
            "exact cwd confirmed; turn supplies explicit sandboxPolicy; no read isolation")
        if request["sandbox"] == "workspace-write":
            roots = sandbox.get("writableRoots")
            if not isinstance(roots, list) or any(root != request["cwd"] for root in roots):
                raise BackendError("runtime resolved additional writable roots")
            if not sandbox.get("excludeSlashTmp") or not sandbox.get("excludeTmpdirEnvVar"):
                raise BackendError("runtime did not exclude shared temporary write roots")
    thread = response.get("thread") or {}
    if thread.get("environments") != _environments(request):
        raise BackendError("runtime did not confirm the requested local environment and workspace"
                           if request["agent_tools"] == ENGINEERING_PROFILE else
                           "runtime did not confirm disabled environment access")
    if not isinstance(thread.get("id"), str) or not thread["id"]:
        raise BackendError("runtime did not provide a thread identity")
    result["environments"] = thread["environments"]
    result["settings_evidence"] = "app-server thread/start response; not provider-side per-token telemetry"
    result["tool_limit"] = (
        "native shell/file tools use runtime sandbox; command guidance and file ownership are not OS allowlists; "
        "reads outside the workspace and per-command resource limits are not restricted by this protocol; "
        "owned descendants remain reserved until the process executor confirms release"
        if request["agent_tools"] == ENGINEERING_PROFILE else
        "known execution/delegation/connectors disabled; exhaustive builtin tool-free guarantee unavailable")
    return result


def _observe_tool(request, state, item, completed):
    """Retain runtime observations; model-written check claims are not receipts.

    Full event payloads remain in backend-events.jsonl. The result's command
    summary is bounded so long output cannot make the durable result unreadable.
    Native command descendants are covered by the enclosing execution runner,
    not independently admitted or released from these item notifications.
    """
    kind = item.get("type")
    tool_types = {"commandExecution", "fileChange", "mcpToolCall", "dynamicToolCall", "collabAgentToolCall", "webSearch"}
    if kind not in tool_types:
        return
    if request["agent_tools"] != ENGINEERING_PROFILE or kind not in {"commandExecution", "fileChange"}:
        raise BackendError(f"unexpected tool activity: {kind}; result held")
    identity = item.get("id")
    if not isinstance(identity, str) or not identity:
        raise BackendError("runtime tool observation has no item identity")
    records = state["commands" if kind == "commandExecution" else "file_changes"]
    existing = next((record for record in records if record["id"] == identity), None)
    if existing is None:
        if len(records) >= 128:
            raise BackendError("bounded tool observation limit reached; full events retained")
        existing = {"id": identity, "observed_at": time.time()}
        records.append(existing)
    existing.update(status=item.get("status"), completed=completed)
    if completed:
        existing["completed_at"] = time.time()
    if kind == "commandExecution":
        existing.update({key: item.get(key) for key in ("command", "cwd", "exitCode", "durationMs", "processId", "source")})
        output = item.get("aggregatedOutput") or ""
        if not isinstance(output, str) or not isinstance(existing["command"], str):
            raise BackendError("malformed command observation")
        # Output is evidence only to this explicitly reported truncation boundary.
        existing["aggregatedOutput"] = output[:4096]
        existing["output_truncated"] = len(output) > 4096
        if len(existing["command"]) > 8192:
            existing["command"] = existing["command"][:8192]
            existing["command_truncated"] = True
            raise BackendError("command observation exceeds bounded summary; full events retained")
        cwd = existing["cwd"]
        if not isinstance(cwd, str) or not Path(cwd).is_absolute() or not Path(cwd).resolve().is_relative_to(Path(request["cwd"])):
            raise BackendError("command working directory is outside the authorized workspace")
        if existing["status"] == "declined":
            raise BackendError("runtime declined command execution; permission hold retained")
    else:
        changes = item.get("changes")
        if not isinstance(changes, list) or len(changes) > 128:
            raise BackendError("malformed or oversized file-change observation")
        existing["changes"] = [{key: change.get(key) for key in ("path", "kind")} for change in changes if isinstance(change, dict)]
        if len(existing["changes"]) != len(changes):
            raise BackendError("malformed file-change observation")
        if request["sandbox"] != "workspace-write":
            raise BackendError("read-only responsibility attempted a file change")
        for change in existing["changes"]:
            name = change["path"]
            if not isinstance(name, str) or not (Path(request["cwd"]) / name).resolve().is_relative_to(Path(request["cwd"])):
                raise BackendError("file-change observation is outside the authorized workspace")
        if existing["status"] == "declined":
            raise BackendError("runtime declined file change; permission hold retained")
    if len(json.dumps(state, ensure_ascii=False).encode()) > MAX_BYTES * 3 // 4:
        # Do not discard identities or status. Full event output is still retained.
        for record in state["commands"]:
            if record.get("aggregatedOutput"):
                record["aggregatedOutput"] = ""
                record["output_truncated"] = True
        raise BackendError("bounded result evidence limit reached; full events retained")


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
             "observed_settings": {}, "settings_verified": False,
             "configured": {key: request[key] for key in ("model", "effort", "service_tier", "sandbox", "approval", "network", "agent_tools")},
             "operation_id": request["operation_id"], "thread_id": None, "turn_id": None,
             "detail": "startup not yet acknowledged", "commands": [], "file_changes": [],
             "events": str(directory / "backend-events.jsonl")}
    _atomic(destination, state)
    interrupted = [False]
    def on_signal(signum, frame):
        interrupted[0] = True
    previous_signals = {sig: signal.signal(sig, on_signal) for sig in (signal.SIGTERM, signal.SIGINT)}
    client = None
    try:
        if request["agent_tools"] == ENGINEERING_PROFILE and os.environ.get("CODEX_EXEC_SERVER_URL"):
            raise BackendError("engineering local execution refuses CODEX_EXEC_SERVER_URL override")
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
        if isinstance(response, dict):
            # Keep a mismatch's actual safe settings before verification rejects
            # it. Do not copy configuration layers or arbitrary response fields.
            state["observed_settings"] = {key: response.get(key) for key in (
                "model", "modelProvider", "reasoningEffort", "serviceTier", "cwd",
                "runtimeWorkspaceRoots", "sandbox", "approvalPolicy", "activePermissionProfile")}
            thread = response.get("thread")
            state["thread_id"] = thread.get("id") if isinstance(thread, dict) else None
            state["observed_settings"]["environments"] = thread.get("environments") if isinstance(thread, dict) else None
        _atomic(destination, state)
        state["effective"] = verify_effective(request, response)
        state["settings_verified"] = True
        state["detail"] = "thread created; turn not yet acknowledged"
        _atomic(destination, state)
        if interrupted[0]:
            raise BackendError("cancelled before turn dispatch")
        params = {"threadId": state["thread_id"], "model": request["model"], "effort": request["effort"],
                  "serviceTier": request["service_tier"], "serviceTierForTurn": request["service_tier"],
                  "approvalPolicy": "never", "sandboxPolicy": _sandbox_policy(request),
                  "environments": _environments(request), "input": [{"type": "text", "text": request["prompt"]}],
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
                if method in {"item/started", "item/completed"}:
                    item = body.get("item", {})
                    _observe_tool(request, state, item, method == "item/completed")
                    if item.get("type") in {"commandExecution", "fileChange"}:
                        _atomic(destination, state)
                    if method == "item/completed" and item.get("type") == "agentMessage":
                        final_text = item.get("text")
                if method == "turn/completed" and body.get("turn", {}).get("id") == state["turn_id"]:
                    turn = body["turn"]
                    if turn.get("status") != "completed" or cancellation_sent:
                        raise BackendError("turn did not complete normally: " + json.dumps(turn.get("error") or turn.get("status")))
                    if final_text is None:
                        # Some runtimes include final items in the turn snapshot.
                        for item in turn.get("items", []):
                            if item.get("type") == "agentMessage":
                                final_text = item.get("text")
                    for item in turn.get("items", []):
                        _observe_tool(request, state, item, True)
                    if not isinstance(final_text, str):
                        raise BackendError("completed turn has no final text")
                    result = _json(final_text)
                    if not isinstance(result, dict):
                        raise BackendError("final result must be one JSON object")
                    if len(json.dumps({**state, "result": result}, ensure_ascii=False).encode()) > MAX_BYTES:
                        raise BackendError("final result plus observations exceeds bounded evidence size")
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
