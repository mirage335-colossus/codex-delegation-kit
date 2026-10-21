#!/usr/bin/env python3
"""Prepare disposable engineering examples; never launch a controller or model.

The source fixture deliberately fails total("2,3") == 5. The controller makes
independent private copies, where workers may experiment and propose a patch.
Use --fixture-only for an operator exercise that must construct its own run.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = {
    "totals.py": '''"""Parse comma-separated integers and total every value in order."""


def parse_values(text):
    return [int(piece.strip()) for piece in text.split(",") if piece.strip()]


def aggregate(values):
    return sum(values[1:])


def total(text):
    return aggregate(parse_values(text))
''',
    "test_totals.py": '''import unittest

from totals import parse_values, total


class TotalTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(total(""), 0)

    def test_single_value(self):
        self.assertEqual(total("7"), 7)

    def test_multiple_values(self):
        self.assertEqual(total("2,3"), 5)

    def test_negative_values(self):
        self.assertEqual(total("-4,9,-2"), 3)

    def test_whitespace_and_empty_fields(self):
        self.assertEqual(total(" 2 , , 3 "), 5)

    def test_parser_preserves_values_and_order(self):
        self.assertEqual(parse_values(" 2 , , -3 , 5 "), [2, -3, 5])


if __name__ == "__main__":
    unittest.main()
''',
    ".gitignore": "__pycache__/\n*.pyc\n",
    "AGENTS.md": """# Disposable totals fixture

