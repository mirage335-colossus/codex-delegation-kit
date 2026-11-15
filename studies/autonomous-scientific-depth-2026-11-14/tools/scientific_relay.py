#!/usr/bin/env python3
"""Cooperative author accounting and exact-request mailbox. Never executes tools.

enqueue/assignment are actor operations. claim/publish are external operator
operations; their control receipts and response mounts are hidden/read-only to
actors. These helpers are not authenticated per-caller enforcement or a scheduler.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import time

_spec = importlib.util.spec_from_file_location("primary_research_meter", Path(__file__).with_name("research_meter.py"))
meter = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(meter)
_storage_spec = importlib.util.spec_from_file_location(
    "relay_artifact_storage", Path(__file__).resolve().parents[3] / "engineering.py")
storage = importlib.util.module_from_spec(_storage_spec)
_storage_spec.loader.exec_module(storage)
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
# Fixed opportunity for the separately admitted neutral paired study route.
# This does not change scientific-v1's existing profile or admission semantics.
NEUTRAL_LIMITS = {"wall_seconds": 8 * 3600, "setup_seconds": 45, "cleanup_seconds": 30,
                  "terminal_collection_seconds": 2,
                  "max_open_children": 11, "max_active_identities": 12, "max_assignments": 32,
                  "web_items": 1000, "browser_actions": 50, "public_calls": 40,
                  "max_protocol_bytes": 512 * 1024 * 1024, "max_evidence_bytes": 512 * 1024 * 1024,
                  "max_message_bytes": 2 * 1024 * 1024, "max_stderr_bytes": 1024 * 1024,
                  "max_relay_bytes": 512 * 1024 * 1024, "max_relay_response_bytes": 16 * 1024 * 1024,
                  "max_relay_requests": 4096, "artifact_lock_seconds": 30, "max_artifact_entries": 65536,
                  "token_cap": None}


def checked(path):
    path = Path(path).absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("symlinked relay path refused")
    return path


def read_snapshot(path, maximum=2 * 1024 * 1024):
    """One bounded descriptor read supplies validation, hashes and copied bytes."""
    fd = os.open(checked(path), os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("relay input is not a regular file")
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("relay input byte ceiling reached")
    return data


def read_json(path, maximum=2 * 1024 * 1024):
    return json.loads(read_snapshot(path, maximum))


def sync_directory(path):
    fd = os.open(checked(path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def service_lock(directory):
    """Shared read-only lock inode: actors, operator and collector serialize here."""
    lock = checked(directory / "relay/inbox/.service.lock").open("rb")
    deadline = time.monotonic() + 2
    try:
        while True:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return lock
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("bounded service closure/publication lock expired")
                time.sleep(.01)
    except BaseException:
        lock.close()
        raise


def close_author(directory, payload):
    """Close delivery synchronously, before child collection or owned cleanup."""
    directory, _ = context(directory, require_live=False)
    # A durable intent immediately stops admissions, including a publisher that
    # already owns the lock but has not reached its final commit check.
    intent = directory / "relay/inbox/closing.json"
    requested = dict(payload, closure_requested_monotonic=time.monotonic())
    if len(meter._json_bytes(requested)) > 2 * 1024 * 1024:
        raise ValueError("service closure snapshot exceeds byte ceiling")
    try:
        exclusive_json(intent, requested)
        sync_directory(intent.parent)
    except FileExistsError:
        pass
    lock = service_lock(directory)
    try:
        terminal = directory / "relay/inbox/terminal.json"
        if terminal.exists():
            closed = read_json(terminal)
        else:
            closed = dict(read_json(intent), closed_monotonic=time.monotonic())
            meter._atomic_json(terminal, closed)
            sync_directory(terminal.parent)
        stopped = directory / "relay/control/stopped.json"
        if not stopped.exists():
            meter._atomic_json(stopped, closed)
            sync_directory(stopped.parent)
        return closed
    finally:
        lock.close()


def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value) or value in {".", ".."}:
        raise ValueError("invalid stable identifier")
    return value


def context(directory, *, require_live=True):
    directory = checked(directory)
    profile = read_json(directory / "support/profile.json")
    if profile.get("name") == "neutral-v1":
        if (set(profile) != {"name", "limits", "relay_services", "max_open_children"}
                or profile["limits"] != NEUTRAL_LIMITS
                or any(type(profile["limits"][key]) is not type(value) for key, value in NEUTRAL_LIMITS.items())
                or type(profile["max_open_children"]) is not int or profile["max_open_children"] != 11
                or profile["relay_services"] != {"public": True, "dependencies": True}
                or any(type(value) is not bool for value in profile["relay_services"].values())):
            raise ValueError("fixed neutral profile limits/services required")
    elif profile.get("name") != "scientific-v1":
        raise ValueError("scientific profile required")
    if require_live:
        timing = read_json(directory / "relay/inbox/dispatch.json")
        if ((directory / "relay/inbox/closing.json").exists()
                or (directory / "relay/inbox/terminal.json").exists()
                or time.monotonic() >= timing["deadline_monotonic"]):
            raise ValueError("episode deadline/terminal reached; no new admission")
    return directory, profile


def exclusive_json(path, value):
    with checked(path).open("xb") as stream:
        stream.write(meter._json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def dependency(parameters):
    if not isinstance(parameters, dict) or set(parameters) != {"path", "purpose"}:
        raise ValueError("dependency needs exact ordinary relative path and purpose")
    path = Path(parameters["path"])
    if (not parameters["purpose"] or path.is_absolute() or not path.parts
            or any(part in {"..", ".git", ".codex", "_ref", "_appraisal", "evaluation"} for part in path.parts)
            or path.name in {"AGENTS.md", "AGENTS.override.md"}):
        raise ValueError("dependency is outside ordinary source scope")
    return path


def units(kind, parameters):
    if kind == "web":
        # This is the root-service web.run envelope, NOT an inferred native tool schema.
        return meter._validate_request(parameters)[1]
    if kind in {"browser", "browser_control", "public"}:
        if (not isinstance(parameters, dict) or set(parameters) != {"tool", "arguments"}
                or not isinstance(parameters["tool"], str) or not parameters["tool"]
                or not isinstance(parameters["arguments"], dict)):
            raise ValueError("public action needs exact tool and argument object")
        return 1  # One explicit action/call; browser control has a separate category.
    if kind == "dependency":
        dependency(parameters)
        return 0
    if kind == "capability" and parameters == {}:
        return 0
    raise ValueError("unsupported relay kind/operation units")


def enqueue(directory, request):
    directory, profile = context(directory)
    if not isinstance(request, dict) or set(request) != {"id", "author", "kind", "parameters"}:
        raise ValueError("request must retain id, author, kind and literal parameters only")
    request_id, author = identifier(request["id"]), identifier(request["author"])
    kind, parameters = request["kind"], request["parameters"]
    if len(meter._json_bytes(request)) > profile["limits"]["max_message_bytes"]:
        raise ValueError("relay request byte ceiling reached")
    count = units(kind, parameters)
    service = "dependencies" if kind == "dependency" else "public"
    if kind != "capability" and not profile["relay_services"][service]:
        raise ValueError("requested service was frozen unavailable")
    target = checked(directory / "work/outbox" / (request_id + ".json"))
    accounting = checked(directory / "work/accounting")
    lock = service_lock(directory)
    try:
        context(directory)
        state_path = accounting / "relay.json"
        state = read_json(state_path) if state_path.exists() else {"requests": {}, "used": {"browser": 0, "public": 0, "browser_control": 0}}
        if request_id in state["requests"] or target.exists():
            raise ValueError("stable request id already used; do not replay")
        if len(state["requests"]) >= profile["limits"]["max_relay_requests"]:
            raise ValueError("relay request ceiling reached")
        ticket = None
        if kind == "web":
            ticket = meter.reserve(accounting / "web", "author", parameters)
        elif kind in {"browser", "public"}:
            key = "browser_actions" if kind == "browser" else "public_calls"
            if state["used"][kind] + count > profile["limits"][key]:
                raise ValueError("shared public-action allocation exceeded")
            state["used"][kind] += count
        elif kind == "browser_control":
            # Initialization/control is recorded separately, never silently treated as content.
            state["used"][kind] += count
        receipt = {"request": request, "operations": count, "web_reservation": ticket,
                   "author_identity": "cooperative; not authenticated", "status": "reserved"}
        state["requests"][request_id] = {"kind": kind, "operations": count,
                                          "web_reservation_id": ticket["id"] if ticket else None}
        # Charge before publication; failed writes and duplicate reservations are never refunded.
        meter._atomic_json(state_path, state)
        context(directory)
        if len(meter._json_bytes(receipt)) > profile["limits"]["max_message_bytes"]:
            raise ValueError("relay receipt byte ceiling reached")
        exclusive_json(target, receipt)
        return receipt
    finally:
        lock.close()


def assignment(directory, author, child, scope):
    directory, profile = context(directory)
    for value in (author, child, scope):
        identifier(value)
    accounting = checked(directory / "work/accounting")
    lock = service_lock(directory)
    try:
        context(directory)
        path = accounting / "assignments.json"
        state = read_json(path) if path.exists() else {"assignments": [], "cooperative": True}
        existing = next((row for row in state["assignments"] if row["child"] == child and row["scope"] == scope), None)
        if existing:
            return dict(existing, continued=True)
        if len(state["assignments"]) >= profile["limits"]["max_assignments"]:
            raise ValueError("shared helper assignment allocation exceeded")
        row = {"author": author, "child": child, "scope": scope, "ordinal": len(state["assignments"]) + 1}
        state["assignments"].append(row)
        context(directory)
        meter._atomic_json(path, state)
        return dict(row, continued=False)
    finally:
        lock.close()


def claim(directory, request_id, scope_review):
    """Operator scope review precedes any action. This does not perform the action."""
    directory, profile = context(directory)
    identifier(request_id)
    if not isinstance(scope_review, str) or not scope_review.strip():
        raise ValueError("operator must reference the applicable scope/permission review")
    lock = service_lock(directory)
    try:
        context(directory)
        data = read_snapshot(directory / "work/outbox" / (request_id + ".json"), profile["limits"]["max_message_bytes"])
        receipt = json.loads(data)
        request = receipt["request"]
        if not isinstance(request, dict) or set(request) != {"id", "author", "kind", "parameters"}:
            raise ValueError("invalid claimed request shape")
        identifier(request["author"])
        if request["id"] != request_id or receipt["operations"] != units(request["kind"], request["parameters"]):
            raise ValueError("request identity/unit mismatch")
        service = "dependencies" if request["kind"] == "dependency" else "public"
        if request["kind"] != "capability" and not profile["relay_services"][service]:
            raise ValueError("requested service unavailable")
        frozen = {"receipt": receipt, "outbox_sha256": hashlib.sha256(data).hexdigest(),
                  "literal_request_hex": data.hex(), "scope_review": scope_review,
                  "execution": "not performed by mailbox; operator must execute exact request once"}
        context(directory)
        exclusive_json(directory / "relay/control" / (request_id + ".claim.json"), frozen)
        return frozen
    finally:
        lock.close()


def publish(directory, request_id, response_file, *, status, actual_operations, actual_calls, request_sha256,
            dependency_file=None):
    """Commit one checked snapshot, or retain it privately after author closure."""
    directory, profile = context(directory, require_live=False)
    identifier(request_id)
    if status not in {"returned", "error", "blocked"} or type(actual_operations) is not int or actual_operations < 0:
        raise ValueError("invalid relay result status/count")
    if type(actual_calls) is not int or actual_calls < 0:
        raise ValueError("actual tool invocation count required")
    data = read_snapshot(response_file, profile["limits"]["max_relay_response_bytes"])
    dependency_data = (read_snapshot(dependency_file, profile["limits"]["max_relay_response_bytes"])
                       if dependency_file is not None else None)
    control = checked(directory / "relay/control")
    lock = service_lock(directory)
    try:
        frozen = read_json(control / (request_id + ".claim.json"), 8 * 1024 * 1024)
        if request_sha256 != frozen["outbox_sha256"]:
            raise ValueError("response is not bound to the claimed exact request")
        target = checked(directory / "relay/inbox" / request_id)
        state_path = control / "published.json"
        state = read_json(state_path) if state_path.exists() else {"bytes": 0, "requests": [], "violations": []}
        if target.exists() or request_id in state["requests"]:
            raise ValueError("response already published or disposition reserved; do not replay")
        receipt, request = frozen["receipt"], frozen["receipt"]["request"]
        relative = None
        if dependency_data is not None:
            if request["kind"] != "dependency" or status != "returned":
                raise ValueError("dependency bytes require a returned ordinary dependency request")
            relative = dependency(request["parameters"])
        size = len(data) + (len(dependency_data) if dependency_data is not None else 0)
        if state["bytes"] + size > profile["limits"]["max_relay_bytes"]:
            raise ValueError("relay aggregate storage ceiling reached")
        violation = actual_operations > receipt["operations"] or (
            request["kind"] in {"web", "browser", "browser_control", "public"} and actual_calls > 1)
        result = {"request": request, "request_sha256": request_sha256, "status": status,
                  "reserved_operations": receipt["operations"], "actual_operations": actual_operations,
                  "actual_tool_calls": actual_calls, "scope_review": frozen["scope_review"],
                  "actual_count_basis": "operator declaration; no tool interception",
                  "response_sha256": hashlib.sha256(data).hexdigest(), "response_bytes": len(data),
                  "allocation_violation": violation}
        if relative is not None:
            dest = directory / "relay/dependencies" / request_id / relative
            result["dependency"] = {"path": str(dest.relative_to(directory)),
                                    "sha256": hashlib.sha256(dependency_data).hexdigest(),
                                    "bytes": len(dependency_data), "requested_source_path": request["parameters"]["path"],
                                    "frozen_source_revision": read_json(directory / "support/project-source.json")["revision"],
                                    "provenance_basis": "operator scope review; bytes hashed, source acquisition not executed by relay"}
        staging = control / (request_id + ".publication")
        response_stage = staging / "response"
        raw_destinations = [response_stage / "response.bin", target / "response.bin"]
        if relative is not None:
            raw_destinations.extend([staging / "dependency" / relative, dest])
        # Admit concrete staging AND final files before any reservation or copy.
        # A refusal leaves the supplied response/dependency and existing evidence
        # intact. It does not refund the earlier acquisition or authorize replay.
        # This is a preflight, not a lock against concurrent ignore-rule changes.
        storage.validate_artifact_paths(raw_destinations)
        # This operator-only reservation retains actual costs even if publication
        # fails. Late results never finish or mutate the locked author meter.
        state["bytes"] += size
        state["requests"].append(request_id)
        state.setdefault("dispositions", {})[request_id] = {"delivery": "pending", "actual_operations": actual_operations,
                                                         "actual_tool_calls": actual_calls}
        if violation:
            state["violations"].append({"id": request_id, "actual_operations": actual_operations,
                                        "reserved_operations": receipt["operations"], "actual_tool_calls": actual_calls})
        meter._atomic_json(state_path, state)
        staging.mkdir()
        response_stage.mkdir()
        with (response_stage / "response.bin").open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if relative is not None:
            dep_stage = staging / "dependency" / relative
            dep_stage.parent.mkdir(parents=True)
            with dep_stage.open("xb") as stream:
                stream.write(dependency_data)
                stream.flush()
                os.fsync(stream.fileno())
            dep_stage.chmod(0o400)
        window = None
        if profile["name"] == "neutral-v1":
            window_path = control / (request_id + ".publication-window.json")
            window = {"request_id": request_id, "dependency_temporarily_visible": False,
                      "qualification": "Live checks and filesystem renames are separate observations, not atomic with the root terminal. Any near-close exposure requires terminal-attribution review; transient dependency visibility is not author attainment."}
            result["publication_window"] = {"audit_path": str(window_path.relative_to(directory)),
                                            "qualification": window["qualification"]}
        result.update(published_to_author=True, disposition="author_delivery")
        exclusive_json(response_stage / "receipt.json", result)
        # Publication/closure share this lock. Revalidate after all private
        # snapshot writes, immediately before the actor-visible rename.
        try:
            context(directory)
        except ValueError as error:
            result.update(published_to_author=False, disposition="late_private_audit",
                          withheld_reason=str(error), audit_path=str(response_stage.relative_to(directory)))
            if relative is not None:
                result["dependency"]["path"] = str(dep_stage.relative_to(directory))
            meter._atomic_json(response_stage / "receipt.json", result)
        if result["published_to_author"]:
            if relative is not None:
                if window is not None:
                    window["dependency_visibility_started_monotonic"] = time.monotonic()
                os.rename(staging / "dependency", directory / "relay/dependencies" / request_id)
                sync_directory(directory / "relay/dependencies")
                if window is not None:
                    window["dependency_visibility_observed_monotonic"] = time.monotonic()
            if window is not None:
                # close_author durably writes its intent before acquiring this
                # lock. Dependency rename/fsync can therefore cross that intent.
                window["final_live_check_started_monotonic"] = time.monotonic()
                try:
                    context(directory)
                except ValueError as error:
                    window["final_live_check_completed_monotonic"] = time.monotonic()
                    window["withheld_reason"] = str(error)
                    if relative is not None:
                        os.rename(directory / "relay/dependencies" / request_id, staging / "dependency")
                        sync_directory(directory / "relay/dependencies")
                        sync_directory(staging)
                        window["dependency_temporarily_visible"] = True
                        window["dependency_withdrawn_observed_monotonic"] = time.monotonic()
                        result["dependency"]["path"] = str(dep_stage.relative_to(directory))
                    result.update(published_to_author=False, disposition="late_private_audit",
                                  withheld_reason=str(error), audit_path=str(response_stage.relative_to(directory)))
                    meter._atomic_json(response_stage / "receipt.json", result)
                else:
                    window["final_live_check_completed_monotonic"] = time.monotonic()
            if result["published_to_author"]:
                if window is not None:
                    window["response_rename_started_monotonic"] = time.monotonic()
                os.rename(response_stage, target)
                sync_directory(target.parent)
                if window is not None:
                    window["response_visibility_observed_monotonic"] = time.monotonic()
                    window["closure_intent_observed_after_visibility"] = (directory / "relay/inbox/closing.json").exists()
                if receipt["web_reservation"]:
                    meter.finish(directory / "work/accounting/web", "author", receipt["web_reservation"]["id"],
                                 "returned" if status == "returned" else "error", result)
        if window is not None:
            window.update(disposition=result["disposition"], published_to_author=result["published_to_author"])
            exclusive_json(window_path, window)
            sync_directory(control)
        state["dispositions"][request_id]["delivery"] = result["disposition"]
        meter._atomic_json(state_path, state)
        return result
    finally:
        lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("enqueue", "assignment", "claim", "publish"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    for key in ("id", "author", "child", "scope", "scope-review", "request-sha256", "status"):
        parser.add_argument("--" + key)
    parser.add_argument("--response", type=Path)
    parser.add_argument("--dependency-file", type=Path)
    parser.add_argument("--actual-operations", type=int)
    parser.add_argument("--actual-calls", type=int)
    args = parser.parse_args()
    try:
        if args.operation == "enqueue":
            result = enqueue(args.directory, read_json(args.request))
        elif args.operation == "assignment":
            result = assignment(args.directory, args.author, args.child, args.scope)
        elif args.operation == "claim":
            result = claim(args.directory, args.id, args.scope_review)
        else:
            result = publish(args.directory, args.id, args.response, status=args.status,
                             actual_operations=args.actual_operations, actual_calls=args.actual_calls,
                             request_sha256=args.request_sha256,
                             dependency_file=args.dependency_file)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, meter.MeterError) as error:
        print(json.dumps({"status": "hold", "error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
