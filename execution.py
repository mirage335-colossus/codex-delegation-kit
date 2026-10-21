#!/usr/bin/env python3
"""Owned Linux subprocess execution, with receipts that survive controller exit.

The controller admits and sandboxes commands before calling this adapter. This
module is an ownership mechanism, not a sandbox, resource limiter, or authority
to run arbitrary inventory text. A lost runner is deliberately *uncertain*:
absence of a PID or heartbeat cannot prove that all of its work stopped.
"""

from __future__ import annotations

import argparse
import ctypes
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


FINAL = {"completed", "cancelled", "setup_error"}
_RUNNERS: dict[str, subprocess.Popen] = {}


class ExecutionError(ValueError):
    """Invalid specification or conflicting operation ownership."""


def _safe(path):
    path = Path(path).absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ExecutionError(f"symlink is not allowed in operation path: {path}")
    return path


def _read(path):
    path = _safe(path)
    with path.open("r", encoding="utf-8") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ExecutionError("operation record exceeds 1 MiB")
    return json.loads(raw)


def _write(path, data):
    path = _safe(path)
    raw = (json.dumps(data, sort_keys=True, allow_nan=False) + "\n").encode()
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".receipt-", delete=False) as output:
            temporary = Path(output.name)
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _lock(path):
    path = _safe(path)
    return os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600), "r+")


