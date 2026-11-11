def select_route(routes, memory_limit_mb, min_bits=None, max_error=None):
    candidates = [
        r for r in routes
        if r['supported']
        and r['qualified']
        and r['memory_mb'] <= memory_limit_mb
        and (min_bits is None or r['bits'] >= min_bits)
        and (max_error is None or r['error'] <= max_error)
    ]
    if not candidates:
        return None

    # Compare relative results on the two stated workloads. Maximizing the
    # weaker relative result avoids making either idle latency or burst service
    # the sole objective when the caller has not supplied workload weights.
    best_easy_ms = min(r['easy_ms'] for r in candidates)
    best_capacity = max(r['stress_capacity'] for r in candidates)

    def score(route):
        quiet = (
            1.0 if best_easy_ms == 0 and route['easy_ms'] == 0
            else 0.0 if best_easy_ms == 0
            else best_easy_ms / route['easy_ms']
        )
        stress = route['stress_capacity'] / best_capacity
        return min(quiet, stress), quiet * stress, stress

    return max(candidates, key=score)['id']
