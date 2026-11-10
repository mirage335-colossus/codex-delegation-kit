#!/usr/bin/env python3
"""Bounded runner for the action-recovery study's exact-source backend tests.

This is a small experiment harness, not a scheduler or controller. Each run
has an immutable backend source copy, a disjoint private workspace, and owned
execution records outside that workspace. A run is never replayed after its
launch marker exists.
"""
from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import sys
import time

sys.dont_write_bytecode = True


STUDY = Path(__file__).resolve().parent
REPO = STUDY.parents[1]
DEFAULT_RUNS = Path("/tmp/action-recovery-runs")
CODEX = Path("/home/user/.local/bin/codex")
WALL_LIMIT = 240.0
BACKEND_TIMEOUT = 215.0  # execution.py adds ten seconds for owned cleanup
MODEL_POLICY = {
    "model": "gpt-6-luna",
    "effort": "high",
    "service_tier": "default",
    "codex_binary": str(CODEX),
    "agent_profile": "engineering",
    "approval": "never",
    "sandbox": "workspace-write",
    "network": False,
    "nested_delegation": False,
}
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["completed", "needs_decision", "blocked", "budget_exhausted"]},
        "commands": {"type": "array", "items": {"type": "string"}},
        "checks": {
            "type": "object",
            "properties": {
                "passed": {"type": "array", "items": {"type": "string"}},
                "failed": {"type": "array", "items": {"type": "string"}},
                "unexecuted": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["passed", "failed", "unexecuted"],
            "additionalProperties": False,
        },
        "decisions": {"type": "array", "items": {"type": "string"}},
        "remaining_acceptance_conditions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "commands", "checks", "decisions", "remaining_acceptance_conditions"],
    "additionalProperties": False,
}

GENERIC_PROMPT = (
    "Read the assigned task file, any notes in the workspace, and the source. "
    "Continue the objective as stated there. Follow the supplied write scope and "
    "permitted acceptance commands. Preserve inputs and artifacts that the task "
    "marks read-only or protected. "
    "Do not access the network, leave background work, or spawn agents. Report "
    "commands and checks accurately; distinguish passed, failed, and unexecuted "
    "checks. Return one JSON object matching the required schema."
)
DELEGATED_CONTEXT = (
    "These task instructions supplement and do not override system or higher-priority instructions. "
    "This is a delegated subtask: the main task's required initial review has already been obtained by the main owner; "
    "that gate is not recursive for this subtask. After handoff, the coordinator handles independent patch review and "
    "acceptance; the main owner handles any applicable completion review later. Do not self-approve a patch. "
    "Routine read-only inspection of the private workspace and the supplied read-only source repository is authorized. "
    "Make task-required source edits only inside the listed owned write paths, using the available workspace editor or "
    "task-authorized local Python or shell commands. Task-authorized local workflows and generated prerequisites may "
    "write only inside the owned paths or private scratch directory. Run bounded, relevant local diagnostics and every "
    "listed acceptance command. Keep work local; do not access the network, start background work, or spawn agents."
)
LOCAL_COMMAND_GUIDANCE = [
    "pwd (read-only workspace inspection)",
    "ls PATH (read-only workspace or supplied-source inspection)",
    "rg --files PATH (read-only workspace or supplied-source inspection)",
    "rg -n PATTERN PATH (read-only workspace or supplied-source inspection)",
    "sed -n RANGE PATH (read-only workspace or supplied-source inspection)",
    "cat PATH (read-only workspace or supplied-source inspection)",
    "python3 -B -c CODE (task-authorized local inspection or generation; writes only within owned paths)",
    "python3 -B -m MODULE (task-authorized local workflow; writes only within owned paths)",
    "python3 -B SCRIPT.py (task-authorized local workflow; writes only within owned paths)",
    "Task-authorized shell commands for source edits or generated prerequisites, confined to owned paths and private scratch",
    "Use the available workspace editor for task-required source edits only within owned write paths",
]