def _canonical(spec):
    required = {"argv", "cwd", "env", "timeout_seconds", "operation_id"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ExecutionError(f"execution spec fields must be exactly {sorted(required)}")
    argv = spec["argv"]
    if (not isinstance(argv, list) or not argv
            or not all(isinstance(v, str) and "\0" not in v for v in argv)
            or not argv[0]):
        raise ExecutionError("argv must be a nonempty list of strings without NULs")
    if not isinstance(spec["cwd"], str) or not Path(spec["cwd"]).is_absolute():
        raise ExecutionError("cwd must be an absolute path")
    env = spec["env"]
    if (not isinstance(env, dict)
            or not all(isinstance(k, str) and k and "=" not in k and "\0" not in k
                       and isinstance(v, str) and "\0" not in v for k, v in env.items())):
        raise ExecutionError("env must contain valid string names and values")
    timeout = spec["timeout_seconds"]
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ExecutionError("timeout_seconds must be finite and positive")
    if not isinstance(spec["operation_id"], str) or not spec["operation_id"].strip():
        raise ExecutionError("operation_id must be nonempty")
    raw = json.dumps(spec, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(raw.encode()) > 1024 * 1024:
        raise ExecutionError("execution spec exceeds 1 MiB")
    return hashlib.sha256(raw.encode()).hexdigest()


def _boot():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def _identity(pid, boot=None):
    """Read Linux start ticks, not a recyclable PID alone."""
    try:
        raw = Path(f"/proc/{int(pid)}/stat").read_text()
        fields = raw[raw.rfind(")") + 2:].split()
        return {"pid": int(pid), "start_ticks": int(fields[19]),
                "boot_id": boot or _boot(), "ppid": int(fields[1]),
                "pgid": int(fields[2]), "session": int(fields[3]), "state": fields[0]}
    except (FileNotFoundError, ProcessLookupError):
        return None


def _matches(saved, current):
    return (isinstance(saved, dict) and current is not None
            and all(saved.get(k) == current.get(k) for k in ("pid", "start_ticks", "boot_id"))
            and current["state"] != "Z")


def _alive(saved):
    return isinstance(saved, dict) and _matches(saved, _identity(saved.get("pid", -1)))


def _descendants(root_pid):
    boot = _boot()
    processes = {}
    for entry in Path("/proc").iterdir():
        if entry.name.isdecimal():
            try:
                info = _identity(int(entry.name), boot)
            except PermissionError:
                continue
            if info is not None:
                processes[info["pid"]] = info
    owned = {root_pid}
    while True:
        added = {pid for pid, info in processes.items() if info["ppid"] in owned} - owned
        if not added:
            break
        owned |= added
    return [processes[pid] for pid in sorted(owned - {root_pid})
            if processes[pid]["state"] != "Z"]


def _signal_owned(identity, sig):
    """pidfd pins the target across the identity check and signal syscall."""
    if identity.get("boot_id") != _boot():
        return False
    try:
        fd = os.pidfd_open(identity["pid"])
    except ProcessLookupError:
        return False
    try:
        if not _matches(identity, _identity(identity["pid"])):
            return False
        signal.pidfd_send_signal(fd, sig)
        return True
    except ProcessLookupError:
        return False
    finally:
        os.close(fd)


def _subreaper():
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise ExecutionError("Linux pidfd support is required for owned cancellation")
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "cannot establish descendant ownership")


def _reap_empty():
    """Only call after Popen.poll() has reaped the main child."""
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return True  # Kernel confirms this subreaper has no child left.
        if pid == 0:
            return False


def launch(directory: Path, spec: dict) -> dict:
    """Fence a new operation before launching. Existing operations only observe."""
    fingerprint = _canonical(spec)
    directory = _safe(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with _lock(directory / "metadata.lock") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (directory / "spec.json").exists():
            if _canonical(_read(directory / "spec.json")) != fingerprint:
                raise ExecutionError("operation already exists with a different specification")
            return observe(directory)
        _write(directory / "spec.json", spec)
        _write(directory / "receipt.json", {
            "version": 1, "operation_id": spec["operation_id"], "spec_sha256": fingerprint,
            "state": "prepared", "released": False, "prepared_at": time.time(),
            "detail": "launch fenced; runner acknowledgement pending",
        })
        try:
            with (directory / "runner.stderr").open("ab") as errors:
                runner = subprocess.Popen(
                    [sys.executable, "-B", str(Path(__file__).resolve()), "_run", str(directory)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=errors,
                    start_new_session=True, close_fds=True,
                )
            _RUNNERS[str(directory)] = runner
        except OSError as error:
            # Popen failed synchronously: no command runner was created.
            _write(directory / "receipt.json", {
                "version": 1, "operation_id": spec["operation_id"], "spec_sha256": fingerprint,
                "state": "setup_error", "released": True, "finished_at": time.time(),
                "returncode": None, "detail": f"runner launch failed: {error}",
            })
    end = time.monotonic() + 0.3
    while time.monotonic() < end:
        result = observe(directory)
        if result["state"] != "prepared":
            return result
        time.sleep(0.01)
    return observe(directory)


def observe(directory: Path) -> dict:
    directory = _safe(directory)
    runner = _RUNNERS.get(str(directory))
    if runner is not None and runner.poll() is not None:
        _RUNNERS.pop(str(directory), None)
    try:
        result = _read(directory / "receipt.json")
    except FileNotFoundError:
        return {"state": "uncertain", "released": False, "detail": "no durable runner receipt"}
    if result.get("state") in FINAL:
        return result
    if result.get("state") == "prepared":
        # The launching controller may have died either side of Popen. No retry.
        if time.time() - result.get("prepared_at", 0) > 2:
            return dict(result, state="uncertain", released=False,
                        detail="launch acknowledgement missing; preserve operation, do not relaunch")
        return result
    if not _alive(result.get("runner")):
        return dict(result, state="uncertain", released=False,
                    detail="owned runner no longer identifiable; descendants may survive")
    return result


def cancel(directory: Path, reason: str) -> dict:
    """Persist a request; the owning runner verifies and terminates its children."""
    if not isinstance(reason, str) or not reason.strip():
        raise ExecutionError("cancellation reason must be nonempty")
    directory = _safe(directory)
    result = observe(directory)
    if result["state"] in FINAL or not directory.is_dir():
        return result
    with _lock(directory / "metadata.lock") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not (directory / "cancel.json").exists():
            _write(directory / "cancel.json", {"reason": reason, "requested_at": time.time()})
    return observe(directory)


def _run(directory):
    directory = _safe(directory)
    with _lock(directory / "execution.lock") as owner:
        try:
            fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        spec = _read(directory / "spec.json")
        receipt = _read(directory / "receipt.json")
        if receipt.get("state") != "prepared":
            return 0
        if receipt.get("spec_sha256") != _canonical(spec):
            raise ExecutionError("prepared specification checksum mismatch")
        receipt.update(state="running", runner=_identity(os.getpid()), started_at=time.time(),
                       detail="owned runner starting command", descendants=[])
        _write(directory / "receipt.json", receipt)
        command = None
        cancel_reason = None
        started = time.monotonic()
        cancellation_started = None
        interrupted = []
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(sig, lambda received, frame: interrupted.append(received))
        try:
            _subreaper()
            if (directory / "cancel.json").exists():
                cancel_reason = _read(directory / "cancel.json")["reason"]
            else:
                with (directory / "stdout").open("wb") as stdout, (directory / "stderr").open("wb") as stderr:
                    command = subprocess.Popen(spec["argv"], cwd=spec["cwd"],
                                               env=dict(os.environ, **spec["env"]),
                                               stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                               start_new_session=True, close_fds=True)
                    receipt.update(command=_identity(command.pid), detail="command running")
                    _write(directory / "receipt.json", receipt)
                    last_recorded = time.monotonic()
                    last_members = None
                    while True:
                        returncode = command.poll()
                        descendants = _descendants(os.getpid())
                        if cancel_reason is None:
                            if (directory / "cancel.json").exists():
                                cancel_reason = _read(directory / "cancel.json")["reason"]
                            elif interrupted:
                                cancel_reason = f"runner received signal {interrupted[0]}"
                            elif time.monotonic() - started >= spec["timeout_seconds"]:
                                cancel_reason = "execution timeout"
                        if cancel_reason is not None:
                            if cancellation_started is None:
                                cancellation_started = time.monotonic()
                                receipt["cancellation_requested_at"] = time.time()
                                receipt["cancellation_reason"] = cancel_reason
                            cancelling_for = time.monotonic() - cancellation_started
                            sig = (signal.SIGKILL if cancelling_for >= 1.5
                                   else signal.SIGTERM)
                            # Give an agent wrapper one second to use its supported
                            # interruption protocol before signalling its server.
                            targets = ([receipt["command"]]
                                       if cancelling_for < 1 and _alive(receipt.get("command"))
                                       else reversed(descendants))
                            for identity in targets:
                                _signal_owned(identity, sig)
                        receipt.update(descendants=descendants, observed_at=time.time(),
                                       detail=(f"cancelling: {cancel_reason}" if cancel_reason else "command running"))
                        members = [(v["pid"], v["start_ticks"]) for v in descendants]
                        marker = (members, cancel_reason)
                        if marker != last_members or time.monotonic() - last_recorded >= 1:
                            _write(directory / "receipt.json", receipt)
                            last_recorded = time.monotonic()
                            last_members = marker
                        if returncode is not None and _reap_empty():
                            break
                        time.sleep(0.05)
                    stdout.flush()
                    stderr.flush()
                    os.fsync(stdout.fileno())
                    os.fsync(stderr.fileno())
            receipt.update(state="cancelled" if cancel_reason else "completed", released=True,
                           returncode=command.returncode if command else None, descendants=[],
                           finished_at=time.time(), detail=cancel_reason or "command and descendants exited")
        except BaseException as error:
            # Only a failure before command creation proves resources are free.
            receipt.update(state="setup_error" if command is None else "uncertain",
                           released=command is None, finished_at=time.time(), returncode=None,
                           detail=f"{type(error).__name__}: {error}")
        _write(directory / "receipt.json", receipt)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["_run"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    return _run(args.directory)


if __name__ == "__main__":
    raise SystemExit(main())
