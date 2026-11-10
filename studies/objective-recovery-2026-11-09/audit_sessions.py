#!/usr/bin/env python3
"""Audit owner-session evidence without exporting private reasoning or metadata."""

from __future__ import annotations

import glob
import json
import re
from pathlib import Path
from typing import Any


SESSION_DIRS = (Path("/home/user/.codex/sessions/2026/11/09"),
                Path("/home/user/.codex/sessions/2026/11/10"))
RUNS_DIR = Path("/tmp/objective-recovery-runs")
OUT = Path(__file__).parent / "results"
TRACE_DIR = OUT / "traces"
PREFIXES = ("/root/objective_u", "/root/objective_help")
CALLSITE_RE = re.compile(r"(?:tools|functions)\.exec_command\s*\(")
HELPER_TOOL_RE = re.compile(r"spawn_agent|followup_task|send_message|agent.*(send|message|task)|helper", re.I)


def load_session(path: Path) -> tuple[str | None, list[dict[str, Any]], list[str]]:
    """Read records, retaining them only if this is a selected agent session."""
    records: list[dict[str, Any]] = []
    issues: list[str] = []
    agent_path: str | None = None
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except Exception as exc:
                if agent_path:
                    issues.append(f"session_jsonl_line_{line_no}: {type(exc).__name__}: {exc}")
                continue
            if not isinstance(record, dict):
                continue
            if record.get("type") == "session_meta":
                payload = record.get("payload")
                candidate = payload.get("agent_path") if isinstance(payload, dict) else None
                if isinstance(candidate, str) and candidate.startswith(PREFIXES):
                    agent_path = candidate
                    records.append(record)
                else:
                    return None, [], []
            elif agent_path:
                records.append(record)
    return agent_path, records, issues


