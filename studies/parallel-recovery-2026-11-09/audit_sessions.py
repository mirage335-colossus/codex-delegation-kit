#!/usr/bin/env python3
"""Audit owner-session evidence without exporting private reasoning or metadata."""

from __future__ import annotations

import collections
import glob
import json
import os
import re
from pathlib import Path
from typing import Any


SESSION_DIR = Path("/home/user/.codex/sessions/2026/11/09")
RUNS_DIR = Path("/tmp/delegation-recovery-runs")
OUT = Path(__file__).parent / "results"
TRACE_DIR = OUT / "traces"
PREFIXES = ("/root/trial_q", "/root/transfer_", "/root/projection_help_")
CALLSITE_RE = re.compile(r"(?:tools|functions)\.exec_command\s*\(")


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
                 if isinstance(item, dict) and item.get("type") == "text"
                 and isinstance(item.get("text"), str)]
        return "\n".join(parts)
    return ""


def audit_calls(records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    outputs: dict[str, str] = {}
    calls: list[dict[str, Any]] = []
    for record in records:
        p = payload(record)
        if record.get("type") == "response_item" and p.get("type") in ("custom_tool_call_output", "function_call_output"):
            call_id = p.get("call_id")
            if isinstance(call_id, str):
                outputs[call_id] = string_content(p.get("output"))

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
        elif p.get("type") in ("custom_tool_call_output", "function_call_output") and p.get("call_id") in outputs:
            # Only outputs paired to an exec-related call are retained below.
            if p.get("call_id") in {c.get("call_id") for c in calls}:
                traces.append({"kind": "tool_output", "call_id": p.get("call_id"),
                               "output": outputs[p.get("call_id")]})
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
            entry.update({"model": p.get("model"), "effort": p.get("effort")})
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
                    latest_usage = (ordinal, usage)
    ordered = sorted(turns.values(), key=lambda t: (t.get("started_at", ""), str(t.get("turn_id", ""))))
    return ordered, latest_usage[1] if latest_usage else None


def stage1_report(agent_id: str) -> dict[str, Any]:
    if agent_id.startswith("projection_help_"):
        return {"applicable": False, "reason": "helper sessions do not have owner stage1 self-reports"}
    run_id = agent_id.removeprefix("trial_").removeprefix("transfer_")
    stage1 = RUNS_DIR / run_id / "results" / "stage1.json"
    final = RUNS_DIR / run_id / "results" / "final.json"
    result: dict[str, Any] = {"stage1_path": str(stage1)}
    try:
        parsed = json.loads(stage1.read_text(encoding="utf-8"))
        result["stage1_parse"] = "valid"
        result["stage1_shell_invocations_self_report"] = parsed.get("shell_invocations") if isinstance(parsed, dict) else None
    except Exception as exc:
        result["stage1_parse"] = "error"
        result["stage1_parse_error"] = f"{type(exc).__name__}: {exc}"
    try:
        parsed_final = json.loads(final.read_text(encoding="utf-8"))
        if isinstance(parsed_final, dict):
            chosen = {}
            for key, value in parsed_final.items():
                if not any(x in key.lower() for x in ("invocation", "shell_invocations")):
                    continue
                if isinstance(value, dict):
                    chosen[key] = {k: v for k, v in value.items()
                                   if isinstance(v, (int, float)) and not isinstance(v, bool)}
            result["final_invocation_self_report_fields"] = chosen
    except Exception as exc:
        result["final_parse_error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> None:
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    agents: list[dict[str, Any]] = []
    for filename in sorted(glob.glob(str(SESSION_DIR / "*.jsonl"))):
        path = Path(filename)
        agent_path, records, session_issues = load_session(path)
        if not agent_path:
            continue
        agent_id = agent_path.rsplit("/", 1)[-1]
        role = "helper" if agent_id.startswith("projection_help_") else "owner"
        turns, usage = session_turns(records)
        call_summary, traces = audit_calls(records)
        report = {
            "agent": agent_id,
            "role": role,
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
            "stage1_and_final_self_reports": stage1_report(agent_id),
        }
        agents.append(report)
        trace_path = TRACE_DIR / f"{agent_id}.json"
        trace_path.write_text(json.dumps({"agent": agent_id, "calls": call_summary["calls"],
                                         "exec_tool_trace": traces}, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
        if session_issues:
            report["session_record_issues"] = session_issues

    output = {
        "scope": {"session_meta_agent_path_prefixes": list(PREFIXES),
                  "session_count": len(agents),
                  "account_ids_and_base_instructions_exported": False,
                  "analysis_or_reasoning_exported": False,
                  "count_semantics": "exec_command counts are source callsite counts, not verified executed-command counts; manual callsite inspection is required before interpreting them as budget use.",
                  "audit_repair": "Preserved task_started timestamps when applying turn_context settings; added transfer-owner and projection-helper selection/role handling; retained tool-call timestamps; included direct function_call exec_command records."},
        "agent_count": len(agents),
        "agents": agents,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "session-audit.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")


if __name__ == "__main__":
    main()
