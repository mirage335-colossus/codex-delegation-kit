"""Frozen selector checks with synthetic observations; no performance claims."""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path
import sys


def route(name, bits, capacity, easy, **extra):
    return dict(id=name, bits=bits, stress_capacity=capacity, easy_ms=easy,
                supported=extra.get('supported', True), qualified=extra.get('qualified', True),
                memory_mb=extra.get('memory_mb', 64), error=extra.get('error', 0.01))


def evaluate(path):
    spec = importlib.util.spec_from_file_location('participant', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    a = route('oak', 64, 80, .8, error=0)
    b = route('elm', 16, 260, .9)
    c = route('ash', 8, 800, .3, qualified=False)
    d = route('fir', 8, 1000, .2, supported=False)
    e = route('yew', 16, 400, .4, memory_mb=2048)
    inputs = [a, b, c, d, e]
    cases = [
        ('capacity_before_backlog', inputs, 1024, None, None, 'elm'),
        ('higher_precision_override', inputs, 1024, 32, None, 'oak'),
        ('unavailable_override', inputs, 1024, 128, None, None),
        ('explicit_error_contract', inputs, 1024, None, .001, 'oak'),
        ('memory_boundary', [a, b], 64, None, None, 'elm'),
        ('no_route', [a, b], 63, None, None, None),
        ('higher_precision_algorithm', [route('dogwood', 64, 500, .8), b], 1024, None, None, 'dogwood'),
        ('unqualified_only', [c, d], 1024, None, None, None),
        ('no_error_compliant_route', [b], 1024, None, 0, None),
        ('minimum_floor_is_not_maximum', [a, route('cedar', 32, 240, .7)], 1024, 32, None, 'cedar'),
        ('format_label_permutation', [dict(a, id=9007199254740997), dict(b, id=9007199254740999)], 1024, None, None, 9007199254740999),
        ('reordered_inputs', list(reversed(inputs)), 1024, None, None, 'elm'),
    ]
    results = []
    for name, rows, memory, floor, error, expected in cases:
        supplied = deepcopy(rows)
        before = deepcopy(supplied)
        try:
            actual = module.select_route(supplied, memory, min_bits=floor, max_error=error)
            passed = actual == expected and supplied == before
            results.append(dict(case=name, passed=passed, expected=expected, actual=actual,
                                input_preserved=supplied == before))
        except Exception as exc:
            results.append(dict(case=name, passed=False, exception=repr(exc), expected=expected))
    return dict(passed=sum(x['passed'] for x in results), total=len(results), results=results)


if __name__ == '__main__':
    result = evaluate(Path(sys.argv[1]))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['passed'] == result['total'] else 1)
