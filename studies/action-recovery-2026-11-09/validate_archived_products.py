"""Reconstruct fresh-run products from durable fixtures, then evaluate read-only.

No actor workspace, old grading workspace, or previously recorded command is
used as input. Receipts include the actual new evaluator argv and file hashes.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


STUDY = Path(__file__).resolve().parent
ALLOWED = {
    "cedar": ("pipeline/dispatcher.py", "work/"),
    "marlin": ("cache/catalog.sqlite", "work/"),
    "orchid": ("work/",),
    "harbor": ("deliverables/weekly_summary.json",),
}


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink is not an archived task product: {path}")
        if path.is_file():
            stat = path.stat()
            result[path.relative_to(root).as_posix()] = {
                "sha256": fingerprint(path),
                "bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }
    return result


def replay(run_id, root):
    archive = STUDY / "results" / "runs" / run_id
    manifest_path = archive / "products" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    case = manifest["case_label"]
    if manifest["run_id"] != run_id or case not in ALLOWED:
        raise ValueError("Invalid manifest identity")
    fixture = STUDY / "cases" / "heldout" / case / "participant"
    reference = manifest["participant_snapshot_reference_hashes"]
    fixture_before = snapshot(fixture)
    if {name: item["sha256"] for name, item in fixture_before.items()} != reference:
        raise ValueError("Durable fixture does not match frozen participant hashes")
    products_before = snapshot(archive / "products")
    workspace = root / run_id / "workspace"
    shutil.copytree(fixture, workspace, copy_function=shutil.copy2)
    if snapshot(workspace) != fixture_before:
        raise ValueError("Frozen fixture copy did not preserve bytes and mtimes")
    copied = {}
    for entry in manifest["products"]:
        path = PurePosixPath(entry["path"])
        if path.is_absolute() or ".." in path.parts or path.parts[0] != "products":
            raise ValueError(f"Unsafe product path: {path}")
        relative = PurePosixPath(*path.parts[1:]).as_posix()
        if relative in copied or not any(
            relative.startswith(rule) if rule.endswith("/") else relative == rule
            for rule in ALLOWED[case]
        ):
            raise ValueError(f"Unexpected product path: {relative}")
        expected = {key: entry[key] for key in ("sha256", "bytes", "mtime_ns")}
        if products_before.get(relative) != expected:
            raise ValueError(f"Archived product differs from its manifest: {relative}")
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(archive / path.as_posix(), destination)
        copied[relative] = expected
    before = snapshot(workspace)
    if any(before.get(name) != expected for name, expected in copied.items()):
        raise ValueError("Product overlay failed byte/mtime verification")
    evaluator = STUDY / "cases" / "heldout" / case / "private" / "evaluate.py"
    evaluator_scratch = root / run_id / "evaluator-scratch"
    evaluator_scratch.mkdir()
    argv = [sys.executable, "-B", str(evaluator), str(workspace)]
    environment = dict(
        os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(workspace),
        PARTICIPANT_ROOT=str(workspace), TMPDIR=str(evaluator_scratch),
    )
    completed = subprocess.run(
        argv, cwd=workspace, env=environment, capture_output=True,
        text=True, timeout=30,
    )
    try:
        evaluation = json.loads(completed.stdout)
    except json.JSONDecodeError:
        evaluation = None
    after = snapshot(workspace)
    source_unchanged = snapshot(fixture) == fixture_before
    archive_unchanged = snapshot(archive / "products") == products_before
    workspace_unchanged = before == after
    passed = (
        completed.returncode == 0 and evaluation is not None
        and evaluation.get("accepted") is True
        and workspace_unchanged and source_unchanged and archive_unchanged
    )
    return {
        "run_id": run_id, "case": case,
        "source_condition": manifest["source_condition"],
        "accepted": passed, "fixture": str(fixture),
        "manifest_sha256": fingerprint(manifest_path),
        "fixture_reference_hashes_verified": True,
        "reconstructed_workspace": str(workspace),
        "reconstructed_files": before, "products": copied,
        "evaluator_sha256": fingerprint(evaluator),
        "actual_argv": argv, "actual_cwd": str(workspace),
        "returncode": completed.returncode, "evaluation": evaluation,
        "stdout": completed.stdout, "stderr": completed.stderr,
        "workspace_bytes_and_mtimes_unchanged": workspace_unchanged,
        "durable_fixture_unchanged": source_unchanged,
        "archived_products_unchanged": archive_unchanged,
    }


def main():
    root = Path(tempfile.mkdtemp(prefix="delegation-kit-archive-replay-"))
    records = []
    for number in range(1, 17):
        run_id = f"g{number:03d}"
        try:
            record = replay(run_id, root)
        except Exception as error:
            record = {"run_id": run_id, "accepted": False,
                      "error": f"{type(error).__name__}: {error}"}
        records.append(record)
        print(f"{run_id}: {'PASS' if record['accepted'] else 'FAIL'}", flush=True)
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "script_sha256": fingerprint(Path(__file__)),
        "method": "Durable frozen participant fixtures plus manifest-listed archived products; fresh unique workspace per run; evaluator argv constructed directly; no previous argv, actor workspace, or grader workspace reused. Evaluators verify retained products; no missing products are generated.",
        "scope": "Reproduces archived functional/control acceptance, not original owner handoff completeness or model inference.",
        "replay_root": str(root), "run_count": len(records),
        "accepted_count": sum(record["accepted"] for record in records),
        "all_accepted": all(record["accepted"] for record in records),
        "records": records,
    }
    target = STUDY / "results" / "archive-replay-validation.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(target)
    return 0 if report["all_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
