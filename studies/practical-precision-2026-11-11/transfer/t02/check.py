from selector import select_route


def route(id, *, bits=32, supported=True, qualified=True, memory_mb=10,
          error=0.01, easy_ms=1, stress_capacity=10):
    return {
        "id": id,
        "bits": bits,
        "supported": supported,
        "qualified": qualified,
        "memory_mb": memory_mb,
        "error": error,
        "easy_ms": easy_ms,
        "stress_capacity": stress_capacity,
    }


def main():
    fast = route("idle", easy_ms=1, stress_capacity=10, bits=64)
    burst = route("burst", easy_ms=10, stress_capacity=100, bits=32)
    balanced = route("balanced", easy_ms=2, stress_capacity=80, bits=48)
    original = [fast.copy(), burst.copy(), balanced.copy()]

    assert select_route([fast, burst, balanced], 20) == "balanced"
    assert select_route([fast, burst, balanced], 20, min_bits=48) == "balanced"
    assert select_route([fast, burst, balanced], 20, min_bits=65) is None
    assert select_route([fast, burst, balanced], 20, max_error=0.009) is None

    excluded = [
        route("unsupported", supported=False, easy_ms=0, stress_capacity=1000),
        route("unqualified", qualified=False, easy_ms=0, stress_capacity=1000),
        route("too-large", memory_mb=21, easy_ms=0, stress_capacity=1000),
    ]
    assert select_route(excluded + [balanced], 20) == "balanced"
    assert select_route(excluded, 20) is None
    assert select_route([route("zero", easy_ms=0), route("other", easy_ms=2)], 20) == "zero"
    assert [fast, burst, balanced] == original


if __name__ == "__main__":
    main()
