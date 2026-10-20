"""Synthetic, disposable helper examples; no model calls or service requests.

Run from a source checkout with: python3 examples/demo.py
All evidence strings below describe fixtures, not actual engineering results.
"""

import importlib.util
import json
from pathlib import Path
import tempfile


SPEC = importlib.util.spec_from_file_location(
    "demo_supervisor", Path(__file__).resolve().parents[1] / "supervisor.py"
)
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)


def packet():
    return json.dumps({
        "baseline": "synthetic fixture revision demo-1; no dirty changes",
        "scope": ["fixture.py: reject negative input with ValueError"],
        "contracts": ["Existing nonnegative input behavior stays unchanged"],
        "decisions": ["This example simulates bookkeeping, not model behavior"],
        "acceptance_checks": ["fixture-contract"],
        "allowed_commands": ["synthetic checks only"],
        "stop_conditions": ["Any consequential contract ambiguity"],
        "budget": {"seconds": 60, "max_worker_results": 2},
    })


def result(*, failed=False, verdict=None, new_evidence=False):
    value = {
        "status": "completed",
        "changed_paths": ["fixture.py"],
        "checks": {
            "passed": [] if failed else ["fixture-contract"],
            "failed": ["fixture-contract"] if failed else [],
            "unexecuted": [],
        },
        "evidence": ["synthetic/failed-check.txt" if failed else "synthetic/passed-check.txt"],
    }
    if verdict is not None:
        value["verdict"] = verdict
    if new_evidence:
        value["new_evidence"] = ["synthetic/new-causal-observation.txt"]
    return json.dumps(value, indent=2) + "\n"


def require(value, expected):
    if value != expected:
        raise RuntimeError(f"Expected {expected!r}, got {value!r}")


def demonstrate(store):
    def open_case(name):
        state = ledger.open_assignment(store, name, packet(), now=100)
        require(state["next_action"], "dispatch_luna")

    def record(name, kind, actor, raw, now):
        return ledger.record_result(store, name, kind, actor, raw, now=now)

    open_case("completion")
    state = record("completion", "worker", "luna-demo", result(), 101)
    require(state["next_action"], "strong_review")
    state = record("completion", "review", "supervisor", result(verdict="accept"), 102)
    require(state["state"], "done")

    open_case("repair-then-takeover")
    first_failure = result(failed=True, new_evidence=True)
    state = record("repair-then-takeover", "worker", "luna-demo", first_failure, 101)
    require(state["next_action"], "luna_repair")
    state = record("repair-then-takeover", "worker", "luna-demo", result(failed=True), 102)
    require(state["next_action"], "strong_takeover")
    original = ledger.load_events(store / "repair-then-takeover")[1]["payload_text"]
    require(original, first_failure)
    require(state["repair_used"], True)
    state = record("repair-then-takeover", "strong", "supervisor", result(), 103)
    require(state["state"], "done")

    open_case("review-rejection")
    record("review-rejection", "worker", "luna-demo", result(), 101)
    state = record("review-rejection", "review", "supervisor",
                   result(verdict="substantive_reject"), 102)
    require(state["next_action"], "strong_takeover")

    open_case("interruption")
    state = record("interruption", "interruption", "supervisor", json.dumps({
        "outcome": "blocked", "category": "service_safety_access",
        "operation": "synthetic authorized fixture check",
        "notice": "SYNTHETIC NOTICE: operation unavailable",
        "scope": ["fixture.py"], "evidence": ["synthetic/notice.txt"],
    }), 101)
    require(state["next_action"], "assess_interruption")
    require(state["worker_results"], 0)
    require(state["repair_used"], False)
    return {
        "simulation_only": True,
        "completion": "passing worker output requires independent acceptance",
        "repair_then_takeover": "one repair; repeated failure takes over; original evidence retained",
        "review_rejection": "substantive rejection takes over despite passing checks",
        "interruption": "hold; no repair or worker result spent; no model dispatched",
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="delegation-demo-") as temporary:
        print(json.dumps(demonstrate(Path(temporary) / "state"), indent=2))
