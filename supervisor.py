#!/usr/bin/env python3
"""Supervisor-only delegation bookkeeping; this program never spawns agents.

Actor labels are assertions, not authentication or permission enforcement. The
strong supervisor runs this tool and executes its next_action using native tools.
The supplied store is the only state location; no project ownership is inferred.

Packet JSON fields:
  baseline: string
  scope, contracts, decisions, acceptance_checks, allowed_commands,
    stop_conditions: lists of strings
  budget: {"seconds": 600, "max_worker_results": 2} (last field optional)

Worker, review, and strong result JSON fields:
  status: completed | needs_decision | blocked | budget_exhausted
  changed_paths: list of strings
  checks: {"passed": [...], "failed": [...], "unexecuted": [...]}
  evidence: nonempty list of reference strings
  new_evidence: optional list of reference strings
  commands, decisions, remaining_acceptance_conditions: optional lists of strings
Review results additionally require verdict: accept | substantive_reject.
Check lists must partition the original acceptance_checks exactly. A completed
worker result can report failed acceptance checks; it cannot approve integration.

Validation result JSON fields (--kind validation):
  outcome: blocked | ready | unresolved
  command: nonempty string of at most 2048 characters
  evidence: nonempty compact list of reference strings
  original_report: optional exact worker/wrapper text (at most 64 KiB)
  decisions: optional compact list of strings
All JSON inputs, including validation results, are limited to 64 KiB total.
Validation bookkeeping does not independently verify commands or evidence.
blocked pauses ready, repair_allowed, or review_required as validation_paused
with next_action resolve_validation. ready resumes before the original deadline
with verify_existing_work for ready/repair_allowed or independent_review for
review_required. unresolved requires engineering_takeover. Validation never resumes
takeover/done or resets the original deadline, result budget, or repair allowance.

Interruption JSON (--kind interruption), separate from implementation failure:
  outcome: blocked | resolved
  category: model_refusal | model_uncertainty | service_safety_access
  operation: nonempty stable reference to the attempted operation; mark unknown details
  notice: nonempty evidence string; retain exact accessible original text, label
    PARTIAL and include the verbatim available portion when incomplete, or label
    UNAVAILABLE with the evidence limitation when no text is accessible
    (availability labels are not original service notices; never fabricate text)
  scope, evidence: nonempty lists of strings
  model, effort: optional nonempty strings; changed_paths, decisions: optional lists
  resolution_evidence: nonempty list required only for resolved
blocked holds ready/repair/review/validation/takeover as interruption_paused with
assess_interruption. It consumes no worker result/repair and keeps the deadline.
Further blocked records for the same hold retain evidence without resuming it.
Keep operation/scope identity stable; mark uncertainty and append newly available
notice details in evidence/decisions without rewriting original events. A missing
notice description does not authorize a retry or establish the restriction's scope.
Expiry does not turn this hold into capability takeover. resolved requires the
same category/operation/scope and supported external resolution evidence before
the original deadline. This is bookkeeping, not permission or a retry command;
the supervisor must verify actual supported resolution. No agent is spawned.

Examples:
  python3 supervisor.py --store /tmp/example open --assignment example --packet task.json
  python3 supervisor.py --store /tmp/example record --assignment example --kind worker \
      --actor worker-1 --result result.json
  python3 supervisor.py --store /tmp/example record --assignment example --kind review \
      --actor supervisor --result review.json
  python3 supervisor.py --store /tmp/example record --assignment example --kind validation \
      --actor supervisor --result validation-blocked.json
  python3 supervisor.py --store /tmp/example record --assignment example --kind validation \
      --actor supervisor --result validation-ready.json
  python3 supervisor.py --store /tmp/example status --assignment example

The elapsed investigation budget and result limit are enforced at recording and
status checks. This does not monitor a running agent's commands or kill agents.
Each event atomically retains the exact original JSON text and its checksum.
The tool never edits or deletes existing events. Same-ID open always fails.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time


MAX_INPUT_BYTES = 65536
ASSIGNMENT_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,79}\Z")
ACTOR_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
STATUSES = {"completed", "needs_decision", "blocked", "budget_exhausted"}
PACKET_FIELDS = {
    "baseline", "scope", "contracts", "decisions", "acceptance_checks",
    "allowed_commands", "budget", "stop_conditions",
}
RESULT_FIELDS = {
    "status", "changed_paths", "checks", "evidence", "new_evidence", "commands",
    "decisions", "remaining_acceptance_conditions",
}
VALIDATION_OUTCOMES = {"blocked", "ready", "unresolved"}
RECORD_KINDS = {"worker", "review", "strong", "validation", "interruption"}


class LedgerError(ValueError):
    """Invalid input, conflicting operation, or damaged ledger."""


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def string_list(value, name, *, nonempty=False):
    require(isinstance(value, list) and len(value) <= 128, f"{name}: expected a compact list")
    require(not nonempty or bool(value), f"{name}: must not be empty")
    require(all(isinstance(item, str) and item.strip() and len(item) <= 2048
                for item in value), f"{name}: expected nonempty strings of at most 2048 characters")
    require(len(value) == len(set(value)), f"{name}: duplicate items")


def validate_packet(packet):
    require(isinstance(packet, dict) and set(packet) == PACKET_FIELDS,
            f"packet fields must be exactly {', '.join(sorted(PACKET_FIELDS))}")
    require(isinstance(packet["baseline"], str) and packet["baseline"].strip()
            and len(packet["baseline"]) <= 4096, "baseline: expected a compact nonempty string")
    for name in PACKET_FIELDS - {"baseline", "budget"}:
        string_list(packet[name], name, nonempty=name in {
            "scope", "acceptance_checks", "allowed_commands", "stop_conditions"})
    budget = packet["budget"]
    require(isinstance(budget, dict) and "seconds" in budget
            and set(budget) <= {"seconds", "max_worker_results"}, "invalid budget fields")
    require(type(budget["seconds"]) is int and 1 <= budget["seconds"] <= 86400,
            "budget.seconds must be an integer from 1 to 86400")
    require(type(budget.get("max_worker_results", 2)) is int
            and budget.get("max_worker_results", 2) in {1, 2},
            "budget.max_worker_results must be 1 or 2")


def validate_result(result, packet, kind):
    if kind == "interruption":
        required = {"outcome", "category", "operation", "notice", "scope", "evidence"}
        require(isinstance(result, dict) and required <= set(result)
                <= required | {"model", "effort", "changed_paths", "decisions", "resolution_evidence"},
                "invalid interruption result fields")
        require(isinstance(result["outcome"], str) and result["outcome"] in {"blocked", "resolved"},
                "invalid interruption outcome")
        require(isinstance(result["category"], str)
                and result["category"] in {"model_refusal", "model_uncertainty", "service_safety_access"},
                "invalid interruption category")
        for field in ("operation", "notice", "model", "effort"):
            if field in result:
                require(isinstance(result[field], str) and result[field].strip()
                        and len(result[field].encode("utf-8")) <= (MAX_INPUT_BYTES if field == "notice" else 2048),
                        f"{field}: expected a bounded nonempty string")
        for field in ("scope", "evidence", "changed_paths", "decisions", "resolution_evidence"):
            string_list(result.get(field, []), field,
                        nonempty=field in {"scope", "evidence"}
                        or (field == "resolution_evidence" and result["outcome"] == "resolved"))
        require(result["outcome"] == "resolved" or "resolution_evidence" not in result,
                "blocked interruption cannot assert resolution")
        return
    if kind == "validation":
        require(isinstance(result, dict) and {"outcome", "command", "evidence"} <= set(result)
                and set(result) <= {"outcome", "command", "evidence", "original_report", "decisions"},
                "invalid validation result fields")
        require(isinstance(result["outcome"], str) and result["outcome"] in VALIDATION_OUTCOMES,
                "invalid validation outcome")
        require(isinstance(result["command"], str) and result["command"].strip()
                and len(result["command"]) <= 2048, "validation command must be a nonempty string of at most 2048 characters")
        string_list(result["evidence"], "evidence", nonempty=True)
        if "original_report" in result:
            require(isinstance(result["original_report"], str)
                    and len(result["original_report"].encode("utf-8")) <= MAX_INPUT_BYTES,
                    "original_report must be a string of at most 64 KiB")
        string_list(result.get("decisions", []), "decisions")
        return
    required = {"status", "changed_paths", "checks", "evidence"}
    allowed = RESULT_FIELDS.copy()
    if kind == "review":
        required.add("verdict")
        allowed.add("verdict")
    require(isinstance(result, dict) and required <= set(result) <= allowed,
            f"invalid {kind} result fields")
    require(isinstance(result["status"], str) and result["status"] in STATUSES, "invalid result status")
    string_list(result["changed_paths"], "changed_paths")
    string_list(result["evidence"], "evidence", nonempty=True)
    string_list(result.get("new_evidence", []), "new_evidence")
    for field in ("commands", "decisions", "remaining_acceptance_conditions"):
        string_list(result.get(field, []), field)
    checks = result["checks"]
    require(isinstance(checks, dict) and set(checks) == {"passed", "failed", "unexecuted"},
            "checks must contain passed, failed, and unexecuted")
    listed = []
    for key, values in checks.items():
        string_list(values, f"checks.{key}")
        listed.extend(values)
    require(len(listed) == len(set(listed))
            and set(listed) == set(packet["acceptance_checks"]),
            "checks must partition the original acceptance_checks exactly")
    if kind == "review":
        require(isinstance(result["verdict"], str)
                and result["verdict"] in {"accept", "substantive_reject"}, "invalid review verdict")
        if result["verdict"] == "accept":
            require(result["status"] == "completed" and not checks["failed"]
                    and not checks["unexecuted"], "accept requires all original checks passed")


def decode_json(raw):
    require(isinstance(raw, str) and len(raw.encode("utf-8")) <= MAX_INPUT_BYTES,
            "JSON input exceeds 64 KiB")
    def reject_constant(value):
        raise LedgerError(f"non-finite JSON number: {value}")
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_object)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise LedgerError(f"invalid JSON: {exc}") from exc


def read_input(path):
    with Path(path).open("rb") as source:
        raw = source.read(MAX_INPUT_BYTES + 1)
    require(len(raw) <= MAX_INPUT_BYTES, "JSON input exceeds 64 KiB")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LedgerError("JSON input must be UTF-8") from exc


def timestamp(now):
    value = time.time() if now is None else now
    require(type(value) in {int, float} and math.isfinite(value) and 0 <= value <= 253402128000,
            "invalid current timestamp")
    return value


@contextmanager
def locked_store(store):
    store = Path(store).expanduser().resolve()
    store.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (store / ".lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield store


def assignment_path(store, assignment):
    require(isinstance(assignment, str) and ASSIGNMENT_RE.fullmatch(assignment) is not None,
            "assignment must be a stable lowercase identifier of at most 80 characters")
    path = store / assignment
    require(not path.is_symlink(), "assignment path cannot be a symlink")
    return path


def append_event(directory, events, kind, actor, raw, now):
    event = {
        "schema": 1, "sequence": len(events), "kind": kind, "actor": actor,
        "recorded_at": now, "payload_text": raw,
        "payload_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }
    encoded = (json.dumps(event, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    destination = directory / f"{len(events):06d}.json"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".event-", delete=False) as output:
            temporary = Path(output.name)
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
            os.fchmod(output.fileno(), 0o444)
        # link() is atomic and refuses to replace a retained event.
        os.link(temporary, destination)
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return events + [event]


def load_events(directory):
    require(directory.is_dir(), "assignment does not exist")
    files = sorted(directory.glob("*.json"))
    require(bool(files), "assignment is empty or damaged")
    events = []
    for sequence, path in enumerate(files):
        require(path.name == f"{sequence:06d}.json" and not path.is_symlink(),
                "event sequence is damaged")
        event = json.loads(path.read_text(encoding="utf-8"))
        require(isinstance(event, dict) and set(event) == {
            "schema", "sequence", "kind", "actor", "recorded_at", "payload_text", "payload_sha256"
        } and event["schema"] == 1 and event["sequence"] == sequence,
                "event metadata is damaged")
        timestamp(event["recorded_at"])
        require(isinstance(event["payload_text"], str)
                and hashlib.sha256(event["payload_text"].encode("utf-8")).hexdigest()
                == event["payload_sha256"], "original payload checksum mismatch")
        require(sequence == 0 or event["recorded_at"] >= events[-1]["recorded_at"],
                "event timestamps went backwards")
        events.append(event)
    return events


def derive(events, now, *, require_strong_review=False):
    """Replay acceptance, optionally requiring review of takeover-authored work.

    Existing advisory ledgers retain their historical strong-completion rule.
    Engineering controllers opt in for the whole assignment, including replay.
    """
    require(events[0]["kind"] == "open", "ledger must begin with open")
    packet = decode_json(events[0]["payload_text"])
    validate_packet(packet)
    deadline = events[0]["recorded_at"] + packet["budget"]["seconds"]
    state = {
        "state": "ready", "next_action": "dispatch_worker", "reason": "opened",
        "repair_used": False, "worker_results": 0, "worker_actors": [],
        "deadline": deadline, "changed_paths": [], "evidence": [], "awaiting_worker_report": True,
        "validation_resume_state": None,
        "interruption_resume_state": None, "interruption_context": None,
    }
    # Keep legacy repair comparisons unchanged. Interruption-only references
    # retain evidence but cannot make a later implementation repair ineligible.
    repair_comparison_evidence = set()
    # Keep authors separate so the same takeover owner can continue a rejected
    # repair without becoming eligible to approve its own implementation.
    strong_actors = set()

    def expire(at):
        if at >= deadline and state["state"] in {"ready", "repair_allowed", "validation_paused"}:
            takeover("deadline_expired")

    def takeover(reason):
        state.update(state="takeover", next_action="engineering_takeover", reason=reason)

    for event in events[1:]:
        expire(event["recorded_at"])
        kind, actor = event["kind"], event["actor"]
        if kind == "budget":
            require(state["state"] == "takeover" and state["reason"] == "deadline_expired"
                    and actor == "supervisor"
                    and decode_json(event["payload_text"]) == {"reason": "deadline_expired"},
                    "invalid retained budget event")
            continue
        require(kind in RECORD_KINDS, "invalid retained event kind")
        result = decode_json(event["payload_text"])
        validate_result(result, packet, kind)
        require(ACTOR_RE.fullmatch(actor) is not None, "invalid retained actor")
        if kind == "interruption":
            context = {key: result[key] for key in ("category", "operation", "scope")}
            if result["outcome"] == "blocked":
                if state["state"] == "interruption_paused":
                    require(context == state["interruption_context"],
                            "additional evidence must match the held operation")
                else:
                    require(state["state"] in {"ready", "repair_allowed", "review_required",
                                               "validation_paused", "takeover"},
                            "interruption requires an active assignment")
                    state.update(interruption_resume_state=state["state"],
                                 interruption_context=context, state="interruption_paused",
                                 next_action="assess_interruption", reason=result["category"])
            else:
                require(state["state"] == "interruption_paused", "no interruption is awaiting resolution")
                require(context == state["interruption_context"], "resolution must match the held operation")
                require(event["recorded_at"] < deadline, "interruption cannot resume after the original deadline")
                resume = state["interruption_resume_state"]
                actions = {"ready": "verify_existing_work", "repair_allowed": "verify_existing_work",
                           "review_required": "independent_review", "validation_paused": "resolve_validation",
                           "takeover": "engineering_takeover"}
                require(resume in actions, "interruption resume state is damaged")
                state.update(state=resume, next_action=actions[resume], reason="interruption_resolved",
                             interruption_resume_state=None, interruption_context=None)
            state["evidence"] = list(dict.fromkeys(state["evidence"] + result["evidence"]
                                                 + result.get("resolution_evidence", [])))
            state["changed_paths"] = sorted(set(state["changed_paths"] + result.get("changed_paths", [])))
            continue
        if kind == "validation":
            outcome = result["outcome"]
            active_states = {"ready", "repair_allowed", "review_required", "validation_paused"}
            require(state["state"] in active_states,
                    "validation is not allowed after takeover or completion")
            state["evidence"] = list(dict.fromkeys(state["evidence"] + result["evidence"]))
            repair_comparison_evidence.update(result["evidence"])
            if outcome == "blocked":
                if state["state"] != "validation_paused":
                    state["validation_resume_state"] = state["state"]
                state.update(state="validation_paused", next_action="resolve_validation",
                             reason="validation_blocked")
            elif outcome == "ready":
                require(state["state"] == "validation_paused",
                        "validation-ready requires a paused assignment")
                require(event["recorded_at"] < deadline,
                        "validation cannot resume after the original deadline")
                resume = state["validation_resume_state"]
                require(resume in {"ready", "repair_allowed", "review_required"},
                        "validation resume state is damaged")
                if resume == "review_required":
                    state.update(state="review_required", next_action="independent_review",
                                 reason="validation_resolved")
                else:
                    # Validation bookkeeping has not consumed the pending worker report.
                    state.update(state=resume, next_action="verify_existing_work",
                                 reason="validation_resolved")
                state["validation_resume_state"] = None
            else:
                state.update(state="takeover", next_action="engineering_takeover",
                             reason="validation_prerequisite_unresolved",
                             validation_resume_state=None)
            continue
        checks = result["checks"]
        all_passed = result["status"] == "completed" and not checks["failed"] and not checks["unexecuted"]
        previous_evidence = repair_comparison_evidence.copy()
        repair_comparison_evidence.update(result["evidence"] + result.get("new_evidence", []))
        state["changed_paths"] = sorted(set(state["changed_paths"] + result["changed_paths"]))
        state["evidence"] = list(dict.fromkeys(state["evidence"] + result["evidence"]
                                             + result.get("new_evidence", [])))
        if kind == "worker":
            require(state["worker_results"] < packet["budget"].get("max_worker_results", 2),
                    "worker result budget exhausted; worker assignment already stopped; no additional worker result is allowed")
            require(state["state"] in {"ready", "repair_allowed"}
                    or (state["state"] == "takeover" and state["reason"] == "deadline_expired"
                        and state["awaiting_worker_report"]),
                    "Worker assignment already stopped; no additional worker result is allowed")
            state["worker_results"] += 1
            state["worker_actors"].append(actor)
            state["awaiting_worker_report"] = False
            if event["recorded_at"] >= deadline:
                takeover("deadline_expired")
            elif result["status"] != "completed":
                takeover(result["status"])
            elif checks["unexecuted"]:
                takeover("verification_incomplete")
            elif checks["failed"]:
                if state["repair_used"]:
                    takeover("repair_exhausted")
                elif state["worker_results"] >= packet["budget"].get("max_worker_results", 2):
                    takeover("worker_result_budget_exhausted")
                elif not set(result.get("new_evidence", [])) - previous_evidence:
                    takeover("no_new_evidence_for_repair")
                else:
                    state.update(state="repair_allowed", next_action="worker_repair",
                                 reason="one_evidence_based_repair", repair_used=True,
                                 awaiting_worker_report=True)
            else:
                state.update(state="review_required", next_action="independent_review", reason="worker_checks_passed")
        elif kind == "review":
            require(state["state"] == "review_required", "no worker result is awaiting review")
            require(actor not in state["worker_actors"] and actor not in strong_actors,
                    "worker cannot review its own assignment")
            if result["verdict"] == "substantive_reject":
                takeover("substantive_review_rejection")
            else:
                state.update(state="done", next_action="done", reason="independent_review_accepted")
        else:
            require(state["state"] == "takeover", "strong completion requires a takeover")
            require(actor not in state["worker_actors"], "worker cannot approve its own takeover")
            if require_strong_review:
                strong_actors.add(actor)
            if all_passed:
                if require_strong_review:
                    state.update(state="review_required", next_action="independent_review",
                                 reason="strong_checks_passed")
                else:
                    state.update(state="done", next_action="done", reason="strong_takeover_completed",
                                 downstream_guidance="consider_permitted_worker_for_separable_downstream_implementation")
            else:
                takeover("strong_work_incomplete")
    expire(now)
    return packet, state


def summarize(store, assignment, events, now):
    _, state = derive(events, now)
    state.pop("worker_actors")
    state.pop("awaiting_worker_report")
    state.update(
        assignment=assignment,
        deadline_utc=datetime.fromtimestamp(state.pop("deadline"), timezone.utc).isoformat(),
        remaining_seconds=max(0, events[0]["recorded_at"]
                              + decode_json(events[0]["payload_text"])["budget"]["seconds"] - now),
        events=[str(store / assignment / f"{index:06d}.json") for index in range(len(events))],
    )
    return state


def open_assignment(store, assignment, raw_packet, *, now=None):
    now = timestamp(now)
    validate_packet(decode_json(raw_packet))
    with locked_store(store) as store:
        directory = assignment_path(store, assignment)
        require(not directory.exists(), "assignment already exists; retain its original identity and evidence")
        directory.mkdir(mode=0o700)
        events = append_event(directory, [], "open", "supervisor", raw_packet, now)
        return summarize(store, assignment, events, now)


def record_result(store, assignment, kind, actor, raw_result, *, now=None):
    now = timestamp(now)
    require(kind in RECORD_KINDS, "invalid record kind")
    require(isinstance(actor, str) and ACTOR_RE.fullmatch(actor) is not None, "invalid actor label")
    with locked_store(store) as store:
        directory = assignment_path(store, assignment)
        events = load_events(directory)
        require(now >= events[-1]["recorded_at"], "clock went backwards; stop and resolve before recording")
        packet, _ = derive(events, now)
        validate_result(decode_json(raw_result), packet, kind)
        # Validate the complete transition before atomically appending anything.
        prospective = {"kind": kind, "actor": actor, "payload_text": raw_result, "recorded_at": now}
        derive(events + [prospective], now)
        events = append_event(directory, events, kind, actor, raw_result, now)
        return summarize(store, assignment, events, now)


def status(store, assignment, *, now=None):
    now = timestamp(now)
    with locked_store(store) as store:
        events = load_events(assignment_path(store, assignment))
        require(now >= events[-1]["recorded_at"], "clock went backwards; stop and resolve before continuing")
        _, previous = derive(events, events[-1]["recorded_at"])
        _, current = derive(events, now)
        if previous["state"] in {"ready", "repair_allowed", "validation_paused"} \
                and current["reason"] == "deadline_expired":
            events = append_event(store / assignment, events, "budget", "supervisor",
                                  '{"reason":"deadline_expired"}', now)
        return summarize(store, assignment, events, now)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--store", required=True, help="explicit ledger directory")
    commands = parser.add_subparsers(dest="command", required=True)
    opener = commands.add_parser("open", help="open a new stable assignment")
    opener.add_argument("--assignment", required=True)
    opener.add_argument("--packet", required=True)
    recorder = commands.add_parser("record", help="retain an original result and determine the next action")
    recorder.add_argument("--assignment", required=True)
    recorder.add_argument("--kind", choices=sorted(RECORD_KINDS), required=True)
    recorder.add_argument("--actor", required=True)
    recorder.add_argument("--result", required=True)
    query = commands.add_parser("status", help="replay retained evidence and enforce the current deadline")
    query.add_argument("--assignment", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "open":
            result = open_assignment(args.store, args.assignment, read_input(args.packet))
        elif args.command == "record":
            result = record_result(args.store, args.assignment, args.kind, args.actor, read_input(args.result))
        else:
            result = status(args.store, args.assignment)
    except (LedgerError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"supervisor: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
