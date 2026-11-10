"""Stdlib-only evaluator helpers; never imported by participant code."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_scope(participant, manifest_path, editable=(), runtime=(), preserve_mtime=False):
    manifest = json.loads(Path(manifest_path).read_text())
    failures = []
    for name, record in manifest.items():
        path = participant / name
        if name in editable:
            continue
        if not path.is_file():
            failures.append("missing immutable file: " + name)
        elif fingerprint(path) != record["sha256"]:
            failures.append("changed immutable file: " + name)
        elif preserve_mtime and path.stat().st_mtime_ns != record["mtime_ns"]:
            failures.append("rewritten immutable file: " + name)
    for path in participant.rglob("*"):
        if not path.is_file():
            continue
        name = path.relative_to(participant).as_posix()
        if name not in manifest and not any(name.startswith(prefix) for prefix in runtime):
            failures.append("unauthorized file: " + name)
    return failures


def command(participant, arguments):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        result = subprocess.run([sys.executable, *arguments], cwd=participant,
                                env=environment, text=True, capture_output=True, timeout=2)
        return {"argv": [sys.executable, *arguments], "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired as error:
        return {"argv": [sys.executable, *arguments], "returncode": "timeout", "stdout": str(error.stdout or ""), "stderr": str(error.stderr or "")}


class Evaluation:
    def __init__(self, participant):
        self.participant = Path(participant).resolve()
        self.checks = []

    def add(self, name, passed, detail):
        self.checks.append({"id": name, "passed": bool(passed), "detail": detail})

    def execute(self, name, arguments):
        result = command(self.participant, arguments)
        self.add(name, result["returncode"] == 0, result)

    def finish(self):
        accepted = all(check["passed"] for check in self.checks)
        print(json.dumps({"accepted": accepted, "checks": self.checks}, indent=2))
        raise SystemExit(0 if accepted else 1)
