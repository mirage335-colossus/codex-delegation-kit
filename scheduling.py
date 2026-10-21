"""Small, explainable scheduling heuristics; no execution or mutable state.

The controller supplies only ready tasks, owns capacity and persists decisions.
Estimates are costs to the *next useful result*, not promises of completion.
Strict user priority wins. Within a priority, aging creates an original-work
service opportunity; finite inventories drain, while a continuing stream of
higher-priority arrivals can intentionally delay lower-priority work.
"""

from __future__ import annotations

import math


def _number(value, default=0.0):
    value = default if value is None else value
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("scheduling values must be finite numbers")
    return float(value)


def _setting(policy, name, default):
    # Accept nested controls as well as the original flat public format.
    return _number(policy.get("scheduling", {}).get(name, policy.get(name, default)))


def next_quantum(task, policy):
    """Larger service opportunities after an interrupted attempt, never reset.

    The caller stores the returned quantum when parking. An existing explicit
    quantum is a lower bound. Quanta only trigger reassessment; they are neither
    correctness timeouts nor hard active-service budgets.
    """
    base = max(0.01, _setting(policy, "discovery_seconds", 30.0))
    initial = max(0.01, _number(task.get("initial_quantum_seconds"), base))
    interruptions = max(0, int(_number(task.get("preemptions"))))
    maximum = max(initial, _setting(policy, "max_quantum_seconds", 3600.0))
    progressive = min(maximum, initial * (2 ** min(interruptions, 20)))
    return max(progressive, _number(task.get("quantum_seconds"), initial))


def estimated_cost(task, policy):
    """Conservative restart cost without subtracting censored elapsed time.

    A censored attempt is only a lower bound. When an old estimate was exceeded,
    use at least twice observed service and disclose that the estimate changed.
    Explicit fresh remaining-work observations can be supplied by the controller
    as ``remaining_seconds`` with ``remaining_observed_at``.
    """
    estimate = task.get("estimate_seconds")
    service = max(0.0, _number(task.get("service_seconds")))
    quantum = next_quantum(task, policy)
    provenance = str(task.get("estimate_provenance", "declared"))
    if estimate is None:
        expected = max(quantum, service * 2.0)
        provenance = "bounded discovery; duration unknown"
    else:
        expected = max(0.01, _number(estimate))
        if service >= expected:
            expected = max(quantum, service * 2.0)
            provenance = "censored lower bound exceeded prior estimate"
    setup = max(0.0, _number(task.get("setup_seconds")))
    restart = max(0.0, _number(task.get("restart_seconds"))) if task.get("preemptions", 0) else 0.0
    uncertainty = min(1.0, max(0.0, _number(task.get("uncertainty"), 0.5 if estimate is None else 0.0)))
    unlock = max(0.0, _number(task.get("unlock_value")))
    # Bound fan-out so speculative dependency counts do not dominate all work.
    value = 1.0 + min(4.0, math.log2(1.0 + unlock))
    cost = (expected + setup + restart) * (1.0 + uncertainty) / value
    return cost, expected, provenance


