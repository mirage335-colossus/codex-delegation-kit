def select_route(routes, memory_limit_mb, min_bits=None, max_error=None):
    candidates = [r for r in routes if r['supported'] and r['memory_mb'] <= memory_limit_mb]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r['bits'])['id']