Use Python's standard library and the existing unittest entrypoint. Preserve
all original assertions and parser behavior. Do not commit, publish, access
network services, or modify global configuration. Managed assignments use a
private controller copy; the original repository remains read-only. Experimental
wrappers belong only in the assignment's declared private scratch scope.
""",
}

READ_COMMANDS = [
    "Read and search actual repository files using bounded local commands.",
    "Run python3 -B -m unittest -v and bounded Python wrappers against the actual totals module.",
]
CHECKS = ["all existing total tests pass", "preserve parser behavior"]


def coding_task(*, depends_on=None):
    task = {
        "id": "correct-total", "role": "worker",
        "prompt": (
            "The actual total('2,3') returns 3, but the contract requires 5. "
            "Inspect the code, reproduce the original failure, and implement the "
            "small correction in your private copy. Preserve every existing test "
            "and parser behavior. Run the unchanged unittest suite. Return the "
            "patch, actual commands/results, original failures and remaining issues. "
            "If prerequisite observations exist, use their discriminating evidence; "
            "agreement among agents is not proof of cause."
        ),
        "write_scope": ["totals.py"],
        "allowed_commands": READ_COMMANDS + [
            "Edit only totals.py in the private copy; do not modify the original source or acceptance tests."
        ],
        "acceptance_checks": CHECKS,
    }
    if depends_on:
        task["depends_on"] = depends_on
    return task


def diagnostic_tasks():
    comparison = {
        "inputs": ["", "7", "2,3", "-4,9,-2", " 2 , , 3 "],
        "expected_totals": [0, 7, 5, 3, 5],
        "environment": "Same supplied source snapshot, local Python 3, standard library, python -B; no network.",
        "original_failure": "total('2,3') returns 3; required result is 5.",
    }
    descriptions = [
        (
            "parser", "Parsing discards or mis-converts one of the comma-separated input values.",
            "Compare parse_values outputs to explicit expected integer lists for the matched inputs, then compare total outputs. Separate parser observations from aggregate behavior.",
            "Inspect actual parsing code. Exercise it directly and report which observations discriminate this hypothesis. Do not correct production code.",
        ),
        (
            "reducer", "Aggregation excludes a value even when given the correct parsed integer list.",
            "Bypass parsing: compare aggregate on [], [7], [2,3] and [-4,9,-2] with Python sum on those exact lists. Retain the original failing case and faithful observed outputs.",
            "Inspect and call the actual aggregate helper. Use a tiny wrapper under scratch/ if useful. Report the observed failure mechanism and uncertainties without applying a correction.",
        ),
        (
            "slow-order", "Parser ordering or retained state changes the values across repeated calls.",
            "Record parsed lists and totals for the matched inputs; wait 45 seconds in one bounded Python command, repeat the same observations, and compare ordering and repeatability. The wait deliberately exposes asynchronous ingestion, not a timing qualification.",
            "Run this slower independent experiment without changing source. Publish your final observation promptly after the repeat. The controller may start dependent engineering work while you are still running.",
        ),
    ]
    tasks = []
    for name, hypothesis, experiment, prompt in descriptions:
        tasks.append({
            "id": name, "role": "scout", "prompt": prompt,
            "hypothesis": hypothesis, "experiment": experiment,
            "comparison": comparison, "write_scope": ["scratch/"],
            "allowed_commands": READ_COMMANDS + [
                "Create and run bounded diagnostic wrappers only under scratch/ in the private copy.",
                "For slow-order only, one time.sleep(45) in its bounded experiment is permitted."
            ],
        })
    return tasks


def inventory(source, args):
    tasks = [coding_task()]
    if args.kind == "diagnosis":
        tasks = diagnostic_tasks() + [coding_task(depends_on=[{
            "task": "reducer", "evidence": "failure_reproduced"
        }])]
    return {
        "version": 1, "id": "engineering-" + args.kind,
        "workspace": str(source),
        "policy": {
            "capacity": {"reasoning": 4, "processes": 4, "cpu": 4, "memory_mb": 0},
            "allowed_cwds": [str(source)], "allowed_executables": [],
            "process_boundary": "inherited",
            "boundary_description": (
                "Authorized disposable fixture. The launcher inherits its invoking OS boundary. "
                "Each agent must resolve the configured restricted workspace sandbox before inference; "
                "only its private copy is writable, and its native commands share the worker allocation. "
                "Command guidance is not an OS allowlist or a per-command resource quota."
            ),
            "model": args.model, "effort": args.effort,
            "service_tier": args.service_tier,
            "codex_binary": str(args.codex_binary.resolve()),
            "agent_profile": "engineering", "sandbox": "workspace-write",
            "approval": "never", "network": False,
            "task_timeout_seconds": 180, "max_active_seconds": 1200,
            "deadline_seconds": 900,
        },
        "tasks": tasks,
    }


def prepare(args):
    directory = args.directory.absolute()
    if any(path.is_symlink() for path in (directory, *directory.parents)):
        raise ValueError("fixture directory must not traverse symlinks")
    if directory.exists():
        raise ValueError("fixture directory must be new; existing files were preserved")
    directory.mkdir(parents=True, mode=0o700)
    source = directory / "source"
    source.mkdir()
    for name, content in FIXTURE.items():
        (source / name).write_text(content, encoding="utf-8")
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    subprocess.run(["git", "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
                    "init", "-q", "--template=", str(source)], check=True,
                   capture_output=True, env=environment, timeout=10)
    result = {
        "validation_kind": "prepared_fixture_only_no_model_calls",
        "source": str(source), "run": str(directory / "run"),
        "observed_defect_to_reproduce": "total('2,3') should equal 5; fixture currently returns 3.",
        "fixture_only": args.fixture_only,
    }
    if not args.fixture_only:
        path = directory / "inventory.json"
        path.write_text(json.dumps(inventory(source, args), indent=2) + "\n")
        command = [sys.executable, "-B", str(ROOT / "controller.py"), "--run", result["run"]]
        result.update(inventory=str(path), commands={
            "start": command + ["start", str(path)],
            **{name: command + [name] for name in ("status", "pause", "resume", "recover", "stop")},
        })
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True, help="new disposable directory; never reused or overwritten")
    parser.add_argument("--kind", choices=["coding", "diagnosis"], default="coding")
    parser.add_argument("--fixture-only", action="store_true", help="create source only; coordinator must construct its own inventory")
    parser.add_argument("--model")
    parser.add_argument("--effort")
    parser.add_argument("--service-tier")
    parser.add_argument("--codex-binary", type=Path)
    args = parser.parse_args()
    if not args.fixture_only:
        for name in ("model", "effort", "service_tier", "codex_binary"):
            if not getattr(args, name):
                parser.error("--" + name.replace("_", "-") + " is required unless --fixture-only")
        if not args.codex_binary.is_absolute() or not args.codex_binary.is_file() or not os.access(args.codex_binary, os.X_OK):
            parser.error("--codex-binary must name an available absolute executable")
    try:
        prepare(args)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, f"engineering example: {error}\n")


if __name__ == "__main__":
    main()