def rank(tasks, now, policy):
    """Return copied tasks, with deterministic score and readable selection reason.

    This is not globally optimal under unknown durations and multiple resources.
    The controller may backfill lower-ranked compatible work. It must not use
    rank to bypass dependencies, holds, deadlines, budgets or user stops.
    """
    now = _number(now)
    aging = max(0.01, _setting(policy, "aging_seconds", 300.0))
    decorated = []
    for source in tasks:
        task = dict(source)
        priority = _number(task.get("priority"))
        ready = _number(task.get("ready_at"), _number(task.get("created_at"), now))
        waiting = max(0.0, now - ready)
        original = task.get("origin", "original") == "original" or task.get("required_for_original", False)
        aged = original and waiting >= aging
        cost, estimate, provenance = estimated_cost(task, policy)
        # Gentle aging preserves the fast sweep until an explicit aged opportunity.
        score = cost / (1.0 + min(waiting / aging, 1.0))
        confidence = task.get("estimate_confidence", "unknown" if task.get("estimate_seconds") is None else "declared")
        task.update(score=score, selection_reason=(
            f"priority={priority:g}; "
            f"{'aged original service opportunity' if aged else 'fast useful result'}; "
            f"cost={score:.3f}s-equivalent, expected={estimate:.3f}s; "
            f"setup={_number(task.get('setup_seconds')):g}s, "
            f"unlock={_number(task.get('unlock_value')):g}; "
            f"confidence={confidence}; provenance={provenance}"
        ))
        # Old original tasks receive FIFO service opportunities, not a slow quota.
        key = (-priority, 0 if aged else 1, ready if aged else score,
               0 if original else 1, ready, str(task["id"]))
        decorated.append((key, task))
    return [task for _, task in sorted(decorated, key=lambda pair: pair[0])]


def should_preempt(active, candidate, now, policy):
    """Whether safe restart is plausibly worthwhile, after a service opportunity.

    Cancellation must still be acknowledged and the needed resources released
    before replacement dispatch. This function never proves either fact.
    """
    if active.get("preemption", "never") != "restart":
        return False
    if active.get("timing_required", False) or active.get("hold"):
        return False
    maximum = max(0, int(_setting(policy, "max_preemptions", 2)))
    if _number(active.get("preemptions")) >= maximum:
        return False
    if _number(candidate.get("priority")) < _number(active.get("priority")):
        return False
    started = active.get("started_at")
    if started is None:
        return False
    elapsed = max(0.0, _number(now) - _number(started))
    minimum = max(0.01, _setting(policy, "minimum_service_seconds", 5.0))
    if elapsed < max(minimum, _number(active.get("quantum_seconds"), next_quantum(active, policy))):
        return False
    # A freed CPU does not release a reasoning slot, and vice versa. Without a
    # capacity observation, require the victim to cover all replacement demand.
    held, needed = active.get("resources", {}), candidate.get("resources", {})
    available = policy.get("available", {})
    shared = False
    for resource, amount in needed.items():
        demand = max(0.0, _number(amount))
        free = max(0.0, _number(available.get(resource)))
        released = max(0.0, _number(held.get(resource)))
        if demand > free + released:
            return False
        shared |= demand > free and released > 0
    if not shared:
        return False
    # Protect an aged original opportunity from a stream of cheap auxiliary work.
    waiting = _number(now) - _number(active.get("ready_at"), _number(active.get("created_at"), now))
    if (active.get("origin", "original") == "original"
            and candidate.get("origin", "original") != "original"
            and not candidate.get("required_for_original", False)
            and waiting >= _setting(policy, "aging_seconds", 300.0)):
        return False
    active_cost, _, _ = estimated_cost(active, policy)
    if active.get("remaining_seconds") is not None and active.get("remaining_observed_at") is not None:
        # Only use a recent observation from the current attempt; old totals are
        # never transformed into residuals merely by subtracting elapsed time.
        observed = _number(active["remaining_observed_at"])
        freshness = max(0.01, _setting(policy, "estimate_freshness_seconds", 30.0))
        if _number(started) <= observed <= now and now - observed <= freshness:
            active_cost = max(0.0, _number(active["remaining_seconds"]))
    candidate_cost, _, _ = estimated_cost(candidate, policy)
    restart = max(0.0, _number(active.get("restart_seconds")))
    hysteresis = max(1.0, _setting(policy, "preemption_hysteresis", 1.5))
    minimum_gain = max(0.0, _setting(policy, "minimum_gain_seconds", 1.0))
    # The interrupted attempt's service is lost for restart-only tasks. Already
    # retained partial results do not make unfinished execution resumable.
    return active_cost - candidate_cost > hysteresis * (elapsed + restart) + minimum_gain
