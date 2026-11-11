def select_route(routes, memory_limit_mb, min_bits=None, max_error=None):
    """Choose the qualified route with the best challenging-work capacity.

    Precision and error are constraints only when requested; bit width alone
    is not evidence that a route is more useful. Easy-case latency breaks
    capacity ties, so a small idle-case advantage cannot displace capacity.
    """
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
    return max(candidates, key=lambda r: (r['stress_capacity'], -r['easy_ms']))['id']
