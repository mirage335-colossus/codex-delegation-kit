#!/usr/bin/env python3
"""Opt-in, cooperative web-operation budget receipts for the depth study.

This is a local accounting helper, not a security boundary. It accounts only
for calls whose wrapper uses it.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import uuid


WEB_ARRAYS = ("search_query", "open", "click", "find", "screenshot")
RUN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")


class MeterError(Exception):
    pass


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False) + "\n").encode("utf-8")


def _atomic_json(path: Path, value: object) -> None:
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        with tmp.open("xb") as stream:
            stream.write(_json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def _read_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise MeterError(f"cannot read {path.name}: {exc}") from exc


def _validate_request(raw: object) -> tuple[dict, int]:
    if not isinstance(raw, dict):
        raise MeterError("request must be a JSON object")
    allowed = set(WEB_ARRAYS) | {"response_length"}
    extra = set(raw) - allowed
    if extra:
        raise MeterError("unsupported web.run field(s): " + ", ".join(sorted(extra)))
    if "response_length" in raw and raw["response_length"] not in ("short", "medium", "long"):
        raise MeterError("response_length must be short, medium, or long")
    count = 0
    for key in WEB_ARRAYS:
        if key not in raw:
            continue
        if not isinstance(raw[key], list):
            raise MeterError(f"{key} must be an array")
        for item in raw[key]:
            if not isinstance(item, dict):
                raise MeterError(f"each {key} item must be an object")
        count += len(raw[key])
    if count == 0:
        raise MeterError("request must contain at least one web operation")
    return raw, count


def _allocation(root: Path, run: str) -> tuple[dict, int, int]:
    if not RUN_RE.fullmatch(run) or run in (".", ".."):
        raise MeterError("invalid run name")
    data = _read_json(root / "allocations.json")
    if not isinstance(data, dict) or not isinstance(data.get("runs"), dict):
        raise MeterError("allocations.json must contain a runs object")
    total_cap = data.get("total_cap")
    caps = data["runs"]
    if not isinstance(total_cap, int) or isinstance(total_cap, bool) or total_cap < 0:
        raise MeterError("total_cap must be a nonnegative integer")
    if run not in caps:
        raise MeterError("unknown run")
    for name, value in caps.items():
        if not isinstance(name, str) or not RUN_RE.fullmatch(name):
            raise MeterError("allocations contain an invalid run name")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise MeterError(f"invalid cap for run {name}")
    cap = caps[run]
    return data, cap, total_cap


def _load_state(root: Path) -> dict:
    path = root / "meter.json"
    if not path.exists():
        return {"version": 1, "used": {}, "receipts": []}
    state = _read_json(path)
    if (not isinstance(state, dict) or state.get("version") != 1
            or not isinstance(state.get("used"), dict)
            or not isinstance(state.get("receipts"), list)):
        raise MeterError("meter.json has an invalid shape")
    return state


def _locked(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    lock = (root / ".research-meter.lock").open("a+b")
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
    return lock


def _receipt_path(root: Path, receipt_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", receipt_id):
        raise MeterError("invalid receipt id")
    return root / "receipts" / f"{receipt_id}.json"


def reserve(root: Path, run: str, request: object) -> dict:
    normalized, count = _validate_request(request)
    # Preflight before creating the lock file so bad or unknown admissions do
    # not create meter state. Recheck under lock for the actual reservation.
    _allocation(root, run)
    lock = _locked(root)
    try:
        _, run_cap, total_cap = _allocation(root, run)
        state = _load_state(root)
        used_by_run = state["used"]
        used_run = used_by_run.get(run, 0)
        total_used = sum(used_by_run.values())
        if used_run + count > run_cap:
            raise MeterError(f"per-run cap exceeded ({used_run}+{count}>{run_cap})")
        if total_used + count > total_cap:
            raise MeterError(f"total cap exceeded ({total_used}+{count}>{total_cap})")
        receipt_id = uuid.uuid4().hex
        receipt = {"id": receipt_id, "run": run, "request": normalized,
                   "operations": count, "status": "reserved"}
        used_by_run[run] = used_run + count
        state["receipts"].append(receipt_id)
        # Charge atomically before creating the ticket receipt. If the later
        # receipt write fails, no ticket escapes and the quota stays consumed.
        _atomic_json(root / "meter.json", state)
        (root / "receipts").mkdir(exist_ok=True)
        _atomic_json(_receipt_path(root, receipt_id), receipt)
        remaining = {"run": run_cap - used_by_run[run],
                     "total": total_cap - sum(used_by_run.values())}
        return {"admitted": True, "id": receipt_id, "run": run,
                "request": normalized, "operations": count, "remaining": remaining}
    finally:
        lock.close()


def finish(root: Path, run: str, receipt_id: str, status: str,
           metadata: object | None = None) -> dict:
    if not RUN_RE.fullmatch(run) or run in (".", ".."):
        raise MeterError("invalid run name")
    if status not in ("returned", "error"):
        raise MeterError("status must be returned or error")
    if metadata is not None and not isinstance(metadata, dict):
        raise MeterError("metadata must be a JSON object")
    lock = _locked(root)
    try:
        path = _receipt_path(root, receipt_id)
        receipt = _read_json(path)
        if not isinstance(receipt, dict) or receipt.get("run") != run:
            raise MeterError("receipt does not belong to this run")
        if receipt.get("status") != "reserved":
            raise MeterError("receipt is already finished")
        receipt["status"] = status
        if metadata is not None:
            receipt["result"] = metadata
        _atomic_json(path, receipt)
        return {"finished": True, "id": receipt_id, "status": status,
                "operations": receipt["operations"]}
    finally:
        lock.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    reserve_parser = sub.add_parser("reserve")
    reserve_parser.add_argument("--root", required=True, type=Path)
    reserve_parser.add_argument("--run", required=True)
    reserve_parser.add_argument("--request-json", required=True)
    finish_parser = sub.add_parser("finish")
    finish_parser.add_argument("--root", required=True, type=Path)
    finish_parser.add_argument("--run", required=True)
    finish_parser.add_argument("--id", required=True)
    finish_parser.add_argument("--status", choices=("returned", "error"), required=True)
    finish_parser.add_argument("--metadata-json")
    args = parser.parse_args(argv)
    try:
        if args.command == "reserve":
            try:
                request = json.loads(args.request_json)
            except json.JSONDecodeError as exc:
                raise MeterError(f"invalid request JSON: {exc}") from exc
            result = reserve(args.root, args.run, request)
        else:
            metadata = None
            if args.metadata_json is not None:
                try:
                    metadata = json.loads(args.metadata_json)
                except json.JSONDecodeError as exc:
                    raise MeterError(f"invalid metadata JSON: {exc}") from exc
            result = finish(args.root, args.run, args.id, args.status, metadata)
        print(json.dumps(result, sort_keys=True))
        return 0
    except MeterError as exc:
        print(json.dumps({"admitted": False, "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
