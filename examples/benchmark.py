#!/usr/bin/env python3
"""Deterministic synthetic scheduling exercise; no subprocesses or model calls.

All policies see the same arrivals, useful outcomes, resources and dispatch cost.
Actual duration is private to the simulator, not the adaptive rank function.
This measures the policy, not real engineering productivity or model quality.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scheduling import next_quantum, rank, should_preempt


# Declared before collecting results. Regressions are retained in the report.
TARGETS = {
    "complete_identical_inventory": True,
    "fast_sweep_early_at_least_both_baselines": True,
    "maximum_makespan_ratio_to_fifo": 1.6,
    "maximum_preemptions_per_task": 2,
}
POLICY = {
    "discovery_seconds": 3, "minimum_service_seconds": 2,
    "max_preemptions": 2, "max_quantum_seconds": 96,
    "aging_seconds": 30, "preemption_hysteresis": 1.5,
    "minimum_gain_seconds": 1,
}
DISPATCH_SECONDS = 0.02


def job(name, duration, estimate=None, *, arrival=0, setup=0, restart=0,
        preemption="never", depends=(), origin="original", unlock=0):
    return {
        "id": name, "duration": duration, "estimate_seconds": estimate,
        "arrival": arrival, "setup_seconds": setup, "restart_seconds": restart,
        "preemption": preemption, "depends_on": list(depends), "origin": origin,
        "unlock_value": unlock, "priority": 0, "created_at": arrival,
        "resources": {"processes": 1}, "service_seconds": 0,
        "preemptions": 0, "quantum_seconds": 3, "initial_quantum_seconds": 3,
    }


def fixtures():
    return {
        "fast_sweep": {"capacity": 2, "early_at": 10, "tasks": [
            job("a-slow", 20, 20), job("b-slow", 18, 18),
            *[job(f"quick-{i}", d, d) for i, d in enumerate([2, 1, 3, 4, 2, 1])],
        ]},
        "arriving_fast_restart": {"capacity": 1, "early_at": 12, "tasks": [
            job("slow", 45, 45, restart=2, preemption="restart"),
            *[job(f"arrival-{i}", 1, 1, arrival=4 + i) for i in range(5)],
        ]},
        "nonpreemptible_and_setup": {"capacity": 2, "early_at": 12, "tasks": [
            job("a-nonpreemptible", 25, 25), job("b-prepare", 7, 7, setup=3, unlock=5),
            *[job(f"prepared-{i}", 1 + i % 2, 1 + i % 2, depends=["b-prepare"]) for i in range(5)],
            job("standalone", 2, 2, arrival=2),
        ]},
        "poor_estimates_and_unknown": {"capacity": 2, "early_at": 10, "tasks": [
            job("a-overestimated", 2, 30), job("b-overestimated", 2, 25),
            job("c-underestimated", 18, .5, preemption="restart", restart=2),
            job("d-unknown-slow", 17, None, preemption="restart", restart=1),
            job("e-unknown-fast", 1, None), job("f-accurate", 3, 3),
        ]},
        "continuing_auxiliary_arrivals": {"capacity": 1, "early_at": 15, "tasks": [
            job("original-expensive", 18, 18),
            *[job(f"aux-{i:02d}", 1, 1, arrival=i, origin="followup") for i in range(40)],
        ]},
    }


def simulate(fixture, mode):
    tasks = {task["id"]: copy.deepcopy(task) for task in fixture["tasks"]}
    waiting = set(tasks)
    running = {}
    completed = {}
    first_dispatch = {}
    events = []
    now = 0.0
    idle = wasted = setup = scheduling_cpu = 0.0
    dispatches = 0
    iterations = 0
    capacity = fixture["capacity"]

    def eligible():
        result = []
        for name in sorted(waiting):
            task = tasks[name]
            if task["arrival"] <= now and all(dep in completed for dep in task["depends_on"]):
                task.setdefault("ready_at", max([task["arrival"]] + [completed[dep] for dep in task["depends_on"]]))
                # Do not expose the simulator's true duration to policy code.
                result.append({key: value for key, value in task.items() if key != "duration"})
        return result

    def ordered(ready):
        nonlocal scheduling_cpu
        before = time.process_time()
        if mode == "adaptive":
            result = rank(ready, now, POLICY)
        else:
            result = sorted(ready, key=lambda task: (-task["priority"], task["ready_at"], task["id"]))
        scheduling_cpu += time.process_time() - before
        return result

    while waiting or running:
        iterations += 1
        if iterations > 10000:
            raise RuntimeError("simulation failed to make progress")
        for name, attempt in list(running.items()):
            if attempt["finish"] <= now + 1e-9:
                completed[name] = now
                tasks[name]["service_seconds"] += now - attempt["started_at"]
                events.append({"time": round(now, 4), "task": name, "event": "useful_result"})
                del running[name]

        ready = ordered(eligible())
        if mode == "adaptive" and ready and len(running) == capacity:
            candidate = ready[0]
            # Highest-cost eligible victim first; all slots identical in this model.
            victims = sorted(running, key=lambda name: tasks[name].get("estimate_seconds") or 3, reverse=True)
            for name in victims:
                attempt = running[name]
                active = dict(tasks[name], started_at=attempt["started_at"])
                if should_preempt(active, candidate, now, POLICY):
                    elapsed = now - attempt["started_at"]
                    wasted += elapsed
                    tasks[name]["service_seconds"] += elapsed
                    tasks[name]["preemptions"] += 1
                    tasks[name]["quantum_seconds"] = next_quantum(tasks[name], POLICY)
                    waiting.add(name)
                    del running[name]
                    events.append({"time": round(now, 4), "task": name, "event": "restart_deferral",
                                   "lost_service": round(elapsed, 4)})
                    ready = ordered(eligible())
                    break

        if mode != "fixed_batch" or not running:
            for selected in ready[:capacity - len(running)]:
                name = selected["id"]
                task = tasks[name]
                waiting.remove(name)
                start = now
                overhead = task["setup_seconds"] + (task["restart_seconds"] if task["preemptions"] else 0)
                setup += overhead
                running[name] = {"started_at": start, "finish": start + task["duration"] + overhead + DISPATCH_SECONDS}
                first_dispatch.setdefault(name, start)
                dispatches += 1
                events.append({"time": round(now, 4), "task": name, "event": "dispatch"})

        if not waiting and not running:
            break
        future = [attempt["finish"] for attempt in running.values()]
        future += [task["arrival"] for name, task in tasks.items() if name in waiting and task["arrival"] > now]
        if mode == "adaptive" and waiting:
            future += [attempt["started_at"] + max(POLICY["minimum_service_seconds"], tasks[name]["quantum_seconds"])
                       for name, attempt in running.items()
                       if attempt["started_at"] + max(POLICY["minimum_service_seconds"], tasks[name]["quantum_seconds"]) > now + 1e-9]
        if not future:
            raise ValueError("fixture has missing/cyclic dependencies")
        next_time = min(future)
        idle += max(0, capacity - len(running)) * (next_time - now)
        now = next_time

    useful_times = sorted(completed.values())
    delays = [first_dispatch[name] - tasks[name]["ready_at"] for name in tasks]
    total_service = sum(task["service_seconds"] for task in tasks.values())
    return {
        "kind": "deterministic_simulation", "mode": mode,
        "completed": len(completed), "early_at_seconds": fixture["early_at"],
        "early_useful_results": sum(value <= fixture["early_at"] for value in useful_times),
        "makespan_seconds": round(now, 4),
        "completion_curve": [[round(value, 4), index + 1] for index, value in enumerate(useful_times)],
        "mean_dispatch_delay_seconds": round(statistics.mean(delays), 4),
        "max_dispatch_delay_seconds": round(max(delays, default=0), 4),
        "idle_slot_seconds": round(idle, 4),
        "setup_and_restart_seconds": round(setup, 4),
        "wasted_interrupted_seconds": round(wasted, 4),
        "active_service_seconds": round(total_service, 4),
        "dispatches": dispatches,
        "dispatch_overhead_seconds": round(dispatches * DISPATCH_SECONDS, 4),
        "measured_policy_cpu_seconds": scheduling_cpu,
        "preemptions": {name: task["preemptions"] for name, task in tasks.items() if task["preemptions"]},
        "events": events,
    }


def benchmark():
    results = {}
    checks = []
    for name, fixture in fixtures().items():
        results[name] = {mode: simulate(fixture, mode) for mode in ["fifo", "fixed_batch", "adaptive"]}
        adaptive, fifo = results[name]["adaptive"], results[name]["fifo"]
        complete = all(result["completed"] == len(fixture["tasks"]) for result in results[name].values())
        bounded = adaptive["makespan_seconds"] <= fifo["makespan_seconds"] * TARGETS["maximum_makespan_ratio_to_fifo"]
        preemptions = max(adaptive["preemptions"].values(), default=0) <= TARGETS["maximum_preemptions_per_task"]
        checks.append({"fixture": name, "complete_inventory": complete, "bounded_makespan": bounded,
                       "bounded_preemptions": preemptions})
    fast = results["fast_sweep"]
    early = all(fast["adaptive"]["early_useful_results"] >= fast[mode]["early_useful_results"] for mode in ["fifo", "fixed_batch"])
    return {
        "kind": "deterministic_simulation", "targets_declared_before_measurement": TARGETS,
        "policy": POLICY, "dispatch_cost_seconds_all_modes": DISPATCH_SECONDS,
        "checks": checks, "fast_sweep_early_target": early,
        "passed": early and all(all(value for key, value in item.items() if key != "fixture") for item in checks),
        "results": results,
        "limits": ["Synthetic useful outcomes, not engineering acceptance or live model integration.",
                   "Single homogeneous resource dimension; controller tests cover admission and ownership.",
                   "Poor estimates may regress early results; comparison retains those outcomes.",
                   "Python policy CPU is measured separately; simulated time includes equal dispatch overhead."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = benchmark()
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
