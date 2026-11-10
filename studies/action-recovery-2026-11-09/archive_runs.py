#!/usr/bin/env python3
"""Archive selected finished harness runs without copying raw runtime logs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STUDY_DIR = Path(__file__).resolve().parent
DEFAULT_RUNS_DIR = Path("/tmp/action-recovery-runs")
ARCHIVE_DIR = STUDY_DIR / "results" / "runs"
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$")

# High-confidence secret shapes. Generic words such as "key" or "authorization"
# are not sufficient: generated instructions often mention those concepts.
SECRET_PATTERNS = (
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)://[^/@\s:]+:[^/@\s]+@"),
)
SENSITIVE_KEYS = re.compile(r"(?i)(?:^|[_-])(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|client[_-]?secret|private[_-]?key|credential)(?:$|[_-])")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}: {exc}") from exc


def audit_secrets(value: Any, path: str = "$", hits: list[str] | None = None) -> list[str]:
    """Return locations of likely secrets without printing their values."""
    if hits is None:
        hits = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if SENSITIVE_KEYS.search(str(key)) and child not in (None, "", [], {}):
                hits.append(child_path)
            audit_secrets(child, child_path, hits)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            audit_secrets(child, f"{path}[{index}]", hits)
    elif isinstance(value, str):
        if any(pattern.search(value) for pattern in SECRET_PATTERNS):
            hits.append(path)
    return hits


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def archived_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Keep run provenance while excluding launch environment values."""
    result = dict(metadata)
    execution_spec = result.get("prepared_execution_spec")
    if isinstance(execution_spec, dict):
        result["prepared_execution_spec"] = {
            key: value for key, value in execution_spec.items() if key != "env"
        }
    return result


def archived_request(request: dict[str, Any]) -> dict[str, Any]:
    # Preserve the actual task text and resolved execution settings. The backend
    # binary path and environment are intentionally omitted as machine details.
    fields = (
        "prompt", "model", "effort", "service_tier", "role", "approval",
        "sandbox", "network", "execution_environment", "allowed_commands",
        "write_scope", "resources", "timeout_seconds", "task_id", "operation_id",
    )
    return {key: request[key] for key in fields if key in request}


def archived_collection(collection: dict[str, Any]) -> dict[str, Any]:
    # `backend_collection` embeds event histories. The top-level collected result
    # already contains final decisions, ordinary commands/tool outputs, settings,
    # usage, protected-file audit, release observation, and the actual patch.
    return {
        key: value
        for key, value in collection.items()
        if key not in {"backend_collection", "stdout", "stderr"}
    }


def archive_one(run_id: str, runs_dir: Path, archive_dir: Path) -> Path:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"invalid run ID: {run_id!r}")

    run_root = (runs_dir / run_id).resolve()
    expected_root = runs_dir.resolve() / run_id
    if run_root != expected_root:
        raise ValueError(f"run path escapes runs directory: {run_id}")
    operation = run_root / "operation"
    metadata_path = run_root / "run.json"
    request_path = operation / "backend-request.json"
    result_path = operation / "backend-result.json"
    collection_path = operation / "collection.json"
    instruction_path = operation / "developer-instructions.txt"
    receipt_path = operation / "receipt.json"

    metadata = load_json(metadata_path)
    request = load_json(request_path)
    backend_result = load_json(result_path)
    collection = load_json(collection_path)
    receipt = load_json(receipt_path)
    instructions = instruction_path.read_text(encoding="utf-8")

    if not isinstance(metadata, dict) or metadata.get("run_id") != run_id:
        raise ValueError(f"run metadata ID does not match {run_id}")
    if not isinstance(receipt, dict) or receipt.get("released") is not True:
        raise ValueError(f"run {run_id} has no verified release receipt")
    if receipt.get("state") != "completed":
        raise ValueError(f"run {run_id} is not completed")
    if not isinstance(collection, dict) or collection.get("collection_called") is not True:
        raise ValueError(f"run {run_id} has no completed collection")
    if not isinstance(request, dict) or not isinstance(backend_result, dict):
        raise ValueError(f"run {run_id} has malformed backend artifacts")

    # Inspect all content before writing an archive. In particular, do not copy
    # request or instruction text if it contains a recognizable credential.
    scan_inputs = {
        "run_metadata": metadata,
        "backend_request": request,
        "backend_result": backend_result,
        "collection": collection,
        "release_receipt": receipt,
        "developer_instructions": instructions,
    }
    hits = audit_secrets(scan_inputs)
    if hits:
        raise ValueError(f"possible secrets found in {run_id}: {', '.join(hits)}")

    target = archive_dir / run_id
    if target.exists():
        raise FileExistsError(f"archive already exists: {target}; refusing to overwrite")

    target.mkdir(parents=True)
    outputs: dict[str, Any] = {
        "run-metadata.json": archived_metadata(metadata),
        "request.json": archived_request(request),
        "developer-instructions.txt": instructions,
        "model-result.json": {
            key: backend_result[key]
            for key in ("result", "commands", "configured", "effective", "observed_settings", "settings_verified", "status", "termination_kind", "usage", "file_changes")
            if key in backend_result
        },
        "collection.json": archived_collection(collection),
        "release-receipt.json": receipt,
    }
    try:
        for name, value in outputs.items():
            path = target / name
            if name.endswith(".txt"):
                path.write_text(value, encoding="utf-8")
            else:
                write_json(path, value)

        archived_files = {}
        for name in outputs:
            path = target / name
            archived_files[name] = {"sha256": sha256(path), "bytes": path.stat().st_size}

        source_paths = {
            "run_metadata": metadata_path,
            "backend_request": request_path,
            "backend_result": result_path,
            "collection": collection_path,
            "developer_instructions": instruction_path,
            "release_receipt": receipt_path,
        }
        source_artifacts = {
            name: {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}
            for name, path in source_paths.items()
        }
        source_hashes = metadata.get("source_hashes", {})
        source_snapshots = []
        if isinstance(source_hashes, dict):
            source_snapshots = [
                {"path": path, "sha256": digest}
                for path, digest in sorted(source_hashes.items())
            ]
        manifest = {
            "run_id": run_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "source_artifacts": source_artifacts,
            "source_version_snapshot_hashes": source_snapshots,
            "archived_files": archived_files,
            "omitted": [
                "raw app-server event logs and embedded backend event history",
                "runtime-state databases and sidecars",
                "workspace/source fixtures (source version snapshots are already in the study)",
                "raw process stdout/stderr artifacts and collection base64 stdout/stderr",
                "environment values, binary paths, and unselected backend request fields",
            ],
            "secret_screen": "No high-confidence secret pattern or populated sensitive request key was found in inspected source artifacts.",
        }
        write_json(target / "manifest.json", manifest)
    except BaseException:
        # Keep a failed archive from looking complete; caller can inspect/remove it.
        raise
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_ids", nargs="+", help="completed run IDs to archive")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--archive-dir", type=Path, default=ARCHIVE_DIR)
    args = parser.parse_args(argv)

    seen: set[str] = set()
    try:
        for run_id in args.run_ids:
            if run_id in seen:
                raise ValueError(f"duplicate run ID: {run_id}")
            seen.add(run_id)
            print(archive_one(run_id, args.runs_dir, args.archive_dir))
    except (OSError, ValueError) as exc:
        print(f"archive_runs: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