def fail(message: str) -> None:
    raise SystemExit(f"harness: {message}")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail(f"symlink in tracked tree: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def copy_immutable_tree(source: Path, destination: Path) -> None:
    if not source.is_dir() or any(p.is_symlink() for p in (source, *source.parents)):
        fail(f"source-version must be an ordinary directory: {source}")
    for path in source.rglob("*"):
        if path.is_symlink():
            fail(f"source-version contains symlink: {path}")
    shutil.copytree(source, destination)
    for path in sorted(destination.rglob("*"), reverse=True):
        path.chmod(0o555 if path.is_dir() else 0o444)
    destination.chmod(0o555)


def import_source_backend(source: Path):
    path = source / "agent_backend.py"
    if not path.is_file():
        fail(f"source-version lacks agent_backend.py: {path}")
    spec = importlib.util.spec_from_file_location("action_recovery_exact_agent_backend", path)
    if spec is None or spec.loader is None:
        fail("could not load the exact-source backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_run(run_dir: Path) -> dict:
    try:
        return json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        fail(f"run metadata unavailable or invalid: {error}")


def atomic_json(path: Path, value: object) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def workspace_template(value: str | Path) -> Path:
    candidate = Path(value)
    if candidate.is_dir():
        return candidate.resolve()
    if candidate.is_absolute():
        fail(f"workspace template unavailable: {candidate}")
    for parent in (STUDY / "workspace-templates", STUDY / "fixtures",
                   STUDY / "cases" / "development", STUDY):
        named = parent / candidate
        if named.is_dir():
            return named.resolve()
    fail(f"workspace template path or named fixture unavailable: {value}")


def parse_write_scope(values: list[str] | None, *, smoke_default: bool) -> list[str]:
    items = []
    for value in values or []:
        try:
            parsed = json.loads(value) if value.lstrip().startswith("[") else value
        except ValueError as error:
            fail(f"invalid JSON write-scope list: {error}")
        if isinstance(parsed, list):
            items.extend(parsed)
        else:
            items.append(parsed)
    if values is None and smoke_default:
        items.append("answer.py")
    normalized = []
    for item in items:
        if not isinstance(item, str) or not item.strip():
            fail("write-scope entries must be nonempty strings")
        relative = Path(item)
        if relative.is_absolute() or ".." in relative.parts or ".git" in relative.parts or relative == Path("."):
            fail(f"write scope may not escape the workspace or include Git metadata: {item}")
        name = relative.as_posix().rstrip("/")
        if name and name not in normalized:
            normalized.append(name)
    if "scratch" not in normalized:
        normalized.append("scratch")
    return normalized


def validate_acceptance_command(command: str) -> str:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    try:
        words = list(lexer)
    except ValueError as error:
        fail(f"invalid acceptance command: {error}")
    if any(word and all(char in ";&|<>" for char in word) for word in words):
        fail("acceptance commands may not chain, redirect, or background commands")
    if not words or words[0] != "python3":
        fail("acceptance commands must invoke python3 on a local script or module")
    start = 1 + (1 if len(words) > 1 and words[1] == "-B" else 0)
    if len(words) <= start:
        fail("acceptance command must name a local Python script or module")
    if words[start] == "-m":
        if len(words) <= start + 1 or not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", words[start + 1]):
            fail("acceptance -m target must be a Python module name")
    elif words[start] == "-c":
        if len(words) <= start + 1 or not words[start + 1].strip():
            fail("acceptance -c command must contain Python code")
    else:
        script = Path(words[start])
        if script.is_absolute() or ".." in script.parts or script.suffix != ".py":
            fail("acceptance script must be a relative local .py path")
    return command


def protected_hashes(hashes: dict[str, str], write_scope: list[str]) -> dict[str, str]:
    roots = [Path(name) for name in write_scope]
    return {
        name: value for name, value in hashes.items()
        if not any(Path(name) == root or root in Path(name).parents for root in roots)
    }


def prepare(args) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", args.run_id):
        fail("run id must contain 1-64 ASCII letters, digits, dots, underscores or hyphens")
    root = args.runs_root.absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        fail(f"runs root traverses a symlink: {root}")
    run_dir = root / args.run_id
    if run_dir.exists():
        fail(f"run already exists; preserve and reconcile it instead of reusing identity: {run_dir}")
    if not CODEX.is_file() or not os.access(CODEX, os.X_OK):
        fail(f"configured Codex executable unavailable: {CODEX}")
    version = args.source_version.resolve()
    template = workspace_template(args.workspace_template)
    root.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(mode=0o700)
    source = run_dir / "source-fixture"
    workspace = run_dir / "workspace"
    operation = run_dir / "operation"
    copy_immutable_tree(version, source)
    if not template.is_dir() or any(p.is_symlink() for p in (template, *template.parents)):
        fail(f"workspace template must be an ordinary directory: {template}")
    if any(p.is_symlink() for p in template.rglob("*")):
        fail("workspace template contains symlinks")
    shutil.copytree(template, workspace)
    scratch = workspace / "scratch"
    scratch.mkdir(exist_ok=True)
    before = tree_hashes(workspace)
    operation.mkdir(mode=0o700)
    before_dir = operation / "workspace-before"
    before_dir.mkdir(parents=True, mode=0o700)
    shutil.copytree(workspace, before_dir, dirs_exist_ok=True)
    task_file = Path(args.task_file)
    if task_file.is_absolute() or ".." in task_file.parts:
        fail("task file must be a relative path inside the participant workspace")
    task_name = task_file.as_posix()
    task_path = workspace / task_file
    if not task_path.is_file():
        fail(f"task file unavailable inside workspace: {task_name}")
    prompt_path = args.prompt_file.resolve() if args.prompt_file else None
    if prompt_path is not None:
        if not prompt_path.is_file():
            fail(f"prompt file unavailable: {prompt_path}")
        prompt = prompt_path.read_text(encoding="utf-8")
    elif template == (STUDY / "smoke-template").resolve():
        prompt_path = STUDY / "smoke-prompt.txt"
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt_path = None
        prompt = GENERIC_PROMPT.replace("the assigned task file", task_name)
    prompt = f"{DELEGATED_CONTEXT}\n\n{prompt}"
    smoke_default = template == (STUDY / "smoke-template").resolve()
    write_scope = parse_write_scope(args.write_scope, smoke_default=smoke_default)
    commands = [validate_acceptance_command(command) for command in args.acceptance_command]
    if not commands and smoke_default:
        commands = ["python3 -B -m unittest -v test_answer.py"]
    if not commands:
        fail("provide at least one --acceptance-command")
    task = {
        "id": args.run_id,
        "operation_id": args.run_id,
        "cwd": str(workspace),
        "prompt": prompt,
        "role": args.role,
        "write_scope": write_scope,
        "allowed_commands": [*LOCAL_COMMAND_GUIDANCE, *commands],
        "scratch_directory": str(scratch),
        "timeout_seconds": BACKEND_TIMEOUT,
        "resources": {"cpu": 1, "memory_mb": 256},
        "output_schema": OUTPUT_SCHEMA,
        "source_repository": str(template),
    }
    backend = import_source_backend(source)
    prepared = backend.prepare(task, MODEL_POLICY, operation)
    request = json.loads((operation / "backend-request.json").read_text(encoding="utf-8"))
    developer_instructions = backend._instructions(request)
    (operation / "developer-instructions.txt").write_text(developer_instructions, encoding="utf-8")
    record = {
        "run_id": args.run_id,
        "source_version": str(version),
        "backend_source_fixture": str(source),
        "source_repository": str(template),
        "source_template_sha256_by_path": tree_hashes(template),
        "source_fixture": str(source),
        "source_hashes": tree_hashes(source),
        "backend_source_sha256": digest(source / "agent_backend.py"),
        "workspace": str(workspace),
        "workspace_before_hashes": before,
        "protected_file_hashes_before": protected_hashes(before, write_scope),
        "write_scope": write_scope,
        "task_file": task_name,
        "operation_directory": str(operation),
        "prompt_file": str(prompt_path) if prompt_path else None,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "developer_instructions_sha256": hashlib.sha256(developer_instructions.encode()).hexdigest(),
        "request_sha256": digest(operation / "backend-request.json"),
        "policy": MODEL_POLICY,
        "task": task,
        "prepared_execution_spec": prepared,
        "owner_wall_limit_seconds": WALL_LIMIT,
        "backend_timeout_seconds": BACKEND_TIMEOUT,
        "launch_requested": False,
    }
    atomic_json(run_dir / "run.json", record)
    print(json.dumps({"status": "prepared", "run_directory": str(run_dir),
                      "operation_directory": str(operation),
                      "workspace": str(workspace),
                      "source_sha256": record["backend_source_sha256"],
                      "request_sha256": record["request_sha256"],
                      "model_run_started": False}, sort_keys=True))


def modules(run_dir: Path):
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    import execution
    run = load_run(run_dir)
    backend = import_source_backend(Path(run["source_fixture"]))
    return run, backend, execution


def run(args) -> None:
    run_dir = (args.runs_root / args.run_id).absolute()
    meta, backend, execution = modules(run_dir)
    operation = Path(meta["operation_directory"])
    marker = operation / "launch-requested.json"
    if marker.exists():
        # The process may have died around launch. Observe the same operation;
        # never launch a replacement or replay a model turn.
        launch_record = json.loads(marker.read_text(encoding="utf-8"))
        remaining = max(0.0, float(launch_record["requested_at"]) + WALL_LIMIT - time.time())
        start = time.monotonic() - (WALL_LIMIT - remaining)
        observation = execution.observe(operation)
        action = "observe_existing"
    else:
        requested_at = time.time()
        atomic_json(marker, {"requested_at": requested_at, "spec_sha256": digest(operation / "backend-request.json")})
        start = time.monotonic()
        observation = execution.launch(operation, meta["prepared_execution_spec"])
        action = "launched"
    hard_end = start + WALL_LIMIT
    cancel_at = start + WALL_LIMIT - 5.0
    while not observation.get("released", False) and time.monotonic() < cancel_at:
        time.sleep(min(0.5, max(0.0, cancel_at - time.monotonic())))
        observation = execution.observe(operation)
    if not observation.get("released", False):
        observation = execution.cancel(operation, "study owner wall deadline")
    while not observation.get("released", False) and time.monotonic() < hard_end:
        time.sleep(min(0.25, max(0.0, hard_end - time.monotonic())))
        observation = execution.observe(operation)
    # Retain the execution receipt verbatim. If release is not verified, no
    # backend collection is eligible; a later collect command only observes.
    atomic_json(operation / "last-observation.json", observation)
    print(json.dumps({"action": action, "state": observation.get("state"),
                      "released": observation.get("released", False),
                      "detail": observation.get("detail"),
                      "operation_directory": str(operation),
                      "wall_elapsed_seconds": round(time.monotonic() - start, 3)}, sort_keys=True))


def collect(args) -> None:
    run_dir = (args.runs_root / args.run_id).absolute()
    meta, backend, execution = modules(run_dir)
    operation = Path(meta["operation_directory"])
    observation = execution.observe(operation)
    if not observation.get("released", False):
        result = {"status": "hold", "detail": "owned execution release is unverified; backend.collect was not called",
                  "observation": observation, "collection_called": False}
        atomic_json(operation / "collection-hold.json", result)
        print(json.dumps(result, sort_keys=True))
        return
    collected = backend.collect(operation, observation)
    stdout_path, stderr_path = operation / "stdout", operation / "stderr"
    stdout = stdout_path.read_bytes() if stdout_path.exists() else b""
    stderr = stderr_path.read_bytes() if stderr_path.exists() else b""
    before = Path(operation / "workspace-before")
    workspace = Path(meta["workspace"])
    before_hashes = meta.get("workspace_before_hashes")
    if not isinstance(before_hashes, dict):
        before_hashes = tree_hashes(before)
    after_hashes = tree_hashes(workspace)
    task = meta.get("task", {})
    write_scope = meta.get("write_scope", task.get("write_scope", ["scratch"]))
    protected_before = protected_hashes(before_hashes, write_scope)
    protected_after = protected_hashes(after_hashes, write_scope)
    changes = []
    patch = []
    for name in sorted(set(before_hashes) | set(after_hashes)):
        if before_hashes.get(name) == after_hashes.get(name):
            continue
        prior, current = before / name, workspace / name
        item = {"path": name, "before_sha256": before_hashes.get(name),
                "after_sha256": after_hashes.get(name)}
        changes.append(item)
        try:
            old = prior.read_text(encoding="utf-8").splitlines(keepends=True) if prior.exists() else []
            new = current.read_text(encoding="utf-8").splitlines(keepends=True) if current.exists() else []
            patch.extend(difflib.unified_diff(old, new, fromfile=f"a/{name}", tofile=f"b/{name}"))
        except (OSError, UnicodeError):
            patch.append(f"Binary or unreadable change: {name}\n")
    patch_text = "".join(patch)
    (operation / "actual.patch").write_text(patch_text, encoding="utf-8")
    result = {
        "backend_collection": collected,
        "status": collected.get("status"),
        "detail": collected.get("detail"),
        "result": collected.get("result"),
        "effective": collected.get("effective"),
        "usage": collected.get("usage"),
        "configured": collected.get("configured"),
        "observed_settings": collected.get("observed_settings"),
        "settings_verified": collected.get("settings_verified"),
        "commands": collected.get("commands"),
        "file_changes": collected.get("file_changes"),
        "termination_kind": collected.get("termination_kind"),
        "observation": observation,
        "collection_called": True,
        "backend_result_sha256": digest(operation / "backend-result.json") if (operation / "backend-result.json").is_file() else None,
        "source_backend_sha256": meta["backend_source_sha256"],
        "source_tree_sha256_by_path": meta.get("source_hashes", {}),
        "source_repository": meta.get("source_repository", task.get("source_repository")),
        "source_template_sha256_by_path": meta.get("source_template_sha256_by_path", {}),
        "developer_instructions_sha256": meta["developer_instructions_sha256"],
        "request_sha256": meta["request_sha256"],
        "stdout": {"sha256": hashlib.sha256(stdout).hexdigest(), "base64": base64.b64encode(stdout).decode("ascii")},
        "stderr": {"sha256": hashlib.sha256(stderr).hexdigest(), "base64": base64.b64encode(stderr).decode("ascii")},
        "workspace_before_hashes": before_hashes,
        "workspace_after_hashes": after_hashes,
        "write_scope": write_scope,
        "protected_file_hashes_before": protected_before,
        "protected_file_hashes_after": protected_after,
        "protected_files_unchanged": protected_before == protected_after,
        "protected_files_changed": sorted(
            name for name in set(protected_before) | set(protected_after)
            if protected_before.get(name) != protected_after.get(name)
        ),
        "actual_changes": changes,
        "actual_patch_sha256": hashlib.sha256(patch_text.encode()).hexdigest(),
        "actual_patch": patch_text,
    }
    atomic_json(operation / "collection.json", result)
    print(json.dumps({"status": result["status"], "detail": result["detail"],
                      "collection_called": True, "collection_path": str(operation / "collection.json"),
                      "actual_patch_sha256": result["actual_patch_sha256"]}, sort_keys=True))


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--run-id", required=True)
    p.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS)
    p.add_argument("--source-version", type=Path, default=STUDY / "versions" / "baseline")
    p.add_argument("--workspace-template", default=str(STUDY / "smoke-template"),
                   help="template directory or named fixture (for example: participant)")
    p.add_argument("--task-file", default="TASK.md", help="relative task path inside the workspace")
    p.add_argument("--write-scope", action="append", help="owned workspace path; repeat or pass one JSON string list")
    p.add_argument("--acceptance-command", action="append", default=[],
                   help="bounded Python standard-library unittest command; repeat as needed")
    p.add_argument("--role", choices=["owner", "worker", "scout", "reviewer"], default="owner")
    p.add_argument("--prompt-file", type=Path, help="optional prompt file; otherwise use the task file contract")
    p.set_defaults(func=prepare)
    for name, func in (("run", run), ("collect", collect)):
        p = commands.add_parser(name)
        p.add_argument("--run-id", required=True)
        p.add_argument("--runs-root", type=Path, default=DEFAULT_RUNS)
        p.set_defaults(func=func)
    return root


if __name__ == "__main__":
    options = parser().parse_args()
    options.func(options)