def payload(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("payload")
    return value if isinstance(value, dict) else {}


def string_content(value: Any) -> str:
    """Extract plain text only; omit opaque/non-text content blocks."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [item.get("text", "") for item in value
                 if isinstance(item, dict) and item.get("type") in ("text", "output_text", "input_text")
                 and isinstance(item.get("text"), str)]
        return "\n".join(parts)
    return ""


def audit_calls(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    outputs: dict[str, tuple[str, Any]] = {}
    calls: list[dict[str, Any]] = []
    for record in records:
        p = payload(record)
        if record.get("type") == "response_item" and p.get("type") in ("custom_tool_call_output", "function_call_output"):
            call_id = p.get("call_id")
            if isinstance(call_id, str):
                outputs[call_id] = (string_content(p.get("output")), record.get("timestamp"))

    for record in records:
        p = payload(record)
        if record.get("type") != "response_item" or p.get("type") not in ("custom_tool_call", "function_call"):
            continue
        name = p.get("name")
        source = p.get("input")
        if not isinstance(source, str) and isinstance(source, (dict, list)):
            source = json.dumps(source, ensure_ascii=False)
        if not isinstance(source, str):
            continue
        matches = list(CALLSITE_RE.finditer(source))
        direct = name in ("exec_command", "functions.exec_command")
        if not matches and not direct:
            continue
        call_id = p.get("call_id")
        for match in matches:
            line = source.count("\n", 0, match.start()) + 1
            calls.append({
                "outer_tool": name,
                "line": line,
                "callsite": source[match.start():match.end()],
                "ordinal": record.get("ordinal"),
                "call_id": call_id,
                "timestamp": record.get("timestamp"),
            })
        if direct:
            calls.append({"outer_tool": name, "direct_call": True,
                          "ordinal": record.get("ordinal"), "call_id": call_id,
                          "timestamp": record.get("timestamp")})
    # Runtime call multiplicity cannot be proven from source callsites alone.
    executable_sources = [
        string_content(payload(r).get("input"))
        for r in records
        if r.get("type") == "response_item"
        and payload(r).get("type") in ("custom_tool_call", "function_call")
        and isinstance(payload(r).get("input"), str)
        and (CALLSITE_RE.search(payload(r).get("input", ""))
             or payload(r).get("name") in ("exec_command", "functions.exec_command"))
    ]
    dynamic_risk = any(re.search(r"\b(for|while)\b|\.forEach\s*\(|\bmap\s*\(", src)
                       for src in executable_sources)
    summary = {
        "observed_exec_command_callsites": len(calls),
        "count_basis": "literal tools.exec_command/functions.exec_command callsites plus direct exec_command tool calls",
        "syntactic_count_limit": "Callsites inside loops or dynamically constructed calls may execute multiple times or be missed; outer exec batching can also contain several nested calls.",
        "loop_or_map_syntax_seen": dynamic_risk,
        "calls": calls,
    }
    # Keep a relevant tool trace, excluding all reasoning and unrelated tool traffic.
    traces = []
    relevant_call_ids = {c.get("call_id") for c in calls}
    helper_call_ids: set[str] = set()
    for record in records:
        p = payload(record)
        if record.get("type") != "response_item":
            continue
        if p.get("type") in ("custom_tool_call", "function_call"):
            source = p.get("input")
            if not isinstance(source, str) and isinstance(source, (dict, list)):
                source = json.dumps(source, ensure_ascii=False)
            if isinstance(source, str) and (CALLSITE_RE.search(source)
                                            or p.get("name") in ("exec_command", "functions.exec_command")):
                traces.append({"kind": "tool_input", "tool": p.get("name"),
                               "call_id": p.get("call_id"), "timestamp": record.get("timestamp"),
                               "source": source})
            elif isinstance(source, str) and HELPER_TOOL_RE.search(str(p.get("name", "")) + " " + source):
                call_id = p.get("call_id")
                if isinstance(call_id, str):
                    helper_call_ids.add(call_id)
                traces.append({"kind": "helper_delivery_tool_input", "tool": p.get("name"),
                               "call_id": call_id, "timestamp": record.get("timestamp"),
                               "source": source})
        elif p.get("type") in ("custom_tool_call_output", "function_call_output") and p.get("call_id") in outputs:
            # Retain outputs only for the requested exec and helper-delivery evidence.
            call_id = p.get("call_id")
            if call_id in relevant_call_ids or call_id in helper_call_ids:
                kind = "tool_output" if call_id in relevant_call_ids else "helper_delivery_tool_output"
                traces.append({"kind": kind, "call_id": call_id,
                               "timestamp": outputs[p.get("call_id")][1],
                               "output": outputs[p.get("call_id")][0]})
    return summary, traces


def session_turns(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    turns: dict[str, dict[str, Any]] = {}
    latest_usage: tuple[int, dict[str, Any]] | None = None
    active_turn: str | None = None
    for record in records:
        p = payload(record)
        if record.get("type") == "turn_context":
            entry = turns.setdefault(str(p.get("turn_id", "unknown")), {
                "turn_id": p.get("turn_id"), "observed_exec_command_callsites": 0})
            entry.update({"effective_model_observed": p.get("model"),
                          "effective_effort_observed": p.get("effort")})
        if record.get("type") == "event_msg" and p.get("type") == "task_started":
            turn_id = str(p.get("turn_id", "unknown"))
            entry = turns.setdefault(turn_id, {"turn_id": p.get("turn_id")})
            entry["started_at"] = record.get("timestamp") or p.get("started_at")
            entry.setdefault("observed_exec_command_callsites", 0)
            active_turn = turn_id
        elif record.get("type") == "event_msg" and p.get("type") == "task_complete":
            turn_id = str(p.get("turn_id", "unknown"))
            entry = turns.setdefault(turn_id, {"turn_id": p.get("turn_id")})
            entry["completed_at"] = record.get("timestamp") or p.get("started_at")
            entry.setdefault("observed_exec_command_callsites", 0)
            if active_turn == turn_id:
                active_turn = None
        if record.get("type") == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
            source = p.get("input")
            if not isinstance(source, str) and isinstance(source, (dict, list)):
                source = json.dumps(source, ensure_ascii=False)
            if isinstance(source, str):
                count = len(list(CALLSITE_RE.finditer(source)))
                if p.get("name") in ("exec_command", "functions.exec_command"):
                    count += 1
                if active_turn is not None and count:
                    turns.setdefault(active_turn, {"turn_id": active_turn,
                                                   "observed_exec_command_callsites": 0})[
                                                       "observed_exec_command_callsites"] += count
        if record.get("type") == "token_usage_record":
            ordinal = record.get("ordinal", -1)
            if not isinstance(ordinal, int):
                ordinal = -1
            if latest_usage is None or ordinal >= latest_usage[0]:
                usage = p.get("thread_token_usage")
                if isinstance(usage, dict):
                    # Keep cumulative totals and cached-input subset only.
                    totals = usage.get("total_token_usage", usage)
                    if isinstance(totals, dict):
                        keep = {k: totals[k] for k in (
                            "total_tokens", "input_tokens", "output_tokens",
                            "reasoning_output_tokens", "cached_input_tokens",
                            "cache_read_input_tokens", "cached_input_token_count",
                        ) if k in totals}
                        latest_usage = (ordinal, keep)
    ordered = sorted(turns.values(), key=lambda t: (t.get("started_at", ""), str(t.get("turn_id", ""))))
    return ordered, latest_usage[1] if latest_usage else None


def visible_final_message(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return only an assistant final-channel message, never analysis text."""
    found = None
    for record in records:
        p = payload(record)
        if (record.get("type") == "response_item" and p.get("type") == "message"
                and p.get("role") == "assistant"
                and (p.get("channel") == "final" or p.get("phase") in ("final", "final_answer"))):
            text = string_content(p.get("content"))
            if text:
                found = {"timestamp": record.get("timestamp"), "text": text}
    return found


def first_action(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first recorded tool invocation identity and timestamp."""
    for record in records:
        p = payload(record)
        if record.get("type") == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
            return {"tool": p.get("name"), "timestamp": record.get("timestamp")}
    return None


def requested_settings(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Retain only explicit requested model/effort fields when present."""
    allowed = ("requested_model", "requested_effort", "model_requested", "effort_requested")
    for record in records:
        if record.get("type") == "session_meta":
            p = payload(record)
            return {
                "requested_model": next((p[key] for key in allowed
                                          if key in p and key in ("requested_model", "model_requested")), None),
                "requested_effort": next((p[key] for key in allowed
                                           if key in p and key in ("requested_effort", "effort_requested")), None),
            }
    return {"requested_model": None, "requested_effort": None}


def main() -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    agents: list[dict[str, Any]] = []
    paths = sorted({filename for directory in SESSION_DIRS
                    for filename in glob.glob(str(directory / "*.jsonl"))})
    for filename in paths:
        path = Path(filename)
        agent_path, records, session_issues = load_session(path)
        if not agent_path:
            continue
        agent_id = agent_path.rsplit("/", 1)[-1]
        role = "helper" if agent_id.startswith("objective_help") else "owner"
        turns, usage = session_turns(records)
        call_summary, traces = audit_calls(records)
        final_message = visible_final_message(records)
        # Ignore in-progress participants when producing a sealed snapshot.
        if final_message is None:
            continue
        report = {
            "agent": agent_id,
            "role": role,
            "requested_model_effort_observed": requested_settings(records),
            "first_action": first_action(records),
            "final_visible_message": final_message,
            "turns": turns,
            "observed_exec_command_callsites": call_summary["observed_exec_command_callsites"],
            "observed_exec_command_callsites_by_turn": [
                {"turn_id": turn.get("turn_id"), "count": turn.get("observed_exec_command_callsites", 0)}
                for turn in turns
            ],
            "shell_invocation_count_basis": call_summary["count_basis"],
            "syntactic_count_limit": call_summary["syntactic_count_limit"],
            "loop_or_map_syntax_seen": call_summary["loop_or_map_syntax_seen"],
            "turn_timestamps_are_wall_clock": True,
            "latest_cumulative_thread_usage": usage,
            "usage_scope_note": "Root/coordinator, scout, and review sessions are excluded; only selected participant agent paths are included.",
        }
        agents.append(report)
        trace_path = TRACE_DIR / f"{agent_id}.json"
        trace_path.write_text(json.dumps({"agent": agent_id, "calls": call_summary["calls"],
                                         "exec_tool_trace": traces}, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        if session_issues:
            report["session_record_issues"] = session_issues

    output = {
        "scope": {"session_dates_scanned": [str(path) for path in SESSION_DIRS],
                  "session_meta_agent_path_prefixes": list(PREFIXES),
                  "session_count": len(agents),
                  "account_ids_and_base_instructions_exported": False,
                  "analysis_or_reasoning_exported": False,
                  "count_semantics": "Literal callsite counts are not exhaustive runtime verification; they cannot establish exact executed shell-call totals.",
                  "audit_repair": "Selected only objective owner/helper paths; retained participant final-channel messages and matched exec-related tool source/output evidence."},
        "agent_count": len(agents),
        "agents": agents,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "session-audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")


if __name__ == "__main__":
    main()
