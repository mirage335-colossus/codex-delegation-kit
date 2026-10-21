#!/usr/bin/env python3
"""Bounded real-model integration exercise; model calls require authorization.

Supply explicit settings. This creates and retains a private temporary directory
unless --directory selects a new directory. It runs only agent tasks under the
backend's read-only-no-exec profile; it is not a general process-sandbox proof.
No global configuration is changed. No inference runs with --prepare-only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import controller
from controller_store import Store


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def inventory(workspace, args, *, interrupt=False):
    def task(name, prompt, expected, **extra):
        return {"id": name, "kind": "agent", "prompt": prompt,
                "cwd": str(workspace), "preemption": "never",
                "timeout_seconds": args.timeout,
                "resources": {"reasoning": 1, "processes": 1, "cpu": 1, "memory_mb": 0},
                "acceptance": {"type": "json", "equals": expected, "evidence": "answer"}, **extra}
    if interrupt:
        tasks = [task("interrupt-probe", 'Return only JSON with key "numbers" containing the integers from 1 through 2000 in order. Write the explicit array.', {"probe": "never accept a cancelled result"})]
    else:
        tasks = [
            task("diagnose-total", 'Inspect this Python function: def total(xs): return sum(xs[1:]). Its contract is to sum every element. Return only {"bug":"skips_first"} if it skips the first element; otherwise return {"bug":"none"}.', {"bug": "skips_first"}),
            task("diagnose-boundary", 'Inspect this Python function: def nonnegative(x): return x > 0. Its contract includes zero. Return only {"bug":"excludes_zero"} if it excludes zero; otherwise return {"bug":"none"}.', {"bug": "excludes_zero"}),
            task("derive-total-fix", 'The accepted diagnosis says sum(xs[1:]) skips the first input. Give the Python expression summing all inputs. Return only {"expression":"sum(xs)"}.', {"expression": "sum(xs)"}, depends_on=["diagnose-total"]),
        ]
    return {
        "version": 1, "id": "live-interrupt" if interrupt else "live-replenish", "workspace": str(workspace),
        "policy": {
            "capacity": {"reasoning": args.parallel, "processes": args.parallel, "cpu": args.parallel, "memory_mb": 0},
            "allowed_cwds": [str(workspace)], "allowed_executables": [],
            "process_boundary": "inherited",
            "boundary_description": (
                "This fixture admits only the approved agent adapter launcher. "
                "The launcher inherits its invoking OS boundary, which may be the explicitly approved runtime environment. "
                "Each model thread must resolve the narrower read-only, never-approval, network-disabled profile before inference. "
                "This does not establish a sandbox for arbitrary process tasks."
            ),
            "model": args.model, "effort": args.effort, "service_tier": args.service_tier,
            "codex_binary": str(args.codex_binary.resolve()), "agent_profile": "read-only-no-exec",
            "network": False, "sandbox": "read-only", "approval": "never",
            "max_active_seconds": args.timeout * len(tasks) + 20,
            "deadline_seconds": args.timeout * len(tasks) + 30,
        },
        "tasks": tasks,
    }


def state(run):
    store = Store(run)
    try:
        return store.read()
    finally:
        store.close()


def backend_running(run):
    current = state(run)
    for aid, attempt in current["attempts"].items():
        receipt = run / "operations" / aid / "backend-result.json"
        if attempt.get("released") or not receipt.exists():
            continue
        value = json.loads(receipt.read_text())
        if value.get("turn_id") and value.get("detail") == "turn running":
            return aid
    return None


def wait_for(predicate, timeout, description, *, run=None, process=None):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        if run is not None:
            current = state(run)
            if current["holds"]:
                raise RuntimeError(f"{description}: held execution: {json.dumps(current['holds'])}")
        if process is not None and process.poll() is not None:
            raise RuntimeError(f"{description}: controller exited with {process.returncode}")
        time.sleep(.05)
    raise TimeoutError(description)


def launch_controller(run, label):
    stdout = (run.parent / f"{label}.stdout").open("w")
    stderr = (run.parent / f"{label}.stderr").open("w")
    try:
        process = subprocess.Popen([sys.executable, "-B", str(Path(controller.__file__).resolve()), "--run", str(run), "recover"], stdout=stdout, stderr=stderr)
    finally:
        stdout.close()
        stderr.close()
    return process


def reconcile_stopped(run, seconds=8):
    instance = controller.Controller(run)
    try:
        return instance.run(max_seconds=seconds)
    finally:
        instance.close()


def exercise(args):
    directory = args.directory.absolute() if args.directory else Path(tempfile.mkdtemp(prefix="delegation-live-agent-"))
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("live exercise requires an empty directory; existing evidence was preserved")
    workspace = directory / "workspace"
    workspace.mkdir()
    normal = inventory(workspace, args)
    interrupt = inventory(workspace, args, interrupt=True)
    write(directory / "inventory.json", normal)
    write(directory / "interrupt-inventory.json", interrupt)
    evidence = {"validation_kind": "real_model_integration", "directory": str(directory),
                "requested": {"model": args.model, "effort": args.effort, "service_tier": args.service_tier},
                "acceptance": {}, "limitations": [
                    "Independent app-server sessions, not this chat's native subagent tree.",
                    "Resolved runtime settings are checked; provider-side per-token model identity is not exposed.",
                    "Only supplied-context read-only agent work is exercised; arbitrary subprocess sandbox propagation is not proved.",
                    "The three exact-answer checks establish bounded result ingestion, not patch acceptance or general model quality."]}
    if args.prepare_only:
        evidence["validation_kind"] = "prepared_only_no_model_calls"
        write(directory / "evidence.json", evidence)
        print(json.dumps(evidence, indent=2))
        return 0
    runs = []
    children = []
    try:
        run = directory / "run"
        controller.initialize(run, normal)
        runs.append(run)
        child = launch_controller(run, "initial-controller")
        children.append(child)
        print(json.dumps({"phase": "waiting_for_live_turn", "directory": str(directory)}), flush=True)
        original_attempt = wait_for(lambda: backend_running(run), args.timeout, "live turn not observed", run=run, process=child)
        before = state(run)
        # Kill only the controller process this fixture created. Its owned runner
        # and app-server are deliberately left alive for reconciliation.
        child.terminate()
        child.wait(timeout=5)
        recovered = launch_controller(run, "recovered-controller")
        children.append(recovered)
        print(json.dumps({"phase": "controller_restarted", "attempt": original_attempt}), flush=True)
        wait_for(lambda: all(t["status"] == "completed" for t in state(run)["tasks"].values()), args.timeout * 3,
                 "all original answers not completed", run=run, process=recovered)
        recovered.wait(timeout=5)
        after = state(run)
        instance = controller.Controller(run)
        try:
            events = instance.store.events()
            evidence["summary"] = instance.summary()
        finally:
            instance.close()
        claims = [event for event in events if event["kind"] == "claimed"]
        results = [event for event in events if event["kind"] == "observed_result"]
        dependent_claim = next(event for event in claims if event["data"]["task"] == "derive-total-fix")
        predecessor_result = next(event for event in results if event["data"]["task"] == "diagnose-total")
        evidence["acceptance"].update(
            actual_dispatch=True, actual_observation=True, result_ingestion=True,
            automatic_replenishment=dependent_claim["sequence"] > predecessor_result["sequence"],
            controller_restart_preserved_attempt=original_attempt in after["attempts"],
            no_duplicate_attempts=all(len(task["attempts"]) == 1 for task in after["tasks"].values()),
        )
        evidence["restart_snapshot"] = {"attempts_before": list(before["attempts"]), "attempts_after": list(after["attempts"])}
        evidence["model_results"] = {aid: a.get("agent_result") for aid, a in after["attempts"].items()}
        evidence["dispatch_delay_seconds"] = dependent_claim["time"] - predecessor_result["time"]
        stop_run = directory / "interrupt-run"
        controller.initialize(stop_run, interrupt)
        runs.append(stop_run)
        child = launch_controller(stop_run, "interrupt-controller")
        children.append(child)
        interrupted_attempt = wait_for(lambda: backend_running(stop_run), args.timeout, "interruptible live turn not observed", run=stop_run, process=child)
        print(json.dumps({"phase": "requesting_persistent_stop", "attempt": interrupted_attempt}), flush=True)
        controller.control(stop_run, "stop", "bounded live interruption exercise")
        child.wait(timeout=12)
        stopped = state(stop_run)
        count = len(stopped["attempts"])
        # Recovery must observe the durable stop and never dispatch a successor.
        recovery_summary = reconcile_stopped(stop_run)
        stopped_again = state(stop_run)
        receipt = json.loads((stop_run / "operations" / interrupted_attempt / "backend-result.json").read_text())
        events_path = stop_run / "operations" / interrupted_attempt / "backend-events.jsonl"
        protocol_events = [json.loads(line) for line in events_path.read_text().splitlines()] if events_path.exists() else []
        interrupted_seen = any(e.get("method") == "turn/completed" and e.get("params", {}).get("turn", {}).get("status") == "interrupted" for e in protocol_events)
        evidence["acceptance"].update(
            persistent_stop=stopped_again["mode"] == "stopped",
            recovery_respects_stop=len(stopped_again["attempts"]) == count,
            owned_execution_released=all(a.get("released") for a in stopped_again["attempts"].values()),
            protocol_interruption_observed=interrupted_seen,
            cancellation_not_accepted=stopped_again["tasks"]["interrupt-probe"]["acceptance_status"] != "validated",
        )
        evidence["interruption"] = {"receipt": receipt, "summary": recovery_summary}
        evidence["complete"] = all(evidence["acceptance"].values())
        if not evidence["complete"]:
            evidence["limitation"] = "A cancellation race or incomplete protocol observation left at least one requirement unverified; no retry was performed."
        return 0 if evidence["complete"] else 1
    except BaseException as error:
        evidence.update(complete=False, error=str(error))
        return 1
    finally:
        for run in runs:
            try:
                controller.control(run, "stop", "live exercise cleanup")
            except Exception as error:
                evidence.setdefault("cleanup_errors", []).append(str(error))
        for child in children:
            if child.poll() is None:
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.terminate()
                    child.wait(timeout=5)
        for run in runs:
            try:
                evidence.setdefault("cleanup", {})[str(run)] = reconcile_stopped(run)
            except Exception as error:
                evidence.setdefault("cleanup_errors", []).append(str(error))
        # Retain receipts even after a failed cleanup or uncertain execution.
        write(directory / "evidence.json", evidence)
        print(json.dumps(evidence, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--service-tier", required=True)
    parser.add_argument("--codex-binary", type=Path, required=True)
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--parallel", type=int, default=2, choices=range(1, 5), help="explicit share allocated to this bounded exercise")
    parser.add_argument("--timeout", type=float, default=90, help="per-model-call wall deadline, seconds")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.timeout <= 0 or args.timeout > 180:
        parser.error("timeout must be positive and at most 180 seconds")
    return exercise(args)


if __name__ == "__main__":
    raise SystemExit(main())
