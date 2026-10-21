#!/usr/bin/env python3
"""Self-contained real-process controller exercise; no model calls.

Creates only a disposable temporary workspace unless --directory is supplied.
The result includes an intentional valid failing check and its diagnosis lane.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import controller


def inventory(workspace):
    executable = str(Path(sys.executable).resolve())
    def task(name, code, **extra):
        value = {"id": name, "kind": "process", "argv": [executable, "-c", code],
                 "estimate_seconds": 0.05, "timeout_seconds": 5,
                 "acceptance": {"type": "exit", "success_codes": [0], "failure_codes": [],
                                "category": "test", "evidence": "check"}}
        value.update(extra)
        return value
    known_failure = task("known-failure", "raise SystemExit(7)")
    known_failure["acceptance"]["failure_codes"] = [7]
    return {
        "version": 1, "id": "process-demo", "workspace": str(workspace),
        "policy": {
            "capacity": {"reasoning": 0, "processes": 2, "cpu": 2, "memory_mb": 128},
            "allowed_cwds": [str(workspace)], "allowed_executables": [executable],
            "process_boundary": "inherited",
            "boundary_description": "Local disposable exercise; inherits the invoking shell's filesystem/network restrictions.",
            "network": False, "sandbox": "read-only", "approval": "never",
            "max_active_seconds": 15, "deadline_seconds": 30,
        },
        "tasks": [
            task("slow-independent", "import time; time.sleep(0.3)", estimate_seconds=0.3),
            task("quick-check", "assert 2 + 2 == 4"),
            known_failure,
            task("diagnose-failure", "assert 'failure evidence is usable'",
                 depends_on=[{"task": "known-failure", "evidence": "check"}]),
            task("dependent-check", "assert sum([1, 2, 3]) == 6", depends_on=["quick-check"]),
        ],
    }


def exercise(directory):
    directory = Path(directory).absolute()
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "inventory.json").exists() or (directory / "run").exists():
        raise ValueError("demo needs a fresh directory; existing run and inventory were preserved")
    workspace = directory / "workspace"
    workspace.mkdir(exist_ok=True)
    run = directory / "run"
    source = inventory(workspace)
    (directory / "inventory.json").write_text(json.dumps(source, indent=2) + "\n")
    controller.initialize(run, source)
    instance = controller.Controller(run)
    try:
        summary = instance.run(max_seconds=20)
        if not summary["all_original_complete"] or summary["valid_failures"] != 1:
            raise RuntimeError(f"demo acceptance incomplete: {summary}")
        evidence = {
            "validation_kind": "real_process_execution_no_model_calls",
            "run_directory": str(run),
            "summary": summary,
            "operating_commands": {
                action: shlex.join([sys.executable, str(Path(controller.__file__).resolve()),
                                    "--run", str(run), action])
                for action in ("status", "pause", "resume", "recover", "stop")},
        }
        print(json.dumps(evidence, indent=2))
    except BaseException:
        controller.control(run, "stop", "demo failed; stop owned execution")
        instance.run(max_seconds=6)
        raise
    finally:
        instance.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, help="retain a new demo directory for inspection")
    args = parser.parse_args()
    if args.directory:
        exercise(args.directory)
    else:
        with tempfile.TemporaryDirectory(prefix="delegation-controller-demo-") as directory:
            exercise(directory)


if __name__ == "__main__":
    main()
